#!/usr/bin/env python3
"""
Walk the ISE ERS resource endpoints.
Get the total number of a specific ISE ERS resource.

Usage: ise_walk.py

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

import os
import requests
import sys
import time

# Silence any warnings about certificates
requests.packages.urllib3.disable_warnings()

# List of supported ISE resources
RESOURCE_NAMES = [      
    # Deployment
    'node',
    'sessionservicenode',

    # Network Devices
    'networkdevicegroup',
    'networkdevice',

    # Endpoints
    'endpointgroup',
    'endpoint',
    'endpointcert',  # POST(create) only!!!
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
]



"""
"""
def resource_count (resource) :
    LEAF = ' ┣╸'
    count = 0
    try :
        url = 'https://'+env['ise_rest_hostname']+'/ers/config/'+resource
        r = requests.get(url,
                        auth=(env['ise_rest_username'], env['ise_rest_password']),
                        headers={'Accept': 'application/json'},
                        verify=env['ise_verify'].lower().startswith('t')
                        )

        if r.status_code == 401 :
            if resource == 'guestuser' :
                print(f"{LEAF}{resource} [{count}] ⟁ requires sponsor account")
        elif r.status_code == 404 :
            print(f'{LEAF}{resource} [{count}] ⟁ Not configured')
        else :
            count = r.json()['SearchResult']['total']
            print(f'{LEAF}{resource} [{count}]')
            
    except Exception as e:
        if resource == 'endpointcert' :
            print(f"{LEAF}{resource} [{count}] ⟁ POST endpointcert only!")
        else :
            print(f"{LEAF}{resource} [{count}] ⟁ Exception ")


if __name__ == "__main__":
    """
    Entrypoint for local script.
    """

    # Load Environment Variables
    env = { k : v for (k, v) in os.environ.items() }

    print('C▶'+env['ise_rest_hostname'])
    for resource in RESOURCE_NAMES :
        resource_count(resource)
