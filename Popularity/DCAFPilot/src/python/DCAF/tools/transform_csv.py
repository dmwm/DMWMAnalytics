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
from math import log
import pandas as pd
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
        usage += '         transform_csv --fin=2014.csv.gz --fout=train.csv.gz --target-thr=\'row["naccess"]>0 and row["nusers"]>5\' --drops=naccess,nusers,totcpu,rnaccess,rnusers,rtotcpu,nsites,s_0,s_1,s_2,s_3,s_4,wct'
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
        self.parser.add_option("--log-cols", action="store", type="string",
            dest="logcols", default="", help="columns to apply log transformation, comma separated")
        self.parser.add_option("--log-all", action="store_true",
            dest="logall", default="", help="option to apply log transformation to all columns except 'id' and 'target'")
        msg  = "threshold to determine columns to pick for log transform, "
        msg += "mean of top ten rows is selected for comparison, default value is None"
        self.parser.add_option("--log-thr", action="store", type="float",
            dest="logthr", default=None, help=msg)
        msg  = "amount to increase selected column values before log transformation, "
        msg += "actual since <nil> values are replaced with -1 during transformation. "
        msg += "default value is 2"
        self.parser.add_option("--log-bias", action="store", type="int",
            dest="logbias", default=2, help=msg)
        self.parser.add_option("--log-ignore", action="store", type="string",
            dest="logignore", default="id,target,tier,dataset",
            help="Columns to ignore for log transform, default='id,target,tier,dataset'")
    def get_opt(self):
        "Return list of options"
        return self.parser.parse_args()

def get_log_cols(fin, logthr, logignore, nrows=10):
    comp = None
    if  fin.endswith(".gz"):
        comp = "gzip"
    elif fin.endswith(".bz2"):
        comp = "bz2"
    dfr = pd.read_csv(fin, compression=comp, nrows=nrows)
    dfr[dfr.columns] = dfr[dfr.columns].convert_objects(convert_numeric=True)
    dfr = dfr.mean(axis=0, skipna=True)
    logcols = dfr[dfr >= logthr].index.tolist()
    if  logignore:
        logcols = list(set(logcols)-set(logignore))
    return logcols

def transform(fin, fout, target, thr, drops, verbose=0, logcols='', logall=False, logbias=2, logthr=None, logignore=''):
    "Perform transformation on given CSV file"
    istream = fopen(fin, 'r')
    ostream = fopen(fout, 'wb')
    headers = False
    eno     = 0
    logignore = logignore.split(',')
    if  logthr and not logcols:
        logcols = get_log_cols(fin, logthr, logignore)
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
        try:
            item = line.replace('\n', '').replace('<nil>', '-1')
            vals = [eval(v) for v in item.split(',')]
        except Exception as exp:
            print("Unable to parse the line", line, type(line), exp)
            vals = []
            for item in line.split(','):
                try:
                    vals.append(eval(item))
                except:
                    vals.append(-1)
            if  len(vals) != len(headers):
                raise Exception("Unable to parse line '%s', #values != #headers", line)
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
        if  logcols or logall:
            if  logall:
                logcols = new_headers[:]
                logcols = list(set(logcols)-set(logignore))
            for i in xrange(len(new_headers)):
                if  new_headers[i] in logcols:
                    new_vals[i] = str(log(eval(new_vals[i])+logbias))
        ostream.write(','.join(new_vals)+'\n')
    istream.close()
    ostream.close()

def main():
    "Main function"
    optmgr  = OptionParser()
    opts, _ = optmgr.get_opt()
    drops = opts.drops.split(',')
    transform(opts.fin, opts.fout, opts.target, opts.thr, drops,
        opts.verbose, opts.logcols, opts.logall, opts.logbias,
        opts.logthr, opts.logignore)

if __name__ == '__main__':
    main()
