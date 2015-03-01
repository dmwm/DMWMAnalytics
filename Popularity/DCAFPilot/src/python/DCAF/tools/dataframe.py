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
import time
import datetime
import optparse

# package modules
from DCAF.core.analytics import DCAF
from DCAF.utils.utils import popdb_date, fopen

class OptionParser():
    def __init__(self):
        "User based option parser"
        usage  = 'Usage: %prog [options]\n'
        usage += 'Description: create CMS data frame\n'
        usage += 'Example: %prog --start=20140101 --stop=20140108 --dbs-extra=10000 --fout=dataframe.csv\n'
        self.parser = optparse.OptionParser(usage=usage)
        self.parser.add_option("--fout", action="store", type="string",
            dest="fout", default="cmscomp.csv", help="Output file")
        seed = '/ZMM/Summer11-DESIGN42_V11_428_SLHC1-v1/GEN-SIM'
        self.parser.add_option("--seed-dataset", action="store", type="string",
            dest="seed", default=seed,
            help="Seed dataset, default=%s" % seed)
        self.parser.add_option("--dbs-extra", action="store", type="int",
            dest="dbs_extra", default=1000,
            help="Extra datasets from DBS which were not shown in popularityDB, default 1000")
        self.parser.add_option("--start", action="store", type="string",
            dest="start", default="", help="Start timestamp in YYYYMMDD format")
        self.parser.add_option("--stop", action="store", type="string",
            dest="stop", default="", help="Stop timestamp in YYYYMMDD format")
        msg = 'Output file format, deafult csv (supported csv, vw)'
        self.parser.add_option("--format", action="store", type="string",
            dest="dformat", default="csv", help=msg)
        if  'DCAFPILOT_CONFIG' in os.environ:
            cfg = os.environ['DCAFPILOT_CONFIG']
        else:
            cfg = os.path.join(os.environ.get('DCAFPILOT_ROOT', os.getcwd()), 'etc/dcaf.cfg')
        self.parser.add_option("--config", action="store", type="string",
            dest="config", default=cfg, help="Config file, default etc/dcaf.cfg")
        self.parser.add_option("--verbose", action="store", type="int",
            dest="verbose", default=0, help="Verbosity level, default 0")
        self.parser.add_option("--seed-cache", action="store_true",
            dest="update", default=False, help="Seed internal cache with DBS/SiteDB database content")
        self.parser.add_option("--clean-cache", action="store_true",
            dest="clean", default=False, help="Clean-up cache")
        self.parser.add_option("--remove-doc", action="store", type="string",
            dest="docid", default=None, help="Remove given docid from cache")
        self.parser.add_option("--newdata", action="store_true",
            dest="newdata", default=False, help="Get new set of data from DBS, instead of popularity DB")
        self.parser.add_option("--profile", action="store_true",
            dest="profile", default=False, help="Run program under profiler")
    def get_opt(self):
        "Return list of options"
        return self.parser.parse_args()

def main():
    "Main function"
    optmgr  = OptionParser()
    opts, _ = optmgr.get_opt()

    if  opts.verbose:
        print time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())
    time0 = time.time()
    mgr = DCAF(opts.config, opts.verbose)
    if  opts.clean:
        mgr.cleanup('cache')
        return
    if  opts.docid:
        mgr.remove('cache', opts.docid)
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
    dbsextra = opts.dbs_extra
    newdata = opts.newdata
    fout = opts.fout
    def run(fout, tframe, seed, dformat, dbsextra, newdata):
        with fopen(opts.fout, 'w') as ostream:
            for row in mgr.dataframe(tframe, seed, dformat, dbsextra, newdata):
                ostream.write(row+'\n')
    if  opts.profile:
        import cProfile # python profiler
        import pstats   # profiler statistics
        cmd  = 'run(fout,tframe,seed,dformat,dbsextra,newdata)'
        cProfile.runctx(cmd, globals(), locals(), 'profile.dat')
        info = pstats.Stats('profile.dat')
        info.sort_stats('cumulative')
        info.print_stats()
    else:
        run(fout, tframe, seed, dformat, dbsextra, newdata)
    if  opts.verbose:
        print "Elapsed time:", datetime.timedelta(seconds=(time.time()-time0))
        print time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())

if __name__ == '__main__':
    main()
