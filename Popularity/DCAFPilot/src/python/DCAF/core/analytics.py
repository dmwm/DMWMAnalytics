#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=
"""
File       : DCAF.py
Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
Description: Generic module to perform various analytics tasks
"""

# system modules
import os
import sys
import time
import random
import ConfigParser
import multiprocessing as mp

# package modules
from DCAF.core.storage import StorageManager
from DCAF.services.sitedb import SiteDBService
from DCAF.services.dbs import DBSService
from DCAF.services.phedex import PhedexService
from DCAF.services.popdb import PopDBService
from DCAF.services.dashboard import DashboardService
from DCAF.services.utils import site_tier, rel_ver, rel_type, cmssw_test
from DCAF.services.utils import genuid, RFULL, RPRE, RPATCH
from DCAF.services.utils import TIER0, TIER1, TIER2, TIER3, TIER_NA
from DCAF.utils.utils import genkey, ndays, yyyymmdd
from DCAF.utils.regex import DATASET_PAT

def parse_config(filename):
    "Parse given config file into dict representation"
    config = ConfigParser.ConfigParser()
    config.read(filename)
    cdict = {}
    for section in config.sections():
        for pair in config.items(section):
            if  section in cdict:
                cdict[section].update(dict([pair]))
            else:
                cdict[section] = dict([pair])
    return cdict

class DCAF(object):
    def __init__(self, configfile, verbose=0):
        "Main module"
        self.config = parse_config(configfile)
        self.storage = StorageManager(self.config)
        self.sitedb = SiteDBService(self.config, verbose)
        self.dbs = DBSService(self.config, verbose)
        self.popdb = PopDBService(self.config, verbose)
        self.phedex = PhedexService(self.config, verbose)
        self.dashboard = DashboardService(self.config, verbose)
        self.salt = self.config.get('core', {}).get('salt', 'secret sauce')
        self.verbose = verbose
        self.multitask = self.config.get('multitask', False)

    def fetch(self, doc):
        """
        Fetch method retrieves data from data-provide and store them into
        internal data storage.
        """
        source = doc.get('source', None)
        params = doc.get('params', {})
        if  self.verbose:
            print "Fetch data from %s(%s)" % (source, params)
        if  source == 'sitedb':
            for item in self.sitedb.fetch('people', {}):
                print item
                break

    def data_types(self):
        """Return list of data types dicts:

            - dtypes is data types, e.g. mc/data
            - stypes is site types, dict of Tier sites
            - rtypes is release types
              {'series':{'major':{'minor':}}
        """
        dtypes = ['mc', 'data'] # data types, should be small list
        tiers = ['GEN', 'SIM', 'RECO', 'AOD'] # tier types, should be small list
        stypes = {'s_%s'%TIER0:0, 's_%s'%TIER1:0, 's_%s'%TIER2:0, 's_%s'%TIER3:0, 's_%s'%TIER_NA:0} # site types
        rtypes = {} # release types
        releases = self.dbs.releases()
        series = set()
        majors = set()
        minors = set()
        for row in releases:
            rel = row['release']
            sval, major, minor = rel_ver(rel)
            if  not cmssw_test(sval, major, minor):
                continue
            series.add(sval)
            majors.add(major)
            minors.add(minor)
        serdict = {}
        for val in series:
            serdict['rel1_%s'%val] = 0
        majdict = {}
        for val in majors:
            majdict['rel2_%s'%val] = 0
        mindict = {}
        for val in minors:
            mindict['rel3_%s'%val] = 0
        # release types as defined in rel_type function
        typdict = {'relt_%s'%RFULL:0, 'relt_%s'%RPRE:0, 'relt_%s'%RPATCH:0}
        rtypes = {'series': serdict, 'majors': majdict, 'minors': mindict, 'rtypes': typdict}
        return dtypes, stypes, rtypes, tiers

    def dataset_info_all(self, dataset, timeframe):
        "Concurrently obtain information about dataset."
        # NOTE: this function may need expansion if we'll need to obtain more information
        #       about given dataset/timeframe. To extend, please add new local
        #       function similar to procN
        # Each procN function should have (pos, out, args) input arguments
        # the pos is a position in queue, out is an output queue and args
        # are arguments required to pass to internal function

        # output Queue
        output = mp.Queue()
        # local functions to fetch info about dataset from different subsystems
        def proc1(pos, out, dataset):
            try:
                res = [rname for rname in self.dbs.dataset_release_versions(dataset)]
            except:
                res = []
            out.put((pos, res))
        def proc2(pos, out, dataset):
            try:
                res = [sname for sname in self.phedex.sites(dataset)]
            except:
                res = []
            out.put((pos, res))
        def proc3(pos, out, dataset):
            try:
                res = [r for r in self.dbs.dataset_parents(dataset)]
            except:
                res = []
            out.put((pos, res))
        def proc4(pos, out, dataset):
            try:
                res = self.dbs.dataset_summary(dataset)
            except:
                res = dict()
            out.put((pos, res))
        def proc5(pos, out, dataset, tframe):
            try:
                res = self.dashboard.dataset_info(dataset, tframe[0], tframe[1])
            except:
                res = dict()
            out.put((pos, res))
        # concurrent processes to run, each args contains
        # a position value, output queue and args for internal function call
        processes = [
            mp.Process(target=proc1, args=(1, output, dataset)),
            mp.Process(target=proc2, args=(2, output, dataset)),
            mp.Process(target=proc3, args=(3, output, dataset)),
            mp.Process(target=proc4, args=(4, output, dataset)),
            mp.Process(target=proc5, args=(5, output, dataset, timeframe))
        ]
        # Run processes
        for proc in processes:
            proc.start()

        # Exit the completed processes
        for proc in processes:
            proc.join()

        # Get process results from the output queue
        results = [output.get() for _ in processes]
        results.sort() # sort by position
        results = [v for _, v in results] # extract values
        return results

    def dataset_info(self, timeframe, dataset, dtypes, stypes, rtypes, tiers, dformat, target=0):
        "Return common dataset info in specified data format"
        row = self.dbs.dataset_info(dataset)
        if  row:
            if  self.multitask:
                releases, sites, parents, summary, dashboard = \
                        self.dataset_info_all(dataset, timeframe)
            else:
                releases = [rname for rname in self.dbs.dataset_release_versions(dataset)]
                sites = [sname for sname in self.phedex.sites(dataset)]
                parents = [r for r in self.dbs.dataset_parents(dataset)]
                summary = self.dbs.dataset_summary(dataset)
                dashboard = self.dashboard.dataset_info(dataset, timeframe[0], timeframe[1])
            nrels = len(releases)
            series = rtypes['series']
            majors = rtypes['majors']
            minors = rtypes['minors']
            relclf = rtypes['rtypes']
            for rel in releases:
                rserie, rmajor, rminor = rel_ver(rel)
                if  not cmssw_test(rserie, rmajor, rminor):
                    continue
                rtype = rel_type(rel)
                try:
                    series['rel1_%s'%rserie] += 1
                except:
                    pass
                try:
                    majors['rel2_%s'%rmajor] += 1
                except:
                    pass
                try:
                    minors['rel3_%s'%rminor] += 1
                except:
                    pass
                try:
                    relclf['relt_%s'%rtype] += 1
                except:
                    pass
            nsites = len(sites)
            for site in sites:
                stier = site_tier(site)
                stypes['s_%s'%stier] += 1
            dataset_id = row['rid']
            era = genkey(row['acquisition_era_name'], self.salt, 5)
            create_dn = self.sitedb.dnid(row['create_by'])
            dbsinst = row['dbs_instance']
            dtype = row['primary_ds_type']
            # number of data types should be small and simple
            # list look-up shouldn't be a problem
            if  dtype not in dtypes:
                dtypes.append(dtype)
            dtype = dtypes.index(dtype)
            _, prim, proc, tier = dataset.split('/')
            prim = genkey(prim, self.salt, 5)
            proc = genkey(proc, self.salt, 5)
            if  tier not in tiers:
                tiers.append(tier)
            tier = tiers.index(tier)
            parent = parents[0] if len(parents) else 0
            uid = genuid(yyyymmdd(timeframe[0]), dbsinst, dataset_id)
            size_norm = 2**30 # normalization factor for file size
            rec = dict(id=uid, dataset=dataset_id, primds=prim, procds=proc, tier=tier,
                    dtype=dtype, creator=create_dn, nrel=nrels, nsites=nsites,
                    parent=parent, era=era, dbs=dbsinst,
                    nfiles=summary.get('num_file', 0),
                    nlumis=summary.get('num_lumi', 0),
                    nblk=summary.get('num_block', 0),
                    nevt=summary.get('num_event', 0),
                    size=summary.get('file_size', 0)/size_norm,
                    cpu=dashboard.get('cpu', 0),
                    wct=dashboard.get('wct', 0),
                    proc_evts=dashboard.get('nevt', 0))
            if  isinstance(target, dict):
                rec.update(target)
            for key,val in series.items():
                rec.update({key:val})
            for key, val in majors.items():
                rec.update({key:val})
            for key, val in minors.items():
                rec.update({key:val})
            for key, val in relclf.items():
                rec.update({key:val})
            for key, val in stypes.items():
                rec.update({key:val})
            headers = rec.keys()
            headers.sort()
            headers.remove('id')
            headers = ['id'] + headers # let dataset id be the first column
            if  dformat == 'headers':
                yield headers
            elif  dformat == 'csv':
                res = [str(rec[h]) for h in headers]
                yield ','.join(res)
            elif dformat == 'vw':
                target_str = target.get('rnaccess')
                vals = ' '.join([str(rec[h]) for h in headers])
                uid = genkey(vals, self.salt, 5) # unique row identified
                vwrow = "%s '%s |f %s" % (target_str, uid, vals)
                yield vwrow

    def update(self):
        # get fresh copy of hashed db's
        self.dbs.update('datasets')
        self.dbs.update('releases')
        self.sitedb.update('people')
        self.sitedb.update('sites')

    def cleanup(self, cname):
        "Clean-up given collection"
        self.storage.cleanup(cname)

    def remove(self, cname, docid):
        "Remove given docid from given collection"
        spec = {"_id": docid}
        self.storage.cleanup(cname, spec)

    def dataframe(self, timeframe, seed, dformat, dbs_extra, newdata=None):
        """Form a dataframe from various CMS data-providers"""
        dtypes, stypes, rtypes, tiers = self.data_types()
        pop_datasets = 0
        dbs_datasets = 0
        popdb_results = [r for r in self.popdb.dataset_stat(timeframe[0], timeframe[1])]
        if  dformat == 'csv':
            row = popdb_results[0]
            dataset = row['dataset']
            target = dict(naccess=row['naccess'],nusers=row['nusers'],totcpu=row['totcpu'],
                    rnaccess=row['rnaccess'],rnusers=row['rnusers'],rtotcpu=row['rtotcpu'])
            # seed dataset to determine headers of the dataframe
            rows = self.dataset_info(timeframe, seed, dtypes, stypes, rtypes,
                    tiers, 'headers', target)
            headers = [r for r in rows][0]
            yield ','.join(headers)
        tstamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(sec))
        if  newdata: # request new dataset
            if  self.verbose:
                print "Generate dataframe for new datasets", tstamp
            n_days = 7
            if  timeframe:
                n_days = ndays(yyyymmdd(timeframe[0]), yyyymmdd(timeframe[1]))
            new_datasets = self.dbs.new_datasets(n_days)
            target = dict(naccess=0,nusers=0,totcpu=0,
                    rnaccess=0,rnusers=0,rtotcpu=0)
            for row in new_datasets:
                dataset = row['dataset']
                rows = self.dataset_info(timeframe, dataset, dtypes, stypes, \
                        rtypes, tiers, dformat, target)
                for row in rows:
                    yield row
            return
        # get list of popular datasets in certain time frame
#        popdb_results = [r for r in self.popdb.dataset_stat(timeframe[0], timeframe[1])]
        popdb_datasets = {} #
        for row in popdb_results:
            dataset = row['dataset']
            if  not DATASET_PAT.match(dataset):
                continue
            if  self.verbose:
                print "Generate dataframe for %s, timeframe: %s, %s" \
                        % (dataset, timeframe, tstamp)
            target = dict(naccess=row['naccess'],nusers=row['nusers'],totcpu=row['totcpu'],
                    rnaccess=row['rnaccess'],rnusers=row['rnusers'],rtotcpu=row['rtotcpu'])
            rows = self.dataset_info(timeframe, dataset, dtypes, stypes, \
                    rtypes, tiers, dformat, target)
            popdb_datasets[dataset] = row
            for row in rows:
                yield row
                pop_datasets += 1

        # get list of datasets from DBS and discard from this list
        # those who were presented in popdb
        all_dbs_datasets = self.dbs.datasets()
        dbsdatasets = [d for d in all_dbs_datasets if d not in popdb_datasets.keys()]
        target = dict(naccess=0,nusers=0,totcpu=0,
                rnaccess=0,rnusers=0,rtotcpu=0)
        for dataset in random.sample(dbsdatasets, dbs_extra):
            rows = self.dataset_info(timeframe, dataset, dtypes, stypes, \
                    rtypes, tiers, dformat, target)
            for row in rows:
                yield row
                dbs_datasets += 1
        if  self.verbose:
            print "DBS datasets  : %s" % dbs_datasets
            print "PopDB datasets: %s out of %s" % (pop_datasets, len(popdb_results))

    def export(self, dformat):
        "Export analytics dataframe into provided data format"
        print "Export dataframe into %s format" % dformat.lower()
        if  dformat.lower() == 'csv':
            print "Do CSV export"
            headers = []
            for row in self.dataframe():
                if  not headers:
                    headers = row
                    yield ','.join(headers)
                    continue
                yield ','.join(row)
        elif  dformat.lower() == 'vw':
            print "Do vw export"
        else:
            raise NotImplemented
