#!/usr/bin/env python
"""
Survey a Red Hat OpenStack Platform deployment
"""
from __future__ import print_function

import argparse
import json
import logging
import os
import re
import sys
import yaml
# import argparse
# import json

import ospsurvey.probes.services
import ospsurvey.probes.endpoints
import ospsurvey.probes.servers
import ospsurvey.probes.nodes

# This pattern should match the OSP version string in /etc/rhosp-release
DEFAULTS = {
  'config_file': "/home/stack/.ospsurvey.yaml",
  'release_file': "/etc/rhosp-release",
  'release_pattern': r'Red Hat OpenStack Platform release (((\d+)\.(\d+)\.(\d+)) \((.*)\))$'
}

# CONFIG_FILE = DEFAULTS['config_file']
# CONFIG_FILE = "tests/ospsurvey_conf.yaml"
# RELEASE_FILE = DEFAULTS['release_file']


def get_cli_arguments():
  """
  Parse and return the CLI arguments
  """

  parser = argparse.ArgumentParser()

  parser.add_argument('-d', '--debug', action='store_true', default=False)
  parser.add_argument('-c', '--config', default="~/.ospsurvey.yaml")
  parser.add_argument('-r', '--release-file', default="/etc/rhosp-release")
  parser.add_argument('-V', '--require-env', dest="require_env", action='store_true', default=True)
  parser.add_argument('--no-require-env', dest="require_env", action='store_false')

  parser.add_argument('-P', '--profile-dir', default="./profiles")
  
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

  opts = get_cli_arguments()

  debug = opts.debug
  config_file = opts.config
  release_file = opts.release_file

  if debug:
    logging.basicConfig(level=logging.DEBUG)

  if opts.require_env and check_credentials() is False:
    logging.fatal("Missing required environment variables: aborting survey")
    sys.exit(1)
  
  # load configuration
  if os.path.exists(config_file):
    if debug:
      logging.debug("loading config: {}".format(config_file))
    config_stream = open(config_file)
    config = yaml.load(config_stream, Loader=yaml.Loader)

    logging.debug(config)

  # survey

  # determine version
  # if /etc/rhosp-release does not exist
  #  1) this is not a director node (OSP not installed)
  #  2) this is a pre-13 installation - flag and quit
  if not os.path.exists(release_file):
    #
    # You can't survey a system that isn't there
    #
    logging.fatal("Cannot determine OSP release: release file {} does not exist".format(release_file))
    sys.exit(1)

  # read the release string and remove whitespace
  release_string = open(release_file).read().strip()
  logging.debug("release string: {}".format(release_string))

  release_re = re.compile(DEFAULTS['release_pattern'])
  release_data = release_re.match(release_string)

  if release_data is None:
    logging.fatal("Cannot determine release number: \n  Invalid release string: {}".format(release_string))
    sys.exit(1)

  logging.debug(release_data.groups())
  (major, minor, build) = release_data.groups()[2:5]

  #
  # If it exists, read the cluster profile for the indicated version
  #
  
  profile_filename = os.path.join(opts.profile_dir, "osp-{}.yaml".format(major))
  logging.debug("profile for OSP {}: {}".format(major, profile_filename))

  if os.path.exists(profile_filename):
    logging.debug("reading profile for OSP {}: {}".format(major, profile_filename))
    profile_stream = open(profile_filename)
    profile = yaml.load(profile_stream, Loader=yaml.Loader)

  else:
    logging.debug('no profile found: {} does not exist'.format(profile_filename))
    profile = None

  #
  # Now we know what release we're working with and have read the survey profile
  # for the release.  The profile indicates what we should find in a nominal
  # deployment.
  #
  # start examining the cluster
  #

  # get the list of undercloud services
  services = ospsurvey.probes.services.list_services()
  endpoints = ospsurvey.probes.endpoints.list_endpoints()
  servers = ospsurvey.probes.servers.list_servers()
  nodes = ospsurvey.probes.nodes.list_nodes()

  # Questions we can now answer:

  # do all expected services exist?
  # are all present services active?
  # to all services have required endpoints?
  # are all services responding on the accessable interfaces?
  #   admin, internal, public

  # are all nodes in use?
  # what profile matches each server
