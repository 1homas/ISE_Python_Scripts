#!/usr/bin/env python3
"""
Generate the specified number of random ISE endpoint resources using REST APIs.

Examples:
  make-endpoint.py -h
  make-endpoint.py -n 10
  make-endpoint.py -f yaml -g random -n 6
  make-endpoint.py -vtn 1000 --group IOT
  make-endpoint.py -tvf csv -g random -n 1000000 > endpoints_1M.csv  # ⏱ 10.287 seconds

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
import requests
import sys
import time
import yaml

FORMATS = ['csv', 'json', 'pretty', 'line', 'yaml']
FORMAT_DEFAULT = 'json'

# ISE 3.4 Context Visibility > Export, ✔ "Importable only"
# ⚠ Note that ISE does not include custom endpoint attributes for import
ISE_CV_DEFAULT_ENDPOINT_EXPORT_COLUMNS = [
    'MACAddress',
    'EndPointPolicy',
    'IdentityGroup',
    'Description',
    # 'DeviceRegistrationStatus',
    # 'BYODRegistration',
    # 'Device Type',
    # 'EmailAddress',
    # 'ip',
    # 'FirstName',
    # 'host-name',
    # 'LastName',
    # 'MDMServerID',
    # 'MDMServerName',
    # 'MDMEnrolled',
    # 'Location',
    # 'PortalUser',
    'User-Name',
    'StaticAssignment',
    'StaticGroupAssignment',
    # 'MDMOSVersion',
    # 'PortalUser.FirstName',
    # 'PortalUser.LastName',
    # 'PortalUser.EmailAddress',
    # 'PortalUser.PhoneNumber',
    # 'PortalUser.GuestType',
    # 'PortalUser.GuestStatus',
    # 'PortalUser.Location',
    # 'PortalUser.GuestSponsor',
    # 'PortalUser.CreationType',
    # 'AUPAccepted',
]


ICONS = {
    # name : icon
    'ERROR'   : '⛒',
    'INFO'    : 'ℹ',
    'PLAY'    : '▷',
    'TIMER'   : '⏱',
}

endpoint_groups_registry = {}    # id : name
mac_registry = {}


def endpoint_to_csv(endpoint:dict=None) -> dict:
    """
    Returns a dictionary mapping endpoint attributes to an importable endpoint CSV format.

    :param endpoint (dict) : a dictionary representing an endpoint
    """
    return {
        'MACAddress' : endpoint.get('mac', ''),
        'EndPointPolicy' : endpoint.get('endpointPolicy', ''), # endpoint profile id?
        'IdentityGroup' : endpoint.get('groupId', ''),
        'Description' : endpoint.get('description', ''),
        # 'DeviceRegistrationStatus' : 'NotRegistered',
        # 'BYODRegistration' : 'Unknown',
        # 'Device Type' : 'Device Type#All Device Types#T-800',
        # 'EmailAddress' : None,
        # 'ip' : None,
        # 'FirstName' : None,
        # 'host-name' : None,
        # 'LastName' : None,
        # 'MDMServerID' : None,
        # 'MDMServerName' : None,
        # 'MDMEnrolled' : None,
        # 'Location' : 'Location#All Locations#AMER#US#XYZ',
        # 'PortalUser' : None,
        'User-Name' : endpoint.get('name', ''),
        'StaticAssignment' : endpoint.get('staticProfileAssignment', 'false'),
        'StaticGroupAssignment' : endpoint.get('staticGroupAssignment', 'false'),
        # 'MDMOSVersion' : None,
        # 'PortalUser.FirstName' : None,
        # 'PortalUser.LastName' : None,
        # 'PortalUser.EmailAddress' : None,
        # 'PortalUser.PhoneNumber' : None,
        # 'PortalUser.GuestType' : None,
        # 'PortalUser.GuestStatus' : None,
        # 'PortalUser.Location' : None,
        # 'PortalUser.GuestSponsor' : None,
        # 'PortalUser.CreationType' : None,
        # 'AUPAccepted' : None,
    }


def get_random_mac (oui:str=None):
    """
    Returns a unique MAC address with the format `XX:XX:XX:XX:XX:XX`.

    :param oui (str) (optional) an organizationally unique identifier of the MAC address
    """
    SEP = ':' # byte separator
    oui = '{:06X}'.format(random.randint(1, 16777216)) if oui is None else oui  # 16777216 == 2^24
    nic = random.randint(1, 16777216) # starting number for MAC's NIC address
    mac = SEP.join([(oui + '{:06X}'.format(nic))[idx:idx+2] for idx in range(0, 12, 2)]) # Format MAC XX:XX:XX:XX:XX:XX
    while (mac in mac_registry):
        mac = SEP.join([(oui + '{:06X}'.format(nic+1))[idx:idx+2] for idx in range(0, 12, 2)])
    mac_registry[mac] = True
    return mac


def get_endpointgroup_id(name:str='Unknown'):
    """
    Returns the id of the endpoint group with the specified name, otherwise `None`.

    :param name (str) : the name of the endpoint group
    """
    if args.verbosity >= 2: print(f"{ICONS['PLAY']} get_endpointgroup_id(name={name})", file=sys.stderr)
    names = [k for k,v in endpoint_groups_registry.items() if v == name]
    if len(names) == 0:
        return None
    return names[0]


def show(resources:list=None, format:str=FORMAT_DEFAULT, filepath:str='-', headers:list=None, name:str='objects'):
    """
    Show/print/dump the resources in the specified format to the file. `sys.stdout` ('-') by default.

    - resources (list) : a list of list items to show
    - headers (list) : the name of the resource. Example: endpoint, sgt, etc.
    - format (str): one the following formats:
        - `csv`   : Show the items in a Comma-Separated Value (CSV) format
        - `json`  : Show the items as a single JSON string
        - `yaml`  : Show the items as YAML with 2-space indents
    - filepath (str) : Default: `sys.stdout`
    """
    if resources == None: return
    if not format in FORMATS: raise ValueError(f"Unsupported format: {format}")
    if format == 'csv' and headers is None: raise ValueError(f"CSV requires headers")
    if format != 'csv' and name is None: raise ValueError(f"JSON and YAML require an object name")
    if args.verbosity >= 2: print(f"{ICONS['PLAY']} show({len(resources)} as {format} to {filepath})", file=sys.stderr)

    # 💡 Do not close sys.stdout or it may not be re-opened with multiple show() calls
    fh = sys.stdout if filepath == '-' else open(filepath, 'w') # write to sys.stdout/terminal by default

    if format == 'csv':  # CSV
        writer = csv.DictWriter(fh, headers) # , encoding='utf-8')
        writer.writeheader()
        writer.writerows(resources)
    elif format == 'json':  # JSON, one long string
        print(json.dumps({ name: resources }), file=fh)
    elif format == 'line':  # 1 JSON line per object
        print('{', file=fh)
        print(f'"{name}" : [', file=fh)
        print(",\n".join([json.dumps(r) for r in resources]), file=fh)
        print(']\n}', file=fh)
    elif format == 'pretty':  # pretty-print
        print(json.dumps({ name: resources }, indent=2), file=fh)
    elif format == 'yaml':  # YAML
        print(yaml.dump({ name: resources }, indent=2, default_flow_style=False), file=fh)
    else:  # just in case something gets through the CLI parser
        print(f' 🛑 Unknown format: {format}', file=sys.stderr)


def make_endpoint(
        name:str=None,
        mac:str=None,
        description:str=None,
        group:str=None,
        group_type:str='id',            # ['id','name']
        # profile:str=None,             # 🚧 ToDo
        # identityStore:str=None,       # 🚧 ToDo
        # customAttributes:dict=None,   # 🚧 ToDo
        # mdmAttributes:dict=None,      # 🚧 ToDo
    ):
    """
    Make an ISE endpoint object.

    :param name (str) : None,
    :param mac (str) : None,
    :param description (str) : None,
    :param group (str) : None,

    """
    if args.verbosity >= 2: print(f"{ICONS['PLAY']} make_endpoint(name={name}, mac={mac}, description={description}, group={group})", file=sys.stderr)

    mac = get_random_mac()

    group = 'Unknown' if group is None else group
    group = random.choice(list(endpoint_groups_registry.values())) if group == 'random' else group
    group = get_endpointgroup_id(group) if group_type == 'id' else group # CSV uses name, JSON & YAML use 

    # ISE OpenAPI endpoint (/ers/config/endpoint)
    endpoint = {
        'name': mac,
        'description': '', # faker.sentence(nb_words=8), # optional
        'mac': mac,
        'profileId': None,                        # optional
        'staticProfileAssignment'       : False,
        'staticProfileAssignmentDefined': False,  # optional
        'groupId': group,
        'staticGroupAssignment'         : False,
        'staticGroupAssignmentDefined'  : False,  # optional
        # 'portalUser': '',                         # optional
        # 'identityStore': 'InternalUsers',         # optional
        # 'identityStoreId': '',                    # optional
        # 'customAttributes': {                     # optional
        #     'customAttributes': { }
        # },
        # 'mdmAttributes': { },                     # optional
    }
    if args.verbosity >= 2: print(f"{ICONS['INFO']} make_endpoint(): {endpoint}", file=sys.stderr)
    return endpoint

    # ISE OpenAPI endpoint (/api/v1/endpoint)
    # {
    #   "id": "028436a0-ff80-11ee-996b-bacbf94e72cd",
    #   "name": "A7:F2:61:F1:D6:C6",
    #   "description": "",
    #   "customAttributes": null,
    #   "mdmAttributes": null,
    #   "groupId": "aa0e8b20-8bff-11e6-996c-525400b48521",
    #   "identityStore": "",
    #   "identityStoreId": "",
    #   "mac": "A7:F2:61:F1:D6:C6",
    #   "portalUser": "",
    #   "profileId": "",
    #   "ipAddress": null,
    #   "vendor": null,
    #   "productId": null,
    #   "serialNumber": null,
    #   "deviceType": null,
    #   "softwareRevision": null,
    #   "hardwareRevision": null,
    #   "protocol": null,
    #   "staticGroupAssignment": false,
    #   "staticProfileAssignment": false,
    #   "assetId": null,
    #   "assetName": null,
    #   "assetIpAddress": null,
    #   "assetVendor": null,
    #   "assetProductId": null,
    #   "assetSerialNumber": null,
    #   "assetDeviceType": null,
    #   "assetSwRevision": null,
    #   "assetHwRevision": null,
    #   "assetProtocol": null,
    #   "assetConnectedLinks": null
    # }


if __name__ == '__main__':
    """
    Entrypoint for local script.
    """
    argp = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    argp.add_argument('-n', '--number', action='store', type=int, default=1, help='number of endpoints to create', required=False)
    argp.add_argument('-f', '--format', choices=FORMATS, default='yaml', help='Output format or styling')
    argp.add_argument('-g', '--group', action='store', type=str, default='Unknown', help='endpoint group name; `random` chooses randomly', required=False)
    argp.add_argument('-t', '--timer', action='store_true', default=False, help='show total runtime, in seconds')
    argp.add_argument('-v', '--verbosity',  action='count', default=0, help='verbosity count',)
    global args     # promote to global scope for use in other functions
    args = argp.parse_args()

    if args.timer: start_time = time.time()

    env = {k:v for (k, v) in os.environ.items() if k.startswith('ISE_')}  # Load environment variables
    # 💡 Cache endpoint group ids & names - there is no guarantee of consistent ids across ISE deployments even for default groups
    # 🚧 ToDo: Implement paging for >100 endpoint groups
    response = requests.get(
                f"https://{env['ISE_PPAN']}/ers/config/endpointgroup?&size=100", 
                auth=(env['ISE_REST_USERNAME'], env['ISE_REST_PASSWORD']),
                headers={ 'Accept': 'application/json' },
                verify=(False if env['ISE_CERT_VERIFY'][0].lower() in ['f','n'] else True)
            )
    for item in (response.json())['SearchResult']['resources']:
        endpoint_groups_registry[item['id']] = item['name'] # cache id to name

    endpoints = []
    for idx in range(1, args.number+1):
        endpoints.append(make_endpoint(group=args.group, group_type=('id' if args.format == 'json' else 'name')))

    if args.format == 'csv':
        endpoints = [endpoint_to_csv(endpoint) for endpoint in endpoints] # return [dict] for CSV

    show(endpoints, format=args.format, filepath='-', name='endpoint', headers=ISE_CV_DEFAULT_ENDPOINT_EXPORT_COLUMNS)

    if args.timer: print(f"{ICONS['TIMER']} {'{0:.3f}'.format(time.time() - start_time)} seconds", file=sys.stderr)
