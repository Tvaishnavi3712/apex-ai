# ZT .45 BMC firmware validation
# Redfish Functional Testing MEAKV-648-655,793
# 11/1/23 James Patchett

## Target Controller Rchltxfe-c000000-001
Controller-0 iLO 2607:f160:a:d02e:cd:fe0::8000 
Controller-1 iLO 2607:f160:a:d02e:cd:fe0::8001
Worker-0 iLO 2607:f160:a:d02e:cd:fe0::8002 
OAM 2607:f160:0:3043:cd:290:0:10

## Target Subcloud welktxef-d931887-021 (currently on controller 2607:f160:0:3049:cd:290:0:10 )
OAM 2607:f160:10:9249:ce:40a:0:f409
BMC 2607:f160:10:9249:ce:40a:0:e015

ipmitool -I lanplus -U XXXXXX -P XXXXXX -H 2607:f160:10:9249:ce:40a:0:e015 sol activate

## Subcloud welktxef-d931887-021

## MEAKV-648
## Check version of BIOS 
```log
[XXXXXX@vcpe-jumpserver wra-testing]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/UpdateService/FirmwareInventory/BIOS | jq .
{
  "@odata.context": "/redfish/v1/$metadata#SoftwareInventory.SoftwareInventory",
  "@odata.etag": "\"1698794919\"",
  "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/BIOS",
  "@odata.type": "#SoftwareInventory.v1_2_3.SoftwareInventory",
  "Id": "BIOS",
  "Name": "BIOS",
  "Updateable": true,
  "Version": "0.23"
}
[XXXXXX@vcpe-jumpserver wra-testing]$

```

## Check version of BMC

```log
[XXXXXX@vcpe-jumpserver wra-testing]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/UpdateService/FirmwareInventory/BMC | jq .
{
  "@odata.context": "/redfish/v1/$metadata#SoftwareInventory.SoftwareInventory",
  "@odata.etag": "\"1698793584\"",
  "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/BMC",
  "@odata.type": "#SoftwareInventory.v1_2_3.SoftwareInventory",
  "Id": "BMC",
  "Name": "BMC",
  "Updateable": true,
  "Version": "0.45.00"
}
[XXXXXX@vcpe-jumpserver wra-testing]$
```

## MEAKV-649
## set hostname with ZT_Redfish_tests.yml

```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ ansible-playbook --vault-password-file /tmp/vault-pass -i inventory-fe/rchltxfe-1.yml -e attributes_file=vars/proteus_redfish_attributes.yml -e target="welktxef-d931887-021" --tags hostname ZT_Redfish_tests.yml

PLAY [welktxef-d931887-021] *****************************************************************************************************************************************************************************

TASK [redfish/attributes : what we're setting] **********************************************************************************************************************************************************
ok: [welktxef-d931887-021] => {
    "set_attr_item": {
        "attribute": "HostName",
        "new_value": "newhostname2",
        "path": "/redfish/v1/Systems/Self"
    }
}

TASK [redfish/attributes : Setting HostName] ************************************************************************************************************************************************************
ok: [welktxef-d931887-021 -> localhost]

TASK [redfish/attributes : debug] ***********************************************************************************************************************************************************************
ok: [welktxef-d931887-021] => {
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
        "date": "Wed, 01 Nov 2023 17:55:27 GMT",
        "elapsed": 2,
        "etag": "\"1698861327\"",
        "failed": false,
        "msg": "OK (unknown bytes)",
        "odata_version": "4.0",
        "redirected": false,
        "server": "AMI MegaRAC Redfish Service",
        "status": 204,
        "url": "https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Systems/Self"
    }
}

TASK [redfish/attributes : set_fact] ********************************************************************************************************************************************************************
ok: [welktxef-d931887-021]

TASK [redfish/attributes : sleep if needed] *************************************************************************************************************************************************************
ok: [welktxef-d931887-021 -> localhost]
included: /home/XXXXXX/richardson/playbooks/vcp-fe-ib-automation/roles/redfish/attributes/tasks/check_attribute.yml for welktxef-d931887-021

TASK [redfish/attributes : what is currently verified] **************************************************************************************************************************************************
ok: [welktxef-d931887-021] => {
    "msg": "Sending GET to /redfish/v1/Systems/Self and query the returned json for HostName. Value shall be newhostname2"
}

TASK [redfish/attributes : Checking HostName at /redfish/v1/Systems/Self] *******************************************************************************************************************************
ok: [welktxef-d931887-021 -> localhost]

TASK [redfish/attributes : what we're setting] **********************************************************************************************************************************************************
ok: [welktxef-d931887-021] => {
    "set_attr_item": {
        "attribute": "HostName",
        "new_value": "welktxef-d931887-021",
        "path": "/redfish/v1/Systems/Self"
    }
}

TASK [redfish/attributes : Setting HostName] ************************************************************************************************************************************************************
ok: [welktxef-d931887-021 -> localhost]

TASK [redfish/attributes : debug] ***********************************************************************************************************************************************************************
ok: [welktxef-d931887-021] => {
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
        "date": "Wed, 01 Nov 2023 17:56:39 GMT",
        "elapsed": 6,
        "etag": "\"1698861399\"",
        "failed": false,
        "msg": "OK (unknown bytes)",
        "odata_version": "4.0",
        "redirected": false,
        "server": "AMI MegaRAC Redfish Service",
        "status": 204,
        "url": "https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Systems/Self"
    }
}

TASK [redfish/attributes : set_fact] ********************************************************************************************************************************************************************
ok: [welktxef-d931887-021]
included: /home/XXXXXX/richardson/playbooks/vcp-fe-ib-automation/roles/redfish/attributes/tasks/check_attribute.yml for welktxef-d931887-021

TASK [redfish/attributes : what is currently verified] **************************************************************************************************************************************************
ok: [welktxef-d931887-021] => {
    "msg": "Sending GET to /redfish/v1/Systems/Self and query the returned json for HostName. Value shall be welktxef-d931887-021"
}

TASK [redfish/attributes : Checking HostName at /redfish/v1/Systems/Self] *******************************************************************************************************************************
ok: [welktxef-d931887-021 -> localhost]

PLAY RECAP **********************************************************************************************************************************************************************************************
welktxef-d931887-021       : ok=15   changed=0    unreachable=0    failed=0    skipped=5    rescued=0    ignored=0

(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$
```

## MEAKV-650
## set static DNS servers via api

## check Current

```log
[XXXXXX@vcpe-jumpserver wra-testing]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Managers/Self/EthernetInterfaces/eth0 | jq .StaticNameServers
[
  "2607:f160:10:4409:ce:103:0:5",
  "2607:f160:10:4409:ce:103:0:6",
  "::"
]
[XXXXXX@vcpe-jumpserver wra-testing]$

```

## Set to DNS servers to different address to confirm it changes... with ZT_Redfish_tests.yml
## changed IPs in GUI of BMC... 9 and 10 in  now
```log
[XXXXXX@vcpe-jumpserver wra-testing]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Managers/Self/EthernetInterfaces/eth0 | jq .StaticNameServers
[
  "2607:f160:10:4409:ce:103:0:9",
  "2607:f160:10:4409:ce:103:0:10",
  "::"
]
[XXXXXX@vcpe-jumpserver wra-testing]$

(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ ansible-playbook --vault-password-file /tmp/vault-pass -i inventory-fe/rchltxfe-1.yml -e attributes_file=vars/proteus_redfish_attributes.yml -e target="welktxef-d931887-021" --tags dns ZT_Redfish_tests.yml

PLAY [welktxef-d931887-021] *****************************************************************************************************************************************************************************
included: /home/XXXXXX/richardson/playbooks/vcp-fe-ib-automation/roles/redfish/attributes/tasks/set_attribute.yml for welktxef-d931887-021 => (item={'path': '/redfish/v1/Managers/Self/EthernetInterfaces/eth0', 'attribute': 'StaticNameServers', 'new_value': ['2607:f160:10:4409:ce:103:0:5', '2607:f160:10:4409:ce:103:0:6'], 'expected_response': 202, 'expected_value': ['2607:f160:10:4409:ce:103:0:5', '2607:f160:10:4409:ce:103:0:6', '::']})

TASK [redfish/attributes : what we're setting] **********************************************************************************************************************************************************
ok: [welktxef-d931887-021] => {
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

TASK [redfish/attributes : Setting StaticNameServers] ***************************************************************************************************************************************************
ok: [welktxef-d931887-021 -> localhost]

TASK [redfish/attributes : debug] ***********************************************************************************************************************************************************************
ok: [welktxef-d931887-021] => {
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
        "date": "Wed, 01 Nov 2023 18:14:15 GMT",
        "elapsed": 2,
        "etag": "\"1698862442\"",
        "failed": false,
        "json": {
            "@odata.context": "/redfish/v1/$metadata#Task.Task",
            "@odata.id": "/redfish/v1/TaskService/Tasks/3",
            "@odata.type": "#Task.v1_4_2.Task",
            "Description": "Task for EthernetInterface Action",
            "Id": "3",
            "Name": "EthernetInterface Action",
            "TaskState": "New"
        },
        "link": "<http://redfish.dmtf.org/schemas/v1/EthernetInterface.v1_5_1.json>; rel=describedby, <http://redfish.dmtf.org/schemas/v1/Task.v1_4_2.json>, </redfish/v1/TaskService/Tasks/3>; path=",
        "location": "https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/3",
        "msg": "OK (243 bytes)",
        "odata_version": "4.0",
        "prefer": "respond-async; wait=1",
        "redirected": false,
        "server": "AMI MegaRAC Redfish Service",
        "status": 202,
        "url": "https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Managers/Self/EthernetInterfaces/eth0"
    }
}

TASK [redfish/attributes : set_fact] ********************************************************************************************************************************************************************
ok: [welktxef-d931887-021]

TASK [redfish/attributes : sleep if needed] *************************************************************************************************************************************************************
ok: [welktxef-d931887-021 -> localhost]
included: /home/XXXXXX/richardson/playbooks/vcp-fe-ib-automation/roles/redfish/attributes/tasks/check_attribute.yml for welktxef-d931887-021

TASK [redfish/attributes : what is currently verified] **************************************************************************************************************************************************
ok: [welktxef-d931887-021] => {
    "msg": "Sending GET to /redfish/v1/Managers/Self/EthernetInterfaces/eth0 and query the returned json for StaticNameServers. Value shall be ['2607:f160:10:4409:ce:103:0:5', '2607:f160:10:4409:ce:103:0:6', '::']"
}

TASK [redfish/attributes : Checking StaticNameServers at /redfish/v1/Managers/Self/EthernetInterfaces/eth0] *********************************************************************************************
ok: [welktxef-d931887-021 -> localhost]

PLAY RECAP **********************************************************************************************************************************************************************************************
welktxef-d931887-021       : ok=9    changed=0    unreachable=0    failed=0    skipped=2    rescued=0    ignored=0

(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$

```

## Check to see if dns was updated 

```log
[XXXXXX@vcpe-jumpserver wra-testing]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Managers/Self/EthernetInterfaces/eth0 | jq .StaticNameServers
[
  "2607:f160:10:4409:ce:103:0:5",
  "2607:f160:10:4409:ce:103:0:6",
  "::"
]
[XXXXXX@vcpe-jumpserver wra-testing]$
```

## DNS looks good, moving to next test.

## MEAKV-651
## Set NTP servers

## check exiting values

```log
[XXXXXX@vcpe-jumpserver wra-testing]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Managers/Self/NetworkProtocol | jq .NTP
{
  "NTPServers": [
    "2607:f160:10:9200::a",
    "2607:f160:10:9200::b"
  ],
  "Port": 123,
  "ProtocolEnabled": false
}
[XXXXXX@vcpe-jumpserver wra-testing]$
```

## Changing values in BMC UI

## checking values again with wrong server addresses

```log
[XXXXXX@vcpe-jumpserver wra-testing]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Managers/Self/NetworkProtocol | jq .NTP
{
  "NTPServers": [
    "2607:f160:10:9200::c",
    "2607:f160:10:9200::d"
  ],
  "Port": 123,
  "ProtocolEnabled": true
}
[XXXXXX@vcpe-jumpserver wra-testing]$

```


## Now run ZT_Redfish_tests.yml ansible script to set back to correct servers
## Set ntp

```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ ansible-playbook --vault-password-file /tmp/vault-pass -i inventory-fe/rchltxfe-1.yml -e attributes_file=vars/proteus_redfish_attributes.yml -e target="welktxef-d931887-021" --tags ntp ZT_Redfish_tests.yml

PLAY [welktxef-d931887-021] *****************************************************************************************************************************************************************************

TASK [redfish/attributes : what we're setting] **********************************************************************************************************************************************************
ok: [welktxef-d931887-021] => {
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

TASK [redfish/attributes : Setting NTP] *****************************************************************************************************************************************************************
ok: [welktxef-d931887-021 -> localhost]

TASK [redfish/attributes : debug] ***********************************************************************************************************************************************************************
ok: [welktxef-d931887-021] => {
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
        "date": "Fri, 03 Nov 2023 04:40:23 GMT",
        "elapsed": 4,
        "etag": "\"1698862530\"",
        "failed": false,
        "msg": "OK (unknown bytes)",
        "odata_version": "4.0",
        "redirected": false,
        "server": "AMI MegaRAC Redfish Service",
        "status": 204,
        "url": "https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Managers/Self/NetworkProtocol"
    }
}

TASK [redfish/attributes : set_fact] ********************************************************************************************************************************************************************
ok: [welktxef-d931887-021]

TASK [redfish/attributes : sleep if needed] *************************************************************************************************************************************************************
ok: [welktxef-d931887-021 -> localhost]
included: /home/XXXXXX/richardson/playbooks/vcp-fe-ib-automation/roles/redfish/attributes/tasks/check_attribute.yml for welktxef-d931887-021

TASK [redfish/attributes : what is currently verified] **************************************************************************************************************************************************
ok: [welktxef-d931887-021] => {
    "msg": "Sending GET to /redfish/v1/Managers/Self/NetworkProtocol and query the returned json for NTP.NTPServers. Value shall be ['2607:f160:10:9200::a', '2607:f160:10:8200::a']"
}

TASK [redfish/attributes : Checking NTP.NTPServers at /redfish/v1/Managers/Self/NetworkProtocol] ********************************************************************************************************
ok: [welktxef-d931887-021 -> localhost]

PLAY RECAP **********************************************************************************************************************************************************************************************
welktxef-d931887-021       : ok=8    changed=0    unreachable=0    failed=0    skipped=2    rescued=0    ignored=0

(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$
```

## verify settings took with a query to redfish db

```log
[XXXXXX@vcpe-jumpserver wra-testing]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Managers/Self/NetworkProtocol | jq .NTP
{
  "NTPServers": [
    "2607:f160:10:9200::a",
    "2607:f160:10:8200::a"
  ],
  "Port": 123,
  "ProtocolEnabled": true
}
[XXXXXX@vcpe-jumpserver wra-testing]$

```
## success, next test

## MEAKV-652
## delete subscription then put it back

## redfish DB reset command, will result in deleting exisiting subscriptions

```sh
curl -sk -u XXXXXX:XXXXXX -X POST "https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Managers/Self/Actions/Oem/AMIManager.RedfishDBReset" -d '{"RedfishDBResetType": "ResetAll"}' -H "Content-Type: application/json" | python3 -m json.tool
```
## check to see if an subscription exists

```log
[XXXXXX@vcpe-jumpserver wra-testing]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/EventService/Subscriptions | jq .
{
  "@odata.context": "/redfish/v1/$metadata#EventDestinationCollection.EventDestinationCollection",
  "@odata.etag": "\"1698865456\"",
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
[XXXXXX@vcpe-jumpserver wra-testing]$
```

## delete the subscription by reseting the redfish DB

```log
[XXXXXX@vcpe-jumpserver wra-testing]$ curl -sk -u XXXXXX:XXXXXX -X POST "https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Managers/Self/Actions/Oem/AMIManager.RedfishDBReset" -d '{"RedfishDBResetType": "ResetAll"}' -H "Content-Type: application/json" | python3 -m json.tool
{
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.id": "/redfish/v1/TaskService/Tasks/1",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for RedfishDBReset Task",
    "Id": "1",
    "Name": "RedfishDBReset Task",
    "TaskState": "New"
}
[XXXXXX@vcpe-jumpserver wra-testing]$ sleep 120
[XXXXXX@vcpe-jumpserver wra-testing]$

```

## check that subscription is deleted

```log
[XXXXXX@vcpe-jumpserver wra-testing]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/EventService/Subscriptions | jq .
{
  "@odata.context": "/redfish/v1/$metadata#EventDestinationCollection.EventDestinationCollection",
  "@odata.etag": "\"1698865639\"",
  "@odata.id": "/redfish/v1/EventService/Subscriptions",
  "@odata.type": "#EventDestinationCollection.EventDestinationCollection",
  "Description": "Collection for Event Subscriptions",
  "Members": [],
  "Members@odata.count": 0,
  "Name": "Event Subscriptions Collection"
}
[XXXXXX@vcpe-jumpserver wra-testing]$
```

## Now set the subscription URL to bmc

```sh
export IP=2607:f160:10:9249:ce:40a:0:e015
curl -i -s -u XXXXXX:XXXXXX -H "Content-Type: application/json" -k -X POST -n -d '
{
"Context": "Subscription_VCMP-1",
"Destination": "https://vcpme-rch-feocp-redfishalerts.mon.vzwops.com/redfish",
"Protocol": "Redfish"
}' https://[${IP}]/redfish/v1/EventService/Subscriptions

```

```log
[XXXXXX@vcpe-jumpserver wra-testing]$ curl -i -s -u XXXXXX:XXXXXX -H "Content-Type: application/json" -k -X POST -n -d '
{
"Context": "Subscription_VCMP-1",
"Destination": "https://vcpme-rch-feocp-redfishalerts.mon.vzwops.com/redfish",
"Protocol": "Redfish"
}' https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/EventService/Subscriptions
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
ETag: "1698867353"
Content-Type: application/json; charset=UTF-8
OData-Version: 4.0
Content-Length: 612
Date: Wed, 01 Nov 2023 19:35:54 GMT

{"@odata.context":"/redfish/v1/$metadata#EventDestination.EventDestination","@odata.etag":"\"1698867353\"","@odata.id":"/redfish/v1/EventService/Subscriptions","@odata.type":"#EventDestination.v1_6_0.EventDestination","Context":"Subscription_VCMP-1","DeliveryRetryPolicy":"TerminateAfterRetries","Description":"Event Subscription","Destination":"https://vcpme-rch-feocp-redfishalerts.mon.vzwops.com/redfish","EventFormatType":"Event","Id":1,"Name":"Subscription 1","Protocol":"Redfish","Status":{"Health":"OK","HealthRollup":"OK","State":"Enabled"},"SubordinateResources":false,"SubscriptionType":"RedfishEvent"}[XXXXXX@vcpe-jumpserver wra-testing]$
```

## verify subscription is there

```log
[XXXXXX@vcpe-jumpserver wra-testing]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/EventService/Subscriptions | jq .
{
  "@odata.context": "/redfish/v1/$metadata#EventDestinationCollection.EventDestinationCollection",
  "@odata.etag": "\"1698867353\"",
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
[XXXXXX@vcpe-jumpserver wra-testing]$
[XXXXXX@vcpe-jumpserver wra-testing]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/EventService/Subscriptions/1 | jq .
{
  "@odata.context": "/redfish/v1/$metadata#EventDestination.EventDestination",
  "@odata.etag": "\"1698867353\"",
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
[XXXXXX@vcpe-jumpserver wra-testing]$
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

```log
[XXXXXX@vcpe-jumpserver ~]$ curl  -L -w "%{http_code} %{url_effective}\\n" -ku XXXXXX:XXXXXX -H "Content-Type: application/json" -d '{"MessageId" : "EventLog.1.0.ResourceUpdated"}' -X POST https://[${IP}]/redfish/v1/EventService/Actions/EventService.SubmitTestEvent
{"@odata.context":"/redfish/v1/$metadata#Task.Task","@odata.id":"/redfish/v1/TaskService/Tasks/1017","@odata.type":"#Task.v1_4_2.Task","Description":"Task for EventService SubmitTestEvent Action","Id":"1017","Name":"EventService SubmitTestEvent Action","TaskState":"New"}202 https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/EventService/Actions/EventService.SubmitTestEvent
[XXXXXX@vcpe-jumpserver ~]$ curl  -L -w "%{http_code} %{url_effective}\\n" -ku XXXXXX:XXXXXX -H "Content-Type: application/json" -d '{"MessageId" : "EventLog.1.0.ResourceUpdated"}' -X POST https://[${IP}]/redfish/v1/EventService/Actions/EventService.SubmitTestEvent
{"@odata.context":"/redfish/v1/$metadata#Task.Task","@odata.id":"/redfish/v1/TaskService/Tasks/1018","@odata.type":"#Task.v1_4_2.Task","Description":"Task for EventService SubmitTestEvent Action","Id":"1018","Name":"EventService SubmitTestEvent Action","TaskState":"New"}202 https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/EventService/Actions/EventService.SubmitTestEvent
[XXXXXX@vcpe-jumpserver ~]$ curl  -L -w "%{http_code} %{url_effective}\\n" -ku XXXXXX:XXXXXX -H "Content-Type: application/json" -d '{"MessageId" : "EventLog.1.0.ResourceUpdated"}' -X POST https://[${IP}]/redfish/v1/EventService/Actions/EventService.SubmitTestEvent
{"@odata.context":"/redfish/v1/$metadata#Task.Task","@odata.id":"/redfish/v1/TaskService/Tasks/1019","@odata.type":"#Task.v1_4_2.Task","Description":"Task for EventService SubmitTestEvent Action","Id":"1019","Name":"EventService SubmitTestEvent Action","TaskState":"New"}202 https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/EventService/Actions/EventService.SubmitTestEvent
[XXXXXX@vcpe-jumpserver ~]$ curl  -L -w "%{http_code} %{url_effective}\\n" -ku XXXXXX:XXXXXX -H "Content-Type: application/json" -d '{"MessageId" : "EventLog.1.0.ResourceUpdated"}' -X POST https://[${IP}]/redfish/v1/EventService/Actions/EventService.SubmitTestEvent
{"@odata.context":"/redfish/v1/$metadata#Task.Task","@odata.id":"/redfish/v1/TaskService/Tasks/1020","@odata.type":"#Task.v1_4_2.Task","Description":"Task for EventService SubmitTestEvent Action","Id":"1020","Name":"EventService SubmitTestEvent Action","TaskState":"New"}202 https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/EventService/Actions/EventService.SubmitTestEvent
[XXXXXX@vcpe-jumpserver ~]$ curl  -L -w "%{http_code} %{url_effective}\\n" -ku XXXXXX:XXXXXX -H "Content-Type: application/json" -d '{"MessageId" : "EventLog.1.0.ResourceUpdated"}' -X POST https://[${IP}]/redfish/v1/EventService/Actions/EventService.SubmitTestEvent
{"@odata.context":"/redfish/v1/$metadata#Task.Task","@odata.id":"/redfish/v1/TaskService/Tasks/1021","@odata.type":"#Task.v1_4_2.Task","Description":"Task for EventService SubmitTestEvent Action","Id":"1021","Name":"EventService SubmitTestEvent Action","TaskState":"New"}202 https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/EventService/Actions/EventService.SubmitTestEvent
[XXXXXX@vcpe-jumpserver ~]$
```

## Check vcmp tools if alerts made it to them

### alerts are coming into elastic with VCMP tools, I have added screen shots and will upload to test case ### for evidence... queries with new vcmp tools after the rebulid is not working yet.


## Redfish Event URL has been set and is good

## MEAKV-654 
## Redfish add user, change password, then delete user

```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ ansible-playbook --vault-password-file /tmp/vault-pass -i inventory-fe/rchltxfe-1.yml -e attributes_file=vars/proteus_redfish_attributes.yml -e target="welktxef-931887-rz-le2pts6-021" --tags user ZT_Redfish_tests.yml

PLAY [welktxef-931887-rz-le2pts6-021] *************************************************************************************

TASK [redfish/users : Generate request body] ******************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [redfish/users : Add user] *******************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [redfish/users : debug] **********************************************************************************************
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
        "content_length": "577",
        "content_type": "application/json; charset=UTF-8",
        "cookies": {},
        "cookies_string": "",
        "date": "Fri, 03 Nov 2023 17:52:08 GMT",
        "elapsed": 4,
        "etag": "\"1699033926\"",
        "failed": false,
        "json": {
            "@odata.context": "/redfish/v1/$metadata#ManagerAccount.ManagerAccount",
            "@odata.etag": "\"1699033926\"",
            "@odata.id": "/redfish/v1/AccountService/Accounts",
            "@odata.type": "#ManagerAccount.v1_3_1.ManagerAccount",
            "AccountTypes": [
                "Redfish"
            ],
            "Certificates": {
                "@odata.id": "/redfish/v1/AccountService/Accounts/11/Certificates"
            },
            "Description": "Ansible user",
            "Enabled": true,
            "Id": "11",
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
        "location": "https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/AccountService/Accounts/11",
        "msg": "OK (577 bytes)",
        "odata_version": "4.0",
        "redirected": false,
        "server": "AMI MegaRAC Redfish Service",
        "status": 201,
        "url": "https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/AccountService/Accounts"
    }
}

TASK [redfish/users : Storing location of new user] ***********************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [redfish/users : sleep if needed] ************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [redfish/users : get new user with its own credentials] **************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [redfish/users : debug] **********************************************************************************************
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
        "content_length": "581",
        "content_type": "application/json; charset=UTF-8",
        "cookies": {},
        "cookies_string": "",
        "date": "Fri, 03 Nov 2023 17:52:39 GMT",
        "elapsed": 0,
        "etag": "\"1699033926\"",
        "failed": false,
        "json": {
            "@odata.context": "/redfish/v1/$metadata#ManagerAccount.ManagerAccount",
            "@odata.etag": "\"1699033926\"",
            "@odata.id": "/redfish/v1/AccountService/Accounts/11",
            "@odata.type": "#ManagerAccount.v1_3_1.ManagerAccount",
            "AccountTypes": [
                "Redfish"
            ],
            "Certificates": {
                "@odata.id": "/redfish/v1/AccountService/Accounts/11/Certificates"
            },
            "Description": "Ansible user",
            "Enabled": true,
            "Id": "11",
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
        "link": "<http://redfish.dmtf.org/schemas/v1/ManagerAccount.v1_3_1.json>; rel=describedby, </redfish/v1/AccountService/Roles/XXXXXX>; path=/Links/Role, </redfish/v1/AccountService/Accounts/11/Certificates>; path=/Certificates",
        "msg": "OK (581 bytes)",
        "odata_version": "4.0",
        "redirected": false,
        "server": "AMI MegaRAC Redfish Service",
        "status": 200,
        "url": "https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/AccountService/Accounts/11"
    }
}

TASK [redfish/users : Generate request body] ******************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [redfish/users : Change password] ************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [redfish/users : debug] **********************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "response": {
        "allow": "GET, PATCH, DELETE",
        "changed": false,
        "connection": "close",
        "cookies": {},
        "cookies_string": "",
        "date": "Fri, 03 Nov 2023 17:52:48 GMT",
        "elapsed": 8,
        "failed": false,
        "msg": "OK (unknown bytes)",
        "redirected": false,
        "server": "AMI MegaRAC Redfish Service",
        "status": 204,
        "url": "https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/AccountService/Accounts/11"
    }
}

TASK [redfish/users : sleep if needed] ************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [redfish/users : Get new user with its own (updated) credentials] ****************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [redfish/users : debug] **********************************************************************************************
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
        "content_length": "581",
        "content_type": "application/json; charset=UTF-8",
        "cookies": {},
        "cookies_string": "",
        "date": "Fri, 03 Nov 2023 17:53:19 GMT",
        "elapsed": 0,
        "etag": "\"1699033960\"",
        "failed": false,
        "json": {
            "@odata.context": "/redfish/v1/$metadata#ManagerAccount.ManagerAccount",
            "@odata.etag": "\"1699033960\"",
            "@odata.id": "/redfish/v1/AccountService/Accounts/11",
            "@odata.type": "#ManagerAccount.v1_3_1.ManagerAccount",
            "AccountTypes": [
                "Redfish"
            ],
            "Certificates": {
                "@odata.id": "/redfish/v1/AccountService/Accounts/11/Certificates"
            },
            "Description": "Ansible user",
            "Enabled": true,
            "Id": "11",
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
        "link": "<http://redfish.dmtf.org/schemas/v1/ManagerAccount.v1_3_1.json>; rel=describedby, </redfish/v1/AccountService/Roles/XXXXXX>; path=/Links/Role, </redfish/v1/AccountService/Accounts/11/Certificates>; path=/Certificates",
        "msg": "OK (581 bytes)",
        "odata_version": "4.0",
        "redirected": false,
        "server": "AMI MegaRAC Redfish Service",
        "status": 200,
        "url": "https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/AccountService/Accounts/11"
    }
}

TASK [redfish/users : Deleting user] **************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [redfish/users : debug] **********************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "response": {
        "allow": "GET, PATCH, DELETE",
        "changed": false,
        "connection": "close",
        "cookies": {},
        "cookies_string": "",
        "date": "Fri, 03 Nov 2023 17:53:24 GMT",
        "elapsed": 5,
        "failed": false,
        "msg": "OK (unknown bytes)",
        "redirected": false,
        "server": "AMI MegaRAC Redfish Service",
        "status": 204,
        "url": "https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/AccountService/Accounts/11"
    }
}

TASK [redfish/users : sleep if needed] ************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [redfish/users : Check if user is gone] ******************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [redfish/users : debug] **********************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "response": {
        "changed": false,
        "connection": "close",
        "content_length": "515",
        "content_type": "application/json; charset=UTF-8",
        "date": "Fri, 03 Nov 2023 17:53:55 GMT",
        "elapsed": 0,
        "failed": false,
        "json": {
            "error": {
                "@Message.ExtendedInfo": [
                    {
                        "@odata.type": "#Message.v1_0_8.Message",
                        "Message": "The resource at the URI /redfish/v1/AccountService/Accounts/11 was not found.",
                        "MessageArgs": [
                            "/redfish/v1/AccountService/Accounts/11"
                        ],
                        "MessageId": "Base.1.5.ResourceMissingAtURI",
                        "Resolution": "Place a valid resource at the URI or correct the URI and resubmit the request.",
                        "Severity": "Critical"
                    }
                ],
                "code": "Base.1.5.ResourceMissingAtURI",
                "message": "The resource at the URI /redfish/v1/AccountService/Accounts/11 was not found."
            }
        },
        "msg": "HTTP Error 404: Not Found",
        "odata_version": "4.0",
        "redirected": false,
        "server": "AMI MegaRAC Redfish Service",
        "status": 404,
        "url": "https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/AccountService/Accounts/11"
    }
}

PLAY RECAP ****************************************************************************************************************
welktxef-931887-rz-le2pts6-021 : ok=18   changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0

(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$

```
## Passed test, all worked as expected


