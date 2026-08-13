# ZT .45 BMC firmware validation
# Firmware installation testing
# 11/15/23 James Patchett

## Target Controller rchltxib-c000000-003 CR-3 (Richardson infrastructure System)
Controller-0 OAM: 2607:f160:0:3049:cd:290:0:10

## Subcloud rchltxfe-d93180012-001 (VCP-fe Infrastructure)
OAM: 2607:f160:10:9073:ce:40a:0:f400
ILO: 2607:f160:10:9073:ce:406:0:1000

ipmitool -I lanplus -U XXXXXX -P XXXXXX -H 2607:f160:10:9073:ce:406:0:1000 sol activate

## Test Case
### Execute BMC playbook automation script against 2.27 BMC firmware

### Before execution, I removed K8Sctl user, and changed NTP & DNS server info to ensure they changed back after playbook

```log
[XXXXXX@welktxefnce-h-pe1util-vm01 bmc]$ ansible-playbook --vault-password-file ./vault_pass -i inventory/rchltxfb-93180012-rz-le0trtn-001.yaml bmc.yaml

PLAY [BMC configuration playbook] ******************************************************************************************************************************************

TASK [include_role : zts/enable-ssh] ***************************************************************************************************************************************

TASK [zts/enable-ssh : Check if ssh is enabled] ****************************************************************************************************************************
fatal: [rchltxfb-93180012-rz-le0trtn-001 -> localhost]: FAILED! => {"changed": true, "cmd": "sshpass -p \"XXXXXX\" ssh -o StrictHostKeyChecking=no \"XXXXXX\"@\"2607:f160:10:9073:ce:406:0:1000\" \"date\"\n", "delta": "0:00:09.838479", "end": "2023-11-29 13:03:58.541495", "msg": "non-zero return code", "rc": 5, "start": "2023-11-29 13:03:48.703016", "stderr": "Permission denied, please try again.", "stderr_lines": ["Permission denied, please try again."], "stdout": "", "stdout_lines": []}
...ignoring

TASK [zts/enable-ssh : Enable ssh using ipmitool method] *******************************************************************************************************************
skipping: [rchltxfb-93180012-rz-le0trtn-001]

TASK [include_role : zts/check-redfish-health] *****************************************************************************************************************************

TASK [zts/check-redfish-health : Check redfish health] *********************************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001 -> localhost]

TASK [include_role : zts/check_model] **************************************************************************************************************************************

TASK [zts/check_model : Get server model] **********************************************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001 -> localhost]

TASK [zts/check_model : Set server model] **********************************************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001]

TASK [zts/check_model : Display model name] ********************************************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001] => {
    "model_name": "triton                          "
}

TASK [zts/check_model : Fail when model specifier substring in hostname does not match the actual model name] **************************************************************
skipping: [rchltxfb-93180012-rz-le0trtn-001]

TASK [include_role : zts/configure-ipv4] ***********************************************************************************************************************************

TASK [zts/configure-ipv4 : Get initial static IPv4 settings] ***************************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001 -> localhost]

TASK [zts/configure-ipv4 : Display initial static IPv4 settings] ***********************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001] => {
    "get_info.json.IPv4StaticAddresses[0]": {
        "Address": "192.168.0.10",
        "AddressOrigin": "Static",
        "Gateway": "",
        "SubnetMask": "255.255.255.0"
    }
}

TASK [zts/configure-ipv4 : Set static IPv4 IP using ipmitool] **************************************************************************************************************
skipping: [rchltxfb-93180012-rz-le0trtn-001]

TASK [zts/configure-ipv4 : Wait for the Static IP change to take effect] ***************************************************************************************************
skipping: [rchltxfb-93180012-rz-le0trtn-001]

TASK [zts/configure-ipv4 : Set static IPv4 IP using redfish when IPv4StaticAddresses is defined] ***************************************************************************
skipping: [rchltxfb-93180012-rz-le0trtn-001]

TASK [zts/configure-ipv4 : Display output] *********************************************************************************************************************************
skipping: [rchltxfb-93180012-rz-le0trtn-001]

TASK [zts/configure-ipv4 : Wait for the Static IP change to take effect] ***************************************************************************************************
skipping: [rchltxfb-93180012-rz-le0trtn-001]

TASK [zts/configure-ipv4 : Get final static IPv4 settings] *****************************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001 -> localhost]

TASK [zts/configure-ipv4 : Display final static IPv4 settings] *************************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001] => {
    "get_info.json.IPv4StaticAddresses[0]": {
        "Address": "192.168.0.10",
        "AddressOrigin": "Static",
        "Gateway": "",
        "SubnetMask": "255.255.255.0"
    }
}

TASK [include_role : zts/account-create] ***********************************************************************************************************************************

TASK [zts/account-create : Get all user accounts] **************************************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001 -> localhost]

TASK [zts/account-create : Get all user account details] *******************************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001 -> localhost] => (item=None)
ok: [rchltxfb-93180012-rz-le0trtn-001 -> localhost] => (item=None)
ok: [rchltxfb-93180012-rz-le0trtn-001 -> localhost]

TASK [zts/account-create : Set user account list] **************************************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001] => (item=None)
ok: [rchltxfb-93180012-rz-le0trtn-001] => (item=None)
ok: [rchltxfb-93180012-rz-le0trtn-001]

TASK [zts/account-create : Display user accounts] **************************************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001] => {
    "users": [
        {
            "Enabled": true,
            "Id": "4",
            "Name": "XXXXXX",
            "RoleId": "XXXXXX",
            "UserName": "XXXXXX"
        },
        {
            "Enabled": true,
            "Id": "6",
            "Name": "XXXXXX",
            "RoleId": "XXXXXX",
            "UserName": "XXXXXX"
        }
    ]
}

TASK [zts/account-create : Set K8Sctl user variable] ***********************************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001]

TASK [zts/account-create : Create new K8Sctl user] *************************************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001 -> localhost]

TASK [zts/account-create : Display details for K8Sctl user created] ********************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001] => {
    "response.json": {
        "@odata.context": "/redfish/v1/$metadata#ManagerAccount.ManagerAccount",
        "@odata.etag": "\"1701407462\"",
        "@odata.id": "/redfish/v1/AccountService/Accounts",
        "@odata.type": "#ManagerAccount.v1_3_1.ManagerAccount",
        "AccountTypes": [
            "Redfish"
        ],
        "Certificates": {
            "@odata.id": "/redfish/v1/AccountService/Accounts/9/Certificates"
        },
        "Description": "Collection of Account Details",
        "Enabled": true,
        "Id": "9",
        "Links": {
            "Role": {
                "@odata.id": "/redfish/v1/AccountService/Roles/XXXXXX"
            }
        },
        "Locked": false,
        "Name": "Far Edge Account",
        "Password": null,
        "PasswordChangeRequired": false,
        "RoleId": "XXXXXX",
        "UserName": "K8Sctl"
    }
}

TASK [zts/account-create : Fail if K8Sctl user RoleId is not set to XXXXXX] *****************************************************************************************
skipping: [rchltxfb-93180012-rz-le0trtn-001]

TASK [include_role : zts/mac-discover] *************************************************************************************************************************************

TASK [zts/mac-discover : Create temporary working directory] ***************************************************************************************************************
changed: [rchltxfb-93180012-rz-le0trtn-001 -> localhost]

TASK [zts/mac-discover : Copy ZT MAC address discovery scripts to working dir] *********************************************************************************************
changed: [rchltxfb-93180012-rz-le0trtn-001 -> localhost] => (item=zt_find_oam_mac_address.py)
changed: [rchltxfb-93180012-rz-le0trtn-001 -> localhost] => (item=ls6_zt_find_oam_mac_address.py)

TASK [zts/mac-discover : Execute ZT MAC address discovery script for LS3] **************************************************************************************************
changed: [rchltxfb-93180012-rz-le0trtn-001 -> localhost]

TASK [zts/mac-discover : MAC address discovery for LS3 (result)] ***********************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001] => {
    "zt_mac_address_ls3.stdout_lines[0]": "68:05:CA:9A:EB:78"
}

TASK [zts/mac-discover : Execute ZT MAC address discovery script for LS6] **************************************************************************************************
skipping: [rchltxfb-93180012-rz-le0trtn-001]

TASK [zts/mac-discover : MAC address discovery for LS6 (result)] ***********************************************************************************************************
skipping: [rchltxfb-93180012-rz-le0trtn-001]

TASK [zts/mac-discover : Remove temporary working directory] ***************************************************************************************************************
changed: [rchltxfb-93180012-rz-le0trtn-001 -> localhost]

TASK [include_role : zts/system-off] ***************************************************************************************************************************************

TASK [zts/system-off : Force System Off] ***********************************************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001 -> localhost]

TASK [zts/system-off : Wait for ZTS to shutdown] ***************************************************************************************************************************
Pausing for 30 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [rchltxfb-93180012-rz-le0trtn-001 -> localhost]

TASK [include_role : zts/bios-config] **************************************************************************************************************************************

TASK [zts/bios-config : Create temporary working directory] ****************************************************************************************************************
changed: [rchltxfb-93180012-rz-le0trtn-001 -> localhost]

TASK [zts/bios-config : Copy ZT python scripts to working dir] *************************************************************************************************************
changed: [rchltxfb-93180012-rz-le0trtn-001 -> localhost] => (item=zt_bios.py)
changed: [rchltxfb-93180012-rz-le0trtn-001 -> localhost] => (item=ls6_zt_bios.py)
changed: [rchltxfb-93180012-rz-le0trtn-001 -> localhost] => (item=zt_enable_secure_boot.py)

TASK [zts/bios-config : Execute ZT configure BIOS script for LS3] **********************************************************************************************************
changed: [rchltxfb-93180012-rz-le0trtn-001 -> localhost]

TASK [zts/bios-config : debug LS3 (result)] ********************************************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001] => {
    "msg": "matched: key PMS00A to Performance\nmatched: key PMS007 to C0/C1 state\nmatched: key PMS002 to Enable\nmatched: key IIOS1FE to Enable\nmatched: key PCIS007 to Enabled\nmatched: key PRSS011 to Enable\nmatched: key PRSS01A to Enable\nmatched: key NWSK000 to Enabled"
}

TASK [zts/bios-config : Execute ZT configure BIOS script for LS6] **********************************************************************************************************
skipping: [rchltxfb-93180012-rz-le0trtn-001]

TASK [zts/bios-config : debug LS6 (result)] ********************************************************************************************************************************
skipping: [rchltxfb-93180012-rz-le0trtn-001]

TASK [zts/bios-config : Execute ZT secure boot script] *********************************************************************************************************************
changed: [rchltxfb-93180012-rz-le0trtn-001 -> localhost]

TASK [zts/bios-config : debug (result)] ************************************************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001] => {
    "msg": "Changing secure_boot_enable to True\n\nSuccess!"
}

TASK [zts/bios-config : Remove temporary working directory] ****************************************************************************************************************
changed: [rchltxfb-93180012-rz-le0trtn-001 -> localhost]

TASK [zts/bios-config : Get Bios Settings] *********************************************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001 -> localhost]

TASK [zts/bios-config : Fail when BIOS attributes are not set correctly] ***************************************************************************************************
skipping: [rchltxfb-93180012-rz-le0trtn-001]

TASK [include_role : zts/host-name] ****************************************************************************************************************************************

TASK [zts/host-name : Get inital host name] ********************************************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001 -> localhost]

TASK [zts/host-name : Display inital host name] ****************************************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001] => {
    "response_initial.json.HostName": "rchltxfb-93180012-rz-le0trtn-001"
}

TASK [zts/host-name : Wait for any existing PATCH requests to complete] ****************************************************************************************************
skipping: [rchltxfb-93180012-rz-le0trtn-001]

TASK [zts/host-name : Change host name for ZT events] **********************************************************************************************************************
skipping: [rchltxfb-93180012-rz-le0trtn-001]

TASK [zts/host-name : Get final host name] *********************************************************************************************************************************
skipping: [rchltxfb-93180012-rz-le0trtn-001]

TASK [zts/host-name : Display final host name] *****************************************************************************************************************************
skipping: [rchltxfb-93180012-rz-le0trtn-001]

TASK [include_role : zts/configure-dns] ************************************************************************************************************************************

TASK [zts/configure-dns : Get existing DNS Servers configured on the server] ***********************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001 -> localhost]

TASK [zts/configure-dns : Configure Static DNS Servers] ********************************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001 -> localhost]

TASK [zts/configure-dns : Wait for the DNS change to take effect] **********************************************************************************************************
Pausing for 180 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [rchltxfb-93180012-rz-le0trtn-001 -> localhost]

TASK [zts/configure-dns : Get Static DNS Servers configured on the server] *************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001 -> localhost]

TASK [zts/configure-dns : Fail if DNS servers do not match expected values] ************************************************************************************************
skipping: [rchltxfb-93180012-rz-le0trtn-001]

TASK [include_role : zts/configure-ntp] ************************************************************************************************************************************

TASK [zts/configure-ntp : Get NTP Servers configured on the server] ********************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001 -> localhost]

TASK [zts/configure-ntp : Display initial NTP server settings] *************************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001] => {
    "output.json.NTP": {
        "NTPServers": [
            "2607:f160:10:9200::1",
            "2607:f160:10:9200::2"
        ],
        "Port": 123,
        "ProtocolEnabled": true
    }
}

TASK [zts/configure-ntp : Configure Static NTP Servers] ********************************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001 -> localhost]

TASK [zts/configure-ntp : Get NTP Servers configured on the server] ********************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001 -> localhost]

TASK [zts/configure-ntp : Display final NTP server settings] ***************************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001] => {
    "output.json.NTP": {
        "NTPServers": [
            "2607:f160:10:9200::a",
            "2607:f160:10:9200::b"
        ],
        "Port": 123,
        "ProtocolEnabled": true
    }
}

TASK [zts/configure-ntp : Fail if NTP servers do not match expected values] ************************************************************************************************
skipping: [rchltxfb-93180012-rz-le0trtn-001]

TASK [include_role : zts/subscribe-redfish-events] *************************************************************************************************************************

TASK [zts/subscribe-redfish-events : Set facts to subscribe events for ZT servers] *****************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001]

TASK [zts/subscribe-redfish-events : Get Event subscription count] *********************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001 -> localhost]

TASK [zts/subscribe-redfish-events : Delete existing subscriptions] ********************************************************************************************************

TASK [zts/subscribe-redfish-events : Subscribe to Redfish Alarms (LS3)] ****************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001 -> localhost]

TASK [zts/subscribe-redfish-events : Subscribe to Redfish Alarms (LS6)] ****************************************************************************************************
skipping: [rchltxfb-93180012-rz-le0trtn-001]

TASK [include_role : zts/system-on] ****************************************************************************************************************************************

TASK [zts/system-on : Check if system is powered on] ***********************************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001 -> localhost]

TASK [zts/system-on : Display power status] ********************************************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001] => {
    "response.json.PowerState": "Off"
}

TASK [zts/system-on : Force System On] *************************************************************************************************************************************
ok: [rchltxfb-93180012-rz-le0trtn-001 -> localhost]

TASK [zts/system-on : Wait for ZTS to power on] ****************************************************************************************************************************
Pausing for 20 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [rchltxfb-93180012-rz-le0trtn-001 -> localhost]

TASK [include_role : hpe/check_model] **************************************************************************************************************************************
skipping: [rchltxfb-93180012-rz-le0trtn-001]

TASK [include_role : hpe/account-create] ***********************************************************************************************************************************
skipping: [rchltxfb-93180012-rz-le0trtn-001]

TASK [include_role : hpe/mac-discover] *************************************************************************************************************************************
skipping: [rchltxfb-93180012-rz-le0trtn-001]

TASK [include_role : hpe/bios-config] **************************************************************************************************************************************
skipping: [rchltxfb-93180012-rz-le0trtn-001]

TASK [include_role : hpe/dhcp-disable] *************************************************************************************************************************************
skipping: [rchltxfb-93180012-rz-le0trtn-001]

TASK [include_role : hpe/ilo-hostname] *************************************************************************************************************************************
skipping: [rchltxfb-93180012-rz-le0trtn-001]

TASK [include_role : hpe/system-off] ***************************************************************************************************************************************
skipping: [rchltxfb-93180012-rz-le0trtn-001]

TASK [include_role : hpe/host-name] ****************************************************************************************************************************************
skipping: [rchltxfb-93180012-rz-le0trtn-001]

TASK [include_role : hpe/system-on] ****************************************************************************************************************************************
skipping: [rchltxfb-93180012-rz-le0trtn-001]

TASK [include_role : hpe/syslog-disable] ***********************************************************************************************************************************
skipping: [rchltxfb-93180012-rz-le0trtn-001]

TASK [include_role : hpe/subscribe-redfish-events] *************************************************************************************************************************
skipping: [rchltxfb-93180012-rz-le0trtn-001]

PLAY RECAP *****************************************************************************************************************************************************************
rchltxfb-93180012-rz-le0trtn-001 : ok=49   changed=10   unreachable=0    failed=0    skipped=32   rescued=0    ignored=1

[XXXXXX@welktxefnce-h-pe1util-vm01 bmc]$
```

## BMC Playbook has completed with no issues detected
