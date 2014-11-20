#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=
"""
File       : model.py
Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
Description: Generic classification model template
"""

# system modules
import sys
#import time
#import random
#import pprint
#try:
#    import cPickle as pickle
#except:
#    import pickle

# NumPy and pandas
import numpy as np
import pandas as pd

# sklearn modules
from sklearn.cross_validation import train_test_split
from sklearn import metrics

# local modules
from DCAF.ml.utils import OptionParser, normalize, logloss, GLF
from DCAF.ml.clf import classifiers, param_search, crossvalidation, print_clf_report

def get_auc(labels, predictions):
    fpr, tpr, thresholds = metrics.roc_curve(labels, predictions, pos_label=1)
    auc = metrics.auc(fpr,tpr)
    return auc

def read_data(fname, drops=[]):
    "Read and return processed data frame"
    xdf = pd.read_csv(fname)
    # fill NAs
    xdf = xdf.fillna(0)
    # drop fields
    if  drops:
        xdf = xdf.drop(drops, axis=1)
    # drop duplicates
    xdf = xdf.drop_duplicates(take_last=True, inplace=False)
    return xdf

def factorize(col, xdf, sdf=None):
    "Factorize given column in dataframe"
    if  sdf:
        vals = set(xdf[col] + sdf[col])
    else:
        vals = set(xdf[col])
    ids = []
    for uid, val in enumerate(vals):
        ids.append(uid)
    dval = dict(zip(vals, ids))
    out = []
    for val in xdf[col]:
        out.append(dval[val])
    return out

def model(train_file, test_file, clf_name, idx=0, limit=-1, gsearch=None,
          crossval=None, verbose=False):
    """
    Build and run ML algorihtm for given train/test dataframe
    and classifier name. The classifiers are defined externally
    in DCAF.ml.clf module.
    """

    # read data and normalize it
    drops = []
    xdf = read_data(train_file, drops)
    if  test_file:
        tdf = read_data(test_file, drops)
    else:
        tdf = None
    for col in ['era', 'primds', 'procds']:
        xdf[col] = factorize(col, xdf, tdf)
        if  tdf:
            tdf[col] = factorize(col, tdf, xdf)

    # normalize some columns
    columns = []
#    if  train_file and test_file:
#        normalize(columns, xdf, tdf)
#    print "train file:"
#    print xdf.ix[1]
#    if  test_file:
#        print "test file:"
#        print tdf.ix[1]

    # get target variable and exclude choice from train data
    tcol = 'target' # classification column name (what we'll predict)
    target = xdf[tcol]
    xdf = xdf.drop(tcol, axis=1)
    if  verbose:
        print "Columns:", ','.join(xdf.columns)
        print "Target:", target

    # split our train data
    x_train, x_rest, y_train, y_rest = \
            train_test_split(xdf, target, test_size=0.33)
    if  limit > -1 and x_rest.any():
        x_train = x_train[idx:limit]
        y_train = y_train[idx:limit]
        x_rest = x_rest[idx:limit]
        y_rest = y_rest[idx:limit]
    if  verbose:
        print "train shapes:", x_train.shape, y_train.shape
    clf = classifiers(verbose)[clf_name]
    print "clf:", clf
    if  gsearch:
        param_search(clf, x_train, y_train, x_rest, y_rest, gsearch)
        sys.exit(0)
    if  crossval:
        crossvalidation(clf, xdf, target)
        sys.exit(0)

    if  clf_name == 'rfc10':
        bfeatures = best_features(xdf, clf)
    fit = clf.fit(x_train, y_train)
    predictions = fit.predict(x_rest)
    loss = 0
    tot = 0
    for pval, yval in zip(predictions, y_rest):
        if  verbose:
            print "predict value %s, real value %s" % (pval, yval)
        loss += logloss(pval, yval)
        tot += 1
    print "Final Logloss", loss/tot
#    print_clf_report(y_rest, predictions)

    # test data
    if  test_file:
        predictions = fit.predict(tdf)
        if  not isinstance(predictions[0], int):
            predictions = [int(round(i)) for i in predictions]
        out = pd.DataFrame(zip(tdf['dataset'], predictions))
        ofile = 'prediction.txt'
        out.to_csv(ofile, header=False, index=False)

def main():
    "Main function"
    optmgr = OptionParser(classifiers().keys())
    opts, _ = optmgr.options()
    model(train_file=opts.train, test_file=opts.test, clf_name=opts.clf,
            idx=opts.idx, limit=opts.limit, gsearch=opts.gsearch,
            crossval=opts.cv, verbose=opts.verbose)

if __name__ == '__main__':
    main()
