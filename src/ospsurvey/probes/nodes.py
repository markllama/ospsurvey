"""
Query an openstack service and return an object or list of objects representing
The bare metal nodes included
"""
import subprocess
import json
from collections import namedtuple

from ospsurvey.deunicode import decode_dict

def list_nodes(source_fn=subprocess.check_output):
  """
  Get a list of nodesin JSON format and convert it to a named tuple
  that can be used as a object for analysis
  """
  query_string = "openstack baremetal node list --long --format json"
  node_string = source_fn(query_string.split())
  node_records = json.loads(node_string, object_hook=decode_dict)

  if len(node_records) == 0:
    return []

  node_keys = [k.replace(" ", "_") for k in node_records[0].keys()]
  NodeClass = namedtuple("NodeClass", node_keys)
  nodes = [NodeClass._make(s.values()) for s in node_records]
  return nodes

def get_node(id_or_name, source_fn=subprocess.check_output):
  """
  Get the information about a single node and return a named tuple
  """
  query_string = "openstack baremetal node show --format json {}".format(id_or_name)
  node_string = source_fn(query_string.split())
  node_info = json.loads(node_string, object_hook=decode_dict)

  NodeClass = namedtuple("NodeClass", node_info.keys())
  node = NodeClass._make(node_info.values())
  
  return node