# HPE ILO5 3.06 BIOS H08 v2.12
# HPE E910t server
# 8/28/24 James Patchett - MTCE Lab VCPfe
# Platform Deploymnet MEAKV-239-241

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

## MEAKV-239
## Subcloud welktxsr-d931883-012

```log
XXXXXX@controller-0:~$ source /etc/platform/openrc
[XXXXXX@controller-0 ~(keystone_admin)]$  system host-show 1 |grep bm
| bm_ip                  | None                                                                     |
| bm_type                | none                                                                     |
| bm_username            | None                                                                     |
[XXXXXX@controller-0 ~(keystone_admin)]$ system host-update controller-0 bm_ip=2607:f160:10:922a:ce:406:0:1000 bm_type=redfish bm_username=XXXXXX bm_password=XXXXXX
+------------------------+--------------------------------------------------------------------------+
| Property               | Value                                                                    |
+------------------------+--------------------------------------------------------------------------+
| action                 | none                                                                     |
| administrative         | unlocked                                                                 |
| apparmor               | disabled                                                                 |
| availability           | degraded                                                                 |
| bm_ip                  | 2607:f160:10:922a:ce:406:0:1000                                          |
| bm_type                | redfish                                                                  |
| bm_username            | XXXXXX                                                                   |
| boot_device            | /dev/disk/by-path/pci-0000:12:00.0-nvme-1                                |
| capabilities           | {'is_max_cpu_configurable': 'configurable', 'min_cpu_mhz_allowed': None, |
|                        | 'max_cpu_mhz_allowed': None, 'cstates_available': 'C1,C2,POLL',          |
|                        | 'stor_function': 'monitor'}                                              |
| clock_synchronization  | ptp                                                                      |
| config_applied         | 4a19c78f-9e44-416c-a311-96254306d83a                                     |
| config_status          | Config out-of-date                                                       |
| config_target          | 785dac29-b30f-433c-99b8-0791c5ecb4b0                                     |
| console                | ttyS0,115200                                                             |
| created_at             | 2024-07-03T16:13:22.992684+00:00                                         |
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
| max_cpu_mhz_configured | 2340                                                                     |
| mgmt_ip                | 2607:f160:10:9232:ce:40a:0:1                                             |
| mgmt_mac               | d4:f5:ef:55:13:98                                                        |
| operational            | enabled                                                                  |
| personality            | controller                                                               |
| reboot_needed          | False                                                                    |
| reserved               | False                                                                    |
| rootfs_device          | /dev/disk/by-path/pci-0000:12:00.0-nvme-1                                |
| serialid               | None                                                                     |
| software_load          | 22.12                                                                    |
| subfunction_avail      | failed                                                                   |
| subfunction_oper       | disabled                                                                 |
| subfunctions           | controller,worker,lowlatency                                             |
| task                   | Configuration failure, threshold reached, Lock/Unlock to retry           |
| tboot                  |                                                                          |
| ttys_dcd               | False                                                                    |
| updated_at             | 2024-08-28T20:12:40.664718+00:00                                         |
| uptime                 | 852                                                                      |
| uuid                   | 6a0d7b8b-3a64-4f7b-923a-2b19ac35f56a                                     |
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
| availability           | degraded                                                                 |
| bm_ip                  | 2607:f160:10:922a:ce:406:0:1000                                          |
| bm_type                | redfish                                                                  |
| bm_username            | XXXXXX                                                                   |
| boot_device            | /dev/disk/by-path/pci-0000:12:00.0-nvme-1                                |
| capabilities           | {'is_max_cpu_configurable': 'configurable', 'min_cpu_mhz_allowed': None, |
|                        | 'max_cpu_mhz_allowed': None, 'cstates_available': 'C1,C2,POLL',          |
|                        | 'stor_function': 'monitor', 'Personality': 'Controller-Active'}          |
| clock_synchronization  | ptp                                                                      |
| config_applied         | 4a19c78f-9e44-416c-a311-96254306d83a                                     |
| config_status          | Config out-of-date                                                       |
| config_target          | 785dac29-b30f-433c-99b8-0791c5ecb4b0                                     |
| console                | ttyS0,115200                                                             |
| created_at             | 2024-07-03T16:13:22.992684+00:00                                         |
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
| max_cpu_mhz_configured | 2340                                                                     |
| mgmt_ip                | 2607:f160:10:9232:ce:40a:0:1                                             |
| mgmt_mac               | d4:f5:ef:55:13:98                                                        |
| operational            | enabled                                                                  |
| personality            | controller                                                               |
| reboot_needed          | False                                                                    |
| reserved               | False                                                                    |
| rootfs_device          | /dev/disk/by-path/pci-0000:12:00.0-nvme-1                                |
| serialid               | None                                                                     |
| software_load          | 22.12                                                                    |
| subfunction_avail      | failed                                                                   |
| subfunction_oper       | disabled                                                                 |
| subfunctions           | controller,worker,lowlatency                                             |
| task                   | Configuration failure, threshold reached, Lock/Unlock to retry           |
| tboot                  |                                                                          |
| ttys_dcd               | False                                                                    |
| updated_at             | 2024-08-28T20:13:15.230904+00:00                                         |
| uptime                 | 852                                                                      |
| uuid                   | 6a0d7b8b-3a64-4f7b-923a-2b19ac35f56a                                     |
| vim_progress_status    | services-enabled                                                         |
+------------------------+--------------------------------------------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ system host-show 1|grep bm
| bm_ip                  | 2607:f160:10:922a:ce:406:0:1000                                          |
| bm_type                | redfish                                                                  |
| bm_username            | XXXXXX                                                                   |
[XXXXXX@controller-0 ~(keystone_admin)]$
```

## Success


## MEAKV-240

```log

[[XXXXXX@controller-0 ~(keystone_admin)]$ system host-show 1 | grep bm
| bm_ip                  | 2607:f160:10:922a:ce:406:0:1000                                          |
| bm_type                | redfish                                                                  |
| bm_username            | XXXXXX                                                                   |
[XXXXXX@controller-0 ~(keystone_admin)]$ system host-sensor-list 1
+--------------------------------------+----------------------+-------------+----------+---------+
| uuid                                 | name                 | sensortype  | state    | status  |
+--------------------------------------+----------------------+-------------+----------+---------+
| a1a4694e-924e-426f-bc0e-879b75591278 | 01-Inlet Ambient     | temperature | enabled  | offline |
| 4dcf5725-7f15-4c89-9a6f-d344f554f00f | 02-CPU               | temperature | enabled  | offline |
| 9cacc195-f319-48bb-8f90-59f1826d45fb | 03-P DIMM 1-6        | temperature | enabled  | offline |
| c4303903-6588-40b1-81f8-004750655b38 | 04-P PMM 1-6         | temperature | enabled  | offline |
| 3349290a-064c-402c-954f-4805328450e1 | 05-P DIMM 7-12       | temperature | enabled  | offline |
| 17c3370a-14fc-4b20-b6ec-194488a9a3b7 | 06-P PMM 7-12        | temperature | enabled  | offline |
| 9cb58930-6c67-42cc-b8a1-80438022e898 | 07-mLOM              | temperature | enabled  | offline |
| 85b68e0c-7449-4504-a3cc-5133ce873ced | 08-mLOM Zone         | temperature | enabled  | offline |
| ca21fe27-ffa6-483f-96ab-3066236e386d | 09-BMC               | temperature | enabled  | offline |
| 26110f41-8c82-47a5-8129-f151793e8358 | 10-BMC Zone          | temperature | enabled  | offline |
| 2fe74756-ee21-497b-9cd2-44b46ac15de8 | 11-M2                | temperature | enabled  | offline |
| 6677a931-4046-4333-94ce-1b0a90922b33 | 12-M2 Zone           | temperature | enabled  | offline |
| 4f57e02e-817c-44af-a727-a9f3a489956d | 13-Chipset           | temperature | enabled  | offline |
| a33fa71f-154e-41a6-b23b-86fe6062be13 | 14-Battery Zone      | temperature | enabled  | offline |
| ed638d5a-5332-40ef-ba4c-5eb831351a5e | 15-VR P Mem 1        | temperature | enabled  | offline |
| 8f7dab5b-2969-41dc-b35b-775e676029e0 | 16-VR P Mem 2        | temperature | enabled  | offline |
| a3f25ab6-ef90-43fa-9f39-fdb996d69d79 | 17-VR P              | temperature | enabled  | offline |
| 31cd8ca0-41e8-46dc-9a58-df7aa2786e51 | 18-PCI 1 M2          | temperature | enabled  | offline |
| 29185b0b-da1c-4d11-8771-212003a71426 | 19-PCI 1 M2 Zn       | temperature | enabled  | offline |
| 3be8651c-490b-4a73-b291-d5158a70510c | 20-PCI 2 M2          | temperature | enabled  | offline |
| b4a96a2d-2724-4c13-993d-b2b2ce179f58 | 21-PCI 2 M2 Zn       | temperature | enabled  | offline |
| bc00253a-1ba2-4f05-8651-07c91760c08c | 22-PCI 3 M2          | temperature | enabled  | offline |
| 0a70d7f0-cc03-4e19-abf4-cb2cde863171 | 23-PCI 3 M2 Zn       | temperature | enabled  | offline |
| 48e7a7c4-d693-4e08-8271-456366eed235 | 24-PCI 4 M2          | temperature | enabled  | offline |
| 0b56de79-1208-4281-9f7e-d6ba6538e29a | 26.1-PCI 1 GPU-Board | temperature | enabled  | offline |
|                                      | Temp                 |             |          |         |
|                                      |                      |             |          |         |
| f8e83829-b924-4100-98ac-0cc6ba2d5b2f | 26.2-PCI 1 GPU-FPGA  | temperature | enabled  | offline |
|                                      | Core Temp            |             |          |         |
|                                      |                      |             |          |         |
| ec0e723e-dd96-45bb-94ae-8a4a0f8ad901 | 27-PCI 1 Zone        | temperature | enabled  | offline |
| 1c263411-9683-4771-a234-bb7fef26f579 | 28-PCI 2             | temperature | enabled  | offline |
| 816e5c43-af1c-47e3-b338-63ce9eb1b88f | 30.1-PCI 3-Network   | temperature | enabled  | offline |
|                                      | controller           |             |          |         |
|                                      |                      |             |          |         |
| c87b83e3-756d-4733-8a59-c30c5d21042f | 30.2-PCI 3-Network   | temperature | enabled  | offline |
|                                      | controller           |             |          |         |
|                                      |                      |             |          |         |
| 8363c276-f04f-4b75-b745-f9375503901d | 31-PCI 3 Zone        | temperature | enabled  | offline |
| 4641a6b5-19e5-40cd-97ec-e5300e41e804 | 32-PCI 4             | temperature | enabled  | offline |
| 301d92e4-6bf7-4d0b-804d-42ef23ff3ec7 | 36-Sys Exhaust 1     | temperature | enabled  | offline |
| 9e48a215-f9d8-4b9f-ac59-fa91de89a256 | 37-E-Fuse 1          | temperature | enabled  | offline |
| 824ebe0e-bbfc-4910-b9be-25331d391ed5 | 38-E-Fuse 2          | temperature | enabled  | offline |
| 0923dbf7-8d13-43b4-9336-a528ac5b406b | 39-E-Fuse 3          | temperature | enabled  | offline |
| db1f3a99-31e4-4b39-bb4f-853341c2dc35 | 45-PCI 5             | temperature | enabled  | offline |
| 0fac320f-f8e5-47e9-9980-e8aca047f54c | 47-Stor Batt         | temperature | enabled  | offline |
| f15f035d-3d16-41cf-a6e3-2d9e5cb694a8 | 48-PCI 5 Zone        | temperature | enabled  | offline |
| 07fb8039-ed01-4e81-8f73-029bac0b3dc6 | 49-Front Ambient     | temperature | enabled  | offline |
| 24021e4c-bcc9-4d81-bfbd-7c573b6092c0 | 51-CPU 1 PkgTmp      | temperature | enabled  | offline |
| f5fa0435-e970-4931-9129-2b85c170faac | Fan 1                | fan         | enabled  | offline |
| 094d1c2b-8da8-4eae-bdd1-3f57737e8d61 | Fan 2                | fan         | enabled  | offline |
| 0151cb62-2727-4192-8269-a3b9525b813b | Fan 3                | fan         | enabled  | offline |
| 2d6468af-61bf-463f-8193-d2d288bd2a95 | Fan 4                | fan         | enabled  | offline |
| 84245f14-b514-4c24-8dba-979c09058625 | Fan 5                | fan         | disabled | offline |
| 54ce3c1d-f4fd-4909-80fa-f221db5cfa96 | Fan 6                | fan         | disabled | offline |
| 06a57796-190e-471e-a323-5f95247372e8 | HpeServerPowerSupply | power       | enabled  | offline |
+--------------------------------------+----------------------+-------------+----------+---------+
[XXXXXX@controller-0 ~(keystone_admin)]$ system host-sensor-list 1
+--------------------------------------+-----------------------------+-------------+---------+---------+
| uuid                                 | name                        | sensortype  | state   | status  |
+--------------------------------------+-----------------------------+-------------+---------+---------+
| a1a4694e-924e-426f-bc0e-879b75591278 | 01-Inlet Ambient            | temperature | enabled | ok      |
| 4dcf5725-7f15-4c89-9a6f-d344f554f00f | 02-CPU                      | temperature | enabled | ok      |
| 9cacc195-f319-48bb-8f90-59f1826d45fb | 03-P DIMM 1-6               | temperature | enabled | ok      |
| c4303903-6588-40b1-81f8-004750655b38 | 04-P PMM 1-6                | temperature | enabled | offline |
| 3349290a-064c-402c-954f-4805328450e1 | 05-P DIMM 7-12              | temperature | enabled | ok      |
| 17c3370a-14fc-4b20-b6ec-194488a9a3b7 | 06-P PMM 7-12               | temperature | enabled | offline |
| 9cb58930-6c67-42cc-b8a1-80438022e898 | 07-mLOM                     | temperature | enabled | offline |
| 85b68e0c-7449-4504-a3cc-5133ce873ced | 08-mLOM Zone                | temperature | enabled | ok      |
| ca21fe27-ffa6-483f-96ab-3066236e386d | 09-BMC                      | temperature | enabled | ok      |
| 26110f41-8c82-47a5-8129-f151793e8358 | 10-BMC Zone                 | temperature | enabled | ok      |
| 2fe74756-ee21-497b-9cd2-44b46ac15de8 | 11-M2                       | temperature | enabled | offline |
| 6677a931-4046-4333-94ce-1b0a90922b33 | 12-M2 Zone                  | temperature | enabled | ok      |
| 4f57e02e-817c-44af-a727-a9f3a489956d | 13-Chipset                  | temperature | enabled | ok      |
| a33fa71f-154e-41a6-b23b-86fe6062be13 | 14-Battery Zone             | temperature | enabled | ok      |
| ed638d5a-5332-40ef-ba4c-5eb831351a5e | 15-VR P Mem 1               | temperature | enabled | ok      |
| 8f7dab5b-2969-41dc-b35b-775e676029e0 | 16-VR P Mem 2               | temperature | enabled | ok      |
| a3f25ab6-ef90-43fa-9f39-fdb996d69d79 | 17-VR P                     | temperature | enabled | ok      |
| 31cd8ca0-41e8-46dc-9a58-df7aa2786e51 | 18-PCI 1 M2                 | temperature | enabled | offline |
| 29185b0b-da1c-4d11-8771-212003a71426 | 19-PCI 1 M2 Zn              | temperature | enabled | ok      |
| 3be8651c-490b-4a73-b291-d5158a70510c | 20-PCI 2 M2                 | temperature | enabled | offline |
| b4a96a2d-2724-4c13-993d-b2b2ce179f58 | 21-PCI 2 M2 Zn              | temperature | enabled | ok      |
| bc00253a-1ba2-4f05-8651-07c91760c08c | 22-PCI 3 M2                 | temperature | enabled | offline |
| 0a70d7f0-cc03-4e19-abf4-cb2cde863171 | 23-PCI 3 M2 Zn              | temperature | enabled | ok      |
| 48e7a7c4-d693-4e08-8271-456366eed235 | 24-PCI 4 M2                 | temperature | enabled | offline |
| 0b56de79-1208-4281-9f7e-d6ba6538e29a | 26.1-PCI 1 GPU-Board Temp   | temperature | enabled | ok      |
| f8e83829-b924-4100-98ac-0cc6ba2d5b2f | 26.2-PCI 1 GPU-FPGA Core    | temperature | enabled | ok      |
|                                      | Temp                        |             |         |         |
|                                      |                             |             |         |         |
| ec0e723e-dd96-45bb-94ae-8a4a0f8ad901 | 27-PCI 1 Zone               | temperature | enabled | ok      |
| 1c263411-9683-4771-a234-bb7fef26f579 | 28-PCI 2                    | temperature | enabled | offline |
| 816e5c43-af1c-47e3-b338-63ce9eb1b88f | 30.1-PCI 3-Network          | temperature | enabled | ok      |
|                                      | controller                  |             |         |         |
|                                      |                             |             |         |         |
| c87b83e3-756d-4733-8a59-c30c5d21042f | 30.2-PCI 3-Network          | temperature | enabled | ok      |
|                                      | controller                  |             |         |         |
|                                      |                             |             |         |         |
| 8363c276-f04f-4b75-b745-f9375503901d | 31-PCI 3 Zone               | temperature | enabled | ok      |
| 4641a6b5-19e5-40cd-97ec-e5300e41e804 | 32-PCI 4                    | temperature | enabled | offline |
| 301d92e4-6bf7-4d0b-804d-42ef23ff3ec7 | 36-Sys Exhaust 1            | temperature | enabled | ok      |
| 9e48a215-f9d8-4b9f-ac59-fa91de89a256 | 37-E-Fuse 1                 | temperature | enabled | ok      |
| 824ebe0e-bbfc-4910-b9be-25331d391ed5 | 38-E-Fuse 2                 | temperature | enabled | ok      |
| 0923dbf7-8d13-43b4-9336-a528ac5b406b | 39-E-Fuse 3                 | temperature | enabled | ok      |
| db1f3a99-31e4-4b39-bb4f-853341c2dc35 | 45-PCI 5                    | temperature | enabled | offline |
| 0fac320f-f8e5-47e9-9980-e8aca047f54c | 47-Stor Batt                | temperature | enabled | offline |
| f15f035d-3d16-41cf-a6e3-2d9e5cb694a8 | 48-PCI 5 Zone               | temperature | enabled | offline |
| 07fb8039-ed01-4e81-8f73-029bac0b3dc6 | 49-Front Ambient            | temperature | enabled | offline |
| 24021e4c-bcc9-4d81-bfbd-7c573b6092c0 | 51-CPU 1 PkgTmp             | temperature | enabled | ok      |
| f5fa0435-e970-4931-9129-2b85c170faac | Fan 1                       | fan         | enabled | ok      |
| 094d1c2b-8da8-4eae-bdd1-3f57737e8d61 | Fan 2                       | fan         | enabled | ok      |
| 0151cb62-2727-4192-8269-a3b9525b813b | Fan 3                       | fan         | enabled | ok      |
| 2d6468af-61bf-463f-8193-d2d288bd2a95 | Fan 4                       | fan         | enabled | ok      |
| 84245f14-b514-4c24-8dba-979c09058625 | Fan 5                       | fan         | enabled | ok      |
| 54ce3c1d-f4fd-4909-80fa-f221db5cfa96 | Fan 6                       | fan         | enabled | ok      |
| 06a57796-190e-471e-a323-5f95247372e8 | HpeServerPowerSupply        | power       | enabled | ok      |
+--------------------------------------+-----------------------------+-------------+---------+---------+
[XXXXXX@controller-0 ~(keystone_admin)]$
[XXXXXX@controller-0 ~(keystone_admin)]$ system host-sensor-list 1
+--------------------------------------+-----------------------------+-------------+---------+---------+
| uuid                                 | name                        | sensortype  | state   | status  |
+--------------------------------------+-----------------------------+-------------+---------+---------+
| a1a4694e-924e-426f-bc0e-879b75591278 | 01-Inlet Ambient            | temperature | enabled | ok      |
| 4dcf5725-7f15-4c89-9a6f-d344f554f00f | 02-CPU                      | temperature | enabled | ok      |
| 9cacc195-f319-48bb-8f90-59f1826d45fb | 03-P DIMM 1-6               | temperature | enabled | ok      |
| c4303903-6588-40b1-81f8-004750655b38 | 04-P PMM 1-6                | temperature | enabled | offline |
| 3349290a-064c-402c-954f-4805328450e1 | 05-P DIMM 7-12              | temperature | enabled | ok      |
| 17c3370a-14fc-4b20-b6ec-194488a9a3b7 | 06-P PMM 7-12               | temperature | enabled | offline |
| 9cb58930-6c67-42cc-b8a1-80438022e898 | 07-mLOM                     | temperature | enabled | offline |
| 85b68e0c-7449-4504-a3cc-5133ce873ced | 08-mLOM Zone                | temperature | enabled | ok      |
| ca21fe27-ffa6-483f-96ab-3066236e386d | 09-BMC                      | temperature | enabled | ok      |
| 26110f41-8c82-47a5-8129-f151793e8358 | 10-BMC Zone                 | temperature | enabled | ok      |
| 2fe74756-ee21-497b-9cd2-44b46ac15de8 | 11-M2                       | temperature | enabled | offline |
| 6677a931-4046-4333-94ce-1b0a90922b33 | 12-M2 Zone                  | temperature | enabled | ok      |
| 4f57e02e-817c-44af-a727-a9f3a489956d | 13-Chipset                  | temperature | enabled | ok      |
| a33fa71f-154e-41a6-b23b-86fe6062be13 | 14-Battery Zone             | temperature | enabled | ok      |
| ed638d5a-5332-40ef-ba4c-5eb831351a5e | 15-VR P Mem 1               | temperature | enabled | ok      |
| 8f7dab5b-2969-41dc-b35b-775e676029e0 | 16-VR P Mem 2               | temperature | enabled | ok      |
| a3f25ab6-ef90-43fa-9f39-fdb996d69d79 | 17-VR P                     | temperature | enabled | ok      |
| 31cd8ca0-41e8-46dc-9a58-df7aa2786e51 | 18-PCI 1 M2                 | temperature | enabled | offline |
| 29185b0b-da1c-4d11-8771-212003a71426 | 19-PCI 1 M2 Zn              | temperature | enabled | ok      |
| 3be8651c-490b-4a73-b291-d5158a70510c | 20-PCI 2 M2                 | temperature | enabled | offline |
| b4a96a2d-2724-4c13-993d-b2b2ce179f58 | 21-PCI 2 M2 Zn              | temperature | enabled | ok      |
| bc00253a-1ba2-4f05-8651-07c91760c08c | 22-PCI 3 M2                 | temperature | enabled | offline |
| 0a70d7f0-cc03-4e19-abf4-cb2cde863171 | 23-PCI 3 M2 Zn              | temperature | enabled | ok      |
| 48e7a7c4-d693-4e08-8271-456366eed235 | 24-PCI 4 M2                 | temperature | enabled | offline |
| 0b56de79-1208-4281-9f7e-d6ba6538e29a | 26.1-PCI 1 GPU-Board Temp   | temperature | enabled | ok      |
| f8e83829-b924-4100-98ac-0cc6ba2d5b2f | 26.2-PCI 1 GPU-FPGA Core    | temperature | enabled | ok      |
|                                      | Temp                        |             |         |         |
|                                      |                             |             |         |         |
| ec0e723e-dd96-45bb-94ae-8a4a0f8ad901 | 27-PCI 1 Zone               | temperature | enabled | ok      |
| 1c263411-9683-4771-a234-bb7fef26f579 | 28-PCI 2                    | temperature | enabled | offline |
| 816e5c43-af1c-47e3-b338-63ce9eb1b88f | 30.1-PCI 3-Network          | temperature | enabled | ok      |
|                                      | controller                  |             |         |         |
|                                      |                             |             |         |         |
| c87b83e3-756d-4733-8a59-c30c5d21042f | 30.2-PCI 3-Network          | temperature | enabled | ok      |
|                                      | controller                  |             |         |         |
|                                      |                             |             |         |         |
| 8363c276-f04f-4b75-b745-f9375503901d | 31-PCI 3 Zone               | temperature | enabled | ok      |
| 4641a6b5-19e5-40cd-97ec-e5300e41e804 | 32-PCI 4                    | temperature | enabled | offline |
| 301d92e4-6bf7-4d0b-804d-42ef23ff3ec7 | 36-Sys Exhaust 1            | temperature | enabled | ok      |
| 9e48a215-f9d8-4b9f-ac59-fa91de89a256 | 37-E-Fuse 1                 | temperature | enabled | ok      |
| 824ebe0e-bbfc-4910-b9be-25331d391ed5 | 38-E-Fuse 2                 | temperature | enabled | ok      |
| 0923dbf7-8d13-43b4-9336-a528ac5b406b | 39-E-Fuse 3                 | temperature | enabled | ok      |
| db1f3a99-31e4-4b39-bb4f-853341c2dc35 | 45-PCI 5                    | temperature | enabled | offline |
| 0fac320f-f8e5-47e9-9980-e8aca047f54c | 47-Stor Batt                | temperature | enabled | offline |
| f15f035d-3d16-41cf-a6e3-2d9e5cb694a8 | 48-PCI 5 Zone               | temperature | enabled | offline |
| 07fb8039-ed01-4e81-8f73-029bac0b3dc6 | 49-Front Ambient            | temperature | enabled | offline |
| 24021e4c-bcc9-4d81-bfbd-7c573b6092c0 | 51-CPU 1 PkgTmp             | temperature | enabled | ok      |
| f5fa0435-e970-4931-9129-2b85c170faac | Fan 1                       | fan         | enabled | ok      |
| 094d1c2b-8da8-4eae-bdd1-3f57737e8d61 | Fan 2                       | fan         | enabled | ok      |
| 0151cb62-2727-4192-8269-a3b9525b813b | Fan 3                       | fan         | enabled | ok      |
| 2d6468af-61bf-463f-8193-d2d288bd2a95 | Fan 4                       | fan         | enabled | ok      |
| 84245f14-b514-4c24-8dba-979c09058625 | Fan 5                       | fan         | enabled | ok      |
| 54ce3c1d-f4fd-4909-80fa-f221db5cfa96 | Fan 6                       | fan         | enabled | ok      |
| 06a57796-190e-471e-a323-5f95247372e8 | HpeServerPowerSupply        | power       | enabled | ok      |
+--------------------------------------+-----------------------------+-------------+---------+---------+
[XXXXXX@controller-0 ~(keystone_admin)]$ sleep 180
[XXXXXX@controller-0 ~(keystone_admin)]$ system host-sensor-list 1
+--------------------------------------+-----------------------------+-------------+---------+---------+
| uuid                                 | name                        | sensortype  | state   | status  |
+--------------------------------------+-----------------------------+-------------+---------+---------+
| a1a4694e-924e-426f-bc0e-879b75591278 | 01-Inlet Ambient            | temperature | enabled | ok      |
| 4dcf5725-7f15-4c89-9a6f-d344f554f00f | 02-CPU                      | temperature | enabled | ok      |
| 9cacc195-f319-48bb-8f90-59f1826d45fb | 03-P DIMM 1-6               | temperature | enabled | ok      |
| c4303903-6588-40b1-81f8-004750655b38 | 04-P PMM 1-6                | temperature | enabled | offline |
| 3349290a-064c-402c-954f-4805328450e1 | 05-P DIMM 7-12              | temperature | enabled | ok      |
| 17c3370a-14fc-4b20-b6ec-194488a9a3b7 | 06-P PMM 7-12               | temperature | enabled | offline |
| 9cb58930-6c67-42cc-b8a1-80438022e898 | 07-mLOM                     | temperature | enabled | offline |
| 85b68e0c-7449-4504-a3cc-5133ce873ced | 08-mLOM Zone                | temperature | enabled | ok      |
| ca21fe27-ffa6-483f-96ab-3066236e386d | 09-BMC                      | temperature | enabled | ok      |
| 26110f41-8c82-47a5-8129-f151793e8358 | 10-BMC Zone                 | temperature | enabled | ok      |
| 2fe74756-ee21-497b-9cd2-44b46ac15de8 | 11-M2                       | temperature | enabled | offline |
| 6677a931-4046-4333-94ce-1b0a90922b33 | 12-M2 Zone                  | temperature | enabled | ok      |
| 4f57e02e-817c-44af-a727-a9f3a489956d | 13-Chipset                  | temperature | enabled | ok      |
| a33fa71f-154e-41a6-b23b-86fe6062be13 | 14-Battery Zone             | temperature | enabled | ok      |
| ed638d5a-5332-40ef-ba4c-5eb831351a5e | 15-VR P Mem 1               | temperature | enabled | ok      |
| 8f7dab5b-2969-41dc-b35b-775e676029e0 | 16-VR P Mem 2               | temperature | enabled | ok      |
| a3f25ab6-ef90-43fa-9f39-fdb996d69d79 | 17-VR P                     | temperature | enabled | ok      |
| 31cd8ca0-41e8-46dc-9a58-df7aa2786e51 | 18-PCI 1 M2                 | temperature | enabled | offline |
| 29185b0b-da1c-4d11-8771-212003a71426 | 19-PCI 1 M2 Zn              | temperature | enabled | ok      |
| 3be8651c-490b-4a73-b291-d5158a70510c | 20-PCI 2 M2                 | temperature | enabled | offline |
| b4a96a2d-2724-4c13-993d-b2b2ce179f58 | 21-PCI 2 M2 Zn              | temperature | enabled | ok      |
| bc00253a-1ba2-4f05-8651-07c91760c08c | 22-PCI 3 M2                 | temperature | enabled | offline |
| 0a70d7f0-cc03-4e19-abf4-cb2cde863171 | 23-PCI 3 M2 Zn              | temperature | enabled | ok      |
| 48e7a7c4-d693-4e08-8271-456366eed235 | 24-PCI 4 M2                 | temperature | enabled | offline |
| 0b56de79-1208-4281-9f7e-d6ba6538e29a | 26.1-PCI 1 GPU-Board Temp   | temperature | enabled | ok      |
| f8e83829-b924-4100-98ac-0cc6ba2d5b2f | 26.2-PCI 1 GPU-FPGA Core    | temperature | enabled | ok      |
|                                      | Temp                        |             |         |         |
|                                      |                             |             |         |         |
| ec0e723e-dd96-45bb-94ae-8a4a0f8ad901 | 27-PCI 1 Zone               | temperature | enabled | ok      |
| 1c263411-9683-4771-a234-bb7fef26f579 | 28-PCI 2                    | temperature | enabled | offline |
| 816e5c43-af1c-47e3-b338-63ce9eb1b88f | 30.1-PCI 3-Network          | temperature | enabled | ok      |
|                                      | controller                  |             |         |         |
|                                      |                             |             |         |         |
| c87b83e3-756d-4733-8a59-c30c5d21042f | 30.2-PCI 3-Network          | temperature | enabled | ok      |
|                                      | controller                  |             |         |         |
|                                      |                             |             |         |         |
| 8363c276-f04f-4b75-b745-f9375503901d | 31-PCI 3 Zone               | temperature | enabled | ok      |
| 4641a6b5-19e5-40cd-97ec-e5300e41e804 | 32-PCI 4                    | temperature | enabled | offline |
| 301d92e4-6bf7-4d0b-804d-42ef23ff3ec7 | 36-Sys Exhaust 1            | temperature | enabled | ok      |
| 9e48a215-f9d8-4b9f-ac59-fa91de89a256 | 37-E-Fuse 1                 | temperature | enabled | ok      |
| 824ebe0e-bbfc-4910-b9be-25331d391ed5 | 38-E-Fuse 2                 | temperature | enabled | ok      |
| 0923dbf7-8d13-43b4-9336-a528ac5b406b | 39-E-Fuse 3                 | temperature | enabled | ok      |
| db1f3a99-31e4-4b39-bb4f-853341c2dc35 | 45-PCI 5                    | temperature | enabled | offline |
| 0fac320f-f8e5-47e9-9980-e8aca047f54c | 47-Stor Batt                | temperature | enabled | offline |
| f15f035d-3d16-41cf-a6e3-2d9e5cb694a8 | 48-PCI 5 Zone               | temperature | enabled | offline |
| 07fb8039-ed01-4e81-8f73-029bac0b3dc6 | 49-Front Ambient            | temperature | enabled | offline |
| 24021e4c-bcc9-4d81-bfbd-7c573b6092c0 | 51-CPU 1 PkgTmp             | temperature | enabled | ok      |
| f5fa0435-e970-4931-9129-2b85c170faac | Fan 1                       | fan         | enabled | ok      |
| 094d1c2b-8da8-4eae-bdd1-3f57737e8d61 | Fan 2                       | fan         | enabled | ok      |
| 0151cb62-2727-4192-8269-a3b9525b813b | Fan 3                       | fan         | enabled | ok      |
| 2d6468af-61bf-463f-8193-d2d288bd2a95 | Fan 4                       | fan         | enabled | ok      |
| 84245f14-b514-4c24-8dba-979c09058625 | Fan 5                       | fan         | enabled | ok      |
| 54ce3c1d-f4fd-4909-80fa-f221db5cfa96 | Fan 6                       | fan         | enabled | ok      |
| 06a57796-190e-471e-a323-5f95247372e8 | HpeServerPowerSupply        | power       | enabled | ok      |
+--------------------------------------+-----------------------------+-------------+---------+---------+
[XXXXXX@controller-0 ~(keystone_admin)]$
```

## works, took a little time  (~5 mins) for the subcloud to pull all availible sensor data, but eventually did pull it.

## Lets look at ipmitool sensor to verify against... 

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ sudo -i
root@controller-0:~# ipmitool sensor
UID              | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
SysHealth_Stat   | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
01-Inlet Ambient | 28.000     | degrees C  | ok    | na        | na        | na        | na        | 62.000    | 66.000
02-CPU           | 40.000     | degrees C  | ok    | na        | na        | na        | na        | 70.000    | na
03-P DIMM 1-6    | 50.000     | degrees C  | ok    | na        | na        | na        | na        | 89.000    | na
04-P PMM 1-6     | na         |            | na    | na        | na        | na        | na        | 83.000    | na
05-P DIMM 7-12   | 50.000     | degrees C  | ok    | na        | na        | na        | na        | 89.000    | na
06-P PMM 7-12    | na         |            | na    | na        | na        | na        | na        | 83.000    | na
07-mLOM          | na         |            | na    | na        | na        | na        | na        | 100.000   | na
08-mLOM Zone     | 33.000     | degrees C  | ok    | na        | na        | na        | na        | 75.000    | 80.000
09-BMC           | 54.000     | degrees C  | ok    | na        | na        | na        | na        | 105.000   | na
10-BMC Zone      | 33.000     | degrees C  | ok    | na        | na        | na        | na        | 70.000    | 75.000
11-M2            | na         |            | na    | na        | na        | na        | na        | na        | na
12-M2 Zone       | 30.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
13-Chipset       | 50.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
14-Battery Zone  | 29.000     | degrees C  | ok    | na        | na        | na        | na        | 70.000    | 75.000
15-VR P Mem 1    | 51.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
16-VR P Mem 2    | 38.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
17-VR P          | 60.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
18-PCI 1 M2      | na         |            | na    | na        | na        | na        | na        | 80.000    | na
19-PCI 1 M2 Zn   | 32.000     | degrees C  | ok    | na        | na        | na        | na        | 70.000    | 75.000
20-PCI 2 M2      | na         |            | na    | na        | na        | na        | na        | 80.000    | na
21-PCI 2 M2 Zn   | 32.000     | degrees C  | ok    | na        | na        | na        | na        | 70.000    | 75.000
22-PCI 3 M2      | na         |            | na    | na        | na        | na        | na        | 80.000    | na
23-PCI 3 M2 Zn   | 32.000     | degrees C  | ok    | na        | na        | na        | na        | 70.000    | 75.000
24-PCI 4 M2      | na         |            | na    | na        | na        | na        | na        | 80.000    | na
27-PCI 1 Zone    | 38.000     | degrees C  | ok    | na        | na        | na        | na        | 70.000    | 75.000
28-PCI 2         | na         |            | na    | na        | na        | na        | na        | 100.000   | na
31-PCI 3 Zone    | 38.000     | degrees C  | ok    | na        | na        | na        | na        | 70.000    | 75.000
32-PCI 4         | na         |            | na    | na        | na        | na        | na        | 100.000   | na
36-Sys Exhaust 1 | 49.000     | degrees C  | ok    | na        | na        | na        | na        | 80.000    | 85.000
37-E-Fuse 1      | 43.000     | degrees C  | ok    | na        | na        | na        | na        | 100.000   | na
38-E-Fuse 2      | 33.000     | degrees C  | ok    | na        | na        | na        | na        | 100.000   | na
39-E-Fuse 3      | 33.000     | degrees C  | ok    | na        | na        | na        | na        | 100.000   | na
45-PCI 5         | na         |            | na    | na        | na        | na        | na        | 100.000   | na
47-Stor Batt     | na         |            | na    | na        | na        | na        | na        | 60.000    | na
48-PCI 5 Zone    | na         |            | na    | na        | na        | na        | na        | na        | na
49-Front Ambient | na         |            | na    | na        | na        | na        | na        | na        | na
51-CPU 1 PkgTmp  | 74.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
Fan 1            | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
Fan 1 DutyCycle  | 28.616     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 1 Presence   | 0x0        | discrete   | 0x0280| na        | na        | na        | na        | na        | na
Fan 2            | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
Fan 2 DutyCycle  | 28.616     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 2 Presence   | 0x0        | discrete   | 0x0280| na        | na        | na        | na        | na        | na
Fan 3            | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
Fan 3 DutyCycle  | 28.616     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 3 Presence   | 0x0        | discrete   | 0x0280| na        | na        | na        | na        | na        | na
Fan 4            | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
Fan 4 DutyCycle  | 28.616     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 4 Presence   | 0x0        | discrete   | 0x0280| na        | na        | na        | na        | na        | na
Fan 5            | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
Fan 5 DutyCycle  | 28.616     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 5 Presence   | 0x0        | discrete   | 0x0280| na        | na        | na        | na        | na        | na
Fan 6            | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
Fan 6 DutyCycle  | 28.616     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 6 Presence   | 0x0        | discrete   | 0x0280| na        | na        | na        | na        | na        | na
Power Supply 1   | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
PS 1 Input       | 160.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
Power Supply 2   | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
PS 2 Input       | 150.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
Fans             | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
Memory Status    | 0x0        | discrete   | 0x4080| na        | na        | na        | na        | na        | na
Megacell Status  | na         | discrete   | na    | na        | na        | na        | na        | na        | na
CPU Utilization  | 12.000     | percent    | ok    | na        | na        | na        | na        | na        | na
PS 1 Output      | 160.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PS_Volt_Out_01   | 52.000     | Volts      | ok    | na        | na        | na        | na        | na        | na
PS_Volt_In_01    | 52.000     | Volts      | ok    | na        | na        | na        | na        | na        | na
PS_Curr_Out_01   | 3.100      | Amps       | ok    | na        | na        | na        | na        | na        | na
PS_Curr_In_01    | 1.600      | Amps       | ok    | na        | na        | na        | na        | na        | na
PS 2 Output      | 150.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PS_Volt_Out_02   | 52.000     | Volts      | ok    | na        | na        | na        | na        | na        | na
PS_Volt_In_02    | 52.000     | Volts      | ok    | na        | na        | na        | na        | na        | na
PS_Curr_Out_02   | 2.900      | Amps       | ok    | na        | na        | na        | na        | na        | na
PS_Curr_In_02    | 1.600      | Amps       | ok    | na        | na        | na        | na        | na        | na
30.1-PCI 3-Netwo | 35.000     | degrees C  | ok    | na        | na        | na        | 87.000    | 91.000    | 105.000
30.2-PCI 3-Netwo | 35.000     | degrees C  | ok    | na        | na        | na        | 87.000    | 91.000    | 105.000
26.1-PCI 1 GPU-B | 73.000     | degrees C  | ok    | na        | na        | na        | 85.000    | 100.000   | 100.000
26.2-PCI 1 GPU-F | 70.000     | degrees C  | ok    | na        | na        | na        | 85.000    | 100.000   | 100.000
NIC_Link_03P1    | na         | discrete   | na    | na        | na        | na        | na        | na        | na
NIC_Link_03P2    | na         | discrete   | na    | na        | na        | na        | na        | na        | na
LOM_Link_P1      | na         | discrete   | na    | na        | na        | na        | na        | na        | na
LOM_Link_P1      | na         | discrete   | na    | na        | na        | na        | na        | na        | na
LOM_Link_P2      | na         | discrete   | na    | na        | na        | na        | na        | na        | na
LOM_Link_P3      | na         | discrete   | na    | na        | na        | na        | na        | na        | na
LOM_Link_P4      | na         | discrete   | na    | na        | na        | na        | na        | na        | na
CPU_Stat_C1      | 0x0        | discrete   | 0x8080| na        | na        | na        | na        | na        | na
root@controller-0:~#

[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ IP=2607:f160:10:922a:ce:406:0:1000
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ rf_sensor_list.py -u XXXXXX -p XXXXXX -r https://[$IP]
Chassis 'Computer System Chassis' Status
  Sensor                    | Reading    | Health   | LF       | LC       | LNC      | UNC      | UC       | UF       | PhysicalContext
  State                     | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  HpeServerPowerSupply Stat | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  HpeServerPowerSupply Line | 52V        | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  HpeServerPowerSupply Powe | 1500W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  HpeServerPowerSupply Last | 144W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  HpeServerPowerSupply Stat | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  HpeServerPowerSupply Line | 52V        | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  HpeServerPowerSupply Powe | 1500W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  HpeServerPowerSupply Last | 143W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  01-Inlet Ambient          | 28Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 62       | 66       | Intake
  02-CPU                    | 42Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 70       | N/A      | CPU
  03-P DIMM 1-6             | 50Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 89       | N/A      | Memory
  04-P PMM 1-6              | 0Cel       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Memory
  05-P DIMM 7-12            | 50Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 89       | N/A      | Memory
  06-P PMM 7-12             | 0Cel       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Memory
  07-mLOM                   | 0Cel       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard
  08-mLOM Zone              | 33Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 75       | 80       | SystemBoard
  09-BMC                    | 53Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 105      | N/A      | SystemBoard
  10-BMC Zone               | 33Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 70       | 75       | SystemBoard
  11-M2                     | 0Cel       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard
  12-M2 Zone                | 30Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard
  13-Chipset                | 50Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard
  14-Battery Zone           | 29Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 70       | 75       | SystemBoard
  15-VR P Mem 1             | 51Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard
  16-VR P Mem 2             | 38Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard
  17-VR P                   | 60Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard
  18-PCI 1 M2               | 0Cel       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard
  19-PCI 1 M2 Zn            | 32Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 70       | 75       | SystemBoard
  20-PCI 2 M2               | 0Cel       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard
  21-PCI 2 M2 Zn            | 32Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 70       | 75       | SystemBoard
  22-PCI 3 M2               | 0Cel       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard
  23-PCI 3 M2 Zn            | 32Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 70       | 75       | SystemBoard
  24-PCI 4 M2               | 0Cel       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard
  27-PCI 1 Zone             | 38Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 70       | 75       | SystemBoard
  28-PCI 2                  | 0Cel       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard
  31-PCI 3 Zone             | 38Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 70       | 75       | SystemBoard
  32-PCI 4                  | 0Cel       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard
  36-Sys Exhaust 1          | 49Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 80       | 85       | SystemBoard
  37-E-Fuse 1               | 43Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 100      | N/A      | SystemBoard
  38-E-Fuse 2               | 33Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 100      | N/A      | SystemBoard
  39-E-Fuse 3               | 33Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 100      | N/A      | SystemBoard
  45-PCI 5                  | 0Cel       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard
  47-Stor Batt              | 0Cel       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard
  48-PCI 5 Zone             | 0Cel       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard
  49-Front Ambient          | 0Cel       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  51-CPU 1 PkgTmp           | 77Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | CPU
  30.1-PCI 3-Network contro | 35Cel      | OK       | N/A      | N/A      | N/A      | 87       | 91       | 105      | SystemBoard
  30.2-PCI 3-Network contro | 35Cel      | OK       | N/A      | N/A      | N/A      | 87       | 91       | 105      | SystemBoard
  26.1-PCI 1 GPU-Board Temp | 73Cel      | OK       | N/A      | N/A      | N/A      | 85       | 100      | 100      | SystemBoard
  26.2-PCI 1 GPU-FPGA Core  | 70Cel      | OK       | N/A      | N/A      | N/A      | 85       | 100      | 100      | SystemBoard
  Fan 1                     | 28%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard
  Fan 2                     | 28%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard
  Fan 3                     | 28%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard
  Fan 4                     | 28%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard
  Fan 5                     | 28%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard
  Fan 6                     | 28%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard

Chassis '' Status
  Sensor                    | Reading    | Health   | LF       | LC       | LNC      | UNC      | UC       | UF       | PhysicalContext

[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$

```



## Passed MEAKV-240



### MEAKV-241

```log

[XXXXXX@controller-0 ~(keystone_admin)]$ system host-show 1 | grep bm
| bm_ip                  | 2607:f160:10:922a:ce:406:0:1000                                          |
| bm_type                | redfish                                                                  |
| bm_username            | XXXXXX                                                                   |
[XXXXXX@controller-0 ~(keystone_admin)]$ system host-update controller-0 bm_type=none
+------------------------+--------------------------------------------------------------------------+
| Property               | Value                                                                    |
+------------------------+--------------------------------------------------------------------------+
| action                 | none                                                                     |
| administrative         | unlocked                                                                 |
| apparmor               | disabled                                                                 |
| availability           | degraded                                                                 |
| bm_ip                  | None                                                                     |
| bm_type                | none                                                                     |
| bm_username            | None                                                                     |
| boot_device            | /dev/disk/by-path/pci-0000:12:00.0-nvme-1                                |
| capabilities           | {'is_max_cpu_configurable': 'configurable', 'min_cpu_mhz_allowed': None, |
|                        | 'max_cpu_mhz_allowed': None, 'cstates_available': 'C1,C2,POLL',          |
|                        | 'stor_function': 'monitor'}                                              |
| clock_synchronization  | ptp                                                                      |
| config_applied         | 4a19c78f-9e44-416c-a311-96254306d83a                                     |
| config_status          | Config out-of-date                                                       |
| config_target          | 785dac29-b30f-433c-99b8-0791c5ecb4b0                                     |
| console                | ttyS0,115200                                                             |
| created_at             | 2024-07-03T16:13:22.992684+00:00                                         |
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
| max_cpu_mhz_configured | 2340                                                                     |
| mgmt_ip                | 2607:f160:10:9232:ce:40a:0:1                                             |
| mgmt_mac               | d4:f5:ef:55:13:98                                                        |
| operational            | enabled                                                                  |
| personality            | controller                                                               |
| reboot_needed          | False                                                                    |
| reserved               | False                                                                    |
| rootfs_device          | /dev/disk/by-path/pci-0000:12:00.0-nvme-1                                |
| serialid               | None                                                                     |
| software_load          | 22.12                                                                    |
| subfunction_avail      | failed                                                                   |
| subfunction_oper       | disabled                                                                 |
| subfunctions           | controller,worker,lowlatency                                             |
| task                   | Configuration failure, threshold reached, Lock/Unlock to retry           |
| tboot                  |                                                                          |
| ttys_dcd               | False                                                                    |
| updated_at             | 2024-08-28T20:31:21.380174+00:00                                         |
| uptime                 | 1917                                                                     |
| uuid                   | 6a0d7b8b-3a64-4f7b-923a-2b19ac35f56a                                     |
| vim_progress_status    | services-enabled                                                         |
+------------------------+--------------------------------------------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ system host-show 1 | grep bm
| bm_ip                  | None                                                                     |
| bm_type                | none                                                                     |
| bm_username            | None                                                                     |
[XXXXXX@controller-0 ~(keystone_admin)]$ system host-sensor-list 1

[XXXXXX@controller-0 ~(keystone_admin)]$

```

## Sensor interface with WRCP has been removed, test has passed.
