"""
Query an openstack service and return an object or list of objects representing
The services available.
"""
import subprocess
import json
from collections import namedtuple

from ospsurvey.deunicode import decode_dict

def list_stacks(source_fn=subprocess.check_output):
  """
  Get a list of stacks in JSON format and convert it to a named tuple
  that can be used as a object for analysis
  """
  query_string = "openstack stack list --format json"
  stack_string = source_fn(query_string.split())
  stack_records = json.loads(stack_string, object_hook=decode_dict)

  if len(stack_records) == 0:
    return []

  StackClass = namedtuple(
    "StackClass",
    [s.replace(' ', '_') for s in stack_records[0].keys()]
  )
  stacks = [StackClass._make(s.values()) for s in stack_records]

  return stacks

def get_environment(stack_name, source_fn=subprocess.check_output):
  """
  Retrieve and parse the stack environment for the overcloud stack
  """
  query_string = "openstack stack environment show --format json {}".format(stack_name)
  env_string = source_fn(query_string.split())
  env_records = json.loads(env_string, object_hook=decode_dict)

  StackEnvClass = namedtuple(
    "StackEnvClass",
    [s.replace(' ', '_') for s in env_records.keys()]
  )
  stack_env = StackClass._make(env_records.values())
  return stack_env
