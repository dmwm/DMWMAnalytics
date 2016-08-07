#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=

"""
Set of classifiers used in pyspark model
"""

__author__ = "Kipras Kancys"

from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.classification import DecisionTreeClassifier
from pyspark.ml.classification import GBTClassifier


def RFC():
     return RandomForestClassifier(labelCol="indexed")

def DTC():
    return DecisionTreeClassifier(labelCol="indexed")

def GBT():
    return GBTClassifier(labelCol="indexed")

def get_classifier(classifier):

    allClassifiers = {
         "RandomForestClassifier" : RFC,
         "DecisionTreeClassifier" : DTC,
         "GBTClassifier" : GBT
     }

    return allClassifiers[classifier]()
