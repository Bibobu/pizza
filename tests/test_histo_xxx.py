# simple test of histo tool
# requires files/dump.kinase
# THIS FILES WAS NOT PROVIDED

from dump import dump
from gnu import gnu
from histo import histo

d = dump("files/dump.kinase")
h = histo(d)
x, y = h.compute('x', 25)
g = gnu()
g.xtitle("X position")
g.ytitle("Particle Count")
g.title("Histogram of Particle Density")
g.plot(x, y)

print("all done")
