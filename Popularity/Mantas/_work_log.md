Intership Workflow (2016, Spring)
----------------------

### Week 8

21 Mar 2016
* Corrected tags for week 6 assignment 1
* Collected new dataframes
* Implemented prediction ensemble "ensemble_predictions"
* Implemented --log-thr in transform_csv
* Implemented model running recording
* Testing of changes

### Week 7

18 Mar 2016
* Collected results for assignment 1 and 2
* Working with assignment 1 report to find and output all data-tiers sorted prediction results
* Working with assignment 2 graph: to dinamically output plots and draw them correctly
* Collecting data, Friday reporting, video conference
* Preparing to work with new tasks, projecting and writing out implementations

17 Mar 2016
* Assignment 2 (iterative) script run into failure during night run. The reason - headers dismatch raised in headers_diff script. The mismatch occured between iteratively appended and already transformed training data and transformed validation - one week - data. Such random errors are very rare and confusing. This time I think one of 'those' responsible functions may have been found and updated: find_drops function did not perform well in case both training and validation data have disjoint columns, then one file tend to have more columns. Updated.
* Finished csv_to_graph script for assignment 2, but need to wait for data in order to draw and the asignment 2 algorithm, as stated yesterday, should run approximately 10-16 hours. An excercise was to think of data structure to load and plot the data. After solution the script was finished quickly. Hope to produce results tomorow before video conversation.
* Assignment 1 script finished, left to adopt Reporter to print out tier-separated data. Also, need to think of logics how to output it, but first simplest approach may be chosen.

16 Mar 2016
* Adopting check_prediction.py to return aggregated data by tiers. It was not convenient to use verify_predictions.py functions, written new ones using pandas [works fast]. Added new options --tiers_break(use or not output tier breaking), --tiers_col(provide column name for tier), --tiers_map(mapping file of tier id and tier name, since we need names, not ids/hashes), --tiers_map_kval(provide mapping key and value: column names in mapping file for tier id/hash column and tier name column, e.g. 'id,tier' or 'hash,tier'). Already returns result devided by tiers in plain CSV format. Of course, when not using --tiers_break, script works as earlier.
* Assignment 2 script was left working. Small bug fixed, will leave tonight to work. Script with 2 classifiers setting finished in a little more then 2 hours. There are 6 classifiers, 2 dataframe types, so should work about 10-16 hours.
* Again, 2016 old data does not work well. Lots of 0 TP weekly results from assignment 2. Tomorrow hope to see full results for this script.
* Left for assignment 1: add new function to Reporter to read csv to report. Test check_prediction.py --tiers_break performance. From first sight works fine.
* Left fot assignment 2: finish csv_to_graph to draw #scorer plots with each classifier performance
* Later assignment 2 iterative script may be adopted to analyze all old or all new data performance

15 Mar 2016
* Working with assignments 1 and 2
* Assignment 1 in fulltrain/tiervalid setting return 0 TP with 2015sh/2016fw period. Investigated, no errors found
* Assignment 1 return very poor (0TP) results within old 2015sh/2016fw period. Investigated. No errors in script found. Same setting with 2013sh/2014fw old data returns very good (90%+ for T rates) results
* Output iterative results of assignment 2 to csv
* Adopted check_prediction.py to output prediction in plain csv format
* Script csv_to_plot to draw a plot from csv results, already works, need to adopt to draw data from many clfs in one graph, perhaps one graph for one scorer

14 Mar 2016
* Continuing running prediction scripts
* Reporting prediction results
* Continuing working with last week assignments 1 and 2, scripts large, debugging is relatively slow
* Received new tasks:
  - Column selection for log-transform using threshold and first 10 rows
  - Create an emsamble for current 6 classifiers
  - Add probabilistic metric for classifier

### Week #6
11 Mar 2016
* Continuing developing assignments 1 and 2
* Fixed "newdata" function in utils/utils.py (--step parameter)
* Moved log_transform functionality of --log-all and --log-cols to transform_csv and adopted (warning: verify_dfr cannot be used with log transform option since it changes values of dataframe)
* Updated reporter.py (was not rigid with some *.pred files)
* Received task to perform other predictions within different periods and data
* Starting running new predictions
* Observed solid difference in portion of datasets within same datatiers in old and new data. Appears, new dataframes contain relatively many "0" values which origin is curently unknown

10 Mar 2016
* Finished parse_csv script. The version of pandas in module is 0.15.1, so it does not support to_csv command "compression" option, which was implement to work with gzip in 0.17.1. Implemented manually.
* Worked line by line week_4 and week_5 scripts. Error by copy-paste was left in week_4 assignment script. Appears, classifier was trained and validated on the same data, thats why it produced such good results. The true results are much worse. Today in end of work will rerun all 3 past homeworks and tomorrow will report the results.
* Continuing towards assignment 1, rewrote files collecting procedure which used regex, now will work with date ranges. Since on every iteration it calls one python line it works many times slower, ~10 secs vs <1sec previously. In future will look for faster solution here.
* Found that some[or all] new datasets contain 'tier' value as 0.
* Expanded parse_csv to read either from old and new tier.txt structure.
* Writing iterative assignment 2 script (may require one mpre option for verify_prediction to outut in csv format)


09 Mar 2016
* Working towards new assignment 1. Finished script verify_dfr, although troughout the day fixed some small issues.
* Started writing script parse_csv to extract information from csv.gz and form new csv.gz from it.
* To obtain new id-tier mapping in new dataframes, new Go dataframe application has to be compiled. There were some issues regarding making it. Found and fixed MakeFile.
* Assigment from last week was changed to work like assignment from prelast week.
* Met small issue regarding read_csv warning about different data types in column. Ommiting the warning in made by redirecting stderr. Fixed.

08 Mar 2016
* Rewrote reports of last week assignments to use Reporter. There were small issues that were fixed. Report generation script shrinked many times.
* Added XGBoostClassifier and added TPR,TNR,FPR,FNR rates in operation. Still investigating the results in the assignments.
* Started to write script for new weeks assignment 1.
* Began to write verify_dfr script to verify column statistics before and after transformation.

07 Mar 2016
* Installed new RPMs. Were some problems with proxy, manual copying solved the issue.
* Continued working with 'reporter.py' package. The package contains Reporter class which will be convenient and fast to make assigment-related reports. It will may be expanded futher according the needs
* Investigated why last week assignments produces such results
* Reporter has ability to add description-like sections

### Week #5

05 Mar 2016
* Trying to install new RPMs, receiving error 5 related with expired proxy. Working on it

04 Mar 2016
* Found that assignment 2 script failed to produce correct results since merge_csv did not support 1 file input
* Produced the file manually, rerun the script, results for the week were either too bad or wrong. Script rerun with 2 weeks validation period
* Written first version of transform_log
* Produced report for assignment 1
* Had a video conversation, received new tasks for the next week:
  1. Report. Add descriptions.
  2. Use pandas to load framework for log_transformation
  3. Add log_transformation as an option to transform_csv : transform all columns, or transform columns using provided list
  4. Report. Add normalized TP, FP, TN, TP values. Do I understand this right? I have to add:  
   1) TPR = TP/(TP+FN)  
   2) TNR = TN/(TN+FP)  
  5. Provide function to extract datasets from selected datatiers (AOD/AODSIM/MINIAOD/MINIAODSIM/USER). Use pandas library to do that.
  6. Prediction task #1 using (5) function. Do it using old dataframe and new dataframe:  
   1) Learn model on full dataframe, predict/verify datasets only from selected datatiers  
   2) Learn model on selected datatiers, predict/verify datasets on selected datatiers  
   3) Report. Provide results grouped by datatiers  
  7. Prediction task #2:  
   1) initial train data      : 9 last months for 2015  
   2) initial prediction week : first week of 2016  
   3) train model using training data  
   4) predict given week  
   5) verify the prediction, provide scorers, record result to csv report  
   6) add prediction week to train data  
   7) move prediction week one week forward and continue with 3rd step or if no data available continue with 8th step  
   8) use csv report to plot using TPR, TNR rates  
   9) convert csv report and save to human readable form  
* Working with adding xgboost to model using rep, received message, that it is not necessary since new xgboost comes with python APIs 
* Reveiced a message that new RPMs (DCAFPilot 0.1.23) are available, left it for next day

03 Mar 2016
* Received new tasks
* Finishing report generation script for both assignments
* Upload assignment 1 report with TP, TN, FP, FN scorers
* Writing separate script to run xgboost. Suggesting to move it to central "model" unit
* Prolonging the period of training period for assignment2 to 9 months, validation data within 1 week, running the script

02 Mar 2016
* Collected data from both of assigments, wrote a "report" executable which consolidates produced data, calculates mean and std for primary analysis
* Results for assignment 1:
  - Classifiers used: AdaBoostClassifier, BaggingClassifier, DecisionTreeClassifier, KNeighborsClassifier, RandomForestClassifier
  - Script run slow, however, primary results are sufficient to make some conclusions. Average scores for 5 classifiers:
    + accuracy  0.77514
    + precision 0.44486
    + recall    0.33146
    + f1        0.37422
  - Results are too low
  - Further analysis for feature selection should be applied
  - More detailed results may be found in files 'readme' and 'report_prim.txt' under pred_task_0226/assignment_1/results_2015_2016/
* Results for assignment 2:
   - Comparison against prediction using old data allows to come to same conclution as in assignment 1 that some of new features are biased
   - Futher study need to be performed to find out impact of new features individually
   - Detailed results may be found in files 'readme' and 'report.txt' under pred_task_0226/assignment_2/results_2015_01-03_04/

01 Mar 2016
* Wrote script for assignment 2, fixed assigment 1
* Assignment 1 script was running much longer (several hours) - it uses data from more than 1 year period
  - 4 finished, 5th running
* Assignment 2 script runs much shorter since it uses 4 months [3+1] data
  - Constructed setting to run nearly all available - 14 - classifiers (subsequently)
  - Script has finished processing the data with all classifiers (in ~1.5 hours)
  - Continue working towards analysing the output results


### Week #4

29 Feb 2016
* Working with assigment 1
  - Were some differences : 'dbs' -> 'dbsinst' in new dataframe
  - There are situations when new dataframe does not have columns which older one had
* Created draft for assignment 2

26 Feb 2016
* Reading the code how the dataframe is generated and how it differs from information received only from PopDB
* Reading about ROC AUC
* Started to implement framework to work with logistic regression and threshold, stopped after Friday skype call since ROC+AUC and AUC are different methods
* Received new tasks for next week:
  - Run 5 classifiers on newly Go-generated dataframes using 2015 training data and 2016 validation data
  - Running same setting use old and new dataframes to show influence of additional attributes within new dataframe
  - Install Go, run dataframe generation script

25 Feb 2016
* Investigated scorer functions, there relevance, working towards intuition
* Continuing working with prediction script regarding verification methods
* Found out that different verification methods work with different data
  - check_prediction   : dataframes contain information from PopDB plius 1000% of random databases
  - verify_predictions : verifies against PopDB
* Found the duplicates in dataframes data, but its normal in case of sampling with replacement 

24 Feb 2016
* Continue working with inequality of verification results
  - Found duplicates influence in verify_predictions
  - Created script to remove duplicates
  - Added optional --target parameter in verify_predictions to enable evaluation of popular dataset by naccess>10
  - Fixed run script
  - Difference dropped up to 15% for recall, 0.1% for precision score

  -------------------------------------------------------  
  
    Scores for verification with validation set:
    
        Score metric (accuracy_score): 0.999096461744
        Score metric (precision_score): 0.998474307336
        Score metric (recall_score): 0.996953263055
        Score metric (f1_score): 0.997713205476
    
    Scorers for verification with popdb data:
    
      Primal :
        Accuracy                  : 0.836028714888
        Precision                 : 0.5
        Recall                    : 1.0
        F1-score                  : 0
    
      Current :
        Accuracy                  : 0.972475728862
        Precision                 : 0.999590876547
        Recall                    : 0.838164665523
        F1-score                  : 0.911788030042
  
    - Verification with validation set performed with check_prediction script  
    - Verification with validation set performed with verify_predictions script  
    
  --------------------------------------------------------------
* Noticed seed-mbriliau.cert disappears several times a day. Did not investigate the causes yet

23 Feb 2016
* Checking origin of validation and popdb verification mismatch
  - ML model seed seem to have infuence for model prediction instabilily, but current script prediction is done only once, so it should not have influence to mismatch of verifications 
  - Started to looking deeper into data collection and verification processes
* Found dataframe cron still produces incorrect files
  - Reinstalled fresh new copy of latest RMPs (VER=HG1512e, dcafpilot 0.1.21) to avoid any changes I may have made
  - Rerun cron, it still produces corrupt dataframe file (dataframe-20160211-20160217.csv.gz)
  - Collected file size is ~200MB whereas ordinary dataframe file is ~700MB
  - Found errors in log dataframe-20160211-20160217.log (occurs 9 times with different document size figures):
    *dashboard::fetch url=http://dashb-cms-job.cern.ch/dashboard/request.py/jobefficiencyapi, params={'start': '2016-2-11', 'type': 'analysis', 'end': '2016-2-17', 'site': 'all', 'dataset': u'/TT_TuneCUETP8M1_13TeV-powheg-pythia8/RunIIFall15MiniAODv2-PU25nsData2015v1_76X_mcRun2_asymptotic_v12_ext3-v1/MINIAODSIM'}*
    *Caught bson error: BSON document too large (49280874 bytes) - the connected server supports BSON document sizes up to 16777216 bytes*
  - In order to increase BSON document size limit, one line of MongoDB C++ code can be changed before recompilation:
    + https://github.com/mongodb/mongo/blob/master/src/mongo/bson/util/builder.h#L64
* Continuing working with search for reason of different scorer results

22 Feb 2016
* Finished writing 2016 data prediction script
  - Verification made by:
    + prediction results comparison against validation data labels
    + prediction results comparison against data received from popDB
  - Scorers for two verification methods produce different confusion matrices
  - TODO: Need to find the cause of different prediction metrics
  - Observation: in second comparison (with PopDB) there is 0 TP score
  - Task accomplishment : DMWMAnalytics/Popularity/Mantas/pred_task_0219/ (branch mantas)
    + run - the script
    + work_plan.txt - the work plan
    + results.txt - result output from the run


### Week #3

21 Feb 2016
* Reading about scorers
* Reading model.py workflow
* Begin writing script
  - Train model using 2015 second half data
  - Predict and verify according 2016 data

19 Feb 2016
* Update of dcafpilot in vm 0.1.17 -> 0.1.21
* Working according workflow in talk slides
* Approximately half of workflow succeeded, in video conversation find out the importance of transformation in prediction process

18 Feb 2016
* Working with dataframe generation (2 steps - update from DBS and download data within timeframe)
* Dataframe which is generated was errorneuos to read (zcat)
* Fixing merge_csv merging order, but by fetching from git found out it was just fixed
* Robustness of dataframe.py improved using verify_csv function, but failed to test since the dataframe generation process was overall unsuccessful. Need to finish after successful generation of dataframe using dataframe script with dataframe

17 Feb 2016
* Rereading of "Predicting dataset popularity for CMS experiment" (V.Kuznetsov et al.)
* Rereading of Pilot1 talk "DCAFPilot for CMS" (V.Kuznetsov) slides
* Checked current verification resuls, models do not show robust performance (causes unknown for the moment):
  - LinearSVC: TP 0%, TN 87.8%
  - RandomForestClassifier: TP 0%, TN 87.8%
  - SGDClassifier: TP 0.8%, TN 0.9%
  - VW: TP 12.0%, TN 86.9%
  - XGBoost: TP 12.2%, TN 0.0%
* Fixing continuous 404 error logged in /data/srv/logs/admin/feed.lemon:
  - Error: *Feb 17 03:46:36 dcafpilot-web PING FAILED <http://localhost:8330> DCAFPilot HTTP Error 404: Not Found*
  - Fix:
    + 'PING_URL="http://localhost:8330/"' -> 'PING_URL="http://localhost:8330/dcafpilot/"' in /data/srv/current/config/dcafpilot/monitoring-dcafpilot-web.ini
    + restart web server
  - After fix: *Feb 17 16:51:45 dcafpilot-web PING OK <http://localhost:8330/dcafpilot/>*
* Starting working with robustness of dataframe.py

16 Feb 2016
* Set up new branch "mantas" and uploaded worflow document
* Reading of "Predicting dataset popularity for CMS experiment" (V.Kuznetsov et al.) - https://www.dropbox.com/s/ldjxme0upoonbfb/paper.pdf
* Reading slides of Pilot1 talk "DCAFPilot for CMS" by V.Kuznetsov (talk of Pilot2 was not found in the directory DMWMAnalytics/Popularity/DCAFPilot/doc/talks/)
* Printing and reading of: 
  - "Implementing data placement strategies for the CMS experiment based on a popularty model" (D. Giordano et a.)
  - "The CMD Data Management System" (M. Giffels et al.)
  - "Explorint Patterns and Correlations in CMS Computing Operations Data with Big Data Analyrics Techniques" (V. Kuznetsov et el.)
* Printing of:
  - "Explointing CMS data popularity to model the evolution of data management for Run-2 and beyond" (D. Bonacorsi et al.)
  - "CMS computing operations during run 1" (J. Adelman et al.)

15 Feb 2016
* Overviewing "Dynamic Data Management in a Data Grid Environment" (B.Barrefors) - http://digitalcommons.unl.edu/cgi/viewcontent.cgi?article=1113&context=computerscidiss
* Overviewing "The anatomy of the grid:  Enabling scalable virtual organizations." (I.Foster et al.) - http://hpc.sagepub.com/content/15/3/200.full.pdf.
* Filling and formatting of internship workflow document
* Learning using github : fork, fetch, commit, push, merge, setting remote repositories, updating forked DMWMAnalytics repository


### Week #2

14 Feb 2016
* Checking tasks for upcoming week (most important is project selection)
* Dowloading dataframe data for 2013-2016 years, running models and verify crons for new data
* Checking the prediction results - some classifiers gave 0/1 predictions, some all dataset classified as unpopular. TODO: Recheck results in detail next week
* Overviewing "Predicting dataset popularity for CMS experiment" (V.Kuznetsov et al.) - https://www.dropbox.com/s/ldjxme0upoonbfb/paper.pdf
* Working with some UNIX commands

12 Feb 2016
* Checking services configuration /data/srv/current/config/<service>/
* Checking crontab, and manually rerunning dataframe, models, verify cron jobs, and the results obtained
 - Dataframe collected data for previous week
 - Prediction verification showed that classifiers produced errorneous results
* Familiarizing with cherrypy server
* Continuing familiarizing with project structure
* Checking ML models in code

11 Feb 2016
* Recreated VM (named "mbiliau-dev"), in favor of complete configuration needed to perform additional step: request and register personal certificate, which (not explicitly described in "CERN virtual machine tutorial") is performed by
  * https://ca.cern.ch/ca/user/Request.aspx?template=EE2User
  * https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookStartingGrid#ObtainingCert
* Deloyed updated (VER=HG1512e) DMWMAnalytics services from comp.valya repository
* Overviewing DMWM tutorials in https://cms-http-group.web.cern.ch/cms-http-group/tutorials/index.html
  * Monitoring service is verifying reply from http://localhost:8330/, found http://localhost:8330/ is unavailable in my VM (cause currently unknown)
* Checking result from http://localhost:8330/dcafpilot/, familiarizing with access logs /data/srv/logs/dcafpilot/dcaf-*.log

08-10 Feb 2016
* Taking part in excursion for LHC CMS (guide Ivan Glushkov)
* Familiarizing with DMWMAnalytics project structure, reading about CMS services
* Continue reading printed documents
* Familiarizing with DMWMAnalytics project structure, reading about CMS, went to LHC CMS
* Working with DMWMAnalytics services issues (found problems with MongoDB service, VER=HG1509a)


### Week #1

03-05 Feb 2016
* Registration
* Setting up desktop computer (OS, computing account, network)
* Printing and reading of "Predicting CMS datasets popularity with Machine Learning" (L.Giommi)
* Printing and reading of "Using CMS Conference Schedules to Predict CMS Dataset Usage" (Ting Li)
* Setting up VM (named "mbiliau-vm") according "CERN virtual machine tutorial" https://cms-http-group.web.cern.ch/cms-http-group/tutorials/environ/vm-setup.html
* Deploying services for DMWMAnalytics
* Cloning and reviewing DMWMAnalytics project from https://github.com/dmwm/DMWMAnalytics
* Taking part in excursion about LEIR, become familiar with general idea of experiments, history, what is being done, planned to be done in CERN (guide Ivan Glushkov)
