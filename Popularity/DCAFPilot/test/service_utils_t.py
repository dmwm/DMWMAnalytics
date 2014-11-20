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

from DCAF.services.utils import site_tier, rel_type, rel_ver
from DCAF.services.utils import TIER0, TIER1, TIER2, TIER3, TIER_NA
from DCAF.services.utils import RFULL, RPRE, RPATCH

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

    def test_site_tier(self):
        "Test site_tier method"
        result = site_tier('T0_CERN')
        expect = TIER0
        self.assertEqual(expect, result)

        result = site_tier('T1_CERN')
        expect = TIER1
        self.assertEqual(expect, result)

        result = site_tier('T2_CERN')
        expect = TIER2
        self.assertEqual(expect, result)

        result = site_tier('T3_CERN')
        expect = TIER3
        self.assertEqual(expect, result)

        result = site_tier('CERN')
        expect = TIER_NA
        self.assertEqual(expect, result)

    def test_rel_type(self):
        "Test rel_type method"
        result = rel_type('CMSSW_1_0_1')
        expect = RFULL
        self.assertEqual(expect, result)

        result = rel_type('CMSSW_1_0_1_pre')
        expect = RPRE
        self.assertEqual(expect, result)

        result = rel_type('CMSSW_1_0_1_patch')
        expect = RPATCH
        self.assertEqual(expect, result)

    def test_rel_ver(self):
        "Test rel_ver method"
        result = rel_ver('CMSSW_1_0_1')
        expect = ('1', '0', '1')
        self.assertEqual(expect, result)

#
# main
#
if __name__ == '__main__':
    unittest.main()

