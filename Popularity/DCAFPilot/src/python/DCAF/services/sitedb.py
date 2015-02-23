#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=
"""
File       : sitedb.py
Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
Description: SiteDB service module
"""

# system modules
import time
from   types import InstanceType

# package modules
import DCAF.utils.jsonwrapper as json
from DCAF.utils.utils import genkey
from DCAF.services.generic import GenericService

def rowdict(columns, row):
    """Convert given row list into dict with column keys"""
    robj = {}
    for key, val in zip(columns, row):
        robj.setdefault(key, val)
    return robj
    
def sitedb_parser(source):
    """SiteDB parser"""
    if  isinstance(source, str) or isinstance(source, unicode):
        data = json.loads(source)
    elif isinstance(source, InstanceType) or isinstance(source, file):
        # got data descriptor
        try:
            data = json.load(source)
        except Exception as exc:
            print_exc(exc)
            source.close()
            raise
        source.close()
    else:
        data = source
    if  not isinstance(data, dict):
        raise Exception('Wrong data type, %s' % type(data))
    if  'desc' in data:
        columns = data['desc']['columns']
        for row in data['result']:
            yield rowdict(columns, row)
    else:
        for row in data['result']:
            yield row

def user_data(username, sitedb_dict):
    "Find user data in SiteDB dict"
    columns = sitedb_dict['desc']['columns']
    for row in sitedb_dict['result']:
        idx = columns.index('username')
        if  row[idx] == username:
            return dict(zip(columns, row))

class SiteDBService(GenericService):
    """
    Helper class to provide DBS service
    """
    def __init__(self, config=None, verbose=0):
        GenericService.__init__(self, config, verbose)
        self.name = 'sitedb'
        self.url = config['services'][self.name]

    def fetch(self, api, params=None):
        "Fetch data for given api"
        if  api == 'sites':
            api = 'site-names'
        url = '%s/%s' % (self.url, api)
        data = super(SiteDBService, self).fetch(url, params)
        for row in sitedb_parser(data):
            if  api == 'people':
                rid = genkey(str(row['dn']), truncate=5)
                rec = {'dn':row['dn'], 'rid':rid}
            if  api == 'site-names':
                rid = genkey(str(row['alias']), truncate=5)
                rec = {'site':row['alias'], 'rid':rid}
            yield rec

    def update(self, cname):
        "Update internal database with fresh snapshot of data"
        if  self.verbose:
            print "%s update %s" % (self.name, cname)
        self.storage.cleanup(cname)
        docs = self.fetch(cname)
        self.storage.insert(cname, docs)

    def dnid(self, dn):
        "Return DN id from dn database"
        spec = {'dn':dn}
        res = [r for r in self.storage.fetch('people', spec)]
        if  not res:
            rid = self.storage.count('people', {})+1
            self.storage.insert('people', [{'dn':dn,'rid':rid}])
            return rid
        doc = [r for r in res][0]
        return doc['rid']

    def siteid(self, site):
        "Return site id from site database"
        spec = {'site':site}
        res = [r for r in self.storage.fetch('sites', spec)]
        if  not res:
            rid = self.storage.count('sites', {})+1
            self.storage.insert('sites', [{'site':dn,'rid':rid}])
            return rid
        doc = [r for r in res][0]
        return doc['rid']

