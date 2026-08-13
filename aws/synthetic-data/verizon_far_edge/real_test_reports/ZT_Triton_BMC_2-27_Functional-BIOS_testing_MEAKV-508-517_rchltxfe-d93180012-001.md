# ZT Triton 2.27 BMC firmware validation
# BIOS Functional Testing MEAKV-508-517
# 11/29/23 James Patchett

## Target Controller rchltxib-c000000-003 CR-3 (Richardson infrastructure System)
OAM: 2607:f160:0:3049:cd:290:0:10

## Subcloud rchltxfe-d93180012-001 (VCP-fe Infrastructure)
OAM: 2607:f160:10:9073:ce:40a:0:f400
ILO: 2607:f160:10:9073:ce:406:0:1000

ipmitool -I lanplus -U XXXXXX -P XXXXXX -H 2607:f160:10:9073:ce:406:0:1000 sol activate

## Subcloud rchltxfe-d93180012-001
## General info before we start

```log
controller-0:~$ source /etc/platform/openrc
[XXXXXX@controller-0 ~(keystone_admin)]$ system show
+------------------------+--------------------------------------+
| Property               | Value                                |
+------------------------+--------------------------------------+
| contact                | None                                 |
| created_at             | 2023-07-17T16:16:41.669508+00:00     |
| description            | None                                 |
| distributed_cloud_role | subcloud                             |
| https_enabled          | True                                 |
| latitude               | None                                 |
| location               | None                                 |
| longitude              | None                                 |
| name                   | rchltxfe-d93180012-001               |
| region_name            | rchltxfe-d93180012-001               |
| sdn_enabled            | False                                |
| security_feature       | spectre_meltdown_v1                  |
| service_project_name   | services                             |
| shared_services        | []                                   |
| software_version       | 21.12                                |
| system_mode            | simplex                              |
| system_type            | All-in-one                           |
| timezone               | UTC                                  |
| updated_at             | 2023-07-17T17:17:57.144973+00:00     |
| uuid                   | bf8885f0-583a-45fa-bd18-1cab57371a45 |
| vswitch_type           | none                                 |
+------------------------+--------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ system oam-show
+----------------+---------------------------------------+
| Property       | Value                                 |
+----------------+---------------------------------------+
| created_at     | 2023-07-17T16:18:28.746601+00:00      |
| isystem_uuid   | bf8885f0-583a-45fa-bd18-1cab57371a45  |
| oam_end_ip     | 2607:f160:10:9073:ffff:ffff:ffff:fffe |
| oam_gateway_ip | 2607:f160:10:9073:ce:28::             |
| oam_ip         | 2607:f160:10:9073:ce:40a:0:f400       |
| oam_start_ip   | 2607:f160:10:9073::1                  |
| oam_subnet     | 2607:f160:10:9073::/64                |
| updated_at     | None                                  |
| uuid           | 30fca5fe-860d-4d16-ad07-d2b356b994c8  |
+----------------+---------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ fm alarm-list

[XXXXXX@controller-0 ~(keystone_admin)]$ sw-patch query
      Patch ID         RR  Release  Patch State
=====================  ==  =======  ===========
WRCP_21.12_PATCH_0001  Y    21.12    Committed
WRCP_21.12_PATCH_0002  Y    21.12    Committed
WRCP_21.12_PATCH_0003  Y    21.12    Committed
WRCP_21.12_PATCH_0004  Y    21.12    Committed
WRCP_21.12_PATCH_0005  Y    21.12    Committed
WRCP_21.12_PATCH_0006  Y    21.12    Committed
WRCP_21.12_PATCH_0007  Y    21.12    Committed
WRCP_21.12_PATCH_0008  Y    21.12    Committed
WRCP_21.12_PATCH_0009  Y    21.12    Committed
WRCP_21.12_PATCH_0010  N    21.12    Committed

[XXXXXX@controller-0 ~(keystone_admin)]$ system application-list
+--------------------------+----------+-----------------------------------+----------------------------------------+----------+-----------+
| application              | version  | manifest name                     | manifest file                          | status   | progress  |
+--------------------------+----------+-----------------------------------+----------------------------------------+----------+-----------+
| cert-manager             | 21.12-28 | cert-manager-manifest             | certmanager-manifest.yaml              | applied  | completed |
| metrics-server           | 21.12-9  | metrics-server-manifest           | metrics-server_manifest.yaml           | applied  | completed |
| nginx-ingress-controller | 21.12-18 | nginx-ingress-controller-manifest | nginx_ingress_controller_manifest.yaml | applied  | completed |
| oidc-auth-apps           | 21.12-61 | oidc-auth-manifest                | manifest.yaml                          | applied  | completed |
| platform-integ-apps      | 21.12-46 | platform-integration-manifest     | manifest.yaml                          | applied  | completed |
| rook-ceph-apps           | 1.0-14   | rook-ceph-manifest                | manifest.yaml                          | uploaded | completed |
+--------------------------+----------+-----------------------------------+----------------------------------------+----------+-----------+
[XXXXXX@controller-0 ~(keystone_admin)]$
```

## MEAKV-508-517

## inventory file for subcloud
```log
[XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ cat inventory/zt-triton.yml
---
all:
  children:
    wrcp:
      children:
        central:
          hosts:
            rchltxfe-000000-nh-le1dlv2-003.faredge.vzwops.com:
        distributed:
          hosts:
            rchltxfb-93180012-rz-le0trtn-00.faredge.vzwops.com:
              ansible_host: 2607:f160:10:9073:ce:40a:0:f400
              bmc_node_0_address: 2607:f160:10:9073:ce:406:0:1000
              bmc_username: "XXXXXX"
              bmc_password: "XXXXXX"
[XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$

```

```log
[XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ ansible-playbook --vault-password-file /tmp/vault-pass -i inventory/zt-triton.yml -e attributes_file=vars/triton_redfish_attributes.yml --tags bios ZT_Redfish_tests.yml

PLAY [distributed] *************************************************************************************************************************
included: /home/XXXXXX/richardson/playbooks/vcp-fe-ib-automation/roles/redfish/attributes/tasks/check_attribute.yml for rchltxfb-93180012-rz-le0trtn-00.faredge.vzwops.com
included: /home/XXXXXX/richardson/playbooks/vcp-fe-ib-automation/roles/redfish/attributes/tasks/check_attribute.yml for rchltxfb-93180012-rz-le0trtn-00.faredge.vzwops.com
included: /home/XXXXXX/richardson/playbooks/vcp-fe-ib-automation/roles/redfish/attributes/tasks/check_attribute.yml for rchltxfb-93180012-rz-le0trtn-00.faredge.vzwops.com
included: /home/XXXXXX/richardson/playbooks/vcp-fe-ib-automation/roles/redfish/attributes/tasks/check_attribute.yml for rchltxfb-93180012-rz-le0trtn-00.faredge.vzwops.com
included: /home/XXXXXX/richardson/playbooks/vcp-fe-ib-automation/roles/redfish/attributes/tasks/check_attribute.yml for rchltxfb-93180012-rz-le0trtn-00.faredge.vzwops.com
included: /home/XXXXXX/richardson/playbooks/vcp-fe-ib-automation/roles/redfish/attributes/tasks/check_attribute.yml for rchltxfb-93180012-rz-le0trtn-00.faredge.vzwops.com
included: /home/XXXXXX/richardson/playbooks/vcp-fe-ib-automation/roles/redfish/attributes/tasks/check_attribute.yml for rchltxfb-93180012-rz-le0trtn-00.faredge.vzwops.com
included: /home/XXXXXX/richardson/playbooks/vcp-fe-ib-automation/roles/redfish/attributes/tasks/check_attribute.yml for rchltxfb-93180012-rz-le0trtn-00.faredge.vzwops.com
included: /home/XXXXXX/richardson/playbooks/vcp-fe-ib-automation/roles/redfish/attributes/tasks/check_attribute.yml for rchltxfb-93180012-rz-le0trtn-00.faredge.vzwops.com
included: /home/XXXXXX/richardson/playbooks/vcp-fe-ib-automation/roles/redfish/attributes/tasks/check_attribute.yml for rchltxfb-93180012-rz-le0trtn-00.faredge.vzwops.com

TASK [redfish/attributes : what is currently verified] *************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-00.faredge.vzwops.com] => {
    "msg": "Sending GET to /redfish/v1/Systems/Self/Bios and query the returned json for Attributes.SETUP006. Value shall be UEFI"
}

TASK [redfish/attributes : Checking Attributes.SETUP006 at /redfish/v1/Systems/Self/Bios] **************************************************
ok: [rchltxfb-93180012-rz-le0trtn-00.faredge.vzwops.com -> localhost]

TASK [redfish/attributes : what is currently verified] *************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-00.faredge.vzwops.com] => {
    "msg": "Sending GET to /redfish/v1/Systems/Self/Bios and query the returned json for Attributes.SECB001. Value shall be Enabled"
}

TASK [redfish/attributes : Checking Attributes.SECB001 at /redfish/v1/Systems/Self/Bios] ***************************************************
ok: [rchltxfb-93180012-rz-le0trtn-00.faredge.vzwops.com -> localhost]

TASK [redfish/attributes : what is currently verified] *************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-00.faredge.vzwops.com] => {
    "msg": "Sending GET to /redfish/v1/Systems/Self/Bios and query the returned json for Attributes.PMS00A. Value shall be Performance"
}

TASK [redfish/attributes : Checking Attributes.PMS00A at /redfish/v1/Systems/Self/Bios] ****************************************************
ok: [rchltxfb-93180012-rz-le0trtn-00.faredge.vzwops.com -> localhost]

TASK [redfish/attributes : what is currently verified] *************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-00.faredge.vzwops.com] => {
    "msg": "Sending GET to /redfish/v1/Systems/Self/Bios and query the returned json for Attributes.PCIS007. Value shall be Enabled"
}

TASK [redfish/attributes : Checking Attributes.PCIS007 at /redfish/v1/Systems/Self/Bios] ***************************************************
ok: [rchltxfb-93180012-rz-le0trtn-00.faredge.vzwops.com -> localhost]

TASK [redfish/attributes : what is currently verified] *************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-00.faredge.vzwops.com] => {
    "msg": "Sending GET to /redfish/v1/Systems/Self/Bios and query the returned json for Attributes.IIOS1FE. Value shall be Enable"
}

TASK [redfish/attributes : Checking Attributes.IIOS1FE at /redfish/v1/Systems/Self/Bios] ***************************************************
ok: [rchltxfb-93180012-rz-le0trtn-00.faredge.vzwops.com -> localhost]

TASK [redfish/attributes : what is currently verified] *************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-00.faredge.vzwops.com] => {
    "msg": "Sending GET to /redfish/v1/Systems/Self/Bios and query the returned json for Attributes.PMS004. Value shall be Disable"
}

TASK [redfish/attributes : Checking Attributes.PMS004 at /redfish/v1/Systems/Self/Bios] ****************************************************
ok: [rchltxfb-93180012-rz-le0trtn-00.faredge.vzwops.com -> localhost]

TASK [redfish/attributes : what is currently verified] *************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-00.faredge.vzwops.com] => {
    "msg": "Sending GET to /redfish/v1/Systems/Self/Bios and query the returned json for Attributes.PMS007. Value shall be C0/C1 state"
}

TASK [redfish/attributes : Checking Attributes.PMS007 at /redfish/v1/Systems/Self/Bios] ****************************************************
ok: [rchltxfb-93180012-rz-le0trtn-00.faredge.vzwops.com -> localhost]

TASK [redfish/attributes : what is currently verified] *************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-00.faredge.vzwops.com] => {
    "msg": "Sending GET to /redfish/v1/Systems/Self/Bios and query the returned json for Attributes.PMS002. Value shall be Enable"
}

TASK [redfish/attributes : Checking Attributes.PMS002 at /redfish/v1/Systems/Self/Bios] ****************************************************
ok: [rchltxfb-93180012-rz-le0trtn-00.faredge.vzwops.com -> localhost]

TASK [redfish/attributes : what is currently verified] *************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-00.faredge.vzwops.com] => {
    "msg": "Sending GET to /redfish/v1/Systems/Self/Bios and query the returned json for Attributes.PRSS011. Value shall be Enable"
}

TASK [redfish/attributes : Checking Attributes.PRSS011 at /redfish/v1/Systems/Self/Bios] ***************************************************
ok: [rchltxfb-93180012-rz-le0trtn-00.faredge.vzwops.com -> localhost]

TASK [redfish/attributes : what is currently verified] *************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-00.faredge.vzwops.com] => {
    "msg": "Sending GET to /redfish/v1/Systems/Self/Bios and query the returned json for Attributes.PRSS01A. Value shall be Enable"
}

TASK [redfish/attributes : Checking Attributes.PRSS01A at /redfish/v1/Systems/Self/Bios] ***************************************************
ok: [rchltxfb-93180012-rz-le0trtn-00.faredge.vzwops.com -> localhost]

PLAY RECAP *********************************************************************************************************************************
rchltxfb-93180012-rz-le0trtn-00.faredge.vzwops.com : ok=30   changed=0    unreachable=0    failed=0    skipped=20   rescued=0    ignored=0

[XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$
```

## Also checked the values manually with curl commands to redfish

```log
[XXXXXX@vcpe-jumpserver ~]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[2607:f160:10:9073:ce:406:0:1000]/redfish/v1/Systems/1/Bios|jq .Attributes.SETUP006
"CentOS,0x0001,true;UEFI: PXE IP4 Intel(R) Ethernet Network Adapter OCP XXV710-2,0x0002,true;UEFI: PXE IP4 Intel(R) Ethernet Network Adapter XXV710,0x0003,true;UEFI: Built-in EFI Shell,0x0004,true;"
[XXXXXX@vcpe-jumpserver ~]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[2607:f160:10:9073:ce:406:0:1000]/redfish/v1/Systems/1/Bios|jq .Attributes.SECB001
"Enabled"
[XXXXXX@vcpe-jumpserver ~]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[2607:f160:10:9073:ce:406:0:1000]/redfish/v1/Systems/1/Bios|jq .Attributes.PMS00A
"Performance"
[XXXXXX@vcpe-jumpserver ~]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[2607:f160:10:9073:ce:406:0:1000]/redfish/v1/Systems/1/Bios|jq .Attributes.PCIS007
"Enabled"
[XXXXXX@vcpe-jumpserver ~]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[2607:f160:10:9073:ce:406:0:1000]/redfish/v1/Systems/1/Bios|jq .Attributes.IIOS1FE
"Enable"
[XXXXXX@vcpe-jumpserver ~]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[2607:f160:10:9073:ce:406:0:1000]/redfish/v1/Systems/1/Bios|jq .Attributes.PMS004
"Disable"
[XXXXXX@vcpe-jumpserver ~]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[2607:f160:10:9073:ce:406:0:1000]/redfish/v1/Systems/1/Bios|jq .Attributes.PMS007
"C0/C1 state"
[XXXXXX@vcpe-jumpserver ~]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[2607:f160:10:9073:ce:406:0:1000]/redfish/v1/Systems/1/Bios|jq .Attributes.PMS002
"Enable"
[XXXXXX@vcpe-jumpserver ~]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[2607:f160:10:9073:ce:406:0:1000]/redfish/v1/Systems/1/Bios|jq .Attributes.PRSS011
"Enable"
[XXXXXX@vcpe-jumpserver ~]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[2607:f160:10:9073:ce:406:0:1000]/redfish/v1/Systems/1/Bios|jq .Attributes.PRSS01A
"Enable"
[XXXXXX@vcpe-jumpserver ~]$
```