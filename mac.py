#!/usr/bin/env python3
"""
A utility class for MAC addresses.

MAC formats:
`none` : 1234567890AB
`ieee` : 12-34-56-78-90-AB
`onebyte`: 12:34:56:78:90:AB
`twobyte`: 1234:5678:90AB
"""
__author__ = "Thomas Howard"
__email__ = "thomas@cisco.com"
__license__ = "MIT - https://mit-license.org/"

import argparse
import re
import time
import random
import string
import sys


class MAC:

    # Class variables
    FORMATS = [
        "none",  # no separators: XXXXXXXXXXXX
        "ieee",  # onebyte + '-' separator: XX-XX-XX-XX-XX-XX
        "onebyte",  # onebyte + ':' separator (or any separator): XX:XX:XX:XX:XX:XX
        "twobyte",  # twobyte + ':' separator (or any separator): XXXX:XXXX:XXXX
    ]

    @classmethod
    def is_hex(self, s: str = None):
        """
        Returns True if all characters in string s are hexadecimal digits, False otherwise.

        - c (str): a single character string.
        """
        try:
            [int(c, 16) for c in s.split()]
            return True
        except ValueError:
            return False

    @classmethod
    def normalize(self, mac: str = None):
        """
        Returns a MAC address without any separators and all upppercase.

        - mac (str): the MAC address in any format.
        """
        if not isinstance(mac, str):
            raise ValueError(f"mac is not a string: {mac}")
        return mac.strip().translate(str.maketrans("", "", string.punctuation)).upper()

    @classmethod
    def is_mac(self, mac: str = None):
        """
        Returns True if mac is a normalized, 12-digit MAC address, False otherwise.

        - mac (str): a MAC address.
        """
        if not isinstance(mac, str):
            raise ValueError(f"mac is not a string: {mac}")
        mac = self.normalize(mac)
        return len(mac) == 12 and self.is_hex(mac)

    @classmethod
    def is_random(self, mac: str = None):
        """
        Returns True if mac is a random MAC address, False otherwise.
        A MAC address is random when "locally administered" (the 2nd hex digit is one of [26AE]).
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
    def randomized(self, oui: str = None):
        """
        Returns a randomized MAC address prefixed with the specified OUI or a randomized OUI if none is given.

        - oui (str): an optional OUI.
        """
        oui = "{:06X}".format(random.randint(1, 16777216)) if oui == None else oui  # 16777216 == 2^24
        mac = oui + "{:06X}".format(random.randint(1, 16777216))  # 'X' == capitalized hex
        return self.to_format(mac)

    # 💡 "format()" is a built-in Python function
    @classmethod
    def to_format(self, mac: str = None, format: str = "ieee", sep: str = "-"):
        """
        Returns a formatted MAC address with the specified separator between groups of digits.
        The default format is the IEEE802 format: <pre>xx-xx-xx-xx-xx-xx</pre>.

        - mac (str): a MAC address.
        - format (str): one of the supported formats (default: 'ieee'):
            `none` : 1234567890AB
            `ieee` : 12-34-56-78-90-AB
            `onebyte`: 12:34:56:78:90:AB
            `twobyte`: 1234:5678:90AB
        """
        if not isinstance(mac, str):
            raise ValueError(f"mac is not a string: {mac}")
        if not isinstance(format, str):
            raise ValueError(f"format is not a string: {mac}")
        format = format.strip().lower()
        if format not in self.FORMATS:
            raise ValueError(f"format is not one of [{','.join(self.FORMATS)}]: {format}")

        if format == "ieee":
            return self.fmt(mac, sep, 2)
        if format == "onebyte":
            return self.fmt(mac, sep, 2)
        if format == "twobyte":
            return self.fmt(mac, sep, 4)
        if format == "none":
            return self.normalize(mac)

    # 💡 Function name is abbreviated as fmt because `format()` is a builtin Python function
    @classmethod
    def fmt(self, mac: str = None, sep: str = "-", digits: int = 2):
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
        if digits not in [2, 4]:
            raise ValueError(f"digits is not [2,4]: {digits}")
        mac = self.normalize(mac)
        groups = []  # onebyte or twobyte groups
        for n in range(0, 12, digits):  # range(start, stop[, step])
            groups.append(mac[n : n + digits])
        return sep.join(groups)

    @classmethod
    def get_oui(self, mac: str = None):
        """
        Returns the organizationally unique identifier (OUI) (first 6 digits of the MAC address), regardless of delimiters.

        - mac (str): a MAC address.
        """
        if not isinstance(mac, str):
            raise ValueError(f"mac is not a string: {mac}")
        return self.normalize(mac)[0:6]

    @classmethod
    def get_nic(self, mac: str = None):
        """
        Returns the network interface card (NIC) portion (last 6 digits) of the MAC address, regardless of delimiters.

        - mac (str): a MAC address.
        """
        if not isinstance(mac, str):
            raise ValueError(f"mac is not a string: {mac}")
        return self.normalize(mac)[6:]


if __name__ == "__main__":
    argp = argparse.ArgumentParser()
    argp.description = __doc__
    argp.add_argument("-o", "--oui", type=str, help="the base OUI", required=False)
    argp.add_argument("-n", "--number", default=1, type=int, help="the number of MACs to create. Default is 1", required=False)
    argp.add_argument(
        "-f",
        "--format",
        choices=["ieee", "none", "onebyte", "twobyte"],
        default="ieee",
        type=str,
        help="address format",
        required=False,
    )
    argp.add_argument("-s", "--sep", default="-", type=str, help="the separator character", required=False)
    args = argp.parse_args()
    # print(f"args:{args}")

    number = int(args.number) if args.number else 1  # number of MACs
    for n in range(0, number):
        # Use the specified OUI otherwise generate a random one
        oui = args.oui.strip().upper() if args.oui else "{:06X}".format(random.randint(1, 16777216))
        mac = oui + "{:06X}".format(random.randrange(1, 16777216))
        print(MAC.to_format(mac, args.format, args.sep), file=sys.stdout)
        # print(f"{'✔' if MAC.is_random(mac) else '✖'} {MAC.to_format(mac, args.format, args.sep)}")
