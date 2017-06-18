#!/usr/bin/env bash
#
# 19/08/2016
# Osvaldo Demo
# Version: %%VERSION%%
#
#
# Create the virtual-env for python 3.4 and install the base dependencies via pip
# Note this script will require access to the internet via a proxy.
#
#
#

VIRTUALENV=`which virtualenv`

function update_dependencies {
    if [[ -x ~/venv/bin/pip ]]; then
        # This requires internet connectivity!
        cd ~
        pip install -r web/requirements.txt
    else
        echo "ERROR: virtual-env was not created properly. Missing pip command!"
        exit 4
    fi
}

function usage {
cat << EOF
usage: $0 [-h] [-d] [-p <proxy_url>]

This scirpt create the python 3.4 virtual-env for iaas-lae-vsphere-api

        -h  hows this help
        -d  Debug mode
        -p  Proxy URL

Example:

$0 -p http://proxy.mycompany.com:3128/

EOF
exit 1
}


while getopts "p:d" OPTION
do
    case ${OPTION} in
            d) set -x
                ;;
            p) PROXY_URL="${OPTARG}"
                ;;
            h) usage
            ;;
            \?) usage
            ;;

    esac
done

if [[ -n "${PROXY_URL}" ]]; then
    export http_proxy="${PROXY_URL}"
    export https_proxy="${PROXY_URL}"
fi

PROXY_CHECK=`env | grep http | wc -l`

if [[ -x ~/venv/bin/python ]]; then
    echo "Virtual-env has been created already. Updating dependencies!."
    update_dependencies
    exit 0
fi

if [[ $PROXY_CHECK -eq 0 ]]; then
    echo "ERROR: http_proxy and/or https_proxy environment variables are not set. Please set them and re-run the script!"
    usage
fi

# Setup the virtual-env
if [[ -x $VIRTUALENV ]]; then
    VIRTUALENV ~/venv
else
    echo "ERROR: Unable to find the virtualenv command!"
fi

update_dependencies

echo "virtual environment has been setup correctly!"
exit 0