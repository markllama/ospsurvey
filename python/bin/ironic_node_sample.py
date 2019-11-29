#!/usr/bin/env python

from __future__ import print_function

import os

import keystoneauth1.session
import keystoneauth1.identity

import keystonclient.client

import ironicclient.client

auth_env_keys = [
    'OS_AUTH_URL', 'OS_USERNAME', 'OS_PASSWORD',
    'OS_TENANT_NAME', 'OS_TENANT_ID',
    'OS_PROJECT_NAME', 'OS_PROJECT_ID',
    'OS_USER_DOMAIN_NAME', 'OS_USER_DOMAIN_ID',
    'OS_PROJECT_DOMAIN_NAME', 'OS_PROJECT_DOMAIN_ID'
]

def get_os_creds():
    return { k.lower()[3:]:os.environ[k] for k in os.environ.keys() if k in auth_env_keys }

def os_session(os_creds):
    ks_auth = keystoneauth1.identity.Password(**os_creds)
    ks_session = keystoneauth1.session.Session(auth=ks_auth)

    return ks_session

if __name__ == "__main__":

    ks_creds = get_os_creds()
    ks_session = os_session(ks_creds)

    ks_auth_version = int(os.getenv('OS_IDENTITY_API_VERSION')) if 'OS_IDENTITY_API_VERSION' in os.environ.keys() else 2


    ks = keystoneclient.client.Client(ks_auth_version, session=ks_session, auth_url=ks_creds['auth_url'])

    ironic_endpoint = ks.get_endpoint(ks_session, 'baremetal')
    
    ks_token = ks.get_token(ks_session)
    client = ironicclient.client.Client(
        1,
        ks_token
    )

    nodes = client.node.list()

    print(nodes[0].instance_uuid)

    #node = client.node.get_by_instance_uuid(nodes[0].instance_uuid)

    #print(node.properties)
