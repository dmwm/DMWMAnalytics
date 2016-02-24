Intership Workflow (2016, Spring)
----------------------

### Week #4
TODO:
* Continue with 2016 data prediction script
* Redo manually whole dataframe-model-verify process
* Select final scorer functions to use further in project

23 Feb 2016
* Cheking origin of validation and popdb verification mismatch
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
