#!/bin/bash
# Script to generate full dataset out of provided dataframes
# and run the model over this dataset
# The cronjob should be run as following (an example with /data/analytics area):
# 0 1 * * * cron4verify.sh /data/analytics/data/predictions

if [ $# -eq 1 ]; then
    wdir=$1
else
    echo "Usage: cron4verify.sh <prediction area>"
    exit 1
fi
cd $wdir

# loop over prediction dirs
# scan if prediction dir has verify prediction file
# if yes, skip it, if no get popDB data for that time-frame and run verify prediction script
for vdir in `ls`; do
    if [ ! -f $vdir/popdb.verification ]; then
        cd $vdir
        start_day=`echo $vdir | awk -F- '{print $1}'`
        stop_day=`echo $vdir | awk -F- '{print $2}'`
        pname=popdb-$start_day-$stop_day.txt
        popular_datasets --start=$start_day --stop=$stop_day > $pname
        for fname in `ls *.predicted`; do
            bname=`echo $fname | awk -F. '{print $1}'`
            verify_predictions --pred=$fname --popdb=$pname --verbose=1 > $bname.verification
        done
        touch popdb.verification
        cd -
    fi
done
