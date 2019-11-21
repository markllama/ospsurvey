#!/bin/sh
#
# This script is meant to survey the version, size composition and status of a Red Hat OpenStack cluster 
#

# Allow ENV override of variables

: ${UNDERCLOUD_RC_FILE:=${HOME}/stackrc}

function hardware_product_name() {

    PRODUCT_INFO=$(sudo dmidecode -t 1 | grep 'Manufacturer\|Product Name' | tr -d \\t)
    echo ${PRODUCT_INFO}
}

function osp_version() {
    : ${OSP_RELEASE_FILE:=/etc/rhosp-release}
    echo "Release: "
    if [ -r "${OSP_RELEASE_FILE}" ] ; then
        cat ${OSP_RELEASE_FILE}
    else
        echo "OSP <13"
    fi
}

function server_flavor() {
    local server_name_id=$1
    openstack server show ${server_name_id} -f json | jq --raw-output .flavor | cut -d' ' -f1
}

function node_capabilities() {
    local SERVER=$1
    local -a CAPS
    
    CAPS=($(IFS=, openstack baremetal node show ${SERVER} -f json | jq --raw-output .properties.capabilities))
    echo ${CAPS[@]}
}

function main() {
    echo "BEGIN: main"

    echo PRODUCT INFO: $(hardware_product_name)
    echo OSP VERSION : $(osp_version)
    echo "END: main"
}

#
#
#
main
