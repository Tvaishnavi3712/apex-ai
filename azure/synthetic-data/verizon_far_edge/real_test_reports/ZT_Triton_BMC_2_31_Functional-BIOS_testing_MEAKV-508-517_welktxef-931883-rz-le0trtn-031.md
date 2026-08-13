# ZT Triton BMC 2.31 with BIOS 2.10
# Redfish Functional Testing MEAKV-508-517
# 10/17/25 James Patchett


## Target Subcloud welktxef-931883-rz-le0trtn-031
BMC 2607:f160:10:9249:ce:40a:0:e01f

## MEAKV-508-517

```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ ansible-playbook --vault-password-file vault_pass.txt -i inventory/zt-triton-james.yml -e attributes_file=vars/proteus_redfish_attributes.yml -e target="welktxef-931883-rz-le0trtn-031" --tags bios ZT_Redfish_tests.yml

PLAY [welktxef-931883-rz-le0trtn-031] ***************************************************************************************************************
included: /home/XXXXXX/playbooks/vcp-fe-ib-automation/roles/redfish/attributes/tasks/check_attribute.yml for welktxef-931883-rz-le0trtn-031 => (item={'path': '/redfish/v1/Systems/Self/Bios', 'attribute': 'Attributes.SETUP006', 'expected_value': 'UEFI', 'match_type': 'regex'})
included: /home/XXXXXX/playbooks/vcp-fe-ib-automation/roles/redfish/attributes/tasks/check_attribute.yml for welktxef-931883-rz-le0trtn-031 => (item={'path': '/redfish/v1/Systems/Self/Bios', 'attribute': 'Attributes.SECB001', 'expected_value': 'Enabled', 'match_type': 'exact'})
included: /home/XXXXXX/playbooks/vcp-fe-ib-automation/roles/redfish/attributes/tasks/check_attribute.yml for welktxef-931883-rz-le0trtn-031 => (item={'path': '/redfish/v1/Systems/Self/Bios', 'attribute': 'Attributes.PMS00A', 'expected_value': 'Performance', 'match_type': 'exact'})
included: /home/XXXXXX/playbooks/vcp-fe-ib-automation/roles/redfish/attributes/tasks/check_attribute.yml for welktxef-931883-rz-le0trtn-031 => (item={'path': '/redfish/v1/Systems/Self/Bios', 'attribute': 'Attributes.PCIS007', 'expected_value': 'Enabled', 'match_type': 'exact'})
included: /home/XXXXXX/playbooks/vcp-fe-ib-automation/roles/redfish/attributes/tasks/check_attribute.yml for welktxef-931883-rz-le0trtn-031 => (item={'path': '/redfish/v1/Systems/Self/Bios', 'attribute': 'Attributes.IIOS1FE', 'expected_value': 'Enable', 'match_type': 'exact'})
included: /home/XXXXXX/playbooks/vcp-fe-ib-automation/roles/redfish/attributes/tasks/check_attribute.yml for welktxef-931883-rz-le0trtn-031 => (item={'path': '/redfish/v1/Systems/Self/Bios', 'attribute': 'Attributes.PMS007', 'expected_value': 'C0/C1 state', 'match_type': 'exact'})
included: /home/XXXXXX/playbooks/vcp-fe-ib-automation/roles/redfish/attributes/tasks/check_attribute.yml for welktxef-931883-rz-le0trtn-031 => (item={'path': '/redfish/v1/Systems/Self/Bios', 'attribute': 'Attributes.PMS002', 'expected_value': 'Enable', 'match_type': 'exact'})
included: /home/XXXXXX/playbooks/vcp-fe-ib-automation/roles/redfish/attributes/tasks/check_attribute.yml for welktxef-931883-rz-le0trtn-031 => (item={'path': '/redfish/v1/Systems/Self/Bios', 'attribute': 'Attributes.PRSS011', 'expected_value': 'Enable', 'match_type': 'exact'})
included: /home/XXXXXX/playbooks/vcp-fe-ib-automation/roles/redfish/attributes/tasks/check_attribute.yml for welktxef-931883-rz-le0trtn-031 => (item={'path': '/redfish/v1/Systems/Self/Bios', 'attribute': 'Attributes.PRSS01A', 'expected_value': 'Enable', 'match_type': 'exact'})
included: /home/XXXXXX/playbooks/vcp-fe-ib-automation/roles/redfish/attributes/tasks/check_attribute.yml for welktxef-931883-rz-le0trtn-031 => (item={'path': '/redfish/v1/Systems/Self/Bios', 'attribute': 'Attributes.NWSK000', 'expected_value': 'Enabled', 'match_type': 'exact'})
included: /home/XXXXXX/playbooks/vcp-fe-ib-automation/roles/redfish/attributes/tasks/check_attribute.yml for welktxef-931883-rz-le0trtn-031 => (item={'path': '/redfish/v1/Systems/Self/Bios', 'attribute': 'Attributes.PMS012', 'expected_value': 'Enable', 'match_type': 'exact'})
included: /home/XXXXXX/playbooks/vcp-fe-ib-automation/roles/redfish/attributes/tasks/check_attribute.yml for welktxef-931883-rz-le0trtn-031 => (item={'path': '/redfish/v1/Systems/Self/Bios', 'attribute': 'Attributes.MEMS00B', 'expected_value': '8-way Interleave', 'match_type': 'exact'})

TASK [redfish/attributes : what is currently verified] **********************************************************************************************
ok: [welktxef-931883-rz-le0trtn-031] => {
    "msg": "Sending GET to /redfish/v1/Systems/Self/Bios and query the returned json for Attributes.SETUP006. Value shall be UEFI"
}

TASK [redfish/attributes : Checking Attributes.SETUP006 at /redfish/v1/Systems/Self/Bios] ***********************************************************
ok: [welktxef-931883-rz-le0trtn-031 -> localhost]

TASK [redfish/attributes : what is currently verified] **********************************************************************************************
ok: [welktxef-931883-rz-le0trtn-031] => {
    "msg": "Sending GET to /redfish/v1/Systems/Self/Bios and query the returned json for Attributes.SECB001. Value shall be Enabled"
}

TASK [redfish/attributes : Checking Attributes.SECB001 at /redfish/v1/Systems/Self/Bios] ************************************************************
ok: [welktxef-931883-rz-le0trtn-031 -> localhost]

TASK [redfish/attributes : what is currently verified] **********************************************************************************************
ok: [welktxef-931883-rz-le0trtn-031] => {
    "msg": "Sending GET to /redfish/v1/Systems/Self/Bios and query the returned json for Attributes.PMS00A. Value shall be Performance"
}

TASK [redfish/attributes : Checking Attributes.PMS00A at /redfish/v1/Systems/Self/Bios] *************************************************************
ok: [welktxef-931883-rz-le0trtn-031 -> localhost]

TASK [redfish/attributes : what is currently verified] **********************************************************************************************
ok: [welktxef-931883-rz-le0trtn-031] => {
    "msg": "Sending GET to /redfish/v1/Systems/Self/Bios and query the returned json for Attributes.PCIS007. Value shall be Enabled"
}

TASK [redfish/attributes : Checking Attributes.PCIS007 at /redfish/v1/Systems/Self/Bios] ************************************************************
ok: [welktxef-931883-rz-le0trtn-031 -> localhost]

TASK [redfish/attributes : what is currently verified] **********************************************************************************************
ok: [welktxef-931883-rz-le0trtn-031] => {
    "msg": "Sending GET to /redfish/v1/Systems/Self/Bios and query the returned json for Attributes.IIOS1FE. Value shall be Enable"
}

TASK [redfish/attributes : Checking Attributes.IIOS1FE at /redfish/v1/Systems/Self/Bios] ************************************************************
ok: [welktxef-931883-rz-le0trtn-031 -> localhost]

TASK [redfish/attributes : what is currently verified] **********************************************************************************************
ok: [welktxef-931883-rz-le0trtn-031] => {
    "msg": "Sending GET to /redfish/v1/Systems/Self/Bios and query the returned json for Attributes.PMS007. Value shall be C0/C1 state"
}

TASK [redfish/attributes : Checking Attributes.PMS007 at /redfish/v1/Systems/Self/Bios] *************************************************************
ok: [welktxef-931883-rz-le0trtn-031 -> localhost]

TASK [redfish/attributes : what is currently verified] **********************************************************************************************
ok: [welktxef-931883-rz-le0trtn-031] => {
    "msg": "Sending GET to /redfish/v1/Systems/Self/Bios and query the returned json for Attributes.PMS002. Value shall be Enable"
}

TASK [redfish/attributes : Checking Attributes.PMS002 at /redfish/v1/Systems/Self/Bios] *************************************************************
ok: [welktxef-931883-rz-le0trtn-031 -> localhost]

TASK [redfish/attributes : what is currently verified] **********************************************************************************************
ok: [welktxef-931883-rz-le0trtn-031] => {
    "msg": "Sending GET to /redfish/v1/Systems/Self/Bios and query the returned json for Attributes.PRSS011. Value shall be Enable"
}

TASK [redfish/attributes : Checking Attributes.PRSS011 at /redfish/v1/Systems/Self/Bios] ************************************************************
ok: [welktxef-931883-rz-le0trtn-031 -> localhost]

TASK [redfish/attributes : what is currently verified] **********************************************************************************************
ok: [welktxef-931883-rz-le0trtn-031] => {
    "msg": "Sending GET to /redfish/v1/Systems/Self/Bios and query the returned json for Attributes.PRSS01A. Value shall be Enable"
}

TASK [redfish/attributes : Checking Attributes.PRSS01A at /redfish/v1/Systems/Self/Bios] ************************************************************
ok: [welktxef-931883-rz-le0trtn-031 -> localhost]

TASK [redfish/attributes : what is currently verified] **********************************************************************************************
ok: [welktxef-931883-rz-le0trtn-031] => {
    "msg": "Sending GET to /redfish/v1/Systems/Self/Bios and query the returned json for Attributes.NWSK000. Value shall be Enabled"
}

TASK [redfish/attributes : Checking Attributes.NWSK000 at /redfish/v1/Systems/Self/Bios] ************************************************************
ok: [welktxef-931883-rz-le0trtn-031 -> localhost]

TASK [redfish/attributes : what is currently verified] **********************************************************************************************
ok: [welktxef-931883-rz-le0trtn-031] => {
    "msg": "Sending GET to /redfish/v1/Systems/Self/Bios and query the returned json for Attributes.PMS012. Value shall be Enable"
}

TASK [redfish/attributes : Checking Attributes.PMS012 at /redfish/v1/Systems/Self/Bios] *************************************************************
ok: [welktxef-931883-rz-le0trtn-031 -> localhost]

TASK [redfish/attributes : FAIL if Attributes.PMS012 != Enable] *************************************************************************************
fatal: [welktxef-931883-rz-le0trtn-031]: FAILED! => {"changed": false, "msg": "Attributes.PMS012 != Enable. It's "}
...ignoring

TASK [redfish/attributes : what is currently verified] **********************************************************************************************
ok: [welktxef-931883-rz-le0trtn-031] => {
    "msg": "Sending GET to /redfish/v1/Systems/Self/Bios and query the returned json for Attributes.MEMS00B. Value shall be 8-way Interleave"
}

TASK [redfish/attributes : Checking Attributes.MEMS00B at /redfish/v1/Systems/Self/Bios] ************************************************************
ok: [welktxef-931883-rz-le0trtn-031 -> localhost]

TASK [redfish/attributes : FAIL if Attributes.MEMS00B != 8-way Interleave] **************************************************************************
fatal: [welktxef-931883-rz-le0trtn-031]: FAILED! => {"changed": false, "msg": "Attributes.MEMS00B != 8-way Interleave. It's Auto"}
...ignoring

PLAY RECAP ******************************************************************************************************************************************
welktxef-931883-rz-le0trtn-031 : ok=38   changed=0    unreachable=0    failed=0    skipped=22   rescued=0    ignored=2

(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$
```

### Quick check using redfish calls to gather the individual settings:

```sh
IP=2607:f160:10:9249:ce:40a:0:e01f
curl -gsk -u XXXXXX:XXXXXX -X GET https://[$IP]/redfish/v1/Systems/1/Bios|jq .Attributes.SETUP006
curl -gsk -u XXXXXX:XXXXXX -X GET https://[$IP]/redfish/v1/Systems/1/Bios|jq .Attributes.SECB001
curl -gsk -u XXXXXX:XXXXXX -X GET https://[$IP]/redfish/v1/Systems/1/Bios|jq .Attributes.PMS00A
curl -gsk -u XXXXXX:XXXXXX -X GET https://[$IP]/redfish/v1/Systems/1/Bios|jq .Attributes.PCIS007
curl -gsk -u XXXXXX:XXXXXX -X GET https://[$IP]/redfish/v1/Systems/1/Bios|jq .Attributes.IIOS1FE
curl -gsk -u XXXXXX:XXXXXX -X GET https://[$IP]/redfish/v1/Systems/1/Bios|jq .Attributes.PMS007
curl -gsk -u XXXXXX:XXXXXX -X GET https://[$IP]/redfish/v1/Systems/1/Bios|jq .Attributes.PMS002
curl -gsk -u XXXXXX:XXXXXX -X GET https://[$IP]/redfish/v1/Systems/1/Bios|jq .Attributes.PRSS011
curl -gsk -u XXXXXX:XXXXXX -X GET https://[$IP]/redfish/v1/Systems/1/Bios|jq .Attributes.PRSS01A
curl -gsk -u XXXXXX:XXXXXX -X GET https://[$IP]/redfish/v1/Systems/1/Bios|jq .Attributes.NWSK000
curl -gsk -u XXXXXX:XXXXXX -X GET https://[$IP]/redfish/v1/Systems/1/Bios|jq .Attributes.PMS012
curl -gsk -u XXXXXX:XXXXXX -X GET https://[$IP]/redfish/v1/Systems/1/Bios|jq .Attributes.MEMS00B
```


```sh
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ IP=2607:f160:10:9249:ce:40a:0:e01f
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[$IP]/redfish/v1/Systems/1/Bios|jq .Attributes.SETUP006
"starlingx,0x0000,true;UEFI: PXE IP4 Intel(R) Ethernet Network Adapter OCP XXV710-2,0x0002,true;UEFI: PXE IP4 Intel(R) Ethernet Network Adapter XXV710,0x0003,true;UEFI: Built-in EFI Shell,0x0004,true;"
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[$IP]/redfish/v1/Systems/1/Bios|jq .Attributes.SECB001
"Enabled"
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[$IP]/redfish/v1/Systems/1/Bios|jq .Attributes.PMS00A
"Performance"
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[$IP]/redfish/v1/Systems/1/Bios|jq .Attributes.PCIS007
"Enabled"
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[$IP]/redfish/v1/Systems/1/Bios|jq .Attributes.IIOS1FE
"Enable"
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[$IP]/redfish/v1/Systems/1/Bios|jq .Attributes.PMS007
"C0/C1 state"
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[$IP]/redfish/v1/Systems/1/Bios|jq .Attributes.PMS002
"Enable"
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[$IP]/redfish/v1/Systems/1/Bios|jq .Attributes.PRSS011
"Enable"
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[$IP]/redfish/v1/Systems/1/Bios|jq .Attributes.PRSS01A
"Enable"
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[$IP]/redfish/v1/Systems/1/Bios|jq .Attributes.NWSK000
"Enabled"
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[$IP]/redfish/v1/Systems/1/Bios|jq .Attributes.PMS012
null
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[$IP]/redfish/v1/Systems/1/Bios|jq .Attributes.MEMS00B
"Auto"
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$

```

### results are what we expected 
### Pass