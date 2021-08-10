# simple test of pair tool
# requires files/data.rhodo

from pair import pair
from data import data

p = pair("lj/charmm/coul/charmm")
d = data("files/data.rhodo")
p.coeff(d)
p.init(8.0, 10.0)
ev, ec = p.single(5.0, 1, 2, 0.5, -0.5)
print("Energies", ev, ec)

print("all done")
