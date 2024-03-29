#!/usr/bin/env python3
"""
Creates the specified number of ISE internaluser resources using REST APIs.

Requires setting the these environment variables using the `export` command:
  export ISE_HOSTNAME='1.2.3.4'         # hostname or IP address of ISE PAN
  export ISE_REST_USERNAME='admin'      # ISE ERS admin or operator username
  export ISE_REST_PASSWORD='C1sco12345' # ISE ERS admin or operator password
  export ISE_CERT_VERIFY=false          # validate the ISE certificate

You may add these `export` lines to a text file, customize them, and load with `source`:
  source ise_environment.sh

"""

import aiohttp
import asyncio
import argparse
from faker import Faker     # generate fake users, MACs, IPs
import csv
import io
import json
import os
import random
import sys

# Globals
REST_PAGE_SIZE_DEFAULT=20
REST_PAGE_SIZE_MAX=100
REST_PAGE_SIZE=REST_PAGE_SIZE_MAX
WORKERS_MAX=20


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
        'description' : '', # faker.sentence(nb_words=8),
        'enabled' : True,
        'password' : 'ISEisC00L',
        'email' : f"{username}@domain.com",
        'firstName' : firstname,
        'lastName' : lastname,
        'identityGroups' : 'a1740510-8c01-11e6-996c-525400b48521', # Employees
        'passwordIDStore' : "Internal Users",
        'changePassword' : False,
        # 'enablePassword' : "enablePassword",
        'expiryDateEnabled' : False,
        # 'expiryDate' : faker.past_date(start_date='+3M').isoformat(),
        # 💡 ISE 3.2+ :
        'passwordNeverExpires' : True,
        # 'accountNameAlias' : 'user123',
        # 'daysForPasswordExpiration' : 60,
        # 💡 ISE 3.3+ :
        # 'dateModified' : faker.past_date(start_date='-1m').isoformat(),
        # 'dateCreated' : faker.past_date(start_date='-1m').isoformat(),
    
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
    async with session.get(url, ssl=False) as resp:
        response = await resp.json()
        return response['SearchResult']['resources']


async def cache_existing_internalusers (session) :
    """
    Reads existing ISE internalusers and saves them to the username_cache so we do not create an existing user.
    """
    print(f"ⓘ Caching existing users ...", file=sys.stderr)
    rest_endpoint_path = '/ers/config/internaluser'
    response = await session.get(f"{rest_endpoint_path}?size={REST_PAGE_SIZE}")
    if response.status != 200: raise ValueError(f'Bad status: {response}')
    json = await response.json()

    resources = json['SearchResult']['resources']
    if args.verbose : print(f"ⓘ Fetched {len(resources)} resources", file=sys.stderr)

    existing_user_count = json['SearchResult']['total']
    if args.verbose : print(f"ⓘ Existing ISE Internal Users: {existing_user_count}", file=sys.stderr)

    if existing_user_count > REST_PAGE_SIZE :  # we will need more than one fetch
        pages = int(existing_user_count / REST_PAGE_SIZE) + (1 if existing_user_count % REST_PAGE_SIZE else 0)
        urls = []
        for page in range(1, pages + 1):
            urls.append(f"{rest_endpoint_path}?size={REST_PAGE_SIZE}&page={page}")
        urls.pop(0)  # discard first URL; used for the count above
        tasks = [asyncio.ensure_future(get_resource(session, url)) for url in urls]
        responses = await asyncio.gather(*tasks)
        [resources.extend(response) for response in responses]

    for resource in resources :  # add users to the cache
        username_cache[resource['name']] = 1
    print(f"ⓘ Cached {len(username_cache)} users", file=sys.stderr)

    return username_cache


async def ise_internaluser_creator (queue, session):
    PATH = '/ers/config/internaluser'
    while True:
        user_dict = await queue.get() # Get an item from the queue
        response = await session.post(PATH, data=json.dumps(user_dict))
        if response.status == 201 :
            print(f"✔ {response.status} | {user_dict['InternalUser']['name']} | {response.headers['Location'].split('/')[-1]}", file=sys.stderr)
        elif response.status == 400 and (await response.json())['ERSResponse']['messages'][0]['title'].find('Password') :
            # 🐞 ISE will randomly complain about Password Policy even though it's fine
            print(f"🐞 Password Policy error: Re-queue {user_dict['InternalUser']['name']}", file=sys.stderr)
            queue.put_nowait( user_dict )
        elif response.status == 401 :
            print(f"Set the environment variables and verify your credentials are correct! {await response.json()}", file=sys.stderr)
            break
        else :
            error = await response.json()
            print(f"✖ {response.status} {user_dict['InternalUser']['name']} {error['ERSResponse']['messages'][0]['title']}", file=sys.stderr)
        queue.task_done()  # Notify queue the item is processed


async def main ():
    """
    Entrypoint for packaged script.
    """
    global args
    argp = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    argp.add_argument('number', action='store', type=int, default=1, help='Number of users to create')
    argp.add_argument('-t','--timer', action='store_true', default=False, help='time', required=False)
    argp.add_argument('-v', '--verbose', action='count', default=0, help='Verbosity')
    args = argp.parse_args()
    if args.verbose >= 3 : print(f"ⓘ args: {args}", file=sys.stderr)
    if args.timer : start_time = time.time()

    env = {k:v for (k, v) in os.environ.items()} # Load environment variables

    # Create HTTP session
    base_url = f"https://{env['ISE_HOSTNAME']}"
    conn = aiohttp.TCPConnector(ssl=(False if env['ISE_CERT_VERIFY'][0:1].lower() in ['f','n'] else True))
    basic_auth = aiohttp.BasicAuth(login=env['ISE_REST_USERNAME'], password=env['ISE_REST_PASSWORD'])
    json_headers = {'Accept':'application/json', 'Content-Type':'application/json'}
    async with aiohttp.ClientSession(base_url, auth=basic_auth, connector=conn, headers=json_headers) as session:
        # Cache existing ISE users to prevent duplicates and HTTP 400 errors 
        username_cache = await asyncio.wait_for(cache_existing_internalusers(session), 60)
        if args.verbose : print(f"ⓘ username_cache size: {len(username_cache)}")
        users_queue = asyncio.Queue() # Create a queue for the user workload

        # Create worker tasks to process the queue concurrently
        tasks = [asyncio.create_task(ise_internaluser_creator(users_queue, session)) for ii in range(WORKERS_MAX)]
        [users_queue.put_nowait(generate_random_internaluser_data()) for n in range(1, args.number + 1)] # enqueue a user for creation
        await users_queue.join()  # Wait until the queue is finished

    if args.timer : print(f"⏲ {'{0:.3f}'.format(time.time() - start_time)} seconds", file=sys.stderr)


if __name__ == '__main__':
    """
    Entrypoint for local script.
    """
    asyncio.run(main())
