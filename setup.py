#!/usr/bin/env python

from distutils.core import setup, Extension

setup(name = 'AndroidCodeGenerator',
      version = '1.0',
      description = 'This is a python module which generates Android classes.\
 It is most useful for creating an initial database and contentprovider\
 for a project.',
      author = 'spacecowboy',
      author_email = 'spacecowboy@kalderstam.se',
      url = 'https://github.com/spacecowboy/AndroidCodeGenerator',
      packages = ['AndroidCodeGenerator'],
      package_dir = {'AndroidCodeGenerator': 'AndroidCodeGenerator'},
      requires = [],
     )
