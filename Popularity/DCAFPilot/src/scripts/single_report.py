#!/usr/bin/env python
#-*- coding: utf-8 -*-

from __future__ import print_function

__author__ = "Mantas Briliauskas"

# local modules
from DCAF.tools.reporter import Reporter

def gen_report():
    repmgr = Reporter()
    #report setup
    path  = "."
    fout  = "report.rep"
    fbeg1 = "old_"
    fbeg2 = "new_"
    fend  = ".pred"
    rtit  = "Evaluation of data filtering influence"
    desc  = "Description        : single run of classifiers\n"
    desc += "   Training data   : 2015 years\n"
    desc += "   Validation data : 2016 first two weeks\n"
    tit1  = "Validation using old data"
    tit2  = "Validation using new data"
    #report generation
    repmgr.open(fout)
    repmgr.write_section(rtit, desc)
    repmgr.write_table(path, fbeg=fbeg1, fend=fend, title=tit1)
    repmgr.write_table(path, fbeg=fbeg2, fend=fend, title=tit2)
    repmgr.close()

def main():
    gen_report()

if __name__ == '__main__':
    main()
