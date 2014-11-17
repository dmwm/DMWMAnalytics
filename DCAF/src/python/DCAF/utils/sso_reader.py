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

DEFAULT_CERT_PATH="~/.globus/usercert.pem"
DEFAULT_KEY_PATH="~/.globus/userkey.pem"

def setDefaultCertificate(cert, key):
    DEFAULT_CERT_PATH=cert
    DEFAULT_KEY_PATH=key

class HTTPSClientAuthHandler(urllib2.HTTPSHandler):  
    def __init__(self):  
        urllib2.HTTPSHandler.__init__(self)  
        self.key = realpath(expanduser(DEFAULT_KEY_PATH))
        self.cert = realpath(expanduser(DEFAULT_CERT_PATH))

    def https_open(self, req):  
        return self.do_open(self.getConnection, req)  

    def getConnection(self, host, timeout=300):  
        return httplib.HTTPSConnection(host, key_file=self.key, cert_file=self.cert)

def _getResponse(opener, url, data=None, method="GET", debug=0):
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

def getContent(target_url, post_data=None, method="GET", debug=0):
    cert_path = expanduser(DEFAULT_CERT_PATH)
    key_path = expanduser(DEFAULT_KEY_PATH)
    cookie = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie), HTTPSClientAuthHandler())
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

def getdata(url, ckey, cert, method='GET', postdata=None, debug=0):
    setDefaultCertificate(cert, ckey)
    content = getContent(url, postdata, method, debug)
    return content
