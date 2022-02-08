#!/usr/bin/env python
"""
Get the ISE node version information.

Usage: ise_version.py

Requires the following environment variables:
  - ise_rest_hostname : the hostname or IP address of your ISE PAN node
  - ise_rest_username : the ISE ERS admin or operator username
  - ise_rest_password : the ISE ERS admin or operator password
  - ise_verify : validate the ISE certificate (true/false)

Set the environment variables using the `export` command:
  export ise_rest_hostname='1.2.3.4'
  export ise_rest_username='admin'
  export ise_rest_password='C1sco12345'
  export ise_verify=false

You may save the export lines in a text file and source it for use:
  source ise_environment.sh

"""

import requests
import json
import os
import sys

# Silence any warnings about certificates
requests.packages.urllib3.disable_warnings()

# Load Environment Variables
env = { k : v for (k, v) in os.environ.items() }

url = 'https://'+env['ise_rest_hostname']+'/ers/config/op/systemconfig/iseversion'
r = requests.get(url,
                 auth=(env['ise_rest_username'], env['ise_rest_password']),
                 headers={'Accept': 'application/json'},
                 verify=env['ise_verify'].lower().startswith('t')
                )

# Sample output:
#
# {
#   "OperationResult" : {
#     "resultValue" : [ {
#       "value" : "3.1.0.518",
#       "name" : "version"
#     }, {
#       "value" : "1",
#       "name" : "patch information"
#     } ]
#   }
# }
# 

values = r.json()['OperationResult']['resultValue']
version_info = {}
for item in values :
    version_info[item['name']] = item['value']

# Rename patch key
version_info['patch'] = version_info['patch information']
del version_info['patch information']

# Split version into sequence identifiers
(version_info['major'], 
 version_info['minor'], 
 version_info['maintenance'], 
 version_info['build']
 ) = version_info['version'].split('.')

print(json.dumps(version_info, indent=2))

