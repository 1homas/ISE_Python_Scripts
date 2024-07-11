#!/usr/bin/env python3
"""
Show Meraki organization, networks, devices data.

    meraki-show.py {resource} [filters] [options]

🌟Supports both shell-style glob (*,?) and regex filtering of names.
💡Wrap any globs ([*?]) or regex expressions in quotes to prevent any shell command errors.
💡You may omit the 'orgs' filter if you have set a MERAKI_ORG_NAME environment variable.

Requires setting the these environment variables using the `export` command:
    export MERAKI_DASHBOARD_API_KEY='abcdef1234567890abcdef1234567890abcdef12'

You may add these export lines to a text file and load with `source`:
  source ~/.secrets/.env.meraki

Examples:

    meraki-show.py --help

    meraki-show.py orgs
    meraki-show.py networks
    meraki-show.py devices


    meraki-show.py -tv -f {format}
    meraki-show.py {filters} -tv

    meraki-show.py orgs
    meraki-show.py orgs orgs:1homas -f yaml --show id,name,url

    meraki-show.py networks orgs:1homas --show id,name,url,tags
    meraki-show.py networks orgs:1homas --hide productTypes,enrollmentString
    meraki-show.py networks orgs:1homas --hide details,notes,lat,lng,wan1Ip,wan2Ip,productTypes,timeZone,enrollmentString
    meraki-show.py networks orgs:1homas networks:"lab*" -tv --show id,name,url
    meraki-show.py networks networks:"L*" 

    meraki-show.py devices orgs:1homas
    meraki-show.py devices orgs:1homas networks:"lab*"
    meraki-show.py devices networks:"*" devices:"lab*"
    meraki-show.py devices networks:Lab devices:mr46 -vt
    meraki-show.py devices networks:"ho*" model:Z3 -tv --show id,name,url

    meraki-show.py devices model:"MX*"
    meraki-show.py devices model:MR. --hide details,lat,lng,url,tags,notes,wan1Ip,address

    meraki-show.py devices models:Z3,MX68

    meraki-show.py devices serials:Q3EH-TL5Q-BM3J
    meraki-show.py devices serials:Q3EH-TL5Q-BM3J,Q2TN-ZU6W-68MT
    meraki-show.py devices serials:"( Q3EH-TL5Q-BM3J, Q2TN-ZU6W-68MT )"
    meraki-show.py devices "serials:[Q3EH-TL5Q-BM3J,Q2TN-ZU6W-68MT]"

💡Futures:
    meraki-show.py devices networks:Lab devices:"*" link:"1 gbps" --hide url,tags,notes,wan1Ip,address
    meraki-show.py clients
    meraki-show.py ports
    meraki-show.py ports vlan:1-1000
    meraki-show.py ports networks:Lab devices:"z3*"
    meraki-show.py ports networks:Lab devices:"z3*" "switch:*" "port:*" "is:*" "tag:*" "vlan:*" "lldp:*"  "link:*"  "ap:*"  "schedule:*"  "group:*"  "mac:*" -v

"""
__author__ = "Thomas Howard"
__email__ = "thomas@cisco.com"
__license__ = "MIT - https://mit-license.org/"


import argparse
import asyncio
import json
import os
import sys
import requests
from tabulate import tabulate
import meraki.aio
import yaml
import csv
import re
import time
import fnmatch # for string glob matches

ICONS = {
    # name : icon
    'BUG  '   : '🐞',
    'CACHE'   : '↯',
    'DOWN'    : '▽',
    'ERROR'   : '⛒',
    'NONE'    : '∅',
    'FAIL'    : '✖',
    'INFO'    : 'ℹ',
    'ID'      : '⚿',
    'LIST'    : '⁝',
    'LOCK'    : '🔒',
    'PASS'    : '✔',
    'PLAY'    : '▷',
    'TIMEOUT' : '◔',
    'TIP'     : '💡',
    'UNLOCK'  : '🔓',
    'WARN'    : '⚠',
    'WATCH'   : '⏱',
}
MERAKI_BASE_URL = 'https://api.meraki.com/api/v1' # Set up the base URL and headers for the Meraki API
MERAKI_SERIAL_RE = r'[0-9A-Z]{4,4}-[0-9A-Z]{4,4}-[0-9A-Z]{4,4}'
SUPPORTED_FORMATS = ['csv', 'grid', 'table', 'json', 'line', 'pretty', 'yaml']
SUPPORTED_RESOURCES = [ 'orgs', 'networks', 'devices', ] # 💡 ToDo: 'ports', 'clients', 
SUPPORTED_FILTERS = [
    'orgs', # str : glob or regex
    'networks', # str : glob or regex
    'devices', # str : glob or regex
    'model', # str : glob or regex
    'models', # [str] An array of one or more models with an exact match.
    'types', # [str]: Filter devices by product type. Enum:[wireless, appliance, switch, systemsManager, camera, cellularGateway, sensor, secureConnect]
    'serial', # str A serial number that contains the search term or is an exact match.
    'serials', # Devices with serial numbers that are an exact match.

    # 💡ToDo
    # 'module', # module types | module:8x10 

    # Networks
    # 'tags_type', # ['withAnyTags' | 'withAllTags'] indicates networks ANY or ALL of the included tags. If no type is included, 'withAnyTags' will be selected.
    # 'tags', # [str] Filter devices by tags.

    # Ports
    # 'port', # {value} | specified ports or ranges | port:1-10  
    # 'switch', # {value} | ports for switch(es) | switch:"1st floor" 
    # 'is',   # {[aggregated | uplink | trunk | access]}  
    # 'vlan', # [{int}, {name}, native, voice]     
    # 'lldp', # {value}
    # 'link', # {value} port link type set speed/duplex | link:"100 mbps"
    # 'ap',   # ports with specified access policy | ap:*
    # 'schedule', # ports with specified schedule  | schedule:*
    # 'group', # ports in common group               | group:1

    # Clients
    # 'mac', # ports with mac-whitelist | mac_whitelist:aa:bb:cc:dd:ee:ff
    # 'mac_whitelist', # ports with mac-whitelist | mac_whitelist:aa:bb:cc:dd:ee:ff
]


def show_resources(resources:[dict]=None, name:str=None, format='json', filepath:str='-', hide:[str]=None, show:[str]=None) -> None:
    """
    Show/print/dump the resources in the specified format to the file. `sys.stdout` ('-') by default.

    :param resources ([dict]) : a list of dictionary items to format
    :param name (str) : the name of the resource. Example: endpoint, sgt, etc.
    :param format (str): one the following formats:
            - `csv`   : Show the items in a Comma-Separated Value (CSV) format
            - `grid`  : Show the items in a table grid with borders
            - `table` : Show the items in a text-based table
            - `json`  : Show the items as a single JSON string
            - `line`  : Show the items as JSON with each item on it's own line
            - `pretty`: Show the items as JSON pretty-printed with 2-space indents
            - `yaml`  : Show the items as YAML with 2-space indents
    :param filepath (str) : Default: `sys.stdout`
    """
    if resources == None: return
    object_type = None if len(resources) <= 0 else type(resources[0]) 
    if args.verbosity >= 3: print(f"▷ show_resources({len(resources)} x '{name}' as {format} to {filepath})", file=sys.stderr)

    # Hide or show attributes?
    if hide is not None and show is not None: raise ValueError(f'hide and show are mutually exclusive and should not be used at the same time')
    if hide is not None: resources = [{k:v for k,v in resource.items() if k not in hide} for resource in resources]
    if show is not None: resources = [{k:v for k,v in resource.items() if k in show} for resource in resources]

    # 💡 Do not close sys.stdout or it may not be re-opened with multiple show_resources() calls
    fh = sys.stdout if filepath == '-' else open(filepath, 'w') # write to sys.stdout/terminal by default

    if format == 'csv':  # CSV
        headers = {}
        [headers.update(r) for r in resources]  # find all unique keys
        writer = csv.DictWriter(fh, headers.keys(), quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        for row in resources:
            writer.writerow(row)
    elif format == 'grid': # grid
        print(f"{tabulate(resources, headers='keys', tablefmt='simple_grid')}", file=fh)
    elif format == 'table': # table
        print(f"{tabulate(resources, headers='keys', tablefmt='table')}", file=fh)
    elif format == 'json':  # one long string of JSON
        print(json.dumps({ name: resources }), file=fh)
    elif format == 'line':  # 1 JSON object per line
        print('{', file=fh)
        print(f'"{name}" : [', file=fh)
        print(",\n".join([json.dumps(r) for r in resources]), file=fh)
        print(']\n}', file=fh)
    elif format == 'pretty':  # pretty-print
        print(json.dumps({ name: resources }, indent=2), file=fh)
    elif format == 'yaml':  # YAML
        print(yaml.dump({ name: resources }, indent=2, default_flow_style=False), file=fh)
    else:
        print(f"{ICONS['ERROR']} Unknown format: {format}", file=sys.stderr)


def parse_filters_to_dict(filters:[str]=[]):
    """
    Return a dictionary of filter keys and values.
    """
    # print(f"{ICONS['PLAY']} parse_filters_to_dict(filters={filters})")
    filter_dict = {}
    if filters is not None and len(filters) > 0:
        for facet in filters:
            if facet.find(':') <= 0: raise ValueError('Invalid filter: {facet}')
            key,val = facet.split(':')
            key = key.lower().strip()
            if key not in SUPPORTED_FILTERS: 
                print(f"{ICONS['WARN']} Ignoring invalid filter key: {key}", file=sys.stderr)
                continue
            filter_dict[key] = val.strip()
        # Show filter expression
        # print(f"{ICONS['INFO']} Search: {' AND '.join([':'.join([k,v]) for (k,v) in filter_dict.items()])}", file=sys.stderr)
    return filter_dict


def is_meraki_serial(s:str=None) -> bool:
    """
    Returns True if the string s matches the Meraki serial number pattern (xxxx-xxxx-xxxx), False otherwise.
    """
    return re.match(MERAKI_SERIAL_RE, s.strip())


def is_glob_pattern(s:str=None) -> bool:
    """
    Returns True if the search string s is a glob pattern or False if it is regex pattern.
    It looks for characters and sequences that are almost certainly indicative of regex use. 
    If none are found, it defaults to assuming the pattern is a glob.
    There are edge cases where a string could technically be both a valid glob pattern and a regex pattern

    | Pattern | Meaning                          |
    | *       | matches everything               |
    | ?       | matches any single character     |
    | [seq]   | matches any character in seq     |
    | [!seq]  | matches any character not in seq |

    @param s (str): a search pattern (a shell-style glob or regex)
    """
    if s is None: return False

    # Check if any regex-specific character is present in the string
    regex_specific_chars = ['^', '$', '|', '(', ')', '+', '{', '}', '.', '\\']
    for char in regex_specific_chars:
        if char in s: return False  # It's likely a regex pattern

    # Check for regex quantifier patterns that are not used in glob patterns
    return False if re.search(r'\(\?|\[:|\[\.|\[\=|\(\?\<|\(\?\=|\(\?\!|\(\?\:|\(\?\#', s) else True


# Main function to run the script
async def meraki_show(resource:str=None, filters:[str]=[], format:str='yaml', verbosity:int=0, hide:[str]=None, show:[str]=None) -> None:
    """
    Show Meraki org, networks, devices matching the specified filter.
    """
    if verbosity >= 1: print(f"{ICONS['PLAY']} meraki_show(resource={resource}, filters={filters}, format={format}, verbosity={verbosity})")
    if resource is None or resource == '': raise ValueError(f'resource is None or empty')
    if resource not in SUPPORTED_RESOURCES: raise ValueError(f'Invalid resource type: {resource}')

    # Convert filters from list to a dict for quick access
    filter_dict = parse_filters_to_dict(filters) if filters is not None and len(filters) > 0 else {}
    if verbosity >= 3: print(f"{ICONS['INFO']} filter_dict: {filter_dict}", file=sys.stderr)
    if verbosity >= 3: print(f"{ICONS['INFO']} SUPPORTED_FILTERS: {SUPPORTED_FILTERS}", file=sys.stderr)

    # 💡 MERAKI_DASHBOARD_API_KEY environment variable is used automatically!
    async with meraki.aio.AsyncDashboardAPI(suppress_logging=True, print_console=True) as aiomeraki:

        #
        # Organizations
        #

        # Get list of organizations to which API key has access
        orgs = await aiomeraki.organizations.getOrganizations()

        # Use org filter or MERAKI_ORG_NAME environment variable?
        org_filter = filter_dict.pop('orgs', None)
        if org_filter is None and os.getenv('MERAKI_ORG_NAME', None) is not None:
            org_filter = os.getenv('MERAKI_ORG_NAME')
            if verbosity >= 1: print(f"{ICONS['INFO']} Filter 'orgs:{org_filter}' applied from MERAKI_ORG_NAME", file=sys.stderr)

        if org_filter is not None:
            if verbosity >= 2: print(f"{ICONS['INFO']} org_filter: {org_filter}", file=sys.stderr)

            if re.match(r'[\d]{6,}', org_filter): # org ids should have a minimum 6 digits
                if verbosity >= 3: print(f"{ICONS['INFO']} org_filter '{org_filter}' is an org id", file=sys.stderr)
                orgs = list(filter(lambda org: True if org_filter == org['id'] else False, orgs))
            else: # org name
                re_org_filter = None

                # convert glob to regex for re.match()
                if is_glob_pattern(org_filter):
                    re_org_filter = fnmatch.translate(org_filter)
                    if verbosity >= 3: print(f"{ICONS['INFO']} Converted glob filter {org_filter} to {re_org_filter}", file=sys.stderr)

                # Regex filter?
                org_filter = re_org_filter if re_org_filter is not None else org_filter
                orgs = list(filter(lambda org: False if re.search(org_filter, org['name']) is None else True, orgs))
                if verbosity >= 2: print(f"{ICONS['INFO']} Regex filtered orgs: {orgs}", file=sys.stderr)

        # Show Meraki Org?
        if resource.lower().startswith('org'):
            show_resources(orgs, name='organizations', format=format, hide=hide, show=show)
            return

        # Must have exactly 1 org to search other resources
        if len(orgs) <= 0: sys.exit(f"{ICONS['ERROR']} No orgs matched the filter: {org_filter}")
        if len(orgs) > 1 and org_filter is None: sys.exit(f"{ICONS['ERROR']} Must use an 'org' filter to match a single org")
        if len(orgs) > 1: sys.exit(f"{ICONS['ERROR']} More than 1 orgs matched the filter '{org_filter}': {orgs}")

        org_id = orgs[0]['id']

        #
        # Networks
        #

        networks = await aiomeraki.organizations.getOrganizationNetworks(org_id, total_pages=all)
        network_filter = filter_dict.pop('networks', None)
        if network_filter is not None:
            re_network_filter = None
            if is_glob_pattern(network_filter):
                re_network_filter = fnmatch.translate(network_filter) # convert glob to regex for re.match()
                if verbosity >= 3: print(f"{ICONS['INFO']} Converted glob filter {network_filter} to {re_network_filter}", file=sys.stderr)

            # Regex filter?
            network_filter = re_network_filter if re_network_filter is not None else network_filter
            networks = list(filter(lambda network: False if re.search(network_filter, network['name']) is None else True, networks))
            if verbosity >= 3: print(f"{ICONS['INFO']} Matched networks: {','.join([network['name'] for network in networks])}", file=sys.stderr)

        # Show Meraki Network(s)?
        if resource.lower().startswith('net'):
            show_resources(networks, name='networks', format=format, hide=hide, show=show)
            return

        network_ids = [network['id'] for network in networks]
        if verbosity >= 3: print(f"{ICONS['INFO']} Matched networks: {','.join(network_ids)}", file=sys.stderr)

        if verbosity >= 3 and len(filter_dict) > 0: print(f"filter_dict: {filter_dict}", file=sys.stderr)

        #
        # Devices
        # 
        # There are 4 ways to search/filter by device name:
        # - no filter - get all devices
        # - substring: simple alphanumeric substring filter using getOrganizationDevices(name=substring)
        # - glob: perform glob match on the name after getting all devices using getOrganizationDevices() 
        # - regex: perform regex match on the name after getting all devices using getOrganizationDevices() 
        devices = []
        devices_filter = filter_dict.pop('devices', None)
        if devices_filter is None and resource.lower().startswith('dev'): # Get ALL devices
            if verbosity >= 3: print(f"{ICONS['INFO']} devices_filter is None", file=sys.stderr)
            devices = await aiomeraki.organizations.getOrganizationDevices(org_id, total_pages=all)
            if verbosity >= 3: print(f"{ICONS['INFO']} ALL devices: [{len(devices)}]", file=sys.stderr)
        elif re.search(r'\A[a-zA-Z0-9_-]+\Z', devices_filter): # match substring
            if verbosity >= 3: print(f"{ICONS['INFO']} devices_filter '{devices_filter}' is substring", file=sys.stderr)
            # use Meraki names kwarg to filter
            devices = await aiomeraki.organizations.getOrganizationDevices(org_id, total_pages=all, name=devices_filter)
            if verbosity >= 3: print(f"{ICONS['INFO']} substring matched {len(devices)} devices", file=sys.stderr)
        elif is_glob_pattern(devices_filter): # match glob
            if verbosity >= 3: print(f"{ICONS['INFO']} devices_filter '{devices_filter}' is glob", file=sys.stderr)
            # Get all devices and perform glob match
            devices = await aiomeraki.organizations.getOrganizationDevices(org_id, total_pages=all)
            re_devices_filter = fnmatch.translate(devices_filter) # convert glob to regex for re.match()
            if verbosity >= 3: print(f"{ICONS['INFO']} Converted glob filter {devices_filter} to {re_devices_filter}", file=sys.stderr)
            devices = list(filter(lambda device: False if re.search(re_devices_filter, device['name']) is None else True, devices))
            if verbosity >= 3: print(f"{ICONS['INFO']} glob matched {len(devices)} devices: [{len(devices)}] : {','.join([device['name'] for device in devices])}", file=sys.stderr) 
        else: # match regex
            if verbosity >= 3: print(f"{ICONS['INFO']} devices_filter '{devices_filter}' is regex", file=sys.stderr)
            # Get all devices and perform glob match
            devices = await aiomeraki.organizations.getOrganizationDevices(org_id, total_pages=all)
            devices = list(filter(lambda device: False if re.search(devices_filter, device['name']) is None else True, devices))
            if verbosity >= 3: print(f"{ICONS['INFO']} regex matched {len(devices)} devices: {','.join([device['name'] for device in devices])}", file=sys.stderr)

        # @param [str] types : # Filter devices by product type. Enum:[wireless, appliance, switch, systemsManager, camera, cellularGateway, sensor, secureConnect]
        types_filter = filter_dict.pop('types', None)
        if types_filter is not None:
            if verbosity >= 3: print(f"{ICONS['INFO']} types_filter '{types_filter}'", file=sys.stderr)
            TYPES = ['wireless', 'appliance', 'switch', 'systemsManager', 'camera', 'cellularGateway', 'sensor', 'secureConnect']
            types = types_filter.strip('[](), ').split(',')
            for type in types:
                if type not in TYPES:
                    print(f"{ICONS['WARN']} Ignoring invalid filter type: {type}. Must be one of [{','.join(TYPES)}]", file=sys.stderr)
                    types.remove(type)
            if verbosity >= 3: print(f"{ICONS['INFO']} Using types [{','.join(types)}]", file=sys.stderr)
            devices = await aiomeraki.organizations.getOrganizationDevices(org_id, total_pages=all, productTypes=types)
            if verbosity >= 3: print(f"{ICONS['INFO']} types [{','.join(types)}] matched {len(devices)} devices", file=sys.stderr)


        # @param str model : a model that contains the search term or is an exact match.
        model_filter = filter_dict.pop('model', None)
        if model_filter is not None:
            if verbosity >= 3: print(f"{ICONS['INFO']} model:{model_filter}", file=sys.stderr)
            re_model_filter = fnmatch.translate(model_filter) if is_glob_pattern(model_filter) else model_filter # convert glob to regex for re.match()
            devices = list(filter(lambda device: False if re.search(re_model_filter, device['model']) is None else True, devices))
            if len(devices) <= 0: print(f"{ICONS['INFO']} model:{model_filter} matched {len(devices)} devices: Try using a wildcard (. or *)", file=sys.stderr)

        # @param [str] models : an array of one or more models with an exact match.
        models_filter = filter_dict.pop('models', None)
        if models_filter is not None:
            if verbosity >= 3: print(f"{ICONS['INFO']} models:{models_filter}", file=sys.stderr)
            models = models_filter.strip('[](), ').split(',')
            if verbosity >= 3: print(f"{ICONS['INFO']} [models]:{models}", file=sys.stderr)
            devices = list(filter(lambda device: True if device['model'] in models else False, devices))
            if verbosity >= 3: print(f"{ICONS['INFO']} models:{models_filter} matched {len(devices)} devices: {','.join([device['name'] for device in devices])}", file=sys.stderr)

        # serial. A serial number that contains the search term or is an exact match.
        serial_filter = filter_dict.pop('serial', None)
        if serial_filter is not None:
            if verbosity >= 3: print(f"{ICONS['INFO']} serial:{serial_filter}", file=sys.stderr)
            # Q3EH-TL5Q-BM3J
            # re_serial_filter = fnmatch.translate(serial_filter) if is_glob_pattern(serial_filter) else serial_filter # convert glob to regex for re.match()
            # devices = list(filter(lambda device: False if re.search(re_serial_filter, device['serial']) is None else True, devices))
            devices = await aiomeraki.organizations.getOrganizationDevices(org_id, total_pages=all, serial=serial_filter)

        # serials. Devices with serial numbers that are an exact match.
        serials_filter = filter_dict.pop('serials', None)
        if serials_filter is not None:
            if verbosity >= 3: print(f"{ICONS['INFO']} serials:{serials_filter}", file=sys.stderr)
            serials = serials_filter.strip('[](), ').split(',')
            serials = [serial.strip() for serial in serials]
            if verbosity >= 3: print(f"{ICONS['INFO']} [serials]:{serials}", file=sys.stderr)
            for serial in serials:
                if not is_meraki_serial(serial):
                    print(f"{ICONS['WARN']} Invalid Meraki serial number format: {serial}", file=sys.stderr)
                    serials.remove(serial)
            if len(serials) > 0:
                devices = await aiomeraki.organizations.getOrganizationDevices(org_id, total_pages=all, serials=serials)

        # tags: [str] Filter devices by tags.
        tags_filter = filter_dict.pop('tags', None)
        if tags_filter is not None: print(f"{ICONS['ERROR']} tags_filter:{tags_filter} is not implemented", file=sys.stderr)

        # tags_type: ['withAnyTags' | 'withAllTags'] indicates networks ANY or ALL of the included tags. If no type is included, 'withAnyTags' will be selected.
        tags_type_filter = filter_dict.pop('tags_type', None)
        if tags_type_filter is not None: print(f"{ICONS['ERROR']} tags_type_filter:{tags_type_filter} is not implemented", file=sys.stderr)

        # Show Devices?
        if resource.lower().startswith('dev'):
            show_resources(devices, name='devices', format=format, hide=hide, show=show)
            return

        #
        # Modules
        #

        # 'module', # module types | module:8x10 
        module_filter = filter_dict.pop('module', None)
        if module_filter is not None: print(f"{ICONS['ERROR']} module_filter:{module_filter} is not implemented", file=sys.stderr)

        # Show modules?
        if resource.lower().startswith('mod'):
            show_resources(modules, name='modules', format=format, hide=hide, show=show)
            return

        #
        # Ports
        #

        # ports = []

        # switch : ports for switch(es) | switch:"1st floor" 
        switch_filter = filter_dict.pop('switch', None)
        if switch_filter is not None: print(f"{ICONS['ERROR']} switch_filter:{switch_filter} is not implemented", file=sys.stderr)

        # 'port', # {value} | specified ports or ranges | port:1-10  
        port_filter = filter_dict.pop('port', None)
        if port_filter is not None: print(f"{ICONS['ERROR']} port_filter:{port_filter} is not implemented", file=sys.stderr)

        # 'is',   # {[aggregated | uplink | trunk | access]}  
        is_filter = filter_dict.pop('is', None)
        if port_filter is not None: print(f"{ICONS['ERROR']} is_filter:{is_filter} is not implemented", file=sys.stderr)

        # 'vlan', # [{int}, {name}, native, voice]     
        vlan_filter = filter_dict.pop('vlan', None)
        if port_filter is not None: print(f"{ICONS['ERROR']} vlan_filter:{vlan_filter} is not implemented", file=sys.stderr)

        # 'lldp', # {value}
        lldp_filter = filter_dict.pop('lldp', None)
        if port_filter is not None: print(f"{ICONS['ERROR']} lldp_filter:{lldp_filter} is not implemented", file=sys.stderr)

        # 'link', # {value} port link type set speed/duplex | link:"100 mbps"
        link_filter = filter_dict.pop('link', None)
        if port_filter is not None: print(f"{ICONS['ERROR']} link_filter:{link_filter} is not implemented", file=sys.stderr)

        # 'ap',   # ports with specified access policy | ap:*
        ap_filter = filter_dict.pop('ap', None)
        if port_filter is not None: print(f"{ICONS['ERROR']} ap_filter:{ap_filter} is not implemented", file=sys.stderr)

        # 'schedule', # ports with specified schedule  | schedule:*
        schedule_filter = filter_dict.pop('schedule', None)
        if port_filter is not None: print(f"{ICONS['ERROR']} schedule_filter:{schedule_filter} is not implemented", file=sys.stderr)

        # 'group', # ports in common group               | group:1
        group_filter = filter_dict.pop('group', None)
        if port_filter is not None: print(f"{ICONS['ERROR']} group_filter:{group_filter} is not implemented", file=sys.stderr)

        # Show ports?
        if resource.lower().startswith('port'):
            show_resources(ports, name='ports', format=format, hide=hide, show=show)
            return

        #
        # Client
        #

        # mac: A MAC address that contains the search term or is an exact match.
        mac_filter = filter_dict.pop('mac', None)
        if port_filter is not None: print(f"{ICONS['ERROR']} mac_filter:{mac_filter} is not implemented", file=sys.stderr)

        # macs: Devices will have a MAC addresses that are an exact match.
        macs_filter = filter_dict.pop('macs', None)
        if macs_filter is not None: print(f"{ICONS['ERROR']} macs_filter:{macs_filter} is not implemented", file=sys.stderr)

        # 'mac_whitelist', # ports with mac-whitelist | mac_whitelist:aa:bb:cc:dd:ee:ff
        mac_whitelist_filter = filter_dict.pop('mac_whitelist', None)
        if mac_whitelist_filter is not None: print(f"{ICONS['ERROR']} mac_whitelist_filter:{mac_whitelist_filter} is not implemented", file=sys.stderr)

        # Show ports?
        if resource.lower().startswith('port'):
            show_resources(ports, name='ports', format=format, hide=hide, show=show)
            return

        # Any unknown or leftover filters?
        if len(filter_dict) > 0:
            [print(f"{ICONS['ERROR']} filter '{key}:{val}' is not supported", file=sys.stderr) for key,val in filter_dict.items()]

        # Unknown Resource
        print(f"{ICONS['ERROR']} Unknown resource type: {resource}", file=sys.stderr)


if __name__ == '__main__':

    # Set up the command-line argument argp
    argp = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    argp.add_argument('resource', choices=SUPPORTED_RESOURCES, help='resource type to show', type=str)
    argp.add_argument('filters', nargs='*', help=f'filter:value pairs: [{','.join(SUPPORTED_FILTERS)}]', type=str)
    argp.add_argument('-f','--format', help='output format', choices=SUPPORTED_FORMATS, default='table', required=False)
    argp.add_argument('-t','--timer', help='show execution time', required=False, action='store_true', default=False)
    argp.add_argument('-v','--verbosity', help='verbosity', required=False, action='count', default=False)
    argp.add_argument('--hide', help='attributes (columns) to hide', type=str, default=None, required=False)
    argp.add_argument('--show', help='attributes (columns) to show', type=str, default=None, required=False)
    args = argp.parse_args()

    if args.timer: start_time = time.time()
    
    if args.verbosity >= 3: print(f"args: {args}", file=sys.stderr)
    if "MERAKI_DASHBOARD_API_KEY" not in os.environ: sys.exit("You must set the MERAKI_DASHBOARD_API_KEY environment variable!")

    asyncio.run(meraki_show(resource=args.resource, filters=args.filters, format=args.format, verbosity=args.verbosity, hide=args.hide, show=args.show))

    if args.timer : print(f"\n 🕒 {time.time() - start_time} seconds\n", file=sys.stderr)
