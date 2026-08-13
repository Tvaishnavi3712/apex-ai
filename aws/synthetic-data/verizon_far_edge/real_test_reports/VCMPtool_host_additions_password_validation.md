# VCMPtool Lab instance
# Added hosts to alerts and metrics collection, needed validation of creds on BMCs
# James Patchett 9/25/25

## ZT Servers
2607:f160:10:80b1:ce:40a:0:e003  welktxef-931856-rz-le0pts6-004
2607:f160:10:9249:ce:40a:0:e01f  welktxef-931883-rz-le0trtn-031

## HPE Servers
2607:f160:0010:8803:ce:40a:0:e004  welktxsr-931883-rh-le093s6-022

## DELL  
2607:f160:0010:823a:ce:40a:0:e00f 7.10.30.05 "hostname not set"
2607:f160:10:4066:ce:40a:0:e001 7.10.30.05 welktxrh-d931857-rd-le08620-001
2607:f160:10:823a:ce:40a:0:e010 7.20.30.51 "hostname not set"


## ZT Servers Creds
```txt
Username:  XXXXXX
Passwword: XXXXXX
```
## DELL Servers Creds
```txt
Username:  root
Passwword: XXXXXX
```


### ZT servers cred validation via redfish
### 2607:f160:10:80b1:ce:40a:0:e003
### 2607:f160:10:9249:ce:40a:0:e01f

```sh
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ curl -k -u XXXXXX:XXXXXX https://[2607:f160:10:80b1:ce:40a:0:e003]/redfish/v1/Systems | jq .
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   753  100   753    0     0   1647      0 --:--:-- --:--:-- --:--:--  1647
{
  "@Redfish.CollectionCapabilities": {
    "@odata.type": "#CollectionCapabilities.v1_2_0.CollectionCapabilities",
    "Capabilities": [
      {
        "CapabilitiesObject": {
          "@odata.id": "/redfish/v1/Systems/Capabilities"
        },
        "Links": {
          "RelatedItem": [
            {
              "@odata.id": "/redfish/v1/CompositionService/ResourceZones/1"
            }
          ],
          "TargetCollection": {
            "@odata.id": "/redfish/v1/Systems"
          }
        },
        "UseCase": "ComputerSystemComposition"
      }
    ]
  },
  "@odata.context": "/redfish/v1/$metadata#ComputerSystemCollection.ComputerSystemCollection",
  "@odata.etag": "\"1758554478\"",
  "@odata.id": "/redfish/v1/Systems",
  "@odata.type": "#ComputerSystemCollection.ComputerSystemCollection",
  "Description": "Collection of Computer Systems",
  "Members": [
    {
      "@odata.id": "/redfish/v1/Systems/Self"
    }
  ],
  "Members@odata.count": 1,
  "Name": "Systems Collection"
}
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ curl -k -u XXXXXX:XXXXXX https://[2607:f160:10:9249:ce:40a:0:e01f]/redfish/v1/Systems | jq .
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   753  100   753    0     0   2468      0 --:--:-- --:--:-- --:--:--  2468
{
  "@Redfish.CollectionCapabilities": {
    "@odata.type": "#CollectionCapabilities.v1_2_0.CollectionCapabilities",
    "Capabilities": [
      {
        "CapabilitiesObject": {
          "@odata.id": "/redfish/v1/Systems/Capabilities"
        },
        "Links": {
          "RelatedItem": [
            {
              "@odata.id": "/redfish/v1/CompositionService/ResourceZones/1"
            }
          ],
          "TargetCollection": {
            "@odata.id": "/redfish/v1/Systems"
          }
        },
        "UseCase": "ComputerSystemComposition"
      }
    ]
  },
  "@odata.context": "/redfish/v1/$metadata#ComputerSystemCollection.ComputerSystemCollection",
  "@odata.etag": "\"1758154751\"",
  "@odata.id": "/redfish/v1/Systems",
  "@odata.type": "#ComputerSystemCollection.ComputerSystemCollection",
  "Description": "Collection of Computer Systems",
  "Members": [
    {
      "@odata.id": "/redfish/v1/Systems/Self"
    }
  ],
  "Members@odata.count": 1,
  "Name": "Systems Collection"
}
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$

```

### HPe servers cred validation via redfish
### 2607:f160:0010:8803:ce:40a:0:e004

```sh
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ curl -k -u XXXXXX:XXXXXX https://[2607:f160:0010:8803:ce:40a:0:e004]/redfish/v1/Systems | jq .
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   362    0   362    0     0    836      0 --:--:-- --:--:-- --:--:--   836
{
  "@odata.context": "/redfish/v1/$metadata#ComputerSystemCollection.ComputerSystemCollection",
  "@odata.etag": "W/\"AA6D42B0\"",
  "@odata.id": "/redfish/v1/Systems",
  "@odata.type": "#ComputerSystemCollection.ComputerSystemCollection",
  "Description": "Computer Systems view",
  "Name": "Computer Systems",
  "Members": [
    {
      "@odata.id": "/redfish/v1/Systems/1"
    }
  ],
  "Members@odata.count": 1
}
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ curl -k -u XXXXXX:XXXXXX https://[2607:f160:0010:8803:ce:40a:0:e004]/redfish/v1/Systems/1 | jq .
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100  8440    0  8440    0     0  11593      0 --:--:-- --:--:-- --:--:-- 11577
{
  "@odata.context": "/redfish/v1/$metadata#ComputerSystem.ComputerSystem",
  "@odata.etag": "W/\"4A83864F\"",
  "@odata.id": "/redfish/v1/Systems/1",
  "@odata.type": "#ComputerSystem.v1_18_0.ComputerSystem",
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
      "target": "/redfish/v1/Systems/1/Actions/ComputerSystem.Reset"
    }
  },
  "AssetTag": "",
  "Bios": {
    "@odata.id": "/redfish/v1/systems/1/bios"
  },
  "BiosVersion": "H11 v2.50 (04/22/2025)",
  "Boot": {
    "BootOptions": {
      "@odata.id": "/redfish/v1/Systems/1/BootOptions"
    },
    "BootOrder": [
      "Boot0022",
      "Boot000D",
      "Boot0010",
      "Boot0012",
      "Boot0011",
      "Boot0013",
      "Boot0018",
      "Boot001A",
      "Boot0014",
      "Boot0016",
      "Boot001C",
      "Boot001D",
      "Boot001F",
      "Boot0019",
      "Boot001E",
      "Boot001B",
      "Boot0017",
      "Boot0015",
      "Boot000E",
      "Boot000F"
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
      "HD(2,GPT,D3E74043-33F3-4534-8203-8775F4E9FE0F,0x3A98800,0x96000)/\\EFI\\BOOT\\bootx64.efi",
      "UsbClass(0xFFFF,0xFFFF,0xFF,0xFF,0xFF)",
      "PciRoot(0x0)/Pci(0xF,0x0)/Pci(0x0,0x0)/MAC(5CED8CEFAE42,0x1)/IPv4(0.0.0.0)/Uri()",
      "PciRoot(0x0)/Pci(0xF,0x0)/Pci(0x0,0x0)/MAC(5CED8CEFAE42,0x1)/IPv4(0.0.0.0)",
      "PciRoot(0x0)/Pci(0xF,0x0)/Pci(0x0,0x0)/MAC(5CED8CEFAE42,0x1)/IPv6(0000:0000:0000:0000:0000:0000:0000:0000)/Uri()",
      "PciRoot(0x0)/Pci(0xF,0x0)/Pci(0x0,0x0)/MAC(5CED8CEFAE42,0x1)/IPv6(0000:0000:0000:0000:0000:0000:0000:0000)",
      "PciRoot(0x2)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B91438FC,0x1)/IPv4(0.0.0.0)/Uri()",
      "PciRoot(0x2)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B91438FC,0x1)/IPv4(0.0.0.0)",
      "PciRoot(0x1)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B91438EC,0x1)/IPv4(0.0.0.0)/Uri()",
      "PciRoot(0x1)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B91438EC,0x1)/IPv4(0.0.0.0)",
      "PciRoot(0x5)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B914398C,0x1)/IPv4(0.0.0.0)/Uri()",
      "PciRoot(0x5)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B914398C,0x1)/IPv6(0000:0000:0000:0000:0000:0000:0000:0000)/Uri()",
      "PciRoot(0x5)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B914398C,0x1)/IPv6(0000:0000:0000:0000:0000:0000:0000:0000)",
      "PciRoot(0x2)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B91438FC,0x1)/IPv6(0000:0000:0000:0000:0000:0000:0000:0000)/Uri()",
      "PciRoot(0x5)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B914398C,0x1)/IPv4(0.0.0.0)",
      "PciRoot(0x2)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B91438FC,0x1)/IPv6(0000:0000:0000:0000:0000:0000:0000:0000)",
      "PciRoot(0x1)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B91438EC,0x1)/IPv6(0000:0000:0000:0000:0000:0000:0000:0000)",
      "PciRoot(0x1)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B91438EC,0x1)/IPv6(0000:0000:0000:0000:0000:0000:0000:0000)/Uri()",
      "PciRoot(0x0)/Pci(0x10,0x0)/Pci(0x0,0x0)/NVMe(0x1,00-00-00-00-00-00-00-00)",
      "PciRoot(0x0)/Pci(0x11,0x0)/Pci(0x0,0x0)/NVMe(0x1,00-00-00-00-00-00-00-00)"
    ]
  },
  "BootProgress": {
    "LastBootTimeSeconds": 103,
    "LastState": "OSRunning"
  },
  "EthernetInterfaces": {
    "@odata.id": "/redfish/v1/Systems/1/EthernetInterfaces"
  },
  "HostName": "welktxsr-931883-rh-le093s6-022",
  "Links": {
    "ManagedBy": [
      {
        "@odata.id": "/redfish/v1/Managers/1"
      }
    ],
    "Chassis": [
      {
        "@odata.id": "/redfish/v1/Chassis/1"
      }
    ]
  },
  "LocationIndicatorActive": false,
  "LogServices": {
    "@odata.id": "/redfish/v1/Systems/1/LogServices"
  },
  "Manufacturer": "HPE",
  "Memory": {
    "@odata.id": "/redfish/v1/Systems/1/Memory"
  },
  "MemoryDomains": {
    "@odata.id": "/redfish/v1/Systems/1/MemoryDomains"
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
    "@odata.id": "/redfish/v1/Systems/1/NetworkInterfaces"
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
          "target": "/redfish/v1/Systems/1/Actions/Oem/Hpe/HpeComputerSystemExt.PowerButton"
        },
        "#HpeComputerSystemExt.RestoreManufacturingDefaults": {
          "target": "/redfish/v1/Systems/1/Actions/Oem/Hpe/HpeComputerSystemExt.RestoreManufacturingDefaults"
        },
        "#HpeComputerSystemExt.RestoreSystemDefaults": {
          "target": "/redfish/v1/Systems/1/Actions/Oem/Hpe/HpeComputerSystemExt.RestoreSystemDefaults"
        },
        "#HpeComputerSystemExt.SecureSystemErase": {
          "target": "/redfish/v1/Systems/1/Actions/Oem/Hpe/HpeComputerSystemExt.SecureSystemErase"
        },
        "#HpeComputerSystemExt.ServerIntelligentDiagnosticsMode": {
          "target": "/redfish/v1/Systems/1/Actions/Oem/Hpe/HpeComputerSystemExt.ServerIntelligentDiagnosticsMode"
        },
        "#HpeComputerSystemExt.ServerSafeMode": {
          "target": "/redfish/v1/Systems/1/Actions/Oem/Hpe/HpeComputerSystemExt.ServerSafeMode"
        },
        "#HpeComputerSystemExt.SystemReset": {
          "ResetType@Redfish.AllowableValues": [
            "ColdBoot",
            "AuxCycle"
          ],
          "target": "/redfish/v1/Systems/1/Actions/Oem/Hpe/HpeComputerSystemExt.SystemReset"
        }
      },
      "AggregateHealthStatus": {
        "AgentlessManagementService": "Unavailable",
        "AggregateServerHealth": "Critical",
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
            "Health": "Critical"
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
          "Date": "04/22/2025",
          "Family": "H11",
          "VersionString": "H11 v2.50 (04/22/2025)"
        },
        "Current": {
          "Date": "04/22/2025",
          "Family": "H11",
          "VersionString": "H11 v2.50 (04/22/2025)"
        },
        "UefiClass": 3
      },
      "CriticalTempRemainOff": true,
      "CurrentPowerOnTimeSeconds": 6196171,
      "DeviceDiscoveryComplete": {
        "AMSDeviceDiscovery": "NoAMS",
        "DeviceDiscovery": "vMainDeviceDiscoveryComplete",
        "ServerFirmwareInventoryComplete": true
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
          "@odata.id": "/redfish/v1/Systems/1/PCISlots"
        },
        "USBPorts": {
          "@odata.id": "/redfish/v1/Systems/1/USBPorts"
        },
        "USBDevices": {
          "@odata.id": "/redfish/v1/Systems/1/USBDevices"
        },
        "EthernetInterfaces": {
          "@odata.id": "/redfish/v1/Systems/1/EthernetInterfaces"
        },
        "WorkloadPerformanceAdvisor": {
          "@odata.id": "/redfish/v1/Systems/1/WorkloadPerformanceAdvisor"
        },
        "SecureEraseReportService": {
          "@odata.id": "/redfish/v1/Systems/1/SecureEraseReportService"
        },
        "PCIDevices": [
          {
            "@odata.id": "/redfish/v1/Systems/1/PCIDevices"
          }
        ]
      },
      "PCAPartNumber": "P48462-E02",
      "PCASerialNumber": "PYHRC0ALMIY03L",
      "PostDiscoveryCompleteTimeStamp": "2025-07-16T00:46:47Z",
      "PostDiscoveryMode": "Auto",
      "PostMode": "Normal",
      "PostState": "FinishedPost",
      "PowerAutoOn": "Restore",
      "PowerOnDelay": "Minimum",
      "PowerOnMinutes": 584238,
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
      "ServerFQDN": "welktxsr-931883-rh-le093s6-022.faredge.vzwops.com",
      "ServerIntelligentDiagnosticsModeEnabled": false,
      "ServerSafeModeEnabled": false,
      "SystemROMAndiLOEraseComponentStatus": {
        "BIOSSettingsEraseStatus": "Idle",
        "iLOSettingsEraseStatus": "Idle"
      },
      "SystemROMAndiLOEraseStatus": "Idle",
      "SystemUsage": {
        "AvgCPU0Freq": 54,
        "CPU0Power": 69,
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
    "@odata.id": "/redfish/v1/Systems/1/Processors"
  },
  "SKU": "P48541-B21",
  "SecureBoot": {
    "@odata.id": "/redfish/v1/Systems/1/SecureBoot"
  },
  "SerialNumber": "MXQ3460902",
  "Status": {
    "Health": "Warning",
    "HealthRollup": "Warning",
    "State": "Enabled"
  },
  "Storage": {
    "@odata.id": "/redfish/v1/Systems/1/Storage"
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
  "UUID": "35383450-3134-584D-5133-343630393032"
}
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$


```

### DELL servers cred validation via redfish
### 2607:f160:0010:823a:ce:40a:0:e00f 
### 2607:f160:10:4066:ce:40a:0:e001 
### 2607:f160:10:823a:ce:40a:0:e010 

```sh
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ curl -k -u XXXXXX:XXXXXX https://[2607:f160:0010:823a:ce:40a:0:e00f]/redfish/v1/Systems | jq .
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   366  100   366    0     0    585      0 --:--:-- --:--:-- --:--:--   584
{
  "@odata.context": "/redfish/v1/$metadata#ComputerSystemCollection.ComputerSystemCollection",
  "@odata.id": "/redfish/v1/Systems",
  "@odata.type": "#ComputerSystemCollection.ComputerSystemCollection",
  "Description": "Collection of Computer Systems",
  "Members": [
    {
      "@odata.id": "/redfish/v1/Systems/System.Embedded.1"
    }
  ],
  "Members@odata.count": 1,
  "Name": "Computer System Collection"
}
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ curl -k -u XXXXXX:XXXXXX https://[2607:f160:10:4066:ce:40a:0:e001]/redfish/v1/Systems | jq .
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   366  100   366    0     0    610      0 --:--:-- --:--:-- --:--:--   610
{
  "@odata.context": "/redfish/v1/$metadata#ComputerSystemCollection.ComputerSystemCollection",
  "@odata.id": "/redfish/v1/Systems",
  "@odata.type": "#ComputerSystemCollection.ComputerSystemCollection",
  "Description": "Collection of Computer Systems",
  "Members": [
    {
      "@odata.id": "/redfish/v1/Systems/System.Embedded.1"
    }
  ],
  "Members@odata.count": 1,
  "Name": "Computer System Collection"
}
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ curl -k -u XXXXXX:XXXXXX https://[2607:f160:10:823a:ce:40a:0:e010]/redfish/v1/Systems | jq .
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   366  100   366    0     0    213      0  0:00:01  0:00:01 --:--:--   213
{
  "@odata.context": "/redfish/v1/$metadata#ComputerSystemCollection.ComputerSystemCollection",
  "@odata.id": "/redfish/v1/Systems",
  "@odata.type": "#ComputerSystemCollection.ComputerSystemCollection",
  "Description": "Collection of Computer Systems",
  "Members": [
    {
      "@odata.id": "/redfish/v1/Systems/System.Embedded.1"
    }
  ],
  "Members@odata.count": 1,
  "Name": "Computer System Collection"
}
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$
```
