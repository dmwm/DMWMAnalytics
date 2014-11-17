#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=
"""
File       : vw_models.py
Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
Description: This script will perform multiple VW training
             passes and average results among them.
"""

# system modules
import os
import sys
import shutil
import random
import optparse

class OptionParser:
    """Option parser"""
    def __init__(self):
        self.parser = optparse.OptionParser()
        self.parser.add_option("--train", action="store", type="string",
           default="", dest="vwtrain", help="specify input VW train file")
        self.parser.add_option("--test", action="store", type="string",
           default="", dest="vwtest", help="specify input VW test file")
        self.parser.add_option("--out", action="store", type="string",
           default="", dest="vwout", help="specify output VW prediction file")
        self.parser.add_option("--headers", action="store", type="string", dest="headers",
           default="", help="specify output header")
        self.parser.add_option("--opts", action="store", type="string", dest="vwopts",
           default="--passes 40 -l 0.85 --loss_function quantile --quantile_tau 0.6",
           help="specify VW options")
        self.parser.add_option("--passes", action="store", type="int", dest="passes",
           default=10, help="specify number of passes")
    def get_opt(self):
        """Returns parse list of options"""
        return self.parser.parse_args()

def line_offsets(fname):
    """Read in the file once and return a list of line offsets"""
    line_offset = []
    offset = 0
    for _, line in enumerate( open(fname) ):
        line_offset.append(offset)
        offset += len(line)
    return line_offset

def shuffle(vwin, vwout, seed=0):
    "Read input VW file and write out VW with shuffled lines"
    if  seed:
        random.seed(seed)
    offsets = line_offsets(vwin)
    nlines = len(offsets)
    indices = range(nlines)
    random.shuffle(indices)
    with open(vwin, 'r') as istream, open(vwout, 'wb') as ostream:
        for idx in indices:
            istream.seek(offsets[idx])
            line = istream.readline()
            ostream.write(line)

def process(vwtrain, vwtest, vwopts, passes=10):
    "Perform multi-stage processing"
    wdir = '/tmp/vw'
    if  os.path.isdir(wdir):
        shutil.rmtree(wdir)
    os.mkdir(wdir)
    predictions = []
    for idx in range(passes):
        vwname = '%s/%s.%s' % (wdir, vwtrain.split('/')[-1], idx)
        if  idx:
            shuffle(vwtrain, vwname, idx)
        else:
            os.system('cp %s %s' % (vwtrain, vwname))
        vwmodel = '%s/model.%s' % (wdir, idx)
        vwpred = '%s/preds.%s' % (wdir, idx) 
        cmd = 'vw %s -c -k -f %s %s' % (vwname, vwmodel, vwopts)
        print cmd
        os.system(cmd)
        cmd = 'vw %s -t -i %s -p %s' % (vwtest, vwmodel, vwpred)
        print cmd
        os.system(cmd)
        preds = {}
        for _, line in enumerate( open(vwpred) ):
            prob, uid = line.split()
            preds[uid.strip()] = float(prob.strip())
        predictions.append(preds)
    final_preds = {}
    for pdict in predictions:
        for uid, prob in pdict.iteritems():
            uid = long(uid)
            if  uid in final_preds:
                val = (final_preds[uid] + prob)/2.
                final_preds[uid] = val
            else:
                final_preds[uid] = prob
    return final_preds

def main():
    "Main function"
    optmgr = OptionParser()
    opts, _ = optmgr.get_opt()
    if  not opts.vwtrain or not opts.vwtest or not opts.vwopts:
        print "Please provide train/test/opts options, for details see --help"
        sys.exit(1)
    preds = process(opts.vwtrain, opts.vwtest, opts.vwopts, opts.passes)
    with open(opts.vwout, 'w') as ostream:
        ostream.write(opts.headers+'\n')
        keys = sorted(preds.keys())
        for key in keys:
            ostream.write('%s,%f\n' % (key, preds[key]))

if __name__ == '__main__':
    main()
