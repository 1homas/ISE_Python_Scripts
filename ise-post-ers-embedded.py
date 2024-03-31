#!/usr/bin/env python3
"""

A simple POST request for an ISE ERS resource. 
See https://cs.co/ise-api for REST API resource names.

Usage:
  ise-post-ers-embedded.py {resource_name} {resource.json}

Requires setting the these environment variables using the `export` command:
  export ISE_HOSTNAME='1.2.3.4'         # hostname or IP address of ISE PAN
  export ISE_REST_USERNAME='admin'      # ISE ERS admin or operator username
  export ISE_REST_PASSWORD='C1sco12345' # ISE ERS admin or operator password
  export ISE_CERT_VERIFY=false          # validate the ISE certificate

You may add these export lines to a text file and load with `source`:
  source ise-env.sh

"""
__author__ = "Thomas Howard"
__email__ = "thomas@cisco.com"
__license__ = "MIT - https://mit-license.org/"


import requests
import json
import os
import sys

# Silence any warnings about certificates
requests.packages.urllib3.disable_warnings()

HEADERS_JSON = { 'Accept': 'application/json',
                 'Content-Type': 'application/json' }
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
      "radiusSharedSecret": "ISEisC00L",
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
# Load Environment Variables
#
env = { k : v for (k, v) in os.environ.items() }

#
# POST the resource
#
url = 'https://'+env['ISE_HOSTNAME']+'/ers/config/'+resource_name
r = requests.post(url,
                  auth=(env['ISE_REST_USERNAME'], env['ISE_REST_PASSWORD']),
                  headers=HEADERS_JSON,
                  data=payload,
                  verify=(False if env['ISE_CERT_VERIFY'][0].lower() in ['f','n'] else True)
                 )
print(r.status_code)

if r.status_code == 201 :
    print(f'✅ View your new {resource_name}\n   {r.headers["Location"]}')
elif r.status_code == 401 :
    print('Verify you have set the environment variables and your credentials are correct', file=sys.stderr)
    print(r.json())
else :
    print(json.dumps(r.json(), indent=2))
