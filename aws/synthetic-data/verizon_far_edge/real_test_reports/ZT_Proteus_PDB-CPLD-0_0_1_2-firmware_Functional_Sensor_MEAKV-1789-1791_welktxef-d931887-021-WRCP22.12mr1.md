# ZT Proteus .46 BMC firmware 
# ZT Proteus BIOS .23
# 0.0.1.2 PDBCPLD firmware Validatoion
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

### MEAKV-1789
### List All Sensor data in ipmitool
```sh
sudo -i 
ipmitool sensor
```

```log
root@controller-0:~# ipmitool sensor
CPU_0_PROCHOT    | 0x0        | discrete   | 0x0080| na        | na        | na        | na        | na        | na
CPU_0_STATUS     | 0x0        | discrete   | 0x8080| na        | na        | na        | na        | na        | na
CPU_0_Vcore      | 1.819      | Volts      | ok    | na        | 1.690     | na        | na        | 1.870     | na
CPU0DDR_ABC_1.2V | 1.231      | Volts      | ok    | na        | 1.134     | na        | na        | 1.256     | na
CPU0DDR_DEF_1.2V | 1.231      | Volts      | ok    | na        | 1.134     | na        | na        | 1.256     | na
CPU_0_DTS_TEMP   | -34.000    | degrees C  | ok    | na        | na        | na        | na        | na        | na
CPU_0_TEMP       | 64.000     | degrees C  | ok    | na        | na        | na        | 96.000    | 98.000    | na
CPU_0_MARGIN     | 23.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
CPU0_Power       | 125.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_PCH_TEMP     | 34.000     | degrees C  | ok    | na        | 5.000     | na        | na        | 82.000    | na
CPU_0_DIMM_C0    | 40.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_D0    | 38.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_A0    | 36.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_B0    | 36.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_G0    | 39.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_H0    | 38.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_E0    | 38.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_F0    | 37.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
MAX_DIMM_TEMP    | 40.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
INLET_TEMP_L     | 25.000     | degrees C  | ok    | na        | -6.000    | na        | 50.000    | 59.000    | 61.000
INLET_TEMP_R     | 24.000     | degrees C  | ok    | na        | -6.000    | na        | 50.000    | 59.000    | 61.000
INLET_TEMP_MAX   | 25.000     | degrees C  | ok    | na        | -6.000    | na        | 50.000    | 59.000    | 61.000
OUTLET_TEMP_L    | 46.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
OUTLET_TEMP_R    | 42.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
OUTLET_TEMP_MAX  | 46.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 5000.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1B       | 5500.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_2A       | 5000.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_2B       | 5500.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1A_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1B_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_2A_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_2B_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_V1.05        | 1.053      | Volts      | ok    | na        | 0.993     | na        | na        | 1.097     | na
SYS_V12          | 12.138     | Volts      | ok    | na        | 11.348    | na        | na        | 12.552    | na
SYS_V3.3         | 3.329      | Volts      | ok    | na        | 3.104     | na        | na        | 3.431     | na
SYS_V5           | 5.053      | Volts      | ok    | na        | 4.725     | na        | na        | 5.225     | na
CPU_CUPS         | 1.000      | percent    | ok    | na        | na        | na        | na        | 100.000   | na
MB_HSC_TEMP      | 41.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 125.000   | na
DIMM_VREFGH_TEMP | 35.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 125.000   | na
DIMM_VRABCD_TEMP | 36.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 125.000   | na
RTC_Voltage      | 3.038      | Volts      | ok    | na        | 2.289     | na        | na        | 3.444     | na
MB_HSC_PIN       | 220.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
MB_HSC_PIN_AVG   | 220.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
MB_HSC_PEAK_PIN  | 440.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_1_STATUS     | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
PSU_2_STATUS     | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
PSU_1_FAN        | 3840.000   | RPM        | ok    | 800.000   | 1120.000  | na        | na        | na        | na
PSU_2_FAN        | 4000.000   | RPM        | ok    | 800.000   | 1120.000  | na        | na        | na        | na
PSU_1_TEMP_1     | 27.000     | degrees C  | ok    | na        | na        | na        | na        | 60.000    | 64.000
PSU_2_TEMP_1     | 27.000     | degrees C  | ok    | na        | na        | na        | na        | 60.000    | 64.000
PSU_1_TEMP_2     | 46.000     | degrees C  | ok    | na        | na        | na        | na        | 92.000    | 97.000
PSU_2_TEMP_2     | 46.000     | degrees C  | ok    | na        | na        | na        | na        | 92.000    | 97.000
PSU_POWER_IN     | 385.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_1_POWER_IN   | 198.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_2_POWER_IN   | 186.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_1_POWER_OUT  | 180.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_2_POWER_OUT  | 168.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_1_CURRENT_IN | 0.945      | Amps       | ok    | na        | na        | na        | na        | na        | na
PSU_2_CURRENT_IN | 0.882      | Amps       | ok    | na        | na        | na        | na        | na        | na
PSU1_CURRENT_OUT | 14.840     | Amps       | ok    | na        | na        | na        | na        | na        | na
PSU2_CURRENT_OUT | 13.780     | Amps       | ok    | na        | na        | na        | na        | na        | na
PWR_UNIT_REDUND  | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
PWR_UNIT_STATUS  | 0x0        | discrete   | 0x0080| na        | na        | na        | na        | na        | na
ACPI_STATE       | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
SSD_0_TEMP       | 34.000     | degrees C  | ok    | na        | 0.000     | na        | na        | 70.000    | 79.000
SSD_1_TEMP       | 36.000     | degrees C  | ok    | na        | 0.000     | na        | na        | 70.000    | 79.000
PML_WEST_TEMP    | 57.000     | degrees C  | ok    | na        | na        | na        | na        | 110.000   | 114.000
PML_LOCAL_TEMP   | 55.000     | degrees C  | ok    | na        | na        | na        | 80.000    | 85.000    | na
PML_VDD_TEMP     | 59.000     | degrees C  | ok    | na        | na        | na        | na        | 125.000   | na
PML_EAST_TEMP    | 57.000     | degrees C  | ok    | na        | na        | na        | na        | 110.000   | 114.000
SC_1_E810        | 42.000     | degrees C  | ok    | na        | 0.000     | 5.000     | 100.000   | 105.000   | 115.000
SC_2_E810        | 40.000     | degrees C  | ok    | na        | 0.000     | 5.000     | 100.000   | 105.000   | 115.000
root@controller-0:~#
```


### MEAKV-1790
### List All Sensor data in RedFish

### Command is ran from Ansible host in Lab
```sh
source ~/python_venvs/ansible_2.10.15/bin/activate
rf_sensor_list.py -u XXXXXX -p XXXXXX -r https://[2607:f160:10:80b1:ce:40a:0:e008]
```

```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ rf_sensor_list.py -u XXXXXX -p XXXXXX -r https://[$IP]
Chassis 'Computer System Chassis' Status
  Sensor                    | Reading    | Health   | LF       | LC       | LNC      | UNC      | UC       | UF       | PhysicalContext
  State                     | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_V5                    | 5.053V     | OK       | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | 12.138V    | OK       | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | 3.3287V    | OK       | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | 1.0532V    | OK       | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  RTC_Voltage               | 3.038V     | OK       | N/A      | 2.289    | N/A      | N/A      | 3.444    | N/A      | VoltageRegulator
  CPU_0_Vcore               | 1.8164V    | OK       | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | 1.2306V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | 1.2306V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | -33Cel     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_MARGIN              | 21Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_PROCHOT             | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  PSU_1_TEMP_2              | 46Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_1_TEMP_1              | 27Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  PSU_2_TEMP_2              | 46Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_2_TEMP_1              | 27Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  CPU_0_DIMM_C0             | 40Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_D0             | 38Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_A0             | 37Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_B0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_G0             | 39Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_H0             | 38Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_E0             | 38Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_F0             | 37Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  DIMM_VRABCD_TEMP          | 37Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  DIMM_VREFGH_TEMP          | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  MAX_DIMM_TEMP             | 40Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
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
  MB_HSC_TEMP               | 41Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  OUTLET_TEMP_L             | 46Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  OUTLET_TEMP_R             | 41Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  INLET_TEMP_MAX            | 26Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  OUTLET_TEMP_MAX           | 46Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  SYS_PCH_TEMP              | 34Cel      | OK       | N/A      | 5        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_TEMP                | 65Cel      | OK       | N/A      | N/A      | N/A      | 96       | 98       | N/A      | Intake
  SYS_FAN_1A                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_1B                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2A                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2B                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_1_FAN                 | 3840RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_2_FAN                 | 4000RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan

(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$
```

### MEAKV-1791
### List all sensor and data for both previous PDB firmware version as well as new PDB firmware version
### Compare the results of both to ensure nothing new or if anything has changed in format or sensors   

### Command is ran from Ansible host in Lab
```sh
source ~/python_venvs/ansible_2.10.15/bin/activate
rf_sensor_list.py -u XXXXXX -p XXXXXX -r https://[2607:f160:10:80b1:ce:40a:0:e008]
```

### Target PDB 0.0.1.2 (new in test version)

```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[${IP}]/redfish/v1/UpdateService/FirmwareInventory/PDBCPLD | jq .
{
  "@odata.context": "/redfish/v1/$metadata#SoftwareInventory.SoftwareInventory",
  "@odata.etag": "\"1710289590\"",
  "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/PDBCPLD",
  "@odata.type": "#SoftwareInventory.v1_2_3.SoftwareInventory",
  "Id": "PDBCPLD",
  "Name": "PDBCPLD",
  "Updateable": true,
  "Version": "0.0.1.2"
}
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$
```

```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[${IP}]/redfish/v1/UpdateService/FirmwareInventory/BMC  | jq .
{
  "@odata.context": "/redfish/v1/$metadata#SoftwareInventory.SoftwareInventory",
  "@odata.etag": "\"1710289747\"",
  "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/BMC",
  "@odata.type": "#SoftwareInventory.v1_2_3.SoftwareInventory",
  "Id": "BMC",
  "Name": "BMC",
  "Updateable": true,
  "Version": "0.46.00"
}
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ rf_sensor_list.py -u XXXXXX -p XXXXXX -r https://[2607:f160:10:80b1:ce:40a:0:e008]
Chassis 'Computer System Chassis' Status
  Sensor                    | Reading    | Health   | LF       | LC       | LNC      | UNC      | UC       | UF       | PhysicalContext
  State                     | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 212V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 186W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 213V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 162W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_V5                    | 5.014V     | OK       | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | 12.1944V   | OK       | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | 3.3287V    | OK       | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | 1.05156V   | OK       | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  RTC_Voltage               | 3.024V     | OK       | N/A      | 2.289    | N/A      | N/A      | 3.444    | N/A      | VoltageRegulator
  CPU_0_Vcore               | 1.808V     | OK       | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | 1.2269V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | 1.2232V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | -41Cel     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_MARGIN              | 30Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_PROCHOT             | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  PSU_1_TEMP_2              | 45Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_1_TEMP_1              | 27Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  PSU_2_TEMP_2              | 44Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_2_TEMP_1              | 26Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  CPU_0_DIMM_C0             | 40Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_D0             | 38Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_A0             | 37Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_B0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_G0             | 38Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_H0             | 37Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_E0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_F0             | 35Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  DIMM_VRABCD_TEMP          | 40Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  DIMM_VREFGH_TEMP          | 37Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  MAX_DIMM_TEMP             | 40Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  PML_WEST_TEMP             | 62Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  PML_LOCAL_TEMP            | 60Cel      | OK       | N/A      | N/A      | N/A      | 80       | 85       | N/A      | Intake
  PML_VDD_TEMP              | 68Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 125      | N/A      | Intake
  PML_EAST_TEMP             | 62Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  SC_1_E810                 | 44Cel      | OK       | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SC_2_E810                 | 40Cel      | OK       | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SSD_0_TEMP                | 30Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  SSD_1_TEMP                | 30Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  INLET_TEMP_L              | 27Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  INLET_TEMP_R              | 25Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  MB_HSC_TEMP               | 38Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  OUTLET_TEMP_L             | 43Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  OUTLET_TEMP_R             | 40Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  INLET_TEMP_MAX            | 27Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  OUTLET_TEMP_MAX           | 43Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  SYS_PCH_TEMP              | 32Cel      | OK       | N/A      | 5        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_TEMP                | 57Cel      | OK       | N/A      | N/A      | N/A      | 96       | 98       | N/A      | Intake
  SYS_FAN_1A                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_1B                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2A                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2B                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_1_FAN                 | 3840RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_2_FAN                 | 4000RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan

(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 ~]$
```

### Previous PDB 0.0.1.0 (new in test version)
### Target Subcloud welktxef-d931887-021 


```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 pdb-cpld-v10-20240220]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[${IP}]/redfish/v1/UpdateService/FirmwareInventory/PDBCPLD | jq .
{
  "@odata.context": "/redfish/v1/$metadata#SoftwareInventory.SoftwareInventory",
  "@odata.etag": "\"1710289590\"",
  "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/PDBCPLD",
  "@odata.type": "#SoftwareInventory.v1_2_3.SoftwareInventory",
  "Id": "PDBCPLD",
  "Name": "PDBCPLD",
  "Updateable": true,
  "Version": "0.0.1.0"
}
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 pdb-cpld-v10-20240220]$ rf_sensor_list.py -u XXXXXX -p XXXXXX -r https://[$IP]
Chassis 'Computer System Chassis' Status
  Sensor                    | Reading    | Health   | LF       | LC       | LNC      | UNC      | UC       | UF       | PhysicalContext
  State                     | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 212V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 192W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 213V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 168W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_V5                    | 5.053V     | OK       | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | 12.138V    | OK       | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | 3.3287V    | OK       | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | 1.0532V    | OK       | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  RTC_Voltage               | 3.031V     | OK       | N/A      | 2.289    | N/A      | N/A      | 3.444    | N/A      | VoltageRegulator
  CPU_0_Vcore               | 1.8164V    | OK       | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | 1.2306V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | 1.2306V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | -32Cel     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_MARGIN              | 21Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_PROCHOT             | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  PSU_1_TEMP_2              | 46Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_1_TEMP_1              | 28Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  PSU_2_TEMP_2              | 46Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_2_TEMP_1              | 28Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  CPU_0_DIMM_C0             | 40Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_D0             | 37Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_A0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_B0             | 35Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_G0             | 39Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_H0             | 37Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_E0             | 37Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_F0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  DIMM_VRABCD_TEMP          | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  DIMM_VREFGH_TEMP          | 35Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  MAX_DIMM_TEMP             | 40Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  PML_WEST_TEMP             | 56Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  PML_LOCAL_TEMP            | 54Cel      | OK       | N/A      | N/A      | N/A      | 80       | 85       | N/A      | Intake
  PML_VDD_TEMP              | 58Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 125      | N/A      | Intake
  PML_EAST_TEMP             | 56Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  SC_1_E810                 | 42Cel      | OK       | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SC_2_E810                 | 39Cel      | OK       | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SSD_0_TEMP                | 33Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  SSD_1_TEMP                | 35Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  INLET_TEMP_L              | 25Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  INLET_TEMP_R              | 24Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  MB_HSC_TEMP               | 40Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  OUTLET_TEMP_L             | 44Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  OUTLET_TEMP_R             | 41Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  INLET_TEMP_MAX            | 25Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  OUTLET_TEMP_MAX           | 44Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  SYS_PCH_TEMP              | 33Cel      | OK       | N/A      | 5        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_TEMP                | 66Cel      | OK       | N/A      | N/A      | N/A      | 96       | 98       | N/A      | Intake
  SYS_FAN_1A                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_1B                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2A                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2B                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_1_FAN                 | 3840RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_2_FAN                 | 4000RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan

(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 pdb-cpld-v10-20240220]$

```

### Installation of "0.0.1.0" should show missing PSU_1_FAN and PSU_TEMP, but doesn't, so lets power cycle it and see.

```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 pdb-cpld-v10-20240220]$ curl --globoff -L -w "%{http_code} %{url_effective}\\n" -ku XXXXXX:XXXXXX -H "Content-Type: application/json" -X POST https://[$IP]/redfish/v1/Chassis/Self/Actions/Oem/AcReset -d '{"ResetType": "AcPowerCycle"}'
{"@odata.context":"/redfish/v1/$metadata#Task.Task","@odata.id":"/redfish/v1/TaskService/Tasks/23","@odata.type":"#Task.v1_4_2.Task","Description":"Task for Chassis AC Power Reset","Id":"23","Name":"Chassis AC Power Reset","TaskState":"New"}202 https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Chassis/Self/Actions/Oem/AcReset
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 pdb-cpld-v10-20240220]$ echo $IP
2607:f160:10:9249:ce:40a:0:e015
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 pdb-cpld-v10-20240220]$

(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 pdb-cpld-v10-20240220]$ rf_sensor_list.py -u XXXXXX -p XXXXXX -r https://[$IP]
Chassis 'Computer System Chassis' Status
  Sensor                    | Reading    | Health   | LF       | LC       | LNC      | UNC      | UC       | UF       | PhysicalContext
  State                     | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 0V         | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 0V         | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_V5                    | 5.053V     | OK       | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | 12.138V    | OK       | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | 3.3287V    | OK       | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | 1.05484V   | OK       | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  RTC_Voltage               | 3.038V     | OK       | N/A      | 2.289    | N/A      | N/A      | 3.444    | N/A      | VoltageRegulator
  CPU_0_Vcore               | 1.8192V    | OK       | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | 1.2306V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | 1.2306V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | -53Cel     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_MARGIN              | 42Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  PSU_1_TEMP_2              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_1_TEMP_1              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  PSU_2_TEMP_2              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_2_TEMP_1              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  CPU_0_DIMM_C0             | 31Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_D0             | 30Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_A0             | 30Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_B0             | 30Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_G0             | 31Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_H0             | 30Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_E0             | 31Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_F0             | 30Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  DIMM_VRABCD_TEMP          | 31Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  DIMM_VREFGH_TEMP          | 30Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  MAX_DIMM_TEMP             | 31Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  PML_WEST_TEMP             | 44Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  PML_LOCAL_TEMP            | 40Cel      | OK       | N/A      | N/A      | N/A      | 80       | 85       | N/A      | Intake
  PML_VDD_TEMP              | 43Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 125      | N/A      | Intake
  PML_EAST_TEMP             | 44Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  SC_1_E810                 | 35Cel      | OK       | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SC_2_E810                 | 34Cel      | OK       | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SSD_0_TEMP                | 30Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  SSD_1_TEMP                | 31Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  INLET_TEMP_L              | 24Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  INLET_TEMP_R              | 23Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  MB_HSC_TEMP               | 33Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  OUTLET_TEMP_L             | 36Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  OUTLET_TEMP_R             | 34Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  INLET_TEMP_MAX            | 24Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  OUTLET_TEMP_MAX           | 36Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  SYS_PCH_TEMP              | 29Cel      | OK       | N/A      | 5        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_TEMP                | 45Cel      | OK       | N/A      | N/A      | N/A      | 96       | 98       | N/A      | Intake
  SYS_FAN_1A                | 29%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_1B                | 29%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2A                | 29%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2B                | 29%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_1_FAN                 | Absent     | N/A      | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_2_FAN                 | Absent     | N/A      | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan

(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 pdb-cpld-v10-20240220]$


```
### Here are the issues with PDB-CPLD 0.0.1.0 and BMC .46 BIOS .23, Absent PSU FAN & TEMP as they show "Absent" In a Redfish call
### Also noticed that Power Supply Bay Line Input voltage drops to 0V from 212V with 0.0.1.0 installed. 

PSU_1_TEMP_2              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_1_TEMP_1              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  PSU_2_TEMP_2              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_2_TEMP_1              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
PSU_1_FAN                 | Absent     | N/A      | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_2_FAN                 | Absent     | N/A      | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
Power Supply Bay LineInpu | 0V         | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A


### compare sensor name list before/after firmware upgrade

```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 PDB-CPLD]$ cat 0.0.1.2.rf_sensor-out.txt | awk -F\| '{print $1}' > 0.0.1.2-sensor-name-list.txt
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 PDB-CPLD]$ cat 0.0.1.0.rf_sensor-out.txt | awk -F\| '{print $1}' > 0.0.1.0-sensor-name-list.txt
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 PDB-CPLD]$ diff 0.0.1.0-sensor-name-list.txt 0.0.1.2-sensor-name-list.txt
6a7
>   Power Supply Bay LastPowe
9a11
>   Power Supply Bay LastPowe
```

### Results
The new firmware works with restoration of PSU sensor data reading with BMC .46 and Bios .23
