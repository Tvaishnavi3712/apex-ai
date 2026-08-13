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


```log
XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ export IP=2607:f160:10:9249:ce:40a:0:e016
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ curl -ks -u XXXXXX:XXXXXX https://[${IP}]/redfish/v1/EventService/Subscriptions/1 | jq . {
"@odata.context": "/redfish/v1/$metadata#EventDestination.EventDestination", "@odata.etag": "\"1679601517\"",
"@odata.id": "/redfish/v1/EventService/Subscriptions/1",
"@odata.type": "#EventDestination.v1_6_0.EventDestination",
"Context": "subscription",
"DeliveryRetryPolicy": "TerminateAfterRetries",
"Description": "Event Subscription",
"Destination": "https://vcp-fe-redfishevents.mon.vzwops.com:443/", "EventFormatType": "Event",
"Id": "1",
"Name": "Subscription 1",
"Protocol": "Redfish",
"Status": {
"Health": "OK", "HealthRollup": "OK", "State": "Enabled"
},
"SubordinateResources": false, "SubscriptionType": "RedfishEvent"
}
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ curl -ksn https://[$IP]/redfish/v1/Managers/Self/EthernetInterfaces/eth0 | jq .StaticNameServers [
"2607:f160:10:4409:ce:103:0:5", "2607:f160:10:4409:ce:103:0:6", "::"
]
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$
From <https://app.slack.com/client/T013AKGGZS6/D03SFG79T61>

[XXXXXX@welktxefnce-h-pe1util-vm01 bmc]$ curl --noproxy 2607:f160:10:9248:ce:40a:0:e005 -k -X POST https://[2607:f160:10:9248:ce:40a:0:e011]/redfish/v1/EventService/Actions/EventService.SubmitTestEvent -H "Content-Type: application/json" -d @alert-sample.json --user "vcmp:5983868167b9602a6439"
{"error":{"@Message.ExtendedInfo":[{"@odata.type":"#Message.v1_0_8.Message","Message":"The action /redfish/v1/EventService/Actions/EventService.SubmitTestEvent was submitted with the invalid parameter EventType.","MessageArgs":["/redfish/v1/EventService/Actions/EventService.SubmitTestEvent","EventType"],"MessageId":"Base.1.5.ActionParameterUnknown","RelatedProperties":["EventType"],"Resolution":"Correct the invalid parameter and resubmit the request if the operation failed.","Severity":"Warning"},{"@odata.type":"#Message.v1_0_8.Message","Message":"The action /redfish/v1/EventService/Actions/EventService.SubmitTestEvent was submitted with the invalid parameter Message.","MessageArgs":["/redfish/v1/EventService/Actions/EventService.SubmitTestEvent","Message"],"MessageId":"Base.1.5.ActionParameterUnknown","RelatedProperties":["Message"],"Resolution":"Correct the invalid parameter and resubmit the request if the operation failed.","Severity":"Warning"},{"@odata.type":"#Message.v1_0_8.Message","Message":"The TimeStamp value 2017-02-14T09:42:59+00:00 for the property EventTimestamp is in the past or morethan 2 mins to the BMC time.","MessageArgs":["2017-02-14T09:42:59+00:00","EventTimestamp"],"MessageId":"Ami.1.0.TimeStampInvalid","RelatedProperties":["#/EventTimestamp"],"Resolution":"Change the TimeStamp value same as DateTime property in the Manager Instance Resource.","Severity":"Warning"},{"@odata.type":"#Message.v1_0_8.Message","Message":"The value iBMCEvents.1.0.ResourceStatusChanged for the property MessageId is not in the list of acceptable values.","MessageArgs":["iBMCEvents.1.0.ResourceStatusChanged","MessageId"],"MessageId":"Base.1.5.PropertyValueNotInList","RelatedProperties":["#/MessageId"],"Resolution":"Choose a value from the enumeration list that the implementation can support and resubmit the request if the operation failed.","Severity":"Warning"},{"@odata.type":"#Message.v1_0_8.Message","Message":"The value {\"@odata.id\":\"\\/redfish\\/v1\"} for the parameter OriginOfCondition in the action EventService.SubmitTestEvent is of a different type than the parameter can accept.","MessageArgs":["{\"@odata.id\":\"\\/redfish\\/v1 \"}","OriginOfCondition","EventService.SubmitTestEvent"],"MessageId":"Base.1.5.ActionParameterValueTypeError","RelatedProperties":["#/OriginOfCondition"],"Resolution":"Correct the value for the parameter in the request body and resubmit the request if the operation failed.","Severity":"Warning"}],"code":"Base.1.5.GeneralError","message":"A general error has occurred. See Resolution for information on how to resolve the error."}}[XXXXXX@welktxefnce-h-pe1util-vm01 bmc]$

Delete subscription: curl --noproxy 2607:f160:10:9248:ce:40a:0:e011 -k -u $creds -X DELETE https://[2607:f160:10:9248:ce:40a:0:e011]/redfish/v1/EventService/Subscriptions/1|jq .

curl-k-u$creds-x""-XPOST https://[2607:f160:10:9248:ce:40a:0:e011]/redfish/v1/EventService/Subscriptions-H'Content-Type:application/json'-d'{"Context":"Zeus","Description":"Eventsubscrptionsdetails","Destination":"https://vcpme-
feocp-redfishalerts.mon.vzwops.com:443/", "EventFormatType": "Event", "Protocol": "Redfish", "SubscriptionType": "RedfishEvent"}'


[XXXXXX@welktxefnce-h-pe1util-vm01 tasks]$ history |grep bmc.yaml
  124  ansible-playbook -i inventory/welktxef-931887-rz-le0pts6-021.yaml --ask-vault-pass bmc.yaml 
  126  ansible-playbook -i inventory/welktxef-931887-rz-le0pts6-021.yaml --ask-vault-pass bmc.yaml 
  202  ansible-playbook --vault-password-file /tmp/vault-pass -i /home/XXXXXX/hqp_and_ops/bmc/inventory/welktxef-931855-rz-le2aks3-011.yaml bmc.yaml 
  204  ansible-playbook --vault-password-file /tmp/vault-pass -i /home/XXXXXX/hqp_and_ops/bmc/inventory/welktxef-931855-rz-le2aks3-011.yaml bmc.yaml 
  244  ansible-playbook --vault-password-file /tmp/vault-pass -i /home/XXXXXX/hqp_and_ops/bmc/inventory/welktxef-931855-rz-le2aks3-009.yaml bmc.yaml
  246  ansible-playbook --vault-password-file /tmp/vault-pass -i /home/XXXXXX/hqp_and_ops/bmc/inventory/welktxef-931855-rz-le2aks3-009.yaml bmc.yaml
 1033  history |grep bmc.yaml
[XXXXXX@welktxefnce-h-pe1util-vm01 tasks]$ 

```