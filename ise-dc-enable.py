#!/usr/bin/env python3
"""
Enable the ISE APIs using (synchronous) APIs!

Usage:

  ise-dc-enable.py

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


import json
import requests
import os
import sys

DATACONNECT_PASSWORD = "#DataC0nnect"
DATACONNECT_PASSWORD_DAYS_DEFAULT = 90
DATACONNECT_PASSWORD_DAYS_MAX = 3650

env = { k : v for (k,v) in os.environ.items() } # Load environment variables
ssl_verify = False if env['ISE_CERT_VERIFY'][0:1].lower() in ['f','n'] else True

with requests.Session() as session:

    # Initialize ISE REST API Session
    session = requests.Session()
    session.auth = ( env['ISE_REST_USERNAME'], env['ISE_REST_PASSWORD'] )
    session.headers.update({'Content-Type': 'application/json', 'Accept': 'application/json'})
    session.verify=ssl_verify

    url = f"https://{env['ISE_PPAN']}/api/v1/mnt/data-connect/details"
    print(f"ⓘ Data Connect Enabled: {session.get(url).ok}")

    # 💡 Must set password BEFORE enabling!
    #    - Password must contain one or more special characters [#$%&*+,-.:;] ⚠ No @ or !
    #    - Password can't be set to one of the earlier 5 password(s)
    url = f"https://{env['ISE_PPAN']}/api/v1/mnt/data-connect/settings/password"
    print(f"ⓘ Data Connect Password: {session.put(url, json={'password':DATACONNECT_PASSWORD}).json()}")

    # Set Password Expiration
    url = f"https://{env['ISE_PPAN']}/api/v1/mnt/data-connect/settings/password/expiry"
    print(f"ⓘ Data Connect Password Expiration: {session.put(url, json={'passwordExpiresInDays':DATACONNECT_PASSWORD_DAYS_MAX}).json()}")

    # Enable ISE DataConnect via API
    url = f"https://{env['ISE_PPAN']}/api/v1/mnt/data-connect/settings/status"
    print(f"ⓘ Data Connect Password: {session.put(url, json={'isEnabled':True}).json()}")

    # Returns the status of the Dataconnect feature.
    # { 
    #     "response": {
    #         "isEnabled": true,
    #         "isPasswordChanged": true,
    #         "passwordExpiresInDays": 45,
    #         "passwordExpiresOn": "15 December 2021 at 18:05 PST"
    #     }
    # }
    url = f"https://{env['ISE_PPAN']}/api/v1/mnt/data-connect/settings"
    print(f"Data Connect Settings: {session.get(url).json()['response']}")

    # Returns the Dataconnect ODBC details - but these don't change.
    # {
    #     "response": {
    #         "hostname": "isenode",
    #         "port": 2484,
    #         "servicename": "cpm10",
    #         "username": "Admin"
    #     }
    # }
    url = f"https://{env['ISE_PPAN']}/api/v1/mnt/data-connect/details"
    print(f"Data Connect Details: {session.get(url).json()['response']}")

sys.exit(0) # 0 is ok
