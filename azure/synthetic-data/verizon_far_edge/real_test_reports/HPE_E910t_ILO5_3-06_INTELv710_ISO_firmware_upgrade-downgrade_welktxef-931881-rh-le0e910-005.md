# HPE ILO5 3.06 BIOS H08 v2.12
# HPE e910t server INTEL NIC v710 firmware upgrade and downgrade
# 8/20/24 James Patchett - MTCE Lab VCPfe
 

## welktxef-931881-rh-le0e910-005
ILO:  2607:f160:10:922a:ce:406:0:1000
OAM:  2607:f160:10:922a:ce:40a:0:f400

## ISOs provided by Bj with Planning

```log
[XXXXXX@welktxefnce-h-pe1util-vm01 packages]$ ls -latr bootimage_hpe_fvl_*
-rw-r--r-- 1 XXXXXX XXXXXX 93472768 Aug 21 10:59 bootimage_hpe_fvl_downgrade.iso
-rw-r--r-- 1 XXXXXX XXXXXX 93472768 Aug 21 11:06 bootimage_hpe_fvl_upgrade.iso
[XXXXXX@welktxefnce-h-pe1util-vm01 packages]$
```

## Changed name of ISOs to better define their purpose
```log
[XXXXXX@welktxefnce-h-pe1util-vm01 packages]$ ls -latr bootimage_hpe-e910t_intelv710_*
-rw-r--r-- 1 XXXXXX XXXXXX 93472768 Aug 21 10:59 bootimage_hpe-e910t_intelv710_8-24_fvl_downgrade.iso
-rw-r--r-- 1 XXXXXX XXXXXX 93472768 Aug 21 11:06 bootimage_hpe-e910t_intelv710_9-20_fvl_upgrade.iso
[XXXXXX@welktxefnce-h-pe1util-vm01 packages]$

```

## Commands used to upload isos to webdav server
```sh
# curl -X PUT -u 'XXXXXX:XXXXXX' -T intel-e810-fw-v2.54_v2.iso http://[2607:f160:10:9239:ce:290:0:3000]:8080/intel-e810-fw-v4.22-efi_v1.iso

curl -X PUT -u 'XXXXXX:XXXXXX' -T bootimage_hpe-e910t_intelv710_8-24_fvl_downgrade.iso http://[2607:f160:10:9239:ce:290:0:3000]:8080/bootimage_hpe-e910t_intelv710_8-24_fvl_downgrade.iso

curl -X PUT -u 'XXXXXX:XXXXXX' -T bootimage_hpe-e910t_intelv710_9-20_fvl_upgrade.iso http://[2607:f160:10:9239:ce:290:0:3000]:8080/bootimage_hpe-e910t_intelv710_9-20_fvl_upgrade.iso

```

## Commands to use redfish to mount ISO, and install firmware for downgrade to 8.24 (~17min installation)

```sh
IP=2607:f160:10:922a:ce:406:0:1000

curl -g -u XXXXXX:XXXXXX --insecure  -H "Content-Type: application/json" -X GET https://[$IP]/redfish/v1/Managers/1/VirtualMedia/2/ | jq .

curl -g -u XXXXXX:XXXXXX --insecure  -H "Content-Type: application/json" -X POST https://[$IP]/redfish/v1/Managers/1/VirtualMedia/2/Actions/VirtualMedia.EjectMedia/ | jq .

curl -g -u XXXXXX:XXXXXX --insecure  -H "Content-Type: application/json" -X POST -d '{"Image": "http://[2607:f160:10:9239:ce:290:0:3000]:8080/bootimage_hpe-e910t_intelv710_8-24_fvl_downgrade.iso"}'  https://[$IP]/redfish/v1/Managers/1/VirtualMedia/2/Actions/VirtualMedia.InsertMedia/ | jq .

curl -g -u XXXXXX:XXXXXX --insecure  -H "Content-Type: application/json" -X PATCH -d '{ "Oem": {"Hpe": {"BootOnNextServerReset": true}} }'  https://[$IP]/redfish/v1/Managers/1/VirtualMedia/2/ | jq .

curl -g -u XXXXXX:XXXXXX --insecure  -H "Content-Type: application/json" -X PATCH https://[$IP]/redfish/v1/Systems/1/BIOS/Boot/Settings/ -d '{ "Boot": { "BootSourceOverrideEnabled": "Once", "BootSourceOverrideTarget": "Cd", "BootSourceOverrideMode": "UEFI"}}' | jq .

curl -g -u XXXXXX:XXXXXX --insecure -H "Content-Type: application/json" -X POST -d '{"ResetType" : "ForceRestart"}' https://[$IP]/redfish/v1/Systems/1/Actions/ComputerSystem.Reset/


```

## Commands to use redfish to mount ISO, and install firmware for upgrade to 9.20 (~17min installation)

```sh
IP=2607:f160:10:922a:ce:406:0:1000

curl -g -u XXXXXX:XXXXXX --insecure  -H "Content-Type: application/json" -X GET https://[$IP]/redfish/v1/Managers/1/VirtualMedia/2/ | jq .

curl -g -u XXXXXX:XXXXXX --insecure  -H "Content-Type: application/json" -X POST https://[$IP]/redfish/v1/Managers/1/VirtualMedia/2/Actions/VirtualMedia.EjectMedia/ | jq .

curl -g -u XXXXXX:XXXXXX --insecure  -H "Content-Type: application/json" -X POST -d '{"Image": "http://[2607:f160:10:9239:ce:290:0:3000]:8080/bootimage_hpe-e910t_intelv710_9-20_fvl_upgrade.iso"}'  https://[$IP]/redfish/v1/Managers/1/VirtualMedia/2/Actions/VirtualMedia.InsertMedia/ | jq .

curl -g -u XXXXXX:XXXXXX --insecure  -H "Content-Type: application/json" -X PATCH -d '{ "Oem": {"Hpe": {"BootOnNextServerReset": true}} }'  https://[$IP]/redfish/v1/Managers/1/VirtualMedia/2/ | jq .

curl -g -u XXXXXX:XXXXXX --insecure  -H "Content-Type: application/json" -X PATCH https://[$IP]/redfish/v1/Systems/1/BIOS/Boot/Settings/ -d '{ "Boot": { "BootSourceOverrideEnabled": "Once", "BootSourceOverrideTarget": "Cd", "BootSourceOverrideMode": "UEFI"}}' | jq .

curl -g -u XXXXXX:XXXXXX --insecure -H "Content-Type: application/json" -X POST -d '{"ResetType" : "ForceRestart"}' https://[$IP]/redfish/v1/Systems/1/Actions/ComputerSystem.Reset/


```


## uploading the new ISOs to webdav server for test in lab
```log
[XXXXXX@welktxefnce-h-pe1util-vm01 packages]$ curl -X PUT -u 'XXXXXX:XXXXXX' -T bootimage_hpe-e910t_intelv710_8-24_fvl_downgrade.iso http://[2607:f160:10:9239:ce:290:0:3000]:8080/bootimage_hpe-e910t_intelv710_8-24_fvl_downgrade.iso
<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
<html><head>
<title>201 Created</title>
</head><body>
<h1>Created</h1>
<p>Resource /bootimage_hpe-e910t_intelv710_8-24_fvl_downgrade.iso has been created.</p>
</body></html>
[XXXXXX@welktxefnce-h-pe1util-vm01 packages]$ curl -X PUT -u 'XXXXXX:XXXXXX' -T bootimage_hpe-e910t_intelv710_9-20_fvl_upgrade.iso http://[2607:f160:10:9239:ce:290:0:3000]:8080/bootimage_hpe-e910t_intelv710_9-20_fvl_upgrade.iso
<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
<html><head>
<title>201 Created</title>
</head><body>
<h1>Created</h1>
<p>Resource /bootimage_hpe-e910t_intelv710_9-20_fvl_upgrade.iso has been created.</p>
</body></html>
[XXXXXX@welktxefnce-h-pe1util-vm01 packages]$
```

## Attempting downgrade on 910 with 3.06 recipe installed

```log

[XXXXXX@welktxefnce-h-pe1util-vm01 packages]$ IP=2607:f160:10:922a:ce:406:0:1000
[XXXXXX@welktxefnce-h-pe1util-vm01 packages]$ curl -g -u XXXXXX:XXXXXX --insecure  -H "Content-Type: application/json" -X GET https://[$IP]/redfish/v1/Managers/1/VirtualMedia/2/ | jq .
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100  1106    0  1106    0     0   2880      0 --:--:-- --:--:-- --:--:--  2872
{
  "@odata.context": "/redfish/v1/$metadata#VirtualMedia.VirtualMedia",
  "@odata.etag": "W/\"14700DD6\"",
  "@odata.id": "/redfish/v1/Managers/1/VirtualMedia/2/",
  "@odata.type": "#VirtualMedia.v1_3_0.VirtualMedia",
  "Id": "2",
  "Actions": {
    "#VirtualMedia.EjectMedia": {
      "target": "/redfish/v1/Managers/1/VirtualMedia/2/Actions/VirtualMedia.EjectMedia/"
    },
    "#VirtualMedia.InsertMedia": {
      "target": "/redfish/v1/Managers/1/VirtualMedia/2/Actions/VirtualMedia.InsertMedia/"
    }
  },
  "ConnectedVia": "NotConnected",
  "Description": "Virtual Removable Media",
  "Image": "",
  "Inserted": false,
  "MediaTypes": [
    "CD",
    "DVD"
  ],
  "Name": "VirtualMedia",
  "Oem": {
    "Hpe": {
      "@odata.context": "/redfish/v1/$metadata#HpeiLOVirtualMedia.HpeiLOVirtualMedia",
      "@odata.type": "#HpeiLOVirtualMedia.v2_2_0.HpeiLOVirtualMedia",
      "Actions": {
        "#HpeiLOVirtualMedia.EjectVirtualMedia": {
          "target": "/redfish/v1/Managers/1/VirtualMedia/2/Actions/Oem/Hpe/HpeiLOVirtualMedia.EjectVirtualMedia/"
        },
        "#HpeiLOVirtualMedia.InsertVirtualMedia": {
          "target": "/redfish/v1/Managers/1/VirtualMedia/2/Actions/Oem/Hpe/HpeiLOVirtualMedia.InsertVirtualMedia/"
        }
      },
      "BootOnNextServerReset": false
    }
  },
  "WriteProtected": true
}
[XXXXXX@welktxefnce-h-pe1util-vm01 packages]$ curl -g -u XXXXXX:XXXXXX --insecure  -H "Content-Type: application/json" -X POST https://[$IP]/redfish/v1/Managers/1/VirtualMedia/2/Actions/VirtualMedia.EjectMedia/ | jq .
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   187    0   187    0     0    396      0 --:--:-- --:--:-- --:--:--   395
{
  "error": {
    "code": "iLO.0.10.ExtendedInfo",
    "message": "See @Message.ExtendedInfo for more information.",
    "@Message.ExtendedInfo": [
      {
        "MessageId": "iLO.2.23.NoVirtualMediaConnectionAvailable"
      }
    ]
  }
}
[XXXXXX@welktxefnce-h-pe1util-vm01 packages]$ curl -g -u XXXXXX:XXXXXX --insecure  -H "Content-Type: application/json" -X POST -d '{"Image": "http://[2607:f160:10:9239:ce:290:0:3000]:8080/bootimage_hpe-e910t_intelv710_8-24_fvl_downgrade.iso"}'  https://[$IP]/redfish/v1/Managers/1/VirtualMedia/2/Actions/VirtualMedia.InsertMedia/ | jq .
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   273    0   162  100   111    268    184 --:--:-- --:--:-- --:--:--   452
{
  "error": {
    "code": "iLO.0.10.ExtendedInfo",
    "message": "See @Message.ExtendedInfo for more information.",
    "@Message.ExtendedInfo": [
      {
        "MessageId": "Base.1.18.Success"
      }
    ]
  }
}
[XXXXXX@welktxefnce-h-pe1util-vm01 packages]$ curl -g -u XXXXXX:XXXXXX --insecure  -H "Content-Type: application/json" -X PATCH -d '{ "Oem": {"Hpe": {"BootOnNextServerReset": true}} }'  https://[$IP]/redfish/v1/Managers/1/VirtualMedia/2/ | jq .
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   213    0   162  100    51    217     68 --:--:-- --:--:-- --:--:--   285
{
  "error": {
    "code": "iLO.0.10.ExtendedInfo",
    "message": "See @Message.ExtendedInfo for more information.",
    "@Message.ExtendedInfo": [
      {
        "MessageId": "Base.1.18.Success"
      }
    ]
  }
}
[XXXXXX@welktxefnce-h-pe1util-vm01 packages]$ curl -g -u XXXXXX:XXXXXX --insecure  -H "Content-Type: application/json" -X PATCH https://[$IP]/redfish/v1/Systems/1/BIOS/Boot/Settings/ -d '{ "Boot": { "BootSourceOverrideEnabled": "Once", "BootSourceOverrideTarget": "Cd", "BootSourceOverrideMode": "UEFI"}}' | jq .
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   290    0   173  100   117    312    211 --:--:-- --:--:-- --:--:--   522
{
  "error": {
    "code": "iLO.0.10.ExtendedInfo",
    "message": "See @Message.ExtendedInfo for more information.",
    "@Message.ExtendedInfo": [
      {
        "MessageId": "iLO.2.23.SystemResetRequired"
      }
    ]
  }
}
[XXXXXX@welktxefnce-h-pe1util-vm01 packages]$ curl -g -u XXXXXX:XXXXXX --insecure -H "Content-Type: application/json" -X POST -d '{"ResetType" : "ForceRestart"}' https://[$IP]/redfish/v1/Systems/1/Actions/ComputerSystem.Reset/
{"error":{"code":"iLO.0.10.ExtendedInfo","message":"See @Message.ExtendedInfo for more information.","@Message.ExtendedInfo":[{"MessageId":"Base.1.18.Success"}]}}[XXXXXX@welktxefnce-h-pe1util-vm01 packages]$
[XXXXXX@welktxefnce-h-pe1util-vm01 packages]$ curl -s -k -g -u XXXXXX:XXXXXX -H 'Content-Type: application/json' -X GET https://[$IP]/redfish/v1/systems/1/ | jq ".PowerState"
"On"
[XXXXXX@welktxefnce-h-pe1util-vm01 packages]$

```

### Firmware validation of nic card

```log

HPE Ethernet 10/25Gb 2-port 661SFP28 Adapter 	1.3241.0 	PCI-E Slot 3

```

### Upgrade firmware on nic

```log
[XXXXXX@welktxefnce-h-pe1util-vm01 packages]$ IP=2607:f160:10:922a:ce:406:0:1000
[XXXXXX@welktxefnce-h-pe1util-vm01 packages]$
[XXXXXX@welktxefnce-h-pe1util-vm01 packages]$ curl -g -u XXXXXX:XXXXXX --insecure  -H "Content-Type: application/json" -X GET https://[$IP]/redfish/v1/Managers/1/VirtualMedia/2/ | jq .
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100  1106    0  1106    0     0   1165      0 --:--:-- --:--:-- --:--:--  1164
{
  "@odata.context": "/redfish/v1/$metadata#VirtualMedia.VirtualMedia",
  "@odata.etag": "W/\"14700DD6\"",
  "@odata.id": "/redfish/v1/Managers/1/VirtualMedia/2/",
  "@odata.type": "#VirtualMedia.v1_3_0.VirtualMedia",
  "Id": "2",
  "Actions": {
    "#VirtualMedia.EjectMedia": {
      "target": "/redfish/v1/Managers/1/VirtualMedia/2/Actions/VirtualMedia.EjectMedia/"
    },
    "#VirtualMedia.InsertMedia": {
      "target": "/redfish/v1/Managers/1/VirtualMedia/2/Actions/VirtualMedia.InsertMedia/"
    }
  },
  "ConnectedVia": "NotConnected",
  "Description": "Virtual Removable Media",
  "Image": "",
  "Inserted": false,
  "MediaTypes": [
    "CD",
    "DVD"
  ],
  "Name": "VirtualMedia",
  "Oem": {
    "Hpe": {
      "@odata.context": "/redfish/v1/$metadata#HpeiLOVirtualMedia.HpeiLOVirtualMedia",
      "@odata.type": "#HpeiLOVirtualMedia.v2_2_0.HpeiLOVirtualMedia",
      "Actions": {
        "#HpeiLOVirtualMedia.EjectVirtualMedia": {
          "target": "/redfish/v1/Managers/1/VirtualMedia/2/Actions/Oem/Hpe/HpeiLOVirtualMedia.EjectVirtualMedia/"
        },
        "#HpeiLOVirtualMedia.InsertVirtualMedia": {
          "target": "/redfish/v1/Managers/1/VirtualMedia/2/Actions/Oem/Hpe/HpeiLOVirtualMedia.InsertVirtualMedia/"
        }
      },
      "BootOnNextServerReset": false
    }
  },
  "WriteProtected": true
}
[XXXXXX@welktxefnce-h-pe1util-vm01 packages]$ curl -g -u XXXXXX:XXXXXX --insecure  -H "Content-Type: application/json" -X POST https://[$IP]/redfish/v1/Managers/1/VirtualMedia/2/Actions/VirtualMedia.EjectMedia/ | jq .
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   187    0   187    0     0    490      0 --:--:-- --:--:-- --:--:--   489
{
  "error": {
    "code": "iLO.0.10.ExtendedInfo",
    "message": "See @Message.ExtendedInfo for more information.",
    "@Message.ExtendedInfo": [
      {
        "MessageId": "iLO.2.23.NoVirtualMediaConnectionAvailable"
      }
    ]
  }
}
[XXXXXX@welktxefnce-h-pe1util-vm01 packages]$ curl -g -u XXXXXX:XXXXXX --insecure  -H "Content-Type: application/json" -X POST -d '{"Image": "http://[2607:f160:10:9239:ce:290:0:3000]:8080/bootimage_hpe-e910t_intelv710_9-20_fvl_upgrade.iso"}'  https://[$IP]/redfish/v1/Managers/1/VirtualMedia/2/Actions/VirtualMedia.InsertMedia/ | jq .
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   271    0   162  100   109    278    187 --:--:-- --:--:-- --:--:--   464
{
  "error": {
    "code": "iLO.0.10.ExtendedInfo",
    "message": "See @Message.ExtendedInfo for more information.",
    "@Message.ExtendedInfo": [
      {
        "MessageId": "Base.1.18.Success"
      }
    ]
  }
}
[XXXXXX@welktxefnce-h-pe1util-vm01 packages]$ curl -g -u XXXXXX:XXXXXX --insecure  -H "Content-Type: application/json" -X PATCH -d '{ "Oem": {"Hpe": {"BootOnNextServerReset": true}} }'  https://[$IP]/redfish/v1/Managers/1/VirtualMedia/2/ | jq .
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   213    0   162  100    51    256     80 --:--:-- --:--:-- --:--:--   337
{
  "error": {
    "code": "iLO.0.10.ExtendedInfo",
    "message": "See @Message.ExtendedInfo for more information.",
    "@Message.ExtendedInfo": [
      {
        "MessageId": "Base.1.18.Success"
      }
    ]
  }
}
[XXXXXX@welktxefnce-h-pe1util-vm01 packages]$ curl -g -u XXXXXX:XXXXXX --insecure  -H "Content-Type: application/json" -X PATCH https://[$IP]/redfish/v1/Systems/1/BIOS/Boot/Settings/ -d '{ "Boot": { "BootSourceOverrideEnabled": "Once", "BootSourceOverrideTarget": "Cd", "BootSourceOverrideMode": "UEFI"}}' | jq .
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   290    0   173  100   117    332    224 --:--:-- --:--:-- --:--:--   556
{
  "error": {
    "code": "iLO.0.10.ExtendedInfo",
    "message": "See @Message.ExtendedInfo for more information.",
    "@Message.ExtendedInfo": [
      {
        "MessageId": "iLO.2.23.SystemResetRequired"
      }
    ]
  }
}
[XXXXXX@welktxefnce-h-pe1util-vm01 packages]$ curl -g -u XXXXXX:XXXXXX --insecure -H "Content-Type: application/json" -X POST -d '{"ResetType" : "ForceRestart"}' https://[$IP]/redfish/v1/Systems/1/Actions/ComputerSystem.Reset/
{"error":{"code":"iLO.0.10.ExtendedInfo","message":"See @Message.ExtendedInfo for more information.","@Message.ExtendedInfo":[{"MessageId":"Base.1.18.Success"}]}}[XXXXXX@welktxefnce-h-pe1util-vm01 packages]$

```


### After the upgrade check the version of the nic card firmware
### From the ILO UI ---> success
```log
HPE Ethernet 10/25Gb 2-port 661SFP28 Adapter 	1.3353.0 	PCI-E Slot 31

```

