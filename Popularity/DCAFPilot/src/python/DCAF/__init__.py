#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=C0103

"""
DCAF modules

.. moduleauthor:: Valentin Kuznetsov <vkuznet@gmail.com>
"""
__author__ = "Valentin Kuznetsov"
version = "development"

import sys
vinfo = sys.version_info[:2]
CLIENT = 'DCAF/%s::python/%s.%s' % (version, vinfo[0], vinfo[-1])
