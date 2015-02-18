#!/bin/bash
# Script to generate dataframe generator script to be executed via cronjob
# The cronjob should be run as following (an example with /data/analytics area):
# 0 1 * * * cron4dataframe.sh /data/analytics/etc/dcaf.cfg /data/analytics /data/analytics/data/train

if [ $# -eq 3 ]; then
    cfg=$1
    idir=$2
    data_dir=$3
else
    echo "Usage: cron4dataframe.sh <DCAFPilot config file> <location to run/write files> <location of data/train area>"
    exit 1
fi
gfile=/tmp/gen_dataframes.sh
cd $idir
dbsextra=10000
last_file=`ls $data_dir/*.csv.gz | sort -n | tail -1`
last_date=`echo $last_file | awk '{z=split($1,a,"/"); split(a[z],b,"."); n=split(b[1],c,"-"); print c[n]}'`
today=`date +%Y%m%d`

if [ -n $last_date ]; then
    start_day=$last_date
else
    start_day=$today
fi

# write generator script
echo "#!/bin/bash" > $gfile
echo "dataframe --clean-cache" >> $gfile
echo "dataframe --config=$cfg --seed-cache --verbose=1" >> $gfile
dates --start=$start_day | awk \
'{print "nohup dataframe --config="CFG" --verbose=1 --start="$1" --stop="$2" --dbs-extra="DBSEXTRA" --fout=dataframe-"$1"-"$2".csv.gz 2>&1 1>& dataframe-"$1"-"$2".log < /dev/null &"}' \
CFG=$cfg DBSEXTRA=$dbsextra >> $gfile
# change generator script permissions
chmod +x $gfile
# run generator script
$gfile
