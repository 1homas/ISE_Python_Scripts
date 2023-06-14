#!/usr/bin/env python3
#------------------------------------------------------------------------------
# @author: Thomas Howard
# @email: thomas@cisco.com
#------------------------------------------------------------------------------
import aiohttp
import asyncio
import argparse
import csv
import io
import json
import os
import random
import sys
import time
import yaml
from tabulate import tabulate

# Globals
USAGE = """

Show ISE TrustSec data.

Examples:
    ise_get.py endpoint 
    ise_get.py endpoint -v
    ise_get.py endpoint -itv
    ise_get.py endpointgroup -o csv
    ise_get.py endpointgroup -o csv -f endpointgroup.csv
    ise_get.py endpointgroup -o id
    ise_get.py endpointgroup -o line
    ise_get.py endpointgroup -o pretty
    ise_get.py endpointgroup -o pretty --details
    ise_get.py endpointgroup -o table
    ise_get.py endpointgroup -o table --details --noid
    ise_get.py endpointgroup -o yaml

Requires setting the these environment variables using the `export` command:
  export ISE_HOSTNAME='1.2.3.4'         # hostname or IP address of ISE PAN
  export ISE_REST_USERNAME='admin'      # ISE ERS admin or operator username
  export ISE_REST_PASSWORD='C1sco12345' # ISE ERS admin or operator password
  export ISE_CERT_VERIFY=false          # validate the ISE certificate

You may add these export lines to a text file and load with `source`:
  source ise.sh

"""

DATA_DIR = './'
DEFAULT_TRUSTSEC_FILENAME = 'ise_trustsec_matrix.xlsx'

# REST Options
JSON_HEADERS = {'Accept':'application/json', 'Content-Type':'application/json'}
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
    'egressmatrixcell'  : ( 'EgressMatrixCell', '/ers/config/egressmatrixcell' ),

    #
    # ERS
    #

    # Deployment
    'info' : ( 'ERSDeploymentInfo', '/deploymentinfo/getAllInfo' ),    # 'deploymentinfo'=> deploymentinfo/getAllInfo
    'node'                      : ( 'Node', '/ers/config/node' ),
    # 'service'                   : ( 'Service', '/ers/config/service' ),    # 🛑 empty resource; link:service/null gives 404
    'sessionservicenode'        : ( 'SessionServiceNode', '/ers/config/sessionservicenode' ),

    # Network Devices
    'networkdevice'             : ( 'NetworkDevice',    '/ers/config/networkdevice' ),
    'networkdevicegroup'        : ( 'NetworkDeviceGroup', '/ers/config/networkdevicegroup' ),

    # Endpoints
    'endpoint'                  : ( 'ERSEndPoint',      '/ers/config/endpoint' ),
    'endpointcert'              : ( 'ERSEndPointCert',     '/ers/config/endpointcert' ),  # POST(create) only!!!
    'endpointgroup'             : ( 'EndPointGroup',    '/ers/config/endpointgroup' ),
    'profilerprofile'           : ( 'ProfilerProfile',  '/ers/config/profilerprofile' ),

    # RADIUS Authentications
    'activedirectory'  : ( 'ERSActiveDirectory', '/ers/config/activedirectory' ),
    'allowedprotocols'  : ( 'AllowedProtocols', '/ers/config/allowedprotocols' ),
    'adminuser'  : ( 'AdminUser', '/ers/config/adminuser' ),
    'identitygroup'  : ( 'IdentityGroup', '/ers/config/identitygroup' ),
    'internaluser'  : ( 'InternalUser', '/ers/config/internaluser' ),
    'externalradiusserver'  : ( 'ExternalRadiusServer', '/ers/config/externalradiusserver' ),
    'radiusserversequence'  : ( 'RadiusServerSequence', '/ers/config/radiusserversequence' ),
    'idstoresequence'  : ( 'IdStoreSequence', '/ers/config/idstoresequence' ),
    'restidstore'  : ( 'ERSRestIDStore', '/ers/config/restidstore' ),  # RESTIDStore must be enabled / 404 if none configured

    # RADIUS Authorizations / Policy
    'authorizationprofile'  : ( 'AuthorizationProfile', '/ers/config/authorizationprofile' ),
    'downloadableacl'  : ( 'DownloadableAcl', '/ers/config/downloadableacl' ),
    'filterpolicy'  : ( 'ERSFilterPolicy', '/ers/config/filterpolicy' ),  # 404 if none configured

    # Portals
    'portal'  : ( 'ERSPortal', '/ers/config/portal' ),
    'portalglobalsetting'  : ( 'PortalCustomizationGlobalSetting', '/ers/config/portalglobalsetting' ),
    'portaltheme'  : ( 'PortalTheme', '/ers/config/portaltheme' ),
    'hotspotportal'  : ( 'HotspotPortal', '/ers/config/hotspotportal' ),
    'selfregportal'  : ( 'SelfRegPortal', '/ers/config/selfregportal' ),

    # Guest
    'guestlocation'  : ( 'LocationIdentification', '/ers/config/guestlocation' ),
    'guestsmtpnotificationsettings'  : ( 'ERSGuestSmtpNotificationSettings', '/ers/config/guestsmtpnotificationsettings' ),
    'guestssid'  : ( 'GuestSSID', '/ers/config/guestssid' ),
    'guesttype'  : ( 'GuestType', '/ers/config/GuestType' ),
    'guestuser'  : ( 'GuestUser', '/ers/config/___GuestUser__' ),          # 🛑 requires sponsor account!!!
    'smsprovider'  : ( 'SmsProviderIdentification', '/ers/config/smsprovider' ),
    'sponsorportal'  : ( 'SponsoredPortal', '/ers/config/sponsorportal' ),
    'sponsoredguestportal'  : ( 'SponsoredGuestPortal', '/ers/config/sponsoredguestportal' ),
    'sponsorgroup'  : ( 'SponsorGroup', '/ers/config/sponsorgroup' ),
    'sponsorgroupmember'  : ( 'SponsorGroupMember', '/ers/config/sponsorgroupmember' ),

    # BYOD
    'certificateprofile'  : ( 'CertificateProfile', '/ers/config/certificateprofile' ),
    'certificatetemplate'  : ( 'ERSCertificateTemplate', '/ers/config/certificatetemplate' ),
    'byodportal'  : ( 'BYODPortal', '/ers/config/byodportal' ),
    'mydeviceportal'  : ( 'MyDevicePortal', '/ers/config/mydeviceportal' ),
    'nspprofile'  : ( 'ERSNSPProfile', '/ers/config/nspprofile' ),

    # SDA
    'sgt'               : ( 'Sgt',              '/ers/config/sgt' ),
    'sgacl'             : ( 'Sgacl',            '/ers/config/sgacl' ),
    'sgmapping'  : ( 'SGMapping', '/ers/config/sgmapping' ),
    'sgmappinggroup'  : ( 'SGMappingGroup', '/ers/config/sgmappinggroup' ),
    'sgtvnvlan'  : ( 'SgtVNVlanContainer', '/ers/config/sgtvnvlan' ),
    'egressmatrixcell'  : ( 'EgressMatrixCell', '/ers/config/egressmatrixcell' ),
    'sxpconnections'  : ( 'ERSSxpConnection', '/ers/config/sxpconnections' ),
    'sxplocalbindings'  : ( 'ERSSxpLocalBindings', '/ers/config/sxplocalbindings' ),
    'sxpvpns'  : ( 'ERSSxpVpn', '/ers/config/sxpvpns' ),

    # Support / Operations
    # 'supportbundle'  : ( '_____', '/ers/config/_____' ),
    # 'supportbundledownload'  : ( '_____', '/ers/config/_____' ),
    # 'supportbundlestatus'  : ( '_____', '/ers/config/_____' ),

    # TACACS
    'tacacscommandsets'  : ( 'TacacsCommandSets', '/ers/config/tacacscommandsets' ),
    'tacacsexternalservers'  : ( 'TacacsExternalServer', '/ers/config/tacacsexternalservers' ),  # 404 if none configured
    # 'tacacsprofile'  : ( 'TacacsProfile', '/ers/config/tacacsprofile' ),
    # 'tacacsserversequence'  : ( 'TacacsServerSequence', '/ers/config/tacacsserversequence' ),  # 404 if none configured

    # pxGrid / ANC / RTC / TC-NAC
    'pxgridsettings'    : ( 'PxgridSettings', '/ers/config/pxgridsettings/autoapprove' ), # 🛑 PUT only; GET not supported!
    'pxgridnode'        : ( 'pxGridNode', '/ers/config/pxgridnode' ),  # 🐛 🛑 404 always whether pxGrid is enabled or not
    # 'ancendpoint'  : ( '_____', '/ers/config/_____' ),
    # 'ancpolicy'  : ( '_____', '/ers/config/_____' ),
    # 'clearThreatsAndVulneribilities'  : ( 'ERSIrfThreatContext', '/ers/config/threat/clearThreatsAndVulneribilities' ),  # 🛑 PUT only; GET not supported!

    'telemetryinfo' : ( 'TelemetryInfo', '/ers/config/telemetryinfo' ),
    # ACI
    # 'acibindings'  : ( '_____', '/ers/config/_____' ),    # Custom URL: /ers/config/acibindings/getall
    # 'acisettings'  : ( '_____', '/ers/config/_____' ),

    # Operations
    # 'op'  : ( '_____', '/ers/config/_____' ),
    # 'op/systemconfig'  : ( '_____', '/ers/config/_____' ),
    # 'op/systemconfig/iseversion'  : ( '_____', '/ers/config/_____' ),
    
    
    #
    # OpenAPI
    #

}

# This hidden SGT is required for lookups with the default ANY-ANY SGACL.
SGT_ANY = {'id':'92bb1950-8c01-11e6-996c-525400b48521', 'name':'ANY', 'description':'ANY', 'value':65535, 'generationId':0, 'propogateToApic':False}


async def get_ise_resource (session, url) :
    async with session.get(url) as resp:
        json = await resp.json()
        if args.verbosity >= 3 : print(f"ⓘ get_ise_resource({url}): {json}", file=sys.stderr)
        return json['SearchResult']['resources']


async def get_ise_resources (session, path) :
    """
    Fetch the resources from ISE.
    @session : the aiohttp session to reuse
    @path : the REST endpoint path
    """
    if args.verbosity >= 3 : print(f"ⓘ get_ise_resources({path})", file=sys.stderr)

    # Get the first page for the total resources
    response = await session.get(f"{path}?size={REST_PAGE_SIZE}")
    json = await response.json()
    total = json['SearchResult']['total']
    resources = json['SearchResult']['resources']
    if args.verbosity >= 3 : print(f"ⓘ get_ise_resources({path}): Total: {total}", file=sys.stderr)

    # Get all remaining resources if more than the REST page size
    if total > REST_PAGE_SIZE :
        pages = int(total / REST_PAGE_SIZE) + (1 if total % REST_PAGE_SIZE else 0)
        
        # Generate all paging URLs 
        urls = []
        for page in range(2, pages + 1): # already fetched first page above
            urls.append(f"{path}?size={REST_PAGE_SIZE}&page={page}")

        # Get all pages with asyncio!
        tasks = []
        [ tasks.append(asyncio.ensure_future(get_ise_resource(session, url))) for url in urls ]
        responses = await asyncio.gather(*tasks)
        [ resources.extend(response) for response in responses ]

    # remove ugly 'link' attribute to flatten data
    for r in resources:
        if type(r) == dict and r.get('link'): 
            del r['link']

    return resources


async def get_ise_resource_details (session, ers, path) :
    """
    Fetch the resources from ISE.
    @session : the aiohttp session to reuse
    @ers : the ERS object name in the JSON
    @path : the REST endpoint path
    """
    if args.verbosity >= 3 : print(f"ⓘ get_ise_resource_details({ers}, {path})", file=sys.stderr)

    # Get all resources for their UUIDs
    resources = await get_ise_resources(session, path)

    # Save UUIDs
    uuids = [r['id'] for r in resources]
    resources = [] # clear list for detailed data
    for uuid in uuids:
        async with session.get(f"{path}/{uuid}") as resp:
            json = await resp.json()
            if args.verbosity >= 3 : print(f"json: {json}", file=sys.stderr)
            resources.append(json[ers])

    # remove ugly 'link' attribute to flatten data
    for r in resources:
        if type(r) == dict and r.get('link'): 
            del r['link']

    return resources


async def delete_ise_resources (session, ers, path, resources) :
    """
    POST the resources to ISE.
    @session : the aiohttp session to reuse
    @ers : the ERS object name in the JSON
    @path : the REST endpoint path
    @resources : a list of resources identifiers (id or name)
    """
    if args.verbosity >= 3 : print(f"ⓘ > delete_ise_resources({ers}, {path}, {len(df)})", file=sys.stderr)

    for resource in resources :
        if args.verbosity >= 3 : print(f"delete resource: {path}/{resource}", file=sys.stderr)
        async with session.delete(f"{path}/{resource}") as resp:
            if resp.ok : print(f"⌫ {resp.status} {resource}")
            # elif resp.status == 400 : print(f"ⓘ  {resp.status} {row['name']} {(await resp.json())['ERSResponse']['messages'][0]['title']}")
            else : print(f"❌ {resp.status} {(await resp.json())['ERSResponse']['messages'][0]['title']}")

    if args.verbosity >= 3 : print(f"ⓘ < delete_ise_resources({ers}, {path}) {len(resources)}", file=sys.stderr)



async def post_simple_ise_resources (session, ers, path, df) :
    """
    POST the resources to ISE.
    @session : the aiohttp session to reuse
    @ers : the ERS object name in the JSON
    @path : the REST endpoint path
    @df : the dataframe of resources to create
    """
    if args.verbosity >= 3 : print(f"ⓘ > post_simple_ise_resources({ers}, {path}, {len(df)})", file=sys.stderr)

    for row in df.to_dict('records'):
        if args.verbosity >= 3 : print(f"row: {row}", file=sys.stderr)
        resource = { ers : row }
        if args.verbosity >= 3 : print(f"resource: {resource}", file=sys.stderr)
        if args.verbosity >= 3 : print(f"resource as json: {json.dumps(resource)}", file=sys.stderr)
        async with session.post(f"{path}", data=json.dumps(resource)) as resp:
            if resp.ok : print(f"🌟 {resp.status} {row['name']}", file=sys.stderr)
            elif resp.status == 400 : print(f"ⓘ  {resp.status} {row['name']} {(await resp.json())['ERSResponse']['messages'][0]['title']}", file=sys.stderr)
            else : print(f"❌ {resp.status} {(await resp.json())['ERSResponse']['messages'][0]['title']}", file=sys.stderr)

    # Get newly created resources
    resources = await get_ise_resources(session, path)
    resources = await get_ise_resource_details(session, ers, path)

    if args.verbosity >= 3 : print(f"ⓘ < post_simple_ise_resources({ers}, {path}) {len(resources)}", file=sys.stderr)

    return resources


def show (resources=None, format='dump', filename='-') :
    """
    Shows the resources in the specified format to the file handle.
    
    @resources : the list of dictionary items to format
    @format    : ['dump', 'line', 'pretty', 'table', 'csv', 'id', 'yaml']
    @filename  : Default: `sys.stdout`
    """
    if args.verbosity >= 3 : print(f"ⓘ > show(): {len(resources)} resources of type {type(resources[0])}", file=sys.stderr)

    # 💡 Do not close sys.stdout or it may not be re-opened
    fh = sys.stdout # write to terminal by default
    if filename != '-' :
        if args.verbosity >= 3 : print(f"ⓘ Opening {filename}", file=sys.stderr)
        fh = open(filename, 'w')

    if format == 'dump':  # default: dump json
        print(json.dumps(resources), file=fh)

    elif format == 'csv':  # CSV
        headers = {}
        [headers.update(r) for r in resources]  # find all unique keys
        writer = csv.DictWriter(fh, headers.keys(), quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        for row in resources:
            writer.writerow(row)

    elif format == 'id':  # list of ids
        ids = [[r['id']] for r in resources]  # single column table
        print(f"{tabulate(ids, tablefmt='plain')}", file=fh)

    elif format == 'line':  # 1 line per object
        print('[')
        [print(json.dumps(r), end=',\n', file=fh) for r in resources]
        print(']')

    elif format == 'pretty':  # pretty-print
        print(json.dumps(resources, indent=2), file=fh)

    elif format == 'table':  # table
        print(f"\n{tabulate(resources, headers='keys', tablefmt='simple_grid')}", file=fh)

    elif format == 'yaml':  # YAML
        # [print(yaml.dump(r, indent=2, default_flow_style=False), file=fh) for r in resources]
        print(yaml.dump(resources, indent=2, default_flow_style=False), file=fh)

    else:  # just in case something gets through the CLI parser
        print(MSG_CERTIFICATE_ERROR + f': {args.output}', file=sys.stderr)


async def parse_cli_arguments () :
    """
    Parse the command line arguments
    """
    ARGS = argparse.ArgumentParser(
            description=USAGE,
            formatter_class=argparse.RawDescriptionHelpFormatter,   # keep my format
            )

    ARGS.add_argument('resource', type=str, help='resource name')
    ARGS.add_argument('--connections', type=int, default=TCP_CONNECTIONS, help='Connection pool size')
    ARGS.add_argument('--pagesize', type=int, default=REST_PAGE_SIZE, help='REST page size')
    ARGS.add_argument('--noid', action='store_true', default=False, dest='noid', help='hide object UUIDs')
    ARGS.add_argument('-d', '--details', action='store_true', default=False, help='Get resource details')
    ARGS.add_argument('-f', '--filename', default='-', required=False, help='Save output to filename')
    ARGS.add_argument('-i', '--insecure', action='store_true', default=False, help='ignore cert checks')
    ARGS.add_argument('-o', '--output', choices=['dump', 'line', 'pretty', 'table', 'csv', 'id', 'yaml'], default='dump')
    ARGS.add_argument('-t', '--timer', action='store_true', default=False, help='show response timer' )
    ARGS.add_argument('-v', '--verbosity', action='count', default=0, help='Verbosity; multiple allowed')

    return ARGS.parse_args()


async def main ():
    """
    Entrypoint for packaged script.
    """

    global args     # promote to global scope for use in other functions
    args = await parse_cli_arguments()
    if args.verbosity >= 3 : print(f"ⓘ Args: {args}")
    if args.verbosity : print(f"ⓘ connections: {args.connections}", file=sys.stderr)
    if args.verbosity : print(f"ⓘ details: {args.details}", file=sys.stderr)
    if args.verbosity : print(f"ⓘ filename: {args.filename}", file=sys.stderr)
    if args.verbosity : print(f"ⓘ insecure: {args.insecure}", file=sys.stderr)
    if args.verbosity : print(f"ⓘ output: {args.output}", file=sys.stderr)
    if args.verbosity : print(f"ⓘ pagesize: {args.pagesize}", file=sys.stderr)
    if args.verbosity : print(f"ⓘ noid: {args.noid}", file=sys.stderr)
    if args.verbosity : print(f"ⓘ timer: {args.timer}", file=sys.stderr)
    if args.verbosity : print(f"ⓘ verbosity: {args.verbosity}", file=sys.stderr)

    if args.timer :
        global start_time
        start_time = time.time()

    # Load Environment Variables
    global env
    env = { k : v for (k, v) in os.environ.items() if k.startswith('ISE_') }

    resources = []
    try :
        # Create HTTP session
        ssl_verify = (False if (args.insecure or env['ISE_CERT_VERIFY'][0:1].lower() in ['f','n']) else True)
        tcp_conn = aiohttp.TCPConnector(limit=TCP_CONNECTIONS, limit_per_host=TCP_CONNECTIONS, ssl=ssl_verify)
        auth = aiohttp.BasicAuth(login=env['ISE_REST_USERNAME'], password=env['ISE_REST_PASSWORD'])
        base_url = f"https://{env['ISE_HOSTNAME']}"
        session = aiohttp.ClientSession(base_url, auth=auth, connector=tcp_conn, headers=JSON_HEADERS)

        # map the REST endpoint to the ERS object name and URL
        (ers, base_url) = ISE_REST_ENDPOINTS.get(args.resource, (None, None))
        if args.verbosity >= 3 : print(f"\nⓘ ers: {ers} base_url: {base_url}", file=sys.stderr)

        if base_url and args.details :
            resources = await get_ise_resource_details(session, ers, base_url)
        elif base_url :
            resources = await get_ise_resources(session, base_url)
        else :
            print(f"\nUnknown resource: {args.resource}\n", file=sys.stderr)
    except aiohttp.ContentTypeError as e :
        print(f"\n❌ Error: {e.message}\n\n💡Enable the ISE REST APIs\n")
    except aiohttp.ClientConnectorError as e :  # cannot connect to host
        print(f"\n❌ Host unreachable: {e}\n", file=sys.stderr)
    except aiohttp.ClientError as e :           # base aiohttp Exception
        print(f"\n❌ Exception: {e}\n", file=sys.stderr)
    except:                                     # catch *all* exceptions
        print(f"\n❌ Exception: {e}\n", file=sys.stderr)
    finally:
        await session.close()

    # remove id?
    if args.noid :
        for r in resources:
            if type(r) == dict and r.get('id'): 
                del r['id']
 
    show(resources, args.output, args.filename)

    if args.timer :
        duration = time.time() - start_time
        print(f"\n 🕒 {duration} seconds\n", file=sys.stderr)


if __name__ == '__main__':
    """
    Entrypoint for local script.
    """
    asyncio.run(main())
    sys.exit(0) # 0 is ok
