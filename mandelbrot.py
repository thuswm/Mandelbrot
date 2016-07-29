"""
This script will draw the mandelbrot set to a bitmap.

The calculation and generation of a bitmap is really straight forward if no
parameters are allowed. This script however introduces the possibility to adjust
the pixel size of the plot.

Another feature for exploring the details of the plot is a zooming function.
This allows the user to define a small subregion of the plot to be generated in
finer detail.

@author: Michael Thuswaldner
@date: 2016-07-27
"""

from math import pi,sin,cos
import Image


# ----------------------------------------------------------------------------------
def mandelbrotIterations(c,N=100):
    """
    This function does the Mandelbrot iterations.

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

# ----------------------------------------------------------------------------------
class ColorMap:
    """
    This class creates the color map to be used for plotting the Mandelbrot set.
    """

    def __init__(self, N, intensity):
        """
        Constructor.

        Arguments:
        N         -- Number of colors in color map (int).
        intensity -- The color intensity for the RGB color, max 225 (int).

        Return:
        None.
        """

        # The color map list
        self.colorMap = []

        # Calculate color ranges
        tRange = N/2
        bRange = N - tRange

        # Interpolate between Blue and Green
        for i in range(tRange):
            alpha = (i/float(tRange))*0.5*pi
            blue = int(intensity*cos(alpha))
            green = int(intensity*sin(alpha))
            color = (0,green,blue)
            #print(color)

            self.colorMap.append(color)

        # Interpolate between Green and Red
        for i in range(bRange):
            alpha = (i/float(bRange))*0.5*pi
            green = int(intensity*cos(alpha))
            red = int(intensity*sin(alpha))
            color = (red,green,0)
            #print(color)

            self.colorMap.append(color)

        # Replace the last colot with black
        self.colorMap[-1] = (0,0,0)

    def getColor(self, n):
        """
        Returns color number n from the color map.

        Arguments:
        n -- Color number to be returned (int).

        Return:
        RGB color (tuple).
        """

        return self.colorMap[n]

# ----------------------------------------------------------------------------------
class Plot:
    """
    This class acts as the interface between the complex numbers and the bitmap.
    """

    def __init__(self, filename):
        """
        Constructor.

        Arguments:
        filename -- Name of the bitmap file (string, not used).

        Return:
        None.
        """

        # Set internal values
        self.filename = filename

    def setMapping(self, bigPixelSize, noBigPixels, corner, zSize):
        """
        Set the complex to bitmap mapping values.

        Arguments:
        bigPixelSize -- The size in pixels of the bigPixel (int).
        noBigPixels  -- The number of bigPixels per bitmap side (int).
        corner       -- The upper left corner of the plot area (complex).
        zSize        -- The side length of the plot square (float).

        Return:
        None
        """

        # Set internal values
        self.bigPixelSize = bigPixelSize
        self.noBigPixels = noBigPixels
        self.corner = corner
        self.zSize = zSize

        # Calculate bitmap size
        self.size = bigPixelSize*noBigPixels

        # Setup bitmap
        self.img = Image.new( 'RGB', (self.size,self.size), "black") # create a new black image
        self.pixels = self.img.load() # create the pixel map

    def getPixelMap(self):
        """
        Get the bigPixel to complex number map for the bitmap.

        Arguments:
        None.

        Return:
        List of complex numbers associate with the bibPixels.
        """

        # Initialize the pixel map
        pixelMap = []
        for i in range(self.noBigPixels):
            row = []
            for j in range(self.noBigPixels):
                row.append(complex(0.,0.))

            pixelMap.append(row)

        # Iterate through all bigPixels
        for i in range(self.noBigPixels):
            for j in range(self.noBigPixels):

                cDelta = self.zSize/self.noBigPixels

                cReal = self.corner.real + 0.5*cDelta + i*cDelta
                cImag = self.corner.imag - 0.5*cDelta - j*cDelta
                pixelMap[i][j] = complex(cReal,cImag)

        # Return list
        return pixelMap

    def paint(self, ni, nj, color):
        """
        Paint bigPixel (ni,nj) onto bitmap with color.

        Argument:
        ni    -- bigPixel row index (int).
        nj    -- bigPixel column index (int).
        color -- RGB color (tuple).

        Return:
        None
        """

        if (ni > self.noBigPixels) or (nj > self.noBigPixels):
            # Complex number is out of range
            print("Error: bigPixel index out of range!")
        else:
            # Start pixels
            pi = self.bigPixelSize*ni
            pj = self.bigPixelSize*nj

            # Paint a square
            for i in range(self.bigPixelSize):
                for j in range(self.bigPixelSize):
                    self.pixels[pi+i,pj+j] = color

    def showZoomRegion(self, bCorner, bSize, color=(225,0,0)):
        """
        Add a red box to mark a possible zoom area.

        Arguments:
        bCorner          -- The upper left corner of the plot area (complex).
        bSize            -- The side length of the plot square (float).
        color            -- RGB color for the box to be drawn, defailt red
                            (tuple).

        Return:
        None.
        """

        print("Window size: " + str((self.size,self.size)))

        # Calculate edge pixels
        pi1 = int(((-self.corner.real
              + bCorner.real)/float(self.zSize))*self.size) # X-axis upper left index
        pj1 = int(((self.corner.imag
              - bCorner.imag)/float(self.zSize))*self.size) # Y-axis upper left index

        if (pi1 < 0.) or (pj1 < 0.):
            print("Left upper box corner out of range!")

            # Setting upper left corner to (0,0)
            pi1 = 0
            pj1 = 0
        else:
            print("Upper left box corner: " + str((pi1,pj1)))

        pi2 = int(((-self.corner.real + bCorner.real
              + bSize)/float(self.zSize))*self.size) - 1 # X-axis lower left index
        pj2 = int(((self.corner.imag - bCorner.imag
              + bSize)/float(self.zSize))*self.size) - 1 # Y-axis lower left index

        if (pi2 > self.size) or (pj2 > self.size):
            print("Lower right box corner out of range!")

            # Setting lower right corner to (self.size,self.size)
            pi2 = self.size
            pj2 = self.size
        else:
            print("Lower right box corner: " + str((pi2,pj2)))

        # Draw vertical lines
        for j in range(pj2 - pj1):
            self.pixels[pi1,pj1+j] = color
            self.pixels[pi2,pj1+j] = color

        # Draw horizontal lines
        for i in range(pi2 - pi1):
            self.pixels[pi1+i,pj1] = color
            self.pixels[pi1+i,pj2] = color

    def show(self):
        """
        Show the painted Plot.

        Arguments:
        None.

        Return:
        None.
        """

        self.img.show()


# === Main ===================================================================
if __name__ == "__main__":

    # Set max mandelbrot iterations
    iterN = 200

    # Create a color map
    intensity = 200
    colorMap = ColorMap(iterN, intensity)

    # Create plot
    bigPixelSize = 1
    noBigPixels = 500
    corner = complex(-2.,2)
    zSize = 4.
    plot = Plot("text.bmp")
    plot.setMapping(bigPixelSize,noBigPixels,corner,zSize)

    # Get list of complex numbers
    complexList = plot.getPixelMap()

    # Iterate through all complex numbers ans calculate the Mandelbrot
    # iterations.
    for i in range(noBigPixels):
        for j in range(noBigPixels):
            # Get complex number
            c = complexList[i][j]

            # Calculate number of iterations
            mIter = mandelbrotIterations(c,iterN)

            # Get color
            color = colorMap.getColor(mIter-1)

            # Plot bigPixel
            plot.paint(i,j,color)

    # Draw red box
    if (True):
        bCorner = complex(-0.5,0.75)
        bSize = 0.25
        plot.showZoomRegion(bCorner,bSize)

    # Show final plot
    plot.show()
