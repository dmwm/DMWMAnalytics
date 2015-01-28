#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=

"""
File       : csv_split.py
Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
Description: This script split given CSV file into two which
can be used for training and validation.
"""

# system modules
import os
import sys
import random
import optparse

# local modules
from DCAF.utils.utils import fopen

class OptionParser:
    """Option parser"""
    def __init__(self):
        self.parser = optparse.OptionParser()
        self.parser.add_option("--in", action="store", type="string", \
            default="", dest="fin", help="specify input CSV file name")
        self.parser.add_option("--out", action="store", type="string", \
             default="", dest="fout", help="specify output CSV file name")
        self.parser.add_option("--split", action="store", type="int", \
             default=30, dest="split", \
             help="Specify split level in percentage, e.g. 30 means 30%")
        self.parser.add_option("--seed", action="store", type="int", \
             default=0, dest="seed", help="Specify seed for random module")
    def get_opt(self):
        """Returns parse list of options"""
        return self.parser.parse_args()

def line_offsets(fname):
    """Read in the file once and return a list of line offsets"""
    line_offset = []
    offset = 0
    for _, line in enumerate( fopen(fname) ):
        line_offset.append(offset)
        offset += len(line)
    return line_offset

def run(fin, fout, split=30, seed=0):
    "Read input file and write train/validation files"
    if  seed:
        random.seed(seed)
    base, ext = fout.split('.')
    ftest = '%s_valid.%s' % (base, ext)
    offsets = line_offsets(fin)
    nlines = len(offsets)
    indices = range(1, nlines)
    random.shuffle(indices)
    with fopen(fin, 'r') as istream, fopen(fout, 'wb') as ostream, \
        fopen(ftest, 'wb') as tstream:
        headers = istream.readline()
        ostream.write(headers)
        tstream.write(headers)
        count = 0
        for idx in indices:
            istream.seek(offsets[idx])
            line = istream.readline()
            if  count > (nlines-round(nlines*split/100.)):
                tstream.write(line)
            else:
                ostream.write(line)
            count += 1

def main():
    "Main function"
    optmgr = OptionParser()
    opts, _ = optmgr.get_opt()
    if  not opts.fin or not opts.fout:
        print "Usage: %s --help" % __file__
        sys.exit(1)
    run(opts.fin, opts.fout, opts.split, opts.seed)

if __name__ == '__main__':
    main()
