# simple test of vcr tool
# Requires dump.micelle and data.micelle
# ONE OF THESE FILES IS NOT PROVIDED

from dump import dump
from data import data
from gl import gl
from vcr import vcr

d = dump("files/dump.micelle")
dt = data("files/data.micelle")
d.extra(dt)
g = gl(d)
g.rotate(0, 270)
v = vcr(g)
v.q(10)
v.box()
v.axis()
v.clipxlo(0.2)
v.clipxhi(0.5)
v.play()

print("all done")
