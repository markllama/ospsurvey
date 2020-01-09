"""
Query an openstack service and return an object or list of objects representing
The services available.
"""
from collections import namedtuple
import json
import logging
import re
import subprocess

from ospsurvey.deunicode import decode_dict

def list_servers(source_fn=subprocess.check_output):
  """
  Get a list of servers in JSON format and convert it to a named tuple
  that can be used as a object for analysis
  """
  query_string = "openstack server list --long --format json"
  server_string = source_fn(query_string.split())
  server_records = json.loads(server_string, object_hook=decode_dict)

  if len(server_records) == 0:
    return []

  ServerClass = namedtuple(
    "ServerClass",
    [s.replace(' ', '_') for s in server_records[0].keys()]
  )
  servers = [ServerClass._make(s.values()) for s in server_records]
  return servers

def get_server(id_or_name, source_fn=subprocess.check_output):
  """
  Get the information about a single server and return a named tuple
  """
  query_string = "openstack server show --format json {}".format(id_or_name)
  server_string = source_fn(query_string.split())
  server_info = json.loads(server_string, object_hook=decode_dict)

  logging.debug("server_info: {}".format(server_info))
  
  # Convert the JSON object to a proper class.
  # BUT, the JSON keys have colons in them that are not allowed
  # And hyphens and spaces.
  # Colons should really create sub-objects
  
  ServerClass = namedtuple(
    "ServerClass",
    [re.sub('[ -:]', '_', s) for s in server_info.keys()]
  )

  server = ServerClass._make(server_info.values())
  
  return server
