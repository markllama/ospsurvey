"""
Classes and Functions to query the software update status of a Red Hat
server.
"""
import logging
import os
import re
import subprocess
import tempfile

#
# Subscription Manager
#
class SubscriptionManager():
  """
  Query and report status of Subscription Manager
  """
  def __init__(self):
    self._subscribed = None
    self._config = None
    self._status = None
    self._purpose = None
    self._consumed = None
    self._repos = None
  
  def subscribed(self, refresh=False):
    """
    Check if the host is registered using Subscription Manager
    """
    logging.debug("checking subscription")
    if self._subscribed == None or refresh == True:
      try:
        subprocess.check_call(
          "sudo subscription-manager status".split(),
          stdout=open(os.devnull),
          stderr=subprocess.STDOUT)
      except subprocess.CalledProcessError as e:
        # called but unsuccessful
        self.subscribed = False
      except OSError as e:
        # command not found
        self._subscribed = False

      self._subscribed = True

    else:
      logging.debug("using cached value: {}".format(self._subscribed))
      
    return self._subscribed

  def config(self, refresh=False):
    """
    Read the subscription-manager configuration and return it as a dict
    """
    if self._config == None or refresh == True:
    
      config_string = subprocess.check_output("sudo subscription-manager config".split())

      # remove lines afer the one containing "default value in use"
      default_line = '[] - Default value in use'

      config_lines = config_string.split('\n')
      # remove the default line and everything after
      config_lines = config_lines[:config_lines.index(default_line)]
      # remove leading white space because ConfigParser doesn't like it.
      config_lines = [line.lstrip() for line in config_lines]

      config_string = "\n".join(config_lines)
      config_string = re.sub(r'= \[\]', '= default', config_string)
      config_string = re.sub(r'= \[([^]]+)\]', r'= \1', config_string)

      # Write and then read an anonymous temp file because ConfigParser can't
      # read strings
      tf = tempfile.TemporaryFile(mode='w+')
      tf.write(unicode(config_string))
      tf.seek(0)

      sm_config = SmConfigParser()
      sm_config.readfp(tf)

      self._config = sm_config.as_dict()
      
    return self._config

  def status(self, refresh=False):
    """
    Gather subscription manager and yum status
    """
    if self._status == None or refresh == True:
      # define the value search patterns
      status_re = re.compile("Overall Status: (.*)")
      purpose_re = re.compile("System Purpose Status: (.*)")

      # get the actual status
      try:
        sm_status_string = \
          subprocess.check_output("sudo subscription-manager status".split())

        # extract the status string
        status_match = status_re.search(sm_status_string, re.MULTILINE)
        self._status = status_match.groups()[0]

        # extract the purpose string
        purpose_match = purpose_re.search(sm_status_string, re.MULTILINE)
        self._purpose = purpose_match.groups()[0]
      
      except subprocess.CalledProcessError as e:
        self._status = "Unsubscribed"
        self._purpose = "Unknown"
  
    return {'status': self._status, 'purpose': self._purpose}


  def repos(self, refresh=False):
    """
    Get a list of repositories enabled in subscription manager
    """
    if self._repos == None or refresh == True:
      sm_repos_string = \
        subprocess.check_output("sudo subscription-manager repos --list-enabled".split())

      sm_repos_lines = sm_repos_string.split('\n')

      repos = {}

      # The first line of each subscription record will have this string
      marker = "Repo ID"
      # Get the index of each line with the marker in it
      # Those are the beginning lines of subscription records
      starts = [i for i, line in enumerate(sm_repos_lines) if line.startswith(marker + ':')]

      # Collect all of the subscription records
      for start in starts:
        # Clip out just the lines for this record from the output
        end = sm_repos_lines[start:].index("")
        repo_lines = sm_repos_lines[start:start + end]

        title, record = parse_sm_record(repo_lines)
        repos[title] = record

      self._repos = repos

    return self._repos


  def consumed(self, refresh=False):
    """
    Report the consumed subscriptions
    """
    if self._consumed == None or refresh == True:
      # get the actual status
      sm_consumed_string = \
        subprocess.check_output("sudo subscription-manager list --consumed".split())

      # read the header and get the title

      sm_consumed_lines = sm_consumed_string.split('\n')

      # 1st and 3rd lines should match "^\+-*\*$"
      # Second line is title, with white space stripped

      # lines are key/value, with multiple values signalled by white space at the
      # beginning of the line.
      # blank lines signal the end of a structure
      kv_re = re.compile("^([^:]+):\s+(.*)$")

      # Initialize the consumed subscriptions set
      subscriptions = {}

      # The first line of each subscription record will have this string
      marker = "Subscription Name"
      # Get the index of each line with the marker in it
      # Those are the beginning lines of subscription records
      starts = [i for i, line in enumerate(sm_consumed_lines) if line.startswith(marker + ':')]

      # Collect all of the subscription records
      for start in starts:

        # Clip out just the lines for this record from the output
        end = sm_consumed_lines[start:].index("")
        sub_lines = sm_consumed_lines[start:start + end]

        title, record = parse_sm_record(sub_lines)
        subscriptions[title] = record
        self._consumed = subscriptions

    return self._consumed  



# ----------------------------------------------------------------------------
# Module functions
# ----------------------------------------------------------------------------
# Extend the ConfigParser to create a dict
# from https://stackoverflow.com/questions/3220670/read-all-the-contents-in-ini-file-into-dictionary-with-python
import ConfigParser as configparser
class SmConfigParser(configparser.ConfigParser):

  def as_dict(self):
    d = dict(self._sections)
    for k in d:
      d[k] = dict(self._defaults, **d[k])
      d[k].pop('__name__', None)
    return d

def parse_sm_record(lines):
  """
  Create a dict record from a fragment of a subscription-manager output
  """
  # lines are key/value, with multiple values signalled by white space at the
  # beginning of the line.
  # blank lines signal the end of a structure
  kv_re = re.compile('^(([^:]+):)?\s+(.*)$')

  record = {}
  # The subscription name will be the key for each subscription record
  title = re.sub('^.*:\s+', '', lines[0]).strip()

  for l in lines[1:]:
    # check all lines for "((key):)? (value)"
    #new_value = kv_re.match('^(([^:]+):)?\s+(.*)$', l)
    new_value = kv_re.match(l)
    if new_value:
      a,k,v = new_value.groups()
      
      # If a key is present, this is a new field of the record
      if k:
        record[k] = v
        hold_k = k

      # If not, the field is a list of values.  Append to it
      else:
        if type(record[hold_k]) is list:
          record[hold_k].append(v)
        else:
          record[hold_k] = [record[hold_k], v]

  return title, record

