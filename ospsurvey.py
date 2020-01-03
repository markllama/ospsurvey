#!/usr/bin/env python
"""
Survey a Red Hat OpenStack Platform deployment
"""
from __future__ import print_function

import argparse
import logging
import os
import re
import sys
import yaml
#import argparse
#import json

#import ospsurvey

# This pattern should match the OSP version string in /etc/rhosp-release
defaults = {
  'config_file': "/home/stack/.ospsurvey.yaml",
  'release_file': "/etc/rhosp-release",
  'release_pattern': "Red Hat OpenStack Platform release (((\d+)\.(\d+)\.(\d+)) \((.*)\))$"
}

#config_file = defaults['config_file']
#config_file = "tests/ospsurvey_conf.yaml"
#release_file = defaults['release_file']

def get_cli_arguments():
  parser = argparse.ArgumentParser()

  parser.add_argument('-d', '--debug', action='store_true', default=False)
  parser.add_argument('-c', '--config', default="~/.ospsurvey.yaml")
  parser.add_argument('-r', '--release-file', default="/etc/rhosp-release")
  
  return parser.parse_args()

if __name__ == "__main__":

  opts = get_cli_arguments()
  
  debug = opts.debug
  config_file=opts.config
  release_file = opts.release_file
  
  logging.basicConfig(level=logging.DEBUG)
  
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

  release_re = re.compile(defaults['release_pattern'])
  release_data = release_re.match(release_string)

  if release_data == None:
    logging.fatal("Cannot determine release number: \n  Invalid release string: {}".format(release_string))
    sys.exit(1)
    
  logging.debug(release_data.groups())

  print('continuing')

