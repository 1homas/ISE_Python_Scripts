#!/usr/bin/env python3
"""

Query ISE Data Connect using SQL on the ISE Monitoring and Troubleshooting (MNT) node.

Usage:
  iseql.py "{query}"

Example queries (wrap them in quotes!):
  SELECT view_name FROM user_views ORDER BY view_name ASC
  SELECT * FROM node_list
  SELECT * FROM network_devices
  SELECT * FROM security_groups
  SELECT status,username,is_admin,password_never_expires FROM network_access_users
  SELECT * FROM radius_authentications ORDER BY timestamp asc
  SELECT timestamp,username,calling_station_id,policy_set_name,authorization_rule,authorization_profiles,ise_node,endpoint_profile,framed_ip_address,security_group FROM radius_authentications
  SELECT timestamp,username,calling_station_id,nas_identifier,ise_node FROM radius_accounting WHERE stopped = 0 ORDER BY timestamp ASC

These environment variables are required using the `export` command:
  export ISE_PMNT='1.2.3.4'             # hostname or IP address of ISE Primary MNT
  export ISE_CERT_VERIFY=True           # Verify the ISE certificate
  export ISE_DC_PASSWORD='#DataC0nnect' # Data Connect password

You may add these export lines to a text file and load with `source`:
  source ise-env.sh

"""
__author__ = "Thomas Howard"
__email__ = "thomas@cisco.com"
__license__ = "MIT - https://mit-license.org/"

import argparse
import oracledb
import os
import sys
import tabulate

ISE_DC_PORT=2484               # Data Connect port
ISE_DC_USERNAME='dataconnect'  # Data Connect username
ISE_DC_SID='cpm10'             # Data Connect service name identifier

argp = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
argp.add_argument('query', help='An Oracle PL/SQL Query - wrapped in double-quotes', default=None)
args = argp.parse_args()

env = {k:v for (k, v) in os.environ.items() if k.startswith('ISE_')}  # Load environment variables
ssl_verify = False if env['ISE_CERT_VERIFY'][0:1].lower() in ['f','n'] else True # certificate validation, default to True
params = oracledb.ConnectParams(protocol='tcps', host=env['ISE_PMNT'], port=ISE_DC_PORT, sid=ISE_DC_SID, ssl_server_dn_match=ssl_verify)
with oracledb.connect(user=ISE_DC_USERNAME, password=env['ISE_DC_PASSWORD'], params=params) as connection:
    with connection.cursor() as cursor:
        try:
            cursor.execute(args.query)
            headers = [i[0].lower() for i in cursor.description] # description: (name, type_code, display_size, internal_size, precision, scale, null_ok)
            rows = cursor.fetchall()
            print(tabulate.tabulate(rows, headers=headers, tablefmt='table', showindex=False))
        except oracledb.Error as e:
            print(e)
