#! /usr/bin/env python
from __future__ import print_function

#
# Find the count of each type of server:
#  Controller
#  Compute
#  BlockStorage
#  ObjectStorage
#  CephStorage

# get the list of overcloud servers deployed

# get the list of baremetal nodes available
#   with .properties.capabilities {"node": "hint"}
#    and provisioning state

# compare node hint to scheduler hint patterns

# get the HostnameMap and Scheduler Hints




#
# Data Sources:
#  openstack server list
#  openstack baremetal node list
#  openstack baremetal show - .properties.capabilities node=
#  templates/40-ips-from-pool-all.yaml
#  tempaltes/roles/roles_data.yaml

# Read the templates/roles/roles_data.yaml to get a list of roles
# Then read the templates/40-ips-from-pool-all.yaml for hints
# 
#

import os
import sys
import argparse
import json
import yaml
import re
import subprocess

yaml_files = {
    "roles": "roles/roles_data.yaml",
    "ips": "40-ips-from-pool-all.yaml"
}

hints_re = re.compile("^.*SchedulerHints$")

oscmd = {
    'node_list': "openstack baremetal node list -f json",
    'node_data': "openstack baremetal node show -f json"
}

# ===================================================================================================
# Functions
# ===================================================================================================

def parse_cli():

    parser = argparse.ArgumentParser()

    parser.add_argument("--templates", default=os.path.join(os.getenv("HOME"), "templates"))
    parser.add_argument("--server-data", required=False)

    opts = parser.parse_args()
    return opts


def get_nodes():
    """
    TBD
    """
    
    try:
        nodes_json = subprocess.check_output(oscmd['node_list'].split())
    except CalledProcessError as err:
        print("Execution failed:", e, file=sys.stderr)

    nodes = json.loads(nodes_json)

    return nodes

def get_node_data(node_name):
    """
    TBD
    """
    
    try:
        node_json = subprocess.check_output(oscmd['node_data'].split() + [node_name])
    except CalledProcessError as err:
        print("Execution failed:", e, file=sys.stderr)

    node = json.loads(node_json)

    return node

def get_node_capabilities(node):
    """
    TBD
    """

    cap_string = node['properties']['capabilities'].encode('ascii')

    # create an array of these strings
    cap_strings = cap_string.split(',')

    # convert those to key/value pairs
    cap_pairs = [cs.split(':') for cs in cap_strings]
    # convert those to key/value pairs
    caps = { k:v for k,v in cap_pairs }

    return caps

def read_roles(roles_file):

    f = open(roles_file)
    roles_data = yaml.load(f, Loader=yaml.Loader)
    return roles_data

def role_names(roles):
    return [r['name'] for r in roles]

def read_ip_assignments(ips_file):

    f = open(ips_file)
    ips_data = yaml.load(f, Loader=yaml.Loader)

    return ips_data

def read_servers(servers_file):
    
    f = open(servers_file)
    server_data = json.load(f)

    # convert the networks section to a dictionary
    for s in server_data:
        # A way-too-clever one-liner to convert a list of strings to a dict
        s['Networks'] = {n:ip for (n,ip) in [ns.split('=') for ns in s['Networks'].split(',')]}

    return server_data



def server_role(server_tag, role_map):
    """
    1) given server name, determine node id from HostnameMap
    2) given node id, determine role
       a) remove stack name from the beginning of the node id
       b) replace node id index with %index%
      c) find matching Scheduler Hints
    """
    print("Tag: {}, Role Map: {}".format(server_tag, role_map))
    roles = [role_map[r] for r in role_map.keys() if r in server_tag]
    return roles

if __name__ == "__main__":
    print("Begin")
    opts = parse_cli()

    # Get a list of hosts from hostname map
    print("get hostname map")
    ips_data = read_ip_assignments(os.path.join(opts.templates, yaml_files['ips']))
    hostname_map = ips_data['parameter_defaults']['HostnameMap']
    # invert the hostname-id map
    node_map = {v:k for (k,v) in hostname_map.items()}

    # get a list of nodes with capabilities from openstack baremetal nodes

    # get a list of servers from openstack server list

    print(node_map)

    print("End")

sys.exit()

    # roles = read_roles(os.path.join(opts.templates, yaml_files['roles']))

    # ips_data = read_ip_assignments(os.path.join(opts.templates, yaml_files['ips']))

    # hostname_map = ips_data['parameter_defaults']['HostnameMap']
    # node_map = {v:k for (k,v) in hostname_map.items()}

    
    # hint_keys = [h for h in ips_data['parameter_defaults'] if hints_re.match(h)]
    # hints = { h : ips_data['parameter_defaults'][h] for h in hint_keys}

    # # invert the hints so the the Role is the value and the hint pattern the key
    # # tag string fragement -> Role
    # # invert the hints structure so that the tag substring is the key and role is value
    # hint_map = { v['capabilities:node']:k for k,v in hints.items() }
    # # remove the index var from the tag string and the SchedulerHints from the role name
    # hint_map = { k.replace("%index%",''):v.replace("SchedulerHints",'') for k,v in hint_map.items() }

    # if opts.server_data != None:
    #     server_data = read_servers(opts.server_data)

    # #
    # # - Now the real thing:
    # #
    # # assign a role to each server
    # #
    # # Get the server names from openstack
    # role_map = {}
    
    # for s in server_data:
    #     node_tag = node_map[s['Name']]
    #     print("name: {}, node_tag: {}".format(s['Name'], node_tag))
    #     print("{} - Role: {}".format(s['Name'], server_role(node_tag, hint_map)))
            
