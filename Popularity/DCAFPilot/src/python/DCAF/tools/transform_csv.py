#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=
"""
File       : transform_csv.py
Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
Description: Perform transformation with given CSV file. The allowed transformation are
drop multiple columns, convert dataframe into classification problem, rename given target
column.
"""

# system modules
import os
import sys
import gzip
import bz2
import optparse

class OptionParser():
    def __init__(self):
        "User based option parser"
        self.parser = optparse.OptionParser()
        self.parser.add_option("--fin", action="store", type="string",
            dest="fin", default="", help="Input file")
        self.parser.add_option("--fout", action="store", type="string",
            dest="fout", default="", help="Output file")
        self.parser.add_option("--target", action="store", type="string",
            dest="target", default="", help="Target column name")
        self.parser.add_option("--target-thr", action="store", type="float",
            dest="thr", default=0, help="Target threshold, default 0 (use -1 to keep the value intact)")
        self.parser.add_option("--drops", action="store", type="string",
            dest="drops", default="", help="drops column names (comma separated)")
        self.parser.add_option("--verbose", action="store_true",
            dest="verbose", default=0, help="Turn on verbose output")
    def get_opt(self):
        "Return list of options"
        return self.parser.parse_args()

def transform(fin, fout, target, thr, drops, verbose=0):
    "Perform transformation on given CSV file"
    if  fin.endswith('.gz'):
        istream = gzip.open(fin, 'rb')
    elif  fin.endswith('.bz2'):
        istream = bz2.BZ2File(fname, 'r')
    else:
        istream = open(fin, 'r')
    if  fout.endswith('.gz'):
        ostream = gzip.open(fout, 'wb')
    elif  fout.endswith('.bz2'):
        ostream = bz2.BZ2File(fname, 'r')
    else:
        ostream = open(fout, 'w')
    headers = False
    for line in istream.readlines():
        if  not headers:
            headers = line.replace('\n', '').split(',')
            if  drops:
                new_headers = []
                for idx, val in enumerate(headers):
                    if  val in drops or val == target:
                        continue
                    new_headers.append(val)
                ostream.write(','.join(new_headers)+',target\n')
            continue
        vals = line.replace('\n', '').split(',')
        rdict = dict(zip(headers, vals))
        if  thr==-1: # keep regression
            tval = rdict[target]
        else: # do classification
            tval = 1 if float(rdict[target])>=float(thr) else 0
        new_vals = []
        for key in new_headers:
            if  key in drops or key == target:
                continue
            new_vals.append(str(rdict[key]))
        new_vals.append(str(tval))
        ostream.write(','.join(new_vals)+'\n')
    istream.close()
    ostream.close()

def main():
    "Main function"
    optmgr  = OptionParser()
    opts, _ = optmgr.get_opt()
    drops = opts.drops.split(',')
    transform(opts.fin, opts.fout, opts.target, opts.thr, drops, opts.verbose)

if __name__ == '__main__':
    main()
