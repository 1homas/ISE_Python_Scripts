#!/usr/bin/env python3
"""
Query ISE using SQL via Data Connect on the ISE Monitoring and Troubleshooting (MNT) node.
Supported environment variables:
  export ISE_PMNT='1.2.3.4'             # hostname or IP address of ISE Primary MNT
  export ISE_DC_USERNAME='dataconnect'  # Data Connect username
  export ISE_DC_PASSWORD='DataC0nnect'  # Data Connect password
  export ISE_DC_PORT=2484               # Data Connect port
  export ISE_VERIFY=False               # Optional: Disable TLS certificate verification (allow self-signed certs)

"""
__author__ = "Thomas Howard"
__email__ = "thomas@cisco.com"
__license__ = "MIT - https://mit-license.org/"

from isedc import ISEDC
import argparse  # https://docs.python.org/3/library/argparse.html
import oracledb  # https://python-oracledb.readthedocs.io/en/latest/
import logging
import os
import ssl
import sys
import time  # https://docs.python.org/3/library/datetime.html
import tabulate  # https://pypi.org/project/tabulate/
import csv
import json
import yaml
import traceback
import tracemalloc
import pandas as pd
from string import Template
import warnings

# Ignore 'UserWarning: pandas only supports SQLAlchemy connectable (engine/connection) or database string URI or sqlite3 DBAPI2 connection.'
warnings.simplefilter(action="ignore", category=UserWarning)


def read_file(filepath: str = None) -> str:
    if os.path.exists(filepath) and os.path.isfile(filepath):
        with open(filepath, mode="r", encoding="utf-8") as fh:
            return fh.read()


SQL_OPENAPI_OPS = """
    SELECT
        logged_at AS timestamp, -- timestamp
        -- request_time -- ⚠ TIMESTAMP(6) WITH TIME ZONE not supported in thin mode
        administrator, -- username
        client_ip,
        server, -- ISE PPAN
        http_method as method, -- [DELETE, GET, PATCH, PUT, POST]
        http_code AS status, -- HTTP numeric status code
        http_status, -- ⚠ text, not status code
        -- request_body, -- ⚠ may contain JSON and may be very large!
        -- request_id,
        request_name, -- URL of API endpoint
        response_duration AS time, -- milliseconds
        error_message AS error,
        message_text AS text -- ?
        -- response, -- ⚠ contains the JSON response and may be very large!
    FROM openapi_operations
    ORDER BY timestamp ASC -- first/oldest records
    """


SQL_OPENAPI_OPS_BY_USERNAME = """
SELECT
    TO_CHAR(logged_at, 'YYYY-MM-DD HH24:MI:SS') AS timestamp, -- drop fractional seconds
    -- request_time -- ⚠ TIMESTAMP(6) WITH TIME ZONE not supported in thin mode
    administrator, -- username
    client_ip,
    -- server, -- ISE PPAN
    http_method as method, -- [DELETE, GET, PATCH, PUT, POST]
    -- http_code AS status, -- HTTP numeric status code
    -- http_status, -- ⚠ text, not status code
    -- request_body, -- ⚠ may contain JSON and may be very large!
    -- request_id,
    request_name -- URL of API endpoint
    -- response_duration AS time, -- milliseconds
    -- error_message AS error,
    -- message_text AS text -- ?
    -- response, -- ⚠ contains the JSON response and may be very large!
FROM openapi_operations
WHERE administrator = '$username'
    AND logged_at > sysdate - INTERVAL '$days' DAY -- last N days
-- GROUP BY administrator, logged_at, client_ip, http_method, request_name
ORDER BY administrator ASC -- first/oldest records
"""

sql_change_configuration_audit = """
SELECT
    TO_CHAR(timestamp, 'YYYY-MM-DD HH24:MI:SS') AS timestamp, -- drop fractional seconds
    admin_name             , -- Name of the admin who made config change
    event                  , -- Config change done
    failure_flag           , -- Failure flag
    -- host_id                , -- Hostname of ISE node on which change is done
    -- id                     , -- Database unique ID
    -- interface              , -- Interface used for login GUI/CLI
    -- ise_node               , -- Hostname of ISE node
    -- applied_to_acs_instance, -- ISE nodes to which change is applied
    -- local_mode             , -- Local mode
    -- message_class          , -- Message class
    -- message_code           , -- Message code
    modified_properties    , -- Modified properties
    -- nas_ip_address         , -- IP address of NAD
    -- nas_ipv6_address       , -- IPV6 address of NAD
    operation_message_text , -- Operation details
    -- request_response_type  , -- Type of request response
    -- requested_operation    , -- Operation done
    -- object_id              , -- Object ID
    details                , -- Details of the event
    object_name            , -- Name of object for which config is changed
    object_type            -- Type of object for which config is changed
FROM change_configuration_audit
WHERE admin_name = '$username'
    AND timestamp > sysdate - INTERVAL '$days' DAY -- last N days
-- WHERE timestamp > sysdate - INTERVAL '10' SECOND -- last N seconds
-- WHERE timestamp > sysdate - INTERVAL '1' MINUTE  -- last N minutes
-- WHERE timestamp > sysdate - INTERVAL '1' HOUR -- last N hours
ORDER BY timestamp ASC -- first/oldest records
"""

if __name__ == "__main__":

    # Set up the command-line argument argp
    argp = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    argp.add_argument("-i", "--insecure", action="store_true", default=False, help="do not verify certificates (allow self-signed certs)")
    argp.add_argument("-l", "--level", default="WARNING", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], help="log threshold")
    argp.add_argument("-t", "--timer", action="store_true", default=False, help="show total script time")
    args = argp.parse_args()

    logging.basicConfig(stream=sys.stderr, format="%(asctime)s.%(msecs)03d | %(levelname)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    log = logging.getLogger("ISEDC")
    log.setLevel(args.level)

    with ISEDC(
        hostname=os.environ.get("ISE_PMNT"),
        password=os.environ.get("ISE_DC_PASSWORD"),
        insecure=True,
        level=args.level,
    ) as isedc:

        isedc_con = isedc.connect()

        # print(f"## Administrators", end="\n\n")
        # df_admins = pd.read_sql_query("SELECT DISTINCT admin_name FROM administrator_logins", isedc_con)
        # print(f"Admins: {df_admins['ADMIN_NAME'].to_list()}\n\n")
        # # print(f"{df_admins.to_markdown(index=False, tablefmt='github')}\n")
        # # print(f"{df_admins['ADMIN_NAME'].to_list()}\n\n{df_admins.to_markdown(index=False, tablefmt='github')}\n")

        # print(f"### API Operations by Username", end="\n\n")
        # for username in df_admins["ADMIN_NAME"].to_list():
        #     query = Template(SQL_OPENAPI_OPS_BY_USERNAME).substitute(username=username, days=7)
        #     # print(f"query:\n{query}")
        #     df = pd.read_sql_query(query, isedc_con)
        #     # print(f"## {username}\n\n{df.to_markdown(index=False, tablefmt='github')}\n")
        #     print(f"<details><summary><b>{username}</b> [{len(df)}]</summary>\n\n")
        #     print(df.to_markdown(index=False, tablefmt="github"))
        #     print(f"</details>\n")

        # print(f"### Configuration Audit by Username", end="\n\n")
        # for username in df_admins["ADMIN_NAME"].to_list():
        #     query = Template(sql_change_configuration_audit).substitute(username=username, days=7)
        #     # log.debug(f"query:\n{query}")
        #     df = pd.read_sql_query(query, isedc_con)
        #     print(f"<details><summary>{username} [{len(df)}]</summary>\n\n")
        #     print(df.to_markdown(index=False, tablefmt="github"))
        #     print(f"</details>\n")

        print(f"### Configuration Audit by Object_Type", end="\n\n")
        df_object_types = pd.read_sql_query("SELECT DISTINCT object_type FROM change_configuration_audit", isedc_con)
        print(df_object_types)
        print(f"object_types:\n{'\n'.join(df_object_types.dropna()['OBJECT_TYPE'].to_list())}")

        df_cfg_audit = pd.read_sql_query(read_file("data/SQL/change_configuration_audit.sql"), isedc_con)
        print(f"## Configuration Audit\n\n{df_cfg_audit.to_markdown(index=False, tablefmt='github')}\n")

        # print(f"tables: {tables()}", file=sys.stderr)
        # print(f"columns: {table_columns('network_devices')}", file=sys.stderr)
        # print(f"{column_widths('network_devices')}", file=sys.stderr)

        print(f"## RADIUS Authentications", end="\n\n")
        df = pd.read_sql_query(read_file("data/SQL/radius_auths.sql"), isedc_con)
        print(df.to_markdown(index=False, tablefmt="github"))

        print(f"## RADIUS Accounting", end="\n\n")
        df = pd.read_sql_query(read_file("data/SQL/radius_acct.sql"), isedc_con)
        print(df.to_markdown(index=False, tablefmt="github"))

        print(f"## Network Device Groups (NDGs)", end="\n\n")
        df_ndgs = pd.read_sql_query("SELECT * FROM network_device_groups ORDER BY name ASC", isedc_con)
        print(df_ndgs.to_markdown(index=False, tablefmt="github"))

        print(f"## Network Devices", end="\n\n")
        df_devices = pd.read_sql_query("SELECT * FROM network_devices ORDER BY name ASC", isedc_con)
        print(df_devices.to_markdown(index=False, tablefmt="github"))

        print(f"## Endpoint Identity Groups", end="\n\n")
        df_eigs = pd.read_sql_query("SELECT * FROM endpoint_identity_groups ORDER BY name ASC", isedc_con)
        print(df_eigs.to_markdown(index=False, tablefmt="github"))

        print(f"## Endpoints", end="\n\n")
        df_endpoints = pd.read_sql_query(read_file("data/SQL/endpoints_data.sql"), isedc_con)
        print(df_endpoints.to_markdown(index=False, tablefmt="github"))

        print(f"## ISE Nodes", end="\n\n")
        df_nodes = pd.read_sql_query("SELECT * FROM node_list ORDER BY hostname ASC", isedc_con)
        df_nodes.drop(
            [
                "API_NODE",
                "CREATE_TIME",
                "UPDATE_TIME",
                "INSTALLATION_TYPE",
                "PDP_SERVICES",
                "PIC_NODE",
                "UDI_VID",
                "XGRID_PEER",
                "XGRID_ENABLED",
            ],
            axis="columns",
            inplace=True,
        )
        print(df_nodes.to_markdown(index=False, tablefmt="github"))

        print(f"## Policy Sets", end="\n\n")
        # df_policy_sets = pd.read_sql_query(read_file("data/SQL/policy_sets.sql"), isedc_con)
        df_policy_sets = pd.read_sql_query(
            "SELECT id, policyset_status, policyset_name, description FROM policy_sets ORDER BY policyset_name ASC", isedc_con
        )
        print(df_policy_sets.to_markdown(index=False, tablefmt="github"))

        print(f"## Authorization Profiles", end="\n\n")
        df_authz_profiles = pd.read_sql_query(read_file("data/SQL/authorization_profiles.sql"), isedc_con)
        # df_policy_sets = pd.read_sql_query(
        #     "SELECT id, policyset_status, policyset_name, description FROM policy_sets ORDER BY authorization_profiles ASC", isedc_con
        # )
        print(df_authz_profiles.to_markdown(index=False, tablefmt="github"))

        # print(f"## Network Access Users", end="\n\n")
        # #  account_name_alias, last_successful_login_time, password_never_expires,identity_group
        # df_na_users = pd.read_sql_query(read_file("data/SQL/network_access_users.sql"), isedc_con)
        # df_na_users = pd.read_sql_query(
        #     "SELECT username, status, description, email_address, is_admin, expiry_date FROM network_access_users ORDER BY is_admin DESC, username ASC",
        #     isedc_con,
        # )
        # print(df_na_users.to_markdown(index=False, tablefmt="github"))

        print(f"## SGTs", end="\n\n")
        df_sgts = pd.read_sql_query(read_file("data/SQL/security_groups.sql"), isedc_con)
        print(df_sgts.to_markdown(index=False, tablefmt="github"))

        print(f"## SGACLs", end="\n\n")
        df_sgacls = pd.read_sql_query(read_file("data/SQL/security_group_acls.sql"), isedc_con)
        print(df_sgacls.to_markdown(index=False, tablefmt="github"))

        # Filter NDGs by 'Networks#Networks#'
        # networks = list(map(lambda name: print(name) if name.startswith("Networks#Networks#"), df["NAME"].to_list()))

        # df_ndgs = df_ndgs[df_ndgs["NAME"].str.startswith("Networks#Networks#")]
        # print(f"NDGs\n\n{df_ndgs['NAME'].to_list()}")

        # query_template = """
        # SELECT
        #     policy_set_name AS policy_set, --
        #     access_service AS allowed_protocols, --
        #     authentication_method AS authn_method, --
        #     authentication_protocol AS authn_protocol, --
        #     NVL(authorization_rule, '-') AS authz_rule, --
        #     NVL(authorization_profiles, 'ACCESS-REJECT') AS authz_profile, --
        #     MAX(security_group) AS security_group, --
        #     COUNT(CASE WHEN passed = 'Pass' THEN 1 END) AS passed,
        #     COUNT(CASE WHEN passed = 'Fail' THEN 1 END) AS failed,
        #     COUNT(timestamp) AS total,
        #     TO_CHAR(ROUND( (COUNT(CASE WHEN passed = 'Fail' THEN 1 END) / (COUNT(CASE WHEN passed = 'Pass' THEN 1 END) + COUNT(CASE WHEN passed = 'Fail' THEN 1 END)) * 100), 0), 'FM999') || '%' AS fail_pct
        # FROM radius_authentications
        # WHERE timestamp > sysdate - INTERVAL '7' DAY -- last N days
        #   AND location LIKE '%$ndg_name'
        # GROUP BY policy_set_name, access_service, authentication_method, authentication_protocol, authorization_rule, authorization_profiles
        # ORDER BY policy_set_name ASC, total DESC
        # """

        # query = read_file("data/SQL/radius_auths_by_network.sql")
        # ndg_name = "Networks#Networks#thomas"
        # cursor = isedc_con.cursor()
        # results = cursor.execute(
        #     query_template,
        #     [
        #         ndg_name,
        #     ],
        # ).fetchall()
        # print(f"results:\n\n{results}")

        # for ndg_name in df_ndgs["NAME"].to_list():
        #     query = Template(query_template).substitute(ndg_name=ndg_name.split("#")[2])
        #     # print(f"query:\n\n{query}")
        #     df = pd.read_sql_query(query, isedc_con)
        #     print(f"## {ndg_name}\n\n{df.to_markdown(index=False, tablefmt='github')}\n")
    if args.timer:
        print(f"⏱ {'{0:.3f}'.format(time.time() - start_time)} seconds", file=sys.stderr)
