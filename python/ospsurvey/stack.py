"""
Gather information about the overcloud stack
"""

import subprocess
import heatclient

def stack_info(osp_credentials):
  """
  Query the overcloud stack information
  """

  client = heatclient.client.Client(1, endpoint=heaturl)

  
  pass


