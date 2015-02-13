DCAFPilot release notes
=======================

Release 0.X.Y series
--------------------
This release series is targeted to identify necessary step, workflow,
procedures required to build suitable dataframe for data analysis. We also try
to identify necessary metrics for such analysis.

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
