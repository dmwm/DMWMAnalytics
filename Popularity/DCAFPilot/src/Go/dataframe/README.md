<<<<<<< HEAD
### sitestat tool
sitestat tool designed to catch statistics from various CMS sites.
The underlying process follow these steps:

- Fetch all site names from SiteDB
- loop over specific time range, e.g. last 3m
  - create dates for that range
- Use popularity API (DSStatInTImeWindow) 
  to get summary statistics. The API returns various information about dataset
  usage on sites.
- Organize data in number of access bins
- For every bin collect dataset names
- Call DBS APIs to get dataset statistics via blocksummaries API.
- sum up info about file_size which will give total size used by specific site.

Here is example of sitestat tool usage

```
Usage of ./sitestat:
  -bins string
    	Comma separated list of bin values, e.g. 0,1,2,3,4 for naccesses or 0,10,100 for tot cpu metrics
  -breakdown string
    	Breakdown report into more details (tier, dataset)
  -dbsinfo
    	Use DBS to collect dataset information, default use PhEDEx
  -format string
    	Output format type, txt or json (default "txt")
  -metric string
    	Popularity DB metric (NACC, TOTCPU, NUSERS) (default "NACC")
  -profile
    	profile code
  -site string
    	CMS site name, use T1, T2, T3 to specify all Tier sites
  -tier string
    	Look-up specific data-tier
  -trange string
    	Specify time interval in YYYYMMDD format, e.g 20150101-20150201 or use short notations 1d, 1m, 1y for one day, month, year, respectively (default "1d")
=======
### dataframe tool
dataframe tool is designed to catch meta-data information from various CMS sites
and put it into a dataframe file for Machine Learning studies.
The underlying process follow these steps:

- fetch dataset names from PopDB gor a given interval of time
- supplement aforementioned list of dataset names with some
  random dataset from DBS (which represents non-popular dataset)
- loop over dataset names and capture meta-data information from
  DBS, PhEDEx, McM, Dashboard, etc. data-services
  - anonymize all information via internal hash function
- write out dataframe with meta-data attributes

Here is example of dataframe tool usage

```
Usage of ./dataframe:
  -chunkSize int
    	Chunk size for processing URLs (default 100)
  -datamap string
    	Generate datamap file for given attribute, e.g. dataset, tier
  -dbsExtra int
    	Extra number of DBS datasets not listed in popularity DB (default 1000)
  -fout string
    	Name of output file
  -newdata
    	Get new data from DBS instead of popularity DB
  -profile
    	profile code
  -start string
    	Start timestamp in YYYYMMDD format
  -stop string
    	Stop timestamp in YYYYMMDD format
  -test
    	test mode
>>>>>>> master
  -verbose int
    	Verbose level, support 0,1,2
```

### Examples
<<<<<<< HEAD
In all examples below we use T2_XX_Abc as a site name.

```
# list site statistics for last month
sitestat -site T2_XX_Abc -trange 1m

# list site statistics for specific time range
sitestat -site T2_XX_Abc -trange 20150201-20150205

# list site statistics for last 3 months
sitestat -site T2_XX_Abc -trange 3m

# list site statistics for last month and only count AOD data-tier
sitestat -site T2_XX_Abc -trange 1m -tier AOD

# list site statistics for last month with breakdown for all data-tiers
sitestat -site T2_XX_Abc -trange 1m -breakdown tier

# list site statistics for last month with breakdown for all datasets
sitestat -site T2_XX_Abc -trange 1m -breakdown dataset

# list site statistics for last month with breakdown for all data-tiers and look for NUSERS metric
sitestat -site T2_XX_Abc -trange 1m -metric NUSERS -breakdown tier

# by default sitestat relies on PhEDEx data-service to collect
# dataset information on site, but we may use DBS instead
sitestat -site T2_XX_Abc -trange 1m -dbsinfo

# return information in json data format
sitestat -site T2_XX_Abc -trange 1m -format json
=======

```
# run dataframe in a test mode
dataframe -start=20160221 -stop=20160220 -test -profile -verbose 2

# run dataframe to generate data for given period of time and using 10 extra DBS datasets
dataframe -start 20160216 -stop 20160216 -dbsExtra 10 -profile -verbose 1

# run dataframe to generate data for given period of time
dataframe -start 20160216 -stop 20160216

# run dataframe to generate new data (not from PopDB)
dataframe -start=20160223 -stop=20160224 -newdata -profile -verbose 1

# generate datamap file for datasets, the datamap file will contain hash:dataset pairs
dataframe -datamap datasets -profile -verbose 1

# generate datamap file for data-tiers, the datamap file will contain hash:tier pairs
dataframe -datamap tiers -profile -verbose 1
>>>>>>> master
```
