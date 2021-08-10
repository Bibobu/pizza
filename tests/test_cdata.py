# simple test of cdata tool
# creates tmp.cdata

from cdata import cdata
from gl import gl
from vcr import vcr

c = cdata()

print("Defining box")
c.box("box", 0, 0, 0, 10, 5, 5)
print("Defining Sphere")
c.sphere("nucleus", 7, 2, 2, 1)
print("Defining organelle")
c.cap("organelle", 'x', 2.5, 2.5, 1, 1.5, 3.5)
print("Defining nucleus 1")
c.q("nucleus", 5)
print("Defining union")
c.union("interior", "nucleus", "organelle")

print("Defining nucleus2")
c.surf("nuc", "nucleus")

print("Selecting")
c.surfselect("nuchalf", "nuc", "$z < 2.0")

print("Defining parts A")
c.part("A", 100, "box", "interior")

print("Defining parts B")
c.part("B", 100, "nucleus")

print("Defining parts C")
c.part2d("C", 100, "organelle")

print("Writing temp file")
c.write("tmp.cdata", "box", "nucleus", "organelle", "A", "B", "C")

print("Define lines")
c.lbox("linebox", 0, 0, 0, 10, 5, 5)
c.unselect()
c.select("A", "B", "C", "linebox", "organelle", "nuchalf")

# s = svg(c)
# s.rotate(0,0)
# s.lrad(0,0.1)
# s.lcol(0,"yellow")
# s.show(0)

g = gl(c)
v = vcr(g)
g.root.mainloop()

print("all done")
