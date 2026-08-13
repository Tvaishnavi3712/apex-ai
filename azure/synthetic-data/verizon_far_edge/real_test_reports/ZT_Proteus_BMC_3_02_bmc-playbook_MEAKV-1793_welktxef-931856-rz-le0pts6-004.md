# ZT Proteus 3.02 BMC firmware validation
# ZT Proteus BIOS .30
# 10/16/25 James Patchett



## Target Subcloud wwelktxef-931856-rz-le0pts6-004
BMC: 2607:f160:10:80b1:ce:40a:0:e003




## BMC playbook ran against welktxef-d931856-008
## To see if playbook pushes settings change the following:
## Delete K8SCTL user, change DNS IPs, change NTP IPs and then run bmc playbook

```log
(ansible_6.7) szabota@welktxefnce-h-pe1util-vm05:~/playbooks/bmc-10-22-25/bmc$ ansible-playbook --vault-password-file vault.txt -i ./inventory/welktxef-931856-rz-le0pts6-004.yaml bmc.yaml

PLAY [BMC configuration playbook] *******************************************************************************************************************

TASK [include_role : zts/enable-ssh] ****************************************************************************************************************

TASK [zts/enable-ssh : Check if ssh is enabled] *****************************************************************************************************
fatal: [welktxef-931856-rz-le0pts6-004 -> localhost]: FAILED! => {"changed": true, "cmd": "sshpass -p \"XXXXXX\" ssh -o StrictHostKeyChecking=no \"XXXXXX\"@\"2607:f160:10:80b1:ce:40a:0:e003\" \"date\"\n", "delta": "0:00:00.959896", "end": "2025-10-22 22:02:15.229634", "msg": "non-zero return code", "rc": 255, "start": "2025-10-22 22:02:14.269738", "stderr": "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\r\n@    WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!     @\r\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\r\nIT IS POSSIBLE THAT SOMEONE IS DOING SOMETHING NASTY!\r\nSomeone could be eavesdropping on you right now (man-in-the-middle attack)!\r\nIt is also possible that a host key has just been changed.\r\nThe fingerprint for the RSA key sent by the remote host is\nSHA256:2VXIlWKgtmmBp2c1x6dN4nEuF4e4TSXRgqOWu6hTLzQ.\r\nPlease contact your system administrator.\r\nAdd correct host key in /home/szabota/.ssh/known_hosts to get rid of this message.\r\nOffending RSA key in /home/szabota/.ssh/known_hosts:39\r\n  remove with:\r\n  ssh-keygen -f \"/home/szabota/.ssh/known_hosts\" -R \"2607:f160:10:80b1:ce:40a:0:e003\"\r\nPassword authentication is disabled to avoid man-in-the-middle attacks.\r\nKeyboard-interactive authentication is disabled to avoid man-in-the-middle attacks.\r\nXXXXXX@2607:f160:10:80b1:ce:40a:0:e003: Permission denied (publickey,password).", "stderr_lines": ["@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@", "@    WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!     @", "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@", "IT IS POSSIBLE THAT SOMEONE IS DOING SOMETHING NASTY!", "Someone could be eavesdropping on you right now (man-in-the-middle attack)!", "It is also possible that a host key has just been changed.", "The fingerprint for the RSA key sent by the remote host is", "SHA256:2VXIlWKgtmmBp2c1x6dN4nEuF4e4TSXRgqOWu6hTLzQ.", "Please contact your system administrator.", "Add correct host key in /home/szabota/.ssh/known_hosts to get rid of this message.", "Offending RSA key in /home/szabota/.ssh/known_hosts:39", "  remove with:", "  ssh-keygen -f \"/home/szabota/.ssh/known_hosts\" -R \"2607:f160:10:80b1:ce:40a:0:e003\"", "Password authentication is disabled to avoid man-in-the-middle attacks.", "Keyboard-interactive authentication is disabled to avoid man-in-the-middle attacks.", "XXXXXX@2607:f160:10:80b1:ce:40a:0:e003: Permission denied (publickey,password)."], "stdout": "", "stdout_lines": []}
...ignoring

TASK [zts/enable-ssh : Enable ssh using ipmitool method] ********************************************************************************************
skipping: [welktxef-931856-rz-le0pts6-004]

TASK [include_role : zts/check-redfish-health] ******************************************************************************************************

TASK [zts/check-redfish-health : Check redfish health] **********************************************************************************************
ok: [welktxef-931856-rz-le0pts6-004 -> localhost]

TASK [include_role : zts/check_model] ***************************************************************************************************************

TASK [zts/check_model : Get server model] ***********************************************************************************************************
ok: [welktxef-931856-rz-le0pts6-004 -> localhost]

TASK [zts/check_model : Set server model] ***********************************************************************************************************
ok: [welktxef-931856-rz-le0pts6-004]

TASK [zts/check_model : Display model name] *********************************************************************************************************
ok: [welktxef-931856-rz-le0pts6-004] => {
    "model_name": "proteus i_mix"
}

TASK [zts/check_model : Fail when model specifier substring in hostname does not match the actual model name] ***************************************
skipping: [welktxef-931856-rz-le0pts6-004]

TASK [include_role : zts/disable_pam_auth] **********************************************************************************************************

TASK [zts/disable_pam_auth : Get PAM authentication status] *****************************************************************************************
ok: [welktxef-931856-rz-le0pts6-004 -> localhost]

TASK [zts/disable_pam_auth : Disable PAM authentication] ********************************************************************************************
skipping: [welktxef-931856-rz-le0pts6-004]

TASK [include_role : zts/disable_pam_auth] **********************************************************************************************************

TASK [zts/disable_pam_auth : Get PAM authentication status] *****************************************************************************************
ok: [welktxef-931856-rz-le0pts6-004 -> localhost]

TASK [zts/disable_pam_auth : Disable PAM authentication] ********************************************************************************************
skipping: [welktxef-931856-rz-le0pts6-004]

TASK [include_role : zts/configure-ipv4] ************************************************************************************************************

TASK [zts/configure-ipv4 : Get initial static IPv4 settings] ****************************************************************************************
ok: [welktxef-931856-rz-le0pts6-004 -> localhost]

TASK [zts/configure-ipv4 : Display initial static IPv4 settings] ************************************************************************************
ok: [welktxef-931856-rz-le0pts6-004] => {
    "get_info.json.IPv4StaticAddresses[0]": {
        "Address": "192.168.0.10",
        "AddressOrigin": "Static",
        "Gateway": "",
        "SubnetMask": "255.255.255.0"
    }
}

TASK [zts/configure-ipv4 : Set static IPv4 IP using ipmitool] ***************************************************************************************
skipping: [welktxef-931856-rz-le0pts6-004]

TASK [zts/configure-ipv4 : Wait for the Static IP change to take effect] ****************************************************************************
skipping: [welktxef-931856-rz-le0pts6-004]

TASK [zts/configure-ipv4 : Set static IPv4 IP using redfish when IPv4StaticAddresses is defined] ****************************************************
skipping: [welktxef-931856-rz-le0pts6-004]

TASK [zts/configure-ipv4 : Display output] **********************************************************************************************************
skipping: [welktxef-931856-rz-le0pts6-004]

TASK [zts/configure-ipv4 : Wait for the Static IP change to take effect] ****************************************************************************
skipping: [welktxef-931856-rz-le0pts6-004]

TASK [zts/configure-ipv4 : Get final static IPv4 settings] ******************************************************************************************
ok: [welktxef-931856-rz-le0pts6-004 -> localhost]

TASK [zts/configure-ipv4 : Display final static IPv4 settings] **************************************************************************************
ok: [welktxef-931856-rz-le0pts6-004] => {
    "get_info.json.IPv4StaticAddresses[0]": {
        "Address": "192.168.0.10",
        "AddressOrigin": "Static",
        "Gateway": "",
        "SubnetMask": "255.255.255.0"
    }
}

TASK [include_role : zts/account-create] ************************************************************************************************************

TASK [zts/account-create : Get all user accounts] ***************************************************************************************************
ok: [welktxef-931856-rz-le0pts6-004 -> localhost]

TASK [zts/account-create : Get all user account details] ********************************************************************************************
ok: [welktxef-931856-rz-le0pts6-004 -> localhost] => (item=None)
ok: [welktxef-931856-rz-le0pts6-004 -> localhost]

TASK [zts/account-create : Set user account list] ***************************************************************************************************
ok: [welktxef-931856-rz-le0pts6-004] => (item=None)
ok: [welktxef-931856-rz-le0pts6-004]

TASK [zts/account-create : Display user accounts] ***************************************************************************************************
ok: [welktxef-931856-rz-le0pts6-004] => {
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

TASK [zts/account-create : Set XXXXXX user variable] ************************************************************************************************
ok: [welktxef-931856-rz-le0pts6-004]

TASK [zts/account-create : Delete existing XXXXXX user] *********************************************************************************************
skipping: [welktxef-931856-rz-le0pts6-004]

TASK [zts/account-create : Create new XXXXXX user] **************************************************************************************************
ok: [welktxef-931856-rz-le0pts6-004 -> localhost]

TASK [zts/account-create : Display details for XXXXXX user created] *********************************************************************************
ok: [welktxef-931856-rz-le0pts6-004] => {
    "response.json": {
        "@odata.context": "/redfish/v1/$metadata#ManagerAccount.ManagerAccount",
        "@odata.etag": "\"1761293356\"",
        "@odata.id": "/redfish/v1/AccountService/Accounts",
        "@odata.type": "#ManagerAccount.v1_12_1.ManagerAccount",
        "AccountTypes": [
            "Redfish"
        ],
        "Certificates": {
            "@odata.id": "/redfish/v1/AccountService/Accounts/25/Certificates"
        },
        "Description": "Collection of Account Details",
        "Enabled": true,
        "Id": "25",
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
        "UserName": "XXXXXX"
    }
}

TASK [zts/account-create : Fail if XXXXXX user RoleId is not set to XXXXXX] ******************************************************************
skipping: [welktxef-931856-rz-le0pts6-004]

TASK [include_role : zts/mac-discover] **************************************************************************************************************

TASK [zts/mac-discover : Create temporary working directory] ****************************************************************************************
changed: [welktxef-931856-rz-le0pts6-004 -> localhost]

TASK [zts/mac-discover : Copy ZT MAC address discovery scripts to working dir] **********************************************************************
changed: [welktxef-931856-rz-le0pts6-004 -> localhost] => (item=zt_find_oam_mac_address.py)
changed: [welktxef-931856-rz-le0pts6-004 -> localhost] => (item=ls6_zt_find_oam_mac_address.py)

TASK [zts/mac-discover : Execute ZT MAC address discovery script for LS3] ***************************************************************************
skipping: [welktxef-931856-rz-le0pts6-004]

TASK [zts/mac-discover : MAC address discovery for LS3 (result)] ************************************************************************************
skipping: [welktxef-931856-rz-le0pts6-004]

TASK [zts/mac-discover : Execute ZT MAC address discovery script for LS6] ***************************************************************************
changed: [welktxef-931856-rz-le0pts6-004 -> localhost]

TASK [zts/mac-discover : MAC address discovery for LS6 (result)] ************************************************************************************
ok: [welktxef-931856-rz-le0pts6-004] => {
    "zt_mac_address_ls6.stdout_lines[0]": "B4:96:91:B6:13:38"
}

TASK [zts/mac-discover : Remove temporary working directory] ****************************************************************************************
changed: [welktxef-931856-rz-le0pts6-004 -> localhost]

TASK [include_role : zts/system-off] ****************************************************************************************************************

TASK [zts/system-off : Force System Off] ************************************************************************************************************
ok: [welktxef-931856-rz-le0pts6-004 -> localhost]

TASK [zts/system-off : Wait for ZTS to shutdown] ****************************************************************************************************
Pausing for 30 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [welktxef-931856-rz-le0pts6-004 -> localhost]

TASK [include_role : zts/bios-config] ***************************************************************************************************************

TASK [zts/bios-config : Create temporary working directory] *****************************************************************************************
changed: [welktxef-931856-rz-le0pts6-004 -> localhost]

TASK [zts/bios-config : Copy ZT python scripts to working dir] **************************************************************************************
changed: [welktxef-931856-rz-le0pts6-004 -> localhost] => (item=zt_bios.py)
changed: [welktxef-931856-rz-le0pts6-004 -> localhost] => (item=ls6_zt_bios.py)
changed: [welktxef-931856-rz-le0pts6-004 -> localhost] => (item=zt_enable_secure_boot.py)

TASK [zts/bios-config : Execute ZT configure BIOS script for LS3] ***********************************************************************************
skipping: [welktxef-931856-rz-le0pts6-004]

TASK [zts/bios-config : debug LS3 (result)] *********************************************************************************************************
skipping: [welktxef-931856-rz-le0pts6-004]

TASK [zts/bios-config : Execute ZT configure BIOS script for LS6] ***********************************************************************************
changed: [welktxef-931856-rz-le0pts6-004 -> localhost]

TASK [zts/bios-config : debug LS6 (result)] *********************************************************************************************************
ok: [welktxef-931856-rz-le0pts6-004] => {
    "msg": "matched: key PMS00A to Performance\nmatched: key PMS007 to C0/C1 state\nmatched: key PMS002 to Enable\nmatched: key IIOS1FE to Enable\nmatched: key PCIS007 to Enabled\nmatched: key PRSS011 to Enable\nmatched: key PRSS01A to Enable\nmatched: key NWSK000 to Enabled"
}

TASK [zts/bios-config : Execute ZT secure boot script] **********************************************************************************************
skipping: [welktxef-931856-rz-le0pts6-004]

TASK [zts/bios-config : debug (result)] *************************************************************************************************************
skipping: [welktxef-931856-rz-le0pts6-004]

TASK [zts/bios-config : Execute ZT secure boot script (SNO build)] **********************************************************************************
skipping: [welktxef-931856-rz-le0pts6-004]

TASK [zts/bios-config : debug (result)] *************************************************************************************************************
skipping: [welktxef-931856-rz-le0pts6-004]

TASK [zts/bios-config : Remove temporary working directory] *****************************************************************************************
changed: [welktxef-931856-rz-le0pts6-004 -> localhost]

TASK [zts/bios-config : Get Bios Settings] **********************************************************************************************************
ok: [welktxef-931856-rz-le0pts6-004 -> localhost]

TASK [zts/bios-config : Fail when BIOS attributes are not set correctly] ****************************************************************************
skipping: [welktxef-931856-rz-le0pts6-004]

TASK [include_role : zts/host-name] *****************************************************************************************************************

TASK [zts/host-name : Get inital host name] *********************************************************************************************************
ok: [welktxef-931856-rz-le0pts6-004 -> localhost]

TASK [zts/host-name : Display inital host name] *****************************************************************************************************
ok: [welktxef-931856-rz-le0pts6-004] => {
    "response_initial.json.HostName": "welktxef-931856-rz-le0pts6-004-MTCE_lab_TEST"
}

TASK [zts/host-name : Wait for any existing PATCH requests to complete] *****************************************************************************
Pausing for 90 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [welktxef-931856-rz-le0pts6-004]

TASK [zts/host-name : Change host name for ZT events] ***********************************************************************************************
ok: [welktxef-931856-rz-le0pts6-004 -> localhost]

TASK [zts/host-name : Get final host name] **********************************************************************************************************
ok: [welktxef-931856-rz-le0pts6-004 -> localhost]

TASK [zts/host-name : Display final host name] ******************************************************************************************************
ok: [welktxef-931856-rz-le0pts6-004] => {
    "response_final.json.HostName": "welktxef-931856-rz-le0pts6-004"
}

TASK [include_role : zts/configure-dns] *************************************************************************************************************

TASK [zts/configure-dns : Get existing DNS Servers configured on the server] ************************************************************************
ok: [welktxef-931856-rz-le0pts6-004 -> localhost]

TASK [zts/configure-dns : Configure Static DNS Servers] *********************************************************************************************
[WARNING]: Collection ansible.netcommon does not support Ansible version 2.13.7
[DEPRECATION WARNING]: Use 'ansible.utils.ipaddr' module instead. This feature will be removed from ansible.netcommon in a release after 2024-01-01.
 Deprecation warnings can be disabled by setting deprecation_warnings=False in ansible.cfg.
[WARNING]: Collection ansible.utils does not support Ansible version 2.13.7
FAILED - RETRYING: [welktxef-931856-rz-le0pts6-004 -> localhost]: Configure Static DNS Servers (10 retries left).
ok: [welktxef-931856-rz-le0pts6-004 -> localhost]

TASK [zts/configure-dns : Wait for the DNS change to take effect] ***********************************************************************************
[WARNING]: Collection ansible.netcommon does not support Ansible version 2.13.7
[DEPRECATION WARNING]: Use 'ansible.utils.ipaddr' module instead. This feature will be removed from ansible.netcommon in a release after 2024-01-01.
 Deprecation warnings can be disabled by setting deprecation_warnings=False in ansible.cfg.
[WARNING]: Collection ansible.utils does not support Ansible version 2.13.7
Pausing for 180 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [welktxef-931856-rz-le0pts6-004 -> localhost]

TASK [zts/configure-dns : Get Static DNS Servers configured on the server] **************************************************************************
[WARNING]: Collection ansible.netcommon does not support Ansible version 2.13.7
[DEPRECATION WARNING]: Use 'ansible.utils.ipaddr' module instead. This feature will be removed from ansible.netcommon in a release after 2024-01-01.
 Deprecation warnings can be disabled by setting deprecation_warnings=False in ansible.cfg.
[WARNING]: Collection ansible.utils does not support Ansible version 2.13.7
ok: [welktxef-931856-rz-le0pts6-004 -> localhost]

TASK [zts/configure-dns : Fail if DNS servers do not match expected values] *************************************************************************
[WARNING]: Collection ansible.netcommon does not support Ansible version 2.13.7
[DEPRECATION WARNING]: Use 'ansible.utils.ipaddr' module instead. This feature will be removed from ansible.netcommon in a release after 2024-01-01.
 Deprecation warnings can be disabled by setting deprecation_warnings=False in ansible.cfg.
[WARNING]: Collection ansible.utils does not support Ansible version 2.13.7
skipping: [welktxef-931856-rz-le0pts6-004]

TASK [include_role : zts/configure-ntp] *************************************************************************************************************

TASK [zts/configure-ntp : Get NTP Servers configured on the server] *********************************************************************************
ok: [welktxef-931856-rz-le0pts6-004 -> localhost]

TASK [zts/configure-ntp : Display initial NTP server settings] **************************************************************************************
ok: [welktxef-931856-rz-le0pts6-004] => {
    "output.json.NTP": {
        "NTPServers": [
            "2607:f160:10:9200::E",
            "2607:f160:10:9200::F"
        ],
        "Port": 123,
        "ProtocolEnabled": true
    }
}

TASK [zts/configure-ntp : Configure Static NTP Servers] *********************************************************************************************
ok: [welktxef-931856-rz-le0pts6-004 -> localhost]

TASK [zts/configure-ntp : Get NTP Servers configured on the server] *********************************************************************************
ok: [welktxef-931856-rz-le0pts6-004 -> localhost]

TASK [zts/configure-ntp : Display final NTP server settings] ****************************************************************************************
ok: [welktxef-931856-rz-le0pts6-004] => {
    "output.json.NTP": {
        "NTPServers": [
            "2607:f160:10:9200::a",
            "2607:f160:10:9200::b"
        ],
        "Port": 123,
        "ProtocolEnabled": true
    }
}

TASK [zts/configure-ntp : Fail if NTP servers do not match expected values] *************************************************************************
skipping: [welktxef-931856-rz-le0pts6-004]

TASK [include_role : zts/subscribe-redfish-events] **************************************************************************************************

TASK [zts/subscribe-redfish-events : Set facts to subscribe events for ZT servers] ******************************************************************
ok: [welktxef-931856-rz-le0pts6-004]

TASK [zts/subscribe-redfish-events : Get Event subscription count] **********************************************************************************
ok: [welktxef-931856-rz-le0pts6-004 -> localhost]

TASK [zts/subscribe-redfish-events : Delete existing subscriptions] *********************************************************************************

TASK [zts/subscribe-redfish-events : Subscribe to Redfish Alarms (LS3)] *****************************************************************************
skipping: [welktxef-931856-rz-le0pts6-004]

TASK [zts/subscribe-redfish-events : Subscribe to Redfish Alarms (LS6)] *****************************************************************************
ok: [welktxef-931856-rz-le0pts6-004 -> localhost]

TASK [include_role : zts/system-on] *****************************************************************************************************************

TASK [zts/system-on : Check if system is powered on] ************************************************************************************************
ok: [welktxef-931856-rz-le0pts6-004 -> localhost]

TASK [zts/system-on : Display power status] *********************************************************************************************************
ok: [welktxef-931856-rz-le0pts6-004] => {
    "response.json.PowerState": "Off"
}

TASK [zts/system-on : Force System On] **************************************************************************************************************
ok: [welktxef-931856-rz-le0pts6-004 -> localhost]

TASK [zts/system-on : Wait for ZTS to power on] *****************************************************************************************************
Pausing for 20 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [welktxef-931856-rz-le0pts6-004 -> localhost]

TASK [include_role : hpe/check_model] ***************************************************************************************************************
skipping: [welktxef-931856-rz-le0pts6-004]

TASK [include_role : hpe/upgrade_ls3] ***************************************************************************************************************
skipping: [welktxef-931856-rz-le0pts6-004]

TASK [include_role : hpe/upgrade_ls6] ***************************************************************************************************************
skipping: [welktxef-931856-rz-le0pts6-004]

TASK [include_role : hpe/account-create] ************************************************************************************************************
skipping: [welktxef-931856-rz-le0pts6-004]

TASK [include_role : hpe/mac-discover] **************************************************************************************************************
skipping: [welktxef-931856-rz-le0pts6-004]

TASK [include_role : hpe/bios-config] ***************************************************************************************************************
skipping: [welktxef-931856-rz-le0pts6-004]

TASK [include_role : hpe/dhcp-disable] **************************************************************************************************************
skipping: [welktxef-931856-rz-le0pts6-004]

TASK [include_role : hpe/ilo-hostname] **************************************************************************************************************
skipping: [welktxef-931856-rz-le0pts6-004]

TASK [include_role : hpe/system-off] ****************************************************************************************************************
skipping: [welktxef-931856-rz-le0pts6-004]

TASK [include_role : hpe/host-name] *****************************************************************************************************************
skipping: [welktxef-931856-rz-le0pts6-004]

TASK [include_role : hpe/system-on] *****************************************************************************************************************
skipping: [welktxef-931856-rz-le0pts6-004]

TASK [include_role : hpe/syslog-disable] ************************************************************************************************************
skipping: [welktxef-931856-rz-le0pts6-004]

TASK [include_role : hpe/subscribe-redfish-events] **************************************************************************************************
skipping: [welktxef-931856-rz-le0pts6-004]

PLAY RECAP ******************************************************************************************************************************************
welktxef-931856-rz-le0pts6-004 : ok=53   changed=9    unreachable=0    failed=0    skipped=37   rescued=0    ignored=1

(ansible_6.7) szabota@welktxefnce-h-pe1util-vm05:~/playbooks/bmc-10-22-25/bmc$

```

### Evaulated settings in UI of BMC, playbook worked fine, all changed settings were set back to default bmc settings. 
### No errors or issues with BMC playbook, test succesfull.

