#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=

"""
Set of utilities used in pyspark model
"""

__author__ = "Kipras Kancys"

import datetime

def construct_date(date):
    "Constructs datetime.date object from string of type: yearmonthday e.g. 20160805"
    year = int(date[:4])
    month = int(date[4:6])
    day = int(date[6:8])
    return datetime.date(year, month, day)

def get_start_date(train_end):
    "Adds a day to the date. That is needed to make a week_start date from week_end date. Returns string"
    date = construct_date(train_end) + datetime.timedelta(days=1)
    return date.strftime('%Y%m%d')

def add_days(start_date,  ndays):
    "Adds ndays to the date. Returns both dates"
    next_date = start_date + datetime.timedelta(days=ndays)
    return start_date, next_date

def get_file_names(train_start, train_end, ndays):
    "Makes a list of files that covers duration of start and end dates. File format: dataframe-20160805-20160812.csv.gz"
    begin_date = construct_date(str(train_start))
    end_date = construct_date(str(train_end))
    ndays = ndays - 1
    file_names = []

    if (begin_date > end_date):
        print("Start date (" + str(begin_date) + ") is earlier than end date (" + str(end_date) + ")")
    else:
        while (add_days(begin_date, ndays-1)[1] <  end_date):
            beginDate, nextDate = add_days(begin_date, ndays)
            file_names.append("dataframe-"+beginDate.strftime('%Y%m%d')+"-"+nextDate.strftime('%Y%m%d')+".csv.gz")
            begin_date = nextDate +  datetime.timedelta(days=1)

	return file_names
