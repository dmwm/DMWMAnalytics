#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=
"""
File       : vw_split.py
Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
Description: This script will split VW file into train/validation ones.
"""
from __future__ import print_function

# system modules
import os
import sys
import random
import optparse

class OptionParser:
    """Option parser"""
    def __init__(self):
        self.parser = optparse.OptionParser()
        self.parser.add_option("--in", action="store", type="string",
                               default="", dest="fin",
             help="specify input VW file name")
        self.parser.add_option("--out", action="store", type="string",
                               default="", dest="fout",
             help="specify output VW file name")
        self.parser.add_option("--split", action="store", type="string",
                               default="30", dest="split",
             help="Specify split level in percentage, e.g. 30 means 30%, or provide file with ids")
        self.parser.add_option("--seed", action="store", type="int",
                               default=0, dest="seed",
             help="Specify seed for random module")
    def get_opt(self):
        """Returns parse list of options"""
        return self.parser.parse_args()

def line_offsets(fname):
    """Read in the file once and return a list of line offsets"""
    line_offset = []
    offset = 0
    for _, line in enumerate( open(fname) ):
        line_offset.append(offset)
        offset += len(line)
    return line_offset

def run(fin, fout, split, seed=0):
    "Read input file and write train/validation files"
    if  seed:
        random.seed(seed)
    base, ext = fout.split('.')
    ftest = '%s_valid.%s' % (base, ext)
    ltest = '%s_valid.labels' % base
    offsets = line_offsets(fin)
    nlines = len(offsets)
    indices = range(1, nlines)
    ids = None
    if  os.path.exists(split):
        ids = dict([(r.replace('\n',''), r) for r in open(split, 'r').readlines()])
    else:
        split = int(split)
        random.shuffle(indices)
    with open(fin, 'r') as istream, open(fout, 'wb') as ostream, \
        open(ftest, 'wb') as tstream, open(ltest, 'wb') as lstream:
        count = 0
        for idx in indices:
            istream.seek(offsets[idx])
            line = istream.readline()
            if  ids:
                elements = line.split()
                uid = elements[1].replace("'", '')
                label = line.split('|')[0].replace("'", '')
                if  uid in ids: # train sample
                    ostream.write(line)
                else:
                    lstream.write(label+'\n')
                    tstream.write(line)
            else:
                if  count > (nlines-round(nlines*split/100.)):
                    label = line.split('|')[0].replace("'", '')
                    line = '1' + line[1:] # always assign 1 to validation file, but keep labels
                    lstream.write(label+'\n')
                    tstream.write(line)
                else:
                    ostream.write(line)
            count += 1

def main():
    "Main function"
    optmgr = OptionParser()
    opts, _ = optmgr.get_opt()
    if  not opts.fin or not opts.fout:
        print("Usage: %s --help" % __file__)
        sys.exit(1)
    run(opts.fin, opts.fout, opts.split, opts.seed)

if __name__ == '__main__':
    main()
