# ZT Proteus .46 BMC firmware validation
# ZT Proteus BIOS .23
# 1/16/24 James Patchett

## Target Controller rchltxib-c000000-003

## Target RHOL welktxfe-616094361-rz-le0pts6-001
## LaaS C43 RU2-3 right server (host has not been deployed yet)
OAM: ????
BMC: 2607:f160:10:9083:ce:40a:0:e002


### Samsung SSD Tempature issue in BMC
### Drive types SAMSUNG SSD PM9A3 (MZQL21T9HCJR-00A07)
### In .45 BMC Samsung tempature could not be read, which causes fans to spike to 100% utiliztion
### We try to validate we can reproduce issue in lab, then show that new .46 BMC does not have issue with this drive type

### Found a system that has fans 100% running, BMC .45 and BIOS .23 in the MTCE Lab
### will collect some information before we upgrade the host to bmc .46 and see if the fan issue clears.

### BMC\BIOS version and Sensors

```log
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ echo $IP
2607:f160:10:9083:ce:40a:0:e002
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[${IP}]/redfish/v1/UpdateService/FirmwareInventory/
BMC | jq .
{
  "@odata.context": "/redfish/v1/$metadata#SoftwareInventory.SoftwareInventory",
  "@odata.etag": "\"1701903036\"",
  "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/BMC",
  "@odata.type": "#SoftwareInventory.v1_2_3.SoftwareInventory",
  "Id": "BMC",
  "Name": "BMC",
  "Updateable": true,
  "Version": "0.45.00"
}
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[${IP}]/redfish/v1/UpdateService/FirmwareInventory/BIOS | jq .
{
  "@odata.context": "/redfish/v1/$metadata#SoftwareInventory.SoftwareInventory",
  "@odata.etag": "\"1702063590\"",
  "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/BIOS",
  "@odata.type": "#SoftwareInventory.v1_2_3.SoftwareInventory",
  "Id": "BIOS",
  "Name": "BIOS",
  "Updateable": true,
  "Version": "0.23"
}
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$

[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ rf_sensor_list.py -u XXXXXX -p XXXXXX -r https://[$IP]
Chassis 'Computer System Chassis' Status
  Sensor                    | Reading    | Health   | LF       | LC       | LNC      | UNC      | UC       | UF       | PhysicalContext
  State                     | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enable     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 214V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 300W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enable     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 214V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 276W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_V5                    | 5.0218V    | OK       | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | 12.1004V   | OK       | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | 3.3134V    | OK       | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | 1.04664V   | OK       | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  RTC_Voltage               | 3.045V     | OK       | N/A      | 2.289    | N/A      | N/A      | 3.444    | N/A      | VoltageRegulator
  CPU_0_Vcore               | 1.7968V    | OK       | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | 1.2232V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | 1.2232V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | -55Cel     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_MARGIN              | 44Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_PROCHOT             | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  PSU_1_TEMP_2              | 44Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_1_TEMP_1              | 26Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  PSU_2_TEMP_2              | 45Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_2_TEMP_1              | 27Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  CPU_0_DIMM_C0             | 28Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_D0             | 27Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_A0             | 27Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_B0             | 27Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_G0             | 28Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_H0             | 28Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_E0             | 27Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_F0             | 27Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  DIMM_VRABCD_TEMP          | 31Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  DIMM_VREFGH_TEMP          | 31Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  MAX_DIMM_TEMP             | 28Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  PML_WEST_TEMP             | 39Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  PML_LOCAL_TEMP            | 26Cel      | OK       | N/A      | N/A      | N/A      | 80       | 85       | N/A      | Intake
  PML_VDD_TEMP              | 33Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 125      | N/A      | Intake
  PML_EAST_TEMP             | 39Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  SC_1_E810                 | 34Cel      | OK       | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SC_2_E810                 | 36Cel      | OK       | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SSD_0_TEMP                | 27Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  SSD_1_TEMP                | Absent     | N/A      | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  INLET_TEMP_L              | 24Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  INLET_TEMP_R              | 23Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  MB_HSC_TEMP               | 31Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  OUTLET_TEMP_L             | 33Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  OUTLET_TEMP_R             | 32Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  INLET_TEMP_MAX            | 24Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  OUTLET_TEMP_MAX           | 33Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  SYS_PCH_TEMP              | 25Cel      | OK       | N/A      | 5        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_TEMP                | 43Cel      | OK       | N/A      | N/A      | N/A      | 96       | 98       | N/A      | Intake
  SYS_FAN_1A                | 100%       | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_1B                | 100%       | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2A                | 100%       | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2B                | 100%       | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_1_FAN                 | 4640RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_2_FAN                 | 4480RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan

[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$

```

### We see we have FANS 100% and one SSD not reporting in temps

```log
  SYS_FAN_1A                | 100%       | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_1B                | 100%       | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2A                | 100%       | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2B                | 100%       | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan

  SC_1_E810                 | 34Cel      | OK       | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SC_2_E810                 | 36Cel      | OK       | N/A      | 0        | 5        | 100      | 105      | 115      | Intake

  SSD_0_TEMP                | 27Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  SSD_1_TEMP                | Absent     | N/A      | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
```

### Lets go see the Samsung SSD drives to confirm they are there

```log
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[${IP}]/redfish/v1/Chassis/Self | jq .
{
  "@odata.context": "/redfish/v1/$metadata#Chassis.Chassis",
  "@odata.etag": "\"1701903261\"",
  "@odata.id": "/redfish/v1/Chassis/Self",
  "@odata.type": "#Chassis.v1_10_0.Chassis",
  "Actions": {
    "#Chassis.Reset": {
      "@Redfish.ActionInfo": "/redfish/v1/Chassis/Self/ResetActionInfo",
      "@Redfish.OperationApplyTimeSupport": {
        "@odata.type": "#Settings.v1_2_2.OperationApplyTimeSupport",
        "MaintenanceWindowDurationInSeconds": 600,
        "MaintenanceWindowResource": {
          "@odata.id": "/redfish/v1/Chassis/Self"
        },
        "SupportedValues": [
          "Immediate",
          "AtMaintenanceWindowStart"
        ]
      },
      "target": "/redfish/v1/Chassis/Self/Actions/Chassis.Reset"
    }
  },
  "AssetTag": "SR-02199-001",
  "ChassisType": "Other",
  "Description": "Chassis Self",
  "Id": "Self",
  "IndicatorLED": "Off",
  "IndicatorLED@Redfish.AllowableValues": [
    "Lit",
    "Blinking",
    "Off"
  ],
  "Links": {
    "ComputerSystems": [
      {
        "@odata.id": "/redfish/v1/Systems/Self"
      }
    ],
    "ComputerSystems@odata.count": 1,
    "Drives": [
      {
        "@odata.id": "/redfish/v1/Systems/Self/Storage/1/Drives/NVMe_Device0_NSID1"
      },
      {
        "@odata.id": "/redfish/v1/Systems/Self/Storage/1/Drives/NVMe_Device1_NSID1"
      },
      {
        "@odata.id": "/redfish/v1/Systems/Self/Storage/1/Drives/USB_Device2_Port4"
      },
      {
        "@odata.id": "/redfish/v1/Systems/Self/Storage/1/Drives/USB_Device3_Port4"
      },
      {
        "@odata.id": "/redfish/v1/Systems/Self/Storage/1/Drives/USB_Device4_Port4"
      },
      {
        "@odata.id": "/redfish/v1/Systems/Self/Storage/1/Drives/USB_Device5_Port4"
      },
      {
        "@odata.id": "/redfish/v1/Systems/Self/Storage/1/Drives/USB_Device6_Port4"
      },
      {
        "@odata.id": "/redfish/v1/Systems/Self/Storage/1/Drives/USB_Device7_Port4"
      },
      {
        "@odata.id": "/redfish/v1/Systems/Self/Storage/1/Drives/USB_Device8_Port4"
      },
      {
        "@odata.id": "/redfish/v1/Systems/Self/Storage/1/Drives/USB_Device9_Port4"
      }
    ],
    "Drives@odata.count": 10,
    "ManagedBy": [
      {
        "@odata.id": "/redfish/v1/Managers/Self"
      }
    ],
    "ManagedBy@odata.count": 1
  },
  "Location": {
    "Info": "City;Building;Room;Rack;Row",
    "InfoFormat": "City;Building;RoomName;RackName;RowName",
    "Latitude": null,
    "Longitude": null,
    "Placement": {
      "Rack": "Rack",
      "Row": "Row"
    },
    "PostalAddress": {
      "Building": "Building",
      "City": "City",
      "Room": "Room"
    }
  },
  "LogServices": {
    "@odata.id": "/redfish/v1/Chassis/Self/LogServices"
  },
  "Manufacturer": "ZTSYSTEMS",
  "Model": "Proteus I_Mix",
  "Name": "Computer System Chassis",
  "NetworkAdapters": {
    "@odata.id": "/redfish/v1/Chassis/Self/NetworkAdapters"
  },
  "PCIeDevices": {
    "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices"
  },
  "PartNumber": " ",
  "PhysicalSecurity": {
    "IntrusionSensor": null
  },
  "Power": {
    "@odata.id": "/redfish/v1/Chassis/Self/Power"
  },
  "PowerState": "On",
  "SKU": "SR-02199-001",
  "Sensors": {
    "@odata.id": "/redfish/v1/Chassis/Self/Sensors"
  },
  "SerialNumber": "210006140039",
  "Status": {
    "Health": "OK",
    "HealthRollup": "OK",
    "State": "Enabled"
  },
  "Thermal": {
    "@odata.id": "/redfish/v1/Chassis/Self/Thermal"
  }
}
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[${IP}]/redfish/v1/Systems/Self/Storage/1/Drives/NVMe_Device0_NSID1 | jq .
{
  "@odata.context": "/redfish/v1/$metadata#Drive.Drive",
  "@odata.etag": "\"1702063587\"",
  "@odata.id": "/redfish/v1/Systems/Self/Storage/1/Drives/NVMe_Device0_NSID1",
  "@odata.type": "#Drive.v1_7_0.Drive",
  "AssetTag": null,
  "BlockSizeBytes": 512,
  "CapableSpeedGbs": 0,
  "CapacityBytes": 1920383410176,
  "EncryptionAbility": "SelfEncryptingDrive",
  "EncryptionStatus": "Unlocked",
  "FailurePredicted": false,
  "Id": "NVMe_Device0_NSID1",
  "IndicatorLED": null,
  "Links": {
    "Chassis": {
      "@odata.id": "/redfish/v1/Chassis/Self"
    },
    "Endpoints@odata.count": 0,
    "Volumes": [
      {
        "@odata.id": "/redfish/v1/Systems/Self/Storage/1/Volumes/VOL0"
      }
    ],
    "Volumes@odata.count": 1
  },
  "Manufacturer": "N/A",
  "MediaType": "SSD",
  "Model": "SAMSUNG MZQL21T9HCJR-00A07",
  "Name": "NVMe_Device0_NSID1",
  "NegotiatedSpeedGbs": 0,
  "PredictedMediaLifeLeftPercent": 100,
  "Protocol": "NVMe",
  "Revision": "NVMe Spec v1.4",
  "RotationSpeedRPM": 0,
  "SerialNumber": "S64GNS0T817950",
  "Status": {
    "Health": "OK",
    "State": "Enabled"
  },
  "StatusIndicator": "OK"
}
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[${IP}]/redfish/v1/Systems/Self/Storage/1/Drives/NVMe_Device1_NSID1 | jq .
{
  "@odata.context": "/redfish/v1/$metadata#Drive.Drive",
  "@odata.etag": "\"1702063587\"",
  "@odata.id": "/redfish/v1/Systems/Self/Storage/1/Drives/NVMe_Device1_NSID1",
  "@odata.type": "#Drive.v1_7_0.Drive",
  "AssetTag": null,
  "BlockSizeBytes": 512,
  "CapableSpeedGbs": 0,
  "CapacityBytes": 1920383410176,
  "EncryptionAbility": "SelfEncryptingDrive",
  "EncryptionStatus": "Unlocked",
  "FailurePredicted": false,
  "Id": "NVMe_Device1_NSID1",
  "IndicatorLED": null,
  "Links": {
    "Chassis": {
      "@odata.id": "/redfish/v1/Chassis/Self"
    },
    "Endpoints@odata.count": 0,
    "Volumes@odata.count": 0
  },
  "Manufacturer": "N/A",
  "MediaType": "SSD",
  "Model": "SAMSUNG MZQL21T9HCJR-00A07",
  "Name": "NVMe_Device1_NSID1",
  "NegotiatedSpeedGbs": 0,
  "PredictedMediaLifeLeftPercent": 100,
  "Protocol": "NVMe",
  "Revision": "NVMe Spec v1.4",
  "RotationSpeedRPM": 0,
  "SerialNumber": "S64GNS0T817966",
  "Status": {
    "Health": "OK",
    "State": "Enabled"
  },
  "StatusIndicator": "OK"
}
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$

```

### So we see we have the samsung drives in this system

```log
  "Model": "SAMSUNG MZQL21T9HCJR-00A07",
  "Name": "NVMe_Device0_NSID1",
  
  "Model": "SAMSUNG MZQL21T9HCJR-00A07",
  "Name": "NVMe_Device1_NSID1",  
  ```

  ### Ok bug is confirmed, we see it as production has experienced it

  ### Lets install .46 BMC and see if this clears up the fans and SSD temp sensor issue

  ```log 
  [XXXXXX@welktxefnce-h-pe1util-vm01 ZT-Proteus-BMC-update-Redfish-v0.46.00-x86_64_20240116]$ ./update-bmc-redfish-python-v09-20240116.sh $IP XXXXXX XXXXXX ./${IP}_install_46-for-the-fix.txt
===============================================================
          ZT BMC Update for Proteus and Triton
     update-bmc-redfish-python-v09-20240116.sh
                    01/16/2024
                     Ver 0.09
===============================================================

2024-01-17-14:58:30  Check if IP address is valid
2024-01-17-14:58:30  IPv6 IP detected
2024-01-17-14:58:31  2607:f160:10:9083:ce:40a:0:e002 is a valid IP
2024-01-17-14:58:31  IPv6 Address is 2607:f160:10:9083:ce:40a:0:e002
2024-01-17-14:58:32  Redfish credentials are correct, continue update
2024-01-17-14:58:33  Check if right version of python3 is installed
2024-01-17-14:58:33  Python3 is installed, continue update
2024-01-17-14:58:35  Model name is Proteus
2024-01-17-14:58:35  Product is Proteus or Force option is selected, ok to proceed
2024-01-17-14:58:35  System Serial is 21000614N077
2024-01-17-14:58:35  BMC current version is 0.45.00
{"@odata.context":"/redfish/v1/$metadata#Task.Task","@odata.id":"/redfish/v1/TaskService/Tasks/18","@odata.type":"#Task.v1_4_2.Task","Description":"Task for Manager Reset","Id":"18","Name":"Manager Reset","TaskState":"New"}202 https://[2607:f160:10:9083:ce:40a:0:e002]/redfish/v1/Managers/Self/Actions/Manager.Reset
2024-01-17-14:58:36  Resetting BMC Waiting 240 seconds for restart

            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "Task.1.0.Running",
            "Resolution": "None",
            "Severity": "OK"
        },
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "UpdateService.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 62,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20240117_151115 Update status (monitor, running) : Running (Percent complete = 62)
20240117_151115 Checking task status on /redfish/v1/TaskService/Tasks/2
20240117_151115 GET: https://[2607:f160:10:9083:ce:40a:0:e002]/redfish/v1/TaskService/Tasks/2
20240117_151116 HTTP: 200
20240117_151116 JSON: {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1705525625\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/2",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "2",
    "Messages": [
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Task /redfish/v1/UpdateService/upload is running normally.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "Task.1.0.Running",
            "Resolution": "None",
            "Severity": "OK"
        },
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "UpdateService.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 62,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20240117_151116 Task /redfish/v1/TaskService/Tasks/2  status : 200 Running (Percent complete = 62)
20240117_151116 Found 2 messages from [/redfish/v1/TaskService/Tasks/2]
20240117_151116 {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1705525625\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/2",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "2",
    "Messages": [
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Task /redfish/v1/UpdateService/upload is running normally.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "Task.1.0.Running",
            "Resolution": "None",
            "Severity": "OK"
        },
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "UpdateService.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 62,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20240117_151116     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20240117_151116     Unknown             OK          Device is flashing firmware for action /redfish/v1/UpdateService/upload.
20240117_151116 task_status : Running ... checking again
20240117_151121 GET: https://[2607:f160:10:9083:ce:40a:0:e002]/redfish/v1/TaskService/Tasks/2
20240117_151121 HTTP: 200
20240117_151121 JSON: {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1705525625\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/2",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "2",
    "Messages": [
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Task /redfish/v1/UpdateService/upload is running normally.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "Task.1.0.Running",
            "Resolution": "None",
            "Severity": "OK"
        },
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "UpdateService.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 87,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20240117_151121 Update status (monitor, running) : Running (Percent complete = 87)
20240117_151121 Checking task status on /redfish/v1/TaskService/Tasks/2
20240117_151121 GET: https://[2607:f160:10:9083:ce:40a:0:e002]/redfish/v1/TaskService/Tasks/2
20240117_151122 HTTP: 200
20240117_151122 JSON: {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1705525625\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/2",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "2",
    "Messages": [
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Task /redfish/v1/UpdateService/upload is running normally.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "Task.1.0.Running",
            "Resolution": "None",
            "Severity": "OK"
        },
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "UpdateService.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 87,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20240117_151122 Task /redfish/v1/TaskService/Tasks/2  status : 200 Running (Percent complete = 87)
20240117_151122 Found 2 messages from [/redfish/v1/TaskService/Tasks/2]
20240117_151122 {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1705525625\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/2",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "2",
    "Messages": [
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Task /redfish/v1/UpdateService/upload is running normally.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "Task.1.0.Running",
            "Resolution": "None",
            "Severity": "OK"
        },
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "UpdateService.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 87,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20240117_151122     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20240117_151122     Unknown             OK          Device is flashing firmware for action /redfish/v1/UpdateService/upload.
20240117_151122 task_status : Running ... checking again
20240117_151127 GET: https://[2607:f160:10:9083:ce:40a:0:e002]/redfish/v1/TaskService/Tasks/2
20240117_151127 HTTP: 200
20240117_151127 JSON: {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1705525625\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/2",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "2",
    "Messages": [
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Task /redfish/v1/UpdateService/upload is running normally.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "Task.1.0.Running",
            "Resolution": "None",
            "Severity": "OK"
        },
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "UpdateService.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 100,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20240117_151127 Update status (monitor, running) : Running (Percent complete = 100)
20240117_151127 Checking task status on /redfish/v1/TaskService/Tasks/2
20240117_151127 GET: https://[2607:f160:10:9083:ce:40a:0:e002]/redfish/v1/TaskService/Tasks/2
20240117_151128 HTTP: 200
20240117_151128 JSON: {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1705525625\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/2",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "2",
    "Messages": [
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Task /redfish/v1/UpdateService/upload is running normally.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "Task.1.0.Running",
            "Resolution": "None",
            "Severity": "OK"
        },
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "UpdateService.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 100,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20240117_151128 Task /redfish/v1/TaskService/Tasks/2  status : 200 Running (Percent complete = 100)
20240117_151128 Found 2 messages from [/redfish/v1/TaskService/Tasks/2]
20240117_151128 {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1705525625\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/2",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "2",
    "Messages": [
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Task /redfish/v1/UpdateService/upload is running normally.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "Task.1.0.Running",
            "Resolution": "None",
            "Severity": "OK"
        },
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "UpdateService.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 100,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20240117_151128     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20240117_151128     Unknown             OK          Device is flashing firmware for action /redfish/v1/UpdateService/upload.
20240117_151128 task_status : Running ... checking again
20240117_151133 GET: https://[2607:f160:10:9083:ce:40a:0:e002]/redfish/v1/TaskService/Tasks/2
20240117_151133 HTTP: 200
20240117_151133 JSON: {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1705525625\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/2",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "2",
    "Messages": [
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Task /redfish/v1/UpdateService/upload is running normally.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "Task.1.0.Running",
            "Resolution": "None",
            "Severity": "OK"
        },
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "UpdateService.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 100,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20240117_151133 Update status (monitor, running) : Running (Percent complete = 100)
20240117_151133 Checking task status on /redfish/v1/TaskService/Tasks/2
20240117_151133 GET: https://[2607:f160:10:9083:ce:40a:0:e002]/redfish/v1/TaskService/Tasks/2
20240117_151133 HTTP: 200
20240117_151133 JSON: {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1705525625\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/2",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "2",
    "Messages": [
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Task /redfish/v1/UpdateService/upload is running normally.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "Task.1.0.Running",
            "Resolution": "None",
            "Severity": "OK"
        },
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "UpdateService.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 100,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20240117_151133 Task /redfish/v1/TaskService/Tasks/2  status : 200 Running (Percent complete = 100)
20240117_151133 Found 2 messages from [/redfish/v1/TaskService/Tasks/2]
20240117_151133 {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1705525625\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/2",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "2",
    "Messages": [
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Task /redfish/v1/UpdateService/upload is running normally.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "Task.1.0.Running",
            "Resolution": "None",
            "Severity": "OK"
        },
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "UpdateService.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 100,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20240117_151133     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20240117_151133     Unknown             OK          Device is flashing firmware for action /redfish/v1/UpdateService/upload.
20240117_151133 task_status : Running ... checking again
20240117_151138 GET: https://[2607:f160:10:9083:ce:40a:0:e002]/redfish/v1/TaskService/Tasks/2
20240117_151139 HTTP: 200
20240117_151139 JSON: {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1705525625\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/2",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "2",
    "Messages": [
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Task /redfish/v1/UpdateService/upload is running normally.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "Task.1.0.Running",
            "Resolution": "None",
            "Severity": "OK"
        },
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "UpdateService.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 100,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20240117_151139 Update status (monitor, running) : Running (Percent complete = 100)
20240117_151139 Checking task status on /redfish/v1/TaskService/Tasks/2
20240117_151139 GET: https://[2607:f160:10:9083:ce:40a:0:e002]/redfish/v1/TaskService/Tasks/2
20240117_151139 HTTP: 200
20240117_151139 JSON: {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1705525625\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/2",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "2",
    "Messages": [
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Task /redfish/v1/UpdateService/upload is running normally.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "Task.1.0.Running",
            "Resolution": "None",
            "Severity": "OK"
        },
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "UpdateService.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 100,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20240117_151139 Task /redfish/v1/TaskService/Tasks/2  status : 200 Running (Percent complete = 100)
20240117_151139 Found 2 messages from [/redfish/v1/TaskService/Tasks/2]
20240117_151139 {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1705525625\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/2",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "2",
    "Messages": [
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Task /redfish/v1/UpdateService/upload is running normally.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "Task.1.0.Running",
            "Resolution": "None",
            "Severity": "OK"
        },
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "UpdateService.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 100,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20240117_151139     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20240117_151139     Unknown             OK          Device is flashing firmware for action /redfish/v1/UpdateService/upload.
20240117_151139 task_status : Running ... checking again
20240117_151144 GET: https://[2607:f160:10:9083:ce:40a:0:e002]/redfish/v1/TaskService/Tasks/2
20240117_151145 HTTP: 200
20240117_151145 JSON: {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1705525625\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/2",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "2",
    "Messages": [
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Task /redfish/v1/UpdateService/upload is running normally.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "Task.1.0.Running",
            "Resolution": "None",
            "Severity": "OK"
        },
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "UpdateService.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 100,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20240117_151145 Update status (monitor, running) : Running (Percent complete = 100)
20240117_151145 Checking task status on /redfish/v1/TaskService/Tasks/2
20240117_151145 GET: https://[2607:f160:10:9083:ce:40a:0:e002]/redfish/v1/TaskService/Tasks/2
20240117_151145 HTTP: 200
20240117_151145 JSON: {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1705525625\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/2",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "2",
    "Messages": [
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Task /redfish/v1/UpdateService/upload is running normally.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "Task.1.0.Running",
            "Resolution": "None",
            "Severity": "OK"
        },
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "UpdateService.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 100,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20240117_151145 Task /redfish/v1/TaskService/Tasks/2  status : 200 Running (Percent complete = 100)
20240117_151145 Found 2 messages from [/redfish/v1/TaskService/Tasks/2]
20240117_151145 {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1705525625\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/2",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "2",
    "Messages": [
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Task /redfish/v1/UpdateService/upload is running normally.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "Task.1.0.Running",
            "Resolution": "None",
            "Severity": "OK"
        },
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "UpdateService.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 100,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20240117_151145     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20240117_151145     Unknown             OK          Device is flashing firmware for action /redfish/v1/UpdateService/upload.
20240117_151145 task_status : Running ... checking again
20240117_151150 GET: https://[2607:f160:10:9083:ce:40a:0:e002]/redfish/v1/TaskService/Tasks/2
20240117_151151 HTTP: 200
20240117_151151 JSON: {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1705525625\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/2",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "2",
    "Messages": [
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Task /redfish/v1/UpdateService/upload is running normally.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "Task.1.0.Running",
            "Resolution": "None",
            "Severity": "OK"
        },
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "UpdateService.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 100,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20240117_151151 Update status (monitor, running) : Running (Percent complete = 100)
20240117_151151 Checking task status on /redfish/v1/TaskService/Tasks/2
20240117_151151 GET: https://[2607:f160:10:9083:ce:40a:0:e002]/redfish/v1/TaskService/Tasks/2
20240117_151151 HTTP: 200
20240117_151151 JSON: {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1705525625\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/2",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "2",
    "Messages": [
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Task /redfish/v1/UpdateService/upload is running normally.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "Task.1.0.Running",
            "Resolution": "None",
            "Severity": "OK"
        },
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "UpdateService.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 100,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20240117_151151 Task /redfish/v1/TaskService/Tasks/2  status : 200 Running (Percent complete = 100)
20240117_151151 Found 2 messages from [/redfish/v1/TaskService/Tasks/2]
20240117_151151 {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1705525625\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/2",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "2",
    "Messages": [
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Task /redfish/v1/UpdateService/upload is running normally.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "Task.1.0.Running",
            "Resolution": "None",
            "Severity": "OK"
        },
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "UpdateService.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 100,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20240117_151151     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20240117_151151     Unknown             OK          Device is flashing firmware for action /redfish/v1/UpdateService/upload.
20240117_151151 task_status : Running ... checking again
20240117_151156 GET: https://[2607:f160:10:9083:ce:40a:0:e002]/redfish/v1/TaskService/Tasks/2
20240117_151156 HTTP: 200
20240117_151156 JSON: {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1705525625\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/2",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "EndTime": "2024-01-17T21:11:51+00:00",
    "Id": "2",
    "Messages": [
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Task /redfish/v1/UpdateService/upload has completed.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "Task.1.0.Completed",
            "Resolution": "None",
            "Severity": "OK"
        },
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Action /redfish/v1/UpdateService/upload firmware update is completed.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "UpdateService.1.0.FirmwareUpdateCompleted",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 100,
    "TaskState": "Completed",
    "TaskStatus": "OK"
}
20240117_151156 Update status (monitor, running) : Completed (Percent complete = 100)
20240117_151156 Update completed successfully
20240117_151216 Checking task status on /redfish/v1/TaskService/Tasks/2
20240117_151216 GET: https://[2607:f160:10:9083:ce:40a:0:e002]/redfish/v1/TaskService/Tasks/2
20240117_151216 HTTP: 200
20240117_151216 JSON: {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1705525625\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/2",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "EndTime": "2024-01-17T21:11:51+00:00",
    "Id": "2",
    "Messages": [
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Task /redfish/v1/UpdateService/upload has completed.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "Task.1.0.Completed",
            "Resolution": "None",
            "Severity": "OK"
        },
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Action /redfish/v1/UpdateService/upload firmware update is completed.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "UpdateService.1.0.FirmwareUpdateCompleted",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 100,
    "TaskState": "Completed",
    "TaskStatus": "OK"
}
20240117_151216 Task /redfish/v1/TaskService/Tasks/2  status : 200 Completed (Percent complete = 100)
20240117_151216 Found 2 messages from [/redfish/v1/TaskService/Tasks/2]
20240117_151216 {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1705525625\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/2",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "EndTime": "2024-01-17T21:11:51+00:00",
    "Id": "2",
    "Messages": [
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Task /redfish/v1/UpdateService/upload has completed.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "Task.1.0.Completed",
            "Resolution": "None",
            "Severity": "OK"
        },
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Action /redfish/v1/UpdateService/upload firmware update is completed.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "UpdateService.1.0.FirmwareUpdateCompleted",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 100,
    "TaskState": "Completed",
    "TaskStatus": "OK"
}
20240117_151216     Unknown             OK          Task /redfish/v1/UpdateService/upload has completed.
20240117_151216     Unknown             OK          Action /redfish/v1/UpdateService/upload firmware update is completed.
20240117_151216 FW update completed -- waiting 180 seconds before checking for new version
20240117_151517 Polling for up to 600 seconds to detect new FW versions
20240117_151517 Target: BMC                              Any
20240117_151517 GET: https://[2607:f160:10:9083:ce:40a:0:e002]/redfish/v1/UpdateService/FirmwareInventory/BMC
20240117_151517 HTTP: 503
20240117_151517 JSON: {
    "error": {
        "@Message.ExtendedInfo": [
            {
                "@odata.type": "#Message.v1_0_8.Message",
                "Message": "The operation failed because the service is in an unknown state and can no longer take incoming requests.",
                "MessageId": "Base.1.5.ServiceInUnknownState",
                "Resolution": "Restart the service or resubmit the request if the operation failed.",
                "Severity": "Critical"
            }
        ],
        "code": "Base.1.5.ServiceInUnknownState",
        "message": "The operation failed because the service is in an unknown state and can no longer take incoming requests."
    }
}
20240117_151517 fwversion = [Unknown] [Unknown]
20240117_151527 GET: https://[2607:f160:10:9083:ce:40a:0:e002]/redfish/v1/UpdateService/FirmwareInventory/BMC
20240117_151529 HTTP: 503
20240117_151529 JSON: {
    "error": {
        "@Message.ExtendedInfo": [
            {
                "@odata.type": "#Message.v1_0_8.Message",
                "Message": "The operation failed because the service is in an unknown state and can no longer take incoming requests.",
                "MessageId": "Base.1.5.ServiceInUnknownState",
                "Resolution": "Restart the service or resubmit the request if the operation failed.",
                "Severity": "Critical"
            }
        ],
        "code": "Base.1.5.ServiceInUnknownState",
        "message": "The operation failed because the service is in an unknown state and can no longer take incoming requests."
    }
}
20240117_151529 fwversion = [Unknown] [Unknown]
20240117_151539 GET: https://[2607:f160:10:9083:ce:40a:0:e002]/redfish/v1/UpdateService/FirmwareInventory/BMC
20240117_151540 HTTP: 503
20240117_151540 JSON: {
    "error": {
        "@Message.ExtendedInfo": [
            {
                "@odata.type": "#Message.v1_0_8.Message",
                "Message": "The operation failed because the service is in an unknown state and can no longer take incoming requests.",
                "MessageId": "Base.1.5.ServiceInUnknownState",
                "Resolution": "Restart the service or resubmit the request if the operation failed.",
                "Severity": "Critical"
            }
        ],
        "code": "Base.1.5.ServiceInUnknownState",
        "message": "The operation failed because the service is in an unknown state and can no longer take incoming requests."
    }
}
20240117_151540 fwversion = [Unknown] [Unknown]
20240117_151550 GET: https://[2607:f160:10:9083:ce:40a:0:e002]/redfish/v1/UpdateService/FirmwareInventory/BMC
20240117_151551 HTTP: 503
20240117_151551 JSON: {
    "error": {
        "@Message.ExtendedInfo": [
            {
                "@odata.type": "#Message.v1_0_8.Message",
                "Message": "The operation failed because the service is in an unknown state and can no longer take incoming requests.",
                "MessageId": "Base.1.5.ServiceInUnknownState",
                "Resolution": "Restart the service or resubmit the request if the operation failed.",
                "Severity": "Critical"
            }
        ],
        "code": "Base.1.5.ServiceInUnknownState",
        "message": "The operation failed because the service is in an unknown state and can no longer take incoming requests."
    }
}
20240117_151551 fwversion = [Unknown] [Unknown]
20240117_151601 GET: https://[2607:f160:10:9083:ce:40a:0:e002]/redfish/v1/UpdateService/FirmwareInventory/BMC
20240117_151602 HTTP: 503
20240117_151602 JSON: {
    "error": {
        "@Message.ExtendedInfo": [
            {
                "@odata.type": "#Message.v1_0_8.Message",
                "Message": "The operation failed because the service is in an unknown state and can no longer take incoming requests.",
                "MessageId": "Base.1.5.ServiceInUnknownState",
                "Resolution": "Restart the service or resubmit the request if the operation failed.",
                "Severity": "Critical"
            }
        ],
        "code": "Base.1.5.ServiceInUnknownState",
        "message": "The operation failed because the service is in an unknown state and can no longer take incoming requests."
    }
}
20240117_151602 fwversion = [Unknown] [Unknown]
20240117_151612 GET: https://[2607:f160:10:9083:ce:40a:0:e002]/redfish/v1/UpdateService/FirmwareInventory/BMC
20240117_151614 HTTP: 200
20240117_151614 JSON: {
    "@odata.context": "/redfish/v1/$metadata#SoftwareInventory.SoftwareInventory",
    "@odata.etag": "\"1705526143\"",
    "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/BMC",
    "@odata.type": "#SoftwareInventory.v1_2_3.SoftwareInventory",
    "Id": "BMC",
    "Name": "BMC",
    "Updateable": true,
    "Version": "0.46.00"
}
20240117_151614 {
    "@odata.context": "/redfish/v1/$metadata#SoftwareInventory.SoftwareInventory",
    "@odata.etag": "\"1705526143\"",
    "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/BMC",
    "@odata.type": "#SoftwareInventory.v1_2_3.SoftwareInventory",
    "Id": "BMC",
    "Name": "BMC",
    "Updateable": true,
    "Version": "0.46.00"
}
20240117_151614 fwversion = [Version] [0.46.00]
20240117_151614 Obtained 1 of 1 FW versions
20240117_151614 Final BMC FW version: [0.46.00]
20240117_151614 Checking for final FW version match
Statistics: starts
datetime,ecode,nerrs,fw_imgfile,fwver_start,fwver_end,fwver_expected,component_type,component_name,component_count,component_updated,bmc_ip,oshost_ip,osping_pre_secs,osping_total_secs,osping_pass,osping_fail,wait_before_update_poll_start,wait_after_poll_complete,poll_time_for_update_start,poll_time_for_update_complete,poll_time_for_post,poll_count_for_post,poll_time_for_version,poll_count_for_version,do_reboot,do_clear_sel_log,total_time,initiate_fwupdate_time,wait_for_update_done_time,iterate_for_post_complete_time,wait_for_version_available_time,wait_for_host_status_time,
20240117_150601,0,0,v0.46.00.ima,0.45.00,0.46.00,,BMC,BMC,1,1,[2607:f160:10:9083:ce:40a:0:e002],,10,120,0,0,60,180,60,1500,0,2,600,2,0,0,612,61,310,0,57,0
Statistics: ends
20240117_151614 Process completed successfully
2024-01-17-15:16:14  Final Check
2024-01-17-15:16:15  BMC updated successfully to 0.46.00
[XXXXXX@welktxefnce-h-pe1util-vm01 ZT-Proteus-BMC-update-Redfish-v0.46.00-x86_64_20240116]$
```

  ### Upgrade to .46 BMC Firmware was successful, now lets see what the SSDs look like 

```log
  [XXXXXX@welktxefnce-h-pe1util-vm01 ZT-Proteus-BMC-update-Redfish-v0.46.00-x86_64_20240116]$ echo $IP
2607:f160:10:9083:ce:40a:0:e002
[XXXXXX@welktxefnce-h-pe1util-vm01 ZT-Proteus-BMC-update-Redfish-v0.46.00-x86_64_20240116]$

[XXXXXX@welktxefnce-h-pe1util-vm01 ZT-Proteus-BMC-update-Redfish-v0.46.00-x86_64_20240116]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[${IP}]/redfish/v1/UpdateService/FirmwareInventory/BIOS | jq .
{
  "@odata.context": "/redfish/v1/$metadata#SoftwareInventory.SoftwareInventory",
  "@odata.etag": "\"1705526143\"",
  "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/BIOS",
  "@odata.type": "#SoftwareInventory.v1_2_3.SoftwareInventory",
  "Id": "BIOS",
  "Name": "BIOS",
  "Updateable": true,
  "Version": "0.23"
}
[XXXXXX@welktxefnce-h-pe1util-vm01 ZT-Proteus-BMC-update-Redfish-v0.46.00-x86_64_20240116]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[${IP}]/redfish/v1/UpdateService/FirmwareInventory/BMC | jq .
{
  "@odata.context": "/redfish/v1/$metadata#SoftwareInventory.SoftwareInventory",
  "@odata.etag": "\"1705526143\"",
  "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/BMC",
  "@odata.type": "#SoftwareInventory.v1_2_3.SoftwareInventory",
  "Id": "BMC",
  "Name": "BMC",
  "Updateable": true,
  "Version": "0.46.00"
}
[XXXXXX@welktxefnce-h-pe1util-vm01 ZT-Proteus-BMC-update-Redfish-v0.46.00-x86_64_20240116]$ rf_sensor_list.py -u XXXXXX -p XXXXXX -r https://[$IP]
Chassis 'Computer System Chassis' Status
  Sensor                    | Reading    | Health   | LF       | LC       | LNC      | UNC      | UC       | UF       | PhysicalContext
  State                     | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 214V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 240W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 214V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 216W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_V5                    | 5.0296V    | OK       | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | 12.1568V   | OK       | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | 3.3134V    | OK       | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | 1.04664V   | OK       | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  RTC_Voltage               | 3.038V     | OK       | N/A      | 2.289    | N/A      | N/A      | 3.444    | N/A      | VoltageRegulator
  CPU_0_Vcore               | 1.794V     | OK       | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | 1.2232V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | 1.2232V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | -46Cel     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_MARGIN              | 35Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_PROCHOT             | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  PSU_1_TEMP_2              | 44Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_1_TEMP_1              | 26Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  PSU_2_TEMP_2              | 45Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_2_TEMP_1              | 27Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  CPU_0_DIMM_C0             | 31Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_D0             | 30Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_A0             | 29Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_B0             | 29Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_G0             | 31Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_H0             | 30Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_E0             | 30Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_F0             | 29Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  DIMM_VRABCD_TEMP          | 34Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  DIMM_VREFGH_TEMP          | 33Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  MAX_DIMM_TEMP             | 31Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  PML_WEST_TEMP             | 42Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  PML_LOCAL_TEMP            | 29Cel      | OK       | N/A      | N/A      | N/A      | 80       | 85       | N/A      | Intake
  PML_VDD_TEMP              | 38Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 125      | N/A      | Intake
  PML_EAST_TEMP             | 42Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  SC_1_E810                 | 29Cel      | OK       | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SC_2_E810                 | 29Cel      | OK       | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SSD_0_TEMP                | 28Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  SSD_1_TEMP                | 28Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  INLET_TEMP_L              | 25Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  INLET_TEMP_R              | 24Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  MB_HSC_TEMP               | 31Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  OUTLET_TEMP_L             | 35Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  OUTLET_TEMP_R             | 33Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  INLET_TEMP_MAX            | 25Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  OUTLET_TEMP_MAX           | 35Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  SYS_PCH_TEMP              | 29Cel      | OK       | N/A      | 5        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_TEMP                | 52Cel      | OK       | N/A      | N/A      | N/A      | 96       | 98       | N/A      | Intake
  SYS_FAN_1A                | 24%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_1B                | 24%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2A                | 24%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2B                | 24%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_1_FAN                 | 4000RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_2_FAN                 | 4000RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan

  ```

### Ok, lets look and see, is it fixed? 

  ```log
  SC_1_E810                 | 29Cel      | OK       | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SC_2_E810                 | 29Cel      | OK       | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SSD_0_TEMP                | 28Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  SSD_1_TEMP                | 28Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  ```
### Well SSD temps are working...  Did Fans go down ?

  ```log
  SYS_FAN_1A                | 24%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_1B                | 24%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2A                | 24%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2B                | 24%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_1_FAN                 | 4000RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_2_FAN                 | 4000RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
  ```

### Fans went down, .46 BMC appears to have fixed the issue.
### Success .46 bmc firmware does address Samsung SSDs temp issue

