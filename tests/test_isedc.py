#!/usr/bin/env python3
"""
Test the ISEDC module.

Usage:
    python -m pytest -v --log-level=DEBUG --log-file=tests/test_output.txt tests/test_isedc.py
    python -m pytest -v --log-level=DEBUG --log-file=tests/test_output.txt tests/test_isedc.py::test_isedc_formats
    pytest -m pytest tests/test_isedc.py  # run a single tests file and add the current directory to sys.path
    pytest tests/test_isedc.py            # run a single tests file
    pytest -v                             # summarize progress 
    pytest                                # automatically finds and runs `tests` directory contents

Anatomy of a test is broken down into four steps:
- Arrange: prepare everything for our test
- Act: the singular, state-changing action that kicks off the behavior we want to test
- Assert: inspect the resulting state and check if it matches expectations 
- Cleanup: remove artifacts so additional tests are not affected or influenced

"""

__license__ = "MIT - https://mit-license.org/"

from isedc import ISEDC

import argparse
import datetime
import logging
import io
import os
import re
import requests
import string
import sys
import tabulate
import time
import sys
import os
import pytest

# Valid test instance
HOSTNAME = os.environ.get("ISE_PMNT")
PORT = 2484
USERNAME = "dataconnect"
PASSWORD = os.environ.get("ISE_DC_PASSWORD")
INSECURE = True
LEVEL = logging.DEBUG


def test_isedc_constants():
    assert ISEDC.DB_CONNECT_RETRIES >= 3, "DB_CONNECT_RETRIES is valid"
    assert ISEDC.DB_CONNECT_TIMEOUT >= 3, "DB_CONNECT_TIMEOUT is valid"
    assert ISEDC.DATACONNECT_PORT == 2484, "DATACONNECT_PORT is correct"
    assert ISEDC.DATACONNECT_SID == "cpm10", "DATACONNECT_SID is correct"
    assert ISEDC.DATACONNECT_USERNAME == "dataconnect", "DATACONNECT_USERNAME is correct"
    assert ISEDC.DATACONNECT_PASSWORD_DAYS_DEFAULT == 90, "DATACONNECT_PASSWORD_DAYS_DEFAULT is correct"
    assert ISEDC.DATACONNECT_PASSWORD_DAYS_MAX == 3650, "DATACONNECT_PASSWORD_DAYS_MAX is correct"


def test_isedc_init():
    """Assert the constructor options."""

    # hostname (str): the ISE Primary MNT node hostname or IP address. Default: None
    # port (int): the Data Connect port number. Default: 2484
    # username (str): the ISE Data Connect username. Default: 'dataconnect'
    # password (str): the ISE Data Connect password. Default: None
    # insecure (bool): do not perform server certificate validation
    # level (Union[int, str]): logging threshold level

    # isedc = ISEDC(hostname=hostname, password=password, insecure=insecure, level=level)

    with pytest.raises(AssertionError) as excinfo:
        isedc = ISEDC()
    assert excinfo.type is AssertionError, "no args"

    #
    # hostname
    #
    with pytest.raises(AssertionError) as excinfo:
        isedc = ISEDC(hostname=None)
    assert excinfo.type is AssertionError, "hostname is None"
    assert "None" in str(excinfo.value)

    with pytest.raises(AssertionError) as excinfo:
        ISEDC(hostname="")
    assert excinfo.type is AssertionError, "hostname is empty"
    assert "empty" in str(excinfo.value)

    with pytest.raises(AssertionError) as excinfo:
        isedc = ISEDC(hostname=0)
    assert excinfo.type is AssertionError, "hostname is not str"

    with pytest.raises(AssertionError) as excinfo:  # match=r".*"
        isedc = ISEDC(hostname=0, password=PASSWORD, insecure=INSECURE, level=LEVEL)
        version = isedc.version()
    assert excinfo.type is AssertionError, "hostname is not a string"

    with pytest.raises(requests.exceptions.ConnectionError) as excinfo:
        isedc = ISEDC(hostname="asdf", password=PASSWORD, insecure=INSECURE, level=LEVEL)
        version = isedc.version()
    assert excinfo.type is requests.exceptions.ConnectionError, "Verify requests.exceptions.ConnectionError for asdf"

    with pytest.raises(requests.exceptions.ConnectionError) as excinfo:
        isedc = ISEDC(hostname="0.0.0.0", password=PASSWORD, insecure=INSECURE, level=LEVEL)
        version = isedc.version()
    assert excinfo.type is requests.exceptions.ConnectionError, "Verify requests.exceptions.ConnectionError for 0.0.0.0"

    with pytest.raises(requests.exceptions.ConnectionError) as excinfo:
        ISEDC(hostname="10.1.2.300", password=PASSWORD, insecure=INSECURE, level=LEVEL)
        version = isedc.version()
    # print(f"excinfo: {excinfo}")
    # print(f"excinfo.type: {excinfo.type}")
    # print(f"excinfo.value: {str(excinfo.value)}")
    assert excinfo.type is requests.exceptions.ConnectionError, "Verify requests.exceptions.ConnectionError"

    #
    # port
    #
    with pytest.raises(AssertionError) as excinfo:
        isedc = ISEDC(hostname=HOSTNAME, port=None)
    assert excinfo.type is AssertionError, "port is None"

    with pytest.raises(AssertionError) as excinfo:
        isedc = ISEDC(hostname=HOSTNAME, port=0)
    assert excinfo.type is AssertionError, "port is < 1024"

    with pytest.raises(AssertionError) as excinfo:
        isedc = ISEDC(hostname=HOSTNAME, port=1025)
    assert excinfo.type is AssertionError, "port is > 1024"
    assert "port" not in str(excinfo.value), "port is in range"

    with pytest.raises(AssertionError) as excinfo:
        isedc = ISEDC(hostname=HOSTNAME, port=PORT)
    assert excinfo.type is AssertionError, "port is PORT"
    assert "port" not in str(excinfo.value), "port is in range"

    with pytest.raises(AssertionError) as excinfo:
        isedc = ISEDC(hostname=HOSTNAME, port=65534)
    assert excinfo.type is AssertionError, "port is <= 65534"
    assert "port" not in str(excinfo.value), "port is in range"

    with pytest.raises(AssertionError) as excinfo:
        isedc = ISEDC(hostname=HOSTNAME, port=65535)
    assert excinfo.type is AssertionError, "port is > 65534"
    print(str(excinfo.value))
    # assert "port" in str(excinfo.value), "port is > 65534"

    #
    # username
    #
    # 💡ToDo: Test invalid characters
    #

    with pytest.raises(AssertionError) as excinfo:
        isedc = ISEDC(hostname=HOSTNAME, username=None, password=PASSWORD, insecure=INSECURE, level=LEVEL)
    assert excinfo.type is AssertionError, "username is None"

    with pytest.raises(AssertionError) as excinfo:
        isedc = ISEDC(hostname=HOSTNAME, username="", password=PASSWORD, insecure=INSECURE, level=LEVEL)
    assert excinfo.type is AssertionError, "username is empty"

    isedc = ISEDC(hostname=HOSTNAME, username=USERNAME, password=PASSWORD, insecure=INSECURE, level=LEVEL)
    assert isedc is not None, "username is valid"

    #
    # password
    #
    # 💡ToDo: Test invalid characters
    #

    isedc = ISEDC(hostname=HOSTNAME, password=PASSWORD, insecure=INSECURE, level=LEVEL)
    assert isedc is not None, "password is valid"

    #
    # insecure
    #

    with pytest.raises(AssertionError) as excinfo:
        isedc = ISEDC(hostname=HOSTNAME, password=PASSWORD, insecure=None, level=LEVEL)
    assert excinfo.type is AssertionError, "insecure is None"

    with pytest.raises(AssertionError) as excinfo:
        isedc = ISEDC(hostname=HOSTNAME, password=PASSWORD, insecure="", level=LEVEL)
    assert excinfo.type is AssertionError, "insecure is empty"

    with pytest.raises(AssertionError) as excinfo:
        isedc = ISEDC(hostname=HOSTNAME, password=PASSWORD, insecure="asdf", level=LEVEL)
    assert excinfo.type is AssertionError, "insecure is string"

    isedc = ISEDC(hostname=HOSTNAME, password=PASSWORD, insecure=INSECURE, level=LEVEL)
    assert isedc is not None, "insecure is valid"

    #
    # level
    #
    # TypeError
    # ValueError
    with pytest.raises(AssertionError) as excinfo:
        isedc = ISEDC(hostname=HOSTNAME, password=PASSWORD, insecure=INSECURE, level=None)
    assert excinfo.type is AssertionError, "level is None"

    with pytest.raises(AssertionError) as excinfo:
        isedc = ISEDC(hostname=HOSTNAME, password=PASSWORD, insecure=INSECURE, level="")
    assert excinfo.type is AssertionError, "level is empty"

    #
    # Numeric levels
    #
    for level in [logging.NOTSET, logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]:
        isedc = ISEDC(hostname=HOSTNAME, password=PASSWORD, insecure=INSECURE, level=level)
        assert isedc is not None

    #
    # String levels
    #
    for level in ["NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        isedc = ISEDC(hostname=HOSTNAME, password=PASSWORD, insecure=INSECURE, level=level)
        assert isedc is not None


def test_isedc_connection():

    isedc = ISEDC(hostname=HOSTNAME, password=PASSWORD, insecure=INSECURE, level=LEVEL)
    assert isedc is not None, "insecure is valid"
    print(isedc.connect())


def test_isedc_enabled():

    isedc = ISEDC(hostname=HOSTNAME, password=PASSWORD, insecure=INSECURE, level=LEVEL)
    assert isedc is not None, "isedc is valid"
    assert isinstance(isedc.enabled(), bool), "return bool"


def test_isedc_enable():

    isedc = ISEDC(hostname=HOSTNAME, password=PASSWORD, insecure=INSECURE, level=LEVEL)
    assert isedc is not None, "isedc is valid"

    # enabled = True
    enabled = isedc.enable(enable=True)
    assert isinstance(enabled, bool), "enable returns bool"
    assert enabled == True, "enable returns true"

    # 💡ToDo: enabled = False


def test_isedc_version():

    isedc = ISEDC(hostname=HOSTNAME, password=PASSWORD, insecure=INSECURE, level=LEVEL)
    assert isedc is not None, "isedc is valid"
    version = isedc.version()
    print(f"version: {version}")

    assert version is not None
    assert isinstance(version, str), "version is a str"
    assert version.startswith("19"), "version startswith 19"
    assert len(version.split(".")) >= 4, "version tuples"
    assert int(version.split(".")[0]) == 19, "oracle version 19"

    # print(f"version: {version} {version.split(".")[0]}")
    # print(f"excinfo: {excinfo}")
    # print(f"excinfo.type: {excinfo.type}")
    # print(f"excinfo.value: {str(excinfo.value)}")


def test_isedc_formats():

    FORMATS = ["csv", "grid", "json", "line", "markdown", "pretty", "yaml", "table", "text"]
    isedc = ISEDC(hostname=HOSTNAME, password=PASSWORD, insecure=INSECURE, level=LEVEL)
    assert isedc is not None, "isedc is valid"
    assert isinstance(ISEDC.FORMATS, list), f"FORMATS is a list"
    assert len(ISEDC.FORMATS) == len(FORMATS), f"ISEDC.FORMATS == FORMATS"
    for format in FORMATS:
        assert format in ISEDC.FORMATS, f"ISEDC supports {format} format"

    # 💡ToDo: Verify output format
    # for format in isedc.FORMATS:
    #     cursor = isedc.query("SELECT * FROM node_list")
    #     with io.StringIO() as buffer:
    #         isedc.show(cursor, format=format, filepath=buffer)
    #         assert buffer.readable()
    #         print(buffer.getvalue())
    #         assert len(buffer.getvalue()) > 0, f"{format} output > 0"


def test_isedc_tables_columns():

    with ISEDC(
        hostname=os.environ.get("ISE_PMNT"),
        password=os.environ.get("ISE_DC_PASSWORD"),
        insecure=INSECURE,
        level=LEVEL,
    ) as isedc:

        isedc_tables = isedc.tables()  # list of table names
        print(f"isedc_tables: {isedc_tables}", file=sys.stderr)
        assert isinstance(isedc_tables, list)
        assert len(isedc_tables) >= 70

        for table in isedc_tables:
            isedc_columns = isedc.columns(table)
            # print(f"{table} columns: {isedc.columns('network_devices')}", file=sys.stderr)
            assert isinstance(isedc_columns, list)
            assert len(isedc_columns) > 0


# def test_isedc_option_format():
#     pass


# def test_isedc_option_insecure():
#     pass


# def test_isedc_option_level():
#     pass


# def test_isedc_show():

#     with ISEDC(
#         hostname=os.environ.get("ISE_PMNT"),
#         password=os.environ.get("ISE_DC_PASSWORD"),
#         insecure=INSECURE,
#         level=LEVEL,
#     ) as isedc:
#         pass
