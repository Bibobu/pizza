# simple test of pdbfile tool
# requires files/dump.peptide.* and files/peptide.pdb
# THESE FILES WERE NOT PROVIDED
# creates tmp*.pdb

from pdbfile import pdbfile
from dump import dump

d = dump("files/dump.peptide.*")
p = pdbfile("files/peptide", d)
p.one()
p.many()
p.single(0, "tmp.single")

n = flag = 0
while 1:
    index, time, flag = p.iterator(flag)
    if flag == -1:
        break
    p.single(time, "tmp.single")
    n += 1

print("Incrementally processed %d PDB files" % n)

print("all done")
