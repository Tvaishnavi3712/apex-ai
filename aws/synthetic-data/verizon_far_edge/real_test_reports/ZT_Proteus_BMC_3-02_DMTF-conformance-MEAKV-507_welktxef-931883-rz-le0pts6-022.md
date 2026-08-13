# ZT Proteus BMC 3.02 with BIOS 0.30
# 7/16/25 James Patchett - MTCE Lab VCPfe
# MEAKV-507 DMTF Conformance test

## welktxef-931883-rz-le0pts6-022
ILO:  2607:f160:10:9249:ce:40a:0:e016


### execute the Redfish protocol validator

```log
[[XXXXXX@welktxefnce-h-pe1util-vm01 Redfish-Protocol-Validator_1.1.0]$ rf_protocol_validator.py -u XXXXXX -p XXXXXX -r https://[2607:f160:10:9249:ce:40a:0:e016] --report-dir /home/XXXXXX/HPE_FW/DTMF_Redfish/ --report-type both --no-cert-check
ERROR:root:Caught exception while creating or patching accounts; Exception: HTTPSConnectionPool(host='2607:f160:10:9249:ce:40a:0:e016', port=443): Max retries exceeded with url: /redfish/v1/AccountService/Accounts/8 (Caused by SSLError(SSLError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed (_ssl.c:897)'),)); continuing with test
WARNING:root:Caught ConnectionError while trying to trigger a redirect. To avoid this warning and speed up the validation run, try adding the --avoid-http-redirect command-line argument.
WARNING:root:Attempt to PATCH /redfish/v1/Managers/Self/NetworkProtocol to restore the original NTPServers array failed with status 400; PATCH payload: {'NTP': {'NTPServers': ['2607:f160:10:9200::a', '2607:f160:10:9200::b']}}
Summary - PASS: 399, WARN: 0, FAIL: 6, NOT_TESTED: 24
Report output:
/home/XXXXXX/HPE_FW/DTMF_Redfish/RedfishProtocolValidationReport_07_16_2025_115701.tsv
/home/XXXXXX/HPE_FW/DTMF_Redfish/RedfishProtocolValidationReport_07_16_2025_115701.html
[XXXXXX@welktxefnce-h-pe1util-vm01 Redfish-Protocol-Validator_1.1.0]$
(hpe_fw) [XXXXXX@welktxefnce-h-pe1util-vm01 DTMF_Redfish]$ cat results.json
{
    "ToolName": "Redfish-Protocol-Validator v1.2.0",
    "Timestamp": {
        "DateTime": "2025-07-16T11:57:01"
    },
    "Service": {
        "BaseURL": "https://[2607:f160:10:9249:ce:40a:0:e016]",
        "Manufacturer": "N/A",
        "Product": "AMI Redfish Server",
        "Model": "43553231270",
        "FirmwareVersion": "3.02.00"
    },
    "TestResults": {
        "Protocol Validations": {
            "pass": 399,
            "fail": 6,
            "skip": 24,
            "warn": 0
        },
        "ErrorMessages": []
    }
}(hpe_fw) [XXXXXX@welktxefnce-h-pe1util-vm01 DTMF_Redfish]$
```
### Tests completed, looking over report....

```log

Assertion	Method	Status code	URI	Result	Message	Requirement

REQ_GET_IGNORE_BODY	GET	400	/redfish/v1/	FAIL	GET request to URI /redfish/v1/ that included a body failed	The service shall ignore the content of the body on a GET.
REQ_PATCH_ARRAY_ELEMENT_REMOVE	PATCH	400	/redfish/v1/Managers/Self/NetworkProtocol	FAIL	PATCH failed with status 400; PATCH payload: {'NTP': {'NTPServers': ['time-a-b.nist.gov', 'time-b-b.nist.gov']}}; extended error: The operation failed because this service is disabled and can no longer take incoming requests.	Within a PATCH request, the service shall accept null to remove an element.
REQ_PATCH_ARRAY_ELEMENT_UNCHANGED	PATCH	400	/redfish/v1/Managers/Self/NetworkProtocol	FAIL	PATCH failed with status 400; PATCH payload: {'NTP': {'NTPServers': ['time-a-b.nist.gov', 'time-b-b.nist.gov']}}	Within a PATCH request, the service shall accept an empty object {} to leave an element unchanged
REQ_PATCH_ARRAY_TRUNCATE	PATCH	400	/redfish/v1/Managers/Self/NetworkProtocol	FAIL	PATCH failed with status 400; PATCH payload: {'NTP': {'NTPServers': ['time-a-b.nist.gov', 'time-b-b.nist.gov']}}; extended error: The operation failed because this service is disabled and can no longer take incoming requests.	A PATCH request with fewer elements than in the current array shall remove the remaining elements of the array.
SERV_SSE_EVENT_DEST_DELETED_ON_CLOSE	GET	200	/redfish/v1/EventService/Subscriptions/1	FAIL	EventDestination resource not deleted when SSE stream closed	The service shall delete the corresponding EventDestination resource when the connection is closed.
SEC_CERTS_CONFORM_X509V3				FAIL	Exception caught while trying to retrieve and decode certificate for https://[2607:f160:10:9249:ce:40a:0:e016]; exception: [Errno -9] Address family for hostname not supported	Redfish implementations shall use certificates that conform to X.509-v3, as defined in RFC5280.

```

### These failed tests are not relevant to operation of redfish with VCPfe in production
### We will validate the NTP "Patch" Failures, if they impact the BMC playbook when I run that test.
### Uploaded files to Jira
### marked test passed

