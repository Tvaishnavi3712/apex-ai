# ZT .45 BMC firmware validation
# 21.05p6 upgrade to 21.12p10 with firmware installed in subcloud to 2.27
# 11/15/23 James Patchett

## Target Controller rchltxib-c000000-003 CR-3 (Richardson infrastructure System)
OAM: 2607:f160:0:3049:cd:290:0:10

## Subcloud rchltxfe-d93180012-001 (VCP-fe Infrastructure)
OAM: 2607:f160:10:9073:ce:40a:0:f400
ILO: 2607:f160:10:9073:ce:406:0:1000

ipmitool -I lanplus -U XXXXXX -P XXXXXX -H 2607:f160:10:9073:ce:406:0:1000 sol activate


### controller has been upgraded to 21.12p10, next step is to upgrade subcloud with triton 2.27 firmware

### Controller validation of 21.12p10 readyness
```log
[XXXXXX@controller-0 ~(keystone_admin)]$ system show
+------------------------+--------------------------------------+
| Property               | Value                                |
+------------------------+--------------------------------------+
| contact                | demo.contact@verizon.com            |
| created_at             | 2023-12-05T01:21:55.798101+00:00     |
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
| updated_at             | 2023-12-06T03:00:52.809897+00:00     |
| uuid                   | 7035e534-a268-4484-9fae-c8d27c3831a8 |
| vswitch_type           | none                                 |
+------------------------+--------------------------------------+
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

[XXXXXX@controller-0 ~(keystone_admin)]$ fm alarm-list
+---------+------------------------------------------------------------+-------------------------+----------+-------------+
| Alarm   | Reason Text                                                | Entity ID               | Severity | Time Stamp  |
| ID      |                                                            |                         |          |             |
+---------+------------------------------------------------------------+-------------------------+----------+-------------+
| 280.002 | rchltxfe-d93180012-001 kubernetes sync_status is out-of-   | subcloud=               | major    | 2023-12-06T |
|         | sync                                                       | rchltxfe-d93180012-001. |          | 21:59:18.   |
|         |                                                            | resource=kubernetes     |          | 027336      |
|         |                                                            |                         |          |             |
| 280.002 | rchltxfe-d93180012-001 load sync_status is out-of-sync     | subcloud=               | major    | 2023-12-06T |
|         |                                                            | rchltxfe-d93180012-001. |          | 03:16:54.   |
|         |                                                            | resource=load           |          | 023317      |
|         |                                                            |                         |          |             |
+---------+------------------------------------------------------------+-------------------------+----------+-------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ dcmanager subcloud list
+----+------------------------+------------+--------------+---------------+-------------+
| id | name                   | management | availability | deploy status | sync        |
+----+------------------------+------------+--------------+---------------+-------------+
|  2 | rchltxfe-d93180012-001 | managed    | online       | complete      | out-of-sync |
+----+------------------------+------------+--------------+---------------+-------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ dcmanager subcloud show rchltxfe-d93180012-001
+-----------------------------+---------------------------------+
| Field                       | Value                           |
+-----------------------------+---------------------------------+
| id                          | 2                               |
| name                        | rchltxfe-d93180012-001          |
| description                 | Wind River Cloud Platform 21.05 |
| location                    | rchltxfe-d93180012-001          |
| software_version            | 21.05                           |
| management                  | managed                         |
| availability                | online                          |
| deploy_status               | complete                        |
| management_subnet           | 2607:f160:10:907b::/64          |
| management_start_ip         | 2607:f160:10:907b:ce:40a::      |
| management_end_ip           | 2607:f160:10:907b:ce:40a:0:f    |
| management_gateway_ip       | 2607:f160:10:907b:ce:28::       |
| systemcontroller_gateway_ip | 2607:f160:0:3048:cd:28::        |
| group_id                    | 1                               |
| created_at                  | 2023-12-05 15:46:21.700016      |
| updated_at                  | 2023-12-07 19:32:51.434729      |
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
[XXXXXX@controller-0 ~(keystone_admin)]$ system application-list
+--------------------------+----------+-----------------------------------+-----------------------+----------+-------------+
| application              | version  | manifest name                     | manifest file         | status   | progress    |
+--------------------------+----------+-----------------------------------+-----------------------+----------+-------------+
| cert-manager             | 21.12-28 | cert-manager-manifest             | certmanager-manifest. | applied  | completed   |
|                          |          |                                   | yaml                  |          |             |
|                          |          |                                   |                       |          |             |
| nginx-ingress-controller | 21.12-18 | nginx-ingress-controller-manifest | nginx_ingress_control | applied  | Application |
|                          |          |                                   | ler_manifest.yaml     |          | update from |
|                          |          |                                   |                       |          | version 21. |
|                          |          |                                   |                       |          | 05-16 to    |
|                          |          |                                   |                       |          | version 21. |
|                          |          |                                   |                       |          | 12-18       |
|                          |          |                                   |                       |          | completed.  |
|                          |          |                                   |                       |          |             |
| oidc-auth-apps           | 21.12-61 | oidc-auth-manifest                | manifest.yaml         | applied  | completed   |
| platform-integ-apps      | 21.12-46 | platform-integration-manifest     | manifest.yaml         | uploaded | completed   |
| rook-ceph-apps           | 1.0-5    | rook-ceph-manifest                | manifest.yaml         | uploaded | completed   |
+--------------------------+----------+-----------------------------------+-----------------------+----------+-------------+
[XXXXXX@controller-0 ~(keystone_admin)]$

```
### Note that we removed WR-Analtyics as that is not necessary to test new bmc firmware, only interaction with BMC is in focus

### controller is ready for upgrade

### Subcloud upgrade starting

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ cd /opt/platform-backup/upgrade/wrcp-21.12-upgrade/
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ sudo show-certs.sh | grep -E '^\s+Residual Time'
Password:
	 XXXXXX Time	:  392d
	 Residual Time	:  357d
	 Residual Time	:  105d
	 Residual Time	:  2506d
	 Residual Time	:  4203d
	 Residual Time	:  2507d
	 Residual Time	:  1817d
	 Residual Time	:  172d
	 Residual Time	:  3643d
	 Residual Time	:  359d
	 Residual Time	:  359d
	 Residual Time	:  359d
	 Residual Time	:  358d
	 Residual Time	:  4203d
	 Residual Time	:  4203d
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
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ subcloud_group=subcloud-group
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ dcmanager subcloud-group update ${subcloud_group} \
> --update_apply_type parallel --max_parallel_subclouds 50
Subcloud Group not found
ERROR (app) Unable to update subcloud group subcloud-group
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ for subcloud in $(sed -n '/subclouds/ { :a; n; p; ba; }' < subclouds); do
> echo ${subcloud}
> dcmanager subcloud show ${subcloud} | \
> grep sync_status | \
> grep -E -v "in-sync|load_sync|kubernetes_sync|firmware_sync|dc-cert_sync";
> done
-bash: subclouds: No such file or directory
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$  subcloud_group=default
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ dcmanager subcloud-group update ${subcloud_group} \
> --update_apply_type parallel --max_parallel_subclouds 50
Subcloud Group not found
ERROR (app) Unable to update subcloud group default
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$  subcloud_group=Default
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ dcmanager subcloud-group update ${subcloud_group} --update_apply_type parallel --max_parallel_subclouds 50
+------------------------+----------------------------+
| Field                  | Value                      |
+------------------------+----------------------------+
| id                     | 1                          |
| name                   | Default                    |
| description            | Default Subcloud Group     |
| update apply type      | parallel                   |
| max parallel subclouds | 50                         |
| created_at             | None                       |
| updated_at             | 2023-12-12 19:52:04.436675 |
+------------------------+----------------------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ echo '[subclouds]' > subclouds
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ dcmanager subcloud-group list-subclouds ${subcloud_group} -c name -f value >> subclouds
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ for subcloud in $(sed -n '/subclouds/ { :a; n; p; ba; }' < subclouds); do
> echo ${subcloud}
> dcmanager subcloud show ${subcloud} | \
> grep sync_status | \
> grep -E -v "in-sync|load_sync|kubernetes_sync|firmware_sync|dc-cert_sync";
> done
rchltxfe-d93180012-001
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
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for rchltxfe-d93180012-001
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for rchltxfe-d93180012-001
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for rchltxfe-d93180012-001
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for rchltxfe-d93180012-001
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for rchltxfe-d93180012-001
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for rchltxfe-d93180012-001
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for rchltxfe-d93180012-001
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for rchltxfe-d93180012-001
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for rchltxfe-d93180012-001
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for rchltxfe-d93180012-001
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for rchltxfe-d93180012-001
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for rchltxfe-d93180012-001
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for rchltxfe-d93180012-001
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for rchltxfe-d93180012-001
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for rchltxfe-d93180012-001
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for rchltxfe-d93180012-001
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for rchltxfe-d93180012-001
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for rchltxfe-d93180012-001
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-images.yaml for rchltxfe-d93180012-001

TASK [Retrieve list of docker.elastic.co/beats/filebeat tags] ******************
changed: [rchltxfe-d93180012-001]

TASK [Loop over all docker.elastic.co/beats/filebeat tags] *********************
changed: [rchltxfe-d93180012-001] => (item=7.9.3)

TASK [Retrieve list of docker.elastic.co/beats/filebeat-oss tags] **************
changed: [rchltxfe-d93180012-001]

TASK [Loop over all docker.elastic.co/beats/filebeat-oss tags] *****************

TASK [Retrieve list of docker.elastic.co/beats/metricbeat tags] ****************
changed: [rchltxfe-d93180012-001]

TASK [Loop over all docker.elastic.co/beats/metricbeat tags] *******************

TASK [Retrieve list of docker.elastic.co/beats/metricbeat-oss tags] ************
changed: [rchltxfe-d93180012-001]

TASK [Loop over all docker.elastic.co/beats/metricbeat-oss tags] ***************

TASK [Retrieve list of docker.elastic.co/elasticsearch/elasticsearch tags] *****
changed: [rchltxfe-d93180012-001]

TASK [Loop over all docker.elastic.co/elasticsearch/elasticsearch tags] ********

TASK [Retrieve list of docker.elastic.co/elasticsearch/elasticsearch-oss tags] ***
changed: [rchltxfe-d93180012-001]

TASK [Loop over all docker.elastic.co/elasticsearch/elasticsearch-oss tags] ****

TASK [Retrieve list of docker.elastic.co/kibana/kibana tags] *******************
changed: [rchltxfe-d93180012-001]

TASK [Loop over all docker.elastic.co/kibana/kibana tags] **********************

TASK [Retrieve list of docker.elastic.co/kibana/kibana-oss tags] ***************
changed: [rchltxfe-d93180012-001]

TASK [Loop over all docker.elastic.co/kibana/kibana-oss tags] ******************

TASK [Retrieve list of docker.elastic.co/logstash/logstash tags] ***************
changed: [rchltxfe-d93180012-001]

TASK [Loop over all docker.elastic.co/logstash/logstash tags] ******************

TASK [Retrieve list of docker.elastic.co/logstash/logstash-oss tags] ***********
changed: [rchltxfe-d93180012-001]

TASK [Loop over all docker.elastic.co/logstash/logstash-oss tags] **************

TASK [Retrieve list of quay.io/coreos/kube-state-metrics tags] *****************
changed: [rchltxfe-d93180012-001]

TASK [Loop over all quay.io/coreos/kube-state-metrics tags] ********************
changed: [rchltxfe-d93180012-001] => (item=v1.9.7)

TASK [Retrieve list of quay.io/kubernetes-ingress-controller/nginx-ingress-controller tags] ***
changed: [rchltxfe-d93180012-001]

TASK [Loop over all quay.io/kubernetes-ingress-controller/nginx-ingress-controller tags] ***

TASK [Retrieve list of docker.io/wind-river/elastic-services tags] *************
changed: [rchltxfe-d93180012-001]

TASK [Loop over all docker.io/wind-river/elastic-services tags] ****************
changed: [rchltxfe-d93180012-001] => (item=WRA.21.06-00)

TASK [Retrieve list of docker.io/wind-river/wra-kibana tags] *******************
changed: [rchltxfe-d93180012-001]

TASK [Loop over all docker.io/wind-river/wra-kibana tags] **********************
changed: [rchltxfe-d93180012-001] => (item=WRA.21.06-00)

TASK [Retrieve list of docker.io/wind-river/wra-metricbeat tags] ***************
changed: [rchltxfe-d93180012-001]

TASK [Loop over all docker.io/wind-river/wra-metricbeat tags] ******************
changed: [rchltxfe-d93180012-001] => (item=WRA.21.06-00)

TASK [Retrieve list of docker.io/wind-river/wra-elasticsearch tags] ************
changed: [rchltxfe-d93180012-001]

TASK [Loop over all docker.io/wind-river/wra-elasticsearch tags] ***************
changed: [rchltxfe-d93180012-001] => (item=WRA.21.06-01)

TASK [Retrieve list of docker.io/wind-river/wra-logstash tags] *****************
changed: [rchltxfe-d93180012-001]

TASK [Loop over all docker.io/wind-river/wra-logstash tags] ********************
changed: [rchltxfe-d93180012-001] => (item=WRA.21.06-01)

TASK [Retrieve list of docker.io/wind-river/cloud-platform-deployment-manager tags] ***
changed: [rchltxfe-d93180012-001]

TASK [Loop over all docker.io/wind-river/cloud-platform-deployment-manager tags] ***
changed: [rchltxfe-d93180012-001] => (item=WRCP_21.05)

TASK [Retrieve list of docker.io/starlingx/k8s-cni-sriov tags] *****************
changed: [rchltxfe-d93180012-001]

TASK [Loop over all docker.io/starlingx/k8s-cni-sriov tags] ********************
changed: [rchltxfe-d93180012-001] => (item=stx.5.0-v2.6-7-gb18123d8)

TASK [Garbage collect] *********************************************************
changed: [rchltxfe-d93180012-001]

TASK [Wait for 250.001 alarm to clear] *****************************************
FAILED - RETRYING: Wait for 250.001 alarm to clear (60 retries left).
FAILED - RETRYING: Wait for 250.001 alarm to clear (59 retries left).
FAILED - RETRYING: Wait for 250.001 alarm to clear (58 retries left).
changed: [rchltxfe-d93180012-001]

PLAY RECAP *********************************************************************
rchltxfe-d93180012-001     : ok=49   changed=30   unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./cleanup-unused-images_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook --inventory subclouds --ask-pass --user XXXXXX \
> cleanup-unused-images.yaml 0</dev/null
SSH password:

XXXXXX [all] *********************************************************************

TASK [Retrieve application info output] ****************************************
changed: [rchltxfe-d93180012-001]

TASK [Save application namespace and image as fact] ****************************
skipping: [rchltxfe-d93180012-001]

TASK [Retrieve application tag output] *****************************************
skipping: [rchltxfe-d93180012-001]

TASK [Save application tag as fact] ********************************************
skipping: [rchltxfe-d93180012-001]

TASK [Output variables] ********************************************************
skipping: [rchltxfe-d93180012-001]

TASK [Remove unused images] ****************************************************
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-unused-images.yaml for rchltxfe-d93180012-001
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-unused-images.yaml for rchltxfe-d93180012-001
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-unused-images.yaml for rchltxfe-d93180012-001
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-unused-images.yaml for rchltxfe-d93180012-001
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-unused-images.yaml for rchltxfe-d93180012-001
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-unused-images.yaml for rchltxfe-d93180012-001
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-unused-images.yaml for rchltxfe-d93180012-001
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-unused-images.yaml for rchltxfe-d93180012-001
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-unused-images.yaml for rchltxfe-d93180012-001
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-unused-images.yaml for rchltxfe-d93180012-001
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-unused-images.yaml for rchltxfe-d93180012-001
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-unused-images.yaml for rchltxfe-d93180012-001
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-unused-images.yaml for rchltxfe-d93180012-001
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/remove-unused-images.yaml for rchltxfe-d93180012-001

TASK [Retrieve list of vzw-adpf-cmp tags] **************************************
changed: [rchltxfe-d93180012-001]

TASK [Loop over all vzw-adpf-cmp tags] *****************************************

TASK [Retrieve list of vzw-adpf-dip tags] **************************************
changed: [rchltxfe-d93180012-001]

TASK [Loop over all vzw-adpf-dip tags] *****************************************

TASK [Retrieve list of vzw-adpf-dmp tags] **************************************
changed: [rchltxfe-d93180012-001]

TASK [Loop over all vzw-adpf-dmp tags] *****************************************

TASK [Retrieve list of vzw-adpf-dpp tags] **************************************
changed: [rchltxfe-d93180012-001]

TASK [Loop over all vzw-adpf-dpp tags] *****************************************

TASK [Retrieve list of vzw-adpf-init tags] *************************************
changed: [rchltxfe-d93180012-001]

TASK [Loop over all vzw-adpf-init tags] ****************************************

TASK [Retrieve list of vzw-adpf-pmp tags] **************************************
changed: [rchltxfe-d93180012-001]

TASK [Loop over all vzw-adpf-pmp tags] *****************************************

TASK [Retrieve list of vzw-adpf-rmp tags] **************************************
changed: [rchltxfe-d93180012-001]

TASK [Loop over all vzw-adpf-rmp tags] *****************************************

TASK [Retrieve list of vzw-uadpf-cmp tags] *************************************
changed: [rchltxfe-d93180012-001]

TASK [Loop over all vzw-uadpf-cmp tags] ****************************************

TASK [Retrieve list of vzw-uadpf-dip tags] *************************************
changed: [rchltxfe-d93180012-001]

TASK [Loop over all vzw-uadpf-dip tags] ****************************************

TASK [Retrieve list of vzw-uadpf-dmp tags] *************************************
changed: [rchltxfe-d93180012-001]

TASK [Loop over all vzw-uadpf-dmp tags] ****************************************

TASK [Retrieve list of vzw-uadpf-dpp tags] *************************************
changed: [rchltxfe-d93180012-001]

TASK [Loop over all vzw-uadpf-dpp tags] ****************************************

TASK [Retrieve list of vzw-uadpf-init tags] ************************************
changed: [rchltxfe-d93180012-001]

TASK [Loop over all vzw-uadpf-init tags] ***************************************

TASK [Retrieve list of vzw-uadpf-pmp tags] *************************************
changed: [rchltxfe-d93180012-001]

TASK [Loop over all vzw-uadpf-pmp tags] ****************************************

TASK [Retrieve list of vzw-uadpf-rmp tags] *************************************
changed: [rchltxfe-d93180012-001]

TASK [Loop over all vzw-uadpf-rmp tags] ****************************************

TASK [Garbage collect] *********************************************************
changed: [rchltxfe-d93180012-001]

TASK [Wait for 250.001 alarm to clear] *****************************************
FAILED - RETRYING: Wait for 250.001 alarm to clear (60 retries left).
FAILED - RETRYING: Wait for 250.001 alarm to clear (59 retries left).
FAILED - RETRYING: Wait for 250.001 alarm to clear (58 retries left).
changed: [rchltxfe-d93180012-001]

PLAY RECAP *********************************************************************
rchltxfe-d93180012-001     : ok=31   changed=17   unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ local_registry_pass=XXXXXX
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
skipping: [rchltxfe-d93180012-001]

TASK [common/load-images-information : Set kubernetes long version] ************
ok: [rchltxfe-d93180012-001]

TASK [common/load-images-information : Get the list of kubernetes images] ******
changed: [rchltxfe-d93180012-001]

TASK [common/load-images-information : set_fact] *******************************
ok: [rchltxfe-d93180012-001]

TASK [common/load-images-information : Read in system images list] *************
ok: [rchltxfe-d93180012-001]

TASK [common/load-images-information : Check if additional image config file exists] ***
ok: [rchltxfe-d93180012-001]

TASK [common/load-images-information : Read in additional system images list(s) in localhost] ***
skipping: [rchltxfe-d93180012-001]

TASK [common/load-images-information : Create a temporary file on remote] ******
changed: [rchltxfe-d93180012-001]

TASK [common/load-images-information : Fetch the additional images config in case the playbook is executed remotely] ***
changed: [rchltxfe-d93180012-001]

TASK [common/load-images-information : Read in additional system images list(s) fetched from remote] ***
ok: [rchltxfe-d93180012-001]

TASK [common/load-images-information : Remove the temporary file on remote] ****
changed: [rchltxfe-d93180012-001 -> rchltxfe-d93180012-001]

TASK [common/load-images-information : Remove override temp file on Ansible control host] ***
changed: [rchltxfe-d93180012-001 -> localhost]

TASK [common/load-images-information : Categorize system images] ***************
ok: [rchltxfe-d93180012-001]

TASK [common/load-images-information : Append additional static images if provisioned] ***
ok: [rchltxfe-d93180012-001] => (item={'key': u'deploy_manager_img', 'value': u'docker.io/wind-river/cloud-platform-deployment-manager:WRCP_21.05'})
ok: [rchltxfe-d93180012-001] => (item={'key': u'kube_rbac_proxy_img', 'value': u'gcr.io/kubebuilder/kube-rbac-proxy:v0.4.0'})

TASK [common/load-images-information : Append RVMC image for a DC system controller] ***
skipping: [rchltxfe-d93180012-001]

TASK [common/load-images-information : Append additional static images for a DC system controller if provisioned] ***
skipping: [rchltxfe-d93180012-001] => (item={'key': u'rbd_provisioner_img', 'value': u'quay.io/external_storage/rbd-provisioner:v2.1.1-k8s1.11'})
skipping: [rchltxfe-d93180012-001] => (item={'key': u'ceph_config_helper_img', 'value': u'docker.io/starlingx/ceph-config-helper:v1.15.0'})

TASK [Set platform images list] ************************************************
ok: [rchltxfe-d93180012-001]

TASK [Create a temporary file on remote] ***************************************
changed: [rchltxfe-d93180012-001]

TASK [Correct permissions for temporary file on remote] ************************
changed: [rchltxfe-d93180012-001]

TASK [Save list of local registry images excluding apps images to file] ********
changed: [rchltxfe-d93180012-001]

TASK [Read file] ***************************************************************
changed: [rchltxfe-d93180012-001]

TASK [Load list of local registry images from file] ****************************
ok: [rchltxfe-d93180012-001]

TASK [Subtract platform images from local registry images] *********************
ok: [rchltxfe-d93180012-001]

TASK [Append local registry host:port to image names] **************************
ok: [rchltxfe-d93180012-001]

TASK [debug] *******************************************************************
ok: [rchltxfe-d93180012-001] => {
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
changed: [rchltxfe-d93180012-001]

TASK [Pull images from local registry to docker filesystem] ********************
changed: [rchltxfe-d93180012-001] => (item=registry.local:9001/docker.io/starlingx/n3000-opae:stx.4.0-v1.0.0)
changed: [rchltxfe-d93180012-001] => (item=registry.local:9001/docker.io/lwolf/kubectl_deployer:0.4)
changed: [rchltxfe-d93180012-001] => (item=registry.local:9001/docker.io/zookeeper:3.5.5)
changed: [rchltxfe-d93180012-001] => (item=registry.local:9001/quay.io/airshipit/armada:8a1638098f88d92bf799ef4934abe569789b885e-ubuntu_bionic)
changed: [rchltxfe-d93180012-001] => (item=registry.local:9001/gcr.io/kubernetes-helm/tiller:v2.16.1)
changed: [rchltxfe-d93180012-001] => (item=registry.local:9001/docker.io/confluentinc/cp-kafka:5.0.1)
changed: [rchltxfe-d93180012-001] => (item=registry.local:9001/docker.io/danielqsj/kafka-exporter:v1.2.0)
changed: [rchltxfe-d93180012-001] => (item=registry.local:9001/docker.io/josdotso/zookeeper-exporter:v1.1.2)
changed: [rchltxfe-d93180012-001] => (item=registry.local:9001/k8s.gcr.io/defaultbackend-amd64:1.5)

TASK [Set format parameter for docker inspect to retrieve only the size] *******
ok: [rchltxfe-d93180012-001]

TASK [Get docker images size in bytes] *****************************************
changed: [rchltxfe-d93180012-001] => (item=registry.local:9001/docker.io/starlingx/n3000-opae:stx.4.0-v1.0.0)
changed: [rchltxfe-d93180012-001] => (item=registry.local:9001/docker.io/lwolf/kubectl_deployer:0.4)
changed: [rchltxfe-d93180012-001] => (item=registry.local:9001/docker.io/zookeeper:3.5.5)
changed: [rchltxfe-d93180012-001] => (item=registry.local:9001/quay.io/airshipit/armada:8a1638098f88d92bf799ef4934abe569789b885e-ubuntu_bionic)
changed: [rchltxfe-d93180012-001] => (item=registry.local:9001/gcr.io/kubernetes-helm/tiller:v2.16.1)
changed: [rchltxfe-d93180012-001] => (item=registry.local:9001/docker.io/confluentinc/cp-kafka:5.0.1)
changed: [rchltxfe-d93180012-001] => (item=registry.local:9001/docker.io/danielqsj/kafka-exporter:v1.2.0)
changed: [rchltxfe-d93180012-001] => (item=registry.local:9001/docker.io/josdotso/zookeeper-exporter:v1.1.2)
changed: [rchltxfe-d93180012-001] => (item=registry.local:9001/k8s.gcr.io/defaultbackend-amd64:1.5)

TASK [Parse docker images size] ************************************************
ok: [rchltxfe-d93180012-001] => (item=registry.local:9001/docker.io/starlingx/n3000-opae:stx.4.0-v1.0.0, 506492391 bytes)
ok: [rchltxfe-d93180012-001] => (item=registry.local:9001/docker.io/lwolf/kubectl_deployer:0.4, 82474353 bytes)
ok: [rchltxfe-d93180012-001] => (item=registry.local:9001/docker.io/zookeeper:3.5.5, 225210868 bytes)
ok: [rchltxfe-d93180012-001] => (item=registry.local:9001/quay.io/airshipit/armada:8a1638098f88d92bf799ef4934abe569789b885e-ubuntu_bionic, 457539381 bytes)
ok: [rchltxfe-d93180012-001] => (item=registry.local:9001/gcr.io/kubernetes-helm/tiller:v2.16.1, 91160017 bytes)
ok: [rchltxfe-d93180012-001] => (item=registry.local:9001/docker.io/confluentinc/cp-kafka:5.0.1, 557414026 bytes)
ok: [rchltxfe-d93180012-001] => (item=registry.local:9001/docker.io/danielqsj/kafka-exporter:v1.2.0, 15387401 bytes)
ok: [rchltxfe-d93180012-001] => (item=registry.local:9001/docker.io/josdotso/zookeeper-exporter:v1.1.2, 11828993 bytes)
ok: [rchltxfe-d93180012-001] => (item=registry.local:9001/k8s.gcr.io/defaultbackend-amd64:1.5, 5132544 bytes)

TASK [debug] *******************************************************************
ok: [rchltxfe-d93180012-001] => {
    "docker_images_size": "1952639974"
}

TASK [Remove pulled images] ****************************************************
changed: [rchltxfe-d93180012-001]

TASK [Scale to KiB and reserve 5% for docker metadata inside exported archive] ***
ok: [rchltxfe-d93180012-001]

TASK [Determine available space in /opt/platform-backup] ***********************
changed: [rchltxfe-d93180012-001]

TASK [Fail if there is not enough free space to create docker images backup archive] ***
skipping: [rchltxfe-d93180012-001]

TASK [Remove the temporary file from remote] ***********************************
changed: [rchltxfe-d93180012-001]

PLAY RECAP *********************************************************************
rchltxfe-d93180012-001     : ok=31   changed=15   unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./sanity_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook --inventory subclouds --extra-vars "scenario=before" \
> --ask-pass --ask-become-pass --user XXXXXX \
> pre-deployment-subclouds.yaml 0</dev/null
SSH password:
XXXXXX password[defaults to SSH password]:

PLAY [all] *********************************************************************

TASK [Gathering Facts] *********************************************************
ok: [rchltxfe-d93180012-001]

TASK [Read in parameter file] **************************************************
ok: [rchltxfe-d93180012-001]

TASK [set expected Fortville firmware version] *********************************
ok: [rchltxfe-d93180012-001]

TASK [set expected N3000 firmware version] *************************************
ok: [rchltxfe-d93180012-001]

TASK [create directory /home/XXXXXX/sanity] **********************************
ok: [rchltxfe-d93180012-001 -> localhost]

TASK [delete existing file /home/XXXXXX/sanity/output_list] ******************
changed: [rchltxfe-d93180012-001 -> localhost]

TASK [create file /home/XXXXXX/sanity/output_list] ***************************
changed: [rchltxfe-d93180012-001 -> localhost]

TASK [get host patch status] ***************************************************
changed: [rchltxfe-d93180012-001]

TASK [validate host patch status] **********************************************
skipping: [rchltxfe-d93180012-001]

TASK [get host status] *********************************************************
changed: [rchltxfe-d93180012-001]

TASK [validate host status] ****************************************************
skipping: [rchltxfe-d93180012-001]

TASK [get current alarms] ******************************************************
changed: [rchltxfe-d93180012-001]

TASK [validate current alarms] *************************************************
skipping: [rchltxfe-d93180012-001]

TASK [get vim status] **********************************************************
changed: [rchltxfe-d93180012-001]

TASK [validate vim status] *****************************************************
skipping: [rchltxfe-d93180012-001]

TASK [calculate / partition expected usage] ************************************
changed: [rchltxfe-d93180012-001]

TASK [validate / partition free space] *****************************************
skipping: [rchltxfe-d93180012-001]

TASK [validate /opt/dc-vault partition free space] *****************************
skipping: [rchltxfe-d93180012-001]

TASK [identify N3000 NICs] *****************************************************
changed: [rchltxfe-d93180012-001]

TASK [get N3000 NICs firmware version] *****************************************
changed: [rchltxfe-d93180012-001] => (item=enp103s0f0)
changed: [rchltxfe-d93180012-001] => (item=enp103s0f1)
changed: [rchltxfe-d93180012-001] => (item=enp105s0f0)
changed: [rchltxfe-d93180012-001] => (item=enp105s0f1)

TASK [validate N3000 NICs firmware version] ************************************
skipping: [rchltxfe-d93180012-001] => (item=enp103s0f0)
skipping: [rchltxfe-d93180012-001] => (item=enp103s0f1)
skipping: [rchltxfe-d93180012-001] => (item=enp105s0f0)
skipping: [rchltxfe-d93180012-001] => (item=enp105s0f1)

TASK [get N3000 NICs MAC] ******************************************************
changed: [rchltxfe-d93180012-001] => (item=enp103s0f0)
changed: [rchltxfe-d93180012-001] => (item=enp103s0f1)
changed: [rchltxfe-d93180012-001] => (item=enp105s0f0)
changed: [rchltxfe-d93180012-001] => (item=enp105s0f1)

TASK [validate N3000 NICs MACs] ************************************************
skipping: [rchltxfe-d93180012-001] => (item=enp103s0f0)
skipping: [rchltxfe-d93180012-001] => (item=enp103s0f1)
skipping: [rchltxfe-d93180012-001] => (item=enp105s0f0)
skipping: [rchltxfe-d93180012-001] => (item=enp105s0f1)

TASK [identify Fortville NICs] *************************************************
changed: [rchltxfe-d93180012-001]

TASK [get Fortville NICs firmware version] *************************************
changed: [rchltxfe-d93180012-001] => (item=enp179s0f0)
changed: [rchltxfe-d93180012-001] => (item=enp179s0f1)

TASK [validate Fortville NICs firmware version] ********************************
skipping: [rchltxfe-d93180012-001] => (item=enp179s0f0)
skipping: [rchltxfe-d93180012-001] => (item=enp179s0f1)

TASK [get Fortville NICs MAC] **************************************************
changed: [rchltxfe-d93180012-001] => (item=enp179s0f0)
changed: [rchltxfe-d93180012-001] => (item=enp179s0f1)

TASK [validate Fortville NICs MACs] ********************************************
skipping: [rchltxfe-d93180012-001] => (item=enp179s0f0)
skipping: [rchltxfe-d93180012-001] => (item=enp179s0f1)

TASK [identify accelerators] ***************************************************
changed: [rchltxfe-d93180012-001]

TASK [retrieve device information] *********************************************
changed: [rchltxfe-d93180012-001] => (item=pci_0000_6a_00_0)

TASK [output device show information] ******************************************
ok: [rchltxfe-d93180012-001] => (item=pci_0000_6a_00_0) => {
    "msg": [
        "+-----------------------+----------------------------------+",
        "| Property              | Value                            |",
        "+-----------------------+----------------------------------+",
        "| name                  | pci_0000_6a_00_0                 |",
        "| address               | 0000:6a:00.0                     |",
        "| class id              | 120000                           |",
        "| vendor id             | 8086                             |",
        "| device id             | 0d8f                             |",
        "| class name            | Processing accelerators          |",
        "| vendor name           | Intel Corporation                |",
        "| device name           | Device 0d8f                      |",
        "| numa_node             | 0                                |",
        "| enabled               | True                             |",
        "| sriov_totalvfs        | 8                                |",
        "| sriov_numvfs          | 0                                |",
        "| sriov_vfs_pci_address |                                  |",
        "| sriov_vf_pdevice_id   | None                             |",
        "| extra_info            | None                             |",
        "| created_at            | 2023-12-05T16:48:40.796961+00:00 |",
        "| updated_at            | 2023-12-05T16:49:34.945537+00:00 |",
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
changed: [rchltxfe-d93180012-001] => (item=pci_0000_6a_00_0)

TASK [output field information] ************************************************
ok: [rchltxfe-d93180012-001] => (item=pci_0000_6a_00_0) => {
    "msg": "0|None|None|None"
}

TASK [validate sriov_numvfs for Mount Bryce] ***********************************
skipping: [rchltxfe-d93180012-001] => (item=pci_0000_6a_00_0)

TASK [validate driver and sriov_vf_driver fields] ******************************
skipping: [rchltxfe-d93180012-001] => (item=pci_0000_6a_00_0)

TASK [validate extra_info field] ***********************************************
skipping: [rchltxfe-d93180012-001] => (item=pci_0000_6a_00_0)

TASK [get pod status] **********************************************************
changed: [rchltxfe-d93180012-001]

TASK [validate pod status] *****************************************************
changed: [rchltxfe-d93180012-001 -> localhost]

TASK [get system applications] *************************************************
changed: [rchltxfe-d93180012-001]

TASK [validate system applications] ********************************************
skipping: [rchltxfe-d93180012-001] => (item=cert-manager:21.05-17)
skipping: [rchltxfe-d93180012-001] => (item=nginx-ingress-controller:21.05-16)
skipping: [rchltxfe-d93180012-001] => (item=oidc-auth-apps:21.05-44)
skipping: [rchltxfe-d93180012-001] => (item=platform-integ-apps:21.05-30)

PLAY [all] *********************************************************************

TASK [Gathering Facts] *********************************************************
ok: [rchltxfe-d93180012-001]

TASK [validate /opt/platform-backup partition free space] **********************
skipping: [rchltxfe-d93180012-001]

TASK [validate /opt/platform-backup partition type] ****************************
skipping: [rchltxfe-d93180012-001]

TASK [Collect previous backups] ************************************************
ok: [rchltxfe-d93180012-001]

TASK [Delete previous backups] *************************************************

TASK [Get /home size] **********************************************************
changed: [rchltxfe-d93180012-001]

TASK [validate /home size] *****************************************************
skipping: [rchltxfe-d93180012-001]

PLAY RECAP *********************************************************************
rchltxfe-d93180012-001     : ok=29   changed=20   unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ cat /home/XXXXXX/sanity/output_list
rchltxfe-d93180012-001 - check pod status
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
[XXXXXX@controller-0 ~(keystone_admin)]$ cd /opt/platform-backup/upgrade/wrcp-21.12-upgrade/
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./fix-backup-system_$(date "+%Y%m%d%H%M%S").log ansible-playbook --inventory subclouds --ask-pass --ask-become-pass --user XXXXXX fix-backup-system.yaml 0</dev/null
SSH password:
XXXXXX password[defaults to SSH password]:

PLAY [all] *********************************************************************

TASK [Add fail task to backup-system rescue block] *****************************
changed: [rchltxfe-d93180012-001]

PLAY RECAP *********************************************************************
rchltxfe-d93180012-001     : ok=1    changed=1    unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./health-query-upgrade_$(date "+%Y%m%d%H%M%S").log \
> ansible all --inventory subclouds --ask-pass --user XXXXXX --module-name shell \
> --args "source /etc/platform/openrc; system health-query-upgrade"
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
1
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$


```

### pre-checks complete, now on to upgrade of subcloud

```log

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ subcloud_group=Default
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ dcmanager upgrade-strategy create --group ${subcloud_group}
+------------------------+----------------------------+
| Field                  | Value                      |
+------------------------+----------------------------+
| strategy type          | upgrade                    |
| subcloud apply type    | parallel                   |
| max parallel subclouds | 50                         |
| stop on failure        | False                      |
| state                  | initial                    |
| created_at             | 2023-12-12T20:47:45.296787 |
| updated_at             | None                       |
+------------------------+----------------------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ dcmanager strategy-step list -c cloud -c stage -c state
+------------------------+-------+---------+
| cloud                  | stage | state   |
+------------------------+-------+---------+
| rchltxfe-d93180012-001 |     1 | initial |
+------------------------+-------+---------+
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
| created_at             | 2023-12-12T20:47:45.296787 |
| updated_at             | 2023-12-12T20:48:23.869987 |
+------------------------+----------------------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

watch -n15 dcmanager strategy-step list -c cloud -c state -c details \
--max-width 100 --sort-column details --sort-column state

Every 15.0s: dcmanager strategy-step list -c cloud -c state -c details --max-width 100 --sort-colu...  Tue Dec 12 20:48:41 2023

+------------------------+--------------------+---------+
| cloud                  | state              | details |
+------------------------+--------------------+---------+
| rchltxfe-d93180012-001 | installing license |         |
+------------------------+--------------------+---------+

Every 15.0s: dcmanager strategy-step list -c cloud -c state -c details --max-width 100 --sort-colu...  Tue Dec 12 22:47:55 2023

+------------------------+----------+---------+
| cloud                  | state    | details |
+------------------------+----------+---------+
| rchltxfe-d93180012-001 | complete |         |
+------------------------+----------+---------+

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ dcmanager upgrade-strategy delete
+------------------------+----------------------------+
| Field                  | Value                      |
+------------------------+----------------------------+
| strategy type          | upgrade                    |
| subcloud apply type    | parallel                   |
| max parallel subclouds | 50                         |
| stop on failure        | False                      |
| state                  | deleting                   |
| created_at             | 2023-12-12T20:47:45.296787 |
| updated_at             | 2023-12-12T22:48:41.138845 |
+------------------------+----------------------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./set-intel-driver-version_$(date "+%Y%m%d%H%M%S").log ansible-playbook --inventory subclouds --ask-pass --user XXXXXX set-intel-driver-version.yaml 0</dev/null
SSH password:

XXXXXX [all] *********************************************************************

TASK [Retrieve platform release version] ***************************************
changed: [rchltxfe-d93180012-001]

TASK [Retrieve intel_nic_driver_version service parameter] *********************
changed: [rchltxfe-d93180012-001]

TASK [Store service parameter field values] ************************************
ok: [rchltxfe-d93180012-001]

TASK [Delete old intel_nic_driver_version service parameter with resource] *****
changed: [rchltxfe-d93180012-001]

TASK [Clear the driver version] ************************************************
ok: [rchltxfe-d93180012-001]

TASK [Set Intel driver version (with resource)] ********************************
skipping: [rchltxfe-d93180012-001]

TASK [Set Intel driver version] ************************************************
changed: [rchltxfe-d93180012-001]

TASK [Apply service parameters] ************************************************
changed: [rchltxfe-d93180012-001]

TASK [Retrieve current Intel driver version] ***********************************
changed: [rchltxfe-d93180012-001]

PLAY RECAP *********************************************************************
rchltxfe-d93180012-001     : ok=8    changed=6    unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./lock-unlock_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook --inventory subclouds --ask-pass --user XXXXXX lock-unlock.yaml \
> 0</dev/null
SSH password:

XXXXXX [all] *********************************************************************

TASK [Check if host is already locked] *****************************************
changed: [rchltxfe-d93180012-001]

TASK [Lock host] ***************************************************************
changed: [rchltxfe-d93180012-001]

TASK [Wait for host to enter locked state] *************************************
changed: [rchltxfe-d93180012-001]

TASK [Unlock host] *************************************************************
changed: [rchltxfe-d93180012-001]

PLAY RECAP *********************************************************************
rchltxfe-d93180012-001     : ok=4    changed=4    unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ watch dcmanager subcloud-group list-subclouds ${subcloud_group} -f value -c name -c availability


Every 2.0s: dcmanager subcloud-group list-subclouds Default -f value -c name -c availability           Tue Dec 12 23:05:43 2023

rchltxfe-d93180012-001 online

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./confirm-ice-driver-version_$(date "+%Y%m%d%H%M%S").log ansible all --inventory subclouds --ask-pass --ask-become-pass --user XXXXXX --become --module-name shell --args "grep -E 'ice\:.*1\.5\.8$' /var/log/dmesg"
SSH password:
XXXXXX password[defaults to SSH password]:
rchltxfe-d93180012-001 | CHANGED | rc=0 >>
[   30.700936] ice: Intel(R) Ethernet Connection E800 Series Linux Driver - version 1.5.8

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./dm_delete_old_secret_$(date "+%Y%m%d%H%M%S").log ansible all --inventory subclouds --ask-pass --user XXXXXX --module-name shell --args "kubectl --kubeconfig /etc/kubernetes/admin.conf delete secret \
-n platform-deployment-manager platform-deployment-manager-webhook-server-secret"
SSH password:
XXXXXX | CHANGED | rc=0 >>
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
| id                          | 2                               |
| name                        | rchltxfe-d93180012-001          |
| description                 | Wind River Cloud Platform 21.05 |
| location                    | rchltxfe-d93180012-001          |
| software_version            | 21.12                           |
| management                  | managed                         |
| availability                | online                          |
| deploy_status               | pre-deploy                      |
| management_subnet           | 2607:f160:10:907b::/64          |
| management_start_ip         | 2607:f160:10:907b:ce:40a::      |
| management_end_ip           | 2607:f160:10:907b:ce:40a:0:f    |
| management_gateway_ip       | 2607:f160:10:907b:ce:28::       |
| systemcontroller_gateway_ip | 2607:f160:0:3048:cd:28::        |
| group_id                    | 1                               |
| created_at                  | 2023-12-05T15:46:21.700016      |
| updated_at                  | 2023-12-12T23:08:16.631616      |
+-----------------------------+---------------------------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
Every 2.0s: dcmanager subcloud-group list-subclouds Default -c name -c deploy_status                   Tue Dec 12 23:11:06 2023

+------------------------+---------------+
| name                   | deploy_status |
+------------------------+---------------+
| rchltxfe-d93180012-001 | complete      |
+------------------------+---------------+
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
platform-deployment-manager-0   2/2     Running   2          3m11s
registry.local:9001/docker.io/wind-river/cloud-platform-deployment-manager:WRCP_21.12-wrs.4
registry.local:9001/gcr.io/kubebuilder/kube-rbac-proxy:v0.4.0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./install-dm-monitor_$(date "+%Y%m%d%H%M%S").log ansible-playbook --inventory subclouds --ask-pass --user XXXXXX /usr/local/share/applications/playbooks/dm-monitor-book.yaml --extra-vars "dm_monitor_dir=/usr/local/share/applications/helm/dm-monitor-1.0.0.tgz
dm_monitor_overrides=/usr/local/share/applications/overrides/dm-monitor-overrides.yaml" 0</dev/null
SSH password:

XXXXXX [Deployment Manager Monitor Playbook] *************************************

TASK [set_fact] ****************************************************************
ok: [rchltxfe-d93180012-001]

TASK [Get Ip Controller] *******************************************************
changed: [rchltxfe-d93180012-001]

TASK [debug] *******************************************************************
ok: [rchltxfe-d93180012-001] => {
    "msg": "controller ip: 2607:f160:10:907b:ce:40a::"
}

TASK [Install Deployment Manager Monitor] **************************************
changed: [rchltxfe-d93180012-001]

TASK [Wait for Deployment Manager Monitor to be ready] *************************
changed: [rchltxfe-d93180012-001]

PLAY RECAP *********************************************************************
rchltxfe-d93180012-001     : ok=5    changed=3    unreachable=0    failed=0

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
dm-monitor-6bb468c79f-zt8vr   1/1     Running   0          49s
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
fatal: [rchltxfe-d93180012-001]: FAILED! => {"changed": true, "cmd": "source /etc/platform/openrc; system application-remove ptp-notification", "delta": "0:00:02.523024", "end": "2023-12-12 23:13:51.327959", "msg": "non-zero return code", "rc": 1, "start": "2023-12-12 23:13:48.804935", "stderr": "Application-remove rejected: application not found.", "stderr_lines": ["Application-remove rejected: application not found."], "stdout": "", "stdout_lines": []}

PLAY RECAP *********************************************************************
rchltxfe-d93180012-001     : ok=0    changed=0    unreachable=0    failed=1

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
No resources found in notification namespace.

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
```

### PTP was not installed as NADS were not setup before  hand, shouldn't matter...

### Continuing steps

```log
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./metrics-server-upgrade_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook --inventory subclouds --ask-pass --user XXXXXX app-upgrade.yaml \
> --extra-vars="application=metrics-server" \
> 0</dev/null
SSH password:

XXXXXX [all] *********************************************************************

TASK [Copy application overrides to the subcloud] ******************************
skipping: [rchltxfe-d93180012-001]

TASK [Apply application overrides] *********************************************
skipping: [rchltxfe-d93180012-001]

TASK [Remove override file] ****************************************************
skipping: [rchltxfe-d93180012-001]

TASK [Retrieve latest application version] *************************************
changed: [rchltxfe-d93180012-001]

TASK [Upgrade application] *****************************************************
changed: [rchltxfe-d93180012-001]

TASK [Check if application is applied] *****************************************
FAILED - RETRYING: Check if application is applied (60 retries left).
FAILED - RETRYING: Check if application is applied (59 retries left).
FAILED - RETRYING: Check if application is applied (58 retries left).
FAILED - RETRYING: Check if application is applied (57 retries left).
FAILED - RETRYING: Check if application is applied (56 retries left).
FAILED - RETRYING: Check if application is applied (55 retries left).
changed: [rchltxfe-d93180012-001]

PLAY RECAP *********************************************************************
rchltxfe-d93180012-001     : ok=3    changed=3    unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./verify-subcloud-metrics-server_$(date "+%Y%m%d%H%M%S").log ansible all --inventory subclouds --ask-pass --user XXXXXX --module-name shell --args "kubectl --kubeconfig /etc/kubernetes/admin.conf get pods \
-l app=metrics-server -n metrics-server; \
kubectl --kubeconfig /etc/kubernetes/admin.conf get pods \
-A -l "app=metrics-server" -o \
jsonpath="{..image}" | tr -s '[[:space:]]' '\n'| sort | uniq"
SSH password:
XXXXXX | CHANGED | rc=0 >>
NAME                                 READY   STATUS    RESTARTS   AGE
ms-metrics-server-6676595474-hmjvs   1/1     Running   1          2m23s
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
changed: [rchltxfe-d93180012-001]

TASK [Delete failed pods] ******************************************************

PLAY RECAP *********************************************************************
rchltxfe-d93180012-001     : ok=1    changed=1    unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./sanity_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook --inventory subclouds --extra-vars "scenario=after" \
> --ask-pass --ask-become-pass --user XXXXXX \
> sanity.yaml 0</dev/null
SSH password:
XXXXXX password[defaults to SSH password]:

PLAY [all] *********************************************************************

TASK [Gathering Facts] *********************************************************
ok: [rchltxfe-d93180012-001]

TASK [Read in parameter file] **************************************************
ok: [rchltxfe-d93180012-001]

TASK [set expected Fortville firmware version] *********************************
ok: [rchltxfe-d93180012-001]

TASK [set expected N3000 firmware version] *************************************
ok: [rchltxfe-d93180012-001]

TASK [create directory /home/XXXXXX/sanity] **********************************
ok: [rchltxfe-d93180012-001 -> localhost]

TASK [delete existing file /home/XXXXXX/sanity/output_list] ******************
changed: [rchltxfe-d93180012-001 -> localhost]

TASK [create file /home/XXXXXX/sanity/output_list] ***************************
changed: [rchltxfe-d93180012-001 -> localhost]

TASK [get host patch status] ***************************************************
changed: [rchltxfe-d93180012-001]

TASK [validate host patch status] **********************************************
skipping: [rchltxfe-d93180012-001]

TASK [get host status] *********************************************************
changed: [rchltxfe-d93180012-001]

TASK [validate host status] ****************************************************
skipping: [rchltxfe-d93180012-001]

TASK [get current alarms] ******************************************************
changed: [rchltxfe-d93180012-001]

TASK [validate current alarms] *************************************************
skipping: [rchltxfe-d93180012-001]

TASK [get vim status] **********************************************************
changed: [rchltxfe-d93180012-001]

TASK [validate vim status] *****************************************************
skipping: [rchltxfe-d93180012-001]

TASK [calculate / partition expected usage] ************************************
changed: [rchltxfe-d93180012-001]

TASK [validate / partition free space] *****************************************
skipping: [rchltxfe-d93180012-001]

TASK [validate /opt/dc-vault partition free space] *****************************
skipping: [rchltxfe-d93180012-001]

TASK [identify N3000 NICs] *****************************************************
changed: [rchltxfe-d93180012-001]

TASK [get N3000 NICs firmware version] *****************************************
changed: [rchltxfe-d93180012-001] => (item=enp103s0f0)
changed: [rchltxfe-d93180012-001] => (item=enp103s0f1)
changed: [rchltxfe-d93180012-001] => (item=enp105s0f0)
changed: [rchltxfe-d93180012-001] => (item=enp105s0f1)

TASK [validate N3000 NICs firmware version] ************************************
skipping: [rchltxfe-d93180012-001] => (item=enp103s0f0)
skipping: [rchltxfe-d93180012-001] => (item=enp103s0f1)
skipping: [rchltxfe-d93180012-001] => (item=enp105s0f0)
skipping: [rchltxfe-d93180012-001] => (item=enp105s0f1)

TASK [get N3000 NICs MAC] ******************************************************
changed: [rchltxfe-d93180012-001] => (item=enp103s0f0)
changed: [rchltxfe-d93180012-001] => (item=enp103s0f1)
changed: [rchltxfe-d93180012-001] => (item=enp105s0f0)
changed: [rchltxfe-d93180012-001] => (item=enp105s0f1)

TASK [validate N3000 NICs MACs] ************************************************
skipping: [rchltxfe-d93180012-001] => (item=enp103s0f0)
skipping: [rchltxfe-d93180012-001] => (item=enp103s0f1)
skipping: [rchltxfe-d93180012-001] => (item=enp105s0f0)
skipping: [rchltxfe-d93180012-001] => (item=enp105s0f1)

TASK [identify Fortville NICs] *************************************************
changed: [rchltxfe-d93180012-001]

TASK [get Fortville NICs firmware version] *************************************
changed: [rchltxfe-d93180012-001] => (item=enp179s0f0)
changed: [rchltxfe-d93180012-001] => (item=enp179s0f1)

TASK [validate Fortville NICs firmware version] ********************************
skipping: [rchltxfe-d93180012-001] => (item=enp179s0f0)
skipping: [rchltxfe-d93180012-001] => (item=enp179s0f1)

TASK [get Fortville NICs MAC] **************************************************
changed: [rchltxfe-d93180012-001] => (item=enp179s0f0)
changed: [rchltxfe-d93180012-001] => (item=enp179s0f1)

TASK [validate Fortville NICs MACs] ********************************************
skipping: [rchltxfe-d93180012-001] => (item=enp179s0f0)
skipping: [rchltxfe-d93180012-001] => (item=enp179s0f1)

TASK [identify accelerators] ***************************************************
changed: [rchltxfe-d93180012-001]

TASK [retrieve device information] *********************************************
changed: [rchltxfe-d93180012-001] => (item=pci_0000_6a_00_0)

TASK [output device show information] ******************************************
ok: [rchltxfe-d93180012-001] => (item=pci_0000_6a_00_0) => {
    "msg": [
        "+-----------------------+-----------------------------------------------------------------------------+",
        "| Property              | Value                                                                       |",
        "+-----------------------+-----------------------------------------------------------------------------+",
        "| name                  | pci_0000_6a_00_0                                                            |",
        "| address               | 0000:6a:00.0                                                                |",
        "| class id              | 120000                                                                      |",
        "| vendor id             | 8086                                                                        |",
        "| device id             | 0d8f                                                                        |",
        "| class name            | Processing accelerators                                                     |",
        "| vendor name           | Intel Corporation                                                           |",
        "| device name           | Device 0d8f                                                                 |",
        "| numa_node             | 0                                                                           |",
        "| enabled               | True                                                                        |",
        "| sriov_totalvfs        | 8                                                                           |",
        "| sriov_numvfs          | 0                                                                           |",
        "| sriov_vfs_pci_address |                                                                             |",
        "| sriov_vf_pdevice_id   | None                                                                        |",
        "| extra_info            | {'expected_driver': None, 'expected_vf_driver': None, 'expected_numvfs': 0} |",
        "| created_at            | 2023-12-05T16:48:40.796961+00:00                                            |",
        "| updated_at            | 2023-12-12T23:01:12.818788+00:00                                            |",
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
changed: [rchltxfe-d93180012-001] => (item=pci_0000_6a_00_0)

TASK [output field information] ************************************************
ok: [rchltxfe-d93180012-001] => (item=pci_0000_6a_00_0) => {
    "msg": "0|{'expected_driver':None,'expected_vf_driver':None,'expected_numvfs':0}|None|None"
}

TASK [validate sriov_numvfs for Mount Bryce] ***********************************
skipping: [rchltxfe-d93180012-001] => (item=pci_0000_6a_00_0)

TASK [validate driver and sriov_vf_driver fields] ******************************
skipping: [rchltxfe-d93180012-001] => (item=pci_0000_6a_00_0)

TASK [validate extra_info field] ***********************************************
skipping: [rchltxfe-d93180012-001] => (item=pci_0000_6a_00_0)

TASK [get pod status] **********************************************************
changed: [rchltxfe-d93180012-001]

TASK [validate pod status] *****************************************************
changed: [rchltxfe-d93180012-001 -> localhost]

TASK [get system applications] *************************************************
changed: [rchltxfe-d93180012-001]

TASK [validate system applications] ********************************************
skipping: [rchltxfe-d93180012-001] => (item=cert-manager:21.12-28)
skipping: [rchltxfe-d93180012-001] => (item=nginx-ingress-controller:21.12-18)
skipping: [rchltxfe-d93180012-001] => (item=oidc-auth-apps:21.12-61)
skipping: [rchltxfe-d93180012-001] => (item=platform-integ-apps:21.12-46)

PLAY RECAP *********************************************************************
rchltxfe-d93180012-001     : ok=26   changed=19   unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ cat /home/XXXXXX/sanity/output_list
rchltxfe-d93180012-001 - check pod status
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./resize_fs_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook --inventory subclouds --ask-pass --user XXXXXX \
> --extra-vars '{"partitions":[1000],"hfs_docker":250,"cfs_docker_distribution":100}' \
> resize_fs.yaml 0</dev/null
SSH password:

XXXXXX [all] *********************************************************************

TASK [Retrieve list of controllers] ********************************************
changed: [rchltxfe-d93180012-001]

TASK [Retrieve distributed cloud role] *****************************************
changed: [rchltxfe-d93180012-001]

TASK [Confirm cgts volumes] ****************************************************
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/confirm_cgts_volumes.yaml for rchltxfe-d93180012-001

TASK [Retrieve rootfs disk] ****************************************************
changed: [rchltxfe-d93180012-001]

TASK [Retrieve available space on the rootfs device] ***************************
changed: [rchltxfe-d93180012-001]

TASK [set_fact] ****************************************************************
ok: [rchltxfe-d93180012-001]

TASK [Retrieve partitions present on the rootfs device] ************************
changed: [rchltxfe-d93180012-001]

TASK [Validate number of partitions requested] *********************************
skipping: [rchltxfe-d93180012-001]

TASK [Validate requested partition sizes] **************************************
skipping: [rchltxfe-d93180012-001] => (item=[u'1000.0', 1000])

TASK [Determine amount of free space after all partitions are allocated] *******
skipping: [rchltxfe-d93180012-001] => (item=[u'1000.0', 1000])

TASK [Display amount of free space after all partitions are allocated] *********
ok: [rchltxfe-d93180012-001] => {
    "msg": "633"
}

TASK [Verify there is enough space to allocate all partitions] *****************
skipping: [rchltxfe-d93180012-001]

TASK [Create new volumes] ******************************************************
skipping: [rchltxfe-d93180012-001] => (item=[u'1000.0', 1000])

TASK [Retrieve controller filesystems and sizes] *******************************
changed: [rchltxfe-d93180012-001]

TASK [Store requested controller filesystem sizes] *****************************
ok: [rchltxfe-d93180012-001] => (item=etcd 5)
ok: [rchltxfe-d93180012-001] => (item=docker-distribution 32)
ok: [rchltxfe-d93180012-001] => (item=platform 10)
ok: [rchltxfe-d93180012-001] => (item=extension 1)
ok: [rchltxfe-d93180012-001] => (item=database 10)

TASK [Build controller filesystem resizing parms] ******************************
skipping: [rchltxfe-d93180012-001] => (item=etcd 5)
ok: [rchltxfe-d93180012-001] => (item=docker-distribution 32)
skipping: [rchltxfe-d93180012-001] => (item=platform 10)
skipping: [rchltxfe-d93180012-001] => (item=extension 1)
skipping: [rchltxfe-d93180012-001] => (item=database 10)

TASK [Resize all controller filesystems] ***************************************
changed: [rchltxfe-d93180012-001]

TASK [Wait for all controller filesystems to be resized and fully sync] ********
FAILED - RETRYING: Wait for all controller filesystems to be resized and fully sync (720 retries left).
FAILED - RETRYING: Wait for all controller filesystems to be resized and fully sync (719 retries left).
FAILED - RETRYING: Wait for all controller filesystems to be resized and fully sync (718 retries left).
FAILED - RETRYING: Wait for all controller filesystems to be resized and fully sync (717 retries left).
FAILED - RETRYING: Wait for all controller filesystems to be resized and fully sync (716 retries left).
FAILED - RETRYING: Wait for all controller filesystems to be resized and fully sync (715 retries left).
FAILED - RETRYING: Wait for all controller filesystems to be resized and fully sync (714 retries left).
changed: [rchltxfe-d93180012-001]

TASK [Wait for any 400.001 alarm to clear] *************************************
changed: [rchltxfe-d93180012-001]

TASK [Resize host filesystems] *************************************************
included: /opt/platform-backup/upgrade/wrcp-21.12-upgrade/resize_hostfs.yaml for rchltxfe-d93180012-001

TASK [Retrieve host filesystems and sizes] *************************************
changed: [rchltxfe-d93180012-001]

TASK [Store requested host filesystem sizes] ***********************************
ok: [rchltxfe-d93180012-001] => (item=backup 25)
ok: [rchltxfe-d93180012-001] => (item=docker 58)
ok: [rchltxfe-d93180012-001] => (item=kubelet 10)
ok: [rchltxfe-d93180012-001] => (item=scratch 16)

TASK [Build hostfs resizing parms] *********************************************
skipping: [rchltxfe-d93180012-001] => (item=backup 25)
ok: [rchltxfe-d93180012-001] => (item=docker 58)
skipping: [rchltxfe-d93180012-001] => (item=kubelet 10)
skipping: [rchltxfe-d93180012-001] => (item=scratch 16)

TASK [Resize all host filesystems] *********************************************
changed: [rchltxfe-d93180012-001]

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
FAILED - RETRYING: Wait for any 250.001 alarm to clear (290 retries left).
changed: [rchltxfe-d93180012-001]

PLAY RECAP *********************************************************************
rchltxfe-d93180012-001     : ok=20   changed=12   unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$


```

### Upgrade mop 4 completed, next mop is k8 upgrade mop 5

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
| updated_at             | 2023-12-12 19:52:04.436675 |
+------------------------+----------------------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ echo '[subclouds]' > subclouds
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ dcmanager subcloud-group list-subclouds ${subcloud_group} -c name -f value >> subclouds
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ for subcloud in $(sed -n '/subclouds/ { :a; n; p; ba; }' < subclouds); do
> echo ${subcloud}
> dcmanager subcloud show ${subcloud} | \
> grep sync_status | \
> grep -E -v "in-sync|kubernetes_sync|firmware_sync|dc-cert_sync";
> done
rchltxfe-d93180012-001
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./sanity_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook --inventory subclouds --extra-vars "scenario=after" \
> --ask-pass --ask-become-pass --user XXXXXX \
> sanity.yaml 0</dev/null
SSH password:
XXXXXX password[defaults to SSH password]:

PLAY [all] *********************************************************************

TASK [Gathering Facts] *********************************************************
ok: [rchltxfe-d93180012-001]

TASK [Read in parameter file] **************************************************
ok: [rchltxfe-d93180012-001]

TASK [set expected Fortville firmware version] *********************************
ok: [rchltxfe-d93180012-001]

TASK [set expected N3000 firmware version] *************************************
ok: [rchltxfe-d93180012-001]

TASK [create directory /home/XXXXXX/sanity] **********************************
ok: [rchltxfe-d93180012-001 -> localhost]

TASK [delete existing file /home/XXXXXX/sanity/output_list] ******************
changed: [rchltxfe-d93180012-001 -> localhost]

TASK [create file /home/XXXXXX/sanity/output_list] ***************************
changed: [rchltxfe-d93180012-001 -> localhost]

TASK [get host patch status] ***************************************************
changed: [rchltxfe-d93180012-001]

TASK [validate host patch status] **********************************************
skipping: [rchltxfe-d93180012-001]

TASK [get host status] *********************************************************
changed: [rchltxfe-d93180012-001]

TASK [validate host status] ****************************************************
skipping: [rchltxfe-d93180012-001]

TASK [get current alarms] ******************************************************
changed: [rchltxfe-d93180012-001]

TASK [validate current alarms] *************************************************
skipping: [rchltxfe-d93180012-001]

TASK [get vim status] **********************************************************
changed: [rchltxfe-d93180012-001]

TASK [validate vim status] *****************************************************
skipping: [rchltxfe-d93180012-001]

TASK [calculate / partition expected usage] ************************************
changed: [rchltxfe-d93180012-001]

TASK [validate / partition free space] *****************************************
skipping: [rchltxfe-d93180012-001]

TASK [validate /opt/dc-vault partition free space] *****************************
skipping: [rchltxfe-d93180012-001]

TASK [identify N3000 NICs] *****************************************************
changed: [rchltxfe-d93180012-001]

TASK [get N3000 NICs firmware version] *****************************************
changed: [rchltxfe-d93180012-001] => (item=enp103s0f0)
changed: [rchltxfe-d93180012-001] => (item=enp103s0f1)
changed: [rchltxfe-d93180012-001] => (item=enp105s0f0)
changed: [rchltxfe-d93180012-001] => (item=enp105s0f1)

TASK [validate N3000 NICs firmware version] ************************************
skipping: [rchltxfe-d93180012-001] => (item=enp103s0f0)
skipping: [rchltxfe-d93180012-001] => (item=enp103s0f1)
skipping: [rchltxfe-d93180012-001] => (item=enp105s0f0)
skipping: [rchltxfe-d93180012-001] => (item=enp105s0f1)

TASK [get N3000 NICs MAC] ******************************************************
changed: [rchltxfe-d93180012-001] => (item=enp103s0f0)
changed: [rchltxfe-d93180012-001] => (item=enp103s0f1)
changed: [rchltxfe-d93180012-001] => (item=enp105s0f0)
changed: [rchltxfe-d93180012-001] => (item=enp105s0f1)

TASK [validate N3000 NICs MACs] ************************************************
skipping: [rchltxfe-d93180012-001] => (item=enp103s0f0)
skipping: [rchltxfe-d93180012-001] => (item=enp103s0f1)
skipping: [rchltxfe-d93180012-001] => (item=enp105s0f0)
skipping: [rchltxfe-d93180012-001] => (item=enp105s0f1)

TASK [identify Fortville NICs] *************************************************
changed: [rchltxfe-d93180012-001]

TASK [get Fortville NICs firmware version] *************************************
changed: [rchltxfe-d93180012-001] => (item=enp179s0f0)
changed: [rchltxfe-d93180012-001] => (item=enp179s0f1)

TASK [validate Fortville NICs firmware version] ********************************
skipping: [rchltxfe-d93180012-001] => (item=enp179s0f0)
skipping: [rchltxfe-d93180012-001] => (item=enp179s0f1)

TASK [get Fortville NICs MAC] **************************************************
changed: [rchltxfe-d93180012-001] => (item=enp179s0f0)
changed: [rchltxfe-d93180012-001] => (item=enp179s0f1)

TASK [validate Fortville NICs MACs] ********************************************
skipping: [rchltxfe-d93180012-001] => (item=enp179s0f0)
skipping: [rchltxfe-d93180012-001] => (item=enp179s0f1)

TASK [identify accelerators] ***************************************************
changed: [rchltxfe-d93180012-001]

TASK [retrieve device information] *********************************************
changed: [rchltxfe-d93180012-001] => (item=pci_0000_6a_00_0)

TASK [output device show information] ******************************************
ok: [rchltxfe-d93180012-001] => (item=pci_0000_6a_00_0) => {
    "msg": [
        "+-----------------------+-----------------------------------------------------------------------------+",
        "| Property              | Value                                                                       |",
        "+-----------------------+-----------------------------------------------------------------------------+",
        "| name                  | pci_0000_6a_00_0                                                            |",
        "| address               | 0000:6a:00.0                                                                |",
        "| class id              | 120000                                                                      |",
        "| vendor id             | 8086                                                                        |",
        "| device id             | 0d8f                                                                        |",
        "| class name            | Processing accelerators                                                     |",
        "| vendor name           | Intel Corporation                                                           |",
        "| device name           | Device 0d8f                                                                 |",
        "| numa_node             | 0                                                                           |",
        "| enabled               | True                                                                        |",
        "| sriov_totalvfs        | 8                                                                           |",
        "| sriov_numvfs          | 0                                                                           |",
        "| sriov_vfs_pci_address |                                                                             |",
        "| sriov_vf_pdevice_id   | None                                                                        |",
        "| extra_info            | {'expected_driver': None, 'expected_vf_driver': None, 'expected_numvfs': 0} |",
        "| created_at            | 2023-12-05T16:48:40.796961+00:00                                            |",
        "| updated_at            | 2023-12-12T23:01:12.818788+00:00                                            |",
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
changed: [rchltxfe-d93180012-001] => (item=pci_0000_6a_00_0)

TASK [output field information] ************************************************
ok: [rchltxfe-d93180012-001] => (item=pci_0000_6a_00_0) => {
    "msg": "0|{'expected_driver':None,'expected_vf_driver':None,'expected_numvfs':0}|None|None"
}

TASK [validate sriov_numvfs for Mount Bryce] ***********************************
skipping: [rchltxfe-d93180012-001] => (item=pci_0000_6a_00_0)

TASK [validate driver and sriov_vf_driver fields] ******************************
skipping: [rchltxfe-d93180012-001] => (item=pci_0000_6a_00_0)

TASK [validate extra_info field] ***********************************************
skipping: [rchltxfe-d93180012-001] => (item=pci_0000_6a_00_0)

TASK [get pod status] **********************************************************
changed: [rchltxfe-d93180012-001]

TASK [validate pod status] *****************************************************
changed: [rchltxfe-d93180012-001 -> localhost]

TASK [get system applications] *************************************************
changed: [rchltxfe-d93180012-001]

TASK [validate system applications] ********************************************
skipping: [rchltxfe-d93180012-001] => (item=cert-manager:21.12-28)
skipping: [rchltxfe-d93180012-001] => (item=nginx-ingress-controller:21.12-18)
skipping: [rchltxfe-d93180012-001] => (item=oidc-auth-apps:21.12-61)
skipping: [rchltxfe-d93180012-001] => (item=platform-integ-apps:21.12-46)

PLAY RECAP *********************************************************************
rchltxfe-d93180012-001     : ok=26   changed=19   unreachable=0    failed=0

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
| created_at             | 2023-12-12T23:32:54.824563 |
| updated_at             | None                       |
+------------------------+----------------------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ dcmanager strategy-step list -c cloud -c stage -c state
+------------------------+-------+---------+
| cloud                  | stage | state   |
+------------------------+-------+---------+
| rchltxfe-d93180012-001 |     1 | initial |
+------------------------+-------+---------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ dcmanager kube-upgrade-strategy apply
+------------------------+----------------------------+
| Field                  | Value                      |
+------------------------+----------------------------+
| strategy type          | kubernetes                 |
| subcloud apply type    | parallel                   |
| max parallel subclouds | 50                         |
| stop on failure        | False                      |
| state                  | applying                   |
| created_at             | 2023-12-12T23:32:54.824563 |
| updated_at             | 2023-12-12T23:33:32.062975 |
+------------------------+----------------------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ watch -n15 dcmanager strategy-step list -c cloud -c state -c details \
> --max-width 100 --sort-column details --sort-column state

Every 15.0s: dcmanager strategy-step list -c cloud -c state -c details --max-width 100 --sort-colu...  Tue Dec 12 23:34:00 2023

+------------------------+-----------------------------------------+---------+
| cloud                  | state                                   | details |
+------------------------+-----------------------------------------+---------+
| rchltxfe-d93180012-001 | kube creating vim kube upgrade strategy |         |
+------------------------+-----------------------------------------+---------+


Every 15.0s: dcmanager strategy-step list -c cloud -c state -c details --max-width 100 --sort-colu...  Tue Dec 12 23:39:01 2023

+------------------------+-----------------------------------------+-----------------------------+
| cloud                  | state                                   | details                     |
+------------------------+-----------------------------------------+-----------------------------+
| rchltxfe-d93180012-001 | kube applying vim kube upgrade strategy | apply phase is 22% complete |
+------------------------+-----------------------------------------+-----------------------------+

Every 15.0s: dcmanager strategy-step list -c cloud -c state -c details --max-width 100 --sort-colu...  Tue Dec 12 23:46:24 2023

+------------------------+-----------------------------------------+-----------------------------+
| cloud                  | state                                   | details                     |
+------------------------+-----------------------------------------+-----------------------------+
| rchltxfe-d93180012-001 | kube applying vim kube upgrade strategy | apply phase is 77% complete |
+------------------------+-----------------------------------------+-----------------------------+
Every 15.0s: dcmanager strategy-step list -c cloud -c state -c details --max-width 100 --sort-colu...  Tue Dec 12 23:48:30 2023

+------------------------+----------+---------+
| cloud                  | state    | details |
+------------------------+----------+---------+
| rchltxfe-d93180012-001 | complete |         |
+------------------------+----------+---------+

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ dcmanager kube-upgrade-strategy delete
+------------------------+----------------------------+
| Field                  | Value                      |
+------------------------+----------------------------+
| strategy type          | kubernetes                 |
| subcloud apply type    | parallel                   |
| max parallel subclouds | 50                         |
| stop on failure        | False                      |
| state                  | deleting                   |
| created_at             | 2023-12-12T23:32:54.824563 |
| updated_at             | 2023-12-12T23:49:00.239789 |
+------------------------+----------------------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ watch dcmanager kube-upgrade-strategy show

Every 2.0s: dcmanager kube-upgrade-strategy show                                                       Tue Dec 12 23:49:47 2023

ERROR (app) Strategy of type 'kubernetes' not found

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./cleanup-old-pods_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook --inventory subclouds --ask-pass --user XXXXXX \
> cleanup-old-pods.yaml 0</dev/null
SSH password:

XXXXXX [all] *********************************************************************

TASK [Fetch pods in failed state] **********************************************
changed: [rchltxfe-d93180012-001]

TASK [Delete failed pods] ******************************************************

PLAY RECAP *********************************************************************
rchltxfe-d93180012-001     : ok=1    changed=1    unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./apply-kubelet-config_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook --inventory subclouds --ask-pass --user XXXXXX apply-kubelet-config.yaml \
> 0</dev/null
SSH password:

XXXXXX [all] *********************************************************************

TASK [Remove kubelet-config settings for old versions] *************************
changed: [rchltxfe-d93180012-001]

TASK [Reapply kubelet-config settings] *****************************************
changed: [rchltxfe-d93180012-001]

TASK [Wait for kubelet-config settings to be applied] **************************
FAILED - RETRYING: Wait for kubelet-config settings to be applied (10 retries left).
changed: [rchltxfe-d93180012-001]

TASK [Output kubelet-config info] **********************************************
ok: [rchltxfe-d93180012-001] => {
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
rchltxfe-d93180012-001     : ok=4    changed=3    unreachable=0    failed=0

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
| created_at             | 2023-12-13T00:02:28.325415 |
| updated_at             | None                       |
+------------------------+----------------------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ dcmanager strategy-step list -c cloud -c stage -c state
+------------------------+-------+---------+
| cloud                  | stage | state   |
+------------------------+-------+---------+
| rchltxfe-d93180012-001 |     1 | initial |
+------------------------+-------+---------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ dcmanager kube-upgrade-strategy apply
+------------------------+----------------------------+
| Field                  | Value                      |
+------------------------+----------------------------+
| strategy type          | kubernetes                 |
| subcloud apply type    | parallel                   |
| max parallel subclouds | 50                         |
| stop on failure        | False                      |
| state                  | applying                   |
| created_at             | 2023-12-13T00:02:28.325415 |
| updated_at             | 2023-12-13T00:02:44.445820 |
+------------------------+----------------------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

watch -n15 dcmanager strategy-step list -c cloud -c state -c details \
--max-width 100 --sort-column details --sort-column state

Every 15.0s: dcmanager strategy-step list -c cloud -c state -c details --max-width 100 --sort-colu...  Wed Dec 13 00:11:55 2023

+------------------------+-----------------------------------------+-----------------------------+
| cloud                  | state                                   | details                     |
+------------------------+-----------------------------------------+-----------------------------+
| rchltxfe-d93180012-001 | kube applying vim kube upgrade strategy | apply phase is 55% complete |
+------------------------+-----------------------------------------+-----------------------------+


Every 15.0s: dcmanager strategy-step list -c cloud -c state -c details --max-width 100 --sort-colu...  Wed Dec 13 00:21:08 2023

+------------------------+----------+---------+
| cloud                  | state    | details |
+------------------------+----------+---------+
| rchltxfe-d93180012-001 | complete |         |
+------------------------+----------+---------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ watch dcmanager kube-upgrade-strategy show
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./cleanup-old-pods_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook --inventory subclouds --ask-pass --user XXXXXX \
> cleanup-old-pods.yaml 0</dev/null
SSH password:

XXXXXX [all] *********************************************************************

TASK [Fetch pods in failed state] **********************************************
changed: [rchltxfe-d93180012-001]

TASK [Delete failed pods] ******************************************************

PLAY RECAP *********************************************************************
rchltxfe-d93180012-001     : ok=1    changed=1    unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ ANSIBLE_LOG_PATH=./apply-kubelet-config_$(date "+%Y%m%d%H%M%S").log \
> ansible-playbook --inventory subclouds --ask-pass --user XXXXXX apply-kubelet-config.yaml \
> 0</dev/null
SSH password:

XXXXXX [all] *********************************************************************

TASK [Remove kubelet-config settings for old versions] *************************
changed: [rchltxfe-d93180012-001]

TASK [Reapply kubelet-config settings] *****************************************
changed: [rchltxfe-d93180012-001]

TASK [Wait for kubelet-config settings to be applied] **************************
FAILED - RETRYING: Wait for kubelet-config settings to be applied (10 retries left).
changed: [rchltxfe-d93180012-001]

TASK [Output kubelet-config info] **********************************************
ok: [rchltxfe-d93180012-001] => {
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
rchltxfe-d93180012-001     : ok=4    changed=3    unreachable=0    failed=0

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ sleep 120
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ for subcloud in $(dcmanager subcloud-group list-subclouds ${subcloud_group} -f value -c name); do
> dcmanager subcloud show ${subcloud} | awk -F \| -v SUBCLOUD=${subcloud} \
> '$2 ~ / kubernetes_sync_status / { gsub(/ /,"",$3);printf("%-40s: %s\n",SUBCLOUD,$3) }'
> done
rchltxfe-d93180012-001                  : out-of-sync
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ dcmanager kube-upgrade-strategy create --group ${subcloud_group}
+------------------------+----------------------------+
| Field                  | Value                      |
+------------------------+----------------------------+
| strategy type          | kubernetes                 |
| subcloud apply type    | parallel                   |
| max parallel subclouds | 50                         |
| stop on failure        | False                      |
| state                  | initial                    |
| created_at             | 2023-12-13T00:31:40.724876 |
| updated_at             | None                       |
+------------------------+----------------------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ dcmanager strategy-step list -c cloud -c stage -c state
+------------------------+-------+---------+
| cloud                  | stage | state   |
+------------------------+-------+---------+
| rchltxfe-d93180012-001 |     1 | initial |
+------------------------+-------+---------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ dcmanager kube-upgrade-strategy apply
+------------------------+----------------------------+
| Field                  | Value                      |
+------------------------+----------------------------+
| strategy type          | kubernetes                 |
| subcloud apply type    | parallel                   |
| max parallel subclouds | 50                         |
| stop on failure        | False                      |
| state                  | applying                   |
| created_at             | 2023-12-13T00:31:40.724876 |
| updated_at             | 2023-12-13T00:31:57.861061 |
+------------------------+----------------------------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$

[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ dcmanager subcloud list
+----+------------------------+------------+--------------+---------------+---------+
| id | name                   | management | availability | deploy status | sync    |
+----+------------------------+------------+--------------+---------------+---------+
|  2 | rchltxfe-d93180012-001 | managed    | online       | complete      | in-sync |
+----+------------------------+------------+--------------+---------------+---------+
[XXXXXX@controller-0 wrcp-21.12-upgrade(keystone_admin)]$ dcmanager subcloud show rchltxfe-d93180012-001
+-----------------------------+---------------------------------+
| Field                       | Value                           |
+-----------------------------+---------------------------------+
| id                          | 2                               |
| name                        | rchltxfe-d93180012-001          |
| description                 | Wind River Cloud Platform 21.05 |
| location                    | rchltxfe-d93180012-001          |
| software_version            | 21.12                           |
| management                  | managed                         |
| availability                | online                          |
| deploy_status               | complete                        |
| management_subnet           | 2607:f160:10:907b::/64          |
| management_start_ip         | 2607:f160:10:907b:ce:40a::      |
| management_end_ip           | 2607:f160:10:907b:ce:40a:0:f    |
| management_gateway_ip       | 2607:f160:10:907b:ce:28::       |
| systemcontroller_gateway_ip | 2607:f160:0:3048:cd:28::        |
| group_id                    | 1                               |
| created_at                  | 2023-12-05 15:46:21.700016      |
| updated_at                  | 2023-12-12 23:09:00.808828      |
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

```


### completed upgrade, here is the subcloud now..

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ system show
+------------------------+--------------------------------------+
| Property               | Value                                |
+------------------------+--------------------------------------+
| contact                | None                                 |
| created_at             | 2023-12-05T16:16:00.443725+00:00     |
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
| updated_at             | 2023-12-12T22:12:17.176092+00:00     |
| uuid                   | 3d94122e-c272-4b8a-a4b3-4f73302fd9d8 |
| vswitch_type           | none                                 |
+------------------------+--------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ system application-list
+--------------------------+----------+-----------------------------------+-----------------------+----------+-------------+
| application              | version  | manifest name                     | manifest file         | status   | progress    |
+--------------------------+----------+-----------------------------------+-----------------------+----------+-------------+
| cert-manager             | 21.12-28 | cert-manager-manifest             | certmanager-manifest. | applied  | Application |
|                          |          |                                   | yaml                  |          | update from |
|                          |          |                                   |                       |          | version 21. |
|                          |          |                                   |                       |          | 05-17 to    |
|                          |          |                                   |                       |          | version 21. |
|                          |          |                                   |                       |          | 12-28       |
|                          |          |                                   |                       |          | completed.  |
|                          |          |                                   |                       |          |             |
| metrics-server           | 21.12-9  | metrics-server-manifest           | metrics-              | applied  | Application |
|                          |          |                                   | server_manifest.yaml  |          | update from |
|                          |          |                                   |                       |          | version 21. |
|                          |          |                                   |                       |          | 05-6 to     |
|                          |          |                                   |                       |          | version 21. |
|                          |          |                                   |                       |          | 12-9        |
|                          |          |                                   |                       |          | completed.  |
|                          |          |                                   |                       |          |             |
| nginx-ingress-controller | 21.12-18 | nginx-ingress-controller-manifest | nginx_ingress_control | applied  | Application |
|                          |          |                                   | ler_manifest.yaml     |          | update from |
|                          |          |                                   |                       |          | version 21. |
|                          |          |                                   |                       |          | 05-16 to    |
|                          |          |                                   |                       |          | version 21. |
|                          |          |                                   |                       |          | 12-18       |
|                          |          |                                   |                       |          | completed.  |
|                          |          |                                   |                       |          |             |
| oidc-auth-apps           | 21.12-61 | oidc-auth-manifest                | manifest.yaml         | applied  | Application |
|                          |          |                                   |                       |          | update from |
|                          |          |                                   |                       |          | version 21. |
|                          |          |                                   |                       |          | 05-44 to    |
|                          |          |                                   |                       |          | version 21. |
|                          |          |                                   |                       |          | 12-61       |
|                          |          |                                   |                       |          | completed.  |
|                          |          |                                   |                       |          |             |
| platform-integ-apps      | 21.12-46 | platform-integration-manifest     | manifest.yaml         | applied  | Application |
|                          |          |                                   |                       |          | update from |
|                          |          |                                   |                       |          | version 21. |
|                          |          |                                   |                       |          | 05-30 to    |
|                          |          |                                   |                       |          | version 21. |
|                          |          |                                   |                       |          | 12-46       |
|                          |          |                                   |                       |          | completed.  |
|                          |          |                                   |                       |          |             |
| rook-ceph-apps           | 1.0-5    | rook-ceph-manifest                | manifest.yaml         | uploaded | completed   |
+--------------------------+----------+-----------------------------------+-----------------------+----------+-------------+
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

```