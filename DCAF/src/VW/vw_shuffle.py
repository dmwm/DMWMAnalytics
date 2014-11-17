#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=
"""
File       : vw_permutate.py
Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
Description: This script will permutate lines in input VW file
             and write them into provided output file name.
             This may be desired since VW alg. is online based
             and order of VW input does matter.
"""

# system modules
import os
import sys
import random
import optparse

class OptionParser:
    """Option parser"""
    def __init__(self):
        self.parser = optparse.OptionParser()
        self.parser.add_option("-f", "--file", action="store", type="string",
                               default="", dest="vwin",
             help="specify input VW file")
        self.parser.add_option("-o", "--out", action="store", type="string",
                               default="", dest="vwout",
             help="specify output VW file")
        self.parser.add_option("-s", "--seed", action="store", type="int",
                               default=0, dest="seed",
             help="specify random generator seed")
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

def shuffle(vwin, vwout, seed=0):
    "Read input VW file and write out VW with shuffled lines"
    if  seed:
        random.seed(seed)
    offsets = line_offsets(vwin)
    nlines = len(offsets)
    indices = range(nlines)
    random.shuffle(indices)
    with open(vwin, 'r') as istream, open(vwout, 'wb') as ostream:
        for idx in indices:
            istream.seek(offsets[idx])
            line = istream.readline()
            ostream.write(line)

def main():
    "Main function"
    optmgr = OptionParser()
    opts, _ = optmgr.get_opt()
    shuffle(opts.vwin, opts.vwout, opts.seed)

if __name__ == '__main__':
    main()
