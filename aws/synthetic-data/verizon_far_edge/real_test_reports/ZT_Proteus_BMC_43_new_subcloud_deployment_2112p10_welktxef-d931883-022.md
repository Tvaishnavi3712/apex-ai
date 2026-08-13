# ZT .43 BMC firmware validation
# New deploy of sublcoud on 21.12p10
# 9/22/23 James Patchett

## Build and setup of environment

## Target Controller Rchltxfe-c000000-001
Controller-0 iLO 2607:f160:a:d02e:cd:fe0::8000 
Controller-1 iLO 2607:f160:a:d02e:cd:fe0::8001
Worker-0 iLO 2607:f160:a:d02e:cd:fe0::8002 
OAM 2607:f160:0:3043:cd:290:0:10



## Target Subcloud 
welktxef-d931856-008
OAM: 2607:f160:10:80b1:ce:40a:0:f408
BMC: 2607:f160:10:80b1:ce:40a:0:e008


ipmitool -I lanplus -U XXXXXX -P XXXXXX -H 2607:f160:10:80b1:ce:40a:0:e008 sol activate

host_vars:  welktxef-931856-rz-le2pts6-008
From Inventory file not sure its accurate:

OAM: 2607:f160:10:80b1:ce:40a:0:f408
GW: 2607:f160:10:80b1:ce:23::
VLAN: 409
MGMT: 2607:f160:10:80bb::/64
GW: 2607:f160:10:80bb:ce:23::
VLAN: 642



### Routes on the subcloud:
```log
2607:f160:0:3042::/64 via 2607:f160:10:924b:ce:28:: dev vlan622 metric 1 pref medium
2607:f160:10:9249::/64 dev vlan409 proto kernel metric 256 pref medium
2607:f160:10:924b::/64 dev vlan622 proto kernel metric 256 pref medium
fe80::/64 dev vlan409 proto kernel metric 256 pref medium
fe80::/64 dev vlan622 proto kernel metric 256 pref medium
default via 2607:f160:10:9249:ce:28:: dev vlan409 metric 1024 onlink pref medium
```

## Baseline record of controller and subcloud
### Controller:

```log


```

### Subcloud firmware query shows .43, we can now continue with deployment automation 
### Also setting MWAIT enabled for the deployment since this is a ZT proteus
```log
[XXXXXX@welktxefnce-h-pe1util-vm01 host_vars]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/UpdateService/FirmwareInventory/BMC | jq
{
  "@odata.context": "/redfish/v1/$metadata#SoftwareInventory.SoftwareInventory",
  "@odata.etag": "\"1695406675\"",
  "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/BMC",
  "@odata.type": "#SoftwareInventory.v1_2_3.SoftwareInventory",
  "Id": "BMC",
  "Name": "BMC",
  "Updateable": true,
  "Version": "0.43.00"
}
[XXXXXX@welktxefnce-h-pe1util-vm01 host_vars]$

[XXXXXX@welktxefnce-h-pe1util-vm01 host_vars]$ curl -k -w "\\n%{http_code} %{url_effective}\\n" -u XXXXXX:XXXXXX -H "Content-Type: application/json" -d '{"Attributes": {"PMS012": "Enable"}}' -X PATCH https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/Systems/Self/Bios/SD

204 https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/Systems/Self/Bios/SD
[XXXXXX@welktxefnce-h-pe1util-vm01 host_vars]$ curl -u XXXXXX:XXXXXX -ks https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/Systems/Self/Bios | jq '.Attributes.PMS012'
"Enable"
[XXXXXX@welktxefnce-h-pe1util-vm01 host_vars]$

```


### deploying subcloud with 21.12p10 through Ansible server

