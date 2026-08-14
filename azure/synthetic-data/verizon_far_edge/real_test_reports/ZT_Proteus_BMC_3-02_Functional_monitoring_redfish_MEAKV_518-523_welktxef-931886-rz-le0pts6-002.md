# ZT Proteus 3.02 BMC BIOS .30
# 10/08/25 James Patchett - MTCE Lab VCPfe
# validation MEAKV-518-523

## welktxef-931883-rz-le0pts6-022  welktxef-d931883-022
BMC:  2607:f160:10:80b1:ce:40a:0:e003
OAM:  2607:f160:10:80b1:ce:40a:0:f403

## Subcloud welktxef-d931886-002 Info
```log
XXXXXX@controller-0:~$ source /etc/platform/openrc
[XXXXXX@controller-0 ~(keystone_admin)]$ system show
+------------------------+--------------------------------------+
| Property               | Value                                |
+------------------------+--------------------------------------+
| contact                | None                                 |
| created_at             | 2025-10-02T15:12:49.946376+00:00     |
| description            | None                                 |
| distributed_cloud_role | subcloud                             |
| https_enabled          | True                                 |
| latitude               | None                                 |
| location               | None                                 |
| longitude              | None                                 |
| name                   | welktxef-d931883-022                 |
| region_name            | d8d2b37d63a843959d79d875d27313bb     |
| sdn_enabled            | False                                |
| security_feature       | spectre_meltdown_v1                  |
| service_project_name   | services                             |
| shared_services        | []                                   |
| software_version       | 24.09                                |
| system_mode            | simplex                              |
| system_type            | All-in-one                           |
| timezone               | UTC                                  |
| updated_at             | 2025-10-02T15:29:50.824361+00:00     |
| uuid                   | afe43e9c-92d6-44bb-a501-f2ca1505c091 |
| vswitch_type           | none                                 |
+------------------------+--------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ system application-list
s+--------------------------+-----------+-------------------------------------------+------------------+----------+-----------+
| application              | version   | manifest name                             | manifest file    | status   | progress  |
+--------------------------+-----------+-------------------------------------------+------------------+----------+-----------+
| cert-manager             | 24.09-79  | cert-manager-fluxcd-manifests             | fluxcd-manifests | applied  | completed |
| dell-storage             | 24.09-26  | dell-storage-fluxcd-manifests             | fluxcd-manifests | uploaded | completed |
| deployment-manager       | 24.09-30  | deployment-manager-fluxcd-manifests       | fluxcd-manifests | applied  | completed |
| metrics-server           | 24.09-59  | metrics-server-fluxcd-manifests           | fluxcd-manifests | applied  | completed |
| nginx-ingress-controller | 24.09-67  | nginx-ingress-controller-fluxcd-manifests | fluxcd-manifests | applied  | completed |
| oidc-auth-apps           | 24.09-66  | oidc-auth-apps-fluxcd-manifests           | fluxcd-manifests | applied  | completed |
| platform-integ-apps      | 24.09-144 | platform-integ-apps-fluxcd-manifests      | fluxcd-manifests | applied  | completed |
| ptp-notification         | 24.09-191 | ptp-notification-fluxcd-manifests         | fluxcd-manifests | applied  | completed |
| rook-ceph                | 24.09-78  | rook-ceph-fluxcd-manifests                | fluxcd-manifests | uploaded | completed |
| sriov-fec-operator       | 24.09-45  | sriov-fec-operator-fluxcd-manifests       | fluxcd-manifests | applied  | completed |
| wr-analytics             | 24.09-1   | wr-analytics-fluxcd-manifests             | fluxcd-manifests | applied  | completed |
+--------------------------+-----------+-------------------------------------------+------------------+----------+-----------+
[XXXXXX@controller-0 ~(keystone_admin)]$ sw-patch query
Patch ID  RR  Release  Patch State
========  ==  =======  ===========

[XXXXXX@controller-0 ~(keystone_admin)]$ software list
+----------------+------+----------+
| Release        | RR   |  State   |
+----------------+------+----------+
| WRCP-24.09.301 | True | deployed |
+----------------+------+----------+
[XXXXXX@controller-0 ~(keystone_admin)]$
```

## Check Sensors before we start load

```log
root@controller-0:/var/home/XXXXXX# ipmitool sensor | grep -e CPU_0_TEMP -e CPU0_Power -e FAN -e CPU_CUPS
CPU_0_TEMP       | 46.000     | degrees C  | ok    | na        | na        | na        | 96.000    | 98.000    | na
CPU0_Power       | 69.000     | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 5125.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1B       | 5500.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_2A       | 5000.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_2B       | 5500.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1A_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1B_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_2A_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_2B_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
CPU_CUPS         | 1.000      | percent    | ok    | na        | na        | na        | na        | 100.000   | na
PSU_1_FAN        | 4000.000   | RPM        | ok    | 800.000   | 1120.000  | na        | na        | na        | na
PSU_2_FAN        | 3840.000   | RPM        | ok    | 800.000   | 1120.000  | na        | na        | na        | na
root@controller-0:/var/home/XXXXXX#

```


### MEAKV-518 Redfish Thermals

Validated that all Thermals were showing up in VCMP Tools in MTCE Lab, Below is URL I did screenshots with for record.

Uploaded screenshots of VCMP tool metrics


### Thermals I copy/pasted from web UI

Uploaded screenshots of VCMP tool metrics

### MEAKV-519 Redfish Fans

All fans reporting to metrics sever in vcmp tools instance in the MTCE Lab, screen shot taken of metrics in web ui at this address:

Uploaded screenshots of VCMP tool metrics

### MEAKV-520_521 Redfish Voltages

All Voltages/Wattages reporting to metrcis server in vcmp tools instance in the MTCE Lab, Screen shot taken of metrics in we ui at this address:

Uploaded screenshots of VCMP tool metrics

### MEAKV-522 Redfish execution time for 
### /redfish/v1/Systems/1
### /redfish/v1/Chassis/1
### /redfish/v1/Chassis/1/Thermal
### /redfish/v1/Chassis/1/Power


```log
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ echo $IP
2607:f160:10:80b1:ce:40a:0:e003
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ time curl -sk -u 'XXXXXX:XXXXXX' -X GET https://[$IP]/redfish/v1/Chassis/Self/Power | jq .
{
  "@odata.context": "/redfish/v1/$metadata#Power.Power",
  "@odata.etag": "\"1758912942\"",
  "@odata.id": "/redfish/v1/Chassis/Self/Power",
  "@odata.type": "#Power.v1_7_3.Power",
  "Description": "Power sensor readings",
  "Id": "Power",
  "Name": "Power",
  "PowerControl": [
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/PowerControl/0",
      "MemberId": "0",
      "Name": "ADM1278",
      "PhysicalContext": "SystemBoard",
      "PowerAllocatedWatts": 156,
      "PowerConsumedWatts": 152,
      "PowerLimit": {
        "CorrectionInMs": 1000,
        "LimitException": "HardPowerOff",
        "LimitInWatts": 500
      },
      "PowerMetrics": {
        "AverageConsumedWatts": 156,
        "IntervalInMin": 15,
        "MaxConsumedWatts": 396
      },
      "PowerRequestedWatts": 396,
      "RelatedItem@odata.count": 0,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      }
    }
  ],
  "PowerControl@odata.count": 1,
  "PowerSupplies": [
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/PowerSupplies/0",
      "FirmwareVersion": "03.02.00",
      "InputRanges": [
        {
          "InputType": "AC",
          "MaximumVoltage": 264,
          "MinimumVoltage": 90,
          "OutputWattage": 1300
        }
      ],
      "LastPowerOutputWatts": 162,
      "LineInputVoltage": 214,
      "Manufacturer": "Liteon Power",
      "MemberId": "0",
      "Model": "PS-2132-12LR   ",
      "Name": "Power Supply Bay",
      "PowerCapacityWatts": 1300,
      "PowerInputWatts": 168,
      "PowerOutputWatts": 144,
      "PowerSupplyType": "AC",
      "SerialNumber": "6C12D01012204D6",
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      }
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/PowerSupplies/1",
      "FirmwareVersion": "03.02.00",
      "InputRanges": [
        {
          "InputType": "AC",
          "MaximumVoltage": 264,
          "MinimumVoltage": 90,
          "OutputWattage": 1300
        }
      ],
      "LastPowerOutputWatts": 150,
      "LineInputVoltage": 214,
      "Manufacturer": "Liteon Power",
      "MemberId": "1",
      "Model": "PS-2132-12LR   ",
      "Name": "Power Supply Bay",
      "PowerCapacityWatts": 1300,
      "PowerInputWatts": 156,
      "PowerOutputWatts": 132,
      "PowerSupplyType": "AC",
      "SerialNumber": "6C12D01012092D9",
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
      "Name": "MB_HSC_PEAK_PIN",
      "ReadingUnits": "Watts",
      "RelatedItem@odata.count": 0,
      "SensorNumber": 33,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "sensor_reading": 396
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Powers/1",
      "MaxReadingRange": 1020,
      "MemberId": "1",
      "MinReadingRange": 0,
      "Name": "MB_HSC_PIN",
      "ReadingUnits": "Watts",
      "RelatedItem@odata.count": 0,
      "SensorNumber": 42,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "sensor_reading": 152
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Powers/2",
      "MaxReadingRange": 1020,
      "MemberId": "2",
      "MinReadingRange": 0,
      "Name": "MB_HSC_PIN_AVG",
      "ReadingUnits": "Watts",
      "RelatedItem@odata.count": 0,
      "SensorNumber": 46,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "sensor_reading": 156
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Powers/3",
      "MaxReadingRange": 1530,
      "MemberId": "3",
      "MinReadingRange": 0,
      "Name": "PSU_1_POWER_OUT",
      "ReadingUnits": "Watts",
      "RelatedItem@odata.count": 0,
      "SensorNumber": 51,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "sensor_reading": 144
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Powers/4",
      "MaxReadingRange": 1530,
      "MemberId": "4",
      "MinReadingRange": 0,
      "Name": "PSU_2_POWER_OUT",
      "ReadingUnits": "Watts",
      "RelatedItem@odata.count": 0,
      "SensorNumber": 52,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "sensor_reading": 132
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Powers/5",
      "MaxReadingRange": 16.065,
      "MemberId": "5",
      "MinReadingRange": 0,
      "Name": "PSU_1_CURRENT_IN",
      "ReadingUnits": "Amps",
      "RelatedItem@odata.count": 0,
      "SensorNumber": 53,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "sensor_reading": 0.819
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Powers/6",
      "MaxReadingRange": 16.065,
      "MemberId": "6",
      "MinReadingRange": 0,
      "Name": "PSU_2_CURRENT_IN",
      "ReadingUnits": "Amps",
      "RelatedItem@odata.count": 0,
      "SensorNumber": 54,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "sensor_reading": 0.756
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Powers/7",
      "MaxReadingRange": 2805,
      "MemberId": "7",
      "MinReadingRange": 0,
      "Name": "PSU_POWER_IN",
      "ReadingUnits": "Watts",
      "RelatedItem@odata.count": 0,
      "SensorNumber": 58,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "sensor_reading": 319
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Powers/8",
      "MaxReadingRange": 1530,
      "MemberId": "8",
      "MinReadingRange": 0,
      "Name": "PSU_1_POWER_IN",
      "ReadingUnits": "Watts",
      "RelatedItem@odata.count": 0,
      "SensorNumber": 59,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "sensor_reading": 168
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Powers/9",
      "MaxReadingRange": 1530,
      "MemberId": "9",
      "MinReadingRange": 0,
      "Name": "PSU_2_POWER_IN",
      "ReadingUnits": "Watts",
      "RelatedItem@odata.count": 0,
      "SensorNumber": 60,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "sensor_reading": 156
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Powers/10",
      "MaxReadingRange": 135.15,
      "MemberId": "10",
      "MinReadingRange": 0,
      "Name": "PSU1_CURRENT_OUT",
      "ReadingUnits": "Amps",
      "RelatedItem@odata.count": 0,
      "SensorNumber": 67,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "sensor_reading": 12.19
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Powers/11",
      "MaxReadingRange": 135.15,
      "MemberId": "11",
      "MinReadingRange": 0,
      "Name": "PSU2_CURRENT_OUT",
      "ReadingUnits": "Amps",
      "RelatedItem@odata.count": 0,
      "SensorNumber": 68,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "sensor_reading": 12.19
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Powers/12",
      "MaxReadingRange": 255,
      "MemberId": "12",
      "MinReadingRange": 0,
      "Name": "CPU0_Power",
      "ReadingUnits": "Watts",
      "RelatedItem@odata.count": 0,
      "SensorNumber": 108,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "sensor_reading": 78
    }
  ],
  "Powers@odata.count": 13,
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
      "ReadingVolts": 5.0608,
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
      "ReadingVolts": 12.2696,
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
      "ReadingVolts": 3.3338,
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
      "ReadingVolts": 1.05484,
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
      "LowerThresholdCritical": 2.289,
      "MaxReadingRange": 3.885,
      "MemberId": "4",
      "MinReadingRange": 2.1,
      "Name": "RTC_Voltage",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "VoltageRegulator",
      "ReadingVolts": 2.891,
      "RelatedItem@odata.count": 0,
      "SensorNumber": 26,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 3.444
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Voltages/5",
      "LowerThresholdCritical": 1.6904,
      "MaxReadingRange": 2.144,
      "MemberId": "5",
      "MinReadingRange": 1.43,
      "Name": "CPU_0_Vcore",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "VoltageRegulator",
      "ReadingVolts": 1.8192,
      "RelatedItem@odata.count": 0,
      "SensorNumber": 81,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 1.8696
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Voltages/6",
      "LowerThresholdCritical": 1.1344,
      "MaxReadingRange": 1.6635,
      "MemberId": "6",
      "MinReadingRange": 0.72,
      "Name": "CPU0DDR_ABC_1.2V",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "VoltageRegulator",
      "ReadingVolts": 1.2306,
      "RelatedItem@odata.count": 0,
      "SensorNumber": 89,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 1.2565
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Voltages/7",
      "LowerThresholdCritical": 1.1344,
      "MaxReadingRange": 1.6635,
      "MemberId": "7",
      "MinReadingRange": 0.72,
      "Name": "CPU0DDR_DEF_1.2V",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "VoltageRegulator",
      "ReadingVolts": 1.2269,
      "RelatedItem@odata.count": 0,
      "SensorNumber": 90,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 1.2565
    }
  ],
  "Voltages@odata.count": 8
}

real	0m0.675s
user	0m0.013s
sys	0m0.007s
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
  "@odata.etag": "\"1761004200\"",
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
  "AssetTag": "PA-00371-00320743160N006",
  "Bios": {
    "@odata.id": "/redfish/v1/Systems/Self/Bios"
  },
  "BiosVersion": "0.30",
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
      "Boot0005",
      "Boot0006",
      "Boot0007",
      "Boot0008",
      "Boot0009",
      "Boot000A"
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
  "HostName": "welktxef-931856-rz-le0pts6-004",
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
    },
    "TotalSystemMemoryGiB": 128
  },
  "Model": " ",
  "Name": "Proteus I",
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
                "CPU": 3411699333
              },
              {
                "PCIE": 2526898645
              },
              {
                "DIMM": 3743970904
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
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_02"
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
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_17_00"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_17_02"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_17_04"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_18_00"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_1A_00"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_50_00"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_50_02"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_51_00"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_89_00"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_C2_00"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_C2_02"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_C2_03"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_C3_00"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_C4_00"
    }
  ],
  "PCIeDevices@odata.count": 24,
  "PCIeFunctions": [
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_00/PCIeFunctions/DevType3_DMMY_DevIndexB"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_02/PCIeFunctions/DevType3_NRP0_DevIndexC"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_11/PCIeFunctions/DevType3_MRO0_DevIndexD"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_11/PCIeFunctions/DevType3_SAT2_DevIndexE"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_14/PCIeFunctions/DevType3_TERM_DevIndex10"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_14/PCIeFunctions/DevType3_XHCI_DevIndexF"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_16/PCIeFunctions/DevType3_HEC1_DevIndex11"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_16/PCIeFunctions/DevType3_HEC2_DevIndex12"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_16/PCIeFunctions/DevType3_HEC3_DevIndex13"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_17/PCIeFunctions/DevType3_SAT1_DevIndex14"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_1C/PCIeFunctions/DevType3_RP01_DevIndex15"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_1C/PCIeFunctions/DevType3_RP05_DevIndex16"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_1C/PCIeFunctions/DevType3_RP06_DevIndex19"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_1F/PCIeFunctions/DevType3_LPC0_DevIndex1A"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_1F/PCIeFunctions/DevType3_PMC1_DevIndex1B"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_1F/PCIeFunctions/DevType3_SMBS_DevIndex1C"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_1F/PCIeFunctions/DevType3_SPIC_DevIndex1D"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_02_00/PCIeFunctions/DevType3_VB00_DevIndex17"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_03_00/PCIeFunctions/DevType3_OVDL_DevIndex18"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_17_00/PCIeFunctions/DevType3_DMMY_DevIndex1E"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_17_02/PCIeFunctions/DevType3_BR1A_DevIndex1F"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_17_04/PCIeFunctions/DevType3_BR1C_DevIndex20"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_18_00/PCIeFunctions/DevType3_SL01_DevIndex0"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_18_00/PCIeFunctions/DevType3_SL01_DevIndex1"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_18_00/PCIeFunctions/DevType3_SL01_DevIndex2"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_18_00/PCIeFunctions/DevType3_SL01_DevIndex3"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_1A_00/PCIeFunctions/DevType3_SL02_DevIndex4"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_1A_00/PCIeFunctions/DevType3_SL02_DevIndex5"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_1A_00/PCIeFunctions/DevType3_SL02_DevIndex6"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_1A_00/PCIeFunctions/DevType3_SL02_DevIndex7"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_50_00/PCIeFunctions/DevType3_DMMY_DevIndex21"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_50_02/PCIeFunctions/DevType3_BR2A_DevIndex22"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_51_00/PCIeFunctions/DevType3_SL03_DevIndex8"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_89_00/PCIeFunctions/DevType3_DMMY_DevIndex23"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_C2_00/PCIeFunctions/DevType3_DMMY_DevIndex24"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_C2_02/PCIeFunctions/DevType3_BR5A_DevIndex25"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_C2_03/PCIeFunctions/DevType3_BR5B_DevIndex26"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_C3_00/PCIeFunctions/DevType3_SL05_DevIndex9"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_C4_00/PCIeFunctions/DevType3_SL06_DevIndexA"
    }
  ],
  "PCIeFunctions@odata.count": 39,
  "PartNumber": "PA-00371-003",
  "PowerRestorePolicy": "AlwaysOn",
  "PowerState": "On",
  "ProcessorSummary": {
    "Count": 1,
    "Model": "Intel(R) Xeon(R) Gold 6338N CPU @ 2.20GHz, 3500 Mhz, 32 Core(s), 64 Logical Processor(s)",
    "Status": {
      "Health": "OK",
      "State": "Enabled"
    }
  },
  "Processors": {
    "@odata.id": "/redfish/v1/Systems/Self/Processors"
  },
  "SKU": "PA-00371-003",
  "SecureBoot": {
    "@odata.id": "/redfish/v1/Systems/Self/SecureBoot"
  },
  "SerialNumber": "20743160N006",
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
  "UUID": "4344545A-1041-3100-3350-D04B31363236"
}

real	0m0.588s
user	0m0.014s
sys	0m0.005s
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$

[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ time curl -sk -u 'XXXXXX:XXXXXX' -X GET https://[$IP]/redfish/v1/Chassis/Self | jq .
{
  "@odata.context": "/redfish/v1/$metadata#Chassis.Chassis",
  "@odata.etag": "\"1744898842\"",
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
    "AltitudeMeters": null,
    "Contacts": [
      {
        "ContactName": null,
        "EmailAddress": null,
        "PhoneNumber": null
      }
    ],
    "Info": ";;;;;LeftToRight;Slot;Front;0;SLED1;",
    "InfoFormat": "City;Building;Room;Rack;Row;Orientation;LocationType;Reference;LocationOrdinalValue;ServiceLabe;",
    "Latitude": null,
    "Longitude": null,
    "PartLocation": {
      "LocationOrdinalValue": 0,
      "LocationType": "Slot",
      "Orientation": "LeftToRight",
      "Reference": "Front",
      "ServiceLabel": "SLED1"
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
  "Model": "Proteus I_Mix",
  "Name": "Computer System Chassis",
  "NetworkAdapters": {
    "@odata.id": "/redfish/v1/Chassis/Self/NetworkAdapters"
  },
  "Oem": {
    "PSU_Information": {
      "@odata.type": "#ZTOem_Information.PSU_Information",
      "PSU1": {
        "ID": "Liteon Power",
        "MODEL": "PS-2132-12LR   ",
        "REVISION": "01 ",
        "SERIAL": "6C12D01012204D6"
      },
      "PSU2": {
        "ID": "Liteon Power",
        "MODEL": "PS-2132-12LR   ",
        "REVISION": "01 ",
        "SERIAL": "6C12D01012092D9"
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
  "SerialNumber": "207431600003",
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

real	0m0.277s
user	0m0.014s
sys	0m0.006s
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$

[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ time curl -sk -u 'XXXXXX:XXXXXX' -X GET https://[$IP]/redfish/v1/Chassis/Self/Thermal | jq .
{
  "@odata.context": "/redfish/v1/$metadata#Thermal.Thermal",
  "@odata.etag": "\"1758912942\"",
  "@odata.id": "/redfish/v1/Chassis/Self/Thermal",
  "@odata.type": "#Thermal.v1_7_3.Thermal",
  "Description": "Thermal sensor readings",
  "Fans": [
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Fans/0",
      "MemberId": "0",
      "Name": "SYS_FAN_1A",
      "PhysicalContext": "Fan",
      "Reading": 18,
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
      "Reading": 18,
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
      "Reading": 18,
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
      "Reading": 18,
      "ReadingUnits": "Percent",
      "SensorNumber": 4,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      }
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Fans/4",
      "LowerThresholdCritical": 1120,
      "LowerThresholdFatal": 800,
      "MaxReadingRange": 40800,
      "MemberId": "4",
      "MinReadingRange": 0,
      "Name": "PSU_1_FAN",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "Fan",
      "Reading": 4000,
      "ReadingUnits": "RPM",
      "RelatedItem@odata.count": 0,
      "SensorNumber": 62,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      }
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Fans/5",
      "LowerThresholdCritical": 1120,
      "LowerThresholdFatal": 800,
      "MaxReadingRange": 40800,
      "MemberId": "5",
      "MinReadingRange": 0,
      "Name": "PSU_2_FAN",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "Fan",
      "Reading": 4000,
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
      "ReadingCelsius": -46,
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
      "ReadingCelsius": 39,
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
      "Name": "PSU_1_TEMP_2",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "Intake",
      "ReadingCelsius": 44,
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
      "Name": "PSU_1_TEMP_1",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "Intake",
      "ReadingCelsius": 26,
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
      "Name": "PSU_2_TEMP_2",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "Intake",
      "ReadingCelsius": 43,
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
      "Name": "PSU_2_TEMP_1",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "Intake",
      "ReadingCelsius": 26,
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
      "Name": "CPU_0_DIMM_C0",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "Intake",
      "ReadingCelsius": 37,
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
      "SensorNumber": 161,
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
      "Name": "CPU_0_DIMM_A0",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "Intake",
      "ReadingCelsius": 34,
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
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Temperatures/9",
      "LowerThresholdCritical": 6,
      "LowerThresholdUser": null,
      "MemberId": "9",
      "Name": "CPU_0_DIMM_B0",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "Intake",
      "ReadingCelsius": 34,
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
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Temperatures/10",
      "LowerThresholdCritical": 6,
      "LowerThresholdUser": null,
      "MemberId": "10",
      "Name": "CPU_0_DIMM_G0",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "Intake",
      "ReadingCelsius": 36,
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
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Temperatures/11",
      "LowerThresholdCritical": 6,
      "LowerThresholdUser": null,
      "MemberId": "11",
      "Name": "CPU_0_DIMM_H0",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "Intake",
      "ReadingCelsius": 36,
      "RelatedItem@odata.count": 0,
      "SensorNumber": 165,
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
      "Name": "CPU_0_DIMM_E0",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "Intake",
      "ReadingCelsius": 35,
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
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Temperatures/13",
      "LowerThresholdCritical": 6,
      "LowerThresholdUser": null,
      "MemberId": "13",
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
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Temperatures/14",
      "LowerThresholdCritical": 6,
      "LowerThresholdUser": null,
      "MemberId": "14",
      "Name": "DIMM_VRABCD_TEMP",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "Intake",
      "ReadingCelsius": 34,
      "RelatedItem@odata.count": 0,
      "SensorNumber": 168,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 125,
      "UpperThresholdUser": null
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Temperatures/15",
      "LowerThresholdCritical": 6,
      "LowerThresholdUser": null,
      "MemberId": "15",
      "Name": "DIMM_VREFGH_TEMP",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "Intake",
      "ReadingCelsius": 31,
      "RelatedItem@odata.count": 0,
      "SensorNumber": 169,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 125,
      "UpperThresholdUser": null
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Temperatures/16",
      "LowerThresholdCritical": 6,
      "LowerThresholdUser": null,
      "MemberId": "16",
      "Name": "MAX_DIMM_TEMP",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "Intake",
      "ReadingCelsius": 37,
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
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Temperatures/17",
      "LowerThresholdUser": null,
      "MemberId": "17",
      "Name": "PML_WEST_TEMP",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "Intake",
      "ReadingCelsius": 56,
      "RelatedItem@odata.count": 0,
      "SensorNumber": 208,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 110,
      "UpperThresholdFatal": 114,
      "UpperThresholdUser": null
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Temperatures/18",
      "LowerThresholdUser": null,
      "MemberId": "18",
      "Name": "PML_LOCAL_TEMP",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "Intake",
      "ReadingCelsius": 55,
      "RelatedItem@odata.count": 0,
      "SensorNumber": 209,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 85,
      "UpperThresholdNonCritical": 80,
      "UpperThresholdUser": null
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Temperatures/19",
      "LowerThresholdUser": null,
      "MemberId": "19",
      "Name": "PML_VDD_TEMP",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "Intake",
      "ReadingCelsius": 62,
      "RelatedItem@odata.count": 0,
      "SensorNumber": 210,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 125,
      "UpperThresholdUser": null
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Temperatures/20",
      "LowerThresholdUser": null,
      "MemberId": "20",
      "Name": "PML_EAST_TEMP",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "Intake",
      "ReadingCelsius": 57,
      "RelatedItem@odata.count": 0,
      "SensorNumber": 211,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 110,
      "UpperThresholdFatal": 114,
      "UpperThresholdUser": null
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Temperatures/21",
      "LowerThresholdCritical": 0,
      "LowerThresholdNonCritical": 5,
      "LowerThresholdUser": null,
      "MemberId": "21",
      "Name": "SC_1_E810",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "Intake",
      "ReadingCelsius": 41,
      "RelatedItem@odata.count": 0,
      "SensorNumber": 216,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 105,
      "UpperThresholdFatal": 115,
      "UpperThresholdNonCritical": 100,
      "UpperThresholdUser": null
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Temperatures/22",
      "LowerThresholdCritical": 0,
      "LowerThresholdNonCritical": 5,
      "LowerThresholdUser": null,
      "MemberId": "22",
      "Name": "SC_2_E810",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "Intake",
      "ReadingCelsius": 38,
      "RelatedItem@odata.count": 0,
      "SensorNumber": 217,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 105,
      "UpperThresholdFatal": 115,
      "UpperThresholdNonCritical": 100,
      "UpperThresholdUser": null
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Temperatures/23",
      "LowerThresholdCritical": 0,
      "LowerThresholdUser": null,
      "MemberId": "23",
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
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Temperatures/24",
      "LowerThresholdCritical": 0,
      "LowerThresholdUser": null,
      "MemberId": "24",
      "Name": "SSD_1_TEMP",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "Intake",
      "ReadingCelsius": 35,
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
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Temperatures/25",
      "LowerThresholdCritical": -6,
      "LowerThresholdUser": null,
      "MemberId": "25",
      "Name": "INLET_TEMP_L",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "Intake",
      "ReadingCelsius": 25,
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
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Temperatures/26",
      "LowerThresholdCritical": -6,
      "LowerThresholdUser": null,
      "MemberId": "26",
      "Name": "INLET_TEMP_R",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "Intake",
      "ReadingCelsius": 23,
      "RelatedItem@odata.count": 0,
      "SensorNumber": 36,
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
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Temperatures/27",
      "LowerThresholdCritical": 6,
      "LowerThresholdUser": null,
      "MemberId": "27",
      "Name": "MB_HSC_TEMP",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "Intake",
      "ReadingCelsius": 36,
      "RelatedItem@odata.count": 0,
      "SensorNumber": 37,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 125,
      "UpperThresholdUser": null
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Temperatures/28",
      "LowerThresholdUser": null,
      "MemberId": "28",
      "Name": "OUTLET_TEMP_L",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "Intake",
      "ReadingCelsius": 38,
      "RelatedItem@odata.count": 0,
      "SensorNumber": 38,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdUser": null
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Temperatures/29",
      "LowerThresholdUser": null,
      "MemberId": "29",
      "Name": "OUTLET_TEMP_R",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "Intake",
      "ReadingCelsius": 37,
      "RelatedItem@odata.count": 0,
      "SensorNumber": 39,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdUser": null
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Temperatures/30",
      "LowerThresholdCritical": -6,
      "LowerThresholdUser": null,
      "MemberId": "30",
      "Name": "INLET_TEMP_MAX",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "Intake",
      "ReadingCelsius": 25,
      "RelatedItem@odata.count": 0,
      "SensorNumber": 40,
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
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Temperatures/31",
      "LowerThresholdUser": null,
      "MemberId": "31",
      "Name": "OUTLET_TEMP_MAX",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "Intake",
      "ReadingCelsius": 38,
      "RelatedItem@odata.count": 0,
      "SensorNumber": 41,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdUser": null
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Temperatures/32",
      "LowerThresholdCritical": 5,
      "LowerThresholdUser": null,
      "MemberId": "32",
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
      "@odata.id": "/redfish/v1/Chassis/Self/Thermal#/Temperatures/33",
      "LowerThresholdUser": null,
      "MemberId": "33",
      "Name": "CPU_0_TEMP",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "Intake",
      "ReadingCelsius": 52,
      "RelatedItem@odata.count": 0,
      "SensorNumber": 97,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 98,
      "UpperThresholdNonCritical": 96,
      "UpperThresholdUser": null
    }
  ]
}

real	0m0.804s
user	0m0.012s
sys	0m0.007s
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$



[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ time curl -sk -u 'XXXXXX:XXXXXX' -X GET https://[$IP]/redfish/v1/Chassis/Self/Power | jq .
{
  "@odata.context": "/redfish/v1/$metadata#Power.Power",
  "@odata.etag": "\"1758912942\"",
  "@odata.id": "/redfish/v1/Chassis/Self/Power",
  "@odata.type": "#Power.v1_7_3.Power",
  "Description": "Power sensor readings",
  "Id": "Power",
  "Name": "Power",
  "PowerControl": [
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/PowerControl/0",
      "MemberId": "0",
      "Name": "ADM1278",
      "PhysicalContext": "SystemBoard",
      "PowerAllocatedWatts": 156,
      "PowerConsumedWatts": 164,
      "PowerLimit": {
        "CorrectionInMs": 1000,
        "LimitException": "HardPowerOff",
        "LimitInWatts": 500
      },
      "PowerMetrics": {
        "AverageConsumedWatts": 156,
        "IntervalInMin": 15,
        "MaxConsumedWatts": 396
      },
      "PowerRequestedWatts": 396,
      "RelatedItem@odata.count": 0,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      }
    }
  ],
  "PowerControl@odata.count": 1,
  "PowerSupplies": [
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/PowerSupplies/0",
      "FirmwareVersion": "03.02.00",
      "InputRanges": [
        {
          "InputType": "AC",
          "MaximumVoltage": 264,
          "MinimumVoltage": 90,
          "OutputWattage": 1300
        }
      ],
      "LastPowerOutputWatts": 144,
      "LineInputVoltage": 214,
      "Manufacturer": "Liteon Power",
      "MemberId": "0",
      "Model": "PS-2132-12LR   ",
      "Name": "Power Supply Bay",
      "PowerCapacityWatts": 1300,
      "PowerInputWatts": 174,
      "PowerOutputWatts": 162,
      "PowerSupplyType": "AC",
      "SerialNumber": "6C12D01012204D6",
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      }
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/PowerSupplies/1",
      "FirmwareVersion": "03.02.00",
      "InputRanges": [
        {
          "InputType": "AC",
          "MaximumVoltage": 264,
          "MinimumVoltage": 90,
          "OutputWattage": 1300
        }
      ],
      "LastPowerOutputWatts": 132,
      "LineInputVoltage": 214,
      "Manufacturer": "Liteon Power",
      "MemberId": "1",
      "Model": "PS-2132-12LR   ",
      "Name": "Power Supply Bay",
      "PowerCapacityWatts": 1300,
      "PowerInputWatts": 162,
      "PowerOutputWatts": 144,
      "PowerSupplyType": "AC",
      "SerialNumber": "6C12D01012092D9",
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
      "Name": "MB_HSC_PEAK_PIN",
      "ReadingUnits": "Watts",
      "RelatedItem@odata.count": 0,
      "SensorNumber": 33,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "sensor_reading": 396
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Powers/1",
      "MaxReadingRange": 1020,
      "MemberId": "1",
      "MinReadingRange": 0,
      "Name": "MB_HSC_PIN",
      "ReadingUnits": "Watts",
      "RelatedItem@odata.count": 0,
      "SensorNumber": 42,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "sensor_reading": 164
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Powers/2",
      "MaxReadingRange": 1020,
      "MemberId": "2",
      "MinReadingRange": 0,
      "Name": "MB_HSC_PIN_AVG",
      "ReadingUnits": "Watts",
      "RelatedItem@odata.count": 0,
      "SensorNumber": 46,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "sensor_reading": 156
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Powers/3",
      "MaxReadingRange": 1530,
      "MemberId": "3",
      "MinReadingRange": 0,
      "Name": "PSU_1_POWER_OUT",
      "ReadingUnits": "Watts",
      "RelatedItem@odata.count": 0,
      "SensorNumber": 51,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "sensor_reading": 162
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Powers/4",
      "MaxReadingRange": 1530,
      "MemberId": "4",
      "MinReadingRange": 0,
      "Name": "PSU_2_POWER_OUT",
      "ReadingUnits": "Watts",
      "RelatedItem@odata.count": 0,
      "SensorNumber": 52,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "sensor_reading": 144
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Powers/5",
      "MaxReadingRange": 16.065,
      "MemberId": "5",
      "MinReadingRange": 0,
      "Name": "PSU_1_CURRENT_IN",
      "ReadingUnits": "Amps",
      "RelatedItem@odata.count": 0,
      "SensorNumber": 53,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "sensor_reading": 0.819
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Powers/6",
      "MaxReadingRange": 16.065,
      "MemberId": "6",
      "MinReadingRange": 0,
      "Name": "PSU_2_CURRENT_IN",
      "ReadingUnits": "Amps",
      "RelatedItem@odata.count": 0,
      "SensorNumber": 54,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "sensor_reading": 0.756
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Powers/7",
      "MaxReadingRange": 2805,
      "MemberId": "7",
      "MinReadingRange": 0,
      "Name": "PSU_POWER_IN",
      "ReadingUnits": "Watts",
      "RelatedItem@odata.count": 0,
      "SensorNumber": 58,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "sensor_reading": 330
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Powers/8",
      "MaxReadingRange": 1530,
      "MemberId": "8",
      "MinReadingRange": 0,
      "Name": "PSU_1_POWER_IN",
      "ReadingUnits": "Watts",
      "RelatedItem@odata.count": 0,
      "SensorNumber": 59,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "sensor_reading": 174
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Powers/9",
      "MaxReadingRange": 1530,
      "MemberId": "9",
      "MinReadingRange": 0,
      "Name": "PSU_2_POWER_IN",
      "ReadingUnits": "Watts",
      "RelatedItem@odata.count": 0,
      "SensorNumber": 60,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "sensor_reading": 162
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Powers/10",
      "MaxReadingRange": 135.15,
      "MemberId": "10",
      "MinReadingRange": 0,
      "Name": "PSU1_CURRENT_OUT",
      "ReadingUnits": "Amps",
      "RelatedItem@odata.count": 0,
      "SensorNumber": 67,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "sensor_reading": 13.25
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Powers/11",
      "MaxReadingRange": 135.15,
      "MemberId": "11",
      "MinReadingRange": 0,
      "Name": "PSU2_CURRENT_OUT",
      "ReadingUnits": "Amps",
      "RelatedItem@odata.count": 0,
      "SensorNumber": 68,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "sensor_reading": 12.19
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Powers/12",
      "MaxReadingRange": 255,
      "MemberId": "12",
      "MinReadingRange": 0,
      "Name": "CPU0_Power",
      "ReadingUnits": "Watts",
      "RelatedItem@odata.count": 0,
      "SensorNumber": 108,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "sensor_reading": 76
    }
  ],
  "Powers@odata.count": 13,
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
      "ReadingVolts": 5.0608,
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
      "ReadingVolts": 12.2884,
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
      "ReadingVolts": 3.3338,
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
      "ReadingVolts": 1.05648,
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
      "LowerThresholdCritical": 2.289,
      "MaxReadingRange": 3.885,
      "MemberId": "4",
      "MinReadingRange": 2.1,
      "Name": "RTC_Voltage",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "VoltageRegulator",
      "ReadingVolts": 2.891,
      "RelatedItem@odata.count": 0,
      "SensorNumber": 26,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 3.444
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Voltages/5",
      "LowerThresholdCritical": 1.6904,
      "MaxReadingRange": 2.144,
      "MemberId": "5",
      "MinReadingRange": 1.43,
      "Name": "CPU_0_Vcore",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "VoltageRegulator",
      "ReadingVolts": 1.822,
      "RelatedItem@odata.count": 0,
      "SensorNumber": 81,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 1.8696
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Voltages/6",
      "LowerThresholdCritical": 1.1344,
      "MaxReadingRange": 1.6635,
      "MemberId": "6",
      "MinReadingRange": 0.72,
      "Name": "CPU0DDR_ABC_1.2V",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "VoltageRegulator",
      "ReadingVolts": 1.2306,
      "RelatedItem@odata.count": 0,
      "SensorNumber": 89,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 1.2565
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/Power#/Voltages/7",
      "LowerThresholdCritical": 1.1344,
      "MaxReadingRange": 1.6635,
      "MemberId": "7",
      "MinReadingRange": 0.72,
      "Name": "CPU0DDR_DEF_1.2V",
      "Oem": {
        "Ami": {
          "@odata.type": "#AMIChassisPowerThermal.AMIChassisPowerThermal",
          "OwnerLUN": 0
        }
      },
      "PhysicalContext": "VoltageRegulator",
      "ReadingVolts": 1.2306,
      "RelatedItem@odata.count": 0,
      "SensorNumber": 90,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 1.2565
    }
  ],
  "Voltages@odata.count": 8
}

real	0m0.977s
user	0m0.013s
sys	0m0.008s
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$

```
### All Execution times are  under 500ms, all appear normal and in good working order

### Passed


