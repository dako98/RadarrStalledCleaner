#!/bin/bash

VENV=.venv
PACKAGE_NAME=stalled-cleaner
PYTHON=python

source "${VENV}/bin/activate"
python -m pytest
deactivate
