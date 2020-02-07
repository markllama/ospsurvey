"""
Classes and Functions to query the software update status of a Red Hat
server.
"""
import re
import subprocess

class Yum():

  def __init__(self):
    self._repos = None
    self._history = None
    self._updates = None
    self._cves = None

    
    
  def _repo_names(self, selector='enabled'):
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

  def repos(self, selector='enabled', refresh=False):
    if self._repos == None or refresh == True:
      repo_names = self._repo_names()

      repos = {}
      for name in repo_names:
        repos[name] = self.repo_info(name)
      
      self._repos = repos

    return self._repos

  def history(self, count=1, refresh=False):
    return []

  def updates(self, refresh=False):
    #
    # Updates required and available
    #
    """
    Query the package updates available with yum
    Header: Loaded plugins...
    Columns: Advisory ID, reason/level, package name
    Footer: updateinfo list done
    """
    if self._updates == None or refresh == True:
      update_string = subprocess.check_output('sudo yum updateinfo list security'.split())
      update_lines = update_string.split('\n')
      # The header and footer are the first and last lines

      packages = {}
      for line in update_lines:
        # skip non-record lines
        if len(line) == 0 \
           or line.startswith('Loaded') \
           or line.startswith('updateinfo') \
           or line.startswith('This system'):
          continue

        # Split into data components
        # All record lines are three components
        try:
          (advisory, reason, package) = re.split('\s+', line)
        except ValueError:
          continue
    
        if not package in packages:
          packages[package]=list()
      
        packages[package].append({'advisory': advisory, 'level': re.sub('/Sec.$', '', reason)})

      self._updates = packages

    return self._updates

  def cves(self, refresh=False):
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
      try:
        (advisory, reason, package) = re.split('\s+', line.strip())
      except ValueError:
        continue
    
      if not package in packages:
        packages[package]=list()
      
      packages[package].append({'advisory': advisory, 'level': re.sub('/Sec.$', '', reason)})

    return packages


  def repo_info(self, repo_name, refresh=False):
    """
    Get detailed information on a specified yum repository
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
       or line.startswith('updateinfo') \
       or line.startswith('This system'):
      continue

    # Split into data components
    # All record lines are three components
    try:
      (advisory, reason, package) = re.split('\s+', line)
    except ValueError:
      continue
    
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
    try:
      (advisory, reason, package) = re.split('\s+', line.strip())
    except ValueError:
      continue
    
    if not package in packages:
      packages[package]=list()
      
    packages[package].append({'advisory': advisory, 'level': re.sub('/Sec.$', '', reason)})

  return packages
  
