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

class OptionParser():
    def __init__(self):
        "User based option parser"
        self.parser = optparse.OptionParser()
        self.parser.add_option("--pred", action="store", type="string",
            dest="pred", default="", help="Input prediction file")
        self.parser.add_option("--popdb", action="store", type="string",
            dest="popdb", default="", help="Input popular datasets file")
    def get_opt(self):
        "Return list of options"
        return self.parser.parse_args()

def verify_prediction(pred, popdb):
    "Verify prediction file against popdb one"
    pop_data = dict([(r.replace('\n',''),1) for r in open(popdb, 'r').readlines()])
    count = 0
    total = 0
    for line in open(pred, 'r').readlines():
        prob, dataset = line.replace('\n', '').split(',')
        total += 1
        if  dataset in pop_data and float(prob)>0:
            print '%s,%s' % (prob, dataset)
            count += 1
    print "Popular datasets  :", len(pop_data.keys())
    print "Predicted datasets:", total
    print "Wrongly predicted :", count

def main():
    optmgr  = OptionParser()
    opts, _ = optmgr.get_opt()
    verify_prediction(opts.pred, opts.popdb)

if __name__ == '__main__':
    main()
