#!/usr/bin/env python

"""
Standard python setup.py file for DCAF package
To build     : python setup.py build
To install   : python setup.py install --prefix=<some dir>
To clean     : python setup.py clean
To build doc : python setup.py doc
To run tests : python setup.py test
"""
from __future__ import print_function
__author__ = "Valentin Kuznetsov"

import os
import sys
import shutil
import subprocess
from unittest import TextTestRunner, TestLoader
from glob import glob
from os.path import splitext, basename, join as pjoin
from distutils.core import setup
from distutils.cmd import Command
from distutils.command.install import INSTALL_SCHEMES

# add some path which will define the version,
# e.g. it can be done in DCAF/__init__.py
sys.path.append(os.path.join(os.getcwd(), 'src/python'))
try:
    from DCAF import version as dp_version
except:
    dp_version = '1.0.0' # some default

required_python_version = '2.6'

class TestCommand(Command):
    """
    Class to handle unit tests
    """
    user_options = [ ]

    def initialize_options(self):
        """Init method"""
        self._dir = os.getcwd()

    def finalize_options(self):
        """Finalize method"""
        pass

    def run(self):
        """
        Finds all the tests modules in test/, and runs them.
        """
        # list of files to exclude,
        # e.g. [pjoin(self._dir, 'test', 'exclude_t.py')]
        exclude = []
        # list of test files
        testfiles = []
        for tname in glob(pjoin(self._dir, 'test', '*_t.py')):
            if  not tname.endswith('__init__.py') and \
                tname not in exclude:
                testfiles.append('.'.join(
                    ['test', splitext(basename(tname))[0]])
                )
        testfiles.sort()
        try:
            tests = TestLoader().loadTestsFromNames(testfiles)
        except:
            print("\nFail to load unit tests", testfiles)
            raise
        test = TextTestRunner(verbosity = 2)
        test.run(tests)

class CleanCommand(Command):
    """
    Class which clean-up all pyc files
    """
    user_options = [ ]

    def initialize_options(self):
        """Init method"""
        self._clean_me = [ ]
        for root, dirs, files in os.walk('.'):
            for fname in files:
                if  fname.endswith('.pyc') or fname. endswith('.py~') or \
                    fname.endswith('.rst~'):
                    self._clean_me.append(pjoin(root, fname))
            for dname in dirs:
                if  dname == 'build':
                    self._clean_me.append(pjoin(root, dname))

    def finalize_options(self):
        """Finalize method"""
        pass

    def run(self):
        """Run method"""
        for clean_me in self._clean_me:
            try:
                if  os.path.isdir(clean_me):
                    shutil.rmtree(clean_me)
                else:
                    os.unlink(clean_me)
            except:
                pass
class DocCommand(Command):
    """
    Class which build documentation
    """
    user_options = [ ]

    def initialize_options(self):
        """Init method"""
        pass

    def finalize_options(self):
        """Finalize method"""
        pass

    def run(self):
        """Run method"""
        cdir = os.getcwd()
        os.chdir(os.path.join(cdir, 'doc'))
        os.environ['PYTHONPATH'] = os.path.join(cdir, 'src/python')
        subprocess.call('make html', shell=True)
        os.chdir(cdir)

def dirwalk(relativedir):
    """
    Walk a directory tree and look-up for __init__.py files.
    If found yield those dirs. Code based on
    http://code.activestate.com/recipes/105873-walk-a-directory-tree-using-a-generator/
    """
    idir = os.path.join(os.getcwd(), relativedir)
    for fname in os.listdir(idir):
        fullpath = os.path.join(idir, fname)
        if  os.path.isdir(fullpath) and not os.path.islink(fullpath):
            for subdir in dirwalk(fullpath):  # recurse into subdir
                yield subdir
        else:
            initdir, initfile = os.path.split(fullpath)
            if  initfile == '__init__.py':
                yield initdir

def find_packages(relativedir):
    "Find list of packages in a given dir"
    packages = []
    for idir in dirwalk(relativedir):
        package = idir.replace(os.getcwd() + '/', '')
        package = package.replace(relativedir + '/', '')
        package = package.replace('/', '.')
        packages.append(package)
    return packages

def datafiles(idir):
    """Return list of data files in provided relative dir"""
    files = []
    for dirname, dirnames, filenames in os.walk(idir):
        if  dirname.find('.svn') != -1:
            continue
        for subdirname in dirnames:
            if  subdirname.find('.svn') != -1:
                continue
            files.append(os.path.join(dirname, subdirname))
        for filename in filenames:
            if  filename[-1] == '~':
                continue
            files.append(os.path.join(dirname, filename))
    return files

def main():
    "Main function"
    version      = dp_version
    name         = "DCAF"
    description  = "DCAF is Data and Computing Analytics Framework"
    url          = ""
    readme       = "DCAF package %s" % url
    author       = "Valentin Kuznetsov",
    author_email = "vkuznet [at] gmail [dot] com>",
    keywords     = ["DCAF"]
    package_dir  = {'DCAF': 'src/python/DCAF'}
    packages     = find_packages('src/python')
    data_files   = [] # list of tuples whose entries are (dir, [data_files])
    cms_license  = "CMS experiment software"
    classifiers  = [
        "Development Status :: 3 - Production/Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: CMS/CERN Software License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Topic :: Database"
    ]

    if  sys.version < required_python_version:
        msg = "I'm sorry, but %s %s requires Python %s or later."
        print(msg % (name, version, required_python_version))
        sys.exit(1)

    # set default location for "data_files" to
    # platform specific "site-packages" location
    for scheme in INSTALL_SCHEMES.values():
        scheme['data'] = scheme['purelib']

    setup(
        name                 = name,
        version              = version,
        description          = description,
        long_description     = readme,
        keywords             = keywords,
        packages             = packages,
        package_dir          = package_dir,
        data_files           = data_files,
        scripts              = datafiles('bin'),
        requires             = ['python (>=2.6)'],
        classifiers          = classifiers,
        cmdclass             = {'test': TestCommand, 'clean': CleanCommand, 'doc': DocCommand},
        author               = author,
        author_email         = author_email,
        url                  = url,
        license              = cms_license,
    )

if __name__ == "__main__":
    main()
