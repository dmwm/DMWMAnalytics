#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=
"""
File       : phedex.py
Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
Description: Phedex service module
"""

# system modules
import time
from   types import InstanceType

# package modules
import DCAF.utils.jsonwrapper as json
from DCAF.utils.url_utils import getdata
from DCAF.services.generic import GenericService

class PhedexService(GenericService):
    """
    Helper class to provide Phedex service
    """
    def __init__(self, config=None, verbose=0):
        if  not config:
            config = {}
        GenericService.__init__(self, config, verbose)
        self.name = 'phedex'
        self.url = config['services'][self.name]

    def fetch(self, api, params=None):
        "Fetch data for given api"
        if  api == 'replicas':
            url = '%s/blockReplicas' % self.url
        else:
            url = '%s/%s' % (self.url, api)
        try:
            data = json.loads(super(PhedexService, self).fetch(url, params))
            rid = 0
            for row in data['phedex']['block']:
                for repl in row['replica']:
                    node = repl['node']
                    yield node
                rid += 1
        except Exception as exc:
            print str(exc)
            pass

    def sites(self, dataset):
        "Return list of datasets"
        spec = {'dataset':dataset}
        res = set([r for r in self.fetch('replicas', spec)])
        for node in res:
#            row = self.storage.fetch_one('sites', {'site':node})
#            if  row:
#                yield row['site']
            yield node

def test():
    uri = 'mongodb://localhost:8230'
    mgr=PhedexService({'mongodb':{'dburi':uri}, 'db':{'name':'analytics'}})
    dataset = '/GenericTTbar/HC-CMSSW_7_0_4_START70_V7-v1/GEN-SIM-RECO'
    res = mgr.sites(dataset)
    sites = set([r for r in res])
    print sites
if __name__ == '__main__':
    test()
