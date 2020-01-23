#!/usr/bin/env python
from __future__ import print_function
"""
Test functions that process and report the status of Red Hat software
subscriptions, repositories and updates
"""

import unittest

import re

import ospsurvey.probes.software

class TestRHN(unittest.TestCase):

  def test_RHNConfig(self):
    """
    Verify that get_rhn_config() can read and parse an up2date file
    """

    # make sure all of the fields are here
    cfg = ospsurvey.probes.software.get_rhn_config('tests/data/up2date')
    self.assertEqual(len(cfg.keys()), 21)

    # make sure none have [comment] in them
    comment_keys = [c for c in cfg.keys() if re.match('.*\[comment\].*', c)]
    self.assertEqual(len(comment_keys), 0)

    # make sure the blank fields are correctly processed
    blank_fields = [f for f in cfg.keys() if cfg[f] == '']
    self.assertEqual(len(blank_fields), 5)

if __name__ == "__main__":
  unittest.main()
