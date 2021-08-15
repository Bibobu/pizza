# Notes on the version change

## Dependencies
* Only numpy has been ported to python 3. Not numeric.
* PIL is now Pillow (original PIL dev stopped in 2011).
  - Correct the example with
```
    from PIL import Image, ImageTk
```
   retrocompatibility must be checked.
* Check Pmw compatibility with python3.4+ (seems ok)
* Togl support has been dropped by PyopenGL devs. Is it still relevant?
* Globally installation advices should be rewritten using pip or conda
* Is the use of some tools such as MatLab, Gnuplot or Raster3d still
  necessary given the existence of python libs (numpy, scipy, matplotlib...)
* In installing glumpy, we also need python3-devel lib compared to what
  is mentioned in the doc. This lib is installed through package managers.

## Changes

* Well if everything goes well, I'll write a new vizualization tool...
  - It might be better to start off a new project and make it simply dependent on the pizza tools
  - And also make it dependent on glumpy and PyQt, that looks more reasonable
  - This imply dropping several libs actually. Inclugind gl.
* The whole matlab.py and gnu.py could be replaced by matplotlib.

* This is a test modification
