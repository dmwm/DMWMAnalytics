#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=
"""
File       : vw_grid.py
Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
Description: This script will perform grid search over listed parameter space.
"""

# PARAMETER SPACE
PARAMS = {'--passes':8,
        '-l': 0.85,
        '--initial_pass_length': [10,100,1000],
        '--loss_function': 'quantile',
        '--quantile_tau': 0.6,
        }
#PARAMS = {'--passes':range(1,51),
#        '-l': [x/10.0 for x in range(1, 10, 1)],
#        '--power_t': [x/10.0 for x in range(1, 10, 1)],
#        '--decay_learning_rate': [x/10.0 for x in range(1, 5, 1)],
#        '--loss_function': 'quantile',
#        '--quantile_tau': [x/100.0 for x in range(57, 63, 1)],
#        '--nn': range(3,51)
#        }
#################

# system modules
import os
import sys
import pprint
import shutil
import hashlib
import optparse
import itertools
import subprocess

from sklearn.metrics import roc_auc_score
import numpy as np

class OptionParser:
    """Option parser"""
    def __init__(self):
        self.parser = optparse.OptionParser()
        self.parser.add_option("--train", action="store", type="string",
                               default="", dest="train_vw",
             help="specify train VW file")
        self.parser.add_option("--test", action="store", type="string",
                               default="", dest="test_vw",
             help="specify test VW file")
        self.parser.add_option("--wdir", action="store", type="string",
                               default='/tmp/vw', dest="wdir",
             help="Specify workdir")
    def get_opt(self):
        """Returns parse list of options"""
        return self.parser.parse_args()

def gen_model(params):
    "Generate series of models from given set of parameters"
    keys = params.keys()
    opts = ''
    options = []
    for key, val in params.items():
        if  isinstance(val, list):
            opts = []
            for vvv in val:
                opts.append('%s %s' % (key, vvv))
            options.append(opts)
        else:
            options.append(['%s %s' % (key, val)])
    return itertools.product(*options)

def genid(kwds):
    "Generate id for given field"
    if  isinstance(kwds, dict):
        record = dict(kwds)
        data = json.JSONEncoder(sort_keys=True).encode(record)
    else:
        data = str(kwds)
    keyhash = hashlib.md5()
    keyhash.update(data)
    return keyhash.hexdigest()

def run(cmd):
    "Run given command in subprocess"
    print cmd
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc.wait()
    out = proc.stdout.read()
    err = proc.stderr.read()
    proc.stdout.close()
    proc.stderr.close()
    if  out:
        print "ERROR:", out
        sys.exit(1)
    return parse(err)

def labels(train_vw):
    "Read labels from train VW file"
    out = []
    for line in open(train_vw, 'r').readlines():
        label = line.split()[0]
        out.append(int(label))
    return out

def parse(out):
    "Parse given output"
    for line in out.split('\n'):
        if  line.find('average loss') != -1:
            loss = line.replace('average loss =', '').replace('h', '').strip()
            return float(loss)

def parse_predictions(pred_vw):
    "Read prediction from given file"
    out = []
    for line in open(pred_vw, 'r').readlines():
        prob, _ = line.split()
#        out.append(round(float(prob)))
        out.append(float(prob))
    return out

def run_model(wdir, train_vw, test_vw, args, outcome):
    "Run specific model with given set of parameters"
    uid = genid(args)
    res = {'model': args, 'uid': uid}
    model = '%s/model_%s.vw' % (wdir, uid)
    preds = '%s/preds_%s.txt' % (wdir, uid)
    train_preds = '%s/train_preds_%s.txt' % (wdir, uid)

    # run vw to create a model
    cmd = 'vw %s -c -k -f %s %s' % (train_vw, model, args)
    results = run(cmd)
    res.update({'train': results})

    # run vw over test dataset
    cmd = 'vw %s -t -i %s -p %s' % (test_vw, model, preds)
    results = run(cmd)
    res.update({'test': results})

    # final run over train set to get prediciton
    cmd = 'vw %s -t -i %s -p %s' % (train_vw, model, train_preds)
    results = run(cmd)
    scores = parse_predictions(train_preds)
    auc_val = roc_auc_score(np.array(outcome), np.array(scores))
    res.update({'auc': auc_val})

    # clean-up
    for key in [model, preds, train_preds]:
        if  os.path.exists(key):
            os.remove(key)
    return res

def find_best(results):
    "Find best models from provided input"
    models = []
    best = min([row['auc']+row['test']+row['train'] for row in results])
    for row in results:
        if  row['auc']+row['test']+row['train'] == best:
            models.append(row)
    return models

def grid_search(wdir, train_vw, test_vw, outcome):
    "Perform grid search of parameter space and report the results"
    opts = []
    for model_opts in gen_model(PARAMS):
        opts.append(' '.join(model_opts))
    print "Total number of combinations:", len(opts)
    results = []
    for model_opts in opts:
        res = run_model(wdir, train_vw, test_vw, model_opts, outcome)
        results.append(res)
    pprint.pprint(results)
    best_models = find_best(results)
    print "\n### BEST models (auc+train+test)"
    pprint.pprint(best_models)

def main():
    "Main function"
    optmgr = OptionParser()
    opts, _ = optmgr.get_opt()
    if  not opts.train_vw or not opts.test_vw:
        print "Usage: %s --help" % __file__
        sys.exit(1)
    if  os.path.isdir(opts.wdir):
        shutil.rmtree(opts.wdir)
    os.mkdir(opts.wdir)
    outcome = labels(opts.train_vw)
    grid_search(opts.wdir, opts.train_vw, opts.test_vw, outcome)

if __name__ == '__main__':
    main()
