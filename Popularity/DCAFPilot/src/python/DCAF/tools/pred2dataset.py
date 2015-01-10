#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=
"""
File       : pred2dataset.py
Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
Description: Script which convert prediction file (dataset_id,prediction)
             into dataset,prediction
"""

# system modules
import os
import sys
import optparse

# mongodb modules
from pymongo import MongoClient

class OptionParser():
    def __init__(self):
        "User based option parser"
        self.parser = optparse.OptionParser()
        self.parser.add_option("--fin", action="store", type="string",
            dest="fin", default="", help="Input file")
        self.parser.add_option("--fout", action="store", type="string",
            dest="fout", default="", help="Output file")
        uri = 'mongodb://localhost:8230'
        self.parser.add_option("--uri", action="store", type="string",
                dest="uri", default=uri, help="DCAF cache (MongoDB) uri, default %s" %  uri)
        self.parser.add_option("--sep", action="store", type="string",
                dest="sep", default=",", help="Output file separator, default comma")
    def get_opt(self):
        "Return list of options"
        return self.parser.parse_args()

def convert(fin, fout, uri, sep=','):
    """
    Convert input prediction file (id,prediction) into (dataset,prediction)
    by using DCAFPilot cache
    """
    client = MongoClient(uri)
    mgr = client['analytics']['datasets']
    headers = None
    with open(fin, 'r') as istream, open(fout, 'w') as ostream:
        for line in istream.readlines():
            did, dbs, pred = line.replace('\n', '').split(sep)
            if  not headers:
                headers = '%s,%s,%s' % (did, dbs, pred)
                continue
            spec = {'dataset_id':int(did), 'dbs_instance':int(dbs)}
            res = mgr.find_one(spec)
            if  res:
                ostream.write("%5.3f%s%s\n" % (float(pred),sep,res['dataset']))

def main():
    "Main function"
    optmgr  = OptionParser()
    opts, _ = optmgr.get_opt()
    convert(opts.fin, opts.fout, opts.uri, opts.sep)

if __name__ == '__main__':
    main()
