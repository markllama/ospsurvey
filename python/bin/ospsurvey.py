#! /usr/bin/env python
from __future__ import print_function
"""
Survey an OSP system.
Determine the installed version and query a number of stats and configurations to report
the current status of the cluster.

Output data either as a pretty table or as JSON structured data for consumption by a database
or analysis tool.
"""

import keystoneauth1
import keystoneclient
import novaclient

osp_status = {}

def get_osp_api_versions():

  versions = {
    'keystoneauth1': keystoneauth1.__version__,
    'keystoneclient': keystoneclient.__version__,
    'novaclient': novaclient.__version__
  }

  return versions

if __name__ == "__main__":

  
  # report OSP Library Versions
  osp_status['api_versions'] = get_osp_api_versions()

  # create session
  
  # create functions with session

  # call functions to fill structure

  # detect version

  # query overstack name/install/update time

  # query list of overstack nodes
  
  # query overstack node types

  # query hardware make/model
  
  # query compute node local disk

  # report status

  print(osp_status)
