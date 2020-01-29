"""
Classes and Functions to query the software update status of a Red Hat
server.
"""
import os
import re
import subprocess
import tempfile

#
# Subscription Manager
#
import ConfigParser as configparser

# Extend the ConfigParser to create a dict
# from https://stackoverflow.com/questions/3220670/read-all-the-contents-in-ini-file-into-dictionary-with-python
class SmConfigParser(configparser.ConfigParser):

  def as_dict(self):
    d = dict(self._sections)
    for k in d:
      d[k] = dict(self._defaults, **d[k])
      d[k].pop('__name__', None)
    return d

    
def get_sm_config():
  """
  Read the subscription-manager configuration and return it as a dict
  """
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

  
  return sm_config.as_dict()

def get_sm_status():
  """
  Gather subscription manager and yum status
  """

  # define the value search patterns
  status_re = re.compile("Overall Status: (.*)")
  purpose_re = re.compile("System Purpose Status: (.*)")

  # get the actual status
  try:
    sm_status_string = \
      subprocess.check_output("sudo subscription-manager status".split())
  except subprocess.CalledProcessError as e:
    return {'status': 'Unsubscribed'}
  
  # extract the status string
  status_match = status_re.search(sm_status_string, re.MULTILINE)
  status = status_match.groups()[0]

  # extract the purpose string
  purpose_match = purpose_re.search(sm_status_string, re.MULTILINE)
  purpose = purpose_match.groups()[0]

  # report the results as a structure.
  return {'status': status, 'purpose': purpose}

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


def get_sm_consumed():
  """
  Report the consumed subscriptions
  """
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

  return subscriptions


def get_sm_repos():
  """
  Get a list of repositories enabled in subscription manager
  """
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

  return repos

def sm_check():
  """
  Check if the host is registered using Subscription Manager
  """
  try:
    subprocess.check_call(
      "sudo subscription-manager status".split(),
      stdout=open(os.devnull),
      stderr=subprocess.STDOUT)
  except subprocess.CalledProcessError as e:
    # called but unsuccessful
    return False
  except OSError as e:
    # command not found
    return False

  return True
    


#
# RHN Classic
#
def rhn_check():
  """
  Check if the host is registered with RHN Classic or Sat5
  """
  # This needs renaming to show intent
  
  try:
    subprocess.check_call(
      "/usr/sbin/rhn_check",
      stdout=open(os.devnull),
      stderr=subprocess.STDOUT)
  except:
    # CalledSubprocessError returns non-0
    # OSError - no such file
    return False

  return True

def get_rhn_config(up2date_file='/etc/sysconfig/rhn/up2date'):
  """
  Read and return the RHN/Sat5 subscription configuration
  """
  config_file = open(up2date_file)
  lines = config_file.readlines()
  config_file.close()
  
  varlist = [l.strip('\n').split('=') for l in lines if '=' in l and not re.match('.*\[comment\].*', l)]
  
  config = {v[0]:v[1] for v in varlist}
  
  return config

#
# Yum repos and RPMs installed
#
def get_repo_list(selector='enabled'):
  """
  Return a list of YUM repos
  """
  if selector == '':
    selector = 'enabled'
    
  if selector not in ['enabled', 'disabled', 'all']:
    raise ValueError("invalid selector {} - valid selectors: enabled, disabled, all".format(selector))

  repo_string = subprocess.check_output('sudo yum repolist {}'.format(selector).split())
  repo_lines = repo_string.split('\n')

  # the first line should match Loaded Plugins
  # Line 2 may match
  #   This system is receiving updates from RHN Classic or Red Hat Satellite.
  # Line N:
  #   repo id            repo name                        status
  #   no space string    human string                     num of packages?
  # Line ...:
  # Last Line: repolist: nnn
  plugins_lineno = [i[0] for i in enumerate(repo_lines) if repo_lines[i[0]].startswith('Loaded')][0]
  header_lineno = [i[0] for i in enumerate(repo_lines) if repo_lines[i[0]].startswith('repo id')][0]
  footer_lineno = [i[0] for i in enumerate(repo_lines) if repo_lines[i[0]].startswith('repolist')][0]

  # Get the lines between the header and footer, take the first word and just
  # the first half of that.
  repo_ids = [l.split()[0].split('/') for l in repo_lines[header_lineno+1:footer_lineno-1]]

  repo_names = [r[0] for r in repo_ids]

  # if the repo info is out of date, it can have a leading bang (!)
  # remove that too
  repo_names = [re.sub('^!', '', n) for n in repo_names]
  
  return repo_names
  
def get_repo_info(repo_name):
  """
  """
  repo_string = subprocess.check_output("sudo yum repoinfo {}".format(repo_name).split())
  repo_lines = repo_string.split('\n')

  # Ignore the "plugins" line and everything before it
  plugins_lineno = [i[0] for i in enumerate(repo_lines) if repo_lines[i[0]].startswith('Loaded')][0]

  repo_info = {}
  for line in repo_lines[plugins_lineno+1:]:
    # stop when you get to a blank line
    if line == '':
      break

    # Match the key-values around the first colon (:).  Remove white space
    info_match = re.match('^\s*([^:]+[^ ])\s*:\s*(.*)$', line)
    if info_match:
      (k, v) = info_match.groups()
      
      repo_info[k] = v

  return repo_info

# SAMPLE
# yum history info
# Loaded plugins: product-id, search-disabled-repos, subscription-manager
# Transaction ID : 142
# Begin time     : Wed Jan 22 07:56:42 2020
# Begin rpmdb    : 1208:938a582ff2c1559ddafe7b8cd79c3b2dc8dee22c
# End time       :            07:56:43 2020 (1 seconds)
# End rpmdb      : 1209:f9d7dd8d1a5b709ebaa88fca24391194bd1bff7d
# User           :  <rack>
# Return-Code    : Success
# Command Line   : install nano
# Transaction performed with:
#     Installed     rpm-4.11.3-40.el7.x86_64                    @rhel-7-server-rpms
#     Installed     subscription-manager-1.24.13-3.el7_7.x86_64 @rhel-7-server-rpms
#     Installed     yum-3.4.3-163.el7.noarch                    @rhel-7-server-rpms
# Packages Altered:
#     Install nano-2.3.1-10.el7.x86_64 @rhel-7-server-rpms
# history info

def get_yum_history():
  """
  Get information on the most recent software update activity
  """
  info_string = subprocess.check_output("sudo yum history info".split())
  info_lines = info_string.split("\n")
  history = {}

  kv_pattern = re.compile('^([^:]+)\s*:\s+(.*)$')
  rpm_record_pattern = re.compile('^\s+([^\s]+)\s+([^\s]+)\s+(.*)$')
  
  for line in info_lines[1:]:

    kv = kv_pattern.match(line)
    if kv != None:
      (k,v) = kv.groups()
      history[k.strip()] = v

  # Find the start of any of the record sections
  (t_start, p_start, s_start) = (0, 0, 0)
  for i, line in enumerate(info_lines):    
    if line == 'Transaction performed with:':
      t_start = i
      continue
    
    if line == 'Packages Altered:':
      p_start = i
      continue

    if line == 'Scriptlet output:':
      s_start = i
      continue

    if line.startswith("Loaded plugins:"):
      plugins_lineno = i
      continue

  # Step through the transaction lines
  #  End the loop when the first line does not match the record pattern
  if t_start:
    transactions = []
    for line in info_lines[t_start+1:]:
      r_match = rpm_record_pattern.match(line)
      if r_match == None:
        break

      (action, package, repo) = r_match.groups()
      record = {'action': action, 'package': package, 'repo': repo}
      transactions.append(record)

    history['transactions'] = transactions

  # Step through the package lines
  # End the loop when the first line does not match the record pattern
  if p_start:
    packages = []
    for line in info_lines[p_start+1:]:
      r_match = rpm_record_pattern.match(line)
      if r_match == None:
        break

      (action, package, repo) = r_match.groups()
      if action == "Update":
        packages[-1]['new_version'] = package
      else:
        record = {'action': action, 'package': package, 'repo': repo}
        packages.append(record)
    history['packages'] = packages

  # Ignoring Scriptlet output for now - MAL 20200128
  
  # remove Loaded Plugins
  # Note/Remove updates from classic or sat

  return history


#
# Updates required and available
#
def check_updates(check_func=subprocess.check_output):
  """
  Query the package updates available with yum
  Header: Loaded plugins...
  Columns: Advisory ID, reason/level, package name
  Footer: updateinfo list done
  """
  update_string = check_func('sudo yum updateinfo list security'.split())
  update_lines = update_string.split('\n')
  # The header and footer are the first and last lines

  packages = {}
  for line in update_lines:
    # skip non-record lines
    if len(line) == 0 \
       or line.startswith('Loaded') \
       or line.startswith('updateinfo'):
      continue

    # Split into data components
    (advisory, reason, package) = re.split('\s+', line)
    
    if not package in packages:
      packages[package]=list()
      
    packages[package].append({'advisory': advisory, 'level': re.sub('/Sec.$', '', reason)})

  return packages

def check_cves(check_func=subprocess.check_output):
  """
  Query the vulnerability updates available with yum
  Header: Loaded plugins...
  Columns: Advisory ID, reason/level, package name
  Footer: updateinfo list done
  """
  update_string = check_func('sudo yum updateinfo list cves'.split())
  update_lines = update_string.split('\n')
  # The header and footer are the first and last lines

  packages = {}
  for line in update_lines:
    # skip non-record lines
    if len(line) == 0 \
       or line.startswith('Loaded') \
       or line.startswith('updateinfo'):
      continue

    # Split into data components - CVES start with white space
    (advisory, reason, package) = re.split('\s+', line.strip())
    
    if not package in packages:
      packages[package]=list()
      
    packages[package].append({'advisory': advisory, 'level': re.sub('/Sec.$', '', reason)})

  return packages
  
