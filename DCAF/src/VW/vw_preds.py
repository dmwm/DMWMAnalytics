#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=
"""
File       : vw_cross.py
Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
Description: 
"""

# system modules
import os
import sys

def main(vwfile, vwpred, oname):
    "Main function"
    headers = ['id','target','intpred','predvalue']
    with open(vwfile, 'r') as istream, open(vwpred, 'r') as pstream, open(oname, 'w') as ostream:
        ostream.write(','.join(headers) + '\n')
        while True:
            # read one line from input files and construct output
            try:
                vwline = istream.readline()
                vwpred = pstream.readline()
                label = vwline.split()[0]
                pred, rid = vwpred.split()
            except:
                break
            out = '%s,%s,%s,%s\n' % (rid, label, int(round(float(pred))), pred)
            ostream.write(out)


if __name__ == '__main__':
    vwfile = sys.argv[1]
    vwpred = sys.argv[2]
    ofile  = sys.argv[3]
    main(vwfile, vwpred, ofile)
