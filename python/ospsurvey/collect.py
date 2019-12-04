"""
Collect the survey information
"""

import os
import platform

from keystoneauth1 import loading
from keystoneauth1 import session
from heatclient import client

import version

def osp_auth():
  """
  Establish a connection to the OSP undercloud instance
  """

  if 'OS_IDENTITY_API_VERSION' in os.environ.keys():
    identity_api_version = int(os.environ['OS_IDENTITY_API_VERSION'])
  else:
    identity_api_version = 2

  return osp_auth
  

def collect():

  osp_creds = osp_auth()
  
  data = {}

  os = platform.linux_distribution()
  
  data['os'] = {
    'distro': os[0],
    'release': os[1]
  }

  osp = version.version()

  data['osp'] = osp
  return data
