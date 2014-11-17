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
from   types import InstanceType

# package modules
import DCAF.utils.jsonwrapper as json
from DCAF.utils.sso_reader import getdata
from DCAF.utils.utils import get_key_cert
from DCAF.services.generic import GenericService
from DCAF.core.storage import StorageManager

class PopDBService(GenericService):
    """
    Helper class to provide Popularity service
    """
    def __init__(self, config=None):
        GenericService.__init__(self, config)
        self.name = 'popdb'
        self.url = 'https://cms-popularity.cern.ch/popdb/popularity/'
        self.storage = StorageManager(config)
        self.ckey, self.cert = get_key_cert()

    def fetch(self, api, params=None):
        "Fetch data for given api"
        url = '%s/%s' % (self.url, api)
        data = json.loads(getdata(url, self.ckey, self.cert))
        for row in data['DATA']:
            yield row

    def update(self, cname):
        "Update internal database with fresh snapshot of data"
        print "%s update %s" % (self.name, cname)
        docs = self.fetch(cname)
        self.storage.insert(cname, docs)

    def dataset_stat(self, time1, time2):
        "Retrieve dataset popularity info for given time frame"
        api = 'DSStatInTimeWindow'
        params = {'tstart':time1, 'tstop':time2}
        res = self.fetch(api, params)
        for row in res:
            rec = dict(naccess=row['NACC'], totcpu=row['TOTCPU'],
                    nusers=row['NUSERS'], dataset=row['COLLNAME'])
            yield rec

