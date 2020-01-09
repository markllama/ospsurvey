#!/bin/env python
from __future__ import print_function

import argparse
import json
import logging
import os
import sys

import ospsurvey.probes.servers

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
      logging.fatal("no node matching server {}".server.Name)
      
    # and then the role of that node
    node = nodes[0]
    logging.debug("found node {} matching server {}".format(node.Name, server.Name))

  elif opts.role:
    logging.info("Find the servers with role {}".format(opts.role))

  else:
    logging.info("List all servers and their roles")
