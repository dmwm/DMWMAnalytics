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

from DCAF.utils.utils import popdb_date, ndays

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

    def test_ndays(self):
        "Test ndays function"
        time1, time2 = '20141120', '20141124'
        result = ndays(time1, time2)
        expect = 4
        self.assertEqual(expect, result)
#
# main
#
if __name__ == '__main__':
    unittest.main()

