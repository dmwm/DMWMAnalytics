#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=
"""
File       : dataframe.py
Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
Description: Script to yield dataframe
"""

# system modules
import os
import sys
import optparse

# package modules
from DCAF.core.analytics import DCAF

class OptionParser():
    def __init__(self):
        "User based option parser"
        self.parser = optparse.OptionParser()
        self.parser.add_option("--start", action="store", type="string",
            dest="start", default="", help="Start timestamp")
        self.parser.add_option("--stop", action="store", type="string",
            dest="stop", default="", help="Stop timestamp")
        self.parser.add_option("--format", action="store", type="string",
            dest="format", default="csv", help="Output file format")
        self.parser.add_option("--config", action="store", type="string",
            dest="config", default="etc/dcaf.cfg", help="Config file")
    def get_opt(self):
        "Return list of options"
        return self.parser.parse_args()

def main():
    "Main function"
    optmgr  = OptionParser()
    opts, _ = optmgr.get_opt()

    mgr = DCAF(opts.config)
    time1 = opts.start
    time2 = opts.stop
    for row in mgr.dataframe(timeframe=[time1, time2], dformat=opts.format):
        print row

if __name__ == '__main__':
    main()
