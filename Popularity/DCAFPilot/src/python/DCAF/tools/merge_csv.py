#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=
"""
File       : merge_csv.py
Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
Description: 
"""

# system modules
import os
import sys
import glob
import optparse

# local modules
from DCAF.utils.utils import fopen

class OptionParser():
    def __init__(self):
        "User based option parser"
        usage  = "Usage: %prog [options]\n"
        usage += 'Description: merge input files into single one. User may either provide directory or pattern of files\n'
        usage += 'Example: merge_csv --fin=my_data_dir --fout=file.csv.gz --verbose'
        self.parser = optparse.OptionParser(usage=usage)
        self.parser.add_option("--fin", action="store", type="string",
            dest="fin", default="", help="Input files or input directory")
        self.parser.add_option("--fout", action="store", type="string",
            dest="fout", default="", help="Output file")
        self.parser.add_option("--verbose", action="store_true",
            dest="verbose", default=False, help="Turn on verbose output")
    def get_opt(self):
        "Return list of options"
        return self.parser.parse_args()

def files(idir, ext=".csv.gz"):
    "Return list of files from given directory"
    for fname in os.listdir(idir):
        if  fname.endswith(ext):
            yield '%s/%s' % (idir, fname)

def merger(fin, fout, verbose=False):
    "Merger function"
    filelist = []
    if  fin.find(',') != -1: # list of files
        filelist = fin.split(',')
    elif fin.find('*') != -1: # pattern
        filelist = glob.glob(fin)
    elif os.path.isdir(fin): # we got directory name
        for ext in ['.csv.gz', '.csv', 'csv.bz2']:
            filelist = [f for f in files(fin, ext)]
            if  len(filelist):
                break
    if  not filelist:
        print "ERROR; unable to create filelist from %s" % fin
        sys.exit(1)

    headers = None
    with fopen(fout, 'wb') as ostream:
        for fname in filelist:
            if  verbose:
                print "Read", fname
            with fopen(fname, 'r') as istream:
                while True:
                    line = istream.readline()
                    if  not headers:
                        headers = line
                        ostream.write(headers)
                        continue
                    if  line == headers:
                        continue
                    if  not line:
                        break
                    ostream.write(line)

def main():
    "Main function"
    optmgr  = OptionParser()
    opts, _ = optmgr.get_opt()
    merger(opts.fin, opts.fout, opts.verbose)

if __name__ == '__main__':
    main()
