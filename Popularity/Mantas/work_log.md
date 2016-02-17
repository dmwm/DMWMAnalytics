Intership Workflow (2016, Spring)
----------------------

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

### Week #2

08-10 Feb 2016
* Taking part in excursion for LHC CMS (guide Ivan Glushkov)
* Familiarizing with DMWMAnalytics project structure, reading about CMS services
* Continue reading printed documents
* Familiarizing with DMWMAnalytics project structure, reading about CMS, went to LHC CMS
* Working with DMWMAnalytics services issues (found problems with MongoDB service, VER=HG1509a)

11 Feb 2016
* Recreated VM (named "mbiliau-dev"), in favor of complete configuration needed to perform additional step: request and register personal certificate, which (not explicitly described in "CERN virtual machine tutorial") is performed by
  * https://ca.cern.ch/ca/user/Request.aspx?template=EE2User
  * https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookStartingGrid#ObtainingCert
* Deloyed updated (VER=HG1512e) DMWMAnalytics services from comp.valya repository
* Overviewing DMWM tutorials in https://cms-http-group.web.cern.ch/cms-http-group/tutorials/index.html
  * Monitoring service is verifying reply from http://localhost:8330/, found http://localhost:8330/ is unavailable in my VM (cause currently unknown)
* Checking result from http://localhost:8330/dcafpilot/, familiarizing with access logs /data/srv/logs/dcafpilot/dcaf-*.log

12 Feb 2016
* Checking services configuration /data/srv/current/config/<service>/
* Checking crontab, and manually rerunning dataframe, models, verify cron jobs, and the results obtained
 - Dataframe collected data for previous week
 - Prediction verification showed that classifiers produced errorneous results
* Familiarizing with cherrypy server
* Continuing familiarizing with project structure
* Checking ML models in code

14 Feb 2016
* Checking tasks for upcoming week (most important is project selection)
* Dowloading dataframe data for 2013-2016 years, running models and verify crons for new data
* Checking the prediction results - some classifiers gave 0/1 predictions, some all dataset classified as unpopular. TODO: Recheck results in detail next week
* Overviewing "Predicting dataset popularity for CMS experiment" (V.Kuznetsov et al.) - https://www.dropbox.com/s/ldjxme0upoonbfb/paper.pdf
* Working with some UNIX commands

### Week #3
15 Feb 2016
* Overviewing "Dynamic Data Management in a Data Grid Environment" (B.Barrefors) - http://digitalcommons.unl.edu/cgi/viewcontent.cgi?article=1113&context=computerscidiss
* Overviewing "The anatomy of the grid:  Enabling scalable virtual organizations." (I.Foster et al.) - http://hpc.sagepub.com/content/15/3/200.full.pdf.
* Filling and formatting of internship workflow document
* Learning using github : fork, fetch, commit, push, merge, setting remote repositories, updating forked DMWMAnalytics repository

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
