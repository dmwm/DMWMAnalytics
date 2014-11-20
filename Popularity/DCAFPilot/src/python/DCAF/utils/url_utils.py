#!/usr/bin/env python

import os
import sys
import time
import json
import types
import urllib
import urllib2
import httplib

class HTTPSClientAuthHandler(urllib2.HTTPSHandler):
    """
    Simple HTTPS client authentication class based on provided 
    key/ca information
    """
    def __init__(self, key=None, cert=None, level=0):
        if  level:
            urllib2.HTTPSHandler.__init__(self, debuglevel=1)
        else:
            urllib2.HTTPSHandler.__init__(self)
        self.key = key
        self.cert = cert

    def https_open(self, req):
        """Open request method"""
        return self.do_open(self.get_connection, req)

    def get_connection(self, host, timeout=300):
        """Connection method"""
        if  self.cert:
            return httplib.HTTPSConnection(host, key_file=self.key,
                                                cert_file=self.cert)
        return httplib.HTTPSConnection(host)

def getdata(url, params, ckey=None, cert=None, debug=0):
    "Fetch data for given url and set of parameters"
    if  params:
        url += '?%s' % urllib.urlencode(params, doseq=True)
    req = urllib2.Request(url)
    headers = {'Accept': 'application/json;text/json'}
    if  headers:
        for key, val in headers.items():
            req.add_header(key, val)

    if  not ckey:
        ckey = os.path.join(os.environ['HOME'], '.globus/userkey.pem')
    if  not cert:
        cert = os.path.join(os.environ['HOME'], '.globus/usercert.pem')

    handler = HTTPSClientAuthHandler(ckey, cert, debug)
    opener  = urllib2.build_opener(handler)
    urllib2.install_opener(opener)
    data = urllib2.urlopen(req)
    #print len(json.load(data))
    return data.read()

def test():
    # new SiteDB
    api = 'people'
    url = 'https://cmsweb.cern.ch/sitedb/data/prod/' + api
    params = {}

    # test dbs3
    #dbs = "https://cmsweb.cern.ch/dbs/prod/global/DBSReader"
    #url = dbs+"/datasets" + "?dataset=/ZMM*/*/GEN-SIM&detail=True"
    data = getdata(url, params)
    print data

if __name__ == '__main__':
    test()

