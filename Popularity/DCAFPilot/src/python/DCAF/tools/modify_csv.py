#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=
"""
File        : modify_csv.py
Author      : Mantas Briliauskas <m dot briliauskas AT gmail dot com>
Description : represents dataframe modification procedures
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
from DCAF.tools.parse_csv import read_data

class OptionParser(object):
    def __init__(self):
        self.parser = optparse.OptionParser()
        self.parser.add_option("--fin", action="store", type="string",
            dest="fin", default=None, help="Input dataframe")
        self.parser.add_option("--fout", action="store", type="string",
            dest="fout", default=None, help="Output file, same is modified if None, default None")
        self.parser.add_option("--lineno", action="store", type="int",
            dest="lineno", default=None, help="Line number to modify, first line of data indexed by 0")
        self.parser.add_option("--col", action="store", type="string",
            dest="col", default=None, help="Target column name")
        self.parser.add_option("--newval", action="store", type="string",
            dest="newvalue", default=None, help="New value")
        self.parser.add_option("--verbose", action="store", type="int",
            dest="verbose", default=0, help="verbose mode, default 0")
    def options(self):
        return self.parser.parse_args()

def change_data(dfr, lineno, col, newvalue):
    dfr.loc[lineno, col] = newvalue
    return dfr

def write_data(dfr, fout, comp):
    csv = dfr.to_csv(index=False, sep=',')
    fopen(fout, 'w').write(csv)

def main():
    optmgr  = OptionParser()
    opts, _ = optmgr.options()
    dfr, comp = read_data(opts.fin, opts.verbose)
    dfr  = change_data(dfr, opts.lineno, opts.col, opts.newvalue)
    write_data(dfr, opts.fout, comp)

if __name__ == '__main__':
    main()
