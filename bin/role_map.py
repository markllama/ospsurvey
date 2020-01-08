#!/usr/bin/env python
from __future__ import print_function

import re

import ospsurvey.probes.nodes
import ospsurvey.probes.stack

def node_capabilities(node):
  """
  Return just the dict of capabilities strings from a NodeClass object
  """

  cap_string = node.Properties['capabilities']
  cap_entry_strings = cap_string.split(',')
  cap_entries = map(lambda c: c.split(':'), cap_entry_strings)
  capabilities = {c[0]:c[1] for c in cap_entries}

  return capabilities
                    

if __name__ == "__main__":

  # list the stacks and get the environment
  stacks = ospsurvey.probes.stack.list_stacks()
  stack_name = stacks[0].Stack_Name
  stack_env = ospsurvey.probes.stack.get_environment(stack_name)

  # find all of the hints

  hints = {k:v for (k,v) in stack_env.parameter_defaults.items() if k.endswith("Hints")}

  print(hints)
  
  node_patterns = {v['capabilities:node']:re.sub('\SchedulerHints$','',k) for (k,v) in hints.items()}

  print(node_patterns)

  nodes = ospsurvey.probes.nodes.list_nodes()

  node_tags = [{"Name":n.Name, "Capabilities":n.Properties['capabilities']} for n in nodes]

  print(node_tags)
  
