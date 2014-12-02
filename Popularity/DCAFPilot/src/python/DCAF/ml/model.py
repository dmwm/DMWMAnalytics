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
from sklearn import preprocessing
from sklearn.metrics.scorer import SCORERS
from sklearn.pipeline import make_pipeline
from sklearn import metrics

# local modules
from DCAF.ml.utils import OptionParser, normalize, logloss, GLF
from DCAF.ml.clf import learners, param_search, crossvalidation, print_clf_report
import DCAF.utils.jsonwrapper as json

def get_auc(labels, predictions):
    fpr, tpr, thresholds = metrics.roc_curve(labels, predictions, pos_label=1)
    auc = metrics.auc(fpr,tpr)
    return auc

def read_data(fname, drops=[], idx=0, limit=-1):
    "Read and return processed data frame"
    comp = None
    if  fname.endswith('.gz'):
        comp = 'gzip'
    elif  fname.endswith('.bz2'):
        comp = 'bz2'
    xdf = pd.read_csv(fname, compression=comp)
    # fill NAs
    xdf = xdf.fillna(0)
    # drop fields
    if  drops:
        xdf = xdf.drop(drops, axis=1)
    # drop duplicates
    xdf = xdf.drop_duplicates(take_last=True, inplace=False)
    if  limit > -1:
        xdf = xdf[idx:limit]
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

def model(train_file, test_file, learner, lparams=None, scorer=None,
        scaler=None, idx=0, limit=-1, gsearch=None, crossval=None, verbose=False):
    """
    Build and run ML algorihtm for given train/test dataframe
    and classifier name. The learners are defined externally
    in DCAF.ml.clf module.
    """
    if  scaler:
        scaler = getattr(preprocessing, scaler)
    clf = learners()[learner]
    if  lparams:
        if  isinstance(lparams, str):
            lparams = json.loads(lparams)
        elif isinstance(lparams, dict):
            pass
        else:
            raise Exception('Invalid data type for lparams="%s", type: %s' % (lparams, type(lparams)))
        for key, val in lparams.items():
            setattr(clf, key, val)
    print "clf:", clf

    # read data and normalize it
    drops = []
    xdf = read_data(train_file, drops, idx, limit)
    if  test_file:
        tdf = read_data(test_file, drops)
    else:
        tdf = None
    for col in ['era', 'primds', 'procds']:
        xdf[col] = factorize(col, xdf, tdf)
        if  tdf:
            tdf[col] = factorize(col, tdf, xdf)

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
    if  verbose:
        print "train shapes:", x_train.shape, y_train.shape
    if  gsearch:
        param_search(clf, x_train, y_train, x_rest, y_rest, gsearch)
        sys.exit(0)
    if  crossval:
        crossvalidation(clf, xdf, target)
        sys.exit(0)

    if  scaler:
        x_train = scaler.fit_transform(x_train)
    fit = clf.fit(x_train, y_train)
    predictions = fit.predict(x_rest)
    if  scorer:
        print "Score metric: %s" % scorer
        print metrics.SCORERS[scorer](clf, x_rest, y_rest)
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

def model_iter(train_file_list, test_file, learner, lparams=None, scaler=None, verbose=False):
    """
    Build and run ML algorihtm for given train/test dataframe
    and classifier name. The learners are defined externally
    in DCAF.ml.clf module.
    """
    if  learner not in ['SGDClassifier', 'SGDRegressor']:
        raise Exception("Unsupported learner %s" % learner)
    clf = learners()[learner]
    if  lparams:
        if  isinstance(lparams, str):
            lparams = json.loads(lparams)
        elif isinstance(lparams, dict):
            pass
        else:
            raise Exception('Invalid data type for lparams="%s", type: %s' % (lparams, type(lparams)))
        for key, val in lparams.items():
            setattr(clf, key, val)
    print "clf:", clf

    drops = []
    tcol = 'target' # classification column name (what we'll predict)
    fit = None
    for train_file in train_file_list:
        # read data and normalize it
        xdf = read_data(train_file, drops)
        if  test_file:
            tdf = read_data(test_file, drops)
        else:
            tdf = None
        for col in ['era', 'primds', 'procds']:
            xdf[col] = factorize(col, xdf, tdf)
            if  tdf:
                tdf[col] = factorize(col, tdf, xdf)

        # get target variable and exclude choice from train data
        target = xdf[tcol]
        xdf = xdf.drop(tcol, axis=1)
        if  verbose:
            print "Columns:", ','.join(xdf.columns)
            print "Target:", target

        if  scaler:
            xdf = getattr(preprocessing, scaler)().fit_transform(xdf)
#        x_train = xdf
#        y_train = target
        x_train, x_rest, y_train, y_rest = \
                train_test_split(xdf, target, test_size=0.1)
        fit = clf.partial_fit(x_train, y_train)
        print "### SCORE", clf.score(x_rest, y_rest)

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
    optmgr = OptionParser(learners().keys(), SCORERS.keys())
    opts, _ = optmgr.options()
    if  opts.train.find(',') != -1: # list of files
        train_files = opts.train.split(',')
        print "Train file list", train_files
        model_iter(train_file_list=train_files, test_file=opts.test,
                learner=opts.learner, lparams=opts.lparams,
                scaler=opts.scaler, verbose=opts.verbose)
    else:
        model(train_file=opts.train, test_file=opts.test,
                learner=opts.learner, lparams=opts.lparams,
                scorer=opts.scorer, scaler=opts.scaler,
                idx=opts.idx, limit=opts.limit, gsearch=opts.gsearch,
                crossval=opts.cv, verbose=opts.verbose)

if __name__ == '__main__':
    main()
