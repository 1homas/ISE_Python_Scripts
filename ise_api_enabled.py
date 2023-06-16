#!/usr/bin/env python3
"""
Enable the ISE APIs using APIs!

Usage:

  ise_api_enabled.py

Requires setting the these environment variables using the `export` command:
  export ISE_HOSTNAME='1.2.3.4'         # hostname or IP address of ISE PAN
  export ISE_REST_USERNAME='admin'      # ISE ERS admin or operator username
  export ISE_REST_PASSWORD='C1sco12345' # ISE ERS admin or operator password
  export ISE_CERT_VERIFY=false          # validate the ISE certificate

You may add these export lines to a text file and load with `source`:
  source ise_environment.sh

"""

import requests
import os
import sys


CONTENT_TYPE_JSON = 'application/json'
CONTENT_TYPE_XML = 'application/xml'


# Silence any warnings about certificates
requests.packages.urllib3.disable_warnings()

# Load Environment Variables
env = { k : v for (k, v) in os.environ.items() }


def ise_open_api_enable () :
    url = 'https://'+env['ISE_HOSTNAME']+'/admin/API/apiService/update'
    data = '{ "papIsEnabled":true, "psnsIsEnabled":true }'
    r = requests.post(url,
                    auth=(env['ISE_REST_USERNAME'], env['ISE_REST_PASSWORD']),
                    data=data,
                    headers={'Content-Type': CONTENT_TYPE_JSON,
                             'Accept': CONTENT_TYPE_JSON},
                    verify=env['ISE_CERT_VERIFY'].lower().startswith('t')
                    )
    if (r.status_code == 200 or r.status_code == 500 ) :
        print("✅ ISE Open APIs Enabled")
    else :
        print("❌ ISE Open APIs Disabled")



def ise_ers_api_enable () :
    url = 'https://'+env['ISE_HOSTNAME']+'/admin/API/NetworkAccessConfig/ERS'
    data = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<ersConfig>
<id>1</id>
<isCSRFCheck>false</isCSRFCheck>
<isPapEnabled>true</isPapEnabled>
<isPsnsEnabled>true</isPsnsEnabled>
</ersConfig>
"""

    r = requests.put(url,
                    auth=(env['ISE_REST_USERNAME'], env['ISE_REST_PASSWORD']),
                    data=data,
                    headers={'Content-Type': CONTENT_TYPE_XML,
                             'Accept': CONTENT_TYPE_XML},
                    verify=env['ISE_CERT_VERIFY'].lower().startswith('t')
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

