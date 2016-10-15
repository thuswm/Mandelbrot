#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
This module is the GUI front end to the Mandelbrot module. It produces an
interactive tool for exploring the complexities of the graphical representation
of the Mandelbrot set.
"""

import sys
from PySide import QtGui
from PySide import QtCore
from scipy import log10

import mandelbrot as MB

# -------------------------------------------------------------------
class MCoordConverter(QtCore.QObject):
    """
    This class is used for converting between screen and complex coordinates. It
    also carries a collective memory in the form of attributes. These attributes
    are accessible by all instances of this class.

    Note! This class is not entirely safe. If member functions are not called in
    the correct order the internal state of the instance may produce incorrect
    results.
    """

    # Class attributes
    # ----------------
    # The upper left corner of the complex plane
    upperLeftCorner = complex(0.,0.)

    # The pixel to complex scale factor
    scaleFactor = 1.

    # The precision or fidelity of each pixel when represented in the complex
    # plane
    precision = 3

    def __init__(self):
        """
        Constructor.

        Initializes the coordinate converter.
        """

        super(MCoordConverter,self).__init__()

        # Initialize the screen position
        self.screenPos = complex(0.,0.)

        # Initialize pixel screen position
        self.pixelPos = QtCore.QPointF(0,0)


    def setPixelCoord(self, pos):
        """
        Set the screen position in pixel coordinates. This value will internally
        be translated to the corresponding complex number via the two attributes
        upperLeftCorner and scaleFactor.

        Parameters:
        pos     -- The screen position in pixel coordinates (QtCore.QPointF).
        """

        # Set pixel position
        self.pixelPos = pos

        # Get attributes
        corner = MCoordConverter.upperLeftCorner
        scale = MCoordConverter.scaleFactor

        # Calculate the position in the complex plane
        self.complexPos = complex(corner.real+scale*self.pixelPos.x(),
                                 corner.imag-scale*self.pixelPos.y())


    def setPlotArea(self, corner, complexWidth, pixelwidth):
        """
        Set the plot area.

        The plot area width in both the complex plane and the physical
        pixel plane are set with this member function. Using these two numbers
        this class calculates a scale factor between the two in order to
        correctly scale between the two planes.

        Parameters:
        corner           -- The upper left corner of the screen in complex
                            coordinate (complex).
        complexWidth     -- The plot width complex (real part) number (float).
        pixelwidth       -- The plot width in pixels (int).
        """

        # Set class attribute, upper left corner of the plot
        MCoordConverter.upperLeftCorner = corner

        # Set class attribute, with of the plot
        MCoordConverter.scaleFactor = complexWidth/pixelwidth

        # Calculate the coordinate resolution
        MCoordConverter.precision = abs(int(log10(MCoordConverter.scaleFactor)))


    def getPixelCoord(self):
        """
        Returns a QPointf of the pixel coordinates. This information is used for
        transmitting data via signals. It is not beautiful but it will do for
        now.

        Return:
        Pixel coordinates in the form of a tuple (QtCore.QPoint)
        """

        return self.pixelPos

    def getComplex(self):
        """
        Returns the complex coordinates equivalent to the pixel coordinates
        previously set.

        Return:
        Complex coordinate (complex).
        """

        return self.complexPos

    def __str__(self):
        """
        The string representation of the class.

        Return:
        (string)
        """

        # Create the string representation
        out = ""
        if (self.complexPos.real<0):
            out = "(%.*f" % (MCoordConverter.precision,self.complexPos.real)
        else:
            out = "( %.*f" % (MCoordConverter.precision,self.complexPos.real)

        if (self.complexPos.imag < 0):
            out += ""
        else:
            out += "+"
        out += "%.*fi)" % (MCoordConverter.precision,self.complexPos.imag)

        return out

    def __repr__(self):
        """
        The string representation of the class.

        Return:
        (string)
        """

        return self.__str__()


# -------------------------------------------------------------------
class MScene(QtGui.QGraphicsScene):
    """
    Reimplementing the QGraphicsScene for better event control.
    """

    def __init__(self,parent=None):
        """
        Constructor.
        """
        super(MScene,self).__init__(parent)

        # Init color map
        self.colorMap = MB.ColorMap()

        # Init Mandelbrot object
        self.mandelbrotImage = MB.MandelbrotImage()

        # Generate initial image
        self.generateImage()

    def generateImage(self,upperLeft=complex(-2.,2.),width=4.,depth=200,intensity=200,
                      noPixels=500):
        """
        This function contains all for generating the image in the scene.

        Parameters:
        upperLeft    -- The upper left corner of the complex plane to generate (complex)
        width        -- The width of the complex plane to generate (float)
        depth        -- The number of max iterations when calculating the
                        Mandelbrot iterations. This number is also equal to the number
                        of colors in the color map [0,..] (int).
        intensity    -- Intensity of the colors in the color map. [0,255] (int).
        noPixels     -- The size of the bitmap [noPixels x noPixels] (int).
        """

        # Set plot area
        self.screenPos = MCoordConverter()
        self.screenPos.setPlotArea(upperLeft, width, noPixels)

        # Create a color map
        self.colorMap.generate(depth,intensity)

        # Create a image of the Mandelbrot set
        plotRange = MB.PlotRange(upperLeft,width)
        image = self.mandelbrotImage.generate(noPixels,self.colorMap,plotRange,depth)

        # Setup scene
        self.clear()
        self.addPixmap(QtGui.QPixmap.fromImage(image))


# -------------------------------------------------------------------
class MView(QtGui.QGraphicsView):
    """
    Reimplementing the QGraphicsScene for better event control.
    """

    # Class attributes
    mPosSignal = QtCore.Signal(QtCore.QPointF)

    def __init__(self,parent=None):
        """
        Constructor.
        """
        super(MView,self).__init__()

        # Set the alignment of the scene object to the upper left corner
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft |
                                 QtCore.Qt.AlignmentFlag.AlignTop)

        # Allow mouse tracking
        self.setMouseTracking(True)

        # Add a rubber band object to the view
        self.rubberBand = QtGui.QRubberBand(QtGui.QRubberBand.Line,self)

        # Mouse press indicator
        self.mousePress = False

        # Initialize all other attributes used in the class
        self.origin = QtCore.QPointF(0,0)

        # Create screen position objects
        self.origin = QtCore.QPointF() # mouse press position
        self.sPos = MCoordConverter() # mouse movement

        # View scene
        self.scene = MScene()
        self.setScene(self.scene)

        # Set scene properties
        self.depth = 200
        self.intensity = 200
        self.noPixels = 500

        # Create a history list; I don't like the initiation!
        self.history = [[complex(-2.,2.),4.,self.depth,self.intensity,self.noPixels]]

    @QtCore.Slot(int)
    def setDepth(self,depth):
        """
        Set the depth property for the scene.

        Parameters:
        depth     --- Number of colors and number of Mandelbrot iterations
                      (int).
        """

        self.depth = int(depth)

    @QtCore.Slot(int)
    def setIntensity(self,intensity):
        """
        Set the intensity property for the scene.

        Parameters:
        intensity     --- The color intensity [0,255] (int).
        """

        self.intensity = int(intensity)

    @QtCore.Slot(int)
    def setNoPixels(self,noPixels):
        """
        Set the noPixels property for the scene.

        Parameters:
        noPixels     --- Image size [noPixels x noPixels] (int).
        """

        self.noPixels = int(noPixels)

    def mousePressEvent(self,event):
        """
        Overloaded version of mouse press event handler.

        This handles both left and right click events.

        Arguments:
        event -- The event handled by this function.
                 This is a QGraphicsSceneMouseEvent object.

        Return:
        None.
        """

        # Check which mouse button is pressed
        if (event.button() == QtCore.Qt.MouseButton.LeftButton):
            # If mouse press is on
            self.mousePress = True

            # Get mouse press position
            self.origin = event.pos()

            # Set initial size of rubber band
            self.rubberBand.setGeometry(QtCore.QRect(self.origin,QtCore.QSize()))
            self.rubberBand.show()

        elif (event.button() == QtCore.Qt.MouseButton.RightButton):
            # Get the previous image settings from history list
            if (len(self.history)>1):
                # Pop the current image
                self.history.pop()

                # Get the previous one
                prev = self.history.pop()

                # Generate a new image
                self.scene.generateImage(prev[0],prev[1],prev[2],prev[3],prev[4])

            else:
                print("Warning: Cannot go further back in history!")


    def mouseMoveEvent(self,event):
        """
        Overloaded version of mouse movement event handler.

        This handler resizes the rubber band box after the position of the mouse
        pointer but adjusts the size to always show a perfect square box.

        The handler also enables coordinate tracking of the mouse position in
        the view.
        """

        # Get mouse position
        pos = event.pos()

        # Setup local conversion object
        self.sPos.setPixelCoord(pos)

        # Emit signal
        self.mPosSignal.emit(self.sPos.getPixelCoord())

        # Check if mouse is pressed
        if(self.mousePress):
            # Use the largest of dx and dy to make a square
            dx = pos.x() - self.origin.x()
            dy = pos.y() - self.origin.y()

            # Find largest delta, dmax
            dmax = 0
            if (abs(dx)>abs(dy)):
                dmax = abs(dx)
            else:
                dmax = abs(dy)

            # If square is in positive dx
            if (dx>0):
                if (dy>0):
                    pos = self.origin + QtCore.QPoint(dmax,dmax)
                else:
                    pos = self.origin + QtCore.QPoint(dmax,-dmax)
            else:
                if (dy>0):
                    pos = self.origin + QtCore.QPoint(-dmax,dmax)
                else:
                    pos = self.origin + QtCore.QPoint(-dmax,-dmax)

            # Update rubber band geometry
            self.rubberBand.setGeometry(QtCore.QRect(self.origin,pos).normalized())

    def mouseReleaseEvent(self,event):
        """
        Overloaded version of mouse release event handler.

        This handler emits a signal containing the second corner of the
        rubber band.
        """

        # Check which button was pressed
        if (event.button() == QtCore.Qt.MouseButton.LeftButton):
            # Get mouse position
            pos = event.pos()

            # Mouse press is off
            self.mousePress = False

            # Trigger generation of new image
            corner = self.sPos.setPixelCoord(self.rubberBand.pos())
            corner = self.sPos.getComplex()
            width = self.rubberBand.size().width()
            width = width*self.sPos.scaleFactor

            if (width != 0.):
                # Generate the new image
                self.scene.generateImage(corner,width,
                        self.depth,self.intensity,self.noPixels)

                # Add to history
                self.history.append([corner,width,
                        self.depth,self.intensity,self.noPixels])

            # Hide the rubber band
            self.rubberBand.hide()

        else:
            None


    def mouseDoubleClickEvent(self,event):
        """
        Overload the double click event handler.

        Double clicking on the view will trigger a regeneration of the current
        image. This is done when e.g. the image properties are changed but the
        user does not want to change the plot region.
        """

        # Get the current image
        curr = self.history[-1]

        # Generate a new image
        self.scene.generateImage(curr[0],curr[1],self.depth,self.intensity,self.noPixels)

# -------------------------------------------------------------------
class MPanel(QtGui.QWidget):
    """
    This class represents the side panel of the application.
    """

    def __init__(self,parent=None):
        """
        Constructor.
        """

        super(MPanel,self).__init__()

        # Fix the width of this widget
        self.setFixedWidth(300)

        # Create inputs
        self.pixelsLE = QtGui.QLineEdit()
        self.pixelsLE.setText("500")
        self.depthLE = QtGui.QLineEdit()
        self.depthLE.setText("200")
        self.intensityLE = QtGui.QLineEdit()
        self.intensityLE.setText("200")

        # Create vertical layout
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.imageProperties())

        # Create progress bar
        self.pbar = QtGui.QProgressBar()
        self.pbar.setOrientation(QtCore.Qt.Vertical)
        self.pbar.setTextDirection(QtGui.QProgressBar.TopToBottom)
        self.pbar.setMinimum(0)

        # Create horizontal layout
        hbox = QtGui.QHBoxLayout(self)
        hbox.addWidget(self.pbar)
        hbox.addLayout(vbox)

        # Adds a stretchable space to press up the rest
        # of the widgets to the top of the pane.
        vbox.addStretch()


    def imageProperties(self):
        """
        This method generates the GUI for specifying the new plot region.
        """

        # Create a validator
        pixelValid = QtGui.QIntValidator(1,1000)
        depthValid = QtGui.QIntValidator(1,10000)
        intensityValid = QtGui.QIntValidator(1,255)

        # Pixels input
        self.pixelsLE.setValidator(pixelValid)
        pixelsLabel = QtGui.QLabel("Image size [pixels x pixels]")
        pixelsBox = QtGui.QHBoxLayout()
        pixelsBox.addWidget(pixelsLabel)
        pixelsBox.addWidget(self.pixelsLE)

        # Depth input
        self.depthLE.setValidator(depthValid)
        depthLabel = QtGui.QLabel("Color depth [0,1000]")
        depthBox = QtGui.QHBoxLayout()
        depthBox.addWidget(depthLabel)
        depthBox.addWidget(self.depthLE)

        # Intensity input
        self.intensityLE.setValidator(intensityValid)
        intensityLabel = QtGui.QLabel("Color intensity [0,255]")
        intensityBox = QtGui.QHBoxLayout()
        intensityBox.addWidget(intensityLabel)
        intensityBox.addWidget(self.intensityLE)

        # Create vertical layout
        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(pixelsBox)
        vbox.addLayout(depthBox)
        vbox.addLayout(intensityBox)

        # Create group object
        newGroup = QtGui.QGroupBox()
        newGroup.setAlignment(QtCore.Qt.AlignLeft)
        newGroup.setTitle("Image Properties")
        newGroup.setLayout(vbox)

        # Return group
        return newGroup

    @QtCore.Slot(int)
    def setProgressMax(self,itrMax):
        self.pbar.setMaximum(itrMax)

    @QtCore.Slot(int)
    def setProgress(self,itr):
        self.pbar.setValue(itr)


# -------------------------------------------------------------------
class MCentralWidget(QtGui.QWidget):
    """
    This class holds all widgets visible in the main window class.
    """

    def __init__(self,parent=None):
        """
        Constructor.
        """
        super(MCentralWidget,self).__init__(parent)

        # Create panel
        self.panel = MPanel()

        # Setup view
        self.view = MView()

        # HBox
        hbox = QtGui.QHBoxLayout(self)
        hbox.addWidget(self.view)
        hbox.addWidget(self.panel)

        # Connect signals and slots
        self.panel.depthLE.textChanged.connect(self.view.setDepth)
        self.panel.intensityLE.textChanged.connect(self.view.setIntensity)
        self.panel.pixelsLE.textChanged.connect(self.view.setNoPixels)
        self.view.scene.mandelbrotImage.sender.itrSignal.connect(self.panel.setProgress)
        self.view.scene.mandelbrotImage.sender.maxSignal.connect(self.panel.setProgressMax)

# -------------------------------------------------------------------
class MStatusBar(QtGui.QStatusBar):
    """
    This class is created for adding a custom slot to the normal QStatusBar.
    """

    def __init__(self,parent=None):
        """
        Constructor.

        Arguments:
        parent          -- Parent window

        Return:
        None.
        """
        super(MStatusBar,self).__init__(parent)

        # Coordinate conversion object
        self.sPos = MCoordConverter()

    @QtCore.Slot(QtCore.QPointF)
    def showPosition(self,pixelPos):
        """
        Custom slot for showing scene coordinates.

        Parameters:
        pixelPos   -- Variable containing the pixel screen position (QPointF).
        """

        # Set local conversion object
        self.sPos.setPixelCoord(pixelPos)

        # Prepare string
        statusStr = "Mouse position: " + str(self.sPos)

        # Emit signal
        self.showMessage(statusStr)

# -------------------------------------------------------------------
if __name__ == "__main__":
    # The application
    # Test if there already is an instance
    try:
        app = QtGui.QApplication(sys.argv)
    except RuntimeError:
        app = QtGui.QApplication.instance()

    # Status bar
    statBar = MStatusBar()

    # Central widget
    centralWidget = MCentralWidget()

    # Connect mouse position with status bar
    centralWidget.view.mPosSignal.connect(statBar.showPosition)

    # Main window
    mainWindow = QtGui.QMainWindow()
    mainWindow.setCentralWidget(centralWidget)
    mainWindow.setStatusBar(statBar)

    # Show the window
    mainWindow.show()

    # The main event loop
    sys.exit(app.exec_())
