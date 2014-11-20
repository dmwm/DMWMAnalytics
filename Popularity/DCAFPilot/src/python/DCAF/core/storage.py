#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=
"""
File       : storage.py
Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
Description: analytics storage manager
"""

# system modules
import os
import sys
import itertools

# monogo db modules
from pymongo import MongoClient, DESCENDING, ASCENDING
from pymongo.errors import ConnectionFailure, InvalidOperation, DuplicateKeyError, AutoReconnect
from bson.objectid import ObjectId
from bson.code import Code
from bson.errors import InvalidDocument

def create_indexes(coll, index_list):
    """
    Create indexes for provided collection/index_list and
    ensure that they are in place
    """
    index_info = coll.index_information().values()
    for pair in index_list:
        index_exists = 0
        for item in index_info:
            if  item['key'] == [pair]:
                index_exists = 1
        if  not index_exists:
            try:
                if  isinstance(pair, list):
                    coll.create_index(pair)
                else:
                    coll.create_index([pair])
            except Exception as exp:
                print_exc(exp)
        try:
            if  isinstance(pair, list):
                coll.ensure_index(pair)
            else:
                coll.ensure_index([pair])
        except Exception as exp:
            print_exc(exp)

class StorageManager(object):
    def __init__(self, config):
        self.config  = config
        for mfield in ['mongodb', 'db']:
            if  mfield not in config:
                raise Exception('No section %s in config' % mfield)
        self.dburi   = config['mongodb'].get('dburi', '')
        self.cache_size = config['mongodb'].get('bulkupdate_size', 1000)
        self.dbname  = config['db'].get('name', 'analytics')

        # Initialize MongoDB connection
        msg = "%s@%s" % (self.dburi, self.dbname)
        self.dbinst = MongoClient(host=self.dburi)

        # Initialize analytics collection

    def indexes(cname, index_list):
        "Create indexes in given collection for given index list"
#        index_list = [('name', DESCENDING)]
        create_indexes(self.col(cname), index_list)

    def __repr__(self):
        "Show StorageManager representation"
        return "<%s@%s %s>" % (self.dburi, self.dbname, self.dbinst)

    def col(self, cname):
        "col property provides access to collection"
        return self.dbinst[self.dbname][cname]

    def insert(self, cname, docs):
        "Insert docs into given collection"
        size = self.cache_size
        inserted = 0
        try:
            while True:
                nres = self.col(cname).insert(itertools.islice(docs, size))
                if  nres and isinstance(nres, list):
                    inserted += len(nres)
                    if  len(nres) < size:
                        break
                else:
                    break
        except InvalidDocument as exp:
            msg = "Caught bson error: " + str(exp)
            print msg
        except InvalidOperation:
            pass
        except DuplicateKeyError as err:
            if  not isinstance(docs, list):
                raise err
        return inserted

    def fetch(self, cname, spec):
        "Fetch documents from internal storage for given spec query"
        for doc in self.col(cname).find(spec):
            yield doc

    def fetch_one(self, cname, spec):
        "Fetch documents from internal storage for given spec query"
        return self.col(cname).find_one(spec)

    def count(self, cname, spec):
        "Fetch documents from internal storage for given spec query"
        return self.col(cname).find(spec).count()

    def cleanup(self, cname):
        "Cleanup given collection"
        return self.col(cname).remove({})
