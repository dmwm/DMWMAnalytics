#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=
"""
File       : popdb.py
Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
Description: PopDB service module
"""

# system modules
import time
import urllib
from   types import InstanceType

# package modules
import DCAF.utils.jsonwrapper as json
from DCAF.utils.sso_reader import sso_getdata
from DCAF.utils.url_utils import getdata
from DCAF.utils.utils import get_key_cert, genkey
from DCAF.services.generic import GenericService

class PopDBService(GenericService):
    """
    Helper class to provide Popularity service
    """
    def __init__(self, config=None, verbose=0):
        GenericService.__init__(self, config, verbose)
        self.name = 'popdb'
        self.url = config['services'][self.name]
        self.ckey, self.cert = get_key_cert()

    def fetch(self, api, params=None):
        "Fetch data for given api"
        url = '%s/%s?%s' % (self.url, api, urllib.urlencode(params, doseq=True))
        docid = genkey("url=%s params=%s" % (url, params))
        res = self.storage.fetch_one('cache', {'_id':docid})
        if  res and 'data' in res:
            if  self.verbose:
                print "%s::fetch url=%s, params=%s, docid=%s" \
                        % (self.name, url, params, docid)
            data = res['data']
        else:
            if  self.verbose:
                print "%s::fetch url=%s, params=%s" % (self.name, url, params)
            # NOTE: popularity DB has two different access points, one
            # within CERN network and out outside. The former does not require
            # authentication, while later passes through CERN SSO.
            # The following block reflects this, in a future, when popularity DB
            # will move into cmsweb domain we'll no longer need it
            if  self.url.find('cms-popularity-prod.cern.ch') != -1:
                data = getdata(url, ckey=self.ckey, cert=self.cert, debug=self.verbose)
            else:
                data = sso_getdata(url, ckey=self.ckey, cert=self.cert, debug=self.verbose)
            self.storage.insert('cache', {'_id':docid, 'data': data, 'url': url, 'params': params})
        data = json.loads(data)
        for row in data['DATA']:
            yield row

    def update(self, cname):
        "Update internal database with fresh snapshot of data"
        if  self.verbose:
            print "%s update %s" % (self.name, cname)
        self.storage.cleanup(cname)
        docs = self.fetch(cname)
        self.storage.insert(cname, docs)

    def dataset_stat(self, time1, time2):
        "Retrieve dataset popularity info for given time frame"
        api = 'DSStatInTimeWindow'
        params = {'tstart':time1, 'tstop':time2}
        res = self.fetch(api, params)
        for row in res:
            rec = dict(naccess=float(row['NACC']),
                    totcpu=float(row['TOTCPU']),
                    nusers=float(row['NUSERS']),
                    rnaccess=float(row['RNACC']),
                    rtotcpu=float(row['RTOTCPU']),
                    rnusers=float(row['RNUSERS']),
                    dataset=row['COLLNAME'])
            yield rec

