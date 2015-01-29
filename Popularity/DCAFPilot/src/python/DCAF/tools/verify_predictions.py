#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=
"""
File       : verify_prediction.py
Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
Description: Verify prediction file against popular datasets
"""

# system modules
import optparse

# local modules
from DCAF.utils.utils import fopen

class OptionParser():
    def __init__(self):
        "User based option parser"
        self.parser = optparse.OptionParser()
        self.parser.add_option("--pred", action="store", type="string",
            dest="pred", default="", help="Input prediction file")
        self.parser.add_option("--popdb", action="store", type="string",
            dest="popdb", default="", help="Input popular datasets file")
        self.parser.add_option("--verbose", action="store_true",
            dest="verbose", default=False, help="verbose mode")
    def get_opt(self):
        "Return list of options"
        return self.parser.parse_args()

def verify_prediction(pred, popdb, verbose=False):
    "Verify prediction file against popdb one"
    pop_data = dict([(r.replace('\n',''),1) for r in fopen(popdb, 'r').readlines()])
    count = 0
    total = 0
    popular = 0
    totpop = 0
    for line in fopen(pred, 'r').readlines():
        prob, dataset = line.replace('\n', '').split(',')
        total += 1
        if  float(prob)>0:
            popular += 1
        if  dataset in pop_data:
            totpop += 1
            if  float(prob)>0:
                if  verbose:
                    print '%s,%s' % (prob, dataset)
                count += 1
    print "Popular datasets             :", len(pop_data.keys())
    print "Total # of datasets          :", total
    print "# of datasets in popular set :", totpop
    print "Wrongly predicted            :", count
    print "Predicted as popular         :", popular

def main():
    optmgr  = OptionParser()
    opts, _ = optmgr.get_opt()
    verify_prediction(opts.pred, opts.popdb, opts.verbose)

if __name__ == '__main__':
    main()
