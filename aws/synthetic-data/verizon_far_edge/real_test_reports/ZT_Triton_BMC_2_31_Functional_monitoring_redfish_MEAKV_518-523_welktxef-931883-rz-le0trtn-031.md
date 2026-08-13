# ZT Triton 2.31 BMC BIOS 2.10
# 10/15/25 James Patchett - MTCE Lab VCPfe
# validation MEAKV-518-523

##  welktxef-931883-rz-le0trtn-031
BMC:  2607:f160:10:9249:ce:40a:0:e01f
OAM:  2607:f160:10:9249:ce:40a:0:f402

## Subcloud welktxef-d931883-031 Info
```log
XXXXXX@controller-0:~$ source /etc/platform/openrc
[XXXXXX@controller-0 ~(keystone_admin)]$ system show
+------------------------+--------------------------------------+
| Property               | Value                                |
+------------------------+--------------------------------------+
| contact                | None                                 |
| created_at             | 2025-10-20T23:21:57.481049+00:00     |
| description            | None                                 |
| distributed_cloud_role | subcloud                             |
| https_enabled          | True                                 |
| latitude               | None                                 |
| location               | None                                 |
| longitude              | None                                 |
| name                   | welktxef-d931883-031                 |
| region_name            | welktxef-d931883-031                 |
| sdn_enabled            | False                                |
| security_feature       | spectre_meltdown_v1                  |
| service_project_name   | services                             |
| shared_services        | []                                   |
| software_version       | 22.12                                |
| system_mode            | simplex                              |
| system_type            | All-in-one                           |
| timezone               | UTC                                  |
| updated_at             | 2025-10-21T00:14:11.015126+00:00     |
| uuid                   | 30ed6c47-41be-4de3-be49-4b2b4eb7f379 |
| vswitch_type           | none                                 |
+------------------------+--------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ system application-list
+--------------------------+----------+-------------------------------------------+------------------+---------+-----------+
| application              | version  | manifest name                             | manifest file    | status  | progress  |
+--------------------------+----------+-------------------------------------------+------------------+---------+-----------+
| cert-manager             | 22.12-8  | cert-manager-fluxcd-manifests             | fluxcd-manifests | applied | completed |
| metrics-server           | 22.12-2  | metrics-server-fluxcd-manifests           | fluxcd-manifests | applied | completed |
| nginx-ingress-controller | 22.12-1  | nginx-ingress-controller-fluxcd-manifests | fluxcd-manifests | applied | completed |
| oidc-auth-apps           | 22.12-6  | oidc-auth-apps-fluxcd-manifests           | fluxcd-manifests | applied | completed |
| platform-integ-apps      | 22.12-72 | platform-integ-apps-fluxcd-manifests      | fluxcd-manifests | applied | completed |
| wr-analytics             | 23.09-1  | wr-analytics-fluxcd-manifests             | fluxcd-manifests | applied | completed |
+--------------------------+----------+-------------------------------------------+------------------+---------+-----------+
[XXXXXX@controller-0 ~(keystone_admin)]$ sw-patch query
      Patch ID         RR  Release  Patch State
=====================  ==  =======  ===========
WRCP_22.12_PATCH_0001  Y    22.12    Committed
WRCP_22.12_PATCH_0002  Y    22.12    Committed
WRCP_22.12_PATCH_0003  Y    22.12    Committed
WRCP_22.12_PATCH_0004  Y    22.12    Committed
WRCP_22.12_PATCH_0005  Y    22.12    Committed

[XXXXXX@controller-0 ~(keystone_admin)]$
```

## Check Sensors before we start load

```log
root@controller-0:~# ipmitool sensor | grep -e CPU_0_TEMP -e CPU0_Power -e FAN -e CPU_CUPS
CPU_0_TEMP       | 46.000     | degrees C  | ok    | na        | na        | na        | 101.000   | 104.000   | na
CPU0_Power       | 54.000     | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 8320.000   | RPM        | ok    | na        | 1120.000  | na        | na        | 39840.000 | na
SYS_FAN_1B       | 7360.000   | RPM        | ok    | na        | 1120.000  | na        | na        | 39840.000 | na
SYS_FAN_2A       | 8160.000   | RPM        | ok    | na        | 1120.000  | na        | na        | 39840.000 | na
SYS_FAN_2B       | 7360.000   | RPM        | ok    | na        | 1120.000  | na        | na        | 39840.000 | na
SYS_FAN_3A       | 8160.000   | RPM        | ok    | na        | 1120.000  | na        | na        | 39840.000 | na
SYS_FAN_3B       | 7200.000   | RPM        | ok    | na        | 1120.000  | na        | na        | 39840.000 | na
SYS_FAN_4A       | 8320.000   | RPM        | ok    | na        | 1120.000  | na        | na        | 39840.000 | na
SYS_FAN_4B       | 7360.000   | RPM        | ok    | na        | 1120.000  | na        | na        | 39840.000 | na
SYS_FAN_5A       | 8160.000   | RPM        | ok    | na        | 1120.000  | na        | na        | 39840.000 | na
SYS_FAN_5B       | 7360.000   | RPM        | ok    | na        | 1120.000  | na        | na        | 39840.000 | na
SYS_FAN_6A       | 8320.000   | RPM        | ok    | na        | 1120.000  | na        | na        | 39840.000 | na
SYS_FAN_6B       | 7200.000   | RPM        | ok    | na        | 1120.000  | na        | na        | 39840.000 | na
SYS_FAN_7A       | 8160.000   | RPM        | ok    | na        | 1120.000  | na        | na        | 39840.000 | na
SYS_FAN_7B       | 7360.000   | RPM        | ok    | na        | 1120.000  | na        | na        | 39840.000 | na
SYS_FAN_8A       | 8160.000   | RPM        | ok    | na        | 1120.000  | na        | na        | 39840.000 | na
SYS_FAN_8B       | 7360.000   | RPM        | ok    | na        | 1120.000  | na        | na        | 39840.000 | na
SYS_FAN_1_PWM    | 19.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_2_PWM    | 19.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_3_PWM    | 19.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_4_PWM    | 19.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_5_PWM    | 19.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_6_PWM    | 19.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_7_PWM    | 19.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_8_PWM    | 19.000     | percent    | ok    | na        | na        | na        | na        | na        | na
CPU_CUPS         | 9.000      | percent    | ok    | na        | na        | na        | na        | 100.000   | na
PSU_0_FAN        | 6400.000   | RPM        | ok    | 800.000   | 1120.000  | na        | na        | na        | na
PSU_1_FAN        | 6240.000   | RPM        | ok    | 800.000   | 1120.000  | na        | na        | na        | na
root@controller-0:~#

```


### MEAKV-518 Redfish Thermals

Validated that all Thermals were showing up in VCMP Tools in MTCE Lab, Below is URL I did screenshots with for record.

Uploaded WEB UI screenshot


### MEAKV-519 Redfish Fans

All fans reporting to metrics sever in vcmp tools instance in the MTCE Lab, screen shot taken of metrics in web ui at this address:

Uploaded WEB UI screenshot

### MEAKV-520_521 Redfish Voltages

All Voltages/Wattages reporting to metrcis server in vcmp tools instance in the MTCE Lab, Screen shot taken of metrics in we ui at this address:

Uploaded WEB UI screenshot

### MEAKV-522 Redfish execution time for 
### /redfish/v1/Systems/Self
### /redfish/v1/Chassis/Self
### //redfish/v1/Chassis/Self/Thermal
### /redfish/v1/Chassis/Self/Power


```log
[XXXXXX@welktxefnce-h-pe1util-vm01 XXXXXX]$ echo $IP
2607:f160:10:80b1:ce:40a:0:e002
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ time curl -sk -u 'XXXXXX:XXXXXX' -X GET https://[$IP]/redfish/v1/Chassis/Self/Power | jq .
{
  "@odata.context": "/redfish/v1/$metadata#Power.Power",
  "@odata.etag": "\"1759427050\"",
  "@odata.id": "/redfish/v1/Chassis/Self/Power",
  "@odata.type": "#Power.v1_7_3.Power",
  "Description": "Power sensor readings",
  "Id": "Power",
  "Name": "Power",
  "PowerControl": [
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/PowerControl/0",
      "MemberId": "0",
      "Name": "DedicatePowerSupplies",
      "PhysicalContext": "SystemBoard",
      "PowerLimit": {
        "CorrectionInMs": 1000,
        "LimitException": "HardPowerOff",
        "LimitInWatts": 500
      },
      "PowerMetrics": {
        "AverageConsumedWatts": 176,
        "IntervalInMin": 15,
        "MaxConsumedWatts": 280
      },
      "RelatedItem@odata.count": 0
    }
  ],
  "PowerControl@odata.count": 1,
  "PowerSupplies": [
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/PowerSupplies/0",
      "FirmwareVersion": "12.43.00",
      "InputRanges": [
        {
          "InputType": "AC",
          "MaximumVoltage": 264,
          "MinimumVoltage": 90,
          "OutputWattage": 850
        }
      ],
      "LastPowerOutputWatts": 80,
      "LineInputVoltage": 213,
      "Manufacturer": "DELTA",
      "MemberId": "0",
      "Model": "DPS-850AB-8 A�",
      "Name": "Power Supply Bay",
      "PowerCapacityWatts": 850,
      "PowerInputWatts": 88,
      "PowerOutputWatts": 84,
      "PowerSupplyType": "AC",
      "SerialNumber": "JQSD2109000265",
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      }
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/PowerSupplies/1",
      "FirmwareVersion": "12.43.00",
      "InputRanges": [
        {
          "InputType": "AC",
          "MaximumVoltage": 264,
          "MinimumVoltage": 90,
          "OutputWattage": 850
        }
      ],
      "LastPowerOutputWatts": 88,
      "LineInputVoltage": 213,
      "Manufacturer": "DELTA",
      "MemberId": "1",
      "Model": "DPS-850AB-8 A�",
      "Name": "Power Supply Bay",
      "PowerCapacityWatts": 850,
      "PowerInputWatts": 92,
      "PowerOutputWatts": 92,
      "PowerSupplyType": "AC",
      "SerialNumber": "JQSD2109000263",
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      }
    }
  ],
  "PowerSupplies@odata.count": 2,
  "Powers": [
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Powers/0",
      "MaxReadingRange": 1020,
      "MemberId": "0",
      "MinReadingRange": 0,
      "Name": "PSU_0_POWER_OUT",
      "ReadingUnits": "Watts",
      "RelatedItem@odata.count": 0,
      "SensorNumber": 51,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "sensor_reading": 84
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Powers/1",
      "MaxReadingRange": 1020,
      "MemberId": "1",
      "MinReadingRange": 0,
      "Name": "PSU_1_POWER_OUT",
      "ReadingUnits": "Watts",
      "RelatedItem@odata.count": 0,
      "SensorNumber": 52,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "sensor_reading": 92
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Powers/2",
      "MaxReadingRange": 16.065,
      "MemberId": "2",
      "MinReadingRange": 0,
      "Name": "PSU_0_CURRENT_IN",
      "ReadingUnits": "Amps",
      "RelatedItem@odata.count": 0,
      "SensorNumber": 53,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "sensor_reading": 0.378
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Powers/3",
      "MaxReadingRange": 16.065,
      "MemberId": "3",
      "MinReadingRange": 0,
      "Name": "PSU_1_CURRENT_IN",
      "ReadingUnits": "Amps",
      "RelatedItem@odata.count": 0,
      "SensorNumber": 54,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "sensor_reading": 0.441
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Powers/4",
      "MaxReadingRange": 1020,
      "MemberId": "4",
      "MinReadingRange": 0,
      "Name": "PSU_POWER_IN",
      "ReadingUnits": "Watts",
      "RelatedItem@odata.count": 0,
      "SensorNumber": 58,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "sensor_reading": 180
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Powers/5",
      "MaxReadingRange": 1020,
      "MemberId": "5",
      "MinReadingRange": 0,
      "Name": "PSU_0_POWER_IN",
      "ReadingUnits": "Watts",
      "RelatedItem@odata.count": 0,
      "SensorNumber": 59,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "sensor_reading": 88
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Powers/6",
      "MaxReadingRange": 1020,
      "MemberId": "6",
      "MinReadingRange": 0,
      "Name": "PSU_1_POWER_IN",
      "ReadingUnits": "Watts",
      "RelatedItem@odata.count": 0,
      "SensorNumber": 60,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "sensor_reading": 92
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Powers/7",
      "MaxReadingRange": 135.15,
      "MemberId": "7",
      "MinReadingRange": 0,
      "Name": "PSU0_CURRENT_OUT",
      "ReadingUnits": "Amps",
      "RelatedItem@odata.count": 0,
      "SensorNumber": 67,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "sensor_reading": 6.89
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Powers/8",
      "MaxReadingRange": 135.15,
      "MemberId": "8",
      "MinReadingRange": 0,
      "Name": "PSU1_CURRENT_OUT",
      "ReadingUnits": "Amps",
      "RelatedItem@odata.count": 0,
      "SensorNumber": 68,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "sensor_reading": 6.89
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Powers/9",
      "MaxReadingRange": 255,
      "MemberId": "9",
      "MinReadingRange": 0,
      "Name": "CPU0_Power",
      "ReadingUnits": "Watts",
      "RelatedItem@odata.count": 0,
      "SensorNumber": 108,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "sensor_reading": 50
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Powers/10",
      "MaxReadingRange": 255,
      "MemberId": "10",
      "MinReadingRange": 0,
      "Name": "FPGA_BOARD_POWER",
      "ReadingUnits": "Watts",
      "RelatedItem@odata.count": 0,
      "SensorNumber": 185,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "sensor_reading": 54
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Powers/11",
      "MaxReadingRange": 255,
      "MemberId": "11",
      "MinReadingRange": 0,
      "Name": "FPGA_CORE_POWER",
      "ReadingUnits": "Watts",
      "RelatedItem@odata.count": 0,
      "SensorNumber": 186,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "sensor_reading": 10
    }
  ],
  "Powers@odata.count": 12,
  "Voltages": [
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Voltages/0",
      "LowerThresholdCritical": 4.7254,
      "MaxReadingRange": 5.989,
      "MemberId": "0",
      "MinReadingRange": 4,
      "Name": "SYS_V5",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "VoltageRegulator",
      "ReadingVolts": 5.1154,
      "RelatedItem@odata.count": 0,
      "SensorNumber": 21,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 5.2246
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Voltages/1",
      "LowerThresholdCritical": 11.3484,
      "MaxReadingRange": 14.394,
      "MemberId": "1",
      "MinReadingRange": 9.6,
      "Name": "SYS_V12",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "VoltageRegulator",
      "ReadingVolts": 12.1004,
      "RelatedItem@odata.count": 0,
      "SensorNumber": 22,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 12.5516
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Voltages/2",
      "LowerThresholdCritical": 3.1043,
      "MaxReadingRange": 3.9305,
      "MemberId": "2",
      "MinReadingRange": 2.63,
      "Name": "SYS_V3.3",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "VoltageRegulator",
      "ReadingVolts": 3.3083,
      "RelatedItem@odata.count": 0,
      "SensorNumber": 23,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 3.4307
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Voltages/3",
      "LowerThresholdCritical": 0.99252,
      "MaxReadingRange": 1.2582,
      "MemberId": "3",
      "MinReadingRange": 0.84,
      "Name": "SYS_V1.05",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "VoltageRegulator",
      "ReadingVolts": 1.06468,
      "RelatedItem@odata.count": 0,
      "SensorNumber": 25,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 1.09748
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Voltages/4",
      "LowerThresholdCritical": 1.6904,
      "MaxReadingRange": 2.144,
      "MemberId": "4",
      "MinReadingRange": 1.43,
      "Name": "CPU_0_Vcore",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "VoltageRegulator",
      "ReadingVolts": 1.7912,
      "RelatedItem@odata.count": 0,
      "SensorNumber": 81,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 1.8696
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Voltages/5",
      "LowerThresholdCritical": 1.1344,
      "MaxReadingRange": 1.6635,
      "MemberId": "5",
      "MinReadingRange": 0.72,
      "Name": "CPU0DDR_ABC_1.2V",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "VoltageRegulator",
      "ReadingVolts": 1.2195,
      "RelatedItem@odata.count": 0,
      "SensorNumber": 89,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 1.2565
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Voltages/6",
      "LowerThresholdCritical": 1.1344,
      "MaxReadingRange": 1.6635,
      "MemberId": "6",
      "MinReadingRange": 0.72,
      "Name": "CPU0DDR_DEF_1.2V",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "VoltageRegulator",
      "ReadingVolts": 1.2195,
      "RelatedItem@odata.count": 0,
      "SensorNumber": 90,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 1.2565
    }
  ],
  "Voltages@odata.count": 7
}

real	0m0.454s
user	0m0.015s
sys	0m0.006s
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$

[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ time curl -sk -u 'XXXXXX:XXXXXX' -X GET https://[$IP]/redfish/v1/Systems/Self | jq .
{
  "@Redfish.Settings": {
    "@odata.type": "#Settings.v1_2_2.Settings",
    "SettingsObject": {
      "@odata.id": "/redfish/v1/Systems/Self/SD"
    }
  },
  "@odata.context": "/redfish/v1/$metadata#ComputerSystem.ComputerSystem",
  "@odata.etag": "\"1761004466\"",
  "@odata.id": "/redfish/v1/Systems/Self",
  "@odata.type": "#ComputerSystem.v1_22_2.ComputerSystem",
  "Actions": {
    "#ComputerSystem.Reset": {
      "@Redfish.ActionInfo": "/redfish/v1/Systems/Self/ResetActionInfo",
      "@Redfish.OperationApplyTimeSupport": {
        "@odata.type": "#Settings.v1_2_2.OperationApplyTimeSupport",
        "MaintenanceWindowDurationInSeconds": 600,
        "MaintenanceWindowResource": {
          "@odata.id": "/redfish/v1/Systems/Self"
        },
        "SupportedValues": [
          "Immediate",
          "AtMaintenanceWindowStart"
        ]
      },
      "ResetType@Redfish.AllowableValues": [
        "ForceOff",
        "ForceRestart",
        "GracefulShutdown",
        "Nmi",
        "On"
      ],
      "target": "/redfish/v1/Systems/Self/Actions/ComputerSystem.Reset"
    }
  },
  "AssetTag": "PA-00338-001207429370007",
  "Bios": {
    "@odata.id": "/redfish/v1/Systems/Self/Bios"
  },
  "BiosVersion": "2.10",
  "Boot": {
    "BootNext": null,
    "BootOptions": {
      "@odata.id": "/redfish/v1/Systems/Self/BootOptions"
    },
    "BootOrder": [
      "Boot0000",
      "Boot0002",
      "Boot0003",
      "Boot0004",
      "Boot0001"
    ],
    "BootOrderPropertySelection": "BootOrder",
    "BootSourceOverrideEnabled": "Disabled",
    "BootSourceOverrideEnabled@Redfish.AllowableValues": [
      "Disabled",
      "Once",
      "Continuous"
    ],
    "BootSourceOverrideMode": "UEFI",
    "BootSourceOverrideMode@Redfish.AllowableValues": [
      "Legacy",
      "UEFI"
    ],
    "BootSourceOverrideTarget": "None",
    "BootSourceOverrideTarget@Redfish.AllowableValues": [
      "None",
      "Pxe",
      "Floppy",
      "Cd",
      "Usb",
      "Hdd",
      "BiosSetup",
      "Utilities",
      "Diags",
      "UefiShell",
      "UefiTarget",
      "SDCard",
      "UefiHttp",
      "RemoteDrive",
      "UefiBootNext"
    ],
    "Certificates": {
      "@odata.id": "/redfish/v1/Systems/Self/Boot/Certificates"
    },
    "UefiTargetBootSourceOverride": null
  },
  "Description": "System Self",
  "EthernetInterfaces": {
    "@odata.id": "/redfish/v1/Systems/Self/EthernetInterfaces"
  },
  "HostName": "welktxef-931883-rz-le0trtn-031",
  "HostingRoles": [
    "ApplicationServer"
  ],
  "Id": "Self",
  "IndicatorLED": "Off",
  "IndicatorLED@Redfish.AllowableValues": [
    "Lit",
    "Blinking",
    "Off"
  ],
  "Links": {
    "Chassis": [
      {
        "@odata.id": "/redfish/v1/Chassis/Self"
      }
    ],
    "Chassis@odata.count": 1,
    "ManagedBy": [
      {
        "@odata.id": "/redfish/v1/Managers/Self"
      }
    ],
    "ManagedBy@odata.count": 1
  },
  "LogServices": {
    "@odata.id": "/redfish/v1/Systems/Self/LogServices"
  },
  "Manufacturer": "ZTSYSTEMS",
  "Memory": {
    "@odata.id": "/redfish/v1/Systems/Self/Memory"
  },
  "MemoryDomains": {
    "@odata.id": "/redfish/v1/Systems/Self/MemoryDomains"
  },
  "MemorySummary": {
    "Metrics": {
      "@odata.id": "/redfish/v1/Systems/Self/MemorySummary/MemoryMetrics"
    },
    "Status": {
      "Health": "OK",
      "State": "Enabled"
    }
  },
  "Model": " ",
  "Name": "Triton",
  "NetworkInterfaces": {
    "@odata.id": "/redfish/v1/Systems/Self/NetworkInterfaces"
  },
  "Oem": {
    "AMI": {
      "@odata.type": "#AMIManagerBoot.v1_0_0.AMIManagerBoot",
      "ManagerBootConfiguration": {
        "ManagerBootMode@Redfish.AllowableValues": [
          "SoftReset",
          "ResetTimeout"
        ]
      }
    },
    "Ami": {
      "@odata.type": "#AMIBIOSInventoryCRC.v1_0_0.AMIBIOSInventoryCRC",
      "Bios": {
        "Inventory": {
          "Crc": {
            "@odata.id": "/redfish/v1/Systems/Self/Oem/Ami/Inventory/Crc",
            "GroupCrcList": [
              {
                "CERTIFICATE": 2126475715
              },
              {
                "CPU": 1899095367
              },
              {
                "PCIE": 3123310707
              },
              {
                "DIMM": 2258498529
              }
            ]
          }
        },
        "RedfishVersion": "1.8.0",
        "RtpVersion": "1.8.0"
      }
    }
  },
  "PCIeDevices": [
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_00"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_08"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_11"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_14"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_16"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_17"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_1C"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_1F"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_02_00"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_03_00"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_64_00"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_65_00"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_66_08"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_66_09"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_66_10"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_66_11"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_67_00"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_68_00"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_69_00"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_6A_00"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_B2_00"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_B2_02"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_B2_03"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_B2_0E"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_B2_0F"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_B2_10"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_B2_12"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_B2_15"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_B2_16"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_B2_17"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_B3_00"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_B4_00"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_B5_00"
    }
  ],
  "PCIeDevices@odata.count": 33,
  "PCIeFunctions": [
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_00/PCIeFunctions/DevType3_DMI0_DevIndex0"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_08/PCIeFunctions/DevType3_DMMY_DevIndex1"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_11/PCIeFunctions/DevType3_MRO0_DevIndex2"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_11/PCIeFunctions/DevType3_SAT2_DevIndex3"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_14/PCIeFunctions/DevType3_TERM_DevIndex5"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_14/PCIeFunctions/DevType3_XHCI_DevIndex4"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_16/PCIeFunctions/DevType3_HEC1_DevIndex6"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_16/PCIeFunctions/DevType3_HEC2_DevIndex7"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_16/PCIeFunctions/DevType3_HEC3_DevIndex8"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_17/PCIeFunctions/DevType3_SAT1_DevIndex9"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_1C/PCIeFunctions/DevType3_RP01_DevIndexA"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_1C/PCIeFunctions/DevType3_RP05_DevIndexB"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_1F/PCIeFunctions/DevType3_LPC0_DevIndexE"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_1F/PCIeFunctions/DevType3_PMC1_DevIndexF"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_1F/PCIeFunctions/DevType3_SMBS_DevIndex10"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_1F/PCIeFunctions/DevType3_SPIC_DevIndex11"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_02_00/PCIeFunctions/DevType3__DevIndexC"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_03_00/PCIeFunctions/DevType3__DevIndexD"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_64_00/PCIeFunctions/DevType3_BR2A_DevIndex12"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_65_00/PCIeFunctions/DevType3_EPCU_DevIndex13"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_66_08/PCIeFunctions/DevType3_DMMY_DevIndex14"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_66_09/PCIeFunctions/DevType3_DMMY_DevIndex17"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_66_10/PCIeFunctions/DevType3_DMMY_DevIndex19"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_66_11/PCIeFunctions/DevType3_DMMY_DevIndex1C"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_67_00/PCIeFunctions/DevType3_DMMY_DevIndex15"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_67_00/PCIeFunctions/DevType3_DMMY_DevIndex16"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_68_00/PCIeFunctions/DevType3_DMMY_DevIndex18"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_69_00/PCIeFunctions/DevType3_DMMY_DevIndex1A"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_69_00/PCIeFunctions/DevType3_DMMY_DevIndex1B"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_6A_00/PCIeFunctions/DevType3_DMMY_DevIndex1D"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_B2_00/PCIeFunctions/DevType3_BR3A_DevIndex1E"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_B2_02/PCIeFunctions/DevType3_BR3C_DevIndex21"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_B2_03/PCIeFunctions/DevType3_BR3D_DevIndex23"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_B2_0E/PCIeFunctions/DevType3_KTI0_DevIndex25"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_B2_0F/PCIeFunctions/DevType3_KTI1_DevIndex26"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_B2_10/PCIeFunctions/DevType3_KTI2_DevIndex27"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_B2_12/PCIeFunctions/DevType3_DMMY_DevIndex29"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_B2_12/PCIeFunctions/DevType3_DMMY_DevIndex2A"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_B2_12/PCIeFunctions/DevType3_DMMY_DevIndex2B"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_B2_12/PCIeFunctions/DevType3_M3K0_DevIndex28"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_B2_15/PCIeFunctions/DevType3_DMMY_DevIndex2C"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_B2_16/PCIeFunctions/DevType3_DMMY_DevIndex2D"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_B2_16/PCIeFunctions/DevType3_DMMY_DevIndex2E"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_B2_17/PCIeFunctions/DevType3_DMMY_DevIndex2F"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_B3_00/PCIeFunctions/DevType3_DMMY_DevIndex1F"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_B3_00/PCIeFunctions/DevType3_DMMY_DevIndex20"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_B4_00/PCIeFunctions/DevType3_DMMY_DevIndex22"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_B5_00/PCIeFunctions/DevType3_DMMY_DevIndex24"
    }
  ],
  "PCIeFunctions@odata.count": 48,
  "PartNumber": "PA-00338-001",
  "PowerRestorePolicy": "AlwaysOn",
  "PowerState": "On",
  "ProcessorSummary": {
    "Count": 1,
    "Model": "Intel(R) Xeon(R) Gold 6212U CPU @ 2.40GHz, 3900 Mhz, 24 Core(s), 48 Logical Processor(s)",
    "Status": {
      "Health": "OK",
      "State": "Enabled"
    }
  },
  "Processors": {
    "@odata.id": "/redfish/v1/Systems/Self/Processors"
  },
  "SKU": "PA-00338-001",
  "SecureBoot": {
    "@odata.id": "/redfish/v1/Systems/Self/SecureBoot"
  },
  "SerialNumber": "207429370007",
  "SimpleStorage": {
    "@odata.id": "/redfish/v1/Systems/Self/SimpleStorage"
  },
  "Status": {
    "Health": "OK",
    "HealthRollup": "OK",
    "State": "Enabled"
  },
  "Storage": {
    "@odata.id": "/redfish/v1/Systems/Self/Storage"
  },
  "SystemType": "Physical",
  "TrustedModules": [
    {
      "FirmwareVersion": "7.63",
      "FirmwareVersion2": "13.6400",
      "InterfaceType": "TPM2_0",
      "InterfaceTypeSelection": "BiosSetting",
      "Status": {
        "State": "Enabled"
      }
    }
  ],
  "UUID": "4344545A-106F-2000-6265-D42066696C6C"
}

real	0m0.526s
user	0m0.015s
sys	0m0.005s
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$

[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ time curl -sk -u 'XXXXXX:XXXXXX' -X GET https://[$IP]/redfish/v1/Chassis/Self | jq .
{
  "@odata.context": "/redfish/v1/$metadata#Chassis.Chassis",
  "@odata.etag": "\"1759427050\"",
  "@odata.id": "/redfish/v1/Chassis/Self",
  "@odata.type": "#Chassis.v1_25_1.Chassis",
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
  "AssetTag": "                        ",
  "ChassisType": "Other",
  "Description": "Chassis Self",
  "EnvironmentMetrics": {
    "@odata.id": "/redfish/v1/Chassis/Self/EnvironmentMetrics"
  },
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
        "@odata.id": "/redfish/v1/Systems/Self/Storage/1/Drives/NVMe_Device6_NSID1"
      },
      {
        "@odata.id": "/redfish/v1/Systems/Self/Storage/1/Drives/NVMe_Device7_NSID1"
      },
      {
        "@odata.id": "/redfish/v1/Systems/Self/Storage/1/Drives/USB_Device0_Port4"
      },
      {
        "@odata.id": "/redfish/v1/Systems/Self/Storage/1/Drives/USB_Device1_Port4"
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
      }
    ],
    "Drives@odata.count": 8,
    "ManagedBy": [
      {
        "@odata.id": "/redfish/v1/Managers/Self"
      }
    ],
    "ManagedBy@odata.count": 1
  },
  "Location": {
    "AltitudeMeters": null,
    "Contacts": [
      {
        "ContactName": null,
        "EmailAddress": null,
        "PhoneNumber": null
      }
    ],
    "Info": ";;;;;;Bay;Front;0;MB;",
    "InfoFormat": "City;Building;Room;Rack;Row;Orientation;LocationType;Reference;LocationOrdinalValue;ServiceLabe;",
    "Latitude": null,
    "Longitude": null,
    "PartLocation": {
      "LocationOrdinalValue": 0,
      "LocationType": "Bay",
      "Orientation": null,
      "Reference": "Front",
      "ServiceLabel": "MB"
    },
    "Placement": {
      "Rack": null,
      "Row": null
    },
    "PostalAddress": {
      "Building": null,
      "City": null,
      "Room": null
    }
  },
  "LogServices": {
    "@odata.id": "/redfish/v1/Chassis/Self/LogServices"
  },
  "Manufacturer": "ZTSYSTEMS",
  "Model": "TRITON IV",
  "Name": "Computer System Chassis",
  "NetworkAdapters": {
    "@odata.id": "/redfish/v1/Chassis/Self/NetworkAdapters"
  },
  "Oem": {
    "PSU_Information": {
      "@odata.type": "#ZTOem_Information.PSU_Information",
      "PSU1": {
        "ID": "DELTA",
        "MODEL": "DPS-850AB-8 A",
        "REVISION": "S2F",
        "SERIAL": "JQSD2109000265"
      },
      "PSU2": {
        "ID": "DELTA",
        "MODEL": "DPS-850AB-8 A",
        "REVISION": "S2F",
        "SERIAL": "JQSD2109000263"
      }
    }
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
  "PowerSubsystem": {
    "@odata.id": "/redfish/v1/Chassis/Self/PowerSubsystem"
  },
  "SKU": "Default string",
  "Sensors": {
    "@odata.id": "/redfish/v1/Chassis/Self/Sensors"
  },
  "SerialNumber": "207429370007",
  "Status": {
    "Health": "OK",
    "HealthRollup": "OK",
    "State": "Enabled"
  },
  "Thermal": {
    "@odata.id": "/redfish/v1/Chassis/Self/Thermal"
  },
  "ThermalSubsystem": {
    "@odata.id": "/redfish/v1/Chassis/Self/ThermalSubsystem"
  }
}

real	0m0.417s
user	0m0.010s
sys	0m0.006s
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$

[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ time curl -sk -u 'XXXXXX:XXXXXX' -X GET https://[$IP]/redfish/v1/Chassis/Self/Thermal | jq .
{
  "@odata.context": "/redfish/v1/$metadata#Thermal.Thermal",
  "@odata.etag": "\"1759427050\"",
  "@odata.id": "/redfish/v1/Chassis/Self/Thermal",
  "@odata.type": "#Thermal.v1_7_3.Thermal",
  "Description": "Thermal sensor readings",
  "Fans": [
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Fans/0",
      "MemberId": "0",
      "Name": "SYS_FAN_1A",
      "PhysicalContext": "Fan",
      "Reading": 23,
      "ReadingUnits": "Percent",
      "SensorNumber": 1,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      }
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Fans/1",
      "MemberId": "1",
      "Name": "SYS_FAN_1B",
      "PhysicalContext": "Fan",
      "Reading": 23,
      "ReadingUnits": "Percent",
      "SensorNumber": 2,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      }
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Fans/2",
      "MemberId": "2",
      "Name": "SYS_FAN_2A",
      "PhysicalContext": "Fan",
      "Reading": 23,
      "ReadingUnits": "Percent",
      "SensorNumber": 3,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      }
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Fans/3",
      "MemberId": "3",
      "Name": "SYS_FAN_2B",
      "PhysicalContext": "Fan",
      "Reading": 23,
      "ReadingUnits": "Percent",
      "SensorNumber": 4,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      }
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Fans/4",
      "MemberId": "4",
      "Name": "SYS_FAN_3A",
      "PhysicalContext": "Fan",
      "Reading": 23,
      "ReadingUnits": "Percent",
      "SensorNumber": 5,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      }
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Fans/5",
      "MemberId": "5",
      "Name": "SYS_FAN_3B",
      "PhysicalContext": "Fan",
      "Reading": 23,
      "ReadingUnits": "Percent",
      "SensorNumber": 6,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      }
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Fans/6",
      "MemberId": "6",
      "Name": "SYS_FAN_4A",
      "PhysicalContext": "Fan",
      "Reading": 23,
      "ReadingUnits": "Percent",
      "SensorNumber": 7,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      }
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Fans/7",
      "MemberId": "7",
      "Name": "SYS_FAN_4B",
      "PhysicalContext": "Fan",
      "Reading": 23,
      "ReadingUnits": "Percent",
      "SensorNumber": 8,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      }
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Fans/8",
      "MemberId": "8",
      "Name": "SYS_FAN_5A",
      "PhysicalContext": "Fan",
      "Reading": 23,
      "ReadingUnits": "Percent",
      "SensorNumber": 9,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      }
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Fans/9",
      "MemberId": "9",
      "Name": "SYS_FAN_5B",
      "PhysicalContext": "Fan",
      "Reading": 23,
      "ReadingUnits": "Percent",
      "SensorNumber": 10,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      }
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Fans/10",
      "MemberId": "10",
      "Name": "SYS_FAN_6A",
      "PhysicalContext": "Fan",
      "Reading": 23,
      "ReadingUnits": "Percent",
      "SensorNumber": 11,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      }
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Fans/11",
      "MemberId": "11",
      "Name": "SYS_FAN_6B",
      "PhysicalContext": "Fan",
      "Reading": 23,
      "ReadingUnits": "Percent",
      "SensorNumber": 12,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      }
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Fans/12",
      "MemberId": "12",
      "Name": "SYS_FAN_7A",
      "PhysicalContext": "Fan",
      "Reading": 23,
      "ReadingUnits": "Percent",
      "SensorNumber": 13,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      }
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Fans/13",
      "MemberId": "13",
      "Name": "SYS_FAN_7B",
      "PhysicalContext": "Fan",
      "Reading": 23,
      "ReadingUnits": "Percent",
      "SensorNumber": 14,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      }
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Fans/14",
      "MemberId": "14",
      "Name": "SYS_FAN_8A",
      "PhysicalContext": "Fan",
      "Reading": 23,
      "ReadingUnits": "Percent",
      "SensorNumber": 15,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      }
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Fans/15",
      "MemberId": "15",
      "Name": "SYS_FAN_8B",
      "PhysicalContext": "Fan",
      "Reading": 23,
      "ReadingUnits": "Percent",
      "SensorNumber": 16,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      }
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Fans/16",
      "LowerThresholdCritical": 1120,
      "LowerThresholdFatal": 800,
      "MaxReadingRange": 40800,
      "MemberId": "16",
      "MinReadingRange": 0,
      "Name": "PSU_0_FAN",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "Fan",
      "Reading": 6400,
      "ReadingUnits": "RPM",
      "RelatedItem@odata.count": 0,
      "SensorNumber": 62,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      }
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Fans/17",
      "LowerThresholdCritical": 1120,
      "LowerThresholdFatal": 800,
      "MaxReadingRange": 40800,
      "MemberId": "17",
      "MinReadingRange": 0,
      "Name": "PSU_1_FAN",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "Fan",
      "Reading": 6240,
      "ReadingUnits": "RPM",
      "RelatedItem@odata.count": 0,
      "SensorNumber": 63,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      }
    }
  ],
  "Id": "Thermal",
  "Name": "Thermal",
  "Temperatures": [
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Temperatures/0",
      "LowerThresholdUser": null,
      "MemberId": "0",
      "Name": "CPU_0_DTS_TEMP",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "Intake",
      "ReadingCelsius": -54,
      "RelatedItem@odata.count": 0,
      "SensorNumber": 101,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdUser": null
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Temperatures/1",
      "LowerThresholdUser": null,
      "MemberId": "1",
      "Name": "CPU_0_MARGIN",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "Intake",
      "ReadingCelsius": 45,
      "RelatedItem@odata.count": 0,
      "SensorNumber": 106,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdUser": null
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Temperatures/2",
      "LowerThresholdUser": null,
      "MemberId": "2",
      "Name": "PSU_0_TEMP_2",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "Intake",
      "ReadingCelsius": 30,
      "RelatedItem@odata.count": 0,
      "SensorNumber": 147,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 92,
      "UpperThresholdFatal": 97,
      "UpperThresholdUser": null
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Temperatures/3",
      "LowerThresholdUser": null,
      "MemberId": "3",
      "Name": "PSU_0_TEMP_1",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "Intake",
      "ReadingCelsius": 23,
      "RelatedItem@odata.count": 0,
      "SensorNumber": 148,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 60,
      "UpperThresholdFatal": 64,
      "UpperThresholdUser": null
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Temperatures/4",
      "LowerThresholdUser": null,
      "MemberId": "4",
      "Name": "PSU_1_TEMP_2",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "Intake",
      "ReadingCelsius": 30,
      "RelatedItem@odata.count": 0,
      "SensorNumber": 150,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 92,
      "UpperThresholdFatal": 97,
      "UpperThresholdUser": null
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Temperatures/5",
      "LowerThresholdUser": null,
      "MemberId": "5",
      "Name": "PSU_1_TEMP_1",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "Intake",
      "ReadingCelsius": 23,
      "RelatedItem@odata.count": 0,
      "SensorNumber": 151,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 60,
      "UpperThresholdFatal": 64,
      "UpperThresholdUser": null
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Temperatures/6",
      "LowerThresholdCritical": 6,
      "LowerThresholdUser": null,
      "MemberId": "6",
      "Name": "CPU_0_DIMM_A0",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "Intake",
      "ReadingCelsius": 31,
      "RelatedItem@odata.count": 0,
      "SensorNumber": 160,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 82,
      "UpperThresholdUser": null
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Temperatures/7",
      "LowerThresholdCritical": 6,
      "LowerThresholdUser": null,
      "MemberId": "7",
      "Name": "CPU_0_DIMM_B0",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "Intake",
      "ReadingCelsius": 30,
      "RelatedItem@odata.count": 0,
      "SensorNumber": 162,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 82,
      "UpperThresholdUser": null
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Temperatures/8",
      "LowerThresholdCritical": 6,
      "LowerThresholdUser": null,
      "MemberId": "8",
      "Name": "CPU_0_DIMM_C0",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "Intake",
      "ReadingCelsius": 30,
      "RelatedItem@odata.count": 0,
      "SensorNumber": 163,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 82,
      "UpperThresholdUser": null
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Temperatures/9",
      "LowerThresholdCritical": 6,
      "LowerThresholdUser": null,
      "MemberId": "9",
      "Name": "CPU_0_DIMM_D0",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "Intake",
      "ReadingCelsius": 35,
      "RelatedItem@odata.count": 0,
      "SensorNumber": 164,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 82,
      "UpperThresholdUser": null
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Temperatures/10",
      "LowerThresholdCritical": 6,
      "LowerThresholdUser": null,
      "MemberId": "10",
      "Name": "CPU_0_DIMM_E0",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "Intake",
      "ReadingCelsius": 34,
      "RelatedItem@odata.count": 0,
      "SensorNumber": 166,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 82,
      "UpperThresholdUser": null
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Temperatures/11",
      "LowerThresholdCritical": 6,
      "LowerThresholdUser": null,
      "MemberId": "11",
      "Name": "CPU_0_DIMM_F0",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "Intake",
      "ReadingCelsius": 35,
      "RelatedItem@odata.count": 0,
      "SensorNumber": 167,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 82,
      "UpperThresholdUser": null
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Temperatures/12",
      "LowerThresholdCritical": 6,
      "LowerThresholdUser": null,
      "MemberId": "12",
      "Name": "MAX_DIMM_TEMP",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "Intake",
      "ReadingCelsius": 35,
      "RelatedItem@odata.count": 0,
      "SensorNumber": 184,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 82,
      "UpperThresholdUser": null
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Temperatures/13",
      "LowerThresholdUser": null,
      "MemberId": "13",
      "Name": "FPGA_BOARD_TEMP",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "Intake",
      "ReadingCelsius": 49,
      "RelatedItem@odata.count": 0,
      "SensorNumber": 187,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 95,
      "UpperThresholdFatal": 99,
      "UpperThresholdNonCritical": 86,
      "UpperThresholdUser": null
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Temperatures/14",
      "LowerThresholdUser": null,
      "MemberId": "14",
      "Name": "FPGA_CORE",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "Intake",
      "ReadingCelsius": 43,
      "RelatedItem@odata.count": 0,
      "SensorNumber": 189,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 95,
      "UpperThresholdFatal": 99,
      "UpperThresholdNonCritical": 86,
      "UpperThresholdUser": null
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Temperatures/15",
      "LowerThresholdCritical": 0,
      "LowerThresholdUser": null,
      "MemberId": "15",
      "Name": "SSD_0_TEMP",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "Intake",
      "ReadingCelsius": 33,
      "RelatedItem@odata.count": 0,
      "SensorNumber": 230,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 70,
      "UpperThresholdFatal": 79,
      "UpperThresholdUser": null
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Temperatures/16",
      "LowerThresholdCritical": 0,
      "LowerThresholdUser": null,
      "MemberId": "16",
      "Name": "SSD_1_TEMP",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "Intake",
      "ReadingCelsius": 34,
      "RelatedItem@odata.count": 0,
      "SensorNumber": 231,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 70,
      "UpperThresholdFatal": 79,
      "UpperThresholdUser": null
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Temperatures/17",
      "LowerThresholdCritical": -6,
      "LowerThresholdUser": null,
      "MemberId": "17",
      "Name": "MLB_INLET_TEMP",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "Intake",
      "ReadingCelsius": 24,
      "RelatedItem@odata.count": 0,
      "SensorNumber": 35,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 59,
      "UpperThresholdFatal": 61,
      "UpperThresholdNonCritical": 50,
      "UpperThresholdUser": null
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Temperatures/18",
      "LowerThresholdUser": null,
      "MemberId": "18",
      "Name": "MLB_AMB_TEMP",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "Intake",
      "ReadingCelsius": 28,
      "RelatedItem@odata.count": 0,
      "SensorNumber": 36,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdUser": null
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Temperatures/19",
      "LowerThresholdUser": null,
      "MemberId": "19",
      "Name": "MLB_OUTLET_TEMP",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "Intake",
      "ReadingCelsius": 33,
      "RelatedItem@odata.count": 0,
      "SensorNumber": 38,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdUser": null
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Temperatures/20",
      "LowerThresholdCritical": 6,
      "LowerThresholdUser": null,
      "MemberId": "20",
      "Name": "SYS_PCH_TEMP",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "Intake",
      "ReadingCelsius": 30,
      "RelatedItem@odata.count": 0,
      "SensorNumber": 48,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 82,
      "UpperThresholdUser": null
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Temperatures/21",
      "LowerThresholdUser": null,
      "MemberId": "21",
      "Name": "CPU_0_TEMP",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "Intake",
      "ReadingCelsius": 36,
      "RelatedItem@odata.count": 0,
      "SensorNumber": 97,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 104,
      "UpperThresholdNonCritical": 101,
      "UpperThresholdUser": null
    }
  ]
}

real	0m1.574s
user	0m0.011s
sys	0m0.009s
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$



[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ time curl -sk -u 'XXXXXX:XXXXXX' -X GET https://[$IP]/redfish/v1/Chassis/Self/Power | jq .
{
  "@odata.context": "/redfish/v1/$metadata#Power.Power",
  "@odata.etag": "\"1759427050\"",
  "@odata.id": "/redfish/v1/Chassis/Self/Power",
  "@odata.type": "#Power.v1_7_3.Power",
  "Description": "Power sensor readings",
  "Id": "Power",
  "Name": "Power",
  "PowerControl": [
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/PowerControl/0",
      "MemberId": "0",
      "Name": "DedicatePowerSupplies",
      "PhysicalContext": "SystemBoard",
      "PowerLimit": {
        "CorrectionInMs": 1000,
        "LimitException": "HardPowerOff",
        "LimitInWatts": 500
      },
      "PowerMetrics": {
        "AverageConsumedWatts": 176,
        "IntervalInMin": 15,
        "MaxConsumedWatts": 280
      },
      "RelatedItem@odata.count": 0
    }
  ],
  "PowerControl@odata.count": 1,
  "PowerSupplies": [
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/PowerSupplies/0",
      "FirmwareVersion": "12.43.00",
      "InputRanges": [
        {
          "InputType": "AC",
          "MaximumVoltage": 264,
          "MinimumVoltage": 90,
          "OutputWattage": 850
        }
      ],
      "LastPowerOutputWatts": 76,
      "LineInputVoltage": 214,
      "Manufacturer": "DELTA",
      "MemberId": "0",
      "Model": "DPS-850AB-8 A�",
      "Name": "Power Supply Bay",
      "PowerCapacityWatts": 850,
      "PowerInputWatts": 84,
      "PowerOutputWatts": 72,
      "PowerSupplyType": "AC",
      "SerialNumber": "JQSD2109000265",
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      }
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/PowerSupplies/1",
      "FirmwareVersion": "12.43.00",
      "InputRanges": [
        {
          "InputType": "AC",
          "MaximumVoltage": 264,
          "MinimumVoltage": 90,
          "OutputWattage": 850
        }
      ],
      "LastPowerOutputWatts": 84,
      "LineInputVoltage": 213,
      "Manufacturer": "DELTA",
      "MemberId": "1",
      "Model": "DPS-850AB-8 A�",
      "Name": "Power Supply Bay",
      "PowerCapacityWatts": 850,
      "PowerInputWatts": 88,
      "PowerOutputWatts": 76,
      "PowerSupplyType": "AC",
      "SerialNumber": "JQSD2109000263",
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      }
    }
  ],
  "PowerSupplies@odata.count": 2,
  "Powers": [
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Powers/0",
      "MaxReadingRange": 1020,
      "MemberId": "0",
      "MinReadingRange": 0,
      "Name": "PSU_0_POWER_OUT",
      "ReadingUnits": "Watts",
      "RelatedItem@odata.count": 0,
      "SensorNumber": 51,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "sensor_reading": 72
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Powers/1",
      "MaxReadingRange": 1020,
      "MemberId": "1",
      "MinReadingRange": 0,
      "Name": "PSU_1_POWER_OUT",
      "ReadingUnits": "Watts",
      "RelatedItem@odata.count": 0,
      "SensorNumber": 52,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "sensor_reading": 76
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Powers/2",
      "MaxReadingRange": 16.065,
      "MemberId": "2",
      "MinReadingRange": 0,
      "Name": "PSU_0_CURRENT_IN",
      "ReadingUnits": "Amps",
      "RelatedItem@odata.count": 0,
      "SensorNumber": 53,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "sensor_reading": 0.378
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Powers/3",
      "MaxReadingRange": 16.065,
      "MemberId": "3",
      "MinReadingRange": 0,
      "Name": "PSU_1_CURRENT_IN",
      "ReadingUnits": "Amps",
      "RelatedItem@odata.count": 0,
      "SensorNumber": 54,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "sensor_reading": 0.441
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Powers/4",
      "MaxReadingRange": 1020,
      "MemberId": "4",
      "MinReadingRange": 0,
      "Name": "PSU_POWER_IN",
      "ReadingUnits": "Watts",
      "RelatedItem@odata.count": 0,
      "SensorNumber": 58,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "sensor_reading": 172
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Powers/5",
      "MaxReadingRange": 1020,
      "MemberId": "5",
      "MinReadingRange": 0,
      "Name": "PSU_0_POWER_IN",
      "ReadingUnits": "Watts",
      "RelatedItem@odata.count": 0,
      "SensorNumber": 59,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "sensor_reading": 84
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Powers/6",
      "MaxReadingRange": 1020,
      "MemberId": "6",
      "MinReadingRange": 0,
      "Name": "PSU_1_POWER_IN",
      "ReadingUnits": "Watts",
      "RelatedItem@odata.count": 0,
      "SensorNumber": 60,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "sensor_reading": 88
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Powers/7",
      "MaxReadingRange": 135.15,
      "MemberId": "7",
      "MinReadingRange": 0,
      "Name": "PSU0_CURRENT_OUT",
      "ReadingUnits": "Amps",
      "RelatedItem@odata.count": 0,
      "SensorNumber": 67,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "sensor_reading": 5.83
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Powers/8",
      "MaxReadingRange": 135.15,
      "MemberId": "8",
      "MinReadingRange": 0,
      "Name": "PSU1_CURRENT_OUT",
      "ReadingUnits": "Amps",
      "RelatedItem@odata.count": 0,
      "SensorNumber": 68,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "sensor_reading": 6.36
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Powers/9",
      "MaxReadingRange": 255,
      "MemberId": "9",
      "MinReadingRange": 0,
      "Name": "CPU0_Power",
      "ReadingUnits": "Watts",
      "RelatedItem@odata.count": 0,
      "SensorNumber": 108,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "sensor_reading": 50
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Powers/10",
      "MaxReadingRange": 255,
      "MemberId": "10",
      "MinReadingRange": 0,
      "Name": "FPGA_BOARD_POWER",
      "ReadingUnits": "Watts",
      "RelatedItem@odata.count": 0,
      "SensorNumber": 185,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "sensor_reading": 54
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Powers/11",
      "MaxReadingRange": 255,
      "MemberId": "11",
      "MinReadingRange": 0,
      "Name": "FPGA_CORE_POWER",
      "ReadingUnits": "Watts",
      "RelatedItem@odata.count": 0,
      "SensorNumber": 186,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "sensor_reading": 11
    }
  ],
  "Powers@odata.count": 12,
  "Voltages": [
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Voltages/0",
      "LowerThresholdCritical": 4.7254,
      "MaxReadingRange": 5.989,
      "MemberId": "0",
      "MinReadingRange": 4,
      "Name": "SYS_V5",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "VoltageRegulator",
      "ReadingVolts": 5.1076,
      "RelatedItem@odata.count": 0,
      "SensorNumber": 21,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 5.2246
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Voltages/1",
      "LowerThresholdCritical": 11.3484,
      "MaxReadingRange": 14.394,
      "MemberId": "1",
      "MinReadingRange": 9.6,
      "Name": "SYS_V12",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "VoltageRegulator",
      "ReadingVolts": 12.1192,
      "RelatedItem@odata.count": 0,
      "SensorNumber": 22,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 12.5516
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Voltages/2",
      "LowerThresholdCritical": 3.1043,
      "MaxReadingRange": 3.9305,
      "MemberId": "2",
      "MinReadingRange": 2.63,
      "Name": "SYS_V3.3",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "VoltageRegulator",
      "ReadingVolts": 3.3032,
      "RelatedItem@odata.count": 0,
      "SensorNumber": 23,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 3.4307
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Voltages/3",
      "LowerThresholdCritical": 0.99252,
      "MaxReadingRange": 1.2582,
      "MemberId": "3",
      "MinReadingRange": 0.84,
      "Name": "SYS_V1.05",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "VoltageRegulator",
      "ReadingVolts": 1.06468,
      "RelatedItem@odata.count": 0,
      "SensorNumber": 25,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 1.09748
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Voltages/4",
      "LowerThresholdCritical": 1.6904,
      "MaxReadingRange": 2.144,
      "MemberId": "4",
      "MinReadingRange": 1.43,
      "Name": "CPU_0_Vcore",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "VoltageRegulator",
      "ReadingVolts": 1.794,
      "RelatedItem@odata.count": 0,
      "SensorNumber": 81,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 1.8696
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Voltages/5",
      "LowerThresholdCritical": 1.1344,
      "MaxReadingRange": 1.6635,
      "MemberId": "5",
      "MinReadingRange": 0.72,
      "Name": "CPU0DDR_ABC_1.2V",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "VoltageRegulator",
      "ReadingVolts": 1.2195,
      "RelatedItem@odata.count": 0,
      "SensorNumber": 89,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 1.2565
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Voltages/6",
      "LowerThresholdCritical": 1.1344,
      "MaxReadingRange": 1.6635,
      "MemberId": "6",
      "MinReadingRange": 0.72,
      "Name": "CPU0DDR_DEF_1.2V",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "VoltageRegulator",
      "ReadingVolts": 1.2195,
      "RelatedItem@odata.count": 0,
      "SensorNumber": 90,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 1.2565
    }
  ],
  "Voltages@odata.count": 7
}

real	0m0.389s
user	0m0.012s
sys	0m0.008s
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$
```
### All Execution times are  under 500ms, all appear normal and in good working order

### Passed


