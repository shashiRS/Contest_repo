#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"

cd ${DIR}/..
pylint --enable=useless-suppression --exit-zero --rcfile=${DIR}/pylint.config --ignore mfile ${PWD}
