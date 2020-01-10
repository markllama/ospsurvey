#!/bin/env python
from __future__ import print_function

import argparse
import json
import logging
import os
import re
import sys

import ospsurvey.probes.nodes
import ospsurvey.probes.servers
import ospsurvey.probes.stack

def parse_cli():
  """
  Define the CLI arguments for querying a server role
  """
  parser = argparse.ArgumentParser()

  parser.add_argument('-d', '--debug', action='store_true', default=False,
                      help="Print additional information for status and diagnosis")
  selector_group = parser.add_mutually_exclusive_group()
  selector_group.add_argument('-s', '--server',
                              help="Find the role of a specified server")
  selector_group.add_argument('-r', '--role',
                              help="Find the servers under a specified role")

  env_group = parser.add_mutually_exclusive_group()
  env_group.add_argument('-V', '--require-env', dest="require_env", action='store_true', default=True)
  env_group.add_argument('--no-require-env', dest="require_env", action='store_false')
  return parser.parse_args()

def check_credentials():
  """
  Check that the OSP credentials have been sourced into the envinronment
  OS_AUTH_URL
  OS_USERNAME
  OS_PASSWORD

  There are others, but use these as canaries
  """

  required_variables = ('OS_AUTH_URL', 'OS_USERNAME', 'OS_PASSWORD')

  logging.debug("checking openstack auth environment variables")
  ok = True
  for var in required_variables:
    if not var in os.environ:
      logging.warning("missing required environment variable: {}".format(var))
      ok = False
    else:
      logging.debug("OpenStack Auth Var: {} = {}".format(var, os.environ[var]))

  return ok

def node_role(node, hints):
  """
  Given a node and the hints map, return the role for a node
  NOTE: this is very inefficient as it compiles the re's every pass
  """

  tag = node.Properties['capabilities']['node']
  
  for p in hints:
    #print("checking hint {} on node {}".format(p, node.Name))
    if re.match(p, tag):
      return hints[p]

  return None

if __name__ == "__main__":

  opts = parse_cli()

  if opts.debug:
    logging.basicConfig(level=logging.DEBUG)

  if opts.require_env and check_credentials() is False:
    logging.fatal("Missing required environment variables: aborting survey")
    sys.exit(1)

  # ---------------------------------------------------------------------------
  # Prepare to answer the question: get needed baseline information
  #   Nodes and hints
  # ---------------------------------------------------------------------------

  # The first step is to get the list of roles and the node tagging hints
  # to map nodes to roles
  stacks = ospsurvey.probes.stack.list_stacks()
  stack_name = stacks[0].Stack_Name
  stack_env = ospsurvey.probes.stack.get_environment(stack_name)
  # find all of the hints
  hints = {re.sub('SchedulerHints$', '', k):v['capabilities:node'] for (k,v) in stack_env.parameter_defaults.items() if k.endswith("Hints")}
  node_patterns = {re.sub('%index%', '\d+$', v):k for (k,v) in hints.items()}

  # Get a list of all nodes because you can't easily query a single node by its
  # instance UUID
  nodes = ospsurvey.probes.nodes.list_nodes()

  if opts.server:
    logging.info("Find the role of server {}".format(opts.server))
    server = ospsurvey.probes.servers.get_server(opts.server)
    logging.debug(server)

    # with the server we now have the server id.
    # now we need to find the node that corresponds
    one_node = [n for n in nodes if server.id == n.Instance_UUID]
    if len(one_node) == 0:
      logging.fatal("no node matching server {}".format(server.name))

    if len(one_node) > 1:
      logging.fatal("ambiguous match: {} nodes matching server {}".format(len(one_node), server.name))
      
    # and then the role of that node
    node = one_node[0]
    logging.debug("found node {} matching server {}".format(node.Name, server.name))
    role = node_role(node, node_patterns)
    print(role)
    sys.exit(0)

  #
  # We have the list of nodes. We could filter those for the requested role
  # and then query for the individual servers
  # Or just get all the servers and filter here.
  node_roles = {n.Name:node_role(n, node_patterns) for n in nodes}
  servers = ospsurvey.probes.servers.list_servers()
  
  if opts.role:
    # just return all the servers with a given role
    logging.info("Find the servers with role {}".format(opts.role))
    sys.exit(0)
    
  logging.info("List all servers and their roles")
