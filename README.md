# README

A collection of useful Python scripts for working with the Cisco Identity Services Engine (ISE).

## Quick Start

1. Create your Python environment and install necessary Python packages :

```sh
pyenv-install.sh
pipenv shell
```

2. Some of these scripts require the use of these environment variables to communicate with ISE as a [security best practice](https://12factor.net/config):

```sh
export ISE_PPAN='1.2.3.4'             # hostname or IP address of ISE Primary PAN
export ISE_PMNT='1.2.3.4'             # hostname or IP address of ISE Primary MNT
export ISE_REST_USERNAME='admin'      # ISE ERS admin or operator username
export ISE_REST_PASSWORD='C1sco12345' # ISE ERS admin or operator password
export ISE_CERT_VERIFY=false          # validate the ISE certificate
```

You may conveniently edit these export lines in an `ise-environment.sh` text file and load them into your terminal environment with `source`:

```sh
source ise-environment.sh
```

Then verify your environment variables using `env` or `echo`:

```sh
env
echo $ISE_PPAN
```

3. These Python use ISE REST APIs so ensure your ISE node (Primary Administration Node) has the APIs enabled or you may run this script to enable them:

```sh
ise-api-enabled.py
```

4. Run the other scripts.

## cmdb-ci-generator.py

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

## ise-api-enabled.py / ise-api-enabled-aio.py

Enable the ISE ERS and OpenAPI APIs.

```sh
ise-api-enabled.py
```

Response:

```text
✅ ISE Open APIs Enabled
✅ ISE ERS APIs Enabled
```

## ise-ers-count.py

Get the total resource count of a specified ISE ERS resource.

```sh
ise-ers-count.py endpointgroup
```

Response:

```text
20
```

## ise-get.py

Show ISE ERS REST API data in a variety of ways.

- `csv`   : Show the items in a Comma-Separated Value (CSV) format
- `grid`  : Show the items in a grid with borders
- `table` : Show the items in a text table
- `id`    : Show only the id column for the objects (if available)
- `json`  : Show the items as a single JSON string
- `line`  : Show the items as JSON with each item on it's own line
- `pretty`: Show the items as JSON pretty-printed with 2-space indents
- `yaml`  : Show the items as YAML with 2-space indents

```sh
ise-get.py sgt
```

Response:

```json
{
  "sgt": [
    {
      "id": "8337f3e6-fdc7-449b-86a4-ba787c305f21",
      "name": "Cameras"
    },
    {
      "id": "93ad6890-8c01-11e6-996c-525400b48521",
      "name": "Employees",
      "description": "Employee Security Group"
    },
    {
      "id": "93c66ed0-8c01-11e6-996c-525400b48521",
      "name": "Guests",
      "description": "Guest Security Group"
    },
    {
      "id": "ccaf14ab-d8d7-438f-832d-0fdab0b07cfb",
      "name": "IOT"
    },
    {
      "id": "62cc161e-05c8-48bc-ac8b-cde3d77fad4e",
      "name": "NetServices",
      "description": "TrustSec Devices Security Group"
    },
    {
      "id": "947832a0-8c01-11e6-996c-525400b48521",
      "name": "TrustSec_Devices",
      "description": "TrustSec Devices Security Group"
    },
    {
      "id": "92adf9f0-8c01-11e6-996c-525400b48521",
      "name": "Unknown",
      "description": "Unknown Security Group"
    }
  ]
}
```

```sh
ise-get.py sgt -dtf grid --noid
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

## ise-get-ers-raw.py

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

### Resource with the UUID

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

## ise-get-ers.py

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

## ise-post-dacls.py

Generates the specified number of randomly named ISE downloadable ACLs using a REST API.

```sh
ise-post-dacls.py 3
✔ 1 201 https://ise.securitydemo.net/ers/config/downloadableacl/f71d5720-f04c-11ee-a00b-42be146d113b
✔ 2 201 https://ise.securitydemo.net/ers/config/downloadableacl/f71d3010-f04c-11ee-a00b-42be146d113b
✔ 3 201 https://ise.securitydemo.net/ers/config/downloadableacl/f71eb6b0-f04c-11ee-a00b-42be146d113b
```

## ise-post-endpoints.py

Generate the specified number of random ISE endpoint resources using REST APIs.

```sh
ise-post-endpoints.py 2
✔ 1 201 https://ise.securitydemo.net/ers/config/endpoint/0b50b250-f04d-11ee-a00b-42be146d113b
✔ 2 201 https://ise.securitydemo.net/ers/config/endpoint/0b6328e0-f04d-11ee-a00b-42be146d113b
```

## ise-post-internalusers.py

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

## ise-post-ers-embedded.py

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

## ise-post-ers-from-file.py

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

## ise-version.py

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

## ise-walk.py

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

## iseql.py

The ISE Data Connect feature was added in version 3.2 and offers you the ability to use any ODBC (Open Database Connectivity) driver to run Oracle PL/SQL queries directly against the ISE database.

Refer to the ISE [DataConnect documentation](https://cs.co/ise-dataconnect) for the [list of available database table views](https://cs.co/ise-dataconnect#!database-views) and [many SQL query examples](https://cs.co/ise-dataconnect#!guides).

The following environment variables are *required* to use `iseql.py`:

```sh
export ISE_PMNT='1.2.3.4'             # hostname or IP of the ISE Primary MNT node
export ISE_CERT_VERIFY=True           # Verify the ISE certificate
export ISE_DC_PASSWORD='#DataC0nnect' # Data Connect password
```

```sh
iseql.py "SELECT * FROM network_devices"
```

