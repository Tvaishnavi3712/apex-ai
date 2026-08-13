# ZT Proteus PDB-DPLD 0.0.1.2 firmware
# ZT Released this firmware to address PSU sensors data missing 
# ZT Proteus BMC .46 and Bios .23 & .30
# 2/26/24 James Patchett
# Sensor validation before and after installation of PDB 0.0.1.2

## Target subclouds RU_12,13 Right and Left side

## Left side Subcloud welktxef-d931887-021
## BMC 0.46 BIOS 0.30
BMC:  2607:f160:10:9249:ce:40a:0:e015
OAM:  2607:f160:10:9249:ce:40a:0:f409

## Controller IB-CR3 welktxid-c000000-002
BMC:  2607:f160:10:920f:ce:fe0:0:8066
OAM:  2607:f160:10:910a:ce:290:0:10

## Right side Subcloud welktxef-d931883-022
## BMC 0.46 BIOS 0.30
BMC:  2607:f160:10:9249:ce:40a:0:e016
OAM:  2607:f160:10:9249:ce:40a:0:f407

## Controller IB-CR2 welktxib-c000000-001
BMC:  2607:f160:10:920f:ce:fe0:0:8063
OAM:  2607:f160:10:9109:ce:290:0:10

```log
[XXXXXX@welktxefnce-h-pe1util-vm01 pdb-cpld-v12-20240220]$ IP=2607:f160:10:9249:ce:40a:0:e015
[XXXXXX@welktxefnce-h-pe1util-vm01 pdb-cpld-v12-20240220]$ rf_sensor_list.py -u XXXXXX -p XXXXXX -r https://[$IP]
Chassis 'Computer System Chassis' Status
  Sensor                    | Reading    | Health   | LF       | LC       | LNC      | UNC      | UC       | UF       | PhysicalContext
  State                     | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 214V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 1530W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 213V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 1530W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_V5                    | Absent     | N/A      | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | Absent     | N/A      | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | Absent     | N/A      | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | Absent     | N/A      | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  RTC_Voltage               | 3.01V      | OK       | N/A      | 2.289    | N/A      | N/A      | 3.444    | N/A      | VoltageRegulator
  CPU_0_Vcore               | Absent     | N/A      | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_MARGIN              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_PROCHOT             | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  PSU_1_TEMP_2              | 47Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_1_TEMP_1              | 28Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  PSU_2_TEMP_2              | 46Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_2_TEMP_1              | 28Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  CPU_0_DIMM_C0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_D0             | 35Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_A0             | 34Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_B0             | 34Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_G0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_H0             | 35Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_E0             | 35Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_F0             | 35Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  DIMM_VRABCD_TEMP          | 35Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  DIMM_VREFGH_TEMP          | 34Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  MAX_DIMM_TEMP             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  PML_WEST_TEMP             | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  PML_LOCAL_TEMP            | Absent     | N/A      | N/A      | N/A      | N/A      | 80       | 85       | N/A      | Intake
  PML_VDD_TEMP              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 125      | N/A      | Intake
  PML_EAST_TEMP             | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  SC_1_E810                 | Absent     | N/A      | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SC_2_E810                 | Absent     | N/A      | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SSD_0_TEMP                | 33Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  SSD_1_TEMP                | 35Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  INLET_TEMP_L              | 25Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  INLET_TEMP_R              | 24Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  MB_HSC_TEMP               | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  OUTLET_TEMP_L             | 38Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  OUTLET_TEMP_R             | 37Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  INLET_TEMP_MAX            | 25Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  OUTLET_TEMP_MAX           | 38Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  SYS_PCH_TEMP              | 33Cel      | OK       | N/A      | 5        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_TEMP                | 48Cel      | OK       | N/A      | N/A      | N/A      | 96       | 98       | N/A      | Intake
  SYS_FAN_1A                | 30%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_1B                | 30%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2A                | 30%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2B                | 30%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_1_FAN                 | 4320RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_2_FAN                 | 4160RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan

[XXXXXX@welktxefnce-h-pe1util-vm01 pdb-cpld-v12-20240220]$ IP=2607:f160:10:9249:ce:40a:0:e016
[XXXXXX@welktxefnce-h-pe1util-vm01 pdb-cpld-v12-20240220]$ rf_sensor_list.py -u XXXXXX -p XXXXXX -r https://[$IP]
Chassis 'Computer System Chassis' Status
  Sensor                    | Reading    | Health   | LF       | LC       | LNC      | UNC      | UC       | UF       | PhysicalContext
  State                     | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 212V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 186W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 211V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 156W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_V5                    | 5.0062V    | OK       | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | 12.1568V   | OK       | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | 3.2981V    | OK       | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | 1.04828V   | OK       | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  RTC_Voltage               | 3.003V     | OK       | N/A      | 2.289    | N/A      | N/A      | 3.444    | N/A      | VoltageRegulator
  CPU_0_Vcore               | 1.8192V    | OK       | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | 1.2232V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | 1.2232V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | -44Cel     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_MARGIN              | 33Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_PROCHOT             | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  PSU_1_TEMP_2              | 46Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_1_TEMP_1              | 27Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  PSU_2_TEMP_2              | 46Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_2_TEMP_1              | 28Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  CPU_0_DIMM_C0             | 39Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_D0             | 38Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_A0             | 37Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_B0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_G0             | 39Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_H0             | 38Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_E0             | 37Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_F0             | 37Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  DIMM_VRABCD_TEMP          | 35Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  DIMM_VREFGH_TEMP          | 35Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  MAX_DIMM_TEMP             | 39Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  PML_WEST_TEMP             | 55Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  PML_LOCAL_TEMP            | 53Cel      | OK       | N/A      | N/A      | N/A      | 80       | 85       | N/A      | Intake
  PML_VDD_TEMP              | 58Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 125      | N/A      | Intake
  PML_EAST_TEMP             | 54Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  SC_1_E810                 | 44Cel      | OK       | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SC_2_E810                 | 39Cel      | OK       | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SSD_0_TEMP                | 35Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  SSD_1_TEMP                | 36Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  INLET_TEMP_L              | 26Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  INLET_TEMP_R              | 25Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  MB_HSC_TEMP               | 38Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  OUTLET_TEMP_L             | 42Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  OUTLET_TEMP_R             | 40Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  INLET_TEMP_MAX            | 26Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  OUTLET_TEMP_MAX           | 42Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  SYS_PCH_TEMP              | 33Cel      | OK       | N/A      | 5        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_TEMP                | 54Cel      | OK       | N/A      | N/A      | N/A      | 96       | 98       | N/A      | Intake
  SYS_FAN_1A                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_1B                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2A                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2B                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_1_FAN                 | 4000RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_2_FAN                 | 3840RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan

[XXXXXX@welktxefnce-h-pe1util-vm01 pdb-cpld-v12-20240220]$

```


### Installation of PDB firmware 0.0.1.2

```log
[XXXXXX@welktxefnce-h-pe1util-vm01 pdb-cpld-v12-20240220]$ ./update-pdbcpld.sh 2607:f160:10:9249:ce:40a:0:e015 XXXXXX XXXXXX ./2607:f160:10:9249:ce:40a:0:e015-install.log
==============================================================
                     ZT PDBCPLD Update
                     update-PDBCPLD.sh
                     February 20, 2024
                     1.2
==============================================================

2024-02-27-11:26:10  Check if IP address is valid
2024-02-27-11:26:10  IPv6 IP detected
2024-02-27-11:26:11   2607:f160:10:9249:ce:40a:0:e015 is a valid IP
2024-02-27-11:26:11  IPv6 Address is 2607:f160:10:9249:ce:40a:0:e015
2024-02-27-11:26:12  Redfish Credentials are correct, continue update
2024-02-27-11:26:12  Check if right version of python is installed
2024-02-27-11:26:12  Python3 is installed, continue update
{ "@odata.context": "/redfish/v1/$metadata#SoftwareInventory.SoftwareInventory", "@odata.etag": "\"1708984451\"", "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/PDBCPLD", "@odata.type": "#SoftwareInventory.v1_2_3.SoftwareInventory", "Id": "PDBCPLD", "Name": "PDBCPLD", "Updateable": true, "Version": "0.0.1.0" }
2024-02-27-11:26:17  Model name is Proteus
2024-02-27-11:26:17  Product is a Proteus or Force option is selected, it is ok to proceed
2024-02-27-11:26:17  System Serial is 20741213N074
2024-02-27-11:26:17  PDBCPLD current version is 0.0.1.0
2024-02-27-11:26:17  Preparing to update PDBCPLD.....
20240227_114248 Task /redfish/v1/TaskService/Tasks/19  status : 200 Running (Percent complete = 18)
20240227_114248 Found 2 messages from [/redfish/v1/TaskService/Tasks/19]
20240227_114248 {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1709055752\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/19",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "19",
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
            "MessageId": "AmiOem.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 18,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20240227_114248     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20240227_114248     Unknown             OK          Device is flashing firmware for action /redfish/v1/UpdateService/upload.
20240227_114248 task_status : Running ... checking again
20240227_114253 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/19
20240227_114254 HTTP: 200
20240227_114254 JSON: {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1709055752\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/19",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "19",
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
            "MessageId": "AmiOem.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 18,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20240227_114254 Update status (monitor, running) : Running (Percent complete = 18)
20240227_114254 Checking task status on /redfish/v1/TaskService/Tasks/19
20240227_114254 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/19
20240227_114255 HTTP: 200
20240227_114255 JSON: {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1709055752\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/19",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "19",
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
            "MessageId": "AmiOem.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 18,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20240227_114255 Task /redfish/v1/TaskService/Tasks/19  status : 200 Running (Percent complete = 18)
20240227_114255 Found 2 messages from [/redfish/v1/TaskService/Tasks/19]
20240227_114255 {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1709055752\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/19",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "19",
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
            "MessageId": "AmiOem.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 18,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20240227_114255     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20240227_114255     Unknown             OK          Device is flashing firmware for action /redfish/v1/UpdateService/upload.
20240227_114255 task_status : Running ... checking again
20240227_114300 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/19
20240227_114300 HTTP: 200
20240227_114300 JSON: {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1709055752\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/19",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "19",
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
            "MessageId": "AmiOem.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 18,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20240227_114300 Update status (monitor, running) : Running (Percent complete = 18)
20240227_114300 Checking task status on /redfish/v1/TaskService/Tasks/19
20240227_114300 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/19
20240227_114300 HTTP: 200
20240227_114300 JSON: {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1709055752\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/19",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "19",
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
            "MessageId": "AmiOem.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 18,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20240227_114300 Task /redfish/v1/TaskService/Tasks/19  status : 200 Running (Percent complete = 18)
20240227_114300 Found 2 messages from [/redfish/v1/TaskService/Tasks/19]
20240227_114300 {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1709055752\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/19",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "19",
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
            "MessageId": "AmiOem.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 18,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20240227_114300     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20240227_114300     Unknown             OK          Device is flashing firmware for action /redfish/v1/UpdateService/upload.
20240227_114300 task_status : Running ... checking again
20240227_114305 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/19
20240227_114306 HTTP: 200
20240227_114306 JSON: {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1709055752\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/19",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "19",
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
            "MessageId": "AmiOem.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 18,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20240227_114306 Update status (monitor, running) : Running (Percent complete = 18)
20240227_114306 Checking task status on /redfish/v1/TaskService/Tasks/19
20240227_114306 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/19
20240227_114306 HTTP: 200
20240227_114306 JSON: {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1709055752\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/19",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "19",
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
            "MessageId": "AmiOem.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 18,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20240227_114306 Task /redfish/v1/TaskService/Tasks/19  status : 200 Running (Percent complete = 18)
20240227_114306 Found 2 messages from [/redfish/v1/TaskService/Tasks/19]
20240227_114306 {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1709055752\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/19",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "19",
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
            "MessageId": "AmiOem.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 18,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20240227_114306     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20240227_114306     Unknown             OK          Device is flashing firmware for action /redfish/v1/UpdateService/upload.
20240227_114306 task_status : Running ... checking again
20240227_114311 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/19
20240227_114312 HTTP: 200
20240227_114312 JSON: {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1709055752\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/19",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "19",
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
            "MessageId": "AmiOem.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 18,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20240227_114312 Update status (monitor, running) : Running (Percent complete = 18)
20240227_114312 Checking task status on /redfish/v1/TaskService/Tasks/19
20240227_114312 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/19
20240227_114313 HTTP: 200
20240227_114313 JSON: {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1709055752\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/19",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "19",
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
            "MessageId": "AmiOem.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 18,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20240227_114313 Task /redfish/v1/TaskService/Tasks/19  status : 200 Running (Percent complete = 18)
20240227_114313 Found 2 messages from [/redfish/v1/TaskService/Tasks/19]
20240227_114313 {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1709055752\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/19",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "19",
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
            "MessageId": "AmiOem.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 18,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20240227_114313     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20240227_114313     Unknown             OK          Device is flashing firmware for action /redfish/v1/UpdateService/upload.
20240227_114313 task_status : Running ... checking again
20240227_114318 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/19
20240227_114318 HTTP: 200
20240227_114318 JSON: {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1709055752\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/19",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "19",
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
            "MessageId": "AmiOem.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 18,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20240227_114318 Update status (monitor, running) : Running (Percent complete = 18)
20240227_114318 Checking task status on /redfish/v1/TaskService/Tasks/19
20240227_114318 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/19
20240227_114319 HTTP: 200
20240227_114319 JSON: {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1709055752\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/19",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "19",
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
            "MessageId": "AmiOem.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 18,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20240227_114319 Task /redfish/v1/TaskService/Tasks/19  status : 200 Running (Percent complete = 18)
20240227_114319 Found 2 messages from [/redfish/v1/TaskService/Tasks/19]
20240227_114319 {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1709055752\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/19",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "19",
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
            "MessageId": "AmiOem.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 18,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20240227_114319     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20240227_114319     Unknown             OK          Device is flashing firmware for action /redfish/v1/UpdateService/upload.
20240227_114319 task_status : Running ... checking again
20240227_114324 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/19
20240227_114325 HTTP: 200
20240227_114325 JSON: {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1709055752\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/19",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "19",
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
            "MessageId": "AmiOem.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 18,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20240227_114325 Update status (monitor, running) : Running (Percent complete = 18)
20240227_114325 Checking task status on /redfish/v1/TaskService/Tasks/19
20240227_114325 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/19
20240227_114326 HTTP: 200
20240227_114326 JSON: {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1709055752\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/19",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "19",
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
            "MessageId": "AmiOem.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 18,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20240227_114326 Task /redfish/v1/TaskService/Tasks/19  status : 200 Running (Percent complete = 18)
20240227_114326 Found 2 messages from [/redfish/v1/TaskService/Tasks/19]
20240227_114326 {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1709055752\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/19",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "19",
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
            "MessageId": "AmiOem.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 18,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20240227_114326     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20240227_114326     Unknown             OK          Device is flashing firmware for action /redfish/v1/UpdateService/upload.
20240227_114326 task_status : Running ... checking again
20240227_114331 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/19
20240227_114333 HTTP: 200
20240227_114333 JSON: {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1709055752\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/19",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "19",
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
            "MessageId": "AmiOem.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 18,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20240227_114333 Update status (monitor, running) : Running (Percent complete = 18)
20240227_114333 Checking task status on /redfish/v1/TaskService/Tasks/19
20240227_114333 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/19
20240227_114336 HTTP: 200
20240227_114336 JSON: {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1709055752\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/19",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "19",
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
            "MessageId": "AmiOem.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 18,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20240227_114336 Task /redfish/v1/TaskService/Tasks/19  status : 200 Running (Percent complete = 18)
20240227_114336 Found 2 messages from [/redfish/v1/TaskService/Tasks/19]
20240227_114336 {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1709055752\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/19",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "19",
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
            "MessageId": "AmiOem.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 18,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20240227_114336     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20240227_114336     Unknown             OK          Device is flashing firmware for action /redfish/v1/UpdateService/upload.
20240227_114336 task_status : Running ... checking again
20240227_114341 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/19
20240227_114344 HTTP: 200
20240227_114344 JSON: {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1709055752\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/19",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "EndTime": "2024-02-27T17:43:41+00:00",
    "Id": "19",
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
            "MessageId": "AmiOem.1.0.FirmwareUpdateCompleted",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 100,
    "TaskState": "Completed",
    "TaskStatus": "OK"
}
20240227_114344 Update status (monitor, running) : Completed (Percent complete = 100)
20240227_114344 Update completed successfully
20240227_114404 Checking task status on /redfish/v1/TaskService/Tasks/19
20240227_114404 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/19
20240227_114405 HTTP: 200
20240227_114405 JSON: {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1709055752\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/19",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "EndTime": "2024-02-27T17:43:41+00:00",
    "Id": "19",
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
            "MessageId": "AmiOem.1.0.FirmwareUpdateCompleted",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 100,
    "TaskState": "Completed",
    "TaskStatus": "OK"
}
20240227_114405 Task /redfish/v1/TaskService/Tasks/19  status : 200 Completed (Percent complete = 100)
20240227_114405 Found 2 messages from [/redfish/v1/TaskService/Tasks/19]
20240227_114405 {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1709055752\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/19",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "EndTime": "2024-02-27T17:43:41+00:00",
    "Id": "19",
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
            "MessageId": "AmiOem.1.0.FirmwareUpdateCompleted",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 100,
    "TaskState": "Completed",
    "TaskStatus": "OK"
}
20240227_114405     Unknown             OK          Task /redfish/v1/UpdateService/upload has completed.
20240227_114405     Unknown             OK          Action /redfish/v1/UpdateService/upload firmware update is completed.
20240227_114405 FW update completed -- waiting 20 seconds before checking for new version
20240227_114425 Polling for up to 600 seconds to detect new FW versions
20240227_114425 Target: PDBCPLD                          Any
20240227_114425 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/UpdateService/FirmwareInventory/PDBCPLD
20240227_114426 HTTP: 200
20240227_114426 JSON: {
    "@odata.context": "/redfish/v1/$metadata#SoftwareInventory.SoftwareInventory",
    "@odata.etag": "\"1708984451\"",
    "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/PDBCPLD",
    "@odata.type": "#SoftwareInventory.v1_2_3.SoftwareInventory",
    "Id": "PDBCPLD",
    "Name": "PDBCPLD",
    "Updateable": true,
    "Version": "0.0.1.2"
}
20240227_114426 {
    "@odata.context": "/redfish/v1/$metadata#SoftwareInventory.SoftwareInventory",
    "@odata.etag": "\"1708984451\"",
    "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/PDBCPLD",
    "@odata.type": "#SoftwareInventory.v1_2_3.SoftwareInventory",
    "Id": "PDBCPLD",
    "Name": "PDBCPLD",
    "Updateable": true,
    "Version": "0.0.1.2"
}
20240227_114426 fwversion = [Version] [0.0.1.2]
20240227_114426 Obtained 1 of 1 FW versions
20240227_114426 Final PDBCPLD FW version: [0.0.1.2]
20240227_114426 Checking for final FW version match
Statistics: starts
datetime,ecode,nerrs,fw_imgfile,fwver_start,fwver_end,fwver_expected,component_type,component_name,component_count,component_updated,bmc_ip,oshost_ip,osping_pre_secs,osping_total_secs,osping_pass,osping_fail,wait_before_update_poll_start,wait_after_poll_complete,poll_time_for_update_start,poll_time_for_update_complete,poll_time_for_post,poll_count_for_post,poll_time_for_version,poll_count_for_version,do_reboot,do_clear_sel_log,total_time,initiate_fwupdate_time,wait_for_update_done_time,iterate_for_post_complete_time,wait_for_version_available_time,wait_for_host_status_time,
20240227_114228,0,0,Proteus_CM_PVT_v12_20230518.jed,0.0.1.0,0.0.1.2,,PDBCPLD,PDBCPLD,1,1,[2607:f160:10:9249:ce:40a:0:e015],,10,120,0,0,0,20,60,1500,0,2,600,2,0,0,118,2,91,0,1,0
Statistics: ends
20240227_114426 Process completed successfully
2024-02-27-11:44:26  Final Check
2024-02-27-11:44:27  Version of the previous PDBCPLD: 0.0.1.0
2024-02-27-11:44:27  Version of the new PDBCPLD: 0.0.1.2

PDBCPLD updated Successfully to 0.0.1.2
[XXXXXX@welktxefnce-h-pe1util-vm01 pdb-cpld-v12-20240220]$


```

## check the sensors after the installation of new PDB firmware

```log
[XXXXXX@welktxefnce-h-pe1util-vm01 pdb-cpld-v12-20240220]$ IP=2607:f160:10:9249:ce:40a:0:e015
[XXXXXX@welktxefnce-h-pe1util-vm01 pdb-cpld-v12-20240220]$ rf_sensor_list.py -u XXXXXX -p XXXXXX -r https://[$IP]
Chassis 'Computer System Chassis' Status
  Sensor                    | Reading    | Health   | LF       | LC       | LNC      | UNC      | UC       | UF       | PhysicalContext
  State                     | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 213V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 212V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_V5                    | Absent     | N/A      | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | Absent     | N/A      | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | Absent     | N/A      | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | Absent     | N/A      | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  RTC_Voltage               | 3.01V      | OK       | N/A      | 2.289    | N/A      | N/A      | 3.444    | N/A      | VoltageRegulator
  CPU_0_Vcore               | Absent     | N/A      | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_MARGIN              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_PROCHOT             | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  PSU_1_TEMP_2              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_1_TEMP_1              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  PSU_2_TEMP_2              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_2_TEMP_1              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  CPU_0_DIMM_C0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_D0             | 35Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_A0             | 34Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_B0             | 34Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_G0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_H0             | 35Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_E0             | 35Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_F0             | 35Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  DIMM_VRABCD_TEMP          | 35Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  DIMM_VREFGH_TEMP          | 34Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  MAX_DIMM_TEMP             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  PML_WEST_TEMP             | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  PML_LOCAL_TEMP            | Absent     | N/A      | N/A      | N/A      | N/A      | 80       | 85       | N/A      | Intake
  PML_VDD_TEMP              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 125      | N/A      | Intake
  PML_EAST_TEMP             | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  SC_1_E810                 | Absent     | N/A      | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SC_2_E810                 | Absent     | N/A      | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SSD_0_TEMP                | Absent     | N/A      | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  SSD_1_TEMP                | Absent     | N/A      | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  INLET_TEMP_L              | 25Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  INLET_TEMP_R              | 24Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  MB_HSC_TEMP               | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  OUTLET_TEMP_L             | 38Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  OUTLET_TEMP_R             | 37Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  INLET_TEMP_MAX            | 25Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  OUTLET_TEMP_MAX           | 38Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  SYS_PCH_TEMP              | 33Cel      | OK       | N/A      | 5        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_TEMP                | 48Cel      | OK       | N/A      | N/A      | N/A      | 96       | 98       | N/A      | Intake
  SYS_FAN_1A                | 29%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_1B                | 29%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2A                | 29%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2B                | 29%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_1_FAN                 | Absent     | N/A      | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_2_FAN                 | Absent     | N/A      | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan

[XXXXXX@welktxefnce-h-pe1util-vm01 pdb-cpld-v12-20240220]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[${IP}]/redfish/v1/UpdateService/FirmwareInventory/PDBCPLD | jq .
{
  "@odata.context": "/redfish/v1/$metadata#SoftwareInventory.SoftwareInventory",
  "@odata.etag": "\"1708984451\"",
  "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/PDBCPLD",
  "@odata.type": "#SoftwareInventory.v1_2_3.SoftwareInventory",
  "Id": "PDBCPLD",
  "Name": "PDBCPLD",
  "Updateable": true,
  "Version": "0.0.1.2"
}
[XXXXXX@welktxefnce-h-pe1util-vm01 pdb-cpld-v12-20240220]$

[XXXXXX@welktxefnce-h-pe1util-vm01 pdb-cpld-v12-20240220]$ IP=2607:f160:10:9249:ce:40a:0:e016
[XXXXXX@welktxefnce-h-pe1util-vm01 pdb-cpld-v12-20240220]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[${IP}]/redfish/v1/UpdateService/FirmwareInventory/PDBCPLD | jq .
{
  "@odata.context": "/redfish/v1/$metadata#SoftwareInventory.SoftwareInventory",
  "@odata.etag": "\"1708629990\"",
  "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/PDBCPLD",
  "@odata.type": "#SoftwareInventory.v1_2_3.SoftwareInventory",
  "Id": "PDBCPLD",
  "Name": "PDBCPLD",
  "Updateable": false,
  "Version": "0.0.1.2"
}
[XXXXXX@welktxefnce-h-pe1util-vm01 pdb-cpld-v12-20240220]$ rf_sensor_list.py -u XXXXXX -p XXXXXX -r https://[$IP]
Chassis 'Computer System Chassis' Status
  Sensor                    | Reading    | Health   | LF       | LC       | LNC      | UNC      | UC       | UF       | PhysicalContext
  State                     | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 213V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 180W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 212V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 168W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_V5                    | 5.0062V    | OK       | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | 12.1568V   | OK       | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | 3.3083V    | OK       | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | 1.04664V   | OK       | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  RTC_Voltage               | 3.003V     | OK       | N/A      | 2.289    | N/A      | N/A      | 3.444    | N/A      | VoltageRegulator
  CPU_0_Vcore               | 1.8164V    | OK       | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | 1.2232V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | 1.2232V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | -45Cel     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_MARGIN              | 33Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_PROCHOT             | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  PSU_1_TEMP_2              | 46Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_1_TEMP_1              | 28Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  PSU_2_TEMP_2              | 46Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_2_TEMP_1              | 28Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  CPU_0_DIMM_C0             | 39Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_D0             | 38Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_A0             | 37Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_B0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_G0             | 39Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_H0             | 38Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_E0             | 38Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_F0             | 37Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  DIMM_VRABCD_TEMP          | 35Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  DIMM_VREFGH_TEMP          | 35Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  MAX_DIMM_TEMP             | 39Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  PML_WEST_TEMP             | 55Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  PML_LOCAL_TEMP            | 53Cel      | OK       | N/A      | N/A      | N/A      | 80       | 85       | N/A      | Intake
  PML_VDD_TEMP              | 58Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 125      | N/A      | Intake
  PML_EAST_TEMP             | 54Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  SC_1_E810                 | 44Cel      | OK       | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SC_2_E810                 | 39Cel      | OK       | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SSD_0_TEMP                | 35Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  SSD_1_TEMP                | 36Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  INLET_TEMP_L              | 27Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  INLET_TEMP_R              | 25Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  MB_HSC_TEMP               | 38Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  OUTLET_TEMP_L             | 42Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  OUTLET_TEMP_R             | 40Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  INLET_TEMP_MAX            | 27Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  OUTLET_TEMP_MAX           | 42Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  SYS_PCH_TEMP              | 34Cel      | OK       | N/A      | 5        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_TEMP                | 53Cel      | OK       | N/A      | N/A      | N/A      | 96       | 98       | N/A      | Intake
  SYS_FAN_1A                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_1B                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2A                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2B                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_1_FAN                 | 3840RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_2_FAN                 | 3840RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan

[XXXXXX@welktxefnce-h-pe1util-vm01 pdb-cpld-v12-20240220]$
```

## lets AcPowerCycle it with a redfish command to see if this clears.

```log
[XXXXXX@welktxefnce-h-pe1util-vm01 pdb-cpld-v12-20240220]$ IP=2607:f160:10:9249:ce:40a:0:e015
[XXXXXX@welktxefnce-h-pe1util-vm01 pdb-cpld-v12-20240220]$ curl --globoff -L -w "%{http_code} %{url_effective}\\n" -ku XXXXXX:XXXXXX -H "Content-Type: application/json" -X POST https://[$IP]/redfish/v1/Chassis/Self/Actions/Oem/AcReset -d '{"ResetType": "AcPowerCycle"}'
{"@odata.context":"/redfish/v1/$metadata#Task.Task","@odata.id":"/redfish/v1/TaskService/Tasks/20","@odata.type":"#Task.v1_4_2.Task","Description":"Task for Chassis AC Power Reset","Id":"20","Name":"Chassis AC Power Reset","TaskState":"New"}202 https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Chassis/Self/Actions/Oem/AcReset
[XXXXXX@welktxefnce-h-pe1util-vm01 pdb-cpld-v12-20240220]$
```
## looking at the sensors again with rf_sensor_list.py
## Strange, it shows issues, then they clear, then they come back

```log
[XXXXXX@welktxefnce-h-pe1util-vm01 pdb-cpld-v12-20240220]$ IP=2607:f160:10:9249:ce:40a:0:e015
[XXXXXX@welktxefnce-h-pe1util-vm01 pdb-cpld-v12-20240220]$ rf_sensor_list.py -u XXXXXX -p XXXXXX -r https://[$IP]
Chassis 'Computer System Chassis' Status
  Sensor                    | Reading    | Health   | LF       | LC       | LNC      | UNC      | UC       | UF       | PhysicalContext
  State                     | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 213V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 222W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 212V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 210W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_V5                    | 5.053V     | OK       | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | 12.0816V   | OK       | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | 3.3287V    | OK       | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | 1.05484V   | OK       | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  RTC_Voltage               | 3.024V     | OK       | N/A      | 2.289    | N/A      | N/A      | 3.444    | N/A      | VoltageRegulator
  CPU_0_Vcore               | 1.822V     | OK       | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | 1.2306V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | 1.2306V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | -63Cel     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_MARGIN              | 53Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  PSU_1_TEMP_2              | 46Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_1_TEMP_1              | 27Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  PSU_2_TEMP_2              | 45Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_2_TEMP_1              | 27Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  CPU_0_DIMM_C0             | 30Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_D0             | 29Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_A0             | 29Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_B0             | 29Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_G0             | 30Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_H0             | 30Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_E0             | 30Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_F0             | 30Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  DIMM_VRABCD_TEMP          | 30Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  DIMM_VREFGH_TEMP          | 30Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  MAX_DIMM_TEMP             | 30Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  PML_WEST_TEMP             | 44Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  PML_LOCAL_TEMP            | 38Cel      | OK       | N/A      | N/A      | N/A      | 80       | 85       | N/A      | Intake
  PML_VDD_TEMP              | 43Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 125      | N/A      | Intake
  PML_EAST_TEMP             | 44Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  SC_1_E810                 | 34Cel      | OK       | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SC_2_E810                 | 33Cel      | OK       | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SSD_0_TEMP                | 31Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  SSD_1_TEMP                | 32Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  INLET_TEMP_L              | 24Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  INLET_TEMP_R              | 23Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  MB_HSC_TEMP               | 34Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  OUTLET_TEMP_L             | 35Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  OUTLET_TEMP_R             | 36Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  INLET_TEMP_MAX            | 24Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  OUTLET_TEMP_MAX           | 36Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  SYS_PCH_TEMP              | Absent     | N/A      | N/A      | 5        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_TEMP                | 35Cel      | OK       | N/A      | N/A      | N/A      | 96       | 98       | N/A      | Intake
  SYS_FAN_1A                | 100%       | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_1B                | 100%       | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2A                | 100%       | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2B                | 100%       | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_1_FAN                 | 4000RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_2_FAN                 | 4000RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan

[XXXXXX@welktxefnce-h-pe1util-vm01 pdb-cpld-v12-20240220]$ rf_sensor_list.py -u XXXXXX -p XXXXXX -r https://[$IP]
Chassis 'Computer System Chassis' Status
  Sensor                    | Reading    | Health   | LF       | LC       | LNC      | UNC      | UC       | UF       | PhysicalContext
  State                     | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 213V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 222W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 212V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 216W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_V5                    | 5.053V     | OK       | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | 12.0816V   | OK       | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | 3.3287V    | OK       | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | 1.0532V    | OK       | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  RTC_Voltage               | 3.024V     | OK       | N/A      | 2.289    | N/A      | N/A      | 3.444    | N/A      | VoltageRegulator
  CPU_0_Vcore               | 1.8248V    | OK       | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | 1.2269V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | 1.2306V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | -64Cel     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_MARGIN              | 53Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  PSU_1_TEMP_2              | 46Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_1_TEMP_1              | 27Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  PSU_2_TEMP_2              | 45Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_2_TEMP_1              | 28Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  CPU_0_DIMM_C0             | 30Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_D0             | 29Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_A0             | 28Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_B0             | 29Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_G0             | 29Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_H0             | 29Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_E0             | 30Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_F0             | 30Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  DIMM_VRABCD_TEMP          | 30Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  DIMM_VREFGH_TEMP          | 30Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  MAX_DIMM_TEMP             | 30Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  PML_WEST_TEMP             | 43Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  PML_LOCAL_TEMP            | 37Cel      | OK       | N/A      | N/A      | N/A      | 80       | 85       | N/A      | Intake
  PML_VDD_TEMP              | 42Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 125      | N/A      | Intake
  PML_EAST_TEMP             | 43Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  SC_1_E810                 | 34Cel      | OK       | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SC_2_E810                 | 33Cel      | OK       | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SSD_0_TEMP                | 30Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  SSD_1_TEMP                | 32Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  INLET_TEMP_L              | 24Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  INLET_TEMP_R              | 24Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  MB_HSC_TEMP               | 34Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  OUTLET_TEMP_L             | 34Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  OUTLET_TEMP_R             | 35Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  INLET_TEMP_MAX            | 24Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  OUTLET_TEMP_MAX           | 35Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  SYS_PCH_TEMP              | 29Cel      | OK       | N/A      | 5        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_TEMP                | 34Cel      | OK       | N/A      | N/A      | N/A      | 96       | 98       | N/A      | Intake
  SYS_FAN_1A                | 95%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_1B                | 95%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2A                | 95%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2B                | 95%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_1_FAN                 | 4000RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_2_FAN                 | 4000RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan

[XXXXXX@welktxefnce-h-pe1util-vm01 pdb-cpld-v12-20240220]$ rf_sensor_list.py -u XXXXXX -p XXXXXX -r https://[$IP]
Chassis 'Computer System Chassis' Status
  Sensor                    | Reading    | Health   | LF       | LC       | LNC      | UNC      | UC       | UF       | PhysicalContext
  State                     | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 213V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 210W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 212V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 198W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_V5                    | 5.053V     | OK       | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | 12.1004V   | OK       | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | 3.3287V    | OK       | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | 1.0532V    | OK       | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  RTC_Voltage               | 3.024V     | OK       | N/A      | 2.289    | N/A      | N/A      | 3.444    | N/A      | VoltageRegulator
  CPU_0_Vcore               | 1.822V     | OK       | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | 1.2306V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | 1.2306V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | -64Cel     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_MARGIN              | 53Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  PSU_1_TEMP_2              | 46Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_1_TEMP_1              | 28Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  PSU_2_TEMP_2              | 45Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_2_TEMP_1              | 28Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  CPU_0_DIMM_C0             | 30Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_D0             | 29Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_A0             | 28Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_B0             | 29Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_G0             | 29Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_H0             | 29Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_E0             | 30Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_F0             | 29Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  DIMM_VRABCD_TEMP          | 30Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  DIMM_VREFGH_TEMP          | 30Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  MAX_DIMM_TEMP             | 30Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  PML_WEST_TEMP             | 43Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  PML_LOCAL_TEMP            | 37Cel      | OK       | N/A      | N/A      | N/A      | 80       | 85       | N/A      | Intake
  PML_VDD_TEMP              | 41Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 125      | N/A      | Intake
  PML_EAST_TEMP             | 42Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  SC_1_E810                 | 34Cel      | OK       | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SC_2_E810                 | 34Cel      | OK       | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SSD_0_TEMP                | 30Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  SSD_1_TEMP                | 31Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  INLET_TEMP_L              | 25Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  INLET_TEMP_R              | 24Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  MB_HSC_TEMP               | 33Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  OUTLET_TEMP_L             | 33Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  OUTLET_TEMP_R             | 34Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  INLET_TEMP_MAX            | 25Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  OUTLET_TEMP_MAX           | 34Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  SYS_PCH_TEMP              | 29Cel      | OK       | N/A      | 5        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_TEMP                | 34Cel      | OK       | N/A      | N/A      | N/A      | 96       | 98       | N/A      | Intake
  SYS_FAN_1A                | 81%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_1B                | 81%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2A                | 81%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2B                | 81%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_1_FAN                 | 4000RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_2_FAN                 | 4000RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan

[XXXXXX@welktxefnce-h-pe1util-vm01 pdb-cpld-v12-20240220]$ rf_sensor_list.py -u XXXXXX -p XXXXXX -r https://[$IP]
Chassis 'Computer System Chassis' Status
  Sensor                    | Reading    | Health   | LF       | LC       | LNC      | UNC      | UC       | UF       | PhysicalContext
  State                     | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 213V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 198W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 212V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 186W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_V5                    | 5.053V     | OK       | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | 12.1192V   | OK       | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | 3.3236V    | OK       | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | 1.05484V   | OK       | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  RTC_Voltage               | 3.024V     | OK       | N/A      | 2.289    | N/A      | N/A      | 3.444    | N/A      | VoltageRegulator
  CPU_0_Vcore               | 1.8248V    | OK       | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | 1.2306V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | 1.2306V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | -64Cel     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_MARGIN              | 53Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  PSU_1_TEMP_2              | 46Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_1_TEMP_1              | 28Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  PSU_2_TEMP_2              | 46Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_2_TEMP_1              | 28Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  CPU_0_DIMM_C0             | 30Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_D0             | 29Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_A0             | 28Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_B0             | 29Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_G0             | 29Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_H0             | 29Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_E0             | 30Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_F0             | 29Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  DIMM_VRABCD_TEMP          | 30Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  DIMM_VREFGH_TEMP          | 30Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  MAX_DIMM_TEMP             | 30Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  PML_WEST_TEMP             | 43Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  PML_LOCAL_TEMP            | 37Cel      | OK       | N/A      | N/A      | N/A      | 80       | 85       | N/A      | Intake
  PML_VDD_TEMP              | 41Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 125      | N/A      | Intake
  PML_EAST_TEMP             | 42Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  SC_1_E810                 | 34Cel      | OK       | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SC_2_E810                 | 34Cel      | OK       | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SSD_0_TEMP                | 30Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  SSD_1_TEMP                | 31Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  INLET_TEMP_L              | 25Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  INLET_TEMP_R              | 24Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  MB_HSC_TEMP               | 33Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  OUTLET_TEMP_L             | 33Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  OUTLET_TEMP_R             | 34Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  INLET_TEMP_MAX            | 25Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  OUTLET_TEMP_MAX           | 34Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  SYS_PCH_TEMP              | 29Cel      | OK       | N/A      | 5        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_TEMP                | 34Cel      | OK       | N/A      | N/A      | N/A      | 96       | 98       | N/A      | Intake
  SYS_FAN_1A                | 74%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_1B                | 74%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2A                | 74%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2B                | 74%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_1_FAN                 | 4000RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_2_FAN                 | 4000RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan

[XXXXXX@welktxefnce-h-pe1util-vm01 pdb-cpld-v12-20240220]$ rf_sensor_list.py -u XXXXXX -p XXXXXX -r https://[$IP]
Chassis 'Computer System Chassis' Status
  Sensor                    | Reading    | Health   | LF       | LC       | LNC      | UNC      | UC       | UF       | PhysicalContext
  State                     | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 213V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 174W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 212V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 162W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_V5                    | 5.053V     | OK       | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | 12.138V    | OK       | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | 3.3236V    | OK       | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | 1.0532V    | OK       | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  RTC_Voltage               | 3.024V     | OK       | N/A      | 2.289    | N/A      | N/A      | 3.444    | N/A      | VoltageRegulator
  CPU_0_Vcore               | 1.822V     | OK       | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | 1.2306V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | 1.2306V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | -63Cel     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_MARGIN              | 51Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  PSU_1_TEMP_2              | 46Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_1_TEMP_1              | 27Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  PSU_2_TEMP_2              | 46Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_2_TEMP_1              | 27Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  CPU_0_DIMM_C0             | 30Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_D0             | 30Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_A0             | 29Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_B0             | 29Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_G0             | 30Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_H0             | 30Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_E0             | 30Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_F0             | 30Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  DIMM_VRABCD_TEMP          | 30Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  DIMM_VREFGH_TEMP          | 30Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  MAX_DIMM_TEMP             | 30Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  PML_WEST_TEMP             | 44Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  PML_LOCAL_TEMP            | 39Cel      | OK       | N/A      | N/A      | N/A      | 80       | 85       | N/A      | Intake
  PML_VDD_TEMP              | 43Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 125      | N/A      | Intake
  PML_EAST_TEMP             | 43Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  SC_1_E810                 | 35Cel      | OK       | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SC_2_E810                 | 34Cel      | OK       | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SSD_0_TEMP                | 30Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  SSD_1_TEMP                | 31Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  INLET_TEMP_L              | 24Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  INLET_TEMP_R              | 23Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  MB_HSC_TEMP               | 32Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  OUTLET_TEMP_L             | 33Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  OUTLET_TEMP_R             | 33Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  INLET_TEMP_MAX            | 24Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  OUTLET_TEMP_MAX           | 33Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  SYS_PCH_TEMP              | 29Cel      | OK       | N/A      | 5        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_TEMP                | 35Cel      | OK       | N/A      | N/A      | N/A      | 96       | 98       | N/A      | Intake
  SYS_FAN_1A                | 29%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_1B                | 29%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2A                | 29%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2B                | 29%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_1_FAN                 | 3840RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_2_FAN                 | 4000RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan

[XXXXXX@welktxefnce-h-pe1util-vm01 pdb-cpld-v12-20240220]$ rf_sensor_list.py -u XXXXXX -p XXXXXX -r https://[$IP]
Chassis 'Computer System Chassis' Status
  Sensor                    | Reading    | Health   | LF       | LC       | LNC      | UNC      | UC       | UF       | PhysicalContext
  State                     | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 213V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 174W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 212V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 162W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_V5                    | Absent     | N/A      | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | Absent     | N/A      | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | Absent     | N/A      | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | Absent     | N/A      | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  RTC_Voltage               | 3.017V     | OK       | N/A      | 2.289    | N/A      | N/A      | 3.444    | N/A      | VoltageRegulator
  CPU_0_Vcore               | Absent     | N/A      | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_MARGIN              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  PSU_1_TEMP_2              | 46Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_1_TEMP_1              | 27Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  PSU_2_TEMP_2              | 46Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_2_TEMP_1              | 27Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  CPU_0_DIMM_C0             | 30Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_D0             | 30Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_A0             | 29Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_B0             | 29Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_G0             | 30Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_H0             | 30Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_E0             | 30Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_F0             | 30Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  DIMM_VRABCD_TEMP          | 31Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  DIMM_VREFGH_TEMP          | 30Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  MAX_DIMM_TEMP             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  PML_WEST_TEMP             | 44Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  PML_LOCAL_TEMP            | 40Cel      | OK       | N/A      | N/A      | N/A      | 80       | 85       | N/A      | Intake
  PML_VDD_TEMP              | 43Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 125      | N/A      | Intake
  PML_EAST_TEMP             | 44Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  SC_1_E810                 | Absent     | N/A      | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SC_2_E810                 | Absent     | N/A      | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SSD_0_TEMP                | 30Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  SSD_1_TEMP                | 31Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  INLET_TEMP_L              | 24Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  INLET_TEMP_R              | 23Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  MB_HSC_TEMP               | 32Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  OUTLET_TEMP_L             | 33Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  OUTLET_TEMP_R             | 33Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  INLET_TEMP_MAX            | 24Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  OUTLET_TEMP_MAX           | 33Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  SYS_PCH_TEMP              | 29Cel      | OK       | N/A      | 5        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_TEMP                | 40Cel      | OK       | N/A      | N/A      | N/A      | 96       | 98       | N/A      | Intake
  SYS_FAN_1A                | 29%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_1B                | 29%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2A                | 29%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2B                | 29%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_1_FAN                 | 3840RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_2_FAN                 | 4000RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan

[XXXXXX@welktxefnce-h-pe1util-vm01 pdb-cpld-v12-20240220]$


```
## I just wait and look at sensors again, it appears the left sled is having an issue reading the sensors,

```log
[XXXXXX@welktxefnce-h-pe1util-vm01 pdb-cpld-v12-20240220]$ IP=2607:f160:10:9249:ce:40a:0:e015
[XXXXXX@welktxefnce-h-pe1util-vm01 pdb-cpld-v12-20240220]$ rf_sensor_list.py -u XXXXXX -p XXXXXX -r https://[$IP]
Chassis 'Computer System Chassis' Status
  Sensor                    | Reading    | Health   | LF       | LC       | LNC      | UNC      | UC       | UF       | PhysicalContext
  State                     | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 213V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 212V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_V5                    | Absent     | N/A      | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | Absent     | N/A      | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | Absent     | N/A      | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | Absent     | N/A      | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  RTC_Voltage               | 3.01V      | OK       | N/A      | 2.289    | N/A      | N/A      | 3.444    | N/A      | VoltageRegulator
  CPU_0_Vcore               | Absent     | N/A      | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_MARGIN              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  PSU_1_TEMP_2              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_1_TEMP_1              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  PSU_2_TEMP_2              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_2_TEMP_1              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  CPU_0_DIMM_C0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_D0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_A0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_B0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_G0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_H0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_E0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_F0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  DIMM_VRABCD_TEMP          | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  DIMM_VREFGH_TEMP          | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  MAX_DIMM_TEMP             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  PML_WEST_TEMP             | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  PML_LOCAL_TEMP            | Absent     | N/A      | N/A      | N/A      | N/A      | 80       | 85       | N/A      | Intake
  PML_VDD_TEMP              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 125      | N/A      | Intake
  PML_EAST_TEMP             | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  SC_1_E810                 | Absent     | N/A      | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SC_2_E810                 | Absent     | N/A      | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SSD_0_TEMP                | Absent     | N/A      | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  SSD_1_TEMP                | Absent     | N/A      | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  INLET_TEMP_L              | 26Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  INLET_TEMP_R              | 24Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  MB_HSC_TEMP               | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  OUTLET_TEMP_L             | 36Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  OUTLET_TEMP_R             | 35Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  INLET_TEMP_MAX            | 26Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  OUTLET_TEMP_MAX           | 36Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  SYS_PCH_TEMP              | Absent     | N/A      | N/A      | 5        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_TEMP                | Absent     | N/A      | N/A      | N/A      | N/A      | 96       | 98       | N/A      | Intake
  SYS_FAN_1A                | Absent%    | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_1B                | Absent%    | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2A                | Absent%    | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2B                | Absent%    | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_1_FAN                 | Absent     | N/A      | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_2_FAN                 | Absent     | N/A      | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan

[XXXXXX@welktxefnce-h-pe1util-vm01 pdb-cpld-v12-20240220]$ rf_sensor_list.py -u XXXXXX -p XXXXXX -r https://[$IP]
Chassis 'Computer System Chassis' Status
  Sensor                    | Reading    | Health   | LF       | LC       | LNC      | UNC      | UC       | UF       | PhysicalContext
  State                     | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 213V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 212V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_V5                    | Absent     | N/A      | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | Absent     | N/A      | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | Absent     | N/A      | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | Absent     | N/A      | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  RTC_Voltage               | 3.017V     | OK       | N/A      | 2.289    | N/A      | N/A      | 3.444    | N/A      | VoltageRegulator
  CPU_0_Vcore               | Absent     | N/A      | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_MARGIN              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  PSU_1_TEMP_2              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_1_TEMP_1              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  PSU_2_TEMP_2              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_2_TEMP_1              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  CPU_0_DIMM_C0             | 35Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_D0             | 34Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_A0             | 33Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_B0             | 33Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_G0             | 35Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_H0             | 34Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_E0             | 34Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_F0             | 34Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  DIMM_VRABCD_TEMP          | 34Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  DIMM_VREFGH_TEMP          | 33Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  MAX_DIMM_TEMP             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  PML_WEST_TEMP             | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  PML_LOCAL_TEMP            | Absent     | N/A      | N/A      | N/A      | N/A      | 80       | 85       | N/A      | Intake
  PML_VDD_TEMP              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 125      | N/A      | Intake
  PML_EAST_TEMP             | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  SC_1_E810                 | Absent     | N/A      | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SC_2_E810                 | Absent     | N/A      | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SSD_0_TEMP                | Absent     | N/A      | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  SSD_1_TEMP                | Absent     | N/A      | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  INLET_TEMP_L              | 26Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  INLET_TEMP_R              | 25Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  MB_HSC_TEMP               | 34Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  OUTLET_TEMP_L             | 36Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  OUTLET_TEMP_R             | 35Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  INLET_TEMP_MAX            | 26Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  OUTLET_TEMP_MAX           | 36Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  SYS_PCH_TEMP              | 32Cel      | OK       | N/A      | 5        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_TEMP                | 47Cel      | OK       | N/A      | N/A      | N/A      | 96       | 98       | N/A      | Intake
  SYS_FAN_1A                | 30%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_1B                | 30%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2A                | 30%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2B                | 30%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_1_FAN                 | Absent     | N/A      | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_2_FAN                 | Absent     | N/A      | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan

[XXXXXX@welktxefnce-h-pe1util-vm01 pdb-cpld-v12-20240220]$ rf_sensor_list.py -u XXXXXX -p XXXXXX -r https://[$IP]
Chassis 'Computer System Chassis' Status
  Sensor                    | Reading    | Health   | LF       | LC       | LNC      | UNC      | UC       | UF       | PhysicalContext
  State                     | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 213V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 1530W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 212V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 1530W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_V5                    | Absent     | N/A      | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | Absent     | N/A      | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | Absent     | N/A      | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | Absent     | N/A      | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  RTC_Voltage               | 3.017V     | OK       | N/A      | 2.289    | N/A      | N/A      | 3.444    | N/A      | VoltageRegulator
  CPU_0_Vcore               | Absent     | N/A      | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_MARGIN              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  PSU_1_TEMP_2              | 46Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_1_TEMP_1              | 28Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  PSU_2_TEMP_2              | 46Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_2_TEMP_1              | 28Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  CPU_0_DIMM_C0             | 35Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_D0             | 34Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_A0             | 33Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_B0             | 33Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_G0             | 35Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_H0             | 34Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_E0             | 34Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_F0             | 34Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  DIMM_VRABCD_TEMP          | 34Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  DIMM_VREFGH_TEMP          | 33Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  MAX_DIMM_TEMP             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  PML_WEST_TEMP             | 54Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  PML_LOCAL_TEMP            | 51Cel      | OK       | N/A      | N/A      | N/A      | 80       | 85       | N/A      | Intake
  PML_VDD_TEMP              | 55Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 125      | N/A      | Intake
  PML_EAST_TEMP             | 54Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  SC_1_E810                 | Absent     | N/A      | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SC_2_E810                 | Absent     | N/A      | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SSD_0_TEMP                | 33Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  SSD_1_TEMP                | 34Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  INLET_TEMP_L              | 25Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  INLET_TEMP_R              | 24Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  MB_HSC_TEMP               | 34Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  OUTLET_TEMP_L             | 36Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  OUTLET_TEMP_R             | 35Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  INLET_TEMP_MAX            | 25Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  OUTLET_TEMP_MAX           | 36Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  SYS_PCH_TEMP              | 32Cel      | OK       | N/A      | 5        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_TEMP                | 47Cel      | OK       | N/A      | N/A      | N/A      | 96       | 98       | N/A      | Intake
  SYS_FAN_1A                | 29%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_1B                | 29%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2A                | 29%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2B                | 29%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_1_FAN                 | 3840RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_2_FAN                 | 4000RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan

[XXXXXX@welktxefnce-h-pe1util-vm01 pdb-cpld-v12-20240220]$ rf_sensor_list.py -u XXXXXX -p XXXXXX -r https://[$IP]
Chassis 'Computer System Chassis' Status
  Sensor                    | Reading    | Health   | LF       | LC       | LNC      | UNC      | UC       | UF       | PhysicalContext
  State                     | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 213V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 180W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 212V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 168W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_V5                    | Absent     | N/A      | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | Absent     | N/A      | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | Absent     | N/A      | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | Absent     | N/A      | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  RTC_Voltage               | 3.024V     | OK       | N/A      | 2.289    | N/A      | N/A      | 3.444    | N/A      | VoltageRegulator
  CPU_0_Vcore               | Absent     | N/A      | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_MARGIN              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  PSU_1_TEMP_2              | 47Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_1_TEMP_1              | 28Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  PSU_2_TEMP_2              | 46Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_2_TEMP_1              | 28Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  CPU_0_DIMM_C0             | 35Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_D0             | 34Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_A0             | 33Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_B0             | 33Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_G0             | 35Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_H0             | 34Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_E0             | 34Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_F0             | 34Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  DIMM_VRABCD_TEMP          | 33Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  DIMM_VREFGH_TEMP          | 33Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  MAX_DIMM_TEMP             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  PML_WEST_TEMP             | 54Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  PML_LOCAL_TEMP            | 51Cel      | OK       | N/A      | N/A      | N/A      | 80       | 85       | N/A      | Intake
  PML_VDD_TEMP              | 55Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 125      | N/A      | Intake
  PML_EAST_TEMP             | 54Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  SC_1_E810                 | Absent     | N/A      | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SC_2_E810                 | Absent     | N/A      | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SSD_0_TEMP                | 33Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  SSD_1_TEMP                | 34Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  INLET_TEMP_L              | 25Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  INLET_TEMP_R              | 24Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  MB_HSC_TEMP               | 34Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  OUTLET_TEMP_L             | 36Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  OUTLET_TEMP_R             | 36Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  INLET_TEMP_MAX            | 25Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  OUTLET_TEMP_MAX           | 36Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  SYS_PCH_TEMP              | 32Cel      | OK       | N/A      | 5        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_TEMP                | 45Cel      | OK       | N/A      | N/A      | N/A      | 96       | 98       | N/A      | Intake
  SYS_FAN_1A                | 29%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_1B                | 29%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2A                | 29%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2B                | 29%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_1_FAN                 | 3840RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_2_FAN                 | 4000RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan

[XXXXXX@welktxefnce-h-pe1util-vm01 pdb-cpld-v12-20240220]$
```

## Watching with IPMITOOL now to see if there is a difference 

```log
[XXXXXX@welktxefnce-h-pe1util-vm01 pdb-cpld-v12-20240220]$ ipmitool -I lanplus -H $IP -U XXXXXX -P XXXXXX sdr
CPU_0_PROCHOT    | 0x00              | ok
CPU_0_STATUS     | 0x00              | ok
CPU_0_Vcore      | 1.82 Volts        | ok
CPU0DDR_ABC_1.2V | 1.23 Volts        | ok
CPU0DDR_DEF_1.2V | 1.23 Volts        | ok
CPU_0_DTS_TEMP   | -52 degrees C     | ok
CPU_0_TEMP       | 46 degrees C      | ok
CPU_0_MARGIN     | 41 degrees C      | ok
CPU0_Power       | 73 Watts          | ok
SYS_PCH_TEMP     | 33 degrees C      | ok
CPU_0_DIMM_C0    | 36 degrees C      | ok
CPU_0_DIMM_D0    | 34 degrees C      | ok
CPU_0_DIMM_A0    | 33 degrees C      | ok
CPU_0_DIMM_B0    | 33 degrees C      | ok
CPU_0_DIMM_G0    | 35 degrees C      | ok
CPU_0_DIMM_H0    | 34 degrees C      | ok
CPU_0_DIMM_E0    | 34 degrees C      | ok
CPU_0_DIMM_F0    | 34 degrees C      | ok
MAX_DIMM_TEMP    | 36 degrees C      | ok
INLET_TEMP_L     | 25 degrees C      | ok
INLET_TEMP_R     | 24 degrees C      | ok
INLET_TEMP_MAX   | 25 degrees C      | ok
OUTLET_TEMP_L    | 37 degrees C      | ok
OUTLET_TEMP_R    | 36 degrees C      | ok
OUTLET_TEMP_MAX  | 37 degrees C      | ok
SYS_FAN_1A       | 5125 RPM          | ok
SYS_FAN_1B       | 5500 RPM          | ok
SYS_FAN_2A       | 5125 RPM          | ok
SYS_FAN_2B       | 5500 RPM          | ok
SYS_FAN_1A_PWM   | 18 percent        | ok
SYS_FAN_1B_PWM   | 18 percent        | ok
SYS_FAN_2A_PWM   | 18 percent        | ok
SYS_FAN_2B_PWM   | 18 percent        | ok
SYS_V1.05        | 1.05 Volts        | ok
SYS_V12          | 12.16 Volts       | ok
SYS_V3.3         | 3.33 Volts        | ok
SYS_V5           | 5.05 Volts        | ok
CPU_CUPS         | 1 percent         | ok
MB_HSC_TEMP      | 35 degrees C      | ok
DIMM_VREFGH_TEMP | 34 degrees C      | ok
DIMM_VRABCD_TEMP | 34 degrees C      | ok
RTC_Voltage      | 3.02 Volts        | ok
MB_HSC_PIN       | 168 Watts         | ok
MB_HSC_PIN_AVG   | 152 Watts         | ok
MB_HSC_PEAK_PIN  | 440 Watts         | ok
PSU_1_STATUS     | 0x00              | ok
PSU_2_STATUS     | 0x00              | ok
PSU_1_FAN        | 3840 RPM          | ok
PSU_2_FAN        | 4000 RPM          | ok
PSU_1_TEMP_1     | 27 degrees C      | ok
PSU_2_TEMP_1     | 28 degrees C      | ok
PSU_1_TEMP_2     | 46 degrees C      | ok
PSU_2_TEMP_2     | 46 degrees C      | ok
PSU_POWER_IN     | 352 Watts         | ok
PSU_1_POWER_IN   | 186 Watts         | ok
PSU_2_POWER_IN   | 168 Watts         | ok
PSU_1_POWER_OUT  | 162 Watts         | ok
PSU_2_POWER_OUT  | 150 Watts         | ok
PSU_1_CURRENT_IN | 0.88 Amps         | ok
PSU_2_CURRENT_IN | 0.82 Amps         | ok
PSU1_CURRENT_OUT | 13.78 Amps        | ok
PSU2_CURRENT_OUT | 12.72 Amps        | ok
PWR_UNIT_REDUND  | 0x00              | ok
PWR_UNIT_STATUS  | 0x00              | ok
ACPI_STATE       | 0x00              | ok
SSD_0_TEMP       | 33 degrees C      | ok
SSD_1_TEMP       | 34 degrees C      | ok
PML_WEST_TEMP    | 54 degrees C      | ok
PML_LOCAL_TEMP   | 51 degrees C      | ok
PML_VDD_TEMP     | 55 degrees C      | ok
PML_EAST_TEMP    | 54 degrees C      | ok
SC_1_E810        | 41 degrees C      | ok
SC_2_E810        | 39 degrees C      | ok
[XXXXXX@welktxefnce-h-pe1util-vm01 pdb-cpld-v12-20240220]$ ipmitool -I lanplus -H $IP -U XXXXXX -P XXXXXX sdr
CPU_0_PROCHOT    | 0x00              | ok
CPU_0_STATUS     | 0x00              | ok
CPU_0_Vcore      | 1.82 Volts        | ok
CPU0DDR_ABC_1.2V | 1.23 Volts        | ok
CPU0DDR_DEF_1.2V | 1.23 Volts        | ok
CPU_0_DTS_TEMP   | -52 degrees C     | ok
CPU_0_TEMP       | 46 degrees C      | ok
CPU_0_MARGIN     | 41 degrees C      | ok
CPU0_Power       | 73 Watts          | ok
SYS_PCH_TEMP     | 33 degrees C      | ok
CPU_0_DIMM_C0    | 36 degrees C      | ok
CPU_0_DIMM_D0    | 34 degrees C      | ok
CPU_0_DIMM_A0    | 33 degrees C      | ok
CPU_0_DIMM_B0    | 33 degrees C      | ok
CPU_0_DIMM_G0    | 35 degrees C      | ok
CPU_0_DIMM_H0    | 35 degrees C      | ok
CPU_0_DIMM_E0    | 35 degrees C      | ok
CPU_0_DIMM_F0    | 34 degrees C      | ok
MAX_DIMM_TEMP    | 36 degrees C      | ok
INLET_TEMP_L     | 26 degrees C      | ok
INLET_TEMP_R     | 24 degrees C      | ok
INLET_TEMP_MAX   | 26 degrees C      | ok
OUTLET_TEMP_L    | 37 degrees C      | ok
OUTLET_TEMP_R    | 36 degrees C      | ok
OUTLET_TEMP_MAX  | 37 degrees C      | ok
SYS_FAN_1A       | 5125 RPM          | ok
SYS_FAN_1B       | 5500 RPM          | ok
SYS_FAN_2A       | 5000 RPM          | ok
SYS_FAN_2B       | 5500 RPM          | ok
SYS_FAN_1A_PWM   | 18 percent        | ok
SYS_FAN_1B_PWM   | 18 percent        | ok
SYS_FAN_2A_PWM   | 18 percent        | ok
SYS_FAN_2B_PWM   | 18 percent        | ok
SYS_V1.05        | 1.05 Volts        | ok
SYS_V12          | 12.16 Volts       | ok
SYS_V3.3         | 3.33 Volts        | ok
SYS_V5           | 5.05 Volts        | ok
CPU_CUPS         | 1 percent         | ok
MB_HSC_TEMP      | 35 degrees C      | ok
DIMM_VREFGH_TEMP | 34 degrees C      | ok
DIMM_VRABCD_TEMP | 34 degrees C      | ok
RTC_Voltage      | 3.02 Volts        | ok
MB_HSC_PIN       | 152 Watts         | ok
MB_HSC_PIN_AVG   | 152 Watts         | ok
MB_HSC_PEAK_PIN  | 440 Watts         | ok
PSU_1_STATUS     | 0x00              | ok
PSU_2_STATUS     | 0x00              | ok
PSU_1_FAN        | 3840 RPM          | ok
PSU_2_FAN        | 4000 RPM          | ok
PSU_1_TEMP_1     | 28 degrees C      | ok
PSU_2_TEMP_1     | 28 degrees C      | ok
PSU_1_TEMP_2     | 46 degrees C      | ok
PSU_2_TEMP_2     | 46 degrees C      | ok
PSU_POWER_IN     | 352 Watts         | ok
PSU_1_POWER_IN   | 186 Watts         | ok
PSU_2_POWER_IN   | 174 Watts         | ok
PSU_1_POWER_OUT  | 168 Watts         | ok
PSU_2_POWER_OUT  | 156 Watts         | ok
PSU_1_CURRENT_IN | 0.88 Amps         | ok
PSU_2_CURRENT_IN | 0.82 Amps         | ok
PSU1_CURRENT_OUT | 13.78 Amps        | ok
PSU2_CURRENT_OUT | 12.72 Amps        | ok
PWR_UNIT_REDUND  | 0x00              | ok
PWR_UNIT_STATUS  | 0x00              | ok
ACPI_STATE       | 0x00              | ok
SSD_0_TEMP       | 33 degrees C      | ok
SSD_1_TEMP       | 34 degrees C      | ok
PML_WEST_TEMP    | 54 degrees C      | ok
PML_LOCAL_TEMP   | 51 degrees C      | ok
PML_VDD_TEMP     | 55 degrees C      | ok
PML_EAST_TEMP    | 54 degrees C      | ok
SC_1_E810        | 41 degrees C      | ok
SC_2_E810        | 39 degrees C      | ok
[XXXXXX@welktxefnce-h-pe1util-vm01 pdb-cpld-v12-20240220]$ ipmitool -I lanplus -H $IP -U XXXXXX -P XXXXXX sdr
CPU_0_PROCHOT    | 0x00              | ok
CPU_0_STATUS     | 0x00              | ok
CPU_0_Vcore      | 1.82 Volts        | ok
CPU0DDR_ABC_1.2V | 1.23 Volts        | ok
CPU0DDR_DEF_1.2V | 1.23 Volts        | ok
CPU_0_DTS_TEMP   | -51 degrees C     | ok
CPU_0_TEMP       | 47 degrees C      | ok
CPU_0_MARGIN     | 41 degrees C      | ok
CPU0_Power       | 74 Watts          | ok
SYS_PCH_TEMP     | 33 degrees C      | ok
CPU_0_DIMM_C0    | 36 degrees C      | ok
CPU_0_DIMM_D0    | 35 degrees C      | ok
CPU_0_DIMM_A0    | 34 degrees C      | ok
CPU_0_DIMM_B0    | 33 degrees C      | ok
CPU_0_DIMM_G0    | 35 degrees C      | ok
CPU_0_DIMM_H0    | 35 degrees C      | ok
CPU_0_DIMM_E0    | 35 degrees C      | ok
CPU_0_DIMM_F0    | 35 degrees C      | ok
MAX_DIMM_TEMP    | 36 degrees C      | ok
INLET_TEMP_L     | 26 degrees C      | ok
INLET_TEMP_R     | 25 degrees C      | ok
INLET_TEMP_MAX   | 26 degrees C      | ok
OUTLET_TEMP_L    | 38 degrees C      | ok
OUTLET_TEMP_R    | 36 degrees C      | ok
OUTLET_TEMP_MAX  | 38 degrees C      | ok
SYS_FAN_1A       | 5125 RPM          | ok
SYS_FAN_1B       | 5500 RPM          | ok
SYS_FAN_2A       | 5000 RPM          | ok
SYS_FAN_2B       | 5500 RPM          | ok
SYS_FAN_1A_PWM   | 18 percent        | ok
SYS_FAN_1B_PWM   | 18 percent        | ok
SYS_FAN_2A_PWM   | 18 percent        | ok
SYS_FAN_2B_PWM   | 18 percent        | ok
SYS_V1.05        | 1.05 Volts        | ok
SYS_V12          | 12.16 Volts       | ok
SYS_V3.3         | 3.33 Volts        | ok
SYS_V5           | 5.05 Volts        | ok
CPU_CUPS         | 1 percent         | ok
MB_HSC_TEMP      | 35 degrees C      | ok
DIMM_VREFGH_TEMP | 34 degrees C      | ok
DIMM_VRABCD_TEMP | 35 degrees C      | ok
RTC_Voltage      | 3.02 Volts        | ok
MB_HSC_PIN       | 168 Watts         | ok
MB_HSC_PIN_AVG   | 152 Watts         | ok
MB_HSC_PEAK_PIN  | 440 Watts         | ok
PSU_1_STATUS     | 0x00              | ok
PSU_2_STATUS     | 0x00              | ok
PSU_1_FAN        | 3840 RPM          | ok
PSU_2_FAN        | 4000 RPM          | ok
PSU_1_TEMP_1     | 28 degrees C      | ok
PSU_2_TEMP_1     | 28 degrees C      | ok
PSU_1_TEMP_2     | 46 degrees C      | ok
PSU_2_TEMP_2     | 46 degrees C      | ok
PSU_POWER_IN     | 352 Watts         | ok
PSU_1_POWER_IN   | 180 Watts         | ok
PSU_2_POWER_IN   | 168 Watts         | ok
PSU_1_POWER_OUT  | 162 Watts         | ok
PSU_2_POWER_OUT  | 150 Watts         | ok
PSU_1_CURRENT_IN | 0.88 Amps         | ok
PSU_2_CURRENT_IN | 0.82 Amps         | ok
PSU1_CURRENT_OUT | 13.78 Amps        | ok
PSU2_CURRENT_OUT | 12.72 Amps        | ok
PWR_UNIT_REDUND  | 0x00              | ok
PWR_UNIT_STATUS  | 0x00              | ok
ACPI_STATE       | 0x00              | ok
SSD_0_TEMP       | 33 degrees C      | ok
SSD_1_TEMP       | 35 degrees C      | ok
PML_WEST_TEMP    | 55 degrees C      | ok
PML_LOCAL_TEMP   | 52 degrees C      | ok
PML_VDD_TEMP     | 56 degrees C      | ok
PML_EAST_TEMP    | 55 degrees C      | ok
SC_1_E810        | 42 degrees C      | ok
SC_2_E810        | 40 degrees C      | ok
[XXXXXX@welktxefnce-h-pe1util-vm01 pdb-cpld-v12-20240220]$ rf_sensor_list.py -u XXXXXX -p XXXXXX -r https://[$IP]
Chassis 'Computer System Chassis' Status
  Sensor                    | Reading    | Health   | LF       | LC       | LNC      | UNC      | UC       | UF       | PhysicalContext
  State                     | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 213V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 162W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 212V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 156W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_V5                    | 5.053V     | OK       | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | 12.1568V   | OK       | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | 3.3236V    | OK       | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | 1.05484V   | OK       | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  RTC_Voltage               | 3.024V     | OK       | N/A      | 2.289    | N/A      | N/A      | 3.444    | N/A      | VoltageRegulator
  CPU_0_Vcore               | 1.822V     | OK       | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | 1.2306V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | 1.2306V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | -52Cel     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_MARGIN              | 41Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  PSU_1_TEMP_2              | 46Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_1_TEMP_1              | 28Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  PSU_2_TEMP_2              | 46Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_2_TEMP_1              | 28Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  CPU_0_DIMM_C0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_D0             | 35Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_A0             | 34Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_B0             | 33Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_G0             | 35Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_H0             | 35Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_E0             | 35Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_F0             | 35Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  DIMM_VRABCD_TEMP          | 35Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  DIMM_VREFGH_TEMP          | 34Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  MAX_DIMM_TEMP             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  PML_WEST_TEMP             | 55Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  PML_LOCAL_TEMP            | 52Cel      | OK       | N/A      | N/A      | N/A      | 80       | 85       | N/A      | Intake
  PML_VDD_TEMP              | 56Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 125      | N/A      | Intake
  PML_EAST_TEMP             | 55Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  SC_1_E810                 | 42Cel      | OK       | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SC_2_E810                 | 40Cel      | OK       | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SSD_0_TEMP                | 33Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  SSD_1_TEMP                | 35Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  INLET_TEMP_L              | 25Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  INLET_TEMP_R              | 24Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  MB_HSC_TEMP               | 35Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  OUTLET_TEMP_L             | 38Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  OUTLET_TEMP_R             | 36Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  INLET_TEMP_MAX            | 25Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  OUTLET_TEMP_MAX           | 38Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  SYS_PCH_TEMP              | 33Cel      | OK       | N/A      | 5        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_TEMP                | 46Cel      | OK       | N/A      | N/A      | N/A      | 96       | 98       | N/A      | Intake
  SYS_FAN_1A                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_1B                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2A                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2B                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_1_FAN                 | 3840RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_2_FAN                 | 4000RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan

[XXXXXX@welktxefnce-h-pe1util-vm01 pdb-cpld-v12-20240220]$ rf_sensor_list.py -u XXXXXX -p XXXXXX -r https://[$IP]
Chassis 'Computer System Chassis' Status
  Sensor                    | Reading    | Health   | LF       | LC       | LNC      | UNC      | UC       | UF       | PhysicalContext
  State                     | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 212V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 212V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_V5                    | Absent     | N/A      | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | Absent     | N/A      | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | Absent     | N/A      | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | Absent     | N/A      | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  RTC_Voltage               | 3.017V     | OK       | N/A      | 2.289    | N/A      | N/A      | 3.444    | N/A      | VoltageRegulator
  CPU_0_Vcore               | Absent     | N/A      | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_MARGIN              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  PSU_1_TEMP_2              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_1_TEMP_1              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  PSU_2_TEMP_2              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_2_TEMP_1              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  CPU_0_DIMM_C0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_D0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_A0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_B0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_G0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_H0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_E0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_F0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  DIMM_VRABCD_TEMP          | 35Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  DIMM_VREFGH_TEMP          | 34Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  MAX_DIMM_TEMP             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  PML_WEST_TEMP             | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  PML_LOCAL_TEMP            | Absent     | N/A      | N/A      | N/A      | N/A      | 80       | 85       | N/A      | Intake
  PML_VDD_TEMP              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 125      | N/A      | Intake
  PML_EAST_TEMP             | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  SC_1_E810                 | Absent     | N/A      | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SC_2_E810                 | Absent     | N/A      | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SSD_0_TEMP                | Absent     | N/A      | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  SSD_1_TEMP                | Absent     | N/A      | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  INLET_TEMP_L              | 25Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  INLET_TEMP_R              | 24Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  MB_HSC_TEMP               | 35Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  OUTLET_TEMP_L             | 38Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  OUTLET_TEMP_R             | 36Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  INLET_TEMP_MAX            | 25Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  OUTLET_TEMP_MAX           | 38Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  SYS_PCH_TEMP              | 33Cel      | OK       | N/A      | 5        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_TEMP                | Absent     | N/A      | N/A      | N/A      | N/A      | 96       | 98       | N/A      | Intake
  SYS_FAN_1A                | 29%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_1B                | 29%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2A                | 29%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2B                | 29%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_1_FAN                 | Absent     | N/A      | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_2_FAN                 | Absent     | N/A      | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan

[XXXXXX@welktxefnce-h-pe1util-vm01 pdb-cpld-v12-20240220]$ ipmitool -I lanplus -H $IP -U XXXXXX -P XXXXXX sdr
\CPU_0_PROCHOT    | 0x00              | ok
CPU_0_STATUS     | 0x00              | ok
CPU_0_Vcore      | no reading        | ns
CPU0DDR_ABC_1.2V | no reading        | ns
CPU0DDR_DEF_1.2V | no reading        | ns
CPU_0_DTS_TEMP   | no reading        | ns
CPU_0_TEMP       | 48 degrees C      | ok
CPU_0_MARGIN     | no reading        | ns
CPU0_Power       | 240 Watts         | ok
SYS_PCH_TEMP     | 33 degrees C      | ok
CPU_0_DIMM_C0    | 36 degrees C      | ok
CPU_0_DIMM_D0    | 35 degrees C      | ok
CPU_0_DIMM_A0    | 34 degrees C      | ok
CPU_0_DIMM_B0    | 33 degrees C      | ok
CPU_0_DIMM_G0    | 35 degrees C      | ok
CPU_0_DIMM_H0    | 35 degrees C      | ok
CPU_0_DIMM_E0    | 35 degrees C      | ok
CPU_0_DIMM_F0    | 35 degrees C      | ok
MAX_DIMM_TEMP    | no reading        | ns
INLET_TEMP_L     | 25 degrees C      | ok
INLET_TEMP_R     | 24 degrees C      | ok
INLET_TEMP_MAX   | 25 degrees C      | ok
OUTLET_TEMP_L    | 38 degrees C      | ok
OUTLET_TEMP_R    | 37 degrees C      | ok
OUTLET_TEMP_MAX  | 38 degrees C      | ok
SYS_FAN_1A       | 7500 RPM          | ok
SYS_FAN_1B       | 8000 RPM          | ok
SYS_FAN_2A       | 7500 RPM          | ok
SYS_FAN_2B       | 8125 RPM          | ok
SYS_FAN_1A_PWM   | 29 percent        | ok
SYS_FAN_1B_PWM   | 29 percent        | ok
SYS_FAN_2A_PWM   | 29 percent        | ok
SYS_FAN_2B_PWM   | 29 percent        | ok
SYS_V1.05        | no reading        | ns
SYS_V12          | no reading        | ns
SYS_V3.3         | no reading        | ns
SYS_V5           | no reading        | ns
CPU_CUPS         | no reading        | ns
MB_HSC_TEMP      | 35 degrees C      | ok
DIMM_VREFGH_TEMP | 34 degrees C      | ok
DIMM_VRABCD_TEMP | 35 degrees C      | ok
RTC_Voltage      | 3.02 Volts        | ok
MB_HSC_PIN       | 216 Watts         | ok
MB_HSC_PIN_AVG   | 152 Watts         | ok
MB_HSC_PEAK_PIN  | 440 Watts         | ok
PSU_1_STATUS     | 0x00              | ok
PSU_2_STATUS     | 0x00              | ok
PSU_1_FAN        | no reading        | ns
PSU_2_FAN        | no reading        | ns
PSU_1_TEMP_1     | no reading        | ns
PSU_2_TEMP_1     | no reading        | ns
PSU_1_TEMP_2     | no reading        | ns
PSU_2_TEMP_2     | no reading        | ns
PSU_POWER_IN     | no reading        | ns
PSU_1_POWER_IN   | no reading        | ns
PSU_2_POWER_IN   | no reading        | ns
PSU_1_POWER_OUT  | no reading        | ns
PSU_2_POWER_OUT  | no reading        | ns
PSU_1_CURRENT_IN | no reading        | ns
PSU_2_CURRENT_IN | no reading        | ns
PSU1_CURRENT_OUT | no reading        | ns
PSU2_CURRENT_OUT | no reading        | ns
PWR_UNIT_REDUND  | 0x00              | ok
PWR_UNIT_STATUS  | 0x00              | ok
ACPI_STATE       | 0x00              | ok
SSD_0_TEMP       | no reading        | ns
SSD_1_TEMP       | no reading        | ns
PML_WEST_TEMP    | 55 degrees C      | ok
PML_LOCAL_TEMP   | 52 degrees C      | ok
PML_VDD_TEMP     | 56 degrees C      | ok
PML_EAST_TEMP    | 55 degrees C      | ok
SC_1_E810        | no reading        | ns
SC_2_E810        | no reading        | ns
[XXXXXX@welktxefnce-h-pe1util-vm01 pdb-cpld-v12-20240220]$


```