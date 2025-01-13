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
import enum
import re
import time
import random
import string
import sys


class MAC:

    # Class attributes
    BITMASK_OR_LOCALLY_ADMINISTERED = 0b000000100000000000000000
    BITMASK_AND_UNICAST = 0b111111101111111111111111
    SEPARATORS = ":-."
    TR_NO_PUNCTUATION = str.maketrans("", "", string.punctuation)

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


if __name__ == "__main__":
    argp = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    argp.description = __doc__
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
