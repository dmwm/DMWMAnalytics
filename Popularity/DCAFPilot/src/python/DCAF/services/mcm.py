#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=
"""
File       : mcm.py
Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
Description: mcm service module
"""
from __future__ import print_function

# system modules
import time
from   types import InstanceType

# package modules
import DCAF.utils.jsonwrapper as json
from DCAF.utils.utils import get_key_cert
from DCAF.services.generic import GenericService
from DCAF.services.sitedb import SiteDBService

class mcmService(GenericService):
    """
    Helper class to provide mcm service
    """
    def __init__(self, config=None, verbose=0):
        GenericService.__init__(self, config, verbose)
        self.name = 'mcm'
        self.url = config['services'][self.name]
        self.ckey, self.cert = get_key_cert()

    def fetch(self, api, params=None):
        "Fetch data for given api"
        url = '%s/%s' % (self.url, api)
        data = json.loads(super(mcmService, self).fetch(url, params))
        yield data['results']

    def update(self, cname):
        "Update internal database with fresh snapshot of data"
        if  self.verbose:
            print("%s update %s" % (self.name, cname))
        self.storage.cleanup(cname)
        docs = self.fetch(cname)
        self.storage.insert(cname, docs)

    def prepid(self, prepid):
        "Retrieve prepid info for given prepid"
        api = 'get/%s' % prepid
        params = {}
        res = self.fetch(api, params)
        for row in res:
            rec = dict(notes=row['notes'], pwg=row['pwg'],
                    campaign=row['member_of_campaign'],
                    mcdbid=row['mcdb_id'])
            yield rec

def test():
    prepid = 'HIG-Summer12-01312'
    config = {'mongodb':{'dburi':'mongodb://localhost:8230'}, 'db':{'name':'analytics'}}
    mgr = mcmService(config)
    for row in mgr.prepid(prepid):
        print(row)
if __name__ == '__main__':
    test()
