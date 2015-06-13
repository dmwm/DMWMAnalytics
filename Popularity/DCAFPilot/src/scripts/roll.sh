#!/bin/bash

# Script which roll over 2014 year on weekly basis and perform several operations:
# merge new week with core dataset (2013 data)
# transform it into classification problem
# run models
# get popdb data for given week
# verify predictions

odir=$PWD/wdir
drops="nusers,totcpu,rnaccess,rnusers,rtotcpu,nsites,s_0,s_1,s_2,s_3,s_4,wct"
opts="--target=naccess --target-thr=10 --drops=$drops"
opts="--target=naccess --target-thr='row[\"naccess\"]>=10 and row[\"nusers\"]>=3' --drops=$drops"
core=2013.csv.gz
merged=merged.csv.gz
merged_clf=merged_clf.csv.gz
valid_clf=valid.csv.gz
ddir=/afs/cern.ch/user/v/valya/workspace/analytics/data
XGBOOST_CONFIG=/data/analytics/etc/xgboost.conf
clf=RandomForestClassifier
clf=LinearSVC
clf=SGDClassifier
#clf=xgboost
#clf=vw

run() {
    echo $@
}

cmd="merge_csv --fin=$ddir/dataframe-2013*.csv.gz --fout=$merged"
run $cmd

if [ "$clf" == "xgboost" ]; then
    fname=`echo $merged_clf | cut -d'.' -f1`
    vname=`echo $valid_clf | cut -d'.' -f1`
    cmd="cat $XGBOOST_CONFIG | sed -e \"s,train_clf,$fname,g\" -e \"s,valid_clf,$vname,g\" > xgb.conf"
    run $cmd
fi

for fname in $ddir/dataframe-2014*.csv.gz;
do
    dates=`echo $fname | awk '{z=split($1,a,"-"); print a[2], a[3]}' | sed "s,.csv.gz,,g"`
    echo
    run "echo \"Run prediction for $dates\""
    popdb=`echo $dates | awk -F" " '{print "popdb-"$1"-"$2".txt"}'`
    cmd=`echo $dates | awk -F" " '{print "popular_datasets --start="$1" --stop="$2" > popdb-"$1"-"$2".txt"}'`
    run $cmd
    cmd="transform_csv --fin=$merged --fout=$merged_clf $opts"
    run $cmd
    cmd="transform_csv --fin=$fname --fout=$valid_clf $opts"
    run $cmd
    if [ "$clf" == "xgboost" ]; then
        cmd="runxgboost $merged_clf $valid_clf xgb.conf; /bin/cp -f xgpreds.csv pred.txt"
    elif [ "$clf" == "vw" ]; then
        cmd="runvw $merged_clf $valid_clf; /bin/cp -f vwpreds.csv pred.txt"
    else
        cmd="model --learner=$clf --idcol=id --target=target --scaler=StandardScaler --predict=pred.txt --train-file=$merged_clf --newdata=$valid_clf --split=0"
    fi
    run $cmd
    cmd="pred2dataset --fin=pred.txt --fout=${clf}.predicted"
    run $cmd
    cmd="verify_predictions --pred=${clf}.predicted --popdb=$popdb"
    run $cmd
    cmd="merge_csv --fin=$merged,$fname --fout=new_$merged; /bin/mv -f new_$merged $merged"
    run $cmd
done
