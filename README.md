# Mandelbrot
This is a python script generating a GUI based tool for exploring the
visualization of the Mandelbrot set.

The Mandelbrot set is defined as the set of complex numbers c for which the
iterative function,

  z_n+1 = z_n^2 + c

stays bounded to,

  abs(z_N)<=2

for any iterations N.

# Usage of the script
Run the mandelgui.py script in your favourite python environment.

Example (ipython):
run mandelgui.py

This will start a Qt application showing an image property panel, an image view
and a status bar.

## The image property panel
The image property panel has three editable input boxes. These boxes contain
numbers that controls the image generation. The firs number is the size of the
image in pixels, i.e. the default number 500 tells the application to generate
an image of the size 500 times 500.

The second number is the depth of the image. This means the number of colors
used to visualize the Mandelbrot set.

The third number is the color intensity. This number ranges from 0 being all
black to 255 being the brightest.

To the left of the property fields you find a vertical progress bar. Since this
is a python script and the generation (calculation) of the Mandelbrot set image
is relative time consuming this progress bar will inform the user where in the
process the image generation is.

## The image view
This is the portion of the application showing the generated image. It is also
the place where the application interacts with the user.

The following commands are available: zooming -- Box select the area you would
like to inspect closer. As soon as the left mouse button is released the
generation of a new image is started (using input also from the property
panel).  Redraw  -- In order for the updated image properties to take effect
you need to redraw the image. This is done by double clicking anywhere in the
view.  Going back in history -- By right clicking anywhere in the view field
the previous view is generated.

## The status bar
The status bar at the bottom of the application window shows you the current
mouse position in the image view. These coordinates are given in the complex
plane.

