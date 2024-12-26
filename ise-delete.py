#!/usr/bin/env python3
"""
Delete *ALL* ISE resources via REST APIs.

Examples:
    ise-delete.py endpoint 
    ise-delete.py endpoint -tvi
    ise-delete.py -tv endpoint

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
import argparse
import asyncio
import csv
import io
import json
import math
import os
import random
import signal
import ssl
import sys
import time
import traceback

ICONS = {
    # name : icon
    "CACHE": "↯",
    "DOWN": "▽",
    "ERROR": "⛒",
    "NONE": "∅",
    "FAIL": "✖",
    "INFO": "ℹ",
    "ID": "⚿",
    "LIST": "⁝",
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
TCP_LIMIT_DEFAULT = 100  # aiohttp.TCPConnector.limit
TCP_LIMIT = 10  # 🔺ISE ERS APIs for GuestType and InternalUser can have problems with 10+ concurrent connections!
REST_PAGE_SIZE = 100

# Dictionary of ISE REST Endpoints mapping to a tuple of the object name and base URL
# 'Resource': ('ERS_Name', 'REST API Base URL')
ISE_REST_ENDPOINTS = {
    # Deployment @ https://cs.co/ise-api#!deployment-openapi
    "deployment-node": ("-", "/api/v1/deployment/node"),
    "node-group": ("-", "/api/v1/deployment/node-group"),
    "pan-ha": ("-", "/api/v1/deployment/pan-ha"),
    # 'node-interface': ('-', '/api/v1/node/{hostname}/interface'), # 💡 requires ISE node hostname
    # 'sxp-interface': ('-', '/api/v1/node/{hostname}/sxp-interface'), # 💡 requires ISE node hostname
    # 'profile': ('-', '/api/v1/profile/{hostname}'), # 💡 requires ISE node hostname
    "repository": ("-", "/api/v1/repository"),  # Repository @ https://cs.co/ise-api#!repository-openapi
    # 'repository-name': ('-', '/api/v1/repository/{name}'), # 💡 requires repository {name}
    # 'repository-name-files': ('-', '/api/v1/repository/{name}/files'),# 💡 requires repository {name}
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
    # 'trusted-certificate-by-id': ('-', '/api/v1/certs/trusted-certificate/{id}'), # Get Trust Certificate By ID
    # 'system-certificate': ('-', '/api/v1/certs/system-certificate/{hostName}'), # 💡 requires ISE node hostname
    "certificate-signing-request": ("-", "/api/v1/certs/certificate-signing-request"),
    # 'system-certificate-by-name': ('-', '/api/v1/certs/system-certificate/{hostName}'), # 💡 requires ISE node hostname. Get all system certificates of a particular node
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
    # 'ldap-by-name': ('???', '/ers/config/ldap/name/{name}'),
    # 'ldap-by-id': ('???', '/ers/config/ldap/{id}'),
    # Duo MFA
    "duo-sync-ads": ("-", "/api/v1/duo-identitysync/activedirectories"),  # Get the list of all configured Active Directories
    # 'duo-sync-groups': ('-', '/api/v1/duo-identitysync/adgroups/{activeDirectory}'), # 💡 requires id for a list of all groups in the specified AD
    "duo-identitysync": ("-", "/api/v1/duo-identitysync/identitysync"),  # Get the list of all Identitysync configurations
    "duo-mfa": ("-", "/api/v1/duo-mfa/mfa"),  # Get the list of all Duo-MFA configurations
    # 'duo-mfa-enable': ('-', '/api/v1/duo-mfa/enable'), # PUT Enable MFA feature
    # 'duo-mfa-by-name': ('-', '/api/v1/duo-mfa/mfa/{connectionName}'), # Get the specified Duo-MFA configuration
    "duo-mfa-status": ("-", "/api/v1/duo-mfa/status"),  # MFA feature enabled status
    # pxGrid Direct @ https://cs.co/ise-api#!pxgrid-direct-open-api
    "pxgd-config": ("-", "/api/v1/pxgrid-direct/connector-config"),
    # 'pxgd-config-by-name': ('-', '/api/v1/pxgrid-direct/connector-config/{name}'),
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
    # 'sgt-reservation-by-id': ('-', '/api/v1/sgt/reservation/{clientID}'), # 💡 Requires {id}. Get the reserved range for the specific Client.
    # SDA/TrustSec @ https://cs.co/ise-api#!trustsec-openapi
    "trustsec-sgacl-nbarapp": ("-", "/api/v1/trustsec/sgacl/nbarapp"),
    "trustsec-sgvnmapping": ("-", "/api/v1/trustsec/sgvnmapping"),
    "trustsec-virtualnetwork": ("-", "/api/v1/trustsec/virtualnetwork"),
    "trustsec-vnvlanmapping": ("-", "/api/v1/trustsec/vnvlanmapping"),
    "profilerprofile": ("ProfilerProfile", "/ers/config/profilerprofile"),  # Endpoint Profiles @ https://cs.co/ise-api#!profilerprofile
    # Endpoints
    "endpointgroup": ("EndPointGroup", "/ers/config/endpointgroup"),  # EndpointGroups @ https://cs.co/ise-api#!endpointgroup
    "endpoint-custom-attribute": ("-", "/api/v1/endpoint-custom-attribute"),
    # 'endpoint-custom-attribute-by-name': ('-', '/api/v1/endpoint-custom-attribute/{name}'), # Get custom attribute by name
    # 'endpoint-stop-replication': ('-', '/api/v1/stop-replication'),    # Endpoint Stop Replication Service
    "endpoint": ("ERSEndPoint", "/ers/config/endpoint"),  # Endpoint @ https://cs.co/ise-api#!endpoint
    # 'endpointcert': ('ERSEndPointCert', '/ers/config/endpointcert'),  # 🛑 No GET; POST only
    "endpoints": ("-", "/api/v1/endpoint"),  # 💡 Requires ISE 3.2. Endpoints @ https://cs.co/ise-api#!get-all-endpoints
    # 'endpoint-value': ('-', '/api/v1/endpoint/{value}'), # 💡 Requires {value}
    # 'endpoint-summary': ('-', '/api/v1/endpoint/deviceType/summary'), # 🛑 404?
    # TACACS+
    "tacacscommandsets": ("TacacsCommandSets", "/ers/config/tacacscommandsets"),  # TACACS @ https://cs.co/ise-api#!tacacscommandsets
    "tacacsexternalservers": (
        "TacacsExternalServer",
        "/ers/config/tacacsexternalservers",
    ),  # 💡 404 if none configured. TACACS @ https://cs.co/ise-api#!tacacsexternalservers
    "tacacsprofile": ("TacacsProfile", "/ers/config/tacacsprofile"),  # TACACS @ https://cs.co/ise-api#!tacacsprofile
    "tacacsserversequence": (
        "TacacsServerSequence",
        "/ers/config/tacacsserversequence",
    ),  # 💡 404 if none configured. TACACS @ https://cs.co/ise-api#!tacacsserversequence
    # Policy Sets - RADIUS Network Access
    # ERS policy elements
    "allowedprotocols": ("AllowedProtocols", "/ers/config/allowedprotocols"),
    "authorizationprofile": ("AuthorizationProfile", "/ers/config/authorizationprofile"),
    "downloadableacl": ("DownloadableAcl", "/ers/config/downloadableacl"),
    "filterpolicy": ("ERSFilterPolicy", "/ers/config/filterpolicy"),  # 404 if none configured
    # Network Access Policy @ https://cs.co/ise-api#!policy-openapi
    # ⓘ Network Access policy is the assumed default; prefix "na-" not required
    "na-authorization-profiles": ("-", "/api/v1/policy/network-access/authorization-profiles"),
    # 'condition-id': ('-', '/api/v1/policy/network-access/condition/{conditionId}'),
    "na-condition-policyset": ("-", "/api/v1/policy/network-access/condition/policyset"),
    "na-condition-authn": ("-", "/api/v1/policy/network-access/condition-authentication"),
    "na-condition-authz": ("-", "/api/v1/policy/network-access/condition-authorization"),
    "na-dicts": ("-", "/api/v1/policy/network-access/dictionaries"),
    # 'dict-name': ('-', '/api/v1/policy/network-access/dictionaries/{name}'), # 💡 Requires {name}
    "na-dict-authn": ("-", "/api/v1/policy/network-access/dictionaries/authentication"),
    "na-dict-authz": ("-", "/api/v1/policy/network-access/dictionaries/authorization"),
    "na-dict-policyset": ("-", "/api/v1/policy/network-access/dictionaries/policyset"),
    "na-identity-stores": ("-", "/api/v1/policy/network-access/identity-stores"),
    "na-network-condition": ("-", "/api/v1/policy/network-access/network-condition"),
    "na-policy-set": ("-", "/api/v1/policy/network-access/policy-set"),
    # 'policy-set-id': ('-', '/api/v1/policy/network-access/policy-set/{id}'),
    # 'policy-set-id-authn': ('-', '/api/v1/policy/network-access/policy-set/{policyId}/authentication'),
    # 'policy-set-id-authz': ('-', '/api/v1/policy/network-access/policy-set/{policyId}/authorization'),
    # 'policy-set-id-exception': ('-', '/api/v1/policy/network-access/policy-set/{policyId}/exception'),
    "na-global-exception": ("-", "/api/v1/policy/network-access/policy-set/global-exception"),
    "na-security-groups": ("-", "/api/v1/policy/network-access/security-groups"),
    "na-service-names": ("-", "/api/v1/policy/network-access/service-names"),
    "na-time-condition": ("-", "/api/v1/policy/network-access/time-condition"),
    # Policy Sets - TACACS+ Device Admin @ https://cs.co/ise-api#!policy-openapi
    # ⓘ All Device Admin policy objects have the prefix "da-"
    "da-command-sets": ("-", "/api/v1/policy/device-admin/command-sets"),
    "da-condition": ("-", "/api/v1/policy/device-admin/condition"),
    # 'da-condition-id': ('-', '/api/v1/policy/device-admin/condition/{conditionId}'),
    "da-condition-policyset": ("-", "/api/v1/policy/device-admin/condition/policyset"),
    "da-condition-authn": ("-", "/api/v1/policy/device-admin/condition-authentication"),
    "da-condition-authz": ("-", "/api/v1/policy/device-admin/condition-authorization"),
    "da-dict-authn": ("-", "/api/v1/policy/device-admin/dictionaries/authentication"),
    "da-dict-authz": ("-", "/api/v1/policy/device-admin/dictionaries/authorization"),
    "da-dict-policyset": ("-", "/api/v1/policy/device-admin/dictionaries/policyset"),
    "da-identity-stores": ("-", "/api/v1/policy/device-admin/identity-stores"),
    "da-policy-set": ("-", "/api/v1/policy/device-admin/policy-set"),
    # 'da-policy-set-id': ('-', '/api/v1/policy/device-admin/policy-set/{id}'), # 💡 requires {id}
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
    # 'guestuser': ('GuestUser', '/ers/config/___GuestUser__'), # 🛑 requires sponsor account!!!
    # 'smsprovider': ('SmsProviderIdentification', '/ers/config/smsprovider'),
    "sponsorgroup": ("SponsorGroup", "/ers/config/sponsorgroup"),
    "sponsorgroupmember": ("SponsorGroupMember", "/ers/config/sponsorgroupmember"),
    # BYOD
    "certificateprofile": ("CertificateProfile", "/ers/config/certificateprofile"),
    "certificatetemplate": ("ERSCertificateTemplate", "/ers/config/certificatetemplate"),
    "byodportal": ("BYODPortal", "/ers/config/byodportal"),
    "mydeviceportal": ("MyDevicePortal", "/ers/config/mydeviceportal"),
    "nspprofile": ("ERSNSPProfile", "/ers/config/nspprofile"),
    "ipsec": ("ipsec", "/api/v1/ipsec"),  # IPsec @ https://cs.co/ise-api#!ipsec-openapi
    # 'ipsec': ('ipsec', '/api/v1/ipsec/{hostName}/{nadIp}'),
    "ipsec-certificates": ("ipsec-certificates", "/api/v1/ipsec/certificates"),
    # Support / Operations
    # 'supportbundle': ('_____', '/ers/config/supportbundle'),
    # 'supportbundledownload': ('_____', '/ers/config/_____'),
    # 'supportbundlestatus': ('_____', '/ers/config/_____'),
    # Task
    "task": ("-", "/api/v1/task"),
    # 'task-id': ('-', '/api/v1/task/{id}'),
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
    # FiveG
    # '': ('-', ''),
}


async def get_url_response(session, url_q, response_q):
    """
    Take a URL from the queue, use the session to GET a response and put it in the response_q.

    :param session (aiohttp.ClientSession): the aiohttp session to reuse
    :param url_q (asyncio.Queue) : the queue of URLs to GET using the session
    :param response_q (asyncio.Queue) : the queue for all responses
    """
    while True:
        url = await url_q.get()  # Wait for item in the queue
        response = await session.get(url)
        data = await response.json()
        if args.verbosity == 1:
            print(ICONS["DOWN"], end="", flush=True, file=sys.stderr)
        await response_q.put(data)
        url_q.task_done()  # Notify queue item is done


async def extract_ise_resources(response_q: asyncio.Queue = None, resource_q: asyncio.Queue = None):
    """
    Extract the JSON resource(s) from the ISE REST API response and add them to the resource queue for further processing.

    :param response_q (asyncio.Queue) : the queue for all responses
    :param resource_q (asyncio.Queue) : the queue for extracted resources
    """
    while True:
        data = await response_q.get()  # Wait for data in the queue
        if args.verbosity == 1:
            print(ICONS["LIST"], end="", flush=True, file=sys.stderr)
        if isinstance(data, dict):  # ISE ERS API is a dict: {'SearchResult': {'total': 7, 'resources': [{'id': ... }]}}
            resources = data["SearchResult"]["resources"]
        elif isinstance(data, list):  # OpenAPI is a list: []
            resources = data
        else:
            print(f"extract_ise_resources(): Unsupported data type: {data}")
        for resource in resources:
            if args.verbosity >= 3:
                print(f"{ICONS['PLAY']} {resource['id']} | {resource['name']}")
            await resource_q.put(resource)
        response_q.task_done()  # Notify queue item is done


async def delete_ise_resource_by_id(session: aiohttp.ClientSession = None, path: str = None, resource_q: asyncio.Queue = None):
    """
    Delete the specified resource using it's id.

    :param session (aiohttp.ClientSession): the aiohttp session to reuse
    :param path (str) : the REST API endpoint path
    :param resource_q (asyncio.Queue) : the asyncio Queue for ERS resource pages to fetch
    """
    while True:
        resource = await resource_q.get()  # Wait for item in the queue
        try:
            response = await session.delete(f"{path}/{resource['id']}")
            if response.ok:
                if args.verbosity == 1:
                    print(f"{ICONS['PASS']}", end="", flush=True, file=sys.stderr)
                if args.verbosity >= 2:
                    print(f"{ICONS['PASS']} {response.status} | {resource['id']} | {resource['name']}", file=sys.stdout)
            else:
                if args.verbosity == 1:
                    print(f"{ICONS['FAIL']}", end="", flush=True, file=sys.stderr)
                if args.verbosity >= 2:
                    print(
                        f"{ICONS['FAIL']} {response.status} | {resource['id']} | {resource['name']} : {(await response.json()).popitem()[1]['messages'][0]['title']}",
                        file=sys.stdout,
                    )
        except Exception as e:  # catch *all* exceptions
            tb_text = "\n".join(traceback.format_exc().splitlines()[1:])  # remove 'Traceback (most recent call last):'
            print(f"{ICONS['ERROR']} {e.__class__} {tb_text}", file=sys.stderr)
        finally:
            resource_q.task_done()  # Notify queue item is done


async def ise_delete(resource_name: str = None):
    """
    Entrypoint for packaged script.
    """
    if args.verbosity:
        print(f"{ICONS['INFO']} Deleting all '{resource_name}'", file=sys.stderr)
    name, path = ISE_REST_ENDPOINTS[resource_name.strip(", ")]

    env = {k: v for (k, v) in os.environ.items() if k.startswith("ISE_")}  # Load environment variables
    verify_ssl = False if args.insecure or env["ISE_CERT_VERIFY"][0:1].lower() in ["f", "n"] else True
    async with aiohttp.ClientSession(
        f"https://{env['ISE_PPAN']}",
        auth=aiohttp.BasicAuth(login=env["ISE_REST_USERNAME"], password=env["ISE_REST_PASSWORD"]),
        connector=aiohttp.TCPConnector(limit=TCP_LIMIT, ssl=verify_ssl),
        headers={"Accept": "application/json", "Content-Type": "application/json"},
    ) as session:

        # Create queues for the processing pipeline
        url_q = asyncio.Queue()  # load up the URL pages
        response_q = asyncio.Queue(maxsize=2)  # many resources per page size
        resource_q = asyncio.Queue(maxsize=TCP_LIMIT + 1)  # don't bother making more than the connector will use!

        response = await session.get(f"{path}?size={REST_PAGE_SIZE}&page=1")
        data = await response.json()
        await response_q.put(data)

        if isinstance(data, dict):  # ISE ERS API is a dict: {'SearchResult': {'total': 7, 'resources': [{'id': ... }]}}
            total = data["SearchResult"]["total"]
            if args.verbosity:
                print(f"{ICONS['INFO']} Get {total} x '{resource_name}' ERS resource(s)", file=sys.stderr)
            resources = data["SearchResult"]["resources"]
            if total > REST_PAGE_SIZE:
                # Enqueue all page URLs beyond the initial REST page size
                urls = [
                    f"{path}?size={REST_PAGE_SIZE}&page={page}"
                    for page in range(2, 1 + int(total / REST_PAGE_SIZE) + (1 if total % REST_PAGE_SIZE else 0))
                ]
                [await url_q.put(url) for url in urls]  # enqueue URLs
        elif isinstance(data, list):  # OpenAPI is a list: []
            print(f"{ICONS['WARN']} Only the first page of OpenAPI resources is supported", file=sys.stderr)
        else:
            print(f"Unsupported resource type: {resource_name} at {path}", file=sys.stderr)

        try:
            # Schedule all fetch tasks
            url_tasks = [asyncio.create_task(get_url_response(session, url_q, response_q))]  # only 1 needed
            extract_tasks = [asyncio.create_task(extract_ise_resources(response_q, resource_q))]
            delete_tasks = [asyncio.create_task(delete_ise_resource_by_id(session, path, resource_q)) for idx in range(TCP_LIMIT * 2)]

            await url_q.join()  # Block until all items in queue are processed
            print(f"url_q joined")
            await response_q.join()
            print(f"response_q joined")
            await resource_q.join()
            print(f"resource_q joined")
        except Exception as e:
            tb_text = "\n".join(traceback.format_exc().splitlines()[1:])  # remove 'Traceback (most recent call last):'
            print(f"{ICONS['ERROR']} {e.__class__} {tb_text}", file=sys.stderr)
        finally:
            if args.verbosity == 1:
                print(flush=True, file=sys.stderr)  # newline for verbose updates
            [task.cancel() for task in (extract_tasks + url_tasks + delete_tasks)]  # Cancel all tasks


if __name__ == "__main__":
    """
    Entrypoint for local script.
    """
    global args
    argp = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    argp.add_argument("resource", type=str, help="resource name")
    argp.add_argument(
        "-i", "--insecure", action="store_true", default=False, help="do not verify certificates for TLS (allow self-signed certs)"
    )
    argp.add_argument("-t", "--timer", action="store_true", default=False, help="time", required=False)
    argp.add_argument("-v", "--verbosity", action="count", default=0, help="verbosity")
    args = argp.parse_args()
    if args.timer:
        start_time = time.time()

    loop = asyncio.get_event_loop()
    main_task = asyncio.ensure_future(ise_delete(args.resource))

    # Handle CTRL+C interrupts gracefully
    for signal in [signal.SIGINT, signal.SIGTERM]:
        loop.add_signal_handler(signal, main_task.cancel)
    try:
        loop.run_until_complete(main_task)
    finally:
        loop.close()

    if args.timer:
        print(f"⏲ {'{0:.3f}'.format(time.time() - start_time)} seconds", file=sys.stderr)
