#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=
"""
File       : popdb.py
Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
Description: PopDB service module
"""

# system modules
import time
import urllib
import optparse

# package modules
import DCAF.utils.jsonwrapper as json
from DCAF.utils.sso_reader import getdata
from DCAF.utils.utils import get_key_cert, genkey, popdb_date

class OptionParser():
    def __init__(self):
        "User based option parser"
        usage  = 'Usage: %prog [options]\n'
        usage += 'Description: fetch data from popularity DB for given time frame\n'
        usage += 'Example: %prog --start=20150101 --stop=20150108'
        self.parser = optparse.OptionParser(usage=usage)
        self.parser.add_option("--start", action="store", type="string",
            dest="tstart", default="", help="start date, format YYYYMMDD")
        self.parser.add_option("--stop", action="store", type="string",
            dest="tstop", default="", help="end date, format YYYYMMDD")
    def get_opt(self):
        "Return list of options"
        return self.parser.parse_args()

def popdb_datasets(tstart, tstop):
    "Fetch data from popDB for given time frame and print out datasets"
    url = 'https://cms-popularity.cern.ch/popdb/popularity/'
    api = 'DSStatInTimeWindow'
    ckey, cert = get_key_cert()
    params = {'tstart':tstart, 'tstop':tstop}
    url = '%s/%s?%s' % (url, api, urllib.urlencode(params, doseq=True))
    data = getdata(url, ckey, cert, debug=0)
    data = json.loads(data)
    headers = []
    for row in data['DATA']:
        if  not headers:
            headers = row.keys()
            print ','.join(headers)
        out = [str(row[k]) for k in headers]
        print ','.join(out)

def main():
    optmgr  = OptionParser()
    opts, _ = optmgr.get_opt()
    popdb_datasets(popdb_date(opts.tstart), popdb_date(opts.tstop))

if __name__ == '__main__':
    main()
