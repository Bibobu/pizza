#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Pizza.py toolkit, www.cs.sandia.gov/~sjplimp/pizza.html
# Steve Plimpton, sjplimp@sandia.gov, Sandia National Laboratories
#
# Copyright (2005) Sandia Corporation.  Under the terms of Contract
# DE-AC04-94AL85000 with Sandia Corporation, the U.S. Government retains
# certain rights in this software.  This software is distributed under
# the GNU General Public License.
#
# log tool
#
# History
#   8/05, Steve Plimpton (SNL): original version
#   07/21 Germain Clavier: port to python 3 and small add-ons
#
# ToDo list
#  Check consistency of python3 version with gz files
#
# Classes
#   run = A simple container with fields names and data values
#   Variables
#     fields = the fields in byte
#     data = a dict with each fields as a key and corresponding data as values
#     style = style of LAMMPS log file, 1 = multi, 2 = one, 3 = gran
#     Note: What is gran? Never seen it.
#
#   log = A class reading/writing files and containing several runs instances
#   Variables
#     ptr = dictionary, key = name, value = index into data for which column
#     firststr = string that begins a thermo section in log file
#     increment = 1 if log file being read incrementally
#     eof = ptr into incremental file for where to start next read

# Imports and external programs

"""
--- THIS docstr CORRESPONDS TO THE PYTHON2 VERSION. IT NEEDS UPDATE---
Read LAMMPS log files and extract thermodynamic data

l = log("file1")                     read in one or more log files
l = log("log1 log2.gz")              can be gzipped
l = log("file*")                     wildcard expands to multiple files
l = log("log.lammps",0)              two args = store filename, but don't read

  incomplete and duplicate thermo entries are deleted

time = l.next()                      read new thermo info from file

  used with 2-argument constructor to allow reading thermo incrementally
  return time stamp of last thermo read
  return -1 if no new thermo since last read

nvec = l.nvec                        # of vectors of thermo info
nlen = l.nlen                        length of each vectors
names = l.names                      list of vector names
t,pe,... = l.get("Time","KE",...)    return one or more vectors of values
l.write("file.txt")                  write all vectors to a file
l.write("file.txt","Time","PE",...)  write listed vectors to a file

  get and write allow abbreviated (uniquely) vector names
"""


import sys
import re
import glob
from os import popen

try:
    PIZZA_GUNZIP
except NameError:
    PIZZA_GUNZIP = "gunzip"


# Classes definitions

# A run is simply a dict with keys and associated values
class run:
    def __init__(self):
        self.data = {}
        self.fields = []
        self.style = 0


# The log class per-se
class log:

    # --------------------------------------------------------------------

    def __init__(self, *args):
        self.nvec = 0
        self.names = []
        self.ptr = {}
        self.data = []
        self.runs = []

        # flist = list of all log file names

        words = args[0].split()
        self.flist = []
        for word in words:
            self.flist += glob.glob(word)
        if len(self.flist) == 0 and len(args) == 1:
            sys.exit("no log file specified")

        if len(args) == 1:
            self.increment = 0
            self.read_all()
        else:
            if len(self.flist) > 1:
                sys.exit("can only incrementally read one log file")
            self.increment = 1
            self.eof = 0

    # --------------------------------------------------------------------
    # read all thermo from all files

    def read_all(self):
        # self.read_header(self.flist[0])
        # if self.nvec == 0:
        #     sys.exit("log file has no values")

        # read all files

        for file in self.flist:
            self.read_one(file)
        print()

        # sort entries by timestep, cull duplicates

        # self.data.sort(self.compare)
        self.cull()
        self.nlen = len(self.data)
        print("read {:d} log entries".format(self.nlen))

    # --------------------------------------------------------------------

    def next(self):
        if not self.increment:
            sys.exit("cannot read incrementally")

        if self.nvec == 0:
            try:
                open(self.flist[0], 'rb')
            except FileNotFoundError:
                return -1
            # self.read_header(self.flist[0])
            if self.nvec == 0:
                return -1

        self.eof = self.read_one(self.flist[0], self.eof)
        return int(self.data[-1][0])

    # --------------------------------------------------------------------

    def get(self, *keys):
        if len(keys) == 0:
            sys.exit("no log vectors specified")

        # mapl = []
        # for key in keys:
        #     if key in self.ptr:
        #         mapl.append(self.ptr[key])
        #     else:
        #         count = 0
        #         for i in range(self.nvec):
        #             if self.names[i].find(key) == 0:
        #                 count += 1
        #                 index = i
        #         if count == 1:
        #             mapl.append(index)
        #         else:
        #             sys.exit("unique log vector {} not found".format(key))

        required = []
        for key in keys:
            required.append(key.lower())

        runs = []
        for r in self.runs:
            vecs = []
            for k in required:
                v = []
                for fi in r.fields:
                    field_str = fi.decode("utf-8")
                    if field_str.lower() == k:
                        v.extend(r.data[fi])
                vecs.append(v)
            runs.append(vecs)
        # for i in range(len(keys)):
        #     vecs.append(self.nlen * [0])
        #     for j in range(self.nlen):
        #         vecs[i][j] = self.data[j][mapl[i]]
        print(runs)

        return runs

    # --------------------------------------------------------------------

    def write(self, filename, split, *keys):
        restrict = []
        for key in keys:
            restrict.append(key.lower())

        if split:
            for i, r in enumerate(self.runs):
                fname = ''.join([filename, '.run', str(i)])
                with open(fname, "w") as f:
                    fields = []
                    for fi in r.fields:
                        field_str = fi.decode("utf-8")
                        if restrict and field_str.lower() not in restrict:
                            continue
                        else:
                            fields.append(field_str)
                    header = ''.join(['#', *[' {:>15}']*len(fields), '\n'])
                    f.write(header.format(*fields))
                    nentry = len(r.data[b'Step'])
                    for j in range(nentry):
                        f.write(' ')
                        for k in r.fields:
                            field_str = k.decode("utf-8")
                            if restrict and field_str.lower() not in restrict:
                                continue
                            else:
                                f.write(" {:>15}".format(r.data[k][j]))
                        f.write('\n')
        else:
            with open(filename, 'w') as f:
                for r in self.runs:
                    fields = []
                    for fi in r.fields:
                        field_str = fi.decode("utf-8")
                        if restrict and field_str.lower() not in restrict:
                            continue
                        else:
                            fields.append(field_str)
                    header = ''.join(['#', *[' {:>15}']*len(fields), '\n'])
                    f.write(header.format(*fields))
                    nentry = len(r.data[b'Step'])
                    for j in range(nentry):
                        f.write(' ')
                        for k in r.fields:
                            field_str = k.decode("utf-8")
                            if restrict and field_str.lower() not in restrict:
                                continue
                            else:
                                f.write(" {:>15}".format(r.data[k][j]))
                        f.write('\n')
                    f.write('\n')

    # --------------------------------------------------------------------

    def compare(self, a, b):
        if a[0] < b[0]:
            return -1
        elif a[0] > b[0]:
            return 1
        else:
            return 0

    # --------------------------------------------------------------------

    def cull(self):
        i = 1
        while i < len(self.data):
            if self.data[i][0] == self.data[i-1][0]:
                del self.data[i]
            else:
                i += 1

    # --------------------------------------------------------------------

    def read_header(self, file):
        str_multi = b"----- Step"
        str_one = b"Step "

        if file[-3:] == ".gz":
            txt = popen("%s -c %s" % (PIZZA_GUNZIP, file), 'rb').read()
        else:
            txt = open(file, 'rb').read()

        if txt.find(str_multi) >= 0:
            self.firststr = str_multi
            self.style = 1
        elif txt.find(str_one) >= 0:
            self.firststr = str_one
            self.style = 2
        else:
            return

        if self.style == 1:
            s1 = txt.find(self.firststr)
            s2 = txt.find(b"\n--", s1)
            if (s2 == -1):
                s2 = txt.find(b"\nLoop time of", s1)
            pattern = re.compile(b"\s(\S*)\s*=")
            keywords = re.findall(pattern, txt[s1:s2])
            keywords.insert(0, "Step")
            i = 0
            for keyword in keywords:
                self.names.append(keyword)
                self.ptr[keyword] = i
                i += 1

        else:
            s1 = txt.find(self.firststr)
            s2 = txt.find(b"\n", s1)
            line = txt[s1:s2]
            words = line.split()
            for i in range(len(words)):
                self.names.append(words[i])
                self.ptr[words[i]] = i

        self.nvec = len(self.names)

    # --------------------------------------------------------------------

    def read_one(self, *args):

        # read entire (rest of) file into txt

        file = args[0]
        if file[-3:] == ".gz":
            f = popen("%s -c %s" % (PIZZA_GUNZIP, file), 'rb')
        else:
            f = open(file, 'rb')

        # if 2nd arg exists set file ptr to that value
        if len(args) == 2:
            f.seek(args[1])
        txt = f.read()
        if file[-3:] == ".gz":
            eof = 0
        else:
            eof = f.tell()
        f.close()

        start = last = 0
        while not last:

            # chunk = contiguous set of thermo entries (line or multi-line)
            # s1 = 1st char on 1st line of chunk
            # s2 = 1st char on line after chunk
            # set last = 1 if this is last chunk in file, leave 0 otherwise
            # set start = position in file to start looking for next chunk
            # rewind eof if final entry is incomplete

            r = run()
            str_multi = b"----- Step"
            str_one = b"Step "

            # Finding next run (style is run dependent)
            s1_one = txt.find(str_one, start)
            s1_multi = txt.find(str_multi, start)
            if s1_one >= 0 and s1_multi >= 0:
                s1 = min(s1_one, s1_multi)
                r.style, r.firststr = (2, str_one) if s1 == s1_one else (1, str_multi)
            elif s1_one == -1:
                s1 = s1_multi
                r.style = 1
                r.firststr = str_multi
            elif s1_multi == -1:
                s1 = s1_one
                r.style = 2
                r.firststr = str_one
            else:
                last = 1
                break
            # s1 = txt.find(self.firststr, start)

            # Finding fields for current run
            if r.style == 2:
                eol = txt.find(b" \n", s1)
                # print(s1, eol)
                fields = txt[s1:eol].split()
                # print(fields)
                for i, field in enumerate(fields):
                    r.fields.append(field)
                    r.data[field] = []
                # print(r.fields, r.data)
            else:
                eos = txt.find(b"\n--", s1)
                # print(txt[s1:eos])
                fields_re = re.compile(b"\S*\s*=")
                fields = re.findall(fields_re, txt[s1:eos])
                # print(fields)
                for i, field in enumerate(fields):
                    r.fields.append(field.split()[0])
                    r.data[field.split()[0]] = []
                # print(r.fields, r.data)

            s2 = txt.find(b"Loop time of", start+1)

            # found s1,s2 with s1 before s2
            if s1 >= 0 and s2 >= 0 and s1 < s2:
                if r.style == 2:
                    s1 = txt.find(b"\n", s1) + 1
            # found s1,s2 with s2 before s1
            elif s1 >= 0 and s2 >= 0 and s2 < s1:
                s1 = 0
            # found s2, but no s1
            elif s1 == -1 and s2 >= 0:
                last = 1
                s1 = 0
            # found s1, but no s2
            elif s1 >= 0 and s2 == -1:
                last = 1
                if r.style == 1:
                    s2 = txt.rfind(b"\n--", s1) + 1
                else:
                    s1 = txt.find(b"\n", s1) + 1
                    s2 = txt.rfind(b"\n", s1) + 1
                eof -= len(txt) - s2
            # found neither
            # could be end-of-file section
            # or entire read was one chunk
            elif s1 == -1 and s2 == -1:
                # end of file, so exit
                # reset eof to "Loop"
                if txt.find(b"Loop time of", start) == start:
                    eof -= len(txt) - start
                    break

                # entire read is a chunk
                last = 1
                s1 = 0
                if r.style == 1:
                    s2 = txt.rfind(b"\n--", s1) + 1
                else:
                    s2 = txt.rfind(b"\n", s1) + 1
                eof -= len(txt) - s2
                if s1 == s2:
                    break

            # eol = txt.find(b" \n", s1)
            # print(txt[s1:eol])
            chunk = txt[s1:s2-1]
            start = s2

            # split chunk into entries
            # parse each entry for numeric fields, append to data

            if r.style == 1:
                sections = chunk.split(b"\n--")
                entries_re = re.compile(b"\S*\s*=\s*\S*")
                for section in sections:
                    entries = re.findall(entries_re, section)
                    # print(r.data)
                    for entry in entries:
                        field = entry.split(b'=')[0].strip()
                        value = entry.split(b'=')[1].strip()
                        if field == b'Step':
                            r.data[field].append(int(value))
                        else:
                            r.data[field].append(float(value))
                    # word1 = [re.search(pat1, section).group(1)]
                    # word2 = re.findall(pat2, section)
                    # words = word1 + word2
                    # self.data.append(list(map(float, words)))
            else:
                lines = chunk.split(b"\n")
                for line in lines:
                    words = line.split()
                    for i, word in enumerate(words):
                        field = r.fields[i]
                        if field == b'Step':
                            r.data[field].append(int(word))
                        else:
                            r.data[field].append(float(word))
                    self.data.append(list(map(float, words)))
            self.runs.append(r)

            # print(r.data)
            # print last timestep of chunk

            print(r.data[b'Step'][-1])
            # print(int(self.data[len(self.data)-1][0]))
            sys.stdout.flush()

        return eof
