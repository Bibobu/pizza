# simple test of xyz tool
# requires files/dump.micelle.*
# THIS FILE WAS NOT PROVIDED
# creates tmp*.case, etc

from dump import dump
from ensight import ensight

d = dump("files/dump.micelle")
e = ensight(d)
e.one()
e.many()
e.single(0)

print("all done ... type CTRL-D to exit Pizza.py")
