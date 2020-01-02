#!/usr/bin/env python
"""
"""

import unittest

import ospsurvey.probes.services
import ospsurvey.probes.endpoints
import ospsurvey.probes.nodes


class TestProbes(unittest.TestCase):

  def setUp(self):
    pass
  
  def test_services_list(self):

    s = ospsurvey.probes.services.list_services()
    self.assertGreater(len(s), 0, "No services present or reported")


  def test_services_get(self):
    services = ospsurvey.probes.services.list_services()
    s = ospsurvey.probes.services.get_service(services[0].Name)

  def test_endpoints_list(self):

    e = ospsurvey.probes.endpoints.list_endpoints()

    self.assertGreater(len(e), 0, "No endpoints present or reported")

  def test_endpoints_get(self):
    endpoints = ospsurvey.probes.endpoints.list_endpoints(interface="public")
    e = ospsurvey.probes.endpoints.get_endpoint(endpoints[0].ID)

  def test_nodes_list(self):
    s = ospsurvey.probes.nodes.list_nodes()

  def test_nodes_get(self):
    s = ospsurvey.probes.nodes.get_node('node1')
