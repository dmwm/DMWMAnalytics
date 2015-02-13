#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=
# https://raw.githubusercontent.com/cms-sw/ib-scheduler/master/ws_sso_content_reader.py

import re
import os
import sys
import urllib
import urllib2
import httplib
import cookielib
import HTMLParser
import logging

from os.path import expanduser, dirname, realpath

VER=sys.version_info
if  VER[0] == 2 and VER[1] == 7 and VER[2] >= 9:
    # disable SSL verification, since it is default in python 2.7.9
    # and many CMS services do not verify SSL cert.
    # https://www.python.org/dev/peps/pep-0476/
    import ssl
    ssl._create_default_https_context = ssl._create_unverified_context

class HTTPSClientAuthHandler(urllib2.HTTPSHandler):  
    def __init__(self, ckey, cert):
        "HTTPS client authentication handler to Establish HTTPS connection"
        urllib2.HTTPSHandler.__init__(self)  
        self.key = ckey
        self.cert = cert

    def https_open(self, req):  
        "Establish HTTPS connection"
        return self.do_open(self.getConnection, req)  

    def getConnection(self, host, timeout=300):  
        "Establish HTTPS connection"
        return httplib.HTTPSConnection(host, key_file=self.key, cert_file=self.cert)

def _getResponse(opener, url, data=None, method="GET", debug=0):
    "Get response for given url opener and data"
    request = urllib2.Request(url)
    if data:
        request.add_data(data)
    if method != "GET":
        request.get_method = lambda : method
    response = opener.open(request)
    if  debug:
        print("Code: %s\n" % response.code)
        print("Headers: %s\n" % response.headers)
        print("Msg: %s\n" % response.msg)
        print("Url: %s\n" % response.url)
    return response

def getSSOCookie(opener, target_url, cookie, debug):
    "Get SSO cookies"
    opener.addheaders = [('User-agent', 'curl-sso-certificate/0.0.2')] #in sync with cern-get-sso-cookie tool
    parentUrl = target_url
    url = urllib2.unquote(_getResponse(opener, parentUrl).url)
    content = _getResponse(opener, url).read()
    ret = re.search('<form .+? action="(.+?)">', content)
    if ret == None:
        raise Exception("error: The page doesn't have the form with adfs url, check 'User-agent' header")
    url = urllib2.unquote(ret.group(1))
    h = HTMLParser.HTMLParser()
    post_data_local = []
    for match in re.finditer('input type="hidden" name="([^"]*)" value="([^"]*)"', content):
        post_data_local += [(match.group(1), h.unescape(match.group(2)))]
  
    if not post_data_local:
        raise Exception("error: The page doesn't have the form with security attributes, check 'User-agent' header")
    _getResponse(opener, url, urllib.urlencode(post_data_local), debug=debug).read()

def getContent(target_url, ckey, cert, post_data=None, method="GET", debug=0):
    "helper function to get data content from given url via CERN SSO authentication"
    cookie = cookielib.CookieJar()
    httshandler = HTTPSClientAuthHandler(ckey, cert)
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie), httshandler)
    if  debug:
        print("The return page is sso login page, will request cookie.")
    hasCookie = False
    # if the access gave an exception, try to get a cookie
    try:
        getSSOCookie(opener, target_url, cookie, debug)
        hasCookie = True 
        result = _getResponse(opener, target_url, post_data, method, debug).read()
    finally:
        if hasCookie:
            try:
                _getResponse(opener, "https://login.cern.ch/adfs/ls/?wa=wsignout1.0").read()
            except:
                print("Error, could not logout correctly from server") 
    return result

def getdata(url, ckey=None, cert=None, method='GET', postdata=None, debug=0):
    "Get data from SSO based data-service"
    if  not ckey and not cert:
        from DCAF.utils.utils import get_key_cert
        ckey, cert = get_key_cert()
    content = getContent(url, ckey, cert, postdata, method, debug)
    return content
