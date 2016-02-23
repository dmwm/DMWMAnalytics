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
  -verbose int
    	Verbose level, support 0,1,2
```

### Examples
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
```
