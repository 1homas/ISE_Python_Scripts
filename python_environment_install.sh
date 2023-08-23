#!/bin/bash

python3 -m ensurepip --upgrade
python3 -m pip install --upgrade pip # use a virtual development environment
pipenv install
pipenv install -r requirements.txt  # install required Python packages
