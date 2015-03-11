#!/bin/bash
# script to copy files from one location to another
# useful for copying data from local area to AFS
# 0 1 * * * scp.sh host /data/analytics/data/predictions /afs/cern.ch/user/v/valya/workspace/analytics/predictions/

if [ $# -eq 3 ]; then
    host=$1
    wdir=$2
    ddir=$3
else
    echo "Usage: scp.sh <remote host> <source area at remote host> <local destination area>"
    exit 1
fi
# get list of files from remote host
rfiles=`ssh $USER@$host "ls $wdir"`
lfiles=`ls $ddir`
for fname in $rfiles; do
    ftest=`echo $lfiles | grep $fname`
    if [ -n "$ftest" ]; then
        echo "File $fname already at destination"
    else
        echo "scp -r $USER@$host:$wdir/$fname $ddir"
        scp -r $USER@$host:$wdir/* $ddir
    fi
done
