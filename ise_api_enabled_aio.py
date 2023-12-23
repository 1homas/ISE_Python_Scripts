#!/usr/bin/env python3

import asyncio
import aiohttp
import os
import sys

CONTENT_TYPE_JSON = 'application/json'
CONTENT_TYPE_XML = 'application/xml'
USAGE = """
Enable the ISE APIs using (asynchronous) APIs!

Usage:

  ise_api_enabled_aio.py

Requires setting the these environment variables using the `export` command:
  export ISE_HOSTNAME='1.2.3.4'         # hostname or IP address of ISE PAN
  export ISE_REST_USERNAME='admin'      # ISE ERS admin or operator username
  export ISE_REST_PASSWORD='C1sco12345' # ISE ERS admin or operator password
  export ISE_CERT_VERIFY=false          # validate the ISE certificate

You may add these `export` lines to a text file, customize them, and load with `source`:
  source ise_environment.sh

"""

async def ise_open_api_enable (session:aiohttp.ClientSession=None, ssl:bool=True) :
    """
    """
    url = '/admin/API/apiService/update'
    data = '{ "papIsEnabled":true, "psnsIsEnabled":true }'
    async with session.post(url, data=data, ssl=ssl) as response :
        if response.status == 200 or response.status == 500 :
            print("✅ ISE Open APIs Enabled")


async def ise_ers_api_enable (session:aiohttp.ClientSession=None, ssl:bool=True) :
    """
    """
    url = '/admin/API/NetworkAccessConfig/ERS'
    data = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<ersConfig>
<id>1</id>
<isCSRFCheck>false</isCSRFCheck>
<isPapEnabled>true</isPapEnabled>
<isPsnsEnabled>true</isPsnsEnabled>
</ersConfig>
"""
    async with session.put(url, data=data, headers={'Accept':CONTENT_TYPE_XML, 'Content-Type':CONTENT_TYPE_XML}, ssl=ssl) as response :
        if response.status == 200 or response.status == 500 :
            print("✅ ISE ERS APIs Enabled")
        else :
            print("❌ ISE ERS APIs Disabled")



async def main():
    """
    Entrypoint for packaged script.
    """
    env = { k : v for (k, v) in os.environ.items() if k.startswith('ISE_') }
    ssl_verify = False if env['ISE_CERT_VERIFY'][0:1].lower() in ['f','n'] else True

    auth = aiohttp.BasicAuth(login=env['ISE_REST_USERNAME'], password=env['ISE_REST_PASSWORD'])
    session = aiohttp.ClientSession(f"https://{env['ISE_HOSTNAME']}", auth=auth, headers={'Accept':CONTENT_TYPE_JSON, 'Content-Type':CONTENT_TYPE_JSON})
    await asyncio.gather(
      ise_ers_api_enable(session, ssl_verify),
      ise_open_api_enable(session, ssl_verify),
    )
    await session.close()


if __name__ == "__main__":
    """
    Entrypoint for local script.
    """
    asyncio.run(main())
    sys.exit(0) # 0 is ok
