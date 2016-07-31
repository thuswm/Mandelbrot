# Mandelbrot

This is a python script for generating a visualization of the Mandelbrot set.

The Mandelbrot set is defined as the set of complex numbers c for which the
iterative function,

  z_n+1 = z_n^2 + c

stays bounded to,

  abs(z_N)<=2

for any iterations N.

# Usage of the script

The script is not interactive but simple modifications of it makes it possible
for the user explore different parts of the Mandelbrot set.

This script contains a function for testing if a complex number belongs to the
Mandelbrot set. In order not to end up in infinitive loops an approximation has
been introduced where the maximum number of iterations is restricted to a
finite number N. When this number is reaced in the complex number is said to
belong to the set.

Two classes are also present in the script. One for generating the bitmap plot
of the mandel brot set and one for generating the color scale for the plot.

## Setting the plotting area

The term bigPixel has been introduced to allow the generation of a low
resolution plot of the Mandelbrot set with a reduced set of calculation points.
The user may define a bigPixel to be represented by a square of pixles (normal
bitmap pixels).

The initial settings define the bigPixel to be equal to one pixel:

  bigPixelSize = 1

The resolution of the plot is defined by setting the number of bigpixels:

  noBigPixels = 500

The user defines the complex range to be plotted by setting the corner and the
size of a square in the complex plane:

  corner = complex(-2.,2) zSize = 4.

## The red box

When running the script unchanged a red square will appear in the generated
bitmap. This square can be turned on and off by setting the following if
statement to True or False respectively:

  # Draw red box
  if (True):
      bCorner = complex(-0.5,0.75)
      bSize = 0.25
      plot.showZoomRegion(bCorner,bSize)

The idea of this square is to help the user visualize a subsequent refinement
of the plot. The variables under the if-statement should be understood from the
previous description.

## Suggested first use

For a first run of this script one could first run the script as it is and then
alter the plotting area to refine the plot in accordance with the red box.

The steps are the following:
1. Run the unchanged script.
2. Edit the plot area variables to say the following:

  corner = complex(-0.5,0.75)
  zSize = 0.25

3. Run the script again.
