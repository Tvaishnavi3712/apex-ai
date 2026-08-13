# HPE ILO5 3.06 BIOS H08 v2.12
# HPE Sapphire Rapids E910t server
# 8/28/24 James Patchett - MTCE Lab VCPfe
# BMC Playbook MEAKV-1750

## welktxef-931881-rh-le0e910-005
ILO:  2607:f160:10:922a:ce:406:0:1000
OAM:  2607:f160:10:922a:ce:40a:0:f400

## Subcloud welktxef-d931881-005
## General info before we start

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ system show
system oam-show+------------------------+--------------------------------------+
| Property               | Value                                |
+------------------------+--------------------------------------+
| contact                | None                                 |
| created_at             | 2024-07-03T16:11:02.896972+00:00     |
| description            | None                                 |
| distributed_cloud_role | subcloud                             |
| https_enabled          | True                                 |
| latitude               | None                                 |
| location               | None                                 |
| longitude              | None                                 |
| name                   | welktxef-d931881-005                 |
| region_name            | welktxef-d931881-005                 |
| sdn_enabled            | False                                |
| security_feature       | spectre_meltdown_v1                  |
| service_project_name   | services                             |
| shared_services        | []                                   |
| software_version       | 22.12                                |
| system_mode            | simplex                              |
| system_type            | All-in-one                           |
| timezone               | UTC                                  |
| updated_at             | 2024-08-03T02:49:22.960189+00:00     |
| uuid                   | 3b13920e-8deb-484c-bbca-58b710b2d185 |
| vswitch_type           | none                                 |
+------------------------+--------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ system oam-show
+----------------+---------------------------------------+
| Property       | Value                                 |
+----------------+---------------------------------------+
| created_at     | 2024-07-03T16:13:20.520978+00:00      |
| isystem_uuid   | 3b13920e-8deb-484c-bbca-58b710b2d185  |
| oam_end_ip     | 2607:f160:10:922a:ffff:ffff:ffff:fffe |
| oam_gateway_ip | 2607:f160:10:922a:ce:28::             |
| oam_ip         | 2607:f160:10:922a:ce:40a:0:f400       |
| oam_start_ip   | 2607:f160:10:922a::1                  |
| oam_subnet     | 2607:f160:10:922a::/64                |
| updated_at     | None                                  |
| uuid           | d37418df-d18f-4342-b005-749f7b824387  |
+----------------+---------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ system application-list
+--------------------------+-----------+-------------------------------------------+------------------+---------+-----------+
| application              | version   | manifest name                             | manifest file    | status  | progress  |
+--------------------------+-----------+-------------------------------------------+------------------+---------+-----------+
| cert-manager             | 22.12-8   | cert-manager-fluxcd-manifests             | fluxcd-manifests | applied | completed |
| metrics-server           | 22.12-2   | metrics-server-fluxcd-manifests           | fluxcd-manifests | applied | completed |
| nginx-ingress-controller | 22.12-1   | nginx-ingress-controller-fluxcd-manifests | fluxcd-manifests | applied | completed |
| oidc-auth-apps           | 22.12-6   | oidc-auth-apps-fluxcd-manifests           | fluxcd-manifests | applied | completed |
| platform-integ-apps      | 22.12-72  | platform-integ-apps-fluxcd-manifests      | fluxcd-manifests | applied | completed |
| ptp-notification         | 22.12-140 | ptp-notification-fluxcd-manifests         | fluxcd-manifests | applied | completed |
| wr-analytics             | 23.09-1   | wr-analytics-fluxcd-manifests             | fluxcd-manifests | applied | completed |
+--------------------------+-----------+-------------------------------------------+------------------+---------+-----------+
[XXXXXX@controller-0 ~(keystone_admin)]$ sw-patch query
      Patch ID         RR  Release  Patch State
=====================  ==  =======  ===========
WRCP_22.12_PATCH_0001  Y    22.12    Committed
WRCP_22.12_PATCH_0002  Y    22.12    Committed
WRCP_22.12_PATCH_0003  Y    22.12    Committed
WRCP_22.12_PATCH_0004  Y    22.12    Committed
WRCP_22.12_PATCH_0005  Y    22.12    Committed

[XXXXXX@controller-0 ~(keystone_admin)]$ fm alarm-list

[XXXXXX@controller-0 ~(keystone_admin)]$

```


## MEAKV-1750 BMC Playbook run against the ILO after the ILO was reset to facotry default settings.

```log
(atlas) szabota@welktxefnce-h-pe1util-vm05:~/playbooks/bmc-workloadprofile/bmc$ ANSIBLE_LOG_PATH=./bmc-testing_$(date "+%Y%m%d%H%M%S").log ansible-playbook --vault-password-file /tmp/password -i inventory/welktxef-931881-rh-le0e910-005.yaml bmc.yaml

PLAY [BMC configuration playbook] ****************************************************************************************************************************************************

TASK [Initialize me environment variable] ********************************************************************************************************************************************
skipping: [welktxef-931881-rh-le0e910-005]

TASK [Initialize prod environment variable] ******************************************************************************************************************************************
ok: [welktxef-931881-rh-le0e910-005]

TASK [include_role : zts/set_redfish_url] ********************************************************************************************************************************************
skipping: [welktxef-931881-rh-le0e910-005]

TASK [include_role : zts/enable-ssh] *************************************************************************************************************************************************
skipping: [welktxef-931881-rh-le0e910-005]

TASK [include_role : zts/clear_sel_logs] *********************************************************************************************************************************************
skipping: [welktxef-931881-rh-le0e910-005]

TASK [include_role : zts/check_model] ************************************************************************************************************************************************
skipping: [welktxef-931881-rh-le0e910-005]

TASK [include_role : zts/upgrade_ls3] ************************************************************************************************************************************************
skipping: [welktxef-931881-rh-le0e910-005]

TASK [include_role : zts/upgrade_ls6] ************************************************************************************************************************************************
skipping: [welktxef-931881-rh-le0e910-005]

TASK [include_role : zts/upgrade_galene] *********************************************************************************************************************************************
skipping: [welktxef-931881-rh-le0e910-005]

TASK [include_role : zts/disable_pam_auth] *******************************************************************************************************************************************
skipping: [welktxef-931881-rh-le0e910-005]

TASK [include_role : zts/configure-ipv4] *********************************************************************************************************************************************
skipping: [welktxef-931881-rh-le0e910-005]

TASK [include_role : zts/account-create] *********************************************************************************************************************************************
skipping: [welktxef-931881-rh-le0e910-005]

TASK [include_role : zts/mac-discover] ***********************************************************************************************************************************************
skipping: [welktxef-931881-rh-le0e910-005]

TASK [include_role : zts/system-off] *************************************************************************************************************************************************
skipping: [welktxef-931881-rh-le0e910-005]

TASK [include_role : zts/bios-config] ************************************************************************************************************************************************
skipping: [welktxef-931881-rh-le0e910-005]

TASK [include_role : zts/host-name] **************************************************************************************************************************************************
skipping: [welktxef-931881-rh-le0e910-005]

TASK [include_role : zts/configure-dns] **********************************************************************************************************************************************
skipping: [welktxef-931881-rh-le0e910-005]

TASK [include_role : zts/configure-ntp] **********************************************************************************************************************************************
skipping: [welktxef-931881-rh-le0e910-005]

TASK [include_role : zts/subscribe-redfish-events] ***********************************************************************************************************************************
skipping: [welktxef-931881-rh-le0e910-005]

TASK [include_role : zts/system-on] **************************************************************************************************************************************************
skipping: [welktxef-931881-rh-le0e910-005]

TASK [include_role : hpe/check_model] ************************************************************************************************************************************************

TASK [hpe/check_model : Get server model] ********************************************************************************************************************************************
ok: [welktxef-931881-rh-le0e910-005 -> localhost]

TASK [hpe/check_model : Set server model] ********************************************************************************************************************************************
ok: [welktxef-931881-rh-le0e910-005]

TASK [hpe/check_model : Display model name] ******************************************************************************************************************************************
ok: [welktxef-931881-rh-le0e910-005] => {
    "model_name": "ProLiant e910t"
}

TASK [hpe/check_model : Fail when model specifier substring in hostname does not match the actual model name] ************************************************************************
skipping: [welktxef-931881-rh-le0e910-005]

TASK [include_role : hpe/upgrade_ls3] ************************************************************************************************************************************************

TASK [Download firmware] *************************************************************************************************************************************************************

TASK [hpe/download_firmware : Check if upgrade binaries exist locally] ***************************************************************************************************************
ok: [welktxef-931881-rh-le0e910-005 -> localhost]

TASK [hpe/download_firmware : Download & unarchive firmware upgrade binaries to local tmp directory if they do not exist] ************************************************************
skipping: [welktxef-931881-rh-le0e910-005]

TASK [hpe/upgrade_ls3 : Get HPE ILO firmware version before upgrade] *****************************************************************************************************************
included: /home/szabota/playbooks/bmc-workloadprofile/bmc/roles/hpe/upgrade_ls3/tasks/ls3_ilo_firmware_version.yaml for welktxef-931881-rh-le0e910-005

TASK [hpe/upgrade_ls3 : Get HPE ILO version] *****************************************************************************************************************************************
ok: [welktxef-931881-rh-le0e910-005 -> localhost]

TASK [hpe/upgrade_ls3 : Set ILO version] *********************************************************************************************************************************************
ok: [welktxef-931881-rh-le0e910-005]

TASK [hpe/upgrade_ls3 : Display ILO version] *****************************************************************************************************************************************
ok: [welktxef-931881-rh-le0e910-005] => {
    "ilo_version": "3.06 Jul 10 2024"
}

TASK [hpe/upgrade_ls3 : Get HPE NIC firmware version before upgrade] *****************************************************************************************************************
included: /home/szabota/playbooks/bmc-workloadprofile/bmc/roles/hpe/upgrade_ls3/tasks/ls3_nic_version.yaml for welktxef-931881-rh-le0e910-005

TASK [hpe/upgrade_ls3 : Get HPE LS3 NIC interface firmware version] ******************************************************************************************************************
ok: [welktxef-931881-rh-le0e910-005 -> localhost]

TASK [hpe/upgrade_ls3 : Record NIC interface firmware version] ***********************************************************************************************************************
ok: [welktxef-931881-rh-le0e910-005]

TASK [hpe/upgrade_ls3 : Display NIC interface firmware version] **********************************************************************************************************************
ok: [welktxef-931881-rh-le0e910-005] => {
    "nic_version": "1.3353.0"
}

TASK [include_role : hpe/upgrade_ls6] ************************************************************************************************************************************************
skipping: [welktxef-931881-rh-le0e910-005]

TASK [include_role : hpe/upgrade_e930t] **********************************************************************************************************************************************
skipping: [welktxef-931881-rh-le0e910-005]

TASK [include_role : hpe/account-create] *********************************************************************************************************************************************

TASK [hpe/account-create : Create temporary working directory] ***********************************************************************************************************************
changed: [welktxef-931881-rh-le0e910-005 -> localhost]

TASK [hpe/account-create : Copy HPE account creation scripts to working dir] *********************************************************************************************************
changed: [welktxef-931881-rh-le0e910-005 -> localhost] => (item={'filename': 'get_resource_directory.py', 'value': '#!/usr/bin/env python\n\nfrom __future__ import print_function\nimport argparse\nimport ipaddress\nimport yaml\nfrom redfish import RedfishClient as RedfishClient\nimport os\nimport sys\nfrom redfish.rest.v1 import ServerDownOrUnreachableError\n\ndef get_resource_directory_profile():\n    cwd = os.path.dirname(os.path.abspath(__file__))\n    profile_name = "%s/hp_hw_profile.yaml" % cwd\n    try:\n        with open(profile_name) as file:\n            return yaml.load(file, Loader=yaml.FullLoader)["resource_directory"]\n    except IOError:\n        print("Error opening %s" % profile_name)\n        sys.exit(2)\n\ndef get_resource_directory(redfish_obj):\n    profile = get_resource_directory_profile()\n    response = redfish_obj.get(profile["url"])\n    resources = None\n    if response.status == 200:\n        resources = response.dict[profile["section"]]\n    else:\n        sys.stderr.write("\\tResource directory missing at %s\\n" % profile["url"])\n        sys.exit(2)\n    return resources\n\nif __name__ == "__main__":\n    parser = argparse.ArgumentParser(description="get resource directory script")\n    parser.add_argument("-n", dest="ip", required=True, help="The BMC IP address")\n    parser.add_argument("-u", dest="user", required=True, help="The BMC username")\n    parser.add_argument("-p", dest="passwd", required=True, help="The BMC password")\n    args = parser.parse_args()\n    ip = args.ip\n    login_account = args.user\n    login_password = args.passwd\n    ip_adar_type = ipaddress.ip_address(ip)\n    if type(ip_adar_type) == ipaddress.IPv4Address:\n        system_url = "https://" + ip + ""\n    else:\n        system_url = "https://[" + ip + "]"\n    redfish_obj = None\n    try:\n        redfish_obj = RedfishClient(base_url=system_url, username=login_account, password=XXXXXX        redfish_obj.login()\n    except ServerDownOrUnreachableError:\n        sys.stderr.write("ERROR: server not reachable or doesn\'t support Redfish.\\n")\n        sys.exit(2)\n    get_resource_directory(redfish_obj)\n    sys.exit(0)\n'})
changed: [welktxef-931881-rh-le0e910-005 -> localhost] => (item={'filename': 'hp_hw_profile.yaml', 'value': '---\nresource_directory:\n  url: /redfish/v1/resourcedirectory\n  section: Instances\n'})

TASK [hpe/account-create : Copy HPE account creation scripts to working dir] *********************************************************************************************************
changed: [welktxef-931881-rh-le0e910-005 -> localhost] => (item=add_user_account.py)

TASK [hpe/account-create : Execute HPE account creation script] **********************************************************************************************************************
changed: [welktxef-931881-rh-le0e910-005 -> localhost]

TASK [hpe/account-create : Remove temporary working directory] ***********************************************************************************************************************
changed: [welktxef-931881-rh-le0e910-005 -> localhost]

TASK [include_role : hpe/mac-discover] ***********************************************************************************************************************************************

TASK [hpe/mac-discover : Create temporary working directory] *************************************************************************************************************************
changed: [welktxef-931881-rh-le0e910-005 -> localhost]

TASK [hpe/mac-discover : Copy mac discovery scripts to working dir] ******************************************************************************************************************
changed: [welktxef-931881-rh-le0e910-005 -> localhost] => (item={'filename': 'get_resource_directory.py', 'value': '#!/usr/bin/env python\n\nfrom __future__ import print_function\nimport argparse\nimport ipaddress\nimport yaml\nfrom redfish import RedfishClient as RedfishClient\nimport os\nimport sys\nfrom redfish.rest.v1 import ServerDownOrUnreachableError\n\ndef get_resource_directory_profile():\n    cwd = os.path.dirname(os.path.abspath(__file__))\n    profile_name = "%s/hp_hw_profile.yaml" % cwd\n    try:\n        with open(profile_name) as file:\n            return yaml.load(file, Loader=yaml.FullLoader)["resource_directory"]\n    except IOError:\n        print("Error opening %s" % profile_name)\n        sys.exit(2)\n\ndef get_resource_directory(redfish_obj):\n    profile = get_resource_directory_profile()\n    response = redfish_obj.get(profile["url"])\n    resources = None\n    if response.status == 200:\n        resources = response.dict[profile["section"]]\n    else:\n        sys.stderr.write("\\tResource directory missing at %s\\n" % profile["url"])\n        sys.exit(2)\n    return resources\n\nif __name__ == "__main__":\n    parser = argparse.ArgumentParser(description="get resource directory script")\n    parser.add_argument("-n", dest="ip", required=True, help="The BMC IP address")\n    parser.add_argument("-u", dest="user", required=True, help="The BMC username")\n    parser.add_argument("-p", dest="passwd", required=True, help="The BMC password")\n    args = parser.parse_args()\n    ip = args.ip\n    login_account = args.user\n    login_password = args.passwd\n    ip_adar_type = ipaddress.ip_address(ip)\n    if type(ip_adar_type) == ipaddress.IPv4Address:\n        system_url = "https://" + ip + ""\n    else:\n        system_url = "https://[" + ip + "]"\n    redfish_obj = None\n    try:\n        redfish_obj = RedfishClient(base_url=system_url, username=login_account, password=XXXXXX        redfish_obj.login()\n    except ServerDownOrUnreachableError:\n        sys.stderr.write("ERROR: server not reachable or doesn\'t support Redfish.\\n")\n        sys.exit(2)\n    get_resource_directory(redfish_obj)\n    sys.exit(0)\n'})
changed: [welktxef-931881-rh-le0e910-005 -> localhost] => (item={'filename': 'hp_hw_profile.yaml', 'value': '---\nresource_directory:\n  url: /redfish/v1/resourcedirectory\n  section: Instances\n'})

TASK [hpe/mac-discover : Copy MAC address discovery scripts to working dir] **********************************************************************************************************
changed: [welktxef-931881-rh-le0e910-005 -> localhost] => (item=find_ilo_mac_address.py)
changed: [welktxef-931881-rh-le0e910-005 -> localhost] => (item=ls3_92s3_find_ilo_mac_address.py)
changed: [welktxef-931881-rh-le0e910-005 -> localhost] => (item=ls6_find_ilo_mac_address.py)
changed: [welktxef-931881-rh-le0e910-005 -> localhost] => (item=930t_find_ilo_mac_address.py)

TASK [hpe/mac-discover : Execute MAC address discovery script for HPE-LS3-e910] ******************************************************************************************************
changed: [welktxef-931881-rh-le0e910-005 -> localhost]

TASK [hpe/mac-discover : MAC address discovery (result) for HPE-LS3-e910] ************************************************************************************************************
ok: [welktxef-931881-rh-le0e910-005] => {
    "msg": "mac address:d4:f5:ef:55:13:98 firmware:1.3353.0"
}

TASK [hpe/mac-discover : Execute MAC address discovery script for HPE-LS3-92s3] ******************************************************************************************************
skipping: [welktxef-931881-rh-le0e910-005]

TASK [hpe/mac-discover : MAC address discovery (result) for HPE-LS3-92s3] ************************************************************************************************************
skipping: [welktxef-931881-rh-le0e910-005]

TASK [hpe/mac-discover : Execute MAC address discovery script for HPE-LS6-92s6] ******************************************************************************************************
skipping: [welktxef-931881-rh-le0e910-005]

TASK [hpe/mac-discover : MAC address discovery (result) for HPE-LS6-92s6] ************************************************************************************************************
skipping: [welktxef-931881-rh-le0e910-005]

TASK [hpe/mac-discover : Execute MAC address discovery script for HPE-LS3-e910] ******************************************************************************************************
skipping: [welktxef-931881-rh-le0e910-005]

TASK [hpe/mac-discover : MAC address discovery (result) for HPE-LS3-e910] ************************************************************************************************************
skipping: [welktxef-931881-rh-le0e910-005]

TASK [hpe/mac-discover : Remove temporary working directory] *************************************************************************************************************************
changed: [welktxef-931881-rh-le0e910-005 -> localhost]

TASK [hpe/mac-discover : Push MAC address to middleware] *****************************************************************************************************************************
ok: [welktxef-931881-rh-le0e910-005 -> localhost]

TASK [hpe/mac-discover : Push MAC address to middleware] *****************************************************************************************************************************
skipping: [welktxef-931881-rh-le0e910-005]

TASK [hpe/mac-discover : Push MAC address to middleware] *****************************************************************************************************************************
skipping: [welktxef-931881-rh-le0e910-005]

TASK [hpe/mac-discover : Push MAC address to middleware] *****************************************************************************************************************************
skipping: [welktxef-931881-rh-le0e910-005]

TASK [include_role : hpe/bios-config] ************************************************************************************************************************************************
[WARNING]: Collection community.general does not support Ansible version 2.12.10

TASK [hpe/bios-config : Create temporary working directory] **************************************************************************************************************************
changed: [welktxef-931881-rh-le0e910-005 -> localhost]

TASK [hpe/bios-config : Copy bios changing scripts to working dir] *******************************************************************************************************************
changed: [welktxef-931881-rh-le0e910-005 -> localhost] => (item={'filename': 'get_resource_directory.py', 'value': '#!/usr/bin/env python\n\nfrom __future__ import print_function\nimport argparse\nimport ipaddress\nimport yaml\nfrom redfish import RedfishClient as RedfishClient\nimport os\nimport sys\nfrom redfish.rest.v1 import ServerDownOrUnreachableError\n\ndef get_resource_directory_profile():\n    cwd = os.path.dirname(os.path.abspath(__file__))\n    profile_name = "%s/hp_hw_profile.yaml" % cwd\n    try:\n        with open(profile_name) as file:\n            return yaml.load(file, Loader=yaml.FullLoader)["resource_directory"]\n    except IOError:\n        print("Error opening %s" % profile_name)\n        sys.exit(2)\n\ndef get_resource_directory(redfish_obj):\n    profile = get_resource_directory_profile()\n    response = redfish_obj.get(profile["url"])\n    resources = None\n    if response.status == 200:\n        resources = response.dict[profile["section"]]\n    else:\n        sys.stderr.write("\\tResource directory missing at %s\\n" % profile["url"])\n        sys.exit(2)\n    return resources\n\nif __name__ == "__main__":\n    parser = argparse.ArgumentParser(description="get resource directory script")\n    parser.add_argument("-n", dest="ip", required=True, help="The BMC IP address")\n    parser.add_argument("-u", dest="user", required=True, help="The BMC username")\n    parser.add_argument("-p", dest="passwd", required=True, help="The BMC password")\n    args = parser.parse_args()\n    ip = args.ip\n    login_account = args.user\n    login_password = args.passwd\n    ip_adar_type = ipaddress.ip_address(ip)\n    if type(ip_adar_type) == ipaddress.IPv4Address:\n        system_url = "https://" + ip + ""\n    else:\n        system_url = "https://[" + ip + "]"\n    redfish_obj = None\n    try:\n        redfish_obj = RedfishClient(base_url=system_url, username=login_account, password=XXXXXX        redfish_obj.login()\n    except ServerDownOrUnreachableError:\n        sys.stderr.write("ERROR: server not reachable or doesn\'t support Redfish.\\n")\n        sys.exit(2)\n    get_resource_directory(redfish_obj)\n    sys.exit(0)\n'})
changed: [welktxef-931881-rh-le0e910-005 -> localhost] => (item={'filename': 'hp_hw_profile.yaml', 'value': '---\nresource_directory:\n  url: /redfish/v1/resourcedirectory\n  section: Instances\n'})

TASK [hpe/bios-config : Copy HPE python scripts to working dir] **********************************************************************************************************************
changed: [welktxef-931881-rh-le0e910-005 -> localhost] => (item=enable_secure_boot.py)
changed: [welktxef-931881-rh-le0e910-005 -> localhost] => (item=disable_dhcp.py)
changed: [welktxef-931881-rh-le0e910-005 -> localhost] => (item=configure_dns.py)
changed: [welktxef-931881-rh-le0e910-005 -> localhost] => (item=configure_syslog.py)
changed: [welktxef-931881-rh-le0e910-005 -> localhost] => (item=disable_dhcp_ntp.py)
changed: [welktxef-931881-rh-le0e910-005 -> localhost] => (item=set_ilo_sntp_servers.py)

TASK [Power on the system] ***********************************************************************************************************************************************************

TASK [hpe/system-on : Check server power status] *************************************************************************************************************************************
ok: [welktxef-931881-rh-le0e910-005 -> localhost]

TASK [hpe/system-on : Power on server] ***********************************************************************************************************************************************
skipping: [welktxef-931881-rh-le0e910-005]

TASK [hpe/system-on : Wait for HPE server to start] **********************************************************************************************************************************
skipping: [welktxef-931881-rh-le0e910-005]

TASK [hpe/system-on : Wait for system to complete POST after power on] ***************************************************************************************************************
skipping: [welktxef-931881-rh-le0e910-005]

TASK [hpe/bios-config : Check if system is ready for BIOS configuration changes (part 1)] ********************************************************************************************
ok: [welktxef-931881-rh-le0e910-005 -> localhost]

TASK [hpe/bios-config : Get Bios Settings] *******************************************************************************************************************************************
ok: [welktxef-931881-rh-le0e910-005 -> localhost]

TASK [hpe/bios-config : Set HPE BIOS configuration attribute (part 1)] ***************************************************************************************************************
skipping: [welktxef-931881-rh-le0e910-005]

TASK [hpe/bios-config : Display HPE BIOS configuration attribute (part 1) result] ****************************************************************************************************
skipping: [welktxef-931881-rh-le0e910-005]

TASK [hpe/bios-config : Execute HPE secure boot script] ******************************************************************************************************************************
skipping: [welktxef-931881-rh-le0e910-005]

TASK [hpe/bios-config : Display output] **********************************************************************************************************************************************
skipping: [welktxef-931881-rh-le0e910-005]

TASK [Power off the system] **********************************************************************************************************************************************************
skipping: [welktxef-931881-rh-le0e910-005]

TASK [Power on the system] ***********************************************************************************************************************************************************
skipping: [welktxef-931881-rh-le0e910-005]

TASK [hpe/bios-config : Set HPE BIOS configuration attribute (part 2)] ***************************************************************************************************************
skipping: [welktxef-931881-rh-le0e910-005]

TASK [hpe/bios-config : Display HPE BIOS configuration attribute (part 2) result] ****************************************************************************************************
skipping: [welktxef-931881-rh-le0e910-005]

TASK [hpe/bios-config : Set HPE BIOS configuration attribute - HPE ILO v2.97 & CAAS v22.12] ******************************************************************************************
skipping: [welktxef-931881-rh-le0e910-005]

TASK [hpe/bios-config : Set HPE BIOS configuration attribute - HPE ILO v2.97 & CAAS v22.12 & MR1] ************************************************************************************
skipping: [welktxef-931881-rh-le0e910-005]

TASK [hpe/bios-config : Set HPE BIOS configuration attribute - HPE ILO v2.97 & CAAS v22.12 & MR2] ************************************************************************************
skipping: [welktxef-931881-rh-le0e910-005]

TASK [hpe/bios-config : Display HPE BIOS configuration attribute] ********************************************************************************************************************
skipping: [welktxef-931881-rh-le0e910-005]

TASK [hpe/bios-config : Execute HPE secure boot script] ******************************************************************************************************************************
skipping: [welktxef-931881-rh-le0e910-005]

TASK [hpe/bios-config : Display output] **********************************************************************************************************************************************
skipping: [welktxef-931881-rh-le0e910-005]

TASK [hpe/bios-config : Execute HPE disable DHCP script] *****************************************************************************************************************************
changed: [welktxef-931881-rh-le0e910-005 -> localhost]

TASK [hpe/bios-config : Display output] **********************************************************************************************************************************************
ok: [welktxef-931881-rh-le0e910-005] => {
    "result.stdout": "Disabled DHCP on Ethernet Interfaces Successfully!"
}

TASK [hpe/bios-config : Execute HPE configure DNS script] ****************************************************************************************************************************
changed: [welktxef-931881-rh-le0e910-005 -> localhost]

TASK [hpe/bios-config : Display output] **********************************************************************************************************************************************
ok: [welktxef-931881-rh-le0e910-005] => {
    "result.stdout": "Configured DNS on Ethernet Interfaces Successfully!"
}

TASK [hpe/bios-config : Execute HPE configure remote syslog script] ******************************************************************************************************************
changed: [welktxef-931881-rh-le0e910-005 -> localhost]

TASK [hpe/bios-config : Display output] **********************************************************************************************************************************************
ok: [welktxef-931881-rh-le0e910-005] => {
    "result.stdout": "Configured Remote  on Ethernet Interfaces Successfully!"
}

TASK [hpe/bios-config : Execute HPE disable DHCP NTP servers script] *****************************************************************************************************************
changed: [welktxef-931881-rh-le0e910-005 -> localhost]

TASK [hpe/bios-config : Display output] **********************************************************************************************************************************************
ok: [welktxef-931881-rh-le0e910-005] => {
    "result.stdout": "Success!"
}

TASK [hpe/bios-config : Execute HPE configure SNTP servers script] *******************************************************************************************************************
changed: [welktxef-931881-rh-le0e910-005 -> localhost]

TASK [hpe/bios-config : Display output] **********************************************************************************************************************************************
ok: [welktxef-931881-rh-le0e910-005] => {
    "result.stdout": "Success!"
}

TASK [hpe/bios-config : Disable IPv4 use domain setting] *****************************************************************************************************************************
ok: [welktxef-931881-rh-le0e910-005 -> localhost]

TASK [Reset HPE ILO] *****************************************************************************************************************************************************************

TASK [hpe/ilo-reset : Reset ILO] *****************************************************************************************************************************************************
ok: [welktxef-931881-rh-le0e910-005 -> localhost]

TASK [hpe/ilo-reset : Wait for HPE ILO to reset] *************************************************************************************************************************************
Pausing for 30 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [welktxef-931881-rh-le0e910-005]

TASK [hpe/ilo-reset : Check redfish health after ILO reset] **************************************************************************************************************************
FAILED - RETRYING: [welktxef-931881-rh-le0e910-005 -> localhost]: Check redfish health after ILO reset (6 retries left).
ok: [welktxef-931881-rh-le0e910-005 -> localhost]

TASK [hpe/bios-config : Remove temporary working directory] **************************************************************************************************************************
changed: [welktxef-931881-rh-le0e910-005 -> localhost]

TASK [Power off the system] **********************************************************************************************************************************************************

TASK [hpe/system-off : Check server power status] ************************************************************************************************************************************
ok: [welktxef-931881-rh-le0e910-005 -> localhost]

TASK [hpe/system-off : Power off server] *********************************************************************************************************************************************
ok: [welktxef-931881-rh-le0e910-005 -> localhost]

TASK [hpe/system-off : Wait for HPE server to shut down] *****************************************************************************************************************************
Pausing for 10 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [welktxef-931881-rh-le0e910-005]

TASK [Power on the system] ***********************************************************************************************************************************************************

TASK [hpe/system-on : Check server power status] *************************************************************************************************************************************
ok: [welktxef-931881-rh-le0e910-005 -> localhost]

TASK [hpe/system-on : Power on server] ***********************************************************************************************************************************************
ok: [welktxef-931881-rh-le0e910-005 -> localhost]

TASK [hpe/system-on : Wait for HPE server to start] **********************************************************************************************************************************
Pausing for 120 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [welktxef-931881-rh-le0e910-005]

TASK [hpe/system-on : Wait for system to complete POST after power on] ***************************************************************************************************************
ok: [welktxef-931881-rh-le0e910-005 -> localhost]

TASK [hpe/bios-config : Get Bios Settings] *******************************************************************************************************************************************
ok: [welktxef-931881-rh-le0e910-005 -> localhost]

TASK [hpe/bios-config : Fail when BIOS attributes are not set correctly] *************************************************************************************************************
skipping: [welktxef-931881-rh-le0e910-005]

TASK [hpe/bios-config : Fail when BIOS attributes are not set correctly - HPE ILO v2.97 & CAAS v22.12] *******************************************************************************
skipping: [welktxef-931881-rh-le0e910-005]

TASK [include_role : hpe/system-off] *************************************************************************************************************************************************

TASK [hpe/system-off : Check server power status] ************************************************************************************************************************************
ok: [welktxef-931881-rh-le0e910-005 -> localhost]

TASK [hpe/system-off : Power off server] *********************************************************************************************************************************************
ok: [welktxef-931881-rh-le0e910-005 -> localhost]

TASK [hpe/system-off : Wait for HPE server to shut down] *****************************************************************************************************************************
Pausing for 10 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [welktxef-931881-rh-le0e910-005]

TASK [include_role : hpe/ilo-hostname] ***********************************************************************************************************************************************

TASK [hpe/ilo-hostname : Change host name for iLO interface] *************************************************************************************************************************
ok: [welktxef-931881-rh-le0e910-005 -> localhost]

TASK [include_role : hpe/host-name] **************************************************************************************************************************************************

TASK [hpe/host-name : Change host name for iLO events] *******************************************************************************************************************************
ok: [welktxef-931881-rh-le0e910-005 -> localhost]

TASK [hpe/host-name : Change FQDN for iLO events] ************************************************************************************************************************************
ok: [welktxef-931881-rh-le0e910-005 -> localhost]

TASK [include_role : hpe/syslog-disable] *********************************************************************************************************************************************

TASK [hpe/syslog-disable : Disable Remote Syslog] ************************************************************************************************************************************
ok: [welktxef-931881-rh-le0e910-005 -> localhost]

TASK [include_role : hpe/subscribe-redfish-events] ***********************************************************************************************************************************

TASK [hpe/subscribe-redfish-events : Set facts to subscribe events for HPE servers] **************************************************************************************************
ok: [welktxef-931881-rh-le0e910-005]

TASK [hpe/subscribe-redfish-events : Get Event subscription count] *******************************************************************************************************************
ok: [welktxef-931881-rh-le0e910-005 -> localhost]

TASK [hpe/subscribe-redfish-events : Delete existing subscriptions] ******************************************************************************************************************

TASK [hpe/subscribe-redfish-events : Subscribe to Redfish Alarms] ********************************************************************************************************************
ok: [welktxef-931881-rh-le0e910-005 -> localhost]

TASK [hpe/subscribe-redfish-events : Subscribe to Redfish Alarms - HPE 930] **********************************************************************************************************
skipping: [welktxef-931881-rh-le0e910-005]

TASK [include_role : hpe/system-on] **************************************************************************************************************************************************

TASK [hpe/system-on : Check server power status] *************************************************************************************************************************************
ok: [welktxef-931881-rh-le0e910-005 -> localhost]

TASK [hpe/system-on : Power on server] ***********************************************************************************************************************************************
ok: [welktxef-931881-rh-le0e910-005 -> localhost]

TASK [hpe/system-on : Wait for HPE server to start] **********************************************************************************************************************************
Pausing for 120 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [welktxef-931881-rh-le0e910-005]

TASK [hpe/system-on : Wait for system to complete POST after power on] ***************************************************************************************************************
ok: [welktxef-931881-rh-le0e910-005 -> localhost]

TASK [Report success status to middleware] *******************************************************************************************************************************************

TASK [playbook-status-report : Set facts for playbook] *******************************************************************************************************************************
ok: [welktxef-931881-rh-le0e910-005]

TASK [playbook-status-report : Print message if install succeeded] *******************************************************************************************************************
ok: [welktxef-931881-rh-le0e910-005] => {
    "msg": [
        "================================================================",
        " welktxef-d931881-005: Playbook SUCCEEDED! ",
        " playbook: wrapper_bmc.yaml",
        "================================================================"
    ]
}

TASK [playbook-status-report : Print message if install failed] **********************************************************************************************************************
skipping: [welktxef-931881-rh-le0e910-005]

TASK [playbook-status-report : Report status to middleware when success] *************************************************************************************************************
ok: [welktxef-931881-rh-le0e910-005 -> localhost]

TASK [playbook-status-report : include_tasks] ****************************************************************************************************************************************
skipping: [welktxef-931881-rh-le0e910-005]

TASK [playbook-status-report : Get failed job retry count] ***************************************************************************************************************************
skipping: [welktxef-931881-rh-le0e910-005]

TASK [playbook-status-report : display fail_query] ***********************************************************************************************************************************
skipping: [welktxef-931881-rh-le0e910-005]

TASK [playbook-status-report : Set failure count] ************************************************************************************************************************************
skipping: [welktxef-931881-rh-le0e910-005]

TASK [playbook-status-report : Report status to middleware when warning] *************************************************************************************************************
skipping: [welktxef-931881-rh-le0e910-005]

TASK [playbook-status-report : Report status to middleware when failure after remediate] *********************************************************************************************
skipping: [welktxef-931881-rh-le0e910-005]

TASK [playbook-status-report : Report status to middleware when failure] *************************************************************************************************************
skipping: [welktxef-931881-rh-le0e910-005]

PLAY RECAP ***************************************************************************************************************************************************************************
welktxef-931881-rh-le0e910-005 : ok=71   changed=19   unreachable=0    failed=0    skipped=61   rescued=0    ignored=0

(atlas) szabota@welktxefnce-h-pe1util-vm05:~/playbooks/bmc-workloadprofile/bmc$
```


## Bmc playbook worked, server has been configured as per the playbook