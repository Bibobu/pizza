# simple test of patch tool
# creates tmp.data.patch file

from patch import patch

p = patch(0.5)
p.seed = 54321
p.build(100, "hex2", 1, 2, 3)
p.build(50, "tri5", 4, 5)

# Note that the patch lib does not write atom usinf full style.
# You need to add a charge column in order to visualise it in vmd
# using topotools

p.write("tmp.data.patch")

print("all done")
