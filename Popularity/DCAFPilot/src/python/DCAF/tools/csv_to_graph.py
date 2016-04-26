#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=
"""
File        : csv_to_graph.py
Author      : Mantas Briliauskas <mbriliauskas AT gmail dot com>
Description : package for plotting model verification results
"""

from __future__ import print_function

# system modules
import os
import sys
import optparse
import datetime
import numpy as np
import datetime
import matplotlib
from matplotlib import pyplot as plt
from matplotlib.dates import date2num
from matplotlib.pyplot import cm

# package modules
from DCAF.utils.utils import fopen

class OptionParser(object):
    def __init__(self):
        self.parser = optparse.OptionParser()
        self.parser.add_option("--fin", action="store", type="string",
            dest="fin", default=".", help="Input file, file list or directory, default '.'")
        self.parser.add_option("--fbeg", action="store", type="string",
            dest="fbeg", default="", help="Filter files by beginning, default None")
        self.parser.add_option("--fend", action="store", type="string",
            dest="fend", default="", help="Filter files by ending, default None")
        self.parser.add_option("--fout", action="store", type="string",
            dest="fout", default="graph.png", help="File name to store graph, default graph.png")
        self.parser.add_option("--timein", action="store", type="string",
            dest="timein", default=None, help="File name of models running time, *.csv, default None")
        self.parser.add_option("--labels", action="store", type="int",
            dest="labels", default=0, help="Option to display data labels, 0 for no, default 0")
        self.parser.add_option("--x-eq", action="store_true",
            dest="xeq", help="Flag to equalize step for x axis")
        self.parser.add_option("--leg", action="store", type="int",
            dest="leg", default=None, help="Option to show legend for one particular graph only. Provide id from 1, default None")
        self.parser.add_option("--col-rb", action="store_true",
            dest="colrb", help="Use rainbow colors")
    def options(self):
        return self.parser.parse_args()

def plot(data, dates, fout, rundata, labels, xeq, leg, colrb):
    "Plots data according the dates"
    if len(data) == 0:
        print("Error: no data provided.")
        sys.exit(1)
    # number of subplots per width
    nx = max([len(data[t]) for t in data.iterkeys()])
    # running time plotting space
    if  rundata:
        nx += 1
    # number of subplots per height
    ny = len(data)
    ni = 0
    matplotlib.rcParams.update({'font.size': 10})
    fig = plt.figure(figsize=(15,10)) if rundata else plt.figure(figsize=(10,10))
    fig.subplots_adjust(wspace=0.3, hspace=0.8)
    c   = None
    for dftype in sorted(data.keys(), reverse=True):
        if  xeq:
            x = np.arange(len(dates[dftype]))
        else:
            # load dates - new and old data may provide differently
            x = [date2num(datetime.datetime.strptime(str(d), "%Y%m%d")) for d in dates[dftype]]
        # subplot every scorer
        for s in data[dftype]:
            if  colrb:
                col = iter(cm.rainbow(np.linspace(0,1,len(data[dftype][s]))))
            pls = []
            lab = []
            ni  += 1
            if  rundata:
                g = fig.add_subplot(ny, nx, ni+ni/nx)
            else:
                g = fig.add_subplot(ny, nx, ni)
            # graph every classifier
            for clf in data[dftype][s]:
                if  s.lower() == 'auc' and 'ensemble' in clf.lower():
                    continue
                y = data[dftype][s][clf]
                if  len(dates[dftype]) != len(y):
                    print("Error; %s data contain %d dates, but %d data points for %s provided in --fin:" % (dftype, len(dates[dftype]), len(y), clf))
                    sys.exit(1)
                if  colrb:
                    c = next(col)
                plot, = g.plot_date(x=x, y=y, label=clf, fmt="-", color=c, marker='o')
                if  labels:
                    # display labels between 0.10 and 0.90
                    for i, yv in enumerate(y):
                        g.annotate("(%.2f%%)" % (yv*100) \
                            if  yv<=0.90 and yv>=0.10 else "", xy=(x[i],yv), textcoords='data')
                g.grid(True)
                g.set_xticks(x)
                xstep = x[1]-x[0]
                g.set_xlim(min(x)-xstep,max(x)+xstep)
                g.set_ylim(0, 1.003)
                g.set_yticks([0.2*t for t in xrange(0,6)])
                g.set_xticklabels(dates[dftype], rotation=45, ha="right")
                g.set_yticklabels(["{:3.2f}%".format(v*100) for v in g.get_yticks()])
                g.set_title("Classifiers validation using %s dataframe, %s (%%)" % (dftype.lower(), s.upper()), fontsize=10, y=1.01)
                pls.append(plot)
                lab.append("%s (%.2f%%)" % (clf, 100*np.mean(data[dftype][s][clf])))
            # checking avg of data to adjust legend position
            ssum = sum([sum(data[dftype][s][clf]) for clf in data[dftype][s]])
            snum = sum([len(data[dftype][s][clf]) for clf in data[dftype][s]])
            # TODO: adjust left-right also against averages
            lloc = 'upper left' if ssum/snum < 0.20 else 'lower left'
            if  not leg or ni == leg:
                # 'best' loc does not provide best option in this place
                l = g.legend(pls, lab, loc=lloc, prop={'size':8}, fancybox=True)
                l.get_frame().set_alpha(0.6)
    # plot of model running time
    if  rundata:
        g = fig.add_subplot(1, nx, nx)
        c = rundata.keys()
        x = np.arange(len(c))
        # hour scale
        y = [v/3600. for v in rundata.values()]
        if  y:
            g.grid()
            g.set_xticks(x)
            g.set_xticklabels(c, rotation=45, ha='right', fontsize=8)
            g.set_title("Classifiers running time (hours)", fontsize=10, y=1.01)
            g.set_xlim(-1, len(c))
            ax = g.bar(x, y, width=0.5, align='center', alpha=0.5)
            y_bottom, y_top = g.get_ylim()
            y_height = y_top - y_bottom
            if labels:
                for i, child in enumerate(g.containers[0].get_children()):
                    h = child.get_y() + child.get_height() + y_height * 0.01
                    g.text(child.get_x() + child.get_width()/2., h,
                        "(%.2fh)" % y[i], ha='center', va='bottom')
    fig.tight_layout()
    fig.savefig(fout, bbox_inches='tight')

def str_to_num(v):
    "Convert data string to number"
    if v.lower() == "n/a" or v.lower == "nan":
        return 0
    try:
        return int(v)
    except:
        try:
            return float(v)
        except:
            raise Exception("Error: Not possible to convert value %s to num" % v)

def read_data(fin, fbeg, fend, timein):
    "Selects files and picks structured data for plotting"
    if  fin == ".":
        files = [f for f in os.listdir('.') \
                    if (len(fbeg) == 0 or f.startswith(fbeg))
                    and (len(fend) == 0 or f.endswith(fend))]
    elif os.path.isdir(fin):
        files = [os.path.join(fin, f) for f in os.listdir(fin)  \
                    if (len(fbeg) == 0 or f.startswith(fbeg))
                    and (len(fend) == 0 or f.endswith(fend))]        
    elif os.path.isfile(fin):
        # if one file passed, its fn not checked
        files = [fin]
    else:
        print("Cannot produce file list, not a file or directory: \"%s\"" % fin)
        raise SystemExit
    ### data structure:
    #   { dftypes: { scorers: { classifiers: [ ordered weekly results for particular dftype, scorer and classifier ] } } }
    # dftype is dataframe type: old or new
    # dates variable stores ordered dates with an idea that dates in csv
    #   are stored respectfully in same order for all dftype and
    #   classifier combinations
    data    = {}
    dates   = {}
    scorers = []
    headers = []
    rundata = {}
    # read classifiers scores
    for f in files:
        first = True
        for line in fopen(f).readlines():
            vals = line.strip(" \n\r").split(',')
            if  first:
                first = False
                if  not headers:
                    headers = vals
                    if      headers[0] != 'dftype'  \
                        or  headers[1] != 'clf'     \
                        or  headers[2] != 'date'    \
                        or  len(headers) < 4:
                        print("Error: check structure of file %s, headers should be: dftype,clf,date" % f)
                        sys.exit(1)
                    scorers = headers[3:]
                elif headers != vals:
                    print("Original headers: %s" % headers)
                    print("Headers in %s: %s" % (f, vals))
                    sys.exit(1)
            else:
                row = dict(zip(headers, vals))
                if  not row['dftype'] in data:
                    data[row['dftype']] = {}
                if  not row['dftype'] in dates:
                    dates[row['dftype']] = []
                if  not row['date'] in dates[row['dftype']]:
                    dates[row['dftype']].append(row['date'])
                for s in scorers:
                    if  not s in data[row['dftype']]:
                        data[row['dftype']][s] = {}
                    if  not row['clf'] in data[row['dftype']][s]:
                        data[row['dftype']][s][row['clf']] = []
                    data[row['dftype']][s][row['clf']].append(str_to_num(row[s]))
    # read classifiers running time
    if  timein:
        head = []
        for line in open(timein, 'r').readlines():
            if  not head:
                head = line
                continue
            line = line.strip(" \r\n").split(',')
            rundata[line[0]] = float(line[1])
    return data, dates, rundata

def main():
    optmgr  = OptionParser()
    opts, _ = optmgr.options()
    data, dates, rundata = read_data(opts.fin, opts.fbeg,
            opts.fend, opts.timein)
    plot(data, dates, opts.fout, rundata, opts.labels,
            opts.xeq, opts.leg, opts.colrb)

if __name__ == '__main__':
    main()
