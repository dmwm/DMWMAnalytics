#!/bin/bash
# Script to generate full dataset out of provided dataframes
# and run the model over this dataset
# The cronjob should be run as following (an example with /data/analytics area):
# 0 1 * * * cron4models.sh /data/analytics /data/analytics/data/train

if [ $# -eq 2 ]; then
    wdir=$1
    ddir=$2
else
    echo "Usage: cron4models.sh <workdir> <train set, e.g. data/train or data/train/2014*.csv.gz>"
    exit 1
fi
cd $wdir
# generic naming conventions
train=train.csv.gz
train_clf=train_clf.csv.gz

# model parameters, subject to change over time
drops="nusers,totcpu,rnaccess,rnusers,rtotcpu,nsites,s_0,s_1,s_2,s_3,s_4,wct"
target=naccess
thr=10
# or we may use complex target
# target=naccess
# thr="row['naccess']>10 and row['nsites']<50"

# find out last date
today=`date +%Y%m%d`
if [ -n "`ls $ddir | grep csv.gz`" ]; then
    last_file=`ls $ddir/*.csv.gz | sort -n | tail -1`
    last_date=`echo $last_file | awk '{z=split($1,a,"/"); split(a[z],b,"."); n=split(b[1],c,"-"); print c[n]}'`
else
    last_date=""
fi
today=`date +%Y%m%d`

if [ -n "$last_date" ]; then
    start_day=`newdate --date=$last_date`
else
    start_day=$today
fi

# merge data
echo "merge_csv --fin=$ddir --fout=$train"
merge_csv --fin=$ddir --fout=$train --verbose

# transform the data
echo "transform_csv --fin=$train --fout=$train_clf --target=naccess --target-thr=$thr --drops=$drops"
transform_csv --fin=$train --fout=$train_clf --target=naccess --target-thr=$thr --drops=$drops

# generate new data
newtstamps="$start_day-$today"
new=new-$newtstamps.csv.gz
newdata=newdata-$newtstamps.csv.gz
echo "New data: $new"
echo "dataframe --start=$start_day --stop=$today --newdata --fout=$new"
dataframe --start=$start_day --stop=$today --newdata --fout=$new

# transform the newdata
echo "transform_csv --fin=$new --fout=$newdata --target=naccess --target-thr=$thr --drops=$drops"
transform_csv --fin=$new --fout=$newdata --target=naccess --target-thr=$thr --drops=$drops

# run models via run_models script
echo "run_models $train_clf $newdata predict"
run_models $train_clf $newdata predict

# final touch
echo
echo "### Prediction files:"
ls -la *.predicted

# move files in place
if [ -n "$DCAFPILOT_PREDICTIONS" ] && [ -d $DCAFPILOT_PREDICTIONS ]; then
    mkdir -p $DCAFPILOT_PREDICTIONS/$newtstamps
    /bin/mv -f *.predicted $DCAFPILOT_PREDICTIONS/$newtstamps
fi

# clean-up
rm $train $train_clf $new $newdata
rm *.libsvm* *.vw* pred.txt vwpreds* xgpreds* *.ids *.model
