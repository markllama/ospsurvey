#! /usr/bin/env python
from __future__ import print_function
"""
Survey an OSP system.
Determine the installed version and query a number of stats and configurations to report
the current status of the cluster.

Output data either as a pretty table or as JSON structured data for consumption by a database
or analysis tool.
"""

import json

import keystoneauth1
import keystoneclient
import novaclient

osp_status = {}

def get_osp_module_versions():
  """
  """
  versions = {
    'keystoneauth1': keystoneauth1.__version__,
    'keystoneclient': keystoneclient.__version__,
    'novaclient': novaclient.__version__
  }

  return versions

osp_varmap = {
  'OS_IDENTITY_API_VERSION': 'identity_api_version',

  'OS_CLOUDNAME': 'cloudname',
  
  'OS_AUTH_URL': 'auth_url',
  'OS_PASSWORD': 'password',

  'OS_USERNAME': 'username',
  'OS_USER_DOMAIN_NAME': 'user_domain_name',

  'OS_TENANT_NAME': 'tenant_name',

  'OS_PROJECT_NAME': 'project_name',
  'OS_PROJECT_DOMAIN_NAME': 'project_domain_name',

  'COMPUTE_API_VERSION': 'compute_api_version',
  'NOVA_VERSION': 'nova_version',

  'OS_BAREMETAL_API_VERSION': 'baremetal_api_version',
  'IRONIC_API_VERSION': 'ironic_api_version',

  'OS_IMAGE_API_VERSION': 'image_api_version'
}

def get_osp_envvars():
  envvars = {}
  for k,v in osp_varname_map.items():
    envvars[v] = os.environ[k] if k in os.environ else None

  return envvars
  
if __name__ == "__main__":

  
  # report OSP Library Versions
  osp_status['python_versions'] = get_osp_module_versions()

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

  print(json.dumps(osp_status))
