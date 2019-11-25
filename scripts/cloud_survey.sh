#!/bin/sh
#
# This script is meant to survey the version, size composition and status of a Red Hat OpenStack cluster 
#

# Allow ENV override of variables

: ${UNDERCLOUD_RC_FILE:=${HOME}/stackrc}

#
# OSP9, 10, 11 and 12 are EOL and should get no updates. This table is based on the
# version and release number of the python-tripleoclient package.  THis is a proxy for
# a proper version number but should be sufficient until all clouds have moved to OSP13
#
declare -A TRIPLEO_VERSION_MAP
TRIPLEO_VERSION_MAP=(
    [2.0.0-15]=OSP9
    [2.0.0-14]=OSP9
    [2.0.0-13]=OSP9
    [2.0.0-4]=OSP9
    [2.0.0-3]=OSP9
    [2.0.0-2]=OSP9

    [5.4.6-4]=OSP10
    [5.4.6-3]=OSP10
    [5.4.6-2]=OSP10
    [5.4.6-1]=OSP10
    [5.4.5-1]=OSP10
    [5.4.3-1]=OSP10
    [5.4.2-2]=OSP10
    [5.4.2-1]=OSP10

    [6.2.4-1]=OSP11
    [6.2.3-1]=OSP11
    [6.2.0-2]=OSP11
    [6.2.0-1]=OSP11
    [6.1.0-6]=OSP11

    [7.3.10-4]=OSP12
    [7.3.10-3]=OSP12
    [7.3.8-1]=OSP12
    [7.3.3-7]=OSP12
)
#
# This script generates input and updates for cells of a spreadsheet that shows the current
# state of a Red Hat OpenStack cluster
#
# Fields:
#   * Product Version
#   * Scheduled Upgrade
#   * Node Counts:
#   ** Director
#   ** Controller
#   ** Compute*
#   ** Logging
#   ** Cinder
#   ** Swift
#   ** Ceph*
#   * Total Nodes
#   * Version 7 count
#   * Version 8 count
#   * Compute Local Storage
#   * Hardware Product
#
# Compute and Ceph nodes can have multiple 
#

#
# Determine the hardware using dmidecode. Record type 1 Is System Information
#   Use variable and echo to remove newlines
function hardware_product_name() {
    PRODUCT_INFO=$(sudo dmidecode -t 1 | grep 'Manufacturer\|Product Name' | tr -d \\t)
    echo ${PRODUCT_INFO}
}


#
# /etc/os-release is present on all relevent systems
# It is defined in the systemd spec
# https://www.freedesktop.org/software/systemd/man/os-release.html
# ID and VENDOR_ID
function os_version() {
    # Allow override of release file
    : ${RELEASE_FILE=/etc/os-release}
    local -a RELEASE=($(grep -e '^\(ID\|VERSION_ID\)=' ${RELEASE_FILE} | sed -e 's/.*=//'))
    echo ${RELEASE[@]}
}

function package_version() {
    local PKGNAME=$1

    local QUERYFORMAT='%{VERSION}-%{RELEASE}\n'
    local VERSION_STRING=$(rpm --query --queryformat "${QUERYFORMAT}" ${PKGNAME})

    # Remove everything after that last dot in the version-release string
    VERSION_STRING=${VERSION_STRING%\.*}

    echo ${VERSION_STRING}
}


#
# For OSP13+ use /etc/rhosp-release
# Before OSP13 Red Hat did not provide a standard version file location
# Proxies can be used: YUM repo names, 
#
function osp_version() {
    : ${OSP_RELEASE_FILE:=/etc/rhosp-release}
    echo -n "Release: "
    if [ -r "${OSP_RELEASE_FILE}" ] ; then
        cat ${OSP_RELEASE_FILE}
    else
        echo ${TRIPLEO_VERSION_MAP[$(package_version python-tripleoclient)]}
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

function overcloud_stack_name() {
    local -a STACKS
    STACKS=($(openstack stack list -f value -c 'Stack Name'))

    # Check for length != 1
    
    echo ${STACKS[0]}
}

function overcloud_server_types() {
    local CLOUD=$1
    SERVER_TYPES=($(openstack stack resource list ord1 -f value -c resource_name | grep Servers))

    echo ${SERVER_TYPES[@]}

}

function overcloud_server_count() {
    local CLOUD=$1
    local SERVER_TYPE=$2
    openstack stack resource show ${CLOUD} ${SERVER_TYPE} -f json | jq '.attributes.value | length'
}

function main() {
    echo "BEGIN: main"

    echo "PRODUCT INFO: $(hardware_product_name)"
    echo "OS VERSION  : $(os_version)"
    echo "OSP VERSION : $(osp_version)"
    echo "END: main"
}

#
#
#
main
