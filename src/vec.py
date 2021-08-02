# Pizza.py toolkit, www.cs.sandia.gov/~sjplimp/pizza.html
# Steve Plimpton, sjplimp@sandia.gov, Sandia National Laboratories
#
# Copyright (2005) Sandia Corporation.  Under the terms of Contract
# DE-AC04-94AL85000 with Sandia Corporation, the U.S. Government retains
# certain rights in this software.  This software is distributed under
# the GNU General Public License.
#
# vec tool
#
#
#
# History
#   8/05, Steve Plimpton (SNL): original version
#
# ToDo list
#
# Variables
#   n = length of each vector
#   nvec = # of vectors
#   names = list of vector names
#   ptr = dictionary, key = name, value = index into data for which column
#   data[i][j] = 2d array of floats, i = 0 to # of entries, j = 0 to nvecs-1

"""
Create numeric vectors from columns in file or list of vecs
v = vec("file1")                    read in numeric vectors from a file
v = vec(array)                      array = list of numeric vectors

  skip blank lines and lines that start with non-numeric characters
  example array with 2 vecs = [[1,2,3,4,5], [10,20,30,40,50]]
  assigns names = "col1", "col2", etc

nvec = v.nvec                       # of vectors
nlen = v.nlen		            lengths of vectors
names = v.names		            list of vector names
x,y,... = l.get(1,"col2",...)       return one or more vectors of values
l.write("file.txt")	            write all vectors to a file
l.write("file.txt","col1",7,...)    write listed vectors to a file

  get and write allow abbreviated (uniquely) vector names or digits (1-Nvec)
"""

# Imports and external programs

import sys

# Class definition


class vec:

    # --------------------------------------------------------------------

    def __init__(self, data):
        self.data = []

        if isinstance(data, str):
            lines = open(data, "r").readlines()
            for line in lines:
                words = line.split()
                if len(words) and words[0][0] in "0123456789.-":
                    self.data.append(list(map(float, words)))
        elif isinstance(data, list):
            nlen = len(data[0])
            for dat in data[1:]:
                if len(dat) != nlen:
                    sys.exit("lists are not all same length")
            for i in range(nlen):
                values = [dat[i] for dat in data]
                self.data.append(list(map(float, values)))
        else:
            sys.exit("invalid argument to vec")

        if len(self.data) == 0:
            self.nlen = self.nvec = 0
        else:
            self.nlen = len(self.data)
            self.nvec = len(self.data[0])

        self.names = []
        for i in range(self.nvec):
            self.names.append(str("col%d" % (i + 1)))

        self.ptr = {}
        for i in range(self.nvec):
            self.ptr[self.names[i]] = i

        print("read %d vectors of length %d" % (self.nvec, self.nlen))

    # --------------------------------------------------------------------

    def get(self, *keys):
        if len(keys) == 0:
            sys.exit("no vectors specified")

        kmap = []
        for key in keys:
            if isinstance(key, int):
                kmap.append(key - 1)
            elif key in self.ptr:
                kmap.append(self.ptr[key])
            else:
                count = 0
                for i in range(self.nvec):
                    if self.names[i].find(key) == 0:
                        count += 1
                        index = i
                if count == 1:
                    kmap.append(index)
                else:
                    sys.exit("unique vector %s not found" % key)

        vecs = []
        for i in range(len(keys)):
            vecs.append(self.nlen * [0])
            for j in range(self.nlen):
                vecs[i][j] = self.data[j][kmap[i]]

        if len(keys) == 1:
            return vecs[0]
        else:
            return vecs

    # --------------------------------------------------------------------

    def write(self, filename, *keys):
        if len(keys):
            kmap = []
            for key in keys:
                if isinstance(key, int):
                    kmap.append(key - 1)
                elif key in self.ptr:
                    kmap.append(self.ptr[key])
                else:
                    count = 0
                    for i in range(self.nvec):
                        if self.names[i].find(key) == 0:
                            count += 1
                            index = i
                    if count == 1:
                        kmap.append(index)
                    else:
                        sys.exit("unique vector %s not found" % key)
        else:
            kmap = range(self.nvec)

        f = open(filename, "w")
        for i in range(self.nlen):
            for j in range(len(kmap)):
                f.write("{}".format(self.data[i][kmap[j]]))
            f.write("\n")
        f.close()
