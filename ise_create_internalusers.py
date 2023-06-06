#!/usr/bin/env python3
#------------------------------------------------------------------------------
# @author: Thomas Howard
# @email: thomas@cisco.com
#------------------------------------------------------------------------------
import aiohttp
import asyncio
import argparse
from faker import Faker     # generate fake users, MACs, IPs
import csv
import io
import json
import os
import random

# Globals
USAGE = """

Creates the specified number of ISE internaluser resources using REST APIs.

Requires setting the these environment variables using the `export` command:
  export ISE_HOSTNAME='1.2.3.4'         # hostname or IP address of ISE PAN
  export ISE_REST_USERNAME='admin'      # ISE ERS admin or operator username
  export ISE_REST_PASSWORD='C1sco12345' # ISE ERS admin or operator password
  export ISE_CERT_VERIFY=false          # validate the ISE certificate

You may add these export lines to a text file and load with `source`:
  source ise_environment.sh

"""
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

#_△_△_△_△_△_△_△_△_△_△_△_△_△_△_△_△_△_△_△_△_△_△_△_△_△_△_△_△_△_△_△_△_△_△_△_△_△_△_△
# 🛑  No user-serviceable parts below here 🛑 
#_△_△_△_△_△_△_△_△_△_△_△_△_△_△_△_△_△_△_△_△_△_△_△_△_△_△_△_△_△_△_△_△_△_△_△_△_△_△_△

faker = Faker('en-US')    # fake data generator
username_cache = {}       # NAS identifier name cache to ensure uniqueness

def get_username (firstname=faker.first_name(), lastname=faker.last_name()) :
    """
    Returns the next available instance (name-#) of a name
    """
    n = 1
    username = (firstname[0:1] + lastname[0:8]).lower()
    while (username in username_cache) :
        n += 1
        username = (firstname[0:1] + lastname[0:8] + str(n)).lower()

    username_cache[username] = 1    # cache it
    return username


#------------------------------------------------------------------------------
#
#------------------------------------------------------------------------------
def generate_random_internaluser_data () :
    """
    Return an internaluser object ready for conversion to JSON.
    """

    firstname = faker.first_name()
    lastname = faker.last_name()
    username = get_username(firstname, lastname)

    resource = {
      'InternalUser' : {
        'name' : username,
        'description' : faker.sentence(nb_words=8),
        'enabled' : True,
        'password' : 'ISEisC00L',
        'email' : f"{username}@domain.com",
        'firstName' : firstname,
        'lastName' : lastname,
        'identityGroups' : 'a1740510-8c01-11e6-996c-525400b48521', # Employees
        'passwordIDStore' : "Internal Users",
        'changePassword' : True,
        'passwordNeverExpires' : True,
        'dateModified' : faker.past_date(start_date='-1m').isoformat(),
        'dateCreated' : faker.past_date(start_date='-1m').isoformat(),
        # 'enablePassword' : "enablePassword",
        # 'accountNameAlias' : 'user123'
        # 'daysForPasswordExpiration' : 60
        # 'expiryDateEnabled' : True
        # 'expiryDate' : faker.past_date(start_date='+3M').isoformat(),
    
        # Custom Attributes
        'customAttributes' : {},
        #     "key1": "value1",
        #     "key2": "value2"
        #     'Created' : faker.past_datetime(start_date='-5y').isoformat(sep='T'),
        #     'Updated' : faker.past_datetime(start_date='-6m').isoformat(sep='T'),
        # Organization
        #     'Owner-First-Name' : firstname,
        #     'Owner-Last-Name' : lastname,
        #     'Owner_Email' : username,
        #     'Department' : random.choice(CORPORATE_DEPARTMENTS),
        #     'Zone' : random.choice(ZONES),
        #     'Authorization' : random.choice(['Internet','Employee','Quarantine','Guest','IOT']),
        # Location
        #     'Site' : location.iloc[0]['City3'],
        #     'Building' : location.iloc[0]['Building'],
        #     'Floor' : '',
        #     'Room' : '',
        # Network
        #     "Authorization": "",
        #     "Expiration": "",
        #     "iPSK": ""
        #     'Network_Type' : network_type,
        #     'iPSK' : faker.password(12) if (network_type == 'wireless' and os.iloc[0].Type in ['RHEL','Linux']) else '',
        #     'MAC' : faker.mac_address().upper(),
        #     'Endpoint-IPv4-Static' : faker.ipv4_private() if faker.boolean(.1) else '',
        #     'Identity-Group' : 'Employee',
        # },
      }
    }
    return resource


async def get_resource (session, url) :
    async with session.get(url) as resp:
        response = await resp.json()
        return response['SearchResult']['resources']


async def cache_existing_internalusers (session) :
    """
    Reads existing ISE internalusers and saves them to the username_cache 
    so we do not create an existing user.
    """

    rest_endpoint_path = '/ers/config/internaluser'
    response = await session.get(f"{rest_endpoint_path}?size={REST_PAGE_SIZE}")
    if response.status != 200:
        raise ValueError(f'Bad status: {response}')
    json = await response.json()

    resources = json['SearchResult']['resources']
    if args.verbose : print(f"ⓘ Fetched {len(resources)} resources")

    existing_user_count = json['SearchResult']['total']
    if args.verbose : print(f"ⓘ Existing ISE Internal Users: {existing_user_count}")

    if existing_user_count > REST_PAGE_SIZE :  # we will need more than one fetch
        pages = int(existing_user_count / REST_PAGE_SIZE) + (1 if existing_user_count % REST_PAGE_SIZE else 0)
        urls = []
        for page in range(1, pages + 1):
            urls.append(f"{rest_endpoint_path}?size={REST_PAGE_SIZE}&page={page}")
        urls.pop(0)  # discard first URL; used for the count above

        tasks = []
        [ tasks.append(asyncio.ensure_future(get_resource(session, url))) for url in urls ]

        responses = await asyncio.gather(*tasks)
        [ resources.extend(response) for response in responses ]

    # add users to the cache
    if args.verbose : print(f"ⓘ Adding {len(resources)} users to username_cache")
    for resource in resources :
        username_cache[resource['name']] = 1


async def parse_cli_arguments () :
    """
    Parse the command line arguments
    """
    
    ARGS = argparse.ArgumentParser(
            description=USAGE,
            formatter_class=argparse.RawDescriptionHelpFormatter,   # keep my format
            )
    ARGS.add_argument(
            'number', action='store', type=int, default=1, 
            help='Number of users to create',
            )
    ARGS.add_argument(
            '--verbose', '-v', action='count', default=0,
            help='Verbosity',
            )

    return ARGS.parse_args()


async def create_ise_internalusers () :

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

    # Cache existing ISE users to prevent duplicates and HTTP 400 errors 
    await asyncio.wait_for(cache_existing_internalusers(session), 60)
    if args.verbose : print(f"ⓘ username_cache size: {len(username_cache)}")

    # Generate requested number of users
    users = []
    for n in range(1, args.number + 1) :
        users.append( generate_random_internaluser_data() )
    if args.verbose : print(f"ⓘ Generated {len(users)} users")

    # Create the users with asyncio!
    tasks = []
    [ tasks.append(asyncio.ensure_future(session.post('/ers/config/internaluser', data=json.dumps(user)))) for user in users ]
    responses = await asyncio.gather(*tasks)
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
    asyncio.run(create_ise_internalusers())


if __name__ == '__main__':
    """
    Entrypoint for local script.
    """
    asyncio.run(create_ise_internalusers())
