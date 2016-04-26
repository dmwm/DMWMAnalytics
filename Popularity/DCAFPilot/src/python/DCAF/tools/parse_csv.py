#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=
"""
File        : parse_csv.py
Author      : Mantas Briliauskas <m dot briliauskas AT gmail dot com>
Description : represents dataframe parsing procedures
"""
from __future__ import print_function

# system modules
import os
import re
import sys
import pandas as pd
import optparse
import StringIO

# package modules
from DCAF.utils.utils import fopen

class OptionParser(object):
    def __init__(self):
        self.parser = optparse.OptionParser()
        self.parser.add_option("--fin", action="store", type="string",
            dest="fin", default=None, help="Input file, usually a dataframe *.csv.gz")
        self.parser.add_option("--fout", action="store", type="string",
            dest="fout", default=None, help="Output file")
        self.parser.add_option("--tiers", action="store", type="string",
            dest="tiers", default=None, help="List of tiers to parse, default None")
        self.parser.add_option("--tiers-col", action="store", type="string",
            dest="col", default=None, help="Target tier column name")
        self.parser.add_option("--mapping", action="store", type="string",
            dest="tiersmap", default=None, help="File with tier id and name mapping, default None")
        msg  = "Columns in  mapping file to denote tier id and name, default 'id,tier'"
        self.parser.add_option("--mapping-kval", action="store",
            type="string", dest="kval", default="id,tier", help=msg)
        self.parser.add_option("--verbose", action="store",
            type="int", dest="verbose", default=0, help="Verbose mode, default 0, values 0-2")
        msg  = "Convert data to numeric data before parsing. "
        msg += "Default value is False. "
        msg += "If option is active, non-numeric values are set to -1"
        self.parser.add_option("--convert-to-num", action="store_true",
            dest="ctn", help=msg)
    def options(self):
        return self.parser.parse_args()

def read_data(fname, verbose=False, convert_to_num=False):
    "Reads data to pandas dataframe, avoiding mixed types warning"
    if  fname is None or not fname:
        msg  = "ERROR in parse_csv. "
        msg += "Usage: parse_csv --fin=train.csv.gz --fout=train_.csv.gz "
        msg += "--tiers=AOD,AODSIM,MINIAOD --mapping=old_tiers.txt "
        msg += "--mapping-kval=id,tier"
        print(msg)
        sys.exit(1)
    # must check before stderr redirect
    if  not os.path.isfile(fname):
        print("ERROR: file %s provided as --fin does not exists" % fname)
        sys.exit(1)
    comp = None
    xdf  = None
    if  fname.endswith('.gz'):
        comp = 'gzip'
    elif fname.endswith('.bz2'):
        comp = 'bz2'
    # capturing warning
    origstd = sys.stderr
    out = StringIO.StringIO()
    sys.stderr = out
    xdf = pd.read_csv(fname, compression=comp)
    out = out.getvalue()
    if  out and verbose:
        print("Message received while reading %s: %s", (fname, out))
    sys.stderr = origstd
    reg_spc = re.compile("^\s*$")
    reg_msg = re.compile("DtypeWarning: Columns [^ ]+ have mixed types")
    if  reg_spc.search(out) is None and reg_msg.search(out) is None:
        print("ERROR: unexpected message received while reading %s: %s" % (fname, out))
        sys.exit(1)
    if  convert_to_num:
        xdf[xdf.columns] = xdf[xdf.columns].convert_objects(convert_numeric=True)
        xdf = xdf.fillna(-1)
    return xdf, comp

def parse_data(dfr, query, col, values, mapping, kval, verbose, convert_to_num):
    "Selecting parsing procedure"
    supported = {'tiers':'__parse_tiers'}
    values = values.split(',')
    if  query in supported.keys():
        fnc = getattr(sys.modules[__name__], supported[query])
        return fnc(dfr, col, values, mapping, kval, verbose, convert_to_num)
    else:
        print("ERROR parse_csv; query %s is not supported")
        sys.exit(1)

def __parse_tiers(dfr, col, values, mapping, kval, verbose, convert_to_num):
    "Parsing selected tiers, id-name mapping applied if preferred"
    if  verbose:
        print("Selected values: ", values)
    if  mapping is not None:
        kvals = kval.split(',')
        if  len(kvals) != 2:
            msg = "ERROR: please provide --mapping-kval in format key_column,value_column starting from 0"
            print(msg)
            sys.exit(1)
        mkeycol = kvals[0]
        mvalcol = kvals[1]
        maps, _ = read_data(mapping, verbose, convert_to_num)
        if  mvalcol in maps.columns:
            extr    = maps[mvalcol].isin(values)
        else:
            print("ERROR: %s column in not in mapping file %s"
                    % (mvalcol, mapping))
            sys.exit(1)
        if  values == "*":
            values = list(set(maps.loc[:, mkeycol].tolist()))
        else:
            values = maps.loc[maps[mvalcol].isin(values), mkeycol].tolist()
        if  verbose:
            print("Values after mapping: ", values)
        if  verbose > 1:
            print("Mapping key column   : ", mkeycol)
            print("Mapping value column : ", mvalcol)
            print("Extracted mapping    :\n", maps[extr])
    #print(dfr['id'].mean())
    if  verbose:
        print("Original dataframe size : [%d,%d]" % (dfr.shape[0], dfr.shape[1]))
    dfr = dfr[dfr[col].isin(values)]
    #print(dfr['id'].mean())
    #exit()
    if  verbose:
        print("Parsed data size        : [%d,%d]" % (dfr.shape[0], dfr.shape[1]))
    return dfr

def write_data(dfr, fout, comp):
    csv = dfr.to_csv(index=False, sep=',')
    fopen(fout, 'w').write(csv)

def main():
    optmgr    = OptionParser()
    opts, _   = optmgr.options()
    dfr, comp = read_data(opts.fin, verbose=opts.verbose, convert_to_num=opts.ctn)
    dfr       = parse_data(dfr, 'tiers', opts.col, opts.tiers, opts.tiersmap,
                opts.kval, opts.verbose, convert_to_num=opts.ctn)
    write_data(dfr, opts.fout, comp)

if __name__ == '__main__':
    main()
