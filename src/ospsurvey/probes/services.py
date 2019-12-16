"""
Query an openstack service and return an object or list of objects representing
The services available.
"""
import subprocess
import json
from collection import namedtuple

from ../deunicode import decode_dict

def list_services():
  """
  """
  query_string = "openstack service list --long --format json"
  service_string = subprocess.check_output(query_string.split())
  service_list = json.loads(service_string, object_hook=decode_dict)
  return service_list


def get_service(id_or_name):
  query_string = "openstack service show --format json {}".format(id_or_name)
  service_string = subprocess.check_output(query_string.split())
  print service_string
  service_info = json.loads(service_string, object_hook=decode_dict)
  return service_info
