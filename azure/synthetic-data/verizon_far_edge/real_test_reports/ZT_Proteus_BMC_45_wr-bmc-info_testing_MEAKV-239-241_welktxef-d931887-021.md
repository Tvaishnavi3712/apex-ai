# ZT .45 BMC firmware validation
# 10/30/23 James Patchett

## Target Controller Rchltxfe-c000000-001
Controller-0 iLO 2607:f160:a:d02e:cd:fe0::8000 
Controller-1 iLO 2607:f160:a:d02e:cd:fe0::8001
Worker-0 iLO 2607:f160:a:d02e:cd:fe0::8002 
OAM 2607:f160:0:3043:cd:290:0:10



## Target Subcloud welktxef-d931887-021 (currently on controller 2607:f160:0:3049:cd:290:0:10 )
OAM 2607:f160:10:9249:ce:40a:0:f409
BMC 2607:f160:10:9249:ce:40a:0:e015

welktxef-931887-rz-le2pts6-021.yaml

ipmitool -I lanplus -U XXXXXX -P XXXXXX -H 2607:f160:10:9249:ce:40a:0:e015 sol activate

## Subcloud welktxef-d931887-021

## BMC testing, validation that WR can talk with BMC and extract sensor and BMC information

## First validate no bmc info on subcloud

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ system host-show 1 | grep bm
| bm_ip                 | None                                                                 |
| bm_type               | none                                                                 |
| bm_username           | None                                                                 |
[XXXXXX@controller-0 ~(keystone_admin)]$ system host-sensor-list 1

[XXXXXX@controller-0 ~(keystone_admin)]$
```

## confirmed no bmc data in WR

## Now Configure BMC with WR

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ system host-list
+----+--------------+-------------+----------------+-------------+--------------+
| id | hostname     | personality | administrative | operational | availability |
+----+--------------+-------------+----------------+-------------+--------------+
| 1  | controller-0 | controller  | locked         | disabled    | online       |
+----+--------------+-------------+----------------+-------------+--------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ system host-show 1
+-----------------------+----------------------------------------------------------------------+
| Property              | Value                                                                |
+-----------------------+----------------------------------------------------------------------+
| action                | none                                                                 |
| administrative        | locked                                                               |
| availability          | online                                                               |
| bm_ip                 | None                                                                 |
| bm_type               | none                                                                 |
| bm_username           | None                                                                 |
| boot_device           | /dev/disk/by-path/pci-0000:c3:00.0-nvme-1                            |
| capabilities          | {u'stor_function': u'monitor', u'Personality': u'Controller-Active'} |
| clock_synchronization | ptp                                                                  |
| config_applied        | 6c90a90a-4017-4bb9-9dab-198f5b76d18f                                 |
| config_status         | None                                                                 |
| config_target         | 6c90a90a-4017-4bb9-9dab-198f5b76d18f                                 |
| console               | ttyS0,115200                                                         |
| created_at            | 2023-10-24T23:15:23.347829+00:00                                     |
| device_image_update   | None                                                                 |
| hostname              | controller-0                                                         |
| id                    | 1                                                                    |
| install_output        | text                                                                 |
| install_state         | None                                                                 |
| install_state_info    | None                                                                 |
| inv_state             | inventoried                                                          |
| invprovision          | provisioned                                                          |
| location              | {}                                                                   |
| mgmt_ip               | 2607:f160:10:809f:ce:40a:0:1                                         |
| mgmt_mac              | b4:96:91:b5:5e:54                                                    |
| operational           | disabled                                                             |
| personality           | controller                                                           |
| reboot_needed         | False                                                                |
| reserved              | False                                                                |
| rootfs_device         | /dev/disk/by-path/pci-0000:c3:00.0-nvme-1                            |
| serialid              | None                                                                 |
| software_load         | 21.12                                                                |
| subfunction_avail     | online                                                               |
| subfunction_oper      | disabled                                                             |
| subfunctions          | controller,worker,lowlatency                                         |
| task                  |                                                                      |
| tboot                 | false                                                                |
| ttys_dcd              | None                                                                 |
| updated_at            | 2023-10-30T22:47:10.077573+00:00                                     |
| uptime                | 9362                                                                 |
| uuid                  | 166fa19c-d4a5-4d3e-aec3-a09bf8a04f85                                 |
| vim_progress_status   | services-disabled                                                    |
+-----------------------+----------------------------------------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$
[XXXXXX@controller-0 ~(keystone_admin)]$ system host-update controller-0 bm_ip=2607:f160:10:9249:ce:40a:0:e015 bm_type=redfish bm_username=K8Sctl bm_password=XXXXXX
+-----------------------+-------------------------------------------+
| Property              | Value                                     |
+-----------------------+-------------------------------------------+
| action                | none                                      |
| administrative        | locked                                    |
| availability          | online                                    |
| bm_ip                 | 2607:f160:10:9249:ce:40a:0:e015           |
| bm_type               | redfish                                   |
| bm_username           | K8Sctl                                    |
| boot_device           | /dev/disk/by-path/pci-0000:c3:00.0-nvme-1 |
| capabilities          | {u'stor_function': u'monitor'}            |
| clock_synchronization | ptp                                       |
| config_applied        | 6c90a90a-4017-4bb9-9dab-198f5b76d18f      |
| config_status         | None                                      |
| config_target         | 6c90a90a-4017-4bb9-9dab-198f5b76d18f      |
| console               | ttyS0,115200                              |
| created_at            | 2023-10-24T23:15:23.347829+00:00          |
| device_image_update   | None                                      |
| hostname              | controller-0                              |
| id                    | 1                                         |
| install_output        | text                                      |
| install_state         | None                                      |
| install_state_info    | None                                      |
| inv_state             | inventoried                               |
| invprovision          | provisioned                               |
| location              | {}                                        |
| mgmt_ip               | 2607:f160:10:809f:ce:40a:0:1              |
| mgmt_mac              | b4:96:91:b5:5e:54                         |
| operational           | disabled                                  |
| personality           | controller                                |
| reboot_needed         | False                                     |
| reserved              | False                                     |
| rootfs_device         | /dev/disk/by-path/pci-0000:c3:00.0-nvme-1 |
| serialid              | None                                      |
| software_load         | 21.12                                     |
| subfunction_avail     | online                                    |
| subfunction_oper      | disabled                                  |
| subfunctions          | controller,worker,lowlatency              |
| task                  |                                           |
| tboot                 | false                                     |
| ttys_dcd              | None                                      |
| updated_at            | 2023-10-30T22:49:11.011231+00:00          |
| uptime                | 9362                                      |
| uuid                  | 166fa19c-d4a5-4d3e-aec3-a09bf8a04f85      |
| vim_progress_status   | services-disabled                         |
+-----------------------+-------------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$

```
## Check that BMC has been configured 

```log

[XXXXXX@controller-0 ~(keystone_admin)]$ system host-show 1 | grep bm
| bm_ip                 | 2607:f160:10:9249:ce:40a:0:e015                                      |
| bm_type               | redfish                                                              |
| bm_username           | K8Sctl                                                               |
[XXXXXX@controller-0 ~(keystone_admin)]$ system host-show 1
+-----------------------+----------------------------------------------------------------------+
| Property              | Value                                                                |
+-----------------------+----------------------------------------------------------------------+
| action                | none                                                                 |
| administrative        | locked                                                               |
| availability          | online                                                               |
| bm_ip                 | 2607:f160:10:9249:ce:40a:0:e015                                      |
| bm_type               | redfish                                                              |
| bm_username           | K8Sctl                                                               |
| boot_device           | /dev/disk/by-path/pci-0000:c3:00.0-nvme-1                            |
| capabilities          | {u'stor_function': u'monitor', u'Personality': u'Controller-Active'} |
| clock_synchronization | ptp                                                                  |
| config_applied        | 6c90a90a-4017-4bb9-9dab-198f5b76d18f                                 |
| config_status         | None                                                                 |
| config_target         | 6c90a90a-4017-4bb9-9dab-198f5b76d18f                                 |
| console               | ttyS0,115200                                                         |
| created_at            | 2023-10-24T23:15:23.347829+00:00                                     |
| device_image_update   | None                                                                 |
| hostname              | controller-0                                                         |
| id                    | 1                                                                    |
| install_output        | text                                                                 |
| install_state         | None                                                                 |
| install_state_info    | None                                                                 |
| inv_state             | inventoried                                                          |
| invprovision          | provisioned                                                          |
| location              | {}                                                                   |
| mgmt_ip               | 2607:f160:10:809f:ce:40a:0:1                                         |
| mgmt_mac              | b4:96:91:b5:5e:54                                                    |
| operational           | disabled                                                             |
| personality           | controller                                                           |
| reboot_needed         | False                                                                |
| reserved              | False                                                                |
| rootfs_device         | /dev/disk/by-path/pci-0000:c3:00.0-nvme-1                            |
| serialid              | None                                                                 |
| software_load         | 21.12                                                                |
| subfunction_avail     | online                                                               |
| subfunction_oper      | disabled                                                             |
| subfunctions          | controller,worker,lowlatency                                         |
| task                  |                                                                      |
| tboot                 | false                                                                |
| ttys_dcd              | None                                                                 |
| updated_at            | 2023-10-30T22:50:10.208179+00:00                                     |
| uptime                | 9362                                                                 |
| uuid                  | 166fa19c-d4a5-4d3e-aec3-a09bf8a04f85                                 |
| vim_progress_status   | services-disabled                                                    |
+-----------------------+----------------------------------------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$

```
## BMC is configured

## check Sensor data to see that BMC is populating with data now

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ system host-sensor-list 1
+--------------------------------------+------------------+-------------+---------+---------+
| uuid                                 | name             | sensortype  | state   | status  |
+--------------------------------------+------------------+-------------+---------+---------+
| 44e94c2e-6c74-412d-898b-01f992fe7b95 | ADM1278          | power       | enabled | offline |
| 3066a0e2-4a4a-4f1a-9439-558674846231 | CPU0DDR_ABC_1.2V | voltage     | enabled | ok      |
| 94de3512-ed84-4e73-b6da-50a57808a31a | CPU0DDR_DEF_1.2V | voltage     | enabled | ok      |
| f6c20746-04d6-4bec-85e4-e5638709718d | CPU_0_DIMM_A0    | temperature | enabled | ok      |
| e8734e9c-2e05-41c2-bf52-b166aef7220e | CPU_0_DIMM_B0    | temperature | enabled | ok      |
| 7c864b1f-f5cc-4d5d-9427-cb24bb6c53e5 | CPU_0_DIMM_C0    | temperature | enabled | ok      |
| 6c84c5a1-2f2b-4736-823c-ec5e6c6ef4e1 | CPU_0_DIMM_D0    | temperature | enabled | ok      |
| 7598f279-01d4-47ad-8448-5164728ea2df | CPU_0_DIMM_E0    | temperature | enabled | ok      |
| e1f445de-e4ce-4ee0-a68b-e80ca06d0c13 | CPU_0_DIMM_F0    | temperature | enabled | ok      |
| b693f948-1c67-4ffa-bba7-10f73a9f3aa4 | CPU_0_DIMM_G0    | temperature | enabled | ok      |
| a686c414-38c2-4b26-8998-cb73167050ee | CPU_0_DIMM_H0    | temperature | enabled | ok      |
| 1c1a4af7-2c37-4a26-b0a2-6d7535360681 | CPU_0_DTS_TEMP   | temperature | enabled | ok      |
| 774383ea-d6cb-4d10-9ff8-ca4ea70f656d | CPU_0_MARGIN     | temperature | enabled | ok      |
| d513f291-8d02-4256-a0bb-2030643f1497 | CPU_0_PROCHOT    | temperature | enabled | ok      |
| fa22b58e-412f-4ec1-a441-33d7461e6e95 | CPU_0_TEMP       | temperature | enabled | ok      |
| c877bc43-9dd2-437b-b626-9865711c30bf | CPU_0_Vcore      | voltage     | enabled | ok      |
| f1ad03e4-6afd-4d29-9676-59d28028b614 | DIMM_VRABCD_TEMP | temperature | enabled | ok      |
| 5281c222-80b9-429d-84df-491e602937b6 | DIMM_VREFGH_TEMP | temperature | enabled | ok      |
| 8b432071-e278-4755-9481-d2b7c80dee69 | INLET_TEMP_L     | temperature | enabled | ok      |
| b13ce8e3-a631-4934-8645-ca560025728c | INLET_TEMP_MAX   | temperature | enabled | ok      |
| 0e273535-6758-4678-85a3-4aafd3b296d1 | INLET_TEMP_R     | temperature | enabled | ok      |
| 8ddaca0b-f449-48a3-b151-80d50cdbd2d4 | MAX_DIMM_TEMP    | temperature | enabled | ok      |
| f824d4b8-0d0a-434b-b889-9425ae3a5e13 | MB_HSC_TEMP      | temperature | enabled | ok      |
| fc9931c5-96b3-41a2-b1da-668f77780989 | OUTLET_TEMP_L    | temperature | enabled | ok      |
| 2289d6a9-6db8-42b2-a533-cc77437c564f | OUTLET_TEMP_MAX  | temperature | enabled | ok      |
| 71c146a6-0967-4252-b0a0-493c5c87d1c1 | OUTLET_TEMP_R    | temperature | enabled | ok      |
| 85c43c3c-a67e-40ca-a0b1-f306b547ab49 | PML_EAST_TEMP    | temperature | enabled | ok      |
| cfa94cdb-62b9-48c0-bbcf-f3e6313706a9 | PML_LOCAL_TEMP   | temperature | enabled | ok      |
| 219a3c0f-0904-4416-9542-669e35d05a90 | PML_VDD_TEMP     | temperature | enabled | ok      |
| bebcb46d-18f5-49cf-b46d-3f491dbc58a1 | PML_WEST_TEMP    | temperature | enabled | ok      |
| 5fbce48c-2ded-4cb5-8325-ee9117b1520c | PSU_1_FAN        | fan         | enabled | ok      |
| c762f711-a11a-48f7-ae1c-11911960a5b5 | PSU_1_TEMP_1     | temperature | enabled | ok      |
| eef8bbf9-0a99-4a5b-9ebd-dce1288db896 | PSU_1_TEMP_2     | temperature | enabled | ok      |
| 4c91640d-41a9-4da6-b210-96cad8223573 | PSU_2_FAN        | fan         | enabled | ok      |
| 03a34f62-3462-4169-b43e-bed49481adaf | PSU_2_TEMP_1     | temperature | enabled | ok      |
| 4aead0ee-f774-4b04-ad8f-992a88915bc4 | PSU_2_TEMP_2     | temperature | enabled | ok      |
| 35778a55-95a1-4e89-a339-bfa4a065d1d7 | Power Supply Bay | power       | enabled | offline |
| 46f1980f-a467-477d-9be5-4eebf6b73eca | RTC_Voltage      | voltage     | enabled | ok      |
| 56de7567-4c58-44a8-a914-09a996415770 | SC_1_E810        | temperature | enabled | offline |
| 6d90b4ff-4848-45be-ad23-9d062e88aa48 | SC_2_E810        | temperature | enabled | ok      |
| 7e9becff-fa84-4ff0-9090-181dd954ac6d | SSD_0_TEMP       | temperature | enabled | ok      |
| dcf701dc-31cc-456d-8d0a-48e36bb2b75c | SSD_1_TEMP       | temperature | enabled | ok      |
| dc65862a-1541-4b2c-b99a-8745a90154db | SYS_FAN_1A       | fan         | enabled | ok      |
| 3eed2b05-6f40-4ae9-8cdd-5582852f9de7 | SYS_FAN_1B       | fan         | enabled | ok      |
| 2d240eda-99f9-4501-9e4d-baa8d7f1c99b | SYS_FAN_2A       | fan         | enabled | ok      |
| 4b3798f9-3df2-4198-97b3-42501d3b107c | SYS_FAN_2B       | fan         | enabled | ok      |
| b31d3025-5c2c-4de3-94ac-8aa06318d9a6 | SYS_PCH_TEMP     | temperature | enabled | ok      |
| e52bbf0f-e89a-434c-9439-bad7c0eb0b21 | SYS_V1.05        | voltage     | enabled | ok      |
| 77047b32-742b-4e27-b604-5110dbfd2890 | SYS_V12          | voltage     | enabled | ok      |
| c3eb333b-ddff-4019-9f88-2038a84be82b | SYS_V3.3         | voltage     | enabled | ok      |
| 8bc7ad33-4e59-4391-938e-03629028d2bd | SYS_V5           | voltage     | enabled | ok      |
+--------------------------------------+------------------+-------------+---------+---------+
[XXXXXX@controller-0 ~(keystone_admin)]$
```

## Data has populated... looks good

## Remove BMC information from subcloud

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ system host-show 1 | grep bm
| bm_ip                 | 2607:f160:10:9249:ce:40a:0:e015                                      |
| bm_type               | redfish                                                              |
| bm_username           | K8Sctl                                                               |
[XXXXXX@controller-0 ~(keystone_admin)]$ system host-show 1
+-----------------------+----------------------------------------------------------------------+
| Property              | Value                                                                |
+-----------------------+----------------------------------------------------------------------+
| action                | none                                                                 |
| administrative        | locked                                                               |
| availability          | online                                                               |
| bm_ip                 | 2607:f160:10:9249:ce:40a:0:e015                                      |
| bm_type               | redfish                                                              |
| bm_username           | K8Sctl                                                               |
| boot_device           | /dev/disk/by-path/pci-0000:c3:00.0-nvme-1                            |
| capabilities          | {u'stor_function': u'monitor', u'Personality': u'Controller-Active'} |
| clock_synchronization | ptp                                                                  |
| config_applied        | 6c90a90a-4017-4bb9-9dab-198f5b76d18f                                 |
| config_status         | None                                                                 |
| config_target         | 6c90a90a-4017-4bb9-9dab-198f5b76d18f                                 |
| console               | ttyS0,115200                                                         |
| created_at            | 2023-10-24T23:15:23.347829+00:00                                     |
| device_image_update   | None                                                                 |
| hostname              | controller-0                                                         |
| id                    | 1                                                                    |
| install_output        | text                                                                 |
| install_state         | None                                                                 |
| install_state_info    | None                                                                 |
| inv_state             | inventoried                                                          |
| invprovision          | provisioned                                                          |
| location              | {}                                                                   |
| mgmt_ip               | 2607:f160:10:809f:ce:40a:0:1                                         |
| mgmt_mac              | b4:96:91:b5:5e:54                                                    |
| operational           | disabled                                                             |
| personality           | controller                                                           |
| reboot_needed         | False                                                                |
| reserved              | False                                                                |
| rootfs_device         | /dev/disk/by-path/pci-0000:c3:00.0-nvme-1                            |
| serialid              | None                                                                 |
| software_load         | 21.12                                                                |
| subfunction_avail     | online                                                               |
| subfunction_oper      | disabled                                                             |
| subfunctions          | controller,worker,lowlatency                                         |
| task                  |                                                                      |
| tboot                 | false                                                                |
| ttys_dcd              | None                                                                 |
| updated_at            | 2023-10-30T22:53:10.478382+00:00                                     |
| uptime                | 9752                                                                 |
| uuid                  | 166fa19c-d4a5-4d3e-aec3-a09bf8a04f85                                 |
| vim_progress_status   | services-disabled                                                    |
+-----------------------+----------------------------------------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$
[XXXXXX@controller-0 ~(keystone_admin)]$ system host-update 1 bm_type=none
+-----------------------+-------------------------------------------+
| Property              | Value                                     |
+-----------------------+-------------------------------------------+
| action                | none                                      |
| administrative        | locked                                    |
| availability          | online                                    |
| bm_ip                 | None                                      |
| bm_type               | none                                      |
| bm_username           | None                                      |
| boot_device           | /dev/disk/by-path/pci-0000:c3:00.0-nvme-1 |
| capabilities          | {u'stor_function': u'monitor'}            |
| clock_synchronization | ptp                                       |
| config_applied        | 6c90a90a-4017-4bb9-9dab-198f5b76d18f      |
| config_status         | None                                      |
| config_target         | 6c90a90a-4017-4bb9-9dab-198f5b76d18f      |
| console               | ttyS0,115200                              |
| created_at            | 2023-10-24T23:15:23.347829+00:00          |
| device_image_update   | None                                      |
| hostname              | controller-0                              |
| id                    | 1                                         |
| install_output        | text                                      |
| install_state         | None                                      |
| install_state_info    | None                                      |
| inv_state             | inventoried                               |
| invprovision          | provisioned                               |
| location              | {}                                        |
| mgmt_ip               | 2607:f160:10:809f:ce:40a:0:1              |
| mgmt_mac              | b4:96:91:b5:5e:54                         |
| operational           | disabled                                  |
| personality           | controller                                |
| reboot_needed         | False                                     |
| reserved              | False                                     |
| rootfs_device         | /dev/disk/by-path/pci-0000:c3:00.0-nvme-1 |
| serialid              | None                                      |
| software_load         | 21.12                                     |
| subfunction_avail     | online                                    |
| subfunction_oper      | disabled                                  |
| subfunctions          | controller,worker,lowlatency              |
| task                  |                                           |
| tboot                 | false                                     |
| ttys_dcd              | None                                      |
| updated_at            | 2023-10-30T22:53:10.478382+00:00          |
| uptime                | 9752                                      |
| uuid                  | 166fa19c-d4a5-4d3e-aec3-a09bf8a04f85      |
| vim_progress_status   | services-disabled                         |
+-----------------------+-------------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$

[XXXXXX@controller-0 ~(keystone_admin)]$ system host-show 1 | grep bm
| bm_ip                 | None                                                                 |
| bm_type               | none                                                                 |
| bm_username           | None                                                                 |
[XXXXXX@controller-0 ~(keystone_admin)]$ system host-show 1
+-----------------------+----------------------------------------------------------------------+
| Property              | Value                                                                |
+-----------------------+----------------------------------------------------------------------+
| action                | none                                                                 |
| administrative        | locked                                                               |
| availability          | online                                                               |
| bm_ip                 | None                                                                 |
| bm_type               | none                                                                 |
| bm_username           | None                                                                 |
| boot_device           | /dev/disk/by-path/pci-0000:c3:00.0-nvme-1                            |
| capabilities          | {u'stor_function': u'monitor', u'Personality': u'Controller-Active'} |
| clock_synchronization | ptp                                                                  |
| config_applied        | 6c90a90a-4017-4bb9-9dab-198f5b76d18f                                 |
| config_status         | None                                                                 |
| config_target         | 6c90a90a-4017-4bb9-9dab-198f5b76d18f                                 |
| console               | ttyS0,115200                                                         |
| created_at            | 2023-10-24T23:15:23.347829+00:00                                     |
| device_image_update   | None                                                                 |
| hostname              | controller-0                                                         |
| id                    | 1                                                                    |
| install_output        | text                                                                 |
| install_state         | None                                                                 |
| install_state_info    | None                                                                 |
| inv_state             | inventoried                                                          |
| invprovision          | provisioned                                                          |
| location              | {}                                                                   |
| mgmt_ip               | 2607:f160:10:809f:ce:40a:0:1                                         |
| mgmt_mac              | b4:96:91:b5:5e:54                                                    |
| operational           | disabled                                                             |
| personality           | controller                                                           |
| reboot_needed         | False                                                                |
| reserved              | False                                                                |
| rootfs_device         | /dev/disk/by-path/pci-0000:c3:00.0-nvme-1                            |
| serialid              | None                                                                 |
| software_load         | 21.12                                                                |
| subfunction_avail     | online                                                               |
| subfunction_oper      | disabled                                                             |
| subfunctions          | controller,worker,lowlatency                                         |
| task                  |                                                                      |
| tboot                 | false                                                                |
| ttys_dcd              | None                                                                 |
| updated_at            | 2023-10-30T22:54:10.402735+00:00                                     |
| uptime                | 9752                                                                 |
| uuid                  | 166fa19c-d4a5-4d3e-aec3-a09bf8a04f85                                 |
| vim_progress_status   | services-disabled                                                    |
+-----------------------+----------------------------------------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$
```

## Removed with no issue, tests are success....

