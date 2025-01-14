#!/usr/bin/env python3
"""
Test the MAC module.

Usage:
    python -m pytest -v --log-level=DEBUG --log-file=tests/test_output.txt tests/test_mac.py
    python -m pytest -v --log-level=DEBUG --log-file=tests/test_output.txt tests/test_mac.py::test_ouis
    pytest -m pytest tests/test_mac.py  # run a single tests file and add the current directory to sys.path
    pytest tests/test_mac.py            # run a single tests file
    pytest -v                           # summarize progress 
    pytest                              # automatically finds and runs `tests` directory contents

Anatomy of a test is broken down into four steps:
- Arrange: prepare everything for our test
- Act: the singular, state-changing action that kicks off the behavior we want to test
- Assert: inspect the resulting state and check if it matches expectations 
- Cleanup: remove artifacts so additional tests are not affected or influenced

"""
__license__ = "MIT - https://mit-license.org/"


import datetime
import enum
import io
import os
import pytest
import random
import re
import requests
import string
import sys
import tabulate
import time
import traceback
import tracemalloc

tracemalloc.start()
from mac import MAC

print(globals)
import mac

MACS_GOOD = [
    "000000000000",  # no separators
    "123456789012",  # no separators
    "ABCDEFABCDEF",  # no separators
    "00:00:00:00:00:00",  # zeros
    "11:11:11:11:11:11",  # ones
    "ff:ff:ff:ff:ff:ff",  # all lowercase
    "FF:FF:FF:FF:FF:FF",  # all uppercase
    "01:23:45:67:89:AB",  # sequence
    "FE:DC:BA:98:76:54",  # sequence
    "1234.1234.1234",  # 3 groups, . separated
    "aaaa.bbbb.cccc",  # 3 groups, . separated
]

MACS_BAD = [
    "00000000000",  # missing digit
    "0000000000000",  # extra zero
    "00000000000O",  # capitial O, not zero
    "00:00:00:00:00000",  # extra zero
    "FFFFF:FF:FF:FF:FF",  # extra F
    "00:00:00:00:00:000",  # extra zero
    "11:11:11:11:11:11:",  # extra :
    "ff:ff:ff::f:ff:ff",  # extra :
    "aaaa.bb.bb.cccc",  # extra .
    "aa.aa.bb.bb.cccc",  # missing separator
    "aaa.abb.bbc.ccc",  # 4 groups
]

# Random MACs contain 2,6,A,E in the second digit
MACS_LOCALLY_ADMINISTERED = [
    "02:00:00:00:00:00",  # 2
    "06:00:00:00:00:00",  # 6
    "0A:00:00:00:00:00",  # A
    "0E:00:00:00:00:00",  # E
]


# -----------------------------------------------------------------------------
# MAC
# -----------------------------------------------------------------------------


def test_mac_utils_constants():
    assert MAC.TD_30D == datetime.timedelta(days=30), f"TD_30D is valid"
    assert isinstance(MAC.FORMATS.IEEE, MAC.FORMATS), f"MAC.FORMATS.IEEE is MAC.FORMATS"
    print(type(MAC.FORMATS))
    # assert isinstance(MAC.FORMATS, enum.Enum), f"MAC.FORMATS is enum.Enum"
    # assert len(MAC.FORMATS) == 4, f"FORMATS has 4 items"


def test_mac_utils_init():
    """Assert the constructor options."""

    # default
    mac_utils = MAC()  # defaults: load_ieee=False, expiration=TD_30D
    mac_utils = MAC(load_ieee=False)
    mac_utils = MAC(load_ieee=True)


# with pytest.raises(TypeError) as excinfo:
#     mac_utils = MAC(load_ieee="No")
#     print(f"excinfo: {excinfo}")
# tb_text = "\n".join(traceback.format_exc().splitlines()[1:])  # remove 'Traceback (most recent call last):'
# print(f"{excinfo.__class__} {tb_text}", file=sys.stderr)
# assert excinfo.type is TypeError, f"load_ieee is not bool"


def test_mac_utils_formats():
    assert MAC is not None, f"MAC is valid"
    assert isinstance(MAC.FORMATS, type), f"FORMATS is a class"


def test_is_hex():
    # test random hex strings
    HEX_STRINGS = [
        "0123456789abcdef",  # all lowercase
        "0123456789ABCDEF",  # all lowercase
        "a",
        "ffff",
        "aabbccddeeff",
        "".join(random.choices(string.hexdigits, k=5)),
        "".join(random.choices(string.hexdigits, k=25)),
    ]
    for s in HEX_STRINGS:
        assert MAC.is_hex(s), f"str {s} is_hex()"

    for mac in MACS_GOOD:
        assert MAC.is_hex(MAC.normalize(mac)), f"mac {mac} is_hex()"


def test_normalize():

    # for mac in MACS_LOCALLY_ADMINISTERED:
    #     assert MAC.normalize(mac) == ,"MAC.normalize({mac}) is normalized"
    pass


def test_is_mac():
    for mac in MACS_LOCALLY_ADMINISTERED + MACS_GOOD:
        assert MAC.is_mac(mac), f"mac ({mac}) is a valid MAC"
    for mac in MACS_BAD:
        assert MAC.is_mac(mac) is False, f"mac ({mac}) is an invalid MAC"


def test_is_local():
    for mac in MACS_LOCALLY_ADMINISTERED:
        assert MAC.is_local(mac), f"MAC.is_local({mac}) is locally administered"


def test_random():
    # ⚠ simply a randomly generated MAC address - not necessarily a locally administered MAC address!
    for idx in range(1, 100):
        # generate random MACs
        mac = MAC.random()
        assert isinstance(mac, str), f"{mac} is str"
        assert MAC.is_mac(mac), f"{mac} is a MAC"
        assert all([digit in string.hexdigits for digit in list(mac)]), f"mac ({mac}) is unformatted"

    # with random OUIs
    for idx in range(1, 100):
        OUI = "".join(random.choices(string.hexdigits, k=6))
        mac = MAC.random(oui=OUI)
        assert isinstance(mac, str), f"{mac} is str"
        assert MAC.is_mac(mac), f"{mac} is a MAC"
        assert all([digit in string.hexdigits for digit in list(mac)]), f"mac ({mac}) is unformatted"

    # with specific OUI
    for idx in range(1, 100):
        OUI = "FFFFFF"
        mac = MAC.random(oui=OUI)
        assert isinstance(mac, str), f"{mac} is str"
        assert MAC.is_mac(mac), f"{mac} is a MAC"
        assert all([digit in string.hexdigits for digit in list(mac)]), f"mac ({mac}) is unformatted"


def test_local():
    # default
    for idx in range(1, 100):
        mac = MAC.local()
        assert isinstance(mac, str), f"{mac} is str"
        assert MAC.is_mac(mac), f"{mac} is a MAC"
        assert MAC.is_local(mac), f"{mac} is local"
        assert all([digit in string.hexdigits for digit in list(mac)]), f"mac ({mac}) is unformatted"

    # with random OUIs
    for idx in range(1, 100):
        OUI = "".join(random.choices(string.hexdigits, k=6))
        mac = MAC.local(oui=OUI)
        assert isinstance(mac, str), f"{mac} is str"
        assert MAC.is_mac(mac), f"{mac} is a MAC"
        assert MAC.is_local(mac), f"{mac} is local"
        assert all([digit in string.hexdigits for digit in list(mac)]), f"mac ({mac}) is unformatted"

    # with specific OUI
    for idx in range(1, 100):
        OUI = "FFFFFF"
        mac = MAC.local(oui=OUI)
        assert isinstance(mac, str), f"{mac} is str"
        assert MAC.is_mac(mac), f"{mac} is a MAC"
        assert MAC.is_local(mac), f"{mac} is local"
        assert all([digit in string.hexdigits for digit in list(mac)]), f"mac ({mac}) is unformatted"


def test_to_format():

    # NONE
    random_mac = "".join(random.choices(string.hexdigits, k=12)).upper()
    mac = MAC.to_format(random_mac, MAC.FORMATS.NONE)
    assert isinstance(mac, str), f"{mac} is str"
    assert MAC.is_mac(mac), f"{mac} is a MAC"
    assert len(mac) == 12, f"{mac} has length 12"
    assert all([digit in string.hexdigits for digit in list(mac)]), f"{mac} digits are only hex"

    # check behavior with NONE and conflicting separators
    mac = MAC.to_format(random_mac, MAC.FORMATS.NONE, "-")
    assert not any([digit == "-" for digit in list(mac)]), f"MAC.to_format({mac}, NONE) ignores separator `-`"
    assert not any([digit == ":" for digit in list(mac)]), f"MAC.to_format({mac}, NONE) ignores separator `:`"
    assert not any([digit == "." for digit in list(mac)]), f"MAC.to_format({mac}, NONE) ignores separator `.`"

    mac = MAC.to_format(random_mac, MAC.FORMATS.IEEE)
    assert len(mac) == len("XX-XX-XX-XX-XX-XX"), f"MAC.to_format({mac}, IEEE) len({mac}) == {len("XX-XX-XX-XX-XX-XX")}"
    assert mac.count("-") == 5, f"MAC.to_format({mac}, IEEE) has 5 x -'s"

    # check behavior with IEEE and duplicate separator
    sep = "-"
    mac = MAC.to_format(random_mac, MAC.FORMATS.IEEE, sep)
    assert len(mac) == len("XX-XX-XX-XX-XX-XX"), f"MAC.to_format({mac}, IEEE) len({mac}) == {len("XX-XX-XX-XX-XX-XX")}"
    assert mac.count("-") == 5, f"MAC.to_format({mac}, IEEE) has 5 x -'s"

    # ignores conflicting separator `:`
    sep = ":"
    mac = MAC.to_format(random_mac, MAC.FORMATS.IEEE, sep)
    assert len(mac) == len("XX-XX-XX-XX-XX-XX"), f"MAC.to_format({mac}, IEEE) len({mac}) == {len("XX-XX-XX-XX-XX-XX")}"
    # 🐞Bug
    # assert mac.count("-") == 5, f"MAC.to_format({mac}, IEEE) has 5 x -'s"
    # assert mac.count(sep) == 0, f"MAC.to_format({mac}, IEEE) ignores separator {sep}"

    # ignores conflicting separator `.`
    sep = "."
    mac = MAC.to_format(random_mac, MAC.FORMATS.IEEE, sep)
    # 🐞Bug
    # assert mac.count("-") == 5, f"MAC.to_format({mac}, IEEE) has 5 x -'s"
    # assert mac.count(sep) == 0, f"MAC.to_format({mac}, IEEE) ignores separator{sep}"
    assert len(mac) == len("XX-XX-XX-XX-XX-XX"), f"MAC.to_format({mac}, IEEE) len({mac}) == {len("XX-XX-XX-XX-XX-XX")}"


def test_fmt():
    # Returns a formatted MAC address with the specified separator between groups of digits.
    # def fmt(self, mac: str = None, sep: str = "-", digits: int = 2):

    # default
    sep = "-"
    digits = 2
    for idx in range(1, 100):
        mac = MAC.fmt(MAC.random())
        assert isinstance(mac, str), f"mac ({mac}) is str"
        assert MAC.is_mac(mac), f"mac ({mac}) is a MAC"
        assert len(mac) == (12 + 12 / digits - 1), f"len({mac}) == {12+12/digits-1}"
        assert all([digit in (string.hexdigits + sep) for digit in list(mac)]), f"mac ({mac}) is default (IEEE)"
        assert mac.count(sep) == 5, f"default mac ({mac}) separators are {sep}'s (IEEE)"
        assert len(mac.split(sep)) == 6, f"default mac ({mac}) has 6 groups"
        assert all([len(group) == 2 for group in mac.split(sep)]), f"default mac ({mac}) has 2 digits per group"

    # separators, digits=2 by default
    for sep in MAC.SEPARATORS:
        for idx in range(1, 100):
            mac = MAC.fmt(MAC.random(), sep=sep)
            assert isinstance(mac, str), f"mac ({mac}) is str"
            assert MAC.is_mac(mac), f"mac ({mac}) is a MAC"
            assert len(mac) == 17, f"len({mac}) == 17"  # XX-XX-XX-XX-XX-XX
            assert all([digit in (string.hexdigits + sep) for digit in list(mac)]), f"mac ({mac}) digits OK"
            assert mac.count(sep) == 5, f"default mac ({mac}) separators are {sep}'s"
            assert len(mac.split(sep)) == 6, f"default mac ({mac}) has 6 groups"
            assert all([len(group) == 2 for group in mac.split(sep)]), f"default mac ({mac}) has 2 digits per group"

    # digits
    sep = "-"  # default separator
    for digits in [2, 4]:
        for idx in range(1, 100):
            mac = MAC.fmt(MAC.random(), digits=digits)
            assert isinstance(mac, str), f"mac ({mac}) is str"
            assert MAC.is_mac(mac), f"mac ({mac}) is a MAC"
            assert len(mac) == (12 + 12 / digits - 1), f"len({mac}) == {12+12/digits-1}"
            assert all([digit in (string.hexdigits + sep) for digit in list(mac)]), f"mac ({mac}) digits OK"
            assert mac.count(sep) == (12 / digits - 1), f"default mac ({mac}) separators are {sep}'s"
            assert len(mac.split(sep)) == (12 / digits), f"default mac ({mac}) has 6 groups"
            assert all([len(group) == digits for group in mac.split(sep)]), f"default mac ({mac}) has 2 digits per group"

    sep = ":"
    digits = 0  # no separators
    for sep in MAC.SEPARATORS:
        for idx in range(1, 100):
            mac = MAC.fmt(MAC.random(), sep=sep, digits=0)
            assert isinstance(mac, str), f"mac ({mac}) is str"
            assert MAC.is_mac(mac), f"mac ({mac}) is a MAC"
            assert len(mac) == 12, f"len({mac}) == 12"
            assert all([digit in (string.hexdigits + sep) for digit in list(mac)]), f"mac ({mac}) digits OK"
            assert len(mac.split(sep)) == 1, f"only 1 group in mac ({mac}) with no separators"
            assert all([len(group) == 12 for group in mac.split(sep)]), f"default mac ({mac}) has 12 digits per group"


def test_oui():
    # random OUI
    for idx in range(1, 100):
        OUI = "{:06X}".format(random.randint(1, 16777216))  # 16777216 == 2^24
        mac = MAC.random(oui=OUI)
        assert isinstance(mac, str), f"{mac} is str"
        assert MAC.is_mac(mac), f"{mac} is a MAC"
        assert MAC.oui(mac) == OUI, f"MAC.oui({mac}) == {OUI}"

    # specific OUI
    for idx in range(1, 100):
        OUI = "FFFFFF"
        mac = MAC.random(oui=OUI)
        assert isinstance(mac, str), f"{mac} is str"
        assert MAC.is_mac(mac), f"{mac} is a MAC"
        assert MAC.oui(mac) == OUI, f"MAC.oui({mac}) == {OUI}"


def test_nic():
    # random OUI
    for idx in range(1, 100):
        OUI = "{:06X}".format(random.randint(1, 16777216))  # 16777216 == 2^24
        mac = MAC.random(oui=OUI)
        assert isinstance(mac, str), f"{mac} is str"
        assert MAC.is_mac(mac), f"{mac} is a MAC"
        assert MAC.nic(mac) == mac[6:], f"MAC.nic({mac}) == {mac[6:]}"

    # specific OUI
    for idx in range(1, 100):
        OUI = "FFFFFF"
        mac = MAC.random(oui=OUI)
        assert isinstance(mac, str), f"{mac} is str"
        assert MAC.is_mac(mac), f"{mac} is a MAC"
        assert MAC.oui(mac) == OUI, f"MAC.oui({mac}) == {OUI}"
        assert MAC.nic(mac) == mac[6:], f"MAC.nic({mac}) == {mac[6:]}"


def test_org() -> str:
    mac_utils = MAC(load_ieee=True)
    for idx in range(1, 100):
        mac = MAC.random()
        org = mac_utils.org(mac)
        print(f"org: {"unknown" if org == None else org}")
        assert org == None or isinstance(org, str), f"org is None|str"


def test_ouis():
    mac_utils = MAC(load_ieee=True)

    # Test "Cisco Systems, Inc"
    mac = "00000c123456"
    org = mac_utils.org(mac)
    print(f"org {org} from {mac} is None|str")
    ouis = mac_utils.ouis(org)
    print(f"org {org} has {len(ouis)} OUIs")

    for idx in range(1, 100):
        mac = MAC.random()
        org = mac_utils.org(mac)
        assert org == None or isinstance(org, str), f"org {org} from {mac} is None|str"
        print(f"org {org} from {mac} is None|str")
        if org is None:
            continue
        ouis = mac_utils.ouis(org)
        print(f"org {org} has {len(ouis)} OUIs")
