#!/usr/bin/env python
"""
Get details about a specific ISE ERS resource.
See https://cs.co/ise-api for REST API resource names.

Usage: ise_get_ers_resource.py {resource_name}

Requires the following environment variables:
  - ise_rest_hostname : the hostname or IP address of your ISE PAN node
  - ise_rest_username : the ISE ERS admin or operator username
  - ise_rest_password : the ISE ERS admin or operator password
  - ise_verify : validate the ISE certificate (true/false)

Set the environment variables using the `export` command:
  export ise_rest_hostname='1.2.3.4'
  export ise_rest_username='admin'
  export ise_rest_password='C1sco12345'
  export ise_verify=false

You may save the export lines in a text file and source it for use:
  source ise_environment.sh

"""

import requests
import json
import os
import sys

# Silence any warnings about certificates
requests.packages.urllib3.disable_warnings()

DEBUG = 0
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


resource_name = sys.argv[1]
if resource_name not in RESOURCE_NAMES :
    print(f'❌ Invalid ISE ERS resource ({resource_name}).\nTry one of these:', file=sys.stderr)
    for resource in RESOURCE_NAMES :
        print(f'- {resource}', file=sys.stderr)
    sys.exit(1)

"""
Returns a boolean value based on the object type and value.
"""
def to_bool (o) :
    # number
    if type(o) == 'int' :
        if o > 0 : return True

    # string
    elif type(o) == 'str' :
        s = o.lower()
        # true | yes | on
        if s.startswith('t') or s.startswith('y') or s.startswith('o') :
            return True

    else :
        return False

"""
Prints debug output to stderr.
"""
def debug (s) :
    print(s, file=sys.stderr)


#
# Load Environment Variables
#
env = { k : v for (k, v) in os.environ.items() }
hostname = env['ise_rest_hostname']
username = env['ise_rest_username']
password = env['ise_rest_password']
verify = to_bool(env['ise_verify'])




#
# Get resource IDs
#
resources = []
url = 'https://'+hostname+'/ers/config/'+resource_name+'?size=100'
while (url) :
    r = requests.get(url, auth=(username, password), headers=HEADERS_JSON, verify=verify)
    if DEBUG : debug(r.text)
    resources += r.json()["SearchResult"]["resources"]
    try :
        url = r.json()["SearchResult"]["nextPage"]["href"]
    except Exception as e :
        url = None


#
# Show resource details
#
object_name = ''
details = []
for resource in resources :
    # if DEBUG : debug(resource)

    url = 'https://'+hostname+'/ers/config/'+resource_name+'/'+resource["id"]
    r = requests.get(url, auth=(username, password), headers=HEADERS_JSON, verify=verify)

    detail = r.json()
    object_name = list(detail)[0]   # save the resource name for the output
    detail = detail[object_name]
    del detail['link']    # Delete unnecessary link attribute
    if DEBUG : debug(detail)
    details.append( detail )


output = {}
output[object_name] = details
print(json.dumps(output))

if DEBUG : debug(f'Total: {len(resources)}')
