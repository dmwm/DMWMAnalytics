Intership Workflow (2016, Spring)
----------------------

### Week #5
TODO:
* Assignment 1: use 2015 new dataframes for training 5 classifiers, 2016 data for verification, obtain the results
* Assignment 2: within same period using old and new dataframes analyze effect of new columns in new dataframe
* Study usage of auc scorer

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
