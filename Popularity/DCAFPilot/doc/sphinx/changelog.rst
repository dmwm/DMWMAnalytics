DCAFPilot release notes
=======================

Release 0.X.Y series
--------------------
This release series is targeted to identify necessary step, workflow,
procedures required to build suitable dataframe for data analysis. We also try
to identify necessary metrics for such analysis.

0.0.X releases are preliminary implementation of all components

- 0.0.26

  - generate persistent rid for people/releases/sites cache entries
  - add new slides for CMS Computing Data Mining talk

- 0.0.21

  - move VW into src/python domain

- 0.0.18

  - add multitask option into configuration and the code. It uses
    multiprocessing module to concurrently submit url calls to data-services

- 0.0.17
  
  - switch to use capped collection analytics cache, it is configurable via
    etc/dcaf.cfg file and default size is 5GB

- 0.0.16
  
  - add static web service

- 0.0.15

  - add cron4dataframe and cron4model scripts to generate dataframes
    and run models via cronjobs
  - add new tool newdata, required by cron4model

- 0.0.14

  - add overlap option and turn it off by default in all generator
    scripts. This will allow to use dataframe (popDB) with dates which
    will not overlap

- 0.0.12

  - add multiprocess functionality to fetch information about dataset from
    various data-services

- 0.0.10

  - add code to use different access point for popularity DB, one within CERN
    network does not require authentication while another goes through CERN SSO
    for clients outside CERN network. In later case used must supply his/her
    credentials. Please note, that CERN SSO does not work with proxy files.

- 0.0.9

  - re-factor sso_reader to support cern-get-sso-cookie tool which allows
    usage of proxy file when accessing the site. This is required to run
    DCAFPilot as service on CERN VM where we use proxies

- 0.0.8

  - use get_key_cert in sso_reader

- 0.0.7

  - use get_key_cert in getdata, this will allow to use X509 certificates

- 0.0.6

  - add tier lookup
  - add tier classification during verification step

- 0.0.5

  - add fopen and convert code to use it
  - add support for VW, xgboost algorithms
  - add CSV to libSVM data format converter
  - add Pilot1 talks, CMS and CERN IT
    - https://indico.cern.ch/event/365073/
    - https://indico.cern.ch/event/368319/

- 0.0.4

  - Fine-tuned release which allows to perform data analysis. It includes
    the following steps:

    - dataframe generation
    - model builder
    - data transformation tools
    - prediction

- 0.0.3

  - Second usable release of DCAFPilot which provides all PopularityDB
    metrics.

- 0.0.2

  - First usable release of DCAFPilot which is based on normalized target
    variable (taken as naccess variable from PopularityDB).
