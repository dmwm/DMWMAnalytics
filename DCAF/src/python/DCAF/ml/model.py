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
from utils import OptionParser, normalize
from clf import classifiers, param_search, crossvalidation, print_clf_report

def get_auc(labels, predictions):
    fpr, tpr, thresholds = metrics.roc_curve(labels, predictions, pos_label=1)
    auc = metrics.auc(fpr,tpr)
    return auc

def read_data(fname='data/train.csv', **kwds):
    "Read and return processed data frame"
    xdf = pd.read_csv(fname)
    # fill NAs
    xdf = xdf.fillna(0)
    # drop fields
    drops = []
    if  drops:
        xdf = xdf.drop(drops, axis=1)
    # drop duplicates
#    xdf = xdf.drop_duplicates(take_last=True, inplace=False)
    return xdf

def model(train_file='data/train.csv', test_file='data/test.csv',
          clf_name='rfc10', idx=0, limit=-1, gsearch=None,
          crossval=None, verbose=False):
    "Model for given plan"
    print "Construct model %s" % clf_name

    # read data and normalize it
    xdf = read_data(train_file)
    tdf = read_data(test_file)
    ids = tdf.customer_ID # replace with whatever id we need to use
    # normalize some columns
    columns = []
    normalize(columns, xdf, tdf)
    print "sample train:"
    print xdf.ix[1]
    print "sample test:"
    print tdf.ix[1]

    # exclude columns, e.g. customer id
#    drops = ['customer_ID']
#    if  drops:
#        xdf = xdf.drop(drops, axis=1)
#        tdf = tdf.drop(drops, axis=1)

    # get target variable and exclude choice from train data
    tcol = 'SOME_NAME' # classification column name (what we'll predict)
    target = xdf[tcol]
    xdf = xdf.drop(tcol, axis=1)
    print "Columns:", ','.join(xdf.columns)
    print "Target:", target

    # split our train data
    x_train, x_rest, y_train, y_rest = \
            train_test_split(xdf, target, test_size=0.33)
    if  limit > -1 and x_rest != None:
        x_train = x_train[idx:limit]
        y_train = y_train[idx:limit]
        x_rest = x_rest[idx:limit]
        y_rest = y_rest[idx:limit]
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
    print_clf_report(y_rest, predictions)

    # test data
    predictions = fit.predict(tdf)
    if  not isinstance(predictions[0], int):
        predictions = [int(round(i)) for i in predictions]
    out = pd.DataFrame(zip(ids, predictions))
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
