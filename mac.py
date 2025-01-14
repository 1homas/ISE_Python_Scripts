#!/usr/bin/env python3
"""
A utility class for MAC addresses.
Generates MAC addresses when run from the command line.

Usage:
  mac.py 
  mac.py --help
  mac.py --oui 00000C
  mac.py --format 0  # normalized without separators
  mac.py --format 2b --sep .  # two-byte format, '.' separator
  mac.py --local -n 100 -s :
  mac.py -n10 --local

MAC formats (default separator is '-'):
- `0` : 1234567890AB
- `ieee` : 12-34-56-78-90-AB
- `1b`: 12-34-56-78-90-AB
- `2b`: 1234-5678-90AB
"""

__license__ = "MIT - https://mit-license.org/"

import argparse
import csv
import datetime
import enum
import os
import random
import re
import requests
import string
import sys
import time


class MAC:

    # Class attributes
    BITMASK_OR_LOCALLY_ADMINISTERED = 0b000000100000000000000000
    BITMASK_AND_UNICAST = 0b111111101111111111111111
    SEPARATORS = ":-."
    TD_30D = datetime.timedelta(days=30)
    TR_NO_PUNCTUATION = str.maketrans("", "", string.punctuation)

    # lazy load singletons
    ieee_oui_dict = None
    log = None

    def __init__(cls, load_ieee: bool = False, expiration: datetime.timedelta = TD_30D) -> None:
        if not isinstance(load_ieee, bool):
            raise TypeError(f"load_ieee is not bool")
        # Lazy load IEEE data
        cls.ieee_oui_dict = cls.get_ieee_oui_dict(expiration) if load_ieee else None

    class FORMATS(enum.Enum):
        NONE = "0"  # no separators: XXXXXXXXXXXX
        ONEBYTE = "1b"  # onebyte + ':' separator (or any separator): XX:XX:XX:XX:XX:XX
        TWOBYTE = "2b"  # twobyte + ':' separator (or any separator): XXXX:XXXX:XXXX
        IEEE = "ieee"  # onebyte + '-' separator: XX-XX-XX-XX-XX-XX

        @classmethod
        def get(cls, value):
            for attr in cls:
                if attr.value == value.strip().lower():
                    return attr
            raise ValueError(f"{value} is not valid for {cls.__name__}")

    @classmethod
    def get_ieee_oui_dict(cls, expiration: datetime.timedelta = TD_30D) -> dict:
        """
        Returns the `ieee_oui_dict` singleton instance.

        - returns (dict): dictionary of { "oui" : "organization", ... }
        """
        if cls.ieee_oui_dict == None:
            # lazy init logging
            if cls.log == None:
                import logging

                logging.basicConfig(
                    stream=sys.stderr,
                    format="%(asctime)s.%(msecs)03d | %(levelname)s | %(module)s | %(funcName)s | %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                )
                level = "INFO"
                cls.log = logging.getLogger()
                cls.log.setLevel(level)  # logging threshold
                cls.log.debug(f"MAC logging initialized @ level={level})")

            # lazy download & init IEEE OUI dict
            cls.ieee_oui_dict = cls._load_ieee_oui_dict(expiration)

        return cls.ieee_oui_dict

    @classmethod
    def _load_ieee_oui_dict(cls, expiration: datetime.timedelta = TD_30D):
        """
        Return a dict of IEEE {OUI:Organization}, downloading the data from the IEEE, if necessary.

        - expiration (datetime.timedelta) : time duration until the IEEE OUI file is expired and needs to be downloaded
        """
        IEEE_OUI_URL = "https://standards-oui.ieee.org/oui/oui.txt"
        IEEE_OUI_TXT_FILENAME = "ieee_ouis.txt"
        IEEE_OUI_CSV_FILENAME = "ieee_ouis.csv"
        # use a fake User-Agent or the IEEE site will reject your requests as a bot
        USER_AGENT_HEADER = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0"}

        def download(url: str = None, headers: dict = None):
            cls.log.critical(f"load_ieee_oui_dict().download({IEEE_OUI_URL})")
            try:
                response = requests.get(IEEE_OUI_URL, headers=USER_AGENT_HEADER)
                with open(IEEE_OUI_TXT_FILENAME, "w") as file:
                    file.write(response.text)
                    cls.log.critical(f"load_ieee_oui_dict().download(): Saved {IEEE_OUI_TXT_FILENAME}")
            except requests.exceptions.ConnectionError:
                cls.log.error(f"load_ieee_oui_dict().download(): Connection problem.")

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
                cls.info(f"IEEE file expired: {now_dt} (now) > {ouis_text_expired_dt} text expiration")

                response = requests.head(IEEE_OUI_URL, headers=USER_AGENT_HEADER)
                cls.log.info(f"IEEE OUI HEAD Request: {response.headers}")

                # Convert Last-Modified to timestamp for easy comparison: ['Last-Modified']: Thu, 26 Dec 2024 17:01:23 GMT
                url_last_modified_ts = datetime.datetime.strptime(response.headers["Last-Modified"], "%a, %d %b %Y %H:%M:%S %Z").timestamp()
                url_last_modified_dt = datetime.datetime.fromtimestamp(url_last_modified_ts)
                cls.log.info(
                    f"{IEEE_OUI_URL} modified {response.headers['Last-Modified']} ({url_last_modified_dt.strftime(FS_ISO8601_DT)})"
                )

                if url_last_modified_ts > ouis_text_modified_ts:  # URL is newer?
                    cls.log.info(f"IEEE file updated: {url_last_modified_dt} > {ouis_text_expired_dt} text expiration")
                    download(IEEE_OUI_URL, USER_AGENT_HEADER)
            else:
                cls.log.info(f"IEEE file current: {ouis_text_modified_dt} < {ouis_text_expired_dt} expiration")

        # Invalid OUI file?
        if os.path.getsize(IEEE_OUI_TXT_FILENAME) < 1000000:
            cls.log.debug(f"Invalid size: {IEEE_OUI_TXT_FILENAME}: Verify HTTP User-Agent ")
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
                cls.log.debug(f"IEEE OUI base16 lines parsed")

            # Save filtered oui_table to CSV file
            with open(IEEE_OUI_CSV_FILENAME, "w", encoding="utf-8", newline="") as file:
                writer = csv.writer(file)
                writer.writerows(oui_table)
                cls.log.info(f"Saved {IEEE_OUI_CSV_FILENAME}")

        # Read CSV ["OUI", "Organization"] into MAC lookup dictionary
        with open(IEEE_OUI_CSV_FILENAME, "r", newline="") as csvfile:
            csv_reader = csv.reader(csvfile)
            oui_dict = {}
            for row in csv_reader:
                if row:  # Ensure the row is not empty
                    oui_dict[row[0]] = row[1]  # { "OUI" : "Organization" }
            return oui_dict

    @classmethod
    def is_hex(cls, s: str = None):
        """
        Returns True if all characters in string s are hexadecimal digits, False otherwise.

        - c (str): a single character string.
        """
        return all([c in string.hexdigits for c in list(s)])

    @classmethod
    def normalize(cls, mac: str = None):
        """
        Returns a MAC address without any separators and all upppercase.

        - mac (str): the MAC address in any format.
        """
        if not isinstance(mac, str):
            raise ValueError(f"mac is not a string: {mac}")
        return mac.strip().translate(cls.TR_NO_PUNCTUATION).upper()

    @classmethod
    def is_mac(cls, mac: str = None):
        """
        Returns True if mac is a normalized, 12-digit MAC address, False otherwise.

        - mac (str): a MAC address.
        """
        try:
            assert isinstance(mac, str), f"mac ({mac}) is str"
            assert mac[0] in string.hexdigits, f"first mac digit is hex"
            assert mac[-1] in string.hexdigits, f"last mac digit is hex"
            assert len(mac) in [
                12,  # 1234567890ab FORMATS.NONE (normalized)
                14,  # 1234.5678.90ab FORMATS.TWOBYTE
                17,  # 12:34:56:78:90:ab FORMATS.ONEBYTE
            ], f"mac length is normal"
            assert len(mac.strip().translate(cls.TR_NO_PUNCTUATION).upper()) == 12, f"normalized mac ({mac}) OK)"
            assert all([digit in (string.hexdigits + cls.SEPARATORS) for digit in list(mac)]), f"mac ({mac}) chars OK"
            return True
        except Exception as e:
            return False

    @classmethod
    def is_local(cls, mac: str = None):
        """
        Returns True if mac is a locally administered (random) MAC address, False otherwise.
        A MAC address is considered random when "locally administered" (the 2nd hex digit is one of [26AE]).
        This is typically done for endpoint privacy.

        RADIUS:Calling-Station-ID MATCHES ^.[26AaEe].*
                   12:34:56:78:90:AB
            0001 ──┘└── 0010
                          │├── 0: Unicast (evens)
                          │└── 1: Multicast (odds)
                          ├── 0: globally unique [0,1,4,5,8,9,C,D]
                          └── 1: locally administered [2,6,A,E]

        - mac (str): a MAC address.
        """
        if not isinstance(mac, str):
            raise ValueError(f"mac is not a string: {mac}")
        return re.match("^.[26AE].*", mac) != None  # match string start; Return None if no match

    @classmethod
    def local(cls, oui: str = None):
        """
        Returns a random, unformatted, locally administered MAC address.
        A convenience method for `MAC.random(local=True)`.

        - oui (str): an optional OUI.
        """
        oui = "{:06X}".format(random.randint(1, 16777216)) if oui == None else oui  # 16777216 == 2^24

        # RADIUS:Calling-Station-ID MATCHES ^.[26AaEe].*
        #            12:34:56:78:90:AB
        #     0001 ──┘└── 0010 = 2
        #                 0110 = 6
        #                 1010 = A
        #                 1110 = E
        #                   │├── 0: Unicast (evens)
        #                   │└── 1: Multicast (odds)
        #                   ├── 0: globally unique [0,1,4,5,8,9,C,D]
        #                   └── 1: locally administered [2,6,A,E]
        #
        # Set locally administered bit in OUI:
        #                       OUI (hex):    0    0    0    0    0    0
        #                       OUI (bin): 0000 0000 0000 0000 0000 0000
        # Locally Administered Mask (bin): 0000 0010 0000 0000 0000 0000
        #              Unicast Mask (bin): 1111 1110 1111 1111 1111 1111
        #
        # 💡 Bitwise precedence requires & then |
        oui = "{:06X}".format(int(oui, 16) & cls.BITMASK_AND_UNICAST | cls.BITMASK_OR_LOCALLY_ADMINISTERED)
        mac = oui + "{:06X}".format(random.randint(1, 16777216))  # 'X' == capitalized hex
        return mac  # cls.to_format(mac)

    @classmethod
    def random(cls, oui: str = None):
        """
        Returns a randomly generated, unformatted MAC address with the specified OUI and a randomized OUI if none is given.
        It is not necessarily a random, locally administered MAC address unless `local=True`.

        - oui (str): an optional OUI.
        """
        oui = "{:06X}".format(random.randint(1, 16777216)) if oui == None else oui  # 16777216 == 2^24
        mac = oui + "{:06X}".format(random.randint(1, 16777216))  # 'X' == capitalized hex
        return mac  # cls.to_format(mac)

    # 💡 "format()" is a built-in Python function
    @classmethod
    def to_format(cls, mac: str = None, format: str = FORMATS.IEEE, sep: str = "-"):
        """
        Returns a formatted MAC address with the specified separator between groups of digits.
        The default format is the IEEE802 format: <pre>xx-xx-xx-xx-xx-xx</pre>.

        - mac (str): a MAC address.
        - format (str): one of the supported formats (default: 'IEEE'):
            `NONE` : 1234567890AB
            `IEEE` : 12-34-56-78-90-AB
            `ONEBYTE`: 12:34:56:78:90:AB
            `TWOBYTE`: 1234:5678:90AB
        """
        if not isinstance(mac, str):
            raise ValueError(f"mac is not a string: {mac}")
        if not isinstance(format, cls.FORMATS):
            raise ValueError(f"format {format} is not a valid format: {cls.FORMATS}")

        if format == cls.FORMATS.IEEE:
            return cls.fmt(mac, sep, 2)
        if format == cls.FORMATS.ONEBYTE:
            return cls.fmt(mac, sep, 2)
        if format == cls.FORMATS.TWOBYTE:
            return cls.fmt(mac, sep, 4)
        if format == cls.FORMATS.NONE:
            return cls.normalize(mac)

    # 💡 Function name is abbreviated as fmt because `format()` is a builtin Python function
    @classmethod
    def fmt(cls, mac: str = None, sep: str = "-", digits: int = 2):
        """
        Returns a formatted MAC address with the specified separator between groups of digits.
        The default format is the IEEE802 format: <pre>xx-xx-xx-xx-xx-xx</pre>.

        - mac (str): a MAC address.
        - sep (int): a separator character. Default: '-'.
        - digits (int): the number of digits in a group (0,2,4). O means no separator. Default: 2.
        """
        if not isinstance(mac, str):
            raise ValueError(f"mac is not a string: {mac}")
        if not isinstance(sep, str):
            raise ValueError(f"separator is not a string: {sep}")
        if not isinstance(digits, int):
            raise ValueError(f"digits is not an int: {digits}")
        if digits not in [0, 2, 4]:
            raise ValueError(f"digits is not [2,4]: {digits}")
        mac = cls.normalize(mac)

        if digits == 0:
            return mac

        groups = []  # onebyte or twobyte groups
        for n in range(0, 12, digits):  # range(start, stop[, step])
            groups.append(mac[n : n + digits])
        return sep.join(groups)

    @classmethod
    def oui(cls, mac: str = None):
        """
        Returns the organizationally unique identifier (OUI) (first 6 digits of the MAC address), regardless of delimiters.

        - mac (str): a MAC address.
        """
        if not isinstance(mac, str):
            raise ValueError(f"mac is not a string: {mac}")
        return cls.normalize(mac)[0:6]

    @classmethod
    def nic(cls, mac: str = None):
        """
        Returns the network interface card (NIC) portion (last 6 digits) of the MAC address, regardless of delimiters.

        - mac (str): a MAC address.
        """
        if not isinstance(mac, str):
            raise ValueError(f"mac is not a string: {mac}")
        return cls.normalize(mac)[6:]

    @classmethod
    def org(cls, mac: str = None) -> str:
        """
        Returns the IEEE organization name registered to the specified OUI or None is there is not one.

        - mac (str): a MAC address or OUI.
        """
        print(f"org({mac})")
        if not isinstance(mac, str):
            raise ValueError(f"mac is not a string: {mac}")
        if cls.ieee_oui_dict is None:
            cls.ieee_oui_dict = cls._load_ieee_oui_dict(cls.TD_30D)  # lazy load the dict

        return cls.ieee_oui_dict.get(cls.normalize(mac)[0:6], None) if len(mac) > 6 else cls.ieee_oui_dict.get(mac, None)

    @classmethod
    def ouis(cls, org: str = None) -> [str]:
        """
        Returns all known OUIs for a given organization name.

        - org (str): an organization name from the IEEE OUI list
        - returns ([str]): a list of OUIs belonging to that organization in `org`
        """
        print(f"ouis({org})")

        oui_dict = cls.get_ieee_oui_dict()
        # print(f"🐛 ouis({org})")
        ouis = []
        for k, v in oui_dict.items():
            if v == org:
                # print(f"{v} has {k}")
                ouis.append(k)
        print(f"org {org} has {len(ouis)} OUIs")
        return ouis


if __name__ == "__main__":
    argp = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    argp.add_argument(
        "-f",
        "--format",
        choices=["0", "ieee", "1b", "2b"],
        default="ieee",
        type=str,
        # type=MAC.FORMATS,
        help="address format",
        required=False,
    )
    argp.add_argument("-l", "--local", action="store_true", default=False, help="locally administered (random)")
    argp.add_argument("-n", "--number", default=1, type=int, help="the number of MACs to create. Default is 1", required=False)
    argp.add_argument("-o", "--oui", type=str, help="the base OUI", required=False)
    argp.add_argument("-s", "--separator", default="-", type=str, help="the separator character", required=False)
    args = argp.parse_args()

    number = int(args.number) if args.number else 1  # number of MACs
    for n in range(0, number):
        mac = MAC.local(args.oui) if args.local else MAC.random(args.oui)
        print(MAC.to_format(mac, MAC.FORMATS.get(args.format), args.separator), file=sys.stdout)
