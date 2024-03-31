#!/usr/bin/env python3
"""
Delete ISE resources via REST APIs.

Examples:
    ise-delete.py endpoint 
    ise-delete.py endpoint -tv
    ise-delete.py -v endpoint,endpointgroup,identitygroup,internaluser,networkdevicegroup,networkdevice

Requires setting the these environment variables using the `export` command:
  export ISE_PPAN='1.2.3.4'             # hostname or IP address of ISE Primary PAN
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
import os
import random
import signal
import sys
import time
import traceback
import yaml
import math
from tabulate import tabulate

WORKER_COUNT = 20
DATA_DIR = './'

# REST Options
JSON_HEADERS = {'Accept':'application/json', 'Content-Type':'application/json'}
REST_PAGE_SIZE_MAX=100
REST_PAGE_SIZE=REST_PAGE_SIZE_MAX

# Dictionary of ISE REST Endpoints mapping to a tuple of the object name and base URL
# 'Resource': ('ERS_Name', 'REST API Base URL')
ISE_REST_ENDPOINTS = {
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


async def get_ers_resources (session, path):
    """
    Return the resources from the JSON response.
    @session : the aiohttp session to reuse
    @name    : the ERS object name in the JSON
    @path    : the REST endpoint path
    """
    async with session.get(path) as response:
        # print(f"ⓘ get_ers_resources({path}): {json}", file=sys.stderr)
        data = await response.json()
        data = data['SearchResult']['resources'] if data.get('SearchResult', None) != None else data
        return data


async def delete_ise_resource (session, path):
    async with session.delete(path) as resp:
        print(f"ⓘ {resp.status} | {path} ", file=sys.stderr)
        return resp


async def q_all_resources (session:aiohttp.ClientSession=None, q:asyncio.Queue=None, name:str=None, path:str=None):
    """
    Return the specified resources from ISE.
    @session : the aiohttp session to reuse
    @name    : the ERS object name
    @path    : the REST endpoint path
    """
    # Get the first page for the total resources
    response = await session.get(f"{path}?size={REST_PAGE_SIZE}")
    json = await response.json()
    resources = []
    total = 0
    is_ers = False
    #
    # ISE ERS or OpenAPI?
    # ERS is a dict: {'SearchResult': {'total': 7, 'resources': [{'id': ...
    # OpenAPI is a list: {'response': [{'id': ...
    #
    if result:= json.get('SearchResult', None) != None:
        is_ers = True
        total = json['SearchResult']['total']
        resources = json['SearchResult']['resources']
        # Get all remaining resources if more than the REST page size
        if total > REST_PAGE_SIZE:
            urls = [] # Generate all paging URLs
            for page in range(2, math.ceil(total / REST_PAGE_SIZE)+1): # already fetched first page above
                urls.append(f"{path}?size={REST_PAGE_SIZE}&page={page}")
            # Get all pages with asyncio!
            tasks = []
            [tasks.append(asyncio.ensure_future(get_ers_resources(session, url))) for url in urls]
            responses = await asyncio.gather(*tasks)
            [resources.extend(response) for response in responses]
    else:
        if json.get('response'): # OpenAPI
            resources = json['response']
            total = len(resources)
        else: # hotpatch / patch
            resources = json
            total = 1

    if len(resources) > 0:
        print(f"ⓘ Deleting {len(resources)} {name} ...", file=sys.stderr)
        # remove ugly 'link' attribute to flatten data
        for r in resources:
            if isinstance(r, dict) and r.get('link'): 
                del r['link']
            r['path'] = path
        # resources.sort(key=lambda r: len(r['name']), reverse=True)
        [await q.put(resource) for resource in resources]


async def delete_resource (q, session):
    while True:
        resource_data = await q.get() # Get an item from the queue
        response = await session.delete(resource_data['path']+'/'+resource_data['id'])
        print(f"✔ {response.status} | {resource_data['id']} | {resource_data['name']}", file=sys.stdout)
        q.task_done()  # Notify queue the item is processed


async def main ():
    """
    Entrypoint for packaged script.
    """
    argp = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    argp.add_argument('resources', type=str, help='resource name')
    argp.add_argument('-t','--timer', action='store_true', default=False, help='time', required=False)
    argp.add_argument('-v','--verbosity', action='count', default=0, help='Verbosity')
    args = argp.parse_args()
    if args.timer: start_time = time.time()

    env = {k:v for (k, v) in os.environ.items() if k.startswith('ISE_')}  # Load environment variables

    # Create HTTP session
    base_url = f"https://{env['ISE_PPAN']}"
    conn = aiohttp.TCPConnector(ssl=(False if env['ISE_CERT_VERIFY'][0:1].lower() in ['f','n'] else True))
    basic_auth = aiohttp.BasicAuth(login=env['ISE_REST_USERNAME'], password=env['ISE_REST_PASSWORD'])
    json_headers = {'Accept':'application/json', 'Content-Type':'application/json'}
    async with aiohttp.ClientSession(base_url, auth=basic_auth, connector=conn, headers=json_headers) as session:
        try:
            resource_q = asyncio.Queue() # Create a queue for the user workload
            tasks = [asyncio.create_task(delete_resource(resource_q, session)) for ii in range(WORKER_COUNT)]

            for resource in args.resources.strip(', ').split(','):
                if ISE_REST_ENDPOINTS.get(resource, None) == None: 
                    print(f"Skipping unknown resource: {resource}")
                    continue
                name, path = ISE_REST_ENDPOINTS[resource] 
                await q_all_resources(session, resource_q, name, path) 

            await resource_q.join()  # process the queue until finished

        except aiohttp.ContentTypeError as e:
            print(f"\n❌ Error: {e.message}\n\n💡Enable the ISE REST APIs\n")
        except aiohttp.ClientConnectorError as e:  # cannot connect to host
            print(f"\n❌ Host unreachable: {e}\n", file=sys.stderr)
        except aiohttp.ClientError as e:           # base aiohttp Exception
            print(f"\n❌ ClientError Exception: {e}\n", file=sys.stderr)
        except Exception as e: # catch *all* exceptions
            tb_text = '\n'.join(traceback.format_exc().splitlines()[1:]) # remove 'Traceback (most recent call last):'
            print(f"💣 {e.__class__} {tb_text}", file=sys.stderr) # {urlpath} | {url} | {data} |  {response.status} {request.method} {request.path}
        finally:
            await session.close()
            [task.cancel() for task in tasks] # cancel all workers when queue is done
            await asyncio.gather(*tasks, return_exceptions=True) # wait until all worker tasks are cancelled

    if args.timer: print(f"⏲ {'{0:.3f}'.format(time.time() - start_time)} seconds", file=sys.stderr)



if __name__ == '__main__':
    """
    Entrypoint for local script.
    """
    loop = asyncio.get_event_loop()
    main_task = asyncio.ensure_future(main())

    # Handle CTRL+C interrupts gracefully
    for signal in [signal.SIGINT, signal.SIGTERM]:
        loop.add_signal_handler(signal, main_task.cancel)
    try:
        loop.run_until_complete(main_task)
    finally:
        loop.close()

