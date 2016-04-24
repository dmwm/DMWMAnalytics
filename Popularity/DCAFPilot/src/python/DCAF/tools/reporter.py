#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=
"""
File        : reporter.py
Author      : Mantas Briliauskas <m dot briliauskas AT gmail dot com>
Description : Represents prediction reporter module
"""

from __future__ import print_function

# system modules
import os
import re
import sys
import glob
import optparse
import operator
import pandas as pd

class Reporter(object):
    def __init__(self):
        self.__writing = False
        self.__fout    = None
        self.__ostream = None

    ### PUBLIC FUNCTIONS ###
    def open(self, fout):
        "Prepares file to write"
        try:
            self.__ostream = open(fout, 'w')
            self.__writing = True
            self.__fout    = fout
        except IOError:
            print ("Error: cannot open file %s for writing" % fout)
    
    def close(self):
        "Closes open file"
        self.__ostream.close()
        self.__writing = False
        self.__fout    = None

    def write_section(self, title, text):
        "Writes formatted text section with title"
        if  self.__writing:
            bor  = self.__border(len(title) + 1)
            self.__write(bor  + "\n" + title + "\n" + bor + "\n")
            self.__write(text + "\n")
            self.__write(bor  + "\n\n")
        else:
            raise Exception("Error: open file for writing first")

    def write_csv_table(self, path, fbeg="", fend=".csv"):
        """
        Gathers information from *.csv file and prints a table
        Used with *.csv formed by check_predictions --plain-out
        """
        data = self.__read_csv_data(path, fbeg, fend)
        out  = ""
        beg  = (" ".join(fbeg.split("_"))).capitalize()
        for clf in sorted(data.keys()):
            title = beg + (" ".join(clf.split("_"))).capitalize()
            out += self.__pd_table(title, data[clf]['slist'], data[clf]['tlist'], data[clf]['sdata'])
            out += "\n"
        self.__write(out)

    def write_table(self, path, fbeg="", fend="", title=""):
        """
        Writes formatted section with some text and title
        Used with check_predictions *.pred output
        Use 'fbeg' as prefix (e.g. 'old' or 'new') if data from files with specific beginning is needed.
        """
        clfs, scorers, data = self.__read_pred_data(path, fbeg, fend)
        out  = self.__pd_table(title, scorers, clfs, data) + "\n"
        self.__write(out)


    ### Private functions ###

    def __write(self, rawtxt):
        "Writes string to output files"
        if  self.__writing:
            try:
                self.__ostream.write(rawtxt)
            except IOError:
                print("Error: cannot write to file %s" % self.__fout)
            except:
                print("Unknown error occured while writing to %s" % self.__fout)
                print("RAW:\n", rawtxt)
        else:
            print("Error: writing in closed mode.")

    def __get_file_list(self, path, fbeg, fend):
        "Selects files by given parameters and returns"
        files = [f for f in os.listdir(path)
                if os.path.isfile(os.path.join(path, f))
                    and (len(fbeg) == 0 or f.startswith(fbeg))
                    and (len(fend) == 0 or f.endswith(fend))]
        if  path != '.':
            files = [os.path.join(path, f) for f in files]
        files = sorted(files)
        return files
    
    def __sort_csv_data(self, data):
        "Function used in __read_csv_data() to sort data by some column (TPR)."
        def getKey(item):
            # hardcoded for now : sorting by TPR
            return item[1][4]
        for clf in data.iterkeys():
            rows = dict(zip(data[clf]['tlist'], data[clf]['sdata']))
            # tprp = data[clf]['slist'].index('tpr')
            sorted_r = sorted(rows.items(), key=getKey, reverse=True)
            ntlist = []
            nsdata = []
            for item in sorted_r:
                ntlist.append(item[0])
                nsdata.append(item[1])
            data[clf]['tlist'] = ntlist
            data[clf]['sdata'] = nsdata
        return data

    def __read_csv_data(self, path, fbeg="", fend="*.pred"):
        """
        Reads scorer data from ".csv" type files
        Formed by check_prediction --plain-output
        """
        files = self.__get_file_list(path, fbeg, fend)
        if  len(files) == 0:
            print("WARNING: no files collected from '%s' with beginning '%s' and end '%s'" % (path, fbeg, fend))
            return None
        data = {}
        for f in files:
            clf = os.path.basename(f).replace(fbeg,"").replace(fend,"")
            if  clf not in data: data[clf] = {}
            slist = []
            tlist = []
            sdata = []
            for line in open(f,'r').readlines():
                line = line.strip(' \r\n').split(',')
                if  not slist:
                    if  not line[0] == 'tier':
                        print("Error: first header is not 'tier' in file %s" % f)
                        sys.exit(1)
                    slist = line[1:]
                    continue
                tlist.append(line[0])
                sdata.append(line[1:])
            data[clf]['slist'] = slist
            data[clf]['tlist'] = tlist
            data[clf]['sdata'] = sdata
        #return self.__sort_csv_data(data)
        return data

    def __read_pred_data(self, path, fbeg="", fend="*.pred"):
        """
        Reads semi-structured scorer data from ".pred" type files
        Files formed by check_prediction without --plain-output setting
        """
        files = self.__get_file_list(path, fbeg, fend)
        if  len(files) == 0:
            print("Warning: no files collected from %s with beginning %s and end %s" % (path, fbeg, fend))
            return None
        scores  = []
        clfs    = []
        scorers = []
        lines_n = 0
        for f in files:
            ss = []
            n  = 0
            if  not scorers:
                # extract values under parentheses
                r   = re.compile(r"(\([^)]+\))")
                for l in open(f, 'r').readlines():
                    sr = l.strip(' \t\n\r')
                    if  sr:
                        sr = r.search(l)
                        if  not sr:
                            print("ERROR: cannot read scorers. Unresolved line: %s" % l)
                            sys.exit(1)
                        sr = sr.groups()[0][1:-1]
                        sr = sr.split('_')[0].lower()  #skipping "_score"
                        scorers.append(sr)
                        lines_n += 1
            for l in open(f, 'r').readlines():
                s = l.strip(' \t\n\r')
                if  not s:
                    continue
                s = s.split(' ')[-1]
                v = self.__to_num(s)
                if  v is not None:
                    ss.append(v)
                else:
                    print("Cannot read numeric value: ", s)
                n += 1
            if  n == lines_n: #is consistent
                scores.append(ss)
                base = os.path.basename(f)
                a    = len(fbeg)
                b    = len(fend) if fend > 0 else None
                clfs.append(base[a:-b]) #extract clf from filename
            else:
                print("Error reading %s: %d line count instead %d. Skipping."
                    % (f, n, lines_n))
        # clfs    - file names witout extension
        # scorers - list of scorers,
        # scores  - scores respectfully
        return clfs, scorers, scores
    
    def __border(self, n, sign="="):
        "Returns a line from n sign symbols"
        return str(sign) * n

    def __pd_table(self, title, col_names, row_names, data):
        """
        Given data forms a table. Does not include data logics.
        If name is None or empty str, name section is skipped.
        """
        pd.set_option('display.width', 1000)
        pd.set_option('display.float_format', '{:,.5f}'.format)
        _rows = row_names
        out = ""
        if  title is not None and len(title) > 0:
            _bor  = self.__border(len(title) + 1)
            out  = _bor  + "\n"
            out += title + "\n"
            out += _bor  + "\n"
        out += str(pd.DataFrame(data, _rows, col_names)) + "\n"
        return out

    def __to_num(self, s):
        "Converts string to number"
        try:
            return int(s)
        except:
            try:
                return float(s)
            except:
                return None
