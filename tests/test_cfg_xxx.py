# simple test of cfg tool
# requires files/dump.peptide.*
# THESE FILES WERE NOT PROVIDED
# THE TEST SCRIPT IS NOT WORKING AT THE MOMENT
# creates tmp*.cfg

from dump import dump
from cfg import cfg

d = dump("files/dump.peptide.*")
d.sort()
x = cfg(d)
x.one()
x.many()
x.single(0, "tmp.single")

print("all done")
