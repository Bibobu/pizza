# Pizza.py toolkit, www.cs.sandia.gov/~sjplimp/pizza.html
# Steve Plimpton, sjplimp@sandia.gov, Sandia National Laboratories
#
# Copyright (2005) Sandia Corporation.  Under the terms of Contract
# DE-AC04-94AL85000 with Sandia Corporation, the U.S. Government retains
# certain rights in this software.  This software is distributed under
# the GNU General Public License.
#
# plotview tool
#
#
#
# History
#   8/05, Matt Jones (BYU): original version
#
# ToDo list
#   option to plot all N vectors against linear index?
#
# Variables
#   source = source of vector data
#   plot = plotting object
#   nplots = # of plots (not including 1st vector)
#   names = names of plots (from vector source)
#   radiovar = index of clicked radio button (0 = none, 1-N)
#   checkbuttons = list of check button objects
#   checkvars = list of status of check buttons
#   checkold = list of status of check buttons before click

"""
Plot multiple vectors from a data set
p = plotview(d,pl)      create GUI for viewing plots

  d = Pizza.py object that contains vectors (log, vec)
  pl = Pizza.py plotting object (gnu, matlab)

p.select(2)             select one plot as current (1-N)
p.yes(3)                toggle one plot's visibility
p.no(3)

  only one plot is selected at a time
  multiple plots can be visible at same time
  select is same as clicking on left-side radio-button
  yes/no is same as clicking on right-side checkbox

p.x = "Time"            which vector is X vector (1st vec by default)
p.file("pressure")      filename prefix for saving a plot
p.save()                save currently selected plot to file.eps
"""

# Imports and external programs

import sys
import re
import glob
import time
import tkinter as tk

# Class definition


class plotview:

    # --------------------------------------------------------------------

    def __init__(self, source, plot):
        self.source = source
        self.plot = plot

        # create GUI

        # from __main__ import tkroot

        tkroot = tk.Tk()
        root = tk.Toplevel(tkroot)
        root.title("Pizza.py plotview tool")

        self.frame1 = tk.Frame(root)
        self.frame2 = tk.Frame(root)
        self.frame3 = tk.Frame(root)

        tk.Button(self.frame1, text="Print As:", command=self.save).pack(side=tk.TOP)
        self.entry = tk.Entry(self.frame1, width=16)
        self.entry.insert(0, "tmp")
        self.entry.pack(side=tk.TOP)

        tk.Label(self.frame2, text="Select").pack(side=tk.LEFT)
        tk.Label(self.frame2, text="Display").pack(side=tk.RIGHT)

        self.nplots = source.nvec
        self.names = source.names
        self.x = self.names[0]

        self.radiovar = tk.IntVar()
        self.checkbuttons = []
        self.checkvars = []
        self.checkold = []

        # for each vector (not including 1st)
        # create a plot and title it
        # create a line in GUI with selection and check button

        for i in range(self.nplots):
            self.plot.select(i + 1)
            self.plot.xtitle(self.x)
            self.plot.ytitle(self.names[i])
            self.plot.title(self.names[i])

            b = tk.BooleanVar()
            b.set(0)
            self.checkvars.append(b)
            self.checkold.append(0)

            line = tk.Frame(self.frame3)
            rtitle = "%d %s" % (i + 1, self.names[i])
            tk.Radiobutton(
                line,
                text=rtitle,
                value=i + 1,
                variable=self.radiovar,
                command=self.radioselect,
            ).pack(side=tk.LEFT)
            cbutton = tk.Checkbutton(line, variable=b, command=self.check)
            cbutton.pack(side=tk.RIGHT)
            self.checkbuttons.append(cbutton)
            line.pack(side=tk.TOP, fill=tk.X)

        self.radiovar.set(0)
        self.frame1.pack(side=tk.TOP)
        self.frame2.pack(side=tk.TOP, fill=tk.X)
        self.frame3.pack(side=tk.TOP, fill=tk.X)

    # --------------------------------------------------------------------
    # set radio button and checkbox

    def select(self, n):
        self.plot.select(n)
        self.radiovar.set(n)
        self.yes(n)

    # --------------------------------------------------------------------
    # only invoke if currently unset

    def yes(self, n):
        if not self.checkvars[n - 1].get():
            self.checkbuttons[n - 1].invoke()

    # --------------------------------------------------------------------
    # only invoke if currently set

    def no(self, n):
        if self.checkvars[n - 1].get():
            self.checkbuttons[n - 1].invoke()

    # --------------------------------------------------------------------

    def file(self, newtext):
        oldtext = self.entry.get()
        self.entry.delete(0, len(oldtext))
        self.entry.insert(0, newtext)

    # --------------------------------------------------------------------

    def save(self):
        n = self.radiovar.get()
        if n == 0:
            sys.exit("no plot selected")
        name = self.entry.get()
        self.plot.save(name)

    # --------------------------------------------------------------------
    # called when any radio selection button is clicked

    def radioselect(self):
        self.select(self.radiovar.get())

    # --------------------------------------------------------------------
    # called when any checkbox is clicked
    # draws or hides plot
    # loop is to find which checkbox changed status
    # grab x,y data to plot out of source object

    def check(self):
        for i in range(self.nplots):
            if int(self.checkvars[i].get()) != self.checkold[i]:
                if self.checkvars[i].get():
                    self.radiovar.set(i + 1)
                    self.plot.select(i + 1)
                    self.plot.xtitle(self.x)
                    x, y = self.source.get(self.x, self.names[i])
                    self.plot.plot(x, y)
                else:
                    if self.radiovar.get() == i + 1:
                        self.radiovar.set(0)
                    self.plot.hide(i + 1)
                self.checkold[i] = int(self.checkvars[i].get())

    # --------------------------------------------------------------------
    # called by lammps() tool to update all visible plots with new data

    def refresh(self):
        for i in range(self.nplots):
            if self.checkvars[i].get():
                self.plot.select(i + 1)
                self.plot.xtitle(self.x)
                x, y = self.source.get(self.x, self.names[i])
                self.plot.plot(x, y)
