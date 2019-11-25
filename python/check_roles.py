#! /usr/bin/env python
from __future__ import print_function

#
# Read the templates/roles/roles_data.yaml to get a list of roles
# Then read the templates/40-ips-from-pool-all.yaml for hints
#

import os
import argparse #
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

    
if __name__ == "__main__":
    print("Begin")
    opts = parse_cli()
    print(opts)

    roles = read_roles(os.path.join(opts.templates, yaml_files['roles']))

    print(role_names(roles))

    ips_data = read_ip_assignments(os.path.join(opts.templates, yaml_files['ips']))

    hints = [h for h in ips_data['parameter_defaults'] if hints_re.match(h)]

    print("hints: {}".format(hints))
    print(ips_data['parameter_defaults']['HostnameMap'])
    
    
    
    print("End")
