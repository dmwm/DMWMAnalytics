#!/usr/bin/env python
#-*- coding: ISO-8859-1 -*-

"""
Config utilities
"""

__author__ = "Valentin Kuznetsov"

import os
import ConfigParser
from DAS.utils.option import DASOption

def read_configparser(config):
    """Read configuration"""
    config = ConfigParser.ConfigParser()
    config.read(config)

    configdict = {}

    for option in OPTIONS:
        value = option.get_from_configparser(config)
        if option.destination:
            configdict[option.destination] = value
        else:
            if option.section in configdict:
                configdict[option.section][option.name] = value
            else:
                configdict[option.section] = {}
                configdict[option.section][option.name] = value

    return configdict

def configfile():
    """
    Return configuration file name $ROOT/etc/das.cfg
    """
    if  'DCAF_CONFIG' in os.environ:
        config = os.environ['DCAF_CONFIG']
        if  not os.path.isfile(config):
            raise EnvironmentError('No config file %s found' % config)
        return config
    else:
        raise EnvironmentError('DCAF_CONFIG environment is not set up')

def readconfig_helper(debug=False):
    """
    Read configuration file and store parameters into dictionary.
    """
    configdict = {}
    config  = configfile()
    error = 'Unable to read configuration file'
    try:
        configdict = read_configparser(config)
        if  debug:
            print "### Read configuration from %s" % config
    except Exception as exp:
        raise Exception(error + str(exp))
    if  not configdict:
        raise Exception(error)
    configdict['config_file'] = config
    return configdict

class ConfigSingleton(object):
    """
    Configuration singleton class.
    """
    def __init__(self):
        self.config = None
        self.config_debug = None

    def config(self, debug=False):
        """Return config"""
        if  debug:
            if not self.config_debug:
                self.config_debug = readconfig_helper(debug)
            return self.config_debug
        else:
            if not self.config:
                self.config = readconfig_helper()
            return self.config

# ensure unique name for singleton object
CONFIG_SINGLETON = ConfigSingleton()

def readconfig(debug=False):
    """
    Return configuration
    """
    return CONFIG_SINGLETON.config(debug)
