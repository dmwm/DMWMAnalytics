#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=

"""
General set of useful utilities
"""

__author__ = "Valentin Kuznetsov"

# system modules
import os
import re
import sys
import time
import hashlib
import calendar
import datetime

def dates_from_today(ndays=7):
    "Return unix timestamps for provided ndays from today"
    today_tstamp = calendar.timegm(datetime.date.today().timetuple())
    return today_tstamp-ndays*24*60*60, today_tstamp

def unixtstamp(date):
    "Return unix timestamp for prodided date format YYYYMMDD"
    year, mm, dd = int(date[:4]), int(date[4:6]), int(date[6:])
    tstamp = calendar.timegm(datetime.date(year, mm, dd).timetuple())
    return tstamp

def ndays(date1, date2):
    "Return number of days between two dates"
    diff = abs(unixtstamp(date1)-unixtstamp(date2))
    return round(diff/(24*60*60))

def date4unixtstamp(unixtime):
    "Return date in format YYYYMMDD for given unix timestamp"
    return time.strftime("%Y%m%d", time.gmtime(unixtime))

def dates(start_date, ndays=7):
    "Generate dates intervals starting from given date and using given step"
    today = calendar.timegm(datetime.date.today().timetuple())
    year = int(start_date[:4])
    month = int(start_date[4:6])
    date = int(start_date[6:8])
    past_date = calendar.timegm(datetime.date(year, month, date).timetuple())
    rows = [r for r in xrange(past_date, today, ndays*24*60*60)]
    for idx in xrange(0, len(rows)-1):
        yield date4unixtstamp(rows[idx]), date4unixtstamp(rows[idx+1])

def popdb_date(tstamp):
    "Return date in popDB format YYYY-M-D"
    if  tstamp.find('-') != -1:
        return tstamp
    if  len(tstamp)==8: # YYYYMMDD format
        year = tstamp[:4]
        month = int(tstamp[4:6])
        day = int(tstamp[6:8])
        return '%s-%s-%s' % (year, month, day)
    return tstamp

def dashboard_date(tstamp):
    "Return date in dashboard format YY-M-DD:"
    if  tstamp.find('-') != -1:
        return tstamp
    if  len(tstamp)==8: # YYYYMMDD format
        year = tstamp[2:4]
        month = tstamp[4:6]
        day = tstamp[6:8]
        return '%s-%s-%s' % (year, month, day)
    return tstamp

def genkey(doc, salt="", truncate=0, method='md5'):
    "Generate hash for given doc and optional salt"
    func = getattr(hashlib, method)
    res = func(salt+doc).hexdigest()
    if  truncate:
        return res[len(res)-truncate:]
    return res

def get_key_cert():
    """
    Get user key/certificate
    """
    key  = None
    cert = None
    globus_key  = os.path.join(os.environ['HOME'], '.globus/userkey.pem')
    globus_cert = os.path.join(os.environ['HOME'], '.globus/usercert.pem')
    if  os.path.isfile(globus_key):
        key  = globus_key
    if  os.path.isfile(globus_cert):
        cert  = globus_cert

    # First presendence to HOST Certificate, RARE
    if  'X509_HOST_CERT' in os.environ:
        cert = os.environ['X509_HOST_CERT']
        key  = os.environ['X509_HOST_KEY']

    # Second preference to User Proxy, very common
    elif 'X509_USER_PROXY' in os.environ:
        cert = os.environ['X509_USER_PROXY']
        key  = cert

    # Third preference to User Cert/Proxy combinition
    elif 'X509_USER_CERT' in os.environ:
        cert = os.environ['X509_USER_CERT']
        key  = os.environ['X509_USER_KEY']

    # Worst case, look for cert at default location /tmp/x509up_u$uid
    elif not key or not cert:
        uid  = os.getuid()
        cert = '/tmp/x509up_u'+str(uid)
        key  = cert

    if  not os.path.exists(cert):
        raise Exception("Certificate PEM file %s not found" % key)
    if  not os.path.exists(key):
        raise Exception("Key PEM file %s not found" % key)

    return key, cert
