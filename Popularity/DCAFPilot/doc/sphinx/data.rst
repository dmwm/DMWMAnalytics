Data location
=============

DCAFPilot operates with a dataframe which is defined as a flat
comma separated value (CSV) file. For simplicity we already generated
several dataframes and stored them at CERN github repository.
They can be accessed as following:

.. doctest::

    git clone https://:@git.cern.ch/kerberos/CMS-DMWM-Analytics-data

Please refer to README.md file in each data directory.

Data description
================

The dataframe was constructed out of several CMS data-services:

- DBS, main CMS data catalog
- PhEDEx, data transfer service
- PopularityDB, CMS data-service which collects historical information
  about dataset accesses
- SiteDB, CMS personel database
- Dashboard, CMS job dashboard database

We extracted the following bits from every data-service:

id: unique id, it is constructed from tstamp, dbs instance id and dataset id as
following long('%s%s%s'%(tstamp,dbsinst,dataset_id)) % 2**30

cpu: CPU time reported by Dashboard data-service for given dataset

creator: anonymized DN of the user who created given dataset, reported by DBS

dataset: DBS dataset id (comes from DBS APIs/database backend)

dbs: DBS instance id

dtype: anonymized DBS data type (e.g. data, mc)

era: anonymized DBS acquisition era name associated with given dataset

nblk: number of blocks in given dataset, reported by DBS

nevt: number of events in given dataset, reported by DBS

nfiles: number of files in given dataset, reported by DBS

nlumis: number of lumi sections in given dataset, reported by DBS

nrel: number of releases associated with given dataset, reported by DBS

nsites: number of sites associated with given dataset, reported by Phedex

parent: parent id of given dataset, reported by DBS

primds: anonymized primary dataset name, reported by DBS

proc_evts: number of processed events, reported by Dashboard

procds: anonymized processed dataset name, reported by DBS

rel1_N: DBS release counter defined as N-number of series releases associated
with given dataset

rel2_N: DBS release counter defined as N-number of major releases associated
with given dataset

rel3_N: DBS release counter defined as N-number of minor releases associated
with given dataset

s_X: Phedex site counter, i.e. number of Tier sites holding this dataset
replica

size: size of the dataset, reported by DBS and normalized to GB metric

tier: anonymized tier name, reported by DBS

wct: wall clock counter for given dataset, reported by Dashboard

naccess: number of accesses to a dataset, reported by PopularityDB

nusers: number of users*days to a dataset, reported by PopularityDB

totcpu: number of cpu hours to accessed dataset, reported by PopularityDB

rnaccess: naccess(dataset)/SUM_i naccess(i), reported by PopularityDB

rnusers: nusers(dataset)/SUM_i nusers(i), reported by PopularityDB

rtotcpu: totcpu(dataset)/SUM_i totcpu(i), reported by PopularityDB
