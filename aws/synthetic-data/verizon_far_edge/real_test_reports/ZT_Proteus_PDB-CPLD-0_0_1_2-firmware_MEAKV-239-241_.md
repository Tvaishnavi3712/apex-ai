# ZT Proteus .46 BMC firmware validation
# ZT Proteus BIOS .23
# 1/16/24 James Patchett

## Target Controller rchltxib-c000000-003
Controller-0 iLO 2607:f160:a:d02e:cd:fe0::8006 
Controller-1 iLO 2607:f160:a:d02e:cd:fe0::8007
Worker-0 iLO 2607:f160:a:d02e:cd:fe0::8008 
OAM 2607:f160:0:3049:cd:290:0:10

## Target Subcloud welktxef-d931856-008
OAM: 2607:f160:10:80b1:ce:40a:0:f408
BMC: 2607:f160:10:80b1:ce:40a:0:e008

ipmitool -I lanplus -U XXXXXX -P XXXXXX -H 2607:f160:10:80b1:ce:40a:0:e008 sol activate

### Subcloud Readyness Information

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ system show
+------------------------+--------------------------------------+
| Property               | Value                                |
+------------------------+--------------------------------------+
| contact                | None                                 |
| created_at             | 2024-01-18T18:53:10.717875+00:00     |
| description            | None                                 |
| distributed_cloud_role | subcloud                             |
| https_enabled          | True                                 |
| latitude               | None                                 |
| location               | None                                 |
| longitude              | None                                 |
| name                   | welktxef-d931856-008                 |
| region_name            | welktxef-d931856-008                 |
| sdn_enabled            | False                                |
| security_feature       | spectre_meltdown_v1                  |
| service_project_name   | services                             |
| shared_services        | []                                   |
| software_version       | 21.12                                |
| system_mode            | simplex                              |
| system_type            | All-in-one                           |
| timezone               | UTC                                  |
| updated_at             | 2024-01-29T20:35:21.200685+00:00     |
| uuid                   | f00ecd76-d5a1-4e2e-8797-e08691fefbec |
| vswitch_type           | none                                 |
+------------------------+--------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ sw-patch query
      Patch ID         RR  Release  Patch State
=====================  ==  =======  ===========
WRCP_21.12_PATCH_0001  Y    21.12    Committed
WRCP_21.12_PATCH_0002  Y    21.12    Committed
WRCP_21.12_PATCH_0003  Y    21.12    Committed
WRCP_21.12_PATCH_0004  Y    21.12    Committed
WRCP_21.12_PATCH_0005  Y    21.12    Committed
WRCP_21.12_PATCH_0006  Y    21.12    Committed
WRCP_21.12_PATCH_0007  Y    21.12    Committed
WRCP_21.12_PATCH_0008  Y    21.12    Committed
WRCP_21.12_PATCH_0009  Y    21.12    Committed
WRCP_21.12_PATCH_0010  N    21.12    Committed

[XXXXXX@controller-0 ~(keystone_admin)]$ system application-list
+--------------------------+----------+-----------------------------------+-----------------------+----------+--------------+
| application              | version  | manifest name                     | manifest file         | status   | progress     |
+--------------------------+----------+-----------------------------------+-----------------------+----------+--------------+
| cert-manager             | 21.12-28 | cert-manager-manifest             | certmanager-manifest. | applied  | Application  |
|                          |          |                                   | yaml                  |          | update from  |
|                          |          |                                   |                       |          | version 21.  |
|                          |          |                                   |                       |          | 05-17 to     |
|                          |          |                                   |                       |          | version 21.  |
|                          |          |                                   |                       |          | 12-28        |
|                          |          |                                   |                       |          | completed.   |
|                          |          |                                   |                       |          |              |
| metrics-server           | 21.12-9  | metrics-server-manifest           | metrics-              | applied  | Application  |
|                          |          |                                   | server_manifest.yaml  |          | update from  |
|                          |          |                                   |                       |          | version 21.  |
|                          |          |                                   |                       |          | 05-6 to      |
|                          |          |                                   |                       |          | version 21.  |
|                          |          |                                   |                       |          | 12-9         |
|                          |          |                                   |                       |          | completed.   |
|                          |          |                                   |                       |          |              |
| nginx-ingress-controller | 21.12-18 | nginx-ingress-controller-manifest | nginx_ingress_control | applied  | Application  |
|                          |          |                                   | ler_manifest.yaml     |          | update from  |
|                          |          |                                   |                       |          | version 21.  |
|                          |          |                                   |                       |          | 05-16 to     |
|                          |          |                                   |                       |          | version 21.  |
|                          |          |                                   |                       |          | 12-18        |
|                          |          |                                   |                       |          | completed.   |
|                          |          |                                   |                       |          |              |
| oidc-auth-apps           | 21.12-61 | oidc-auth-manifest                | manifest.yaml         | applied  | Application  |
|                          |          |                                   |                       |          | update from  |
|                          |          |                                   |                       |          | version 21.  |
|                          |          |                                   |                       |          | 05-44 to     |
|                          |          |                                   |                       |          | version 21.  |
|                          |          |                                   |                       |          | 12-61        |
|                          |          |                                   |                       |          | completed.   |
|                          |          |                                   |                       |          |              |
| platform-integ-apps      | 21.12-46 | platform-integration-manifest     | manifest.yaml         | applied  | Application  |
|                          |          |                                   |                       |          | update from  |
|                          |          |                                   |                       |          | version 21.  |
|                          |          |                                   |                       |          | 05-30 to     |
|                          |          |                                   |                       |          | version 21.  |
|                          |          |                                   |                       |          | 12-46        |
|                          |          |                                   |                       |          | completed.   |
|                          |          |                                   |                       |          |              |
| rook-ceph-apps           | 1.0-5    | rook-ceph-manifest                | manifest.yaml         | uploaded | completed    |
+--------------------------+----------+-----------------------------------+-----------------------+----------+--------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ fm alarm-list

[XXXXXX@controller-0 ~(keystone_admin)]$

```

### MEAKV-239
### Subcloud 

Verify that distributed region controller-0 host has no BMC information after current deployment. If that is the case, manually provision BMC for host. For example:

```sh 
system host-show 1 | grep bm
system host-update controller-0 bm_ip=2607:f160:10:9073:ce:406:0:1000 bm_type=redfish bm_username=XXXXXX bm_password=XXXXXX
system host-show 1 | grep bm
```

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ system host-show 1 | grep bm
| bm_ip                 | None                                                                 |
| bm_type               | none                                                                 |
| bm_username           | None                                                                 |
[XXXXXX@controller-0 ~(keystone_admin)]$ system host-update controller-0 bm_ip=2607:f160:10:80b1:ce:40a:0:e008 bm_type=redfish bm_username=XXXXXX bm_password=XXXXXX
+-----------------------+-------------------------------------------+
| Property              | Value                                     |
+-----------------------+-------------------------------------------+
| action                | none                                      |
| administrative        | unlocked                                  |
| availability          | available                                 |
| bm_ip                 | 2607:f160:10:80b1:ce:40a:0:e008           |
| bm_type               | redfish                                   |
| bm_username           | XXXXXX                             |
| boot_device           | /dev/disk/by-path/pci-0000:c3:00.0-nvme-1 |
| capabilities          | {u'stor_function': u'monitor'}            |
| clock_synchronization | ntp                                       |
| config_applied        | 2573607a-3a65-45b1-99c6-d331a0c81b9b      |
| config_status         | None                                      |
| config_target         | 2573607a-3a65-45b1-99c6-d331a0c81b9b      |
| console               | ttyS0,115200                              |
| created_at            | 2024-01-18T18:55:16.372532+00:00          |
| device_image_update   | None                                      |
| hostname              | controller-0                              |
| id                    | 1                                         |
| install_output        | text                                      |
| install_state         | None                                      |
| install_state_info    | None                                      |
| inv_state             | inventoried                               |
| invprovision          | provisioned                               |
| location              | {}                                        |
| mgmt_ip               | 2607:f160:10:80bb:ce:40a:0:1              |
| mgmt_mac              | b4:96:91:eb:94:54                         |
| operational           | enabled                                   |
| personality           | controller                                |
| reboot_needed         | False                                     |
| reserved              | False                                     |
| rootfs_device         | /dev/disk/by-path/pci-0000:c3:00.0-nvme-1 |
| serialid              | None                                      |
| software_load         | 21.12                                     |
| subfunction_avail     | available                                 |
| subfunction_oper      | enabled                                   |
| subfunctions          | controller,worker,lowlatency              |
| task                  |                                           |
| tboot                 | false                                     |
| ttys_dcd              | None                                      |
| updated_at            | 2024-01-30T01:29:17.275343+00:00          |
| uptime                | 14399                                     |
| uuid                  | 51ab64cd-b168-4077-b755-b013746564d9      |
| vim_progress_status   | services-enabled                          |
+-----------------------+-------------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ system host-show 1 | grep bm
| bm_ip                 | 2607:f160:10:80b1:ce:40a:0:e008                                      |
| bm_type               | redfish                                                              |
| bm_username           | XXXXXX                                                        |
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

| bm_ip                 | 2607:f160:10:80b1:ce:40a:0:e008                                      |
| bm_type               | redfish                                                              |
| bm_username           | XXXXXX                                                        |
[XXXXXX@controller-0 ~(keystone_admin)]$ system host-sensor-list 1
+--------------------------------------+------------+-------------+---------+--------+
| uuid                                 | name       | sensortype  | state   | status |
+--------------------------------------+------------+-------------+---------+--------+
| 3435a3e4-d3a8-4e81-8069-353189e1e55b | ADM1278    | power       | enabled | ok     |
| 89323161-5c29-4b44-8a17-fd2312a4b831 | CPU0DDR_AB | voltage     | enabled | ok     |
|                                      | C_1.2V     |             |         |        |
|                                      |            |             |         |        |
| be7db199-1bf0-40b3-8545-fa17bf8375fe | CPU0DDR_DE | voltage     | enabled | ok     |
|                                      | F_1.2V     |             |         |        |
|                                      |            |             |         |        |
| 1bae9cd6-22d7-4754-9220-2a3039aaaf5d | CPU_0_DIMM | temperature | enabled | ok     |
|                                      | _A0        |             |         |        |
|                                      |            |             |         |        |
| fb792c22-7742-41f5-ae58-2d43068babde | CPU_0_DIMM | temperature | enabled | ok     |
|                                      | _B0        |             |         |        |
|                                      |            |             |         |        |
| c2b408e6-d399-464c-9696-2d2a45d9afc5 | CPU_0_DIMM | temperature | enabled | ok     |
|                                      | _C0        |             |         |        |
|                                      |            |             |         |        |
| 2180e752-f446-4668-8d70-9d70facbe1c9 | CPU_0_DIMM | temperature | enabled | ok     |
|                                      | _D0        |             |         |        |
|                                      |            |             |         |        |
| 566e95e7-8880-4280-bba3-cff7d861c047 | CPU_0_DIMM | temperature | enabled | ok     |
|                                      | _E0        |             |         |        |
|                                      |            |             |         |        |
| 81ff290e-50cb-4533-9ec0-34beaf4aca52 | CPU_0_DIMM | temperature | enabled | ok     |
|                                      | _F0        |             |         |        |
|                                      |            |             |         |        |
| fcaaa23c-e6a8-4d5c-828a-25fa34c2d016 | CPU_0_DIMM | temperature | enabled | ok     |
|                                      | _G0        |             |         |        |
|                                      |            |             |         |        |
| c7dc1755-bedb-471f-804b-81d70b1d17a2 | CPU_0_DIMM | temperature | enabled | ok     |
|                                      | _H0        |             |         |        |
|                                      |            |             |         |        |
| 00d8eea5-fb0b-40d9-9a28-b413bb5aebdc | CPU_0_DTS_ | temperature | enabled | ok     |
|                                      | TEMP       |             |         |        |
|                                      |            |             |         |        |
| 3bb6ac95-af7f-445b-9413-e7915028061e | CPU_0_MARG | temperature | enabled | ok     |
|                                      | IN         |             |         |        |
|                                      |            |             |         |        |
| 4500a7fd-d66a-406a-a6e1-a52eba4efca2 | CPU_0_PROC | temperature | enabled | ok     |
|                                      | HOT        |             |         |        |
|                                      |            |             |         |        |
| 9a9df2dd-f2b8-47da-8517-5c73a725939b | CPU_0_TEMP | temperature | enabled | ok     |
| 45399432-3390-4919-9984-d40954dfcf2b | CPU_0_Vcor | voltage     | enabled | ok     |
|                                      | e          |             |         |        |
|                                      |            |             |         |        |
| 5a8c0cad-9643-4d23-a8c8-f5e1c47d89a2 | DIMM_VRABC | temperature | enabled | ok     |
|                                      | D_TEMP     |             |         |        |
|                                      |            |             |         |        |
| 47b51677-8eaa-417a-80d4-a8894a76f980 | DIMM_VREFG | temperature | enabled | ok     |
|                                      | H_TEMP     |             |         |        |
|                                      |            |             |         |        |
| 21b8cfd7-56ea-487b-8ca0-2b7729b1db61 | INLET_TEMP | temperature | enabled | ok     |
|                                      | _L         |             |         |        |
|                                      |            |             |         |        |
| 9abe33c8-10e0-42cf-a373-92983a6c4a78 | INLET_TEMP | temperature | enabled | ok     |
|                                      | _MAX       |             |         |        |
|                                      |            |             |         |        |
| 2065e4e6-a6eb-4af4-bb8f-73769ab5cf85 | INLET_TEMP | temperature | enabled | ok     |
|                                      | _R         |             |         |        |
|                                      |            |             |         |        |
| dae19b51-651f-4f04-b2dc-ffc9c6764060 | MAX_DIMM_T | temperature | enabled | ok     |
|                                      | EMP        |             |         |        |
|                                      |            |             |         |        |
| 7edffac0-d744-48b0-b4d9-b88e06f713f2 | MB_HSC_TEM | temperature | enabled | ok     |
|                                      | P          |             |         |        |
|                                      |            |             |         |        |
| 927282f5-eec1-4cb8-9698-e0f544b06f6a | OUTLET_TEM | temperature | enabled | ok     |
|                                      | P_L        |             |         |        |
|                                      |            |             |         |        |
| ed3f88c4-8d4c-48d4-ac1e-c7006f261b52 | OUTLET_TEM | temperature | enabled | ok     |
|                                      | P_MAX      |             |         |        |
|                                      |            |             |         |        |
| d12d4ab6-5eba-410b-9603-ccfb24b631d3 | OUTLET_TEM | temperature | enabled | ok     |
|                                      | P_R        |             |         |        |
|                                      |            |             |         |        |
| 443dbf0c-3645-4c27-938b-ffca8dd84bbb | PML_EAST_T | temperature | enabled | ok     |
|                                      | EMP        |             |         |        |
|                                      |            |             |         |        |
| 25e611fd-894a-4269-8696-66afa35d3908 | PML_LOCAL_ | temperature | enabled | ok     |
|                                      | TEMP       |             |         |        |
|                                      |            |             |         |        |
| 6529eba4-a08d-4805-984a-dfffe183035c | PML_VDD_TE | temperature | enabled | ok     |
|                                      | MP         |             |         |        |
|                                      |            |             |         |        |
| e3bdbfaa-ae79-411d-b4c0-472f92c4cf7d | PML_WEST_T | temperature | enabled | ok     |
|                                      | EMP        |             |         |        |
|                                      |            |             |         |        |
| ee21b446-61e8-4642-b748-580519a406e6 | PSU_1_FAN  | fan         | enabled | ok     |
| 0f10f89a-9702-473a-913f-5773d1eb1c64 | PSU_1_TEMP | temperature | enabled | ok     |
|                                      | _1         |             |         |        |
|                                      |            |             |         |        |
| 3f6bb3f0-75ef-4c12-8f59-63af477b220f | PSU_1_TEMP | temperature | enabled | ok     |
|                                      | _2         |             |         |        |
|                                      |            |             |         |        |
| 7c71a362-1f97-44c0-a338-217f4911d123 | PSU_2_FAN  | fan         | enabled | ok     |
| 397bc911-b27d-4c14-993e-b7ed0d51b0bc | PSU_2_TEMP | temperature | enabled | ok     |
|                                      | _1         |             |         |        |
|                                      |            |             |         |        |
| 9478797b-4cc6-4dd8-a597-e33ae00aece8 | PSU_2_TEMP | temperature | enabled | ok     |
|                                      | _2         |             |         |        |
|                                      |            |             |         |        |
| 0f77cca4-a003-4606-be80-1e0faac03f6a | Power      | power       | enabled | ok     |
|                                      | Supply Bay |             |         |        |
|                                      |            |             |         |        |
| 87378162-b482-41ec-aef0-fe35426754bc | RTC_Voltag | voltage     | enabled | ok     |
|                                      | e          |             |         |        |
|                                      |            |             |         |        |
| 1674146f-0076-4b3f-8149-d78a368169cc | SC_1_E810  | temperature | enabled | ok     |
| a6cadc28-d8b2-4f75-8410-b8224e219ec7 | SC_2_E810  | temperature | enabled | ok     |
| e1d75f9b-b4c2-4ba1-8bbc-64090784c7e9 | SSD_0_TEMP | temperature | enabled | ok     |
| a77937e3-2aa7-481d-9663-1c99bb961168 | SSD_1_TEMP | temperature | enabled | ok     |
| c46a41e8-135a-46a7-acc7-7e8f8a5bc777 | SYS_FAN_1A | fan         | enabled | ok     |
| ef04def5-2feb-44ad-9766-7899db87e5be | SYS_FAN_1B | fan         | enabled | ok     |
| 879627a6-b955-49e3-8f83-74d1117dc38b | SYS_FAN_2A | fan         | enabled | ok     |
| 108de965-1c91-4c29-999c-aa8ce1bbf846 | SYS_FAN_2B | fan         | enabled | ok     |
| 6dc16ef3-4a5a-4605-ae42-2401d4ac69d8 | SYS_PCH_TE | temperature | enabled | ok     |
|                                      | MP         |             |         |        |
|                                      |            |             |         |        |
| 8948bbf8-c767-411a-a293-1325b53ed0ee | SYS_V1.05  | voltage     | enabled | ok     |
| 2d16e3a7-71c7-4886-b926-2a9155277b2d | SYS_V12    | voltage     | enabled | ok     |
| 5ea3c91b-760d-4128-83d7-fef79649561e | SYS_V3.3   | voltage     | enabled | ok     |
| 2675ace0-18b6-4bcc-bc8d-2c96d5358d5a | SYS_V5     | voltage     | enabled | ok     |
+--------------------------------------+------------+-------------+---------+--------+
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
| bm_ip                 | 2607:f160:10:80b1:ce:40a:0:e008                                      |
| bm_type               | redfish                                                              |
| bm_username           | XXXXXX                                                        |
[XXXXXX@controller-0 ~(keystone_admin)]$ system host-update controller-0 bm_type=none
+-----------------------+-------------------------------------------+
| Property              | Value                                     |
+-----------------------+-------------------------------------------+
| action                | none                                      |
| administrative        | unlocked                                  |
| availability          | available                                 |
| bm_ip                 | None                                      |
| bm_type               | none                                      |
| bm_username           | None                                      |
| boot_device           | /dev/disk/by-path/pci-0000:c3:00.0-nvme-1 |
| capabilities          | {u'stor_function': u'monitor'}            |
| clock_synchronization | ntp                                       |
| config_applied        | 2573607a-3a65-45b1-99c6-d331a0c81b9b      |
| config_status         | None                                      |
| config_target         | 2573607a-3a65-45b1-99c6-d331a0c81b9b      |
| console               | ttyS0,115200                              |
| created_at            | 2024-01-18T18:55:16.372532+00:00          |
| device_image_update   | None                                      |
| hostname              | controller-0                              |
| id                    | 1                                         |
| install_output        | text                                      |
| install_state         | None                                      |
| install_state_info    | None                                      |
| inv_state             | inventoried                               |
| invprovision          | provisioned                               |
| location              | {}                                        |
| mgmt_ip               | 2607:f160:10:80bb:ce:40a:0:1              |
| mgmt_mac              | b4:96:91:eb:94:54                         |
| operational           | enabled                                   |
| personality           | controller                                |
| reboot_needed         | False                                     |
| reserved              | False                                     |
| rootfs_device         | /dev/disk/by-path/pci-0000:c3:00.0-nvme-1 |
| serialid              | None                                      |
| software_load         | 21.12                                     |
| subfunction_avail     | available                                 |
| subfunction_oper      | enabled                                   |
| subfunctions          | controller,worker,lowlatency              |
| task                  |                                           |
| tboot                 | false                                     |
| ttys_dcd              | None                                      |
| updated_at            | 2024-01-30T01:33:17.340364+00:00          |
| uptime                | 14779                                     |
| uuid                  | 51ab64cd-b168-4077-b755-b013746564d9      |
| vim_progress_status   | services-enabled                          |
+-----------------------+-------------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ system host-show 1 | grep bm
| bm_ip                 | None                                                                 |
| bm_type               | none                                                                 |
| bm_username           | None                                                                 |
[XXXXXX@controller-0 ~(keystone_admin)]$ system host-sensor-list 1

[XXXXXX@controller-0 ~(keystone_admin)]$
```
