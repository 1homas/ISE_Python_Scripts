#!/usr/bin/env python
"""
A simple POST request for an ISE ERS resource. 
See https://cs.co/ise-api for REST API resource names.

Usage: 
  ise_post_ers_from_file.py {resource_name} {resource_file.json}

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
  ise_post_ers_from_file.py {resource_name} {resource_file.json}
"""

# Validate command line arguments
if len(sys.argv) < 3 : 
    print(USAGE)
    sys.exit(1)

resource_name = sys.argv[1]
json_filepath = sys.argv[2]

#
# Load Environment Variables
#
env = { k : v for (k, v) in os.environ.items() }
hostname = env['ise_rest_hostname']
username = env['ise_rest_username']
password = env['ise_rest_password']
verify = False if env['ise_verify'][0].lower() in ['f','n'] else True

#
# Load the JSON data
# 
json_data = ''
with open(json_filepath) as f: json_data = f.read()
# print(json_data)

#
# POST the resource
#
url = 'https://'+hostname+'/ers/config/'+resource_name
r = requests.post(url,
                  auth=(username, password),
                  headers=HEADERS_JSON,
                  data=json_data,
                  verify=verify
                 )
print(r.status_code)

if r.status_code == 201 :
    print(f'✅ Get your new {resource_name} at {r.headers["Location"]}')
elif r.status_code == 401 :
    print("""
Verify you have set the environment variables and your credentials are correct:
  export ise_rest_hostname='1.2.3.4'
  export ise_rest_username='admin'
  export ise_rest_password='C1sco12345'
  export ise_verify=false
""", file=sys.stderr)
else :
    print(json.dumps(r.json(), indent=2))
