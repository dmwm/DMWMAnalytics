#!/bin/bash
start=$1
dbsextra=10000
if [ -z $start ]; then
    echo "Usage: generate_scripts.sh YYYYMMDD <overlap (optional)>"
    exit
fi
overlap=""
if [ $# -eq 2 ] && [ "$2"=="overlap" ]; then
    overlap="--overlap"
fi
echo "#!/bin/bash"
echo "dataframe --seed-cache"
src/python/DCAF/tools/dates.py --start=$start $overlap \
    | awk '{print "nohup time dataframe --start="$1" --stop="$2" --dbs-extra="DBSEXTRA" --verbose=1 --fout=dataframe-"$1"-"$2".csv 2>&1 1>& dataframe-"$1"-"$2".log < /dev/null &"}' DBSEXTRA=$dbsextra
