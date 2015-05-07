#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=
"""
File       : popdb.py
Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
Description: PopDB service module
"""
from __future__ import print_function

# system modules
import time
import urllib
import socket
import optparse

# package modules
import DCAF.utils.jsonwrapper as json
from DCAF.utils.sso_reader import getdata as sso_getdata
from DCAF.utils.url_utils import getdata
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
        url = 'https://cms-popularity.cern.ch/popdb/popularity/'
        host = socket.gethostbyaddr(socket.gethostname())[0]
        if  host.endswith('cern.ch'):
            url = 'http://cms-popularity-prod.cern.ch/popdb/popularity'
        self.parser.add_option("--url", action="store", type="string",
            dest="url", default=url, help="Popularity DB URL:, %s" % url)
    def get_opt(self):
        "Return list of options"
        return self.parser.parse_args()

def popdb_datasets(tstart, tstop, url):
    "Fetch data from popDB for given time frame and print out datasets"
    api = 'DSStatInTimeWindow'
    ckey, cert = get_key_cert()
    params = {'tstart':tstart, 'tstop':tstop}
    url = '%s/%s?%s' % (url, api, urllib.urlencode(params, doseq=True))
    # NOTE: popularity DB has two different access points, one
    # within CERN network and out outside. The former does not require
    # authentication, while later passes through CERN SSO.
    # The following block reflects this, in a future, when popularity DB
    # will move into cmsweb domain we'll no longer need it
    if  url.find('cms-popularity-prod.cern.ch') != -1:
        data = getdata(url, ckey=ckey, cert=cert, debug=0)
    else:
        data = sso_getdata(url, ckey=ckey, cert=cert, debug=0)
    data = json.loads(data)
    headers = []
    for row in data['DATA']:
        if  not headers:
            headers = row.keys()
            print(','.join(headers))
        out = [str(row[k]) for k in headers]
        print(','.join(out))

def main():
    optmgr  = OptionParser()
    opts, _ = optmgr.get_opt()
    popdb_datasets(popdb_date(opts.tstart), popdb_date(opts.tstop), opts.url)

if __name__ == '__main__':
    main()
