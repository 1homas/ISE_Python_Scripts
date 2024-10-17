#!/usr/bin/env python3
"""

Show ISE REST APIs data.

Examples:
    ise-get.py endpoint 
    ise-get.py endpoint -itv
    ise-get.py endpoints -itv
    ise-get.py endpointgroup -f csv -f endpointgroup.csv
    ise-get.py endpointgroup -f pretty --details
    ise-get.py endpointgroup -f grid --details --noid
    ise-get.py endpointgroup -f yaml
    ise-get.py allowedprotocols -f yaml --details
    ise-get.py internaluser -ivt -f table --details
    ise-get.py na-policy-set-authz --vars id=11a1d056-7a2b-4b58-bdd0-624d005ac92e

    ise-get.py all -v --details -f yaml --save saved_config

Requires setting the these environment variables using the `export` command:
  export ISE_PPAN='1.2.3.4'             # hostname or IP address of ISE Primary PAN
  export ISE_REST_USERNAME='admin'      # ISE ERS admin or operator username
  export ISE_REST_PASSWORD='C1sco12345' # ISE ERS admin or operator password
  export ISE_VERIFY=false          # validate the ISE certificate

You may add these export lines to a text file and load with `source`:
  source ise.sh

"""
__author__ = "Thomas Howard"
__email__ = "thomas@cisco.com"
__license__ = "MIT - https://mit-license.org/"


import aiohttp
import aiohttp_client_cache
import asyncio
import argparse
import csv
import datetime
import io
import json
import math
import os
import random
import ssl
import sys
import time
import traceback
import yaml
from string import Template
from tabulate import tabulate

ICONS = {
    # name : icon
    "BUG  ": "🐞",
    "CACHE": "↯",
    "DOWN": "▽",
    "ERROR": "⛒",
    "NONE": "∅",
    "FAIL": "✖",
    "INFO": "ℹ",
    "ID": "⚿",
    "LIST": "⁝",
    "LOCK": "🔒",
    "PASS": "✔",
    "PLAY": "▷",
    "TIMEOUT": "◔",
    "TIP": "💡",
    "UNLOCK": "🔓",
    "WARN": "⚠",
    "WATCH": "⏱",
}

# Limit TCP connection pool size to prevent connection refusals by ISE
# See https://cs.co/ise-scale for concurrent REST connection limits.
# Testing with ISE 3.x shows no performance gain for > ~5 connections.
TCP_LIMIT = 10  # 🔺ISE ERS APIs for GuestType and InternalUser can have problems with 10+ concurrent connections!
REST_PAGE_SIZE = 100

# Dictionary of ISE REST Endpoints mapping to a tuple of the object name and base URL
ISE_REST_ENDPOINTS = {
    #
    # '{resource}': '( {object_name}, {api_resource_path} )',
    #
    # Deployment @ https://cs.co/ise-api#!deployment-openapi
    "deployment-node": ("-", "/api/v1/deployment/node"),
    "node-group": ("-", "/api/v1/deployment/node-group"),
    "pan-ha": ("-", "/api/v1/deployment/pan-ha"),
    # 'node-interface': ('-', '/api/v1/node/$hostname/interface'),
    # 'sxp-interface': ('-', '/api/v1/node/$hostname/sxp-interface'),
    # 'profile': ('-', '/api/v1/profile/$hostname'),
    "repository": ("-", "/api/v1/repository"),  # Repository @ https://cs.co/ise-api#!repository-openapi
    "repository-name": ("-", "/api/v1/repository/$name"),  # 💡 requires repository $name
    "repository-name-files": ("-", "/api/v1/repository/$name/files"),
    # Patching @ https://cs.co/ise-api#!patch-and-hot-patch-openapi
    "hotpatch": ("-", "/api/v1/hotpatch"),
    "patch": ("-", "/api/v1/patch"),
    # DeploymentInfo @ https://cs.co/ise-api#!deploymentinfo
    # 'info': ('ERSDeploymentInfo', '/deploymentinfo/getAllInfo'),  # 'deploymentinfo'=> deploymentinfo/getAllInfo
    "node": ("Node", "/ers/config/node"),  # Node @ https://cs.co/ise-api#!node
    # 'service': ('Service', '/ers/config/service'),  # 🛑 empty resource; link:service/null gives 404
    "sessionservicenode": ("SessionServiceNode", "/ers/config/sessionservicenode"),
    # Certificates @ https://cs.co/ise-api#!certificate-openapi
    "trusted-certificate": ("-", "/api/v1/certs/trusted-certificate"),  # Get list of all trusted certificates
    "trusted-certificate-id": ("-", "/api/v1/certs/trusted-certificate/$id"),
    "system-certificate": ("-", "/api/v1/certs/system-certificate/$hostname"),
    "certificate-signing-request": ("-", "/api/v1/certs/certificate-signing-request"),
    "system-certificate-by-name": ("-", "/api/v1/certs/system-certificate/$hostname"),
    # Backup Restore
    "last-backup-status": ("-", "/api/v1/backup-restore/config/last-backup-status"),
    # Upgrade
    "upgrade-prepare-status": ("-", "/api/v1/upgrade/prepare/get-status"),
    "upgrade-proceed-status": ("-", "/api/v1/upgrade/proceed/get-status"),
    "upgrade-stage-status": ("-", "/api/v1/upgrade/stage/get-status"),
    "upgrade-summary-status": ("-", "/api/v1/upgrade/summary/get-status"),
    # System Settings
    "lsd": ("-", "/api/v1/lsd/updateLsdSettings"),  # LSD
    "settings-proxy": ("-", "/api/v1/system-settings/proxy"),
    "settings-ttg": ("-", "/api/v1/system-settings/telemetry/transport-gateway"),
    # Data Connect @ https://cs.co/ise-dataconnect
    "data-connect-details": ("-", "/api/v1/mnt/data-connect/details"),
    "data-connect-settings": ("-", "/api/v1/mnt/data-connect/settings"),
    # Identity Stores
    "activedirectory": ("ERSActiveDirectory", "/ers/config/activedirectory"),
    "restidstore": ("ERSRestIDStore", "/ers/config/restidstore"),  # RESTIDStore must be enabled / 404 if none configured
    # LDAP @ https://cs.co/ise-api#!ldap
    # 'ldap': ('???', '/ers/config/ldap'), # 404 if unconfigured?
    # 'ldap-rootcacertificates': ('???', '/ers/config/ldap/rootcacertificates'),
    # 'ldap-hosts': ('???', '/ers/config/ldap/hosts'),
    "ldap-by-name": ("???", "/ers/config/ldap/name/$name"),
    "ldap-by-id": ("???", "/ers/config/ldap/$id"),
    # Duo MFA
    "duo-sync-ads": ("-", "/api/v1/duo-identitysync/activedirectories"),
    "duo-sync-groups": ("-", "/api/v1/duo-identitysync/adgroups/$id"),
    "duo-identitysync": ("-", "/api/v1/duo-identitysync/identitysync"),
    "duo-mfa": ("-", "/api/v1/duo-mfa/mfa"),  # Get the list of all Duo-MFA configurations
    # 'duo-mfa-enable': ('-', '/api/v1/duo-mfa/enable'), # PUT
    "duo-mfa-by-name": ("-", "/api/v1/duo-mfa/mfa/$name"),  # Get the specified Duo-MFA configuration
    "duo-mfa-status": ("-", "/api/v1/duo-mfa/status"),  # MFA feature enabled status
    # pxGrid Direct @ https://cs.co/ise-api#!pxgrid-direct-open-api
    "pxgd-config": ("-", "/api/v1/pxgrid-direct/connector-config"),
    "pxgd-config-by-name": ("-", "/api/v1/pxgrid-direct/connector-config/$name"),
    "pxgd-references": ("-", "/api/v1/pxgrid-direct/dictionary-references"),
    "externalradiusserver": ("ExternalRadiusServer", "/ers/config/externalradiusserver"),
    "radiusserversequence": ("RadiusServerSequence", "/ers/config/radiusserversequence"),
    "idstoresequence": ("IdStoreSequence", "/ers/config/idstoresequence"),
    # Network Devices
    "networkdevicegroup": ("NetworkDeviceGroup", "/ers/config/networkdevicegroup"),
    "networkdevice": ("NetworkDevice", "/ers/config/networkdevice"),  #
    # TrustSec
    "sgt": ("Sgt", "/ers/config/sgt"),
    "sgacl": ("Sgacl", "/ers/config/sgacl"),
    "sgmapping": ("SGMapping", "/ers/config/sgmapping"),
    "sgmappinggroup": ("SGMappingGroup", "/ers/config/sgmappinggroup"),
    "sgtvnvlan": ("SgtVNVlanContainer", "/ers/config/sgtvnvlan"),
    "egressmatrixcell": ("EgressMatrixCell", "/ers/config/egressmatrixcell"),
    "sxpconnections": ("ERSSxpConnection", "/ers/config/sxpconnections"),
    "sxplocalbindings": ("ERSSxpLocalBindings", "/ers/config/sxplocalbindings"),
    "sxpvpns": ("ERSSxpVpn", "/ers/config/sxpvpns"),
    "sgt-reservation": ("-", "/api/v1/sgt/reservation"),  # SgtRangeReservation @ https://cs.co/ise-api#!sgt-reservation-openapi
    "sgt-reservation-by-id": ("-", "/api/v1/sgt/reservation/$id"),  # Requires $id. Get the reserved range for the specific Client.
    # SDA/TrustSec @ https://cs.co/ise-api#!trustsec-openapi
    "trustsec-sgacl-nbarapp": ("-", "/api/v1/trustsec/sgacl/nbarapp"),
    "trustsec-sgvnmapping": ("-", "/api/v1/trustsec/sgvnmapping"),
    "trustsec-virtualnetwork": ("-", "/api/v1/trustsec/virtualnetwork"),
    "trustsec-vnvlanmapping": ("-", "/api/v1/trustsec/vnvlanmapping"),
    "profilerprofile": ("ProfilerProfile", "/ers/config/profilerprofile"),  # Endpoint Profiles @ https://cs.co/ise-api#!profilerprofile
    # Endpoints
    "endpointgroup": ("EndPointGroup", "/ers/config/endpointgroup"),  # EndpointGroups @ https://cs.co/ise-api#!endpointgroup
    "endpoint-custom-attribute": ("-", "/api/v1/endpoint-custom-attribute"),
    "endpoint-custom-attribute-by-name": ("-", "/api/v1/endpoint-custom-attribute/$name"),  # Get custom attribute by name
    # 'endpoint-stop-replication': ('-', '/api/v1/stop-replication'),    # Endpoint Stop Replication Service
    "endpoint": ("ERSEndPoint", "/ers/config/endpoint"),  # Endpoint @ https://cs.co/ise-api#!endpoint
    # 'endpointcert': ('ERSEndPointCert', '/ers/config/endpointcert'),  # 🛑 POST only
    "endpoints": ("-", "/api/v1/endpoint"),  # 💡 Requires ISE 3.2. Endpoints @ https://cs.co/ise-api#!get-all-endpoints
    "endpoint-value": ("-", "/api/v1/endpoint/$value"),  # Requires $value
    # 'endpoint-summary': ('-', '/api/v1/endpoint/deviceType/summary'), # 🛑 404?
    # TACACS+
    "tacacscommandsets": ("TacacsCommandSets", "/ers/config/tacacscommandsets"),
    "tacacsexternalservers": ("TacacsExternalServer", "/ers/config/tacacsexternalservers"),  # 💡 404 if none configured
    "tacacsprofile": ("TacacsProfile", "/ers/config/tacacsprofile"),
    "tacacsserversequence": ("TacacsServerSequence", "/ers/config/tacacsserversequence"),  # 💡 404 if none configured
    # Policy Sets - RADIUS Network Access
    # ERS policy elements
    "allowedprotocols": ("AllowedProtocols", "/ers/config/allowedprotocols"),
    "authorizationprofile": ("AuthorizationProfile", "/ers/config/authorizationprofile"),
    "downloadableacl": ("DownloadableAcl", "/ers/config/downloadableacl"),
    "filterpolicy": ("ERSFilterPolicy", "/ers/config/filterpolicy"),  # 404 if none configured
    # Network Access Policy @ https://cs.co/ise-api#!policy-openapi
    # ⓘ Network Access policy is the assumed default; prefix "na-" not required
    "na-authorization-profiles": ("-", "/api/v1/policy/network-access/authorization-profiles"),
    "na-condition": ("-", "/api/v1/policy/network-access/condition"),
    "na-condition-id": ("-", "/api/v1/policy/network-access/condition/$id"),
    "na-condition-policyset": ("-", "/api/v1/policy/network-access/condition/policyset"),
    "na-condition-authn": ("-", "/api/v1/policy/network-access/condition-authentication"),
    "na-condition-authz": ("-", "/api/v1/policy/network-access/condition-authorization"),
    "na-dicts": ("-", "/api/v1/policy/network-access/dictionaries"),
    "na-dict-name": ("-", "/api/v1/policy/network-access/dictionaries/$name"),
    "na-dict-authn": ("-", "/api/v1/policy/network-access/dictionaries/authentication"),
    "na-dict-authz": ("-", "/api/v1/policy/network-access/dictionaries/authorization"),
    "na-dict-policyset": ("-", "/api/v1/policy/network-access/dictionaries/policyset"),
    "na-identity-stores": ("-", "/api/v1/policy/network-access/identity-stores"),
    "na-network-condition": ("-", "/api/v1/policy/network-access/network-condition"),
    "na-policy-set": ("-", "/api/v1/policy/network-access/policy-set"),
    "na-policy-set-id": ("-", "/api/v1/policy/network-access/policy-set/$id"),
    "na-policy-set-authn": ("-", "/api/v1/policy/network-access/policy-set/$id/authentication"),
    "na-policy-set-authz": ("-", "/api/v1/policy/network-access/policy-set/$id/authorization"),
    "na-policy-set-exception": ("-", "/api/v1/policy/network-access/policy-set/$id/exception"),
    "na-global-exception": ("-", "/api/v1/policy/network-access/policy-set/global-exception"),
    "na-security-groups": ("-", "/api/v1/policy/network-access/security-groups"),
    "na-service-names": ("-", "/api/v1/policy/network-access/service-names"),
    "na-time-condition": ("-", "/api/v1/policy/network-access/time-condition"),
    # Policy Sets - TACACS+ Device Admin @ https://cs.co/ise-api#!policy-openapi
    # ⓘ All Device Admin policy objects have the prefix "da-"
    "da-command-sets": ("-", "/api/v1/policy/device-admin/command-sets"),
    "da-condition": ("-", "/api/v1/policy/device-admin/condition"),
    "da-condition-id": ("-", "/api/v1/policy/device-admin/condition/$id"),
    "da-condition-policyset": ("-", "/api/v1/policy/device-admin/condition/policyset"),
    "da-condition-authn": ("-", "/api/v1/policy/device-admin/condition-authentication"),
    "da-condition-authz": ("-", "/api/v1/policy/device-admin/condition-authorization"),
    "da-dict-authn": ("-", "/api/v1/policy/device-admin/dictionaries/authentication"),
    "da-dict-authz": ("-", "/api/v1/policy/device-admin/dictionaries/authorization"),
    "da-dict-policyset": ("-", "/api/v1/policy/device-admin/dictionaries/policyset"),
    "da-identity-stores": ("-", "/api/v1/policy/device-admin/identity-stores"),
    "da-policy-set": ("-", "/api/v1/policy/device-admin/policy-set"),
    "da-policy-set-id": ("-", "/api/v1/policy/device-admin/policy-set/$id"),
    "da-global-exception": ("-", "/api/v1/policy/device-admin/policy-set/global-exception"),
    "da-service-names": ("-", "/api/v1/policy/device-admin/service-names"),
    "da-shell-profiles": ("-", "/api/v1/policy/device-admin/shell-profiles"),
    "da-time-condition": ("-", "/api/v1/policy/device-admin/time-condition"),
    # Users
    "adminuser": ("AdminUser", "/ers/config/adminuser"),
    "identitygroup": ("IdentityGroup", "/ers/config/identitygroup"),
    "internaluser": ("InternalUser", "/ers/config/internaluser"),
    # Guest Portals
    "portal": ("ERSPortal", "/ers/config/portal"),
    "portalglobalsetting": ("PortalCustomizationGlobalSetting", "/ers/config/portalglobalsetting"),
    "portaltheme": ("PortalTheme", "/ers/config/portaltheme"),
    "hotspotportal": ("HotspotPortal", "/ers/config/hotspotportal"),
    "selfregportal": ("SelfRegPortal", "/ers/config/selfregportal"),
    "sponsorportal": ("SponsorPortal", "/ers/config/sponsorportal"),
    "sponsoredguestportal": ("SponsoredGuestPortal", "/ers/config/sponsoredguestportal"),
    # 'guestlocation': ('LocationIdentification', '/ers/config/guestlocation'),
    "guestsmtpnotificationsettings": ("ERSGuestSmtpNotificationSettings", "/ers/config/guestsmtpnotificationsettings"),
    "guestssid": ("GuestSSID", "/ers/config/guestssid"),
    "guesttype": ("GuestType", "/ers/config/guesttype"),  # 🛑 500 internal errors?
    "guestuser": ("GuestUser", "/ers/config/guestuser"),  # 🛑 requires sponsor account
    # 'smsprovider': ('SmsProviderIdentification', '/ers/config/smsprovider'),
    "sponsorgroup": ("SponsorGroup", "/ers/config/sponsorgroup"),
    "sponsorgroupmember": ("SponsorGroupMember", "/ers/config/sponsorgroupmember"),
    # BYOD
    "certificateprofile": ("CertificateProfile", "/ers/config/certificateprofile"),
    "certificatetemplate": ("ERSCertificateTemplate", "/ers/config/certificatetemplate"),
    "byodportal": ("BYODPortal", "/ers/config/byodportal"),
    "mydeviceportal": ("MyDevicePortal", "/ers/config/mydeviceportal"),
    "nspprofile": ("ERSNSPProfile", "/ers/config/nspprofile"),
    # IPsec @ https://cs.co/ise-api#!ipsec-openapi
    "ipsec": ("ipsec", "/api/v1/ipsec"),
    "ipsec": ("ipsec", "/api/v1/ipsec/$hostname/$ip"),
    "ipsec-certificates": ("ipsec-certificates", "/api/v1/ipsec/certificates"),
    # Support / Operations
    # 'supportbundle': ('_____', '/ers/config/supportbundle'),
    # 'supportbundledownload': ('_____', '/ers/config/_____'),
    # 'supportbundlestatus': ('_____', '/ers/config/_____'),
    # Task
    "task": ("-", "/api/v1/task"),
    "task-id": ("-", "/api/v1/task/$id"),
    # pxGrid / ANC / RTC / TC-NAC @ https://github.com/cisco-pxgrid/pxgrid-rest-ws/wiki
    # 'pxgridsettings': ('PxgridSettings', '/ers/config/pxgridsettings/autoapprove'), # 🛑 PUT only; GET not supported!
    # 'pxgridnode': ('pxGridNode', '/ers/config/pxgridnode'),  # 🛑 🐛 404 always whether pxGrid is enabled or not
    "ancendpoint": ("ErsAncEndpoint", "/ers/config/ancendpoint"),  # ANCEndpoint @ https://cs.co/ise-api#!ancendpoint
    "ancpolicy": ("ErsAncPolicy", "/ers/config/ancpolicy"),  # ANCPolicy @ https://cs.co/ise-api#!ancpolicy
    # 'ancpolicy-version': ('VersionInfo', '/ers/config/ancpolicy/versioninfo'), # 💡 No `SearchResult`, only `VersionInfo` object. Get ANC policy version information
    # 'clearThreatsAndVulneribilities': ('ERSIrfThreatContext', '/ers/config/threat/clearThreatsAndVulneribilities'),  # 🛑 PUT only; GET not supported! @ https://cs.co/ise-api#!clearThreatsAndVulneribilities
    "telemetryinfo": ("TelemetryInfo", "/ers/config/telemetryinfo"),  # Telemetry @ https://cs.co/ise-api#!telemetryinfo
    # 'acibindings': ('ACIBindings', '/ers/config/acibindings/getall'), # ACI @ https://cs.co/ise-api#!acibindings
    # 'acisettings': ('AciSettings', '/ers/config/acisettings'), # ACI @ https://cs.co/ise-api#!acisettings
    # Operations
    # 'op': ('_____', '/ers/config/_____'),
    # 'op/systemconfig': ('_____', '/ers/config/_____'),
    # 'op/systemconfig/iseversion': ('_____', '/ers/config/_____'),
    # License
    "license-system-smart-state": ("-", "/api/v1/license/system/smart-state"),
    "license-system-register": ("-", "/api/v1/license/system/register"),
    "license-system-tier-state": ("-", "/api/v1/license/system/tier-state"),
    "license-system-eval-license": ("-", "/api/v1/license/system/eval-license"),
    "license-system-connection-type": ("-", "/api/v1/license/system/connection-type"),
    "license-system-feature-to-tier-mapping": ("-", "/api/v1/license/system/feature-to-tier-mapping"),
}


async def show_resources(
    resources: [dict] = None, name: str = None, format="json", filepath: str = "-", hide: [str] = None, show: [str] = None
) -> None:
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
    if resources == None:
        return
    object_type = None if len(resources) <= 0 else type(resources[0])
    if args.verbosity >= 3:
        print(f"▷ show_resources({len(resources)} x '{name}' as {format} to {filepath})", file=sys.stderr)

    # Hide or show attributes?
    if hide is not None and show is not None:
        raise ValueError(f"hide and show are mutually exclusive and should not be used at the same time")
    if hide is not None:
        resources = [{k: v for k, v in resource.items() if k not in hide} for resource in resources]
    if show is not None:
        resources = [{k: v for k, v in resource.items() if k in show} for resource in resources]

    # 💡 Do not close sys.stdout or it may not be re-opened with multiple show_resources() calls
    fh = sys.stdout if filepath == "-" else open(filepath, "w")  # write to sys.stdout/terminal by default

    if format == "csv":  # CSV
        headers = {}
        [headers.update(r) for r in resources]  # find all unique keys
        writer = csv.DictWriter(fh, headers.keys(), quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        for row in resources:
            writer.writerow(row)
    elif format == "grid":  # grid
        print(f"{tabulate(resources, headers='keys', tablefmt='simple_grid')}", file=fh)
    elif format == "table":  # table
        print(f"{tabulate(resources, headers='keys', tablefmt='table')}", file=fh)
    elif format == "json":  # one long string of JSON
        print(json.dumps({name: resources}), file=fh)
    elif format == "line":  # 1 JSON object per line
        print("{", file=fh)
        print(f'"{name}" : [', file=fh)
        print(",\n".join([json.dumps(r) for r in resources]), file=fh)
        print("]\n}", file=fh)
    elif format == "pretty":  # pretty-print
        print(json.dumps({name: resources}, indent=2), file=fh)
    elif format == "yaml":  # YAML
        print(yaml.dump({name: resources}, indent=2, default_flow_style=False), file=fh)
    else:
        print(f"{ICONS['ERROR']} Unknown format: {format}", file=sys.stderr)


async def get_url_task(session: aiohttp.ClientSession = None, q: asyncio.Queue = None, resources: list = None, ers_name: str = None):
    """
    Runs URL requests.

    :param session (aiohttp.ClientSession) : a session to run the requests.
    :param q (asyncio.Queue) : a queue to pull API requests from
    :param resources (list) : a list to append the response data into
    :param ers_name (str) : the ISE ERS REST object name being fetched; used to extract the details data
    """
    if q is None:
        raise ValueError(f"q is None")
    if session is None:
        raise ValueError(f"session is None")
    while True:
        url = await q.get()  # Get an item or wait if empty
        try:
            response = await session.get(url)
            if response.status == 200:
                data = await response.json()
                if data.get(ers_name, None) is None:
                    resources.extend(data["SearchResult"]["resources"])
                else:
                    resources.append(data)
                # if args.verbosity > 1: print(f"{ICONS['PASS']} | {url}", file=sys.stdout)
                if args.verbosity == 1:
                    print(".", end="", file=sys.stderr, flush=True)  # print '.' for progress

            elif response.status == 401:
                print("Set the environment variables and verify your credentials are correct!", file=sys.stderr)
                print(await response.json(), file=sys.stderr)
            else:
                print(f"{ICONS['FAIL']} {response.status}:\n{json.dumps(await response.json(), indent=2)}")
        except Exception as e:
            tb_text = "\n".join(traceback.format_exc().splitlines()[1:])  # remove 'Traceback (most recent call last):'
            print(f"{ICONS['ERROR']} {e.__class__} {url} | {data} | {tb_text}", file=sys.stderr)

        q.task_done()  # Notify queue the item is processed


async def ise_get_all(session: aiohttp.ClientSession = None, ers_name: str = None, urlpath: str = None, details: bool = False) -> [dict]:
    """
    Return all of the specified resources from ISE.

    :param session (aiohttp.ClientSession): the aiohttp session to reuse
    :param ers_name (str) : the ERS object name.
    :param urlpath (str): the REST endpoint path.
    :param details (bool): True to get all object details, False otherwise
    """
    if args.verbosity:
        print(f"▷ ise_get_all {'' if ers_name is None else ers_name} ({urlpath})", end=" ", file=sys.stderr, flush=True)

    resources = []
    response = await session.get(f"{urlpath}?size={REST_PAGE_SIZE}&page=1")  # Get the first page for the `total` resources
    data = await response.json()
    #
    # ISE ERS or OpenAPI?
    # ERS returns a dict: {'SearchResult': {'total': 7, 'resources': [{'id': ...
    # OpenAPI requires no `name` and returns a response list: {'response': [{'id': ...
    #
    try:
        if urlpath.startswith("/ers"):  # ERS is a dict: {'SearchResult': {'total': 7, 'resources': [{'id': ...
            total = data["SearchResult"]["total"]
            if args.verbosity:
                print(f"[{total}]", end=" ", file=sys.stderr, flush=True)

            # Create AsyncIO Queue and Tasks to control the number of outstanding requests
            resource_q = asyncio.Queue(maxsize=TCP_LIMIT * 2)
            tasks = [asyncio.create_task(get_url_task(session, resource_q, resources, ers_name=ers_name)) for idx in range(TCP_LIMIT)]

            # Get *all* resource ids if more than the initial REST page size
            urls = [
                f"{urlpath}?size={REST_PAGE_SIZE}&page={page}"
                for page in range(1, 1 + int(total / REST_PAGE_SIZE) + (1 if total % REST_PAGE_SIZE else 0))
            ]  # Generate paging URLs
            [await resource_q.put(url) for url in urls]  # enqueue URLs
            await resource_q.join()  # Block until all items in queue are processed

            # Get resource details
            if total > 0 and details and ers_name != "SponsorGroupMember":  # 🔺 There is no GET by ID for /ers/config/sponsorgroupmember
                uuids = [r["id"] for r in resources]  # Extract UUIDs from summary resources
                urls = [f"{urlpath}/{uuid}" for uuid in uuids]  # Generate resource URLs
                resources.clear()  # remove all original data
                [await resource_q.put(url) for url in urls]  # enqueue URLs
                await resource_q.join()  # Block until all items in queue are processed

                if ers_name == "GuestType":
                    await asyncio.sleep(1)  # 💡 There is a conconcurrency issue with GuestType resources.

                resources = [resource[ers_name] for resource in resources]

            # Cancel our worker tasks and wait for their cancellation.
            [task.cancel() for task in tasks]
            await asyncio.gather(*tasks, return_exceptions=True)

        elif urlpath.startswith("/api"):  # OpenAPI is a list [] *or* dict with a list: {'response': [{'id': ...
            if isinstance(data, list):  # list of resources Example: endpoints
                resources = data
            elif isinstance(data, dict):
                if data.get("response"):  # 'response' key to resources list?
                    resources = data["response"]  # response contains a list of resources
                else:  # the data is the object. Example: hotpatch, patch, etc.
                    resources = data
        else:
            if args.verbosity:
                print(f"Unknown ISE urlpath: {urlpath})", file=sys.stderr)
            resources = data
    except Exception as e:
        tb_text = "\n".join(traceback.format_exc().splitlines()[1:])  # remove 'Traceback (most recent call last):'
        print(f"{ICONS['ERROR']} {e.__class__} {urlpath} | {data} | {tb_text}", file=sys.stderr)
    finally:
        if args.verbosity:
            print(file=sys.stderr, flush=True)  # send a newline after the outputs

    # remove ugly 'link' attribute to flatten data
    for r in resources:
        if type(r) == dict and r.get("link"):
            del r["link"]
    return resources


async def cache_filter_by_paging(response):
    """
    Filter which pages get cached with aiohttp_client_cache, if any.
    """
    return False if len(response.url.query_string) > 0 else True  # do not cache queries


async def get(
    resource: str = None,
    details: bool = False,
    filepath: str = None,
    format: str = None,
    noid: bool = True,
    insecure: bool = True,
    hide: [str] = None,
    show: [str] = None,
    vars: dict = None,
) -> None:
    """
    Get ISE resources via REST API.

    param: resource (str) :
    param: details (bool) :
    param: filepath (str :
    param: format (str) :
    param: noid (bool) :
    param: insecure (bool) :
    """
    env = {k: v for (k, v) in os.environ.items() if k.startswith("ISE_")}  # Load environment variables

    resources = []
    try:
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        if args.insecure or env.get("ISE_CERT_VERIFY", "True")[0:1].lower() in ["f", "n"]:
            ssl_context.check_hostname = False  # required before setting verify_mode == ssl.CERT_NONE
            ssl_context.verify_mode = ssl.CERT_NONE  # any cert is accepted; validation errors are ignored
            # if args.verbosity: print(f"{ICONS['UNLOCK']} Certificate verification disabled", file=sys.stderr)

        tcp_conn = aiohttp.TCPConnector(limit=TCP_LIMIT, limit_per_host=TCP_LIMIT, ssl=ssl_context)
        auth = aiohttp.BasicAuth(login=env["ISE_REST_USERNAME"], password=env["ISE_REST_PASSWORD"])
        base_url = f"https://{env['ISE_PPAN']}"
        headers = {"Accept": "application/json", "Content-Type": "application/json"}

        session = None
        if args.nocache:
            session = aiohttp.ClientSession(base_url, auth=auth, connector=tcp_conn, headers=headers)
            if args.verbosity:
                print(f"{ICONS['NONE']} Caching disabled")
        else:
            cache = aiohttp_client_cache.SQLiteBackend(
                cache_name="aiohttp-cache", filter_fn=cache_filter_by_paging, use_temp=False, autoclose=True
            )
            if args.verbosity:
                print(f"{ICONS['CACHE']} Caching enabled for {args.expiration} seconds on all URLs with SQLite")

            session = aiohttp_client_cache.CachedSession(
                base_url=base_url,
                auth=auth,
                cache=cache,
                connector=tcp_conn,
                headers=headers,
                expire_after=datetime.timedelta(seconds=args.expiration),
                # keepalive_timeout=600,
                # force_close=True, # use True to close underlying sockets after connection releasing and disable keep-alive feature
            )

        # map the REST endpoint to the ERS object name and URL
        (ers_name, urlpath) = ISE_REST_ENDPOINTS.get(resource, (None, None))
        if urlpath is None:
            print(f"{ICONS['ERROR']} Unknown resource: {resource}\n", file=sys.stderr)
            print(f"Did you mean: {', '.join(filter(lambda x: x.startswith(resource[0:3]), ISE_REST_ENDPOINTS.keys()))}\n", file=sys.stderr)
        else:
            if vars_dict:  # apply vars substitution
                urlpath = Template(urlpath).substitute(vars_dict)

            resources = await ise_get_all(session, ers_name, urlpath, details)

            # remove id from resource dict?
            if noid and isinstance(resources[0], dict):
                for r in resources:
                    del r["id"]

            if isinstance(resources, dict):
                resources = [resources]  # put individual dicts into a list for consistency

            if filepath and filepath != "-":
                if not os.path.exists(filepath):
                    os.makedirs(filepath)
                filename = ".".join([resource, format])
                filepath = os.path.join(filepath, filename)

    except aiohttp.ContentTypeError as e:
        print(f"\n{ICONS['ERROR']} Error: {e.message}\n\n💡Enable the ISE REST APIs\n")
    except aiohttp.ClientConnectorError as e:  # cannot connect to host
        print(f"\n{ICONS['ERROR']} Host unreachable: {e}\n", file=sys.stderr)
    except:  # catch *all* exceptions
        print(f"\n{ICONS['ERROR']} Exception: {e}\n", file=sys.stderr)
    finally:
        # print('-----', flush=True)
        # print(f"{ICONS['INFO']} finally: session.close() with {len(resources)} resources\n", file=sys.stderr)
        await session.close()

    await show_resources(resources, resource, format, filepath, hide=hide, show=show)


if __name__ == "__main__":
    """
    Command line script invocation.
    """
    global args  # promote to global scope for use in other functions
    argp = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    argp.add_argument("resource", type=str, help="resource name")
    argp.add_argument("--noid", action="store_true", default=False, dest="noid", help="hide resource object UUIDs")
    argp.add_argument("-d", "--details", action="store_true", default=False, help="get ERS resource details")
    argp.add_argument("-e", "--expiration", type=int, default=3600, help="cache expiration, in seconds")
    argp.add_argument(
        "-f",
        "--format",
        choices=["csv", "id", "grid", "table", "json", "line", "pretty", "yaml"],
        default="table",
        help="output format or styling",
    )
    argp.add_argument("-i", "--insecure", action="store_true", default=False, help="do not verify certificates (allow self-signed certs)")
    argp.add_argument("-n", "--nocache", action="store_true", default=False, help="use caching to improve performance")
    argp.add_argument("-s", "--save", default="-", required=False, help="save output to specified directory. Default: stdout")
    argp.add_argument("-t", "--timer", action="store_true", default=False, help="show total runtime, in seconds")
    argp.add_argument("-v", "--verbosity", action="count", default=0, help="verbosity; multiple allowed")
    argp.add_argument("--hide", help="comma-separated attributes (columns) to hide", type=str, default=None, required=False)
    argp.add_argument("--show", help="comma-separated attributes (columns) to show", type=str, default=None, required=False)
    argp.add_argument("--vars", type=str, default=None, help="substitute variables in URLs: key1=val1,key2=val2")
    args = argp.parse_args()

    if args.timer:
        start_time = time.time()

    # parse vars into a dict for URL variables ($id, $name, $hostname, etc.)
    vars_dict = None
    if args.vars:
        vars_dict = {}
        pairs = args.vars.split(",")
        for pair in pairs:
            key, val = pair.split("=")
            vars_dict[key.strip()] = val.strip()

    if args.resource.lower() == "all":
        for resource in ISE_REST_ENDPOINTS.keys():
            asyncio.run(
                get(
                    resource=resource,
                    details=args.details,
                    filepath=args.save,
                    format=args.format,
                    noid=args.noid,
                    insecure=args.insecure,
                    hide=args.hide,
                    show=args.show,
                    vars=vars_dict,
                )
            )
    else:
        asyncio.run(
            get(
                resource=args.resource,
                details=args.details,
                filepath=args.save,
                format=args.format,
                noid=args.noid,
                insecure=args.insecure,
                hide=args.hide,
                show=args.show,
                vars=vars_dict,
            )
        )

    if args.timer:
        print(f"⏲ {'{0:.3f}'.format(time.time() - start_time)} seconds", file=sys.stderr)
