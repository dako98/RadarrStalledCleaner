#!/bin/bash

VENV=.venv
PYTHON=python

echo -e "\033[96m--------Building venv--------\033[0m"
${PYTHON} -m venv ${VENV}
source ${VENV}/bin/activate

echo -e "\033[96m--------Upgrading pip--------\033[0m"
${PYTHON} -m pip install pip setuptools --upgrade
pip install -r requirements.txt
pip install -e .

deactivate
echo -e "\033[96m--------Finished building venv--------\033[0m"
