# ZT Triton BMC 2.31 with BIOS 2.10
# 10/17/25 James Patchett - MTCE Lab VCPfe
# MEAKV-239-241 System test 24.09.301
 
## welktxef-931883-rz-le0trtn-031
BMC:  2607:f160:10:9249:ce:40a:0:e01f
OAM:  2607:f160:10:9249:ce:40a:0:f402


### MEAKV-239
### Subcloud 

Verify that distributed region controller-0 host has no BMC information after current deployment. If that is the case, manually provision BMC for host. For example:

```sh 
system host-show 1 | grep bm
system host-update controller-0 bm_ip=2607:f160:10:9249:ce:40a:0:e01f bm_type=redfish bm_username=XXXXXX bm_password=XXXXXX
system host-show 1 | grep bm
```

```log


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
[[XXXXXX@controller-0 ~(keystone_admin)]$ system host-show 1 | grep bm
| bm_ip                  | 2607:f160:10:9249:ce:40a:0:e039                                         |
| bm_type                | redfish                                                                 |
| bm_username            | XXXXXX                                                           |
[XXXXXX@controller-0 ~(keystone_admin)]$ system host-sensor-list 1
+--------------------------------------+--------------+-------------+---------+--------+
| uuid                                 | name         | sensortype  | state   | status |
+--------------------------------------+--------------+-------------+---------+--------+
| f3726db9-586a-4921-8291-3dbde95a4645 | ADM1278      | power       | enabled | ok     |
| 8d6c0f1d-e4be-4b6b-b0a7-ba0cabb4d7cd | CPU0DDR_ABC_ | voltage     | enabled | ok     |
|                                      | 1.2V         |             |         |        |
|                                      |              |             |         |        |
| 6f7a9de4-7d07-42a2-9818-8137ad5bfbab | CPU0DDR_DEF_ | voltage     | enabled | ok     |
|                                      | 1.2V         |             |         |        |
|                                      |              |             |         |        |
| c7774fb3-15a2-488a-91bd-fc17621de2fa | CPU_0_DIMM_A | temperature | enabled | ok     |
|                                      | 0            |             |         |        |
|                                      |              |             |         |        |
| debe176f-8b50-4bac-8bec-5498054c659c | CPU_0_DIMM_B | temperature | enabled | ok     |
|                                      | 0            |             |         |        |
|                                      |              |             |         |        |
| 3195555a-8e7b-43fb-baff-baa44fad03a9 | CPU_0_DIMM_C | temperature | enabled | ok     |
|                                      | 0            |             |         |        |
|                                      |              |             |         |        |
| dba1dc86-b5c9-4fd5-a32c-e3b7e9ebc5e5 | CPU_0_DIMM_D | temperature | enabled | ok     |
|                                      | 0            |             |         |        |
|                                      |              |             |         |        |
| 12b63b41-cac8-445b-861f-af19f4619d5d | CPU_0_DIMM_E | temperature | enabled | ok     |
|                                      | 0            |             |         |        |
|                                      |              |             |         |        |
| c615b3e3-f9ea-4034-b1ff-ce627c35084f | CPU_0_DIMM_F | temperature | enabled | ok     |
|                                      | 0            |             |         |        |
|                                      |              |             |         |        |
| 563fca36-0cf3-4655-9762-68dba39a1740 | CPU_0_DIMM_G | temperature | enabled | ok     |
|                                      | 0            |             |         |        |
|                                      |              |             |         |        |
| 0b16a1c2-8c39-4135-ae71-643698d0b631 | CPU_0_DIMM_H | temperature | enabled | ok     |
|                                      | 0            |             |         |        |
|                                      |              |             |         |        |
| 8e200e05-0cdc-4234-8ca7-b85714333325 | CPU_0_DTS_TE | temperature | enabled | ok     |
|                                      | MP           |             |         |        |
|                                      |              |             |         |        |
| 047a0f6e-358f-496d-bd36-2b9f80f80b1d | CPU_0_MARGIN | temperature | enabled | ok     |
| 89aea6ed-ded6-4fe2-9675-e1e4843be386 | CPU_0_TEMP   | temperature | enabled | ok     |
| 93cdb3f8-8e06-4ce1-95bc-eb673a673d86 | CPU_0_Vcore  | voltage     | enabled | ok     |
| c370ad24-c54c-4e06-929c-a3958a50b779 | DIMM_VRABCD_ | temperature | enabled | ok     |
|                                      | TEMP         |             |         |        |
|                                      |              |             |         |        |
| dfda666f-fc73-472e-9a3b-1fa3f46450f5 | DIMM_VREFGH_ | temperature | enabled | ok     |
|                                      | TEMP         |             |         |        |
|                                      |              |             |         |        |
| 23832972-c45e-4202-af64-8ac42377bf31 | INLET_TEMP_L | temperature | enabled | ok     |
| e31f6aa5-1a3b-4012-b08d-2dde68a61543 | INLET_TEMP_M | temperature | enabled | ok     |
|                                      | AX           |             |         |        |
|                                      |              |             |         |        |
| 067fc5df-466f-4cfe-8b5f-26d4ffb4be00 | INLET_TEMP_R | temperature | enabled | ok     |
| c194afa2-17e0-4dd8-a258-5a57489e65e7 | MAX_DIMM_TEM | temperature | enabled | ok     |
|                                      | P            |             |         |        |
|                                      |              |             |         |        |
| 8afb37c9-cd2d-4ad7-aef4-86b5f33a310d | MB_HSC_TEMP  | temperature | enabled | ok     |
| b092f2c3-108d-4480-940c-7cdd7c0f2c18 | OUTLET_TEMP_ | temperature | enabled | ok     |
|                                      | L            |             |         |        |
|                                      |              |             |         |        |
| faaa2ec5-1307-4794-96cc-5f905ca1ebd1 | OUTLET_TEMP_ | temperature | enabled | ok     |
|                                      | MAX          |             |         |        |
|                                      |              |             |         |        |
| 88bc0173-c64b-47dc-af74-f9777dde2709 | OUTLET_TEMP_ | temperature | enabled | ok     |
|                                      | R            |             |         |        |
|                                      |              |             |         |        |
| fd505eb9-683b-48cf-92bf-08926dd9e409 | PML_EAST_TEM | temperature | enabled | ok     |
|                                      | P            |             |         |        |
|                                      |              |             |         |        |
| c2be6d23-6d94-49b2-af79-cf1d1fc4d74f | PML_LOCAL_TE | temperature | enabled | ok     |
|                                      | MP           |             |         |        |
|                                      |              |             |         |        |
| 41ece266-5c47-4c4e-b430-8cd405bab5e0 | PML_VDD_TEMP | temperature | enabled | ok     |
| a4d7adce-0dce-40e5-baa6-794eb10c1b82 | PML_WEST_TEM | temperature | enabled | ok     |
|                                      | P            |             |         |        |
|                                      |              |             |         |        |
| 8ecab77c-7430-4b15-90c9-bb4b574ae934 | PSU_1_FAN    | fan         | enabled | ok     |
| 5dbe084e-d6a4-44bf-87e2-ae794c6e81f9 | PSU_1_TEMP_1 | temperature | enabled | ok     |
| 52c790be-0047-4cc7-a276-7caebc07ff85 | PSU_1_TEMP_2 | temperature | enabled | ok     |
| 4c610ac8-7542-4a25-bcd1-0c7aa39b7ec0 | PSU_2_FAN    | fan         | enabled | ok     |
| 4a566d75-bff8-4d57-9e50-c353296b64e1 | PSU_2_TEMP_1 | temperature | enabled | ok     |
| ef119319-e65b-4159-8f6c-00b48e7db10a | PSU_2_TEMP_2 | temperature | enabled | ok     |
| 00d3c2e3-f62d-40ae-ab62-708227dc0a63 | Power Supply | power       | enabled | ok     |
|                                      | Bay          |             |         |        |
|                                      |              |             |         |        |
| abace099-8858-4873-8a66-b9b19da96a4e | RTC_Voltage  | voltage     | enabled | ok     |
| 8dc712ed-f45c-445f-b49a-d1e6209fa202 | SC_1_E810    | temperature | enabled | ok     |
| 8618963f-7d11-44f4-92c5-d3f22760c64c | SC_2_E810    | temperature | enabled | ok     |
| 8dabf886-e6eb-4c54-bebf-3da34b4cc1c9 | SSD_0_TEMP   | temperature | enabled | ok     |
| 9289f2b6-9d70-4e8d-ace4-61bd439af5dc | SSD_1_TEMP   | temperature | enabled | ok     |
| ac73aa9e-5df6-405b-8796-847503c8bd49 | SYS_FAN_1A   | fan         | enabled | ok     |
| 907c8514-9728-4a6b-9f74-91e74ed7a391 | SYS_FAN_1B   | fan         | enabled | ok     |
| 8a6264ab-fd68-4622-9239-fa3d9c3740b3 | SYS_FAN_2A   | fan         | enabled | ok     |
| 49bc7596-8b6e-4764-bbd8-7294c8dc14ab | SYS_FAN_2B   | fan         | enabled | ok     |
| 13ebdd40-ddf3-4602-b63c-8b9ac586526a | SYS_PCH_TEMP | temperature | enabled | ok     |
| 97ebbe06-de24-4974-8003-ca3df7f4d3fa | SYS_V1.05    | voltage     | enabled | ok     |
| a9077a09-1aff-4441-973c-375f1d6b0542 | SYS_V12      | voltage     | enabled | ok     |
| 28d8a0f5-c306-4e00-a5ed-4947640a9d62 | SYS_V3.3     | voltage     | enabled | ok     |
| 69c52933-9dc3-4b26-b44b-9f7629f60c4c | SYS_V5       | voltage     | enabled | ok     |
+--------------------------------------+--------------+-------------+---------+--------+
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
| bm_ip                  | 2607:f160:10:9249:ce:40a:0:e039                                         |
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
| boot_device            | /dev/disk/by-path/pci-0000:c3:00.0-nvme-1                               |
| capabilities           | {'is_max_cpu_configurable': 'configurable', 'stor_function': 'monitor'} |
| clock_synchronization  | ptp                                                                     |
| config_applied         | 05ee700a-284c-4af7-b226-ddb3e65db0d3                                    |
| config_status          | None                                                                    |
| config_target          | 05ee700a-284c-4af7-b226-ddb3e65db0d3                                    |
| console                | tty0                                                                    |
| created_at             | 2025-10-02T03:21:56.466168+00:00                                        |
| cstates_available      | C1,C2,POLL                                                              |
| device_image_update    | None                                                                    |
| hostname               | controller-0                                                            |
| hw_settle              | 0                                                                       |
| id                     | 1                                                                       |
| install_output         | text                                                                    |
| install_state          | None                                                                    |
| install_state_info     | None                                                                    |
| inv_state              | inventoried                                                             |
| invprovision           | provisioned                                                             |
| iscsi_initiator_name   | iqn.2018-05.io.starlingx:e473553f6f                                     |
| location               | {}                                                                      |
| max_cpu_mhz_allowed    | 3500                                                                    |
| max_cpu_mhz_configured | 2500                                                                    |
| mgmt_mac               | b4:96:91:b6:0d:e8                                                       |
| min_cpu_mhz_allowed    | 800                                                                     |
| nvme_host_id           | 78b59e86-8a94-409f-820e-e6f90740bc82                                    |
| nvme_host_nqn          | nqn.2014-08.org.nvmexpress:uuid:ac6c7bac-49e3-49cd-80c4-ae0f02deed07    |
| operational            | enabled                                                                 |
| personality            | controller                                                              |
| reboot_needed          | False                                                                   |
| reserved               | False                                                                   |
| rootfs_device          | /dev/disk/by-path/pci-0000:c3:00.0-nvme-1                               |
| serialid               | None                                                                    |
| subfunction_avail      | available                                                               |
| subfunction_oper       | enabled                                                                 |
| subfunctions           | controller,worker,lowlatency                                            |
| sw_version             | 24.09                                                                   |
| task                   |                                                                         |
| tboot                  |                                                                         |
| ttys_dcd               | False                                                                   |
| updated_at             | 2025-10-06T22:10:18.808709+00:00                                        |
| uptime                 | 362364                                                                  |
| uuid                   | 6648ab1a-6910-410c-98fe-10e7c8bb3bd3                                    |
| vim_progress_status    | services-enabled                                                        |
+------------------------+-------------------------------------------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ system host-show 1 | grep bm
| bm_ip                  | None                                                                    |
| bm_type                | none                                                                    |
| bm_username            | None                                                                    |
[XXXXXX@controller-0 ~(keystone_admin)]$ system host-sensor-list 1

[XXXXXX@controller-0 ~(keystone_admin)]$
```

