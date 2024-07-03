#!/bin/bash

#
# Script to install all the needed dependencies package for Linux
# usage:execute on terminal "./install_pip_user_dependencies.sh"
#

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
# index url and trusted host to be used for pip install
index_url=https://artifactory.geo.conti.de/artifactory/api/pypi/c_adas_cip_pypi_v/simple
trusted_host_url=artifactory.geo.conti.de
pip3 install -i $index_url --trusted-host $trusted_host_url --upgrade pip setuptools wheel pipenv
pip3 install -i $index_url --trusted-host $trusted_host_url -r "${DIR}/install_scripts/dependencies_user.txt"

if [ -n "$JENKINS_URL" ]; then
  echo "Running in jenkins therefore skip qt dependency library installation as qt is not required in jenkins"
else
  echo "Not running in jenkins therefore install qt dependency library as its required on local setup"
  # to work Qt the dependency library ''libxcb-xinerama0'' must be installed
  sudo apt-get update
  sudo apt-get install libxcb-xinerama0
fi
echo "All Modules installed successfully"
