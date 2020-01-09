#!/usr/bin/env python
from __future__ import print_function

import re

import ospsurvey.probes.nodes
import ospsurvey.probes.stack

def node_role(node, hints):
  """
  Given a node and the hints map, return the role for a node
  NOTE: this is very inefficient as it compiles the re's every pass
  """

  tag = node.Properties['capabilities']['node']
  
  for p in hints.keys():
    print("checking hint {} on node {}".format(p, node.Name))
    if re.match(p, tag):
      return hints[p]

  return None

def get_server_from_node(node, servers):
  """
  Given the list of servers and a single node, find the server associated,
  if any
  """
  # get the node instance ID
  instance_id = node.Instance_UUID
  node_servers = [s for s in servers if s.ID == instance_id]
  if len(node_servers) == 0:
    return None

  return node_servers[0]
  
if __name__ == "__main__":

  # list the stacks and get the environment
  stacks = ospsurvey.probes.stack.list_stacks()
  stack_name = stacks[0].Stack_Name
  stack_env = ospsurvey.probes.stack.get_environment(stack_name)

  # find all of the hints

  hints = {re.sub('SchedulerHints$', '', k):v['capabilities:node'] for (k,v) in stack_env.parameter_defaults.items() if k.endswith("Hints")}

  print(hints)
  
  node_patterns = {re.sub('%index%', '\d+$', v):k for (k,v) in hints.items()}

  print(node_patterns)

  nodes = ospsurvey.probes.nodes.list_nodes()

  node_tags = [{"Name":n.Name, "Capabilities":n.Properties['capabilities']} for n in nodes]

  node_roles = {n.Name:node_role(n, node_patterns) for n in nodes}

  print(node_roles)

  # Now assocate nodes to servers and we'll have a role map for servers
  # For each node, look up the instance UID, then find that instance and
  # get the display name.  Associate the display name with the role
  server_roles = {node_role(n,servers):node_roles[n.Name] for n in nodes}

  print(server_roles)
