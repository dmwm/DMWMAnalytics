#!/usr/bin/env python
#-*- coding: ISO-8859-1 -*-
#pylint: disable=C0103

"""
Regular expression patterns
"""

__author__ = "Valentin Kuznetsov"

# system modules
import re
import calendar

def word_chars(word, equal=True):
    """
    Creates a pattern of given word as series of its characters, e.g.
    for given word dataset I'll get
    '^d$|^da$|^dat$|^data$|^datas$|^datase$|^dataset$'
    which can be used later in regular expressions
    """
    pat = r'|'.join(['^%s$' % word[:x+1] for x in xrange(len(word))])
    if  equal:
        pat += '|^%s=' % word
    return pat

DAYS = [d for d in calendar.day_abbr if d]
MONTHS = [m for m in calendar.month_abbr if m]

HTTP_PAT = \
    re.compile(r"http://.*|https://.*")
IP_PAT = \
    re.compile(r"^([0-9]{1,3}\.){3,3}[0-9]{1,3}$")
YYYYMMDD_PAT = \
    re.compile(r'[0-2]0[0-9][0-9][0-1][0-9][0-3][0-9]')
TIER_PAT = \
    re.compile(r'T[0-9]_') # T1_CH_CERN
FLOAT_PAT = \
    re.compile(r'(^[-]?\d+\.\d*$|^\d*\.{1,1}\d+$)')
INT_PAT = \
    re.compile(r'(^[0-9-]$|^[0-9-][0-9]*$)')
PHEDEX_NODE_PAT = \
    re.compile(r'^T[0-9]_[A-Z]+(_)[A-Z]+') # T2_UK_NO
SE_PAT = \
    re.compile(r'[a-z]+(\.)[a-z]+(\.)') # a.b.c
NUM_PAT = \
    re.compile(r'^[-]?[0-9][0-9\.]*$') # -123
