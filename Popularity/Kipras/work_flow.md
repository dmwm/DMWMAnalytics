Summer student (2016)

### Week 5

28 Jul 2016

- Got the final output. Very low TP rate (need to investigate it) and high execution time(need to improve it).

25-27 Jul 2016

- Combining roll script and model on spark.
- Model output file formatting
- Retrieving files from HDFS and merging them
- Time measuring and producing proper format results file
- Ssh analytix problem
- Fixing paths

### Week 4

20-22 Jul 2016

- Learning hadoop spark (...)
- Running a RandomForestClassifier on given data (done)
- Running a hadoop model script from inside roll2.sh (done)
- Moving files from local dir to HDFS (if not exist on HDFS) from inside script (done) 
- Making proper output in hadoop model that could be used by roll2.sh (pending)
- Moving files from HDFS back to local dir (pending)
- Measuring classifier execution time (haven't started yet)

### Week 3

13-15 Jul 2016

- Trying different drops. Valentin suggesged:

> drops="campain,creation_date,tier_name,dataset_access_type,dataset_id,energy,flown_with,idataset,last_modification_date,last_modified_by,mcmevts,mcmpid,mcmtype,nseq,parent_dataset,parent_dataset_id,pdataset,physics_group_name,prep_id,primary_ds_name,primary_ds_type,processed_ds_name,processing_version,pwg,this_dataset,rnaccess,rnusers,rtotcpu,s_0,s_1,s_2,s_3,s_4,totcpu,wct,cpu,xtcrosssection"

Which gives prety good results. RandomForestClassifier (old data TPR, TNR ; new data TPR TNR) - (89.85% , 99.23% ; 86.69% , 98.94%) 

I tried no to drop some of these parameters(these changes has no effect on old data).

- Date related params: creation_date, last_modification_date. Results on new data TPR +3%
- Modification related params: last_modified_by,last_modification_date. Results on new data TPR +3%
- Mcm type params: mcmevts,mcmpid,mcmtype. Results on new data TPR -2%
- Parent ds related params: parent_dataset,parent_dataset_id. Results on new data TPR +4.5%
- Primary ds related params primary_ds_name,primary_ds_type. Results on new data TPR +3.5%
- Process params: processed_ds_name,processing_version. Results on new data TPR +4%

After that I tried to combined best results giving drops. However none of the all possible compositions of process, primary, parent parameters are not giving better results. 

Finally I stayed with such drop:

> drops="campain,creation_date,tier_name,dataset_access_type,dataset_id,energy,flown_with,idataset,last_modification_date,last_modified_by,mcmevts,mcmpid,mcmtype,nseq,pdataset,physics_group_name,prep_id,primary_ds_name,primary_ds_type,processed_ds_name,processing_version,pwg,this_dataset,rnaccess,rnusers,rtotcpu,s_0,s_1,s_2,s_3,s_4,totcpu,wct,cpu,xtcrosssection"

Which gives (89.85% , 99.23% ; 91.17% , 98.94%) instead of (89.85% , 99.23% ; 86.69% , 98.94%)

11-12 Jul 2016

- Got PCA results, they are close to what we had before. However they took around 4 times more time to calculate.

### Week 2

7-8 Jul 2016 

- Experimenting with PCA, configuring VM and learning hadoop spark.

6 Jul 2016

- Trying different scalers. No significant changes in most of the clasifiers. However SGD clasifier performs poorly on new data with no scaler and MinMaxScaler.

5 Jul 2016

- Calculating ratio of popular and other datasets in our weekly data. Everything looks normal. 

| Data | Week      | Pop  | Total | Proc |
|------|-----------|------|-------|------|
| Old  | 0526-0601 | 1611 | 12066 | 13%  |
| Old  | 0602-0608 | 1337 | 11570 | 11%  |
| Old  | 0609-0615 | 1773 | 12107 | 14%  |
| Old  | 0616-0622 | 1477 | 11899 | 12%  |
| New  | 0526-0601 | 1803 | 12367 | 14%  |
| New  | 0602-0608 | 1569 | 11679 | 13%  |
| New  | 0609-0615 | 1918 | 12305 | 15%  |
| New  | 0616-0622 | 1744 | 12223 | 14%  |

- Analyzing drop parameters code part. Got the actual results. That are very similar to the previous. Which means we can drop those parameters with almost no loss of accuracy.

4 Jul 2016

- Idea for the next day to find out witch parameters are actually used in model script.
- Dropping parameters and running roll script. Result is identical, which means that dropped parameters originally might not be used in model.
- Rules to drop parameter:
  - Exploring parameters that are highly correlated (value > 0.6)
  - Taking a first pair of parameters with highest correlation. 
  - Sum of abs correlations for each of these parameters. Choosing parameter that is more correlated with the others.
  - Removing such parameters and recalculating all the correlations.
  - Repeating until there is no parameters correlated more then 0.6.
  - Dropped parameters: rel1_8, rel1_5, nfiles, rel3_0, parent, rel1_3
- Plotting correlation between parameters (plot with parameters that are correlated more than 0.6 is added). 
Considering old data, 5 weeks (2016.05.26-2016.06.29)
- Updating roll plot with 3 weeks data (plot added to week_2 folder)

### Week 1

1 Jun 2016

- Running roll script on fixed data. Results in week_1 folder. 
- Exploring differencies between old and new data.

30 Jun 2016

- Review of the project plan:

> **Project plan:**  
> **PART No 1**
> - Do separate parts of roll2 process:
>   - Merge dataframes
>   - Transform dataframes 
>   - Split data to training and validation parts
>   - Make a model on training data
>   - Use that model on validation data
>   - Get statistics of TPR, FPR, CPU time and RAM  
> - This should be done for both old and new data (date after the bug fix).
> - Rolling process means: Let's say starting from 3 weeks training data we predict the next week. For the next week we add another week to training data and we predict 5-th week using 4 weeks data.
> -  To get TPR and FPR statistics we compare our prediction with actual labels which we get from (naccess, nusers, totcpu .. or other metrics)
> - RF, SGD and XGB classifiers should be used for modelling. 
> - We should also try to combine multiple classifiers together to get better predictions.
> 
> **PART No 2**  
> - At the beginning  run a simple modeling algorithm on SPARK
> - Later move all model process to SPARK to decrees computing time

29 Jun 2016

- Analyzing roll2.sh script. Found that current profile (source /data/srv/current/apps/DCAFPilot/etc/profile.d/init.sh) has to be sourced before running the script.
- Getting to know git


28 Jun 2016

- Plotting histograms of every parameter of two weeks: 2015 11 19-2015 11 25 and 2016 06 16-2016 06 22.
- Looking for differences in distributions. Visible differences in most rel_.. parameters.
- Reading about bash scripting. 
- Trying terminal editors.

27 Jun 2016  

- Setting up VM

