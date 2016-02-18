#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=
"""
File       : find_drops.py
Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
Description: 
"""
from __future__ import print_function

# system modules
import os
import re
import sys
import gzip
import optparse

# package modules
from DCAF.utils.utils import fopen

class OptionParser():
    def __init__(self):
        "User based option parser"
        usage  = "Usage: %prog [options]\n"
        usage += 'Description: find common headers between files and print attributes to drop\n'
        usage += 'Example: find_drops --file1=file1.csv.gz --file2=file2.csv.gz'
        self.parser = optparse.OptionParser(usage=usage)
        self.parser.add_option("--file1", action="store", type="string",
            dest="file1", default="", help="Input file1")
        self.parser.add_option("--file2", action="store", type="string",
            dest="file2", default="", help="Input file2")
        self.parser.add_option("--drops", action="store", type="string",
            dest="drops", default="", help="Input drops")
    def get_opt(self):
        "Return list of options"
        return self.parser.parse_args()

def find_drops(file1, file2, idrops=None):
    "Find difference in headers of two files and print it out"
    with fopen(file1) as istream1, fopen(file2) as istream2:
        headers1 = istream1.readline().replace('\n', '').split(',')
        headers2 = istream2.readline().replace('\n', '').split(',')
        if  len(headers1) > len(headers2):
            drops = set(headers1)-set(headers2)
        else:
            drops = set(headers2)-set(headers1)
        if  idrops:
            print(','.join(set(list(drops)+idrops.split(','))))
        else:
            print(','.join(drops))

def main():
    "Main function"
    optmgr  = OptionParser()
    opts, _ = optmgr.get_opt()
    find_drops(opts.file1, opts.file2, opts.drops)

if __name__ == '__main__':
    main()
