#! /usr/bin/env python
from __future__ import print_function

#
# Read the templates/roles/roles_data.yaml to get a list of roles
# Then read the templates/40-ips-from-pool-all.yaml for hints
#

import os
import argparse
import json
import yaml
import re

yaml_files = {
    "roles": "roles/roles_data.yaml",
    "ips": "40-ips-from-pool-all.yaml"
}

hints_re = re.compile("^.*SchedulerHints$")

def parse_cli():

    parser = argparse.ArgumentParser()

    parser.add_argument("--templates", default=os.path.join(os.getenv("HOME"), "templates"))
    parser.add_argument("--server-data", required=False)

    opts = parser.parse_args()
    return opts

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



def server_role(server_name, role_catalog):
    """
    1) given server name, determine node id from HostnameMap
    2) given node id, determine role
       a) remove stack name from the beginning of the node id
       b) replace node id index with %index%
       c) find matching Scheduler Hints
    """
    pass

if __name__ == "__main__":
    print("Begin")
    opts = parse_cli()

    roles = read_roles(os.path.join(opts.templates, yaml_files['roles']))

    ips_data = read_ip_assignments(os.path.join(opts.templates, yaml_files['ips']))

    hostname_map = ips_data['parameter_defaults']['HostnameMap']
    print(hostname_map)
    node_map = {v:k for (k,v) in hostname_map.items()}
    print(node_map)

    hints = [h for h in ips_data['parameter_defaults'] if hints_re.match(h)]

    if opts.server_data != None:
        server_data = read_servers(opts.server_data)

    #
    # - Now the real thing:
    #
    # assign a role to each server
    role_map = {}
    
    for s in server_data:
        print(server_role(s, role_map))
    
    print("End")
