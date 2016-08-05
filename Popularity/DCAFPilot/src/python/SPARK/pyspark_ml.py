#!/usr/bin/env python

# File       : pyspark_ml.py
# Author     : Kipras Kancys <kipras [DOT] kan  AT gmail [dot] com>
# Description: pyspark model

import time
import argparse

from SPARK.utils.utils import getTrainDataFileNames, getStartDate
from SPARK.utils.classifiers import getClassifier

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

def labelData(data): return data.map(lambda row: LabeledPoint(row[-1], row[:-1]))

def loadAndPrepData(sqlContext, sc, tfiles, vfile, drops):

    columns = getMutualColumns(sc, tfiles +[vfile])

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

    binarizer = Binarizer(threshold=10.0, inputCol="naccess", outputCol="target")

    train_data = binarizer.transform(train_data)
    valid_data = binarizer.transform(valid_data)

    drops = drops.split(",")
    cols = [x for x in train_data.columns if x not in set(drops)]

    train_data = train_data.select(cols)
    valid_data = valid_data.select(cols)

    trLabeled = labelData(train_data)
    training = sqlContext.createDataFrame(trLabeled, ['features','label'])

    tsLabeled = labelData(valid_data)
    testing = sqlContext.createDataFrame(tsLabeled, ['features','label'])

    return training, testing

def model(classifiers, training, testing, week):

    results = ""
    timing = []

    for classifier in classifiers:

        timeStart = time.time()

        clf = getClassifier(classifier)

        labelIndexer = StringIndexer(inputCol="label", outputCol="indexed")
        featureIndexer = VectorIndexer(inputCol="features", outputCol="indexedFeatures")

        pipeline = Pipeline(stages=[labelIndexer, featureIndexer, clf])
        model = pipeline.fit(training)

        prediction = model.transform(testing)

        metrics = BinaryClassificationMetrics(prediction.select("label","prediction").rdd)

        results = results + "new," + classifier + "," + week + "," + str(metrics.areaUnderROC) + "," +str(metrics.areaUnderPR) + "\n"

        timing.append(time.time()-timeStart)

    return results, timing

def getMutualColumns(sc, files):
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

    valid_start = getStartDate(opts.train_end)
    filesValid = getTrainDataFileNames(valid_start, opts.valid_end, valid_step_days, False)

    clf = opts.clf.split(",")
    train_end = opts.train_end

    timing = []

    for i in range(0, len(clf)):
        timing.append(0)

    results = "dftype,clf,date,areaUnderROC,areaUnderPR\n"
    time = "model,running_time_s\n"

    for week in filesValid:

        weekString = week.split("-")[1]

        print("Validation file " + week)
        filesTrain = getTrainDataFileNames(opts.train_start, train_end, valid_step_days, False)
        print("Training files: " + filesTrain[0] + ":" + filesTrain[-1] )

        training, testing = loadAndPrepData(sqlContext, sc, filesTrain, week, opts.drops)
        resultsTemp, timeTemp = model(clf, training, testing, weekString)

        results = results + resultsTemp

        for i in range(0, len(clf)):
            timing[i] += timeTemp[i]

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
