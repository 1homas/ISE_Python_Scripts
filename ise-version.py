#!/usr/bin/env python3
"""
Get the ISE node version information.

Usage: ise-version.py

Requires setting the these environment variables using the `export` command:
  export ISE_PPAN='1.2.3.4'             # hostname or IP address of ISE Primary PAN
  export ISE_REST_USERNAME='admin'      # ISE ERS admin or operator username
  export ISE_REST_PASSWORD='C1sco12345' # ISE ERS admin or operator password
  export ISE_CERT_VERIFY=false          # validate the ISE certificate

You may add these export lines to a text file and load with `source`:
  source ise-env.sh

"""
__author__ = "Thomas Howard"
__email__ = "thomas@cisco.com"
__license__ = "MIT - https://mit-license.org/"


import json
import os
import requests
import sys

requests.packages.urllib3.disable_warnings() # Silence any warnings about certificates

env = { k:v for (k, v) in os.environ.items() } # Load Environment Variables

with requests.Session() as session:
    # Initialize ISE REST API Session
    session.auth = ( env['ISE_REST_USERNAME'], env['ISE_REST_PASSWORD'] )
    session.headers.update({'Accept': 'application/json'})
    session.verify = False if env['ISE_CERT_VERIFY'][0:1].lower() in ['f','n'] else True

    url = f"https://{env['ISE_PPAN']}/ers/config/op/systemconfig/iseversion"
    r = session.get(url)

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
version_info['semver'] = f"{version_info['major']}.{version_info['minor']}.{version_info['patch']}"

print(json.dumps(version_info, indent=2))

