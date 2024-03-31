#!/usr/bin/env python3
"""
Enable the ISE APIs using (synchronous) APIs.

Usage:

  ise-api-enabled.py

Requires setting the these environment variables using the `export` command:
  export ISE_PPAN='1.2.3.4'             # hostname or IP address of ISE Primary PAN
  export ISE_REST_USERNAME='admin'      # ISE ERS admin or operator username
  export ISE_REST_PASSWORD='C1sco12345' # ISE ERS admin or operator password
  export ISE_CERT_VERIFY=false          # validate the ISE certificate

You may add these export lines to a text file and load with `source`:
  source env.sh

"""
__author__ = "Thomas Howard"
__email__ = "thomas@cisco.com"
__license__ = "MIT - https://mit-license.org/"

import os
import requests
import sys

requests.packages.urllib3.disable_warnings() # Silence any requests package warnings about certificates


def ise_open_api_enable (session:requests.Session=None, ssl_verify:bool=True) :
    url = 'https://'+env['ISE_PPAN']+'/admin/API/apiService/update'
    data = '{ "papIsEnabled":true, "psnsIsEnabled":true }'
    r = session.post(url, data=data, verify=ssl_verify)
    if (r.status_code == 200 or r.status_code == 500 ) : # 500 if already enabled
        print(f"✅ {r.status_code} ISE Open APIs Enabled")
    else :
        print(f"❌ {r.status_code} ISE Open APIs Disabled")


def ise_ers_api_enable (session:requests.Session=None, ssl_verify:bool=True) :
    url = 'https://'+env['ISE_PPAN']+'/admin/API/NetworkAccessConfig/ERS'
    data = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<ersConfig>
<id>1</id>
<isCSRFCheck>false</isCSRFCheck>
<isPapEnabled>true</isPapEnabled>
<isPsnsEnabled>true</isPsnsEnabled>
</ersConfig>
"""
    r = session.put(url, data=data, headers={'Content-Type': 'application/xml', 'Accept': 'application/xml'}, verify=ssl_verify)
    print(f"{'✅' if r.ok else '❌'} {r.status_code} ISE ERS APIs {'Enabled' if r.ok else 'Disabled'}")


if __name__ == "__main__":
    """
    Entrypoint for local script.
    """
    env = { k : v for (k,v) in os.environ.items() } # Load environment variables
    ssl_verify = False if env['ISE_CERT_VERIFY'][0:1].lower() in ['f','n'] else True

    with requests.Session() as session:
      session = requests.Session()
      session.auth = ( env['ISE_REST_USERNAME'], env['ISE_REST_PASSWORD'] )
      session.headers.update({'Content-Type': 'application/json', 'Accept': 'application/json'})

      ise_open_api_enable(session, ssl_verify)
      ise_ers_api_enable(session, ssl_verify)

    sys.exit(0) # 0 is ok

