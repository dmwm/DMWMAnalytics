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
import pandas as pd

# sklearn
from sklearn import metrics
from sklearn.metrics.scorer import SCORERS
#from sklearn.metrics import explained_variance_score
#from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# package modules
from DCAF.ml.utils import logloss, rates
from DCAF.utils.utils import fopen
from parse_csv import read_data


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
        self.parser.add_option("--plain-output", action="store_true",
            dest="plainout", default=False, help="Output result in comma separated format, default False")
        self.parser.add_option("--tiers-break", action="store_true",
            dest="tiers_break", default=False, help="Break scores by tiers")
        self.parser.add_option("--tiers-col", action="store", type="string",
            dest="tiers_col", default="tier", help="Name of tier column for tier break, default 'tier'")
        self.parser.add_option("--tiers-map", action="store", type="string",
            dest="tiers_map", default="", help="Mapping file for tier names, default None")
        self.parser.add_option("--tiers-map-kval", action="store", type="string",
            dest="tiers_map_kval", default="id,tier", help="Comma separated key and tier column names in mapping file, default 'id,tier'")
    def get_opt(self):
        "Return list of options"
        return self.parser.parse_args()

FLT_PAT = re.compile(r'(^[-]?\d+\.\d*$|^\d*\.{1,1}\d+$)')
INT_PAT = re.compile(r'(^[0-9-]$|^[0-9-][0-9]*$)')

def loader(ifile, target, sep=','):
    "Load prediction from given file"
    headers = None
    tidx  = None
    arr   = []
    with fopen(ifile, 'r') as istream:
        while True:
            row = istream.readline().replace('\n', '').replace('\r', '').split(sep)
            if  not headers:
                headers = row
                tidx = headers.index(target)
                continue
            if  len(row) < 2:
                break
            val  = row[tidx]
            if  INT_PAT.match(val):
                val = int(val)
            elif FLT_PAT.match(val):
                val = float(val)
            else:
                raise Exception("Parsed value '%s' has unknown data-type" % val)
            arr.append(val)
    return arr

def checker(predictions, y_true, scorer, verbose=False, plainout=False, tierflag=""):
    "Check our model prediction and dump logloss value"
    if  verbose:
        loss = 0
        tot = 0
        if  tierflag:
            print("Predictions for tier : %s" % tierflag)
        for pval, yval in zip(predictions, y_true):
            if  verbose:
                print("predict value %s, real value %s" % (pval, yval))
            loss += logloss(pval, yval)
            tot += 1
        print("Final Logloss          :", loss/tot)
    plain = ""
    # sklearn metrics for regression
    if  not scorer:
        print("ERROR: no scorer provided, please see --help for their list")
        sys.exit(1)
    for scr in scorer.split(','):
        slist = ['tp', 'tn', 'fp', 'fn', 'tpr', 'tnr', 'fpr', 'fnr']
        if  scr.lower() in slist:
            res = rates(y_true, predictions)
            if  plainout:
                plain += str(res[scr.lower()]) + ','
            else:
                print("Score metric (%s): %s" % (scr.upper(), res[scr.lower()]))
            continue        
        scr_str = repr(metrics.SCORERS[scr]).replace('make_scorer(', '').replace(')', '')
        method = scr_str.split(',')[0]
        res = getattr(metrics, method)(y_true, predictions)
        if  plainout:
            plain += str(res) + ','
        else:
            print("Score metric (%s): %s" % (method, res))
    if  plainout:
        if  tierflag:
            print("%s,%s" % (tierflag, plain[:-1]))
        else:
            print(plain[:-1])

def get_tiers(dfr, tiers_col, tiers_map, tiers_map_kval, verbose):
    # returns in same order as in opts.fin file
    tiers = dfr.loc[:, tiers_col]
    if  tiers_map:
        mdfr, _ = read_data(tiers_map, verbose, False)
        kcol = tiers_map_kval.split(',')[0]
        vcol = tiers_map_kval.split(',')[1]
        mkeys = mdfr.loc[:, kcol].tolist()
        mvals = mdfr.loc[:, vcol].tolist()
        replc = dict(zip(mkeys, mvals))
        tiers = tiers.replace(replc).tolist()
    return tiers

def dataframe2tiers(tiers, predictions):
    data = {}
    keys = []
    for i in xrange(len(tiers)):
        if  tiers[i] in keys:
            data[tiers[i]].append(predictions[i])
        else:
            keys.append(tiers[i])
            data[tiers[i]] = [predictions[i]]
    return data

def checker_with_tiers(predictions, real_values, fin, scorer, tiers_col, tiers_map, tiers_map_kval, plainout, verbose):
    dfr, _     = read_data(fin, verbose, False)
    tiers      = get_tiers(dfr, tiers_col, tiers_map, tiers_map_kval, verbose)
    tiers_pred = dataframe2tiers(tiers, predictions)
    tiers_real = dataframe2tiers(tiers, real_values)
    print("tier," + scorer)
    for tier in sorted(tiers_pred.keys()):
        # checker(predictions, y_true, scorer, verbose=False, plainout=False, tierflag="")
        checker(tiers_pred[tier], tiers_real[tier], scorer, verbose, plainout, tier)

def main():
    "Main function"
    optmgr  = OptionParser(SCORERS.keys())
    opts, _ = optmgr.get_opt()
    predictions = loader(opts.fpred, opts.fpred_target, opts.fpred_sep)
    real_values = loader(opts.fin, opts.fin_target, opts.fin_sep)
    if  len(predictions) != len(real_values):
        print("Error: input file and prediction file lengths are different")
        sys.exit(1)
    if  opts.tiers_break:
        checker_with_tiers(predictions, real_values, opts.fin, opts.scorer, opts.tiers_col, opts.tiers_map, opts.tiers_map_kval, opts.plainout, opts.verbose)
    else:
        checker(predictions, real_values, opts.scorer, opts.verbose, opts.plainout)

if __name__ == '__main__':
    main()
