# simple test of clog tool
# requires files/log.ccell
# creates tmp.clog and tmp.clog.two

from log import log
c = log("files/log.ccell")

print("# of vectors =", c.nvec)
print("length of vectors =", c.nlen)
print("names of vectors =", c.names)

time, a, b = c.get("Step", "prey", "predator")[0]
print("a: ", a)
print("b: ", b)
c.write("tmp.clog")
c.write("tmp.clog.two", "Step", "prey")

print("all done")
