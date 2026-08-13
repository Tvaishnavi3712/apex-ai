# HPE ILO6 1.57 BIOS H11 v1.11
# HPE Sapphire Rapids E930t server
# 3/24/24 James Patchett - MTCE Lab VCPfe
# BMC Playbook MEAKV-1793

## welktxsr-931883-rh-le093s6-001
ILO:  2607:f160:10:80b1:ce:40a:0:e002
OAM:  2607:f160:10:80b1:ce:40a:0:f402

## Subcloud welktxsr-d931883-001
## General info before we start

```log
XXXXXX@controller-0:~$ source /etc/platform/openrc
[XXXXXX@controller-0 ~(keystone_admin)]$ system show
+------------------------+--------------------------------------+
| Property               | Value                                |
+------------------------+--------------------------------------+
| contact                | None                                 |
| created_at             | 2024-03-21T18:58:05.425483+00:00     |
| description            | None                                 |
| distributed_cloud_role | subcloud                             |
| https_enabled          | True                                 |
| latitude               | None                                 |
| location               | None                                 |
| longitude              | None                                 |
| name                   | welktxsr-d931883-001                 |
| region_name            | welktxsr-d931883-001                 |
| sdn_enabled            | False                                |
| security_feature       | spectre_meltdown_v1                  |
| service_project_name   | services                             |
| shared_services        | []                                   |
| software_version       | 22.12                                |
| system_mode            | simplex                              |
| system_type            | All-in-one                           |
| timezone               | UTC                                  |
| updated_at             | 2024-03-26T18:48:17.340880+00:00     |
| uuid                   | 158d0999-7bda-4663-a51f-7576c175117f |
| vswitch_type           | none                                 |
+------------------------+--------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ system oam-show
+----------------+---------------------------------------+
| Property       | Value                                 |
+----------------+---------------------------------------+
| created_at     | 2024-03-21T18:59:47.482500+00:00      |
| isystem_uuid   | 158d0999-7bda-4663-a51f-7576c175117f  |
| oam_end_ip     | 2607:f160:10:80b1:ffff:ffff:ffff:fffe |
| oam_gateway_ip | 2607:f160:10:80b1:ce:23::             |
| oam_ip         | 2607:f160:10:80b1:ce:40a:0:f402       |
| oam_start_ip   | 2607:f160:10:80b1::1                  |
| oam_subnet     | 2607:f160:10:80b1::/64                |
| updated_at     | None                                  |
| uuid           | 45723e45-0576-4cda-9d26-7a70682b972c  |
+----------------+---------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ system application-list
+--------------------------+----------+-------------------------------------------+------------------+---------+-----------+
| application              | version  | manifest name                             | manifest file    | status  | progress  |
+--------------------------+----------+-------------------------------------------+------------------+---------+-----------+
| cert-manager             | 22.12-8  | cert-manager-fluxcd-manifests             | fluxcd-manifests | applied | completed |
| metrics-server           | 22.12-1  | metrics-server-fluxcd-manifests           | fluxcd-manifests | applied | completed |
| nginx-ingress-controller | 22.12-1  | nginx-ingress-controller-fluxcd-manifests | fluxcd-manifests | applied | completed |
| oidc-auth-apps           | 22.12-6  | oidc-auth-apps-fluxcd-manifests           | fluxcd-manifests | applied | completed |
| platform-integ-apps      | 22.12-66 | platform-integ-apps-fluxcd-manifests      | fluxcd-manifests | applied | completed |
| ptp-notification         | 22.      | ptp-notification-fluxcd-manifests         | fluxcd-manifests | applied | completed |
|                          | 12-138   |                                           |                  |         |           |
|                          |          |                                           |                  |         |           |
| sriov-fec-operator       | 22.12-3  | sriov-fec-operator-fluxcd-manifests       | fluxcd-manifests | applied | completed |
| wr-analytics             | 23.09-0  | wr-analytics-fluxcd-manifests             | fluxcd-manifests | applied | completed |
+--------------------------+----------+-------------------------------------------+------------------+---------+-----------+
[XXXXXX@controller-0 ~(keystone_admin)]$ sw-patch query
      Patch ID         RR  Release  Patch State
=====================  ==  =======  ===========
WRCP_22.12_PATCH_0001  Y    22.12    Committed
WRCP_22.12_PATCH_0002  Y    22.12    Committed
WRCP_22.12_PATCH_0003  Y    22.12    Committed
WRCP_22.12_PATCH_0004  Y    22.12     Applied

[XXXXXX@controller-0 ~(keystone_admin)]$ fm alarm-list
+----------+-------------------------------------------------------+--------------------+----------+--------------+
| Alarm ID | Reason Text                                           | Entity ID          | Severity | Time Stamp   |
+----------+-------------------------------------------------------+--------------------+----------+--------------+
| 100.119  | controller-0 is not locked to remote PTP Grand Master | host=controller-0. | major    | 2024-03-26T1 |
|          |                                                       | instance=ptp4l-    |          | 8:48:42.     |
|          |                                                       | legacy-2.ptp=no-   |          | 707911       |
|          |                                                       | lock               |          |              |
|          |                                                       |                    |          |              |
| 100.119  | controller-0 is not locked to remote PTP Grand Master | host=controller-0. | major    | 2024-03-26T1 |
|          |                                                       | instance=ptp4l-    |          | 8:48:42.     |
|          |                                                       | legacy.ptp=no-lock |          | 036900       |
|          |                                                       |                    |          |              |
+----------+-------------------------------------------------------+--------------------+----------+--------------+
[XXXXXX@controller-0 ~(keystone_admin)]$


```


### Generate test events to go to MTCE Lab VCMP tools instance

```log
[XXXXXX@welktxefnce-h-pe1util-vm01 XXXXXX]$ IP=2607:f160:10:8803:ce:40a:0:e002
[XXXXXX@welktxefnce-h-pe1util-vm01 XXXXXX]$
[XXXXXX@welktxefnce-h-pe1util-vm01 XXXXXX]$ cat eventtest.json |jq .
{
  "EventID": "myEventId",
  "EventTimestamp": "2024-05-06T23:23:23Z",
  "Severity": "Critical",
  "Message": "This is a test event message for James ",
  "MessageId": "iLOResourceEvents.1.3.DrvArrLogDrvErasing",
  "MessageArgs": [
    "1",
    "slot 3"
  ],
  "OriginOfCondition": "/redfish/v1/Systems/1/Storage"
}
[XXXXXX@welktxefnce-h-pe1util-vm01 XXXXXX]$ curl -u XXXXXX:XXXXXX -i --insecure -H "Content-Type: application/json" --data "@eventtest.json" -X POST https://[$IP]/redfish/v1/EventService/Actions/EventService.SubmitTestEvent
^C
[XXXXXX@welktxefnce-h-pe1util-vm01 XXXXXX]$ curl -u XXXXXX:XXXXXX -i --insecure -H "Content-Type: application/json" --data "@eventtest.json" -X POST https://[$IP]/redfish/v1/EventService/Actions/EventService.SubmitTestEvent
HTTP/1.1 200 OK
Cache-Control: no-cache
Content-type: application/json; charset=utf-8
Date: Mon, 06 May 2024 18:13:33 GMT
ETag: W/"02C2D1BB"
OData-Version: 4.0
Transfer-Encoding: chunked
X-Content-Type-Options: nosniff
X-Frame-Options: sameorigin
X-XSS-Protection: 1; mode=block

{"error":{"code":"iLO.0.10.ExtendedInfo","message":"See @Message.ExtendedInfo for more information.","@Message.ExtendedInfo":[{"MessageId":"Base.1.18.Success"}]}}[XXXXXX@welktxefnh/v1/EventService/Actions/EventService.SubmitTestEventzon1 -i --insecure -H "Content-Type: application/json" --data "@eventtest.json" -X POST https://[$IP]/redfish
HTTP/1.1 200 OK
Cache-Control: no-cache
Content-type: application/json; charset=utf-8
Date: Mon, 06 May 2024 18:14:02 GMT
ETag: W/"02C2D1BB"
OData-Version: 4.0
Transfer-Encoding: chunked
X-Content-Type-Options: nosniff
X-Frame-Options: sameorigin
X-XSS-Protection: 1; mode=block

{"error":{"code":"iLO.0.10.ExtendedInfo","message":"See @Message.ExtendedInfo for more information.","@Message.ExtendedInfo":[{"MessageId":"Base.1.18.Success"}]}}[XXXXXX@welktxefnh/v1/EventService/Actions/EventService.SubmitTestEventzon1 -i --insecure -H "Content-Type: application/json" --data "@eventtest.json" -X POST https://[$IP]/redfish
HTTP/1.1 200 OK
Cache-Control: no-cache
Content-type: application/json; charset=utf-8
Date: Mon, 06 May 2024 18:14:03 GMT
ETag: W/"02C2D1BB"
OData-Version: 4.0
Transfer-Encoding: chunked
X-Content-Type-Options: nosniff
X-Frame-Options: sameorigin
X-XSS-Protection: 1; mode=block

{"error":{"code":"iLO.0.10.ExtendedInfo","message":"See @Message.ExtendedInfo for more information.","@Message.ExtendedInfo":[{"MessageId":"Base.1.18.Success"}]}}[XXXXXX@welktxefnh/v1/EventService/Actions/EventService.SubmitTestEventzon1 -i --insecure -H "Content-Type: application/json" --data "@eventtest.json" -X POST https://[$IP]/redfish
HTTP/1.1 200 OK
Cache-Control: no-cache
Content-type: application/json; charset=utf-8
Date: Mon, 06 May 2024 18:14:05 GMT
ETag: W/"02C2D1BB"
OData-Version: 4.0
Transfer-Encoding: chunked
X-Content-Type-Options: nosniff
X-Frame-Options: sameorigin
X-XSS-Protection: 1; mode=block

{"error":{"code":"iLO.0.10.ExtendedInfo","message":"See @Message.ExtendedInfo for more information.","@Message.ExtendedInfo":[{"MessageId":"Base.1.18.Success"}]}}[XXXXXX@welktxefnh/v1/EventService/Actions/EventService.SubmitTestEventzon1 -i --insecure -H "Content-Type: application/json" --data "@eventtest.json" -X POST https://[$IP]/redfish
HTTP/1.1 200 OK
Cache-Control: no-cache
Content-type: application/json; charset=utf-8
Date: Mon, 06 May 2024 18:14:06 GMT
ETag: W/"02C2D1BB"
OData-Version: 4.0
Transfer-Encoding: chunked
X-Content-Type-Options: nosniff
X-Frame-Options: sameorigin
X-XSS-Protection: 1; mode=block

{"error":{"code":"iLO.0.10.ExtendedInfo","message":"See @Message.ExtendedInfo for more information.","@Message.ExtendedInfo":[{"MessageId":"Base.1.18.Success"}]}}[XXXXXX@welktxefnh/v1/EventService/Actions/EventService.SubmitTestEventzon1 -i --insecure -H "Content-Type: application/json" --data "@eventtest.json" -X POST https://[$IP]/redfish
HTTP/1.1 200 OK
Cache-Control: no-cache
Content-type: application/json; charset=utf-8
Date: Mon, 06 May 2024 18:14:07 GMT
ETag: W/"02C2D1BB"
OData-Version: 4.0
Transfer-Encoding: chunked
X-Content-Type-Options: nosniff
X-Frame-Options: sameorigin
X-XSS-Protection: 1; mode=block

{"error":{"code":"iLO.0.10.ExtendedInfo","message":"See @Message.ExtendedInfo for more information.","@Message.ExtendedInfo":[{"MessageId":"Base.1.18.Success"}]}}[XXXXXX@welktxefnce-h-pe1util-vm01 XXXXXX]$
```
