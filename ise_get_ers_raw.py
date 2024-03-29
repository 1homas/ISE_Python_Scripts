#!/usr/bin/env python
"""
A simple, single GET request for an ISE ERS resource. 
See https://cs.co/ise-api for REST API resource names.

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

#
# Show the resource
#
url = f"https://{env['ISE_HOSTNAME']}/ers/config/{resource_name}"
r = requests.get(url, 
                 auth=(env['ISE_REST_USERNAME'], env['ISE_REST_PASSWORD']),
                 headers=HEADERS_JSON,
                 verify=(False if env['ISE_CERT_VERIFY'][0].lower() in ['f','n'] else True)
                 )

if r.status_code == 401 :
    print(r.status_code, file=sys.stderr)
    print(USAGE, file=sys.stderr)
    print(r.json())
else :
    print(json.dumps(r.json(), indent=2))
