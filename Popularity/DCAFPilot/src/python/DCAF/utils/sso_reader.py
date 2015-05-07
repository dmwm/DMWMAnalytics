#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=
# https://raw.githubusercontent.com/cms-sw/ib-scheduler/master/ws_sso_content_reader.py

from __future__ import print_function
import re
import os
import sys
import urllib
import urllib2
import httplib
import cookielib
import HTMLParser
import logging

from tempfile import NamedTemporaryFile
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

def getdata_old(url, ckey=None, cert=None, method='GET', postdata=None, debug=0):
    "Get data from SSO based data-service"
    if  not ckey and not cert:
        from DCAF.utils.utils import get_key_cert
        ckey, cert = get_key_cert()
    content = getContent(url, ckey, cert, postdata, method, debug)
    return content

def check_tool(tool):
    for idir in os.environ['PATH'].split(':'):
        fname = os.path.join(idir, tool)
        if  os.path.exists(fname):
            return True

def get_cern_sso_cookie(url, debug=0):
    """
    Check existance of certn-get-sso-cookie tool on a system, see
    http://linux.web.cern.ch/linux/docs/cernssocookie.shtml
    """
    cern_tool = 'cern-get-sso-cookie'
    if  check_tool(cern_tool):
        cookiefile = NamedTemporaryFile(delete=False)
        cmd = '%s --krb -r -u "%s" -o %s' % (cern_tool, url, cookiefile.name)
        if  debug:
            print("Get CERN SSO cookies", cmd)
        os.system(cmd)
        cookie = cookielib.MozillaCookieJar(cookiefile.name)
        cookie.load()
        cookiefile.close()
        os.unlink(cookiefile.name)
        return cookie

def getdata_new(url, params, headers=None, ckey=None, cert=None, debug=0):
    "Fetch data for given url and set of parameters"
    if  params:
        url += '?%s' % urllib.urlencode(params, doseq=True)
    if  debug:
        print("getdata:url", url)
    req = urllib2.Request(url)
    if  headers == None:
        headers = {'Accept': 'application/json'}
    if  headers:
        for key, val in headers.items():
            req.add_header(key, val)

    handler = HTTPSClientAuthHandler(ckey, cert)
    cookie = get_cern_sso_cookie(url, debug)
    if  cookie:
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie), handler)
    else:
        opener  = urllib2.build_opener(handler)
    urllib2.install_opener(opener)
    data = urllib2.urlopen(req)
    return data.read()

def getdata(url, params=None, headers=None, ckey=None, cert=None, debug=0, method='GET', postdata=None):
    """
    Wrapper around old/new implementation of getdata.
    The original implementation is pure python based, but it does not
    work with proxy files, while new implementation uses cern-get-sso-cookie
    tool to get cookie and then pass it into python library for processing.
    """
    if  check_tool('cern-get-sso-cookie'):
        return getdata_new(url, params, ckey=ckey, cert=cert, debug=debug)
    else:
        return getdata_old(url, ckey, cert, method, postdata, debug)
