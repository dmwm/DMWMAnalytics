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
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.ensemble import GradientBoostingClassifier, AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB, BernoulliNB
from sklearn.linear_model import SGDClassifier, RidgeClassifier, RidgeClassifierCV
from sklearn.cross_validation import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler

def classifiers(verbose=0):
    "Return dict of available classifier"
    models = {}
    cost = 20 # 20 gives 0.88
    models['svc'] = svm.LinearSVC(C=cost, dual=False, verbose=verbose)
    models['svm_sigm'] = svm.SVC(C=1.0, kernel='sigmoid', degree=3, gamma=0.0)
    models['svm_poly'] = svm.SVC(C=1.0, kernel='poly', degree=3, gamma=0.0)
    models['svm_rbf']= svm.SVC(kernel='rbf', C=cost, verbose=verbose)
    models['knc'] = KNeighborsClassifier()
    rfc_params = {'max_features': 20, 'min_samples_split': 10, 'min_samples_leaf': 10}
    models['rfc10_params'] = RandomForestClassifier(n_estimators=10, n_jobs=-1, **rfc_params)
    models['rfc10'] = RandomForestClassifier(n_estimators=10, n_jobs=-1, criterion='entropy')
    models['rfc100'] = RandomForestClassifier(n_estimators=100, n_jobs=-1, criterion='entropy')
    models['rfc50'] = RandomForestClassifier(n_estimators=50, n_jobs=-1, criterion='entropy')
    models['rfc10_gini'] = RandomForestClassifier(n_estimators=10, n_jobs=-1, criterion='gini')
    models['rfc100_gini'] = RandomForestClassifier(n_estimators=100, n_jobs=-1, criterion='gini')
    models['etc10'] = ExtraTreesClassifier(n_estimators=10)
    models['etc100'] = ExtraTreesClassifier(n_estimators=100)
    models['gnb'] = GaussianNB()
    models['bnb'] = BernoulliNB()
    models['sgd'] = SGDClassifier()
    models['rdg'] = RidgeClassifier(alpha=1)
    models['gbc10'] = GradientBoostingClassifier(n_estimators=10)
    models['gbc50'] = GradientBoostingClassifier(n_estimators=50)
    models['dtc'] = DecisionTreeClassifier(criterion='entropy')
    models['abc_rfc10'] = AdaBoostClassifier(base_estimator=models['rfc10'])
    models['abc_rfc100'] = AdaBoostClassifier(base_estimator=models['rfc100'])
    models['abc_rfc50'] = AdaBoostClassifier(base_estimator=models['rfc50'])
    models['abc_etc10'] = AdaBoostClassifier(base_estimator=models['etc10'])
    models['abc_etc100'] = AdaBoostClassifier(base_estimator=models['etc100'])
    models['abc_gbc10'] = AdaBoostClassifier(base_estimator=models['gbc10'])
    models['abc_gbc50'] = AdaBoostClassifier(base_estimator=models['gbc50'])
    steps = [('pca', PCA(n_components='mle', whiten=True)), ('clf', models['rfc10'])]
    models['pca_rfc10'] = Pipeline(steps=steps)
    steps = [('pca', PCA(n_components='mle', whiten=True)), ('clf', models['rfc100'])]
    models['pca_rfc100'] = Pipeline(steps=steps)
    steps = [('pca', PCA(n_components='mle', whiten=True)), ('clf', models['knc'])]
    models['pca_knc'] = Pipeline(steps=steps)
    steps = [('pca', PCA(n_components='mle', whiten=True)), ('clf', models['svc'])]
    models['pca_svc'] = Pipeline(steps=steps)
    steps = [('lda', LDA()), ('clf', models['rfc10'])]
    models['lda_rfc10'] = Pipeline(steps=steps)
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
