#!/usr/bin/env python3
"""
Query ISE Data Connect using SQL on the ISE Monitoring and Troubleshooting (MNT) node.

ⓘ Thin vs Thick oracledb Clients
  This script uses the oracledb package and runs as a "thin" client without the need for additional ODBC drivers.
  The main limitation with the ISE database has been timestamp fields containing TimeZone information.
  You may workaround this problem by simply excluding those columns in your queries.
  Refer to the ISE Data Connect documentation (https://cs.co/ise-dataconnect) for tables with TimeZone fields.
  If you want to run in "thick" mode, you will need to locally install the 
  Oracle Instant Client (https://www.oracle.com/database/technologies/instant-client/downloads.html) 
  which is not currently available for the macOS ARM architecture.

Example queries (wrap them in quotes!):
  SELECT view_name FROM user_views ORDER BY view_name ASC
  SELECT * FROM node_list
  SELECT * FROM network_devices
  SELECT authentication_method, COUNT(*) FROM radius_authentications GROUP BY authentication_method
  SELECT status,username,is_admin,password_never_expires FROM network_access_users
  SELECT * FROM radius_authentications ORDER BY timestamp asc
  SELECT timestamp,username,calling_station_id,policy_set_name,authorization_rule,authorization_profiles,ise_node,endpoint_profile,framed_ip_address,security_group FROM radius_authentications
  SELECT timestamp,username,calling_station_id,nas_identifier,ise_node FROM radius_accounting WHERE stopped = 0 ORDER BY timestamp ASC

These environment variables are required using the `export` command:
  export ISE_PMNT='1.2.3.4'             # hostname or IP address of ISE Primary MNT
  export ISE_DC_PASSWORD='#DataC0nnect' # Data Connect password
  export ISE_CERT_VERIFY=False          # Optional: Disable TLS certificate verification (allow self-signed certs)

You may add these export lines to a text file and load with `source`:
  source ise-env.sh

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

ISE_DC_PORT=2484               # Data Connect port
ISE_DC_USERNAME='dataconnect'  # Data Connect username
ISE_DC_SID='cpm10'             # Data Connect service name identifier
FORMATS = ['csv', 'grid', 'json', 'table', 'text']


def show(table:list=None, headers:list=None, format:str='text', filepath:str='-') -> None:
    """
    Print the table in the specified format to the file. Default: `sys.stdout` ('-').

    - table (list) : a list of list items to show
    - headers (list) : the column names for the table
    - format (str): one the following formats:
      - `csv`   : Show the items in a Comma-Separated Value (CSV) format
      - `grid`  : Show the items in a table grid with borders
      - `json`  : Show the items as a single JSON string
      - `table` : Show the items in a text-based table
      - `text`  : Show the items in a text-based table (no header line separator)
    - filepath (str) : Default: `sys.stdout`
    """
    if table == None or len(table) <= 0: return

    # 💡 Do not close sys.stdout or it may not be re-opened with multiple show() calls
    fh = sys.stdout if filepath == '-' else open(filepath, 'w') # write to sys.stdout/terminal by default

    if format == 'csv':  # CSV
        import csv
        writer = csv.writer(fh)
        writer.writerow(headers)
        writer.writerows(table)
    elif format == 'grid': # grid
        print(f"{tabulate.tabulate(table, headers=headers, tablefmt='simple_grid')}", file=fh)
    elif format == 'table': # table
        print(f"{tabulate.tabulate(table, headers=headers, tablefmt='table')}", file=fh)
    elif format == 'json':  # JSON, one long string
        import json
        # must convert table values to str in case of datetime objects
        d = {}
        table_dicts = []
        for row in table:
            for header, value in zip(headers, row):
                d[header] = str(value) 
            table_dicts.append(d)
        print(json.dumps({ 'table': table_dicts }), file=fh)
    elif format == 'text':  # pretty-print
        print(f"{tabulate.tabulate(table, headers=headers, tablefmt='plain')}", file=fh)
    else:  # just in case something gets through the CLI parser
        print(f"✖ Unknown format: {format}", file=sys.stderr)


argp = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
argp.add_argument('query', help='an Oracle PL/SQL Query, wrapped in double-quotes', default=None)
argp.add_argument('-f', '--format', choices=FORMATS, default='table')
argp.add_argument('-i', '--insecure', action='store_true', default=False, help='do not verify certificates for TLS (allow self-signed certs)')
argp.add_argument('-t', '--timer', action='store_true', default=False, help='show total script time' )
argp.add_argument('-v', '--verbosity', action='count', default=0, help='verbosity; multiple allowed')
args = argp.parse_args()

if args.query is None or args.query == "": print(f"query is empty", file=sys.stderr)
if args.timer: start_time = time.time()

env = {k:v for (k, v) in os.environ.items() if k.startswith('ISE_')}  # Load environment variables

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
if args.insecure or env.get('ISE_CERT_VERIFY', 'True')[0:1].lower() in ['f','n']:
    if args.verbosity: print("ⓘ TLS security disabled", file=sys.stderr)
    ssl_context.check_hostname = False # required before setting verify_mode == ssl.CERT_NONE
    ssl_context.verify_mode = ssl.CERT_NONE # any cert is accepted; validation errors are ignored

params = oracledb.ConnectParams(
            protocol='tcps',  # tcp "secure" with TLS
            host=env['ISE_PMNT'], # name or IP address of database host machine
            port=ISE_DC_PORT, # DB listener, Default: 1521
            service_name=ISE_DC_SID, 
            user=ISE_DC_USERNAME, # the name of the user to connect to
            password=env['ISE_DC_PASSWORD'],
            retry_count=3, # connection attempts retries before being terminated. Default: 0
            retry_delay=3, # seconds to wait before a new connection attempt. Default: 0
            ssl_context=ssl_context, # an SSLContext object which is used for connecting to the database using TLS
            # ssl_server_dn_match=False, # boolean indicating if the server certificate distinguished name (DN) should be matched. Default: True
            # ssl_server_cert_dn=False # the distinguished name (DN), which should be matched with the server
            # wallet_location=DIR_EWALLET, # the directory containing the PEM-encoded wallet file, ewallet.pem
          )
if args.verbosity : print(f"ⓘ OracleDB Connect String: {params.get_connect_string()}", file=sys.stderr)

try:
    with oracledb.connect(params=params) as connection:
        with connection.cursor() as cursor:
            cursor.execute(args.query)
            headers = [i[0].lower() for i in cursor.description] # description: (name, type_code, display_size, internal_size, precision, scale, null_ok)
            rows = cursor.fetchall() # returns a list of tuples
            show(table=rows, headers=headers, format=args.format)
except oracledb.Error as e:
    print(f"Oracle Error: {e}", file=sys.stderr)
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)

if args.timer: print(f"⏱ {'{0:.3f}'.format(time.time() - start_time)} seconds", file=sys.stderr)
