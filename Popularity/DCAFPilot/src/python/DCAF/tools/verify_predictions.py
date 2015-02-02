#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=
"""
File       : verify_prediction.py
Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
Description: Verify prediction file against popular datasets
"""

# system modules
import optparse

# local modules
from DCAF.utils.utils import fopen

class OptionParser():
    def __init__(self):
        "User based option parser"
        usage  = 'Usage: %prog [options]\n'
        usage += 'Description: verify prediction file against popular dataset one retrieved from popularity DB\n'
        usage += 'Example: %prog --pred=pred.txt.out --popdb=popdb-20150101-20150108.txt'
        self.parser = optparse.OptionParser(usage=usage)
        self.parser.add_option("--pred", action="store", type="string",
            dest="pred", default="", help="Input prediction file")
        self.parser.add_option("--popdb", action="store", type="string",
            dest="popdb", default="", help="Input popular datasets file")
        self.parser.add_option("--verbose", action="store_true",
            dest="verbose", default=False, help="verbose mode")
    def get_opt(self):
        "Return list of options"
        return self.parser.parse_args()

def read_popdb(popdb):
    "Read popdb data"
    headers = []
    pdict = {}
    with fopen(popdb, 'r') as istream:
        while True:
            if  not headers:
                for row in istream.readline().replace('\n', '').split(','):
                    if  row == 'COLLNAME':
                        headers.append('dataset')
                    elif row == 'NACC':
                        headers.append('naccess')
                    elif row == 'RNACC':
                        headers.append('rnaccess')
                    else:
                        headers.append(row.lower())
                continue
            vals = istream.readline().replace('\n', '').split(',')
            if  len(vals) < 2:
                break
            row = dict(zip(headers, vals))
            dataset = row.pop('dataset')
            pdict[dataset] = row
    return pdict

def metrics(tpos, tneg, fpos, fneg):
    "Return accuracy, precision, recall, f1score"
    try:
        accuracy = float(tpos+tneg)/float(tpos+tneg+fpos+fneg)
    except:
        accuracy = 0
    try:
        precision = float(tpos)/float(tpos+fpos)
    except:
        precision = 0
    try:
        recall = float(tpos)/float(tpos+fneg)
    except:
        recall = 0
    try:
        f1score = 2*precition*recall/(precition+recall)
    except:
        f1score = 0
    return accuracy, precision, recall, f1score

def verify_prediction(pred, popdb, verbose=False):
    "Verify prediction file against popdb one"
    pdict = read_popdb(popdb)
    total = 0
    popular = 0
    totpop = 0
    tpos = 0
    tneg = 0
    fpos = 0
    fneg = 0
    for line in fopen(pred, 'r').readlines():
        prob, dataset = line.replace('\n', '').split(',')
        total += 1
        if  float(prob)>0:
            popular += 1
        if  dataset in pdict:
            totpop += 1
            if  verbose:
                naccess = pdict[dataset]['naccess']
                nusers = pdict[dataset]['nusers']
                print 'prob=%s nacc=%s nusers=%s %s' % (prob, naccess, nusers, dataset)
            if  float(prob)>0:
                tpos += 1
            else:
                fneg += 1
        else:
            if  float(prob)>0:
                fpos += 1
            else:
                tneg += 1
    accuracy, precision, recall, f1score = metrics(fpos, tneg, fpos, fneg)
    print "# dataset in popdb sample :", len(pdict.keys())
    print "# datasets we predict     :", total
    print "# datasets in popular set :", totpop
    print "Predicted as popular      :", popular
    print
    print "True positive             :", tpos
    print "True negative             :", tneg
    print "False positive            :", fpos
    print "False negative            :", fneg
    print
    print "Accuracy                  :", accuracy
    print "Precision                 :", precision
    print "Recall                    :", recall
    print "F1-score                  :", f1score

def main():
    optmgr  = OptionParser()
    opts, _ = optmgr.get_opt()
    verify_prediction(opts.pred, opts.popdb, opts.verbose)

if __name__ == '__main__':
    main()
