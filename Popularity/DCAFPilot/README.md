DCAF stands for Data and Computing Analytics Framework.
The aim of this project is to collect information from
CMS data-services and represent it in a form suitable
for analysis, e.g. machine learning tools. For full
description of CMS analytics challenge please refer to this
twiki [1].

We foresee that this project will require uses of different
technique, e.g. standard machine learning, online learning
or custom based solutions, see [2,3,4,5]. Usage of common
frameworks or languages is desired [6,7,8].

The framework consists of several layers:
- storage layer, which can be used to keep information from various
  CMS data-services. Currently, DCAF uses MongoDB and
  associated py-mongo driver as a storage solution, but
  it can be replaced with any other key-value store or RDBMS database.
- mapping layer to provide mapping between sensitive information and its
  numerical representation, e.g. DNs into set of unique ids
- aggregated layer which collects and merge information from various
  CMS data-sources
- representation layer will take care of data representation suitable
  for analysis framework, e.g. represent our dataframe into CSV data-format
- analysis layer which will either use a custom analysis algorithm or
  provide bridge to other learning system libraries. The easiest solution
  would be to use python sklearn library [7] which already provides broad
  variety of learning algorithms.

Dependencies
------------
DCAF currently depends on MongoDB. The MongoDB is object-oriented database. It
is distributed as a binary package which is available from MongoDB [9] web
site. Just download appropriate package for your underlying OS and run mongodb
as following:

```
port=XXXX # setup your favorite port number
mongod --fork --dbpath=/path/mongodb/db --port $port --nohttpinterface
--logpath /path/mongodb/logs/mongodb.log --logappend
```

The DCAF etc/dcaf.cfg configuration file is place where you'll specify
your port and database collections.

The pymongo driver [10] is freely available python driver for MongoDB.
It can be installed via pip or any package management tools on your OS
as well as normal python package (download, untar, run python setup.py
install).

Usage
-----

To use DCAF package simply setup your environment, see setup.sh for
example.

To start any analysis we need data. The DCAF package provides simple
way to generate dataframe for any period of time, e.g.

```
# to get some help
dataframe --help

Usage: dataframe.py [options]

Options:
  -h, --help            show this help message and exit
  --fout=FOUT           Output file
  --seed-dataset=SEED   Seed dataset,
                        default=/ZMM/Summer11-DESIGN42_V11_428_SLHC1-v1/GEN-
                        SIM
  --dbs-extra=DBS_EXTRA
                        Extra datasets from DBS which were not shown in
                        popularityDB, default 1000
  --metric=METRIC       Output target metric (naccess by default), supported
                        naccess, nusers, totcpu or python expression of those
  --start=START         Start timestamp in YYYYMMDD format
  --stop=STOP           Stop timestamp in YYYYMMDD format
  --format=DFORMAT      Output file format, deafult csv (supported csv, vw)
  --config=CONFIG       Config file, default etc/dcaf.cfg
  --verbose=VERBOSE     Verbosity level, default 0
  --update              Update internal storage (get new DBS/SiteDB database
                        content
  --newdata             Get new set of data from DBS, instead of popularity DB

# to run a script
dataframe --start=20141112 --stop=20141119 --fout=file.csv
```

DCAF package talks to several CMS data-services:

- popularity DB, to get spanshot of popular dataset over period of time
- DBS, to get meta-data information about given dataset
- Phedex, to get location information about given dataset
- SiteDB, to get user and site information
- Dashboard, to get historical usage of user jobs

All of these information are formed into single dataframe. The popularity
of certain dataset are defined via Popularity DB metrics, such as number
of dataset accesses, their CPU usage time, etc. By default the
dataframe script generates csv files for naccess parameter.

The actual analysis of data can be performed in any Machine Learning
(ML) tool. But DCAF package also includes series of R/Python sklearn-based
scripts to do this. For instance, someone can use ```model``` script to
perform data analysis, e.g.

```
bin/model --help

Usage: model.py [options]

Options:
  -h, --help            show this help message and exit
  --scaler=SCALER       model scalers: ['StandardScaler', 'MinMaxScaler'],
                        default None
  --scorer=SCORER       model scorers: ['accuracy', 'adjusted_rand_score',
                        'average_precision', 'f1', 'log_loss',
                        'mean_absolute_error', 'mean_squared_error',
                        'precision', 'r2', 'recall', 'roc_auc'], default None
  --learner=LEARNER     model learners: ['AdaBoostClassifier',
                        'AdaBoostRegressor', 'BagginRegressor',
                        'BaggincClassifier', 'BernoulliNB',
                        'DecisionTreeClassifier', 'ExtraTreesClassifier',
                        'GaussianNB', 'GradientBoostingClassifier',
                        'GradientBoostingRegressor', 'KNeighborsClassifier',
                        'LinearSVC', 'PCA', 'RandomForestClassifier',
                        'RandomForestRegressor', 'RidgeClassifier',
                        'SGDClassifier', 'SGDRegressor', 'SVC', 'SVR',
                        'lda_rfc', 'pca_knc', 'pca_rfc', 'pca_svc']
  --learner-params=LPARAMS
                        model classifier parameters, supply via JSON
  --train-file=TRAIN    train file, default train.csv
  --test-file=TEST      test file, default no test file
  --idx=IDX             initial index counter, default 0
  --limit=LIMIT         number of rows to process, default 10000
  --verbose=VERBOSE     verbose output, default=0
  --roc                 plot roc curve
  --full                Use full sample for training, i.e. don't split
  --crossval            Perform cross-validation for given model and quit
  --gsearch=GSEARCH     perform grid search, gsearch=<parameters>
  --predict             Yield prediction, used by pylearn
```

References
----------

[1] https://twiki.cern.ch/twiki/bin/view/Main/CMSDataMiningForAnalysisModel

[2] http://www.wikiwand.com/en/Machine_learning

[3] http://www.wikiwand.com/en/Online_machine_learning

[4] http://www.wikiwand.com/en/Vowpal_Wabbit

[5] http://www.wikiwand.com/en/Stochastic_gradient_descent

[6] http://www.wikiwand.com/en/R_(programming_language)

[7] http://scikit-learn.org/

[8] http://0xdata.com/

[9] http://www.mongodb.org/downloads

[10] http://api.mongodb.org/python/current/
