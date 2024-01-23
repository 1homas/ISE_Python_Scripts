#!/usr/bin/env python3
"""
Get the ISE node version information.

Usage: ise_version.py

Requires setting the these environment variables using the `export` command:
  export ISE_HOSTNAME='1.2.3.4'         # hostname or IP address of ISE PAN
  export ISE_REST_USERNAME='admin'      # ISE ERS admin or operator username
  export ISE_REST_PASSWORD='C1sco12345' # ISE ERS admin or operator password
  export ISE_CERT_VERIFY=false          # validate the ISE certificate

You may save the export lines in a text file and source it for use:
  source ise_environment.sh

"""

import requests
import json
import os
import sys

requests.packages.urllib3.disable_warnings() # Silence any warnings about certificates

env = { k:v for (k, v) in os.environ.items() } # Load Environment Variables
url = 'https://'+env['ISE_HOSTNAME']+'/ers/config/op/systemconfig/iseversion'
basic_auth = (env['ISE_REST_USERNAME'], env['ISE_REST_PASSWORD'])
json_headers = {'Accept': 'application/json'}
ssl_verify = False if env['ISE_CERT_VERIFY'][0:1].lower() in ['f','n'] else True
r = requests.get(url, auth=basic_auth, headers=json_headers, verify=ssl_verify)

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
for item in values:
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

