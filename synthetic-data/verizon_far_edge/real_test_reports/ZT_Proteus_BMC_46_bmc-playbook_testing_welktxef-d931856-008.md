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


## BMC playbook ran against welktxef-d931856-008
## To see if playbook pushes settings change the following:
## Delete K8SCTL user, change DNS IPs, change NTP IPs and then run bmc playbook

```log
[XXXXXX@welktxefnce-h-pe1util-vm01 bmc]$ source ~/python_venvs/ansible_2.10.15/bin/activate
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 bmc]$ ansible-playbook --vault-password-file /tmp/vault-pass -i ./inventory/welktxef-931856-rz-le2pts6-008.yaml bmc.yaml

PLAY [BMC configuration playbook] ***********************************************************************************************************

TASK [include_role : zts/enable-ssh] ********************************************************************************************************

TASK [zts/enable-ssh : Check if ssh is enabled] *********************************************************************************************
fatal: [welktxef-931856-rz-le2pts6-008 -> localhost]: FAILED! => {"changed": true, "cmd": "sshpass -p \"XXXXXX\" ssh -o StrictHostKeyChecking=no \"XXXXXX\"@\"2607:f160:10:80b1:ce:40a:0:e008\" \"date\"\n", "delta": "0:00:00.813747", "end": "2024-01-16 13:29:54.083834", "msg": "non-zero return code", "rc": 255, "start": "2024-01-16 13:29:53.270087", "stderr": "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\r\n@    WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!     @\r\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\r\nIT IS POSSIBLE THAT SOMEONE IS DOING SOMETHING NASTY!\r\nSomeone could be eavesdropping on you right now (man-in-the-middle attack)!\r\nIt is also possible that a host key has just been changed.\r\nThe fingerprint for the RSA key sent by the remote host is\nSHA256:w1AshBu8/HtaGVdN+xBqHg3LGiXvKgnCUvzkz3m4i+k.\r\nPlease contact your system administrator.\r\nAdd correct host key in /home/XXXXXX/.ssh/known_hosts to get rid of this message.\r\nOffending RSA key in /home/XXXXXX/.ssh/known_hosts:2\r\nPassword authentication is disabled to avoid man-in-the-middle attacks.\r\nKeyboard-interactive authentication is disabled to avoid man-in-the-middle attacks.\r\nXXXXXX@2607:f160:10:80b1:ce:40a:0:e008: Permission denied (publickey,password).", "stderr_lines": ["@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@", "@    WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!     @", "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@", "IT IS POSSIBLE THAT SOMEONE IS DOING SOMETHING NASTY!", "Someone could be eavesdropping on you right now (man-in-the-middle attack)!", "It is also possible that a host key has just been changed.", "The fingerprint for the RSA key sent by the remote host is", "SHA256:w1AshBu8/HtaGVdN+xBqHg3LGiXvKgnCUvzkz3m4i+k.", "Please contact your system administrator.", "Add correct host key in /home/XXXXXX/.ssh/known_hosts to get rid of this message.", "Offending RSA key in /home/XXXXXX/.ssh/known_hosts:2", "Password authentication is disabled to avoid man-in-the-middle attacks.", "Keyboard-interactive authentication is disabled to avoid man-in-the-middle attacks.", "XXXXXX@2607:f160:10:80b1:ce:40a:0:e008: Permission denied (publickey,password)."], "stdout": "", "stdout_lines": []}
...ignoring

TASK [zts/enable-ssh : Enable ssh using ipmitool method] ************************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [include_role : zts/check-redfish-health] **********************************************************************************************

TASK [zts/check-redfish-health : Check redfish health] **************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [include_role : zts/check_model] *******************************************************************************************************

TASK [zts/check_model : Get server model] ***************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [zts/check_model : Set server model] ***************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008]

TASK [zts/check_model : Display model name] *************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "model_name": "proteus i"
}

TASK [zts/check_model : Fail when model specifier substring in hostname does not match the actual model name] *******************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [include_role : zts/configure-ipv4] ****************************************************************************************************

TASK [zts/configure-ipv4 : Get initial static IPv4 settings] ********************************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [zts/configure-ipv4 : Display initial static IPv4 settings] ****************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "get_info.json.IPv4StaticAddresses[0]": {
        "Address": "192.168.0.10",
        "AddressOrigin": "Static",
        "Gateway": "",
        "SubnetMask": "255.255.255.0"
    }
}

TASK [zts/configure-ipv4 : Set static IPv4 IP using ipmitool] *******************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [zts/configure-ipv4 : Wait for the Static IP change to take effect] ********************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [zts/configure-ipv4 : Set static IPv4 IP using redfish when IPv4StaticAddresses is defined] ********************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [zts/configure-ipv4 : Display output] **************************************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [zts/configure-ipv4 : Wait for the Static IP change to take effect] ********************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [zts/configure-ipv4 : Get final static IPv4 settings] **********************************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [zts/configure-ipv4 : Display final static IPv4 settings] ******************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "get_info.json.IPv4StaticAddresses[0]": {
        "Address": "192.168.0.10",
        "AddressOrigin": "Static",
        "Gateway": "",
        "SubnetMask": "255.255.255.0"
    }
}

TASK [include_role : zts/account-create] ****************************************************************************************************

TASK [zts/account-create : Get all user accounts] *******************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [zts/account-create : Get all user account details] ************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost] => (item=None)
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [zts/account-create : Set user account list] *******************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => (item=None)
ok: [welktxef-931856-rz-le2pts6-008]

TASK [zts/account-create : Display user accounts] *******************************************************************************************
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

TASK [zts/account-create : Set K8Sctl user variable] ****************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008]

TASK [zts/account-create : Create new K8Sctl user] ******************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [zts/account-create : Display details for K8Sctl user created] *************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "response.json": {
        "@odata.context": "/redfish/v1/$metadata#ManagerAccount.ManagerAccount",
        "@odata.etag": "\"1705556212\"",
        "@odata.id": "/redfish/v1/AccountService/Accounts",
        "@odata.type": "#ManagerAccount.v1_4_0.ManagerAccount",
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

TASK [zts/account-create : Fail if K8Sctl user RoleId is not set to XXXXXX] **********************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [include_role : zts/mac-discover] ******************************************************************************************************

TASK [zts/mac-discover : Create temporary working directory] ********************************************************************************
changed: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [zts/mac-discover : Copy ZT MAC address discovery scripts to working dir] **************************************************************
changed: [welktxef-931856-rz-le2pts6-008 -> localhost] => (item=zt_find_oam_mac_address.py)
changed: [welktxef-931856-rz-le2pts6-008 -> localhost] => (item=ls6_zt_find_oam_mac_address.py)

TASK [zts/mac-discover : Execute ZT MAC address discovery script for LS3] *******************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [zts/mac-discover : MAC address discovery for LS3 (result)] ****************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [zts/mac-discover : Execute ZT MAC address discovery script for LS6] *******************************************************************
changed: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [zts/mac-discover : MAC address discovery for LS6 (result)] ****************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "zt_mac_address_ls6.stdout_lines[0]": "B4:96:91:EB:94:54"
}

TASK [zts/mac-discover : Remove temporary working directory] ********************************************************************************
changed: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [include_role : zts/system-off] ********************************************************************************************************

TASK [zts/system-off : Force System Off] ****************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [zts/system-off : Wait for ZTS to shutdown] ********************************************************************************************
Pausing for 30 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [include_role : zts/bios-config] *******************************************************************************************************

TASK [zts/bios-config : Create temporary working directory] *********************************************************************************
changed: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [zts/bios-config : Copy ZT python scripts to working dir] ******************************************************************************
changed: [welktxef-931856-rz-le2pts6-008 -> localhost] => (item=zt_bios.py)
changed: [welktxef-931856-rz-le2pts6-008 -> localhost] => (item=ls6_zt_bios.py)
changed: [welktxef-931856-rz-le2pts6-008 -> localhost] => (item=zt_enable_secure_boot.py)

TASK [zts/bios-config : Execute ZT configure BIOS script for LS3] ***************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [zts/bios-config : debug LS3 (result)] *************************************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [zts/bios-config : Execute ZT configure BIOS script for LS6] ***************************************************************************
changed: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [zts/bios-config : debug LS6 (result)] *************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "msg": "matched: key PMS00A to Performance\nmatched: key PMS007 to C0/C1 state\nmatched: key PMS002 to Enable\nmatched: key IIOS1FE to Enable\nmatched: key PCIS007 to Enabled\nmatched: key PRSS011 to Enable\nmatched: key PRSS01A to Enable\nmatched: key NWSK000 to Enabled"
}

TASK [zts/bios-config : Execute ZT secure boot script] **************************************************************************************
changed: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [zts/bios-config : debug (result)] *****************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "msg": "Changing secure_boot_enable to True\n\nSuccess!"
}

TASK [zts/bios-config : Remove temporary working directory] *********************************************************************************
changed: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [zts/bios-config : Get Bios Settings] **************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [zts/bios-config : Fail when BIOS attributes are not set correctly] ********************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [include_role : zts/host-name] *********************************************************************************************************

TASK [zts/host-name : Get inital host name] *************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [zts/host-name : Display inital host name] *********************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "response_initial.json.HostName": "welktxef-931856-rz-le2pts6-008"
}

TASK [zts/host-name : Wait for any existing PATCH requests to complete] *********************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [zts/host-name : Change host name for ZT events] ***************************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [zts/host-name : Get final host name] **************************************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [zts/host-name : Display final host name] **********************************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [include_role : zts/configure-dns] *****************************************************************************************************

TASK [zts/configure-dns : Get existing DNS Servers configured on the server] ****************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [zts/configure-dns : Configure Static DNS Servers] *************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [zts/configure-dns : Wait for the DNS change to take effect] ***************************************************************************
Pausing for 180 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [zts/configure-dns : Get Static DNS Servers configured on the server] ******************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [zts/configure-dns : Fail if DNS servers do not match expected values] *****************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [include_role : zts/configure-ntp] *****************************************************************************************************

TASK [zts/configure-ntp : Get NTP Servers configured on the server] *************************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [zts/configure-ntp : Display initial NTP server settings] ******************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "output.json.NTP": {
        "NTPServers": [
            "2607:f160:10:9200::c",
            "2607:f160:10:9200::d"
        ],
        "Port": 123,
        "ProtocolEnabled": true
    }
}

TASK [zts/configure-ntp : Configure Static NTP Servers] *************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [zts/configure-ntp : Get NTP Servers configured on the server] *************************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [zts/configure-ntp : Display final NTP server settings] ********************************************************************************
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

TASK [zts/configure-ntp : Fail if NTP servers do not match expected values] *****************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [include_role : zts/subscribe-redfish-events] ******************************************************************************************

TASK [zts/subscribe-redfish-events : Set facts to subscribe events for ZT servers] **********************************************************
ok: [welktxef-931856-rz-le2pts6-008]

TASK [zts/subscribe-redfish-events : Get Event subscription count] **************************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [zts/subscribe-redfish-events : Delete existing subscriptions] *************************************************************************

TASK [zts/subscribe-redfish-events : Subscribe to Redfish Alarms (LS3)] *********************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [zts/subscribe-redfish-events : Subscribe to Redfish Alarms (LS6)] *********************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [include_role : zts/system-on] *********************************************************************************************************

TASK [zts/system-on : Check if system is powered on] ****************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [zts/system-on : Display power status] *************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "response.json.PowerState": "Off"
}

TASK [zts/system-on : Force System On] ******************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [zts/system-on : Wait for ZTS to power on] *********************************************************************************************
Pausing for 20 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [include_role : hpe/check_model] *******************************************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [include_role : hpe/account-create] ****************************************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [include_role : hpe/mac-discover] ******************************************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [include_role : hpe/bios-config] *******************************************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [include_role : hpe/dhcp-disable] ******************************************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [include_role : hpe/ilo-hostname] ******************************************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [include_role : hpe/system-off] ********************************************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [include_role : hpe/host-name] *********************************************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [include_role : hpe/system-on] *********************************************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [include_role : hpe/syslog-disable] ****************************************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [include_role : hpe/subscribe-redfish-events] ******************************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

PLAY RECAP **********************************************************************************************************************************
welktxef-931856-rz-le2pts6-008 : ok=49   changed=10   unreachable=0    failed=0    skipped=32   rescued=0    ignored=1

(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 bmc]$

```

### Evaulated settings in UI of BMC, playbook worked fine, all changed settings were set back to default bmc settings. 
### No errors or issues with BMC playbook, test succesfull.

