#!/bin/bash

# date              : 2016 04 01
# author            : Mantas Briliauskas < m dot briliauskas eta gmail dot com >
# SPARK part author : Kipras Kancys < kipras dot kan eta gmail dot com >
# description       : prep data, perform rolling forecast on SPARK, record results and plot

# main script settings
use_log=0
use_ensemble=0
plot_result=1

# dataframe selection options

data=("old" "new")

old_path=/afs/cern.ch/user/v/valya/public/analytics/data_old
new_path=/afs/cern.ch/user/v/valya/public/analytics/data

# rolling forecast
train_start=20160526
train_end=20160601
train_max_trail_days=0      # length of training data, use 0 for fixed start date
valid_step_days=7           # iteration step length
valid_step_data_ext=5       # validation data extension to period starting[train_end+1]
                            #   ending [train_end+1+valid_step_days+valid_step_data_ext]
                            #   needed to catch the data within the period, default +5
valid_end=20160622          # stop date. use future date like 20200101 to run until data  

# other options
#classifiers=("XGBClassifier" "RandomForestClassifier" "SGDClassifier" "pca_rfc" "pca_sgd" "pca_xgb")
classifiers=("RandomForestClassifier")

drops="campain,creation_date,tier_name,dataset_access_type,dataset_id,energy,flown_with,idataset,last_modification_date,last_modified_by,mcmevts,mcmpid,mcmtype,nseq,pdataset,physics_group_name,prep_id,pwg,this_dataset,rnaccess,rnusers,rtotcpu,s_0,s_1,s_2,s_3,s_4,totcpu,wct,cpu,xtcrosssection,processed_ds_name,processing_version"

scorer="tpr,tnr"
plot_file="graph.png"
result_file="result_out.csv"
running_time_file="model_running.csv"

finished="no" # iteration indicator

# merges old or new data
merge_period_data() {
    # merge_period_data {old;new} date_start date_end file_out {train;valid}
    pref=$1; __train_start=$2; __train_end=$3; __fout=$4 __tag=$5
    dol='$'
    path=`eval "echo \"${dol}${pref}_path\""`
    files=`get_file_list $path $__train_start $__train_end`
    #echo "[$pref] $tag files: $files"
    merge_csv --fin=$files --fout=$__fout
}

# prepares iteration training data
prepare_train_data() {
    # prepare_train_data {old,new} date_train_end
    pref=$1; __train_end=$2
    dol='$'
    path=`eval "echo \"${dol}${pref}_path\""`
    if [ -f ${pref}_train.csv.gz ]; then
        if [ $train_max_trail_days -ne 0 ]; then
            __train_start=`newdate --date=$__train_end --step=-$train_max_trail_days`
            echo "[$pref] Merging training data... [$__train_start, $__train_end]"
            merge_period_data $pref $__train_start $__train_end ${pref}_train.csv.gz
        else
            echo "[$pref] Merging training and validation data..."
            tfiles="${pref}_train.csv.gz,${pref}_valid.csv.gz"
            merge_csv --fin=$tfiles --fout="_${pref}_train.csv.gz"
            mv "_${pref}_train.csv.gz" ${pref}_train.csv.gz
        fi
    else
        echo "[$pref] Merging init training data... ($train_start $__train_end)"
        merge_period_data $pref $train_start $train_end ${pref}_train.csv.gz
    fi
    # transformation performed after validation data is known
}

# returns difference between dates
dates_diff() {
    # dates_diff date1 date2
    ## ========
    ## test results: filter files from dir with 169 dataframe files
    ## python 15s (calc only diff of numbers) : `python -c "print $2-$1"`
    ## awk 2-3s (calc only diff of numbers)   : `awk "BEGIN {print $2-$1}"`
    ## perl 3s (calc only diff of numbers)    : `perl -e "${dol}d=$d2-$d1; print \"${dol}d\";"`
    ## perl/posix 9s (exact diff of dates)    : `perl -e "use Date::Parse; use POSIX; ${dol}d1=str2time(\"$d1\"); ${dol}d2=str2time(\"$d2\"); ${dol}d3=floor((${dol}d2-${dol}d1)/(24*60*60)); print \"${dol}d3\";"`   
    ## exact diff is not needed for now, enabling awk
    ######
    d1=$1; d2=$2
    dol='$'
    d=`awk "BEGIN {print $2-$1}"`
    echo "$d"
}

# produces a list of dataframes to work with
get_file_list() {
    # get_file_list data_path start_date end_date
    if [ $# -ne 3 ]; then echo "ERROR in get_file_list(). Given params: $@"; exit 1; fi
    path=$1; start_date=$2; end_date=$3;
    files=""
    for f in `ls $path | egrep "\.csv\.gz$"`; do
        st=`echo $f | awk '{z=split($1,a,"/"); split(a[z],b,"."); n=split(b[1],c,"-"); print c[n-1]}'`
        en=`echo $f | awk '{z=split($1,a,"/"); split(a[z],b,"."); n=split(b[1],c,"-"); print c[n]}'`
        diff_st=`dates_diff $start_date $st`
        diff_en=`dates_diff $en $end_date`
        if [ $diff_st -ge 0 -a $diff_en -ge 0 ]; then
            files="$path/$f,$files"
        fi
    done
    if [ -n "$files" ]; then
        echo ${files::${#files}-1}
    else
        echo ""
    fi
}

# checks consistency of train and valid data
column_count_check() {
    # column_count_check {old,new} train_clf_file valid_clf_file
    pref=$1
    f1=$2 #usually train_clf.csv.gz
    f2=$3 #usually valid_clf.csv.gz
    hdiff=`headers_diff $f1 $f2`
    if [ ! "${#hdiff}" -le 0 ]; then
        endl=$'\n'
        echo "[$pref] Error: different number of attributes. Difference:$endl$hdiff"
        exit 1
    fi
}


run_model_on_hadoop(){
    #ssh to analytix and run script    
 
    {
        ssh -o "StrictHostKeyChecking no" analytix << EOF 
        cd spark
        bash run.sh $1 $2 $3 $4 $5 
EOF
    } || {
        echo 'Failed to run, fixing know hosts'
        sed -i "/\b\(analytix\)\b/d" /afs/cern.ch/user/k/kkancys/.ssh/known_hosts
        ssh -o "StrictHostKeyChecking no" analytix << EOF
        cd spark
        bash run.sh $1 $2 $3 $4 $5
EOF
    }
}


# predicts, verifies, and stores the result
predict_and_write() {
    # predict_and_measure {old,new} classifier validation_start_date
    pref=$1; clf=$2; valid_start=$3
    
   # model --learner=$clf --idcol=id --target=target --train-file="${pref}_train_clf.csv.gz" --newdata="${pref}_valid_clf.csv.gz" --scaler=StandardScaler --predict="${pref}_${clf}.txt" --split=0 --timeout=$running_time_file #--proba
    
    run_model_on_hadoop $clf "${pref}_train_clf.csv.gz" "${pref}_valid_clf.csv.gz" "${pref}_${clf}.txt" $running_time_file

    out=`check_prediction --fin="${pref}_valid_clf.csv.gz" --fpred="${pref}_${clf}.txt" --scorer=$scorer --plain-output` #--threshold=0.5`
    # do not uncomment if ensembler used
    #rm "${pref}_${clf}.txt"
    echo "[$pref] to csv: $out"
    echo "$pref,$clf,$valid_start,$out" >> "$result_file"
}

# ensemble part
ensemble_and_write() {
    # ensemble_and_write (old|new) validation_file validation_start_date
    pref=$1; fvalid=$2; valid_start=$3
    echo "[$pref] Collecting ensemble..."
    ensemble_predictions --fbeg="${pref}_" --fout="${pref}_Ensemble.txt"
    out=`check_prediction --fin="${pref}_valid_clf.csv.gz" --fpred="${pref}_Ensemble.txt" --scorer=$scorer --plain-output`
    echo "[$pref] to csv: $out"
    echo "$pref,Ensemble,$valid_start,$out" >> "$result_file"
}

# result file preparation
prepare_out_csv() {
    echo "dftype,clf,date,$scorer" > "$result_file"
}

##### MAIN ITERATION #####

# predicts and measures performance, then concats train and valid data
iteration() {
    # usage : iteration {old,new} date_train_end
    pref=$1; __train_end=$2; __valid_start=`newdate --date=$2 --step=1`
    dol='$'
    echo "[$pref] Separation date: $__valid_start"
    vdata_step=`python -c "print($valid_step_days+$valid_step_data_ext)"`
    __valid_end=`newdate --date=$__valid_start --step=$vdata_step`
    path=`eval "echo \"${dol}${pref}_path\""`
    vfiles=`get_file_list $path $__valid_start $__valid_end`
    if [[ ! -z "${vfiles// }" ]] || [[ "$__valid_end" -gt $valid_end ]]; then
        prepare_train_data $pref $__train_end
        echo "[$pref] Validation files: \"$vfiles\""
        echo "[$pref] Preparing validation, transforming all data..."
        merge_csv --fin=$vfiles --fout=${pref}_valid.csv.gz
        __drops=`find_drops --file1=${pref}_train.csv.gz --file2=${pref}_valid.csv.gz --drops=$drops`
        logstr=""; if [ $use_log -eq 1 ]; then logstr="--log-thr=100000"; fi #logstr="--log-all"
        transform_csv --fin=${pref}_train.csv.gz --fout=${pref}_train_clf.csv.gz --target=naccess --target-thr=10 --drops=$__drops $logstr
        transform_csv --fin=${pref}_valid.csv.gz --fout=${pref}_valid_clf.csv.gz --target=naccess --target-thr=10 --drops=$__drops $logstr
        echo "[$pref] Data is prepared. Verifying..."
        if [ $use_log -ne 1 ]; then
            verify_dfr --file1=${pref}_train.csv.gz --file2=${pref}_train_clf.csv.gz
            verify_dfr --file1=${pref}_valid.csv.gz --file2=${pref}_valid_clf.csv.gz
        fi
        column_count_check $pref ${pref}_train_clf.csv.gz ${pref}_valid_clf.csv.gz
        echo "[$pref] Predicting, writing data ..."
        for clf in "${classifiers[@]}"; do
            predict_and_write $pref $clf $__valid_start
        done
        if [ $use_ensemble -eq 1 ]; then
            ensemble_and_write $pref ${pref}_valid_clf.csv.gz $__valid_start
        fi
    else
        finished="yes"
    fi
}

# prepares result file
prepare_out_csv $result_file

echo "model,running_time_s" > $running_time_file


for d in "${data[@]}"; do
    if [ -f "${d}_train.csv.gz" ]; then rm "${d}_train.csv.gz"; fi
    finished="no"
    n=1
    __train_end=$train_end
    while [ "$finished" == "no" ]; do
        echo "===== Starting iteration << $n >> ===== |`date +'%Y-%m-%d %T'`|"
        iteration $d $__train_end
        __train_end=`newdate --date=$__train_end --step=$valid_step_days`
        ((n+=1))
        if [ `newdate --date=$__train_end --step=$valid_step_days` -gt $valid_end ]; then
            break
        fi
    done
    echo "[$d] Work done."
done

python groupAndSum.py $running_time_file

if [ $plot_result -eq 1 ]; then
    csv_to_graph --fin=$result_file --fout=$plot_file --timein=$running_time_file --x-eq --col-rb
fi
