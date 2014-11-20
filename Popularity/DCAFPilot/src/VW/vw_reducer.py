#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=
"""
File       : vw_reducer.py
Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
Description: This script will reduce content of input VW file with
             given list of dropped attributes
"""

# system modules
import os
import re
import sys
import optparse

class OptionParser:
    """Option parser"""
    def __init__(self):
        self.parser = optparse.OptionParser()
        self.parser.add_option("-d", "--drop", action="store", type="string",
                               default="", dest="drop",
             help="specify list of attributes to drop from VW file")
        self.parser.add_option("-f", "--file", action="store", type="string",
                               default="", dest="vwin",
             help="specify input VW file")
        self.parser.add_option("-o", "--out", action="store", type="string",
                               default="", dest="vwout",
             help="specify output VW file")
    def get_opt(self):
        """Returns parse list of options"""
        return self.parser.parse_args()

def attr_in_fields(attr, drops):
    "Check if given attribute exists in drop list"
    for drop in drops:
        if  drop.endswith('$') or drop.startswith('^'): # regular expression
            pat = re.compile(drop)
            if  pat.match(attr):
                return True
        elif  attr.find(drop) != -1:
            return True
    return False

def dropper(vwin, vwout, drops):
    "Read input VW file and drops given attributes"
    with open(vwin, 'r') as istream, open(vwout, 'wb') as ostream:
        while True:
            fields = istream.readline().replace('\n', '').split()
            if  not fields:
                break
            out = [o for o in fields if not attr_in_fields(o, drops)]
            ostream.write(' '.join(out)+'\n')

def main():
    "Main function"
    optmgr = OptionParser()
    opts, _ = optmgr.get_opt()
    drops = opts.drop.split(',')
    dropper(opts.vwin, opts.vwout, drops)

if __name__ == '__main__':
    main()
