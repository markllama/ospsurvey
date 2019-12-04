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


# In OSP 13+ you can read this file to get OSP version and upstream release
default_version_file = "/etc/rhosp-release"

# heat_template_version
#        : 2015-04-30 - OSP9
#        : pike       - OSP12
#        : queens     - OSP13

# repos numbers
# yum info -C installed python-tripleoclient | grep 'From repo' | cut -d: -f

#
# The OSP packages are installed from specific repositories.  You can query a
# package and then lookup the repo name in this table.
#
yum_repos = {
    "osp9-rhel-x86_64-server-7-ost-9-director": "9",
    "rhel-7-server-openstack-10-rpms": "10",
    "rhel-7-server-openstack-12-rpms": "12",
    "rhel-7-server-openstack-13-rpms": "13"
}

default_osp_package = "python_tripleoclient"


def version(version_file=default_version_file):
    """
    Query and report the OSP version installed.
    """

    if os.path.exists(version_file):
        (version_number, version_name) = version_from_file(version_file)

    return version_number


def version_from_file(version_file):
    """
    From OSP 13 on the version release and build numbers are reported in a
    file: /etc/rhosp-release.
    It reports the OSP version and the upstream release name
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
    """
    The source repo name is stored with the package.
    Query the package information only for the installed package and
    work from cached data to avoid side effects to the host.
    The "From repo" line indicates where the package came from.
    That name should indicate the major version of OSP from a table.
    """
    
    info_command_template = "yum info installed --cacheonly {}"
    info_command = info_command_template.format(package_name)

    # subprocess wants a list of arguments, not a single string
    package_info = subprocess.check_output(info_command.split())

    # check_output returns the stdout as a single string
    # Convert to an array of lines
    package_lines = package_info.split("\n")

    # should check that there is EXACTLY one line
    repo_lines = \
        [line for line in package_lines if line.startswith("From repo ")]

    # "From repo    : <repo name>"
    # Get the value and remove white space.
    repo_name = repo_lines[0].split(':')[1].strip()
    
    version_string = yum_repos[repo_name] \
        if repo_name in yum_repos.keys() \
           else None

    return version_string

    

    
                 
    
