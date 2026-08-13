# ZT Proteus PDB-CPLD 0.0.1.2 Firmware Validation
# ZT Proteus .46 BMC / BIOS .23
# 1/16/24 James Patchett

# Target subclouds RU_12,13 Right and Left side

## Left side Subcloud welktxef-d931887-021
## BMC 0.46 BIOS 0.23
BMC:  2607:f160:10:9249:ce:40a:0:e015
OAM:  2607:f160:10:9249:ce:40a:0:f409

## Subcloud welktxef-d931856-008 Info
```log
XXXXXX@controller-0:~$ source /etc/platform/openrc
[XXXXXX@controller-0 ~(keystone_admin)]$ system show
+------------------------+--------------------------------------+
| Property               | Value                                |
+------------------------+--------------------------------------+
| contact                | None                                 |
| created_at             | 2024-03-07T18:03:00.044462+00:00     |
| description            | None                                 |
| distributed_cloud_role | subcloud                             |
| https_enabled          | True                                 |
| latitude               | None                                 |
| location               | None                                 |
| longitude              | None                                 |
| name                   | welktxef-d931887-021                 |
| region_name            | welktxef-d931887-021                 |
| sdn_enabled            | False                                |
| security_feature       | spectre_meltdown_v1                  |
| service_project_name   | services                             |
| shared_services        | []                                   |
| software_version       | 22.12                                |
| system_mode            | simplex                              |
| system_type            | All-in-one                           |
| timezone               | UTC                                  |
| updated_at             | 2024-03-11T19:05:24.739152+00:00     |
| uuid                   | 23aff978-9c1f-4e92-aca9-97621b54bd8a |
| vswitch_type           | none                                 |
+------------------------+--------------------------------------+
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

[XXXXXX@controller-0 ~(keystone_admin)]$
```

### MEAKV-239
### Subcloud 

Verify that distributed region controller-0 host has no BMC information after current deployment. If that is the case, manually provision BMC for host. For example:

```sh 
system host-show 1 | grep bm
system host-update controller-0 bm_ip=2607:f160:10:9249:ce:40a:0:e015 bm_type=redfish bm_username=XXXXXX bm_password=XXXXXX
system host-show 1 | grep bm
```

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ system host-show 1 | grep bm
system host-update controller-0 bm_ip=2607:f160:10:9249:ce:40a:0:e015 bm_type=redfish bm_username=XXXXXX bm_password=XXXXXX
system host-show 1 | grep bm
| bm_ip                  | None                                                                    |
| bm_type                | none                                                                    |
| bm_username            | None                                                                    |
+------------------------+-------------------------------------------------------------------------+
| Property               | Value                                                                   |
+------------------------+-------------------------------------------------------------------------+
| action                 | none                                                                    |
| administrative         | unlocked                                                                |
| apparmor               | disabled                                                                |
| availability           | available                                                               |
| bm_ip                  | 2607:f160:10:9249:ce:40a:0:e015                                         |
| bm_type                | redfish                                                                 |
| bm_username            | XXXXXX                                                           |
| boot_device            | /dev/disk/by-path/pci-0000:c3:00.0-nvme-1                               |
| capabilities           | {'is_max_cpu_configurable': 'configurable', 'min_cpu_mhz_allowed': 800, |
|                        | 'max_cpu_mhz_allowed': 3500, 'cstates_available': 'C1,C2,POLL',         |
|                        | 'stor_function': 'monitor'}                                             |
| clock_synchronization  | ntp                                                                     |
| config_applied         | 2fc34cc7-a6b4-4c65-9f3e-20b002fdb1d4                                    |
| config_status          | None                                                                    |
| config_target          | 2fc34cc7-a6b4-4c65-9f3e-20b002fdb1d4                                    |
| console                | ttyS0,115200                                                            |
| created_at             | 2024-03-07T18:05:01.227874+00:00                                        |
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
| max_cpu_mhz_configured | None                                                                    |
| mgmt_ip                | 2607:f160:10:809f:ce:40a:0:1                                            |
| mgmt_mac               | b4:96:91:b5:5e:54                                                       |
| operational            | enabled                                                                 |
| personality            | controller                                                              |
| reboot_needed          | False                                                                   |
| reserved               | False                                                                   |
| rootfs_device          | /dev/disk/by-path/pci-0000:c3:00.0-nvme-1                               |
| serialid               | None                                                                    |
| software_load          | 22.12                                                                   |
| subfunction_avail      | available                                                               |
| subfunction_oper       | enabled                                                                 |
| subfunctions           | controller,worker,lowlatency                                            |
| task                   |                                                                         |
| tboot                  |                                                                         |
| ttys_dcd               | False                                                                   |
| updated_at             | 2024-03-13T23:28:51.753405+00:00                                        |
| uptime                 | 76364                                                                   |
| uuid                   | 70ed4746-2443-4a84-b78e-cb3634c3c17f                                    |
| vim_progress_status    | services-enabled                                                        |
+------------------------+-------------------------------------------------------------------------+
| bm_ip                  | 2607:f160:10:9249:ce:40a:0:e015                                         |
| bm_type                | redfish                                                                 |
| bm_username            | XXXXXX                                                           |
[XXXXXX@controller-0 ~(keystone_admin)]$
```


### MEAKV-240
### Subcloud

Verify that host has BMC information provisioned, then display host sensor status. 
Verify that host sensor list is displayed, all appropriate sensors are listed, and associated status is provided (it will take a while for data to become available after configuring BMC).


```sh
system host-show 1 | grep bm
system host-sensor-list 1
```

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ system host-show 1 | grep bm
| bm_ip                  | 2607:f160:10:9249:ce:40a:0:e015                                         |
| bm_type                | redfish                                                                 |
| bm_username            | XXXXXX                                                           |
[XXXXXX@controller-0 ~(keystone_admin)]$ system host-sensor-list 1
+--------------------------------------+------------------+-------------+---------+--------+
| uuid                                 | name             | sensortype  | state   | status |
+--------------------------------------+------------------+-------------+---------+--------+
| a9da3786-7b12-439b-a55d-2128752eed6b | ADM1278          | power       | enabled | ok     |
| 9bee2824-193c-4c3a-90fa-2febd3863eb6 | CPU0DDR_ABC_1.2V | voltage     | enabled | ok     |
| b082c2c8-4ab2-4190-ae0a-0b2ca554efd1 | CPU0DDR_DEF_1.2V | voltage     | enabled | ok     |
| 3c01a316-3a11-4294-8779-34ed41614df4 | CPU_0_DIMM_A0    | temperature | enabled | ok     |
| 4e5ef96e-d7c9-4be9-849d-8f1715d0ae64 | CPU_0_DIMM_B0    | temperature | enabled | ok     |
| e32973f7-ed4c-4eb1-882c-508ae46c53d9 | CPU_0_DIMM_C0    | temperature | enabled | ok     |
| 64214511-52b5-445b-a745-d8f4f7fb30be | CPU_0_DIMM_D0    | temperature | enabled | ok     |
| b1c2ca4c-dde9-43ec-a613-7b52762eadca | CPU_0_DIMM_E0    | temperature | enabled | ok     |
| 4503ccc5-260b-4f83-b929-f79f02633452 | CPU_0_DIMM_F0    | temperature | enabled | ok     |
| 28bf360d-f84f-4fe2-a62a-bb66883b2a70 | CPU_0_DIMM_G0    | temperature | enabled | ok     |
| bda5c746-fc38-4c4b-a821-8376c20a8220 | CPU_0_DIMM_H0    | temperature | enabled | ok     |
| 105cbd74-510c-4f53-8b04-3718ff2aa91c | CPU_0_DTS_TEMP   | temperature | enabled | ok     |
| 4f2a45cb-ddd7-494e-aff7-ce9de192bbe4 | CPU_0_MARGIN     | temperature | enabled | ok     |
| a37e0af2-16b1-450e-89db-67d4d8db02e5 | CPU_0_TEMP       | temperature | enabled | ok     |
| 4c1efbc1-61d2-4ba3-ae59-1f4ca793b7f7 | CPU_0_Vcore      | voltage     | enabled | ok     |
| 019db39b-ef33-4023-985d-859f61944ca3 | DIMM_VRABCD_TEMP | temperature | enabled | ok     |
| 0400ef0b-bb24-4c09-a827-cb699ab15ae9 | DIMM_VREFGH_TEMP | temperature | enabled | ok     |
| 607a89b1-fecf-432c-8ee4-c76a47346d8c | INLET_TEMP_L     | temperature | enabled | ok     |
| fa63498f-6529-4c43-919f-b56a9584f8b4 | INLET_TEMP_MAX   | temperature | enabled | ok     |
| 7989740b-2dfd-4e02-a0a9-a8c1d63827ec | INLET_TEMP_R     | temperature | enabled | ok     |
| 4ecaf290-8479-4622-96cd-7da9bef378bf | MAX_DIMM_TEMP    | temperature | enabled | ok     |
| 3dd69a83-f0a8-4255-a0c7-f4238321026e | MB_HSC_TEMP      | temperature | enabled | ok     |
| a47fe143-24b2-4fac-94c5-e71411662cda | OUTLET_TEMP_L    | temperature | enabled | ok     |
| 6256f794-f9fd-4589-be77-9ca8478d7156 | OUTLET_TEMP_MAX  | temperature | enabled | ok     |
| 33cfbce0-5249-4b04-a66f-4c488972231e | OUTLET_TEMP_R    | temperature | enabled | ok     |
| 0bc5375e-1006-4885-b5ce-7d829611ad3d | PML_EAST_TEMP    | temperature | enabled | ok     |
| a8826a1c-618f-46bb-aac1-deeb5f11c352 | PML_LOCAL_TEMP   | temperature | enabled | ok     |
| 38da129b-366d-4894-a151-74c73052e05b | PML_VDD_TEMP     | temperature | enabled | ok     |
| 3ca8fcba-b2ed-402e-af33-72ba4c576e79 | PML_WEST_TEMP    | temperature | enabled | ok     |
| b71dcf80-9304-4e31-9712-2d13dd2af47d | PSU_1_FAN        | fan         | enabled | ok     |
| c5cd65be-d1b0-4bf1-9954-917f0564b87a | PSU_1_TEMP_1     | temperature | enabled | ok     |
| ee6166c6-43cc-4b9a-b9f2-2cb3e9d7a4e7 | PSU_1_TEMP_2     | temperature | enabled | ok     |
| f2c77e9b-19c8-467f-b435-dcae7d52d3c5 | PSU_2_FAN        | fan         | enabled | ok     |
| f44779cd-cac8-4d5b-9c98-7890fc36ed2c | PSU_2_TEMP_1     | temperature | enabled | ok     |
| 11913ceb-cbf0-4c48-a939-53d926468d68 | PSU_2_TEMP_2     | temperature | enabled | ok     |
| 08d03da6-11dc-4320-b856-58ef6238461f | Power Supply Bay | power       | enabled | ok     |
| d6b15cad-6a7e-4a19-8228-6d3290bb444f | RTC_Voltage      | voltage     | enabled | ok     |
| 36b4c634-5cd3-45a9-ae59-61626e007373 | SC_1_E810        | temperature | enabled | ok     |
| cf797e18-3b32-406a-b3a5-d1c0cfc73784 | SC_2_E810        | temperature | enabled | ok     |
| 36639749-b954-48a4-97b5-48c050becb2e | SSD_0_TEMP       | temperature | enabled | ok     |
| 4ab1a5cc-b227-4eb9-b2e9-557c19dfa722 | SSD_1_TEMP       | temperature | enabled | ok     |
| c54b9087-2943-4f3c-9d33-af8acab5cfb8 | SYS_FAN_1A       | fan         | enabled | ok     |
| 5a11ae9f-47f0-4026-8489-aeadc7c9f658 | SYS_FAN_1B       | fan         | enabled | ok     |
| 9bdbc8d0-3950-4c7d-be98-f75c98b2512b | SYS_FAN_2A       | fan         | enabled | ok     |
| c7456a19-d474-475a-a7aa-b4bb6f702da9 | SYS_FAN_2B       | fan         | enabled | ok     |
| cf507efa-c021-4b17-b55c-32e96fa33068 | SYS_PCH_TEMP     | temperature | enabled | ok     |
| bceeeb9b-2c76-4b58-8727-be5b54b18a6e | SYS_V1.05        | voltage     | enabled | ok     |
| a2a81292-4409-4523-aa8d-f876637fda89 | SYS_V12          | voltage     | enabled | ok     |
| ae2aff3e-bb6f-4dc7-8f01-729e059b6e3d | SYS_V3.3         | voltage     | enabled | ok     |
| bb60c5d1-7477-4b4a-b3b6-0eb4627a69f7 | SYS_V5           | voltage     | enabled | ok     |
+--------------------------------------+------------------+-------------+---------+--------+
[XXXXXX@controller-0 ~(keystone_admin)]$
```

### MEAKV-241
### Subcloud

Verify that host has BMC information provisioned, remove configuration, verify removed. 
Verify BMC provisioning is removed, and that the host sensor list is empty.




```sh
system host-show 1 | grep bm
system host-update controller-0 bm_type=none
system host-show 1 | grep bm
system host-sensor-list 1
```


```log
[XXXXXX@controller-0 ~(keystone_admin)]$ system host-show 1 | grep bm
system host-update controller-0 bm_type=none
system host-show 1 | grep bm
system host-sensor-list 1
| bm_ip                  | 2607:f160:10:9249:ce:40a:0:e015                                         |
| bm_type                | redfish                                                                 |
| bm_username            | XXXXXX                                                           |
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
| boot_device            | /dev/disk/by-path/pci-0000:c3:00.0-nvme-1                               |
| capabilities           | {'is_max_cpu_configurable': 'configurable', 'min_cpu_mhz_allowed': 800, |
|                        | 'max_cpu_mhz_allowed': 3500, 'cstates_available': 'C1,C2,POLL',         |
|                        | 'stor_function': 'monitor'}                                             |
| clock_synchronization  | ntp                                                                     |
| config_applied         | 2fc34cc7-a6b4-4c65-9f3e-20b002fdb1d4                                    |
| config_status          | None                                                                    |
| config_target          | 2fc34cc7-a6b4-4c65-9f3e-20b002fdb1d4                                    |
| console                | ttyS0,115200                                                            |
| created_at             | 2024-03-07T18:05:01.227874+00:00                                        |
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
| max_cpu_mhz_configured | None                                                                    |
| mgmt_ip                | 2607:f160:10:809f:ce:40a:0:1                                            |
| mgmt_mac               | b4:96:91:b5:5e:54                                                       |
| operational            | enabled                                                                 |
| personality            | controller                                                              |
| reboot_needed          | False                                                                   |
| reserved               | False                                                                   |
| rootfs_device          | /dev/disk/by-path/pci-0000:c3:00.0-nvme-1                               |
| serialid               | None                                                                    |
| software_load          | 22.12                                                                   |
| subfunction_avail      | available                                                               |
| subfunction_oper       | enabled                                                                 |
| subfunctions           | controller,worker,lowlatency                                            |
| task                   |                                                                         |
| tboot                  |                                                                         |
| ttys_dcd               | False                                                                   |
| updated_at             | 2024-03-13T23:29:25.485184+00:00                                        |
| uptime                 | 76364                                                                   |
| uuid                   | 70ed4746-2443-4a84-b78e-cb3634c3c17f                                    |
| vim_progress_status    | services-enabled                                                        |
+------------------------+-------------------------------------------------------------------------+
| bm_ip                  | None                                                                    |
| bm_type                | none                                                                    |
| bm_username            | None                                                                    |

[XXXXXX@controller-0 ~(keystone_admin)]$
```
