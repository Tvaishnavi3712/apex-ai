# ZT .43 BMC firmware validation
# 8/25/23 James Patchett

## Build and setup of environment

## Target Controller Rchltxfe-c000000-001
Controller-0 iLO 2607:f160:a:d02e:cd:fe0::8000 
Controller-1 iLO 2607:f160:a:d02e:cd:fe0::8001
Worker-0 iLO 2607:f160:a:d02e:cd:fe0::8002 
OAM 2607:f160:0:3043:cd:290:0:10



## Target Subcloud welktxef-d931887-021 (currently on controller 2607:f160:0:3049:cd:290:0:10 )
iLO 2607:f160:10:9249:ce:40a:0:e015
OAM 2607:f160:10:9249:ce:40a:0:f409

ipmitool -I lanplus -U XXXXXX -P XXXXXX -H 2607:f160:10:9249:ce:40a:0:e015 sol activate

## Installation of controller complete back to 21.05p6

## Installation of Subcloud complete back to 21.05p6


## Baseline record of controller and subcloud
### Controller:

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ system show
+------------------------+--------------------------------------+
| Property               | Value                                |
+------------------------+--------------------------------------+
| contact                | demo.engineer@verizon.com              |
| created_at             | 2023-08-26T04:43:17.345039+00:00     |
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
| software_version       | 21.05                                |
| system_mode            | duplex                               |
| system_type            | Standard                             |
| timezone               | UTC                                  |
| updated_at             | 2023-08-28T17:07:34.990840+00:00     |
| uuid                   | 85d98699-635d-490f-ae18-ba3302ed8605 |
| vswitch_type           | none                                 |
+------------------------+--------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$
[XXXXXX@controller-0 ~(keystone_admin)]$ system oam-show
+-----------------+--------------------------------------+
| Property        | Value                                |
+-----------------+--------------------------------------+
| created_at      | 2023-08-26T04:44:49.344247+00:00     |
| isystem_uuid    | 85d98699-635d-490f-ae18-ba3302ed8605 |
| oam_c0_ip       | 2607:f160:0:3043:cd:290:0:11         |
| oam_c1_ip       | 2607:f160:0:3043:cd:290:0:12         |
| oam_floating_ip | 2607:f160:0:3043:cd:290:0:10         |
| oam_gateway_ip  | 2607:f160:0:3043:cd:28::             |
| oam_subnet      | 2607:f160:0:3043::/64                |
| updated_at      | None                                 |
| uuid            | d94befa0-1fc3-4644-8570-cd08a4ec9a10 |
+-----------------+--------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$
[XXXXXX@controller-0 ~(keystone_admin)]$ sw-patch query
      Patch ID         RR  Release  Patch State
=====================  ==  =======  ===========
WRCP_21.05_PATCH_0001  N    21.05    Committed
WRCP_21.05_PATCH_0002  Y    21.05    Committed
WRCP_21.05_PATCH_0003  N    21.05    Committed
WRCP_21.05_PATCH_0004  N    21.05    Committed
WRCP_21.05_PATCH_0005  N    21.05     Applied
WRCP_21.05_PATCH_0006  N    21.05     Applied

[XXXXXX@controller-0 ~(keystone_admin)]$
[XXXXXX@controller-0 ~(keystone_admin)]$ dcmanager subcloud list
+----+----------------------+------------+--------------+---------------+---------+
| id | name                 | management | availability | deploy status | sync    |
+----+----------------------+------------+--------------+---------------+---------+
|  1 | welktxef-d931887-021 | managed    | online       | complete      | in-sync |
+----+----------------------+------------+--------------+---------------+---------+
[XXXXXX@controller-0 ~(keystone_admin)]$
[XXXXXX@controller-0 ~(keystone_admin)]$ fm alarm-list

[XXXXXX@controller-0 ~(keystone_admin)]$
[XXXXXX@controller-0 ~(keystone_admin)]$ system application-list
+--------------------------+----------+-----------------------------------+-------------------------------+----------+-----------+
| application              | version  | manifest name                     | manifest file                 | status   | progress  |
+--------------------------+----------+-----------------------------------+-------------------------------+----------+-----------+
| cert-manager             | 21.05-17 | cert-manager-manifest             | certmanager-manifest.yaml     | applied  | completed |
| nginx-ingress-controller | 21.05-16 | nginx-ingress-controller-manifest | nginx_ingress_controller_mani | applied  | completed |
|                          |          |                                   | fest.yaml                     |          |           |
|                          |          |                                   |                               |          |           |
| oidc-auth-apps           | 21.05-44 | oidc-auth-manifest                | manifest.yaml                 | applied  | completed |
| platform-integ-apps      | 21.05-30 | platform-integration-manifest     | manifest.yaml                 | uploaded | completed |
| rook-ceph-apps           | 1.0-5    | rook-ceph-manifest                | manifest.yaml                 | uploaded | completed |
| wr-analytics             | 21.06-2  | analytics-armada-manifest         | wr-analytics.yaml             | applied  | completed |
+--------------------------+----------+-----------------------------------+-------------------------------+----------+-----------+
[XXXXXX@controller-0 ~(keystone_admin)]$

```

### Subcloud:

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ system show
+------------------------+--------------------------------------+
| Property               | Value                                |
+------------------------+--------------------------------------+
| contact                | None                                 |
| created_at             | 2023-08-28T20:43:54.718946+00:00     |
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
| software_version       | 21.05                                |
| system_mode            | simplex                              |
| system_type            | All-in-one                           |
| timezone               | UTC                                  |
| updated_at             | 2023-08-28T21:30:15.870814+00:00     |
| uuid                   | 1e26f91c-9dd3-4461-93e8-b0ae27b4e7e0 |
| vswitch_type           | none                                 |
+------------------------+--------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ system oam-show
+----------------+---------------------------------------+
| Property       | Value                                 |
+----------------+---------------------------------------+
| created_at     | 2023-08-28T20:46:02.053885+00:00      |
| isystem_uuid   | 1e26f91c-9dd3-4461-93e8-b0ae27b4e7e0  |
| oam_end_ip     | 2607:f160:10:9249:ffff:ffff:ffff:fffe |
| oam_gateway_ip | 2607:f160:10:9249:ce:28::             |
| oam_ip         | 2607:f160:10:9249:ce:40a:0:f409       |
| oam_start_ip   | 2607:f160:10:9249::1                  |
| oam_subnet     | 2607:f160:10:9249::/64                |
| updated_at     | None                                  |
| uuid           | 21adbc65-6c2b-46a7-b85d-a58d1152ed90  |
+----------------+---------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ sw-patch query
      Patch ID         RR  Release  Patch State
=====================  ==  =======  ===========
WRCP_21.05_PATCH_0001  N    21.05    Committed
WRCP_21.05_PATCH_0002  Y    21.05    Committed
WRCP_21.05_PATCH_0003  N    21.05    Committed
WRCP_21.05_PATCH_0004  N    21.05    Committed
WRCP_21.05_PATCH_0005  N    21.05     Applied
WRCP_21.05_PATCH_0006  N    21.05     Applied

[XXXXXX@controller-0 ~(keystone_admin)]$
[XXXXXX@controller-0 ~(keystone_admin)]$ system application-list
+--------------------------+----------+-----------------------------------+-------------------------------+----------+-----------+
| application              | version  | manifest name                     | manifest file                 | status   | progress  |
+--------------------------+----------+-----------------------------------+-------------------------------+----------+-----------+
| cert-manager             | 21.05-17 | cert-manager-manifest             | certmanager-manifest.yaml     | applied  | completed |
| nginx-ingress-controller | 21.05-16 | nginx-ingress-controller-manifest | nginx_ingress_controller_mani | applied  | completed |
|                          |          |                                   | fest.yaml                     |          |           |
|                          |          |                                   |                               |          |           |
| oidc-auth-apps           | 21.05-44 | oidc-auth-manifest                | manifest.yaml                 | applied  | completed |
| platform-integ-apps      | 21.05-30 | platform-integration-manifest     | manifest.yaml                 | applied  | completed |
| rook-ceph-apps           | 1.0-5    | rook-ceph-manifest                | manifest.yaml                 | uploaded | completed |
+--------------------------+----------+-----------------------------------+-------------------------------+----------+-----------+
[XXXXXX@controller-0 ~(keystone_admin)]$
[XXXXXX@controller-0 ~(keystone_admin)]$ fm alarm-list

[XXXXXX@controller-0 ~(keystone_admin)]$

```


### Subcloud firmware query 
```log
[XXXXXX@welktxefnce-h-pe1util-vm01 wr-installer]$  curl -gsk -u XXXXXX:XXXXXX -X GET https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/UpdateService/FirmwareInventory/BMC | jq
{
  "@odata.context": "/redfish/v1/$metadata#SoftwareInventory.SoftwareInventory",
  "@odata.etag": "\"1694029572\"",
  "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/BMC",
  "@odata.type": "#SoftwareInventory.v1_2_3.SoftwareInventory",
  "Id": "BMC",
  "Name": "BMC",
  "Updateable": true,
  "Version": "0.43.00"
}
[XXXXXX@welktxefnce-h-pe1util-vm01 wr-installer]$
```

### All set to upgrade controller and subcloud to 21.12p10

### Following Wrapper MOP 21.12p10

### audit CGTS volumes with subcloud

Running audit from controller:

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ mkdir wrcp-cgts
[XXXXXX@controller-0 ~(keystone_admin)]$ mv wrcp-21.05-cgts_volume_audit-v1.0.zip wrcp-cgts/
[XXXXXX@controller-0 ~(keystone_admin)]$ cd wrcp-cgts/
[XXXXXX@controller-0 wrcp-cgts(keystone_admin)]$ ls
wrcp-21.05-cgts_volume_audit-v1.0.zip
[XXXXXX@controller-0 wrcp-cgts(keystone_admin)]$ sudo -i
Password:
XXXXXX
controller-0:~#
controller-0:~# cd /opt/
controller-0:/opt# ls
backups  branding  collectd  containerd  dc  dc-vault  deploy  etcd  extension  extracharts  patching  platform  platform-backup
controller-0:/opt# mkdir wrdiags/
controller-0:/opt# mkdir wrdiags/misc
controller-0:/opt# cd wrdiags/misc
controller-0:/opt/wrdiags/misc# chown -R XXXXXX /opt/wrdiags/
controller-0:/opt/wrdiags/misc# exit
logout
[XXXXXX@controller-0 wrcp-cgts(keystone_admin)]$ ls
wrcp-21.05-cgts_volume_audit-v1.0.zip
[XXXXXX@controller-0 wrcp-cgts(keystone_admin)]$ cp wrcp-21.05-cgts_volume_audit-v1.0.zip /opt/wrdiags/misc/
[XXXXXX@controller-0 wrcp-cgts(keystone_admin)]$ cd /opt/wrdiags/misc/
[XXXXXX@controller-0 misc(keystone_admin)]$ unzip *.zip
Archive:  wrcp-21.05-cgts_volume_audit-v1.0.zip
   creating: wrcp-21.05-cgts_volume_audit/
  inflating: wrcp-21.05-cgts_volume_audit/cgts_volume_audit.sh
  inflating: wrcp-21.05-cgts_volume_audit/ansible.cfg
  inflating: wrcp-21.05-cgts_volume_audit/cr_play.yaml
  inflating: wrcp-21.05-cgts_volume_audit/subcloud_play.yaml
[XXXXXX@controller-0 misc(keystone_admin)]$ cd wrcp-21.05-cgts_volume_audit/
[XXXXXX@controller-0 wrcp-21.05-cgts_volume_audit(keystone_admin)]$ XXXXXX_password=XXXXXX
[XXXXXX@controller-0 wrcp-21.05-cgts_volume_audit(keystone_admin)]$ cat <<EOF > cr.inv
> [all:vars]
> ansible_user=XXXXXX
> ansible_password=${XXXXXX_password}
> ansible_become_password=${XXXXXX_password}
> [systemcontroller]
> 2607:f160:0:3043:cd:290:0:10
> EOF
[XXXXXX@controller-0 wrcp-21.05-cgts_volume_audit(keystone_admin)]$ bash cgts_volume_audit.sh

PLAY [all] *********************************************************************

TASK [Create /tmp/wr_cgts_volume_audit] ****************************************
changed: [2607:f160:0:3043:cd:290:0:10]

TASK [Copy the subcloud playbook to the central region] ************************
changed: [2607:f160:0:3043:cd:290:0:10] => (item=subcloud_play.yaml)
changed: [2607:f160:0:3043:cd:290:0:10] => (item=ansible.cfg)

TASK [Get System Controller name] **********************************************
changed: [2607:f160:0:3043:cd:290:0:10]

TASK [Create output file] ******************************************************
changed: [2607:f160:0:3043:cd:290:0:10]

TASK [Create subcloud inventory file] ******************************************
changed: [2607:f160:0:3043:cd:290:0:10]

TASK [Run subcloud playbook] ***************************************************
changed: [2607:f160:0:3043:cd:290:0:10]

TASK [Fetch /tmp/wr_cgts_volume_audit/rchltxfe-c000000-001_cgts_volume.csv] ****
changed: [2607:f160:0:3043:cd:290:0:10]

TASK [Delete /tmp/wr_cgts_volume_audit] ****************************************
changed: [2607:f160:0:3043:cd:290:0:10]

PLAY RECAP *********************************************************************
2607:f160:0:3043:cd:290:0:10 : ok=8    changed=8    unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.05-cgts_volume_audit(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.05-cgts_volume_audit(keystone_admin)]$ results_file=$(ls -rt results/*_cgts_volume.csv | tail -n1)
[XXXXXX@controller-0 wrcp-21.05-cgts_volume_audit(keystone_admin)]$ cat ${results_file}
[XXXXXX@controller-0 wrcp-21.05-cgts_volume_audit(keystone_admin)]$ ls -lrt archive/
total 8
-rw-r--r-- 1 XXXXXX sys_protected 2382 Sep  7 18:41 ansible_cgts_volume_20230907184056.log
-rw-r--r-- 1 XXXXXX sys_protected 1450 Sep  7 18:41 2023-09-07_cgts_volume_audit.log
[XXXXXX@controller-0 wrcp-21.05-cgts_volume_audit(keystone_admin)]$ more 2023-09-07_cgts_volume_audit.log
2023-09-07_cgts_volume_audit.log: No such file or directory
[XXXXXX@controller-0 wrcp-21.05-cgts_volume_audit(keystone_admin)]$ more archive/2023-09-07_cgts_volume_audit.log
2023-09-07 18:40:56 audit begins
2023-09-07 18:40:56 base directory: /opt/wrdiags/misc/wrcp-21.05-cgts_volume_audit
2023-09-07 18:40:56 archive: /opt/wrdiags/misc/wrcp-21.05-cgts_volume_audit/archive
2023-09-07 18:40:56 results directory: /opt/wrdiags/misc/wrcp-21.05-cgts_volume_audit/results
2023-09-07 18:40:56 results file: /opt/wrdiags/misc/wrcp-21.05-cgts_volume_audit/results/2023-09-07_cgts_volume.csv
2023-09-07 18:40:56 ansible play begins, using inventory file /opt/wrdiags/misc/wrcp-21.05-cgts_volume_audit/cr.inv, play file /opt/wrdiags/mis
c/wrcp-21.05-cgts_volume_audit/cr_play.yaml and log file /opt/wrdiags/misc/wrcp-21.05-cgts_volume_audit/archive/ansible_cgts_volume_20230907184
056.log
2023-09-07 18:41:15 ansible finishes
2023-09-07 18:41:15 creating master csv file with headers
2023-09-07 18:41:15 appending /opt/wrdiags/misc/wrcp-21.05-cgts_volume_audit/2023-09-07_rchltxfe-c000000-001_cgts_volume.csv/2607:f160:0:3043:c
d:290:0:10/tmp/wr_cgts_volume_audit/rchltxfe-c000000-001_cgts_volume.csv to /opt/wrdiags/misc/wrcp-21.05-cgts_volume_audit/results/2023-09-07_c
gts_volume.csv
2023-09-07 18:41:15 /opt/wrdiags/misc/wrcp-21.05-cgts_volume_audit/2023-09-07_rchltxfe-c000000-001_cgts_volume.csv/2607:f160:0:3043:cd:290:0:10
/tmp/wr_cgts_volume_audit/rchltxfe-c000000-001_cgts_volume.csv appended to /opt/wrdiags/misc/wrcp-21.05-cgts_volume_audit/results/2023-09-07_cg
ts_volume.csv
2023-09-07 18:41:15 Deleting individual csv files
[XXXXXX@controller-0 wrcp-21.05-cgts_volume_audit(keystone_admin)]$ more archive/ansible_cgts_volume_20230907184056.log
2023-09-07 18:40:57,457 passlib.registry registered 'md5_crypt' handler: <class 'passlib.handlers.md5_crypt.md5_crypt'>
2023-09-07 18:40:57,461 p=2124841 u=XXXXXX |  PLAY [all] *********************************************************************
2023-09-07 18:40:57,468 p=2124841 u=XXXXXX |  TASK [Create /tmp/wr_cgts_volume_audit] ****************************************
2023-09-07 18:40:58,603 p=2124841 u=XXXXXX |  changed: [2607:f160:0:3043:cd:290:0:10]
2023-09-07 18:40:58,607 p=2124841 u=XXXXXX |  TASK [Copy the subcloud playbook to the central region] ************************
2023-09-07 18:41:00,662 p=2124841 u=XXXXXX |  changed: [2607:f160:0:3043:cd:290:0:10] => (item=subcloud_play.yaml)
2023-09-07 18:41:02,486 p=2124841 u=XXXXXX |  changed: [2607:f160:0:3043:cd:290:0:10] => (item=ansible.cfg)
2023-09-07 18:41:02,490 p=2124841 u=XXXXXX |  TASK [Get System Controller name] **********************************************
2023-09-07 18:41:04,898 p=2124841 u=XXXXXX |  changed: [2607:f160:0:3043:cd:290:0:10]
2023-09-07 18:41:04,902 p=2124841 u=XXXXXX |  TASK [Create output file] ******************************************************
2023-09-07 18:41:05,940 p=2124841 u=XXXXXX |  changed: [2607:f160:0:3043:cd:290:0:10]
2023-09-07 18:41:05,943 p=2124841 u=XXXXXX |  TASK [Create subcloud inventory file] ******************************************
2023-09-07 18:41:08,510 p=2124841 u=XXXXXX |  changed: [2607:f160:0:3043:cd:290:0:10]
2023-09-07 18:41:08,513 p=2124841 u=XXXXXX |  TASK [Run subcloud playbook] ***************************************************
2023-09-07 18:41:12,980 p=2124841 u=XXXXXX |  changed: [2607:f160:0:3043:cd:290:0:10]
2023-09-07 18:41:12,985 p=2124841 u=XXXXXX |  TASK [Fetch /tmp/wr_cgts_volume_audit/rchltxfe-c000000-001_cgts_volume.csv] ****
2023-09-07 18:41:14,162 p=2124841 u=XXXXXX |  changed: [2607:f160:0:3043:cd:290:0:10]
2023-09-07 18:41:14,166 p=2124841 u=XXXXXX |  TASK [Delete /tmp/wr_cgts_volume_audit] ****************************************
2023-09-07 18:41:15,199 p=2124841 u=XXXXXX |  changed: [2607:f160:0:3043:cd:290:0:10]
2023-09-07 18:41:15,200 p=2124841 u=XXXXXX |  PLAY RECAP *********************************************************************
2023-09-07 18:41:15,200 p=2124841 u=XXXXXX |  2607:f160:0:3043:cd:290:0:10 : ok=8    changed=8    unreachable=0    failed=0
[XXXXXX@controller-0 wrcp-21.05-cgts_volume_audit(keystone_admin)]$
```

### followed procedure, no extra cgts-volumes to deal with

### next step in mop "resizing file systems"
### Controller:

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ . /etc/platform/openrc; for i in {controller-{0,1},worker-0}; do system host-fs-list ${i}; done; system controllerfs-list

+--------------------------------------+---------+-------------+----------------+
| UUID                                 | FS Name | Size in GiB | Logical Volume |
+--------------------------------------+---------+-------------+----------------+
| fb639f09-57c1-4ee7-bfa9-381e6e0a6c6b | backup  | 55          | backup-lv      |
| 8abfb873-7712-4cb7-9cc3-0f7a12855616 | docker  | 30          | docker-lv      |
| 7ef01b61-0365-4152-a7b2-e3d90e08247e | kubelet | 10          | kubelet-lv     |
| 98aaa036-c021-4a15-9e9c-ed03d9995a1e | scratch | 16          | scratch-lv     |
+--------------------------------------+---------+-------------+----------------+
+--------------------------------------+---------+-------------+----------------+
| UUID                                 | FS Name | Size in GiB | Logical Volume |
+--------------------------------------+---------+-------------+----------------+
| bbb16755-489b-42cb-82e1-b697be10c074 | backup  | 55          | backup-lv      |
| 326a8272-e385-4981-b52a-ba88e95e55d5 | docker  | 30          | docker-lv      |
| 835dff4e-e586-4e5d-bc89-80d01f148695 | kubelet | 10          | kubelet-lv     |
| 2c154a73-2bef-4c32-9ddb-422e809eeea1 | scratch | 16          | scratch-lv     |
+--------------------------------------+---------+-------------+----------------+
+--------------------------------------+---------+-------------+----------------+
| UUID                                 | FS Name | Size in GiB | Logical Volume |
+--------------------------------------+---------+-------------+----------------+
| 250961a7-4367-4773-823f-20caeb55ed40 | docker  | 30          | docker-lv      |
| b897fcdb-8bd3-4816-9b91-bb490d0ba85b | kubelet | 10          | kubelet-lv     |
| 0175e383-9e9b-49c2-bc3a-ed1e03c82a36 | scratch | 4           | scratch-lv     |
+--------------------------------------+---------+-------------+----------------+
+--------------------------------------+---------------------+------+-----------------------+------------+-----------+
| UUID                                 | FS Name             | Size | Logical Volume        | Replicated | State     |
|                                      |                     | in   |                       |            |           |
|                                      |                     | GiB  |                       |            |           |
+--------------------------------------+---------------------+------+-----------------------+------------+-----------+
| 07d54785-5aaa-4f77-9cf5-f2d9ee2b764f | dc-vault            | 15   | dc-vault-lv           | True       | available |
| 152ea036-b33f-4653-8238-a571ce9f40bd | extension           | 1    | extension-lv          | True       | available |
| 25fe7fe4-752c-4aad-9f70-9db59b0c136f | docker-distribution | 32   | dockerdistribution-lv | True       | available |
| 76e27a6c-27de-44a2-9611-8544543d8850 | platform            | 40   | platform-lv           | True       | available |
| c7ed638b-58f6-416e-8c49-a4d2831a5728 | database            | 10   | pgsql-lv              | True       | available |
| d0273139-7234-40d6-af33-ce59b00ae647 | etcd                | 5    | etcd-lv               | True       | available |
+--------------------------------------+---------------------+------+-----------------------+------------+-----------+
[XXXXXX@controller-0 ~(keystone_admin)]$
[XXXXXX@controller-0 ~(keystone_admin)]$

```

### Sizes for controller are wrong, will have to resize them:

### checking subcloud:

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ . /etc/platform/openrc; system host-fs-list controller-0; system controllerfs-list
+--------------------------------------+---------+-------------+----------------+
| UUID                                 | FS Name | Size in GiB | Logical Volume |
+--------------------------------------+---------+-------------+----------------+
| 457a25ad-bc7b-431f-ba70-4516686a0af5 | backup  | 25          | backup-lv      |
| c82e789d-0caf-4f07-b16b-7bedf97ddf41 | docker  | 30          | docker-lv      |
| 990d5dc8-b730-4a59-9a2c-d947f4f31dbc | kubelet | 10          | kubelet-lv     |
| f5a4a9f1-a6f7-4720-bfad-24a871f5ddce | scratch | 16          | scratch-lv     |
+--------------------------------------+---------+-------------+----------------+
+--------------------------------------+---------------------+------+-----------------------+------------+-----------+
| UUID                                 | FS Name             | Size | Logical Volume        | Replicated | State     |
|                                      |                     | in   |                       |            |           |
|                                      |                     | GiB  |                       |            |           |
+--------------------------------------+---------------------+------+-----------------------+------------+-----------+
| 5a155c30-a6fc-4e0a-b299-1db44ba11949 | etcd                | 5    | etcd-lv               | True       | available |
| 641f7319-296e-4389-9e07-6690d380f26d | platform            | 10   | platform-lv           | True       | available |
| 68a95597-e2c8-45c5-8dd7-948377e49b27 | docker-distribution | 32   | dockerdistribution-lv | True       | available |
| 8431b70e-2e2f-4b95-86ab-7714ba109d5a | extension           | 1    | extension-lv          | True       | available |
| f2c36c3c-eaee-4e8e-900f-24f5b5b01129 | database            | 10   | pgsql-lv              | True       | available |
+--------------------------------------+---------------------+------+-----------------------+------------+-----------+
[XXXXXX@controller-0 ~(keystone_admin)]$
```

### subcloud requires resizing as well, with docker hostfs at 30gb


### Controller resizing: 

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ source /etc/platform/openrc
[XXXXXX@controller-0 ~(keystone_admin)]$ unzip wrcp-21.05-resize_docker-v1.3.zip
Archive:  wrcp-21.05-resize_docker-v1.3.zip
   creating: wrcp-21.05-resize_docker/
  inflating: wrcp-21.05-resize_docker/create_cgts_volume.yaml
  inflating: wrcp-21.05-resize_docker/current-subclouds.yaml
  inflating: wrcp-21.05-resize_docker/confirm_cgts_volumes.yaml
  inflating: wrcp-21.05-resize_docker/resize_fs.yaml
  inflating: wrcp-21.05-resize_docker/current-system-controller.yaml
  inflating: wrcp-21.05-resize_docker/ansible.cfg
  inflating: wrcp-21.05-resize_docker/vault-client-keyring.py
  inflating: wrcp-21.05-resize_docker/sanity.yaml
  inflating: wrcp-21.05-resize_docker/resize_hostfs.yaml
[XXXXXX@controller-0 ~(keystone_admin)]$ rm -f wrcp-21.05-resize_docker-v1.3.zip wrcp-21.05-resize_docker-v1.3.zip.md5
[XXXXXX@controller-0 ~(keystone_admin)]$ ls
ad_ca.pem                          k8s_root_ca_cert.pem                         welktxef-d931887-021-install-values.yaml
ansible_20230826044127.log         k8s_root_ca_key.pem                          wind-river-cloud-platform-deployment-manager-2.0.6.tgz
ansible.log                        license.lic                                  wind-river-cloud-platform-deployment-manager.yaml
ansible_netapp_20230826050635.log  localhost.yml                                wra-21.06-volume-resize-v1.3-allinone.zip
central-cloud-deployment.yaml      master-bootstrap-and-deploy-playbook.yaml    wrap
deployment-config.yaml             welktxef-d5400002-003-bootstrap-values.yaml  wrap-21.06-2
dex-ca.pem                         welktxef-d5400002-003-deploy-standard.yaml   wrcp-21.05-resize_docker
dex-cert.pem                       welktxef-d5400002-003-deploy-values.yaml     wrcp-21.05-resize_docker-mop-1-system-controllers-v1.3.pdf
dex-key.pem                        welktxef-d5400002-003-install-values.yaml    wrcp-21.05-resize_docker-mop-2-subclouds-v1.3.pdf
dex-overrides.yaml                 welktxef-d931887-021-bootstrap-values.yaml   wrcp-21.05-resize_docker-v1.3_allinone.zip
dm-helm-overrides.yaml             welktxef-d931887-021-deploy-standard.yaml    wrcp-cgts
dm-playbook-overrides.yaml         welktxef-d931887-021-deploy-values.yaml      wsregistry.mtce.vzwops.com
[XXXXXX@controller-0 ~(keystone_admin)]$ cd /home/XXXXXX/wrcp-21.05-resize_docker
[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$ sudo show-certs.sh | grep -E '^\s+Residual Time'
Password:
	 XXXXXX Time	:  389d
	 Residual Time	:  352d
	 Residual Time	:  201d
	 Residual Time	:  2602d
	 Residual Time	:  4299d
	 Residual Time	:  2603d
	 Residual Time	:  1812d
	 Residual Time	:  167d
	 Residual Time	:  2603d
	 Residual Time	:  3637d
	 Residual Time	:  3637d
	 Residual Time	:  3637d
	 Residual Time	:  355d
	 Residual Time	:  4299d
	 Residual Time	:  173d
	 Residual Time	:  173d
[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$ sw-patch query | grep WRCP_21.05_PATCH_0006
WRCP_21.05_PATCH_0006  N    21.05     Applied
[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$ XXXXXX_password=XXXXXX
[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$ cat <<EOF > secret.yml
> ---
> ansible_user: XXXXXX
> ansible_password: ${XXXXXX_password}
> ansible_become_password: ${XXXXXX_password}
> EOF
[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$ keyring get ansible XXXXXX | wc -l
0
[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$ sudo keyring set ansible XXXXXX
Password for 'XXXXXX' in 'ansible':
[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$ keyring get ansible XXXXXX | wc -l
1
[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$ ansible-vault encrypt secret.yml
Encryption successful
[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$ echo -e '[system-controller]\nlocalhost' > controller
[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$ ANSIBLE_LOG_PATH=./sanity_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook --inventory controller --extra-vars "scenario=current" \
> sanity.yaml --extra-vars "@secret.yml" 0</dev/null
ERROR! Syntax Error while loading YAML.
  found character that cannot start any token

The error appears to have been in '/home/XXXXXX/wrcp-21.05-resize_docker/secret.yml': line 3, column 19, but may
be elsewhere in the file depending on the exact syntax problem.

[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$ passwd
Changing password for user XXXXXX.
Changing password for XXXXXX.
(current) UNIX password:
XXXXXX password:
XXXXXX new password:
XXXXXX all authentication tokens updated successfully.
[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$ XXXXXX_password=XXXXXX
[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$ cat <<EOF > secret.yml
> ---
> ansible_user: XXXXXX
> ansible_password: ${XXXXXX_password}
> ansible_become_password: ${XXXXXX_password}
> EOF
[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$ keyring get ansible XXXXXX | wc -l
1
[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$ ANSIBLE_LOG_PATH=./sanity_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook --inventory controller --extra-vars "scenario=current" \
> sanity.yaml --extra-vars "@secret.yml" 0</dev/null

PLAY [all] *********************************************************************

TASK [Gathering Facts] *********************************************************
ok: [localhost]

TASK [Read in parameter file] **************************************************
ok: [localhost]

TASK [set expected Fortville firmware version] *********************************
ok: [localhost]

TASK [set expected N3000 firmware version] *************************************
ok: [localhost]

TASK [create directory /home/XXXXXX/sanity] **********************************
changed: [localhost -> localhost]

TASK [delete existing file /home/XXXXXX/sanity/output_list] ******************
ok: [localhost -> localhost]

TASK [create file /home/XXXXXX/sanity/output_list] ***************************
changed: [localhost -> localhost]

TASK [get host patch status] ***************************************************
changed: [localhost]

TASK [validate host patch status] **********************************************
skipping: [localhost]

TASK [get host status] *********************************************************
changed: [localhost]

TASK [validate host status] ****************************************************
skipping: [localhost]

TASK [get current alarms] ******************************************************
changed: [localhost]

TASK [validate current alarms] *************************************************
skipping: [localhost]

TASK [get vim status] **********************************************************
changed: [localhost]

TASK [validate vim status] *****************************************************
skipping: [localhost]

TASK [calculate / partition expected usage] ************************************
changed: [localhost]

TASK [validate / partition free space] *****************************************
skipping: [localhost]

TASK [validate /opt/dc-vault partition free space] *****************************
skipping: [localhost]

TASK [identify N3000 NICs] *****************************************************
changed: [localhost]

TASK [get N3000 NICs firmware version] *****************************************

TASK [validate N3000 NICs firmware version] ************************************

TASK [get N3000 NICs MAC] ******************************************************

TASK [validate N3000 NICs MACs] ************************************************

TASK [identify Fortville NICs] *************************************************
changed: [localhost]

TASK [get Fortville NICs firmware version] *************************************
changed: [localhost] => (item=ens2f0)
changed: [localhost] => (item=ens2f1)
changed: [localhost] => (item=ens3f0)
changed: [localhost] => (item=ens3f1)

TASK [validate Fortville NICs firmware version] ********************************
skipping: [localhost] => (item=ens2f0)
skipping: [localhost] => (item=ens2f1)
skipping: [localhost] => (item=ens3f0)
skipping: [localhost] => (item=ens3f1)

TASK [get Fortville NICs MAC] **************************************************
changed: [localhost] => (item=ens2f0)
changed: [localhost] => (item=ens2f1)
changed: [localhost] => (item=ens3f0)
changed: [localhost] => (item=ens3f1)

TASK [validate Fortville NICs MACs] ********************************************
skipping: [localhost] => (item=ens2f0)
skipping: [localhost] => (item=ens2f1)
skipping: [localhost] => (item=ens3f0)
skipping: [localhost] => (item=ens3f1)

TASK [identify accelerators] ***************************************************
changed: [localhost]

TASK [retrieve device information] *********************************************

TASK [output device show information] ******************************************

TASK [retrieve device information] *********************************************

TASK [output field information] ************************************************

TASK [validate sriov_numvfs for Mount Bryce] ***********************************

TASK [validate driver and sriov_vf_driver fields] ******************************

TASK [validate extra_info field] ***********************************************

TASK [get pod status] **********************************************************
changed: [localhost]

TASK [validate pod status] *****************************************************
skipping: [localhost]

TASK [get system applications] *************************************************
changed: [localhost]

TASK [validate system applications] ********************************************
skipping: [localhost] => (item=cert-manager:21.05-17)
skipping: [localhost] => (item=nginx-ingress-controller:21.05-16)
skipping: [localhost] => (item=oidc-auth-apps:21.05-44)

PLAY RECAP *********************************************************************
localhost                  : ok=19   changed=14   unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$ cat /home/XXXXXX/sanity/output_list
[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$

[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$ docker_size=250gib
[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$ docker_distribution_size=100gib
[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$ ANSIBLE_LOG_PATH=./resize_fs_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook resize_fs.yaml \
> -e "{\"hfs_docker\":${docker_size},\"cfs_docker_distribution\":${docker_distribution_size}}" \
> 0</dev/null

PLAY [all] *********************************************************************

TASK [Retrieve list of controllers] ********************************************
changed: [localhost]

TASK [Retrieve distributed cloud role] *****************************************
changed: [localhost]

TASK [Confirm cgts volumes] ****************************************************
skipping: [localhost] => (item=controller-0)
skipping: [localhost] => (item=controller-1)

TASK [Retrieve controller filesystems and sizes] *******************************
changed: [localhost]

TASK [Store requested controller filesystem sizes] *****************************
ok: [localhost] => (item=dc-vault 15)
ok: [localhost] => (item=extension 1)
ok: [localhost] => (item=docker-distribution 32)
ok: [localhost] => (item=platform 40)
ok: [localhost] => (item=database 10)
ok: [localhost] => (item=etcd 5)

TASK [Build controller filesystem resizing parms] ******************************
skipping: [localhost] => (item=dc-vault 15)
skipping: [localhost] => (item=extension 1)
skipping: [localhost] => (item=docker-distribution 32)
skipping: [localhost] => (item=platform 40)
skipping: [localhost] => (item=database 10)
skipping: [localhost] => (item=etcd 5)

TASK [Resize all controller filesystems] ***************************************
skipping: [localhost]

TASK [Wait for all controller filesystems to be resized and fully sync] ********
skipping: [localhost]

TASK [Wait for any 400.001 alarm to clear] *************************************
skipping: [localhost]

TASK [Resize host filesystems] *************************************************
included: /home/XXXXXX/wrcp-21.05-resize_docker/resize_hostfs.yaml for localhost
included: /home/XXXXXX/wrcp-21.05-resize_docker/resize_hostfs.yaml for localhost

TASK [Retrieve host filesystems and sizes] *************************************
changed: [localhost]

TASK [Store requested host filesystem sizes] ***********************************
ok: [localhost] => (item=backup 55)
ok: [localhost] => (item=docker 30)
ok: [localhost] => (item=kubelet 10)
ok: [localhost] => (item=scratch 16)

TASK [Build hostfs resizing parms] *********************************************
skipping: [localhost] => (item=backup 55)
skipping: [localhost] => (item=docker 30)
skipping: [localhost] => (item=kubelet 10)
skipping: [localhost] => (item=scratch 16)

TASK [Resize all host filesystems] *********************************************
skipping: [localhost]

TASK [Retrieve host filesystems and sizes] *************************************
changed: [localhost]

TASK [Store requested host filesystem sizes] ***********************************
ok: [localhost] => (item=backup 55)
ok: [localhost] => (item=docker 30)
ok: [localhost] => (item=kubelet 10)
ok: [localhost] => (item=scratch 16)

TASK [Build hostfs resizing parms] *********************************************
skipping: [localhost] => (item=backup 55)
skipping: [localhost] => (item=docker 30)
skipping: [localhost] => (item=kubelet 10)
skipping: [localhost] => (item=scratch 16)

TASK [Resize all host filesystems] *********************************************
skipping: [localhost]

TASK [Wait for any 250.001 alarm to clear] *************************************
changed: [localhost]

PLAY RECAP *********************************************************************
localhost                  : ok=11   changed=6    unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$

[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$ docker_size=250
[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$ docker_distribution_size=100
[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$ ANSIBLE_LOG_PATH=./resize_fs_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook resize_fs.yaml \
> -e "{\"hfs_docker\":${docker_size},\"cfs_docker_distribution\":${docker_distribution_size}}" \
> 0</dev/null

PLAY [all] *********************************************************************

TASK [Retrieve list of controllers] ********************************************
changed: [localhost]

TASK [Retrieve distributed cloud role] *****************************************
changed: [localhost]

TASK [Confirm cgts volumes] ****************************************************
skipping: [localhost] => (item=controller-0)
skipping: [localhost] => (item=controller-1)

TASK [Retrieve controller filesystems and sizes] *******************************
changed: [localhost]

TASK [Store requested controller filesystem sizes] *****************************
ok: [localhost] => (item=dc-vault 15)
ok: [localhost] => (item=extension 1)
ok: [localhost] => (item=docker-distribution 32)
ok: [localhost] => (item=platform 40)
ok: [localhost] => (item=database 10)
ok: [localhost] => (item=etcd 5)

TASK [Build controller filesystem resizing parms] ******************************
skipping: [localhost] => (item=dc-vault 15)
skipping: [localhost] => (item=extension 1)
ok: [localhost] => (item=docker-distribution 32)
skipping: [localhost] => (item=platform 40)
skipping: [localhost] => (item=database 10)
skipping: [localhost] => (item=etcd 5)

TASK [Resize all controller filesystems] ***************************************
changed: [localhost]

TASK [Wait for all controller filesystems to be resized and fully sync] ********
FAILED - RETRYING: Wait for all controller filesystems to be resized and fully sync (720 retries left).
FAILED - RETRYING: Wait for all controller filesystems to be resized and fully sync (719 retries left).
FAILED - RETRYING: Wait for all controller filesystems to be resized and fully sync (718 retries left).
changed: [localhost]

TASK [Wait for any 400.001 alarm to clear] *************************************
FAILED - RETRYING: Wait for any 400.001 alarm to clear (300 retries left).
FAILED - RETRYING: Wait for any 400.001 alarm to clear (299 retries left).
FAILED - RETRYING: Wait for any 400.001 alarm to clear (298 retries left).
FAILED - RETRYING: Wait for any 400.001 alarm to clear (297 retries left).
FAILED - RETRYING: Wait for any 400.001 alarm to clear (296 retries left).
FAILED - RETRYING: Wait for any 400.001 alarm to clear (295 retries left).
FAILED - RETRYING: Wait for any 400.001 alarm to clear (294 retries left).
FAILED - RETRYING: Wait for any 400.001 alarm to clear (293 retries left).
FAILED - RETRYING: Wait for any 400.001 alarm to clear (292 retries left).
FAILED - RETRYING: Wait for any 400.001 alarm to clear (291 retries left).
FAILED - RETRYING: Wait for any 400.001 alarm to clear (290 retries left).
FAILED - RETRYING: Wait for any 400.001 alarm to clear (289 retries left).
FAILED - RETRYING: Wait for any 400.001 alarm to clear (288 retries left).
FAILED - RETRYING: Wait for any 400.001 alarm to clear (287 retries left).
FAILED - RETRYING: Wait for any 400.001 alarm to clear (286 retries left).
FAILED - RETRYING: Wait for any 400.001 alarm to clear (285 retries left).
FAILED - RETRYING: Wait for any 400.001 alarm to clear (284 retries left).
FAILED - RETRYING: Wait for any 400.001 alarm to clear (283 retries left).
changed: [localhost]

TASK [Resize host filesystems] *************************************************
included: /home/XXXXXX/wrcp-21.05-resize_docker/resize_hostfs.yaml for localhost
included: /home/XXXXXX/wrcp-21.05-resize_docker/resize_hostfs.yaml for localhost

TASK [Retrieve host filesystems and sizes] *************************************
changed: [localhost]

TASK [Store requested host filesystem sizes] ***********************************
ok: [localhost] => (item=backup 55)
ok: [localhost] => (item=docker 30)
ok: [localhost] => (item=kubelet 10)
ok: [localhost] => (item=scratch 16)

TASK [Build hostfs resizing parms] *********************************************
skipping: [localhost] => (item=backup 55)
ok: [localhost] => (item=docker 30)
skipping: [localhost] => (item=kubelet 10)
skipping: [localhost] => (item=scratch 16)

TASK [Resize all host filesystems] *********************************************
changed: [localhost]

TASK [Retrieve host filesystems and sizes] *************************************
changed: [localhost]

TASK [Store requested host filesystem sizes] ***********************************
ok: [localhost] => (item=backup 55)
ok: [localhost] => (item=docker 30)
ok: [localhost] => (item=kubelet 10)
ok: [localhost] => (item=scratch 16)

TASK [Build hostfs resizing parms] *********************************************
skipping: [localhost] => (item=backup 55)
ok: [localhost] => (item=docker 30)
skipping: [localhost] => (item=kubelet 10)
skipping: [localhost] => (item=scratch 16)

TASK [Resize all host filesystems] *********************************************
changed: [localhost]

TASK [Wait for any 250.001 alarm to clear] *************************************
FAILED - RETRYING: Wait for any 250.001 alarm to clear (300 retries left).
changed: [localhost]

PLAY RECAP *********************************************************************
localhost                  : ok=19   changed=11   unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$ fm alarm-list

[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$ lsblk -o NAME,SIZE --noheadings --list | grep docker
cgts--vg-docker--lv              250G
cgts--vg-dockerdistribution--lv  100G
[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$ ANSIBLE_LOG_PATH=./sanity_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook --inventory controller --extra-vars "scenario=current" \
> sanity.yaml --extra-vars "@secret.yml" 0</dev/null

PLAY [all] *********************************************************************

TASK [Gathering Facts] *********************************************************
ok: [localhost]

TASK [Read in parameter file] **************************************************
ok: [localhost]

TASK [set expected Fortville firmware version] *********************************
ok: [localhost]

TASK [set expected N3000 firmware version] *************************************
ok: [localhost]

TASK [create directory /home/XXXXXX/sanity] **********************************
ok: [localhost -> localhost]

TASK [delete existing file /home/XXXXXX/sanity/output_list] ******************
changed: [localhost -> localhost]

TASK [create file /home/XXXXXX/sanity/output_list] ***************************
changed: [localhost -> localhost]

TASK [get host patch status] ***************************************************
changed: [localhost]

TASK [validate host patch status] **********************************************
skipping: [localhost]

TASK [get host status] *********************************************************
changed: [localhost]

TASK [validate host status] ****************************************************
skipping: [localhost]

TASK [get current alarms] ******************************************************
changed: [localhost]

TASK [validate current alarms] *************************************************
skipping: [localhost]

TASK [get vim status] **********************************************************
changed: [localhost]

TASK [validate vim status] *****************************************************
skipping: [localhost]

TASK [calculate / partition expected usage] ************************************
changed: [localhost]

TASK [validate / partition free space] *****************************************
skipping: [localhost]

TASK [validate /opt/dc-vault partition free space] *****************************
skipping: [localhost]

TASK [identify N3000 NICs] *****************************************************
changed: [localhost]

TASK [get N3000 NICs firmware version] *****************************************

TASK [validate N3000 NICs firmware version] ************************************

TASK [get N3000 NICs MAC] ******************************************************

TASK [validate N3000 NICs MACs] ************************************************

TASK [identify Fortville NICs] *************************************************
changed: [localhost]

TASK [get Fortville NICs firmware version] *************************************
changed: [localhost] => (item=ens2f0)
changed: [localhost] => (item=ens2f1)
changed: [localhost] => (item=ens3f0)
changed: [localhost] => (item=ens3f1)

TASK [validate Fortville NICs firmware version] ********************************
skipping: [localhost] => (item=ens2f0)
skipping: [localhost] => (item=ens2f1)
skipping: [localhost] => (item=ens3f0)
skipping: [localhost] => (item=ens3f1)

TASK [get Fortville NICs MAC] **************************************************
changed: [localhost] => (item=ens2f0)
changed: [localhost] => (item=ens2f1)
changed: [localhost] => (item=ens3f0)
changed: [localhost] => (item=ens3f1)

TASK [validate Fortville NICs MACs] ********************************************
skipping: [localhost] => (item=ens2f0)
skipping: [localhost] => (item=ens2f1)
skipping: [localhost] => (item=ens3f0)
skipping: [localhost] => (item=ens3f1)

TASK [identify accelerators] ***************************************************
changed: [localhost]

TASK [retrieve device information] *********************************************

TASK [output device show information] ******************************************

TASK [retrieve device information] *********************************************

TASK [output field information] ************************************************

TASK [validate sriov_numvfs for Mount Bryce] ***********************************

TASK [validate driver and sriov_vf_driver fields] ******************************

TASK [validate extra_info field] ***********************************************

TASK [get pod status] **********************************************************
changed: [localhost]

TASK [validate pod status] *****************************************************
skipping: [localhost]

TASK [get system applications] *************************************************
changed: [localhost]

TASK [validate system applications] ********************************************
skipping: [localhost] => (item=cert-manager:21.05-17)
skipping: [localhost] => (item=nginx-ingress-controller:21.05-16)
skipping: [localhost] => (item=oidc-auth-apps:21.05-44)

PLAY RECAP *********************************************************************
localhost                  : ok=19   changed=14   unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$ cat /home/XXXXXX/sanity/output_list
[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$

[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$ . /etc/platform/openrc; for i in {controller-{0,1},worker-0}; do system host-fs-list ${i}; done; system controllerfs-list
+--------------------------------------+---------+-------------+----------------+
| UUID                                 | FS Name | Size in GiB | Logical Volume |
+--------------------------------------+---------+-------------+----------------+
| fb639f09-57c1-4ee7-bfa9-381e6e0a6c6b | backup  | 55          | backup-lv      |
| 8abfb873-7712-4cb7-9cc3-0f7a12855616 | docker  | 250         | docker-lv      |
| 7ef01b61-0365-4152-a7b2-e3d90e08247e | kubelet | 10          | kubelet-lv     |
| 98aaa036-c021-4a15-9e9c-ed03d9995a1e | scratch | 16          | scratch-lv     |
+--------------------------------------+---------+-------------+----------------+
+--------------------------------------+---------+-------------+----------------+
| UUID                                 | FS Name | Size in GiB | Logical Volume |
+--------------------------------------+---------+-------------+----------------+
| bbb16755-489b-42cb-82e1-b697be10c074 | backup  | 55          | backup-lv      |
| 326a8272-e385-4981-b52a-ba88e95e55d5 | docker  | 250         | docker-lv      |
| 835dff4e-e586-4e5d-bc89-80d01f148695 | kubelet | 10          | kubelet-lv     |
| 2c154a73-2bef-4c32-9ddb-422e809eeea1 | scratch | 16          | scratch-lv     |
+--------------------------------------+---------+-------------+----------------+
+--------------------------------------+---------+-------------+----------------+
| UUID                                 | FS Name | Size in GiB | Logical Volume |
+--------------------------------------+---------+-------------+----------------+
| 250961a7-4367-4773-823f-20caeb55ed40 | docker  | 30          | docker-lv      |
| b897fcdb-8bd3-4816-9b91-bb490d0ba85b | kubelet | 10          | kubelet-lv     |
| 0175e383-9e9b-49c2-bc3a-ed1e03c82a36 | scratch | 4           | scratch-lv     |
+--------------------------------------+---------+-------------+----------------+
+--------------------------------------+---------------------+------+-----------------------+------------+-----------+
| UUID                                 | FS Name             | Size | Logical Volume        | Replicated | State     |
|                                      |                     | in   |                       |            |           |
|                                      |                     | GiB  |                       |            |           |
+--------------------------------------+---------------------+------+-----------------------+------------+-----------+
| 07d54785-5aaa-4f77-9cf5-f2d9ee2b764f | dc-vault            | 15   | dc-vault-lv           | True       | available |
| 152ea036-b33f-4653-8238-a571ce9f40bd | extension           | 1    | extension-lv          | True       | available |
| 25fe7fe4-752c-4aad-9f70-9db59b0c136f | docker-distribution | 100  | dockerdistribution-lv | True       | available |
| 76e27a6c-27de-44a2-9611-8544543d8850 | platform            | 40   | platform-lv           | True       | available |
| c7ed638b-58f6-416e-8c49-a4d2831a5728 | database            | 10   | pgsql-lv              | True       | available |
| d0273139-7234-40d6-af33-ce59b00ae647 | etcd                | 5    | etcd-lv               | True       | available |
+--------------------------------------+---------------------+------+-----------------------+------------+-----------+
[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$

```


### controller file system resizing is complete moving on to the subcloud

### Subcloud resizing:

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ source /etc/platform/openrc
[XXXXXX@controller-0 ~(keystone_admin)]$ unzip wrcp-21.05-resize_docker-v1.3.zip
unzip:  cannot find or open wrcp-21.05-resize_docker-v1.3.zip, wrcp-21.05-resize_docker-v1.3.zip.zip or wrcp-21.05-resize_docker-v1.3.zip.ZIP.
[XXXXXX@controller-0 ~(keystone_admin)]$ ls
ad_ca.pem                          k8s_root_ca_key.pem                          wind-river-cloud-platform-deployment-manager-2.0.6.tgz
ansible_20230826044127.log         license.lic                                  wind-river-cloud-platform-deployment-manager.yaml
ansible.log                        localhost.yml                                wra-21.06-volume-resize-v1.3-allinone.zip
ansible_netapp_20230826050635.log  master-bootstrap-and-deploy-playbook.yaml    wrap
central-cloud-deployment.yaml      sanity                                       wrap-21.06-2
deployment-config.yaml             welktxef-d5400002-003-bootstrap-values.yaml  wrcp-21.05-resize_docker
dex-ca.pem                         welktxef-d5400002-003-deploy-standard.yaml   wrcp-21.05-resize_docker-mop-1-system-controllers-v1.3.pdf
dex-cert.pem                       welktxef-d5400002-003-deploy-values.yaml     wrcp-21.05-resize_docker-mop-2-subclouds-v1.3.pdf
dex-key.pem                        welktxef-d5400002-003-install-values.yaml    wrcp-21.05-resize_docker-v1.3_allinone.zip
dex-overrides.yaml                 welktxef-d931887-021-bootstrap-values.yaml   wrcp-cgts
dm-helm-overrides.yaml             welktxef-d931887-021-deploy-standard.yaml    wsregistry.mtce.vzwops.com
dm-playbook-overrides.yaml         welktxef-d931887-021-deploy-values.yaml
k8s_root_ca_cert.pem               welktxef-d931887-021-install-values.yaml
[XXXXXX@controller-0 ~(keystone_admin)]$ cd wrcp-21.05-resize_docker
[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$ ls
ansible.cfg                create_cgts_volume.yaml         resize_fs_20230907195155.log  sanity_20230907193903.log  vault-client-keyring.py
ansible.log                current-subclouds.yaml          resize_fs.yaml                sanity_20230907195900.log
confirm_cgts_volumes.yaml  current-system-controller.yaml  resize_hostfs.yaml            sanity.yaml
controller                 resize_fs_20230907194921.log    sanity_20230907193453.log     secret.yml
[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$ rm -f wrcp-21.05-resize_docker-v1.3.zip wrcp-21.05-resize_docker-v1.3.zip.md5
[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$ cd /home/XXXXXX/wrcp-21.05-resize_docker
[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$ sudo show-certs.sh | grep -E '^\s+Residual Time'
Password:
	 XXXXXX Time	:  389d
	 Residual Time	:  352d
	 Residual Time	:  201d
	 Residual Time	:  2602d
	 Residual Time	:  4299d
	 Residual Time	:  2603d
	 Residual Time	:  1812d
	 Residual Time	:  167d
	 Residual Time	:  2603d
	 Residual Time	:  3637d
	 Residual Time	:  3637d
	 Residual Time	:  3637d
	 Residual Time	:  355d
	 Residual Time	:  4299d
	 Residual Time	:  173d
	 Residual Time	:  173d
[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$ XXXXXX_password=XXXXXX
[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$ cat <<EOF > secret.yml
> ---
> ansible_user: XXXXXX
> ansible_password: "XXXXXX"
> ansible_become_password: "XXXXXX"
> EOF
[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$ keyring get ansible XXXXXX | wc -l
1
[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$ ansible-vault encrypt secret.yml
Encryption successful
[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$ dcmanager subcloud list -c name -c management -c availability -f value | \
> grep -E -v "unmanaged|offline" | awk '{print $1}' > subclouds
[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$ for subcloud in $(cat subclouds); do
> echo ${subcloud}:
> fm --os-region-name ${subcloud} --os-endpoint-type admin alarm-list --mgmt_affecting | \
> awk -F \| '$6 ~ / True / { print $0 }'
> done
welktxef-d931887-021:
[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$ cd /home/XXXXXX/wrcp-21.05-resize_docker
[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$ docker_size=58
[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$ docker_distribution_size=32
[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$ volume_size=1000
[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$ ANSIBLE_LOG_PATH=./resize_fs_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook -i subclouds resize_fs.yaml -e '@secret.yml' \
> -e "{\"partitions\":[${volume_size}],\"hfs_docker\":${docker_size},
> \"cfs_docker_distribution\":${docker_distribution_size}}" 0</dev/null

PLAY [all] *********************************************************************

TASK [Retrieve list of controllers] ********************************************
changed: [welktxef-d931887-021]

TASK [Retrieve distributed cloud role] *****************************************
changed: [welktxef-d931887-021]

TASK [Confirm cgts volumes] ****************************************************
included: /home/XXXXXX/wrcp-21.05-resize_docker/confirm_cgts_volumes.yaml for welktxef-d931887-021

TASK [Retrieve rootfs disk] ****************************************************
changed: [welktxef-d931887-021]

TASK [Retrieve available space on the rootfs device] ***************************
changed: [welktxef-d931887-021]

TASK [set_fact] ****************************************************************
ok: [welktxef-d931887-021]

TASK [Retrieve partitions present on the rootfs device] ************************
changed: [welktxef-d931887-021]

TASK [Validate number of partitions requested] *********************************
skipping: [welktxef-d931887-021]

TASK [Validate requested partition sizes] **************************************
skipping: [welktxef-d931887-021] => (item=[None, 1000])

TASK [Determine amount of free space after all partitions are allocated] *******
ok: [welktxef-d931887-021] => (item=[None, 1000])

TASK [Display amount of free space after all partitions are allocated] *********
ok: [welktxef-d931887-021] => {
    "msg": "633"
}

TASK [Verify there is enough space to allocate all partitions] *****************
skipping: [welktxef-d931887-021]

TASK [Create new volumes] ******************************************************
included: /home/XXXXXX/wrcp-21.05-resize_docker/create_cgts_volume.yaml for welktxef-d931887-021 => (item=[None, 1000])

TASK [Create a new disk partition] *********************************************
changed: [welktxef-d931887-021]

TASK [fail] ********************************************************************
skipping: [welktxef-d931887-021]

TASK [Wait for the new partition to be ready] **********************************
FAILED - RETRYING: Wait for the new partition to be ready (200 retries left).
FAILED - RETRYING: Wait for the new partition to be ready (199 retries left).
FAILED - RETRYING: Wait for the new partition to be ready (198 retries left).
changed: [welktxef-d931887-021]

TASK [Add the new partition to the cgts volume group] **************************
changed: [welktxef-d931887-021]

TASK [fail] ********************************************************************
skipping: [welktxef-d931887-021]

TASK [Wait for the physical volume to be provisioned] **************************
FAILED - RETRYING: Wait for the physical volume to be provisioned (200 retries left).
changed: [welktxef-d931887-021]

TASK [Retrieve controller filesystems and sizes] *******************************
changed: [welktxef-d931887-021]

TASK [Store requested controller filesystem sizes] *****************************
ok: [welktxef-d931887-021] => (item=etcd 5)
ok: [welktxef-d931887-021] => (item=platform 10)
ok: [welktxef-d931887-021] => (item=docker-distribution 32)
ok: [welktxef-d931887-021] => (item=extension 1)
ok: [welktxef-d931887-021] => (item=database 10)

TASK [Build controller filesystem resizing parms] ******************************
skipping: [welktxef-d931887-021] => (item=etcd 5)
skipping: [welktxef-d931887-021] => (item=platform 10)
skipping: [welktxef-d931887-021] => (item=docker-distribution 32)
skipping: [welktxef-d931887-021] => (item=extension 1)
skipping: [welktxef-d931887-021] => (item=database 10)

TASK [Resize all controller filesystems] ***************************************
skipping: [welktxef-d931887-021]

TASK [Wait for all controller filesystems to be resized and fully sync] ********
skipping: [welktxef-d931887-021]

TASK [Wait for any 400.001 alarm to clear] *************************************
skipping: [welktxef-d931887-021]

TASK [Resize host filesystems] *************************************************
included: /home/XXXXXX/wrcp-21.05-resize_docker/resize_hostfs.yaml for welktxef-d931887-021

TASK [Retrieve host filesystems and sizes] *************************************
changed: [welktxef-d931887-021]

TASK [Store requested host filesystem sizes] ***********************************
ok: [welktxef-d931887-021] => (item=backup 25)
ok: [welktxef-d931887-021] => (item=docker 30)
ok: [welktxef-d931887-021] => (item=kubelet 10)
ok: [welktxef-d931887-021] => (item=scratch 16)

TASK [Build hostfs resizing parms] *********************************************
skipping: [welktxef-d931887-021] => (item=backup 25)
ok: [welktxef-d931887-021] => (item=docker 30)
skipping: [welktxef-d931887-021] => (item=kubelet 10)
skipping: [welktxef-d931887-021] => (item=scratch 16)

TASK [Resize all host filesystems] *********************************************
changed: [welktxef-d931887-021]

TASK [Wait for any 250.001 alarm to clear] *************************************
FAILED - RETRYING: Wait for any 250.001 alarm to clear (300 retries left).
changed: [welktxef-d931887-021]

PLAY RECAP *********************************************************************
welktxef-d931887-021       : ok=22   changed=13   unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$ . /etc/platform/openrc; system host-fs-list controller-0; system controllerfs-list

+--------------------------------------+---------+-------------+----------------+
| UUID                                 | FS Name | Size in GiB | Logical Volume |
+--------------------------------------+---------+-------------+----------------+
| 457a25ad-bc7b-431f-ba70-4516686a0af5 | backup  | 25          | backup-lv      |
| c82e789d-0caf-4f07-b16b-7bedf97ddf41 | docker  | 58          | docker-lv      |
| 990d5dc8-b730-4a59-9a2c-d947f4f31dbc | kubelet | 10          | kubelet-lv     |
| f5a4a9f1-a6f7-4720-bfad-24a871f5ddce | scratch | 16          | scratch-lv     |
+--------------------------------------+---------+-------------+----------------+
+--------------------------------------+---------------------+------+-----------------------+------------+-----------+
| UUID                                 | FS Name             | Size | Logical Volume        | Replicated | State     |
|                                      |                     | in   |                       |            |           |
|                                      |                     | GiB  |                       |            |           |
+--------------------------------------+---------------------+------+-----------------------+------------+-----------+
| 5a155c30-a6fc-4e0a-b299-1db44ba11949 | etcd                | 5    | etcd-lv               | True       | available |
| 641f7319-296e-4389-9e07-6690d380f26d | platform            | 10   | platform-lv           | True       | available |
| 68a95597-e2c8-45c5-8dd7-948377e49b27 | docker-distribution | 32   | dockerdistribution-lv | True       | available |
| 8431b70e-2e2f-4b95-86ab-7714ba109d5a | extension           | 1    | extension-lv          | True       | available |
| f2c36c3c-eaee-4e8e-900f-24f5b5b01129 | database            | 10   | pgsql-lv              | True       | available |
+--------------------------------------+---------------------+------+-----------------------+------------+-----------+
[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$
```

### File system resizing of subcloud is complete.

###  Verify nonrevertive bonding on system controller:

```log
[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$ . /etc/platform/openrc; for host in {controller-{0,1},worker-0}; do for interface in {nfsbond0,pxeboot0}; do system host-if-show ${host} ${interface} | grep -E "primary_reselect \| failure" >/dev/null 2>&1 || echo "ERROR, host ${host} interface ${interface} is not configured w/ primary-reselect=failure"; done; done

[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$
```
### Controller is ok with nonrevertive bonding

### Verify influxDB service is stopped/Disabled on the system controller

```log
[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$ systemctl status influxdb.service
● influxdb.service - InfluxDB open-source, distributed, time series database
   Loaded: loaded (/etc/systemd/system/influxdb.service; enabled; vendor preset: disabled)
   Active: active (running) since Sat 2023-08-26 05:16:04 UTC; 1 weeks 5 days ago
     Docs: https://influxdb.com/docs/
 Main PID: 93743 (sh)
    Tasks: 47
   Memory: 654.5M
   CGroup: /system.slice/influxdb.service
           ├─93743 /bin/sh -c /usr/bin/influxd -config /etc/influxdb/influxdb.conf -pidfile /var/run/influxdb/influxdb.pid  >> /dev/null 2>>...
           └─93744 /usr/bin/influxd -config /etc/influxdb/influxdb.conf -pidfile /var/run/influxdb/influxdb.pid
[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$
```

### influxdb running on system controller, will address after checking subcloud

### subcloud verification:

```log
[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$ systemctl status influxdb.service
● influxdb.service - InfluxDB open-source, distributed, time series database
   Loaded: loaded (/etc/systemd/system/influxdb.service; enabled; vendor preset: disabled)
   Active: active (running) since Wed 2023-09-06 19:46:59 UTC; 24h ago
     Docs: https://influxdb.com/docs/
 Main PID: 3087 (sh)
    Tasks: 10
   Memory: 98.9M
   CGroup: /system.slice/influxdb.service
           ├─3087 /bin/sh -c /usr/bin/influxd -config /etc/influxdb/influxdb.conf -pidfile /var/run/influxdb/influxdb.pid  >> /dev/null 2>> ...
           └─3095 /usr/bin/influxd -config /etc/influxdb/influxdb.conf -pidfile /var/run/influxdb/influxdb.pid
[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$

```

### Subcloud also has influxDB running..

### running mop 1 on controller:

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ unzip wrcp-21.05-disable_influxdb-v1.1-allinone.zip
Archive:  wrcp-21.05-disable_influxdb-v1.1-allinone.zip
  inflating: wrcp-21.05-disable_influxdb-mop-1-system-controllers-v1.1.pdf
  inflating: wrcp-21.05-disable_influxdb-mop-2-subclouds-v1.1.pdf
 extracting: wrcp-21.05-disable_influxdb-v1.1.zip
 extracting: wrcp-21.05-disable_influxdb-v1.1.zip.md5
[XXXXXX@controller-0 ~(keystone_admin)]$ unzip wrcp-21.05-disable_influxdb-v1.1.zip
Archive:  wrcp-21.05-disable_influxdb-v1.1.zip
   creating: wrcp-21.05-disable_influxdb/
  inflating: wrcp-21.05-disable_influxdb/enable_influxdb.yaml
  inflating: wrcp-21.05-disable_influxdb/ansible.cfg
  inflating: wrcp-21.05-disable_influxdb/vault-client-keyring.py
  inflating: wrcp-21.05-disable_influxdb/disable_influxdb.yaml
[XXXXXX@controller-0 ~(keystone_admin)]$ rm -f wrcp-21.05-disable_influxdb-v1.1.zip wrcp-21.05-disable_influxdb-v1.1.zip.md5
[XXXXXX@controller-0 ~(keystone_admin)]$
[XXXXXX@controller-0 ~(keystone_admin)]$ cd /home/XXXXXX/wrcp-21.05-disable_influxdb
[XXXXXX@controller-0 wrcp-21.05-disable_influxdb(keystone_admin)]$ sudo show-certs.sh | grep -E '^\s+Residual Time'
Password:
	 XXXXXX Time	:  389d
	 Residual Time	:  352d
	 Residual Time	:  201d
	 Residual Time	:  2602d
	 Residual Time	:  4299d
	 Residual Time	:  2603d
	 Residual Time	:  1812d
	 Residual Time	:  167d
	 Residual Time	:  2603d
	 Residual Time	:  3637d
	 Residual Time	:  3637d
	 Residual Time	:  3637d
	 Residual Time	:  355d
	 Residual Time	:  4299d
	 Residual Time	:  173d
	 Residual Time	:  173d
[XXXXXX@controller-0 wrcp-21.05-disable_influxdb(keystone_admin)]$ XXXXXX_password=XXXXXX
[XXXXXX@controller-0 wrcp-21.05-disable_influxdb(keystone_admin)]$ cat <<EOF > secret.yml
> ---
> ansible_user: XXXXXX
> ansible_password: ${XXXXXX_password}
> ansible_become_password: ${XXXXXX_password}
> EOF
[XXXXXX@controller-0 wrcp-21.05-disable_influxdb(keystone_admin)]$ keyring get ansible XXXXXX | wc -l
1
[XXXXXX@controller-0 wrcp-21.05-disable_influxdb(keystone_admin)]$ ansible-vault encrypt secret.yml
Encryption successful
[XXXXXX@controller-0 wrcp-21.05-disable_influxdb(keystone_admin)]$ ansible-vault encrypt secret.yml
ERROR! input is already encrypted
[XXXXXX@controller-0 wrcp-21.05-disable_influxdb(keystone_admin)]$ source /etc/platform/openrc
[XXXXXX@controller-0 wrcp-21.05-disable_influxdb(keystone_admin)]$ source /etc/platform/openrc
[XXXXXX@controller-0 wrcp-21.05-disable_influxdb(keystone_admin)]$ cd /home/XXXXXX/wrcp-21.05-disable_influxdb
[XXXXXX@controller-0 wrcp-21.05-disable_influxdb(keystone_admin)]$ ANSIBLE_LOG_PATH=./disable_influxdb_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook -i controller-0,controller-1, disable_influxdb.yaml -e "XXXXXX" \
> 0</dev/null

PLAY [all] *********************************************************************

TASK [Check platform version] **************************************************
changed: [controller-1]
changed: [controller-0]

TASK [Delete process monitoring configuration for influxdb] ********************
changed: [controller-1]
changed: [controller-0]

TASK [Stop process monitoring for influxdb] ************************************
changed: [controller-1]
changed: [controller-0]

TASK [Wait 3 seconds] **********************************************************
Pausing for 3 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [controller-0]

TASK [Remove manifest puppet entries for influxdb] *****************************
changed: [controller-1] => (item=aio)
changed: [controller-0] => (item=aio)
changed: [controller-0] => (item=controller)
changed: [controller-1] => (item=controller)

TASK [Disable collectd output] *************************************************
changed: [controller-0] => (item={u'To': u'\\1ModulePath ""', u'State': u'present', u'Match': u'^(\\s*)ModulePath\\s.*$'})
changed: [controller-1] => (item={u'To': u'\\1ModulePath ""', u'State': u'present', u'Match': u'^(\\s*)ModulePath\\s.*$'})
changed: [controller-0] => (item={u'To': u'', u'State': u'absent', u'Match': u'^\\s*Import\\s.*$'})
changed: [controller-1] => (item={u'To': u'', u'State': u'absent', u'Match': u'^\\s*Import\\s.*$'})
changed: [controller-0] => (item={u'To': u'', u'State': u'absent', u'Match': u'^\\s*LogTraces\\s.*$'})
changed: [controller-1] => (item={u'To': u'', u'State': u'absent', u'Match': u'^\\s*LogTraces\\s.*$'})
changed: [controller-0] => (item={u'To': u'', u'State': u'absent', u'Match': u'^\\s*Encoding\\s.*$'})
changed: [controller-1] => (item={u'To': u'', u'State': u'absent', u'Match': u'^\\s*Encoding\\s.*$'})

TASK [Remove global puppet hieradata entries for collectd] *********************
changed: [controller-1] => (item=module_path)
changed: [controller-0] => (item=module_path)
changed: [controller-1] => (item=plugins)
changed: [controller-0] => (item=plugins)
changed: [controller-1] => (item=log_traces)
changed: [controller-0] => (item=log_traces)
changed: [controller-1] => (item=encoding)
changed: [controller-0] => (item=encoding)

TASK [Populate services list] **************************************************
ok: [controller-1]
ok: [controller-0]

TASK [Stop and disable influxdb service] ***************************************
changed: [controller-1] => (item=influxdb.service)
changed: [controller-0] => (item=influxdb.service)

TASK [Disable collectd interface to influxdb] **********************************
changed: [controller-0]
changed: [controller-1]

TASK [Reset service failed status] *********************************************
changed: [controller-0]
changed: [controller-1]
 [WARNING]: flush_handlers task does not support when conditional


RUNNING HANDLER [restart collectd] *********************************************
changed: [controller-0]
changed: [controller-1]

TASK [Catalog influxdb data files] *********************************************
ok: [controller-1]
ok: [controller-0]

TASK [Delete existing influxdb data files to reclaim disk space] ***************
changed: [controller-0] => (item=/var/lib/influxdb/data/collectd/collectd samples/17)
changed: [controller-1] => (item=/var/lib/influxdb/data/_internal/monitor/10)
changed: [controller-1] => (item=/var/lib/influxdb/data/_internal/monitor/8)
changed: [controller-0] => (item=/var/lib/influxdb/data/collectd/collectd samples/11)
changed: [controller-0] => (item=/var/lib/influxdb/data/collectd/collectd samples/13)
changed: [controller-1] => (item=/var/lib/influxdb/data/_internal/monitor/12)
changed: [controller-1] => (item=/var/lib/influxdb/data/_internal/monitor/13)
changed: [controller-0] => (item=/var/lib/influxdb/data/collectd/collectd samples/21)
changed: [controller-1] => (item=/var/lib/influxdb/data/_internal/monitor/6)
changed: [controller-0] => (item=/var/lib/influxdb/data/collectd/collectd samples/25)
changed: [controller-1] => (item=/var/lib/influxdb/data/_internal/monitor/9)
changed: [controller-0] => (item=/var/lib/influxdb/data/collectd/collectd samples/15)
changed: [controller-1] => (item=/var/lib/influxdb/data/_internal/monitor/7)
changed: [controller-0] => (item=/var/lib/influxdb/data/collectd/collectd samples/19)
changed: [controller-1] => (item=/var/lib/influxdb/data/_internal/monitor/11)
changed: [controller-0] => (item=/var/lib/influxdb/data/collectd/collectd samples/23)
changed: [controller-0] => (item=/var/lib/influxdb/data/_internal/monitor/14)
changed: [controller-0] => (item=/var/lib/influxdb/data/_internal/monitor/26)
changed: [controller-0] => (item=/var/lib/influxdb/data/_internal/monitor/24)
changed: [controller-0] => (item=/var/lib/influxdb/data/_internal/monitor/18)
changed: [controller-0] => (item=/var/lib/influxdb/data/_internal/monitor/20)
changed: [controller-0] => (item=/var/lib/influxdb/data/_internal/monitor/12)
changed: [controller-0] => (item=/var/lib/influxdb/data/_internal/monitor/22)
changed: [controller-0] => (item=/var/lib/influxdb/data/_internal/monitor/16)

TASK [Wait 5 seconds] **********************************************************
Pausing for 5 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [controller-0]

TASK [Verify influxdb process is no longer present] ****************************
changed: [controller-0]
changed: [controller-1]

TASK [Verify influxdb is no longer present] ************************************
changed: [controller-0]
changed: [controller-1]

PLAY RECAP *********************************************************************
controller-0               : ok=17   changed=13   unreachable=0    failed=0
controller-1               : ok=15   changed=13   unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.05-disable_influxdb(keystone_admin)]$

[XXXXXX@controller-0 wrcp-21.05-disable_influxdb(keystone_admin)]$ systemctl status influxdb.service
● influxdb.service - InfluxDB open-source, distributed, time series database
   Loaded: loaded (/etc/systemd/system/influxdb.service; disabled; vendor preset: disabled)
   Active: inactive (dead)
     Docs: https://influxdb.com/docs/
[XXXXXX@controller-0 wrcp-21.05-disable_influxdb(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.05-disable_influxdb(keystone_admin)]$
```

### controller influxDB disabled

### Running mop 2 on subcloud:

```log
[XXXXXX@controller-0 wrcp-21.05-disable_influxdb(keystone_admin)]$ ansible-vault encrypt secret.yml
ERROR! input is already encrypted
[XXXXXX@controller-0 wrcp-21.05-disable_influxdb(keystone_admin)]$ dcmanager subcloud list -c name -c management -c availability -f value | \
> grep -E -v "unmanaged|offline" | awk '{print $1}' > subclouds
[XXXXXX@controller-0 wrcp-21.05-disable_influxdb(keystone_admin)]$ ANSIBLE_LOG_PATH=./disable_influxdb_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook -i subclouds disable_influxdb.yaml -e '@secret.yml' 0</dev/null

PLAY [all] *********************************************************************

TASK [Check platform version] **************************************************
changed: [welktxef-d931887-021]

TASK [Delete process monitoring configuration for influxdb] ********************
changed: [welktxef-d931887-021]

TASK [Stop process monitoring for influxdb] ************************************
changed: [welktxef-d931887-021]

TASK [Wait 3 seconds] **********************************************************
Pausing for 3 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [welktxef-d931887-021]

TASK [Remove manifest puppet entries for influxdb] *****************************
changed: [welktxef-d931887-021] => (item=aio)
changed: [welktxef-d931887-021] => (item=controller)

TASK [Disable collectd output] *************************************************
changed: [welktxef-d931887-021] => (item={u'To': u'\\1ModulePath ""', u'State': u'present', u'Match': u'^(\\s*)ModulePath\\s.*$'})
changed: [welktxef-d931887-021] => (item={u'To': u'', u'State': u'absent', u'Match': u'^\\s*Import\\s.*$'})
changed: [welktxef-d931887-021] => (item={u'To': u'', u'State': u'absent', u'Match': u'^\\s*LogTraces\\s.*$'})
changed: [welktxef-d931887-021] => (item={u'To': u'', u'State': u'absent', u'Match': u'^\\s*Encoding\\s.*$'})

TASK [Remove global puppet hieradata entries for collectd] *********************
changed: [welktxef-d931887-021] => (item=module_path)
changed: [welktxef-d931887-021] => (item=plugins)
changed: [welktxef-d931887-021] => (item=log_traces)
changed: [welktxef-d931887-021] => (item=encoding)

TASK [Populate services list] **************************************************
ok: [welktxef-d931887-021]

TASK [Stop and disable influxdb service] ***************************************
changed: [welktxef-d931887-021] => (item=influxdb.service)

TASK [Disable collectd interface to influxdb] **********************************
changed: [welktxef-d931887-021]

TASK [Reset service failed status] *********************************************
changed: [welktxef-d931887-021]
 [WARNING]: flush_handlers task does not support when conditional


RUNNING HANDLER [restart collectd] *********************************************
changed: [welktxef-d931887-021]

TASK [Catalog influxdb data files] *********************************************
ok: [welktxef-d931887-021]

TASK [Delete existing influxdb data files to reclaim disk space] ***************
changed: [welktxef-d931887-021] => (item=/var/lib/influxdb/data/collectd/collectd samples/15)
changed: [welktxef-d931887-021] => (item=/var/lib/influxdb/data/collectd/collectd samples/9)
changed: [welktxef-d931887-021] => (item=/var/lib/influxdb/data/collectd/collectd samples/13)
changed: [welktxef-d931887-021] => (item=/var/lib/influxdb/data/collectd/collectd samples/19)
changed: [welktxef-d931887-021] => (item=/var/lib/influxdb/data/collectd/collectd samples/11)
changed: [welktxef-d931887-021] => (item=/var/lib/influxdb/data/collectd/collectd samples/17)
changed: [welktxef-d931887-021] => (item=/var/lib/influxdb/data/collectd/collectd samples/21)
changed: [welktxef-d931887-021] => (item=/var/lib/influxdb/data/collectd/collectd samples/7)
changed: [welktxef-d931887-021] => (item=/var/lib/influxdb/data/_internal/monitor/20)
changed: [welktxef-d931887-021] => (item=/var/lib/influxdb/data/_internal/monitor/14)
changed: [welktxef-d931887-021] => (item=/var/lib/influxdb/data/_internal/monitor/10)
changed: [welktxef-d931887-021] => (item=/var/lib/influxdb/data/_internal/monitor/12)
changed: [welktxef-d931887-021] => (item=/var/lib/influxdb/data/_internal/monitor/16)
changed: [welktxef-d931887-021] => (item=/var/lib/influxdb/data/_internal/monitor/22)
changed: [welktxef-d931887-021] => (item=/var/lib/influxdb/data/_internal/monitor/18)
changed: [welktxef-d931887-021] => (item=/var/lib/influxdb/data/_internal/monitor/8)

TASK [Wait 5 seconds] **********************************************************
Pausing for 5 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [welktxef-d931887-021]

TASK [Verify influxdb process is no longer present] ****************************
changed: [welktxef-d931887-021]

TASK [Verify influxdb is no longer present] ************************************
changed: [welktxef-d931887-021]

PLAY RECAP *********************************************************************
welktxef-d931887-021       : ok=17   changed=13   unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.05-disable_influxdb(keystone_admin)]$

on the subcloud
[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$ systemctl status influxdb.service
● influxdb.service - InfluxDB open-source, distributed, time series database
   Loaded: loaded (/etc/systemd/system/influxdb.service; disabled; vendor preset: disabled)
   Active: inactive (dead)
     Docs: https://influxdb.com/docs/
[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.05-resize_docker(keystone_admin)]$

```

### Completed influxDB shutdown on both controller and subcloud, moving on to next step

### Verify WRA DB size and Retention time has
### skipping, as WRA has no impact with BMC .43

### WRA removed from controller 

### Ensure necessary docker images are availible in private registry

```log
[XXXXXX@controller-0 wrcp-21.05-disable_influxdb(keystone_admin)]$ system service-parameter-list --service=docker

+--------------------------------------+---------+------------------+-------------+-------------------------------------------------------------------------------------------------------------------------------+-------------+----------+
| uuid                                 | service | section          | name        | value                                                                                                                         | personality | resource |
+--------------------------------------+---------+------------------+-------------+-------------------------------------------------------------------------------------------------------------------------------+-------------+----------+
| 27367aa4-f50d-4916-b9ba-83b7ecbfd1e9 | docker  | docker-registry  | auth-secret | 38fd52f3-1713-4315-b325-d7b80cca31df                                                                                          | None        | None     |
| 6046599a-d1d1-4d3a-bef2-203e31ad6603 | docker  | docker-registry  | type        | docker                                                                                                                        | None        | None     |
| 49f7ad5a-14dc-41cd-9214-16f8b9c37753 | docker  | docker-registry  | url         | wsregistry.mtce.vzwops.com:443/vcp_far_edge_in_building_docker/625619392498.dkr.ecr.us-west-2.amazonaws.com/docker.io         | None        | None     |
| 9c78be7a-3821-4371-b68b-4d504e5ade5c | docker  | elastic-registry | auth-secret | 3e7a149d-e372-45d0-9fd0-48e57a6e674e                                                                                          | None        | None     |
| 571ad8a2-d7bf-435d-94aa-3843cf0a4f6c | docker  | elastic-registry | type        | docker                                                                                                                        | None        | None     |
| 2fa8049f-bdc3-46b6-a0bd-e29fa1248999 | docker  | elastic-registry | url         | wsregistry.mtce.vzwops.com:443/vcp_far_edge_in_building_docker/625619392498.dkr.ecr.us-west-2.amazonaws.com/docker.elastic.co | None        | None     |
| c17a88d0-21af-473b-8148-6596e567990a | docker  | gcr-registry     | auth-secret | ff956761-4a5e-4dbe-bb69-f508437f7ad8                                                                                          | None        | None     |
| 61d1b77b-9c8a-4b2a-894b-13bf4ba6130e | docker  | gcr-registry     | type        | docker                                                                                                                        | None        | None     |
| b9193de3-5596-4dc9-91fc-b0111071d6dd | docker  | gcr-registry     | url         | wsregistry.mtce.vzwops.com:443/vcp_far_edge_in_building_docker/625619392498.dkr.ecr.us-west-2.amazonaws.com/gcr.io            | None        | None     |
| dd76fc7d-89b3-4c77-90c2-ed233f4ab1f7 | docker  | k8s-registry     | auth-secret | efbd3a5f-64f2-407b-914b-29a003e6518d                                                                                          | None        | None     |
| 74a9f81a-b3aa-4ac0-b655-c3d540048435 | docker  | k8s-registry     | type        | docker                                                                                                                        | None        | None     |
| 0a96c740-39a9-40e1-97ab-6e9b4a6fc3dd | docker  | k8s-registry     | url         | wsregistry.mtce.vzwops.com:443/vcp_far_edge_in_building_docker/625619392498.dkr.ecr.us-west-2.amazonaws.com/k8s.gcr.io        | None        | None     |
| b30a7ec4-bc48-4562-b6dd-6645b2a399a0 | docker  | quay-registry    | auth-secret | c044c017-5a3b-45dc-a59e-3764eb693455                                                                                          | None        | None     |
| 72459c95-fcc6-47ea-b1cd-ead2678ecc00 | docker  | quay-registry    | type        | docker                                                                                                                        | None        | None     |
| 3e478bea-bc16-4637-a108-32ec770d2d88 | docker  | quay-registry    | url         | wsregistry.mtce.vzwops.com:443/vcp_far_edge_in_building_docker/625619392498.dkr.ecr.us-west-2.amazonaws.com/quay.io           | None        | None     |
+--------------------------------------+---------+------------------+-------------+-------------------------------------------------------------------------------------------------------------------------------+-------------+----------+
[XXXXXX@controller-0 wrcp-21.05-disable_influxdb(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.05-disable_influxdb(keystone_admin)]$

```

### Registry configured on system controller


### ensure System controllers registry is trusted by subclouds

### checking the subcloud:

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ . /etc/platform/openrc
[XXXXXX@controller-0 ~(keystone_admin)]$ sudo docker login registry.central:9001 -u XXXXXX -p
Password:
XXXXXX needs an argument: 'p' in -p
See 'docker login --help'.
[XXXXXX@controller-0 ~(keystone_admin)]$ sudo docker login registry.central:9001 -u XXXXXX -p XXXXXX
WARNING! Using --password via the CLI is insecure. Use --password-stdin.
Error response from daemon: Get https://registry.central:9001/v2/: unauthorized: authentication required
[XXXXXX@controller-0 ~(keystone_admin)]$ sudo docker login registry.central:9001 -u XXXXXX -p XXXXXX
[XXXXXX@controller-0 ~(keystone_admin)]$ . /etc/platform/openrc
[XXXXXX@controller-0 ~(keystone_admin)]$ sudo docker login registry.central:9001 -u XXXXXX -p XXXXXX
WARNING! Using --password via the CLI is insecure. Use --password-stdin.
WARNING! Your password will be stored unencrypted in /root/.docker/config.json.
Configure a credential helper to remove this warning. See
https://docs.docker.com/engine/reference/commandline/login/#credentials-store

Login Succeeded
[XXXXXX@controller-0 ~(keystone_admin)]$

```

### Subcloud trust with controller registry is good

### Verify ZT BMC is operational (proteus)

```log
[XXXXXX@vcpe-jumpserver ~]$ curl -ks -u XXXXXX:XXXXXX https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Systems/Self | jq '.HostName'
"welktxef-931887-rz-le2pts6-021"
[XXXXXX@vcpe-jumpserver ~]$ curl -ks -u XXXXXX:XXXXXX https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Systems/Self | jq '.BiosVersion'

"0.23"
[XXXXXX@vcpe-jumpserver ~]$

```

### we are good on BMC

### enabling M state on proteus (will see if this works with .43)

To enable the m wait state on proteus we use the following command:

```sh
curl -k -w "\\n%{http_code} %{url_effective}\\n" \
-u ${auth} \
-H "Content-Type: application/json" \
-d '{"Attributes": {"PMS012": "Enable"}}' \
-X PATCH https://[${IP}]/redfish/v1/Systems/Self/Bios/SD
```

```log
[XXXXXX@vcpe-jumpserver ~]$ curl -k -w "\\n%{http_code} %{url_effective}\\n" -u ${auth} -H "Content-Type: application/json" -d '{"Attributes": {"PMS012": "Enable"}}' -X PATCH https://[${IP}]/redfish/v1/Systems/Self/Bios/SD
{"error":{"@Message.ExtendedInfo":[{"@odata.type":"#Message.v1_0_8.Message","Message":"The requested operation is temporarily unavailable since Host System Reboot might be in progress or Host might be in Bios Setup or Redfish Inventory processing might be in progress. Please try after sometime.","MessageId":"Ami.1.0.ServiceTemporarilyUnavailableDueToHostBooting","Resolution":"Retry after some time.","Severity":"Critical"}],"code":"Ami.1.0.ServiceTemporarilyUnavailableDueToHostBooting","message":"The requested operation is temporarily unavailable since Host System Reboot might be in progress or Host might be in Bios Setup or Redfish Inventory processing might be in progress. Please try after sometime."}}
503 https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Systems/Self/Bios/SD
[XXXXXX@vcpe-jumpserver ~]$
[XXXXXX@vcpe-jumpserver ~]$ curl -k -w "\\n%{http_code} %{url_effective}\\n" -u XXXXXX:XXXXXX -H "Content-Type: application/json" -d '{"Attributes": {"PMS012": "Enable"}}' -X PATCH https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Systems/Self/Bios/SD
{"error":{"@Message.ExtendedInfo":[{"@odata.type":"#Message.v1_0_8.Message","Message":"The requested operation is temporarily unavailable since Host System Reboot might be in progress or Host might be in Bios Setup or Redfish Inventory processing might be in progress. Please try after sometime.","MessageId":"Ami.1.0.ServiceTemporarilyUnavailableDueToHostBooting","Resolution":"Retry after some time.","Severity":"Critical"}],"code":"Ami.1.0.ServiceTemporarilyUnavailableDueToHostBooting","message":"The requested operation is temporarily unavailable since Host System Reboot might be in progress or Host might be in Bios Setup or Redfish Inventory processing might be in progress. Please try after sometime."}}
503 https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Systems/Self/Bios/SD
[XXXXXX@vcpe-jumpserver ~]$
```

### we should not get this while the os is in a booted state
### resetting the BMC to see if this addresses the issue

```log
[XXXXXX@vcpe-jumpserver ~]$ ipmitool -I lanplus -H 2607:f160:10:9249:ce:40a:0:e015  -U XXXXXX -P XXXXXX mc reset cold
Sent cold reset command to MC
[XXXXXX@vcpe-jumpserver ~]$
```

### trying again to set state

```log 
[XXXXXX@vcpe-jumpserver ~]$ curl -k -w "\\n%{http_code} %{url_effective}\\n" -u XXXXXX:XXXXXX -H "Content-Type: application/json" -d '{"Attributes": {"PMS012": "Enable"}}' -X PATCH https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Systems/Self/Bios/SD
{"error":{"@Message.ExtendedInfo":[{"@odata.type":"#Message.v1_0_8.Message","Message":"The requested operation is temporarily unavailable since Host System Reboot might be in progress or Host might be in Bios Setup or Redfish Inventory processing might be in progress. Please try after sometime.","MessageId":"Ami.1.0.ServiceTemporarilyUnavailableDueToHostBooting","Resolution":"Retry after some time.","Severity":"Critical"}],"code":"Ami.1.0.ServiceTemporarilyUnavailableDueToHostBooting","message":"The requested operation is temporarily unavailable since Host System Reboot might be in progress or Host might be in Bios Setup or Redfish Inventory processing might be in progress. Please try after sometime."}}
503 https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Systems/Self/Bios/SD
[XXXXXX@vcpe-jumpserver ~]$

```

### Same issue, going to reboot the host to see if it clears.

```log

curl -u XXXXXX:XXXXXX -ks https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Systems/Self/Bios | jq '.Attributes.PMS012'
"Disable"


```

### problem does not resolve, we cannot set MWAIT via redfish 
### ZT has problem and working


### continuing with upgrades
### System Pre-Checks and Scripts to Evaluate Hosts for Upgrade

```log
controller
[XXXXXX@controller-0 ~(keystone_admin)]$ sw-patch query
      Patch ID         RR  Release  Patch State
=====================  ==  =======  ===========
WRCP_21.05_PATCH_0001  N    21.05    Committed
WRCP_21.05_PATCH_0002  Y    21.05    Committed
WRCP_21.05_PATCH_0003  N    21.05    Committed
WRCP_21.05_PATCH_0004  N    21.05    Committed
WRCP_21.05_PATCH_0005  N    21.05     Applied
WRCP_21.05_PATCH_0006  N    21.05     Applied

[XXXXXX@controller-0 ~(keystone_admin)]$

subcloud 

[XXXXXX@controller-0 ~(keystone_admin)]$ sw-patch query
      Patch ID         RR  Release  Patch State
=====================  ==  =======  ===========
WRCP_21.05_PATCH_0001  N    21.05    Committed
WRCP_21.05_PATCH_0002  Y    21.05    Committed
WRCP_21.05_PATCH_0003  N    21.05    Committed
WRCP_21.05_PATCH_0004  N    21.05    Committed
WRCP_21.05_PATCH_0005  N    21.05     Applied
WRCP_21.05_PATCH_0006  N    21.05     Applied

[XXXXXX@controller-0 ~(keystone_admin)]$

controller


controller-0:~# show-certs.sh | grep Residual
	 Residual Time	:  388d
	 Residual Time	:  351d
	 Residual Time	:  200d
	 Residual Time	:  2601d
	 Residual Time	:  4297d
	 Residual Time	:  2602d
	 Residual Time	:  1811d
	 Residual Time	:  166d
	 Residual Time	:  2602d
	 Residual Time	:  3636d
	 Residual Time	:  3636d
	 Residual Time	:  3636d
	 Residual Time	:  354d
	 Residual Time	:  4297d
controller-0:~#

subcloud

controller-0:~# show-certs.sh | grep Residual
	 Residual Time	:  389d
	 Residual Time	:  353d
	 Residual Time	:  200d
	 Residual Time	:  2601d
	 Residual Time	:  4297d
	 Residual Time	:  2602d
	 Residual Time	:  1811d
	 Residual Time	:  353d
	 Residual Time	:  169d
	 Residual Time	:  2602d
	 Residual Time	:  3638d
	 Residual Time	:  3638d
	 Residual Time	:  3638d
	 Residual Time	:  355d
	 Residual Time	:  4297d
controller-0:~#

controller

[XXXXXX@controller-0 ~(keystone_admin)]$ system application-list
+--------------------------+----------+-----------------------------------+------------------------------------+----------+-----------+
| application              | version  | manifest name                     | manifest file                      | status   | progress  |
+--------------------------+----------+-----------------------------------+------------------------------------+----------+-----------+
| cert-manager             | 21.05-17 | cert-manager-manifest             | certmanager-manifest.yaml          | applied  | completed |
| nginx-ingress-controller | 21.05-16 | nginx-ingress-controller-manifest | nginx_ingress_controller_manifest. | applied  | completed |
|                          |          |                                   | yaml                               |          |           |
|                          |          |                                   |                                    |          |           |
| oidc-auth-apps           | 21.05-44 | oidc-auth-manifest                | manifest.yaml                      | applied  | completed |
| platform-integ-apps      | 21.05-30 | platform-integration-manifest     | manifest.yaml                      | uploaded | completed |
| rook-ceph-apps           | 1.0-5    | rook-ceph-manifest                | manifest.yaml                      | uploaded | completed |
+--------------------------+----------+-----------------------------------+------------------------------------+----------+-----------+
[XXXXXX@controller-0 ~(keystone_admin)]$

subcloud

[XXXXXX@controller-0 ~(keystone_admin)]$ system application-list
+--------------------------+----------+-----------------------------------+------------------------------------+----------+-----------+
| application              | version  | manifest name                     | manifest file                      | status   | progress  |
+--------------------------+----------+-----------------------------------+------------------------------------+----------+-----------+
| cert-manager             | 21.05-17 | cert-manager-manifest             | certmanager-manifest.yaml          | applied  | completed |
| nginx-ingress-controller | 21.05-16 | nginx-ingress-controller-manifest | nginx_ingress_controller_manifest. | applied  | completed |
|                          |          |                                   | yaml                               |          |           |
|                          |          |                                   |                                    |          |           |
| oidc-auth-apps           | 21.05-44 | oidc-auth-manifest                | manifest.yaml                      | applied  | completed |
| platform-integ-apps      | 21.05-30 | platform-integration-manifest     | manifest.yaml                      | applied  | completed |
| rook-ceph-apps           | 1.0-5    | rook-ceph-manifest                | manifest.yaml                      | uploaded | completed |
+--------------------------+----------+-----------------------------------+------------------------------------+----------+-----------+
[XXXXXX@controller-0 ~(keystone_admin)]$


controller

[XXXXXX@controller-0 ~(keystone_admin)]$ df -k /
Filesystem     1K-blocks    Used Available Use% Mounted on
/dev/sda4       20027216 8332620  10654212  44% /
[XXXXXX@controller-0 ~(keystone_admin)]$

subcloud

[XXXXXX@controller-0 ~(keystone_admin)]$ df -k /
Filesystem     1K-blocks    Used Available Use% Mounted on
/dev/nvme0n1p4  20027216 8490380  10496452  45% /
[XXXXXX@controller-0 ~(keystone_admin)]$

controller

[XXXXXX@controller-0 ~(keystone_admin)]$ df -k /scratch/
Filesystem                       1K-blocks  Used Available Use% Mounted on
/dev/mapper/cgts--vg-scratch--lv  16382844 49204  15478396   1% /scratch
[XXXXXX@controller-0 ~(keystone_admin)]$

subcloud
[XXXXXX@controller-0 ~(keystone_admin)]$ df -k /scratch/
Filesystem                       1K-blocks  Used Available Use% Mounted on
/dev/mapper/cgts--vg-scratch--lv  16382844 49156  15478444   1% /scratch
[XXXXXX@controller-0 ~(keystone_admin)]$

controller
[XXXXXX@controller-0 ~(keystone_admin)]$ df -k /opt/platform-backup/
Filesystem     1K-blocks     Used Available Use% Mounted on
/dev/sda1       30106488 14523400  14030704  51% /opt/platform-backup
[XXXXXX@controller-0 ~(keystone_admin)]$

subcloud

[XXXXXX@controller-0 ~(keystone_admin)]$ df -k /opt/platform-backup/
Filesystem     1K-blocks     Used Available Use% Mounted on
/dev/nvme0n1p1  30106488 10665004  17889100  38% /opt/platform-backup
[XXXXXX@controller-0 ~(keystone_admin)]$

controller
[XXXXXX@controller-0 ~(keystone_admin)]$ df -k /opt/dc-vault
Filesystem     1K-blocks    Used Available Use% Mounted on
/dev/drbd6      15350212 2386984  12160440  17% /opt/dc-vault
[XXXXXX@controller-0 ~(keystone_admin)]$

subcloud

[XXXXXX@controller-0 ~(keystone_admin)]$ df -k /opt/dc-vault
df: ‘/opt/dc-vault’: No such file or directory
[XXXXXX@controller-0 ~(keystone_admin)]$


controller

controller-0:~# tridentctl -n trident version
+----------------+----------------+
| SERVER VERSION | CLIENT VERSION |
+----------------+----------------+
| 20.04.0        | 20.04.0        |
+----------------+----------------+
controller-0:~#

subcloud

controller-0:~# tridentctl -n trident version
Error: could not find a Trident pod in the trident namespace. You may need to use the -n option to specify the correct namespace
controller-0:~#



controller
[XXXXXX@controller-0 ~(keystone_admin)]$ fm alarm-list

[XXXXXX@controller-0 ~(keystone_admin)]$

subcloud

[XXXXXX@controller-0 ~(keystone_admin)]$ fm alarm-list

[XXXXXX@controller-0 ~(keystone_admin)]$


controller 
[XXXXXX@controller-0 ~(keystone_admin)]$ ip -o a | awk '{print $2,"\t",$4}' | grep pxeboot
pxeboot0 	 169.254.202.2/24
pxeboot0 	 169.254.202.1/24
pxeboot0 	 fe80::4adf:37ff:febb:1c84/64
[XXXXXX@controller-0 ~(keystone_admin)]$

subcloud 
[XXXXXX@controller-0 ~(keystone_admin)]$ ip -o a | awk '{print $2,"\t",$4}' | grep pxeboot
[XXXXXX@controller-0 ~(keystone_admin)]$

controller
[XXXXXX@controller-0 ~(keystone_admin)]$ sudo ethtool -m ens1f0|grep output
Password:
XXXXXX, try again.
Password:
	XXXXXX output power                        : 0.7830 mW / -1.06 dBm
	Laser output power high alarm             : Off
	Laser output power low alarm              : Off
	Laser output power high warning           : Off
	Laser output power low warning            : Off
	Laser output power high alarm threshold   : 2.5119 mW / 4.00 dBm
	Laser output power low alarm threshold    : 0.3981 mW / -4.00 dBm
	Laser output power high warning threshold : 2.2387 mW / 3.50 dBm
	Laser output power low warning threshold  : 0.5012 mW / -3.00 dBm
[XXXXXX@controller-0 ~(keystone_admin)]$

subcloud

[XXXXXX@controller-0 ~(keystone_admin)]$ sudo ethtool -m ens1f0|grep output
Password:
XXXXXX, try again.
Password:
	XXXXXX output power                        : 0.5918 mW / -2.28 dBm
	Laser output power high alarm             : Off
	Laser output power low alarm              : Off
	Laser output power high warning           : Off
	Laser output power low warning            : Off
	Laser output power high alarm threshold   : 1.0000 mW / 0.00 dBm
	Laser output power low alarm threshold    : 0.1585 mW / -8.00 dBm
	Laser output power high warning threshold : 0.7943 mW / -1.00 dBm
	Laser output power low warning threshold  : 0.1995 mW / -7.00 dBm
[XXXXXX@controller-0 ~(keystone_admin)]$


```


### prechecks are good, we can proceed.

### Upgrade 1 - System Controller - WRCP
### Follow MOP 1 Section 3 'Pre-deployment' of the v1.14 MOP bundle, with the following additions:

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ source /etc/platform/openrc
[XXXXXX@controller-0 ~(keystone_admin)]$ [ "$(hostname)" == "controller-1" ] && system host-swact controller-1 && exit
[XXXXXX@controller-0 ~(keystone_admin)]$ XXXXXX_password=XXXXXX
[XXXXXX@controller-0 ~(keystone_admin)]$ admin_password=XXXXXX
[XXXXXX@controller-0 ~(keystone_admin)]$ ansible-playbook /usr/share/ansible/stx-ansible/playbooks/backup.yml \
> -e "XXXXXX" \
> -e "XXXXXX"



```
I could not get the system to backup up the controller, moving on as steps were not working.





### STOP after executing step 10. 
### Copy cleanup-unexpected-images_v1.1.zip into /opt/platform-backup/upgrade/wrcp-21.12-upgrade directory.
### Unzip cleanup-unexpected-images_v1.1.zip

```log

[XXXXXX@controller-0 upgrade(keystone_admin)]$ cd /opt/platform-backup/upgrade/wrcp-21.12-upgrade
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ system oam-show
+-----------------+--------------------------------------+
| Property        | Value                                |
+-----------------+--------------------------------------+
| created_at      | 2023-08-26T04:44:49.344247+00:00     |
| isystem_uuid    | 85d98699-635d-490f-ae18-ba3302ed8605 |
| oam_c0_ip       | 2607:f160:0:3043:cd:290:0:11         |
| oam_c1_ip       | 2607:f160:0:3043:cd:290:0:12         |
| oam_floating_ip | 2607:f160:0:3043:cd:290:0:10         |
| oam_gateway_ip  | 2607:f160:0:3043:cd:28::             |
| oam_subnet      | 2607:f160:0:3043::/64                |
| updated_at      | None                                 |
| uuid            | d94befa0-1fc3-4644-8570-cd08a4ec9a10 |
+-----------------+--------------------------------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ cp ~/cleanup-unexpected-images_v1.1.zip .
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ unzip cleanup-unexpected-images_v1.1.zip
Archive:  cleanup-unexpected-images_v1.1.zip
replace cleanup-unexpected-images.yaml? [y]es, [n]o, [A]ll, [N]one, [r]ename: y
  inflating: cleanup-unexpected-images.yaml
replace remove-images.yaml? [y]es, [n]o, [A]ll, [N]one, [r]ename: y
  inflating: remove-images.yaml
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$




```

### Continuing step 11 of deployment in mop 1


```log

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ sudo show-certs.sh | grep -E '^\s+Residual Time'
Password:
	 XXXXXX Time	:  385d
	 Residual Time	:  348d
	 Residual Time	:  197d
	 Residual Time	:  2597d
	 Residual Time	:  4294d
	 Residual Time	:  2599d
	 Residual Time	:  1808d
	 Residual Time	:  163d
	 Residual Time	:  2599d
	 Residual Time	:  3633d
	 Residual Time	:  3633d
	 Residual Time	:  3633d
	 Residual Time	:  351d
	 Residual Time	:  4294d
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ for s in $(echo dcmanager sw-manager); do
> for t in $(echo upgrade patch fw-update kube-upgrade); do
> $s $t-strategy delete
> done
> done
Not found
ERROR (app) Unable to delete sw update strategy
Not found
ERROR (app) Unable to delete sw update strategy
Not found
ERROR (app) Unable to delete sw update strategy
Not found
ERROR (app) Unable to delete sw update strategy
Strategy delete failed
Strategy delete failed
Strategy delete failed
Strategy delete failed
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ sw-patch query | grep WRCP_21.05_PATCH_0005
WRCP_21.05_PATCH_0005  N    21.05     Applied
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ bmc_username=OSPctl
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ bmc_password=XXXXXX
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ system host-list --column hostname --format value > inventory
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./validate-pxe-boot-order_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook --inventory inventory validate-pxe-boot-order.yaml \
> --extra-vars "bmc_username=${bmc_username} bmc_password=${bmc_password}" \
> --ask-become-pass --ask-pass --user XXXXXX 0</dev/null
SSH password:
XXXXXX password[defaults to SSH password]:

PLAY [all] *********************************************************************

TASK [Gathering Facts] *********************************************************
ok: [controller-0]
ok: [controller-1]
ok: [worker-0]

TASK [Validate bmc_username] ***************************************************
skipping: [controller-0]

TASK [Validate bmc_password] ***************************************************
skipping: [controller-0]

TASK [Retrieve pxeboot interface assignment] ***********************************
changed: [controller-1 -> localhost]
changed: [worker-0 -> localhost]
changed: [controller-0 -> localhost]

TASK [Retrieve BMC address] ****************************************************
changed: [controller-0 -> localhost]
changed: [controller-1 -> localhost]
changed: [worker-0 -> localhost]

TASK [Retrieve pxeboot interface pci address] **********************************
ok: [controller-0] => (item=u'ens2f0')
skipping: [controller-0] => (item=u'ens2f1')
skipping: [controller-1] => (item=u'ens2f1')
ok: [controller-1] => (item=u'ens2f0')
ok: [worker-0] => (item=u'ens2f0')
skipping: [worker-0] => (item=u'ens2f1')

TASK [Ensure pxeboot interface pci address is available] ***********************
skipping: [controller-0]
skipping: [controller-1]
skipping: [worker-0]

TASK [Retrieve pxeboot interface slot and port information] ********************
changed: [controller-0]
changed: [controller-1]
changed: [worker-0]

TASK [Ensure pxeboot interface slot is available] ******************************
skipping: [controller-0]
skipping: [controller-1]
skipping: [worker-0]

TASK [Build pxeboot boot device name] ******************************************
ok: [controller-0]
ok: [controller-1]
ok: [worker-0]

TASK [Retrieve boot order list] ************************************************
ok: [controller-0]
ok: [worker-0]
ok: [controller-1]

TASK [Extract first nic from boot order list] **********************************
skipping: [controller-0] => (item=Unknown.Unknown.200.3)
skipping: [controller-0] => (item=Unknown.Unknown.200.2)
ok: [controller-0] => (item=NIC.Slot.2.1.IPv4)
skipping: [controller-0] => (item=Unknown.Unknown.200.1)
skipping: [controller-0] => (item=Generic.USB.1.1)
skipping: [controller-0] => (item=HD.EmbRAID.1.2)
skipping: [controller-0] => (item=NIC.Slot.1.1.IPv6)
skipping: [controller-0] => (item=NIC.Slot.1.1.Httpv4)
skipping: [controller-0] => (item=NIC.Slot.1.1.IPv4)
skipping: [controller-0] => (item=NIC.Slot.2.1.Httpv4)
skipping: [controller-0] => (item=NIC.Slot.3.1.Httpv4)
skipping: [controller-0] => (item=NIC.Slot.3.1.IPv4)
skipping: [controller-0] => (item=NIC.Slot.2.1.Httpv6)
skipping: [controller-0] => (item=NIC.Slot.2.1.IPv6)
skipping: [controller-1] => (item=HD.EmbRAID.1.3)
skipping: [controller-0] => (item=NIC.Slot.3.1.Httpv6)
skipping: [controller-1] => (item=Unknown.Unknown.200.4)
skipping: [controller-0] => (item=NIC.Slot.3.1.IPv6)
skipping: [controller-1] => (item=Unknown.Unknown.200.3)
skipping: [controller-0] => (item=HD.SD.1.2)
skipping: [controller-0] => (item=NIC.LOM.1.1.Httpv4)
skipping: [controller-0] => (item=NIC.LOM.1.1.IPv4)
skipping: [controller-0] => (item=NIC.FlexLOM.1.1.Httpv4)
skipping: [controller-0] => (item=NIC.FlexLOM.1.1.IPv4)
skipping: [controller-0] => (item=NIC.FlexLOM.1.1.Httpv6)
ok: [controller-1] => (item=NIC.Slot.2.1.IPv4)
skipping: [controller-0] => (item=NIC.FlexLOM.1.1.IPv6)
skipping: [controller-1] => (item=Generic.USB.1.1)
skipping: [controller-0] => (item=NIC.LOM.1.1.Httpv6)
skipping: [controller-1] => (item=HD.EmbRAID.1.2)
skipping: [controller-0] => (item=NIC.LOM.1.1.IPv6)
skipping: [controller-1] => (item=HD.SD.1.2)
skipping: [controller-0] => (item=NIC.Slot.1.1.Httpv6)
skipping: [controller-1] => (item=NIC.LOM.1.1.Httpv4)
skipping: [controller-0] => (item=CD.Virtual.3.1)
skipping: [controller-1] => (item=NIC.LOM.1.1.IPv4)
skipping: [controller-1] => (item=NIC.FlexLOM.1.1.Httpv4)
skipping: [controller-1] => (item=NIC.FlexLOM.1.1.IPv4)
skipping: [controller-1] => (item=NIC.FlexLOM.1.1.Httpv6)
skipping: [controller-1] => (item=NIC.FlexLOM.1.1.IPv6)
skipping: [controller-1] => (item=NIC.LOM.1.1.Httpv6)
skipping: [controller-1] => (item=NIC.LOM.1.1.IPv6)
skipping: [controller-1] => (item=NIC.Slot.1.1.Httpv6)
skipping: [worker-0] => (item=HD.EmbRAID.1.3)
skipping: [controller-1] => (item=NIC.Slot.1.1.IPv6)
skipping: [worker-0] => (item=Unknown.Unknown.200.3)
skipping: [controller-1] => (item=NIC.Slot.1.1.Httpv4)
skipping: [worker-0] => (item=Unknown.Unknown.200.2)
skipping: [controller-1] => (item=NIC.Slot.1.1.IPv4)
skipping: [controller-1] => (item=NIC.Slot.2.1.Httpv4)
skipping: [controller-1] => (item=NIC.Slot.3.1.Httpv4)
skipping: [controller-1] => (item=NIC.Slot.3.1.IPv4)
skipping: [controller-1] => (item=NIC.Slot.2.1.Httpv6)
skipping: [controller-1] => (item=NIC.Slot.2.1.IPv6)
ok: [worker-0] => (item=NIC.Slot.2.1.IPv4)
skipping: [controller-1] => (item=NIC.Slot.3.1.Httpv6)
skipping: [worker-0] => (item=Generic.USB.1.1)
skipping: [controller-1] => (item=NIC.Slot.3.1.IPv6)
skipping: [worker-0] => (item=HD.EmbRAID.1.2)
skipping: [worker-0] => (item=HD.SD.1.2)
skipping: [worker-0] => (item=NIC.LOM.1.1.Httpv4)
skipping: [worker-0] => (item=NIC.LOM.1.1.IPv4)
skipping: [worker-0] => (item=NIC.FlexLOM.1.1.Httpv4)
skipping: [worker-0] => (item=NIC.FlexLOM.1.1.IPv4)
skipping: [worker-0] => (item=NIC.FlexLOM.1.1.Httpv6)
skipping: [worker-0] => (item=NIC.FlexLOM.1.1.IPv6)
skipping: [worker-0] => (item=NIC.LOM.1.1.Httpv6)
skipping: [worker-0] => (item=NIC.LOM.1.1.IPv6)
skipping: [worker-0] => (item=NIC.Slot.1.1.Httpv6)
skipping: [worker-0] => (item=NIC.Slot.1.1.IPv6)
skipping: [worker-0] => (item=NIC.Slot.1.1.IPv4)
skipping: [worker-0] => (item=NIC.Slot.1.1.Httpv4)
skipping: [worker-0] => (item=NIC.Slot.2.1.Httpv4)
skipping: [worker-0] => (item=NIC.Slot.3.1.Httpv4)
skipping: [worker-0] => (item=NIC.Slot.3.1.IPv4)
skipping: [worker-0] => (item=NIC.Slot.2.1.Httpv6)
skipping: [worker-0] => (item=NIC.Slot.2.1.IPv6)
skipping: [worker-0] => (item=NIC.Slot.3.1.Httpv6)
skipping: [worker-0] => (item=NIC.Slot.3.1.IPv6)

TASK [Check first nic in boot order list matches pxeboot interface] ************
skipping: [controller-0]
skipping: [controller-1]
skipping: [worker-0]

PLAY RECAP *********************************************************************
controller-0               : ok=8    changed=3    unreachable=0    failed=0
controller-1               : ok=8    changed=3    unreachable=0    failed=0
worker-0                   : ok=8    changed=3    unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ rm -f inventory
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ system host-fs-show controller-0 scratch | grep "size" | awk '{ print $4 }'
16
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ df -h /scratch
Filesystem                        Size  Used Avail Use% Mounted on
/dev/mapper/cgts--vg-scratch--lv   16G   49M   15G   1% /scratch
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ system host-fs-modify controller-0 scratch=32
+--------------------------------------+---------+-------------+----------------+
| UUID                                 | FS Name | Size in GiB | Logical Volume |
+--------------------------------------+---------+-------------+----------------+
| fb639f09-57c1-4ee7-bfa9-381e6e0a6c6b | backup  | 55          | backup-lv      |
| 8abfb873-7712-4cb7-9cc3-0f7a12855616 | docker  | 250         | docker-lv      |
| 7ef01b61-0365-4152-a7b2-e3d90e08247e | kubelet | 10          | kubelet-lv     |
| 98aaa036-c021-4a15-9e9c-ed03d9995a1e | scratch | 32          | scratch-lv     |
+--------------------------------------+---------+-------------+----------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ system host-fs-show controller-0 scratch | grep "size" | awk '{ print $4 }'
32
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ system host-fs-show controller-1 scratch | grep "size" | awk '{ print $4 }'
16
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ system host-fs-modify controller-1 scratch=32
+--------------------------------------+---------+-------------+----------------+
| UUID                                 | FS Name | Size in GiB | Logical Volume |
+--------------------------------------+---------+-------------+----------------+
| bbb16755-489b-42cb-82e1-b697be10c074 | backup  | 55          | backup-lv      |
| 326a8272-e385-4981-b52a-ba88e95e55d5 | docker  | 250         | docker-lv      |
| 835dff4e-e586-4e5d-bc89-80d01f148695 | kubelet | 10          | kubelet-lv     |
| 2c154a73-2bef-4c32-9ddb-422e809eeea1 | scratch | 32          | scratch-lv     |
+--------------------------------------+---------+-------------+----------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ system host-fs-show controller-1 scratch | grep "size" | awk '{ print $4 }'
32
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ echo -e '[system-controller]\nlocalhost' > controller
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./sanity_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook --inventory controller --extra-vars "scenario=before" \
> --ask-pass --ask-become-pass --user XXXXXX \
> pre-deployment-system-controller.yaml 0</dev/null
SSH password:
XXXXXX password[defaults to SSH password]:

PLAY [all] *********************************************************************

TASK [Gathering Facts] *********************************************************
ok: [localhost]

TASK [Read in parameter file] **************************************************
ok: [localhost]

TASK [set expected Fortville firmware version] *********************************
ok: [localhost]

TASK [set expected N3000 firmware version] *************************************
ok: [localhost]

TASK [create directory /home/XXXXXX/sanity] **********************************
ok: [localhost -> localhost]

TASK [delete existing file /home/XXXXXX/sanity/output_list] ******************
changed: [localhost -> localhost]

TASK [create file /home/XXXXXX/sanity/output_list] ***************************
changed: [localhost -> localhost]

TASK [get host patch status] ***************************************************
changed: [localhost]

TASK [validate host patch status] **********************************************
skipping: [localhost]

TASK [get host status] *********************************************************
changed: [localhost]

TASK [validate host status] ****************************************************
skipping: [localhost]

TASK [get current alarms] ******************************************************
changed: [localhost]

TASK [validate current alarms] *************************************************
skipping: [localhost]

TASK [get vim status] **********************************************************
changed: [localhost]

TASK [validate vim status] *****************************************************
skipping: [localhost]

TASK [calculate / partition expected usage] ************************************
changed: [localhost]

TASK [validate / partition free space] *****************************************
skipping: [localhost]

TASK [validate /opt/dc-vault partition free space] *****************************
skipping: [localhost]

TASK [identify N3000 NICs] *****************************************************
changed: [localhost]

TASK [get N3000 NICs firmware version] *****************************************

TASK [validate N3000 NICs firmware version] ************************************

TASK [get N3000 NICs MAC] ******************************************************

TASK [validate N3000 NICs MACs] ************************************************

TASK [identify Fortville NICs] *************************************************
changed: [localhost]

TASK [get Fortville NICs firmware version] *************************************
changed: [localhost] => (item=ens2f0)
changed: [localhost] => (item=ens2f1)
changed: [localhost] => (item=ens3f0)
changed: [localhost] => (item=ens3f1)

TASK [validate Fortville NICs firmware version] ********************************
skipping: [localhost] => (item=ens2f0)
skipping: [localhost] => (item=ens2f1)
skipping: [localhost] => (item=ens3f0)
skipping: [localhost] => (item=ens3f1)

TASK [get Fortville NICs MAC] **************************************************
changed: [localhost] => (item=ens2f0)
changed: [localhost] => (item=ens2f1)
changed: [localhost] => (item=ens3f0)
changed: [localhost] => (item=ens3f1)

TASK [validate Fortville NICs MACs] ********************************************
skipping: [localhost] => (item=ens2f0)
skipping: [localhost] => (item=ens2f1)
skipping: [localhost] => (item=ens3f0)
skipping: [localhost] => (item=ens3f1)

TASK [identify accelerators] ***************************************************
changed: [localhost]

TASK [retrieve device information] *********************************************

TASK [output device show information] ******************************************

TASK [retrieve device information] *********************************************

TASK [output field information] ************************************************

TASK [validate sriov_numvfs for Mount Bryce] ***********************************

TASK [validate driver and sriov_vf_driver fields] ******************************

TASK [validate extra_info field] ***********************************************

TASK [get pod status] **********************************************************
changed: [localhost]

TASK [validate pod status] *****************************************************
skipping: [localhost]

TASK [get system applications] *************************************************
changed: [localhost]

TASK [validate system applications] ********************************************
skipping: [localhost] => (item=cert-manager:21.05-17)
skipping: [localhost] => (item=nginx-ingress-controller:21.05-16)
skipping: [localhost] => (item=oidc-auth-apps:21.05-44)

PLAY [all] *********************************************************************

TASK [Gathering Facts] *********************************************************
ok: [localhost]

TASK [validate /scratch partition free space] **********************************
skipping: [localhost]

PLAY RECAP *********************************************************************
localhost                  : ok=20   changed=14   unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ cat /home/XXXXXX/sanity/output_list
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ system application-show --format value --column app_version wr-analytics | cut -d- -f1
application not found: wr-analytics
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ cat /home/XXXXXX/sanity/output_list
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ system application-show --format value --column app_version wr-analytics | cut -d- -f1
application not found: wr-analytics
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ system license-show | grep "21.12"
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ system license-install ../license.lic
Error: Could not open file ../license.lic for read.
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ pwd
/opt/platform-backup/upgrade/wrcp-21.12-upgrade
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ls ../license_2112.lic
../license_2112.lic
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ system license-install ../license_2112.lic
Success: new license installed

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ system license-show | grep "21.12"
        COMPONENTS=WRCP_CONTAINER:21.12 OPTIONS=SUITE \
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ system --os-region-name SystemController load-import ../WRCP-2112-PATCH/wind-river-cloud-platform-host-installer-21.12-b45-PATCH_0010.iso ../WRCP-2112-PATCH/wind-river-cloud-platform-host-installer-21.12-b45-PATCH_0010.sig
This operation will take a while. Please wait.
............................................................................................................................................................................. ...................................
+--------------------+-----------------------+
| Property           | Value                 |
+--------------------+-----------------------+
| id                 | 2                     |
| state              | importing             |
| software_version   | 21.12                 |
| compatible_version | 21.05                 |
| required_patches   | WRCP_21.05_PATCH_0005 |
+--------------------+-----------------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$  system --os-region-name SystemController load-list
+----+----------+------------------+
| id | state    | software_version |
+----+----------+------------------+
| 1  | active   | 21.05            |
| 2  | imported | 21.12            |
+----+----------+------------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./set-intel-driver-version_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook --inventory controller --ask-pass --user XXXXXX \
> set-intel-driver-version.yaml 0</dev/null
SSH password:

XXXXXX [all] *********************************************************************

TASK [Retrieve platform release version] ***************************************
changed: [localhost]

TASK [Retrieve intel_nic_driver_version service parameter] *********************
changed: [localhost]

TASK [Store service parameter field values] ************************************
skipping: [localhost]

TASK [Delete old intel_nic_driver_version service parameter with resource] *****
skipping: [localhost]

TASK [Clear the driver version] ************************************************
skipping: [localhost]

TASK [Set Intel driver version (with resource)] ********************************
changed: [localhost]

TASK [Set Intel driver version] ************************************************
skipping: [localhost]

TASK [Apply service parameters] ************************************************
changed: [localhost]

TASK [Retrieve current Intel driver version] ***********************************
changed: [localhost]

PLAY RECAP *********************************************************************
localhost                  : ok=5    changed=5    unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ fm alarm-list

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$


```
### Completed prestaging 

### Mop 1 Section 4 Deployment

```log
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ cd
[XXXXXX@controller-0 ~(keystone_admin)]$ cd /opt/platform-backup/upgrade/wrcp-21.12-upgrade
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ system health-query-upgrade
System Health:
All hosts are provisioned: [OK]
All hosts are unlocked/enabled: [OK]
All hosts have current configurations: [OK]
All hosts are patch current: [OK]
No alarms: [OK]
All kubernetes nodes are ready: [OK]
All kubernetes control plane pods are ready: [OK]
Required patches are applied: [OK]
License valid for upgrade: [OK]
All kubernetes applications are in a valid state: [OK]
Active controller is controller-0: [OK]

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ fm alarm-list --mgmt_affecting --nowrap | awk -F \| '$6 ~ / True / { print $0 }'
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ system upgrade-start --force
+--------------+--------------------------------------+
| Property     | Value                                |
+--------------+--------------------------------------+
| uuid         | 65d23774-fcc6-45b5-bfd9-db2fe6067de2 |
| state        | starting                             |
| from_release | 21.05                                |
| to_release   | 21.12                                |
+--------------+--------------------------------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

Every 2.0s: system upgrade-show                                                                                                           Mon Sep 11 22:48:00 2023

+--------------+--------------------------------------+
| Property     | Value                                |
+--------------+--------------------------------------+
| uuid         | 65d23774-fcc6-45b5-bfd9-db2fe6067de2 |
| state        | started                              |
| from_release | 21.05                                |
| to_release   | 21.12                                |
+--------------+--------------------------------------+

```

### 4.2 Upgrade system controller controller-1

```log
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ system host-lock controller-1
+-----------------------+-------------------------------------------------+
| Property              | Value                                           |
+-----------------------+-------------------------------------------------+
| action                | none                                            |
| administrative        | unlocked                                        |
| availability          | available                                       |
| bm_ip                 | 2607:f160:a:d02e:cd:fe0::8001                   |
| bm_type               | redfish                                         |
| bm_username           | OSPctl                                          |
| boot_device           | /dev/disk/by-path/pci-0000:5c:00.0-scsi-0:1:0:0 |
| capabilities          | {}                                              |
| clock_synchronization | ntp                                             |
| config_applied        | 7671997a-d586-4951-8ff5-956b708e4198            |
| config_status         | None                                            |
| config_target         | 7671997a-d586-4951-8ff5-956b708e4198            |
| console               | ttyS0,115200                                    |
| created_at            | 2023-08-26T05:19:18.631627+00:00                |
| device_image_update   | None                                            |
| hostname              | controller-1                                    |
| id                    | 2                                               |
| install_output        | text                                            |
| install_state         | completed                                       |
| install_state_info    | None                                            |
| inv_state             | inventoried                                     |
| invprovision          | provisioned                                     |
| location              | {}                                              |
| mgmt_ip               | 2607:f160:0:3042:cd:290:0:12                    |
| mgmt_mac              | 48:df:37:bb:1f:f8                               |
| operational           | enabled                                         |
| personality           | controller                                      |
| reboot_needed         | False                                           |
| reserved              | False                                           |
| rootfs_device         | /dev/disk/by-path/pci-0000:5c:00.0-scsi-0:1:0:0 |
| serialid              | None                                            |
| software_load         | 21.05                                           |
| task                  | Locking                                         |
| tboot                 | false                                           |
| ttys_dcd              | None                                            |
| updated_at            | 2023-09-11T22:45:55.458319+00:00                |
| uptime                | 1444142                                         |
| uuid                  | 5a47ec4b-6652-4cf4-9333-cd0eba25148c            |
| vim_progress_status   | services-enabled                                |
+-----------------------+-------------------------------------------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

Every 2.0s: system host-list | grep controller-1                                                                                          Mon Sep 11 23:09:22 2023

| 2  | controller-1 | controller  | locked         | disabled    | online	|

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ system host-upgrade controller-1
+-----------------------+-------------------------------------------------+
| Property              | Value                                           |
+-----------------------+-------------------------------------------------+
| action                | none                                            |
| administrative        | locked                                          |
| availability          | online                                          |
| bm_ip                 | 2607:f160:a:d02e:cd:fe0::8001                   |
| bm_type               | redfish                                         |
| bm_username           | OSPctl                                          |
| boot_device           | /dev/disk/by-path/pci-0000:5c:00.0-scsi-0:1:0:0 |
| capabilities          | {}                                              |
| clock_synchronization | ntp                                             |
| config_applied        | 7671997a-d586-4951-8ff5-956b708e4198            |
| config_status         | None                                            |
| config_target         | 7671997a-d586-4951-8ff5-956b708e4198            |
| console               | ttyS0,115200                                    |
| created_at            | 2023-08-26T05:19:18.631627+00:00                |
| device_image_update   | None                                            |
| hostname              | controller-1                                    |
| id                    | 2                                               |
| install_output        | text                                            |
| install_state         | completed                                       |
| install_state_info    | None                                            |
| inv_state             | inventoried                                     |
| invprovision          | provisioned                                     |
| location              | {}                                              |
| mgmt_ip               | 2607:f160:0:3042:cd:290:0:12                    |
| mgmt_mac              | 48:df:37:bb:1f:f8                               |
| operational           | disabled                                        |
| personality           | controller                                      |
| reboot_needed         | False                                           |
| reserved              | False                                           |
| rootfs_device         | /dev/disk/by-path/pci-0000:5c:00.0-scsi-0:1:0:0 |
| serialid              | None                                            |
| software_load         | 21.05                                           |
| task                  |                                                 |
| tboot                 | false                                           |
| ttys_dcd              | None                                            |
| updated_at            | 2023-09-11T23:09:03.551527+00:00                |
| uptime                | 1445307                                         |
| uuid                  | 5a47ec4b-6652-4cf4-9333-cd0eba25148c            |
| vim_progress_status   | services-disabled                               |
+-----------------------+-------------------------------------------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
Every 2.0s: system upgrade-show                                                                                                           Mon Sep 11 23:14:10 2023

+--------------+--------------------------------------+
| Property     | Value                                |
+--------------+--------------------------------------+
| uuid         | 65d23774-fcc6-45b5-bfd9-db2fe6067de2 |
| state        | data-migration                       |
| from_release | 21.05                                |
| to_release   | 21.12                                |
+--------------+--------------------------------------+

Every 2.0s: system upgrade-show                                                                                                           Mon Sep 11 23:27:06 2023

+--------------+--------------------------------------+
| Property     | Value                                |
+--------------+--------------------------------------+
| uuid         | 65d23774-fcc6-45b5-bfd9-db2fe6067de2 |
| state        | data-migration-complete              |
| from_release | 21.05                                |
| to_release   | 21.12                                |
+--------------+--------------------------------------+

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ system host-unlock controller-1
+-----------------------+-------------------------------------------------+
| Property              | Value                                           |
+-----------------------+-------------------------------------------------+
| action                | none                                            |
| administrative        | locked                                          |
| availability          | online                                          |
| bm_ip                 | 2607:f160:a:d02e:cd:fe0::8001                   |
| bm_type               | redfish                                         |
| bm_username           | OSPctl                                          |
| boot_device           | /dev/disk/by-path/pci-0000:5c:00.0-scsi-0:1:0:0 |
| capabilities          | {}                                              |
| clock_synchronization | ntp                                             |
| config_applied        | 7671997a-d586-4951-8ff5-956b708e4198            |
| config_status         | None                                            |
| config_target         | 7671997a-d586-4951-8ff5-956b708e4198            |
| console               | ttyS0,115200                                    |
| created_at            | 2023-08-26T05:19:18.631627+00:00                |
| device_image_update   | None                                            |
| hostname              | controller-1                                    |
| id                    | 2                                               |
| install_output        | text                                            |
| install_state         | completed                                       |
| install_state_info    | None                                            |
| inv_state             | inventoried                                     |
| invprovision          | provisioned                                     |
| location              | {}                                              |
| mgmt_ip               | 2607:f160:0:3042:cd:290:0:12                    |
| mgmt_mac              | 48:df:37:bb:1f:f8                               |
| operational           | disabled                                        |
| personality           | controller                                      |
| reboot_needed         | False                                           |
| reserved              | False                                           |
| rootfs_device         | /dev/disk/by-path/pci-0000:5c:00.0-scsi-0:1:0:0 |
| serialid              | None                                            |
| software_load         | 21.12                                           |
| task                  | Unlocking                                       |
| tboot                 | false                                           |
| ttys_dcd              | None                                            |
| updated_at            | 2023-09-11T23:27:03.689083+00:00                |
| uptime                | 201                                             |
| uuid                  | 5a47ec4b-6652-4cf4-9333-cd0eba25148c            |
| vim_progress_status   | services-disabled                               |
+-----------------------+-------------------------------------------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$



Every 2.0s: system host-list | grep controller-1                                                                                          Mon Sep 11 23:39:59 2023

| 2  | controller-1 | controller  | unlocked	   | enabled     | degraded	|


Every 2.0s: fm alarm-list --nowrap --query alarm_id=400.001                                                                               Mon Sep 11 23:45:59 2023
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ system host-show controller-1 --column software_load --format value
21.12
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ system upgrade-show
+--------------+--------------------------------------+
| Property     | Value                                |
+--------------+--------------------------------------+
| uuid         | 65d23774-fcc6-45b5-bfd9-db2fe6067de2 |
| state        | upgrading-controllers                |
| from_release | 21.05                                |
| to_release   | 21.12                                |
+--------------+--------------------------------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ system host-swact controller-0 && exit
+-----------------------+-------------------------------------------------+
| Property              | Value                                           |
+-----------------------+-------------------------------------------------+
| action                | none                                            |
| administrative        | unlocked                                        |
| availability          | available                                       |
| bm_ip                 | 2607:f160:a:d02e:cd:fe0::8000                   |
| bm_type               | redfish                                         |
| bm_username           | OSPctl                                          |
| boot_device           | /dev/disk/by-path/pci-0000:5c:00.0-scsi-0:1:0:0 |
| capabilities          | {}                                              |
| clock_synchronization | ntp                                             |
| config_applied        | 7671997a-d586-4951-8ff5-956b708e4198            |
| config_status         | None                                            |
| config_target         | 7671997a-d586-4951-8ff5-956b708e4198            |
| console               | ttyS0,115200                                    |
| created_at            | 2023-08-26T04:44:50.532044+00:00                |
| device_image_update   | None                                            |
| hostname              | controller-0                                    |
| id                    | 1                                               |
| install_output        | text                                            |
| install_state         | None                                            |
| install_state_info    | None                                            |
| inv_state             | inventoried                                     |
| invprovision          | provisioned                                     |
| location              | {}                                              |
| mgmt_ip               | 2607:f160:0:3042:cd:290:0:11                    |
| mgmt_mac              | 48:df:37:bb:1c:84                               |
| operational           | enabled                                         |
| personality           | controller                                      |
| reboot_needed         | False                                           |
| reserved              | False                                           |
| rootfs_device         | /dev/disk/by-path/pci-0000:5c:00.0-scsi-0:1:0:0 |
| serialid              | None                                            |
| software_load         | 21.05                                           |
| task                  | Swacting                                        |
| tboot                 | false                                           |
| ttys_dcd              | None                                            |
| updated_at            | 2023-09-11T23:46:58.527605+00:00                |
| uptime                | 9727                                            |
| uuid                  | 6332fe27-8284-463b-a573-a8b3b38846de            |
| vim_progress_status   | services-enabled                                |
+-----------------------+-------------------------------------------------+
logout
Connection to 2607:f160:0:3043:cd:290:0:10 closed.
[XXXXXX@vcpe-jumpserver ~]$

logging into OAM of controller-1

[XXXXXX@controller-1 ~(keystone_admin)]$ sw-manager upgrade-strategy create --alarm-restrictions relaxed
Strategy Upgrade Strategy:
  strategy-uuid:                          680d576e-5b0e-4f78-abdd-d4c36e8daa80
  controller-apply-type:                  serial
  storage-apply-type:                     serial
  worker-apply-type:                      serial
  default-instance-action:                migrate
  alarm-restrictions:                     relaxed
  current-phase:                          build
  current-phase-completion:               0%
  state:                                  building
  inprogress:                             true
[XXXXXX@controller-1 ~(keystone_admin)]$
Every 2.0s: sw-manager upgrade-strategy show                                                                                              Mon Sep 11 23:52:17 2023

Strategy Upgrade Strategy:
  strategy-uuid:                          680d576e-5b0e-4f78-abdd-d4c36e8daa80
  controller-apply-type:                  serial
  storage-apply-type:                     serial
  worker-apply-type:                      serial
  default-instance-action:                migrate
  alarm-restrictions:                     relaxed
  current-phase:                          build
  current-phase-completion:               100%
  state:                                  ready-to-apply
  build-result:                           success
  build-reason:


[XXXXXX@controller-1 ~(keystone_admin)]$ sw-manager upgrade-strategy apply
Strategy Upgrade Strategy:
  strategy-uuid:                          680d576e-5b0e-4f78-abdd-d4c36e8daa80
  controller-apply-type:                  serial
  storage-apply-type:                     serial
  worker-apply-type:                      serial
  default-instance-action:                migrate
  alarm-restrictions:                     relaxed
  current-phase:                          apply
  current-phase-completion:               0%
  state:                                  applying
  inprogress:                             true
[XXXXXX@controller-1 ~(keystone_admin)]$

Every 2.0s: sw-manager upgrade-strategy show                                                                                              Mon Sep 11 23:53:03 2023

[XXXXXX@controller-1 ~(keystone_admin)]$ sw-manager upgrade-strategy apply

Strategy Upgrade Strategy:
  strategy-uuid:                          680d576e-5b0e-4f78-abdd-d4c36e8daa80
  controller-apply-type:                  serial
  storage-apply-type:                     serial
  worker-apply-type:                      serial
  default-instance-action:                migrate
  alarm-restrictions:                     relaxed
  current-phase:                          apply
  current-phase-completion:               10%
  state:                                  applying
  inprogress:                             true


Every 2.0s: sw-manager upgrade-strategy show                                                                                              Tue Sep 12 01:04:21 2023

Strategy Upgrade Strategy:
  strategy-uuid:                          680d576e-5b0e-4f78-abdd-d4c36e8daa80
  controller-apply-type:                  serial
  storage-apply-type:                     serial
  worker-apply-type:                      serial
  default-instance-action:                migrate
  alarm-restrictions:                     relaxed
  current-phase:                          apply
  current-phase-completion:               100%
  state:                                  applied
  apply-result:                           success
  apply-reason:



[XXXXXX@controller-1 ~(keystone_admin)]$ sw-manager upgrade-strategy delete
Strategy deleted
[XXXXXX@controller-1 ~(keystone_admin)]$
[XXXXXX@controller-1 ~(keystone_admin)]$ system host-swact controller-1 && exit
+-----------------------+-------------------------------------------------+
| Property              | Value                                           |
+-----------------------+-------------------------------------------------+
| action                | none                                            |
| administrative        | unlocked                                        |
| availability          | available                                       |
| bm_ip                 | 2607:f160:a:d02e:cd:fe0::8001                   |
| bm_type               | redfish                                         |
| bm_username           | OSPctl                                          |
| boot_device           | /dev/disk/by-path/pci-0000:5c:00.0-scsi-0:1:0:0 |
| capabilities          | {}                                              |
| clock_synchronization | ntp                                             |
| config_applied        | 7671997a-d586-4951-8ff5-956b708e4198            |
| config_status         | None                                            |
| config_target         | None                                            |
| console               | ttyS0,115200                                    |
| created_at            | 2023-08-26T05:19:18.631627+00:00                |
| device_image_update   | None                                            |
| hostname              | controller-1                                    |
| id                    | 2                                               |
| install_output        | text                                            |
| install_state         | completed                                       |
| install_state_info    | None                                            |
| inv_state             | inventoried                                     |
| invprovision          | provisioned                                     |
| location              | {}                                              |
| mgmt_ip               | 2607:f160:0:3042:cd:290:0:12                    |
| mgmt_mac              | 48:df:37:bb:1f:f8                               |
| operational           | enabled                                         |
| personality           | controller                                      |
| reboot_needed         | False                                           |
| reserved              | False                                           |
| rootfs_device         | /dev/disk/by-path/pci-0000:5c:00.0-scsi-0:1:0:0 |
| serialid              | None                                            |
| software_load         | 21.12                                           |
| task                  | Swacting                                        |
| tboot                 | false                                           |
| ttys_dcd              | None                                            |
| updated_at            | 2023-09-12T01:02:01.559852+00:00                |
| uptime                | 5122                                            |
| uuid                  | 5a47ec4b-6652-4cf4-9333-cd0eba25148c            |
| vim_progress_status   | services-enabled                                |
+-----------------------+-------------------------------------------------+
logout
Connection to 2607:f160:0:3043:cd:290:0:10 closed.
[XXXXXX@vcpe-jumpserver ~]$

controller-0:~$ source /etc/platform/openrc
[XXXXXX@controller-0 ~(keystone_admin)]$ cd /opt/platform-backup/upgrade/wrcp-21.12-upgrade
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ system upgrade-activate
+--------------+--------------------------------------+
| Property     | Value                                |
+--------------+--------------------------------------+
| uuid         | 65d23774-fcc6-45b5-bfd9-db2fe6067de2 |
| state        | activation-requested                 |
| from_release | 21.05                                |
| to_release   | 21.12                                |
+--------------+--------------------------------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$



Every 2.0s: system upgrade-show                                                                                                           Tue Sep 12 01:11:07 2023

+--------------+--------------------------------------+
| Property     | Value                                |
+--------------+--------------------------------------+
| uuid         | 65d23774-fcc6-45b5-bfd9-db2fe6067de2 |
| state        | activating                           |
| from_release | 21.05                                |
| to_release   | 21.12                                |
+--------------+--------------------------------------+

Every 2.0s: system upgrade-show                                                                                                           Tue Sep 12 01:20:46 2023

+--------------+--------------------------------------+
| Property     | Value                                |
+--------------+--------------------------------------+
| uuid         | 65d23774-fcc6-45b5-bfd9-db2fe6067de2 |
| state        | activation-complete                  |
| from_release | 21.05                                |
| to_release   | 21.12                                |
+--------------+--------------------------------------+

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ system upgrade-complete
+--------------+--------------------------------------+
| Property     | Value                                |
+--------------+--------------------------------------+
| uuid         | 65d23774-fcc6-45b5-bfd9-db2fe6067de2 |
| state        | completing                           |
| from_release | 21.05                                |
| to_release   | 21.12                                |
+--------------+--------------------------------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

Every 2.0s: system upgrade-show                                                                                                           Tue Sep 12 01:21:50 2023

No upgrade in progress

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ system host-upgrade-list
+----+--------------+-------------+-----------------+----------------+
| id | hostname     | personality | running_release | target_release |
+----+--------------+-------------+-----------------+----------------+
| 1  | controller-0 | controller  | 21.12           | 21.12          |
| 2  | controller-1 | controller  | 21.12           | 21.12          |
| 3  | worker-0     | worker      | 21.12           | 21.12          |
+----+--------------+-------------+-----------------+----------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./confirm-ice-driver-version_$(date "+%Y%m%d%H%M%S").log \
> ansible all --inventory controller-0,controller-1,worker-0, --ask-pass --ask-become-pass \
> --user XXXXXX --become --module-name shell \
> --args "grep -E 'ice\:.*1\.5\.8$' /var/log/dmesg"
SSH password:
XXXXXX password[defaults to SSH password]:
worker-0 | CHANGED | rc=0 >>
[   19.650038] ice: Intel(R) Ethernet Connection E800 Series Linux Driver - version 1.5.8

controller-1 | CHANGED | rc=0 >>
[   18.246815] ice: Intel(R) Ethernet Connection E800 Series Linux Driver - version 1.5.8

controller-0 | CHANGED | rc=0 >>
[   18.195597] ice: Intel(R) Ethernet Connection E800 Series Linux Driver - version 1.5.8

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./apply-kubelet-config_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook apply-kubelet-config.yaml 0</dev/null

PLAY [all] *********************************************************************

TASK [Remove kubelet-config settings for old versions] *************************
changed: [localhost]

TASK [Reapply kubelet-config settings] *****************************************
changed: [localhost]

TASK [Wait for kubelet-config settings to be applied] **************************
FAILED - RETRYING: Wait for kubelet-config settings to be applied (10 retries left).
changed: [localhost]

TASK [Output kubelet-config info] **********************************************
ok: [localhost] => {
    "msg": [
        "imageGCLowThresholdPercent: 75",
        "imageGCHighThresholdPercent: 79",
        "evictionHard:",
        "  imagefs.available: 2Gi",
        "  memory.available: 100Mi",
        "  nodefs.inodesFree: 5%",
        "  nodefs.available: 10%",
        "    imageGCLowThresholdPercent: 75",
        "    imageGCHighThresholdPercent: 79",
        "    evictionHard:",
        "      imagefs.available: 2Gi",
        "      memory.available: 100Mi",
        "      nodefs.inodesFree: 5%",
        "      nodefs.available: 10%"
    ]
}

PLAY RECAP *********************************************************************
localhost                  : ok=4    changed=3    unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ sleep 240

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ vi registry-vars.yaml
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./pull-images_$(date "+%Y%m%d%H%M%S").log ansible-playbook --inventory localhost, --extra-vars "@registry-vars.yaml" --ask-pass --ask-become-pass pull-images.yaml 0</dev/null
SSH password:
XXXXXX password[defaults to SSH password]:

PLAY [all] *********************************************************************

TASK [Validate private_registry] ***********************************************
skipping: [localhost]

TASK [Validate private_registry_user] ******************************************
skipping: [localhost]

TASK [Validate private_registry_pass] ******************************************
skipping: [localhost]

TASK [Validate local_registry_pass] ********************************************
skipping: [localhost]

TASK [Read in images list] *****************************************************
ok: [localhost]

TASK [Log in to private registry] **********************************************
changed: [localhost]

TASK [Pull images from private registry] ***************************************
changed: [localhost] => (item=docker.io/rabbitmq:3.8.11-management)
changed: [localhost] => (item=docker.io/starlingx/locationservice-base:stx.5.0-v1.0.1)
changed: [localhost] => (item=docker.io/starlingx/notificationclient-base:stx.5.0-v1.0.4)
changed: [localhost] => (item=docker.io/starlingx/notificationservice-base:stx.6.0-v1.0.7)
changed: [localhost] => (item=docker.io/wind-river/cloud-platform-deployment-manager:WRCP_21.12-wrs.4)
changed: [localhost] => (item=k8s.gcr.io/metrics-server/metrics-server:v0.4.1)

TASK [Tag local images] ********************************************************
changed: [localhost] => (item=docker.io/rabbitmq:3.8.11-management)
changed: [localhost] => (item=docker.io/starlingx/locationservice-base:stx.5.0-v1.0.1)
changed: [localhost] => (item=docker.io/starlingx/notificationclient-base:stx.5.0-v1.0.4)
changed: [localhost] => (item=docker.io/starlingx/notificationservice-base:stx.6.0-v1.0.7)
changed: [localhost] => (item=docker.io/wind-river/cloud-platform-deployment-manager:WRCP_21.12-wrs.4)
changed: [localhost] => (item=k8s.gcr.io/metrics-server/metrics-server:v0.4.1)

TASK [Log in to local registry] ************************************************
changed: [localhost]

TASK [Push images to local registry] *******************************************
changed: [localhost] => (item=docker.io/rabbitmq:3.8.11-management)
changed: [localhost] => (item=docker.io/starlingx/locationservice-base:stx.5.0-v1.0.1)
changed: [localhost] => (item=docker.io/starlingx/notificationclient-base:stx.5.0-v1.0.4)
changed: [localhost] => (item=docker.io/starlingx/notificationservice-base:stx.6.0-v1.0.7)
changed: [localhost] => (item=docker.io/wind-river/cloud-platform-deployment-manager:WRCP_21.12-wrs.4)
changed: [localhost] => (item=k8s.gcr.io/metrics-server/metrics-server:v0.4.1)

TASK [Verify images in local registry] *****************************************
changed: [localhost] => (item=docker.io/rabbitmq:3.8.11-management)
changed: [localhost] => (item=docker.io/starlingx/locationservice-base:stx.5.0-v1.0.1)
changed: [localhost] => (item=docker.io/starlingx/notificationclient-base:stx.5.0-v1.0.4)
changed: [localhost] => (item=docker.io/starlingx/notificationservice-base:stx.6.0-v1.0.7)
changed: [localhost] => (item=docker.io/wind-river/cloud-platform-deployment-manager:WRCP_21.12-wrs.4)
changed: [localhost] => (item=k8s.gcr.io/metrics-server/metrics-server:v0.4.1)

TASK [Clean the local image cache] *********************************************
changed: [localhost] => (item=docker.io/rabbitmq:3.8.11-management)
changed: [localhost] => (item=docker.io/starlingx/locationservice-base:stx.5.0-v1.0.1)
changed: [localhost] => (item=docker.io/starlingx/notificationclient-base:stx.5.0-v1.0.4)
changed: [localhost] => (item=docker.io/starlingx/notificationservice-base:stx.6.0-v1.0.7)
changed: [localhost] => (item=docker.io/wind-river/cloud-platform-deployment-manager:WRCP_21.12-wrs.4)
changed: [localhost] => (item=k8s.gcr.io/metrics-server/metrics-server:v0.4.1)

PLAY RECAP *********************************************************************
localhost                  : ok=8    changed=7    unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ kubectl delete secret -n platform-deployment-manager \
> platform-deployment-manager-webhook-server-secret
secret "platform-deployment-manager-webhook-server-secret" deleted
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ kubectl delete secret -n platform-deployment-manager \
> platform-deployment-manager-webhook-server-secret
secret "platform-deployment-manager-webhook-server-secret" deleted
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ XXXXXX_password=XXXXXX
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ cp /usr/local/share/applications/overrides/examples/dm-playbook-overrides.yaml .
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ chmod 644 dm-playbook-overrides.yaml
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ echo "ansible_become_pass: \"${XXXXXX_password}\"" >> dm-playbook-overrides.yaml
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ cp /usr/local/share/applications/overrides/examples/dm-playbook-overrides.yaml .
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ chmod 644 dm-playbook-overrides.yaml
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ echo "ansible_become_pass: \"${XXXXXX_password}\"" >> dm-playbook-overrides.yaml
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./upgrade-dm_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook --extra-vars "@dm-playbook-overrides.yaml" \
> /usr/local/share/applications/playbooks/wind-river-cloud-platform-deployment-manager.yaml \
> 0</dev/null

PLAY [Deployment Manager Playbook] *********************************************

TASK [set_fact] ****************************************************************
ok: [localhost]

TASK [set_fact] ****************************************************************
ok: [localhost]

TASK [set_fact] ****************************************************************
skipping: [localhost]

TASK [Create A Temporary Download Directory] ***********************************
skipping: [localhost]

TASK [Download Deployment Manager Helm Chart From Repo] ************************
skipping: [localhost]

TASK [Reference Downloaded Helm Chart] *****************************************
skipping: [localhost]

TASK [Upload Deployment Manager Helm Chart] ************************************
skipping: [localhost]

TASK [set_fact] ****************************************************************
skipping: [localhost]

TASK [Upload Deployment Manager Helm Chart Overrides] **************************
skipping: [localhost]

TASK [set_fact] ****************************************************************
skipping: [localhost]

TASK [Clean download directory] ************************************************
skipping: [localhost]

TASK [Retrieve software version number] ****************************************
changed: [localhost]

TASK [Fail if software version is not defined] *********************************
skipping: [localhost]

TASK [Set software version and platform path] **********************************
ok: [localhost]

TASK [Set config path facts] ***************************************************
ok: [localhost]

TASK [Mark the bootstrap as finalized] *****************************************
changed: [localhost]

TASK [Get list of releases in helmv2] ******************************************
changed: [localhost]

TASK [Query for DM release in helmv2] ******************************************
fatal: [localhost]: FAILED! => {"changed": true, "cmd": "grep -iq '\"name\":\"deployment-manager\"' <<< [u'{\"Next\":\"\",\"Releases\":[{\"Name\":\"cm-cert-manager\",\"Revision\":3,\"Updated\":\"Tue Sep 12 01:11:04 2023\",\"Status\":\"DEPLOYED\",\"Chart\":\"cert-manager-v0.1.0\",\"AppVersion\":\"\",\"Namespace\":\"cert-manager\"},{\"Name\":\"cm-cert-manager-psp-rolebinding\",\"Revision\":1,\"Updated\":\"Sat Aug 26 05:05:24 2023\",\"Status\":\"DEPLOYED\",\"Chart\":\"psp-rolebinding-0.1.0\",\"AppVersion\":\"\",\"Namespace\":\"cert-manager\"},{\"Name\":\"ic-nginx-ingress\",\"Revision\":2,\"Updated\":\"Tue Sep 12 01:12:10 2023\",\"Status\":\"DEPLOYED\",\"Chart\":\"ingress-nginx-3.10.1\",\"AppVersion\":\"\",\"Namespace\":\"kube-system\"},{\"Name\":\"oidc-auth-secret-observer\",\"Revision\":1,\"Updated\":\"Tue Sep 12 01:17:49 2023\",\"Status\":\"DEPLOYED\",\"Chart\":\"secret-observer-0.1.0\",\"AppVersion\":\"\",\"Namespace\":\"kube-system\"},{\"Name\":\"oidc-dex\",\"Revision\":2,\"Updated\":\"Tue Sep 12 01:16:52 2023\",\"Status\":\"DEPLOYED\",\"Chart\":\"dex-0.8.0\",\"AppVersion\":\"\",\"Namespace\":\"kube-system\"},{\"Name\":\"oidc-oidc-client\",\"Revision\":2,\"Updated\":\"Tue Sep 12 01:17:25 2023\",\"Status\":\"DEPLOYED\",\"Chart\":\"oidc-client-0.1.0\",\"AppVersion\":\"\",\"Namespace\":\"kube-system\"}]}']", "delta": "0:00:00.002930", "end": "2023-09-12 02:29:38.960058", "msg": "non-zero return code", "rc": 1, "start": "2023-09-12 02:29:38.957128", "stderr": "", "stderr_lines": [], "stdout": "", "stdout_lines": []}
...ignoring

TASK [Get list of releases in helmv3] ******************************************
changed: [localhost]

TASK [Query for DM release in helmv3] ******************************************
changed: [localhost]

TASK [Get armada pod name] *****************************************************
skipping: [localhost]

TASK [Show armada pod] *********************************************************
skipping: [localhost]

TASK [Copy files into tiller container if using helmv2] ************************
skipping: [localhost]

TASK [Reinstall Deployment Manager (helmv2)] ***********************************
skipping: [localhost]

TASK [Search webhook configurations for v1] ************************************
changed: [localhost]

TASK [Query for validating webhook configuration] ******************************
changed: [localhost]

TASK [Delete validating webhook configuration] *********************************
changed: [localhost]

TASK [Search webhook service for v1] *******************************************
changed: [localhost]

TASK [Query for webhook-server-service] ****************************************
changed: [localhost]

TASK [Delete webhook-server-service] *******************************************
changed: [localhost]

TASK [Search webhook secret for v1] ********************************************
changed: [localhost]

TASK [Query for webhook-server-secret] *****************************************
fatal: [localhost]: FAILED! => {"changed": true, "cmd": "grep -iq 'webhook-server-secret' <<< []", "delta": "0:00:00.002454", "end": "2023-09-12 02:29:40.424153", "msg": "non-zero return code", "rc": 1, "start": "2023-09-12 02:29:40.421699", "stderr": "", "stderr_lines": [], "stdout": "", "stdout_lines": []}
...ignoring

TASK [Delete webhook-server-secret] ********************************************
skipping: [localhost]

TASK [Install Deployment Manager] **********************************************
changed: [localhost]

TASK [Search for the pod of the Deployment Manager] ****************************
changed: [localhost]

TASK [debug] *******************************************************************
ok: [localhost] => {
    "msg": "platform-deployment-manager-0"
}

TASK [Restart Deployment Manager if reinstalled] *******************************
changed: [localhost]

TASK [Wait for Deployment Manager to be ready] *********************************
changed: [localhost]

TASK [Upload Deployment Configuration File] ************************************
skipping: [localhost]

TASK [set_fact] ****************************************************************
skipping: [localhost]

TASK [wait_for] ****************************************************************
skipping: [localhost]

TASK [Apply Deployment Configuration File] *************************************
skipping: [localhost]

TASK [Get platform-deployment-manager namespace default registry key] **********
changed: [localhost]

TASK [Copy default-registry-key to platform-deployment-manager namespace] ******
skipping: [localhost]

PLAY RECAP *********************************************************************
localhost                  : ok=24   changed=19   unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ rm -f dm-playbook-overrides.yaml
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ kubectl get pods --selector control-plane=controller-manager \
> --namespace platform-deployment-manager
NAME                            READY   STATUS    RESTARTS   AGE
platform-deployment-manager-0   2/2     Running   2          52s
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ kubectl get pods --selector control-plane=controller-manager \
> --namespace platform-deployment-manager \
> --output jsonpath="{..image}" | tr -s '[[:space:]]' '\n'| sort | uniq
registry.local:9001/docker.io/wind-river/cloud-platform-deployment-manager:WRCP_21.12-wrs.4
registry.local:9001/gcr.io/kubebuilder/kube-rbac-proxy:v0.4.0
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$


[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ kubectl get pods --selector app=dm-monitor --namespace platform-deployment-manager
NAME                          READY   STATUS    RESTARTS   AGE
dm-monitor-7d7d8bd5df-sqj6k   1/1     Running   0          12s
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ kubectl get pods --selector app=dm-monitor --namespace platform-deployment-manager \
> --output jsonpath="{..image}" | tr -s '[[:space:]]' '\n'| sort | uniq
registry.local:9001/docker.io/wind-river/dm-monitor:WRCP_21.05-v1.0.0
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ cd /home/XXXXXX
[XXXXXX@controller-0 ~(keystone_admin)]$ tridentctl version --namespace trident
+----------------+----------------+
| SERVER VERSION | CLIENT VERSION |
+----------------+----------------+
| 20.04.0        | 21.04.1        |
+----------------+----------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ yaml() { file=$1;shift;cmds=${@/#/;a};\
> python -c "import yaml;a=yaml.safe_load(open('${file}'))${cmds};print(yaml.dump(a))"; }
[XXXXXX@controller-0 ~(keystone_admin)]$ yaml /opt/platform-backup/upgrade/localhost.yml \
> "['netapp_k8s_storageclasses'][0]['parameters']['fsType']='nfs'" \
> "['trident_force_reinstall']=True" > localhost.yml
[XXXXXX@controller-0 ~(keystone_admin)]$ log_prefix=/opt/platform-backup/upgrade/wrcp-21.12-upgrade
[XXXXXX@controller-0 ~(keystone_admin)]$ ANSIBLE_CONFIG=${log_prefix}/ansible.cfg PATH=$PATH:/usr/sbin \
> ANSIBLE_LOG_PATH=${log_prefix}/netapp_upgrade_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook /usr/share/ansible/stx-ansible/playbooks/install_netapp_backend.yml \
> 0</dev/null

PLAY [all] *********************************************************************

TASK [common/prepare-env : stat] ***********************************************
ok: [localhost -> localhost] => (item=/home/XXXXXX/secrets.yml)
ok: [localhost -> localhost] => (item=/home/XXXXXX/localhost_secrets.yml)
ok: [localhost -> localhost] => (item=/home/XXXXXX/site.yml)
ok: [localhost -> localhost] => (item=/home/XXXXXX/localhost.yml)

TASK [common/prepare-env : include_vars] ***************************************
skipping: [localhost] => (item={'_ansible_parsed': True, u'stat': {u'exists': False}, '_ansible_item_result': True, '_ansible_no_log': False, '_ansible_delegated_vars': {'ansible_delegated_host': u'localhost', 'ansible_host': u'localhost'}, u'changed': False, 'failed': False, 'item': u'/home/XXXXXX/secrets.yml', u'invocation': {u'module_args': {u'get_checksum': True, u'follow': False, u'checksum_algorithm': u'sha1', u'path': u'/home/XXXXXX/secrets.yml', u'get_mime': True, u'get_md5': None, u'get_attributes': True}}, '_ansible_ignore_errors': None, '_ansible_item_label': u'/home/XXXXXX/secrets.yml'})
skipping: [localhost] => (item={'_ansible_parsed': True, u'stat': {u'exists': False}, '_ansible_item_result': True, '_ansible_no_log': False, '_ansible_delegated_vars': {'ansible_delegated_host': u'localhost', 'ansible_host': u'localhost'}, u'changed': False, 'failed': False, 'item': u'/home/XXXXXX/localhost_secrets.yml', u'invocation': {u'module_args': {u'get_checksum': True, u'follow': False, u'checksum_algorithm': u'sha1', u'path': u'/home/XXXXXX/localhost_secrets.yml', u'get_mime': True, u'get_md5': None, u'get_attributes': True}}, '_ansible_ignore_errors': None, '_ansible_item_label': u'/home/XXXXXX/localhost_secrets.yml'})
skipping: [localhost] => (item={'_ansible_parsed': True, u'stat': {u'exists': False}, '_ansible_item_result': True, '_ansible_no_log': False, '_ansible_delegated_vars': {'ansible_delegated_host': u'localhost', 'ansible_host': u'localhost'}, u'changed': False, 'failed': False, 'item': u'/home/XXXXXX/site.yml', u'invocation': {u'module_args': {u'get_checksum': True, u'follow': False, u'checksum_algorithm': u'sha1', u'path': u'/home/XXXXXX/site.yml', u'get_mime': True, u'get_md5': None, u'get_attributes': True}}, '_ansible_ignore_errors': None, '_ansible_item_label': u'/home/XXXXXX/site.yml'})
ok: [localhost] => (item={'_ansible_parsed': True, u'stat': {u'isuid': False, u'uid': 42425, u'exists': True, u'attr_flags': u'e', u'woth': False, u'device_type': 0, u'mtime': 1694485916.8306155, u'block_size': 4096, u'inode': 8727, u'isgid': False, u'size': 4098, u'executable': False, u'roth': True, u'charset': u'us-ascii', u'readable': True, u'isreg': True, u'version': u'18446744071894360215', u'pw_name': u'XXXXXX', u'gid': 345, u'ischr': False, u'wusr': True, u'writeable': True, u'isdir': False, u'blocks': 16, u'xoth': False, u'rusr': True, u'nlink': 1, u'issock': False, u'rgrp': True, u'gr_name': u'sys_protected', u'path': u'/home/XXXXXX/localhost.yml', u'xusr': False, u'atime': 1694485916.7856147, u'mimetype': u'text/x-c', u'ctime': 1694485916.8306155, u'isblk': False, u'checksum': u'716e3dfa99ef111e9f4d5fced1bf56ce887b3d95', u'dev': 2052, u'wgrp': False, u'isfifo': False, u'mode': u'0644', u'xgrp': False, u'islnk': False, u'attributes': [u'extents']}, '_ansible_item_result': True, '_ansible_no_log': False, '_ansible_delegated_vars': {'ansible_delegated_host': u'localhost', 'ansible_host': u'localhost'}, u'changed': False, 'failed': False, 'item': u'/home/XXXXXX/localhost.yml', u'invocation': {u'module_args': {u'get_checksum': True, u'follow': False, u'checksum_algorithm': u'sha1', u'path': u'/home/XXXXXX/localhost.yml', u'get_mime': True, u'get_md5': None, u'get_attributes': True}}, '_ansible_ignore_errors': None, '_ansible_item_label': u'/home/XXXXXX/localhost.yml'})

TASK [common/prepare-env : Set SSH port] ***************************************
skipping: [localhost]

TASK [common/prepare-env : Format the ansible host if it is an IP address] *****
skipping: [localhost]

TASK [common/prepare-env : Set SSH hostname] ***********************************
skipping: [localhost]

TASK [common/prepare-env : Set SSH hostname if SSH port is not default] ********
skipping: [localhost]

TASK [common/prepare-env : Check connectivity] *********************************
skipping: [localhost]

TASK [common/prepare-env : Fail if host is unreachable] ************************
skipping: [localhost]

TASK [common/prepare-env : Gather remote SSH public key] ***********************
skipping: [localhost]

TASK [common/prepare-env : Print warning if ssh-keyscan command is timed out] ***
skipping: [localhost]

TASK [common/prepare-env : Add remote SSH public keys into the known_hosts] ****
skipping: [localhost]

TASK [common/prepare-env : Fail if password change response sequence is not defined] ***
skipping: [localhost]

TASK [common/prepare-env : debug] **********************************************
skipping: [localhost]

TASK [common/prepare-env : Change initial password] ****************************
skipping: [localhost]

TASK [common/get-kube-version : Get kubernetes_version from the DB] ************
changed: [localhost]

TASK [common/get-kube-version : Set kubernetes_version to the value from DB] ***
ok: [localhost]

TASK [roles/common/push-docker-images : Set default values for docker_http_proxy and docker_https_proxy if they are undefined] ***
ok: [localhost]

TASK [roles/common/push-docker-images : Get docker registries if not in bootstap or restore mode] ***
included: /usr/share/ansible/stx-ansible/playbooks/roles/common/push-docker-images/tasks/get_docker_registry.yml for localhost => (item={u'name': u'k8s_registry', u'value': {u'url': u'k8s.gcr.io'}})
included: /usr/share/ansible/stx-ansible/playbooks/roles/common/push-docker-images/tasks/get_docker_registry.yml for localhost => (item={u'name': u'gcr_registry', u'value': {u'url': u'gcr.io'}})
included: /usr/share/ansible/stx-ansible/playbooks/roles/common/push-docker-images/tasks/get_docker_registry.yml for localhost => (item={u'name': u'quay_registry', u'value': {u'url': u'quay.io'}})
included: /usr/share/ansible/stx-ansible/playbooks/roles/common/push-docker-images/tasks/get_docker_registry.yml for localhost => (item={u'name': u'docker_registry', u'value': {u'url': u'docker.io'}})
included: /usr/share/ansible/stx-ansible/playbooks/roles/common/push-docker-images/tasks/get_docker_registry.yml for localhost => (item={u'name': u'elastic_registry', u'value': {u'url': u'docker.elastic.co'}})
included: /usr/share/ansible/stx-ansible/playbooks/roles/common/push-docker-images/tasks/get_docker_registry.yml for localhost => (item={u'name': u'ghcr_registry', u'value': {u'url': u'ghcr.io'}})

TASK [roles/common/push-docker-images : Query the k8s_registry] ****************
changed: [localhost]

TASK [roles/common/push-docker-images : set_fact] ******************************
ok: [localhost]

TASK [roles/common/push-docker-images : set_fact] ******************************
ok: [localhost] => (item=None)
ok: [localhost] => (item=None)
ok: [localhost] => (item=None)
ok: [localhost]

TASK [roles/common/push-docker-images : Validate k8s_registry information if it exists] ***
skipping: [localhost]

TASK [roles/common/push-docker-images : Set secure to bool] ********************
skipping: [localhost]

TASK [roles/common/push-docker-images : Get the k8s_registry barbican secret if it's authenticated] ***
changed: [localhost]

TASK [roles/common/push-docker-images : Validate k8s_registry secret] **********
skipping: [localhost]

TASK [roles/common/push-docker-images : set_fact] ******************************
ok: [localhost]

TASK [roles/common/push-docker-images : set_fact] ******************************
ok: [localhost]

TASK [roles/common/push-docker-images : set_fact] ******************************
ok: [localhost] => (item=None)
ok: [localhost] => (item=None)
ok: [localhost] => (item=None)
skipping: [localhost] => (item=None)
ok: [localhost] => (item=None)
ok: [localhost]

TASK [roles/common/push-docker-images : set_fact] ******************************
ok: [localhost]

TASK [roles/common/push-docker-images : Query the gcr_registry] ****************
changed: [localhost]

TASK [roles/common/push-docker-images : set_fact] ******************************
ok: [localhost]

TASK [roles/common/push-docker-images : set_fact] ******************************
ok: [localhost] => (item=None)
ok: [localhost] => (item=None)
ok: [localhost] => (item=None)
ok: [localhost]

TASK [roles/common/push-docker-images : Validate gcr_registry information if it exists] ***
skipping: [localhost]

TASK [roles/common/push-docker-images : Set secure to bool] ********************
skipping: [localhost]

TASK [roles/common/push-docker-images : Get the gcr_registry barbican secret if it's authenticated] ***
changed: [localhost]

TASK [roles/common/push-docker-images : Validate gcr_registry secret] **********
skipping: [localhost]

TASK [roles/common/push-docker-images : set_fact] ******************************
ok: [localhost]

TASK [roles/common/push-docker-images : set_fact] ******************************
ok: [localhost]

TASK [roles/common/push-docker-images : set_fact] ******************************
ok: [localhost] => (item=None)
ok: [localhost] => (item=None)
ok: [localhost] => (item=None)
skipping: [localhost] => (item=None)
ok: [localhost] => (item=None)
ok: [localhost]

TASK [roles/common/push-docker-images : set_fact] ******************************
ok: [localhost]

TASK [roles/common/push-docker-images : Query the quay_registry] ***************
changed: [localhost]

TASK [roles/common/push-docker-images : set_fact] ******************************
ok: [localhost]

TASK [roles/common/push-docker-images : set_fact] ******************************
ok: [localhost] => (item=None)
ok: [localhost] => (item=None)
ok: [localhost] => (item=None)
ok: [localhost]

TASK [roles/common/push-docker-images : Validate quay_registry information if it exists] ***
skipping: [localhost]

TASK [roles/common/push-docker-images : Set secure to bool] ********************
skipping: [localhost]

TASK [roles/common/push-docker-images : Get the quay_registry barbican secret if it's authenticated] ***
changed: [localhost]

TASK [roles/common/push-docker-images : Validate quay_registry secret] *********
skipping: [localhost]

TASK [roles/common/push-docker-images : set_fact] ******************************
ok: [localhost]

TASK [roles/common/push-docker-images : set_fact] ******************************
ok: [localhost]

TASK [roles/common/push-docker-images : set_fact] ******************************
ok: [localhost] => (item=None)
ok: [localhost] => (item=None)
ok: [localhost] => (item=None)
skipping: [localhost] => (item=None)
ok: [localhost] => (item=None)
ok: [localhost]

TASK [roles/common/push-docker-images : set_fact] ******************************
ok: [localhost]

TASK [roles/common/push-docker-images : Query the docker_registry] *************
changed: [localhost]

TASK [roles/common/push-docker-images : set_fact] ******************************
ok: [localhost]

TASK [roles/common/push-docker-images : set_fact] ******************************
ok: [localhost] => (item=None)
ok: [localhost] => (item=None)
ok: [localhost] => (item=None)
ok: [localhost]

TASK [roles/common/push-docker-images : Validate docker_registry information if it exists] ***
skipping: [localhost]

TASK [roles/common/push-docker-images : Set secure to bool] ********************
skipping: [localhost]

TASK [roles/common/push-docker-images : Get the docker_registry barbican secret if it's authenticated] ***
changed: [localhost]

TASK [roles/common/push-docker-images : Validate docker_registry secret] *******
skipping: [localhost]

TASK [roles/common/push-docker-images : set_fact] ******************************
ok: [localhost]

TASK [roles/common/push-docker-images : set_fact] ******************************
ok: [localhost]

TASK [roles/common/push-docker-images : set_fact] ******************************
ok: [localhost] => (item=None)
ok: [localhost] => (item=None)
ok: [localhost] => (item=None)
skipping: [localhost] => (item=None)
ok: [localhost] => (item=None)
ok: [localhost]

TASK [roles/common/push-docker-images : set_fact] ******************************
ok: [localhost]

TASK [roles/common/push-docker-images : Query the elastic_registry] ************
changed: [localhost]

TASK [roles/common/push-docker-images : set_fact] ******************************
ok: [localhost]

TASK [roles/common/push-docker-images : set_fact] ******************************
ok: [localhost] => (item=None)
ok: [localhost] => (item=None)
ok: [localhost] => (item=None)
ok: [localhost]

TASK [roles/common/push-docker-images : Validate elastic_registry information if it exists] ***
skipping: [localhost]

TASK [roles/common/push-docker-images : Set secure to bool] ********************
skipping: [localhost]

TASK [roles/common/push-docker-images : Get the elastic_registry barbican secret if it's authenticated] ***
changed: [localhost]

TASK [roles/common/push-docker-images : Validate elastic_registry secret] ******
skipping: [localhost]

TASK [roles/common/push-docker-images : set_fact] ******************************
ok: [localhost]

TASK [roles/common/push-docker-images : set_fact] ******************************
ok: [localhost]

TASK [roles/common/push-docker-images : set_fact] ******************************
ok: [localhost] => (item=None)
ok: [localhost] => (item=None)
ok: [localhost] => (item=None)
skipping: [localhost] => (item=None)
ok: [localhost] => (item=None)
ok: [localhost]

TASK [roles/common/push-docker-images : set_fact] ******************************
ok: [localhost]

TASK [roles/common/push-docker-images : Query the ghcr_registry] ***************
changed: [localhost]

TASK [roles/common/push-docker-images : set_fact] ******************************
ok: [localhost]

TASK [roles/common/push-docker-images : set_fact] ******************************
ok: [localhost] => (item=None)
ok: [localhost] => (item=None)
ok: [localhost] => (item=None)
ok: [localhost]

TASK [roles/common/push-docker-images : Validate ghcr_registry information if it exists] ***
skipping: [localhost]

TASK [roles/common/push-docker-images : Set secure to bool] ********************
skipping: [localhost]

TASK [roles/common/push-docker-images : Get the ghcr_registry barbican secret if it's authenticated] ***
changed: [localhost]

TASK [roles/common/push-docker-images : Validate ghcr_registry secret] *********
skipping: [localhost]

TASK [roles/common/push-docker-images : set_fact] ******************************
ok: [localhost]

TASK [roles/common/push-docker-images : set_fact] ******************************
ok: [localhost]

TASK [roles/common/push-docker-images : set_fact] ******************************
ok: [localhost] => (item=None)
ok: [localhost] => (item=None)
ok: [localhost] => (item=None)
skipping: [localhost] => (item=None)
ok: [localhost] => (item=None)
ok: [localhost]

TASK [roles/common/push-docker-images : set_fact] ******************************
ok: [localhost]

TASK [roles/common/push-docker-images : Get registry credentials if registry type is AWS ECR] ***
skipping: [localhost] => (item=None)
skipping: [localhost] => (item=None)
skipping: [localhost] => (item=None)
skipping: [localhost] => (item=None)
skipping: [localhost] => (item=None)
skipping: [localhost] => (item=None)
skipping: [localhost]

TASK [common/load-images-information : Set kubernetes long version] ************
ok: [localhost]

TASK [common/load-images-information : Get the list of kubernetes images] ******
changed: [localhost]

TASK [common/load-images-information : set_fact] *******************************
ok: [localhost]

TASK [common/load-images-information : Read in system images list] *************
ok: [localhost]

TASK [common/load-images-information : Check if additional image config file exists] ***
ok: [localhost]

TASK [common/load-images-information : Read in additional system images list(s) in localhost] ***
ok: [localhost]

TASK [common/load-images-information : Create a temporary file on remote] ******
skipping: [localhost]

TASK [common/load-images-information : Fetch the additional images config in case the playbook is executed remotely] ***
skipping: [localhost]

TASK [common/load-images-information : Read in additional system images list(s) fetched from remote] ***
skipping: [localhost]

TASK [common/load-images-information : Remove the temporary file on remote] ****
skipping: [localhost]

TASK [common/load-images-information : Remove override temp file on Ansible control host] ***
skipping: [localhost]

TASK [common/load-images-information : Categorize system images] ***************
ok: [localhost]

TASK [common/load-images-information : Append additional static images if provisioned] ***
ok: [localhost] => (item={'key': u'kube_rbac_proxy_img', 'value': u'gcr.io/kubebuilder/kube-rbac-proxy:v0.4.0'})
ok: [localhost] => (item={'key': u'deploy_manager_img', 'value': u'docker.io/wind-river/cloud-platform-deployment-manager:WRCP_21.12-wrs.4'})
ok: [localhost] => (item={'key': u'dm_monitor_img', 'value': u'docker.io/wind-river/dm-monitor:WRCP_21.05-v1.0.0'})

TASK [common/load-images-information : Append RVMC image for a DC system controller] ***
ok: [localhost]

TASK [common/load-images-information : Append additional static images for a DC system controller if provisioned] ***
ok: [localhost] => (item={'key': u'rbd_provisioner_img', 'value': u'quay.io/external_storage/rbd-provisioner:v2.1.1-k8s1.11'})
ok: [localhost] => (item={'key': u'ceph_config_helper_img', 'value': u'docker.io/starlingx/ceph-config-helper:v1.15.0'})

TASK [roles/common/push-docker-images : Set download images list] **************
skipping: [localhost]

TASK [roles/common/push-docker-images : Set download images list to static images (both general and security specific) if upgrading platform] ***
skipping: [localhost]

TASK [roles/common/push-docker-images : Set download images list to k8s network images if upgrading k8s networking] ***
skipping: [localhost]

TASK [roles/common/push-docker-images : Set download images list to kubernetes images if upgrading kubernetes] ***
skipping: [localhost]

TASK [roles/common/push-docker-images : Set download images list to netapp images if installing trident] ***
ok: [localhost]

TASK [roles/common/push-docker-images : set_fact] ******************************
ok: [localhost]

TASK [roles/common/push-docker-images : debug] *********************************
ok: [localhost] => {
    "download_images_list": [
        "docker.io/netapp/trident:21.04.1",
        "quay.io/k8scsi/csi-provisioner:v2.1.1",
        "quay.io/k8scsi/csi-attacher:v3.1.0",
        "quay.io/k8scsi/csi-resizer:v1.1.0",
        "quay.io/k8scsi/csi-node-driver-registrar:v2.1.0",
        "quay.io/k8scsi/csi-snapshotter:v3.0.3",
        "quay.io/k8scsi/snapshot-controller:v2.0.0-rc2"
    ]
}

TASK [roles/common/push-docker-images : Set registries information] ************
ok: [localhost] => (item={u'replaced_url': u'wsregistry.mtce.vzwops.com:443/vcp_far_edge_in_building_docker/625619392498.dkr.ecr.us-west-2.amazonaws.com/k8s.gcr.io', u'default_url': u'k8s.gcr.io'})
ok: [localhost] => (item={u'replaced_url': u'wsregistry.mtce.vzwops.com:443/vcp_far_edge_in_building_docker/625619392498.dkr.ecr.us-west-2.amazonaws.com/gcr.io', u'default_url': u'gcr.io'})
ok: [localhost] => (item={u'replaced_url': u'wsregistry.mtce.vzwops.com:443/vcp_far_edge_in_building_docker/625619392498.dkr.ecr.us-west-2.amazonaws.com/quay.io', u'default_url': u'quay.io'})
ok: [localhost] => (item={u'replaced_url': u'wsregistry.mtce.vzwops.com:443/vcp_far_edge_in_building_docker/625619392498.dkr.ecr.us-west-2.amazonaws.com/docker.io', u'default_url': u'docker.io'})
ok: [localhost] => (item={u'replaced_url': u'wsregistry.mtce.vzwops.com:443/vcp_far_edge_in_building_docker/625619392498.dkr.ecr.us-west-2.amazonaws.com/docker.elastic.co', u'default_url': u'docker.elastic.co'})
ok: [localhost] => (item={u'replaced_url': u'wsregistry.mtce.vzwops.com:443/vcp_far_edge_in_building_docker/625619392498.dkr.ecr.us-west-2.amazonaws.com/ghcr.io', u'default_url': u'ghcr.io'})

TASK [roles/common/push-docker-images : Log in k8s, gcr, quay, ghcr, docker registries if credentials exist] ***
changed: [localhost] => (item=None)
changed: [localhost] => (item=None)
changed: [localhost] => (item=None)
changed: [localhost] => (item=None)
changed: [localhost] => (item=None)
changed: [localhost]

TASK [roles/common/push-docker-images : Get local registry credentials] ********
changed: [localhost]

TASK [roles/common/push-docker-images : set_fact] ******************************
ok: [localhost]

TASK [roles/common/push-docker-images : set_fact] ******************************
ok: [localhost]

TASK [roles/common/push-docker-images : Push imported images to local registry] ***
skipping: [localhost]

TASK [roles/common/push-docker-images : set_fact] ******************************
skipping: [localhost]

TASK [roles/common/push-docker-images : debug] *********************************
skipping: [localhost]

TASK [roles/common/push-docker-images : debug] *********************************
ok: [localhost] => {
    "msg": [
        "Image is up to date for sha256:11f27747c1b6c7c6a30779bee14756c5ba50470fd1818588c07d39340fc9691f",
        "Image is up to date for sha256:8bbdcebae17939af19756da6e7a429aa61fcef42b2173605a24464363a6d1514",
        "Image is up to date for sha256:0b5dda75f10a364f3aa1d349ea09498c0dde44e23e1df14d1e519421d394b14b",
        "Image is up to date for sha256:a629116f045900baf2a2a2f5a9591f40b2d244ddbe2125f9b445701a8c4d83fd",
        "Image is up to date for sha256:78fec43cc85827a896969195328203bad5f1dd2eb23be55e10d479976a920177",
        "500 Server Error: Internal Server Error (\"manifest unknown: manifest unknown\")",
        "Image wsregistry.mtce.vzwops.com:443/vcp_far_edge_in_building_docker/625619392498.dkr.ecr.us-west-2.amazonaws.com/docker.io/netapp/trident:21.04.1 not found on local registry, attempt to download...",
        "Image download succeeded: wsregistry.mtce.vzwops.com:443/vcp_far_edge_in_building_docker/625619392498.dkr.ecr.us-west-2.amazonaws.com/docker.io/netapp/trident:21.04.1",
        "Image push succeeded: registry.local:9001/docker.io/netapp/trident:21.04.1",
        "Image wsregistry.mtce.vzwops.com:443/vcp_far_edge_in_building_docker/625619392498.dkr.ecr.us-west-2.amazonaws.com/docker.io/netapp/trident:21.04.1 download succeeded by containerd",
        "500 Server Error: Internal Server Error (\"manifest unknown: manifest unknown\")",
        "Image wsregistry.mtce.vzwops.com:443/vcp_far_edge_in_building_docker/625619392498.dkr.ecr.us-west-2.amazonaws.com/quay.io/k8scsi/csi-provisioner:v2.1.1 not found on local registry, attempt to download...",
        "Image download succeeded: wsregistry.mtce.vzwops.com:443/vcp_far_edge_in_building_docker/625619392498.dkr.ecr.us-west-2.amazonaws.com/quay.io/k8scsi/csi-provisioner:v2.1.1",
        "Image push succeeded: registry.local:9001/quay.io/k8scsi/csi-provisioner:v2.1.1",
        "Image wsregistry.mtce.vzwops.com:443/vcp_far_edge_in_building_docker/625619392498.dkr.ecr.us-west-2.amazonaws.com/quay.io/k8scsi/csi-provisioner:v2.1.1 download succeeded by containerd",
        "500 Server Error: Internal Server Error (\"manifest unknown: manifest unknown\")",
        "Image wsregistry.mtce.vzwops.com:443/vcp_far_edge_in_building_docker/625619392498.dkr.ecr.us-west-2.amazonaws.com/quay.io/k8scsi/csi-attacher:v3.1.0 not found on local registry, attempt to download...",
        "Image download succeeded: wsregistry.mtce.vzwops.com:443/vcp_far_edge_in_building_docker/625619392498.dkr.ecr.us-west-2.amazonaws.com/quay.io/k8scsi/csi-attacher:v3.1.0",
        "Image push succeeded: registry.local:9001/quay.io/k8scsi/csi-attacher:v3.1.0",
        "Image wsregistry.mtce.vzwops.com:443/vcp_far_edge_in_building_docker/625619392498.dkr.ecr.us-west-2.amazonaws.com/quay.io/k8scsi/csi-attacher:v3.1.0 download succeeded by containerd",
        "500 Server Error: Internal Server Error (\"manifest unknown: manifest unknown\")",
        "Image wsregistry.mtce.vzwops.com:443/vcp_far_edge_in_building_docker/625619392498.dkr.ecr.us-west-2.amazonaws.com/quay.io/k8scsi/csi-resizer:v1.1.0 not found on local registry, attempt to download...",
        "Image download succeeded: wsregistry.mtce.vzwops.com:443/vcp_far_edge_in_building_docker/625619392498.dkr.ecr.us-west-2.amazonaws.com/quay.io/k8scsi/csi-resizer:v1.1.0",
        "Image push succeeded: registry.local:9001/quay.io/k8scsi/csi-resizer:v1.1.0",
        "Image wsregistry.mtce.vzwops.com:443/vcp_far_edge_in_building_docker/625619392498.dkr.ecr.us-west-2.amazonaws.com/quay.io/k8scsi/csi-resizer:v1.1.0 download succeeded by containerd",
        "500 Server Error: Internal Server Error (\"manifest unknown: manifest unknown\")",
        "Image wsregistry.mtce.vzwops.com:443/vcp_far_edge_in_building_docker/625619392498.dkr.ecr.us-west-2.amazonaws.com/quay.io/k8scsi/csi-node-driver-registrar:v2.1.0 not found on local registry, attempt to download...",
        "Image download succeeded: wsregistry.mtce.vzwops.com:443/vcp_far_edge_in_building_docker/625619392498.dkr.ecr.us-west-2.amazonaws.com/quay.io/k8scsi/csi-node-driver-registrar:v2.1.0",
        "Image push succeeded: registry.local:9001/quay.io/k8scsi/csi-node-driver-registrar:v2.1.0",
        "Image wsregistry.mtce.vzwops.com:443/vcp_far_edge_in_building_docker/625619392498.dkr.ecr.us-west-2.amazonaws.com/quay.io/k8scsi/csi-node-driver-registrar:v2.1.0 download succeeded by containerd",
        "500 Server Error: Internal Server Error (\"manifest unknown: manifest unknown\")",
        "Image wsregistry.mtce.vzwops.com:443/vcp_far_edge_in_building_docker/625619392498.dkr.ecr.us-west-2.amazonaws.com/quay.io/k8scsi/csi-snapshotter:v3.0.3 not found on local registry, attempt to download...",
        "Image download succeeded: wsregistry.mtce.vzwops.com:443/vcp_far_edge_in_building_docker/625619392498.dkr.ecr.us-west-2.amazonaws.com/quay.io/k8scsi/csi-snapshotter:v3.0.3",
        "Image push succeeded: registry.local:9001/quay.ioImage is up to date for sha256:33308d4a9ea36d9019552e31c1ae8d43c461b1b3a0839152120b86cb5ab55945",
        "Image is up to date for sha256:d4553944fbf7b50f20eece0ec3f638202fdbe2a1a597af8c3f3823201cc695b3",
        "/k8scsi/csi-snapshotter:v3.0.3",
        "Image wsregistry.mtce.vzwops.com:443/vcp_far_edge_in_building_docker/625619392498.dkr.ecr.us-west-2.amazonaws.com/quay.io/k8scsi/csi-snapshotter:v3.0.3 download succeeded by containerd",
        "Image wsregistry.mtce.vzwops.com:443/vcp_far_edge_in_building_docker/625619392498.dkr.ecr.us-west-2.amazonaws.com/quay.io/k8scsi/snapshot-controller:v2.0.0-rc2 found on local registry",
        "All images downloaded and pushed to the local registry in 38.7185637951 seconds"
    ]
}

TASK [roles/common/push-docker-images : Log out of k8s, gcr, quay, ghcr docker registries if credentials exist] ***
ok: [localhost] => (item=None)
ok: [localhost] => (item=None)
ok: [localhost] => (item=None)
ok: [localhost] => (item=None)
ok: [localhost] => (item=None)
ok: [localhost]

TASK [roles/k8s-storage-backends/snapshot-controller : Ensures snapshot controller setup folder is present] ***
changed: [localhost]

TASK [roles/k8s-storage-backends/snapshot-controller : Ensures snapshot CRD setup directory is present] ***
changed: [localhost]

TASK [roles/k8s-storage-backends/snapshot-controller : Create snapshot-controller template files] ***
changed: [localhost] => (item=/usr/share/ansible/stx-ansible/playbooks/roles/k8s-storage-backends/snapshot-controller/templates/k8s-v1.18.1/volume-snapshot-controller/snapshot-controller-deployment.yaml.j2)
changed: [localhost] => (item=/usr/share/ansible/stx-ansible/playbooks/roles/k8s-storage-backends/snapshot-controller/templates/k8s-v1.18.1/volume-snapshot-controller/rbac-volume-snapshot-controller.yaml.j2)

TASK [roles/k8s-storage-backends/snapshot-controller : Copy snapshots CRD files] ***
changed: [localhost] => (item=/usr/share/ansible/stx-ansible/playbooks/roles/k8s-storage-backends/snapshot-controller/files/k8s-v1.18.1/crd/snapshot.storage.k8s.io_volumesnapshots.yaml)
changed: [localhost] => (item=/usr/share/ansible/stx-ansible/playbooks/roles/k8s-storage-backends/snapshot-controller/files/k8s-v1.18.1/crd/snapshot.storage.k8s.io_volumesnapshotclasses.yaml)
changed: [localhost] => (item=/usr/share/ansible/stx-ansible/playbooks/roles/k8s-storage-backends/snapshot-controller/files/k8s-v1.18.1/crd/snapshot.storage.k8s.io_volumesnapshotcontents.yaml)

TASK [roles/k8s-storage-backends/snapshot-controller : Add Snapshot CRDs] ******
changed: [localhost]

TASK [roles/k8s-storage-backends/snapshot-controller : Activate snapshot-controller service] ***
changed: [localhost]

TASK [roles/k8s-storage-backends/snapshot-controller : Wait for snapshot-controller service to be active] ***
changed: [localhost]

TASK [roles/k8s-storage-backends/netapp : Ensures trident setup folder is present] ***
changed: [localhost]

TASK [roles/k8s-storage-backends/netapp : Create trident template files] *******
changed: [localhost] => (item=/usr/share/ansible/stx-ansible/playbooks/roles/k8s-storage-backends/netapp/tasks/../templates/trident-deployment.yaml.j2)
changed: [localhost] => (item=/usr/share/ansible/stx-ansible/playbooks/roles/k8s-storage-backends/netapp/tasks/../templates/trident-clusterrolebinding.yaml.j2)
changed: [localhost] => (item=/usr/share/ansible/stx-ansible/playbooks/roles/k8s-storage-backends/netapp/tasks/../templates/trident-crds.yaml.j2)
changed: [localhost] => (item=/usr/share/ansible/stx-ansible/playbooks/roles/k8s-storage-backends/netapp/tasks/../templates/trident-service.yaml.j2)
changed: [localhost] => (item=/usr/share/ansible/stx-ansible/playbooks/roles/k8s-storage-backends/netapp/tasks/../templates/trident-serviceaccount.yaml.j2)
changed: [localhost] => (item=/usr/share/ansible/stx-ansible/playbooks/roles/k8s-storage-backends/netapp/tasks/../templates/trident-daemonset.yaml.j2)
changed: [localhost] => (item=/usr/share/ansible/stx-ansible/playbooks/roles/k8s-storage-backends/netapp/tasks/../templates/trident-podsecuritypolicy.yaml.j2)
changed: [localhost] => (item=/usr/share/ansible/stx-ansible/playbooks/roles/k8s-storage-backends/netapp/tasks/../templates/trident-namespace.yaml.j2)
changed: [localhost] => (item=/usr/share/ansible/stx-ansible/playbooks/roles/k8s-storage-backends/netapp/tasks/../templates/trident-clusterrole.yaml.j2)

TASK [roles/k8s-storage-backends/netapp : Check if trident is already installed] ***
skipping: [localhost]

TASK [roles/k8s-storage-backends/netapp : Uninstall trident services] **********
changed: [localhost]

TASK [roles/k8s-storage-backends/netapp : Create namespace for trident installer] ***
changed: [localhost]

TASK [roles/k8s-storage-backends/netapp : Fail if creating namespace fails] ****
skipping: [localhost]

TASK [roles/k8s-storage-backends/netapp : Fail if the docker registry secret name to be used differs from default name] ***
skipping: [localhost]

TASK [roles/k8s-storage-backends/netapp : Check if secret exists] **************
changed: [localhost]

TASK [roles/k8s-storage-backends/netapp : Create secret if it doesn't exist] ***
skipping: [localhost]

TASK [roles/k8s-storage-backends/netapp : Install trident services] ************

TASK [roles/k8s-storage-backends/netapp : Configure backends] ******************
included: /usr/share/ansible/stx-ansible/playbooks/roles/k8s-storage-backends/netapp/tasks/configure-backend.yml for localhost
included: /usr/share/ansible/stx-ansible/playbooks/roles/k8s-storage-backends/netapp/tasks/configure-backend.yml for localhost

TASK [roles/k8s-storage-backends/netapp : Set backend filename] ****************
ok: [localhost]

TASK [roles/k8s-storage-backends/netapp : Add NetApp backend] ******************
changed: [localhost] => (item=None)
changed: [localhost] => (item=None)
changed: [localhost]

TASK [roles/k8s-storage-backends/netapp : Cleanup backend file] ****************
changed: [localhost]

TASK [roles/k8s-storage-backends/netapp : Set backend filename] ****************
ok: [localhost]

TASK [roles/k8s-storage-backends/netapp : Add NetApp backend] ******************
changed: [localhost] => (item=None)
changed: [localhost] => (item=None)
changed: [localhost]

TASK [roles/k8s-storage-backends/netapp : Cleanup backend file] ****************
changed: [localhost]

TASK [roles/k8s-storage-backends/netapp : Configure kubernetes storage classes] ***
included: /usr/share/ansible/stx-ansible/playbooks/roles/k8s-storage-backends/netapp/tasks/configure-storage-classes.yml for localhost

TASK [roles/k8s-storage-backends/netapp : Set StorageClass filename] ***********
ok: [localhost]

TASK [roles/k8s-storage-backends/netapp : Set StorageClass headers] ************
ok: [localhost]

TASK [roles/k8s-storage-backends/netapp : Prepare StorageClass content] ********
ok: [localhost]

TASK [roles/k8s-storage-backends/netapp : Create storage-class.yaml] ***********
changed: [localhost]

TASK [roles/k8s-storage-backends/netapp : Remove StorageClass if it exists] ****
changed: [localhost]

TASK [roles/k8s-storage-backends/netapp : Create K8s StorageClass] *************
changed: [localhost]

TASK [roles/k8s-storage-backends/netapp : Configure kubernetes snapshot storage classes] ***
included: /usr/share/ansible/stx-ansible/playbooks/roles/k8s-storage-backends/netapp/tasks/configure-snapshot-storage-classes.yml for localhost

TASK [roles/k8s-storage-backends/netapp : Set VolumeSnapshotClass filename] ****
ok: [localhost]

TASK [roles/k8s-storage-backends/netapp : Set VolumeSnapshotClass headers] *****
ok: [localhost]

TASK [roles/k8s-storage-backends/netapp : Prepare VolumeSnapshotClass content] ***
ok: [localhost]

TASK [roles/k8s-storage-backends/netapp : Create snapshot-storage-class.yaml] ***
changed: [localhost]

TASK [roles/k8s-storage-backends/netapp : Remove VolumeSnapshotClass if it exists] ***
changed: [localhost]

TASK [roles/k8s-storage-backends/netapp : Create K8s VolumeSnapshotClass] ******
changed: [localhost]

TASK [roles/k8s-storage-backends/netapp : Clean staging folder] ****************
changed: [localhost]

PLAY RECAP *********************************************************************
localhost                  : ok=116  changed=41   unreachable=0    failed=0

[XXXXXX@controller-0 ~(keystone_admin)]$

[XXXXXX@controller-0 ~(keystone_admin)]$ rm -f localhost.yml
[XXXXXX@controller-0 ~(keystone_admin)]$ kubectl wait --for condition=Ready --timeout 120s pods --all --namespace trident
pod/trident-csi-5f44c44567-8qvvv condition met
pod/trident-csi-kvx4p condition met
pod/trident-csi-t8w5m condition met
pod/trident-csi-tg6jv condition met
[XXXXXX@controller-0 ~(keystone_admin)]$

controller-0:~$ source /etc/platform/openrc
[XXXXXX@controller-0 ~(keystone_admin)]$ kubectl get pods --namespace trident
NAME                           READY   STATUS    RESTARTS   AGE
trident-csi-5f44c44567-8qvvv   5/5     Running   2          67m
trident-csi-kvx4p              2/2     Running   0          67m
trident-csi-t8w5m              2/2     Running   0          67m
trident-csi-tg6jv              2/2     Running   0          67m
[XXXXXX@controller-0 ~(keystone_admin)]$

[XXXXXX@controller-0 ~(keystone_admin)]$ tridentctl version --namespace trident
+----------------+----------------+
| SERVER VERSION | CLIENT VERSION |
+----------------+----------------+
| 21.04.1        | 21.04.1        |
+----------------+----------------+
[XXXXXX@controller-0 ~(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./sanity_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook --inventory controller --extra-vars "scenario=after" \
> --ask-pass --ask-become-pass --user XXXXXX sanity.yaml 0</dev/null
SSH password:
XXXXXX password[defaults to SSH password]:

PLAY [all] *********************************************************************

TASK [Gathering Facts] *********************************************************
ok: [localhost]

TASK [Read in parameter file] **************************************************
ok: [localhost]

TASK [set expected Fortville firmware version] *********************************
ok: [localhost]

TASK [set expected N3000 firmware version] *************************************
ok: [localhost]

TASK [create directory /home/XXXXXX/sanity] **********************************
changed: [localhost -> localhost]

TASK [delete existing file /home/XXXXXX/sanity/output_list] ******************
ok: [localhost -> localhost]

TASK [create file /home/XXXXXX/sanity/output_list] ***************************
changed: [localhost -> localhost]

TASK [get host patch status] ***************************************************
changed: [localhost]

TASK [validate host patch status] **********************************************
skipping: [localhost]

TASK [get host status] *********************************************************
changed: [localhost]

TASK [validate host status] ****************************************************
skipping: [localhost]

TASK [get current alarms] ******************************************************
changed: [localhost]

TASK [validate current alarms] *************************************************
skipping: [localhost]

TASK [get vim status] **********************************************************
changed: [localhost]

TASK [validate vim status] *****************************************************
skipping: [localhost]

TASK [calculate / partition expected usage] ************************************
changed: [localhost]

TASK [validate / partition free space] *****************************************
skipping: [localhost]

TASK [validate /opt/dc-vault partition free space] *****************************
skipping: [localhost]

TASK [identify N3000 NICs] *****************************************************
changed: [localhost]

TASK [get N3000 NICs firmware version] *****************************************

TASK [validate N3000 NICs firmware version] ************************************

TASK [get N3000 NICs MAC] ******************************************************

TASK [validate N3000 NICs MACs] ************************************************

TASK [identify Fortville NICs] *************************************************
changed: [localhost]

TASK [get Fortville NICs firmware version] *************************************
changed: [localhost] => (item=ens2f0)
changed: [localhost] => (item=ens2f1)
changed: [localhost] => (item=ens3f0)
changed: [localhost] => (item=ens3f1)

TASK [validate Fortville NICs firmware version] ********************************
skipping: [localhost] => (item=ens2f0)
skipping: [localhost] => (item=ens2f1)
skipping: [localhost] => (item=ens3f0)
skipping: [localhost] => (item=ens3f1)

TASK [get Fortville NICs MAC] **************************************************
changed: [localhost] => (item=ens2f0)
changed: [localhost] => (item=ens2f1)
changed: [localhost] => (item=ens3f0)
changed: [localhost] => (item=ens3f1)

TASK [validate Fortville NICs MACs] ********************************************
skipping: [localhost] => (item=ens2f0)
skipping: [localhost] => (item=ens2f1)
skipping: [localhost] => (item=ens3f0)
skipping: [localhost] => (item=ens3f1)

TASK [identify accelerators] ***************************************************
changed: [localhost]

TASK [retrieve device information] *********************************************

TASK [output device show information] ******************************************

TASK [retrieve device information] *********************************************

TASK [output field information] ************************************************

TASK [validate sriov_numvfs for Mount Bryce] ***********************************

TASK [validate driver and sriov_vf_driver fields] ******************************

TASK [validate extra_info field] ***********************************************

TASK [get pod status] **********************************************************
changed: [localhost]

TASK [validate pod status] *****************************************************
skipping: [localhost]

TASK [get system applications] *************************************************
changed: [localhost]

TASK [validate system applications] ********************************************
skipping: [localhost] => (item=cert-manager:21.12-28)
skipping: [localhost] => (item=nginx-ingress-controller:21.12-18)
skipping: [localhost] => (item=oidc-auth-apps:21.12-61)

PLAY RECAP *********************************************************************
localhost                  : ok=19   changed=14   unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ cat /home/XXXXXX/sanity/output_list
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$




```


### mop 2 


```log

[XXXXXX@controller-0 ~(keystone_admin)]$ cd /opt/platform-backup/upgrade/wrcp-21.12-upgrade
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ app_dir=/usr/local/share/applications
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ dcmanager subcloud-deploy upload \
> --deploy-playbook ${app_dir}/playbooks/wind-river-cloud-platform-deployment-manager.yaml \
> --deploy-overrides ${app_dir}/overrides/wind-river-cloud-platform-deployment-manager-\
> overrides-subcloud.yaml \
> --deploy-chart ${app_dir}/helm/wind-river-cloud-platform-deployment-manager-2.0.8-4.tgz \
> --prestage-images prestage_images.txt
+------------------+--------------------------------------------------------------------------------------------------------------+
| Field            | Value                                                                                                        |
+------------------+--------------------------------------------------------------------------------------------------------------+
| deploy_playbook  | /usr/local/share/applications/playbooks/wind-river-cloud-platform-deployment-manager.yaml                    |
| deploy_overrides | /usr/local/share/applications/overrides/wind-river-cloud-platform-deployment-manager-overrides-subcloud.yaml |
| deploy_chart     | /usr/local/share/applications/helm/wind-river-cloud-platform-deployment-manager-2.0.8-4.tgz                  |
| prestage_images  | prestage_images.txt                                                                                          |
+------------------+--------------------------------------------------------------------------------------------------------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./sanity_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook --inventory controller --extra-vars "scenario=after" \
> --ask-pass --ask-become-pass --user XXXXXX sanity.yaml 0</dev/null
SSH password:
XXXXXX password[defaults to SSH password]:

PLAY [all] *********************************************************************

TASK [Gathering Facts] *********************************************************
ok: [localhost]

TASK [Read in parameter file] **************************************************
ok: [localhost]

TASK [set expected Fortville firmware version] *********************************
ok: [localhost]

TASK [set expected N3000 firmware version] *************************************
ok: [localhost]

TASK [create directory /home/XXXXXX/sanity] **********************************
changed: [localhost -> localhost]

TASK [delete existing file /home/XXXXXX/sanity/output_list] ******************
ok: [localhost -> localhost]

TASK [create file /home/XXXXXX/sanity/output_list] ***************************
changed: [localhost -> localhost]

TASK [get host patch status] ***************************************************
changed: [localhost]

TASK [validate host patch status] **********************************************
skipping: [localhost]

TASK [get host status] *********************************************************
changed: [localhost]

TASK [validate host status] ****************************************************
skipping: [localhost]

TASK [get current alarms] ******************************************************
changed: [localhost]

TASK [validate current alarms] *************************************************
skipping: [localhost]

TASK [get vim status] **********************************************************
changed: [localhost]

TASK [validate vim status] *****************************************************
skipping: [localhost]

TASK [calculate / partition expected usage] ************************************
changed: [localhost]

TASK [validate / partition free space] *****************************************
skipping: [localhost]

TASK [validate /opt/dc-vault partition free space] *****************************
skipping: [localhost]

TASK [identify N3000 NICs] *****************************************************
changed: [localhost]

TASK [get N3000 NICs firmware version] *****************************************

TASK [validate N3000 NICs firmware version] ************************************

TASK [get N3000 NICs MAC] ******************************************************

TASK [validate N3000 NICs MACs] ************************************************

TASK [identify Fortville NICs] *************************************************
changed: [localhost]

TASK [get Fortville NICs firmware version] *************************************
changed: [localhost] => (item=ens2f0)
changed: [localhost] => (item=ens2f1)
changed: [localhost] => (item=ens3f0)
changed: [localhost] => (item=ens3f1)

TASK [validate Fortville NICs firmware version] ********************************
skipping: [localhost] => (item=ens2f0)
skipping: [localhost] => (item=ens2f1)
skipping: [localhost] => (item=ens3f0)
skipping: [localhost] => (item=ens3f1)

TASK [get Fortville NICs MAC] **************************************************
changed: [localhost] => (item=ens2f0)
changed: [localhost] => (item=ens2f1)
changed: [localhost] => (item=ens3f0)
changed: [localhost] => (item=ens3f1)

TASK [validate Fortville NICs MACs] ********************************************
skipping: [localhost] => (item=ens2f0)
skipping: [localhost] => (item=ens2f1)
skipping: [localhost] => (item=ens3f0)
skipping: [localhost] => (item=ens3f1)

TASK [identify accelerators] ***************************************************
changed: [localhost]

TASK [retrieve device information] *********************************************

TASK [output device show information] ******************************************

TASK [retrieve device information] *********************************************

TASK [output field information] ************************************************

TASK [validate sriov_numvfs for Mount Bryce] ***********************************

TASK [validate driver and sriov_vf_driver fields] ******************************

TASK [validate extra_info field] ***********************************************

TASK [get pod status] **********************************************************
changed: [localhost]

TASK [validate pod status] *****************************************************
skipping: [localhost]

TASK [get system applications] *************************************************
changed: [localhost]

TASK [validate system applications] ********************************************
skipping: [localhost] => (item=cert-manager:21.12-28)
skipping: [localhost] => (item=nginx-ingress-controller:21.12-18)
skipping: [localhost] => (item=oidc-auth-apps:21.12-61)

PLAY RECAP *********************************************************************
localhost                  : ok=19   changed=14   unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ cat /home/XXXXXX/sanity/output_list
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ system --os-region-name SystemController load-delete \
> $(system load-list | grep "imported" | awk -F \| '{ print $2 }')
Deleted load: load 1
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ cd /opt/platform-backup/upgrade/wrcp-21.12-upgrade
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ sudo show-certs.sh | grep -E '^\s+Residual Time'
Password:
XXXXXX, try again.
Password:
	 XXXXXX Time	:  385d
	 Residual Time	:  348d
	 Residual Time	:  196d
	 Residual Time	:  2597d
	 Residual Time	:  4294d
	 Residual Time	:  2598d
	 Residual Time	:  1808d
	 Residual Time	:  163d
	 Residual Time	:  3649d
	 Residual Time	:  365d
	 Residual Time	:  365d
	 Residual Time	:  365d
	 Residual Time	:  351d
	 Residual Time	:  4294d
	 Residual Time	:  4294d
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ for s in $(echo dcmanager sw-manager); do
> for t in $(echo upgrade patch fw-update kube-upgrade); do
> $s $t-strategy delete
> done
> done
Not found
ERROR (app) Unable to delete sw update strategy
Not found
ERROR (app) Unable to delete sw update strategy
Not found
ERROR (app) Unable to delete sw update strategy
Not found
ERROR (app) Unable to delete sw update strategy
Strategy delete failed
Strategy delete failed
Strategy delete failed
Strategy delete failed
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ echo -e '[system-controller]\nlocalhost' > controller
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./sanity_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook --inventory controller --extra-vars "scenario=after" \
> --ask-pass --ask-become-pass --user XXXXXX \
> sanity.yaml 0</dev/null
SSH password:
XXXXXX password[defaults to SSH password]:

PLAY [all] *********************************************************************

TASK [Gathering Facts] *********************************************************
ok: [localhost]

TASK [Read in parameter file] **************************************************
ok: [localhost]

TASK [set expected Fortville firmware version] *********************************
ok: [localhost]

TASK [set expected N3000 firmware version] *************************************
ok: [localhost]

TASK [create directory /home/XXXXXX/sanity] **********************************
ok: [localhost -> localhost]

TASK [delete existing file /home/XXXXXX/sanity/output_list] ******************
changed: [localhost -> localhost]

TASK [create file /home/XXXXXX/sanity/output_list] ***************************
changed: [localhost -> localhost]

TASK [get host patch status] ***************************************************
changed: [localhost]

TASK [validate host patch status] **********************************************
skipping: [localhost]

TASK [get host status] *********************************************************
changed: [localhost]

TASK [validate host status] ****************************************************
skipping: [localhost]

TASK [get current alarms] ******************************************************
changed: [localhost]

TASK [validate current alarms] *************************************************
skipping: [localhost]

TASK [get vim status] **********************************************************
changed: [localhost]

TASK [validate vim status] *****************************************************
skipping: [localhost]

TASK [calculate / partition expected usage] ************************************
changed: [localhost]

TASK [validate / partition free space] *****************************************
skipping: [localhost]

TASK [validate /opt/dc-vault partition free space] *****************************
skipping: [localhost]

TASK [identify N3000 NICs] *****************************************************
changed: [localhost]

TASK [get N3000 NICs firmware version] *****************************************

TASK [validate N3000 NICs firmware version] ************************************

TASK [get N3000 NICs MAC] ******************************************************

TASK [validate N3000 NICs MACs] ************************************************

TASK [identify Fortville NICs] *************************************************
changed: [localhost]

TASK [get Fortville NICs firmware version] *************************************
changed: [localhost] => (item=ens2f0)
changed: [localhost] => (item=ens2f1)
changed: [localhost] => (item=ens3f0)
changed: [localhost] => (item=ens3f1)

TASK [validate Fortville NICs firmware version] ********************************
skipping: [localhost] => (item=ens2f0)
skipping: [localhost] => (item=ens2f1)
skipping: [localhost] => (item=ens3f0)
skipping: [localhost] => (item=ens3f1)

TASK [get Fortville NICs MAC] **************************************************
changed: [localhost] => (item=ens2f0)
changed: [localhost] => (item=ens2f1)
changed: [localhost] => (item=ens3f0)
changed: [localhost] => (item=ens3f1)

TASK [validate Fortville NICs MACs] ********************************************
skipping: [localhost] => (item=ens2f0)
skipping: [localhost] => (item=ens2f1)
skipping: [localhost] => (item=ens3f0)
skipping: [localhost] => (item=ens3f1)

TASK [identify accelerators] ***************************************************
changed: [localhost]

TASK [retrieve device information] *********************************************

TASK [output device show information] ******************************************

TASK [retrieve device information] *********************************************

TASK [output field information] ************************************************

TASK [validate sriov_numvfs for Mount Bryce] ***********************************

TASK [validate driver and sriov_vf_driver fields] ******************************

TASK [validate extra_info field] ***********************************************

TASK [get pod status] **********************************************************
changed: [localhost]

TASK [validate pod status] *****************************************************
skipping: [localhost]

TASK [get system applications] *************************************************
changed: [localhost]

TASK [validate system applications] ********************************************
skipping: [localhost] => (item=cert-manager:21.12-28)
skipping: [localhost] => (item=nginx-ingress-controller:21.12-18)
skipping: [localhost] => (item=oidc-auth-apps:21.12-61)

PLAY RECAP *********************************************************************
localhost                  : ok=19   changed=14   unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ cat /home/XXXXXX/sanity/output_list
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
[XXXXXX@controller-0 ~(keystone_admin)]$ system kube-version-list | awk -F \| '$4 ~ / active / { gsub(/ /,"",$2);print $2 }'
v1.18.1
[XXXXXX@controller-0 ~(keystone_admin)]$
controller-0:~$ source /etc/platform/openrc
[XXXXXX@controller-0 ~(keystone_admin)]$ system kube-version-list | awk -F \| '$4 ~ / active / { gsub(/ /,"",$2);print $2 }'
v1.18.1
[XXXXXX@controller-0 ~(keystone_admin)]$ system health-query-kube-upgrade
System Health:
All hosts are provisioned: [OK]
All hosts are unlocked/enabled: [OK]
All hosts have current configurations: [OK]
All hosts are patch current: [OK]
No alarms: [Fail]
[2] alarms found, [0] of which are management affecting and [0] are certificate expiration alarms. Use "fm alarm-list" for details
All kubernetes nodes are ready: [OK]
All kubernetes control plane pods are ready: [OK]
Armada pods: [OK]
All kubernetes applications are in a valid state: [OK]

[XXXXXX@controller-0 ~(keystone_admin)]$ fm alarm-list --nowrap --mgmt_affecting | awk -F \| '$6 ~ / True / { print $0 }'
[XXXXXX@controller-0 ~(keystone_admin)]$ available=$(system kube-version-list | awk -F \| '$4 ~ / available / { print $2 }')

[XXXXXX@controller-0 ~(keystone_admin)]$ echo ${available}
v1.19.13
[XXXXXX@controller-0 ~(keystone_admin)]$ sw-manager kube-upgrade-strategy create --to-version ${available} --alarm-restrictions relaxed
Strategy Kubernetes Upgrade Strategy:
  strategy-uuid:                          6b468fa6-0a45-48c6-903a-49d2560750c5
  controller-apply-type:                  serial
  storage-apply-type:                     serial
  worker-apply-type:                      serial
  default-instance-action:                stop-start
  alarm-restrictions:                     relaxed
  current-phase:                          build
  current-phase-completion:               0%
  state:                                  building
  inprogress:                             true
[XXXXXX@controller-0 ~(keystone_admin)]$
Every 2.0s: sw-manager kube-upgrade-strategy show                                                                                         Tue Sep 12 04:14:09 2023

Strategy Kubernetes Upgrade Strategy:
  strategy-uuid:                          6b468fa6-0a45-48c6-903a-49d2560750c5
  controller-apply-type:                  serial
  storage-apply-type:                     serial
  worker-apply-type:                      serial
  default-instance-action:                stop-start
  alarm-restrictions:                     relaxed
  current-phase:                          build
  current-phase-completion:               100%
  state:                                  ready-to-apply
  build-result:                           success
  build-reason:



[XXXXXX@controller-0 ~(keystone_admin)]$ sw-manager kube-upgrade-strategy apply
Strategy Kubernetes Upgrade Strategy:
  strategy-uuid:                          6b468fa6-0a45-48c6-903a-49d2560750c5
  controller-apply-type:                  serial
  storage-apply-type:                     serial
  worker-apply-type:                      serial
  default-instance-action:                stop-start
  alarm-restrictions:                     relaxed
  current-phase:                          apply
  current-phase-completion:               0%
  state:                                  applying
  inprogress:                             true
[XXXXXX@controller-0 ~(keystone_admin)]$

Every 2.0s: sw-manager kube-upgrade-strategy show                                                                                         Tue Sep 12 16:04:02 2023

Strategy Kubernetes Upgrade Strategy:
  strategy-uuid:                          6b468fa6-0a45-48c6-903a-49d2560750c5
  controller-apply-type:                  serial
  storage-apply-type:                     serial
  worker-apply-type:                      serial
  default-instance-action:                stop-start
  alarm-restrictions:                     relaxed
  current-phase:                          apply
  current-phase-completion:               100%
  state:                                  applied
  apply-result:                           success
  apply-reason:


controller-1:~$ source /etc/platform/openrc
[XXXXXX@controller-1 ~(keystone_admin)]$ sw-manager kube-upgrade-strategy delete
Strategy deleted
[XXXXXX@controller-1 ~(keystone_admin)]$ system application-apply cert-manager
+---------------+----------------------------------+
| Property      | Value                            |
+---------------+----------------------------------+
| active        | True                             |
| app_version   | 21.12-28                         |
| created_at    | 2023-09-12T01:10:57.543560+00:00 |
| manifest_file | certmanager-manifest.yaml        |
| manifest_name | cert-manager-manifest            |
| name          | cert-manager                     |
| progress      | None                             |
| status        | applying                         |
| updated_at    | 2023-09-12T05:00:32.553008+00:00 |
+---------------+----------------------------------+
Please use 'system application-list' or 'system application-show cert-manager' to view the current progress.
[XXXXXX@controller-1 ~(keystone_admin)]$ system application-apply oidc-auth-apps
+---------------+----------------------------------+
| Property      | Value                            |
+---------------+----------------------------------+
| active        | True                             |
| app_version   | 21.12-61                         |
| created_at    | 2023-09-12T01:15:42.559240+00:00 |
| manifest_file | manifest.yaml                    |
| manifest_name | oidc-auth-manifest               |
| name          | oidc-auth-apps                   |
| progress      | None                             |
| status        | applying                         |
| updated_at    | 2023-09-12T05:01:35.639543+00:00 |
+---------------+----------------------------------+
Please use 'system application-list' or 'system application-show oidc-auth-apps' to view the current progress.
[XXXXXX@controller-1 ~(keystone_admin)]$ watch 'system application-list --nowrap | grep -E "cert-manager|oidc-auth-apps"'
[XXXXXX@controller-1 ~(keystone_admin)]$ kubectl --kubeconfig=/etc/kubernetes/admin.conf get pods -A | sed '1d' | \
> grep -E -v 'Running|Complete|ContainerCreating'
[XXXXXX@controller-1 ~(keystone_admin)]$ system kube-host-upgrade-list
+----+--------------+-------------+----------------+-----------------------+-----------------+--------+
| id | hostname     | personality | target_version | control_plane_version | kubelet_version | status |
+----+--------------+-------------+----------------+-----------------------+-----------------+--------+
| 1  | controller-0 | controller  | v1.19.13       | v1.19.13              | v1.19.13        | None   |
| 2  | controller-1 | controller  | v1.19.13       | v1.19.13              | v1.19.13        | None   |
| 3  | worker-0     | worker      | v1.19.13       | N/A                   | v1.19.13        | None   |
+----+--------------+-------------+----------------+-----------------------+-----------------+--------+
[XXXXXX@controller-1 ~(keystone_admin)]$
[XXXXXX@controller-1 ~(keystone_admin)]$ [ "$(hostname)" == "controller-1" ] && system host-swact controller-1 && exit
+-----------------------+-------------------------------------------------+
| Property              | Value                                           |
+-----------------------+-------------------------------------------------+
| action                | none                                            |
| administrative        | unlocked                                        |
| availability          | available                                       |
| bm_ip                 | 2607:f160:a:d02e:cd:fe0::8001                   |
| bm_type               | redfish                                         |
| bm_username           | OSPctl                                          |
| boot_device           | /dev/disk/by-path/pci-0000:5c:00.0-scsi-0:1:0:0 |
| capabilities          | {}                                              |
| clock_synchronization | ntp                                             |
| config_applied        | 2a900759-9a79-4368-83d3-b4a865cc03e1            |
| config_status         | None                                            |
| config_target         | 2a900759-9a79-4368-83d3-b4a865cc03e1            |
| console               | ttyS0,115200                                    |
| created_at            | 2023-08-26T05:19:18.631627+00:00                |
| device_image_update   | None                                            |
| hostname              | controller-1                                    |
| id                    | 2                                               |
| install_output        | text                                            |
| install_state         | completed                                       |
| install_state_info    | None                                            |
| inv_state             | inventoried                                     |
| invprovision          | provisioned                                     |
| location              | {}                                              |
| mgmt_ip               | 2607:f160:0:3042:cd:290:0:12                    |
| mgmt_mac              | 48:df:37:bb:1f:f8                               |
| operational           | enabled                                         |
| personality           | controller                                      |
| reboot_needed         | False                                           |
| reserved              | False                                           |
| rootfs_device         | /dev/disk/by-path/pci-0000:5c:00.0-scsi-0:1:0:0 |
| serialid              | None                                            |
| software_load         | 21.12                                           |
| task                  | Swacting                                        |
| tboot                 | false                                           |
| ttys_dcd              | None                                            |
| updated_at            | 2023-09-12T16:04:32.190128+00:00                |
| uptime                | 41523                                           |
| uuid                  | 5a47ec4b-6652-4cf4-9333-cd0eba25148c            |
| vim_progress_status   | services-enabled                                |
+-----------------------+-------------------------------------------------+
logout
Connection to 2607:f160:0:3043:cd:290:0:10 closed.
[XXXXXX@vcpe-jumpserver ~]$
[XXXXXX@controller-0 ~(keystone_admin)]$ cd /opt/platform-backup/upgrade/wrcp-21.12-upgrade
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./apply-kubelet-config_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook apply-kubelet-config.yaml 0</dev/null

PLAY [all] *********************************************************************

TASK [Remove kubelet-config settings for old versions] *************************
changed: [localhost]

TASK [Reapply kubelet-config settings] *****************************************
changed: [localhost]

TASK [Wait for kubelet-config settings to be applied] **************************
FAILED - RETRYING: Wait for kubelet-config settings to be applied (10 retries left).
changed: [localhost]

TASK [Output kubelet-config info] **********************************************
ok: [localhost] => {
    "msg": [
        "evictionHard:",
        "  imagefs.available: 2Gi",
        "  memory.available: 100Mi",
        "  nodefs.available: 10%",
        "  nodefs.inodesFree: 5%",
        "imageGCHighThresholdPercent: 79",
        "imageGCLowThresholdPercent: 75",
        "    imageGCLowThresholdPercent: 75",
        "    imageGCHighThresholdPercent: 79",
        "    evictionHard:",
        "      imagefs.available: 2Gi",
        "      memory.available: 100Mi",
        "      nodefs.inodesFree: 5%",
        "      nodefs.available: 10%"
    ]
}

PLAY RECAP *********************************************************************
localhost                  : ok=4    changed=3    unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ sleep 120
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ system kube-version-list | awk -F \| '$4 ~ / active / { gsub(/ /,"",$2);print $2 }'
v1.19.13
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ system health-query-kube-upgrade
System Health:
All hosts are provisioned: [OK]
All hosts are unlocked/enabled: [OK]
All hosts have current configurations: [OK]
All hosts are patch current: [OK]
No alarms: [Fail]
[9] alarms found, [0] of which are management affecting and [0] are certificate expiration alarms. Use "fm alarm-list" for details
All kubernetes nodes are ready: [OK]
All kubernetes control plane pods are ready: [OK]
Armada pods: [OK]
All kubernetes applications are in a valid state: [OK]

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ fm alarm-list --nowrap --mgmt_affecting | awk -F \| '$6 ~ / True / { print $0 }'
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ available=$(system kube-version-list | awk -F \| '$4 ~ / available / { print $2 }')

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ echo ${available}
v1.20.9
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ sw-manager kube-upgrade-strategy create --to-version ${available} --alarm-restrictions relaxed
Strategy Kubernetes Upgrade Strategy:
  strategy-uuid:                          02f32e02-4e1e-41b9-b508-7d058d6621fe
  controller-apply-type:                  serial
  storage-apply-type:                     serial
  worker-apply-type:                      serial
  default-instance-action:                stop-start
  alarm-restrictions:                     relaxed
  current-phase:                          build
  current-phase-completion:               0%
  state:                                  building
  inprogress:                             true
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

watch sw-manager kube-upgrade-strategy show

Every 2.0s: sw-manager kube-upgrade-strategy show                                                                                         Tue Sep 12 16:21:25 2023

Strategy Kubernetes Upgrade Strategy:
  strategy-uuid:                          02f32e02-4e1e-41b9-b508-7d058d6621fe
  controller-apply-type:                  serial
  storage-apply-type:                     serial
  worker-apply-type:                      serial
  default-instance-action:                stop-start
  alarm-restrictions:                     relaxed
  current-phase:                          build
  current-phase-completion:               100%
  state:                                  ready-to-apply
  build-result:                           success
  build-reason:

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ sw-manager kube-upgrade-strategy apply
Strategy Kubernetes Upgrade Strategy:
  strategy-uuid:                          02f32e02-4e1e-41b9-b508-7d058d6621fe
  controller-apply-type:                  serial
  storage-apply-type:                     serial
  worker-apply-type:                      serial
  default-instance-action:                stop-start
  alarm-restrictions:                     relaxed
  current-phase:                          apply
  current-phase-completion:               0%
  state:                                  applying
  inprogress:                             true
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
Every 2.0s: sw-manager kube-upgrade-strategy show                                                                                         Tue Sep 12 16:22:21 2023

Strategy Kubernetes Upgrade Strategy:
  strategy-uuid:                          02f32e02-4e1e-41b9-b508-7d058d6621fe
  controller-apply-type:                  serial
  storage-apply-type:                     serial
  worker-apply-type:                      serial
  default-instance-action:                stop-start
  alarm-restrictions:                     relaxed
  current-phase:                          apply
  current-phase-completion:               0%
  state:                                  applying
  inprogress:                             true


Every 2.0s: sw-manager kube-upgrade-strategy show                                                                                         Tue Sep 12 17:02:04 2023

Strategy Kubernetes Upgrade Strategy:
  strategy-uuid:                          02f32e02-4e1e-41b9-b508-7d058d6621fe
  controller-apply-type:                  serial
  storage-apply-type:                     serial
  worker-apply-type:                      serial
  default-instance-action:                stop-start
  alarm-restrictions:                     relaxed
  current-phase:                          apply
  current-phase-completion:               85%
  state:                                  applying
  inprogress:                             true


Every 2.0s: sw-manager kube-upgrade-strategy show                                                                                         Tue Sep 12 17:08:44 2023

Strategy Kubernetes Upgrade Strategy:
  strategy-uuid:                          02f32e02-4e1e-41b9-b508-7d058d6621fe
  controller-apply-type:                  serial
  storage-apply-type:                     serial
  worker-apply-type:                      serial
  default-instance-action:                stop-start
  alarm-restrictions:                     relaxed
  current-phase:                          apply
  current-phase-completion:               100%
  state:                                  applied
  apply-result:                           success
  apply-reason:

  | progress      | None                             |
[XXXXXX@controller-1 ~(keystone_admin)]$ watch sw-manager kube-upgrade-strategy show
[XXXXXX@controller-1 ~(keystone_admin)]$ sw-manager kube-upgrade-strategy delete
Strategy deleted
[XXXXXX@controller-1 ~(keystone_admin)]$ system application-apply cert-manager
+---------------+----------------------------------+
| Property      | Value                            |
+---------------+----------------------------------+
| active        | True                             |
| app_version   | 21.12-28                         |
| created_at    | 2023-09-12T01:10:57.543560+00:00 |
| manifest_file | certmanager-manifest.yaml        |
| manifest_name | cert-manager-manifest            |
| name          | cert-manager                     |
| progress      | None                             |
| status        | applying                         |
| updated_at    | 2023-09-12T17:06:53.049258+00:00 |
+---------------+----------------------------------+
Please use 'system application-list' or 'system application-show cert-manager' to view the current progress.
[XXXXXX@controller-1 ~(keystone_admin)]$ system application-apply oidc-auth-apps
+---------------+----------------------------------+
| Property      | Value                            |
+---------------+----------------------------------+
| active        | True                             |
| app_version   | 21.12-61                         |
| created_at    | 2023-09-12T01:15:42.559240+00:00 |
| manifest_file | manifest.yaml                    |
| manifest_name | oidc-auth-manifest               |
| name          | oidc-auth-apps                   |
| progress      | None                             |
| status        | applying                         |
| updated_at    | 2023-09-12T17:07:53.509566+00:00 |
+---------------+----------------------------------+
Please use 'system application-list' or 'system application-show oidc-auth-apps' to view the current progress.
[XXXXXX@controller-1 ~(keystone_admin)]$ watch 'system application-list --nowrap | grep -E "cert-manager|oidc-auth-apps"'
[XXXXXX@controller-1 ~(keystone_admin)]$





Every 2.0s: system application-list --nowrap | grep -E "cert-manager|oidc-auth-apps"                                                      Tue Sep 12 17:09:46 2023

| cert-manager             | 21.12-28 | cert-manager-manifest             | certmanager-manifest.yaml              | applied  | completed
                                      |
| oidc-auth-apps           | 21.12-61 | oidc-auth-manifest                | manifest.yaml                          | applied  | completed
                                      |




[XXXXXX@controller-1 ~(keystone_admin)]$ kubectl --kubeconfig=/etc/kubernetes/admin.conf get pods -A | sed '1d' | \
> grep -E -v 'Running|Complete|ContainerCreating'
[XXXXXX@controller-1 ~(keystone_admin)]$
[XXXXXX@controller-1 ~(keystone_admin)]$ [ "$(hostname)" == "controller-1" ] && system host-swact controller-1 && exit
+-----------------------+-------------------------------------------------+
| Property              | Value                                           |
+-----------------------+-------------------------------------------------+
| action                | none                                            |
| administrative        | unlocked                                        |
| availability          | available                                       |
| bm_ip                 | 2607:f160:a:d02e:cd:fe0::8001                   |
| bm_type               | redfish                                         |
| bm_username           | OSPctl                                          |
| boot_device           | /dev/disk/by-path/pci-0000:5c:00.0-scsi-0:1:0:0 |
| capabilities          | {}                                              |
| clock_synchronization | ntp                                             |
| config_applied        | 48b358c1-f2e3-4313-bf25-48ccec85d059            |
| config_status         | None                                            |
| config_target         | 48b358c1-f2e3-4313-bf25-48ccec85d059            |
| console               | ttyS0,115200                                    |
| created_at            | 2023-08-26T05:19:18.631627+00:00                |
| device_image_update   | None                                            |
| hostname              | controller-1                                    |
| id                    | 2                                               |
| install_output        | text                                            |
| install_state         | completed                                       |
| install_state_info    | None                                            |
| inv_state             | inventoried                                     |
| invprovision          | provisioned                                     |
| location              | {}                                              |
| mgmt_ip               | 2607:f160:0:3042:cd:290:0:12                    |
| mgmt_mac              | 48:df:37:bb:1f:f8                               |
| operational           | enabled                                         |
| personality           | controller                                      |
| reboot_needed         | False                                           |
| reserved              | False                                           |
| rootfs_device         | /dev/disk/by-path/pci-0000:5c:00.0-scsi-0:1:0:0 |
| serialid              | None                                            |
| software_load         | 21.12                                           |
| task                  | Swacting                                        |
| tboot                 | false                                           |
| ttys_dcd              | None                                            |
| updated_at            | 2023-09-12T17:10:38.168315+00:00                |
| uptime                | 1887                                            |
| uuid                  | 5a47ec4b-6652-4cf4-9333-cd0eba25148c            |
| vim_progress_status   | services-enabled                                |
+-----------------------+-------------------------------------------------+
logout
Connection to 2607:f160:0:3043:cd:290:0:10 closed.
[XXXXXX@vcpe-jumpserver ~]$
controller-0:~$ source /etc/platform/openrc
[XXXXXX@controller-0 ~(keystone_admin)]$ dcmanager subcloud list
+----+----------------------+------------+--------------+---------------+-------------+
| id | name                 | management | availability | deploy status | sync        |
+----+----------------------+------------+--------------+---------------+-------------+
|  1 | welktxef-d931887-021 | managed    | online       | complete      | out-of-sync |
+----+----------------------+------------+--------------+---------------+-------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ cd /opt/platform-backup/upgrade/wrcp-21.12-upgrade
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./apply-kubelet-config_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook apply-kubelet-config.yaml 0</dev/null

PLAY [all] *********************************************************************

TASK [Remove kubelet-config settings for old versions] *************************
changed: [localhost]

TASK [Reapply kubelet-config settings] *****************************************
changed: [localhost]

TASK [Wait for kubelet-config settings to be applied] **************************
FAILED - RETRYING: Wait for kubelet-config settings to be applied (10 retries left).
sleep 120
FAILED - RETRYING: Wait for kubelet-config settings to be applied (9 retries left).
FAILED - RETRYING: Wait for kubelet-config settings to be applied (8 retries left).
FAILED - RETRYING: Wait for kubelet-config settings to be applied (7 retries left).
changed: [localhost]

TASK [Output kubelet-config info] **********************************************
ok: [localhost] => {
    "msg": [
        "evictionHard:",
        "  imagefs.available: 2Gi",
        "  memory.available: 100Mi",
        "  nodefs.available: 10%",
        "  nodefs.inodesFree: 5%",
        "imageGCHighThresholdPercent: 79",
        "imageGCLowThresholdPercent: 75",
        "    imageGCLowThresholdPercent: 75",
        "    imageGCHighThresholdPercent: 79",
        "    evictionHard:",
        "      imagefs.available: 2Gi",
        "      memory.available: 100Mi",
        "      nodefs.inodesFree: 5%",
        "      nodefs.available: 10%"
    ]
}

PLAY RECAP *********************************************************************
localhost                  : ok=4    changed=3    unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ sleep 120
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ system kube-version-list | awk -F \| '$4 ~ / active / { gsub(/ /,"",$2);print $2 }'
v1.20.9
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ system health-query-kube-upgrade
System Health:
All hosts are provisioned: [OK]
All hosts are unlocked/enabled: [OK]
All hosts have current configurations: [OK]
All hosts are patch current: [OK]
No alarms: [Fail]
[6] alarms found, [0] of which are management affecting and [0] are certificate expiration alarms. Use "fm alarm-list" for details
All kubernetes nodes are ready: [OK]
All kubernetes control plane pods are ready: [OK]
Armada pods: [OK]
All kubernetes applications are in a valid state: [OK]

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ fm alarm-list --nowrap --mgmt_affecting | awk -F \| '$6 ~ / True / { print $0 }'
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
\[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ fm alarm-list --nowrap --mgmt_affecting | awk -F \| '$6 ~ / True / { print $0 }'
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ available=$(system kube-version-list | awk -F \| '$4 ~ / available / { print $2 }')

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ echo ${available}
v1.21.8
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ sw-manager kube-upgrade-strategy create --to-version ${available} --alarm-restrictions relaxed
Strategy Kubernetes Upgrade Strategy:
  strategy-uuid:                          a416951c-100a-4a2b-a9de-9937a10a7c20
  controller-apply-type:                  serial
  storage-apply-type:                     serial
  worker-apply-type:                      serial
  default-instance-action:                stop-start
  alarm-restrictions:                     relaxed
  current-phase:                          build
  current-phase-completion:               0%
  state:                                  building
  inprogress:                             true
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

Every 2.0s: sw-manager kube-upgrade-strategy show                                                                                         Tue Sep 12 17:18:25 2023

Strategy Kubernetes Upgrade Strategy:
  strategy-uuid:                          a416951c-100a-4a2b-a9de-9937a10a7c20
  controller-apply-type:                  serial
  storage-apply-type:                     serial
  worker-apply-type:                      serial
  default-instance-action:                stop-start
  alarm-restrictions:                     relaxed
  current-phase:                          build
  current-phase-completion:               100%
  state:                                  ready-to-apply
  build-result:                           success
  build-reason:


[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ sw-manager kube-upgrade-strategy apply
Strategy Kubernetes Upgrade Strategy:
  strategy-uuid:                          a416951c-100a-4a2b-a9de-9937a10a7c20
  controller-apply-type:                  serial
  storage-apply-type:                     serial
  worker-apply-type:                      serial
  default-instance-action:                stop-start
  alarm-restrictions:                     relaxed
  current-phase:                          apply
  current-phase-completion:               0%
  state:                                  applying
  inprogress:                             true
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

Every 2.0s: sw-manager kube-upgrade-strategy show                                                                                         Tue Sep 12 17:46:23 2023

Strategy Kubernetes Upgrade Strategy:
  strategy-uuid:                          a416951c-100a-4a2b-a9de-9937a10a7c20
  controller-apply-type:                  serial
  storage-apply-type:                     serial
  worker-apply-type:                      serial
  default-instance-action:                stop-start
  alarm-restrictions:                     relaxed
  current-phase:                          apply
  current-phase-completion:               59%
  state:                                  applying
  inprogress:                             true


Every 2.0s: sw-manager kube-upgrade-strategy show                                                                                         Tue Sep 12 18:10:26 2023

Strategy Kubernetes Upgrade Strategy:
  strategy-uuid:                          a416951c-100a-4a2b-a9de-9937a10a7c20
  controller-apply-type:                  serial
  storage-apply-type:                     serial
  worker-apply-type:                      serial
  default-instance-action:                stop-start
  alarm-restrictions:                     relaxed
  current-phase:                          apply
  current-phase-completion:               100%
  state:                                  applied
  apply-result:                           success
  apply-reason:


[XXXXXX@controller-1 ~(keystone_admin)]$ sw-manager kube-upgrade-strategy delete
Strategy deleted
[XXXXXX@controller-1 ~(keystone_admin)]$ system application-apply cert-manager
+---------------+----------------------------------+
| Property      | Value                            |
+---------------+----------------------------------+
| active        | True                             |
| app_version   | 21.12-28                         |
| created_at    | 2023-09-12T01:10:57.543560+00:00 |
| manifest_file | certmanager-manifest.yaml        |
| manifest_name | cert-manager-manifest            |
| name          | cert-manager                     |
| progress      | None                             |
| status        | applying                         |
| updated_at    | 2023-09-12T18:03:23.021056+00:00 |
+---------------+----------------------------------+
Please use 'system application-list' or 'system application-show cert-manager' to view the current progress.
[XXXXXX@controller-1 ~(keystone_admin)]$ system application-apply oidc-auth-apps
+---------------+----------------------------------+
| Property      | Value                            |
+---------------+----------------------------------+
| active        | True                             |
| app_version   | 21.12-61                         |
| created_at    | 2023-09-12T01:15:42.559240+00:00 |
| manifest_file | manifest.yaml                    |
| manifest_name | oidc-auth-manifest               |
| name          | oidc-auth-apps                   |
| progress      | None                             |
| status        | applying                         |
| updated_at    | 2023-09-12T18:04:24.199127+00:00 |
+---------------+----------------------------------+
Please use 'system application-list' or 'system application-show oidc-auth-apps' to view the current progress.
[XXXXXX@controller-1 ~(keystone_admin)]$ watch 'system application-list --nowrap | grep -E "cert-manager|oidc-auth-apps"'
[XXXXXX@controller-1 ~(keystone_admin)]$


Every 2.0s: system application-list --nowrap | grep -E "cert-manager|oidc-auth-apps"                                                      Tue Sep 12 18:11:24 2023

| cert-manager             | 21.12-28 | cert-manager-manifest             | certmanager-manifest.yaml              | applied  | completed
                                      |
| oidc-auth-apps           | 21.12-61 | oidc-auth-manifest                | manifest.yaml                          | applied  | completed
                                      |



[XXXXXX@controller-1 ~(keystone_admin)]$ kubectl --kubeconfig=/etc/kubernetes/admin.conf get pods -A | sed '1d' | \
> grep -E -v 'Running|Complete|ContainerCreating'
[XXXXXX@controller-1 ~(keystone_admin)]$
[XXXXXX@controller-1 ~(keystone_admin)]$ kubectl --kubeconfig=/etc/kubernetes/admin.conf get pods -A | sed '1d' | \
> grep -E -v 'Running|Complete|ContainerCreating'
[XXXXXX@controller-1 ~(keystone_admin)]$ system kube-host-upgrade-list
+----+--------------+-------------+----------------+-----------------------+-----------------+--------+
| id | hostname     | personality | target_version | control_plane_version | kubelet_version | status |
+----+--------------+-------------+----------------+-----------------------+-----------------+--------+
| 1  | controller-0 | controller  | v1.21.8        | v1.21.8               | v1.21.8         | None   |
| 2  | controller-1 | controller  | v1.21.8        | v1.21.8               | v1.21.8         | None   |
| 3  | worker-0     | worker      | v1.21.8        | N/A                   | v1.21.8         | None   |
+----+--------------+-------------+----------------+-----------------------+-----------------+--------+
[XXXXXX@controller-1 ~(keystone_admin)]$




[XXXXXX@controller-1 ~(keystone_admin)]$ rm -f /opt/platform-backup/upgrade/wrcp-21.12-upgrade/controller
[XXXXXX@controller-1 ~(keystone_admin)]$

```

### completed Mop 2 of 5 upgrade mops

### now to subcloud prestaging

### wrapper mop instructions are to ignore prestaging subcloud mop # 3
### using wrapper mop instructions

```log
controller-0:~$ source /etc/platform/openrc
[XXXXXX@controller-0 ~(keystone_admin)]$ welktxef-d931887-021^C
[XXXXXX@controller-0 ~(keystone_admin)]$ sudo -i
Password:
XXXXXX sudo -i

controller-0:~# cd /opt/platform-backup/
controller-0:/opt/platform-backup# rm -rf 21.05/
controller-0:/opt/platform-backup# mkdir 21.12
mkdir: cannot create directory ‘21.12’: File exists
controller-0:/opt/platform-backup#
controller-0:/opt/platform-backup# ls
21.12  lost+found
controller-0:/opt/platform-backup# cd 21.12/
controller-0:/opt/platform-backup/21.12# ls
bootimage.iso  bootimage.md5  container-image1.tar.gz  container-image2.tar.gz  container-image3.tar.gz  container-image.tar.gz.md5
controller-0:/opt/platform-backup/21.12# ls -latr
total 10619928
-rwxr-xr-x  1 root root 3949985792 Aug 18 18:13 bootimage.iso
-rwxr-xr-x  1 root root         48 Aug 18 18:13 bootimage.md5
-rwxr-xr-x  1 root root 2440630483 Aug 18 18:13 container-image1.tar.gz
-rwxr-xr-x  1 root root 2519922147 Aug 18 18:14 container-image2.tar.gz
-rwxr-xr-x  1 root root 1964228493 Aug 18 18:14 container-image3.tar.gz
drwxr-xr-x  2 root root       4096 Aug 18 18:14 .
-rwxr-xr-x  1 root root        174 Aug 18 18:14 container-image.tar.gz.md5
drwxr-xr-x. 4 root root       4096 Aug 18 22:19 ..
controller-0:/opt/platform-backup/21.12# md5sum -c *.md5
bootimage.iso: OK
container-image1.tar.gz: OK
container-image2.tar.gz: OK
container-image3.tar.gz: OK
controller-0:/opt/platform-backup/21.12#

```

### subcloud is prestaged now

### Wrapper mop:  Pre-checks for subclouds

```log

[XXXXXX@controller-0 21.12(keystone_admin)]$ . /etc/platform/openrc; fm alarm-list


[XXXXXX@controller-0 21.12(keystone_admin)]$

[XXXXXX@controller-0 21.12(keystone_admin)]$ kubectl get pods -A
NAMESPACE                     NAME                                              READY   STATUS              RESTARTS   AGE
armada                        armada-api-c5f5cd68-nzgvw                         2/2     Running             0          4d19h
cert-manager                  cm-cert-manager-856678cfb7-gxxbd                  1/1     Running             0          4d19h
cert-manager                  cm-cert-manager-cainjector-85849bd97-p74bh        1/1     Running             1          4d19h
cert-manager                  cm-cert-manager-webhook-5745478cbc-24k5k          1/1     Running             0          4d19h
kube-system                   calico-kube-controllers-5cd4695574-n62qv          1/1     Running             11         14d
kube-system                   calico-node-5j7m6                                 1/1     Running             5          14d
kube-system                   ceph-pools-audit-1694544600-gd8lx                 0/1     Completed           0          15m
kube-system                   ceph-pools-audit-1694544900-jsmw4                 0/1     Completed           0          10m
kube-system                   ceph-pools-audit-1694545200-r4xl7                 0/1     Completed           0          5m3s
kube-system                   ceph-pools-audit-1694545500-lh6s7                 0/1     ContainerCreating   0          2s
kube-system                   cephfs-provisioner-54847c557b-n7gbn               1/1     Running             1          4d19h
kube-system                   cephfs-storage-init-g64q5                         0/1     Completed           0          14d
kube-system                   coredns-666cb94996-xzhs6                          1/1     Running             5          14d
kube-system                   ic-nginx-ingress-ingress-nginx-controller-r7vn2   1/1     Running             0          4d19h
kube-system                   kube-apiserver-controller-0                       1/1     Running             5          14d
kube-system                   kube-controller-manager-controller-0              1/1     Running             7          14d
kube-system                   kube-multus-ds-amd64-bgmsm                        1/1     Running             6          14d
kube-system                   kube-proxy-nzxfm                                  1/1     Running             5          14d
kube-system                   kube-scheduler-controller-0                       1/1     Running             6          14d
kube-system                   kube-sriov-cni-ds-amd64-bglpk                     1/1     Running             5          14d
kube-system                   kube-sriov-device-plugin-amd64-lgq2d              0/1     CrashLoopBackOff    1360       4d19h
kube-system                   oidc-dex-c9d9d6f58-kzl4v                          1/1     Running             0          4d19h
kube-system                   rbd-provisioner-77bfb6dbb-t9gml                   1/1     Running             1          4d19h
kube-system                   storage-init-rbd-provisioner-4rpph                0/1     Completed           0          14d
kube-system                   stx-oidc-client-58569bc855-qjtwn                  1/1     Running             1          4d19h
platform-deployment-manager   platform-deployment-manager-0                     2/2     Running             1          4d19h
[XXXXXX@controller-0 21.12(keystone_admin)]$


```

### prechecks with subclouds good proceeding...


### wrapper mop- Upgrade 5 - Subclouds wrcp


```log

controller-0:~$ source /etc/platform/openrc
[XXXXXX@controller-0 ~(keystone_admin)]$ sw-patch query
      Patch ID         RR  Release  Patch State
=====================  ==  =======  ===========
WRCP_21.05_PATCH_0001  N    21.05    Committed
WRCP_21.05_PATCH_0002  Y    21.05    Committed
WRCP_21.05_PATCH_0003  N    21.05    Committed
WRCP_21.05_PATCH_0004  N    21.05    Committed
WRCP_21.05_PATCH_0005  N    21.05     Applied
WRCP_21.05_PATCH_0006  N    21.05     Applied

[XXXXXX@controller-0 ~(keystone_admin)]$ sudo sw-patch commit --release 21.05 --all
Password:
XXXXXX, try again.
Password:
XXXXXX following patches will be committed:
    WRCP_21.05_PATCH_0001
    WRCP_21.05_PATCH_0002
    WRCP_21.05_PATCH_0003
    WRCP_21.05_PATCH_0004
    WRCP_21.05_PATCH_0005
    WRCP_21.05_PATCH_0006

This commit operation would free 3.55 MiB

WARNING: Committing a patch is an irreversible operation. Committed patches
         cannot be removed.

Would you like to continue? [y/N]: y
The patches have been committed.
[XXXXXX@controller-0 ~(keystone_admin)]$ sw-patch query
      Patch ID         RR  Release  Patch State
=====================  ==  =======  ===========
WRCP_21.05_PATCH_0001  N    21.05    Committed
WRCP_21.05_PATCH_0002  Y    21.05    Committed
WRCP_21.05_PATCH_0003  N    21.05    Committed
WRCP_21.05_PATCH_0004  N    21.05    Committed
WRCP_21.05_PATCH_0005  N    21.05    Committed
WRCP_21.05_PATCH_0006  N    21.05    Committed

[XXXXXX@controller-0 ~(keystone_admin)]$


```

### didn't stop at right place, and accidently did some clean up work that caused patching to be off

### ran Tamas, mop for this issue "reverting wrcp 21.12p10 system controller clean up procedure

### now the patches are good, proceeding with next mop and steps for upgrading subcloud 


```log
[XXXXXX@controller-0 ~(keystone_admin)]$
[XXXXXX@controller-0 ~(keystone_admin)]$ source /etc/platform/openrc
[XXXXXX@controller-0 ~(keystone_admin)]$ cd /opt/platform-backup/upgrade/wrcp-21.12-upgrade
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ sw-patch query
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

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ system show
+------------------------+--------------------------------------+
| Property               | Value                                |
+------------------------+--------------------------------------+
| contact                | demo.engineer@verizon.com              |
| created_at             | 2023-08-26T04:43:17.345039+00:00     |
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
| updated_at             | 2023-09-12T01:10:47.235770+00:00     |
| uuid                   | 85d98699-635d-490f-ae18-ba3302ed8605 |
| vswitch_type           | none                                 |
+------------------------+--------------------------------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ cd /opt/platform-backup/upgrade/wrcp-21.12-upgrade
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ sudo show-certs.sh | grep -E '^\s+Residual Time'
Password:
	 XXXXXX Time	:  384d
	 Residual Time	:  347d
	 Residual Time	:  196d
	 Residual Time	:  2597d
	 Residual Time	:  4293d
	 Residual Time	:  2598d
	 Residual Time	:  1807d
	 Residual Time	:  162d
	 Residual Time	:  3649d
	 Residual Time	:  365d
	 Residual Time	:  365d
	 Residual Time	:  365d
	 Residual Time	:  350d
	 Residual Time	:  4293d
	 Residual Time	:  4293d
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ for s in $(echo dcmanager sw-manager); do
> for t in $(echo upgrade patch fw-update kube-upgrade); do
> $s $t-strategy delete
> done
> done
Not found
ERROR (app) Unable to delete sw update strategy
Not found
ERROR (app) Unable to delete sw update strategy
Not found
ERROR (app) Unable to delete sw update strategy
Not found
ERROR (app) Unable to delete sw update strategy
Strategy delete failed
Strategy delete failed
Strategy delete failed
Strategy delete failed
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ dcmanager subcloud-group list
+----+---------+------------------------+
| id | name    | description            |
+----+---------+------------------------+
|  1 | Default | Default Subcloud Group |
+----+---------+------------------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ dcmanager subcloud-group list Default
usage: dcmanager subcloud-group list [-h] [-f {csv,json,table,value,yaml}]
                                     [-c COLUMN] [--max-width <integer>]
                                     [--fit-width] [--print-empty]
                                     [--noindent]
                                     [--quote {all,minimal,none,nonnumeric}]
                                     [--sort-column SORT_COLUMN]
dcmanager subcloud-group list: error: unrecognized arguments: Default
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ dcmanager subcloud-group show Default
+------------------------+------------------------+
| Field                  | Value                  |
+------------------------+------------------------+
| id                     | 1                      |
| name                   | Default                |
| description            | Default Subcloud Group |
| update apply type      | parallel               |
| max parallel subclouds | 2                      |
| created_at             | None                   |
| updated_at             | None                   |
+------------------------+------------------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ subcloud_group=Default
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ dcmanager subcloud-group update ${subcloud_group} \
> --update_apply_type parallel --max_parallel_subclouds 50
+------------------------+----------------------------+
| Field                  | Value                      |
+------------------------+----------------------------+
| id                     | 1                          |
| name                   | Default                    |
| description            | Default Subcloud Group     |
| update apply type      | parallel                   |
| max parallel subclouds | 50                         |
| created_at             | None                       |
| updated_at             | 2023-09-12 21:20:17.302241 |
+------------------------+----------------------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ echo '[subclouds]' > subclouds
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ dcmanager subcloud-group list-subclouds ${subcloud_group} -c name -f value >> subclouds
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ more subclouds
[subclouds]
welktxef-d931887-021
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ for subcloud in $(sed -n '/subclouds/ { :a; n; p; ba; }' < subclouds); do
> echo ${subcloud}
> dcmanager subcloud show ${subcloud} | \
> grep sync_status | \
> grep -E -v "in-sync|load_sync|kubernetes_sync|firmware_sync|dc-cert_sync";
> don
> ^C
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ for subcloud in $(sed -n '/subclouds/ { :a; n; p; ba; }' < subclouds); do
> echo ${subcloud}
> dcmanager subcloud show ${subcloud} | \
> grep sync_status | \
> grep -E -v "in-sync|load_sync|kubernetes_sync|firmware_sync|dc-cert_sync";
> done
welktxef-d931887-021
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ sudo -u XXXXXX psql --tuples-only --pset pager=off --dbname dcmanager --command \
> "select name from subclouds where data_install = '' and name in (${names})"
Password:

XXXXXX wrcp-21.12-upgrade(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./cleanup-images_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook --inventory subclouds --ask-pass --user XXXXXX \
> cleanup-images.yaml 0</dev/null
SSH password:

XXXXXX [all] *********************************************************************

TASK [Remove container images] *************************************************
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931887-021
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931887-021
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931887-021
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931887-021
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931887-021
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931887-021
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931887-021
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931887-021
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931887-021
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931887-021
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931887-021
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931887-021
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931887-021
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931887-021
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931887-021
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931887-021
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931887-021
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931887-021
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931887-021

TASK [Retrieve list of docker.elastic.co/beats/filebeat tags] ******************
changed: [welktxef-d931887-021]

TASK [Loop over all docker.elastic.co/beats/filebeat tags] *********************

TASK [Retrieve list of docker.elastic.co/beats/filebeat-oss tags] **************
changed: [welktxef-d931887-021]

TASK [Loop over all docker.elastic.co/beats/filebeat-oss tags] *****************

TASK [Retrieve list of docker.elastic.co/beats/metricbeat tags] ****************
changed: [welktxef-d931887-021]

TASK [Loop over all docker.elastic.co/beats/metricbeat tags] *******************

TASK [Retrieve list of docker.elastic.co/beats/metricbeat-oss tags] ************
changed: [welktxef-d931887-021]

TASK [Loop over all docker.elastic.co/beats/metricbeat-oss tags] ***************

TASK [Retrieve list of docker.elastic.co/elasticsearch/elasticsearch tags] *****
changed: [welktxef-d931887-021]

TASK [Loop over all docker.elastic.co/elasticsearch/elasticsearch tags] ********

TASK [Retrieve list of docker.elastic.co/elasticsearch/elasticsearch-oss tags] ***
changed: [welktxef-d931887-021]

TASK [Loop over all docker.elastic.co/elasticsearch/elasticsearch-oss tags] ****

TASK [Retrieve list of docker.elastic.co/kibana/kibana tags] *******************
changed: [welktxef-d931887-021]

TASK [Loop over all docker.elastic.co/kibana/kibana tags] **********************

TASK [Retrieve list of docker.elastic.co/kibana/kibana-oss tags] ***************
changed: [welktxef-d931887-021]

TASK [Loop over all docker.elastic.co/kibana/kibana-oss tags] ******************

TASK [Retrieve list of docker.elastic.co/logstash/logstash tags] ***************
changed: [welktxef-d931887-021]

TASK [Loop over all docker.elastic.co/logstash/logstash tags] ******************

TASK [Retrieve list of docker.elastic.co/logstash/logstash-oss tags] ***********
changed: [welktxef-d931887-021]

TASK [Loop over all docker.elastic.co/logstash/logstash-oss tags] **************

TASK [Retrieve list of quay.io/coreos/kube-state-metrics tags] *****************
changed: [welktxef-d931887-021]

TASK [Loop over all quay.io/coreos/kube-state-metrics tags] ********************

TASK [Retrieve list of quay.io/kubernetes-ingress-controller/nginx-ingress-controller tags] ***
changed: [welktxef-d931887-021]

TASK [Loop over all quay.io/kubernetes-ingress-controller/nginx-ingress-controller tags] ***

TASK [Retrieve list of docker.io/wind-river/elastic-services tags] *************
changed: [welktxef-d931887-021]

TASK [Loop over all docker.io/wind-river/elastic-services tags] ****************

TASK [Retrieve list of docker.io/wind-river/wra-kibana tags] *******************
changed: [welktxef-d931887-021]

TASK [Loop over all docker.io/wind-river/wra-kibana tags] **********************

TASK [Retrieve list of docker.io/wind-river/wra-metricbeat tags] ***************
changed: [welktxef-d931887-021]

TASK [Loop over all docker.io/wind-river/wra-metricbeat tags] ******************

TASK [Retrieve list of docker.io/wind-river/wra-elasticsearch tags] ************
changed: [welktxef-d931887-021]

TASK [Loop over all docker.io/wind-river/wra-elasticsearch tags] ***************

TASK [Retrieve list of docker.io/wind-river/wra-logstash tags] *****************
changed: [welktxef-d931887-021]

TASK [Loop over all docker.io/wind-river/wra-logstash tags] ********************

TASK [Retrieve list of docker.io/wind-river/cloud-platform-deployment-manager tags] ***
changed: [welktxef-d931887-021]

TASK [Loop over all docker.io/wind-river/cloud-platform-deployment-manager tags] ***
changed: [welktxef-d931887-021] => (item=WRCP_21.05)

TASK [Retrieve list of docker.io/starlingx/k8s-cni-sriov tags] *****************
changed: [welktxef-d931887-021]

TASK [Loop over all docker.io/starlingx/k8s-cni-sriov tags] ********************
changed: [welktxef-d931887-021] => (item=stx.5.0-v2.6-7-gb18123d8)

TASK [Garbage collect] *********************************************************
changed: [welktxef-d931887-021]

PLAY RECAP *********************************************************************
welktxef-d931887-021       : ok=41   changed=22   unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./cleanup-unexpected-images_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook --inventory subclouds --ask-pass --user XXXXXX \
> cleanup-unexpected-images.yaml 0</dev/null
SSH password:

XXXXXX [all] *********************************************************************

TASK [Remove container images] *************************************************
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931887-021
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931887-021
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931887-021
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931887-021
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931887-021
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931887-021
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931887-021
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931887-021
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931887-021
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931887-021
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931887-021
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931887-021
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931887-021
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931887-021
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931887-021
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931887-021
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931887-021
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931887-021
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931887-021
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931887-021

TASK [Retrieve list of docker.io/hashicorp/vault-k8s tags] *********************
changed: [welktxef-d931887-021]

TASK [Loop over all docker.io/hashicorp/vault-k8s tags] ************************

TASK [Retrieve list of docker.io/netapp/trident tags] **************************
changed: [welktxef-d931887-021]

TASK [Loop over all docker.io/netapp/trident tags] *****************************

TASK [Retrieve list of docker.io/starlingx/intel-fpga-plugin tags] *************
changed: [welktxef-d931887-021]

TASK [Loop over all docker.io/starlingx/intel-fpga-plugin tags] ****************

TASK [Retrieve list of docker.io/starlingx/portieris tags] *********************
changed: [welktxef-d931887-021]

TASK [Loop over all docker.io/starlingx/portieris tags] ************************

TASK [Retrieve list of docker.io/starlingx/rvmc tags] **************************
changed: [welktxef-d931887-021]

TASK [Loop over all docker.io/starlingx/rvmc tags] *****************************

TASK [Retrieve list of docker.io/starlingx/stx-fm-subagent tags] ***************
changed: [welktxef-d931887-021]

TASK [Loop over all docker.io/starlingx/stx-fm-subagent tags] ******************

TASK [Retrieve list of docker.io/starlingx/stx-fm-trap-subagent tags] **********
changed: [welktxef-d931887-021]

TASK [Loop over all docker.io/starlingx/stx-fm-trap-subagent tags] *************

TASK [Retrieve list of docker.io/starlingx/stx-platformclients tags] ***********
changed: [welktxef-d931887-021]

TASK [Loop over all docker.io/starlingx/stx-platformclients tags] **************

TASK [Retrieve list of docker.io/starlingx/stx-platformclients tags] ***********
changed: [welktxef-d931887-021]

TASK [Loop over all docker.io/starlingx/stx-platformclients tags] **************

TASK [Retrieve list of docker.io/starlingx/stx-snmp tags] **********************
changed: [welktxef-d931887-021]

TASK [Loop over all docker.io/starlingx/stx-snmp tags] *************************

TASK [Retrieve list of docker.io/starlingx/stx-vault-manager tags] *************
changed: [welktxef-d931887-021]

TASK [Loop over all docker.io/starlingx/stx-vault-manager tags] ****************

TASK [Retrieve list of docker.io/untergeek/curator tags] ***********************
changed: [welktxef-d931887-021]

TASK [Loop over all docker.io/untergeek/curator tags] **************************

TASK [Retrieve list of docker.io/vault tags] ***********************************
changed: [welktxef-d931887-021]

TASK [Loop over all docker.io/vault tags] **************************************

TASK [Retrieve list of docker.io/wind-river/cmk tags] **************************
changed: [welktxef-d931887-021]

TASK [Loop over all docker.io/wind-river/cmk tags] *****************************

TASK [Retrieve list of k8s.gcr.io/nfd/node-feature-discovery tags] *************
changed: [welktxef-d931887-021]

TASK [Loop over all k8s.gcr.io/nfd/node-feature-discovery tags] ****************

TASK [Retrieve list of quay.io/k8scsi/csi-attacher tags] ***********************
changed: [welktxef-d931887-021]

TASK [Loop over all quay.io/k8scsi/csi-attacher tags] **************************

TASK [Retrieve list of quay.io/k8scsi/csi-node-driver-registrar tags] **********
changed: [welktxef-d931887-021]

TASK [Loop over all quay.io/k8scsi/csi-node-driver-registrar tags] *************

TASK [Retrieve list of quay.io/k8scsi/csi-provisioner tags] ********************
changed: [welktxef-d931887-021]

TASK [Loop over all quay.io/k8scsi/csi-provisioner tags] ***********************

TASK [Retrieve list of quay.io/k8scsi/csi-resizer tags] ************************
changed: [welktxef-d931887-021]

TASK [Loop over all quay.io/k8scsi/csi-resizer tags] ***************************

TASK [Retrieve list of quay.io/k8scsi/csi-snapshotter tags] ********************
changed: [welktxef-d931887-021]

TASK [Loop over all quay.io/k8scsi/csi-snapshotter tags] ***********************

TASK [Garbage collect] *********************************************************
changed: [welktxef-d931887-021]

TASK [Wait for 250.001 alarm to clear] *****************************************
FAILED - RETRYING: Wait for 250.001 alarm to clear (60 retries left).
FAILED - RETRYING: Wait for 250.001 alarm to clear (59 retries left).
FAILED - RETRYING: Wait for 250.001 alarm to clear (58 retries left).
changed: [welktxef-d931887-021]

PLAY RECAP *********************************************************************
welktxef-d931887-021       : ok=42   changed=22   unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_ROLES_PATH=/usr/share/ansible/stx-ansible/playbooks/roles \
> ANSIBLE_LOG_PATH=./local-registry-size_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook --inventory subclouds \
> --extra-vars "local_registry_pass=${local_registry_pass}" \
> --ask-pass --ask-become-pass --user XXXXXX \
> calculate-user-local-registry-size.yaml 0</dev/null
SSH password:
XXXXXX password[defaults to SSH password]:

PLAY [all] *********************************************************************

TASK [Validate local_registry_pass] ********************************************
skipping: [welktxef-d931887-021]

TASK [common/load-images-information : Set kubernetes long version] ************
ok: [welktxef-d931887-021]

TASK [common/load-images-information : Get the list of kubernetes images] ******
changed: [welktxef-d931887-021]

TASK [common/load-images-information : set_fact] *******************************
ok: [welktxef-d931887-021]

TASK [common/load-images-information : Read in system images list] *************
ok: [welktxef-d931887-021]

TASK [common/load-images-information : Check if additional image config file exists] ***
ok: [welktxef-d931887-021]

TASK [common/load-images-information : Read in additional system images list(s) in localhost] ***
skipping: [welktxef-d931887-021]

TASK [common/load-images-information : Create a temporary file on remote] ******
changed: [welktxef-d931887-021]

TASK [common/load-images-information : Fetch the additional images config in case the playbook is executed remotely] ***
changed: [welktxef-d931887-021]

TASK [common/load-images-information : Read in additional system images list(s) fetched from remote] ***
ok: [welktxef-d931887-021]

TASK [common/load-images-information : Remove the temporary file on remote] ****
changed: [welktxef-d931887-021 -> welktxef-d931887-021]

TASK [common/load-images-information : Remove override temp file on Ansible control host] ***
changed: [welktxef-d931887-021 -> localhost]

TASK [common/load-images-information : Categorize system images] ***************
ok: [welktxef-d931887-021]

TASK [common/load-images-information : Append additional static images if provisioned] ***
ok: [welktxef-d931887-021] => (item={'key': u'deploy_manager_img', 'value': u'docker.io/wind-river/cloud-platform-deployment-manager:WRCP_21.05'})
ok: [welktxef-d931887-021] => (item={'key': u'kube_rbac_proxy_img', 'value': u'gcr.io/kubebuilder/kube-rbac-proxy:v0.4.0'})

TASK [common/load-images-information : Append RVMC image for a DC system controller] ***
skipping: [welktxef-d931887-021]

TASK [common/load-images-information : Append additional static images for a DC system controller if provisioned] ***
skipping: [welktxef-d931887-021] => (item={'key': u'rbd_provisioner_img', 'value': u'quay.io/external_storage/rbd-provisioner:v2.1.1-k8s1.11'})
skipping: [welktxef-d931887-021] => (item={'key': u'ceph_config_helper_img', 'value': u'docker.io/starlingx/ceph-config-helper:v1.15.0'})

TASK [Set platform images list] ************************************************
ok: [welktxef-d931887-021]

TASK [Create a temporary file on remote] ***************************************
changed: [welktxef-d931887-021]

TASK [Correct permissions for temporary file on remote] ************************
changed: [welktxef-d931887-021]

TASK [Save list of local registry images excluding apps images to file] ********
changed: [welktxef-d931887-021]

TASK [Read file] ***************************************************************
changed: [welktxef-d931887-021]

TASK [Load list of local registry images from file] ****************************
ok: [welktxef-d931887-021]

TASK [Subtract platform images from local registry images] *********************
ok: [welktxef-d931887-021]

TASK [Append local registry host:port to image names] **************************
ok: [welktxef-d931887-021]

TASK [debug] *******************************************************************
ok: [welktxef-d931887-021] => {
    "image_list": [
        "registry.local:9001/quay.io/airshipit/armada:8a1638098f88d92bf799ef4934abe569789b885e-ubuntu_bionic",
        "registry.local:9001/gcr.io/kubernetes-helm/tiller:v2.16.1",
        "registry.local:9001/docker.io/starlingx/n3000-opae:stx.4.0-v1.0.0"
    ]
}

TASK [Log in to local registry] ************************************************
changed: [welktxef-d931887-021]

TASK [Pull images from local registry to docker filesystem] ********************
changed: [welktxef-d931887-021] => (item=registry.local:9001/quay.io/airshipit/armada:8a1638098f88d92bf799ef4934abe569789b885e-ubuntu_bionic)
changed: [welktxef-d931887-021] => (item=registry.local:9001/gcr.io/kubernetes-helm/tiller:v2.16.1)
changed: [welktxef-d931887-021] => (item=registry.local:9001/docker.io/starlingx/n3000-opae:stx.4.0-v1.0.0)

TASK [Set format parameter for docker inspect to retrieve only the size] *******
ok: [welktxef-d931887-021]

TASK [Get docker images size in bytes] *****************************************
changed: [welktxef-d931887-021] => (item=registry.local:9001/quay.io/airshipit/armada:8a1638098f88d92bf799ef4934abe569789b885e-ubuntu_bionic)
changed: [welktxef-d931887-021] => (item=registry.local:9001/gcr.io/kubernetes-helm/tiller:v2.16.1)
changed: [welktxef-d931887-021] => (item=registry.local:9001/docker.io/starlingx/n3000-opae:stx.4.0-v1.0.0)

TASK [Parse docker images size] ************************************************
ok: [welktxef-d931887-021] => (item=registry.local:9001/quay.io/airshipit/armada:8a1638098f88d92bf799ef4934abe569789b885e-ubuntu_bionic, 457539381 bytes)
ok: [welktxef-d931887-021] => (item=registry.local:9001/gcr.io/kubernetes-helm/tiller:v2.16.1, 91160017 bytes)
ok: [welktxef-d931887-021] => (item=registry.local:9001/docker.io/starlingx/n3000-opae:stx.4.0-v1.0.0, 506492391 bytes)

TASK [debug] *******************************************************************
ok: [welktxef-d931887-021] => {
    "docker_images_size": "1055191789"
}

TASK [Remove pulled images] ****************************************************
changed: [welktxef-d931887-021]

TASK [Scale to KiB and reserve 5% for docker metadata inside exported archive] ***
ok: [welktxef-d931887-021]

TASK [Determine available space in /opt/platform-backup] ***********************
changed: [welktxef-d931887-021]

TASK [Fail if there is not enough free space to create docker images backup archive] ***
skipping: [welktxef-d931887-021]

TASK [Remove the temporary file from remote] ***********************************
changed: [welktxef-d931887-021]

PLAY RECAP *********************************************************************
welktxef-d931887-021       : ok=31   changed=15   unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$



[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ cat /home/XXXXXX/sanity/output_list
welktxef-d931887-021 - check pod status
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

controller-0:~$ source /etc/platform/openrc
[XXXXXX@controller-0 ~(keystone_admin)]$ kubectl get pods -A
NAMESPACE                     NAME                                              READY   STATUS      RESTARTS   AGE
armada                        armada-api-c5f5cd68-nzgvw                         2/2     Running     0          4d22h
cert-manager                  cm-cert-manager-856678cfb7-gxxbd                  1/1     Running     0          4d22h
cert-manager                  cm-cert-manager-cainjector-85849bd97-p74bh        1/1     Running     1          4d22h
cert-manager                  cm-cert-manager-webhook-5745478cbc-24k5k          1/1     Running     0          4d22h
kube-system                   calico-kube-controllers-5cd4695574-n62qv          1/1     Running     11         15d
kube-system                   calico-node-5j7m6                                 1/1     Running     5          15d
kube-system                   ceph-pools-audit-1694554800-vkcvb                 0/1     Completed   0          11m
kube-system                   ceph-pools-audit-1694555100-vlsrs                 0/1     Completed   0          6m50s
kube-system                   ceph-pools-audit-1694555400-kgprl                 0/1     Completed   0          110s
kube-system                   cephfs-provisioner-54847c557b-n7gbn               1/1     Running     1          4d22h
kube-system                   cephfs-storage-init-g64q5                         0/1     Completed   0          15d
kube-system                   coredns-666cb94996-xzhs6                          1/1     Running     5          15d
kube-system                   ic-nginx-ingress-ingress-nginx-controller-r7vn2   1/1     Running     0          4d22h
kube-system                   kube-apiserver-controller-0                       1/1     Running     5          15d
kube-system                   kube-controller-manager-controller-0              1/1     Running     7          15d
kube-system                   kube-multus-ds-amd64-bgmsm                        1/1     Running     6          15d
kube-system                   kube-proxy-nzxfm                                  1/1     Running     5          15d
kube-system                   kube-scheduler-controller-0                       1/1     Running     6          15d
kube-system                   kube-sriov-cni-ds-amd64-bglpk                     1/1     Running     5          15d
kube-system                   kube-sriov-device-plugin-amd64-lgq2d              0/1     Completed   1393       4d22h
kube-system                   oidc-dex-c9d9d6f58-kzl4v                          1/1     Running     0          4d22h
kube-system                   rbd-provisioner-77bfb6dbb-t9gml                   1/1     Running     1          4d22h
kube-system                   storage-init-rbd-provisioner-4rpph                0/1     Completed   0          15d
kube-system                   stx-oidc-client-58569bc855-qjtwn                  1/1     Running     1          4d22h
platform-deployment-manager   platform-deployment-manager-0                     2/2     Running     1          4d22h
[XXXXXX@controller-0 ~(keystone_admin)]$ exit

pod status is fine, no application on the box continuing

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ for subcloud in $(sed -n '/subclouds/ { :a; n; p; ba; }' < subclouds); do
> echo ${subcloud}
> system --os-region-name ${subcloud} --os-endpoint-type admin application-show \
> --format value --column app_version wr-analytics | cut -d- -f1
> done
welktxef-d931887-021
application not found: wr-analytics
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./fix-backup-system_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook --inventory subclouds --ask-pass --ask-become-pass --user XXXXXX \
> fix-backup-system.yaml 0</dev/null
SSH password:
XXXXXX password[defaults to SSH password]:

PLAY [all] *********************************************************************

TASK [Add fail task to backup-system rescue block] *****************************
changed: [welktxef-d931887-021]

PLAY RECAP *********************************************************************
welktxef-d931887-021       : ok=1    changed=1    unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$


```


### Deployment section of mop for subcloud

```log
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ source /etc/platform/openrc
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ cd /opt/platform-backup/upgrade/wrcp-21.12-upgrade
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ dcmanager upgrade-strategy create --group ${subcloud_group}
+------------------------+----------------------------+
| Field                  | Value                      |
+------------------------+----------------------------+
| strategy type          | upgrade                    |
| subcloud apply type    | parallel                   |
| max parallel subclouds | 50                         |
| stop on failure        | False                      |
| state                  | initial                    |
| created_at             | 2023-09-12T21:59:23.350462 |
| updated_at             | None                       |
+------------------------+----------------------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ dcmanager strategy-step list -c cloud -c stage -c state
+----------------------+-------+---------+
| cloud                | stage | state   |
+----------------------+-------+---------+
| welktxef-d931887-021 |     1 | initial |
+----------------------+-------+---------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ dcmanager upgrade-strategy apply
+------------------------+----------------------------+
| Field                  | Value                      |
+------------------------+----------------------------+
| strategy type          | upgrade                    |
| subcloud apply type    | parallel                   |
| max parallel subclouds | 50                         |
| stop on failure        | False                      |
| state                  | applying                   |
| created_at             | 2023-09-12T21:59:23.350462 |
| updated_at             | 2023-09-12T22:00:10.947889 |
+------------------------+----------------------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

Every 15.0s: dcmanager strategy-step list -c cloud -c state -c details --max-width 100 --sort-column details --sort-column state          Tue Sep 12 22:00:26 2023

+----------------------+--------------------+---------+
| cloud                | state              | details |
+----------------------+--------------------+---------+
| welktxef-d931887-021 | installing license |         |
+----------------------+--------------------+---------+

Every 15.0s: dcmanager strategy-step list -c cloud -c state -c details --max-width 100 --sort-column details --sort-column state          Tue Sep 12 22:20:07 2023

+----------------------+-------------------+---------+
| cloud                | state             | details |
+----------------------+-------------------+---------+
| welktxef-d931887-021 | upgrading simplex |         |
+----------------------+-------------------+---------+

Every 15.0s: dcmanager strategy-step list -c cloud -c state -c details --max-width 100 --sort-column details --sort-column state          Tue Sep 12 23:20:41 2023

+----------------------+----------+---------+
| cloud                | state    | details |
+----------------------+----------+---------+
| welktxef-d931887-021 | complete |         |
+----------------------+----------+---------+



```

### upgrade complete 

### 4.8 

```log

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ dcmanager upgrade-strategy delete
+------------------------+----------------------------+
| Field                  | Value                      |
+------------------------+----------------------------+
| strategy type          | upgrade                    |
| subcloud apply type    | parallel                   |
| max parallel subclouds | 50                         |
| stop on failure        | False                      |
| state                  | deleting                   |
| created_at             | 2023-09-12T21:59:23.350462 |
| updated_at             | 2023-09-12T23:22:36.263565 |
+------------------------+----------------------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./set-intel-driver-version_$(date "+%Y%m%d%H%M%S").log ansible-playbook --inventory subclouds --ask-pass --user XXXXXX set-intel-driver-version.yaml 0</dev/null
SSH password:

XXXXXX [all] *********************************************************************

TASK [Retrieve platform release version] ***************************************
changed: [welktxef-d931887-021]

TASK [Retrieve intel_nic_driver_version service parameter] *********************
changed: [welktxef-d931887-021]

TASK [Store service parameter field values] ************************************
ok: [welktxef-d931887-021]

TASK [Delete old intel_nic_driver_version service parameter with resource] *****
changed: [welktxef-d931887-021]

TASK [Clear the driver version] ************************************************
ok: [welktxef-d931887-021]

TASK [Set Intel driver version (with resource)] ********************************
skipping: [welktxef-d931887-021]

TASK [Set Intel driver version] ************************************************
changed: [welktxef-d931887-021]

TASK [Apply service parameters] ************************************************
changed: [welktxef-d931887-021]

TASK [Retrieve current Intel driver version] ***********************************
changed: [welktxef-d931887-021]

PLAY RECAP *********************************************************************
welktxef-d931887-021       : ok=8    changed=6    unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./lock-unlock_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook --inventory subclouds --ask-pass --user XXXXXX lock-unlock.yaml \
> 0</dev/null
SSH password:

XXXXXX [all] *********************************************************************

TASK [Check if host is already locked] *****************************************
changed: [welktxef-d931887-021]

TASK [Lock host] ***************************************************************
changed: [welktxef-d931887-021]

TASK [Wait for host to enter locked state] *************************************
changed: [welktxef-d931887-021]

TASK [Unlock host] *************************************************************
changed: [welktxef-d931887-021]

PLAY RECAP *********************************************************************
welktxef-d931887-021       : ok=4    changed=4    unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

Every 2.0s: dcmanager subcloud-group list-subclouds Default -f value -c name -c availability                                              Tue Sep 12 23:35:39 2023

welktxef-d931887-021 online


[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./confirm-ice-driver-version_$(date "+%Y%m%d%H%M%S").log \
> ansible all --inventory subclouds --ask-pass --ask-become-pass --user XXXXXX --become \
> --module-name shell --args "grep -E 'ice\:.*1\.5\.8$' /var/log/dmesg"
SSH password:
XXXXXX password[defaults to SSH password]:
welktxef-d931887-021 | CHANGED | rc=0 >>
[   12.872643] ice: Intel(R) Ethernet Connection E800 Series Linux Driver - version 1.5.8

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./dm_delete_old_secret_$(date "+%Y%m%d%H%M%S").log \
> ansible all --inventory subclouds --ask-pass --user XXXXXX --module-name shell \
> --args "kubectl --kubeconfig /etc/kubernetes/admin.conf delete secret \
> -n platform-deployment-manager platform-deployment-manager-webhook-server-secret"
SSH password:
XXXXXX | CHANGED | rc=0 >>
secret "platform-deployment-manager-webhook-server-secret" deleted

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ for subcloud in $(dcmanager subcloud-group list-subclouds ${subcloud_group} -f value -c name); do dcmanager subcloud reconfig --XXXXXX-password ${XXXXXX_password} --deploy-config subclouds-deployment-config.yaml ${subcloud}; done
+-----------------------------+---------------------------------+
| Field                       | Value                           |
+-----------------------------+---------------------------------+
| id                          | 1                               |
| name                        | welktxef-d931887-021            |
| description                 | Wind River Cloud Platform 21.05 |
| location                    | welktxef-d931887-021            |
| software_version            | 21.12                           |
| management                  | managed                         |
| availability                | online                          |
| deploy_status               | pre-deploy                      |
| management_subnet           | 2607:f160:10:809f::/64          |
| management_start_ip         | 2607:f160:10:809f:ce:40a::      |
| management_end_ip           | 2607:f160:10:809f:ce:40a:0:f    |
| management_gateway_ip       | 2607:f160:10:809f:ce:28::       |
| systemcontroller_gateway_ip | 2607:f160:0:3042:cd:28::        |
| group_id                    | 1                               |
| created_at                  | 2023-08-28T20:16:09.254300      |
| updated_at                  | 2023-09-13T01:58:41.225952      |
+-----------------------------+---------------------------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

Every 2.0s: dcmanager subcloud-group list-subclouds Default -c name -c deploy_status                                                      Wed Sep 13 02:23:42 2023

+----------------------+---------------+
| name                 | deploy_status |
+----------------------+---------------+
| welktxef-d931887-021 | complete      |
+----------------------+---------------+


[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./verify-subcloud-dm_$(date "+%Y%m%d%H%M%S").log \
> ansible all --inventory subclouds --ask-pass --user XXXXXX --module-name shell \
> --args "kubectl --kubeconfig /etc/kubernetes/admin.conf get pods \
> -l control-plane=controller-manager -n platform-deployment-manager; \
> kubectl --kubeconfig /etc/kubernetes/admin.conf get pods \
> -l control-plane=controller-manager -n platform-deployment-manager \
> -o jsonpath="{..image}" | tr -s '[[:space:]]' '\n'| sort | uniq"
SSH password:
XXXXXX | CHANGED | rc=0 >>
NAME                            READY   STATUS    RESTARTS   AGE
platform-deployment-manager-0   2/2     Running   2          25m
registry.local:9001/docker.io/wind-river/cloud-platform-deployment-manager:WRCP_21.12-wrs.4
registry.local:9001/gcr.io/kubebuilder/kube-rbac-proxy:v0.4.0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./install-dm-monitor_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook --inventory subclouds --ask-pass --user XXXXXX \
> /usr/local/share/applications/playbooks/dm-monitor-book.yaml \
> --extra-vars "dm_monitor_dir=/usr/local/share/applications/helm/dm-monitor-1.0.0.tgz
> dm_monitor_overrides=/usr/local/share/applications/overrides/dm-monitor-overrides.yaml" \
> 0</dev/null
SSH password:

XXXXXX [Deployment Manager Monitor Playbook] *************************************

TASK [set_fact] ****************************************************************
ok: [welktxef-d931887-021]

TASK [Get Ip Controller] *******************************************************
changed: [welktxef-d931887-021]

TASK [debug] *******************************************************************
ok: [welktxef-d931887-021] => {
    "msg": "controller ip: 2607:f160:10:809f:ce:40a::"
}

TASK [Install Deployment Manager Monitor] **************************************
changed: [welktxef-d931887-021]

TASK [Wait for Deployment Manager Monitor to be ready] *************************
changed: [welktxef-d931887-021]

PLAY RECAP *********************************************************************
welktxef-d931887-021       : ok=5    changed=3    unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./verify-subcloud-dm-monitor_$(date "+%Y%m%d%H%M%S").log \
> ansible all --inventory subclouds --ask-pass --user XXXXXX --module-name shell \
> --args "kubectl --kubeconfig /etc/kubernetes/admin.conf get pods \
> -l app=dm-monitor -n platform-deployment-manager; \
> kubectl --kubeconfig /etc/kubernetes/admin.conf get pods \
> -l app=dm-monitor -n platform-deployment-manager \
> -o jsonpath="{..image}" | tr -s '[[:space:]]' '\n'| sort | uniq"
SSH password:
XXXXXX | CHANGED | rc=0 >>
NAME                          READY   STATUS    RESTARTS   AGE
dm-monitor-85bc647788-ttbkv   1/1     Running   0          35s
registry.local:9001/docker.io/wind-river/dm-monitor:WRCP_21.05-v1.0.0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$




[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./ptp-notification-upgrade_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook --inventory subclouds --ask-pass --user XXXXXX app-apply.yaml \
> --extra-vars "application=ptp-notification preop=delete
> overrides_file=ptp-notification-overrides.yaml overrides_chart_name=ptp-notification
> overrides_namespace=notification" \
> 0</dev/null
SSH password:

XXXXXX [all] *********************************************************************

TASK [Remove application] ******************************************************
changed: [welktxef-d931887-021]

TASK [Check if application is removed] *****************************************
FAILED - RETRYING: Check if application is removed (6 retries left).
changed: [welktxef-d931887-021]

TASK [Delete application] ******************************************************
changed: [welktxef-d931887-021]

TASK [Retrieve latest application version] *************************************
changed: [welktxef-d931887-021]

TASK [Upload application] ******************************************************
changed: [welktxef-d931887-021]

TASK [Check if application is uploaded] ****************************************
changed: [welktxef-d931887-021]

TASK [Copy application overrides to the subcloud] ******************************
changed: [welktxef-d931887-021]

TASK [Apply application overrides] *********************************************
changed: [welktxef-d931887-021]

TASK [Remove override file] ****************************************************
changed: [welktxef-d931887-021]

TASK [Apply application] *******************************************************
changed: [welktxef-d931887-021]

TASK [Check if application is applied] *****************************************
FAILED - RETRYING: Check if application is applied (12 retries left).
changed: [welktxef-d931887-021]

PLAY RECAP *********************************************************************
welktxef-d931887-021       : ok=11   changed=11   unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./verify-subcloud-ptp_notification_$(date "+%Y%m%d%H%M%S").log \
> ansible all --inventory subclouds --ask-pass --user XXXXXX --module-name shell \
> --args "kubectl --kubeconfig /etc/kubernetes/admin.conf get pods \
> -l app=ptp-notification -n notification; \
> kubectl --kubeconfig /etc/kubernetes/admin.conf get pods \
> -A -l "app=ptp-notification" -o \
> jsonpath="{..image}" | tr -s '[[:space:]]' '\n' | sort | uniq"
SSH password:
XXXXXX | CHANGED | rc=0 >>
NAME                         READY   STATUS    RESTARTS   AGE
ptp-ptp-notification-n64lk   3/3     Running   0          100s
registry.local:9001/docker.io/rabbitmq:3.8.11-management
registry.local:9001/docker.io/starlingx/locationservice-base:stx.5.0-v1.0.1
registry.local:9001/docker.io/starlingx/notificationservice-base:stx.6.0-v1.0.7

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./metrics-server-upgrade_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook --inventory subclouds --ask-pass --user XXXXXX app-upgrade.yaml \
> --extra-vars="application=metrics-server" \
> 0</dev/null
SSH password:

XXXXXX [all] *********************************************************************

TASK [Copy application overrides to the subcloud] ******************************
skipping: [welktxef-d931887-021]

TASK [Apply application overrides] *********************************************
skipping: [welktxef-d931887-021]

TASK [Remove override file] ****************************************************
skipping: [welktxef-d931887-021]

TASK [Retrieve latest application version] *************************************
changed: [welktxef-d931887-021]

TASK [Upgrade application] *****************************************************
fatal: [welktxef-d931887-021]: FAILED! => {"changed": true, "cmd": "source /etc/platform/openrc; system application-update --reuse-user-overrides true /usr/local/share/applications/helm/metrics-server-21.12-9.tgz", "delta": "0:00:02.206107", "end": "2023-09-13 21:45:39.408625", "msg": "non-zero return code", "rc": 1, "start": "2023-09-13 21:45:37.202518", "stderr": "Application-update rejected: application not found.", "stderr_lines": ["Application-update rejected: application not found."], "stdout": "", "stdout_lines": []}

PLAY RECAP *********************************************************************
welktxef-d931887-021       : ok=1    changed=1    unreachable=0    failed=1

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

no WRA installed, its ok.

skipping checknig if wra is runnign, as its  not

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ for subcloud in $(dcmanager subcloud-group list-subclouds ${subcloud_group} -f value -c name); do
> if [ "$(dcmanager subcloud show ${subcloud} -c software_version -f value)" != "21.12" ]; then
> echo "${subcloud} was not upgraded to 21.12"
> fi
> done
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./cleanup-old-pods_$(date "+%Y%m%d%H%M%S").log ansible-playbook --inventory subclouds --ask-pass --user XXXXXX cleanup-old-pods.yaml 0</dev/null
SSH password:

XXXXXX [all] *********************************************************************

TASK [Fetch pods in failed state] **********************************************
changed: [welktxef-d931887-021]

TASK [Delete failed pods] ******************************************************

PLAY RECAP *********************************************************************
welktxef-d931887-021       : ok=1    changed=1    unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./sanity_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook --inventory subclouds --extra-vars "scenario=after" \
> --ask-pass --ask-become-pass --user XXXXXX \
> sanity.yaml 0</dev/null
SSH password:
XXXXXX password[defaults to SSH password]:

PLAY [all] *********************************************************************

TASK [Gathering Facts] *********************************************************
ok: [welktxef-d931887-021]

TASK [Read in parameter file] **************************************************
ok: [welktxef-d931887-021]

TASK [set expected Fortville firmware version] *********************************
ok: [welktxef-d931887-021]

TASK [set expected N3000 firmware version] *************************************
ok: [welktxef-d931887-021]

TASK [create directory /home/XXXXXX/sanity] **********************************
ok: [welktxef-d931887-021 -> localhost]

TASK [delete existing file /home/XXXXXX/sanity/output_list] ******************
changed: [welktxef-d931887-021 -> localhost]

TASK [create file /home/XXXXXX/sanity/output_list] ***************************
changed: [welktxef-d931887-021 -> localhost]

TASK [get host patch status] ***************************************************
changed: [welktxef-d931887-021]

TASK [validate host patch status] **********************************************
skipping: [welktxef-d931887-021]

TASK [get host status] *********************************************************
changed: [welktxef-d931887-021]

TASK [validate host status] ****************************************************
skipping: [welktxef-d931887-021]

TASK [get current alarms] ******************************************************
changed: [welktxef-d931887-021]

TASK [validate current alarms] *************************************************
skipping: [welktxef-d931887-021]

TASK [get vim status] **********************************************************
changed: [welktxef-d931887-021]

TASK [validate vim status] *****************************************************
skipping: [welktxef-d931887-021]

TASK [calculate / partition expected usage] ************************************
changed: [welktxef-d931887-021]

TASK [validate / partition free space] *****************************************
skipping: [welktxef-d931887-021]

TASK [validate /opt/dc-vault partition free space] *****************************
skipping: [welktxef-d931887-021]

TASK [identify N3000 NICs] *****************************************************
changed: [welktxef-d931887-021]

TASK [get N3000 NICs firmware version] *****************************************

TASK [validate N3000 NICs firmware version] ************************************

TASK [get N3000 NICs MAC] ******************************************************

TASK [validate N3000 NICs MACs] ************************************************

TASK [identify Fortville NICs] *************************************************
changed: [welktxef-d931887-021]

TASK [get Fortville NICs firmware version] *************************************

TASK [validate Fortville NICs firmware version] ********************************

TASK [get Fortville NICs MAC] **************************************************

TASK [validate Fortville NICs MACs] ********************************************

TASK [identify accelerators] ***************************************************
changed: [welktxef-d931887-021]

TASK [retrieve device information] *********************************************
changed: [welktxef-d931887-021] => (item=pci_0000_51_00_0)

TASK [output device show information] ******************************************
ok: [welktxef-d931887-021] => (item=pci_0000_51_00_0) => {
    "msg": [
        "+-----------------------+-----------------------------------------------------------------------------+",
        "| Property              | Value                                                                       |",
        "+-----------------------+-----------------------------------------------------------------------------+",
        "| name                  | pci_0000_51_00_0                                                            |",
        "| address               | 0000:51:00.0                                                                |",
        "| class id              | 120001                                                                      |",
        "| vendor id             | 8086                                                                        |",
        "| device id             | 0d5c                                                                        |",
        "| class name            | Processing accelerators                                                     |",
        "| vendor name           | Intel Corporation                                                           |",
        "| device name           | Device 0d5c                                                                 |",
        "| numa_node             | 0                                                                           |",
        "| enabled               | True                                                                        |",
        "| sriov_totalvfs        | 16                                                                          |",
        "| sriov_numvfs          | 0                                                                           |",
        "| sriov_vfs_pci_address |                                                                             |",
        "| sriov_vf_pdevice_id   | None                                                                        |",
        "| extra_info            | {'expected_driver': None, 'expected_vf_driver': None, 'expected_numvfs': 0} |",
        "| created_at            | 2023-08-28T20:46:17.144032+00:00                                            |",
        "| updated_at            | 2023-09-12T23:33:27.285821+00:00                                            |",
        "| root_key              | None                                                                        |",
        "| revoked_key_ids       | None                                                                        |",
        "| boot_page             | None                                                                        |",
        "| bitstream_id          | None                                                                        |",
        "| bmc_build_version     | None                                                                        |",
        "| bmc_fw_version        | None                                                                        |",
        "| retimer_a_version     | None                                                                        |",
        "| retimer_b_version     | None                                                                        |",
        "| driver                | None                                                                        |",
        "| sriov_vf_driver       | None                                                                        |",
        "+-----------------------+-----------------------------------------------------------------------------+"
    ]
}

TASK [retrieve device information] *********************************************
changed: [welktxef-d931887-021] => (item=pci_0000_51_00_0)

TASK [output field information] ************************************************
ok: [welktxef-d931887-021] => (item=pci_0000_51_00_0) => {
    "msg": "0|{'expected_driver':None,'expected_vf_driver':None,'expected_numvfs':0}|None|None"
}

TASK [validate sriov_numvfs for Mount Bryce] ***********************************
skipping: [welktxef-d931887-021] => (item=pci_0000_51_00_0)

TASK [validate driver and sriov_vf_driver fields] ******************************
skipping: [welktxef-d931887-021] => (item=pci_0000_51_00_0)

TASK [validate extra_info field] ***********************************************
skipping: [welktxef-d931887-021] => (item=pci_0000_51_00_0)

TASK [get pod status] **********************************************************
changed: [welktxef-d931887-021]

TASK [validate pod status] *****************************************************
changed: [welktxef-d931887-021 -> localhost]

TASK [get system applications] *************************************************
changed: [welktxef-d931887-021]

TASK [validate system applications] ********************************************
skipping: [welktxef-d931887-021] => (item=cert-manager:21.12-28)
skipping: [welktxef-d931887-021] => (item=nginx-ingress-controller:21.12-18)
skipping: [welktxef-d931887-021] => (item=oidc-auth-apps:21.12-61)
skipping: [welktxef-d931887-021] => (item=platform-integ-apps:21.12-46)

PLAY RECAP *********************************************************************
welktxef-d931887-021       : ok=22   changed=15   unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ cat /home/XXXXXX/sanity/output_list
welktxef-d931887-021 - check pod status
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$


```



### Upgrade activites are complete.  We stopped as post-deployment scripts where not ran, so caused issues with some of the upgrades.
### however for this testing, which we need to validate the deployment with new bmc, that has been done, and was successful with the WRCP rebuild of the subcloud

### Test is considered succesful for BMC .43 21.05p6 upgrade to 21.12p10.


