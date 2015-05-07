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
from __future__ import print_function

# system modules
import os
import re
import sys
import gzip
import bz2
import optparse

# local modules
from DCAF.utils.regex import INT_PAT, FLOAT_PAT
from DCAF.utils.utils import fopen

class OptionParser():
    def __init__(self):
        "User based option parser"
        usage  = 'Usage: %prog [options]\n'
        usage += 'Description: transform dataframe from given CSV file, e.g. create classification dataset\n'
        usage += 'Example: transform_csv --fin=2014.csv.gz --fout=train.csv.gz --target=naccess --target-thr=100 --drops=nusers,totcpu,rnaccess,rnusers,rtotcpu,nsites,s_0,s_1,s_2,s_3,s_4,wct\n'
        usage += '         transform_csv --fin=2014.csv.gz --fout=train.csv.gz --target=naccess --target-thr=\'row["naccess"]>0 and row["nusers"]>5 --drops=totcpu,nsites\''
        self.parser = optparse.OptionParser(usage=usage)
        self.parser.add_option("--fin", action="store", type="string",
            dest="fin", default="", help="Input file")
        self.parser.add_option("--fout", action="store", type="string",
            dest="fout", default="", help="Output file")
        self.parser.add_option("--target", action="store", type="string",
            dest="target", default="", help="Target column name")
        msg  = 'Target threshold, default 0 (use -1 to keep the value intact) or '
        msg += 'supply valid python expression using the _row_ as a dict of parameters, e.g. '
        msg += 'row["naccess"]>10 and row["nusers"]>5'
        self.parser.add_option("--target-thr", action="store", type="string",
            dest="thr", default="0", help=msg)
        self.parser.add_option("--drops", action="store", type="string",
            dest="drops", default="", help="drops column names (comma separated)")
        self.parser.add_option("--verbose", action="store_true",
            dest="verbose", default=0, help="Turn on verbose output")
    def get_opt(self):
        "Return list of options"
        return self.parser.parse_args()

def transform(fin, fout, target, thr, drops, verbose=0):
    "Perform transformation on given CSV file"
    istream = fopen(fin, 'r')
    ostream = fopen(fout, 'wb')
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
        vals = [eval(v) for v in line.replace('\n', '').split(',')]
        row = dict(zip(headers, vals))
        if  thr==-1: # keep regression
            tval = row[target]
        else: # do classification
            if  INT_PAT.match(thr) or FLOAT_PAT.match(thr):
                tval = 1 if float(row[target])>float(thr) else 0
            else:
                try:
                    cond = eval(thr)
                    if  cond:
                        tval = 1
                    else:
                        tval = 0
                except:
                    print("Please supply valid python condition, e.g. row['naccess']>10 and row['nusers']>5")
                    sys.exit(1)
        new_vals = []
        for key in new_headers:
            if  key in drops or key == target:
                continue
            new_vals.append(str(row[key]))
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
