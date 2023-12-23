#!/usr/bin/env python3

import os
import requests
import sys

requests.packages.urllib3.disable_warnings() # Silence any requests package warnings about certificates

CONTENT_TYPE_JSON = 'application/json'
CONTENT_TYPE_XML = 'application/xml'
USAGE = """
Enable the ISE APIs using (synchronous) APIs!

Usage:

  ise_api_enabled.py

Requires setting the these environment variables using the `export` command:
  export ISE_HOSTNAME='1.2.3.4'         # hostname or IP address of ISE PAN
  export ISE_REST_USERNAME='admin'      # ISE ERS admin or operator username
  export ISE_REST_PASSWORD='C1sco12345' # ISE ERS admin or operator password
  export ISE_CERT_VERIFY=false          # validate the ISE certificate

You may add these `export` lines to a text file, customize them, and load with `source`:
  source ise_environment.sh

"""

def ise_open_api_enable (session:requests.Session=None) :
    url = 'https://'+env['ISE_HOSTNAME']+'/admin/API/apiService/update'
    data = '{ "papIsEnabled":true, "psnsIsEnabled":true }'
    r = session.post(url,
                    auth=(env['ISE_REST_USERNAME'], env['ISE_REST_PASSWORD']),
                    data=data,
                    headers={'Content-Type': CONTENT_TYPE_JSON, 'Accept': CONTENT_TYPE_JSON},
                    verify=env['ISE_CERT_VERIFY'].lower().startswith('t')
                    )
    if (r.status_code == 200 or r.status_code == 500 ) : # 500 if already enabled
        print("✅ ISE Open APIs Enabled")
    else :
        print("❌ ISE Open APIs Disabled")


def ise_ers_api_enable (session:requests.Session=None) :
    url = 'https://'+env['ISE_HOSTNAME']+'/admin/API/NetworkAccessConfig/ERS'
    data = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<ersConfig>
<id>1</id>
<isCSRFCheck>false</isCSRFCheck>
<isPapEnabled>true</isPapEnabled>
<isPsnsEnabled>true</isPsnsEnabled>
</ersConfig>
"""
    r = session.put(url, data=data, 
                    headers={'Content-Type': CONTENT_TYPE_XML, 'Accept': CONTENT_TYPE_XML},
                    verify=env['ISE_CERT_VERIFY'].lower().startswith('t')
                    )
    print(f"{'✅' if r.ok else '❌'} ISE ERS APIs {'Enabled' if r.ok else 'Disabled'}")


if __name__ == "__main__":
    """
    Entrypoint for local script.
    """
    env = { k : v for (k, v) in os.environ.items() } # Load Environment Variables

    with requests.Session() as session:
      session = requests.Session()
      session.auth = auth=( env['ISE_REST_USERNAME'], env['ISE_REST_PASSWORD'] )
      session.headers.update({'Content-Type': CONTENT_TYPE_JSON, 'Accept': CONTENT_TYPE_JSON})

      ise_open_api_enable(session)
      ise_ers_api_enable(session)

    sys.exit(0) # 0 is ok

