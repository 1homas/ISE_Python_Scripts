#!/usr/bin/env python
"""
A simple POST request for an ISE ERS resource. 
See https://cs.co/ise-api for REST API resource names.

Usage: 
  ise_post_ers_embedded.py {resource_name} {resource.json}

Requires the following environment variables:
  - ise_rest_hostname : the hostname or IP address of your ISE PAN node
  - ise_rest_username : the ISE ERS admin or operator username
  - ise_rest_password : the ISE ERS admin or operator password
  - ise_verify : validate the ISE certificate (true/false)

You may save the export lines in a text file and source it for use:
  source ise_environment.sh

"""

import requests
import json
import os
import sys

# Silence any warnings about certificates
requests.packages.urllib3.disable_warnings()

HEADERS_JSON = { 'Accept': 'application/json',
                 'Content-Type': 'application/json' }
USAGE = """
Usage: 
  ise_post_ers_embedded.py
"""

#
# Load Environment Variables
#
env = { k : v for (k, v) in os.environ.items() }
hostname = env['ise_rest_hostname']
username = env['ise_rest_username']
password = env['ise_rest_password']
verify = False if env['ise_verify'][0].lower() in ['f','n'] else True


# Validate command line arguments
if len(sys.argv) > 1 : 
    print(USAGE)
    sys.exit(1)

#
# Resource Name and Configuration
# Do not include the 'id' or 'link' attributes when doing a POST
#
resource_name = 'networkdevice'
payload = """
{
  "NetworkDevice": {
    "name": "my_network_device",
    "description": "",
    "authenticationSettings": {
      "networkProtocol": "RADIUS",
      "radiusSharedSecret": "C1sco12345",
      "enableKeyWrap": false,
      "dtlsRequired": false,
      "keyEncryptionKey": "",
      "messageAuthenticatorCodeKey": "",
      "keyInputFormat": "ASCII",
      "enableMultiSecret": "false"
    },
    "profileName": "Cisco",
    "coaPort": 1700,
    "NetworkDeviceIPList": [
      {
        "ipaddress": "10.20.30.40",
        "mask": 32
      }
    ],
    "NetworkDeviceGroupList": [
      "Location#All Locations",
      "IPSEC#Is IPSEC Device#No",
      "Device Type#All Device Types"
    ]
  }
}
"""

#
# POST the resource
#
url = 'https://'+hostname+'/ers/config/'+resource_name
r = requests.post(url,
                  auth=(username, password),
                  headers=HEADERS_JSON,
                  data=payload,
                  verify=verify
                 )
print(r.status_code)

if r.status_code == 201 :
    print(f'✅ View your new {resource_name}\n   {r.headers["Location"]}')
elif r.status_code == 401 :
    print("""
Verify you have set the environment variables and your credentials are correct:
  export ise_rest_hostname='1.2.3.4'
  export ise_rest_username='admin'
  export ise_rest_password='C1sco12345'
  export ise_verify=false
""", file=sys.stderr)
    print(r.json())
else :
    print(json.dumps(r.json(), indent=2))
