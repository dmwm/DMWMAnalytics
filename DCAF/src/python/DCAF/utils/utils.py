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
