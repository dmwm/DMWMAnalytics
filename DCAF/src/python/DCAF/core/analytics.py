#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=
"""
File       : DCAF.py
Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
Description: Generic module to perform various analytics tasks
"""

# system modules
import os
import sys
import ConfigParser

# package modules
from DCAF.core.storage import StorageManager
from DCAF.services.sitedb import SiteDBService
from DCAF.services.dbs import DBSService
from DCAF.services.phedex import PhedexService
from DCAF.services.popdb import PopDBService
from DCAF.utils.utils import genkey

def parse_config(filename):
    "Parse given config file into dict representation"
    config = ConfigParser.ConfigParser()
    config.read(filename)
    cdict = {}
    for section in config.sections():
        for pair in config.items(section):
            cdict[section] = dict([pair])
    return cdict

class DCAF(object):
    def __init__(self, configfile):
        "Main module"
        self.config = parse_config(configfile)
        self.storage = StorageManager(self.config)
        self.sitedb = SiteDBService(self.config)
        self.dbs = DBSService(self.config)
        self.popdb = PopDBService(self.config)
        self.phedex = PhedexService(self.config)
        self.salt = self.config.get('core', {}).get('salt', 'secret sauce')

    def fetch(self, doc):
        """
        Fetch method retrieves data from data-provide and store them into
        internal data storage.
        """
        source = doc.get('source', None)
        params = doc.get('params', {})
        print "Fetch data from %s(%s)" % (source, params)
        if  source == 'sitedb':
            for item in self.sitedb.fetch('people', {}):
                print item
                break

    def dataframe(self, timeframe=None, dformat='csv'):
        "Form a dataframe from various CMS data-providers"
        headers = ['dataset','primds','type','created','release','site','naccess','nusers','totcpu']
        if  dformat == 'csv':
            yield ','.join(headers)
        # get list of popular datasets in certain time frame
        res = self.popdb.dataset_stat(timeframe[0], timeframe[1])
        for row in res:
            dataset = row['dataset']
            naccess = row['naccess']
            nusers = row['nusers']
            totcpu = row['totcpu']
            row = self.dbs.dataset_info(dataset)
            if  row:
                versions = [r for r in self.dbs.dataset_release_versions(dataset)]
                for rel in versions:
                    sites = [r for r in self.phedex.sites(dataset)]
                    for site in sites:
                        dataset_id = row['rid']
                        created_dn = row['create_by']
                        dtype = genkey(row['primary_ds_type'], self.salt, 5)
                        prim = genkey(row['primary_ds_name'], self.salt, 5)
                        if  dformat=='csv':
                            rec = [dataset_id,prim,dtype,self.sitedb.dnid(created_dn),\
                                    rel,site,naccess,nusers,totcpu]
                            res = [str(r) for r in rec]
                            yield ','.join(res)

    def export(self, dformat):
        "Export analytics dataframe into provided data format"
        print "Export dataframe into %s format" % dformat.lower()
        if  dformat.lower() == 'csv':
            print "Do CSV export"
            headers = []
            for row in self.dataframe():
                if  not headers:
                    headers = row
                    yield ','.join(headers)
                    continue
                yield ','.join(row)
        elif  dformat.lower() == 'vw':
            print "Do vw export"
        else:
            raise NotImplemented
def test():
    configfile = 'etc/analytics.cfg'
    mgr = DCAF(configfile)
    time1 = '2012-6-26'
    time2 = '2012-7-3'
    for row in mgr.dataframe(timeframe=[time1, time2], dformat='csv'):
        print row

if __name__ == '__main__':
    test()
