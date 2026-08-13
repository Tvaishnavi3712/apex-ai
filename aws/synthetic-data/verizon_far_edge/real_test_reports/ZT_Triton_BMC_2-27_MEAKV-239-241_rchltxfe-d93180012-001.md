# ZT Triton 2.27 BMC firmware validation
# MEAKV-239-240
# 12/13/23 James Patchett

## Target Controller rchltxib-c000000-003 CR-3 (Richardson infrastructure System)
OAM: 2607:f160:0:3049:cd:290:0:10

## Subcloud rchltxfe-d93180012-001 (VCP-fe Infrastructure)
OAM: 2607:f160:10:9073:ce:40a:0:f400
ILO: 2607:f160:10:9073:ce:406:0:1000

ipmitool -I lanplus -U XXXXXX -P XXXXXX -H 2607:f160:10:9073:ce:406:0:1000 sol activate


### Subcloud Readyness Information

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ system show
+------------------------+--------------------------------------+
| Property               | Value                                |
+------------------------+--------------------------------------+
| contact                | None                                 |
| created_at             | 2023-12-13T16:29:19.953081+00:00     |
| description            | None                                 |
| distributed_cloud_role | subcloud                             |
| https_enabled          | True                                 |
| latitude               | None                                 |
| location               | None                                 |
| longitude              | None                                 |
| name                   | rchltxfe-d93180012-001               |
| region_name            | rchltxfe-d93180012-001               |
| sdn_enabled            | False                                |
| security_feature       | spectre_meltdown_v1                  |
| service_project_name   | services                             |
| shared_services        | []                                   |
| software_version       | 21.12                                |
| system_mode            | simplex                              |
| system_type            | All-in-one                           |
| timezone               | UTC                                  |
| updated_at             | 2023-12-13T17:41:31.309394+00:00     |
| uuid                   | 4b4996b9-b5bd-447f-ab81-f2a1f6b8dfda |
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
+--------------------------+----------+-----------------------------------+----------------------------------------+----------+-----------+
| application              | version  | manifest name                     | manifest file                          | status   | progress  |
+--------------------------+----------+-----------------------------------+----------------------------------------+----------+-----------+
| cert-manager             | 21.12-28 | cert-manager-manifest             | certmanager-manifest.yaml              | applied  | completed |
| metrics-server           | 21.12-9  | metrics-server-manifest           | metrics-server_manifest.yaml           | applied  | completed |
| nginx-ingress-controller | 21.12-18 | nginx-ingress-controller-manifest | nginx_ingress_controller_manifest.yaml | applied  | completed |
| oidc-auth-apps           | 21.12-61 | oidc-auth-manifest                | manifest.yaml                          | applied  | completed |
| platform-integ-apps      | 21.12-46 | platform-integration-manifest     | manifest.yaml                          | applied  | completed |
| rook-ceph-apps           | 1.0-14   | rook-ceph-manifest                | manifest.yaml                          | uploaded | completed |
+--------------------------+----------+-----------------------------------+----------------------------------------+----------+-----------+
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
[XXXXXX@controller-0 ~(keystone_admin)]$

[XXXXXX@controller-0 ~(keystone_admin)]$ system host-update controller-0 bm_ip=2607:f160:10:9073:ce:406:0:1000 bm_type=redfish bm_username=K8Sctl bm_password=XXXXXX
+-----------------------+-------------------------------------------+
| Property              | Value                                     |
+-----------------------+-------------------------------------------+
| action                | none                                      |
| administrative        | unlocked                                  |
| availability          | available                                 |
| bm_ip                 | 2607:f160:10:9073:ce:406:0:1000           |
| bm_type               | redfish                                   |
| bm_username           | K8Sctl                                    |
| boot_device           | /dev/disk/by-path/pci-0000:b4:00.0-nvme-1 |
| capabilities          | {u'stor_function': u'monitor'}            |
| clock_synchronization | ntp                                       |
| config_applied        | 41386ba8-c2a0-4ccb-8cfe-2d7f83a05379      |
| config_status         | None                                      |
| config_target         | 41386ba8-c2a0-4ccb-8cfe-2d7f83a05379      |
| console               | ttyS0,115200                              |
| created_at            | 2023-12-13T16:31:53.708705+00:00          |
| device_image_update   | None                                      |
| hostname              | controller-0                              |
| id                    | 1                                         |
| install_output        | text                                      |
| install_state         | None                                      |
| install_state_info    | None                                      |
| inv_state             | inventoried                               |
| invprovision          | provisioned                               |
| location              | {}                                        |
| mgmt_ip               | 2607:f160:10:907b:ce:40a:0:1              |
| mgmt_mac              | 68:05:ca:9a:eb:78                         |
| operational           | enabled                                   |
| personality           | controller                                |
| reboot_needed         | False                                     |
| reserved              | False                                     |
| rootfs_device         | /dev/disk/by-path/pci-0000:b4:00.0-nvme-1 |
| serialid              | None                                      |
| software_load         | 21.12                                     |
| subfunction_avail     | available                                 |
| subfunction_oper      | enabled                                   |
| subfunctions          | controller,worker,lowlatency              |
| task                  |                                           |
| tboot                 | false                                     |
| ttys_dcd              | None                                      |
| updated_at            | 2023-12-13T18:53:58.356046+00:00          |
| uptime                | 6242                                      |
| uuid                  | d4a46b99-89dd-46e6-8273-b2fe8f4e8afd      |
| vim_progress_status   | services-enabled                          |
+-----------------------+-------------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$

[XXXXXX@controller-0 ~(keystone_admin)]$ system host-show 1 | grep bm
| bm_ip                 | 2607:f160:10:9073:ce:406:0:1000                                      |
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

| bm_ip                 | 2607:f160:10:9073:ce:406:0:1000                                      |
| bm_type               | redfish                                                              |
| bm_username           | XXXXXX                                                        |
[XXXXXX@controller-0 ~(keystone_admin)]$ system host-sensor-list 1
+--------------------------------------+------------------+-------------+---------+---------+
| uuid                                 | name             | sensortype  | state   | status  |
+--------------------------------------+------------------+-------------+---------+---------+
| 3e419bb1-6937-4570-8dff-a54e0fa7c636 | CPU0DDR_ABC_1.2V | voltage     | enabled | ok      |
| bfbe7ce6-5f98-4dcd-8932-d6dc1d5a3d81 | CPU0DDR_DEF_1.2V | voltage     | enabled | ok      |
| f3bf52b8-6a76-4ab9-b738-8658874b79c3 | CPU_0_DIMM_A0    | temperature | enabled | ok      |
| 2eabf32f-c6fb-4f0e-903c-c0f01d64b8a8 | CPU_0_DIMM_B0    | temperature | enabled | ok      |
| 68a633e0-dc61-42fd-bfc0-98e23f18328a | CPU_0_DIMM_C0    | temperature | enabled | ok      |
| 72083a68-40ef-4d7e-aa8d-27892748c9dc | CPU_0_DIMM_D0    | temperature | enabled | ok      |
| 0962eea1-1e79-4de0-a0cf-3f5846abec7c | CPU_0_DIMM_E0    | temperature | enabled | ok      |
| 03aaa30e-c4b7-4e66-a34c-dbf347a5cc68 | CPU_0_DIMM_F0    | temperature | enabled | ok      |
| 13f2af9b-3550-4843-9ad9-abadef075bb5 | CPU_0_DTS_TEMP   | temperature | enabled | ok      |
| 942ff781-4c31-4bf3-aa63-e5f96cd329be | CPU_0_MARGIN     | temperature | enabled | ok      |
| 6278cdb5-6d29-4f73-a1d9-af6be7433715 | CPU_0_PROCHOT    | temperature | enabled | ok      |
| 599f364a-1630-4061-80be-39154cb1d0b3 | CPU_0_TEMP       | temperature | enabled | ok      |
| 7e4a5164-0336-4a03-aa5a-5bc9ba927f74 | CPU_0_Vcore      | voltage     | enabled | ok      |
| aa9f26a6-82c7-4330-8417-478e9ff6bb21 | FPGA_BOARD_TEMP  | temperature | enabled | ok      |
| de2f9f0f-c42f-4b7b-a569-77e1d30c9fcf | FPGA_CORE        | temperature | enabled | ok      |
| bbcccbb5-dbc0-439f-bba4-e13a0eb33245 | MAX_DIMM_TEMP    | temperature | enabled | ok      |
| 6979c624-1b6c-4a31-b753-afccaa9ad7af | MLB_AMB_TEMP     | temperature | enabled | ok      |
| f6381847-9714-4ba7-a407-be5a72745385 | MLB_INLET_TEMP   | temperature | enabled | ok      |
| b6f2a90c-33a1-45ad-bad0-316d0d376b25 | MLB_OUTLET_TEMP  | temperature | enabled | ok      |
| bce4a79b-62c7-4d0c-855b-f04ab4938bba | PSU_0_FAN        | fan         | enabled | ok      |
| 4ea22e2a-a440-44a0-88dd-57648203b2a5 | PSU_0_TEMP_1     | temperature | enabled | ok      |
| 4df4213b-b613-4fa7-b540-c0766fa74440 | PSU_0_TEMP_2     | temperature | enabled | ok      |
| 5d39ce5e-6c18-4c72-903b-ffb72fa84440 | PSU_1_FAN        | fan         | enabled | ok      |
| 126823cd-34a3-4757-a7a5-67783abc55be | PSU_1_TEMP_1     | temperature | enabled | ok      |
| da418fee-5661-49e3-8845-627725dc2f28 | PSU_1_TEMP_2     | temperature | enabled | ok      |
| e320acd5-d706-4ff3-9012-bd19c0a96345 | Power Supply Bay | power       | enabled | offline |
| 377271c1-a112-44d4-8c64-9186f6d8841e | SSD_0_TEMP       | temperature | enabled | offline |
| bc6b0e11-e6b2-42c9-b124-b762eab83e5b | SSD_1_TEMP       | temperature | enabled | ok      |
| 1721f532-dd6b-4212-b59b-e9e31be315e3 | SYS_FAN_1A       | fan         | enabled | ok      |
| 48bc944e-3740-4ff2-8b8d-dd2790a09b13 | SYS_FAN_1B       | fan         | enabled | ok      |
| 036b9873-fe12-4472-abbd-c4b7ad7fb1be | SYS_FAN_2A       | fan         | enabled | ok      |
| 2ad6dea4-8d20-4f5a-aaff-a2403c5bcb34 | SYS_FAN_2B       | fan         | enabled | ok      |
| 75a4248f-d610-4809-b255-930fef529c9d | SYS_FAN_3A       | fan         | enabled | ok      |
| 0a332d54-f755-4ad4-ac5e-dcb1a0ff29fd | SYS_FAN_3B       | fan         | enabled | ok      |
| 4a263507-905d-4f94-a541-29823f0cb13c | SYS_FAN_4A       | fan         | enabled | ok      |
| 31f1d8ef-18cf-496a-969a-176043bb6089 | SYS_FAN_4B       | fan         | enabled | ok      |
| 9337014a-d70d-4a68-aa5f-f83ded82f9f6 | SYS_FAN_5A       | fan         | enabled | ok      |
| 880f9bf1-ac36-4c3d-b284-36b4856d8fb5 | SYS_FAN_5B       | fan         | enabled | ok      |
| e9fb9188-98e5-4777-a9b7-4229b99c9fbe | SYS_FAN_6A       | fan         | enabled | ok      |
| 3b3ba676-fb41-4ce4-9f5c-4db6b4646b34 | SYS_FAN_6B       | fan         | enabled | ok      |
| c14d3cd9-25ce-4d9f-b28a-896893265681 | SYS_FAN_7A       | fan         | enabled | ok      |
| f36f1a6f-1f7c-4721-92fd-5548aaefed35 | SYS_FAN_7B       | fan         | enabled | ok      |
| 4ec7b363-7ea2-42ce-9096-1680a5a03de0 | SYS_FAN_8A       | fan         | enabled | ok      |
| 0b7ec41a-1468-409b-88f1-086a1765a7ce | SYS_FAN_8B       | fan         | enabled | ok      |
| 2921d520-773c-4d31-92d6-c12c1d218602 | SYS_PCH_TEMP     | temperature | enabled | ok      |
| f21ac8a3-708f-4bc6-8b76-5de18d0aee7a | SYS_V1.05        | voltage     | enabled | ok      |
| 89175fa8-9c62-4e3e-8fd8-fd3dfefc69c5 | SYS_V12          | voltage     | enabled | ok      |
| 3a99c135-1bc7-4a50-be13-8f71065b3249 | SYS_V3.3         | voltage     | enabled | ok      |
| aa81cbb7-f81c-4916-80b3-53da91f4b32f | SYS_V5           | voltage     | enabled | ok      |
+--------------------------------------+------------------+-------------+---------+---------+
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

| bm_ip                 | 2607:f160:10:9073:ce:406:0:1000                                      |
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
| boot_device           | /dev/disk/by-path/pci-0000:b4:00.0-nvme-1 |
| capabilities          | {u'stor_function': u'monitor'}            |
| clock_synchronization | ntp                                       |
| config_applied        | 41386ba8-c2a0-4ccb-8cfe-2d7f83a05379      |
| config_status         | None                                      |
| config_target         | 41386ba8-c2a0-4ccb-8cfe-2d7f83a05379      |
| console               | ttyS0,115200                              |
| created_at            | 2023-12-13T16:31:53.708705+00:00          |
| device_image_update   | None                                      |
| hostname              | controller-0                              |
| id                    | 1                                         |
| install_output        | text                                      |
| install_state         | None                                      |
| install_state_info    | None                                      |
| inv_state             | inventoried                               |
| invprovision          | provisioned                               |
| location              | {}                                        |
| mgmt_ip               | 2607:f160:10:907b:ce:40a:0:1              |
| mgmt_mac              | 68:05:ca:9a:eb:78                         |
| operational           | enabled                                   |
| personality           | controller                                |
| reboot_needed         | False                                     |
| reserved              | False                                     |
| rootfs_device         | /dev/disk/by-path/pci-0000:b4:00.0-nvme-1 |
| serialid              | None                                      |
| software_load         | 21.12                                     |
| subfunction_avail     | available                                 |
| subfunction_oper      | enabled                                   |
| subfunctions          | controller,worker,lowlatency              |
| task                  |                                           |
| tboot                 | false                                     |
| ttys_dcd              | None                                      |
| updated_at            | 2023-12-13T20:44:03.938285+00:00          |
| uptime                | 12862                                     |
| uuid                  | d4a46b99-89dd-46e6-8273-b2fe8f4e8afd      |
| vim_progress_status   | services-enabled                          |
+-----------------------+-------------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ system host-show 1 | grep bm
| bm_ip                 | None                                                                 |
| bm_type               | none                                                                 |
| bm_username           | None                                                                 |
[XXXXXX@controller-0 ~(keystone_admin)]$ system host-sensor-list 1

[XXXXXX@controller-0 ~(keystone_admin)]$
```
