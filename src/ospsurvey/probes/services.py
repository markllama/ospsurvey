"""
Query an openstack service and return an object or list of objects representing
The services available.
"""
import subprocess
import json
from collections import namedtuple

from ospsurvey.deunicode import decode_dict

def list_services(source_fn=subprocess.check_output):
  """
  Get a list of services in JSON format and convert it to a named tuple
  that can be used as a object for analysis
  """
  query_string = "openstack service list --long --format json"
  service_string = source_fn(query_string.split())
  service_list = json.loads(service_string, object_hook=decode_dict)
  
  return service_list


def get_service(id_or_name, source_fn=subprocess.check_output):
  """
  Get the information about a single service and return a named tuple
  """
  query_string = "openstack service show --format json {}".format(id_or_name)
  service_string = source_fn(query_string.split())
  service_info = json.loads(service_string, object_hook=decode_dict)
  return service_info
