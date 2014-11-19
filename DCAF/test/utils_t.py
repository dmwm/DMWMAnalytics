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

from DCAF.utils.utils import popdb_date

class testStorageManager(unittest.TestCase):
    """
    A test class for the StorageManager class
    """
    def setUp(self):
        "set up connection"
        pass

    def tearDown(self):
        "Perform clean-up"
        pass

    def test_popdb_date(self):
        "Test popdb_date method"
        result = popdb_date('20140105')
        expect = '2014-1-5'
        self.assertEqual(expect, result)

        result = popdb_date(expect)
        self.assertEqual(expect, result)
#
# main
#
if __name__ == '__main__':
    unittest.main()

