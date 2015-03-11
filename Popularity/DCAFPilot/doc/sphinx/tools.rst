DCAFPilot tools
===============

This section describes set of tools available in DCAFPilot framework.
Each tool has *--help* option and we encourage users to explore it in details.
Here we'll only provide short description of each tool:

- check_prediction, check predictions of the model against predicted file

- cron4dataframe.sh, crontab script to generate dataframe

- cron4models.sh, crontab script to run models over the given data

- cron4verify.sh, crontab script to verify model prediction

- csv2libsvm, CSV to LibSVM convert script

- csv2vw, CSV to VW convert script

- dataframe, dataframe generator script, capable to capture historical and new
  data from CMS data-services

- dates, script to generate date pairs from given date and a step, e.g. weeks
  from given date

- dcaf_server, stand-alone static file web server (can be used to serve
  prediction files)

- generate_scripts.sh, helper script to generate series of dataframe actions
  from given date

- merge_csv, merge multiple CSV into single file

- model, script to run ML algorithm over the data, based on python scikit-learn
  library

- new_datasets, produce file with new datasets/dbs pairs from provided training
  set and new data files

- newdate, helper script to print next date from given one

- popular_datasets, script to collect dataset info from popularity DB

- pred2dataset, script which convert ML output into human readable form, yields
  probability and dataset name pairs

- printjson, helper script to print content of JSON file

- run_models, shell script to run different ML models, either validate them or
  yield predictions

- runvw, script to run VW algorithm

- runxgboost, script to run xgboost algorithm

- scp.sh, script to copy files from CERN VM into CERN AFS node

- slice_data, slice train/newdata files with respect to prodived dataset/dbs
  set

- test_models.sh, helper script to test different models

- tier_lookup, helper script to look-up DBS TIER from local cache and input
  data file

- transform_csv, script to perform transformation over provided CSV dataframe

- verify_predictions, script to verify prediction against popularity DB data
  for given time period

- vw_pred2csv, helper script to convert VW prediction into CSV data format
