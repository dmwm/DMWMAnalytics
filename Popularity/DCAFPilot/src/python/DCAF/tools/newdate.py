#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=

"""
File       : newdate.py
Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
Description: Generate new date from given one and a step
"""

# system modules
import sys
import optparse

# package modules
from DCAF.utils.utils import newdate

class OptionParser():
    "User based option parser"
    def __init__(self):
        usage  = 'Usage: %prog [options]\n'
        usage += 'Description: prints new date from given date and step\n'
        usage += 'Example: %prog --date=20140101'
        self.parser = optparse.OptionParser(usage=usage)
        self.parser.add_option("--date", action="store", type="string", \
            dest="date", default="", help="Input date (YYYYMMDD)")
        self.parser.add_option("--step", action="store", type="int", \
            dest="step", default=1, help="Date step from given date")
    def get_opt(self):
        "Return list of options"
        return self.parser.parse_args()

def main():
    "Main function"
    optmgr  = OptionParser()
    opts, _ = optmgr.get_opt()
    if  not opts.date:
        print "Please specify the date, see --help for more options"
        sys.exit(1)
    print newdate(opts.date, opts.step)

if __name__ == '__main__':
    main()
