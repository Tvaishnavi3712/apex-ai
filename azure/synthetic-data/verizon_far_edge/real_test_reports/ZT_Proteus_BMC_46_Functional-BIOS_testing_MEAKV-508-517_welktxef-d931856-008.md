# ZT Proteus .46 BMC firmware validation
# ZT Proteus BIOS .23
# 1/16/24 James Patchett

## Target Controller rchltxib-c000000-003
Controller-0 iLO 2607:f160:a:d02e:cd:fe0::8006 
Controller-1 iLO 2607:f160:a:d02e:cd:fe0::8007
Worker-0 iLO 2607:f160:a:d02e:cd:fe0::8008 
OAM 2607:f160:0:3049:cd:290:0:10

## Target Subcloud welktxef-d931856-008
OAM: 2607:f160:10:80b1:ce:40a:0:f408
BMC: 2607:f160:10:80b1:ce:40a:0:e008

ipmitool -I lanplus -U XXXXXX -P XXXXXX -H 2607:f160:10:80b1:ce:40a:0:e008 sol activate

## Subcloud welktxef-931856-rz-le2pts6-008

## MEAKV-508-517


```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ pwd
/home/XXXXXX/richardson/playbooks/vcp-fe-ib-automation
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ ansible-playbook --vault-password-file /tmp/vault-pass -i inventory-fe/rchltxfe-1.yml -e attributes_file=vars/proteus_redfish_attributes.yml -e target="welktxef-931856-rz-le2pts6-008" --tags bios ZT_Redfish_tests.yml

PLAY [welktxef-931856-rz-le2pts6-008] **********************************************************************************************************************
included: /home/XXXXXX/richardson/playbooks/vcp-fe-ib-automation/roles/redfish/attributes/tasks/check_attribute.yml for welktxef-931856-rz-le2pts6-008 => (item={'path': '/redfish/v1/Systems/Self/Bios', 'attribute': 'Attributes.SETUP006', 'expected_value': 'UEFI', 'match_type': 'regex'})
included: /home/XXXXXX/richardson/playbooks/vcp-fe-ib-automation/roles/redfish/attributes/tasks/check_attribute.yml for welktxef-931856-rz-le2pts6-008 => (item={'path': '/redfish/v1/Systems/Self/Bios', 'attribute': 'Attributes.SECB001', 'expected_value': 'Enabled', 'match_type': 'exact'})
included: /home/XXXXXX/richardson/playbooks/vcp-fe-ib-automation/roles/redfish/attributes/tasks/check_attribute.yml for welktxef-931856-rz-le2pts6-008 => (item={'path': '/redfish/v1/Systems/Self/Bios', 'attribute': 'Attributes.PMS00A', 'expected_value': 'Performance', 'match_type': 'exact'})
included: /home/XXXXXX/richardson/playbooks/vcp-fe-ib-automation/roles/redfish/attributes/tasks/check_attribute.yml for welktxef-931856-rz-le2pts6-008 => (item={'path': '/redfish/v1/Systems/Self/Bios', 'attribute': 'Attributes.PCIS007', 'expected_value': 'Enabled', 'match_type': 'exact'})
included: /home/XXXXXX/richardson/playbooks/vcp-fe-ib-automation/roles/redfish/attributes/tasks/check_attribute.yml for welktxef-931856-rz-le2pts6-008 => (item={'path': '/redfish/v1/Systems/Self/Bios', 'attribute': 'Attributes.IIOS1FE', 'expected_value': 'Enable', 'match_type': 'exact'})
included: /home/XXXXXX/richardson/playbooks/vcp-fe-ib-automation/roles/redfish/attributes/tasks/check_attribute.yml for welktxef-931856-rz-le2pts6-008 => (item={'path': '/redfish/v1/Systems/Self/Bios', 'attribute': 'Attributes.PMS007', 'expected_value': 'C0/C1 state', 'match_type': 'exact'})
included: /home/XXXXXX/richardson/playbooks/vcp-fe-ib-automation/roles/redfish/attributes/tasks/check_attribute.yml for welktxef-931856-rz-le2pts6-008 => (item={'path': '/redfish/v1/Systems/Self/Bios', 'attribute': 'Attributes.PMS002', 'expected_value': 'Enable', 'match_type': 'exact'})
included: /home/XXXXXX/richardson/playbooks/vcp-fe-ib-automation/roles/redfish/attributes/tasks/check_attribute.yml for welktxef-931856-rz-le2pts6-008 => (item={'path': '/redfish/v1/Systems/Self/Bios', 'attribute': 'Attributes.PRSS011', 'expected_value': 'Enable', 'match_type': 'exact'})
included: /home/XXXXXX/richardson/playbooks/vcp-fe-ib-automation/roles/redfish/attributes/tasks/check_attribute.yml for welktxef-931856-rz-le2pts6-008 => (item={'path': '/redfish/v1/Systems/Self/Bios', 'attribute': 'Attributes.PRSS01A', 'expected_value': 'Enable', 'match_type': 'exact'})
included: /home/XXXXXX/richardson/playbooks/vcp-fe-ib-automation/roles/redfish/attributes/tasks/check_attribute.yml for welktxef-931856-rz-le2pts6-008 => (item={'path': '/redfish/v1/Systems/Self/Bios', 'attribute': 'Attributes.NWSK000', 'expected_value': 'Enabled', 'match_type': 'exact'})
included: /home/XXXXXX/richardson/playbooks/vcp-fe-ib-automation/roles/redfish/attributes/tasks/check_attribute.yml for welktxef-931856-rz-le2pts6-008 => (item={'path': '/redfish/v1/Systems/Self/Bios', 'attribute': 'Attributes.PMS012', 'expected_value': 'Enable', 'match_type': 'exact'})
included: /home/XXXXXX/richardson/playbooks/vcp-fe-ib-automation/roles/redfish/attributes/tasks/check_attribute.yml for welktxef-931856-rz-le2pts6-008 => (item={'path': '/redfish/v1/Systems/Self/Bios', 'attribute': 'Attributes.MEMS00B', 'expected_value': '8-way Interleave', 'match_type': 'exact'})

TASK [redfish/attributes : what is currently verified] *****************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "msg": "Sending GET to /redfish/v1/Systems/Self/Bios and query the returned json for Attributes.SETUP006. Value shall be UEFI"
}

TASK [redfish/attributes : Checking Attributes.SETUP006 at /redfish/v1/Systems/Self/Bios] ******************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [redfish/attributes : what is currently verified] *****************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "msg": "Sending GET to /redfish/v1/Systems/Self/Bios and query the returned json for Attributes.SECB001. Value shall be Enabled"
}

TASK [redfish/attributes : Checking Attributes.SECB001 at /redfish/v1/Systems/Self/Bios] *******************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [redfish/attributes : what is currently verified] *****************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "msg": "Sending GET to /redfish/v1/Systems/Self/Bios and query the returned json for Attributes.PMS00A. Value shall be Performance"
}

TASK [redfish/attributes : Checking Attributes.PMS00A at /redfish/v1/Systems/Self/Bios] ********************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [redfish/attributes : what is currently verified] *****************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "msg": "Sending GET to /redfish/v1/Systems/Self/Bios and query the returned json for Attributes.PCIS007. Value shall be Enabled"
}

TASK [redfish/attributes : Checking Attributes.PCIS007 at /redfish/v1/Systems/Self/Bios] *******************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [redfish/attributes : what is currently verified] *****************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "msg": "Sending GET to /redfish/v1/Systems/Self/Bios and query the returned json for Attributes.IIOS1FE. Value shall be Enable"
}

TASK [redfish/attributes : Checking Attributes.IIOS1FE at /redfish/v1/Systems/Self/Bios] *******************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [redfish/attributes : what is currently verified] *****************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "msg": "Sending GET to /redfish/v1/Systems/Self/Bios and query the returned json for Attributes.PMS007. Value shall be C0/C1 state"
}

TASK [redfish/attributes : Checking Attributes.PMS007 at /redfish/v1/Systems/Self/Bios] ********************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [redfish/attributes : what is currently verified] *****************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "msg": "Sending GET to /redfish/v1/Systems/Self/Bios and query the returned json for Attributes.PMS002. Value shall be Enable"
}

TASK [redfish/attributes : Checking Attributes.PMS002 at /redfish/v1/Systems/Self/Bios] ********************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [redfish/attributes : what is currently verified] *****************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "msg": "Sending GET to /redfish/v1/Systems/Self/Bios and query the returned json for Attributes.PRSS011. Value shall be Enable"
}

TASK [redfish/attributes : Checking Attributes.PRSS011 at /redfish/v1/Systems/Self/Bios] *******************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [redfish/attributes : what is currently verified] *****************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "msg": "Sending GET to /redfish/v1/Systems/Self/Bios and query the returned json for Attributes.PRSS01A. Value shall be Enable"
}

TASK [redfish/attributes : Checking Attributes.PRSS01A at /redfish/v1/Systems/Self/Bios] *******************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [redfish/attributes : what is currently verified] *****************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "msg": "Sending GET to /redfish/v1/Systems/Self/Bios and query the returned json for Attributes.NWSK000. Value shall be Enabled"
}

TASK [redfish/attributes : Checking Attributes.NWSK000 at /redfish/v1/Systems/Self/Bios] *******************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [redfish/attributes : what is currently verified] *****************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "msg": "Sending GET to /redfish/v1/Systems/Self/Bios and query the returned json for Attributes.PMS012. Value shall be Enable"
}

TASK [redfish/attributes : Checking Attributes.PMS012 at /redfish/v1/Systems/Self/Bios] ********************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [redfish/attributes : FAIL if Attributes.PMS012 != Enable] ********************************************************************************************
fatal: [welktxef-931856-rz-le2pts6-008]: FAILED! => {"changed": false, "msg": "Attributes.PMS012 != Enable. It's Disable"}
...ignoring

TASK [redfish/attributes : what is currently verified] *****************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "msg": "Sending GET to /redfish/v1/Systems/Self/Bios and query the returned json for Attributes.MEMS00B. Value shall be 8-way Interleave"
}

TASK [redfish/attributes : Checking Attributes.MEMS00B at /redfish/v1/Systems/Self/Bios] *******************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [redfish/attributes : FAIL if Attributes.MEMS00B != 8-way Interleave] *********************************************************************************
fatal: [welktxef-931856-rz-le2pts6-008]: FAILED! => {"changed": false, "msg": "Attributes.MEMS00B != 8-way Interleave. It's 2-way Interleave"}
...ignoring

PLAY RECAP *************************************************************************************************************************************************
welktxef-931856-rz-le2pts6-008 : ok=38   changed=0    unreachable=0    failed=0    skipped=22   rescued=0    ignored=2

(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$

```

### Quick check using redfish calls to gather the individual settings:

```sh
IP=2607:f160:10:80b1:ce:40a:0:e008
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

```log
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ IP=2607:f160:10:80b1:ce:40a:0:e008
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[$IP]/redfish/v1/Systems/1/Bios|jq .Attributes.SETUP006
"CentOS,0x0001,true;UEFI: PXE IPv4 Intel(R) Ethernet Network Adapter E810-XXV-4,0x0002,true;UEFI: PXE IPv4 Intel(R) Ethernet Network Adapter E810-XXV-4,0x0003,true;UEFI: PXE IPv4 Intel(R) Ethernet Network Adapter E810-XXV-4,0x0004,true;UEFI: PXE IPv4 Intel(R) Ethernet Network Adapter E810-XXV-4,0x0005,true;UEFI: PXE IPv4 Intel(R) Ethernet Network Adapter E810-XXV-4,0x0006,true;UEFI: PXE IPv4 Intel(R) Ethernet Network Adapter E810-XXV-4,0x0007,true;UEFI: PXE IPv4 Intel(R) Ethernet Network Adapter E810-XXV-4,0x0008,true;UEFI: PXE IPv4 Intel(R) Ethernet Network Adapter E810-XXV-4,0x0009,true;UEFI: Built-in EFI Shell,0x000A,true;"
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[$IP]/redfish/v1/Systems/1/Bios|jq .Attributes.SECB001
"Enabled"
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[$IP]/redfish/v1/Systems/1/Bios|jq .Attributes.PMS00A
"Performance"
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[$IP]/redfish/v1/Systems/1/Bios|jq .Attributes.PCIS007
"Enabled"
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[$IP]/redfish/v1/Systems/1/Bios|jq .Attributes.IIOS1FE
"Enable"
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[$IP]/redfish/v1/Systems/1/Bios|jq .Attributes.PMS007
"C0/C1 state"
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[$IP]/redfish/v1/Systems/1/Bios|jq .Attributes.PMS002
"Enable"
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[$IP]/redfish/v1/Systems/1/Bios|jq .Attributes.PRSS011
"Enable"
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[$IP]/redfish/v1/Systems/1/Bios|jq .Attributes.PRSS01A
"Enable"
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[$IP]/redfish/v1/Systems/1/Bios|jq .Attributes.NWSK000
"Enabled"
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[$IP]/redfish/v1/Systems/1/Bios|jq .Attributes.PMS012
"Disable"
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[$IP]/redfish/v1/Systems/1/Bios|jq .Attributes.MEMS00B
"2-way Interleave"
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$
```
### NOTES on results

MEMS00B was set to default of 2-way interleave, at some point in the past Vz was trying to set 8-way interleave for performance, however samsung never tested it, and
we pulled that setting.  The testing script for proteus has not accounted for that change, will update the script for future testing.

End result is, BIOS settings are set correctly in BMC playbook, confirmed in these BIOS settings validation test.
