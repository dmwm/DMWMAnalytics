#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=
"""
File       : verify_prediction.py
Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
Description: Verify prediction file against popular datasets
"""
from __future__ import print_function

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
        self.parser.add_option("--format", action="store", type="string",
            dest="oformat", default="", help="Output format, plain or csv, default plain")
        self.parser.add_option("--verbose", action="store", type="int",
            dest="verbose", default=False, help="verbose mode")
        msg  = "Column of --popdb used in evaluation of popular database, "
        msg += "default None - no additional filtering will be used"
        self.parser.add_option("--target", action="store", type="string",
            dest="target", default=None, help=msg)
        msg  = "Value to determine popular databases, used with --target value,"
        msg += "e.g. --target=naccess --target-thr=10, records holding naccess>10 "
        msg += "will be evaluated as popular"
        self.parser.add_option("--target-thr", action="store", type="float",
            dest="thr", default=None, help=msg)
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
            try:
                dataset = row.pop('dataset')
                pdict[dataset] = row
            except:
                pass
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
        f1score = 2*precision*recall/(precision+recall)
    except:
        f1score = 0
    return accuracy, precision, recall, f1score

def datasets2tiers(datasets):
    "Convert list of datasets to dict of tier counters"
    tiers = {}
    for dataset in datasets:
        _, prim, proc, tier = dataset.split('/')
        if  tier in tiers:
            tiers[tier] += 1
        else:
            tiers[tier] = 1
    return tiers

def classify(datasets):
    "Classify datasets"
    tiers = datasets2tiers(datasets)
    pairs = [(v, k) for k, v in tiers.items()]
    width = ''
    pairs.sort()
    pairs.reverse()
    for key, val in pairs:
        if  not width:
            width = len(str(key))+1
        print('%s %s %s'  % (key, ' '*(width-len(str(key))), val))

def percentage(tp, tn, fp, fn):
    "Return percentage of TP/TN/FP/FN"
    tot = float(tp+tn+fp+fn)
    return 100*tp/tot, 100*tn/tot, 100*fp/tot, 100*fn/tot

def classify_all(tplist, tnlist, fplist, fnlist):
    "Classify datasets"
    tptiers = datasets2tiers(tplist)
    tntiers = datasets2tiers(tnlist)
    fptiers = datasets2tiers(fplist)
    fntiers = datasets2tiers(fnlist)
    alltiers = set(tptiers.keys()+tntiers.keys()+fptiers.keys()+fntiers.keys())
    width = max([len(t) for t in alltiers])
    title = 'TIER ' + ' '*(width-len('TIER')) + '  TP(%)  TN(%)  FP(%)  FN(%)'
    print(title)
    print('-'*len(title))
    for tier in sorted(alltiers):
        pad = ' '*(width-len(tier))
        tp, tn, fp, fn = percentage(tptiers.get(tier, 0),
                                    tntiers.get(tier, 0),
                                    fptiers.get(tier, 0),
                                    fntiers.get(tier, 0))
        print('%s %s %6.2f %6.2f %6.2f %6.2f' % (tier, pad, tp, tn, fp, fn))
    print()

def verify_prediction(pred, popdb, oformat, verbose, target, thr):
    "Verify prediction file against popdb one"
    pdict = read_popdb(popdb)
    total = 0
    popular = 0
    totpop = 0
    tpos = 0
    tneg = 0
    fpos = 0
    fneg = 0
    tp_list = []
    tn_list = []
    fp_list = []
    fn_list = []
    def is_popular(dataset, pdict):
        return (target is None or float(pdict[dataset][target]) > thr)
    for line in fopen(pred, 'r').readlines():
        prob, dataset = line.replace('\n', '').split(',')
        total += 1
        if  float(prob)>0:
            popular += 1
        if  dataset in pdict and is_popular(dataset, pdict):
            totpop += 1
            if  float(prob)>0:
                tpos += 1
                tp_list.append(dataset)
                if  verbose>1:
                    print('TP, prob=%s dataset=%s' % (prob, dataset))
            else:
                fneg += 1
                fn_list.append(dataset)
                if  verbose>1:
                    print('FN, prob=%s dataset=%s' % (prob, dataset))
        else:
            if  float(prob)>0:
                fpos += 1
                fp_list.append(dataset)
                if  verbose>1:
                    print('FP, prob=%s dataset=%s' % (prob, dataset))
            else:
                tneg += 1
                tn_list.append(dataset)
                if  verbose>1:
                    print('TN, prob=%s dataset=%s' % (prob, dataset))
    accuracy, precision, recall, f1score = metrics(tpos, tneg, fpos, fneg)
    print("# dataset in popdb sample :", len(pdict.keys()))
    print("# datasets we predict     :", total)
    print("# datasets in popular set :", totpop)
    print("Predicted as popular      :", popular)
    print()
    def perc(vvv):
        return '%s' % round(vvv*100./total, 1)
    def space(vvv):
        return '%s%s' % (vvv, ' '*(len(str(total))-len(str(vvv))))
    tptiers = datasets2tiers(tp_list)
    tntiers = datasets2tiers(tn_list)
    fptiers = datasets2tiers(fp_list)
    fntiers = datasets2tiers(fn_list)
    alltiers = set(tptiers.keys()+tntiers.keys()+fptiers.keys()+fntiers.keys())
    if  oformat=='csv':
        out = 'cls,tp,tn,fp,fn\n'
        out += '%s,ALL,%s,%s,%s,%s\n' \
                % (pred.split('.')[0], perc(tpos), perc(tneg), perc(fpos), perc(fneg))
        for tier in sorted(alltiers):
            tp, tn, fp, fn = percentage(tptiers.get(tier, 0),
                                        tntiers.get(tier, 0),
                                        fptiers.get(tier, 0),
                                        fntiers.get(tier, 0))
            out += '%s,%s,%s,%s,%s,%s\n' \
                    % (pred.split('.')[0], tier, tp, tn, fp, fn)
        print(out)
    else:
        if  verbose:
            print("True positive             : %s, %s%%" % (space(tpos), perc(tpos)))
            print("True negative             : %s, %s%%" % (space(tneg), perc(tneg)))
            print("False positive            : %s, %s%%" % (space(fpos), perc(fpos)))
            print("False negative            : %s, %s%%" % (space(fneg), perc(fneg)))
            print()
        classify_all(tp_list, tn_list, fp_list, fn_list)
        width = max([len(t) for t in alltiers])
        msg = 'ALL tiers'
        pad = ' '*(width-len(msg))
        tp, tn, fp, fn = percentage(tpos, tneg, fpos, fneg)
        print("%s %s %6.2f %6.2f %6.2f %6.2f\n" % (msg, pad, tp, tn, fp, fn))
        if  verbose:
            print("Classification of TP sample")
            classify(tp_list)
            print("Classification of TN sample")
            classify(tn_list)
            print("Classification of FP sample")
            classify(fp_list)
            print("Classification of FN sample")
            classify(fn_list)
        print("Accuracy                  :", accuracy)
        print("Precision                 :", precision)
        print("Recall                    :", recall)
        print("F1-score                  :", f1score)

def main():
    optmgr  = OptionParser()
    opts, _ = optmgr.get_opt()
    verify_prediction(opts.pred, opts.popdb, opts.oformat, opts.verbose,
        opts.target, opts.thr)
if __name__ == '__main__':
    main()
