#!/usr/bin/env python3
"""
Query ISE using SQL via Data Connect on the ISE Monitoring and Troubleshooting (MNT) node.
The default output format is a streamed CSV (comma-separated value) to minimize client memory usage with large datasets.
⚠ Many output formats are supported however they require buffering all query results in memory before printing to calculate column widths (grid,table) or map attriute names (json,yaml).

Example commands:
  iseql.py -n ise.demo.local -u dataconnect -p "ISEisC00L" "SELECT * FROM node_list" -f table
  iseql.py -it -n ise.demo.local -u dataconnect -p "ISEisC00L" "SELECT COUNT(*) AS total FROM radius_authentications"
  iseql.py "SELECT * FROM node_list" -f yaml  # ⚠ requires environment variables
  iseql.py "SELECT * FROM radius_authentications ORDER BY timestamp ASC FETCH FIRST 10 ROWS ONLY"
  iseql.py -it "SELECT * FROM radius_authentications ORDER BY timestamp ASC FETCH FIRST 10 ROWS ONLY"

Here are a few example queries (wrap them in quotes!):
  SELECT view_name FROM user_views ORDER BY view_name ASC
  SELECT * FROM node_list
  SELECT * FROM network_devices
  SELECT COUNT(*) FROM radius_authentications
  SELECT timestamp, calling_station_id, username FROM radius_accounting WHERE timestamp > sysdate - INTERVAL '1' MINUTE 
  SELECT authentication_method, COUNT(*) FROM radius_authentications GROUP BY authentication_method

It is faster to edit and save your favorite or complex SQL queries into files then include them:
  iseql.py "$(cat data/SQL/radius_auths_by_policy.sql)" -f table

Many SQL queries have been created for you in https://github.com/1homas/ISE_Python_Scripts/tree/main/data/SQL

Supported environment variables:
  export ISE_PMNT='1.2.3.4'             # hostname or IP address of ISE Primary MNT
  export ISE_DC_USERNAME='dataconnect'  # Data Connect username
  export ISE_DC_PASSWORD='DataC0nnect'  # Data Connect password
  export ISE_DC_PORT=2484               # Data Connect port
  export ISE_VERIFY=False               # Optional: Disable TLS certificate verification (allow self-signed certs)

You may add these export lines to a text file and load with `source`:
  source ~/.secrets/ise-dataconnect.sh

ⓘ Thin vs Thick oracledb Clients
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

import argparse
import oracledb
import os
import ssl
import sys
import time
import tabulate
import csv
import json
import yaml

ISE_DC_PORT = 2484  # Data Connect port
ISE_DC_SID = "cpm10"  # Data Connect service name identifier
ISE_DC_USERNAME = "dataconnect"  # Data Connect username
FORMATS = ["csv", "grid", "json", "line", "pretty", "yaml", "raw", "table", "text"]


def show(table: list = None, headers: list = None, format: str = "text", filepath: str = "-") -> None:
    """
    Print the table in the specified format to the file. Default: `sys.stdout` ('-').

    - table (list) : a list of list items to show
    - headers (list) : the column names for the table
    - format (str): one the following formats:
      - `csv`   : Show the items in a Comma-Separated Value (CSV) format
      - `grid`  : Show the items in a table grid with borders
      - `json`  : Show the items as a single JSON string
      - `line`  : Show the items each on their own line in JSON format
      - `pretty`: Show the items in an indented JSON format
      - `table` : Show the items in a text-based table
      - `text`  : Show the items in a text-based table (no header line separator)
      - `yaml`  : Show the items in a YAML format
    - filepath (str) : Default: `sys.stdout`
    """
    if table == None or len(table) <= 0:
        return

    # 💡 Do not close sys.stdout or it may not be re-opened with multiple show() calls
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
        print(json.dumps({"table": [dict(zip(headers, row)) for row in rows]}, default=(lambda o: str(o))), file=fh)
    elif format == "line":  # 1 JSON object per line
        print("{", file=fh)
        print(f'"table" : [', file=fh)
        print(",\n".join([json.dumps(r, default=(lambda o: str(o))) for r in [dict(zip(headers, row)) for row in rows]]), file=fh)
        print("]\n}", file=fh)
    elif format == "pretty":  # pretty-print with 2-space indents
        print(json.dumps({"table": [dict(zip(headers, row)) for row in rows]}, default=(lambda o: str(o)), indent=2), file=fh)
    elif format == "yaml":  # YAML
        print(yaml.dump({"table": [dict(zip(headers, row)) for row in rows]}, indent=2, default_flow_style=False), file=fh)
    elif format == "text":  # pretty-print
        print(f"{tabulate.tabulate(table, headers=headers, tablefmt='plain')}", file=fh)
    else:  # just in case something gets through the CLI parser
        print(f"✖ Unknown format: {format}", file=sys.stderr)


argp = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
argp.add_argument("query", help="an Oracle PL/SQL Query, wrapped in double-quotes", default=None)
argp.add_argument("-n", "--name", action="store", default=None, help="ISE MNT hostname or IP address", type=str)
argp.add_argument("-u", "--username", action="store", default=ISE_DC_USERNAME, help="username", type=str)
argp.add_argument("-p", "--password", action="store", default=None, help="password", type=str)
argp.add_argument("--port", action="store", default=None, help="Data Connect Port number", type=int)
argp.add_argument("-f", "--format", choices=FORMATS, default="csv")
argp.add_argument("-i", "--insecure", action="store_true", default=False, help="do not verify certificates (allow self-signed certs)")
argp.add_argument("-t", "--timer", action="store_true", default=False, help="show total script time")
argp.add_argument("-v", "--verbosity", action="count", default=0, help="verbosity; multiple allowed")
args = argp.parse_args()

if args.query is None or args.query == "":
    sys.exit(f"Required query is empty")
if args.timer:
    start_time = time.time()

env = {k: v for (k, v) in os.environ.items() if k.startswith("ISE_")}  # Load environment variables

# Merge settings from 1) CLI args, 2) environment variables and 3) static defaults
host = args.name or env.get("ISE_PMNT")
port = args.port or env.get("ISE_DC_PORT") or ISE_DC_PORT
username = args.username or env.get("ISE_DC_USERNAME") or ISE_DC_USERNAME
password = args.password or env.get("ISE_DC_PASSWORD")

if host is None:
    sys.exit("Missing host: Set ISE_PMNT environment variable or use --name option")
if port is None:
    sys.exit("Missing port: Set ISE_DC_PORT environment variable or use --port option")
if username is None:
    sys.exit("Missing username: Set ISE_DC_USERNAME environment variable or use --username option")
if password is None:
    sys.exit("Missing password: Set ISE_DC_PASSWORD environment variable or use --password option")

if args.verbosity >= 3:
    print(f"{username}:{password}@{host}:{port} with {'✖' if args.insecure else '✔'}TLS")

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
if args.insecure or env.get("ISE_VERIFY", "True")[0:1].lower() in ["f", "n"]:
    if args.verbosity:
        print("ⓘ TLS security disabled", file=sys.stderr)
    ssl_context.check_hostname = False  # required before setting verify_mode == ssl.CERT_NONE
    ssl_context.verify_mode = ssl.CERT_NONE  # any cert is accepted; validation errors are ignored

params = oracledb.ConnectParams(
    protocol="tcps",  # tcp "secure" with TLS
    host=host,  # name or IP address of database host machine
    port=port,  # Oracle Default: 1521
    service_name=ISE_DC_SID,
    user=username,  # the name of the user to connect to
    password=password,
    retry_count=3,  # connection attempts retries before being terminated. Default: 0
    retry_delay=3,  # seconds to wait before a new connection attempt. Default: 0
    ssl_context=ssl_context,  # an SSLContext object which is used for connecting to the database using TLS
    # ssl_server_dn_match=False, # boolean indicating if the server certificate distinguished name (DN) should be matched. Default: True
    # ssl_server_cert_dn=False # the distinguished name (DN), which should be matched with the server
    # wallet_location=DIR_EWALLET, # the directory containing the PEM-encoded wallet file, ewallet.pem
)
if args.verbosity:
    print(f"ⓘ OracleDB Connect String: {params.get_connect_string()}", file=sys.stderr)

try:
    with oracledb.connect(params=params) as connection:
        with connection.cursor() as cursor:
            cursor.execute(args.query)

            # Use CSV by default to stream results without large memory buffering
            if args.format == "csv":
                # Get header names from cursor.description, a list of sets about each column:
                #   [ (name, type_code, display_size, internal_size, precision, scale, null_ok), ... ]
                headers = [f"{i[0]}".lower() for i in cursor.description]
                writer = csv.writer(sys.stdout, quoting=0, skipinitialspace=True)
                writer.writerow(headers)
                while True:
                    rows = cursor.fetchmany()  # use default Cursor.arraysize
                    if not rows:
                        break
                    writer.writerows(rows)
            else:
                # All other formats require buffering all results in memory for column width sizing (grid|table) or map attribute names (JSON|YAML)
                headers = [f"{i[0]}".lower() for i in cursor.description]
                rows = cursor.fetchall()  # returns a list of tuples
                show(table=rows, headers=headers, format=args.format)

except oracledb.Error as e:
    print(f"Oracle Error: {e}", file=sys.stderr)
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)

if args.timer:
    print(f"⏱ {'{0:.3f}'.format(time.time() - start_time)} seconds", file=sys.stderr)
