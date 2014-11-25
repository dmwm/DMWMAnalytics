#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=
"""
File       : dashboard.py
Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
Description: Dashboard service module
"""

# system modules
import time
from   types import InstanceType

# package modules
import DCAF.utils.jsonwrapper as json
from DCAF.utils.utils import get_key_cert, dashboard_date
from DCAF.services.generic import GenericService
from DCAF.services.sitedb import SiteDBService
from DCAF.core.storage import StorageManager

class DashboardService(GenericService):
    """
    Helper class to provide Dashboard service
    """
    def __init__(self, config=None, verbose=0):
        GenericService.__init__(self, config, verbose)
        self.name = 'dashboard'
        self.url = "http://dashb-cms-job.cern.ch/dashboard/request.py"
        self.storage = StorageManager(config)
        self.ckey, self.cert = get_key_cert()
        self.sitedb = SiteDBService(config)

    def fetch(self, api, params=None):
        "Fetch data for given api"
        url = '%s/%s' % (self.url, api)
        data = json.loads(super(DashboardService, self).fetch(url, params))
        for row in data['jobs']:
            yield row

    def update(self, cname):
        "Update internal database with fresh snapshot of data"
        if  self.verbose:
            print "%s update %s" % (self.name, cname)
        self.storage.cleanup(cname)
        docs = self.fetch(cname)
        self.storage.insert(cname, docs)

    def dataset_info(self, dataset, date1, date2, site='all', jobtype='analysis'):
        "Retrieve dataset info for given time frame and (optional) site name"
        api = 'jobefficiencyapi'
        params = {'start':dashboard_date(date1),
                  'end':dashboard_date(date2),
                  'site':site, 'dataset':dataset, 'type':jobtype}
        res = self.fetch(api, params)
        cpu = 0
        wct = 0
        nevt = 0
        for row in res:
            cpu += row['WrapCPU']
            wct += row['WrapWC']
            nevt += row['NEventsProcessed']
#            siteid = self.sitedb.siteid(row['VOName'])
#            rec = dict(cpu=row['WrapCPU'], wct=row['WrapWC'],
#                    nevt=row['NEventsProcessed'], site=siteid)
#            yield rec
        return {'cpu':int(round(cpu)), 'wct': int(round(wct)), 'nevt': nevt}

def test():
    dataset="/QCD_Pt-1000to1400_Tune4C_13TeV_pythia8/Spring14dr-castor_PU20bx25_POSTLS170_V5-v1/AODSIM"
    config = {'mongodb':{'dburi':'mongodb://localhost:8230'}, 'db':{'name':'analytics'}}
    mgr = DashboardService(config)
#    for row in mgr.dataset_info(dataset, '20141001', '20141031'):
#        print row
    row = mgr.dataset_info(dataset, '20141001', '20141031')
    print row
if __name__ == '__main__':
    test()
