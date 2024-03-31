#!/usr/bin/env python3
"""
Walk the ISE ERS resource endpoints.
Get the total number of a specific ISE ERS resource.

Usage: ise-walk.py

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



def resource_count (resource) :
    """
    Walk through the list of ISE Resources and count them. 
    """
    LEAF = ' ┣╸'
    count = 0
    try :
        url = 'https://'+env['ISE_HOSTNAME']+'/ers/config/'+resource
        r = requests.get(url,
                        auth=(env['ISE_REST_USERNAME'], env['ISE_REST_PASSWORD']),
                        headers={'Accept': 'application/json'},
                        verify=(False if env['ISE_CERT_VERIFY'][0:1].lower() in ['f','n'] else True)
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

    print('C▶'+env['ISE_HOSTNAME'])
    for resource in RESOURCE_NAMES :
        resource_count(resource)
