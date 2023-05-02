#!/bin/bash

VENV=.venv
PACKAGE_NAME=stalled-cleaner
PYTHON=python3.9

source "${VENV}/bin/activate"
${PYTHON} -m "${PACKAGE_NAME}.main"
deactivate
