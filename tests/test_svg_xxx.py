# simple test of svg tool
# requires files/dump.kinase
# THIS FILE WAS NOT PROVIDED
# creates tmp*.png

from dump import dump
from svg import svg
from vizinfo import colors

d = dump("files/dump.kinase")
s = svg(d)

s.bg("white")
s.rotate(60, 130)
s.box(1)
s.file = "tmp"

print("kill image window when ready to contine ...")
s.show(0)
s.all()

s.acol([1, 4, 6, 8, 9], ["gray", "red", "blue", "green", "yellow"])
s.arad(list(range(9)), 0.3)
s.label(0.2, 0.4, 'h', 15, "red", "test label #1")
s.label(-0.2, -0.4, 'h', 15, "yellow", "test label #2")

print("kill image window when ready to contine ...")
s.show(0)
s.pan(60, 130, 1, 60, 30, 0.5)
s.all(0, 10, 0)

print("all done")
