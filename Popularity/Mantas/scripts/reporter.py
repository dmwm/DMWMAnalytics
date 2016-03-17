#!/usr/bin/env python
#-*- coding: utf-8 -*-

from __future__ import print_function

# system modules
import os
import re
import sys
import glob
import optparse
import pandas as pd

class Reporter(object):
    def __init__(self):
        self.__writing = False
        self.__fout    = None
        self.__ostream = None

    ### PUBLIC FUNCTIONS ###
    def open(self, fout):
        try:
            self.__ostream = open(fout, 'w')
            self.__writing = True
            self.__fout    = fout
        except IOError:
            print ("Error: cannot open file %s for writing" % fout)
    
    def close(self):
        self.__ostream.close()
        self.__writing = False
        self.__fout    = None

    def write_section(self, title, text):
        if  self.__writing:
            bor  = self.__border(len(title) + 1)
            self.__write(bor  + "\n" + title + "\n" + bor + "\n")
            self.__write(text + "\n")
            self.__write(bor  + "\n\n")
        else:
            raise Exception("Error: open file for writing first")

    def write_table(self, path, fbeg="", fend="", title="", totals=[]):
        """
        Selects prediction files in path using fbeg and fend.
        If table title is provided, it will be outputted.
        Total functions are aggregation functions like mean, rmse.
        Full list available in stots keys, where each value corresponds to
            function fnk(row_names, col_names, data)
        Use fbeg as prefix (e.g. 'old' or 'new') if data from files with
            specific beginning is needed
        """
        #supported 'total' functions
        stots = {'mean':'__get_mean', 'rmse':'__get_rmse'}
        clfs, scorers, data = self.__read_data(path, fbeg, fend)
        _tnames = []
        _tdata  = []
        if  totals is not None and len(totals) > 0:
            _tkeys  = stots.keys()
            for i in xrange(len(totals)):
                if  totals[i] in _tkeys:
                    _tnames.append(totals[i])
                    _fnk = getattr(cls.__name__, totals[i])
                    _tdata.append(_fnk(clfs, scorers, data))
                else:
                    msg  = "Error: unrecognized total function %s.\n"
                    msg += "Available total functions are: " 
                    print(msg % totals[i], _tkeys)
        out  = self.__pd_table(title, scorers, clfs, data, _tnames, _tdata)
        out += "\n"
        self.__write(out)

    ### PRIVATE FUNCTIONS ###
    def __write(self, rawtxt):
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
        files = [os.path.join(path, f) for f in os.listdir(path)
                if os.path.isfile(os.path.join(path, f))
                    and (len(fbeg) == 0 or f.startswith(fbeg))
                    and (len(fend) == 0 or f.endswith(fend))]
        return files

    def __read_data(self, path, fbeg="", fend="*.pred"):
        """
        Reads scorers data from files
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
                # values under parentheses
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
                #exit()
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
        # clfs - file names witout extension, scorers - list of scorers,
        # scores - scores respectfully
        return clfs, scorers, scores
    
    def __border(self, n, sign="="):
        "Returns a line from n sign symbols"
        bor  = ""
        for i in xrange(n):
            bor += str(sign)
        return bor

    def __pd_table(self, title, col_names, row_names, data, total_names=[], total_data=[]):
        """
        Given data forms a table. Does not include data logics.
        If name is None or empty str, name section is skipped.
        Totals are aggregated data like mean, RMSE, etc.
        Total_data must have #total_names members.
        Each total_data member must have #col_names values.
        TODO: alter total_names and total_data to dict
        """
        pd.set_option('display.width', 1000)
        pd.set_option('display.float_format', '{:,.5f}'.format)
        _data = data
        if  total_data is not None and len(total_data) > 0:
            if  total_names is None or len(total_names) != len(total_data):
                raise Exception("Error: please provide as many total_names as total_data rows.")
            coln  = len(col_names)
            _data += [['' for i in xrange(coln)]]
            for i in xrange(len(total_data)):
                if  len(total_data[i]) == coln:
                    _data += total_data[i]
                else:
                    print("Error adding total_data : %d columns expected, %d given. Line: " % (coln, len(total_data[i])), total_data[i])
        _rows = row_names
        if  total_names is not None and len(total_names) > 0:
            _rows += ['']
            for i in xrange(len(total_names)):
                _rows += [str(total_names[i])]
        if  title is not None and len(title) > 0:
            _bor  = self.__border(len(title) + 1)
            out  = _bor  + "\n"
            out += title + "\n"
            out += _bor  + "\n"
        else:
            out  = ""
        out += str(pd.DataFrame(_data, _rows, col_names)) + "\n"
        return out

    def __to_num(self, s):
        try:
            return int(s)
        except:
            try:
                return float(s)
            except:
                return None

    def __get_means(self, _, __, data):
        "Calculates mean of many lists"
        sums = data[0]
        n = len(data)
        for i in xrange(1, n):
            sums = [x+y for x,y in zip(sums, data[i])]
        means = [x/n for x in sums]
        return means

    def __get_rmses(self, _, __, data):
        means = __get_means(data)
        ses   = [[pow(s[i]-means[i], 2) for i in xrange(len(s))] for s in data]
        mses  = get_means(ses)
        rmses = [sqrt(s) for s in mses]
        return rmses
