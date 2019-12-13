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

default_osp_package = "python-tripleoclient"


def version(version_file=default_version_file, osp_package=default_osp_package):
    """
    Query and report the OSP version installed.
    """

    if os.path.exists(version_file):
        (version_string, version_name) = version_from_file(version_file)

    else:
        package_info = get_package_info(osp_package)
        repo_name = get_package_repo_name(package_info)
        version_string = get_version_from_repo_name(repo_name)

        if version_string == None:
            version_string = "unknown"
            
    return version_string


def version_from_file(version_filename):
    """
    From OSP 13 on the version release and build numbers are reported in a
    file: /etc/rhosp-release.
    It reports the OSP version and the upstream release name
    """

    version_pattern = "Red Hat OpenStack Platform release ([\d.]+) \((.*)\)"
    version_re = re.compile(version_pattern)
    
    # should try and check.  A single line with a newline
    
    version_file = open(version_filename)
    release_string = version_file.read().strip()
    version_file.close()
    
    release_match = version_re.match(release_string)

    if release_match == None:
        return (None,None)

    return release_match.groups()

def get_package_info(package_name):
    """
    Query the system for package information of a specified RPM
    Query the package information only for the installed package and
    work from cached data to avoid side effects to the host.
    Return a list of lines from the response STDOUT
    """
    
    info_command_template = "yum info installed --cacheonly {}"
    info_command = info_command_template.format(package_name)

    # subprocess wants a list of arguments, not a single string
    try:
        package_info = subprocess.check_output(info_command.split(),
                                               stderr=subprocess.STDOUT)
        package_info = str(package_info)
        
    except subprocess.CalledProcessError as e:
        print(e)
        package_info = ""

    return package_info.split("\n")

def get_package_repo_name(package_info):
    """
    The source repo name is stored with the package.
    The "From repo" line indicates where the package came from.

    Return the repo name or None if not found
    """

    # should check that there is EXACTLY one line
    repo_lines = \
        [line for line in package_info if line.startswith("From repo ")]

    # "From repo    : <repo name>"
    # Get the value and remove white space.
    if len(repo_lines) > 0:
        repo_name = repo_lines[0].split(':')[1].strip()
    else:
        repo_name = None

    return repo_name
    

def get_version_from_repo_name(package_repo_name):
    """
    Get the repo name for an OSP package
    That name should indicate the major version of OSP from a table.

    Return the version matching the repo name or None if not found
    """
    
    version_string = yum_repos[package_repo_name] \
        if package_repo_name in yum_repos.keys() \
           else None

    return version_string

    

    
                 
    
