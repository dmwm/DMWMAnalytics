Generator tool
==============

.. toctree::
   :maxdepth: 4

The generator.py is a main tool which generates CMS meta-data. Here is a tool
options:

.. doctest::

   Usage: generator.py [options]

   Options:
     -h, --help            show this help message and exit
     -v VERBOSE, --verbose=VERBOSE
                           verbose output
     --system=SYSTEM       specify CMS system: dbs or phedex
     --generate=GENERATE   specify desired meta-data to generate: datasets,
                           blocks, files, runs, lumis
     --in=INPUT            specify input generator JSON file
     --out=OUTPUT          specify output JSON file
     --number=NUMBER       specify number of entities to generate/add
     --prim=PRIM           specify primary dataset name
     --proc=PROC           specify processed dataset name
     --tier=TIER           specify data-tier name
     --action=ACTION       specify action to be applied for given input.
                           Supported actions: add_blocks, add_files, gen_blocks,
                           gen_files

DBS workflow
============

To generate DBS meta-data we start with dataset generation. For example the
following command will generate 2 datasets which will be stored in datasets.json file

.. doctest::

   ./generator.py --system=dbs --generate=datasets --number=2

Let's proceed and generate 10 blocks for our datasets. In this step we will
explicitly specify the output JSON file

.. doctest::

   ./generator.py --system=dbs --in=datasets.json --out=dbs_blocks.json --number=10 --action=gen_blocks


Phedex workflow
===============

We start in a similar way with DBS, but in this case provide phedex as a system value

.. doctest::

   ./generator.py --system=phedex --generate=datasets --number=2

The output of the command will be

.. doctest::

    [{"dataset": {"blocks": [], "name": "/ond/aww/GEN", "is-open": "n", "dbs_name": "global"}}]

Since Phedex uses blocks as embeded property of the dataset to generate them we use a different
action, e.g. add_blocks

.. doctest::

   ./generator.py --system=phedex --in=datasets.json --out=blocks.json --number=1 --action=add_blocks

The output will be blocks.json file with the following structure

.. doctest::

    [{"dataset": {"blocks": [
                 {"block": {"name": "/ond/aww/GEN#e08akg6h-v59k-2jsx-xkhp-mzu6h8aw99gv"}}],
      "name": "/ond/aww/GEN", "is-open": "n", "dbs_name": "global"}}]

Now if we want to add files to the block we will issue the following command

.. doctest::

   ./generator.py --system=phedex --in=blocks.json --out=files.json --number=2 --action=add_files

Here the output of files.json file

.. doctest::
    [{"dataset": {"blocks": [
                 {"block": {"files": [
                           {"file": {"checksum": "cksum:4861,adler32:7845",
                                     "bytes": 38, "name": "/store/cms/xvwqa.root"}},
                           {"file": {"checksum": "cksum:6013,adler32:9914",
                                     "bytes": 35, "name": "/store/cms/dluce.root"}}],
                  "nfiles": 2, "size": 73,
                  "name": "/ond/aww/GEN#e08akg6h-v59k-2jsx-xkhp-mzu6h8aw99gv"}}], 
      "name": "/ond/aww/GEN", "is-open": "n", "dbs_name": "global"}}]
