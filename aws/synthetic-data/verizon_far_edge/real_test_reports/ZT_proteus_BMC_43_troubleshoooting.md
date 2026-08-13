# ZT .43 BMC firmware validation
# 8/25/23 James Patchett

## Build and setup of environment

## Target Controller Rchltxfe-c000000-001
Controller-0 iLO 2607:f160:a:d02e:cd:fe0::8000 
Controller-1 iLO 2607:f160:a:d02e:cd:fe0::8001
Worker-0 iLO 2607:f160:a:d02e:cd:fe0::8002 
OAM 2607:f160:0:3043:cd:290:0:10



## Target Subcloud welktxef-d931887-021 (currently on controller 2607:f160:0:3049:cd:290:0:10 )
iLO 2607:f160:10:9249:ce:40a:0:e015
OAM 2607:f160:10:9249:ce:40a:0:f409

ipmitool -I lanplus -U XXXXXX -P XXXXXX -H 2607:f160:10:9249:ce:40a:0:e015 sol activate

### working issues with ZT on redfish

```log

[XXXXXX@vcpe-jumpserver ~]$ curl -k -w "\\n%{http_code} %{url_effective}\\n" -u XXXXXX:XXXXXX -H "Content-Type: application/json" -d '{"Attributes": {"PMS012": "Disable"}}' -X PATCH https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Systems/Self/Bios/SD
{"error":{"@Message.ExtendedInfo":[{"@odata.type":"#Message.v1_0_8.Message","Message":"The requested operation is temporarily unavailable since Host System Reboot might be in progress or Host might be in Bios Setup or Redfish Inventory processing might be in progress. Please try after sometime.","MessageId":"Ami.1.0.ServiceTemporarilyUnavailableDueToHostBooting","Resolution":"Retry after some time.","Severity":"Critical"}],"code":"Ami.1.0.ServiceTemporarilyUnavailableDueToHostBooting","message":"The requested operation is temporarily unavailable since Host System Reboot might be in progress or Host might be in Bios Setup or Redfish Inventory processing might be in progress. Please try after sometime."}}
503 https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Systems/Self/Bios/SD
[XXXXXX@vcpe-jumpserver ~]$ curl -sk -u XXXXXX:XXXXXX -X POST "https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Managers/Self/Actions/Oem/AMIManager.RedfishDBReset" -d '{"RedfishDBResetType": "ResetAll"}' -H "Content-Type: application/json" | python3 -m json.tool
{
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.id": "/redfish/v1/TaskService/Tasks/1",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for RedfishDBReset Task",
    "Id": "1",
    "Name": "RedfishDBReset Task",
    "TaskState": "New"
}
[XXXXXX@vcpe-jumpserver ~]$

[XXXXXX@vcpe-jumpserver ~]$ curl -k -w "\\n%{http_code} %{url_effective}\\n" -u XXXXXX:XXXXXX -H "Content-Type: application/json" -d '{"Attributes": {"PMS012": "Disable"}}' -X PATCH https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Systems/Self/Bios/SD

204 https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Systems/Self/Bios/SD
[XXXXXX@vcpe-jumpserver ~]$
[XXXXXX@vcpe-jumpserver ~]$ curl -k -w "\\n%{http_code} %{url_effective}\\n" -u XXXXXX:XXXXXX -H "Content-Type: application/json" -d '{"Attributes": {"PMS012": "Enable"}}' -X PATCH https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Systems/Self/Bios/SD

204 https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Systems/Self/Bios/SD
[XXXXXX@vcpe-jumpserver ~]$



```

