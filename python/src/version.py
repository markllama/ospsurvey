#
# version.py: determine the OSP version installed on a director host
#
from __future__ import print_function

"""
version(): determine the OSP version installed on a director host

If /etc/rhosp-release exists:
  Read the version from there
Else
  check the package version of the python-tripleoclient RPM
  and compare to a table of known releases
"""

import os
import re
import subprocess


default_version_file = "/etc/rhosp-release"

# heat_template_version
#        : 2015-04-30 - OSP9
#        : pike       - OSP12
#        : queens     - OSP13

# repos numbers
# yum info installed python-tripleoclient | grep 'From repo' | cut -d: -f

yum_repos = {
    "osp9-rhel-x86_64-server-7-ost-9-director": "9",
    "rhel-7-server-openstack-10-rpms": "10",
    "rhel-7-server-openstack-12-rpms": "12",
    "rhel-7-server-openstack-13-rpms": "13"
}

default_osp_package = "python_tripleoclient"


def version(version_file=default_version_file):
    """
    TBD
    """

    if os.path.exists(version_file):
        (version_number, version_name) = version_from_file(version_file)

    return version_number


def version_from_file(version_file):
    """
    TBD
    """

    version_pattern = "Red Hat OpenStack Platform release ([\d.]+) \((.*)\)"
    version_re = re.compile(version_pattern)
    
    # should try and check.  A single line with a newline
    release_string = open(version_file).read().strip()
    release_match = version_re.match(release_string)

    if release_match == None:
        return (None,None)

    return release_match.groups()

def version_from_repo_name(package_name=default_osp_package):

    info_command_template = "yum info installed {}"
    info_command = info_command_template.format(package_name)

    # subprocess wants a list of arguments, not a single string
    package_info = subprocess.check_output(info_command.split())

    # check_output returns the stdout as a single string
    package_lines = package_info.split("\n")

    # should check that there is EXACTLY one line
    repo_lines = [line for line in package_lines if line.startswith("From repo ")]
    repo_name = repo_lines[0].split(':')[1].strip()

    version_string = yum_repos[repo_name] if repo_name in yum_repos.keys() else None

    return version_string

    

    
                 
    
