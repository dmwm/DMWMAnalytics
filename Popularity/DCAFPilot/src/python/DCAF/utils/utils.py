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
import bz2
import gzip
import time
import hashlib
import calendar
import datetime
import ConfigParser

def parse_config(filename):
    "Parse given config file into dict representation"
    config = ConfigParser.ConfigParser()
    config.read(filename)
    cdict = {}
    for section in config.sections():
        for pair in config.items(section):
            if  section in cdict:
                cdict[section].update(dict([pair]))
            else:
                cdict[section] = dict([pair])
    return cdict

class myGzipFile(gzip.GzipFile):
    def __enter__(self):
        "Context manager enter method"
        if self.fileobj is None:
            raise ValueError("I/O operation on closed GzipFile object")
        return self

    def __exit__(self, *args):
        "Context manager exit method"
        self.close()

def fopen(fin, mode='r'):
    "Return file descriptor for given file"
    if  fin.endswith('.gz'):
        stream = gzip.open(fin, mode)
        # if we use old python we switch to custom gzip class to support
        # context manager and with statements
        if  not hasattr(stream, "__exit__"):
            stream = myGzipFile(fin, mode)
    elif  fin.endswith('.bz2'):
        stream = bz2.BZ2File(fin, mode)
    else:
        stream = open(fin, mode)
    return stream

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

def dates(start_date, ndays=7, overlap=False):
    "Generate dates intervals starting from given date and using given step"
    today = calendar.timegm(datetime.date.today().timetuple())
    year = int(start_date[:4])
    month = int(start_date[4:6])
    date = int(start_date[6:8])
    past_date = calendar.timegm(datetime.date(year, month, date).timetuple())
    rows = [r for r in xrange(past_date, today, ndays*24*60*60)]
    for idx in xrange(0, len(rows)-1):
        if  overlap:
            date1 = rows[idx]
            date2 = rows[idx+1]
        else:
            date1 = rows[idx]
            date2 = rows[idx+1]-24*60*60
        yield date4unixtstamp(date1), date4unixtstamp(date2)

def newdate(start_date, step=1):
    "Generate new date from given date using given step"
    today = calendar.timegm(datetime.date.today().timetuple())
    year = int(start_date[:4])
    month = int(start_date[4:6])
    date = int(start_date[6:8])
    past_date = calendar.timegm(datetime.date(year, month, date).timetuple())
    return date4unixtstamp(past_date+24*60*60*step)

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

def yyyymmdd(tstamp):
    "Return date in dashboard format YYYYMMDD:"
    if  tstamp.find('-') != -1: # popdb time string
        year, month, day = tstamp.split('-')
        month = month if len(month) == 2 else '0%s' % month
        day = day if len(day) == 2 else '0%s' % day
        return '%s%s%s' % (year, month, day)
    elif len(str(tstamp)) == 10: # unix time
        return date4unixtstamp(unixtime)
    else:
        raise Exception("Unsupported time format '%s'" % tstamp)

def genkey(doc, salt="", truncate=0, method='md5'):
    "Generate hash for given doc and optional salt"
    func = getattr(hashlib, method)
    res = func(salt+doc).hexdigest()
    if  truncate:
        return int(res[len(res)-truncate:], 16)
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
