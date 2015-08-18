#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=
"""
File       : check_prediction.py
Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
Description: 
"""
from __future__ import print_function

# system modules
import os
import re
import sys
import gzip
import optparse

# sklearn
from sklearn import metrics
from sklearn.metrics.scorer import SCORERS
#from sklearn.metrics import explained_variance_score
#from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# package modules
from DCAF.ml.utils import logloss, rates
from DCAF.utils.utils import fopen

class OptionParser():
    def __init__(self, scorers=None):
        "User based option parser"
        if  scorers:
            scorers.sort()
        usage  = "Usage: %prog [options]\n"
        usage += 'Description: check prediction against data file\n'
        usage += 'Example: check_prediction --fin=valid_clf.csv.gz --fpred=pred.txt --scorer=accuracy,precision,recall,f1'
        self.parser = optparse.OptionParser(usage=usage)
        self.parser.add_option("--fin", action="store", type="string",
            dest="fin", default="", help="Input file, default None")
        self.parser.add_option("--fin-target", action="store", type="string",
            dest="fin_target", default="target", help="Name of target column for input file, default target")
        self.parser.add_option("--fin-sep", action="store", type="string",
            dest="fin_sep", default=",", help="Separator for input file, default comma")
        self.parser.add_option("--fpred", action="store", type="string",
            dest="fpred", default="", help="Prediction file")
        self.parser.add_option("--fpred-target", action="store", type="string",
            dest="fpred_target", default="prediction", help="Name of target column for prediction file, default prediction")
        self.parser.add_option("--fpred-sep", action="store", type="string",
            dest="fpred_sep", default=",", help="Separator for prediction file, default comma")
        self.parser.add_option("--scorer", action="store", type="string",
            dest="scorer", default="", help="model scorers: %s, default None" % scorers)
        self.parser.add_option("--verbose", action="store_true",
            dest="verbose", default=False, help="verbose mode")
    def get_opt(self):
        "Return list of options"
        return self.parser.parse_args()

FLT_PAT = re.compile(r'(^[-]?\d+\.\d*$|^\d*\.{1,1}\d+$)')
INT_PAT = re.compile(r'(^[0-9-]$|^[0-9-][0-9]*$)')

def loader(ifile, target, sep=','):
    "Load prediction from given file"
    headers = None
    tidx = None
    arr = []
    with fopen(ifile, 'r') as istream:
        while True:
            row = istream.readline().replace('\n', '').split(sep)
            if  not headers:
                headers = row
                tidx = headers.index(target)
                continue
            if  len(row) < 2:
                break
            val = row[tidx]
            if  INT_PAT.match(val):
                val = int(val)
            elif FLT_PAT.match(val):
                val = float(val)
            else:
                raise Exception("Parsed value '%s' has unknown data-type" % val)
            arr.append(val)
    return arr

def checker(predictions, y_true, scorer, verbose=False):
    "Check our model prediction and dump logloss value"
    if  verbose:
        loss = 0
        tot = 0
        for pval, yval in zip(predictions, y_true):
            if  verbose:
                print("predict value %s, real value %s" % (pval, yval))
            loss += logloss(pval, yval)
            tot += 1
        print("Final Logloss          :", loss/tot)

    # sklearn metrics for regression
    if  not scorer:
        print("ERROR: no scorer provided, please see --help for their list")
        sys.exit(1)
    for scr in scorer.split(','):
        if  scr.lower() in ['tp', 'tn', 'fp', 'fn']:
            res = rates(y_true, predictions)
            print("Score metric (%s): %s" % (scr.upper(), res[scr.lower()]))
            continue
        scr_str = repr(metrics.SCORERS[scr]).replace('make_scorer(', '').replace(')', '')
        method = scr_str.split(',')[0]
        res = getattr(metrics, method)(y_true, predictions)
        print("Score metric (%s): %s" % (method, res))

def main():
    "Main function"
    optmgr  = OptionParser(SCORERS.keys())
    opts, _ = optmgr.get_opt()

    predictions = loader(opts.fpred, opts.fpred_target, opts.fpred_sep)
    real_values = loader(opts.fin, opts.fin_target, opts.fin_sep)
    checker(predictions, real_values, opts.scorer, opts.verbose)

if __name__ == '__main__':
    main()
