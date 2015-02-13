#!/usr/bin/env python

import os
import sys
import time
import json
import types
import urllib
import urllib2
import httplib

# package modules
from DCAF.utils.utils import get_key_cert

VER=sys.version_info
if  VER[0] == 2 and VER[1] == 7 and VER[2] >= 9:
    # disable SSL verification, since it is default in python 2.7.9
    # and many CMS services do not verify SSL cert.
    # https://www.python.org/dev/peps/pep-0476/
    import ssl
    ssl._create_default_https_context = ssl._create_unverified_context

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

def getdata(url, params, headers=None, ckey=None, cert=None, debug=0):
    "Fetch data for given url and set of parameters"
    if  params:
        url += '?%s' % urllib.urlencode(params, doseq=True)
    if  debug:
        print "getdata:url", url
    req = urllib2.Request(url)
    if  headers == None:
        headers = {'Accept': 'application/json'}
    if  headers:
        for key, val in headers.items():
            req.add_header(key, val)

    ckey, cert = get_key_cert()
    handler = HTTPSClientAuthHandler(ckey, cert, debug)
    opener  = urllib2.build_opener(handler)
    urllib2.install_opener(opener)
    data = urllib2.urlopen(req)
    #print len(json.load(data))
    return data.read()
