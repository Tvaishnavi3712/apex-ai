# HPE ILO6 1.57 BIOS H11 v1.11
# HPE Sapphire Rapids E930t server
# 4/08/24 James Patchett - MTCE Lab VCPfe
# Platform Deploymnet MEAKV-965 

## Controller rchltxfe-c000000-001
OAM:  2607:f160:0:3043:cd:290:0:10

## welktxsr-931883-rh-le093s6-012
## welktxsr-d931883-012
ILO:  2607:f160:10:8803:ce:40a:0:e001
OAM:  2607:f160:0010:8803:ce:40a:0:f401


## Controller rchltxfe-c000000-001
## General info before we start

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ system show
+------------------------+--------------------------------------+
| Property               | Value                                |
+------------------------+--------------------------------------+
| contact                | demo.engineer@verizon.com              |
| created_at             | 2024-02-23T14:27:13.522174+00:00     |
| description            | Wind River Cloud Platform 22.12.4    |
| distributed_cloud_role | systemcontroller                     |
| https_enabled          | True                                 |
| latitude               | None                                 |
| location               | None                                 |
| longitude              | None                                 |
| name                   | rchltxfe-c000000-001                 |
| region_name            | RegionOne                            |
| sdn_enabled            | False                                |
| security_feature       | spectre_meltdown_v1                  |
| service_project_name   | services                             |
| software_version       | 22.12                                |
| system_mode            | duplex                               |
| system_type            | Standard                             |
| timezone               | UTC                                  |
| updated_at             | 2024-04-02T21:48:23.804892+00:00     |
| uuid                   | bbf4823c-1b22-440a-83b3-55fe6679c36f |
| vswitch_type           | none                                 |
+------------------------+--------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ system oam-show
+-----------------+--------------------------------------+
| Property        | Value                                |
+-----------------+--------------------------------------+
| created_at      | 2024-02-23T14:28:51.897364+00:00     |
| isystem_uuid    | bbf4823c-1b22-440a-83b3-55fe6679c36f |
| oam_c0_ip       | 2607:f160:0:3043:cd:290:0:11         |
| oam_c1_ip       | 2607:f160:0:3043:cd:290:0:12         |
| oam_floating_ip | 2607:f160:0:3043:cd:290:0:10         |
| oam_gateway_ip  | 2607:f160:0:3043:cd:28::             |
| oam_subnet      | 2607:f160:0:3043::/64                |
| updated_at      | None                                 |
| uuid            | 7feebde0-cb74-4c6f-bc4f-231d2deca4da |
+-----------------+--------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ system application-list
+--------------------------+----------+-------------------------------------------+------------------+----------+-----------+
| application              | version  | manifest name                             | manifest file    | status   | progress  |
+--------------------------+----------+-------------------------------------------+------------------+----------+-----------+
| cert-manager             | 22.12-8  | cert-manager-fluxcd-manifests             | fluxcd-manifests | applied  | completed |
| nginx-ingress-controller | 22.12-1  | nginx-ingress-controller-fluxcd-manifests | fluxcd-manifests | applied  | completed |
| oidc-auth-apps           | 22.12-6  | oidc-auth-apps-fluxcd-manifests           | fluxcd-manifests | applied  | completed |
| platform-integ-apps      | 22.12-66 | platform-integ-apps-fluxcd-manifests      | fluxcd-manifests | uploaded | completed |
| wr-analytics             | 23.09-0  | wr-analytics-fluxcd-manifests             | fluxcd-manifests | applied  | completed |
+--------------------------+----------+-------------------------------------------+------------------+----------+-----------+
[XXXXXX@controller-0 ~(keystone_admin)]$ sw-patch query
      Patch ID         RR  Release  Patch State
=====================  ==  =======  ===========
WRCP_22.12_PATCH_0001  Y    22.12    Committed
WRCP_22.12_PATCH_0002  Y    22.12    Committed
WRCP_22.12_PATCH_0003  Y    22.12    Committed
WRCP_22.12_PATCH_0004  Y    22.12    Committed

[XXXXXX@controller-0 ~(keystone_admin)]$

```


## Initiate Deployment of subcloud
## Subcloud welktxsr-d931883-012

```log
XXXXXX@caromacl255 Downloads % cat install-22.12.4-welktxsr-931883-rh-le093s6-012.txt |more
Script started on 2024-04-08 21:19:00+00:00 [TERM="xterm-256color" TTY="/dev/pts/67" COLUMNS="165" LINES="17"]
szabota@welktxefnce-h-pe1util-vm05:~/playbooks/wr-installer-atlas-me$ ^M(reverse-i-search)`': ESC^Hs': ipmitool -I lanplus -H ${IP} -U XXXXXX -P XXXXXX ^MESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[1@oESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CEESC[CESC[CESC[CESC[CESC[CESC[C^MESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CEESC[24Pu': source ~/python_venvs/ansible_6.7/bin/activate^MESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC^HESC[1@rESC[CESC[CESC^HESC[1@cESC[CESC[CESC^HESC[1@eESC[CESC[CESC^HESC[1@ ESC[CESC[CESC[C^MES^MESC[41@szabota@welktxefnce-h-pe1util-vm05:~/playbooks/wr-installer-atlas-me$ESC[C
(ansible_6.7) szabota@welktxefnce-h-pe1util-vm05:~/playbooks/wr-installer-atlas-me$ ^MESC[K(ansible_6.7) szabota@welktxefnce-h-pe1util-vm05:~/playbooks/wr-installer-atlas-me$ ^MESC[K(ansible_6.7) szabota@welktxefnce-h-pe1util-vm05:~/playbooks/wr-installer-atlas-me$ ^MESC[K(ansible_6.7) szabota@welktxefnce-h-pe1util-vm05:~/playbooks/wr-installer-atlas-me$ ^MESC[K(ansible_6.7) szabota@welktxefnce-h-pe1util-vm05:~/playbooks/wr-installer-atlas-me$ ^MESC[Creverse-i-search)`': ESC^Hw': curl --globoff -L -w "\\n%{http_code} %{url_effective}\\n" -kn -H "Content-Type: application/json" -H 'If-None-Match: ""' -d '{"ResetType": "ForceRestart"}' -X POST https://[${IP}]/redfish/v1/Systems/Self/Actions/ComputerSystem.ResetESC[A^MESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[C^MESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[Cr': cd playbooks/wr-installer-atlas-me/ESC[K
^MESC[KESC[AESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CEESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC^H^H^H^H^H^H^H^H^H^H^H^H^H^HESC[1@-ESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC^H^H^H^H^H^H^H^H^H^H^H^H^H^H^HESC[1PESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC^H^H^H^H^H^H^H^H^H^H^H^H^H^H^': ansible-playbook --vault-password-file ./vault_pass -i inventory/welktxsr-d931883-012.yaml wr_rem^H^H^H^H^H^H^MESC[Cansible_6.7) szabota@welktxefnce-h-pe1util-vm05:~/playbooks/wr-installer-atlas-me$ ansible-playbook --vault-password-file ./vault_pass -i inventory/welktxsr-d931883-012.yaml ESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[CESC[C

PLAY [Wind River Remote Subcloud Installer] **********************************************************************************************

TASK [Reset BMC] *************************************************************************************************************************
Monday 08 April 2024  21:25:14 +0000 (0:00:00.037)       0:00:00.037 **********

TASK [remote/reset_bmc : Reset ZTS BMC using IPMItool] ***********************************************************************************
Monday 08 April 2024  21:25:14 +0000 (0:00:00.029)       0:00:00.066 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/reset_bmc : Wait for ZTS BMC to reset] **************************************************************************************
Monday 08 April 2024  21:25:14 +0000 (0:00:00.016)       0:00:00.082 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/reset_bmc : Reset HPE ILO using Redfish] ************************************************************************************
Monday 08 April 2024  21:25:14 +0000 (0:00:00.018)       0:00:00.101 **********
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012 -> localhost]ESC[0m

TASK [remote/reset_bmc : Wait for HPE BMC to reset] **************************************************************************************
Monday 08 April 2024  21:25:15 +0000 (0:00:00.677)       0:00:00.778 **********
Pausing for 180 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [Download Files] ********************************************************************************************************************
Monday 08 April 2024  21:28:15 +0000 (0:03:00.021)       0:03:00.800 **********

TASK [common/download_files : Check if artifact files exist locally] *********************************************************************
Monday 08 April 2024  21:28:15 +0000 (0:00:00.026)       0:03:00.826 **********
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012 -> localhost]ESC[0m

TASK [common/download_files : Download & unarchive artifact files to local directory if they don't exist] ********************************
Monday 08 April 2024  21:28:15 +0000 (0:00:00.276)       0:03:01.103 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [Set Facts] *************************************************************************************************************************
Monday 08 April 2024  21:28:15 +0000 (0:00:00.016)       0:03:01.119 **********

TASK [remote/set-facts : Set facts for vip, ansible, and wr_admin] ***********************************************************************
Monday 08 April 2024  21:28:15 +0000 (0:00:00.024)       0:03:01.143 **********
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/set-facts : Get central controller's software load version] *****************************************************************
Monday 08 April 2024  21:28:15 +0000 (0:00:00.035)       0:03:01.178 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)]ESC[0m

TASK [remote/set-facts : Set facts for wr_release_version] *******************************************************************************
Monday 08 April 2024  21:28:21 +0000 (0:00:05.947)       0:03:07.126 **********
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/set-facts : Print wr_release_version] ***************************************************************************************
Monday 08 April 2024  21:28:21 +0000 (0:00:00.016)       0:03:07.142 **********
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012] => ESC[0m
ESC[0;32m  msg: 'wr_release_version: 22.12'ESC[0m

TASK [Remote Configure] ******************************************************************************************************************
Monday 08 April 2024  21:28:21 +0000 (0:00:00.022)       0:03:07.165 **********

TASK [remote/remote-configure : Set facts] ***********************************************************************************************
Monday 08 April 2024  21:28:21 +0000 (0:00:00.040)       0:03:07.206 **********
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-configure : Set facts - new] *****************************************************************************************
Monday 08 April 2024  21:28:21 +0000 (0:00:00.012)       0:03:07.219 **********
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-configure : Set facts for which image list to use based on WR version] ***********************************************
Monday 08 April 2024  21:28:21 +0000 (0:00:00.019)       0:03:07.238 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-configure : Set facts for which image list to use based on WR version] ***********************************************
Monday 08 April 2024  21:28:21 +0000 (0:00:00.014)       0:03:07.252 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-configure : Set facts for which image list to use based on WR version] ***********************************************
Monday 08 April 2024  21:28:21 +0000 (0:00:00.015)       0:03:07.267 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-configure : Print wr_image_list] *************************************************************************************
Monday 08 April 2024  21:28:21 +0000 (0:00:00.014)       0:03:07.282 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-configure : print wr_license_key] ************************************************************************************
Monday 08 April 2024  21:28:21 +0000 (0:00:00.019)       0:03:07.301 **********
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012] => ESC[0m
ESC[0;32m  msg: wr_license_key = IyBXaW5kIFJpdmVyIFByb2R1Y3QgQWN0aXZhdGlvbiBGaWxlIChpbnN0YWxsLnR4dCkKIyBJc3N1ZWQgZm9yIGhvc3Q6IDxWZXJpem9uPiA8VmVyaXpvbj4gPEFueT4KIyBMaWNlbnNlIG51bWJlcihzKTogNjgyMzc0CiMgSXNzdWVkIG9uOiAxMy1hcHItMjAyMyAwOTo1MDo1MAojCiMgTm90ZTogdGhpcyBsaWNlbnNlIGlzIGdlbmVyYXRlZCBjdW11bGF0aXZlbHkgZm9yIGFsbAojIFdpbmQgUml2ZXIgc29mdHdhcmUgbWFuYWdlZCBieSB0aGlzIGhvc3QuCgojIDEuIEZsZXhMTSBsaWNlbnNlIGZpbGU6CiMgQmVnaW46IFNlcnZlciBsaWNlbnNlICAtLS0tLS0tLS0tLS0tLS0tLS0tLS0KIyBTZXJpYWwgTnVtYmVyOiA2ODQ0NDktVmVyaXpvblBPQy1HNFdEQzlDUEVLCgpQQUNLQUdFIFdSQ1BfQ09OVEFJTkVSX1BLRyB3cnNkIDIyIDg1MERCRTAwQkFCRSBcCglDT01QT05FTlRTPVdSQ1BfQ09OVEFJTkVSOjIyLjEyIE9QVElPTlM9U1VJVEUgXAoJU0lHTj0xNkI4MjY4NjkwRDgKSU5DUkVNRU5UIFdSQ1BfQ09OVEFJTkVSX1BLRyB3cnNkIDIyIHBlcm1hbmVudCB1bmNvdW50ZWQgNEMxRUE2NjQyNUUyIFwKCVZFTkRPUl9TVFJJTkc9PGxuPjY4MjM3NDwvbG4+PHBzPjIyMTMtNDM8L3BzPiBIT1NUSUQ9QU5ZIFwKCUlTU1VFRD0xMy1hcHItMjAyMyBTTj1zZXJpYWwtVmVyaXpvbi1MVjJJV0FVTEVCIFwKCVNUQVJUPTEzLWFwci0yMDIzIFNJR049NDI2RjUyOUUxRjYwCg==ESC[0m

TASK [remote/remote-configure : Copy storage checking script if server is HPE-LS3-e910] **************************************************
Monday 08 April 2024  21:28:21 +0000 (0:00:00.019)       0:03:07.321 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012] => (item=hpe_storage_check.py) ESC[0m

TASK [remote/remote-configure : Execute storage checking script if server is HPE-LS3-e910] ***********************************************
Monday 08 April 2024  21:28:21 +0000 (0:00:00.023)       0:03:07.344 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor HPE HPE-LS3-e910 (4 disks)] ***********************
Monday 08 April 2024  21:28:21 +0000 (0:00:00.016)       0:03:07.361 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor HPE HPE-LS3-e910 (2 disks)] ***********************
Monday 08 April 2024  21:28:21 +0000 (0:00:00.016)       0:03:07.377 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor HPE HPE-LS3-92s3] *********************************
Monday 08 April 2024  21:28:21 +0000 (0:00:00.017)       0:03:07.395 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor HPE HPE-LS6-92s6] *********************************
Monday 08 April 2024  21:28:21 +0000 (0:00:00.015)       0:03:07.411 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor HPE HPE-LS6-93s6] *********************************
Monday 08 April 2024  21:28:21 +0000 (0:00:00.016)       0:03:07.428 **********
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor ZTS ZTS-LS6-93s6] *********************************
Monday 08 April 2024  21:28:21 +0000 (0:00:00.017)       0:03:07.446 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor ZTS ZTS-LS3-trtn] *********************************
Monday 08 April 2024  21:28:21 +0000 (0:00:00.014)       0:03:07.460 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-configure : Set facts for Corning] ***********************************************************************************
Monday 08 April 2024  21:28:21 +0000 (0:00:00.012)       0:03:07.472 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor ZTS ZTS-LS6-pts6 & ZTS-LS3-pts3 ZTS-LS6-aks6 & ZTS-LS3-aks3 & ZTS-XXX-ptmm] ***
Monday 08 April 2024  21:28:21 +0000 (0:00:00.016)       0:03:07.489 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-configure : Find out which DM Docker version contral has] ************************************************************
Monday 08 April 2024  21:28:21 +0000 (0:00:00.015)       0:03:07.504 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-configure : Find out which DM file version contral has] **************************************************************
Monday 08 April 2024  21:28:21 +0000 (0:00:00.019)       0:03:07.524 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-configure : Print dm docker version and dm file version] *************************************************************
Monday 08 April 2024  21:28:21 +0000 (0:00:00.016)       0:03:07.540 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-configure : Discover Wind River docker image names] ******************************************************************
Monday 08 April 2024  21:28:21 +0000 (0:00:00.017)       0:03:07.557 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-configure : Print local_images_full] *********************************************************************************
Monday 08 April 2024  21:28:21 +0000 (0:00:00.015)       0:03:07.573 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-configure : Create fact for Wind River docker image names] ***********************************************************
Monday 08 April 2024  21:28:21 +0000 (0:00:00.016)       0:03:07.590 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-configure : Determine DM Helm Chart path] ****************************************************************************
Monday 08 April 2024  21:28:21 +0000 (0:00:00.017)       0:03:07.607 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-configure : Print dm_helm_chart] *************************************************************************************
Monday 08 April 2024  21:28:21 +0000 (0:00:00.016)       0:03:07.624 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-configure : Set DM Helm Chart file] **********************************************************************************
Monday 08 April 2024  21:28:21 +0000 (0:00:00.016)       0:03:07.640 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-configure : Lookup Deployment Manager image tag] *********************************************************************
Monday 08 April 2024  21:28:21 +0000 (0:00:00.017)       0:03:07.658 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-configure : Lookup RBAC Proxy image tag] *****************************************************************************
Monday 08 April 2024  21:28:21 +0000 (0:00:00.017)       0:03:07.675 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-configure : Copy WRCP DM Playbook] ***********************************************************************************
Monday 08 April 2024  21:28:22 +0000 (0:00:00.020)       0:03:07.695 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012] => (item=None) ESC[0m

TASK [remote/remote-configure : Set a fact for the central controller VIP address] *******************************************************
Monday 08 April 2024  21:28:22 +0000 (0:00:00.017)       0:03:07.713 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-configure : Configure WRCP seed template] ****************************************************************************
Monday 08 April 2024  21:28:22 +0000 (0:00:00.022)       0:03:07.735 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012] => (item={'src': 'bootstrap-values.yaml', 'dest': 'welktxsr-d931833-012-bootstrap-values.yaml'}) ESC[0m
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012] => (item={'src': 'deploy-values.yaml', 'dest': 'welktxsr-d931833-012-deploy-values.yaml'}) ESC[0m
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012] => (item={'src': 'deploy-standard.yaml', 'dest': 'welktxsr-d931833-012-deploy-standard.yaml'}) ESC[0m
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012] => (item={'src': 'install-values.yaml', 'dest': 'welktxsr-d931833-012-install-values.yaml'}) ESC[0m

TASK [remote/remote-configure : Set a fact for the central controller VIP address] *******************************************************
Monday 08 April 2024  21:28:22 +0000 (0:00:00.026)       0:03:07.762 **********
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-configure : Retrieve sysinv password from CC] ************************************************************************
Monday 08 April 2024  21:28:22 +0000 (0:00:00.031)       0:03:07.793 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)]ESC[0m

TASK [remote/remote-configure : Store sysinv password] ***********************************************************************************
Monday 08 April 2024  21:28:25 +0000 (0:00:03.625)       0:03:11.419 **********
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-configure : copy seed templates] *************************************************************************************
Monday 08 April 2024  21:28:25 +0000 (0:00:00.027)       0:03:11.446 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)] => (item={'src': 'bootstrap-values.yaml', 'dest': 'welktxsr-d931833-012-bootstrap-values.yaml'})ESC[0m
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)] => (item={'src': 'deploy-standard.yaml', 'dest': 'welktxsr-d931833-012-deploy-standard.yaml'})ESC[0m
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)] => (item={'src': 'install-values.yaml', 'dest': 'welktxsr-d931833-012-install-values.yaml'})ESC[0m

TASK [remote/remote-configure : Copy SSL cert files] *************************************************************************************
Monday 08 April 2024  21:28:35 +0000 (0:00:09.266)       0:03:20.713 **********
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)] => (item={'filename': 'k8s_root_ca_cert.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIF8jCCA9qgAwIBAgIJAIf9Ql2uDZh+MA0GCSqGSIb3DQEBDQUAMIGFMQswCQYD\nVQQGEwJVUzEOMAwGA1UECAwFVGV4YXMxETAPBgNVBAcMCFdlc3RsYWtlMR0wGwYD\nVQQKDBRWZXJpem9uIFNvdXJjaW5nIExMQzE0MDIGA1UEAwwrVmVyaXpvbiBOZXR3\nb3JrIFdFTEtUWElCIExBQiAxIDMgUlNBIEs4UyBDQTAeFw0yMDEwMjUyMjEyNDha\nFw0zMDEwMjMyMjEyNDhaMIGFMQswCQYDVQQGEwJVUzEOMAwGA1UECAwFVGV4YXMx\nETAPBgNVBAcMCFdlc3RsYWtlMR0wGwYDVQQKDBRWZXJpem9uIFNvdXJjaW5nIExM\nQzE0MDIGA1UEAwwrVmVyaXpvbiBOZXR3b3JrIFdFTEtUWElCIExBQiAxIDMgUlNB\nIEs4UyBDQTCCAiIwDQYJKoZIhvcNAQEBBQADggIPADCCAgoCggIBAKyF9svdv/qG\n7HxBr1DWvZ3CQiDsA4m1kj0hD7jo3B3W/32ODcPpgeNmp4Oful0SsndpqEGhXDq5\noiBfqszMUpzDgdQ7siIHekb2olFEK2KniMP3H53nilIppeyMby5K3ZwF0Qbmk5WK\ncoXoYegP+Uv9bV0AMH6Dn4CVgYrLAYfmPyGgUSt4vuZ9F/rf9UkBf/DcZGqMnMax\n/Gfaq8KwmDzD9D8IVCHPrM5f4+CaKMQCFu5QkSsLYJFRiuQWWaICMMdnqpb0HZh5\niPnCSHwPPUyXxtujdI97Ovy4X5WR46jJ2+KzPYe8tVa/DL3TlKmRL9AF+oSE17bw\nzGAE7GNWxPojebHIUuoKdOQC1qiJBVS+c14r9+9P2Uy6XEhNUs+h3juRI4U3YkQ1\nUCUU3opqhOPh4jUIuPGg5aX07lt4Wpxc48D+CY1D4i6vaJLl3WCsVK7PFwWVQQEW\nIQabfuj1R2jEu7pp2Yabza58S00v1P5/kv/DNr7ADm8eYRvxLAAXCedMeSDXKBgd\npPmVXXZoZ8+X8VRGYxcw0mBBLIAiTOntT2vgLeq5T3QyiVKdU6TLAYEjS65QZ3Eg\naIX0wRqlcQI7lruTXubtENG6wWXYtnDf5795ZID1YIEqkgzZLMBqq1SBiLnWd6aK\n78Zsr4j5GmTBGpKRmwE2oO1btJCCYyG5AgMBAAGjYzBhMA8GA1UdEwEB/wQFMAMB\nAf8wHQYDVR0OBBYEFEDQ5EaGp3x02WUuvqetygqpM3dCMB8GA1UdIwQYMBaAFEDQ\n5EaGp3x02WUuvqetygqpM3dCMA4GA1UdDwEB/wQEAwICpDANBgkqhkiG9w0BAQ0F\nAAOCAgEAeCMxVJr5Jyg87DVaUtEhiWfhto993ENrnevAGqrBOoRc/KU1/C3paqhR\nsvr2r2LR+npSmeo6iz0FaO31XwHSHX95+XJeGP5Q8TGddbRiTglQsMfOkGNzxqgg\nTkdZ8A1y9v2jprONUmLADVGIVT0AoHc7V9w1I8NKhrY+rIllum4FRDiDPSnImh5h\nxmH+Nq2ZuEFVdtV/oNKzEu2ywmbgBRd5Jv3rTejxltmTZtyq8IKoKguj3NVFn93Q\nU4TbsxkcAdrLMooLYYDRTWA4t0iqKM/UkYUg4xl2l9NrY7ZUbaNd5+YsLNdqXO/c\nmp7wyMv/8ZIy1BLG4zJmX/JzWkYmULqQ+A+21+YuqrV3a81V7vcHhJcRaPOrg5cd\nYwY2eCbXMvNOdrzppIglUrlddNuqAhs1MTi/VibxYuI9isU0JckXIcCy1L+xbEda\n6v/z6wSrScVz0I4m0DpK6xMQ8t9sLcrGp5uGbj6J4nQWd+QLdq6kmAzDOZ/Gs0wb\nPYdkER4dXAVcioYFekpKv7d+nur0FPtMNIw0OdhX2eAwC22IFAq2DZRjUFvaBGaD\ni1ptfq6P1mVJ2T/exYujEDtq+8yQTfWgFm/DjEfWtcCp0Jukgv8opLR2DpCf5Ucq\nd5X7d/DP0mukJ3vZ8EIqYorwZJ1L1a2jgngjA+gPxIaW+JHfTHU=\n-----END CERTIFICATE-----\n'})ESC[0m
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)] => (item={'filename': 'k8s_root_ca_key.pem', 'value': '-----BEGIN PRIVATE KEY-----\nMIIJQQIBADANBgkqhkiG9w0BAQEFAASCCSswggknAgEAAoICAQCshfbL3b/6hux8\nQa9Q1r2dwkIg7AOJtZI9IQ+46Nwd1v99jg3D6YHjZqeDn7pdErJ3aahBoVw6uaIg\nX6rMzFKcw4HUO7IiB3pG9qJRRCtip4jD9x+d54pSKaXsjG8uSt2cBdEG5pOVinKF\n6GHoD/lL/W1dADB+g5+AlYGKywGH5j8hoFEreL7mfRf63/VJAX/w3GRqjJzGsfxn\n2qvCsJg8w/Q/CFQhz6zOX+PgmijEAhbuUJErC2CRUYrkFlmiAjDHZ6qW9B2YeYj5\nwkh8Dz1Ml8bbo3SPezr8uF+VkeOoydvisz2HvLVWvwy905SpkS/QBfqEhNe28Mxg\nBOxjVsT6I3mxyFLqCnTkAtaoiQVUvnNeK/fvT9lMulxITVLPod47kSOFN2JENVAl\nFN6KaoTj4eI1CLjxoOWl9O5beFqcXOPA/gmNQ+Iur2iS5d1grFSuzxcFlUEBFiEG\nm37o9UdoxLu6admGm82ufEtNL9T+f5L/wza+wA5vHmEb8SwAFwnnTHkg1ygYHaT5\nlV12aGfPl/FURmMXMNJgQSyAIkzp7U9r4C3quU90MolSnVOkywGBI0uuUGdxIGiF\n9MEapXECO5a7k17m7RDRusFl2LZw3+e/eWSA9WCBKpIM2SzAaqtUgYi51nemiu/G\nbK+I+RpkwRqSkZsBNqDtW7SQgmMhuQIDAQABAoICACysO62qa+2pRk8eixD5qfvR\ns2Hm+zuLYqSljPaqhWTMqTePswzJyDJkAHhawd0b3E6Dc2gbKlCihNKxMv744WNq\nVJHqK0QYf5ckgf9dEYboLsffk7ZFoFGKK0bHTnrENAIUl32b8xdD1EfMVp3KlRkS\nNGFijSwVVRXsoLCZxHm2Kx6/7oS9LWFtfuodV9xhoQlzaCUW5/mjWOJjgxpUs/b4\nHqS7uV1P80U1G0KraGboy5tGDXEB7y1x2e8Zwnfq7UqVE10nNQqoXcmefzpwj8Tn\ngDybZLFKjYmnDEkkj7jDHEbldsdRG/usWNZGlTYbPDA3fBkYdOsQCzvJypQmgbZ+\n3yk3Lj2+9vLEMfPrruuzyOSXgki6o5uvy7Je6PdBpsz75k8FH6a+Rw3vvP8HuP3S\nLSUYm3tyOheXHR7BKN4bnfi11RAWvDpT9S+QnZ+R8DmQzOADlnjRC8WewDJYoNJ1\np1jeuqswlxo144oMO92cmdS2dAbPvS6aQP1I85Q2NniY+6YhHkBwIQIlfVs1JPbY\nX7QtTy1IXQhR3sospyvUwY2GPSAeVHDRL53ClQKDsvWpSy0MAmWYJkZu1P+jKBim\nj34ytApgG65Hv/RHf3L4+4zzItZ3TN2tJ/g9EKc6oMNtqKbbG56kkmvRPWKtMGV8\nFqxCvG5NydUK7fN+P2WJAoIBAQDXLFC//Fn9ed1U+pKa2M25aJwEetkGLXQvkwVi\n8uJFaXITb2ceveSEo6iBExyn4eYL5A4X+RZdJJdRRbj4whsNN13Pm+6lYX3pp7MN\nO+78uvwVfKZiWPFKfZs7ZH1/O9VIlLGnXUHeaHK1tmv9ixxMixdnjUDkcVa0O3qT\nKBLpvXnVEMYizxQBN0P5Z9QvQQGpUhKnNw+FhV1SP+YHxrB0Pu6qbYAmZZC2MQc1\nTsDyqGjmHk9VJaFYAAPEjqACDbfnkVUCj0ylM4xPQuBJs9DOKh4InG+znusdmd8H\nmvoEFDppsrH1NhO6GTeuCk6n0WBi6cUm76K/gPscYyV4ZtkfAoIBAQDNQgDXtfqv\nxbAhvDk0o/P8fqOdgQF0uFTqYHmyW31Ty9nF0ptA8LVJOIljU3zlLplhIFjBnSEG\nLqu4jnLLRR+zej0MXmJuZ9BMWmQeTrZzttnH5bn54E07DPJ5BvFoTMJNklBiXjB5\n5hTPZS4yK1KjoxY+Ypnj4W1iZjP37ya/A34J2nlYtoW4LdVfJHqCxBXel9Nz2zkv\nvwwPu8Eu7gFLuhNQM6Iv4mORGI8yg7Y/BwodfDPRuFvrG1KXkjwASb0O5b1suRQy\n9H80q5EAbT36K1z48ilr8fcroN+hV8g4yntrBBgOHPMmBk/vHKU8B1rkBr0p2haI\n3PwKmDFRsDInAoIBAGrjjMmSZnHQk+6e+y0I/klYegiPrjevZMQtWMOqvFSW6SBW\nevd+hYKOeiqEf/u18D1/8LBgAIgMoU6yQAzy/9U059k2MPrez1m/AOdWGoZZrNhP\nr6ezX0oN04tRhDYsVutTUl09qnb9k95I3KR68nfjsKC0PsQ8uUGXOnDXu215vofl\naUfpbpqcBZxjw7glptmh97oxU/iUI6O0MmUygn18tbrb4okwcw7OlDIbCSaCGnoW\nHHrD0r6QY07FOx9KCU1zmLNI1F5MmSrWoex68wM3UOweKi8khs+RnIV+qyxTkCDp\nsBWL44jS9iHy5Nfg3uzEDDgnWsWfIR8c8YQ6MykCggEADr0ollTI9Yo6hZGggfkr\n8fueABddZWY/Ir1ev8H2E+hVcPEYmOcv/VwD8Y/zLfnUpbbO6MhBsNH1HsGL2LDT\n/+1NKPA2HTtzJ6ht/Acm7tQ4ezQx0JGcuhrJ5orrFtQ8N5nED+w3iulMoT/gu1WF\nD58MX9pwtn5ffmtcW/deTuUPTeHUSNyCaaFQ6w4RhgZSk7NPSch6KMWNNiwDST1p\n9mgcLuwmP04AXFDpJ3VxxsDYpxleFzcn0pAZtCyaBmNFIia5HW+E1cvcvol7Vg6C\nHs6yVGX/N3MejpF0vX8yL3HKvvqCR7EofJiDcOYbr13P1wPs3W59o8JKjvAyymze\njQKCAQAUY/0asRL33D7tFoIbLg/N9hi+tCCM35DMf2FeXm3QwSkAR/BJw0ewCE5C\n+VqukHN3/i0Xe8KSHwEuLK2sGLk9Ys8A5NytjqFApYwpIk8UrRONfC12H3ez5VYk\nJlhMVhVXEZvVhEFJiBC7q6x6s7BVtLTGV7FA5CW8YKBhwHwrpm+h/Xb798oaKyel\nP/xYq+GZzfWfbvUjZvgN0J0RGxKA+GRgsmhoyOfgCVXgSzuUkI+9cAUvC0OV407L\n4XIK0GDJ7Tv/2USSPfmueyGEmacc/oYUPVBUgeINSoaCM4cpZwyLylVEtKOdQoEE\n77G5mvQsoXxsMjd+nbHil450UHsL\n-----END PRIVATE KEY-----\n'})ESC[0m

TASK [Remote Install] ********************************************************************************************************************
Monday 08 April 2024  21:28:40 +0000 (0:00:05.553)       0:03:26.266 **********

TASK [remote/remote-install : Check if the subcloud deployed but failed] *****************************************************************
Monday 08 April 2024  21:28:40 +0000 (0:00:00.085)       0:03:26.351 **********
ESC[0;31mfatal: [welktxsr-931883-rh-le093s6-012 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)]: FAILED! => changed=true ESC[0m
:
ESC[0;31m  cmd: |-ESC[0m
ESC[0;31m    . /etc/platform/openrcESC[0m
ESC[0;31m    dcmanager subcloud show welktxsr-d931833-012 --column "deploy_status" --format valueESC[0m
ESC[0;31m  delta: '0:00:03.720305'ESC[0m
ESC[0;31m  end: '2024-04-08 21:28:46.282971'ESC[0m
ESC[0;31m  msg: non-zero return codeESC[0m
ESC[0;31m  rc: 1ESC[0m
ESC[0;31m  start: '2024-04-08 21:28:42.562666'ESC[0m
ESC[0;31m  stderr: ERROR (app) The resource could not be found. Subcloud not foundESC[0m
ESC[0;31m  stderr_lines: <omitted>ESC[0m
ESC[0;31m  stdout: ''ESC[0m
ESC[0;31m  stdout_lines: <omitted>ESC[0m
ESC[0;36m...ignoringESC[0m

TASK [remote/remote-install : debug] *****************************************************************************************************
Monday 08 April 2024  21:28:46 +0000 (0:00:05.831)       0:03:32.182 **********
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012] => ESC[0m
ESC[0;32m  msg: 'subcloud_status:'ESC[0m

TASK [remote/remote-install : Delete the subcloud that is in failed state] ***************************************************************
Monday 08 April 2024  21:28:46 +0000 (0:00:00.019)       0:03:32.202 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-install : include_tasks] *********************************************************************************************
Monday 08 April 2024  21:28:46 +0000 (0:00:00.018)       0:03:32.220 **********
ESC[0;36mincluded: /home/szabota/playbooks/wr-installer-atlas-me/roles/remote/remote-utility/tasks/enable_mwait.yaml for welktxsr-931883-rh-le093s6-012ESC[0m

TASK [remote/remote-install : Enable mwait for ZTS Proteus] ******************************************************************************
Monday 08 April 2024  21:28:46 +0000 (0:00:00.029)       0:03:32.250 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-install : Deploy remote cloud] ***************************************************************************************
Monday 08 April 2024  21:28:46 +0000 (0:00:00.016)       0:03:32.266 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)]ESC[0m

TASK [remote/remote-install : 1st polling prep: Obtain Keystone auth token] **************************************************************
Monday 08 April 2024  21:28:53 +0000 (0:00:06.774)       0:03:39.041 **********
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012 -> localhost]ESC[0m

TASK [remote/remote-install : 1st polling: Wait for subcloud to start installing OS] *****************************************************
Monday 08 April 2024  21:28:54 +0000 (0:00:00.968)       0:03:40.009 **********
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 1st polling: Wait for subcloud to start installing OS (40 retries left).ESC[0m
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012 -> localhost]ESC[0m

TASK [remote/remote-install : 1st polling result: Fail if the installation failed] *******************************************************
Monday 08 April 2024  21:29:25 +0000 (0:00:30.989)       0:04:10.999 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-install : 2nd polling prep: Obtain Keystone auth token] **************************************************************
Monday 08 April 2024  21:29:25 +0000 (0:00:00.022)       0:04:11.022 **********
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012 -> localhost]ESC[0m

TASK [remote/remote-install : 2nd polling: Wait for subcloud to install OS (this will take a while)] *************************************
Monday 08 April 2024  21:29:26 +0000 (0:00:00.894)       0:04:11.916 **********
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (100 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (99 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a
while) (98 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (97 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (96 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (95 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (94 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (93 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (92 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (91 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (90 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (89 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (88 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (87 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (86 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (85 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (84 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (83 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (82 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (81 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (80 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (79 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (78 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (77 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (76 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (75 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (74 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (73 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (72 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (71 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (70 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (69 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (68 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (67 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (66 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (65 retries left).ESC[0m
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012 -> localhost]ESC[0m

TASK [remote/remote-install : 2nd polling result: Fail if any error occurred] ************************************************************
Monday 08 April 2024  21:47:39 +0000 (0:18:13.378)       0:22:25.295 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-install : include_tasks] *********************************************************************************************
Monday 08 April 2024  21:47:39 +0000 (0:00:00.020)       0:22:25.316 **********
ESC[0;36mincluded: /home/szabota/playbooks/wr-installer-atlas-me/roles/remote/remote-install/tasks/set-time.yaml for welktxsr-931883-rh-le093s6-012ESC[0m

TASK [remote/remote-install : Test if remote host is pingable] ***************************************************************************
Monday 08 April 2024  21:47:39 +0000 (0:00:00.029)       0:22:25.345 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)]ESC[0m

TASK [remote/remote-install : Get subcloud system time] **********************************************************************************
Monday 08 April 2024  21:47:41 +0000 (0:00:02.099)       0:22:27.445 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-install : Print subcloud system time] ********************************************************************************
Monday 08 April 2024  21:47:43 +0000 (0:00:01.864)       0:22:29.310 **********
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012] => ESC[0m
ESC[0;32m  msg: 'subcloud system time: Mon 08 Apr 2024 09:47:43 PM UTC'ESC[0m

TASK [remote/remote-install : Stop NTP service] ******************************************************************************************
Monday 08 April 2024  21:47:43 +0000 (0:00:00.025)       0:22:29.335 **********
ESC[0;31mfatal: [welktxsr-931883-rh-le093s6-012]: FAILED! => changed=false ESC[0m
ESC[0;31m  msg: 'Could not find the requested service ntpd: host'ESC[0m
ESC[0;36m...ignoringESC[0m

TASK [remote/remote-install : Get central controller system time] ************************************************************************
Monday 08 April 2024  21:47:45 +0000 (0:00:01.808)       0:22:31.144 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)]ESC[0m

TASK [remote/remote-install : Print central controller system time] **********************************************************************
Monday 08 April 2024  21:47:47 +0000 (0:00:02.127)       0:22:33.272 **********
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012] => ESC[0m
ESC[0;32m  msg: 'central system time: Mon 08 Apr 2024 09:47:47 PM UTC'ESC[0m

:
TASK [remote/remote-install : Set subcloud system time by central controller system time] ************************************************
Monday 08 April 2024  21:47:47 +0000 (0:00:00.025)       0:22:33.297 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-install : Set subcloud system time by NTP server] ********************************************************************
Monday 08 April 2024  21:47:49 +0000 (0:00:01.423)       0:22:34.720 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-install : Start NTP service] *****************************************************************************************
Monday 08 April 2024  21:47:56 +0000 (0:00:07.545)       0:22:42.266 **********
ESC[0;31mfatal: [welktxsr-931883-rh-le093s6-012]: FAILED! => changed=false ESC[0m
ESC[0;31m  msg: 'Could not find the requested service ntpd: host'ESC[0m
ESC[0;36m...ignoringESC[0m

TASK [remote/remote-install : Sync system time to RT clock after adjustment] *************************************************************
Monday 08 April 2024  21:47:58 +0000 (0:00:01.555)       0:22:43.821 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-install : Get subcloud system time after adjustment] *****************************************************************
Monday 08 April 2024  21:47:59 +0000 (0:00:01.560)       0:22:45.381 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-install : Print subcloud system time after adjustment] ***************************************************************
Monday 08 April 2024  21:48:01 +0000 (0:00:01.392)       0:22:46.773 **********
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012] => ESC[0m
ESC[0;32m  msg: 'subcloud system time after adjustment: Mon 08 Apr 2024 09:48:00 PM UTC'ESC[0m

TASK [remote/remote-install : Set variable time_is_set to true so this code will not be executed again] **********************************
Monday 08 April 2024  21:48:01 +0000 (0:00:00.025)       0:22:46.799 **********
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-install : 3rd polling prep: Obtain Keystone auth token] **************************************************************
Monday 08 April 2024  21:48:01 +0000 (0:00:00.025)       0:22:46.825 **********
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012 -> localhost]ESC[0m

TASK [remote/remote-install : 3rd polling: Wait for subcloud to install OS (this may take a while)] **************************************
Monday 08 April 2024  21:48:02 +0000 (0:00:00.865)       0:22:47.690 **********
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012 -> localhost]ESC[0m

TASK [remote/remote-install : 3rd polling result: Fail if any error occurred] ************************************************************
Monday 08 April 2024  21:48:02 +0000 (0:00:00.495)       0:22:48.186 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-install : include_tasks] *********************************************************************************************
Monday 08 April 2024  21:48:02 +0000 (0:00:00.021)       0:22:48.207 **********
ESC[0;36mincluded: /home/szabota/playbooks/wr-installer-atlas-me/roles/remote/remote-install/tasks/set-time.yaml for welktxsr-931883-rh-le093s6-012ESC[0m

TASK [remote/remote-install : Test if remote host is pingable] ***************************************************************************
Monday 08 April 2024  21:48:02 +0000 (0:00:00.032)       0:22:48.240 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)]ESC[0m

TASK [remote/remote-install : Get subcloud system time] **********************************************************************************
Monday 08 April 2024  21:48:04 +0000 (0:00:02.084)       0:22:50.324 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-install : Print subcloud system time] ********************************************************************************
Monday 08 April 2024  21:48:06 +0000 (0:00:01.395)       0:22:51.720 **********
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012] => ESC[0m
ESC[0;32m  msg: 'subcloud system time: Mon 08 Apr 2024 09:48:05 PM UTC'ESC[0m

TASK [remote/remote-install : Stop NTP service] ******************************************************************************************
Monday 08 April 2024  21:48:06 +0000 (0:00:00.025)       0:22:51.745 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-install : Get central controller system time] ************************************************************************
Monday 08 April 2024  21:48:06 +0000 (0:00:00.018)       0:22:51.764 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-install : Print central controller system time] **********************************************************************
Monday 08 April 2024  21:48:06 +0000 (0:00:00.016)       0:22:51.781 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-install : Set subcloud system time by central controller system time] ************************************************
Monday 08 April 2024  21:48:06 +0000 (0:00:00.015)       0:22:51.796 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-install : Set subcloud system time by NTP server] ********************************************************************
Monday 08 April 2024  21:48:06 +0000 (0:00:00.014)       0:22:51.811 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-install : Start NTP service] *****************************************************************************************
Monday 08 April 2024  21:48:06 +0000 (0:00:00.016)       0:22:51.827 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-install : Sync system time to RT clock after adjustment] *************************************************************
Monday 08 April 2024  21:48:06 +0000 (0:00:00.016)       0:22:51.844 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-install : Get subcloud system time after adjustment] *****************************************************************
Monday 08 April 2024  21:48:06 +0000 (0:00:00.015)       0:22:51.859 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-install : Print subcloud system time after adjustment] ***************************************************************
Monday 08 April 2024  21:48:06 +0000 (0:00:00.015)       0:22:51.875 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-install : Set variable time_is_set to true so this code will not be executed again] **********************************
Monday 08 April 2024  21:48:06 +0000 (0:00:00.015)       0:22:51.891 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-install : 4th polling prep: Obtain Keystone auth token] **************************************************************
Monday 08 April 2024  21:48:06 +0000 (0:00:00.017)       0:22:51.909 **********
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012 -> localhost]ESC[0m

TASK [remote/remote-install : 4th polling: Wait for subcloud to install OS (this may still take a while)] ********************************
Monday 08 April 2024  21:48:07 +0000 (0:00:00.872)       0:22:52.781 **********
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still ta
ke a while) (100 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (99 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (98 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (97 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (96 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (95 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (94 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (93 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (92 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (91 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (90 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (89 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (88 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (87 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (86 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (85 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (84 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (83 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (82 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (81 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (80 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (79 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (78 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (77 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (76 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (75 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (74 retries left).ESC[0m
:
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still ta
ke a while) (73 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (72 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (71 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (70 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (69 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (68 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (67 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (66 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (65 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (64 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (63 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (62 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (61 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (60 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (59 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (58 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (57 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (56 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (55 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (54 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (53 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (52 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (51 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (50 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (49 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (48 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (47 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (46 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (45 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (44 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (43 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (42 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (41 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (40 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (39 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (38 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (37 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (36 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (35 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (34 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (33 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (32 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (31 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (30 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (29 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (28 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (27 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (26 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (25 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (24 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (23 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (22 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (21 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still ta
ke a while) (20 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (19 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (18 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (17 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (16 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (15 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (14 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (13 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (12 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (11 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (10 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (9 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (8 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (7 retries left).ESC[0m
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012 -> localhost]ESC[0m

TASK [remote/remote-install : 4th polling result: Fail if the installation failed] *******************************************************
Monday 08 April 2024  22:35:41 +0000 (0:47:34.327)       1:10:27.108 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-install : include_tasks] *********************************************************************************************
Monday 08 April 2024  22:35:41 +0000 (0:00:00.021)       1:10:27.130 **********
ESC[0;36mincluded: /home/szabota/playbooks/wr-installer-atlas-me/roles/remote/remote-install/tasks/set-time.yaml for welktxsr-931883-rh-le093s6-012ESC[0m

TASK [remote/remote-install : Test if remote host is pingable] ***************************************************************************
Monday 08 April 2024  22:35:41 +0000 (0:00:00.035)       1:10:27.165 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)]ESC[0m

TASK [remote/remote-install : Get subcloud system time] **********************************************************************************
Monday 08 April 2024  22:35:43 +0000 (0:00:02.119)       1:10:29.285 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-install : Print subcloud system time] ********************************************************************************
Monday 08 April 2024  22:35:45 +0000 (0:00:01.505)       1:10:30.790 **********
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012] => ESC[0m
ESC[0;32m  msg: 'subcloud system time: Mon 08 Apr 2024 10:35:44 PM UTC'ESC[0m

TASK [remote/remote-install : Stop NTP service] ******************************************************************************************
Monday 08 April 2024  22:35:45 +0000 (0:00:00.025)       1:10:30.816 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-install : Get central controller system time] ************************************************************************
Monday 08 April 2024  22:35:45 +0000 (0:00:00.019)       1:10:30.835 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-install : Print central controller system time] **********************************************************************
Monday 08 April 2024  22:35:45 +0000 (0:00:00.016)       1:10:30.852 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-install : Set subcloud system time by central controller system time] ************************************************
Monday 08 April 2024  22:35:45 +0000 (0:00:00.015)       1:10:30.867 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-install : Set subcloud system time by NTP server] ********************************************************************
Monday 08 April 2024  22:35:45 +0000 (0:00:00.014)       1:10:30.882 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-install : Start NTP service] *****************************************************************************************
Monday 08 April 2024  22:35:45 +0000 (0:00:00.017)       1:10:30.899 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-install : Sync system time to RT clock after adjustment] *************************************************************
Monday 08 April 2024  22:35:45 +0000 (0:00:00.015)       1:10:30.915 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-install : Get subcloud system time after adjustment] *****************************************************************
Monday 08 April 2024  22:35:45 +0000 (0:00:00.016)       1:10:30.932 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-install : Print subcloud system time after adjustment] ***************************************************************
Monday 08 April 2024  22:35:45 +0000 (0:00:00.018)       1:10:30.950 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-install : Set variable time_is_set to true so this code will not be executed again] **********************************
Monday 08 April 2024  22:35:45 +0000 (0:00:00.016)       1:10:30.967 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-install : 5th polling prep: Obtain Keystone auth token] **************************************************************
Monday 08 April 2024  22:35:45 +0000 (0:00:00.017)       1:10:30.985 **********
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012 -> localhost]ESC[0m

TASK [remote/remote-install : 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while)] *******************
Monday 08 April 2024  22:35:46 +0000 (0:00:00.866)       1:10:31.851 **********
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012 -> localhost]ESC[0m

TASK [remote/remote-install : 5th polling result: Fail if install/bootstrap/deploy failed] ***********************************************
Monday 08 April 2024  22:35:46 +0000 (0:00:00.498)       1:10:32.350 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-install : include_tasks] *********************************************************************************************
Monday 08 April 2024  22:35:46 +0000 (0:00:00.020)       1:10:32.370 **********
ESC[0;36mincluded: /home/szabota/playbooks/wr-installer-atlas-me/roles/remote/remote-install/tasks/set-time.yaml for welktxsr-931883-rh-le
093s6-012ESC[0m

TASK [remote/remote-install : Test if remote host is pingable] ***************************************************************************
Monday 08 April 2024  22:35:46 +0000 (0:00:00.038)       1:10:32.409 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)]ESC[0m

TASK [remote/remote-install : Get subcloud system time] **********************************************************************************
Monday 08 April 2024  22:35:48 +0000 (0:00:02.110)       1:10:34.519 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-install : Print subcloud system time] ********************************************************************************
Monday 08 April 2024  22:35:50 +0000 (0:00:01.545)       1:10:36.065 **********
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012] => ESC[0m
ESC[0;32m  msg: 'subcloud system time: Mon 08 Apr 2024 10:35:50 PM UTC'ESC[0m

TASK [remote/remote-install : Stop NTP service] ******************************************************************************************
Monday 08 April 2024  22:35:50 +0000 (0:00:00.025)       1:10:36.091 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-install : Get central controller system time] ************************************************************************
Monday 08 April 2024  22:35:50 +0000 (0:00:00.019)       1:10:36.110 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-install : Print central controller system time] **********************************************************************
Monday 08 April 2024  22:35:50 +0000 (0:00:00.016)       1:10:36.127 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-install : Set subcloud system time by central controller system time] ************************************************
Monday 08 April 2024  22:35:50 +0000 (0:00:00.016)       1:10:36.143 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-install : Set subcloud system time by NTP server] ********************************************************************
Monday 08 April 2024  22:35:50 +0000 (0:00:00.016)       1:10:36.159 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-install : Start NTP service] *****************************************************************************************
Monday 08 April 2024  22:35:50 +0000 (0:00:00.016)       1:10:36.176 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-install : Sync system time to RT clock after adjustment] *************************************************************
Monday 08 April 2024  22:35:50 +0000 (0:00:00.016)       1:10:36.192 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-install : Get subcloud system time after adjustment] *****************************************************************
Monday 08 April 2024  22:35:50 +0000 (0:00:00.014)       1:10:36.207 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-install : Print subcloud system time after adjustment] ***************************************************************
Monday 08 April 2024  22:35:50 +0000 (0:00:00.015)       1:10:36.222 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-install : Set variable time_is_set to true so this code will not be executed again] **********************************
Monday 08 April 2024  22:35:50 +0000 (0:00:00.015)       1:10:36.238 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-install : 6th polling prep: Obtain Keystone auth token] **************************************************************
Monday 08 April 2024  22:35:50 +0000 (0:00:00.017)       1:10:36.256 **********
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012 -> localhost]ESC[0m

TASK [remote/remote-install : 6th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while)] *******************
Monday 08 April 2024  22:35:51 +0000 (0:00:00.905)       1:10:37.161 **********
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012 -> localhost]ESC[0m

TASK [remote/remote-install : include_tasks] *********************************************************************************************
Monday 08 April 2024  22:35:51 +0000 (0:00:00.463)       1:10:37.625 **********
ESC[0;36mincluded: /home/szabota/playbooks/wr-installer-atlas-me/roles/remote/remote-utility/tasks/disable_mwait.yaml for welktxsr-931883-rh-le093s6-012ESC[0m

TASK [remote/remote-install : Disable mwait for ZTS Proteus] *****************************************************************************
Monday 08 April 2024  22:35:51 +0000 (0:00:00.048)       1:10:37.674 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-install : 6th polling result: Fail if bootstrap/deploy failed] *******************************************************
Monday 08 April 2024  22:35:52 +0000 (0:00:00.017)       1:10:37.691 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-install : include_tasks] *********************************************************************************************
Monday 08 April 2024  22:35:52 +0000 (0:00:00.019)       1:10:37.711 **********
ESC[0;36mincluded: /home/szabota/playbooks/wr-installer-atlas-me/roles/remote/remote-install/tasks/set-time.yaml for welktxsr-931883-rh-le093s6-012ESC[0m

TASK [remote/remote-install : Test if remote host is pingable] ***************************************************************************
Monday 08 April 2024  22:35:52 +0000 (0:00:00.042)       1:10:37.754 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)]ESC[0m

TASK [remote/remote-install : Get subcloud system time] **********************************************************************************
Monday 08 April 2024  22:35:54 +0000 (0:00:02.091)       1:10:39.845 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-install : Print subcloud system time] ********************************************************************************
Monday 08 April 2024  22:35:55 +0000 (0:00:01.580)       1:10:41.426 **********
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012] => ESC[0m
ESC[0;32m  msg: 'subcloud system time: Mon 08 Apr 2024 10:35:55 PM UTC'ESC[0m

TASK [remote/remote-install : Stop NTP service] ******************************************************************************************
Monday 08 April 2024  22:35:55 +0000 (0:00:00.026)       1:10:41.452 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-install : Get central controller system time] ************************************************************************
Monday 08 April 2024  22:35:55 +0000 (0:00:00.018)       1:10:41.471 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-install : Print central controller system time] **********************************************************************
Monday 08 April 2024  22:35:55 +0000 (0:00:00.016)       1:10:41.487 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-install : Set subcloud system time by central controller system time] ************************************************
Monday 08 April 2024  22:35:55 +0000 (0:00:00.015)       1:10:41.503 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-install : Set subcloud system time by NTP server] ********************************************************************
Monday 08 April 2024  22:35:55 +0000 (0:00:00.015)       1:10:41.518 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-install : Start NTP service] *****************************************************************************************
Monday 08 April 2024  22:35:55 +0000 (0:00:00.016)       1:10:41.534 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-install : Sync system time to RT clock after adjustment] *************************************************************
Monday 08 April 2024  22:35:55 +0000 (0:00:00.015)       1:10:41.550 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-install : Get subcloud system time after adjustment] *****************************************************************
Monday 08 April 2024  22:35:55 +0000 (0:00:00.015)       1:10:41.566 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-install : Print subcloud system time after adjustment] ***************************************************************
Monday 08 April 2024  22:35:55 +0000 (0:00:00.016)       1:10:41.582 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-install : Set variable time_is_set to true so this code will not be executed again] **********************************
Monday 08 April 2024  22:35:55 +0000 (0:00:00.015)       1:10:41.597 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-install : Wait for controller-0 restart] *****************************************************************************
Monday 08 April 2024  22:35:55 +0000 (0:00:00.015)       1:10:41.612 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-install : Wait for controller-0 recovery] ****************************************************************************
Monday 08 April 2024  22:35:55 +0000 (0:00:00.021)       1:10:41.634 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/remote-install : setup kdump] ***********************************************************************************************
Monday 08 April 2024  22:35:55 +0000 (0:00:00.018)       1:10:41.652 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [Wait for hosts and system to be reconciled] ****************************************************************************************
Monday 08 April 2024  22:35:55 +0000 (0:00:00.018)       1:10:41.671 **********

TASK [common/wait_for_reconciliation : Making sure node is reachable] ********************************************************************
Monday 08 April 2024  22:35:56 +0000 (0:00:00.028)       1:10:41.699 **********
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [common/wait_for_reconciliation : Wait for K8s API to be up] ************************************************************************
Monday 08 April 2024  22:35:57 +0000 (0:00:01.687)       1:10:43.386 **********
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [common/wait_for_reconciliation : Wait for all 3 hosts to show up] ******************************************************************
Monday 08 April 2024  22:35:59 +0000 (0:00:01.722)       1:10:45.109 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [common/wait_for_reconciliation : Wait for hosts to be reconciled] ******************************************************************
Monday 08 April 2024  22:35:59 +0000 (0:00:00.024)       1:10:45.133 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [common/wait_for_reconciliation : Wait for systems to be reconciled] ****************************************************************
Monday 08 April 2024  22:36:01 +0000 (0:00:01.551)       1:10:46.685 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [Remote Manage] *********************************************************************************************************************
Monday 08 April 2024  22:36:02 +0000 (0:00:01.599)       1:10:48.284 **********

TASK [remote/manage : 1st Obtain Keystone auth token] ************************************************************************************
Monday 08 April 2024  22:36:02 +0000 (0:00:00.071)       1:10:48.356 **********
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012 -> localhost]ESC[0m

TASK [remote/manage : 1st Wait for contoller-0 availability status online] ***************************************************************
Monday 08 April 2024  22:36:03 +0000 (0:00:01.061)       1:10:49.417 **********
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 1st Wait for contoller-0 availability status online (100 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012 -> localhost]: 1st Wait for contoller-0 availability status online (99 retries left).ESC[0m
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012 -> localhost]ESC[0m

TASK [remote/manage : 2nd Obtain Keystone auth token] ************************************************************************************
Monday 08 April 2024  22:37:04 +0000 (0:01:01.219)       1:11:50.637 **********
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012 -> localhost]ESC[0m

TASK [remote/manage : 2nd Wait for contoller-0 availability status online] ***************************************************************
Monday 08 April 2024  22:37:05 +0000 (0:00:00.954)       1:11:51.591 **********
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012 -> localhost]ESC[0m

TASK [remote/manage : Wait for system to stabilize before running kubectl] ***************************************************************
Monday 08 April 2024  22:37:06 +0000 (0:00:00.507)       1:11:52.098 **********
Pausing for 480 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [Wait for system and hosts to be reconciled] ****************************************************************************************
Monday 08 April 2024  22:45:06 +0000 (0:08:00.020)       1:19:52.118 **********

TASK [common/wait_for_reconciliation : Making sure node is reachable] ********************************************************************
Monday 08 April 2024  22:45:06 +0000 (0:00:00.027)       1:19:52.145 **********
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [common/wait_for_reconciliation : Wait for K8s API to be up] ************************************************************************
Monday 08 April 2024  22:45:07 +0000 (0:00:01.480)       1:19:53.626 **********
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [common/wait_for_reconciliation : Wait for all 3 hosts to show up] ******************************************************************
Monday 08 April 2024  22:45:09 +0000 (0:00:01.475)       1:19:55.101 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m
TASK [common/wait_for_reconciliation : Wait for hosts to be reconciled] ******************************************************************
Monday 08 April 2024  22:45:09 +0000 (0:00:00.016)       1:19:55.118 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [common/wait_for_reconciliation : Wait for systems to be reconciled] ****************************************************************
Monday 08 April 2024  22:45:10 +0000 (0:00:01.505)       1:19:56.624 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/manage : Wait for distributed cloud to be reconciled but subcloud OAM VIP becomes unreachable] ******************************
Monday 08 April 2024  22:45:12 +0000 (0:00:01.502)       1:19:58.127 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/manage : Check if the subcloud deployed but failed] *************************************************************************
Monday 08 April 2024  22:45:12 +0000 (0:00:00.026)       1:19:58.153 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)]ESC[0m

TASK [remote/manage : Set distributed cloud state to managed] ****************************************************************************
Monday 08 April 2024  22:45:18 +0000 (0:00:05.874)       1:20:04.028 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)]ESC[0m

TASK [remote/manage : Wait for system to stabilize] **************************************************************************************
Monday 08 April 2024  22:45:24 +0000 (0:00:05.911)       1:20:09.939 **********
Pausing for 300 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [Remote Trust] **********************************************************************************************************************
Monday 08 April 2024  22:50:24 +0000 (0:05:00.020)       1:25:09.959 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [Remote Starlingx] ******************************************************************************************************************
Monday 08 April 2024  22:50:24 +0000 (0:00:00.022)       1:25:09.982 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [Remote Starlingx and Registry] *****************************************************************************************************
Monday 08 April 2024  22:50:24 +0000 (0:00:00.020)       1:25:10.002 **********

TASK [remote/starlingx : Copy ICA cert] **************************************************************************************************
Monday 08 April 2024  22:50:24 +0000 (0:00:00.069)       1:25:10.072 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012] => (item={'filename': 'vz_root_ica_cert.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIFNzCCAx+gAwIBAgIUGLJR/hP48n+vdq2v1hcfspXo/78wDQYJKoZIhvcNAQEL\nBQAwWjELMAkGA1UEBhMCVVMxEDAOBgNVBAoMB1Zlcml6b24xEzARBgNVBAsMClZa\nSUFNIFRlc3QxJDAiBgNVBAMMG1Zlcml6b24gTmV0d29yayBSU0EgQ0EgVGVzdDAe\nFw0yMDEwMjIyMTE0MDNaFw0zMDEwMjIyMTE0MDNaMIGRMQswCQYDVQQGEwJVUzEL\nMAkGA1UECAwCVFgxETAPBgNVBAcMCFdlc3RsYWtlMRAwDgYDVQQKDAdWZXJpem9u\nMR0wGwYDVQQLDBRWZXJpem9uIFNvdXJjaW5nIExMQzExMC8GA1UEAwwoVmVyaXpv\nbiBOZXR3b3JrIFdFTEtUWElCIExBQiAxIDMgUlNBIElDQTCCASIwDQYJKoZIhvcN\nAQEBBQADggEPADCCAQoCggEBANhkGTXOCKEYf5znDDeX3n/DHFPVqazgQsr0/SIG\n4eb1JY5q5Jq3ZhAaZCr9HJuCkwAP/zgYH0llqOvf8AC2Uh+7z1b33IbwxPmJfWCP\nAqSNFkLWWVRdbELapCu408QsrLMW8IrdP6PLiKAepwncfm4T0/6bANqIEmUkpw8Q\nxProeiNwlGbwUll+tELmdCk7vA7hKX3j1kUvS5Z84Z5ivJBWEcUEggmC97TK4aLo\nFVEHbyahze568JVEaM1vY5L4mnRRTl+u5ipaSMxVBsiXzF7eFuKCzqF7wxbDIt2T\nIFEJtwyJDW5bXjyXgiF1d5H/URprUcRV9Qmf2+PXcfwHII8CAwEAAaOBvDCBuTAS\nBgNVHRMBAf8ECDAGAQH/AgEAMA4GA1UdDwEB/wQEAwIBBjAfBgNVHSMEGDAWgBQl\neng3lqGBeTrbLVuABoEmUHm1+TBTBgNVHR8ETDBKMEigRqBEhkJodHRwOi8vc2Vj\ndXJlLnN0YWdpbmcuc2VjdXJpdHljcmVkZW50aWFsaW5nLmNvbS9jcmwvdnpuZXRy\nc2FjYS5jcmwwHQYDVR0OBBYEFP0Z+/vaDLtAoFig1I9ttNKnmzByMA0GCSqGSIb3\nDQEBCwUAA4ICAQBuXVTf9e01HeymHgRcFCwP2N6G6u+vIzY8Bz0zSUZeRDHMZQcS\nNoabDyn5FfGJlw4BqGC591Sp0/unFQDzAg17rDBcrgwajeFeUiFdb9PiAJwHaX9S\nvq/7VmVLCmpeb+a/laXAe6+tkY1kcFrd1+ItRKC6ZGXMsoDkmk5Ndxxgw77estcI\nMiiLQbvpXRygX5wD4/ayazuLms9qITZkOZ1nTLVqq7QrwYCsSoih7hj6sbsfXr19\nGoYWmk8Y7O/d3ttgyHuRH9k/2dQ/xL7avRpMNkPdr7ocJqI46hvx2X6UyOo7IBua\nkSkFbSmPZWIVAidNMBOnvffCQ32tfjT2/xso/a9cdskvxqgLi0MPARU9Nl2Pufsb\nD7l4/sBvz/PiNTKp+Daa9FdyLb9ySidos1uS0c24bUtY1RXXGAVV2qgfyrzvzfye\nSM+w16hMU/yeYiuA1jsPmsnZnuIJj4Nv8ZjjZ0WS53pP5wcghaHkBrqWQNT8meqA\nVElrMBPlYq67T+AXP0B9lf5Sc3QVIio7XKKfqrlcQxY2JGLEyE53JgZGX7dpwU4I\nukLvyHbT4p06oY3qG6+wH8+YIXCNAYtadJ/C5/u9GcLX5NnZrcuduj0inw2/a3Ao\nWgCt6/Pr28BkCvkWdDt9d8Z40qeu1aZdcr157mR+yZGPfBfB2vasrNIEwQ==\n-----END CERTIFICATE-----\n'})ESC[0m
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012] => (item={'filename': 'vz_root_ica_key.pem', 'value': '-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA2GQZNc4IoRh/nOcMN5fef8McU9WprOBCyvT9Igbh5vUljmrk\nmrdmEBpkKv0cm4KTAA//OBgfSWWo69/wALZSH7vPVvfchvDE+Yl9YI8CpI0WQtZZ\nVF1sQtqkK7jTxCyssxbwit0/o8uIoB6nCdx+bhPT/psA2ogSZSSnDxDE+uh6I3CU\nZvBSWX60QuZ0KTu8DuEpfePWRS9LlnzhnmK8kFYRxQSCCYL3tMrhougVUQdvJqHN\n7nrwlURozW9jkviadFFOX67mKlpIzFUGyJfMXt4W4oLOoXvDFsMi3ZMgUQm3DIkN\nbltePJeCIXV3kf9RGmtRxFX1CZ/b49dx/AcgjwIDAQABAoIBABSd1NkPfDr8/ouQ\nZ9WUHprFmBlUrgnOhA6aMNPhG/zJNn7PKGClQJAgM5L08pjOY/sJiyNpCPIRQXrX\npyIqPMDRP/vlOZmRrvKnas6cUYAkAQ71JSWokPv9oM6ZmXODXiDh+qEAW2PbrHS0\n9u01mMYcFYKYeghYFoiUaWZCDsJo3v3dgeE9aQ4tB9ksovSmWrpuCY7NKbd7Qrbo\n5XxQhkujTkE6knOHz8CVwYETtj8LZ/bvHIkGMGvRvwsKYDZkIKr5CZ7DX+KcMfPN\neMZU4VCHYSXNxsyp5DJ1Zw+gx8/32kUL0CzJLLam1G021Hq41KPwwSV/KPrOKel7\nHXDLXeECgYEA8MR+lgxGjYTc/k4TdZvcFVgqHGLXnyjO7ZVt4b7UpwmayLuoSD/M\nOpHQYX+JBIIWTNlGhG8UV3DPC3v+auhYa7twwbekS30IYCAmu5GCKgMAcWFinz6A\nYZxG55P/hShetCyOqikgwXqzMlwGs8KEul8f8BKssROzUy8mIlFhjq0CgYEA5hTM\nSNxAD3dlRtb0771fBU7fjx8JPfjptP9vP/JVEelkc/ti9nZ5buTC+9cQC/B+YFx7\nc82uCrXV13bGR9iH8xBhwU7JOYJZbgCpwp0F56wIN5Pdk9Eo79Batrw3oGBG4Yvt\nDc2eltxQbHgObc/qygf88j9XqD8aGIvQrc4Jf6sCgYAtxX03M1A6WTbWFau3YRD+\n8crXqKbLOCvWmODR2MB+nOHTJXHBgndl7xCJaIB43e41X9z7Ek7wrJ5/1WuxkUg1\n+uVdvna6byOnepVCdVAkgnuUEmp4UZ6AcAA+yDD8dIdEg2//w1/ZyGTGvx37EJDB\nCZJ9xl8ULuWZe84pGgWM5QKBgQCYVUbYKrNjShrM5z9uh4QlII6V1Oeql2YtBz4i\nKZE3db6jp9pi8hf+WwnZ8g9WyFjz9edqydAkmTXHHYW0ReHlBYCjm0VRhUMuuNOs\n3YfuVpFuMsFuv/oJpXqaKE3wKi5j4OAH1o7ctWuuFWMAQ7vhHZ7UySmBZJ4jiFaW\n7KaPVwKBgE8E0xbSDVGxXbEGwRXxeaOSemEHD9uEnbAyq1p3EBBhBvInWmDiP5vJ\n68IYNZ4SGxXEKDifwrLGHyekt3RK9B2+U03okd1qH7gfBIlxBJivcjhBe2PtK/Qj\n6fBN0fC1UJoE6pseT9cJDaBq2wMRXJGRYtT8fU9PPJcfa23JlKNS\n-----END RSA PRIVATE KEY-----'})ESC[0m

TASK [remote/starlingx : Create VZ ICA secret to back the clusterIssuer] *****************************************************************
Monday 08 April 2024  22:50:29 +0000 (0:00:05.397)       1:25:15.469 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/starlingx : Create VZ ICA clusterIssuer] ************************************************************************************
Monday 08 April 2024  22:50:31 +0000 (0:00:01.547)       1:25:17.016 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/starlingx : Make sure VZ ICA clusterIssuer is Ready before proceeding] ******************************************************
Monday 08 April 2024  22:50:32 +0000 (0:00:01.652)       1:25:18.669 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/starlingx : create Rest Api (starlingx) certificate] ************************************************************************
Monday 08 April 2024  22:50:34 +0000 (0:00:01.523)       1:25:20.193 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/starlingx : make sure Rest Api (starlingx) certificate is Ready before proceeding] ******************************************
Monday 08 April 2024  22:50:36 +0000 (0:00:01.817)       1:25:22.011 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/starlingx : wait until system configuration is updated] *********************************************************************
Monday 08 April 2024  22:50:37 +0000 (0:00:01.549)       1:25:23.560 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/starlingx : create registry certificate] ************************************************************************************
Monday 08 April 2024  22:50:42 +0000 (0:00:04.894)       1:25:28.455 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/starlingx : make sure registry certificate is Ready before proceeding] ******************************************************
Monday 08 April 2024  22:50:44 +0000 (0:00:01.686)       1:25:30.141 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/starlingx : wait until system configuration is updated] *********************************************************************
Monday 08 April 2024  22:50:46 +0000 (0:00:01.741)       1:25:31.883 **********
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012]: wait until system configuration is updated (20 retries left).ESC[0m
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [Remote Integ] **********************************************************************************************************************
Monday 08 April 2024  22:51:26 +0000 (0:00:40.547)       1:26:12.430 **********

TASK [remote/integ : Detect applied status of platform-integ-apps application] ***********************************************************
Monday 08 April 2024  22:51:26 +0000 (0:00:00.061)       1:26:12.492 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/integ : Fail if platform-integ-apps application apply failed] ***************************************************************
Monday 08 April 2024  22:51:31 +0000 (0:00:05.082)       1:26:17.574 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [Remote Ldap] ***********************************************************************************************************************
Monday 08 April 2024  22:51:31 +0000 (0:00:00.030)       1:26:17.605 **********

TASK [remote/ldap : Create temporary working directory] **********************************************************************************
Monday 08 April 2024  22:51:32 +0000 (0:00:00.151)       1:26:17.757 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/ldap : Copy SSL root certificates] ******************************************************************************************
Monday 08 April 2024  22:51:32 +0000 (0:00:00.031)       1:26:17.788 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012] => (item={'filename': 'vz_root_ca_cert.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIFpTCCA42gAwIBAgIUa3vZ0YGxO1TQ8NwhiVfQC0JslXgwDQYJKoZIhvcNAQEL\nBQAwWjELMAkGA1UEBhMCVVMxEDAOBgNVBAoMB1Zlcml6b24xEzARBgNVBAsMClZa\nSUFNIFRlc3QxJDAiBgNVBAMMG1Zlcml6b24gTmV0d29yayBSU0EgQ0EgVGVzdDAe\nFw0yMDA2MTUyMTAxMTNaFw0zNTA2MTUyMTAxMTNaMFoxCzAJBgNVBAYTAlVTMRAw\nDgYDVQQKDAdWZXJpem9uMRMwEQYDVQQLDApWWklBTSBUZXN0MSQwIgYDVQQDDBtW\nZXJpem9uIE5ldHdvcmsgUlNBIENBIFRlc3QwggIiMA0GCSqGSIb3DQEBAQUAA4IC\nDwAwggIKAoICAQC8AIrksI57CbIl5uGZ6yqfpQj3aK+N8f1EVHdwK9JFskoipvC8\n7yFTk8tgmO1i0YA5oRGfNxneqCdrXZiWL6Ko8v/iln9vuN+2rK3rgWZPPRJBAsBN\na49L7U6lJjIGxIZtZqmK5h47oiUtwlYVrbZMN2ijuBQ22/eQ9tsFDV28oBuZ3WAR\npSSbj/tubPQYkw3YYOhv/VpEpsd0rkoEt3QCmTVcX2rtblanpXowTV5R0Hy4014n\nT49jrEo40r4mwYoyS835Uv4ENUFA+pXicT9eUot3RSH6rYdx4A/14UtoI9U0ol8M\n62GHpxSASQ2Kc3yQWvxRGTFslTduYM+vVmMLEDDdqcsjYnStPpwdxxmKItmbjxSv\nIwYIndp8A04WkX2iiJCciC3BNxiLamPtYVyB1HHqbGTGirKYuSvwZt337q1OI3WH\nwVn2S4Mj/wqa4iCyGTvFSUnGq34Xkrb9XNwWBok9Tc2XWGAU/mb/xcd1hX74GZbF\nsrZ11aPtym4kMAjU2KQi96GcAH2lnGZYoOja1J4Cs4WYx1uAx74H/m84CrYavVfl\n1ONJVLDfuZaEkSmu+jHQX15pAECNORTuLD06PbWnOEcOi1xmbt/OT3SA3rhD2mb7\n2wxl7oJpV3ap8xGwYmxiFzmInxFJ1axjg8Rimol0mXTKAy6OdNHbCOnAwwIDAQAB\no2MwYTAPBgNVHRMBAf8EBTADAQH/MA4GA1UdDwEB/wQEAwIBBjAfBgNVHSMEGDAW\ngBQleng3lqGBeTrbLVuABoEmUHm1+TAdBgNVHQ4EFgQUJXp4N5ahgXk62y1bgAaB\nJlB5tfkwDQYJKoZIhvcNAQELBQADggIBADQ9jpmVh9nyY7ZQ4s+S9RuSRYn7QsrW\nDePeMzQgh8ZtS8WE65GY5HS61iHNP2Co8Q1lAaBWF4ipq+VZOcQbPLccHzd1kZv4\ns4u0aTzBd9ccidl73FS0DJDQOBbzPSzgsaiGHSMyGzkTeA8z3ntsSqrXXcDUvoRi\nFus/110AwdtNhJLrWveX6btYtHp9Lqe0YtNCy5AaXlrr1yRSckP5BWVtlwD4dzSO\n/dqI3wHS/ncUx9wSQomZ+AmxYW3KtJQKgHzTqHru1x9BBk7Bzfz9FZr6HLLmEitj\nuFoDRd5TNt5LbO0zDQokvY3oqso6Htup/rS7C08mcmnelYE+yXuOc1YrlyGnpBzk\nmy+1VYbOxRRdqKAZRbE72u/h847IVpsOvjR51iksuCAurZdp2+y2zvV8NhWekuNy\nirECRy9cb4YasjRaKi0/TCGPVSICuLyeG2W72liCj/N2VKfjPP9zsOR5XjwCXfRg\n+9xhLy77/gov2NWXx5fzTkhxCrHOxFdLVMn0wQhksDmw6QsXzDIHSpIOypdDfnx9\nCsthx3nhkuHLUaEP22D22dG+vImA9ukj4R/RRI/87jmi9Q8+ehH+NqN0GZZcLjdN\nSLVXpncuwWQFUDPR06wNkkkmBSXWiIYhwqSpU0Pl3er3fD0uWvXuWPm2PzfOmUAE\nUrkzyw9XmLw0\n-----END CERTIFICATE-----\n'}) ESC[0m
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012] => (item={'filename': 'vz_root_ica_cert.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIFNzCCAx+gAwIBAgIUGLJR/hP48n+vdq2v1hcfspXo/78wDQYJKoZIhvcNAQEL\nBQAwWjELMAkGA1UEBhMCVVMxEDAOBgNVBAoMB1Zlcml6b24xEzARBgNVBAsMClZa\nSUFNIFRlc3QxJDAiBgNVBAMMG1Zlcml6b24gTmV0d29yayBSU0EgQ0EgVGVzdDAe\nFw0yMDEwMjIyMTE0MDNaFw0zMDEwMjIyMTE0MDNaMIGRMQswCQYDVQQGEwJVUzEL\nMAkGA1UECAwCVFgxETAPBgNVBAcMCFdlc3RsYWtlMRAwDgYDVQQKDAdWZXJpem9u\nMR0wGwYDVQQLDBRWZXJpem9uIFNvdXJjaW5nIExMQzExMC8GA1UEAwwoVmVyaXpv\nbiBOZXR3b3JrIFdFTEtUWElCIExBQiAxIDMgUlNBIElDQTCCASIwDQYJKoZIhvcN\nAQEBBQADggEPADCCAQoCggEBANhkGTXOCKEYf5znDDeX3n/DHFPVqazgQsr0/SIG\n4eb1JY5q5Jq3ZhAaZCr9HJuCkwAP/zgYH0llqOvf8AC2Uh+7z1b33IbwxPmJfWCP\nAqSNFkLWWVRdbELapCu408QsrLMW8IrdP6PLiKAepwncfm4T0/6bANqIEmUkpw8Q\nxProeiNwlGbwUll+tELmdCk7vA7hKX3j1kUvS5Z84Z5ivJBWEcUEggmC97TK4aLo\nFVEHbyahze568JVEaM1vY5L4mnRRTl+u5ipaSMxVBsiXzF7eFuKCzqF7wxbDIt2T\nIFEJtwyJDW5bXjyXgiF1d5H/URprUcRV9Qmf2+PXcfwHII8CAwEAAaOBvDCBuTAS\nBgNVHRMBAf8ECDAGAQH/AgEAMA4GA1UdDwEB/wQEAwIBBjAfBgNVHSMEGDAWgBQl\neng3lqGBeTrbLVuABoEmUHm1+TBTBgNVHR8ETDBKMEigRqBEhkJodHRwOi8vc2Vj\ndXJlLnN0YWdpbmcuc2VjdXJpdHljcmVkZW50aWFsaW5nLmNvbS9jcmwvdnpuZXRy\nc2FjYS5jcmwwHQYDVR0OBBYEFP0Z+/vaDLtAoFig1I9ttNKnmzByMA0GCSqGSIb3\nDQEBCwUAA4ICAQBuXVTf9e01HeymHgRcFCwP2N6G6u+vIzY8Bz0zSUZeRDHMZQcS\nNoabDyn5FfGJlw4BqGC591Sp0/unFQDzAg17rDBcrgwajeFeUiFdb9PiAJwHaX9S\nvq/7VmVLCmpeb+a/laXAe6+tkY1kcFrd1+ItRKC6ZGXMsoDkmk5Ndxxgw77estcI\nMiiLQbvpXRygX5wD4/ayazuLms9qITZkOZ1nTLVqq7QrwYCsSoih7hj6sbsfXr19\nGoYWmk8Y7O/d3ttgyHuRH9k/2dQ/xL7avRpMNkPdr7ocJqI46hvx2X6UyOo7IBua\nkSkFbSmPZWIVAidNMBOnvffCQ32tfjT2/xso/a9cdskvxqgLi0MPARU9Nl2Pufsb\nD7l4/sBvz/PiNTKp+Daa9FdyLb9ySidos1uS0c24bUtY1RXXGAVV2qgfyrzvzfye\nSM+w16hMU/yeYiuA1jsPmsnZnuIJj4Nv8ZjjZ0WS53pP5wcghaHkBrqWQNT8meqA\nVElrMBPlYq67T+AXP0B9lf5Sc3QVIio7XKKfqrlcQxY2JGLEyE53JgZGX7dpwU4I\nukLvyHbT4p06oY3qG6+wH8+YIXCNAYtadJ/C5/u9GcLX5NnZrcuduj0inw2/a3Ao\nWgCt6/Pr28BkCvkWdDt9d8Z40qeu1aZdcr157mR+yZGPfBfB2vasrNIEwQ==\n-----END CERTIFICATE-----\n'}) ESC[0m
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012] => (item={'filename': 'vz_root_ica_key.pem', 'value': '-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA2GQZNc4IoRh/nOcMN5fef8McU9WprOBCyvT9Igbh5vUljmrk\nmrdmEBpkKv0cm4KTAA//OBgfSWWo69/wALZSH7vPVvfchvDE+Yl9YI8CpI0WQtZZ\nVF1sQtqkK7jTxCyssxbwit0/o8uIoB6nCdx+bhPT/psA2ogSZSSnDxDE+uh6I3CU\nZvBSWX60QuZ0KTu8DuEpfePWRS9LlnzhnmK8kFYRxQSCCYL3tMrhougVUQdvJqHN\n7nrwlURozW
9jkviadFFOX67mKlpIzFUGyJfMXt4W4oLOoXvDFsMi3ZMgUQm3DIkN\nbltePJeCIXV3kf9RGmtRxFX1CZ/b49dx/AcgjwIDAQABAoIBABSd1NkPfDr8/ouQ\nZ9WUHprFmBlUrgnOhA6aMNPhG/zJNn7PKGClQJAgM5L08pjOY/sJiyNpCPIRQXrX\npyIqPMDRP/vlOZmRrvKnas6cUYAkAQ71JSWokPv9oM6ZmXODXiDh+qEAW2PbrHS0\n9u01mMYcFYKYeghYFoiUaWZCDsJo3v3dgeE9aQ4tB9ksovSmWrpuCY7NKbd7Qrbo\n5XxQhkujTkE6knOHz8CVwYETtj8LZ/bvHIkGMGvRvwsKYDZkIKr5CZ7DX+KcMfPN\neMZU4VCHYSXNxsyp5DJ1Zw+gx8/32kUL0CzJLLam1G021Hq41KPwwSV/KPrOKel7\nHXDLXeECgYEA8MR+lgxGjYTc/k4TdZvcFVgqHGLXnyjO7ZVt4b7UpwmayLuoSD/M\nOpHQYX+JBIIWTNlGhG8UV3DPC3v+auhYa7twwbekS30IYCAmu5GCKgMAcWFinz6A\nYZxG55P/hShetCyOqikgwXqzMlwGs8KEul8f8BKssROzUy8mIlFhjq0CgYEA5hTM\nSNxAD3dlRtb0771fBU7fjx8JPfjptP9vP/JVEelkc/ti9nZ5buTC+9cQC/B+YFx7\nc82uCrXV13bGR9iH8xBhwU7JOYJZbgCpwp0F56wIN5Pdk9Eo79Batrw3oGBG4Yvt\nDc2eltxQbHgObc/qygf88j9XqD8aGIvQrc4Jf6sCgYAtxX03M1A6WTbWFau3YRD+\n8crXqKbLOCvWmODR2MB+nOHTJXHBgndl7xCJaIB43e41X9z7Ek7wrJ5/1WuxkUg1\n+uVdvna6byOnepVCdVAkgnuUEmp4UZ6AcAA+yDD8dIdEg2//w1/ZyGTGvx37EJDB\nCZJ9xl8ULuWZe84pGgWM5QKBgQCYVUbYKrNjShrM5z9uh4QlII6V1Oeql2YtBz4i\nKZE3db6jp9pi8hf+WwnZ8g9WyFjz9edqydAkmTXHHYW0ReHlBYCjm0VRhUMuuNOs\n3YfuVpFuMsFuv/oJpXqaKE3wKi5j4OAH1o7ctWuuFWMAQ7vhHZ7UySmBZJ4jiFaW\n7KaPVwKBgE8E0xbSDVGxXbEGwRXxeaOSemEHD9uEnbAyq1p3EBBhBvInWmDiP5vJ\n68IYNZ4SGxXEKDifwrLGHyekt3RK9B2+U03okd1qH7gfBIlxBJivcjhBe2PtK/Qj\n6fBN0fC1UJoE6pseT9cJDaBq2wMRXJGRYtT8fU9PPJcfa23JlKNS\n-----END RSA PRIVATE KEY-----'}) ESC[0m

TASK [remote/ldap : Copy templates] ******************************************************************************************************
Monday 08 April 2024  22:51:32 +0000 (0:00:00.038)       1:26:17.826 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012] => (item={'name': 'req-ldap.cnf', 'mode': '0644'}) ESC[0m

TASK [remote/ldap : Generate SSL cert] ***************************************************************************************************
Monday 08 April 2024  22:51:32 +0000 (0:00:00.025)       1:26:17.852 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/ldap : Copy templates] ******************************************************************************************************
Monday 08 April 2024  22:51:32 +0000 (0:00:00.021)       1:26:17.873 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012] => (item={'name': 'dex-overrides.yaml', 'mode': '0644'}) ESC[0m

TASK [remote/ldap : Copy SSL dex certs to server] ****************************************************************************************
Monday 08 April 2024  22:51:32 +0000 (0:00:00.023)       1:26:17.897 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012] => (item=dex-cert.pem) ESC[0m
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012] => (item=dex-key.pem) ESC[0m
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012] => (item=dex-ca.pem) ESC[0m

TASK [remote/ldap : Copy SSL AD cert to server] ******************************************************************************************
Monday 08 April 2024  22:51:32 +0000 (0:00:00.024)       1:26:17.922 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012] => (item={'filename': 'ad_ca.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIFpTCCA42gAwIBAgIUa3vZ0YGxO1TQ8NwhiVfQC0JslXgwDQYJKoZIhvcNAQEL\nBQAwWjELMAkGA1UEBhMCVVMxEDAOBgNVBAoMB1Zlcml6b24xEzARBgNVBAsMClZa\nSUFNIFRlc3QxJDAiBgNVBAMMG1Zlcml6b24gTmV0d29yayBSU0EgQ0EgVGVzdDAe\nFw0yMDA2MTUyMTAxMTNaFw0zNTA2MTUyMTAxMTNaMFoxCzAJBgNVBAYTAlVTMRAw\nDgYDVQQKDAdWZXJpem9uMRMwEQYDVQQLDApWWklBTSBUZXN0MSQwIgYDVQQDDBtW\nZXJpem9uIE5ldHdvcmsgUlNBIENBIFRlc3QwggIiMA0GCSqGSIb3DQEBAQUAA4IC\nDwAwggIKAoICAQC8AIrksI57CbIl5uGZ6yqfpQj3aK+N8f1EVHdwK9JFskoipvC8\n7yFTk8tgmO1i0YA5oRGfNxneqCdrXZiWL6Ko8v/iln9vuN+2rK3rgWZPPRJBAsBN\na49L7U6lJjIGxIZtZqmK5h47oiUtwlYVrbZMN2ijuBQ22/eQ9tsFDV28oBuZ3WAR\npSSbj/tubPQYkw3YYOhv/VpEpsd0rkoEt3QCmTVcX2rtblanpXowTV5R0Hy4014n\nT49jrEo40r4mwYoyS835Uv4ENUFA+pXicT9eUot3RSH6rYdx4A/14UtoI9U0ol8M\n62GHpxSASQ2Kc3yQWvxRGTFslTduYM+vVmMLEDDdqcsjYnStPpwdxxmKItmbjxSv\nIwYIndp8A04WkX2iiJCciC3BNxiLamPtYVyB1HHqbGTGirKYuSvwZt337q1OI3WH\nwVn2S4Mj/wqa4iCyGTvFSUnGq34Xkrb9XNwWBok9Tc2XWGAU/mb/xcd1hX74GZbF\nsrZ11aPtym4kMAjU2KQi96GcAH2lnGZYoOja1J4Cs4WYx1uAx74H/m84CrYavVfl\n1ONJVLDfuZaEkSmu+jHQX15pAECNORTuLD06PbWnOEcOi1xmbt/OT3SA3rhD2mb7\n2wxl7oJpV3ap8xGwYmxiFzmInxFJ1axjg8Rimol0mXTKAy6OdNHbCOnAwwIDAQAB\no2MwYTAPBgNVHRMBAf8EBTADAQH/MA4GA1UdDwEB/wQEAwIBBjAfBgNVHSMEGDAW\ngBQleng3lqGBeTrbLVuABoEmUHm1+TAdBgNVHQ4EFgQUJXp4N5ahgXk62y1bgAaB\nJlB5tfkwDQYJKoZIhvcNAQELBQADggIBADQ9jpmVh9nyY7ZQ4s+S9RuSRYn7QsrW\nDePeMzQgh8ZtS8WE65GY5HS61iHNP2Co8Q1lAaBWF4ipq+VZOcQbPLccHzd1kZv4\ns4u0aTzBd9ccidl73FS0DJDQOBbzPSzgsaiGHSMyGzkTeA8z3ntsSqrXXcDUvoRi\nFus/110AwdtNhJLrWveX6btYtHp9Lqe0YtNCy5AaXlrr1yRSckP5BWVtlwD4dzSO\n/dqI3wHS/ncUx9wSQomZ+AmxYW3KtJQKgHzTqHru1x9BBk7Bzfz9FZr6HLLmEitj\nuFoDRd5TNt5LbO0zDQokvY3oqso6Htup/rS7C08mcmnelYE+yXuOc1YrlyGnpBzk\nmy+1VYbOxRRdqKAZRbE72u/h847IVpsOvjR51iksuCAurZdp2+y2zvV8NhWekuNy\nirECRy9cb4YasjRaKi0/TCGPVSICuLyeG2W72liCj/N2VKfjPP9zsOR5XjwCXfRg\n+9xhLy77/gov2NWXx5fzTkhxCrHOxFdLVMn0wQhksDmw6QsXzDIHSpIOypdDfnx9\nCsthx3nhkuHLUaEP22D22dG+vImA9ukj4R/RRI/87jmi9Q8+ehH+NqN0GZZcLjdN\nSLVXpncuwWQFUDPR06wNkkkmBSXWiIYhwqSpU0Pl3er3fD0uWvXuWPm2PzfOmUAE\nUrkzyw9XmLw0\n-----END CERTIFICATE-----\n'}) ESC[0m

TASK [remote/ldap : Configure local-dex.tls] *********************************************************************************************
Monday 08 April 2024  22:51:32 +0000 (0:00:00.024)       1:26:17.946 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m
TASK [remote/ldap : Configure generic] ***************************************************************************************************
Monday 08 April 2024  22:51:32 +0000 (0:00:00.017)       1:26:17.964 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/ldap : Configure wadcert] ***************************************************************************************************
Monday 08 April 2024  22:51:32 +0000 (0:00:00.018)       1:26:17.982 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/ldap : Configure dex-overrides.yaml] ****************************************************************************************
Monday 08 April 2024  22:51:32 +0000 (0:00:00.018)       1:26:18.000 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/ldap : Wait for distributed cloud synchronization] **************************************************************************
Monday 08 April 2024  22:51:32 +0000 (0:00:00.020)       1:26:18.021 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/ldap : Remove temporary working directory] **********************************************************************************
Monday 08 April 2024  22:51:32 +0000 (0:00:00.020)       1:26:18.041 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/ldap : bringing in variables from the system controller] ********************************************************************
Monday 08 April 2024  22:51:32 +0000 (0:00:00.017)       1:26:18.059 **********
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/ldap : Copy SSL AD cert to server] ******************************************************************************************
Monday 08 April 2024  22:51:32 +0000 (0:00:00.039)       1:26:18.098 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012] => (item={'filename': 'ad_ca.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIFpTCCA42gAwIBAgIUa3vZ0YGxO1TQ8NwhiVfQC0JslXgwDQYJKoZIhvcNAQEL\nBQAwWjELMAkGA1UEBhMCVVMxEDAOBgNVBAoMB1Zlcml6b24xEzARBgNVBAsMClZa\nSUFNIFRlc3QxJDAiBgNVBAMMG1Zlcml6b24gTmV0d29yayBSU0EgQ0EgVGVzdDAe\nFw0yMDA2MTUyMTAxMTNaFw0zNTA2MTUyMTAxMTNaMFoxCzAJBgNVBAYTAlVTMRAw\nDgYDVQQKDAdWZXJpem9uMRMwEQYDVQQLDApWWklBTSBUZXN0MSQwIgYDVQQDDBtW\nZXJpem9uIE5ldHdvcmsgUlNBIENBIFRlc3QwggIiMA0GCSqGSIb3DQEBAQUAA4IC\nDwAwggIKAoICAQC8AIrksI57CbIl5uGZ6yqfpQj3aK+N8f1EVHdwK9JFskoipvC8\n7yFTk8tgmO1i0YA5oRGfNxneqCdrXZiWL6Ko8v/iln9vuN+2rK3rgWZPPRJBAsBN\na49L7U6lJjIGxIZtZqmK5h47oiUtwlYVrbZMN2ijuBQ22/eQ9tsFDV28oBuZ3WAR\npSSbj/tubPQYkw3YYOhv/VpEpsd0rkoEt3QCmTVcX2rtblanpXowTV5R0Hy4014n\nT49jrEo40r4mwYoyS835Uv4ENUFA+pXicT9eUot3RSH6rYdx4A/14UtoI9U0ol8M\n62GHpxSASQ2Kc3yQWvxRGTFslTduYM+vVmMLEDDdqcsjYnStPpwdxxmKItmbjxSv\nIwYIndp8A04WkX2iiJCciC3BNxiLamPtYVyB1HHqbGTGirKYuSvwZt337q1OI3WH\nwVn2S4Mj/wqa4iCyGTvFSUnGq34Xkrb9XNwWBok9Tc2XWGAU/mb/xcd1hX74GZbF\nsrZ11aPtym4kMAjU2KQi96GcAH2lnGZYoOja1J4Cs4WYx1uAx74H/m84CrYavVfl\n1ONJVLDfuZaEkSmu+jHQX15pAECNORTuLD06PbWnOEcOi1xmbt/OT3SA3rhD2mb7\n2wxl7oJpV3ap8xGwYmxiFzmInxFJ1axjg8Rimol0mXTKAy6OdNHbCOnAwwIDAQAB\no2MwYTAPBgNVHRMBAf8EBTADAQH/MA4GA1UdDwEB/wQEAwIBBjAfBgNVHSMEGDAW\ngBQleng3lqGBeTrbLVuABoEmUHm1+TAdBgNVHQ4EFgQUJXp4N5ahgXk62y1bgAaB\nJlB5tfkwDQYJKoZIhvcNAQELBQADggIBADQ9jpmVh9nyY7ZQ4s+S9RuSRYn7QsrW\nDePeMzQgh8ZtS8WE65GY5HS61iHNP2Co8Q1lAaBWF4ipq+VZOcQbPLccHzd1kZv4\ns4u0aTzBd9ccidl73FS0DJDQOBbzPSzgsaiGHSMyGzkTeA8z3ntsSqrXXcDUvoRi\nFus/110AwdtNhJLrWveX6btYtHp9Lqe0YtNCy5AaXlrr1yRSckP5BWVtlwD4dzSO\n/dqI3wHS/ncUx9wSQomZ+AmxYW3KtJQKgHzTqHru1x9BBk7Bzfz9FZr6HLLmEitj\nuFoDRd5TNt5LbO0zDQokvY3oqso6Htup/rS7C08mcmnelYE+yXuOc1YrlyGnpBzk\nmy+1VYbOxRRdqKAZRbE72u/h847IVpsOvjR51iksuCAurZdp2+y2zvV8NhWekuNy\nirECRy9cb4YasjRaKi0/TCGPVSICuLyeG2W72liCj/N2VKfjPP9zsOR5XjwCXfRg\n+9xhLy77/gov2NWXx5fzTkhxCrHOxFdLVMn0wQhksDmw6QsXzDIHSpIOypdDfnx9\nCsthx3nhkuHLUaEP22D22dG+vImA9ukj4R/RRI/87jmi9Q8+ehH+NqN0GZZcLjdN\nSLVXpncuwWQFUDPR06wNkkkmBSXWiIYhwqSpU0Pl3er3fD0uWvXuWPm2PzfOmUAE\nUrkzyw9XmLw0\n-----END CERTIFICATE-----\n'})ESC[0m

TASK [remote/ldap : create oidc-auth-apps-certificate] ***********************************************************************************
Monday 08 April 2024  22:51:35 +0000 (0:00:02.804)       1:26:20.903 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/ldap : make sure oidc certificate is Ready before proceeding] ***************************************************************
Monday 08 April 2024  22:51:36 +0000 (0:00:01.683)       1:26:22.586 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/ldap : wait until system configuration is updated] **************************************************************************
Monday 08 April 2024  22:51:38 +0000 (0:00:01.494)       1:26:24.081 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/ldap : create dex-ca-cert secret] *******************************************************************************************
Monday 08 April 2024  22:51:43 +0000 (0:00:04.805)       1:26:28.886 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/ldap : template overrides] **************************************************************************************************
Monday 08 April 2024  22:51:44 +0000 (0:00:01.578)       1:26:30.464 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012] => (item=stx-oidc-client.yaml)ESC[0m
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012] => (item=dex-overrides-2212.yaml)ESC[0m
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012] => (item=secret-observer-overrides.yaml)ESC[0m

TASK [remote/ldap : override oidc-client] ************************************************************************************************
Monday 08 April 2024  22:51:52 +0000 (0:00:08.158)       1:26:38.623 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/ldap : create wad ca cert secret] *******************************************************************************************
Monday 08 April 2024  22:51:58 +0000 (0:00:05.488)       1:26:44.112 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/ldap : override dex] ********************************************************************************************************
Monday 08 April 2024  22:52:00 +0000 (0:00:01.585)       1:26:45.697 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/ldap : override secret observer] ********************************************************************************************
Monday 08 April 2024  22:52:05 +0000 (0:00:05.291)       1:26:50.989 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/ldap : Detect oidc-auth-apps application in applying state (from a previous attempt)] ***************************************
Monday 08 April 2024  22:52:11 +0000 (0:00:05.780)       1:26:56.769 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/ldap : Fail if oidc-auth-apps application-abort failed] *********************************************************************
Monday 08 April 2024  22:52:16 +0000 (0:00:04.943)       1:27:01.713 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/ldap : Detect oidc-auth-apps application in apply-failed or aborted state] **************************************************
Monday 08 April 2024  22:52:16 +0000 (0:00:00.016)       1:27:01.730 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/ldap : Fail if oidc-auth-apps application apply failed] *********************************************************************
Monday 08 April 2024  22:52:21 +0000 (0:00:05.112)       1:27:06.842 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/ldap : Apply oidc-auth-apps application] ************************************************************************************
Monday 08 April 2024  22:52:21 +0000 (0:00:00.020)       1:27:06.862 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/ldap : Detect applied status of oidc-auth-apps application] *****************************************************************
Monday 08 April 2024  22:52:26 +0000 (0:00:05.007)       1:27:11.869 **********
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012]: Detect applied status of oidc-auth-apps application (60 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012]: Detect applied status of oidc-auth-apps application (59 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012]: Detect applied status of oidc-auth-apps application (58 retries left).ESC[0m
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/ldap : Fail if oidc-auth-apps application apply failed] *********************************************************************
Monday 08 April 2024  22:53:20 +0000 (0:00:53.858)       1:28:05.728 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [Remote Nvme] ***********************************************************************************************************************
Monday 08 April 2024  22:53:20 +0000 (0:00:00.023)       1:28:05.751 **********

TASK [remote/nvme : Install nvme-cli static files] ***************************************************************************************
Monday 08 April 2024  22:53:20 +0000 (0:00:00.118)       1:28:05.869 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/nvme : Run nvme-cli post-install script] ************************************************************************************
Monday 08 April 2024  22:53:20 +0000 (0:00:00.021)       1:28:05.890 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/nvme : Obtain current NVMe drive F/W versions] ******************************************************************************
Monday 08 April 2024  22:53:20 +0000 (0:00:00.022)       1:28:05.913 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/nvme : Check current NVMe drive F/W versions] *******************************************************************************
Monday 08 April 2024  22:53:21 +0000 (0:00:01.646)       1:28:07.559 **********
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/nvme : Stage NVMe F/W images and update script] *****************************************************************************
Monday 08 April 2024  22:53:21 +0000 (0:00:00.031)       1:28:07.591 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/nvme : Run NVMe F/W update script] ******************************************************************************************
Monday 08 April 2024  22:53:21 +0000 (0:00:00.019)       1:28:07.610 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/nvme : Verify NVMe F/W update script results] *******************************************************************************
Monday 08 April 2024  22:53:21 +0000 (0:00:00.018)       1:28:07.629 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/nvme : Obtain updated NVMe drive F/W versions] ******************************************************************************
Monday 08 April 2024  22:53:21 +0000 (0:00:00.030)       1:28:07.659 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/nvme : Verify updated NVMe drive F/W versions] ******************************************************************************
Monday 08 April 2024  22:53:23 +0000 (0:00:01.762)       1:28:09.422 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/nvme : Remove NVMe F/W images and update script] ****************************************************************************
Monday 08 April 2024  22:53:23 +0000 (0:00:00.032)       1:28:09.455 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [Remote Metrics Server] *************************************************************************************************************
Monday 08 April 2024  22:53:23 +0000 (0:00:00.022)       1:28:09.477 **********

TASK [remote/metrics-server : Set facts - release independent] ***************************************************************************
Monday 08 April 2024  22:53:23 +0000 (0:00:00.085)       1:28:09.563 **********
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/metrics-server : Set facts - 22.12] *****************************************************************************************
Monday 08 April 2024  22:53:23 +0000 (0:00:00.016)       1:28:09.579 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/metrics-server : Set facts - 22.12] *****************************************************************************************
Monday 08 April 2024  22:53:23 +0000 (0:00:00.015)       1:28:09.595 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/metrics-server : Set facts - 22.12] *****************************************************************************************
Monday 08 April 2024  22:53:23 +0000 (0:00:00.016)       1:28:09.611 **********
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/metrics-server : Detect presence of existing application] *******************************************************************
Monday 08 April 2024  22:53:23 +0000 (0:00:00.018)       1:28:09.630 **********
ESC[0;31mfatal: [welktxsr-931883-rh-le093s6-012]: FAILED! => changed=true ESC[0m
ESC[0;31m  cmd: |-ESC[0m
ESC[0;31m    . /etc/platform/openrcESC[0m
ESC[0;31m    system application-show metrics-server --column status --format valueESC[0m
ESC[0;31m  delta: '0:00:03.879844'ESC[0m
ESC[0;31m  end: '2024-04-08 22:53:29.149804'ESC[0m
ESC[0;31m  msg: non-zero return codeESC[0m
ESC[0;31m  rc: 1ESC[0m
ESC[0;31m  start: '2024-04-08 22:53:25.269960'ESC[0m
ESC[0;31m  stderr: 'application not found: metrics-server'ESC[0m
ESC[0;31m  stderr_lines: <omitted>ESC[0m
ESC[0;31m  stdout: ''ESC[0m
ESC[0;31m  stdout_lines: <omitted>ESC[0m
ESC[0;36m...ignoringESC[0m

TASK [remote/metrics-server : Print message if system already has the appication] ********************************************************
Monday 08 April 2024  22:53:29 +0000 (0:00:05.411)       1:28:15.041 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/metrics-server : Apply again since the previous apply failed or in uploaded state] ******************************************
Monday 08 April 2024  22:53:29 +0000 (0:00:00.017)       1:28:15.059 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/metrics-server : Wait until apply is in the applied or apply-failed state] **************************************************
Monday 08 April 2024  22:53:29 +0000 (0:00:00.016)       1:28:15.075 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/metrics-server : Print message if re-apply succeeds] ************************************************************************
Monday 08 April 2024  22:53:29 +0000 (0:00:00.016)       1:28:15.091 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/metrics-server : Print message if re-apply failed] **************************************************************************
Monday 08 April 2024  22:53:29 +0000 (0:00:00.018)       1:28:15.110 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/metrics-server : Noop if system requires no further action or needs manual investigation] ***********************************
Monday 08 April 2024  22:53:29 +0000 (0:00:00.018)       1:28:15.129 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/metrics-server : Upload application] ****************************************************************************************
Monday 08 April 2024  22:53:29 +0000 (0:00:00.019)       1:28:15.148 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/metrics-server : Wait until application is in the uploaded state] ***********************************************************
Monday 08 April 2024  22:53:34 +0000 (0:00:05.481)       1:28:20.630 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/metrics-server : Apply application] *****************************************************************************************
Monday 08 April 2024  22:53:41 +0000 (0:00:06.225)       1:28:26.855 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/metrics-server : Wait until application is in the applied or apply-failed state] ********************************************
Monday 08 April 2024  22:53:46 +0000 (0:00:05.531)       1:28:32.387 **********
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012]: Wait until application is in the applied or apply-failed state (90 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012]: Wait until application is in the applied or apply-failed state (89 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012]: Wait until application is in the applied or apply-failed state (88 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012]: Wait until application is in the applied or apply-failed state (87 retries left).ESC[0m
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/metrics-server : Apply again since the first apply failed] ******************************************************************
Monday 08 April 2024  22:54:56 +0000 (0:01:10.058)       1:29:42.446 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/metrics-server : Wait again until apply is in the applied or apply-failed state] ********************************************
Monday 08 April 2024  22:54:56 +0000 (0:00:00.023)       1:29:42.470 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/metrics-server : Print message if apply is successful] **********************************************************************
Monday 08 April 2024  22:54:56 +0000 (0:00:00.022)       1:29:42.492 **********
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012] => ESC[0m
ESC[0;32m  msg:ESC[0m
ESC[0;32m  - =======================================================ESC[0m
ESC[0;32m  - ' welktxsr-d931833-012: metrics-server install SUCCEEDED! 'ESC[0m
ESC[0;32m  - =======================================================ESC[0m

TASK [remote/metrics-server : Print message if apply is failure] *************************************************************************
Monday 08 April 2024  22:54:56 +0000 (0:00:00.026)       1:29:42.518 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [Remote wrap-get-central-version] ***************************************************************************************************
Monday 08 April 2024  22:54:56 +0000 (0:00:00.025)       1:29:42.543 **********

TASK [remote/wrap-get-central-version : Determine central WRA current version] ***********************************************************
Monday 08 April 2024  22:54:56 +0000 (0:00:00.087)       1:29:42.631 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)]ESC[0m

TASK [remote/wrap-get-central-version : Set facts for wra_target_version] ****************************************************************
Monday 08 April 2024  22:55:02 +0000 (0:00:05.765)       1:29:48.396 **********
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/wrap-get-central-version : debug] *******************************************************************************************
Monday 08 April 2024  22:55:02 +0000 (0:00:00.019)       1:29:48.415 **********
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012] => ESC[0m
ESC[0;32m  msg: wra_target_version:23.09-0ESC[0m

TASK [Remote wrap-23.09-0] ***************************************************************************************************************
Monday 08 April 2024  22:55:02 +0000 (0:00:00.022)       1:29:48.438 **********

TASK [remote/wrap-23.09-0 : Set facts for playbook] **************************************************************************************
Monday 08 April 2024  22:55:02 +0000 (0:00:00.131)       1:29:48.569 **********
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/wrap-23.09-0 : Noop if the system is NOT at the right caas_version] *********************************************************
Monday 08 April 2024  22:55:02 +0000 (0:00:00.016)       1:29:48.586 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/wrap-23.09-0 : Print message if system is NOT at the right caas_version] ****************************************************
Monday 08 April 2024  22:55:02 +0000 (0:00:00.015)       1:29:48.601 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/wrap-23.09-0 : Determine WRA current version and status] ********************************************************************
Monday 08 April 2024  22:55:02 +0000 (0:00:00.015)       1:29:48.616 **********
ESC[0;31mfatal: [welktxsr-931883-rh-le093s6-012]: FAILED! => changed=true ESC[0m
ESC[0;31m  cmd: |-ESC[0m
ESC[0;31m    . /etc/platform/openrcESC[0m
ESC[0;31m    system application-show wr-analytics --column app_version --column status --format valueESC[0m
ESC[0;31m  delta: '0:00:05.193554'ESC[0m
ESC[0;31m  end: '2024-04-08 22:55:09.573161'ESC[0m
ESC[0;31m  msg: non-zero return codeESC[0m
ESC[0;31m  rc: 1ESC[0m
ESC[0;31m  start: '2024-04-08 22:55:04.379607'ESC[0m
ESC[0;31m  stderr: 'application not found: wr-analytics'ESC[0m
ESC[0;31m  stderr_lines: <omitted>ESC[0m
ESC[0;31m  stdout: ''ESC[0m
ESC[0;31m  stdout_lines: <omitted>ESC[0m
ESC[0;36m...ignoringESC[0m

TASK [remote/wrap-23.09-0 : Set facts for current WRA version and status] ****************************************************************
Monday 08 April 2024  22:55:09 +0000 (0:00:06.909)       1:29:55.526 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/wrap-23.09-0 : debug] *******************************************************************************************************
Monday 08 April 2024  22:55:09 +0000 (0:00:00.017)       1:29:55.543 **********
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012] => ESC[0m
ESC[0;32m  msg: 'wra_status:, wra_version:'ESC[0m

TASK [remote/wrap-23.09-0 : Determine if version is up-to-date] **************************************************************************
Monday 08 April 2024  22:55:09 +0000 (0:00:00.017)       1:29:55.560 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m
:

TASK [remote/wrap-23.09-0 : Noop because version is up-to-date] **************************************************************************
Monday 08 April 2024  22:55:09 +0000 (0:00:00.015)       1:29:55.576 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [Delete the existing WRA app] *******************************************************************************************************
Monday 08 April 2024  22:55:09 +0000 (0:00:00.015)       1:29:55.591 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/wrap-23.09-0 : Delete app if just uploaded] *********************************************************************************
Monday 08 April 2024  22:55:09 +0000 (0:00:00.020)       1:29:55.612 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/wrap-23.09-0 : Set facts for central security file] *************************************************************************
Monday 08 April 2024  22:55:09 +0000 (0:00:00.022)       1:29:55.635 **********
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/wrap-23.09-0 : Set facts for working dir] ***********************************************************************************
Monday 08 April 2024  22:55:09 +0000 (0:00:00.024)       1:29:55.659 **********
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/wrap-23.09-0 : Create working directory on host] ****************************************************************************
Monday 08 April 2024  22:55:10 +0000 (0:00:00.024)       1:29:55.684 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/wrap-23.09-0 : Copy files to host] ******************************************************************************************
Monday 08 April 2024  22:55:11 +0000 (0:00:01.728)       1:29:57.412 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012] => (item=wr-analytics-23.09-0.tgz)ESC[0m

TASK [remote/wrap-23.09-0 : Copy templates to host] **************************************************************************************
Monday 08 April 2024  22:55:14 +0000 (0:00:03.159)       1:30:00.572 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012] => (item=elastic-services-security-config.yaml)ESC[0m
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012] => (item=logstash_sev_overrides-dropAll6.yaml)ESC[0m
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012] => (item=logstash_samsung_vdu_parser.yaml)ESC[0m
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012] => (item=helm-logstash_extra_envvars.yaml)ESC[0m
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012] => (item=metricbeat-overrides.yaml)ESC[0m

TASK [remote/wrap-23.09-0 : Copy elastic security override from CC to Subcloud] **********************************************************
Monday 08 April 2024  22:55:28 +0000 (0:00:14.046)       1:30:14.618 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)]ESC[0m

TASK [remote/wrap-23.09-0 : Upload wr-analytics application] *****************************************************************************
Monday 08 April 2024  22:55:31 +0000 (0:00:02.442)       1:30:17.061 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/wrap-23.09-0 : Wait until application is in the uploaded state] *************************************************************
Monday 08 April 2024  22:55:36 +0000 (0:00:05.486)       1:30:22.547 **********
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012]: Wait until application is in the uploaded state (30 retries left).ESC[0m
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/wrap-23.09-0 : Assign labels to nodes] **************************************************************************************
Monday 08 April 2024  22:55:58 +0000 (0:00:21.463)       1:30:44.011 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/wrap-23.09-0 : Create monitor namesapce] ************************************************************************************
Monday 08 April 2024  22:56:04 +0000 (0:00:06.070)       1:30:50.081 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/wrap-23.09-0 : Update Elastic overrides] ************************************************************************************
Monday 08 April 2024  22:56:07 +0000 (0:00:03.243)       1:30:53.325 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/wrap-23.09-0 : Update Logstash overrides] ***********************************************************************************
Monday 08 April 2024  22:56:14 +0000 (0:00:07.037)       1:31:00.362 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/wrap-23.09-0 : Update Metricbeat overide] ***********************************************************************************
Monday 08 April 2024  22:56:20 +0000 (0:00:05.743)       1:31:06.106 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/wrap-23.09-0 : Apply wr-analytics application] ******************************************************************************
Monday 08 April 2024  22:56:27 +0000 (0:00:07.112)       1:31:13.218 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/wrap-23.09-0 : Wait until application is in the applied or apply-failed state] **********************************************
Monday 08 April 2024  22:56:33 +0000 (0:00:06.049)       1:31:19.268 **********
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012]: Wait until application is in the applied or apply-failed state (90 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012]: Wait until application is in the applied or apply-failed state (89 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012]: Wait until application is in the applied or apply-failed state (88 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012]: Wait until application is in the applied or apply-failed state (87 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012]: Wait until application is in the applied or apply-failed state (86 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012]: Wait until application is in the applied or apply-failed state (85 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012]: Wait until application is in the applied or apply-failed state (84 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012]: Wait until application is in the applied or apply-failed state (83 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012]: Wait until application is in the applied or apply-failed state (82 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012]: Wait until application is in the applied or apply-failed state (81 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012]: Wait until application is in the applied or apply-failed state (80 retries left).ESC[0m
ESC[1;30mFAILED - RETRYING: [welktxsr-931883-rh-le093s6-012]: Wait until application is in the applied or apply-failed state (79 retries left).ESC[0m
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/wrap-23.09-0 : Print message if install succeeded] **************************************************************************
Monday 08 April 2024  23:03:54 +0000 (0:07:21.118)       1:38:40.387 **********
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012] => ESC[0m
ESC[0;32m  msg:ESC[0m
ESC[0;32m  - ===================================================================ESC[0m
ESC[0;32m  - ' welktxsr-d931833-012: WRA 23.09-0 install SUCCEEDED! 'ESC[0m
ESC[0;32m  - ===================================================================ESC[0m

TASK [remote/wrap-23.09-0 : Print message if install failed] *****************************************************************************
Monday 08 April 2024  23:03:54 +0000 (0:00:00.029)       1:38:40.416 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [Remote fpga-user-image] ************************************************************************************************************
Monday 08 April 2024  23:03:54 +0000 (0:00:00.026)       1:38:40.443 **********

TASK [include_role : remote/set-facts] ***************************************************************************************************
Monday 08 April 2024  23:03:54 +0000 (0:00:00.107)       1:38:40.550 **********

TASK [remote/set-facts : Set facts for vip, ansible, and wr_admin] ***********************************************************************
Monday 08 April 2024  23:03:54 +0000 (0:00:00.018)       1:38:40.569 **********
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/set-facts : Get central controller's software load version] *****************************************************************
Monday 08 April 2024  23:03:54 +0000 (0:00:00.042)       1:38:40.611 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)]ESC[0m

TASK [remote/set-facts : Set facts for wr_release_version] *******************************************************************************
Monday 08 April 2024  23:04:00 +0000 (0:00:05.781)       1:38:46.392 **********
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/set-facts : Print wr_release_version] ***************************************************************************************
Monday 08 April 2024  23:04:00 +0000 (0:00:00.019)       1:38:46.411 **********
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012] => ESC[0m
ESC[0;32m  msg: 'wr_release_version: 22.12'ESC[0m

TASK [remote/fpga-user-image : Set facts for default fpga_image_file] ********************************************************************
Monday 08 April 2024  23:04:00 +0000 (0:00:00.026)       1:38:46.438 **********
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/fpga-user-image : Set facts for fpga_image_file from host_vars] *************************************************************
Monday 08 April 2024  23:04:00 +0000 (0:00:00.024)       1:38:46.463 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/fpga-user-image : Print message if server is not LS3 cascadelake] ***********************************************************
Monday 08 April 2024  23:04:00 +0000 (0:00:00.022)       1:38:46.486 **********
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012] => ESC[0m
ESC[0;32m  msg:ESC[0m
ESC[0;32m  - ==================================================================================ESC[0m
ESC[0;32m  - ' Server type HPE-LS6-93s6 is not LS3 cascadelake, no action will take place! 'ESC[0m
ESC[0;32m  - ==================================================================================ESC[0m

TASK [remote/fpga-user-image : Register noop because server is not LS3 cascadelake] ******************************************************
Monday 08 April 2024  23:04:00 +0000 (0:00:00.019)       1:38:46.505 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/fpga-user-image : Check if FPGA update is stuck] ****************************************************************************
Monday 08 April 2024  23:04:02 +0000 (0:00:01.431)       1:38:47.937 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m
:

TASK [remote/fpga-user-image : Abort FPGA update] ****************************************************************************************
Monday 08 April 2024  23:04:02 +0000 (0:00:00.020)       1:38:47.957 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/fpga-user-image : include_tasks] ********************************************************************************************
Monday 08 April 2024  23:04:02 +0000 (0:00:00.021)       1:38:47.978 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/fpga-user-image : Check FPGA update status (HPE-LS3-e910)] ******************************************************************
Monday 08 April 2024  23:04:02 +0000 (0:00:00.019)       1:38:47.998 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/fpga-user-image : Check FPGA update status (ZTS-LS3-trtn)] ******************************************************************
Monday 08 April 2024  23:04:02 +0000 (0:00:00.018)       1:38:48.017 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/fpga-user-image : Noop if the system has been updated] **********************************************************************
Monday 08 April 2024  23:04:02 +0000 (0:00:00.019)       1:38:48.036 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/fpga-user-image : Print message if the system has been updated] *************************************************************
Monday 08 April 2024  23:04:02 +0000 (0:00:00.019)       1:38:48.055 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/fpga-user-image : In main block] ********************************************************************************************
Monday 08 April 2024  23:04:02 +0000 (0:00:00.020)       1:38:48.076 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/fpga-user-image : Copy files to host] ***************************************************************************************
Monday 08 April 2024  23:04:02 +0000 (0:00:00.019)       1:38:48.095 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012] => (item=20ww43.5-1x2x25G-5GLDPC-v1.6.2-3.0.1-unsigned.bin) ESC[0m

TASK [remote/fpga-user-image : Do system device-image-upload] ****************************************************************************
Monday 08 April 2024  23:04:02 +0000 (0:00:00.021)       1:38:48.117 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/fpga-user-image : debug - print UUID] ***************************************************************************************
Monday 08 April 2024  23:04:02 +0000 (0:00:00.018)       1:38:48.136 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/fpga-user-image : Do system device-image-apply] *****************************************************************************
Monday 08 April 2024  23:04:02 +0000 (0:00:00.019)       1:38:48.155 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/fpga-user-image : Do system host-device-image-update] ***********************************************************************
Monday 08 April 2024  23:04:02 +0000 (0:00:00.019)       1:38:48.175 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/fpga-user-image : Wait till application completed] **************************************************************************
Monday 08 April 2024  23:04:02 +0000 (0:00:00.019)       1:38:48.194 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/fpga-user-image : Do system device-image-state-list] ************************************************************************
Monday 08 April 2024  23:04:02 +0000 (0:00:00.018)       1:38:48.213 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/fpga-user-image : force an error if image state is not completed] ***********************************************************
Monday 08 April 2024  23:04:02 +0000 (0:00:00.019)       1:38:48.232 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/fpga-user-image : include_tasks] ********************************************************************************************
Monday 08 April 2024  23:04:02 +0000 (0:00:00.019)       1:38:48.252 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [Install DM Monitor] ****************************************************************************************************************
Monday 08 April 2024  23:04:02 +0000 (0:00:00.021)       1:38:48.273 **********

TASK [remote/dm-monitor : Install DM Monitor] ********************************************************************************************
Monday 08 April 2024  23:04:02 +0000 (0:00:00.147)       1:38:48.421 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/dm-monitor : Wait for DM Monitor pod created] *******************************************************************************
Monday 08 April 2024  23:04:40 +0000 (0:00:37.728)       1:39:26.149 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/dm-monitor : Wait for control-plane pods become ready] **********************************************************************
Monday 08 April 2024  23:04:42 +0000 (0:00:01.573)       1:39:27.723 **********
ESC[0;33mchanged: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [remote/dm-monitor : debug] *********************************************************************************************************
Monday 08 April 2024  23:04:43 +0000 (0:00:01.570)       1:39:29.294 **********
ESC[0;32mok: [welktxsr-931883-rh-le093s6-012] => ESC[0m
ESC[0;32m  dm_monitor_pod_ready.stdout_lines:ESC[0m
ESC[0;32m  - pod/dm-monitor-5898579658-r44j5 condition metESC[0m

TASK [2212mr1 workarounds] ***************************************************************************************************************
Monday 08 April 2024  23:04:43 +0000 (0:00:00.030)       1:39:29.324 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [include_tasks] *********************************************************************************************************************
Monday 08 April 2024  23:04:43 +0000 (0:00:00.021)       1:39:29.345 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

TASK [include_tasks] *********************************************************************************************************************
Monday 08 April 2024  23:04:43 +0000 (0:00:00.021)       1:39:29.366 **********
ESC[0;36mskipping: [welktxsr-931883-rh-le093s6-012]ESC[0m

PLAY RECAP *******************************************************************************************************************************
ESC[0;33mwelktxsr-931883-rh-le093s6-012ESC[0m : ESC[0;32mok=149 ESC[0m ESC[0;33mchanged=78  ESC[0m unreachable=0    failed=0    ESC[0;36mskipped=152 ESC[0m rescued=0    ESC[1;35mignored=5   ESC[0m

Monday 08 April 2024  23:04:43 +0000 (0:00:00.024)       1:39:29.391 **********
===============================================================================
remote/remote-install : 4th polling: Wait for subcloud to install OS (this may still take a while) ----------------------------- 2854.33s
remote/remote-install : 2nd polling: Wait for subcloud to install OS (this will take a while) ---------------------------------- 1093.38s
remote/manage : Wait for system to stabilize before running kubectl ------------------------------------------------------------- 480.02s
remote/wrap-23.09-0 : Wait until application is in the applied or apply-failed state -------------------------------------------- 441.12s
remote/manage : Wait for system to stabilize ------------------------------------------------------------------------------------ 300.02s
remote/reset_bmc : Wait for HPE BMC to reset ------------------------------------------------------------------------------------ 180.02s
remote/metrics-server : Wait until application is in the applied or apply-failed state ------------------------------------------- 70.06s
remote/manage : 1st Wait for contoller-0 availability status online -------------------------------------------------------------- 61.22s
remote/ldap : Detect applied status of oidc-auth-apps application ---------------------------------------------------------------- 53.86s
remote/starlingx : wait until system configuration is updated -------------------------------------------------------------------- 40.55s
remote/dm-monitor : Install DM Monitor ------------------------------------------------------------------------------------------- 37.73s
remote/remote-install : 1st polling: Wait for subcloud to start installing OS ---------------------------------------------------- 30.99s
remote/wrap-23.09-0 : Wait until application is in the uploaded state ------------------------------------------------------------ 21.46s
remote/wrap-23.09-0 : Copy templates to host ------------------------------------------------------------------------------------- 14.05s
remote/set-facts : Get central controller's software load version ---------------------------------------------------------------- 11.73s
remote/remote-configure : copy seed templates ------------------------------------------------------------------------------------- 9.27s
remote/ldap : template overrides -------------------------------------------------------------------------------------------------- 8.16s
remote/remote-install : Set subcloud system time by NTP server -------------------------------------------------------------------- 7.55s
remote/wrap-23.09-0 : Update Metricbeat overide ----------------------------------------------------------------------------------- 7.11s
remote/wrap-23.09-0 : Update Elastic overrides ------------------------------------------------------------------------------------ 7.04s
(ansible_6.7) szabota@welktxefnce-h-pe1util-vm05:~/playbooks/wr-installer-atlas-me$ ^MESC[K(ansible_6.7) szabota@welktxefnce-h-pe1util-vm05:~/playbooks/wr-installer-atlas-me$ ^MESC[K(ansible_6.7) szabota@welktxefnce-h-pe1util-vm05:~/playbooks/wr-installer-atlas-me$ exit

Script done on 2024-04-09 02:30:59+00:00 [COMMAND_EXIT_CODE="0"]
XXXXXX@caromacl255 Downloads %

```

## Validate deployment of subcloud on Controller

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ dcmanager subcloud list
+----+----------------------+------------+--------------+---------------+---------+------------------+----------------------------+
| id | name                 | management | availability | deploy status | sync    | backup status    | backup datetime            |
+----+----------------------+------------+--------------+---------------+---------+------------------+----------------------------+
| 20 | welktxef-d931855-003 | managed    | online       | complete      | in-sync | complete-central | 2024-04-05 15:44:26.305872 |
| 25 | welktxef-d931884-034 | managed    | online       | complete      | in-sync | complete-central | 2024-04-05 20:42:15.594723 |
| 34 | welktxsr-d931833-012 | managed    | online       | complete      | in-sync | None             | None                       |
| 35 | welktxef-d931882-006 | managed    | online       | complete      | in-sync | None             | None                       |
| 36 | welktxef-d931887-021 | managed    | online       | complete      | in-sync | None             | None                       |
+----+----------------------+------------+--------------+---------------+---------+------------------+----------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ 
[XXXXXX@controller-0 ~(keystone_admin)]$ dcmanager subcloud show welktxef-d931887-021
+-----------------------------+---------------------------------+
| Field                       | Value                           |
+-----------------------------+---------------------------------+
| id                          | 36                              |
| name                        | welktxef-d931887-021            |
| description                 | Wind River Cloud Platform 22.12 |
| location                    | welktxef-d931887-021            |
| software_version            | 22.12                           |
| management                  | managed                         |
| availability                | online                          |
| deploy_status               | complete                        |
| management_subnet           | 2607:f160:10:809f::/64          |
| management_start_ip         | 2607:f160:10:809f:ce:40a::      |
| management_end_ip           | 2607:f160:10:809f:ce:40a:0:f    |
| management_gateway_ip       | 2607:f160:10:809f:ce:28::       |
| systemcontroller_gateway_ip | 2607:f160:0:3042:cd:28::        |
| group_id                    | 1                               |
| created_at                  | 2024-04-10 13:29:01.334272      |
| updated_at                  | 2024-04-10 15:56:27.002956      |
| backup_status               | None                            |
| backup_datetime             | None                            |
| dc-cert_sync_status         | in-sync                         |
| firmware_sync_status        | in-sync                         |
| identity_sync_status        | in-sync                         |
| kubernetes_sync_status      | in-sync                         |
| kube-rootca_sync_status     | in-sync                         |
| load_sync_status            | in-sync                         |
| patching_sync_status        | in-sync                         |
| platform_sync_status        | in-sync                         |
+-----------------------------+---------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$
```


## Deploymnet of subcloud was a success