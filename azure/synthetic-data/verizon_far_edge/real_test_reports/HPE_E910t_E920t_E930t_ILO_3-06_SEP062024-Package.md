# HPE ILO5 3.06
# HPE E910t server BIOS H08 2.12
# HPE E920t server BIOS H10 1.70
# 9/6/24 James Patchett - MTCE Lab VCPfe



## e920t Rollback to 2.66

```log
[XXXXXX@welktxefnce-h-pe1util-vm01 EL8000t-Firmware-Update-Scripts-Sep06-2024]$ cat hostnames-e920t.yaml
# e920t
- "2607:f160:10:9249:ce:40a:0:e009"
[XXXXXX@welktxefnce-h-pe1util-vm01 EL8000t-Firmware-Update-Scripts-Sep06-2024]$

(hpe_fw) [XXXXXX@welktxefnce-h-pe1util-vm01 EL8000t-Firmware-Update-Scripts-Sep06-2024]$ python ./ilo_fw_updater.py --hostnames ./hostnames-e920t.yaml --username XXXXXX --password XXXXXX --packageDir ./firmware_recipes/e920t_rollback --logsDir ./logs --process ./firmware_recipes/e920t_rollback/process_e920t_rollback-ALL-ILO266.yaml --model e920t --biosupdate rollback
Start firmware update process at 2024/09/06 16:29:44
Overall firmware update progress: 100%|████████████████████████████████████████████████████| 1/1 [28:36<00:00, 1716.43s/iterating iLO5]
Elapsed time: 0:28:36.511025
Running the BIOS update script.
Overall BIOS update progress: 100%|█████████████████████████████████████████████████████████| 1/1 [04:31<00:00, 271.98s/iterating iLO5]
Exiting the program...
(hpe_fw) [XXXXXX@welktxefnce-h-pe1util-vm01 EL8000t-Firmware-Update-Scripts-Sep06-2024]$
```
## Redfish BIOS Settings

```log
[XXXXXX@welktxefnce-h-pe1util-vm01 EL8000t-Firmware-Update-Scripts-Sep06-2024]$ IP=2607:f160:10:9249:ce:40a:0:e009
[XXXXXX@welktxefnce-h-pe1util-vm01 EL8000t-Firmware-Update-Scripts-Sep06-2024]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[$IP]/redfish/v1/Systems/1/bios/settings |jq .
{
  "@odata.context": "/redfish/v1/$metadata#Bios.Bios",
  "@odata.etag": "W/\"4B76454AF9F4A7A7A796BD432C41FE2E\"",
  "@odata.id": "/redfish/v1/systems/1/bios/settings/",
  "@odata.type": "#Bios.v1_0_4.Bios",
  "AttributeRegistry": "BiosAttributeRegistryH10.v1_1_40",
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
    "AdvancedMemProtection": "Auto",
    "AllowLoginWithIlo": "Disabled",
    "AssetTagProtection": "Unlocked",
    "AutoPowerOn": "RestoreLastState",
    "BootMode": "Uefi",
    "BootOrderPolicy": "RetryIndefinitely",
    "CollabPowerControl": "Disabled",
    "ConsistentDevNaming": "LomsAndSlots",
    "CustomPostMessage": "",
    "DaylightSavingsTime": "DaylightSavingsTimeDisabled",
    "DcuIpPrefetcher": "Enabled",
    "DcuStreamPrefetcher": "Enabled",
    "DeadBlockPredictor": "Disabled",
    "Dhcpv4": "Enabled",
    "DramRapl": 0,
    "DramRaplLimit": "Disabled",
    "DramRaplReport": "Enabled",
    "EmbNicEnable": "Auto",
    "EmbNicLinkSpeed": "Auto",
    "EmbNicPCIeOptionROM": "Enabled",
    "EmbVideoConnection": "Auto",
    "EmbeddedDiagnostics": "Enabled",
    "EmbeddedIpxe": "Enabled",
    "EmbeddedSata": "Ahci",
    "EmbeddedUefiShell": "Enabled",
    "EmsConsole": "Disabled",
    "EnabledCoresPerProc": 0,
    "EnergyEfficientTurbo": "Disabled",
    "EnergyPerfBias": "MaxPerf",
    "EnhancedProcPerf": "Disabled",
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
    "IntelPerfMonitoring": "Disabled",
    "IntelPriorityBaseFreq": "Disabled",
    "IntelProcVtd": "Enabled",
    "IntelTxt": "Disabled",
    "IntelVmdSupport": "Disabled",
    "IntelVrocSupport": "None",
    "IntelligentProvisioning": "Enabled",
    "IpmiWatchdogTimerPolicy": "PowerCycle",
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
    "LlcPrefetch": "Enabled",
    "LocalRemoteThreshold": "Auto",
    "MaxMemBusFreqMHz": "Auto",
    "MaxPcieSpeed": "PerPortCtrl",
    "MemClearWarmReset": "Disabled",
    "MemFastTraining": "Enabled",
    "MemMirrorMode": "Full",
    "MemPatrolScrubbing": "Enabled",
    "MemRefreshRate": "Refreshx1",
    "MemoryConfigurationViolationReporting": "Enabled",
    "MemoryRemap": "NoAction",
    "MinProcIdlePkgState": "NoState",
    "MinProcIdlePower": "NoCStates",
    "MixedPowerSupplyReporting": "Enabled",
    "MkTme": "Disabled",
    "NetworkBootRetry": "Enabled",
    "NetworkBootRetryCount": 20,
    "NicBoot1": "NetworkBoot",
    "NoExecutionProtection": "Enabled",
    "Numa": "Enabled",
    "NumaGroupSizeOpt": "Clustered",
    "NvmeOptionRom": "Enabled",
    "NvmePort1": "Nvme",
    "NvmePort10": "Nvme",
    "NvmePort11": "Nvme",
    "NvmePort12": "Nvme",
    "NvmePort13": "Nvme",
    "NvmePort14": "Nvme",
    "NvmePort15": "Nvme",
    "NvmePort16": "Nvme",
    "NvmePort2": "Nvme",
    "NvmePort3": "Nvme",
    "NvmePort4": "Nvme",
    "NvmePort5": "Nvme",
    "NvmePort6": "Nvme",
    "NvmePort7": "Nvme",
    "NvmePort8": "Nvme",
    "NvmePort9": "Nvme",
    "NvmeRaid": "Disabled",
    "PatrolScrubDuration": 24,
    "PciPeerToPeerSerialization": "Disabled",
    "PciResourcePadding": "Normal",
    "PciSlot1Aspm": "Disabled",
    "PciSlot1Bifurcation": "Auto",
    "PciSlot1Enable": "Auto",
    "PciSlot1LinkSpeed": "Auto",
    "PciSlot1OptionROM": "Enabled",
    "PciSlot2Aspm": "Disabled",
    "PciSlot2Bifurcation": "Auto",
    "PciSlot2Enable": "Auto",
    "PciSlot2LinkSpeed": "Auto",
    "PciSlot2OptionROM": "Enabled",
    "PciSlot3Aspm": "Disabled",
    "PciSlot3Bifurcation": "Auto",
    "PciSlot3Enable": "Auto",
    "PciSlot3LinkSpeed": "Auto",
    "PciSlot3OptionROM": "Enabled",
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
    "PowerRegulator": "StaticHighPerf",
    "PreBootNetwork": "Auto",
    "PrebootNetworkEnvPolicy": "Auto",
    "PrebootNetworkProxy": "",
    "ProcAes": "Enabled",
    "ProcHyperthreading": "Enabled",
    "ProcRapl": 0,
    "ProcTurbo": "Enabled",
    "ProcVirtualization": "Enabled",
    "ProcX2Apic": "Enabled",
    "ProcessorConfigTDPLevel": "Level2",
    "ProcessorJitterControl": "Disabled",
    "ProcessorJitterControlFrequency": 0,
    "ProcessorJitterControlOptimization": "ZeroLatency",
    "ProcessorPhysicalAddress": "Limited",
    "ProductId": "P40893-B21",
    "RemoteXptPrefetcher": "Auto",
    "RemovableFlashBootSeq": "ExternalKeysFirst",
    "RestoreDefaults": "No",
    "RestoreManufacturingDefaults": "No",
    "RomSelection": "CurrentRom",
    "SataSanitize": "Disabled",
    "SataSecureErase": "Disabled",
    "SaveUserDefaults": "No",
    "SciRasSupport": "Ghesv1Support",
    "SecStartBackupImage": "Disabled",
    "SecureBootStatus": "Disabled",
    "SerialConsoleBaudRate": "BaudRate115200",
    "SerialConsoleEmulation": "Vt100Plus",
    "SerialConsolePort": "Auto",
    "SerialNumber": "MXQ1370PP6",
    "SerialPortDtrSupport": "Disabled",
    "ServerAssetTag": "",
    "ServerConfigLockStatus": "Disabled",
    "ServerName": "welktxef-931884-rh-le092s6-0",
    "ServerOtherInfo": "",
    "ServerPrimaryOs": "",
    "ServiceEmail": "",
    "ServiceName": "",
    "ServiceOtherInfo": "",
    "ServicePhone": "",
    "SetupBrowserSelection": "Auto",
    "SgxAutoMpRegistrationAgent": "Enabled",
    "SgxEnable": "Disabled",
    "SgxLaunchControlPolicy": "IntelLocked",
    "SgxLePublicKeyHash0": "",
    "SgxLePublicKeyHash1": "",
    "SgxLePublicKeyHash2": "",
    "SgxLePublicKeyHash3": "",
    "SgxLePublicKeyWriteEnable": "Enabled",
    "SgxPrmrrSize": "2Gb",
    "Slot1MctpBroadcastSupport": "Enabled",
    "Slot1NicBoot1": "NetworkBoot",
    "Slot1NicBoot2": "Disabled",
    "Slot1NicBoot3": "Disabled",
    "Slot1NicBoot4": "Disabled",
    "Slot2MctpBroadcastSupport": "Enabled",
    "Slot2NicBoot1": "NetworkBoot",
    "Slot2NicBoot2": "Disabled",
    "Slot2NicBoot3": "Disabled",
    "Slot2NicBoot4": "Disabled",
    "Slot3MctpBroadcastSupport": "Enabled",
    "Sriov": "Enabled",
    "StaleAtoS": "Disabled",
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
    "Tpm20SoftwareInterfaceOperation": "NoAction",
    "Tpm20SoftwareInterfaceStatus": "Fifo",
    "Tpm2Operation": "NoAction",
    "TpmActivePcrs": "Sha1Sha256",
    "TpmChipId": "STMicroGen10Plus",
    "TpmFips": "FipsMode",
    "TpmFipsModeSwitch": "NoAction",
    "TpmModeSwitchOperation": "NoAction",
    "TpmState": "PresentEnabled",
    "TpmType": "Tpm20",
    "TpmUefiOpromMeasuring": "Enabled",
    "TpmVisibility": "Visible",
    "Tsx": "Enabled",
    "UefiOptimizedBoot": "Enabled",
    "UefiSerialDebugLevel": "ErrorsOnly",
    "UefiShellBootOrder": "Disabled",
    "UefiShellPhysicalPresenceKeystroke": "Enabled",
    "UefiShellScriptVerification": "Disabled",
    "UefiShellStartup": "Disabled",
    "UefiShellStartupLocation": "Auto",
    "UefiShellStartupUrl": "",
    "UefiShellStartupUrlFromDhcp": "Disabled",
    "UncoreFreqScaling": "Maximum",
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
    "VmdonCpu1Stack5Port2": "Disabled",
    "VmdonCpu1Stack5Port3": "Disabled",
    "WakeOnLan": "Enabled",
    "WorkloadProfile": "Custom",
    "XptPrefetcher": "Auto",
    "iSCSISoftwareInitiator": "Enabled"
  },
  "Id": "settings",
  "Name": "BIOS Pending Settings"
}
[XXXXXX@welktxefnce-h-pe1util-vm01 EL8000t-Firmware-Update-Scripts-Sep06-2024]$
```

## ILO 2.66 BIOS settings we need to validate with the rollback


bios_attribute_name_workload_profile: WorkloadProfile
    "WorkloadProfile": "Custom",

bios_attribute_name_proc_virtualization: ProcVirtualization
    "ProcVirtualization": "Enabled",

bios_attribute_value_sriov: Enabled
    "Sriov": "Enabled",

bios_attribute_name_pci_slot1_enable: PciSlot1Enable
    "PciSlot1Enable": "Auto",

bios_attribute_name_sub_numa_clustering: SubNumaClustering
    "SubNumaClustering": "Disabled",

bios_attribute_name_min_proc_idle_power: MinProcIdlePower
    "MinProcIdlePower": "NoCStates",

bios_attribute_name_proc_turbo: ProcTurbo
    "ProcTurbo": "Enabled",

bios_attribute_name_proc_hyperthreading: ProcHyperthreading
    "ProcHyperthreading": "Enabled",

bios_attribute_name_llc_prefetch: LlcPrefetch
    "LlcPrefetch": "Enabled",

bios_attribute_name_processor_config_tdp_level: ProcessorConfigTDPLevel
    "ProcessorConfigTDPLevel": "Level2",


## Will come back and validate settings are correct ******************************

## ILO 3.06 Upgrade with BIOS settings

```log
(hpe_fw) [XXXXXX@welktxefnce-h-pe1util-vm01 EL8000t-Firmware-Update-Scripts-Sep06-2024]$ python ./ilo_fw_updater.py --hostnames ./hostnames-e920t.yaml --username XXXXXX --password XXXXXX --packageDir ./firmware_recipes/e920t_upgrade --logsDir ./logs --process ./firmware_recipes/e920t_upgrade/process_e920t_upgrade-upload-apply-ALL-ILO306.yaml --model e920t --biosupdate upgrade --dryrun
Start firmware update process at 2024/09/06 18:01:44
Overall firmware update progress: 100%|██████████████████████████████████████████████████████| 1/1 [00:04<00:00,  4.44s/iterating iLO5]
Elapsed time: 0:00:04.531301
Not running BIOS update script because this is a dryrun.
(hpe_fw) [XXXXXX@welktxefnce-h-pe1util-vm01 EL8000t-Firmware-Update-Scripts-Sep06-2024]$ python ./ilo_fw_updater.py --hostnames ./hostnames-e920t.yaml --username XXXXXX --password XXXXXX --packageDir ./firmware_recipes/e920t_upgrade --logsDir ./logs --process ./firmware_recipes/e920t_upgrade/process_e920t_upgrade-upload-apply-ALL-ILO306.yaml --model e920t --biosupdate upgrade
Start firmware update process at 2024/09/06 18:02:35
Overall firmware update progress:   0%|                                                                                                                                       Overall firmware update progress: 100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████Overall firmware update progress: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 1/1 [27:33<00:00, 1653.36s/iterating iLO5]
Elapsed time: 0:27:33.452786
Running the BIOS update script.
Overall BIOS update progress: 100%|█████████████████████████████████████████████████████████████████████████████████████████████████| 1/1 [00:19<00:00, 19.94s/iterating iLO5]
Exiting the program...
(hpe_fw) [XXXXXX@welktxefnce-h-pe1util-vm01 EL8000t-Firmware-Update-Scripts-Sep06-2024]$


```

## Redfish bios settings

```log
[XXXXXX@welktxefnce-h-pe1util-vm01 logs]$ IP=2607:f160:10:9249:ce:40a:0:e009
[XXXXXX@welktxefnce-h-pe1util-vm01 logs]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[$IP]/redfish/v1/Systems/1/bios/settings |jq .
{
  "@odata.context": "/redfish/v1/$metadata#Bios.Bios",
  "@odata.etag": "W/\"4AC96E7E56B847474744AF1AED6296B3\"",
  "@odata.id": "/redfish/v1/systems/1/bios/settings/",
  "@odata.type": "#Bios.v1_0_4.Bios",
  "AttributeRegistry": "BiosAttributeRegistryH10.v1_1_70",
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
    "AdvancedMemProtection": "Auto",
    "AllowLoginWithIlo": "Disabled",
    "AssetTagProtection": "Unlocked",
    "AutoPowerOn": "RestoreLastState",
    "BootMode": "Uefi",
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
    "EmbNicEnable": "Auto",
    "EmbNicLinkSpeed": "Auto",
    "EmbNicPCIeOptionROM": "Enabled",
    "EmbVideoConnection": "Auto",
    "EmbeddedDiagnostics": "Enabled",
    "EmbeddedIpxe": "Enabled",
    "EmbeddedSata": "Ahci",
    "EmbeddedUefiShell": "Enabled",
    "EmsConsole": "Disabled",
    "EnabledCoresPerProc": 0,
    "EnergyEfficientTurbo": "Disabled",
    "EnergyPerfBias": "MaxPerf",
    "EnergyPerformancePreference": "Disabled",
    "EnhancedProcPerf": "Disabled",
    "EppProfile": "Moderate",
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
    "IntelPerfMonitoring": "Disabled",
    "IntelPriorityBaseFreq": "Disabled",
    "IntelProcVtd": "Enabled",
    "IntelTxt": "Disabled",
    "IntelVmdDirectAssign": "Disabled",
    "IntelVmdSupport": "Disabled",
    "IntelVrocSupport": "None",
    "IntelligentProvisioning": "Enabled",
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
    "LlcPrefetch": "Enabled",
    "LocalRemoteThreshold": "Auto",
    "MaxMemBusFreqMHz": "Auto",
    "MaxPcieSpeed": "PerPortCtrl",
    "MemClearWarmReset": "Disabled",
    "MemFastTraining": "Enabled",
    "MemMirrorMode": "Full",
    "MemPatrolScrubbing": "Disabled",
    "MemRefreshRate": "Refreshx1",
    "MemoryConfigurationViolationReporting": "Enabled",
    "MemoryRemap": "NoAction",
    "MicrosoftSecuredCoreSupport": "Disabled",
    "MinProcIdlePkgState": "NoState",
    "MinProcIdlePower": "C6",
    "MixedPowerSupplyReporting": "Enabled",
    "MkTme": "Disabled",
    "NetworkBootRetry": "Enabled",
    "NetworkBootRetryCount": 20,
    "NicBoot1": "NetworkBoot",
    "NoExecutionProtection": "Enabled",
    "Numa": "Enabled",
    "NumaGroupSizeOpt": "Clustered",
    "NvmeOptionRom": "Enabled",
    "NvmePort1": "Nvme",
    "NvmePort10": "Nvme",
    "NvmePort11": "Nvme",
    "NvmePort12": "Nvme",
    "NvmePort13": "Nvme",
    "NvmePort14": "Nvme",
    "NvmePort15": "Nvme",
    "NvmePort16": "Nvme",
    "NvmePort2": "Nvme",
    "NvmePort3": "Nvme",
    "NvmePort4": "Nvme",
    "NvmePort5": "Nvme",
    "NvmePort6": "Nvme",
    "NvmePort7": "Nvme",
    "NvmePort8": "Nvme",
    "NvmePort9": "Nvme",
    "NvmeRaid": "Disabled",
    "OmitBootDeviceEvent": "Disabled",
    "PatrolScrubDuration": 24,
    "PciPeerToPeerSerialization": "Disabled",
    "PciResourcePadding": "Normal",
    "PciSlot1Aspm": "Disabled",
    "PciSlot1Bifurcation": "Auto",
    "PciSlot1Enable": "Auto",
    "PciSlot1LinkSpeed": "Auto",
    "PciSlot1OptionROM": "Enabled",
    "PciSlot2Aspm": "Disabled",
    "PciSlot2Bifurcation": "Auto",
    "PciSlot2Enable": "Auto",
    "PciSlot2LinkSpeed": "Auto",
    "PciSlot2OptionROM": "Enabled",
    "PciSlot3Aspm": "Disabled",
    "PciSlot3Bifurcation": "Auto",
    "PciSlot3Enable": "Auto",
    "PciSlot3LinkSpeed": "Auto",
    "PciSlot3OptionROM": "Enabled",
    "PcieHotPlugErrControl": "HotplugSurprise",
    "PcuPMax": 0,
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
    "ProcX2Apic": "Enabled",
    "ProcessorConfigTDPLevel": "Level2",
    "ProcessorPhysicalAddress": "Limited",
    "ProcessorUuidControl": "LockDisable",
    "RemoteXptPrefetcher": "Auto",
    "RemovableFlashBootSeq": "ExternalKeysFirst",
    "RestoreDefaults": "No",
    "RestoreManufacturingDefaults": "No",
    "RomSelection": "CurrentRom",
    "SataSanitize": "Disabled",
    "SataSecureErase": "Disabled",
    "SaveUserDefaults": "No",
    "SciRasSupport": "Ghesv1Support",
    "SecStartBackupImage": "Disabled",
    "SecureBootStatus": "Disabled",
    "SerialConsoleBaudRate": "BaudRate115200",
    "SerialConsoleEmulation": "Vt100Plus",
    "SerialConsolePort": "Auto",
    "SerialNumber": "MXQ1370PP6",
    "SerialPortDtrSupport": "Disabled",
    "ServerAssetTag": "",
    "ServerConfigLockStatus": "Disabled",
    "ServerName": "welktxef-931884-rh-le092s6-0",
    "ServerOtherInfo": "",
    "ServerPrimaryOs": "",
    "ServiceEmail": "",
    "ServiceName": "",
    "ServiceOtherInfo": "",
    "ServicePhone": "",
    "SetupBrowserSelection": "Auto",
    "SgxAutoMpRegistrationAgent": "Enabled",
    "SgxEnable": "Disabled",
    "SgxLaunchControlPolicy": "IntelLocked",
    "SgxLePublicKeyHash0": "",
    "SgxLePublicKeyHash1": "",
    "SgxLePublicKeyHash2": "",
    "SgxLePublicKeyHash3": "",
    "SgxLePublicKeyWriteEnable": "Enabled",
    "SgxPrmrrSize": "2Gb",
    "Slot1MctpBroadcastSupport": "Enabled",
    "Slot1NicBoot1": "NetworkBoot",
    "Slot1NicBoot2": "Disabled",
    "Slot1NicBoot3": "Disabled",
    "Slot1NicBoot4": "Disabled",
    "Slot2MctpBroadcastSupport": "Enabled",
    "Slot2NicBoot1": "NetworkBoot",
    "Slot2NicBoot2": "Disabled",
    "Slot2NicBoot3": "Disabled",
    "Slot2NicBoot4": "Disabled",
    "Slot3MctpBroadcastSupport": "Enabled",
    "SnoopResponseHoldOff": 0,
    "Sriov": "Enabled",
    "StaleAtoS": "Disabled",
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
    "Tpm20SoftwareInterfaceOperation": "NoAction",
    "Tpm20SoftwareInterfaceStatus": "Fifo",
    "Tpm2Operation": "NoAction",
    "TpmActivePcrs": "Sha1Sha256",
    "TpmChipId": "STMicroGen10Plus",
    "TpmFips": "FipsMode",
    "TpmFipsModeSwitch": "NoAction",
    "TpmModeSwitchOperation": "NoAction",
    "TpmState": "PresentEnabled",
    "TpmType": "Tpm20",
    "TpmUefiOpromMeasuring": "Enabled",
    "TpmVisibility": "Visible",
    "Tsx": "Enabled",
    "UefiOptimizedBoot": "Enabled",
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
    "UncoreFrequencyMAX": 24,
    "UncoreFrequencyMIN": 8,
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
    "VmdonCpu1Stack5Port2": "Disabled",
    "VmdonCpu1Stack5Port3": "Disabled",
    "WakeOnLan": "Enabled",
    "WorkloadProfile": "vRAN",
    "XptPrefetcher": "Auto",
    "iSCSISoftwareInitiator": "Enabled"
  },
  "Id": "settings",
  "Name": "BIOS Pending Settings"
}
[XXXXXX@welktxefnce-h-pe1util-vm01 logs]$
```

## BIOS settings is easy for e920t 3.06, just look for WorkloadProfile and ensure its set to "vRAN"

    "WorkloadProfile": "vRAN",

## Success


## e910t Rollback to 2.66

```log

(hpe_fw) [XXXXXX@welktxefnce-h-pe1util-vm01 EL8000t-Firmware-Update-Scripts-Sep06-2024]$ cat hostnames-e910t.yaml
# e910t
- "2607:f160:10:922a:ce:406:0:1000"
(hpe_fw) [XXXXXX@welktxefnce-h-pe1util-vm01 EL8000t-Firmware-Update-Scripts-Sep06-2024]$
(hpe_fw) [XXXXXX@welktxefnce-h-pe1util-vm01 EL8000t-Firmware-Update-Scripts-Sep06-2024]$ python ./ilo_fw_updater.py --hostnames ./hostnames-e910t.yaml --username XXXXXX --password XXXXXX --packageDir ./firmware_recipes/e910t_rollback --logsDir ./logs --process ./firmware_recipes/e910t_rollback/process_e910t_rollback-ALL-ILO266.yaml --model e910t --biosupdate rollback --dryrun
Start firmware update process at 2024/09/06 18:41:11
Overall firmware update progress: 100%|█████████████████████████████████████████████████████████████████████████████████████████████| 1/1 [00:06<00:00,  6.99s/iterating iLO5]
Elapsed time: 0:00:07.035290
Not running BIOS update script because this is a dryrun.
(hpe_fw) [XXXXXX@welktxefnce-h-pe1util-vm01 EL8000t-Firmware-Update-Scripts-Sep06-2024]$
(hpe_fw) [XXXXXX@welktxefnce-h-pe1util-vm01 EL8000t-Firmware-Update-Scripts-Sep06-2024]$ python ./ilo_fw_updater.py --hostnames ./hostnames-e910t.yaml --username XXXXXX --password XXXXXX --packageDir ./firmware_recipes/e910t_rollback --logsDir ./logs --process ./firmware_recipes/e910t_rollback/process_e910t_rollback-ALL-ILO266.yaml --model e910t --biosupdate rollback
Start firmware update process at 2024/09/06 18:41:51
Overall firmware update progress: 100%|███████████████████████████████████████████████████████████████████████████████████████████| 1/1 [29:47<00:00, 1787.60s/iterating iLO5]
Elapsed time: 0:29:47.649365
Running the BIOS update script.
Overall BIOS update progress: 100%|█████████████████████████████████████████████████████████████████████████████████████████████████| 1/1 [00:33<00:00, 33.44s/iterating iLO5]
Exiting the program...
(hpe_fw) [XXXXXX@welktxefnce-h-pe1util-vm01 EL8000t-Firmware-Update-Scripts-Sep06-2024]$
```

## Check the BIOS settings for rollback with e910t

```log
[XXXXXX@welktxefnce-h-pe1util-vm01 logs]$ IP=2607:f160:10:922a:ce:406:0:1000
[XXXXXX@welktxefnce-h-pe1util-vm01 logs]$
[XXXXXX@welktxefnce-h-pe1util-vm01 logs]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[$IP]/redfish/v1/Systems/1/bios/settings |jq .
{
  "@odata.context": "/redfish/v1/$metadata#Bios.Bios",
  "@odata.etag": "W/\"F2D80D1631A8F3F3F366F6BC5B312B74\"",
  "@odata.id": "/redfish/v1/systems/1/bios/settings/",
  "@odata.type": "#Bios.v1_0_0.Bios",
  "AttributeRegistry": "BiosAttributeRegistryH08.v1_1_40",
  "Attributes": {
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
    "AsrStatus": "Enabled",
    "AsrTimeoutMinutes": "Timeout10",
    "AssetTagProtection": "Unlocked",
    "AutoPowerOn": "RestoreLastState",
    "BootMode": "Uefi",
    "BootOrderPolicy": "RetryIndefinitely",
    "ChannelInterleaving": "Enabled",
    "CollabPowerControl": "Disabled",
    "ConsistentDevNaming": "LomsAndSlots",
    "CustomPostMessage": "",
    "DaylightSavingsTime": "Disabled",
    "DcuIpPrefetcher": "Enabled",
    "DcuStreamPrefetcher": "Enabled",
    "Dhcpv4": "Enabled",
    "DynamicPowerCapping": "Disabled",
    "EmbNicEnable": "Auto",
    "EmbNicLinkSpeed": "Auto",
    "EmbNicPCIeOptionROM": "Enabled",
    "EmbSas1Aspm": "Disabled",
    "EmbSata1Aspm": "Disabled",
    "EmbSata1Enable": "Auto",
    "EmbSata1PCIeOptionROM": "Enabled",
    "EmbSata2Aspm": "Disabled",
    "EmbSata2Enable": "Auto",
    "EmbSata2PCIeOptionROM": "Enabled",
    "EmbVideoConnection": "Auto",
    "EmbeddedDiagnostics": "Enabled",
    "EmbeddedSata": "Ahci",
    "EmbeddedUefiShell": "Enabled",
    "EmsConsole": "Disabled",
    "EnabledCoresPerProc": 0,
    "EnergyEfficientTurbo": "Disabled",
    "EnergyPerfBias": "MaxPerf",
    "EraseUserDefaults": "No",
    "ExtendedAmbientTemp": "Disabled",
    "ExtendedMemTest": "Disabled",
    "F11BootMenu": "Enabled",
    "FCScanPolicy": "CardConfig",
    "FanFailPolicy": "Shutdown",
    "FanInstallReq": "EnableMessaging",
    "FlexLom1Aspm": "Disabled",
    "HttpSupport": "Auto",
    "HwPrefetcher": "Enabled",
    "IODCConfiguration": "Auto",
    "IntelDmiLinkFreq": "Auto",
    "IntelNicDmaChannels": "Enabled",
    "IntelPerfMonitoring": "Disabled",
    "IntelProcVtd": "Enabled",
    "IntelTxt": "Disabled",
    "IntelligentProvisioning": "Enabled",
    "Ipv4Address": "0.0.0.0",
    "Ipv4Gateway": "0.0.0.0",
    "Ipv4PrimaryDNS": "0.0.0.0",
    "Ipv4SecondaryDNS": "0.0.0.0",
    "Ipv4SubnetMask": "0.0.0.0",
    "Ipv6Address": "::",
    "Ipv6ConfigPolicy": "Automatic",
    "Ipv6Duid": "Auto",
    "Ipv6Gateway": "::",
    "Ipv6PrimaryDNS": "::",
    "Ipv6SecondaryDNS": "::",
    "LLCDeadLineAllocation": "Enabled",
    "LlcPrefetch": "Enabled",
    "LocalRemoteThreshold": "Auto",
    "MaxMemBusFreqMHz": "Auto",
    "MaxPcieSpeed": "PerPortCtrl",
    "MemClearWarmReset": "Disabled",
    "MemFastTraining": "Enabled",
    "MemMirrorMode": "Full",
    "MemPatrolScrubbing": "Enabled",
    "MemRefreshRate": "Refreshx1",
    "MemoryControllerInterleaving": "Auto",
    "MemoryRemap": "NoAction",
    "MinProcIdlePkgState": "NoState",
    "MinProcIdlePower": "NoCStates",
    "NetworkBootRetry": "Enabled",
    "NetworkBootRetryCount": 20,
    "NicBoot1": "NetworkBoot",
    "NicBoot2": "NetworkBoot",
    "NicBoot3": "Disabled",
    "NicBoot4": "Disabled",
    "NicBoot5": "Disabled",
    "NodeInterleaving": "Disabled",
    "NumaGroupSizeOpt": "Clustered",
    "NvmeFormat1": "Disabled",
    "NvmeFormat2": "Disabled",
    "NvmeOptionRom": "Enabled",
    "OpportunisticSelfRefresh": "Disabled",
    "PciPeerToPeerSerialization": "Disabled",
    "PciResourcePadding": "Normal",
    "PciSlot1Aspm": "Disabled",
    "PciSlot1Bifurcation": "Auto",
    "PciSlot1Enable": "Auto",
    "PciSlot1LinkSpeed": "Auto",
    "PciSlot1OptionROM": "Enabled",
    "PciSlot3Aspm": "Disabled",
    "PciSlot3Bifurcation": "Auto",
    "PciSlot3Enable": "Auto",
    "PciSlot3LinkSpeed": "Auto",
    "PciSlot3OptionROM": "Enabled",
    "PersistentMemBackupPowerPolicy": "WaitForBackupPower",
    "PostBootProgress": "Disabled",
    "PostDiscoveryMode": "Auto",
    "PostF1Prompt": "Delayed20Sec",
    "PostVideoSupport": "DisplayAll",
    "PowerButton": "Enabled",
    "PowerOnDelay": "NoDelay",
    "PowerRegulator": "StaticHighPerf",
    "PreBootNetwork": "Auto",
    "PrebootNetworkEnvPolicy": "Auto",
    "PrebootNetworkProxy": "",
    "ProcAes": "Enabled",
    "ProcHyperthreading": "Enabled",
    "ProcTurbo": "Enabled",
    "ProcVirtualization": "Enabled",
    "ProcX2Apic": "Enabled",
    "ProcessorConfigTDPLevel": "Level2",
    "ProcessorJitterControl": "Disabled",
    "ProcessorJitterControlFrequency": 0,
    "ProcessorJitterControlOptimization": "ZeroLatency",
    "ProductId": "P27064-B21",
    "RedundantPowerSupply": "BalancedMode",
    "RemovableFlashBootSeq": "ExternalKeysFirst",
    "RestoreDefaults": "No",
    "RestoreManufacturingDefaults": "No",
    "RomSelection": "CurrentRom",
    "SataSecureErase": "Disabled",
    "SaveUserDefaults": "No",
    "SecStartBackupImage": "Disabled",
    "SecureBootStatus": "Disabled",
    "SerialConsoleBaudRate": "BaudRate115200",
    "SerialConsoleEmulation": "Vt100Plus",
    "SerialConsolePort": "Auto",
    "SerialNumber": "MXQ1300HFN",
    "ServerAssetTag": "",
    "ServerConfigLockStatus": "Disabled",
    "ServerName": "welktxef-931881-rh-le0e910-0",
    "ServerOtherInfo": "",
    "ServerPrimaryOs": "",
    "ServiceEmail": "",
    "ServiceName": "",
    "ServiceOtherInfo": "",
    "ServicePhone": "",
    "SetupBrowserSelection": "Auto",
    "Slot1MctpBroadcastSupport": "Enabled",
    "Slot3MctpBroadcastSupport": "Enabled",
    "Slot3NicBoot1": "NetworkBoot",
    "Slot3NicBoot2": "Disabled",
    "Sriov": "Enabled",
    "StaleAtoS": "Disabled",
    "SubNumaClustering": "Disabled",
    "ThermalConfig": "OptimalCooling",
    "ThermalShutdown": "Enabled",
    "TimeFormat": "Utc",
    "TimeZone": "Unspecified",
    "Tpm20SoftwareInterfaceOperation": "NoAction",
    "Tpm20SoftwareInterfaceStatus": "Fifo",
    "Tpm2Operation": "NoAction",
    "TpmActivePcrs": "Sha1Sha256",
    "TpmChipId": "StMicroGen10",
    "TpmFips": "FipsMode",
    "TpmFipsModeSwitch": "NoAction",
    "TpmModeSwitchOperation": "NoAction",
    "TpmState": "PresentEnabled",
    "TpmType": "Tpm20",
    "TpmUefiOpromMeasuring": "Enabled",
    "TpmVisibility": "Visible",
    "UefiOptimizedBoot": "Enabled",
    "UefiSerialDebugLevel": "Disabled",
    "UefiShellBootOrder": "Disabled",
    "UefiShellScriptVerification": "Disabled",
    "UefiShellStartup": "Disabled",
    "UefiShellStartupLocation": "Auto",
    "UefiShellStartupUrl": "",
    "UefiShellStartupUrlFromDhcp": "Disabled",
    "UncoreFreqScaling": "Maximum",
    "UrlBootFile": "",
    "UrlBootFile2": "",
    "UrlBootFile3": "",
    "UrlBootFile4": "",
    "UsbBoot": "Enabled",
    "UsbControl": "UsbEnabled",
    "UserDefaultsState": "Disabled",
    "UtilityLang": "English",
    "VirtualInstallDisk": "Disabled",
    "VirtualSerialPort": "Com1Irq4",
    "VlanControl": "Disabled",
    "VlanId": 0,
    "VlanPriority": 0,
    "WakeOnLan": "Enabled",
    "WorkloadProfile": "Custom",
    "XptPrefetcher": "Auto",
    "iSCSIPolicy": "SoftwareInitiator"
  },
  "Id": "settings",
  "Name": "BIOS Pending Settings"
}
[XXXXXX@welktxefnce-h-pe1util-vm01 logs]$
```


## BIOS settings for e910t




## E910t 3.06 Upgrade 

```log
(hpe_fw) [XXXXXX@welktxefnce-h-pe1util-vm01 EL8000t-Firmware-Update-Scripts-Sep06-2024]$ python ./ilo_fw_updater.py --hostnames ./hostnames-e910t.yaml --username XXXXXX --password XXXXXX --packageDir ./firmware_recipes/e910t_upgrade --logsDir ./logs --process ./firmware_recipes/e910t_upgrade/process_e910t_upgrade-upload-apply-ALL-ILO306.yaml --model e910t --biosupdate upgrade --dryrun
Start firmware update process at 2024/09/06 19:26:58
Overall firmware update progress: 100%|█████████████████████████████████████████████████████████████████████████████████████████████| 1/1 [00:10<00:00, 10.57s/iterating iLO5]
Elapsed time: 0:00:10.645027
Not running BIOS update script because this is a dryrun.
(hpe_fw) [XXXXXX@welktxefnce-h-pe1util-vm01 EL8000t-Firmware-Update-Scripts-Sep06-2024]$ python ./ilo_fw_updater.py --hostnames ./hostnames-e910t.yaml --username XXXXXX --password XXXXXX --packageDir ./firmware_recipes/e910t_upgrade --logsDir ./logs --process ./firmware_recipes/e910t_upgrade/process_e910t_upgrade-upload-apply-ALL-ILO306.yaml --model e910t --biosupdate upgrade
Start firmware update process at 2024/09/06 19:27:20

(hpe_fw) [XXXXXX@welktxefnce-h-pe1util-vm01 EL8000t-Firmware-Update-Scripts-Sep06-2024]$ python ./ilo_fw_updater.py --hostnames ./hostnames-e910t.yaml --username XXXXXX --password XXXXXX --packageDir ./firmware_recipes/e910t_upgrade --logsDir ./logs --process ./firmware_recipes/e910t_upgrade/process_e910t_upgrade-upload-apply-ALL-ILO306.yaml --model e910t --biosupdate upgrade
Start firmware update process at 2024/09/06 19:27:20
Overall firmware update progress: 100%|███████████████████████████████████████████████████████████████████████████████████████████| 1/1 [27:01<00:00, 1621.27s/iterating iLO5]
Elapsed time: 0:27:01.322572
Running the BIOS update script.
Overall BIOS update progress:   0%|                                                                                                         | 0/1 [00:00<?, ?iterating iLO5/s]Overall BIOS update progress: 100%|█████████████████████████████████████████████████████████████████████████████████████████████████| 1/1 [00:20<00:00, 20.18s/iterating iLO5]
Exiting the program...
(hpe_fw) [XXXXXX@welktxefnce-h-pe1util-vm01 EL8000t-Firmware-Update-Scripts-Sep06-2024]$

```

## BIOS settings for e910t

```log
[XXXXXX@welktxefnce-h-pe1util-vm01 logs]$ IP=2607:f160:10:922a:ce:406:0:1000
[XXXXXX@welktxefnce-h-pe1util-vm01 logs]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[$IP]/redfish/v1/Systems/1/bios/settings |jq .
{
  "@odata.context": "/redfish/v1/$metadata#Bios.Bios",
  "@odata.etag": "W/\"8C2A76B638908C8C8CB2CF123F520DD5\"",
  "@odata.id": "/redfish/v1/systems/1/bios/settings/",
  "@odata.type": "#Bios.v1_0_0.Bios",
  "AttributeRegistry": "BiosAttributeRegistryH08.v1_2_12",
  "Attributes": {
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
    "AsrStatus": "Enabled",
    "AsrTimeoutMinutes": "Timeout10",
    "AssetTagProtection": "Unlocked",
    "AutoPowerOn": "RestoreLastState",
    "BootMode": "Uefi",
    "BootOrderPolicy": "RetryIndefinitely",
    "ChannelInterleaving": "Enabled",
    "CollabPowerControl": "Disabled",
    "ConsistentDevNaming": "LomsAndSlots",
    "CustomPostMessage": "",
    "DaylightSavingsTime": "Disabled",
    "DcuIpPrefetcher": "Enabled",
    "DcuStreamPrefetcher": "Enabled",
    "Dhcpv4": "Enabled",
    "EmbNic2Enable": "Auto",
    "EmbNic2LinkSpeed": "Auto",
    "EmbNic2PCIeOptionROM": "Enabled",
    "EmbNicEnable": "Auto",
    "EmbNicLinkSpeed": "Auto",
    "EmbNicPCIeOptionROM": "Enabled",
    "EmbSas1Aspm": "Disabled",
    "EmbSata1Aspm": "Disabled",
    "EmbSata1Enable": "Auto",
    "EmbSata1PCIeOptionROM": "Enabled",
    "EmbSata2Aspm": "Disabled",
    "EmbSata2Enable": "Auto",
    "EmbSata2PCIeOptionROM": "Enabled",
    "EmbVideoConnection": "Auto",
    "EmbeddedDiagnostics": "Enabled",
    "EmbeddedSata": "Ahci",
    "EmbeddedUefiShell": "Enabled",
    "EmsConsole": "Disabled",
    "EnabledCoresPerProc": 0,
    "EnergyEfficientTurbo": "Disabled",
    "EnergyPerfBias": "MaxPerf",
    "EnergyPerformancePreference": "Disabled",
    "EraseUserDefaults": "No",
    "ExtendedAmbientTemp": "Disabled",
    "ExtendedMemTest": "Disabled",
    "F11BootMenu": "Enabled",
    "FCScanPolicy": "CardConfig",
    "FanFailPolicy": "Shutdown",
    "FanInstallReq": "EnableMessaging",
    "FlexLom1Aspm": "Disabled",
    "HttpSupport": "Auto",
    "HwPrefetcher": "Enabled",
    "IODCConfiguration": "Auto",
    "IntelDmiLinkFreq": "Auto",
    "IntelNicDmaChannels": "Enabled",
    "IntelPerfMonitoring": "Disabled",
    "IntelProcVtd": "Enabled",
    "IntelTxt": "Disabled",
    "IntelligentProvisioning": "Enabled",
    "IpmiWatchdogTimerAction": "PowerCycle",
    "IpmiWatchdogTimerStatus": "IpmiWatchdogTimerOff",
    "IpmiWatchdogTimerTimeout": "Timeout30Min",
    "Ipv4Address": "0.0.0.0",
    "Ipv4Gateway": "0.0.0.0",
    "Ipv4PrimaryDNS": "0.0.0.0",
    "Ipv4SecondaryDNS": "0.0.0.0",
    "Ipv4SubnetMask": "0.0.0.0",
    "Ipv6Address": "::",
    "Ipv6ConfigPolicy": "Automatic",
    "Ipv6Duid": "Auto",
    "Ipv6Gateway": "::",
    "Ipv6PrimaryDNS": "::",
    "Ipv6SecondaryDNS": "::",
    "LLCDeadLineAllocation": "Enabled",
    "LlcPrefetch": "Enabled",
    "LocalRemoteThreshold": "Auto",
    "MaxMemBusFreqMHz": "Auto",
    "MaxPcieSpeed": "PerPortCtrl",
    "MemClearWarmReset": "Disabled",
    "MemFastTraining": "Enabled",
    "MemMirrorMode": "Full",
    "MemPatrolScrubbing": "Disabled",
    "MemRefreshRate": "Refreshx1",
    "MemoryControllerInterleaving": "Auto",
    "MemoryRemap": "NoAction",
    "MinProcIdlePkgState": "NoState",
    "MinProcIdlePower": "C6",
    "NetworkBootRetry": "Enabled",
    "NetworkBootRetryCount": 20,
    "NicBoot1": "NetworkBoot",
    "NicBoot2": "NetworkBoot",
    "NicBoot3": "Disabled",
    "NicBoot4": "Disabled",
    "NicBoot5": "Disabled",
    "NumaGroupSizeOpt": "Clustered",
    "NvmeFormat11": "Disabled",
    "NvmeFormat12": "Disabled",
    "NvmeOptionRom": "Enabled",
    "OpportunisticSelfRefresh": "Disabled",
    "PciPeerToPeerSerialization": "Disabled",
    "PciResourcePadding": "Normal",
    "PciSlot1Aspm": "Disabled",
    "PciSlot1Bifurcation": "Auto",
    "PciSlot1Enable": "Auto",
    "PciSlot1LinkSpeed": "Auto",
    "PciSlot1OptionROM": "Enabled",
    "PciSlot3Aspm": "Disabled",
    "PciSlot3Bifurcation": "Auto",
    "PciSlot3Enable": "Auto",
    "PciSlot3LinkSpeed": "Auto",
    "PciSlot3OptionROM": "Enabled",
    "PersistentMemBackupPowerPolicy": "WaitForBackupPower",
    "PostBootProgress": "Disabled",
    "PostDiscoveryMode": "Auto",
    "PostF1Prompt": "Delayed20Sec",
    "PostVideoSupport": "DisplayAll",
    "PostedInterruptThrottle": "Enabled",
    "PowerButton": "Enabled",
    "PowerOnDelay": "NoDelay",
    "PowerRegulator": "OsControl",
    "PreBootNetwork": "Auto",
    "PrebootNetworkEnvPolicy": "Auto",
    "PrebootNetworkProxy": "",
    "ProcAes": "Enabled",
    "ProcHyperthreading": "Enabled",
    "ProcTurbo": "Enabled",
    "ProcVirtualization": "Enabled",
    "ProcX2Apic": "Enabled",
    "ProcessorConfigTDPLevel": "Level2",
    "ProcessorJitterControl": "Disabled",
    "ProcessorJitterControlFrequency": 0,
    "ProcessorJitterControlOptimization": "ZeroLatency",
    "ProductId": "P27064-B21",
    "RefreshWatermarks": "Auto",
    "RemovableFlashBootSeq": "ExternalKeysFirst",
    "RestoreDefaults": "No",
    "RestoreManufacturingDefaults": "No",
    "RomSelection": "CurrentRom",
    "SataSecureErase": "Disabled",
    "SaveUserDefaults": "No",
    "SecStartBackupImage": "Disabled",
    "SecureBootStatus": "Disabled",
    "SerialConsoleBaudRate": "BaudRate115200",
    "SerialConsoleEmulation": "Vt100Plus",
    "SerialConsolePort": "Auto",
    "SerialNumber": "MXQ1300HFN",
    "ServerAssetTag": "",
    "ServerConfigLockStatus": "Disabled",
    "ServerName": "welktxef-931881-rh-le0e910-0",
    "ServerOtherInfo": "",
    "ServerPrimaryOs": "",
    "ServiceEmail": "",
    "ServiceName": "",
    "ServiceOtherInfo": "",
    "ServicePhone": "",
    "SetupBrowserSelection": "Auto",
    "Slot1MctpBroadcastSupport": "Enabled",
    "Slot3MctpBroadcastSupport": "Enabled",
    "Slot3NicBoot1": "NetworkBoot",
    "Slot3NicBoot2": "Disabled",
    "Sriov": "Enabled",
    "StaleAtoS": "Disabled",
    "SubNumaClustering": "Disabled",
    "ThermalConfig": "OptimalCooling",
    "ThermalShutdown": "Enabled",
    "TimeFormat": "Utc",
    "TimeZone": "Unspecified",
    "Tpm20SoftwareInterfaceOperation": "NoAction",
    "Tpm20SoftwareInterfaceStatus": "Fifo",
    "Tpm2Operation": "NoAction",
    "TpmActivePcrs": "Sha1Sha256",
    "TpmChipId": "StMicroGen10",
    "TpmFips": "FipsMode",
    "TpmFipsModeSwitch": "NoAction",
    "TpmModeSwitchOperation": "NoAction",
    "TpmState": "PresentEnabled",
    "TpmType": "Tpm20",
    "TpmUefiOpromMeasuring": "Enabled",
    "TpmVisibility": "Visible",
    "UefiOptimizedBoot": "Enabled",
    "UefiSerialDebugLevel": "Disabled",
    "UefiShellBootOrder": "Disabled",
    "UefiShellScriptVerification": "Disabled",
    "UefiShellStartup": "Disabled",
    "UefiShellStartupLocation": "Auto",
    "UefiShellStartupUrl": "",
    "UefiShellStartupUrlFromDhcp": "Disabled",
    "UefiVariableAccessFwControl": "Disabled",
    "UncoreFreqScaling": "Maximum",
    "UrlBootFile": "",
    "UrlBootFile2": "",
    "UrlBootFile3": "",
    "UrlBootFile4": "",
    "UsbBoot": "Enabled",
    "UsbControl": "UsbEnabled",
    "UserDefaultsState": "Disabled",
    "UtilityLang": "English",
    "VirtualInstallDisk": "Disabled",
    "VirtualSerialPort": "Com1Irq4",
    "VlanControl": "Disabled",
    "VlanId": 0,
    "VlanPriority": 0,
    "WakeOnLan": "Enabled",
    "WorkloadProfile": "Custom",
    "XptPrefetcher": "Auto",
    "iSCSIPolicy": "SoftwareInitiator"
  },
  "Id": "settings",
  "Name": "BIOS Pending Settings"
}
[XXXXXX@welktxefnce-h-pe1util-vm01 logs]$
```



## BIOS settings need to be validated with expectations
```txt
    "WorkloadProfile": "Custom",

"MemPatrolScrubbing": "Disabled"
    "MemPatrolScrubbing": "Disabled",

"MinProcIdlePower": "C6"
   "MinProcIdlePower": "C6",

"PowerRegulator":  "OSControl"
    "PowerRegulator": "OsControl",
```

## Settings are in alignment with expectations



## Setting up Iteration installation testing
## Rollback to ILO 2.66
## Sleep 5 mins
## Upgrade to ILO 3.06
## Sleep 5 mins
## Loop till 20 iterations

### e910t.bash
```sh
#!/bin/bash



echo "Rolling back, sleeping 5 mins then Upgrading, for 20 iterations"

source ~/python_venvs/hpe_fw/bin/activate

count=0
while [ $count -lt 20 ] ; do

python ./ilo_fw_updater.py --hostnames ./hostnames-e910t.yaml --username XXXXXX --password XXXXXX --packageDir ./firmware_recipes/e910t_rollback --logsDir ./logs --process ./firmware_recipes/e910t_rollback/process_e910t_rollback-ALL-ILO266.yaml --model e910t --biosupdate rollback

echo "going to sleep for 5 mins now.... "

sleep 300

echo "Upgrading the ILO now "
python ./ilo_fw_updater.py --hostnames ./hostnames-e910t.yaml --username XXXXXX --password XXXXXX --packageDir ./firmware_recipes/e910t_upgrade --logsDir ./logs --process ./firmware_recipes/e910t_upgrade/process_e910t_upgrade-upload-apply-ALL-ILO306.yaml --model e910t --biosupdate upgrade



echo "going to sleep for 5 mins now.... "

sleep 300

count=$((count+1))
done
```

### e920t.bash
```sh
#!/bin/bash

echo "Rolling back, sleeping 5 mins then Upgrading, for 20 iterations"

source ~/python_venvs/hpe_fw/bin/activate

count=0
while [ $count -lt 20 ] ; do

python ./ilo_fw_updater.py --hostnames ./hostnames-e920t.yaml --username XXXXXX --password XXXXXX --packageDir ./firmware_recipes/e920t_rollback --logsDir ./logs --process ./firmware_recipes/e920t_rollback/process_e920t_rollback-ALL-ILO266.yaml --model e920t --biosupdate rollback

echo "going to sleep for 5 mins now.... "

sleep 300

echo "Upgrading the ILO now "

python ./ilo_fw_updater.py --hostnames ./hostnames-e920t.yaml --username XXXXXX --password XXXXXX --packageDir ./firmware_recipes/e920t_upgrade --logsDir ./logs --process ./firmware_recipes/e920t_upgrade/process_e920t_upgrade-upload-apply-ALL-ILO306.yaml --model e920t --biosupdate upgrade


echo "going to sleep for 5 mins now.... "

sleep 300

count=$((count+1))
done
```

## Results
## e910t 20 passes 
## e920t 20 passes