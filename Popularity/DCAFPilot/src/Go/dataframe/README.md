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
  -verbose int
    	Verbose level, support 0,1,2
```

### Examples

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
```
