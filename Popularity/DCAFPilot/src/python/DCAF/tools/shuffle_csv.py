#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=
"""
File        : shuffle_csv.py
Author      : Mantas Briliauskas <m dot briliauskas AT gmail dot com>
Description : shuffles data in dataframe
"""

from __future__ import print_function

# system modules
import os
import sys
import numpy as np
import pandas as pd
import optparse
from subprocess import check_call

# package modules
from DCAF.utils.utils import fopen

class OptionParser(object):
    def __init__(self):
        self.parser = optparse.OptionParser()
        self.parser.add_option("--fin", action="store", type="string",
            dest="fin", default=None, help="Input file")
        self.parser.add_option("--fout", action="store", type="string",
            dest="fout", default=None, help="Output file (optional), default=None")
    def options(self):
        return self.parser.parse_args()

def shuffle(dfr):
    "Shuffles the data at random"
    dfr.reindex(np.random.permutation(dfr.index), axis=0)
    return dfr

def save_data(dfr, fout):
    "Writes dfr to file"
    fstem = '.'.join(fout.split('.')[0:-1])
    dfr.to_csv(fstem, index=False)
    if  fout.endswith('.gz'):
        check_call(['gzip', '-f', fstem])
    elif fin.endswith('.bz2'):
        check_call(['bzip2', '-f', fstem])
    elif not fin.endswith('.csv'):
        print("Error in shuffle_csv: compression %s not supported" % comp)

def read_data(fin):
    "Reads data to dfr"
    if  not os.path.isfile(fin):
        print("ERROR: input file %s does not exist" % fin)
        sys.exit(1)
    dfr  = None
    comp = None
    if  fin.endswith('.gz'):
        comp = 'gzip'
    elif fin.endswith('.bz2'):
        comp = 'bz2'
    dfr = pd.read_csv(fin, compression=comp)
    return dfr

def main():
    optmgr  = OptionParser()
    opts, _ = optmgr.options()
    dfr     = read_data(opts.fin)
    dfr     = shuffle(dfr)
    if  opts.fout:
        save_data(dfr, opts.fout)
    else:
        save_data(dfr, opts.fin)

if __name__ == '__main__':
    main()
