#! /usr/bin/env python
from __future__ import print_function
"""
Survey an OSP system.
Determine the installed version and query a number of stats and configurations to report
the current status of the cluster.

Output data either as a pretty table or as JSON structured data for consumption by a database
or analysis tool.
"""

import os
import json

import keystoneauth1
import keystoneauth1.identity
import keystoneauth1.session

import keystoneclient
import keystoneclient.v3

import novaclient
import novaclient.client

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
  """
  TBD
  """
  envvars = {}
  for k,v in osp_varmap.items():
    envvars[v] = os.environ[k] if k in os.environ else None

  return envvars

def create_keystone_session(credentials):
  """
  TBD
  """
  auth = keystoneauth1.identity.v3.Password(
    auth_url=credentials['auth_url'],
    username=credentials['username'],
    password=credentials['password'],
    project_name=credentials['project_name'],
    user_domain_name=credentials['user_domain_name'],
    project_domain_name=credentials['project_domain_name']
  )

  session = keystoneauth1.session.Session(auth=auth)
  
  return session

  
if __name__ == "__main__":

  osp_envvars = get_osp_envvars()
  
  # report OSP Library Versions
  osp_status['python_versions'] = get_osp_module_versions()

  # create session
  ks_session = create_keystone_session(osp_envvars)

  # NOTE: All inputs have NOVA_VERSION at 1.1, but it's deprecated
  # The novaclient library sets API_MIN_VERSION at 2.1 and MAX_VERSION at 2.6
  nova = novaclient.client.Client(2, session=ks_session)
  
  # create functions with session

  # call functions to fill structure

  # detect version

  # query overstack name/install/update time

  # query list of overstack nodes
  
  # query overstack node types

  # query hardware make/model
  
  # query compute node local disk

  # report status

  print(json.dumps(osp_envvars))
  print(json.dumps(osp_status))
