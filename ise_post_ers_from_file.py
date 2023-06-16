#!/usr/bin/env python
USAGE = """
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

# Silence any warnings about certificates
requests.packages.urllib3.disable_warnings()

HEADERS_JSON = { 'Accept': 'application/json',
                 'Content-Type': 'application/json' }

# Validate command line arguments
if len(sys.argv) < 3 : 
    print(USAGE)
    sys.exit(1)

resource_name = sys.argv[1]
json_filepath = sys.argv[2]

#
# Load Environment Variables
#
ENV = { k : v for (k, v) in os.environ.items() }

#
# Load the JSON data
# 
json_data = ''
with open(json_filepath) as f: json_data = f.read()
print(json_data)

#
# POST the resource
#
url = f"https://{ENV['ISE_HOSTNAME']}/ers/config/{resource_name}"
r = requests.post(url,
                  auth=(ENV['ISE_REST_USERNAME'], ENV['ISE_REST_PASSWORD']),
                  headers=HEADERS_JSON,
                  data=json_data,
                  verify=(False if ENV['ISE_CERT_VERIFY'][0].lower() in ['f','n'] else True)
                 )
print(r.status_code)

if r.status_code == 201 :
    print(f'✅ View your new {resource_name}\n   {r.headers["Location"]}')
elif r.status_code == 401 :
    print(f'X {r.status_code}\n   {json.dumps(r.json(), indent=2)}')
    print(USAGE, file=sys.stderr)
else :
    print(json.dumps(r.json(), indent=2))
