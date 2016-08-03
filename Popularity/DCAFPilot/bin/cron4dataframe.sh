#!/bin/bash
# Script to generate dataframe generator script to be executed via cronjob
# The cronjob should be run as following (an example with /data/analytics area):
# 0 1 * * * cron4dataframe.sh /data/analytics/etc/dcaf.cfg /data/analytics /data/analytics/data/train

if [ $# -eq 3 ]; then
    cfg=$1
    wdir=$2
    ddir=$3
else
    echo "Usage: cron4dataframe.sh <DCAFPilot config file> <workdir> <data train area>"
    exit 1
fi
gfile=/tmp/gen_dataframes.sh
if [ -f $gfile ]; then
    rm -f $gfile
fi
mkdir -p $ddir/log
cd $wdir
dbsextra=10000
if [ -n "`ls $ddir | grep csv.gz`" ]; then
    last_file=`ls $ddir/*.csv.gz | sort -n | tail -1`
    last_date=`echo $last_file | awk '{z=split($1,a,"/"); split(a[z],b,"."); n=split(b[1],c,"-"); print c[n]}'`
else
    # get a date from a past such that we'll step one day from it and still have a week
    # i.e. we need to get a 9 days back timestamp. On Linux we can use GNU date
    #    last_date=`date --date="9 days ago" +%Y%m%d`
    # but it does not work on OSX, instead we'll use perl
    last_date=`perl -MPOSIX=strftime -le 'print strftime("%Y%m%d", localtime(time-9*86400))'`
fi
today=`date +%Y%m%d`

if [ -n "$last_date" ]; then
    start_day=`newdate --date=$last_date`
else
    start_day=$today
fi

diff=`python -c "print $today-$start_day"`
if [ $diff -le 7 ]; then
    echo "Period less than a week, no more work, go sleep"
    exit 0
fi
# write generator script
echo "#!/bin/bash" > $gfile
#echo "dataframe --config=$cfg --seed-cache --verbose=1" >> $gfile
echo "mkdir -p $ddir/log" >> $gfile
# previous way to generate dataframes, via python dataframe
#dates --start=$start_day | awk \
#'{print "nohup dataframe --config="CFG" --verbose=1 --start="$1" --stop="$2" --dbs-extra="DBSEXTRA" --fout="DDIR"/dataframe-"$1"-"$2".csv.gz 2>&1 1>& "DDIR"/log/dataframe-"$1"-"$2".log < /dev/null &"}' \
#DDIR=$ddir CFG=$cfg DBSEXTRA=$dbsextra >> $gfile
# new way to generate dataframes, via Go implementation of dataframe
dates --start=$start_day | awk \
'{print "nohup dataframe2go --verbose=1 --start="$1" --stop="$2" --dbs-extra="DBSEXTRA" --fout="DDIR"/dataframe-"$1"-"$2".csv 2>&1 1>& "DDIR"/log/dataframe-"$1"-"$2".log < /dev/null &"}' \
DDIR=$ddir DBSEXTRA=$dbsextra >> $gfile
echo "ls $ddir/dataframe-*.csv | awk '{print \"gzip \"\$1\"\"}' | /bin/sh " >> $gfile

# change generator script permissions
chmod +x $gfile

# run generator script
$gfile
