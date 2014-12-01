This file contains description of dataframe produced by DCAFPilot project.

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

target: target metric reported by PopularityDB, current default is normalized
number of access to given dataset (other metrics can be normalized CPU and
number of users associated with given dataset).

