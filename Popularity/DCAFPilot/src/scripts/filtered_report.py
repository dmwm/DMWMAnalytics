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
    fbeg1 = "old_normal_"
    fbeg2 = "old_valid_data_-_only_selected_tiers_"
    fbeg3 = "old_train_and_valid_only_selected_tiers_"
    fbeg4 = "new_normal_"
    fbeg5 = "new_valid_data_-_only_selected_tiers_"
    fbeg6 = "new_train_and_valid_only_selected_tiers_"
    fend  = ".pred"
    rtit  = "Evaluation of data filtering influence"
    desc  = "Description    : train and predict classifiers using filtered data\n"
    desc += "   Data filter : only datasets from tiers AOD, AODSIM, MINIAOD, MINIAODSIM, USER\n"
    desc += "   Subtask 1   : train on full data, predict on full data\n"
    desc += "   Subtask 2   : train on full data, predict on filtered data \n"
    desc += "   Subtask 3   : train on filtered data, predict on filtered data\n"
    tit1  = "Old full data"
    tit2  = "Old filtered validation"
    tit3  = "Old filtered training and validation"
    tit4  = "New full data"
    tit5  = "New filtered validation"
    tit6  = "New filtered training and validation"
    #report generation
    repmgr.open(fout)
    repmgr.write_section(rtit, desc)
    #repmgr.write_csv_table(path, fbeg="old_", fend=".pred")
    #repmgr.write_csv_table(path, fbeg="new_", fend=".pred")
    repmgr.write_table(path, fbeg=fbeg1, fend=fend, title=tit1)
    repmgr.write_table(path, fbeg=fbeg2, fend=fend, title=tit2)
    repmgr.write_table(path, fbeg=fbeg3, fend=fend, title=tit3)
    repmgr.write_table(path, fbeg=fbeg4, fend=fend, title=tit4)
    repmgr.write_table(path, fbeg=fbeg5, fend=fend, title=tit5)
    repmgr.write_table(path, fbeg=fbeg6, fend=fend, title=tit6)
    repmgr.close()

def main():
    gen_report()

if __name__ == '__main__':
    main()
