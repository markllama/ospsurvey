from __future__ import print_function

import unittest

import ospsurvey.version

class TestSample(unittest.TestCase):

  def test_sample(self):
    self.assertTrue(True)
    v = ospsurvey.version.version()

    print(v)
