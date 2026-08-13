# HPE ILO6 1.57 BIOS H11 v1.11
# HPE Sapphire Rapids E930t server
# 4/08/24 James Patchett - MTCE Lab VCPfe
# Platform Deploymnet MEAKV-239-241

## Controller rchltxfe-c000000-001
OAM:  2607:f160:0:3043:cd:290:0:10

## welktxsr-931883-rh-le093s6-001
## welktxsr-d931883-012
ILO:  2607:f160:10:8803:ce:40a:0:e001
OAM:  2607:f160:10:8803:ce:40a:0:f401


## welktxsr-d931883-012
## Subcloud status/info before we start

```log
====================================================================
         SYSTEM: welktxsr-d931833-012
====================================================================


Linux controller-0 5.10.0-6-rt-amd64 #1 SMP PREEMPT_RT StarlingX Debian 5.10.177-1.stx.73 (2023-11-25 x86_64
Last login: Wed Apr 10 12:49:13 2024 from 2607:f160:0:3042:cd:290:0:11
XXXXXX@controller-0:~$ source /etc/platform/openrc
[XXXXXX@controller-0 ~(keystone_admin)]$ system show
+------------------------+--------------------------------------+
| Property               | Value                                |
+------------------------+--------------------------------------+
| contact                | None                                 |
| created_at             | 2024-04-08T21:53:42.439427+00:00     |
| description            | None                                 |
| distributed_cloud_role | subcloud                             |
| https_enabled          | True                                 |
| latitude               | None                                 |
| location               | None                                 |
| longitude              | None                                 |
| name                   | welktxsr-d931833-012                 |
| region_name            | welktxsr-d931833-012                 |
| sdn_enabled            | False                                |
| security_feature       | spectre_meltdown_v1                  |
| service_project_name   | services                             |
| shared_services        | []                                   |
| software_version       | 22.12                                |
| system_mode            | simplex                              |
| system_type            | All-in-one                           |
| timezone               | UTC                                  |
| updated_at             | 2024-04-09T18:44:44.619951+00:00     |
| uuid                   | def895ea-6135-41bf-bcb4-885da1488448 |
| vswitch_type           | none                                 |
+------------------------+--------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ system oam-show
+----------------+---------------------------------------+
| Property       | Value                                 |
+----------------+---------------------------------------+
| created_at     | 2024-04-08T21:55:20.284984+00:00      |
| isystem_uuid   | def895ea-6135-41bf-bcb4-885da1488448  |
| oam_end_ip     | 2607:f160:10:8803:ffff:ffff:ffff:fffe |
| oam_gateway_ip | 2607:f160:10:8803:ce:23::             |
| oam_ip         | 2607:f160:10:8803:ce:40a:0:f401       |
| oam_start_ip   | 2607:f160:10:8803::1                  |
| oam_subnet     | 2607:f160:10:8803::/64                |
| updated_at     | None                                  |
| uuid           | fa1d8f52-115e-45e8-97df-492f8ef5fb5b  |
+----------------+---------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ system application-list
+--------------------------+----------+-------------------------------------------+------------------+---------+-----------+
| application              | version  | manifest name                             | manifest file    | status  | progress  |
+--------------------------+----------+-------------------------------------------+------------------+---------+-----------+
| cert-manager             | 22.12-8  | cert-manager-fluxcd-manifests             | fluxcd-manifests | applied | completed |
| metrics-server           | 22.12-1  | metrics-server-fluxcd-manifests           | fluxcd-manifests | applied | completed |
| nginx-ingress-controller | 22.12-1  | nginx-ingress-controller-fluxcd-manifests | fluxcd-manifests | applied | completed |
| oidc-auth-apps           | 22.12-6  | oidc-auth-apps-fluxcd-manifests           | fluxcd-manifests | applied | completed |
| platform-integ-apps      | 22.12-66 | platform-integ-apps-fluxcd-manifests      | fluxcd-manifests | applied | completed |
| wr-analytics             | 23.09-0  | wr-analytics-fluxcd-manifests             | fluxcd-manifests | applied | completed |
+--------------------------+----------+-------------------------------------------+------------------+---------+-----------+
[XXXXXX@controller-0 ~(keystone_admin)]$ sw-patch query
      Patch ID         RR  Release  Patch State
=====================  ==  =======  ===========
WRCP_22.12_PATCH_0001  Y    22.12    Committed
WRCP_22.12_PATCH_0002  Y    22.12    Committed
WRCP_22.12_PATCH_0003  Y    22.12    Committed
WRCP_22.12_PATCH_0004  Y    22.12    Committed

[XXXXXX@controller-0 ~(keystone_admin)]$ fm alarm-list

[XXXXXX@controller-0 ~(keystone_admin)]$
```

## MEAKV-239
## Subcloud welktxsr-d931883-012

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ system host-show 1 |grep bm
| bm_ip                  | None                                                                     |
| bm_type                | none                                                                     |
| bm_username            | None                                                                     |
[XXXXXX@controller-0 ~(keystone_admin)]$
[XXXXXX@controller-0 ~(keystone_admin)]$ system host-update controller-0 bm_ip=2607:f160:10:8803:ce:40a:0:e001 bm_type=redfish bm_username=XXXXXX bm_password=XXXXXX
+------------------------+--------------------------------------------------------------------------+
| Property               | Value                                                                    |
+------------------------+--------------------------------------------------------------------------+
| action                 | none                                                                     |
| administrative         | unlocked                                                                 |
| apparmor               | disabled                                                                 |
| availability           | available                                                                |
| bm_ip                  | 2607:f160:10:8803:ce:40a:0:e001                                          |
| bm_type                | redfish                                                                  |
| bm_username            | XXXXXX                                                                   |
| boot_device            | /dev/disk/by-path/pci-0000:03:00.0-nvme-1                                |
| capabilities           | {'is_max_cpu_configurable': 'configurable', 'min_cpu_mhz_allowed': None, |
|                        | 'max_cpu_mhz_allowed': None, 'cstates_available': 'C1,C1E,C6,POLL',      |
|                        | 'stor_function': 'monitor'}                                              |
| clock_synchronization  | ntp                                                                      |
| config_applied         | 34d27d6f-13f0-477d-8052-18dd3f1d528b                                     |
| config_status          | None                                                                     |
| config_target          | 34d27d6f-13f0-477d-8052-18dd3f1d528b                                     |
| console                | ttyS0,115200                                                             |
| created_at             | 2024-04-08T21:55:21.922294+00:00                                         |
| device_image_update    | None                                                                     |
| hostname               | controller-0                                                             |
| hw_settle              | 0                                                                        |
| id                     | 1                                                                        |
| install_output         | text                                                                     |
| install_state          | None                                                                     |
| install_state_info     | None                                                                     |
| inv_state              | inventoried                                                              |
| invprovision           | provisioned                                                              |
| location               | {}                                                                       |
| max_cpu_mhz_allowed    | None                                                                     |
| max_cpu_mhz_configured | None                                                                     |
| mgmt_ip                | 2607:f160:10:80d6:ce:40a:0:1                                             |
| mgmt_mac               | f0:b2:b9:14:3a:00                                                        |
| operational            | enabled                                                                  |
| personality            | controller                                                               |
| reboot_needed          | False                                                                    |
| reserved               | False                                                                    |
| rootfs_device          | /dev/disk/by-path/pci-0000:03:00.0-nvme-1                                |
| serialid               | None                                                                     |
| software_load          | 22.12                                                                    |
| subfunction_avail      | available                                                                |
| subfunction_oper       | enabled                                                                  |
| subfunctions           | controller,worker,lowlatency                                             |
| task                   |                                                                          |
| tboot                  |                                                                          |
| ttys_dcd               | False                                                                    |
| updated_at             | 2024-04-10T17:04:04.386229+00:00                                         |
| uptime                 | 80599                                                                    |
| uuid                   | 0a90afd5-43af-4808-b31f-aafe9df34ee2                                     |
| vim_progress_status    | services-enabled                                                         |
+------------------------+--------------------------------------------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$
[XXXXXX@controller-0 ~(keystone_admin)]$ system host-show 1
+------------------------+--------------------------------------------------------------------------+
| Property               | Value                                                                    |
+------------------------+--------------------------------------------------------------------------+
| action                 | none                                                                     |
| administrative         | unlocked                                                                 |
| apparmor               | disabled                                                                 |
| availability           | available                                                                |
| bm_ip                  | 2607:f160:10:8803:ce:40a:0:e001                                          |
| bm_type                | redfish                                                                  |
| bm_username            | XXXXXX                                                                   |
| boot_device            | /dev/disk/by-path/pci-0000:03:00.0-nvme-1                                |
| capabilities           | {'is_max_cpu_configurable': 'configurable', 'min_cpu_mhz_allowed': None, |
|                        | 'max_cpu_mhz_allowed': None, 'cstates_available': 'C1,C1E,C6,POLL',      |
|                        | 'stor_function': 'monitor', 'Personality': 'Controller-Active'}          |
| clock_synchronization  | ntp                                                                      |
| config_applied         | 34d27d6f-13f0-477d-8052-18dd3f1d528b                                     |
| config_status          | None                                                                     |
| config_target          | 34d27d6f-13f0-477d-8052-18dd3f1d528b                                     |
| console                | ttyS0,115200                                                             |
| created_at             | 2024-04-08T21:55:21.922294+00:00                                         |
| device_image_update    | None                                                                     |
| hostname               | controller-0                                                             |
| hw_settle              | 0                                                                        |
| id                     | 1                                                                        |
| install_output         | text                                                                     |
| install_state          | None                                                                     |
| install_state_info     | None                                                                     |
| inv_state              | inventoried                                                              |
| invprovision           | provisioned                                                              |
| location               | {}                                                                       |
| max_cpu_mhz_allowed    | None                                                                     |
| max_cpu_mhz_configured | None                                                                     |
| mgmt_ip                | 2607:f160:10:80d6:ce:40a:0:1                                             |
| mgmt_mac               | f0:b2:b9:14:3a:00                                                        |
| operational            | enabled                                                                  |
| personality            | controller                                                               |
| reboot_needed          | False                                                                    |
| reserved               | False                                                                    |
| rootfs_device          | /dev/disk/by-path/pci-0000:03:00.0-nvme-1                                |
| serialid               | None                                                                     |
| software_load          | 22.12                                                                    |
| subfunction_avail      | available                                                                |
| subfunction_oper       | enabled                                                                  |
| subfunctions           | controller,worker,lowlatency                                             |
| task                   |                                                                          |
| tboot                  |                                                                          |
| ttys_dcd               | False                                                                    |
| updated_at             | 2024-04-10T17:36:12.388816+00:00                                         |
| uptime                 | 82524                                                                    |
| uuid                   | 0a90afd5-43af-4808-b31f-aafe9df34ee2                                     |
| vim_progress_status    | services-enabled                                                         |
+------------------------+--------------------------------------------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ system host-show 1|grep bm
| bm_ip                  | 2607:f160:10:8803:ce:40a:0:e001                                          |
| bm_type                | redfish                                                                  |
| bm_username            | XXXXXX                                                                   |
[XXXXXX@controller-0 ~(keystone_admin)]$
```

## Success


## MEAKV-240

```log

[XXXXXX@controller-0 ~(keystone_admin)]$ system host-show 1 | grep bm
system host-sensor-list 1
| bm_ip                  | 2607:f160:10:8803:ce:40a:0:e001                                          |
| bm_type                | redfish                                                                  |
| bm_username            | XXXXXX                                                                   |
+--------------------------------------+---------------------------+-------------+---------+---------+
| uuid                                 | name                      | sensortype  | state   | status  |
+--------------------------------------+---------------------------+-------------+---------+---------+
| fcefabad-049f-4ff6-be5b-c498f8e03bb9 | 01-Inlet Ambient          | temperature | enabled | ok      |
| bc2e4cf2-488a-4aa7-ad7c-0cb4857cd628 | 02-CPU 1 PkgTmp           | temperature | enabled | ok      |
| a4173096-9cb1-465b-a53d-435647a5e143 | 03-P1 DIMM 1-6            | temperature | enabled | ok      |
| e9cc9ee7-4b66-441d-8626-a31b912a7841 | 04-P1 PMM 1-6             | temperature | enabled | offline |
| 5fdefa68-b5e6-4519-b8b8-b5dc6f7161a1 | 05-P1 DIMM 7-12           | temperature | enabled | ok      |
| c31d6bad-233f-48b6-bb85-f3de6621ff50 | 06-P1 PMM 7-12            | temperature | enabled | offline |
| d7b50336-4c97-41ed-9d46-77b50ff1ddd6 | 07-VR P1                  | temperature | enabled | ok      |
| 906c781c-2ada-4eb4-8def-7a4163addd6d | 08-Chipset                | temperature | enabled | ok      |
| 770656d5-fd48-436c-89c5-6c3eb0c22302 | 09-BMC                    | temperature | enabled | ok      |
| 45cea5c2-f0ca-4b7b-a482-4351ea0df000 | 10-M2                     | temperature | enabled | ok      |
| d59e6478-3189-4013-85c9-c06552cc8513 | 15.1-PCI 1-Network        | temperature | enabled | ok      |
|                                      | controller                |             |         |         |
|                                      |                           |             |         |         |
| b94c4de7-b3f3-428d-967e-e9bb0e0bfa08 | 15.2-PCI 1-SFP28          | temperature | enabled | ok      |
|                                      | (SFF-8402)                |             |         |         |
|                                      |                           |             |         |         |
| ee51790a-4c0d-4e48-ae34-6821104a7e23 | 16-PCI 1 Zone             | temperature | enabled | ok      |
| 669d8e0a-8579-4b88-bef0-f807809bf259 | 17.1-PCI 2-Network        | temperature | enabled | ok      |
|                                      | controller                |             |         |         |
|                                      |                           |             |         |         |
| a11a8e57-560c-453f-8f0f-51eeeb6194a7 | 18-PCI 2 Zone             | temperature | enabled | ok      |
| 5b91b317-530d-4416-aebd-e972365009e5 | 19.1-PCI 3-Network        | temperature | enabled | ok      |
|                                      | controller                |             |         |         |
|                                      |                           |             |         |         |
| 565611f9-addb-4135-b142-05c235d141b7 | 19.2-PCI 3-SFP28          | temperature | enabled | ok      |
|                                      | (SFF-8402)                |             |         |         |
|                                      |                           |             |         |         |
| c7e8f9aa-dbc1-48d4-a6e3-189d4dedb01d | 20-PCI 3 Zone             | temperature | enabled | ok      |
| 433aa7cb-7723-44c8-af01-bf9bee8422db | 21-PCI 4                  | temperature | enabled | offline |
| 81e08b4d-34a7-4a22-9b4b-795afaa2c602 | 22-PCI 4 Zone             | temperature | enabled | offline |
| 20a32828-c394-4f87-a064-adebf486497d | 27-Sys Exhaust 1          | temperature | enabled | ok      |
| 11bd3a75-4e1f-4f89-9fbb-3bdc4d68d4ab | Fan 1                     | fan         | enabled | ok      |
| fa4a1ea4-68e8-4a11-acdb-98b8d12a428e | Fan 2                     | fan         | enabled | ok      |
| d7d4e6d9-d31b-4d70-93fa-5623bf59a879 | Fan 3                     | fan         | enabled | ok      |
| b3aa3cab-d2f7-4302-a93c-fa196076db7e | Fan 4                     | fan         | enabled | ok      |
| 77317b31-6541-4e5c-bbb7-168280f64d5b | Fan 5                     | fan         | enabled | ok      |
| 712c23a1-3a36-44d6-87bc-89170988f218 | Fan 6                     | fan         | enabled | ok      |
| 47dc2f1a-d450-4f70-8dbc-de9e3144ccb3 | HpeServerPowerSupply      | power       | enabled | ok      |
+--------------------------------------+---------------------------+-------------+---------+---------+
[XXXXXX@controller-0 ~(keystone_admin)]$


```

## I see some temp sensors are offline, lets validate at the redfish commands to verify

```log
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ IP=2607:f160:10:8803:ce:40a:0:e001
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ echo $IP
2607:f160:10:8803:ce:40a:0:e001
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ rf_sensor_list.py -u XXXXXX -p XXXXXX -r https://[$IP]
Chassis 'Computer System Chassis' Status
  Sensor                    | Reading    | Health   | LF       | LC       | LNC      | UNC      | UC       | UF       | PhysicalContext
  State                     | Enabled    | Warning  | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  HpeServerPowerSupply Stat | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  HpeServerPowerSupply Line | 213V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  HpeServerPowerSupply Powe | 1500W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  HpeServerPowerSupply Last | 175W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  HpeServerPowerSupply Stat | Unavailabl | Critical | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  HpeServerPowerSupply Line | 0V         | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  HpeServerPowerSupply Powe | 1500W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  HpeServerPowerSupply Last | 0W         | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  01-Inlet Ambient          | 34Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 62       | 66       | Intake
  02-CPU 1 PkgTmp           | 82Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 91       | N/A      | CPU
  03-P1 DIMM 1-6            | 50Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 90       | N/A      | Memory
  04-P1 PMM 1-6             | 0Cel       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Memory
  05-P1 DIMM 7-12           | 57Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 90       | N/A      | Memory
  06-P1 PMM 7-12            | 0Cel       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Memory
  07-VR P1                  | 73Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | N/A      | SystemBoard
  08-Chipset                | 46Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 100      | N/A      | SystemBoard
  09-BMC                    | 56Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | N/A      | SystemBoard
  10-M2                     | 45Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 80       | N/A      | SystemBoard
  16-PCI 1 Zone             | 31Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 70       | 75       | SystemBoard
  18-PCI 2 Zone             | 31Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 70       | 75       | SystemBoard
  20-PCI 3 Zone             | 31Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 70       | 75       | SystemBoard
  21-PCI 4                  | 0Cel       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard
  22-PCI 4 Zone             | 0Cel       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard
  27-Sys Exhaust 1          | 62Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 85       | N/A      | SystemBoard
  15.1-PCI 1-Network contro | 61Cel      | OK       | N/A      | N/A      | N/A      | 95       | 105      | 115      | SystemBoard
  15.2-PCI 1-SFP28 (SFF-840 | 32Cel      | OK       | N/A      | N/A      | N/A      | 70       | 75       | N/A      | SystemBoard
  17.1-PCI 2-Network contro | 63Cel      | OK       | N/A      | N/A      | N/A      | 95       | 105      | 115      | SystemBoard
  19.1-PCI 3-Network contro | 57Cel      | OK       | N/A      | N/A      | N/A      | 95       | 105      | 115      | SystemBoard
  19.2-PCI 3-SFP28 (SFF-840 | 32Cel      | OK       | N/A      | N/A      | N/A      | 70       | 75       | N/A      | SystemBoard
  Fan 1                     | 24%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard
  Fan 2                     | 24%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard
  Fan 3                     | 24%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard
  Fan 4                     | 24%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard
  Fan 5                     | 24%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard
  Fan 6                     | 24%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard

Chassis 'HPE EL8000t     ' Status
  Sensor                    | Reading    | Health   | LF       | LC       | LNC      | UNC      | UC       | UF       | PhysicalContext

[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$

```
## PCI-SLOT4 is empty, explains PCI missing temp sensors as well as Proc1 Dimm2, Dimm5, Dimm8 and Dimm11 are empty slots, explaining the missing sensor data.


## Passed MEAKV-240
## Screenshots of ILO6 WEB GUI showing missing devices to be uploaded with test case


### MEAKV-241

```log

[XXXXXX@controller-0 ~(keystone_admin)]$ system host-show 1 | grep bm
| bm_ip                  | 2607:f160:10:8803:ce:40a:0:e001                                          |
| bm_type                | redfish                                                                  |
| bm_username            | XXXXXX                                                                   |
[XXXXXX@controller-0 ~(keystone_admin)]$ system host-update controller-0 bm_type=none
+------------------------+--------------------------------------------------------------------------+
| Property               | Value                                                                    |
+------------------------+--------------------------------------------------------------------------+
| action                 | none                                                                     |
| administrative         | unlocked                                                                 |
| apparmor               | disabled                                                                 |
| availability           | available                                                                |
| bm_ip                  | None                                                                     |
| bm_type                | none                                                                     |
| bm_username            | None                                                                     |
| boot_device            | /dev/disk/by-path/pci-0000:03:00.0-nvme-1                                |
| capabilities           | {'is_max_cpu_configurable': 'configurable', 'min_cpu_mhz_allowed': None, |
|                        | 'max_cpu_mhz_allowed': None, 'cstates_available': 'C1,C1E,C6,POLL',      |
|                        | 'stor_function': 'monitor'}                                              |
| clock_synchronization  | ntp                                                                      |
| config_applied         | 34d27d6f-13f0-477d-8052-18dd3f1d528b                                     |
| config_status          | None                                                                     |
| config_target          | 34d27d6f-13f0-477d-8052-18dd3f1d528b                                     |
| console                | ttyS0,115200                                                             |
| created_at             | 2024-04-08T21:55:21.922294+00:00                                         |
| device_image_update    | None                                                                     |
| hostname               | controller-0                                                             |
| hw_settle              | 0                                                                        |
| id                     | 1                                                                        |
| install_output         | text                                                                     |
| install_state          | None                                                                     |
| install_state_info     | None                                                                     |
| inv_state              | inventoried                                                              |
| invprovision           | provisioned                                                              |
| location               | {}                                                                       |
| max_cpu_mhz_allowed    | None                                                                     |
| max_cpu_mhz_configured | None                                                                     |
| mgmt_ip                | 2607:f160:10:80d6:ce:40a:0:1                                             |
| mgmt_mac               | f0:b2:b9:14:3a:00                                                        |
| operational            | enabled                                                                  |
| personality            | controller                                                               |
| reboot_needed          | False                                                                    |
| reserved               | False                                                                    |
| rootfs_device          | /dev/disk/by-path/pci-0000:03:00.0-nvme-1                                |
| serialid               | None                                                                     |
| software_load          | 22.12                                                                    |
| subfunction_avail      | available                                                                |
| subfunction_oper       | enabled                                                                  |
| subfunctions           | controller,worker,lowlatency                                             |
| task                   |                                                                          |
| tboot                  |                                                                          |
| ttys_dcd               | False                                                                    |
| updated_at             | 2024-04-10T17:55:37.398229+00:00                                         |
| uptime                 | 83689                                                                    |
| uuid                   | 0a90afd5-43af-4808-b31f-aafe9df34ee2                                     |
| vim_progress_status    | services-enabled                                                         |
+------------------------+--------------------------------------------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ system host-show 1 | grep bm
| bm_ip                  | None                                                                     |
| bm_type                | none                                                                     |
| bm_username            | None                                                                     |
[XXXXXX@controller-0 ~(keystone_admin)]$
[XXXXXX@controller-0 ~(keystone_admin)]$ system host-sensor-list 1

[XXXXXX@controller-0 ~(keystone_admin)]$

```

## Sensor interface with WRCP has been removed, test has passed.
