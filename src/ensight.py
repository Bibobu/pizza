# Pizza.py toolkit, www.cs.sandia.gov/~sjplimp/pizza.html
# Steve Plimpton, sjplimp@sandia.gov, Sandia National Laboratories
#
# Copyright (2005) Sandia Corporation.  Under the terms of Contract
# DE-AC04-94AL85000 with Sandia Corporation, the U.S. Government retains
# certain rights in this software.  This software is distributed under
# the GNU General Public License.
#
# ensight tool
#
#
# History
#   10/06, Steve Plimpton (SNL): original version
#
# ToDo list
#   binary files
#   create vector or tensor variable files, not just scalar
#     via pair of args like ["vx","vy","vz"],"vel"
#
# Variables
#   data = data file to read from
#   which = 0 for particles, 1 for elements
#   change = 0 for unchanging mesh coords, 1 for changing mesh coords (def = 0)

"""
Convert LAMMPS snapshots or meshes to Ensight format
e = ensight(d)       d = object with atoms or elements (dump,data,mdump)
e.change = 1         set to 1 if element nodal xyz change with time (def = 0)
e.maxtype = 10       max particle type, set if query to data will be bad

e.one()
e.one("new")
e.one("cns","Centro","eng","Energy")
e.one("new","cns","Centro","eng","Energy")
                     write all snapshots as an Ensight data set
                     Ensight header file = tmp.case (no 1st arg) or new.case
                     Ensight coord file = tmp.xyz or new.xyz
                     additional pairs of args create auxiliary files:
                       tmp.cns, tmp.eng or new.cns, new.eng
                     cns,eng = column name in dump file and file name suffix
                     Centro,Energy = Ensight name for the variable

e.increment()        same args as one(), but process dump out-of-core

e.many()             same args as one(), but create multiple Ensight files
                     tmp0000.xyz, tmp0001.xyz, etc
                     new0000.cns, new0001.cns, etc
                     new0000.eng, new0001.eng, etc

e.single(N)          same args as one() prepended by N, but write a single snap
"""

# Imports and external programs

import sys
import types

# Class definition


class ensight:

    # --------------------------------------------------------------------

    def __init__(self, data):
        self.change = 0
        self.maxtype = 0
        self.data = data
        if type(data) is types.InstanceType and ".dump" in str(data.__class__):
            self.which = 0
        elif type(data) is types.InstanceType and ".data" in str(data.__class__):
            self.which = 0
        elif type(data) is types.InstanceType and ".mdump" in str(data.__class__):
            self.which = 1
        elif type(data) is types.InstanceType and ".cdata" in str(data.__class__):
            self.which = 1
        else:
            sys.exit("unrecognized object passed to ensight")

    # --------------------------------------------------------------------

    def one(self, *args):
        if len(args) % 2 == 0:
            root = "tmp"
        else:
            root = args[0]
            args = args[1:]

        pairs = []
        for i in range(0, len(args), 2):
            pairs.append([args[i], args[i + 1]])

        # max # of types for all steps in Ensight files

        if self.which == 0 and self.maxtype == 0:
            self.maxtype = self.data.maxtype()

        # write Ensight *.case header file

        f = open("%s.case" % root, "w")
        times = self.data.time()
        self.case_file(f, root, pairs, 0, len(times), times)
        f.close()

        # open additional files

        f = open(root + ".xyz", "w")
        vfiles = []
        for pair in pairs:
            vfiles.append(open(root + "." + pair[0], "w"))

        # loop over snapshots
        # write coords into xyz file, variables into their files

        first = 1
        n = flag = etype = 0
        while 1:
            which, time, flag = self.data.iterator(flag)
            if flag == -1:
                break

            if self.which == 0:
                f.write("BEGIN TIME STEP\n")
                time, box, atoms, bonds, tris, lines = self.data.viz(which)
                self.coord_file_atoms(f, box, atoms)
                f.write("END TIME STEP\n")
            elif self.change == 0 and first:
                f.write("BEGIN TIME STEP\n")
                time, box, nodes, elements, nvalues, evalues = self.data.mviz(which)
                self.coord_file_elements(f, box, nodes, elements)
                etype = len(elements[0])
                first = 0
                f.write("END TIME STEP\n")
            elif self.change:
                f.write("BEGIN TIME STEP\n")
                time, box, nodes, elements, nvalues, evalues = self.data.mviz(which)
                self.coord_file_elements(f, box, nodes, elements)
                etype = len(elements[0])
                f.write("END TIME STEP\n")

            for i in range(len(pairs)):
                vfiles[i].write("BEGIN TIME STEP\n")
                values = self.data.vecs(time, pairs[i][0])
                if self.which == 0:
                    self.variable_file_atoms(vfiles[i], pairs[i][1], atoms, values)
                else:
                    self.variable_file_elements(vfiles[i], pairs[i][1], etype, values)
                vfiles[i].write("END TIME STEP\n")

            print(time)
            sys.stdout.flush()
            n += 1

        # close additional files

        f.close()
        for f in vfiles:
            f.close()

        print("\nwrote %s snapshots in Ensight format" % n)

    # --------------------------------------------------------------------

    def increment(self, *args):
        if len(args) % 2 == 0:
            root = "tmp"
        else:
            root = args[0]
            args = args[1:]

        pairs = []
        for i in range(0, len(args), 2):
            pairs.append([args[i], args[i + 1]])

        # max # of types for all steps in Ensight files

        if self.which == 0 and self.maxtype == 0:
            self.maxtype = self.data.maxtype()

        # open additional files

        f = open(root + ".xyz", "w")
        vfiles = []
        for pair in pairs:
            vfiles.append(open(root + "." + pair[0], "w"))

        # loop over snapshots
        # write coords into xyz file, variables into their files

        times = []
        first = 1
        n = etype = 0
        while 1:
            time = self.data.next()
            if time == -1:
                break
            times.append(time)
            self.data.tselect.one(time)
            self.data.delete()

            if self.which == 0:
                f.write("BEGIN TIME STEP\n")
                time, box, atoms, bonds, tris, lines = self.data.viz(0)
                self.coord_file_atoms(f, box, atoms)
                f.write("END TIME STEP\n")
            elif self.change == 0 and first:
                f.write("BEGIN TIME STEP\n")
                time, box, nodes, elements, nvalues, evalues = self.data.mviz(0)
                self.coord_file_elements(f, box, nodes, elements)
                etype = len(elements[0])
                first = 0
                f.write("END TIME STEP\n")
            elif self.change:
                f.write("BEGIN TIME STEP\n")
                time, box, nodes, elements, nvalues, evalues = self.data.mviz(0)
                self.coord_file_elements(f, box, nodes, elements)
                etype = len(elements[0])
                f.write("END TIME STEP\n")

            for i in range(len(pairs)):
                vfiles[i].write("BEGIN TIME STEP\n")
                values = self.data.vecs(time, pairs[i][0])
                if self.which == 0:
                    self.variable_file_atoms(vfiles[i], pairs[i][1], atoms, values)
                else:
                    self.variable_file_elements(vfiles[i], pairs[i][1], etype, values)
                vfiles[i].write("END TIME STEP\n")

            print(time)
            sys.stdout.flush()
            n += 1

        # close additional files

        f.close()
        for f in vfiles:
            f.close()

        # write Ensight *.case header file now that know all timesteps

        f = open("%s.case" % root, "w")
        self.case_file(f, root, pairs, 0, len(times), times)
        f.close()

        print("\nwrote %s snapshots in Ensight format" % n)

    # --------------------------------------------------------------------

    def many(self, *args):
        if len(args) % 2 == 0:
            root = "tmp"
        else:
            root = args[0]
            args = args[1:]

        pairs = []
        for i in range(0, len(args), 2):
            pairs.append([args[i], args[i + 1]])

        # max # of types for all steps in Ensight files

        if self.which == 0 and self.maxtype == 0:
            self.maxtype = self.data.maxtype()

        # write Ensight *.case header file

        f = open("%s.case" % root, "w")
        times = self.data.time()
        self.case_file(f, root, pairs, 1, len(times), times)
        f.close()

        # loop over snapshots
        # generate unique filenames
        # write coords into one xyz file per snapshot, variables into their files

        first = 1
        n = flag = etype = 0
        while 1:
            which, time, flag = self.data.iterator(flag)
            if flag == -1:
                break

            files = []
            if n < 10:
                file = root + "000" + str(n) + ".xyz"
                for pair in pairs:
                    files.append(root + "000" + str(n) + "." + pair[0])
            elif n < 100:
                file = root + "00" + str(n) + ".xyz"
                for pair in pairs:
                    files.append(root + "00" + str(n) + "." + pair[0])
            elif n < 1000:
                file = root + "0" + str(n) + ".xyz"
                for pair in pairs:
                    files.append(root + "0" + str(n) + "." + pair[0])
            else:
                file = root + str(n) + ".xyz"
                for pair in pairs:
                    files.append(root + str(n) + "." + pair[0])

            if self.which == 0:
                f = open(file, "w")
                time, box, atoms, bonds, tris, lines = self.data.viz(which)
                self.coord_file_atoms(f, box, atoms)
                f.close()
            elif self.change == 0 and first:
                f = open(root + ".xyz", "w")
                time, box, nodes, elements, nvalues, evalues = self.data.mviz(which)
                self.coord_file_elements(f, box, nodes, elements)
                etype = len(elements[0])
                first = 0
                f.close()
            elif self.change:
                f = open(file, "w")
                time, box, nodes, elements, nvalues, evalues = self.data.mviz(which)
                self.coord_file_elements(f, box, nodes, elements)
                etype = len(elements[0])
                f.close()

            for i in range(len(pairs)):
                values = self.data.vecs(time, pairs[i][0])
                f = open(files[i], "w")
                if self.which == 0:
                    self.variable_file_atoms(f, pairs[i][1], atoms, values)
                else:
                    self.variable_file_elements(f, pairs[i][1], etype, values)
                f.close()

            print(time)
            sys.stdout.flush()
            n += 1

        print("\nwrote %s snapshots in Ensight format" % n)

    # --------------------------------------------------------------------

    def single(self, time, *args):
        if len(args) % 2 == 0:
            root = "tmp"
        else:
            root = args[0]
            args = args[1:]

        pairs = []
        for i in range(0, len(args), 2):
            pairs.append([args[i], args[i + 1]])

        # max # of types for all steps in Ensight files

        if self.which == 0 and self.maxtype == 0:
            self.maxtype = self.data.maxtype()

        # write Ensight *.case header file

        f = open("%s.case" % root, "w")
        self.case_file(f, root, pairs, 0, 1, [time])
        f.close()

        # write coords into xyz file, variables into their files

        which = self.data.findtime(time)
        etype = 0

        f = open(root + ".xyz", "w")
        if self.which == 0:
            time, box, atoms, bonds, tris, lines = self.data.viz(which)
            self.coord_file_atoms(f, box, atoms)
        else:
            time, box, nodes, elements, nvalues, evalues = self.data.mviz(which)
            self.coord_file_elements(f, box, nodes, elements)
            etype = len(elements[0])
        f.close()

        for i in range(len(pairs)):
            values = self.data.vecs(time, pairs[i][0])
            f = open(root + "." + pairs[i][0], "w")
            if self.which == 0:
                self.variable_file_atoms(f, pairs[i][1], atoms, values)
            else:
                self.variable_file_elements(f, pairs[i][1], etype, values)
            f.close()

    # --------------------------------------------------------------------
    # write Ensight case file

    def case_file(self, f, root, pairs, multifile, nsnaps, times):
        f.write("# Ensight case file\n")
        f.write("FORMAT\ntype: ensight gold\n")

        if self.which == 0:
            if multifile:
                #        print >>f,"GEOMETRY\nmodel: %s****.xyz change_coords_only\n" % root
                f.write("GEOMETRY\nmodel: %s****.xyz\n" % root)
            else:
                #        print >>f,"GEOMETRY\nmodel: 1 1 %s.xyz change_coords_only\n" % root
                f.write("GEOMETRY\nmodel: 1 1 %s.xyz\n" % root)
        else:
            if self.change == 0:
                f.write("GEOMETRY\nmodel: %s.xyz\n" % root)
            elif multifile:
                f.write("GEOMETRY\nmodel: %s****.xyz\n" % root)
            else:
                f.write("GEOMETRY\nmodel: 1 1 %s.xyz\n" % root)

        if len(pairs):
            f.write("VARIABLE\n")
            for pair in pairs:
                if self.which == 0:
                    if multifile:
                        f.write("scalar per node: %s %s****.%s\n" % (
                            pair[1],
                            root,
                            pair[0],
                            )
                        )
                    else:
                        f.write("scalar per node: 1 1 %s %s.%s\n" % (
                            pair[1],
                            root,
                            pair[0],
                            )
                        )
                else:
                    if multifile:
                        f.write("scalar per element: %s %s****.%s\n" % (
                            pair[1],
                            root,
                            pair[0],
                            )
                        )
                    else:
                        f.write("scalar per element: 1 1 %s %s.%s\n" % (
                            pair[1],
                            root,
                            pair[0],
                            )
                        )

        f.write("TIME\n")
        f.write("time set: 1\n")
        f.write("number of steps: {}\n".format(nsnaps))
        f.write("filename start number: 0\n")
        f.write("filename increment: 1\n")
        f.write("time values:\n")
        for i in range(nsnaps):
            f.write("{}\n".format(times[i]))
            if i % 10 == 9:
                f.write("\n")
        f.write("\n")
        f.write("\n")

        if not multifile:
            f.write("FILE\n")
            f.write("file set: 1\n")
            f.write("number of steps: {}\n".format(nsnaps))

    # --------------------------------------------------------------------
    # write Ensight coordinates for atoms
    # partition into "parts"
    # one part = coords for all atoms of a single type

    def coord_file_atoms(self, f, box, atoms):
        f.write("Particle geometry\nfor a collection of atoms\n")
        f.write("node id given\n")
        f.write("element id off\n")
        f.write("extents\n")
        f.write("%12.5e%12.5e\n" % (box[0], box[3]))
        f.write("%12.5e%12.5e\n" % (box[1], box[4]))
        f.write("%12.5e%12.5e\n" % (box[2], box[5]))

        for t in range(1, self.maxtype + 1):
            f.write("part\n")
            f.write("%10d\n" % t)
            f.write("type\n", t)
            f.write("coordinates\n")
            group = [atom for atom in atoms if int(atom[1]) == t]
            f.write("%10d\n" % len(group))
            for atom in group:
                f.write("%10d\n" % int(atom[0]))
            for atom in group:
                f.write("%12.5e\n" % atom[2])
            for atom in group:
                f.write("%12.5e\n" % atom[3])
            for atom in group:
                f.write("%12.5e\n" % atom[4])
            f.write("point\n")
            f.write("%10d\n" % len(group))
            for i in range(1, len(group) + 1):
                f.write("%10d\n" % i)

    # --------------------------------------------------------------------
    # write Ensight coordinates for elements

    def coord_file_elements(self, f, box, nodes, elements):
        f.write("Element geometry\nfor a collection of elements\n")
        f.write("node id given\n")
        f.write("element id given\n")
        f.write("extents\n")
        f.write("%12.5e%12.5e\n" % (box[0], box[3]))
        f.write("%12.5e%12.5e\n" % (box[1], box[4]))
        f.write("%12.5e%12.5e\n" % (box[2], box[5]))

        f.write("part\n")
        f.write("%10d\n" % 1)
        f.write("all elements\n")
        f.write("coordinates\n")
        f.write("%10d\n" % len(nodes))
        for node in nodes:
            f.write("%10d\n" % int(node[0]))
        for node in nodes:
            f.write("%12.5e\n" % node[2])
        for node in nodes:
            f.write("%12.5e\n" % node[3])
        for node in nodes:
            f.write("%12.5e\n" % node[4])

        if len(elements[0]) == 5:
            f.write("tria3\n")
        elif len(elements[0]) == 6:
            f.write("tetra4\n")
        else:
            sys.exit("unrecognized element type")
        f.write("%10d\n" % len(elements))

        for element in elements:
            f.write("%10d\n" % int(element[0]))
        if len(elements[0]) == 5:
            for element in elements:
                f.write("%10d%10d%10d\n" % (
                    int(element[2]),
                    int(element[3]),
                    int(element[4]),
                    )
                )
        elif len(elements[0]) == 6:
            for element in elements:
                f.write("%10d%10d%10d%10d\n" % (
                    int(element[2]),
                    int(element[3]),
                    int(element[4]),
                    int(element[5]),
                    )
                )

    # --------------------------------------------------------------------
    # write Ensight variable values for atoms
    # partition into "parts"
    # one part = values for all atoms of a single type

    def variable_file_atoms(self, f, name, atoms, values):
        f.write("Particle %s\n" % name)
        for t in range(1, self.maxtype + 1):
            f.write("part\n")
            f.write("%10d\n" % t)
            f.write("coordinates\n")
            group = [values[i] for i in range(len(atoms)) if int(atoms[i][1]) == t]
            for value in group:
                f.write("%12.5e\n" % value)

    # --------------------------------------------------------------------
    # write Ensight variable values for elements

    def variable_file_elements(self, f, name, etype, values):
        f.write("Element %s\n" % name)
        f.write("part\n")
        f.write("%10d\n" % 1)
        if etype == 5:
            f.write("tria3\n")
        elif etype == 6:
            f.write("tetra4\n")
        for value in values:
            f.write("%12.5e\n" % value)
