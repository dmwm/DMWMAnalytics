DCAF stands for Data and Computing Analytics Framework.
The aim of this project is to collect information from
CMS data-services and represent it in a form suitable
for analysis, e.g. machine learning tools. For full
description of CMS analytics challenge please refer to this
twiki [1].

We foresee that this project will require uses of different
technique, e.g. standard machine learning, online learning
or custom based solutions, see [2,3,4,5]. Usage of common
frameworks or languages is desired [6,7,8].

The framework consists of several layers:
- storage layer, which can be used to keep information from various
  CMS data-services. Currently, DCAF uses MongoDB and
  associated py-mongo driver as a storage solution, but
  it can be replaced with any other key-value store or RDBMS database.
- mapping layer to provide mapping between sensitive information and its
  numerical representation, e.g. DNs into set of unique ids
- aggregated layer which collects and merge information from various
  CMS data-sources
- representation layer will take care of data representation suitable
  for analysis framework, e.g. represent our dataframe into CSV data-format
- analysis layer which will either use a custom analysis algorithm or
  provide bridge to other learning system libraries. The easiest solution
  would be to use python sklearn library [7] which already provides broad
  variety of learning algorithms.

Dependencies
------------
DCAF currently depends on MongoDB. The MongoDB is object-oriented database. It
is distributed as a binary package which is available from MongoDB [9] web
site. Just download appropriate package for your underlying OS and run mongodb
as following:

```
port=XXXX # setup your favorite port number
mongod --fork --dbpath=/path/mongodb/db --port $port --nohttpinterface
--logpath /path/mongodb/logs/mongodb.log --logappend
```

The DCAF etc/dcaf.cfg configuration file is place where you'll specify
your port and database collections.

The pymongo driver [10] is freely available python driver for MongoDB.
It can be installed via pip or any package management tools on your OS
as well as normal python package (download, untar, run python setup.py
install).

Usage
-----
To use DCAF package simply setup your environment, see setup.sh for
example, and run dataframe script as following

```
# to get some help
dataframe --help
Usage: dataframe [options]

Options:
  -h, --help       show this help message and exit
  --start=START    Start timestamp
  --stop=STOP      Stop timestamp
  --format=FORMAT  Output file format
  --config=CONFIG  Config file

# to run a script
dataframe --start=2012-6-26 --stop=2012-7-3
```

References
----------

[1] https://twiki.cern.ch/twiki/bin/view/Main/CMSDataMiningForAnalysisModel

[2] http://www.wikiwand.com/en/Machine_learning

[3] http://www.wikiwand.com/en/Online_machine_learning

[4] http://www.wikiwand.com/en/Vowpal_Wabbit

[5] http://www.wikiwand.com/en/Stochastic_gradient_descent

[6] http://www.wikiwand.com/en/R_(programming_language)

[7] http://scikit-learn.org/

[8] http://0xdata.com/

[9] http://www.mongodb.org/downloads

[10] http://api.mongodb.org/python/current/
