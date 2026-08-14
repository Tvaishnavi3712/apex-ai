# HPE ILO5 3.06 BIOS H10 v1.70
# HPE Sapphire Rapids E920t server
# 6/28/24 James Patchett - MTCE Lab VCPfe
# Platform Deploymnet MEAKV-965 

## Test case is to deploy sublcoud with production automation in the lab.


## welktxef-931884-rh-le292s6-034
ILO:  2607:f160:10:9249:ce:40a:0:e009
OAM:  2607:f160:10:9249:ce:40a:0:f408

## Subcloud welktxef-d931884-034 
## General info before we start

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ system show
+------------------------+--------------------------------------+
| Property               | Value                                |
+------------------------+--------------------------------------+
| contact                | None                                 |
| created_at             | 2024-08-23T14:55:17.130193+00:00     |
| description            | None                                 |
| distributed_cloud_role | subcloud                             |
| https_enabled          | True                                 |
| latitude               | None                                 |
| location               | None                                 |
| longitude              | None                                 |
| name                   | welktxef-d931884-034                 |
| region_name            | welktxef-d931884-034                 |
| sdn_enabled            | False                                |
| security_feature       | spectre_meltdown_v1                  |
| service_project_name   | services                             |
| shared_services        | []                                   |
| software_version       | 22.12                                |
| system_mode            | simplex                              |
| system_type            | All-in-one                           |
| timezone               | UTC                                  |
| updated_at             | 2024-08-28T16:36:15.405154+00:00     |
| uuid                   | 55b2fccb-ef0b-4e94-afa1-bcefcb789357 |
| vswitch_type           | none                                 |
+------------------------+--------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ system oam-show
+----------------+---------------------------------------+
| Property       | Value                                 |
+----------------+---------------------------------------+
| created_at     | 2024-08-23T14:57:11.033367+00:00      |
| isystem_uuid   | 55b2fccb-ef0b-4e94-afa1-bcefcb789357  |
| oam_end_ip     | 2607:f160:10:9249:ffff:ffff:ffff:fffe |
| oam_gateway_ip | 2607:f160:10:9249:ce:28::             |
| oam_ip         | 2607:f160:10:9249:ce:40a:0:f408       |
| oam_start_ip   | 2607:f160:10:9249::1                  |
| oam_subnet     | 2607:f160:10:9249::/64                |
| updated_at     | None                                  |
| uuid           | 2970009b-1352-4840-a9a7-7274899c7946  |
+----------------+---------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ system application-list
+--------------------------+-----------+-------------------------------------------+------------------+---------+-----------+
| application              | version   | manifest name                             | manifest file    | status  | progress  |
+--------------------------+-----------+-------------------------------------------+------------------+---------+-----------+
| cert-manager             | 22.12-8   | cert-manager-fluxcd-manifests             | fluxcd-manifests | applied | completed |
| metrics-server           | 22.12-2   | metrics-server-fluxcd-manifests           | fluxcd-manifests | applied | completed |
| nginx-ingress-controller | 22.12-1   | nginx-ingress-controller-fluxcd-manifests | fluxcd-manifests | applied | completed |
| oidc-auth-apps           | 22.12-6   | oidc-auth-apps-fluxcd-manifests           | fluxcd-manifests | applied | completed |
| platform-integ-apps      | 22.12-72  | platform-integ-apps-fluxcd-manifests      | fluxcd-manifests | applied | completed |
| ptp-notification         | 22.12-140 | ptp-notification-fluxcd-manifests         | fluxcd-manifests | applied | completed |
| wr-analytics             | 23.09-1   | wr-analytics-fluxcd-manifests             | fluxcd-manifests | applied | completed |
+--------------------------+-----------+-------------------------------------------+------------------+---------+-----------+
[XXXXXX@controller-0 ~(keystone_admin)]$ sw-patch query
      Patch ID         RR  Release  Patch State
=====================  ==  =======  ===========
WRCP_22.12_PATCH_0001  Y    22.12    Committed
WRCP_22.12_PATCH_0002  Y    22.12    Committed
WRCP_22.12_PATCH_0003  Y    22.12    Committed
WRCP_22.12_PATCH_0004  Y    22.12    Committed
WRCP_22.12_PATCH_0005  Y    22.12    Committed

[XXXXXX@controller-0 ~(keystone_admin)]$
```

## Initiate Deployment of subcloud
## Subcloud welktxef-d931884-034 

### Refer to uploaded log from script of installation details of Ansible deployment
### welktxef-d931884-034_ansiblePrestaged_20240823143034.log


## Deploymnet of subcloud was a success