#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=
"""
File       : new_datasets.py
Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
Description: Find out which datasets were new in provided train/valid files
"""

# system modules
import os
import sys
import optparse

# local modules
from DCAF.utils.utils import fopen

class OptionParser():
    def __init__(self):
        "User based option parser"
        usage  = "Usage: %prog [options]\n"
        usage += "Description: produce file with new datasets/dbs pairs from provided training set and new data files"
        self.parser = optparse.OptionParser(usage=usage)
        self.parser.add_option("--fin", action="store", type="string",
            dest="fin", default="", help="Input train file")
        self.parser.add_option("--fnew", action="store", type="string",
            dest="fnew", default="", help="New data file")
        self.parser.add_option("--fout", action="store", type="string",
            dest="fout", default="", help="Output file")
    def get_opt(self):
        "Return list of options"
        return self.parser.parse_args()

def dataset_ids(fin):
    "Return dataset ids from given file"
    ids = set()
    headers = []
    didx = None
    tidx = None
    dbsidx = None
    with fopen(fin, 'r') as istream:
        while True:
            if  not headers:
                headers = istream.readline().replace('\n', '').split(',')
                didx = headers.index('dataset')
                tidx = headers.index('target')
                dbsidx = headers.index('dbs')
                continue
            row = istream.readline().replace('\n', '').split(',')
            if  len(row) < 2:
                break
            if  float(row[tidx]) > 0:
                ids.add((row[didx],row[dbsidx]))
    return set(ids)

def new_datasets(fin, fnew, fout):
    "Find out which datasets were new in provided train/valid files"
    train_ids = dataset_ids(fin)
    valid_ids = dataset_ids(fnew)
    ids = valid_ids - train_ids
    with fopen(fout, 'wb') as ostream:
        ostream.write('dataset,dbs\n')
        for pair in ids:
            ostream.write(','.join(pair)+'\n')

def main():
    "Main function"
    optmgr  = OptionParser()
    opts, _ = optmgr.get_opt()
    new_datasets(opts.fin, opts.fnew, opts.fout)

if __name__ == '__main__':
    main()
