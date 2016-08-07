#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=

"""
Code to perform rolling prediction on SPARK
"""

__author__ = "Kipras Kancys"

import time
import argparse

from SPARK.utils.utils import get_file_names, get_start_date
from SPARK.utils.classifiers import get_classifier

from pyspark import SparkContext
from pyspark.sql import SQLContext

from pyspark.mllib.regression import LabeledPoint
from pyspark.mllib.evaluation import BinaryClassificationMetrics
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.classification import DecisionTreeClassifier
from pyspark.ml.classification import GBTClassifier
from pyspark.ml import Pipeline
from pyspark.ml.feature import Binarizer, StringIndexer, VectorIndexer

valid_step_days=7

class OptionParser():
    def __init__(self):
        "User based option parser"
        self.parser = argparse.ArgumentParser(prog='PROG', description=__doc__)
        self.parser.add_argument("--clf", action="store",
            dest="clf", default="RandomForestClassifier", help="Classifier to use")
        self.parser.add_argument("--tstart", action="store",
            dest="train_start", default="", help="Training start date")
        self.parser.add_argument("--tend", action="store",
            dest="train_end", default="", help="Training end date")
        self.parser.add_argument("--vend", action="store",
            dest="valid_end", default="", help="Validation end date")
        self.parser.add_argument("--drops", action="store",
            dest="drops", default="", help="Columns to drop")
        self.parser.add_argument("--prediction", action="store",
            dest="fprediction", default="output.txt", help="Output file for predictions")

class SparkLogger(object):
    "Control Spark Logger"
    def __init__(self, ctx):
        self.logger = ctx._jvm.org.apache.log4j
        self.rlogger = self.logger.LogManager.getRootLogger()

    def set_level(self, level):
        "Set Spark Logger level"
        self.rlogger.setLevel(getattr(self.logger.Level, level))

    def lprint(self, stream, msg):
        "Print message via Spark Logger to given stream"
        getattr(self.rlogger, stream)(msg)

    def info(self, msg):
        "Print message via Spark Logger to info stream"
        self.lprint('info', msg)

    def error(self, msg):
        "Print message via Spark Logger to error stream"
        self.lprint('error', msg)

    def warning(self, msg):
        "Print message via Spark Logger to warning stream"
        self.lprint('warning', msg)

def label_data(data): return data.map(lambda row: LabeledPoint(row[-1], row[:-1]))

def load_data(sqlContext, sc, tfiles, vfile):
    "Loads and makes data of the same structure"
    columns = get_mutual_columns(sc, tfiles +[vfile])

    valid_data = sqlContext.read.format('com.databricks.spark.csv') \
            .options(header='true', inferschema='true') \
            .load(vfile)

    valid_data = valid_data.select(columns)

    train_data = sqlContext.read.format('com.databricks.spark.csv').options(header='true', inferschema='true').load(tfiles[0])
    train_data = train_data.select(columns)

    for ffile in tfiles[1:]:
        temp = sqlContext.read.format('com.databricks.spark.csv').options(header='true', inferschema='true').load(ffile)
        temp = temp.select(columns)
        train_data = train_data.unionAll(temp)

    return valid_data, train_data

def prep_data(sqlContext, data, drops):
    """Prepares date for ML. Preparation includes: making a label column (by the rule: naacess > 10),
	applying drops and transforming data into LabeledPoint"""

    binarizer = Binarizer(threshold=10.0, inputCol="naccess", outputCol="target")
    data = binarizer.transform(data)

    drops = drops.split(",")
    cols = [x for x in data.columns if x not in set(drops)]

    data = data.select(cols)

    labeled = label_data(data)
    preped_data = sqlContext.createDataFrame(labeled, ['features','label'])

    return preped_data

def model(classifiers, training, testing, week):

    results = ""
    timing = []

    for classifier in classifiers:

        timeStart = time.time()

        clf = get_classifier(classifier)

        labelIndexer = StringIndexer(inputCol="label", outputCol="indexed")
        featureIndexer = VectorIndexer(inputCol="features", outputCol="indexedFeatures")

        pipeline = Pipeline(stages=[labelIndexer, featureIndexer, clf])
        model = pipeline.fit(training)

        prediction = model.transform(testing)

        metrics = BinaryClassificationMetrics(prediction.select("label","prediction").rdd)

        results = results + "new," + classifier + "," + week + "," + str(metrics.areaUnderROC) + "," +str(metrics.areaUnderPR) + "\n"

        timing.append(time.time()-timeStart)

    return results, timing

def get_mutual_columns(sc, files):
    "Collects headers of all files and keeps the ones that exist in all dataframes"
    f1 = sc.textFile(files[0])
    columns = sc.parallelize(f1.first().split(","))
    for file in files[1:]:
        f2 = sc.textFile(file)
        f2columns = sc.parallelize(f2.first().split(","))
        columns = columns.intersection(f2columns)

    return columns.collect()

def main():
    "Main function"

    sc = SparkContext(appName="model_on_Spark")
    sqlContext = SQLContext(sc)
    logger = SparkLogger(sc)
    logger.set_level('ERROR')

    optmgr  = OptionParser()
    opts = optmgr.parser.parse_args()

    valid_start = get_start_date(opts.train_end)
    validFiles = get_file_names(valid_start, opts.valid_end, valid_step_days)

    clf = opts.clf.split(",")
    train_end = opts.train_end

    timing = []

    for i in range(0, len(clf)):
        timing.append(0)

    results = "dftype,clf,date,areaUnderROC,areaUnderPR\n"
    time = "model,running_time_s\n"

    for week in validFiles:

        weekString = week.split("-")[1]

        print("Validation file " + week)
        trainFiles = get_file_names(opts.train_start, train_end, valid_step_days)
        print("Training files: " + trainFiles[0] + ":" + trainFiles[-1])
        train_data, valid_data = load_data(sqlContext, sc, trainFiles, week)
        training = prep_data(sqlContext, train_data, opts.drops)
        validating = prep_data(sqlContext, valid_data, opts.drops)

        resultsTemp, timeTemp = model(clf, training, validating, weekString)

        results = results + resultsTemp

        for i in range(0, len(clf)):
            timing[i] += timeTemp[i]

        train_end = get_start_date(week.split("-")[2].split(".csv")[0])

    iterator = 0

    for classifier in clf:
        time = time + str(classifier) + "," + str(timing[iterator]) + "\n"
        iterator += 1

    text_file = open("results.csv", "w")
    text_file.write(results)
    text_file.close()

    text_file = open("model_running.csv", "w")
    text_file.write(time)
    text_file.close()

if __name__ == '__main__':
    main()
