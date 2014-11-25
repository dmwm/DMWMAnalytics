#!/bin/bash
start=$1
if [ -z $start ]; then
    echo "Please specify input date"
    exit
fi
echo "#!/bin/bash"
echo "dataframe --update"
src/python/DCAF/tools/dates.py --start=$start \
    | awk '{print "nohup time dataframe --start="$1" --stop="$2" --dbs-extra=100 --verbose=1 --fout=dataframe-"$1"-"$2".csv 2>&1 1>& dataframe-"$1"-"$2".log < /dev/null &"}'

