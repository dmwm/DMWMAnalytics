#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=

"""
File       : preds2dataset.py
Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
Description: Script which convert prediction file (dataset_id,prediction)
into dataset,prediction using datasets and prediction files
"""

# system modules
import optparse

# local modules
from DCAF.utils.utils import fopen

# pandas
import pandas as pd

class OptionParser():
    "User based option parser"
    def __init__(self):
        usage  = 'Usage: %prog [options]\n'
        usage += 'Description: convert prediction file into human readable form\n'
        usage += 'Example: %prog --fin=pred.txt --datasets=datasets.csv.gz --fout=pred.txt.out'
        self.parser = optparse.OptionParser(usage=usage)
        self.parser.add_option("--fin", action="store", type="string", \
            dest="fin", default="", help="Input file")
        self.parser.add_option("--fout", action="store", type="string", \
            dest="fout", default="", help="Output file")
        self.parser.add_option("--datasets", action="store", type="string", \
            dest="datasets", default="", help="DBS datasets input file")
        self.parser.add_option("--sep", action="store", type="string", \
            dest="sep", default=",", help="Output file separator, default comma")
    def get_opt(self):
        "Return list of options"
        return self.parser.parse_args()

def convert(fin, fout, datasets, sep=','):
    """
    Convert input prediction file (id,prediction) into (dataset,prediction)
    by using datasets file
    """
    headers = None
    df = pd.read_csv(datasets)
    with fopen(fin, 'r') as istream, fopen(fout, 'w') as ostream:
        for line in istream.readlines():
            did, dbs, pred = line.replace('\n', '').split(sep)
            if  not headers:
                headers = '%s,%s,%s' % (did, dbs, pred)
                continue
            res = df[(df.hash==int(did)) & (df.dbsinst==int(dbs))]
            if  not res.empty:
                dataset = res.get_value(res.index[0], 'dataset')
                ostream.write("%5.3f%s%s\n" % (float(pred), sep, dataset))

def main():
    "Main function"
    optmgr = OptionParser()
    opts, _ = optmgr.get_opt()
    convert(opts.fin, opts.fout, opts.datasets, opts.sep)

if __name__ == '__main__':
    main()
