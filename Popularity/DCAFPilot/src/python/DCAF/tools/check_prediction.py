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
from DCAF.tools.parse_csv import read_data

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
            dest="tiers_break", default=False, help="Flag to break scores by tiers")
        self.parser.add_option("--tiers-col", action="store", type="string",
            dest="tiers_col", default="tier", help="Name of tier column for tier break, default tier")
        self.parser.add_option("--tiers-map", action="store", type="string",
            dest="tiers_map", default="", help="Mapping file to alias tier ids to tier names, default None")
        self.parser.add_option("--tiers-map-kval", action="store", type="string",
            dest="tiers_map_kval", default="id,tier", help="Columns in mapping file to denote tier id and name, default 'id,tier'")
        self.parser.add_option("--threshold", action="store", type="float",
            dest="threshold", default=None, help="Threshold for probabilistic prediction to step to 1 or 0; e.g. 0.5, default None")
    def get_opt(self):
        "Return list of options"
        return self.parser.parse_args()

def str_to_num(s):
    "Converts string to number including scientific notation"
    try:
        return int(s)
    except:
        try:
            return float(s)
        except:
            raise Exception("Parsed value '%s' has unknown data-type" % s)

def loader(ifile, target, sep=',', threshold=None):
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
#             if  len(row) < 2:
            if  not row or (isinstance(row, list) and len(row)==1 and not row[0]):
                break
            # changed since previous approach did not recognice scientific notation
            val  = str_to_num(row[tidx])
            if  threshold:
                val = 1 if val >= threshold else 0
            arr.append(val)
    return arr

def checker(predictions, y_true, probabilities, scorer, verbose=False, plainout=False, tier=None):
    "Check our model prediction and dump logloss value"
    if  verbose:
        loss = 0
        tot = 0
        if  tier:
            print("Predictions for tier %s       :" % tier)
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
    slist = ['tp', 'tn', 'fp', 'fn', 'tpr', 'tnr', 'fpr', 'fnr', 'auc']
    res = None
    for scr in scorer.split(','):
        if  scr.lower() in slist:
            if  not res:
                res = rates(y_true, predictions, probabilities)
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
        if  tier:
            print("%s,%s" % (tier, plain[:-1]))
        else:
            print(plain[:-1])

def get_tiers(dfr, tiers_col, tiers_map, tiers_map_kval, verbose):
    "Extract column of tiers and replace its data by mapping names if provided"
    tiers = dfr.loc[:, tiers_col]
    if  tiers_map:
        mdfr, _ = read_data(tiers_map, verbose, False)
        kcol = tiers_map_kval.split(',')[0]
        vcol = tiers_map_kval.split(',')[1]
        if  verbose:
            print("Reading tier mapping file %s, id col: %s, name col: %s" % (tiers_map, kcol, vcol))
        mkeys = mdfr.loc[:, kcol].tolist()
        mvals = mdfr.loc[:, vcol].tolist()
        replc = dict(zip(mkeys, mvals))
        tiers = tiers.replace(replc).tolist()
    return tiers

def dataframe2tiers(tiers, predictions):
    "Aggregate predictions by tiers"
    data = {}
    keys = [] # unique tiers
    for i in xrange(len(tiers)):
        if  tiers[i] in keys:
            data[tiers[i]].append(predictions[i])
        else:
            keys.append(tiers[i])
            data[tiers[i]] = [predictions[i]]
    return data

def checker_with_tiers(predictions, real_values, probabilities, fin, scorer, tiers_col, tiers_map, tiers_map_kval, plainout, verbose):
    "Map validation data with tiers extracted from fin and check each tier seprately"
    dfr, _     = read_data(fin, verbose, False)
    tiers      = get_tiers(dfr, tiers_col, tiers_map, tiers_map_kval, verbose)
    tiers_pred = dataframe2tiers(tiers, predictions)
    tiers_real = dataframe2tiers(tiers, real_values)
    if  probabilities:
        tiers_prob = dataframe2tiers(tiers, probabilities)
    if  plainout:
        print("tier," + scorer)
    for tier in sorted(tiers_pred.keys()):
        if  probabilities:
            checker(tiers_pred[tier], tiers_real[tier], tiers_prob[tier], scorer, verbose, plainout, tier)
        else:
            checker(tiers_pred[tier], tiers_real[tier], None, scorer, verbose, plainout, tier)

def main():
    "Main function"
    optmgr  = OptionParser(SCORERS.keys())
    opts, _ = optmgr.get_opt()
    predictions = loader(opts.fpred, opts.fpred_target, opts.fpred_sep, opts.threshold)
    real_values = loader(opts.fin, opts.fin_target, opts.fin_sep, None)
    probabilities = None
    if  opts.threshold:
        probabilities = loader(opts.fpred, opts.fpred_target, opts.fpred_sep, None)
    if  len(predictions) != len(real_values):
        print("Error: input file and prediction file lengths are different: %s vs %s" % (len(predictions), len(real_values)))
        sys.exit(1)
    if  opts.tiers_break:
        checker_with_tiers(predictions, real_values, probabilities, opts.fin, opts.scorer, opts.tiers_col, opts.tiers_map, opts.tiers_map_kval, opts.plainout, opts.verbose)
    else:
        checker(predictions, real_values, probabilities, opts.scorer, opts.verbose, opts.plainout)

if __name__ == '__main__':
    main()
