#!/usr/bin/env python
"""
A simple, single GET request for an ISE ERS resource. 
See https://cs.co/ise-api for REST API resource names.

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

HEADERS_JSON = { 'Accept': 'application/json' }
USAGE = """
Usage: 
  ise_get_ers_raw.py {resource}

Examples:
  ise_get_ers_raw.py networkdevice
  ise_get_ers_raw.py networkdevice/0b6e9500-8b4a-11ec-ac96-46ca1867e58d
  ise_get_ers_raw.py networkdevicegroup
  ise_get_ers_raw.py identitygroup
  ise_get_ers_raw.py op/systemconfig/iseversion
"""

# Validate command line arguments
if len(sys.argv) < 2 : 
    print(USAGE)
    sys.exit(1)

resource_name = sys.argv[1]

#
# Load Environment Variables
#
env = { k : v for (k, v) in os.environ.items() }
hostname = env['ise_rest_hostname']
username = env['ise_rest_username']
password = env['ise_rest_password']
verify = False if env['ise_verify'][0].lower() in ['f','n'] else True


#
# Show the resource
#
url = 'https://'+hostname+'/ers/config/'+resource_name
r = requests.get(url, auth=(username, password), headers=HEADERS_JSON, verify=verify)

if r.status_code == 401 :
    print(r.status_code, file=sys.stderr)
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
