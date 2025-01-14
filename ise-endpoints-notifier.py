#!/usr/bin/env python3
"""
Periodically queries ISE via the Data Connect feature for new endpoints and sends a notification when new endpoint(s) are detected.
The default query period is 1 minute.
The endpoint data is augmented with the respective IEEE OUI Organization name.
You may optionally specify an initial `--after` datetime for the first query.
The default notification goes to ntfy.sh using the public `ise-endpoints-notifier` topic but you may create your own topic or alternate notification mechanism (email, SMS, webhook, etc.).

Rquired environment variables:
- ISE_PMNT
- ISE_DC_PASSWORD
- ISE_VERIFY

Optional environment variable for ntfy.sh notification topic name (account required):
- NTFY_TOPIC 

Usage:
  ise-endpoints-notifier.py --help
  ise-endpoints-notifier.py
  ise-endpoints-notifier.py --level INFO
  ise-endpoints-notifier.py --show --format github
  ise-endpoints-notifier.py --after "2025-01-01 00:00:00"

"""

__license__ = "MIT - https://mit-license.org/"

from isedc import ISEDC
from string import Template
from typing import Union
import argparse
import csv
import datetime
import logging
import mac
import os
import re
import requests
import signal
import string
import sys
import tabulate
import time

FS_ISO8601_DT = "%Y-%m-%d %H:%M:%S"  # 2024-11-05 00:15:40 local time
NTFY_TOPIC = os.environ.get("NTFY_TOPIC") or "ise-endpoints-notifier"
PERIOD_DEFAULT = 60  # seconds
PERIOD_MIN = 5  # minimum query period, in seconds. If you need realtime, use Cisco pxGrid


# Create a default logger to sys.stderr
logging.basicConfig(
    stream=sys.stderr,
    format="%(asctime)s.%(msecs)03d | %(levelname)s | %(module)s | %(funcName)s | %(message)s",
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
    seconds = int(seconds)  # drop fractional seconds from floats
    days = seconds // (24 * 3600)
    seconds %= 24 * 3600  # seconds remainder from days
    hours = seconds // 3600
    seconds %= 3600  # seconds remainder from hours
    minutes = seconds // 60
    seconds %= 60  # seconds remainder from minutes

    # return (days, hours, minutes, seconds)
    return f"{days}d {hours}h {minutes}m {seconds}s"


def ntfy(topic: str = None, title: str = "", data: str = None, headers: dict = {}):
    """
    Send a notification via ntfy.sh. Markdown is supported in the message body.
    """
    assert topic is not None
    data = data if data is not None else ""
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


def send_endpoints_notification(endpoints: [dict] = None, topic: str = NTFY_TOPIC) -> None:
    """
    Package the notification message and send via ntfy.sh.
    - endpoints ([dict]) : list of endpoint dictionaries
    - topic (str) : ntfy.sh topic name
    """
    MAX_ENDPOINTS = 3  # maximum number of endpoints to send via NTFY

    if len(endpoints) <= MAX_ENDPOINTS:
        # Repackage dictionary attributes into key-value pairs for readability in each notification
        for endpoint in endpoints:
            attrs = "\n".join([f"{k}: {v}" for k, v in endpoint.items()])
            ntfy(
                topic,
                title=f"New Endpoint: {endpoint['mac']}",
                data=attrs,
                headers={"Tags": "new"},
            )
    else:
        # headline summary only to prevent a notification flood
        log.debug(f"Notify on {type(endpoints)} Endpoints")
        ntfy(topic, title=f"New Endpoints: {len(endpoints)}", headers={"Tags": "new"})


def show(endpoints: [dict] = None, format: str = "table") -> None:
    """_summary_
    Print a table of the ISE endpoints' attributes.
    - endpoints ([dict]) : list of endpoint dictionaries
    """
    if len(endpoints) <= 0:
        return
    print(tabulate.tabulate(endpoints, headers="keys", tablefmt=format), file=sys.stdout)


def get_endpoints_after(timestamp: int = 0) -> [dict]:
    """
    Returns a list of of endpoint dictionaries for all new endpoints after `timestamp`.
    - timestamp (int) : seconds since the Unix epoch
    - returns ([dict]) : list of new endpoints as dictionaries
    """
    timestamp = int(timestamp)  # remove milli/micro-seconds
    timestamp_dt_str = datetime.datetime.fromtimestamp(timestamp).strftime(FS_ISO8601_DT)
    dhms = timestamp_to_dhms(datetime.datetime.now().timestamp() - timestamp)
    after_dt_str = datetime.datetime.fromtimestamp(timestamp).strftime(FS_ISO8601_DT)
    sql_endpoints_created_after = Template(SQL_ENDPOINTS_CREATED).substitute(timestamp=after_dt_str)
    cursor = isedc.query(sql_endpoints_created_after)
    rows = cursor.fetchall()
    endpoints = []
    if len(rows) > 0:
        headers = [f"{column[0]}".lower() for column in cursor.description]
        endpoints = [dict(zip(headers, row)) for row in rows]  # make a list of dicts
    log.info(f"{len(endpoints)} new endpoints since ⏲ {timestamp_dt_str} ▽ {timestamp} ⧖ {dhms} ago")
    return endpoints


def add_ieee_oui_attributes(endpoints: [dict] = None) -> [dict]:
    """
    Add endpoint attributes `oui` and `ieee_oui_org` from the IEEE OUI table for reference.
    - endpoints ([dict]) : list of endpoint dictionaries
    - returns ([dict]) : list of endpoint dictionaries with IEEE OUI attributes added
    """
    NO_MAC_DELIMITERS = str.maketrans("", "", string.punctuation)  # remove delimiters from MAC address
    for endpoint in endpoints:
        endpoint["oui"] = endpoint["mac"].strip().translate(NO_MAC_DELIMITERS)[0:6].upper()
        endpoint["ieee_oui_org"] = ieee_oui_dict.get(endpoint["oui"], "Unknown")
    return endpoints


if __name__ == "__main__":
    """
    Run from script
    """
    signal.signal(signal.SIGINT, lambda signum, frame: sys.exit(0))  # Handle CTRL+C interrupts gracefully

    argp = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    argp.add_argument("-a", "--after", type=str, default=None, help="query after datetime, YYYY-MM-DD HH:MM:SS")
    argp.add_argument("-f", "--format", choices=["github", "markdown", "table"], default="table", help="output format or styling")
    argp.add_argument("-i", "--insecure", action="store_true", default=False, help="do not verify certs (allow self-signed)")
    argp.add_argument("-l", "--level", default="WARNING", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], help="log threshold")
    argp.add_argument("-p", "--period", type=int, default=PERIOD_DEFAULT, help="query period, in seconds")
    argp.add_argument("-s", "--show", action="store_true", help="show new endpoints")
    args = argp.parse_args()

    log.setLevel(args.level)
    if args.period < PERIOD_MIN:
        sys.exit(f"period < {PERIOD_MIN}s")

    mac_utils = mac.MAC(load_ieee=True)
    ieee_oui_dict = mac_utils.get_ieee_oui_dict()
    with ISEDC(
        hostname=os.environ.get("ISE_PMNT"),
        password=os.environ.get("ISE_DC_PASSWORD"),
        insecure=True,
        level=args.level,
    ) as isedc:

        # find new endpoints
        now_ts = datetime.datetime.now(tz=None).timestamp()
        period_start = datetime.datetime.strptime(args.after, FS_ISO8601_DT).timestamp() if args.after else now_ts
        while True:
            endpoints = get_endpoints_after(timestamp=period_start)
            period_start = datetime.datetime.now(tz=None).timestamp()  # tz=None uses the local system's timezone
            if ieee_oui_dict:
                endpoints = add_ieee_oui_attributes(endpoints)
            send_endpoints_notification(endpoints, NTFY_TOPIC)
            if args.show:
                show(endpoints, args.format)
            time.sleep(args.period)  # sleep until next poll
