# ZT .45 BMC firmware validation
# 10/24/23 James Patchett

## Target Controller Rchltxfe-c000000-001
Controller-0 iLO 2607:f160:a:d02e:cd:fe0::8000 
Controller-1 iLO 2607:f160:a:d02e:cd:fe0::8001
Worker-0 iLO 2607:f160:a:d02e:cd:fe0::8002 
OAM 2607:f160:0:3043:cd:290:0:10



## Target Subcloud welktxef-d931887-021 (currently on controller 2607:f160:0:3049:cd:290:0:10 )
OAM 2607:f160:10:9249:ce:40a:0:f409
BMC 2607:f160:10:9249:ce:40a:0:e015

welktxef-931887-rz-le2pts6-021.yaml

ipmitool -I lanplus -U XXXXXX -P XXXXXX -H 2607:f160:10:9249:ce:40a:0:e015 sol activate

## Target Subcloud welktxef-d931856-008
OAM: 2607:f160:10:80b1:ce:40a:0:f408
BMC: 2607:f160:10:80b1:ce:40a:0:e008

welktxef-931856-rz-le2pts6-008.yaml

ipmitool -I lanplus -U XXXXXX -P XXXXXX -H 2607:f160:10:80b1:ce:40a:0:e008 sol activate

## BMC playbook ran against welktxef-d931887-021
## before run had to remove existing user XXXXXX/K8Sctl

```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 bmc]$ ansible-playbook --vault-password-file /tmp/vault-pass -i ./inventory/welktxef-931887-rz-le2pts6-021.yaml bmc.yaml

PLAY [BMC configuration playbook] ****************************************************************************************************************************************************

TASK [include_role : zts/enable-ssh] *************************************************************************************************************************************************

TASK [zts/enable-ssh : Check if ssh is enabled] **************************************************************************************************************************************
fatal: [welktxef-931887-rz-le2pts6-021 -> localhost]: FAILED! => {"changed": true, "cmd": "sshpass -p \"XXXXXX\" ssh -o StrictHostKeyChecking=no \"XXXXXX\"@\"2607:f160:10:9249:ce:40a:0:e015\" \"date\"\n", "delta": "0:00:09.998359", "end": "2023-10-30 15:05:45.681109", "msg": "non-zero return code", "rc": 5, "start": "2023-10-30 15:05:35.682750", "stderr": "Permission denied, please try again.", "stderr_lines": ["Permission denied, please try again."], "stdout": "", "stdout_lines": []}
...ignoring

TASK [zts/enable-ssh : Enable ssh using ipmitool method] *****************************************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [include_role : zts/check-redfish-health] ***************************************************************************************************************************************

TASK [zts/check-redfish-health : Check redfish health] *******************************************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [include_role : zts/check_model] ************************************************************************************************************************************************

TASK [zts/check_model : Get server model] ********************************************************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [zts/check_model : Set server model] ********************************************************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [zts/check_model : Display model name] ******************************************************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "model_name": "proteus i_mix"
}

TASK [zts/check_model : Fail when model specifier substring in hostname does not match the actual model name] ************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [include_role : zts/upgrade_ls3] ************************************************************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [include_role : zts/configure-ipv4] *********************************************************************************************************************************************

TASK [zts/configure-ipv4 : Get initial static IPv4 settings] *************************************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [zts/configure-ipv4 : Display initial static IPv4 settings] *********************************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "get_info.json.IPv4StaticAddresses[0]": {
        "Address": "192.168.0.10",
        "AddressOrigin": "Static",
        "Gateway": "192.168.0.1",
        "SubnetMask": "255.255.255.0"
    }
}

TASK [zts/configure-ipv4 : Set static IPv4 IP using ipmitool] ************************************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [zts/configure-ipv4 : Wait for the Static IP change to take effect] *************************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [zts/configure-ipv4 : Set static IPv4 IP using redfish when IPv4StaticAddresses is defined] *************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [zts/configure-ipv4 : Display output] *******************************************************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [zts/configure-ipv4 : Wait for the Static IP change to take effect] *************************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [zts/configure-ipv4 : Get final static IPv4 settings] ***************************************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [zts/configure-ipv4 : Display final static IPv4 settings] ***********************************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "get_info.json.IPv4StaticAddresses[0]": {
        "Address": "192.168.0.10",
        "AddressOrigin": "Static",
        "Gateway": "192.168.0.1",
        "SubnetMask": "255.255.255.0"
    }
}

TASK [include_role : zts/account-create] *********************************************************************************************************************************************

TASK [zts/account-create : Get all user accounts] ************************************************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [zts/account-create : Get all user account details] *****************************************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost] => (item=None)
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [zts/account-create : Set user account list] ************************************************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => (item=None)
ok: [welktxef-931887-rz-le2pts6-021]

TASK [zts/account-create : Display user accounts] ************************************************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "users": [
        {
            "Enabled": true,
            "Id": "1",
            "Name": "Default Account",
            "RoleId": "XXXXXX",
            "UserName": "XXXXXX"
        }
    ]
}

TASK [zts/account-create : Set K8Sctl user variable] *********************************************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [zts/account-create : Create new K8Sctl user] ***********************************************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [zts/account-create : Display details for K8Sctl user created] ******************************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "response.json": {
        "@odata.context": "/redfish/v1/$metadata#ManagerAccount.ManagerAccount",
        "@odata.etag": "\"1698696354\"",
        "@odata.id": "/redfish/v1/AccountService/Accounts",
        "@odata.type": "#ManagerAccount.v1_3_1.ManagerAccount",
        "AccountTypes": [
            "Redfish"
        ],
        "Certificates": {
            "@odata.id": "/redfish/v1/AccountService/Accounts/7/Certificates"
        },
        "Description": "Collection of Account Details",
        "Enabled": true,
        "Id": "7",
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

TASK [zts/account-create : Fail if K8Sctl user RoleId is not set to XXXXXX] ***************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [include_role : zts/mac-discover] ***********************************************************************************************************************************************

TASK [zts/mac-discover : Create temporary working directory] *************************************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [zts/mac-discover : Copy ZT MAC address discovery scripts to working dir] *******************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost] => (item=zt_find_oam_mac_address.py)
changed: [welktxef-931887-rz-le2pts6-021 -> localhost] => (item=ls6_zt_find_oam_mac_address.py)

TASK [zts/mac-discover : Execute ZT MAC address discovery script for LS3] ************************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [zts/mac-discover : MAC address discovery for LS3 (result)] *********************************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [zts/mac-discover : Execute ZT MAC address discovery script for LS6] ************************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [zts/mac-discover : MAC address discovery for LS6 (result)] *********************************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "zt_mac_address_ls6.stdout_lines[0]": "B4:96:91:B5:5E:54"
}

TASK [zts/mac-discover : Remove temporary working directory] *************************************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [include_role : zts/system-off] *************************************************************************************************************************************************

TASK [zts/system-off : Force System Off] *********************************************************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [zts/system-off : Wait for ZTS to shutdown] *************************************************************************************************************************************
Pausing for 30 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [include_role : zts/bios-config] ************************************************************************************************************************************************

TASK [zts/bios-config : Create temporary working directory] **************************************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [zts/bios-config : Copy ZT python scripts to working dir] ***********************************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost] => (item=zt_bios.py)
changed: [welktxef-931887-rz-le2pts6-021 -> localhost] => (item=ls6_zt_bios.py)
changed: [welktxef-931887-rz-le2pts6-021 -> localhost] => (item=zt_enable_secure_boot.py)

TASK [zts/bios-config : Execute ZT configure BIOS script for LS3] ********************************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [zts/bios-config : debug LS3 (result)] ******************************************************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [zts/bios-config : Execute ZT configure BIOS script for LS6] ********************************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [zts/bios-config : debug LS6 (result)] ******************************************************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "msg": "matched: key PMS00A to Performance\nmatched: key PMS007 to C0/C1 state\nmatched: key PMS002 to Enable\nmatched: key IIOS1FE to Enable\nmatched: key PCIS007 to Enabled\nmatched: key PRSS011 to Enable\nmatched: key PRSS01A to Enable\nmatched: key NWSK000 to Enabled"
}

TASK [zts/bios-config : Execute ZT secure boot script] *******************************************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [zts/bios-config : debug (result)] **********************************************************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "msg": "Changing secure_boot_enable to True\n\nSuccess!"
}

TASK [zts/bios-config : Remove temporary working directory] **************************************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [zts/bios-config : Get Bios Settings] *******************************************************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [zts/bios-config : Fail when BIOS attributes are not set correctly] *************************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [include_role : zts/host-name] **************************************************************************************************************************************************

TASK [zts/host-name : Get inital host name] ******************************************************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [zts/host-name : Display inital host name] **************************************************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "response_initial.json.HostName": "welktxef-931887-rz-le2pts6-021"
}

TASK [zts/host-name : Wait for any existing PATCH requests to complete] **************************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [zts/host-name : Change host name for ZT events] ********************************************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [zts/host-name : Get final host name] *******************************************************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [zts/host-name : Display final host name] ***************************************************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [include_role : zts/configure-dns] **********************************************************************************************************************************************

TASK [zts/configure-dns : Get existing DNS Servers configured on the server] *********************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [zts/configure-dns : Configure Static DNS Servers] ******************************************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [zts/configure-dns : Wait for the DNS change to take effect] ********************************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [zts/configure-dns : Get Static DNS Servers configured on the server] ***********************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [zts/configure-dns : Fail if DNS servers do not match expected values] **********************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [include_role : zts/configure-ntp] **********************************************************************************************************************************************

TASK [zts/configure-ntp : Get NTP Servers configured on the server] ******************************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [zts/configure-ntp : Display initial NTP server settings] ***********************************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "output.json.NTP": {
        "NTPServers": [
            "2607:f160:10:9200::a",
            "2607:f160:10:9200::b"
        ],
        "Port": 123,
        "ProtocolEnabled": false
    }
}

TASK [zts/configure-ntp : Configure Static NTP Servers] ******************************************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [zts/configure-ntp : Get NTP Servers configured on the server] ******************************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [zts/configure-ntp : Display final NTP server settings] *************************************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "output.json.NTP": {
        "NTPServers": [
            "2607:f160:10:9200::a",
            "2607:f160:10:9200::b"
        ],
        "Port": 123,
        "ProtocolEnabled": false
    }
}

TASK [zts/configure-ntp : Fail if NTP servers do not match expected values] **********************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [include_role : zts/subscribe-redfish-events] ***********************************************************************************************************************************

TASK [zts/subscribe-redfish-events : Set facts to subscribe events for ZT servers] ***************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [zts/subscribe-redfish-events : Get Event subscription count] *******************************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [zts/subscribe-redfish-events : Delete existing subscriptions] ******************************************************************************************************************

TASK [zts/subscribe-redfish-events : Subscribe to Redfish Alarms (LS3)] **************************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [zts/subscribe-redfish-events : Subscribe to Redfish Alarms (LS6)] **************************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [include_role : zts/system-on] **************************************************************************************************************************************************

TASK [zts/system-on : Check if system is powered on] *********************************************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [zts/system-on : Display power status] ******************************************************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "response.json.PowerState": "Off"
}

TASK [zts/system-on : Force System On] ***********************************************************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [zts/system-on : Wait for ZTS to power on] **************************************************************************************************************************************
Pausing for 20 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [include_role : hpe/check_model] ************************************************************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [include_role : hpe/account-create] *********************************************************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [include_role : hpe/mac-discover] ***********************************************************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [include_role : hpe/bios-config] ************************************************************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [include_role : hpe/dhcp-disable] ***********************************************************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [include_role : hpe/ilo-hostname] ***********************************************************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [include_role : hpe/system-off] *************************************************************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [include_role : hpe/host-name] **************************************************************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [include_role : hpe/system-on] **************************************************************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [include_role : hpe/syslog-disable] *********************************************************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [include_role : hpe/subscribe-redfish-events] ***********************************************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

PLAY RECAP ***************************************************************************************************************************************************************************
welktxef-931887-rz-le2pts6-021 : ok=45   changed=10   unreachable=0    failed=0    skipped=37   rescued=0    ignored=1

(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 bmc]$
```


## BMC playbook ran against welktxef-d931856-008
## before run had to remove existing user XXXXXX

```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 bmc]$ ansible-playbook --vault-password-file /tmp/vault-pass -i ./inventory/welktxef-931856-rz-le2pts6-008.yaml bmc.yaml

PLAY [BMC configuration playbook] ****************************************************************************************************************************************************

TASK [include_role : zts/enable-ssh] *************************************************************************************************************************************************

TASK [zts/enable-ssh : Check if ssh is enabled] **************************************************************************************************************************************
fatal: [welktxef-931856-rz-le2pts6-008 -> localhost]: FAILED! => {"changed": true, "cmd": "sshpass -p \"XXXXXX\" ssh -o StrictHostKeyChecking=no \"XXXXXX\"@\"2607:f160:10:80b1:ce:40a:0:e008\" \"date\"\n", "delta": "0:00:07.719900", "end": "2023-10-30 15:12:50.242871", "msg": "non-zero return code", "rc": 5, "start": "2023-10-30 15:12:42.522971", "stderr": "Permission denied, please try again.", "stderr_lines": ["Permission denied, please try again."], "stdout": "", "stdout_lines": []}
...ignoring

TASK [zts/enable-ssh : Enable ssh using ipmitool method] *****************************************************************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [include_role : zts/check-redfish-health] ***************************************************************************************************************************************

TASK [zts/check-redfish-health : Check redfish health] *******************************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [include_role : zts/check_model] ************************************************************************************************************************************************

TASK [zts/check_model : Get server model] ********************************************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [zts/check_model : Set server model] ********************************************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008]

TASK [zts/check_model : Display model name] ******************************************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "model_name": "proteus i"
}

TASK [zts/check_model : Fail when model specifier substring in hostname does not match the actual model name] ************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [include_role : zts/upgrade_ls3] ************************************************************************************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [include_role : zts/configure-ipv4] *********************************************************************************************************************************************

TASK [zts/configure-ipv4 : Get initial static IPv4 settings] *************************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [zts/configure-ipv4 : Display initial static IPv4 settings] *********************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "get_info.json.IPv4StaticAddresses[0]": {
        "Address": "192.168.0.10",
        "AddressOrigin": "Static",
        "Gateway": "",
        "SubnetMask": "255.255.255.0"
    }
}

TASK [zts/configure-ipv4 : Set static IPv4 IP using ipmitool] ************************************************************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [zts/configure-ipv4 : Wait for the Static IP change to take effect] *************************************************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [zts/configure-ipv4 : Set static IPv4 IP using redfish when IPv4StaticAddresses is defined] *************************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [zts/configure-ipv4 : Display output] *******************************************************************************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [zts/configure-ipv4 : Wait for the Static IP change to take effect] *************************************************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [zts/configure-ipv4 : Get final static IPv4 settings] ***************************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [zts/configure-ipv4 : Display final static IPv4 settings] ***********************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "get_info.json.IPv4StaticAddresses[0]": {
        "Address": "192.168.0.10",
        "AddressOrigin": "Static",
        "Gateway": "",
        "SubnetMask": "255.255.255.0"
    }
}

TASK [include_role : zts/account-create] *********************************************************************************************************************************************

TASK [zts/account-create : Get all user accounts] ************************************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [zts/account-create : Get all user account details] *****************************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost] => (item=None)
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [zts/account-create : Set user account list] ************************************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => (item=None)
ok: [welktxef-931856-rz-le2pts6-008]

TASK [zts/account-create : Display user accounts] ************************************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "users": [
        {
            "Enabled": true,
            "Id": "1",
            "Name": "Default Account",
            "RoleId": "XXXXXX",
            "UserName": "XXXXXX"
        }
    ]
}

TASK [zts/account-create : Set K8Sctl user variable] *********************************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008]

TASK [zts/account-create : Create new K8Sctl user] ***********************************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [zts/account-create : Display details for K8Sctl user created] ******************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "response.json": {
        "@odata.context": "/redfish/v1/$metadata#ManagerAccount.ManagerAccount",
        "@odata.etag": "\"1698696778\"",
        "@odata.id": "/redfish/v1/AccountService/Accounts",
        "@odata.type": "#ManagerAccount.v1_3_1.ManagerAccount",
        "AccountTypes": [
            "Redfish"
        ],
        "Certificates": {
            "@odata.id": "/redfish/v1/AccountService/Accounts/6/Certificates"
        },
        "Description": "Collection of Account Details",
        "Enabled": true,
        "Id": "6",
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

TASK [zts/account-create : Fail if K8Sctl user RoleId is not set to XXXXXX] ***************************************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [include_role : zts/mac-discover] ***********************************************************************************************************************************************

TASK [zts/mac-discover : Create temporary working directory] *************************************************************************************************************************
changed: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [zts/mac-discover : Copy ZT MAC address discovery scripts to working dir] *******************************************************************************************************
changed: [welktxef-931856-rz-le2pts6-008 -> localhost] => (item=zt_find_oam_mac_address.py)
changed: [welktxef-931856-rz-le2pts6-008 -> localhost] => (item=ls6_zt_find_oam_mac_address.py)

TASK [zts/mac-discover : Execute ZT MAC address discovery script for LS3] ************************************************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [zts/mac-discover : MAC address discovery for LS3 (result)] *********************************************************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [zts/mac-discover : Execute ZT MAC address discovery script for LS6] ************************************************************************************************************
changed: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [zts/mac-discover : MAC address discovery for LS6 (result)] *********************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "zt_mac_address_ls6.stdout_lines[0]": "B4:96:91:EB:94:54"
}

TASK [zts/mac-discover : Remove temporary working directory] *************************************************************************************************************************
changed: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [include_role : zts/system-off] *************************************************************************************************************************************************

TASK [zts/system-off : Force System Off] *********************************************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [zts/system-off : Wait for ZTS to shutdown] *************************************************************************************************************************************
Pausing for 30 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [include_role : zts/bios-config] ************************************************************************************************************************************************

TASK [zts/bios-config : Create temporary working directory] **************************************************************************************************************************
changed: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [zts/bios-config : Copy ZT python scripts to working dir] ***********************************************************************************************************************
changed: [welktxef-931856-rz-le2pts6-008 -> localhost] => (item=zt_bios.py)
changed: [welktxef-931856-rz-le2pts6-008 -> localhost] => (item=ls6_zt_bios.py)
changed: [welktxef-931856-rz-le2pts6-008 -> localhost] => (item=zt_enable_secure_boot.py)

TASK [zts/bios-config : Execute ZT configure BIOS script for LS3] ********************************************************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [zts/bios-config : debug LS3 (result)] ******************************************************************************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [zts/bios-config : Execute ZT configure BIOS script for LS6] ********************************************************************************************************************
changed: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [zts/bios-config : debug LS6 (result)] ******************************************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "msg": "matched: key PMS00A to Performance\nmatched: key PMS007 to C0/C1 state\nmatched: key PMS002 to Enable\nmatched: key IIOS1FE to Enable\nmatched: key PCIS007 to Enabled\nmatched: key PRSS011 to Enable\nmatched: key PRSS01A to Enable\nmatched: key NWSK000 to Enabled"
}

TASK [zts/bios-config : Execute ZT secure boot script] *******************************************************************************************************************************
changed: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [zts/bios-config : debug (result)] **********************************************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "msg": "Changing secure_boot_enable to True\n\nSuccess!"
}

TASK [zts/bios-config : Remove temporary working directory] **************************************************************************************************************************
changed: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [zts/bios-config : Get Bios Settings] *******************************************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [zts/bios-config : Fail when BIOS attributes are not set correctly] *************************************************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [include_role : zts/host-name] **************************************************************************************************************************************************

TASK [zts/host-name : Get inital host name] ******************************************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [zts/host-name : Display inital host name] **************************************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "response_initial.json.HostName": "welktxef-931883-rz-le2pts6-022"
}

TASK [zts/host-name : Wait for any existing PATCH requests to complete] **************************************************************************************************************
Pausing for 90 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [welktxef-931856-rz-le2pts6-008]

TASK [zts/host-name : Change host name for ZT events] ********************************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [zts/host-name : Get final host name] *******************************************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [zts/host-name : Display final host name] ***************************************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "response_final.json.HostName": "welktxef-931856-rz-le2pts6-008"
}

TASK [include_role : zts/configure-dns] **********************************************************************************************************************************************

TASK [zts/configure-dns : Get existing DNS Servers configured on the server] *********************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [zts/configure-dns : Configure Static DNS Servers] ******************************************************************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [zts/configure-dns : Wait for the DNS change to take effect] ********************************************************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [zts/configure-dns : Get Static DNS Servers configured on the server] ***********************************************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [zts/configure-dns : Fail if DNS servers do not match expected values] **********************************************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [include_role : zts/configure-ntp] **********************************************************************************************************************************************

TASK [zts/configure-ntp : Get NTP Servers configured on the server] ******************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [zts/configure-ntp : Display initial NTP server settings] ***********************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "output.json.NTP": {
        "NTPServers": [
            "2607:f160:10:9200::a",
            "2607:f160:10:8200::a"
        ],
        "Port": 123,
        "ProtocolEnabled": false
    }
}

TASK [zts/configure-ntp : Configure Static NTP Servers] ******************************************************************************************************************************
FAILED - RETRYING: Configure Static NTP Servers (10 retries left).
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [zts/configure-ntp : Get NTP Servers configured on the server] ******************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [zts/configure-ntp : Display final NTP server settings] *************************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "output.json.NTP": {
        "NTPServers": [
            "2607:f160:10:9200::a",
            "2607:f160:10:9200::b"
        ],
        "Port": 123,
        "ProtocolEnabled": true
    }
}

TASK [zts/configure-ntp : Fail if NTP servers do not match expected values] **********************************************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [include_role : zts/subscribe-redfish-events] ***********************************************************************************************************************************

TASK [zts/subscribe-redfish-events : Set facts to subscribe events for ZT servers] ***************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008]

TASK [zts/subscribe-redfish-events : Get Event subscription count] *******************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [zts/subscribe-redfish-events : Delete existing subscriptions] ******************************************************************************************************************

TASK [zts/subscribe-redfish-events : Subscribe to Redfish Alarms (LS3)] **************************************************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [zts/subscribe-redfish-events : Subscribe to Redfish Alarms (LS6)] **************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [include_role : zts/system-on] **************************************************************************************************************************************************

TASK [zts/system-on : Check if system is powered on] *********************************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [zts/system-on : Display power status] ******************************************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "response.json.PowerState": "Off"
}

TASK [zts/system-on : Force System On] ***********************************************************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [zts/system-on : Wait for ZTS to power on] **************************************************************************************************************************************
Pausing for 20 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [include_role : hpe/check_model] ************************************************************************************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [include_role : hpe/account-create] *********************************************************************************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [include_role : hpe/mac-discover] ***********************************************************************************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [include_role : hpe/bios-config] ************************************************************************************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [include_role : hpe/dhcp-disable] ***********************************************************************************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [include_role : hpe/ilo-hostname] ***********************************************************************************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [include_role : hpe/system-off] *************************************************************************************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [include_role : hpe/host-name] **************************************************************************************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [include_role : hpe/system-on] **************************************************************************************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [include_role : hpe/syslog-disable] *********************************************************************************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [include_role : hpe/subscribe-redfish-events] ***********************************************************************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

PLAY RECAP ***************************************************************************************************************************************************************************
welktxef-931856-rz-le2pts6-008 : ok=50   changed=10   unreachable=0    failed=0    skipped=32   rescued=0    ignored=1

(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 bmc]$
```

