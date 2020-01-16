#!/usr/bin/env python
from __future__ import print_function
"""
Query and compile subscription manager information:
  subscription status
  configuration
  consumed subscriptions
  enabled repos
"""

import configparser
import json
import re
import subprocess  

# Extend the ConfigParser to create a dict
# from https://stackoverflow.com/questions/3220670/read-all-the-contents-in-ini-file-into-dictionary-with-python

def sm_output_parse(sm_output):
  """
  Title
  Key: Value [...Values]
  """

  #
  # The header begins and ends with a marker line matching: ^+-+
  #
  marker_re = re.compile(r'^\+-+\+$')

class SmConfigParser(configparser.ConfigParser):

  def as_dict(self):
    d = dict(self._sections)
    for k in d:
      d[k] = dict(self._defaults, **d[k])
      d[k].pop('__name__', None)
    return d

if __name__ == "__main__":

  sm_config_string_orig = subprocess.check_output("sudo subscription-manager config".split())

  # remove lines afer the one containing "default value in use"
  default_line = '[] - Default value in use'
  sm_config_all_lines = sm_config_string_orig.split('\n')
  sm_config_lines = sm_config_all_lines[:sm_config_all_lines.index(default_line)]
  sm_config_string = '\n'.join(sm_config_lines)

  sm_config_string_default = re.sub(r'= \[\]', '= default', sm_config_string)
  sm_config_string_unbracket = re.sub(r'= \[([^]]+)\]', r'= \1', sm_config_string_default)

  sm_config = SmConfigParser()
  sm_config.read_string(unicode(sm_config_string_unbracket))

  print(json.dumps(sm_config.as_dict()))
  
  #sm_config.read('/etc/rhsm/rhsm.conf')
