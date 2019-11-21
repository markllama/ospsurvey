#!/bin/bash

function increment_version() {
    local version="$1"
    local field="$2"
    
    local major=0
    local minor=0
    local build=0

    # break down the version number into it's components
    regex="([0-9]+).([0-9]+).([0-9]+)"
    if [[ $version =~ $regex ]]; then
        major="${BASH_REMATCH[1]}"
        minor="${BASH_REMATCH[2]}"
        build="${BASH_REMATCH[3]}"
    fi

    # check paramater to see which number to increment
    case $field in
        "major")
            major=$(echo $major+1 | bc)
            minor=0
            build=0
            ;;
        "minor")
            minor=$(echo $minor + 1 | bc)
            build=0
            ;;
        "build")
            build=$(echo $build + 1 | bc)
            ;;
        *)
            build=$(echo $build + 1 | bc)
            ;;
    esac
    
    echo "${major}.${minor}.${build}"
}

NEW_VERSION=$(increment_version $1 $2)
echo "new version: ${NEW_VERSION}"
