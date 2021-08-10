# simple test of dump tool
# requires files/dump.peptide.only and files/dump.bond
# THESE FILES WERE NOT PROVIDED
# THE TEST SCRIPT IS NOT WORKING AT THE MOMENT
# uses gl and vcr tools to visualize peptide molecule with bonds

from dump import dump
from bdump import bdump
from gl import gl
from vcr import vcr

dm = dump("files/dump.peptide.only")
b = bdump("files/dump.bond")
b.map(1, "id", 2, "type", 3, "atom1", 4, "atom2")
dm.extra(b)
g = gl(dm)
v = vcr(g)

print("all done")
