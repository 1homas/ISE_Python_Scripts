#!/usr/bin/env python3
"""

Show all of the endpoints assigned an "Unknown" endpoint policy by ISE and any matching IEEE OUI organization.
The ISE Profiling Feed Service updates OUIs but it is missing some from the IEEE OUI registry.
This script identifies all endpoints in an ISE deployment with Unknown profiles and matches IEEE OUI registry organizations.

Example:
  ise-endpoints-profile-unknown.py

Required environment variables:
  export ISE_PMNT='1.2.3.4'             # hostname or IP address of ISE Primary MNT
  export ISE_DC_PASSWORD='D@t@C0nnect'  # Your ISE Data Connect password
  export ISE_VERIFY=False               # Optional: Disable TLS certificate verification (allow self-signed certs)

You may add these export lines to a text file and load with `source`:
  source ~/.secrets/ise-dataconnect.sh

"""
__author__ = "Thomas Howard"
__email__ = "thomas@cisco.com"
__license__ = "MIT - https://mit-license.org/"

from isedc import ISEDC
import argparse
import csv
import datetime
import logging
import os
import re
import requests
import signal
import string
import sys
import tabulate
import time

FS_ISO8601_DT = "%Y-%m-%d %H:%M:%S"  # 2024-11-05 00:15:40 local time
TR_NO_PUNCTUATION = str.maketrans("", "", string.punctuation)  # remove delimiters from MAC address

# SQL_FILENAME = "data/SQL/endpoints_first_auth.sql"
SQL_ENDPOINTS_CREATED = """
SELECT
    mac_address,
    CASE WHEN REGEXP_LIKE(mac_address, '^.[26AE].*', 'i') THEN 'true' ELSE 'false' END AS is_random, -- random MAC feature column: ✔ ⚀, ⚁, ⚂, ⚃, ⚄, ⚅
    TO_CHAR(create_time, 'YYYY-MM-DD HH24:MI:SS') AS created, -- time when record added; drop fractional seconds
    endpoint_policy, -- endpoint profile classification
    matched_value AS cf -- Matched Certainty Factor (CF)
FROM endpoints_data
ORDER BY mac_address ASC
"""

# Create a default logger to sys.stderr
logging.basicConfig(
    stream=sys.stderr,
    format="%(asctime)s.%(msecs)03d | %(levelname)s | %(module)s | %(funcName)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger()


def load_ieee_oui_dict(expiration: datetime.timedelta = datetime.timedelta(days=7)):
    """
    Return a dict of IEEE {OUI:Organization}, downloading the data from the IEEE, if necessary.
    """
    IEEE_OUI_URL = "https://standards-oui.ieee.org/oui/oui.txt"
    IEEE_OUI_TXT_FILENAME = "ieee_ouis.txt"
    IEEE_OUI_CSV_FILENAME = "ieee_ouis.csv"
    # use a fake User-Agent or the IEEE site will reject your requests as a bot
    USER_AGENT_HEADER = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0"}

    def download(url: str = None, headers: dict = None):
        log.critical(f"load_ieee_oui_dict().download({IEEE_OUI_URL})")
        try:
            response = requests.get(IEEE_OUI_URL, headers=USER_AGENT_HEADER)
            with open(IEEE_OUI_TXT_FILENAME, "w") as file:
                file.write(response.text)
                log.critical(f"load_ieee_oui_dict().download(): Saved {IEEE_OUI_TXT_FILENAME}")
        except requests.exceptions.ConnectionError:
            log.error(f"load_ieee_oui_dict().download(): Connection problem.")

    # Download IEEE OUIs locally if missing or older than `expiration`
    if not os.path.exists(IEEE_OUI_TXT_FILENAME):
        # No OUI file - download it
        download(IEEE_OUI_URL, USER_AGENT_HEADER)
    else:
        # Check file modification, cache expiration, document Last-Modified header before downloading
        now_dt = datetime.datetime.now()
        ouis_text_modified_ts = os.path.getmtime(IEEE_OUI_TXT_FILENAME)
        ouis_text_modified_dt = datetime.datetime.fromtimestamp(int(ouis_text_modified_ts))  # use int() to drop μseconds
        ouis_text_expired_dt = ouis_text_modified_dt + expiration  # expire after `expiration` timedelta

        if now_dt.timestamp() > ouis_text_expired_dt.timestamp():
            log.info(f"IEEE file expired: {now_dt} (now) > {ouis_text_expired_dt} text expiration")

            response = requests.head(IEEE_OUI_URL, headers=USER_AGENT_HEADER)
            log.info(f"IEEE OUI HEAD Request: {response.headers}")

            # Convert Last-Modified to timestamp for easy comparison: ['Last-Modified']: Thu, 26 Dec 2024 17:01:23 GMT
            url_last_modified_ts = datetime.datetime.strptime(response.headers["Last-Modified"], "%a, %d %b %Y %H:%M:%S %Z").timestamp()
            url_last_modified_dt = datetime.datetime.fromtimestamp(url_last_modified_ts)
            log.info(f"{IEEE_OUI_URL} modified {response.headers['Last-Modified']} ({url_last_modified_dt.strftime(FS_ISO8601_DT)})")

            if url_last_modified_ts > ouis_text_modified_ts:  # URL is newer?
                log.info(f"IEEE file updated: {url_last_modified_dt} > {ouis_text_expired_dt} text expiration")
                download(IEEE_OUI_URL, USER_AGENT_HEADER)
        else:
            log.info(f"IEEE file current: {ouis_text_modified_dt} < {ouis_text_expired_dt} expiration")

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
        return oui_dict


if __name__ == "__main__":
    """
    Run from script
    """
    signal.signal(signal.SIGINT, lambda signum, frame: sys.exit(0))  # Handle CTRL+C interrupts gracefully

    argp = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    argp.add_argument("-f", "--format", choices=["table", "github"], default="table", help="output format or styling")
    argp.add_argument("-i", "--insecure", action="store_true", default=False, help="do not verify certificates (allow self-signed certs)")
    argp.add_argument("-l", "--level", default="WARNING", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], help="log threshold")
    argp.add_argument("-t", "--timer", action="store_true", default=False, help="show total runtime, in seconds")
    args = argp.parse_args()

    log.setLevel(args.level)

    if args.timer:
        start_time = time.time()

    oui_dict = load_ieee_oui_dict()

    with ISEDC(hostname=os.environ.get("ISE_PMNT"), password=os.environ.get("ISE_DC_PASSWORD"), insecure=True, level=args.level) as isedc:

        cursor = isedc.query(SQL_ENDPOINTS_CREATED)
        rows = cursor.fetchall()
        headers = [f"{column[0]}".lower() for column in cursor.description]
        all_endpoints = [dict(zip(headers, row)) for row in rows]  # make a list of dicts
        endpoints = []
        for endpoint in all_endpoints:  # unpack list of tuples
            if re.match("^.[26AE].*", endpoint["mac_address"]):
                continue  # skip random MAC addresses
            if endpoint["endpoint_policy"] != "Unknown":
                continue  # skip random MAC addresses

            # Add feature column(s)
            endpoint["oui"] = endpoint["mac_address"].strip().translate(TR_NO_PUNCTUATION)[0:6].upper()
            if endpoint["endpoint_policy"] == "Unknown" and oui_dict.get(endpoint["oui"]):
                # continue  # skip random MAC addresses
                endpoint["ieee_oui_org"] = oui_dict.get(endpoint["oui"], "Unknown")
                endpoints.append(endpoint)

        # show endpoints
        print(tabulate.tabulate(endpoints, headers="keys", tablefmt=args.format), file=sys.stdout)

    if args.timer:
        print(f"⏲ {'{0:.3f}'.format(time.time() - start_time)} seconds", file=sys.stderr)
