#!/usr/bin/env python3
"""
Send a notification when a new endpoint is detected in ISE.

Notification requires a ntfy.sh account and environment variable with the topic name in the environment variable `NTFY_TOPIC`. 

"""
__author__ = "Thomas Howard"
__email__ = "thomas@cisco.com"
__license__ = "MIT - https://mit-license.org/"

from isedc import ISEDC
from pathlib import Path
from string import Template
from typing import Union
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

ENDPOINTS_RUNTIME_FILEPATH = "./.endpoints_last_run.txt"
FS_ISO8601_DT = "%Y-%m-%d %H:%M:%S"  # 2024-11-05 00:15:40 local time
FS_ISO8601_UTC = "%Y-%m-%dT%H:%M:%SZ"  # 2024-11-05T00:15:40Z (UTC)
MAX_NOTIFICATIONS = 3
NTFY_TOPIC = "1homas"
PERIOD_DEFAULT = 60  # seconds
TR_NO_PUNCTUATION = str.maketrans("", "", string.punctuation)  # remove delimiters from MAC address


# Create a default logger to sys.stderr
logging.basicConfig(
    stream=sys.stderr,
    format="%(asctime)s.%(msecs)03d | %(levelname)s | %(module)s | %(funcName)s | %(message)s",
    # format="%(asctime)s | %(levelname)s | %(module)s | %(funcName)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger()


def timestamp_to_dhms(seconds: Union[int, float] = 0) -> str:
    """
    Return the number of days, hours, minutes, and remaining seconds in the timestamp, in seconds.
    Usage:
        days, hours, minutes, seconds = timestamp_to_dhms(seconds)
        print(f"{seconds} seconds is {days}d {hours}h, {minutes}m, {seconds}s")
    """
    seconds = int(seconds)  # drop milliseconds
    days = seconds // (24 * 3600)
    seconds %= 24 * 3600  # seconds remainder from days
    hours = seconds // 3600
    seconds %= 3600  # seconds remainder from hours
    minutes = seconds // 60
    seconds %= 60  # seconds remainder from minutes

    # return (days, hours, minutes, seconds)
    return f"{days}d {hours}h {minutes}m {seconds}s"


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

        if ouis_text_modified_ts > ouis_text_expired_dt.timestamp():
            log.critical(f"{IEEE_OUI_TXT_FILENAME} modified @ {ouis_text_modified_dt} expires @ {ouis_text_expired_dt} ({expiration})")

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


def read_file(filepath: str = None) -> str:
    """
    Read and return the file contents at the filepath.
      filepath: an absolute or relative path from this script.
      returns: the file contents as a string.
    """
    assert os.path.exists(filepath)
    assert os.path.isfile(filepath)
    with open(filepath, mode="r", encoding="utf-8") as fh:
        return fh.read()


def ntfy(topic: str = None, title: str = "", data: str = None, headers: dict = {}):
    """
    Send a notification via ntfy.sh. Markdown is supported in the message body.
    """
    assert topic is not None
    assert data is not None
    assert isinstance(headers, dict)
    log.debug(f"ntfy(topic={topic}, title={title}, data={data}, headers={headers})")
    if title and isinstance(title, str) and len(title) > 0:
        headers.update({"Title": f"{title}"})
    headers.update({"Markdown": "true"})
    requests.post(f"https://ntfy.sh/{topic}", data=data.encode("utf-8"), headers=headers)


SQL_ENDPOINTS_CREATED = """
SELECT
    mac_address AS mac,
    CASE WHEN REGEXP_LIKE(mac_address, '^.[26AE].*', 'i') THEN 'true' ELSE 'false' END AS random, -- random MAC
    TO_CHAR(create_time, 'YYYY-MM-DD HH24:MI:SS') AS created, -- time when record added; drop fractional seconds
    -- hostname,
    endpoint_ip,
    endpoint_policy, -- endpoint profile classification
    -- static_group_assignment AS static_grp,
    -- static_assignment AS static, -- 
    matched_value AS cf -- Matched Certainty Factor (CF)
FROM endpoints_data
WHERE create_time >= TIMESTAMP '$timestamp' -- after time of last query
  AND NOT REGEXP_LIKE(mac_address, '^.[26AE].*') -- do not include randomized MACs
ORDER BY create_time ASC
"""


def query_endpoints(timestamp: int = 0) -> None:
    """ """
    timestamp = int(timestamp)  # remove milli/micro-seconds
    timestamp_dt_str = datetime.datetime.fromtimestamp(timestamp).strftime(FS_ISO8601_DT)
    dhms = timestamp_to_dhms(datetime.datetime.now().timestamp() - timestamp)
    log.info(f"▽ {timestamp} ⏲ {timestamp_dt_str} ⧖ {dhms} ago")

    after_dt_str = datetime.datetime.fromtimestamp(timestamp).strftime(FS_ISO8601_DT)
    sql_endpoints_created_after = Template(SQL_ENDPOINTS_CREATED).substitute(timestamp=after_dt_str)
    touch_file = Path(ENDPOINTS_RUNTIME_FILEPATH).touch(mode=0o666, exist_ok=True)
    cursor = isedc.query(sql_endpoints_created_after)
    rows = cursor.fetchall()

    if len(rows) <= 0:  # nothing to see here
        log.info(f"No new endpoints")
        return

    headers = [f"{column[0]}".lower() for column in cursor.description]
    endpoints = [dict(zip(headers, row)) for row in rows]  # make a list of dicts

    if len(rows) <= MAX_NOTIFICATIONS:
        # send endpoint details in each notification
        for endpoint in endpoints:
            endpoint["oui"] = endpoint["mac"].strip().translate(TR_NO_PUNCTUATION)[0:6].upper()
            # Add feature column(s)
            if endpoint["endpoint_policy"] == "Unknown":
                endpoint["ieee_oui_org"] = oui_dict.get(endpoint["oui"], "Unknown")
            # Repackage dictionary attributes into key-value pairs for readability
            attrs = "\n".join([f"{k}: {v}" for k, v in endpoint.items()])
            ntfy(NTFY_TOPIC, title=f"New Endpoint: {endpoint['mac']}", data=attrs, headers={"Tags": "new"})
    else:
        # summarize new endpoints to prevent a notification flood
        log.debug(f"Notify on {type(endpoints)} Endpoints")
        lines = []
        for endpoint in endpoints:
            endpoint["oui"] = endpoint["mac"].strip().translate(TR_NO_PUNCTUATION)[0:6].upper()
            lines.append(
                f"""{endpoint["mac"]} | {endpoint["endpoint_policy"]} | {endpoint["cf"]} | {oui_dict.get(endpoint["oui"], "Unknown")}"""
            )
        log.debug(f"New Endpoints: {len(lines)}\n{'\n'.join(lines)}")
        ntfy(NTFY_TOPIC, title=f"New Endpoints: {len(endpoints)}", data="\n".join(lines), headers={"Tags": "new"})

    print(tabulate.tabulate(endpoints, headers="keys", tablefmt="markdown"), file=sys.stdout)


if __name__ == "__main__":
    """
    Run from script
    """
    signal.signal(signal.SIGINT, lambda signum, frame: sys.exit(0))  # Handle CTRL+C interrupts gracefully

    argp = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    argp.add_argument("-f", "--format", choices=["table", "github"], default="table", help="output format or styling")
    argp.add_argument("-i", "--insecure", action="store_true", default=False, help="do not verify certificates (allow self-signed certs)")
    argp.add_argument("-l", "--level", default="WARNING", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], help="log threshold")
    argp.add_argument("-p", "--period", type=int, default=PERIOD_DEFAULT, help="query period, in seconds")
    args = argp.parse_args()

    log.setLevel(args.level)

    oui_dict = load_ieee_oui_dict()
    # print(list(oui_dict.keys()))
    with ISEDC(
        hostname=os.environ.get("ISE_PMNT"),
        password=os.environ.get("ISE_DC_PASSWORD"),
        insecure=True,
        level=args.level,
    ) as isedc:

        # find new endpoints since last run
        last_run = os.path.getmtime(ENDPOINTS_RUNTIME_FILEPATH) if os.path.exists(ENDPOINTS_RUNTIME_FILEPATH) else 0
        while True:
            now = datetime.datetime.now(tz=None).timestamp()  # tz=None uses the local system's timezone
            query_endpoints(timestamp=last_run)
            last_run = now
            time.sleep(args.period)  # sleep until next poll
