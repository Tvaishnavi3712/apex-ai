# HPE ILO5 3.06 BIOS H10 1.70
# HPE E920t server
# 9/6/24 James Patchett - MTCE Lab VCPfe
# Platform Deploymnet MEAKV-239-241

## welktxef-931883-rh-le092s6-010
ILO:  2607:F160:10:9249:CE:40A:0:E00A
OAM:  2607:f160:10:9249:ce:40a:0:f405

## Subcloud welktxef-d931883-010
## General info before we start

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ system show
+------------------------+--------------------------------------+
| Property               | Value                                |
+------------------------+--------------------------------------+
| contact                | None                                 |
| created_at             | 2024-07-06T06:01:35.388553+00:00     |
| description            | None                                 |
| distributed_cloud_role | subcloud                             |
| https_enabled          | True                                 |
| latitude               | None                                 |
| location               | None                                 |
| longitude              | None                                 |
| name                   | welktxef-d931883-010                 |
| region_name            | welktxef-d931883-010                 |
| sdn_enabled            | False                                |
| security_feature       | spectre_meltdown_v1                  |
| service_project_name   | services                             |
| shared_services        | []                                   |
| software_version       | 22.12                                |
| system_mode            | simplex                              |
| system_type            | All-in-one                           |
| timezone               | UTC                                  |
| updated_at             | 2024-09-02T04:29:14.820032+00:00     |
| uuid                   | d5210f5b-d238-4dad-a491-4b9bbb2f6aba |
| vswitch_type           | none                                 |
+------------------------+--------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ system oam-show
+----------------+---------------------------------------+
| Property       | Value                                 |
+----------------+---------------------------------------+
| created_at     | 2024-07-06T06:03:29.802939+00:00      |
| isystem_uuid   | d5210f5b-d238-4dad-a491-4b9bbb2f6aba  |
| oam_end_ip     | 2607:f160:10:9249:ffff:ffff:ffff:fffe |
| oam_gateway_ip | 2607:f160:10:9249:ce:28::             |
| oam_ip         | 2607:f160:10:9249:ce:40a:0:f405       |
| oam_start_ip   | 2607:f160:10:9249::1                  |
| oam_subnet     | 2607:f160:10:9249::/64                |
| updated_at     | None                                  |
| uuid           | 76a9eba6-7f5f-4cda-a882-8954a9cc0b0d  |
+----------------+---------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ system application-list
+--------------------------+----------+-------------------------------------------+------------------+---------+------------------+
| application              | version  | manifest name                             | manifest file    | status  | progress         |
+--------------------------+----------+-------------------------------------------+------------------+---------+------------------+
| cert-manager             | 22.12-8  | cert-manager-fluxcd-manifests             | fluxcd-manifests | applied | completed        |
| metrics-server           | 22.12-1  | metrics-server-fluxcd-manifests           | fluxcd-manifests | applied | Application      |
|                          |          |                                           |                  |         | update from      |
|                          |          |                                           |                  |         | version 22.12-2  |
|                          |          |                                           |                  |         | to version 22.   |
|                          |          |                                           |                  |         | 12-1 completed.  |
|                          |          |                                           |                  |         |                  |
| nginx-ingress-controller | 22.12-1  | nginx-ingress-controller-fluxcd-manifests | fluxcd-manifests | applied | completed        |
| oidc-auth-apps           | 22.12-6  | oidc-auth-apps-fluxcd-manifests           | fluxcd-manifests | applied | completed        |
| platform-integ-apps      | 22.12-62 | platform-integ-apps-fluxcd-manifests      | fluxcd-manifests | applied | Application      |
|                          |          |                                           |                  |         | update from      |
|                          |          |                                           |                  |         | version 22.12-72 |
|                          |          |                                           |                  |         | to version 22.   |
|                          |          |                                           |                  |         | 12-62 completed. |
|                          |          |                                           |                  |         |                  |
| ptp-notification         | 22.      | ptp-notification-fluxcd-manifests         | fluxcd-manifests | applied | Application      |
|                          | 12-138   |                                           |                  |         | update from      |
|                          |          |                                           |                  |         | version 22.      |
|                          |          |                                           |                  |         | 12-140 to        |
|                          |          |                                           |                  |         | version 22.      |
|                          |          |                                           |                  |         | 12-138 completed |
|                          |          |                                           |                  |         | .                |
|                          |          |                                           |                  |         |                  |
| wr-analytics             | 22.12-1  | wr-analytics-fluxcd-manifests             | fluxcd-manifests | applied | completed        |
+--------------------------+----------+-------------------------------------------+------------------+---------+------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ sw-patch query
      Patch ID         RR  Release  Patch State
=====================  ==  =======  ===========
WRCP_22.12_PATCH_0001  Y    22.12    Committed
WRCP_22.12_PATCH_0002  Y    22.12    Committed
WRCP_22.12_PATCH_0003  Y    22.12    Committed
WRCP_22.12_PATCH_0004  Y    22.12    Available
WRCP_22.12_PATCH_0005  Y    22.12    Available

[XXXXXX@controller-0 ~(keystone_admin)]$ fm alarm-list

[XXXXXX@controller-0 ~(keystone_admin)]$
```

## MEAKV-239


```log
[XXXXXX@controller-0 ~(keystone_admin)]$ system host-show 1 |grep bm
| bm_ip                  | None                                                                    |
| bm_type                | none                                                                    |
| bm_username            | None                                                                    |
[XXXXXX@controller-0 ~(keystone_admin)]$ system host-update controller-0 bm_ip=2607:F160:10:9249:CE:40A:0:E00A bm_type=redfish bm_username=XXXXXX bm_password=XXXXXX
+------------------------+-------------------------------------------------------------------------+
| Property               | Value                                                                   |
+------------------------+-------------------------------------------------------------------------+
| action                 | none                                                                    |
| administrative         | unlocked                                                                |
| apparmor               | disabled                                                                |
| availability           | available                                                               |
| bm_ip                  | 2607:F160:10:9249:CE:40A:0:E00A                                         |
| bm_type                | redfish                                                                 |
| bm_username            | XXXXXX                                                                  |
| boot_device            | /dev/disk/by-path/pci-0000:c2:00.0-nvme-1                               |
| capabilities           | {'is_max_cpu_configurable': 'configurable', 'stor_function': 'monitor', |
|                        | 'min_cpu_mhz_allowed': 800, 'max_cpu_mhz_allowed': 3500}                |
| clock_synchronization  | ptp                                                                     |
| config_applied         | 43ea95cf-98e5-49d6-93e1-b31067a94a12                                    |
| config_status          | None                                                                    |
| config_target          | 43ea95cf-98e5-49d6-93e1-b31067a94a12                                    |
| console                | ttyS0,115200                                                            |
| created_at             | 2024-07-06T06:03:31.484283+00:00                                        |
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
| max_cpu_mhz_allowed    | 3500                                                                    |
| max_cpu_mhz_configured | 3500                                                                    |
| mgmt_ip                | 2607:f160:10:924a:ce:40a:0:1                                            |
| mgmt_mac               | b4:96:91:b7:d9:f4                                                       |
| operational            | enabled                                                                 |
| personality            | controller                                                              |
| reboot_needed          | False                                                                   |
| reserved               | False                                                                   |
| rootfs_device          | /dev/disk/by-path/pci-0000:c2:00.0-nvme-1                               |
| serialid               | None                                                                    |
| software_load          | 22.12                                                                   |
| subfunction_avail      | available                                                               |
| subfunction_oper       | enabled                                                                 |
| subfunctions           | controller,worker,lowlatency                                            |
| task                   |                                                                         |
| tboot                  |                                                                         |
| ttys_dcd               | False                                                                   |
| updated_at             | 2024-09-06T20:36:15.830962+00:00                                        |
| uptime                 | 403966                                                                  |
| uuid                   | 0cb8ff32-f309-4dd2-86e9-33c7fa475842                                    |
| vim_progress_status    | services-enabled                                                        |
+------------------------+-------------------------------------------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ system host-show 1|grep bm
| bm_ip                  | 2607:F160:10:9249:CE:40A:0:E00A                                         |
| bm_type                | redfish                                                                 |
| bm_username            | XXXXXX                                                                  |
[XXXXXX@controller-0 ~(keystone_admin)]$
```

## Success

## Sleeping 5 mins, till trying to look for sensor data.

## MEAKV-240

```log
[XXXXXX@controller-0 ~(keystone_admin)]$  system host-show 1 | grep bm
| bm_ip                  | 2607:F160:10:9249:CE:40A:0:E00A                                         |
| bm_type                | redfish                                                                 |
| bm_username            | XXXXXX                                                                  |
[XXXXXX@controller-0 ~(keystone_admin)]$ system host-sensor-list 1
+--------------------------------------+----------------+-------------+---------+---------+
| uuid                                 | name           | sensortype  | state   | status  |
+--------------------------------------+----------------+-------------+---------+---------+
| 64f82e46-bd15-49d6-84ee-76e2b4857ea0 | 01-Inlet       | temperature | enabled | ok      |
|                                      | Ambient        |             |         |         |
|                                      |                |             |         |         |
| 1e235608-59ea-46dd-b044-96c6abaa2a56 | 02-CPU 1       | temperature | enabled | ok      |
| 663aed72-f6f0-461b-a613-82b2b36e7864 | 03-P1 DIMM 1-6 | temperature | enabled | ok      |
| 02ac51ad-ce8e-48a4-b109-ecf2068b57db | 04-P1 PMM 1-6  | temperature | enabled | offline |
| 6a2525b8-e7fb-449b-a24d-3f66f4b27f7c | 05-P1 DIMM     | temperature | enabled | ok      |
|                                      | 7-12           |             |         |         |
|                                      |                |             |         |         |
| 44d3aa20-1a8c-4893-af45-932047322b34 | 06-P1 PMM 7-12 | temperature | enabled | offline |
| 1c994c52-53ad-4f10-bd22-e3fecd2cc10a | 07-VR P1       | temperature | enabled | ok      |
| 918dd8d1-0036-4447-9b01-26c1180e1b7a | 08-VR P1 Mem 1 | temperature | enabled | ok      |
| fd7b138b-bdea-455c-9034-2f55bdf89daa | 09-VR P1 Mem 2 | temperature | enabled | ok      |
| c274b997-e603-438f-9b06-8d970d789701 | 10-Chipset     | temperature | enabled | ok      |
| 9d5b2415-ef92-42e0-a690-359220c7d0e0 | 12-Battery     | temperature | enabled | ok      |
|                                      | Zone           |             |         |         |
|                                      |                |             |         |         |
| b44dd911-dac3-473d-9448-956f9581b6ab | 17-LOM Card    | temperature | enabled | offline |
| 3645bb35-cb82-4fd2-98a6-8053acdc0ecf | 18-LOM Card    | temperature | enabled | ok      |
|                                      | Zone           |             |         |         |
|                                      |                |             |         |         |
| a6dfb811-c93a-45bc-b477-15f85a77fbe0 | 20-mLOM Zone   | temperature | enabled | offline |
| ca7b8bd2-aba3-4cb2-a5b3-a277b86cb1b8 | 21.1-PCI       | temperature | enabled | ok      |
|                                      | 1-Network      |             |         |         |
|                                      | controller     |             |         |         |
|                                      |                |             |         |         |
| 583bb8a4-9cf4-4b30-8181-5472b5a2f9fc | 21.2-PCI       | temperature | enabled | ok      |
|                                      | 1-SFP28        |             |         |         |
|                                      | (SFF-8402)     |             |         |         |
|                                      |                |             |         |         |
| 649b6884-b159-4b67-a262-4127a1db5048 | 21.3-PCI       | temperature | enabled | ok      |
|                                      | 1-SFP28        |             |         |         |
|                                      | (SFF-8402)     |             |         |         |
|                                      |                |             |         |         |
| 150273d1-9d08-4b83-8ea7-8c5133574d45 | 22-PCI 1 Zone  | temperature | enabled | ok      |
| 91bee66d-d6d2-4024-91ca-3e7d01877a66 | 23.1-PCI       | temperature | enabled | ok      |
|                                      | 2-Network      |             |         |         |
|                                      | controller     |             |         |         |
|                                      |                |             |         |         |
| dcd5cb38-a24b-475f-ab9d-14c81a9ae8fe | 23.2-PCI       | temperature | enabled | ok      |
|                                      | 2-SFP28        |             |         |         |
|                                      | (SFF-8402)     |             |         |         |
|                                      |                |             |         |         |
| 395633d1-2ba8-4fbb-9402-f749bf141c5a | 23.3-PCI       | temperature | enabled | ok      |
|                                      | 2-SFP28        |             |         |         |
|                                      | (SFF-8402)     |             |         |         |
|                                      |                |             |         |         |
| 7454fd36-09ce-4421-a7d7-18fa47cb10d8 | 24-PCI 2 Zone  | temperature | enabled | ok      |
| 681eeeaf-d496-44a1-9680-4f777a69d82a | 25.1-PCI 3-On  | temperature | enabled | ok      |
|                                      | Board          |             |         |         |
|                                      |                |             |         |         |
| 51b79b6a-d3e8-4aaa-9993-e2d153f1186c | 25.2-PCI 3-GPU | temperature | enabled | ok      |
|                                      | ASIC           |             |         |         |
|                                      |                |             |         |         |
| 9347f8eb-f0c6-41ae-a1c7-52ee063480de | 25.3-PCI 3-GPU | temperature | enabled | ok      |
|                                      | ASIC           |             |         |         |
|                                      |                |             |         |         |
| 85f0dc1a-4833-461d-8cae-8748d387fbba | 25.4-PCI       | temperature | enabled | ok      |
|                                      | 3-Chip Cores   |             |         |         |
|                                      |                |             |         |         |
| 3a8d1a0a-72df-4b61-b5c2-9f28070f0bdb | 26-PCI 3 Zone  | temperature | enabled | ok      |
| fe5dacae-e081-4ba2-b902-5489502f43aa | 27-PCI 4       | temperature | enabled | offline |
| 8132749d-d882-4b53-997e-9dbbb88cd15d | 28-PCI 4 Zone  | temperature | enabled | offline |
| e56ba726-0d85-444e-b6d4-79dd55dcdef8 | 29-PCI 5       | temperature | enabled | offline |
| fa787131-e87a-4d1d-be10-8e969e452aff | 30-PCI 5 Zone  | temperature | enabled | offline |
| a6deb0cf-93b6-482f-b1e9-a64a5ba25d78 | 31-E-Fuse 1    | temperature | enabled | ok      |
| c7b405f0-ff4e-49a3-8719-5c5dc79ae8dc | 32-E-Fuse 2    | temperature | enabled | ok      |
| b12679a2-2a21-46ab-a996-9ed6b4ce1a50 | 33-E-Fuse 3    | temperature | enabled | ok      |
| 91a355f5-922e-4d48-b675-c85a8e8481bd | 34-Stor Batt   | temperature | enabled | offline |
| 282141d1-5fbd-4e97-8b27-21f480b7ae90 | 39-Sys Exhaust | temperature | enabled | ok      |
|                                      | 1              |             |         |         |
|                                      |                |             |         |         |
| 3941c454-0f31-4702-8e2e-c9fad07ef004 | 40-CPU 1       | temperature | enabled | ok      |
|                                      | PkgTmp         |             |         |         |
|                                      |                |             |         |         |
| 88c41e95-6a4f-469a-aeca-af90b204aa2e | 45-HD          | temperature | enabled | offline |
|                                      | Controller     |             |         |         |
|                                      |                |             |         |         |
| 8f43b901-dcb2-4677-b904-7e25ea362e04 | 46-HD Cntlr    | temperature | enabled | offline |
|                                      | Zone           |             |         |         |
|                                      |                |             |         |         |
| f7db8c65-a398-4bf6-a2bb-2140de7bc16f | 47-HD Max      | temperature | enabled | offline |
| 7a08929a-18dd-49aa-96b6-18aacc272de6 | 48-Board Inlet | temperature | enabled | offline |
| 2d8285e6-4cca-46b5-9e38-56fbf2cea446 | Fan 1          | fan         | enabled | ok      |
| 02bd5a3b-3b02-490a-9d8a-f21f8430f6e2 | Fan 2          | fan         | enabled | ok      |
| 7f35acc5-19f6-4760-86a6-eaa848090251 | Fan 3          | fan         | enabled | ok      |
| 724ed093-59f5-49c7-b8dc-9a7c2fbd8098 | Fan 4          | fan         | enabled | ok      |
| 9d5ca10c-8445-4fb3-b822-8ece4225a12c | Fan 5          | fan         | enabled | ok      |
| d0e2cc50-b9f3-4259-8ee1-72ea3e11ec16 | Fan 6          | fan         | enabled | ok      |
| 5651c52b-2452-4cf9-8632-a0b558715fc9 | HpeServerPower | power       | enabled | ok      |
|                                      | Supply         |             |         |         |
|                                      |                |             |         |         |
+--------------------------------------+----------------+-------------+---------+---------+
[XXXXXX@controller-0 ~(keystone_admin)]$ system host-sensor-list 1
+--------------------------------------+----------------+-------------+---------+---------+
| uuid                                 | name           | sensortype  | state   | status  |
+--------------------------------------+----------------+-------------+---------+---------+
| 64f82e46-bd15-49d6-84ee-76e2b4857ea0 | 01-Inlet       | temperature | enabled | ok      |
|                                      | Ambient        |             |         |         |
|                                      |                |             |         |         |
| 1e235608-59ea-46dd-b044-96c6abaa2a56 | 02-CPU 1       | temperature | enabled | ok      |
| 663aed72-f6f0-461b-a613-82b2b36e7864 | 03-P1 DIMM 1-6 | temperature | enabled | ok      |
| 02ac51ad-ce8e-48a4-b109-ecf2068b57db | 04-P1 PMM 1-6  | temperature | enabled | offline |
| 6a2525b8-e7fb-449b-a24d-3f66f4b27f7c | 05-P1 DIMM     | temperature | enabled | ok      |
|                                      | 7-12           |             |         |         |
|                                      |                |             |         |         |
| 44d3aa20-1a8c-4893-af45-932047322b34 | 06-P1 PMM 7-12 | temperature | enabled | offline |
| 1c994c52-53ad-4f10-bd22-e3fecd2cc10a | 07-VR P1       | temperature | enabled | ok      |
| 918dd8d1-0036-4447-9b01-26c1180e1b7a | 08-VR P1 Mem 1 | temperature | enabled | ok      |
| fd7b138b-bdea-455c-9034-2f55bdf89daa | 09-VR P1 Mem 2 | temperature | enabled | ok      |
| c274b997-e603-438f-9b06-8d970d789701 | 10-Chipset     | temperature | enabled | ok      |
| 9d5b2415-ef92-42e0-a690-359220c7d0e0 | 12-Battery     | temperature | enabled | ok      |
|                                      | Zone           |             |         |         |
|                                      |                |             |         |         |
| b44dd911-dac3-473d-9448-956f9581b6ab | 17-LOM Card    | temperature | enabled | offline |
| 3645bb35-cb82-4fd2-98a6-8053acdc0ecf | 18-LOM Card    | temperature | enabled | ok      |
|                                      | Zone           |             |         |         |
|                                      |                |             |         |         |
| a6dfb811-c93a-45bc-b477-15f85a77fbe0 | 20-mLOM Zone   | temperature | enabled | offline |
| ca7b8bd2-aba3-4cb2-a5b3-a277b86cb1b8 | 21.1-PCI       | temperature | enabled | ok      |
|                                      | 1-Network      |             |         |         |
|                                      | controller     |             |         |         |
|                                      |                |             |         |         |
| 583bb8a4-9cf4-4b30-8181-5472b5a2f9fc | 21.2-PCI       | temperature | enabled | ok      |
|                                      | 1-SFP28        |             |         |         |
|                                      | (SFF-8402)     |             |         |         |
|                                      |                |             |         |         |
| 649b6884-b159-4b67-a262-4127a1db5048 | 21.3-PCI       | temperature | enabled | ok      |
|                                      | 1-SFP28        |             |         |         |
|                                      | (SFF-8402)     |             |         |         |
|                                      |                |             |         |         |
| 150273d1-9d08-4b83-8ea7-8c5133574d45 | 22-PCI 1 Zone  | temperature | enabled | ok      |
| 91bee66d-d6d2-4024-91ca-3e7d01877a66 | 23.1-PCI       | temperature | enabled | ok      |
|                                      | 2-Network      |             |         |         |
|                                      | controller     |             |         |         |
|                                      |                |             |         |         |
| dcd5cb38-a24b-475f-ab9d-14c81a9ae8fe | 23.2-PCI       | temperature | enabled | ok      |
|                                      | 2-SFP28        |             |         |         |
|                                      | (SFF-8402)     |             |         |         |
|                                      |                |             |         |         |
| 395633d1-2ba8-4fbb-9402-f749bf141c5a | 23.3-PCI       | temperature | enabled | ok      |
|                                      | 2-SFP28        |             |         |         |
|                                      | (SFF-8402)     |             |         |         |
|                                      |                |             |         |         |
| 7454fd36-09ce-4421-a7d7-18fa47cb10d8 | 24-PCI 2 Zone  | temperature | enabled | ok      |
| 681eeeaf-d496-44a1-9680-4f777a69d82a | 25.1-PCI 3-On  | temperature | enabled | ok      |
|                                      | Board          |             |         |         |
|                                      |                |             |         |         |
| 51b79b6a-d3e8-4aaa-9993-e2d153f1186c | 25.2-PCI 3-GPU | temperature | enabled | ok      |
|                                      | ASIC           |             |         |         |
|                                      |                |             |         |         |
| 9347f8eb-f0c6-41ae-a1c7-52ee063480de | 25.3-PCI 3-GPU | temperature | enabled | ok      |
|                                      | ASIC           |             |         |         |
|                                      |                |             |         |         |
| 85f0dc1a-4833-461d-8cae-8748d387fbba | 25.4-PCI       | temperature | enabled | ok      |
|                                      | 3-Chip Cores   |             |         |         |
|                                      |                |             |         |         |
| 3a8d1a0a-72df-4b61-b5c2-9f28070f0bdb | 26-PCI 3 Zone  | temperature | enabled | ok      |
| fe5dacae-e081-4ba2-b902-5489502f43aa | 27-PCI 4       | temperature | enabled | offline |
| 8132749d-d882-4b53-997e-9dbbb88cd15d | 28-PCI 4 Zone  | temperature | enabled | offline |
| e56ba726-0d85-444e-b6d4-79dd55dcdef8 | 29-PCI 5       | temperature | enabled | offline |
| fa787131-e87a-4d1d-be10-8e969e452aff | 30-PCI 5 Zone  | temperature | enabled | offline |
| a6deb0cf-93b6-482f-b1e9-a64a5ba25d78 | 31-E-Fuse 1    | temperature | enabled | ok      |
| c7b405f0-ff4e-49a3-8719-5c5dc79ae8dc | 32-E-Fuse 2    | temperature | enabled | ok      |
| b12679a2-2a21-46ab-a996-9ed6b4ce1a50 | 33-E-Fuse 3    | temperature | enabled | ok      |
| 91a355f5-922e-4d48-b675-c85a8e8481bd | 34-Stor Batt   | temperature | enabled | offline |
| 282141d1-5fbd-4e97-8b27-21f480b7ae90 | 39-Sys Exhaust | temperature | enabled | ok      |
|                                      | 1              |             |         |         |
|                                      |                |             |         |         |
| 3941c454-0f31-4702-8e2e-c9fad07ef004 | 40-CPU 1       | temperature | enabled | ok      |
|                                      | PkgTmp         |             |         |         |
|                                      |                |             |         |         |
| 88c41e95-6a4f-469a-aeca-af90b204aa2e | 45-HD          | temperature | enabled | offline |
|                                      | Controller     |             |         |         |
|                                      |                |             |         |         |
| 8f43b901-dcb2-4677-b904-7e25ea362e04 | 46-HD Cntlr    | temperature | enabled | offline |
|                                      | Zone           |             |         |         |
|                                      |                |             |         |         |
| f7db8c65-a398-4bf6-a2bb-2140de7bc16f | 47-HD Max      | temperature | enabled | offline |
| 7a08929a-18dd-49aa-96b6-18aacc272de6 | 48-Board Inlet | temperature | enabled | offline |
| 2d8285e6-4cca-46b5-9e38-56fbf2cea446 | Fan 1          | fan         | enabled | ok      |
| 02bd5a3b-3b02-490a-9d8a-f21f8430f6e2 | Fan 2          | fan         | enabled | ok      |
| 7f35acc5-19f6-4760-86a6-eaa848090251 | Fan 3          | fan         | enabled | ok      |
| 724ed093-59f5-49c7-b8dc-9a7c2fbd8098 | Fan 4          | fan         | enabled | ok      |
| 9d5ca10c-8445-4fb3-b822-8ece4225a12c | Fan 5          | fan         | enabled | ok      |
| d0e2cc50-b9f3-4259-8ee1-72ea3e11ec16 | Fan 6          | fan         | enabled | ok      |
| 5651c52b-2452-4cf9-8632-a0b558715fc9 | HpeServerPower | power       | enabled | ok      |
|                                      | Supply         |             |         |         |
|                                      |                |             |         |         |
+--------------------------------------+----------------+-------------+---------+---------+
[XXXXXX@controller-0 ~(keystone_admin)]$
```

## works, took a little time  (~5 mins) for the subcloud to pull all availible sensor data, but eventually did pull it.

## Lets look at ipmitool sensor to verify against... 

```log
root@controller-0:~# ipmitool sensor
UID              | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
SysHealth_Stat   | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
01-Inlet Ambient | 28.000     | degrees C  | ok    | na        | na        | na        | na        | 62.000    | 66.000
02-CPU 1         | 60.000     | degrees C  | ok    | na        | na        | na        | na        | 70.000    | na
03-P1 DIMM 1-6   | 35.000     | degrees C  | ok    | na        | na        | na        | na        | 90.000    | na
04-P1 PMM 1-6    | na         |            | na    | na        | na        | na        | na        | 82.000    | na
05-P1 DIMM 7-12  | 35.000     | degrees C  | ok    | na        | na        | na        | na        | 90.000    | na
06-P1 PMM 7-12   | na         |            | na    | na        | na        | na        | na        | 82.000    | na
07-VR P1         | 68.000     | degrees C  | ok    | na        | na        | na        | na        | 110.000   | 115.000
08-VR P1 Mem 1   | 54.000     | degrees C  | ok    | na        | na        | na        | na        | 110.000   | 115.000
09-VR P1 Mem 2   | 37.000     | degrees C  | ok    | na        | na        | na        | na        | 110.000   | 115.000
10-Chipset       | 35.000     | degrees C  | ok    | na        | na        | na        | na        | 100.000   | na
12-Battery Zone  | 28.000     | degrees C  | ok    | na        | na        | na        | na        | 70.000    | 75.000
17-LOM Card      | na         |            | na    | na        | na        | na        | na        | 100.000   | na
18-LOM Card Zone | 26.000     | degrees C  | ok    | na        | na        | na        | na        | 95.000    | 100.000
20-mLOM Zone     | na         |            | na    | na        | na        | na        | na        | 85.000    | 90.000
22-PCI 1 Zone    | 26.000     | degrees C  | ok    | na        | na        | na        | na        | 70.000    | 75.000
24-PCI 2 Zone    | 26.000     | degrees C  | ok    | na        | na        | na        | na        | 70.000    | 75.000
26-PCI 3 Zone    | 26.000     | degrees C  | ok    | na        | na        | na        | na        | 70.000    | 75.000
27-PCI 4         | na         |            | na    | na        | na        | na        | na        | 100.000   | na
28-PCI 4 Zone    | na         |            | na    | na        | na        | na        | na        | 70.000    | 75.000
29-PCI 5         | na         |            | na    | na        | na        | na        | na        | 100.000   | na
30-PCI 5 Zone    | na         |            | na    | na        | na        | na        | na        | 70.000    | 75.000
31-E-Fuse 1      | 43.000     | degrees C  | ok    | na        | na        | na        | na        | 100.000   | na
32-E-Fuse 2      | 29.000     | degrees C  | ok    | na        | na        | na        | na        | 100.000   | na
33-E-Fuse 3      | 29.000     | degrees C  | ok    | na        | na        | na        | na        | 100.000   | na
34-Stor Batt     | na         |            | na    | na        | na        | na        | na        | 60.000    | na
39-Sys Exhaust 1 | 46.000     | degrees C  | ok    | na        | na        | na        | na        | 85.000    | 90.000
40-CPU 1 PkgTmp  | 89.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
45-HD Controller | na         |            | na    | na        | na        | na        | na        | 100.000   | na
46-HD Cntlr Zone | na         |            | na    | na        | na        | na        | na        | na        | na
47-HD Max        | na         |            | na    | na        | na        | na        | na        | 60.000    | na
48-Board Inlet   | na         |            | na    | na        | na        | na        | na        | na        | na
Fan 1            | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
Fan 1 DutyCycle  | 45.864     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 1 Presence   | 0x0        | discrete   | 0x0280| na        | na        | na        | na        | na        | na
Fan 2            | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
Fan 2 DutyCycle  | 45.864     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 2 Presence   | 0x0        | discrete   | 0x0280| na        | na        | na        | na        | na        | na
Fan 3            | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
Fan 3 DutyCycle  | 45.864     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 3 Presence   | 0x0        | discrete   | 0x0280| na        | na        | na        | na        | na        | na
Fan 4            | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
Fan 4 DutyCycle  | 45.864     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 4 Presence   | 0x0        | discrete   | 0x0280| na        | na        | na        | na        | na        | na
Fan 5            | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
Fan 5 DutyCycle  | 45.864     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 5 Presence   | 0x0        | discrete   | 0x0280| na        | na        | na        | na        | na        | na
Fan 6            | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
Fan 6 DutyCycle  | 45.864     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 6 Presence   | 0x0        | discrete   | 0x0280| na        | na        | na        | na        | na        | na
Power Supply 1   | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
PS 1 Input       | 160.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
Power Supply 2   | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
PS 2 Input       | 200.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
Fans             | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
Memory Status    | 0x0        | discrete   | 0x4080| na        | na        | na        | na        | na        | na
Megacell Status  | na         | discrete   | na    | na        | na        | na        | na        | na        | na
CPU Utilization  | 63.000     | percent    | ok    | na        | na        | na        | na        | na        | na
PS 1 Output      | 160.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PS_Volt_Out_01   | 214.000    | Volts      | ok    | na        | na        | na        | na        | na        | na
PS_Volt_In_01    | 214.000    | Volts      | ok    | na        | na        | na        | na        | na        | na
PS_Curr_Out_01   | 0.700      | Amps       | ok    | na        | na        | na        | na        | na        | na
PS_Curr_In_01    | 0.500      | Amps       | ok    | na        | na        | na        | na        | na        | na
PS 2 Output      | 190.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PS_Volt_Out_02   | 212.000    | Volts      | ok    | na        | na        | na        | na        | na        | na
PS_Volt_In_02    | 212.000    | Volts      | ok    | na        | na        | na        | na        | na        | na
PS_Curr_Out_02   | 0.800      | Amps       | ok    | na        | na        | na        | na        | na        | na
PS_Curr_In_02    | 0.500      | Amps       | ok    | na        | na        | na        | na        | na        | na
25.1-PCI 3-On Bo | 43.000     | degrees C  | ok    | na        | na        | na        | 75.000    | 80.000    | 85.000
25.2-PCI 3-GPU A | 50.000     | degrees C  | ok    | na        | na        | na        | 105.000   | 110.000   | 115.000
25.3-PCI 3-GPU A | 50.000     | degrees C  | ok    | na        | na        | na        | 105.000   | 110.000   | 115.000
25.4-PCI 3-Chip  | 48.000     | degrees C  | ok    | na        | na        | na        | 115.000   | 120.000   | 125.000
21.1-PCI 1-Netwo | 37.000     | degrees C  | ok    | na        | na        | na        | 95.000    | 105.000   | 115.000
21.2-PCI 1-SFP28 | 29.000     | degrees C  | ok    | na        | na        | na        | 73.000    | 78.000    | 0.000
21.3-PCI 1-SFP28 | 26.000     | degrees C  | ok    | na        | na        | na        | 75.000    | 80.000    | 0.000
23.1-PCI 2-Netwo | 37.000     | degrees C  | ok    | na        | na        | na        | 95.000    | 105.000   | 115.000
23.2-PCI 2-SFP28 | 28.000     | degrees C  | ok    | na        | na        | na        | 73.000    | 78.000    | 0.000
23.3-PCI 2-SFP28 | 27.000     | degrees C  | ok    | na        | na        | na        | 75.000    | 80.000    | 0.000
NIC_Link_01P4    | na         | discrete   | na    | na        | na        | na        | na        | na        | na
NIC_Link_01P1    | 0x0        | discrete   | 0x0280| na        | na        | na        | na        | na        | na
NIC_Link_01P2    | 0x0        | discrete   | 0x0280| na        | na        | na        | na        | na        | na
NIC_Link_01P3    | na         | discrete   | na    | na        | na        | na        | na        | na        | na
NIC_Link_02P2    | 0x0        | discrete   | 0x0280| na        | na        | na        | na        | na        | na
NIC_Link_02P4    | na         | discrete   | na    | na        | na        | na        | na        | na        | na
NIC_Link_02P1    | 0x0        | discrete   | 0x0280| na        | na        | na        | na        | na        | na
NIC_Link_02P3    | na         | discrete   | na    | na        | na        | na        | na        | na        | na
LOM_Link_P1      | na         | discrete   | na    | na        | na        | na        | na        | na        | na
CPU_Stat_C1      | 0x0        | discrete   | 0x8080| na        | na        | na        | na        | na        | na
root@controller-0:~#

[XXXXXX@welktxefnce-h-pe1util-vm01 HPE_FW]$ IP=2607:F160:10:9249:CE:40A:0:E00A
[XXXXXX@welktxefnce-h-pe1util-vm01 HPE_FW]$ rf_sensor_list.py -u XXXXXX -p XXXXXX -r https://[$IP]
Chassis 'Computer System Chassis' Status
  Sensor                    | Reading    | Health   | LF       | LC       | LNC      | UNC      | UC       | UF       | PhysicalContext
  State                     | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  HpeServerPowerSupply Stat | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  HpeServerPowerSupply Line | 214V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  HpeServerPowerSupply Powe | 1500W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  HpeServerPowerSupply Last | 210W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  HpeServerPowerSupply Stat | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  HpeServerPowerSupply Line | 212V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  HpeServerPowerSupply Powe | 1500W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  HpeServerPowerSupply Last | 210W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  01-Inlet Ambient          | 27Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 62       | 66       | Intake
  02-CPU 1                  | 60Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 70       | N/A      | CPU
  03-P1 DIMM 1-6            | 34Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 90       | N/A      | Memory
  04-P1 PMM 1-6             | 0Cel       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Memory
  05-P1 DIMM 7-12           | 34Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 90       | N/A      | Memory
  06-P1 PMM 7-12            | 0Cel       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Memory
  07-VR P1                  | 67Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 115      | SystemBoard
  08-VR P1 Mem 1            | 54Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 115      | SystemBoard
  09-VR P1 Mem 2            | 36Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 115      | SystemBoard
  10-Chipset                | 34Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 100      | N/A      | SystemBoard
  12-Battery Zone           | 27Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 70       | 75       | SystemBoard
  17-LOM Card               | 0Cel       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard
  18-LOM Card Zone          | 25Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 95       | 100      | SystemBoard
  20-mLOM Zone              | 0Cel       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard
  22-PCI 1 Zone             | 25Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 70       | 75       | SystemBoard
  24-PCI 2 Zone             | 25Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 70       | 75       | SystemBoard
  26-PCI 3 Zone             | 25Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 70       | 75       | SystemBoard
  27-PCI 4                  | 0Cel       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard
  28-PCI 4 Zone             | 0Cel       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard
  29-PCI 5                  | 0Cel       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard
  30-PCI 5 Zone             | 0Cel       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard
  31-E-Fuse 1               | 43Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 100      | N/A      | SystemBoard
  32-E-Fuse 2               | 29Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 100      | N/A      | SystemBoard
  33-E-Fuse 3               | 29Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 100      | N/A      | SystemBoard
  34-Stor Batt              | 0Cel       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard
  39-Sys Exhaust 1          | 46Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 85       | 90       | SystemBoard
  40-CPU 1 PkgTmp           | 89Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | CPU
  45-HD Controller          | 0Cel       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard
  46-HD Cntlr Zone          | 0Cel       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard
  47-HD Max                 | 0Cel       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard
  48-Board Inlet            | 0Cel       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard
  25.1-PCI 3-On Board       | 43Cel      | OK       | N/A      | N/A      | N/A      | 75       | 80       | 85       | SystemBoard
  25.2-PCI 3-GPU ASIC       | 50Cel      | OK       | N/A      | N/A      | N/A      | 105      | 110      | 115      | SystemBoard
  25.3-PCI 3-GPU ASIC       | 50Cel      | OK       | N/A      | N/A      | N/A      | 105      | 110      | 115      | SystemBoard
  25.4-PCI 3-Chip Cores     | 48Cel      | OK       | N/A      | N/A      | N/A      | 115      | 120      | 125      | SystemBoard
  21.1-PCI 1-Network contro | 36Cel      | OK       | N/A      | N/A      | N/A      | 95       | 105      | 115      | SystemBoard
  21.2-PCI 1-SFP28 (SFF-840 | 28Cel      | OK       | N/A      | N/A      | N/A      | 73       | 78       | N/A      | SystemBoard
  21.3-PCI 1-SFP28 (SFF-840 | 25Cel      | OK       | N/A      | N/A      | N/A      | 75       | 80       | N/A      | SystemBoard
  23.1-PCI 2-Network contro | 36Cel      | OK       | N/A      | N/A      | N/A      | 95       | 105      | 115      | SystemBoard
  23.2-PCI 2-SFP28 (SFF-840 | 26Cel      | OK       | N/A      | N/A      | N/A      | 73       | 78       | N/A      | SystemBoard
  23.3-PCI 2-SFP28 (SFF-840 | 26Cel      | OK       | N/A      | N/A      | N/A      | 75       | 80       | N/A      | SystemBoard
  Fan 1                     | 37%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard
  Fan 2                     | 37%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard
  Fan 3                     | 37%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard
  Fan 4                     | 37%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard
  Fan 5                     | 37%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard
  Fan 6                     | 37%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard

Chassis 'HPE EL8000t     ' Status
  Sensor                    | Reading    | Health   | LF       | LC       | LNC      | UNC      | UC       | UF       | PhysicalContext

[XXXXXX@welktxefnce-h-pe1util-vm01 HPE_FW]$
```



## Passed MEAKV-240



### MEAKV-241

```log

[XXXXXX@controller-0 ~(keystone_admin)]$ system host-show 1 | grep bm
| bm_ip                  | 2607:F160:10:9249:CE:40A:0:E00A                                         |
| bm_type                | redfish                                                                 |
| bm_username            | XXXXXX                                                                  |
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
| boot_device            | /dev/disk/by-path/pci-0000:c2:00.0-nvme-1                               |
| capabilities           | {'is_max_cpu_configurable': 'configurable', 'stor_function': 'monitor', |
|                        | 'min_cpu_mhz_allowed': 800, 'max_cpu_mhz_allowed': 3500}                |
| clock_synchronization  | ptp                                                                     |
| config_applied         | 43ea95cf-98e5-49d6-93e1-b31067a94a12                                    |
| config_status          | None                                                                    |
| config_target          | 43ea95cf-98e5-49d6-93e1-b31067a94a12                                    |
| console                | ttyS0,115200                                                            |
| created_at             | 2024-07-06T06:03:31.484283+00:00                                        |
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
| max_cpu_mhz_allowed    | 3500                                                                    |
| max_cpu_mhz_configured | 3500                                                                    |
| mgmt_ip                | 2607:f160:10:924a:ce:40a:0:1                                            |
| mgmt_mac               | b4:96:91:b7:d9:f4                                                       |
| operational            | enabled                                                                 |
| personality            | controller                                                              |
| reboot_needed          | False                                                                   |
| reserved               | False                                                                   |
| rootfs_device          | /dev/disk/by-path/pci-0000:c2:00.0-nvme-1                               |
| serialid               | None                                                                    |
| software_load          | 22.12                                                                   |
| subfunction_avail      | available                                                               |
| subfunction_oper       | enabled                                                                 |
| subfunctions           | controller,worker,lowlatency                                            |
| task                   |                                                                         |
| tboot                  |                                                                         |
| ttys_dcd               | False                                                                   |
| updated_at             | 2024-09-06T20:49:04.857038+00:00                                        |
| uptime                 | 404736                                                                  |
| uuid                   | 0cb8ff32-f309-4dd2-86e9-33c7fa475842                                    |
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
