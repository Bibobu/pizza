# simple test of xyz tool
# requires files/dump.peptide.*
# THESE FILES WERE NOT PROVIDED
# creates tmp*.xyz

from dump import dump
from xyz import xyz

d = dump("files/dump.peptide.*")
x = xyz(d)
x.one()
x.many()
x.single(0, "tmp.single")

print("all done ... type CTRL-D to exit Pizza.py")
