# ZT Triton 2.27 BMC firmware validation
# MEAKV-648-654
# 12/13/23 James Patchett

## Target Controller rchltxib-c000000-003 CR-3 (Richardson infrastructure System)
OAM: 2607:f160:0:3049:cd:290:0:10

## Subcloud rchltxfe-d93180012-001 (VCP-fe Infrastructure)
OAM: 2607:f160:10:9073:ce:40a:0:f400
ILO: 2607:f160:10:9073:ce:406:0:1000

ipmitool -I lanplus -U XXXXXX -P XXXXXX -H 2607:f160:10:9073:ce:406:0:1000 sol activate

## Subcloud rchltxfe-d93180012-001

## MEAKV-648
## Check version of BIOS 
```log
[XXXXXX@vcpe-jumpserver ~]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[2607:f160:10:9073:ce:406:0:1000]/redfish/v1/UpdateService/FirmwareInventory/BIOS | jq .
{
  "@odata.context": "/redfish/v1/$metadata#SoftwareInventory.SoftwareInventory",
  "@odata.etag": "\"1702504534\"",
  "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/BIOS",
  "@odata.type": "#SoftwareInventory.v1_2_3.SoftwareInventory",
  "Id": "BIOS",
  "Name": "BIOS",
  "Updateable": true,
  "Version": "2.06"
}
[XXXXXX@vcpe-jumpserver ~]$
```

## Check version of BMC

```log
[XXXXXX@vcpe-jumpserver ~]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[2607:f160:10:9073:ce:406:0:1000]/redfish/v1/UpdateService/FirmwareInventory/BMC | jq .
{
  "@odata.context": "/redfish/v1/$metadata#SoftwareInventory.SoftwareInventory",
  "@odata.etag": "\"1701987533\"",
  "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/BMC",
  "@odata.type": "#SoftwareInventory.v1_2_3.SoftwareInventory",
  "Id": "BMC",
  "Name": "BMC",
  "Updateable": true,
  "Version": "2.27.00"
}
[XXXXXX@vcpe-jumpserver ~]$
```

## MEAKV-649
## set hostname with ZT_Redfish_tests.yml

## Changed hostname with Browser...

```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[2607:f160:10:9073:ce:406:0:1000]/redfish/v1/Systems/Self | jq ."HostName"
"rchltxfb-93180012-rz-le0trtn-002"
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$
```

```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ ansible-playbook --vault-password-file /tmp/vault-pass -i inventory-fe/rchltxfe-1.yml -e attributes_file=vars/proteus_redfish_attributes.yml -e target="rchltxfb-93180012-rz-le0trtn-001" --tags hostname ZT_Redfish_tests.yml

PLAY [rchltxfb-93180012-rz-le0trtn-001] *******************************************************************************************************

TASK [redfish/attributes : what we're setting] ************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001] => {
    "set_attr_item": {
        "attribute": "HostName",
        "new_value": "newhostname2",
        "path": "/redfish/v1/Systems/Self"
    }
}

TASK [redfish/attributes : Setting HostName] **************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001 -> localhost]

TASK [redfish/attributes : debug] *************************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001] => {
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
        "date": "Thu, 14 Dec 2023 01:04:04 GMT",
        "elapsed": 3,
        "etag": "\"1702515844\"",
        "failed": false,
        "msg": "OK (unknown bytes)",
        "odata_version": "4.0",
        "redirected": false,
        "server": "AMI MegaRAC Redfish Service",
        "status": 204,
        "url": "https://[2607:f160:10:9073:ce:406:0:1000]/redfish/v1/Systems/Self"
    }
}

TASK [redfish/attributes : set_fact] **********************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001]

TASK [redfish/attributes : sleep if needed] ***************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001 -> localhost]
included: /home/XXXXXX/richardson/playbooks/vcp-fe-ib-automation/roles/redfish/attributes/tasks/check_attribute.yml for rchltxfb-93180012-rz-le0trtn-001

TASK [redfish/attributes : what is currently verified] ****************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001] => {
    "msg": "Sending GET to /redfish/v1/Systems/Self and query the returned json for HostName. Value shall be newhostname2"
}

TASK [redfish/attributes : Checking HostName at /redfish/v1/Systems/Self] *********************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001 -> localhost]

TASK [redfish/attributes : what we're setting] ************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001] => {
    "set_attr_item": {
        "attribute": "HostName",
        "new_value": "rchltxfb-93180012-rz-le0trtn-001",
        "path": "/redfish/v1/Systems/Self"
    }
}

TASK [redfish/attributes : Setting HostName] **************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001 -> localhost]

TASK [redfish/attributes : debug] *************************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001] => {
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
        "date": "Thu, 14 Dec 2023 01:05:16 GMT",
        "elapsed": 6,
        "etag": "\"1702515916\"",
        "failed": false,
        "msg": "OK (unknown bytes)",
        "odata_version": "4.0",
        "redirected": false,
        "server": "AMI MegaRAC Redfish Service",
        "status": 204,
        "url": "https://[2607:f160:10:9073:ce:406:0:1000]/redfish/v1/Systems/Self"
    }
}

TASK [redfish/attributes : set_fact] **********************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001]
included: /home/XXXXXX/richardson/playbooks/vcp-fe-ib-automation/roles/redfish/attributes/tasks/check_attribute.yml for rchltxfb-93180012-rz-le0trtn-001

TASK [redfish/attributes : what is currently verified] ****************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001] => {
    "msg": "Sending GET to /redfish/v1/Systems/Self and query the returned json for HostName. Value shall be rchltxfb-93180012-rz-le0trtn-001"
}

TASK [redfish/attributes : Checking HostName at /redfish/v1/Systems/Self] *********************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001 -> localhost]

PLAY RECAP ************************************************************************************************************************************
rchltxfb-93180012-rz-le0trtn-001 : ok=15   changed=0    unreachable=0    failed=0    skipped=5    rescued=0    ignored=0

(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$
```

## MEAKV-650
## set static DNS servers via api

## change DNS servers to something false...

```log
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[2607:f160:10:9073:ce:406:0:1000]/redfish/v1/Managers/Self/EthernetInterfaces/eth0 | jq ."StaticNameServers"
[
  "2607:f160:10:4409:ce:103:0:9",
  "2607:f160:10:4409:ce:103:0:10",
  "::"
]
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$
```
```log

(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ ansible-playbook --vault-password-file /tmp/vault-pass -i inventory-fe/rchltxfe-1.yml -e attributes_file=vars/proteus_redfish_attributes.yml -e target="rchltxfb-93180012-rz-le0trtn-001" --tags dns ZT_Redfish_tests.yml

PLAY [rchltxfb-93180012-rz-le0trtn-001] *******************************************************************************************************
included: /home/XXXXXX/richardson/playbooks/vcp-fe-ib-automation/roles/redfish/attributes/tasks/set_attribute.yml for rchltxfb-93180012-rz-le0trtn-001 => (item={'path': '/redfish/v1/Managers/Self/EthernetInterfaces/eth0', 'attribute': 'StaticNameServers', 'new_value': ['2607:f160:10:4409:ce:103:0:5', '2607:f160:10:4409:ce:103:0:6'], 'expected_response': 202, 'expected_value': ['2607:f160:10:4409:ce:103:0:5', '2607:f160:10:4409:ce:103:0:6', '::']})

TASK [redfish/attributes : what we're setting] ************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001] => {
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

TASK [redfish/attributes : Setting StaticNameServers] *****************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001 -> localhost]

TASK [redfish/attributes : debug] *************************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001] => {
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
        "date": "Thu, 14 Dec 2023 01:15:05 GMT",
        "elapsed": 5,
        "etag": "\"1702516495\"",
        "failed": false,
        "json": {
            "@odata.context": "/redfish/v1/$metadata#Task.Task",
            "@odata.id": "/redfish/v1/TaskService/Tasks/6",
            "@odata.type": "#Task.v1_4_2.Task",
            "Description": "Task for EthernetInterface Action",
            "Id": "6",
            "Name": "EthernetInterface Action",
            "TaskState": "New"
        },
        "link": "<http://redfish.dmtf.org/schemas/v1/EthernetInterface.v1_5_1.json>; rel=describedby, <http://redfish.dmtf.org/schemas/v1/Task.v1_4_2.json>, </redfish/v1/TaskService/Tasks/6>; path=",
        "location": "https://[2607:f160:10:9073:ce:406:0:1000]/redfish/v1/TaskService/Tasks/6",
        "msg": "OK (243 bytes)",
        "odata_version": "4.0",
        "prefer": "respond-async; wait=1",
        "redirected": false,
        "server": "AMI MegaRAC Redfish Service",
        "status": 202,
        "url": "https://[2607:f160:10:9073:ce:406:0:1000]/redfish/v1/Managers/Self/EthernetInterfaces/eth0"
    }
}

TASK [redfish/attributes : set_fact] **********************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001]

TASK [redfish/attributes : sleep if needed] ***************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001 -> localhost]
included: /home/XXXXXX/richardson/playbooks/vcp-fe-ib-automation/roles/redfish/attributes/tasks/check_attribute.yml for rchltxfb-93180012-rz-le0trtn-001

TASK [redfish/attributes : what is currently verified] ****************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001] => {
    "msg": "Sending GET to /redfish/v1/Managers/Self/EthernetInterfaces/eth0 and query the returned json for StaticNameServers. Value shall be ['2607:f160:10:4409:ce:103:0:5', '2607:f160:10:4409:ce:103:0:6', '::']"
}

TASK [redfish/attributes : Checking StaticNameServers at /redfish/v1/Managers/Self/EthernetInterfaces/eth0] ***********************************
ok: [rchltxfb-93180012-rz-le0trtn-001 -> localhost]

PLAY RECAP ************************************************************************************************************************************
rchltxfb-93180012-rz-le0trtn-001 : ok=9    changed=0    unreachable=0    failed=0    skipped=2    rescued=0    ignored=0

(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ 

```

## Check to see if dns was updated 

```log
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[2607:f160:10:9073:ce:406:0:1000]/redfish/v1/Managers/Self/EthernetInterfaces/eth0 | jq ."StaticNameServers"
[
  "2607:f160:10:4409:ce:103:0:5",
  "2607:f160:10:4409:ce:103:0:6",
  "::"
]
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$
```

## DNS looks good, moving to next test.

## MEAKV-651
## Set NTP servers

## check exiting values

```log
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[2607:f160:10:9073:ce:406:0:1000]/redfish/v1/Managers/Self/NetworkProtocol | jq .NTP
{
  "NTPServers": [
    "2607:f160:10:9200::e",
    "2607:f160:10:9200::f"
  ],
  "Port": 123,
  "ProtocolEnabled": true
}
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$
```

## Now run ZT_Redfish_tests.yml ansible script to set back to correct servers
## Set ntp

```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ ansible-playbook --vault-password-file /tmp/vault-pass -i inventory-fe/rchltxfe-1.yml -e attributes_file=vars/proteus_redfish_attributes.yml -e target="rchltxfb-93180012-rz-le0trtn-001" --tags ntp ZT_Redfish_tests.yml

PLAY [rchltxfb-93180012-rz-le0trtn-001] *******************************************************************************************************

TASK [redfish/attributes : what we're setting] ************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001] => {
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

TASK [redfish/attributes : Setting NTP] *******************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001 -> localhost]

TASK [redfish/attributes : debug] *************************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001] => {
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
        "date": "Fri, 15 Dec 2023 11:34:10 GMT",
        "elapsed": 4,
        "etag": "\"1702516605\"",
        "failed": false,
        "msg": "OK (unknown bytes)",
        "odata_version": "4.0",
        "redirected": false,
        "server": "AMI MegaRAC Redfish Service",
        "status": 204,
        "url": "https://[2607:f160:10:9073:ce:406:0:1000]/redfish/v1/Managers/Self/NetworkProtocol"
    }
}

TASK [redfish/attributes : set_fact] **********************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001]

TASK [redfish/attributes : sleep if needed] ***************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001 -> localhost]
included: /home/XXXXXX/richardson/playbooks/vcp-fe-ib-automation/roles/redfish/attributes/tasks/check_attribute.yml for rchltxfb-93180012-rz-le0trtn-001

TASK [redfish/attributes : what is currently verified] ****************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001] => {
    "msg": "Sending GET to /redfish/v1/Managers/Self/NetworkProtocol and query the returned json for NTP.NTPServers. Value shall be ['2607:f160:10:9200::a', '2607:f160:10:8200::a']"
}

TASK [redfish/attributes : Checking NTP.NTPServers at /redfish/v1/Managers/Self/NetworkProtocol] **********************************************
ok: [rchltxfb-93180012-rz-le0trtn-001 -> localhost]

PLAY RECAP ************************************************************************************************************************************
rchltxfb-93180012-rz-le0trtn-001 : ok=8    changed=0    unreachable=0    failed=0    skipped=2    rescued=0    ignored=0

(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$

```

## verify settings took with a query to redfish db

```log
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[2607:f160:10:9073:ce:406:0:1000]/redfish/v1/Managers/Self/NetworkProtocol | jq .NTP
{
  "NTPServers": [
    "2607:f160:10:9200::a",
    "2607:f160:10:8200::a"
  ],
  "Port": 123,
  "ProtocolEnabled": true
}
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$

```
## success, next test

## MEAKV-652
## delete subscription then put it back

## redfish DB reset command, will result in deleting exisiting subscriptions

```sh
curl -sk -u XXXXXX:XXXXXX -X POST "https://[2607:f160:10:9073:ce:406:0:1000]/redfish/v1/Managers/Self/Actions/Oem/AMIManager.RedfishDBReset" -d '{"RedfishDBResetType": "ResetAll"}' -H "Content-Type: application/json" | python3 -m json.tool
```
## check to see if an subscription exists

```log
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[2607:f160:10:9073:ce:406:0:1000]/redfish/v1/EventService/Subscriptions | jq .
{
  "@odata.context": "/redfish/v1/$metadata#EventDestinationCollection.EventDestinationCollection",
  "@odata.etag": "\"1702517514\"",
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
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$
```

## delete the subscription by reseting the redfish DB

```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ curl -sk -u XXXXXX:XXXXXX -X POST "https://[2607:f160:10:9073:ce:406:0:1000]/redfish/v1/Managers/Self/Actions/Oem/AMIManager.RedfishDBReset" -d '{"RedfishDBResetType": "ResetAll"}' -H "Content-Type: application/json" | python3 -m json.tool
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
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[2607:f160:10:9073:ce:406:0:1000]/redfish/v1/EventService/Subscriptions | jq .
{
  "@odata.context": "/redfish/v1/$metadata#EventDestinationCollection.EventDestinationCollection",
  "@odata.etag": "\"1702517761\"",
  "@odata.id": "/redfish/v1/EventService/Subscriptions",
  "@odata.type": "#EventDestinationCollection.EventDestinationCollection",
  "Description": "Collection for Event Subscriptions",
  "Members": [],
  "Members@odata.count": 0,
  "Name": "Event Subscriptions Collection"
}
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$

```

## Now set the subscription URL to bmc

```sh
export IP=2607:f160:10:9073:ce:406:0:1000
curl -i -s -u XXXXXX:XXXXXX -H "Content-Type: application/json" -k -X POST -n -d '
{
"Context": "Subscription_VCMP-1",
"Destination": "https://vcpme-rch-feocp-redfishalerts.mon.vzwops.com/redfish",
"Protocol": "Redfish"
}' https://[${IP}]/redfish/v1/EventService/Subscriptions

```

```log
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ export IP=2607:f160:10:9073:ce:406:0:1000
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ curl -i -s -u XXXXXX:XXXXXX -H "Content-Type: application/json" -k -X POST -n -d '
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
ETag: "1702518341"
Content-Type: application/json; charset=UTF-8
OData-Version: 4.0
Content-Length: 612
Date: Thu, 14 Dec 2023 01:45:42 GMT

{"@odata.context":"/redfish/v1/$metadata#EventDestination.EventDestination","@odata.etag":"\"1702518341\"","@odata.id":"/redfish/v1/EventService/Subscriptions","@odata.type":"#EventDestination.v1_6_0.EventDestination","Context":"Subscription_VCMP-1","DeliveryRetryPolicy":"TerminateAfterRetries","Description":"Event Subscription","Destination":"https://vcpme-rch-feocp-redfishalerts.mon.vzwops.com/redfish","EventFormatType":"Event","Id":1,"Name":"Subscription 1","Protocol":"Redfish","Status":{"Health":"OK","HealthRollup":"OK","State":"Enabled"},"SubordinateResources":false,"SubscriptionType":"RedfishEvent"}[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$
```

## verify subscription is there

```log
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[2607:f160:10:9073:ce:406:0:1000]/redfish/v1/EventService/Subscriptions | jq .
{
  "@odata.context": "/redfish/v1/$metadata#EventDestinationCollection.EventDestinationCollection",
  "@odata.etag": "\"1702518341\"",
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
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[2607:f160:10:9073:ce:406:0:1000]/redfish/v1/EventService/Subscriptions/1 | jq .
{
  "@odata.context": "/redfish/v1/$metadata#EventDestination.EventDestination",
  "@odata.etag": "\"1702518341\"",
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
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$
```

## submit an event for BMC to send to nortbound VCMP Tools

```sh
export IP="2607:f160:10:9073:ce:406:0:1000"
curl  -L -w "%{http_code} %{url_effective}\\n" \
-ku XXXXXX:XXXXXX \
-H "Content-Type: application/json" \
-d '{"MessageId" : "EventLog.1.0.ResourceUpdated"}' \
-X POST https://[${IP}]/redfish/v1/EventService/Actions/EventService.SubmitTestEvent
```

```log
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ export IP="2607:f160:10:9073:ce:406:0:1000"
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ curl  -L -w "%{http_code} %{url_effective}\\n" \
> -ku XXXXXX:XXXXXX \
> -H "Content-Type: application/json" \
> -d '{"MessageId" : "EventLog.1.0.ResourceUpdated"}' \
> -X POST https://[${IP}]/redfish/v1/EventService/Actions/EventService.SubmitTestEvent
{"@odata.context":"/redfish/v1/$metadata#Task.Task","@odata.id":"/redfish/v1/TaskService/Tasks/3","@odata.type":"#Task.v1_4_2.Task","Description":"Task for EventService SubmitTestEvent Action","Id":"3","Name":"EventService SubmitTestEvent Action","TaskState":"New"}202 https://[2607:f160:10:9073:ce:406:0:1000]/redfish/v1/EventService/Actions/EventService.SubmitTestEvent
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ curl  -L -w "%{http_code} %{url_effective}\\n" \
> -ku XXXXXX:XXXXXX \
> -H "Content-Type: application/json" \
> -d '{"MessageId" : "EventLog.1.0.ResourceUpdated"}' \
> -X POST https://[${IP}]/redfish/v1/EventService/Actions/EventService.SubmitTestEvent
curl  -L -w "%{http_code} %{url_effective}\\n" \
-ku XXXXXX:XXXXXX \
-H "Content-Type: application/json" \
-d '{"MessageId" : "EventLog.1.0.ResourceUpdated"}' \
-X POST https://[${IP}]/redfish/v1/EventService/Actions/EventService.SubmitTestEvent{"@odata.context":"/redfish/v1/$metadata#Task.Task","@odata.id":"/redfish/v1/TaskService/Tasks/4","@odata.type":"#Task.v1_4_2.Task","Description":"Task for EventService SubmitTestEvent Action","Id":"4","Name":"EventService SubmitTestEvent Action","TaskState":"New"}202 https://[2607:f160:10:9073:ce:406:0:1000]/redfish/v1/EventService/Actions/EventService.SubmitTestEvent
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ curl  -L -w "%{http_code} %{url_effective}\\n" \
> -ku XXXXXX:XXXXXX \
> -H "Content-Type: application/json" \
> -d '{"MessageId" : "EventLog.1.0.ResourceUpdated"}' \
> -X POST https://[${IP}]/redfish/v1/EventService/Actions/EventService.SubmitTestEvent
{"@odata.context":"/redfish/v1/$metadata#Task.Task","@odata.id":"/redfish/v1/TaskService/Tasks/5","@odata.type":"#Task.v1_4_2.Task","Description":"Task for EventService SubmitTestEvent Action","Id":"5","Name":"EventService SubmitTestEvent Action","TaskState":"New"}202 https://[2607:f160:10:9073:ce:406:0:1000]/redfish/v1/EventService/Actions/EventService.SubmitTestEvent
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ curl  -L -w "%{http_code} %{url_effective}\\n" -ku XXXXXX:XXXXXX -H "Content-Type: application/json" -d '{"MessageId" : "EventLog.1.0.ResourceUpdated"}' -X POST https://[${IP}]/redfish/v1/EventService/Actions/EventService.SubmitTestEvent
{"@odata.context":"/redfish/v1/$metadata#Task.Task","@odata.id":"/redfish/v1/TaskService/Tasks/6","@odata.type":"#Task.v1_4_2.Task","Description":"Task for EventService SubmitTestEvent Action","Id":"6","Name":"EventService SubmitTestEvent Action","TaskState":"New"}202 https://[2607:f160:10:9073:ce:406:0:1000]/redfish/v1/EventService/Actions/EventService.SubmitTestEvent
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ curl  -L -w "%{http_code} %{url_effective}\\n" -ku XXXXXX:XXXXXX -H "Content-Type: application/json" -d '{"MessageId" : "EventLog.1.0.ResourceUpdated"}' -X POST https://[${IP}]/redfish/v1/EventService/Actions/EventService.SubmitTestEvent
{"@odata.context":"/redfish/v1/$metadata#Task.Task","@odata.id":"/redfish/v1/TaskService/Tasks/7","@odata.type":"#Task.v1_4_2.Task","Description":"Task for EventService SubmitTestEvent Action","Id":"7","Name":"EventService SubmitTestEvent Action","TaskState":"New"}202 https://[2607:f160:10:9073:ce:406:0:1000]/redfish/v1/EventService/Actions/EventService.SubmitTestEvent
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ curl  -L -w "%{http_code} %{url_effective}\\n" -ku XXXXXX:XXXXXX -H "Content-Type: application/json" -d '{"MessageId" : "EventLog.1.0.ResourceUpdated"}' -X POST https://[${IP}]/redfish/v1/EventService/Actions/EventService.SubmitTestEvent
{"@odata.context":"/redfish/v1/$metadata#Task.Task","@odata.id":"/redfish/v1/TaskService/Tasks/8","@odata.type":"#Task.v1_4_2.Task","Description":"Task for EventService SubmitTestEvent Action","Id":"8","Name":"EventService SubmitTestEvent Action","TaskState":"New"}202 https://[2607:f160:10:9073:ce:406:0:1000]/redfish/v1/EventService/Actions/EventService.SubmitTestEvent
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$
```

## Check vcmp tools if alerts made it to them

### alerts are coming into elastic with VCMP tools, I have added screen shots and will upload to test case ### for evidence... queries with new vcmp tools after the rebulid is not working yet.

All Alerts came into the system and was validated, will upload screen shots

## Redfish Event URL has been set and is good

## MEAKV-654 
## Redfish add user, change password, then delete user

```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ ansible-playbook --vault-password-file /tmp/vault-pass -i inventory-fe/rchltxfe-1.yml -e attributes_file=vars/proteus_redfish_attributes.yml -e target="rchltxfb-93180012-rz-le0trtn-001" --tags user ZT_Redfish_tests.yml

PLAY [rchltxfb-93180012-rz-le0trtn-001] *******************************************************************************************************

TASK [redfish/users : Generate request body] **************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001]

TASK [redfish/users : Add user] ***************************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001 -> localhost]

TASK [redfish/users : debug] ******************************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001] => {
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
        "date": "Thu, 14 Dec 2023 01:56:33 GMT",
        "elapsed": 4,
        "etag": "\"1702518991\"",
        "failed": false,
        "json": {
            "@odata.context": "/redfish/v1/$metadata#ManagerAccount.ManagerAccount",
            "@odata.etag": "\"1702518991\"",
            "@odata.id": "/redfish/v1/AccountService/Accounts",
            "@odata.type": "#ManagerAccount.v1_3_1.ManagerAccount",
            "AccountTypes": [
                "Redfish"
            ],
            "Certificates": {
                "@odata.id": "/redfish/v1/AccountService/Accounts/7/Certificates"
            },
            "Description": "Ansible user",
            "Enabled": true,
            "Id": "7",
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
        "link": "<http://redfish.dmtf.org/schemas/v1/ManagerAccount.v1_3_1.json>; rel=describedby, </redfish/v1/AccountService/Accounts>; path=",
        "location": "https://[2607:f160:10:9073:ce:406:0:1000]/redfish/v1/AccountService/Accounts/7",
        "msg": "OK (575 bytes)",
        "odata_version": "4.0",
        "redirected": false,
        "server": "AMI MegaRAC Redfish Service",
        "status": 201,
        "url": "https://[2607:f160:10:9073:ce:406:0:1000]/redfish/v1/AccountService/Accounts"
    }
}

TASK [redfish/users : Storing location of new user] *******************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001]

TASK [redfish/users : sleep if needed] ********************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001 -> localhost]

TASK [redfish/users : get new user with its own credentials] **********************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001 -> localhost]

TASK [redfish/users : debug] ******************************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001] => {
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
        "date": "Thu, 14 Dec 2023 01:57:04 GMT",
        "elapsed": 1,
        "etag": "\"1702518991\"",
        "failed": false,
        "json": {
            "@odata.context": "/redfish/v1/$metadata#ManagerAccount.ManagerAccount",
            "@odata.etag": "\"1702518991\"",
            "@odata.id": "/redfish/v1/AccountService/Accounts/7",
            "@odata.type": "#ManagerAccount.v1_3_1.ManagerAccount",
            "AccountTypes": [
                "Redfish"
            ],
            "Certificates": {
                "@odata.id": "/redfish/v1/AccountService/Accounts/7/Certificates"
            },
            "Description": "Ansible user",
            "Enabled": true,
            "Id": "7",
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
        "link": "<http://redfish.dmtf.org/schemas/v1/ManagerAccount.v1_3_1.json>; rel=describedby, </redfish/v1/AccountService/Roles/XXXXXX>; path=/Links/Role, </redfish/v1/AccountService/Accounts/7/Certificates>; path=/Certificates",
        "msg": "OK (578 bytes)",
        "odata_version": "4.0",
        "redirected": false,
        "server": "AMI MegaRAC Redfish Service",
        "status": 200,
        "url": "https://[2607:f160:10:9073:ce:406:0:1000]/redfish/v1/AccountService/Accounts/7"
    }
}

TASK [redfish/users : Generate request body] **************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001]

TASK [redfish/users : Change password] ********************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001 -> localhost]

TASK [redfish/users : debug] ******************************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001] => {
    "response": {
        "allow": "GET, PATCH, DELETE",
        "changed": false,
        "connection": "close",
        "cookies": {},
        "cookies_string": "",
        "date": "Thu, 14 Dec 2023 01:57:17 GMT",
        "elapsed": 12,
        "failed": false,
        "msg": "OK (unknown bytes)",
        "redirected": false,
        "server": "AMI MegaRAC Redfish Service",
        "status": 204,
        "url": "https://[2607:f160:10:9073:ce:406:0:1000]/redfish/v1/AccountService/Accounts/7"
    }
}

TASK [redfish/users : sleep if needed] ********************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001 -> localhost]

TASK [redfish/users : Get new user with its own (updated) credentials] ************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001 -> localhost]

TASK [redfish/users : debug] ******************************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001] => {
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
        "date": "Thu, 14 Dec 2023 01:57:49 GMT",
        "elapsed": 0,
        "etag": "\"1702519026\"",
        "failed": false,
        "json": {
            "@odata.context": "/redfish/v1/$metadata#ManagerAccount.ManagerAccount",
            "@odata.etag": "\"1702519026\"",
            "@odata.id": "/redfish/v1/AccountService/Accounts/7",
            "@odata.type": "#ManagerAccount.v1_3_1.ManagerAccount",
            "AccountTypes": [
                "Redfish"
            ],
            "Certificates": {
                "@odata.id": "/redfish/v1/AccountService/Accounts/7/Certificates"
            },
            "Description": "Ansible user",
            "Enabled": true,
            "Id": "7",
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
        "link": "<http://redfish.dmtf.org/schemas/v1/ManagerAccount.v1_3_1.json>; rel=describedby, </redfish/v1/AccountService/Roles/XXXXXX>; path=/Links/Role, </redfish/v1/AccountService/Accounts/7/Certificates>; path=/Certificates",
        "msg": "OK (578 bytes)",
        "odata_version": "4.0",
        "redirected": false,
        "server": "AMI MegaRAC Redfish Service",
        "status": 200,
        "url": "https://[2607:f160:10:9073:ce:406:0:1000]/redfish/v1/AccountService/Accounts/7"
    }
}

TASK [redfish/users : Deleting user] **********************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001 -> localhost]

TASK [redfish/users : debug] ******************************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001] => {
    "response": {
        "allow": "GET, PATCH, DELETE",
        "changed": false,
        "connection": "close",
        "cookies": {},
        "cookies_string": "",
        "date": "Thu, 14 Dec 2023 01:57:55 GMT",
        "elapsed": 5,
        "failed": false,
        "msg": "OK (unknown bytes)",
        "redirected": false,
        "server": "AMI MegaRAC Redfish Service",
        "status": 204,
        "url": "https://[2607:f160:10:9073:ce:406:0:1000]/redfish/v1/AccountService/Accounts/7"
    }
}

TASK [redfish/users : sleep if needed] ********************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001 -> localhost]

TASK [redfish/users : Check if user is gone] **************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001 -> localhost]

TASK [redfish/users : debug] ******************************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001] => {
    "response": {
        "changed": false,
        "connection": "close",
        "content_length": "512",
        "content_type": "application/json; charset=UTF-8",
        "date": "Thu, 14 Dec 2023 01:58:26 GMT",
        "elapsed": 0,
        "failed": false,
        "json": {
            "error": {
                "@Message.ExtendedInfo": [
                    {
                        "@odata.type": "#Message.v1_0_8.Message",
                        "Message": "The resource at the URI /redfish/v1/AccountService/Accounts/7 was not found.",
                        "MessageArgs": [
                            "/redfish/v1/AccountService/Accounts/7"
                        ],
                        "MessageId": "Base.1.5.ResourceMissingAtURI",
                        "Resolution": "Place a valid resource at the URI or correct the URI and resubmit the request.",
                        "Severity": "Critical"
                    }
                ],
                "code": "Base.1.5.ResourceMissingAtURI",
                "message": "The resource at the URI /redfish/v1/AccountService/Accounts/7 was not found."
            }
        },
        "msg": "HTTP Error 404: Not Found",
        "odata_version": "4.0",
        "redirected": false,
        "server": "AMI MegaRAC Redfish Service",
        "status": 404,
        "url": "https://[2607:f160:10:9073:ce:406:0:1000]/redfish/v1/AccountService/Accounts/7"
    }
}

PLAY RECAP ************************************************************************************************************************************
rchltxfb-93180012-rz-le0trtn-001 : ok=18   changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0

(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$

```
## Passed test, all worked as expected


