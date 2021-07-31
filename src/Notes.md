# Notes on the version change

## Dependencies
* Only numpy has been ported to python 3. Not numeric.
* PIL is now Pillow (original PIL dev stopped in 2011).
  - Correct the example with
```
    from PIL import Image, ImageTk
```
   retrocompatibility must be checked.
* Check Pmw compatibility with python3.4+
* Togl support has been dropped by PyopenGL devs. Is it still relevant?
* Globally installation advices should be rewritten using pip or conda
* Is the use of some tools such as MatLab, Gnuplot or Raster3d still
  necessary given the existence of python libs (numpy, scipy, matplotlib...)

## Changes

