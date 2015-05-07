#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=
"""
File       : generic.py
Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
Description: Generic service module
"""
from __future__ import print_function

# system modules
import time

# package modules
from DCAF.utils.url_utils import getdata
from DCAF.utils.utils import genkey
from DCAF.core.storage import StorageManager

class GenericService(object):
    "Generic DCAF service class"
    def __init__(self, config=None, verbose=0):
        if  not config:
            config = {}
        self.name = 'generic'
        self.verbose = verbose
        self.storage = StorageManager(config)

    def fetch(self, url, params, cache=True):
        "Fetch data for given api"
        debug = 0
        data = "[]"
        if  cache:
            docid = genkey("url=%s params=%s" % (url, params))
            res = self.storage.fetch_one('cache', {'_id':docid})
            if  res and 'data' in res:
                if  self.verbose:
                    print("%s::fetch url=%s, params=%s, docid=%s" \
                            % (self.name, url, params, docid))
                return res['data']
        if  self.verbose:
            print("%s::fetch url=%s, params=%s" % (self.name, url, params))
            debug = self.verbose-1
        try:
            data = getdata(url, params, debug=debug)
        except Exception as exc:
            print(str(exc))
            for attempt in xrange(3):
                time.sleep(0.1)
                print("Attempt %s" % attempt)
                try:
                    data = getdata(url, params, debug=debug)
                    break
                except Exception as err:
                    print(str(err))
                    pass
        if  cache:
            self.storage.insert('cache', {'_id':docid, 'data': data, 'url': url, 'params': params})
        return data
