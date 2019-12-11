#!/usr/bin/env python
from __future__ import print_function

import unittest

import ospsurvey.version

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

    
    def test_version_from_bad_file(self):
        """
        If the result is invalid return None for both strings
        """
        test_file = "tests/data/rhosp-release-bad"
        v0 = ospsurvey.version.version_from_file(test_file)
        self.assertIsInstance(v0, tuple)
        self.assertEqual(len(v0), 2)

        self.assertEqual(v0, (None, None))

    def test_version_from_rpm_repo(self):
        """
        Get the RPM info and parse for repo.
        """
        test_package = "filesystem"
        ospsurvey.version.get_package_info(test_package)

    def test_get_package_info(self):
        test_package = "filesystem"

        # find a package you know is installed

        # get the package info

        # make sure it worked and you got a good string
        i0 = ospsurvey.version.get_package_info(test_package)

        # it should succeed

        # it should return a an array of strings
        # The strings should include a Name, Version, Release and From repo

    def test_get_package_repo_name(self):

        repo_info = {
            "good": [
                "Nothing to see here",
                "From repo : 1234",
                "More Nothing : emptyinformation"
            ],

            "bad": [
                "no lines that match"
            ]
        }
        repo_name = ospsurvey.version.get_package_repo_name(repo_info['good'])

        self.assertEqual(repo_name, "1234")

        no_repo =  ospsurvey.version.get_package_repo_name(repo_info['bad'])
        self.assertEqual(no_repo, None)


    def test_version_from_repo_name(self):
        """
        Get an OSP version from a known RH repository name
        Return the OSP number or None if not found
        """
        
        v0 = ospsurvey.version.get_version_from_repo_name("nothing matches")
        self.assertEqual(v0, None)

        v1 = ospsurvey.version.get_version_from_repo_name(
            "rhel-7-server-openstack-10-rpms")

        self.assertEqual(v1, "10")

if __name__ == "__main__":
    unittest.main()
