#!/bin/env python
from __future__ import print_function

"""
Collect information from the overcloud nodes
"""

import os
import argparse
import logging
import sys

def parse_cli_arguments():

  parser = argparse.ArgumentParser()
  parser.add_argument("-d", "--debug", action="store_true", default=False,
                      help="Print additional information for status and diagnosis")

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

  opts = parse_cli_arguments()
  if opts.debug:
    logging.basicConfig(level=logging.DEBUG)

  if opts.require_env and check_credentials() is False:
    logging.fatal("Missing required environment variables: aborting survey")
    sys.exit(1)
