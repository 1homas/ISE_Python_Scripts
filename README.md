# README

A collection of useful Python scripts for working with the Cisco Identity Services Engine (ISE).

## Quick Start

1. Create your Python environment and install the necessary packages from the `requirements.txt` list then launch your Python environment:

```sh
pipenv install -r requirements.txt
pipenv shell
```

2. Some of these scripts require the use of these environment variables to communicate with ISE as a [security best practice](https://12factor.net/config):

```sh
export ISE_PPAN='1.2.3.4'             # hostname or IP address of ISE Primary PAN
export ISE_PMNT='1.2.3.4'             # hostname or IP address of ISE Primary MNT
export ISE_REST_USERNAME='admin'      # ISE ERS admin or operator username
export ISE_REST_PASSWORD='C1sco12345' # ISE ERS admin or operator password
export ISE_VERIFY=False               # validate the ISE certificate (used by some scripts)
export ISE_CERT_VERIFY=$ISE_VERIFY    # validate the ISE certificate (used by some scripts)
```

You may disable TLS certificate verification and allow self-signed certs using the `-i`/`--insecure` command line option or the environment variable `ISE_VERIFY=False`.

You may conveniently import these environment variables from a `.env` text file into your terminal environment using `source .env` then verify your environment variables using `env` or `echo`:

```sh
env
echo $ISE_PPAN
```

3. Enable and verify the ISE REST APIs on your ISE PAN (Primary Administration Node) :

```sh
ise-api-enabled.py
```

4. Run the scripts.

## `cmdb-ci-generator.py`

Cisco Identity Services Engine (ISE) 3.2 and later has a feature called pxGrid Direct with the ability to retrieve JSON-formatted data representing tables of endpoint attributes and save them to data dictionaries in ISE. This capability is used to download configuration items (CIs) from configuration management databases (CMDBs) for use in authorizing endpoints as shown in the [Cisco ISE Webinar](https://cs.co/ise-webinars) [ISE pxGrid Direct with CMDBs](https://youtu.be/g8fzBPY8gU8).

In order to test this feature, it is very useful to generate a sample set of JSON data records that you can serve from any HTTP/S server as an ISE pxGrid Direct Connector. This script generates random data for functional and scale testing.

```sh
cmdb-ci-generator.py --help                 # see all of your options
cmdb-ci-generator.py                        # create a single, random config item in JSON
cmdb-ci-generator.py -n 10                  # create 10 config items on the screen
cmdb-ci-generator.py -n 1000 > CMDB.json    # create 1000 items saved to `CMDB.json`
cmdb-ci-generator.py -f line -tvn 1_000_000 > CMDB_1M.json  # save 1M CIs and time it
```

You may customize the script to included more or fewer columns/fields representing whichever attributes you think are interesting. Creating your new attributes and random data should be straightforward given the many examples in the script.

## `ise-api-enabled.py` / `ise-api-enabled-aio.py`

Enable the ISE ERS and OpenAPI APIs.

```sh
ise-api-enabled.py
```

Response:

```text
✅ ISE Open APIs Enabled
✅ ISE ERS APIs Enabled
```

## `ise-dc-enable.py`

Enable the ISE Data Connect feature via REST APIs.

```sh
ise-dc-enable.py
ⓘ Data Connect Enabled: False
ⓘ Data Connect Password: {'success': {'message': 'Dataconnect password has been updated successfully'}, 'version': '1.0.0'}
ⓘ Data Connect Password Expiration: {'success': {'message': 'Dataconnect password expiry has been updated successfully as 3650 days'}, 'version': '1.0.0'}
ⓘ Data Connect Password: {'success': {'message': 'Dataconnect Setting has been enabled and dataconnect certificate added to trust store successfully'}, 'version': '1.0.0'}
Data Connect Settings: {'isEnabled': True, 'isPasswordChanged': True, 'passwordExpiresOn': '02 April 2034 at 13:50 UTC', 'passwordExpiresInDays': 3650}
Data Connect Details: {'hostname': 'ise.securitydemo.net', 'port': 2484, 'servicename': 'cpm10', 'username': 'dataconnect'}
```

## `ise-endpoints-notifier.py`

Send a notification when a new, non-random MAC address(es) are detected in your ISE deployment by periodically querying ISE using the Data Connect feature and the ISEDC (ISE Data Connect Client)`isedc.py`.

```sh
ise-endpoints-notifier.py
```

## `ise-ers-count.py`

Get the total resource count of a specified ISE ERS resource.

```sh
ise-ers-count.py endpointgroup
```

Response:

```text
20
```

## `ise-get.py`

Show ISE ERS REST API data in a variety of formats. Uses Python `asyncio` to do it quickly for 100's or 1000's of resources.

- `csv` : Show the items in a Comma-Separated Value (CSV) format
- `grid` : Show the items in a grid with borders
- `table` : Show the items in a text table
- `id` : Show only the id column for the objects (if available)
- `json` : Show the items as a single JSON string
- `line` : Show the items as JSON with each item on it's own line
- `pretty`: Show the items as JSON pretty-printed with 2-space indents
- `yaml` : Show the items as YAML with 2-space indents

```sh
ise-get.py sgt
```

Response:

```text
id                                    name              description
------------------------------------  ----------------  --------------------------------
8337f3e6-fdc7-449b-86a4-ba787c305f21  Cameras
93ad6890-8c01-11e6-996c-525400b48521  Employees         Employee Security Group
93c66ed0-8c01-11e6-996c-525400b48521  Guests            Guest Security Group
ccaf14ab-d8d7-438f-832d-0fdab0b07cfb  IOT"
62cc161e-05c8-48bc-ac8b-cde3d77fad4e  NetServices       TrustSec Devices Security Group
947832a0-8c01-11e6-996c-525400b48521  TrustSec_Devices  TrustSec Devices Security Group
92adf9f0-8c01-11e6-996c-525400b48521  Unknown           Unknown Security Group
```

Use the `-d/--details` flag to perform an additional lookup for each resource to get all of their attributes:

```sh
ise-get.py sgt --time --format grid --details --hide id
```

Response:

```text
▶ 2023-06-16T10:01:11
┌──────────────────┬─────────┬────────────────┬───────────────────┬─────────────────────────────────┐
│ name             │   value │   generationId │ propogateToApic   │ description                     │
├──────────────────┼─────────┼────────────────┼───────────────────┼─────────────────────────────────┤
│ Cameras          │       7 │              8 │ False             │                                 │
├──────────────────┼─────────┼────────────────┼───────────────────┼─────────────────────────────────┤
│ Employees        │       4 │             28 │ True              │ Employee Security Group         │
├──────────────────┼─────────┼────────────────┼───────────────────┼─────────────────────────────────┤
│ Guests           │       6 │             28 │ True              │ Guest Security Group            │
├──────────────────┼─────────┼────────────────┼───────────────────┼─────────────────────────────────┤
│ IOT              │       5 │              8 │ False             │                                 │
├──────────────────┼─────────┼────────────────┼───────────────────┼─────────────────────────────────┤
│ NetServices      │       3 │              8 │ False             │ TrustSec Devices Security Group │
├──────────────────┼─────────┼────────────────┼───────────────────┼─────────────────────────────────┤
│ TrustSec_Devices │       2 │             28 │ True              │ TrustSec Devices Security Group │
├──────────────────┼─────────┼────────────────┼───────────────────┼─────────────────────────────────┤
│ Unknown          │       0 │             28 │ False             │ Unknown Security Group          │
└──────────────────┴─────────┴────────────────┴───────────────────┴─────────────────────────────────┘
■ 2023-06-16T10:01:12
⏲ 0.774 seconds
```

## `ise-get-ers-raw.py`

Get the raw output from an REST GET for resource list or resource.

### Resource list by default

```sh
ise-get-ers-raw.py networkdevice
```

```json
{
  "SearchResult": {
    "total": 2,
    "resources": [
      {
        "id": "0b6e9500-8b4a-11ec-ac96-46ca1867e58d",
        "name": "lab-mr46-1",
        "description": "",
        "link": {
          "rel": "self",
          "href": "https://198.18.133.27/ers/config/networkdevice/0b6e9500-8b4a-11ec-ac96-46ca1867e58d",
          "type": "application/json"
        }
      },
      {
        "id": "a1f86c60-8b5b-11ec-ac96-46ca1867e58d",
        "name": "my_network_device",
        "description": "",
        "link": {
          "rel": "self",
          "href": "https://198.18.133.27/ers/config/networkdevice/a1f86c60-8b5b-11ec-ac96-46ca1867e58d",
          "type": "application/json"
        }
      }
    ]
  }
}
```

### Filter JSON Output with `jq`

```sh
ise-get-ers-raw.py profilerprofile | jq .SearchResult.total
```

### Get Resource by UUID

```sh
ise-get-ers-raw.py networkdevice/0b6e9500-8b4a-11ec-ac96-46ca1867e58d
```

Response:

```json
{
  "NetworkDevice": {
    "id": "0b6e9500-8b4a-11ec-ac96-46ca1867e58d",
    "name": "lab-mr46-1",
    "description": "",
    "authenticationSettings": {
      "networkProtocol": "RADIUS",
      "radiusSharedSecret": "C1sco12345",
      "enableKeyWrap": false,
      "dtlsRequired": false,
      "keyEncryptionKey": "",
      "messageAuthenticatorCodeKey": "",
      "keyInputFormat": "ASCII",
      "enableMultiSecret": "false"
    },
    "profileName": "Cisco",
    "coaPort": 1700,
    "link": {
      "rel": "self",
      "href": "https://198.18.133.27/ers/config/networkdevice/0b6e9500-8b4a-11ec-ac96-46ca1867e58d",
      "type": "application/json"
    },
    "NetworkDeviceIPList": [
      {
        "ipaddress": "10.80.60.151",
        "mask": 32
      }
    ],
    "NetworkDeviceGroupList": [
      "Location#All Locations",
      "IPSEC#Is IPSEC Device#No",
      "Device Type#All Device Types"
    ]
  }
}
```

## `ise-get-ers.py`

Get the detailed contents of all resources of the specified type :

```sh
ise-get-ers.py downloadableacl
```

Response:

```json
{
  "DownloadableAcl": [
    {
      "id": "9825aa40-8c01-11e6-996c-525400b48521",
      "name": "DENY_ALL_IPV4_TRAFFIC",
      "description": "Deny all ipv4 traffic",
      "dacl": "deny ip any any",
      "daclType": "IPV4"
    },
    {
      "id": "5cc3d850-ea30-11ea-8b14-005056871e13",
      "name": "DENY_ALL_IPV6_TRAFFIC",
      "description": "Deny all ipv6 traffic",
      "dacl": "deny ipv6 any any",
      "daclType": "IPV6"
    },
    {
      "id": "982498d0-8c01-11e6-996c-525400b48521",
      "name": "PERMIT_ALL_IPV4_TRAFFIC",
      "description": "Allow all ipv4 Traffic",
      "dacl": "permit ip any any",
      "daclType": "IPV4"
    },
    {
      "id": "5cc278c0-ea30-11ea-8b14-005056871e13",
      "name": "PERMIT_ALL_IPV6_TRAFFIC",
      "description": "Allow all ipv6 Traffic",
      "dacl": "permit ipv6 any any",
      "daclType": "IPV6"
    }
  ]
}
```

## `ise-post-dacls.py`

Generates the specified number of randomly named ISE downloadable ACLs using a REST API.

```sh
ise-post-dacls.py 3
✔ 1 201 https://ise.securitydemo.net/ers/config/downloadableacl/f71d5720-f04c-11ee-a00b-42be146d113b
✔ 2 201 https://ise.securitydemo.net/ers/config/downloadableacl/f71d3010-f04c-11ee-a00b-42be146d113b
✔ 3 201 https://ise.securitydemo.net/ers/config/downloadableacl/f71eb6b0-f04c-11ee-a00b-42be146d113b
```

## `ise-post-endpoints.py`

Generate the specified number of random ISE endpoint resources using REST APIs.

```sh
ise-post-endpoints.py 2
✔ 1 201 https://ise.securitydemo.net/ers/config/endpoint/0b50b250-f04d-11ee-a00b-42be146d113b
✔ 2 201 https://ise.securitydemo.net/ers/config/endpoint/0b6328e0-f04d-11ee-a00b-42be146d113b
```

## `ise-post-internalusers.py`

Generates the specified number of ISE internaluser resources using a REST API.

```sh
ise-post-internalusers.py 1
✔ 201 | jwood | c9107917-3d4c-4f2e-96c9-2ccba5f9220a

ise-post-internalusers.py -vt 3
ⓘ Cached 90 existing users
✔ 201 | rrobbins | e6ca8c5f-e5b0-4165-8031-ea78adbb125a
✔ 201 | rmanning | 236370d0-e4e2-42a1-9465-ee87d2541eea
✔ 201 | mwolfe | f331682f-d106-456e-af47-48ac4bbb78d2
⏲ 0.540 seconds
```

## `ise-post-ers-embedded.py`

A simple REST POST example using JSON data embedded in the script. You may use `ise-get-ers-raw.py` to get sample resource JSON data to embed in your script.

```sh
ise-post-ers-embedded.py
```

Response:

```text
201
✅ View your new networkdevice
   https://198.18.133.27/ers/config/networkdevice/4aedf8f0-8b5a-11ec-ac96-46ca1867e58d
```

## `ise-post-ers-from-file.py`

Another REST POST example using JSON data in a separate file. This allows more flexibility to specify any resource type and the data file on the command line.

```sh
ise-post-ers-from-file.py networkdevice data/JSON/my_network_device.json
```

Response:

```text
201
✅ View your new networkdevice
   https://198.18.133.27/ers/config/networkdevice/a1f86c60-8b5b-11ec-ac96-46ca1867e58d
```

## `ise-version.py`

Very simple ISE version query that also generates a [semantic version](https://semver.org) for convenience.

```sh
ise-version.py
```

Response:

```json
{
  "version": "3.3.0.430",
  "patch": "1",
  "major": "3",
  "minor": "3",
  "maintenance": "0",
  "build": "430",
  "semver": "3.3.1"
}
```

## `ise-walk.py`

Walk the ISE ERS resources to get a summary count of all of the objects.

```sh
ise-walk.py
```

Response:

```text
C▶198.18.133.27
 ┣╸node [1]
 ┣╸sessionservicenode [0]
 ┣╸networkdevicegroup [5]
 ┣╸networkdevice [0]
 ┣╸endpointgroup [20]
 ┣╸endpoint [0]
 ┣╸endpointcert [0] ⟁ POST endpointcert only!
 ┣╸profilerprofile [677]
 ┣╸activedirectory [0]
 ┣╸allowedprotocols [2]
 ┣╸adminuser [1]
 ┣╸identitygroup [8]
 ┣╸internaluser [0]
 ┣╸externalradiusserver [0]
 ┣╸radiusserversequence [0]
 ┣╸idstoresequence [5]
 ┣╸restidstore [0]
 ┣╸authorizationprofile [9]
 ┣╸downloadableacl [4]
 ┣╸filterpolicy [0]
 ┣╸portal [5]
 ┣╸portalglobalsetting [1]
 ┣╸portaltheme [4]
 ┣╸hotspotportal [1]
 ┣╸selfregportal [1]
 ┣╸guestlocation [1]
 ┣╸guestsmtpnotificationsettings [1]
 ┣╸guestssid [0]
 ┣╸guesttype [4]
 ┣╸guestuser [0] ⟁ requires sponsor account
 ┣╸smsprovider [9]
 ┣╸sponsorportal [1]
 ┣╸sponsoredguestportal [1]
 ┣╸sponsorgroup [3]
 ┣╸sponsorgroupmember [4]
 ┣╸certificateprofile [0]
 ┣╸certificatetemplate [3]
 ┣╸byodportal [1]
 ┣╸mydeviceportal [1]
 ┣╸nspprofile [2]
 ┣╸sgt [16]
 ┣╸sgacl [4]
 ┣╸sgmapping [0]
 ┣╸sgmappinggroup [0]
 ┣╸sgtvnvlan [0]
 ┣╸egressmatrixcell [1]
 ┣╸sxpconnections [0]
 ┣╸sxplocalbindings [0]
 ┣╸sxpvpns [1]
 ┣╸tacacscommandsets [1]
 ┣╸tacacsexternalservers [0] ⟁ Not configured
 ┣╸tacacsprofile [4]
 ┣╸tacacsserversequence [0] ⟁ Not configured
 ┣╸ancendpoint [0]
 ┣╸ancpolicy [0]
```

## `isedc.py`

This builds on `iseql.py` by creating an ISEDC (ISE Data Connect Client) Python class that may be used to establish a single, long-lived connection for many SQL queries to generate charts, reports, etc. While meant to be used by other scripts (see `ise-endpoints-notifier.py`), it conveniently has the same command line arguments as `iseql.py` wrapped around the ISEDC class if you only want to use it.

## `iseql.py`

Conveniently run an Oracle PL/SQL query directly against the ISE database from the command line. This script uses ISE Data Connect feature - added in ISE 3.2 - and works with any ODBC (Open Database Connectivity) driver. To learn more about the [ISE Data Connect](https://cs.co/ise-dataconnect) documentation with the list of available [database table views](https://cs.co/ise-dataconnect#!database-views) and [SQL query examples](https://cs.co/ise-dataconnect#!guides). The ISE Webinars ▷ [Next Generation ISE Telemetry, Monitoring, and Custom Reporting Part 2](https://youtu.be/dp7HWthncks) and ▷[How to Get Data Out of ISE](https://youtu.be/vBw4CxX_EhM) also cover it.

The following environment variables are _recommended_ with `iseql.py`:

```sh
export ISE_PMNT='1.2.3.4'             # hostname or IP of the ISE Primary MNT node
export ISE_DC_PASSWORD='D@t@C0nnect'  # Data Connect password
export ISE_VERIFY=Fals                # for self-signed certs
```


Example:

```sh
iseql.py "SELECT * FROM network_devices"
id,name,ip_mask,profile_name,location,type
c81f36f0-89cb-11ef-9c62-6ecbd13ff78e,thomas-mx68-3vq7,10.1.10.1/32,Cisco,Location#All Locations#Networks#thomas,Device Type#All Device Types#Meraki#MX#MX68
```

The default output is instantly streamed as CSV (comma-separated values) because "pretty" table formats require *buffering all results in memory* first to calculate maximum column widths *then* write the beautifully aligned table. 

Be careful with queries of large tables like `radius_authentications` and `radius_accounting`! Downloading 10,000+ rows will take many seconds and 3X or more with some "pretty" formats. A quick performance time test using the `-t/timer` option to retrieve 10,000 RADIUS Accounting rows (`iseql.py "SELECT * FROM radius_accounting FETCH FIRST 10000 ROWS ONLY" -tf csv`):

| Format          | Time (seconds) |
|-----------------|----------------|
| `csv` (default) |            3.9 |
| `json`          |            4.7 |
| `line`          |            4.9 |
| `pretty`        |            4.9 |
| `text`          |           11.8 |
| `table`         |           11.9 |
| `markdown`      |           12.0 |
| `yaml`          |           29.0 |


Edit, save, and use your complex queries in `*.sql` files or try some of mine from the `data/SQL/` directory:

```sh
iseql.py data/sql/radius_acct_counts_by_day.sql -f markdown
| timestamp   |   starts |   stops |   interims |   others |   total |
|-------------|----------|---------|------------|----------|---------|
| 2024-09-01  |       22 |      21 |          0 |        0 |      43 |
| 2024-09-02  |       29 |      30 |          0 |        0 |      59 |
| 2024-09-03  |       22 |      21 |          0 |        0 |      43 |
| 2024-09-04  |       20 |      20 |          0 |        0 |      40 |
| 2024-09-05  |       40 |      40 |          0 |        0 |      80 |
| 2024-09-06  |       68 |      64 |          0 |       56 |     188 |
| 2024-09-07  |       67 |      67 |          0 |        0 |     134 |
```

