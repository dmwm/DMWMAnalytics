#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=
"""
File       : slice_data.py
Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
Description: Helper script which allows to slice data/prediction
with respect to given ids files. This is usefull when we want
to select only those data which contains new dataset, e.g.
from validation set. In this case new dataset ids can be supplied
to this script and it will select prediction/dataset according
to this id list.
"""

# system modules
import os
import sys
import gzip
import optparse

# local modules
from DCAF.utils.utils import fopen

class OptionParser():
    def __init__(self):
        "User based option parser"
        self.parser = optparse.OptionParser()
        self.parser.add_option("--pred", action="store", type="string",
            dest="pred", default="", help="prediction file")
        self.parser.add_option("--data", action="store", type="string",
            dest="data", default="", help="dataset file")
        self.parser.add_option("--ids", action="store", type="string",
            dest="ids", default="", help="ids file")
    def get_opt(self):
        "Return list of options"
        return self.parser.parse_args()

def select(pred, data, ids):
    "Select prediction and data based on provided ids"
    sids = set([str(i.replace('\n','')) for i in myopen(ids).readlines() if not i.startswith('id')])
    ipred = fopen(pred, 'r')
    idata = fopen(data, 'r')
    pheaders = []
    dheaders = []
    didx = 0
    with fopen('new_pred.txt', 'wb') as opred, fopen('new_data.txt', 'wb') as odata:
        while True:
            pline = ipred.readline().replace('\n', '').split(',')
            dline = idata.readline().replace('\n', '').split(',')
            if  not dheaders:
                pheaders = pline
                dheaders = dline
                didx = dheaders.index('dataset')
                opred.write(','.join(pheaders)+'\n')
                odata.write(','.join(dheaders)+'\n')
                continue
            if  len(pline) == 1:
                break
            if  pline[0] in sids and dline[didx] in sids and dline[-1]=='1':
                opred.write(','.join(pline)+'\n')
                odata.write(','.join(dline)+'\n')

def main():
    "Main function"
    optmgr  = OptionParser()
    opts, _ = optmgr.get_opt()
    select(opts.pred, opts.data, opts.ids)

if __name__ == '__main__':
    main()
