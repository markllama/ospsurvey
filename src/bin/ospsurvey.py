#! /usr/bin/env python
from __future__ import print_function
"""
Survey an OSP system.
Determine the installed version and query a number of stats and configurations to report
the current status of the cluster.

Output data either as a pretty table or as JSON structured data for consumption by a database
or analysis tool.
"""

#
# Standard Libraries
#
import sys
import os
import json

from oslo_serialization import jsonutils

# Several libraries have moved between Python 2 and 3
if sys.version_info.major < 3:
  from urlparse import urlparse
  #import httplib as httplib
  import urllib2 as urllib
else:
  from urllib.parse import urlparse
  import urllib.request as urllib
  #import http.client as httplib

import subprocess

#
# OpenStack libraries
#
import keystoneauth1
import keystoneauth1.identity
import keystoneauth1.session

import keystoneclient
import keystoneclient.v3

import novaclient
import novaclient.client

# ----------------------------------------------------------------------------
# Setup Functions
# ----------------------------------------------------------------------------

osp_status = {}

def get_osp_module_versions():
  """
  Collect the module versions of the OSP API 
  """
  versions = {
    'keystoneauth1': keystoneauth1.__version__,
    'keystoneclient': keystoneclient.__version__,
    'novaclient': novaclient.__version__
  }

  return versions

#
# Authentication Setup
#

#
# The list of environment variables used for OSP API access
# Map the environment variable name to the parameter named used by the
# Keystoneauth Session object
#
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
  Collect and return the OSP authentication values from the environment
  """
  envvars = {}
  for k,v in osp_varmap.items():
    envvars[v] = os.environ[k] if k in os.environ else None

  return envvars


def create_keystone_session(credentials):
  """
  Create a keystone Session object from the provided credentials.
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

def collect_services(ksclient):
  """
  Query and return the set of admin services
  """
  services = ksclient.services.list()

  print(jsonutils.to_primative(services, level=1))

  return services

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

    ping = ping_test(url.hostname)
    if ping:
      print("- HOST OK")
    else:
      print("- HOST ERROR")

    url_status = url_check(endpoint.url)
    if url_status:
      print("- ENDPOINT OK")
    else:
      print("- ENDPOINT ERROR")
      

def ping_test(host, count=1):
  """
  Send a set of ICMP packets at a host and check that it responds.
  """
  ping_cmd = "ping -q -n -c {} {}" # insert count and host
  dev_null = open("/dev/null")
  return subprocess.call(ping_cmd.format(count, host).split(), stdout=dev_null, stderr=dev_null) == 0

def url_check(url):

  try: 
    query = urllib.urlopen(url)
  except urllib.HTTPError as err:
    if err.code == 300:
      print("multiple choice redirect")
      return True
    elif err.code == 400:
      print("bad request")
      return True
    elif err.code == 401:
      print("unauthorized")
      return True
    elif err.code == 404:
      print("not found")
      return True
    else:
      raise err
  except urllib.URLError as err:
    print("url error")
    return False
    
  response_code = query.getcode()

  return response_code == 200 
#  conn = httplib.HTTPConnection(url.netloc)
#  conn.request("GET", url.path)
  

# --------------------------------------------------------------------------
#
# MAIN - connect to the OSP service and start gathering data
# 
# --------------------------------------------------------------------------
  
if __name__ == "__main__":
  
  # report OSP Library Versions
  osp_status['python_versions'] = get_osp_module_versions()

  # Read he OSP related environment variables, used to connect to the service
  # endpoints
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

  # At least in the stackrc I have seen, the v3/ suffix has been missing from
  # the AUTH_URL.  Add it if using version 3 and it's not in the URL
  if osp_envvars['identity_api_version'] == "3" and \
     not osp_envvars['auth_url'].endswith('v3'):
    osp_envvars['auth_url'] += "v3/"

  # create session for API auth and access
  print("creating session to: {}".format(osp_envvars['auth_url']))
  ks_session = create_keystone_session(osp_envvars)
  #ks_session = keystoneauth1.session.Session(auth=osp_envvars)

  # The API client uses the session object for auth and service endpoint
  # discovery. Create a client for each service to talk to.
  print("creating keystone client")
  ks = keystoneclient.client.Client(session=ks_session)

  services = collect_services(ks)
  
  # using the keystone client, check the service endpoints
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
