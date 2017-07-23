#!/bin/sh
# Author: Kipras Kancys <kipras [DOT] kan AT gmail [DOT] com>
# A script to move data to HDFS, submit a spark job and retrieve results

pyscript=pyspark_ml.py

clf=$1      # classifier
ftrain=$2   # train data file
fvalid=$3   # valid data file
foutput=$4  # output file
ftime=$5    # time file

if $(hadoop fs -test -f $ftrain); then
    echo "Train data file already exist on HDFS DFS"
else 
    hdfs dfs -copyFromLocal $ftrain $ftrain
    echo "Train data file was copied to HDFS DFS"; 
fi 

if $(hadoop fs -test -f $fvalid); then
    echo "Validation data file already exist on HDFS DFS"
else
    hdfs dfs -copyFromLocal $fvalid $fvalid
    echo "Validation data file was copied to HDFS DFS";
fi

PYSPARK_PYTHON='/afs/cern.ch/user/v/valya/public/python27' \
    spark-submit \
        --master yarn-client \
        --executor-memory 2g \
        --driver-class-path '/usr/lib/hive/lib/*' \
        --driver-java-options '-Dspark.executor.extraClassPath=/usr/lib/hive/lib/*' \
        $pyscript --clf $clf --train=$ftrain --valid=$fvalid

# get files from HDFS
hdfs dfs -copyToLocal output .
hdfs dfs -copyToLocal timing .

hdfs dfs -rm -R output
hdfs dfs -rm -R timing
hdfs dfs -rm $ftrain
hdfs dfs -rm $fvalid

# write results to output file
echo "dataset,prediction" > $foutput #header
find ./output -name 'part*' | while read line; do cat "$line" >> $foutput; done
rm -rf output

# write time result to time file
find ./timing -name 'part*' | while read line; do cat "$line" >> $ftime; done
rm -rf timing

