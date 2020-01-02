"""
Query endpoint information from OpenStack service
"""
import subprocess
import json
from collections import namedtuple

from ospsurvey.deunicode import decode_dict

def list_endpoints(source_fn=subprocess.check_output, interface=None):
  """
  Get a list of services in JSON format and convert it to a named tuple
  that can be used as a object for analysis
  """
  query_string = "openstack service list --long --format json"
  if interface != None:
    query_string += "--interface {}".format(interface)
  
  endpoint_string = source_fn(query_string.split())
  endpoint_data = json.loads(endpoint_string, object_hook=decode_dict)

  if len(endpoint_data) == 0:
    return []

  EpClass = namedtuple('Endpoint', endpoint_data[0].keys())

  # each element needs to be turned into a named tuple
  endpoints = [EpClass._make(ep.values()) for ep in endpoint_data]
  return endpoints


def get_endpoint(id_or_name, source_fn=subprocess.check_output):
  """
  Get the information about a single service and return a named tuple
  """
  query_string = "openstack endpoint show --format json {}".format(id_or_name)
  endpoint_string = source_fn(query_string.split())
  endpoint_info = json.loads(endpoint_string, object_hook=decode_dict)

  EpClass = namedtuple('Endpoint', endpoint_info.keys())
  endpoint = EpClass._make(endpoint_info.values())
  
  return endpoint


def check_endpoint(endpoint):
  """
  Given an endpoint object, verify that the endpoint is responding to queries
  """

  pass
  

