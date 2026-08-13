# ZT Proteus PDB-CPLD 0.0.1.2 Firmware Validation
# ZT Proteus .46 BMC / BIOS .30
# 1/16/24 James Patchett
# Power supply pull, and validate power failover still works
# Target subclouds J30-RU_12,13 Left side

## Left side Subcloud welktxef-d931887-021
## BMC 0.46 BIOS 0.30
BMC:  2607:f160:10:9249:ce:40a:0:e015
OAM:  2607:f160:10:9249:ce:40a:0:f409

## Subcloud welktxef-d931856-008 Info
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

### Firmware capture of test system Left side

```log
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ echo $IP
2607:f160:10:9249:ce:40a:0:e015
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[${IP}]/redfish/v1/UpdateService/FirmwareInventory/BMC | jq .
{
  "@odata.context": "/redfish/v1/$metadata#SoftwareInventory.SoftwareInventory",
  "@odata.etag": "\"1710377166\"",
  "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/BMC",
  "@odata.type": "#SoftwareInventory.v1_2_3.SoftwareInventory",
  "Id": "BMC",
  "Name": "BMC",
  "Updateable": true,
  "Version": "0.46.00"
}
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[${IP}]/redfish/v1/UpdateService/FirmwareInventory/BIOS | jq .
{
  "@odata.context": "/redfish/v1/$metadata#SoftwareInventory.SoftwareInventory",
  "@odata.etag": "\"1710377166\"",
  "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/BIOS",
  "@odata.type": "#SoftwareInventory.v1_2_3.SoftwareInventory",
  "Id": "BIOS",
  "Name": "BIOS",
  "Updateable": true,
  "Version": "0.30"
}
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[${IP}]/redfish/v1/UpdateService/FirmwareInventory/PDBCPLD | jq .
{
  "@odata.context": "/redfish/v1/$metadata#SoftwareInventory.SoftwareInventory",
  "@odata.etag": "\"1710377166\"",
  "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/PDBCPLD",
  "@odata.type": "#SoftwareInventory.v1_2_3.SoftwareInventory",
  "Id": "PDBCPLD",
  "Name": "PDBCPLD",
  "Updateable": true,
  "Version": "0.0.1.2"
}
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$


```

### Firmware capture of test system Right side

```log
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ echo $IP
2607:f160:10:9249:ce:40a:0:e016
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[${IP}]/redfish/v1/UpdateService/FirmwareInventory/BMC| jq .
{
  "@odata.context": "/redfish/v1/$metadata#SoftwareInventory.SoftwareInventory",
  "@odata.etag": "\"1709780777\"",
  "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/BMC",
  "@odata.type": "#SoftwareInventory.v1_2_3.SoftwareInventory",
  "Id": "BMC",
  "Name": "BMC",
  "Updateable": true,
  "Version": "0.46.00"
}
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[${IP}]/redfish/v1/UpdateService/FirmwareInventory/BIOS| jq .
{
  "@odata.context": "/redfish/v1/$metadata#SoftwareInventory.SoftwareInventory",
  "@odata.etag": "\"1709780777\"",
  "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/BIOS",
  "@odata.type": "#SoftwareInventory.v1_2_3.SoftwareInventory",
  "Id": "BIOS",
  "Name": "BIOS",
  "Updateable": true,
  "Version": "0.30"
}
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[${IP}]/redfish/v1/UpdateService/FirmwareInventory/PDBCPLD| jq .
{
  "@odata.context": "/redfish/v1/$metadata#SoftwareInventory.SoftwareInventory",
  "@odata.etag": "\"1709780777\"",
  "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/PDBCPLD",
  "@odata.type": "#SoftwareInventory.v1_2_3.SoftwareInventory",
  "Id": "PDBCPLD",
  "Name": "PDBCPLD",
  "Updateable": false,
  "Version": "0.0.1.2"
}
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$

```

### Pull Left Power cable

### Show sensors for both sleds, Left first then Right

```log
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ echo $IP
2607:f160:10:9249:ce:40a:0:e015
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ rf_sensor_list.py -u XXXXXX -p XXXXXX -r https://[$IP]
Chassis 'Computer System Chassis' Status
  Sensor                    | Reading    | Health   | LF       | LC       | LNC      | UNC      | UC       | UF       | PhysicalContext
  State                     | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 214V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 150W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 213V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 144W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_V5                    | 5.053V     | OK       | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | 12.1568V   | OK       | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | 3.3236V    | OK       | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | 1.0532V    | OK       | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  RTC_Voltage               | 3.031V     | OK       | N/A      | 2.289    | N/A      | N/A      | 3.444    | N/A      | VoltageRegulator
  CPU_0_Vcore               | 1.8248V    | OK       | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | 1.2306V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | 1.2306V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | -50Cel     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_MARGIN              | 40Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  PSU_1_TEMP_2              | 46Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_1_TEMP_1              | 27Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  PSU_2_TEMP_2              | 45Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_2_TEMP_1              | 27Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  CPU_0_DIMM_C0             | 37Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_D0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_A0             | 34Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_B0             | 34Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_G0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_H0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_E0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_F0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  DIMM_VRABCD_TEMP          | 35Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  DIMM_VREFGH_TEMP          | 34Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  MAX_DIMM_TEMP             | 37Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  PML_WEST_TEMP             | 57Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  PML_LOCAL_TEMP            | 54Cel      | OK       | N/A      | N/A      | N/A      | 80       | 85       | N/A      | Intake
  PML_VDD_TEMP              | 59Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 125      | N/A      | Intake
  PML_EAST_TEMP             | 56Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  SC_1_E810                 | 42Cel      | OK       | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SC_2_E810                 | 39Cel      | OK       | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SSD_0_TEMP                | 34Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  SSD_1_TEMP                | 36Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  INLET_TEMP_L              | 26Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  INLET_TEMP_R              | 24Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  MB_HSC_TEMP               | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  OUTLET_TEMP_L             | 39Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  OUTLET_TEMP_R             | 37Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  INLET_TEMP_MAX            | 26Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  OUTLET_TEMP_MAX           | 39Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  SYS_PCH_TEMP              | 34Cel      | OK       | N/A      | 5        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_TEMP                | 48Cel      | OK       | N/A      | N/A      | N/A      | 96       | 98       | N/A      | Intake
  SYS_FAN_1A                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_1B                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2A                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2B                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_1_FAN                 | 3840RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_2_FAN                 | 4000RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan

[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$

[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ rf_sensor_list.py -u XXXXXX -p XXXXXX -r https://[$IP]
Chassis 'Computer System Chassis' Status
  Sensor                    | Reading    | Health   | LF       | LC       | LNC      | UNC      | UC       | UF       | PhysicalContext
  State                     | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 213V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 144W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 213V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 132W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_V5                    | 4.9984V    | OK       | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | 12.138V    | OK       | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | 3.2981V    | OK       | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | 1.04664V   | OK       | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  RTC_Voltage               | 3.024V     | OK       | N/A      | 2.289    | N/A      | N/A      | 3.444    | N/A      | VoltageRegulator
  CPU_0_Vcore               | 1.8164V    | OK       | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | 1.2232V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | 1.2232V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | -50Cel     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_MARGIN              | 39Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  PSU_1_TEMP_2              | 46Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_1_TEMP_1              | 27Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  PSU_2_TEMP_2              | 45Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_2_TEMP_1              | 27Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  CPU_0_DIMM_C0             | 38Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_D0             | 37Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_A0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_B0             | 35Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_G0             | 37Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_H0             | 37Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_E0             | 37Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_F0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  DIMM_VRABCD_TEMP          | 35Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  DIMM_VREFGH_TEMP          | 34Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  MAX_DIMM_TEMP             | 38Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  PML_WEST_TEMP             | 55Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  PML_LOCAL_TEMP            | 54Cel      | OK       | N/A      | N/A      | N/A      | 80       | 85       | N/A      | Intake
  PML_VDD_TEMP              | 58Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 125      | N/A      | Intake
  PML_EAST_TEMP             | 54Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  SC_1_E810                 | 44Cel      | OK       | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SC_2_E810                 | 39Cel      | OK       | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SSD_0_TEMP                | 35Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  SSD_1_TEMP                | 36Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  INLET_TEMP_L              | 26Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  INLET_TEMP_R              | 25Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  MB_HSC_TEMP               | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  OUTLET_TEMP_L             | 40Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  OUTLET_TEMP_R             | 38Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  INLET_TEMP_MAX            | 26Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  OUTLET_TEMP_MAX           | 40Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  SYS_PCH_TEMP              | 33Cel      | OK       | N/A      | 5        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_TEMP                | 48Cel      | OK       | N/A      | N/A      | N/A      | 96       | 98       | N/A      | Intake
  SYS_FAN_1A                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_1B                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2A                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2B                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_1_FAN                 | 3840RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_2_FAN                 | 4000RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan

[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$



```


### Pulled Primary power supply 

### checking the sensors of both sleds again



```log
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ echo $IP
2607:f160:10:9249:ce:40a:0:e015
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ rf_sensor_list.py -u XXXXXX -p XXXXXX -r https://[$IP]
Chassis 'Computer System Chassis' Status
  Sensor                    | Reading    | Health   | LF       | LC       | LNC      | UNC      | UC       | UF       | PhysicalContext
  State                     | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | Warning  | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 214V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 213V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 306W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_V5                    | 5.053V     | OK       | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | 12.0628V   | OK       | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | 3.3287V    | OK       | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | 1.0532V    | OK       | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  RTC_Voltage               | 3.031V     | OK       | N/A      | 2.289    | N/A      | N/A      | 3.444    | N/A      | VoltageRegulator
  CPU_0_Vcore               | 1.8248V    | OK       | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | 1.2269V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | 1.2306V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | -51Cel     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_MARGIN              | 40Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  PSU_1_TEMP_2              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_1_TEMP_1              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  PSU_2_TEMP_2              | 44Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_2_TEMP_1              | 27Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  CPU_0_DIMM_C0             | 37Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_D0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_A0             | 35Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_B0             | 34Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_G0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_H0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_E0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_F0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  DIMM_VRABCD_TEMP          | 35Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  DIMM_VREFGH_TEMP          | 34Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  MAX_DIMM_TEMP             | 37Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  PML_WEST_TEMP             | 57Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  PML_LOCAL_TEMP            | 55Cel      | OK       | N/A      | N/A      | N/A      | 80       | 85       | N/A      | Intake
  PML_VDD_TEMP              | 59Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 125      | N/A      | Intake
  PML_EAST_TEMP             | 57Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  SC_1_E810                 | 42Cel      | OK       | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SC_2_E810                 | 40Cel      | OK       | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SSD_0_TEMP                | 34Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  SSD_1_TEMP                | 36Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  INLET_TEMP_L              | 26Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  INLET_TEMP_R              | 24Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  MB_HSC_TEMP               | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  OUTLET_TEMP_L             | 39Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  OUTLET_TEMP_R             | 37Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  INLET_TEMP_MAX            | 26Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  OUTLET_TEMP_MAX           | 39Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  SYS_PCH_TEMP              | 33Cel      | OK       | N/A      | 5        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_TEMP                | 47Cel      | OK       | N/A      | N/A      | N/A      | 96       | 98       | N/A      | Intake
  SYS_FAN_1A                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_1B                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2A                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2B                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_1_FAN                 | Absent     | N/A      | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_2_FAN                 | 4800RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan

[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ ipmitool -I lanplus -H $IP -U XXXXXX -P XXXXXX sdr
CPU_0_PROCHOT    | 0x00              | ok
CPU_0_STATUS     | 0x00              | ok
CPU_0_Vcore      | 1.82 Volts        | ok
CPU0DDR_ABC_1.2V | 1.23 Volts        | ok
CPU0DDR_DEF_1.2V | 1.23 Volts        | ok
CPU_0_DTS_TEMP   | -43 degrees C     | ok
CPU_0_TEMP       | 55 degrees C      | ok
CPU_0_MARGIN     | 32 degrees C      | ok
CPU0_Power       | 73 Watts          | ok
SYS_PCH_TEMP     | 32 degrees C      | ok
CPU_0_DIMM_C0    | 37 degrees C      | ok
CPU_0_DIMM_D0    | 36 degrees C      | ok
CPU_0_DIMM_A0    | 35 degrees C      | ok
CPU_0_DIMM_B0    | 34 degrees C      | ok
CPU_0_DIMM_G0    | 36 degrees C      | ok
CPU_0_DIMM_H0    | 36 degrees C      | ok
CPU_0_DIMM_E0    | 36 degrees C      | ok
CPU_0_DIMM_F0    | 36 degrees C      | ok
MAX_DIMM_TEMP    | 37 degrees C      | ok
INLET_TEMP_L     | 26 degrees C      | ok
INLET_TEMP_R     | 24 degrees C      | ok
INLET_TEMP_MAX   | 26 degrees C      | ok
OUTLET_TEMP_L    | 39 degrees C      | ok
OUTLET_TEMP_R    | 37 degrees C      | ok
OUTLET_TEMP_MAX  | 39 degrees C      | ok
SYS_FAN_1A       | 5000 RPM          | ok
SYS_FAN_1B       | 5500 RPM          | ok
SYS_FAN_2A       | 5000 RPM          | ok
SYS_FAN_2B       | 5500 RPM          | ok
SYS_FAN_1A_PWM   | 18 percent        | ok
SYS_FAN_1B_PWM   | 18 percent        | ok
SYS_FAN_2A_PWM   | 18 percent        | ok
SYS_FAN_2B_PWM   | 18 percent        | ok
SYS_V1.05        | 1.05 Volts        | ok
SYS_V12          | 12.06 Volts       | ok
SYS_V3.3         | 3.32 Volts        | ok
SYS_V5           | 5.05 Volts        | ok
CPU_CUPS         | 1 percent         | ok
MB_HSC_TEMP      | 36 degrees C      | ok
DIMM_VREFGH_TEMP | 34 degrees C      | ok
DIMM_VRABCD_TEMP | 35 degrees C      | ok
RTC_Voltage      | 3.03 Volts        | ok
MB_HSC_PIN       | 164 Watts         | ok
MB_HSC_PIN_AVG   | 156 Watts         | ok
MB_HSC_PEAK_PIN  | 440 Watts         | ok
PSU_1_STATUS     | 0x00              | ok
PSU_2_STATUS     | 0x00              | ok
PSU_1_FAN        | no reading        | ns
PSU_2_FAN        | 4960 RPM          | ok
PSU_1_TEMP_1     | no reading        | ns
PSU_2_TEMP_1     | 27 degrees C      | ok
PSU_1_TEMP_2     | no reading        | ns
PSU_2_TEMP_2     | 45 degrees C      | ok
PSU_POWER_IN     | 319 Watts         | ok
PSU_1_POWER_IN   | no reading        | ns
PSU_2_POWER_IN   | 324 Watts         | ok
PSU_1_POWER_OUT  | no reading        | ns
PSU_2_POWER_OUT  | 306 Watts         | ok
PSU_1_CURRENT_IN | no reading        | ns
PSU_2_CURRENT_IN | 1.51 Amps         | ok
PSU1_CURRENT_OUT | no reading        | ns
PSU2_CURRENT_OUT | 25.44 Amps        | ok
PWR_UNIT_REDUND  | 0x00              | ok
PWR_UNIT_STATUS  | 0x00              | ok
ACPI_STATE       | 0x00              | ok
SSD_0_TEMP       | 34 degrees C      | ok
SSD_1_TEMP       | 36 degrees C      | ok
PML_WEST_TEMP    | 57 degrees C      | ok
PML_LOCAL_TEMP   | 55 degrees C      | ok
PML_VDD_TEMP     | 59 degrees C      | ok
PML_EAST_TEMP    | 57 degrees C      | ok
SC_1_E810        | 42 degrees C      | ok
SC_2_E810        | 39 degrees C      | ok
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$

[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ echo $IP
2607:f160:10:9249:ce:40a:0:e016
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ rf_sensor_list.py -u XXXXXX -p XXXXXX -r https://[$IP]
Chassis 'Computer System Chassis' Status
  Sensor                    | Reading    | Health   | LF       | LC       | LNC      | UNC      | UC       | UF       | PhysicalContext
  State                     | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | Warning  | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 213V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 213V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 294W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_V5                    | 4.9984V    | OK       | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | 12.0252V   | OK       | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | 3.2981V    | OK       | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | 1.045V     | OK       | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  RTC_Voltage               | 3.024V     | OK       | N/A      | 2.289    | N/A      | N/A      | 3.444    | N/A      | VoltageRegulator
  CPU_0_Vcore               | 1.8164V    | OK       | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | 1.2232V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | 1.2232V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | -49Cel     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_MARGIN              | 38Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  PSU_1_TEMP_2              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_1_TEMP_1              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  PSU_2_TEMP_2              | 44Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_2_TEMP_1              | 27Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  CPU_0_DIMM_C0             | 38Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_D0             | 37Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_A0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_B0             | 35Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_G0             | 37Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_H0             | 37Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_E0             | 37Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_F0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  DIMM_VRABCD_TEMP          | 35Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  DIMM_VREFGH_TEMP          | 34Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  MAX_DIMM_TEMP             | 38Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  PML_WEST_TEMP             | 55Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  PML_LOCAL_TEMP            | 54Cel      | OK       | N/A      | N/A      | N/A      | 80       | 85       | N/A      | Intake
  PML_VDD_TEMP              | 58Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 125      | N/A      | Intake
  PML_EAST_TEMP             | 55Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  SC_1_E810                 | 44Cel      | OK       | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SC_2_E810                 | 39Cel      | OK       | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SSD_0_TEMP                | 35Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  SSD_1_TEMP                | 36Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  INLET_TEMP_L              | 26Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  INLET_TEMP_R              | 24Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  MB_HSC_TEMP               | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  OUTLET_TEMP_L             | 40Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  OUTLET_TEMP_R             | 38Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  INLET_TEMP_MAX            | 26Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  OUTLET_TEMP_MAX           | 40Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  SYS_PCH_TEMP              | 33Cel      | OK       | N/A      | 5        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_TEMP                | 49Cel      | OK       | N/A      | N/A      | N/A      | 96       | 98       | N/A      | Intake
  SYS_FAN_1A                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_1B                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2A                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2B                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_1_FAN                 | Absent     | N/A      | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_2_FAN                 | 4800RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan

[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$  ipmitool -I lanplus -H $IP -U XXXXXX -P XXXXXX sdr
CPU_0_PROCHOT    | 0x00              | ok
CPU_0_STATUS     | 0x00              | ok
CPU_0_Vcore      | 1.82 Volts        | ok
CPU0DDR_ABC_1.2V | 1.22 Volts        | ok
CPU0DDR_DEF_1.2V | 1.22 Volts        | ok
CPU_0_DTS_TEMP   | -49 degrees C     | ok
CPU_0_TEMP       | 49 degrees C      | ok
CPU_0_MARGIN     | 40 degrees C      | ok
CPU0_Power       | 72 Watts          | ok
SYS_PCH_TEMP     | 33 degrees C      | ok
CPU_0_DIMM_C0    | 38 degrees C      | ok
CPU_0_DIMM_D0    | 37 degrees C      | ok
CPU_0_DIMM_A0    | 36 degrees C      | ok
CPU_0_DIMM_B0    | 35 degrees C      | ok
CPU_0_DIMM_G0    | 37 degrees C      | ok
CPU_0_DIMM_H0    | 37 degrees C      | ok
CPU_0_DIMM_E0    | 37 degrees C      | ok
CPU_0_DIMM_F0    | 36 degrees C      | ok
MAX_DIMM_TEMP    | 38 degrees C      | ok
INLET_TEMP_L     | 27 degrees C      | ok
INLET_TEMP_R     | 25 degrees C      | ok
INLET_TEMP_MAX   | 27 degrees C      | ok
OUTLET_TEMP_L    | 40 degrees C      | ok
OUTLET_TEMP_R    | 38 degrees C      | ok
OUTLET_TEMP_MAX  | 40 degrees C      | ok
SYS_FAN_1A       | 5000 RPM          | ok
SYS_FAN_1B       | 5500 RPM          | ok
SYS_FAN_2A       | 5000 RPM          | ok
SYS_FAN_2B       | 5500 RPM          | ok
SYS_FAN_1A_PWM   | 18 percent        | ok
SYS_FAN_1B_PWM   | 18 percent        | ok
SYS_FAN_2A_PWM   | 18 percent        | ok
SYS_FAN_2B_PWM   | 18 percent        | ok
SYS_V1.05        | 1.05 Volts        | ok
SYS_V12          | 12.04 Volts       | ok
SYS_V3.3         | 3.30 Volts        | ok
SYS_V5           | 5.00 Volts        | ok
CPU_CUPS         | 3 percent         | ok
MB_HSC_TEMP      | 36 degrees C      | ok
DIMM_VREFGH_TEMP | 34 degrees C      | ok
DIMM_VRABCD_TEMP | 35 degrees C      | ok
RTC_Voltage      | 3.02 Volts        | ok
MB_HSC_PIN       | 152 Watts         | ok
MB_HSC_PIN_AVG   | 152 Watts         | ok
MB_HSC_PEAK_PIN  | 388 Watts         | ok
PSU_1_STATUS     | 0x00              | ok
PSU_2_STATUS     | 0x00              | ok
PSU_1_FAN        | no reading        | ns
PSU_2_FAN        | 4960 RPM          | ok
PSU_1_TEMP_1     | no reading        | ns
PSU_2_TEMP_1     | 27 degrees C      | ok
PSU_1_TEMP_2     | no reading        | ns
PSU_2_TEMP_2     | 45 degrees C      | ok
PSU_POWER_IN     | 308 Watts         | ok
PSU_1_POWER_IN   | no reading        | ns
PSU_2_POWER_IN   | 312 Watts         | ok
PSU_1_POWER_OUT  | no reading        | ns
PSU_2_POWER_OUT  | 288 Watts         | ok
PSU_1_CURRENT_IN | no reading        | ns
PSU_2_CURRENT_IN | 1.51 Amps         | ok
PSU1_CURRENT_OUT | no reading        | ns
PSU2_CURRENT_OUT | 23.85 Amps        | ok
PWR_UNIT_REDUND  | 0x00              | ok
PWR_UNIT_STATUS  | 0x00              | ok
ACPI_STATE       | 0x00              | ok
SSD_0_TEMP       | 35 degrees C      | ok
SSD_1_TEMP       | 36 degrees C      | ok
PML_WEST_TEMP    | 55 degrees C      | ok
PML_LOCAL_TEMP   | 54 degrees C      | ok
PML_VDD_TEMP     | 58 degrees C      | ok
PML_EAST_TEMP    | 55 degrees C      | ok
SC_1_E810        | 44 degrees C      | ok
SC_2_E810        | 39 degrees C      | ok
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$

```

### Put power back to PSU_1 now checking again

```log
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ echo $IP
2607:f160:10:9249:ce:40a:0:e015
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ rf_sensor_list.py -u XXXXXX -p XXXXXX -r https://[$IP]
Chassis 'Computer System Chassis' Status
  Sensor                    | Reading    | Health   | LF       | LC       | LNC      | UNC      | UC       | UF       | PhysicalContext
  State                     | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 214V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 144W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 213V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 144W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_V5                    | 5.053V     | OK       | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | 12.1568V   | OK       | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | 3.3236V    | OK       | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | 1.0532V    | OK       | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  RTC_Voltage               | 3.031V     | OK       | N/A      | 2.289    | N/A      | N/A      | 3.444    | N/A      | VoltageRegulator
  CPU_0_Vcore               | 1.8248V    | OK       | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | 1.2306V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | 1.2306V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | -51Cel     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_MARGIN              | 40Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  PSU_1_TEMP_2              | 43Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_1_TEMP_1              | 27Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  PSU_2_TEMP_2              | 45Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_2_TEMP_1              | 27Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  CPU_0_DIMM_C0             | 37Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_D0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_A0             | 35Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_B0             | 34Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_G0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_H0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_E0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_F0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  DIMM_VRABCD_TEMP          | 35Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  DIMM_VREFGH_TEMP          | 34Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  MAX_DIMM_TEMP             | 37Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  PML_WEST_TEMP             | 57Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  PML_LOCAL_TEMP            | 55Cel      | OK       | N/A      | N/A      | N/A      | 80       | 85       | N/A      | Intake
  PML_VDD_TEMP              | 59Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 125      | N/A      | Intake
  PML_EAST_TEMP             | 57Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  SC_1_E810                 | 43Cel      | OK       | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SC_2_E810                 | 40Cel      | OK       | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SSD_0_TEMP                | 34Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  SSD_1_TEMP                | 36Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  INLET_TEMP_L              | 26Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  INLET_TEMP_R              | 24Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  MB_HSC_TEMP               | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  OUTLET_TEMP_L             | 39Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  OUTLET_TEMP_R             | 37Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  INLET_TEMP_MAX            | 26Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  OUTLET_TEMP_MAX           | 39Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  SYS_PCH_TEMP              | 33Cel      | OK       | N/A      | 5        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_TEMP                | 47Cel      | OK       | N/A      | N/A      | N/A      | 96       | 98       | N/A      | Intake
  SYS_FAN_1A                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_1B                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2A                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2B                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_1_FAN                 | 3840RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_2_FAN                 | 3840RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan

[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ ipmitool -I lanplus -H $IP -U XXXXXX -P XXXXXX sdr
CPU_0_PROCHOT    | 0x00              | ok
CPU_0_STATUS     | 0x00              | ok
CPU_0_Vcore      | 1.82 Volts        | ok
CPU0DDR_ABC_1.2V | 1.23 Volts        | ok
CPU0DDR_DEF_1.2V | 1.23 Volts        | ok
CPU_0_DTS_TEMP   | -44 degrees C     | ok
CPU_0_TEMP       | 54 degrees C      | ok
CPU_0_MARGIN     | 33 degrees C      | ok
CPU0_Power       | 68 Watts          | ok
SYS_PCH_TEMP     | 32 degrees C      | ok
CPU_0_DIMM_C0    | 37 degrees C      | ok
CPU_0_DIMM_D0    | 36 degrees C      | ok
CPU_0_DIMM_A0    | 35 degrees C      | ok
CPU_0_DIMM_B0    | 34 degrees C      | ok
CPU_0_DIMM_G0    | 36 degrees C      | ok
CPU_0_DIMM_H0    | 36 degrees C      | ok
CPU_0_DIMM_E0    | 36 degrees C      | ok
CPU_0_DIMM_F0    | 36 degrees C      | ok
MAX_DIMM_TEMP    | 37 degrees C      | ok
INLET_TEMP_L     | 26 degrees C      | ok
INLET_TEMP_R     | 24 degrees C      | ok
INLET_TEMP_MAX   | 26 degrees C      | ok
OUTLET_TEMP_L    | 39 degrees C      | ok
OUTLET_TEMP_R    | 37 degrees C      | ok
OUTLET_TEMP_MAX  | 39 degrees C      | ok
SYS_FAN_1A       | 5125 RPM          | ok
SYS_FAN_1B       | 5500 RPM          | ok
SYS_FAN_2A       | 5125 RPM          | ok
SYS_FAN_2B       | 5500 RPM          | ok
SYS_FAN_1A_PWM   | 18 percent        | ok
SYS_FAN_1B_PWM   | 18 percent        | ok
SYS_FAN_2A_PWM   | 18 percent        | ok
SYS_FAN_2B_PWM   | 18 percent        | ok
SYS_V1.05        | 1.05 Volts        | ok
SYS_V12          | 12.18 Volts       | ok
SYS_V3.3         | 3.33 Volts        | ok
SYS_V5           | 5.05 Volts        | ok
CPU_CUPS         | 1 percent         | ok
MB_HSC_TEMP      | 36 degrees C      | ok
DIMM_VREFGH_TEMP | 34 degrees C      | ok
DIMM_VRABCD_TEMP | 35 degrees C      | ok
RTC_Voltage      | 3.03 Volts        | ok
MB_HSC_PIN       | 160 Watts         | ok
MB_HSC_PIN_AVG   | 156 Watts         | ok
MB_HSC_PEAK_PIN  | 440 Watts         | ok
PSU_1_STATUS     | 0x00              | ok
PSU_2_STATUS     | 0x00              | ok
PSU_1_FAN        | 3840 RPM          | ok
PSU_2_FAN        | 3840 RPM          | ok
PSU_1_TEMP_1     | 27 degrees C      | ok
PSU_2_TEMP_1     | 27 degrees C      | ok
PSU_1_TEMP_2     | 44 degrees C      | ok
PSU_2_TEMP_2     | 45 degrees C      | ok
PSU_POWER_IN     | 330 Watts         | ok
PSU_1_POWER_IN   | 174 Watts         | ok
PSU_2_POWER_IN   | 156 Watts         | ok
PSU_1_POWER_OUT  | 156 Watts         | ok
PSU_2_POWER_OUT  | 144 Watts         | ok
PSU_1_CURRENT_IN | 0.82 Amps         | ok
PSU_2_CURRENT_IN | 0.76 Amps         | ok
PSU1_CURRENT_OUT | 13.25 Amps        | ok
PSU2_CURRENT_OUT | 12.19 Amps        | ok
PWR_UNIT_REDUND  | 0x00              | ok
PWR_UNIT_STATUS  | 0x00              | ok
ACPI_STATE       | 0x00              | ok
SSD_0_TEMP       | 34 degrees C      | ok
SSD_1_TEMP       | 36 degrees C      | ok
PML_WEST_TEMP    | 57 degrees C      | ok
PML_LOCAL_TEMP   | 55 degrees C      | ok
PML_VDD_TEMP     | 59 degrees C      | ok
PML_EAST_TEMP    | 57 degrees C      | ok
SC_1_E810        | 42 degrees C      | ok
SC_2_E810        | 40 degrees C      | ok
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$

[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ echo $IP
2607:f160:10:9249:ce:40a:0:e016
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ rf_sensor_list.py -u XXXXXX -p XXXXXX -r https://[$IP]
Chassis 'Computer System Chassis' Status
  Sensor                    | Reading    | Health   | LF       | LC       | LNC      | UNC      | UC       | UF       | PhysicalContext
  State                     | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 214V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 156W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 213V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 132W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_V5                    | 4.9984V    | OK       | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | 12.1568V   | OK       | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | 3.2981V    | OK       | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | 1.045V     | OK       | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  RTC_Voltage               | 3.024V     | OK       | N/A      | 2.289    | N/A      | N/A      | 3.444    | N/A      | VoltageRegulator
  CPU_0_Vcore               | 1.8192V    | OK       | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | 1.2232V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | 1.2232V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | -51Cel     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_MARGIN              | 40Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  PSU_1_TEMP_2              | 44Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_1_TEMP_1              | 27Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  PSU_2_TEMP_2              | 45Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_2_TEMP_1              | 27Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  CPU_0_DIMM_C0             | 38Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_D0             | 37Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_A0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_B0             | 35Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_G0             | 37Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_H0             | 37Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_E0             | 37Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_F0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  DIMM_VRABCD_TEMP          | 35Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  DIMM_VREFGH_TEMP          | 34Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  MAX_DIMM_TEMP             | 38Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  PML_WEST_TEMP             | 55Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  PML_LOCAL_TEMP            | 54Cel      | OK       | N/A      | N/A      | N/A      | 80       | 85       | N/A      | Intake
  PML_VDD_TEMP              | 58Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 125      | N/A      | Intake
  PML_EAST_TEMP             | 55Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  SC_1_E810                 | 44Cel      | OK       | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SC_2_E810                 | 39Cel      | OK       | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SSD_0_TEMP                | 35Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  SSD_1_TEMP                | 36Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  INLET_TEMP_L              | 26Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  INLET_TEMP_R              | 24Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  MB_HSC_TEMP               | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  OUTLET_TEMP_L             | 40Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  OUTLET_TEMP_R             | 38Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  INLET_TEMP_MAX            | 26Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  OUTLET_TEMP_MAX           | 40Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  SYS_PCH_TEMP              | 33Cel      | OK       | N/A      | 5        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_TEMP                | 47Cel      | OK       | N/A      | N/A      | N/A      | 96       | 98       | N/A      | Intake
  SYS_FAN_1A                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_1B                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2A                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2B                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_1_FAN                 | 3840RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_2_FAN                 | 3840RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan

[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$  ipmitool -I lanplus -H $IP -U XXXXXX -P XXXXXX sdr
CPU_0_PROCHOT    | 0x00              | ok
CPU_0_STATUS     | 0x00              | ok
CPU_0_Vcore      | 1.82 Volts        | ok
CPU0DDR_ABC_1.2V | 1.22 Volts        | ok
CPU0DDR_DEF_1.2V | 1.22 Volts        | ok
CPU_0_DTS_TEMP   | -50 degrees C     | ok
CPU_0_TEMP       | 48 degrees C      | ok
CPU_0_MARGIN     | 40 degrees C      | ok
CPU0_Power       | 69 Watts          | ok
SYS_PCH_TEMP     | 33 degrees C      | ok
CPU_0_DIMM_C0    | 38 degrees C      | ok
CPU_0_DIMM_D0    | 37 degrees C      | ok
CPU_0_DIMM_A0    | 36 degrees C      | ok
CPU_0_DIMM_B0    | 35 degrees C      | ok
CPU_0_DIMM_G0    | 37 degrees C      | ok
CPU_0_DIMM_H0    | 37 degrees C      | ok
CPU_0_DIMM_E0    | 37 degrees C      | ok
CPU_0_DIMM_F0    | 36 degrees C      | ok
MAX_DIMM_TEMP    | 38 degrees C      | ok
INLET_TEMP_L     | 26 degrees C      | ok
INLET_TEMP_R     | 24 degrees C      | ok
INLET_TEMP_MAX   | 26 degrees C      | ok
OUTLET_TEMP_L    | 40 degrees C      | ok
OUTLET_TEMP_R    | 38 degrees C      | ok
OUTLET_TEMP_MAX  | 40 degrees C      | ok
SYS_FAN_1A       | 5000 RPM          | ok
SYS_FAN_1B       | 5500 RPM          | ok
SYS_FAN_2A       | 5000 RPM          | ok
SYS_FAN_2B       | 5500 RPM          | ok
SYS_FAN_1A_PWM   | 18 percent        | ok
SYS_FAN_1B_PWM   | 18 percent        | ok
SYS_FAN_2A_PWM   | 18 percent        | ok
SYS_FAN_2B_PWM   | 18 percent        | ok
SYS_V1.05        | 1.05 Volts        | ok
SYS_V12          | 12.16 Volts       | ok
SYS_V3.3         | 3.30 Volts        | ok
SYS_V5           | 5.01 Volts        | ok
CPU_CUPS         | 1 percent         | ok
MB_HSC_TEMP      | 36 degrees C      | ok
DIMM_VREFGH_TEMP | 34 degrees C      | ok
DIMM_VRABCD_TEMP | 35 degrees C      | ok
RTC_Voltage      | 3.02 Volts        | ok
MB_HSC_PIN       | 156 Watts         | ok
MB_HSC_PIN_AVG   | 152 Watts         | ok
MB_HSC_PEAK_PIN  | 388 Watts         | ok
PSU_1_STATUS     | 0x00              | ok
PSU_2_STATUS     | 0x00              | ok
PSU_1_FAN        | 3840 RPM          | ok
PSU_2_FAN        | 3840 RPM          | ok
PSU_1_TEMP_1     | 27 degrees C      | ok
PSU_2_TEMP_1     | 27 degrees C      | ok
PSU_1_TEMP_2     | 44 degrees C      | ok
PSU_2_TEMP_2     | 45 degrees C      | ok
PSU_POWER_IN     | 330 Watts         | ok
PSU_1_POWER_IN   | 168 Watts         | ok
PSU_2_POWER_IN   | 156 Watts         | ok
PSU_1_POWER_OUT  | 150 Watts         | ok
PSU_2_POWER_OUT  | 144 Watts         | ok
PSU_1_CURRENT_IN | 0.82 Amps         | ok
PSU_2_CURRENT_IN | 0.76 Amps         | ok
PSU1_CURRENT_OUT | 12.72 Amps        | ok
PSU2_CURRENT_OUT | 11.66 Amps        | ok
PWR_UNIT_REDUND  | 0x00              | ok
PWR_UNIT_STATUS  | 0x00              | ok
ACPI_STATE       | 0x00              | ok
SSD_0_TEMP       | 35 degrees C      | ok
SSD_1_TEMP       | 36 degrees C      | ok
PML_WEST_TEMP    | 55 degrees C      | ok
PML_LOCAL_TEMP   | 54 degrees C      | ok
PML_VDD_TEMP     | 58 degrees C      | ok
PML_EAST_TEMP    | 55 degrees C      | ok
SC_1_E810        | 44 degrees C      | ok
SC_2_E810        | 39 degrees C      | ok
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$

```

### Now pulling PSU_2 power and checking sensors


```log
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ echo $IP
2607:f160:10:9249:ce:40a:0:e015
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ rf_sensor_list.py -u XXXXXX -p XXXXXX -r https://[$IP]
Chassis 'Computer System Chassis' Status
  Sensor                    | Reading    | Health   | LF       | LC       | LNC      | UNC      | UC       | UF       | PhysicalContext
  State                     | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 213V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 300W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | Warning  | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 213V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_V5                    | 5.053V     | OK       | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | 12.138V    | OK       | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | 3.3287V    | OK       | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | 1.0532V    | OK       | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  RTC_Voltage               | 3.031V     | OK       | N/A      | 2.289    | N/A      | N/A      | 3.444    | N/A      | VoltageRegulator
  CPU_0_Vcore               | 1.8248V    | OK       | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | 1.2306V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | 1.2306V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | -51Cel     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_MARGIN              | 40Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  PSU_1_TEMP_2              | 45Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_1_TEMP_1              | 27Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  PSU_2_TEMP_2              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_2_TEMP_1              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  CPU_0_DIMM_C0             | 37Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_D0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_A0             | 35Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_B0             | 34Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_G0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_H0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_E0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_F0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  DIMM_VRABCD_TEMP          | 35Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  DIMM_VREFGH_TEMP          | 34Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  MAX_DIMM_TEMP             | 37Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  PML_WEST_TEMP             | 57Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  PML_LOCAL_TEMP            | 55Cel      | OK       | N/A      | N/A      | N/A      | 80       | 85       | N/A      | Intake
  PML_VDD_TEMP              | 59Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 125      | N/A      | Intake
  PML_EAST_TEMP             | 57Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  SC_1_E810                 | 42Cel      | OK       | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SC_2_E810                 | 40Cel      | OK       | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SSD_0_TEMP                | 34Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  SSD_1_TEMP                | 36Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  INLET_TEMP_L              | 26Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  INLET_TEMP_R              | 25Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  MB_HSC_TEMP               | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  OUTLET_TEMP_L             | 39Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  OUTLET_TEMP_R             | 37Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  INLET_TEMP_MAX            | 26Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  OUTLET_TEMP_MAX           | 39Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  SYS_PCH_TEMP              | 34Cel      | OK       | N/A      | 5        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_TEMP                | 47Cel      | OK       | N/A      | N/A      | N/A      | 96       | 98       | N/A      | Intake
  SYS_FAN_1A                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_1B                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2A                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2B                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_1_FAN                 | 4960RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_2_FAN                 | Absent     | N/A      | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan

[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ ipmitool -I lanplus -H $IP -U XXXXXX -P XXXXXX sdr
CPU_0_PROCHOT    | 0x00              | ok
CPU_0_STATUS     | 0x00              | ok
CPU_0_Vcore      | 1.82 Volts        | ok
CPU0DDR_ABC_1.2V | 1.23 Volts        | ok
CPU0DDR_DEF_1.2V | 1.23 Volts        | ok
CPU_0_DTS_TEMP   | -51 degrees C     | ok
CPU_0_TEMP       | 47 degrees C      | ok
CPU_0_MARGIN     | 39 degrees C      | ok
CPU0_Power       | 68 Watts          | ok
SYS_PCH_TEMP     | 33 degrees C      | ok
CPU_0_DIMM_C0    | 37 degrees C      | ok
CPU_0_DIMM_D0    | 36 degrees C      | ok
CPU_0_DIMM_A0    | 35 degrees C      | ok
CPU_0_DIMM_B0    | 34 degrees C      | ok
CPU_0_DIMM_G0    | 36 degrees C      | ok
CPU_0_DIMM_H0    | 36 degrees C      | ok
CPU_0_DIMM_E0    | 36 degrees C      | ok
CPU_0_DIMM_F0    | 36 degrees C      | ok
MAX_DIMM_TEMP    | 37 degrees C      | ok
INLET_TEMP_L     | 26 degrees C      | ok
INLET_TEMP_R     | 25 degrees C      | ok
INLET_TEMP_MAX   | 26 degrees C      | ok
OUTLET_TEMP_L    | 39 degrees C      | ok
OUTLET_TEMP_R    | 37 degrees C      | ok
OUTLET_TEMP_MAX  | 39 degrees C      | ok
SYS_FAN_1A       | 5125 RPM          | ok
SYS_FAN_1B       | 5500 RPM          | ok
SYS_FAN_2A       | 5125 RPM          | ok
SYS_FAN_2B       | 5500 RPM          | ok
SYS_FAN_1A_PWM   | 18 percent        | ok
SYS_FAN_1B_PWM   | 18 percent        | ok
SYS_FAN_2A_PWM   | 18 percent        | ok
SYS_FAN_2B_PWM   | 18 percent        | ok
SYS_V1.05        | 1.05 Volts        | ok
SYS_V12          | 12.14 Volts       | ok
SYS_V3.3         | 3.33 Volts        | ok
SYS_V5           | 5.05 Volts        | ok
CPU_CUPS         | 0 percent         | ok
MB_HSC_TEMP      | 36 degrees C      | ok
DIMM_VREFGH_TEMP | 34 degrees C      | ok
DIMM_VRABCD_TEMP | 35 degrees C      | ok
RTC_Voltage      | 3.03 Volts        | ok
MB_HSC_PIN       | 156 Watts         | ok
MB_HSC_PIN_AVG   | 156 Watts         | ok
MB_HSC_PEAK_PIN  | 440 Watts         | ok
PSU_1_STATUS     | 0x00              | ok
PSU_2_STATUS     | 0x00              | ok
PSU_1_FAN        | 4800 RPM          | ok
PSU_2_FAN        | no reading        | ns
PSU_1_TEMP_1     | 27 degrees C      | ok
PSU_2_TEMP_1     | no reading        | ns
PSU_1_TEMP_2     | 45 degrees C      | ok
PSU_2_TEMP_2     | no reading        | ns
PSU_POWER_IN     | 308 Watts         | ok
PSU_1_POWER_IN   | 312 Watts         | ok
PSU_2_POWER_IN   | no reading        | ns
PSU_1_POWER_OUT  | 288 Watts         | ok
PSU_2_POWER_OUT  | no reading        | ns
PSU_1_CURRENT_IN | 1.45 Amps         | ok
PSU_2_CURRENT_IN | no reading        | ns
PSU1_CURRENT_OUT | 23.85 Amps        | ok
PSU2_CURRENT_OUT | no reading        | ns
PWR_UNIT_REDUND  | 0x00              | ok
PWR_UNIT_STATUS  | 0x00              | ok
ACPI_STATE       | 0x00              | ok
SSD_0_TEMP       | 34 degrees C      | ok
SSD_1_TEMP       | 36 degrees C      | ok
PML_WEST_TEMP    | 57 degrees C      | ok
PML_LOCAL_TEMP   | 55 degrees C      | ok
PML_VDD_TEMP     | 59 degrees C      | ok
PML_EAST_TEMP    | 57 degrees C      | ok
SC_1_E810        | 42 degrees C      | ok
SC_2_E810        | 40 degrees C      | ok
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$

[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ echo $IP
2607:f160:10:9249:ce:40a:0:e016
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ rf_sensor_list.py -u XXXXXX -p XXXXXX -r https://[$IP]
Chassis 'Computer System Chassis' Status
  Sensor                    | Reading    | Health   | LF       | LC       | LNC      | UNC      | UC       | UF       | PhysicalContext
  State                     | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 213V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 294W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | Warning  | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 213V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_V5                    | 5.0062V    | OK       | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | 12.138V    | OK       | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | 3.2981V    | OK       | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | 1.04664V   | OK       | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  RTC_Voltage               | 3.024V     | OK       | N/A      | 2.289    | N/A      | N/A      | 3.444    | N/A      | VoltageRegulator
  CPU_0_Vcore               | 1.8164V    | OK       | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | 1.2232V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | 1.2232V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | -50Cel     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_MARGIN              | 39Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  PSU_1_TEMP_2              | 45Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_1_TEMP_1              | 27Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  PSU_2_TEMP_2              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_2_TEMP_1              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  CPU_0_DIMM_C0             | 38Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_D0             | 37Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_A0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_B0             | 35Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_G0             | 38Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_H0             | 37Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_E0             | 37Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_F0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  DIMM_VRABCD_TEMP          | 35Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  DIMM_VREFGH_TEMP          | 34Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  MAX_DIMM_TEMP             | 38Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  PML_WEST_TEMP             | 55Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  PML_LOCAL_TEMP            | 54Cel      | OK       | N/A      | N/A      | N/A      | 80       | 85       | N/A      | Intake
  PML_VDD_TEMP              | 58Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 125      | N/A      | Intake
  PML_EAST_TEMP             | 55Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  SC_1_E810                 | 44Cel      | OK       | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SC_2_E810                 | 39Cel      | OK       | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SSD_0_TEMP                | 35Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  SSD_1_TEMP                | 36Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  INLET_TEMP_L              | 26Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  INLET_TEMP_R              | 25Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  MB_HSC_TEMP               | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  OUTLET_TEMP_L             | 40Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  OUTLET_TEMP_R             | 38Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  INLET_TEMP_MAX            | 26Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  OUTLET_TEMP_MAX           | 40Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  SYS_PCH_TEMP              | 34Cel      | OK       | N/A      | 5        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_TEMP                | 48Cel      | OK       | N/A      | N/A      | N/A      | 96       | 98       | N/A      | Intake
  SYS_FAN_1A                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_1B                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2A                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2B                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_1_FAN                 | 4960RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_2_FAN                 | Absent     | N/A      | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan

[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$  ipmitool -I lanplus -H $IP -U XXXXXX -P XXXXXX sdr
CPU_0_PROCHOT    | 0x00              | ok
CPU_0_STATUS     | 0x00              | ok
CPU_0_Vcore      | 1.82 Volts        | ok
CPU0DDR_ABC_1.2V | 1.22 Volts        | ok
CPU0DDR_DEF_1.2V | 1.22 Volts        | ok
CPU_0_DTS_TEMP   | -50 degrees C     | ok
CPU_0_TEMP       | 48 degrees C      | ok
CPU_0_MARGIN     | 38 degrees C      | ok
CPU0_Power       | 70 Watts          | ok
SYS_PCH_TEMP     | 34 degrees C      | ok
CPU_0_DIMM_C0    | 38 degrees C      | ok
CPU_0_DIMM_D0    | 37 degrees C      | ok
CPU_0_DIMM_A0    | 36 degrees C      | ok
CPU_0_DIMM_B0    | 35 degrees C      | ok
CPU_0_DIMM_G0    | 38 degrees C      | ok
CPU_0_DIMM_H0    | 37 degrees C      | ok
CPU_0_DIMM_E0    | 37 degrees C      | ok
CPU_0_DIMM_F0    | 36 degrees C      | ok
MAX_DIMM_TEMP    | 38 degrees C      | ok
INLET_TEMP_L     | 27 degrees C      | ok
INLET_TEMP_R     | 25 degrees C      | ok
INLET_TEMP_MAX   | 27 degrees C      | ok
OUTLET_TEMP_L    | 40 degrees C      | ok
OUTLET_TEMP_R    | 38 degrees C      | ok
OUTLET_TEMP_MAX  | 40 degrees C      | ok
SYS_FAN_1A       | 5000 RPM          | ok
SYS_FAN_1B       | 5500 RPM          | ok
SYS_FAN_2A       | 5000 RPM          | ok
SYS_FAN_2B       | 5500 RPM          | ok
SYS_FAN_1A_PWM   | 18 percent        | ok
SYS_FAN_1B_PWM   | 18 percent        | ok
SYS_FAN_2A_PWM   | 18 percent        | ok
SYS_FAN_2B_PWM   | 18 percent        | ok
SYS_V1.05        | 1.05 Volts        | ok
SYS_V12          | 12.14 Volts       | ok
SYS_V3.3         | 3.30 Volts        | ok
SYS_V5           | 5.00 Volts        | ok
CPU_CUPS         | 3 percent         | ok
MB_HSC_TEMP      | 36 degrees C      | ok
DIMM_VREFGH_TEMP | 34 degrees C      | ok
DIMM_VRABCD_TEMP | 35 degrees C      | ok
RTC_Voltage      | 3.02 Volts        | ok
MB_HSC_PIN       | 140 Watts         | ok
MB_HSC_PIN_AVG   | 152 Watts         | ok
MB_HSC_PEAK_PIN  | 388 Watts         | ok
PSU_1_STATUS     | 0x00              | ok
PSU_2_STATUS     | 0x00              | ok
PSU_1_FAN        | 4800 RPM          | ok
PSU_2_FAN        | no reading        | ns
PSU_1_TEMP_1     | 27 degrees C      | ok
PSU_2_TEMP_1     | no reading        | ns
PSU_1_TEMP_2     | 44 degrees C      | ok
PSU_2_TEMP_2     | no reading        | ns
PSU_POWER_IN     | 308 Watts         | ok
PSU_1_POWER_IN   | 312 Watts         | ok
PSU_2_POWER_IN   | no reading        | ns
PSU_1_POWER_OUT  | 282 Watts         | ok
PSU_2_POWER_OUT  | no reading        | ns
PSU_1_CURRENT_IN | 1.45 Amps         | ok
PSU_2_CURRENT_IN | no reading        | ns
PSU1_CURRENT_OUT | 23.32 Amps        | ok
PSU2_CURRENT_OUT | no reading        | ns
PWR_UNIT_REDUND  | 0x00              | ok
PWR_UNIT_STATUS  | 0x00              | ok
ACPI_STATE       | 0x00              | ok
SSD_0_TEMP       | 35 degrees C      | ok
SSD_1_TEMP       | 36 degrees C      | ok
PML_WEST_TEMP    | 55 degrees C      | ok
PML_LOCAL_TEMP   | 54 degrees C      | ok
PML_VDD_TEMP     | 58 degrees C      | ok
PML_EAST_TEMP    | 55 degrees C      | ok
SC_1_E810        | 44 degrees C      | ok
SC_2_E810        | 39 degrees C      | ok
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$

```

### Now we plugged back in the power, will check again to confirm all returned as expected.

```log
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ rf_sensor_list.py -u XXXXXX -p XXXXXX -r https://[$IP]
Chassis 'Computer System Chassis' Status
  Sensor                    | Reading    | Health   | LF       | LC       | LNC      | UNC      | UC       | UF       | PhysicalContext
  State                     | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 214V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 144W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 213V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 138W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_V5                    | 5.053V     | OK       | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | 12.1568V   | OK       | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | 3.3236V    | OK       | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | 1.0532V    | OK       | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  RTC_Voltage               | 3.031V     | OK       | N/A      | 2.289    | N/A      | N/A      | 3.444    | N/A      | VoltageRegulator
  CPU_0_Vcore               | 1.8276V    | OK       | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | 1.2306V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | 1.2306V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | -50Cel     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_MARGIN              | 38Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  PSU_1_TEMP_2              | 46Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_1_TEMP_1              | 27Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  PSU_2_TEMP_2              | 43Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_2_TEMP_1              | 27Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  CPU_0_DIMM_C0             | 37Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_D0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_A0             | 34Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_B0             | 34Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_G0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_H0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_E0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_F0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  DIMM_VRABCD_TEMP          | 35Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  DIMM_VREFGH_TEMP          | 34Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  MAX_DIMM_TEMP             | 37Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  PML_WEST_TEMP             | 56Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  PML_LOCAL_TEMP            | 54Cel      | OK       | N/A      | N/A      | N/A      | 80       | 85       | N/A      | Intake
  PML_VDD_TEMP              | 59Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 125      | N/A      | Intake
  PML_EAST_TEMP             | 56Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  SC_1_E810                 | 42Cel      | OK       | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SC_2_E810                 | 39Cel      | OK       | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SSD_0_TEMP                | 34Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  SSD_1_TEMP                | 36Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  INLET_TEMP_L              | 25Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  INLET_TEMP_R              | 24Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  MB_HSC_TEMP               | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  OUTLET_TEMP_L             | 39Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  OUTLET_TEMP_R             | 38Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  INLET_TEMP_MAX            | 25Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  OUTLET_TEMP_MAX           | 39Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  SYS_PCH_TEMP              | 34Cel      | OK       | N/A      | 5        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_TEMP                | 48Cel      | OK       | N/A      | N/A      | N/A      | 96       | 98       | N/A      | Intake
  SYS_FAN_1A                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_1B                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2A                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2B                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_1_FAN                 | 3840RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_2_FAN                 | 4000RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan

[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ ipmitool -I lanplus -H $IP -U XXXXXX -P XXXXXX sdr
CPU_0_PROCHOT    | 0x00              | ok
CPU_0_STATUS     | 0x00              | ok
CPU_0_Vcore      | 1.82 Volts        | ok
CPU0DDR_ABC_1.2V | 1.23 Volts        | ok
CPU0DDR_DEF_1.2V | 1.23 Volts        | ok
CPU_0_DTS_TEMP   | -50 degrees C     | ok
CPU_0_TEMP       | 48 degrees C      | ok
CPU_0_MARGIN     | 38 degrees C      | ok
CPU0_Power       | 68 Watts          | ok
SYS_PCH_TEMP     | 33 degrees C      | ok
CPU_0_DIMM_C0    | 37 degrees C      | ok
CPU_0_DIMM_D0    | 36 degrees C      | ok
CPU_0_DIMM_A0    | 34 degrees C      | ok
CPU_0_DIMM_B0    | 34 degrees C      | ok
CPU_0_DIMM_G0    | 36 degrees C      | ok
CPU_0_DIMM_H0    | 36 degrees C      | ok
CPU_0_DIMM_E0    | 36 degrees C      | ok
CPU_0_DIMM_F0    | 36 degrees C      | ok
MAX_DIMM_TEMP    | 37 degrees C      | ok
INLET_TEMP_L     | 25 degrees C      | ok
INLET_TEMP_R     | 24 degrees C      | ok
INLET_TEMP_MAX   | 25 degrees C      | ok
OUTLET_TEMP_L    | 39 degrees C      | ok
OUTLET_TEMP_R    | 38 degrees C      | ok
OUTLET_TEMP_MAX  | 39 degrees C      | ok
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
MB_HSC_TEMP      | 36 degrees C      | ok
DIMM_VREFGH_TEMP | 34 degrees C      | ok
DIMM_VRABCD_TEMP | 35 degrees C      | ok
RTC_Voltage      | 3.02 Volts        | ok
MB_HSC_PIN       | 148 Watts         | ok
MB_HSC_PIN_AVG   | 156 Watts         | ok
MB_HSC_PEAK_PIN  | 440 Watts         | ok
PSU_1_STATUS     | 0x00              | ok
PSU_2_STATUS     | 0x00              | ok
PSU_1_FAN        | 3840 RPM          | ok
PSU_2_FAN        | 4000 RPM          | ok
PSU_1_TEMP_1     | 27 degrees C      | ok
PSU_2_TEMP_1     | 27 degrees C      | ok
PSU_1_TEMP_2     | 46 degrees C      | ok
PSU_2_TEMP_2     | 44 degrees C      | ok
PSU_POWER_IN     | 319 Watts         | ok
PSU_1_POWER_IN   | 168 Watts         | ok
PSU_2_POWER_IN   | 156 Watts         | ok
PSU_1_POWER_OUT  | 150 Watts         | ok
PSU_2_POWER_OUT  | 138 Watts         | ok
PSU_1_CURRENT_IN | 0.82 Amps         | ok
PSU_2_CURRENT_IN | 0.76 Amps         | ok
PSU1_CURRENT_OUT | 12.72 Amps        | ok
PSU2_CURRENT_OUT | 11.66 Amps        | ok
PWR_UNIT_REDUND  | 0x00              | ok
PWR_UNIT_STATUS  | 0x00              | ok
ACPI_STATE       | 0x00              | ok
SSD_0_TEMP       | 34 degrees C      | ok
SSD_1_TEMP       | 36 degrees C      | ok
PML_WEST_TEMP    | 56 degrees C      | ok
PML_LOCAL_TEMP   | 54 degrees C      | ok
PML_VDD_TEMP     | 59 degrees C      | ok
PML_EAST_TEMP    | 56 degrees C      | ok
SC_1_E810        | 42 degrees C      | ok
SC_2_E810        | 39 degrees C      | ok
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$

[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ echo $IP
2607:f160:10:9249:ce:40a:0:e016
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ rf_sensor_list.py -u XXXXXX -p XXXXXX -r https://[$IP]
Chassis 'Computer System Chassis' Status
  Sensor                    | Reading    | Health   | LF       | LC       | LNC      | UNC      | UC       | UF       | PhysicalContext
  State                     | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 213V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 144W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 213V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 132W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_V5                    | 5.0062V    | OK       | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | 12.1568V   | OK       | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | 3.2981V    | OK       | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | 1.045V     | OK       | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  RTC_Voltage               | 3.024V     | OK       | N/A      | 2.289    | N/A      | N/A      | 3.444    | N/A      | VoltageRegulator
  CPU_0_Vcore               | 1.8164V    | OK       | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | 1.2232V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | 1.2232V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | -47Cel     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_MARGIN              | 36Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  PSU_1_TEMP_2              | 46Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_1_TEMP_1              | 27Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  PSU_2_TEMP_2              | 44Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_2_TEMP_1              | 27Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  CPU_0_DIMM_C0             | 38Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_D0             | 37Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_A0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_B0             | 35Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_G0             | 37Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_H0             | 37Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_E0             | 37Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_F0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  DIMM_VRABCD_TEMP          | 35Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  DIMM_VREFGH_TEMP          | 34Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  MAX_DIMM_TEMP             | 38Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  PML_WEST_TEMP             | 55Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  PML_LOCAL_TEMP            | 54Cel      | OK       | N/A      | N/A      | N/A      | 80       | 85       | N/A      | Intake
  PML_VDD_TEMP              | 58Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 125      | N/A      | Intake
  PML_EAST_TEMP             | 54Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  SC_1_E810                 | 43Cel      | OK       | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SC_2_E810                 | 39Cel      | OK       | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SSD_0_TEMP                | 35Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  SSD_1_TEMP                | 36Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  INLET_TEMP_L              | 26Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  INLET_TEMP_R              | 24Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  MB_HSC_TEMP               | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  OUTLET_TEMP_L             | 40Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  OUTLET_TEMP_R             | 38Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  INLET_TEMP_MAX            | 26Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  OUTLET_TEMP_MAX           | 40Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  SYS_PCH_TEMP              | 33Cel      | OK       | N/A      | 5        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_TEMP                | 51Cel      | OK       | N/A      | N/A      | N/A      | 96       | 98       | N/A      | Intake
  SYS_FAN_1A                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_1B                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2A                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2B                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_1_FAN                 | 3840RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_2_FAN                 | 4000RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan

[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$  ipmitool -I lanplus -H $IP -U XXXXXX -P XXXXXX sdr
CPU_0_PROCHOT    | 0x00              | ok
CPU_0_STATUS     | 0x00              | ok
CPU_0_Vcore      | 1.82 Volts        | ok
CPU0DDR_ABC_1.2V | 1.22 Volts        | ok
CPU0DDR_DEF_1.2V | 1.22 Volts        | ok
CPU_0_DTS_TEMP   | -51 degrees C     | ok
CPU_0_TEMP       | 47 degrees C      | ok
CPU_0_MARGIN     | 40 degrees C      | ok
CPU0_Power       | 70 Watts          | ok
SYS_PCH_TEMP     | 34 degrees C      | ok
CPU_0_DIMM_C0    | 38 degrees C      | ok
CPU_0_DIMM_D0    | 37 degrees C      | ok
CPU_0_DIMM_A0    | 36 degrees C      | ok
CPU_0_DIMM_B0    | 35 degrees C      | ok
CPU_0_DIMM_G0    | 37 degrees C      | ok
CPU_0_DIMM_H0    | 37 degrees C      | ok
CPU_0_DIMM_E0    | 37 degrees C      | ok
CPU_0_DIMM_F0    | 36 degrees C      | ok
MAX_DIMM_TEMP    | 38 degrees C      | ok
INLET_TEMP_L     | 26 degrees C      | ok
INLET_TEMP_R     | 25 degrees C      | ok
INLET_TEMP_MAX   | 26 degrees C      | ok
OUTLET_TEMP_L    | 40 degrees C      | ok
OUTLET_TEMP_R    | 38 degrees C      | ok
OUTLET_TEMP_MAX  | 40 degrees C      | ok
SYS_FAN_1A       | 5000 RPM          | ok
SYS_FAN_1B       | 5500 RPM          | ok
SYS_FAN_2A       | 5125 RPM          | ok
SYS_FAN_2B       | 5500 RPM          | ok
SYS_FAN_1A_PWM   | 18 percent        | ok
SYS_FAN_1B_PWM   | 18 percent        | ok
SYS_FAN_2A_PWM   | 18 percent        | ok
SYS_FAN_2B_PWM   | 18 percent        | ok
SYS_V1.05        | 1.05 Volts        | ok
SYS_V12          | 12.14 Volts       | ok
SYS_V3.3         | 3.30 Volts        | ok
SYS_V5           | 5.00 Volts        | ok
CPU_CUPS         | 2 percent         | ok
MB_HSC_TEMP      | 36 degrees C      | ok
DIMM_VREFGH_TEMP | 34 degrees C      | ok
DIMM_VRABCD_TEMP | 35 degrees C      | ok
RTC_Voltage      | 3.02 Volts        | ok
MB_HSC_PIN       | 152 Watts         | ok
MB_HSC_PIN_AVG   | 152 Watts         | ok
MB_HSC_PEAK_PIN  | 388 Watts         | ok
PSU_1_STATUS     | 0x00              | ok
PSU_2_STATUS     | 0x00              | ok
PSU_1_FAN        | 3840 RPM          | ok
PSU_2_FAN        | 4000 RPM          | ok
PSU_1_TEMP_1     | 27 degrees C      | ok
PSU_2_TEMP_1     | 27 degrees C      | ok
PSU_1_TEMP_2     | 46 degrees C      | ok
PSU_2_TEMP_2     | 44 degrees C      | ok
PSU_POWER_IN     | 319 Watts         | ok
PSU_1_POWER_IN   | 168 Watts         | ok
PSU_2_POWER_IN   | 156 Watts         | ok
PSU_1_POWER_OUT  | 150 Watts         | ok
PSU_2_POWER_OUT  | 138 Watts         | ok
PSU_1_CURRENT_IN | 0.82 Amps         | ok
PSU_2_CURRENT_IN | 0.76 Amps         | ok
PSU1_CURRENT_OUT | 12.19 Amps        | ok
PSU2_CURRENT_OUT | 11.13 Amps        | ok
PWR_UNIT_REDUND  | 0x00              | ok
PWR_UNIT_STATUS  | 0x00              | ok
ACPI_STATE       | 0x00              | ok
SSD_0_TEMP       | 35 degrees C      | ok
SSD_1_TEMP       | 36 degrees C      | ok
PML_WEST_TEMP    | 55 degrees C      | ok
PML_LOCAL_TEMP   | 54 degrees C      | ok
PML_VDD_TEMP     | 58 degrees C      | ok
PML_EAST_TEMP    | 54 degrees C      | ok
SC_1_E810        | 44 degrees C      | ok
SC_2_E810        | 39 degrees C      | ok
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$


```

### We observed exactly what we expected to happen to sensors during power cord pull

### Now I'm validating the hosts did not have a power intruption during our failover of power

```log
WARNING: Unauthorized access to this system is forbidden and will be
prosecuted by law. By accessing this system, you agree that your
actions may be monitored if unauthorized usage is suspected.


====================================================================
         SYSTEM: welktxef-d931887-021
====================================================================


Linux controller-0 5.10.0-6-rt-amd64 #1 SMP PREEMPT_RT StarlingX Debian 5.10.177-1.stx.73 (2023-11-25 x86_64
Last login: Thu Mar 14 01:22:28 UTC 2024 from 2607:f160:10:9239:ce:290:0:3000 on pts/0
XXXXXX@controller-0:~$ uptime
 21:17:49 up 20:32,  1 user,  load average: 9.26, 8.88, 9.25
XXXXXX@controller-0:~$



controller-0 login: XXXXXX
Password:

XXXXXX Unauthorized access to this system is forbidden and will be
prosecuted by law. By accessing this system, you agree that your
actions may be monitored if unauthorized usage is suspected.


====================================================================
         SYSTEM: welktxef-d931883-022
====================================================================


Linux controller-0 5.10.0-6-rt-amd64 #1 SMP PREEMPT_RT StarlingX Debian 5.10.177-1.stx.73 (2023-11-25 x86_64
Last login: Thu Mar 14 18:37:37 UTC 2024 from 2607:f160:10:9105:ce:290:0:11 on pts/0
XXXXXX@controller-0:~$ uptime
 21:20:01 up 7 days, 20:04,  2 users,  load average: 4.21, 3.10, 3.04
XXXXXX@controller-0:~$



```


### Uptime shows that neither host in the chassis lost power during power cord failure, we are a pass on this test.