"""
Collect the survey information
"""

import platform

import version

def collect():

  data = {}

  os = platform.linux_distribution()
  
  data['os'] = {
    'distro': os[0],
    'release': os[1]
  }

  osp = version.version()

  data['osp'] = osp
  return data
