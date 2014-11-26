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
from DCAF.utils.utils import popdb_date

class OptionParser():
    def __init__(self):
        "User based option parser"
        self.parser = optparse.OptionParser()
        self.parser.add_option("--fout", action="store", type="string",
            dest="fout", default="cmscomp.csv", help="Output file")
        seed = '/ZMM/Summer11-DESIGN42_V11_428_SLHC1-v1/GEN-SIM'
        self.parser.add_option("--seed-dataset", action="store", type="string",
            dest="seed", default=seed,
            help="Seed dataset, default=%s" % seed)
        self.parser.add_option("--dbs-extra", action="store", type="int",
            dest="dbs_extra", default=1000,
            help="Extra datasets from DBS which were not shown in popularityDB, default 1000")
        self.parser.add_option("--metric", action="store", type="string",
            dest="metric", default="naccess",
            help="Output target metric (naccess by default), supported naccess, nusers, totcpu or python expression of those")
        self.parser.add_option("--start", action="store", type="string",
            dest="start", default="", help="Start timestamp in YYYYMMDD format")
        self.parser.add_option("--stop", action="store", type="string",
            dest="stop", default="", help="Stop timestamp in YYYYMMDD format")
        msg = 'Output file format, deafult csv (supported csv, vw)'
        self.parser.add_option("--format", action="store", type="string",
            dest="dformat", default="csv", help=msg)
        self.parser.add_option("--config", action="store", type="string",
            dest="config", default="etc/dcaf.cfg", help="Config file, default etc/dcaf.cfg")
        self.parser.add_option("--verbose", action="store", type="int",
            dest="verbose", default=0, help="Verbosity level, default 0")
        self.parser.add_option("--seed-cache", action="store_true",
            dest="update", default=False, help="Seed internal cache with DBS/SiteDB database content")
        self.parser.add_option("--clean-cache", action="store_true",
            dest="clean", default=False, help="Clean-up cache")
        self.parser.add_option("--newdata", action="store_true",
            dest="newdata", default=False, help="Get new set of data from DBS, instead of popularity DB")
    def get_opt(self):
        "Return list of options"
        return self.parser.parse_args()

def main():
    "Main function"
    optmgr  = OptionParser()
    opts, _ = optmgr.get_opt()

    mgr = DCAF(opts.config, opts.verbose)
    if  opts.clean:
        mgr.cleanup('cache')
        return
    if  opts.update:
        mgr.update()
        return
    if  opts.start or opts.stop:
        tframe = [popdb_date(opts.start), popdb_date(opts.stop)]
    else:
        tframe = None
    fout = opts.fout
    seed = opts.seed
    dformat = opts.dformat
    metric = opts.metric
    dbsextra = opts.dbs_extra
    newdata = opts.newdata
    with open(opts.fout, 'w') as ostream:
        for row in mgr.dataframe(tframe, seed, dformat, metric, dbsextra, newdata):
            ostream.write(row+'\n')

if __name__ == '__main__':
    main()
