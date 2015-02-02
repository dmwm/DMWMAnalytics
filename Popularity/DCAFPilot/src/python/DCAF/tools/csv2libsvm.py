#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=
"""
File       : csv2libsvm.py
Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
Description: 
Convert CSV file to libsvm format, the idea was taken from
https://raw.githubusercontent.com/zygmuntz/phraug/master/csv2libsvm.py

libSVM data format:
    1 101:1.2 102:0.03
    0 1:2.1 10001:300 10002:400 

Each line represent a single instance, and in the first line '1' is the
instance label,'101' and '102' are feature indices, '1.2' and '0.03' are
feature values. In the binary classification case, '1' is used to indicate
positive samples, and '0' is used to indicate negative samples.

"""

# system modules
import os
import sys
import gzip
import bz2
import optparse

class OptionParser():
    def __init__(self):
        "User based option parser"
        usage = 'Usage: %prog [options]\n'
        usage += 'Description: convert input CSV file into libSVM data-format\n'
        usage += 'Example: %prog --fin=file.csv.gz --fout=file.libsvm'
        self.parser = optparse.OptionParser(usage=usage)
        self.parser.add_option("--fin", action="store", type="string",
            dest="fin", default="", help="Input file")
        self.parser.add_option("--fout", action="store", type="string",
            dest="fout", default="", help="Output file")
        self.parser.add_option("--idcol", action="store", type="string",
            dest="idcol", default="id", help="id variable name")
        self.parser.add_option("--target", action="store", type="string",
            dest="target", default="target", help="Target variable name")
        self.parser.add_option("--prediction", action="store", type="string",
            default='', dest="preds", help="prediction value to assign")
        self.parser.add_option("--verbose", action="store_true",
            dest="debug", default=False, help="Turn on verbose output")
    def get_opt(self):
        "Return list of options"
        return self.parser.parse_args()

def fopen(fin, mode='r'):
    "Return file descriptor for given file"
    if  fin.endswith('.gz'):
        stream = gzip.open(fin, mode)
    elif  fin.endswith('.bz2'):
        stream = bz2.BZ2File(fin, mode)
    else:
        stream = open(fin, mode)
    return stream

def convert(fin, fout, target='target', idcol='id', preds=''):
    "Convert from CSV to libSVM data format"
    istream = fopen(fin, 'r')
    headers = []
    tidx = -1 # target column is usually last
    ridx = 0 # index column is usually first
    with fopen(fout, 'wb') as ostream:
        while True:
            if  not headers:
                headers = istream.readline().replace('\n', '').split(',')
                try:
                    tidx = headers.index(target)
                except ValueError:
                    tidx = None
                ridx = headers.index(idcol)
                continue
            try:
                vals = istream.readline().replace('\n', '').split(',')
            except:
                break
            if  len(vals) == 1 and not vals[0]:
                break
            ostream.write(row_svm(vals, tidx, ridx, preds))

def row_svm(vals, tidx, ridx, preds):
    "Yield libSVM row"
    new_line = []
    if  preds:
        label = preds
    else:
        label = vals[tidx]
        if float( label ) == 0.0:
            label = "0"
    new_line.append( label )

    for idx, item in enumerate(vals):
        if  idx == ridx or idx == tidx:
            continue
        if  item == '' or float(item) == 0.0:
            continue
        new_item = "%s:%s" % (idx + 1, item)
        new_line.append(new_item)
    return ' '.join(new_line) + '\n'

def main():
    "Main function"
    optmgr  = OptionParser()
    opts, _ = optmgr.get_opt()
    convert(opts.fin, opts.fout, opts.target, opts.idcol, opts.preds)

if __name__ == '__main__':
    main()

