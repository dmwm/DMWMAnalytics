#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable-msg=
"""
File       : logloss.py
Author     : Valentin Kuznetsov <vkuznet@gmail.com>
Description: script to calculate logloss function from given input
"""

# system modules
import os
import sys
import scipy as sp

import optparse

class OptionParser:
    """Option parser"""
    def __init__(self):
        self.parser = optparse.OptionParser()
        self.parser.add_option("--fpred", action="store", type="string",
                               default="", dest="fpred",
             help="specify prediction file")
        self.parser.add_option("--fobs", action="store", type="string",
                               default="", dest="fobs",
             help="specify prediction file")
    def get_opt(self):
        """Returns parse list of options"""
        return self.parser.parse_args()

def logloss(obs, pred):
    """LogLoss function
    https://www.kaggle.com/wiki/LogarithmicLoss
    """
    epsilon = 1e-15
    pred = sp.maximum(epsilon, pred)
    pred = sp.minimum(1-epsilon, pred)
    ll = sum(obs*sp.log(pred) + sp.subtract(1,obs)*sp.log(sp.subtract(1,pred)))
    ll = ll * -1.0/len(obs)
    return ll

def calc_logloss(fpred, fobs):
    "Calculate logloss value for input prediction/actual value files"
    obs = [float(r.replace('\n','').split(',')[-1]) for r in open(fobs) if not
            r.lower().startswith('id')]
    pred = [int(r.replace('\n','').split(',')[-1]) for r in open(fpred) if not
            r.lower().startswith('id')]
    print "obs", obs[:5]
    print "pred", pred[:5]
    print "LogLoss", logloss(obs, pred)

def main():
    "Main function"
    optmgr = OptionParser()
    opts, _ = optmgr.get_opt()
    calc_logloss(opts.fpred, opts.fobs)
    

if __name__ == '__main__':
    main()
