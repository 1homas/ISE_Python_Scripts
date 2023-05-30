#!/usr/bin/env python3
"""
Enable the ISE APIs
Author: Thomas Howard, thomas@cisco.com

Usage:

  ise_enable_apis.py

Requires the following environment variables:
- ise_rest_hostname : the hostname or IP address of your ISE PAN node
- ise_rest_username : the ISE ERS admin or operator username
- ise_rest_password : the ISE ERS admin or operator password
- ise_verify : validate the ISE certificate (true/false)

"""

import asyncio
import aiohttp
import os
from time import time
import sys



CONTENT_TYPE_JSON = 'application/json'
CONTENT_TYPE_XML = 'application/xml'

ENV_VARS = {
    'ise_rest_hostname': 'the hostname or IP address of your ISE PAN node',
    'ise_rest_username': 'the ISE ERS admin or operator username',
    'ise_rest_password': 'the ISE ERS admin or operator password',
    'ise_verify': 'Validate the ISE certificate (true/false)',
}

#
# ISE ERS Connection Limits (see https://cs.co/ise-scale)
#   ISE 2.4: 10 
#   ISE 2.6: 30
#
TCP_CONNECTIONS_MAX = 30
TCP_CONNECTIONS_DEFAULT = 10

env_cfg = { k : v for (k, v) in os.environ.items() if k.startswith('ise_') }

hostname = env_cfg['ise_rest_hostname']
username = env_cfg['ise_rest_username']
password = env_cfg['ise_rest_password']
verify = env_cfg['ise_verify']




async def ise_open_api_enable () :
    url = 'https://'+hostname+'/admin/API/apiService/update'
    data = '{ "papIsEnabled":true, "psnsIsEnabled":true }'

    auth = aiohttp.BasicAuth(login=username, password=password, encoding='utf-8')
    connector = aiohttp.TCPConnector(
        limit=TCP_CONNECTIONS_DEFAULT,
        ssl=(False if verify else None),
    )

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
    url = 'https://'+hostname+'/admin/API/NetworkAccessConfig/ERS'
    data = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<ersConfig>
<id>1</id>
<isCSRFCheck>false</isCSRFCheck>
<isPapEnabled>true</isPapEnabled>
<isPsnsEnabled>true</isPsnsEnabled>
</ersConfig>
"""

    auth = aiohttp.BasicAuth(login=username, password=password, encoding='utf-8')
    connector = aiohttp.TCPConnector(
        limit=TCP_CONNECTIONS_DEFAULT,
        ssl=(False if verify else None),
    )

    session = aiohttp.ClientSession(auth=auth, connector=connector)
    session.headers['Content-Type'] = CONTENT_TYPE_XML
    session.headers['Accept'] = CONTENT_TYPE_XML

    async with session.put(url, data=data) as response :
        # print(response.status)
        # print(await response.text())
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

