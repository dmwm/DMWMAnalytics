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
            dest="fin", default="", help="Input prediction file")
        self.parser.add_option("--fvw", action="store", type="string",
            dest="fvw", default="", help="Input VW file")
        self.parser.add_option("--fout", action="store", type="string",
            dest="fout", default="", help="Output file")
        self.parser.add_option("--headers", action="store", type="string",
            dest="headers", default="dataset,dbs,prediction", help="Headers for CSV file (comma separated), default dataset,dbs,prediction")
    def get_opt(self):
        "Return list of options"
        return self.parser.parse_args()

def get_dbs(vwrow):
    "Extract dbs id from given VW row"
    for item in vwrow.split():
        if  item.startswith('dbs'):
            return item.split(':')[-1]
    return 0
def convert(fin, fvw, fout, headers):
    "Function which convert VW input file into CSV output one"
    with open(fin, 'r') as istream, open(fvw, 'r') as wstream, open(fout, 'w') as ostream:
        ostream.write(headers+'\n')
        while True:
            try:
                vwrow = wstream.readline()
                if  not vwrow:
                    break
                row = istream.readline().replace('\n', '').split()
                ostream.write("%s,%s,%s\n" % (row[-1], get_dbs(vwrow), row[0]))
            except:
                break

def main():
    "Main function"
    optmgr  = OptionParser()
    opts, _ = optmgr.get_opt()
    convert(opts.fin, opts.fvw, opts.fout, opts.headers)

if __name__ == '__main__':
    main()
