#!/usr/bin/env python
"""
"""

import unittest

import ospsurvey.probes.services


class TestProbes(unittest.TestCase):

  def test_services_list(self):

    s = ospsurvey.probes.services.list_services()


  def test_services_get(self):
    s = ospsurvey.probes.services.get_service('nova')
