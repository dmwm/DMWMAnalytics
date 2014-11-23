#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=
"""
File       : clf.py
Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
Description: generic module with sklearn classifiers
"""

# system modules
import os
import sys

# NumPy and pandas
import numpy as np
import pandas as pd

# sklean
from sklearn import svm, grid_search
from sklearn.metrics import roc_curve, auc, accuracy_score, confusion_matrix
from sklearn.metrics import classification_report, precision_score
from sklearn.pipeline import Pipeline
from sklearn.decomposition import PCA
from sklearn.lda import LDA
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.ensemble import GradientBoostingClassifier, AdaBoostClassifier
from sklearn.ensemble import BaggingClassifier
from sklearn.ensemble import GradientBoostingRegressor, ExtraTreesRegressor
from sklearn.ensemble import BaggingRegressor, AdaBoostRegressor
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.naive_bayes import GaussianNB, BernoulliNB
from sklearn.linear_model import SGDClassifier, RidgeClassifier, RidgeClassifierCV
from sklearn.svm import SVR
from sklearn.cross_validation import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler

def classifiers(clf=None, kwds=None):
    "Return dict of available classifier"
    models = {}

    # common classifiers
    models['svc'] = svm.LinearSVC()
    models['svm'] = svm.SVC()
    models['knc'] = KNeighborsClassifier()
    models['rfc'] = RandomForestClassifier()
    models['etc'] = ExtraTreesClassifier()
    models['gnb'] = GaussianNB()
    models['bnb'] = BernoulliNB()
    models['sgd'] = SGDClassifier()
    models['rgd'] = RidgeClassifier()
    models['gbc'] = GradientBoostingClassifier()
    models['dtc'] = DecisionTreeClassifier()
    models['pca'] = PCA()

    # common ensemble classifiers
    models['abc'] = AdaBoostClassifier()
    models['bc'] = BaggingClassifier()

    # examples how to construct pipelines
    steps = [('pca', PCA(n_components='mle', whiten=True)), ('clf', models['rfc'])]
    models['pca_rfc'] = Pipeline(steps=steps)
    steps = [('pca', PCA(n_components='mle', whiten=True)), ('clf', models['knc'])]
    models['pca_knc'] = Pipeline(steps=steps)
    steps = [('pca', PCA(n_components='mle', whiten=True)), ('clf', models['svc'])]
    models['pca_svc'] = Pipeline(steps=steps)
    steps = [('lda', LDA()), ('clf', models['rfc'])]
    models['lda_rfc'] = Pipeline(steps=steps)

    # common regressors
    models['rfr'] = RandomForestRegressor()
    models['svr'] = SVR()
    models['gbr'] = GradientBoostingRegressor()
    models['abr'] = AdaBoostRegressor()
    models['br'] = BaggingRegressor()

    return models

def param_search(clf, X_train, Y_train, X_rest, Y_rest, gsearch):
    """
    Perform grid search for given set of parameters which are
    specified as gsearch string
    """
    parameters = eval(gsearch)
    print "test classifier", clf
    print "parameters", parameters
    svr = clf
    scores = ['precision', 'recall']
    for score in scores:
        clf = grid_search.GridSearchCV(svr, parameters)
        clf.fit(X_train, Y_train)
        print("# Tuning hyper-parameters for %s" % score)
        print("Best parameters set found on development set:")
        print(clf.best_estimator_)
        print("Grid scores on development set:")
        for params, mean_score, scores in clf.grid_scores_:
            print("%0.3f (+/-%0.03f) for %r"
                  % (mean_score, scores.std() / 2, params))
        y_true, y_pred = Y_rest, clf.predict(X_rest)
        print(classification_report(y_true, y_pred))
    sys.exit(0)

def crossvalidation(clf, X_train, Y_train):
    "Perform cross-validation"
    scores = cross_val_score(clf, X_train, Y_train, cv=5)
    print("CV accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))

def print_clf_report(y_rest, predictions):
    "Prepare classification report"
    print pd.crosstab(y_rest, predictions, rownames=["Actual"], colnames=["Predicted"])
    print "classification report:\n", classification_report(y_rest, predictions)
