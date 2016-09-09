#!/usr/bin/env python

import math
import numpy as np
import pandas as pd
from pandas import read_csv
import xgboost as xgb
from sklearn.cross_validation import train_test_split 
from sklearn import preprocessing

# Here i keep prepared csv file for ML
f = open('/opt/data/TransferMonitoring/out.csv')
dataframe = read_csv(f).astype(np.float32)

# save headers to seperate list
original_headers = list(dataframe.columns.values)

# fields that are output and can't be used as input
drop_list_output = ['tr_id','t_error_code','tr_timestamp_complete','timestamp_tr_st']
for el in drop_list_output:
    try:
        dataframe = dataframe.drop(el, axis=1)
    except:
        print('There was no such field:{}'.format(el))

# fields that are non vairiating and useless
drop_list_non_variate = ['block_size','buf_size','channel_type',
                            'dst_site_name','src_site_name','t_timeout','src_srm_v','tcp_buf_size']
for el in drop_list_non_variate:
    try:
        dataframe = dataframe.drop(el, axis=1)
    except:
        print('There was no such field:{}'.format(el))

# fields that correlating and useless        
drop_list_correlating =['file_metadata|name','file_metadata|dst_type',
                        'file_metadata|request_id','file_metadata|src_type',
                        'file_metadata|md5','file_metadata|src_rse',
                        'file_metadata|dst_rse','file_metadata|activity',
                        'file_metadata|scope','file_metadata|dest_rse_id']
for el in drop_list_correlating:
    try:
        dataframe = dataframe.drop(el, axis=1)
    except:
        print('There was no such field:{}'.format(el))

dataframe = dataframe[dataframe.timestamp_tr_dlt != -1 ]

# from dataframe pop target column and transform to ndarray
target=dataframe.pop('timestamp_tr_dlt')

prepared_headers = list(dataframe.columns.values)
# prepared_headers

matrix_to_scale = dataframe.as_matrix()
# matrix_to_scale

#  scale between [0;1]
min_max_scaler = preprocessing.MinMaxScaler()
X_scalled = min_max_scaler.fit_transform(matrix_to_scale)

X = X_scalled
y = target.as_matrix()

log_f= lambda x: math.log(x+2)

y = list(map(log_f,y))

X_train, X_test, y_train, y_test = train_test_split( X, y, test_size=0.33, random_state=92)

# Fit a Random Forest 
model = xgb.XGBRegressor(n_estimators=200, subsample=0.7 , learning_rate=0.05)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

exp_2 = lambda x: math.exp(x) -2
y_test = list(map(exp_2,y_test))
y_pred = list(map(exp_2,y_pred)) 

# output=[]
# comparing real values to predicted
i = 0
with open('preds.csv', 'w') as ostream:
    for answ, pred in zip(y_test, y_pred):
        if  int(answ):
            row = '{},{}\n'.format(round(answ/1000.), round(pred/1000.))
            ostream.write(row)
