# HPE ILO6 1.57 BIOS H11 v1.11
# HPE Sapphire Rapids E930t server
# 4/08/24 James Patchett - MTCE Lab VCPfe
# Platform Deploymnet MEAKV-965 

## Controller rchltxfe-c000000-001
OAM:  2607:f160:0:3043:cd:290:0:10

## welktxsr-931883-rh-le093s6-001
## welktxsr-d931883-001
ILO:  2607:f160:10:80b1:ce:40a:0:e002
OAM:  2607:f160:10:80b1:ce:40a:0:f402

## Controller rchltxfe-c000000-001
## General info before we start

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ system show
+------------------------+--------------------------------------+
| Property               | Value                                |
+------------------------+--------------------------------------+
| contact                | demo.engineer@verizon.com              |
| created_at             | 2024-05-24T19:38:31.409443+00:00     |
| description            | Wind River Cloud Platform 22.12.5    |
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
| software_version       | 22.12                                |
| system_mode            | duplex                               |
| system_type            | Standard                             |
| timezone               | UTC                                  |
| updated_at             | 2024-05-24T20:56:09.336633+00:00     |
| uuid                   | 8eac0d49-bc33-43eb-a80e-fe2d28db5749 |
| vswitch_type           | none                                 |
+------------------------+--------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ system oam-show
+-----------------+--------------------------------------+
| Property        | Value                                |
+-----------------+--------------------------------------+
| created_at      | 2024-05-24T19:40:09.737477+00:00     |
| isystem_uuid    | 8eac0d49-bc33-43eb-a80e-fe2d28db5749 |
| oam_c0_ip       | 2607:f160:0:3043:cd:290:0:11         |
| oam_c1_ip       | 2607:f160:0:3043:cd:290:0:12         |
| oam_floating_ip | 2607:f160:0:3043:cd:290:0:10         |
| oam_gateway_ip  | 2607:f160:0:3043:cd:28::             |
| oam_subnet      | 2607:f160:0:3043::/64                |
| updated_at      | None                                 |
| uuid            | f30d40d6-2ed8-4e8b-9c2f-bf52462744c3 |
+-----------------+--------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ system application-list
+--------------------------+----------+-------------------------------------------+------------------+----------+-----------+
| application              | version  | manifest name                             | manifest file    | status   | progress  |
+--------------------------+----------+-------------------------------------------+------------------+----------+-----------+
| cert-manager             | 22.12-8  | cert-manager-fluxcd-manifests             | fluxcd-manifests | applied  | completed |
| nginx-ingress-controller | 22.12-1  | nginx-ingress-controller-fluxcd-manifests | fluxcd-manifests | applied  | completed |
| oidc-auth-apps           | 22.12-6  | oidc-auth-apps-fluxcd-manifests           | fluxcd-manifests | applied  | completed |
| platform-integ-apps      | 22.12-72 | platform-integ-apps-fluxcd-manifests      | fluxcd-manifests | uploaded | completed |
| wr-analytics             | 23.09-1  | wr-analytics-fluxcd-manifests             | fluxcd-manifests | applied  | completed |
+--------------------------+----------+-------------------------------------------+------------------+----------+-----------+
[XXXXXX@controller-0 ~(keystone_admin)]$ sw-patch list
Error: Command must be run as sudo or root
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
WRCP_22.12_PATCH_0001  Y    22.12    Committed
WRCP_22.12_PATCH_0002  Y    22.12    Committed
WRCP_22.12_PATCH_0003  Y    22.12    Committed
WRCP_22.12_PATCH_0004  Y    22.12    Committed
WRCP_22.12_PATCH_0005  Y    22.12    Committed

[XXXXXX@controller-0 ~(keystone_admin)]$

```


## Initiate Deployment of subcloud
## Subcloud welktxsr-d931883-001

### Refer to uploaded log from script of installation details of Ansible deployment
### install-welktxsr-d931833-001.txt


### Validate deployment of subcloud on Controller

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ dcmanager subcloud list
+----+---------------------------+------------+--------------+---------------+-------------+------------------+----------------------------+
| id | name                      | management | availability | deploy status | sync        | backup status    | backup datetime            |
+----+---------------------------+------------+--------------+---------------+-------------+------------------+----------------------------+
|  2 | welktxef-d931887-021      | managed    | online       | complete      | in-sync     | complete-central | 2024-06-24 22:27:34.331295 |
|  3 | welktxsr-d931833-012      | unmanaged  | offline      | rehome-failed | unknown     | None             | None                       |
|  9 | welktxsr-d931883-008      | managed    | online       | complete      | in-sync     | complete-central | 2024-06-02 20:19:36.129313 |
| 13 | welktxef-d931855-003      | managed    | online       | complete      | in-sync     | None             | None                       |
| 15 | welktxsr-d29991572156-001 | managed    | online       | complete      | in-sync     | None             | None                       |
| 24 | welktxfb-d29991572161-001 | managed    | online       | complete      | in-sync     | None             | None                       |
| 32 | welktxfb-d29991572162-001 | managed    | online       | complete      | in-sync     | None             | None                       |
| 42 | welktxef-d931883-022      | managed    | offline      | complete      | out-of-sync | None             | None                       |
| 43 | welktxef-d931884-034      | managed    | online       | complete      | out-of-sync | None             | None                       |
| 47 | welktxsr-d931883-002      | managed    | online       | complete      | in-sync     | None             | None                       |
| 48 | welktxsr-d931883-001      | managed    | online       | complete      | in-sync     | None             | None                       |
| 50 | welktxfb-d1372466-015     | unmanaged  | online       | complete      | out-of-sync | None             | None                       |
+----+---------------------------+------------+--------------+---------------+-------------+------------------+----------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ dcmanager subcloud show welktxsr-d931883-001
+-----------------------------+---------------------------------+
| Field                       | Value                           |
+-----------------------------+---------------------------------+
| id                          | 48                              |
| name                        | welktxsr-d931883-001            |
| description                 | Wind River Cloud Platform 22.12 |
| location                    | welktxsr-d931883-001            |
| software_version            | 22.12                           |
| management                  | managed                         |
| availability                | online                          |
| deploy_status               | complete                        |
| management_subnet           | 2607:f160:10:80d2::/64          |
| management_start_ip         | 2607:f160:10:80d2:ce:40a::      |
| management_end_ip           | 2607:f160:10:80d2:ce:40a:0:f    |
| management_gateway_ip       | 2607:f160:10:80d2:ce:23::       |
| systemcontroller_gateway_ip | 2607:f160:0:3042:cd:28::        |
| group_id                    | 1                               |
| created_at                  | 2024-06-28 16:27:04.601936      |
| updated_at                  | 2024-06-28 17:55:05.667690      |
| backup_status               | None                            |
| backup_datetime             | None                            |
| dc-cert_sync_status         | in-sync                         |
| firmware_sync_status        | in-sync                         |
| identity_sync_status        | in-sync                         |
| kubernetes_sync_status      | in-sync                         |
| kube-rootca_sync_status     | in-sync                         |
| load_sync_status            | in-sync                         |
| patching_sync_status        | in-sync                         |
| platform_sync_status        | in-sync                         |
+-----------------------------+---------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$
```


## Deploymnet of subcloud was a success