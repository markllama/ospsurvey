#!/usr/bin/env python

from __future__ import print_function

import os

import keystoneauth1.session
import keystoneauth1.identity.v3

import novaclient.client

# Only v3 credentials
ks_credentials = {
    "auth_url": os.getenv('OS_AUTH_URL'),
    "username": os.getenv('OS_USERNAME'),
    "password": os.getenv('OS_PASSWORD'),
    "user_domain_name": os.getenv('OS_USER_DOMAIN_NAME'),
    "project_name": os.getenv('OS_PROJECT_NAME'),
    "project_domain_name": os.getenv('OS_PROJECT_DOMAIN_NAME')
}

if __name__ == "__main__":

    print(ks_credentials)

    ks_auth = keystoneauth1.identity.v3.Password(**ks_credentials)
    ks_session = keystoneauth1.session.Session(auth=ks_auth)


    client = novaclient.client.Client(2,session=ks_session)

    print(client)
    servers = client.servers.list()
    print(servers[0].id)
    server = client.servers.get(servers[0].id)


    print(server.networks)
