#!/bin/bash
# Author: V. Kuznetsov
# Example script how to tests several models from DCAFPilot learners
# as well as VW/xgboost ones. It runs over provided train/validation
# files

if [ $# -eq 2 ]; then
    train=$1
    valid=$2
    xgconf=""
elif [ $# -eq 3 ]; then
    train=$1
    valid=$2
    xgconf=$3
else
    echo "Usage: test_models.sh <train> <valid> <xgconf>"
    exit 1
fi

scorers="accuracy,precision,recall,f1"
run_alg()
{
for alg in "RandomForestClassifier" "SGDClassifier" "LinearSVC"; do
    echo ""
    echo "##### TEST $alg for $1/$2 #####"
    if [ -f pred.txt ]; then
        rm pred.txt
    fi
    model --learner=$alg --idcol=id --target=target --scaler=StandardScaler \
        --predict=pred.txt --train-file=$1 --newdata=$2 --split=0
    echo "All data scorers"
    check_prediction --fin=$2 --fpred=pred.txt --scorer=$scorers
    echo "New data scorers"
    new_datasets --fine=$1 --fnew=$2 --fout=ndd.csv.gz
    slice_data --pred=pred.txt --data=$2 --ids=ndd.csv.gz
    check_prediction --fin=new_data.txt --fpred=new_pred.txt --scorer=$scorers
done
}
run_vw()
{
    echo "##### TEST VW for $1/$2 #####"
    if [ -f pred.txt ]; then
        rm pred.txt
    fi
    runvw $1 $2
    new_datasets --fin=$1 --fnew=$2 --fout=ndd.csv.gz
    slice_data --pred=vwpreds.csv --data=$2 --ids=ndd.csv.gz
    echo "New data scorers"
    check_prediction --fin=new_data.txt --fpred=new_pred.txt --scorer=accuracy,precision,recall,f1
}
run_xgb()
{
    echo "##### TEST xgboost for $1/$2 #####"
    if [ -f pred.txt ]; then
        rm pred.txt
    fi
    runxgboost $1 $2 $3
    new_datasets --fin=$1 --fnew=$2 --fout=ndd.csv.gz
    slice_data --pred=xgpreds.csv --data=$2 --ids=ndd.csv.gz
    echo "New data scorers"
    check_prediction --fin=new_data.txt --fpred=new_pred.txt --scorer=accuracy,precision,recall,f1
}

run_alg $train $valid
run_vw $train $valid
run_xgb $train $valid $xgconf
