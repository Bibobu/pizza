# simple test of log tool
# requires files/log.obstacle
# creates tmp.log and tmp.log.two

from log import log

# This is a log file from a very old lammps version
# It needs to be tested with a new one
lg = log("files/log.obstacle")

print("# of vectors = ", lg.nvec)
print("length of vectors = ", lg.nlen)
print("names of vectors = ", lg.names)

time, temp, press = lg.get("Step", "Temperature", "Pressure")[0]
print("temp :\n", temp)
print("press :\n", press)
lg.write("tmp.log")
lg.write("tmp.log.two", "Step", "E_pair")

print("all done")
