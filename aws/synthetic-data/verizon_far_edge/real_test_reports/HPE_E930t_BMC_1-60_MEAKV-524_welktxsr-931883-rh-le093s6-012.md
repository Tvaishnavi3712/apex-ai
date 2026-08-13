# HPE ILO6 1.60 BIOS H11 v1.11
# HPE Sapphire Rapids E930t server
# 6/28/24 James Patchett - MTCE Lab VCPfe
# BMC Playbook MEAKV-1793

## welktxsr-931883-rh-le093s6-012
ILO:  2607:f160:10:8803:ce:40a:0:e001




### Generate test events to go to MTCE Lab VCMP tools instance

```log
(hpe_fw) [XXXXXX@welktxefnce-h-pe1util-vm01 XXXXXX]$ IP=2607:f160:10:8803:ce:40a:0:e001
(hpe_fw) [XXXXXX@welktxefnce-h-pe1util-vm01 XXXXXX]$
(hpe_fw) [XXXXXX@welktxefnce-h-pe1util-vm01 XXXXXX]$ cat eventtest.json
{

  "EventID": "myEventId",

  "EventTimestamp": "2023-02-13T14:49:20Z",

  "Severity": "Warning",

  "Message": "This is a test event message",

  "MessageId": "iLOResourceEvents.1.3.DrvArrLogDrvErasing",

  "MessageArgs": [ "1", "slot 3" ],

  "OriginOfCondition": "/redfish/v1/Systems/1/Storage"

}
(hpe_fw) [XXXXXX@welktxefnce-h-pe1util-vm01 XXXXXX]$


(hpe_fw) [XXXXXX@welktxefnce-h-pe1util-vm01 XXXXXX]$ curl -u XXXXXX:XXXXXX -i --insecure -H "Content-Type: application/json" --data "@eventtest.json" -X POST https://[$IP]/redfish/v1/EventService/Actions/EventService.SubmitTestEvent
HTTP/1.1 200 OK
Cache-Control: no-cache
Content-type: application/json; charset=utf-8
Date: Fri, 28 Jun 2024 20:02:49 GMT
ETag: W/"02C2D1BB"
OData-Version: 4.0
Transfer-Encoding: chunked
X-Content-Type-Options: nosniff
X-Frame-Options: sameorigin
X-XSS-Protection: 1; mode=block

{"error":{"code":"iLO.0.10.ExtendedInfo","message":"See @Message.ExtendedInfo for more information.","@Message.ExtendedInfo":[{"MessageId":"Base.1.18.Success"}]}}(hpe_fw) [XXXXXX@welktxefnce-h-pe1util-vm01 XXXXXX]$ curl -u XXXXXX:XXXXXX -i --insecure -H "Content-Type: ata "@eventtest.json" -X POST https://[$IP]/redfish/v1/EventService/Actions/EventService.SubmitTestEvent
HTTP/1.1 200 OK
Cache-Control: no-cache
Content-type: application/json; charset=utf-8
Date: Fri, 28 Jun 2024 20:02:52 GMT
ETag: W/"02C2D1BB"
OData-Version: 4.0
Transfer-Encoding: chunked
X-Content-Type-Options: nosniff
X-Frame-Options: sameorigin
X-XSS-Protection: 1; mode=block

{"error":{"code":"iLO.0.10.ExtendedInfo","message":"See @Message.ExtendedInfo for more information.","@Message.ExtendedInfo":[{"MessageId":"Base.1.18.Success"}]}}(hpe_fw) [XXXXXX@welktxefnce-h-pe1util-vm01 XXXXXX]$ curl -u XXXXXX:XXXXXX -i --insecure -H "Content-Type: ata "@eventtest.json" -X POST https://[$IP]/redfish/v1/EventService/Actions/EventService.SubmitTestEvent
HTTP/1.1 200 OK
Cache-Control: no-cache
Content-type: application/json; charset=utf-8
Date: Fri, 28 Jun 2024 20:02:53 GMT
ETag: W/"02C2D1BB"
OData-Version: 4.0
Transfer-Encoding: chunked
X-Content-Type-Options: nosniff
X-Frame-Options: sameorigin
X-XSS-Protection: 1; mode=block

{"error":{"code":"iLO.0.10.ExtendedInfo","message":"See @Message.ExtendedInfo for more information.","@Message.ExtendedInfo":[{"MessageId":"Base.1.18.Success"}]}}(hpe_fw) [XXXXXX@welktxefnce-h-pe1util-vm01 XXXXXX]$ curl -u XXXXXX:XXXXXX -i --insecure -H "Content-Type: ata "@eventtest.json" -X POST https://[$IP]/redfish/v1/EventService/Actions/EventService.SubmitTestEvent
HTTP/1.1 200 OK
Cache-Control: no-cache
Content-type: application/json; charset=utf-8
Date: Fri, 28 Jun 2024 20:02:54 GMT
ETag: W/"02C2D1BB"
OData-Version: 4.0
Transfer-Encoding: chunked
X-Content-Type-Options: nosniff
X-Frame-Options: sameorigin
X-XSS-Protection: 1; mode=block

{"error":{"code":"iLO.0.10.ExtendedInfo","message":"See @Message.ExtendedInfo for more information.","@Message.ExtendedInfo":[{"MessageId":"Base.1.18.Success"}]}}(hpe_fw) [XXXXXX@welktxefnce-h-pe1util-vm01 XXXXXX]$ curl -u XXXXXX:XXXXXX -i --insecure -H "Content-Type: ata "@eventtest.json" -X POST https://[$IP]/redfish/v1/EventService/Actions/EventService.SubmitTestEvent
HTTP/1.1 200 OK
Cache-Control: no-cache
Content-type: application/json; charset=utf-8
Date: Fri, 28 Jun 2024 20:02:55 GMT
ETag: W/"02C2D1BB"
OData-Version: 4.0
Transfer-Encoding: chunked
X-Content-Type-Options: nosniff
X-Frame-Options: sameorigin
X-XSS-Protection: 1; mode=block

{"error":{"code":"iLO.0.10.ExtendedInfo","message":"See @Message.ExtendedInfo for more information.","@Message.ExtendedInfo":[{"MessageId":"Base.1.18.Success"}]}}(hpe_fw) [XXXXXX@welktxefnce-h-pe1util-vm01 XXXXXX]$
```


### Validated with this URL to Web UI of Elastic of the MTCE Lab VCMP tools

https://kibana-rchlab.mon.vzwops.com/app/discover#/?_a=(columns:!(timestamp,hostname,message,log_type,level),filters:!(('$state':(store:appState),meta:(alias:!n,disabled:!f,index:'2ed36b1b-9ef9-4d4e-9640-79a712033a40',key:url.domain,negate:!f,params:(query:vcpme-rch-feocp-redfishalerts.mon.vzwops.com),type:phrase),query:(match_phrase:(url.domain:vcpme-rch-feocp-redfishalerts.mon.vzwops.com)))),index:'2ed36b1b-9ef9-4d4e-9640-79a712033a40',interval:auto,query:(language:kuery,query:''),sort:!(!('@timestamp',asc)))&_g=(filters:!(),refreshInterval:(pause:!t,value:60000),time:(from:now-5m,to:now))

### Will upload screen shots of host sending alerts to VMCP tools collector, there are many sent... 