# HPE ILO6 1.68 BIOS H11 v2.50
# HPE Sapphire Rapids E930t server
# 1/21/26 James Patchett - MTCE Lab VCPfe
# FlexRAN BIOS settings correction after wrong firmware update command

## MTCE Lab HPe E930t system
ILO:  2607:f160:10:80b1:ce:40a:0:e002

### 1st step is to validate BIOS, iLO and settings are what we expect for this issue

#### Set IP variable of ilo of target system
```sh
IP=2607:f160:10:80b1:ce:40a:0:e002
```

#### Pull the BIOS version
```sh
curl -ks -u XXXXXX:XXXXXX https://[$IP]/redfish/v1/Systems/1 | jq .BiosVersion
```
```txt
"H11 v2.50 (04/22/2025)"
```

#### pull the ILO version
```sh
curl -ks -u XXXXXX:XXXXXX https://[$IP]/redfish/v1/Managers/1 | jq .FirmwareVersion
```
```txt
"iLO 6 v1.68"
```

#### Validate the bios settings are incorrect, we are looking specifically at 4 settings to determine
```sh
 curl -gsk -u XXXXXX:XXXXXX -X GET https://[$IP]/redfish/v1/Systems/1/bios/settings |jq . | egrep 'UncoreFrequencyMAX|UncoreFrequencyMIN|PcieGlobalAspm|MinProcIdlePower|AvxIccpPreGrantLevel'
 ```

 ```txt
    "AvxIccpPreGrantLevel": "128Heavy",
    "MinProcIdlePower": "C6",
    "PcieGlobalAspm": "Enabled",
    "UncoreFrequencyMAX": 0,
    "UncoreFrequencyMIN": 0,
 ```

#### If the BIOS/iLO versions match, and bios settings are matching the above settings, then proceed 2nd step to address the wrong settings

### 2nd step is to correct the bios settings by the following procedure

#### Set IP variable of ilo of target system
```sh
IP=2607:f160:10:80b1:ce:40a:0:e002
```

#### Power off the host
```sh
curl -k -u XXXXXX:XXXXXX -H "Content-Type: application/json" -X POST https://[$IP]/redfish/v1/Systems/1/Actions/ComputerSystem.Reset -d '{"ResetType": "ForceOff"}'
```

#### Restore BIOS defaults
```sh
curl -gsk -u XXXXXX:XXXXXX -H "Content-Type: application/json" -X PATCH https://[$IP]/redfish/v1/Systems/1/bios/settings -d '{"Attributes": {"RestoreDefaults": "Yes"}}'
```

#### Power on the host
```sh
curl -k -u XXXXXX:XXXXXX -H "Content-Type: application/json" -X POST https://[$IP]/redfish/v1/Systems/1/Actions/ComputerSystem.Reset -d '{"ResetType": "On"}'
```

#### Wait for host to complete POST 
```txt
Once the system has started to boot the operating system, you are now past POST, and can continue
```

#### Apply vRAN workload profile
```sh
curl -gsk -u XXXXXX:XXXXXX -H "Content-Type: application/json" -X PATCH https://[$IP]/redfish/v1/Systems/1/bios/settings -d '{"Attributes": {"WorkloadProfile": "vRAN"}}'
```

#### Reboot the system to activate the profile
```sh
curl -k -u XXXXXX:XXXXXX -H "Content-Type: application/json" -X POST https://[$IP]/redfish/v1/Systems/1/Actions/ComputerSystem.Reset -d '{"ResetType": "ForceRestart"}'
```

#### Validate the bios settings are correct now after the procedure
```sh
 curl -gsk -u XXXXXX:XXXXXX -X GET https://[$IP]/redfish/v1/Systems/1/bios/settings |jq . | egrep 'UncoreFrequencyMAX|UncoreFrequencyMIN|PcieGlobalAspm|MinProcIdlePower|AvxIccpPreGrantLevel'
 ```

 ```txt
    "AvxIccpPreGrantLevel": "512Heavy",
    "MinProcIdlePower": "C6WithoutC1E",
    "PcieGlobalAspm": "Disabled",
    "UncoreFrequencyMAX": 22,
    "UncoreFrequencyMIN": 8,
 ```

#### as long as your settings match the above data, the fix was succesful.

## Procedure completed