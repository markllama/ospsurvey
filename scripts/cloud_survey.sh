#!/bin/sh
#
# This script is meant to survey the version, size composition and status of a Red Hat OpenStack cluster 
#

# Allow ENV override of variables

OSP_RELEASE_FILE=${OSP_RELEASE_FILE:=/etc/rhosp-release}
UNDERCLOUD_RC_FILE=${UNDERCLOUD_RC_FILE:=${HOME}/stackrc}

function hardware_product_name() {

    PRODUCT_INFO=$(sudo dmidecode -t 1 | grep 'Manufacturer\|Product Name' | tr -d \\t)
    echo ${PRODUCT_INFO}
}

function osp_version() {
    echo "Release: "
    if [ -r ${OSP_RELEASE_FILE} ] ; then
        cat ${OSP_RELEASE_FILE}
    fi
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
