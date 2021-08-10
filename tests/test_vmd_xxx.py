# simple test of vmd tool
# requires files/dump.peptide.only and files/dump.bond
# uses gl and vcr tools to visualize peptide molecule with bonds
# The vmd lib is still buggy and my objective is still to get rid of it.

from vmd import vmd

v = vmd()
v('menu main off')
v.rep('VDW')
v.new('files/peptide.pdb', 'pdb')
v.flush()

print("all done")
