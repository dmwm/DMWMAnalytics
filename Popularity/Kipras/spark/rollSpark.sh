#!/bin/bash

train_start=20160526
train_end=20160601
valid_end=20160727

classifiers="RandomForestClassifier,DecisionTreeClassifier,GBTClassifier"

drops="naccess,campain,creation_date,tier_name,dataset_access_type,dataset_id,energy,flown_with,idataset,last_modification_date,last_modified_by,mcmevts,mcmpid,mcmtype,nseq,pdataset,physics_group_name,prep_id,primary_ds_name,primary_ds_type,processed_ds_name,processing_version,pwg,this_dataset,rnaccess,rnusers,rtotcpu,s_0,s_1,s_2,s_3,s_4,totcpu,wct,cpu,xtcrosssection"

PYSPARK_PYTHON='/afs/cern.ch/user/v/valya/public/python27' \
         spark-submit \
         --jars spark-csv_2.11-1.4.0.jar,commons-csv-1.4.jar \
         --master yarn-client \
         --executor-memory 2g \
         --driver-class-path '/usr/lib/hive/lib/*' \
         --driver-java-options '-Dspark.executor.extraClassPath=/usr/lib/hive/lib/*' \
         pyspark_ml.py --clf $classifiers --tstart $train_start --tend $train_end --vend $valid_end --drops $drops

