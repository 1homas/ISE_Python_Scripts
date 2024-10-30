#!/usr/bin/env python3
"""
A simple, single GET request for an ISE ERS resource. 
See https://cs.co/ise-api for REST API resource names.

Usage: 
  ise-get-ers-raw.py {resource}

Examples:
  ise-get-ers-raw.py networkdevice
  ise-get-ers-raw.py networkdevice/0b6e9500-8b4a-11ec-ac96-46ca1867e58d
  ise-get-ers-raw.py networkdevicegroup
  ise-get-ers-raw.py identitygroup
  ise-get-ers-raw.py op/systemconfig/iseversion

Requires setting the these environment variables using the `export` command:
  export ISE_PPAN='1.2.3.4'             # hostname or IP address of ISE Primary PAN
  export ISE_REST_USERNAME='admin'      # ISE ERS admin or operator username
  export ISE_REST_PASSWORD='C1sco12345' # ISE ERS admin or operator password
  export ISE_CERT_VERIFY=false          # validate the ISE certificate

You may add these export lines to a text file and load with `source`:
  source ise.sh

"""
__author__ = "Thomas Howard"
__email__ = "thomas@cisco.com"
__license__ = "MIT - https://mit-license.org/"

import requests
import json
import os
import sys

requests.packages.urllib3.disable_warnings()  # Silence any warnings about certificates

HEADERS_JSON = {"Accept": "application/json"}

# Validate command line arguments
if len(sys.argv) < 2:
    print(USAGE)
    sys.exit(1)

resource_name = sys.argv[1]

#
# Load Environment Variables
#
env = {k: v for (k, v) in os.environ.items()}

#
# Show the resource
#
url = f"https://{env['ISE_PPAN']}/ers/config/{resource_name}"
r = requests.get(
    url,
    auth=(env["ISE_REST_USERNAME"], env["ISE_REST_PASSWORD"]),
    headers=HEADERS_JSON,
    verify=(False if env["ISE_CERT_VERIFY"][0].lower() in ["f", "n"] else True),
)

if r.status_code == 401:
    print(r.status_code, file=sys.stderr)
    print(USAGE, file=sys.stderr)
    print(r.json())
else:
    print(json.dumps(r.json(), indent=2))
