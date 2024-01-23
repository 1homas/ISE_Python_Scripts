#!/usr/bin/env python3
"""

Show ISE REST APIs data.

Examples:
    ise_get.py endpoint 
    ise_get.py endpoint -v
    ise_get.py endpoint -itv
    ise_get.py endpointgroup -f  csv
    ise_get.py endpointgroup -f  csv -f endpointgroup.csv
    ise_get.py endpointgroup -f  id
    ise_get.py endpointgroup -f  line
    ise_get.py endpointgroup -f  pretty
    ise_get.py endpointgroup -f  pretty --details
    ise_get.py endpointgroup -f  grid
    ise_get.py endpointgroup -f  grid --details --noid
    ise_get.py endpointgroup -f  yaml
    ise_get.py --format yaml --noid pxgd-connector-config > pxgd-connector-config.yaml

Requires setting the these environment variables using the `export` command:
  export ISE_HOSTNAME='1.2.3.4'         # hostname or IP address of ISE PAN
  export ISE_REST_USERNAME='admin'      # ISE ERS admin or operator username
  export ISE_REST_PASSWORD='C1sco12345' # ISE ERS admin or operator password
  export ISE_CERT_VERIFY=false          # validate the ISE certificate

You may add these export lines to a text file and load with `source`:
  source ise.sh

"""

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
import yaml
from tabulate import tabulate


DATA_DIR = './data'
DT_ISO8601 = "%Y-%m-%d %H:%M:%S" # DateTime Formats for strftime()

REST_PAGE_SIZE_DEFAULT=20
REST_PAGE_SIZE_MAX=100
REST_PAGE_SIZE=REST_PAGE_SIZE_MAX

# Limit TCP connection pool size to prevent connection refusals by ISE!
# 30 for ISE 2.6+; See https://cs.co/ise-scale for Concurrent ERS Connections.
# Testing with ISE 3.0 shows *no* performance gain for >5-10
TCP_CONNECTIONS_DEFAULT=10
TCP_CONNECTIONS_MAX=30
TCP_CONNECTIONS=TCP_CONNECTIONS_DEFAULT

# Dictionary of ISE REST Endpoints mapping to a tuple of the object name and base URL
ISE_REST_ENDPOINTS = {
    # 'Resource',       : ( 'Object',           'Base_URL' )
    # -----------------   ----------------------  -----------------------
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
        data = await resp.json()
        # print('.', end='', file=sys.stderr, flush=True)
        # if args.verbosity >= 3: print(f"ⓘ get_ers_resources({path}): {data}", file=sys.stderr)
        return data['SearchResult']['resources']

async def get_ers_resource_detail (session, path):
    """
    Return the resources from the JSON response.
    @session : the aiohttp session to reuse
    @path    : the REST endpoint path
    """
    async with session.get(path) as resp:
        print('.', end='', file=sys.stderr, flush=True)
        # if args.verbosity >= 3: print(f"ⓘ get_ers_resource_detail({path}): {data}", file=sys.stderr)
        return (await resp.json())


async def ise_get_old (session=None, name=None, path=None, detailed=False):
    """
    Return the specified resources from ISE.
    @session : the aiohttp session to reuse
    @name    : the ERS object name
    @path    : the REST endpoint path
    @detailed: True to get all object details, False otherwise
    """
    # Get the first page for the total resources
    response = await session.get(f"{path}?size={REST_PAGE_SIZE}")
    json = await response.json()
    resources = []
    #
    # ISE ERS or OpenAPI?
    # ERS is a dict: {'SearchResult': {'total': 7, 'resources': [{'id': ...
    # OpenAPI is a list: {'response': [{'id': ...
    #
    if result:= json.get('SearchResult', None) != None:
        print(f"Getting {total} {name} resources ...", file=sys.stderr)

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

        if total > 0 and detailed:
            print(f"Getting {len(resources)} {name} details ", end='', file=sys.stderr, flush=True)
            # Extract UUIDs and get all resource details
            uuids = [r['id'] for r in resources]
            resources = [] # clear list for detailed data
            for uuid in uuids:
                print('.', end='', file=sys.stderr, flush=True)
                async with session.get(f"{path}/{uuid}") as r:
                    json = await r.json()
                    # if args.verbosity >= 3: print(f"json: {json}", file=sys.stderr)
                    resources.append(json[name])
            print(file=sys.stderr, flush=True)

    else:
        if json.get('response'): # OpenAPI
            resources = json['response']
            total = len(resources)
        else: # hotpatch / patch
            resources = json
            total = 1

    if args.verbosity: print(f"ⓘ ise_get({path}): Total: {total}", file=sys.stderr)

    # remove ugly 'link' attribute to flatten data
    for r in resources:
        if type(r) == dict and r.get('link'): 
            del r['link']
    return resources


def show (resources=None, name=None, format='json', filename='-'):
    """
    Shows the resources in the specified format to the file handle.

    @resources : the list of dictionary items to format
    @name      : the name of the resource. Example: endpoint, sgt, etc.
    @format    : 
        - `csv`   : Show the items in a Comma-Separated Value (CSV) format
        - `grid`  : Show the items in a table grid with borders
        - `table` : Show the items in a text-based table
        - `id`    : Show only the id column for the objects (if available)
        - `json`  : Show the items as a single JSON string
        - `line`  : Show the items as JSON with each item on it's own line
        - `pretty`: Show the items as JSON pretty-printed with 2-space indents
        - `yaml`  : Show the items as YAML with 2-space indents
    @filename  : Default: `sys.stdout`
    """
    if resources == None: return
    object_type = None if len(resources) <= 0 else type(resources[0]) 
    if args.verbosity >= 3: print(f"ⓘ show(): {len(resources)} x '{name}' resources of type {type(object_type)}", file=sys.stderr)

    # 💡 Do not close sys.stdout or it may not be re-opened
    fh = sys.stdout # write to terminal by default
    if filename != '-':
        if args.verbosity >= 3: print(f"ⓘ Opening {filename}", file=sys.stderr)
        fh = open(filename, 'w')

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
    elif format == 'line':  # 1 line per object
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


async def ise_get (session=None, name=None, path=None, detailed=False):
    """
    Return the specified resources from ISE.
    @session : the aiohttp session to reuse
    @name    : the ERS object name
    @path    : the REST endpoint path
    @detailed: True to get all object details, False otherwise
    """
    print(f"ise_get(name:{name}, path:{path}, detailed:{detailed})")
    resources = []
    response = await session.get(f"{path}") # Get the first page for the `total` resources
    data = await response.json()
    # print(f"data: {data})")
    if path.startswith('/ers'):
        # ERS is a dict: {'SearchResult': {'total': 7, 'resources': [{'id': ...
        total = data['SearchResult']['total']
        if total > 1000: print(f"Getting {total} {name} resources", file=sys.stderr, flush=True)
        # Get all resources if more than the REST page size
        urls = [f"{path}?size={REST_PAGE_SIZE}&page={page}" for page in range(1, 1+int(total/REST_PAGE_SIZE)+(1 if total%REST_PAGE_SIZE else 0))] # Generate paging URLs
        tasks = [asyncio.ensure_future(get_ers_resources(session, url)) for url in urls]
        responses = await asyncio.gather(*tasks)
        [resources.extend(response) for response in responses]

        if total > 0 and detailed:
            print(f"Getting {len(resources)} {name} details", file=sys.stderr, flush=True)
            uuids = [r['id'] for r in resources] # Extract UUIDs from summary resources
            urls = [f"{path}/{uuid}" for uuid in uuids] # Generate resource URLs
            tasks = [asyncio.ensure_future(get_ers_resource_detail(session, url)) for url in urls]
            responses = await asyncio.gather(*tasks)
            resources = [response[name] for response in responses]
            print(file=sys.stderr, flush=True)

    elif path.startswith('/api'): # OpenAPI is a list [] *or* dict with a list: {'response': [{'id': ...
        if isinstance(data, list):  # list of resources Example: endpoints
            resources = data
        elif isinstance(data, dict):
            if data.get('response'): # 'response' key to resources list?
                resources = data['response']   # response contains a list of resources
            else: # the data is the object. Example: hotpatch, patch, etc.
                resources = data
    else:
        print(f"Other path: {path})")
        resources = data

    total = len(resources)
    if args.verbosity: print(f"ⓘ ise_get({path}): Total: {total}", file=sys.stderr)

    # remove ugly 'link' attribute to flatten data
    for r in resources:
        if type(r) == dict and r.get('link'): 
            del r['link']
    return resources


async def get(resource:str=None, details:bool=False, noid:bool=True, verbosity:int=0):
    """
    Entrypoint for packaged script.
    """

    env = {k:v for (k, v) in os.environ.items() if k.startswith('ISE_')}  # Load environment variables

    resources = []
    try:
        # Create HTTP session
        verify_ssl = (False if env['ISE_CERT_VERIFY'][0:1].lower() in ['f','n'] else True)
        tcp_conn = aiohttp.TCPConnector(limit=TCP_CONNECTIONS, limit_per_host=TCP_CONNECTIONS, ssl=verify_ssl)
        auth = aiohttp.BasicAuth(login=env['ISE_REST_USERNAME'], password=env['ISE_REST_PASSWORD'])
        base_url = f"https://{env['ISE_HOSTNAME']}"
        headers = {'Accept':'application/json', 'Content-Type':'application/json'}
        session = aiohttp.ClientSession(base_url, auth=auth, connector=tcp_conn, headers=headers)

        # map the REST endpoint to the ERS object name and URL
        (name, base_url) = ISE_REST_ENDPOINTS.get(resource, (None, None))
        if verbosity >= 3: print(f"\nⓘ object: '{name}' base_url: {base_url}", file=sys.stderr)
        if base_url:
            resources = await ise_get(session, name, base_url, details)

            if noid and isinstance(resources[0], dict): # remove id from resource dict?
                for r in resources: del r['id']

            if args.verbosity >= 3: print(f"ⓘ type(resources): {type(resources)}", file=sys.stderr)
            if isinstance(resources, dict): resources = [ resources ]
            show(resources, args.resource, args.format, args.filename)

        else:
            print(f"\nUnknown resource: {resource}\n", file=sys.stderr)
    except aiohttp.ContentTypeError as e:
        print(f"\n❌ Error: {e.message}\n\n💡Enable the ISE REST APIs\n")
    except aiohttp.ClientConnectorError as e:  # cannot connect to host
        print(f"\n❌ Host unreachable: {e}\n", file=sys.stderr)
    except aiohttp.ClientError as e:           # base aiohttp Exception
        print(f"\n❌ Exception: {e}\n", file=sys.stderr)
    except:                                     # catch *all* exceptions
        print(f"\n❌ Exception: {e}\n", file=sys.stderr)
    finally:
        await session.close()


if __name__ == '__main__':
    """
    Entrypoint for local script.
    """
    global args     # promote to global scope for use in other functions
    argp = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)  # Keep __doc__ format
    argp.add_argument('resource', type=str, help='resource name')
    argp.add_argument('--connections', type=int, default=TCP_CONNECTIONS, help='Connection pool size')
    argp.add_argument('--pagesize', type=int, default=REST_PAGE_SIZE, help='REST page size')
    argp.add_argument('--noid', action='store_true', default=False, dest='noid', help='hide object UUIDs')
    argp.add_argument('--filename', default='-', required=False, help='Save output to filename. Default: stdout')
    argp.add_argument('-d', '--details', action='store_true', default=False, help='Get resource details')
    argp.add_argument('-i', '--insecure', action='store_true', default=False, help='ignore cert checks')
    argp.add_argument('-f', '--format', choices=['csv', 'id', 'grid', 'table', 'json', 'line', 'pretty', 'yaml'], default='pretty')
    argp.add_argument('-t', '--timer', action='store_true', default=False, help='show response timer' )
    argp.add_argument('-v', '--verbosity', action='count', default=0, help='Verbosity; multiple allowed')
    args = argp.parse_args()

    if args.verbosity >= 3: print(f"ⓘ Args: {args}")
    if args.verbosity >= 2: print(f"ⓘ connections: {args.connections}", file=sys.stderr)
    if args.verbosity >= 2: print(f"ⓘ details: {args.details}", file=sys.stderr)
    if args.verbosity >= 2: print(f"ⓘ filename: {args.filename}", file=sys.stderr)
    if args.verbosity >= 2: print(f"ⓘ insecure: {args.insecure}", file=sys.stderr)
    if args.verbosity >= 2: print(f"ⓘ format: {args.format}", file=sys.stderr)
    if args.verbosity >= 2: print(f"ⓘ pagesize: {args.pagesize}", file=sys.stderr)
    if args.verbosity >= 2: print(f"ⓘ noid: {args.noid}", file=sys.stderr)
    if args.verbosity >= 2: print(f"ⓘ timer: {args.timer}", file=sys.stderr)
    if args.verbosity >= 2: print(f"ⓘ verbosity: {args.verbosity}", file=sys.stderr)

    if args.timer: start_time = time.time()

    asyncio.run(get(resource=args.resource, details=args.details, noid=args.noid, verbosity=args.verbosity))

    if args.timer: print(f"⏲ {len(resources)} {args.resource} in {'{0:.3f}'.format(time.time() - start_time)} seconds", file=sys.stderr)
    sys.exit(0) # 0 is ok
