# HPE ILO5 3.06 BIOS H08 v2.12
# HPE Sapphire Rapids E910t server
# 6/28/24 James Patchett - MTCE Lab VCPfe
# Platform Deploymnet MEAKV-965 

## Test case is to deploy sublcoud with production automation in the lab.


## welktxef-931881-rh-le0e910-006
ILO:  2607:f160:10:922b:ce:406:0:1000
OAM:  2607:f160:10:922b:ce:40a:0:f400

## Subcloud welktxef-d931882-006
## General info before we start

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ system show
+------------------------+--------------------------------------+
| Property               | Value                                |
+------------------------+--------------------------------------+
| contact                | None                                 |
| created_at             | 2024-08-23T14:50:47.190124+00:00     |
| description            | None                                 |
| distributed_cloud_role | subcloud                             |
| https_enabled          | True                                 |
| latitude               | None                                 |
| location               | None                                 |
| longitude              | None                                 |
| name                   | welktxef-d931882-006                 |
| region_name            | welktxef-d931882-006                 |
| sdn_enabled            | False                                |
| security_feature       | spectre_meltdown_v1                  |
| service_project_name   | services                             |
| shared_services        | []                                   |
| software_version       | 22.12                                |
| system_mode            | simplex                              |
| system_type            | All-in-one                           |
| timezone               | UTC                                  |
| updated_at             | 2024-08-27T22:05:15.567565+00:00     |
| uuid                   | 2758a567-d053-4553-b551-4042fd27da68 |
| vswitch_type           | none                                 |
+------------------------+--------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ system oam-show
+----------------+---------------------------------------+
| Property       | Value                                 |
+----------------+---------------------------------------+
| created_at     | 2024-08-23T14:53:04.135326+00:00      |
| isystem_uuid   | 2758a567-d053-4553-b551-4042fd27da68  |
| oam_end_ip     | 2607:f160:10:922b:ffff:ffff:ffff:fffe |
| oam_gateway_ip | 2607:f160:10:922b:ce:28::             |
| oam_ip         | 2607:f160:10:922b:ce:40a:0:f400       |
| oam_start_ip   | 2607:f160:10:922b::1                  |
| oam_subnet     | 2607:f160:10:922b::/64                |
| updated_at     | None                                  |
| uuid           | 0d664ebd-8b65-4a74-b19e-16c31d9d6bdd  |
+----------------+---------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$  system application-list
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

[XXXXXX@controller-0 ~(keystone_admin)]$ fm alarm-list

[XXXXXX@controller-0 ~(keystone_admin)]$

```



## Initiate Deployment of subcloud
## Subcloud welktxsr-d931883-001

### Refer to uploaded log from script of installation details of Ansible deployment
### welktxef-d931882-006_ansiblePrestaged_20240823142940.log


## Deploymnet of subcloud was a success