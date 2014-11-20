#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=
"""
File       : utils.py
Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
Description: Set of utilities for CMS services
"""

# system modules
import os
import sys
import optparse

# package modules
from DCAF.utils.regex import INT_PAT

TIER0 = 0
TIER1 = 1
TIER2 = 2
TIER3 = 3
TIER_NA = 4
def site_tier(site):
    "Return site tier"
    if  site.startswith('T0'):
        return TIER0
    elif site.startswith('T1'):
        return TIER1
    elif site.startswith('T2'):
        return TIER2
    elif site.startswith('T3'):
        return TIER3
    return TIER_NA

RFULL = 0
RPRE = 1
RPATCH = 2
def rel_type(release):
    "Release type classifier"
    if  release.find('_patch') != -1:
        return RPATCH
    elif release.find('_pre') != -1:
        return RPRE
    return RFULL

def rel_ver(release):
    "Return release versions"
    if  release.startswith('CMSSW_'):
        arr = release.split('_') # CMSSW_1_1_1
        return arr[1], arr[2], arr[3]
    return 0, 0, 0

def cmssw_test(rserie, rmajor, rminor):
    "Return if provided parameter match CMSSW release schema"
    cond = INT_PAT.match(str(rserie)) and INT_PAT.match(str(rmajor)) and INT_PAT.match(str(rminor))
    return cond
