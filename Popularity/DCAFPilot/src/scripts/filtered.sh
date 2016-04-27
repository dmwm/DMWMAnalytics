#!/bin/bash

# date        : 2016 03 04
# author      : Mantas Briliauskas < m dot briliauskas eta gmail dot com >
# description :
#   perform prediction using three cases and provide results
#   case 1 : train model using full dataframe, predict using full dataframe
#   case 2 : train model using full dataframe, predict filtered data
#   case 3 : train model using filtered data, predict filtered data
#   filter : set by tiers in 'tiers' variable

# main script settings
use_log=0
output_tiers=0      # split results by tiers or not
use_ensemble=0

# dataframe selection options
old_path=/data/srv/state/dcafpilot/analytics/old_data
new_path=/data/srv/state/dcafpilot/analytics/data
train_start=20150101
train_end=20151231
valid_start=20160101
valid_end=20160120

# other script settings
data=("old" "new")
drops="nusers,totcpu,rnaccess,rnusers,rtotcpu,nsites,s_0,s_1,s_2,s_3,s_4,wct"
scorer="tp,tn,fp,fn,tpr,tnr,fpr,fnr"
tiers="AOD,AODSIM,MINIAOD,MINIAODSIM,USER"
#classifiers=("AdaBoostClassifier" "BaggingClassifier" "DecisionTreeClassifier" "ExtraTreesClassifier" "GradientBoostingClassifier" "XGBClassifier")
classifiers=("XGBClassifier")

running_time_data="model_running.csv"

# prepares dataframes for prediction
prepare_data() {
    # prepare_data {old,new}
    pref=$1
    echo "[$pref] Preparing data..."
    dol='$'
    path=`eval "echo \"${dol}${pref}_path\""`
    tfiles=`get_file_list $path $train_start $train_end`
    vfiles=`get_file_list $path $valid_start $valid_end`
    #echo "$pref training files   : $tfiles"
    echo "$pref validation files : $vfiles"    
    merge_csv --fin=$tfiles --fout=${pref}_train.csv.gz
    merge_csv --fin=$vfiles --fout=${pref}_valid.csv.gz
    __drops=`find_drops --file1=${pref}_train.csv.gz --file2=${pref}_valid.csv.gz --drops=$drops`
    logstr=""; if [ $use_log -eq 1 ]; then logstr="--log-thr=100000"; fi
    transform_csv --fin=${pref}_train.csv.gz --fout=${pref}_train_clf.csv.gz --target=naccess --target-thr=10 --drops=$__drops $logstr
    transform_csv --fin=${pref}_valid.csv.gz --fout=${pref}_valid_clf.csv.gz --target=naccess --target-thr=10 --drops=$__drops $logstr
    verify_csv $pref
}

# extracts data by selected tiers and forms new dataframe
run_parse_csv(){
    # run_parse_csv {old,new} fin fout
    pref=$1; fin=$2; fout=$3
    mkeyval=""
    echo "[$pref] Extracting data $fin -> $fout..."
    if   [ "$pref" == "old" ]; then mkeyval="id,tier"
    elif [ "$pref" == "new" ]; then mkeyval="hash,tier"; fi
    parse_csv --fin=$fin --fout=$fout --tiers=$tiers --tiers-col=tier --mapping=${pref}_tiers.txt --mapping-kval=$mkeyval
}

# predicts, verifies the prediction and stores the result
predict_and_verify() {
    # predict_and_measure {old,new} classifier train_file valid_file tag
    pref=$1; clf=$2; ftrain=$3; fvalid=$4; tag=$5
    kval=""
    if   [ "$pref" == "old" ]; then kval="id,tier"
    elif [ "$pref" == "new" ]; then kval="hash,tier"
    else echo "Error: unrecognized prefix $pref"; exit 1; fi
    echo "[$pref] Predicting $tag data..."
    model --learner=$clf --idcol=id --target=target --train-file=$ftrain --newdata=$fvalid --predict="${pref}_${tag}_${clf}.txt" --split=0 --timeout=$running_time_data
    tiersstr=""; if [[ $output_tiers == 1 ]]; then tiersstr="--tiers-break --tiers-map=${pref}_tiers.txt --tiers-map-kval=$kval --plain-output"; fi
    check_prediction --fin=$fvalid --fpred="${pref}_${tag}_${clf}.txt" --scorer=$scorer $tiersstr > "${pref}_${tag}_${clf}.pred"
    # ensembler uses predictions
    #rm "${pref}_${tag}_${clf}.txt"
}

# checks correctness of formed dataframes
verify_csv() {
    # verify_csv {old,new}
    pref=$1
    if [ ! $use_log -eq 1 ]; then
        # verify_dfr checks column statistics if data was transformed correnctly
        verify_dfr --file1=${pref}_train.csv.gz --file2=${pref}_train_clf.csv.gz --drops=$drops
        verify_dfr --file1=${pref}_valid.csv.gz --file2=${pref}_valid_clf.csv.gz --drops=$drops
    fi
    hdiff=`headers_diff ${pref}_train_clf.csv.gz ${pref}_valid_clf.csv.gz`
    if [ ! "${#hdiff}" -le 0 ]; then
        endl=$'\n'
        echo "[$pref] Error: different number of attributes. Difference:$endl$hdiff"
        exit 1
    fi
}

# creates ensemble of predictions, verifies, and stores the result
ensemble_and_verify() {
    # ensemble_and_check (old|new) tag validation_file
    pref=$1; tag=$2; fvalid=$3
    if [ ${#classifiers[@]} -lt 2 ]; then
        echo "ERROR in ensemble_and_verify(): cannot ensemble 1 file"
        exit 1
    fi
    kval=""
    if   [ "$pref" == "old" ]; then kval="id,tier"
    elif [ "$pref" == "new" ]; then kval="hash,tier"
    else echo "Error: unrecognized prefix $pref"; exit 1; fi
    ensemble_predictions --fbeg="${pref}_${tag}_" --fout="${pref}_${tag}_Ensemble.txt"
    tiersstr=""; if [ $output_tiers -eq 1 ]; then tiersstr="--tiers-break --tiers-map=${pref}_tiers.txt --tiers-map-kval=$kval --plain-output"; fi
    check_prediction --fin=$fvalid --fpred="${pref}_${tag}_Ensemble.txt" --scorer=$scorer $tiersstr > "${pref}_${tag}_Ensemble.pred"
}

# produces a list of dataframes to work with
get_file_list() {
    # running 10-30 secs because of constant python execution
    if [ $# -ne 3 ]; then echo "ERROR in get_file_list()"; exit 1; fi
    path=$1
    start_date=$2
    end_date=$3
    files=""
    for f in `ls $path | egrep "\.csv\.gz$"`; do
        st=`echo $f | awk '{z=split($1,a,"/"); split(a[z],b,"."); n=split(b[1],c,"-"); print c[n-1]}'`
        en=`echo $f | awk '{z=split($1,a,"/"); split(a[z],b,"."); n=split(b[1],c,"-"); print c[n]}'`
        diff_st=`python -c "print $st-$start_date"`
        diff_en=`python -c "print $end_date-$en"`
        if [ $diff_st -ge 0 -a $diff_en -ge 0 ]; then
            files="$path/$f,$files"
        fi       
    done
    echo ${files::${#files}-1}
}

###

# removes old running time records
rm $running_time_data

# main block
for d in "${data[@]}"; do
    prepare_data $d
    run_parse_csv $d "${d}_train_clf.csv.gz" "${d}_train_dfr.csv.gz"
    run_parse_csv $d "${d}_valid_clf.csv.gz" "${d}_valid_dfr.csv.gz"
    #shuffle_csv --fin="${d}_valid_clf.csv.gz"
    #shuffle_csv --fin="${d}_valid_dfr.csv.gz"
    for classifier in "${classifiers[@]}"; do
        predict_and_verify $d $classifier "${d}_train_clf.csv.gz" "${d}_valid_clf.csv.gz" normal
        predict_and_verify $d $classifier "${d}_train_clf.csv.gz" "${d}_valid_dfr.csv.gz" valid_data_-_only_selected_tiers
        predict_and_verify $d $classifier "${d}_train_dfr.csv.gz" "${d}_valid_dfr.csv.gz" train_and_valid_only_selected_tiers
    done
    if [ $use_ensemble -eq 1 ]; then
        ensemble_and_verify $d normal "${d}_valid_clf.csv.gz"
        ensemble_and_verify $d valid_data_-_only_selected_tiers "${d}_valid_dfr.csv.gz"
        ensemble_and_verify $d train_and_valid_only_selected_tiers "${d}_valid_dfr.csv.gz"
    fi
done
