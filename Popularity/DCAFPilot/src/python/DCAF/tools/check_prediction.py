#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=
"""
File       : check_prediction.py
Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
Description: 
"""

# system modules
import os
import sys
import gzip
import optparse

# pandas
import pandas as pd

# package modules
from DCAF.ml.utils import logloss

class OptionParser():
    def __init__(self):
        "User based option parser"
        self.parser = optparse.OptionParser()
        self.parser.add_option("--fin", action="store", type="string",
            dest="fin", default="", help="Input file")
        self.parser.add_option("--fin-target", action="store", type="string",
            dest="fin_target", default="target", help="Name of target column for input file")
        self.parser.add_option("--fin-sep", action="store", type="string",
            dest="fin_sep", default="", help="Separator for input file")
        self.parser.add_option("--fpred", action="store", type="string",
            dest="fpred", default="", help="Prediction file")
        self.parser.add_option("--fpred-target", action="store", type="string",
            dest="fpred_target", default="prediction", help="Name of target column for prediction file")
        self.parser.add_option("--fpred-sep", action="store", type="string",
            dest="fpred_sep", default=",", help="Separator for prediction file")
        self.parser.add_option("--verbose", action="store_true",
            dest="verbose", default=False, help="verbose mode")
    def get_opt(self):
        "Return list of options"
        return self.parser.parse_args()

def loader(ifile, target, sep=','):
    "Load prediction from given file"
    comp = None
    if  ifile.endswith('.gz'):
        comp = 'gzip'
    elif  ifile.endswith('.bz2'):
        comp = 'bz2'
    df = pd.read_csv(ifile, sep=sep)
    return df[target]

def checker(predictions, y_rest, verbose=False):
    "Check our model prediction and dump logloss value"
    loss = 0
    tot = 0
    for pval, yval in zip(predictions, y_rest):
        if  verbose:
            print "predict value %s, real value %s" % (pval, yval)
        loss += logloss(pval, yval)
        tot += 1
    print "Final Logloss", loss/tot

def main():
    "Main function"
    optmgr  = OptionParser()
    opts, _ = optmgr.get_opt()

    predictions = loader(opts.fpred, opts.fpred_target, opts.fpred_sep)
    real_values = loader(opts.fin, opts.fin_target, opts.fin_sep)
    checker(predictions, real_values, opts.verbose)

if __name__ == '__main__':
    main()
