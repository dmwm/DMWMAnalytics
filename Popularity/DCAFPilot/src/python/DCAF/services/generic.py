#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=
"""
File       : generic.py
Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
Description: Generic service module
"""

# system modules
import time

# package modules
from DCAF.utils.url_utils import getdata

class GenericService(object):
    "Generic DCAF service class"
    def __init__(self, config=None, verbose=0):
        if  not config:
            config = {}
        self.name = 'generic'
        self.verbose = verbose

    def fetch(self, url, params):
        "Fetch data for given api"
        debug = 0
        data = []
        if  self.verbose:
            print "GenericService::fetch", url, params
            debug = self.verbose-1
        try:
            data = getdata(url, params, debug=debug)
        except Exception as exc:
            print str(exc)
            for attempt in xrange(3):
                time.sleep(0.1)
                print "Attempt %s" % attempt
                try:
                    data = getdata(url, params, debug=debug)
                    break
                except Exception as err:
                    print str(err)
                    pass
        return data
