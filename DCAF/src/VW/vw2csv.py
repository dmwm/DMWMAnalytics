#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=
"""
File       : vw2csv.py
Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
Description: Read VW output and convert to CSV format
"""

# system modules
import os
import sys
import optparse

class OptionParser:
    """Option parser"""
    def __init__(self):
        self.parser = optparse.OptionParser()
        self.parser.add_option("--train", action="store", type="string",
                               default="", dest="vwtrain",
             help="specify input VW train file")
        self.parser.add_option("--test", action="store", type="string",
                               default="", dest="vwtest",
             help="specify input VW test file")
    def get_opt(self):
        """Returns parse list of options"""
        return self.parser.parse_args()

def features(fname):
    "Find full list of features"
    flist = []
    with open(fname, 'r') as stream:
        for line in stream.readlines():
            values = line.split('|f')[-1]
            features = dict([v.split(':') for v in values.split()])
            flist = list(set(flist+features.keys()))
    return flist

def vw2csv(flist, fname, write_target=True):
    "Convert given VW file into csv using given list of features"
    oname = '%s.csv' % fname
    header = False
    with open(fname, 'r') as istream, open(oname, 'w') as ostream:
        if  not header:
            if  write_target:
                ostream.write(','.join(['id']+flist+['target']))
            else:
                ostream.write(','.join(['id']+flist))
            ostream.write('\n')
        for line in istream.readlines():
            uid, values = line.split('|f')
            target, uid = uid.replace("'", '').split()
            fdict = dict([v.split(':') for v in values.split()])
            items = [uid]
            for key in flist:
                items.append(fdict.get(key, 0))
            if  write_target:
                items.append(target)
            ostream.write(','.join([str(i) for i in items]))
            ostream.write('\n')

def main():
    "Main function"
    optmgr = OptionParser()
    opts, _ = optmgr.get_opt()
    trainfile = opts.vwtrain
    testfile = opts.vwtest
    if  not trainfile or not testfile:
        print "Usage: %s --help" % __file__
        sys.exit(0)
    flist_train = features(trainfile)
    flist_test = features(testfile)
    flist = list(set(flist_train+flist_test))
    vw2csv(flist, trainfile, write_target=True)
    vw2csv(flist, testfile, write_target=False)

if __name__ == '__main__':
    main()
