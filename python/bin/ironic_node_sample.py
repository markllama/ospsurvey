#!/usr/bin/env python

from __future__ import print_function

import os

import keystoneauth1.session
import keystoneauth1.identity.v3

import ironicclient

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

    print(os_credentials)
    ks_auth = keystoneauth1.identity.v3.Password(**ks_credentials)

    ks_session = keystoneauth1.session.Session(auth=ks_auth)


    client = ironicclient.client.Client(
        1,
        os_ironic_api_version=os.getenv("IRONIC_API_VERSION"),
        session=ks_session
    )

    nodes = client.node.list()

    print(nodes[0].instance_uuid)

    node = client.node.get_by_instance_uuid(nodes[0].instance_uuid)

    print(node.properties)
