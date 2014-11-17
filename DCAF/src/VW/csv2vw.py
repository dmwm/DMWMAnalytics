#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=
"""
File       : csv2vw.py
Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
Description: Convert CSV file into VW data format
             we assume that CSV file should have id/target attributes
"""

# system modules
import os
import sys
from   optparse import OptionParser

class OptionManager:
    """Option parser manager"""
    def __init__(self):
        usage  = "Usage: %prog [options]\n"
        self.parser = OptionParser(usage=usage)
        self.parser.add_option("--csv", action="store", type="string",
            default='', dest="csv", help="CSV file name")
        self.parser.add_option("--vw", action="store", type="string",
            default='', dest="vw", help="vw file name")
        self.parser.add_option("--sep", action="store", type="string",
            default=',', dest="sep", help="CSV separator, default ,")
        self.parser.add_option("--rid", action="store", type="string",
            default='id', dest="rid", help="row id name in CSV")
        self.parser.add_option("--target", action="store", type="string",
            default='target', dest="target", help="target(label) name in CSV, default target. If not provided (in a test set) we'll use 1 for label assignment")
        self.parser.add_option("--drops", action="store", type="string",
            default='', dest="drops", help="comma separated list of drop attributes, e.g. a,b")

    def get_opt(self):
        """Returns parse list of options"""
        return self.parser.parse_args()

def csv2vw(fname, oname, sep=',', rid='id', target='target', drops=''):
    """Read and parse CSV input and write VW rows"""
    drops = drops.split(',')
    headers = []
    idx = 0
    with open(fname, 'r') as istream, open(oname, 'w') as ostream:
        for line in istream.readlines():
            line = line.replace('\n', '')
            if  not headers:
                headers = line.split(sep)
                continue
            fdict = dict(zip(headers, line.split(sep)))
            tval = fdict.get(target, 1)
            rval = fdict.get(rid, idx)
            for kkk in drops + [target, rid]:
                if  kkk in fdict:
                    del fdict[kkk]
            out  = "%s '%s |f" % (tval, rval)
            out += ''.join([' %s:%s'%(k,v) for k,v in fdict.items()])
            ostream.write(out + '\n')
            idx += 1

def main():
    "Main function"
    optmgr  = OptionManager()
    opts, _ = optmgr.get_opt()
    csvname = opts.csv
    if not csvname:
        print "No input CSV file is provided"
        sys.exit(1)
    vwname  = opts.vw if opts.vw else '%s.vw' % csvname.split('.csv')[0]
    csv2vw(csvname, vwname, opts.sep, opts.rid, opts.target, opts.drops)

if __name__ == '__main__':
    main()
