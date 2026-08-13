# HPE ILO6 1.57 BIOS H11 v1.11
# HPE Sapphire Rapids E930t server
# 3/24/24 James Patchett - MTCE Lab VCPfe
# BMC Playbook MEAKV-1793

## welktxsr-931883-rh-le093s6-001
ILO:  2607:f160:10:80b1:ce:40a:0:e002
OAM:  2607:f160:10:80b1:ce:40a:0:f402

## Subcloud welktxsr-d931883-001
## General info before we start

```log
XXXXXX@controller-0:~$ source /etc/platform/openrc
[XXXXXX@controller-0 ~(keystone_admin)]$ system show
+------------------------+--------------------------------------+
| Property               | Value                                |
+------------------------+--------------------------------------+
| contact                | None                                 |
| created_at             | 2024-03-21T18:58:05.425483+00:00     |
| description            | None                                 |
| distributed_cloud_role | subcloud                             |
| https_enabled          | True                                 |
| latitude               | None                                 |
| location               | None                                 |
| longitude              | None                                 |
| name                   | welktxsr-d931883-001                 |
| region_name            | welktxsr-d931883-001                 |
| sdn_enabled            | False                                |
| security_feature       | spectre_meltdown_v1                  |
| service_project_name   | services                             |
| shared_services        | []                                   |
| software_version       | 22.12                                |
| system_mode            | simplex                              |
| system_type            | All-in-one                           |
| timezone               | UTC                                  |
| updated_at             | 2024-03-26T18:48:17.340880+00:00     |
| uuid                   | 158d0999-7bda-4663-a51f-7576c175117f |
| vswitch_type           | none                                 |
+------------------------+--------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ system oam-show
+----------------+---------------------------------------+
| Property       | Value                                 |
+----------------+---------------------------------------+
| created_at     | 2024-03-21T18:59:47.482500+00:00      |
| isystem_uuid   | 158d0999-7bda-4663-a51f-7576c175117f  |
| oam_end_ip     | 2607:f160:10:80b1:ffff:ffff:ffff:fffe |
| oam_gateway_ip | 2607:f160:10:80b1:ce:23::             |
| oam_ip         | 2607:f160:10:80b1:ce:40a:0:f402       |
| oam_start_ip   | 2607:f160:10:80b1::1                  |
| oam_subnet     | 2607:f160:10:80b1::/64                |
| updated_at     | None                                  |
| uuid           | 45723e45-0576-4cda-9d26-7a70682b972c  |
+----------------+---------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ system application-list
+--------------------------+----------+-------------------------------------------+------------------+---------+-----------+
| application              | version  | manifest name                             | manifest file    | status  | progress  |
+--------------------------+----------+-------------------------------------------+------------------+---------+-----------+
| cert-manager             | 22.12-8  | cert-manager-fluxcd-manifests             | fluxcd-manifests | applied | completed |
| metrics-server           | 22.12-1  | metrics-server-fluxcd-manifests           | fluxcd-manifests | applied | completed |
| nginx-ingress-controller | 22.12-1  | nginx-ingress-controller-fluxcd-manifests | fluxcd-manifests | applied | completed |
| oidc-auth-apps           | 22.12-6  | oidc-auth-apps-fluxcd-manifests           | fluxcd-manifests | applied | completed |
| platform-integ-apps      | 22.12-66 | platform-integ-apps-fluxcd-manifests      | fluxcd-manifests | applied | completed |
| ptp-notification         | 22.      | ptp-notification-fluxcd-manifests         | fluxcd-manifests | applied | completed |
|                          | 12-138   |                                           |                  |         |           |
|                          |          |                                           |                  |         |           |
| sriov-fec-operator       | 22.12-3  | sriov-fec-operator-fluxcd-manifests       | fluxcd-manifests | applied | completed |
| wr-analytics             | 23.09-0  | wr-analytics-fluxcd-manifests             | fluxcd-manifests | applied | completed |
+--------------------------+----------+-------------------------------------------+------------------+---------+-----------+
[XXXXXX@controller-0 ~(keystone_admin)]$ sw-patch query
      Patch ID         RR  Release  Patch State
=====================  ==  =======  ===========
WRCP_22.12_PATCH_0001  Y    22.12    Committed
WRCP_22.12_PATCH_0002  Y    22.12    Committed
WRCP_22.12_PATCH_0003  Y    22.12    Committed
WRCP_22.12_PATCH_0004  Y    22.12     Applied

[XXXXXX@controller-0 ~(keystone_admin)]$ fm alarm-list
+----------+-------------------------------------------------------+--------------------+----------+--------------+
| Alarm ID | Reason Text                                           | Entity ID          | Severity | Time Stamp   |
+----------+-------------------------------------------------------+--------------------+----------+--------------+
| 100.119  | controller-0 is not locked to remote PTP Grand Master | host=controller-0. | major    | 2024-03-26T1 |
|          |                                                       | instance=ptp4l-    |          | 8:48:42.     |
|          |                                                       | legacy-2.ptp=no-   |          | 707911       |
|          |                                                       | lock               |          |              |
|          |                                                       |                    |          |              |
| 100.119  | controller-0 is not locked to remote PTP Grand Master | host=controller-0. | major    | 2024-03-26T1 |
|          |                                                       | instance=ptp4l-    |          | 8:48:42.     |
|          |                                                       | legacy.ptp=no-lock |          | 036900       |
|          |                                                       |                    |          |              |
+----------+-------------------------------------------------------+--------------------+----------+--------------+
[XXXXXX@controller-0 ~(keystone_admin)]$


```



## MEAKV-1793 BMC Playbook run against the ILO
## BMC Playbook required many modifications for it to work with the e930t Sapphire rapids server.
## a Fork of BMC playbook "atlas" branch was created as "bmc-sapphire-rapids" and will be pushed back to gitlab for Baris to incoporate into production playbook.

```log

szabota@welktxefnce-h-pe1util-vm05:~/playbooks/bmc-sapphire-rapids/bmc$ source ~/python_venvs/atlas/bin/activate
(atlas) szabota@welktxefnce-h-pe1util-vm05:~/playbooks/bmc-sapphire-rapids/bmc$ ansible-playbook --vault-password-file ./vault.txt -i inventory/welktxsr-931883-rh-le093s6-012.yaml bmc.yaml

PLAY [BMC configuration playbook] ******************************************************************************************************************

TASK [Initialize me environment variable] **********************************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [Initialize prod environment variable] ********************************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : zts/enable-ssh] ***************************************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : zts/clear_sel_logs] ***********************************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : zts/check_model] **************************************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : zts/upgrade_ls3] **************************************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : zts/upgrade_ls6] **************************************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : zts/disable_pam_auth] *********************************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : zts/configure-ipv4] ***********************************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : zts/account-create] ***********************************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : zts/mac-discover] *************************************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : zts/system-off] ***************************************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : zts/bios-config] **************************************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : zts/host-name] ****************************************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : zts/configure-dns] ************************************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : zts/configure-ntp] ************************************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : zts/subscribe-redfish-events] *************************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : zts/system-on] ****************************************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : hpe/check_model] **************************************************************************************************************

TASK [hpe/check_model : Get server model] **********************************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/check_model : Set server model] **********************************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012]

TASK [hpe/check_model : Display model name] ********************************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012] => {
    "model_name": "Edgeline e930t"
}

TASK [hpe/check_model : Fail when model specifier substring in hostname does not match the actual model name] **************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : hpe/upgrade_ls3] **************************************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : hpe/upgrade_ls6] **************************************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : hpe/account-create] ***********************************************************************************************************

TASK [hpe/account-create : Create temporary working directory] *************************************************************************************
changed: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/account-create : Copy HPE account creation scripts to working dir] ***********************************************************************
changed: [welktxsr-931883-rh-le093s6-012 -> localhost] => (item={'filename': 'get_resource_directory.py', 'value': '#!/usr/bin/env python\n\nfrom __future__ import print_function\nimport argparse\nimport ipaddress\nimport yaml\nfrom redfish import RedfishClient as RedfishClient\nimport os\nimport sys\nfrom redfish.rest.v1 import ServerDownOrUnreachableError\n\ndef get_resource_directory_profile():\n    cwd = os.path.dirname(os.path.abspath(__file__))\n    profile_name = "%s/hp_hw_profile.yaml" % cwd\n    try:\n        with open(profile_name) as file:\n            return yaml.load(file, Loader=yaml.FullLoader)["resource_directory"]\n    except IOError:\n        print("Error opening %s" % profile_name)\n        sys.exit(2)\n\ndef get_resource_directory(redfish_obj):\n    profile = get_resource_directory_profile()\n    response = redfish_obj.get(profile["url"])\n    resources = None\n    if response.status == 200:\n        resources = response.dict[profile["section"]]\n    else:\n        sys.stderr.write("\\tResource directory missing at %s\\n" % profile["url"])\n        sys.exit(2)\n    return resources\n\nif __name__ == "__main__":\n    parser = argparse.ArgumentParser(description="get resource directory script")\n    parser.add_argument("-n", dest="ip", required=True, help="The BMC IP address")\n    parser.add_argument("-u", dest="user", required=True, help="The BMC username")\n    parser.add_argument("-p", dest="passwd", required=True, help="The BMC password")\n    args = parser.parse_args()\n    ip = args.ip\n    login_account = args.user\n    login_password = args.passwd\n    ip_adar_type = ipaddress.ip_address(ip)\n    if type(ip_adar_type) == ipaddress.IPv4Address:\n        system_url = "https://" + ip + ""\n    else:\n        system_url = "https://[" + ip + "]"\n    redfish_obj = None\n    try:\n        redfish_obj = RedfishClient(base_url=system_url, username=login_account, password=XXXXXX        redfish_obj.login()\n    except ServerDownOrUnreachableError:\n        sys.stderr.write("ERROR: server not reachable or doesn\'t support Redfish.\\n")\n        sys.exit(2)\n    get_resource_directory(redfish_obj)\n    sys.exit(0)\n'})
changed: [welktxsr-931883-rh-le093s6-012 -> localhost] => (item={'filename': 'hp_hw_profile.yaml', 'value': '---\nresource_directory:\n  url: /redfish/v1/resourcedirectory\n  section: Instances\n'})

TASK [hpe/account-create : Copy HPE account creation scripts to working dir] ***********************************************************************
changed: [welktxsr-931883-rh-le093s6-012 -> localhost] => (item=add_user_account.py)

TASK [hpe/account-create : Execute HPE account creation script] ************************************************************************************
changed: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/account-create : Remove temporary working directory] *************************************************************************************
changed: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [include_role : hpe/mac-discover] *************************************************************************************************************

TASK [hpe/mac-discover : Create temporary working directory] ***************************************************************************************
changed: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/mac-discover : Copy mac discovery scripts to working dir] ********************************************************************************
changed: [welktxsr-931883-rh-le093s6-012 -> localhost] => (item={'filename': 'get_resource_directory.py', 'value': '#!/usr/bin/env python\n\nfrom __future__ import print_function\nimport argparse\nimport ipaddress\nimport yaml\nfrom redfish import RedfishClient as RedfishClient\nimport os\nimport sys\nfrom redfish.rest.v1 import ServerDownOrUnreachableError\n\ndef get_resource_directory_profile():\n    cwd = os.path.dirname(os.path.abspath(__file__))\n    profile_name = "%s/hp_hw_profile.yaml" % cwd\n    try:\n        with open(profile_name) as file:\n            return yaml.load(file, Loader=yaml.FullLoader)["resource_directory"]\n    except IOError:\n        print("Error opening %s" % profile_name)\n        sys.exit(2)\n\ndef get_resource_directory(redfish_obj):\n    profile = get_resource_directory_profile()\n    response = redfish_obj.get(profile["url"])\n    resources = None\n    if response.status == 200:\n        resources = response.dict[profile["section"]]\n    else:\n        sys.stderr.write("\\tResource directory missing at %s\\n" % profile["url"])\n        sys.exit(2)\n    return resources\n\nif __name__ == "__main__":\n    parser = argparse.ArgumentParser(description="get resource directory script")\n    parser.add_argument("-n", dest="ip", required=True, help="The BMC IP address")\n    parser.add_argument("-u", dest="user", required=True, help="The BMC username")\n    parser.add_argument("-p", dest="passwd", required=True, help="The BMC password")\n    args = parser.parse_args()\n    ip = args.ip\n    login_account = args.user\n    login_password = args.passwd\n    ip_adar_type = ipaddress.ip_address(ip)\n    if type(ip_adar_type) == ipaddress.IPv4Address:\n        system_url = "https://" + ip + ""\n    else:\n        system_url = "https://[" + ip + "]"\n    redfish_obj = None\n    try:\n        redfish_obj = RedfishClient(base_url=system_url, username=login_account, password=XXXXXX        redfish_obj.login()\n    except ServerDownOrUnreachableError:\n        sys.stderr.write("ERROR: server not reachable or doesn\'t support Redfish.\\n")\n        sys.exit(2)\n    get_resource_directory(redfish_obj)\n    sys.exit(0)\n'})
changed: [welktxsr-931883-rh-le093s6-012 -> localhost] => (item={'filename': 'hp_hw_profile.yaml', 'value': '---\nresource_directory:\n  url: /redfish/v1/resourcedirectory\n  section: Instances\n'})

TASK [hpe/mac-discover : Copy MAC address discovery scripts to working dir] ************************************************************************
changed: [welktxsr-931883-rh-le093s6-012 -> localhost] => (item=find_ilo_mac_address.py)
changed: [welktxsr-931883-rh-le093s6-012 -> localhost] => (item=ls3_92s3_find_ilo_mac_address.py)
changed: [welktxsr-931883-rh-le093s6-012 -> localhost] => (item=ls6_find_ilo_mac_address.py)
changed: [welktxsr-931883-rh-le093s6-012 -> localhost] => (item=930t_find_ilo_mac_address.py)

TASK [hpe/mac-discover : Execute MAC address discovery script for HPE-LS3-e910] ********************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [hpe/mac-discover : MAC address discovery (result) for HPE-LS3-e910] **************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [hpe/mac-discover : Execute MAC address discovery script for HPE-LS3-92s3] ********************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [hpe/mac-discover : MAC address discovery (result) for HPE-LS3-92s3] **************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [hpe/mac-discover : Execute MAC address discovery script for HPE-LS6-92s6] ********************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [hpe/mac-discover : MAC address discovery (result) for HPE-LS6-92s6] **************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [hpe/mac-discover : Execute MAC address discovery script for HPE-LS6-93s6] ********************************************************************
changed: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/mac-discover : MAC address discovery (result) for HPE-LS6-93s6] **************************************************************************
ok: [welktxsr-931883-rh-le093s6-012] => {
    "msg": "mac address:F0:B2:B9:14:38:B0 firmware:4.22 (0x8001A52F)"
}

TASK [hpe/mac-discover : Remove temporary working directory] ***************************************************************************************
changed: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/mac-discover : Push MAC address to middleware] *******************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [hpe/mac-discover : Push MAC address to middleware] *******************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [hpe/mac-discover : Push MAC address to middleware] *******************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [hpe/mac-discover : Push MAC address to middleware] *******************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [include_role : hpe/bios-config] **************************************************************************************************************

TASK [hpe/bios-config : Execute e910t e920t bios configs] ******************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [hpe/bios-config : Execute e930t bios config] *************************************************************************************************
[WARNING]: Collection community.general does not support Ansible version 2.12.10
included: /home/szabota/playbooks/bmc-sapphire-rapids/bmc/roles/hpe/bios-config/tasks/e930t.yaml for welktxsr-931883-rh-le093s6-012

TASK [hpe/bios-config : Create temporary working directory] ****************************************************************************************
changed: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/bios-config : Copy bios changing scripts to working dir] *********************************************************************************
changed: [welktxsr-931883-rh-le093s6-012 -> localhost] => (item={'filename': 'get_resource_directory.py', 'value': '#!/usr/bin/env python\n\nfrom __future__ import print_function\nimport argparse\nimport ipaddress\nimport yaml\nfrom redfish import RedfishClient as RedfishClient\nimport os\nimport sys\nfrom redfish.rest.v1 import ServerDownOrUnreachableError\n\ndef get_resource_directory_profile():\n    cwd = os.path.dirname(os.path.abspath(__file__))\n    profile_name = "%s/hp_hw_profile.yaml" % cwd\n    try:\n        with open(profile_name) as file:\n            return yaml.load(file, Loader=yaml.FullLoader)["resource_directory"]\n    except IOError:\n        print("Error opening %s" % profile_name)\n        sys.exit(2)\n\ndef get_resource_directory(redfish_obj):\n    profile = get_resource_directory_profile()\n    response = redfish_obj.get(profile["url"])\n    resources = None\n    if response.status == 200:\n        resources = response.dict[profile["section"]]\n    else:\n        sys.stderr.write("\\tResource directory missing at %s\\n" % profile["url"])\n        sys.exit(2)\n    return resources\n\nif __name__ == "__main__":\n    parser = argparse.ArgumentParser(description="get resource directory script")\n    parser.add_argument("-n", dest="ip", required=True, help="The BMC IP address")\n    parser.add_argument("-u", dest="user", required=True, help="The BMC username")\n    parser.add_argument("-p", dest="passwd", required=True, help="The BMC password")\n    args = parser.parse_args()\n    ip = args.ip\n    login_account = args.user\n    login_password = args.passwd\n    ip_adar_type = ipaddress.ip_address(ip)\n    if type(ip_adar_type) == ipaddress.IPv4Address:\n        system_url = "https://" + ip + ""\n    else:\n        system_url = "https://[" + ip + "]"\n    redfish_obj = None\n    try:\n        redfish_obj = RedfishClient(base_url=system_url, username=login_account, password=XXXXXX        redfish_obj.login()\n    except ServerDownOrUnreachableError:\n        sys.stderr.write("ERROR: server not reachable or doesn\'t support Redfish.\\n")\n        sys.exit(2)\n    get_resource_directory(redfish_obj)\n    sys.exit(0)\n'})
changed: [welktxsr-931883-rh-le093s6-012 -> localhost] => (item={'filename': 'hp_hw_profile.yaml', 'value': '---\nresource_directory:\n  url: /redfish/v1/resourcedirectory\n  section: Instances\n'})

TASK [hpe/bios-config : Copy HPE python scripts to working dir] ************************************************************************************
changed: [welktxsr-931883-rh-le093s6-012 -> localhost] => (item=enable_secure_boot.py)
changed: [welktxsr-931883-rh-le093s6-012 -> localhost] => (item=disable_dhcp.py)
changed: [welktxsr-931883-rh-le093s6-012 -> localhost] => (item=configure_dns.py)
changed: [welktxsr-931883-rh-le093s6-012 -> localhost] => (item=configure_syslog.py)
changed: [welktxsr-931883-rh-le093s6-012 -> localhost] => (item=disable_dhcp_ntp.py)
changed: [welktxsr-931883-rh-le093s6-012 -> localhost] => (item=set_ilo_sntp_servers.py)

TASK [Power on the system] *************************************************************************************************************************

TASK [hpe/system-on : Check server power status] ***************************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/system-on : Power on server] *************************************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [hpe/system-on : Wait for HPE server to start] ************************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [hpe/system-on : Wait for system to complete POST after power on] *****************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [hpe/bios-config : Check if system is ready for BIOS configuration changes (part 1)] **********************************************************
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/bios-config : Get Bios Settings] *********************************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/bios-config : Set HPE BIOS configuration attribute] **************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [hpe/bios-config : Display HPE BIOS configuration attribute e930t WorkloadProfile should be vRAN in the result] *******************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [hpe/bios-config : Execute HPE secure boot script] ********************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [hpe/bios-config : Display output] ************************************************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [hpe/bios-config : Execute HPE disable DHCP script] *******************************************************************************************
changed: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/bios-config : Display output] ************************************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012] => {
    "result.stdout": "Disabled DHCP on Ethernet Interfaces Successfully!"
}

TASK [hpe/bios-config : Execute HPE configure DNS script] ******************************************************************************************
changed: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/bios-config : Display output] ************************************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012] => {
    "result.stdout": "Configured DNS on Ethernet Interfaces Successfully!"
}

TASK [hpe/bios-config : Execute HPE configure remote syslog script] ********************************************************************************
changed: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/bios-config : Display output] ************************************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012] => {
    "result.stdout": "Configured Remote  on Ethernet Interfaces Successfully!"
}

TASK [hpe/bios-config : Execute HPE disable DHCP NTP servers script] *******************************************************************************
changed: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/bios-config : Display output] ************************************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012] => {
    "result.stdout": "Success!"
}

TASK [hpe/bios-config : Execute HPE configure SNTP servers script] *********************************************************************************
changed: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/bios-config : Display output] ************************************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012] => {
    "result.stdout": "Success!"
}

TASK [hpe/bios-config : Disable IPv4 use domain setting] *******************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [Reset HPE ILO] *******************************************************************************************************************************
TASK [hpe/ilo-reset : Reset ILO] *******************************************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/ilo-reset : Wait for HPE ILO to reset] ***************************************************************************************************
Pausing for 30 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [welktxsr-931883-rh-le093s6-012]

TASK [hpe/ilo-reset : Check redfish health after ILO reset] ****************************************************************************************
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Check redfish health after ILO reset (6 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Check redfish health after ILO reset (5 retries left).
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/bios-config : Remove temporary working directory] ****************************************************************************************
changed: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [Power off the system] ************************************************************************************************************************

TASK [hpe/system-off : Check server power status] **************************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/system-off : Power off server] ***********************************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/system-off : Wait for HPE server to shut down] *******************************************************************************************
Pausing for 10 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [welktxsr-931883-rh-le093s6-012]

TASK [Power on the system] *************************************************************************************************************************

TASK [hpe/system-on : Check server power status] ***************************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/system-on : Power on server] *************************************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/system-on : Wait for HPE server to start] ************************************************************************************************
Pausing for 120 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [welktxsr-931883-rh-le093s6-012]

TASK [hpe/system-on : Wait for system to complete POST after power on] *****************************************************************************
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (30 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (29 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (28 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (27 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (26 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (25 retries left).
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/bios-config : Get Bios Settings] *********************************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/bios-config : Fail when BIOS attributes are not set correctly] ***************************************************************************
skipping: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : hpe/system-off] ***************************************************************************************************************

TASK [hpe/system-off : Check server power status] **************************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/system-off : Power off server] ***********************************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/system-off : Wait for HPE server to shut down] *******************************************************************************************
Pausing for 10 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [welktxsr-931883-rh-le093s6-012]

TASK [include_role : hpe/ilo-hostname] *************************************************************************************************************

TASK [hpe/ilo-hostname : Change host name for iLO interface] ***************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [include_role : hpe/host-name] ****************************************************************************************************************

TASK [hpe/host-name : Change host name for iLO events] *********************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/host-name : Change FQDN for iLO events] **************************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [include_role : hpe/syslog-disable] ***********************************************************************************************************

TASK [hpe/syslog-disable : Disable Remote Syslog] **************************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [include_role : hpe/subscribe-redfish-events] *************************************************************************************************

TASK [hpe/subscribe-redfish-events : Set facts to subscribe events for HPE servers] ****************************************************************
ok: [welktxsr-931883-rh-le093s6-012]

TASK [hpe/subscribe-redfish-events : Get Event subscription count] *********************************************************************************
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/subscribe-redfish-events : Delete existing subscriptions] ********************************************************************************

TASK [hpe/subscribe-redfish-events : Subscribe to Redfish Alarms] **********************************************************************************
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [include_role : hpe/system-on] ****************************************************************************************************************

TASK [hpe/system-on : Check server power status] ***************************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/system-on : Power on server] *************************************************************************************************************
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [hpe/system-on : Wait for HPE server to start] ************************************************************************************************
Pausing for 120 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [welktxsr-931883-rh-le093s6-012]

TASK [hpe/system-on : Wait for system to complete POST after power on] *****************************************************************************
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (30 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (29 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (28 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (27 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (26 retries left).
FAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: Wait for system to complete POST after power on (25 retries left).
ok: [welktxsr-931883-rh-le093s6-012 -> localhost]

TASK [Report success status to middleware] *********************************************************************************************************
ERROR! couldn't resolve module/action 'postgresql_query'. This often indicates a misspelling, missing collection, or incorrect module path.

The error appears to be in '/home/szabota/playbooks/bmc-sapphire-rapids/bmc/roles/playbook-status-report/tasks/main.yaml': line 56, column 7, but may
be elsewhere in the file depending on the exact syntax problem.

The offending line appears to be:


    - name: Get failed job retry count
      ^ here

TASK [Report failure status to middleware] *********************************************************************************************************

PLAY RECAP *****************************************************************************************************************************************
welktxsr-931883-rh-le093s6-012 : ok=60   changed=19   unreachable=0    failed=0    skipped=39   rescued=0    ignored=0

(atlas) szabota@welktxefnce-h-pe1util-vm05:~/playbooks/bmc-sapphire-rapids/bmc$


```


## Bmc playbook worked.