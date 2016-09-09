# Transfer metrics analytics

LHC experiments transfer more than 10 PB/week between all grid sites using the FTS transfer service.
In particular, CMS manages almost 5 PB/week of FTS transfers with PhEDEx.

FTS sends metrics about each transfer (e.g. transfer rate, duration) to a central HDFS storage at CERN.
We propose to use ML techniques to process this raw data and generate predictions of transfer rates/latencies on all
links between Grid sites.

The first task in this project is to prepare the data in a format suitable for ML, converting them json format ascii files to a flat table format. Process from unstructured to numerical representation needs to be done. 

The next step is to evaluate different ML algorithms for a regression problem, and produce predictions for the transfer rate on each link. We want to evaluate the performance of running ML algorithms with scripts based on common libraries (e.g. python scikit-learn) and compare with running ML directly on the Hadoop cluster with Spark.

Finally the predictions need to be fed back to PhEDEx  routing,  so that it can use a better estimate of transfer rates/latencies when choosing the best path to transfer each file.

After this is completed, additional goals for this project will be to extend the regression study also to data transferred using the xrootd protocol (for which we have raw data on HDFS) and to PhEDEx  transfer logs (which need to be imported into HDFS)

Tools: python language, Spark ML libraries, HDFS

## Data location

FTS raw data are collected on the HDFS cluster hadalytic.cern.ch
The data can be found in the following directory:

```
hdfs dfs -ls /user/wdtmon/fts
```

The records are in json fomat, the format is documented here:

https://twiki.cern.ch/twiki/bin/view/LCG/WLCGTransferMonitoring

And an example record is this:

```
 {"tr_id":"2016-06-22-2201__tbn18.nikhef.nl__grid002.ft.uam.es__856147523__4d964812-2576-58e0-92d0-a2ef2e24afac","endpnt":"fts3.cern.ch","src_srm_v":"2.2.0","dest_srm_v":"2.2.0","vo":"atlas","src_url":"srm://tbn18.nikhef.nl:8446/srm/managerv2?SFN=/dpm/nikhef.nl/home/atlas/atlasdatadisk/rucio/mc15_13TeV/5d/cb/EVNT.08775130._013235.pool.root.1","dst_url":"srm://grid002.ft.uam.es:8443/srm/managerv2?SFN=/pnfs/ft.uam.es/data/atlas/atlasdatadisk/rucio/mc15_13TeV/5d/cb/EVNT.08775130._013235.pool.root.1","src_hostname":"tbn18.nikhef.nl","dst_hostname":"grid002.ft.uam.es","src_site_name":"","dst_site_name":"","t_channel":"srm://tbn18.nikhef.nl__srm://grid002.ft.uam.es","timestamp_tr_st":"1466632862284","timestamp_tr_comp":"1466632865616","timestamp_chk_src_st":"1466632860931","timestamp_chk_src_ended":"1466632861355","timestamp_checksum_dest_st":"1466632865692","timestamp_checksum_dest_ended":"1466632865737","t_timeout":"1121","chk_timeout":"1800","t_error_code":"","tr_error_scope":"","t_failure_phase":"","tr_error_category":"","t_final_transfer_state":"Ok","tr_bt_transfered":"10565043","nstreams":"3","buf_size":"0","tcp_buf_size":"0","block_size":"0","f_size":"10565043","time_srm_prep_st":"1466632860931","time_srm_prep_end":"1466632862284","time_srm_fin_st":"1466632865616","time_srm_fin_end":"1466632865692","srm_space_token_src":"","srm_space_token_dst":"ATLASDATADISK","t__error_message":"","tr_timestamp_start":"1466632860151.000000","tr_timestamp_complete":"1466632866232.000000","channel_type":"urlcopy","user_dn":"/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=ddmadmin/CN=531497/CN=Robot: ATLAS Data Management","file_metadata":{"adler32": "68e800b9", "src_type": "DISK", "src_rse": "NIKHEF-ELPROD_DATADISK", "request_id": "c0c7d290714848f8a1592873a2aafe3f", "src_rse_id": "4ed5590e5d6e4008b1b9e92253962784", "name": "EVNT.08775130._013235.pool.root.1", "request_type": "transfer", "filesize": 10565043, "dest_rse_id": "a07afdb2953442f78bd87136e32c2674", "activity": "Data Consolidation", "dst_rse": "UAM-LCG2_DATADISK", "dst_type": "DISK", "scope": "mc15_13TeV", "md5": null},"job_metadata":{"multi_sources": true, "issuer": "rucio"},"retry":"0","retry_max":"0","job_m_replica":"true","job_state":"FINISHED","is_recoverable":"1"}
```

More example records are found in the data directory in this repository.

The required fields will have to be extracted from the jsons and stored as flat csv for further processing

For more details on the data collection, see:

http://wdtmon.web.cern.ch/wdtmon/index.html
http://awg-virtual.cern.ch/data-sources-index/projects/#wdtmon-fts

The xrootd raw data are found on the same cluster:

```
hdfs dfs -ls /user/wdtmon/xrootd/cms
```

### Initial work

The initial work on this project has been started by CERN summer students
and can be found here:

https://github.com/nikmagini/TransferMonitoring
