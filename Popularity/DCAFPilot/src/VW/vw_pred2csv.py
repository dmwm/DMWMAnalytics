#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=
"""
File       : vw_pred2csv.py
Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
Description: Script to convert VW predictions into CSV format
"""

# system modules
import os
import sys
import optparse

class OptionParser():
    def __init__(self):
        "User based option parser"
        self.parser = optparse.OptionParser()
        self.parser.add_option("--fin", action="store", type="string",
            dest="fin", default="", help="Input file")
        self.parser.add_option("--fout", action="store", type="string",
            dest="fout", default="", help="Output file")
        self.parser.add_option("--headers", action="store", type="string",
            dest="headers", default="id,prediction", help="Headers for CSV file (comma separated), default id,prediction")
    def get_opt(self):
        "Return list of options"
        return self.parser.parse_args()

def convert(fin, fout, headers):
    "Function which convert VW input file into CSV output one"
    with open(fin, 'r') as istream, open(fout, 'w') as ostream:
        ostream.write(headers+'\n')
        for line in istream.readlines():
            row = line.replace('\n', '').split()
            ostream.write("%s,%s\n" % (row[-1], row[0]))

def main():
    "Main function"
    optmgr  = OptionParser()
    opts, _ = optmgr.get_opt()
    convert(opts.fin, opts.fout, opts.headers)

if __name__ == '__main__':
    main()
