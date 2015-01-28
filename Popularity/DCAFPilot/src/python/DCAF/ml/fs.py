#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=
'''
Fast-learning online tool based on hash trick and logistic regression.
Courtesy Sam Hocevar <sam@hocevar.net>,
http://www.kaggle.com/c/tradeshift-text-classification/forums/t/10537/beat-the-benchmark-with-less-than-400mb-of-memory

Generic case of loss function and various improvements done by
Valentin Kuznetsov <vkuznet@gmail.com>
'''

# system modules
import os
import sys
import random
import socket
import hashlib
import optparse

from datetime import datetime
from math import log, exp, sqrt, tanh, pi, atan

# local modeuls
from DCAF.utils.utils import fopen

#try:
#    import pyhash
#    hash = pyhash.fnv1_64()
#    print "Using pyhash.fnv1_64"
#except Exception as exc:
#    print "Unable to load pyhash", str(exc)
#    pass

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

class OptionParser():
    def __init__(self):
        "User based option parser"
        self.parser = optparse.OptionParser()
        self.parser.add_option("--fin", action="store", type="string",
            dest="fin", default="data/train.csv", help="input file")
        self.parser.add_option("--ftest", action="store", type="string",
            dest="ftest", default="data/test.csv", help="input test file")
        self.parser.add_option("--flabels", action="store", type="string",
            dest="flabels", default="data/trainLabels.csv", help="input labels file")
        misses = "" # list of comma separater miss values
        self.parser.add_option("--misses", action="store", type="string",
            dest="misses", default=misses, help="Column misses, default %s" % misses)
        self.parser.add_option("--bits", action="store", type="int",
            dest="bits", default=24, help="Number of bits")
        self.parser.add_option("--alpha", action="store", type="float",
            dest="alpha", default=0.1, help="learning rate for sgd optimization")
        hcols="" # list of comma separated columns to perform cross-product
        self.parser.add_option("--cols", action="store", type="string",
            dest="cols", default=hcols,
            help="hash collision indecies, default %s" % hcols)
        self.parser.add_option("--no-out", action="store_true",
            dest="no_out", default=False)
        # GLF default parameters which reduces GLF to sigmoid
        self.parser.add_option("--a", action="store", type="float",
            dest="a", default=0, help="GLF a parameter, the lower asymptote")
        self.parser.add_option("--k", action="store", type="float",
            dest="k", default=1, help="GLF k parameter, the upper asymptote")
        self.parser.add_option("--b", action="store", type="float",
            dest="b", default=1, help="GLF b parameter, the growth rate")
        self.parser.add_option("--q", action="store", type="float",
            dest="q", default=1, help="GLF q parameter, the dependent term")
        self.parser.add_option("--m", action="store", type="float",
            dest="m", default=0, help="GLF m parameter, the time of maximum growth")
        self.parser.add_option("--nu", action="store", type="float",
            dest="nu", default=1, help="GLF nu parameter, the cutoff")
    def get_opt(self):
        "Return list of options"
        return self.parser.parse_args()


# A. x, y generator
# INPUT:
#     path: path to train.csv or test.csv
#     label_path: (optional) path to trainLabels.csv
# YIELDS:
#     ID: id of the instance (can also acts as instance count)
#     x: a list of indices that its value is 1
#     y: (if label_path is present) label value of y1 to y33
def data(path, D, ndim, extra_dim, label_path=None, hcols=[], misses=[]):
    for t, line in enumerate(fopen(path)):
        # initialize our generator
        if t == 0:
            # create a static x,
            # so we don't have to construct a new x for every instance
            x = [0] * (ndim + extra_dim)
            if label_path:
                label = fopen(label_path)
                label.readline()  # we don't need the headers
            continue
        # parse x
        counter = 0
        for m, feat in enumerate(line.rstrip().split(',')):
            if  m in misses:
                continue
            if  m == 0:
                try:
                    ID = int(feat)
                except:
                    continue
            else:
                # one-hot encode everything with hash trick
                # categorical: one-hotted
                # boolean: ONE-HOTTED
                # numerical: ONE-HOTTED!
                # note, the build in hash(), although fast is not stable,
                #       i.e., same value won't always have the same hash
                #       on different machines
                if  misses:
                    idx = counter
                else:
                    idx = m
                x[idx] = abs(hash(str(m) + '_' + str(feat))) % D
            counter += 1
        row = line.rstrip().split(',')
        tidx = ndim
        for i in xrange(len(hcols)):
          for j in xrange(i+1, len(hcols)):
            tidx += 1
            try:
                val = str(tidx)+'_'+row[hcols[i]]+"_"+row[hcols[j]]
                x[tidx] = abs(hash(val)) % D
            except Exception as exc:
                print "tidx=%s, i=%s, j=%s" % (tidx, i, j)
                print str(exc)
                raise

        # parse y, if provided
        if label_path:
            # use float() to prevent future type casting, [1:] to ignore id
            y = [float(y) for y in label.readline().split(',')[1:]]
        yield (ID, x, y) if label_path else (ID, x)


# B. Bounded logloss
# INPUT:
#     p: our prediction
#     y: real answer
# OUTPUT
#     bounded logarithmic loss of p given y
def logloss(p, y):
    p = max(min(p, 1. - 10e-16), 10e-16)
    return -log(p) if y == 1. else -log(1. - p)

class GLF(object):
    def __init__(self, a=0, k=1, b=1, q=1, m=0, nu=1):
        "GLF (Generalized Logistic Function) object"
        self.a = a
        self.k = k
        self.b = b
        self.q = q
        self.m = m
        self.nu = nu
    def __repr__(self):
        "Representation of GLF object"
        return "<GenLogFunc(a=%s, k=%s, b=%s, q=%s, m=%s, nu=%s)>, http://www.wikiwand.com/en/Generalised_logistic_function" \
                % (self.a, self.k, self.b, self.q, self.m, self.nu)
    def logistic(self, t):
        "Generalized logistic function"
        return self.a+(self.k-self.a)/(1.+self.q*exp(-self.b*(t-self.m)))**(1/self.nu)
    def sigmoid(self, t):
        "Generalized logistic function reduced to sigmoid function"
        return 1./(1.+exp(-t))
    def tanh(self, t):
        "hyperbolic tangent function"
        return (1.+tanh(t))/2. # bounded tanh (in [0,1] range)
    def algebraic(self, t):
        "algebraic function"
        return t/sqrt(1.+t**2)
    def absval(self, t):
        "absolute value function"
        return t/(1.+abs(t))
    def guderman(self, t):
        "Gudermannian function"
        return (2./pi)*atan(pi*t/2.)

# C. Get probability estimation on x
# INPUT:
#     x: features
#     w: weights
#     g: generalized logistic func object
# OUTPUT:
#     probability of p(y = 1 | x; w)
def predict(x, w, g):
    wTx = 0.
    for i in x:  # do wTx
        wTx += w[i] * 1.  # w[i] * x[i], but if i in x we got x[i] = 1.
    val = max(min(wTx, 40.), -40.)
    return g.logistic(val)

# D. Update given model
# INPUT:
# alpha: learning rate
#     w: weights
#     n: sum of previous absolute gradients for a given feature
#        this is used for adaptive learning rate
#     x: feature, a list of indices
#     p: prediction of our model
#     y: answer
# MODIFIES:
#     w: weights
#     n: sum of past absolute gradients
def update(alpha, w, n, x, p, y):
    for i in x:
        # alpha / sqrt(n) is the adaptive learning rate
        # (p - y) * x[i] is the current gradient
        # note that in our case, if i in x then x[i] = 1.
        n[i] += abs(p - y)
        if  not n[i]: n[i] = 1e-30 # VK addition to avoid divZer w/ different learn functions
        w[i] -= (p - y) * 1. * alpha / sqrt(n[i])


def run(train, test, label, bits, alpha, hcols, no_out, misses, glf):
    "Run train/test program"
    print("Train model with b=%s, a=%s, cols=%s, misses=%s, host=%s"\
            % (bits, alpha, hcols, misses, socket.gethostname()))
    sys.__stdout__.flush()
    start = datetime.now()

    # find out number of dimensions
    ndim = 146 # number of features in our dataset plus 1 bias feature
    extra_dim = 1 # extra dimension for hcols interactions
    for i in xrange(len(hcols)):
        for j in xrange(i+1, len(hcols)):
            extra_dim += 1
    if  misses:
        ndim -= len(misses)
    print('Dim: %s, extra %s' % (ndim, extra_dim))
    sys.__stdout__.flush()

    # number of weights use for each model, we have 32 of them
    D = 2 ** bits

    # a list for range(0, 33) - 13, no need to learn y14 since it is always 0
    K = [k for k in range(33) if k != 13]

    # initialize our model, all 32 of them, again ignoring y14
    w = [[0.] * D if k != 13 else None for k in range(33)]
    n = [[0.] * D if k != 13 else None for k in range(33)]

    loss = 0.
    loss_y14 = log(1. - 10**-16)

    for ID, x, y in data(train, D, ndim, extra_dim, label, hcols, misses=misses):
        # get predictions and train on all labels
        for k in K:
            p = predict(x, w[k], glf)
            update(alpha, w[k], n[k], x, p, y[k])
            loss += logloss(p, y[k])  # for progressive validation
        loss += loss_y14  # the loss of y14, logloss is never zero
        # print out progress, so that we know everything is working
        if ID % 100000 == 0:
            print('%s\tencountered: %d\tcurrent logloss: %f' % (
                datetime.now(), ID, (loss/33.)/ID))
            sys.__stdout__.flush()
    print "Final loss", (loss/33.)/ID

    if  no_out:
        print "No output request"
        sys.__stdout__.flush()
    else:
        oname = 'b%s_a%s.csv' % (bits, alpha)
        print "Yield %s" % oname
        sys.__stdout__.flush()
        with fopen(oname, 'w') as outfile:
            outfile.write('id_label,pred\n')
            for ID, x in data(test, D, ndim, extra_dim, hcols=hcols, misses=misses):
                predSum = 1.0
                for k in K:
                    p = predict(x, w[k], glf)
                    outfile.write('%s_y%d,%s\n' % (ID, k+1, str(p)))
                    predSum -= p
                    if k == 12:
                        outfile.write('%s_y14,0.0\n' % ID)
                    if k == 31:
                        p = max(0.01,predSum)
                        outfile.write('%s_y33,%s\n' % (ID, str(p)))

    print('Done, elapsed time: %s' % str(datetime.now() - start))
    sys.__stdout__.flush()

def main():
    "Main function"
    optmgr  = OptionParser()
    opts, _ = optmgr.get_opt()

    train = opts.fin
    label = opts.flabels
    test = opts.ftest

    bits = opts.bits
    alpha = float(opts.alpha)
    cols = [int(r) for r in opts.cols.split(',') if r]
    no_out = opts.no_out
    misses = [int(r) for r in opts.misses.split(',') if r]
    glf = GLF(opts.a, opts.k, opts.b, opts.q, opts.m, opts.nu)
    print glf
    run(train, test, label, bits, alpha, cols, no_out, misses, glf)

if __name__ == '__main__':
    main()

