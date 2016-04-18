#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=
"""
File        : verify_dfr.py
Author      : Mantas Briliauskas <m dot briliauskas AT gmail dot com>
Description : compares column summaries of two dataframes
"""
from __future__ import print_function

# system modules
import os
import re
import sys
import numpy as np
import pandas as pd
import warnings as wn
import StringIO
import optparse

# package modules
from DCAF.utils.utils import fopen

class OptionParser(object):
    def __init__(self):
        self.parser = optparse.OptionParser()
        self.parser.add_option("--file1", action="store", type="string",
            default=None, dest="file1", help="First dataframe file")
        self.parser.add_option("--file2", action="store", type="string",
            default=None, dest="file2", help="Second dataframe file")
        self.parser.add_option("--drops", action="store", type="string",
            default=None, dest="drops", help="Columns to drop before summarization")
    def options(self):
        return self.parser.parse_args()

def read_summary(fin, drops=None):
    "Reads summary for provided file"
    if  not fin:
        print("ERROR in read_summary: please provide fname")
        sys.exit(1)
    comp = None
    xdf  = None
    if  fin.endswith('.gz'):
        comp = 'gzip'
    elif fin.endswith('.bz2'):
        comp = 'bz2'
    stderr = sys.stderr
    sys.stderr = out = StringIO.StringIO()
    xdf = pd.read_csv(fin, compression=comp)
    sys.stderr = stderr
    out = out.getvalue()
    reg_spc = re.compile("^\s*$")
    reg_msg = re.compile("DtypeWarning: Columns [^ ]+ have mixed types")
    if  reg_spc.search(out) is None and reg_msg.search(out) is None:
        print("ERROR: unexpected message from pd.read_csv received: ", out)
        sys.exit(1)
    xdf[xdf.columns] = xdf[xdf.columns].convert_objects(convert_numeric=True)
    xdf[xdf.columns] = xdf[xdf.columns].astype('float32')
    xdf = xdf.fillna(-1)
    if  drops is not None and drops:
        drops = drops.replace('\n','').split(',')
        cols = xdf.columns
        for d in drops:
            if d in cols:
                xdf.drop(d, axis=1)
    desc = xdf.describe(include=['number'])
    return desc

def compare(summ1, summ2):
    "Compares two dfr summaries, returns nothing if success"
    failed = 0
    for col in summ1.columns:
        if  col in summ2.columns:
            for stat in summ1.index:
                if  float(summ1.loc[stat, col]) != float(summ2.loc[stat, col]):
                    print("> CSV summary verification failed. Loc[%s, %s]: %.2f vs %.2f"
                        % (stat, col, summ1.loc[stat, col],
                                 summ2.loc[stat, col]))
                    failed += 1
    if  failed == 0:
        failed = ""
    else:
        failed = ("ERROR: %d column statictics mismatch. Transformation procedure should be revised." % failed)
    return failed

def main():
    optmgr = OptionParser()
    opts, _ = optmgr.options()
    summ1 = read_summary(opts.file1, opts.drops)
    summ2 = read_summary(opts.file2, opts.drops)
    failed = compare(summ1, summ2)
    if  failed:
        print(failed)
        print("Verification failed with files: %s vs %s" % (opts.file1, opts.file2))

if __name__ == '__main__':
    main()
