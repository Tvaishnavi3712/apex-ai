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
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ system show
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
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ fm alarm-list
+----------+------------------------------------------------------------+-----------------------+----------+---------------+
| Alarm ID | Reason Text                                                | Entity ID             | Severity | Time Stamp    |
+----------+------------------------------------------------------------+-----------------------+----------+---------------+
| 280.002  | welktxef-d931887-021 patching sync_status is out-of-sync   | subcloud=             | major    | 2023-10-24T16 |
|          |                                                            | welktxef-d931887-021. |          | :34:44.017908 |
|          |                                                            | resource=patching     |          |               |
|          |                                                            |                       |          |               |
| 280.002  | welktxef-d931856-008 patching sync_status is out-of-sync   | subcloud=             | major    | 2023-10-24T16 |
|          |                                                            | welktxef-d931856-008. |          | :34:43.816885 |
|          |                                                            | resource=patching     |          |               |
|          |                                                            |                       |          |               |
| 280.002  | welktxef-d931856-008 kubernetes sync_status is out-of-sync | subcloud=             | major    | 2023-10-24T01 |
|          |                                                            | welktxef-d931856-008. |          | :14:42.655342 |
|          |                                                            | resource=kubernetes   |          |               |
|          |                                                            |                       |          |               |
| 280.002  | welktxef-d931887-021 kubernetes sync_status is out-of-sync | subcloud=             | major    | 2023-10-24T01 |
|          |                                                            | welktxef-d931887-021. |          | :14:42.554967 |
|          |                                                            | resource=kubernetes   |          |               |
|          |                                                            |                       |          |               |
| 280.002  | welktxef-d931856-008 load sync_status is out-of-sync       | subcloud=             | major    | 2023-10-23T23 |
|          |                                                            | welktxef-d931856-008. |          | :32:43.676881 |
|          |                                                            | resource=load         |          |               |
|          |                                                            |                       |          |               |
| 280.002  | welktxef-d931887-021 load sync_status is out-of-sync       | subcloud=             | major    | 2023-10-23T23 |
|          |                                                            | welktxef-d931887-021. |          | :32:43.276233 |
|          |                                                            | resource=load         |          |               |
|          |                                                            |                       |          |               |
+----------+------------------------------------------------------------+-----------------------+----------+---------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ system application-list
+--------------------------+----------+-----------------------------------+-------------------------+----------+-----------------------------+
| application              | version  | manifest name                     | manifest file           | status   | progress                    |
+--------------------------+----------+-----------------------------------+-------------------------+----------+-----------------------------+
| cert-manager             | 21.12-28 | cert-manager-manifest             | certmanager-manifest.   | applied  | completed                   |
|                          |          |                                   | yaml                    |          |                             |
|                          |          |                                   |                         |          |                             |
| nginx-ingress-controller | 21.12-18 | nginx-ingress-controller-manifest | nginx_ingress_controlle | applied  | Application update from     |
|                          |          |                                   | r_manifest.yaml         |          | version 21.05-16 to version |
|                          |          |                                   |                         |          | 21.12-18 completed.         |
|                          |          |                                   |                         |          |                             |
| oidc-auth-apps           | 21.12-61 | oidc-auth-manifest                | manifest.yaml           | applied  | completed                   |
| platform-integ-apps      | 21.12-46 | platform-integration-manifest     | manifest.yaml           | uploaded | completed                   |
| rook-ceph-apps           | 1.0-5    | rook-ceph-manifest                | manifest.yaml           | uploaded | completed                   |
+--------------------------+----------+-----------------------------------+-------------------------+----------+-----------------------------+
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

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ dcmanager subcloud list
+----+----------------------+------------+--------------+---------------+-------------+
| id | name                 | management | availability | deploy status | sync        |
+----+----------------------+------------+--------------+---------------+-------------+
|  5 | welktxef-d931887-021 | managed    | online       | complete      | out-of-sync |
|  6 | welktxef-d931856-008 | managed    | online       | complete      | out-of-sync |
+----+----------------------+------------+--------------+---------------+-------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ dcmanager subcloud show welktxef-d931887-021
+-----------------------------+---------------------------------+
| Field                       | Value                           |
+-----------------------------+---------------------------------+
| id                          | 5                               |
| name                        | welktxef-d931887-021            |
| description                 | Wind River Cloud Platform 21.05 |
| location                    | welktxef-d931887-021            |
| software_version            | 21.05                           |
| management                  | managed                         |
| availability                | online                          |
| deploy_status               | complete                        |
| management_subnet           | 2607:f160:10:809f::/64          |
| management_start_ip         | 2607:f160:10:809f:ce:40a::      |
| management_end_ip           | 2607:f160:10:809f:ce:40a:0:f    |
| management_gateway_ip       | 2607:f160:10:809f:ce:28::       |
| systemcontroller_gateway_ip | 2607:f160:0:3042:cd:28::        |
| group_id                    | 1                               |
| created_at                  | 2023-10-02 19:29:24.044196      |
| updated_at                  | 2023-10-23 18:30:26.400473      |
| dc-cert_sync_status         | in-sync                         |
| firmware_sync_status        | in-sync                         |
| identity_sync_status        | in-sync                         |
| kubernetes_sync_status      | out-of-sync                     |
| kube-rootca_sync_status     | in-sync                         |
| load_sync_status            | out-of-sync                     |
| patching_sync_status        | out-of-sync                     |
| platform_sync_status        | in-sync                         |
+-----------------------------+---------------------------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ dcmanager subcloud show welktxef-d931856-008
+-----------------------------+---------------------------------+
| Field                       | Value                           |
+-----------------------------+---------------------------------+
| id                          | 6                               |
| name                        | welktxef-d931856-008            |
| description                 | Wind River Cloud Platform 21.05 |
| location                    | welktxef-d931856-008            |
| software_version            | 21.05                           |
| management                  | managed                         |
| availability                | online                          |
| deploy_status               | complete                        |
| management_subnet           | 2607:f160:10:80bb::/64          |
| management_start_ip         | 2607:f160:10:80bb:ce:40a::      |
| management_end_ip           | 2607:f160:10:80bb:ce:40a:0:f    |
| management_gateway_ip       | 2607:f160:10:80bb:ce:23::       |
| systemcontroller_gateway_ip | 2607:f160:0:3042:cd:28::        |
| group_id                    | 1                               |
| created_at                  | 2023-10-02 21:56:39.788890      |
| updated_at                  | 2023-10-10 18:19:31.217724      |
| dc-cert_sync_status         | in-sync                         |
| firmware_sync_status        | in-sync                         |
| identity_sync_status        | in-sync                         |
| kubernetes_sync_status      | out-of-sync                     |
| kube-rootca_sync_status     | in-sync                         |
| load_sync_status            | out-of-sync                     |
| patching_sync_status        | out-of-sync                     |
| platform_sync_status        | in-sync                         |
+-----------------------------+---------------------------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
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

### Following Wrapper MOP 21.12p10 to install subclouds

### 21.12P10 upgrade mop 4 Subclouds Starting at section 3

```log
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ source /etc/platform/openrc
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ cd /opt/platform-backup/upgrade/wrcp-21.12-upgrade
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ sudo show-certs.sh | grep -E '^\s+Residual Time'
Password:
	 XXXXXX Time	:  374d
	 Residual Time	:  339d
	 Residual Time	:  154d
	 Residual Time	:  2555d
	 Residual Time	:  4252d
	 Residual Time	:  2556d
	 Residual Time	:  1799d
	 Residual Time	:  154d
	 Residual Time	:  3649d
	 Residual Time	:  365d
	 Residual Time	:  365d
	 Residual Time	:  365d
	 Residual Time	:  340d
	 Residual Time	:  4252d
	 Residual Time	:  4252d
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
| updated_at             | 2023-10-24 16:45:19.887605 |
+------------------------+----------------------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ echo '[subclouds]' > subclouds
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ dcmanager subcloud-group list-subclouds ${subcloud_group} -c name -f value >> subclouds
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ for subcloud in $(sed -n '/subclouds/ { :a; n; p; ba; }' < subclouds); do
> echo ${subcloud}
> dcmanager subcloud show ${subcloud} | \
> grep sync_status | \
> grep -E -v "in-sync|load_sync|kubernetes_sync|firmware_sync|dc-cert_sync";
> done
welktxef-d931887-021
| patching_sync_status        | out-of-sync                     |
welktxef-d931856-008
| patching_sync_status        | out-of-sync                     |
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

```

### need to commit patches on subcloud, missed this step in the wrapper mop

```log 
====================================================================
         SYSTEM: welktxef-d931856-008
====================================================================

controller-0:~$ source /etc/platform/openrc
--alldmin@controller-0 ~(keystone_admin)]$ sudo sw-patch commit --release 21.05
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
[XXXXXX@controller-0 ~(keystone_admin)]$
====================================================================
         SYSTEM: welktxef-d931887-021
====================================================================

controller-0:~$ source /etc/platform/openrc
--alldmin@controller-0 ~(keystone_admin)]$ sudo sw-patch commit --release 21.05
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
[XXXXXX@controller-0 ~(keystone_admin)]$

```

### waiting for controller to catch up with status of subcloud patch status

```log
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ for subcloud in $(sed -n '/subclouds/ { :a; n; p; ba; }' < subclouds); do echo ${subcloud}; dcmanager subcloud show ${subcloud} | grep sync_status | grep -E -v "in-sync|load_sync|kubernetes_sync|firmware_sync|dc-cert_sync"; done
welktxef-d931887-021
welktxef-d931856-008
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

```

### subcloud status fixed, continuing

```log
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ for subcloud in $(sed -n '/subclouds/ { :a; n; p; ba; }' < subclouds); do
> echo ${subcloud}
> dcmanager subcloud show ${subcloud} | \
> grep sync_status | \
> grep -E -v "in-sync|load_sync|kubernetes_sync|firmware_sync|dc-cert_sync";
> done
welktxef-d931887-021
welktxef-d931856-008
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ names=$(dcmanager subcloud-group list-subclouds ${subcloud_group} --format value \
> --column name | xargs printf "'%s'," | head -c -1)

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
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931887-021, welktxef-d931856-008
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931887-021, welktxef-d931856-008
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931887-021, welktxef-d931856-008
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931887-021, welktxef-d931856-008
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931887-021, welktxef-d931856-008
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931887-021, welktxef-d931856-008
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931887-021, welktxef-d931856-008
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931887-021, welktxef-d931856-008
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931887-021, welktxef-d931856-008
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931887-021, welktxef-d931856-008
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931887-021, welktxef-d931856-008
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931887-021, welktxef-d931856-008
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931887-021, welktxef-d931856-008
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931887-021, welktxef-d931856-008
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931887-021, welktxef-d931856-008
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931887-021, welktxef-d931856-008
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931887-021, welktxef-d931856-008
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931887-021, welktxef-d931856-008
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931887-021, welktxef-d931856-008

TASK [Retrieve list of docker.elastic.co/beats/filebeat tags] ******************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Loop over all docker.elastic.co/beats/filebeat tags] *********************

TASK [Retrieve list of docker.elastic.co/beats/filebeat-oss tags] **************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Loop over all docker.elastic.co/beats/filebeat-oss tags] *****************

TASK [Retrieve list of docker.elastic.co/beats/metricbeat tags] ****************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Loop over all docker.elastic.co/beats/metricbeat tags] *******************

TASK [Retrieve list of docker.elastic.co/beats/metricbeat-oss tags] ************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Loop over all docker.elastic.co/beats/metricbeat-oss tags] ***************

TASK [Retrieve list of docker.elastic.co/elasticsearch/elasticsearch tags] *****
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Loop over all docker.elastic.co/elasticsearch/elasticsearch tags] ********

TASK [Retrieve list of docker.elastic.co/elasticsearch/elasticsearch-oss tags] ***
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Loop over all docker.elastic.co/elasticsearch/elasticsearch-oss tags] ****

TASK [Retrieve list of docker.elastic.co/kibana/kibana tags] *******************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Loop over all docker.elastic.co/kibana/kibana tags] **********************

TASK [Retrieve list of docker.elastic.co/kibana/kibana-oss tags] ***************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Loop over all docker.elastic.co/kibana/kibana-oss tags] ******************

TASK [Retrieve list of docker.elastic.co/logstash/logstash tags] ***************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Loop over all docker.elastic.co/logstash/logstash tags] ******************

TASK [Retrieve list of docker.elastic.co/logstash/logstash-oss tags] ***********
changed: [welktxef-d931887-021]
changed: [welktxef-d931856-008]

TASK [Loop over all docker.elastic.co/logstash/logstash-oss tags] **************

TASK [Retrieve list of quay.io/coreos/kube-state-metrics tags] *****************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Loop over all quay.io/coreos/kube-state-metrics tags] ********************

TASK [Retrieve list of quay.io/kubernetes-ingress-controller/nginx-ingress-controller tags] ***
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Loop over all quay.io/kubernetes-ingress-controller/nginx-ingress-controller tags] ***

TASK [Retrieve list of docker.io/wind-river/elastic-services tags] *************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Loop over all docker.io/wind-river/elastic-services tags] ****************

TASK [Retrieve list of docker.io/wind-river/wra-kibana tags] *******************
changed: [welktxef-d931887-021]
changed: [welktxef-d931856-008]

TASK [Loop over all docker.io/wind-river/wra-kibana tags] **********************

TASK [Retrieve list of docker.io/wind-river/wra-metricbeat tags] ***************
changed: [welktxef-d931887-021]
changed: [welktxef-d931856-008]

TASK [Loop over all docker.io/wind-river/wra-metricbeat tags] ******************

TASK [Retrieve list of docker.io/wind-river/wra-elasticsearch tags] ************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Loop over all docker.io/wind-river/wra-elasticsearch tags] ***************

TASK [Retrieve list of docker.io/wind-river/wra-logstash tags] *****************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Loop over all docker.io/wind-river/wra-logstash tags] ********************

TASK [Retrieve list of docker.io/wind-river/cloud-platform-deployment-manager tags] ***
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Loop over all docker.io/wind-river/cloud-platform-deployment-manager tags] ***
changed: [welktxef-d931856-008] => (item=WRCP_21.05)
changed: [welktxef-d931887-021] => (item=WRCP_21.05)

TASK [Retrieve list of docker.io/starlingx/k8s-cni-sriov tags] *****************
changed: [welktxef-d931887-021]
changed: [welktxef-d931856-008]

TASK [Loop over all docker.io/starlingx/k8s-cni-sriov tags] ********************
changed: [welktxef-d931856-008] => (item=stx.5.0-v2.6-7-gb18123d8)
changed: [welktxef-d931887-021] => (item=stx.5.0-v2.6-7-gb18123d8)

TASK [Garbage collect] *********************************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

PLAY RECAP *********************************************************************
welktxef-d931856-008       : ok=41   changed=22   unreachable=0    failed=0
welktxef-d931887-021       : ok=41   changed=22   unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./cleanup-unused-images_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook --inventory subclouds --ask-pass --user XXXXXX \
> cleanup-unused-images.yaml 0</dev/null
SSH password:

XXXXXX [all] *********************************************************************

TASK [Retrieve application info output] ****************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Save application namespace and image as fact] ****************************
skipping: [welktxef-d931887-021]
skipping: [welktxef-d931856-008]

TASK [Retrieve application tag output] *****************************************
skipping: [welktxef-d931887-021]
skipping: [welktxef-d931856-008]

TASK [Save application tag as fact] ********************************************
skipping: [welktxef-d931887-021]
skipping: [welktxef-d931856-008]

TASK [Remove unused images] ****************************************************
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-unused-images.yaml for welktxef-d931856-008, welktxef-d931887-021
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-unused-images.yaml for welktxef-d931856-008, welktxef-d931887-021
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-unused-images.yaml for welktxef-d931856-008, welktxef-d931887-021
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-unused-images.yaml for welktxef-d931856-008, welktxef-d931887-021
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-unused-images.yaml for welktxef-d931856-008, welktxef-d931887-021
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-unused-images.yaml for welktxef-d931856-008, welktxef-d931887-021
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-unused-images.yaml for welktxef-d931856-008, welktxef-d931887-021
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-unused-images.yaml for welktxef-d931856-008, welktxef-d931887-021
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-unused-images.yaml for welktxef-d931856-008, welktxef-d931887-021
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-unused-images.yaml for welktxef-d931856-008, welktxef-d931887-021
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-unused-images.yaml for welktxef-d931856-008, welktxef-d931887-021
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-unused-images.yaml for welktxef-d931856-008, welktxef-d931887-021
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-unused-images.yaml for welktxef-d931856-008, welktxef-d931887-021
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-unused-images.yaml for welktxef-d931856-008, welktxef-d931887-021

TASK [Retrieve list of vzw-adpf-cmp tags] **************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Loop over all vzw-adpf-cmp tags] *****************************************

TASK [Retrieve list of vzw-adpf-dip tags] **************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Loop over all vzw-adpf-dip tags] *****************************************

TASK [Retrieve list of vzw-adpf-dmp tags] **************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Loop over all vzw-adpf-dmp tags] *****************************************

TASK [Retrieve list of vzw-adpf-dpp tags] **************************************
changed: [welktxef-d931887-021]
changed: [welktxef-d931856-008]

TASK [Loop over all vzw-adpf-dpp tags] *****************************************

TASK [Retrieve list of vzw-adpf-init tags] *************************************
changed: [welktxef-d931887-021]
changed: [welktxef-d931856-008]

TASK [Loop over all vzw-adpf-init tags] ****************************************

TASK [Retrieve list of vzw-adpf-pmp tags] **************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Loop over all vzw-adpf-pmp tags] *****************************************

TASK [Retrieve list of vzw-adpf-rmp tags] **************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Loop over all vzw-adpf-rmp tags] *****************************************

TASK [Retrieve list of vzw-uadpf-cmp tags] *************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Loop over all vzw-uadpf-cmp tags] ****************************************

TASK [Retrieve list of vzw-uadpf-dip tags] *************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Loop over all vzw-uadpf-dip tags] ****************************************

TASK [Retrieve list of vzw-uadpf-dmp tags] *************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Loop over all vzw-uadpf-dmp tags] ****************************************

TASK [Retrieve list of vzw-uadpf-dpp tags] *************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Loop over all vzw-uadpf-dpp tags] ****************************************

TASK [Retrieve list of vzw-uadpf-init tags] ************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Loop over all vzw-uadpf-init tags] ***************************************

TASK [Retrieve list of vzw-uadpf-pmp tags] *************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Loop over all vzw-uadpf-pmp tags] ****************************************

TASK [Retrieve list of vzw-uadpf-rmp tags] *************************************
changed: [welktxef-d931887-021]
changed: [welktxef-d931856-008]

TASK [Loop over all vzw-uadpf-rmp tags] ****************************************

TASK [Garbage collect] *********************************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

PLAY RECAP *********************************************************************
welktxef-d931856-008       : ok=30   changed=16   unreachable=0    failed=0
welktxef-d931887-021       : ok=30   changed=16   unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

```

### no designer patches, continuing

```log
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
ok: [welktxef-d931856-008]

TASK [common/load-images-information : Get the list of kubernetes images] ******
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [common/load-images-information : set_fact] *******************************
ok: [welktxef-d931887-021]
ok: [welktxef-d931856-008]

TASK [common/load-images-information : Read in system images list] *************
ok: [welktxef-d931887-021]
ok: [welktxef-d931856-008]

TASK [common/load-images-information : Check if additional image config file exists] ***
ok: [welktxef-d931856-008]
ok: [welktxef-d931887-021]

TASK [common/load-images-information : Read in additional system images list(s) in localhost] ***
skipping: [welktxef-d931887-021]
skipping: [welktxef-d931856-008]

TASK [common/load-images-information : Create a temporary file on remote] ******
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [common/load-images-information : Fetch the additional images config in case the playbook is executed remotely] ***
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [common/load-images-information : Read in additional system images list(s) fetched from remote] ***
ok: [welktxef-d931887-021]
ok: [welktxef-d931856-008]

TASK [common/load-images-information : Remove the temporary file on remote] ****
changed: [welktxef-d931887-021 -> welktxef-d931887-021]
changed: [welktxef-d931856-008 -> welktxef-d931856-008]

TASK [common/load-images-information : Remove override temp file on Ansible control host] ***
changed: [welktxef-d931887-021 -> localhost]
changed: [welktxef-d931856-008 -> localhost]

TASK [common/load-images-information : Categorize system images] ***************
ok: [welktxef-d931887-021]
ok: [welktxef-d931856-008]

TASK [common/load-images-information : Append additional static images if provisioned] ***
ok: [welktxef-d931887-021] => (item={'key': u'deploy_manager_img', 'value': u'docker.io/wind-river/cloud-platform-deployment-manager:WRCP_21.05'})
ok: [welktxef-d931856-008] => (item={'key': u'deploy_manager_img', 'value': u'docker.io/wind-river/cloud-platform-deployment-manager:WRCP_21.05'})
ok: [welktxef-d931887-021] => (item={'key': u'kube_rbac_proxy_img', 'value': u'gcr.io/kubebuilder/kube-rbac-proxy:v0.4.0'})
ok: [welktxef-d931856-008] => (item={'key': u'kube_rbac_proxy_img', 'value': u'gcr.io/kubebuilder/kube-rbac-proxy:v0.4.0'})

TASK [common/load-images-information : Append RVMC image for a DC system controller] ***
skipping: [welktxef-d931887-021]
skipping: [welktxef-d931856-008]

TASK [common/load-images-information : Append additional static images for a DC system controller if provisioned] ***
skipping: [welktxef-d931887-021] => (item={'key': u'rbd_provisioner_img', 'value': u'quay.io/external_storage/rbd-provisioner:v2.1.1-k8s1.11'})
skipping: [welktxef-d931856-008] => (item={'key': u'rbd_provisioner_img', 'value': u'quay.io/external_storage/rbd-provisioner:v2.1.1-k8s1.11'})
skipping: [welktxef-d931887-021] => (item={'key': u'ceph_config_helper_img', 'value': u'docker.io/starlingx/ceph-config-helper:v1.15.0'})
skipping: [welktxef-d931856-008] => (item={'key': u'ceph_config_helper_img', 'value': u'docker.io/starlingx/ceph-config-helper:v1.15.0'})

TASK [Set platform images list] ************************************************
ok: [welktxef-d931887-021]
ok: [welktxef-d931856-008]

TASK [Create a temporary file on remote] ***************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Correct permissions for temporary file on remote] ************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Save list of local registry images excluding apps images to file] ********
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Read file] ***************************************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Load list of local registry images from file] ****************************
ok: [welktxef-d931887-021]
ok: [welktxef-d931856-008]

TASK [Subtract platform images from local registry images] *********************
ok: [welktxef-d931887-021]
ok: [welktxef-d931856-008]

TASK [Append local registry host:port to image names] **************************
ok: [welktxef-d931887-021]
ok: [welktxef-d931856-008]

TASK [debug] *******************************************************************
ok: [welktxef-d931887-021] => {
    "image_list": [
        "registry.local:9001/quay.io/airshipit/armada:8a1638098f88d92bf799ef4934abe569789b885e-ubuntu_bionic",
        "registry.local:9001/gcr.io/kubernetes-helm/tiller:v2.16.1",
        "registry.local:9001/docker.io/starlingx/n3000-opae:stx.4.0-v1.0.0",
        "registry.local:9001/docker.io/starlingx/notificationclient-base:stx.5.0-v1.0.4"
    ]
}
ok: [welktxef-d931856-008] => {
    "image_list": [
        "registry.local:9001/quay.io/airshipit/armada:8a1638098f88d92bf799ef4934abe569789b885e-ubuntu_bionic",
        "registry.local:9001/gcr.io/kubernetes-helm/tiller:v2.16.1",
        "registry.local:9001/docker.io/starlingx/n3000-opae:stx.4.0-v1.0.0",
        "registry.local:9001/docker.io/starlingx/notificationclient-base:stx.5.0-v1.0.4"
    ]
}

TASK [Log in to local registry] ************************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Pull images from local registry to docker filesystem] ********************
changed: [welktxef-d931856-008] => (item=registry.local:9001/quay.io/airshipit/armada:8a1638098f88d92bf799ef4934abe569789b885e-ubuntu_bionic)
changed: [welktxef-d931887-021] => (item=registry.local:9001/quay.io/airshipit/armada:8a1638098f88d92bf799ef4934abe569789b885e-ubuntu_bionic)
changed: [welktxef-d931856-008] => (item=registry.local:9001/gcr.io/kubernetes-helm/tiller:v2.16.1)
changed: [welktxef-d931887-021] => (item=registry.local:9001/gcr.io/kubernetes-helm/tiller:v2.16.1)
changed: [welktxef-d931856-008] => (item=registry.local:9001/docker.io/starlingx/n3000-opae:stx.4.0-v1.0.0)
changed: [welktxef-d931887-021] => (item=registry.local:9001/docker.io/starlingx/n3000-opae:stx.4.0-v1.0.0)
changed: [welktxef-d931856-008] => (item=registry.local:9001/docker.io/starlingx/notificationclient-base:stx.5.0-v1.0.4)
changed: [welktxef-d931887-021] => (item=registry.local:9001/docker.io/starlingx/notificationclient-base:stx.5.0-v1.0.4)

TASK [Set format parameter for docker inspect to retrieve only the size] *******
ok: [welktxef-d931887-021]
ok: [welktxef-d931856-008]

TASK [Get docker images size in bytes] *****************************************
changed: [welktxef-d931856-008] => (item=registry.local:9001/quay.io/airshipit/armada:8a1638098f88d92bf799ef4934abe569789b885e-ubuntu_bionic)
changed: [welktxef-d931887-021] => (item=registry.local:9001/quay.io/airshipit/armada:8a1638098f88d92bf799ef4934abe569789b885e-ubuntu_bionic)
changed: [welktxef-d931856-008] => (item=registry.local:9001/gcr.io/kubernetes-helm/tiller:v2.16.1)
changed: [welktxef-d931887-021] => (item=registry.local:9001/gcr.io/kubernetes-helm/tiller:v2.16.1)
changed: [welktxef-d931856-008] => (item=registry.local:9001/docker.io/starlingx/n3000-opae:stx.4.0-v1.0.0)
changed: [welktxef-d931856-008] => (item=registry.local:9001/docker.io/starlingx/notificationclient-base:stx.5.0-v1.0.4)
changed: [welktxef-d931887-021] => (item=registry.local:9001/docker.io/starlingx/n3000-opae:stx.4.0-v1.0.0)
changed: [welktxef-d931887-021] => (item=registry.local:9001/docker.io/starlingx/notificationclient-base:stx.5.0-v1.0.4)

TASK [Parse docker images size] ************************************************
ok: [welktxef-d931887-021] => (item=registry.local:9001/quay.io/airshipit/armada:8a1638098f88d92bf799ef4934abe569789b885e-ubuntu_bionic, 457539381 bytes)
ok: [welktxef-d931856-008] => (item=registry.local:9001/quay.io/airshipit/armada:8a1638098f88d92bf799ef4934abe569789b885e-ubuntu_bionic, 457539381 bytes)
ok: [welktxef-d931887-021] => (item=registry.local:9001/gcr.io/kubernetes-helm/tiller:v2.16.1, 91160017 bytes)
ok: [welktxef-d931856-008] => (item=registry.local:9001/gcr.io/kubernetes-helm/tiller:v2.16.1, 91160017 bytes)
ok: [welktxef-d931887-021] => (item=registry.local:9001/docker.io/starlingx/n3000-opae:stx.4.0-v1.0.0, 506492391 bytes)
ok: [welktxef-d931856-008] => (item=registry.local:9001/docker.io/starlingx/n3000-opae:stx.4.0-v1.0.0, 506492391 bytes)
ok: [welktxef-d931887-021] => (item=registry.local:9001/docker.io/starlingx/notificationclient-base:stx.5.0-v1.0.4, 829010683 bytes)
ok: [welktxef-d931856-008] => (item=registry.local:9001/docker.io/starlingx/notificationclient-base:stx.5.0-v1.0.4, 829010683 bytes)

TASK [debug] *******************************************************************
ok: [welktxef-d931887-021] => {
    "docker_images_size": "1884202472"
}
ok: [welktxef-d931856-008] => {
    "docker_images_size": "1884202472"
}

TASK [Remove pulled images] ****************************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Scale to KiB and reserve 5% for docker metadata inside exported archive] ***
ok: [welktxef-d931887-021]
ok: [welktxef-d931856-008]

TASK [Determine available space in /opt/platform-backup] ***********************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Fail if there is not enough free space to create docker images backup archive] ***
skipping: [welktxef-d931887-021]
skipping: [welktxef-d931856-008]

TASK [Remove the temporary file from remote] ***********************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

PLAY RECAP *********************************************************************
welktxef-d931856-008       : ok=31   changed=15   unreachable=0    failed=0
welktxef-d931887-021       : ok=31   changed=15   unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./sanity_$(date "+%Y%m%d%H%M%S").log ansible-playbook --inventory subclouds --extra-vars "scenario=before" --ask-pass --ask-become-pass --user XXXXXX pre-deployment-subclouds.yaml 0</dev/null
SSH password:
XXXXXX password[defaults to SSH password]:

PLAY [all] *********************************************************************

TASK [Gathering Facts] *********************************************************
ok: [welktxef-d931887-021]
ok: [welktxef-d931856-008]

TASK [Read in parameter file] **************************************************
ok: [welktxef-d931887-021]
ok: [welktxef-d931856-008]

TASK [set expected Fortville firmware version] *********************************
ok: [welktxef-d931887-021]
ok: [welktxef-d931856-008]

TASK [set expected N3000 firmware version] *************************************
ok: [welktxef-d931887-021]
ok: [welktxef-d931856-008]

TASK [create directory /home/XXXXXX/sanity] **********************************
ok: [welktxef-d931856-008 -> localhost]
ok: [welktxef-d931887-021 -> localhost]

TASK [delete existing file /home/XXXXXX/sanity/output_list] ******************
changed: [welktxef-d931887-021 -> localhost]
ok: [welktxef-d931856-008 -> localhost]

TASK [create file /home/XXXXXX/sanity/output_list] ***************************
changed: [welktxef-d931887-021 -> localhost]
changed: [welktxef-d931856-008 -> localhost]

TASK [get host patch status] ***************************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [validate host patch status] **********************************************
skipping: [welktxef-d931887-021]
skipping: [welktxef-d931856-008]

TASK [get host status] *********************************************************
changed: [welktxef-d931887-021]
changed: [welktxef-d931856-008]

TASK [validate host status] ****************************************************
skipping: [welktxef-d931887-021]
skipping: [welktxef-d931856-008]

TASK [get current alarms] ******************************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [validate current alarms] *************************************************
skipping: [welktxef-d931887-021]
skipping: [welktxef-d931856-008]

TASK [get vim status] **********************************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [validate vim status] *****************************************************
skipping: [welktxef-d931887-021]
skipping: [welktxef-d931856-008]

TASK [calculate / partition expected usage] ************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [validate / partition free space] *****************************************
skipping: [welktxef-d931887-021]
skipping: [welktxef-d931856-008]

TASK [validate /opt/dc-vault partition free space] *****************************
skipping: [welktxef-d931887-021]
skipping: [welktxef-d931856-008]

TASK [identify N3000 NICs] *****************************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [get N3000 NICs firmware version] *****************************************

TASK [validate N3000 NICs firmware version] ************************************

TASK [get N3000 NICs MAC] ******************************************************

TASK [validate N3000 NICs MACs] ************************************************

TASK [identify Fortville NICs] *************************************************
changed: [welktxef-d931887-021]
changed: [welktxef-d931856-008]

TASK [get Fortville NICs firmware version] *************************************

TASK [validate Fortville NICs firmware version] ********************************

TASK [get Fortville NICs MAC] **************************************************

TASK [validate Fortville NICs MACs] ********************************************

TASK [identify accelerators] ***************************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [retrieve device information] *********************************************
changed: [welktxef-d931856-008] => (item=pci_0000_51_00_0)
changed: [welktxef-d931887-021] => (item=pci_0000_51_00_0)

TASK [output device show information] ******************************************
ok: [welktxef-d931887-021] => (item=pci_0000_51_00_0) => {
    "msg": [
        "+-----------------------+----------------------------------+",
        "| Property              | Value                            |",
        "+-----------------------+----------------------------------+",
        "| name                  | pci_0000_51_00_0                 |",
        "| address               | 0000:51:00.0                     |",
        "| class id              | 120001                           |",
        "| vendor id             | 8086                             |",
        "| device id             | 0d5c                             |",
        "| class name            | Processing accelerators          |",
        "| vendor name           | Intel Corporation                |",
        "| device name           | Device 0d5c                      |",
        "| numa_node             | 0                                |",
        "| enabled               | True                             |",
        "| sriov_totalvfs        | 16                               |",
        "| sriov_numvfs          | 1                                |",
        "| sriov_vfs_pci_address | 0000:52:00.0                     |",
        "| sriov_vf_pdevice_id   | 0d5d                             |",
        "| extra_info            | {'expected_numvfs': 1}           |",
        "| created_at            | 2023-10-02T19:59:39.799717+00:00 |",
        "| updated_at            | 2023-10-23T18:30:28.657909+00:00 |",
        "| root_key              | None                             |",
        "| revoked_key_ids       | None                             |",
        "| boot_page             | None                             |",
        "| bitstream_id          | None                             |",
        "| bmc_build_version     | None                             |",
        "| bmc_fw_version        | None                             |",
        "| driver                | igb_uio                          |",
        "| sriov_vf_driver       | igb_uio                          |",
        "+-----------------------+----------------------------------+"
    ]
}
ok: [welktxef-d931856-008] => (item=pci_0000_51_00_0) => {
    "msg": [
        "+-----------------------+----------------------------------+",
        "| Property              | Value                            |",
        "+-----------------------+----------------------------------+",
        "| name                  | pci_0000_51_00_0                 |",
        "| address               | 0000:51:00.0                     |",
        "| class id              | 120001                           |",
        "| vendor id             | 8086                             |",
        "| device id             | 0d5c                             |",
        "| class name            | Processing accelerators          |",
        "| vendor name           | Intel Corporation                |",
        "| device name           | Device 0d5c                      |",
        "| numa_node             | 0                                |",
        "| enabled               | True                             |",
        "| sriov_totalvfs        | 16                               |",
        "| sriov_numvfs          | 1                                |",
        "| sriov_vfs_pci_address | 0000:52:00.0                     |",
        "| sriov_vf_pdevice_id   | 0d5d                             |",
        "| extra_info            | {'expected_numvfs': 1}           |",
        "| created_at            | 2023-10-02T22:24:59.776788+00:00 |",
        "| updated_at            | 2023-10-10T18:19:32.190629+00:00 |",
        "| root_key              | None                             |",
        "| revoked_key_ids       | None                             |",
        "| boot_page             | None                             |",
        "| bitstream_id          | None                             |",
        "| bmc_build_version     | None                             |",
        "| bmc_fw_version        | None                             |",
        "| driver                | igb_uio                          |",
        "| sriov_vf_driver       | igb_uio                          |",
        "+-----------------------+----------------------------------+"
    ]
}

TASK [retrieve device information] *********************************************
changed: [welktxef-d931856-008] => (item=pci_0000_51_00_0)
changed: [welktxef-d931887-021] => (item=pci_0000_51_00_0)

TASK [output field information] ************************************************
ok: [welktxef-d931887-021] => (item=pci_0000_51_00_0) => {
    "msg": "1|{'expected_numvfs':1}|igb_uio|igb_uio"
}
ok: [welktxef-d931856-008] => (item=pci_0000_51_00_0) => {
    "msg": "1|{'expected_numvfs':1}|igb_uio|igb_uio"
}

TASK [validate sriov_numvfs for Mount Bryce] ***********************************
skipping: [welktxef-d931887-021] => (item=pci_0000_51_00_0)
skipping: [welktxef-d931856-008] => (item=pci_0000_51_00_0)

TASK [validate driver and sriov_vf_driver fields] ******************************
skipping: [welktxef-d931887-021] => (item=pci_0000_51_00_0)
skipping: [welktxef-d931856-008] => (item=pci_0000_51_00_0)

TASK [validate extra_info field] ***********************************************
skipping: [welktxef-d931887-021] => (item=pci_0000_51_00_0)
skipping: [welktxef-d931856-008] => (item=pci_0000_51_00_0)

TASK [get pod status] **********************************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [validate pod status] *****************************************************
skipping: [welktxef-d931887-021]
skipping: [welktxef-d931856-008]

TASK [get system applications] *************************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [validate system applications] ********************************************
skipping: [welktxef-d931887-021] => (item=cert-manager:21.05-17)
skipping: [welktxef-d931887-021] => (item=nginx-ingress-controller:21.05-16)
skipping: [welktxef-d931887-021] => (item=oidc-auth-apps:21.05-44)
skipping: [welktxef-d931887-021] => (item=platform-integ-apps:21.05-30)
skipping: [welktxef-d931856-008] => (item=cert-manager:21.05-17)
skipping: [welktxef-d931856-008] => (item=nginx-ingress-controller:21.05-16)
skipping: [welktxef-d931856-008] => (item=oidc-auth-apps:21.05-44)
skipping: [welktxef-d931856-008] => (item=platform-integ-apps:21.05-30)

PLAY [all] *********************************************************************

TASK [Gathering Facts] *********************************************************
ok: [welktxef-d931887-021]
ok: [welktxef-d931856-008]

TASK [validate /opt/platform-backup partition free space] **********************
skipping: [welktxef-d931887-021]
skipping: [welktxef-d931856-008]

TASK [validate /opt/platform-backup partition type] ****************************
skipping: [welktxef-d931887-021]
skipping: [welktxef-d931856-008]

TASK [Collect previous backups] ************************************************
ok: [welktxef-d931856-008]
ok: [welktxef-d931887-021]

TASK [Delete previous backups] *************************************************

TASK [Get /home size] **********************************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [validate /home size] *****************************************************
skipping: [welktxef-d931887-021]
skipping: [welktxef-d931856-008]

PLAY RECAP *********************************************************************
welktxef-d931856-008       : ok=24   changed=14   unreachable=0    failed=0
welktxef-d931887-021       : ok=24   changed=15   unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ cat /home/XXXXXX/sanity/output_list
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ for subcloud in $(sed -n '/subclouds/ { :a; n; p; ba; }' < subclouds); do
> echo ${subcloud}
> system --os-region-name ${subcloud} --os-endpoint-type admin application-show \
> --format value --column app_version wr-analytics | cut -d- -f1
> done
welktxef-d931887-021
application not found: wr-analytics
welktxef-d931856-008
application not found: wr-analytics
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./fix-backup-system_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook --inventory subclouds --ask-pass --ask-become-pass --user XXXXXX \
> fix-backup-system.yaml 0</dev/null
SSH password:
XXXXXX password[defaults to SSH password]:

PLAY [all] *********************************************************************

TASK [Add fail task to backup-system rescue block] *****************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

PLAY RECAP *********************************************************************
welktxef-d931856-008       : ok=1    changed=1    unreachable=0    failed=0
welktxef-d931887-021       : ok=1    changed=1    unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

```
### set MWAIT enable on subclouds

```log
[XXXXXX@vcpe-jumpserver ~]$ curl --globoff -L -w "\\n%{http_code} %{url_effective}\\n" -u XXXXXX:XXXXXX -k -H "Content-Type: application/json" -d '{"Attributes": {"PMS012": "Enable"}}' -X PATCH https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/Systems/Self/Bios/SD

204 https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/Systems/Self/Bios/SD
[XXXXXX@vcpe-jumpserver ~]$
[XXXXXX@vcpe-jumpserver ~]$ curl --globoff -L -w "\\n%{http_code} %{url_effective}\\n" -u XXXXXX:XXXXXX -k -H "Content-Type: application/json" -d '{"Attributes": {"PMS012": "Enable"}}' -X PATCH https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Systems/Self/Bios/SD

204 https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Systems/Self/Bios/SD
[XXXXXX@vcpe-jumpserver ~]$

```

### starting section 4 Deployment of Mop 4 subclouds

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
| created_at             | 2023-10-24T17:09:34.183632 |
| updated_at             | None                       |
+------------------------+----------------------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ dcmanager strategy-step list -c cloud -c stage -c state
+----------------------+-------+---------+
| cloud                | stage | state   |
+----------------------+-------+---------+
| welktxef-d931887-021 |     1 | initial |
| welktxef-d931856-008 |     1 | initial |
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
| created_at             | 2023-10-24T17:09:34.183632 |
| updated_at             | 2023-10-24T17:10:00.626340 |
+------------------------+----------------------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$


Every 15.0s: dcmanager strategy-step list -c cloud -c state -c details --max-width 100 --sort-column details --sort-c...  Tue Oct 24 17:10:48 2023

+----------------------+--------------------------+---------+
| cloud                | state                    | details |
+----------------------+--------------------------+---------+
| welktxef-d931887-021 | finishing patch strategy |         |
| welktxef-d931856-008 | finishing patch strategy |         |
+----------------------+--------------------------+---------+

Every 15.0s: dcmanager strategy-step list -c cloud -c state -c details --max-width 100 --sort-column details --sort-c...  Tue Oct 24 17:11:04 2023

+----------------------+------------------+---------+
| cloud                | state            | details |
+----------------------+------------------+---------+
| welktxef-d931887-021 | starting upgrade |         |
| welktxef-d931856-008 | starting upgrade |         |
+----------------------+------------------+---------+

Every 15.0s: dcmanager strategy-step list -c cloud -c state -c details --max-width 100 --sort-column details --sort-c...  Tue Oct 24 17:18:27 2023

+----------------------+-------------------+---------+
| cloud                | state             | details |
+----------------------+-------------------+---------+
| welktxef-d931887-021 | upgrading simplex |         |
| welktxef-d931856-008 | upgrading simplex |         |
+----------------------+-------------------+---------+

Every 15.0s: dcmanager strategy-step list -c cloud -c state -c details --max-width ...  Tue Oct 24 18:47:41 2023

+----------------------+----------+---------+
| cloud                | state    | details |
+----------------------+----------+---------+
| welktxef-d931887-021 | complete |         |
| welktxef-d931856-008 | complete |         |
+----------------------+----------+---------+


```

### paused in mop to validate communication before contining with 4.9

```log
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ansible all --inventory subclouds --ask-pass --user XXXXXX -m ping
SSH password:
XXXXXX | SUCCESS => {
    "changed": false,
    "ping": "pong"
}
welktxef-d931887-021 | SUCCESS => {
    "changed": false,
    "ping": "pong"
}
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ dcmanager upgrade-strategy delete
+------------------------+----------------------------+
| Field                  | Value                      |
+------------------------+----------------------------+
| strategy type          | upgrade                    |
| subcloud apply type    | parallel                   |
| max parallel subclouds | 50                         |
| stop on failure        | False                      |
| state                  | deleting                   |
| created_at             | 2023-10-24T17:09:34.183632 |
| updated_at             | 2023-10-24T18:50:10.006932 |
+------------------------+----------------------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./set-intel-driver-version_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook --inventory subclouds --ask-pass --user XXXXXX \
> set-intel-driver-version.yaml 0</dev/null
SSH password:

XXXXXX [all] *********************************************************************

TASK [Retrieve platform release version] ***************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Retrieve intel_nic_driver_version service parameter] *********************
changed: [welktxef-d931887-021]
changed: [welktxef-d931856-008]

TASK [Store service parameter field values] ************************************
ok: [welktxef-d931887-021]
ok: [welktxef-d931856-008]

TASK [Delete old intel_nic_driver_version service parameter with resource] *****
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Clear the driver version] ************************************************
ok: [welktxef-d931887-021]
ok: [welktxef-d931856-008]

TASK [Set Intel driver version (with resource)] ********************************
skipping: [welktxef-d931887-021]
skipping: [welktxef-d931856-008]

TASK [Set Intel driver version] ************************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Apply service parameters] ************************************************
changed: [welktxef-d931887-021]
changed: [welktxef-d931856-008]

TASK [Retrieve current Intel driver version] ***********************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

PLAY RECAP *********************************************************************
welktxef-d931856-008       : ok=8    changed=6    unreachable=0    failed=0
welktxef-d931887-021       : ok=8    changed=6    unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./lock-unlock_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook --inventory subclouds --ask-pass --user XXXXXX lock-unlock.yaml \
> 0</dev/null
SSH password:

XXXXXX [all] *********************************************************************

TASK [Check if host is already locked] *****************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Lock host] ***************************************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Wait for host to enter locked state] *************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Unlock host] *************************************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

PLAY RECAP *********************************************************************
welktxef-d931856-008       : ok=4    changed=4    unreachable=0    failed=0
welktxef-d931887-021       : ok=4    changed=4    unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

Every 2.0s: dcmanager subcloud-group list-subclouds Default -f value -c name -c ava...  Tue Oct 24 19:04:21 2023

welktxef-d931887-021 online
welktxef-d931856-008 online



```
### Continuing to next step

```log
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./confirm-ice-driver-version_$(date "+%Y%m%d%H%M%S").log \
> ansible all --inventory subclouds --ask-pass --ask-become-pass --user XXXXXX --become \
> --module-name shell --args "grep -E 'ice\:.*1\.5\.8$' /var/log/dmesg"
SSH password:
XXXXXX password[defaults to SSH password]:
welktxef-d931856-008 | CHANGED | rc=0 >>
[   11.381281] ice: Intel(R) Ethernet Connection E800 Series Linux Driver - version 1.5.8

welktxef-d931887-021 | CHANGED | rc=0 >>
[   12.877166] ice: Intel(R) Ethernet Connection E800 Series Linux Driver - version 1.5.8

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./dm_delete_old_secret_$(date "+%Y%m%d%H%M%S").log \
> ansible all --inventory subclouds --ask-pass --user XXXXXX --module-name shell \
> --args "kubectl --kubeconfig /etc/kubernetes/admin.conf delete secret \
> -n platform-deployment-manager platform-deployment-manager-webhook-server-secret"
SSH password:
XXXXXX | CHANGED | rc=0 >>
secret "platform-deployment-manager-webhook-server-secret" deleted

welktxef-d931887-021 | CHANGED | rc=0 >>
secret "platform-deployment-manager-webhook-server-secret" deleted

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ XXXXXX_password=XXXXXX
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ for subcloud in $(dcmanager subcloud-group list-subclouds ${subcloud_group} -f value -c name); do
> dcmanager subcloud reconfig --XXXXXX-password ${XXXXXX_password} \
> --deploy-config subclouds-deployment-config.yaml ${subcloud}
> done
+-----------------------------+---------------------------------+
| Field                       | Value                           |
+-----------------------------+---------------------------------+
| id                          | 5                               |
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
| created_at                  | 2023-10-02T19:29:24.044196      |
| updated_at                  | 2023-10-24T19:07:01.830845      |
+-----------------------------+---------------------------------+
+-----------------------------+---------------------------------+
| Field                       | Value                           |
+-----------------------------+---------------------------------+
| id                          | 6                               |
| name                        | welktxef-d931856-008            |
| description                 | Wind River Cloud Platform 21.05 |
| location                    | welktxef-d931856-008            |
| software_version            | 21.12                           |
| management                  | managed                         |
| availability                | online                          |
| deploy_status               | pre-deploy                      |
| management_subnet           | 2607:f160:10:80bb::/64          |
| management_start_ip         | 2607:f160:10:80bb:ce:40a::      |
| management_end_ip           | 2607:f160:10:80bb:ce:40a:0:f    |
| management_gateway_ip       | 2607:f160:10:80bb:ce:23::       |
| systemcontroller_gateway_ip | 2607:f160:0:3042:cd:28::        |
| group_id                    | 1                               |
| created_at                  | 2023-10-02T21:56:39.788890      |
| updated_at                  | 2023-10-24T19:07:02.689766      |
+-----------------------------+---------------------------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
Every 2.0s: dcmanager subcloud-group list-subclouds Default -c name -c deploy_status    Tue Oct 24 19:07:48 2023

+----------------------+---------------+
| name                 | deploy_status |
+----------------------+---------------+
| welktxef-d931887-021 | complete      |
| welktxef-d931856-008 | complete      |
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
platform-deployment-manager-0   2/2     Running   2          119s
registry.local:9001/docker.io/wind-river/cloud-platform-deployment-manager:WRCP_21.12-wrs.4
registry.local:9001/gcr.io/kubebuilder/kube-rbac-proxy:v0.4.0

welktxef-d931887-021 | CHANGED | rc=0 >>
NAME                            READY   STATUS    RESTARTS   AGE
platform-deployment-manager-0   2/2     Running   2          2m2s
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
ok: [welktxef-d931856-008]

TASK [Get Ip Controller] *******************************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [debug] *******************************************************************
ok: [welktxef-d931887-021] => {
    "msg": "controller ip: 2607:f160:10:809f:ce:40a::"
}
ok: [welktxef-d931856-008] => {
    "msg": "controller ip: 2607:f160:10:80bb:ce:40a::"
}

TASK [Install Deployment Manager Monitor] **************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Wait for Deployment Manager Monitor to be ready] *************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

PLAY RECAP *********************************************************************
welktxef-d931856-008       : ok=5    changed=3    unreachable=0    failed=0
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
dm-monitor-78c7f7db95-7tznl   1/1     Running   0          35s
registry.local:9001/docker.io/wind-river/dm-monitor:WRCP_21.05-v1.0.0

welktxef-d931887-021 | CHANGED | rc=0 >>
NAME                          READY   STATUS    RESTARTS   AGE
dm-monitor-85bc647788-9dsqf   1/1     Running   0          36s
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
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Check if application is removed] *****************************************
FAILED - RETRYING: Check if application is removed (6 retries left).
FAILED - RETRYING: Check if application is removed (6 retries left).
changed: [welktxef-d931887-021]
changed: [welktxef-d931856-008]

TASK [Delete application] ******************************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Retrieve latest application version] *************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Upload application] ******************************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Check if application is uploaded] ****************************************
FAILED - RETRYING: Check if application is uploaded (30 retries left).
FAILED - RETRYING: Check if application is uploaded (30 retries left).
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Copy application overrides to the subcloud] ******************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Apply application overrides] *********************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Remove override file] ****************************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Apply application] *******************************************************
changed: [welktxef-d931887-021]
changed: [welktxef-d931856-008]

TASK [Check if application is applied] *****************************************
FAILED - RETRYING: Check if application is applied (12 retries left).
FAILED - RETRYING: Check if application is applied (12 retries left).
FAILED - RETRYING: Check if application is applied (11 retries left).
FAILED - RETRYING: Check if application is applied (11 retries left).
FAILED - RETRYING: Check if application is applied (10 retries left).
FAILED - RETRYING: Check if application is applied (10 retries left).
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

PLAY RECAP *********************************************************************
welktxef-d931856-008       : ok=11   changed=11   unreachable=0    failed=0
welktxef-d931887-021       : ok=11   changed=11   unreachable=0    failed=0

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
ptp-ptp-notification-stw66   3/3     Running   0          54s
registry.local:9001/docker.io/rabbitmq:3.8.11-management
registry.local:9001/docker.io/starlingx/locationservice-base:stx.5.0-v1.0.1
registry.local:9001/docker.io/starlingx/notificationservice-base:stx.6.0-v1.0.7

welktxef-d931887-021 | CHANGED | rc=0 >>
NAME                         READY   STATUS    RESTARTS   AGE
ptp-ptp-notification-q9qc7   3/3     Running   0          54s
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
skipping: [welktxef-d931856-008]

TASK [Apply application overrides] *********************************************
skipping: [welktxef-d931887-021]
skipping: [welktxef-d931856-008]

TASK [Remove override file] ****************************************************
skipping: [welktxef-d931887-021]
skipping: [welktxef-d931856-008]

TASK [Retrieve latest application version] *************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Upgrade application] *****************************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Check if application is applied] *****************************************
FAILED - RETRYING: Check if application is applied (12 retries left).
FAILED - RETRYING: Check if application is applied (12 retries left).
FAILED - RETRYING: Check if application is applied (11 retries left).
FAILED - RETRYING: Check if application is applied (11 retries left).
FAILED - RETRYING: Check if application is applied (10 retries left).
FAILED - RETRYING: Check if application is applied (10 retries left).
FAILED - RETRYING: Check if application is applied (9 retries left).
FAILED - RETRYING: Check if application is applied (9 retries left).
FAILED - RETRYING: Check if application is applied (8 retries left).
changed: [welktxef-d931887-021]
FAILED - RETRYING: Check if application is applied (7 retries left).
changed: [welktxef-d931856-008]

PLAY RECAP *********************************************************************
welktxef-d931856-008       : ok=3    changed=3    unreachable=0    failed=0
welktxef-d931887-021       : ok=3    changed=3    unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./verify-subcloud-metrics-server_$(date "+%Y%m%d%H%M%S").log \
> ansible all --inventory subclouds --ask-pass --user XXXXXX --module-name shell \
> --args "kubectl --kubeconfig /etc/kubernetes/admin.conf get pods \
> -l app=metrics-server -n metrics-server; \
> kubectl --kubeconfig /etc/kubernetes/admin.conf get pods \
> -A -l "app=metrics-server" -o \
> jsonpath="{..image}" | tr -s '[[:space:]]' '\n'| sort | uniq"
SSH password:
XXXXXX | CHANGED | rc=0 >>
NAME                                 READY   STATUS    RESTARTS   AGE
ms-metrics-server-6676595474-nrq4d   1/1     Running   1          106s
registry.local:9001/k8s.gcr.io/metrics-server/metrics-server:v0.4.1

welktxef-d931887-021 | CHANGED | rc=0 >>
NAME                                 READY   STATUS    RESTARTS   AGE
ms-metrics-server-6676595474-kgp79   1/1     Running   0          107s
registry.local:9001/k8s.gcr.io/metrics-server/metrics-server:v0.4.1

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ for subcloud in $(dcmanager subcloud-group list-subclouds ${subcloud_group} -f value -c name); do
> if [ "$(dcmanager subcloud show ${subcloud} -c software_version -f value)" != "21.12" ]; then
> echo "${subcloud} was not upgraded to 21.12"
> fi
> done
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./cleanup-old-pods_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook --inventory subclouds --ask-pass --user XXXXXX \
> cleanup-old-pods.yaml 0</dev/null
SSH password:

XXXXXX [all] *********************************************************************

TASK [Fetch pods in failed state] **********************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Delete failed pods] ******************************************************

PLAY RECAP *********************************************************************
welktxef-d931856-008       : ok=1    changed=1    unreachable=0    failed=0
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
ok: [welktxef-d931856-008]
ok: [welktxef-d931887-021]

TASK [Read in parameter file] **************************************************
ok: [welktxef-d931887-021]
ok: [welktxef-d931856-008]

TASK [set expected Fortville firmware version] *********************************
ok: [welktxef-d931887-021]
ok: [welktxef-d931856-008]

TASK [set expected N3000 firmware version] *************************************
ok: [welktxef-d931887-021]
ok: [welktxef-d931856-008]

TASK [create directory /home/XXXXXX/sanity] **********************************
ok: [welktxef-d931887-021 -> localhost]
ok: [welktxef-d931856-008 -> localhost]

TASK [delete existing file /home/XXXXXX/sanity/output_list] ******************
changed: [welktxef-d931887-021 -> localhost]
ok: [welktxef-d931856-008 -> localhost]

TASK [create file /home/XXXXXX/sanity/output_list] ***************************
changed: [welktxef-d931887-021 -> localhost]
changed: [welktxef-d931856-008 -> localhost]

TASK [get host patch status] ***************************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [validate host patch status] **********************************************
skipping: [welktxef-d931887-021]
skipping: [welktxef-d931856-008]

TASK [get host status] *********************************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [validate host status] ****************************************************
skipping: [welktxef-d931887-021]
skipping: [welktxef-d931856-008]

TASK [get current alarms] ******************************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [validate current alarms] *************************************************
skipping: [welktxef-d931887-021]
skipping: [welktxef-d931856-008]

TASK [get vim status] **********************************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [validate vim status] *****************************************************
skipping: [welktxef-d931887-021]
skipping: [welktxef-d931856-008]

TASK [calculate / partition expected usage] ************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [validate / partition free space] *****************************************
skipping: [welktxef-d931887-021]
skipping: [welktxef-d931856-008]

TASK [validate /opt/dc-vault partition free space] *****************************
skipping: [welktxef-d931887-021]
skipping: [welktxef-d931856-008]

TASK [identify N3000 NICs] *****************************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [get N3000 NICs firmware version] *****************************************

TASK [validate N3000 NICs firmware version] ************************************

TASK [get N3000 NICs MAC] ******************************************************

TASK [validate N3000 NICs MACs] ************************************************

TASK [identify Fortville NICs] *************************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [get Fortville NICs firmware version] *************************************

TASK [validate Fortville NICs firmware version] ********************************

TASK [get Fortville NICs MAC] **************************************************

TASK [validate Fortville NICs MACs] ********************************************

TASK [identify accelerators] ***************************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [retrieve device information] *********************************************
changed: [welktxef-d931856-008] => (item=pci_0000_51_00_0)
changed: [welktxef-d931887-021] => (item=pci_0000_51_00_0)

TASK [output device show information] ******************************************
ok: [welktxef-d931887-021] => (item=pci_0000_51_00_0) => {
    "msg": [
        "+-----------------------+-----------------------------------------------------------------------------------------+",
        "| Property              | Value                                                                                   |",
        "+-----------------------+-----------------------------------------------------------------------------------------+",
        "| name                  | pci_0000_51_00_0                                                                        |",
        "| address               | 0000:51:00.0                                                                            |",
        "| class id              | 120001                                                                                  |",
        "| vendor id             | 8086                                                                                    |",
        "| device id             | 0d5c                                                                                    |",
        "| class name            | Processing accelerators                                                                 |",
        "| vendor name           | Intel Corporation                                                                       |",
        "| device name           | Device 0d5c                                                                             |",
        "| numa_node             | 0                                                                                       |",
        "| enabled               | True                                                                                    |",
        "| sriov_totalvfs        | 16                                                                                      |",
        "| sriov_numvfs          | 1                                                                                       |",
        "| sriov_vfs_pci_address | 0000:52:00.0                                                                            |",
        "| sriov_vf_pdevice_id   | 0d5d                                                                                    |",
        "| extra_info            | {'expected_driver': u'igb_uio', 'expected_vf_driver': u'igb_uio', 'expected_numvfs': 1} |",
        "| created_at            | 2023-10-02T19:59:39.799717+00:00                                                        |",
        "| updated_at            | 2023-10-24T19:04:10.781928+00:00                                                        |",
        "| root_key              | None                                                                                    |",
        "| revoked_key_ids       | None                                                                                    |",
        "| boot_page             | None                                                                                    |",
        "| bitstream_id          | None                                                                                    |",
        "| bmc_build_version     | None                                                                                    |",
        "| bmc_fw_version        | None                                                                                    |",
        "| retimer_a_version     | None                                                                                    |",
        "| retimer_b_version     | None                                                                                    |",
        "| driver                | igb_uio                                                                                 |",
        "| sriov_vf_driver       | igb_uio                                                                                 |",
        "+-----------------------+-----------------------------------------------------------------------------------------+"
    ]
}
ok: [welktxef-d931856-008] => (item=pci_0000_51_00_0) => {
    "msg": [
        "+-----------------------+-----------------------------------------------------------------------------------------+",
        "| Property              | Value                                                                                   |",
        "+-----------------------+-----------------------------------------------------------------------------------------+",
        "| name                  | pci_0000_51_00_0                                                                        |",
        "| address               | 0000:51:00.0                                                                            |",
        "| class id              | 120001                                                                                  |",
        "| vendor id             | 8086                                                                                    |",
        "| device id             | 0d5c                                                                                    |",
        "| class name            | Processing accelerators                                                                 |",
        "| vendor name           | Intel Corporation                                                                       |",
        "| device name           | Device 0d5c                                                                             |",
        "| numa_node             | 0                                                                                       |",
        "| enabled               | True                                                                                    |",
        "| sriov_totalvfs        | 16                                                                                      |",
        "| sriov_numvfs          | 1                                                                                       |",
        "| sriov_vfs_pci_address | 0000:52:00.0                                                                            |",
        "| sriov_vf_pdevice_id   | 0d5d                                                                                    |",
        "| extra_info            | {'expected_driver': u'igb_uio', 'expected_vf_driver': u'igb_uio', 'expected_numvfs': 1} |",
        "| created_at            | 2023-10-02T22:24:59.776788+00:00                                                        |",
        "| updated_at            | 2023-10-24T19:04:04.176279+00:00                                                        |",
        "| root_key              | None                                                                                    |",
        "| revoked_key_ids       | None                                                                                    |",
        "| boot_page             | None                                                                                    |",
        "| bitstream_id          | None                                                                                    |",
        "| bmc_build_version     | None                                                                                    |",
        "| bmc_fw_version        | None                                                                                    |",
        "| retimer_a_version     | None                                                                                    |",
        "| retimer_b_version     | None                                                                                    |",
        "| driver                | igb_uio                                                                                 |",
        "| sriov_vf_driver       | igb_uio                                                                                 |",
        "+-----------------------+-----------------------------------------------------------------------------------------+"
    ]
}

TASK [retrieve device information] *********************************************
changed: [welktxef-d931856-008] => (item=pci_0000_51_00_0)
changed: [welktxef-d931887-021] => (item=pci_0000_51_00_0)

TASK [output field information] ************************************************
ok: [welktxef-d931887-021] => (item=pci_0000_51_00_0) => {
    "msg": "1|{'expected_driver':u'igb_uio','expected_vf_driver':u'igb_uio','expected_numvfs':1}|igb_uio|igb_uio"
}
ok: [welktxef-d931856-008] => (item=pci_0000_51_00_0) => {
    "msg": "1|{'expected_driver':u'igb_uio','expected_vf_driver':u'igb_uio','expected_numvfs':1}|igb_uio|igb_uio"
}

TASK [validate sriov_numvfs for Mount Bryce] ***********************************
skipping: [welktxef-d931887-021] => (item=pci_0000_51_00_0)
skipping: [welktxef-d931856-008] => (item=pci_0000_51_00_0)

TASK [validate driver and sriov_vf_driver fields] ******************************
skipping: [welktxef-d931887-021] => (item=pci_0000_51_00_0)
skipping: [welktxef-d931856-008] => (item=pci_0000_51_00_0)

TASK [validate extra_info field] ***********************************************
skipping: [welktxef-d931887-021] => (item=pci_0000_51_00_0)
skipping: [welktxef-d931856-008] => (item=pci_0000_51_00_0)

TASK [get pod status] **********************************************************
changed: [welktxef-d931887-021]
changed: [welktxef-d931856-008]

TASK [validate pod status] *****************************************************
skipping: [welktxef-d931887-021]
skipping: [welktxef-d931856-008]

TASK [get system applications] *************************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [validate system applications] ********************************************
skipping: [welktxef-d931887-021] => (item=cert-manager:21.12-28)
skipping: [welktxef-d931887-021] => (item=nginx-ingress-controller:21.12-18)
skipping: [welktxef-d931887-021] => (item=oidc-auth-apps:21.12-61)
skipping: [welktxef-d931887-021] => (item=platform-integ-apps:21.12-46)
skipping: [welktxef-d931856-008] => (item=cert-manager:21.12-28)
skipping: [welktxef-d931856-008] => (item=nginx-ingress-controller:21.12-18)
skipping: [welktxef-d931856-008] => (item=oidc-auth-apps:21.12-61)
skipping: [welktxef-d931856-008] => (item=platform-integ-apps:21.12-46)

PLAY RECAP *********************************************************************
welktxef-d931856-008       : ok=21   changed=13   unreachable=0    failed=0
welktxef-d931887-021       : ok=21   changed=14   unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ cat /home/XXXXXX/sanity/output_list
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./resize_fs_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook --inventory subclouds --ask-pass --user XXXXXX \
> --extra-vars '{"partitions":[1000],"hfs_docker":250,"cfs_docker_distribution":100}' \
> resize_fs.yaml 0</dev/null
SSH password:

XXXXXX [all] *********************************************************************

TASK [Retrieve list of controllers] ********************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Retrieve distributed cloud role] *****************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Confirm cgts volumes] ****************************************************
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/confirm_cgts_volumes.yaml for welktxef-d931887-021, welktxef-d931856-008

TASK [Retrieve rootfs disk] ****************************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Retrieve available space on the rootfs device] ***************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [set_fact] ****************************************************************
ok: [welktxef-d931887-021]
ok: [welktxef-d931856-008]

TASK [Retrieve partitions present on the rootfs device] ************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Validate number of partitions requested] *********************************
skipping: [welktxef-d931887-021]
skipping: [welktxef-d931856-008]

TASK [Validate requested partition sizes] **************************************
skipping: [welktxef-d931887-021] => (item=[u'1000.0', 1000])
skipping: [welktxef-d931856-008] => (item=[u'1000.0', 1000])

TASK [Determine amount of free space after all partitions are allocated] *******
skipping: [welktxef-d931887-021] => (item=[u'1000.0', 1000])
skipping: [welktxef-d931856-008] => (item=[u'1000.0', 1000])

TASK [Display amount of free space after all partitions are allocated] *********
ok: [welktxef-d931887-021] => {
    "msg": "633"
}
ok: [welktxef-d931856-008] => {
    "msg": "558"
}

TASK [Verify there is enough space to allocate all partitions] *****************
skipping: [welktxef-d931887-021]
skipping: [welktxef-d931856-008]

TASK [Create new volumes] ******************************************************
skipping: [welktxef-d931887-021] => (item=[u'1000.0', 1000])
skipping: [welktxef-d931856-008] => (item=[u'1000.0', 1000])

TASK [Retrieve controller filesystems and sizes] *******************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Store requested controller filesystem sizes] *****************************
ok: [welktxef-d931887-021] => (item=platform 10)
ok: [welktxef-d931856-008] => (item=database 10)
ok: [welktxef-d931887-021] => (item=extension 1)
ok: [welktxef-d931856-008] => (item=docker-distribution 32)
ok: [welktxef-d931887-021] => (item=database 10)
ok: [welktxef-d931856-008] => (item=extension 1)
ok: [welktxef-d931887-021] => (item=docker-distribution 32)
ok: [welktxef-d931856-008] => (item=platform 10)
ok: [welktxef-d931887-021] => (item=etcd 5)
ok: [welktxef-d931856-008] => (item=etcd 5)

TASK [Build controller filesystem resizing parms] ******************************
skipping: [welktxef-d931887-021] => (item=platform 10)
skipping: [welktxef-d931887-021] => (item=extension 1)
skipping: [welktxef-d931856-008] => (item=database 10)
skipping: [welktxef-d931887-021] => (item=database 10)
ok: [welktxef-d931856-008] => (item=docker-distribution 32)
skipping: [welktxef-d931856-008] => (item=extension 1)
ok: [welktxef-d931887-021] => (item=docker-distribution 32)
skipping: [welktxef-d931887-021] => (item=etcd 5)
skipping: [welktxef-d931856-008] => (item=platform 10)
skipping: [welktxef-d931856-008] => (item=etcd 5)

TASK [Resize all controller filesystems] ***************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Wait for all controller filesystems to be resized and fully sync] ********
FAILED - RETRYING: Wait for all controller filesystems to be resized and fully sync (720 retries left).
FAILED - RETRYING: Wait for all controller filesystems to be resized and fully sync (720 retries left).
FAILED - RETRYING: Wait for all controller filesystems to be resized and fully sync (719 retries left).
FAILED - RETRYING: Wait for all controller filesystems to be resized and fully sync (719 retries left).
FAILED - RETRYING: Wait for all controller filesystems to be resized and fully sync (718 retries left).
FAILED - RETRYING: Wait for all controller filesystems to be resized and fully sync (718 retries left).
FAILED - RETRYING: Wait for all controller filesystems to be resized and fully sync (717 retries left).
FAILED - RETRYING: Wait for all controller filesystems to be resized and fully sync (717 retries left).
FAILED - RETRYING: Wait for all controller filesystems to be resized and fully sync (716 retries left).
FAILED - RETRYING: Wait for all controller filesystems to be resized and fully sync (716 retries left).
FAILED - RETRYING: Wait for all controller filesystems to be resized and fully sync (715 retries left).
FAILED - RETRYING: Wait for all controller filesystems to be resized and fully sync (715 retries left).
FAILED - RETRYING: Wait for all controller filesystems to be resized and fully sync (714 retries left).
FAILED - RETRYING: Wait for all controller filesystems to be resized and fully sync (714 retries left).
FAILED - RETRYING: Wait for all controller filesystems to be resized and fully sync (713 retries left).
FAILED - RETRYING: Wait for all controller filesystems to be resized and fully sync (713 retries left).
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Wait for any 400.001 alarm to clear] *************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Resize host filesystems] *************************************************
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/resize_hostfs.yaml for welktxef-d931887-021, welktxef-d931856-008

TASK [Retrieve host filesystems and sizes] *************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Store requested host filesystem sizes] ***********************************
ok: [welktxef-d931887-021] => (item=backup 25)
ok: [welktxef-d931887-021] => (item=docker 58)
ok: [welktxef-d931856-008] => (item=backup 25)
ok: [welktxef-d931856-008] => (item=docker 58)
ok: [welktxef-d931887-021] => (item=kubelet 10)
ok: [welktxef-d931856-008] => (item=kubelet 10)
ok: [welktxef-d931887-021] => (item=scratch 16)
ok: [welktxef-d931856-008] => (item=scratch 16)

TASK [Build hostfs resizing parms] *********************************************
skipping: [welktxef-d931887-021] => (item=backup 25)
skipping: [welktxef-d931856-008] => (item=backup 25)
ok: [welktxef-d931887-021] => (item=docker 58)
ok: [welktxef-d931856-008] => (item=docker 58)
skipping: [welktxef-d931887-021] => (item=kubelet 10)
skipping: [welktxef-d931887-021] => (item=scratch 16)
skipping: [welktxef-d931856-008] => (item=kubelet 10)
skipping: [welktxef-d931856-008] => (item=scratch 16)

TASK [Resize all host filesystems] *********************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Wait for any 250.001 alarm to clear] *************************************
FAILED - RETRYING: Wait for any 250.001 alarm to clear (300 retries left).
FAILED - RETRYING: Wait for any 250.001 alarm to clear (300 retries left).
FAILED - RETRYING: Wait for any 250.001 alarm to clear (299 retries left).
FAILED - RETRYING: Wait for any 250.001 alarm to clear (299 retries left).
FAILED - RETRYING: Wait for any 250.001 alarm to clear (298 retries left).
FAILED - RETRYING: Wait for any 250.001 alarm to clear (298 retries left).
FAILED - RETRYING: Wait for any 250.001 alarm to clear (297 retries left).
FAILED - RETRYING: Wait for any 250.001 alarm to clear (297 retries left).
FAILED - RETRYING: Wait for any 250.001 alarm to clear (296 retries left).
FAILED - RETRYING: Wait for any 250.001 alarm to clear (296 retries left).
FAILED - RETRYING: Wait for any 250.001 alarm to clear (295 retries left).
FAILED - RETRYING: Wait for any 250.001 alarm to clear (295 retries left).
FAILED - RETRYING: Wait for any 250.001 alarm to clear (294 retries left).
FAILED - RETRYING: Wait for any 250.001 alarm to clear (294 retries left).
FAILED - RETRYING: Wait for any 250.001 alarm to clear (293 retries left).
FAILED - RETRYING: Wait for any 250.001 alarm to clear (293 retries left).
FAILED - RETRYING: Wait for any 250.001 alarm to clear (292 retries left).
FAILED - RETRYING: Wait for any 250.001 alarm to clear (292 retries left).
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

PLAY RECAP *********************************************************************
welktxef-d931856-008       : ok=20   changed=12   unreachable=0    failed=0
welktxef-d931887-021       : ok=20   changed=12   unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$


```

### MOP 4 of wrcp 21.12p10 complete, next is MOP 5 

```log
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ system kube-version-list | awk -F \| '$4 ~ / active / { gsub(/ /,"",$2);print $2 }'
v1.21.8
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
| updated_at             | 2023-10-24 16:45:19.887605 |
+------------------------+----------------------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ echo '[subclouds]' > subclouds
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ dcmanager subcloud-group list-subclouds ${subcloud_group} -c name -f value >> subclouds
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ for subcloud in $(sed -n '/subclouds/ { :a; n; p; ba; }' < subclouds); do
> echo ${subcloud}
> dcmanager subcloud show ${subcloud} | \
> grep sync_status | \
> grep -E -v "in-sync|kubernetes_sync|firmware_sync|dc-cert_sync";
> done
welktxef-d931887-021
welktxef-d931856-008
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./sanity_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook --inventory subclouds --extra-vars "scenario=after" \
> --ask-pass --ask-become-pass --user XXXXXX \
> sanity.yaml 0</dev/null
SSH password:
XXXXXX password[defaults to SSH password]:

PLAY [all] *********************************************************************

TASK [Gathering Facts] *********************************************************
ok: [welktxef-d931856-008]
ok: [welktxef-d931887-021]

TASK [Read in parameter file] **************************************************
ok: [welktxef-d931887-021]
ok: [welktxef-d931856-008]

TASK [set expected Fortville firmware version] *********************************
ok: [welktxef-d931887-021]
ok: [welktxef-d931856-008]

TASK [set expected N3000 firmware version] *************************************
ok: [welktxef-d931887-021]
ok: [welktxef-d931856-008]

TASK [create directory /home/XXXXXX/sanity] **********************************
ok: [welktxef-d931887-021 -> localhost]
ok: [welktxef-d931856-008 -> localhost]

TASK [delete existing file /home/XXXXXX/sanity/output_list] ******************
changed: [welktxef-d931887-021 -> localhost]
ok: [welktxef-d931856-008 -> localhost]

TASK [create file /home/XXXXXX/sanity/output_list] ***************************
changed: [welktxef-d931887-021 -> localhost]
changed: [welktxef-d931856-008 -> localhost]

TASK [get host patch status] ***************************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [validate host patch status] **********************************************
skipping: [welktxef-d931887-021]
skipping: [welktxef-d931856-008]

TASK [get host status] *********************************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [validate host status] ****************************************************
skipping: [welktxef-d931887-021]
skipping: [welktxef-d931856-008]

TASK [get current alarms] ******************************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [validate current alarms] *************************************************
skipping: [welktxef-d931887-021]
skipping: [welktxef-d931856-008]

TASK [get vim status] **********************************************************
changed: [welktxef-d931887-021]
changed: [welktxef-d931856-008]

TASK [validate vim status] *****************************************************
skipping: [welktxef-d931887-021]
skipping: [welktxef-d931856-008]

TASK [calculate / partition expected usage] ************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [validate / partition free space] *****************************************
skipping: [welktxef-d931887-021]
skipping: [welktxef-d931856-008]

TASK [validate /opt/dc-vault partition free space] *****************************
skipping: [welktxef-d931887-021]
skipping: [welktxef-d931856-008]

TASK [identify N3000 NICs] *****************************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [get N3000 NICs firmware version] *****************************************

TASK [validate N3000 NICs firmware version] ************************************

TASK [get N3000 NICs MAC] ******************************************************

TASK [validate N3000 NICs MACs] ************************************************

TASK [identify Fortville NICs] *************************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [get Fortville NICs firmware version] *************************************

TASK [validate Fortville NICs firmware version] ********************************

TASK [get Fortville NICs MAC] **************************************************

TASK [validate Fortville NICs MACs] ********************************************

TASK [identify accelerators] ***************************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [retrieve device information] *********************************************
changed: [welktxef-d931856-008] => (item=pci_0000_51_00_0)
changed: [welktxef-d931887-021] => (item=pci_0000_51_00_0)

TASK [output device show information] ******************************************
ok: [welktxef-d931887-021] => (item=pci_0000_51_00_0) => {
    "msg": [
        "+-----------------------+-----------------------------------------------------------------------------------------+",
        "| Property              | Value                                                                                   |",
        "+-----------------------+-----------------------------------------------------------------------------------------+",
        "| name                  | pci_0000_51_00_0                                                                        |",
        "| address               | 0000:51:00.0                                                                            |",
        "| class id              | 120001                                                                                  |",
        "| vendor id             | 8086                                                                                    |",
        "| device id             | 0d5c                                                                                    |",
        "| class name            | Processing accelerators                                                                 |",
        "| vendor name           | Intel Corporation                                                                       |",
        "| device name           | Device 0d5c                                                                             |",
        "| numa_node             | 0                                                                                       |",
        "| enabled               | True                                                                                    |",
        "| sriov_totalvfs        | 16                                                                                      |",
        "| sriov_numvfs          | 1                                                                                       |",
        "| sriov_vfs_pci_address | 0000:52:00.0                                                                            |",
        "| sriov_vf_pdevice_id   | 0d5d                                                                                    |",
        "| extra_info            | {'expected_driver': u'igb_uio', 'expected_vf_driver': u'igb_uio', 'expected_numvfs': 1} |",
        "| created_at            | 2023-10-02T19:59:39.799717+00:00                                                        |",
        "| updated_at            | 2023-10-24T19:04:10.781928+00:00                                                        |",
        "| root_key              | None                                                                                    |",
        "| revoked_key_ids       | None                                                                                    |",
        "| boot_page             | None                                                                                    |",
        "| bitstream_id          | None                                                                                    |",
        "| bmc_build_version     | None                                                                                    |",
        "| bmc_fw_version        | None                                                                                    |",
        "| retimer_a_version     | None                                                                                    |",
        "| retimer_b_version     | None                                                                                    |",
        "| driver                | igb_uio                                                                                 |",
        "| sriov_vf_driver       | igb_uio                                                                                 |",
        "+-----------------------+-----------------------------------------------------------------------------------------+"
    ]
}
ok: [welktxef-d931856-008] => (item=pci_0000_51_00_0) => {
    "msg": [
        "+-----------------------+-----------------------------------------------------------------------------------------+",
        "| Property              | Value                                                                                   |",
        "+-----------------------+-----------------------------------------------------------------------------------------+",
        "| name                  | pci_0000_51_00_0                                                                        |",
        "| address               | 0000:51:00.0                                                                            |",
        "| class id              | 120001                                                                                  |",
        "| vendor id             | 8086                                                                                    |",
        "| device id             | 0d5c                                                                                    |",
        "| class name            | Processing accelerators                                                                 |",
        "| vendor name           | Intel Corporation                                                                       |",
        "| device name           | Device 0d5c                                                                             |",
        "| numa_node             | 0                                                                                       |",
        "| enabled               | True                                                                                    |",
        "| sriov_totalvfs        | 16                                                                                      |",
        "| sriov_numvfs          | 1                                                                                       |",
        "| sriov_vfs_pci_address | 0000:52:00.0                                                                            |",
        "| sriov_vf_pdevice_id   | 0d5d                                                                                    |",
        "| extra_info            | {'expected_driver': u'igb_uio', 'expected_vf_driver': u'igb_uio', 'expected_numvfs': 1} |",
        "| created_at            | 2023-10-02T22:24:59.776788+00:00                                                        |",
        "| updated_at            | 2023-10-24T19:04:04.176279+00:00                                                        |",
        "| root_key              | None                                                                                    |",
        "| revoked_key_ids       | None                                                                                    |",
        "| boot_page             | None                                                                                    |",
        "| bitstream_id          | None                                                                                    |",
        "| bmc_build_version     | None                                                                                    |",
        "| bmc_fw_version        | None                                                                                    |",
        "| retimer_a_version     | None                                                                                    |",
        "| retimer_b_version     | None                                                                                    |",
        "| driver                | igb_uio                                                                                 |",
        "| sriov_vf_driver       | igb_uio                                                                                 |",
        "+-----------------------+-----------------------------------------------------------------------------------------+"
    ]
}

TASK [retrieve device information] *********************************************
changed: [welktxef-d931856-008] => (item=pci_0000_51_00_0)
changed: [welktxef-d931887-021] => (item=pci_0000_51_00_0)

TASK [output field information] ************************************************
ok: [welktxef-d931887-021] => (item=pci_0000_51_00_0) => {
    "msg": "1|{'expected_driver':u'igb_uio','expected_vf_driver':u'igb_uio','expected_numvfs':1}|igb_uio|igb_uio"
}
ok: [welktxef-d931856-008] => (item=pci_0000_51_00_0) => {
    "msg": "1|{'expected_driver':u'igb_uio','expected_vf_driver':u'igb_uio','expected_numvfs':1}|igb_uio|igb_uio"
}

TASK [validate sriov_numvfs for Mount Bryce] ***********************************
skipping: [welktxef-d931887-021] => (item=pci_0000_51_00_0)
skipping: [welktxef-d931856-008] => (item=pci_0000_51_00_0)

TASK [validate driver and sriov_vf_driver fields] ******************************
skipping: [welktxef-d931887-021] => (item=pci_0000_51_00_0)
skipping: [welktxef-d931856-008] => (item=pci_0000_51_00_0)

TASK [validate extra_info field] ***********************************************
skipping: [welktxef-d931887-021] => (item=pci_0000_51_00_0)
skipping: [welktxef-d931856-008] => (item=pci_0000_51_00_0)

TASK [get pod status] **********************************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [validate pod status] *****************************************************
skipping: [welktxef-d931887-021]
skipping: [welktxef-d931856-008]

TASK [get system applications] *************************************************
changed: [welktxef-d931887-021]
changed: [welktxef-d931856-008]

TASK [validate system applications] ********************************************
skipping: [welktxef-d931887-021] => (item=cert-manager:21.12-28)
skipping: [welktxef-d931887-021] => (item=nginx-ingress-controller:21.12-18)
skipping: [welktxef-d931887-021] => (item=oidc-auth-apps:21.12-61)
skipping: [welktxef-d931887-021] => (item=platform-integ-apps:21.12-46)
skipping: [welktxef-d931856-008] => (item=cert-manager:21.12-28)
skipping: [welktxef-d931856-008] => (item=nginx-ingress-controller:21.12-18)
skipping: [welktxef-d931856-008] => (item=oidc-auth-apps:21.12-61)
skipping: [welktxef-d931856-008] => (item=platform-integ-apps:21.12-46)

PLAY RECAP *********************************************************************
welktxef-d931856-008       : ok=21   changed=13   unreachable=0    failed=0
welktxef-d931887-021       : ok=21   changed=14   unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ cat /home/XXXXXX/sanity/output_list
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
```

### Completed prechecks now to deployment

```log
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ dcmanager kube-upgrade-strategy create --group ${subcloud_group}
+------------------------+----------------------------+
| Field                  | Value                      |
+------------------------+----------------------------+
| strategy type          | kubernetes                 |
| subcloud apply type    | parallel                   |
| max parallel subclouds | 50                         |
| stop on failure        | False                      |
| state                  | initial                    |
| created_at             | 2023-10-24T19:31:41.824609 |
| updated_at             | None                       |
+------------------------+----------------------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ dcmanager strategy-step list -c cloud -c stage -c state
+----------------------+-------+---------+
| cloud                | stage | state   |
+----------------------+-------+---------+
| welktxef-d931887-021 |     1 | initial |
| welktxef-d931856-008 |     1 | initial |
+----------------------+-------+---------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ dcmanager kube-upgrade-strategy apply
+------------------------+----------------------------+
| Field                  | Value                      |
+------------------------+----------------------------+
| strategy type          | kubernetes                 |
| subcloud apply type    | parallel                   |
| max parallel subclouds | 50                         |
| stop on failure        | False                      |
| state                  | applying                   |
| created_at             | 2023-10-24T19:31:41.824609 |
| updated_at             | 2023-10-24T19:31:58.651902 |
+------------------------+----------------------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

Every 15.0s: dcmanager strategy-step list -c cloud -c state -c details --max-width ...  Tue Oct 24 19:58:32 2023

+----------------------+----------+---------+
| cloud                | state    | details |
+----------------------+----------+---------+
| welktxef-d931887-021 | complete |         |
| welktxef-d931856-008 | complete |         |
+----------------------+----------+---------+

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ dcmanager kube-upgrade-strategy delete
+------------------------+----------------------------+
| Field                  | Value                      |
+------------------------+----------------------------+
| strategy type          | kubernetes                 |
| subcloud apply type    | parallel                   |
| max parallel subclouds | 50                         |
| stop on failure        | False                      |
| state                  | deleting                   |
| created_at             | 2023-10-24T19:31:41.824609 |
| updated_at             | 2023-10-24T19:58:54.452144 |
+------------------------+----------------------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ watch dcmanager kube-upgrade-strategy show
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./cleanup-old-pods_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook --inventory subclouds --ask-pass --user XXXXXX \
> cleanup-old-pods.yaml 0</dev/null
SSH password:

XXXXXX [all] *********************************************************************

TASK [Fetch pods in failed state] **********************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Delete failed pods] ******************************************************

PLAY RECAP *********************************************************************
welktxef-d931856-008       : ok=1    changed=1    unreachable=0    failed=0
welktxef-d931887-021       : ok=1    changed=1    unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./apply-kubelet-config_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook --inventory subclouds --ask-pass --user XXXXXX apply-kubelet-config.yaml \
> 0</dev/null
SSH password:

XXXXXX [all] *********************************************************************

TASK [Remove kubelet-config settings for old versions] *************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Reapply kubelet-config settings] *****************************************
changed: [welktxef-d931887-021]
changed: [welktxef-d931856-008]

TASK [Wait for kubelet-config settings to be applied] **************************
FAILED - RETRYING: Wait for kubelet-config settings to be applied (10 retries left).
FAILED - RETRYING: Wait for kubelet-config settings to be applied (10 retries left).
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Output kubelet-config info] **********************************************
ok: [welktxef-d931887-021] => {
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
ok: [welktxef-d931856-008] => {
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
welktxef-d931856-008       : ok=4    changed=3    unreachable=0    failed=0
welktxef-d931887-021       : ok=4    changed=3    unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ sleep 120
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
  [XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ dcmanager kube-upgrade-strategy create --group ${subcloud_group}
+------------------------+----------------------------+
| Field                  | Value                      |
+------------------------+----------------------------+
| strategy type          | kubernetes                 |
| subcloud apply type    | parallel                   |
| max parallel subclouds | 50                         |
| stop on failure        | False                      |
| state                  | initial                    |
| created_at             | 2023-10-24T20:04:16.728866 |
| updated_at             | None                       |
+------------------------+----------------------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ dcmanager strategy-step list -c cloud -c stage -c state
+----------------------+-------+---------+
| cloud                | stage | state   |
+----------------------+-------+---------+
| welktxef-d931887-021 |     1 | initial |
| welktxef-d931856-008 |     1 | initial |
+----------------------+-------+---------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ dcmanager kube-upgrade-strategy apply
+------------------------+----------------------------+
| Field                  | Value                      |
+------------------------+----------------------------+
| strategy type          | kubernetes                 |
| subcloud apply type    | parallel                   |
| max parallel subclouds | 50                         |
| stop on failure        | False                      |
| state                  | applying                   |
| created_at             | 2023-10-24T20:04:16.728866 |
| updated_at             | 2023-10-24T20:04:31.245768 |
+------------------------+----------------------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

Every 15.0s: dcmanager strategy-step list -c cloud -c state -c details --max-width ...  Tue Oct 24 20:04:54 2023

+----------------------+-----------------------------------------+---------+
| cloud                | state                                   | details |
+----------------------+-----------------------------------------+---------+
| welktxef-d931887-021 | kube creating vim kube upgrade strategy |         |
| welktxef-d931856-008 | kube creating vim kube upgrade strategy |         |
+----------------------+-----------------------------------------+---------+

Every 15.0s: dcmanager strategy-step list -c cloud -c state -c details --max-width ...  Tue Oct 24 20:07:16 2023

+----------------------+-----------------------------------------+-----------------------------+
| cloud                | state                                   | details                     |
+----------------------+-----------------------------------------+-----------------------------+
| welktxef-d931887-021 | kube applying vim kube upgrade strategy | apply phase is 11% complete |
| welktxef-d931856-008 | kube applying vim kube upgrade strategy | apply phase is 11% complete |
+----------------------+-----------------------------------------+-----------------------------+

Every 15.0s: dcmanager strategy-step list -c cloud -c state -c details --max-width ...  Tue Oct 24 20:24:40 2023

+----------------------+----------+---------+
| cloud                | state    | details |
+----------------------+----------+---------+
| welktxef-d931887-021 | complete |         |
| welktxef-d931856-008 | complete |         |
+----------------------+----------+---------+

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ dcmanager kube-upgrade-strategy delete
+------------------------+----------------------------+
| Field                  | Value                      |
+------------------------+----------------------------+
| strategy type          | kubernetes                 |
| subcloud apply type    | parallel                   |
| max parallel subclouds | 50                         |
| stop on failure        | False                      |
| state                  | deleting                   |
| created_at             | 2023-10-24T20:04:16.728866 |
| updated_at             | 2023-10-24T20:25:08.484490 |
+------------------------+----------------------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ watch dcmanager kube-upgrade-strategy show
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

Every 2.0s: dcmanager kube-upgrade-strategy show                                        Tue Oct 24 20:26:31 2023

ERROR (app) Strategy of type 'kubernetes' not found

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./cleanup-old-pods_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook --inventory subclouds --ask-pass --user XXXXXX \
> cleanup-old-pods.yaml 0</dev/null
SSH password:

XXXXXX [all] *********************************************************************

TASK [Fetch pods in failed state] **********************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Delete failed pods] ******************************************************

PLAY RECAP *********************************************************************
welktxef-d931856-008       : ok=1    changed=1    unreachable=0    failed=0
welktxef-d931887-021       : ok=1    changed=1    unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./apply-kubelet-config_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook --inventory subclouds --ask-pass --user XXXXXX apply-kubelet-config.yaml \
> 0</dev/null
SSH password:

XXXXXX [all] *********************************************************************

TASK [Remove kubelet-config settings for old versions] *************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Reapply kubelet-config settings] *****************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Wait for kubelet-config settings to be applied] **************************
FAILED - RETRYING: Wait for kubelet-config settings to be applied (10 retries left).
FAILED - RETRYING: Wait for kubelet-config settings to be applied (10 retries left).
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Output kubelet-config info] **********************************************
ok: [welktxef-d931887-021] => {
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
ok: [welktxef-d931856-008] => {
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
welktxef-d931856-008       : ok=4    changed=3    unreachable=0    failed=0
welktxef-d931887-021       : ok=4    changed=3    unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ sleep 120
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ for subcloud in $(dcmanager subcloud-group list-subclouds ${subcloud_group} -f value -c name); do
> dcmanager subcloud show ${subcloud} | awk -F \| -v SUBCLOUD=${subcloud} \
> '$2 ~ / kubernetes_sync_status / { gsub(/ /,"",$3);printf("%-40s: %s\n",SUBCLOUD,$3) }'
> done
welktxef-d931887-021                    : out-of-sync
welktxef-d931856-008                    : out-of-sync
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ dcmanager kube-upgrade-strategy create --group ${subcloud_group}
+------------------------+----------------------------+
| Field                  | Value                      |
+------------------------+----------------------------+
| strategy type          | kubernetes                 |
| subcloud apply type    | parallel                   |
| max parallel subclouds | 50                         |
| stop on failure        | False                      |
| state                  | initial                    |
| created_at             | 2023-10-24T20:51:45.874632 |
| updated_at             | None                       |
+------------------------+----------------------------+

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ dcmanager strategy-step list -c cloud -c stage -c state
+----------------------+-------+---------+
| cloud                | stage | state   |
+----------------------+-------+---------+
| welktxef-d931887-021 |     1 | initial |
| welktxef-d931856-008 |     1 | initial |
+----------------------+-------+---------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ dcmanager kube-upgrade-strategy apply
+------------------------+----------------------------+
| Field                  | Value                      |
+------------------------+----------------------------+
| strategy type          | kubernetes                 |
| subcloud apply type    | parallel                   |
| max parallel subclouds | 50                         |
| stop on failure        | False                      |
| state                  | applying                   |
| created_at             | 2023-10-24T20:51:45.874632 |
| updated_at             | 2023-10-24T20:52:11.298259 |
+------------------------+----------------------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

Every 15.0s: dcmanager strategy-step list -c cloud -c state -c details --max-width ...  Tue Oct 24 21:05:34 2023

+----------------------+----------+---------+
| cloud                | state    | details |
+----------------------+----------+---------+
| welktxef-d931887-021 | complete |         |
| welktxef-d931856-008 | complete |         |
+----------------------+----------+---------+

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ dcmanager kube-upgrade-strategy delete
+------------------------+----------------------------+
| Field                  | Value                      |
+------------------------+----------------------------+
| strategy type          | kubernetes                 |
| subcloud apply type    | parallel                   |
| max parallel subclouds | 50                         |
| stop on failure        | False                      |
| state                  | deleting                   |
| created_at             | 2023-10-24T20:51:45.874632 |
| updated_at             | 2023-10-24T21:06:09.658604 |
+------------------------+----------------------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ watch dcmanager kube-upgrade-strategy show
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./cleanup-old-pods_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook --inventory subclouds --ask-pass --user XXXXXX \
> cleanup-old-pods.yaml 0</dev/null
SSH password:

XXXXXX [all] *********************************************************************

TASK [Fetch pods in failed state] **********************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Delete failed pods] ******************************************************

PLAY RECAP *********************************************************************
welktxef-d931856-008       : ok=1    changed=1    unreachable=0    failed=0
welktxef-d931887-021       : ok=1    changed=1    unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./apply-kubelet-config_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook --inventory subclouds --ask-pass --user XXXXXX apply-kubelet-config.yaml \
> 0</dev/null
SSH password:

XXXXXX [all] *********************************************************************

TASK [Remove kubelet-config settings for old versions] *************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Reapply kubelet-config settings] *****************************************
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Wait for kubelet-config settings to be applied] **************************
FAILED - RETRYING: Wait for kubelet-config settings to be applied (10 retries left).
FAILED - RETRYING: Wait for kubelet-config settings to be applied (10 retries left).
changed: [welktxef-d931856-008]
changed: [welktxef-d931887-021]

TASK [Output kubelet-config info] **********************************************
ok: [welktxef-d931887-021] => {
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
ok: [welktxef-d931856-008] => {
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
welktxef-d931856-008       : ok=4    changed=3    unreachable=0    failed=0
welktxef-d931887-021       : ok=4    changed=3    unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ sleep 120

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ for subcloud in $(dcmanager subcloud-group list-subclouds ${subcloud_group} -f value -c name); do
> dcmanager subcloud show ${subcloud} | awk -F \| -v SUBCLOUD=${subcloud} \
> '$2 ~ / kubernetes_sync_status / { gsub(/ /,"",$3);printf("%-40s: %s\n",SUBCLOUD,$3) }'
> done
welktxef-d931887-021                    : in-sync
welktxef-d931856-008                    : in-sync
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$





```



### upgrade was a success, no issue with BMC .45 on these two subcloud upgrades.

```log

```