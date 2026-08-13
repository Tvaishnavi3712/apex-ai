# HPE ILO6 3.06 BIOS H08 v2.12
# HPE Sapphire Rapids E910t server
# 9/5/24 James Patchett - MTCE Lab VCPfe
# FlexRAN BIOS settings validation MEAKV-1860

## welktxef-931881-rh-le0e910-005
ILO:  2607:f160:10:922a:ce:406:0:1000
OAM:  2607:f160:10:922a:ce:40a:0:f400

## Subcloud welktxef-d931881-005
## General info before we start

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ system show
system oam-show+------------------------+--------------------------------------+
| Property               | Value                                |
+------------------------+--------------------------------------+
| contact                | None                                 |
| created_at             | 2024-07-03T16:11:02.896972+00:00     |
| description            | None                                 |
| distributed_cloud_role | subcloud                             |
| https_enabled          | True                                 |
| latitude               | None                                 |
| location               | None                                 |
| longitude              | None                                 |
| name                   | welktxef-d931881-005                 |
| region_name            | welktxef-d931881-005                 |
| sdn_enabled            | False                                |
| security_feature       | spectre_meltdown_v1                  |
| service_project_name   | services                             |
| shared_services        | []                                   |
| software_version       | 22.12                                |
| system_mode            | simplex                              |
| system_type            | All-in-one                           |
| timezone               | UTC                                  |
| updated_at             | 2024-08-03T02:49:22.960189+00:00     |
| uuid                   | 3b13920e-8deb-484c-bbca-58b710b2d185 |
| vswitch_type           | none                                 |
+------------------------+--------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ system oam-show
+----------------+---------------------------------------+
| Property       | Value                                 |
+----------------+---------------------------------------+
| created_at     | 2024-07-03T16:13:20.520978+00:00      |
| isystem_uuid   | 3b13920e-8deb-484c-bbca-58b710b2d185  |
| oam_end_ip     | 2607:f160:10:922a:ffff:ffff:ffff:fffe |
| oam_gateway_ip | 2607:f160:10:922a:ce:28::             |
| oam_ip         | 2607:f160:10:922a:ce:40a:0:f400       |
| oam_start_ip   | 2607:f160:10:922a::1                  |
| oam_subnet     | 2607:f160:10:922a::/64                |
| updated_at     | None                                  |
| uuid           | d37418df-d18f-4342-b005-749f7b824387  |
+----------------+---------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ system application-list
+--------------------------+-----------+-------------------------------------------+------------------+---------+-----------+
| application              | version   | manifest name                             | manifest file    | status  | progress  |
+--------------------------+-----------+-------------------------------------------+------------------+---------+-----------+
| cert-manager             | 22.12-8   | cert-manager-fluxcd-manifests             | fluxcd-manifests | applied | completed |
| metrics-server           | 22.12-2   | metrics-server-fluxcd-manifests           | fluxcd-manifests | applied | completed |
| nginx-ingress-controller | 22.12-1   | nginx-ingress-controller-fluxcd-manifests | fluxcd-manifests | applied | completed |
| oidc-auth-apps           | 22.12-6   | oidc-auth-apps-fluxcd-manifests           | fluxcd-manifests | applied | completed |
| platform-integ-apps      | 22.12-72  | platform-integ-apps-fluxcd-manifests      | fluxcd-manifests | applied | completed |
| ptp-notification         | 22.12-140 | ptp-notification-fluxcd-manifests         | fluxcd-manifests | applied | completed |
| wr-analytics             | 23.09-1   | wr-analytics-fluxcd-manifests             | fluxcd-manifests | applied | completed |
+--------------------------+-----------+-------------------------------------------+------------------+---------+-----------+
[XXXXXX@controller-0 ~(keystone_admin)]$ sw-patch query
      Patch ID         RR  Release  Patch State
=====================  ==  =======  ===========
WRCP_22.12_PATCH_0001  Y    22.12    Committed
WRCP_22.12_PATCH_0002  Y    22.12    Committed
WRCP_22.12_PATCH_0003  Y    22.12    Committed
WRCP_22.12_PATCH_0004  Y    22.12    Committed
WRCP_22.12_PATCH_0005  Y    22.12    Committed

[XXXXXX@controller-0 ~(keystone_admin)]$ fm alarm-list

[XXXXXX@controller-0 ~(keystone_admin)]$

```

### Have to validate that BIOS settings are configured with the WorkloadProfile set to "vRAN"

```log
(atlas) szabota@welktxefnce-h-pe1util-vm05:~/playbooks/bmc-workloadprofile/bmc$ echo $IP
2607:f160:10:922a:ce:406:0:1000
(atlas) szabota@welktxefnce-h-pe1util-vm05:~/playbooks/bmc-workloadprofile/bmc$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[$IP]/redfish/v1/Systems/1/bios/settings |jq .Attributes.WorkloadProfile
"Custom"
(atlas) szabota@welktxefnce-h-pe1util-vm05:~/playbooks/bmc-workloadprofile/bmc$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[$IP]/redfish/v1/Systems/1/bios/settings |jq .
{
  "@odata.context": "/redfish/v1/$metadata#Bios.Bios",
  "@odata.etag": "W/\"52C3BDDCC345A2A2A2C8593C53E05859\"",
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
    "MinProcIdlePower": "NoCStates",
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
(atlas) szabota@welktxefnce-h-pe1util-vm05:~/playbooks/bmc-workloadprofile/bmc$
```

### in the ILO5 we can see that the Redfish call shows we are set with WorkloadProfile set to "custom" 
### For e910t this  is correct, per the Planning BIOS referenced configuration for Intel Flex Ran
```log
H08 v2.12

Additional BIOS settings changes in the Custom profile: 
"MemPatrolScrubbing": "Disabled"
"MinProcIdlePower": "C6"
"PowerRegulator":  "OSControl"

```

### now compare to above captured bios settings of the e910t

```log

    "MemPatrolScrubbing": "Disabled",
    "MinProcIdlePower": "NoCStates",
    "PowerRegulator": "StaticHighPerf",
    

```

### Settings do not match, only MemPatrolScrubbing was set. 
### will consult the BMC Playbook to see why settings were not applied, I suspect 3.06 logic is not present in the plabyook