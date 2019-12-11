#! /usr/bin/env python
from __future__ import print_function
"""
Survey an OSP system.
Determine the installed version and query a number of stats and configurations to report
the current status of the cluster.

Output data either as a pretty table or as JSON structured data for consumption by a database
or analysis tool.
"""

import sys
import os
import json

if sys.version_info.major < 3:
  import urlparse
else:
  import urllib.parse as urlparse

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


def confirm_endpoints(ksclient):
  """
  Check the endpoint access for the keystone client provided
  """

  endpoints = (ep for ep in ksclient.endpoints.list() if ep.interface == 'admin')

  print('Endpoints')
  for endpoint in endpoints:
    # get the service by id
    ep_service = ksclient.services.get(endpoint.service_id)
    print('Service Name: {}, Service Type: {}, URL: {}'.format(
      ep_service.name, ep_service.type, endpoint.url
    ))

    # ping the URL host
    url = urlparse(endpoint.url)
    print("testing endpoint {} - host: {}, port: {}".format(
      ep_service.name, url.hostname, url.port
    ))

    # 
  }

  
if __name__ == "__main__":
  
  # report OSP Library Versions
  osp_status['python_versions'] = get_osp_module_versions()

  osp_envvars = get_osp_envvars()
  # check for auth info
  # must have auth_url, username and password at least
  if not (osp_envvars['username'] and osp_envvars['password'] and osp_envvars['auth_url']):
    print(
      '''
      FATAL: no OSP credentials.  Please source the stackrc file and try again
      '''.strip()
    )
    sys.exit(1)

  if osp_envvars['identity_api_version'] == "3" and not osp_envvars['auth_url'].endswith('v3'):
    osp_envvars['auth_url'] += "v3/"
  

  # create session
  print("creating sesson to: {}".format(osp_envvars['auth_url']))
  ks_session = create_keystone_session(osp_envvars)

  print("creating keystone client")
  ks = keystoneclient.client.Client(session=ks_session)

  #endpoints = ks.endpoints.list()
  confirm_endpoints(ks)
  
  # NOTE: All inputs have NOVA_VERSION at 1.1, but it's deprecated
  # The novaclient library sets API_MIN_VERSION at 2.1 and MAX_VERSION at 2.6
  print("creating nova client")
  nova = novaclient.client.Client(2, session=ks_session)
  
  # create functions with session
  #servers = nova.servers.list()

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
