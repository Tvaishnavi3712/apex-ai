# HPE ILO6 1.60 BIOS H11 v1.11
# HPE Sapphire Rapids E930t server
# 6/28/24 James Patchett - MTCE Lab VCPfe
# validation MEAKV-518-523


## welktxsr-931883-rh-le093s6-001
## welktxsr-d931883-001
ILO:  2607:f160:10:80b1:ce:40a:0:e002
OAM:  2607:f160:10:80b1:ce:40a:0:f402

### MEAKV-518 Redfish Thermals

Validated that all Thermals were showing up in VCMP Tools in MTCE Lab, Below is URL I did screenshots with for record.

https://vcp-rchlab-performance.mon.vzwops.com/grafana/explore?panes=%7B%22Z0U%22:%7B%22datasource%22:%22c6ea65a8-9025-4968-b9e5-00f851753940%22,%22queries%22:%5B%7B%22refId%22:%22A%22,%22expr%22:%22redfish_chassis_temperature_celsius%7Binstance%3D%5C%222607:f160:10:80b1:ce:40a:0:e002%5C%22%7D%22,%22range%22:true,%22instant%22:true,%22datasource%22:%7B%22type%22:%22prometheus%22,%22uid%22:%22c6ea65a8-9025-4968-b9e5-00f851753940%22%7D,%22editorMode%22:%22builder%22,%22legendFormat%22:%22__auto%22,%22useBackend%22:false,%22disableTextWrap%22:false,%22fullMetaSearch%22:false,%22includeNullMetadata%22:true%7D%5D,%22range%22:%7B%22from%22:%22now-15m%22,%22to%22:%22now%22%7D%7D%7D&schemaVersion=1&orgId=1

### Thermals I copy/pasted from web UI
```txt
redfish_chassis_temperature_celsius{chassis_id="1", datacenter="westlake", dc="westlake", host="redfishagent-victoria-metrics-agent-0", hostname="welktxsr-d29991563801-rh-le093s6-001", instance="2607:f160:10:80b1:ce:40a:0:e002", job="redfish-exporter", resource="temperature", sensor="01-Inlet Ambient", sensor_id="0"}
32

redfish_chassis_temperature_celsius{chassis_id="1", datacenter="westlake", dc="westlake", host="redfishagent-victoria-metrics-agent-0", hostname="welktxsr-d29991563801-rh-le093s6-001", instance="2607:f160:10:80b1:ce:40a:0:e002", job="redfish-exporter", resource="temperature", sensor="02-CPU 1 PkgTmp", sensor_id="1"}
61

redfish_chassis_temperature_celsius{chassis_id="1", datacenter="westlake", dc="westlake", host="redfishagent-victoria-metrics-agent-0", hostname="welktxsr-d29991563801-rh-le093s6-001", instance="2607:f160:10:80b1:ce:40a:0:e002", job="redfish-exporter", resource="temperature", sensor="03-P1 DIMM 1-6", sensor_id="2"}
41

redfish_chassis_temperature_celsius{chassis_id="1", datacenter="westlake", dc="westlake", host="redfishagent-victoria-metrics-agent-0", hostname="welktxsr-d29991563801-rh-le093s6-001", instance="2607:f160:10:80b1:ce:40a:0:e002", job="redfish-exporter", resource="temperature", sensor="04-P1 PMM 1-6", sensor_id="3"}
0

redfish_chassis_temperature_celsius{chassis_id="1", datacenter="westlake", dc="westlake", host="redfishagent-victoria-metrics-agent-0", hostname="welktxsr-d29991563801-rh-le093s6-001", instance="2607:f160:10:80b1:ce:40a:0:e002", job="redfish-exporter", resource="temperature", sensor="05-P1 DIMM 7-12", sensor_id="4"}
50

redfish_chassis_temperature_celsius{chassis_id="1", datacenter="westlake", dc="westlake", host="redfishagent-victoria-metrics-agent-0", hostname="welktxsr-d29991563801-rh-le093s6-001", instance="2607:f160:10:80b1:ce:40a:0:e002", job="redfish-exporter", resource="temperature", sensor="06-P1 PMM 7-12", sensor_id="5"}
0

redfish_chassis_temperature_celsius{chassis_id="1", datacenter="westlake", dc="westlake", host="redfishagent-victoria-metrics-agent-0", hostname="welktxsr-d29991563801-rh-le093s6-001", instance="2607:f160:10:80b1:ce:40a:0:e002", job="redfish-exporter", resource="temperature", sensor="07-VR P1", sensor_id="6"}
56

redfish_chassis_temperature_celsius{chassis_id="1", datacenter="westlake", dc="westlake", host="redfishagent-victoria-metrics-agent-0", hostname="welktxsr-d29991563801-rh-le093s6-001", instance="2607:f160:10:80b1:ce:40a:0:e002", job="redfish-exporter", resource="temperature", sensor="08-Chipset", sensor_id="7"}
47

redfish_chassis_temperature_celsius{chassis_id="1", datacenter="westlake", dc="westlake", host="redfishagent-victoria-metrics-agent-0", hostname="welktxsr-d29991563801-rh-le093s6-001", instance="2607:f160:10:80b1:ce:40a:0:e002", job="redfish-exporter", resource="temperature", sensor="09-BMC", sensor_id="8"}
54

redfish_chassis_temperature_celsius{chassis_id="1", datacenter="westlake", dc="westlake", host="redfishagent-victoria-metrics-agent-0", hostname="welktxsr-d29991563801-rh-le093s6-001", instance="2607:f160:10:80b1:ce:40a:0:e002", job="redfish-exporter", resource="temperature", sensor="10-M2", sensor_id="9"}
40

redfish_chassis_temperature_celsius{chassis_id="1", datacenter="westlake", dc="westlake", host="redfishagent-victoria-metrics-agent-0", hostname="welktxsr-d29991563801-rh-le093s6-001", instance="2607:f160:10:80b1:ce:40a:0:e002", job="redfish-exporter", resource="temperature", sensor="15.1-PCI 1-Network controller", sensor_id="16"}
66

redfish_chassis_temperature_celsius{chassis_id="1", datacenter="westlake", dc="westlake", host="redfishagent-victoria-metrics-agent-0", hostname="welktxsr-d29991563801-rh-le093s6-001", instance="2607:f160:10:80b1:ce:40a:0:e002", job="redfish-exporter", resource="temperature", sensor="15.2-PCI 1-SFP28 (SFF-8402)", sensor_id="17"}
40

redfish_chassis_temperature_celsius{chassis_id="1", datacenter="westlake", dc="westlake", host="redfishagent-victoria-metrics-agent-0", hostname="welktxsr-d29991563801-rh-le093s6-001", instance="2607:f160:10:80b1:ce:40a:0:e002", job="redfish-exporter", resource="temperature", sensor="15.3-PCI 1-SFP28 (SFF-8402)", sensor_id="18"}
36

redfish_chassis_temperature_celsius{chassis_id="1", datacenter="westlake", dc="westlake", host="redfishagent-victoria-metrics-agent-0", hostname="welktxsr-d29991563801-rh-le093s6-001", instance="2607:f160:10:80b1:ce:40a:0:e002", job="redfish-exporter", resource="temperature", sensor="15.4-PCI 1-SFP28 (SFF-8402)", sensor_id="19"}
37

redfish_chassis_temperature_celsius{chassis_id="1", datacenter="westlake", dc="westlake", host="redfishagent-victoria-metrics-agent-0", hostname="welktxsr-d29991563801-rh-le093s6-001", instance="2607:f160:10:80b1:ce:40a:0:e002", job="redfish-exporter", resource="temperature", sensor="15.5-PCI 1-SFP28 (SFF-8402)", sensor_id="20"}
37

redfish_chassis_temperature_celsius{chassis_id="1", datacenter="westlake", dc="westlake", host="redfishagent-victoria-metrics-agent-0", hostname="welktxsr-d29991563801-rh-le093s6-001", instance="2607:f160:10:80b1:ce:40a:0:e002", job="redfish-exporter", resource="temperature", sensor="16-PCI 1 Zone", sensor_id="10"}
32

redfish_chassis_temperature_celsius{chassis_id="1", datacenter="westlake", dc="westlake", host="redfishagent-victoria-metrics-agent-0", hostname="welktxsr-d29991563801-rh-le093s6-001", instance="2607:f160:10:80b1:ce:40a:0:e002", job="redfish-exporter", resource="temperature", sensor="17.1-PCI 2-Network controller", sensor_id="21"}
69

redfish_chassis_temperature_celsius{chassis_id="1", datacenter="westlake", dc="westlake", host="redfishagent-victoria-metrics-agent-0", hostname="welktxsr-d29991563801-rh-le093s6-001", instance="2607:f160:10:80b1:ce:40a:0:e002", job="redfish-exporter", resource="temperature", sensor="17.2-PCI 2-SFP28 (SFF-8402)", sensor_id="22"}
31

redfish_chassis_temperature_celsius{chassis_id="1", datacenter="westlake", dc="westlake", host="redfishagent-victoria-metrics-agent-0", hostname="welktxsr-d29991563801-rh-le093s6-001", instance="2607:f160:10:80b1:ce:40a:0:e002", job="redfish-exporter", resource="temperature", sensor="17.3-PCI 2-SFP28 (SFF-8402)", sensor_id="23"}
33
```


### MEAKV-519 Redfish Fans

All fans reporting to metrics sever in vcmp tools instance in the MTCE Lab, screen shot taken of metrics in web ui at this address:

https://vcp-rchlab-performance.mon.vzwops.com/grafana/explore?panes=%7B%22Z0U%22:%7B%22datasource%22:%22c6ea65a8-9025-4968-b9e5-00f851753940%22,%22queries%22:%5B%7B%22refId%22:%22A%22,%22expr%22:%22redfish_chassis_fan_rpm_percentage%7Binstance%3D%5C%222607:f160:10:80b1:ce:40a:0:e002%5C%22%7D%22,%22range%22:true,%22instant%22:true,%22datasource%22:%7B%22type%22:%22prometheus%22,%22uid%22:%22c6ea65a8-9025-4968-b9e5-00f851753940%22%7D,%22editorMode%22:%22builder%22,%22legendFormat%22:%22__auto%22,%22useBackend%22:false,%22disableTextWrap%22:false,%22fullMetaSearch%22:false,%22includeNullMetadata%22:true%7D%5D,%22range%22:%7B%22from%22:%22now-3h%22,%22to%22:%22now%22%7D%7D%7D&schemaVersion=1&orgId=1

### MEAKV-520_521 Redfish Voltages

All Voltages/Wattages reporting to metrcis server in vcmp tools instance in the MTCE Lab, Screen shot taken of metrics in we ui at this address:

https://vcp-rchlab-performance.mon.vzwops.com/grafana/explore?panes=%7B%22Z0U%22:%7B%22datasource%22:%22c6ea65a8-9025-4968-b9e5-00f851753940%22,%22queries%22:%5B%7B%22refId%22:%22A%22,%22expr%22:%22redfish_chassis_power_powersupply_line_input_voltage%7Binstance%3D%5C%222607:f160:10:80b1:ce:40a:0:e002%5C%22%7D%22,%22range%22:true,%22instant%22:true,%22datasource%22:%7B%22type%22:%22prometheus%22,%22uid%22:%22c6ea65a8-9025-4968-b9e5-00f851753940%22%7D,%22editorMode%22:%22builder%22,%22legendFormat%22:%22__auto%22,%22useBackend%22:false,%22disableTextWrap%22:false,%22fullMetaSearch%22:false,%22includeNullMetadata%22:true%7D%5D,%22range%22:%7B%22from%22:%22now-3h%22,%22to%22:%22now%22%7D%7D%7D&schemaVersion=1&orgId=1

### MEAKV-522 Redfish execution time for 
### /redfish/v1/Systems/1
### /redfish/v1/Chassis/1
### /redfish/v1/Chassis/1/Thermal
### /redfish/v1/Chassis/1/Power


```log
[XXXXXX@welktxefnce-h-pe1util-vm01 XXXXXX]$ echo $IP
2607:f160:10:80b1:ce:40a:0:e002
(hpe_fw) [XXXXXX@welktxefnce-h-pe1util-vm01 XXXXXX]$ time curl -sk -u 'XXXXXX:XXXXXX' -X GET https://[$IP]/redfish/v1/chassis/1/Power | jq .
{
  "@odata.context": "/redfish/v1/$metadata#Power.Power",
  "@odata.etag": "W/\"353D990A\"",
  "@odata.id": "/redfish/v1/Chassis/1/Power",
  "@odata.type": "#Power.v1_7_1.Power",
  "Id": "Power",
  "Name": "PowerMetrics",
  "Oem": {
    "Hpe": {
      "@odata.context": "/redfish/v1/$metadata#HpePowerMetricsExt.HpePowerMetricsExt",
      "@odata.type": "#HpePowerMetricsExt.v2_5_1.HpePowerMetricsExt",
      "BrownoutRecoveryEnabled": true,
      "HasCpuPowerMetering": true,
      "HasDimmPowerMetering": true,
      "HasGpuPowerMetering": false,
      "HasPowerMetering": true,
      "HighEfficiencyMode": "Balanced",
      "Links": {
        "PowerMeter": {
          "@odata.id": "/redfish/v1/Chassis/1/Power/PowerMeter"
        },
        "FastPowerMeter": {
          "@odata.id": "/redfish/v1/Chassis/1/Power/FastPowerMeter"
        },
        "SlowPowerMeter": {
          "@odata.id": "/redfish/v1/Chassis/1/Power/SlowPowerMeter"
        },
        "FederatedGroupCapping": {
          "@odata.id": "/redfish/v1/Chassis/1/Power/FederatedGroupCapping"
        }
      },
      "MinimumSafelyAchievableCap": null,
      "MinimumSafelyAchievableCapValid": false,
      "PowerMetric": {
        "AmbTemp": 32,
        "Cap": 0,
        "CpuCapLim": 100,
        "CpuMax": 0,
        "CpuPwrSavLim": 100,
        "CpuWatts": 71,
        "DimmWatts": 13,
        "GpuWatts": 0,
        "PrMode": "osc",
        "PunCap": false,
        "UnachCap": false
      },
      "SNMPPowerThresholdAlert": {
        "DurationInMin": 0,
        "ThresholdWatts": 0,
        "Trigger": "Disabled"
      }
    }
  },
  "PowerControl": [
    {
      "@odata.id": "/redfish/v1/Chassis/1/Power#PowerControl/0",
      "MemberId": "0",
      "PowerCapacityWatts": 3000,
      "PowerConsumedWatts": 132,
      "PowerMetrics": {
        "AverageConsumedWatts": 131,
        "IntervalInMin": 20,
        "MaxConsumedWatts": 178,
        "MinConsumedWatts": 130
      }
    }
  ],
  "PowerSupplies": [
    {
      "@odata.id": "/redfish/v1/Chassis/1/Power#PowerSupplies/0",
      "FirmwareVersion": "1.01",
      "LastPowerOutputWatts": 132,
      "LineInputVoltage": 212,
      "LineInputVoltageType": "Unknown",
      "Manufacturer": null,
      "MemberId": "0",
      "Model": "P11298-001 ",
      "Name": "HpeServerPowerSupply",
      "Oem": {
        "Hpe": {
          "@odata.context": "/redfish/v1/$metadata#HpeServerPowerSupply.HpeServerPowerSupply",
          "@odata.type": "#HpeServerPowerSupply.v2_0_0.HpeServerPowerSupply",
          "AveragePowerOutputWatts": 132,
          "BayNumber": 1,
          "Domain": "System",
          "HotplugCapable": true,
          "MaxPowerOutputWatts": 167,
          "Mismatched": false,
          "PowerSupplyStatus": {
            "State": "Ok"
          },
          "iPDUCapable": false
        }
      },
      "PowerCapacityWatts": 1500,
      "PowerSupplyType": "AC",
      "SerialNumber": "6W2317RB00AZ",
      "SparePartNumber": "P11771-001",
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      }
    },
    {
      "@odata.id": "/redfish/v1/Chassis/1/Power#PowerSupplies/1",
      "FirmwareVersion": "1.01",
      "LastPowerOutputWatts": 132,
      "LineInputVoltage": 213,
      "LineInputVoltageType": "Unknown",
      "Manufacturer": null,
      "MemberId": "1",
      "Model": "P11298-001 ",
      "Name": "HpeServerPowerSupply",
      "Oem": {
        "Hpe": {
          "@odata.context": "/redfish/v1/$metadata#HpeServerPowerSupply.HpeServerPowerSupply",
          "@odata.type": "#HpeServerPowerSupply.v2_0_0.HpeServerPowerSupply",
          "AveragePowerOutputWatts": 132,
          "BayNumber": 2,
          "Domain": "System",
          "HotplugCapable": true,
          "MaxPowerOutputWatts": 167,
          "Mismatched": false,
          "PowerSupplyStatus": {
            "State": "Ok"
          },
          "iPDUCapable": false
        }
      },
      "PowerCapacityWatts": 1500,
      "PowerSupplyType": "AC",
      "SerialNumber": "6W2317RB00DS",
      "SparePartNumber": "P11771-001",
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      }
    }
  ]
}

real	0m0.573s
user	0m0.011s
sys	0m0.007s
(hpe_fw) [XXXXXX@welktxefnce-h-pe1util-vm01 XXXXXX]$ 

(hpe_fw) [XXXXXX@welktxefnce-h-pe1util-vm01 XXXXXX]$ time curl -sk -u 'XXXXXX:XXXXXX' -X GET https://[$IP]/redfish/v1/Systems/1/ | jq .
{
  "@odata.context": "/redfish/v1/$metadata#ComputerSystem.ComputerSystem",
  "@odata.etag": "W/\"08E8F1C7\"",
  "@odata.id": "/redfish/v1/Systems/1/",
  "@odata.type": "#ComputerSystem.v1_17_0.ComputerSystem",
  "Id": "1",
  "Actions": {
    "#ComputerSystem.Reset": {
      "ResetType@Redfish.AllowableValues": [
        "On",
        "ForceOff",
        "GracefulShutdown",
        "ForceRestart",
        "Nmi",
        "PushPowerButton",
        "GracefulRestart"
      ],
      "target": "/redfish/v1/Systems/1/Actions/ComputerSystem.Reset/"
    }
  },
  "AssetTag": "",
  "Bios": {
    "@odata.id": "/redfish/v1/systems/1/bios/"
  },
  "BiosVersion": "H11 v1.11 (03/07/2024)",
  "Boot": {
    "BootOptions": {
      "@odata.id": "/redfish/v1/Systems/1/BootOptions/"
    },
    "BootOrder": [
      "Boot0022",
      "Boot000E",
      "Boot0011",
      "Boot0013",
      "Boot0012",
      "Boot0014",
      "Boot0019",
      "Boot001B",
      "Boot0015",
      "Boot0017",
      "Boot001D",
      "Boot001E",
      "Boot0020",
      "Boot001A",
      "Boot001F",
      "Boot001C",
      "Boot0018",
      "Boot0016",
      "Boot000F",
      "Boot0010"
    ],
    "BootSourceOverrideEnabled": "Disabled",
    "BootSourceOverrideMode": "UEFI",
    "BootSourceOverrideTarget": "None",
    "BootSourceOverrideTarget@Redfish.AllowableValues": [
      "None",
      "Cd",
      "Hdd",
      "Usb",
      "SDCard",
      "Utilities",
      "Diags",
      "BiosSetup",
      "Pxe",
      "UefiShell",
      "UefiHttp",
      "UefiTarget"
    ],
    "UefiTargetBootSourceOverride": "None",
    "UefiTargetBootSourceOverride@Redfish.AllowableValues": [
      "HD(2,GPT,146F7031-A456-4840-B7BE-9F1AB0A1A351,0x3A98800,0x96000)/\\EFI\\BOOT\\bootx64.efi",
      "UsbClass(0xFFFF,0xFFFF,0xFF,0xFF,0xFF)",
      "PciRoot(0x0)/Pci(0xF,0x0)/Pci(0x0,0x0)/MAC(5CED8CEFADF4,0x1)/IPv4(0.0.0.0)/Uri()",
      "PciRoot(0x0)/Pci(0xF,0x0)/Pci(0x0,0x0)/MAC(5CED8CEFADF4,0x1)/IPv4(0.0.0.0)",
      "PciRoot(0x0)/Pci(0xF,0x0)/Pci(0x0,0x0)/MAC(5CED8CEFADF4,0x1)/IPv6(0000:0000:0000:0000:0000:0000:0000:0000)/Uri()",
      "PciRoot(0x0)/Pci(0xF,0x0)/Pci(0x0,0x0)/MAC(5CED8CEFADF4,0x1)/IPv6(0000:0000:0000:0000:0000:0000:0000:0000)",
      "PciRoot(0x2)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B9143AD4,0x1)/IPv4(0.0.0.0)/Uri()",
      "PciRoot(0x2)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B9143AD4,0x1)/IPv4(0.0.0.0)",
      "PciRoot(0x1)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B9143BD0,0x1)/IPv4(0.0.0.0)/Uri()",
      "PciRoot(0x1)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B9143BD0,0x1)/IPv4(0.0.0.0)",
      "PciRoot(0x5)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B9143AB4,0x1)/IPv4(0.0.0.0)/Uri()",
      "PciRoot(0x5)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B9143AB4,0x1)/IPv6(0000:0000:0000:0000:0000:0000:0000:0000)/Uri()",
      "PciRoot(0x5)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B9143AB4,0x1)/IPv6(0000:0000:0000:0000:0000:0000:0000:0000)",
      "PciRoot(0x2)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B9143AD4,0x1)/IPv6(0000:0000:0000:0000:0000:0000:0000:0000)/Uri()",
      "PciRoot(0x5)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B9143AB4,0x1)/IPv4(0.0.0.0)",
      "PciRoot(0x2)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B9143AD4,0x1)/IPv6(0000:0000:0000:0000:0000:0000:0000:0000)",
      "PciRoot(0x1)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B9143BD0,0x1)/IPv6(0000:0000:0000:0000:0000:0000:0000:0000)",
      "PciRoot(0x1)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B9143BD0,0x1)/IPv6(0000:0000:0000:0000:0000:0000:0000:0000)/Uri()",
      "PciRoot(0x0)/Pci(0x10,0x0)/Pci(0x0,0x0)/NVMe(0x1,00-00-00-00-00-00-00-00)",
      "PciRoot(0x0)/Pci(0x11,0x0)/Pci(0x0,0x0)/NVMe(0x1,00-00-00-00-00-00-00-00)"
    ]
  },
  "EthernetInterfaces": {
    "@odata.id": "/redfish/v1/Systems/1/EthernetInterfaces/"
  },
  "HostName": "welktxsr-d29991563801-rh-le093s6-001",
  "Links": {
    "ManagedBy": [
      {
        "@odata.id": "/redfish/v1/Managers/1/"
      }
    ],
    "Chassis": [
      {
        "@odata.id": "/redfish/v1/Chassis/1/"
      }
    ]
  },
  "LocationIndicatorActive": false,
  "LogServices": {
    "@odata.id": "/redfish/v1/Systems/1/LogServices/"
  },
  "Manufacturer": "HPE",
  "Memory": {
    "@odata.id": "/redfish/v1/Systems/1/Memory/"
  },
  "MemoryDomains": {
    "@odata.id": "/redfish/v1/Systems/1/MemoryDomains/"
  },
  "MemorySummary": {
    "Status": {
      "HealthRollup": "OK"
    },
    "TotalSystemMemoryGiB": 256,
    "TotalSystemPersistentMemoryGiB": 0
  },
  "Model": "Edgeline e930t",
  "Name": "Computer System",
  "NetworkInterfaces": {
    "@odata.id": "/redfish/v1/Systems/1/NetworkInterfaces/"
  },
  "Oem": {
    "Hpe": {
      "@odata.context": "/redfish/v1/$metadata#HpeComputerSystemExt.HpeComputerSystemExt",
      "@odata.type": "#HpeComputerSystemExt.v2_14_0.HpeComputerSystemExt",
      "Actions": {
        "#HpeComputerSystemExt.PowerButton": {
          "PushType@Redfish.AllowableValues": [
            "Press",
            "PressAndHold"
          ],
          "target": "/redfish/v1/Systems/1/Actions/Oem/Hpe/HpeComputerSystemExt.PowerButton/"
        },
        "#HpeComputerSystemExt.RestoreManufacturingDefaults": {
          "target": "/redfish/v1/Systems/1/Actions/Oem/Hpe/HpeComputerSystemExt.RestoreManufacturingDefaults/"
        },
        "#HpeComputerSystemExt.RestoreSystemDefaults": {
          "target": "/redfish/v1/Systems/1/Actions/Oem/Hpe/HpeComputerSystemExt.RestoreSystemDefaults/"
        },
        "#HpeComputerSystemExt.SecureSystemErase": {
          "target": "/redfish/v1/Systems/1/Actions/Oem/Hpe/HpeComputerSystemExt.SecureSystemErase/"
        },
        "#HpeComputerSystemExt.ServerIntelligentDiagnosticsMode": {
          "target": "/redfish/v1/Systems/1/Actions/Oem/Hpe/HpeComputerSystemExt.ServerIntelligentDiagnosticsMode/"
        },
        "#HpeComputerSystemExt.ServerSafeMode": {
          "target": "/redfish/v1/Systems/1/Actions/Oem/Hpe/HpeComputerSystemExt.ServerSafeMode/"
        },
        "#HpeComputerSystemExt.SystemReset": {
          "ResetType@Redfish.AllowableValues": [
            "ColdBoot",
            "AuxCycle"
          ],
          "target": "/redfish/v1/Systems/1/Actions/Oem/Hpe/HpeComputerSystemExt.SystemReset/"
        }
      },
      "AggregateHealthStatus": {
        "AgentlessManagementService": "Unavailable",
        "AggregateServerHealth": "OK",
        "BiosOrHardwareHealth": {
          "Status": {
            "Health": "OK"
          }
        },
        "FanRedundancy": "Redundant",
        "Fans": {
          "Status": {
            "Health": "OK"
          }
        },
        "Memory": {
          "Status": {
            "Health": "OK"
          }
        },
        "Network": {
          "Status": {
            "Health": "OK"
          }
        },
        "PowerSupplies": {
          "PowerSuppliesMismatch": false,
          "Status": {
            "Health": "OK"
          }
        },
        "Processors": {
          "Status": {
            "Health": "OK"
          }
        },
        "Storage": {
          "Status": {
            "Health": "OK"
          }
        },
        "Temperatures": {
          "Status": {
            "Health": "OK"
          }
        }
      },
      "Bios": {
        "Backup": {
          "Date": "03/07/2024",
          "Family": "H11",
          "VersionString": "H11 v1.11 (03/07/2024)"
        },
        "Current": {
          "Date": "03/07/2024",
          "Family": "H11",
          "VersionString": "H11 v1.11 (03/07/2024)"
        },
        "UefiClass": 3
      },
      "CriticalTempRemainOff": true,
      "CurrentPowerOnTimeSeconds": 19680,
      "DeviceDiscoveryComplete": {
        "AMSDeviceDiscovery": "NoAMS",
        "DeviceDiscovery": "vMainDeviceDiscoveryComplete"
      },
      "ElapsedEraseTimeInMinutes": 0,
      "EndOfPostDelaySeconds": 0,
      "EstimatedEraseTimeInMinutes": 0,
      "IndicatorLED": "Off",
      "IntelligentProvisioningAlwaysOn": true,
      "IntelligentProvisioningIndex": 7,
      "IntelligentProvisioningLocation": "System Board",
      "IntelligentProvisioningVersion": "4.31.5",
      "IsColdBooting": false,
      "Links": {
        "PCISlots": {
          "@odata.id": "/redfish/v1/Systems/1/PCISlots/"
        },
        "USBPorts": {
          "@odata.id": "/redfish/v1/Systems/1/USBPorts/"
        },
        "USBDevices": {
          "@odata.id": "/redfish/v1/Systems/1/USBDevices/"
        },
        "EthernetInterfaces": {
          "@odata.id": "/redfish/v1/Systems/1/EthernetInterfaces/"
        },
        "WorkloadPerformanceAdvisor": {
          "@odata.id": "/redfish/v1/Systems/1/WorkloadPerformanceAdvisor/"
        },
        "SecureEraseReportService": {
          "@odata.id": "/redfish/v1/Systems/1/SecureEraseReportService/"
        },
        "PCIDevices": [
          {
            "@odata.id": "/redfish/v1/Systems/1/PCIDevices/"
          }
        ]
      },
      "PCAPartNumber": "P48462-E02",
      "PCASerialNumber": "PYHRC0ALMIY02V",
      "PostDiscoveryCompleteTimeStamp": "2024-06-28T17:27:01Z",
      "PostDiscoveryMode": "Auto",
      "PostMode": "Normal",
      "PostState": "FinishedPost",
      "PowerAutoOn": "Restore",
      "PowerOnDelay": "Minimum",
      "PowerOnMinutes": 16818,
      "PowerRegulatorMode": "OSControl",
      "PowerRegulatorModesSupported": [
        "OSControl",
        "Dynamic",
        "Max",
        "Min"
      ],
      "SMBIOS": {
        "extref": "/smbios"
      },
      "ServerFQDN": "welktxsr-d29991563801-rh-le093s6-001.faredge.vzwops.com",
      "ServerIntelligentDiagnosticsModeEnabled": false,
      "ServerSafeModeEnabled": false,
      "SystemROMAndiLOEraseComponentStatus": {
        "BIOSSettingsEraseStatus": "Idle",
        "iLOSettingsEraseStatus": "Idle"
      },
      "SystemROMAndiLOEraseStatus": "Idle",
      "SystemUsage": {
        "AvgCPU0Freq": 50,
        "CPU0Power": 73,
        "CPUICUtil": 0,
        "CPUUtil": 2,
        "IOBusUtil": 0,
        "JitterCount": 0,
        "MemoryBusUtil": 0
      },
      "UserDataEraseComponentStatus": {},
      "UserDataEraseStatus": "Idle",
      "VirtualProfile": "Inactive"
    }
  },
  "PowerState": "On",
  "ProcessorSummary": {
    "Count": 1,
    "Model": "Intel(R) Xeon(R) Gold 6443N",
    "Status": {
      "HealthRollup": "OK"
    }
  },
  "Processors": {
    "@odata.id": "/redfish/v1/Systems/1/Processors/"
  },
  "SKU": "P48541-B21",
  "SecureBoot": {
    "@odata.id": "/redfish/v1/Systems/1/SecureBoot/"
  },
  "SerialNumber": "MXQ346090F",
  "Status": {
    "Health": "OK",
    "HealthRollup": "OK",
    "State": "Enabled"
  },
  "Storage": {
    "@odata.id": "/redfish/v1/Systems/1/Storage/"
  },
  "SystemType": "Physical",
  "TrustedModules": [
    {
      "FirmwareVersion": "1.512",
      "InterfaceType": "TPM2_0",
      "Oem": {
        "Hpe": {
          "@odata.context": "/redfish/v1/$metadata#HpeTrustedModuleExt.HpeTrustedModuleExt",
          "@odata.type": "#HpeTrustedModuleExt.v2_0_0.HpeTrustedModuleExt",
          "VendorName": "STMicro"
        }
      },
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      }
    }
  ],
  "UUID": "35383450-3134-584D-5133-343630393046"
}

real	0m0.444s
user	0m0.012s
sys	0m0.005s
(hpe_fw) [XXXXXX@welktxefnce-h-pe1util-vm01 XXXXXX]$

(hpe_fw) [XXXXXX@welktxefnce-h-pe1util-vm01 XXXXXX]$  time curl -sk -u 'XXXXXX:XXXXXX' -X GET https://[$IP]/redfish/v1/Chassis/1/ | jq .
{
  "@odata.context": "/redfish/v1/$metadata#Chassis.Chassis",
  "@odata.etag": "W/\"501622E7\"",
  "@odata.id": "/redfish/v1/Chassis/1/",
  "@odata.type": "#Chassis.v1_23_0.Chassis",
  "Id": "1",
  "AssetTag": "",
  "ChassisType": "Other",
  "EnvironmentalClass": "A2",
  "Links": {
    "ContainedBy": {
      "@odata.id": "/redfish/v1/Chassis/EnclosureChassis/"
    },
    "ManagedBy": [
      {
        "@odata.id": "/redfish/v1/Managers/1/"
      }
    ],
    "ComputerSystems": [
      {
        "@odata.id": "/redfish/v1/Systems/1/"
      }
    ]
  },
  "LocationIndicatorActive": false,
  "Manufacturer": "HPE",
  "Model": "Edgeline e930t",
  "Name": "Computer System Chassis",
  "NetworkAdapters": {
    "@odata.id": "/redfish/v1/Chassis/1/NetworkAdapters/"
  },
  "Oem": {
    "Hpe": {
      "@odata.context": "/redfish/v1/$metadata#HpeServerChassis.HpeServerChassis",
      "@odata.type": "#HpeServerChassis.v2_4_0.HpeServerChassis",
      "Actions": {
        "#HpeServerChassis.DisableMCTPOnServer": {
          "target": "/redfish/v1/Chassis/1/Actions/Oem/Hpe/HpeServerChassis.DisableMCTPOnServer/"
        },
        "#HpeServerChassis.FactoryResetMCTP": {
          "target": "/redfish/v1/Chassis/1/Actions/Oem/Hpe/HpeServerChassis.FactoryResetMCTP/"
        },
        "#HpeServerChassis.ModifyEnclosureChassisFru": {
          "target": "/redfish/v1/Chassis/1/Actions/Oem/Hpe/HpeServerChassis.ModifyEnclosureChassisFru/"
        }
      },
      "BayNumber": 1,
      "ElConfigOverride": false,
      "Firmware": {
        "PlatformDefinitionTable": {
          "Current": {
            "VersionString": "9.10.0 Build 11"
          }
        },
        "SystemProgrammableLogicDevice": {
          "Current": {
            "VersionString": "0x04"
          }
        }
      },
      "Links": {
        "Devices": {
          "@odata.id": "/redfish/v1/Chassis/1/Devices/"
        }
      },
      "MCTPEnabledOnServer": true,
      "SystemMaintenanceSwitches": {
        "Sw1": "Off",
        "Sw10": "On",
        "Sw11": "Off",
        "Sw12": "Off",
        "Sw2": "Off",
        "Sw3": "Off",
        "Sw4": "Off",
        "Sw5": "Off",
        "Sw6": "Off",
        "Sw7": "Off",
        "Sw8": "Off",
        "Sw9": "Off"
      },
      "TelcoModeEnabled": null
    }
  },
  "PCIeDevices": {
    "@odata.id": "/redfish/v1/Chassis/1/PCIeDevices/"
  },
  "PCIeSlots": {
    "@odata.id": "/redfish/v1/Chassis/1/PCIeSlots/"
  },
  "Power": {
    "@odata.id": "/redfish/v1/Chassis/1/Power/"
  },
  "PowerState": "On",
  "SKU": "P48541-B21",
  "SerialNumber": "MXQ346090F",
  "Status": {
    "Health": "OK",
    "State": "Enabled"
  },
  "Thermal": {
    "@odata.id": "/redfish/v1/Chassis/1/Thermal/"
  },
  "ThermalSubsystem": {
    "@odata.id": "/redfish/v1/Chassis/1/ThermalSubsystem/"
  }
}

real	0m0.460s
user	0m0.011s
sys	0m0.006s
(hpe_fw) [XXXXXX@welktxefnce-h-pe1util-vm01 XXXXXX]$

(hpe_fw) [XXXXXX@welktxefnce-h-pe1util-vm01 XXXXXX]$ time curl -sk -u 'XXXXXX:XXXXXX' -X GET https://[$IP]/redfish/v1/Chassis/1/Thermal | jq .
{
  "@odata.context": "/redfish/v1/$metadata#Thermal.Thermal",
  "@odata.etag": "W/\"A3A0DE5D\"",
  "@odata.id": "/redfish/v1/Chassis/1/Thermal",
  "@odata.type": "#Thermal.v1_7_1.Thermal",
  "Id": "Thermal",
  "Fans": [
    {
      "@odata.id": "/redfish/v1/Chassis/1/Thermal#Fans/0",
      "MemberId": "0",
      "Name": "Fan 1",
      "Oem": {
        "Hpe": {
          "@odata.context": "/redfish/v1/$metadata#HpeServerFan.HpeServerFan",
          "@odata.type": "#HpeServerFan.v2_0_0.HpeServerFan",
          "HotPluggable": true,
          "Location": "System",
          "Redundant": true
        }
      },
      "PhysicalContext": "SystemBoard",
      "Reading": 22,
      "ReadingUnits": "Percent",
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      }
    },
    {
      "@odata.id": "/redfish/v1/Chassis/1/Thermal#Fans/1",
      "MemberId": "1",
      "Name": "Fan 2",
      "Oem": {
        "Hpe": {
          "@odata.context": "/redfish/v1/$metadata#HpeServerFan.HpeServerFan",
          "@odata.type": "#HpeServerFan.v2_0_0.HpeServerFan",
          "HotPluggable": true,
          "Location": "System",
          "Redundant": true
        }
      },
      "PhysicalContext": "SystemBoard",
      "Reading": 22,
      "ReadingUnits": "Percent",
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      }
    },
    {
      "@odata.id": "/redfish/v1/Chassis/1/Thermal#Fans/2",
      "MemberId": "2",
      "Name": "Fan 3",
      "Oem": {
        "Hpe": {
          "@odata.context": "/redfish/v1/$metadata#HpeServerFan.HpeServerFan",
          "@odata.type": "#HpeServerFan.v2_0_0.HpeServerFan",
          "HotPluggable": true,
          "Location": "System",
          "Redundant": true
        }
      },
      "PhysicalContext": "SystemBoard",
      "Reading": 22,
      "ReadingUnits": "Percent",
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      }
    },
    {
      "@odata.id": "/redfish/v1/Chassis/1/Thermal#Fans/3",
      "MemberId": "3",
      "Name": "Fan 4",
      "Oem": {
        "Hpe": {
          "@odata.context": "/redfish/v1/$metadata#HpeServerFan.HpeServerFan",
          "@odata.type": "#HpeServerFan.v2_0_0.HpeServerFan",
          "HotPluggable": true,
          "Location": "System",
          "Redundant": true
        }
      },
      "PhysicalContext": "SystemBoard",
      "Reading": 22,
      "ReadingUnits": "Percent",
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      }
    },
    {
      "@odata.id": "/redfish/v1/Chassis/1/Thermal#Fans/4",
      "MemberId": "4",
      "Name": "Fan 5",
      "Oem": {
        "Hpe": {
          "@odata.context": "/redfish/v1/$metadata#HpeServerFan.HpeServerFan",
          "@odata.type": "#HpeServerFan.v2_0_0.HpeServerFan",
          "HotPluggable": true,
          "Location": "System",
          "Redundant": true
        }
      },
      "PhysicalContext": "SystemBoard",
      "Reading": 22,
      "ReadingUnits": "Percent",
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      }
    },
    {
      "@odata.id": "/redfish/v1/Chassis/1/Thermal#Fans/5",
      "MemberId": "5",
      "Name": "Fan 6",
      "Oem": {
        "Hpe": {
          "@odata.context": "/redfish/v1/$metadata#HpeServerFan.HpeServerFan",
          "@odata.type": "#HpeServerFan.v2_0_0.HpeServerFan",
          "HotPluggable": true,
          "Location": "System",
          "Redundant": true
        }
      },
      "PhysicalContext": "SystemBoard",
      "Reading": 22,
      "ReadingUnits": "Percent",
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      }
    }
  ],
  "Name": "Thermal",
  "Oem": {
    "Hpe": {
      "@odata.context": "/redfish/v1/$metadata#HpeThermalExt.HpeThermalExt",
      "@odata.type": "#HpeThermalExt.v2_0_0.HpeThermalExt",
      "Actions": {
        "#HpeThermalExt.SetUserTempThreshold": {
          "target": "/redfish/v1/Chassis/1/Thermal/Actions/Oem/Hpe/HpeThermalExt.SetUserTempThreshold"
        }
      },
      "FanPercentMinimum": 0,
      "ThermalConfiguration": "OptimalCooling"
    }
  },
  "Temperatures": [
    {
      "@odata.id": "/redfish/v1/Chassis/1/Thermal#Temperatures/0",
      "MemberId": "0",
      "Name": "01-Inlet Ambient",
      "Oem": {
        "Hpe": {
          "@odata.context": "/redfish/v1/$metadata#HpeSeaOfSensors.HpeSeaOfSensors",
          "@odata.type": "#HpeSeaOfSensors.v2_1_0.HpeSeaOfSensors",
          "CriticalTempUserThreshold": 0,
          "LocationXmm": 10,
          "LocationYmm": 0,
          "WarningTempUserThreshold": 0
        }
      },
      "PhysicalContext": "Intake",
      "ReadingCelsius": 32,
      "SensorNumber": 1,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 62,
      "UpperThresholdFatal": 66
    },
    {
      "@odata.id": "/redfish/v1/Chassis/1/Thermal#Temperatures/1",
      "MemberId": "1",
      "Name": "02-CPU 1 PkgTmp",
      "Oem": {
        "Hpe": {
          "@odata.context": "/redfish/v1/$metadata#HpeSeaOfSensors.HpeSeaOfSensors",
          "@odata.type": "#HpeSeaOfSensors.v2_1_0.HpeSeaOfSensors",
          "CriticalTempUserThreshold": 0,
          "LocationXmm": 7,
          "LocationYmm": 10,
          "WarningTempUserThreshold": 0
        }
      },
      "PhysicalContext": "CPU",
      "ReadingCelsius": 61,
      "SensorNumber": 2,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 91,
      "UpperThresholdFatal": null
    },
    {
      "@odata.id": "/redfish/v1/Chassis/1/Thermal#Temperatures/2",
      "MemberId": "2",
      "Name": "03-P1 DIMM 1-6",
      "Oem": {
        "Hpe": {
          "@odata.context": "/redfish/v1/$metadata#HpeSeaOfSensors.HpeSeaOfSensors",
          "@odata.type": "#HpeSeaOfSensors.v2_1_0.HpeSeaOfSensors",
          "LocationXmm": 2,
          "LocationYmm": 11
        }
      },
      "PhysicalContext": "Memory",
      "ReadingCelsius": 42,
      "SensorNumber": 3,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 90,
      "UpperThresholdFatal": null
    },
    {
      "@odata.id": "/redfish/v1/Chassis/1/Thermal#Temperatures/3",
      "MemberId": "3",
      "Name": "04-P1 PMM 1-6",
      "Oem": {
        "Hpe": {
          "@odata.context": "/redfish/v1/$metadata#HpeSeaOfSensors.HpeSeaOfSensors",
          "@odata.type": "#HpeSeaOfSensors.v2_1_0.HpeSeaOfSensors",
          "LocationXmm": 2,
          "LocationYmm": 11
        }
      },
      "PhysicalContext": "Memory",
      "ReadingCelsius": 0,
      "SensorNumber": 4,
      "Status": {
        "State": "Absent"
      },
      "UpperThresholdCritical": null,
      "UpperThresholdFatal": null
    },
    {
      "@odata.id": "/redfish/v1/Chassis/1/Thermal#Temperatures/4",
      "MemberId": "4",
      "Name": "05-P1 DIMM 7-12",
      "Oem": {
        "Hpe": {
          "@odata.context": "/redfish/v1/$metadata#HpeSeaOfSensors.HpeSeaOfSensors",
          "@odata.type": "#HpeSeaOfSensors.v2_1_0.HpeSeaOfSensors",
          "LocationXmm": 13,
          "LocationYmm": 11
        }
      },
      "PhysicalContext": "Memory",
      "ReadingCelsius": 50,
      "SensorNumber": 5,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 90,
      "UpperThresholdFatal": null
    },
    {
      "@odata.id": "/redfish/v1/Chassis/1/Thermal#Temperatures/5",
      "MemberId": "5",
      "Name": "06-P1 PMM 7-12",
      "Oem": {
        "Hpe": {
          "@odata.context": "/redfish/v1/$metadata#HpeSeaOfSensors.HpeSeaOfSensors",
          "@odata.type": "#HpeSeaOfSensors.v2_1_0.HpeSeaOfSensors",
          "LocationXmm": 13,
          "LocationYmm": 11
        }
      },
      "PhysicalContext": "Memory",
      "ReadingCelsius": 0,
      "SensorNumber": 6,
      "Status": {
        "State": "Absent"
      },
      "UpperThresholdCritical": null,
      "UpperThresholdFatal": null
    },
    {
      "@odata.id": "/redfish/v1/Chassis/1/Thermal#Temperatures/6",
      "MemberId": "6",
      "Name": "07-VR P1",
      "Oem": {
        "Hpe": {
          "@odata.context": "/redfish/v1/$metadata#HpeSeaOfSensors.HpeSeaOfSensors",
          "@odata.type": "#HpeSeaOfSensors.v2_1_0.HpeSeaOfSensors",
          "LocationXmm": 6,
          "LocationYmm": 13
        }
      },
      "PhysicalContext": "SystemBoard",
      "ReadingCelsius": 57,
      "SensorNumber": 7,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 110,
      "UpperThresholdFatal": null
    },
    {
      "@odata.id": "/redfish/v1/Chassis/1/Thermal#Temperatures/7",
      "MemberId": "7",
      "Name": "08-Chipset",
      "Oem": {
        "Hpe": {
          "@odata.context": "/redfish/v1/$metadata#HpeSeaOfSensors.HpeSeaOfSensors",
          "@odata.type": "#HpeSeaOfSensors.v2_1_0.HpeSeaOfSensors",
          "LocationXmm": 4,
          "LocationYmm": 3
        }
      },
      "PhysicalContext": "SystemBoard",
      "ReadingCelsius": 48,
      "SensorNumber": 8,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 100,
      "UpperThresholdFatal": null
    },
    {
      "@odata.id": "/redfish/v1/Chassis/1/Thermal#Temperatures/8",
      "MemberId": "8",
      "Name": "09-BMC",
      "Oem": {
        "Hpe": {
          "@odata.context": "/redfish/v1/$metadata#HpeSeaOfSensors.HpeSeaOfSensors",
          "@odata.type": "#HpeSeaOfSensors.v2_1_0.HpeSeaOfSensors",
          "LocationXmm": 11,
          "LocationYmm": 2
        }
      },
      "PhysicalContext": "SystemBoard",
      "ReadingCelsius": 55,
      "SensorNumber": 9,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 110,
      "UpperThresholdFatal": null
    },
    {
      "@odata.id": "/redfish/v1/Chassis/1/Thermal#Temperatures/9",
      "MemberId": "9",
      "Name": "10-M2",
      "Oem": {
        "Hpe": {
          "@odata.context": "/redfish/v1/$metadata#HpeSeaOfSensors.HpeSeaOfSensors",
          "@odata.type": "#HpeSeaOfSensors.v2_1_0.HpeSeaOfSensors",
          "LocationXmm": 0,
          "LocationYmm": 0
        }
      },
      "PhysicalContext": "SystemBoard",
      "ReadingCelsius": 40,
      "SensorNumber": 10,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 80,
      "UpperThresholdFatal": null
    },
    {
      "@odata.id": "/redfish/v1/Chassis/1/Thermal#Temperatures/10",
      "MemberId": "10",
      "Name": "16-PCI 1 Zone",
      "Oem": {
        "Hpe": {
          "@odata.context": "/redfish/v1/$metadata#HpeSeaOfSensors.HpeSeaOfSensors",
          "@odata.type": "#HpeSeaOfSensors.v2_1_0.HpeSeaOfSensors",
          "CriticalTempUserThreshold": 0,
          "LocationXmm": 0,
          "LocationYmm": 4,
          "WarningTempUserThreshold": 0
        }
      },
      "PhysicalContext": "SystemBoard",
      "ReadingCelsius": 32,
      "SensorNumber": 11,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 70,
      "UpperThresholdFatal": 75
    },
    {
      "@odata.id": "/redfish/v1/Chassis/1/Thermal#Temperatures/11",
      "MemberId": "11",
      "Name": "18-PCI 2 Zone",
      "Oem": {
        "Hpe": {
          "@odata.context": "/redfish/v1/$metadata#HpeSeaOfSensors.HpeSeaOfSensors",
          "@odata.type": "#HpeSeaOfSensors.v2_1_0.HpeSeaOfSensors",
          "CriticalTempUserThreshold": 0,
          "LocationXmm": 0,
          "LocationYmm": 4,
          "WarningTempUserThreshold": 0
        }
      },
      "PhysicalContext": "SystemBoard",
      "ReadingCelsius": 32,
      "SensorNumber": 12,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 70,
      "UpperThresholdFatal": 75
    },
    {
      "@odata.id": "/redfish/v1/Chassis/1/Thermal#Temperatures/12",
      "MemberId": "12",
      "Name": "20-PCI 3 Zone",
      "Oem": {
        "Hpe": {
          "@odata.context": "/redfish/v1/$metadata#HpeSeaOfSensors.HpeSeaOfSensors",
          "@odata.type": "#HpeSeaOfSensors.v2_1_0.HpeSeaOfSensors",
          "CriticalTempUserThreshold": 0,
          "LocationXmm": 0,
          "LocationYmm": 4,
          "WarningTempUserThreshold": 0
        }
      },
      "PhysicalContext": "SystemBoard",
      "ReadingCelsius": 32,
      "SensorNumber": 13,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 70,
      "UpperThresholdFatal": 75
    },
    {
      "@odata.id": "/redfish/v1/Chassis/1/Thermal#Temperatures/13",
      "MemberId": "13",
      "Name": "21-PCI 4",
      "Oem": {
        "Hpe": {
          "@odata.context": "/redfish/v1/$metadata#HpeSeaOfSensors.HpeSeaOfSensors",
          "@odata.type": "#HpeSeaOfSensors.v2_1_0.HpeSeaOfSensors",
          "LocationXmm": 15,
          "LocationYmm": 4
        }
      },
      "PhysicalContext": "SystemBoard",
      "ReadingCelsius": 0,
      "SensorNumber": 14,
      "Status": {
        "State": "Absent"
      },
      "UpperThresholdCritical": null,
      "UpperThresholdFatal": null
    },
    {
      "@odata.id": "/redfish/v1/Chassis/1/Thermal#Temperatures/14",
      "MemberId": "14",
      "Name": "22-PCI 4 Zone",
      "Oem": {
        "Hpe": {
          "@odata.context": "/redfish/v1/$metadata#HpeSeaOfSensors.HpeSeaOfSensors",
          "@odata.type": "#HpeSeaOfSensors.v2_1_0.HpeSeaOfSensors",
          "LocationXmm": 15,
          "LocationYmm": 4
        }
      },
      "PhysicalContext": "SystemBoard",
      "ReadingCelsius": 0,
      "SensorNumber": 15,
      "Status": {
        "State": "Absent"
      },
      "UpperThresholdCritical": null,
      "UpperThresholdFatal": null
    },
    {
      "@odata.id": "/redfish/v1/Chassis/1/Thermal#Temperatures/15",
      "MemberId": "15",
      "Name": "27-Sys Exhaust 1",
      "Oem": {
        "Hpe": {
          "@odata.context": "/redfish/v1/$metadata#HpeSeaOfSensors.HpeSeaOfSensors",
          "@odata.type": "#HpeSeaOfSensors.v2_1_0.HpeSeaOfSensors",
          "CriticalTempUserThreshold": 0,
          "LocationXmm": 5,
          "LocationYmm": 15,
          "WarningTempUserThreshold": 0
        }
      },
      "PhysicalContext": "SystemBoard",
      "ReadingCelsius": 51,
      "SensorNumber": 16,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 85,
      "UpperThresholdFatal": null
    },
    {
      "@odata.id": "/redfish/v1/Chassis/1/Thermal#Temperatures/16",
      "MemberId": "16",
      "Name": "15.1-PCI 1-Network controller",
      "Oem": {
        "Hpe": {
          "@odata.context": "/redfish/v1/$metadata#HpeSeaOfSensors.HpeSeaOfSensors",
          "@odata.type": "#HpeSeaOfSensors.v2_1_0.HpeSeaOfSensors",
          "LocationXmm": 0,
          "LocationYmm": 4,
          "MainSensorName": "15-PCI 1"
        }
      },
      "PhysicalContext": "SystemBoard",
      "ReadingCelsius": 67,
      "SensorNumber": 17,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 105,
      "UpperThresholdFatal": 115,
      "UpperThresholdNonCritical": 95
    },
    {
      "@odata.id": "/redfish/v1/Chassis/1/Thermal#Temperatures/17",
      "MemberId": "17",
      "Name": "15.2-PCI 1-SFP28 (SFF-8402)",
      "Oem": {
        "Hpe": {
          "@odata.context": "/redfish/v1/$metadata#HpeSeaOfSensors.HpeSeaOfSensors",
          "@odata.type": "#HpeSeaOfSensors.v2_1_0.HpeSeaOfSensors",
          "LocationXmm": 0,
          "LocationYmm": 4,
          "MainSensorName": "15-PCI 1"
        }
      },
      "PhysicalContext": "SystemBoard",
      "ReadingCelsius": 41,
      "SensorNumber": 17,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 78,
      "UpperThresholdFatal": null,
      "UpperThresholdNonCritical": 73
    },
    {
      "@odata.id": "/redfish/v1/Chassis/1/Thermal#Temperatures/18",
      "MemberId": "18",
      "Name": "15.3-PCI 1-SFP28 (SFF-8402)",
      "Oem": {
        "Hpe": {
          "@odata.context": "/redfish/v1/$metadata#HpeSeaOfSensors.HpeSeaOfSensors",
          "@odata.type": "#HpeSeaOfSensors.v2_1_0.HpeSeaOfSensors",
          "LocationXmm": 0,
          "LocationYmm": 4,
          "MainSensorName": "15-PCI 1"
        }
      },
      "PhysicalContext": "SystemBoard",
      "ReadingCelsius": 37,
      "SensorNumber": 17,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 75,
      "UpperThresholdFatal": null,
      "UpperThresholdNonCritical": 70
    },
    {
      "@odata.id": "/redfish/v1/Chassis/1/Thermal#Temperatures/19",
      "MemberId": "19",
      "Name": "15.4-PCI 1-SFP28 (SFF-8402)",
      "Oem": {
        "Hpe": {
          "@odata.context": "/redfish/v1/$metadata#HpeSeaOfSensors.HpeSeaOfSensors",
          "@odata.type": "#HpeSeaOfSensors.v2_1_0.HpeSeaOfSensors",
          "LocationXmm": 0,
          "LocationYmm": 4,
          "MainSensorName": "15-PCI 1"
        }
      },
      "PhysicalContext": "SystemBoard",
      "ReadingCelsius": 37,
      "SensorNumber": 17,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 75,
      "UpperThresholdFatal": null,
      "UpperThresholdNonCritical": 70
    },
    {
      "@odata.id": "/redfish/v1/Chassis/1/Thermal#Temperatures/20",
      "MemberId": "20",
      "Name": "15.5-PCI 1-SFP28 (SFF-8402)",
      "Oem": {
        "Hpe": {
          "@odata.context": "/redfish/v1/$metadata#HpeSeaOfSensors.HpeSeaOfSensors",
          "@odata.type": "#HpeSeaOfSensors.v2_1_0.HpeSeaOfSensors",
          "LocationXmm": 0,
          "LocationYmm": 4,
          "MainSensorName": "15-PCI 1"
        }
      },
      "PhysicalContext": "SystemBoard",
      "ReadingCelsius": 37,
      "SensorNumber": 17,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 75,
      "UpperThresholdFatal": null,
      "UpperThresholdNonCritical": 70
    },
    {
      "@odata.id": "/redfish/v1/Chassis/1/Thermal#Temperatures/21",
      "MemberId": "21",
      "Name": "17.1-PCI 2-Network controller",
      "Oem": {
        "Hpe": {
          "@odata.context": "/redfish/v1/$metadata#HpeSeaOfSensors.HpeSeaOfSensors",
          "@odata.type": "#HpeSeaOfSensors.v2_1_0.HpeSeaOfSensors",
          "LocationXmm": 0,
          "LocationYmm": 4,
          "MainSensorName": "17-PCI 2"
        }
      },
      "PhysicalContext": "SystemBoard",
      "ReadingCelsius": 70,
      "SensorNumber": 18,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 105,
      "UpperThresholdFatal": 115,
      "UpperThresholdNonCritical": 95
    },
    {
      "@odata.id": "/redfish/v1/Chassis/1/Thermal#Temperatures/22",
      "MemberId": "22",
      "Name": "17.2-PCI 2-SFP28 (SFF-8402)",
      "Oem": {
        "Hpe": {
          "@odata.context": "/redfish/v1/$metadata#HpeSeaOfSensors.HpeSeaOfSensors",
          "@odata.type": "#HpeSeaOfSensors.v2_1_0.HpeSeaOfSensors",
          "LocationXmm": 0,
          "LocationYmm": 4,
          "MainSensorName": "17-PCI 2"
        }
      },
      "PhysicalContext": "SystemBoard",
      "ReadingCelsius": 32,
      "SensorNumber": 18,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 75,
      "UpperThresholdFatal": null,
      "UpperThresholdNonCritical": 70
    },
    {
      "@odata.id": "/redfish/v1/Chassis/1/Thermal#Temperatures/23",
      "MemberId": "23",
      "Name": "17.3-PCI 2-SFP28 (SFF-8402)",
      "Oem": {
        "Hpe": {
          "@odata.context": "/redfish/v1/$metadata#HpeSeaOfSensors.HpeSeaOfSensors",
          "@odata.type": "#HpeSeaOfSensors.v2_1_0.HpeSeaOfSensors",
          "LocationXmm": 0,
          "LocationYmm": 4,
          "MainSensorName": "17-PCI 2"
        }
      },
      "PhysicalContext": "SystemBoard",
      "ReadingCelsius": 33,
      "SensorNumber": 18,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 75,
      "UpperThresholdFatal": null,
      "UpperThresholdNonCritical": 70
    },
    {
      "@odata.id": "/redfish/v1/Chassis/1/Thermal#Temperatures/24",
      "MemberId": "24",
      "Name": "19.1-PCI 3-Network controller",
      "Oem": {
        "Hpe": {
          "@odata.context": "/redfish/v1/$metadata#HpeSeaOfSensors.HpeSeaOfSensors",
          "@odata.type": "#HpeSeaOfSensors.v2_1_0.HpeSeaOfSensors",
          "LocationXmm": 0,
          "LocationYmm": 4,
          "MainSensorName": "19-PCI 3"
        }
      },
      "PhysicalContext": "SystemBoard",
      "ReadingCelsius": 64,
      "SensorNumber": 19,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 105,
      "UpperThresholdFatal": 115,
      "UpperThresholdNonCritical": 95
    },
    {
      "@odata.id": "/redfish/v1/Chassis/1/Thermal#Temperatures/25",
      "MemberId": "25",
      "Name": "19.2-PCI 3-SFP28 (SFF-8402)",
      "Oem": {
        "Hpe": {
          "@odata.context": "/redfish/v1/$metadata#HpeSeaOfSensors.HpeSeaOfSensors",
          "@odata.type": "#HpeSeaOfSensors.v2_1_0.HpeSeaOfSensors",
          "LocationXmm": 0,
          "LocationYmm": 4,
          "MainSensorName": "19-PCI 3"
        }
      },
      "PhysicalContext": "SystemBoard",
      "ReadingCelsius": 37,
      "SensorNumber": 19,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 78,
      "UpperThresholdFatal": null,
      "UpperThresholdNonCritical": 73
    },
    {
      "@odata.id": "/redfish/v1/Chassis/1/Thermal#Temperatures/26",
      "MemberId": "26",
      "Name": "19.3-PCI 3-SFP28 (SFF-8402)",
      "Oem": {
        "Hpe": {
          "@odata.context": "/redfish/v1/$metadata#HpeSeaOfSensors.HpeSeaOfSensors",
          "@odata.type": "#HpeSeaOfSensors.v2_1_0.HpeSeaOfSensors",
          "LocationXmm": 0,
          "LocationYmm": 4,
          "MainSensorName": "19-PCI 3"
        }
      },
      "PhysicalContext": "SystemBoard",
      "ReadingCelsius": 33,
      "SensorNumber": 19,
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      },
      "UpperThresholdCritical": 75,
      "UpperThresholdFatal": null,
      "UpperThresholdNonCritical": 70
    }
  ]
}

real	0m0.366s
user	0m0.014s
sys	0m0.006s
(hpe_fw) [XXXXXX@welktxefnce-h-pe1util-vm01 XXXXXX]$



(hpe_fw) [XXXXXX@welktxefnce-h-pe1util-vm01 XXXXXX]$  time curl -sk -u 'XXXXXX:XXXXXX' -X GET https://[$IP]/redfish/v1/Chassis/1/Power | jq .
{
  "@odata.context": "/redfish/v1/$metadata#Power.Power",
  "@odata.etag": "W/\"B99833D4\"",
  "@odata.id": "/redfish/v1/Chassis/1/Power",
  "@odata.type": "#Power.v1_7_1.Power",
  "Id": "Power",
  "Name": "PowerMetrics",
  "Oem": {
    "Hpe": {
      "@odata.context": "/redfish/v1/$metadata#HpePowerMetricsExt.HpePowerMetricsExt",
      "@odata.type": "#HpePowerMetricsExt.v2_5_1.HpePowerMetricsExt",
      "BrownoutRecoveryEnabled": true,
      "HasCpuPowerMetering": true,
      "HasDimmPowerMetering": true,
      "HasGpuPowerMetering": false,
      "HasPowerMetering": true,
      "HighEfficiencyMode": "Balanced",
      "Links": {
        "PowerMeter": {
          "@odata.id": "/redfish/v1/Chassis/1/Power/PowerMeter"
        },
        "FastPowerMeter": {
          "@odata.id": "/redfish/v1/Chassis/1/Power/FastPowerMeter"
        },
        "SlowPowerMeter": {
          "@odata.id": "/redfish/v1/Chassis/1/Power/SlowPowerMeter"
        },
        "FederatedGroupCapping": {
          "@odata.id": "/redfish/v1/Chassis/1/Power/FederatedGroupCapping"
        }
      },
      "MinimumSafelyAchievableCap": null,
      "MinimumSafelyAchievableCapValid": false,
      "PowerMetric": {
        "AmbTemp": 32,
        "Cap": 0,
        "CpuCapLim": 100,
        "CpuMax": 0,
        "CpuPwrSavLim": 100,
        "CpuWatts": 71,
        "DimmWatts": 13,
        "GpuWatts": 0,
        "PrMode": "osc",
        "PunCap": false,
        "UnachCap": false
      },
      "SNMPPowerThresholdAlert": {
        "DurationInMin": 0,
        "ThresholdWatts": 0,
        "Trigger": "Disabled"
      }
    }
  },
  "PowerControl": [
    {
      "@odata.id": "/redfish/v1/Chassis/1/Power#PowerControl/0",
      "MemberId": "0",
      "PowerCapacityWatts": 3000,
      "PowerConsumedWatts": 133,
      "PowerMetrics": {
        "AverageConsumedWatts": 132,
        "IntervalInMin": 20,
        "MaxConsumedWatts": 178,
        "MinConsumedWatts": 130
      }
    }
  ],
  "PowerSupplies": [
    {
      "@odata.id": "/redfish/v1/Chassis/1/Power#PowerSupplies/0",
      "FirmwareVersion": "1.01",
      "LastPowerOutputWatts": 133,
      "LineInputVoltage": 212,
      "LineInputVoltageType": "Unknown",
      "Manufacturer": null,
      "MemberId": "0",
      "Model": "P11298-001 ",
      "Name": "HpeServerPowerSupply",
      "Oem": {
        "Hpe": {
          "@odata.context": "/redfish/v1/$metadata#HpeServerPowerSupply.HpeServerPowerSupply",
          "@odata.type": "#HpeServerPowerSupply.v2_0_0.HpeServerPowerSupply",
          "AveragePowerOutputWatts": 133,
          "BayNumber": 1,
          "Domain": "System",
          "HotplugCapable": true,
          "MaxPowerOutputWatts": 169,
          "Mismatched": false,
          "PowerSupplyStatus": {
            "State": "Ok"
          },
          "iPDUCapable": false
        }
      },
      "PowerCapacityWatts": 1500,
      "PowerSupplyType": "AC",
      "SerialNumber": "6W2317RB00AZ",
      "SparePartNumber": "P11771-001",
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      }
    },
    {
      "@odata.id": "/redfish/v1/Chassis/1/Power#PowerSupplies/1",
      "FirmwareVersion": "1.01",
      "LastPowerOutputWatts": 133,
      "LineInputVoltage": 213,
      "LineInputVoltageType": "Unknown",
      "Manufacturer": null,
      "MemberId": "1",
      "Model": "P11298-001 ",
      "Name": "HpeServerPowerSupply",
      "Oem": {
        "Hpe": {
          "@odata.context": "/redfish/v1/$metadata#HpeServerPowerSupply.HpeServerPowerSupply",
          "@odata.type": "#HpeServerPowerSupply.v2_0_0.HpeServerPowerSupply",
          "AveragePowerOutputWatts": 133,
          "BayNumber": 2,
          "Domain": "System",
          "HotplugCapable": true,
          "MaxPowerOutputWatts": 169,
          "Mismatched": false,
          "PowerSupplyStatus": {
            "State": "Ok"
          },
          "iPDUCapable": false
        }
      },
      "PowerCapacityWatts": 1500,
      "PowerSupplyType": "AC",
      "SerialNumber": "6W2317RB00DS",
      "SparePartNumber": "P11771-001",
      "Status": {
        "Health": "OK",
        "State": "Enabled"
      }
    }
  ]
}

real	0m0.376s
user	0m0.010s
sys	0m0.008s
(hpe_fw) [XXXXXX@welktxefnce-h-pe1util-vm01 XXXXXX]$

```
### All Execution times are  under 500ms, all appear normal and in good working order

### Passed


