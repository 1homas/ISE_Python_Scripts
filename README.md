# README


## Quick Start

1. Create your Python environment and install necessary Python packages :

    ```sh
    python -m ensurepip --upgrade
    pip3   install --upgrade pipenv     # use pipenv for virtual development environment
    pipenv install --python 3.9         # use Python 3.9 or later
    pipenv install -r requirements.txt  # install required packages (`pip freeze > requirements.txt`)
    pipenv shell
    ```

    If you have any problems installing Python or Ansible, see [Installing Ansible](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html).


2. Export your credentials for ISE into your shell environment. 

     export ISE_HOSTNAME='1.2.3.4'         # hostname or IP address of ISE PAN
     export ISE_REST_USERNAME='admin'      # ISE ERS admin or operator username
     export ISE_REST_PASSWORD='C1sco12345' # ISE ERS admin or operator password
     export ISE_CERT_VERIFY=false          # validate the ISE certificate

   You may store these lines to a text file and load with `source`:

      source ise.sh

1. These Python use ISE REST APIs so ensure your ISE node (Primary Administration Node) has the APIs enabled or you may run this script to enable them:

    ise_api_enabled.py

2. Run the other scripts.




## ise_enable_apis.py / ise_enable_apis_async.py

Enable the ISE ERS and OpenAPI APIs.

```bash
> ise_enable_apis.py
✅ ISE Open APIs Enabled
✅ ISE ERS APIs Enabled
```




## ise_ers_count.py

Get the total resource count of a specified ISE ERS resource.

```bash
> ise_ers_count.py endpointgroup
20
```




## ise_get_ers_raw.py

Get the raw output from an REST GET for resource list or resource.

A resource list by default :
```bash
> ise_get_ers_raw.py networkdevice
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

A specific resource with the UUID :
```bash
> ise_get_ers_raw.py networkdevice/0b6e9500-8b4a-11ec-ac96-46ca1867e58d
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




## ise_get_ers_resource.py

Get the detailed contents of all resources of the specified type :

```bash
> ise_get_ers_resource.py downloadableacl
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




## ise_post_ers_embedded.py

A simple REST POST example using JSON data embedded in the script. You may use `ise_get_ers_raw.py` to get sample resource JSON data to embed in your script.


```bash
> ise_post_ers_embedded.py
201
✅ View your new networkdevice
   https://198.18.133.27/ers/config/networkdevice/4aedf8f0-8b5a-11ec-ac96-46ca1867e58d
```




## ise_post_ers_from_file.py

Another REST POST example using JSON data in a separate file. This allows more flexibility to specify any resource type and the data file on the command line.

```bash
> ise_post_ers_from_file.py networkdevice my_network_device.json
201
✅ View your new networkdevice
   https://198.18.133.27/ers/config/networkdevice/a1f86c60-8b5b-11ec-ac96-46ca1867e58d
```




## ise_version.py

Very simple ISE version query.

```bash
> ise_version.py
{
  "version": "3.1.0.518",
  "patch": "1",
  "major": "3",
  "minor": "1",
  "maintenance": "0",
  "build": "518"
}
```




## ise_walk.py

Walk the ISE ERS resources to get a summary count of all of the objects.

```bash
> ise_walk.py
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


