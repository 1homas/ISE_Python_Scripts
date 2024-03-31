#!/usr/bin/env python3
"""
Generate the specified number of random ISE endpoint resources using REST APIs.

Examples:
  ise-post-endpoints.py -h
  ise-post-endpoints.py
  ise-post-endpoints.py -n 10
  ise-post-endpoints.py -n 100 -v

Requires setting the these environment variables using the `export` command:
  export ISE_HOSTNAME='1.2.3.4'         # hostname or IP address of ISE PAN
  export ISE_REST_USERNAME='admin'      # ISE ERS admin or operator username
  export ISE_REST_PASSWORD='C1sco12345' # ISE ERS admin or operator password
  export ISE_CERT_VERIFY=false          # validate the ISE certificate

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
from faker import Faker     # generate fake endpoints, MACs, IPs

JSON_HEADERS = {'Accept':'application/json', 'Content-Type':'application/json'}
REST_PAGE_SIZE_DEFAULT=20
REST_PAGE_SIZE_MAX=100
REST_PAGE_SIZE=REST_PAGE_SIZE_MAX

# Limit TCP connection pool size to prevent connection refusals by ISE!
# 30 for ISE 2.6+; See https://cs.co/ise-scale for Concurrent ERS Connections.
# Testing with ISE 3.0 shows *no* performance gain for >5-10
TCP_CONNECTIONS_DEFAULT=10
TCP_CONNECTIONS_MAX=30
TCP_CONNECTIONS=5

ENDPOINT_GROUP_UNKNOWN = "aa0e8b20-8bff-11e6-996c-525400b48521"

# ISE Context Visibility > Export columns
# ⚠ Note that ISE does not include custom endpoint attributes!
ISE_CV_DEFAULT_ENDPOINT_EXPORT_COLUMNS = [
    'MACAddress',
    'EndPointPolicy',
    'IdentityGroup',
    'Description',
    'DeviceRegistrationStatus',
    'BYODRegistration',
    'Device Type',
    'EmailAddress',
    'ip',
    'FirstName',
    'host-name',
    'LastName',
    'MDMServerID',
    'MDMServerName',
    'MDMEnrolled',
    'Location',
    'PortalUser',
    'User-Name',
    'StaticAssignment',
    'StaticGroupAssignment',
    'MDMOSVersion',
    'PortalUser.FirstName',
    'PortalUser.LastName',
    'PortalUser.EmailAddress',
    'PortalUser.PhoneNumber',
    'PortalUser.GuestType',
    'PortalUser.GuestStatus',
    'PortalUser.Location',
    'PortalUser.GuestSponsor',
    'PortalUser.CreationType',
    'AUPAccepted',
]


faker = Faker('en-US')    # fake data generator
mac_cache = {}       # MAC cache to ensure uniqueness


def get_random_mac () :
    """
    Returns a unique MAC address.
    """
    n = 1
    mac = faker.mac_address().upper()
    while (mac in mac_cache) :
        mac = faker.mac_address().upper()
    mac_cache[mac] = 1    # cache it
    return mac


def generate_random_endpoint_data () :
    """
    Return an endpoint object ready for conversion to JSON.
    """
    mac = get_random_mac()
    endpoint_group = ENDPOINT_GROUP_UNKNOWN
    resource = {
        'ERSEndPoint' : {
            'name' : mac,
            'mac'  : mac,
            'description' : '', # faker.sentence(nb_words=8), # optional
            'groupId' : 'aa0e8b20-8bff-11e6-996c-525400b48521', # Unknown Endpoint Identity Group
            'staticGroupAssignment'          : False,
            'staticGroupAssignmentDefined'   : False,  # optional
            'profileId' : '',                # optional
            'staticProfileAssignment'        : False,
            'staticProfileAssignmentDefined' : False,  # optional
            # 'portalUser' : '',        # optional
            # 'identityStore' : '',     # optional
            # 'identityStoreId' : '',   # optional
            'customAttributes' : {    # optional
                'customAttributes' : { }
            },
            # 'mdmAttributes' : { },    # optional
        }
    }
    return resource


async def get_resource (session, url) :
    async with session.get(url) as resp:
        response = await resp.json()
        return response['SearchResult']['resources']


async def cache_existing_endpoints (session) :
    """
    Reads existing ISE endpoints and saves them to the mac_cache 
    so we do not attempt to create an existing endpoint.
    """

    rest_endpoint_path = '/ers/config/endpoint'
    response = await session.get(f"{rest_endpoint_path}?size={REST_PAGE_SIZE}")
    if response.status != 200:
        raise ValueError(f'Bad status: {response}')
    json = await response.json()

    resources = json['SearchResult']['resources']
    if args.verbose : print(f"ⓘ Fetched {len(resources)} resources")

    existing_endpoint_count = json['SearchResult']['total']
    if args.verbose : print(f"ⓘ Existing ISE Internal endpoints: {existing_endpoint_count}")

    # Determine number of pages needed to get all existing resources
    if existing_endpoint_count > REST_PAGE_SIZE :  # we will need more than one fetch
        pages = int(existing_endpoint_count / REST_PAGE_SIZE) + (1 if existing_endpoint_count % REST_PAGE_SIZE else 0)
        urls = []
        for page in range(1, pages + 1):
            urls.append(f"{rest_endpoint_path}?size={REST_PAGE_SIZE}&page={page}")
        urls.pop(0)  # discard first URL; already used for the count above

        # Get all the pages using asyncio
        tasks = []
        [ tasks.append(asyncio.ensure_future(get_resource(session, url))) for url in urls ]
        responses = await asyncio.gather(*tasks)
        [ resources.extend(response) for response in responses ]

    # Add endpoints to the cache
    if args.verbose : print(f"ⓘ Adding {len(resources)} endpoints to mac_cache")
    for resource in resources :
        mac_cache[resource['name']] = 1


async def parse_cli_arguments () :
    """
    Returns the parsed command line arguments.
    """
    ARGS = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ARGS.add_argument('number', action='store', type=int, default=1, help='Number of endpoints to create',)
    ARGS.add_argument('--verbose', '-v', action='count', default=0, help='Verbosity',)
    return ARGS.parse_args()


async def create_ise_endpoints () :

    global args     # promote to global scope for use in other functions
    args = await parse_cli_arguments()
    if args.verbose >= 3 : print(f"ⓘ Args: {args}")
    if args.verbose : print(f"ⓘ TCP_CONNECTIONS: {TCP_CONNECTIONS}")
    if args.verbose : print(f"ⓘ REST_PAGE_SIZE: {REST_PAGE_SIZE}")

    # Load Environment Variables
    env = { k : v for (k, v) in os.environ.items() if k.startswith('ISE_') }
    if args.verbose >= 4 : print(f"ⓘ env: {env}")

    # Create HTTP session
    ssl_verify = (False if env['ISE_CERT_VERIFY'][0:1].lower() in ['f','n'] else True)
    tcp_conn = aiohttp.TCPConnector(limit=TCP_CONNECTIONS, limit_per_host=TCP_CONNECTIONS, ssl=ssl_verify)
    auth = aiohttp.BasicAuth(login=env['ISE_REST_USERNAME'], password=env['ISE_REST_PASSWORD'])
    base_url = f"https://{env['ISE_HOSTNAME']}"
    session = aiohttp.ClientSession(base_url, auth=auth, connector=tcp_conn, headers=JSON_HEADERS)

    # Cache existing ISE endpoints to prevent duplicates and HTTP 400 errors 
    await asyncio.wait_for(cache_existing_endpoints(session), 60)
    if args.verbose : print(f"ⓘ mac_cache size: {len(mac_cache)}")

    # Generate requested number of endpoints
    endpoints = []
    for n in range(1, args.number + 1) :
        endpoints.append( generate_random_endpoint_data() )
    if args.verbose : print(f"ⓘ Generated {len(endpoints)} endpoints")

    # Create the endpoints with asyncio!
    tasks = []
    [ tasks.append(asyncio.ensure_future(session.post('/ers/config/endpoint', data=json.dumps(endpoint)))) for endpoint in endpoints ]
    responses = await asyncio.gather(*tasks)    # wait for all tasks to complete
    if args.verbose : print(f"ⓘ Created {len(responses)} responses")
    
    for n,response in enumerate(responses, start=1) :
        if response.status == 201 :
            print(f"✔ {n} {response.status} {response.headers['Location']}")
        elif response.status == 401 :
            print("Set the environment variables and verify your credentials are correct!")
            print(await response.json())
        else :
            print(f"✖ {n} {response.status} :\n{json.dumps(await response.json(), indent=2)}")

    await session.close()


def main ():
    """
    Entrypoint for packaged script.
    """
    asyncio.run(create_ise_endpoints())


if __name__ == '__main__':
    """
    Entrypoint for local script.
    """
    asyncio.run(create_ise_endpoints())
