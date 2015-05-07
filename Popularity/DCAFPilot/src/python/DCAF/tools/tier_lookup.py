#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=

"""
File       : dataset_lookup.py
Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
Description: Script which look-up data-tier info in local cache of datasets
"""
from __future__ import print_function

# system modules
import os
import optparse

# mongodb modules
from pymongo import MongoClient

# local modules
from DCAF.utils.utils import fopen, parse_config, genkey
from DCAF.services.dbs import DBSService

class OptionParser():
    "User based option parser"
    def __init__(self):
        usage  = 'Usage: %prog [options]\n'
        usage += 'Description: look-up dataset info in local cache\n'
        usage += 'Example: %prog --fin=file.csv.gz'
        self.parser = optparse.OptionParser(usage=usage)
        config = os.getenv('DCAFPILOT_CONFIG', 'etc/dcaf.cfg')
        self.parser.add_option("--config", action="store", type="string", \
            dest="config", default=config, help="DCAF config, default %s" %  config)
        self.parser.add_option("--sep", action="store", type="string", \
            dest="sep", default=",", help="Output file separator, default comma")
        self.parser.add_option("--sort", action="store", type="string", \
            dest="sort", default="tier", help="Sort by tier or id, default by tier name")
    def get_opt(self):
        "Return list of options"
        return self.parser.parse_args()

def convert(config, sep=',', sortby='tier'):
    "Lookup DBS data tiers"
    dbs = DBSService(config)
    tiers = {}
    salt = config.get('core', {}).get('salt', 'secret sauce')
    for tier in dbs.data_tiers():
        tid = genkey(tier, salt, 5)
        if  sortby == 'tier':
            tiers[tier] = tid
        else:
            tiers[tid] = tier
    for tier in sorted(tiers.keys()):
        if  sortby == 'tier':
            print('%s%s%s' % (tiers[tier], sep, tier))
        else:
            print('%s%s%s' % (tier, sep, tiers[tier]))

def main():
    "Main function"
    optmgr = OptionParser()
    opts, _ = optmgr.get_opt()
    config = parse_config(opts.config)
    convert(config, opts.sep, opts.sort)

if __name__ == '__main__':
    main()
