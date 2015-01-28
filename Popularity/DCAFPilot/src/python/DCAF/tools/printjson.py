#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=
"""
File       : printjson.py
Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
Description: Print json to stdout in nice human readable format
"""

# system modules
import sys
import json
import pprint

def main():
    "Main function"
    doc = json.load(open(sys.argv[1]))
    pprint.pprint(doc)

if __name__ == '__main__':
    main()
