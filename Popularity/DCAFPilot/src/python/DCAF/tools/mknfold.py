#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=
"""
File       : mknfold.py
Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
Description: Helper script to split input file into train/test
by using match/nfold values. Loop over input file and store
lines with match==random.randint(1,nfold) into test file. The
rest goes into train file.
"""

# system modules
import os
import sys
import random
import optparse

# local modules
from DCAF.utils.utils import fopen

class OptionParser():
    def __init__(self):
        "User based option parser"
        usage  = 'Usage: %prog [options]\n'
        usage += 'Description: split fiven file into train/test ones\n'
        usage += 'Example: %prog --fin=file.csv'
        self.parser = optparse.OptionParser(usage=usage)
        self.parser.add_option("--fin", action="store", type="string",
            dest="fin", default="", help="Input file")
        self.parser.add_option("--match", action="store", type="int",
            dest="match", default=1, help="value to match nfold, default 1")
        self.parser.add_option("--nfold", action="store", type="int",
            dest="nfold", default=5, help="nfold value, default 5")
        self.parser.add_option("--verbose", action="store_true",
            dest="debug", default=False, help="Turn on verbose output")
    def get_opt(self):
        "Return list of options"
        return self.parser.parse_args()

def mknfold(fin, match=1, nfold=5):
    "Split input file into few"
    random.seed(123)
    with fopen(fin, 'r') as istream:
        with fopen(fin+'.train', 'w') as otrain:
            with fopen(fin+'.test', 'w') as otest:
                for line in istream:
                    if  random.randint( 1 , nfold ) == match:
                        otest.write(line)
                    else:
                        otrain.write(line)

def main():
    "Main function"
    optmgr  = OptionParser()
    opts, _ = optmgr.get_opt()
    mknfold(opts.fin, opts.match, opts.nfold)

if __name__ == '__main__':
    main()
