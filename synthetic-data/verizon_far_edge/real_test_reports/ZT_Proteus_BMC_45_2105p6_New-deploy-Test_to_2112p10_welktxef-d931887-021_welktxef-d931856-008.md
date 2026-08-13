# ZT .45 BMC firmware validation
# 10/24/23 James Patchett

## Target Controller Rchltxfe-c000000-001
Controller-0 iLO 2607:f160:a:d02e:cd:fe0::8000 
Controller-1 iLO 2607:f160:a:d02e:cd:fe0::8001
Worker-0 iLO 2607:f160:a:d02e:cd:fe0::8002 
OAM 2607:f160:0:3043:cd:290:0:10



## Target Subcloud welktxef-d931887-021 (currently on controller 2607:f160:0:3049:cd:290:0:10 ) 
OAM 2607:f160:10:9249:ce:40a:0:f409
BMC 2607:f160:10:9249:ce:40a:0:e015

ipmitool -I lanplus -U XXXXXX -P XXXXXX -H 2607:f160:10:9249:ce:40a:0:e015 sol activate

## Target Subcloud welktxef-d931856-008
OAM: 2607:f160:10:80b1:ce:40a:0:f408
BMC: 2607:f160:10:80b1:ce:40a:0:e008

ipmitool -I lanplus -U XXXXXX -P XXXXXX -H 2607:f160:10:80b1:ce:40a:0:e008 sol activate

## Baseline record of controller and subcloud
### Controller:

```log
controller-0:~$ source /etc/platform/openrc
[XXXXXX@controller-0 ~(keystone_admin)]$ dcmanager subcloud list
+----+----------------------+------------+--------------+---------------+---------+
| id | name                 | management | availability | deploy status | sync    |
+----+----------------------+------------+--------------+---------------+---------+
|  5 | welktxef-d931887-021 | managed    | online       | complete      | in-sync |
|  6 | welktxef-d931856-008 | managed    | online       | complete      | in-sync |
+----+----------------------+------------+--------------+---------------+---------+
[XXXXXX@controller-0 ~(keystone_admin)]$ system show
+------------------------+--------------------------------------+
| Property               | Value                                |
+------------------------+--------------------------------------+
| contact                | james.patchett@verizon.com           |
| created_at             | 2023-09-28T20:30:38.051313+00:00     |
| description            | Wind River Cloud Platform 21.05      |
| distributed_cloud_role | systemcontroller                     |
| https_enabled          | True                                 |
| latitude               | None                                 |
| location               | None                                 |
| longitude              | None                                 |
| name                   | rchltxfe-c000000-001                 |
| region_name            | RegionOne                            |
| sdn_enabled            | False                                |
| security_feature       | spectre_meltdown_v1                  |
| service_project_name   | services                             |
| software_version       | 21.12                                |
| system_mode            | duplex                               |
| system_type            | Standard                             |
| timezone               | UTC                                  |
| updated_at             | 2023-10-23T23:20:34.259400+00:00     |
| uuid                   | 688e92e8-82aa-4d3d-935f-2b186742acbb |
| vswitch_type           | none                                 |
+------------------------+--------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ system application-list
+--------------------------+----------+-----------------------------------+----------------------------------------+----------+-------------------------------------------------------------------------+
| application              | version  | manifest name                     | manifest file                          | status   | progress                                                                |
+--------------------------+----------+-----------------------------------+----------------------------------------+----------+-------------------------------------------------------------------------+
| cert-manager             | 21.12-28 | cert-manager-manifest             | certmanager-manifest.yaml              | applied  | completed                                                               |
| nginx-ingress-controller | 21.12-18 | nginx-ingress-controller-manifest | nginx_ingress_controller_manifest.yaml | applied  | Application update from version 21.05-16 to version 21.12-18 completed. |
| oidc-auth-apps           | 21.12-61 | oidc-auth-manifest                | manifest.yaml                          | applied  | completed                                                               |
| platform-integ-apps      | 21.12-46 | platform-integration-manifest     | manifest.yaml                          | uploaded | completed                                                               |
| rook-ceph-apps           | 1.0-5    | rook-ceph-manifest                | manifest.yaml                          | uploaded | completed                                                               |
+--------------------------+----------+-----------------------------------+----------------------------------------+----------+-------------------------------------------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ sw-patch query
      Patch ID         RR  Release  Patch State
=====================  ==  =======  ===========
WRCP_21.05_PATCH_0001  N    21.05    Committed
WRCP_21.05_PATCH_0002  Y    21.05    Committed
WRCP_21.05_PATCH_0003  N    21.05    Committed
WRCP_21.05_PATCH_0004  N    21.05    Committed
WRCP_21.05_PATCH_0005  N    21.05    Committed
WRCP_21.05_PATCH_0006  N    21.05    Committed
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

[XXXXXX@controller-0 ~(keystone_admin)]$
[XXXXXX@controller-0 ~(keystone_admin)]$ dcmanager subcloud list
+----+----------------------+------------+--------------+---------------+---------+
| id | name                 | management | availability | deploy status | sync    |
+----+----------------------+------------+--------------+---------------+---------+
|  5 | welktxef-d931887-021 | managed    | online       | complete      | in-sync |
|  6 | welktxef-d931856-008 | managed    | online       | complete      | in-sync |
+----+----------------------+------------+--------------+---------------+---------+
[XXXXXX@controller-0 ~(keystone_admin)]$
[XXXXXX@controller-0 ~(keystone_admin)]$ fm alarm-list

[XXXXXX@controller-0 ~(keystone_admin)]$




```


### Subclouds firmware query 

```log

[XXXXXX@vcpe-jumpserver ~]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/UpdateService/FirmwareInventory/BMC | jq
{
  "@odata.context": "/redfish/v1/$metadata#SoftwareInventory.SoftwareInventory",
  "@odata.etag": "\"1698085132\"",
  "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/BMC",
  "@odata.type": "#SoftwareInventory.v1_2_3.SoftwareInventory",
  "Id": "BMC",
  "Name": "BMC",
  "Updateable": true,
  "Version": "0.45.00"
}
[XXXXXX@vcpe-jumpserver ~]$
[XXXXXX@vcpe-jumpserver ~]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/UpdateService/FirmwareInventory/BMC | jq
{
  "@odata.context": "/redfish/v1/$metadata#SoftwareInventory.SoftwareInventory",
  "@odata.etag": "\"1697725242\"",
  "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/BMC",
  "@odata.type": "#SoftwareInventory.v1_2_3.SoftwareInventory",
  "Id": "BMC",
  "Name": "BMC",
  "Updateable": true,
  "Version": "0.45.00"
}
[XXXXXX@vcpe-jumpserver ~]$

```

### Running automation on subcloud to deploy with recently updated 21.12P10 controller


### Removing subcloud and wiping disks for redeployment

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ dcmanager subcloud unmanage welktxef-d931887-021
+-----------------------------+---------------------------------+
| Field                       | Value                           |
+-----------------------------+---------------------------------+
| id                          | 5                               |
| name                        | welktxef-d931887-021            |
| description                 | Wind River Cloud Platform 21.05 |
| location                    | welktxef-d931887-021            |
| software_version            | 21.12                           |
| management                  | unmanaged                       |
| availability                | online                          |
| deploy_status               | complete                        |
| management_subnet           | 2607:f160:10:809f::/64          |
| management_start_ip         | 2607:f160:10:809f:ce:40a::      |
| management_end_ip           | 2607:f160:10:809f:ce:40a:0:f    |
| management_gateway_ip       | 2607:f160:10:809f:ce:28::       |
| systemcontroller_gateway_ip | 2607:f160:0:3042:cd:28::        |
| group_id                    | 1                               |
| created_at                  | 2023-10-02T19:29:24.044196      |
| updated_at                  | 2023-10-24T22:28:35.209578      |
+-----------------------------+---------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ dcmanager subcloud unmanage welktxef-d931856-008
+-----------------------------+---------------------------------+
| Field                       | Value                           |
+-----------------------------+---------------------------------+
| id                          | 6                               |
| name                        | welktxef-d931856-008            |
| description                 | Wind River Cloud Platform 21.05 |
| location                    | welktxef-d931856-008            |
| software_version            | 21.12                           |
| management                  | unmanaged                       |
| availability                | online                          |
| deploy_status               | complete                        |
| management_subnet           | 2607:f160:10:80bb::/64          |
| management_start_ip         | 2607:f160:10:80bb:ce:40a::      |
| management_end_ip           | 2607:f160:10:80bb:ce:40a:0:f    |
| management_gateway_ip       | 2607:f160:10:80bb:ce:23::       |
| systemcontroller_gateway_ip | 2607:f160:0:3042:cd:28::        |
| group_id                    | 1                               |
| created_at                  | 2023-10-02T21:56:39.788890      |
| updated_at                  | 2023-10-24T22:28:47.194375      |
+-----------------------------+---------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$

NOW on the Subclouds Console 

/etc/motd.d/10-system:


====================================================================
         SYSTEM: welktxef-d931856-008
====================================================================

controller-0:~$ sudo -i
Password:
XXXXXX wipedisk
This will result in the loss of all data on the hard drives and
will require this node to be re-installed.
The following disks will be wiped:
    /dev/nvme0n1
    /dev/nvme0n1p5
    /dev/nvme0n1p6

Are you absolutely sure? [y/n] y
Type 'wipediskscompletely' to confirm: wipediskscompletely
Wiping /dev/nvme0n1p5...
/dev/nvme0n1p5: 8 bytes were erased at offset 0x00000218 (LVM2_member): 4c 56 4d 32 20 30 30 31
Trying to unmount /dev/nvme0n1p5
Warning! /dev/nvme0n1p5 is not mounted
34+0 records in
34+0 records out
17408 bytes (17 kB) copied, 0.000103917 s, 168 MB/s
34+0 records in
34+0 records out
17408 bytes (17 kB) copied, 0.00014657 s, 119 MB/s
Wiping /dev/nvme0n1p6...
/dev/nvme0n1p6: 8 bytes were erased at offset 0x00000218 (LVM2_member): 4c 56 4d 32 20 30 30 31
Trying to unmount /dev/nvme0n1p6
Warning! /dev/nvme0n1p6 is not mounted
34+0 records in
34+0 records out
17408 bytes (17 kB) copied, 0.000149986 s, 116 MB/s
34+0 records in
34+0 records out
17408 bytes (17 kB) copied, 0.000145302 s, 120 MB/s
Skipping wipe backup partition /dev/nvme0n1p1...
Wiping partition /dev/nvme0n1p2...
/dev/nvme0n1p2: 8 bytes were erased at offset 0x00000036 (vfat): 46 41 54 31 36 20 20 20
/dev/nvme0n1p2: 1 bytes were erased at offset 0x00000000 (vfat): eb
/dev/nvme0n1p2: 2 bytes were erased at offset 0x000001fe (vfat): 55 aa
Trying to unmount /dev/nvme0n1p2
/dev/nvme0n1p2 has been successfully unmounted
34+0 records in
34+0 records out
17408 bytes (17 kB) copied, 0.000677678 s, 25.7 MB/s
34+0 records in
34+0 records out
17408 bytes (17 kB) copied, 0.00105445 s, 16.5 MB/s
Removing partition /dev/nvme0n1p2...
Warning: The kernel is still using the old partition table.
The new table will be used at the next reboot.
The operation has completed successfully.
Wiping partition /dev/nvme0n1p3...
/dev/nvme0n1p3: 2 bytes were erased at offset 0x00000438 (ext4): 53 ef
Trying to unmount /dev/nvme0n1p3
/dev/nvme0n1p3 has been successfully unmounted
34+0 records in
34+0 records out
17408 bytes (17 kB) copied, 0.000525043 s, 33.2 MB/s
34+0 records in
34+0 records out
17408 bytes (17 kB) copied, 0.000400641 s, 43.5 MB/s
Removing partition /dev/nvme0n1p3...
Warning: The kernel is still using the old partition table.
The new table will be used at the next reboot.
The operation has completed successfully.
Wiping partition /dev/nvme0n1p4...
/dev/nvme0n1p4: 2 bytes were erased at offset 0x00000438 (ext4): 53 ef
Removing partition /dev/nvme0n1p4...
Warning: The kernel is still using the old partition table.
The new table will be used at the next reboot.
The operation has completed successfully.
Wiping partition /dev/nvme0n1p5...
Trying to unmount /dev/nvme0n1p5
Warning! /dev/nvme0n1p5 is not mounted
34+0 records in
34+0 records out
17408 bytes (17 kB) copied, 0.000165889 s, 105 MB/s
34+0 records in
34+0 records out
17408 bytes (17 kB) copied, 0.000131294 s, 133 MB/s
Removing partition /dev/nvme0n1p5...
Warning: The kernel is still using the old partition table.
The new table will be used at the next reboot.
The operation has completed successfully.
Wiping partition /dev/nvme0n1p6...
Trying to unmount /dev/nvme0n1p6
Warning! /dev/nvme0n1p6 is not mounted
34+0 records in
34+0 records out
17408 bytes (17 kB) copied, 0.000170698 s, 102 MB/s
34+0 records in
34+0 records out
17408 bytes (17 kB) copied, 0.000204415 s, 85.2 MB/s
Removing partition /dev/nvme0n1p6...
Warning: The kernel is still using the old partition table.
The new table will be used at the next reboot.
The operation has completed successfully.
1+0 records in
1+0 records out
440 bytes (440 B) copied, 9.1497e-05 s, 4.8 MB/s
The disk(s) have been wiped.
controller-0:~#
/etc/motd.d/10-system:


====================================================================
         SYSTEM: welktxef-d931887-021
====================================================================

controller-0:~$ sudo -i
Password:
XXXXXX wipedisk
This will result in the loss of all data on the hard drives and
will require this node to be re-installed.
The following disks will be wiped:
    /dev/nvme0n1
    /dev/nvme0n1p5
    /dev/nvme0n1p6

Are you absolutely sure? [y/n] y
Type 'wipediskscompletely' to confirm: wipediskscompletely
Wiping /dev/nvme0n1p5...
/dev/nvme0n1p5: 8 bytes were erased at offset 0x00000218 (LVM2_member): 4c 56 4d 32 20 30 30 31
Trying to unmount /dev/nvme0n1p5
Warning! /dev/nvme0n1p5 is not mounted
34+0 records in
34+0 records out
17408 bytes (17 kB) copied, 0.000149553 s, 116 MB/s
34+0 records in
34+0 records out
17408 bytes (17 kB) copied, 0.000139568 s, 125 MB/s
Wiping /dev/nvme0n1p6...
/dev/nvme0n1p6: 8 bytes were erased at offset 0x00000218 (LVM2_member): 4c 56 4d 32 20 30 30 31
Trying to unmount /dev/nvme0n1p6
Warning! /dev/nvme0n1p6 is not mounted
34+0 records in
34+0 records out
17408 bytes (17 kB) copied, 0.000146093 s, 119 MB/s
34+0 records in
34+0 records out
17408 bytes (17 kB) copied, 0.000162867 s, 107 MB/s
Skipping wipe backup partition /dev/nvme0n1p1...
Wiping partition /dev/nvme0n1p2...
/dev/nvme0n1p2: 8 bytes were erased at offset 0x00000036 (vfat): 46 41 54 31 36 20 20 20
/dev/nvme0n1p2: 1 bytes were erased at offset 0x00000000 (vfat): eb
/dev/nvme0n1p2: 2 bytes were erased at offset 0x000001fe (vfat): 55 aa
Trying to unmount /dev/nvme0n1p2
/dev/nvme0n1p2 has been successfully unmounted
34+0 records in
34+0 records out
17408 bytes (17 kB) copied, 0.00310546 s, 5.6 MB/s
34+0 records in
34+0 records out
17408 bytes (17 kB) copied, 0.000765987 s, 22.7 MB/s
Removing partition /dev/nvme0n1p2...
Warning: The kernel is still using the old partition table.
The new table will be used at the next reboot.
The operation has completed successfully.
Wiping partition /dev/nvme0n1p3...
/dev/nvme0n1p3: 2 bytes were erased at offset 0x00000438 (ext4): 53 ef
Trying to unmount /dev/nvme0n1p3
/dev/nvme0n1p3 has been successfully unmounted
34+0 records in
34+0 records out
17408 bytes (17 kB) copied, 0.00462125 s, 3.8 MB/s
34+0 records in
34+0 records out
17408 bytes (17 kB) copied, 0.000493613 s, 35.3 MB/s
Removing partition /dev/nvme0n1p3...
Warning: The kernel is still using the old partition table.
The new table will be used at the next reboot.
The operation has completed successfully.
Wiping partition /dev/nvme0n1p4...
/dev/nvme0n1p4: 2 bytes were erased at offset 0x00000438 (ext4): 53 ef
Removing partition /dev/nvme0n1p4...
Warning: The kernel is still using the old partition table.
The new table will be used at the next reboot.
The operation has completed successfully.
Wiping partition /dev/nvme0n1p5...
Trying to unmount /dev/nvme0n1p5
Warning! /dev/nvme0n1p5 is not mounted
34+0 records in
34+0 records out
17408 bytes (17 kB) copied, 0.000190541 s, 91.4 MB/s
34+0 records in
34+0 records out
17408 bytes (17 kB) copied, 0.000174632 s, 99.7 MB/s
Removing partition /dev/nvme0n1p5...
Warning: The kernel is still using the old partition table.
The new table will be used at the next reboot.
The operation has completed successfully.
Wiping partition /dev/nvme0n1p6...
Trying to unmount /dev/nvme0n1p6
Warning! /dev/nvme0n1p6 is not mounted
34+0 records in
34+0 records out
17408 bytes (17 kB) copied, 0.000147488 s, 118 MB/s
34+0 records in
34+0 records out
17408 bytes (17 kB) copied, 0.000199319 s, 87.3 MB/s
Removing partition /dev/nvme0n1p6...
Warning: The kernel is still using the old partition table.
The new table will be used at the next reboot.
The operation has completed successfully.
1+0 records in
1+0 records out
440 bytes (440 B) copied, 0.000108823 s, 4.0 MB/s
The disk(s) have been wiped.
controller-0:~#

ISSUED POWEROFF TO SUBCLOUDS

[XXXXXX@controller-0 ~(keystone_admin)]$ dcmanager subcloud list
+----+----------------------+------------+--------------+---------------+---------+
| id | name                 | management | availability | deploy status | sync    |
+----+----------------------+------------+--------------+---------------+---------+
|  5 | welktxef-d931887-021 | unmanaged  | offline      | complete      | unknown |
|  6 | welktxef-d931856-008 | unmanaged  | offline      | complete      | unknown |
+----+----------------------+------------+--------------+---------------+---------+
[XXXXXX@controller-0 ~(keystone_admin)]$ dcmanager subcloud delete welktxef-d931887-021
[XXXXXX@controller-0 ~(keystone_admin)]$ dcmanager subcloud delete welktxef-d931856-008


```


