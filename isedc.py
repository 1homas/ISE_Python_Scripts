#!/usr/bin/env python3
"""
ISE Data Connect object wrapper in Python to query the ISE Monitoring and Troubleshooting (MNT) node's database using SQL.
The default output format is a streamed CSV (comma-separated value) to minimize client memory usage with large datasets.
⚠ All other formats must store *all* results in memory for formatting column widths (grid|markdown|table) or attribute name mapping (JSON|YAML).
⚠ SQL statements must not contain a trailing semicolon (“;”) or they will fail with `oracledb`
⚡ Many SQL queries have been created for you in https://github.com/1homas/ISE_Python_Scripts/tree/main/data/SQL

Usage with environment variables:
  export ISE_PMNT='1.2.3.4'             # hostname or IP address of ISE Primary MNT
  export ISE_DC_PASSWORD='D@t@C0nnect'  # Data Connect password
  export ISE_VERIFY=False               # Optional: Disable TLS certificate verification (allow self-signed certs)

  isedc.py data/SQL/node_list.sql
  isedc.py "$(cat data/SQL/radius_auths_by_policy.sql)" -f table
  isedc.py "SELECT * FROM node_list" -f yaml
  isedc.py -it "SELECT * FROM radius_accounting ORDER BY timestamp ASC FETCH FIRST 10 ROWS ONLY"

Without environment variables:
  isedc.py -it -n ise.example.org -u dataconnect -p "D@t@C0nnect" "SELECT * FROM node_list" -f table

⚠ Thin vs Thick oracledb Clients
  This script uses the oracledb package and runs as a "thin" client without the need for additional ODBC drivers.
  The main limitation with the ISE database has been timestamp fields containing TimeZone information.
  You may workaround this problem by simply excluding those columns in your queries.
  Refer to the ISE Data Connect documentation (https://cs.co/ise-dataconnect) for tables with TimeZone fields.
  If you want to run in "thick" mode, you will need to locally install the 
  Oracle Instant Client (https://www.oracle.com/database/technologies/instant-client/downloads.html) 
  which is not currently available for the macOS ARM architecture.

"""
__author__ = "Thomas Howard"
__email__ = "thomas@cisco.com"
__license__ = "MIT - https://mit-license.org/"

import argparse  # https://docs.python.org/3/library/argparse.html
import csv
import json
import logging
import oracledb  # https://python-oracledb.readthedocs.io/en/latest/
import os
import requests
import signal
import ssl
import sys
import tabulate  # https://pypi.org/project/tabulate/
import traceback
import yaml
from typing import Union

# -----------------------------------------------------------------------------
# Thick Client Option
# import platform
# d = None  # On Linux, no directory should be passed
# if platform.system() == "Darwin":  # macOS
#     d = os.environ.get("HOME") + ("/Downloads/instantclient_23_3")
# elif platform.system() == "Windows":  # Windows
#     d = r"C:\oracle\instantclient_23_5"
# oracledb.init_oracle_client(lib_dir=d)
# -----------------------------------------------------------------------------


class ISEDC:

    # Class variables
    DB_CONNECT_RETRIES = 3
    DB_CONNECT_TIMEOUT = 5  # seconds
    DATACONNECT_PORT = 2484  # Data Connect port
    DATACONNECT_SID = "cpm10"  # Data Connect service name identifier
    DATACONNECT_USERNAME = "dataconnect"  # Data Connect username
    DATACONNECT_PASSWORD_DAYS_DEFAULT = 90
    DATACONNECT_PASSWORD_DAYS_MAX = 3650
    FORMATS = ["csv", "grid", "json", "line", "markdown", "pretty", "table", "text", "yaml"]

    def __init__(
        self,
        hostname: str = None,
        port: int = DATACONNECT_PORT,
        username: str = DATACONNECT_USERNAME,
        password: str = None,
        insecure: bool = False,  # Do not perform server certificate validation
        level: Union[int, str] = "WARN",  # logging threshold level
    ):
        """
        Creates an ISEDC instance with the spcecific configuration options.

        hostname (str): the ISE Primary MNT node hostname or IP address. Default: None
        port (int): the Data Connect port number. Default: 2484
        username (str): the ISE Data Connect username. Default: 'dataconnect'
        password (str): the ISE Data Connect password. Default: None
        insecure (bool): do not perform server certificate validation
        level (Union[int, str]): logging threshold level
        """

        # Create a default logger to sys.stderr
        assert level is not None, "level is None"
        assert level != "", "level is empty"
        assert isinstance(level, int) or isinstance(level, str), "level is int or str"
        logging.basicConfig(
            stream=sys.stderr,
            format="%(asctime)s.%(msecs)03d | %(levelname)s | %(module)s | %(funcName)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        self.log = logging.getLogger()
        self.log.setLevel(level)  # logging threshold
        self.log.debug(f"ISEDC(hostname={hostname},port={port},username={username},insecure={insecure},level={level})")

        assert hostname is not None, "hostname is None"
        assert isinstance(hostname, str), "hostname is not a string"
        assert hostname != "", "hostname is empty"
        self.hostname = hostname

        assert port is not None, "port is not None"
        assert isinstance(port, int), "port is not an int"
        assert port >= 1025
        assert port <= 65534
        self.port = port

        assert username is not None, "username is None"
        assert isinstance(username, str), "username is not a string"
        assert username != "", "username is empty"
        self.username = username

        assert password is not None, "password is None"
        assert isinstance(password, str), "password is not a string"
        assert password != "", "password is empty"
        assert len(password) >= 8, "password is too short"
        # 💡ToDo: match Data Connect Password validation
        self.password = password

        assert insecure is not None, "insecure is None"
        assert isinstance(insecure, bool)
        self.insecure = insecure
        self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        if self.insecure:
            self.ssl_context.check_hostname = False  # required before setting verify_mode == ssl.CERT_NONE
            self.ssl_context.verify_mode = ssl.CERT_NONE  # any cert is accepted; validation errors are ignored
            self.log.debug(f"{'⚠' if self.insecure else '✔'} TLS security {'dis' if self.insecure else 'en'}abled")

        self.params = oracledb.ConnectParams(
            protocol="tcps",  # tcp "secure" with TLS
            host=self.hostname,  # name or IP address of database host machine
            port=self.port,  # Oracle Default: 1521
            service_name=self.DATACONNECT_SID,
            user=self.username,  # the name of the user to connect to
            password=self.password,
            retry_count=3,  # connection attempts retries before being terminated. Default: 0
            retry_delay=3,  # seconds to wait before a new connection attempt. Default: 0
            ssl_context=self.ssl_context,  # an SSLContext object which is used for connecting to the database using TLS
            # ssl_server_dn_match=False, # boolean indicating if the server certificate distinguished name (DN) should be matched. Default: True
            # ssl_server_cert_dn=False # the distinguished name (DN), which should be matched with the server
            # wallet_location=DIR_EWALLET, # the directory containing the PEM-encoded wallet file, ewallet.pem
        )
        self.log.debug(f"OracleDB Connection String: {self.params.get_connect_string()}")
        self.connection = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Close the database connection."""
        self.close()

    # def __del__(self) -> None:
    #     """ Close the connection. """
    #     self.connection.close()

    def connect(self):
        """
        Connect to the database and return the connection.
        Connection timeout after ~12 * 60s = 720s
        https://python-oracledb.readthedocs.io/en/latest/user_guide/troubleshooting.html#dpy-4011
        """
        if self.connection != None:
            return self.connection
        if not self.enabled():
            self.enable(True)

        for attempt in range(self.DB_CONNECT_RETRIES):
            try:
                self.log.info(f"Attempting to connect ({attempt + 1}/{self.DB_CONNECT_RETRIES})...")
                self.connection = oracledb.connect(params=self.params, tcp_connect_timeout=self.DB_CONNECT_TIMEOUT)
                if self.connection:
                    self.log.info(f"Connected successfully")
                    return self.connection
            except oracledb.DatabaseError:
                pass
        raise Exception("Failed to connect to the database after {self.DB_CONNECT_RETRIES} attempts")

    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
            self.log.info(f"Connection closed")
            logging.shutdown()

    def version(self):
        """
        Returns the ISE Data Connect Oracle database version.
        """
        return self.connect().version

    def get_connect_string(self):
        """
        Returns a list of all ISE Data Connect tables.
        """
        return self.params.get_connect_string()

    def query(self, q: str = None):
        """
        Returns the results of the query, `q`.
        - q (str): a PL/SQL query string or `*.sql` filepath
        """
        self.log.debug(f"q={q}")

        assert isinstance(q, str)
        assert q is not None
        assert q != ""

        q = self.read_sql_file(q) if q.strip().lower().endswith(".sql") else q  # load SQL query from file?
        self.log.debug(f"SQL query:\n-----\n{q}\n-----")

        try:
            # ⚠ Do not close the cursor or it cannot be used by the calling function!
            # execute() returns a cursor
            return self.connect().cursor().execute(q)
        except oracledb.DatabaseError as e:
            if "DPY-4011" in str(e):
                self.log.error(f"DPY-4011: Database connecting closed")
                self.close()
                return self.connect().cursor().execute(q)
            elif "ORA-02399" in str(e):
                # 60 minute max connect time
                self.log.error(f"ORA-02399: exceeded maximum connect time, you are being logged off")
                self.close()
                return self.connect().cursor().execute(q)
            elif "ORA-03113" in str(e):
                # 12 minutes?
                self.log.error(f"ORA-03113 Session timeout")
                self.close()
                return self.connect().cursor().execute(q)
            else:
                self.log.error(f"Unknown error: {str(e)}")
                self.close()
                return self.connect().cursor().execute(q)
                # raise

    def _handle_exception(self, e: Exception = None) -> None:
        """Handle an Exception."""
        tb_text = "\n".join(traceback.format_exc().splitlines()[1:])  # remove 'Traceback (most recent call last):'
        self.log.error(f"{e.__class__} | {tb_text}")

    def read_sql_file(self, filepath: str = None) -> str:
        """
        Read and return the file contents at the filepath.
        filepath: an absolute or relative path from this script.
        returns: the file contents as a string.
        """
        self.log.debug(f"filepath={filepath}")

        assert filepath.strip().lower().endswith(".sql")
        assert os.path.exists(filepath)
        assert os.path.isfile(filepath)

        with open(filepath, mode="r", encoding="utf-8") as fh:
            return fh.read()

    def csv_stream(self, cursor: oracledb.Cursor = None, filepath="-"):
        """
        Return the query results in a stream of comma-separated values (CSV) format.
        - cursor (Cursor): cursor
        - file (File): file
        """
        self.log.debug(f"cursor={cursor}, filepath={filepath}")

        assert isinstance(cursor, oracledb.Cursor)
        assert isinstance(filepath, str)
        assert filepath is not None
        assert filepath != ""
        fh = sys.stdout if filepath == "-" else open(filepath, "w")  # write to sys.stdout/terminal by default

        # Get header names from cursor.description, a list of sets about each column:
        #   [ (name, type_code, display_size, internal_size, precision, scale, null_ok), ... ]
        headers = [f"{column[0]}".lower() for column in cursor.description]
        writer = csv.writer(fh, quoting=0, skipinitialspace=True)
        writer.writerow(headers)
        while True:
            rows = cursor.fetchmany()  # use default Cursor.arraysize
            if not rows:
                break
            writer.writerows(rows)

    def cursor_headers(self, cursor: oracledb.Cursor = None):
        """
        Returns a list of the header names from the cursor.
        """
        # Get header names from cursor.description, a list of sets about each column:
        #   [ (name, type_code, display_size, internal_size, precision, scale, null_ok), ... ]
        return [f"{column[0]}".lower() for column in cursor.description]

    def enabled(self) -> bool:
        """
        Get the ISE Data Connect status.
        """
        with requests.Session() as session:
            # Initialize ISE REST API Session
            session.auth = (os.environ.get("ISE_REST_USERNAME"), os.environ.get("ISE_REST_PASSWORD"))
            session.headers.update({"Content-Type": "application/json", "Accept": "application/json"})
            session.verify = False if os.environ.get("ISE_VERIFY")[0:1].lower() in ["f", "n"] else True

            # Returns the settings of the Dataconnect feature.
            # {
            #     "response": {
            #         "isEnabled": true,
            #         "isPasswordChanged": true,
            #         "passwordExpiresInDays": 45,
            #         "passwordExpiresOn": "15 December 2021 at 18:05 PST"
            #     }
            # }
            url = f"https://{self.hostname}/api/v1/mnt/data-connect/settings"
            self.log.debug(f"Checking if {url} enabled")
            response = session.get(url)
            is_enabled = self.to_bool((response.json()["response"])["isEnabled"])
            self.log.debug(f"enabled:{is_enabled} response: {response.json()}")
            return is_enabled

    def enable(self, enable: bool = True):
        """
        Enable/Disable the ISE Data Connect service and returns the state as a boolean.
        """
        assert isinstance(enable, bool)
        self.log.debug(f"enable={enable}")

        if self.enabled() == enable:
            return enable

        with requests.Session() as session:
            # Initialize ISE REST API Session
            session.auth = (os.environ.get("ISE_REST_USERNAME"), os.environ.get("ISE_REST_PASSWORD"))
            session.headers.update({"Content-Type": "application/json", "Accept": "application/json"})
            session.verify = False if os.environ.get("ISE_VERIFY")[0:1].lower() in ["f", "n"] else True

            url = f"https://{self.hostname}/api/v1/mnt/data-connect/details"
            self.log.debug(f"ISEDC.enable() details: {session.get(url).ok}")

            # 💡 Must set password BEFORE enabling!
            #    - Password must contain one or more special characters [#$%&*+,-.:;] ⚠ No @ or !
            #    - Password can't be set to one of the earlier 5 password(s)
            url = f"https://{self.hostname}/api/v1/mnt/data-connect/settings/password"
            response = session.put(url, json={"password": os.environ.get("ISE_DC_PASSWORD")})
            self.log.debug(f"ISEDC.enable() password: {response.json()}")

            # Set Password Expiration
            url = f"https://{self.hostname}/api/v1/mnt/data-connect/settings/password/expiry"
            response = session.put(url, json={"passwordExpiresInDays": self.DATACONNECT_PASSWORD_DAYS_MAX})
            self.log.debug(f"ISEDC.enable() password-expiry:\n{response.json}")

            # Enable ISE DataConnect via API
            url = f"https://{self.hostname}/api/v1/mnt/data-connect/settings/status"
            response = session.put(url, json={"isEnabled": True})
            self.log.debug(f"ISEDC.enable() status: {response.json()}")

            # Returns the settings of the Dataconnect feature.
            # {
            #     "response": {
            #         "isEnabled": true,
            #         "isPasswordChanged": true,
            #         "passwordExpiresInDays": 45,
            #         "passwordExpiresOn": "15 December 2021 at 18:05 PST"
            #     }
            # }
            url = f"https://{self.hostname}/api/v1/mnt/data-connect/settings"
            self.log.debug(f"ISEDC.enable() settings: {session.get(url).json()['response']}")

            # Returns the Dataconnect ODBC details - but these don't change.
            # {
            #     "response": {
            #         "hostname": "isenode",
            #         "port": 2484,
            #         "servicename": "cpm10",
            #         "username": "Admin"
            #     }
            # }
            url = f"https://{self.hostname}/api/v1/mnt/data-connect/details"
            self.log.debug(f"ISEDC.enable() details: {session.get(url).json()['response']}")

    def tables(self):
        """
        Returns a list of all ISE Data Connect tables.
        """
        sql_dc_tables = """SELECT view_name FROM user_views ORDER BY view_name ASC"""

        try:
            cursor = self.query(sql_dc_tables)  # returns a cursor for iterating
            rows = cursor.fetchall()
            return [row[0].lower() for row in rows]  # convert [(tuple),(tuple),...] to list
        except oracledb.Error as e:
            self._handle_exception(e)

    def columns(self, table: str = None):
        """
        Returns a list of all ISE Data Connect tables.
        - table (str): a single character string.
        """
        sql_dc_table_columns = f"""SELECT table_name, column_name FROM all_tab_columns WHERE table_name = '{table.strip().upper()}' ORDER BY table_name ASC, column_name ASC"""
        self.log.debug(f"columns(table={table}): sql_dc_table_columns: {sql_dc_table_columns}")
        try:
            cursor = self.query(sql_dc_table_columns)
            rows = cursor.fetchall()
            return [row[1].lower() for row in rows]  # convert [(tuple),(tuple),...] to list
        except Exception as e:
            self._handle_exception(e)

    def column_widths(self, table: str = None, columns: list = []):
        """ """
        self.log.debug(f"table={table}, columns={columns}")
        # normalie columns to a list
        if not isinstance(columns, list):
            raise ValueError(f"columns is not a list")
        if len(columns) <= 0:
            columns = self.columns(table)  # get columns for the table
            self.log.debug(f"Fetched columns: {columns}")

        widths = []
        for column in columns:
            cursor = self.query(f"SELECT MAX(LENGTH({column})) AS width FROM {table}")
            widths += (column, cursor.fetchone()[0])
            return widths

    def show(self, data: Union[list, oracledb.Cursor] = None, headers: list = None, format: str = "text", filepath: str = "-") -> None:
        """
        Print the table in the specified format to the file. Default: `sys.stdout` ('-').

        - data (list) : a list of lists/tuples or an oracledb.Cursor with data to show
        - headers (list) : the column names for the table
        - format (str): one the following formats:
          - `csv`     : Show the items in a Comma-Separated Value (CSV) format
          - `grid`    : Show the items in a table grid with borders
          - `json`    : Show the items as a single, unformatted JSON string
          - `line`    : Show the items each on their own line in JSON format
          - `markdown`: Show the items in Markdown table format
          - `pretty`  : Show the items in an indented JSON format
          - `table`   : Show the items in a text-based table
          - `text`    : Show the items in a text-based table (no header line separator)
          - `yaml`    : Show the items in a YAML format
        - filepath (str) : Default: `sys.stdout`
        """
        assert data != None

        # normalize cursor results to a `data` table ([list] of iterables) and headers
        if isinstance(data, oracledb.Cursor):
            headers = [f"{column[0]}".lower() for column in data.description]
            table = data.fetchall()  # returns a list of tuples
        else:
            table = data

        if len(table) <= 0:
            self.log.info(f"No rows to show")
            return

        try:
            # 💡 Do not close sys.stdout or it may not be re-opened with multiple cursor_show() calls
            fh = sys.stdout if filepath == "-" else open(filepath, "w")  # write to sys.stdout/terminal by default

            if format == "csv":  # CSV
                writer = csv.writer(fh)
                writer.writerow(headers)
                writer.writerows(table)
            elif format == "grid":  # grid
                print(f"{tabulate.tabulate(table, headers=headers, tablefmt='simple_grid')}", file=fh)
            elif format == "table":  # table
                print(f"{tabulate.tabulate(table, headers=headers, tablefmt='table')}", file=fh)
            elif format == "json":  # JSON, one long string
                print(json.dumps({"table": [dict(zip(headers, row)) for row in table]}, default=(lambda o: str(o))), file=fh)
            elif format == "line":  # 1 JSON object per line
                print("{", file=fh)
                print(f'"table" : [', file=fh)
                print(",\n".join([json.dumps(r, default=(lambda o: str(o))) for r in [dict(zip(headers, row)) for row in table]]), file=fh)
                print("]\n}", file=fh)
            elif format == "markdown":
                print(f"{tabulate.tabulate(table, headers=headers, tablefmt='github')}", file=fh)
            elif format == "pretty":  # pretty-print with 2-space indents
                print(json.dumps({"table": [dict(zip(headers, row)) for row in table]}, default=(lambda o: str(o)), indent=2), file=fh)
            elif format == "yaml":  # YAML
                print(yaml.dump({"table": [dict(zip(headers, row)) for row in table]}, indent=2, default_flow_style=False), file=fh)
            elif format == "text":  # pretty-print
                print(f"{tabulate.tabulate(table, headers=headers, tablefmt='plain')}", file=fh)
            else:  # just in case something gets through the CLI parser
                print(f"✖ Unknown format: {format}", file=sys.stderr)
        except Exception as e:
            self._handle_exception(e)

    @classmethod
    def to_bool(self, o):
        """
        Returns a boolean value based on the object type and value.
        """
        return True if (isinstance(o, int) and o > 0) or (isinstance(o, str) and s[0:1].lower() in ["t", "y", "o"]) else False


if __name__ == "__main__":
    """
    Run from script
    """
    signal.signal(signal.SIGINT, lambda signum, frame: sys.exit(1))  # Handle CTRL+C interrupts gracefully

    # Set up the command-line argument argp
    argp = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    argp.add_argument("query", help="an Oracle PL/SQL Query in double-quotes or *.sql filepath", default=None)
    argp.add_argument("-n", "--hostname", action="store", default=None, help="ISE MNT hostname or IP address", type=str)
    argp.add_argument("-p", "--password", action="store", default=None, help="password", type=str)
    argp.add_argument("-f", "--format", choices=ISEDC.FORMATS, default="csv")
    argp.add_argument("-i", "--insecure", action="store_true", default=False, help="do not verify certificates (allow self-signed certs)")
    argp.add_argument("-l", "--level", default="WARNING", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], help="log threshold")
    argp.add_argument("-t", "--timer", action="store_true", default=False, help="show total script execution time")
    args = argp.parse_args()

    if args.query is None or args.query == "":
        sys.exit(f"Required query is empty")
    if args.timer:
        import time  # lazy load

        start_time = time.time()

    # Merge settings from 1) CLI args, 2) environment variables and 3) static defaults
    with ISEDC(
        hostname=(args.hostname or os.environ.get("ISE_PMNT")),
        password=(args.password or os.environ.get("ISE_DC_PASSWORD")),
        insecure=args.insecure or os.environ.get("ISE_VERIFY", "True")[0:1].lower() in ["f", "n"],
        level=args.level,
    ) as isedc:

        if not isedc.enabled():
            print(f"ISEDC NOT Enabled")
            enabled = isedc.enable(True)
            print(f"ISEDC {'' if enabled else 'NOT '}Enabled")

        try:

            # Use CSV by default to stream results without large memory buffering.
            if args.format == "csv":
                # Get header names from cursor.description, a list of sets about each column:
                #   [ (name, type_code, display_size, internal_size, precision, scale, null_ok), ... ]
                cursor = isedc.query(args.query)
                headers = [f"{i[0]}".lower() for i in cursor.description]
                writer = csv.writer(sys.stdout, quoting=0, skipinitialspace=True)
                writer.writerow(headers)
                while True:
                    rows = cursor.fetchmany()  # use default Cursor.arraysize
                    if not rows:
                        break
                    writer.writerows(rows)
            else:
                isedc.show(data=isedc.query(args.query), format=args.format)

        except oracledb.DatabaseError as e:
            if "DPY-3022" in str(e):
                import re

                table_matches = re.search(r".* FROM (\w+).*", args.query)
                if table_matches:  # None if no regex matches are found
                    table_name = table_matches.group(1)
                    columns = isedc.columns(table_name)
                    print(columns)
                print(f"{str(e)}\nPlease select columns without a timezone:\n{', '.join(list(map(str.lower, columns)))}", file=sys.stderr)
            elif "ORA-00942" in str(e):
                import re

                table_matches = re.search(r".* FROM (\w+).*", args.query)
                if table_matches:  # None if no regex matches are found
                    table_name = table_matches.group(1)
                    tables = [s for s in isedc.tables() if s.startswith(table_name[0:4])]
                print(f"{str(e)}\nPlease verify the table name '{table_name}'.\nDid you mean {tables}", file=sys.stderr)
            else:
                print(f"{str(e)}")

    if args.timer:
        print(f"⏱ {'{0:.3f}'.format(time.time() - start_time)} seconds", file=sys.stderr)
