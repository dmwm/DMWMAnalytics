#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=
"""
File       : clf.py
Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
Description: generic module with sklearn learners
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
from sklearn.linear_model import SGDRegressor
from sklearn.svm import SVR
from sklearn.cross_validation import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler

def learners(clf=None, kwds=None):
    "Return dict of available classifier"
    models = {}

    # common classifiers
    models['LinearSVC'] = svm.LinearSVC()
    models['SVC'] = svm.SVC()
    models['KNeighborsClassifier'] = KNeighborsClassifier()
    models['RandomForestClassifier'] = RandomForestClassifier()
    models['ExtraTreesClassifier'] = ExtraTreesClassifier()
    models['GaussianNB'] = GaussianNB()
    models['BernoulliNB'] = BernoulliNB()
    models['SGDClassifier'] = SGDClassifier()
    models['RidgeClassifier'] = RidgeClassifier()
    models['GradientBoostingClassifier'] = GradientBoostingClassifier()
    models['DecisionTreeClassifier'] = DecisionTreeClassifier()
    models['PCA'] = PCA()

    # common ensemble classifiers
    models['AdaBoostClassifier'] = AdaBoostClassifier()
    models['BaggincClassifier'] = BaggingClassifier()

    # examples how to construct pipelines
    steps = [('PCA', PCA(n_components='mle', whiten=True)), ('clf', models['RandomForestClassifier'])]
    models['pca_rfc'] = Pipeline(steps=steps)
    steps = [('PCA', PCA(n_components='mle', whiten=True)), ('clf', models['KNeighborsClassifier'])]
    models['pca_knc'] = Pipeline(steps=steps)
    steps = [('PCA', PCA(n_components='mle', whiten=True)), ('clf', models['SVC'])]
    models['pca_svc'] = Pipeline(steps=steps)
    steps = [('LDA', LDA()), ('clf', models['RandomForestClassifier'])]
    models['lda_rfc'] = Pipeline(steps=steps)

    # common regressors
    models['RandomForestRegressor'] = RandomForestRegressor()
    models['SVR'] = SVR()
    models['SGDRegressor'] = SGDRegressor()
    models['GradientBoostingRegressor'] = GradientBoostingRegressor()
    models['AdaBoostRegressor'] = AdaBoostRegressor()
    models['BagginRegressor'] = BaggingRegressor()

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
