# ZT Proteus .46 BMC firmware validation
# ZT Proteus BIOS .23
# 1/29/24 James Patchett

## Target Controller rchltxib-c000000-003
Controller-0 iLO 2607:f160:a:d02e:cd:fe0::8006 
Controller-1 iLO 2607:f160:a:d02e:cd:fe0::8007
Worker-0 iLO 2607:f160:a:d02e:cd:fe0::8008 
OAM 2607:f160:0:3049:cd:290:0:10

## Target Subcloud welktxef-d931856-008
OAM: 2607:f160:10:80b1:ce:40a:0:f408
BMC: 2607:f160:10:80b1:ce:40a:0:e008

ipmitool -I lanplus -U XXXXXX -P XXXXXX -H 2607:f160:10:80b1:ce:40a:0:e008 sol activate

## Baseline record of controller and subcloud
### Controller:

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ system show
+------------------------+--------------------------------------+
| Property               | Value                                |
+------------------------+--------------------------------------+
| contact                | demo.contact@verizon.com            |
| created_at             | 2024-01-18T00:40:33.250920+00:00     |
| description            | Wind River Cloud Platform 21.05      |
| distributed_cloud_role | systemcontroller                     |
| https_enabled          | True                                 |
| latitude               | None                                 |
| location               | None                                 |
| longitude              | None                                 |
| name                   | rchltxib-c000000-003                 |
| region_name            | RegionOne                            |
| sdn_enabled            | False                                |
| security_feature       | spectre_meltdown_v1                  |
| service_project_name   | services                             |
| software_version       | 21.12                                |
| system_mode            | duplex                               |
| system_type            | Standard                             |
| timezone               | UTC                                  |
| updated_at             | 2024-01-26T23:27:36.478975+00:00     |
| uuid                   | dbdde529-5c44-414c-a95c-5a95297c22ad |
| vswitch_type           | none                                 |
+------------------------+--------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ fm alarm-list
+----------+------------------------------------------------------------+-----------------------+----------+-------------+
| Alarm ID | Reason Text                                                | Entity ID             | Severity | Time Stamp  |
+----------+------------------------------------------------------------+-----------------------+----------+-------------+
| 280.002  | welktxef-d931856-008 kubernetes sync_status is out-of-sync | subcloud=             | major    | 2024-01-27T |
|          |                                                            | welktxef-d931856-008. |          | 01:05:39.   |
|          |                                                            | resource=kubernetes   |          | 487968      |
|          |                                                            |                       |          |             |
| 280.002  | welktxef-d931856-008 load sync_status is out-of-sync       | subcloud=             | major    | 2024-01-26T |
|          |                                                            | welktxef-d931856-008. |          | 23:27:40.   |
|          |                                                            | resource=load         |          | 834882      |
|          |                                                            |                       |          |             |
+----------+------------------------------------------------------------+-----------------------+----------+-------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ system application-list
+--------------------------+----------+-----------------------------------+-----------------------+----------+--------------+
| application              | version  | manifest name                     | manifest file         | status   | progress     |
+--------------------------+----------+-----------------------------------+-----------------------+----------+--------------+
| cert-manager             | 21.12-28 | cert-manager-manifest             | certmanager-manifest. | applied  | completed    |
|                          |          |                                   | yaml                  |          |              |
|                          |          |                                   |                       |          |              |
| nginx-ingress-controller | 21.12-18 | nginx-ingress-controller-manifest | nginx_ingress_control | applied  | Application  |
|                          |          |                                   | ler_manifest.yaml     |          | update from  |
|                          |          |                                   |                       |          | version 21.  |
|                          |          |                                   |                       |          | 05-16 to     |
|                          |          |                                   |                       |          | version 21.  |
|                          |          |                                   |                       |          | 12-18        |
|                          |          |                                   |                       |          | completed.   |
|                          |          |                                   |                       |          |              |
| oidc-auth-apps           | 21.12-61 | oidc-auth-manifest                | manifest.yaml         | applied  | completed    |
| platform-integ-apps      | 21.12-46 | platform-integration-manifest     | manifest.yaml         | uploaded | completed    |
| rook-ceph-apps           | 1.0-5    | rook-ceph-manifest                | manifest.yaml         | uploaded | completed    |
+--------------------------+----------+-----------------------------------+-----------------------+----------+--------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ sw-patch query
      Patch ID         RR  Release  Patch State
=====================  ==  =======  ===========
WRCP_21.05_PATCH_0001  N    21.05    Committed
WRCP_21.05_PATCH_0002  Y    21.05    Committed
WRCP_21.05_PATCH_0003  N    21.05    Committed
WRCP_21.05_PATCH_0004  N    21.05    Committed
WRCP_21.05_PATCH_0005  N    21.05     Applied
WRCP_21.05_PATCH_0006  N    21.05     Applied
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

[XXXXXX@controller-0 ~(keystone_admin)]$ dcmanager subcloud list
+----+----------------------+------------+--------------+-----------------+-------------+
| id | name                 | management | availability | deploy status   | sync        |
+----+----------------------+------------+--------------+-----------------+-------------+
|  3 | welktxef-d931856-008 | managed    | online       | prestage-failed | out-of-sync |
+----+----------------------+------------+--------------+-----------------+-------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ dcmanager subcloud show welktxef-d931856-008
+-----------------------------+---------------------------------+
| Field                       | Value                           |
+-----------------------------+---------------------------------+
| id                          | 3                               |
| name                        | welktxef-d931856-008            |
| description                 | Wind River Cloud Platform 21.05 |
| location                    | welktxef-d931856-008            |
| software_version            | 21.05                           |
| management                  | managed                         |
| availability                | online                          |
| deploy_status               | prestage-failed                 |
| management_subnet           | 2607:f160:10:80bb::/64          |
| management_start_ip         | 2607:f160:10:80bb:ce:40a::      |
| management_end_ip           | 2607:f160:10:80bb:ce:40a:0:f    |
| management_gateway_ip       | 2607:f160:10:80bb:ce:23::       |
| systemcontroller_gateway_ip | 2607:f160:0:3048:cd:28::        |
| group_id                    | 1                               |
| created_at                  | 2024-01-18 18:24:54.661389      |
| updated_at                  | 2024-01-27 03:44:39.090921      |
| dc-cert_sync_status         | in-sync                         |
| firmware_sync_status        | in-sync                         |
| identity_sync_status        | in-sync                         |
| kubernetes_sync_status      | out-of-sync                     |
| kube-rootca_sync_status     | in-sync                         |
| load_sync_status            | out-of-sync                     |
| patching_sync_status        | in-sync                         |
| platform_sync_status        | in-sync                         |
+-----------------------------+---------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$
```


### Subclouds firmware query 
```log
[XXXXXX@vcpe-jumpserver ~]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/UpdateService/FirmwareInventory/BMC | jq .
{
  "@odata.context": "/redfish/v1/$metadata#SoftwareInventory.SoftwareInventory",
  "@odata.etag": "\"1706206759\"",
  "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/BMC",
  "@odata.type": "#SoftwareInventory.v1_2_3.SoftwareInventory",
  "Id": "BMC",
  "Name": "BMC",
  "Updateable": true,
  "Version": "0.46.00"
}
[XXXXXX@vcpe-jumpserver ~]$

```

### Following Wrapper MOP 21.12p10 to install subclouds

### 21.12P10 upgrade mop 4 Subclouds Starting at section 3

```log
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ cd /opt/platform-backup/upgrade/wrcp-21.12-upgrade
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ sudo show-certs.sh | grep -E '^\s+Residual Time'
Password:
	 XXXXXX Time	:  388d
	 Residual Time	:  353d
	 Residual Time	:  57d
	 Residual Time	:  2458d
	 Residual Time	:  4155d
	 Residual Time	:  2459d
	 Residual Time	:  1813d
	 Residual Time	:  168d
	 Residual Time	:  3647d
	 Residual Time	:  363d
	 Residual Time	:  363d
	 Residual Time	:  363d
	 Residual Time	:  354d
	 Residual Time	:  4155d
	 Residual Time	:  4155d
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
| updated_at             | 2024-01-27 03:42:05.256686 |
+------------------------+----------------------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ echo '[subclouds]' > subclouds
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ dcmanager subcloud-group list-subclouds ${subcloud_group} -c name -f value >> subclouds
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ for subcloud in $(sed -n '/subclouds/ { :a; n; p; ba; }' < subclouds); do
> echo ${subcloud}
> dcmanager subcloud show ${subcloud} | \
> grep sync_status | \
> grep -E -v "in-sync|load_sync|kubernetes_sync|firmware_sync|dc-cert_sync";
> done
welktxef-d931856-008
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ names=$(dcmanager subcloud-group list-subclouds ${subcloud_group} --format value \
> --column name | xargs printf "'%s'," | head -c -1)
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ sudo -u XXXXXX psql --tuples-only --pset pager=off --dbname dcmanager --command \
> "select name from subclouds where data_install = '' and name in (${names})"

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./cleanup-images_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook --inventory subclouds --ask-pass --user XXXXXX \
> cleanup-images.yaml 0</dev/null
SSH password:

XXXXXX [all] *********************************************************************

TASK [Remove container images] *************************************************
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931856-008
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931856-008
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931856-008
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931856-008
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931856-008
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931856-008
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931856-008
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931856-008
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931856-008
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931856-008
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931856-008
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931856-008
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931856-008
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931856-008
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931856-008
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931856-008
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931856-008
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931856-008
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for welktxef-d931856-008

TASK [Retrieve list of docker.elastic.co/beats/filebeat tags] ******************
changed: [welktxef-d931856-008]

TASK [Loop over all docker.elastic.co/beats/filebeat tags] *********************
changed: [welktxef-d931856-008] => (item=7.9.3)

TASK [Retrieve list of docker.elastic.co/beats/filebeat-oss tags] **************
changed: [welktxef-d931856-008]

TASK [Loop over all docker.elastic.co/beats/filebeat-oss tags] *****************

TASK [Retrieve list of docker.elastic.co/beats/metricbeat tags] ****************
changed: [welktxef-d931856-008]

TASK [Loop over all docker.elastic.co/beats/metricbeat tags] *******************

TASK [Retrieve list of docker.elastic.co/beats/metricbeat-oss tags] ************
changed: [welktxef-d931856-008]

TASK [Loop over all docker.elastic.co/beats/metricbeat-oss tags] ***************

TASK [Retrieve list of docker.elastic.co/elasticsearch/elasticsearch tags] *****
changed: [welktxef-d931856-008]

TASK [Loop over all docker.elastic.co/elasticsearch/elasticsearch tags] ********

TASK [Retrieve list of docker.elastic.co/elasticsearch/elasticsearch-oss tags] ***
changed: [welktxef-d931856-008]

TASK [Loop over all docker.elastic.co/elasticsearch/elasticsearch-oss tags] ****

TASK [Retrieve list of docker.elastic.co/kibana/kibana tags] *******************
changed: [welktxef-d931856-008]

TASK [Loop over all docker.elastic.co/kibana/kibana tags] **********************

TASK [Retrieve list of docker.elastic.co/kibana/kibana-oss tags] ***************
changed: [welktxef-d931856-008]

TASK [Loop over all docker.elastic.co/kibana/kibana-oss tags] ******************

TASK [Retrieve list of docker.elastic.co/logstash/logstash tags] ***************
changed: [welktxef-d931856-008]

TASK [Loop over all docker.elastic.co/logstash/logstash tags] ******************

TASK [Retrieve list of docker.elastic.co/logstash/logstash-oss tags] ***********
changed: [welktxef-d931856-008]

TASK [Loop over all docker.elastic.co/logstash/logstash-oss tags] **************

TASK [Retrieve list of quay.io/coreos/kube-state-metrics tags] *****************
changed: [welktxef-d931856-008]

TASK [Loop over all quay.io/coreos/kube-state-metrics tags] ********************
changed: [welktxef-d931856-008] => (item=v1.9.7)

TASK [Retrieve list of quay.io/kubernetes-ingress-controller/nginx-ingress-controller tags] ***
changed: [welktxef-d931856-008]

TASK [Loop over all quay.io/kubernetes-ingress-controller/nginx-ingress-controller tags] ***

TASK [Retrieve list of docker.io/wind-river/elastic-services tags] *************
changed: [welktxef-d931856-008]

TASK [Loop over all docker.io/wind-river/elastic-services tags] ****************
changed: [welktxef-d931856-008] => (item=WRA.21.06-00)

TASK [Retrieve list of docker.io/wind-river/wra-kibana tags] *******************
changed: [welktxef-d931856-008]

TASK [Loop over all docker.io/wind-river/wra-kibana tags] **********************
changed: [welktxef-d931856-008] => (item=WRA.21.06-00)

TASK [Retrieve list of docker.io/wind-river/wra-metricbeat tags] ***************
changed: [welktxef-d931856-008]

TASK [Loop over all docker.io/wind-river/wra-metricbeat tags] ******************
changed: [welktxef-d931856-008] => (item=WRA.21.06-00)

TASK [Retrieve list of docker.io/wind-river/wra-elasticsearch tags] ************
changed: [welktxef-d931856-008]

TASK [Loop over all docker.io/wind-river/wra-elasticsearch tags] ***************
changed: [welktxef-d931856-008] => (item=WRA.21.06-01)

TASK [Retrieve list of docker.io/wind-river/wra-logstash tags] *****************
changed: [welktxef-d931856-008]

TASK [Loop over all docker.io/wind-river/wra-logstash tags] ********************
changed: [welktxef-d931856-008] => (item=WRA.21.06-01)

TASK [Retrieve list of docker.io/wind-river/cloud-platform-deployment-manager tags] ***
changed: [welktxef-d931856-008]

TASK [Loop over all docker.io/wind-river/cloud-platform-deployment-manager tags] ***
changed: [welktxef-d931856-008] => (item=WRCP_21.05)

TASK [Retrieve list of docker.io/starlingx/k8s-cni-sriov tags] *****************
changed: [welktxef-d931856-008]

TASK [Loop over all docker.io/starlingx/k8s-cni-sriov tags] ********************
changed: [welktxef-d931856-008] => (item=stx.5.0-v2.6-7-gb18123d8)

TASK [Garbage collect] *********************************************************
changed: [welktxef-d931856-008]

TASK [Wait for 250.001 alarm to clear] *****************************************
FAILED - RETRYING: Wait for 250.001 alarm to clear (60 retries left).
FAILED - RETRYING: Wait for 250.001 alarm to clear (59 retries left).
FAILED - RETRYING: Wait for 250.001 alarm to clear (58 retries left).
changed: [welktxef-d931856-008]

PLAY RECAP *********************************************************************
welktxef-d931856-008       : ok=49   changed=30   unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./cleanup-unused-images_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook --inventory subclouds --ask-pass --user XXXXXX \
> cleanup-unused-images.yaml 0</dev/null
SSH password:

XXXXXX [all] *********************************************************************

TASK [Retrieve application info output] ****************************************
changed: [welktxef-d931856-008]

TASK [Save application namespace and image as fact] ****************************
skipping: [welktxef-d931856-008]

TASK [Retrieve application tag output] *****************************************
skipping: [welktxef-d931856-008]

TASK [Save application tag as fact] ********************************************
skipping: [welktxef-d931856-008]

TASK [Output variables] ********************************************************
skipping: [welktxef-d931856-008]

TASK [Remove unused images] ****************************************************
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-unused-images.yaml for welktxef-d931856-008
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-unused-images.yaml for welktxef-d931856-008
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-unused-images.yaml for welktxef-d931856-008
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-unused-images.yaml for welktxef-d931856-008
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-unused-images.yaml for welktxef-d931856-008
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-unused-images.yaml for welktxef-d931856-008
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-unused-images.yaml for welktxef-d931856-008
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-unused-images.yaml for welktxef-d931856-008
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-unused-images.yaml for welktxef-d931856-008
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-unused-images.yaml for welktxef-d931856-008
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-unused-images.yaml for welktxef-d931856-008
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-unused-images.yaml for welktxef-d931856-008
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-unused-images.yaml for welktxef-d931856-008
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-unused-images.yaml for welktxef-d931856-008

TASK [Retrieve list of vzw-adpf-cmp tags] **************************************
changed: [welktxef-d931856-008]

TASK [Loop over all vzw-adpf-cmp tags] *****************************************

TASK [Retrieve list of vzw-adpf-dip tags] **************************************
changed: [welktxef-d931856-008]

TASK [Loop over all vzw-adpf-dip tags] *****************************************

TASK [Retrieve list of vzw-adpf-dmp tags] **************************************
changed: [welktxef-d931856-008]

TASK [Loop over all vzw-adpf-dmp tags] *****************************************

TASK [Retrieve list of vzw-adpf-dpp tags] **************************************
changed: [welktxef-d931856-008]

TASK [Loop over all vzw-adpf-dpp tags] *****************************************

TASK [Retrieve list of vzw-adpf-init tags] *************************************
changed: [welktxef-d931856-008]

TASK [Loop over all vzw-adpf-init tags] ****************************************

TASK [Retrieve list of vzw-adpf-pmp tags] **************************************
changed: [welktxef-d931856-008]

TASK [Loop over all vzw-adpf-pmp tags] *****************************************

TASK [Retrieve list of vzw-adpf-rmp tags] **************************************
changed: [welktxef-d931856-008]

TASK [Loop over all vzw-adpf-rmp tags] *****************************************

TASK [Retrieve list of vzw-uadpf-cmp tags] *************************************
changed: [welktxef-d931856-008]

TASK [Loop over all vzw-uadpf-cmp tags] ****************************************

TASK [Retrieve list of vzw-uadpf-dip tags] *************************************
changed: [welktxef-d931856-008]

TASK [Loop over all vzw-uadpf-dip tags] ****************************************

TASK [Retrieve list of vzw-uadpf-dmp tags] *************************************
changed: [welktxef-d931856-008]

TASK [Loop over all vzw-uadpf-dmp tags] ****************************************

TASK [Retrieve list of vzw-uadpf-dpp tags] *************************************
changed: [welktxef-d931856-008]

TASK [Loop over all vzw-uadpf-dpp tags] ****************************************

TASK [Retrieve list of vzw-uadpf-init tags] ************************************
changed: [welktxef-d931856-008]

TASK [Loop over all vzw-uadpf-init tags] ***************************************

TASK [Retrieve list of vzw-uadpf-pmp tags] *************************************
changed: [welktxef-d931856-008]

TASK [Loop over all vzw-uadpf-pmp tags] ****************************************

TASK [Retrieve list of vzw-uadpf-rmp tags] *************************************
changed: [welktxef-d931856-008]

TASK [Loop over all vzw-uadpf-rmp tags] ****************************************

TASK [Garbage collect] *********************************************************
changed: [welktxef-d931856-008]

TASK [Wait for 250.001 alarm to clear] *****************************************
FAILED - RETRYING: Wait for 250.001 alarm to clear (60 retries left).
FAILED - RETRYING: Wait for 250.001 alarm to clear (59 retries left).
FAILED - RETRYING: Wait for 250.001 alarm to clear (58 retries left).
changed: [welktxef-d931856-008]

PLAY RECAP *********************************************************************
welktxef-d931856-008       : ok=31   changed=17   unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ local_registry_pass=XXXXXX
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_ROLES_PATH=/usr/share/ansible/stx-ansible/playbooks/roles ANSIBLE_LOG_PATH=./local-registry-size_$(date "+%Y%m%d%H%M%S").log ansible-playbook --inventory subclouds --extra-vars "local_registry_pass=${local_registry_pass}" --ask-pass --ask-become-pass --user XXXXXX calculate-user-local-registry-size.yaml 0</dev/null
SSH password:
XXXXXX password[defaults to SSH password]:

PLAY [all] *********************************************************************

TASK [Validate local_registry_pass] ********************************************
skipping: [welktxef-d931856-008]

TASK [common/load-images-information : Set kubernetes long version] ************
ok: [welktxef-d931856-008]

TASK [common/load-images-information : Get the list of kubernetes images] ******
changed: [welktxef-d931856-008]

TASK [common/load-images-information : set_fact] *******************************
ok: [welktxef-d931856-008]

TASK [common/load-images-information : Read in system images list] *************
ok: [welktxef-d931856-008]

TASK [common/load-images-information : Check if additional image config file exists] ***
ok: [welktxef-d931856-008]

TASK [common/load-images-information : Read in additional system images list(s) in localhost] ***
skipping: [welktxef-d931856-008]

TASK [common/load-images-information : Create a temporary file on remote] ******
changed: [welktxef-d931856-008]

TASK [common/load-images-information : Fetch the additional images config in case the playbook is executed remotely] ***
changed: [welktxef-d931856-008]

TASK [common/load-images-information : Read in additional system images list(s) fetched from remote] ***
ok: [welktxef-d931856-008]

TASK [common/load-images-information : Remove the temporary file on remote] ****
changed: [welktxef-d931856-008 -> welktxef-d931856-008]

TASK [common/load-images-information : Remove override temp file on Ansible control host] ***
changed: [welktxef-d931856-008 -> localhost]

TASK [common/load-images-information : Categorize system images] ***************
ok: [welktxef-d931856-008]

TASK [common/load-images-information : Append additional static images if provisioned] ***
ok: [welktxef-d931856-008] => (item={'key': u'deploy_manager_img', 'value': u'docker.io/wind-river/cloud-platform-deployment-manager:WRCP_21.05'})
ok: [welktxef-d931856-008] => (item={'key': u'kube_rbac_proxy_img', 'value': u'gcr.io/kubebuilder/kube-rbac-proxy:v0.4.0'})

TASK [common/load-images-information : Append RVMC image for a DC system controller] ***
skipping: [welktxef-d931856-008]

TASK [common/load-images-information : Append additional static images for a DC system controller if provisioned] ***
skipping: [welktxef-d931856-008] => (item={'key': u'rbd_provisioner_img', 'value': u'quay.io/external_storage/rbd-provisioner:v2.1.1-k8s1.11'})
skipping: [welktxef-d931856-008] => (item={'key': u'ceph_config_helper_img', 'value': u'docker.io/starlingx/ceph-config-helper:v1.15.0'})

TASK [Set platform images list] ************************************************
ok: [welktxef-d931856-008]

TASK [Create a temporary file on remote] ***************************************
changed: [welktxef-d931856-008]

TASK [Correct permissions for temporary file on remote] ************************
changed: [welktxef-d931856-008]

TASK [Save list of local registry images excluding apps images to file] ********
changed: [welktxef-d931856-008]

TASK [Read file] ***************************************************************
changed: [welktxef-d931856-008]

TASK [Load list of local registry images from file] ****************************
ok: [welktxef-d931856-008]

TASK [Subtract platform images from local registry images] *********************
ok: [welktxef-d931856-008]

TASK [Append local registry host:port to image names] **************************
ok: [welktxef-d931856-008]

TASK [debug] *******************************************************************
ok: [welktxef-d931856-008] => {
    "image_list": [
        "registry.local:9001/docker.io/starlingx/n3000-opae:stx.4.0-v1.0.0",
        "registry.local:9001/docker.io/lwolf/kubectl_deployer:0.4",
        "registry.local:9001/docker.io/zookeeper:3.5.5",
        "registry.local:9001/quay.io/airshipit/armada:8a1638098f88d92bf799ef4934abe569789b885e-ubuntu_bionic",
        "registry.local:9001/gcr.io/kubernetes-helm/tiller:v2.16.1",
        "registry.local:9001/docker.io/confluentinc/cp-kafka:5.0.1",
        "registry.local:9001/docker.io/danielqsj/kafka-exporter:v1.2.0",
        "registry.local:9001/docker.io/josdotso/zookeeper-exporter:v1.1.2",
        "registry.local:9001/k8s.gcr.io/defaultbackend-amd64:1.5"
    ]
}

TASK [Log in to local registry] ************************************************
changed: [welktxef-d931856-008]

TASK [Pull images from local registry to docker filesystem] ********************
changed: [welktxef-d931856-008] => (item=registry.local:9001/docker.io/starlingx/n3000-opae:stx.4.0-v1.0.0)
changed: [welktxef-d931856-008] => (item=registry.local:9001/docker.io/lwolf/kubectl_deployer:0.4)
changed: [welktxef-d931856-008] => (item=registry.local:9001/docker.io/zookeeper:3.5.5)
changed: [welktxef-d931856-008] => (item=registry.local:9001/quay.io/airshipit/armada:8a1638098f88d92bf799ef4934abe569789b885e-ubuntu_bionic)
changed: [welktxef-d931856-008] => (item=registry.local:9001/gcr.io/kubernetes-helm/tiller:v2.16.1)
changed: [welktxef-d931856-008] => (item=registry.local:9001/docker.io/confluentinc/cp-kafka:5.0.1)
changed: [welktxef-d931856-008] => (item=registry.local:9001/docker.io/danielqsj/kafka-exporter:v1.2.0)
changed: [welktxef-d931856-008] => (item=registry.local:9001/docker.io/josdotso/zookeeper-exporter:v1.1.2)
changed: [welktxef-d931856-008] => (item=registry.local:9001/k8s.gcr.io/defaultbackend-amd64:1.5)

TASK [Set format parameter for docker inspect to retrieve only the size] *******
ok: [welktxef-d931856-008]

TASK [Get docker images size in bytes] *****************************************
changed: [welktxef-d931856-008] => (item=registry.local:9001/docker.io/starlingx/n3000-opae:stx.4.0-v1.0.0)
changed: [welktxef-d931856-008] => (item=registry.local:9001/docker.io/lwolf/kubectl_deployer:0.4)
changed: [welktxef-d931856-008] => (item=registry.local:9001/docker.io/zookeeper:3.5.5)
changed: [welktxef-d931856-008] => (item=registry.local:9001/quay.io/airshipit/armada:8a1638098f88d92bf799ef4934abe569789b885e-ubuntu_bionic)
changed: [welktxef-d931856-008] => (item=registry.local:9001/gcr.io/kubernetes-helm/tiller:v2.16.1)
changed: [welktxef-d931856-008] => (item=registry.local:9001/docker.io/confluentinc/cp-kafka:5.0.1)
changed: [welktxef-d931856-008] => (item=registry.local:9001/docker.io/danielqsj/kafka-exporter:v1.2.0)
changed: [welktxef-d931856-008] => (item=registry.local:9001/docker.io/josdotso/zookeeper-exporter:v1.1.2)
changed: [welktxef-d931856-008] => (item=registry.local:9001/k8s.gcr.io/defaultbackend-amd64:1.5)

TASK [Parse docker images size] ************************************************
ok: [welktxef-d931856-008] => (item=registry.local:9001/docker.io/starlingx/n3000-opae:stx.4.0-v1.0.0, 506492391 bytes)
ok: [welktxef-d931856-008] => (item=registry.local:9001/docker.io/lwolf/kubectl_deployer:0.4, 82474353 bytes)
ok: [welktxef-d931856-008] => (item=registry.local:9001/docker.io/zookeeper:3.5.5, 225210868 bytes)
ok: [welktxef-d931856-008] => (item=registry.local:9001/quay.io/airshipit/armada:8a1638098f88d92bf799ef4934abe569789b885e-ubuntu_bionic, 457539381 bytes)
ok: [welktxef-d931856-008] => (item=registry.local:9001/gcr.io/kubernetes-helm/tiller:v2.16.1, 91160017 bytes)
ok: [welktxef-d931856-008] => (item=registry.local:9001/docker.io/confluentinc/cp-kafka:5.0.1, 557414026 bytes)
ok: [welktxef-d931856-008] => (item=registry.local:9001/docker.io/danielqsj/kafka-exporter:v1.2.0, 15387401 bytes)
ok: [welktxef-d931856-008] => (item=registry.local:9001/docker.io/josdotso/zookeeper-exporter:v1.1.2, 11828993 bytes)
ok: [welktxef-d931856-008] => (item=registry.local:9001/k8s.gcr.io/defaultbackend-amd64:1.5, 5132544 bytes)

TASK [debug] *******************************************************************
ok: [welktxef-d931856-008] => {
    "docker_images_size": "1952639974"
}

TASK [Remove pulled images] ****************************************************
changed: [welktxef-d931856-008]

TASK [Scale to KiB and reserve 5% for docker metadata inside exported archive] ***
ok: [welktxef-d931856-008]

TASK [Determine available space in /opt/platform-backup] ***********************
changed: [welktxef-d931856-008]

TASK [Fail if there is not enough free space to create docker images backup archive] ***
skipping: [welktxef-d931856-008]

TASK [Remove the temporary file from remote] ***********************************
changed: [welktxef-d931856-008]

PLAY RECAP *********************************************************************
welktxef-d931856-008       : ok=31   changed=15   unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./sanity_$(date "+%Y%m%d%H%M%S").log ansible-playbook --inventory subclouds --extra-vars "scenario=before" --ask-pass --ask-become-pass --user XXXXXX pre-deployment-subclouds.yaml 0</dev/null
SSH password:
XXXXXX password[defaults to SSH password]:

PLAY [all] *********************************************************************

TASK [Gathering Facts] *********************************************************
ok: [welktxef-d931856-008]

TASK [Read in parameter file] **************************************************
ok: [welktxef-d931856-008]

TASK [set expected Fortville firmware version] *********************************
ok: [welktxef-d931856-008]

TASK [set expected N3000 firmware version] *************************************
ok: [welktxef-d931856-008]

TASK [create directory /home/XXXXXX/sanity] **********************************
ok: [welktxef-d931856-008 -> localhost]

TASK [delete existing file /home/XXXXXX/sanity/output_list] ******************
changed: [welktxef-d931856-008 -> localhost]

TASK [create file /home/XXXXXX/sanity/output_list] ***************************
changed: [welktxef-d931856-008 -> localhost]

TASK [get host patch status] ***************************************************
changed: [welktxef-d931856-008]

TASK [validate host patch status] **********************************************
skipping: [welktxef-d931856-008]

TASK [get host status] *********************************************************
changed: [welktxef-d931856-008]

TASK [validate host status] ****************************************************
skipping: [welktxef-d931856-008]

TASK [get current alarms] ******************************************************
changed: [welktxef-d931856-008]

TASK [validate current alarms] *************************************************
skipping: [welktxef-d931856-008]

TASK [get vim status] **********************************************************
changed: [welktxef-d931856-008]

TASK [validate vim status] *****************************************************
skipping: [welktxef-d931856-008]

TASK [calculate / partition expected usage] ************************************
changed: [welktxef-d931856-008]

TASK [validate / partition free space] *****************************************
skipping: [welktxef-d931856-008]

TASK [validate /opt/dc-vault partition free space] *****************************
skipping: [welktxef-d931856-008]

TASK [identify N3000 NICs] *****************************************************
changed: [welktxef-d931856-008]

TASK [get N3000 NICs firmware version] *****************************************

TASK [validate N3000 NICs firmware version] ************************************

TASK [get N3000 NICs MAC] ******************************************************

TASK [validate N3000 NICs MACs] ************************************************

TASK [identify Fortville NICs] *************************************************
changed: [welktxef-d931856-008]

TASK [get Fortville NICs firmware version] *************************************

TASK [validate Fortville NICs firmware version] ********************************

TASK [get Fortville NICs MAC] **************************************************

TASK [validate Fortville NICs MACs] ********************************************

TASK [identify accelerators] ***************************************************
changed: [welktxef-d931856-008]

TASK [retrieve device information] *********************************************
changed: [welktxef-d931856-008] => (item=pci_0000_51_00_0)

TASK [output device show information] ******************************************
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
        "| sriov_numvfs          | 0                                |",
        "| sriov_vfs_pci_address |                                  |",
        "| sriov_vf_pdevice_id   | None                             |",
        "| extra_info            | None                             |",
        "| created_at            | 2024-01-18T18:55:37.574824+00:00 |",
        "| updated_at            | 2024-01-25T18:02:53.736107+00:00 |",
        "| root_key              | None                             |",
        "| revoked_key_ids       | None                             |",
        "| boot_page             | None                             |",
        "| bitstream_id          | None                             |",
        "| bmc_build_version     | None                             |",
        "| bmc_fw_version        | None                             |",
        "| driver                | None                             |",
        "| sriov_vf_driver       | None                             |",
        "+-----------------------+----------------------------------+"
    ]
}

TASK [retrieve device information] *********************************************
changed: [welktxef-d931856-008] => (item=pci_0000_51_00_0)

TASK [output field information] ************************************************
ok: [welktxef-d931856-008] => (item=pci_0000_51_00_0) => {
    "msg": "0|None|None|None"
}

TASK [validate sriov_numvfs for Mount Bryce] ***********************************
skipping: [welktxef-d931856-008] => (item=pci_0000_51_00_0)

TASK [validate driver and sriov_vf_driver fields] ******************************
skipping: [welktxef-d931856-008] => (item=pci_0000_51_00_0)

TASK [validate extra_info field] ***********************************************
skipping: [welktxef-d931856-008] => (item=pci_0000_51_00_0)

TASK [get pod status] **********************************************************
changed: [welktxef-d931856-008]

TASK [validate pod status] *****************************************************
changed: [welktxef-d931856-008 -> localhost]

TASK [get system applications] *************************************************
changed: [welktxef-d931856-008]

TASK [validate system applications] ********************************************
skipping: [welktxef-d931856-008] => (item=cert-manager:21.05-17)
skipping: [welktxef-d931856-008] => (item=nginx-ingress-controller:21.05-16)
skipping: [welktxef-d931856-008] => (item=oidc-auth-apps:21.05-44)
skipping: [welktxef-d931856-008] => (item=platform-integ-apps:21.05-30)

PLAY [all] *********************************************************************

TASK [Gathering Facts] *********************************************************
ok: [welktxef-d931856-008]

TASK [validate /opt/platform-backup partition free space] **********************
skipping: [welktxef-d931856-008]

TASK [validate /opt/platform-backup partition type] ****************************
skipping: [welktxef-d931856-008]

TASK [Collect previous backups] ************************************************
ok: [welktxef-d931856-008]

TASK [Delete previous backups] *************************************************

TASK [Get /home size] **********************************************************
changed: [welktxef-d931856-008]

TASK [validate /home size] *****************************************************
skipping: [welktxef-d931856-008]

PLAY RECAP *********************************************************************
welktxef-d931856-008       : ok=25   changed=16   unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ cat /home/XXXXXX/sanity/output_list
welktxef-d931856-008 - check pod status
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./fix-backup-system_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook --inventory subclouds --ask-pass --ask-become-pass --user XXXXXX \
> fix-backup-system.yaml 0</dev/null
SSH password:
XXXXXX password[defaults to SSH password]:

PLAY [all] *********************************************************************

TASK [Add fail task to backup-system rescue block] *****************************
changed: [welktxef-d931856-008]

PLAY RECAP *********************************************************************
welktxef-d931856-008       : ok=1    changed=1    unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./health-query-upgrade_$(date "+%Y%m%d%H%M%S").log ansible all --inventory subclouds --ask-pass --user XXXXXX --module-name shell --args "source /etc/platform/openrc; system health-query-upgrade"
SSH password:
XXXXXX | CHANGED | rc=0 >>
System Health:
All hosts are provisioned: [OK]
All hosts are unlocked/enabled: [OK]
All hosts have current configurations: [OK]
All hosts are patch current: [OK]
Ceph Storage Healthy: [OK]
No alarms: [OK]
All kubernetes nodes are ready: [OK]
All kubernetes control plane pods are ready: [OK]
No imported load found. Unable to test further

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$




```
### Prechecks done, moving to deploymnet steps

### set MWAIT enable on subclouds

```log
[XXXXXX@vcpe-jumpserver ~]$ curl --globoff -L -w "\\n%{http_code} %{url_effective}\\n" -u XXXXXX:XXXXXX -k -H "Content-Type: application/json" -d '{"Attributes": {"PMS012": "Enable"}}' -X PATCH https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/Systems/Self/Bios/SD

204 https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/Systems/Self/Bios/SD
[XXXXXX@vcpe-jumpserver ~]$

```

### starting section 4 Deployment of Mop 4 subclouds

```log

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ source /etc/platform/openrc
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ cd /opt/platform-backup/upgrade/wrcp-21.12-upgrade
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ dcmanager upgrade-strategy create --group ${subcloud_group}
ERROR (app) Bad strategy request: Strategy of type: 'upgrade' already exists
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ dcmanager strategy-step list -c cloud -c stage -c state
+----------------------+-------+---------+
| cloud                | stage | state   |
+----------------------+-------+---------+
| welktxef-d931856-008 |     1 | initial |
+----------------------+-------+---------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ dcmanager upgrade-strategy apply
+------------------------+----------------------------+
| Field                  | Value                      |
+------------------------+----------------------------+
| strategy type          | upgrade                    |
| subcloud apply type    | parallel                   |
| max parallel subclouds | 50                         |
| stop on failure        | False                      |
| state                  | applying                   |
| created_at             | 2024-01-29T19:30:12.025101 |
| updated_at             | 2024-01-29T19:30:46.643525 |
+------------------------+----------------------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$


Every 15.0s: dcmanager strategy-step list -c cloud -c state -c details --max-width 100 --sort-column...  Mon Jan 29 19:31:04 2024

+----------------------+--------------------+---------+
| cloud                | state              | details |
+----------------------+--------------------+---------+
| welktxef-d931856-008 | installing license |         |
+----------------------+--------------------+---------+


Every 15.0s: dcmanager strategy-step list -c cloud -c state -c details --max-width 100 --sort-column...  Mon Jan 29 19:31:36 2024

+----------------------+------------------+---------+
| cloud                | state            | details |
+----------------------+------------------+---------+
| welktxef-d931856-008 | starting upgrade |         |
+----------------------+------------------+---------+


Every 15.0s: dcmanager strategy-step list -c cloud -c state -c details --max-width 100 --sort-column...  Mon Jan 29 19:41:55 2024

+----------------------+-------------------+---------+
| cloud                | state             | details |
+----------------------+-------------------+---------+
| welktxef-d931856-008 | upgrading simplex |         |
+----------------------+-------------------+---------+

Every 15.0s: dcmanager strategy-step list -c cloud -c state -c details --max-width 100 --sort-column...  Mon Jan 29 20:00:07 2024

+----------------------+----------------+---------+
| cloud                | state          | details |
+----------------------+----------------+---------+
| welktxef-d931856-008 | migrating data |         |
+----------------------+----------------+---------+


Every 15.0s: dcmanager strategy-step list -c cloud -c state -c details --max-width 100 --sort-column...  Mon Jan 29 20:17:31 2024

+----------------------+----------------+---------+
| cloud                | state          | details |
+----------------------+----------------+---------+
| welktxef-d931856-008 | migrating data |         |
+----------------------+----------------+---------+

Every 15.0s: dcmanager strategy-step list -c cloud -c state -c details --max-width 100 --sort-column...  Mon Jan 29 20:47:18 2024

+----------------------+--------------------+---------+
| cloud                | state              | details |
+----------------------+--------------------+---------+
| welktxef-d931856-008 | activating upgrade |         |
+----------------------+--------------------+---------+



Every 15.0s: dcmanager strategy-step list -c cloud -c state -c details --max-width 100 --sort-column...  Mon Jan 29 21:14:54 2024

+----------------------+----------+---------+
| cloud                | state    | details |
+----------------------+----------+---------+
| welktxef-d931856-008 | complete |         |
+----------------------+----------+---------+

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ dcmanager upgrade-strategy delete
+------------------------+----------------------------+
| Field                  | Value                      |
+------------------------+----------------------------+
| strategy type          | upgrade                    |
| subcloud apply type    | parallel                   |
| max parallel subclouds | 50                         |
| stop on failure        | False                      |
| state                  | deleting                   |
| created_at             | 2024-01-29T19:30:12.025101 |
| updated_at             | 2024-01-29T21:15:17.213413 |
+------------------------+----------------------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./set-intel-driver-version_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook --inventory subclouds --ask-pass --user XXXXXX \
> set-intel-driver-version.yaml 0</dev/null
SSH password:

XXXXXX [all] *********************************************************************

TASK [Retrieve platform release version] ***************************************
changed: [welktxef-d931856-008]

TASK [Retrieve intel_nic_driver_version service parameter] *********************
changed: [welktxef-d931856-008]

TASK [Store service parameter field values] ************************************
ok: [welktxef-d931856-008]

TASK [Delete old intel_nic_driver_version service parameter with resource] *****
changed: [welktxef-d931856-008]

TASK [Clear the driver version] ************************************************
ok: [welktxef-d931856-008]

TASK [Set Intel driver version (with resource)] ********************************
skipping: [welktxef-d931856-008]

TASK [Set Intel driver version] ************************************************
changed: [welktxef-d931856-008]

TASK [Apply service parameters] ************************************************
changed: [welktxef-d931856-008]

TASK [Retrieve current Intel driver version] ***********************************
changed: [welktxef-d931856-008]

PLAY RECAP *********************************************************************
welktxef-d931856-008       : ok=8    changed=6    unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./lock-unlock_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook --inventory subclouds --ask-pass --user XXXXXX lock-unlock.yaml \
> 0</dev/null
SSH password:

XXXXXX [all] *********************************************************************

TASK [Check if host is already locked] *****************************************
changed: [welktxef-d931856-008]

TASK [Lock host] ***************************************************************
changed: [welktxef-d931856-008]

TASK [Wait for host to enter locked state] *************************************
changed: [welktxef-d931856-008]

TASK [Unlock host] *************************************************************
changed: [welktxef-d931856-008]

PLAY RECAP *********************************************************************
welktxef-d931856-008       : ok=4    changed=4    unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
watch dcmanager subcloud-group list-subclouds ${subcloud_group} -f value -c name -c availability

[XXXXXX@controller-0 ~(keystone_admin)]$ cd /opt/platform-backup/upgrade/wrcp-21.12-upgrade/
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./confirm-ice-driver-version_$(date "+%Y%m%d%H%M%S").log ansible all --inventory subclouds --ask-pass --ask-become-pass --user XXXXXX --become --module-name shell --args "grep -E 'ice\:.*1\.5\.8$' /var/log/dmesg"
SSH password:
XXXXXX password[defaults to SSH password]:
welktxef-d931856-008 | CHANGED | rc=0 >>
[   11.380027] ice: Intel(R) Ethernet Connection E800 Series Linux Driver - version 1.5.8

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

[XXXXXX@controller-0 ~(keystone_admin)]$ cd /opt/platform-backup/upgrade/wrcp-21.12-upgrade/
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./confirm-ice-driver-version_$(date "+%Y%m%d%H%M%S").log ansible all --inventory subclouds --ask-pass --ask-become-pass --user XXXXXX --become --module-name shell --args "grep -E 'ice\:.*1\.5\.8$' /var/log/dmesg"
SSH password:
XXXXXX password[defaults to SSH password]:
welktxef-d931856-008 | CHANGED | rc=0 >>
[   11.380027] ice: Intel(R) Ethernet Connection E800 Series Linux Driver - version 1.5.8

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./dm_delete_old_secret_$(date "+%Y%m%d%H%M%S").log \
> ansible all --inventory subclouds --ask-pass --user XXXXXX --module-name shell \
> --args "kubectl --kubeconfig /etc/kubernetes/admin.conf delete secret \
> -n platform-deployment-manager platform-deployment-manager-webhook-server-secret"
SSH password:
XXXXXX | CHANGED | rc=0 >>
secret "platform-deployment-manager-webhook-server-secret" deleted

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ subcloud_group=Default
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ for subcloud in $(dcmanager subcloud-group list-subclouds ${subcloud_group} -f value -c name); do dcmanager subcloud reconfig --XXXXXX-password ${XXXXXX_password} --deploy-config subclouds-deployment-config.yaml ${subcloud}; done
+-----------------------------+---------------------------------+
| Field                       | Value                           |
+-----------------------------+---------------------------------+
| id                          | 3                               |
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
| systemcontroller_gateway_ip | 2607:f160:0:3048:cd:28::        |
| group_id                    | 1                               |
| created_at                  | 2024-01-18T18:24:54.661389      |
| updated_at                  | 2024-01-29T21:50:32.989763      |
+-----------------------------+---------------------------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

Every 2.0s: dcmanager subcloud-group list-subclouds Default -c name -c deploy_status                     Mon Jan 29 21:51:19 2024

+----------------------+---------------+
| name                 | deploy_status |
+----------------------+---------------+
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
platform-deployment-manager-0   2/2     Running   2          56s
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
ok: [welktxef-d931856-008]

TASK [Get Ip Controller] *******************************************************
changed: [welktxef-d931856-008]

TASK [debug] *******************************************************************
ok: [welktxef-d931856-008] => {
    "msg": "controller ip: 2607:f160:10:80bb:ce:40a::"
}

TASK [Install Deployment Manager Monitor] **************************************
changed: [welktxef-d931856-008]

TASK [Wait for Deployment Manager Monitor to be ready] *************************
changed: [welktxef-d931856-008]

PLAY RECAP *********************************************************************
welktxef-d931856-008       : ok=5    changed=3    unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$


[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./metrics-server-upgrade_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook --inventory subclouds --ask-pass --user XXXXXX app-upgrade.yaml \
> --extra-vars="application=metrics-server" \
> 0</dev/null
SSH password:

XXXXXX [all] *********************************************************************

TASK [Copy application overrides to the subcloud] ******************************
skipping: [welktxef-d931856-008]

TASK [Apply application overrides] *********************************************
skipping: [welktxef-d931856-008]

TASK [Remove override file] ****************************************************
skipping: [welktxef-d931856-008]

TASK [Retrieve latest application version] *************************************
changed: [welktxef-d931856-008]

TASK [Upgrade application] *****************************************************
changed: [welktxef-d931856-008]

TASK [Check if application is applied] *****************************************
FAILED - RETRYING: Check if application is applied (60 retries left).
FAILED - RETRYING: Check if application is applied (59 retries left).
FAILED - RETRYING: Check if application is applied (58 retries left).
FAILED - RETRYING: Check if application is applied (57 retries left).
FAILED - RETRYING: Check if application is applied (56 retries left).
FAILED - RETRYING: Check if application is applied (55 retries left).
FAILED - RETRYING: Check if application is applied (54 retries left).
changed: [welktxef-d931856-008]

PLAY RECAP *********************************************************************
welktxef-d931856-008       : ok=3    changed=3    unreachable=0    failed=0

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

TASK [Delete failed pods] ******************************************************

PLAY RECAP *********************************************************************
welktxef-d931856-008       : ok=1    changed=1    unreachable=0    failed=0

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

TASK [Read in parameter file] **************************************************
ok: [welktxef-d931856-008]

TASK [set expected Fortville firmware version] *********************************
ok: [welktxef-d931856-008]

TASK [set expected N3000 firmware version] *************************************
ok: [welktxef-d931856-008]

TASK [create directory /home/XXXXXX/sanity] **********************************
ok: [welktxef-d931856-008 -> localhost]

TASK [delete existing file /home/XXXXXX/sanity/output_list] ******************
changed: [welktxef-d931856-008 -> localhost]

TASK [create file /home/XXXXXX/sanity/output_list] ***************************
changed: [welktxef-d931856-008 -> localhost]

TASK [get host patch status] ***************************************************
changed: [welktxef-d931856-008]

TASK [validate host patch status] **********************************************
skipping: [welktxef-d931856-008]

TASK [get host status] *********************************************************
changed: [welktxef-d931856-008]

TASK [validate host status] ****************************************************
skipping: [welktxef-d931856-008]

TASK [get current alarms] ******************************************************
changed: [welktxef-d931856-008]

TASK [validate current alarms] *************************************************
skipping: [welktxef-d931856-008]

TASK [get vim status] **********************************************************
changed: [welktxef-d931856-008]

TASK [validate vim status] *****************************************************
skipping: [welktxef-d931856-008]

TASK [calculate / partition expected usage] ************************************
changed: [welktxef-d931856-008]

TASK [validate / partition free space] *****************************************
skipping: [welktxef-d931856-008]

TASK [validate /opt/dc-vault partition free space] *****************************
skipping: [welktxef-d931856-008]

TASK [identify N3000 NICs] *****************************************************
changed: [welktxef-d931856-008]

TASK [get N3000 NICs firmware version] *****************************************

TASK [validate N3000 NICs firmware version] ************************************

TASK [get N3000 NICs MAC] ******************************************************

TASK [validate N3000 NICs MACs] ************************************************

TASK [identify Fortville NICs] *************************************************
changed: [welktxef-d931856-008]

TASK [get Fortville NICs firmware version] *************************************

TASK [validate Fortville NICs firmware version] ********************************

TASK [get Fortville NICs MAC] **************************************************

TASK [validate Fortville NICs MACs] ********************************************

TASK [identify accelerators] ***************************************************
changed: [welktxef-d931856-008]

TASK [retrieve device information] *********************************************
changed: [welktxef-d931856-008] => (item=pci_0000_51_00_0)

TASK [output device show information] ******************************************
ok: [welktxef-d931856-008] => (item=pci_0000_51_00_0) => {
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
        "| created_at            | 2024-01-18T18:55:37.574824+00:00                                            |",
        "| updated_at            | 2024-01-29T21:29:56.920450+00:00                                            |",
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
changed: [welktxef-d931856-008] => (item=pci_0000_51_00_0)

TASK [output field information] ************************************************
ok: [welktxef-d931856-008] => (item=pci_0000_51_00_0) => {
    "msg": "0|{'expected_driver':None,'expected_vf_driver':None,'expected_numvfs':0}|None|None"
}

TASK [validate sriov_numvfs for Mount Bryce] ***********************************
skipping: [welktxef-d931856-008] => (item=pci_0000_51_00_0)

TASK [validate driver and sriov_vf_driver fields] ******************************
skipping: [welktxef-d931856-008] => (item=pci_0000_51_00_0)

TASK [validate extra_info field] ***********************************************
skipping: [welktxef-d931856-008] => (item=pci_0000_51_00_0)

TASK [get pod status] **********************************************************
changed: [welktxef-d931856-008]

TASK [validate pod status] *****************************************************
changed: [welktxef-d931856-008 -> localhost]

TASK [get system applications] *************************************************
changed: [welktxef-d931856-008]

TASK [validate system applications] ********************************************
skipping: [welktxef-d931856-008] => (item=cert-manager:21.12-28)
skipping: [welktxef-d931856-008] => (item=nginx-ingress-controller:21.12-18)
skipping: [welktxef-d931856-008] => (item=oidc-auth-apps:21.12-61)
skipping: [welktxef-d931856-008] => (item=platform-integ-apps:21.12-46)

PLAY RECAP *********************************************************************
welktxef-d931856-008       : ok=22   changed=15   unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./resize_fs_$(date "+%Y%m%d%H%M%S").log ansible-playbook --inventory subclouds --ask-pass --user XXXXXX --extra-vars '{"partitions":[1000],"hfs_docker":250,"cfs_docker_distribution":100}' resize_fs.yaml 0</dev/null
SSH password:

XXXXXX [all] *********************************************************************

TASK [Retrieve list of controllers] ********************************************
changed: [welktxef-d931856-008]

TASK [Retrieve distributed cloud role] *****************************************
changed: [welktxef-d931856-008]

TASK [Confirm cgts volumes] ****************************************************
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/confirm_cgts_volumes.yaml for welktxef-d931856-008

TASK [Retrieve rootfs disk] ****************************************************
changed: [welktxef-d931856-008]

TASK [Retrieve available space on the rootfs device] ***************************
changed: [welktxef-d931856-008]

TASK [set_fact] ****************************************************************
ok: [welktxef-d931856-008]

TASK [Retrieve partitions present on the rootfs device] ************************
changed: [welktxef-d931856-008]

TASK [Validate number of partitions requested] *********************************
skipping: [welktxef-d931856-008]

TASK [Validate requested partition sizes] **************************************
skipping: [welktxef-d931856-008] => (item=[None, 1000])

TASK [Determine amount of free space after all partitions are allocated] *******
ok: [welktxef-d931856-008] => (item=[None, 1000])

TASK [Display amount of free space after all partitions are allocated] *********
ok: [welktxef-d931856-008] => {
    "msg": "558"
}

TASK [Verify there is enough space to allocate all partitions] *****************
skipping: [welktxef-d931856-008]

TASK [Create new volumes] ******************************************************
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/create_cgts_volume.yaml for welktxef-d931856-008 => (item=[None, 1000])

TASK [Create a new disk partition] *********************************************
changed: [welktxef-d931856-008]

TASK [fail] ********************************************************************
skipping: [welktxef-d931856-008]

TASK [Wait for the new partition to be ready] **********************************
FAILED - RETRYING: Wait for the new partition to be ready (200 retries left).
FAILED - RETRYING: Wait for the new partition to be ready (199 retries left).
FAILED - RETRYING: Wait for the new partition to be ready (198 retries left).
changed: [welktxef-d931856-008]

TASK [Add the new partition to the cgts volume group] **************************
changed: [welktxef-d931856-008]

TASK [fail] ********************************************************************
skipping: [welktxef-d931856-008]

TASK [Wait for the physical volume to be provisioned] **************************
FAILED - RETRYING: Wait for the physical volume to be provisioned (200 retries left).
FAILED - RETRYING: Wait for the physical volume to be provisioned (199 retries left).
FAILED - RETRYING: Wait for the physical volume to be provisioned (198 retries left).
FAILED - RETRYING: Wait for the physical volume to be provisioned (197 retries left).
FAILED - RETRYING: Wait for the physical volume to be provisioned (196 retries left).
changed: [welktxef-d931856-008]

TASK [Retrieve controller filesystems and sizes] *******************************
changed: [welktxef-d931856-008]

TASK [Store requested controller filesystem sizes] *****************************
ok: [welktxef-d931856-008] => (item=docker-distribution 32)
ok: [welktxef-d931856-008] => (item=database 10)
ok: [welktxef-d931856-008] => (item=etcd 5)
ok: [welktxef-d931856-008] => (item=extension 1)
ok: [welktxef-d931856-008] => (item=platform 10)

TASK [Build controller filesystem resizing parms] ******************************
ok: [welktxef-d931856-008] => (item=docker-distribution 32)
skipping: [welktxef-d931856-008] => (item=database 10)
skipping: [welktxef-d931856-008] => (item=etcd 5)
skipping: [welktxef-d931856-008] => (item=extension 1)
skipping: [welktxef-d931856-008] => (item=platform 10)

TASK [Resize all controller filesystems] ***************************************
changed: [welktxef-d931856-008]

TASK [Wait for all controller filesystems to be resized and fully sync] ********
FAILED - RETRYING: Wait for all controller filesystems to be resized and fully sync (720 retries left).
FAILED - RETRYING: Wait for all controller filesystems to be resized and fully sync (719 retries left).
FAILED - RETRYING: Wait for all controller filesystems to be resized and fully sync (718 retries left).
FAILED - RETRYING: Wait for all controller filesystems to be resized and fully sync (717 retries left).
changed: [welktxef-d931856-008]

TASK [Wait for any 400.001 alarm to clear] *************************************
changed: [welktxef-d931856-008]

TASK [Resize host filesystems] *************************************************
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/resize_hostfs.yaml for welktxef-d931856-008

TASK [Retrieve host filesystems and sizes] *************************************
changed: [welktxef-d931856-008]

TASK [Store requested host filesystem sizes] ***********************************
ok: [welktxef-d931856-008] => (item=backup 25)
ok: [welktxef-d931856-008] => (item=docker 30)
ok: [welktxef-d931856-008] => (item=kubelet 10)
ok: [welktxef-d931856-008] => (item=scratch 16)

TASK [Build hostfs resizing parms] *********************************************
skipping: [welktxef-d931856-008] => (item=backup 25)
ok: [welktxef-d931856-008] => (item=docker 30)
skipping: [welktxef-d931856-008] => (item=kubelet 10)
skipping: [welktxef-d931856-008] => (item=scratch 16)

TASK [Resize all host filesystems] *********************************************
changed: [welktxef-d931856-008]

TASK [Wait for any 250.001 alarm to clear] *************************************
FAILED - RETRYING: Wait for any 250.001 alarm to clear (300 retries left).
FAILED - RETRYING: Wait for any 250.001 alarm to clear (299 retries left).
FAILED - RETRYING: Wait for any 250.001 alarm to clear (298 retries left).
FAILED - RETRYING: Wait for any 250.001 alarm to clear (297 retries left).
FAILED - RETRYING: Wait for any 250.001 alarm to clear (296 retries left).
FAILED - RETRYING: Wait for any 250.001 alarm to clear (295 retries left).
FAILED - RETRYING: Wait for any 250.001 alarm to clear (294 retries left).
FAILED - RETRYING: Wait for any 250.001 alarm to clear (293 retries left).
FAILED - RETRYING: Wait for any 250.001 alarm to clear (292 retries left).
FAILED - RETRYING: Wait for any 250.001 alarm to clear (291 retries left).
changed: [welktxef-d931856-008]

PLAY RECAP *********************************************************************
welktxef-d931856-008       : ok=26   changed=16   unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

```

### K8 upgrade portion...

```log

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ system kube-version-list | awk -F \| '$4 ~ / active / { gsub(/ /,"",$2);print $2 }'
v1.21.8
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
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ echo $subcloud_group
Default
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
| updated_at             | 2024-01-27 03:42:05.256686 |
+------------------------+----------------------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ echo '[subclouds]' > subclouds
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ dcmanager subcloud-group list-subclouds ${subcloud_group} -c name -f value >> subclouds
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ for subcloud in $(sed -n '/subclouds/ { :a; n; p; ba; }' < subclouds); do
> echo ${subcloud}
> dcmanager subcloud show ${subcloud} | \
> grep sync_status | \
> grep -E -v "in-sync|kubernetes_sync|firmware_sync|dc-cert_sync";
> done
welktxef-d931856-008
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./sanity_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook --inventory subclouds --extra-vars "scenario=after" \
> --ask-pass --ask-become-pass --user XXXXXX \
> sanity.yaml 0</dev/null
SSH password:
XXXXXX password[defaults to SSH password]:

PLAY [all] *********************************************************************

TASK [Gathering Facts] *********************************************************
ok: [welktxef-d931856-008]

TASK [Read in parameter file] **************************************************
ok: [welktxef-d931856-008]

TASK [set expected Fortville firmware version] *********************************
ok: [welktxef-d931856-008]

TASK [set expected N3000 firmware version] *************************************
ok: [welktxef-d931856-008]

TASK [create directory /home/XXXXXX/sanity] **********************************
ok: [welktxef-d931856-008 -> localhost]

TASK [delete existing file /home/XXXXXX/sanity/output_list] ******************
changed: [welktxef-d931856-008 -> localhost]

TASK [create file /home/XXXXXX/sanity/output_list] ***************************
changed: [welktxef-d931856-008 -> localhost]

TASK [get host patch status] ***************************************************
changed: [welktxef-d931856-008]

TASK [validate host patch status] **********************************************
skipping: [welktxef-d931856-008]

TASK [get host status] *********************************************************
changed: [welktxef-d931856-008]

TASK [validate host status] ****************************************************
skipping: [welktxef-d931856-008]

TASK [get current alarms] ******************************************************
changed: [welktxef-d931856-008]

TASK [validate current alarms] *************************************************
skipping: [welktxef-d931856-008]

TASK [get vim status] **********************************************************
changed: [welktxef-d931856-008]

TASK [validate vim status] *****************************************************
skipping: [welktxef-d931856-008]

TASK [calculate / partition expected usage] ************************************
changed: [welktxef-d931856-008]

TASK [validate / partition free space] *****************************************
skipping: [welktxef-d931856-008]

TASK [validate /opt/dc-vault partition free space] *****************************
skipping: [welktxef-d931856-008]

TASK [identify N3000 NICs] *****************************************************
changed: [welktxef-d931856-008]

TASK [get N3000 NICs firmware version] *****************************************

TASK [validate N3000 NICs firmware version] ************************************

TASK [get N3000 NICs MAC] ******************************************************

TASK [validate N3000 NICs MACs] ************************************************

TASK [identify Fortville NICs] *************************************************
changed: [welktxef-d931856-008]

TASK [get Fortville NICs firmware version] *************************************

TASK [validate Fortville NICs firmware version] ********************************

TASK [get Fortville NICs MAC] **************************************************

TASK [validate Fortville NICs MACs] ********************************************

TASK [identify accelerators] ***************************************************
changed: [welktxef-d931856-008]

TASK [retrieve device information] *********************************************
changed: [welktxef-d931856-008] => (item=pci_0000_51_00_0)

TASK [output device show information] ******************************************
ok: [welktxef-d931856-008] => (item=pci_0000_51_00_0) => {
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
        "| created_at            | 2024-01-18T18:55:37.574824+00:00                                            |",
        "| updated_at            | 2024-01-29T21:29:56.920450+00:00                                            |",
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
changed: [welktxef-d931856-008] => (item=pci_0000_51_00_0)

TASK [output field information] ************************************************
ok: [welktxef-d931856-008] => (item=pci_0000_51_00_0) => {
    "msg": "0|{'expected_driver':None,'expected_vf_driver':None,'expected_numvfs':0}|None|None"
}

TASK [validate sriov_numvfs for Mount Bryce] ***********************************
skipping: [welktxef-d931856-008] => (item=pci_0000_51_00_0)

TASK [validate driver and sriov_vf_driver fields] ******************************
skipping: [welktxef-d931856-008] => (item=pci_0000_51_00_0)

TASK [validate extra_info field] ***********************************************
skipping: [welktxef-d931856-008] => (item=pci_0000_51_00_0)

TASK [get pod status] **********************************************************
changed: [welktxef-d931856-008]

TASK [validate pod status] *****************************************************
changed: [welktxef-d931856-008 -> localhost]

TASK [get system applications] *************************************************
changed: [welktxef-d931856-008]

TASK [validate system applications] ********************************************
skipping: [welktxef-d931856-008] => (item=cert-manager:21.12-28)
skipping: [welktxef-d931856-008] => (item=nginx-ingress-controller:21.12-18)
skipping: [welktxef-d931856-008] => (item=oidc-auth-apps:21.12-61)
skipping: [welktxef-d931856-008] => (item=platform-integ-apps:21.12-46)

PLAY RECAP *********************************************************************
welktxef-d931856-008       : ok=22   changed=15   unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ cat /home/XXXXXX/sanity/output_list
welktxef-d931856-008 - check pod status
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ cat /home/XXXXXX/sanity/output_list
welktxef-d931856-008 - check pod status
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ cd /opt/platform-backup/upgrade/wrcp-21.12-upgrade
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ dcmanager kube-upgrade-strategy create --group ${subcloud_group}
+------------------------+----------------------------+
| Field                  | Value                      |
+------------------------+----------------------------+
| strategy type          | kubernetes                 |
| subcloud apply type    | parallel                   |
| max parallel subclouds | 50                         |
| stop on failure        | False                      |
| state                  | initial                    |
| created_at             | 2024-01-29T22:18:33.694351 |
| updated_at             | None                       |
+------------------------+----------------------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ dcmanager strategy-step list -c cloud -c stage -c state
+----------------------+-------+---------+
| cloud                | stage | state   |
+----------------------+-------+---------+
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
| created_at             | 2024-01-29T22:18:33.694351 |
| updated_at             | 2024-01-29T22:18:49.868826 |
+------------------------+----------------------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

Every 15.0s: dcmanager strategy-step list -c cloud -c state -c details --max-width 100 --sort-column...  Mon Jan 29 22:19:27 2024

+----------------------+-----------------------------------------+---------+
| cloud                | state                                   | details |
+----------------------+-----------------------------------------+---------+
| welktxef-d931856-008 | kube applying vim kube upgrade strategy |         |
+----------------------+-----------------------------------------+---------+

Every 15.0s: dcmanager strategy-step list -c cloud -c state -c details --max-width 100 --sort-column...  Mon Jan 29 22:33:02 2024

+----------------------+----------+---------+
| cloud                | state    | details |
+----------------------+----------+---------+
| welktxef-d931856-008 | complete |         |
+----------------------+----------+---------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./cleanup-old-pods_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook --inventory subclouds --ask-pass --user XXXXXX \
> cleanup-old-pods.yaml 0</dev/null
SSH password:

XXXXXX [all] *********************************************************************

TASK [Fetch pods in failed state] **********************************************
changed: [welktxef-d931856-008]

TASK [Delete failed pods] ******************************************************

PLAY RECAP *********************************************************************
welktxef-d931856-008       : ok=1    changed=1    unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ watch -n15 dcmanager strategy-step list -c cloud -c state -c details \
> --max-width 100 --sort-column details --sort-column state
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ dcmanager kube-upgrade-strategy delete
+------------------------+----------------------------+
| Field                  | Value                      |
+------------------------+----------------------------+
| strategy type          | kubernetes                 |
| subcloud apply type    | parallel                   |
| max parallel subclouds | 50                         |
| stop on failure        | False                      |
| state                  | deleting                   |
| created_at             | 2024-01-29T22:18:33.694351 |
| updated_at             | 2024-01-29T22:33:31.142187 |
+------------------------+----------------------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./cleanup-old-pods_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook --inventory subclouds --ask-pass --user XXXXXX \
> cleanup-old-pods.yaml 0</dev/null
SSH password:

XXXXXX [all] *********************************************************************

TASK [Fetch pods in failed state] **********************************************
changed: [welktxef-d931856-008]

TASK [Delete failed pods] ******************************************************

PLAY RECAP *********************************************************************
welktxef-d931856-008       : ok=1    changed=1    unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./apply-kubelet-config_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook --inventory subclouds --ask-pass --user XXXXXX apply-kubelet-config.yaml \
> 0</dev/null
SSH password:

XXXXXX [all] *********************************************************************

TASK [Remove kubelet-config settings for old versions] *************************
fatal: [welktxef-d931856-008]: UNREACHABLE! => {"changed": false, "msg": "Authentication failure.", "unreachable": true}

PLAY RECAP *********************************************************************
welktxef-d931856-008       : ok=0    changed=0    unreachable=1    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./apply-kubelet-config_$(date "+%Y%m%d%H%M%S").log ansible-playbook --inventory subclouds --ask-pass --user XXXXXX apply-kubelet-config.yaml 0</dev/null
SSH password:

XXXXXX [all] *********************************************************************

TASK [Remove kubelet-config settings for old versions] *************************
changed: [welktxef-d931856-008]

TASK [Reapply kubelet-config settings] *****************************************
changed: [welktxef-d931856-008]

TASK [Wait for kubelet-config settings to be applied] **************************
FAILED - RETRYING: Wait for kubelet-config settings to be applied (10 retries left).
sleep 120
changed: [welktxef-d931856-008]

TASK [Output kubelet-config info] **********************************************
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

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ sleep 120

[XXXXXX@controller-0 ~(keystone_admin)]$ subcloud_group=Default
[XXXXXX@controller-0 ~(keystone_admin)]$
[XXXXXX@controller-0 ~(keystone_admin)]$ for subcloud in $(dcmanager subcloud-group list-subclouds ${subcloud_group} -f value -c name); do
> dcmanager subcloud show ${subcloud} | awk -F \| -v SUBCLOUD=${subcloud} \
> '$2 ~ / kubernetes_sync_status / { gsub(/ /,"",$3);printf("%-40s: %s\n",SUBCLOUD,$3) }'
> done
welktxef-d931856-008                    : out-of-sync
[XXXXXX@controller-0 ~(keystone_admin)]$ dcmanager kube-upgrade-strategy create --group ${subcloud_group}
+------------------------+----------------------------+
| Field                  | Value                      |
+------------------------+----------------------------+
| strategy type          | kubernetes                 |
| subcloud apply type    | parallel                   |
| max parallel subclouds | 50                         |
| stop on failure        | False                      |
| state                  | initial                    |
| created_at             | 2024-01-29T23:54:42.255348 |
| updated_at             | None                       |
+------------------------+----------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ dcmanager strategy-step list -c cloud -c stage -c state
+----------------------+-------+---------+
| cloud                | stage | state   |
+----------------------+-------+---------+
| welktxef-d931856-008 |     1 | initial |
+----------------------+-------+---------+
[XXXXXX@controller-0 ~(keystone_admin)]$ dcmanager kube-upgrade-strategy apply
+------------------------+----------------------------+
| Field                  | Value                      |
+------------------------+----------------------------+
| strategy type          | kubernetes                 |
| subcloud apply type    | parallel                   |
| max parallel subclouds | 50                         |
| stop on failure        | False                      |
| state                  | applying                   |
| created_at             | 2024-01-29T23:54:42.255348 |
| updated_at             | 2024-01-29T23:54:55.977399 |
+------------------------+----------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$

Every 15.0s: dcmanager strategy-step list -c cloud -c state -c details --max-width 100 --sort-column...  Tue Jan 30 00:09:46 2024

+----------------------+----------+---------+
| cloud                | state    | details |
+----------------------+----------+---------+
| welktxef-d931856-008 | complete |         |
+----------------------+----------+---------+


controller-0:~$ source /etc/platform/openrc
[XXXXXX@controller-0 ~(keystone_admin)]$ cd /opt/platform-backup/upgrade/wrcp-21.12-upgrade/
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ subcloud_group=Default
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./apply-kubelet-config_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook --inventory subclouds --ask-pass --user XXXXXX apply-kubelet-config.yaml \
> 0</dev/null
SSH password:

XXXXXX [all] *********************************************************************

TASK [Remove kubelet-config settings for old versions] *************************
changed: [welktxef-d931856-008]

TASK [Reapply kubelet-config settings] *****************************************
changed: [welktxef-d931856-008]

TASK [Wait for kubelet-config settings to be applied] **************************
FAILED - RETRYING: Wait for kubelet-config settings to be applied (10 retries left).
changed: [welktxef-d931856-008]

TASK [Output kubelet-config info] **********************************************
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

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$


Every 15.0s: dcmanager strategy-step list -c cloud -c state -c details --max-width 100 --sort-column...  Tue Jan 30 01:03:22 2024

+----------------------+----------+---------+
| cloud                | state    | details |
+----------------------+----------+---------+
| welktxef-d931856-008 | complete |         |
+----------------------+----------+---------+

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./apply-kubelet-config_$(date "+%Y%m%d%H%M%S").log ansible-playbook --inventory subclouds --ask-pass --user XXXXXX apply-kubelet-config.yaml 0</dev/null
SSH password:

XXXXXX [all] *********************************************************************

TASK [Remove kubelet-config settings for old versions] *************************
changed: [welktxef-d931856-008]

TASK [Reapply kubelet-config settings] *****************************************
changed: [welktxef-d931856-008]

TASK [Wait for kubelet-config settings to be applied] **************************
FAILED - RETRYING: Wait for kubelet-config settings to be applied (10 retries left).
changed: [welktxef-d931856-008]

TASK [Output kubelet-config info] **********************************************
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

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$




```


### upgrade was a success, no issue with BMC .46 on this subcloud .

```log
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ dcmanager subcloud list
+----+----------------------+------------+--------------+---------------+---------+
| id | name                 | management | availability | deploy status | sync    |
+----+----------------------+------------+--------------+---------------+---------+
|  3 | welktxef-d931856-008 | managed    | online       | complete      | in-sync |
+----+----------------------+------------+--------------+---------------+---------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ dcmanager subcloud show welktxef-d931856-008
+-----------------------------+---------------------------------+
| Field                       | Value                           |
+-----------------------------+---------------------------------+
| id                          | 3                               |
| name                        | welktxef-d931856-008            |
| description                 | Wind River Cloud Platform 21.05 |
| location                    | welktxef-d931856-008            |
| software_version            | 21.12                           |
| management                  | managed                         |
| availability                | online                          |
| deploy_status               | complete                        |
| management_subnet           | 2607:f160:10:80bb::/64          |
| management_start_ip         | 2607:f160:10:80bb:ce:40a::      |
| management_end_ip           | 2607:f160:10:80bb:ce:40a:0:f    |
| management_gateway_ip       | 2607:f160:10:80bb:ce:23::       |
| systemcontroller_gateway_ip | 2607:f160:0:3048:cd:28::        |
| group_id                    | 1                               |
| created_at                  | 2024-01-18 18:24:54.661389      |
| updated_at                  | 2024-01-29 21:51:04.980772      |
| dc-cert_sync_status         | in-sync                         |
| firmware_sync_status        | in-sync                         |
| identity_sync_status        | in-sync                         |
| kubernetes_sync_status      | in-sync                         |
| kube-rootca_sync_status     | in-sync                         |
| load_sync_status            | in-sync                         |
| patching_sync_status        | in-sync                         |
| platform_sync_status        | in-sync                         |
+-----------------------------+---------------------------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ sw-patch query
      Patch ID         RR  Release  Patch State
=====================  ==  =======  ===========
WRCP_21.05_PATCH_0001  N    21.05    Committed
WRCP_21.05_PATCH_0002  Y    21.05    Committed
WRCP_21.05_PATCH_0003  N    21.05    Committed
WRCP_21.05_PATCH_0004  N    21.05    Committed
WRCP_21.05_PATCH_0005  N    21.05     Applied
WRCP_21.05_PATCH_0006  N    21.05     Applied
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

Now we login to the subcloud
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ssh welktxef-d931856-008
The authenticity of host 'welktxef-d931856-008 (2607:f160:10:80bb:ce:40a::)' can't be established.
ECDSA key fingerprint is SHA256:0frNKZm0JFEDu/VnioFvrw15vKJs1lezjeh4W4j8Nww.
ECDSA key fingerprint is MD5:3e:82:ee:9f:0b:88:71:74:06:14:e4:b9:02:ee:67:ea.
Are you sure you want to continue connecting (yes/no)? yes
Warning: Permanently added 'welktxef-d931856-008,2607:f160:10:80bb:ce:40a::' (ECDSA) to the list of known hosts.
Release 21.12
------------------------------------------------------------------------
W A R N I N G *** W A R N I N G *** W A R N I N G *** W A R N I N G ***
------------------------------------------------------------------------
THIS IS A PRIVATE COMPUTER SYSTEM.
This computer system including all related equipment, network devices
(specifically including Internet access), are provided only for authorized use.
All computer systems may be monitored for all lawful purposes, including to
ensure that their use is authorized, for management of the system, to
facilitate protection against unauthorized access, and to verify security
procedures, survivability and operational security. Monitoring includes active
attacks by authorized personnel and their entities to test or verify the
security of the system. During monitoring, information may be examined,
recorded, copied and used for authorized purposes. All information including
personal information, placed on or sent over this system may be monitored. Uses
of this system, authorized or unauthorized, constitutes consent to monitoring
of this system. Unauthorized use may subject you to criminal prosecution.
Evidence of any such unauthorized use collected during monitoring may be used
for administrative, criminal or other adverse action. Use of this system
constitutes consent to monitoring for these purposes.

XXXXXX@welktxef-d931856-008's password:
XXXXXX login: Tue Jan 30 01:07:13 2024 from 2607:f160:0:3048:cd:290:0:11
/etc/motd.d/00-header:

WARNING: Unauthorized access to this system is forbidden and will be
prosecuted by law. By accessing this system, you agree that your
actions may be monitored if unauthorized usage is suspected.

/etc/motd.d/10-system:


====================================================================
         SYSTEM: welktxef-d931856-008
====================================================================

controller-0:~$ source /etc/platform/openrc `
> source /etc/platform/openrc `^C
controller-0:~$ source /etc/platform/openrc
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

[XXXXXX@controller-0 ~(keystone_admin)]$
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
[XXXXXX@controller-0 ~(keystone_admin)]$




```