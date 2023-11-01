#!/usr/bin/env python3
"""
Enable the ISE APIs
Author: Thomas Howard, thomas@cisco.com

Usage:

  ise_api_enabled_aio.py

Requires setting the these environment variables using the `export` command:
  export ISE_HOSTNAME='1.2.3.4'         # hostname or IP address of ISE PAN
  export ISE_REST_USERNAME='admin'      # ISE ERS admin or operator username
  export ISE_REST_PASSWORD='C1sco12345' # ISE ERS admin or operator password
  export ISE_CERT_VERIFY=false          # validate the ISE certificate

You may add these export lines to a text file and load with `source`:
  source ise_environment.sh

"""

import asyncio
import aiohttp
import os
from time import time
import sys


CONTENT_TYPE_JSON = 'application/json'
CONTENT_TYPE_XML = 'application/xml'

#
# ISE ERS Connection Limits (see https://cs.co/ise-scale)
#   ISE 2.4: 10 
#   ISE 2.6: 30
#
TCP_CONNECTIONS_MAX = 30
TCP_CONNECTIONS_DEFAULT = 10

ENV = { k : v for (k, v) in os.environ.items() if k.startswith('ISE_') }


async def ise_open_api_enable () :
    url = f"https://{ENV['ISE_HOSTNAME']}/admin/API/apiService/update"
    data = '{ "papIsEnabled":true, "psnsIsEnabled":true }'

    auth = aiohttp.BasicAuth(login=ENV['ISE_REST_USERNAME'], password=ENV['ISE_REST_PASSWORD'], encoding='utf-8')
    connector = aiohttp.TCPConnector(limit=TCP_CONNECTIONS_DEFAULT, ssl=False)

    session = aiohttp.ClientSession(auth=auth, connector=connector)
    session.headers['Content-Type'] = CONTENT_TYPE_JSON
    session.headers['Accept'] = CONTENT_TYPE_JSON

    async with session.post(url, data=data) as response :
        # print(response.status)
        # print(await response.text())
        if (response.status == 200 or response.status == 500 ) :
            print("✅ ISE Open APIs Enabled")
    await session.close()


async def ise_ers_api_enable () :
    url = f"https://{ENV['ISE_HOSTNAME']}/admin/API/NetworkAccessConfig/ERS"
    data = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<ersConfig>
<id>1</id>
<isCSRFCheck>false</isCSRFCheck>
<isPapEnabled>true</isPapEnabled>
<isPsnsEnabled>true</isPsnsEnabled>
</ersConfig>
"""

    auth = aiohttp.BasicAuth(login=ENV['ISE_REST_USERNAME'], password=ENV['ISE_REST_PASSWORD'], encoding='utf-8')
    connector = aiohttp.TCPConnector(limit=TCP_CONNECTIONS_DEFAULT, ssl=False)

    session = aiohttp.ClientSession(auth=auth, connector=connector)
    session.headers['Content-Type'] = CONTENT_TYPE_XML
    session.headers['Accept'] = CONTENT_TYPE_XML

    async with session.put(url, data=data) as response :
        if (response.status == 200) :
            print("✅ ISE ERS APIs Enabled")
    await session.close()



async def main():

    await ise_open_api_enable()
    await ise_ers_api_enable()


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()

sys.exit(0) # 0 is ok

