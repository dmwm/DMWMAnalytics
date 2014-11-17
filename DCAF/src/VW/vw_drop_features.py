#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=
"""
File       : vw_drop_features.py
Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
Description: 
"""

# system modules
import os
import re
import sys
import optparse

class OptionParser():
    def __init__(self):
        "User based option parser"
        self.parser = optparse.OptionParser()
        self.parser.add_option("--fin", action="store", type="string",
            dest="fin", default="", help="Input file")
        self.parser.add_option("--fout", action="store", type="string",
            dest="fout", default="", help="Input file")
        self.parser.add_option("--drops", action="store", type="string",
            dest="drops", default="", help="Input file")
    def get_opt(self):
        "Return list of options"
        return self.parser.parse_args()

LET = re.compile('[a-zA-Z]')

def drop_features(fin, fout, drops):
    "Add namespaces into VW input file"
    with open(fout, 'wb') as ostream:
        for _, line in enumerate(open(fin, 'r')):
            elements = line.split()
            attributes = []
            for item in line.split():
                name = item.split(':')[0]
                if  name not in drops:
                    attributes.append(item)
            ostream.write(' '.join(attributes)+'\n')

def main():
    "Main function"
    optmgr  = OptionParser()
    opts, _ = optmgr.get_opt()
    drops = [d for d in opts.drops.split(',')]
    drop_features(opts.fin, opts.fout, drops)

if __name__ == '__main__':
    main()
