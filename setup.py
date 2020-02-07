#!/usr/bin/env python
"""
Survey and report the state of a deployed Red Hat Openstack Platform cluster

This module contains a set of libraries and a driver script to query the
state of an OpenStack cluster from the Director node.
"""
# Setup structure from pypa sample project:
#  https://github.com/pypa/sampleproject/blob/master/setup.py

from setuptools import setup, find_packages
from os import path
# io.open is needed for projects that support Python 2.7
# It ensures open() defaults to text mode with universal newlines,
# and accepts an argument to specify the text encoding
# Python 3 only projects can skip this import
from io import open

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README'), encoding='utf-8') as f:
  long_description = f.read()
  
setup(
  name='ospsurvey',
  version='0.2.4',
  description='Survey an OpenStack Cluster',
  long_description=long_description,
  #long_description_content_type='text/markdown',
  url='https://github.com/markllama/ospsurvey',
  author='Mark Lamourine',
  author_email='markllama@gmail.com',
  include_package_data=True,
  classifiers=[
    'License :: OSI Approved :: Apache 2.0 License',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.5',
    'Development Status :: 3 - Alpha',
    'Intended Audience :: OpenStack Administrators',
  ],
  keywords='openstack director redhat',
  
  package_dir={'': 'src'},
  packages=find_packages(where='src'),
  package_data={
    '.': ['*.txt', '*.rst', '*.md']
  },

  scripts=[
    'bin/server-role',
    'bin/service-checks',
    'bin/check-updates',
    'bin/rh-subscription'
  ],
  python_requires='>=2.7',

  test_suite="tests"
)
