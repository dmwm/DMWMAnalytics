#!/bin/bash
# Script to generate full dataset out of provided dataframes
# and run the model over this dataset
# The cronjob should be run as following (an example with /data/analytics area):
# 0 1 * * * cron4models.sh /data/analytics /data/analytics/data/train

if [ $# -eq 2 ]; then
    wdir=$1
    ddir=$2
else
    echo "Usage: cron4models.sh <workdir> <train set, e.g. data/train or data/train/2014*.csv>"
    exit 1
fi
cd $wdir

# VK, no need for MongoDB seed anymore since we'll use Go dataframes
# seed MongoDB with fresh snapshot of DBS datasets
# dataframe --seed-cache --verbose=1

echo "Workdir $wdir"
# generic naming conventions
train=train.csv.gz
train_clf=train_clf.csv.gz

# drops used for old data (generated via python dataframe)
# drops="nusers,totcpu,rnaccess,rnusers,rtotcpu,nsites,s_0,s_1,s_2,s_3,s_4,wct"

# drops used with new data (generated via Go version of dataframe)
drops="campain,creation_date,tier_name,dataset_access_type,dataset_id,energy,flown_with,idataset,last_modification_date,last_modified_by,mcmevts,mcmpid,mcmtype,nseq,pdataset,physics_group_name,prep_id,primary_ds_name,primary_ds_type,processed_ds_name,processing_version,pwg,this_dataset,rnaccess,rnusers,rtotcpu,s_0,s_1,s_2,s_3,s_4,totcpu,wct,cpu,xtcrosssection"

target=naccess
thr=10
# or we may use complex target
# target=naccess
# thr="row['naccess']>10 and row['nsites']<50"

# find out last date
today=`date +%Y%m%d`
if [ -n "`ls $ddir | grep csv`" ]; then
    last_file=`ls $ddir/*.csv | sort -n | tail -1`
    last_date=`echo $last_file | awk '{z=split($1,a,"/"); split(a[z],b,"."); n=split(b[1],c,"-"); print c[n]}'`
else
    last_date=""
    echo "No data files found in $ddir, exit"
    exit 0
fi
today=`date +%Y%m%d`

if [ -n "$last_date" ]; then
    start_day=`newdate --date=$last_date`
else
    start_day=$today
fi

# merge data
echo "Workdir: $PWD"
echo "merge_csv --fin=$ddir --fout=$train"
merge_csv --fin=$ddir --fout=$train --verbose

# generate new data
newtstamps="$start_day-$today"
new=new-$newtstamps.csv
echo "WORKDIR: $PWD"
echo "New data: $new"
echo "dataframe2go -start=$start_day -stop=$today -newdata -fout=$new"
dataframe2go -start=$start_day -stop=$today -newdata -fout=$new

# gzip new data since dataframe2go does not perform gzip
gzip $new
new=new-$newtstamps.csv.gz

# find common set of drop headers
drops=`find_drops --file1=$new --file2=$train --drops=$drops`
echo "Drop attributes: $drops"

# transform the data
echo "transform_csv --fin=$train --fout=$train_clf --target=naccess --target-thr=$thr --drops=$drops"
transform_csv --fin=$train --fout=$train_clf --target=naccess --target-thr=$thr --drops=$drops
echo "$wdir/$train_clf"
zcat $train_clf | head -1

# transform the newdata
newdata=newdata-$newtstamps.csv.gz
echo "transform_csv --fin=$new --fout=$newdata --target=naccess --target-thr=$thr --drops=$drops"
transform_csv --fin=$new --fout=$newdata --target=naccess --target-thr=$thr --drops=$drops
echo "$wdir/$newdata"
zcat $newdata | head -1

# run models via run_models script
echo "run_models $train_clf $newdata predict"
run_models $train_clf $newdata predict $ddir/datasets.txt.gz

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
