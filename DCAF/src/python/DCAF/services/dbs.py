#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=
"""
File       : dbs.py
Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
Description: DBS service module
"""

# system modules
import time
from   types import InstanceType

# package modules
import DCAF.utils.jsonwrapper as json
from DCAF.utils.url_utils import getdata
from DCAF.services.generic import GenericService
from DCAF.core.storage import StorageManager

class DBSService(GenericService):
    """
    Helper class to provide DBS service
    """
    def __init__(self, config=None):
        GenericService.__init__(self, config)
        self.name = 'dbs'
        self.url = 'https://cmsweb.cern.ch/dbs/prod/global/DBSReader/'
        self.storage = StorageManager(config)
        if  not self.storage.col('datasets').count():
            index_list = [('dataset', DESCENDING), ('rid', DESCENDING)]
            self.storage.create_indexes('datasets', index_list)
            self.update('datasets')
        if  not self.storage.col('releases').count():
            index_list = [('release', DESCENDING), ('rid', DESCENDING)]
            self.storage.create_indexes('releases', index_list)
            self.update('releases')

    def fetch(self, api, params=None):
        "Fetch data for given api"
        if  api == 'releases':
            url = '%s/releaseversions' % self.url
        else:
            url = '%s/%s' % (self.url, api)
        data = json.loads(super(DBSService, self).fetch(url, params))
        rid = 0
        if  api == 'releases':
            data = data[0]['release_version']
        for row in data:
            if  api == 'datasets':
                row['rid'] = rid
                yield row
            elif api == 'releases':
                rec = {'release':row, 'rid':rid}
                yield rec
            rid += 1

    def update(self, cname):
        "Update internal database with fresh snapshot of data"
        print "%s update %s" % (self.name, cname)
        if  cname == 'datasets':
            docs = self.fetch('datasets', {'dataset':'/*/*/*', 'detail':'true'})
            self.storage.insert('datasets', docs)
        elif cname == 'releases':
            docs = self.fetch('releases')
            self.storage.insert('releases', docs)

    def datasets(self):
        "Return list of datasets"
        spec = {}
        for row in self.storage.fetch('datasets', spec):
            yield row

    def releases(self):
        "Return list of releases"
        spec = {}
        for row in self.storage.fetch('releases', spec):
            yield row

    def dataset_info(self, dataset):
        "Return list of datasets"
        spec = {'dataset':dataset}
        res = [r for r in self.storage.fetch('datasets', spec)]
        if  not len(res):
            # TODO look-up dataset in other DBS instances
            return None
        else:
            return res[0]

    def dataset_release_versions(self, dataset):
        "Return dataset release versions"
        url = '%s/releaseversions' % self.url
        params = {'dataset':dataset}
        data = json.loads(super(DBSService, self).fetch(url, params))
        for ver in set(data[0]['release_version']):
            row = self.storage.fetch_one('releases', {'release':ver})
            yield row['rid']
