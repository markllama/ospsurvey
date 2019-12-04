#!/usr/bin/env python
from __future__ import print_function

import unittest

from context import ospsurvey

class TestOspVersion(unittest.TestCase):

    def test_version_from_file(self):
        """
        Read a version file and return the version number
        """
        test_file = "tests/data/rhosp-release"
        v0 = ospsurvey.version.version_from_file(test_file)

        # must return a tuple with two strings in it
        self.assertIsInstance(v0, tuple)
        self.assertEqual(len(v0), 2)

        # first string is OSP version
        self.assertEqual("13.0.8", v0[0])

        # second string is OpenStack release name
        self.assertEqual("Queens", v0[1])

    

    def test_version_from_rpm_repo(self):
        """
        If the result is invalid return None for both strings
        """
        test_file = "tests/data/rhosp-release-bad"
        v0 = ospsurvey.version.version_from_file(test_file)
        self.assertIsInstance(v0, tuple)
        self.assertEqual(len(v0), 2)

        self.assertEqual(v0, (None, None))


if __name__ == "__main__":
    unittest.main()
