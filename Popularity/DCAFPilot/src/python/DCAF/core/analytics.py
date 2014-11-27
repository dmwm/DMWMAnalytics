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
import random
import ConfigParser

# package modules
from DCAF.core.storage import StorageManager
from DCAF.services.sitedb import SiteDBService
from DCAF.services.dbs import DBSService
from DCAF.services.phedex import PhedexService
from DCAF.services.popdb import PopDBService
from DCAF.services.dashboard import DashboardService
from DCAF.services.utils import site_tier, rel_ver, rel_type, cmssw_test
from DCAF.services.utils import RFULL, RPRE, RPATCH
from DCAF.services.utils import TIER0, TIER1, TIER2, TIER3, TIER_NA
from DCAF.utils.utils import genkey, ndays
from DCAF.utils.regex import DATASET_PAT

def parse_config(filename):
    "Parse given config file into dict representation"
    config = ConfigParser.ConfigParser()
    config.read(filename)
    cdict = {}
    for section in config.sections():
        for pair in config.items(section):
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

    def dataset_info(self, timeframe, dataset, dtypes, stypes, rtypes, tiers, dformat, target=0):
        "Return common dataset info in specified data format"
        row = self.dbs.dataset_info(dataset)
        if  row:
            releases = [rname for rname in self.dbs.dataset_release_versions(dataset)]
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
                series['rel1_%s'%rserie] += 1
                majors['rel2_%s'%rmajor] += 1
                minors['rel3_%s'%rminor] += 1
                relclf['relt_%s'%rtype] += 1
            sites = [sname for sname in self.phedex.sites(dataset)]
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
            target_str = '%5.3f' % target if target else 0
            summary = self.dbs.dataset_summary(dataset)
            dashboard = self.dashboard.dataset_info(dataset, timeframe[0], timeframe[1])
            rec = dict(dataset=dataset_id, primds=prim, procds=proc, tier=tier,
                    dtype=dtype, creator=create_dn, nrel=nrels, nsites=nsites,
                    nfiles=summary['num_file'], nlumis=summary['num_lumi'],
                    nblk=summary['num_block'], nevt=summary['num_event'],
                    size=summary['file_size'], era=era, dbs=dbsinst,
                    cpu=dashboard['cpu'], wct=dashboard['wct'], proc_evts=dashboard['nevt'],
                    target=target_str)
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
            headers.remove('dataset')
            headers = ['dataset'] + headers # let dataset id be the first column
            headers.remove('target')
            if  target != -1:
                headers += ['target'] # make target to be last column
            if  dformat == 'headers':
                yield headers
            elif  dformat == 'csv':
                res = [str(rec[h]) for h in headers]
                yield ','.join(res)
            elif dformat == 'vw':
                target = rec.pop('target')
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

    def dataframe(self, timeframe, seed, dformat, metric, dbs_extra, newdata=None):
        """Form a dataframe from various CMS data-providers"""
        dtypes, stypes, rtypes, tiers = self.data_types()
        pop_datasets = 0
        dbs_datasets = 0
        if  dformat == 'csv':
            # seed dataset to determine headers of the dataframe
            rows = self.dataset_info(timeframe, seed, dtypes, stypes, rtypes, tiers, 'headers')
            headers = [r for r in rows][0]
            yield ','.join(headers)
        if  newdata: # request new dataset
            if  self.verbose:
                print "Generate dataframe for new datasets"
            n_days = 7
            if  timeframe:
                n_days = ndays(timeframe[0], timeframe[1])
            new_datasets = self.dbs.new_datasets(n_days)
            for row in new_datasets:
                dataset = row['dataset']
                target = -1 # we will need to predict it
                rows = self.dataset_info(timeframe, dataset, dtypes, stypes, rtypes, tiers, \
                        dformat, target)
                for row in rows:
                    yield row
            return
        # get list of popular datasets in certain time frame
        popdb_results = [r for r in self.popdb.dataset_stat(timeframe[0], timeframe[1])]
        popdb_datasets = {} #
        for row in popdb_results:
            dataset = row['dataset']
            if  not DATASET_PAT.match(dataset):
                continue
            if  self.verbose:
                print "Generate dataframe for %s, timeframe: %s" % (dataset, timeframe)
            naccess = row['naccess']
            nusers = row['nusers']
            totcpu = row['totcpu']
            if  metric=='naccess' or metric=='nusers' or metric=='totcpu':
                target = row[metric]
            elif basestring(metric, str) and len(metric)>0:
                try:
                    target = eval(metric)
                except Exception as exc:
                    print 'ERROR, unable to eval metric="%s"' % metric
                    raise exc
            else:
                target = naccess
            rows = self.dataset_info(timeframe, dataset, dtypes, stypes, rtypes, tiers, dformat, target)
            popdb_datasets[dataset] = row
            for row in rows:
                yield row
                pop_datasets += 1

        # get list of datasets from DBS and discard from this list
        # those who were presented in popdb
        all_dbs_datasets = self.dbs.datasets()
        dbsdatasets = [d for d in all_dbs_datasets if d not in popdb_datasets.keys()]
        for dataset in random.sample(dbsdatasets, dbs_extra):
            rows = self.dataset_info(timeframe, dataset, dtypes, stypes, rtypes, tiers, dformat)
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
