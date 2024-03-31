#!/usr/bin/env python3
"""

Show ISE REST APIs data.

Examples:
    ise-get.py endpoint 
    ise-get.py endpoint -itv
    ise-get.py endpointgroup -f csv -f endpointgroup.csv
    ise-get.py endpointgroup -f pretty --details
    ise-get.py endpointgroup -f grid --details --noid
    ise-get.py endpointgroup -f yaml
    ise-get.py allowedprotocols -f yaml -p saved --details 
    ise-get.py all --details -f yaml --save demo_config 

Requires setting the these environment variables using the `export` command:
  export ISE_HOSTNAME='1.2.3.4'         # hostname or IP address of ISE PAN
  export ISE_REST_USERNAME='admin'      # ISE ERS admin or operator username
  export ISE_REST_PASSWORD='C1sco12345' # ISE ERS admin or operator password
  export ISE_CERT_VERIFY=false          # validate the ISE certificate

You may add these export lines to a text file and load with `source`:
  source ise.sh

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
import math
import os
import random
import sys
import time
import traceback
import yaml
from tabulate import tabulate


DATA_DIR = './data'
REST_PAGE_SIZE_MAX=100
REST_PAGE_SIZE=REST_PAGE_SIZE_MAX

# Limit TCP connection pool size to prevent connection refusals by ISE
# See https://cs.co/ise-scale for Concurrent ERS Connections.
# Testing with ISE 3.x shows no performance gain for >5-10 connections.
TCP_LIMIT_DEFAULT=100 # aiohttp.TCPConnector.limit
TCP_LIMIT=10  # 🔺ISE ERS APIs for GuestType and InternalUser can have problems with 10+ concurrent connections!

# Dictionary of ISE REST Endpoints mapping to a tuple of the object name and base URL
ISE_REST_ENDPOINTS = {
    #
    # '{resource}': '( {object_name}, {api_resource_path} )',
    #
    # Deployment @ https://cs.co/ise-api#!deployment-openapi
    'deployment-node': ('-', '/api/v1/deployment/node'),
    'node-group': ('-', '/api/v1/deployment/node-group'),
    'pan-ha': ('-', '/api/v1/deployment/pan-ha'),
    # 'node-interface': ('-', '/api/v1/node/{hostname}/interface'), # 💡 requires ISE node hostname
    # 'sxp-interface': ('-', '/api/v1/node/{hostname}/sxp-interface'), # 💡 requires ISE node hostname
    # 'profile': ('-', '/api/v1/profile/{hostname}'), # 💡 requires ISE node hostname
    'repository': ('-', '/api/v1/repository'), # Repository @ https://cs.co/ise-api#!repository-openapi
    # 'repository-name': ('-', '/api/v1/repository/{name}'), # 💡 requires repository {name}
    # 'repository-name-files': ('-', '/api/v1/repository/{name}/files'),# 💡 requires repository {name}
    # Patching @ https://cs.co/ise-api#!patch-and-hot-patch-openapi
    'hotpatch': ('-', '/api/v1/hotpatch'),
    'patch': ('-', '/api/v1/patch'),
    # DeploymentInfo @ https://cs.co/ise-api#!deploymentinfo 
    # 'info': ('ERSDeploymentInfo', '/deploymentinfo/getAllInfo'),  # 'deploymentinfo'=> deploymentinfo/getAllInfo
    'node': ('Node', '/ers/config/node'), # Node @ https://cs.co/ise-api#!node
    # 'service': ('Service', '/ers/config/service'),  # 🛑 empty resource; link:service/null gives 404
    'sessionservicenode': ('SessionServiceNode', '/ers/config/sessionservicenode'),
    # Certificates @ https://cs.co/ise-api#!certificate-openapi
    'trusted-certificate': ('-', '/api/v1/certs/trusted-certificate'), # Get list of all trusted certificates
    # 'trusted-certificate-by-id': ('-', '/api/v1/certs/trusted-certificate/{id}'), # Get Trust Certificate By ID
    # 'system-certificate': ('-', '/api/v1/certs/system-certificate/{hostName}'), # 💡 requires ISE node hostname
    'certificate-signing-request': ('-', '/api/v1/certs/certificate-signing-request'),
    # 'system-certificate-by-name': ('-', '/api/v1/certs/system-certificate/{hostName}'), # 💡 requires ISE node hostname. Get all system certificates of a particular node
    # Backup Restore
    'last-backup-status': ('-', '/api/v1/backup-restore/config/last-backup-status'),

    # Upgrade
    'upgrade-prepare-status': ('-', '/api/v1/upgrade/prepare/get-status'),
    'upgrade-proceed-status': ('-', '/api/v1/upgrade/proceed/get-status'),
    'upgrade-stage-status': ('-', '/api/v1/upgrade/stage/get-status'),
    'upgrade-summary-status': ('-', '/api/v1/upgrade/summary/get-status'),

    # System Settings
    'lsd': ('-', '/api/v1/lsd/updateLsdSettings'), # LSD
    'settings-proxy': ('-', '/api/v1/system-settings/proxy'),
    'settings-ttg': ('-', '/api/v1/system-settings/telemetry/transport-gateway'),
    # Data Connect @ https://cs.co/ise-dataconnect
    'data-connect-details': ('-', '/api/v1/mnt/data-connect/details'),
    'data-connect-settings': ('-', '/api/v1/mnt/data-connect/settings'),

    # Identity Stores
    'activedirectory': ('ERSActiveDirectory', '/ers/config/activedirectory'),
    'restidstore': ('ERSRestIDStore', '/ers/config/restidstore'),  # RESTIDStore must be enabled / 404 if none configured
    # LDAP @ https://cs.co/ise-api#!ldap
    # 'ldap': ('???', '/ers/config/ldap'), # 404 if unconfigured?
    # 'ldap-rootcacertificates': ('???', '/ers/config/ldap/rootcacertificates'),
    # 'ldap-hosts': ('???', '/ers/config/ldap/hosts'),
    # 'ldap-by-name': ('???', '/ers/config/ldap/name/{name}'),
    # 'ldap-by-id': ('???', '/ers/config/ldap/{id}'),
    # Duo MFA
    'duo-sync-ads': ('-', '/api/v1/duo-identitysync/activedirectories'), # Get the list of all configured Active Directories
    # 'duo-sync-groups': ('-', '/api/v1/duo-identitysync/adgroups/{activeDirectory}'), # 💡 requires id for a list of all groups in the specified AD
    'duo-identitysync': ('-', '/api/v1/duo-identitysync/identitysync'), # Get the list of all Identitysync configurations
    'duo-mfa': ('-', '/api/v1/duo-mfa/mfa'), # Get the list of all Duo-MFA configurations
    # 'duo-mfa-enable': ('-', '/api/v1/duo-mfa/enable'), # PUT Enable MFA feature
    # 'duo-mfa-by-name': ('-', '/api/v1/duo-mfa/mfa/{connectionName}'), # Get the specified Duo-MFA configuration
    'duo-mfa-status': ('-', '/api/v1/duo-mfa/status'), # MFA feature enabled status
    # pxGrid Direct @ https://cs.co/ise-api#!pxgrid-direct-open-api
    'pxgd-config': ('-', '/api/v1/pxgrid-direct/connector-config'), 
    # 'pxgd-config-by-name': ('-', '/api/v1/pxgrid-direct/connector-config/{name}'),
    'pxgd-references': ('-', '/api/v1/pxgrid-direct/dictionary-references'),
    'externalradiusserver': ('ExternalRadiusServer', '/ers/config/externalradiusserver'),
    'radiusserversequence': ('RadiusServerSequence', '/ers/config/radiusserversequence'),
    'idstoresequence': ('IdStoreSequence', '/ers/config/idstoresequence'),

    # Network Devices
    'networkdevicegroup': ('NetworkDeviceGroup', '/ers/config/networkdevicegroup'),
    'networkdevice': ('NetworkDevice', '/ers/config/networkdevice'), # 

    # TrustSec
    'sgt': ('Sgt', '/ers/config/sgt'),
    'sgacl': ('Sgacl', '/ers/config/sgacl'),
    'sgmapping': ('SGMapping', '/ers/config/sgmapping'),
    'sgmappinggroup': ('SGMappingGroup', '/ers/config/sgmappinggroup'),
    'sgtvnvlan': ('SgtVNVlanContainer', '/ers/config/sgtvnvlan'),
    'egressmatrixcell': ('EgressMatrixCell', '/ers/config/egressmatrixcell'),
    'sxpconnections': ('ERSSxpConnection', '/ers/config/sxpconnections'),
    'sxplocalbindings': ('ERSSxpLocalBindings', '/ers/config/sxplocalbindings'),
    'sxpvpns': ('ERSSxpVpn', '/ers/config/sxpvpns'),
    'sgt-reservation': ('-', '/api/v1/sgt/reservation'), # SgtRangeReservation @ https://cs.co/ise-api#!sgt-reservation-openapi
    # 'sgt-reservation-by-id': ('-', '/api/v1/sgt/reservation/{clientID}'), # 💡 Requires {id}. Get the reserved range for the specific Client.

    # SDA/TrustSec @ https://cs.co/ise-api#!trustsec-openapi
    'trustsec-sgacl-nbarapp': ('-', '/api/v1/trustsec/sgacl/nbarapp'),
    'trustsec-sgvnmapping': ('-', '/api/v1/trustsec/sgvnmapping'),
    'trustsec-virtualnetwork': ('-', '/api/v1/trustsec/virtualnetwork'),
    'trustsec-vnvlanmapping': ('-', '/api/v1/trustsec/vnvlanmapping'),
    'profilerprofile': ('ProfilerProfile', '/ers/config/profilerprofile'), # Endpoint Profiles @ https://cs.co/ise-api#!profilerprofile

    # Endpoints
    'endpointgroup': ('EndPointGroup', '/ers/config/endpointgroup'), # EndpointGroups @ https://cs.co/ise-api#!endpointgroup
    'endpoint-custom-attribute': ('-', '/api/v1/endpoint-custom-attribute'),
    # 'endpoint-custom-attribute-by-name': ('-', '/api/v1/endpoint-custom-attribute/{name}'), # Get custom attribute by name
    # 'endpoint-stop-replication': ('-', '/api/v1/stop-replication'),    # Endpoint Stop Replication Service
    'endpoint': ('ERSEndPoint', '/ers/config/endpoint'), # Endpoint @ https://cs.co/ise-api#!endpoint
    # 'endpointcert': ('ERSEndPointCert', '/ers/config/endpointcert'),  # 🛑 No GET; POST only
    'endpoints': ('-', '/api/v1/endpoint'), # 💡 Requires ISE 3.2. Endpoints @ https://cs.co/ise-api#!get-all-endpoints
    # 'endpoint-value': ('-', '/api/v1/endpoint/{value}'), # 💡 Requires {value}
    # 'endpoint-summary': ('-', '/api/v1/endpoint/deviceType/summary'), # 🛑 404?

    # TACACS+
    'tacacscommandsets': ('TacacsCommandSets', '/ers/config/tacacscommandsets'),    # TACACS @ https://cs.co/ise-api#!tacacscommandsets
    'tacacsexternalservers': ('TacacsExternalServer', '/ers/config/tacacsexternalservers'),  # 💡 404 if none configured. TACACS @ https://cs.co/ise-api#!tacacsexternalservers
    'tacacsprofile': ('TacacsProfile', '/ers/config/tacacsprofile'),    # TACACS @ https://cs.co/ise-api#!tacacsprofile
    'tacacsserversequence': ('TacacsServerSequence', '/ers/config/tacacsserversequence'),  # 💡 404 if none configured. TACACS @ https://cs.co/ise-api#!tacacsserversequence

    # Policy Sets - RADIUS Network Access
    # ERS policy elements
    'allowedprotocols': ('AllowedProtocols', '/ers/config/allowedprotocols'),
    'authorizationprofile': ('AuthorizationProfile', '/ers/config/authorizationprofile'),
    'downloadableacl': ('DownloadableAcl', '/ers/config/downloadableacl'),
    'filterpolicy': ('ERSFilterPolicy', '/ers/config/filterpolicy'),  # 404 if none configured
    # Network Access Policy @ https://cs.co/ise-api#!policy-openapi
    # ⓘ Network Access policy is the assumed default; prefix "na-" not required
    'na-authorization-profiles': ('-', '/api/v1/policy/network-access/authorization-profiles'),
    # 'condition-id': ('-', '/api/v1/policy/network-access/condition/{conditionId}'),
    'na-condition-policyset': ('-', '/api/v1/policy/network-access/condition/policyset'),
    'na-condition-authn': ('-', '/api/v1/policy/network-access/condition-authentication'),
    'na-condition-authz': ('-', '/api/v1/policy/network-access/condition-authorization'),
    'na-dicts': ('-', '/api/v1/policy/network-access/dictionaries'),
    # 'dict-name': ('-', '/api/v1/policy/network-access/dictionaries/{name}'), # 💡 Requires {name}
    'na-dict-authn': ('-', '/api/v1/policy/network-access/dictionaries/authentication'),
    'na-dict-authz': ('-', '/api/v1/policy/network-access/dictionaries/authorization'),
    'na-dict-policyset': ('-', '/api/v1/policy/network-access/dictionaries/policyset'),
    'na-identity-stores': ('-', '/api/v1/policy/network-access/identity-stores'),
    'na-network-condition': ('-', '/api/v1/policy/network-access/network-condition'),
    'na-policy-set': ('-', '/api/v1/policy/network-access/policy-set'),
    # 'policy-set-id': ('-', '/api/v1/policy/network-access/policy-set/{id}'),
    # 'policy-set-id-authn': ('-', '/api/v1/policy/network-access/policy-set/{policyId}/authentication'),
    # 'policy-set-id-authz': ('-', '/api/v1/policy/network-access/policy-set/{policyId}/authorization'),
    # 'policy-set-id-exception': ('-', '/api/v1/policy/network-access/policy-set/{policyId}/exception'),
    'na-global-exception': ('-', '/api/v1/policy/network-access/policy-set/global-exception'),
    'na-security-groups': ('-', '/api/v1/policy/network-access/security-groups'),
    'na-service-names': ('-', '/api/v1/policy/network-access/service-names'),
    'na-time-condition': ('-', '/api/v1/policy/network-access/time-condition'),

    # Policy Sets - TACACS+ Device Admin @ https://cs.co/ise-api#!policy-openapi
    # ⓘ All Device Admin policy objects have the prefix "da-"
    'da-command-sets': ('-', '/api/v1/policy/device-admin/command-sets'),
    'da-condition': ('-', '/api/v1/policy/device-admin/condition'),
    # 'da-condition-id': ('-', '/api/v1/policy/device-admin/condition/{conditionId}'),
    'da-condition-policyset': ('-', '/api/v1/policy/device-admin/condition/policyset'),
    'da-condition-authn': ('-', '/api/v1/policy/device-admin/condition-authentication'),
    'da-condition-authz': ('-', '/api/v1/policy/device-admin/condition-authorization'),
    'da-dict-authn': ('-', '/api/v1/policy/device-admin/dictionaries/authentication'),
    'da-dict-authz': ('-', '/api/v1/policy/device-admin/dictionaries/authorization'),
    'da-dict-policyset': ('-', '/api/v1/policy/device-admin/dictionaries/policyset'),
    'da-identity-stores': ('-', '/api/v1/policy/device-admin/identity-stores'),
    'da-policy-set': ('-', '/api/v1/policy/device-admin/policy-set'),
    # 'da-policy-set-id': ('-', '/api/v1/policy/device-admin/policy-set/{id}'), # 💡 requires {id}
    'da-global-exception': ('-', '/api/v1/policy/device-admin/policy-set/global-exception'),
    'da-service-names': ('-', '/api/v1/policy/device-admin/service-names'),
    'da-shell-profiles': ('-', '/api/v1/policy/device-admin/shell-profiles'),
    'da-time-condition': ('-', '/api/v1/policy/device-admin/time-condition'),

    # Users
    'adminuser': ('AdminUser', '/ers/config/adminuser'),
    'identitygroup': ('IdentityGroup', '/ers/config/identitygroup'),
    'internaluser': ('InternalUser', '/ers/config/internaluser'),

    # Guest Portals
    'portal': ('ERSPortal', '/ers/config/portal'),
    'portalglobalsetting': ('PortalCustomizationGlobalSetting', '/ers/config/portalglobalsetting'),
    'portaltheme': ('PortalTheme', '/ers/config/portaltheme'),
    'hotspotportal': ('HotspotPortal', '/ers/config/hotspotportal'),
    'selfregportal': ('SelfRegPortal', '/ers/config/selfregportal'),
    'sponsorportal': ('SponsorPortal', '/ers/config/sponsorportal'),
    'sponsoredguestportal': ('SponsoredGuestPortal', '/ers/config/sponsoredguestportal'),
    # 'guestlocation': ('LocationIdentification', '/ers/config/guestlocation'),
    'guestsmtpnotificationsettings': ('ERSGuestSmtpNotificationSettings', '/ers/config/guestsmtpnotificationsettings'),
    'guestssid': ('GuestSSID', '/ers/config/guestssid'),
    'guesttype': ('GuestType', '/ers/config/guesttype'), # 🛑 500 internal errors?
    # 'guestuser': ('GuestUser', '/ers/config/___GuestUser__'), # 🛑 requires sponsor account!!!
    # 'smsprovider': ('SmsProviderIdentification', '/ers/config/smsprovider'),
    'sponsorgroup': ('SponsorGroup', '/ers/config/sponsorgroup'),
    'sponsorgroupmember': ('SponsorGroupMember', '/ers/config/sponsorgroupmember'),

    # BYOD
    'certificateprofile': ('CertificateProfile', '/ers/config/certificateprofile'),
    'certificatetemplate': ('ERSCertificateTemplate', '/ers/config/certificatetemplate'),
    'byodportal': ('BYODPortal', '/ers/config/byodportal'),
    'mydeviceportal': ('MyDevicePortal', '/ers/config/mydeviceportal'),
    'nspprofile': ('ERSNSPProfile', '/ers/config/nspprofile'),
    'ipsec': ('ipsec', '/api/v1/ipsec'), # IPsec @ https://cs.co/ise-api#!ipsec-openapi
    # 'ipsec': ('ipsec', '/api/v1/ipsec/{hostName}/{nadIp}'),
    'ipsec-certificates': ('ipsec-certificates','/api/v1/ipsec/certificates'),
    # Support / Operations
    # 'supportbundle': ('_____', '/ers/config/supportbundle'),
    # 'supportbundledownload': ('_____', '/ers/config/_____'),
    # 'supportbundlestatus': ('_____', '/ers/config/_____'),
    # Task
    'task': ('-', '/api/v1/task'),
    # 'task-id': ('-', '/api/v1/task/{id}'),

    # pxGrid / ANC / RTC / TC-NAC @ https://github.com/cisco-pxgrid/pxgrid-rest-ws/wiki
    # 'pxgridsettings': ('PxgridSettings', '/ers/config/pxgridsettings/autoapprove'), # 🛑 PUT only; GET not supported!
    # 'pxgridnode': ('pxGridNode', '/ers/config/pxgridnode'),  # 🛑 🐛 404 always whether pxGrid is enabled or not
    'ancendpoint': ('ErsAncEndpoint', '/ers/config/ancendpoint'),    # ANCEndpoint @ https://cs.co/ise-api#!ancendpoint

    'ancpolicy': ('ErsAncPolicy', '/ers/config/ancpolicy'), # ANCPolicy @ https://cs.co/ise-api#!ancpolicy
    # 'ancpolicy-version': ('VersionInfo', '/ers/config/ancpolicy/versioninfo'), # 💡 No `SearchResult`, only `VersionInfo` object. Get ANC policy version information
    # 'clearThreatsAndVulneribilities': ('ERSIrfThreatContext', '/ers/config/threat/clearThreatsAndVulneribilities'),  # 🛑 PUT only; GET not supported! @ https://cs.co/ise-api#!clearThreatsAndVulneribilities
    'telemetryinfo': ('TelemetryInfo', '/ers/config/telemetryinfo'), # Telemetry @ https://cs.co/ise-api#!telemetryinfo
    # 'acibindings': ('ACIBindings', '/ers/config/acibindings/getall'), # ACI @ https://cs.co/ise-api#!acibindings
    # 'acisettings': ('AciSettings', '/ers/config/acisettings'), # ACI @ https://cs.co/ise-api#!acisettings
    # Operations
    # 'op': ('_____', '/ers/config/_____'),
    # 'op/systemconfig': ('_____', '/ers/config/_____'),
    # 'op/systemconfig/iseversion': ('_____', '/ers/config/_____'),
    # License
    'license-system-smart-state': ('-', '/api/v1/license/system/smart-state'),
    'license-system-register': ('-', '/api/v1/license/system/register'),
    'license-system-tier-state': ('-', '/api/v1/license/system/tier-state'),
    'license-system-eval-license': ('-', '/api/v1/license/system/eval-license'),
    'license-system-connection-type': ('-', '/api/v1/license/system/connection-type'),
    'license-system-feature-to-tier-mapping': ('-', '/api/v1/license/system/feature-to-tier-mapping'),

    # FiveG
    # '': ('-', ''),

}


def show(resources=None, name=None, filepath='-', format='json'):
    """
    Show/print/dump the resources in the specified format to the file. `sys.stdout` ('-') by default.

    - resources ([dict]) : a list of dictionary items to format
    - name (str) : the name of the resource. Example: endpoint, sgt, etc.
    - format (str): one the following formats:
        - `csv`   : Show the items in a Comma-Separated Value (CSV) format
        - `grid`  : Show the items in a table grid with borders
        - `table` : Show the items in a text-based table
        - `id`    : Show only the id column for the objects (if available)
        - `json`  : Show the items as a single JSON string
        - `line`  : Show the items as JSON with each item on it's own line
        - `pretty`: Show the items as JSON pretty-printed with 2-space indents
        - `yaml`  : Show the items as YAML with 2-space indents
    - filepath (str) : Default: `sys.stdout`
    """
    if resources == None: return
    object_type = None if len(resources) <= 0 else type(resources[0]) 
    if args.verbosity >= 3: print(f"▷ show({len(resources)} x '{name}' as {format} to {filepath})", file=sys.stderr)

    # 💡 Do not close sys.stdout or it may not be re-opened with multiple show() calls
    fh = sys.stdout if filepath == '-' else open(filepath, 'w') # write to sys.stdout/terminal by default

    if format == 'csv':  # CSV
        headers = {}
        [headers.update(r) for r in resources]  # find all unique keys
        writer = csv.DictWriter(fh, headers.keys(), quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        for row in resources:
            writer.writerow(row)
    elif format == 'id':  # list of ids only
        ids = [[r['id']] for r in resources]  # single column table
        print(f"{tabulate(ids, tablefmt='plain')}", file=fh)
    elif format == 'grid': # grid
        print(f"{tabulate(resources, headers='keys', tablefmt='simple_grid')}", file=fh)
    elif format == 'table': # table
        print(f"{tabulate(resources, headers='keys', tablefmt='table')}", file=fh)
    elif format == 'json':  # JSON, one long string
        print(json.dumps({ name: resources }), file=fh)
    elif format == 'line':  # 1 JSON line per object
        print('{')
        print(f'{name} = [')
        [print(json.dumps(r), end=',\n', file=fh) for r in resources]
        print(']\n}')
    elif format == 'pretty':  # pretty-print
        print(json.dumps({ name: resources }, indent=2), file=fh)
    elif format == 'yaml':  # YAML
        print(yaml.dump({ name: resources }, indent=2, default_flow_style=False), file=fh)
    else:  # just in case something gets through the CLI parser
        print(f' 🛑 Unknown format: {format}', file=sys.stderr)


async def get_ise_ers_resources (session:aiohttp.ClientSession=None, urlpath:str=None, details:bool=False):
    """
    Return the resources from the JSON response.
    - session (aiohttp.ClientSession): the aiohttp session to reuse
    - urlpath (str): the REST endpoint path.
    - details (bool): return endpoint details
    """
    async with session.get(urlpath) as response:
        if args.verbosity: print('.', end='', file=sys.stderr, flush=True) # print '.' for progress
        data = await response.json()
        return data if details else data['SearchResult']['resources']


async def ise_get (session:aiohttp.ClientSession=None, ers_name:str=None, urlpath:str=None, details:bool=False):
    """
    Return the specified resources from ISE.

    - session (aiohttp.ClientSession): the aiohttp session to reuse
    - ers_name (str) : the ERS object name.
    - urlpath (str): the REST endpoint path.
    - details (bool): True to get all object details, False otherwise
    """
    if args.verbosity: print(f"▷ ise_get {ers_name} ({urlpath})", end=' ', file=sys.stderr, flush=True)
    resources = []
    response = await session.get(f"{urlpath}") # Get the first page for the `total` resources
    data = await response.json()
    try:
        if urlpath.startswith('/ers'): # ERS is a dict: {'SearchResult': {'total': 7, 'resources': [{'id': ...
            total = data['SearchResult']['total']
            if args.verbosity: print(f"[{total}]", end=' ', file=sys.stderr, flush=True)

            # Get all resources if more than the REST page size
            urls = [f"{urlpath}?size={REST_PAGE_SIZE}&page={page}" for page in range(1, 1+int(total/REST_PAGE_SIZE)+(1 if total%REST_PAGE_SIZE else 0))] # Generate paging URLs
            tasks = [asyncio.ensure_future(get_ise_ers_resources(session, url)) for url in urls]
            responses = await asyncio.gather(*tasks)
            [resources.extend(response) for response in responses]

            if total > 0 and details and ers_name != 'SponsorGroupMember': # 🔺 There is no GET by ID for /ers/config/sponsorgroupmember
                uuids = [r['id'] for r in resources] # Extract UUIDs from summary resources
                urls = [f"{urlpath}/{uuid}" for uuid in uuids] # Generate resource URLs
                tasks = [asyncio.ensure_future(get_ise_ers_resources(session, url, details)) for url in urls]
                responses = await asyncio.gather(*tasks)
                # if ers_name == 'GuestType': await asyncio.sleep(1)  # 💡 There is a conconcurrency issue with GuestType resources. 
                resources = [response[ers_name] for response in responses]

        elif urlpath.startswith('/api'): # OpenAPI is a list [] *or* dict with a list: {'response': [{'id': ...
            if isinstance(data, list):  # list of resources Example: endpoints
                resources = data
            elif isinstance(data, dict):
                if data.get('response'): # 'response' key to resources list?
                    resources = data['response']   # response contains a list of resources
                else: # the data is the object. Example: hotpatch, patch, etc.
                    resources = data
        else:
            if args.verbosity: print(f"Unknown ISE urlpath: {urlpath})", file=sys.stderr)
            resources = data
    except Exception as e:
        tb_text = '\n'.join(traceback.format_exc().splitlines()[1:]) # remove 'Traceback (most recent call last):'
        print(f"💣 {e.__class__} {urlpath} | {data} | {tb_text}", file=sys.stderr) # {urlpath} | {url} | {data} |  {response.status} {request.method} {request.path}
    finally:
        if args.verbosity: print(file=sys.stderr, flush=True) # send a newline after the outputs

    # remove ugly 'link' attribute to flatten data
    for r in resources:
        if type(r) == dict and r.get('link'): 
            del r['link']
    return resources


async def get(session:aiohttp.ClientSession=None, resource:str=None, details:bool=False, filepath:str=None, format:str=None, noid:bool=True):
    """
    Entrypoint for packaged script.
    """

    resources = []
    try:
        # Create HTTP session
        env = {k:v for (k, v) in os.environ.items() if k.startswith('ISE_')}  # Load environment variables
        verify_ssl = (False if env['ISE_CERT_VERIFY'][0:1].lower() in ['f','n'] else True)
        tcp_conn = aiohttp.TCPConnector(limit=TCP_LIMIT, limit_per_host=TCP_LIMIT, ssl=verify_ssl) # limit default: 100
        auth = aiohttp.BasicAuth(login=env['ISE_REST_USERNAME'], password=env['ISE_REST_PASSWORD'])
        base_url = f"https://{env['ISE_HOSTNAME']}"
        headers = {'Accept':'application/json', 'Content-Type':'application/json'}
        session = aiohttp.ClientSession(base_url, auth=auth, connector=tcp_conn, headers=headers)

        # map the REST endpoint to the ERS object name and URL
        (ers_name, urlpath) = ISE_REST_ENDPOINTS.get(resource, (None, None))
        if urlpath:
            resources = await ise_get(session, ers_name, urlpath, details)

            if noid and isinstance(resources[0], dict): # remove id from resource dict?
                for r in resources: del r['id']

            if isinstance(resources, dict): resources = [ resources ]
            if filepath and filepath != '-':
                if not os.path.exists(filepath): os.makedirs(filepath)
                filename = '.'.join([resource, format])
                filepath = os.path.join(filepath,filename)
            show(resources, resource, filepath, format)
        else:
            print(f"\nUnknown resource: {resource}\n", file=sys.stderr)
            # print(f"Supported API objects:\n{', '.join(ISE_REST_ENDPOINTS.keys())}\n", file=sys.stderr)
            print(f"Did you mean: {', '.join(filter(lambda x: x.startswith(resource[0:3]), ISE_REST_ENDPOINTS.keys()))}\n", file=sys.stderr)
    except aiohttp.ContentTypeError as e:
        print(f"\n❌ Error: {e.message}\n\n💡Enable the ISE REST APIs\n")
    except aiohttp.ClientConnectorError as e:  # cannot connect to host
        print(f"\n❌ Host unreachable: {e}\n", file=sys.stderr)
    except:                                    # catch *all* exceptions
        print(f"\n❌ Exception: {e}\n", file=sys.stderr)
    finally:
        await session.close()


if __name__ == '__main__':
    """
    Command line script invocation.
    """
    global args     # promote to global scope for use in other functions
    argp = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)  # Keep __doc__ format
    argp.add_argument('resource', type=str, help='resource name')
    argp.add_argument('--noid', action='store_true', default=False, dest='noid', help='hide object UUIDs')
    argp.add_argument('-s', '--save', default='-', required=False, help='Save output to directory. Default: stdout')
    argp.add_argument('-d', '--details', action='store_true', default=False, help='Get resource details')
    argp.add_argument('-i', '--insecure', action='store_true', default=False, help='ignore cert checks')
    argp.add_argument('-f', '--format', choices=['csv', 'id', 'grid', 'table', 'json', 'line', 'pretty', 'yaml'], default='pretty')
    argp.add_argument('-t', '--timer', action='store_true', default=False, help='show response timer' )
    argp.add_argument('-v', '--verbosity', action='count', default=0, help='Verbosity; multiple allowed')
    args = argp.parse_args()

    if args.verbosity >= 2: print(f"ⓘ details: {args.details}", file=sys.stderr)
    if args.verbosity >= 2: print(f"ⓘ save: {args.save}", file=sys.stderr)
    if args.verbosity >= 2: print(f"ⓘ insecure: {args.insecure}", file=sys.stderr)
    if args.verbosity >= 2: print(f"ⓘ format: {args.format}", file=sys.stderr)
    if args.verbosity >= 2: print(f"ⓘ noid: {args.noid}", file=sys.stderr)
    if args.verbosity >= 2: print(f"ⓘ timer: {args.timer}", file=sys.stderr)
    if args.verbosity >= 2: print(f"ⓘ verbosity: {args.verbosity}", file=sys.stderr)
    if args.timer: start_time = time.time()

    if args.resource.lower() == 'all':
        for resource in ISE_REST_ENDPOINTS.keys():
            asyncio.run(get(resource=resource, details=args.details, filepath=args.save, format=args.format, noid=args.noid))
    else:
        asyncio.run(get(resource=args.resource, details=args.details, filepath=args.save, format=args.format, noid=args.noid))

    if args.timer: print(f"⏲ {len(resources)} {args.resource} in {'{0:.3f}'.format(time.time() - start_time)} seconds", file=sys.stderr)
