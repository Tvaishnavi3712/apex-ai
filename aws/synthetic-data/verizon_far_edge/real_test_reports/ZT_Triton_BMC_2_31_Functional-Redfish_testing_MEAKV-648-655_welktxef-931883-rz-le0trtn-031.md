# ZT Proteus .46 BMC firmware validation
# ZT Proteus BIOS .23
# Redfish Functional Testing MEAKV-648-MEAKV-654 
# 1/16/24 James Patchett

## Target Controller rchltxib-c000000-003
Controller-0 iLO 2607:f160:a:d02e:cd:fe0::8006 
Controller-1 iLO 2607:f160:a:d02e:cd:fe0::8007
Worker-0 iLO 2607:f160:a:d02e:cd:fe0::8008 
OAM 2607:f160:0:3049:cd:290:0:10

## Target Subcloud welktxef-d931856-008
OAM: 2607:f160:10:80b1:ce:40a:0:f408
BMC: 2607:f160:10:80b1:ce:40a:0:e008

ipmitool -I lanplus -U XXXXXX -P XXXXXX -H 2607:f160:10:80b1:ce:40a:0:e008 sol activate

## Subcloud welktxef-d931856-008

## MEAKV-648
## Check version of BIOS 
```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ IP=2607:f160:10:80b1:ce:40a:0:e008
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[${IP}]/redfish/v1/UpdateService/FirmwareInventory/BIOS | jq .
{
  "@odata.context": "/redfish/v1/$metadata#SoftwareInventory.SoftwareInventory",
  "@odata.etag": "\"1704933378\"",
  "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/BIOS",
  "@odata.type": "#SoftwareInventory.v1_2_3.SoftwareInventory",
  "Id": "BIOS",
  "Name": "BIOS",
  "Updateable": true,
  "Version": "0.23"
}
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 ~]$

```

## Check version of BMC

```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[${IP}]/redfish/v1/UpdateService/FirmwareInventory/BMC | jq .
{
  "@odata.context": "/redfish/v1/$metadata#SoftwareInventory.SoftwareInventory",
  "@odata.etag": "\"1704933378\"",
  "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/BMC",
  "@odata.type": "#SoftwareInventory.v1_2_3.SoftwareInventory",
  "Id": "BMC",
  "Name": "BMC",
  "Updateable": true,
  "Version": "0.46.00"
}
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 ~]$
```

## MEAKV-649
## set hostname with ZT_Redfish_tests.yml

```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$  ansible-playbook --vault-password-file /tmp/vault-pass -i inventory-fe/rchltxfe-1.yml -e attributes_file=vars/proteus_redfish_attributes.yml -e target="welktxef-931856-rz-le2pts6-008" --tags hostname ZT_Redfish_tests.yml

PLAY [welktxef-931856-rz-le2pts6-008] **********************************************************************************************************************

TASK [redfish/attributes : what we're setting] *************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "set_attr_item": {
        "attribute": "HostName",
        "new_value": "newhostname2",
        "path": "/redfish/v1/Systems/Self"
    }
}

TASK [redfish/attributes : Setting HostName] ***************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [redfish/attributes : debug] **************************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
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
        "date": "Tue, 16 Jan 2024 21:56:05 GMT",
        "elapsed": 4,
        "etag": "\"1705442165\"",
        "failed": false,
        "msg": "OK (unknown bytes)",
        "odata_version": "4.0",
        "redirected": false,
        "server": "AMI MegaRAC Redfish Service",
        "status": 204,
        "url": "https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/Systems/Self"
    }
}

TASK [redfish/attributes : set_fact] ***********************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008]

TASK [redfish/attributes : sleep if needed] ****************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]
included: /home/XXXXXX/richardson/playbooks/vcp-fe-ib-automation/roles/redfish/attributes/tasks/check_attribute.yml for welktxef-931856-rz-le2pts6-008

TASK [redfish/attributes : what is currently verified] *****************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "msg": "Sending GET to /redfish/v1/Systems/Self and query the returned json for HostName. Value shall be newhostname2"
}

TASK [redfish/attributes : Checking HostName at /redfish/v1/Systems/Self] **********************************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [redfish/attributes : what we're setting] *************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "set_attr_item": {
        "attribute": "HostName",
        "new_value": "welktxef-931856-rz-le2pts6-008",
        "path": "/redfish/v1/Systems/Self"
    }
}

TASK [redfish/attributes : Setting HostName] ***************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [redfish/attributes : debug] **************************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
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
        "date": "Tue, 16 Jan 2024 21:57:18 GMT",
        "elapsed": 7,
        "etag": "\"1705442238\"",
        "failed": false,
        "msg": "OK (unknown bytes)",
        "odata_version": "4.0",
        "redirected": false,
        "server": "AMI MegaRAC Redfish Service",
        "status": 204,
        "url": "https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/Systems/Self"
    }
}

TASK [redfish/attributes : set_fact] ***********************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008]
included: /home/XXXXXX/richardson/playbooks/vcp-fe-ib-automation/roles/redfish/attributes/tasks/check_attribute.yml for welktxef-931856-rz-le2pts6-008

TASK [redfish/attributes : what is currently verified] *****************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "msg": "Sending GET to /redfish/v1/Systems/Self and query the returned json for HostName. Value shall be welktxef-931856-rz-le2pts6-008"
}

TASK [redfish/attributes : Checking HostName at /redfish/v1/Systems/Self] **********************************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

PLAY RECAP *************************************************************************************************************************************************
welktxef-931856-rz-le2pts6-008 : ok=15   changed=0    unreachable=0    failed=0    skipped=5    rescued=0    ignored=0

(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$
```

## MEAKV-650
## set static DNS servers via api

## check Current

```log
[XXXXXX@vcpe-jumpserver wra-testing]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Managers/Self/EthernetInterfaces/(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/Managers/Self/EthernetInterfaces/eth0 | jq .StaticNameServers
[
  "2607:f160:10:4409:ce:103:0:5",
  "2607:f160:10:4409:ce:103:0:6",
  "::"
]
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$

```

## Set to DNS servers to different address to confirm it changes... with ZT_Redfish_tests.yml
## changed IPs in GUI of BMC... 9 and 10 in  now
```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/Managers/Self/EthernetInterfaces/eth0 | jq .StaticNameServers
[
  "2607:f160:10:4409:ce:103:0:9",
  "2607:f160:10:4409:ce:103:0:10",
  "::"
]
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$  ansible-playbook --vault-password-file /tmp/vault-pass -i inventory-fe/rchltxfe-1.yml -e attributes_file=vars/proteus_redfish_attributes.yml -e target="welktxef-931856-rz-le2pts6-008" --tags dns ZT_Redfish_tests.yml

PLAY [welktxef-931856-rz-le2pts6-008] **********************************************************************************************************************
included: /home/XXXXXX/richardson/playbooks/vcp-fe-ib-automation/roles/redfish/attributes/tasks/set_attribute.yml for welktxef-931856-rz-le2pts6-008 => (item={'path': '/redfish/v1/Managers/Self/EthernetInterfaces/eth0', 'attribute': 'StaticNameServers', 'new_value': ['2607:f160:10:4409:ce:103:0:5', '2607:f160:10:4409:ce:103:0:6'], 'expected_response': 202, 'expected_value': ['2607:f160:10:4409:ce:103:0:5', '2607:f160:10:4409:ce:103:0:6', '::']})

TASK [redfish/attributes : what we're setting] *************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
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

TASK [redfish/attributes : Setting StaticNameServers] ******************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [redfish/attributes : debug] **************************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "response": {
        "access_control_allow_credentials": "true",
        "access_control_allow_headers": "X-Auth-Token",
        "access_control_allow_origin": "*",
        "access_control_expose_headers": "X-Auth-Token",
        "allow": "GET, PATCH",
        "cache_control": "no-cache, must-revalidate",
        "changed": false,
        "connection": "close",
        "content_length": "243",
        "content_type": "application/json; charset=UTF-8",
        "cookies": {},
        "cookies_string": "",
        "date": "Tue, 16 Jan 2024 22:01:30 GMT",
        "elapsed": 3,
        "etag": "\"1705442485\"",
        "failed": false,
        "json": {
            "@odata.context": "/redfish/v1/$metadata#Task.Task",
            "@odata.id": "/redfish/v1/TaskService/Tasks/8",
            "@odata.type": "#Task.v1_4_2.Task",
            "Description": "Task for EthernetInterface Action",
            "Id": "8",
            "Name": "EthernetInterface Action",
            "TaskState": "New"
        },
        "link": "<http://redfish.dmtf.org/schemas/v1/EthernetInterface.v1_5_1.json>; rel=describedby, <http://redfish.dmtf.org/schemas/v1/Task.v1_4_2.json>, </redfish/v1/TaskService/Tasks/8>; path=",
        "location": "https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/TaskService/Tasks/8",
        "msg": "OK (243 bytes)",
        "odata_version": "4.0",
        "prefer": "respond-async; wait=1",
        "redirected": false,
        "server": "AMI MegaRAC Redfish Service",
        "status": 202,
        "url": "https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/Managers/Self/EthernetInterfaces/eth0"
    }
}

TASK [redfish/attributes : set_fact] ***********************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008]

TASK [redfish/attributes : sleep if needed] ****************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]
included: /home/XXXXXX/richardson/playbooks/vcp-fe-ib-automation/roles/redfish/attributes/tasks/check_attribute.yml for welktxef-931856-rz-le2pts6-008

TASK [redfish/attributes : what is currently verified] *****************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "msg": "Sending GET to /redfish/v1/Managers/Self/EthernetInterfaces/eth0 and query the returned json for StaticNameServers. Value shall be ['2607:f160:10:4409:ce:103:0:5', '2607:f160:10:4409:ce:103:0:6', '::']"
}

TASK [redfish/attributes : Checking StaticNameServers at /redfish/v1/Managers/Self/EthernetInterfaces/eth0] ************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

PLAY RECAP *************************************************************************************************************************************************
welktxef-931856-rz-le2pts6-008 : ok=9    changed=0    unreachable=0    failed=0    skipped=2    rescued=0    ignored=0

(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$

```

## Check to see if dns was updated 

```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/Managers/Self/EthernetInterfaces/eth0 | jq .StaticNameServers
[
  "2607:f160:10:4409:ce:103:0:5",
  "2607:f160:10:4409:ce:103:0:6",
  "::"
]
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$
```

## DNS looks good, moving to next test.

## MEAKV-651
## Set NTP servers

## check exiting values

```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/Managers/Self/NetworkProtocol | jq .NTP
{
  "NTPServers": [
    "2607:f160:10:9200::a",
    "2607:f160:10:9200::b"
  ],
  "Port": 123,
  "ProtocolEnabled": true
}
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$
```

## Changing values in BMC UI

## checking values again with wrong server addresses

```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/Managers/Self/NetworkProtocol | jq .NTP
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
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$  ansible-playbook --vault-password-file /tmp/vault-pass -i inventory-fe/rchltxfe-1.yml -e attributes_file=vars/proteus_redfish_attributes.yml -e target="welktxef-931856-rz-le2pts6-008" --tags ntp ZT_Redfish_tests.yml

PLAY [welktxef-931856-rz-le2pts6-008] **********************************************************************************************************************

TASK [redfish/attributes : what we're setting] *************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
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

TASK [redfish/attributes : Setting NTP] ********************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [redfish/attributes : debug] **************************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
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
        "date": "Tue, 16 Jan 2024 22:29:26 GMT",
        "elapsed": 3,
        "etag": "\"1705442568\"",
        "failed": false,
        "msg": "OK (unknown bytes)",
        "odata_version": "4.0",
        "redirected": false,
        "server": "AMI MegaRAC Redfish Service",
        "status": 204,
        "url": "https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/Managers/Self/NetworkProtocol"
    }
}

TASK [redfish/attributes : set_fact] ***********************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008]

TASK [redfish/attributes : sleep if needed] ****************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]
included: /home/XXXXXX/richardson/playbooks/vcp-fe-ib-automation/roles/redfish/attributes/tasks/check_attribute.yml for welktxef-931856-rz-le2pts6-008

TASK [redfish/attributes : what is currently verified] *****************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "msg": "Sending GET to /redfish/v1/Managers/Self/NetworkProtocol and query the returned json for NTP.NTPServers. Value shall be ['2607:f160:10:9200::a', '2607:f160:10:8200::a']"
}

TASK [redfish/attributes : Checking NTP.NTPServers at /redfish/v1/Managers/Self/NetworkProtocol] ***********************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

PLAY RECAP *************************************************************************************************************************************************
welktxef-931856-rz-le2pts6-008 : ok=8    changed=0    unreachable=0    failed=0    skipped=2    rescued=0    ignored=0

(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$
```

## verify settings took with a query to redfish db

```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/Managers/Self/NetworkProtocol | jq .NTP
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
## check to see if an subscription exists

```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/EventService/Subscriptions | jq .
{
  "@odata.context": "/redfish/v1/$metadata#EventDestinationCollection.EventDestinationCollection",
  "@odata.etag": "\"1705444489\"",
  "@odata.id": "/redfish/v1/EventService/Subscriptions",
  "@odata.type": "#EventDestinationCollection.EventDestinationCollection",
  "Description": "Collection for Event Subscriptions",
  "Members": [],
  "Members@odata.count": 0,
  "Name": "Event Subscriptions Collection"
}
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$
```

## delete the subscription by reseting the redfish DB

```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ curl -sk -u XXXXXX:XXXXXX -X POST "https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/Managers/Self/Actions/Oem/AMIManager.RedfishDBReset" -d '{"RedfishDBResetType": "ResetAll"}' -H "Content-Type: application/json" | python3 -m json.tool
{
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.id": "/redfish/v1/TaskService/Tasks/1",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for RedfishDBReset Task",
    "Id": "1",
    "Name": "RedfishDBReset Task",
    "TaskState": "New"
}
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ sleep 120 
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$
```

## check that subscription is deleted

```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/EventService/Subscriptions | jq .
{
  "@odata.context": "/redfish/v1/$metadata#EventDestinationCollection.EventDestinationCollection",
  "@odata.etag": "\"1705444489\"",
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
ETag: "1705445115"
Content-Type: application/json; charset=UTF-8
OData-Version: 4.0
Content-Length: 612
Date: Tue, 16 Jan 2024 22:45:16 GMT

{"@odata.context":"/redfish/v1/$metadata#EventDestination.EventDestination","@odata.etag":"\"1705445115\"","@odata.id":"/redfish/v1/EventService/Subscriptions","@odata.type":"#EventDestination.v1_6_0.EventDestination","Context":"Subscription_VCMP-1","DeliveryRetryPolicy":"TerminateAfterRetries","Description":"Event Subscription","Destination":"https://vcpme-rch-feocp-redfishalerts.mon.vzwops.com/redfish","EventFormatType":"Event","Id":1,"Name":"Subscription 1","Protocol":"Redfish","Status":{"Health":"OK","HealthRollup":"OK","State":"Enabled"},"SubordinateResources":false,"SubscriptionType":"RedfishEvent"}(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$
```

## verify subscription is there

```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/EventService/Subscriptions | jq .
{
  "@odata.context": "/redfish/v1/$metadata#EventDestinationCollection.EventDestinationCollection",
  "@odata.etag": "\"1705445116\"",
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
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/EventService/Subscriptions/1 | jq .
{
  "@odata.context": "/redfish/v1/$metadata#EventDestination.EventDestination",
  "@odata.etag": "\"1705445115\"",
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
export IP="2607:f160:10:80b1:ce:40a:0:e008"
curl  -L -w "%{http_code} %{url_effective}\\n" \
-ku XXXXXX:XXXXXX \
-H "Content-Type: application/json" \
-d '{"MessageId" : "EventLog.1.0.ResourceUpdated"}' \
-X POST https://[${IP}]/redfish/v1/EventService/Actions/EventService.SubmitTestEvent
```

Sent 5 alerts

```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ while [ $count -lt 5 ] ; do
> export IP="2607:f160:10:80b1:ce:40a:0:e008"
> curl  -L -w "%{http_code} %{url_effective}\\n" \
> -ku XXXXXX:XXXXXX \
> -H "Content-Type: application/json" \
> -d '{"MessageId" : "EventLog.1.0.ResourceUpdated"}' \
> -X POST https://[${IP}]/redfish/v1/EventService/Actions/EventService.SubmitTestEvent
> count=$((count+1))
> done
{"@odata.context":"/redfish/v1/$metadata#Task.Task","@odata.id":"/redfish/v1/TaskService/Tasks/16","@odata.type":"#Task.v1_4_2.Task","Description":"Task for EventService SubmitTestEvent Action","Id":"16","Name":"EventService SubmitTestEvent Action","TaskState":"New"}202 https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/EventService/Actions/EventService.SubmitTestEvent
{"@odata.context":"/redfish/v1/$metadata#Task.Task","@odata.id":"/redfish/v1/TaskService/Tasks/17","@odata.type":"#Task.v1_4_2.Task","Description":"Task for EventService SubmitTestEvent Action","Id":"17","Name":"EventService SubmitTestEvent Action","TaskState":"New"}202 https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/EventService/Actions/EventService.SubmitTestEvent
{"@odata.context":"/redfish/v1/$metadata#Task.Task","@odata.id":"/redfish/v1/TaskService/Tasks/18","@odata.type":"#Task.v1_4_2.Task","Description":"Task for EventService SubmitTestEvent Action","Id":"18","Name":"EventService SubmitTestEvent Action","TaskState":"New"}202 https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/EventService/Actions/EventService.SubmitTestEvent
{"@odata.context":"/redfish/v1/$metadata#Task.Task","@odata.id":"/redfish/v1/TaskService/Tasks/19","@odata.type":"#Task.v1_4_2.Task","Description":"Task for EventService SubmitTestEvent Action","Id":"19","Name":"EventService SubmitTestEvent Action","TaskState":"New"}202 https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/EventService/Actions/EventService.SubmitTestEvent
{"@odata.context":"/redfish/v1/$metadata#Task.Task","@odata.id":"/redfish/v1/TaskService/Tasks/20","@odata.type":"#Task.v1_4_2.Task","Description":"Task for EventService SubmitTestEvent Action","Id":"20","Name":"EventService SubmitTestEvent Action","TaskState":"New"}202 https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/EventService/Actions/EventService.SubmitTestEvent
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$
```

## Check vcmp tools if alerts made it to them
1 sample alert in vcmp tools

```log
{
  "@odata.context": [
    "/redfish/v1/$metadata#Event.Event"
  ],
  "@odata.context.keyword": [
    "/redfish/v1/$metadata#Event.Event"
  ],
  "@odata.type": [
    "#Event.v1_4_1.Event"
  ],
  "@odata.type.keyword": [
    "#Event.v1_4_1.Event"
  ],
  "@timestamp": [
    "2024-01-16T23:02:03.275Z"
  ],
  "@version": [
    "1"
  ],
  "@version.keyword": [
    "1"
  ],
  "Context": [
    "Subscription_VCMP-1"
  ],
  "Context.keyword": [
    "Subscription_VCMP-1"
  ],
  "datacenter": [
    "unknown_datacenter"
  ],
  "datacenter.keyword": [
    "unknown_datacenter"
  ],
  "event.original": [
    "{\"host\":{\"ip\":\"2001:db8:42:2d:eb03:1b6f:bed3:cfe3\"},\"Message\":\"SubmitTestEvent Action has been triggered\",\"@version\":\"1\",\"MessageId\":\"EventLog.1.0.ResourceUpdated\",\"user_agent\":{\"original\":\"LuaSocket 3.0-rc1\"},\"Context\":\"Subscription_VCMP-1\",\"Id\":\"13\",\"EventType\":\"Other\",\"@odata.type\":\"#Event.v1_4_1.Event\",\"event\":{\"original\":\"{\\\"@odata.context\\\":\\\"/redfish/v1/$metadata#Event.Event\\\",\\\"@odata.type\\\":\\\"#Event.v1_4_1.Event\\\",\\\"Context\\\":\\\"Subscription_VCMP-1\\\",\\\"Events\\\":[{\\\"Context\\\":\\\"Subscription_VCMP-1\\\",\\\"EventId\\\":\\\"SubmitTestEvent_1705446116\\\",\\\"EventTimestamp\\\":\\\"2024-01-16T23:01:55+00:00\\\",\\\"EventType\\\":\\\"Other\\\",\\\"MemberId\\\":\\\"SubmitTestEvent_1705446116\\\",\\\"Message\\\":\\\"SubmitTestEvent Action has been triggered\\\",\\\"MessageArgs\\\":[\\\"test1\\\",\\\"test2\\\",\\\"test3\\\",\\\"test4\\\"],\\\"MessageId\\\":\\\"EventLog.1.0.ResourceUpdated\\\",\\\"OriginOfCondition\\\":{\\\"@odata.id\\\":\\\"/redfish/v1/EventService/Actions/EventService.SubmitTestEvent\\\"}}],\\\"Events@odata.count\\\":1,\\\"Id\\\":\\\"13\\\",\\\"Name\\\":\\\"Event Array\\\"}\"},\"type\":\"events\",\"Severity\":\"%{[Events][0][Severity]}\",\"HOSTIP\":\"%{[headers][x_real_ip]}\",\"message\":\"{\\\"Context\\\":\\\"Subscription_VCMP-1\\\",\\\"MemberId\\\":\\\"SubmitTestEvent_1705446116\\\",\\\"OriginOfCondition\\\":{\\\"@odata.id\\\":\\\"/redfish/v1/EventService/Actions/EventService.SubmitTestEvent\\\"},\\\"MessageArgs\\\":[\\\"test1\\\",\\\"test2\\\",\\\"test3\\\",\\\"test4\\\"],\\\"Message\\\":\\\"SubmitTestEvent Action has been triggered\\\",\\\"EventTimestamp\\\":\\\"2024-01-16T23:01:55+00:00\\\",\\\"EventType\\\":\\\"Other\\\",\\\"EventId\\\":\\\"SubmitTestEvent_1705446116\\\",\\\"MessageId\\\":\\\"EventLog.1.0.ResourceUpdated\\\"}\",\"Name\":\"Event Array\",\"url\":{\"path\":\"/redfish\",\"domain\":\"vcpme-rch-feocp-redfishalerts.mon.vzwops.com\",\"port\":443},\"@timestamp\":\"2024-01-16T23:02:03.275821Z\",\"datacenter\":\"unknown_datacenter\",\"Events@odata.count\":1,\"Events\":[{\"EventTimestamp\":\"2024-01-16T23:01:55+00:00\",\"EventId\":\"SubmitTestEvent_1705446116\",\"EventType\":\"Other\",\"MemberId\":\"SubmitTestEvent_1705446116\",\"Message\":\"SubmitTestEvent Action has been triggered\",\"MessageArgs\":[\"test1\",\"test2\",\"test3\",\"test4\"],\"MessageId\":\"EventLog.1.0.ResourceUpdated\",\"Context\":\"Subscription_VCMP-1\",\"OriginOfCondition\":{\"@odata.id\":\"/redfish/v1/EventService/Actions/EventService.SubmitTestEvent\"}}],\"EventTimestamp\":\"2024-01-16T23:01:55+00:00\",\"EventId\":\"SubmitTestEvent_1705446116\",\"http\":{\"version\":\"HTTP/1.1\",\"request\":{\"mime_type\":\"application/json\",\"body\":{\"bytes\":\"608\"}},\"method\":\"POST\"},\"@odata.context\":\"/redfish/v1/$metadata#Event.Event\"}"
  ],
  "event.original.keyword": [
    "{\"host\":{\"ip\":\"2001:db8:42:2d:eb03:1b6f:bed3:cfe3\"},\"Message\":\"SubmitTestEvent Action has been triggered\",\"@version\":\"1\",\"MessageId\":\"EventLog.1.0.ResourceUpdated\",\"user_agent\":{\"original\":\"LuaSocket 3.0-rc1\"},\"Context\":\"Subscription_VCMP-1\",\"Id\":\"13\",\"EventType\":\"Other\",\"@odata.type\":\"#Event.v1_4_1.Event\",\"event\":{\"original\":\"{\\\"@odata.context\\\":\\\"/redfish/v1/$metadata#Event.Event\\\",\\\"@odata.type\\\":\\\"#Event.v1_4_1.Event\\\",\\\"Context\\\":\\\"Subscription_VCMP-1\\\",\\\"Events\\\":[{\\\"Context\\\":\\\"Subscription_VCMP-1\\\",\\\"EventId\\\":\\\"SubmitTestEvent_1705446116\\\",\\\"EventTimestamp\\\":\\\"2024-01-16T23:01:55+00:00\\\",\\\"EventType\\\":\\\"Other\\\",\\\"MemberId\\\":\\\"SubmitTestEvent_1705446116\\\",\\\"Message\\\":\\\"SubmitTestEvent Action has been triggered\\\",\\\"MessageArgs\\\":[\\\"test1\\\",\\\"test2\\\",\\\"test3\\\",\\\"test4\\\"],\\\"MessageId\\\":\\\"EventLog.1.0.ResourceUpdated\\\",\\\"OriginOfCondition\\\":{\\\"@odata.id\\\":\\\"/redfish/v1/EventService/Actions/EventService.SubmitTestEvent\\\"}}],\\\"Events@odata.count\\\":1,\\\"Id\\\":\\\"13\\\",\\\"Name\\\":\\\"Event Array\\\"}\"},\"type\":\"events\",\"Severity\":\"%{[Events][0][Severity]}\",\"HOSTIP\":\"%{[headers][x_real_ip]}\",\"message\":\"{\\\"Context\\\":\\\"Subscription_VCMP-1\\\",\\\"MemberId\\\":\\\"SubmitTestEvent_1705446116\\\",\\\"OriginOfCondition\\\":{\\\"@odata.id\\\":\\\"/redfish/v1/EventService/Actions/EventService.SubmitTestEvent\\\"},\\\"MessageArgs\\\":[\\\"test1\\\",\\\"test2\\\",\\\"test3\\\",\\\"test4\\\"],\\\"Message\\\":\\\"SubmitTestEvent Action has been triggered\\\",\\\"EventTimestamp\\\":\\\"2024-01-16T23:01:55+00:00\\\",\\\"EventType\\\":\\\"Other\\\",\\\"EventId\\\":\\\"SubmitTestEvent_1705446116\\\",\\\"MessageId\\\":\\\"EventLog.1.0.ResourceUpdated\\\"}\",\"Name\":\"Event Array\",\"url\":{\"path\":\"/redfish\",\"domain\":\"vcpme-rch-feocp-redfishalerts.mon.vzwops.com\",\"port\":443},\"@timestamp\":\"2024-01-16T23:02:03.275821Z\",\"datacenter\":\"unknown_datacenter\",\"Events@odata.count\":1,\"Events\":[{\"EventTimestamp\":\"2024-01-16T23:01:55+00:00\",\"EventId\":\"SubmitTestEvent_1705446116\",\"EventType\":\"Other\",\"MemberId\":\"SubmitTestEvent_1705446116\",\"Message\":\"SubmitTestEvent Action has been triggered\",\"MessageArgs\":[\"test1\",\"test2\",\"test3\",\"test4\"],\"MessageId\":\"EventLog.1.0.ResourceUpdated\",\"Context\":\"Subscription_VCMP-1\",\"OriginOfCondition\":{\"@odata.id\":\"/redfish/v1/EventService/Actions/EventService.SubmitTestEvent\"}}],\"EventTimestamp\":\"2024-01-16T23:01:55+00:00\",\"EventId\":\"SubmitTestEvent_1705446116\",\"http\":{\"version\":\"HTTP/1.1\",\"request\":{\"mime_type\":\"application/json\",\"body\":{\"bytes\":\"608\"}},\"method\":\"POST\"},\"@odata.context\":\"/redfish/v1/$metadata#Event.Event\"}"
  ],
  "EventId": [
    "SubmitTestEvent_1705446116"
  ],
  "EventId.keyword": [
    "SubmitTestEvent_1705446116"
  ],
  "Events.Context": [
    "Subscription_VCMP-1"
  ],
  "Events.Context.keyword": [
    "Subscription_VCMP-1"
  ],
  "Events.EventId": [
    "SubmitTestEvent_1705446116"
  ],
  "Events.EventId.keyword": [
    "SubmitTestEvent_1705446116"
  ],
  "Events.EventTimestamp": [
    "2024-01-16T23:01:55.000Z"
  ],
  "Events.EventType": [
    "Other"
  ],
  "Events.EventType.keyword": [
    "Other"
  ],
  "Events.MemberId": [
    "SubmitTestEvent_1705446116"
  ],
  "Events.MemberId.keyword": [
    "SubmitTestEvent_1705446116"
  ],
  "Events.Message": [
    "SubmitTestEvent Action has been triggered"
  ],
  "Events.Message.keyword": [
    "SubmitTestEvent Action has been triggered"
  ],
  "Events.MessageArgs": [
    "test1",
    "test2",
    "test3",
    "test4"
  ],
  "Events.MessageArgs.keyword": [
    "test1",
    "test2",
    "test3",
    "test4"
  ],
  "Events.MessageId": [
    "EventLog.1.0.ResourceUpdated"
  ],
  "Events.MessageId.keyword": [
    "EventLog.1.0.ResourceUpdated"
  ],
  "Events.OriginOfCondition.@odata.id": [
    "/redfish/v1/EventService/Actions/EventService.SubmitTestEvent"
  ],
  "Events.OriginOfCondition.@odata.id.keyword": [
    "/redfish/v1/EventService/Actions/EventService.SubmitTestEvent"
  ],
  "Events@odata.count": [
    1
  ],
  "EventTimestamp": [
    "2024-01-16T23:01:55.000Z"
  ],
  "EventType": [
    "Other"
  ],
  "EventType.keyword": [
    "Other"
  ],
  "host.ip": [
    "2001:db8:42:2d:eb03:1b6f:bed3:cfe3"
  ],
  "host.ip.keyword": [
    "2001:db8:42:2d:eb03:1b6f:bed3:cfe3"
  ],
  "HOSTIP": [
    "%{[headers][x_real_ip]}"
  ],
  "HOSTIP.keyword": [
    "%{[headers][x_real_ip]}"
  ],
  "http.method": [
    "POST"
  ],
  "http.method.keyword": [
    "POST"
  ],
  "http.request.body.bytes": [
    "608"
  ],
  "http.request.body.bytes.keyword": [
    "608"
  ],
  "http.request.mime_type": [
    "application/json"
  ],
  "http.request.mime_type.keyword": [
    "application/json"
  ],
  "http.version": [
    "HTTP/1.1"
  ],
  "http.version.keyword": [
    "HTTP/1.1"
  ],
  "Id": [
    "13"
  ],
  "Id.keyword": [
    "13"
  ],
  "message": [
    "{\"Context\":\"Subscription_VCMP-1\",\"MemberId\":\"SubmitTestEvent_1705446116\",\"OriginOfCondition\":{\"@odata.id\":\"/redfish/v1/EventService/Actions/EventService.SubmitTestEvent\"},\"MessageArgs\":[\"test1\",\"test2\",\"test3\",\"test4\"],\"Message\":\"SubmitTestEvent Action has been triggered\",\"EventTimestamp\":\"2024-01-16T23:01:55+00:00\",\"EventType\":\"Other\",\"EventId\":\"SubmitTestEvent_1705446116\",\"MessageId\":\"EventLog.1.0.ResourceUpdated\"}"
  ],
  "Message": [
    "SubmitTestEvent Action has been triggered"
  ],
  "message.keyword": [
    "{\"Context\":\"Subscription_VCMP-1\",\"MemberId\":\"SubmitTestEvent_1705446116\",\"OriginOfCondition\":{\"@odata.id\":\"/redfish/v1/EventService/Actions/EventService.SubmitTestEvent\"},\"MessageArgs\":[\"test1\",\"test2\",\"test3\",\"test4\"],\"Message\":\"SubmitTestEvent Action has been triggered\",\"EventTimestamp\":\"2024-01-16T23:01:55+00:00\",\"EventType\":\"Other\",\"EventId\":\"SubmitTestEvent_1705446116\",\"MessageId\":\"EventLog.1.0.ResourceUpdated\"}"
  ],
  "Message.keyword": [
    "SubmitTestEvent Action has been triggered"
  ],
  "MessageId": [
    "EventLog.1.0.ResourceUpdated"
  ],
  "MessageId.keyword": [
    "EventLog.1.0.ResourceUpdated"
  ],
  "Name": [
    "Event Array"
  ],
  "Name.keyword": [
    "Event Array"
  ],
  "Severity": [
    "%{[Events][0][Severity]}"
  ],
  "Severity.keyword": [
    "%{[Events][0][Severity]}"
  ],
  "type": [
    "events"
  ],
  "type.keyword": [
    "events"
  ],
  "url.domain": [
    "vcpme-rch-feocp-redfishalerts.mon.vzwops.com"
  ],
  "url.domain.keyword": [
    "vcpme-rch-feocp-redfishalerts.mon.vzwops.com"
  ],
  "url.path": [
    "/redfish"
  ],
  "url.path.keyword": [
    "/redfish"
  ],
  "url.port": [
    443
  ],
  "user_agent.original": [
    "LuaSocket 3.0-rc1"
  ],
  "user_agent.original.keyword": [
    "LuaSocket 3.0-rc1"
  ],
  "_id": "14uDFI0BiKogKt9dsgZk",
  "_index": "vcp-faredge-so-2024.01.15-000048",
  "_score": null
}
```

### alerts are coming into elastic with VCMP tools, I have added screen shots and will upload to test case ### for evidence... queries with new vcmp tools after the rebulid is not working yet.


## Redfish Event URL has been set and is good

## MEAKV-654 
## Redfish add user, change password, then delete user

```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$  ansible-playbook --vault-password-file /tmp/vault-pass -i inventory-fe/rchltxfe-1.yml -e attributes_file=vars/proteus_redfish_attributes.yml -e target="welktxef-931856-rz-le2pts6-008" --tags user ZT_Redfish_tests.yml

PLAY [welktxef-931856-rz-le2pts6-008] **********************************************************************************************************************

TASK [redfish/users : Generate request body] ***************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008]

TASK [redfish/users : Add user] ****************************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [redfish/users : debug] *******************************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
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
        "date": "Tue, 16 Jan 2024 23:14:41 GMT",
        "elapsed": 5,
        "etag": "\"1705446879\"",
        "failed": false,
        "json": {
            "@odata.context": "/redfish/v1/$metadata#ManagerAccount.ManagerAccount",
            "@odata.etag": "\"1705446879\"",
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
        "location": "https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/AccountService/Accounts/5",
        "msg": "OK (575 bytes)",
        "odata_version": "4.0",
        "redirected": false,
        "server": "AMI MegaRAC Redfish Service",
        "status": 201,
        "url": "https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/AccountService/Accounts"
    }
}

TASK [redfish/users : Storing location of new user] ********************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008]

TASK [redfish/users : sleep if needed] *********************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [redfish/users : get new user with its own credentials] ***********************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [redfish/users : debug] *******************************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
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
        "date": "Tue, 16 Jan 2024 23:15:12 GMT",
        "elapsed": 0,
        "etag": "\"1705446879\"",
        "failed": false,
        "json": {
            "@odata.context": "/redfish/v1/$metadata#ManagerAccount.ManagerAccount",
            "@odata.etag": "\"1705446879\"",
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
        "url": "https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/AccountService/Accounts/5"
    }
}

TASK [redfish/users : Generate request body] ***************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008]

TASK [redfish/users : Change password] *********************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [redfish/users : debug] *******************************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "response": {
        "allow": "GET, PATCH, DELETE",
        "changed": false,
        "connection": "close",
        "cookies": {},
        "cookies_string": "",
        "date": "Tue, 16 Jan 2024 23:15:21 GMT",
        "elapsed": 9,
        "failed": false,
        "msg": "OK (unknown bytes)",
        "redirected": false,
        "server": "AMI MegaRAC Redfish Service",
        "status": 204,
        "url": "https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/AccountService/Accounts/5"
    }
}

TASK [redfish/users : sleep if needed] *********************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [redfish/users : Get new user with its own (updated) credentials] *************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [redfish/users : debug] *******************************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
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
        "date": "Tue, 16 Jan 2024 23:15:52 GMT",
        "elapsed": 0,
        "etag": "\"1705446912\"",
        "failed": false,
        "json": {
            "@odata.context": "/redfish/v1/$metadata#ManagerAccount.ManagerAccount",
            "@odata.etag": "\"1705446912\"",
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
        "url": "https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/AccountService/Accounts/5"
    }
}

TASK [redfish/users : Deleting user] ***********************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [redfish/users : debug] *******************************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "response": {
        "allow": "GET, PATCH, DELETE",
        "changed": false,
        "connection": "close",
        "cookies": {},
        "cookies_string": "",
        "date": "Tue, 16 Jan 2024 23:15:58 GMT",
        "elapsed": 5,
        "failed": false,
        "msg": "OK (unknown bytes)",
        "redirected": false,
        "server": "AMI MegaRAC Redfish Service",
        "status": 204,
        "url": "https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/AccountService/Accounts/5"
    }
}

TASK [redfish/users : sleep if needed] *********************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [redfish/users : Check if user is gone] ***************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [redfish/users : debug] *******************************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "response": {
        "changed": false,
        "connection": "close",
        "content_length": "512",
        "content_type": "application/json; charset=UTF-8",
        "date": "Tue, 16 Jan 2024 23:16:29 GMT",
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
        "url": "https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/AccountService/Accounts/5"
    }
}

PLAY RECAP *************************************************************************************************************************************************
welktxef-931856-rz-le2pts6-008 : ok=18   changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0

(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$
```
## Passed test, all worked as expected


