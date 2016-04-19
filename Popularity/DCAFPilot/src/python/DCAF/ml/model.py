#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=
"""
File       : model.py
Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
Description: Generic classification model template
"""
from __future__ import print_function

# system modules
import os
import sys
import time
import glob
import random
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
from DCAF.ml.utils import OptionParser, normalize, logloss, GLF, rates
from DCAF.ml.clf import learners, param_search, crossvalidation, print_clf_report
import DCAF.utils.jsonwrapper as json

def files(idir, ext=".csv.gz"):
    "Return list of files from given directory"
    for fname in os.listdir(idir):
        if  fname.endswith(ext):
            yield '%s/%s' % (idir, fname)

def get_auc(labels, predictions):
    fpr, tpr, thresholds = metrics.roc_curve(labels, predictions, pos_label=1)
    auc = metrics.auc(fpr,tpr)
    return auc

def read_data(fname, drops=[], idx=0, limit=-1, scaler=None):
    "Read and return processed data frame"
    comp = None
    if  fname.endswith('.gz'):
        comp = 'gzip'
    elif  fname.endswith('.bz2'):
        comp = 'bz2'
    if  scaler:
        xdf = pd.read_csv(fname, compression=comp, dtype=np.float32)
    else:
        xdf = pd.read_csv(fname, compression=comp)
    # fill NAs
    xdf = xdf.fillna(0)
    # drop fields
    if  drops:
        xdf = xdf.drop(drops, axis=1)
    # drop duplicates
#    xdf = xdf.drop_duplicates(take_last=True, inplace=False)
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

def get_dbs_header(tdf, fname):
    "Returns DBS header, 'dbs' is in old dataframe, 'dbsinst' in new"
    dfkeys = tdf.keys()
    if  'dbsinst' in dfkeys:
        return 'dbsinst'
    elif 'dbs' in dfkeys:
        return 'dbs'
    else:
        msg = "ERROR: dbs header in file %s was not found"
        print(msg % fname)
        sys.exit(1)

def model(train_file, newdata_file, idcol, tcol, learner, lparams=None,
        drops=None, split=0.3, scorer=None, scaler=None, ofile=None,
        idx=0, limit=-1,  gsearch=None, crossval=None, seed=123,
        verbose=False, timeout=None, proba=False):
    """
    Build and run ML algorihtm for given train/test dataframe
    and classifier name. The learners are defined externally
    in DCAF.ml.clf module.
    """
    clf = learners()[learner]
    if  proba and not (hasattr(clf, 'predict_proba') and callable(getattr(clf, 'predict_proba'))):
        raise Exception("ERROR: model %s does not provide method 'predict_proba'" % learner)
    if  lparams:
        if  isinstance(lparams, str):
            lparams = json.loads(lparams)
        elif isinstance(lparams, dict):
            pass
        else:
            raise Exception('Invalid data type for lparams="%s", type: %s' % (lparams, type(lparams)))
        for key, val in lparams.items():
            setattr(clf, key, val)
    setattr(clf, "random_state", seed)
    random.seed(seed)
    print(clf)
    if  split:
        if  isinstance(split, int):
            split = split/100.
        elif isinstance(split, float):
            pass
        elif isinstance(split, basestring):
            split = float(split)
        print("Split level: train %s%%, validation %s%%" % (round((1-split)*100), round(split*100)))
    if  verbose:
        print("idx/limit", idx, limit)

    # read data and normalize it
    if  drops:
        if  isinstance(drops, basestring):
            drops = drops.split(',')
        if  idcol not in drops:
            drops += [idcol]
    else:
        drops = [idcol]
    xdf = read_data(train_file, drops, idx, limit, scaler)

    # get target variable and exclude choice from train data
    target = xdf[tcol]
    xdf = xdf.drop(tcol, axis=1)
    if  verbose:
        print("Train file", train_file)
        print("Columns:", ','.join(xdf.columns))
        print("train shapes:", xdf.shape, target.shape)
        if  verbose>1:
            print("Target:", tcol, target)

    # split our train data
    if  split:
        x_train, x_rest, y_train, y_rest = \
                train_test_split(xdf, target, test_size=split, random_state=seed)
        if  verbose:
            print("train shapes after splitting:", x_train.shape, y_train.shape)
    else:
        x_train = xdf
        y_train = target
        x_rest = None
        y_rest = None
    if  gsearch:
        param_search(clf, x_train, y_train, x_rest, y_rest, gsearch)
        sys.exit(0)
    if  crossval:
        crossvalidation(clf, xdf, target)
        sys.exit(0)

    if  scaler:
        x_train = getattr(preprocessing, scaler)().fit_transform(x_train)
    time0 = time.time()
    fit = clf.fit(x_train, y_train)
    rtime = time.time()-time0
    if  verbose:
        print("Train elapsed time", time.time()-time0)
    if  split:
        if  proba:
            print("ERROR in model.py: probabilities not supported in split mode")
            sys.exit(1)
        time0 = time.time()
        predictions = fit.predict(x_rest)
        rtime += time.time()-time0
        try:
            importances = clf.feature_importances_
            if  importances.any():
                print("Feature ranking:")
                columns = xdf.columns
                indices = np.argsort(importances)[::-1]
                num = 9 if len(columns)>9 else len(columns)
                for f in range(num):
                    print("%d. importance %f, feature %s" % (f + 1, importances[indices[f]], columns[indices[f]]))
        except:
            pass
        if  scorer:
            for scr in scorer.split(','):
                slist = ['tp', 'tn', 'fp', 'fn', 'tpr', 'tnr', 'fpr', 'fnr']
                if  scr.lower() in slist:
                    res = rates(y_rest, predictions)
                    print("Score metric (%s): %s" % (scr.upper(), res[scr.lower()]))
                    continue
                scr_str = repr(metrics.SCORERS[scr]).replace('make_scorer(', '').replace(')', '')
                method = scr_str.split(',')[0]
                res = getattr(metrics, method)(y_rest, predictions)
                print("Score metric (%s): %s" % (method, res))
        if  verbose:
            loss = 0
            tot = 0
            for pval, yval in zip(predictions, y_rest):
                if  verbose>1:
                    print("predict value %s, real value %s" % (pval, yval))
                loss += logloss(pval, yval)
                tot += 1
            print("Final Logloss", loss/tot)
    else:
        print("Since there is no train/validation splitting, no prediction metrics will be shown")

    # new data file for which we want to predict
    if  newdata_file:
        nfiles = []
        if  os.path.isfile(newdata_file):
            nfiles = [newdata_file]
        else:
            if newdata_file.find(',') != -1:
                nfiles = newdata_file.split(',')
            elif newdata_file.find('*') != -1:
                nfiles = glob.glob(newdata_file)
            elif os.path.isdir(newdata_file):
                for ext in ['.csv.gz', '.csv', 'csv.bz2']:
                    nfiles = [f for f in findfiles(fin, ext)]
            else:
                print("ERROR: unrecognized input --newdata=%s" % newdata_file)
                sys.exit(1)
            if  not len(nfiles):
                print("WARNING: no files to predict in %s" % newdata_file)
                return
        outfname = None
        for ni, nfile in enumerate(nfiles): # iterate on files to predict
            if  len(nfiles) > 1:
                outfname = '%s_%s_%s' % (learner, ofile, ni)
                print("You provided file list, the output file name %s will be replaced with %s_%s_%s" % (ofile, learner, ofile, ni))
            else:
                outfname = ofile
            tdf = read_data(nfile, drops, scaler=scaler)
            if  tcol in tdf.columns:
                tdf = tdf.drop(tcol, axis=1)
            if  verbose:
                print("New data file", nfile)
                print("Columns:", ','.join(tdf.columns))
                print("test shapes:", tdf.shape)
            datasets = [int(i) for i in list(tdf['dataset'])]
            dbs_h = get_dbs_header(tdf, nfile)
            dbses = [int(i) for i in list(tdf[dbs_h])]
            if  scaler:
                tdf = getattr(preprocessing, scaler)().fit_transform(tdf)
            if  verbose:
                print(tdf)
            time0 = time.time()
            predictions = fit.predict(tdf) if not proba else np.asarray(fit.predict_proba(tdf))[:,list(fit.classes_).index(1)]
            rtime += time.time()-time0
            out = pd.DataFrame({'dataset':datasets, dbs_h: dbses, 'prediction':predictions})
            if  outfname:
                out.to_csv(outfname, header=True, index=False)
            if  timeout: # output running time
                data = {}
                if  os.path.isfile(timeout): # append if file exists
                    headers = []
                    for line in open(timeout, 'r'):
                        line = line.strip(" \r\n").split(',')
                        if  not headers:
                            headers = line
                            if  line[0] != 'model' or line[1] != 'running_time_s':
                                print("Error writing model running time to %s: unrecognized output file found." % timeout)
                            continue
                        else:
                            data[line[0]] = float(line[1])
                if  learner in data:
                    data[learner] += rtime
                else:
                    data[learner] = rtime
                fstream = open(timeout, 'w')
                fstream.write("model,running_time_s\n")
                for key in sorted(data.keys()):
                    fstream.write("%s,%.3f\n" % (key,data[key]))
                fstream.close()

def model_iter(train_file_list, newdata_file, idcol, tcol,
    learner, lparams=None, drops=None, split=0.1, scaler=None, ofile=None, seed=123, verbose=False):
    """
    Build and run ML algorihtm for given train/test dataframe
    and classifier name. The learners are defined externally
    in DCAF.ml.clf module.
    """
    if  learner not in ['SGDClassifier', 'SGDRegressor']:
        raise Exception("Unsupported learner %s" % learner)
    clf = learners()[learner]
    setattr(clf, "random_state", seed)
    random.seed(seed)
    if  lparams:
        if  isinstance(lparams, str):
            lparams = json.loads(lparams)
        elif isinstance(lparams, dict):
            pass
        else:
            raise Exception('Invalid data type for lparams="%s", type: %s' % (lparams, type(lparams)))
        for key, val in lparams.items():
            setattr(clf, key, val)
    print("clf:", clf)

    if  drops:
        if  isinstance(drops, basestring):
            drops = drops.split(',')
        if  idcol not in drops:
            drops += [idcol]
    else:
        drops = [idcol]
    fit = None
    for train_file in train_file_list:
        print("Train file", train_file)
        # read data and normalize it
        xdf = read_data(train_file, drops, scaler=scaler)

        # get target variable and exclude choice from train data
        target = xdf[tcol]
        xdf = xdf.drop(tcol, axis=1)
        if  verbose:
            print("Columns:", ','.join(xdf.columns))
            print("Target:", target)

        if  scaler:
            xdf = getattr(preprocessing, scaler)().fit_transform(xdf)
        if  split:
            x_train, x_rest, y_train, y_rest = \
                    train_test_split(xdf, target, test_size=0.1, random_state=seed)
            time0 = time.time()
            fit = clf.partial_fit(x_train, y_train)
            if  verbose:
                print("Train elapsed time", time.time()-time0)
            print("### SCORE", clf.score(x_rest, y_rest))
        else:
            x_train = xdf
            y_train = target
            time0 = time.time()
            fit = clf.partial_fit(x_train, y_train)
            if  verbose:
                print("Train elapsed time", time.time()-time0)

    # new data for which we want to predict
    if  newdata_file:
        tdf = read_data(newdata_file, drops, scaler=scaler)
        if  tcol in tdf.columns:
            tdf = tdf.drop(tcol, axis=1)
        datasets = [int(i) for i in list(tdf['dataset'])]
        dbs_h = get_dbs_header(tdf, newdata_file)
        dbses = [int(i) for i in list(tdf[dbs_h])]
        if  scaler:
            tdf = getattr(preprocessing, scaler)().fit_transform(tdf)
        predictions = fit.predict_proba(tdf)
        data = {'dataset':datasets, dbs_h: dbses, 'prediction':predictions}
        out = pd.DataFrame(data=data)
        if  ofile:
            out.to_csv(ofile, header=True, index=False)

def main():
    "Main function"
    optmgr = OptionParser(learners().keys(), SCORERS.keys())
    opts, _ = optmgr.options()
    if  opts.learner_help:
        obj = learners()[opts.learner_help]
        print(obj)
        print(obj.__doc__)
        sys.exit(0)
    ofile = opts.predict
    if  not ofile:
        ofile = "%s.predictions" % opts.learner
    model2run = 'model'
    if  opts.train.find(',') != -1: # list of files
        train_files = opts.train.split(',')
        model2run = 'model_iter'
    elif os.path.isdir(opts.train): # we got directory name
        for ext in ['.csv.gz', '.csv']:
            train_files = [f for f in files(opts.train, ext)]
            model2run = 'model_iter'
            if  len(train_files):
                break

#    random.seed(12345)
    if  model2run == 'model_iter':
        model_iter(train_file_list=train_files, newdata_file=opts.newdata,
                idcol=opts.idcol, tcol=opts.target,
                learner=opts.learner, lparams=opts.lparams,
                drops=opts.drops, split=opts.split,
                scaler=opts.scaler, ofile=ofile, seed=opts.seed, verbose=opts.verbose)
    else:
        model(train_file=opts.train, newdata_file=opts.newdata,
                idcol=opts.idcol, tcol=opts.target,
                learner=opts.learner, lparams=opts.lparams,
                drops=opts.drops, split=opts.split,
                scorer=opts.scorer, scaler=opts.scaler, ofile=ofile,
                idx=opts.idx, limit=opts.limit, gsearch=opts.gsearch,
                crossval=opts.cv, seed=opts.seed, verbose=opts.verbose,
                timeout=opts.timeout, proba=opts.proba)

if __name__ == '__main__':
    main()
