#!/usr/bin/env python

from __future__ import print_function

import os

import keystoneauth1.session
import keystoneauth1.identity

import novaclient.client

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

    client = novaclient.client.Client(2,session=ks_session)

    print(client)
    servers = client.servers.list()
    print(servers[0].id)
    server = client.servers.get(servers[0].id)


    print(server.networks)
