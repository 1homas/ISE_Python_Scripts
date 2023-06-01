#!/usr/bin/env python
"""
A simple POST request for an ISE ERS resource. 
See https://cs.co/ise-api for REST API resource names.

Usage: 
  ise_post_ers_from_file.py {resource_name} {resource_file.json}

Requires the following environment variables:
  - ISE_HOSTNAME : the hostname or IP address of your ISE PAN node
  - ISE_REST_USERNAME : the ISE ERS admin or operator username
  - ISE_REST_PASSWORD : the ISE ERS admin or operator password
  - ISE_CERT_VERIFY : validate the ISE certificate (true/false)

Set the environment variables using the `export` command:
  export ISE_HOSTNAME='1.2.3.4'
  export ISE_REST_USERNAME='admin'
  export ISE_REST_PASSWORD='C1sco12345'
  export ISE_CERT_VERIFY=false

You may `source` the export lines from a text file for use:
  source ise.sh
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
hostname = env['ISE_HOSTNAME']
username = env['ISE_REST_USERNAME']
password = env['ISE_REST_PASSWORD']
verify = False if env['ISE_CERT_VERIFY'][0].lower() in ['f','n'] else True

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
    print(f'✅ View your new {resource_name}\n   {r.headers["Location"]}')
elif r.status_code == 401 :
    print("""
Verify you have set the environment variables and your credentials are correct:
  export ISE_HOSTNAME='1.2.3.4'
  export ISE_REST_USERNAME='admin'
  export ISE_REST_PASSWORD='C1sco12345'
  export ISE_CERT_VERIFY=false
""", file=sys.stderr)
else :
    print(json.dumps(r.json(), indent=2))
