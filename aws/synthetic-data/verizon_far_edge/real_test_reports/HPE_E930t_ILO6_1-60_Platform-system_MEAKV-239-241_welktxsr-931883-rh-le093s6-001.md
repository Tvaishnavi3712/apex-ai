# HPE ILO6 1.60 BIOS H11 v1.11
# HPE Sapphire Rapids E930t server
# 6/28/24 James Patchett - MTCE Lab VCPfe
# Platform Deploymnet MEAKV-239-241

## Controller rchltxfe-c000000-001
OAM:  2607:f160:0:3043:cd:290:0:10

## welktxsr-931883-rh-le093s6-001
## welktxsr-d931883-001
ILO:  2607:f160:10:80b1:ce:40a:0:e002
OAM:  2607:f160:10:80b1:ce:40a:0:f402


## welktxsr-d931883-001
## Subcloud status/info before we start

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ system show
+------------------------+--------------------------------------+
| Property               | Value                                |
+------------------------+--------------------------------------+
| contact                | None                                 |
| created_at             | 2024-06-28T16:59:06.305793+00:00     |
| description            | None                                 |
| distributed_cloud_role | subcloud                             |
| https_enabled          | True                                 |
| latitude               | None                                 |
| location               | None                                 |
| longitude              | None                                 |
| name                   | welktxsr-d931883-001                 |
| region_name            | welktxsr-d931883-001                 |
| sdn_enabled            | False                                |
| security_feature       | spectre_meltdown_v1                  |
| service_project_name   | services                             |
| shared_services        | []                                   |
| software_version       | 22.12                                |
| system_mode            | simplex                              |
| system_type            | All-in-one                           |
| timezone               | UTC                                  |
| updated_at             | 2024-06-28T17:49:39.995411+00:00     |
| uuid                   | bb1b30b6-3971-4a90-b360-77c37e117c8f |
| vswitch_type           | none                                 |
+------------------------+--------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ system oam-show
+----------------+---------------------------------------+
| Property       | Value                                 |
+----------------+---------------------------------------+
| created_at     | 2024-06-28T17:00:44.323797+00:00      |
| isystem_uuid   | bb1b30b6-3971-4a90-b360-77c37e117c8f  |
| oam_end_ip     | 2607:f160:10:80b1:ffff:ffff:ffff:fffe |
| oam_gateway_ip | 2607:f160:10:80b1:ce:23::             |
| oam_ip         | 2607:f160:10:80b1:ce:40a:0:f402       |
| oam_start_ip   | 2607:f160:10:80b1::1                  |
| oam_subnet     | 2607:f160:10:80b1::/64                |
| updated_at     | None                                  |
| uuid           | d7c9003a-12f6-42f7-b7c9-e953d5f0eeb7  |
+----------------+---------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ system application-list
+--------------------------+----------+-------------------------------------------+------------------+---------+-----------+
| application              | version  | manifest name                             | manifest file    | status  | progress  |
+--------------------------+----------+-------------------------------------------+------------------+---------+-----------+
| cert-manager             | 22.12-8  | cert-manager-fluxcd-manifests             | fluxcd-manifests | applied | completed |
| metrics-server           | 22.12-2  | metrics-server-fluxcd-manifests           | fluxcd-manifests | applied | completed |
| nginx-ingress-controller | 22.12-1  | nginx-ingress-controller-fluxcd-manifests | fluxcd-manifests | applied | completed |
| oidc-auth-apps           | 22.12-6  | oidc-auth-apps-fluxcd-manifests           | fluxcd-manifests | applied | completed |
| platform-integ-apps      | 22.12-72 | platform-integ-apps-fluxcd-manifests      | fluxcd-manifests | applied | completed |
| wr-analytics             | 23.09-1  | wr-analytics-fluxcd-manifests             | fluxcd-manifests | applied | completed |
+--------------------------+----------+-------------------------------------------+------------------+---------+-----------+
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

## MEAKV-239
## Subcloud welktxsr-d931883-012

```log

[XXXXXX@controller-0 ~(keystone_admin)]$ system host-show 1 |grep bm
| bm_ip                  | None                                                                    |
| bm_type                | none                                                                    |
| bm_username            | None                                                                    |
[XXXXXX@controller-0 ~(keystone_admin)]$


[XXXXXX@controller-0 ~(keystone_admin)]$ system host-update controller-0 bm_ip=2607:f160:10:80b1:ce:40a:0:e002 bm_type=redfish bm_username=XXXXXX bm_password=XXXXXX
+------------------------+-------------------------------------------------------------------------+
| Property               | Value                                                                   |
+------------------------+-------------------------------------------------------------------------+
| action                 | none                                                                    |
| administrative         | unlocked                                                                |
| apparmor               | disabled                                                                |
| availability           | available                                                               |
| bm_ip                  | 2607:f160:10:80b1:ce:40a:0:e002                                         |
| bm_type                | redfish                                                                 |
| bm_username            | XXXXXX                                                           |
| boot_device            | /dev/disk/by-path/pci-0000:03:00.0-nvme-1                               |
| capabilities           | {'is_max_cpu_configurable': 'configurable', 'min_cpu_mhz_allowed': 800, |
|                        | 'max_cpu_mhz_allowed': 3600, 'cstates_available': 'C1,C2,POLL',         |
|                        | 'stor_function': 'monitor'}                                             |
| clock_synchronization  | ntp                                                                     |
| config_applied         | 1d867f6f-6300-4e5f-9c60-8144502f5159                                    |
| config_status          | None                                                                    |
| config_target          | 1d867f6f-6300-4e5f-9c60-8144502f5159                                    |
| console                | ttyS0,115200                                                            |
| created_at             | 2024-06-28T17:00:45.976144+00:00                                        |
| device_image_update    | None                                                                    |
| hostname               | controller-0                                                            |
| hw_settle              | 0                                                                       |
| id                     | 1                                                                       |
| install_output         | text                                                                    |
| install_state          | None                                                                    |
| install_state_info     | None                                                                    |
| inv_state              | inventoried                                                             |
| invprovision           | provisioned                                                             |
| location               | {}                                                                      |
| max_cpu_mhz_allowed    | 3600                                                                    |
| max_cpu_mhz_configured | None                                                                    |
| mgmt_ip                | 2607:f160:10:80d2:ce:40a:0:1                                            |
| mgmt_mac               | f0:b2:b9:14:3a:b4                                                       |
| operational            | enabled                                                                 |
| personality            | controller                                                              |
| reboot_needed          | False                                                                   |
| reserved               | False                                                                   |
| rootfs_device          | /dev/disk/by-path/pci-0000:03:00.0-nvme-1                               |
| serialid               | None                                                                    |
| software_load          | 22.12                                                                   |
| subfunction_avail      | available                                                               |
| subfunction_oper       | enabled                                                                 |
| subfunctions           | controller,worker,lowlatency                                            |
| task                   |                                                                         |
| tboot                  |                                                                         |
| ttys_dcd               | False                                                                   |
| updated_at             | 2024-06-28T22:13:04.826964+00:00                                        |
| uptime                 | 17155                                                                   |
| uuid                   | f6909a48-850b-4b0b-baa7-8def07daca3a                                    |
| vim_progress_status    | services-enabled                                                        |
+------------------------+-------------------------------------------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$
[XXXXXX@controller-0 ~(keystone_admin)]$ system host-show 1
+------------------------+-------------------------------------------------------------------------+
| Property               | Value                                                                   |
+------------------------+-------------------------------------------------------------------------+
| action                 | none                                                                    |
| administrative         | unlocked                                                                |
| apparmor               | disabled                                                                |
| availability           | available                                                               |
| bm_ip                  | 2607:f160:10:80b1:ce:40a:0:e002                                         |
| bm_type                | redfish                                                                 |
| bm_username            | XXXXXX                                                           |
| boot_device            | /dev/disk/by-path/pci-0000:03:00.0-nvme-1                               |
| capabilities           | {'is_max_cpu_configurable': 'configurable', 'min_cpu_mhz_allowed': 800, |
|                        | 'max_cpu_mhz_allowed': 3600, 'cstates_available': 'C1,C2,POLL',         |
|                        | 'stor_function': 'monitor', 'Personality': 'Controller-Active'}         |
| clock_synchronization  | ntp                                                                     |
| config_applied         | 1d867f6f-6300-4e5f-9c60-8144502f5159                                    |
| config_status          | None                                                                    |
| config_target          | 1d867f6f-6300-4e5f-9c60-8144502f5159                                    |
| console                | ttyS0,115200                                                            |
| created_at             | 2024-06-28T17:00:45.976144+00:00                                        |
| device_image_update    | None                                                                    |
| hostname               | controller-0                                                            |
| hw_settle              | 0                                                                       |
| id                     | 1                                                                       |
| install_output         | text                                                                    |
| install_state          | None                                                                    |
| install_state_info     | None                                                                    |
| inv_state              | inventoried                                                             |
| invprovision           | provisioned                                                             |
| location               | {}                                                                      |
| max_cpu_mhz_allowed    | 3600                                                                    |
| max_cpu_mhz_configured | None                                                                    |
| mgmt_ip                | 2607:f160:10:80d2:ce:40a:0:1                                            |
| mgmt_mac               | f0:b2:b9:14:3a:b4                                                       |
| operational            | enabled                                                                 |
| personality            | controller                                                              |
| reboot_needed          | False                                                                   |
| reserved               | False                                                                   |
| rootfs_device          | /dev/disk/by-path/pci-0000:03:00.0-nvme-1                               |
| serialid               | None                                                                    |
| software_load          | 22.12                                                                   |
| subfunction_avail      | available                                                               |
| subfunction_oper       | enabled                                                                 |
| subfunctions           | controller,worker,lowlatency                                            |
| task                   |                                                                         |
| tboot                  |                                                                         |
| ttys_dcd               | False                                                                   |
| updated_at             | 2024-06-28T22:15:26.026357+00:00                                        |
| uptime                 | 17155                                                                   |
| uuid                   | f6909a48-850b-4b0b-baa7-8def07daca3a                                    |
| vim_progress_status    | services-enabled                                                        |
+------------------------+-------------------------------------------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ system host-show 1|grep bm
| bm_ip                  | 2607:f160:10:80b1:ce:40a:0:e002                                         |
| bm_type                | redfish                                                                 |
| bm_username            | XXXXXX                                                           |
[XXXXXX@controller-0 ~(keystone_admin)]$
```

## Success


## MEAKV-240

```log

[XXXXXX@controller-0 ~(keystone_admin)]$ system host-show 1 | grep bm
| bm_ip                  | 2607:f160:10:80b1:ce:40a:0:e002                                         |
| bm_type                | redfish                                                                 |
| bm_username            | XXXXXX                                                           |
[XXXXXX@controller-0 ~(keystone_admin)]$ system host-sensor-list 1
+--------------------------------------+------------------------+-------------+---------+---------+
| uuid                                 | name                   | sensortype  | state   | status  |
+--------------------------------------+------------------------+-------------+---------+---------+
| fc8e3e54-42d2-4c19-a1a7-3d2a2e2c3ff5 | 01-Inlet Ambient       | temperature | enabled | ok      |
| 37ed06ae-b50a-46bb-9175-830cc9df35b8 | 02-CPU 1 PkgTmp        | temperature | enabled | ok      |
| aa3b4401-d209-4d11-9f40-b065e251e5be | 03-P1 DIMM 1-6         | temperature | enabled | ok      |
| e8579687-98f8-4cda-9762-a15b4369c6d0 | 04-P1 PMM 1-6          | temperature | enabled | offline |
| d3c07c6a-59a4-4170-950c-5d1bf5367151 | 05-P1 DIMM 7-12        | temperature | enabled | ok      |
| 6264c9c1-6616-4532-be41-b1d1ca994d27 | 06-P1 PMM 7-12         | temperature | enabled | offline |
| 42c3c592-fbb3-4e7d-922e-3cb3a7f3e62e | 07-VR P1               | temperature | enabled | ok      |
| 3294e349-23d4-42e2-b36b-8d8c230abfe9 | 08-Chipset             | temperature | enabled | ok      |
| 728215bf-0160-4da0-9e41-c3f3d3d84ee5 | 09-BMC                 | temperature | enabled | ok      |
| fbacf122-2abd-4ea5-ba57-630dc614d918 | 10-M2                  | temperature | enabled | ok      |
| b9b437ba-59fd-4605-8367-361b9c35b65d | 15.1-PCI 1-Network     | temperature | enabled | ok      |
|                                      | controller             |             |         |         |
|                                      |                        |             |         |         |
| 6f590702-203c-4b37-a74b-7240f44c6fc8 | 15.2-PCI 1-SFP28       | temperature | enabled | ok      |
|                                      | (SFF-8402)             |             |         |         |
|                                      |                        |             |         |         |
| 1fc63155-47e5-4568-8165-26b5eec35452 | 15.3-PCI 1-SFP28       | temperature | enabled | ok      |
|                                      | (SFF-8402)             |             |         |         |
|                                      |                        |             |         |         |
| 3befa2b4-1ac4-442c-8af1-e5408546b65b | 15.4-PCI 1-SFP28       | temperature | enabled | ok      |
|                                      | (SFF-8402)             |             |         |         |
|                                      |                        |             |         |         |
| 5dc5eddc-e6a9-433f-81ff-306f4022b49e | 15.5-PCI 1-SFP28       | temperature | enabled | ok      |
|                                      | (SFF-8402)             |             |         |         |
|                                      |                        |             |         |         |
| 090e3864-ca6e-45c9-a9aa-9cbf5cdc30e4 | 16-PCI 1 Zone          | temperature | enabled | ok      |
| be356e15-cc28-4bc5-870f-91c9e9a6a693 | 17.1-PCI 2-Network     | temperature | enabled | ok      |
|                                      | controller             |             |         |         |
|                                      |                        |             |         |         |
| 2230a958-fedb-4e98-8ee2-7b44cb399343 | 17.2-PCI 2-SFP28       | temperature | enabled | ok      |
|                                      | (SFF-8402)             |             |         |         |
|                                      |                        |             |         |         |
| 9fca1a45-6f5a-4a53-b187-5f5bbb7192c8 | 17.3-PCI 2-SFP28       | temperature | enabled | ok      |
|                                      | (SFF-8402)             |             |         |         |
|                                      |                        |             |         |         |
| ad8977d1-06f5-4516-9950-94ff502fe677 | 18-PCI 2 Zone          | temperature | enabled | ok      |
| c865b9f0-045f-4a6a-a9f2-148fba91ecf3 | 19.1-PCI 3-Network     | temperature | enabled | ok      |
|                                      | controller             |             |         |         |
|                                      |                        |             |         |         |
| bf203188-edf2-4dc5-a1aa-a000f3a84c19 | 19.2-PCI 3-SFP28       | temperature | enabled | ok      |
|                                      | (SFF-8402)             |             |         |         |
|                                      |                        |             |         |         |
| 6f576c58-eccb-486f-b1ac-6c88345ee0ff | 19.3-PCI 3-SFP28       | temperature | enabled | ok      |
|                                      | (SFF-8402)             |             |         |         |
|                                      |                        |             |         |         |
| 60304c1d-2c18-4bff-afbc-254a8e992d8b | 20-PCI 3 Zone          | temperature | enabled | ok      |
| 56ef55eb-05b6-4e7e-8f1c-b0176363371f | 21-PCI 4               | temperature | enabled | offline |
| 3583c61a-2097-4202-b2d6-5cc3feab34ec | 22-PCI 4 Zone          | temperature | enabled | offline |
| 5de18a15-88a1-4607-b574-31539a75b5b5 | 27-Sys Exhaust 1       | temperature | enabled | ok      |
| b6964613-41fd-4868-a45d-9f844851fe6e | Fan 1                  | fan         | enabled | ok      |
| e3404c44-4bc6-4739-a802-f46c10bda578 | Fan 2                  | fan         | enabled | ok      |
| 04601ac4-62bc-4d67-8274-e25b6e3a5058 | Fan 3                  | fan         | enabled | ok      |
| afca9867-d0cc-4922-aa71-1631fbf56124 | Fan 4                  | fan         | enabled | ok      |
| 22b3af92-c39a-45bf-b7b0-01c14b9b16de | Fan 5                  | fan         | enabled | ok      |
| c5b84ec5-ccdc-4e8e-8da0-302b3e89408a | Fan 6                  | fan         | enabled | ok      |
| 43b94237-26fc-47f2-940f-d24404f0e662 | HpeServerPowerSupply   | power       | enabled | ok      |
+--------------------------------------+------------------------+-------------+---------+---------+
[XXXXXX@controller-0 ~(keystone_admin)]$
```

## Lets compare to what the OS can get with IMPITOOL 

```log
root@controller-0:~# ipmitool sensor
UID              | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
SysHealth_Stat   | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
01-Inlet Ambient | 32.000     | degrees C  | ok    | na        | na        | na        | na        | 62.000    | 66.000
02-CPU 1 PkgTmp  | 61.000     | degrees C  | ok    | na        | na        | na        | na        | 91.000    | na
03-P1 DIMM 1-6   | 42.000     | degrees C  | ok    | na        | na        | na        | na        | 90.000    | na
04-P1 PMM 1-6    | na         |            | na    | na        | na        | na        | na        | 82.000    | na
05-P1 DIMM 7-12  | 50.000     | degrees C  | ok    | na        | na        | na        | na        | 90.000    | na
06-P1 PMM 7-12   | na         |            | na    | na        | na        | na        | na        | 82.000    | na
07-VR P1         | 57.000     | degrees C  | ok    | na        | na        | na        | na        | 110.000   | na
08-Chipset       | 48.000     | degrees C  | ok    | na        | na        | na        | na        | 100.000   | na
09-BMC           | 55.000     | degrees C  | ok    | na        | na        | na        | na        | 110.000   | na
10-M2            | 40.000     | degrees C  | ok    | na        | na        | na        | na        | 80.000    | na
16-PCI 1 Zone    | 32.000     | degrees C  | ok    | na        | na        | na        | na        | 70.000    | 75.000
18-PCI 2 Zone    | 32.000     | degrees C  | ok    | na        | na        | na        | na        | 70.000    | 75.000
20-PCI 3 Zone    | 32.000     | degrees C  | ok    | na        | na        | na        | na        | 70.000    | 75.000
21-PCI 4         | na         |            | na    | na        | na        | na        | na        | 95.000    | na
22-PCI 4 Zone    | na         |            | na    | na        | na        | na        | na        | 70.000    | 75.000
27-Sys Exhaust 1 | 51.000     | degrees C  | ok    | na        | na        | na        | na        | 85.000    | na
Fan 1            | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
Fan 1 DutyCycle  | 17.640     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 1 Presence   | 0x0        | discrete   | 0x0280| na        | na        | na        | na        | na        | na
Fan 2            | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
Fan 2 DutyCycle  | 17.640     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 2 Presence   | 0x0        | discrete   | 0x0280| na        | na        | na        | na        | na        | na
Fan 3            | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
Fan 3 DutyCycle  | 17.640     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 3 Presence   | 0x0        | discrete   | 0x0280| na        | na        | na        | na        | na        | na
Fan 4            | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
Fan 4 DutyCycle  | 17.640     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 4 Presence   | 0x0        | discrete   | 0x0280| na        | na        | na        | na        | na        | na
Fan 5            | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
Fan 5 DutyCycle  | 17.640     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 5 Presence   | 0x0        | discrete   | 0x0280| na        | na        | na        | na        | na        | na
Fan 6            | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
Fan 6 DutyCycle  | 17.640     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 6 Presence   | 0x0        | discrete   | 0x0280| na        | na        | na        | na        | na        | na
Power Supply 1   | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
PS 1 Input       | 150.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
Power Supply 2   | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
PS 2 Input       | 2550.000   | Watts      | ok    | na        | na        | na        | na        | na        | na
Power Meter      | 130.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
Fans             | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
Memory Status    | 0x0        | discrete   | 0x4080| na        | na        | na        | na        | na        | na
Megacell Status  | na         | discrete   | na    | na        | na        | na        | na        | na        | na
Intrusion        | na         | discrete   | na    | na        | na        | na        | na        | na        | na
CPU Utilization  | 7.000      | unspecified | ok    | na        | na        | na        | na        | na        | na
PS 1 Output      | 0.000      | Watts      | ok    | na        | na        | na        | na        | na        | na
PS_Volt_Out_01   | 0.000      | Volts      | ok    | na        | na        | na        | na        | na        | na
PS_Volt_In_01    | 211.000    | Volts      | ok    | na        | na        | na        | na        | na        | na
PS_Curr_Out_01   | 0.000      | Amps       | ok    | na        | na        | na        | na        | na        | na
PS_Curr_In_01    | 0.300      | Amps       | ok    | na        | na        | na        | na        | na        | na
PS 2 Output      | 0.000      | Watts      | ok    | na        | na        | na        | na        | na        | na
PS_Volt_Out_02   | 0.000      | Volts      | ok    | na        | na        | na        | na        | na        | na
PS_Volt_In_02    | 212.000    | Volts      | ok    | na        | na        | na        | na        | na        | na
PS_Curr_Out_02   | 0.000      | Amps       | ok    | na        | na        | na        | na        | na        | na
PS_Curr_In_02    | 0.300      | Amps       | ok    | na        | na        | na        | na        | na        | na
15.1-PCI 1-Netwo | 67.000     | degrees C  | ok    | na        | na        | na        | 95.000    | 105.000   | 115.000
15.2-PCI 1-SFP28 | 41.000     | degrees C  | ok    | na        | na        | na        | 73.000    | 78.000    | 0.000
15.3-PCI 1-SFP28 | 37.000     | degrees C  | ok    | na        | na        | na        | 70.000    | 75.000    | 0.000
15.4-PCI 1-SFP28 | 37.000     | degrees C  | ok    | na        | na        | na        | 70.000    | 75.000    | 0.000
15.5-PCI 1-SFP28 | 37.000     | degrees C  | ok    | na        | na        | na        | 70.000    | 75.000    | 0.000
17.1-PCI 2-Netwo | 70.000     | degrees C  | ok    | na        | na        | na        | 95.000    | 105.000   | 115.000
17.2-PCI 2-SFP28 | 32.000     | degrees C  | ok    | na        | na        | na        | 70.000    | 75.000    | 0.000
17.3-PCI 2-SFP28 | 33.000     | degrees C  | ok    | na        | na        | na        | 70.000    | 75.000    | 0.000
19.1-PCI 3-Netwo | 64.000     | degrees C  | ok    | na        | na        | na        | 95.000    | 105.000   | 115.000
19.2-PCI 3-SFP28 | 37.000     | degrees C  | ok    | na        | na        | na        | 73.000    | 78.000    | 0.000
19.3-PCI 3-SFP28 | 33.000     | degrees C  | ok    | na        | na        | na        | 70.000    | 75.000    | 0.000
LOM_Link_P1      | na         | discrete   | na    | na        | na        | na        | na        | na        | na
NIC_Link_01P1    | 0x0        | discrete   | 0x0280| na        | na        | na        | na        | na        | na
NIC_Link_01P2    | 0x0        | discrete   | 0x0280| na        | na        | na        | na        | na        | na
NIC_Link_01P3    | 0x0        | discrete   | 0x0280| na        | na        | na        | na        | na        | na
NIC_Link_01P4    | na         | discrete   | na    | na        | na        | na        | na        | na        | na
NIC_Link_02P1    | na         | discrete   | na    | na        | na        | na        | na        | na        | na
NIC_Link_02P2    | 0x0        | discrete   | 0x0280| na        | na        | na        | na        | na        | na
NIC_Link_02P3    | na         | discrete   | na    | na        | na        | na        | na        | na        | na
NIC_Link_02P4    | 0x0        | discrete   | 0x0280| na        | na        | na        | na        | na        | na
NIC_Link_03P1    | 0x0        | discrete   | 0x0280| na        | na        | na        | na        | na        | na
NIC_Link_03P2    | 0x0        | discrete   | 0x0280| na        | na        | na        | na        | na        | na
NIC_Link_03P3    | na         | discrete   | na    | na        | na        | na        | na        | na        | na
NIC_Link_03P4    | na         | discrete   | na    | na        | na        | na        | na        | na        | na
CPU_Stat_C1      | 0x0        | discrete   | 0x8080| na        | na        | na        | na        | na        | na
root@controller-0:~#
```


## Passed MEAKV-240


### MEAKV-241

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ system host-show 1 | grep bm
| bm_ip                  | 2607:f160:10:80b1:ce:40a:0:e002                                         |
| bm_type                | redfish                                                                 |
| bm_username            | XXXXXX                                                           |
[XXXXXX@controller-0 ~(keystone_admin)]$ system host-update controller-0 bm_type=none
+------------------------+-------------------------------------------------------------------------+
| Property               | Value                                                                   |
+------------------------+-------------------------------------------------------------------------+
| action                 | none                                                                    |
| administrative         | unlocked                                                                |
| apparmor               | disabled                                                                |
| availability           | available                                                               |
| bm_ip                  | None                                                                    |
| bm_type                | none                                                                    |
| bm_username            | None                                                                    |
| boot_device            | /dev/disk/by-path/pci-0000:03:00.0-nvme-1                               |
| capabilities           | {'is_max_cpu_configurable': 'configurable', 'min_cpu_mhz_allowed': 800, |
|                        | 'max_cpu_mhz_allowed': 3600, 'cstates_available': 'C1,C2,POLL',         |
|                        | 'stor_function': 'monitor'}                                             |
| clock_synchronization  | ntp                                                                     |
| config_applied         | 1d867f6f-6300-4e5f-9c60-8144502f5159                                    |
| config_status          | None                                                                    |
| config_target          | 1d867f6f-6300-4e5f-9c60-8144502f5159                                    |
| console                | ttyS0,115200                                                            |
| created_at             | 2024-06-28T17:00:45.976144+00:00                                        |
| device_image_update    | None                                                                    |
| hostname               | controller-0                                                            |
| hw_settle              | 0                                                                       |
| id                     | 1                                                                       |
| install_output         | text                                                                    |
| install_state          | None                                                                    |
| install_state_info     | None                                                                    |
| inv_state              | inventoried                                                             |
| invprovision           | provisioned                                                             |
| location               | {}                                                                      |
| max_cpu_mhz_allowed    | 3600                                                                    |
| max_cpu_mhz_configured | None                                                                    |
| mgmt_ip                | 2607:f160:10:80d2:ce:40a:0:1                                            |
| mgmt_mac               | f0:b2:b9:14:3a:b4                                                       |
| operational            | enabled                                                                 |
| personality            | controller                                                              |
| reboot_needed          | False                                                                   |
| reserved               | False                                                                   |
| rootfs_device          | /dev/disk/by-path/pci-0000:03:00.0-nvme-1                               |
| serialid               | None                                                                    |
| software_load          | 22.12                                                                   |
| subfunction_avail      | available                                                               |
| subfunction_oper       | enabled                                                                 |
| subfunctions           | controller,worker,lowlatency                                            |
| task                   |                                                                         |
| tboot                  |                                                                         |
| ttys_dcd               | False                                                                   |
| updated_at             | 2024-06-28T22:19:44.803708+00:00                                        |
| uptime                 | 17555                                                                   |
| uuid                   | f6909a48-850b-4b0b-baa7-8def07daca3a                                    |
| vim_progress_status    | services-enabled                                                        |
+------------------------+-------------------------------------------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ system host-show 1 | grep bm
| bm_ip                  | None                                                                    |
| bm_type                | none                                                                    |
| bm_username            | None                                                                    |
[XXXXXX@controller-0 ~(keystone_admin)]$ system host-sensor-list 1

[XXXXXX@controller-0 ~(keystone_admin)]$

```

## Sensor interface with WRCP has been removed, test has passed.
