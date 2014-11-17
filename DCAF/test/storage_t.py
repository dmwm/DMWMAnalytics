#!/usr/bin/env python
#pylint: disable-msg=C0301,C0103

"""
Unit test for StorageManager class
"""

import os
import re
import time
import unittest

from pymongo import MongoClient

from CMSCompAnalytics.core.storage import StorageManager

class testStorageManager(unittest.TestCase):
    """
    A test class for the StorageManager class
    """
    def setUp(self):
        "set up connection"
        self.dburi = 'mongodb://localhost:8230'
        self.dbname = 'test_analytics'
        self.config = {'mongodb':{'dburi':self.dburi}, 'db':{'name':self.dbname}}
        self.storage = StorageManager(self.config)

    def tearDown(self):
        "Perform clean-up"
        client = MongoClient(self.dburi)
        client.drop_database(self.dbname) 

    def test_init(self):
        "Test init method"
        config = {}
        self.assertRaises(Exception, StorageManager, config)

    def test_insert(self):
        "Test init method"
        docs = [{'a':1}, {'b':1}]
        self.storage.insert('sitedb', docs)
        spec = {}
        result = [d for d in self.storage.fetch('sitedb', spec)]
        expect = docs
        self.assertEqual(expect, result)

#
# main
#
if __name__ == '__main__':
    unittest.main()

