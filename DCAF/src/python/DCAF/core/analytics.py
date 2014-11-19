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
from DCAF.services.utils import site_tier, rel_ver, rel_type, cmssw_test
from DCAF.services.utils import RFULL, RPRE, RPATCH
from DCAF.services.utils import TIER0, TIER1, TIER2, TIER3, TIER_NA
from DCAF.utils.utils import genkey

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

    def dataset_info(self, dataset, dtypes, stypes, rtypes, tiers, dformat, target=0):
        "Return common dataset info in specified data format"
        row = self.dbs.dataset_info(dataset)
        if  row:
            releases = [rname for _rid,rname in self.dbs.dataset_release_versions(dataset)]
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
            sites = [sname for _rid,sname in self.phedex.sites(dataset)]
            nsites = len(sites)
            for site in sites:
                stier = site_tier(site)
                stypes['s_%s'%stier] += 1
            dataset_id = row['rid']
            era = genkey(row['acquisition_era_name'], self.salt, 5)
            create_dn = self.sitedb.dnid(row['create_by'])
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
            rec = dict(dataset=dataset_id, primds=prim, procds=proc, tier=tier,
                    dtype=dtype, created=create_dn, nrel=nrels, nsites=nsites,
                    nfiles=summary['num_file'], nlumis=summary['num_lumi'],
                    nblk=summary['num_block'], nevt=summary['num_event'],
                    size=summary['file_size'], era=era, target=target_str)
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
            headers.remove('target')
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

    def dataframe(self, timeframe, seed, dformat, metric, dbs_extra=100, verbose=0):
        """Form a dataframe from various CMS data-providers"""
        dtypes, stypes, rtypes, tiers = self.data_types()
        if  dformat == 'csv':
            # seed dataset to determine headers of the dataframe
            rows = self.dataset_info(seed, dtypes, stypes, rtypes, tiers, 'headers')
            headers = [r for r in rows][0]
            yield ','.join(headers)
        if  not timeframe: # request new dataset
            new_datasets = self.dbs.new_datasets()
            for dataset in new_datasets:
                rows = self.dataset_info(dataset, dtypes, stypes, rtypes, tiers, dformat)
                for row in rows:
                    yield row
            return
        # get list of popular datasets in certain time frame
        res = [r for r in self.popdb.dataset_stat(timeframe[0], timeframe[1])]
        popdb_datasets = {} #
        for row in res:
            dataset = row['dataset']
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
            rows = self.dataset_info(dataset, dtypes, stypes, rtypes, tiers, dformat, target)
            popdb_datasets[dataset] = row
            for row in rows:
                yield row

        # get list of datasets from DBS and discard from this list
        # those who were presented in popdb
        dbs_datasets = [d for d in self.dbs.datasets() if d not in popdb_datasets.keys()]
        for dataset in random.sample(dbs_datasets, dbs_extra):
            rows = self.dataset_info(dataset, dtypes, stypes, rtypes, tiers, dformat)
            for row in rows:
                yield row

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
