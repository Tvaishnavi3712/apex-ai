# HPE ILO6 1.57 BIOS H11 v1.11
# HPE Sapphire Rapids E930t server
# 4/24/24 James Patchett - MTCE Lab VCPfe
# BMC Playbook MEAKV-1750

## welktxsr-931883-rh-le093s6-012
ILO:  2607:f160:0010:8803:ce:40a:0:e001
OAM:  2607:f160:0010:8803:ce:40a:0:f401

## Server has been reset to factory defaults with ilo6 decommissioning process (in lifecyclemanagment)

## Anil and Ashish has configured the ILO6 IPV6 on the box after system was factory reset.

## Lets look at a few things at factory defaults before running the bmc playbook against the host.

## Bios settings:

```log
(hpe_fw) [XXXXXX@welktxefnce-h-pe1util-vm01 ZT-Triton-BMC-update-Redfish-v2.27.00-x86_64_20231027]$ echo $ILO
2607:f160:10:8803:ce:40a:0:e001
(hpe_fw) [XXXXXX@welktxefnce-h-pe1util-vm01 ZT-Triton-BMC-update-Redfish-v2.27.00-x86_64_20231027]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[$ILO]/redfish/v1/Systems/1/Bios | jq .
{
  "@Redfish.Settings": {
    "@odata.type": "#Settings.v1_0_0.Settings",
    "ETag": "",
    "Messages": [
      {
        "MessageId": "Base.1.0.Success"
      }
    ],
    "SettingsObject": {
      "@odata.id": "/redfish/v1/systems/1/bios/settings/"
    },
    "Time": null
  },
  "@odata.context": "/redfish/v1/$metadata#Bios.Bios",
  "@odata.etag": "W/\"0815D03B3A7CC5C5C53077B39FA56DBD\"",
  "@odata.id": "/redfish/v1/systems/1/bios/",
  "@odata.type": "#Bios.v1_0_4.Bios",
  "Actions": {
    "#Bios.ChangePassword": {
      "target": "/redfish/v1/systems/1/bios/Actions/Bios.ChangePasswords/"
    },
    "#Bios.ResetBios": {
      "target": "/redfish/v1/systems/1/bios/Actions/Bios.ResetBios/"
    }
  },
  "AttributeRegistry": "BiosAttributeRegistryH11.v1_1_11",
  "Attributes": {
    "AccessControlService": "Enabled",
    "AcpiHpet": "Enabled",
    "AcpiRootBridgePxm": "Enabled",
    "AcpiSlit": "Enabled",
    "AdjSecPrefetch": "Enabled",
    "AdminEmail": "",
    "AdminName": "",
    "AdminOtherInfo": "",
    "AdminPhone": "",
    "AdvCrashDumpMode": "Disabled",
    "AdvancedMemProtection": "AdvancedEcc",
    "AllowLoginWithIlo": "Disabled",
    "AssetTagProtection": "Unlocked",
    "AutoPowerOn": "RestoreLastState",
    "BootOrderPolicy": "RetryIndefinitely",
    "CollabPowerControl": "Enabled",
    "ConsistentDevNaming": "LomsAndSlots",
    "CustomPostMessage": "",
    "DaylightSavingsTime": "DaylightSavingsTimeDisabled",
    "DcuIpPrefetcher": "Enabled",
    "DcuStreamPrefetcher": "Enabled",
    "DeadBlockPredictor": "Disabled",
    "Dhcpv4": "Enabled",
    "DisableDynamicLoadlineSwitch": "NotDisableDLLSwitch",
    "DramRapl": 0,
    "DramRaplLimit": "Disabled",
    "DramRaplReport": "Enabled",
    "DynamicIntelSpeedSelectMode": "Disabled",
    "DynamicPowerCapping": "Disabled",
    "EmbSata1Aspm": "Disabled",
    "EmbSata1Enable": "Auto",
    "EmbSata1PCIeOptionROM": "Enabled",
    "EmbSata2Aspm": "Disabled",
    "EmbSata2Enable": "Auto",
    "EmbSata2PCIeOptionROM": "Enabled",
    "EmbSata3Aspm": "Disabled",
    "EmbSata3Enable": "Auto",
    "EmbSata3PCIeOptionROM": "Enabled",
    "EmbVideoConnection": "Auto",
    "EmbeddedDiagnostics": "Enabled",
    "EmbeddedIpxe": "Enabled",
    "EmbeddedSata": "Ahci",
    "EmbeddedSerialPort": "Com2Irq3",
    "EmbeddedUefiShell": "Enabled",
    "EmsConsole": "Disabled",
    "EnabledCoresPerProc": 0,
    "EnergyEfficientTurbo": "Enabled",
    "EnergyPerfBias": "BalancedPerf",
    "EnergyPerformancePreference": "Disabled",
    "EppProfile": "Disabled",
    "EraseUserDefaults": "No",
    "ExtendedAmbientTemp": "Disabled",
    "ExtendedMemTest": "Disabled",
    "F11BootMenu": "Enabled",
    "FCScanPolicy": "CardConfig",
    "FanFailPolicy": "Shutdown",
    "FanInstallReq": "EnableMessaging",
    "HourFormat": "24Hours",
    "HttpSupport": "Auto",
    "HwPrefetcher": "Enabled",
    "IODCConfiguration": "Auto",
    "IntelDmiLinkFreq": "Auto",
    "IntelNicDmaChannels": "Enabled",
    "IntelPchVmdSupport": "Disabled",
    "IntelPriorityCorePower": "Disabled",
    "IntelProcVtd": "Enabled",
    "IntelSpeedSelectConfigLevel": "Base",
    "IntelTxt": "Disabled",
    "IntelVmdDirectAssign": "VmdDirectAssignEnabledAll",
    "IntelVmdSupport": "Disabled",
    "IntelVrocSupport": "None",
    "IntelligentProvisioning": "Enabled",
    "IoatSnoopResponseHoldOff": "10",
    "IpmiWatchdogTimerAction": "PowerCycle",
    "IpmiWatchdogTimerStatus": "IpmiWatchdogTimerOff",
    "IpmiWatchdogTimerTimeout": "Timeout30Min",
    "Ipv4Address": "0.0.0.0",
    "Ipv4Gateway": "0.0.0.0",
    "Ipv4PrimaryDNS": "0.0.0.0",
    "Ipv4SubnetMask": "0.0.0.0",
    "Ipv6Address": "::",
    "Ipv6ConfigPolicy": "Automatic",
    "Ipv6Duid": "Auto",
    "Ipv6Gateway": "::",
    "Ipv6PrimaryDNS": "::",
    "IpxeAutoStartScriptLocation": "Auto",
    "IpxeBootOrder": "Disabled",
    "IpxeScriptAutoStart": "Disabled",
    "IpxeScriptVerification": "Disabled",
    "IpxeStartupUrl": "",
    "LLCDeadLineAllocation": "Enabled",
    "LlcPrefetch": "Disabled",
    "MaxMemBusFreqMHz": "Auto",
    "MaxPcieSpeed": "PerPortCtrl",
    "MemClearWarmReset": "Disabled",
    "MemFastTraining": "Enabled",
    "MemMirrorMode": "Full",
    "MemPatrolScrubbing": "Enabled",
    "MemRefreshRate": "Refreshx1",
    "MemoryConfigurationViolationReporting": "Enabled",
    "MemoryPermanentFaultDetect": "Enabled",
    "MemoryRemap": "NoAction",
    "MicrosoftSecuredCoreSupport": "Disabled",
    "MinProcIdlePkgState": "NoState",
    "MinProcIdlePower": "C6",
    "MixedPowerSupplyReporting": "Enabled",
    "MkTme": "Disabled",
    "NetworkBootRetry": "Enabled",
    "NetworkBootRetryCount": 20,
    "NicBoot1": "NetworkBoot",
    "Numa": "Enabled",
    "NumaGroupSizeOpt": "Flat",
    "NvmeOptionRom": "Enabled",
    "OmitBootDeviceEvent": "Disabled",
    "OptimizedPowerMode": "Enabled",
    "OsbLocalRemoteRead": "Auto",
    "PatrolScrubDuration": 24,
    "PchCrashLogFeature": "Disabled",
    "PciResourcePadding": "Disabled",
    "PciSlot17LinkSpeed": "Auto",
    "PciSlot1Aspm": "Disabled",
    "PciSlot1Bifurcation": "NoBifurcation",
    "PciSlot1Enable": "Auto",
    "PciSlot1LinkSpeed": "Auto",
    "PciSlot1OptionROM": "Enabled",
    "PciSlot2Aspm": "Disabled",
    "PciSlot2Bifurcation": "NoBifurcation",
    "PciSlot2Enable": "Auto",
    "PciSlot2LinkSpeed": "Auto",
    "PciSlot2OptionROM": "Enabled",
    "PciSlot3Aspm": "Disabled",
    "PciSlot3Bifurcation": "NoBifurcation",
    "PciSlot3Enable": "Auto",
    "PciSlot3LinkSpeed": "Auto",
    "PciSlot3OptionROM": "Enabled",
    "PcieHotPlugErrControl": "HotplugSurprise",
    "PcuPMax": 0,
    "PersistentMemAddressRangeScrub": "Enabled",
    "PersistentMemBackupPowerPolicy": "WaitForBackupPower",
    "PersistentMemNumaAffinity": "IsolatedNumaDomains",
    "PersistentMemScanMem": "Enabled",
    "PlatformCertificate": "Enabled",
    "PlatformRASPolicy": "FirmwareFirst",
    "PostAsr": "PostAsrOff",
    "PostAsrDelay": "Delay30Min",
    "PostBootProgress": "Disabled",
    "PostDiscoveryMode": "Auto",
    "PostF1Prompt": "Delayed20Sec",
    "PostScreenMode": "VerboseMode",
    "PostVideoSupport": "DisplayAll",
    "PowerButton": "Enabled",
    "PowerOnDelay": "NoDelay",
    "PowerRegulator": "DynamicPowerSavings",
    "PreBootNetwork": "Auto",
    "PrebootNetworkEnvPolicy": "Auto",
    "PrebootNetworkProxy": "",
    "ProcAes": "Enabled",
    "ProcHyperthreading": "Enabled",
    "ProcRapl": 0,
    "ProcTurbo": "Enabled",
    "ProcVirtualization": "Enabled",
    "ProcX2Apic": "Auto",
    "ProcessorConfigTDPLevel": "Normal",
    "ProcessorPhysicalAddress": "Limited",
    "ProcessorUuidControl": "LockDisable",
    "ProductId": "P48541-B21",
    "RedundantPowerSupplyGpuDomain": "BalancedMode",
    "RedundantPowerSupplySystemDomain": "BalancedMode",
    "RestoreDefaults": "No",
    "RestoreManufacturingDefaults": "No",
    "RomSelection": "CurrentRom",
    "SataSanitize": "Disabled",
    "SataSecureErase": "Disabled",
    "SaveUserDefaults": "No",
    "SciRasSupport": "Ghesv2Support",
    "SecStartBackupImage": "Disabled",
    "SecureBootStatus": "Disabled",
    "SerialConsoleBaudRate": "BaudRate115200",
    "SerialConsoleEmulation": "Vt100Plus",
    "SerialConsolePort": "Auto",
    "SerialNumber": "MXQ346090C",
    "SerialPortDtrSupport": "Disabled",
    "ServerAssetTag": "",
    "ServerConfigLockStatus": "Disabled",
    "ServerName": "",
    "ServerOtherInfo": "",
    "ServerPrimaryOs": "",
    "ServiceEmail": "",
    "ServiceName": "",
    "ServiceOtherInfo": "",
    "ServicePhone": "",
    "SetupBrowserSelection": "Auto",
    "SgxAutoMpRegistrationAgent": "Enabled",
    "SgxEnable": "Disabled",
    "SgxFactoryReset": "Disabled",
    "SgxLaunchControlPolicy": "IntelLocked",
    "SgxLePublicKeyHash0": "",
    "SgxLePublicKeyHash1": "",
    "SgxLePublicKeyHash2": "",
    "SgxLePublicKeyHash3": "",
    "SgxLePublicKeyWriteEnable": "Enabled",
    "SgxPrmrrSize": "2Gb",
    "Slot1EoiBroadcastSupport": "Disabled",
    "Slot1MctpBroadcastSupport": "Enabled",
    "Slot1NicBoot1": "NetworkBoot",
    "Slot1NicBoot2": "Disabled",
    "Slot1NicBoot3": "Disabled",
    "Slot1NicBoot4": "Disabled",
    "Slot2EoiBroadcastSupport": "Disabled",
    "Slot2MctpBroadcastSupport": "Enabled",
    "Slot2NicBoot1": "NetworkBoot",
    "Slot2NicBoot2": "Disabled",
    "Slot2NicBoot3": "Disabled",
    "Slot2NicBoot4": "Disabled",
    "Slot3EoiBroadcastSupport": "Disabled",
    "Slot3MctpBroadcastSupport": "Enabled",
    "Slot3NicBoot1": "NetworkBoot",
    "Slot3NicBoot2": "Disabled",
    "Slot3NicBoot3": "Disabled",
    "Slot3NicBoot4": "Disabled",
    "SnoopResponseHoldOff": "9",
    "Sriov": "Enabled",
    "StaleAtoS": "Auto",
    "SubNumaClustering": "Disabled",
    "TPM2EndorsementDisable": "Enabled",
    "TPM2StorageDisable": "Enabled",
    "ThermalConfig": "OptimalCooling",
    "ThermalShutdown": "Enabled",
    "TimeFormat": "Utc",
    "TimeZone": "Unspecified",
    "Tme": "Disabled",
    "TmeExclusiveBase": "",
    "TmeExclusiveLen": "",
    "Tpm20SoftwareInterfaceStatus": "Fifo",
    "Tpm2Operation": "NoAction",
    "TpmActivePcrs": "Sha256Sha384",
    "TpmChipId": "STMicroGen11",
    "TpmState": "PresentEnabled",
    "TpmUefiOpromMeasuring": "Enabled",
    "TpmVisibility": "Visible",
    "Tsx": "Enabled",
    "UefiSerialDebugLevel": "ErrorsOnly",
    "UefiShellBootOrder": "Disabled",
    "UefiShellPhysicalPresenceKeystroke": "Enabled",
    "UefiShellScriptVerification": "Disabled",
    "UefiShellStartup": "Disabled",
    "UefiShellStartupLocation": "Auto",
    "UefiShellStartupUrl": "",
    "UefiShellStartupUrlFromDhcp": "Disabled",
    "UefiVariableAccessFwControl": "Disabled",
    "UncoreFreqScaling": "Auto",
    "UncoreFrequencyMAX": 0,
    "UncoreFrequencyMIN": 0,
    "UrlBootFile": "",
    "UrlBootFile2": "",
    "UrlBootFile3": "",
    "UrlBootFile4": "",
    "UsbBoot": "Enabled",
    "UsbControl": "UsbEnabled",
    "UserDefaultsState": "Disabled",
    "UtilityLang": "English",
    "VirtualNuma": "Disabled",
    "VirtualSerialPort": "Com1Irq4",
    "VlanControl": "Disabled",
    "VlanId": 0,
    "VlanPriority": 0,
    "WakeOnLan": "Enabled",
    "WorkloadProfile": "GeneralPowerEfficientCompute",
    "iSCSISoftwareInitiator": "Enabled"
  },
  "Id": "bios",
  "Name": "BIOS Current Settings",
  "Oem": {
    "Hpe": {
      "@odata.type": "#HpeBiosExt.v2_0_0.HpeBiosExt",
      "Links": {
        "BaseConfigs": {
          "@odata.id": "/redfish/v1/systems/1/bios/oem/hpe/baseconfigs/"
        },
        "Boot": {
          "@odata.id": "/redfish/v1/systems/1/bios/oem/hpe/boot/"
        },
        "KmsConfig": {
          "@odata.id": "/redfish/v1/systems/1/bios/oem/hpe/kmsconfig/"
        },
        "Mappings": {
          "@odata.id": "/redfish/v1/systems/1/bios/oem/hpe/mappings/"
        },
        "ServerConfigLock": {
          "@odata.id": "/redfish/v1/systems/1/bios/oem/hpe/serverconfiglock/"
        },
        "TlsConfig": {
          "@odata.id": "/redfish/v1/systems/1/bios/oem/hpe/tlsconfig/"
        },
        "iScsi": {
          "@odata.id": "/redfish/v1/systems/1/bios/oem/hpe/iscsi/"
        }
      },
      "SettingsObject": {
        "UnmodifiedETag": "W/\"683C8082ECF5F7F7F78FC89B6C44744E\""
      }
    }
  }
}
(hpe_fw) [XXXXXX@welktxefnce-h-pe1util-vm01 ZT-Triton-BMC-update-Redfish-v2.27.00-x86_64_20231027]$

```

## I noticed after factory reset, the default is not to use vRAN workloadprofile... interesting

```log
 "WorkloadProfile": "GeneralPowerEfficientCompute",
```
## Looking at more system settings at default level

```log

(hpe_fw) [XXXXXX@welktxefnce-h-pe1util-vm01 ZT-Triton-BMC-update-Redfish-v2.27.00-x86_64_20231027]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[$ILO]/redfish/v1/Systems/1/ | jq .
{
  "@odata.context": "/redfish/v1/$metadata#ComputerSystem.ComputerSystem",
  "@odata.etag": "W/\"1E68B8AB\"",
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
      "UsbClass(0xFFFF,0xFFFF,0xFF,0xFF,0xFF)",
      "PciRoot(0x0)/Pci(0xF,0x0)/Pci(0x0,0x0)/MAC(5CED8CEFAE00,0x1)/IPv4(0.0.0.0)/Uri()",
      "PciRoot(0x0)/Pci(0xF,0x0)/Pci(0x0,0x0)/MAC(5CED8CEFAE00,0x1)/IPv4(0.0.0.0)",
      "PciRoot(0x0)/Pci(0xF,0x0)/Pci(0x0,0x0)/MAC(5CED8CEFAE00,0x1)/IPv6(0000:0000:0000:0000:0000:0000:0000:0000)/Uri()",
      "PciRoot(0x0)/Pci(0xF,0x0)/Pci(0x0,0x0)/MAC(5CED8CEFAE00,0x1)/IPv6(0000:0000:0000:0000:0000:0000:0000:0000)",
      "PciRoot(0x2)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B9143BC4,0x1)/IPv4(0.0.0.0)/Uri()",
      "PciRoot(0x2)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B9143BC4,0x1)/IPv4(0.0.0.0)",
      "PciRoot(0x1)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B91438B0,0x1)/IPv4(0.0.0.0)/Uri()",
      "PciRoot(0x1)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B91438B0,0x1)/IPv4(0.0.0.0)",
      "PciRoot(0x5)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B9143A00,0x1)/IPv4(0.0.0.0)/Uri()",
      "PciRoot(0x5)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B9143A00,0x1)/IPv6(0000:0000:0000:0000:0000:0000:0000:0000)/Uri()",
      "PciRoot(0x5)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B9143A00,0x1)/IPv6(0000:0000:0000:0000:0000:0000:0000:0000)",
      "PciRoot(0x2)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B9143BC4,0x1)/IPv6(0000:0000:0000:0000:0000:0000:0000:0000)/Uri()",
      "PciRoot(0x5)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B9143A00,0x1)/IPv4(0.0.0.0)",
      "PciRoot(0x2)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B9143BC4,0x1)/IPv6(0000:0000:0000:0000:0000:0000:0000:0000)",
      "PciRoot(0x1)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B91438B0,0x1)/IPv6(0000:0000:0000:0000:0000:0000:0000:0000)",
      "PciRoot(0x1)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B91438B0,0x1)/IPv6(0000:0000:0000:0000:0000:0000:0000:0000)/Uri()",
      "PciRoot(0x0)/Pci(0x10,0x0)/Pci(0x0,0x0)/NVMe(0x1,00-00-00-00-00-00-00-00)",
      "PciRoot(0x0)/Pci(0x11,0x0)/Pci(0x0,0x0)/NVMe(0x1,00-00-00-00-00-00-00-00)"
    ]
  },
  "EthernetInterfaces": {
    "@odata.id": "/redfish/v1/Systems/1/EthernetInterfaces/"
  },
  "HostName": "",
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
      "@odata.type": "#HpeComputerSystemExt.v2_12_0.HpeComputerSystemExt",
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
      "CurrentPowerOnTimeSeconds": null,
      "DeviceDiscoveryComplete": {
        "AMSDeviceDiscovery": "NoAMS",
        "DeviceDiscovery": "vMainDeviceDiscoveryComplete"
      },
      "ElapsedEraseTimeInMinutes": 0,
      "EndOfPostDelaySeconds": 0,
      "EstimatedEraseTimeInMinutes": 0,
      "IndicatorLED": "Off",
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
      "PCASerialNumber": "PYHRC0ALMIY02Z",
      "PostDiscoveryCompleteTimeStamp": null,
      "PostDiscoveryMode": "Auto",
      "PostMode": "Normal",
      "PostState": "InPostDiscoveryComplete",
      "PowerAutoOn": "Restore",
      "PowerOnDelay": "Minimum",
      "PowerOnMinutes": 0,
      "PowerRegulatorMode": "Dynamic",
      "PowerRegulatorModesSupported": [
        "OSControl",
        "Dynamic",
        "Max",
        "Min"
      ],
      "SMBIOS": {
        "extref": "/smbios"
      },
      "ServerFQDN": "",
      "ServerIntelligentDiagnosticsModeEnabled": false,
      "ServerSafeModeEnabled": false,
      "SystemROMAndiLOEraseComponentStatus": {
        "BIOSSettingsEraseStatus": "Idle",
        "iLOSettingsEraseStatus": "Idle"
      },
      "SystemROMAndiLOEraseStatus": "Idle",
      "SystemUsage": {
        "AvgCPU0Freq": 35,
        "CPU0Power": 70,
        "CPUICUtil": 0,
        "CPUUtil": 6,
        "IOBusUtil": 0,
        "JitterCount": 137,
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
  "SerialNumber": "MXQ346090C",
  "Status": {
    "Health": "Warning",
    "HealthRollup": "Warning",
    "State": "Starting"
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
  "UUID": "35383450-3134-584D-5133-343630393043"
}
(hpe_fw) [XXXXXX@welktxefnce-h-pe1util-vm01 ZT-Triton-BMC-update-Redfish-v2.27.00-x86_64_20231027]$
```


## Now lets run the BMC playbook to see if it configures properly

```log

(failed reverse-i-search)`ansible-play': source ~/python_venvs/^Csible_6.7/bin/activate
szabota@welktxefnce-h-pe1util-vm05:~/playbooks/bmc-sapphire-rapids/bmc$ ansible-playbook --vault-password-file ./vault.txt -i inventory/welktxsr-931883-rh-le093s6-012.yaml bmc.yaml

PLAY [BMC configuration playbook] *****************************************************************************************************

TASK [Initialize me environment variable] *********************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [Initialize prod environment variable] *******************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : zts/enable-ssh] **************************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : zts/clear_sel_logs] **********************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : zts/check_model] *************************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : zts/upgrade_ls3] *************************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : zts/upgrade_ls6] *************************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : zts/disable_pam_auth] ********************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : zts/configure-ipv4] **********************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : zts/account-create] **********************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : zts/mac-discover] ************************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : zts/system-off] **************************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : zts/bios-config] *************************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : zts/host-name] ***************************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : zts/configure-dns] ***********************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : zts/configure-ntp] ***********************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : zts/subscribe-redfish-events] ************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : zts/system-on] ***************************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : hpe/check_model] *************************************************************************************************

TASK [hpe/check_model : Get server model] *********************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/check_model : Set server model] *********************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012]

TASK [hpe/check_model : Display model name] *******************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012] => {
    "model_name": "Edgeline e930t"
}

TASK [hpe/check_model : Fail when model specifier substring in hostname does not match the actual model name] *************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : hpe/upgrade_ls3] *************************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : hpe/upgrade_ls6] *************************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : hpe/account-create] **********************************************************************************************

TASK [hpe/account-create : Create temporary working directory] ************************************************************************
changed: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/account-create : Copy HPE account creation scripts to working dir] **********************************************************
changed: [welktxsr-931883-rh-le093s6-012 -> localhost] => (item={'filename': 'get_resource_directory.py', 'value': '#!/usr/bin/env python\n\nfrom __future__ import print_function\nimport argparse\nimport ipaddress\nimport yaml\nfrom redfish import RedfishClient as RedfishClient\nimport os\nimport sys\nfrom redfish.rest.v1 import ServerDownOrUnreachableError\n\ndef get_resource_directory_profile():\n    cwd = os.path.dirname(os.path.abspath(__file__))\n    profile_name = "%s/hp_hw_profile.yaml" % cwd\n    try:\n        with open(profile_name) as file:\n            return yaml.load(file, Loader=yaml.FullLoader)["resource_directory"]\n    except IOError:\n        print("Error opening %s" % profile_name)\n        sys.exit(2)\n\ndef get_resource_directory(redfish_obj):\n    profile = get_resource_directory_profile()\n    response = redfish_obj.get(profile["url"])\n    resources = None\n    if response.status == 200:\n        resources = response.dict[profile["section"]]\n    else:\n        sys.stderr.write("\\tResource directory missing at %s\\n" % profile["url"])\n        sys.exit(2)\n    return resources\n\nif __name__ == "__main__":\n    parser = argparse.ArgumentParser(description="get resource directory script")\n    parser.add_argument("-n", dest="ip", required=True, help="The BMC IP address")\n    parser.add_argument("-u", dest="user", required=True, help="The BMC username")\n    parser.add_argument("-p", dest="passwd", required=True, help="The BMC password")\n    args = parser.parse_args()\n    ip = args.ip\n    login_account = args.user\n    login_password = args.passwd\n    ip_adar_type = ipaddress.ip_address(ip)\n    if type(ip_adar_type) == ipaddress.IPv4Address:\n        system_url = "https://" + ip + ""\n    else:\n        system_url = "https://[" + ip + "]"\n    redfish_obj = None\n    try:\n        redfish_obj = RedfishClient(base_url=system_url, username=login_account, password=XXXXXX        redfish_obj.login()\n    except ServerDownOrUnreachableError:\n        sys.stderr.write("ERROR: server not reachable or doesn\'t support Redfish.\\n")\n        sys.exit(2)\n    get_resource_directory(redfish_obj)\n    sys.exit(0)\n'})
changed: [welktxsr-931883-rh-le093s6-012 -> localhost] => (item={'filename': 'hp_hw_profile.yaml', 'value': '---\nresource_directory:\n  url: /redfish/v1/resourcedirectory\n  section: Instances\n'})

TASK [hpe/account-create : Copy HPE account creation scripts to working dir] **********************************************************
changed: [welktxsr-931883-rh-le093s6-012 -> localhost] => (item=add_user_account.py)

TASK [hpe/account-create : Execute HPE account creation script] ***********************************************************************
changed: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/account-create : Remove temporary working directory] ************************************************************************
changed: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [include_role : hpe/mac-discover] ************************************************************************************************

TASK [hpe/mac-discover : Create temporary working directory] **************************************************************************
changed: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/mac-discover : Copy mac discovery scripts to working dir] *******************************************************************
changed: [welktxsr-931883-rh-le093s6-012 -> localhost] => (item={'filename': 'get_resource_directory.py', 'value': '#!/usr/bin/env python\n\nfrom __future__ import print_function\nimport argparse\nimport ipaddress\nimport yaml\nfrom redfish import RedfishClient as RedfishClient\nimport os\nimport sys\nfrom redfish.rest.v1 import ServerDownOrUnreachableError\n\ndef get_resource_directory_profile():\n    cwd = os.path.dirname(os.path.abspath(__file__))\n    profile_name = "%s/hp_hw_profile.yaml" % cwd\n    try:\n        with open(profile_name) as file:\n            return yaml.load(file, Loader=yaml.FullLoader)["resource_directory"]\n    except IOError:\n        print("Error opening %s" % profile_name)\n        sys.exit(2)\n\ndef get_resource_directory(redfish_obj):\n    profile = get_resource_directory_profile()\n    response = redfish_obj.get(profile["url"])\n    resources = None\n    if response.status == 200:\n        resources = response.dict[profile["section"]]\n    else:\n        sys.stderr.write("\\tResource directory missing at %s\\n" % profile["url"])\n        sys.exit(2)\n    return resources\n\nif __name__ == "__main__":\n    parser = argparse.ArgumentParser(description="get resource directory script")\n    parser.add_argument("-n", dest="ip", required=True, help="The BMC IP address")\n    parser.add_argument("-u", dest="user", required=True, help="The BMC username")\n    parser.add_argument("-p", dest="passwd", required=True, help="The BMC password")\n    args = parser.parse_args()\n    ip = args.ip\n    login_account = args.user\n    login_password = args.passwd\n    ip_adar_type = ipaddress.ip_address(ip)\n    if type(ip_adar_type) == ipaddress.IPv4Address:\n        system_url = "https://" + ip + ""\n    else:\n        system_url = "https://[" + ip + "]"\n    redfish_obj = None\n    try:\n        redfish_obj = RedfishClient(base_url=system_url, username=login_account, password=XXXXXX        redfish_obj.login()\n    except ServerDownOrUnreachableError:\n        sys.stderr.write("ERROR: server not reachable or doesn\'t support Redfish.\\n")\n        sys.exit(2)\n    get_resource_directory(redfish_obj)\n    sys.exit(0)\n'})
changed: [welktxsr-931883-rh-le093s6-012 -> localhost] => (item={'filename': 'hp_hw_profile.yaml', 'value': '---\nresource_directory:\n  url: /redfish/v1/resourcedirectory\n  section: Instances\n'})

TASK [hpe/mac-discover : Copy MAC address discovery scripts to working dir] ***********************************************************
changed: [welktxsr-931883-rh-le093s6-012 -> localhost] => (item=find_ilo_mac_address.py)
changed: [welktxsr-931883-rh-le093s6-012 -> localhost] => (item=ls3_92s3_find_ilo_mac_address.py)
changed: [welktxsr-931883-rh-le093s6-012 -> localhost] => (item=ls6_find_ilo_mac_address.py)
changed: [welktxsr-931883-rh-le093s6-012 -> localhost] => (item=930t_find_ilo_mac_address.py)

TASK [hpe/mac-discover : Execute MAC address discovery script for HPE-LS3-e910] *******************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [hpe/mac-discover : MAC address discovery (result) for HPE-LS3-e910] *************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [hpe/mac-discover : Execute MAC address discovery script for HPE-LS3-92s3] *******************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [hpe/mac-discover : MAC address discovery (result) for HPE-LS3-92s3] *************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [hpe/mac-discover : Execute MAC address discovery script for HPE-LS6-92s6] *******************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [hpe/mac-discover : MAC address discovery (result) for HPE-LS6-92s6] *************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [hpe/mac-discover : Execute MAC address discovery script for HPE-LS6-93s6] *******************************************************
changed: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/mac-discover : MAC address discovery (result) for HPE-LS6-93s6] *************************************************************
ok: [welktxsr-931883-rh-le093s6-012] => {
    "msg": "mac address:F0:B2:B9:14:3B:C4 firmware:4.22 (0x8001A52F)"
}

TASK [hpe/mac-discover : Remove temporary working directory] **************************************************************************
changed: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/mac-discover : Push MAC address to middleware] ******************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [hpe/mac-discover : Push MAC address to middleware] ******************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [hpe/mac-discover : Push MAC address to middleware] ******************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [hpe/mac-discover : Push MAC address to middleware] ******************************************************************************
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [include_role : hpe/bios-config] *************************************************************************************************

TASK [hpe/bios-config : Execute e910t e920t bios configs] *****************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [hpe/bios-config : Execute e930t bios config] ************************************************************************************
[WARNING]: Collection community.general does not support Ansible version 2.12.10
included: /home/szabota/playbooks/bmc-sapphire-rapids/bmc/roles/hpe/bios-config/tasks/e930t.yaml for welktxsr-931883-rh-le093s6-012

TASK [hpe/bios-config : Create temporary working directory] ***************************************************************************
changed: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/bios-config : Copy bios changing scripts to working dir] ********************************************************************
changed: [welktxsr-931883-rh-le093s6-012 -> localhost] => (item={'filename': 'get_resource_directory.py', 'value': '#!/usr/bin/env python\n\nfrom __future__ import print_function\nimport argparse\nimport ipaddress\nimport yaml\nfrom redfish import RedfishClient as RedfishClient\nimport os\nimport sys\nfrom redfish.rest.v1 import ServerDownOrUnreachableError\n\ndef get_resource_directory_profile():\n    cwd = os.path.dirname(os.path.abspath(__file__))\n    profile_name = "%s/hp_hw_profile.yaml" % cwd\n    try:\n        with open(profile_name) as file:\n            return yaml.load(file, Loader=yaml.FullLoader)["resource_directory"]\n    except IOError:\n        print("Error opening %s" % profile_name)\n        sys.exit(2)\n\ndef get_resource_directory(redfish_obj):\n    profile = get_resource_directory_profile()\n    response = redfish_obj.get(profile["url"])\n    resources = None\n    if response.status == 200:\n        resources = response.dict[profile["section"]]\n    else:\n        sys.stderr.write("\\tResource directory missing at %s\\n" % profile["url"])\n        sys.exit(2)\n    return resources\n\nif __name__ == "__main__":\n    parser = argparse.ArgumentParser(description="get resource directory script")\n    parser.add_argument("-n", dest="ip", required=True, help="The BMC IP address")\n    parser.add_argument("-u", dest="user", required=True, help="The BMC username")\n    parser.add_argument("-p", dest="passwd", required=True, help="The BMC password")\n    args = parser.parse_args()\n    ip = args.ip\n    login_account = args.user\n    login_password = args.passwd\n    ip_adar_type = ipaddress.ip_address(ip)\n    if type(ip_adar_type) == ipaddress.IPv4Address:\n        system_url = "https://" + ip + ""\n    else:\n        system_url = "https://[" + ip + "]"\n    redfish_obj = None\n    try:\n        redfish_obj = RedfishClient(base_url=system_url, username=login_account, password=XXXXXX        redfish_obj.login()\n    except ServerDownOrUnreachableError:\n        sys.stderr.write("ERROR: server not reachable or doesn\'t support Redfish.\\n")\n        sys.exit(2)\n    get_resource_directory(redfish_obj)\n    sys.exit(0)\n'})
changed: [welktxsr-931883-rh-le093s6-012 -> localhost] => (item={'filename': 'hp_hw_profile.yaml', 'value': '---\nresource_directory:\n  url: /redfish/v1/resourcedirectory\n  section: Instances\n'})

TASK [hpe/bios-config : Copy HPE python scripts to working dir] ***********************************************************************
changed: [welktxsr-931883-rh-le093s6-012 -> localhost] => (item=enable_secure_boot.py)
changed: [welktxsr-931883-rh-le093s6-012 -> localhost] => (item=disable_dhcp.py)
changed: [welktxsr-931883-rh-le093s6-012 -> localhost] => (item=configure_dns.py)
changed: [welktxsr-931883-rh-le093s6-012 -> localhost] => (item=configure_syslog.py)
changed: [welktxsr-931883-rh-le093s6-012 -> localhost] => (item=disable_dhcp_ntp.py)
changed: [welktxsr-931883-rh-le093s6-012 -> localhost] => (item=set_ilo_sntp_servers.py)

TASK [Power on the system] ************************************************************************************************************

TASK [hpe/system-on : Check server power status] **************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/system-on : Power on server] ************************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [hpe/system-on : Wait for HPE server to start] ***********************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [hpe/system-on : Wait for system to complete POST after power on] ****************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [hpe/bios-config : Check if system is ready for BIOS configuration changes (part 1)] *********************************************
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/bios-config : Get Bios Settings] ********************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/bios-config : Set HPE BIOS configuration attribute] *************************************************************************
[DEPRECATION WARNING]: The default value 10 for parameter param1 is being deprecated and it will be replaced by 60. This feature will
be removed from community.general in version 9.0.0. Deprecation warnings can be disabled by setting deprecation_warnings=False in
ansible.cfg.
changed: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/bios-config : Display HPE BIOS configuration attribute e930t WorkloadProfile should be vRAN in the result] ******************
ok: [welktxsr-931883-rh-le093s6-012] => {
    "result": {
        "changed": true,
        "deprecations": [
            {
                "collection_name": "community.general",
                "msg": "The default value 10 for parameter param1 is being deprecated and it will be replaced by 60",
                "version": "9.0.0"
            }
        ],
        "failed": false,
        "msg": "Modified BIOS attributes {'WorkloadProfile': 'vRAN'}"
    }
}

TASK [hpe/bios-config : Execute HPE secure boot script] *******************************************************************************
changed: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/bios-config : Display output] ***********************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012] => {
    "result.stdout": "args.secure_boot_enable=False\n\n\nShowing Secure Boot properties before changes:\n\n\n{\n    \"@odata.context\": \"/redfish/v1/$metadata#SecureBoot.SecureBoot\",\n    \"@odata.etag\": \"W/\\\"FCD9344F\\\"\",\n    \"@odata.id\": \"/redfish/v1/Systems/1/SecureBoot\",\n    \"@odata.type\": \"#SecureBoot.v1_1_0.SecureBoot\",\n    \"Actions\": {\n        \"#SecureBoot.ResetKeys\": {\n            \"target\": \"/redfish/v1/Systems/1/SecureBoot/Actions/SecureBoot.ResetKeys\"\n        }\n    },\n    \"Id\": \"SecureBoot\",\n    \"Name\": \"SecureBoot\",\n    \"SecureBootCurrentBoot\": \"Disabled\",\n    \"SecureBootDatabases\": {\n        \"@odata.id\": \"/redfish/v1/Systems/1/SecureBoot/SecureBootDatabases\"\n    },\n    \"SecureBootEnable\": false,\n    \"SecureBootMode\": \"UserMode\"\n}\n[\n    {\n        \"MessageArgs\": [\n            \"SecureBootEnable or ResetToDefaultKeys or ResetAllKeys\"\n        ],\n        \"MessageId\": \"iLO.2.26.UnableToModifyDuringSystemPOST\"\n    }\n]"
}

TASK [hpe/bios-config : Execute HPE disable DHCP script] ******************************************************************************
changed: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/bios-config : Display output] ***********************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012] => {
    "result.stdout": "Disabled DHCP on Ethernet Interfaces Successfully!"
}

TASK [hpe/bios-config : Execute HPE configure DNS script] *****************************************************************************
changed: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/bios-config : Display output] ***********************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012] => {
    "result.stdout": "Configured DNS on Ethernet Interfaces Successfully!"
}

TASK [hpe/bios-config : Execute HPE configure remote syslog script] *******************************************************************
changed: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/bios-config : Display output] ***********************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012] => {
    "result.stdout": "Configured Remote  on Ethernet Interfaces Successfully!"
}

TASK [hpe/bios-config : Execute HPE disable DHCP NTP servers script] ******************************************************************
changed: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/bios-config : Display output] ***********************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012] => {
    "result.stdout": "Success!"
}

TASK [hpe/bios-config : Execute HPE configure SNTP servers script] ********************************************************************
changed: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/bios-config : Display output] ***********************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012] => {
    "result.stdout": "Success!"
}

TASK [hpe/bios-config : Disable IPv4 use domain setting] ******************************************************************************
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [Reset HPE ILO] ******************************************************************************************************************

TASK [hpe/ilo-reset : Reset ILO] ******************************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/ilo-reset : Wait for HPE ILO to reset] **************************************************************************************
Pausing for 30 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [welktxsr-931883-rh-le093s6-012]

TASK [hpe/ilo-reset : Check redfish health after ILO reset] ***************************************************************************
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Check redfish health after ILO reset (6 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Check redfish health after ILO reset (5 retries left).
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/bios-config : Remove temporary working directory] ***************************************************************************
changed: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [Power off the system] ***********************************************************************************************************

TASK [hpe/system-off : Check server power status] *************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/system-off : Power off server] **********************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/system-off : Wait for HPE server to shut down] ******************************************************************************
Pausing for 10 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [welktxsr-931883-rh-le093s6-012]

TASK [Power on the system] ************************************************************************************************************

TASK [hpe/system-on : Check server power status] **************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/system-on : Power on server] ************************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/system-on : Wait for HPE server to start] ***********************************************************************************
Pausing for 120 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [welktxsr-931883-rh-le093s6-012]

TASK [hpe/system-on : Wait for system to complete POST after power on] ****************************************************************
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (30 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (29 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (28 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (27 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (26 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (25 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (24 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (23 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (22 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (21 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (20 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (19 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (18 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (17 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (16 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (15 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (14 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (13 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (12 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (11 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (10 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (9 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (8 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (7 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (6 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (5 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (4 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (3 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (2 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (1 retries left).
fatal: [welktxsr-931883-rh-le093s6-012 -> localhost]: FAILED! => {"allow": "GET, HEAD, PATCH", "attempts": 30, "cache_control": "no-cache", "changed": false, "connection": "close", "content": "{\"@odata.context\":\"/redfish/v1/$metadata#ComputerSystem.ComputerSystem\",\"@odata.etag\":\"W/\\\"5C4CD08F\\\"\",\"@odata.id\":\"/redfish/v1/Systems/1\",\"@odata.type\":\"#ComputerSystem.v1_17_0.ComputerSystem\",\"Id\":\"1\",\"Actions\":{\"#ComputerSystem.Reset\":{\"ResetType@Redfish.AllowableValues\":[\"On\",\"ForceOff\",\"GracefulShutdown\",\"ForceRestart\",\"Nmi\",\"PushPowerButton\",\"GracefulRestart\"],\"target\":\"/redfish/v1/Systems/1/Actions/ComputerSystem.Reset\"}},\"AssetTag\":\"\",\"Bios\":{\"@odata.id\":\"/redfish/v1/systems/1/bios\"},\"BiosVersion\":\"H11 v1.11 (03/07/2024)\",\"Boot\":{\"BootOptions\":{\"@odata.id\":\"/redfish/v1/Systems/1/BootOptions\"},\"BootOrder\":[\"Boot000E\",\"Boot0011\",\"Boot0013\",\"Boot0012\",\"Boot0014\",\"Boot0019\",\"Boot001B\",\"Boot0015\",\"Boot0017\",\"Boot001D\",\"Boot001E\",\"Boot0020\",\"Boot001A\",\"Boot001F\",\"Boot001C\",\"Boot0018\",\"Boot0016\",\"Boot000F\",\"Boot0010\"],\"BootSourceOverrideEnabled\":\"Disabled\",\"BootSourceOverrideMode\":\"UEFI\",\"BootSourceOverrideTarget\":\"None\",\"BootSourceOverrideTarget@Redfish.AllowableValues\":[\"None\",\"Cd\",\"Hdd\",\"Usb\",\"SDCard\",\"Utilities\",\"Diags\",\"BiosSetup\",\"Pxe\",\"UefiShell\",\"UefiHttp\",\"UefiTarget\"],\"UefiTargetBootSourceOverride\":\"None\",\"UefiTargetBootSourceOverride@Redfish.AllowableValues\":[\"UsbClass(0xFFFF,0xFFFF,0xFF,0xFF,0xFF)\",\"PciRoot(0x0)/Pci(0xF,0x0)/Pci(0x0,0x0)/MAC(5CED8CEFAE00,0x1)/IPv4(0.0.0.0)/Uri()\",\"PciRoot(0x0)/Pci(0xF,0x0)/Pci(0x0,0x0)/MAC(5CED8CEFAE00,0x1)/IPv4(0.0.0.0)\",\"PciRoot(0x0)/Pci(0xF,0x0)/Pci(0x0,0x0)/MAC(5CED8CEFAE00,0x1)/IPv6(0000:0000:0000:0000:0000:0000:0000:0000)/Uri()\",\"PciRoot(0x0)/Pci(0xF,0x0)/Pci(0x0,0x0)/MAC(5CED8CEFAE00,0x1)/IPv6(0000:0000:0000:0000:0000:0000:0000:0000)\",\"PciRoot(0x2)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B9143BC4,0x1)/IPv4(0.0.0.0)/Uri()\",\"PciRoot(0x2)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B9143BC4,0x1)/IPv4(0.0.0.0)\",\"PciRoot(0x1)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B91438B0,0x1)/IPv4(0.0.0.0)/Uri()\",\"PciRoot(0x1)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B91438B0,0x1)/IPv4(0.0.0.0)\",\"PciRoot(0x5)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B9143A00,0x1)/IPv4(0.0.0.0)/Uri()\",\"PciRoot(0x5)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B9143A00,0x1)/IPv6(0000:0000:0000:0000:0000:0000:0000:0000)/Uri()\",\"PciRoot(0x5)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B9143A00,0x1)/IPv6(0000:0000:0000:0000:0000:0000:0000:0000)\",\"PciRoot(0x2)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B9143BC4,0x1)/IPv6(0000:0000:0000:0000:0000:0000:0000:0000)/Uri()\",\"PciRoot(0x5)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B9143A00,0x1)/IPv4(0.0.0.0)\",\"PciRoot(0x2)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B9143BC4,0x1)/IPv6(0000:0000:0000:0000:0000:0000:0000:0000)\",\"PciRoot(0x1)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B91438B0,0x1)/IPv6(0000:0000:0000:0000:0000:0000:0000:0000)\",\"PciRoot(0x1)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B91438B0,0x1)/IPv6(0000:0000:0000:0000:0000:0000:0000:0000)/Uri()\",\"PciRoot(0x0)/Pci(0x10,0x0)/Pci(0x0,0x0)/NVMe(0x1,00-00-00-00-00-00-00-00)\",\"PciRoot(0x0)/Pci(0x11,0x0)/Pci(0x0,0x0)/NVMe(0x1,00-00-00-00-00-00-00-00)\"]},\"EthernetInterfaces\":{\"@odata.id\":\"/redfish/v1/Systems/1/EthernetInterfaces\"},\"HostName\":\"\",\"Links\":{\"ManagedBy\":[{\"@odata.id\":\"/redfish/v1/Managers/1\"}],\"Chassis\":[{\"@odata.id\":\"/redfish/v1/Chassis/1\"}]},\"LocationIndicatorActive\":null,\"LogServices\":{\"@odata.id\":\"/redfish/v1/Systems/1/LogServices\"},\"Manufacturer\":\"HPE\",\"Memory\":{\"@odata.id\":\"/redfish/v1/Systems/1/Memory\"},\"MemoryDomains\":{\"@odata.id\":\"/redfish/v1/Systems/1/MemoryDomains\"},\"MemorySummary\":{\"Status\":{\"HealthRollup\":\"OK\"},\"TotalSystemMemoryGiB\":256,\"TotalSystemPersistentMemoryGiB\":0},\"Model\":\"Edgeline e930t\",\"Name\":\"Computer System\",\"NetworkInterfaces\":{\"@odata.id\":\"/redfish/v1/Systems/1/NetworkInterfaces\"},\"Oem\":{\"Hpe\":{\"@odata.context\":\"/redfish/v1/$metadata#HpeComputerSystemExt.HpeComputerSystemExt\",\"@odata.type\":\"#HpeComputerSystemExt.v2_12_0.HpeComputerSystemExt\",\"Actions\":{\"#HpeComputerSystemExt.PowerButton\":{\"PushType@Redfish.AllowableValues\":[\"Press\",\"PressAndHold\"],\"target\":\"/redfish/v1/Systems/1/Actions/Oem/Hpe/HpeComputerSystemExt.PowerButton\"},\"#HpeComputerSystemExt.RestoreManufacturingDefaults\":{\"target\":\"/redfish/v1/Systems/1/Actions/Oem/Hpe/HpeComputerSystemExt.RestoreManufacturingDefaults\"},\"#HpeComputerSystemExt.RestoreSystemDefaults\":{\"target\":\"/redfish/v1/Systems/1/Actions/Oem/Hpe/HpeComputerSystemExt.RestoreSystemDefaults\"},\"#HpeComputerSystemExt.SecureSystemErase\":{\"target\":\"/redfish/v1/Systems/1/Actions/Oem/Hpe/HpeComputerSystemExt.SecureSystemErase\"},\"#HpeComputerSystemExt.ServerIntelligentDiagnosticsMode\":{\"target\":\"/redfish/v1/Systems/1/Actions/Oem/Hpe/HpeComputerSystemExt.ServerIntelligentDiagnosticsMode\"},\"#HpeComputerSystemExt.ServerSafeMode\":{\"target\":\"/redfish/v1/Systems/1/Actions/Oem/Hpe/HpeComputerSystemExt.ServerSafeMode\"},\"#HpeComputerSystemExt.SystemReset\":{\"ResetType@Redfish.AllowableValues\":[\"ColdBoot\",\"AuxCycle\"],\"target\":\"/redfish/v1/Systems/1/Actions/Oem/Hpe/HpeComputerSystemExt.SystemReset\"}},\"AggregateHealthStatus\":{\"AgentlessManagementService\":\"Unavailable\",\"AggregateServerHealth\":\"OK\",\"BiosOrHardwareHealth\":{\"Status\":{\"Health\":\"OK\"}},\"FanRedundancy\":\"Redundant\",\"Memory\":{\"Status\":{\"Health\":\"OK\"}},\"Network\":{\"Status\":{\"Health\":null}},\"Processors\":{\"Status\":{\"Health\":\"OK\"}},\"Storage\":{\"Status\":{\"Health\":\"OK\"}}},\"Bios\":{\"Backup\":{\"Date\":\"03/07/2024\",\"Family\":\"H11\",\"VersionString\":\"H11 v1.11 (03/07/2024)\"},\"Current\":{\"Date\":\"03/07/2024\",\"Family\":\"H11\",\"VersionString\":\"H11 v1.11 (03/07/2024)\"},\"UefiClass\":3},\"CriticalTempRemainOff\":true,\"CurrentPowerOnTimeSeconds\":292,\"DeviceDiscoveryComplete\":{\"AMSDeviceDiscovery\":\"NoAMS\",\"DeviceDiscovery\":\"Busy\"},\"ElapsedEraseTimeInMinutes\":0,\"EndOfPostDelaySeconds\":0,\"EstimatedEraseTimeInMinutes\":0,\"IndicatorLED\":\"Blinking\",\"IsColdBooting\":false,\"Links\":{\"PCISlots\":{\"@odata.id\":\"/redfish/v1/Systems/1/PCISlots\"},\"USBPorts\":{\"@odata.id\":\"/redfish/v1/Systems/1/USBPorts\"},\"USBDevices\":{\"@odata.id\":\"/redfish/v1/Systems/1/USBDevices\"},\"EthernetInterfaces\":{\"@odata.id\":\"/redfish/v1/Systems/1/EthernetInterfaces\"},\"WorkloadPerformanceAdvisor\":{\"@odata.id\":\"/redfish/v1/Systems/1/WorkloadPerformanceAdvisor\"},\"SecureEraseReportService\":{\"@odata.id\":\"/redfish/v1/Systems/1/SecureEraseReportService\"},\"PCIDevices\":[{\"@odata.id\":\"/redfish/v1/Systems/1/PCIDevices\"}]},\"PCAPartNumber\":\"P48462-E02\",\"PCASerialNumber\":\"PYHRC0ALMIY02Z\",\"PostDiscoveryCompleteTimeStamp\":null,\"PostDiscoveryMode\":\"Auto\",\"PostMode\":\"Normal\",\"PostState\":\"InPostDiscoveryStart\",\"PowerAutoOn\":\"Restore\",\"PowerOnDelay\":\"Minimum\",\"PowerOnMinutes\":0,\"PowerRegulatorMode\":\"OSControl\",\"PowerRegulatorModesSupported\":[\"OSControl\",\"Dynamic\",\"Max\",\"Min\"],\"SMBIOS\":{\"extref\":\"/smbios\"},\"ServerFQDN\":\"\",\"ServerIntelligentDiagnosticsModeEnabled\":false,\"ServerSafeModeEnabled\":false,\"SystemROMAndiLOEraseComponentStatus\":{\"BIOSSettingsEraseStatus\":\"Idle\",\"iLOSettingsEraseStatus\":\"Idle\"},\"SystemROMAndiLOEraseStatus\":\"Idle\",\"SystemUsage\":{\"AvgCPU0Freq\":0,\"CPU0Power\":0,\"CPUICUtil\":0,\"CPUUtil\":10,\"IOBusUtil\":0,\"JitterCount\":0,\"MemoryBusUtil\":0},\"UserDataEraseComponentStatus\":{},\"UserDataEraseStatus\":\"Idle\",\"VirtualProfile\":\"Inactive\"}},\"PowerState\":\"On\",\"ProcessorSummary\":{\"Count\":1,\"Model\":\"Intel(R) Xeon(R) Gold 6443N\",\"Status\":{\"HealthRollup\":\"OK\"}},\"Processors\":{\"@odata.id\":\"/redfish/v1/Systems/1/Processors\"},\"SKU\":\"P48541-B21\",\"SecureBoot\":{\"@odata.id\":\"/redfish/v1/Systems/1/SecureBoot\"},\"SerialNumber\":\"MXQ346090C\",\"Status\":{\"Health\":\"OK\",\"HealthRollup\":\"OK\",\"State\":\"Starting\"},\"Storage\":{\"@odata.id\":\"/redfish/v1/Systems/1/Storage\"},\"SystemType\":\"Physical\",\"TrustedModules\":[{\"FirmwareVersion\":\"1.512\",\"InterfaceType\":\"TPM2_0\",\"Oem\":{\"Hpe\":{\"@odata.context\":\"/redfish/v1/$metadata#HpeTrustedModuleExt.HpeTrustedModuleExt\",\"@odata.type\":\"#HpeTrustedModuleExt.v2_0_0.HpeTrustedModuleExt\",\"VendorName\":\"STMicro\"}},\"Status\":{\"Health\":\"OK\",\"State\":\"Enabled\"}}],\"UUID\":\"35383450-3134-584D-5133-343630393043\"}", "content_type": "application/json; charset=utf-8", "cookies": {}, "cookies_string": "", "date": "Wed, 24 Apr 2024 21:08:58 GMT", "elapsed": 0, "etag": "W/\"5C4CD08F\"", "json": {"@odata.context": "/redfish/v1/$metadata#ComputerSystem.ComputerSystem", "@odata.etag": "W/\"5C4CD08F\"", "@odata.id": "/redfish/v1/Systems/1", "@odata.type": "#ComputerSystem.v1_17_0.ComputerSystem", "Actions": {"#ComputerSystem.Reset": {"ResetType@Redfish.AllowableValues": ["On", "ForceOff", "GracefulShutdown", "ForceRestart", "Nmi", "PushPowerButton", "GracefulRestart"], "target": "/redfish/v1/Systems/1/Actions/ComputerSystem.Reset"}}, "AssetTag": "", "Bios": {"@odata.id": "/redfish/v1/systems/1/bios"}, "BiosVersion": "H11 v1.11 (03/07/2024)", "Boot": {"BootOptions": {"@odata.id": "/redfish/v1/Systems/1/BootOptions"}, "BootOrder": ["Boot000E", "Boot0011", "Boot0013", "Boot0012", "Boot0014", "Boot0019", "Boot001B", "Boot0015", "Boot0017", "Boot001D", "Boot001E", "Boot0020", "Boot001A", "Boot001F", "Boot001C", "Boot0018", "Boot0016", "Boot000F", "Boot0010"], "BootSourceOverrideEnabled": "Disabled", "BootSourceOverrideMode": "UEFI", "BootSourceOverrideTarget": "None", "BootSourceOverrideTarget@Redfish.AllowableValues": ["None", "Cd", "Hdd", "Usb", "SDCard", "Utilities", "Diags", "BiosSetup", "Pxe", "UefiShell", "UefiHttp", "UefiTarget"], "UefiTargetBootSourceOverride": "None", "UefiTargetBootSourceOverride@Redfish.AllowableValues": ["UsbClass(0xFFFF,0xFFFF,0xFF,0xFF,0xFF)", "PciRoot(0x0)/Pci(0xF,0x0)/Pci(0x0,0x0)/MAC(5CED8CEFAE00,0x1)/IPv4(0.0.0.0)/Uri()", "PciRoot(0x0)/Pci(0xF,0x0)/Pci(0x0,0x0)/MAC(5CED8CEFAE00,0x1)/IPv4(0.0.0.0)", "PciRoot(0x0)/Pci(0xF,0x0)/Pci(0x0,0x0)/MAC(5CED8CEFAE00,0x1)/IPv6(0000:0000:0000:0000:0000:0000:0000:0000)/Uri()", "PciRoot(0x0)/Pci(0xF,0x0)/Pci(0x0,0x0)/MAC(5CED8CEFAE00,0x1)/IPv6(0000:0000:0000:0000:0000:0000:0000:0000)", "PciRoot(0x2)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B9143BC4,0x1)/IPv4(0.0.0.0)/Uri()", "PciRoot(0x2)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B9143BC4,0x1)/IPv4(0.0.0.0)", "PciRoot(0x1)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B91438B0,0x1)/IPv4(0.0.0.0)/Uri()", "PciRoot(0x1)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B91438B0,0x1)/IPv4(0.0.0.0)", "PciRoot(0x5)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B9143A00,0x1)/IPv4(0.0.0.0)/Uri()", "PciRoot(0x5)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B9143A00,0x1)/IPv6(0000:0000:0000:0000:0000:0000:0000:0000)/Uri()", "PciRoot(0x5)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B9143A00,0x1)/IPv6(0000:0000:0000:0000:0000:0000:0000:0000)", "PciRoot(0x2)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B9143BC4,0x1)/IPv6(0000:0000:0000:0000:0000:0000:0000:0000)/Uri()", "PciRoot(0x5)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B9143A00,0x1)/IPv4(0.0.0.0)", "PciRoot(0x2)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B9143BC4,0x1)/IPv6(0000:0000:0000:0000:0000:0000:0000:0000)", "PciRoot(0x1)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B91438B0,0x1)/IPv6(0000:0000:0000:0000:0000:0000:0000:0000)", "PciRoot(0x1)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B91438B0,0x1)/IPv6(0000:0000:0000:0000:0000:0000:0000:0000)/Uri()", "PciRoot(0x0)/Pci(0x10,0x0)/Pci(0x0,0x0)/NVMe(0x1,00-00-00-00-00-00-00-00)", "PciRoot(0x0)/Pci(0x11,0x0)/Pci(0x0,0x0)/NVMe(0x1,00-00-00-00-00-00-00-00)"]}, "EthernetInterfaces": {"@odata.id": "/redfish/v1/Systems/1/EthernetInterfaces"}, "HostName": "", "Id": "1", "Links": {"Chassis": [{"@odata.id": "/redfish/v1/Chassis/1"}], "ManagedBy": [{"@odata.id": "/redfish/v1/Managers/1"}]}, "LocationIndicatorActive": null, "LogServices": {"@odata.id": "/redfish/v1/Systems/1/LogServices"}, "Manufacturer": "HPE", "Memory": {"@odata.id": "/redfish/v1/Systems/1/Memory"}, "MemoryDomains": {"@odata.id": "/redfish/v1/Systems/1/MemoryDomains"}, "MemorySummary": {"Status": {"HealthRollup": "OK"}, "TotalSystemMemoryGiB": 256, "TotalSystemPersistentMemoryGiB": 0}, "Model": "Edgeline e930t", "Name": "Computer System", "NetworkInterfaces": {"@odata.id": "/redfish/v1/Systems/1/NetworkInterfaces"}, "Oem": {"Hpe": {"@odata.context": "/redfish/v1/$metadata#HpeComputerSystemExt.HpeComputerSystemExt", "@odata.type": "#HpeComputerSystemExt.v2_12_0.HpeComputerSystemExt", "Actions": {"#HpeComputerSystemExt.PowerButton": {"PushType@Redfish.AllowableValues": ["Press", "PressAndHold"], "target": "/redfish/v1/Systems/1/Actions/Oem/Hpe/HpeComputerSystemExt.PowerButton"}, "#HpeComputerSystemExt.RestoreManufacturingDefaults": {"target": "/redfish/v1/Systems/1/Actions/Oem/Hpe/HpeComputerSystemExt.RestoreManufacturingDefaults"}, "#HpeComputerSystemExt.RestoreSystemDefaults": {"target": "/redfish/v1/Systems/1/Actions/Oem/Hpe/HpeComputerSystemExt.RestoreSystemDefaults"}, "#HpeComputerSystemExt.SecureSystemErase": {"target": "/redfish/v1/Systems/1/Actions/Oem/Hpe/HpeComputerSystemExt.SecureSystemErase"}, "#HpeComputerSystemExt.ServerIntelligentDiagnosticsMode": {"target": "/redfish/v1/Systems/1/Actions/Oem/Hpe/HpeComputerSystemExt.ServerIntelligentDiagnosticsMode"}, "#HpeComputerSystemExt.ServerSafeMode": {"target": "/redfish/v1/Systems/1/Actions/Oem/Hpe/HpeComputerSystemExt.ServerSafeMode"}, "#HpeComputerSystemExt.SystemReset": {"ResetType@Redfish.AllowableValues": ["ColdBoot", "AuxCycle"], "target": "/redfish/v1/Systems/1/Actions/Oem/Hpe/HpeComputerSystemExt.SystemReset"}}, "AggregateHealthStatus": {"AgentlessManagementService": "Unavailable", "AggregateServerHealth": "OK", "BiosOrHardwareHealth": {"Status": {"Health": "OK"}}, "FanRedundancy": "Redundant", "Memory": {"Status": {"Health": "OK"}}, "Network": {"Status": {"Health": null}}, "Processors": {"Status": {"Health": "OK"}}, "Storage": {"Status": {"Health": "OK"}}}, "Bios": {"Backup": {"Date": "03/07/2024", "Family": "H11", "VersionString": "H11 v1.11 (03/07/2024)"}, "Current": {"Date": "03/07/2024", "Family": "H11", "VersionString": "H11 v1.11 (03/07/2024)"}, "UefiClass": 3}, "CriticalTempRemainOff": true, "CurrentPowerOnTimeSeconds": 292, "DeviceDiscoveryComplete": {"AMSDeviceDiscovery": "NoAMS", "DeviceDiscovery": "Busy"}, "ElapsedEraseTimeInMinutes": 0, "EndOfPostDelaySeconds": 0, "EstimatedEraseTimeInMinutes": 0, "IndicatorLED": "Blinking", "IsColdBooting": false, "Links": {"EthernetInterfaces": {"@odata.id": "/redfish/v1/Systems/1/EthernetInterfaces"}, "PCIDevices": [{"@odata.id": "/redfish/v1/Systems/1/PCIDevices"}], "PCISlots": {"@odata.id": "/redfish/v1/Systems/1/PCISlots"}, "SecureEraseReportService": {"@odata.id": "/redfish/v1/Systems/1/SecureEraseReportService"}, "USBDevices": {"@odata.id": "/redfish/v1/Systems/1/USBDevices"}, "USBPorts": {"@odata.id": "/redfish/v1/Systems/1/USBPorts"}, "WorkloadPerformanceAdvisor": {"@odata.id": "/redfish/v1/Systems/1/WorkloadPerformanceAdvisor"}}, "PCAPartNumber": "P48462-E02", "PCASerialNumber": "PYHRC0ALMIY02Z", "PostDiscoveryCompleteTimeStamp": null, "PostDiscoveryMode": "Auto", "PostMode": "Normal", "PostState": "InPostDiscoveryStart", "PowerAutoOn": "Restore", "PowerOnDelay": "Minimum", "PowerOnMinutes": 0, "PowerRegulatorMode": "OSControl", "PowerRegulatorModesSupported": ["OSControl", "Dynamic", "Max", "Min"], "SMBIOS": {"extref": "/smbios"}, "ServerFQDN": "", "ServerIntelligentDiagnosticsModeEnabled": false, "ServerSafeModeEnabled": false, "SystemROMAndiLOEraseComponentStatus": {"BIOSSettingsEraseStatus": "Idle", "iLOSettingsEraseStatus": "Idle"}, "SystemROMAndiLOEraseStatus": "Idle", "SystemUsage": {"AvgCPU0Freq": 0, "CPU0Power": 0, "CPUICUtil": 0, "CPUUtil": 10, "IOBusUtil": 0, "JitterCount": 0, "MemoryBusUtil": 0}, "UserDataEraseComponentStatus": {}, "UserDataEraseStatus": "Idle", "VirtualProfile": "Inactive"}}, "PowerState": "On", "ProcessorSummary": {"Count": 1, "Model": "Intel(R) Xeon(R) Gold 6443N", "Status": {"HealthRollup": "OK"}}, "Processors": {"@odata.id": "/redfish/v1/Systems/1/Processors"}, "SKU": "P48541-B21", "SecureBoot": {"@odata.id": "/redfish/v1/Systems/1/SecureBoot"}, "SerialNumber": "MXQ346090C", "Status": {"Health": "OK", "HealthRollup": "OK", "State": "Starting"}, "Storage": {"@odata.id": "/redfish/v1/Systems/1/Storage"}, "SystemType": "Physical", "TrustedModules": [{"FirmwareVersion": "1.512", "InterfaceType": "TPM2_0", "Oem": {"Hpe": {"@odata.context": "/redfish/v1/$metadata#HpeTrustedModuleExt.HpeTrustedModuleExt", "@odata.type": "#HpeTrustedModuleExt.v2_0_0.HpeTrustedModuleExt", "VendorName": "STMicro"}}, "Status": {"Health": "OK", "State": "Enabled"}}], "UUID": "35383450-3134-584D-5133-343630393043"}, "link": "</redfish/v1/SchemaStore/en/ComputerSystem.json>; rel=describedby", "msg": "OK (unknown bytes)", "odata_version": "4.0", "redirected": false, "status": 200, "transfer_encoding": "chunked", "url": "https://[2607:f160:0010:8803:ce:40a:0:e001]/redfish/v1/Systems/1", "x_content_type_options": "nosniff", "x_frame_options": "sameorigin", "x_xss_protection": "1; mode=block"}

TASK [Report failure status to middleware] ********************************************************************************************
ERROR! couldn't resolve module/action 'postgresql_query'. This often indicates a misspelling, missing collection, or incorrect module path.

The error appears to be in '/home/szabota/playbooks/bmc-sapphire-rapids/bmc/roles/playbook-status-report/tasks/main.yaml': line 56, column 7, but may
be elsewhere in the file depending on the exact syntax problem.

The offending line appears to be:


    - name: Get failed job retry count
      ^ here

PLAY RECAP ****************************************************************************************************************************
welktxsr-931883-rh-le093s6-012 : ok=48   changed=21   unreachable=0    failed=0    skipped=33   rescued=1    ignored=0

szabota@welktxefnce-h-pe1util-vm05:~/playbooks/bmc-sapphire-rapids/bmc$
```

## Failed, due to a timeout, waiting for the server to finish POST The SPR systems seem to take longer in post
## edited the hpe/system-on/tasks/main.yaml to adjust retries from "30" to "50"

## Running bmc playbook again

```log
szabota@welktxefnce-h-pe1util-vm05:~/playbooks/bmc-sapphire-rapids/bmc$ ansible-playbook --vault-password-file ./vault.txt -i inventory/welktxsr-931883-rh-le093s6-012.yaml bmc.yaml

PLAY [BMC configuration playbook] *****************************************************************************************************

TASK [Initialize me environment variable] *********************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [Initialize prod environment variable] *******************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : zts/enable-ssh] **************************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : zts/clear_sel_logs] **********************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : zts/check_model] *************************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : zts/upgrade_ls3] *************************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : zts/upgrade_ls6] *************************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : zts/disable_pam_auth] ********************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : zts/configure-ipv4] **********************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : zts/account-create] **********************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : zts/mac-discover] ************************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : zts/system-off] **************************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : zts/bios-config] *************************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : zts/host-name] ***************************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : zts/configure-dns] ***********************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : zts/configure-ntp] ***********************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : zts/subscribe-redfish-events] ************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : zts/system-on] ***************************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : hpe/check_model] *************************************************************************************************

TASK [hpe/check_model : Get server model] *********************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/check_model : Set server model] *********************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012]

TASK [hpe/check_model : Display model name] *******************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012] => {
    "model_name": "Edgeline e930t"
}

TASK [hpe/check_model : Fail when model specifier substring in hostname does not match the actual model name] *************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : hpe/upgrade_ls3] *************************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : hpe/upgrade_ls6] *************************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : hpe/account-create] **********************************************************************************************

TASK [hpe/account-create : Create temporary working directory] ************************************************************************
changed: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/account-create : Copy HPE account creation scripts to working dir] **********************************************************
changed: [welktxsr-931883-rh-le093s6-012 -> localhost] => (item={'filename': 'get_resource_directory.py', 'value': '#!/usr/bin/env python\n\nfrom __future__ import print_function\nimport argparse\nimport ipaddress\nimport yaml\nfrom redfish import RedfishClient as RedfishClient\nimport os\nimport sys\nfrom redfish.rest.v1 import ServerDownOrUnreachableError\n\ndef get_resource_directory_profile():\n    cwd = os.path.dirname(os.path.abspath(__file__))\n    profile_name = "%s/hp_hw_profile.yaml" % cwd\n    try:\n        with open(profile_name) as file:\n            return yaml.load(file, Loader=yaml.FullLoader)["resource_directory"]\n    except IOError:\n        print("Error opening %s" % profile_name)\n        sys.exit(2)\n\ndef get_resource_directory(redfish_obj):\n    profile = get_resource_directory_profile()\n    response = redfish_obj.get(profile["url"])\n    resources = None\n    if response.status == 200:\n        resources = response.dict[profile["section"]]\n    else:\n        sys.stderr.write("\\tResource directory missing at %s\\n" % profile["url"])\n        sys.exit(2)\n    return resources\n\nif __name__ == "__main__":\n    parser = argparse.ArgumentParser(description="get resource directory script")\n    parser.add_argument("-n", dest="ip", required=True, help="The BMC IP address")\n    parser.add_argument("-u", dest="user", required=True, help="The BMC username")\n    parser.add_argument("-p", dest="passwd", required=True, help="The BMC password")\n    args = parser.parse_args()\n    ip = args.ip\n    login_account = args.user\n    login_password = args.passwd\n    ip_adar_type = ipaddress.ip_address(ip)\n    if type(ip_adar_type) == ipaddress.IPv4Address:\n        system_url = "https://" + ip + ""\n    else:\n        system_url = "https://[" + ip + "]"\n    redfish_obj = None\n    try:\n        redfish_obj = RedfishClient(base_url=system_url, username=login_account, password=XXXXXX        redfish_obj.login()\n    except ServerDownOrUnreachableError:\n        sys.stderr.write("ERROR: server not reachable or doesn\'t support Redfish.\\n")\n        sys.exit(2)\n    get_resource_directory(redfish_obj)\n    sys.exit(0)\n'})
changed: [welktxsr-931883-rh-le093s6-012 -> localhost] => (item={'filename': 'hp_hw_profile.yaml', 'value': '---\nresource_directory:\n  url: /redfish/v1/resourcedirectory\n  section: Instances\n'})

TASK [hpe/account-create : Copy HPE account creation scripts to working dir] **********************************************************
changed: [welktxsr-931883-rh-le093s6-012 -> localhost] => (item=add_user_account.py)

TASK [hpe/account-create : Execute HPE account creation script] ***********************************************************************
changed: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/account-create : Remove temporary working directory] ************************************************************************
changed: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [include_role : hpe/mac-discover] ************************************************************************************************

TASK [hpe/mac-discover : Create temporary working directory] **************************************************************************
changed: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/mac-discover : Copy mac discovery scripts to working dir] *******************************************************************
changed: [welktxsr-931883-rh-le093s6-012 -> localhost] => (item={'filename': 'get_resource_directory.py', 'value': '#!/usr/bin/env python\n\nfrom __future__ import print_function\nimport argparse\nimport ipaddress\nimport yaml\nfrom redfish import RedfishClient as RedfishClient\nimport os\nimport sys\nfrom redfish.rest.v1 import ServerDownOrUnreachableError\n\ndef get_resource_directory_profile():\n    cwd = os.path.dirname(os.path.abspath(__file__))\n    profile_name = "%s/hp_hw_profile.yaml" % cwd\n    try:\n        with open(profile_name) as file:\n            return yaml.load(file, Loader=yaml.FullLoader)["resource_directory"]\n    except IOError:\n        print("Error opening %s" % profile_name)\n        sys.exit(2)\n\ndef get_resource_directory(redfish_obj):\n    profile = get_resource_directory_profile()\n    response = redfish_obj.get(profile["url"])\n    resources = None\n    if response.status == 200:\n        resources = response.dict[profile["section"]]\n    else:\n        sys.stderr.write("\\tResource directory missing at %s\\n" % profile["url"])\n        sys.exit(2)\n    return resources\n\nif __name__ == "__main__":\n    parser = argparse.ArgumentParser(description="get resource directory script")\n    parser.add_argument("-n", dest="ip", required=True, help="The BMC IP address")\n    parser.add_argument("-u", dest="user", required=True, help="The BMC username")\n    parser.add_argument("-p", dest="passwd", required=True, help="The BMC password")\n    args = parser.parse_args()\n    ip = args.ip\n    login_account = args.user\n    login_password = args.passwd\n    ip_adar_type = ipaddress.ip_address(ip)\n    if type(ip_adar_type) == ipaddress.IPv4Address:\n        system_url = "https://" + ip + ""\n    else:\n        system_url = "https://[" + ip + "]"\n    redfish_obj = None\n    try:\n        redfish_obj = RedfishClient(base_url=system_url, username=login_account, password=XXXXXX        redfish_obj.login()\n    except ServerDownOrUnreachableError:\n        sys.stderr.write("ERROR: server not reachable or doesn\'t support Redfish.\\n")\n        sys.exit(2)\n    get_resource_directory(redfish_obj)\n    sys.exit(0)\n'})
changed: [welktxsr-931883-rh-le093s6-012 -> localhost] => (item={'filename': 'hp_hw_profile.yaml', 'value': '---\nresource_directory:\n  url: /redfish/v1/resourcedirectory\n  section: Instances\n'})

TASK [hpe/mac-discover : Copy MAC address discovery scripts to working dir] ***********************************************************
changed: [welktxsr-931883-rh-le093s6-012 -> localhost] => (item=find_ilo_mac_address.py)
changed: [welktxsr-931883-rh-le093s6-012 -> localhost] => (item=ls3_92s3_find_ilo_mac_address.py)
changed: [welktxsr-931883-rh-le093s6-012 -> localhost] => (item=ls6_find_ilo_mac_address.py)
changed: [welktxsr-931883-rh-le093s6-012 -> localhost] => (item=930t_find_ilo_mac_address.py)

TASK [hpe/mac-discover : Execute MAC address discovery script for HPE-LS3-e910] *******************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [hpe/mac-discover : MAC address discovery (result) for HPE-LS3-e910] *************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [hpe/mac-discover : Execute MAC address discovery script for HPE-LS3-92s3] *******************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [hpe/mac-discover : MAC address discovery (result) for HPE-LS3-92s3] *************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [hpe/mac-discover : Execute MAC address discovery script for HPE-LS6-92s6] *******************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [hpe/mac-discover : MAC address discovery (result) for HPE-LS6-92s6] *************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [hpe/mac-discover : Execute MAC address discovery script for HPE-LS6-93s6] *******************************************************
changed: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/mac-discover : MAC address discovery (result) for HPE-LS6-93s6] *************************************************************
ok: [welktxsr-931883-rh-le093s6-012] => {
    "msg": "mac address:F0:B2:B9:14:38:B0 firmware:4.22 (0x8001A52F)"
}

TASK [hpe/mac-discover : Remove temporary working directory] **************************************************************************
changed: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/mac-discover : Push MAC address to middleware] ******************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [hpe/mac-discover : Push MAC address to middleware] ******************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [hpe/mac-discover : Push MAC address to middleware] ******************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [hpe/mac-discover : Push MAC address to middleware] ******************************************************************************
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [include_role : hpe/bios-config] *************************************************************************************************

TASK [hpe/bios-config : Execute e910t e920t bios configs] *****************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [hpe/bios-config : Execute e930t bios config] ************************************************************************************
[WARNING]: Collection community.general does not support Ansible version 2.12.10
included: /home/szabota/playbooks/bmc-sapphire-rapids/bmc/roles/hpe/bios-config/tasks/e930t.yaml for welktxsr-931883-rh-le093s6-012

TASK [hpe/bios-config : Create temporary working directory] ***************************************************************************
changed: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/bios-config : Copy bios changing scripts to working dir] ********************************************************************
changed: [welktxsr-931883-rh-le093s6-012 -> localhost] => (item={'filename': 'get_resource_directory.py', 'value': '#!/usr/bin/env python\n\nfrom __future__ import print_function\nimport argparse\nimport ipaddress\nimport yaml\nfrom redfish import RedfishClient as RedfishClient\nimport os\nimport sys\nfrom redfish.rest.v1 import ServerDownOrUnreachableError\n\ndef get_resource_directory_profile():\n    cwd = os.path.dirname(os.path.abspath(__file__))\n    profile_name = "%s/hp_hw_profile.yaml" % cwd\n    try:\n        with open(profile_name) as file:\n            return yaml.load(file, Loader=yaml.FullLoader)["resource_directory"]\n    except IOError:\n        print("Error opening %s" % profile_name)\n        sys.exit(2)\n\ndef get_resource_directory(redfish_obj):\n    profile = get_resource_directory_profile()\n    response = redfish_obj.get(profile["url"])\n    resources = None\n    if response.status == 200:\n        resources = response.dict[profile["section"]]\n    else:\n        sys.stderr.write("\\tResource directory missing at %s\\n" % profile["url"])\n        sys.exit(2)\n    return resources\n\nif __name__ == "__main__":\n    parser = argparse.ArgumentParser(description="get resource directory script")\n    parser.add_argument("-n", dest="ip", required=True, help="The BMC IP address")\n    parser.add_argument("-u", dest="user", required=True, help="The BMC username")\n    parser.add_argument("-p", dest="passwd", required=True, help="The BMC password")\n    args = parser.parse_args()\n    ip = args.ip\n    login_account = args.user\n    login_password = args.passwd\n    ip_adar_type = ipaddress.ip_address(ip)\n    if type(ip_adar_type) == ipaddress.IPv4Address:\n        system_url = "https://" + ip + ""\n    else:\n        system_url = "https://[" + ip + "]"\n    redfish_obj = None\n    try:\n        redfish_obj = RedfishClient(base_url=system_url, username=login_account, password=XXXXXX        redfish_obj.login()\n    except ServerDownOrUnreachableError:\n        sys.stderr.write("ERROR: server not reachable or doesn\'t support Redfish.\\n")\n        sys.exit(2)\n    get_resource_directory(redfish_obj)\n    sys.exit(0)\n'})
changed: [welktxsr-931883-rh-le093s6-012 -> localhost] => (item={'filename': 'hp_hw_profile.yaml', 'value': '---\nresource_directory:\n  url: /redfish/v1/resourcedirectory\n  section: Instances\n'})

TASK [hpe/bios-config : Copy HPE python scripts to working dir] ***********************************************************************
changed: [welktxsr-931883-rh-le093s6-012 -> localhost] => (item=enable_secure_boot.py)
changed: [welktxsr-931883-rh-le093s6-012 -> localhost] => (item=disable_dhcp.py)
changed: [welktxsr-931883-rh-le093s6-012 -> localhost] => (item=configure_dns.py)
changed: [welktxsr-931883-rh-le093s6-012 -> localhost] => (item=configure_syslog.py)
changed: [welktxsr-931883-rh-le093s6-012 -> localhost] => (item=disable_dhcp_ntp.py)
changed: [welktxsr-931883-rh-le093s6-012 -> localhost] => (item=set_ilo_sntp_servers.py)

TASK [Power on the system] ************************************************************************************************************

TASK [hpe/system-on : Check server power status] **************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/system-on : Power on server] ************************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [hpe/system-on : Wait for HPE server to start] ***********************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [hpe/system-on : Wait for system to complete POST after power on] ****************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [hpe/bios-config : Check if system is ready for BIOS configuration changes (part 1)] *********************************************
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/bios-config : Get Bios Settings] ********************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/bios-config : Set HPE BIOS configuration attribute] *************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [hpe/bios-config : Display HPE BIOS configuration attribute e930t WorkloadProfile should be vRAN in the result] ******************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [hpe/bios-config : Execute HPE secure boot script] *******************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [hpe/bios-config : Display output] ***********************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [hpe/bios-config : Execute HPE disable DHCP script] ******************************************************************************
changed: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/bios-config : Display output] ***********************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012] => {
    "result.stdout": "Disabled DHCP on Ethernet Interfaces Successfully!"
}

TASK [hpe/bios-config : Execute HPE configure DNS script] *****************************************************************************
changed: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/bios-config : Display output] ***********************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012] => {
    "result.stdout": "Configured DNS on Ethernet Interfaces Successfully!"
}

TASK [hpe/bios-config : Execute HPE configure remote syslog script] *******************************************************************
changed: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/bios-config : Display output] ***********************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012] => {
    "result.stdout": "Configured Remote  on Ethernet Interfaces Successfully!"
}

TASK [hpe/bios-config : Execute HPE disable DHCP NTP servers script] ******************************************************************
changed: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/bios-config : Display output] ***********************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012] => {
    "result.stdout": "Success!"
}

TASK [hpe/bios-config : Execute HPE configure SNTP servers script] ********************************************************************
changed: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/bios-config : Display output] ***********************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012] => {
    "result.stdout": "Success!"
}

TASK [hpe/bios-config : Disable IPv4 use domain setting] ******************************************************************************
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [Reset HPE ILO] ******************************************************************************************************************

TASK [hpe/ilo-reset : Reset ILO] ******************************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/ilo-reset : Wait for HPE ILO to reset] **************************************************************************************
Pausing for 30 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [welktxsr-931883-rh-le093s6-012]

TASK [hpe/ilo-reset : Check redfish health after ILO reset] ***************************************************************************
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Check redfish health after ILO reset (6 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Check redfish health after ILO reset (5 retries left).
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/bios-config : Remove temporary working directory] ***************************************************************************
changed: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [Power off the system] ***********************************************************************************************************

TASK [hpe/system-off : Check server power status] *************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/system-off : Power off server] **********************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/system-off : Wait for HPE server to shut down] ******************************************************************************
Pausing for 10 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [welktxsr-931883-rh-le093s6-012]

TASK [Power on the system] ************************************************************************************************************

TASK [hpe/system-on : Check server power status] **************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/system-on : Power on server] ************************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/system-on : Wait for HPE server to start] ***********************************************************************************
Pausing for 120 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [welktxsr-931883-rh-le093s6-012]

TASK [hpe/system-on : Wait for system to complete POST after power on] ****************************************************************
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (50 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (49 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (48 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (47 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (46 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (45 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (44 retries left).
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/bios-config : Get Bios Settings] ********************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/bios-config : Fail when BIOS attributes are not set correctly] **************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : hpe/system-off] **************************************************************************************************

TASK [hpe/system-off : Check server power status] *************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/system-off : Power off server] **********************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/system-off : Wait for HPE server to shut down] ******************************************************************************
Pausing for 10 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : hpe/ilo-hostname] ************************************************************************************************

TASK [hpe/ilo-hostname : Change host name for iLO interface] **************************************************************************
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [include_role : hpe/host-name] ***************************************************************************************************

TASK [hpe/host-name : Change host name for iLO events] ********************************************************************************
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/host-name : Change FQDN for iLO events] *************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [include_role : hpe/syslog-disable] **********************************************************************************************

TASK [hpe/syslog-disable : Disable Remote Syslog] *************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [include_role : hpe/subscribe-redfish-events] ************************************************************************************

TASK [hpe/subscribe-redfish-events : Set facts to subscribe events for HPE servers] ***************************************************
ok: [welktxsr-931883-rh-le093s6-012]

TASK [hpe/subscribe-redfish-events : Get Event subscription count] ********************************************************************
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/subscribe-redfish-events : Delete existing subscriptions] *******************************************************************

TASK [hpe/subscribe-redfish-events : Subscribe to Redfish Alarms] *********************************************************************
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [include_role : hpe/system-on] ***************************************************************************************************

TASK [hpe/system-on : Check server power status] **************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/system-on : Power on server] ************************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/system-on : Wait for HPE server to start] ***********************************************************************************
Pausing for 120 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [welktxsr-931883-rh-le093s6-012]

TASK [hpe/system-on : Wait for system to complete POST after power on] ****************************************************************
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (50 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (49 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (48 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (47 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (46 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (45 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (44 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (43 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (42 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (41 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (40 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (39 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (38 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (37 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (36 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (35 retries left).
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [Report success status to middleware] ********************************************************************************************
ERROR! couldn't resolve module/action 'postgresql_query'. This often indicates a misspelling, missing collection, or incorrect module path.

The error appears to be in '/home/szabota/playbooks/bmc-sapphire-rapids/bmc/roles/playbook-status-report/tasks/main.yaml': line 56, column 7, but may
be elsewhere in the file depending on the exact syntax problem.

The offending line appears to be:


    - name: Get failed job retry count
      ^ here

TASK [Report failure status to middleware] ********************************************************************************************

PLAY RECAP ****************************************************************************************************************************
welktxsr-931883-rh-le093s6-012 : ok=60   changed=19   unreachable=0    failed=0    skipped=39   rescued=0    ignored=0

szabota@welktxefnce-h-pe1util-vm05:~/playbooks/bmc-sapphire-rapids/bmc$
```

## Playbook worked this time, as we increased timeouts waiting for POST to finish after power on.


## Lets take a quick look at bios settings again after our playbook

```log

(hpe_fw) [XXXXXX@welktxefnce-h-pe1util-vm01 ZT-Triton-BMC-update-Redfish-v2.27.00-x86_64_20231027]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[$ILO]/redfish/v1/Systems/1/ | jq .
{
  "@odata.context": "/redfish/v1/$metadata#ComputerSystem.ComputerSystem",
  "@odata.etag": "W/\"B433A5FE\"",
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
  "AssetTag": "                                ",
  "Bios": {
    "@odata.id": "/redfish/v1/systems/1/bios/"
  },
  "BiosVersion": "H11 v1.11 (03/07/2024)",
  "Boot": {
    "BootOptions": {
      "@odata.id": "/redfish/v1/Systems/1/BootOptions/"
    },
    "BootOrder": [
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
      "UsbClass(0xFFFF,0xFFFF,0xFF,0xFF,0xFF)",
      "PciRoot(0x0)/Pci(0xF,0x0)/Pci(0x0,0x0)/MAC(5CED8CEFAE00,0x1)/IPv4(0.0.0.0)/Uri()",
      "PciRoot(0x0)/Pci(0xF,0x0)/Pci(0x0,0x0)/MAC(5CED8CEFAE00,0x1)/IPv4(0.0.0.0)",
      "PciRoot(0x0)/Pci(0xF,0x0)/Pci(0x0,0x0)/MAC(5CED8CEFAE00,0x1)/IPv6(0000:0000:0000:0000:0000:0000:0000:0000)/Uri()",
      "PciRoot(0x0)/Pci(0xF,0x0)/Pci(0x0,0x0)/MAC(5CED8CEFAE00,0x1)/IPv6(0000:0000:0000:0000:0000:0000:0000:0000)",
      "PciRoot(0x2)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B9143BC4,0x1)/IPv4(0.0.0.0)/Uri()",
      "PciRoot(0x2)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B9143BC4,0x1)/IPv4(0.0.0.0)",
      "PciRoot(0x1)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B91438B0,0x1)/IPv4(0.0.0.0)/Uri()",
      "PciRoot(0x1)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B91438B0,0x1)/IPv4(0.0.0.0)",
      "PciRoot(0x5)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B9143A00,0x1)/IPv4(0.0.0.0)/Uri()",
      "PciRoot(0x5)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B9143A00,0x1)/IPv6(0000:0000:0000:0000:0000:0000:0000:0000)/Uri()",
      "PciRoot(0x5)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B9143A00,0x1)/IPv6(0000:0000:0000:0000:0000:0000:0000:0000)",
      "PciRoot(0x2)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B9143BC4,0x1)/IPv6(0000:0000:0000:0000:0000:0000:0000:0000)/Uri()",
      "PciRoot(0x5)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B9143A00,0x1)/IPv4(0.0.0.0)",
      "PciRoot(0x2)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B9143BC4,0x1)/IPv6(0000:0000:0000:0000:0000:0000:0000:0000)",
      "PciRoot(0x1)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B91438B0,0x1)/IPv6(0000:0000:0000:0000:0000:0000:0000:0000)",
      "PciRoot(0x1)/Pci(0x1,0x0)/Pci(0x0,0x0)/MAC(F0B2B91438B0,0x1)/IPv6(0000:0000:0000:0000:0000:0000:0000:0000)/Uri()",
      "PciRoot(0x0)/Pci(0x10,0x0)/Pci(0x0,0x0)/NVMe(0x1,00-00-00-00-00-00-00-00)",
      "PciRoot(0x0)/Pci(0x11,0x0)/Pci(0x0,0x0)/NVMe(0x1,00-00-00-00-00-00-00-00)"
    ]
  },
  "EthernetInterfaces": {
    "@odata.id": "/redfish/v1/Systems/1/EthernetInterfaces/"
  },
  "HostName": "welktxsr-931883-rh-le093s6-012",
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
      "@odata.type": "#HpeComputerSystemExt.v2_12_0.HpeComputerSystemExt",
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
      "CurrentPowerOnTimeSeconds": 502,
      "DeviceDiscoveryComplete": {
        "AMSDeviceDiscovery": "NoAMS",
        "DeviceDiscovery": "vMainDeviceDiscoveryComplete"
      },
      "ElapsedEraseTimeInMinutes": 0,
      "EndOfPostDelaySeconds": 0,
      "EstimatedEraseTimeInMinutes": 0,
      "IndicatorLED": "Off",
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
      "PCASerialNumber": "PYHRC0ALMIY02Z",
      "PostDiscoveryCompleteTimeStamp": "2024-04-24T21:32:19Z",
      "PostDiscoveryMode": "Auto",
      "PostMode": "Normal",
      "PostState": "InPostDiscoveryComplete",
      "PowerAutoOn": "Restore",
      "PowerOnDelay": "Minimum",
      "PowerOnMinutes": 0,
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
      "ServerFQDN": "welktxsr-931883-rh-le093s6-012.faredge.vzwops.com",
      "ServerIntelligentDiagnosticsModeEnabled": false,
      "ServerSafeModeEnabled": false,
      "SystemROMAndiLOEraseComponentStatus": {
        "BIOSSettingsEraseStatus": "Idle",
        "iLOSettingsEraseStatus": "Idle"
      },
      "SystemROMAndiLOEraseStatus": "Idle",
      "SystemUsage": {
        "AvgCPU0Freq": 52,
        "CPU0Power": 73,
        "CPUICUtil": 0,
        "CPUUtil": 3,
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
  "SerialNumber": "MXQ346090C",
  "Status": {
    "Health": "Warning",
    "HealthRollup": "Warning",
    "State": "Starting"
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
  "UUID": "35383450-3134-584D-5133-343630393043"
}
(hpe_fw) [XXXXXX@welktxefnce-h-pe1util-vm01 ZT-Triton-BMC-update-Redfish-v2.27.00-x86_64_20231027]$

(hpe_fw) [XXXXXX@welktxefnce-h-pe1util-vm01 ZT-Triton-BMC-update-Redfish-v2.27.00-x86_64_20231027]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[$ILO]/redfish/v1/Systems/1/Bios | jq .
{
  "@Redfish.Settings": {
    "@odata.type": "#Settings.v1_0_0.Settings",
    "ETag": "295C613B",
    "Messages": [
      {
        "MessageId": "Base.1.0.Success"
      }
    ],
    "SettingsObject": {
      "@odata.id": "/redfish/v1/systems/1/bios/settings/"
    },
    "Time": "2024-04-24T21:00:04+00:00"
  },
  "@odata.context": "/redfish/v1/$metadata#Bios.Bios",
  "@odata.etag": "W/\"F036DEEF265E8E8E8E275D549BD48FFC\"",
  "@odata.id": "/redfish/v1/systems/1/bios/",
  "@odata.type": "#Bios.v1_0_4.Bios",
  "Actions": {
    "#Bios.ChangePassword": {
      "target": "/redfish/v1/systems/1/bios/Actions/Bios.ChangePasswords/"
    },
    "#Bios.ResetBios": {
      "target": "/redfish/v1/systems/1/bios/Actions/Bios.ResetBios/"
    }
  },
  "AttributeRegistry": "BiosAttributeRegistryH11.v1_1_11",
  "Attributes": {
    "AccessControlService": "Enabled",
    "AcpiHpet": "Enabled",
    "AcpiRootBridgePxm": "Enabled",
    "AcpiSlit": "Enabled",
    "AdjSecPrefetch": "Enabled",
    "AdminEmail": "",
    "AdminName": "",
    "AdminOtherInfo": "",
    "AdminPhone": "",
    "AdvCrashDumpMode": "Disabled",
    "AdvancedMemProtection": "AdvancedEcc",
    "AllowLoginWithIlo": "Disabled",
    "AssetTagProtection": "Unlocked",
    "AutoPowerOn": "RestoreLastState",
    "BootOrderPolicy": "RetryIndefinitely",
    "CollabPowerControl": "Disabled",
    "ConsistentDevNaming": "LomsAndSlots",
    "CustomPostMessage": "",
    "DaylightSavingsTime": "DaylightSavingsTimeDisabled",
    "DcuIpPrefetcher": "Enabled",
    "DcuStreamPrefetcher": "Enabled",
    "DeadBlockPredictor": "Disabled",
    "Dhcpv4": "Enabled",
    "DisableDynamicLoadlineSwitch": "NotDisableDLLSwitch",
    "DramRapl": 0,
    "DramRaplLimit": "Disabled",
    "DramRaplReport": "Enabled",
    "DynamicIntelSpeedSelectMode": "Disabled",
    "DynamicPowerCapping": "Disabled",
    "EmbSata1Aspm": "Disabled",
    "EmbSata1Enable": "Auto",
    "EmbSata1PCIeOptionROM": "Enabled",
    "EmbSata2Aspm": "Disabled",
    "EmbSata2Enable": "Auto",
    "EmbSata2PCIeOptionROM": "Enabled",
    "EmbSata3Aspm": "Disabled",
    "EmbSata3Enable": "Auto",
    "EmbSata3PCIeOptionROM": "Enabled",
    "EmbVideoConnection": "Auto",
    "EmbeddedDiagnostics": "Enabled",
    "EmbeddedIpxe": "Enabled",
    "EmbeddedSata": "Ahci",
    "EmbeddedSerialPort": "Com2Irq3",
    "EmbeddedUefiShell": "Enabled",
    "EmsConsole": "Disabled",
    "EnabledCoresPerProc": 0,
    "EnergyEfficientTurbo": "Disabled",
    "EnergyPerfBias": "MaxPerf",
    "EnergyPerformancePreference": "Disabled",
    "EppProfile": "Disabled",
    "EraseUserDefaults": "No",
    "ExtendedAmbientTemp": "Disabled",
    "ExtendedMemTest": "Disabled",
    "F11BootMenu": "Enabled",
    "FCScanPolicy": "CardConfig",
    "FanFailPolicy": "Shutdown",
    "FanInstallReq": "EnableMessaging",
    "HourFormat": "24Hours",
    "HttpSupport": "Auto",
    "HwPrefetcher": "Enabled",
    "IODCConfiguration": "Auto",
    "IntelDmiLinkFreq": "Auto",
    "IntelNicDmaChannels": "Enabled",
    "IntelPchVmdSupport": "Disabled",
    "IntelPriorityCorePower": "Disabled",
    "IntelProcVtd": "Enabled",
    "IntelSpeedSelectConfigLevel": "Base",
    "IntelTxt": "Disabled",
    "IntelVmdDirectAssign": "VmdDirectAssignEnabledAll",
    "IntelVmdSupport": "Disabled",
    "IntelVrocSupport": "None",
    "IntelligentProvisioning": "Enabled",
    "IoatSnoopResponseHoldOff": "7",
    "IpmiWatchdogTimerAction": "PowerCycle",
    "IpmiWatchdogTimerStatus": "IpmiWatchdogTimerOff",
    "IpmiWatchdogTimerTimeout": "Timeout30Min",
    "Ipv4Address": "0.0.0.0",
    "Ipv4Gateway": "0.0.0.0",
    "Ipv4PrimaryDNS": "0.0.0.0",
    "Ipv4SubnetMask": "0.0.0.0",
    "Ipv6Address": "::",
    "Ipv6ConfigPolicy": "Automatic",
    "Ipv6Duid": "Auto",
    "Ipv6Gateway": "::",
    "Ipv6PrimaryDNS": "::",
    "IpxeAutoStartScriptLocation": "Auto",
    "IpxeBootOrder": "Disabled",
    "IpxeScriptAutoStart": "Disabled",
    "IpxeScriptVerification": "Disabled",
    "IpxeStartupUrl": "",
    "LLCDeadLineAllocation": "Enabled",
    "LlcPrefetch": "Disabled",
    "MaxMemBusFreqMHz": "Auto",
    "MaxPcieSpeed": "PerPortCtrl",
    "MemClearWarmReset": "Disabled",
    "MemFastTraining": "Enabled",
    "MemMirrorMode": "Full",
    "MemPatrolScrubbing": "Disabled",
    "MemRefreshRate": "Refreshx1",
    "MemoryConfigurationViolationReporting": "Enabled",
    "MemoryPermanentFaultDetect": "Enabled",
    "MemoryRemap": "NoAction",
    "MicrosoftSecuredCoreSupport": "Disabled",
    "MinProcIdlePkgState": "NoState",
    "MinProcIdlePower": "C6",
    "MixedPowerSupplyReporting": "Enabled",
    "MkTme": "Disabled",
    "NetworkBootRetry": "Enabled",
    "NetworkBootRetryCount": 20,
    "NicBoot1": "NetworkBoot",
    "Numa": "Enabled",
    "NumaGroupSizeOpt": "Clustered",
    "NvmeOptionRom": "Enabled",
    "OmitBootDeviceEvent": "Disabled",
    "OptimizedPowerMode": "Disabled",
    "OsbLocalRemoteRead": "Auto",
    "PatrolScrubDuration": 24,
    "PchCrashLogFeature": "Disabled",
    "PciResourcePadding": "Disabled",
    "PciSlot17LinkSpeed": "Auto",
    "PciSlot1Aspm": "Disabled",
    "PciSlot1Bifurcation": "NoBifurcation",
    "PciSlot1Enable": "Auto",
    "PciSlot1LinkSpeed": "Auto",
    "PciSlot1OptionROM": "Enabled",
    "PciSlot2Aspm": "Disabled",
    "PciSlot2Bifurcation": "NoBifurcation",
    "PciSlot2Enable": "Auto",
    "PciSlot2LinkSpeed": "Auto",
    "PciSlot2OptionROM": "Enabled",
    "PciSlot3Aspm": "Disabled",
    "PciSlot3Bifurcation": "NoBifurcation",
    "PciSlot3Enable": "Auto",
    "PciSlot3LinkSpeed": "Auto",
    "PciSlot3OptionROM": "Enabled",
    "PcieHotPlugErrControl": "HotplugSurprise",
    "PcuPMax": 0,
    "PersistentMemBackupPowerPolicy": "WaitForBackupPower",
    "PlatformCertificate": "Enabled",
    "PlatformRASPolicy": "FirmwareFirst",
    "PostAsr": "PostAsrOff",
    "PostAsrDelay": "Delay30Min",
    "PostBootProgress": "Disabled",
    "PostDiscoveryMode": "Auto",
    "PostF1Prompt": "Delayed20Sec",
    "PostScreenMode": "VerboseMode",
    "PostVideoSupport": "DisplayAll",
    "PowerButton": "Enabled",
    "PowerOnDelay": "NoDelay",
    "PowerRegulator": "OsControl",
    "PreBootNetwork": "Auto",
    "PrebootNetworkEnvPolicy": "Auto",
    "PrebootNetworkProxy": "",
    "ProcAes": "Enabled",
    "ProcHyperthreading": "Enabled",
    "ProcRapl": 0,
    "ProcTurbo": "Enabled",
    "ProcVirtualization": "Enabled",
    "ProcX2Apic": "ForceEnabled",
    "ProcessorConfigTDPLevel": "Level2",
    "ProcessorPhysicalAddress": "Limited",
    "ProcessorUuidControl": "LockDisable",
    "ProductId": "P48541-B21",
    "RedundantPowerSupplyGpuDomain": "BalancedMode",
    "RedundantPowerSupplySystemDomain": "BalancedMode",
    "RestoreDefaults": "No",
    "RestoreManufacturingDefaults": "No",
    "RomSelection": "CurrentRom",
    "SataSanitize": "Disabled",
    "SataSecureErase": "Disabled",
    "SaveUserDefaults": "No",
    "SciRasSupport": "Ghesv2Support",
    "SecStartBackupImage": "Disabled",
    "SecureBootStatus": "Disabled",
    "SerialConsoleBaudRate": "BaudRate115200",
    "SerialConsoleEmulation": "Vt100Plus",
    "SerialConsolePort": "Auto",
    "SerialNumber": "MXQ346090C",
    "SerialPortDtrSupport": "Disabled",
    "ServerAssetTag": "",
    "ServerConfigLockStatus": "Disabled",
    "ServerName": "welktxsr-931883-rh-le093s6-0",
    "ServerOtherInfo": "",
    "ServerPrimaryOs": "",
    "ServiceEmail": "",
    "ServiceName": "",
    "ServiceOtherInfo": "",
    "ServicePhone": "",
    "SetupBrowserSelection": "Auto",
    "SgxAutoMpRegistrationAgent": "Enabled",
    "SgxEnable": "Disabled",
    "SgxFactoryReset": "Disabled",
    "SgxLaunchControlPolicy": "IntelLocked",
    "SgxLePublicKeyHash0": "",
    "SgxLePublicKeyHash1": "",
    "SgxLePublicKeyHash2": "",
    "SgxLePublicKeyHash3": "",
    "SgxLePublicKeyWriteEnable": "Enabled",
    "SgxPrmrrSize": "2Gb",
    "Slot1EoiBroadcastSupport": "Disabled",
    "Slot1MctpBroadcastSupport": "Enabled",
    "Slot1NicBoot1": "NetworkBoot",
    "Slot1NicBoot2": "Disabled",
    "Slot1NicBoot3": "Disabled",
    "Slot1NicBoot4": "Disabled",
    "Slot2EoiBroadcastSupport": "Disabled",
    "Slot2MctpBroadcastSupport": "Enabled",
    "Slot2NicBoot1": "NetworkBoot",
    "Slot2NicBoot2": "Disabled",
    "Slot2NicBoot3": "Disabled",
    "Slot2NicBoot4": "Disabled",
    "Slot3EoiBroadcastSupport": "Disabled",
    "Slot3MctpBroadcastSupport": "Enabled",
    "Slot3NicBoot1": "NetworkBoot",
    "Slot3NicBoot2": "Disabled",
    "Slot3NicBoot3": "Disabled",
    "Slot3NicBoot4": "Disabled",
    "SnoopResponseHoldOff": "9",
    "Sriov": "Enabled",
    "StaleAtoS": "Auto",
    "SubNumaClustering": "Disabled",
    "TPM2EndorsementDisable": "Enabled",
    "TPM2StorageDisable": "Enabled",
    "ThermalConfig": "OptimalCooling",
    "ThermalShutdown": "Enabled",
    "TimeFormat": "Utc",
    "TimeZone": "Unspecified",
    "Tme": "Disabled",
    "TmeExclusiveBase": "",
    "TmeExclusiveLen": "",
    "Tpm20SoftwareInterfaceStatus": "Fifo",
    "Tpm2Operation": "NoAction",
    "TpmActivePcrs": "Sha256Sha384",
    "TpmChipId": "STMicroGen11",
    "TpmState": "PresentEnabled",
    "TpmUefiOpromMeasuring": "Enabled",
    "TpmVisibility": "Visible",
    "Tsx": "Enabled",
    "UefiSerialDebugLevel": "ErrorsOnly",
    "UefiShellBootOrder": "Disabled",
    "UefiShellPhysicalPresenceKeystroke": "Enabled",
    "UefiShellScriptVerification": "Disabled",
    "UefiShellStartup": "Disabled",
    "UefiShellStartupLocation": "Auto",
    "UefiShellStartupUrl": "",
    "UefiShellStartupUrlFromDhcp": "Disabled",
    "UefiVariableAccessFwControl": "Disabled",
    "UncoreFreqScaling": "Custom",
    "UncoreFrequencyMAX": 0,
    "UncoreFrequencyMIN": 0,
    "UrlBootFile": "",
    "UrlBootFile2": "",
    "UrlBootFile3": "",
    "UrlBootFile4": "",
    "UsbBoot": "Enabled",
    "UsbControl": "UsbEnabled",
    "UserDefaultsState": "Disabled",
    "UtilityLang": "English",
    "VirtualNuma": "Disabled",
    "VirtualSerialPort": "Com1Irq4",
    "VlanControl": "Disabled",
    "VlanId": 0,
    "VlanPriority": 0,
    "WakeOnLan": "Enabled",
    "WorkloadProfile": "vRAN",
    "iSCSISoftwareInitiator": "Enabled"
  },
  "Id": "bios",
  "Name": "BIOS Current Settings",
  "Oem": {
    "Hpe": {
      "@odata.type": "#HpeBiosExt.v2_0_0.HpeBiosExt",
      "Links": {
        "BaseConfigs": {
          "@odata.id": "/redfish/v1/systems/1/bios/oem/hpe/baseconfigs/"
        },
        "Boot": {
          "@odata.id": "/redfish/v1/systems/1/bios/oem/hpe/boot/"
        },
        "KmsConfig": {
          "@odata.id": "/redfish/v1/systems/1/bios/oem/hpe/kmsconfig/"
        },
        "Mappings": {
          "@odata.id": "/redfish/v1/systems/1/bios/oem/hpe/mappings/"
        },
        "ServerConfigLock": {
          "@odata.id": "/redfish/v1/systems/1/bios/oem/hpe/serverconfiglock/"
        },
        "TlsConfig": {
          "@odata.id": "/redfish/v1/systems/1/bios/oem/hpe/tlsconfig/"
        },
        "iScsi": {
          "@odata.id": "/redfish/v1/systems/1/bios/oem/hpe/iscsi/"
        }
      },
      "SettingsObject": {
        "UnmodifiedETag": "W/\"30651442DBDBB1B1B1F1464EF30C05F0\""
      }
    }
  }
}
(hpe_fw) [XXXXXX@welktxefnce-h-pe1util-vm01 ZT-Triton-BMC-update-Redfish-v2.27.00-x86_64_20231027]$

```

## Workload profile is "vRAN"
## ILO was configured with all attributes from bmc playbook, screen shots will be uploaded as well of ILO GUI


## MEAKV-1750 is a pass, with one recorded issue to followup on 
## After factory reset 

    "WorkloadProfile": "GeneralPowerEfficientCompute",


## After BMC playbook run

    "WorkloadProfile": "vRAN",


### I have contacted HP David Spinks to investigate 

