#!/bin/env python
from __future__ import print_function

import argparse
import json
import logging
import os
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

  if opts.server:
    logging.info("Find the role of server {}".format(opts.server))
    server = ospsurvey.probes.servers.get_server(opts.server)
    logging.debug(server)

    # with the server we now have the server id.
    # now we need to find the node that corresponds
    nodes = ospsurvey.probes.nodes.list_nodes()
    nodes = [n for n in nodes if server.id == n.Instance_UUID]
    if len(nodes) == 0:
      logging.fatal("no node matching server {}".format(server.name))

    if len(nodes) > 1:
      logging.fatal("ambiguous match: {} nodes matching server {}".format(len(nodes), server.name))
      
    # and then the role of that node
    node = nodes[0]
    logging.debug("found node {} matching server {}".format(node.Name, server.name))

    # now find the role of that node
    stacks = ospsurvey.probes.stack.list_stacks()
    stack_name = stacks[0].Stack_Name
    stack_env = ospsurvey.probes.stack.get_environment(stack_name)

    # find all of the hints
    hints = {re.sub('SchedulerHints$', '', k):v['capabilities:node'] for (k,v) in stack_env.parameter_defaults.items() if k.endswith("Hints")}



  elif opts.role:
    logging.info("Find the servers with role {}".format(opts.role))

  else:
    logging.info("List all servers and their roles")
