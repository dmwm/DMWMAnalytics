#!/usr/bin/env python

import sys
import pandas

fileName = sys.argv[1]

df = pandas.read_csv(fileName)
grouped = df.groupby("model")

grouped.sum().to_csv(fileName)

