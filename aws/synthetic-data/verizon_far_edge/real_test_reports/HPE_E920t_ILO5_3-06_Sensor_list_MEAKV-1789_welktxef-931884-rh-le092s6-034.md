# HPE ILO5 3.06 BIOS H10 v1.70
# HPE Sapphire Rapids E920t server
# 9/6/24 James Patchett - MTCE Lab VCPfe
# sensors MEAKV-1750

## welktxef-931884-rh-le292s6-034
ILO:  2607:f160:10:9249:ce:40a:0:e009
OAM:  2607:f160:10:9249:ce:40a:0:f408

## Subcloud welktxef-d931884-034 
## General info before we start

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ system show
+------------------------+--------------------------------------+
| Property               | Value                                |
+------------------------+--------------------------------------+
| contact                | None                                 |
| created_at             | 2024-08-23T14:55:17.130193+00:00     |
| description            | None                                 |
| distributed_cloud_role | subcloud                             |
| https_enabled          | True                                 |
| latitude               | None                                 |
| location               | None                                 |
| longitude              | None                                 |
| name                   | welktxef-d931884-034                 |
| region_name            | welktxef-d931884-034                 |
| sdn_enabled            | False                                |
| security_feature       | spectre_meltdown_v1                  |
| service_project_name   | services                             |
| shared_services        | []                                   |
| software_version       | 22.12                                |
| system_mode            | simplex                              |
| system_type            | All-in-one                           |
| timezone               | UTC                                  |
| updated_at             | 2024-08-28T16:36:15.405154+00:00     |
| uuid                   | 55b2fccb-ef0b-4e94-afa1-bcefcb789357 |
| vswitch_type           | none                                 |
+------------------------+--------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ system oam-show
+----------------+---------------------------------------+
| Property       | Value                                 |
+----------------+---------------------------------------+
| created_at     | 2024-08-23T14:57:11.033367+00:00      |
| isystem_uuid   | 55b2fccb-ef0b-4e94-afa1-bcefcb789357  |
| oam_end_ip     | 2607:f160:10:9249:ffff:ffff:ffff:fffe |
| oam_gateway_ip | 2607:f160:10:9249:ce:28::             |
| oam_ip         | 2607:f160:10:9249:ce:40a:0:f408       |
| oam_start_ip   | 2607:f160:10:9249::1                  |
| oam_subnet     | 2607:f160:10:9249::/64                |
| updated_at     | None                                  |
| uuid           | 2970009b-1352-4840-a9a7-7274899c7946  |
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

[XXXXXX@controller-0 ~(keystone_admin)]$
```

### List all sensors on the machine
### Validate no sensors are experiencing issues, or not showing data

```log
root@controller-0:~# ipmitool sensor
UID              | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
SysHealth_Stat   | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
01-Inlet Ambient | 27.000     | degrees C  | ok    | na        | na        | na        | na        | 62.000    | 66.000
02-CPU 1         | 40.000     | degrees C  | ok    | na        | na        | na        | na        | 70.000    | na
03-P1 DIMM 1-6   | 40.000     | degrees C  | ok    | na        | na        | na        | na        | 90.000    | na
04-P1 PMM 1-6    | na         |            | na    | na        | na        | na        | na        | 82.000    | na
05-P1 DIMM 7-12  | 36.000     | degrees C  | ok    | na        | na        | na        | na        | 90.000    | na
06-P1 PMM 7-12   | na         |            | na    | na        | na        | na        | na        | 82.000    | na
07-VR P1         | 54.000     | degrees C  | ok    | na        | na        | na        | na        | 110.000   | 115.000
08-VR P1 Mem 1   | 44.000     | degrees C  | ok    | na        | na        | na        | na        | 110.000   | 115.000
09-VR P1 Mem 2   | 35.000     | degrees C  | ok    | na        | na        | na        | na        | 110.000   | 115.000
10-Chipset       | 32.000     | degrees C  | ok    | na        | na        | na        | na        | 100.000   | na
12-Battery Zone  | 27.000     | degrees C  | ok    | na        | na        | na        | na        | 70.000    | 75.000
17-LOM Card      | na         |            | na    | na        | na        | na        | na        | 100.000   | na
18-LOM Card Zone | 24.000     | degrees C  | ok    | na        | na        | na        | na        | 95.000    | 100.000
20-mLOM Zone     | na         |            | na    | na        | na        | na        | na        | 85.000    | 90.000
21-PCI 1         | 37.000     | degrees C  | ok    | na        | na        | na        | na        | 100.000   | na
22-PCI 1 Zone    | 26.000     | degrees C  | ok    | na        | na        | na        | na        | 70.000    | 75.000
23-PCI 2         | 36.000     | degrees C  | ok    | na        | na        | na        | na        | 100.000   | na
24-PCI 2 Zone    | 26.000     | degrees C  | ok    | na        | na        | na        | na        | 70.000    | 75.000
25-PCI 3         | 50.000     | degrees C  | ok    | na        | na        | na        | na        | 100.000   | na
26-PCI 3 Zone    | 26.000     | degrees C  | ok    | na        | na        | na        | na        | 70.000    | 75.000
27-PCI 4         | na         |            | na    | na        | na        | na        | na        | 100.000   | na
28-PCI 4 Zone    | na         |            | na    | na        | na        | na        | na        | 70.000    | 75.000
29-PCI 5         | na         |            | na    | na        | na        | na        | na        | 100.000   | na
30-PCI 5 Zone    | na         |            | na    | na        | na        | na        | na        | 70.000    | 75.000
31-E-Fuse 1      | 36.000     | degrees C  | ok    | na        | na        | na        | na        | 100.000   | na
32-E-Fuse 2      | 29.000     | degrees C  | ok    | na        | na        | na        | na        | 100.000   | na
33-E-Fuse 3      | 25.000     | degrees C  | ok    | na        | na        | na        | na        | 100.000   | na
34-Stor Batt     | na         |            | na    | na        | na        | na        | na        | 60.000    | na
39-Sys Exhaust 1 | 40.000     | degrees C  | ok    | na        | na        | na        | na        | 85.000    | 90.000
40-CPU 1 PkgTmp  | 68.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
45-HD Controller | na         |            | na    | na        | na        | na        | na        | 100.000   | na
46-HD Cntlr Zone | na         |            | na    | na        | na        | na        | na        | na        | na
47-HD Max        | na         |            | na    | na        | na        | na        | na        | 60.000    | na
48-Board Inlet   | na         |            | na    | na        | na        | na        | na        | na        | na
Fan 1            | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
Fan 1 DutyCycle  | 47.824     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 1 Presence   | 0x0        | discrete   | 0x0280| na        | na        | na        | na        | na        | na
Fan 2            | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
Fan 2 DutyCycle  | 39.984     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 2 Presence   | 0x0        | discrete   | 0x0280| na        | na        | na        | na        | na        | na
Fan 3            | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
Fan 3 DutyCycle  | 39.984     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 3 Presence   | 0x0        | discrete   | 0x0280| na        | na        | na        | na        | na        | na
Fan 4            | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
Fan 4 DutyCycle  | 39.984     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 4 Presence   | 0x0        | discrete   | 0x0280| na        | na        | na        | na        | na        | na
Fan 5            | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
Fan 5 DutyCycle  | 39.984     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 5 Presence   | 0x0        | discrete   | 0x0280| na        | na        | na        | na        | na        | na
Fan 6            | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
Fan 6 DutyCycle  | 39.984     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 6 Presence   | 0x0        | discrete   | 0x0280| na        | na        | na        | na        | na        | na
Power Supply 1   | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
PS 1 Input       | 150.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
Power Supply 2   | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
PS 2 Input       | 190.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
Fans             | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
Memory Status    | 0x0        | discrete   | 0x4080| na        | na        | na        | na        | na        | na
Megacell Status  | na         | discrete   | na    | na        | na        | na        | na        | na        | na
CPU Utilization  | 71.000     | percent    | ok    | na        | na        | na        | na        | na        | na
PS 1 Output      | 0.000      | Watts      | ok    | na        | na        | na        | na        | na        | na
PS_Volt_Out_01   | 0.000      | Volts      | ok    | na        | na        | na        | na        | na        | na
PS_Volt_In_01    | 214.000    | Volts      | ok    | na        | na        | na        | na        | na        | na
PS_Curr_Out_01   | 0.000      | Amps       | ok    | na        | na        | na        | na        | na        | na
PS_Curr_In_01    | 0.400      | Amps       | ok    | na        | na        | na        | na        | na        | na
PS 2 Output      | 0.000      | Watts      | ok    | na        | na        | na        | na        | na        | na
PS_Volt_Out_02   | 0.000      | Volts      | ok    | na        | na        | na        | na        | na        | na
PS_Volt_In_02    | 212.000    | Volts      | ok    | na        | na        | na        | na        | na        | na
PS_Curr_Out_02   | 0.000      | Amps       | ok    | na        | na        | na        | na        | na        | na
PS_Curr_In_02    | 0.400      | Amps       | ok    | na        | na        | na        | na        | na        | na
CPU_Stat_C1      | 0x0        | discrete   | 0x8080| na        | na        | na        | na        | na        | na
root@controller-0:~#
```

### Test has PASSED

No issues with detecting missing sensors, or data
