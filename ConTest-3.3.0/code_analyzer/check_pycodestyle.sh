#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"

pycodestyle --exclude venv,mfile,design_files,resource_rc.py  --config=${DIR}/pep8.config `realpath ${DIR}/..`
