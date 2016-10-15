"""
This script will generate a visualization of the Mandelbrot set.

@author: Michael Thuswaldner
@date: 2016-07-27
"""

from math import pi,sin,cos
from PySide import QtGui, QtCore


# ----------------------------------------------------------------------------------
class PlotRange:
    """
    This class is a simple container for the Mandelbrot plot range definition.
    The plot range is always a square region.
    """

    def __init__(self, corner=complex(0.,0.), zSize = 2.):
        """
        Constructor with default values.

        Arguments:
        corner       -- The upper left corner of the plot area (complex).
        zSize        -- The side length of the plot square (float).

        Return:
        None.
        """

        self.corner = corner
        self.zSize = zSize

# ----------------------------------------------------------------------------------
class ColorMap:
    """
    This class creates the color map to be used for plotting the Mandelbrot set.

    NOTE! This is perhaps not the best way to create a color map but it will do
    for now.
    """

    def __init__(self):
        """
        Constructor.
        """

    def generate(self, N, intensity):
        """
        This function generates the color map.

        Arguments:
        N         -- Number of colors in color map (int).
        intensity -- The color intensity for the RGB color, max 225 (int).

        Return:
        None.

        """

        # The color map list
        self.colorMap = []

        # Calculate color ranges
        self.N = N
        tRange = N/2
        bRange = N - tRange
        fRange = tRange/3

        # Interpolate between Blue and Green
        for i in range(tRange):
            alpha = (i/float(tRange))*0.5*pi
            blue = int(intensity*cos(alpha))
            green = int(intensity*sin(alpha))
            color = (0,green,blue)

            self.colorMap.append(color)

        # Interpolate between Green and Red
        for i in range(bRange):
            alpha = (i/float(bRange))*0.5*pi
            green = int(intensity*cos(alpha))
            red = int(intensity*sin(alpha))
            color = (red,green,0)

            self.colorMap.append(color)

        # Make the upper end transition to a darker shade of blue
        d = 0.05
        for i in range(fRange):
            darkness = d + ((1.-d)/fRange)*i
            color = self.colorMap[i]
            green = int(darkness*color[1])
            blue = int(darkness*color[2])
            self.colorMap[i] = (0,green,blue)

        # Replace the last color with black
        self.colorMap[-1] = (0,0,0)

    def getColor(self, n):
        """
        Returns color number n from the color map.

        Arguments:
        n -- Color number to be returned (int).

        Return:
        RGB color (tuple).
        """

        if (n<self.N):
            return self.colorMap[n]
        else:
            print("Error: Color map request out of range!")
            exit(2)

# ----------------------------------------------------------------------------------
class SenderObject(QtCore.QObject):
    """
    This is a simple class which will allow me to send a signal from another
    class which itself does not inherit from QObject.
    """

    # Attributes
    itrSignal = QtCore.Signal(int)
    maxSignal = QtCore.Signal(int)

    def __init__(self):
        """
        Constructor.
        """

        super(SenderObject,self).__init__()

# ----------------------------------------------------------------------------------
class MandelBase(object):
    """
    This class is the base class for the Mandelbrot calculation and is used to
    hide member functions not directly accessed by the user.

    The MandelbrotImage class inherits this class and is then used as the user
    interface.
    """

    def __init__(self):
        """
        Constructor.

        Set the complex to bitmap mapping values.

        Return:
        None
        """

        # Create a sender object for emitting signals
        self.sender = SenderObject()


    def mandelbrotIterations(self,c,N=100):
        """
        This member function does the Mandelbrot iterations.

        Iterate the function:
        z(n+1) = z(n)^2 + c
        for the complex number c and return the number of iterations before |z(n+1)|>2

        The maximum number of iterations are limited to N.

        Arguments:
        c -- test value (complex) to see if it belongs to the Mandelbrot set.

        Return:
        Number of iterations until the iteration yields |z(n+1)|>2. The maximum number
        of iterations are limited to N.
        """

        # Initialize start value for iteration
        z = complex(0.,0.)

        # Iteration counter
        n = 0

        # Iterate
        while (abs(z) < 2.) and (n < N):
            n = n + 1
            z = z*z + c

        return n


    def getPixelMap(self,noPixels,plotRange):
        """
        Get the pixel to complex number map for the bitmap.

        Arguments:
        noPixels     -- The number of pixels per bitmap side (int).
        plotRange    -- The range in the complex plane to plot.

        Return:
        List of complex numbers associate with the pixels.
        """

        # Initialize the pixel map
        pixelMap = []
        for i in range(noPixels):
            row = []
            for j in range(noPixels):
                row.append(complex(0.,0.))

            pixelMap.append(row)

        # Iterate through all pixels
        cDelta = plotRange.zSize/float(noPixels)
        for i in range(noPixels):
            for j in range(noPixels):

                cReal = plotRange.corner.real + 0.5*cDelta + i*cDelta
                cImag = plotRange.corner.imag - 0.5*cDelta - j*cDelta
                pixelMap[i][j] = complex(cReal,cImag)

        # Return list
        return pixelMap


    def fillImage(self, plotRange, noPixels, iterN, colorMap):
        """
        This function fills the image with colors representing the mandelbrot
        iterations.

        Arguments:
        plotRange    -- The range in the complex plane to plot.
        noPixels     -- The number of pixels per bitmap side (int).
        iterN        -- Max number of manderbrot iterations.
        colorMap     -- The color map object.

        Return:
        The generated image.
        """

        # Create image object
        image = QtGui.QImage(noPixels,noPixels,QtGui.QImage.Format_RGB32)

        # iteration number
        itrNo = 1

        # Get list of complex numbers
        complexList = self.getPixelMap(noPixels,plotRange)

        # Send max number of iterations to progress bar
        self.sender.maxSignal.emit(noPixels*noPixels)

        # Iterate through all complex numbers and calculate the Mandelbrot
        # iterations.
        for i in range(noPixels):
            for j in range(noPixels):
                # Get complex number
                c = complexList[i][j]

                # Calculate number of iterations
                mIter = self.mandelbrotIterations(c,iterN)

                # Get color
                color = colorMap.getColor(mIter-1)

                # Plot Pixel
                if (i > noPixels) or (j > noPixels):
                    # Complex number is out of range
                    print("Error: Pixel index out of range!")
                else:
                    # Paint one pixel
                    image.setPixel(i,j,QtGui.qRgb(color[0],color[1],color[2]))

                # Emit signal and increase iteration number
                self.sender.itrSignal.emit(itrNo)
                itrNo += 1

        return image

# ----------------------------------------------------------------------------------
class MandelbrotImage(MandelBase):
    """
    This class generate an image of the mandelbrot set.

    This is the interface for other applications.
    """

    def __init__(self):
        """
        Constructor.
        """

        # Init base class
        super(MandelbrotImage,self).__init__()


    def generate(self, noPixels, colorMap, plotRange, depth):
        """
        This function fills the image with the range plotRange of the Mandelbrot
        set. The depth of the colors, i.e. the number of colors used for
        representation, is the same as the imaximum number of Mandelbrot iterations.

        Arguments:
        noPixels     -- Image size, pixels x pixels (int)
        colorMap     -- The color map used for the image.
        plotRange    -- The range in the complex plane to plot.
        depth        -- The maximum number of Mandelbrot iterations.


        Return:
        The generated image.
        """

        # Fill image and return
        return self.fillImage(plotRange,noPixels,depth,colorMap)


# === Main ===================================================================
if __name__ == "__main__":

    print("Generating an image of the mandelbrot set")

    # Variables
    depth = 200
    intensity = 200
    noPixels = 500
    plotRange = PlotRange(complex(-2.,2.),4.)

    # Create a color map
    colorMap = ColorMap()
    colorMap.generate(depth,intensity)

    # Create a image of the mandelbrot set
    mandelbrot = MandelbrotImage(noPixels,colorMap)
    mandelbrot.generate(plotRange,depth)
    mandelbrot.save("slask.bmp")

    print("Done! The picture is saved to a file.")
