#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=
"""
File        : ensemble_predictions.py
Author      : Mantas Briliauskas <m dot briliauskas AT gmail dot com>
Description : prepresents package used to ensemble separate predictions
"""
from __future__ import print_function

# system modules
import os
import sys
import glob
import numpy as np
import pandas as pd
import optparse

# package modules
from DCAF.utils.utils import fopen

class OptionParser(object):
    def __init__(self):
        self.parser = optparse.OptionParser()
        self.parser.add_option("--fin", action="store", type="string",
            dest="fin", default=".", help="Comma separated files or directory, default '.' is current dir")
        self.parser.add_option("--fbeg", action="store", type="string",
            dest="fbeg", default=None, help="Select files only with specific beginning, default=''")
        self.parser.add_option("--fend", action="store", type="string",
            dest="fend", default=".txt", help="Select files only with specific ending, default='.txt'")
        self.parser.add_option("--fout", action="store", type="string",
            dest="fout", default='${fbeg}Ensemble.txt', help="File name to output ensemble result, use ${fbeg} or ${fend} to replace them by --fbeg or --fend respectfully, default='${fbeg}ensemble.txt'")
        self.parser.add_option("--threshold", action="store", type="float",
            dest="threshold", default=0.5, help="Threshold to separate positive and negative predictions, default 0.5")
    def options(self):
        return self.parser.parse_args()

def get_file_list(fin, fbeg, fend):
    "Extracts files using given parameters"
    def find_files(idir, fbeg, fend):
        files = [f for f in os.listdir(idir) \
            if (not fbeg or f.startswith(fbeg)) and (not fend or f.endswith(fend))]
        if  idir != ".":
            files = [os.path.join(idir, f) for f in files]
        return files
    filelist = []
    if  fin == '.':           # current dir
        filelist = find_files(fin, fbeg, fend)
    elif fin.find(',') != -1: # list of files
        filelist = fin.split(',')
    elif fin.find('*') != -1: # pattern
        filelist = glob.glob(fin)
    elif os.path.isdir(fin):  # we got directory name
        filelist = find_files(fin, fbeg, fend)
    if  len(filelist) < 2:
        print("ERROR in ensembling: please provide directory or file list to process. Less than 2 files found. Received:\n%s" % fin)
        sys.exit(1)
    return filelist

def ensemble_manual(fin, fbeg, fend, fout, threshold):
    "Ensembles predictions or probabilities of prediction files"
    filelist = get_file_list(fin, fbeg, fend)
    fout = fout.replace("${fbeg}", fbeg).replace("${fend}", fend)
    if  fout in filelist:
        filelist.remove(fout)
    istreams = [open(f, 'r') for f in filelist]
    ostream  = open(fout, 'w')
    headers  = []
    n        = 0
    while True:
        lines = [i.readline().strip(" \n\r").split(',') for i in istreams]
        if  not any([line[0] for line in lines]):
            break
        if  not headers:
            headers = lines[0]
            for h in lines[1:]:
                if  headers != h:
                    print("ERROR in ensemble_predictions. Headers mismatch:")
                    print("%s and %s" % (str(headers), str(h)))
                    print("Passed files: ", filelist)
                    sys.exit(1)
            ostream.write(",".join(headers) + "\n")
            continue
        n += 1
        if  not all([(lines[0][0] == l[0] and lines[0][1] == l[1]) \
                for l in lines[1:]]):
            msg  = "Error in ensemble_predictions: inconsistent data: first two columns in prediction files must be equal "
            msg += "in all given files. Mismatch: "
            print(msg, lines)
            sys.exit(1)
        xm  = np.mean([float(line[2]) for line in lines])
        val = 1 if xm >= threshold else 0
        ostream.write(",".join([lines[0][0],lines[0][1],str(val)]) + "\n")
    for i in istreams:
        i.close()
    ostream.close()

def main():
    optmgr  = OptionParser()
    opts, _ = optmgr.options()
    ensemble_manual(opts.fin, opts.fbeg, opts.fend, opts.fout, opts.threshold)

if __name__ == '__main__':
    main()
