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

import ospsurvey.probes.services
import ospsurvey.probes.endpoints
import ospsurvey.probes.servers
import ospsurvey.probes.nodes
import ospsurvey.probes.stack

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

def check_undercloud_services(services, profile):
  """
  Check that the undercloud services match the expected services from the profile
  """

  # count the services and compare to the expected number
  service_count_actual = len(services)
  service_profile = profile['profile']['undercloud']['services']
  service_count_expected = len(service_profile)

  logging.debug("service count - expected: {}, actual: {}".format(
    service_count_expected,
    service_count_actual))

  # check that the list of expected services matches
  service_names_expected = set(service_profile)
  service_names_actual = set(s.Name for s in services)

  missing_services = service_names_expected - service_names_actual
  extra_services = service_names_actual - service_names_expected

  logging.debug("\n - missing services: {}\n- extra services: {}".format(missing_services, extra_services))

  return {
    'count': {
      'expected': service_count_expected,
      'actual': service_count_actual
      },
    'missing': list(missing_services),
    'extra': list(extra_services)
    }

def read_profile_hints(template_dir=os.path.join(os.environ['HOME'], "templates")):
  """
  Find the list of defined profiles and any assignment hints from the templates
  """

  # read the template files and find any files and structures that contain Hints
  # find the
  template_files = [tf for tf in os.listdir(template_dir) if tf.endswith(".yaml")]
  logging.debug("found {} yaml files in template dir {}".format(len(template_files), template_dir))

  # find any hints
  for filename in template_files:
    template_data = yaml.load(open(os.path.join(template_dir, filename)))

    # check if it has hints.
    if 'parameter_defaults' in template_data:
      hint_keys = [k for k in template_data['parameter_defaults'].keys() if k.endswith("Hints")]
      if len(hint_keys) > 0:
        logging.debug(json.dumps(template_data))

    
def resolve_host_roles(servers, hostname_map):
  """
  Use the stack environment to identify server hosts and roles for them
  """
  # use the HostnameMap and *SchedulerHints to determine the role of each
  # server
  #
  # invert the HostnameMap so the hostname is the key and the
  # node label hint is the value:
  logging.debug(hostname_map)
  node_label_map = {v:k for (k,v) in hostname_map.items()}
  logging.debug(node_label_map)
  # Get all of the *Hints structures
  #  Get the role names from them
  #  Get the capabilities:node: pattern strings
  #for server in servers:
    
  

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
  logging.debug(yaml.dump(profile))

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
  
  check_undercloud_services(services, profile)

  # get overcloud stack name
  stacks = ospsurvey.probes.stack.list_stacks()
  stack_name = stacks[0].Stack_Name
  
  # get overcloud stack environment
  stack_env = ospsurvey.probes.stack.get_environment(stack_name)

  server_roles = resolve_host_roles(servers, stack_env.parameter_defaults['HostnameMap'])
  
  #read_profile_hints()
