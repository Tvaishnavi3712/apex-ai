# ZT Proteus .46 BMC firmware validation
# ZT Proteus BIOS .23
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


### Samsung SSD Tempature issue in BMC
### Drive types SAMSUNG SSD PM9A3 (MZQL21T9HCJR-00A07)
### In .45 BMC Samsung tempature could not be read, which causes fans to spike to 100% utiliztion
### We try to validate we can reproduce issue in lab, then show that new .46 BMC does not have issue with this drive type

### Current system is on .46 BMC, need to install .45 and see if we can spot the temp missing for Samsung ssd.

```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 ZT-Proteus-BMC-update-Redfish-v0.45.00-x86_64_20231017]$ ./update-bmc-redfish-python*.sh 2607:f160:10:80b1:ce:40a:0:e008 XXXXXX XXXXXX ./log-36.txt
===============================================================
          ZT BMC Update for Proteus and Triton
     update-bmc-redfish-python-v08-20231017.sh
                    10/17/2023
                     Ver 0.08
===============================================================

2024-01-16-17:49:49  Check if IP address is valid
2024-01-16-17:49:49  IPv6 IP detected
2024-01-16-17:49:50  2607:f160:10:80b1:ce:40a:0:e008 is a valid IP
2024-01-16-17:49:50  IPv6 Address is 2607:f160:10:80b1:ce:40a:0:e008
2024-01-16-17:49:52  Redfish Creditials are correct, continue update
2024-01-16-17:49:52  Check if right version of python3 is installed
2024-01-16-17:49:52  Python3 is installed, continue update
2024-01-16-17:49:55  Model name is Proteus
2024-01-16-17:49:55  Product is Proteus or Force option is slected, ok to proceed
2024-01-16-17:49:55  System Serial is 207736270043
2024-01-16-17:49:55  BMC current version is 0.46.00
{"@odata.context":"/redfish/v1/$metadata#Task.Task","@odata.id":"/redfish/v1/TaskService/Tasks/21","@odata.type":"#Task.v1_4_2.Task","Description":"Task for Manager Reset","Id":"21","Name":"Manager Reset","TaskState":"New"}202 https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/Managers/Self/Actions/Manager.Reset
2024-01-16-17:49:56  Restting BMC Waiting 240 seconds for retart
2024-01-16-17:53:57  Reset AMIManager.RedfishDBReset/ Process will take 3 minutes
{
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.id": "/redfish/v1/TaskService/Tasks/1",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for RedfishDBReset Task",
    "Id": "1",
    "Name": "RedfishDBReset Task",
    "TaskState": "New"
}
20240116_180822 GET: https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/TaskService/Tasks/2
20240116_180823 HTTP: 200
20240116_180823 JSON: {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1705449564\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/2",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "2",
    "Messages": [
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Task Redfish:TaskService:Tasks:2 has stopped due to an exception condition.",
            "MessageArgs": [
                "Redfish:TaskService:Tasks:2"
            ],
            "MessageId": "Task.1.0.Exception",
            "Resolution": "None",
            "Severity": "WARNING"
        },
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "The action /redfish/v1/UpdateService/upload is not supported by the resource.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "Base.1.5.ActionNotSupported",
            "Resolution": "The action supplied cannot be resubmitted to the implementation.  Perhaps the action was invalid, the wrong resource was the target or the implementation documentation may be of assistance.",
            "Severity": "Critical"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 0,
    "TaskState": "Exception",
    "TaskStatus": "Warning"
}
20240116_180823 Update status (monitor, running) : Exception (Percent complete = 0)
20240116_180823 ERROR: Update completes with unexpected status [Exception]
20240116_180823 Checking task status on /redfish/v1/TaskService/Tasks/2
20240116_180823 GET: https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/TaskService/Tasks/2
20240116_180823 HTTP: 200
20240116_180823 JSON: {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1705449564\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/2",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "2",
    "Messages": [
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Task Redfish:TaskService:Tasks:2 has stopped due to an exception condition.",
            "MessageArgs": [
                "Redfish:TaskService:Tasks:2"
            ],
            "MessageId": "Task.1.0.Exception",
            "Resolution": "None",
            "Severity": "WARNING"
        },
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "The action /redfish/v1/UpdateService/upload is not supported by the resource.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "Base.1.5.ActionNotSupported",
            "Resolution": "The action supplied cannot be resubmitted to the implementation.  Perhaps the action was invalid, the wrong resource was the target or the implementation documentation may be of assistance.",
            "Severity": "Critical"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 0,
    "TaskState": "Exception",
    "TaskStatus": "Warning"
}
20240116_180823 Task /redfish/v1/TaskService/Tasks/2  status : 200 Exception (Percent complete = 0)
20240116_180823 Found 2 messages from [/redfish/v1/TaskService/Tasks/2]
20240116_180823 {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1705449564\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/2",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "2",
    "Messages": [
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Task Redfish:TaskService:Tasks:2 has stopped due to an exception condition.",
            "MessageArgs": [
                "Redfish:TaskService:Tasks:2"
            ],
            "MessageId": "Task.1.0.Exception",
            "Resolution": "None",
            "Severity": "WARNING"
        },
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "The action /redfish/v1/UpdateService/upload is not supported by the resource.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "Base.1.5.ActionNotSupported",
            "Resolution": "The action supplied cannot be resubmitted to the implementation.  Perhaps the action was invalid, the wrong resource was the target or the implementation documentation may be of assistance.",
            "Severity": "Critical"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 0,
    "TaskState": "Exception",
    "TaskStatus": "Warning"
}
20240116_180823     Unknown             WARNING     Task Redfish:TaskService:Tasks:2 has stopped due to an exception condition.
20240116_180823     Unknown             Critical    The action /redfish/v1/UpdateService/upload is not supported by the resource.
20240116_180823                         Resolution  The action supplied cannot be resubmitted to the implementation.  Perhaps the action was invalid, the wrong resource was the target or the implementation documentation may be of assistance.
20240116_180823 Checking task status on /redfish/v1/TaskService/Tasks/2
20240116_180823 GET: https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/TaskService/Tasks/2
20240116_180823 HTTP: 200
20240116_180823 JSON: {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1705449564\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/2",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "2",
    "Messages": [
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Task Redfish:TaskService:Tasks:2 has stopped due to an exception condition.",
            "MessageArgs": [
                "Redfish:TaskService:Tasks:2"
            ],
            "MessageId": "Task.1.0.Exception",
            "Resolution": "None",
            "Severity": "WARNING"
        },
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "The action /redfish/v1/UpdateService/upload is not supported by the resource.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "Base.1.5.ActionNotSupported",
            "Resolution": "The action supplied cannot be resubmitted to the implementation.  Perhaps the action was invalid, the wrong resource was the target or the implementation documentation may be of assistance.",
            "Severity": "Critical"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 0,
    "TaskState": "Exception",
    "TaskStatus": "Warning"
}
20240116_180823 Task /redfish/v1/TaskService/Tasks/2  status : 200 Exception (Percent complete = 0)
20240116_180823 Found 2 messages from [/redfish/v1/TaskService/Tasks/2]
20240116_180823 {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1705449564\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/2",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "2",
    "Messages": [
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Task Redfish:TaskService:Tasks:2 has stopped due to an exception condition.",
            "MessageArgs": [
                "Redfish:TaskService:Tasks:2"
            ],
            "MessageId": "Task.1.0.Exception",
            "Resolution": "None",
            "Severity": "WARNING"
        },
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "The action /redfish/v1/UpdateService/upload is not supported by the resource.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "Base.1.5.ActionNotSupported",
            "Resolution": "The action supplied cannot be resubmitted to the implementation.  Perhaps the action was invalid, the wrong resource was the target or the implementation documentation may be of assistance.",
            "Severity": "Critical"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 0,
    "TaskState": "Exception",
    "TaskStatus": "Warning"
}
20240116_180823     Unknown             WARNING     Task Redfish:TaskService:Tasks:2 has stopped due to an exception condition.
20240116_180823     Unknown             Critical    The action /redfish/v1/UpdateService/upload is not supported by the resource.
20240116_180823                         Resolution  The action supplied cannot be resubmitted to the implementation.  Perhaps the action was invalid, the wrong resource was the target or the implementation documentation may be of assistance.
20240116_180823 The FW update did not complete after 1500 seconds
Statistics: starts
datetime,ecode,nerrs,fw_imgfile,fwver_start,fwver_end,fwver_expected,component_type,component_name,component_count,component_updated,bmc_ip,oshost_ip,osping_pre_secs,osping_total_secs,osping_pass,osping_fail,wait_before_update_poll_start,wait_after_poll_complete,poll_time_for_update_start,poll_time_for_update_complete,poll_time_for_post,poll_count_for_post,poll_time_for_version,poll_count_for_version,do_reboot,do_clear_sel_log,total_time,initiate_fwupdate_time,wait_for_update_done_time,iterate_for_post_complete_time,wait_for_version_available_time,wait_for_host_status_time,
20240116_175820,-1,1,v0.45.00.ima,0.46.00,,,BMC,BMC,1,1,[2607:f160:10:80b1:ce:40a:0:e008],,10,120,0,0,60,180,60,1500,0,2,600,2,0,0,603,62,538,0,0,0
Statistics: ends
20240116_180823 ERROR: Process failed
2024-01-16-18:08:23  Final Check
2024-01-16-18:08:24  BMC updated Successfully to 0.45.00
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 ZT-Proteus-BMC-update-Redfish-v0.45.00-x86_64_20231017]$

```

### BMC is now .45 

```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 ZT-Proteus-BMC-update-Redfish-v0.45.00-x86_64_20231017]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[${IP}]/redfish/v1/UpdateService/FirmwareInventory/BMC | jq .
{
  "@odata.context": "/redfish/v1/$metadata#SoftwareInventory.SoftwareInventory",
  "@odata.etag": "\"1705451116\"",
  "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/BMC",
  "@odata.type": "#SoftwareInventory.v1_2_3.SoftwareInventory",
  "Id": "BMC",
  "Name": "BMC",
  "Updateable": true,
  "Version": "0.45.00"
}
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 ZT-Proteus-BMC-update-Redfish-v0.45.00-x86_64_20231017]$
```


### Sensor list 

```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 ZT-Proteus-BMC-update-Redfish-v0.45.00-x86_64_20231017]$ rf_sensor_list.py -u XXXXXX -p XXXXXX -r https://[2607:f160:10:80b1:ce:40a:0:e008]
Chassis 'Computer System Chassis' Status
  Sensor                    | Reading    | Health   | LF       | LC       | LNC      | UNC      | UC       | UF       | PhysicalContext
  State                     | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enable     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 212V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 180W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enable     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 213V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 162W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_V5                    | 4.9984V    | OK       | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | 12.1568V   | OK       | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | 3.3236V    | OK       | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | 1.05156V   | OK       | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  RTC_Voltage               | 3.01V      | OK       | N/A      | 2.289    | N/A      | N/A      | 3.444    | N/A      | VoltageRegulator
  CPU_0_Vcore               | 1.808V     | OK       | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | 1.2232V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | 1.2232V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | -42Cel     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_MARGIN              | 31Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_PROCHOT             | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  PSU_1_TEMP_2              | 45Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_1_TEMP_1              | 26Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  PSU_2_TEMP_2              | 45Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_2_TEMP_1              | 26Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  CPU_0_DIMM_C0             | 39Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_D0             | 38Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_A0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_B0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_G0             | 37Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_H0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_E0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_F0             | 35Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  DIMM_VRABCD_TEMP          | 40Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  DIMM_VREFGH_TEMP          | 37Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  MAX_DIMM_TEMP             | 39Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  PML_WEST_TEMP             | 61Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  PML_LOCAL_TEMP            | 59Cel      | OK       | N/A      | N/A      | N/A      | 80       | 85       | N/A      | Intake
  PML_VDD_TEMP              | 66Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 125      | N/A      | Intake
  PML_EAST_TEMP             | 60Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  SC_1_E810                 | Absent     | N/A      | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SC_2_E810                 | Absent     | N/A      | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SSD_0_TEMP                | 29Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  SSD_1_TEMP                | 30Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  INLET_TEMP_L              | 26Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  INLET_TEMP_R              | 24Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  MB_HSC_TEMP               | 37Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  OUTLET_TEMP_L             | 43Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  OUTLET_TEMP_R             | 39Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  INLET_TEMP_MAX            | 26Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  OUTLET_TEMP_MAX           | 43Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  SYS_PCH_TEMP              | 32Cel      | OK       | N/A      | 5        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_TEMP                | 56Cel      | OK       | N/A      | N/A      | N/A      | 96       | 98       | N/A      | Intake
  SYS_FAN_1A                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_1B                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2A                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2B                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_1_FAN                 | 4000RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_2_FAN                 | 4000RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan

(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 ZT-Proteus-BMC-update-Redfish-v0.45.00-x86_64_20231017]$
```

### SSD looks good on this, however I noticed E810 INTEL cards are not receiving temps, interesting.

```log
 SC_1_E810                 | Absent     | N/A      | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SC_2_E810                 | Absent     | N/A      | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
```

### But fans not 100%

```log
  SYS_FAN_1A                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_1B                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2A                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2B                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_1_FAN                 | 4000RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_2_FAN                 | 4000RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
```

### Going to install other versions of bios and bmc to try and trigger ssd temp failure 


### Installing bios .30
```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 ZT-Proteus-BMC-update-Redfish-v0.45.00-x86_64_20231017]$ rf_sensor_list.py -u XXXXXX -p XXXXXX -r https://[2607:f160:10:80b1:ce:40a:0:e008]
Chassis 'Computer System Chassis' Status
  Sensor                    | Reading    | Health   | LF       | LC       | LNC      | UNC      | UC       | UF       | PhysicalContext
  State                     | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enable     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 212V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 180W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enable     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 213V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 162W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_V5                    | 4.9984V    | OK       | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | 12.1568V   | OK       | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | 3.3236V    | OK       | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | 1.05156V   | OK       | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  RTC_Voltage               | 3.01V      | OK       | N/A      | 2.289    | N/A      | N/A      | 3.444    | N/A      | VoltageRegulator
  CPU_0_Vcore               | 1.808V     | OK       | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | 1.2232V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | 1.2232V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | -42Cel     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_MARGIN              | 31Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_PROCHOT             | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  PSU_1_TEMP_2              | 45Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_1_TEMP_1              | 26Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  PSU_2_TEMP_2              | 45Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_2_TEMP_1              | 26Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  CPU_0_DIMM_C0             | 39Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_D0             | 38Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_A0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_B0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_G0             | 37Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_H0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_E0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_F0             | 35Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  DIMM_VRABCD_TEMP          | 40Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  DIMM_VREFGH_TEMP          | 37Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  MAX_DIMM_TEMP             | 39Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  PML_WEST_TEMP             | 61Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  PML_LOCAL_TEMP            | 59Cel      | OK       | N/A      | N/A      | N/A      | 80       | 85       | N/A      | Intake
  PML_VDD_TEMP              | 66Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 125      | N/A      | Intake
  PML_EAST_TEMP             | 60Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  SC_1_E810                 | Absent     | N/A      | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SC_2_E810                 | Absent     | N/A      | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SSD_0_TEMP                | 29Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  SSD_1_TEMP                | 30Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  INLET_TEMP_L              | 26Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  INLET_TEMP_R              | 24Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  MB_HSC_TEMP               | 37Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  OUTLET_TEMP_L             | 43Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  OUTLET_TEMP_R             | 39Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  INLET_TEMP_MAX            | 26Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  OUTLET_TEMP_MAX           | 43Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  SYS_PCH_TEMP              | 32Cel      | OK       | N/A      | 5        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_TEMP                | 56Cel      | OK       | N/A      | N/A      | N/A      | 96       | 98       | N/A      | Intake
  SYS_FAN_1A                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_1B                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2A                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2B                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_1_FAN                 | 4000RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_2_FAN                 | 4000RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan

(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 ZT-Proteus-BMC-update-Redfish-v0.45.00-x86_64_20231017]$
```

### No change, installing .26 BMC, then .23 BIOS again

```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 ZT-Proteus-BMC-update-Redfish-v0.26.00-x86_64_20220726]$ ./update-*  $IP XXXXXX XXXXXX ./install-log.txt
IPv6 IP detected
[2607:f160:10:80b1:ce:40a:0:e008]
Check if right version of python is installed
Model name is Proteus
Product is L6 or Force option is slected, ok to proceed
Current BMC version is 0.45.00
System Serial is 207736270043
BMC version is 0.45.00
2024-01-16-18:52:44  Check for task that are not in a completed state
2024-01-16-18:52:45  There are a total of 7
2024-01-16-18:52:46  Task Number: 1    Task State: Completed
2024-01-16-18:52:46  Task Number: 2    Task State: Exception
2024-01-16-18:52:46  Task found that is not in a complete state
2024-01-16-18:52:46  Task found that are not in a complete state, will delete all task
204 https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/TaskService/Tasks/1
204 https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/TaskService/Tasks/2
204 https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/TaskService/Tasks/3
204 https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/TaskService/Tasks/4
204 https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/TaskService/Tasks/5
204 https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/TaskService/Tasks/6
204 https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/TaskService/Tasks/7
{"@odata.context":"/redfish/v1/$metadata#Task.Task","@odata.id":"/redfish/v1/TaskService/Tasks/1","@odata.type":"#Task.v1_4_2.Task","Description":"Task for Manager Reset","Id":"1","Name":"Manager Reset","TaskState":"New"}202 https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/Managers/Self/Actions/Manager.Reset
Restting BMC Waiting 240 seconds for retart
BMC ready continue flash
Updating BMC.....
20240116_185703 Version 3.0.4
20240116_185703 Copyright 2021 ZT Group Int'l, Inc. All Rights Reserved.
20240116_185703 GET: https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1
20240116_185703 GET: https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/UpdateService
20240116_185703 GET: https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/UpdateService/FirmwareInventory
20240116_185704 GET: https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/UpdateService/FirmwareInventory/BMC
20240116_185704 {
    "@odata.context": "/redfish/v1/$metadata#SoftwareInventory.SoftwareInventory",
    "@odata.etag": "\"1705452971\"",
    "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/BMC",
    "@odata.type": "#SoftwareInventory.v1_2_3.SoftwareInventory",
    "Id": "BMC",
    "Name": "BMC",
    "Updateable": true,
    "Version": "0.45.00"
}
20240116_185704 fwversion = [0.45.00]
20240116_185704 Initial BMC FW version: [0.45.00]
20240116_185704 initiate_fwupdate from /home/XXXXXX/ZT_FW/ZT-Proteus-BMC-update-Redfish-v0.26.00-x86_64_20220726 with v0.26.00.ima via redfish/v1/UpdateService/FirmwareInventory/BMC [timeout=300]
20240116_185704 JSON update_parameters : {"Targets": ["/redfish/v1/UpdateService/FirmwareInventory/BMC"]}
20240116_185704 JSON OEM_parameters    : {"ImageType": "BMC"}
20240116_185704 POST: https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/UpdateService/upload
20240116_185801 POST done: return code 202
20240116_185801 POST done: return data:
<Response [202]>
20240116_185801 {"@odata.type":"#UpdateService.v1_6_0.UpdateService","Messages":[{"@odata.type":"#Message.v1_0_8.Message","Message":"A new task /redfish/v1/TaskService/Tasks/2 was created.","MessageArgs":["/redfish/v1/TaskService/Tasks/2"],"MessageId":"Task.1.0.New","Resolution":"None","Severity":"OK"},{"@odata.type":"#Message.v1_0_8.Message","Message":"The action UpdateService.MultipartPush was submitted to do firmware update.","MessageArgs":["UpdateService.MultipartPush"],"MessageId":"UpdateService.1.0.StartFirmwareUpdate","Resolution":"None","Severity":"OK"}]}
20240116_185801 initiate_fwupdate returns polling uri: redfish/v1/TaskService/Tasks/2
20240116_185901 Polling for up to 60 seconds to check that the update starts
20240116_185901 GET: https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/TaskService/Tasks/2
20240116_185902 Update status : Running
20240116_185902 Polling for up to 1500 seconds to check that the update completes properly
20240116_185902 GET: https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/TaskService/Tasks/2
20240116_185903 Update status : Running (Percent complete = 0)
20240116_185903 Checking status on redfish/v1/TaskService/Tasks/2
20240116_185903 GET: https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/TaskService/Tasks/2
20240116_185904 Task     status : Running (Percent complete = 0)
20240116_185904 Found 2 messages from [redfish/v1/TaskService/Tasks/2]
20240116_185904 {"@odata.context": "/redfish/v1/$metadata#Task.Task", "@odata.etag": "\"1705453081\"", "@odata.id": "/redfish/v1/TaskService/Tasks/2", "@odata.type": "#Task.v1_4_2.Task", "Description": "Task for Update Service Task", "Id": "2", "Messages": [{"@odata.type": "#Message.v1_0_8.Message", "Message": "Task /redfish/v1/UpdateService/upload is running normally.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "Task.1.0.Running", "Resolution": "None", "Severity": "OK"}, {"@odata.type": "#Message.v1_0_8.Message", "Message": "Device is prepareing flash area for action /redfish/v1/UpdateService/upload.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "UpdateService.1.0.PrepareFlashArea", "Resolution": "None", "Severity": "OK"}], "Name": "Update Service Task", "PercentComplete": 0, "TaskState": "Running", "TaskStatus": "OK"}
.......etc

```

### So ended up on .36 bmc and .27 bios, then installed newly released .46 bmc bios

### wow, problem exists in .46 BMC ?? no way... but it does, however bios is .27 going to push new bios to .23 and see.

```log
[XXXXXX@welktxefnce-h-pe1util-vm01 ZT-Proteus-BMC-update-Redfish-v0.46.00-x86_64_20240116]$ rf_sensor_list.py -u XXXXXX -p XXXXXX -r https://[2607:f160:10:80b1:ce:40a:0:e008]
Chassis 'Computer System Chassis' Status
  Sensor                    | Reading    | Health   | LF       | LC       | LNC      | UNC      | UC       | UF       | PhysicalContext
  State                     | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 212V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 234W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 213V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 222W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_V5                    | 5.014V     | OK       | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | 12.138V    | OK       | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | 3.3236V    | OK       | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | 1.04992V   | OK       | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  RTC_Voltage               | 3.003V     | OK       | N/A      | 2.289    | N/A      | N/A      | 3.444    | N/A      | VoltageRegulator
  CPU_0_Vcore               | 1.808V     | OK       | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | 1.2232V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | 1.2232V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | -62Cel     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_MARGIN              | 51Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_PROCHOT             | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  PSU_1_TEMP_2              | 45Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_1_TEMP_1              | 27Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  PSU_2_TEMP_2              | 44Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_2_TEMP_1              | 26Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  CPU_0_DIMM_C0             | 28Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_D0             | 27Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_A0             | 27Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_B0             | 27Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_G0             | 27Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_H0             | 27Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_E0             | 27Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_F0             | 27Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  DIMM_VRABCD_TEMP          | 32Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  DIMM_VREFGH_TEMP          | 30Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  MAX_DIMM_TEMP             | 28Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  PML_WEST_TEMP             | 41Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  PML_LOCAL_TEMP            | 34Cel      | OK       | N/A      | N/A      | N/A      | 80       | 85       | N/A      | Intake
  PML_VDD_TEMP              | 40Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 125      | N/A      | Intake
  PML_EAST_TEMP             | 41Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  SC_1_E810                 | 33Cel      | OK       | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SC_2_E810                 | 32Cel      | OK       | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SSD_0_TEMP                | Absent     | N/A      | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  SSD_1_TEMP                | Absent     | N/A      | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  INLET_TEMP_L              | 24Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  INLET_TEMP_R              | 23Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  MB_HSC_TEMP               | 30Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  OUTLET_TEMP_L             | 33Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  OUTLET_TEMP_R             | 32Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  INLET_TEMP_MAX            | 24Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  OUTLET_TEMP_MAX           | 33Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  SYS_PCH_TEMP              | 26Cel      | OK       | N/A      | 5        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_TEMP                | 36Cel      | OK       | N/A      | N/A      | N/A      | 96       | 98       | N/A      | Intake
  SYS_FAN_1A                | 100%       | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_1B                | 100%       | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2A                | 100%       | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2B                | 100%       | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_1_FAN                 | 4160RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_2_FAN                 | 4000RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan

[XXXXXX@welktxefnce-h-pe1util-vm01 ZT-Proteus-BMC-update-Redfish-v0.46.00-x86_64_20240116]$
```

### After install of .23 bios with .46 bmc installed, results have changed on the sensors

```log
[XXXXXX@welktxefnce-h-pe1util-vm01 ZT-Proteus-BIOS-update-Redfish-v0.23-x86-64_20220726]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[${IP}]/redfish/v1/UpdateService/FirmwareInventory/BMC | jq .
{
  "@odata.context": "/redfish/v1/$metadata#SoftwareInventory.SoftwareInventory",
  "@odata.etag": "\"1705511922\"",
  "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/BMC",
  "@odata.type": "#SoftwareInventory.v1_2_3.SoftwareInventory",
  "Id": "BMC",
  "Name": "BMC",
  "Updateable": true,
  "Version": "0.46.00"
}
[XXXXXX@welktxefnce-h-pe1util-vm01 ZT-Proteus-BIOS-update-Redfish-v0.23-x86-64_20220726]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[${IP}]/redfish/v1/UpdateService/FirmwareInventory/BIOS | jq .
{
  "@odata.context": "/redfish/v1/$metadata#SoftwareInventory.SoftwareInventory",
  "@odata.etag": "\"1705511922\"",
  "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/BIOS",
  "@odata.type": "#SoftwareInventory.v1_2_3.SoftwareInventory",
  "Id": "BIOS",
  "Name": "BIOS",
  "Updateable": true,
  "Version": "0.23"
}
[XXXXXX@welktxefnce-h-pe1util-vm01 ZT-Proteus-BIOS-update-Redfish-v0.23-x86-64_20220726]$ rf_sensor_list.py -u XXXXXX -p XXXXXX -r https://[2607:f160:10:80b1:ce:40a:0:e008]
Chassis 'Computer System Chassis' Status
  Sensor                    | Reading    | Health   | LF       | LC       | LNC      | UNC      | UC       | UF       | PhysicalContext
  State                     | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 213V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 180W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 213V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 162W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_V5                    | 5.0062V    | OK       | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | 12.1756V   | OK       | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | 3.3236V    | OK       | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | 1.05156V   | OK       | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  RTC_Voltage               | 3.003V     | OK       | N/A      | 2.289    | N/A      | N/A      | 3.444    | N/A      | VoltageRegulator
  CPU_0_Vcore               | 1.8136V    | OK       | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | 1.2269V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | 1.2232V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | -57Cel     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_MARGIN              | 46Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_PROCHOT             | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  PSU_1_TEMP_2              | 44Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_1_TEMP_1              | 26Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  PSU_2_TEMP_2              | 42Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_2_TEMP_1              | 26Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  CPU_0_DIMM_C0             | 33Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_D0             | 32Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_A0             | 31Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_B0             | 31Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_G0             | 32Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_H0             | 32Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_E0             | 32Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_F0             | 31Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  DIMM_VRABCD_TEMP          | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  DIMM_VREFGH_TEMP          | 34Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  MAX_DIMM_TEMP             | 33Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  PML_WEST_TEMP             | 50Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  PML_LOCAL_TEMP            | 46Cel      | OK       | N/A      | N/A      | N/A      | 80       | 85       | N/A      | Intake
  PML_VDD_TEMP              | 52Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 125      | N/A      | Intake
  PML_EAST_TEMP             | 49Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  SC_1_E810                 | 39Cel      | OK       | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SC_2_E810                 | 37Cel      | OK       | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SSD_0_TEMP                | 28Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  SSD_1_TEMP                | 28Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  INLET_TEMP_L              | 26Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  INLET_TEMP_R              | 24Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  MB_HSC_TEMP               | 31Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  OUTLET_TEMP_L             | 35Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  OUTLET_TEMP_R             | 33Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  INLET_TEMP_MAX            | 26Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  OUTLET_TEMP_MAX           | 35Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  SYS_PCH_TEMP              | 27Cel      | OK       | N/A      | 5        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_TEMP                | 41Cel      | OK       | N/A      | N/A      | N/A      | 96       | 98       | N/A      | Intake
  SYS_FAN_1A                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_1B                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2A                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2B                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_1_FAN                 | 4000RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_2_FAN                 | 3840RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan

[XXXXXX@welktxefnce-h-pe1util-vm01 ZT-Proteus-BIOS-update-Redfish-v0.23-x86-64_20220726]$
```