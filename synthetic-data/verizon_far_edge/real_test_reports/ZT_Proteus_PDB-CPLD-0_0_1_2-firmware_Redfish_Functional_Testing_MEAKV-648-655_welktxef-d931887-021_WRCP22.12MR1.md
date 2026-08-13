# ZT Proteus .46 BMC firmware validation
# ZT Proteus BIOS .23
# Redfish Functional Testing MEAKV-648-MEAKV-654 
# 3/12/24 James Patchett

## Target subclouds RU_12,13 Right and Left side

## Left side Subcloud welktxef-d931887-021
## BMC 0.46 BIOS 0.23
BMC:  2607:f160:10:9249:ce:40a:0:e015
OAM:  2607:f160:10:9249:ce:40a:0:f409

## Subcloud welktxef-d931887-021 Info
```log
XXXXXX@controller-0:~$ source /etc/platform/openrc
[XXXXXX@controller-0 ~(keystone_admin)]$ system show
+------------------------+--------------------------------------+
| Property               | Value                                |
+------------------------+--------------------------------------+
| contact                | None                                 |
| created_at             | 2024-03-07T18:03:00.044462+00:00     |
| description            | None                                 |
| distributed_cloud_role | subcloud                             |
| https_enabled          | True                                 |
| latitude               | None                                 |
| location               | None                                 |
| longitude              | None                                 |
| name                   | welktxef-d931887-021                 |
| region_name            | welktxef-d931887-021                 |
| sdn_enabled            | False                                |
| security_feature       | spectre_meltdown_v1                  |
| service_project_name   | services                             |
| shared_services        | []                                   |
| software_version       | 22.12                                |
| system_mode            | simplex                              |
| system_type            | All-in-one                           |
| timezone               | UTC                                  |
| updated_at             | 2024-03-11T19:05:24.739152+00:00     |
| uuid                   | 23aff978-9c1f-4e92-aca9-97621b54bd8a |
| vswitch_type           | none                                 |
+------------------------+--------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ system application-list
+--------------------------+----------+-------------------------------------------+------------------+---------+-----------+
| application              | version  | manifest name                             | manifest file    | status  | progress  |
+--------------------------+----------+-------------------------------------------+------------------+---------+-----------+
| cert-manager             | 22.12-8  | cert-manager-fluxcd-manifests             | fluxcd-manifests | applied | completed |
| metrics-server           | 22.12-1  | metrics-server-fluxcd-manifests           | fluxcd-manifests | applied | completed |
| nginx-ingress-controller | 22.12-1  | nginx-ingress-controller-fluxcd-manifests | fluxcd-manifests | applied | completed |
| oidc-auth-apps           | 22.12-6  | oidc-auth-apps-fluxcd-manifests           | fluxcd-manifests | applied | completed |
| platform-integ-apps      | 22.12-66 | platform-integ-apps-fluxcd-manifests      | fluxcd-manifests | applied | completed |
| wr-analytics             | 23.09-0  | wr-analytics-fluxcd-manifests             | fluxcd-manifests | applied | completed |
+--------------------------+----------+-------------------------------------------+------------------+---------+-----------+
[XXXXXX@controller-0 ~(keystone_admin)]$ sw-patch query
      Patch ID         RR  Release  Patch State
=====================  ==  =======  ===========
WRCP_22.12_PATCH_0001  Y    22.12    Committed
WRCP_22.12_PATCH_0002  Y    22.12    Committed
WRCP_22.12_PATCH_0003  Y    22.12    Committed
WRCP_22.12_PATCH_0004  Y    22.12    Committed

[XXXXXX@controller-0 ~(keystone_admin)]$
```

## Subcloud welktxef-d931887-021

## MEAKV-648
## Check version of BIOS 
```log
[XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[${IP}]/redfish/v1/UpdateService/FirmwareInventory/BIOS | jq .
{
  "@odata.context": "/redfish/v1/$metadata#SoftwareInventory.SoftwareInventory",
  "@odata.etag": "\"1710182309\"",
  "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/BIOS",
  "@odata.type": "#SoftwareInventory.v1_2_3.SoftwareInventory",
  "Id": "BIOS",
  "Name": "BIOS",
  "Updateable": true,
  "Version": "0.23"
}
[XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$

```

## Check version of BMC

```log
[XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[${IP}]/redfish/v1/UpdateService/FirmwareInventory/BMC | jq .
{
  "@odata.context": "/redfish/v1/$metadata#SoftwareInventory.SoftwareInventory",
  "@odata.etag": "\"1710182976\"",
  "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/BMC",
  "@odata.type": "#SoftwareInventory.v1_2_3.SoftwareInventory",
  "Id": "BMC",
  "Name": "BMC",
  "Updateable": true,
  "Version": "0.46.00"
}
[XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$
```

## MEAKV-649
## set hostname with ZT_Redfish_tests.yml

```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ ansible-playbook --vault-password-file ./vault_pass.txt -i inventory-fe/rchltxfe-1.yml -e attributes_file=vars/proteus_redfish_attributes.yml -e target="welktxef-931887-rz-le2pts6-021" --tags hostname ZT_Redfish_tests.yml

PLAY [welktxef-931887-rz-le2pts6-021] ***********************************************************************************************************

TASK [redfish/attributes : what we're setting] **************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "set_attr_item": {
        "attribute": "HostName",
        "new_value": "newhostname2",
        "path": "/redfish/v1/Systems/Self"
    }
}

TASK [redfish/attributes : Setting HostName] ****************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [redfish/attributes : debug] ***************************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "response": {
        "access_control_allow_credentials": "true",
        "access_control_allow_headers": "X-Auth-Token",
        "access_control_allow_origin": "*",
        "access_control_expose_headers": "X-Auth-Token",
        "allow": "GET,PATCH",
        "cache_control": "no-cache, must-revalidate",
        "changed": false,
        "connection": "close",
        "cookies": {},
        "cookies_string": "",
        "date": "Tue, 12 Mar 2024 21:33:04 GMT",
        "elapsed": 2,
        "etag": "\"1710279184\"",
        "failed": false,
        "msg": "OK (unknown bytes)",
        "odata_version": "4.0",
        "redirected": false,
        "server": "AMI MegaRAC Redfish Service",
        "status": 204,
        "url": "https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Systems/Self"
    }
}

TASK [redfish/attributes : set_fact] ************************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [redfish/attributes : sleep if needed] *****************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]
included: /home/XXXXXX/richardson/playbooks/vcp-fe-ib-automation/roles/redfish/attributes/tasks/check_attribute.yml for welktxef-931887-rz-le2pts6-021

TASK [redfish/attributes : what is currently verified] ******************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "msg": "Sending GET to /redfish/v1/Systems/Self and query the returned json for HostName. Value shall be newhostname2"
}

TASK [redfish/attributes : Checking HostName at /redfish/v1/Systems/Self] ***********************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [redfish/attributes : what we're setting] **************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "set_attr_item": {
        "attribute": "HostName",
        "new_value": "welktxef-931887-rz-le2pts6-021",
        "path": "/redfish/v1/Systems/Self"
    }
}

TASK [redfish/attributes : Setting HostName] ****************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [redfish/attributes : debug] ***************************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "response": {
        "access_control_allow_credentials": "true",
        "access_control_allow_headers": "X-Auth-Token",
        "access_control_allow_origin": "*",
        "access_control_expose_headers": "X-Auth-Token",
        "allow": "GET,PATCH",
        "cache_control": "no-cache, must-revalidate",
        "changed": false,
        "connection": "close",
        "cookies": {},
        "cookies_string": "",
        "date": "Tue, 12 Mar 2024 21:34:08 GMT",
        "elapsed": 2,
        "etag": "\"1710279248\"",
        "failed": false,
        "msg": "OK (unknown bytes)",
        "odata_version": "4.0",
        "redirected": false,
        "server": "AMI MegaRAC Redfish Service",
        "status": 204,
        "url": "https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Systems/Self"
    }
}

TASK [redfish/attributes : set_fact] ************************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]
included: /home/XXXXXX/richardson/playbooks/vcp-fe-ib-automation/roles/redfish/attributes/tasks/check_attribute.yml for welktxef-931887-rz-le2pts6-021

TASK [redfish/attributes : what is currently verified] ******************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "msg": "Sending GET to /redfish/v1/Systems/Self and query the returned json for HostName. Value shall be welktxef-931887-rz-le2pts6-021"
}

TASK [redfish/attributes : Checking HostName at /redfish/v1/Systems/Self] ***********************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

PLAY RECAP **************************************************************************************************************************************
welktxef-931887-rz-le2pts6-021 : ok=15   changed=0    unreachable=0    failed=0    skipped=5    rescued=0    ignored=0

(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$
```

## MEAKV-650
## set static DNS servers via api

## check Current

```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[$IP]/redfish/v1/Managers/Self/EthernetInterfaces/eth0 | jq .StaticNameServers
[
  "2607:f160:10:4409:ce:103:0:5",
  "2607:f160:10:4409:ce:103:0:6",
  "::"
]
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$
```

## Set to DNS servers to different address to confirm it changes... with ZT_Redfish_tests.yml
## changed IPs in GUI of BMC... 7 and 8 in  now
```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[$IP]/redfish/v1/Managers/Self/EthernetInterfaces/eth0 | jq .StaticNameServers
[
  "2607:f160:10:4409:ce:103:0:7",
  "2607:f160:10:4409:ce:103:0:8",
  "::"
]
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ ansible-playbook --vault-password-file ./vault_pass.txt -i inventory-fe/rchltxfe-1.yml -e attributes_file=vars/proteus_redfish_attributes.yml -e target="welktxef-931887-rz-le2pts6-021" --tags dns ZT_Redfish_tests.yml

PLAY [welktxef-931887-rz-le2pts6-021] ***********************************************************************************************************
included: /home/XXXXXX/richardson/playbooks/vcp-fe-ib-automation/roles/redfish/attributes/tasks/set_attribute.yml for welktxef-931887-rz-le2pts6-021 => (item={'path': '/redfish/v1/Managers/Self/EthernetInterfaces/eth0', 'attribute': 'StaticNameServers', 'new_value': ['2607:f160:10:4409:ce:103:0:5', '2607:f160:10:4409:ce:103:0:6'], 'expected_response': 202, 'expected_value': ['2607:f160:10:4409:ce:103:0:5', '2607:f160:10:4409:ce:103:0:6', '::']})

TASK [redfish/attributes : what we're setting] **************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "set_attr_item": {
        "attribute": "StaticNameServers",
        "expected_response": 202,
        "expected_value": [
            "2607:f160:10:4409:ce:103:0:5",
            "2607:f160:10:4409:ce:103:0:6",
            "::"
        ],
        "new_value": [
            "2607:f160:10:4409:ce:103:0:5",
            "2607:f160:10:4409:ce:103:0:6"
        ],
        "path": "/redfish/v1/Managers/Self/EthernetInterfaces/eth0"
    }
}

TASK [redfish/attributes : Setting StaticNameServers] *******************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [redfish/attributes : debug] ***************************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "response": {
        "access_control_allow_credentials": "true",
        "access_control_allow_headers": "X-Auth-Token",
        "access_control_allow_origin": "*",
        "access_control_expose_headers": "X-Auth-Token",
        "allow": "GET, PATCH",
        "cache_control": "no-cache, must-revalidate",
        "changed": false,
        "connection": "close",
        "content_length": "245",
        "content_type": "application/json; charset=UTF-8",
        "cookies": {},
        "cookies_string": "",
        "date": "Tue, 12 Mar 2024 21:39:05 GMT",
        "elapsed": 1,
        "etag": "\"1710279483\"",
        "failed": false,
        "json": {
            "@odata.context": "/redfish/v1/$metadata#Task.Task",
            "@odata.id": "/redfish/v1/TaskService/Tasks/10",
            "@odata.type": "#Task.v1_4_2.Task",
            "Description": "Task for EthernetInterface Action",
            "Id": "10",
            "Name": "EthernetInterface Action",
            "TaskState": "New"
        },
        "link": "<http://redfish.dmtf.org/schemas/v1/EthernetInterface.v1_5_1.json>; rel=describedby, <http://redfish.dmtf.org/schemas/v1/Task.v1_4_2.json>, </redfish/v1/TaskService/Tasks/10>; path=",
        "location": "https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/10",
        "msg": "OK (245 bytes)",
        "odata_version": "4.0",
        "prefer": "respond-async; wait=1",
        "redirected": false,
        "server": "AMI MegaRAC Redfish Service",
        "status": 202,
        "url": "https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Managers/Self/EthernetInterfaces/eth0"
    }
}

TASK [redfish/attributes : set_fact] ************************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [redfish/attributes : sleep if needed] *****************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]
included: /home/XXXXXX/richardson/playbooks/vcp-fe-ib-automation/roles/redfish/attributes/tasks/check_attribute.yml for welktxef-931887-rz-le2pts6-021

TASK [redfish/attributes : what is currently verified] ******************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "msg": "Sending GET to /redfish/v1/Managers/Self/EthernetInterfaces/eth0 and query the returned json for StaticNameServers. Value shall be ['2607:f160:10:4409:ce:103:0:5', '2607:f160:10:4409:ce:103:0:6', '::']"
}

TASK [redfish/attributes : Checking StaticNameServers at /redfish/v1/Managers/Self/EthernetInterfaces/eth0] *************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

PLAY RECAP **************************************************************************************************************************************
welktxef-931887-rz-le2pts6-021 : ok=9    changed=0    unreachable=0    failed=0    skipped=2    rescued=0    ignored=0

(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$
```

## DNS looks good, moving to next test.

## MEAKV-651
## Set NTP servers

## check exiting values

```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[$IP]/redfish/v1/Managers/Self/NetworkProtocol | jq .NTP
{
  "NTPServers": [
    "2607:f160:10:9200::a",
    "2607:f160:10:9200::b"
  ],
  "Port": 123,
  "ProtocolEnabled": false
}
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$
```

## Changing values in BMC UI

## checking values again with wrong server addresses

```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[$IP]/redfish/v1/Managers/Self/NetworkProtocol | jq .NTP
{
  "NTPServers": [
    "2607:f160:10:9200::c",
    "2607:f160:10:9200::d"
  ],
  "Port": 123,
  "ProtocolEnabled": true
}
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$

```


## Now run ZT_Redfish_tests.yml ansible script to set back to correct servers
## Set ntp

```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ ansible-playbook --vault-password-file ./vault_pass.txt -i inventory-fe/rchltxfe-1.yml -e attributes_file=vars/proteus_redfish_attributes.yml -e target="welktxef-931887-rz-le2pts6-021" --tags ntp ZT_Redfish_tests.yml

PLAY [welktxef-931887-rz-le2pts6-021] ***********************************************************************************************************

TASK [redfish/attributes : what we're setting] **************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "set_attr_item": {
        "attribute": "NTP",
        "expected_value": [
            "2607:f160:10:9200::a",
            "2607:f160:10:8200::a"
        ],
        "new_value": {
            "NTPServers": [
                "2607:f160:10:9200::a",
                "2607:f160:10:8200::a"
            ]
        },
        "path": "/redfish/v1/Managers/Self/NetworkProtocol",
        "verify_attribute": "NTP.NTPServers"
    }
}

TASK [redfish/attributes : Setting NTP] *********************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [redfish/attributes : debug] ***************************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "response": {
        "access_control_allow_credentials": "true",
        "access_control_allow_headers": "X-Auth-Token",
        "access_control_allow_origin": "*",
        "access_control_expose_headers": "X-Auth-Token",
        "allow": "GET, PATCH",
        "cache_control": "no-cache, must-revalidate",
        "changed": false,
        "connection": "close",
        "cookies": {},
        "cookies_string": "",
        "date": "Thu, 14 Mar 2024 08:32:27 GMT",
        "elapsed": 2,
        "etag": "\"1710279607\"",
        "failed": false,
        "msg": "OK (unknown bytes)",
        "odata_version": "4.0",
        "redirected": false,
        "server": "AMI MegaRAC Redfish Service",
        "status": 204,
        "url": "https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Managers/Self/NetworkProtocol"
    }
}

TASK [redfish/attributes : set_fact] ************************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [redfish/attributes : sleep if needed] *****************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]
included: /home/XXXXXX/richardson/playbooks/vcp-fe-ib-automation/roles/redfish/attributes/tasks/check_attribute.yml for welktxef-931887-rz-le2pts6-021

TASK [redfish/attributes : what is currently verified] ******************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "msg": "Sending GET to /redfish/v1/Managers/Self/NetworkProtocol and query the returned json for NTP.NTPServers. Value shall be ['2607:f160:10:9200::a', '2607:f160:10:8200::a']"
}

TASK [redfish/attributes : Checking NTP.NTPServers at /redfish/v1/Managers/Self/NetworkProtocol] ************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

PLAY RECAP **************************************************************************************************************************************
welktxef-931887-rz-le2pts6-021 : ok=8    changed=0    unreachable=0    failed=0    skipped=2    rescued=0    ignored=0

(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$
```

## verify settings took with a query to redfish db

```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[$IP]/redfish/v1/Managers/Self/NetworkProtocol | jq .NTP
{
  "NTPServers": [
    "2607:f160:10:9200::a",
    "2607:f160:10:8200::a"
  ],
  "Port": 123,
  "ProtocolEnabled": true
}
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$
```
## success, next test

## MEAKV-652
## delete subscription then put it back

## redfish DB reset command, will result in deleting exisiting subscriptions

```sh
curl -sk -u XXXXXX:XXXXXX -X POST "https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/Managers/Self/Actions/Oem/AMIManager.RedfishDBReset" -d '{"RedfishDBResetType": "ResetAll"}' -H "Content-Type: application/json" | python3 -m json.tool
```
## delete the subscription by reseting the redfish DB

```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ curl -sk -u XXXXXX:XXXXXX -X POST "https://[$IP]/redfish/v1/Managers/Self/Actions/Oem/AMIManager.RedfishDBReset" -d '{"RedfishDBResetType": "ResetAll"}' -H "Content-Type: application/json" | python3 -m json.tool
{
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.id": "/redfish/v1/TaskService/Tasks/1",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for RedfishDBReset Task",
    "Id": "1",
    "Name": "RedfishDBReset Task",
    "TaskState": "New"
}
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$
```

## check that subscription is deleted

```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[$IP]/redfish/v1/EventService/Subscriptions | jq .
{
  "@odata.context": "/redfish/v1/$metadata#EventDestinationCollection.EventDestinationCollection",
  "@odata.etag": "\"1710282948\"",
  "@odata.id": "/redfish/v1/EventService/Subscriptions",
  "@odata.type": "#EventDestinationCollection.EventDestinationCollection",
  "Description": "Collection for Event Subscriptions",
  "Members": [],
  "Members@odata.count": 0,
  "Name": "Event Subscriptions Collection"
}
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$
```

## Now set the subscription URL to bmc

```sh
export IP=2607:f160:10:80b1:ce:40a:0:e008
curl -i -s -u XXXXXX:XXXXXX -H "Content-Type: application/json" -k -X POST -n -d '
{
"Context": "Subscription_VCMP-1",
"Destination": "https://vcpme-rch-feocp-redfishalerts.mon.vzwops.com/redfish",
"Protocol": "Redfish"
}' https://[${IP}]/redfish/v1/EventService/Subscriptions

```

```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ echo $IP
2607:f160:10:9249:ce:40a:0:e015
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ curl -i -s -u XXXXXX:XXXXXX -H "Content-Type: application/json" -k -X POST -n -d '
> {
> "Context": "Subscription_VCMP-1",
> "Destination": "https://vcpme-rch-feocp-redfishalerts.mon.vzwops.com/redfish",
> "Protocol": "Redfish"
> }' https://[${IP}]/redfish/v1/EventService/Subscriptions
HTTP/1.1 201 Created
Server: AMI MegaRAC Redfish Service
Location: /redfish/v1/EventService/Subscriptions/1
Allow: GET, POST
Access-Control-Allow-Origin: *
Access-Control-Expose-Headers: X-Auth-Token
Access-Control-Allow-Headers: X-Auth-Token
Access-Control-Allow-Credentials: true
Cache-Control: no-cache, must-revalidate
Link: <http://redfish.dmtf.org/schemas/v1/EventDestination.v1_6_0.json>; rel=describedby
Link: <http://redfish.dmtf.org/schemas/v1/EventDestination.v1_6_0.json>
Link: </redfish/v1/EventService/Subscriptions>; path=
ETag: "1710283092"
Content-Type: application/json; charset=UTF-8
OData-Version: 4.0
Content-Length: 612
Date: Tue, 12 Mar 2024 22:38:12 GMT

{"@odata.context":"/redfish/v1/$metadata#EventDestination.EventDestination","@odata.etag":"\"1710283092\"","@odata.id":"/redfish/v1/EventService/Subscriptions","@odata.type":"#EventDestination.v1_6_0.EventDestination","Context":"Subscription_VCMP-1","DeliveryRetryPolicy":"TerminateAfterRetries","Description":"Event Subscription","Destination":"https://vcpme-rch-feocp-redfishalerts.mon.vzwops.com/redfish","EventFormatType":"Event","Id":1,"Name":"Subscription 1","Protocol":"Redfish","Status":{"Health":"OK","HealthRollup":"OK","State":"Enabled"},"SubordinateResources":false,"SubscriptionType":"RedfishEvent"}(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$
```

## verify subscription is there

```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1ucurl -gsk -u XXXXXX:XXXXXX -X GET https://[$IP]/redfish/v1/EventService/Subscriptions | jq .
{
  "@odata.context": "/redfish/v1/$metadata#EventDestinationCollection.EventDestinationCollection",
  "@odata.etag": "\"1710283092\"",
  "@odata.id": "/redfish/v1/EventService/Subscriptions",
  "@odata.type": "#EventDestinationCollection.EventDestinationCollection",
  "Description": "Collection for Event Subscriptions",
  "Members": [
    {
      "@odata.id": "/redfish/v1/EventService/Subscriptions/1"
    }
  ],
  "Members@odata.count": 1,
  "Name": "Event Subscriptions Collection"
}
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[$IP]/redfish/v1/EventService/Subscriptions/1 | jq .
{
  "@odata.context": "/redfish/v1/$metadata#EventDestination.EventDestination",
  "@odata.etag": "\"1710283092\"",
  "@odata.id": "/redfish/v1/EventService/Subscriptions/1",
  "@odata.type": "#EventDestination.v1_6_0.EventDestination",
  "Context": "Subscription_VCMP-1",
  "DeliveryRetryPolicy": "TerminateAfterRetries",
  "Description": "Event Subscription",
  "Destination": "https://vcpme-rch-feocp-redfishalerts.mon.vzwops.com/redfish",
  "EventFormatType": "Event",
  "Id": "1",
  "Name": "Subscription 1",
  "Protocol": "Redfish",
  "Status": {
    "Health": "OK",
    "HealthRollup": "OK",
    "State": "Enabled"
  },
  "SubordinateResources": false,
  "SubscriptionType": "RedfishEvent"
}
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$
```

## submit an event for BMC to send to nortbound VCMP Tools

```sh
export IP="2607:f160:10:9249:ce:40a:0:e015"
curl  -L -w "%{http_code} %{url_effective}\\n" \
-ku XXXXXX:XXXXXX \
-H "Content-Type: application/json" \
-d '{"MessageId" : "EventLog.1.0.ResourceUpdated"}' \
-X POST https://[${IP}]/redfish/v1/EventService/Actions/EventService.SubmitTestEvent
```

Sent 5 alerts

```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ curl  -L -w "%{http_code} %{url_effective}\\n" -ku XXXXXX:XXXXXX -H "Content-Type: application/json" -d '{"MessageId" : "EventLog.1.0.ResourceUpdated"}' -X POST https://[${IP}]/redfish/v1/EventService/Actions/EventService.SubmitTestEvent
^[[A{"@odata.context":"/redfish/v1/$metadata#Task.Task","@odata.id":"/redfish/v1/TaskService/Tasks/18","@odata.type":"#Task.v1_4_2.Task","Description":"Task for EventService SubmitTestEvent Action","Id":"18","Name":"EventService SubmitTestEvent Action","TaskState":"New"}202 https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/EventService/Actions/EventService.SubmitTestEvent
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ curl  -L -w "%{http_code} %{url_effective}\\n" -ku XXXXXX:XXXXXX -H "Content-Type: application/json" -d '{"MessageId" : "EventLog.1.0.ResourceUpdated"}' -X POST https://[${IP}]/redfish/v1/EventService/Actions/EventService.SubmitTestEvent
^[[A{"@odata.context":"/redfish/v1/$metadata#Task.Task","@odata.id":"/redfish/v1/TaskService/Tasks/19","@odata.type":"#Task.v1_4_2.Task","Description":"Task for EventService SubmitTestEvent Action","Id":"19","Name":"EventService SubmitTestEvent Action","TaskState":"New"}202 https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/EventService/Actions/EventService.SubmitTestEvent
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ curl  -L -w "%{http_code} %{url_effective}\\n" -ku XXXXXX:XXXXXX -H "Content-Type: application/json" -d '{"MessageId" : "EventLog.1.0.ResourceUpdated"}' -X POST https://[${IP}]/redfish/v1/EventService/Actions/EventService.SubmitTestEvent
^[[A{"@odata.context":"/redfish/v1/$metadata#Task.Task","@odata.id":"/redfish/v1/TaskService/Tasks/20","@odata.type":"#Task.v1_4_2.Task","Description":"Task for EventService SubmitTestEvent Action","Id":"20","Name":"EventService SubmitTestEvent Action","TaskState":"New"}202 https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/EventService/Actions/EventService.SubmitTestEvent
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ curl  -L -w "%{http_code} %{url_effective}\\n" -ku XXXXXX:XXXXXX -H "Content-Type: application/json" -d '{"MessageId" : "EventLog.1.0.ResourceUpdated"}' -X POST https://[${IP}]/redfish/v1/EventService/Actions/EventService.SubmitTestEvent
{"@odata.context":"/redfish/v1/$metadata#Task.Task","@odata.id":"/redfish/v1/TaskService/Tasks/21","@odata.type":"#Task.v1_4_2.Task","Description":"Task for EventService SubmitTestEvent Action","Id":"21","Name":"EventService SubmitTestEvent Action","TaskState":"New"}202 https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/EventService/Actions/EventService.SubmitTestEvent
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$
```

## Check vcmp tools if alerts made it to them
1 sample alert in vcmp tools

```log
{
  "_index": "vcp-faredge-so-2024.03.11-000076",
  "_id": "RB4MNY4BCHmWGJZFoqlA",
  "_version": 1,
  "_score": 0,
  "_ignored": [
    "message.keyword",
    "event.original.keyword"
  ],
  "_source": {
    "url": {
      "port": 443,
      "path": "/redfish",
      "domain": "vcpme-rch-feocp-redfishalerts.mon.vzwops.com"
    },
    "host": {
      "ip": "10.244.250.38"
    },
    "EventType": "Other",
    "http": {
      "method": "POST",
      "request": {
        "body": {
          "bytes": "608"
        },
        "mime_type": "application/json"
      },
      "version": "HTTP/1.1"
    },
    "type": "events",
    "MessageId": "EventLog.1.0.ResourceUpdated",
    "datacenter": "unknown_datacenter",
    "Events": [
      {
        "MessageId": "EventLog.1.0.ResourceUpdated",
        "OriginOfCondition": {
          "@odata.id": "/redfish/v1/EventService/Actions/EventService.SubmitTestEvent"
        },
        "EventTimestamp": "2024-03-12T23:42:57+00:00",
        "EventType": "Other",
        "Context": "Subscription_VCMP-1",
        "Message": "SubmitTestEvent Action has been triggered",
        "MemberId": "SubmitTestEvent_1710286978",
        "MessageArgs": [
          "test1",
          "test2",
          "test3",
          "test4"
        ],
        "EventId": "SubmitTestEvent_1710286978"
      }
    ],
    "@odata.type": "#Event.v1_4_1.Event",
    "Context": "Subscription_VCMP-1",
    "Events@odata.count": 1,
    "message": "{\"Context\":\"Subscription_VCMP-1\",\"OriginOfCondition\":{\"@odata.id\":\"/redfish/v1/EventService/Actions/EventService.SubmitTestEvent\"},\"MemberId\":\"SubmitTestEvent_1710286978\",\"MessageArgs\":[\"test1\",\"test2\",\"test3\",\"test4\"],\"Message\":\"SubmitTestEvent Action has been triggered\",\"EventTimestamp\":\"2024-03-12T23:42:57+00:00\",\"EventType\":\"Other\",\"EventId\":\"SubmitTestEvent_1710286978\",\"MessageId\":\"EventLog.1.0.ResourceUpdated\"}",
    "@odata.context": "/redfish/v1/$metadata#Event.Event",
    "EventId": "SubmitTestEvent_1710286978",
    "Severity": "%{[Events][0][Severity]}",
    "@timestamp": "2024-03-12T23:43:04.130760Z",
    "EventTimestamp": "2024-03-12T23:42:57+00:00",
    "Name": "Event Array",
    "event": {
      "original": "{\"url\":{\"port\":443,\"path\":\"/redfish\",\"domain\":\"vcpme-rch-feocp-redfishalerts.mon.vzwops.com\"},\"host\":{\"ip\":\"10.244.250.38\"},\"EventType\":\"Other\",\"http\":{\"method\":\"POST\",\"request\":{\"body\":{\"bytes\":\"608\"},\"mime_type\":\"application/json\"},\"version\":\"HTTP/1.1\"},\"type\":\"events\",\"MessageId\":\"EventLog.1.0.ResourceUpdated\",\"datacenter\":\"unknown_datacenter\",\"Events\":[{\"MessageId\":\"EventLog.1.0.ResourceUpdated\",\"OriginOfCondition\":{\"@odata.id\":\"/redfish/v1/EventService/Actions/EventService.SubmitTestEvent\"},\"EventTimestamp\":\"2024-03-12T23:42:57+00:00\",\"EventType\":\"Other\",\"Context\":\"Subscription_VCMP-1\",\"Message\":\"SubmitTestEvent Action has been triggered\",\"MemberId\":\"SubmitTestEvent_1710286978\",\"MessageArgs\":[\"test1\",\"test2\",\"test3\",\"test4\"],\"EventId\":\"SubmitTestEvent_1710286978\"}],\"@odata.type\":\"#Event.v1_4_1.Event\",\"Context\":\"Subscription_VCMP-1\",\"Events@odata.count\":1,\"message\":\"{\\\"Context\\\":\\\"Subscription_VCMP-1\\\",\\\"OriginOfCondition\\\":{\\\"@odata.id\\\":\\\"/redfish/v1/EventService/Actions/EventService.SubmitTestEvent\\\"},\\\"MemberId\\\":\\\"SubmitTestEvent_1710286978\\\",\\\"MessageArgs\\\":[\\\"test1\\\",\\\"test2\\\",\\\"test3\\\",\\\"test4\\\"],\\\"Message\\\":\\\"SubmitTestEvent Action has been triggered\\\",\\\"EventTimestamp\\\":\\\"2024-03-12T23:42:57+00:00\\\",\\\"EventType\\\":\\\"Other\\\",\\\"EventId\\\":\\\"SubmitTestEvent_1710286978\\\",\\\"MessageId\\\":\\\"EventLog.1.0.ResourceUpdated\\\"}\",\"@odata.context\":\"/redfish/v1/$metadata#Event.Event\",\"EventId\":\"SubmitTestEvent_1710286978\",\"Severity\":\"%{[Events][0][Severity]}\",\"@timestamp\":\"2024-03-12T23:43:04.130760Z\",\"EventTimestamp\":\"2024-03-12T23:42:57+00:00\",\"Name\":\"Event Array\",\"event\":{\"original\":\"{\\\"@odata.context\\\":\\\"/redfish/v1/$metadata#Event.Event\\\",\\\"@odata.type\\\":\\\"#Event.v1_4_1.Event\\\",\\\"Context\\\":\\\"Subscription_VCMP-1\\\",\\\"Events\\\":[{\\\"Context\\\":\\\"Subscription_VCMP-1\\\",\\\"EventId\\\":\\\"SubmitTestEvent_1710286978\\\",\\\"EventTimestamp\\\":\\\"2024-03-12T23:42:57+00:00\\\",\\\"EventType\\\":\\\"Other\\\",\\\"MemberId\\\":\\\"SubmitTestEvent_1710286978\\\",\\\"Message\\\":\\\"SubmitTestEvent Action has been triggered\\\",\\\"MessageArgs\\\":[\\\"test1\\\",\\\"test2\\\",\\\"test3\\\",\\\"test4\\\"],\\\"MessageId\\\":\\\"EventLog.1.0.ResourceUpdated\\\",\\\"OriginOfCondition\\\":{\\\"@odata.id\\\":\\\"/redfish/v1/EventService/Actions/EventService.SubmitTestEvent\\\"}}],\\\"Events@odata.count\\\":1,\\\"Id\\\":\\\"12\\\",\\\"Name\\\":\\\"Event Array\\\"}\"},\"user_agent\":{\"original\":\"LuaSocket 3.0-rc1\"},\"@version\":\"1\",\"HOSTIP\":\"%{[headers][x_real_ip]}\",\"Id\":\"12\",\"Message\":\"SubmitTestEvent Action has been triggered\"}"
    },
    "user_agent": {
      "original": "LuaSocket 3.0-rc1"
    },
    "@version": "1",
    "HOSTIP": "%{[headers][x_real_ip]}",
    "Id": "12",
    "Message": "SubmitTestEvent Action has been triggered"
  },
  "fields": {
    "EventType": [
      "Other"
    ],
    "@odata.type": [
      "#Event.v1_4_1.Event"
    ],
    "type": [
      "events"
    ],
    "http.method.keyword": [
      "POST"
    ],
    "Name": [
      "Event Array"
    ],
    "@odata.context.keyword": [
      "/redfish/v1/$metadata#Event.Event"
    ],
    "HOSTIP": [
      "%{[headers][x_real_ip]}"
    ],
    "host.ip.keyword": [
      "10.244.250.38"
    ],
    "Events.Message": [
      "SubmitTestEvent Action has been triggered"
    ],
    "type.keyword": [
      "events"
    ],
    "user_agent.original.keyword": [
      "LuaSocket 3.0-rc1"
    ],
    "EventId": [
      "SubmitTestEvent_1710286978"
    ],
    "Events@odata.count": [
      1
    ],
    "MessageId.keyword": [
      "EventLog.1.0.ResourceUpdated"
    ],
    "datacenter.keyword": [
      "unknown_datacenter"
    ],
    "http.version": [
      "HTTP/1.1"
    ],
    "Events.EventTimestamp": [
      "2024-03-12T23:42:57.000Z"
    ],
    "user_agent.original": [
      "LuaSocket 3.0-rc1"
    ],
    "Events.OriginOfCondition.@odata.id.keyword": [
      "/redfish/v1/EventService/Actions/EventService.SubmitTestEvent"
    ],
    "Id.keyword": [
      "12"
    ],
    "Events.EventId.keyword": [
      "SubmitTestEvent_1710286978"
    ],
    "event.original": [
      "{\"url\":{\"port\":443,\"path\":\"/redfish\",\"domain\":\"vcpme-rch-feocp-redfishalerts.mon.vzwops.com\"},\"host\":{\"ip\":\"10.244.250.38\"},\"EventType\":\"Other\",\"http\":{\"method\":\"POST\",\"request\":{\"body\":{\"bytes\":\"608\"},\"mime_type\":\"application/json\"},\"version\":\"HTTP/1.1\"},\"type\":\"events\",\"MessageId\":\"EventLog.1.0.ResourceUpdated\",\"datacenter\":\"unknown_datacenter\",\"Events\":[{\"MessageId\":\"EventLog.1.0.ResourceUpdated\",\"OriginOfCondition\":{\"@odata.id\":\"/redfish/v1/EventService/Actions/EventService.SubmitTestEvent\"},\"EventTimestamp\":\"2024-03-12T23:42:57+00:00\",\"EventType\":\"Other\",\"Context\":\"Subscription_VCMP-1\",\"Message\":\"SubmitTestEvent Action has been triggered\",\"MemberId\":\"SubmitTestEvent_1710286978\",\"MessageArgs\":[\"test1\",\"test2\",\"test3\",\"test4\"],\"EventId\":\"SubmitTestEvent_1710286978\"}],\"@odata.type\":\"#Event.v1_4_1.Event\",\"Context\":\"Subscription_VCMP-1\",\"Events@odata.count\":1,\"message\":\"{\\\"Context\\\":\\\"Subscription_VCMP-1\\\",\\\"OriginOfCondition\\\":{\\\"@odata.id\\\":\\\"/redfish/v1/EventService/Actions/EventService.SubmitTestEvent\\\"},\\\"MemberId\\\":\\\"SubmitTestEvent_1710286978\\\",\\\"MessageArgs\\\":[\\\"test1\\\",\\\"test2\\\",\\\"test3\\\",\\\"test4\\\"],\\\"Message\\\":\\\"SubmitTestEvent Action has been triggered\\\",\\\"EventTimestamp\\\":\\\"2024-03-12T23:42:57+00:00\\\",\\\"EventType\\\":\\\"Other\\\",\\\"EventId\\\":\\\"SubmitTestEvent_1710286978\\\",\\\"MessageId\\\":\\\"EventLog.1.0.ResourceUpdated\\\"}\",\"@odata.context\":\"/redfish/v1/$metadata#Event.Event\",\"EventId\":\"SubmitTestEvent_1710286978\",\"Severity\":\"%{[Events][0][Severity]}\",\"@timestamp\":\"2024-03-12T23:43:04.130760Z\",\"EventTimestamp\":\"2024-03-12T23:42:57+00:00\",\"Name\":\"Event Array\",\"event\":{\"original\":\"{\\\"@odata.context\\\":\\\"/redfish/v1/$metadata#Event.Event\\\",\\\"@odata.type\\\":\\\"#Event.v1_4_1.Event\\\",\\\"Context\\\":\\\"Subscription_VCMP-1\\\",\\\"Events\\\":[{\\\"Context\\\":\\\"Subscription_VCMP-1\\\",\\\"EventId\\\":\\\"SubmitTestEvent_1710286978\\\",\\\"EventTimestamp\\\":\\\"2024-03-12T23:42:57+00:00\\\",\\\"EventType\\\":\\\"Other\\\",\\\"MemberId\\\":\\\"SubmitTestEvent_1710286978\\\",\\\"Message\\\":\\\"SubmitTestEvent Action has been triggered\\\",\\\"MessageArgs\\\":[\\\"test1\\\",\\\"test2\\\",\\\"test3\\\",\\\"test4\\\"],\\\"MessageId\\\":\\\"EventLog.1.0.ResourceUpdated\\\",\\\"OriginOfCondition\\\":{\\\"@odata.id\\\":\\\"/redfish/v1/EventService/Actions/EventService.SubmitTestEvent\\\"}}],\\\"Events@odata.count\\\":1,\\\"Id\\\":\\\"12\\\",\\\"Name\\\":\\\"Event Array\\\"}\"},\"user_agent\":{\"original\":\"LuaSocket 3.0-rc1\"},\"@version\":\"1\",\"HOSTIP\":\"%{[headers][x_real_ip]}\",\"Id\":\"12\",\"Message\":\"SubmitTestEvent Action has been triggered\"}"
    ],
    "http.request.mime_type": [
      "application/json"
    ],
    "Severity.keyword": [
      "%{[Events][0][Severity]}"
    ],
    "Message.keyword": [
      "SubmitTestEvent Action has been triggered"
    ],
    "Events.MessageId": [
      "EventLog.1.0.ResourceUpdated"
    ],
    "Events.Context": [
      "Subscription_VCMP-1"
    ],
    "Events.MessageArgs.keyword": [
      "test1",
      "test2",
      "test3",
      "test4"
    ],
    "@version.keyword": [
      "1"
    ],
    "@odata.context": [
      "/redfish/v1/$metadata#Event.Event"
    ],
    "EventId.keyword": [
      "SubmitTestEvent_1710286978"
    ],
    "Events.Message.keyword": [
      "SubmitTestEvent Action has been triggered"
    ],
    "Events.EventId": [
      "SubmitTestEvent_1710286978"
    ],
    "Events.MemberId.keyword": [
      "SubmitTestEvent_1710286978"
    ],
    "url.path": [
      "/redfish"
    ],
    "EventTimestamp": [
      "2024-03-12T23:42:57.000Z"
    ],
    "@odata.type.keyword": [
      "#Event.v1_4_1.Event"
    ],
    "http.version.keyword": [
      "HTTP/1.1"
    ],
    "Id": [
      "12"
    ],
    "Events.MessageArgs": [
      "test1",
      "test2",
      "test3",
      "test4"
    ],
    "Message": [
      "SubmitTestEvent Action has been triggered"
    ],
    "http.request.body.bytes": [
      "608"
    ],
    "Events.MessageId.keyword": [
      "EventLog.1.0.ResourceUpdated"
    ],
    "Events.OriginOfCondition.@odata.id": [
      "/redfish/v1/EventService/Actions/EventService.SubmitTestEvent"
    ],
    "Events.EventType.keyword": [
      "Other"
    ],
    "host.ip": [
      "10.244.250.38"
    ],
    "@version": [
      "1"
    ],
    "url.port": [
      443
    ],
    "http.request.mime_type.keyword": [
      "application/json"
    ],
    "http.method": [
      "POST"
    ],
    "Name.keyword": [
      "Event Array"
    ],
    "Events.EventType": [
      "Other"
    ],
    "Context": [
      "Subscription_VCMP-1"
    ],
    "url.path.keyword": [
      "/redfish"
    ],
    "Events.Context.keyword": [
      "Subscription_VCMP-1"
    ],
    "url.domain.keyword": [
      "vcpme-rch-feocp-redfishalerts.mon.vzwops.com"
    ],
    "Severity": [
      "%{[Events][0][Severity]}"
    ],
    "datacenter": [
      "unknown_datacenter"
    ],
    "message": [
      "{\"Context\":\"Subscription_VCMP-1\",\"OriginOfCondition\":{\"@odata.id\":\"/redfish/v1/EventService/Actions/EventService.SubmitTestEvent\"},\"MemberId\":\"SubmitTestEvent_1710286978\",\"MessageArgs\":[\"test1\",\"test2\",\"test3\",\"test4\"],\"Message\":\"SubmitTestEvent Action has been triggered\",\"EventTimestamp\":\"2024-03-12T23:42:57+00:00\",\"EventType\":\"Other\",\"EventId\":\"SubmitTestEvent_1710286978\",\"MessageId\":\"EventLog.1.0.ResourceUpdated\"}"
    ],
    "http.request.body.bytes.keyword": [
      "608"
    ],
    "@timestamp": [
      "2024-03-12T23:43:04.130Z"
    ],
    "url.domain": [
      "vcpme-rch-feocp-redfishalerts.mon.vzwops.com"
    ],
    "HOSTIP.keyword": [
      "%{[headers][x_real_ip]}"
    ],
    "Context.keyword": [
      "Subscription_VCMP-1"
    ],
    "Events.MemberId": [
      "SubmitTestEvent_1710286978"
    ],
    "EventType.keyword": [
      "Other"
    ],
    "MessageId": [
      "EventLog.1.0.ResourceUpdated"
    ]
  },
  "ignored_field_values": {
    "message.keyword": [
      "{\"Context\":\"Subscription_VCMP-1\",\"OriginOfCondition\":{\"@odata.id\":\"/redfish/v1/EventService/Actions/EventService.SubmitTestEvent\"},\"MemberId\":\"SubmitTestEvent_1710286978\",\"MessageArgs\":[\"test1\",\"test2\",\"test3\",\"test4\"],\"Message\":\"SubmitTestEvent Action has been triggered\",\"EventTimestamp\":\"2024-03-12T23:42:57+00:00\",\"EventType\":\"Other\",\"EventId\":\"SubmitTestEvent_1710286978\",\"MessageId\":\"EventLog.1.0.ResourceUpdated\"}"
    ],
    "event.original.keyword": [
      "{\"url\":{\"port\":443,\"path\":\"/redfish\",\"domain\":\"vcpme-rch-feocp-redfishalerts.mon.vzwops.com\"},\"host\":{\"ip\":\"10.244.250.38\"},\"EventType\":\"Other\",\"http\":{\"method\":\"POST\",\"request\":{\"body\":{\"bytes\":\"608\"},\"mime_type\":\"application/json\"},\"version\":\"HTTP/1.1\"},\"type\":\"events\",\"MessageId\":\"EventLog.1.0.ResourceUpdated\",\"datacenter\":\"unknown_datacenter\",\"Events\":[{\"MessageId\":\"EventLog.1.0.ResourceUpdated\",\"OriginOfCondition\":{\"@odata.id\":\"/redfish/v1/EventService/Actions/EventService.SubmitTestEvent\"},\"EventTimestamp\":\"2024-03-12T23:42:57+00:00\",\"EventType\":\"Other\",\"Context\":\"Subscription_VCMP-1\",\"Message\":\"SubmitTestEvent Action has been triggered\",\"MemberId\":\"SubmitTestEvent_1710286978\",\"MessageArgs\":[\"test1\",\"test2\",\"test3\",\"test4\"],\"EventId\":\"SubmitTestEvent_1710286978\"}],\"@odata.type\":\"#Event.v1_4_1.Event\",\"Context\":\"Subscription_VCMP-1\",\"Events@odata.count\":1,\"message\":\"{\\\"Context\\\":\\\"Subscription_VCMP-1\\\",\\\"OriginOfCondition\\\":{\\\"@odata.id\\\":\\\"/redfish/v1/EventService/Actions/EventService.SubmitTestEvent\\\"},\\\"MemberId\\\":\\\"SubmitTestEvent_1710286978\\\",\\\"MessageArgs\\\":[\\\"test1\\\",\\\"test2\\\",\\\"test3\\\",\\\"test4\\\"],\\\"Message\\\":\\\"SubmitTestEvent Action has been triggered\\\",\\\"EventTimestamp\\\":\\\"2024-03-12T23:42:57+00:00\\\",\\\"EventType\\\":\\\"Other\\\",\\\"EventId\\\":\\\"SubmitTestEvent_1710286978\\\",\\\"MessageId\\\":\\\"EventLog.1.0.ResourceUpdated\\\"}\",\"@odata.context\":\"/redfish/v1/$metadata#Event.Event\",\"EventId\":\"SubmitTestEvent_1710286978\",\"Severity\":\"%{[Events][0][Severity]}\",\"@timestamp\":\"2024-03-12T23:43:04.130760Z\",\"EventTimestamp\":\"2024-03-12T23:42:57+00:00\",\"Name\":\"Event Array\",\"event\":{\"original\":\"{\\\"@odata.context\\\":\\\"/redfish/v1/$metadata#Event.Event\\\",\\\"@odata.type\\\":\\\"#Event.v1_4_1.Event\\\",\\\"Context\\\":\\\"Subscription_VCMP-1\\\",\\\"Events\\\":[{\\\"Context\\\":\\\"Subscription_VCMP-1\\\",\\\"EventId\\\":\\\"SubmitTestEvent_1710286978\\\",\\\"EventTimestamp\\\":\\\"2024-03-12T23:42:57+00:00\\\",\\\"EventType\\\":\\\"Other\\\",\\\"MemberId\\\":\\\"SubmitTestEvent_1710286978\\\",\\\"Message\\\":\\\"SubmitTestEvent Action has been triggered\\\",\\\"MessageArgs\\\":[\\\"test1\\\",\\\"test2\\\",\\\"test3\\\",\\\"test4\\\"],\\\"MessageId\\\":\\\"EventLog.1.0.ResourceUpdated\\\",\\\"OriginOfCondition\\\":{\\\"@odata.id\\\":\\\"/redfish/v1/EventService/Actions/EventService.SubmitTestEvent\\\"}}],\\\"Events@odata.count\\\":1,\\\"Id\\\":\\\"12\\\",\\\"Name\\\":\\\"Event Array\\\"}\"},\"user_agent\":{\"original\":\"LuaSocket 3.0-rc1\"},\"@version\":\"1\",\"HOSTIP\":\"%{[headers][x_real_ip]}\",\"Id\":\"12\",\"Message\":\"SubmitTestEvent Action has been triggered\"}"
    ]
  }
}
}
```
### Another alert

```log
{
  "_index": "vcp-faredge-so-2024.03.11-000076",
  "_id": "ex4MNY4BCHmWGJZFsa5P",
  "_version": 1,
  "_score": 0,
  "_ignored": [
    "message.keyword",
    "event.original.keyword"
  ],
  "_source": {
    "url": {
      "port": 443,
      "path": "/redfish",
      "domain": "vcpme-rch-feocp-redfishalerts.mon.vzwops.com"
    },
    "host": {
      "ip": "10.244.4.23"
    },
    "EventType": "Other",
    "http": {
      "method": "POST",
      "request": {
        "body": {
          "bytes": "608"
        },
        "mime_type": "application/json"
      },
      "version": "HTTP/1.1"
    },
    "type": "events",
    "MessageId": "EventLog.1.0.ResourceUpdated",
    "datacenter": "unknown_datacenter",
    "Events": [
      {
        "MessageId": "EventLog.1.0.ResourceUpdated",
        "OriginOfCondition": {
          "@odata.id": "/redfish/v1/EventService/Actions/EventService.SubmitTestEvent"
        },
        "EventTimestamp": "2024-03-12T23:43:01+00:00",
        "EventType": "Other",
        "Context": "Subscription_VCMP-1",
        "Message": "SubmitTestEvent Action has been triggered",
        "MemberId": "SubmitTestEvent_1710286981",
        "MessageArgs": [
          "test1",
          "test2",
          "test3",
          "test4"
        ],
        "EventId": "SubmitTestEvent_1710286981"
      }
    ],
    "@odata.type": "#Event.v1_4_1.Event",
    "Context": "Subscription_VCMP-1",
    "Events@odata.count": 1,
    "message": "{\"Context\":\"Subscription_VCMP-1\",\"OriginOfCondition\":{\"@odata.id\":\"/redfish/v1/EventService/Actions/EventService.SubmitTestEvent\"},\"MemberId\":\"SubmitTestEvent_1710286981\",\"MessageArgs\":[\"test1\",\"test2\",\"test3\",\"test4\"],\"Message\":\"SubmitTestEvent Action has been triggered\",\"EventTimestamp\":\"2024-03-12T23:43:01+00:00\",\"EventType\":\"Other\",\"EventId\":\"SubmitTestEvent_1710286981\",\"MessageId\":\"EventLog.1.0.ResourceUpdated\"}",
    "@odata.context": "/redfish/v1/$metadata#Event.Event",
    "EventId": "SubmitTestEvent_1710286981",
    "Severity": "%{[Events][0][Severity]}",
    "@timestamp": "2024-03-12T23:43:08.059367Z",
    "EventTimestamp": "2024-03-12T23:43:01+00:00",
    "Name": "Event Array",
    "event": {
      "original": "{\"url\":{\"port\":443,\"path\":\"/redfish\",\"domain\":\"vcpme-rch-feocp-redfishalerts.mon.vzwops.com\"},\"host\":{\"ip\":\"10.244.4.23\"},\"EventType\":\"Other\",\"http\":{\"method\":\"POST\",\"request\":{\"body\":{\"bytes\":\"608\"},\"mime_type\":\"application/json\"},\"version\":\"HTTP/1.1\"},\"type\":\"events\",\"MessageId\":\"EventLog.1.0.ResourceUpdated\",\"datacenter\":\"unknown_datacenter\",\"Events\":[{\"MessageId\":\"EventLog.1.0.ResourceUpdated\",\"OriginOfCondition\":{\"@odata.id\":\"/redfish/v1/EventService/Actions/EventService.SubmitTestEvent\"},\"EventTimestamp\":\"2024-03-12T23:43:01+00:00\",\"EventType\":\"Other\",\"Context\":\"Subscription_VCMP-1\",\"Message\":\"SubmitTestEvent Action has been triggered\",\"MemberId\":\"SubmitTestEvent_1710286981\",\"MessageArgs\":[\"test1\",\"test2\",\"test3\",\"test4\"],\"EventId\":\"SubmitTestEvent_1710286981\"}],\"@odata.type\":\"#Event.v1_4_1.Event\",\"Context\":\"Subscription_VCMP-1\",\"Events@odata.count\":1,\"message\":\"{\\\"Context\\\":\\\"Subscription_VCMP-1\\\",\\\"OriginOfCondition\\\":{\\\"@odata.id\\\":\\\"/redfish/v1/EventService/Actions/EventService.SubmitTestEvent\\\"},\\\"MemberId\\\":\\\"SubmitTestEvent_1710286981\\\",\\\"MessageArgs\\\":[\\\"test1\\\",\\\"test2\\\",\\\"test3\\\",\\\"test4\\\"],\\\"Message\\\":\\\"SubmitTestEvent Action has been triggered\\\",\\\"EventTimestamp\\\":\\\"2024-03-12T23:43:01+00:00\\\",\\\"EventType\\\":\\\"Other\\\",\\\"EventId\\\":\\\"SubmitTestEvent_1710286981\\\",\\\"MessageId\\\":\\\"EventLog.1.0.ResourceUpdated\\\"}\",\"@odata.context\":\"/redfish/v1/$metadata#Event.Event\",\"EventId\":\"SubmitTestEvent_1710286981\",\"Severity\":\"%{[Events][0][Severity]}\",\"@timestamp\":\"2024-03-12T23:43:08.059367Z\",\"EventTimestamp\":\"2024-03-12T23:43:01+00:00\",\"Name\":\"Event Array\",\"event\":{\"original\":\"{\\\"@odata.context\\\":\\\"/redfish/v1/$metadata#Event.Event\\\",\\\"@odata.type\\\":\\\"#Event.v1_4_1.Event\\\",\\\"Context\\\":\\\"Subscription_VCMP-1\\\",\\\"Events\\\":[{\\\"Context\\\":\\\"Subscription_VCMP-1\\\",\\\"EventId\\\":\\\"SubmitTestEvent_1710286981\\\",\\\"EventTimestamp\\\":\\\"2024-03-12T23:43:01+00:00\\\",\\\"EventType\\\":\\\"Other\\\",\\\"MemberId\\\":\\\"SubmitTestEvent_1710286981\\\",\\\"Message\\\":\\\"SubmitTestEvent Action has been triggered\\\",\\\"MessageArgs\\\":[\\\"test1\\\",\\\"test2\\\",\\\"test3\\\",\\\"test4\\\"],\\\"MessageId\\\":\\\"EventLog.1.0.ResourceUpdated\\\",\\\"OriginOfCondition\\\":{\\\"@odata.id\\\":\\\"/redfish/v1/EventService/Actions/EventService.SubmitTestEvent\\\"}}],\\\"Events@odata.count\\\":1,\\\"Id\\\":\\\"13\\\",\\\"Name\\\":\\\"Event Array\\\"}\"},\"user_agent\":{\"original\":\"LuaSocket 3.0-rc1\"},\"@version\":\"1\",\"HOSTIP\":\"%{[headers][x_real_ip]}\",\"Id\":\"13\",\"Message\":\"SubmitTestEvent Action has been triggered\"}"
    },
    "user_agent": {
      "original": "LuaSocket 3.0-rc1"
    },
    "@version": "1",
    "HOSTIP": "%{[headers][x_real_ip]}",
    "Id": "13",
    "Message": "SubmitTestEvent Action has been triggered"
  },
  "fields": {
    "EventType": [
      "Other"
    ],
    "@odata.type": [
      "#Event.v1_4_1.Event"
    ],
    "type": [
      "events"
    ],
    "http.method.keyword": [
      "POST"
    ],
    "@odata.context.keyword": [
      "/redfish/v1/$metadata#Event.Event"
    ],
    "Name": [
      "Event Array"
    ],
    "HOSTIP": [
      "%{[headers][x_real_ip]}"
    ],
    "host.ip.keyword": [
      "10.244.4.23"
    ],
    "Events.Message": [
      "SubmitTestEvent Action has been triggered"
    ],
    "type.keyword": [
      "events"
    ],
    "user_agent.original.keyword": [
      "LuaSocket 3.0-rc1"
    ],
    "EventId": [
      "SubmitTestEvent_1710286981"
    ],
    "datacenter.keyword": [
      "unknown_datacenter"
    ],
    "MessageId.keyword": [
      "EventLog.1.0.ResourceUpdated"
    ],
    "Events@odata.count": [
      1
    ],
    "http.version": [
      "HTTP/1.1"
    ],
    "Events.EventTimestamp": [
      "2024-03-12T23:43:01.000Z"
    ],
    "Events.OriginOfCondition.@odata.id.keyword": [
      "/redfish/v1/EventService/Actions/EventService.SubmitTestEvent"
    ],
    "user_agent.original": [
      "LuaSocket 3.0-rc1"
    ],
    "Id.keyword": [
      "13"
    ],
    "Events.EventId.keyword": [
      "SubmitTestEvent_1710286981"
    ],
    "event.original": [
      "{\"url\":{\"port\":443,\"path\":\"/redfish\",\"domain\":\"vcpme-rch-feocp-redfishalerts.mon.vzwops.com\"},\"host\":{\"ip\":\"10.244.4.23\"},\"EventType\":\"Other\",\"http\":{\"method\":\"POST\",\"request\":{\"body\":{\"bytes\":\"608\"},\"mime_type\":\"application/json\"},\"version\":\"HTTP/1.1\"},\"type\":\"events\",\"MessageId\":\"EventLog.1.0.ResourceUpdated\",\"datacenter\":\"unknown_datacenter\",\"Events\":[{\"MessageId\":\"EventLog.1.0.ResourceUpdated\",\"OriginOfCondition\":{\"@odata.id\":\"/redfish/v1/EventService/Actions/EventService.SubmitTestEvent\"},\"EventTimestamp\":\"2024-03-12T23:43:01+00:00\",\"EventType\":\"Other\",\"Context\":\"Subscription_VCMP-1\",\"Message\":\"SubmitTestEvent Action has been triggered\",\"MemberId\":\"SubmitTestEvent_1710286981\",\"MessageArgs\":[\"test1\",\"test2\",\"test3\",\"test4\"],\"EventId\":\"SubmitTestEvent_1710286981\"}],\"@odata.type\":\"#Event.v1_4_1.Event\",\"Context\":\"Subscription_VCMP-1\",\"Events@odata.count\":1,\"message\":\"{\\\"Context\\\":\\\"Subscription_VCMP-1\\\",\\\"OriginOfCondition\\\":{\\\"@odata.id\\\":\\\"/redfish/v1/EventService/Actions/EventService.SubmitTestEvent\\\"},\\\"MemberId\\\":\\\"SubmitTestEvent_1710286981\\\",\\\"MessageArgs\\\":[\\\"test1\\\",\\\"test2\\\",\\\"test3\\\",\\\"test4\\\"],\\\"Message\\\":\\\"SubmitTestEvent Action has been triggered\\\",\\\"EventTimestamp\\\":\\\"2024-03-12T23:43:01+00:00\\\",\\\"EventType\\\":\\\"Other\\\",\\\"EventId\\\":\\\"SubmitTestEvent_1710286981\\\",\\\"MessageId\\\":\\\"EventLog.1.0.ResourceUpdated\\\"}\",\"@odata.context\":\"/redfish/v1/$metadata#Event.Event\",\"EventId\":\"SubmitTestEvent_1710286981\",\"Severity\":\"%{[Events][0][Severity]}\",\"@timestamp\":\"2024-03-12T23:43:08.059367Z\",\"EventTimestamp\":\"2024-03-12T23:43:01+00:00\",\"Name\":\"Event Array\",\"event\":{\"original\":\"{\\\"@odata.context\\\":\\\"/redfish/v1/$metadata#Event.Event\\\",\\\"@odata.type\\\":\\\"#Event.v1_4_1.Event\\\",\\\"Context\\\":\\\"Subscription_VCMP-1\\\",\\\"Events\\\":[{\\\"Context\\\":\\\"Subscription_VCMP-1\\\",\\\"EventId\\\":\\\"SubmitTestEvent_1710286981\\\",\\\"EventTimestamp\\\":\\\"2024-03-12T23:43:01+00:00\\\",\\\"EventType\\\":\\\"Other\\\",\\\"MemberId\\\":\\\"SubmitTestEvent_1710286981\\\",\\\"Message\\\":\\\"SubmitTestEvent Action has been triggered\\\",\\\"MessageArgs\\\":[\\\"test1\\\",\\\"test2\\\",\\\"test3\\\",\\\"test4\\\"],\\\"MessageId\\\":\\\"EventLog.1.0.ResourceUpdated\\\",\\\"OriginOfCondition\\\":{\\\"@odata.id\\\":\\\"/redfish/v1/EventService/Actions/EventService.SubmitTestEvent\\\"}}],\\\"Events@odata.count\\\":1,\\\"Id\\\":\\\"13\\\",\\\"Name\\\":\\\"Event Array\\\"}\"},\"user_agent\":{\"original\":\"LuaSocket 3.0-rc1\"},\"@version\":\"1\",\"HOSTIP\":\"%{[headers][x_real_ip]}\",\"Id\":\"13\",\"Message\":\"SubmitTestEvent Action has been triggered\"}"
    ],
    "Severity.keyword": [
      "%{[Events][0][Severity]}"
    ],
    "http.request.mime_type": [
      "application/json"
    ],
    "Message.keyword": [
      "SubmitTestEvent Action has been triggered"
    ],
    "Events.MessageId": [
      "EventLog.1.0.ResourceUpdated"
    ],
    "Events.Context": [
      "Subscription_VCMP-1"
    ],
    "Events.MessageArgs.keyword": [
      "test1",
      "test2",
      "test3",
      "test4"
    ],
    "@version.keyword": [
      "1"
    ],
    "@odata.context": [
      "/redfish/v1/$metadata#Event.Event"
    ],
    "EventId.keyword": [
      "SubmitTestEvent_1710286981"
    ],
    "Events.Message.keyword": [
      "SubmitTestEvent Action has been triggered"
    ],
    "Events.EventId": [
      "SubmitTestEvent_1710286981"
    ],
    "Events.MemberId.keyword": [
      "SubmitTestEvent_1710286981"
    ],
    "url.path": [
      "/redfish"
    ],
    "EventTimestamp": [
      "2024-03-12T23:43:01.000Z"
    ],
    "@odata.type.keyword": [
      "#Event.v1_4_1.Event"
    ],
    "Id": [
      "13"
    ],
    "http.version.keyword": [
      "HTTP/1.1"
    ],
    "Events.MessageArgs": [
      "test1",
      "test2",
      "test3",
      "test4"
    ],
    "http.request.body.bytes": [
      "608"
    ],
    "Message": [
      "SubmitTestEvent Action has been triggered"
    ],
    "Events.MessageId.keyword": [
      "EventLog.1.0.ResourceUpdated"
    ],
    "Events.OriginOfCondition.@odata.id": [
      "/redfish/v1/EventService/Actions/EventService.SubmitTestEvent"
    ],
    "Events.EventType.keyword": [
      "Other"
    ],
    "host.ip": [
      "10.244.4.23"
    ],
    "url.port": [
      443
    ],
    "@version": [
      "1"
    ],
    "http.request.mime_type.keyword": [
      "application/json"
    ],
    "http.method": [
      "POST"
    ],
    "Name.keyword": [
      "Event Array"
    ],
    "Events.EventType": [
      "Other"
    ],
    "Context": [
      "Subscription_VCMP-1"
    ],
    "url.path.keyword": [
      "/redfish"
    ],
    "Events.Context.keyword": [
      "Subscription_VCMP-1"
    ],
    "url.domain.keyword": [
      "vcpme-rch-feocp-redfishalerts.mon.vzwops.com"
    ],
    "datacenter": [
      "unknown_datacenter"
    ],
    "Severity": [
      "%{[Events][0][Severity]}"
    ],
    "message": [
      "{\"Context\":\"Subscription_VCMP-1\",\"OriginOfCondition\":{\"@odata.id\":\"/redfish/v1/EventService/Actions/EventService.SubmitTestEvent\"},\"MemberId\":\"SubmitTestEvent_1710286981\",\"MessageArgs\":[\"test1\",\"test2\",\"test3\",\"test4\"],\"Message\":\"SubmitTestEvent Action has been triggered\",\"EventTimestamp\":\"2024-03-12T23:43:01+00:00\",\"EventType\":\"Other\",\"EventId\":\"SubmitTestEvent_1710286981\",\"MessageId\":\"EventLog.1.0.ResourceUpdated\"}"
    ],
    "http.request.body.bytes.keyword": [
      "608"
    ],
    "@timestamp": [
      "2024-03-12T23:43:08.059Z"
    ],
    "HOSTIP.keyword": [
      "%{[headers][x_real_ip]}"
    ],
    "url.domain": [
      "vcpme-rch-feocp-redfishalerts.mon.vzwops.com"
    ],
    "Context.keyword": [
      "Subscription_VCMP-1"
    ],
    "Events.MemberId": [
      "SubmitTestEvent_1710286981"
    ],
    "MessageId": [
      "EventLog.1.0.ResourceUpdated"
    ],
    "EventType.keyword": [
      "Other"
    ]
  },
  "ignored_field_values": {
    "message.keyword": [
      "{\"Context\":\"Subscription_VCMP-1\",\"OriginOfCondition\":{\"@odata.id\":\"/redfish/v1/EventService/Actions/EventService.SubmitTestEvent\"},\"MemberId\":\"SubmitTestEvent_1710286981\",\"MessageArgs\":[\"test1\",\"test2\",\"test3\",\"test4\"],\"Message\":\"SubmitTestEvent Action has been triggered\",\"EventTimestamp\":\"2024-03-12T23:43:01+00:00\",\"EventType\":\"Other\",\"EventId\":\"SubmitTestEvent_1710286981\",\"MessageId\":\"EventLog.1.0.ResourceUpdated\"}"
    ],
    "event.original.keyword": [
      "{\"url\":{\"port\":443,\"path\":\"/redfish\",\"domain\":\"vcpme-rch-feocp-redfishalerts.mon.vzwops.com\"},\"host\":{\"ip\":\"10.244.4.23\"},\"EventType\":\"Other\",\"http\":{\"method\":\"POST\",\"request\":{\"body\":{\"bytes\":\"608\"},\"mime_type\":\"application/json\"},\"version\":\"HTTP/1.1\"},\"type\":\"events\",\"MessageId\":\"EventLog.1.0.ResourceUpdated\",\"datacenter\":\"unknown_datacenter\",\"Events\":[{\"MessageId\":\"EventLog.1.0.ResourceUpdated\",\"OriginOfCondition\":{\"@odata.id\":\"/redfish/v1/EventService/Actions/EventService.SubmitTestEvent\"},\"EventTimestamp\":\"2024-03-12T23:43:01+00:00\",\"EventType\":\"Other\",\"Context\":\"Subscription_VCMP-1\",\"Message\":\"SubmitTestEvent Action has been triggered\",\"MemberId\":\"SubmitTestEvent_1710286981\",\"MessageArgs\":[\"test1\",\"test2\",\"test3\",\"test4\"],\"EventId\":\"SubmitTestEvent_1710286981\"}],\"@odata.type\":\"#Event.v1_4_1.Event\",\"Context\":\"Subscription_VCMP-1\",\"Events@odata.count\":1,\"message\":\"{\\\"Context\\\":\\\"Subscription_VCMP-1\\\",\\\"OriginOfCondition\\\":{\\\"@odata.id\\\":\\\"/redfish/v1/EventService/Actions/EventService.SubmitTestEvent\\\"},\\\"MemberId\\\":\\\"SubmitTestEvent_1710286981\\\",\\\"MessageArgs\\\":[\\\"test1\\\",\\\"test2\\\",\\\"test3\\\",\\\"test4\\\"],\\\"Message\\\":\\\"SubmitTestEvent Action has been triggered\\\",\\\"EventTimestamp\\\":\\\"2024-03-12T23:43:01+00:00\\\",\\\"EventType\\\":\\\"Other\\\",\\\"EventId\\\":\\\"SubmitTestEvent_1710286981\\\",\\\"MessageId\\\":\\\"EventLog.1.0.ResourceUpdated\\\"}\",\"@odata.context\":\"/redfish/v1/$metadata#Event.Event\",\"EventId\":\"SubmitTestEvent_1710286981\",\"Severity\":\"%{[Events][0][Severity]}\",\"@timestamp\":\"2024-03-12T23:43:08.059367Z\",\"EventTimestamp\":\"2024-03-12T23:43:01+00:00\",\"Name\":\"Event Array\",\"event\":{\"original\":\"{\\\"@odata.context\\\":\\\"/redfish/v1/$metadata#Event.Event\\\",\\\"@odata.type\\\":\\\"#Event.v1_4_1.Event\\\",\\\"Context\\\":\\\"Subscription_VCMP-1\\\",\\\"Events\\\":[{\\\"Context\\\":\\\"Subscription_VCMP-1\\\",\\\"EventId\\\":\\\"SubmitTestEvent_1710286981\\\",\\\"EventTimestamp\\\":\\\"2024-03-12T23:43:01+00:00\\\",\\\"EventType\\\":\\\"Other\\\",\\\"MemberId\\\":\\\"SubmitTestEvent_1710286981\\\",\\\"Message\\\":\\\"SubmitTestEvent Action has been triggered\\\",\\\"MessageArgs\\\":[\\\"test1\\\",\\\"test2\\\",\\\"test3\\\",\\\"test4\\\"],\\\"MessageId\\\":\\\"EventLog.1.0.ResourceUpdated\\\",\\\"OriginOfCondition\\\":{\\\"@odata.id\\\":\\\"/redfish/v1/EventService/Actions/EventService.SubmitTestEvent\\\"}}],\\\"Events@odata.count\\\":1,\\\"Id\\\":\\\"13\\\",\\\"Name\\\":\\\"Event Array\\\"}\"},\"user_agent\":{\"original\":\"LuaSocket 3.0-rc1\"},\"@version\":\"1\",\"HOSTIP\":\"%{[headers][x_real_ip]}\",\"Id\":\"13\",\"Message\":\"SubmitTestEvent Action has been triggered\"}"
    ]
  }
}
```
### alerts are coming into elastic with VCMP tools, I have added screen shots and will upload to test case ### for evidence... queries with new vcmp tools after the rebulid is not working yet.


## Redfish Event URL has been set and is good

## MEAKV-654 
## Redfish add user, change password, then delete user

```log
( (ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ ansible-playbook --vault-password-file ./vault_pass.txt -i inventry-fe/rchltxfe-1.yml -e attributes_file=vars/proteus_redfish_attributes.yml -e target="welktxef-931887-rz-le2pts6-021" --tags user  ZT_Redfish_tests.yml

PLAY [welktxef-931887-rz-le2pts6-021] ***********************************************************************************************************

TASK [redfish/users : Generate request body] ****************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [redfish/users : Add user] *****************************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [redfish/users : debug] ********************************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "response": {
        "access_control_allow_credentials": "true",
        "access_control_allow_headers": "X-Auth-Token",
        "access_control_allow_origin": "*",
        "access_control_expose_headers": "X-Auth-Token",
        "allow": "GET, POST",
        "cache_control": "no-cache, must-revalidate",
        "changed": false,
        "connection": "close",
        "content_length": "575",
        "content_type": "application/json; charset=UTF-8",
        "cookies": {},
        "cookies_string": "",
        "date": "Tue, 12 Mar 2024 23:56:27 GMT",
        "elapsed": 5,
        "etag": "\"1710287784\"",
        "failed": false,
        "json": {
            "@odata.context": "/redfish/v1/$metadata#ManagerAccount.ManagerAccount",
            "@odata.etag": "\"1710287784\"",
            "@odata.id": "/redfish/v1/AccountService/Accounts",
            "@odata.type": "#ManagerAccount.v1_4_0.ManagerAccount",
            "AccountTypes": [
                "Redfish"
            ],
            "Certificates": {
                "@odata.id": "/redfish/v1/AccountService/Accounts/5/Certificates"
            },
            "Description": "Ansible user",
            "Enabled": true,
            "Id": "5",
            "Links": {
                "Role": {
                    "@odata.id": "/redfish/v1/AccountService/Roles/XXXXXX"
                }
            },
            "Locked": false,
            "Name": "testuser",
            "Password": null,
            "PasswordChangeRequired": true,
            "RoleId": "XXXXXX",
            "UserName": "testuser"
        },
        "link": "<http://redfish.dmtf.org/schemas/v1/ManagerAccount.v1_4_0.json>; rel=describedby, </redfish/v1/AccountService/Accounts>; path=",
        "location": "https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/AccountService/Accounts/5",
        "msg": "OK (575 bytes)",
        "odata_version": "4.0",
        "redirected": false,
        "server": "AMI MegaRAC Redfish Service",
        "status": 201,
        "url": "https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/AccountService/Accounts"
    }
}

TASK [redfish/users : Storing location of new user] *********************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [redfish/users : sleep if needed] **********************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [redfish/users : get new user with its own credentials] ************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [redfish/users : debug] ********************************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "response": {
        "access_control_allow_credentials": "true",
        "access_control_allow_headers": "X-Auth-Token",
        "access_control_allow_origin": "*",
        "access_control_expose_headers": "X-Auth-Token",
        "allow": "GET, PATCH, DELETE",
        "cache_control": "no-cache, must-revalidate",
        "changed": false,
        "connection": "close",
        "content_length": "577",
        "content_type": "application/json; charset=UTF-8",
        "cookies": {},
        "cookies_string": "",
        "date": "Tue, 12 Mar 2024 23:56:58 GMT",
        "elapsed": 0,
        "etag": "\"1710287784\"",
        "failed": false,
        "json": {
            "@odata.context": "/redfish/v1/$metadata#ManagerAccount.ManagerAccount",
            "@odata.etag": "\"1710287784\"",
            "@odata.id": "/redfish/v1/AccountService/Accounts/5",
            "@odata.type": "#ManagerAccount.v1_4_0.ManagerAccount",
            "AccountTypes": [
                "Redfish"
            ],
            "Certificates": {
                "@odata.id": "/redfish/v1/AccountService/Accounts/5/Certificates"
            },
            "Description": "Ansible user",
            "Enabled": true,
            "Id": "5",
            "Links": {
                "Role": {
                    "@odata.id": "/redfish/v1/AccountService/Roles/XXXXXX"
                }
            },
            "Locked": false,
            "Name": "testuser",
            "Password": null,
            "PasswordChangeRequired": true,
            "RoleId": "XXXXXX",
            "UserName": "testuser"
        },
        "link": "<http://redfish.dmtf.org/schemas/v1/ManagerAccount.v1_4_0.json>; rel=describedby, </redfish/v1/AccountService/Roles/XXXXXX>; path=/Links/Role, </redfish/v1/AccountService/Accounts/5/Certificates>; path=/Certificates",
        "msg": "OK (577 bytes)",
        "odata_version": "4.0",
        "redirected": false,
        "server": "AMI MegaRAC Redfish Service",
        "status": 200,
        "url": "https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/AccountService/Accounts/5"
    }
}

TASK [redfish/users : Generate request body] ****************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [redfish/users : Change password] **********************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [redfish/users : debug] ********************************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "response": {
        "allow": "GET, PATCH, DELETE",
        "changed": false,
        "connection": "close",
        "cookies": {},
        "cookies_string": "",
        "date": "Tue, 12 Mar 2024 23:57:06 GMT",
        "elapsed": 7,
        "failed": false,
        "msg": "OK (unknown bytes)",
        "redirected": false,
        "server": "AMI MegaRAC Redfish Service",
        "status": 204,
        "url": "https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/AccountService/Accounts/5"
    }
}

TASK [redfish/users : sleep if needed] **********************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [redfish/users : Get new user with its own (updated) credentials] **************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [redfish/users : debug] ********************************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "response": {
        "access_control_allow_credentials": "true",
        "access_control_allow_headers": "X-Auth-Token",
        "access_control_allow_origin": "*",
        "access_control_expose_headers": "X-Auth-Token",
        "allow": "GET, PATCH, DELETE",
        "cache_control": "no-cache, must-revalidate",
        "changed": false,
        "connection": "close",
        "content_length": "578",
        "content_type": "application/json; charset=UTF-8",
        "cookies": {},
        "cookies_string": "",
        "date": "Tue, 12 Mar 2024 23:57:37 GMT",
        "elapsed": 0,
        "etag": "\"1710287820\"",
        "failed": false,
        "json": {
            "@odata.context": "/redfish/v1/$metadata#ManagerAccount.ManagerAccount",
            "@odata.etag": "\"1710287820\"",
            "@odata.id": "/redfish/v1/AccountService/Accounts/5",
            "@odata.type": "#ManagerAccount.v1_4_0.ManagerAccount",
            "AccountTypes": [
                "Redfish"
            ],
            "Certificates": {
                "@odata.id": "/redfish/v1/AccountService/Accounts/5/Certificates"
            },
            "Description": "Ansible user",
            "Enabled": true,
            "Id": "5",
            "Links": {
                "Role": {
                    "@odata.id": "/redfish/v1/AccountService/Roles/XXXXXX"
                }
            },
            "Locked": false,
            "Name": "testuser",
            "Password": null,
            "PasswordChangeRequired": false,
            "RoleId": "XXXXXX",
            "UserName": "testuser"
        },
        "link": "<http://redfish.dmtf.org/schemas/v1/ManagerAccount.v1_4_0.json>; rel=describedby, </redfish/v1/AccountService/Roles/XXXXXX>; path=/Links/Role, </redfish/v1/AccountService/Accounts/5/Certificates>; path=/Certificates",
        "msg": "OK (578 bytes)",
        "odata_version": "4.0",
        "redirected": false,
        "server": "AMI MegaRAC Redfish Service",
        "status": 200,
        "url": "https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/AccountService/Accounts/5"
    }
}

TASK [redfish/users : Deleting user] ************************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [redfish/users : debug] ********************************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "response": {
        "allow": "GET, PATCH, DELETE",
        "changed": false,
        "connection": "close",
        "cookies": {},
        "cookies_string": "",
        "date": "Tue, 12 Mar 2024 23:57:41 GMT",
        "elapsed": 3,
        "failed": false,
        "msg": "OK (unknown bytes)",
        "redirected": false,
        "server": "AMI MegaRAC Redfish Service",
        "status": 204,
        "url": "https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/AccountService/Accounts/5"
    }
}

TASK [redfish/users : sleep if needed] **********************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [redfish/users : Check if user is gone] ****************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [redfish/users : debug] ********************************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "response": {
        "changed": false,
        "connection": "close",
        "content_length": "512",
        "content_type": "application/json; charset=UTF-8",
        "date": "Tue, 12 Mar 2024 23:58:12 GMT",
        "elapsed": 0,
        "failed": false,
        "json": {
            "error": {
                "@Message.ExtendedInfo": [
                    {
                        "@odata.type": "#Message.v1_0_8.Message",
                        "Message": "The resource at the URI /redfish/v1/AccountService/Accounts/5 was not found.",
                        "MessageArgs": [
                            "/redfish/v1/AccountService/Accounts/5"
                        ],
                        "MessageId": "Base.1.5.ResourceMissingAtURI",
                        "Resolution": "Place a valid resource at the URI or correct the URI and resubmit the request.",
                        "Severity": "Critical"
                    }
                ],
                "code": "Base.1.5.ResourceMissingAtURI",
                "message": "The resource at the URI /redfish/v1/AccountService/Accounts/5 was not found."
            }
        },
        "msg": "HTTP Error 404: Not Found",
        "odata_version": "4.0",
        "redirected": false,
        "server": "AMI MegaRAC Redfish Service",
        "status": 404,
        "url": "https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/AccountService/Accounts/5"
    }
}

PLAY RECAP **************************************************************************************************************************************
welktxef-931887-rz-le2pts6-021 : ok=18   changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0

(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$
```
## Passed test, all worked as expected


