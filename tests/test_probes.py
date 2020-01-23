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
    """
    Check that the list_services function returns a valid list
    of ServiceClass objects
    """
    
    s = ospsurvey.probes.services.list_services()
    self.assertGreater(len(s), 0, "No services present or reported")


  def test_services_get(self):
    """
    Check that the get_service function returns an object and has valid
    structure
    """
    services = ospsurvey.probes.services.list_services()
    s = ospsurvey.probes.services.get_service(services[0].Name)

  def test_endpoints_list(self):
    """
    Check that the list_endpoints function returns more than one element
    and those are valid objects
    """
    e = ospsurvey.probes.endpoints.list_endpoints()

    self.assertGreater(len(e), 0, "No endpoints present or reported")

  def test_endpoints_get(self):
    """
    Check that the get_endpoints returns a single valid EndpointClass object
    """
    endpoints = ospsurvey.probes.endpoints.list_endpoints(interface="public")
    e = ospsurvey.probes.endpoints.get_endpoint(endpoints[0].ID)

  def test_nodes_list(self):
    
    n = ospsurvey.probes.nodes.list_nodes()
    self.assertGreater(len(n), 0, "No nodes present or reported")

  def test_nodes_get(self):
    nodes = ospsurvey.probes.nodes.list_nodes()
    print("getting {}".format(nodes[0].Name))
    n = ospsurvey.probes.nodes.get_node(nodes[0].Name)
