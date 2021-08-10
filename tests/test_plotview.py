# simple test of plotview tool
# requires files/log.obstacle
# creates tmp.plotview.eps

from log import log
from gnu import gnu
from plotview import plotview

lg = log("files/log.obstacle")
g = gnu()
p = plotview(lg.get()[0], g)

p.select(1)
p.select(6)
p.yes(2)
p.yes(5)
p.no(2)

p.file("tmp.plotview")
p.save()

print("all done")
