#!/usr/bin/env python3
"""
Generate the specified number of random ISE endpoint resources.
This script only generates the endpoint data and does not upload or create the endpoints in ISE.

Examples:
  make-ise-endpoint.py -h
  make-ise-endpoint.py -n 10
  make-ise-endpoint.py --format yaml --group random --number 6
  make-ise-endpoint.py -vtn 1000 --group IOT
  make-ise-endpoint.py -tvf csv -g random -n 1000000 > endpoints_1M.csv  # ⏱ 10.287 seconds

You may add these export lines to a text file and load with `source`:
  source ise-env.sh

"""
__author__ = "Thomas Howard"
__email__ = "thomas@cisco.com"
__license__ = "MIT - https://mit-license.org/"

import aiohttp
import asyncio
import argparse
import csv
import datetime
import io
import json
import logging
import os
import pandas as pd
import random
import re
import requests
import sys
import time
import yaml

FORMATS = ["csv", "json", "pretty", "line", "yaml"]
FORMAT_DEFAULT = "json"

# Create a logger to sys.stderr
logging.basicConfig(stream=sys.stderr, format="%(asctime)s.%(msecs)03d | %(levelname)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
log = logging.getLogger(__file__)

# ISE 3.4 Context Visibility > Export, ✔ "Importable only"
# ⚠ Note that ISE does not include custom endpoint attributes for import
ISE_CV_DEFAULT_ENDPOINT_EXPORT_COLUMNS = [
    "MACAddress",
    "EndPointPolicy",
    "IdentityGroup",
    "Description",
    # "DeviceRegistrationStatus",
    # "BYODRegistration",
    # "Device Type",
    # "EmailAddress",
    # "ip",
    # "FirstName",
    # "host-name",
    # "LastName",
    # "MDMServerID",
    # "MDMServerName",
    # "MDMEnrolled",
    # "Location",
    # "PortalUser",
    "User-Name",
    "StaticAssignment",
    "StaticGroupAssignment",
    # "MDMOSVersion",
    # "PortalUser.FirstName",
    # "PortalUser.LastName",
    # "PortalUser.EmailAddress",
    # "PortalUser.PhoneNumber",
    # "PortalUser.GuestType",
    # "PortalUser.GuestStatus",
    # "PortalUser.Location",
    # "PortalUser.GuestSponsor",
    # "PortalUser.CreationType",
    # "AUPAccepted",
]

endpoint_groups_registry = {}  # id : name
mac_registry = {}


def load_ieee_oui_dict(expiration: datetime.timedelta = datetime.timedelta(days=7)):
    """
    Return a dict of IEEE {OUI:Organization}, downloading the data from the IEEE, if necessary.
    """
    IEEE_OUI_URL = "https://standards-oui.ieee.org/oui/oui.txt"
    IEEE_OUI_TXT_FILENAME = "ieee_ouis.txt"
    IEEE_OUI_CSV_FILENAME = "ieee_ouis.csv"

    # use a fake User-Agent or they will reject your requests as a bot
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0"}

    def download(url: str = None, headers: dict = None):
        log.critical(f"load_ieee_oui_dict().download({IEEE_OUI_URL})")
        try:
            response = requests.get(IEEE_OUI_URL, headers=headers)
            with open(IEEE_OUI_TXT_FILENAME, "w") as file:
                file.write(response.text)
                log.critical(f"load_ieee_oui_dict().download(): Saved {IEEE_OUI_TXT_FILENAME}")
        except requests.exceptions.ConnectionError:
            log.error(f"load_ieee_oui_dict().download(): Connection problem.")

    # Download IEEE OUIs locally if missing or older than `expiration`
    if not os.path.exists(IEEE_OUI_TXT_FILENAME):
        # No OUI file - download it
        download(IEEE_OUI_URL, headers)
    else:
        # Check file modification, cache expiration, document Last-Modified header before downloading
        now_dt = datetime.datetime.now()
        ouis_text_modified_ts = os.path.getmtime(IEEE_OUI_TXT_FILENAME)
        ouis_text_modified_dt = datetime.datetime.fromtimestamp(ouis_text_modified_ts)
        ouis_text_expired_dt = ouis_text_modified_dt + expiration  # expire after `expiration` timedelta
        log.critical(f"{IEEE_OUI_TXT_FILENAME} modified @ {ouis_text_modified_dt} expires @ {ouis_text_expired_dt} ({expiration})")

        if ouis_text_modified_ts > ouis_text_expired_dt.timestamp():
            response = requests.head(IEEE_OUI_URL, headers=headers)
            log.critical(f"response.headers: {response.headers}")

            # Convert Last-Modified to timestamp for easy comparison: ['Last-Modified']: Thu, 26 Dec 2024 17:01:23 GMT
            url_last_modified_ts = datetime.datetime.strptime(response.headers["Last-Modified"], "%a, %d %b %Y %H:%M:%S %Z").timestamp()
            url_last_modified_dt = datetime.datetime.fromtimestamp(url_last_modified_ts)
            log.critical(f"{IEEE_OUI_URL} modified {response.headers['Last-Modified']} ({url_last_modified_dt.strftime(FS_ISO8601_DT)})")
            if url_last_modified_ts > ouis_text_modified_ts:  # URL is newer?
                download(IEEE_OUI_URL, headers)

    # Invalid OUI file?
    if os.path.getsize(IEEE_OUI_TXT_FILENAME) < 1000000:
        log.debug(f"Invalid size: {IEEE_OUI_TXT_FILENAME}: Verify HTTP User-Agent ")
        raise Exception("Invalid OUI file - should be much larger")

    # Parse IEEE OUIs for only the "base 16" lines
    if not os.path.exists(IEEE_OUI_CSV_FILENAME):
        with open(IEEE_OUI_TXT_FILENAME, "r") as file:
            lines = file.readlines()
            oui_table = [["OUI", "Organization"]]  # list of lists for CSV file
            for line in lines:
                if re.search(r"\s+\(base 16\)\s+", line):
                    # 00000C     (base 16)		Cisco Systems, Inc
                    oui, org = re.split(r"\s+\(base 16\)\s+", line)
                    oui_table.append([oui.strip(), org.strip()])
            log.debug(f"IEEE OUI base16 lines parsed")

        # Save filtered oui_table to CSV file
        with open(IEEE_OUI_CSV_FILENAME, "w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerows(oui_table)
            log.info(f"Saved {IEEE_OUI_CSV_FILENAME}")

    # Read CSV ["OUI", "Organization"] into MAC lookup dictionary
    with open(IEEE_OUI_CSV_FILENAME, "r", newline="") as csvfile:
        csv_reader = csv.reader(csvfile)
        oui_dict = {}
        for row in csv_reader:
            if row:  # Ensure the row is not empty
                oui_dict[row[0]] = row[1]  # { "OUI" : "Organization" }
        log.info(f"Created `oui_dict` from {IEEE_OUI_CSV_FILENAME}")
        return oui_dict


def get_ouis_by_org(org: str = None):
    """
    Returns a list of OUIs containing the org string in the organization field.
    """
    return df_ouis[df_ouis.Organization.str.lower().str.contains(org.lower())]["OUI"].tolist()


def endpoint_to_csv(endpoint: dict = None, group: str = "Unknown") -> dict:
    """
    Returns a dictionary mapping endpoint attributes to an importable endpoint CSV format.

    :param endpoint (dict) : a dictionary representing an endpoint
    """
    return {
        "MACAddress": endpoint.get("mac", ""),
        "EndPointPolicy": endpoint.get("endpointPolicy", ""),  # 🚧 ToDo: endpoint profile id?
        "IdentityGroup": endpoint.get("groupId", "Unknown"),
        "Description": endpoint.get("description", ""),
        # 'DeviceRegistrationStatus' : 'NotRegistered',
        # 'BYODRegistration' : 'Unknown',
        # 'Device Type' : 'Device Type#All Device Types#T-800',
        # 'EmailAddress' : None,
        # 'ip' : None,
        # 'FirstName' : None,
        # 'host-name' : None,
        # 'LastName' : None,
        # 'MDMServerID' : None,
        # 'MDMServerName' : None,
        # 'MDMEnrolled' : None,
        # 'Location' : 'Location#All Locations#AMER#US#XYZ',
        # 'PortalUser' : None,
        "User-Name": endpoint.get("name", ""),
        "StaticAssignment": endpoint.get("staticProfileAssignment", "false"),
        "StaticGroupAssignment": endpoint.get("staticGroupAssignment", "false"),
        # 'MDMOSVersion' : None,
        # 'PortalUser.FirstName' : None,
        # 'PortalUser.LastName' : None,
        # 'PortalUser.EmailAddress' : None,
        # 'PortalUser.PhoneNumber' : None,
        # 'PortalUser.GuestType' : None,
        # 'PortalUser.GuestStatus' : None,
        # 'PortalUser.Location' : None,
        # 'PortalUser.GuestSponsor' : None,
        # 'PortalUser.CreationType' : None,
        # 'AUPAccepted' : None,
    }


def get_random_mac(oui: str = None):
    """
    Returns a unique MAC address with the format `XX:XX:XX:XX:XX:XX`.

    :param oui (str) (optional) an organizationally unique identifier of the MAC address
    """
    SEP = ":"  # byte separator
    oui = "{:06X}".format(random.randint(1, 16777216)) if oui is None else oui  # 16777216 == 2^24
    nic = random.randint(1, 16777216)  # starting number for MAC's NIC address
    mac = SEP.join([(oui + "{:06X}".format(nic))[idx : idx + 2] for idx in range(0, 12, 2)])  # Format MAC XX:XX:XX:XX:XX:XX
    while mac in mac_registry:
        mac = SEP.join([(oui + "{:06X}".format(nic + 1))[idx : idx + 2] for idx in range(0, 12, 2)])
    mac_registry[mac] = True
    return mac


def get_endpointgroup_id(name: str = "Unknown"):
    """
    Returns the id of the endpoint group with the specified name, otherwise `None`.

    :param name (str) : the name of the endpoint group
    """
    log.debug(f"▷ get_endpointgroup_id(name={name})", file=sys.stderr)
    names = [k for k, v in endpoint_groups_registry.items() if v == name]
    if len(names) == 0:
        return None
    return names[0]


def show(resources: list = None, format: str = FORMAT_DEFAULT, filepath: str = "-", headers: list = None, name: str = "objects"):
    """
    Show/print/dump the resources in the specified format to the file. `sys.stdout` ('-') by default.

    - resources (list) : a list of list items to show
    - headers (list) : the name of the resource. Example: endpoint, sgt, etc.
    - format (str): one the following formats:
        - `csv`   : Show the items in a Comma-Separated Value (CSV) format
        - `json`  : Show the items as a single JSON string
        - `yaml`  : Show the items as YAML with 2-space indents
    - filepath (str) : Default: `sys.stdout`
    """
    if resources == None:
        return
    if not format in FORMATS:
        raise ValueError(f"Unsupported format: {format}")
    if format == "csv" and headers is None:
        raise ValueError(f"CSV requires headers")
    if format != "csv" and name is None:
        raise ValueError(f"JSON and YAML require an object name")
    log.debug(f"▷ show({len(resources)} as {format} to {filepath})", file=sys.stderr)

    # 💡 Do not close sys.stdout or it may not be re-opened with multiple show() calls
    fh = sys.stdout if filepath == "-" else open(filepath, "w")  # write to sys.stdout/terminal by default

    if format == "csv":  # CSV
        writer = csv.DictWriter(fh, headers)  # , encoding='utf-8')
        writer.writeheader()
        writer.writerows(resources)
    elif format == "json":  # JSON, one long string
        print(json.dumps({name: resources}), file=fh)
    elif format == "line":  # 1 JSON line per object
        print("{", file=fh)
        print(f'"{name}" : [', file=fh)
        print(",\n".join([json.dumps(r) for r in resources]), file=fh)
        print("]\n}", file=fh)
    elif format == "pretty":  # pretty-print
        print(json.dumps({name: resources}, indent=2), file=fh)
    elif format == "yaml":  # YAML
        print(yaml.dump({name: resources}, indent=2, default_flow_style=False), file=fh)
    else:  # just in case something gets through the CLI parser
        log.debug(f"show(): Unknown format: {format}")


def make_endpoint(
    name: str = None,
    mac: str = None,
    description: str = None,
    group: str = None,
    group_type: str = "id",  # ['id','name']
    # profile:str=None,             # 🚧 ToDo
    # identityStore:str=None,       # 🚧 ToDo
    # customAttributes:dict=None,   # 🚧 ToDo
    # mdmAttributes:dict=None,      # 🚧 ToDo
):
    """
    Make an ISE endpoint object.

    :param name (str) : None,
    :param mac (str) : None,
    :param description (str) : None,
    :param group (str) : None,
    """
    log.debug(f"▷ make_endpoint(name={name}, mac={mac}, description={description}, group={group})")

    mac = get_random_mac()

    group = "Unknown" if group is None else group
    group = random.choice(list(endpoint_groups_registry.values())) if group == "random" else group
    group = get_endpointgroup_id(group) if group_type == "id" else group  # CSV uses name, JSON & YAML use

    # ISE OpenAPI endpoint (/ers/config/endpoint)
    endpoint = {
        "name": mac,
        "description": "",  # faker.sentence(nb_words=8), # optional
        "mac": mac,
        "profileId": None,  # optional
        "staticProfileAssignment": False,
        "staticProfileAssignmentDefined": False,  # optional
        "groupId": group,
        "staticGroupAssignment": True if group != "Unknown" else False,
        "staticGroupAssignmentDefined": True if group != "Unknown" else False,  # optional
        # 'portalUser': '',                         # optional
        # 'identityStore': 'InternalUsers',         # optional
        # 'identityStoreId': '',                    # optional
        # 'customAttributes': {                     # optional
        #     'customAttributes': { }
        # },
        # 'mdmAttributes': { },                     # optional
    }
    log.debug(f"◁ make_endpoint(): {endpoint}")
    return endpoint

    # ISE OpenAPI endpoint (/api/v1/endpoint)
    # {
    #   "id": "028436a0-ff80-11ee-996b-bacbf94e72cd",
    #   "name": "A7:F2:61:F1:D6:C6",
    #   "description": "",
    #   "customAttributes": null,
    #   "mdmAttributes": null,
    #   "groupId": "aa0e8b20-8bff-11e6-996c-525400b48521",
    #   "identityStore": "",
    #   "identityStoreId": "",
    #   "mac": "A7:F2:61:F1:D6:C6",
    #   "portalUser": "",
    #   "profileId": "",
    #   "ipAddress": null,
    #   "vendor": null,
    #   "productId": null,
    #   "serialNumber": null,
    #   "deviceType": null,
    #   "softwareRevision": null,
    #   "hardwareRevision": null,
    #   "protocol": null,
    #   "staticGroupAssignment": false,
    #   "staticProfileAssignment": false,
    #   "assetId": null,
    #   "assetName": null,
    #   "assetIpAddress": null,
    #   "assetVendor": null,
    #   "assetProductId": null,
    #   "assetSerialNumber": null,
    #   "assetDeviceType": null,
    #   "assetSwRevision": null,
    #   "assetHwRevision": null,
    #   "assetProtocol": null,
    #   "assetConnectedLinks": null
    # }


if __name__ == "__main__":
    """
    Entrypoint for local script.
    """
    argp = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    argp.add_argument("-n", "--number", action="store", type=int, default=1, help="number of endpoints to create", required=False)
    argp.add_argument("-f", "--format", choices=FORMATS, default="yaml", help="Output format or styling")
    argp.add_argument("-g", "--group", action="store", type=str, default="Unknown", help="endpoint group name; `random` chooses randomly")
    argp.add_argument("-l", "--level", default="WARNING", choices=[("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")], help="logging level")
    argp.add_argument("-t", "--timer", action="store_true", default=False, help="show total runtime, in seconds")
    args = argp.parse_args()

    if args.timer:
        start_time = time.time()

    oui_dict = load_ieee_oui_dict()  # { "OUI" : "Organization" }
    df_ouis = pd.DataFrame(data={"OUI": list(oui_dict.keys()), "Organization": list(oui_dict.values())}).drop(index=0)
    print(df_ouis)
    # print(df_ouis.reset_index())
    # log.debug(f"Got OUIs", file=sys.stderr)
    # log.debug(f"IEEE OUIs: {len(df_ouis)}", file=sys.stderr)
    # log.debug(f"- Cisco OUIs: {len(df_ouis[df_ouis.Organization.str.contains('Cisco')])}", file=sys.stderr)
    # log.debug(f"- Meraki OUIs: {len(df_ouis[df_ouis.Organization.str.contains('Meraki')])}", file=sys.stderr)
    # log.debug(f"-  Orgs:\n{df_ouis.Organization.value_counts()}", file=sys.stderr)
    # log.debug(f"Cisco OUIs: {df_ouis[df_ouis.Organization.str.contains('Cisco')]['OUI'].tolist()}", file=sys.stderr)
    # log.debug(f"get_ouis_by_org('cisco'): {get_ouis_by_org('cisco')}", file=sys.stderr)

    # 💡 Cache endpoint group ids & names - there is no guarantee of consistent ids across ISE deployments even for default groups
    # 🚧 ToDo: Implement paging for >100 endpoint groups
    response = requests.get(
        f"https://{os.environ.get('ISE_PPAN')}/ers/config/endpointgroup?&size=100",
        auth=(os.environ.get("ISE_REST_USERNAME"), os.environ.get("ISE_REST_PASSWORD")),
        headers={"Accept": "application/json"},
        verify=(False if os.environ.get("ISE_VERIFY")[0].lower() in ["f", "n"] else True),
    )
    for item in (response.json())["SearchResult"]["resources"]:
        endpoint_groups_registry[item["id"]] = item["name"]  # cache id to name

    endpoints = []
    for idx in range(1, args.number + 1):
        endpoints.append(make_endpoint(group=args.group, group_type=("id" if args.format == "json" else "name")))

    if args.format == "csv":
        endpoints = [endpoint_to_csv(endpoint) for endpoint in endpoints]  # return [dict] for CSV

    show(endpoints, format=args.format, filepath="-", name="endpoint", headers=ISE_CV_DEFAULT_ENDPOINT_EXPORT_COLUMNS)

    if args.timer:
        log.debug(f"⏱ {'{0:.3f}'.format(time.time() - start_time)} seconds")
