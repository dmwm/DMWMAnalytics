#!/bin/bash
idir=$(basename $(dirname $0))
# input data file
dfile=data/train.vw
# model options, see vw --help
opts="--passes 40 -l 0.85 --loss_function quantile --quantile_tau 0.6"

#
### DO NOT MODIFY BELOW unless you know all scripts behavior
#

# file convention
tfile=/tmp/vw_train.vw  # splitted portion of train data
vfile=/tmp/vw_valid.vw  # splitted portion of validation data
lfile=/tmp/vw_label.vw  # validation labels
mfile=/tmp/vw_model.vw  # VW model file
pfile=/tmp/vw_preds.txt # VW prediction file
cfile=/tmp/vw_cross.csv # file with labels and predictions used for cross-validation analysis
ofile=/tmp/vw_cross.pdf # output ROC plots

# perform vw splitting for cross-validation
# it will produce /tmp/vw_train.vw /tmp/vw_valid.vw /tmp/vw_label.vw
echo "$idir/vw_split.py $dfile"
$idir/vw_split.py $dfile

# generate vw model
echo "vw $tfile -c -k -f $mfile $opts"
vw $tfile -c -k -f $mfile $opts

# generate vw predictions
echo "vw $vfile -t -i $mfile -p $pfile"
vw $vfile -t -i $mfile -p $pfile

# generate predictions csv file for analysis
echo "$idir/vw_preds.py $lfile $pfile $cfile"
$idir/vw_preds.py $lfile $pfile $cfile

# generate stats
echo "$idir/vw_cross.R --input=$cfile --output=$ofile"
$idir/vw_cross.R --input=$cfile --output=$ofile
echo "Wrote $ofile"
