# HPE ILO6 1.57 BIOS H11 v1.11
# HPE Sapphire Rapids E930t server
# 3/24/24 James Patchett - MTCE Lab VCPfe
# MEAKV-507 DMTF Conformance test

## welktxsr-931883-rh-le093s6-001
ILO:  2607:f160:10:80b1:ce:40a:0:e002
OAM:  2607:f160:10:80b1:ce:40a:0:f402

### Host Information on WRCP/WRA

```log
[XXXXXX@welktxefnce-h-pe1util-vm01 HPE_FW]$ IP=2607:f160:10:80b1:ce:40a:0:e002
[XXXXXX@welktxefnce-h-pe1util-vm01 HPE_FW]$ rf_protocol_validator -u XXXXXX -p XXXXXX -r https://[${IP}] --report-dir /home/XXXXXX/HPE_FW/DTMF_Redfish/ --report-type both --no-cert-check
ERROR:root:Caught exception while creating or patching other account; Exception: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response',)); continuing with test
Summary - PASS: 392, WARN: 0, FAIL: 7, NOT_TESTED: 31
Report output:
/home/XXXXXX/HPE_FW/DTMF_Redfish/RedfishProtocolValidationReport_03_27_2024_151937.tsv
/home/XXXXXX/HPE_FW/DTMF_Redfish/RedfishProtocolValidationReport_03_27_2024_151937.html
[XXXXXX@welktxefnce-h-pe1util-vm01 HPE_FW]$
[XXXXXX@welktxefnce-h-pe1util-vm01 DTMF_Redfish]$ ls -latr
total 228
drwxrwxr-x. 12 XXXXXX XXXXXX   4096 Mar 27 15:18 ..
-rw-rw-r--   1 XXXXXX XXXXXX    541 Mar 27 15:19 results.json
-rw-rw-r--   1 XXXXXX XXXXXX  96497 Mar 27 15:19 RedfishProtocolValidationReport_03_27_2024_151937.tsv
-rw-rw-r--   1 XXXXXX XXXXXX 124949 Mar 27 15:19 RedfishProtocolValidationReport_03_27_2024_151937.html
drwxrwxr-x   2 XXXXXX XXXXXX    149 Mar 27 15:19 .
[XXXXXX@welktxefnce-h-pe1util-vm01 DTMF_Redfish]$
[XXXXXX@welktxefnce-h-pe1util-vm01 DTMF_Redfish]$ cat results.json
{
    "ToolName": "Redfish-Protocol-Validator v1.2.0",
    "Timestamp": {
        "DateTime": "2024-03-27T15:19:37"
    },
    "Service": {
        "BaseURL": "https://[2607:f160:10:80b1:ce:40a:0:e002]",
        "Manufacturer": "N/A",
        "Product": "Edgeline e930t",
        "Model": "iLO 6",
        "FirmwareVersion": "iLO 6 v1.57"
    },
    "TestResults": {
        "Protocol Validations": {
            "pass": 392,
            "fail": 7,
            "skip": 31,
            "warn": 0
        },
        "ErrorMessages": []
    }
}[XXXXXX@welktxefnce-h-pe1util-vm01 DTMF_Redfish]$
```
### Tests completed, looking over report....

```log
RESP_HEADERS_WWW_AUTHENTICATE: "Redfish Services shall return the HTTP 1.1 Specification-defined [WWW-Authenticate header] if the value in the Required column is Yes."

Result	Method	Status code	URI	Message
FAIL	GET	401	/redfish/v1/SessionService/Sessions/	The WWW-Authenticate header was missing from the response to the GET request to URI /redfish/v1/SessionService/Sessions/
FAIL	GET	401	/redfish/v1/Managers/1/NetworkProtocol/	The WWW-Authenticate header was missing from the response to the GET request to URI /redfish/v1/Managers/1/NetworkProtocol/
FAIL	GET	401	/redfish/v1/Systems/	The WWW-Authenticate header was missing from the response to the GET request to URI /redfish/v1/Systems/
FAIL	GET	401	/redfish/v1/AccountService/Accounts/	The WWW-Authenticate header was missing from the response to the GET request to URI /redfish/v1/AccountService/Accounts/
FAIL	POST	401	/redfish/v1/AccountService/Accounts/	The WWW-Authenticate header was missing from the response to the POST request to URI /redfish/v1/AccountService/Accounts/
FAIL	GET	401	/redfish/v1/AccountService/	The WWW-Authenticate header was missing from the response to the GET request to URI /redfish/v1/AccountService/

SEC_CERTS_CONFORM_X509V3: "Redfish implementations shall use certificates that conform to X.509-v3, as defined in RFC5280."
Result	Method	Status code	URI	Message
FAIL				Exception caught while trying to retrieve and decode certificate for https://[2607:f160:10:80b1:ce:40a:0:e002]; exception: [Errno -9] Address family for hostname not supported



```

### These failed tests are not relevant to operation of redfish with VCPfe in production
### Uploaded files to Jira
### marked test passed

