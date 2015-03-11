Introduction
============

The CMS experiment at CERN has started analytics project to help to understand
its computing resources. Ideally, we'd like to learn from data how the data is
used in CMS, understand user behavior, habits and predict how user will use
computer resources.

The DCAFPilot framework is a pilot project for CMS data analytics. Its scope
is limited to several tasks:

1. Identify set of tools, metrics and approaches suitable for the initial goal

   - identification of Machine Library (ML) toolkits
   - choice of algorithms, i.e. classification vs regression
   - identification of CMS data-services which can contribute to initial dataframe
   - online/offline learning approaches

2. Data acquisition and model analysis

   - construct initial dataframe for ML analysis
   - run classification/regression models and make prediction
   - chose suitable metrics

3. Identify strategy and sources for dataset popularity prediction

   - choice of algorithm(s)/model(s)
   - approach, e.g. time-series
   - usage of structured CMS data-services
   - usage of unstructured data sources, e.g. HN, Calendar systems
   - identification of suitable metrics/classes which influences prediction

4. Machinery setup & automation

   - acquiring the data
   - data anonymity procedure
   - data transformation
   - writing prediction
   - result verification for past prediction
   - model tuning

5. Integration of prediction with reqmgr/PhEDEx subscription

   - merge prediction with reqmgr activity
   - auto-subscribe "popular" data

6. Production deployment

   - data-service components
   - identification of hardware resources
   - manage scripts and production delivery
