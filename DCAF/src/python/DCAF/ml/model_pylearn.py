#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable-msg=
"""
File       : model_pylearn.py
Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
Description: Generic template for pylearn Deep Learning model
    https://groups.google.com/forum/#!topic/pylearn-users/ZAARi3bU860
    https://github.com/admiral-chen/mlp_with_pylearn2/blob/master/mlp_test.py
"""

import warnings
warnings.simplefilter('ignore')
warnings.filterwarnings('ignore')

# system modules
import os
import sys
import time
import random
import numpy as np
import pandas as pd
try:
    import cPickle as pickle
except:
    import pickle

# local modules
from model import read_data
from utils import OptionParser, normalize

# sklearn
from sklearn.cross_validation import train_test_split

# pylearn, supress warnings from depdendent modules, e.g. scipy
with warnings.catch_warnings():
    import theano
    import pylearn2
    from pylearn2.config import yaml_parse
    from pylearn2.models import mlp
    from pylearn2.models.softmax_regression import SoftmaxRegression
    from pylearn2.training_algorithms import sgd, bgd, learning_rule
    from pylearn2.train_extensions.best_params import MonitorBasedSaveBest
    from pylearn2.costs import autoencoder
    from pylearn2 import termination_criteria
    from pylearn2.datasets.dense_design_matrix import DenseDesignMatrix
    from pylearn2.train import Train
    from pylearn2.utils import serial

def data_loader(train_file, test_file, output="traindata"):
    """
    Provide data in a format suitable for pylearn modules. The output data
    should be in a form of numpy array [[...], [...], [...]] where internal
    arrays are data points. The targets should be in a form of numpy array
    [[...], [...], [...]] where internal array represents classification
    points with zeros and ones. For instance, if we predict values 0,1,2,
    then classification points would be in a form of arrays with len=3
    where we'll have 1 for data point and zeros for the rest. For example,
    if target point is 1 the array will look like [0,1,0], while if target
    is 2 the array will be [0,0,1].

    Return target, X for trainig set or ids X for test set.
    """
    xdf = read_data(train_file)
    tdf = read_data(test_file)
    ids = tdf.customer_id # replace customer_id with whatever id we'll use
    normalize(xdf, tdf)
    # exclude columns, e.g. customer id
    drops = []
    if  drops:
        xdf = xdf.drop(drops, axis=1)
        tdf = tdf.drop(drops, axis=1)

    if  output == 'traindata':
        # get target variable and exclude choice from train data
        tcol = 'SOME_NAME' # classification column name (what we'll predict)
        target = xdf[tcol]
        xdf = xdf.drop(tcol, axis=1)
        print "Columns:", ','.join(xdf.columns)
        print "Target:", target
        return target, xdf
    else:
        return ids, tdf

def traindata_loader(train_file, test_file):
    """
    Convert train data into format used on
    http://neuralnetworksanddeeplearning.com/chap1.html
    We return two numpy arrays with train data and target values
    """
    targets, xdf = data_loader(train_file, test_file, 'traindata')
    print "#### traindata_loader"
#    print X.ix[1]
#    print targets[:5]
#    print X.values[1]
#    print Y.values
#    sys.exit(0)
    return xdf.values, targets

def testdata_loader(train_file, test_file):
    """
    Convert test data into format used on
    http://neuralnetworksanddeeplearning.com/chap1.html
    We return ids and numpy array of test data
    """
    ids, xdf = data_loader(train_file, test_file, 'testdata')
    return ids, xdf.values

def nnet(train_file, test_file, verbose=0):
    "NNET implementation based on pylearn"

    xdf, targets = traindata_loader(train_file, test_file)
    if  verbose:
        print "input sample:", xdf[1:2, :]
        print "output sample:", targets[1:2, :]
    # our model constants
    n_input = len(xdf[0]) # data input dimension
    n_output = len(targets[0]) # targets output dimension
    n_hidden1 = 10*n_input
    n_hidden2 = 10*n_output
    print "Settings: n_in=%s, n_out=%s, h1=%s, h2=%s" \
            % (n_input, n_output, n_hidden1, n_hidden2)

    # partition into train, valid, test
    x_tr, x_rest, y_tr, y_rest = \
            train_test_split(xdf, targets, test_size=0.33)
    x_va, x_te, y_va, y_te = \
            train_test_split(x_rest, y_rest, test_size=0.5)

    # represent input data in a form suitable for training with pylearn
    dataset_train = DenseDesignMatrix(X=x_tr, y=y_tr)
    dataset_valid = DenseDesignMatrix(X=x_va, y=y_va)
    dataset_test = DenseDesignMatrix(X=x_te, y=y_te)

    # create training model object
    irange = 0.
    sinit = n_input-5 # should be less than input dimension
    layer1 = mlp.RectifiedLinear(layer_name='h1', dim=n_hidden1,
                                 sparse_init=sinit)
    layer2 = mlp.RectifiedLinear(layer_name='h2', dim=n_hidden2,
                                 sparse_init=sinit)
    layer3 = mlp.Softmax(layer_name='y', n_classes=n_output, irange=irange)
    layers = [layer1, layer2, layer3]
#    layers = [mlp.Sigmoid(layer_name='h0', dim=500, sparse_init=15),
#              mlp.Softmax(layer_name='y', n_classes=n_output, irange=irange)]
    model = mlp.MLP(nvis=n_input, layers=layers)
#    model = SoftmaxRegression(nvis=n_input, n_classes=n_output, irange=irange)

    # construct algorithm object
    term1 = termination_criteria.EpochCounter(max_epochs=1000)
    term2 = termination_criteria.MonitorBased(channel_name="valid_objective",
            prop_decrease=1e-5, N=10)
    criterias = [term1, term2]
    terminate_criteria = termination_criteria.Or(criteria=criterias)
    monitoring_dataset = {'train': dataset_train,
                          'valid': dataset_valid, 'test': dataset_test}
    cost = autoencoder.MeanSquaredReconstructionError()
#    algorithm = bgd.BGD(line_search_mode='exhaustive', batch_size=100,
#            conjugate=1, reset_conjugate=0, reset_alpha=0,
#            updates_per_batch=10, monitoring_dataset=monitoring_dataset,
#            termination_criterion = terminate_criteria,
#    )
    lrule = learning_rule.Momentum(init_momentum=0.5)
    algorithm = sgd.SGD(batch_size=100, learning_rate=0.01,
            monitoring_dataset=monitoring_dataset,
            learning_rule=lrule,
            termination_criterion=terminate_criteria,
    )

    # construct extensions which can be used to monitor training progress
    # for our purpose we'll watch valid_y_mse value
    mon_criteria = 'valid_y_misclass'
    path = os.environ.get('PYLEARN2_TRAIN_FILE_FULL_STEM', '/tmp/models')
    spath = os.path.join(path, 'model.pkl')
#    extensions = [MonitorBasedSaveBest(channel_name=mon_criteria, save_path=spath)]
    ext1 = MonitorBasedSaveBest(channel_name=mon_criteria, save_path=spath)
    ext2 = learning_rule.MomentumAdjustor(start=1, saturate=10,
                                          final_momentum=0.99)
    extensions = [ext1, ext2]

    # perform training step for our model/algorithm and dataset
    train = Train(dataset=dataset_train, model=model,
                  algorithm=algorithm, extensions=extensions,
                  save_path=spath, save_freq=1)
    train.main_loop()

def nnet_predict(train_file, test_dir):
    "Generate prediction for given model and test dataset"
    path = os.environ.get('PYLEARN2_TRAIN_FILE_FULL_STEM', '/tmp/models')
    modelfile = os.path.join(path, 'model.pkl')
    model = serial.load(modelfile)
    gids, tdata = testdata_loader(train_file, test_file)
    testdata = DenseDesignMatrix(X=tdata)
    batch_size = 100
    model.set_batch_size(batch_size)

    # dataset must be multiple of batch size of some batches will have
    # different sizes. theano convolution requires a hard-coded batch size
    dim = len(tdata[0])
    print "Load: %s, dim=%s" % (modelfile, dim)
    extra = batch_size - dim % batch_size
    assert (dim + extra) % batch_size == 0
    if  extra > 0:
        print "Need to adjust batch size, bsize=%s, dim=%s, extra=%s" \
                % (batch_size, dim, extra)
    # construct prediction function
    xdf = model.get_input_space().make_batch_theano()
    target = model.fprop(X)
    func = theano.function([xdf], [target])
    res = func(testdata.X) # array of predicted values
    fit_val = res[0] # results are ndarray of pred values (another array)
    # pair gids with predicted values and yield predictions
    for idx in range(0, len(gids)):
        gid = gids[idx]
        # please note we take abs of predicted value,
        # since sometimes we get negative values
        # it is model's problem, but for output we'll take abs
        predictions = []
        for row in fit_val[idx]:
            val = row if row > 0 else 0
            predictions.append('%.10f' % val)
        print ','.join([gid] + predictions)

def run_yaml(fname):
    "Load given pylearn yaml and run the model"
    with open(fname, 'r') as stream:
        train = yaml_parse.load(stream.read())
        train.main_loop()

def main():
    "Main function for pylearn nnet"
    optmgr = OptionParser()
    opts, _ = optmgr.options()
    if  opts.predict:
        nnet_predict(opts.train, opts.test)
    else:
        nnet(opts.train, opts.test, opts.verbose)

if __name__ == '__main__':
    main()
