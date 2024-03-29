#!/usr/bin/env python
"""
A simple POST request for an ISE ERS resource. 
See https://cs.co/ise-api for REST API resource names.

Usage: 
  ise_post_ers_from_file.py {resource_name} {resource_file.json}
  ise_post_ers_from_file.py networkdevice my_network_device.json

Requires setting the these environment variables using the `export` command:
  export ISE_HOSTNAME='1.2.3.4'         # hostname or IP address of ISE PAN
  export ISE_REST_USERNAME='admin'      # ISE ERS admin or operator username
  export ISE_REST_PASSWORD='C1sco12345' # ISE ERS admin or operator password
  export ISE_CERT_VERIFY=false          # validate the ISE certificate

You may add these export lines to a text file and load with `source`:
  source ise_environment.sh

"""

import requests
import json
import os
import sys

requests.packages.urllib3.disable_warnings() # Silence any warnings about certificates

# Validate command line arguments
if len(sys.argv) < 3 : 
    print(__doc__)
    sys.exit(1)

resource_name = sys.argv[1]
json_filepath = sys.argv[2]

#
# Load the JSON data
# 
json_data = ''
with open(json_filepath) as f: json_data = f.read()
print(json_data)

env = {k:v for (k,v) in os.environ.items() } # Load Environment Variables

#
# POST the resource
#
url = f"https://{env['ISE_HOSTNAME']}/ers/config/{resource_name}"
basic_auth = (env['ISE_REST_USERNAME'], env['ISE_REST_PASSWORD'])
json_headers = { 'Accept': 'application/json', 'Content-Type': 'application/json' }
ssl_verify = False if env['ISE_CERT_VERIFY'][0].lower() in ['f','n'] else True
r = requests.post(url, auth=basic_auth, headers=json_headers, data=json_data, verify=ssl_verify)
print(r.status_code)

if r.status_code == 201 :
    print(f'✅ View your new {resource_name}\n   {r.headers["Location"]}')
elif r.status_code == 401 :
    print(f'X {r.status_code}\n   {json.dumps(r.json(), indent=2)}')
    print(USAGE, file=sys.stderr)
else :
    print(json.dumps(r.json(), indent=2))
