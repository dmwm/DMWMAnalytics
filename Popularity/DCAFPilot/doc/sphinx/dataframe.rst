dataframe tool
==============

.. toctree::
   :maxdepth: 4

The dataframe is a main tool to capture information from various CMS
data-services and build anonymized dataset:

.. doctest::

    model --help
    Usage: dataframe.py [options]

    Options:
      -h, --help            show this help message and exit
      --fout=FOUT           Output file
      --seed-dataset=SEED   Seed dataset,
                            default=/ZMM/Summer11-DESIGN42_V11_428_SLHC1-v1/GEN-
                            SIM
      --dbs-extra=DBS_EXTRA
                            Extra datasets from DBS which were not shown in
                            popularityDB, default 1000
      --start=START         Start timestamp in YYYYMMDD format
      --stop=STOP           Stop timestamp in YYYYMMDD format
      --format=DFORMAT      Output file format, deafult csv (supported csv, vw)
      --config=CONFIG       Config file, default etc/dcaf.cfg
      --verbose=VERBOSE     Verbosity level, default 0
      --seed-cache          Seed internal cache with DBS/SiteDB database content
      --clean-cache         Clean-up cache
      --remove-doc=DOCID    Remove given docid from cache
      --newdata             Get new set of data from DBS, instead of popularity DB

Example
=======

To start, we need to seed our cache with datasets known in DBS.
We assume that you successfully setup your local cache agent (MongoDB).
Then invoke dataframe as following:

.. doctest::

    dataframe --seed-cache --verbose=1

From that on, we're ready to generate new dataframes.
We start with one week of data in 2014 and generate it with additional
non-popular dataset taken from DBS (see --dbs-extra option):

.. doctest::

    dataframe --start=20141224 --stop=20141231 --dbs-extra=100 --verbose=1 --fout=dataframe-20141224-20141231.csv

Here we specified start and stop dates in (YYYYMMDD) date format, we added
100 non-popular dataset and saved output in CSV data format. Please note, that
this command will yield some output which you may save/redirect elsewhere for
debugging puprposes.

As a result a dataset will be generated and ready to use.

If you need to generate "new" data, i.e. those who did not acquire enough
history information in popularity DB, you can generate this sample as
following:

.. doctest::

    dataframe --start=20150101 --stop=20150108 --newdata --verbose=1 --fout=new-20150101-20150108.csv

Additional tools
----------------

When you generate plenty of datasets, it may be desired to transform and merge
them together. This section will provide you with documentation how to do these
steps.

First, let's transform data. For that we'll use transform_csv tool:

.. doctest::

    transform_csv --help
    Usage: transform_csv.py [options]

    Options:
      -h, --help        show this help message and exit
      --fin=FIN         Input file
      --fout=FOUT       Output file
      --target=TARGET   Target column name
      --target-thr=THR  Target threshold, default 0 (use -1 to keep the value
                        intact)
      --drops=DROPS     drops column names (comma separated)
      --verbose         Turn on verbose output

Its usage is quite clear. Here is an example how to transform our dataset into
classification problem by specifying target variable and its threshold. Also,
we'll drop a few variables from a dataset:

.. doctest::

    transform_csv --fin=new-20150101-20150108.csv.gz \
        --fout=newdata-20150101-20150108.csv.gz --target=naccess --target-thr=100
        --drops=nusers,totcpu,rnaccess,rnusers,rtotcpu,nsites,s_0,s_1,s_2,s_3,s_4,wct

Once data is trasformed we can merge several dataframes together into single
file. For that purpose we'll use merge_csv tool:

.. doctest::

    merge_csv --help
    Usage: merge_csv.py [options]

    Options:
      -h, --help   show this help message and exit
      --fin=FIN    Input files or input directory
      --fout=FOUT  Output file
      --verbose    Turn on verbose output

Here is an example how to merge dataframes from specific location into
single file:

.. doctest::

    merge_csv --fin=CMS-DMWM-Analytics-data/Popularity/DCAFPilot/data/0.0.3 \
        --fout=2014.csv.gz --verbose

