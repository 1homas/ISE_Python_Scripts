#!/usr/bin/env python3
"""

Generates the specified number of randomly named ISE downloadable ACLs using a REST API.

Usage:

  ise-post-dacls.py -h
  ise-post-dacls.py 5

Requires setting the these environment variables using the `export` command:
  export ISE_PPAN='1.2.3.4'             # hostname or IP address of ISE Primary PAN
  export ISE_REST_USERNAME='admin'      # ISE ERS admin or operator username
  export ISE_REST_PASSWORD='C1sco12345' # ISE ERS admin or operator password
  export ISE_VERIFY=false               # validate the ISE certificate

You may add these export lines to a text file and load with `source`:
  source ise-env.sh

"""
__author__ = "Thomas Howard"
__email__ = "thomas@cisco.com"
__license__ = "MIT - https://mit-license.org/"


import aiohttp
import asyncio
import argparse
import csv
import io
import json
import os
import random
import string

JSON_HEADERS = {"Accept": "application/json", "Content-Type": "application/json"}
REST_PAGE_SIZE_DEFAULT = 20
REST_PAGE_SIZE_MAX = 100
REST_PAGE_SIZE = REST_PAGE_SIZE_MAX

# Limit TCP connection pool size to prevent connection refusals by ISE!
# 30 for ISE 2.6+; See https://cs.co/ise-scale for Concurrent ERS Connections.
# Testing with ISE 3.0 shows *no* performance gain for >5-10
TCP_CONNECTIONS_DEFAULT = 10
TCP_CONNECTIONS_MAX = 30
TCP_CONNECTIONS = 5


def generate_downloadableacl_data():
    """
    Return an internaluser object ready for conversion to JSON.
    {
      "id": "9825aa40-8c01-11e6-996c-525400b48521",
      "name": "DENY_ALL_IPV4_TRAFFIC",
      "description": "Deny all ipv4 traffic",
      "dacl": "deny ip any any",
      "daclType": "IPV4"
    },
    """
    resource = {
        "DownloadableAcl": {
            "name": f"dACL_{''.join(random.choices(string.ascii_letters, k=5))}",
            "description": "Deny all ipv4 traffic",
            "dacl": "deny ip any any",
            "daclType": "IPV4",
        }
    }
    # print(f"resource:{resource}")
    return resource


async def get_resource(session, url):
    async with session.get(url) as resp:
        response = await resp.json()
        return response["SearchResult"]["resources"]


async def cache_existing_internalusers(session):
    """
    Reads existing ISE internalusers and saves them to the username_cache
    so we do not create an existing user.
    """

    rest_endpoint_path = "/ers/config/internaluser"
    response = await session.get(f"{rest_endpoint_path}?size={REST_PAGE_SIZE}")
    if response.status != 200:
        raise ValueError(f"Bad status: {response}")
    json = await response.json()

    resources = json["SearchResult"]["resources"]
    if args.verbose:
        print(f"ⓘ Fetched {len(resources)} resources")

    existing_user_count = json["SearchResult"]["total"]
    if args.verbose:
        print(f"ⓘ Existing ISE Internal Users: {existing_user_count}")

    if existing_user_count > REST_PAGE_SIZE:  # we will need more than one fetch
        pages = int(existing_user_count / REST_PAGE_SIZE) + (1 if existing_user_count % REST_PAGE_SIZE else 0)
        urls = []
        for page in range(1, pages + 1):
            urls.append(f"{rest_endpoint_path}?size={REST_PAGE_SIZE}&page={page}")
        urls.pop(0)  # discard first URL; used for the count above

        tasks = []
        [tasks.append(asyncio.ensure_future(get_resource(session, url))) for url in urls]

        responses = await asyncio.gather(*tasks)
        [resources.extend(response) for response in responses]

    # add users to the cache
    if args.verbose:
        print(f"ⓘ Adding {len(resources)} users to username_cache")
    for resource in resources:
        username_cache[resource["name"]] = 1


async def create_ise_downloadableacls():

    global args  # promote to global scope for use in other functions
    argp = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    argp.add_argument("number", action="store", type=int, default=1, help="users to create")
    argp.add_argument("--verbose", "-v", action="count", default=0, help="Verbosity")
    args = argp.parse_args()

    # Load Environment Variables
    env = {k: v for (k, v) in os.environ.items() if k.startswith("ISE_")}
    if args.verbose >= 4:
        print(f"ⓘ env: {env}")

    # Create HTTP session
    ssl_verify = False if env["ISE_VERIFY"][0:1].lower() in ["f", "n"] else True
    if args.verbose:
        print(f"ⓘ ISE_VERIFY: {ISE_VERIFY} => ssl_verify:{ssl_verify}")
    tcp_conn = aiohttp.TCPConnector(limit=TCP_CONNECTIONS, limit_per_host=TCP_CONNECTIONS, ssl=ssl_verify)
    auth = aiohttp.BasicAuth(login=env["ISE_REST_USERNAME"], password=env["ISE_REST_PASSWORD"])
    base_url = f"https://{env['ISE_PPAN']}"
    session = aiohttp.ClientSession(base_url, auth=auth, connector=tcp_conn, headers=JSON_HEADERS)

    # Generate requested number of dACLs
    dacls = []
    for n in range(1, args.number + 1):
        dacls.append(generate_downloadableacl_data())
    if args.verbose:
        print(f"ⓘ Generated {len(dacls)} dacls")

    # Create the dACLs with asyncio!
    tasks = []
    [tasks.append(asyncio.ensure_future(session.post("/ers/config/downloadableacl", data=json.dumps(dacl)))) for dacl in dacls]
    responses = await asyncio.gather(*tasks)
    if args.verbose:
        print(f"ⓘ Created {len(responses)} responses")

    for n, response in enumerate(responses, start=1):
        if response.status == 201:
            print(f"✔ {n} {response.status} {response.headers['Location']}")
        elif response.status == 401:
            print("Set the environment variables and verify your credentials are correct!")
            print(await response.json())
        else:
            print(f"✖ {n} {response.status} :\n{json.dumps(await response.json(), indent=2)}")

    await session.close()


if __name__ == "__main__":
    """
    Run from script
    """
    asyncio.run(create_ise_downloadableacls())
