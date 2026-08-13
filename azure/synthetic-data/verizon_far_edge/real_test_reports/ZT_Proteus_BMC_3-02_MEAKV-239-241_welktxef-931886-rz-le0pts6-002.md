# ZT Proteus BMC 3.02 with BIOS 0.30
# 10/17/25 James Patchett - MTCE Lab VCPfe
# MEAKV-239-241 System test 24.09.301
 
## welktxef-931856-rz-le0pts6-004
BMC:  2607:f160:10:80b1:ce:40a:0:e003
OAM:  2607:f160:10:80b1:ce:40a:0:f403


### MEAKV-239
### Subcloud 

Verify that distributed region controller-0 host has no BMC information after current deployment. If that is the case, manually provision BMC for host. For example:

```sh 
system host-show 1 | grep bm
system host-update controller-0 bm_ip=2607:f160:10:80b1:ce:40a:0:e003 bm_type=redfish bm_username=XXXXXX bm_password=XXXXXX
system host-show 1 | grep bm
```

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ system host-show 1 | grep bm
| bm_ip                  | None                                                                    |
| bm_type                | none                                                                    |
| bm_username            | None                                                                    |
[XXXXXX@controller-0 ~(keystone_admin)]$ system host-update controller-0 bm_ip=2607:f160:10:80b1:ce:40a:0:e003 bm_type=redfish bm_username=XXXXXX bm_password=XXXXXX
+------------------------+-------------------------------------------------------------------------+
| Property               | Value                                                                   |
+------------------------+-------------------------------------------------------------------------+
| action                 | none                                                                    |
| administrative         | unlocked                                                                |
| apparmor               | disabled                                                                |
| availability           | available                                                               |
| bm_ip                  | 2607:f160:10:80b1:ce:40a:0:e003                                         |
| bm_type                | redfish                                                                 |
| bm_username            | XXXXXX                                                           |
| boot_device            | /dev/disk/by-path/pci-0000:c3:00.0-nvme-1                               |
| capabilities           | {'is_max_cpu_configurable': 'configurable', 'min_cpu_mhz_allowed': 800, |
|                        | 'max_cpu_mhz_allowed': 3500, 'cstates_available': 'C1,C2,POLL',         |
|                        | 'stor_function': 'monitor'}                                             |
| clock_synchronization  | ptp                                                                     |
| config_applied         | 20a987a9-aa1c-4e5b-a3ec-13e2d1b8e810                                    |
| config_status          | None                                                                    |
| config_target          | 20a987a9-aa1c-4e5b-a3ec-13e2d1b8e810                                    |
| console                | ttyS0,115200                                                            |
| created_at             | 2025-10-20T23:22:49.357464+00:00                                        |
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
| max_cpu_mhz_configured | 2500                                                                    |
| mgmt_ip                | 2607:f160:10:80b6:ce:40a:0:1                                            |
| mgmt_mac               | b4:96:91:b6:13:38                                                       |
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
| updated_at             | 2025-10-22T22:26:36.119509+00:00                                        |
| uptime                 | 942                                                                     |
| uuid                   | 607c7697-d966-4da0-bf12-e197674481d5                                    |
| vim_progress_status    | services-enabled                                                        |
+------------------------+-------------------------------------------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ system host-show 1 | grep bm
| bm_ip                  | 2607:f160:10:80b1:ce:40a:0:e003                                         |
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
| bm_ip                  | 2607:f160:10:80b1:ce:40a:0:e003                                         |
| bm_type                | redfish                                                                 |
| bm_username            | XXXXXX                                                           |
[XXXXXX@controller-0 ~(keystone_admin)]$ system host-sensor-list 1
+--------------------------------------+-------------+-------------+---------+---------+
| uuid                                 | name        | sensortype  | state   | status  |
+--------------------------------------+-------------+-------------+---------+---------+
| 19c7f1a6-9a1d-44ab-a622-d685347d65c9 | ADM1278     | power       | enabled | ok      |
| 22e83a76-429b-45fa-948a-e7be72f1672e | CPU0DDR_ABC | voltage     | enabled | ok      |
|                                      | _1.2V       |             |         |         |
|                                      |             |             |         |         |
| 4d9060a8-6f00-41ea-9445-12fb971aa80b | CPU0DDR_DEF | voltage     | enabled | ok      |
|                                      | _1.2V       |             |         |         |
|                                      |             |             |         |         |
| 04a4ecc2-b8a6-4cca-a642-e5a1925a010e | CPU_0_DIMM_ | temperature | enabled | ok      |
|                                      | A0          |             |         |         |
|                                      |             |             |         |         |
| 051d9b10-51d0-4c0f-84e9-96f8b81d8efe | CPU_0_DIMM_ | temperature | enabled | ok      |
|                                      | B0          |             |         |         |
|                                      |             |             |         |         |
| 1d21cb6c-7e29-44e5-88a6-db4135b82bc6 | CPU_0_DIMM_ | temperature | enabled | ok      |
|                                      | C0          |             |         |         |
|                                      |             |             |         |         |
| e3ac8045-3dab-4ee0-b72b-22a99565f18d | CPU_0_DIMM_ | temperature | enabled | ok      |
|                                      | D0          |             |         |         |
|                                      |             |             |         |         |
| 4eb413cb-f706-43f4-8796-bfdf6b2ae341 | CPU_0_DIMM_ | temperature | enabled | ok      |
|                                      | E0          |             |         |         |
|                                      |             |             |         |         |
| 94bb73f2-b7c9-4cb9-a0a4-e043651dbf61 | CPU_0_DIMM_ | temperature | enabled | ok      |
|                                      | F0          |             |         |         |
|                                      |             |             |         |         |
| 7065401c-fff5-4ba6-a25e-d7922e221ea3 | CPU_0_DIMM_ | temperature | enabled | ok      |
|                                      | G0          |             |         |         |
|                                      |             |             |         |         |
| 0be5a2f7-2bb2-41be-a4bd-14def988e500 | CPU_0_DIMM_ | temperature | enabled | ok      |
|                                      | H0          |             |         |         |
|                                      |             |             |         |         |
| bafa7a1d-6f4f-4d19-872c-0314203e0b44 | CPU_0_DTS_T | temperature | enabled | ok      |
|                                      | EMP         |             |         |         |
|                                      |             |             |         |         |
| 6bf98564-1c0e-4317-b8d0-3a1e354ff5d7 | CPU_0_MARGI | temperature | enabled | ok      |
|                                      | N           |             |         |         |
|                                      |             |             |         |         |
| 8bebd334-5987-45b2-804b-b335cb7cf5fe | CPU_0_TEMP  | temperature | enabled | ok      |
| ae5ce1bb-ff39-4b8a-a464-157163ede297 | CPU_0_Vcore | voltage     | enabled | ok      |
| 191f454b-fcff-4b18-b5ad-be33f0877486 | DIMM_VRABCD | temperature | enabled | ok      |
|                                      | _TEMP       |             |         |         |
|                                      |             |             |         |         |
| 26b56d86-8775-4a5b-b808-bf382b238669 | DIMM_VREFGH | temperature | enabled | ok      |
|                                      | _TEMP       |             |         |         |
|                                      |             |             |         |         |
| d56b3825-0d32-4d2e-9d91-f695a805e1a3 | INLET_TEMP_ | temperature | enabled | ok      |
|                                      | L           |             |         |         |
|                                      |             |             |         |         |
| 2ae0dd42-83d9-4bda-aab5-b89ec0407093 | INLET_TEMP_ | temperature | enabled | ok      |
|                                      | MAX         |             |         |         |
|                                      |             |             |         |         |
| da71a3bb-9015-4658-8e21-062afaeafa8e | INLET_TEMP_ | temperature | enabled | ok      |
|                                      | R           |             |         |         |
|                                      |             |             |         |         |
| d7fde12d-b0c8-43a2-b8d6-e120c3380293 | MAX_DIMM_TE | temperature | enabled | ok      |
|                                      | MP          |             |         |         |
|                                      |             |             |         |         |
| 48dc43b9-a908-4aef-ac2a-3bd490f849f2 | MB_HSC_TEMP | temperature | enabled | ok      |
| c4f309b9-4e45-45fd-9e76-2a421888a53f | OUTLET_TEMP | temperature | enabled | ok      |
|                                      | _L          |             |         |         |
|                                      |             |             |         |         |
| f5bdf4d0-b2b4-4d66-95ab-49ae3a55847a | OUTLET_TEMP | temperature | enabled | ok      |
|                                      | _MAX        |             |         |         |
|                                      |             |             |         |         |
| 9d42d1f9-e08d-42c2-9509-a83967994f6a | OUTLET_TEMP | temperature | enabled | ok      |
|                                      | _R          |             |         |         |
|                                      |             |             |         |         |
| 5c5137d7-1bbe-47f2-87c3-4f71c51cb90f | PML_EAST_TE | temperature | enabled | ok      |
|                                      | MP          |             |         |         |
|                                      |             |             |         |         |
| f85f66a5-182f-4f7d-ace4-6ccb610a4fb4 | PML_LOCAL_T | temperature | enabled | ok      |
|                                      | EMP         |             |         |         |
|                                      |             |             |         |         |
| 61568a87-da28-4b44-9ca2-737c59e02998 | PML_VDD_TEM | temperature | enabled | ok      |
|                                      | P           |             |         |         |
|                                      |             |             |         |         |
| 382a7f77-02ed-4b45-b164-5f1518f6b4dd | PML_WEST_TE | temperature | enabled | ok      |
|                                      | MP          |             |         |         |
|                                      |             |             |         |         |
| 1809ddf7-1118-4101-8e7d-5848985d3ef0 | PSU_1_FAN   | fan         | enabled | offline |
| 5dcc76f1-b4ca-41f1-be20-79d466c88e19 | PSU_1_TEMP_ | temperature | enabled | offline |
|                                      | 1           |             |         |         |
|                                      |             |             |         |         |
| 8a9c4aec-4f54-4274-9a92-a893d60042c2 | PSU_1_TEMP_ | temperature | enabled | offline |
|                                      | 2           |             |         |         |
|                                      |             |             |         |         |
| c4be4f9a-204f-4d9d-87a2-e99244f93266 | PSU_2_FAN   | fan         | enabled | offline |
| a3fbaad0-4c6d-4bbb-8a2a-0177013919a8 | PSU_2_TEMP_ | temperature | enabled | offline |
|                                      | 1           |             |         |         |
|                                      |             |             |         |         |
| 8236c6ca-f858-4ef8-8d3d-3e5a52335409 | PSU_2_TEMP_ | temperature | enabled | offline |
|                                      | 2           |             |         |         |
|                                      |             |             |         |         |
| 0cac8a7f-f17f-4133-9a49-e32ff40ba3c5 | Power       | power       | enabled | ok      |
|                                      | Supply Bay  |             |         |         |
|                                      |             |             |         |         |
| 359b4f11-e275-4de6-ad8f-762dfb85cdec | RTC_Voltage | voltage     | enabled | ok      |
| 852f56b6-ba6e-419c-9c1e-315aea20e652 | SC_1_E810   | temperature | enabled | ok      |
| 340925d8-3fde-4e69-9734-b37c770c1c4d | SC_2_E810   | temperature | enabled | ok      |
| 164acfa2-e1c3-4db2-931c-77367f2e18a8 | SSD_0_TEMP  | temperature | enabled | ok      |
| 917484d2-19f0-46f3-ac34-3b72cbee5c40 | SSD_1_TEMP  | temperature | enabled | ok      |
| e0f412de-91f3-4f3f-915f-a507efc77a49 | SYS_FAN_1A  | fan         | enabled | ok      |
| 0bcbc788-de14-41ca-ac00-b8f53217bf01 | SYS_FAN_1B  | fan         | enabled | ok      |
| 84c21f1c-9334-4b76-91f3-92b6e6a508a5 | SYS_FAN_2A  | fan         | enabled | ok      |
| 9041f321-07ce-49fe-9321-ca9df105d3b6 | SYS_FAN_2B  | fan         | enabled | ok      |
| 1ddbcd93-dfff-41a5-b185-b6fa0c452909 | SYS_PCH_TEM | temperature | enabled | ok      |
|                                      | P           |             |         |         |
|                                      |             |             |         |         |
| a859ef0f-54b8-43cb-a84e-18bf97f63bec | SYS_V1.05   | voltage     | enabled | ok      |
| 219a4659-140f-45c6-a4ce-6be7670ae267 | SYS_V12     | voltage     | enabled | ok      |
| 7e4a2848-05b8-4aad-8f12-239b33747756 | SYS_V3.3    | voltage     | enabled | ok      |
| c18af731-69f9-4e3d-b35f-db2f76864fd5 | SYS_V5      | voltage     | enabled | ok      |
+--------------------------------------+-------------+-------------+---------+---------+
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
| bm_ip                  | 2607:f160:10:80b1:ce:40a:0:e003                                         |
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
| clock_synchronization  | ptp                                                                     |
| config_applied         | 20a987a9-aa1c-4e5b-a3ec-13e2d1b8e810                                    |
| config_status          | None                                                                    |
| config_target          | 20a987a9-aa1c-4e5b-a3ec-13e2d1b8e810                                    |
| console                | ttyS0,115200                                                            |
| created_at             | 2025-10-20T23:22:49.357464+00:00                                        |
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
| max_cpu_mhz_configured | 2500                                                                    |
| mgmt_ip                | 2607:f160:10:80b6:ce:40a:0:1                                            |
| mgmt_mac               | b4:96:91:b6:13:38                                                       |
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
| updated_at             | 2025-10-22T22:31:46.103079+00:00                                        |
| uptime                 | 1252                                                                    |
| uuid                   | 607c7697-d966-4da0-bf12-e197674481d5                                    |
| vim_progress_status    | services-enabled                                                        |
+------------------------+-------------------------------------------------------------------------+
| bm_ip                  | None                                                                    |
| bm_type                | none                                                                    |
| bm_username            | None                                                                    |

[XXXXXX@controller-0 ~(keystone_admin)]$

```

## Compared to sensors showing in impitool

```sh
root@controller-0:~# ipmitool sensor
CPU_0_PROCHOT    | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
CPU_0_STATUS     | 0x0        | discrete   | 0x8080| na        | na        | na        | na        | na        | na
CPU_0_Vcore      | 1.822      | Volts      | ok    | na        | 1.690     | na        | na        | 1.870     | na
CPU0DDR_ABC_1.2V | 1.231      | Volts      | ok    | na        | 1.134     | na        | na        | 1.256     | na
CPU0DDR_DEF_1.2V | 1.231      | Volts      | ok    | na        | 1.134     | na        | na        | 1.256     | na
CPU_0_DTS_TEMP   | -42.000    | degrees C  | ok    | na        | na        | na        | na        | na        | na
CPU_0_TEMP       | 56.000     | degrees C  | ok    | na        | na        | na        | 96.000    | 98.000    | na
CPU_0_MARGIN     | 31.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
CPU0_Power       | 91.000     | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_PCH_TEMP     | 31.000     | degrees C  | ok    | na        | 5.000     | na        | na        | 82.000    | na
CPU_0_DIMM_C0    | 38.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_D0    | 36.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_A0    | 35.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_B0    | 34.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_G0    | 37.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_H0    | 36.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_E0    | 36.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_F0    | 36.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
MAX_DIMM_TEMP    | 38.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
INLET_TEMP_L     | 25.000     | degrees C  | ok    | na        | -6.000    | na        | 50.000    | 59.000    | 61.000
INLET_TEMP_R     | 23.000     | degrees C  | ok    | na        | -6.000    | na        | 50.000    | 59.000    | 61.000
INLET_TEMP_MAX   | 25.000     | degrees C  | ok    | na        | -6.000    | na        | 50.000    | 59.000    | 61.000
OUTLET_TEMP_L    | 41.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
OUTLET_TEMP_R    | 38.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
OUTLET_TEMP_MAX  | 41.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 5125.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1B       | 5500.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_2A       | 5125.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_2B       | 5500.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1A_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1B_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_2A_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_2B_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_V1.05        | 1.055      | Volts      | ok    | na        | 0.993     | na        | na        | 1.097     | na
SYS_V12          | 12.270     | Volts      | ok    | na        | 11.348    | na        | na        | 12.552    | na
SYS_V3.3         | 3.329      | Volts      | ok    | na        | 3.104     | na        | na        | 3.431     | na
SYS_V5           | 5.069      | Volts      | ok    | na        | 4.725     | na        | na        | 5.225     | na
CPU_CUPS         | 21.000     | percent    | ok    | na        | na        | na        | na        | 100.000   | na
MB_HSC_TEMP      | 37.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 125.000   | na
DIMM_VREFGH_TEMP | 32.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 125.000   | na
DIMM_VRABCD_TEMP | 35.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 125.000   | na
RTC_Voltage      | 2.891      | Volts      | ok    | na        | 2.289     | na        | na        | 3.444     | na
MB_HSC_PIN       | 192.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
MB_HSC_PIN_AVG   | 140.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
MB_HSC_PEAK_PIN  | 412.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_1_STATUS     | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
PSU_2_STATUS     | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
PSU_1_FAN        | na         | RPM        | na    | 800.000   | 1120.000  | na        | na        | na        | na
PSU_2_FAN        | na         | RPM        | na    | 800.000   | 1120.000  | na        | na        | na        | na
PSU_1_TEMP_1     | na         | degrees C  | na    | na        | na        | na        | na        | 60.000    | 64.000
PSU_2_TEMP_1     | na         | degrees C  | na    | na        | na        | na        | na        | 60.000    | 64.000
PSU_1_TEMP_2     | na         | degrees C  | na    | na        | na        | na        | na        | 92.000    | 97.000
PSU_2_TEMP_2     | na         | degrees C  | na    | na        | na        | na        | na        | 92.000    | 97.000
PSU_POWER_IN     | na         | Watts      | na    | na        | na        | na        | na        | na        | na
PSU_1_POWER_IN   | na         | Watts      | na    | na        | na        | na        | na        | na        | na
PSU_2_POWER_IN   | na         | Watts      | na    | na        | na        | na        | na        | na        | na
PSU_1_POWER_OUT  | na         | Watts      | na    | na        | na        | na        | na        | na        | na
PSU_2_POWER_OUT  | na         | Watts      | na    | na        | na        | na        | na        | na        | na
PSU_1_CURRENT_IN | na         | Amps       | na    | na        | na        | na        | na        | na        | na
PSU_2_CURRENT_IN | na         | Amps       | na    | na        | na        | na        | na        | na        | na
PSU1_CURRENT_OUT | na         | Amps       | na    | na        | na        | na        | na        | na        | na
PSU2_CURRENT_OUT | na         | Amps       | na    | na        | na        | na        | na        | na        | na
PWR_UNIT_REDUND  | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
PWR_UNIT_STATUS  | 0x0        | discrete   | 0x0080| na        | na        | na        | na        | na        | na
ACPI_STATE       | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
SSD_0_TEMP       | 33.000     | degrees C  | ok    | na        | 0.000     | na        | na        | 70.000    | 79.000
SSD_1_TEMP       | 35.000     | degrees C  | ok    | na        | 0.000     | na        | na        | 70.000    | 79.000
PML_WEST_TEMP    | 57.000     | degrees C  | ok    | na        | na        | na        | na        | 110.000   | 114.000
PML_LOCAL_TEMP   | 55.000     | degrees C  | ok    | na        | na        | na        | 80.000    | 85.000    | na
PML_VDD_TEMP     | 62.000     | degrees C  | ok    | na        | na        | na        | na        | 125.000   | na
PML_EAST_TEMP    | 57.000     | degrees C  | ok    | na        | na        | na        | na        | 110.000   | 114.000
SC_1_E810        | 41.000     | degrees C  | ok    | na        | 0.000     | 5.000     | 100.000   | 105.000   | 115.000
SC_2_E810        | 38.000     | degrees C  | ok    | na        | 0.000     | 5.000     | 100.000   | 105.000   | 115.000
root@controller-0:~#
```

### Test has passed

