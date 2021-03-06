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


  node_keys = [k.replace(" ", "_").lower() for k in node_records[0].keys()]
  NodeClass = namedtuple("NodeClass", node_keys)
  nodes = [NodeClass._make(s.values()) for s in node_records]

  # pre-convert nested capabilities string to dict
  for n in nodes:
    n.properties['capabilities'] = node_capabilities(n)

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

  node.properties['capabilities'] = node_capabilities(node)
  
  return node


def node_capabilities(node):
  """
  Return just the dict of capabilities strings from a NodeClass object
  """

  if type(node.properties['capabilities']) is str:
    cap_string = node.properties['capabilities']
    cap_entry_strings = cap_string.split(',')
    cap_entries = map(lambda c: c.split(':'), cap_entry_strings)
    capabilities = {c[0]:c[1] for c in cap_entries}
  else:
    capabilties = node.properties['capabilities']

  return capabilities
                    

