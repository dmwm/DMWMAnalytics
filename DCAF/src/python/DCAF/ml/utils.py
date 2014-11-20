#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=
"""
File       : utils.py
Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
Description: generic module with useful set of utilites
"""

# system modules
import optparse

def best_features(clf, xdf, targets):
    "Find, print and return best features using simple classifier"
    fit = clf.fit(xdf, targets)
    features = xdf.columns
    importances = clf.feature_importances_
    sorted_idx = np.argsort(importances)
    best_features = features[sorted_idx][::-1]
    best_indecies = importances[sorted_idx][::-1]
    print "Best features/importances:"
    for key, val in zip(best_features, best_indecies):
        print "   %20s: %.3f" % (key, val)
    return best_features

def keep_features(xdf, features):
    "Return dataset with desired features"
    drops = [c for c in xdf.columns if c not in features]
    return xdf.drop(drops, axis=1)

def norm_data(col, xdf, tdf):
    "Normalize given column in input/output datasets"
    # example by using StandardScaler
    # df['var'] = StandardScaler().fit_transform(df.var)
    # but here we need to combine both datasets into one and scale them across
    # all values, so we'll do it manually
    minval = min(xdf[col].min(), tdf[col].min())
    maxval = max(xdf[col].max(), tdf[col].max())
    meanval = (xdf[col].mean() + tdf[col].mean())/2.
    xnorm = (xdf[col] - meanval)/(maxval - minval)
    ynorm = (xdf[col] - meanval)/(maxval - minval)
    return xnorm, ynorm

def normalize(columns, xdf, tdf):
    "Normalize input/output datasets"
    for col in columns:
        if  col in xdf.columns and col in tdf.columns:
            xdf[col], tdf[col] = norm_data(col, xdf, tdf)

class OptionParser(object):
    "Option parser"
    def __init__(self, classifiers=None):
        self.parser = optparse.OptionParser()
        self.parser.add_option("--clf", action="store", type="string",
            default="rfc10", dest="clf",
            help="model classifier: %s" % classifiers)
        self.parser.add_option("--train-file", action="store", type="string",
            default="train.csv", dest="train", help="train file, default train.csv")
        self.parser.add_option("--test-file", action="store", type="string",
            default="test.csv", dest="test", help="test file, default test.csv")
        self.parser.add_option("--idx", action="store", type="int",
            default=0, dest="idx",
            help="initial index counter, default 0")
        self.parser.add_option("--limit", action="store", type="int",
            default=10000, dest="limit",
            help="number of rows to process, default 10000")
        self.parser.add_option("--verbose", action="store", type="int",
            default=0, dest="verbose",
            help="verbose output, default=0")
        self.parser.add_option("--roc", action="store_true",
            default=False, dest="roc",
            help="plot roc curve")
        self.parser.add_option("--full", action="store_true",
            default=False, dest="full",
            help="Use full sample for training, i.e. don't split")
        self.parser.add_option("--crossval", action="store_true",
            default=False, dest="cv",
            help="Perform cross-validation for given model and quit")
        self.parser.add_option("--gsearch", action="store", type="string",
            default=None, dest="gsearch",
            help="perform grid search, gsearch=<parameters>")
        self.parser.add_option("--predict", action="store_true",
            default=False, dest="predict",
            help="Yield prediction, used by pylearn")
    def options(self):
        "Returns parse list of options"
        return self.parser.parse_args()

