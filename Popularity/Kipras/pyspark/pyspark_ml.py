#!/usr/bin/env python

# File       : pyspark_ml.py
# Author     : Kipras Kancys <kipras [DOT] kan  AT gmail [dot] com>
# Description: pysmark model

# system modules
import time
import argparse

# pyspark modules
from pyspark import SparkContext
from pyspark.sql import SQLContext, Row
from pyspark.sql.types import StructType, StructField, LongType

from pyspark.ml import Pipeline
from pyspark.ml.feature import StringIndexer, VectorIndexer, Binarizer
from pyspark.ml.classification import RandomForestClassifier

from pyspark.ml.evaluation import MulticlassClassificationEvaluator

from pyspark.mllib.regression import LabeledPoint

class OptionParser():
    def __init__(self):
        "User based option parser"
        self.parser = argparse.ArgumentParser(prog='PROG', description=__doc__)
        self.parser.add_argument("--clf", action="store",
            dest="clf", default="", help="Classifier to use")
        self.parser.add_argument("--train", action="store",
            dest="ftrain", default="", help="Input train file")
        self.parser.add_argument("--valid", action="store",
            dest="fvalid", default="", help="Input validation file")
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

def prepData(sqlContext, ctx, fname):
    "Load, add label col and convert data into label and feature type dataframe (needed for MLlib)"

    lines = ctx.textFile(fname)
    parts = lines.map(lambda l: l.split(","))

    # to set col names:
    newColumns = parts.first()
    parts = parts.filter(lambda x:x !=newColumns)
    df = parts.toDF()
    oldColumns = df.schema.names
    df = reduce(lambda df, idx: df.withColumnRenamed(oldColumns[idx], newColumns[idx]), xrange(len(oldColumns)), df)

    # make labeled points, needed for algorithms to work
    temp = df.map(lambda row: LabeledPoint(row[-1], row[:-1]))
    temp = sqlContext.createDataFrame(temp, ['features','label'])

    return df,temp

def indexData(df):
    "Add index to dataframe, needed for joining columns"
    schema  = StructType(df.schema.fields[:] + [StructField("index", LongType(), False)])
    row_with_index = Row("row", "index")
    return (df.rdd.zipWithIndex()
        .map(lambda ri: row_with_index(*list(ri[0]) + [ri[1]]))
        .toDF(schema))

def toCSVLine(data):
    return ','.join(str(d) for d in data)

def RFC():
    return RandomForestClassifier(labelCol="indexed")

def model(classifier, ftrain, fvalid, fprediction):

    startTime = time.time()

    ctx = SparkContext(appName="model_on_Spark")
    sqlContext = SQLContext(ctx)
    logger = SparkLogger(ctx)
    logger.set_level('ERROR')

    # load and prepare training and validation data
    rawTrain, train = prepData(sqlContext, ctx, ftrain)
    rawValid, valid = prepData(sqlContext, ctx, fvalid)

    # is needed to join columns
    valid = indexData(valid)
    rawValid = indexData(rawValid)

    classifiers = {
        "RandomForestClassifier" : RFC
    }

    clf = classifiers[classifier]()

    labelIndexer = StringIndexer(inputCol="label", outputCol="indexed")
    featureIndexer = VectorIndexer(inputCol="features", outputCol="indexedFeatures")

    # train and predict
    pipeline = Pipeline(stages=[labelIndexer, featureIndexer, clf])
    model = pipeline.fit(train)

    predictions = model.transform(valid)

    # write to file:

    subsetPrediction = predictions.select("prediction", "index")
    subsetValidData = rawValid.select("dataset", "index")

    output = (subsetValidData
               .join(subsetPrediction, subsetPrediction.index == subsetValidData.index)
                    .drop("index")
                    .drop("index"))

    lines = output.map(toCSVLine)
    lines.saveAsTextFile('output')

    evaluator = MulticlassClassificationEvaluator(
       labelCol="label", predictionCol="prediction", metricName="precision")
    accuracy = evaluator.evaluate(predictions)
    print "Test Error = %g" % (1.0 - accuracy)

    executionTime = time.time() - startTime
    row=classifier+','+str(executionTime)
    ctx.parallelize([row]).saveAsTextFile("timing")

def main():
    "Main function"

    optmgr  = OptionParser()
    opts = optmgr.parser.parse_args()

    model(opts.clf, opts.ftrain, opts.fvalid, opts.fprediction)

if __name__ == '__main__':
    main()
