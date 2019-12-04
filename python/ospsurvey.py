#!/usr/bin/env python
"""
Survey a Red Hat OpenStack Platform deployment
"""
from __future__ import print_function

#import sys
#import os
#import argparse
import json

import ospsurvey


if __name__ == "__main__":

  # collect everything at first
  ospdata = ospsurvey.collect()

  # start with just json
  print(json.dumps(ospdata, indent=2))
