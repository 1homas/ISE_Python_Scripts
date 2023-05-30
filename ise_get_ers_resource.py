#!/usr/bin/env python3
#------------------------------------------------------------------------------
# @author: Thomas Howard
# @email: thomas@cisco.com
#------------------------------------------------------------------------------

import argparse
import requests
import json
import os
import sys


# Globals
USAGE = """
Get details about a specific ISE ERS resource. See https://cs.co/ise-api for REST API resource names.

Requires setting the these environment variables using the `export` command:
  export ISE_HOSTNAME='1.2.3.4'         # hostname or IP address of ISE PAN
  export ISE_REST_USERNAME='admin'      # ISE ERS admin or operator username
  export ISE_REST_PASSWORD='C1sco12345' # ISE ERS admin or operator password
  export ISE_CERT_VERIFY=false          # validate the ISE certificate

You may add these export lines to a text file and load with `source`:
  source ise.sh

"""

DEBUG = 0
ISE_PAGING_MAX=100
HEADERS_JSON = { 'Accept': 'application/json' }
RESOURCE_NAMES = [      # List of supported ISE resources
    # Deployment
    'deploymentinfo/getAllInfo',    # 'deploymentinfo'=> deploymentinfo/getAllInfo
    'node',
    # 'service',    # 🛑 empty resource; link:service/null gives 404
    'sessionservicenode',

    # Network Devices
    'networkdevice',
    'networkdevicegroup',

    # Endpoints
    'endpoint',
    # 'endpointcert',  # POST(create) only!!!
    'endpointgroup',
    'profilerprofile',

    # RADIUS Authentications
    'activedirectory',
    'allowedprotocols',
    'adminuser',
    'identitygroup',
    'internaluser',
    'externalradiusserver',
    'radiusserversequence',
    'idstoresequence',
    'restidstore',  # RESTIDStore must be enabled / 404 if not configured

    # RADIUS Authorizations / Policy
    'authorizationprofile',
    'downloadableacl',
    'filterpolicy',  # 404 if none configured

    # Portals
    'portal',
    'portalglobalsetting',
    'portaltheme',
    'hotspotportal',
    'selfregportal',

    # Guest
    'guestlocation',
    'guestsmtpnotificationsettings',
    'guestssid',
    'guesttype',
    'guestuser',          # 🛑 requires sponsor account!!!
    'smsprovider',
    'sponsorportal',
    'sponsoredguestportal',
    'sponsorgroup',
    'sponsorgroupmember',

    # BYOD
    'certificateprofile',
    'certificatetemplate',
    'byodportal',
    'mydeviceportal',
    'nspprofile',

    # SDA
    'sgt',
    'sgacl',
    'sgmapping',
    'sgmappinggroup',
    'sgtvnvlan',
    'egressmatrixcell',
    'sxpconnections',
    'sxplocalbindings',
    'sxpvpns',

    # TACACS
    'tacacscommandsets',
    'tacacsexternalservers',  # 404 if none configured
    'tacacsprofile',
    'tacacsserversequence',  # 404 if none configured

    # pxGrid / ANC / RTC / TC-NAC
    # 'pxgridnode',  # 🐛 🛑 404 always whether pxGrid is enabled or not
    'ancendpoint',
    'ancpolicy',

    # ACI
    'acibindings/getall',
    'acisettings',

    # Operations
    'op/systemconfig/iseversion',
]


def to_bool (o) :
    """
    Returns a boolean value based on the object type and value.
    """
    # number
    if type(o) == 'int' :
        if o > 0 : return True

    # string
    elif type(o) == 'str' :
        s = o.lower()
        # true | yes | on
        if s[0:1].lower() in ['t','y','o'] : # true/yes/on
            return True

    else :
        return False


def debug (s) :
    """
    Prints debug output to stderr.
    """
    print(s, file=sys.stderr)


def parse_cli_arguments () :
    """
    Parse the command line arguments
    """
    
    ARGS = argparse.ArgumentParser(
            description=USAGE,
            formatter_class=argparse.RawDescriptionHelpFormatter,   # keep my format
            )
    ARGS.add_argument(
            'resource', action='store', default=None, 
            help='ISE API endpoint name',
            )
    ARGS.add_argument(
            '--verbose', '-v', action='count', default=0,
            help='Verbosity',
            )

    return ARGS.parse_args()


def main () :

    global args     # promote to global scope for use in other functions
    args = parse_cli_arguments()
    
    if args.verbose >= 3 : print(f"ⓘ Args: {args}")
    # if args.verbose : print(f"ⓘ TCP_CONNECTIONS: {TCP_CONNECTIONS}")
    # if args.verbose : print(f"ⓘ REST_PAGE_SIZE: {REST_PAGE_SIZE}")

    requests.packages.urllib3.disable_warnings()    # Silence any warnings about certificates

    resource_name = args.resource
    if resource_name not in RESOURCE_NAMES :
        if args.verbose : print("ⓘ ❌ Invalid ISE ERS resource ({resource_name}).\nTry one of these:", file=sys.stderr)
        for resource in RESOURCE_NAMES :
            if args.verbose : print("ⓘ - {resource}", file=sys.stderr)
        sys.exit(1)

    # Load Environment Variables
    env = { k : v for (k, v) in os.environ.items() if k.startswith('ISE_') }
    hostname = env['ISE_HOSTNAME']
    username = env['ISE_REST_USERNAME']
    password = env['ISE_REST_PASSWORD']
    verify = (True if env['ISE_CERT_VERIFY'][0:1].lower() in ['t','y','o'] else False)

    # Get resource IDs
    resources = []
    url = f"https://{hostname}/ers/config/{resource_name}?size={ISE_PAGING_MAX}"
    if args.verbose : print("ⓘ URL: {url}")

    while (url) :
        r = requests.get(url, auth=(username, password), headers=HEADERS_JSON, verify=verify)
        if DEBUG : debug(r.text)
        resources += r.json()["SearchResult"]["resources"]
        try :
            url = r.json()["SearchResult"]["nextPage"]["href"]
        except Exception as e :
            url = None

    if args.verbose : print(f"ⓘ Got {len(resources)} resources")
    if args.verbose : print(f"ⓘ Getting details...")

    # Show resource details
    object_name = ''
    details = []
    for resource in resources :
        # if DEBUG : debug(resource)

        url = f"https://{hostname}/ers/config/{resource_name}/{resource['id']}"
        if args.verbose : print("ⓘ URL: {url}")
        r = requests.get(url, auth=(username, password), headers=HEADERS_JSON, verify=verify)

        detail = r.json()
        object_name = list(detail)[0]   # save the resource name for the output
        detail = detail[object_name]
        del detail['link']    # Delete unnecessary link attribute
        if DEBUG : debug(detail)
        details.append( detail )


    output = {}
    output[object_name] = details
    if args.verbose : print("ⓘ {json.dumps(output, indent=2)}")
    if args.verbose : print("ⓘ Total: {len(resources)}")



if __name__ == '__main__':     # Runs main() if file wasn't imported.  
    main()
