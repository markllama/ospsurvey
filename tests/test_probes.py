#!/usr/bin/env python
"""
"""

import unittest

import ospsurvey.probes.services
import ospsurvey.probes.endpoints


class TestProbes(unittest.TestCase):

  def setUp(self):
    pass
  
  def test_services_list(self):

    s = ospsurvey.probes.services.list_services()


  def test_services_get(self):
    s = ospsurvey.probes.services.get_service('nova')


  def test_endpoints_list(self):

    s = ospsurvey.probes.endpoints.list_endpoints()

  def test_endpoints_get(self):
    s = ospsurvey.probes.endpoints.get_endpoint('f776829dcb7e4f25a2aadd588246f9c9')
