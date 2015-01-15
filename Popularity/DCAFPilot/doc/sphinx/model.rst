Model builder
=============

.. toctree::
   :maxdepth: 4

The model is a main tool to build predictive model:

.. doctest::

    model --help
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
                            'AdaBoostRegressor', 'BaggingClassifier',
                            'BaggingRegressor', 'BernoulliNB',
                            'DecisionTreeClassifier', 'DecisionTreeRegressor',
                            'ExtraTreesClassifier', 'ExtraTreesRegressor',
                            'GaussianNB', 'GradientBoostingClassifier',
                            'GradientBoostingRegressor', 'KNeighborsClassifier',
                            'LinearSVC', 'PCA', 'RandomForestClassifier',
                            'RandomForestRegressor', 'RidgeClassifier',
                            'SGDClassifier', 'SGDRegressor', 'SVC', 'SVR',
                            'lda_rfc', 'pca_knc', 'pca_rfc', 'pca_svc'], default
                            RandomForestClassifier
      --learner-params=LPARAMS
                            model classifier parameters, supply via JSON
      --learner-help=LEARNER_HELP
                            Print learner description, default None
      --drops=DROPS         Comma separated list of columns to drop, default id
      --idcol=IDCOL         id column name, default id
      --target=TARGET       Target column name, default naccess
      --split=SPLIT         split level for train/validation, default 0.33
      --train-file=TRAIN    train file, default train.csv
      --newdata=NEWDATA     new data file, default None
      --idx=IDX             initial index counter, default 0
      --limit=LIMIT         number of rows to process, default -1 (everything)
      --verbose=VERBOSE     verbose output, default=0
      --crossval            Perform cross-validation for given model and quit
      --gsearch=GSEARCH     perform grid search, gsearch=<parameters>
      --predict=PREDICT     Prediction file name, default None

Model
=====

To build predictive model please run as following:

.. doctest::

    model --learner=RandomForestClassifier --idcol=id --target=target
          --train-file=train_clf.csv.gz --scaler=StandardScaler
          --scorer=precision,accuracy,roc_auc

To run your model with new data try this:

.. doctest::

    model --learner=RandomForestClassifier --idcol=id --target=target
          --train-file=train_clf.csv.gz --scaler=StandardScaler
          --newdata=newdata.csv.gz --predict=pred.txt

