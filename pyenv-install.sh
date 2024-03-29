#!/bin/bash

python3 -m ensurepip --upgrade
python3 -m pip install --upgrade pipenv # get the pipev virtual development environment
pipenv install python@3.11              # create your virtual development environment
pipenv install -r requirements.txt      # install required packages into enviroment
