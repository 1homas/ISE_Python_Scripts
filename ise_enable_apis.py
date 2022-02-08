#!/usr/bin/env python3
"""
Enable the ISE APIs

Usage:

  ise_enable_apis.py

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
import os
from time import time
import sys


CONTENT_TYPE_JSON = 'application/json'
CONTENT_TYPE_XML = 'application/xml'


# Silence any warnings about certificates
requests.packages.urllib3.disable_warnings()

# Load Environment Variables
env = { k : v for (k, v) in os.environ.items() }


def ise_open_api_enable () :
    url = 'https://'+env['ise_rest_hostname']+'/admin/API/apiService/update'
    data = '{ "papIsEnabled":true, "psnsIsEnabled":true }'
    r = requests.post(url,
                    auth=(env['ise_rest_username'], env['ise_rest_password']),
                    data=data,
                    headers={'Content-Type': CONTENT_TYPE_JSON,
                             'Accept': CONTENT_TYPE_JSON},
                    verify=env['ise_verify'].lower().startswith('t')
                    )
    if (r.status_code == 200 or r.status_code == 500 ) :
        print("✅ ISE Open APIs Enabled")
    else :
        print("❌ ISE Open APIs Disabled")



def ise_ers_api_enable () :
    url = 'https://'+env['ise_rest_hostname']+'/admin/API/NetworkAccessConfig/ERS'
    data = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<ersConfig>
<id>1</id>
<isCSRFCheck>false</isCSRFCheck>
<isPapEnabled>true</isPapEnabled>
<isPsnsEnabled>true</isPsnsEnabled>
</ersConfig>
"""

    r = requests.put(url,
                    auth=(env['ise_rest_username'], env['ise_rest_password']),
                    data=data,
                    headers={'Content-Type': CONTENT_TYPE_XML,
                             'Accept': CONTENT_TYPE_XML},
                    verify=env['ise_verify'].lower().startswith('t')
                    )
    if (r.status_code == 200) :
        print("✅ ISE ERS APIs Enabled")
    else :
        print("❌ ISE ERS APIs Disabled")



if __name__ == "__main__":
    """
    Entrypoint for local script.
    """

    ise_open_api_enable()
    ise_ers_api_enable()

    sys.exit(0) # 0 is ok

