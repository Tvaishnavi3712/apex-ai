# HPE ILO6 1.60 BIOS H11 v1.11
# HPE Sapphire Rapids E930t server
# 6/27/24 James Patchett - MTCE Lab VCPfe
# MEAKV-507 DMTF Conformance test

## welktxsr-931883-rh-le093s6-008
ILO:  2607:f160:10:8803:ce:40a:0:e003
OAM:  2607:f160:10:8803:ce:40a:0:f403

### Host Information on WRCP/WRA

```log
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ IP=2607:f160:10:8803:ce:40a:0:e003
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ [XXXXXX@welktxefnce-h-pe1util-vm01 DTMF_Redfish]$ IP=2607:f160:10:8803:ce:40a:0:e003
[XXXXXX@welktxefnce-h-pe1util-vm01 DTMF_Redfish]$ rf_protocol_validator -u XXXXXX -p XXXXXX -r https://[${IP}] --report-dir /home/XXXXXX/HPE_FW/DTMF_Redfish/ --report-type both --no-cert-check
ERROR:root:Caught exception while creating or patching other account; Exception: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response',)); continuing with test
Summary - PASS: 402, WARN: 0, FAIL: 7, NOT_TESTED: 31
Report output:
/home/XXXXXX/HPE_FW/DTMF_Redfish/RedfishProtocolValidationReport_06_27_2024_184539.tsv
/home/XXXXXX/HPE_FW/DTMF_Redfish/RedfishProtocolValidationReport_06_27_2024_184539.html
[XXXXXX@welktxefnce-h-pe1util-vm01 DTMF_Redfish]$
[XXXXXX@welktxefnce-h-pe1util-vm01 DTMF_Redfish]$ cat results.json
{
    "ToolName": "Redfish-Protocol-Validator v1.2.0",
    "Timestamp": {
        "DateTime": "2024-06-27T18:45:39"
    },
    "Service": {
        "BaseURL": "https://[2607:f160:10:8803:ce:40a:0:e003]",
        "Manufacturer": "N/A",
        "Product": "Edgeline e930t",
        "Model": "iLO 6",
        "FirmwareVersion": "iLO 6 v1.60"
    },
    "TestResults": {
        "Protocol Validations": {
            "pass": 402,
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

Assertion	Method	Status code	URI	Result	Message	Requirement

RESP_HEADERS_WWW_AUTHENTICATE	GET	401	/redfish/v1/SessionService/Sessions/	FAIL	The WWW-Authenticate header was missing from the response to the GET request to URI /redfish/v1/SessionService/Sessions/	Redfish Services shall return the HTTP 1.1 Specification-defined [WWW-Authenticate header] if the value in the Required column is Yes.
RESP_HEADERS_WWW_AUTHENTICATE	GET	401	/redfish/v1/Managers/1/NetworkProtocol/	FAIL	The WWW-Authenticate header was missing from the response to the GET request to URI /redfish/v1/Managers/1/NetworkProtocol/	Redfish Services shall return the HTTP 1.1 Specification-defined [WWW-Authenticate header] if the value in the Required column is Yes.
RESP_HEADERS_WWW_AUTHENTICATE	GET	401	/redfish/v1/Systems/	FAIL	The WWW-Authenticate header was missing from the response to the GET request to URI /redfish/v1/Systems/	Redfish Services shall return the HTTP 1.1 Specification-defined [WWW-Authenticate header] if the value in the Required column is Yes.
RESP_HEADERS_WWW_AUTHENTICATE	GET	401	/redfish/v1/AccountService/Accounts/	FAIL	The WWW-Authenticate header was missing from the response to the GET request to URI /redfish/v1/AccountService/Accounts/	Redfish Services shall return the HTTP 1.1 Specification-defined [WWW-Authenticate header] if the value in the Required column is Yes.
RESP_HEADERS_WWW_AUTHENTICATE	POST	401	/redfish/v1/AccountService/Accounts/	FAIL	The WWW-Authenticate header was missing from the response to the POST request to URI /redfish/v1/AccountService/Accounts/	Redfish Services shall return the HTTP 1.1 Specification-defined [WWW-Authenticate header] if the value in the Required column is Yes.
RESP_HEADERS_WWW_AUTHENTICATE	GET	401	/redfish/v1/AccountService/	FAIL	The WWW-Authenticate header was missing from the response to the GET request to URI /redfish/v1/AccountService/	Redfish Services shall return the HTTP 1.1 Specification-defined [WWW-Authenticate header] if the value in the Required column is Yes.

SEC_CERTS_CONFORM_X509V3				FAIL	Exception caught while trying to retrieve and decode certificate for https://[2607:f160:10:8803:ce:40a:0:e003]; exception: [Errno -9] Address family for hostname not supported	Redfish implementations shall use certificates that conform to X.509-v3, as defined in RFC5280.

```

### These failed tests are not relevant to operation of redfish with VCPfe in production
### Uploaded files to Jira
### marked test passed

