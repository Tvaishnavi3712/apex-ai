E930t ILO6 integration differences
# James Patchett
# Date 4/18/24


## ILO5 versus ILO6 has many depricated URIs with redfish
## This document is detailing the changes that were needed in the BMC Playbook for e930t


## e920t old call based on HpeBaseNetworkAdapter, this has been depricated with e930t ilo6

```sh
curl -gsk -u XXXXXX:XXXXXX -X GET https://[$ILO]/redfish/v1/Systems/1/BaseNetworkAdapters/1 | jq .
```

```json
{
  "@odata.context": "/redfish/v1/$metadata#HpeBaseNetworkAdapter.HpeBaseNetworkAdapter",
  "@odata.etag": "W/\"CBB6E63F\"",
  "@odata.id": "/redfish/v1/Systems/1/BaseNetworkAdapters/1",
  "@odata.type": "#HpeBaseNetworkAdapter.v2_0_0.HpeBaseNetworkAdapter",
  "Id": "1",
  "FcPorts": [],
  "Firmware": {
    "Current": {
      "VersionString": "4.22 (0x80019C88)"
    }
  },
  "Location": "PCI-E Slot 1",
  "Name": "Intel(R) Eth E810-XXVDA4",
  "PartNumber": "N/A",
  "PhysicalPorts": [
    {
      "FullDuplex": false,
      "IPv4Addresses": [],
      "IPv6Addresses": [],
      "LinkStatus": "LinkUp",
      "MacAddress": "b4:96:91:c3:1f:e0",
      "Name": "",
      "Oem": {
        "Hpe": {
          "@odata.context": "/redfish/v1/$metadata#HpeBaseNetworkAdapterExt.HpeBaseNetworkAdapterExt",
          "@odata.type": "#HpeBaseNetworkAdapterExt.v2_0_0.HpeBaseNetworkAdapterExt",
          "BadReceives": 0,
          "BadTransmits": 0,
          "GoodReceives": 1211405,
          "GoodTransmits": 686170
        }
      },
      "SpeedMbps": 0,
      "Status": {
        "Health": "OK"
      }
    },
    {
      "FullDuplex": false,
      "IPv4Addresses": [],
      "IPv6Addresses": [],
      "LinkStatus": null,
      "MacAddress": "b4:96:91:c3:1f:e1",
      "Name": "",
      "Oem": {
        "Hpe": {
          "@odata.context": "/redfish/v1/$metadata#HpeBaseNetworkAdapterExt.HpeBaseNetworkAdapterExt",
          "@odata.type": "#HpeBaseNetworkAdapterExt.v2_0_0.HpeBaseNetworkAdapterExt",
          "BadReceives": 0,
          "BadTransmits": 0,
          "GoodReceives": 0,
          "GoodTransmits": 0
        }
      },
      "SpeedMbps": 0
    },
    {
      "FullDuplex": false,
      "IPv4Addresses": [],
      "IPv6Addresses": [],
      "LinkStatus": null,
      "MacAddress": "b4:96:91:c3:1f:e2",
      "Name": "",
      "Oem": {
        "Hpe": {
          "@odata.context": "/redfish/v1/$metadata#HpeBaseNetworkAdapterExt.HpeBaseNetworkAdapterExt",
          "@odata.type": "#HpeBaseNetworkAdapterExt.v2_0_0.HpeBaseNetworkAdapterExt",
          "BadReceives": 0,
          "BadTransmits": 0,
          "GoodReceives": 0,
          "GoodTransmits": 0
        }
      },
      "SpeedMbps": 0
    },
    {
      "FullDuplex": false,
      "IPv4Addresses": [],
      "IPv6Addresses": [],
      "LinkStatus": null,
      "MacAddress": "b4:96:91:c3:1f:e3",
      "Name": "",
      "Oem": {
        "Hpe": {
          "@odata.context": "/redfish/v1/$metadata#HpeBaseNetworkAdapterExt.HpeBaseNetworkAdapterExt",
          "@odata.type": "#HpeBaseNetworkAdapterExt.v2_0_0.HpeBaseNetworkAdapterExt",
          "BadReceives": 0,
          "BadTransmits": 0,
          "GoodReceives": 0,
          "GoodTransmits": 0
        }
      },
      "SpeedMbps": 0
    }
  ],
  "SerialNumber": "B49691C31FE0",
  "Status": {
    "Health": "OK",
    "State": "Enabled"
  },
  "StructuredName": "NIC.Slot.1.1",
  "UEFIDevicePath": "PciRoot(0x1)/Pci(0x2,0x0)/Pci(0x0,0x0)"
}
```

## E930t call to Network 



```log

(atlas) szabota@welktxefnce-h-pe1util-vm05:~/playbooks/bmc$ ansible-playbook -i inventory/welktxef-931884-rh-le092s6-034.yaml --vault-password ./vault.txt bmc.yaml

PLAY [BMC configuration playbook] *****************************************************************************************************

TASK [include_role : zts/enable-ssh] **************************************************************************************************
skipping: [welktxef-931884-rh-le092s6-034]

TASK [include_role : zts/check-redfish-health] ****************************************************************************************
skipping: [welktxef-931884-rh-le092s6-034]

TASK [include_role : zts/check_model] *************************************************************************************************
skipping: [welktxef-931884-rh-le092s6-034]

TASK [include_role : zts/disable_pam_auth] ********************************************************************************************
skipping: [welktxef-931884-rh-le092s6-034]

TASK [include_role : zts/upgrade_ls3] *************************************************************************************************
skipping: [welktxef-931884-rh-le092s6-034]

TASK [include_role : zts/upgrade_ls6] *************************************************************************************************
skipping: [welktxef-931884-rh-le092s6-034]

TASK [include_role : zts/disable_pam_auth] ********************************************************************************************
skipping: [welktxef-931884-rh-le092s6-034]

TASK [include_role : zts/configure-ipv4] **********************************************************************************************
skipping: [welktxef-931884-rh-le092s6-034]

TASK [include_role : zts/account-create] **********************************************************************************************
skipping: [welktxef-931884-rh-le092s6-034]

TASK [include_role : zts/mac-discover] ************************************************************************************************
skipping: [welktxef-931884-rh-le092s6-034]

TASK [include_role : zts/system-off] **************************************************************************************************
skipping: [welktxef-931884-rh-le092s6-034]

TASK [include_role : zts/bios-config] *************************************************************************************************
skipping: [welktxef-931884-rh-le092s6-034]

TASK [include_role : zts/host-name] ***************************************************************************************************
skipping: [welktxef-931884-rh-le092s6-034]

TASK [include_role : zts/configure-dns] ***********************************************************************************************
skipping: [welktxef-931884-rh-le092s6-034]

TASK [include_role : zts/configure-ntp] ***********************************************************************************************
skipping: [welktxef-931884-rh-le092s6-034]

TASK [include_role : zts/subscribe-redfish-events] ************************************************************************************
skipping: [welktxef-931884-rh-le092s6-034]

TASK [include_role : zts/system-on] ***************************************************************************************************
skipping: [welktxef-931884-rh-le092s6-034]

TASK [include_role : hpe/check_model] *************************************************************************************************

TASK [hpe/check_model : Get server model] *********************************************************************************************
ok: [welktxef-931884-rh-le092s6-034 -> localhost]

TASK [hpe/check_model : Set server model] *********************************************************************************************
ok: [welktxef-931884-rh-le092s6-034]

TASK [hpe/check_model : Display model name] *******************************************************************************************
ok: [welktxef-931884-rh-le092s6-034] => {
    "model_name": "Edgeline e920t"
}

TASK [hpe/check_model : Fail when model specifier substring in hostname does not match the actual model name] *************************
skipping: [welktxef-931884-rh-le092s6-034]

TASK [include_role : hpe/account-create] **********************************************************************************************

TASK [hpe/account-create : Create temporary working directory] ************************************************************************
changed: [welktxef-931884-rh-le092s6-034 -> localhost]

TASK [hpe/account-create : Copy HPE account creation scripts to working dir] **********************************************************
changed: [welktxef-931884-rh-le092s6-034 -> localhost] => (item={'filename': 'get_resource_directory.py', 'value': '#!/usr/bin/env python\n\nfrom __future__ import print_function\nimport argparse\nimport ipaddress\nimport yaml\nimport redfish\nimport os\nimport sys\nfrom redfish.rest.v1 import ServerDownOrUnreachableError\n\ndef get_resource_directory_profile():\n    cwd = os.path.dirname(os.path.abspath(__file__))\n    profile_name = "%s/hp_hw_profile.yaml" % cwd\n    try:\n        with open(profile_name) as file:\n            return yaml.load(file, Loader=yaml.FullLoader)["resource_directory"]\n    except IOError:\n        print("Error opening %s" % profile_name)\n        sys.exit(2)\n\ndef get_resource_directory(redfish_obj):\n    profile = get_resource_directory_profile()\n    response = redfish_obj.get(profile["url"])\n    resources = None\n    if response.status == 200:\n        resources = response.dict[profile["section"]]\n    else:\n        sys.stderr.write("\\tResource directory missing at %s\\n" % profile["url"])\n        sys.exit(2)\n    return resources\n\nif __name__ == "__main__":\n    parser = argparse.ArgumentParser(description="get resource directory script")\n    parser.add_argument("-n", dest="ip", required=True, help="The BMC IP address")\n    parser.add_argument("-u", dest="user", required=True, help="The BMC username")\n    parser.add_argument("-p", dest="passwd", required=True, help="The BMC password")\n    args = parser.parse_args()\n    ip = args.ip\n    login_account = args.user\n    login_password = args.passwd\n    ip_adar_type = ipaddress.ip_address(ip)\n    if type(ip_adar_type) == ipaddress.IPv4Address:\n        system_url = "https://" + ip + ""\n    else:\n        system_url = "https://[" + ip + "]"\n    redfish_obj = None\n    try:\n        redfish_obj = redfish.redfish_client(base_url=system_url, username=login_account, password=XXXXXX        redfish_obj.login()\n    except ServerDownOrUnreachableError:\n        sys.stderr.write("ERROR: server not reachable or doesn\'t support Redfish.\\n")\n        sys.exit(2)\n    get_resource_directory(redfish_obj)\n    sys.exit(0)\n'})
changed: [welktxef-931884-rh-le092s6-034 -> localhost] => (item={'filename': 'hp_hw_profile.yaml', 'value': '---\nresource_directory:\n  url: /redfish/v1/resourcedirectory\n  section: Instances\n'})

TASK [hpe/account-create : Copy HPE account creation scripts to working dir] **********************************************************
changed: [welktxef-931884-rh-le092s6-034 -> localhost] => (item=add_user_account.py)

TASK [hpe/account-create : Execute HPE account creation script] ***********************************************************************
fatal: [welktxef-931884-rh-le092s6-034 -> localhost]: FAILED! => {"changed": true, "cmd": "/tmp/ansible_bmc_p05tv2di/add_user_account.py -i \"2607:f160:10:9249:ce:40a:0:e009\" -u \"XXXXXX\" -p \"XXXXXX\" -r \"XXXXXX\" -l \"XXXXXX\" -e \"XXXXXX\"\n", "delta": "0:00:00.104087", "end": "2024-09-06 21:02:41.692244", "msg": "non-zero return code", "rc": 1, "start": "2024-09-06 21:02:41.588157", "stderr": "Traceback (most recent call last):\n  File \"/tmp/ansible_bmc_p05tv2di/add_user_account.py\", line 189, in <module>\n    if acct_check(args) is True:\n  File \"/tmp/ansible_bmc_p05tv2di/add_user_account.py\", line 18, in acct_check\n    REDFISH_OBJ = redfish.redfish_client(base_url=SYSTEM_URL,\nAttributeError: module 'redfish' has no attribute 'redfish_client'", "stderr_lines": ["Traceback (most recent call last):", "  File \"/tmp/ansible_bmc_p05tv2di/add_user_account.py\", line 189, in <module>", "    if acct_check(args) is True:", "  File \"/tmp/ansible_bmc_p05tv2di/add_user_account.py\", line 18, in acct_check", "    REDFISH_OBJ = redfish.redfish_client(base_url=SYSTEM_URL,", "AttributeError: module 'redfish' has no attribute 'redfish_client'"], "stdout": "", "stdout_lines": []}

TASK [Force a failure] ****************************************************************************************************************

TASK [force-error : Force failure] ****************************************************************************************************
fatal: [welktxef-931884-rh-le092s6-034 -> localhost]: FAILED! => {"changed": false, "msg": "Failed intentionally"}

PLAY RECAP ****************************************************************************************************************************
welktxef-931884-rh-le092s6-034 : ok=6    changed=3    unreachable=0    failed=1    skipped=18   rescued=1    ignored=0

(atlas) szabota@welktxefnce-h-pe1util-vm05:~/playbooks/bmc$
(atlas) szabota@welktxefnce-h-pe1util-vm05:~/playbooks/bmc$ source ~/python_venvs/
ansible/               atlas/                 hpe_fwupg/             python3.9/             robot/
ansible_6.7/           dmtf/                  kafka/                 redfish_eventlistener/
(atlas) szabota@welktxefnce-h-pe1util-vm05:~/playbooks/bmc$ source ~/python_venvs/ansible
ansible/     ansible_6.7/
(atlas) szabota@welktxefnce-h-pe1util-vm05:~/playbooks/bmc$ source ~/python_venvs/ansible
ansible/     ansible_6.7/
(atlas) szabota@welktxefnce-h-pe1util-vm05:~/playbooks/bmc$ source ~/python_venvs/ansible_6.7/bin/activate
(ansible_6.7) szabota@welktxefnce-h-pe1util-vm05:~/playbooks/bmc$ ansible-playbook -i inventory/welktxef-931884-rh-le092s6-034.yaml --vault-password ./vault.txt bmc.yaml

PLAY [BMC configuration playbook] *****************************************************************************************************

TASK [include_role : zts/enable-ssh] **************************************************************************************************
skipping: [welktxef-931884-rh-le092s6-034]

TASK [include_role : zts/check-redfish-health] ****************************************************************************************
skipping: [welktxef-931884-rh-le092s6-034]

TASK [include_role : zts/check_model] *************************************************************************************************
skipping: [welktxef-931884-rh-le092s6-034]

TASK [include_role : zts/disable_pam_auth] ********************************************************************************************
skipping: [welktxef-931884-rh-le092s6-034]

TASK [include_role : zts/upgrade_ls3] *************************************************************************************************
skipping: [welktxef-931884-rh-le092s6-034]

TASK [include_role : zts/upgrade_ls6] *************************************************************************************************
skipping: [welktxef-931884-rh-le092s6-034]

TASK [include_role : zts/disable_pam_auth] ********************************************************************************************
skipping: [welktxef-931884-rh-le092s6-034]

TASK [include_role : zts/configure-ipv4] **********************************************************************************************
skipping: [welktxef-931884-rh-le092s6-034]

TASK [include_role : zts/account-create] **********************************************************************************************
skipping: [welktxef-931884-rh-le092s6-034]

TASK [include_role : zts/mac-discover] ************************************************************************************************
skipping: [welktxef-931884-rh-le092s6-034]

TASK [include_role : zts/system-off] **************************************************************************************************
skipping: [welktxef-931884-rh-le092s6-034]

TASK [include_role : zts/bios-config] *************************************************************************************************
skipping: [welktxef-931884-rh-le092s6-034]

TASK [include_role : zts/host-name] ***************************************************************************************************
skipping: [welktxef-931884-rh-le092s6-034]

TASK [include_role : zts/configure-dns] ***********************************************************************************************
skipping: [welktxef-931884-rh-le092s6-034]

TASK [include_role : zts/configure-ntp] ***********************************************************************************************
skipping: [welktxef-931884-rh-le092s6-034]

TASK [include_role : zts/subscribe-redfish-events] ************************************************************************************
skipping: [welktxef-931884-rh-le092s6-034]

TASK [include_role : zts/system-on] ***************************************************************************************************
skipping: [welktxef-931884-rh-le092s6-034]

TASK [include_role : hpe/check_model] *************************************************************************************************

TASK [hpe/check_model : Get server model] *********************************************************************************************
ok: [welktxef-931884-rh-le092s6-034 -> localhost]

TASK [hpe/check_model : Set server model] *********************************************************************************************
ok: [welktxef-931884-rh-le092s6-034]

TASK [hpe/check_model : Display model name] *******************************************************************************************
ok: [welktxef-931884-rh-le092s6-034] => {
    "model_name": "Edgeline e920t"
}

TASK [hpe/check_model : Fail when model specifier substring in hostname does not match the actual model name] *************************
skipping: [welktxef-931884-rh-le092s6-034]

TASK [include_role : hpe/account-create] **********************************************************************************************

TASK [hpe/account-create : Create temporary working directory] ************************************************************************
changed: [welktxef-931884-rh-le092s6-034 -> localhost]

TASK [hpe/account-create : Copy HPE account creation scripts to working dir] **********************************************************
changed: [welktxef-931884-rh-le092s6-034 -> localhost] => (item={'filename': 'get_resource_directory.py', 'value': '#!/usr/bin/env python\n\nfrom __future__ import print_function\nimport argparse\nimport ipaddress\nimport yaml\nimport redfish\nimport os\nimport sys\nfrom redfish.rest.v1 import ServerDownOrUnreachableError\n\ndef get_resource_directory_profile():\n    cwd = os.path.dirname(os.path.abspath(__file__))\n    profile_name = "%s/hp_hw_profile.yaml" % cwd\n    try:\n        with open(profile_name) as file:\n            return yaml.load(file, Loader=yaml.FullLoader)["resource_directory"]\n    except IOError:\n        print("Error opening %s" % profile_name)\n        sys.exit(2)\n\ndef get_resource_directory(redfish_obj):\n    profile = get_resource_directory_profile()\n    response = redfish_obj.get(profile["url"])\n    resources = None\n    if response.status == 200:\n        resources = response.dict[profile["section"]]\n    else:\n        sys.stderr.write("\\tResource directory missing at %s\\n" % profile["url"])\n        sys.exit(2)\n    return resources\n\nif __name__ == "__main__":\n    parser = argparse.ArgumentParser(description="get resource directory script")\n    parser.add_argument("-n", dest="ip", required=True, help="The BMC IP address")\n    parser.add_argument("-u", dest="user", required=True, help="The BMC username")\n    parser.add_argument("-p", dest="passwd", required=True, help="The BMC password")\n    args = parser.parse_args()\n    ip = args.ip\n    login_account = args.user\n    login_password = args.passwd\n    ip_adar_type = ipaddress.ip_address(ip)\n    if type(ip_adar_type) == ipaddress.IPv4Address:\n        system_url = "https://" + ip + ""\n    else:\n        system_url = "https://[" + ip + "]"\n    redfish_obj = None\n    try:\n        redfish_obj = redfish.redfish_client(base_url=system_url, username=login_account, password=XXXXXX        redfish_obj.login()\n    except ServerDownOrUnreachableError:\n        sys.stderr.write("ERROR: server not reachable or doesn\'t support Redfish.\\n")\n        sys.exit(2)\n    get_resource_directory(redfish_obj)\n    sys.exit(0)\n'})
changed: [welktxef-931884-rh-le092s6-034 -> localhost] => (item={'filename': 'hp_hw_profile.yaml', 'value': '---\nresource_directory:\n  url: /redfish/v1/resourcedirectory\n  section: Instances\n'})

TASK [hpe/account-create : Copy HPE account creation scripts to working dir] **********************************************************
changed: [welktxef-931884-rh-le092s6-034 -> localhost] => (item=add_user_account.py)

TASK [hpe/account-create : Execute HPE account creation script] ***********************************************************************
changed: [welktxef-931884-rh-le092s6-034 -> localhost]

TASK [hpe/account-create : Remove temporary working directory] ************************************************************************
changed: [welktxef-931884-rh-le092s6-034 -> localhost]

TASK [include_role : hpe/mac-discover] ************************************************************************************************

TASK [hpe/mac-discover : Create temporary working directory] **************************************************************************
changed: [welktxef-931884-rh-le092s6-034 -> localhost]

TASK [hpe/mac-discover : Copy mac discovery scripts to working dir] *******************************************************************
changed: [welktxef-931884-rh-le092s6-034 -> localhost] => (item={'filename': 'get_resource_directory.py', 'value': '#!/usr/bin/env python\n\nfrom __future__ import print_function\nimport argparse\nimport ipaddress\nimport yaml\nimport redfish\nimport os\nimport sys\nfrom redfish.rest.v1 import ServerDownOrUnreachableError\n\ndef get_resource_directory_profile():\n    cwd = os.path.dirname(os.path.abspath(__file__))\n    profile_name = "%s/hp_hw_profile.yaml" % cwd\n    try:\n        with open(profile_name) as file:\n            return yaml.load(file, Loader=yaml.FullLoader)["resource_directory"]\n    except IOError:\n        print("Error opening %s" % profile_name)\n        sys.exit(2)\n\ndef get_resource_directory(redfish_obj):\n    profile = get_resource_directory_profile()\n    response = redfish_obj.get(profile["url"])\n    resources = None\n    if response.status == 200:\n        resources = response.dict[profile["section"]]\n    else:\n        sys.stderr.write("\\tResource directory missing at %s\\n" % profile["url"])\n        sys.exit(2)\n    return resources\n\nif __name__ == "__main__":\n    parser = argparse.ArgumentParser(description="get resource directory script")\n    parser.add_argument("-n", dest="ip", required=True, help="The BMC IP address")\n    parser.add_argument("-u", dest="user", required=True, help="The BMC username")\n    parser.add_argument("-p", dest="passwd", required=True, help="The BMC password")\n    args = parser.parse_args()\n    ip = args.ip\n    login_account = args.user\n    login_password = args.passwd\n    ip_adar_type = ipaddress.ip_address(ip)\n    if type(ip_adar_type) == ipaddress.IPv4Address:\n        system_url = "https://" + ip + ""\n    else:\n        system_url = "https://[" + ip + "]"\n    redfish_obj = None\n    try:\n        redfish_obj = redfish.redfish_client(base_url=system_url, username=login_account, password=XXXXXX        redfish_obj.login()\n    except ServerDownOrUnreachableError:\n        sys.stderr.write("ERROR: server not reachable or doesn\'t support Redfish.\\n")\n        sys.exit(2)\n    get_resource_directory(redfish_obj)\n    sys.exit(0)\n'})
changed: [welktxef-931884-rh-le092s6-034 -> localhost] => (item={'filename': 'hp_hw_profile.yaml', 'value': '---\nresource_directory:\n  url: /redfish/v1/resourcedirectory\n  section: Instances\n'})

TASK [hpe/mac-discover : Copy MAC address discovery scripts to working dir] ***********************************************************
changed: [welktxef-931884-rh-le092s6-034 -> localhost] => (item=find_ilo_mac_address.py)
changed: [welktxef-931884-rh-le092s6-034 -> localhost] => (item=ls3_92s3_find_ilo_mac_address.py)
changed: [welktxef-931884-rh-le092s6-034 -> localhost] => (item=ls6_find_ilo_mac_address.py)

TASK [hpe/mac-discover : Execute MAC address discovery script for HPE-LS3-e910] *******************************************************
skipping: [welktxef-931884-rh-le092s6-034]

TASK [hpe/mac-discover : MAC address discovery (result) for HPE-LS3-e910] *************************************************************
skipping: [welktxef-931884-rh-le092s6-034]

TASK [hpe/mac-discover : Execute MAC address discovery script for HPE-LS3-92s3] *******************************************************
skipping: [welktxef-931884-rh-le092s6-034]

TASK [hpe/mac-discover : MAC address discovery (result) for HPE-LS3-92s3] *************************************************************
skipping: [welktxef-931884-rh-le092s6-034]

TASK [hpe/mac-discover : Execute MAC address discovery script for HPE-LS6-92s6] *******************************************************
skipping: [welktxef-931884-rh-le092s6-034]

TASK [hpe/mac-discover : MAC address discovery (result) for HPE-LS6-92s6] *************************************************************
skipping: [welktxef-931884-rh-le092s6-034]

TASK [hpe/mac-discover : Remove temporary working directory] **************************************************************************
changed: [welktxef-931884-rh-le092s6-034 -> localhost]

TASK [hpe/mac-discover : Push MAC address to middleware] ******************************************************************************
skipping: [welktxef-931884-rh-le092s6-034]

TASK [hpe/mac-discover : Push MAC address to middleware] ******************************************************************************
skipping: [welktxef-931884-rh-le092s6-034]

TASK [hpe/mac-discover : Push MAC address to middleware] ******************************************************************************
skipping: [welktxef-931884-rh-le092s6-034]

TASK [include_role : hpe/bios-config] *************************************************************************************************

TASK [hpe/bios-config : Create temporary working directory] ***************************************************************************
changed: [welktxef-931884-rh-le092s6-034 -> localhost]

TASK [hpe/bios-config : Copy bios changing scripts to working dir] ********************************************************************
changed: [welktxef-931884-rh-le092s6-034 -> localhost] => (item={'filename': 'get_resource_directory.py', 'value': '#!/usr/bin/env python\n\nfrom __future__ import print_function\nimport argparse\nimport ipaddress\nimport yaml\nimport redfish\nimport os\nimport sys\nfrom redfish.rest.v1 import ServerDownOrUnreachableError\n\ndef get_resource_directory_profile():\n    cwd = os.path.dirname(os.path.abspath(__file__))\n    profile_name = "%s/hp_hw_profile.yaml" % cwd\n    try:\n        with open(profile_name) as file:\n            return yaml.load(file, Loader=yaml.FullLoader)["resource_directory"]\n    except IOError:\n        print("Error opening %s" % profile_name)\n        sys.exit(2)\n\ndef get_resource_directory(redfish_obj):\n    profile = get_resource_directory_profile()\n    response = redfish_obj.get(profile["url"])\n    resources = None\n    if response.status == 200:\n        resources = response.dict[profile["section"]]\n    else:\n        sys.stderr.write("\\tResource directory missing at %s\\n" % profile["url"])\n        sys.exit(2)\n    return resources\n\nif __name__ == "__main__":\n    parser = argparse.ArgumentParser(description="get resource directory script")\n    parser.add_argument("-n", dest="ip", required=True, help="The BMC IP address")\n    parser.add_argument("-u", dest="user", required=True, help="The BMC username")\n    parser.add_argument("-p", dest="passwd", required=True, help="The BMC password")\n    args = parser.parse_args()\n    ip = args.ip\n    login_account = args.user\n    login_password = args.passwd\n    ip_adar_type = ipaddress.ip_address(ip)\n    if type(ip_adar_type) == ipaddress.IPv4Address:\n        system_url = "https://" + ip + ""\n    else:\n        system_url = "https://[" + ip + "]"\n    redfish_obj = None\n    try:\n        redfish_obj = redfish.redfish_client(base_url=system_url, username=login_account, password=XXXXXX        redfish_obj.login()\n    except ServerDownOrUnreachableError:\n        sys.stderr.write("ERROR: server not reachable or doesn\'t support Redfish.\\n")\n        sys.exit(2)\n    get_resource_directory(redfish_obj)\n    sys.exit(0)\n'})
changed: [welktxef-931884-rh-le092s6-034 -> localhost] => (item={'filename': 'hp_hw_profile.yaml', 'value': '---\nresource_directory:\n  url: /redfish/v1/resourcedirectory\n  section: Instances\n'})

TASK [hpe/bios-config : Copy HPE python scripts to working dir] ***********************************************************************
changed: [welktxef-931884-rh-le092s6-034 -> localhost] => (item=enable_secure_boot.py)
changed: [welktxef-931884-rh-le092s6-034 -> localhost] => (item=disable_dhcp.py)
changed: [welktxef-931884-rh-le092s6-034 -> localhost] => (item=configure_dns.py)
changed: [welktxef-931884-rh-le092s6-034 -> localhost] => (item=configure_syslog.py)
changed: [welktxef-931884-rh-le092s6-034 -> localhost] => (item=disable_dhcp_ntp.py)
changed: [welktxef-931884-rh-le092s6-034 -> localhost] => (item=set_ilo_sntp_servers.py)
changed: [welktxef-931884-rh-le092s6-034 -> localhost] => (item=reset_ilo.py)

TASK [hpe/bios-config : Check if System is powered on] ********************************************************************************
ok: [welktxef-931884-rh-le092s6-034 -> localhost]

TASK [Power on the system] ************************************************************************************************************
skipping: [welktxef-931884-rh-le092s6-034]

TASK [hpe/bios-config : Set Fan percent Minimum to 10%] *******************************************************************************
ok: [welktxef-931884-rh-le092s6-034 -> localhost]

TASK [hpe/bios-config : Remove temporary working directory] ***************************************************************************
changed: [welktxef-931884-rh-le092s6-034 -> localhost]

TASK [hpe/bios-config : Get Bios Settings] ********************************************************************************************
ok: [welktxef-931884-rh-le092s6-034 -> localhost]

TASK [include_role : hpe/dhcp-disable] ************************************************************************************************

TASK [hpe/dhcp-disable : Disable IPv4 use domain setting] *****************************************************************************
ok: [welktxef-931884-rh-le092s6-034 -> localhost]

TASK [hpe/dhcp-disable : Reset iLO] ***************************************************************************************************
ok: [welktxef-931884-rh-le092s6-034 -> localhost]

TASK [hpe/dhcp-disable : Wait for HPE BMC to reset] ***********************************************************************************
Pausing for 180 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [welktxef-931884-rh-le092s6-034 -> localhost]

TASK [include_role : hpe/ilo-hostname] ************************************************************************************************

TASK [hpe/ilo-hostname : Change host name for iLO interface] **************************************************************************
ok: [welktxef-931884-rh-le092s6-034 -> localhost]

TASK [hpe/ilo-hostname : Reset iLO] ***************************************************************************************************
ok: [welktxef-931884-rh-le092s6-034 -> localhost]

TASK [hpe/ilo-hostname : Wait for HPE BMC to reset] ***********************************************************************************
Pausing for 180 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [welktxef-931884-rh-le092s6-034 -> localhost]

TASK [include_role : hpe/system-off] **************************************************************************************************

TASK [hpe/system-off : Check server power status] *************************************************************************************
ok: [welktxef-931884-rh-le092s6-034 -> localhost]

TASK [hpe/system-off : Force System Off] **********************************************************************************************
ok: [welktxef-931884-rh-le092s6-034 -> localhost]

TASK [hpe/system-off : Wait for HPE to shut down] *************************************************************************************
Pausing for 10 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [welktxef-931884-rh-le092s6-034]

TASK [include_role : hpe/host-name] ***************************************************************************************************

TASK [hpe/host-name : Change host name for iLO events] ********************************************************************************
ok: [welktxef-931884-rh-le092s6-034 -> localhost]

TASK [hpe/host-name : Change FQDN for iLO events] *************************************************************************************
ok: [welktxef-931884-rh-le092s6-034 -> localhost]

TASK [include_role : hpe/system-on] ***************************************************************************************************

TASK [hpe/system-on : Force System On] ************************************************************************************************
ok: [welktxef-931884-rh-le092s6-034 -> localhost]

TASK [hpe/system-on : Wait for HPE to power on] ***************************************************************************************
Pausing for 180 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [welktxef-931884-rh-le092s6-034]

TASK [include_role : hpe/syslog-disable] **********************************************************************************************

TASK [hpe/syslog-disable : Disable Remote Syslog] *************************************************************************************
ok: [welktxef-931884-rh-le092s6-034 -> localhost]

TASK [hpe/syslog-disable : Reset iLO] *************************************************************************************************
ok: [welktxef-931884-rh-le092s6-034 -> localhost]

TASK [hpe/syslog-disable : Wait for HPE BMC to reset] *********************************************************************************
Pausing for 180 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [welktxef-931884-rh-le092s6-034 -> localhost]

TASK [include_role : hpe/subscribe-redfish-events] ************************************************************************************

TASK [hpe/subscribe-redfish-events : Set facts to subscribe events for HPE servers] ***************************************************
ok: [welktxef-931884-rh-le092s6-034]

TASK [hpe/subscribe-redfish-events : Get Event subscription count] ********************************************************************
ok: [welktxef-931884-rh-le092s6-034 -> localhost]

TASK [hpe/subscribe-redfish-events : Delete existing subscriptions] *******************************************************************

TASK [hpe/subscribe-redfish-events : Subscribe to Redfish Alarms] *********************************************************************
ok: [welktxef-931884-rh-le092s6-034 -> localhost]

PLAY RECAP ****************************************************************************************************************************
welktxef-931884-rh-le092s6-034 : ok=38   changed=13   unreachable=0    failed=0    skipped=29   rescued=0    ignored=0

(ansible_6.7) szabota@welktxefnce-h-pe1util-vm05:~/playbooks/bmc$

```