#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=
"""
File       : vw_sort.py
Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
Description: This script will sort train.vw input with respect
             to the following order in train_history.csv:
             offerdate, market, chain
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
        self.parser.add_option("-i", "--in", action="store", type="string",
                               default="", dest="vwin",
             help="specify input VW file")
        self.parser.add_option("-o", "--out", action="store", type="string",
                               default="", dest="vwout",
             help="specify output VW file")
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

def run(vwin, vwout):
    "Read input VW file and write out VW with sorted lines"
    indices = []
    for idx, line in enumerate(open('data/train_history_sorted.csv', 'r')):
        if  idx > 0:
            row = line.split(',')
            indices.append(int(row[0])-1) # account for python index scheme
    offsets = line_offsets(vwin)
    with open(vwin, 'r') as istream, open(vwout, 'wb') as ostream:
        for idx in indices:
            istream.seek(offsets[idx])
            line = istream.readline()
            ostream.write(line)

def main():
    "Main function"
    optmgr = OptionParser()
    opts, _ = optmgr.get_opt()
    run(opts.vwin, opts.vwout)

if __name__ == '__main__':
    main()
