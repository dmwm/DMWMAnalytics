#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=

"""
File       : dataset_lookup.py
Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
Description: Script which look-up dataset info in local cache
"""

# system modules
import optparse

# mongodb modules
from pymongo import MongoClient

# local modules
from DCAF.utils.utils import fopen

class OptionParser():
    "User based option parser"
    def __init__(self):
        usage  = 'Usage: %prog [options]\n'
        usage += 'Description: look-up dataset info in local cache\n'
        usage += 'Example: %prog --fin=file.csv.gz'
        self.parser = optparse.OptionParser(usage=usage)
        self.parser.add_option("--fin", action="store", type="string", \
            dest="fin", default="", help="Input file")
        uri = 'mongodb://localhost:8230'
        self.parser.add_option("--uri", action="store", type="string", \
            dest="uri", default=uri, help="DCAF cache (MongoDB) uri, default %s" %  uri)
        self.parser.add_option("--sep", action="store", type="string", \
            dest="sep", default=",", help="Output file separator, default comma")
    def get_opt(self):
        "Return list of options"
        return self.parser.parse_args()

def convert(fin, uri, sep=','):
    """
    Convert input prediction file (id,prediction) into (dataset,prediction)
    by using DCAFPilot cache
    """
    client = MongoClient(uri)
    mgr = client['analytics']['datasets']
    headers = None
    dbs_id = None
    ds_id = None
    tier_id = None
    tiers = {}
    with fopen(fin, 'r') as istream:
        for line in istream.readlines():
            row = line.replace('\n', '').split(sep)
            if  not headers:
                headers = row
                dbs_id = headers.index('dbs')
                ds_id = headers.index('dataset')
                tier_id = headers.index('tier')
                continue
            spec = {'dataset_id':int(row[ds_id]), 'dbs_instance':int(row[dbs_id])}
            res = mgr.find_one(spec)
            if  res:
                _, prim, proc, tier = res['dataset'].split('/')
                tiers[tier] = row[tier_id]
    for tier in sorted(tiers.keys()):
        print tiers[tier], tier

def main():
    "Main function"
    optmgr = OptionParser()
    opts, _ = optmgr.get_opt()
    convert(opts.fin, opts.uri, opts.sep)

if __name__ == '__main__':
    main()
