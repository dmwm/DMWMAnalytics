#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=
"""
File       : vw_add_namespaces.py
Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
Description: add namespace into VW file
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
    def get_opt(self):
        "Return list of options"
        return self.parser.parse_args()

LET = re.compile('[a-zA-Z]')

def add_namespaces(fin, fout):
    "Add namespaces into VW input file"
    with open(fout, 'wb') as ostream:
        for _, line in enumerate(open(fin, 'r')):
            elements = line.split()
            attributes = []
            for item in line.split():
                if  item == "|f":
                    continue
                if  LET.match(item[0]):
                    name, val = item.split(':')
                    attr = '|%s %s:%s' % (name, name, val)
                else:
                    attr = item
                attributes.append(attr)
            ostream.write(' '.join(attributes)+'\n')

def main():
    "Main function"
    optmgr  = OptionParser()
    opts, _ = optmgr.get_opt()
    add_namespaces(opts.fin, opts.fout)

if __name__ == '__main__':
    main()
