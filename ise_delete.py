#!/usr/bin/env python3
"""
Delete ISE resources via REST APIs.

Examples:
    ise_delete.py endpoint 
    ise_delete.py endpoint -v
    ise_delete.py endpoint -itv
    ise_delete.py endpointgroup -f  csv
    ise_delete.py endpointgroup -f  csv -f endpointgroup.csv
    ise_delete.py endpointgroup -f  id
    ise_delete.py endpointgroup -f  line
    ise_delete.py endpointgroup -f  pretty
    ise_delete.py endpointgroup -f  pretty --details
    ise_delete.py endpointgroup -f  grid
    ise_delete.py endpointgroup -f  grid --details --noid
    ise_delete.py endpointgroup -f  yaml
    ise_delete.py --format yaml --noid pxgd-connector-config > pxgd-connector-config.yaml

Requires setting the these environment variables using the `export` command:
  export ISE_HOSTNAME='1.2.3.4'         # hostname or IP address of ISE PAN
  export ISE_REST_USERNAME='admin'      # ISE ERS admin or operator username
  export ISE_REST_PASSWORD='C1sco12345' # ISE ERS admin or operator password
  export ISE_CERT_VERIFY=false          # validate the ISE certificate

You may add these `export` lines to a text file, customize them, and load with `source`:
  source ise.sh

"""

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
import yaml
import math
from tabulate import tabulate

WORKER_COUNT = 20
DATA_DIR = './'
DT_ISO8601 = "%Y-%m-%dT%H:%M:%S" # DateTime Formats for strftime()

# REST Options
JSON_HEADERS = {'Accept':'application/json', 'Content-Type':'application/json'}
REST_PAGE_SIZE_MAX=100
REST_PAGE_SIZE=REST_PAGE_SIZE_MAX

# Dictionary of ISE REST Endpoints mapping to a tuple of the object name and base URL
ISE_REST_ENDPOINTS = {
    # 'Resource',           : ( 'Object',           'Base_URL' )            # comment
    # -----------------     ----------------------  -----------------------
    'egressmatrixcell'      : ( 'EgressMatrixCell', '/ers/config/egressmatrixcell' ),

    #
    # ERS
    #

    # Deployment
    'info'                  : ( 'ERSDeploymentInfo', '/deploymentinfo/getAllInfo' ),  # 'deploymentinfo'=> deploymentinfo/getAllInfo
    'node'                  : ( 'Node', '/ers/config/node' ),
    # 'service'             : ( 'Service', '/ers/config/service' ),  # 🛑 empty resource; link:service/null gives 404
    'sessionservicenode'    : ( 'SessionServiceNode', '/ers/config/sessionservicenode' ),

    # Network Devices
    'networkdevice'         : ( 'NetworkDevice',        '/ers/config/networkdevice' ),
    'networkdevicegroup'    : ( 'NetworkDeviceGroup',   '/ers/config/networkdevicegroup' ),

    # Endpoints
    'endpoint'              : ( 'ERSEndPoint',          '/ers/config/endpoint' ),
    'endpointcert'          : ( 'ERSEndPointCert',      '/ers/config/endpointcert' ),  # POST(create) only!!!
    'endpointgroup'         : ( 'EndPointGroup',        '/ers/config/endpointgroup' ),
    'profilerprofile'       : ( 'ProfilerProfile',      '/ers/config/profilerprofile' ),

    # RADIUS Authentications
    'activedirectory'       : ( 'ERSActiveDirectory',   '/ers/config/activedirectory' ),
    'allowedprotocols'      : ( 'AllowedProtocols',     '/ers/config/allowedprotocols' ),
    'adminuser'             : ( 'AdminUser',            '/ers/config/adminuser' ),
    'identitygroup'         : ( 'IdentityGroup',        '/ers/config/identitygroup' ),
    'internaluser'          : ( 'InternalUser',         '/ers/config/internaluser' ),
    'externalradiusserver'  : ( 'ExternalRadiusServer', '/ers/config/externalradiusserver' ),
    'radiusserversequence'  : ( 'RadiusServerSequence', '/ers/config/radiusserversequence' ),
    'idstoresequence'       : ( 'IdStoreSequence',      '/ers/config/idstoresequence' ),
    'restidstore'           : ( 'ERSRestIDStore',       '/ers/config/restidstore' ),  # RESTIDStore must be enabled / 404 if none configured

    # RADIUS Authorizations / Policy
    'authorizationprofile'  : ( 'AuthorizationProfile', '/ers/config/authorizationprofile' ),
    'downloadableacl'       : ( 'DownloadableAcl',      '/ers/config/downloadableacl' ),
    'filterpolicy'          : ( 'ERSFilterPolicy',      '/ers/config/filterpolicy' ),  # 404 if none configured

    # Portals
    'portal'                : ( 'ERSPortal',            '/ers/config/portal' ),
    'portalglobalsetting'   : ( 'PortalCustomizationGlobalSetting', '/ers/config/portalglobalsetting' ),
    'portaltheme'           : ( 'PortalTheme',          '/ers/config/portaltheme' ),
    'hotspotportal'         : ( 'HotspotPortal',        '/ers/config/hotspotportal' ),
    'selfregportal'         : ( 'SelfRegPortal',        '/ers/config/selfregportal' ),

    # Guest
    'guestlocation'         : ( 'LocationIdentification', '/ers/config/guestlocation' ),
    'guestsmtpnotificationsettings' : ( 'ERSGuestSmtpNotificationSettings', '/ers/config/guestsmtpnotificationsettings' ),
    'guestssid'             : ( 'GuestSSID',            '/ers/config/guestssid' ),
    'guesttype'             : ( 'GuestType',            '/ers/config/GuestType' ),
    'guestuser'             : ( 'GuestUser',            '/ers/config/___GuestUser__' ), # 🛑 requires sponsor account!!!
    'smsprovider'           : ( 'SmsProviderIdentification', '/ers/config/smsprovider' ),
    'sponsorportal'         : ( 'SponsoredPortal',      '/ers/config/sponsorportal' ),
    'sponsoredguestportal'  : ( 'SponsoredGuestPortal', '/ers/config/sponsoredguestportal' ),
    'sponsorgroup'          : ( 'SponsorGroup',         '/ers/config/sponsorgroup' ),
    'sponsorgroupmember'    : ( 'SponsorGroupMember',   '/ers/config/sponsorgroupmember' ),

    # BYOD
    'certificateprofile'    : ( 'CertificateProfile',   '/ers/config/certificateprofile' ),
    'certificatetemplate'   : ( 'ERSCertificateTemplate', '/ers/config/certificatetemplate' ),
    'byodportal'            : ( 'BYODPortal',           '/ers/config/byodportal' ),
    'mydeviceportal'        : ( 'MyDevicePortal',       '/ers/config/mydeviceportal' ),
    'nspprofile'            : ( 'ERSNSPProfile',        '/ers/config/nspprofile' ),

    # SDA
    'sgt'                   : ( 'Sgt',                  '/ers/config/sgt' ),
    'sgacl'                 : ( 'Sgacl',                '/ers/config/sgacl' ),
    'sgmapping'             : ( 'SGMapping',            '/ers/config/sgmapping' ),
    'sgmappinggroup'        : ( 'SGMappingGroup',       '/ers/config/sgmappinggroup' ),
    'sgtvnvlan'             : ( 'SgtVNVlanContainer',   '/ers/config/sgtvnvlan' ),
    'egressmatrixcell'      : ( 'EgressMatrixCell',     '/ers/config/egressmatrixcell' ),
    'sxpconnections'        : ( 'ERSSxpConnection',     '/ers/config/sxpconnections' ),
    'sxplocalbindings'      : ( 'ERSSxpLocalBindings',  '/ers/config/sxplocalbindings' ),
    'sxpvpns'               : ( 'ERSSxpVpn',            '/ers/config/sxpvpns' ),

    # Support / Operations
    # 'supportbundle'       : ( '_____', '/ers/config/_____' ),
    # 'supportbundledownload': ( '_____', '/ers/config/_____' ),
    # 'supportbundlestatus' : ( '_____', '/ers/config/_____' ),

    # TACACS
    'tacacscommandsets'     : ( 'TacacsCommandSets',    '/ers/config/tacacscommandsets' ),
    'tacacsexternalservers' : ( 'TacacsExternalServer', '/ers/config/tacacsexternalservers' ),  # 404 if none configured
    'tacacsprofile'         : ( 'TacacsProfile',        '/ers/config/tacacsprofile' ),
    'tacacsserversequence'  : ( 'TacacsServerSequence', '/ers/config/tacacsserversequence' ),  # 404 if none configured

    # pxGrid / ANC / RTC / TC-NAC
    'pxgridsettings'        : ( 'PxgridSettings',       '/ers/config/pxgridsettings/autoapprove' ), # 🛑 PUT only; GET not supported!
    'pxgridnode'            : ( 'pxGridNode',           '/ers/config/pxgridnode' ),  # 🐛 🛑 404 always whether pxGrid is enabled or not
    # 'ancendpoint'         : ( '_____', '/ers/config/_____' ),
    # 'ancpolicy'           : ( '_____', '/ers/config/_____' ),
    # 'clearThreatsAndVulneribilities'  : ( 'ERSIrfThreatContext', '/ers/config/threat/clearThreatsAndVulneribilities' ),  # 🛑 PUT only; GET not supported!

    'telemetryinfo' : ( 'TelemetryInfo', '/ers/config/telemetryinfo' ),
    # ACI
    # 'acibindings'         : ( '_____', '/ers/config/_____' ),    # Custom URL: /ers/config/acibindings/getall
    # 'acisettings'         : ( '_____', '/ers/config/_____' ),

    # Operations
    # 'op'                  : ( '_____', '/ers/config/_____' ),
    # 'op/systemconfig'     : ( '_____', '/ers/config/_____' ),
    # 'op/systemconfig/iseversion' : ( '_____', '/ers/config/_____' ),


    #
    # OpenAPI
    #

    # Certificates
    'trusted-certificate'   : ( '-', '/api/v1/certs/trusted-certificate' ),
    'system-certificate'    : ( '-', '/api/v1/certs/system-certificate/{hostName}' ),
    'certificate-signing-request' : ( '-', '/api/v1/certs/certificate-signing-request' ),

    # Backup Restore
    'last-backup-status'    : ( '-', '/api/v1/backup-restore/config/last-backup-status' ),

    # Deployment
    'deployment-node'       : ( '-', '/api/v1//deployment/node' ),
    'node-group'            : ( '-', '/api/v1//deployment/node-group' ),
    'pan-ha'                : ( '-', '/api/v1//deployment/pan-ha' ),
    'node-interface'        : ( '-', '/api/v1/node/{hostname}/interface' ),
    'sxp-interface'         : ( '-', '/api/v1/node/{hostname}/sxp-interface' ),
    'profile'               : ( '-', '/api/v1/profile/{hostname}' ),

    # Endpoints
    'endpoints'             : ( '-', '/api/v1/endpoint' ),
    # 'endpoint-value'      : ( '-', '/api/v1/endpoint/{value}' ),
    'endpoint-summary'      : ( '-', '/api/v1/endpoint/deviceType/summary' ),

    # Endpoint Custom Atributes
    'endpoint-custom-attribute' : ( '-', '/api/v1/endpoint-custom-attribute' ),

    # IPsec
    'ipsec'                 : ( 'ipsec', '/api/v1/ipsec' ),
    # 'ipsec'               : ( 'ipsec', '/api/v1/ipsec/{hostName}/{nadIp}' ),
    'ipsec-certificates'    : ( 'ipsec-certificates','/api/v1/ipsec/certificates' ),

    # LDAP
    'ldap'                  : ( '-', '/api/v1/ldap' ),
    'ldap-rootcacertificates': ( '-', '/api/v1/ldap/rootcacertificates ' ),
    'ldap-hosts'            : ( '-', '/api/v1/ldap/hosts' ),
    # 'ldap'                : ( '-', '/api/v1/ldap/name/{name} ' ),
    # 'ldap'                : ( '-', '/api/v1/ldap/{id}' ),

    # License
    'license-system-smart-state' : ( '-', '/api/v1/license/system/smart-state' ),
    'license-system-register'    : ( '-', '/api/v1/license/system/register' ),
    'license-system-tier-state'  : ( '-', '/api/v1/license/system/tier-state' ),
    'license-system-eval-license': ( '-', '/api/v1/license/system/eval-license' ),
    'license-system-connection-type': ( '-', '/api/v1/license/system/connection-type' ),
    'license-system-feature-to-tier-mapping': ( '-', '/api/v1/license/system/feature-to-tier-mapping' ),

    # LSD
    'lsd'                   : ( '-', '/api/v1/lsd/updateLsdSettings' ),

    # Device Admin
    # ⓘ All Device Admin policy objects have the prefix "da-"
    'da-command-sets'       : ( '-', '/api/v1/policy/device-admin/command-sets' ),
    'da-condition'          : ( '-', '/api/v1/policy/device-admin/condition' ),
    # 'da-condition-id'     : ( '-', '/api/v1/policy/device-admin/condition/{conditionId}' ),
    'da-condition-policyset': ( '-', '/api/v1/policy/device-admin/condition/policyset' ),
    'da-condition-authn'    : ( '-', '/api/v1/policy/device-admin/condition-authentication' ),
    'da-condition-authz'    : ( '-', '/api/v1/policy/device-admin/condition-authorization' ),
    'da-dict-authn'         : ( '-', '/api/v1/policy/device-admin/dictionaries/authentication' ),
    'da-dict-authz'         : ( '-', '/api/v1/policy/device-admin/dictionaries/authorization' ),
    'da-dict-policyset'     : ( '-', '/api/v1/policy/device-admin/dictionaries/policyset' ),
    'da-identity-stores'    : ( '-', '/api/v1/policy/device-admin/identity-stores' ),
    'da-policy-set'         : ( '-', '/api/v1/policy/device-admin/policy-set' ),
    # 'da-policy-set-id'    : ( '-', '/api/v1/policy/device-admin/policy-set/{id}' ),
    'da-global-exception'   : ( '-', '/api/v1/policy/device-admin/policy-set/global-exception' ),
    'da-service-names'      : ( '-', '/api/v1/policy/device-admin/service-names' ),
    'da-shell-profiles'     : ( '-', '/api/v1/policy/device-admin/shell-profiles' ),
    'da-time-condition'     : ( '-', '/api/v1/policy/device-admin/time-condition' ),

    # Network Access Policy
    # ⓘ Network Access policy is the assumed default; prefix "na-" not required
    'authorization-profiles': ( '-', '/api/v1/policy/network-access/authorization-profiles' ),
    # 'condition-id'        : ( '-', '/api/v1/policy/network-access/condition/{conditionId}' ),
    'condition-policyset'   : ( '-', '/api/v1/policy/network-access/condition/policyset' ),
    'condition-authn'       : ( '-', '/api/v1/policy/network-access/condition-authentication' ),
    'condition-authz'       : ( '-', '/api/v1/policy/network-access/condition-authorization' ),
    'dict'                  : ( '-', '/api/v1/policy/network-access/dictionaries' ),
    # 'dict-name'           : ( '-', '/api/v1/policy/network-access/dictionaries/{name}' ),
    'dict-authn'            : ( '-', '/api/v1/policy/network-access/dictionaries/authentication' ),
    'dict-authz'            : ( '-', '/api/v1/policy/network-access/dictionaries/authorization' ),
    'dict-policyset'        : ( '-', '/api/v1/policy/network-access/dictionaries/policyset' ),
    'identity-stores'       : ( '-', '/api/v1/policy/network-access/identity-stores' ),
    'network-condition'     : ( '-', '/api/v1/policy/network-access/network-condition' ),
    'policy-set'            : ( '-', '/api/v1/policy/network-access/policy-set' ),
    # 'policy-set-id'       : ( '-', '/api/v1/policy/network-access/policy-set/{id}' ),
    # 'policy-set-id-authn' : ( '-', '/api/v1/policy/network-access/policy-set/{policyId}/authentication' ),
    # 'policy-set-id-authz' : ( '-', '/api/v1/policy/network-access/policy-set/{policyId}/authorization' ),
    # 'policy-set-id-exception': ( '-', '/api/v1/policy/network-access/policy-set/{policyId}/exception' ),
    'global-exception'      : ( '-', '/api/v1/policy/network-access/policy-set/global-exception' ),
    'security-groups'       : ( '-', '/api/v1/policy/network-access/security-groups' ),
    'service-names'         : ( '-', '/api/v1/policy/network-access/service-names' ),
    'time-condition'        : ( '-', '/api/v1/policy/network-access/time-condition' ),

    # pxGrid Direct
    'pxgd-config'           : ( '-', '/api/v1/pxgrid-direct/connector-config' ),
    # 'pxgd-config-name': ( '-', '/api/v1/pxgrid-direct/connector-config/{name}' ),
    'pxgd-references'       : ( '-', '/api/v1/pxgrid-direct/dictionary-references' ),

    # SgtRangeReservation
    'sgt-reservation'       : ( '-', '/api/v1/sgt/reservation' ),
    # 'sgt-reservation-id'  : ( '-', '/api/v1/sgt/reservation/{id}' ),

    # System Settings
    'proxy'                 : ( '-', '/api/v1/system-settings/proxy' ),
    'transport-gateway'     : ( '-', '/api/v1/system-settings/telemetry/transport-gateway' ),

    # TrustSec
    'trustsec-sgacl-nbarapp': ( '-', '/api/v1/trustsec/sgacl/nbarapp' ),
    'trustsec-sgvnmapping'  : ( '-', '/api/v1/trustsec/sgvnmapping' ),
    'trustsec-virtualnetwork': ( '-', '/api/v1/trustsec/virtualnetwork' ),
    'trustsec-vnvlanmapping': ( '-', '/api/v1/trustsec/vnvlanmapping' ),

    'repository'            : ( '-', '/api/v1/repository' ),
    # 'repository-name'     : ( '-', '/api/v1/repository/{name}' ),
    # 'repository-name-files': ( '-', '/api/v1/repository/{name}/files' ),

    # Data Connect
    'mnt-data-connect-details': ( '-', '/api/v1/mnt/data-connect/details' ),
    'mnt-data-connect-settings': ( '-', '/api/v1/mnt/data-connect/settings' ),

    'task'                  : ( '-', '/api/v1/task' ),
    # 'task-id'             : ( '-', '/api/v1/task/{id}' ),

    # Patching
    'hotpatch'              : ( '-', '/api/v1/hotpatch' ),
    'patch'                 : ( '-', '/api/v1/patch' ),

    # Upgrade
    'upgrade-prepare-status': ( '-', '/api/v1/upgrade/prepare/get-status' ),
    'upgrade-proceed-status': ( '-', '/api/v1/upgrade/proceed/get-status' ),
    'upgrade-stage-status'  : ( '-', '/api/v1/upgrade/stage/get-status' ),
    'upgrade-summary-status': ( '-', '/api/v1/upgrade/summary/get-status' ),
}


async def get_ers_resources (session, path):
    """
    Return the resources from the JSON response.
    @session : the aiohttp session to reuse
    @name    : the ERS object name in the JSON
    @path    : the REST endpoint path
    """
    async with session.get(path) as resp:
        # print(f"ⓘ get_ers_resources({path}): {json}", file=sys.stderr)
        return (await resp.json())['SearchResult']['resources']


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
    argp = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter) # keep my format
    argp.add_argument('resources', type=str, help='resource name')
    argp.add_argument('-t','--timer', action='store_true', default=False, help='time', required=False)
    argp.add_argument('-v','--verbosity', action='count', default=0, help='Verbosity')
    args = argp.parse_args()
    if args.timer: start_time = time.time()

    env = {k:v for (k, v) in os.environ.items() if k.startswith('ISE_')}  # Load environment variables

    # Create HTTP session
    base_url = f"https://{env['ISE_HOSTNAME']}"
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
            print(f"\n❌ Other Exception: {e} {e.message}\n", file=sys.stderr)
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

