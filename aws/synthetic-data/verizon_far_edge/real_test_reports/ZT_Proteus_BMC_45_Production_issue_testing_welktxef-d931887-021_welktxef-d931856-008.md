# ZT .45 BMC firmware validation
# 10/24/23 James Patchett

## Target Controller Rchltxfe-c000000-001
Controller-0 iLO 2607:f160:a:d02e:cd:fe0::8000 
Controller-1 iLO 2607:f160:a:d02e:cd:fe0::8001
Worker-0 iLO 2607:f160:a:d02e:cd:fe0::8002 
OAM 2607:f160:0:3043:cd:290:0:10



## Target Subcloud welktxef-d931887-021 (currently on controller 2607:f160:0:3049:cd:290:0:10 )
OAM 2607:f160:10:9249:ce:40a:0:f409
BMC 2607:f160:10:9249:ce:40a:0:e015

ipmitool -I lanplus -U XXXXXX -P XXXXXX -H 2607:f160:10:9249:ce:40a:0:e015 sol activate

## Target Subcloud welktxef-d931856-008
OAM: 2607:f160:10:80b1:ce:40a:0:f408
BMC: 2607:f160:10:80b1:ce:40a:0:e008

ipmitool -I lanplus -U XXXXXX -P XXXXXX -H 2607:f160:10:80b1:ce:40a:0:e008 sol activate

### Subcloud welktxef-d931887-021
### Curently has .45 bmc, forcing it to install over 10 times to validate redfish issue after installation.

### Iteration 1 of 10

Installed .45, log is kept seperate from this file.

### Redfish commands after .45 bmc installation 
### 
```sh 
curl -gsk -u XXXXXX:XXXXXX -X GET https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Systems/Self | jq .
```

```log
[XXXXXX@welktxefnce-h-pe1util-vm01 archive_1]$  curl -gsk -u XXXXXX:XXXXXX -X GET https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Systems/Self | jq .
{
  "@Redfish.Settings": {
    "@odata.type": "#Settings.v1_2_2.Settings",
    "SettingsObject": {
      "@odata.id": "/redfish/v1/Systems/Self/SD"
    }
  },
  "@odata.context": "/redfish/v1/$metadata#ComputerSystem.ComputerSystem",
  "@odata.etag": "\"1702332298\"",
  "@odata.id": "/redfish/v1/Systems/Self",
  "@odata.type": "#ComputerSystem.v1_8_0.ComputerSystem",
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
        "Nmi",
        "GracefulShutdown",
        "ForceOff",
        "ForceRestart",
        "On"
      ],
      "target": "/redfish/v1/Systems/Self/Actions/ComputerSystem.Reset"
    }
  },
  "AssetTag": "PA-00371-00320741213N074",
  "Bios": {
    "@odata.id": "/redfish/v1/Systems/Self/Bios"
  },
  "BiosVersion": "0.23",
  "Boot": {
    "BootNext": null,
    "BootOptions": {
      "@odata.id": "/redfish/v1/Systems/Self/BootOptions"
    },
    "BootOrder": [
      "Boot0000",
      "Boot0003",
      "Boot0004",
      "Boot0005",
      "Boot0006",
      "Boot0007",
      "Boot0008",
      "Boot0009",
      "Boot0002",
      "Boot000A"
    ],
    "BootOrderPropertySelection": "BootOrder",
    "BootSourceOverrideEnabled": "Disabled",
    "BootSourceOverrideEnabled@Redfish.AllowableValues": [
      "Disabled",
      "Once",
      "Continuous"
    ],
    "BootSourceOverrideMode": null,
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
  "HostName": "welktxef-931887-rz-le2pts6-021",
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
  "Name": "Proteus I_Mix",
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
                "CERTIFICATE": 1
              },
              {
                "CPU": 1
              },
              {
                "PCIE": 1
              },
              {
                "DIMM": 1
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
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_00/PCIeFunctions/DevType3_DMMY_DevIndexC"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_00/PCIeFunctions/DevType3_SLT4_DevIndex9"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_02/PCIeFunctions/DevType3_NRP0_DevIndexD"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_11/PCIeFunctions/DevType3_MRO0_DevIndexE"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_11/PCIeFunctions/DevType3_SAT2_DevIndexF"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_14/PCIeFunctions/DevType3_TERM_DevIndex11"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_14/PCIeFunctions/DevType3_XHCI_DevIndex10"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_16/PCIeFunctions/DevType3_HEC1_DevIndex12"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_16/PCIeFunctions/DevType3_HEC2_DevIndex13"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_16/PCIeFunctions/DevType3_HEC3_DevIndex14"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_17/PCIeFunctions/DevType3_SAT1_DevIndex15"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_1C/PCIeFunctions/DevType3_RP01_DevIndex16"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_1C/PCIeFunctions/DevType3_RP05_DevIndex17"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_1C/PCIeFunctions/DevType3_RP06_DevIndex1A"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_1F/PCIeFunctions/DevType3_LPC0_DevIndex1B"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_1F/PCIeFunctions/DevType3_PMC1_DevIndex1C"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_1F/PCIeFunctions/DevType3_SMBS_DevIndex1D"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_1F/PCIeFunctions/DevType3_SPIC_DevIndex1E"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_02_00/PCIeFunctions/DevType3_VB00_DevIndex18"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_03_00/PCIeFunctions/DevType3_OVDL_DevIndex19"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_17_00/PCIeFunctions/DevType3_DMMY_DevIndex1F"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_17_02/PCIeFunctions/DevType3_BR1A_DevIndex20"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_17_04/PCIeFunctions/DevType3_BR1C_DevIndex21"
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
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_50_00/PCIeFunctions/DevType3_DMMY_DevIndex22"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_50_02/PCIeFunctions/DevType3_BR2A_DevIndex23"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_51_00/PCIeFunctions/DevType3_SL03_DevIndex8"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_89_00/PCIeFunctions/DevType3_DMMY_DevIndex24"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_C2_00/PCIeFunctions/DevType3_DMMY_DevIndex25"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_C2_02/PCIeFunctions/DevType3_BR5A_DevIndex26"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_C2_03/PCIeFunctions/DevType3_BR5B_DevIndex27"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_C3_00/PCIeFunctions/DevType3_SL05_DevIndexA"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_C4_00/PCIeFunctions/DevType3_SL06_DevIndexB"
    }
  ],
  "PCIeFunctions@odata.count": 40,
  "PartNumber": "PA-00371-003",
  "PowerRestorePolicy": "AlwaysOn",
  "PowerState": "On",
  "ProcessorSummary": {
    "Count": 1,
    "Model": "Intel(R) Xeon(R) Gold 6338N CPU @ 2.20GHz, 4000 Mhz, 32 Core(s), 64 Logical Processor(s)",
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
  "SerialNumber": "20741213N074",
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
[XXXXXX@welktxefnce-h-pe1util-vm01 archive_1]$
```

```sh 
curl -gsk -u XXXXXX:XXXXXX -X GET https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Managers/Self | jq .
```

```log
[XXXXXX@welktxefnce-h-pe1util-vm01 archive_1]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Managers/Self | jq .

{
  "@odata.context": "/redfish/v1/$metadata#Manager.Manager",
  "@odata.etag": "\"1702332298\"",
  "@odata.id": "/redfish/v1/Managers/Self",
  "@odata.type": "#Manager.v1_6_0.Manager",
  "Actions": {
    "#Manager.Reset": {
      "@Redfish.ActionInfo": "/redfish/v1/Managers/Self/ResetActionInfo",
      "@Redfish.OperationApplyTimeSupport": {
        "@odata.type": "#Settings.v1_2_2.OperationApplyTimeSupport",
        "MaintenanceWindowDurationInSeconds": 600,
        "MaintenanceWindowResource": {
          "@odata.id": "/redfish/v1/Managers/Self"
        },
        "SupportedValues": [
          "Immediate",
          "AtMaintenanceWindowStart"
        ]
      },
      "target": "/redfish/v1/Managers/Self/Actions/Manager.Reset"
    },
    "Oem": {
      "#AMIManager.RedfishDBReset": {
        "@Redfish.ActionInfo": "/redfish/v1/Managers/Self/Oem/RedfishDBResetActionInfo",
        "target": "/redfish/v1/Managers/Self/Actions/Oem/AMIManager.RedfishDBReset"
      },
      "#AMIVirtualMedia.ConfigureCDInstance": {
        "@Redfish.ActionInfo": "/redfish/v1/Managers/Self/Oem/ConfigureCDInstanceActionInfo",
        "target": "/redfish/v1/Managers/Self/Actions/Oem/AMIVirtualMedia.ConfigureCDInstance"
      },
      "#AMIVirtualMedia.EnableRMedia": {
        "@Redfish.ActionInfo": "/redfish/v1/Managers/Self/Oem/EnableRMediaActionInfo",
        "target": "/redfish/v1/Managers/Self/Actions/Oem/AMIVirtualMedia.EnableRMedia"
      }
    }
  },
  "CommandShell": {
    "ConnectTypesSupported": [
      "IPMI",
      "SSH"
    ],
    "MaxConcurrentSessions": 36,
    "ServiceEnabled": true
  },
  "DateTime": "2023-12-11T22:14:32-00:00",
  "DateTimeLocalOffset": "-00:00",
  "Description": "BMC",
  "EthernetInterfaces": {
    "@odata.id": "/redfish/v1/Managers/Self/EthernetInterfaces"
  },
  "FirmwareVersion": "0.45.00",
  "GraphicalConsole": {
    "ConnectTypesSupported": [
      "KVMIP"
    ],
    "MaxConcurrentSessions": 4,
    "ServiceEnabled": true
  },
  "HostInterfaces": {
    "@odata.id": "/redfish/v1/Managers/Self/HostInterfaces"
  },
  "Id": "Self",
  "Links": {
    "ManagerInChassis": {
      "@odata.id": "/redfish/v1/Chassis/Self"
    }
  },
  "LogServices": {
    "@odata.id": "/redfish/v1/Managers/Self/LogServices"
  },
  "ManagerDiagnosticData": {
    "@odata.id": "/redfish/v1/Managers/Self/ManagerDiagnosticData"
  },
  "ManagerType": "BMC",
  "Model": "43553231270",
  "Name": "Manager",
  "NetworkProtocol": {
    "@odata.id": "/redfish/v1/Managers/Self/NetworkProtocol"
  },
  "Oem": {
    "Ami": {
      "@odata.type": "#AMIManager.v1_0_0.AMIManager",
      "ManagerServiceInfo": {
        "CommandShellServiceInfo": {
          "IPMI": {
            "MaxConcurrentSessions": 36
          }
        },
        "Links": {
          "NetworkProtocol": {
            "@odata.id": "/redfish/v1/Managers/Self/NetworkProtocol"
          }
        }
      },
      "VirtualMedia": {
        "CDInstances": 4,
        "RMediaStatus": "Enabled"
      }
    },
    "IEEE8021X": {
      "@odata.id": "/redfish/v1/Managers/Self/Oem/IEEE8021X"
    }
  },
  "PowerState": "On",
  "Redundancy@odata.count": 0,
  "SerialConsole": {
    "ConnectTypesSupported": [
      "IPMI"
    ],
    "MaxConcurrentSessions": 1,
    "ServiceEnabled": true
  },
  "SerialInterfaces": {
    "@odata.id": "/redfish/v1/Managers/Self/SerialInterfaces"
  },
  "ServiceEntryPointUUID": "5a544443-6f10-0020-6265-d42066696c6c",
  "Status": {
    "Health": "OK",
    "State": "Enabled"
  },
  "Syslog": {
    "@odata.id": "/redfish/v1/Managers/Self/Syslog"
  },
  "UUID": "5a544443-6f10-0020-6265-d42066696c6c",
  "VirtualMedia": {
    "@odata.id": "/redfish/v1/Managers/Self/VirtualMedia"
  }
}
[XXXXXX@welktxefnce-h-pe1util-vm01 archive_1]$
```


### Iteration 2 of 10

Installed .45, log is kept seperate from this file.

### Redfish commands after .45 bmc installation 
### 
```sh 
curl -gsk -u XXXXXX:XXXXXX -X GET https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Systems/Self | jq .
```

```log
[XXXXXX@welktxefnce-h-pe1util-vm01 archive_7]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Systems/Self | jq .

{
  "@Redfish.Settings": {
    "@odata.type": "#Settings.v1_2_2.Settings",
    "SettingsObject": {
      "@odata.id": "/redfish/v1/Systems/Self/SD"
    }
  },
  "@odata.context": "/redfish/v1/$metadata#ComputerSystem.ComputerSystem",
  "@odata.etag": "\"1702333913\"",
  "@odata.id": "/redfish/v1/Systems/Self",
  "@odata.type": "#ComputerSystem.v1_8_0.ComputerSystem",
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
        "Nmi",
        "On",
        "ForceOff",
        "ForceRestart",
        "GracefulShutdown"
      ],
      "target": "/redfish/v1/Systems/Self/Actions/ComputerSystem.Reset"
    }
  },
  "AssetTag": "PA-00371-00320741213N074",
  "Bios": {
    "@odata.id": "/redfish/v1/Systems/Self/Bios"
  },
  "BiosVersion": "0.23",
  "Boot": {
    "BootNext": null,
    "BootOptions": {
      "@odata.id": "/redfish/v1/Systems/Self/BootOptions"
    },
    "BootOrder": [
      "Boot0000",
      "Boot0003",
      "Boot0004",
      "Boot0005",
      "Boot0006",
      "Boot0007",
      "Boot0008",
      "Boot0009",
      "Boot0002",
      "Boot000A"
    ],
    "BootOrderPropertySelection": "BootOrder",
    "BootSourceOverrideEnabled": "Disabled",
    "BootSourceOverrideEnabled@Redfish.AllowableValues": [
      "Disabled",
      "Once",
      "Continuous"
    ],
    "BootSourceOverrideMode": null,
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
  "HostName": "welktxef-931887-rz-le2pts6-021",
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
  "Name": "Proteus I_Mix",
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
                "CERTIFICATE": 1
              },
              {
                "CPU": 1
              },
              {
                "PCIE": 1
              },
              {
                "DIMM": 1
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
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_00/PCIeFunctions/DevType3_DMMY_DevIndexC"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_00/PCIeFunctions/DevType3_SLT4_DevIndex9"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_02/PCIeFunctions/DevType3_NRP0_DevIndexD"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_11/PCIeFunctions/DevType3_MRO0_DevIndexE"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_11/PCIeFunctions/DevType3_SAT2_DevIndexF"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_14/PCIeFunctions/DevType3_TERM_DevIndex11"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_14/PCIeFunctions/DevType3_XHCI_DevIndex10"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_16/PCIeFunctions/DevType3_HEC1_DevIndex12"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_16/PCIeFunctions/DevType3_HEC2_DevIndex13"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_16/PCIeFunctions/DevType3_HEC3_DevIndex14"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_17/PCIeFunctions/DevType3_SAT1_DevIndex15"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_1C/PCIeFunctions/DevType3_RP01_DevIndex16"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_1C/PCIeFunctions/DevType3_RP05_DevIndex17"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_1C/PCIeFunctions/DevType3_RP06_DevIndex1A"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_1F/PCIeFunctions/DevType3_LPC0_DevIndex1B"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_1F/PCIeFunctions/DevType3_PMC1_DevIndex1C"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_1F/PCIeFunctions/DevType3_SMBS_DevIndex1D"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_00_1F/PCIeFunctions/DevType3_SPIC_DevIndex1E"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_02_00/PCIeFunctions/DevType3_VB00_DevIndex18"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_03_00/PCIeFunctions/DevType3_OVDL_DevIndex19"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_17_00/PCIeFunctions/DevType3_DMMY_DevIndex1F"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_17_02/PCIeFunctions/DevType3_BR1A_DevIndex20"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_17_04/PCIeFunctions/DevType3_BR1C_DevIndex21"
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
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_50_00/PCIeFunctions/DevType3_DMMY_DevIndex22"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_50_02/PCIeFunctions/DevType3_BR2A_DevIndex23"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_51_00/PCIeFunctions/DevType3_SL03_DevIndex8"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_89_00/PCIeFunctions/DevType3_DMMY_DevIndex24"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_C2_00/PCIeFunctions/DevType3_DMMY_DevIndex25"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_C2_02/PCIeFunctions/DevType3_BR5A_DevIndex26"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_C2_03/PCIeFunctions/DevType3_BR5B_DevIndex27"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_C3_00/PCIeFunctions/DevType3_SL05_DevIndexA"
    },
    {
      "@odata.id": "/redfish/v1/Chassis/Self/PCIeDevices/00_C4_00/PCIeFunctions/DevType3_SL06_DevIndexB"
    }
  ],
  "PCIeFunctions@odata.count": 40,
  "PartNumber": "PA-00371-003",
  "PowerRestorePolicy": "AlwaysOn",
  "PowerState": "On",
  "ProcessorSummary": {
    "Count": 1,
    "Model": "Intel(R) Xeon(R) Gold 6338N CPU @ 2.20GHz, 4000 Mhz, 32 Core(s), 64 Logical Processor(s)",
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
  "SerialNumber": "20741213N074",
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
[XXXXXX@welktxefnce-h-pe1util-vm01 archive_7]$
[XXXXXX@welktxefnce-h-pe1util-vm01 archive_7]$
```

```sh 
curl -gsk -u XXXXXX:XXXXXX -X GET https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Managers/Self | jq .
```

```log
[XXXXXX@welktxefnce-h-pe1util-vm01 archive_7]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Managers/Self | jq .
{
  "@odata.context": "/redfish/v1/$metadata#Manager.Manager",
  "@odata.etag": "\"1702333913\"",
  "@odata.id": "/redfish/v1/Managers/Self",
  "@odata.type": "#Manager.v1_6_0.Manager",
  "Actions": {
    "#Manager.Reset": {
      "@Redfish.ActionInfo": "/redfish/v1/Managers/Self/ResetActionInfo",
      "@Redfish.OperationApplyTimeSupport": {
        "@odata.type": "#Settings.v1_2_2.OperationApplyTimeSupport",
        "MaintenanceWindowDurationInSeconds": 600,
        "MaintenanceWindowResource": {
          "@odata.id": "/redfish/v1/Managers/Self"
        },
        "SupportedValues": [
          "Immediate",
          "AtMaintenanceWindowStart"
        ]
      },
      "target": "/redfish/v1/Managers/Self/Actions/Manager.Reset"
    },
    "Oem": {
      "#AMIManager.RedfishDBReset": {
        "@Redfish.ActionInfo": "/redfish/v1/Managers/Self/Oem/RedfishDBResetActionInfo",
        "target": "/redfish/v1/Managers/Self/Actions/Oem/AMIManager.RedfishDBReset"
      },
      "#AMIVirtualMedia.ConfigureCDInstance": {
        "@Redfish.ActionInfo": "/redfish/v1/Managers/Self/Oem/ConfigureCDInstanceActionInfo",
        "target": "/redfish/v1/Managers/Self/Actions/Oem/AMIVirtualMedia.ConfigureCDInstance"
      },
      "#AMIVirtualMedia.EnableRMedia": {
        "@Redfish.ActionInfo": "/redfish/v1/Managers/Self/Oem/EnableRMediaActionInfo",
        "target": "/redfish/v1/Managers/Self/Actions/Oem/AMIVirtualMedia.EnableRMedia"
      }
    }
  },
  "CommandShell": {
    "ConnectTypesSupported": [
      "IPMI",
      "SSH"
    ],
    "MaxConcurrentSessions": 36,
    "ServiceEnabled": true
  },
  "DateTime": "2023-12-11T22:33:19-00:00",
  "DateTimeLocalOffset": "-00:00",
  "Description": "BMC",
  "EthernetInterfaces": {
    "@odata.id": "/redfish/v1/Managers/Self/EthernetInterfaces"
  },
  "FirmwareVersion": "0.45.00",
  "GraphicalConsole": {
    "ConnectTypesSupported": [
      "KVMIP"
    ],
    "MaxConcurrentSessions": 4,
    "ServiceEnabled": true
  },
  "HostInterfaces": {
    "@odata.id": "/redfish/v1/Managers/Self/HostInterfaces"
  },
  "Id": "Self",
  "Links": {
    "ManagerInChassis": {
      "@odata.id": "/redfish/v1/Chassis/Self"
    }
  },
  "LogServices": {
    "@odata.id": "/redfish/v1/Managers/Self/LogServices"
  },
  "ManagerDiagnosticData": {
    "@odata.id": "/redfish/v1/Managers/Self/ManagerDiagnosticData"
  },
  "ManagerType": "BMC",
  "Model": "43553231270",
  "Name": "Manager",
  "NetworkProtocol": {
    "@odata.id": "/redfish/v1/Managers/Self/NetworkProtocol"
  },
  "Oem": {
    "Ami": {
      "@odata.type": "#AMIManager.v1_0_0.AMIManager",
      "ManagerServiceInfo": {
        "CommandShellServiceInfo": {
          "IPMI": {
            "MaxConcurrentSessions": 36
          }
        },
        "Links": {
          "NetworkProtocol": {
            "@odata.id": "/redfish/v1/Managers/Self/NetworkProtocol"
          }
        }
      },
      "VirtualMedia": {
        "CDInstances": 4,
        "RMediaStatus": "Enabled"
      }
    },
    "IEEE8021X": {
      "@odata.id": "/redfish/v1/Managers/Self/Oem/IEEE8021X"
    }
  },
  "PowerState": "On",
  "Redundancy@odata.count": 0,
  "SerialConsole": {
    "ConnectTypesSupported": [
      "IPMI"
    ],
    "MaxConcurrentSessions": 1,
    "ServiceEnabled": true
  },
  "SerialInterfaces": {
    "@odata.id": "/redfish/v1/Managers/Self/SerialInterfaces"
  },
  "ServiceEntryPointUUID": "5a544443-6f10-0020-6265-d42066696c6c",
  "Status": {
    "Health": "OK",
    "State": "Enabled"
  },
  "Syslog": {
    "@odata.id": "/redfish/v1/Managers/Self/Syslog"
  },
  "UUID": "5a544443-6f10-0020-6265-d42066696c6c",
  "VirtualMedia": {
    "@odata.id": "/redfish/v1/Managers/Self/VirtualMedia"
  }
}
[XXXXXX@welktxefnce-h-pe1util-vm01 archive_7]$
```

