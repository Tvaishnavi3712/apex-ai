# ZT Proteus PDB-CPLD 0.0.1.2 Firmware Validation
# ZT Proteus .46 BMC / BIOS .30
# 1/16/24 James Patchett
# Platform-Deployment MEAKV-224 WRCP22.12mr1 deployment
# Target subclouds RU_12,13 Left side

## Left side Subcloud welktxef-d931887-021
## BMC 0.46 BIOS 0.30
BMC:  2607:f160:10:9249:ce:40a:0:e015
OAM:  2607:f160:10:9249:ce:40a:0:f409

## Subcloud welktxef-d931856-008 Info
```log
XXXXXX@controller-0:~$ source /etc/platform/openrc
[XXXXXX@controller-0 ~(keystone_admin)]$ system show
+------------------------+--------------------------------------+
| Property               | Value                                |
+------------------------+--------------------------------------+
| contact                | None                                 |
| created_at             | 2024-03-07T18:03:00.044462+00:00     |
| description            | None                                 |
| distributed_cloud_role | subcloud                             |
| https_enabled          | True                                 |
| latitude               | None                                 |
| location               | None                                 |
| longitude              | None                                 |
| name                   | welktxef-d931887-021                 |
| region_name            | welktxef-d931887-021                 |
| sdn_enabled            | False                                |
| security_feature       | spectre_meltdown_v1                  |
| service_project_name   | services                             |
| shared_services        | []                                   |
| software_version       | 22.12                                |
| system_mode            | simplex                              |
| system_type            | All-in-one                           |
| timezone               | UTC                                  |
| updated_at             | 2024-03-11T19:05:24.739152+00:00     |
| uuid                   | 23aff978-9c1f-4e92-aca9-97621b54bd8a |
| vswitch_type           | none                                 |
+------------------------+--------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ system application-list
+--------------------------+----------+-------------------------------------------+------------------+---------+-----------+
| application              | version  | manifest name                             | manifest file    | status  | progress  |
+--------------------------+----------+-------------------------------------------+------------------+---------+-----------+
| cert-manager             | 22.12-8  | cert-manager-fluxcd-manifests             | fluxcd-manifests | applied | completed |
| metrics-server           | 22.12-1  | metrics-server-fluxcd-manifests           | fluxcd-manifests | applied | completed |
| nginx-ingress-controller | 22.12-1  | nginx-ingress-controller-fluxcd-manifests | fluxcd-manifests | applied | completed |
| oidc-auth-apps           | 22.12-6  | oidc-auth-apps-fluxcd-manifests           | fluxcd-manifests | applied | completed |
| platform-integ-apps      | 22.12-66 | platform-integ-apps-fluxcd-manifests      | fluxcd-manifests | applied | completed |
| wr-analytics             | 23.09-0  | wr-analytics-fluxcd-manifests             | fluxcd-manifests | applied | completed |
+--------------------------+----------+-------------------------------------------+------------------+---------+-----------+
[XXXXXX@controller-0 ~(keystone_admin)]$ sw-patch query
      Patch ID         RR  Release  Patch State
=====================  ==  =======  ===========
WRCP_22.12_PATCH_0001  Y    22.12    Committed
WRCP_22.12_PATCH_0002  Y    22.12    Committed
WRCP_22.12_PATCH_0003  Y    22.12    Committed
WRCP_22.12_PATCH_0004  Y    22.12    Committed

[XXXXXX@controller-0 ~(keystone_admin)]$
```



### MEAKV-224
### Ansible install script

```log
(ansible_6.7) szabota@welktxefnce-h-pe1util-vm05:~/playbooks/wr-installer-atlas-me$ more welktxef-931887-rh-le292s6-021-install.txt
Script started on 2024-03-13 23:49:42+00:00 [TERM="xterm-256color" TTY="/dev/pts/10" COLUMNS="145" LINES="23"]
szabota@welktxefnce-h-pe1util-vm05:~/playbooks/wr-installer-atlas-me$




PLAY [Wind River Remote Subcloud Installer] *****************************************************************************************************


TASK [Reset BMC] ********************************************************************************************************************************

Wednesday 13 March 2024  23:50:21 +0000 (0:00:00.036)       0:00:00.036 *******

TASK [remote/reset_bmc : Reset ZTS BMC using IPMItool] ******************************************************************************************

Wednesday 13 March 2024  23:50:21 +0000 (0:00:00.027)       0:00:00.064 *******
changed: [welktxef-931887-rh-le292s6-021 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)]

TASK [remote/reset_bmc : Wait for ZTS BMC to reset] *********************************************************************************************

Wednesday 13 March 2024  23:50:23 +0000 (0:00:02.351)       0:00:02.415 *******
Pausing for 300 seconds

ok: [welktxef-931887-rh-le292s6-021]

TASK [remote/reset_bmc : Reset HPE ILO using Redfish] *******************************************************************************************

Wednesday 13 March 2024  23:55:23 +0000 (0:05:00.025)       0:05:02.440 *******
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/reset_bmc : Wait for HPE BMC to reset] *********************************************************************************************

Wednesday 13 March 2024  23:55:23 +0000 (0:00:00.015)       0:05:02.456 *******
skipping: [welktxef-931887-rh-le292s6-021]

TASK [Download Files] ***************************************************************************************************************************

Wednesday 13 March 2024  23:55:23 +0000 (0:00:00.016)       0:05:02.473 *******

TASK [common/download_files : Check if artifact files exist locally] ****************************************************************************

Wednesday 13 March 2024  23:55:23 +0000 (0:00:00.025)       0:05:02.498 *******
ok: [welktxef-931887-rh-le292s6-021 -> localhost]

TASK [common/download_files : Download & unarchive artifact files to local directory if they don't exist] ***************************************

Wednesday 13 March 2024  23:55:23 +0000 (0:00:00.274)       0:05:02.772 *******
skipping: [welktxef-931887-rh-le292s6-021]

TASK [Set Facts] ********************************************************************************************************************************

Wednesday 13 March 2024  23:55:24 +0000 (0:00:00.018)       0:05:02.790 *******

TASK [remote/set-facts : Set facts for vip, ansible, and wr_admin] ******************************************************************************

Wednesday 13 March 2024  23:55:24 +0000 (0:00:00.025)       0:05:02.816 *******
ok: [welktxef-931887-rh-le292s6-021]

TASK [remote/set-facts : Get central controller's software load version] ************************************************************************

Wednesday 13 March 2024  23:55:24 +0000 (0:00:00.037)       0:05:02.853 *******
changed: [welktxef-931887-rh-le292s6-021 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)]

TASK [remote/set-facts : Set facts for wr_release_version] **************************************************************************************

Wednesday 13 March 2024  23:55:29 +0000 (0:00:05.917)       0:05:08.771 *******
ok: [welktxef-931887-rh-le292s6-021]

TASK [remote/set-facts : Print wr_release_version] **********************************************************************************************

Wednesday 13 March 2024  23:55:30 +0000 (0:00:00.019)       0:05:08.791 *******
ok: [welktxef-931887-rh-le292s6-021] =>
  msg: 'wr_release_version: 22.12'

TASK [Remote Configure] *************************************************************************************************************************

Wednesday 13 March 2024  23:55:30 +0000 (0:00:00.025)       0:05:08.816 *******

TASK [remote/remote-configure : Set facts] ******************************************************************************************************

Wednesday 13 March 2024  23:55:30 +0000 (0:00:00.059)       0:05:08.875 *******
ok: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-configure : Set facts - new] ************************************************************************************************

Wednesday 13 March 2024  23:55:30 +0000 (0:00:00.014)       0:05:08.889 *******
ok: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-configure : Set facts for which image list to use based on WR version] ******************************************************

Wednesday 13 March 2024  23:55:30 +0000 (0:00:00.020)       0:05:08.910 *******
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-configure : Set facts for which image list to use based on WR version] ******************************************************

Wednesday 13 March 2024  23:55:30 +0000 (0:00:00.014)       0:05:08.925 *******
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-configure : Set facts for which image list to use based on WR version] ******************************************************

Wednesday 13 March 2024  23:55:30 +0000 (0:00:00.013)       0:05:08.938 *******
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-configure : Print wr_image_list] ********************************************************************************************

Wednesday 13 March 2024  23:55:30 +0000 (0:00:00.014)       0:05:08.952 *******
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-configure : print wr_license_key] *******************************************************************************************

Wednesday 13 March 2024  23:55:30 +0000 (0:00:00.016)       0:05:08.969 *******
ok: [welktxef-931887-rh-le292s6-021] =>
  msg: wr_license_key = IyBXaW5kIFJpdmVyIFByb2R1Y3QgQWN0aXZhdGlvbiBGaWxlIChpbnN0YWxsLnR4dCkKIyBJc3N1ZWQgZm9yIGhvc3Q6IDxWZXJpem9uPiA8VmVyaXp
vbj4gPEFueT4KIyBMaWNlbnNlIG51bWJlcihzKTogNjgyMzc0CiMgSXNzdWVkIG9uOiAxMy1hcHItMjAyMyAwOTo1MDo1MAojCiMgTm90ZTogdGhpcyBsaWNlbnNlIGlzIGdlbmVyYXRlZCBj
dW11bGF0aXZlbHkgZm9yIGFsbAojIFdpbmQgUml2ZXIgc29mdHdhcmUgbWFuYWdlZCBieSB0aGlzIGhvc3QuCgojIDEuIEZsZXhMTSBsaWNlbnNlIGZpbGU6CiMgQmVnaW46IFNlcnZlciBsa
WNlbnNlICAtLS0tLS0tLS0tLS0tLS0tLS0tLS0KIyBTZXJpYWwgTnVtYmVyOiA2ODQ0NDktVmVyaXpvblBPQy1HNFdEQzlDUEVLCgpQQUNLQUdFIFdSQ1BfQ09OVEFJTkVSX1BLRyB3cnNkID
IyIDg1MERCRTAwQkFCRSBcCglDT01QT05FTlRTPVdSQ1BfQ09OVEFJTkVSOjIyLjEyIE9QVElPTlM9U1VJVEUgXAoJU0lHTj0xNkI4MjY4NjkwRDgKSU5DUkVNRU5UIFdSQ1BfQ09OVEFJTkV
SX1BLRyB3cnNkIDIyIHBlcm1hbmVudCB1bmNvdW50ZWQgNEMxRUE2NjQyNUUyIFwKCVZFTkRPUl9TVFJJTkc9PGxuPjY4MjM3NDwvbG4+PHBzPjIyMTMtNDM8L3BzPiBIT1NUSUQ9QU5ZIFwK
CUlTU1VFRD0xMy1hcHItMjAyMyBTTj1zZXJpYWwtVmVyaXpvbi1MVjJJV0FVTEVCIFwKCVNUQVJUPTEzLWFwci0yMDIzIFNJR049NDI2RjUyOUUxRjYwCg==

TASK [remote/remote-configure : Copy storage checking script if server is HPE-LS3-e910] *********************************************************

Wednesday 13 March 2024  23:55:30 +0000 (0:00:00.017)       0:05:08.986 *******
skipping: [welktxef-931887-rh-le292s6-021] => (item=hpe_storage_check.py)

TASK [remote/remote-configure : Execute storage checking script if server is HPE-LS3-e910] ******************************************************

Wednesday 13 March 2024  23:55:30 +0000 (0:00:00.018)       0:05:09.005 *******
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor HPE HPE-LS3-e910 (4 disks)] ******************************

Wednesday 13 March 2024  23:55:30 +0000 (0:00:00.014)       0:05:09.020 *******
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor HPE HPE-LS3-e910 (2 disks)] ******************************

Wednesday 13 March 2024  23:55:30 +0000 (0:00:00.014)       0:05:09.034 *******
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor HPE HPE-LS3-92s3] ****************************************

Wednesday 13 March 2024  23:55:30 +0000 (0:00:00.015)       0:05:09.050 *******
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor HPE HPE-LS6-92s6] ****************************************

Wednesday 13 March 2024  23:55:30 +0000 (0:00:00.014)       0:05:09.065 *******
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor ZTS ZTS-LS3-trtn] ****************************************

Wednesday 13 March 2024  23:55:30 +0000 (0:00:00.013)       0:05:09.079 *******
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-configure : Set facts for Corning] ******************************************************************************************

Wednesday 13 March 2024  23:55:30 +0000 (0:00:00.017)       0:05:09.096 *******
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor ZTS ZTS-LS6-pts6 & ZTS-LS3-pts3 ZTS-LS6-aks6 & ZTS-LS3-aks
3 & ZTS-XXX-ptmm] ***
Wednesday 13 March 2024  23:55:30 +0000 (0:00:00.016)       0:05:09.112 *******
ok: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-configure : Find out which DM Docker version contral has] *******************************************************************

Wednesday 13 March 2024  23:55:30 +0000 (0:00:00.020)       0:05:09.133 *******
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-configure : Find out which DM file version contral has] *********************************************************************

Wednesday 13 March 2024  23:55:30 +0000 (0:00:00.020)       0:05:09.153 *******
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-configure : Print dm docker version and dm file version] ********************************************************************

Wednesday 13 March 2024  23:55:30 +0000 (0:00:00.018)       0:05:09.172 *******
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-configure : Discover Wind River docker image names] *************************************************************************

Wednesday 13 March 2024  23:55:30 +0000 (0:00:00.019)       0:05:09.192 *******
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-configure : Print local_images_full] ****************************************************************************************

Wednesday 13 March 2024  23:55:30 +0000 (0:00:00.018)       0:05:09.210 *******
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-configure : Create fact for Wind River docker image names] ******************************************************************

Wednesday 13 March 2024  23:55:30 +0000 (0:00:00.018)       0:05:09.228 *******
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-configure : Determine DM Helm Chart path] ***********************************************************************************

Wednesday 13 March 2024  23:55:30 +0000 (0:00:00.019)       0:05:09.247 *******
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-configure : Print dm_helm_chart] ********************************************************************************************

Wednesday 13 March 2024  23:55:30 +0000 (0:00:00.018)       0:05:09.266 *******
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-configure : Set DM Helm Chart file] *****************************************************************************************

Wednesday 13 March 2024  23:55:30 +0000 (0:00:00.017)       0:05:09.283 *******
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-configure : Lookup Deployment Manager image tag] ****************************************************************************

Wednesday 13 March 2024  23:55:30 +0000 (0:00:00.018)       0:05:09.302 *******
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-configure : Lookup RBAC Proxy image tag] ************************************************************************************

Wednesday 13 March 2024  23:55:30 +0000 (0:00:00.018)       0:05:09.320 *******
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-configure : Copy WRCP DM Playbook] ******************************************************************************************

Wednesday 13 March 2024  23:55:30 +0000 (0:00:00.019)       0:05:09.340 *******
skipping: [welktxef-931887-rh-le292s6-021] => (item=None)

TASK [remote/remote-configure : Set a fact for the central controller VIP address] **************************************************************

Wednesday 13 March 2024  23:55:30 +0000 (0:00:00.019)       0:05:09.360 *******
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-configure : Configure WRCP seed template] ***********************************************************************************

Wednesday 13 March 2024  23:55:30 +0000 (0:00:00.022)       0:05:09.382 *******
skipping: [welktxef-931887-rh-le292s6-021] => (item={'src': 'bootstrap-values.yaml', 'dest': 'welktxef-d931887-021-bootstrap-values.yaml'})

skipping: [welktxef-931887-rh-le292s6-021] => (item={'src': 'deploy-values.yaml', 'dest': 'welktxef-d931887-021-deploy-values.yaml'})
skipping: [welktxef-931887-rh-le292s6-021] => (item={'src': 'deploy-standard.yaml', 'dest': 'welktxef-d931887-021-deploy-standard.yaml'})

skipping: [welktxef-931887-rh-le292s6-021] => (item={'src': 'install-values.yaml', 'dest': 'welktxef-d931887-021-install-values.yaml'})


TASK [remote/remote-configure : Set a fact for the central controller VIP address] **************************************************************

Wednesday 13 March 2024  23:55:30 +0000 (0:00:00.028)       0:05:09.410 *******
ok: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-configure : Retrieve sysinv password from CC] *******************************************************************************

Wednesday 13 March 2024  23:55:30 +0000 (0:00:00.025)       0:05:09.436 *******
changed: [welktxef-931887-rh-le292s6-021 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)]

TASK [remote/remote-configure : Store sysinv password] ******************************************************************************************

Wednesday 13 March 2024  23:55:34 +0000 (0:00:03.624)       0:05:13.061 *******
ok: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-configure : copy seed templates] ********************************************************************************************

Wednesday 13 March 2024  23:55:34 +0000 (0:00:00.026)       0:05:13.088 *******
ok: [welktxef-931887-rh-le292s6-021 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)] => (item={'src': 'bootstrap-values.yaml', 'dest'
: 'welktxef-d931887-021-bootstrap-values.yaml'})
ok: [welktxef-931887-rh-le292s6-021 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)] => (item={'src': 'deploy-standard.yaml', 'dest':
 'welktxef-d931887-021-deploy-standard.yaml'})
ok: [welktxef-931887-rh-le292s6-021 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)] => (item={'src': 'install-values.yaml', 'dest':
'welktxef-d931887-021-install-values.yaml'})

TASK [remote/remote-configure : Copy SSL cert files] ********************************************************************************************

Wednesday 13 March 2024  23:55:42 +0000 (0:00:08.283)       0:05:21.371 *******
ok: [welktxef-931887-rh-le292s6-021 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)] => (item={'filename': 'k8s_root_ca_cert.pem', 'v
alue': '-----BEGIN CERTIFICATE-----\nMIIF8jCCA9qgAwIBAgIJAIf9Ql2uDZh+MA0GCSqGSIb3DQEBDQUAMIGFMQswCQYD\nVQQGEwJVUzEOMAwGA1UECAwFVGV4YXMxETAPBgNVBA
cMCFdlc3RsYWtlMR0wGwYD\nVQQKDBRWZXJpem9uIFNvdXJjaW5nIExMQzE0MDIGA1UEAwwrVmVyaXpvbiBOZXR3\nb3JrIFdFTEtUWElCIExBQiAxIDMgUlNBIEs4UyBDQTAeFw0yMDEwMjU
yMjEyNDha\nFw0zMDEwMjMyMjEyNDhaMIGFMQswCQYDVQQGEwJVUzEOMAwGA1UECAwFVGV4YXMx\nETAPBgNVBAcMCFdlc3RsYWtlMR0wGwYDVQQKDBRWZXJpem9uIFNvdXJjaW5nIExM\nQz
E0MDIGA1UEAwwrVmVyaXpvbiBOZXR3b3JrIFdFTEtUWElCIExBQiAxIDMgUlNB\nIEs4UyBDQTCCAiIwDQYJKoZIhvcNAQEBBQADggIPADCCAgoCggIBAKyF9svdv/qG\n7HxBr1DWvZ3CQiD
sA4m1kj0hD7jo3B3W/32ODcPpgeNmp4Oful0SsndpqEGhXDq5\noiBfqszMUpzDgdQ7siIHekb2olFEK2KniMP3H53nilIppeyMby5K3ZwF0Qbmk5WK\ncoXoYegP+Uv9bV0AMH6Dn4CVgYrL
AYfmPyGgUSt4vuZ9F/rf9UkBf/DcZGqMnMax\n/Gfaq8KwmDzD9D8IVCHPrM5f4+CaKMQCFu5QkSsLYJFRiuQWWaICMMdnqpb0HZh5\niPnCSHwPPUyXxtujdI97Ovy4X5WR46jJ2+KzPYe8t
Va/DL3TlKmRL9AF+oSE17bw\nzGAE7GNWxPojebHIUuoKdOQC1qiJBVS+c14r9+9P2Uy6XEhNUs+h3juRI4U3YkQ1\nUCUU3opqhOPh4jUIuPGg5aX07lt4Wpxc48D+CY1D4i6vaJLl3WCsVK
7PFwWVQQEW\nIQabfuj1R2jEu7pp2Yabza58S00v1P5/kv/DNr7ADm8eYRvxLAAXCedMeSDXKBgd\npPmVXXZoZ8+X8VRGYxcw0mBBLIAiTOntT2vgLeq5T3QyiVKdU6TLAYEjS65QZ3Eg\na
IX0wRqlcQI7lruTXubtENG6wWXYtnDf5795ZID1YIEqkgzZLMBqq1SBiLnWd6aK\n78Zsr4j5GmTBGpKRmwE2oO1btJCCYyG5AgMBAAGjYzBhMA8GA1UdEwEB/wQFMAMB\nAf8wHQYDVR0OBB
YEFEDQ5EaGp3x02WUuvqetygqpM3dCMB8GA1UdIwQYMBaAFEDQ\n5EaGp3x02WUuvqetygqpM3dCMA4GA1UdDwEB/wQEAwICpDANBgkqhkiG9w0BAQ0F\nAAOCAgEAeCMxVJr5Jyg87DVaUtE
hiWfhto993ENrnevAGqrBOoRc/KU1/C3paqhR\nsvr2r2LR+npSmeo6iz0FaO31XwHSHX95+XJeGP5Q8TGddbRiTglQsMfOkGNzxqgg\nTkdZ8A1y9v2jprONUmLADVGIVT0AoHc7V9w1I8NK
hrY+rIllum4FRDiDPSnImh5h\nxmH+Nq2ZuEFVdtV/oNKzEu2ywmbgBRd5Jv3rTejxltmTZtyq8IKoKguj3NVFn93Q\nU4TbsxkcAdrLMooLYYDRTWA4t0iqKM/UkYUg4xl2l9NrY7ZUbaNd5
+YsLNdqXO/c\nmp7wyMv/8ZIy1BLG4zJmX/JzWkYmULqQ+A+21+YuqrV3a81V7vcHhJcRaPOrg5cd\nYwY2eCbXMvNOdrzppIglUrlddNuqAhs1MTi/VibxYuI9isU0JckXIcCy1L+xbEda\n
6v/z6wSrScVz0I4m0DpK6xMQ8t9sLcrGp5uGbj6J4nQWd+QLdq6kmAzDOZ/Gs0wb\nPYdkER4dXAVcioYFekpKv7d+nur0FPtMNIw0OdhX2eAwC22IFAq2DZRjUFvaBGaD\ni1ptfq6P1mVJ2
T/exYujEDtq+8yQTfWgFm/DjEfWtcCp0Jukgv8opLR2DpCf5Ucq\nd5X7d/DP0mukJ3vZ8EIqYorwZJ1L1a2jgngjA+gPxIaW+JHfTHU=\n-----END CERTIFICATE-----\n'})
ok: [welktxef-931887-rh-le292s6-021 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)] => (item={'filename': 'k8s_root_ca_key.pem', 'va
lue': '-----BEGIN PRIVATE KEY-----\nMIIJQQIBADANBgkqhkiG9w0BAQEFAASCCSswggknAgEAAoICAQCshfbL3b/6hux8\nQa9Q1r2dwkIg7AOJtZI9IQ+46Nwd1v99jg3D6YHjZqe
Dn7pdErJ3aahBoVw6uaIg\nX6rMzFKcw4HUO7IiB3pG9qJRRCtip4jD9x+d54pSKaXsjG8uSt2cBdEG5pOVinKF\n6GHoD/lL/W1dADB+g5+AlYGKywGH5j8hoFEreL7mfRf63/VJAX/w3GRq
jJzGsfxn\n2qvCsJg8w/Q/CFQhz6zOX+PgmijEAhbuUJErC2CRUYrkFlmiAjDHZ6qW9B2YeYj5\nwkh8Dz1Ml8bbo3SPezr8uF+VkeOoydvisz2HvLVWvwy905SpkS/QBfqEhNe28Mxg\nBOx
jVsT6I3mxyFLqCnTkAtaoiQVUvnNeK/fvT9lMulxITVLPod47kSOFN2JENVAl\nFN6KaoTj4eI1CLjxoOWl9O5beFqcXOPA/gmNQ+Iur2iS5d1grFSuzxcFlUEBFiEG\nm37o9UdoxLu6admG
m82ufEtNL9T+f5L/wza+wA5vHmEb8SwAFwnnTHkg1ygYHaT5\nlV12aGfPl/FURmMXMNJgQSyAIkzp7U9r4C3quU90MolSnVOkywGBI0uuUGdxIGiF\n9MEapXECO5a7k17m7RDRusFl2LZw3
+e/eWSA9WCBKpIM2SzAaqtUgYi51nemiu/G\nbK+I+RpkwRqSkZsBNqDtW7SQgmMhuQIDAQABAoICACysO62qa+2pRk8eixD5qfvR\ns2Hm+zuLYqSljPaqhWTMqTePswzJyDJkAHhawd0b3E
6Dc2gbKlCihNKxMv744WNq\nVJHqK0QYf5ckgf9dEYboLsffk7ZFoFGKK0bHTnrENAIUl32b8xdD1EfMVp3KlRkS\nNGFijSwVVRXsoLCZxHm2Kx6/7oS9LWFtfuodV9xhoQlzaCUW5/mjWOJ
jgxpUs/b4\nHqS7uV1P80U1G0KraGboy5tGDXEB7y1x2e8Zwnfq7UqVE10nNQqoXcmefzpwj8Tn\ngDybZLFKjYmnDEkkj7jDHEbldsdRG/usWNZGlTYbPDA3fBkYdOsQCzvJypQmgbZ+\n3y
k3Lj2+9vLEMfPrruuzyOSXgki6o5uvy7Je6PdBpsz75k8FH6a+Rw3vvP8HuP3S\nLSUYm3tyOheXHR7BKN4bnfi11RAWvDpT9S+QnZ+R8DmQzOADlnjRC8WewDJYoNJ1\np1jeuqswlxo144o
MO92cmdS2dAbPvS6aQP1I85Q2NniY+6YhHkBwIQIlfVs1JPbY\nX7QtTy1IXQhR3sospyvUwY2GPSAeVHDRL53ClQKDsvWpSy0MAmWYJkZu1P+jKBim\nj34ytApgG65Hv/RHf3L4+4zzItZ3
TN2tJ/g9EKc6oMNtqKbbG56kkmvRPWKtMGV8\nFqxCvG5NydUK7fN+P2WJAoIBAQDXLFC//Fn9ed1U+pKa2M25aJwEetkGLXQvkwVi\n8uJFaXITb2ceveSEo6iBExyn4eYL5A4X+RZdJJdRR
bj4whsNN13Pm+6lYX3pp7MN\nO+78uvwVfKZiWPFKfZs7ZH1/O9VIlLGnXUHeaHK1tmv9ixxMixdnjUDkcVa0O3qT\nKBLpvXnVEMYizxQBN0P5Z9QvQQGpUhKnNw+FhV1SP+YHxrB0Pu6qbY
AmZZC2MQc1\nTsDyqGjmHk9VJaFYAAPEjqACDbfnkVUCj0ylM4xPQuBJs9DOKh4InG+znusdmd8H\nmvoEFDppsrH1NhO6GTeuCk6n0WBi6cUm76K/gPscYyV4ZtkfAoIBAQDNQgDXtfqv\nx
bAhvDk0o/P8fqOdgQF0uFTqYHmyW31Ty9nF0ptA8LVJOIljU3zlLplhIFjBnSEG\nLqu4jnLLRR+zej0MXmJuZ9BMWmQeTrZzttnH5bn54E07DPJ5BvFoTMJNklBiXjB5\n5hTPZS4yK1Kjox
Y+Ypnj4W1iZjP37ya/A34J2nlYtoW4LdVfJHqCxBXel9Nz2zkv\nvwwPu8Eu7gFLuhNQM6Iv4mORGI8yg7Y/BwodfDPRuFvrG1KXkjwASb0O5b1suRQy\n9H80q5EAbT36K1z48ilr8fcroN+
hV8g4yntrBBgOHPMmBk/vHKU8B1rkBr0p2haI\n3PwKmDFRsDInAoIBAGrjjMmSZnHQk+6e+y0I/klYegiPrjevZMQtWMOqvFSW6SBW\nevd+hYKOeiqEf/u18D1/8LBgAIgMoU6yQAzy/9U0
59k2MPrez1m/AOdWGoZZrNhP\nr6ezX0oN04tRhDYsVutTUl09qnb9k95I3KR68nfjsKC0PsQ8uUGXOnDXu215vofl\naUfpbpqcBZxjw7glptmh97oxU/iUI6O0MmUygn18tbrb4okwcw7Ol
DIbCSaCGnoW\nHHrD0r6QY07FOx9KCU1zmLNI1F5MmSrWoex68wM3UOweKi8khs+RnIV+qyxTkCDp\nsBWL44jS9iHy5Nfg3uzEDDgnWsWfIR8c8YQ6MykCggEADr0ollTI9Yo6hZGggfkr\n
8fueABddZWY/Ir1ev8H2E+hVcPEYmOcv/VwD8Y/zLfnUpbbO6MhBsNH1HsGL2LDT\n/+1NKPA2HTtzJ6ht/Acm7tQ4ezQx0JGcuhrJ5orrFtQ8N5nED+w3iulMoT/gu1WF\nD58MX9pwtn5ff
mtcW/deTuUPTeHUSNyCaaFQ6w4RhgZSk7NPSch6KMWNNiwDST1p\n9mgcLuwmP04AXFDpJ3VxxsDYpxleFzcn0pAZtCyaBmNFIia5HW+E1cvcvol7Vg6C\nHs6yVGX/N3MejpF0vX8yL3HKvv
qCR7EofJiDcOYbr13P1wPs3W59o8JKjvAyymze\njQKCAQAUY/0asRL33D7tFoIbLg/N9hi+tCCM35DMf2FeXm3QwSkAR/BJw0ewCE5C\n+VqukHN3/i0Xe8KSHwEuLK2sGLk9Ys8A5NytjqF
ApYwpIk8UrRONfC12H3ez5VYk\nJlhMVhVXEZvVhEFJiBC7q6x6s7BVtLTGV7FA5CW8YKBhwHwrpm+h/Xb798oaKyel\nP/xYq+GZzfWfbvUjZvgN0J0RGxKA+GRgsmhoyOfgCVXgSzuUkI+9
cAUvC0OV407L\n4XIK0GDJ7Tv/2USSPfmueyGEmacc/oYUPVBUgeINSoaCM4cpZwyLylVEtKOdQoEE\n77G5mvQsoXxsMjd+nbHil450UHsL\n-----END PRIVATE KEY-----\n'})

TASK [Remote Install] ***************************************************************************************************************************

Wednesday 13 March 2024  23:55:48 +0000 (0:00:05.571)       0:05:26.943 *******

TASK [remote/remote-install : Check if the subcloud deployed but failed] ************************************************************************

Wednesday 13 March 2024  23:55:48 +0000 (0:00:00.065)       0:05:27.008 *******
fatal: [welktxef-931887-rh-le292s6-021 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)]: FAILED! => changed=true
  cmd: |-
    . /etc/platform/openrc
    dcmanager subcloud show welktxef-d931887-021 --column "deploy_status" --format value
  delta: '0:00:03.678635'
  end: '2024-03-13 23:55:53.767282'
  msg: non-zero return code
  rc: 1
  start: '2024-03-13 23:55:50.088647'
  stderr: ERROR (app) The resource could not be found. Subcloud not found
  stderr_lines: <omitted>
  stdout: ''
  stdout_lines: <omitted>
...ignoring%)

TASK [remote/remote-install : debug] ************************************************************************************************************

Wednesday 13 March 2024  23:55:53 +0000 (0:00:05.769)       0:05:32.778 *******
ok: [welktxef-931887-rh-le292s6-021] =>
  msg: 'subcloud_status:'

TASK [remote/remote-install : Delete the subcloud that is in failed state] **********************************************************************

Wednesday 13 March 2024  23:55:54 +0000 (0:00:00.020)       0:05:32.798 *******
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-install : include_tasks] ****************************************************************************************************

Wednesday 13 March 2024  23:55:54 +0000 (0:00:00.018)       0:05:32.817 *******
included: /home/szabota/playbooks/wr-installer-atlas-me/roles/remote/remote-utility/tasks/enable_mwait.yaml for welktxef-931887-rh-le292s6-
021

TASK [remote/remote-install : Enable mwait for ZTS Proteus] *************************************************************************************

Wednesday 13 March 2024  23:55:54 +0000 (0:00:00.029)       0:05:32.846 *******
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-install : Deploy remote cloud] **********************************************************************************************

Wednesday 13 March 2024  23:55:54 +0000 (0:00:00.021)       0:05:32.868 *******
changed: [welktxef-931887-rh-le292s6-021 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)]

TASK [remote/remote-install : 1st polling prep: Obtain Keystone auth token] *********************************************************************

Wednesday 13 March 2024  23:56:00 +0000 (0:00:06.741)       0:05:39.609 *******
ok: [welktxef-931887-rh-le292s6-021 -> localhost]

TASK [remote/remote-install : 1st polling: Wait for subcloud to start installing OS] ************************************************************

Wednesday 13 March 2024  23:56:01 +0000 (0:00:00.981)       0:05:40.590 *******
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 1st polling: Wait for subcloud to start installing OS (40 retries left).

ok: [welktxef-931887-rh-le292s6-021 -> localhost]

TASK [remote/remote-install : 1st polling result: Fail if the installation failed] **************************************************************

Wednesday 13 March 2024  23:56:32 +0000 (0:00:31.072)       0:06:11.663 *******
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-install : 2nd polling prep: Obtain Keystone auth token] *********************************************************************

Wednesday 13 March 2024  23:56:32 +0000 (0:00:00.022)       0:06:11.685 *******
ok: [welktxef-931887-rh-le292s6-021 -> localhost]

TASK [remote/remote-install : 2nd polling: Wait for subcloud to install OS (this will take a while)] ********************************************

Wednesday 13 March 2024  23:56:33 +0000 (0:00:00.851)       0:06:12.537 *******
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (10
0 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (99
 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (98
 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (97
 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (96
 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (95
 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (94
 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (93
 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (92
 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (91
 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (90
 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (89
 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (88
 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (87
 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (86
 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (85
 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (84
 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (83
 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (82
 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (81
 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (80
 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (79
 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (78
 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (77
 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (76
 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (75
 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (74
 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (73
 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (72
 retries left).
ok: [welktxef-931887-rh-le292s6-021 -> localhost]

TASK [remote/remote-install : 2nd polling result: Fail if any error occurred] *******************************************************************

Thursday 14 March 2024  00:11:14 +0000 (0:14:40.381)       0:20:52.918 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-install : include_tasks] ****************************************************************************************************

Thursday 14 March 2024  00:11:14 +0000 (0:00:00.021)       0:20:52.939 ********
included: /home/szabota/playbooks/wr-installer-atlas-me/roles/remote/remote-install/tasks/set-time.yaml for welktxef-931887-rh-le292s6-021


TASK [remote/remote-install : Test if remote host is pingable] **********************************************************************************

Thursday 14 March 2024  00:11:14 +0000 (0:00:00.029)       0:20:52.969 ********
changed: [welktxef-931887-rh-le292s6-021 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)]

TASK [remote/remote-install : Get subcloud system time] *****************************************************************************************

Thursday 14 March 2024  00:11:16 +0000 (0:00:02.119)       0:20:55.088 ********
changed: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-install : Print subcloud system time] ***************************************************************************************

Thursday 14 March 2024  00:11:17 +0000 (0:00:01.669)       0:20:56.758 ********
ok: [welktxef-931887-rh-le292s6-021] =>
  msg: 'subcloud system time: Thu 14 Mar 2024 12:11:17 AM UTC'

TASK [remote/remote-install : Stop NTP service] *************************************************************************************************

Thursday 14 March 2024  00:11:17 +0000 (0:00:00.028)       0:20:56.786 ********
fatal: [welktxef-931887-rh-le292s6-021]: FAILED! => changed=false
  msg: 'Could not find the requested service ntpd: host'
...ignoring

TASK [remote/remote-install : Get central controller system time] *******************************************************************************

Thursday 14 March 2024  00:11:19 +0000 (0:00:01.626)       0:20:58.413 ********
changed: [welktxef-931887-rh-le292s6-021 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)]

TASK [remote/remote-install : Print central controller system time] *****************************************************************************

Thursday 14 March 2024  00:11:21 +0000 (0:00:02.106)       0:21:00.519 ********
ok: [welktxef-931887-rh-le292s6-021] =>
  msg: 'central system time: Thu 14 Mar 2024 12:11:21 AM UTC'

TASK [remote/remote-install : Set subcloud system time by central controller system time] *******************************************************

Thursday 14 March 2024  00:11:21 +0000 (0:00:00.025)       0:21:00.545 ********
changed: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-install : Set subcloud system time by NTP server] ***************************************************************************

Thursday 14 March 2024  00:11:23 +0000 (0:00:01.249)       0:21:01.795 ********
changed: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-install : Start NTP service] ************************************************************************************************

Thursday 14 March 2024  00:11:30 +0000 (0:00:07.363)       0:21:09.158 ********
fatal: [welktxef-931887-rh-le292s6-021]: FAILED! => changed=false
  msg: 'Could not find the requested service ntpd: host'
...ignoring

TASK [remote/remote-install : Sync system time to RT clock after adjustment] ********************************************************************

Thursday 14 March 2024  00:11:31 +0000 (0:00:01.396)       0:21:10.555 ********
changed: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-install : Get subcloud system time after adjustment] ************************************************************************

Thursday 14 March 2024  00:11:33 +0000 (0:00:01.887)       0:21:12.442 ********
changed: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-install : Print subcloud system time after adjustment] **********************************************************************

Thursday 14 March 2024  00:11:34 +0000 (0:00:01.232)       0:21:13.675 ********
ok: [welktxef-931887-rh-le292s6-021] =>
  msg: 'subcloud system time after adjustment: Thu 14 Mar 2024 12:11:34 AM UTC'

TASK [remote/remote-install : Set variable time_is_set to true so this code will not be executed again] *****************************************

Thursday 14 March 2024  00:11:34 +0000 (0:00:00.028)       0:21:13.703 ********
ok: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-install : 3rd polling prep: Obtain Keystone auth token] *********************************************************************

Thursday 14 March 2024  00:11:34 +0000 (0:00:00.027)       0:21:13.731 ********
ok: [welktxef-931887-rh-le292s6-021 -> localhost]

TASK [remote/remote-install : 3rd polling: Wait for subcloud to install OS (this may take a while)] *********************************************

Thursday 14 March 2024  00:11:35 +0000 (0:00:00.874)       0:21:14.605 ********
ok: [welktxef-931887-rh-le292s6-021 -> localhost]

TASK [remote/remote-install : 3rd polling result: Fail if any error occurred] *******************************************************************

Thursday 14 March 2024  00:11:36 +0000 (0:00:00.434)       0:21:15.039 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-install : include_tasks] ****************************************************************************************************

Thursday 14 March 2024  00:11:36 +0000 (0:00:00.021)       0:21:15.060 ********
included: /home/szabota/playbooks/wr-installer-atlas-me/roles/remote/remote-install/tasks/set-time.yaml for welktxef-931887-rh-le292s6-021


TASK [remote/remote-install : Test if remote host is pingable] **********************************************************************************

Thursday 14 March 2024  00:11:36 +0000 (0:00:00.032)       0:21:15.093 ********
changed: [welktxef-931887-rh-le292s6-021 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)]

TASK [remote/remote-install : Get subcloud system time] *****************************************************************************************

Thursday 14 March 2024  00:11:38 +0000 (0:00:02.121)       0:21:17.214 ********
changed: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-install : Print subcloud system time] ***************************************************************************************

Thursday 14 March 2024  00:11:39 +0000 (0:00:01.220)       0:21:18.435 ********
ok: [welktxef-931887-rh-le292s6-021] =>
  msg: 'subcloud system time: Thu 14 Mar 2024 12:11:39 AM UTC'

TASK [remote/remote-install : Stop NTP service] *************************************************************************************************

Thursday 14 March 2024  00:11:39 +0000 (0:00:00.029)       0:21:18.464 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-install : Get central controller system time] *******************************************************************************

Thursday 14 March 2024  00:11:39 +0000 (0:00:00.020)       0:21:18.485 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-install : Print central controller system time] *****************************************************************************

Thursday 14 March 2024  00:11:39 +0000 (0:00:00.017)       0:21:18.503 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-install : Set subcloud system time by central controller system time] *******************************************************

Thursday 14 March 2024  00:11:39 +0000 (0:00:00.018)       0:21:18.521 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-install : Set subcloud system time by NTP server] ***************************************************************************

Thursday 14 March 2024  00:11:39 +0000 (0:00:00.015)       0:21:18.537 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-install : Start NTP service] ************************************************************************************************

Thursday 14 March 2024  00:11:39 +0000 (0:00:00.015)       0:21:18.552 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-install : Sync system time to RT clock after adjustment] ********************************************************************

Thursday 14 March 2024  00:11:39 +0000 (0:00:00.015)       0:21:18.568 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-install : Get subcloud system time after adjustment] ************************************************************************

Thursday 14 March 2024  00:11:39 +0000 (0:00:00.015)       0:21:18.584 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-install : Print subcloud system time after adjustment] **********************************************************************

Thursday 14 March 2024  00:11:39 +0000 (0:00:00.015)       0:21:18.599 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-install : Set variable time_is_set to true so this code will not be executed again] *****************************************

Thursday 14 March 2024  00:11:39 +0000 (0:00:00.015)       0:21:18.615 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-install : 4th polling prep: Obtain Keystone auth token] *********************************************************************

Thursday 14 March 2024  00:11:39 +0000 (0:00:00.016)       0:21:18.632 ********
ok: [welktxef-931887-rh-le292s6-021 -> localhost]

TASK [remote/remote-install : 4th polling: Wait for subcloud to install OS (this may still take a while)] ***************************************

Thursday 14 March 2024  00:11:40 +0000 (0:00:00.837)       0:21:19.469 ********
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (100 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (99 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (98 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (97 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (96 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (95 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (94 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (93 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (92 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (91 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (90 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (89 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (88 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (87 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (86 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (85 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (84 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (83 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (82 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (81 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (80 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (79 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (78 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (77 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (76 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (75 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (74 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (73 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (72 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (71 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (70 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (69 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (68 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (67 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (66 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (65 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (64 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (63 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (62 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (61 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (60 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (59 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (58 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (57 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (56 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (55 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (54 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (53 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (52 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (51 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (50 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (49 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (48 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (47 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (46 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (45 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (44 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (43 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (42 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (41 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (40 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (39 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (38 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (37 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (36 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (35 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (34 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (33 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (32 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (31 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (30 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (29 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (28 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (27 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (26 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (25 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (24 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (23 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (22 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (21 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (20 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (19 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (18 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (17 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (16 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (15 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (14 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (13 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (12 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (11 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while
) (10 retries left).
ok: [welktxef-931887-rh-le292s6-021 -> localhost]

TASK [remote/remote-install : 4th polling result: Fail if the installation failed] **************************************************************

Thursday 14 March 2024  00:57:42 +0000 (0:46:02.192)       1:07:21.662 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-install : include_tasks] ****************************************************************************************************

Thursday 14 March 2024  00:57:42 +0000 (0:00:00.021)       1:07:21.683 ********
included: /home/szabota/playbooks/wr-installer-atlas-me/roles/remote/remote-install/tasks/set-time.yaml for welktxef-931887-rh-le292s6-021


TASK [remote/remote-install : Test if remote host is pingable] **********************************************************************************

Thursday 14 March 2024  00:57:42 +0000 (0:00:00.035)       1:07:21.719 ********
changed: [welktxef-931887-rh-le292s6-021 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)]

TASK [remote/remote-install : Get subcloud system time] *****************************************************************************************

Thursday 14 March 2024  00:57:45 +0000 (0:00:02.114)       1:07:23.834 ********
changed: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-install : Print subcloud system time] ***************************************************************************************

Thursday 14 March 2024  00:57:46 +0000 (0:00:01.204)       1:07:25.039 ********
ok: [welktxef-931887-rh-le292s6-021] =>
  msg: 'subcloud system time: Thu 14 Mar 2024 12:57:46 AM UTC'

TASK [remote/remote-install : Stop NTP service] *************************************************************************************************

Thursday 14 March 2024  00:57:46 +0000 (0:00:00.029)       1:07:25.068 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-install : Get central controller system time] *******************************************************************************

Thursday 14 March 2024  00:57:46 +0000 (0:00:00.019)       1:07:25.088 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-install : Print central controller system time] *****************************************************************************

Thursday 14 March 2024  00:57:46 +0000 (0:00:00.016)       1:07:25.104 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-install : Set subcloud system time by central controller system time] *******************************************************

Thursday 14 March 2024  00:57:46 +0000 (0:00:00.018)       1:07:25.123 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-install : Set subcloud system time by NTP server] ***************************************************************************

Thursday 14 March 2024  00:57:46 +0000 (0:00:00.015)       1:07:25.138 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-install : Start NTP service] ************************************************************************************************

Thursday 14 March 2024  00:57:46 +0000 (0:00:00.014)       1:07:25.153 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-install : Sync system time to RT clock after adjustment] ********************************************************************

Thursday 14 March 2024  00:57:46 +0000 (0:00:00.015)       1:07:25.168 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-install : Get subcloud system time after adjustment] ************************************************************************

Thursday 14 March 2024  00:57:46 +0000 (0:00:00.014)       1:07:25.183 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-install : Print subcloud system time after adjustment] **********************************************************************

Thursday 14 March 2024  00:57:46 +0000 (0:00:00.015)       1:07:25.199 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-install : Set variable time_is_set to true so this code will not be executed again] *****************************************

Thursday 14 March 2024  00:57:46 +0000 (0:00:00.015)       1:07:25.214 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-install : 5th polling prep: Obtain Keystone auth token] *********************************************************************

Thursday 14 March 2024  00:57:46 +0000 (0:00:00.016)       1:07:25.231 ********
ok: [welktxef-931887-rh-le292s6-021 -> localhost]

TASK [remote/remote-install : 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while)] **************************

Thursday 14 March 2024  00:57:47 +0000 (0:00:00.845)       1:07:26.077 ********
ok: [welktxef-931887-rh-le292s6-021 -> localhost]

TASK [remote/remote-install : 5th polling result: Fail if install/bootstrap/deploy failed] ******************************************************

Thursday 14 March 2024  00:57:47 +0000 (0:00:00.488)       1:07:26.566 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-install : include_tasks] ****************************************************************************************************

Thursday 14 March 2024  00:57:47 +0000 (0:00:00.020)       1:07:26.587 ********
included: /home/szabota/playbooks/wr-installer-atlas-me/roles/remote/remote-install/tasks/set-time.yaml for welktxef-931887-rh-le292s6-021


TASK [remote/remote-install : Test if remote host is pingable] **********************************************************************************

Thursday 14 March 2024  00:57:47 +0000 (0:00:00.038)       1:07:26.625 ********
changed: [welktxef-931887-rh-le292s6-021 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)]

TASK [remote/remote-install : Get subcloud system time] *****************************************************************************************

Thursday 14 March 2024  00:57:49 +0000 (0:00:02.121)       1:07:28.747 ********
changed: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-install : Print subcloud system time] ***************************************************************************************

Thursday 14 March 2024  00:57:51 +0000 (0:00:01.195)       1:07:29.942 ********
ok: [welktxef-931887-rh-le292s6-021] =>
  msg: 'subcloud system time: Thu 14 Mar 2024 12:57:50 AM UTC'

TASK [remote/remote-install : Stop NTP service] *************************************************************************************************

Thursday 14 March 2024  00:57:51 +0000 (0:00:00.029)       1:07:29.971 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-install : Get central controller system time] *******************************************************************************

Thursday 14 March 2024  00:57:51 +0000 (0:00:00.018)       1:07:29.990 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-install : Print central controller system time] *****************************************************************************

Thursday 14 March 2024  00:57:51 +0000 (0:00:00.016)       1:07:30.006 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-install : Set subcloud system time by central controller system time] *******************************************************

Thursday 14 March 2024  00:57:51 +0000 (0:00:00.015)       1:07:30.022 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-install : Set subcloud system time by NTP server] ***************************************************************************

Thursday 14 March 2024  00:57:51 +0000 (0:00:00.015)       1:07:30.038 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-install : Start NTP service] ************************************************************************************************

Thursday 14 March 2024  00:57:51 +0000 (0:00:00.015)       1:07:30.053 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-install : Sync system time to RT clock after adjustment] ********************************************************************

Thursday 14 March 2024  00:57:51 +0000 (0:00:00.015)       1:07:30.069 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-install : Get subcloud system time after adjustment] ************************************************************************

Thursday 14 March 2024  00:57:51 +0000 (0:00:00.015)       1:07:30.085 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-install : Print subcloud system time after adjustment] **********************************************************************

Thursday 14 March 2024  00:57:51 +0000 (0:00:00.014)       1:07:30.099 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-install : Set variable time_is_set to true so this code will not be executed again] *****************************************

Thursday 14 March 2024  00:57:51 +0000 (0:00:00.015)       1:07:30.115 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-install : 6th polling prep: Obtain Keystone auth token] *********************************************************************

Thursday 14 March 2024  00:57:51 +0000 (0:00:00.016)       1:07:30.132 ********
ok: [welktxef-931887-rh-le292s6-021 -> localhost]

TASK [remote/remote-install : 6th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while)] **************************

Thursday 14 March 2024  00:57:52 +0000 (0:00:00.854)       1:07:30.986 ********
ok: [welktxef-931887-rh-le292s6-021 -> localhost]

TASK [remote/remote-install : include_tasks] ****************************************************************************************************

Thursday 14 March 2024  00:57:52 +0000 (0:00:00.512)       1:07:31.499 ********
included: /home/szabota/playbooks/wr-installer-atlas-me/roles/remote/remote-utility/tasks/disable_mwait.yaml for welktxef-931887-rh-le292s6
-021

TASK [remote/remote-install : Disable mwait for ZTS Proteus] ************************************************************************************

Thursday 14 March 2024  00:57:52 +0000 (0:00:00.051)       1:07:31.551 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-install : 6th polling result: Fail if bootstrap/deploy failed] **************************************************************

Thursday 14 March 2024  00:57:52 +0000 (0:00:00.023)       1:07:31.574 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-install : include_tasks] ****************************************************************************************************

Thursday 14 March 2024  00:57:52 +0000 (0:00:00.022)       1:07:31.596 ********
included: /home/szabota/playbooks/wr-installer-atlas-me/roles/remote/remote-install/tasks/set-time.yaml for welktxef-931887-rh-le292s6-021


TASK [remote/remote-install : Test if remote host is pingable] **********************************************************************************

Thursday 14 March 2024  00:57:52 +0000 (0:00:00.045)       1:07:31.642 ********
changed: [welktxef-931887-rh-le292s6-021 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)]

TASK [remote/remote-install : Get subcloud system time] *****************************************************************************************

Thursday 14 March 2024  00:57:55 +0000 (0:00:02.156)       1:07:33.799 ********
changed: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-install : Print subcloud system time] ***************************************************************************************

Thursday 14 March 2024  00:57:56 +0000 (0:00:01.214)       1:07:35.014 ********
ok: [welktxef-931887-rh-le292s6-021] =>
  msg: 'subcloud system time: Thu 14 Mar 2024 12:57:56 AM UTC'

TASK [remote/remote-install : Stop NTP service] *************************************************************************************************

Thursday 14 March 2024  00:57:56 +0000 (0:00:00.026)       1:07:35.040 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-install : Get central controller system time] *******************************************************************************

Thursday 14 March 2024  00:57:56 +0000 (0:00:00.020)       1:07:35.060 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-install : Print central controller system time] *****************************************************************************

Thursday 14 March 2024  00:57:56 +0000 (0:00:00.018)       1:07:35.079 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-install : Set subcloud system time by central controller system time] *******************************************************

Thursday 14 March 2024  00:57:56 +0000 (0:00:00.017)       1:07:35.096 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-install : Set subcloud system time by NTP server] ***************************************************************************

Thursday 14 March 2024  00:57:56 +0000 (0:00:00.017)       1:07:35.114 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-install : Start NTP service] ************************************************************************************************

Thursday 14 March 2024  00:57:56 +0000 (0:00:00.019)       1:07:35.134 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-install : Sync system time to RT clock after adjustment] ********************************************************************

Thursday 14 March 2024  00:57:56 +0000 (0:00:00.018)       1:07:35.152 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-install : Get subcloud system time after adjustment] ************************************************************************

Thursday 14 March 2024  00:57:56 +0000 (0:00:00.017)       1:07:35.170 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-install : Print subcloud system time after adjustment] **********************************************************************

Thursday 14 March 2024  00:57:56 +0000 (0:00:00.019)       1:07:35.189 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-install : Set variable time_is_set to true so this code will not be executed again] *****************************************

Thursday 14 March 2024  00:57:56 +0000 (0:00:00.018)       1:07:35.207 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-install : Wait for controller-0 restart] ************************************************************************************

Thursday 14 March 2024  00:57:56 +0000 (0:00:00.018)       1:07:35.226 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-install : Wait for controller-0 recovery] ***********************************************************************************

Thursday 14 March 2024  00:57:56 +0000 (0:00:00.025)       1:07:35.251 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/remote-install : setup kdump] ******************************************************************************************************

Thursday 14 March 2024  00:57:56 +0000 (0:00:00.021)       1:07:35.273 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [Wait for hosts and system to be reconciled] ***********************************************************************************************

Thursday 14 March 2024  00:57:56 +0000 (0:00:00.024)       1:07:35.298 ********

TASK [common/wait_for_reconciliation : Making sure node is reachable] ***************************************************************************

Thursday 14 March 2024  00:57:56 +0000 (0:00:00.033)       1:07:35.331 ********
ok: [welktxef-931887-rh-le292s6-021]

TASK [common/wait_for_reconciliation : Wait for K8s API to be up] *******************************************************************************

Thursday 14 March 2024  00:57:57 +0000 (0:00:01.409)       1:07:36.741 ********
ok: [welktxef-931887-rh-le292s6-021]

TASK [common/wait_for_reconciliation : Wait for all 3 hosts to show up] *************************************************************************

Thursday 14 March 2024  00:57:59 +0000 (0:00:01.372)       1:07:38.113 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [common/wait_for_reconciliation : Wait for hosts to be reconciled] *************************************************************************

Thursday 14 March 2024  00:57:59 +0000 (0:00:00.025)       1:07:38.139 ********
changed: [welktxef-931887-rh-le292s6-021]

TASK [common/wait_for_reconciliation : Wait for systems to be reconciled] ***********************************************************************

Thursday 14 March 2024  00:58:00 +0000 (0:00:01.278)       1:07:39.417 ********
changed: [welktxef-931887-rh-le292s6-021]

TASK [Remote Manage] ****************************************************************************************************************************

Thursday 14 March 2024  00:58:01 +0000 (0:00:01.295)       1:07:40.713 ********

TASK [remote/manage : 1st Obtain Keystone auth token] *******************************************************************************************

Thursday 14 March 2024  00:58:01 +0000 (0:00:00.063)       1:07:40.776 ********
ok: [welktxef-931887-rh-le292s6-021 -> localhost]

TASK [remote/manage : 1st Wait for contoller-0 availability status online] **********************************************************************

Thursday 14 March 2024  00:58:02 +0000 (0:00:00.874)       1:07:41.650 ********
ok: [welktxef-931887-rh-le292s6-021 -> localhost]

TASK [remote/manage : 2nd Obtain Keystone auth token] *******************************************************************************************

Thursday 14 March 2024  00:58:03 +0000 (0:00:00.445)       1:07:42.096 ********
ok: [welktxef-931887-rh-le292s6-021 -> localhost]

TASK [remote/manage : 2nd Wait for contoller-0 availability status online] **********************************************************************

Thursday 14 March 2024  00:58:04 +0000 (0:00:00.859)       1:07:42.955 ********
ok: [welktxef-931887-rh-le292s6-021 -> localhost]

TASK [remote/manage : Wait for system to stabilize before running kubectl] **********************************************************************

Thursday 14 March 2024  00:58:04 +0000 (0:00:00.453)       1:07:43.408 ********
Pausing for 480 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [welktxef-931887-rh-le292s6-021]

TASK [Wait for system and hosts to be reconciled] ***********************************************************************************************

Thursday 14 March 2024  01:06:04 +0000 (0:08:00.020)       1:15:43.428 ********

TASK [common/wait_for_reconciliation : Making sure node is reachable] ***************************************************************************

Thursday 14 March 2024  01:06:04 +0000 (0:00:00.028)       1:15:43.457 ********
ok: [welktxef-931887-rh-le292s6-021]

TASK [common/wait_for_reconciliation : Wait for K8s API to be up] *******************************************************************************

Thursday 14 March 2024  01:06:05 +0000 (0:00:01.281)       1:15:44.739 ********
ok: [welktxef-931887-rh-le292s6-021]

TASK [common/wait_for_reconciliation : Wait for all 3 hosts to show up] *************************************************************************

Thursday 14 March 2024  01:06:07 +0000 (0:00:01.227)       1:15:45.966 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [common/wait_for_reconciliation : Wait for hosts to be reconciled] *************************************************************************

Thursday 14 March 2024  01:06:07 +0000 (0:00:00.017)       1:15:45.984 ********
changed: [welktxef-931887-rh-le292s6-021]

TASK [common/wait_for_reconciliation : Wait for systems to be reconciled] ***********************************************************************

Thursday 14 March 2024  01:06:08 +0000 (0:00:01.257)       1:15:47.242 ********
changed: [welktxef-931887-rh-le292s6-021]

TASK [remote/manage : Wait for distributed cloud to be reconciled but subcloud OAM VIP becomes unreachable] *************************************

Thursday 14 March 2024  01:06:09 +0000 (0:00:01.277)       1:15:48.519 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/manage : Check if the subcloud deployed but failed] ********************************************************************************

Thursday 14 March 2024  01:06:09 +0000 (0:00:00.026)       1:15:48.545 ********
changed: [welktxef-931887-rh-le292s6-021 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)]

TASK [remote/manage : Set distributed cloud state to managed] ***********************************************************************************

Thursday 14 March 2024  01:06:15 +0000 (0:00:05.849)       1:15:54.395 ********
changed: [welktxef-931887-rh-le292s6-021 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)]

TASK [remote/manage : Wait for system to stabilize] *********************************************************************************************

Thursday 14 March 2024  01:06:21 +0000 (0:00:06.075)       1:16:00.471 ********
Pausing for 300 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [welktxef-931887-rh-le292s6-021]

TASK [Remote Trust] *****************************************************************************************************************************

Thursday 14 March 2024  01:11:21 +0000 (0:05:00.020)       1:21:00.492 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [Remote Starlingx] *************************************************************************************************************************

Thursday 14 March 2024  01:11:21 +0000 (0:00:00.023)       1:21:00.515 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [Remote Starlingx and Registry] ************************************************************************************************************

Thursday 14 March 2024  01:11:21 +0000 (0:00:00.020)       1:21:00.536 ********

TASK [remote/starlingx : Copy ICA cert] *********************************************************************************************************

Thursday 14 March 2024  01:11:21 +0000 (0:00:00.065)       1:21:00.601 ********
changed: [welktxef-931887-rh-le292s6-021] => (item={'filename': 'vz_root_ica_cert.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIFNzCCAx+g
AwIBAgIUGLJR/hP48n+vdq2v1hcfspXo/78wDQYJKoZIhvcNAQEL\nBQAwWjELMAkGA1UEBhMCVVMxEDAOBgNVBAoMB1Zlcml6b24xEzARBgNVBAsMClZa\nSUFNIFRlc3QxJDAiBgNVBAMMG
1Zlcml6b24gTmV0d29yayBSU0EgQ0EgVGVzdDAe\nFw0yMDEwMjIyMTE0MDNaFw0zMDEwMjIyMTE0MDNaMIGRMQswCQYDVQQGEwJVUzEL\nMAkGA1UECAwCVFgxETAPBgNVBAcMCFdlc3RsYW
tlMRAwDgYDVQQKDAdWZXJpem9u\nMR0wGwYDVQQLDBRWZXJpem9uIFNvdXJjaW5nIExMQzExMC8GA1UEAwwoVmVyaXpv\nbiBOZXR3b3JrIFdFTEtUWElCIExBQiAxIDMgUlNBIElDQTCCASI
wDQYJKoZIhvcN\nAQEBBQADggEPADCCAQoCggEBANhkGTXOCKEYf5znDDeX3n/DHFPVqazgQsr0/SIG\n4eb1JY5q5Jq3ZhAaZCr9HJuCkwAP/zgYH0llqOvf8AC2Uh+7z1b33IbwxPmJfWCP
\nAqSNFkLWWVRdbELapCu408QsrLMW8IrdP6PLiKAepwncfm4T0/6bANqIEmUkpw8Q\nxProeiNwlGbwUll+tELmdCk7vA7hKX3j1kUvS5Z84Z5ivJBWEcUEggmC97TK4aLo\nFVEHbyahze5
68JVEaM1vY5L4mnRRTl+u5ipaSMxVBsiXzF7eFuKCzqF7wxbDIt2T\nIFEJtwyJDW5bXjyXgiF1d5H/URprUcRV9Qmf2+PXcfwHII8CAwEAAaOBvDCBuTAS\nBgNVHRMBAf8ECDAGAQH/AgEA
MA4GA1UdDwEB/wQEAwIBBjAfBgNVHSMEGDAWgBQl\neng3lqGBeTrbLVuABoEmUHm1+TBTBgNVHR8ETDBKMEigRqBEhkJodHRwOi8vc2Vj\ndXJlLnN0YWdpbmcuc2VjdXJpdHljcmVkZW50a
WFsaW5nLmNvbS9jcmwvdnpuZXRy\nc2FjYS5jcmwwHQYDVR0OBBYEFP0Z+/vaDLtAoFig1I9ttNKnmzByMA0GCSqGSIb3\nDQEBCwUAA4ICAQBuXVTf9e01HeymHgRcFCwP2N6G6u+vIzY8Bz
0zSUZeRDHMZQcS\nNoabDyn5FfGJlw4BqGC591Sp0/unFQDzAg17rDBcrgwajeFeUiFdb9PiAJwHaX9S\nvq/7VmVLCmpeb+a/laXAe6+tkY1kcFrd1+ItRKC6ZGXMsoDkmk5Ndxxgw77estc
I\nMiiLQbvpXRygX5wD4/ayazuLms9qITZkOZ1nTLVqq7QrwYCsSoih7hj6sbsfXr19\nGoYWmk8Y7O/d3ttgyHuRH9k/2dQ/xL7avRpMNkPdr7ocJqI46hvx2X6UyOo7IBua\nkSkFbSmPZW
IVAidNMBOnvffCQ32tfjT2/xso/a9cdskvxqgLi0MPARU9Nl2Pufsb\nD7l4/sBvz/PiNTKp+Daa9FdyLb9ySidos1uS0c24bUtY1RXXGAVV2qgfyrzvzfye\nSM+w16hMU/yeYiuA1jsPmsn
ZnuIJj4Nv8ZjjZ0WS53pP5wcghaHkBrqWQNT8meqA\nVElrMBPlYq67T+AXP0B9lf5Sc3QVIio7XKKfqrlcQxY2JGLEyE53JgZGX7dpwU4I\nukLvyHbT4p06oY3qG6+wH8+YIXCNAYtadJ/C
5/u9GcLX5NnZrcuduj0inw2/a3Ao\nWgCt6/Pr28BkCvkWdDt9d8Z40qeu1aZdcr157mR+yZGPfBfB2vasrNIEwQ==\n-----END CERTIFICATE-----\n'})
changed: [welktxef-931887-rh-le292s6-021] => (item={'filename': 'vz_root_ica_key.pem', 'value': '-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBA
AKCAQEA2GQZNc4IoRh/nOcMN5fef8McU9WprOBCyvT9Igbh5vUljmrk\nmrdmEBpkKv0cm4KTAA//OBgfSWWo69/wALZSH7vPVvfchvDE+Yl9YI8CpI0WQtZZ\nVF1sQtqkK7jTxCyssxbwit
0/o8uIoB6nCdx+bhPT/psA2ogSZSSnDxDE+uh6I3CU\nZvBSWX60QuZ0KTu8DuEpfePWRS9LlnzhnmK8kFYRxQSCCYL3tMrhougVUQdvJqHN\n7nrwlURozW9jkviadFFOX67mKlpIzFUGyJf
MXt4W4oLOoXvDFsMi3ZMgUQm3DIkN\nbltePJeCIXV3kf9RGmtRxFX1CZ/b49dx/AcgjwIDAQABAoIBABSd1NkPfDr8/ouQ\nZ9WUHprFmBlUrgnOhA6aMNPhG/zJNn7PKGClQJAgM5L08pjO
Y/sJiyNpCPIRQXrX\npyIqPMDRP/vlOZmRrvKnas6cUYAkAQ71JSWokPv9oM6ZmXODXiDh+qEAW2PbrHS0\n9u01mMYcFYKYeghYFoiUaWZCDsJo3v3dgeE9aQ4tB9ksovSmWrpuCY7NKbd7Q
rbo\n5XxQhkujTkE6knOHz8CVwYETtj8LZ/bvHIkGMGvRvwsKYDZkIKr5CZ7DX+KcMfPN\neMZU4VCHYSXNxsyp5DJ1Zw+gx8/32kUL0CzJLLam1G021Hq41KPwwSV/KPrOKel7\nHXDLXeEC
gYEA8MR+lgxGjYTc/k4TdZvcFVgqHGLXnyjO7ZVt4b7UpwmayLuoSD/M\nOpHQYX+JBIIWTNlGhG8UV3DPC3v+auhYa7twwbekS30IYCAmu5GCKgMAcWFinz6A\nYZxG55P/hShetCyOqikgw
XqzMlwGs8KEul8f8BKssROzUy8mIlFhjq0CgYEA5hTM\nSNxAD3dlRtb0771fBU7fjx8JPfjptP9vP/JVEelkc/ti9nZ5buTC+9cQC/B+YFx7\nc82uCrXV13bGR9iH8xBhwU7JOYJZbgCpwp
0F56wIN5Pdk9Eo79Batrw3oGBG4Yvt\nDc2eltxQbHgObc/qygf88j9XqD8aGIvQrc4Jf6sCgYAtxX03M1A6WTbWFau3YRD+\n8crXqKbLOCvWmODR2MB+nOHTJXHBgndl7xCJaIB43e41X9z
7Ek7wrJ5/1WuxkUg1\n+uVdvna6byOnepVCdVAkgnuUEmp4UZ6AcAA+yDD8dIdEg2//w1/ZyGTGvx37EJDB\nCZJ9xl8ULuWZe84pGgWM5QKBgQCYVUbYKrNjShrM5z9uh4QlII6V1Oeql2Yt
Bz4i\nKZE3db6jp9pi8hf+WwnZ8g9WyFjz9edqydAkmTXHHYW0ReHlBYCjm0VRhUMuuNOs\n3YfuVpFuMsFuv/oJpXqaKE3wKi5j4OAH1o7ctWuuFWMAQ7vhHZ7UySmBZJ4jiFaW\n7KaPVwK
BgE8E0xbSDVGxXbEGwRXxeaOSemEHD9uEnbAyq1p3EBBhBvInWmDiP5vJ\n68IYNZ4SGxXEKDifwrLGHyekt3RK9B2+U03okd1qH7gfBIlxBJivcjhBe2PtK/Qj\n6fBN0fC1UJoE6pseT9cJ
DaBq2wMRXJGRYtT8fU9PPJcfa23JlKNS\n-----END RSA PRIVATE KEY-----'})

TASK [remote/starlingx : Create VZ ICA secret to back the clusterIssuer] ************************************************************************

Thursday 14 March 2024  01:11:26 +0000 (0:00:04.631)       1:21:05.233 ********
changed: [welktxef-931887-rh-le292s6-021]

TASK [remote/starlingx : Create VZ ICA clusterIssuer] *******************************************************************************************

Thursday 14 March 2024  01:11:27 +0000 (0:00:01.276)       1:21:06.510 ********
changed: [welktxef-931887-rh-le292s6-021]

TASK [remote/starlingx : Make sure VZ ICA clusterIssuer is Ready before proceeding] *************************************************************

Thursday 14 March 2024  01:11:29 +0000 (0:00:01.428)       1:21:07.938 ********
changed: [welktxef-931887-rh-le292s6-021]

TASK [remote/starlingx : create Rest Api (starlingx) certificate] *******************************************************************************

Thursday 14 March 2024  01:11:30 +0000 (0:00:01.218)       1:21:09.157 ********
changed: [welktxef-931887-rh-le292s6-021]

TASK [remote/starlingx : make sure Rest Api (starlingx) certificate is Ready before proceeding] *************************************************

Thursday 14 March 2024  01:11:31 +0000 (0:00:01.470)       1:21:10.628 ********
changed: [welktxef-931887-rh-le292s6-021]

TASK [remote/starlingx : wait until system configuration is updated] ****************************************************************************

Thursday 14 March 2024  01:11:33 +0000 (0:00:01.250)       1:21:11.878 ********
changed: [welktxef-931887-rh-le292s6-021]

TASK [remote/starlingx : create registry certificate] *******************************************************************************************

Thursday 14 March 2024  01:11:37 +0000 (0:00:04.729)       1:21:16.608 ********
changed: [welktxef-931887-rh-le292s6-021]

TASK [remote/starlingx : make sure registry certificate is Ready before proceeding] *************************************************************

Thursday 14 March 2024  01:11:39 +0000 (0:00:01.470)       1:21:18.078 ********
changed: [welktxef-931887-rh-le292s6-021]

TASK [remote/starlingx : wait until system configuration is updated] ****************************************************************************

Thursday 14 March 2024  01:11:40 +0000 (0:00:01.283)       1:21:19.361 ********
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021]: wait until system configuration is updated (20 retries left).
changed: [welktxef-931887-rh-le292s6-021]

TASK [Remote Integ] *****************************************************************************************************************************

Thursday 14 March 2024  01:12:20 +0000 (0:00:39.742)       1:21:59.104 ********

TASK [remote/integ : Detect applied status of platform-integ-apps application] ******************************************************************

Thursday 14 March 2024  01:12:20 +0000 (0:00:00.061)       1:21:59.165 ********
changed: [welktxef-931887-rh-le292s6-021]

TASK [remote/integ : Fail if platform-integ-apps application apply failed] **********************************************************************

Thursday 14 March 2024  01:12:25 +0000 (0:00:04.658)       1:22:03.824 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [Remote Ldap] ******************************************************************************************************************************

Thursday 14 March 2024  01:12:25 +0000 (0:00:00.024)       1:22:03.848 ********

TASK [remote/ldap : Create temporary working directory] *****************************************************************************************

Thursday 14 March 2024  01:12:25 +0000 (0:00:00.076)       1:22:03.925 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/ldap : Copy SSL root certificates] *************************************************************************************************

Thursday 14 March 2024  01:12:25 +0000 (0:00:00.028)       1:22:03.953 ********
skipping: [welktxef-931887-rh-le292s6-021] => (item={'filename': 'vz_root_ca_cert.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIFpTCCA42g
AwIBAgIUa3vZ0YGxO1TQ8NwhiVfQC0JslXgwDQYJKoZIhvcNAQEL\nBQAwWjELMAkGA1UEBhMCVVMxEDAOBgNVBAoMB1Zlcml6b24xEzARBgNVBAsMClZa\nSUFNIFRlc3QxJDAiBgNVBAMMG
1Zlcml6b24gTmV0d29yayBSU0EgQ0EgVGVzdDAe\nFw0yMDA2MTUyMTAxMTNaFw0zNTA2MTUyMTAxMTNaMFoxCzAJBgNVBAYTAlVTMRAw\nDgYDVQQKDAdWZXJpem9uMRMwEQYDVQQLDApWWk
lBTSBUZXN0MSQwIgYDVQQDDBtW\nZXJpem9uIE5ldHdvcmsgUlNBIENBIFRlc3QwggIiMA0GCSqGSIb3DQEBAQUAA4IC\nDwAwggIKAoICAQC8AIrksI57CbIl5uGZ6yqfpQj3aK+N8f1EVHd
wK9JFskoipvC8\n7yFTk8tgmO1i0YA5oRGfNxneqCdrXZiWL6Ko8v/iln9vuN+2rK3rgWZPPRJBAsBN\na49L7U6lJjIGxIZtZqmK5h47oiUtwlYVrbZMN2ijuBQ22/eQ9tsFDV28oBuZ3WAR
\npSSbj/tubPQYkw3YYOhv/VpEpsd0rkoEt3QCmTVcX2rtblanpXowTV5R0Hy4014n\nT49jrEo40r4mwYoyS835Uv4ENUFA+pXicT9eUot3RSH6rYdx4A/14UtoI9U0ol8M\n62GHpxSASQ2
Kc3yQWvxRGTFslTduYM+vVmMLEDDdqcsjYnStPpwdxxmKItmbjxSv\nIwYIndp8A04WkX2iiJCciC3BNxiLamPtYVyB1HHqbGTGirKYuSvwZt337q1OI3WH\nwVn2S4Mj/wqa4iCyGTvFSUnG
q34Xkrb9XNwWBok9Tc2XWGAU/mb/xcd1hX74GZbF\nsrZ11aPtym4kMAjU2KQi96GcAH2lnGZYoOja1J4Cs4WYx1uAx74H/m84CrYavVfl\n1ONJVLDfuZaEkSmu+jHQX15pAECNORTuLD06P
bWnOEcOi1xmbt/OT3SA3rhD2mb7\n2wxl7oJpV3ap8xGwYmxiFzmInxFJ1axjg8Rimol0mXTKAy6OdNHbCOnAwwIDAQAB\no2MwYTAPBgNVHRMBAf8EBTADAQH/MA4GA1UdDwEB/wQEAwIBBj
AfBgNVHSMEGDAW\ngBQleng3lqGBeTrbLVuABoEmUHm1+TAdBgNVHQ4EFgQUJXp4N5ahgXk62y1bgAaB\nJlB5tfkwDQYJKoZIhvcNAQELBQADggIBADQ9jpmVh9nyY7ZQ4s+S9RuSRYn7Qsr
W\nDePeMzQgh8ZtS8WE65GY5HS61iHNP2Co8Q1lAaBWF4ipq+VZOcQbPLccHzd1kZv4\ns4u0aTzBd9ccidl73FS0DJDQOBbzPSzgsaiGHSMyGzkTeA8z3ntsSqrXXcDUvoRi\nFus/110Awd
tNhJLrWveX6btYtHp9Lqe0YtNCy5AaXlrr1yRSckP5BWVtlwD4dzSO\n/dqI3wHS/ncUx9wSQomZ+AmxYW3KtJQKgHzTqHru1x9BBk7Bzfz9FZr6HLLmEitj\nuFoDRd5TNt5LbO0zDQokvY3
oqso6Htup/rS7C08mcmnelYE+yXuOc1YrlyGnpBzk\nmy+1VYbOxRRdqKAZRbE72u/h847IVpsOvjR51iksuCAurZdp2+y2zvV8NhWekuNy\nirECRy9cb4YasjRaKi0/TCGPVSICuLyeG2W7
2liCj/N2VKfjPP9zsOR5XjwCXfRg\n+9xhLy77/gov2NWXx5fzTkhxCrHOxFdLVMn0wQhksDmw6QsXzDIHSpIOypdDfnx9\nCsthx3nhkuHLUaEP22D22dG+vImA9ukj4R/RRI/87jmi9Q8+e
hH+NqN0GZZcLjdN\nSLVXpncuwWQFUDPR06wNkkkmBSXWiIYhwqSpU0Pl3er3fD0uWvXuWPm2PzfOmUAE\nUrkzyw9XmLw0\n-----END CERTIFICATE-----\n'})
skipping: [welktxef-931887-rh-le292s6-021] => (item={'filename': 'vz_root_ica_cert.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIFNzCCAx+
gAwIBAgIUGLJR/hP48n+vdq2v1hcfspXo/78wDQYJKoZIhvcNAQEL\nBQAwWjELMAkGA1UEBhMCVVMxEDAOBgNVBAoMB1Zlcml6b24xEzARBgNVBAsMClZa\nSUFNIFRlc3QxJDAiBgNVBAMM
G1Zlcml6b24gTmV0d29yayBSU0EgQ0EgVGVzdDAe\nFw0yMDEwMjIyMTE0MDNaFw0zMDEwMjIyMTE0MDNaMIGRMQswCQYDVQQGEwJVUzEL\nMAkGA1UECAwCVFgxETAPBgNVBAcMCFdlc3RsY
WtlMRAwDgYDVQQKDAdWZXJpem9u\nMR0wGwYDVQQLDBRWZXJpem9uIFNvdXJjaW5nIExMQzExMC8GA1UEAwwoVmVyaXpv\nbiBOZXR3b3JrIFdFTEtUWElCIExBQiAxIDMgUlNBIElDQTCCAS
IwDQYJKoZIhvcN\nAQEBBQADggEPADCCAQoCggEBANhkGTXOCKEYf5znDDeX3n/DHFPVqazgQsr0/SIG\n4eb1JY5q5Jq3ZhAaZCr9HJuCkwAP/zgYH0llqOvf8AC2Uh+7z1b33IbwxPmJfWC
P\nAqSNFkLWWVRdbELapCu408QsrLMW8IrdP6PLiKAepwncfm4T0/6bANqIEmUkpw8Q\nxProeiNwlGbwUll+tELmdCk7vA7hKX3j1kUvS5Z84Z5ivJBWEcUEggmC97TK4aLo\nFVEHbyahze
568JVEaM1vY5L4mnRRTl+u5ipaSMxVBsiXzF7eFuKCzqF7wxbDIt2T\nIFEJtwyJDW5bXjyXgiF1d5H/URprUcRV9Qmf2+PXcfwHII8CAwEAAaOBvDCBuTAS\nBgNVHRMBAf8ECDAGAQH/AgE
AMA4GA1UdDwEB/wQEAwIBBjAfBgNVHSMEGDAWgBQl\neng3lqGBeTrbLVuABoEmUHm1+TBTBgNVHR8ETDBKMEigRqBEhkJodHRwOi8vc2Vj\ndXJlLnN0YWdpbmcuc2VjdXJpdHljcmVkZW50
aWFsaW5nLmNvbS9jcmwvdnpuZXRy\nc2FjYS5jcmwwHQYDVR0OBBYEFP0Z+/vaDLtAoFig1I9ttNKnmzByMA0GCSqGSIb3\nDQEBCwUAA4ICAQBuXVTf9e01HeymHgRcFCwP2N6G6u+vIzY8B
z0zSUZeRDHMZQcS\nNoabDyn5FfGJlw4BqGC591Sp0/unFQDzAg17rDBcrgwajeFeUiFdb9PiAJwHaX9S\nvq/7VmVLCmpeb+a/laXAe6+tkY1kcFrd1+ItRKC6ZGXMsoDkmk5Ndxxgw77est
cI\nMiiLQbvpXRygX5wD4/ayazuLms9qITZkOZ1nTLVqq7QrwYCsSoih7hj6sbsfXr19\nGoYWmk8Y7O/d3ttgyHuRH9k/2dQ/xL7avRpMNkPdr7ocJqI46hvx2X6UyOo7IBua\nkSkFbSmPZ
WIVAidNMBOnvffCQ32tfjT2/xso/a9cdskvxqgLi0MPARU9Nl2Pufsb\nD7l4/sBvz/PiNTKp+Daa9FdyLb9ySidos1uS0c24bUtY1RXXGAVV2qgfyrzvzfye\nSM+w16hMU/yeYiuA1jsPms
nZnuIJj4Nv8ZjjZ0WS53pP5wcghaHkBrqWQNT8meqA\nVElrMBPlYq67T+AXP0B9lf5Sc3QVIio7XKKfqrlcQxY2JGLEyE53JgZGX7dpwU4I\nukLvyHbT4p06oY3qG6+wH8+YIXCNAYtadJ/
C5/u9GcLX5NnZrcuduj0inw2/a3Ao\nWgCt6/Pr28BkCvkWdDt9d8Z40qeu1aZdcr157mR+yZGPfBfB2vasrNIEwQ==\n-----END CERTIFICATE-----\n'})
skipping: [welktxef-931887-rh-le292s6-021] => (item={'filename': 'vz_root_ica_key.pem', 'value': '-----BEGIN RSA PRIVATE KEY-----\nMIIEowIB
AAKCAQEA2GQZNc4IoRh/nOcMN5fef8McU9WprOBCyvT9Igbh5vUljmrk\nmrdmEBpkKv0cm4KTAA//OBgfSWWo69/wALZSH7vPVvfchvDE+Yl9YI8CpI0WQtZZ\nVF1sQtqkK7jTxCyssxbwi
t0/o8uIoB6nCdx+bhPT/psA2ogSZSSnDxDE+uh6I3CU\nZvBSWX60QuZ0KTu8DuEpfePWRS9LlnzhnmK8kFYRxQSCCYL3tMrhougVUQdvJqHN\n7nrwlURozW9jkviadFFOX67mKlpIzFUGyJ
fMXt4W4oLOoXvDFsMi3ZMgUQm3DIkN\nbltePJeCIXV3kf9RGmtRxFX1CZ/b49dx/AcgjwIDAQABAoIBABSd1NkPfDr8/ouQ\nZ9WUHprFmBlUrgnOhA6aMNPhG/zJNn7PKGClQJAgM5L08pj
OY/sJiyNpCPIRQXrX\npyIqPMDRP/vlOZmRrvKnas6cUYAkAQ71JSWokPv9oM6ZmXODXiDh+qEAW2PbrHS0\n9u01mMYcFYKYeghYFoiUaWZCDsJo3v3dgeE9aQ4tB9ksovSmWrpuCY7NKbd7
Qrbo\n5XxQhkujTkE6knOHz8CVwYETtj8LZ/bvHIkGMGvRvwsKYDZkIKr5CZ7DX+KcMfPN\neMZU4VCHYSXNxsyp5DJ1Zw+gx8/32kUL0CzJLLam1G021Hq41KPwwSV/KPrOKel7\nHXDLXeE
CgYEA8MR+lgxGjYTc/k4TdZvcFVgqHGLXnyjO7ZVt4b7UpwmayLuoSD/M\nOpHQYX+JBIIWTNlGhG8UV3DPC3v+auhYa7twwbekS30IYCAmu5GCKgMAcWFinz6A\nYZxG55P/hShetCyOqikg
wXqzMlwGs8KEul8f8BKssROzUy8mIlFhjq0CgYEA5hTM\nSNxAD3dlRtb0771fBU7fjx8JPfjptP9vP/JVEelkc/ti9nZ5buTC+9cQC/B+YFx7\nc82uCrXV13bGR9iH8xBhwU7JOYJZbgCpw
p0F56wIN5Pdk9Eo79Batrw3oGBG4Yvt\nDc2eltxQbHgObc/qygf88j9XqD8aGIvQrc4Jf6sCgYAtxX03M1A6WTbWFau3YRD+\n8crXqKbLOCvWmODR2MB+nOHTJXHBgndl7xCJaIB43e41X9
z7Ek7wrJ5/1WuxkUg1\n+uVdvna6byOnepVCdVAkgnuUEmp4UZ6AcAA+yDD8dIdEg2//w1/ZyGTGvx37EJDB\nCZJ9xl8ULuWZe84pGgWM5QKBgQCYVUbYKrNjShrM5z9uh4QlII6V1Oeql2Y
tBz4i\nKZE3db6jp9pi8hf+WwnZ8g9WyFjz9edqydAkmTXHHYW0ReHlBYCjm0VRhUMuuNOs\n3YfuVpFuMsFuv/oJpXqaKE3wKi5j4OAH1o7ctWuuFWMAQ7vhHZ7UySmBZJ4jiFaW\n7KaPVw
KBgE8E0xbSDVGxXbEGwRXxeaOSemEHD9uEnbAyq1p3EBBhBvInWmDiP5vJ\n68IYNZ4SGxXEKDifwrLGHyekt3RK9B2+U03okd1qH7gfBIlxBJivcjhBe2PtK/Qj\n6fBN0fC1UJoE6pseT9c
JDaBq2wMRXJGRYtT8fU9PPJcfa23JlKNS\n-----END RSA PRIVATE KEY-----'})

TASK [remote/ldap : Copy templates] *************************************************************************************************************

Thursday 14 March 2024  01:12:25 +0000 (0:00:00.036)       1:22:03.990 ********
skipping: [welktxef-931887-rh-le292s6-021] => (item={'name': 'req-ldap.cnf', 'mode': '0644'})

TASK [remote/ldap : Generate SSL cert] **********************************************************************************************************

Thursday 14 March 2024  01:12:25 +0000 (0:00:00.068)       1:22:04.058 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/ldap : Copy templates] *************************************************************************************************************

Thursday 14 March 2024  01:12:25 +0000 (0:00:00.020)       1:22:04.079 ********
skipping: [welktxef-931887-rh-le292s6-021] => (item={'name': 'dex-overrides.yaml', 'mode': '0644'})

TASK [remote/ldap : Copy SSL dex certs to server] ***********************************************************************************************

Thursday 14 March 2024  01:12:25 +0000 (0:00:00.022)       1:22:04.101 ********
skipping: [welktxef-931887-rh-le292s6-021] => (item=dex-cert.pem)
skipping: [welktxef-931887-rh-le292s6-021] => (item=dex-key.pem)
skipping: [welktxef-931887-rh-le292s6-021] => (item=dex-ca.pem)

TASK [remote/ldap : Copy SSL AD cert to server] *************************************************************************************************

Thursday 14 March 2024  01:12:25 +0000 (0:00:00.026)       1:22:04.128 ********
skipping: [welktxef-931887-rh-le292s6-021] => (item={'filename': 'ad_ca.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIFpTCCA42gAwIBAgIUa3
vZ0YGxO1TQ8NwhiVfQC0JslXgwDQYJKoZIhvcNAQEL\nBQAwWjELMAkGA1UEBhMCVVMxEDAOBgNVBAoMB1Zlcml6b24xEzARBgNVBAsMClZa\nSUFNIFRlc3QxJDAiBgNVBAMMG1Zlcml6b24
gTmV0d29yayBSU0EgQ0EgVGVzdDAe\nFw0yMDA2MTUyMTAxMTNaFw0zNTA2MTUyMTAxMTNaMFoxCzAJBgNVBAYTAlVTMRAw\nDgYDVQQKDAdWZXJpem9uMRMwEQYDVQQLDApWWklBTSBUZXN0
MSQwIgYDVQQDDBtW\nZXJpem9uIE5ldHdvcmsgUlNBIENBIFRlc3QwggIiMA0GCSqGSIb3DQEBAQUAA4IC\nDwAwggIKAoICAQC8AIrksI57CbIl5uGZ6yqfpQj3aK+N8f1EVHdwK9JFskoip
vC8\n7yFTk8tgmO1i0YA5oRGfNxneqCdrXZiWL6Ko8v/iln9vuN+2rK3rgWZPPRJBAsBN\na49L7U6lJjIGxIZtZqmK5h47oiUtwlYVrbZMN2ijuBQ22/eQ9tsFDV28oBuZ3WAR\npSSbj/tu
bPQYkw3YYOhv/VpEpsd0rkoEt3QCmTVcX2rtblanpXowTV5R0Hy4014n\nT49jrEo40r4mwYoyS835Uv4ENUFA+pXicT9eUot3RSH6rYdx4A/14UtoI9U0ol8M\n62GHpxSASQ2Kc3yQWvxRG
TFslTduYM+vVmMLEDDdqcsjYnStPpwdxxmKItmbjxSv\nIwYIndp8A04WkX2iiJCciC3BNxiLamPtYVyB1HHqbGTGirKYuSvwZt337q1OI3WH\nwVn2S4Mj/wqa4iCyGTvFSUnGq34Xkrb9XN
wWBok9Tc2XWGAU/mb/xcd1hX74GZbF\nsrZ11aPtym4kMAjU2KQi96GcAH2lnGZYoOja1J4Cs4WYx1uAx74H/m84CrYavVfl\n1ONJVLDfuZaEkSmu+jHQX15pAECNORTuLD06PbWnOEcOi1x
mbt/OT3SA3rhD2mb7\n2wxl7oJpV3ap8xGwYmxiFzmInxFJ1axjg8Rimol0mXTKAy6OdNHbCOnAwwIDAQAB\no2MwYTAPBgNVHRMBAf8EBTADAQH/MA4GA1UdDwEB/wQEAwIBBjAfBgNVHSME
GDAW\ngBQleng3lqGBeTrbLVuABoEmUHm1+TAdBgNVHQ4EFgQUJXp4N5ahgXk62y1bgAaB\nJlB5tfkwDQYJKoZIhvcNAQELBQADggIBADQ9jpmVh9nyY7ZQ4s+S9RuSRYn7QsrW\nDePeMzQ
gh8ZtS8WE65GY5HS61iHNP2Co8Q1lAaBWF4ipq+VZOcQbPLccHzd1kZv4\ns4u0aTzBd9ccidl73FS0DJDQOBbzPSzgsaiGHSMyGzkTeA8z3ntsSqrXXcDUvoRi\nFus/110AwdtNhJLrWveX
6btYtHp9Lqe0YtNCy5AaXlrr1yRSckP5BWVtlwD4dzSO\n/dqI3wHS/ncUx9wSQomZ+AmxYW3KtJQKgHzTqHru1x9BBk7Bzfz9FZr6HLLmEitj\nuFoDRd5TNt5LbO0zDQokvY3oqso6Htup/
rS7C08mcmnelYE+yXuOc1YrlyGnpBzk\nmy+1VYbOxRRdqKAZRbE72u/h847IVpsOvjR51iksuCAurZdp2+y2zvV8NhWekuNy\nirECRy9cb4YasjRaKi0/TCGPVSICuLyeG2W72liCj/N2VK
fjPP9zsOR5XjwCXfRg\n+9xhLy77/gov2NWXx5fzTkhxCrHOxFdLVMn0wQhksDmw6QsXzDIHSpIOypdDfnx9\nCsthx3nhkuHLUaEP22D22dG+vImA9ukj4R/RRI/87jmi9Q8+ehH+NqN0GZZ
cLjdN\nSLVXpncuwWQFUDPR06wNkkkmBSXWiIYhwqSpU0Pl3er3fD0uWvXuWPm2PzfOmUAE\nUrkzyw9XmLw0\n-----END CERTIFICATE-----\n'})

TASK [remote/ldap : Configure local-dex.tls] ****************************************************************************************************

Thursday 14 March 2024  01:12:25 +0000 (0:00:00.025)       1:22:04.154 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/ldap : Configure generic] **********************************************************************************************************

Thursday 14 March 2024  01:12:25 +0000 (0:00:00.019)       1:22:04.174 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/ldap : Configure wadcert] **********************************************************************************************************

Thursday 14 March 2024  01:12:25 +0000 (0:00:00.019)       1:22:04.193 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/ldap : Configure dex-overrides.yaml] ***********************************************************************************************

Thursday 14 March 2024  01:12:25 +0000 (0:00:00.019)       1:22:04.212 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/ldap : Wait for distributed cloud synchronization] *********************************************************************************

Thursday 14 March 2024  01:12:25 +0000 (0:00:00.021)       1:22:04.233 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/ldap : Remove temporary working directory] *****************************************************************************************

Thursday 14 March 2024  01:12:25 +0000 (0:00:00.020)       1:22:04.254 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/ldap : bringing in variables from the system controller] ***************************************************************************

Thursday 14 March 2024  01:12:25 +0000 (0:00:00.017)       1:22:04.272 ********
ok: [welktxef-931887-rh-le292s6-021]

TASK [remote/ldap : Copy SSL AD cert to server] *************************************************************************************************

Thursday 14 March 2024  01:12:25 +0000 (0:00:00.038)       1:22:04.311 ********
changed: [welktxef-931887-rh-le292s6-021] => (item={'filename': 'ad_ca.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIFpTCCA42gAwIBAgIUa3v
Z0YGxO1TQ8NwhiVfQC0JslXgwDQYJKoZIhvcNAQEL\nBQAwWjELMAkGA1UEBhMCVVMxEDAOBgNVBAoMB1Zlcml6b24xEzARBgNVBAsMClZa\nSUFNIFRlc3QxJDAiBgNVBAMMG1Zlcml6b24g
TmV0d29yayBSU0EgQ0EgVGVzdDAe\nFw0yMDA2MTUyMTAxMTNaFw0zNTA2MTUyMTAxMTNaMFoxCzAJBgNVBAYTAlVTMRAw\nDgYDVQQKDAdWZXJpem9uMRMwEQYDVQQLDApWWklBTSBUZXN0M
SQwIgYDVQQDDBtW\nZXJpem9uIE5ldHdvcmsgUlNBIENBIFRlc3QwggIiMA0GCSqGSIb3DQEBAQUAA4IC\nDwAwggIKAoICAQC8AIrksI57CbIl5uGZ6yqfpQj3aK+N8f1EVHdwK9JFskoipv
C8\n7yFTk8tgmO1i0YA5oRGfNxneqCdrXZiWL6Ko8v/iln9vuN+2rK3rgWZPPRJBAsBN\na49L7U6lJjIGxIZtZqmK5h47oiUtwlYVrbZMN2ijuBQ22/eQ9tsFDV28oBuZ3WAR\npSSbj/tub
PQYkw3YYOhv/VpEpsd0rkoEt3QCmTVcX2rtblanpXowTV5R0Hy4014n\nT49jrEo40r4mwYoyS835Uv4ENUFA+pXicT9eUot3RSH6rYdx4A/14UtoI9U0ol8M\n62GHpxSASQ2Kc3yQWvxRGT
FslTduYM+vVmMLEDDdqcsjYnStPpwdxxmKItmbjxSv\nIwYIndp8A04WkX2iiJCciC3BNxiLamPtYVyB1HHqbGTGirKYuSvwZt337q1OI3WH\nwVn2S4Mj/wqa4iCyGTvFSUnGq34Xkrb9XNw
WBok9Tc2XWGAU/mb/xcd1hX74GZbF\nsrZ11aPtym4kMAjU2KQi96GcAH2lnGZYoOja1J4Cs4WYx1uAx74H/m84CrYavVfl\n1ONJVLDfuZaEkSmu+jHQX15pAECNORTuLD06PbWnOEcOi1xm
bt/OT3SA3rhD2mb7\n2wxl7oJpV3ap8xGwYmxiFzmInxFJ1axjg8Rimol0mXTKAy6OdNHbCOnAwwIDAQAB\no2MwYTAPBgNVHRMBAf8EBTADAQH/MA4GA1UdDwEB/wQEAwIBBjAfBgNVHSMEG
DAW\ngBQleng3lqGBeTrbLVuABoEmUHm1+TAdBgNVHQ4EFgQUJXp4N5ahgXk62y1bgAaB\nJlB5tfkwDQYJKoZIhvcNAQELBQADggIBADQ9jpmVh9nyY7ZQ4s+S9RuSRYn7QsrW\nDePeMzQg
h8ZtS8WE65GY5HS61iHNP2Co8Q1lAaBWF4ipq+VZOcQbPLccHzd1kZv4\ns4u0aTzBd9ccidl73FS0DJDQOBbzPSzgsaiGHSMyGzkTeA8z3ntsSqrXXcDUvoRi\nFus/110AwdtNhJLrWveX6
btYtHp9Lqe0YtNCy5AaXlrr1yRSckP5BWVtlwD4dzSO\n/dqI3wHS/ncUx9wSQomZ+AmxYW3KtJQKgHzTqHru1x9BBk7Bzfz9FZr6HLLmEitj\nuFoDRd5TNt5LbO0zDQokvY3oqso6Htup/r
S7C08mcmnelYE+yXuOc1YrlyGnpBzk\nmy+1VYbOxRRdqKAZRbE72u/h847IVpsOvjR51iksuCAurZdp2+y2zvV8NhWekuNy\nirECRy9cb4YasjRaKi0/TCGPVSICuLyeG2W72liCj/N2VKf
jPP9zsOR5XjwCXfRg\n+9xhLy77/gov2NWXx5fzTkhxCrHOxFdLVMn0wQhksDmw6QsXzDIHSpIOypdDfnx9\nCsthx3nhkuHLUaEP22D22dG+vImA9ukj4R/RRI/87jmi9Q8+ehH+NqN0GZZc
LjdN\nSLVXpncuwWQFUDPR06wNkkkmBSXWiIYhwqSpU0Pl3er3fD0uWvXuWPm2PzfOmUAE\nUrkzyw9XmLw0\n-----END CERTIFICATE-----\n'})

TASK [remote/ldap : create oidc-auth-apps-certificate] ******************************************************************************************

Thursday 14 March 2024  01:12:27 +0000 (0:00:02.209)       1:22:06.520 ********
changed: [welktxef-931887-rh-le292s6-021]

TASK [remote/ldap : make sure oidc certificate is Ready before proceeding] **********************************************************************

Thursday 14 March 2024  01:12:29 +0000 (0:00:01.454)       1:22:07.975 ********
changed: [welktxef-931887-rh-le292s6-021]

TASK [remote/ldap : wait until system configuration is updated] *********************************************************************************

Thursday 14 March 2024  01:12:30 +0000 (0:00:01.262)       1:22:09.237 ********
changed: [welktxef-931887-rh-le292s6-021]

TASK [remote/ldap : create dex-ca-cert secret] **************************************************************************************************

Thursday 14 March 2024  01:12:35 +0000 (0:00:04.776)       1:22:14.014 ********
changed: [welktxef-931887-rh-le292s6-021]

TASK [remote/ldap : template overrides] *********************************************************************************************************

Thursday 14 March 2024  01:12:36 +0000 (0:00:01.337)       1:22:15.351 ********
changed: [welktxef-931887-rh-le292s6-021] => (item=stx-oidc-client.yaml)
changed: [welktxef-931887-rh-le292s6-021] => (item=dex-overrides-2212.yaml)
changed: [welktxef-931887-rh-le292s6-021] => (item=secret-observer-overrides.yaml)

TASK [remote/ldap : override oidc-client] *******************************************************************************************************

Thursday 14 March 2024  01:12:43 +0000 (0:00:06.743)       1:22:22.095 ********
changed: [welktxef-931887-rh-le292s6-021]

TASK [remote/ldap : create wad ca cert secret] **************************************************************************************************

Thursday 14 March 2024  01:12:48 +0000 (0:00:04.844)       1:22:26.939 ********
changed: [welktxef-931887-rh-le292s6-021]

TASK [remote/ldap : override dex] ***************************************************************************************************************

Thursday 14 March 2024  01:12:49 +0000 (0:00:01.310)       1:22:28.249 ********
changed: [welktxef-931887-rh-le292s6-021]

TASK [remote/ldap : override secret observer] ***************************************************************************************************

Thursday 14 March 2024  01:12:54 +0000 (0:00:04.980)       1:22:33.230 ********
changed: [welktxef-931887-rh-le292s6-021]

TASK [remote/ldap : Detect oidc-auth-apps application in applying state (from a previous attempt)] **********************************************

Thursday 14 March 2024  01:12:59 +0000 (0:00:05.107)       1:22:38.337 ********
changed: [welktxef-931887-rh-le292s6-021]

TASK [remote/ldap : Fail if oidc-auth-apps application-abort failed] ****************************************************************************

Thursday 14 March 2024  01:13:04 +0000 (0:00:04.620)       1:22:42.958 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/ldap : Detect oidc-auth-apps application in apply-failed or aborted state] *********************************************************

Thursday 14 March 2024  01:13:04 +0000 (0:00:00.017)       1:22:42.976 ********
changed: [welktxef-931887-rh-le292s6-021]

TASK [remote/ldap : Fail if oidc-auth-apps application apply failed] ****************************************************************************

Thursday 14 March 2024  01:13:09 +0000 (0:00:04.901)       1:22:47.877 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/ldap : Apply oidc-auth-apps application] *******************************************************************************************

Thursday 14 March 2024  01:13:09 +0000 (0:00:00.022)       1:22:47.899 ********
changed: [welktxef-931887-rh-le292s6-021]

TASK [remote/ldap : Detect applied status of oidc-auth-apps application] ************************************************************************

Thursday 14 March 2024  01:13:13 +0000 (0:00:04.610)       1:22:52.509 ********
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021]: Detect applied status of oidc-auth-apps application (60 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021]: Detect applied status of oidc-auth-apps application (59 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021]: Detect applied status of oidc-auth-apps application (58 retries left).
changed: [welktxef-931887-rh-le292s6-021]

TASK [remote/ldap : Fail if oidc-auth-apps application apply failed] ****************************************************************************

Thursday 14 March 2024  01:14:02 +0000 (0:00:49.248)       1:23:41.758 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [Remote Nvme] ******************************************************************************************************************************

Thursday 14 March 2024  01:14:02 +0000 (0:00:00.024)       1:23:41.782 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [Remote Metrics Server] ********************************************************************************************************************

Thursday 14 March 2024  01:14:03 +0000 (0:00:00.020)       1:23:41.803 ********

TASK [remote/metrics-server : Set facts - release independent] **********************************************************************************

Thursday 14 March 2024  01:14:03 +0000 (0:00:00.079)       1:23:41.882 ********
ok: [welktxef-931887-rh-le292s6-021]

TASK [remote/metrics-server : Set facts - 22.12] ************************************************************************************************

Thursday 14 March 2024  01:14:03 +0000 (0:00:00.016)       1:23:41.899 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/metrics-server : Set facts - 22.12] ************************************************************************************************

Thursday 14 March 2024  01:14:03 +0000 (0:00:00.017)       1:23:41.916 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/metrics-server : Set facts - 22.12] ************************************************************************************************

Thursday 14 March 2024  01:14:03 +0000 (0:00:00.018)       1:23:41.935 ********
ok: [welktxef-931887-rh-le292s6-021]

TASK [remote/metrics-server : Detect presence of existing application] **************************************************************************

Thursday 14 March 2024  01:14:03 +0000 (0:00:00.049)       1:23:41.984 ********
fatal: [welktxef-931887-rh-le292s6-021]: FAILED! => changed=true
  cmd: |-
    . /etc/platform/openrc
    system application-show metrics-server --column status --format value
  delta: '0:00:03.377915'
  end: '2024-03-14 01:14:07.628301'
  msg: non-zero return code
  rc: 1
  start: '2024-03-14 01:14:04.250386'
  stderr: 'application not found: metrics-server'
  stderr_lines: <omitted>
  stdout: ''
  stdout_lines: <omitted>
...ignoring

TASK [remote/metrics-server : Print message if system already has the appication] ***************************************************************

Thursday 14 March 2024  01:14:07 +0000 (0:00:04.585)       1:23:46.570 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/metrics-server : Apply again since the previous apply failed or in uploaded state] *************************************************

Thursday 14 March 2024  01:14:07 +0000 (0:00:00.018)       1:23:46.588 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/metrics-server : Wait until apply is in the applied or apply-failed state] *********************************************************

Thursday 14 March 2024  01:14:07 +0000 (0:00:00.017)       1:23:46.606 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/metrics-server : Print message if re-apply succeeds] *******************************************************************************

Thursday 14 March 2024  01:14:07 +0000 (0:00:00.016)       1:23:46.623 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/metrics-server : Print message if re-apply failed] *********************************************************************************

Thursday 14 March 2024  01:14:07 +0000 (0:00:00.020)       1:23:46.643 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/metrics-server : Noop if system requires no further action or needs manual investigation] ******************************************

Thursday 14 March 2024  01:14:07 +0000 (0:00:00.020)       1:23:46.664 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/metrics-server : Upload application] ***********************************************************************************************

Thursday 14 March 2024  01:14:07 +0000 (0:00:00.021)       1:23:46.685 ********
changed: [welktxef-931887-rh-le292s6-021]

TASK [remote/metrics-server : Wait until application is in the uploaded state] ******************************************************************

Thursday 14 March 2024  01:14:12 +0000 (0:00:04.668)       1:23:51.354 ********
changed: [welktxef-931887-rh-le292s6-021]

TASK [remote/metrics-server : Apply application] ************************************************************************************************

Thursday 14 March 2024  01:14:17 +0000 (0:00:04.891)       1:23:56.246 ********
changed: [welktxef-931887-rh-le292s6-021]

TASK [remote/metrics-server : Wait until application is in the applied or apply-failed state] ***************************************************

Thursday 14 March 2024  01:14:22 +0000 (0:00:04.828)       1:24:01.074 ********
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021]: Wait until application is in the applied or apply-failed state (90 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021]: Wait until application is in the applied or apply-failed state (89 retries left).
changed: [welktxef-931887-rh-le292s6-021]

TASK [remote/metrics-server : Apply again since the first apply failed] *************************************************************************

Thursday 14 March 2024  01:14:57 +0000 (0:00:35.048)       1:24:36.123 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/metrics-server : Wait again until apply is in the applied or apply-failed state] ***************************************************

Thursday 14 March 2024  01:14:57 +0000 (0:00:00.022)       1:24:36.145 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/metrics-server : Print message if apply is successful] *****************************************************************************

Thursday 14 March 2024  01:14:57 +0000 (0:00:00.020)       1:24:36.166 ********
ok: [welktxef-931887-rh-le292s6-021] =>
  msg:
  - =======================================================
  - ' welktxef-d931887-021: metrics-server install SUCCEEDED! '
  - =======================================================

TASK [remote/metrics-server : Print message if apply is failure] ********************************************************************************

Thursday 14 March 2024  01:14:57 +0000 (0:00:00.024)       1:24:36.190 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [Remote wrap-get-central-version] **********************************************************************************************************

Thursday 14 March 2024  01:14:57 +0000 (0:00:00.023)       1:24:36.214 ********

TASK [remote/wrap-get-central-version : Determine central WRA current version] ******************************************************************

Thursday 14 March 2024  01:14:57 +0000 (0:00:00.078)       1:24:36.292 ********
changed: [welktxef-931887-rh-le292s6-021 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)]

TASK [remote/wrap-get-central-version : Set facts for wra_target_version] ***********************************************************************

Thursday 14 March 2024  01:15:03 +0000 (0:00:05.851)       1:24:42.144 ********
ok: [welktxef-931887-rh-le292s6-021]

TASK [remote/wrap-get-central-version : debug] **************************************************************************************************

Thursday 14 March 2024  01:15:03 +0000 (0:00:00.019)       1:24:42.163 ********
ok: [welktxef-931887-rh-le292s6-021] =>
  msg: wra_target_version:23.09-0

TASK [Remote wrap-23.09-0] **********************************************************************************************************************

Thursday 14 March 2024  01:15:03 +0000 (0:00:00.022)       1:24:42.186 ********

TASK [remote/wrap-23.09-0 : Set facts for playbook] *********************************************************************************************

Thursday 14 March 2024  01:15:03 +0000 (0:00:00.125)       1:24:42.312 ********
ok: [welktxef-931887-rh-le292s6-021]

TASK [remote/wrap-23.09-0 : Noop if the system is NOT at the right caas_version] ****************************************************************

Thursday 14 March 2024  01:15:03 +0000 (0:00:00.015)       1:24:42.327 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/wrap-23.09-0 : Print message if system is NOT at the right caas_version] ***********************************************************

Thursday 14 March 2024  01:15:03 +0000 (0:00:00.015)       1:24:42.343 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/wrap-23.09-0 : Determine WRA current version and status] ***************************************************************************

Thursday 14 March 2024  01:15:03 +0000 (0:00:00.015)       1:24:42.359 ********
fatal: [welktxef-931887-rh-le292s6-021]: FAILED! => changed=true
  cmd: |-
    . /etc/platform/openrc
    system application-show wr-analytics --column app_version --column status --format value
  delta: '0:00:03.968139'
  end: '2024-03-14 01:15:09.041225'
  msg: non-zero return code
  rc: 1-(83%)
  start: '2024-03-14 01:15:05.073086'
  stderr: 'application not found: wr-analytics'
  stderr_lines: <omitted>
  stdout: ''
  stdout_lines: <omitted>
...ignoring

TASK [remote/wrap-23.09-0 : Set facts for current WRA version and status] ***********************************************************************

Thursday 14 March 2024  01:15:09 +0000 (0:00:05.628)       1:24:47.987 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/wrap-23.09-0 : debug] **************************************************************************************************************

Thursday 14 March 2024  01:15:09 +0000 (0:00:00.018)       1:24:48.005 ********
ok: [welktxef-931887-rh-le292s6-021] =>
  msg: 'wra_status:, wra_version:'

TASK [remote/wrap-23.09-0 : Determine if version is up-to-date] *********************************************************************************

Thursday 14 March 2024  01:15:09 +0000 (0:00:00.017)       1:24:48.023 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/wrap-23.09-0 : Noop because version is up-to-date] *********************************************************************************

Thursday 14 March 2024  01:15:09 +0000 (0:00:00.016)       1:24:48.039 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [Delete the existing WRA app] **************************************************************************************************************

Thursday 14 March 2024  01:15:09 +0000 (0:00:00.015)       1:24:48.054 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/wrap-23.09-0 : Delete app if just uploaded] ****************************************************************************************

Thursday 14 March 2024  01:15:09 +0000 (0:00:00.020)       1:24:48.075 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/wrap-23.09-0 : Set facts for central security file] ********************************************************************************

Thursday 14 March 2024  01:15:09 +0000 (0:00:00.021)       1:24:48.097 ********
ok: [welktxef-931887-rh-le292s6-021]

TASK [remote/wrap-23.09-0 : Set facts for working dir] ******************************************************************************************

Thursday 14 March 2024  01:15:09 +0000 (0:00:00.024)       1:24:48.121 ********
ok: [welktxef-931887-rh-le292s6-021]

TASK [remote/wrap-23.09-0 : Create working directory on host] ***********************************************************************************

Thursday 14 March 2024  01:15:09 +0000 (0:00:00.024)       1:24:48.145 ********
changed: [welktxef-931887-rh-le292s6-021]

TASK [remote/wrap-23.09-0 : Copy files to host] *************************************************************************************************

Thursday 14 March 2024  01:15:10 +0000 (0:00:01.221)       1:24:49.366 ********
changed: [welktxef-931887-rh-le292s6-021] => (item=wr-analytics-23.09-0.tgz)

TASK [remote/wrap-23.09-0 : Copy templates to host] *********************************************************************************************

Thursday 14 March 2024  01:15:12 +0000 (0:00:02.250)       1:24:51.617 ********
changed: [welktxef-931887-rh-le292s6-021] => (item=elastic-services-security-config.yaml)
changed: [welktxef-931887-rh-le292s6-021] => (item=logstash_sev_overrides-dropAll6.yaml)
changed: [welktxef-931887-rh-le292s6-021] => (item=logstash_samsung_vdu_parser.yaml)
changed: [welktxef-931887-rh-le292s6-021] => (item=helm-logstash_extra_envvars.yaml)
changed: [welktxef-931887-rh-le292s6-021] => (item=metricbeat-overrides.yaml)

TASK [remote/wrap-23.09-0 : Copy elastic security override from CC to Subcloud] *****************************************************************

Thursday 14 March 2024  01:15:24 +0000 (0:00:11.182)       1:25:02.800 ********
changed: [welktxef-931887-rh-le292s6-021 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)]

TASK [remote/wrap-23.09-0 : Upload wr-analytics application] ************************************************************************************

Thursday 14 March 2024  01:15:26 +0000 (0:00:02.515)       1:25:05.316 ********
changed: [welktxef-931887-rh-le292s6-021]

TASK [remote/wrap-23.09-0 : Wait until application is in the uploaded state] ********************************************************************

Thursday 14 March 2024  01:15:31 +0000 (0:00:05.042)       1:25:10.358 ********
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021]: Wait until application is in the uploaded state (30 retries left).
changed: [welktxef-931887-rh-le292s6-021]

TASK [remote/wrap-23.09-0 : Assign labels to nodes] *********************************************************************************************

Thursday 14 March 2024  01:15:51 +0000 (0:00:19.530)       1:25:29.888 ********
changed: [welktxef-931887-rh-le292s6-021]

TASK [remote/wrap-23.09-0 : Create monitor namesapce] *******************************************************************************************

Thursday 14 March 2024  01:15:56 +0000 (0:00:05.129)       1:25:35.018 ********
changed: [welktxef-931887-rh-le292s6-021]

TASK [remote/wrap-23.09-0 : Update Elastic overrides] *******************************************************************************************

Thursday 14 March 2024  01:15:58 +0000 (0:00:02.748)       1:25:37.767 ********
changed: [welktxef-931887-rh-le292s6-021]

TASK [remote/wrap-23.09-0 : Update Logstash overrides] ******************************************************************************************

Thursday 14 March 2024  01:16:04 +0000 (0:00:05.316)       1:25:43.083 ********
changed: [welktxef-931887-rh-le292s6-021]

TASK [remote/wrap-23.09-0 : Update Metricbeat overide] ******************************************************************************************

Thursday 14 March 2024  01:16:09 +0000 (0:00:04.831)       1:25:47.914 ********
changed: [welktxef-931887-rh-le292s6-021]

TASK [remote/wrap-23.09-0 : Apply wr-analytics application] *************************************************************************************

Thursday 14 March 2024  01:16:13 +0000 (0:00:04.827)       1:25:52.742 ********
changed: [welktxef-931887-rh-le292s6-021]

TASK [remote/wrap-23.09-0 : Wait until application is in the applied or apply-failed state] *****************************************************

Thursday 14 March 2024  01:16:18 +0000 (0:00:04.744)       1:25:57.487 ********
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021]: Wait until application is in the applied or apply-failed state (90 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021]: Wait until application is in the applied or apply-failed state (89 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021]: Wait until application is in the applied or apply-failed state (88 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021]: Wait until application is in the applied or apply-failed state (87 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021]: Wait until application is in the applied or apply-failed state (86 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021]: Wait until application is in the applied or apply-failed state (85 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021]: Wait until application is in the applied or apply-failed state (84 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021]: Wait until application is in the applied or apply-failed state (83 retries left).
FAILED - RETRYING: [welktxef-931887-rh-le292s6-021]: Wait until application is in the applied or apply-failed state (82 retries left).
changed: [welktxef-931887-rh-le292s6-021]

TASK [remote/wrap-23.09-0 : Print message if install succeeded] *********************************************************************************

Thursday 14 March 2024  01:21:40 +0000 (0:05:21.920)       1:31:19.407 ********
ok: [welktxef-931887-rh-le292s6-021] =>
  msg:--(89%)
  - ===================================================================
  - ' welktxef-d931887-021: WRA 23.09-0 install SUCCEEDED! '
  - ===================================================================

TASK [remote/wrap-23.09-0 : Print message if install failed] ************************************************************************************

Thursday 14 March 2024  01:21:40 +0000 (0:00:00.031)       1:31:19.438 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [Remote fpga-user-image] *******************************************************************************************************************

Thursday 14 March 2024  01:21:40 +0000 (0:00:00.027)       1:31:19.466 ********

TASK [include_role : remote/set-facts] **********************************************************************************************************

Thursday 14 March 2024  01:21:40 +0000 (0:00:00.135)       1:31:19.602 ********

TASK [remote/set-facts : Set facts for vip, ansible, and wr_admin] ******************************************************************************

Thursday 14 March 2024  01:21:40 +0000 (0:00:00.019)       1:31:19.621 ********
ok: [welktxef-931887-rh-le292s6-021]

TASK [remote/set-facts : Get central controller's software load version] ************************************************************************

Thursday 14 March 2024  01:21:40 +0000 (0:00:00.041)       1:31:19.662 ********
changed: [welktxef-931887-rh-le292s6-021 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)]

TASK [remote/set-facts : Set facts for wr_release_version] **************************************************************************************

Thursday 14 March 2024  01:21:46 +0000 (0:00:05.794)       1:31:25.457 ********
ok: [welktxef-931887-rh-le292s6-021]

TASK [remote/set-facts : Print wr_release_version] **********************************************************************************************

Thursday 14 March 2024  01:21:46 +0000 (0:00:00.021)       1:31:25.478 ********
ok: [welktxef-931887-rh-le292s6-021] =>
  msg: 'wr_release_version: 22.12'

TASK [remote/fpga-user-image : Set facts for default fpga_image_file] ***************************************************************************

Thursday 14 March 2024  01:21:46 +0000 (0:00:00.028)       1:31:25.507 ********
ok: [welktxef-931887-rh-le292s6-021]

TASK [remote/fpga-user-image : Set facts for fpga_image_file from host_vars] ********************************************************************

Thursday 14 March 2024  01:21:46 +0000 (0:00:00.026)       1:31:25.534 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/fpga-user-image : Print message if server is not LS3 cascadelake] ******************************************************************

Thursday 14 March 2024  01:21:46 +0000 (0:00:00.024)       1:31:25.558 ********
ok: [welktxef-931887-rh-le292s6-021] =>
  msg:
  - ==================================================================================
  - ' Server type ZTS-LS6-pts6 is not LS3 cascadelake, no action will take place! '
  - ==================================================================================

TASK [remote/fpga-user-image : Register noop because server is not LS3 cascadelake] *************************************************************

Thursday 14 March 2024  01:21:46 +0000 (0:00:00.019)       1:31:25.578 ********
changed: [welktxef-931887-rh-le292s6-021]

TASK [remote/fpga-user-image : Check if FPGA update is stuck] ***********************************************************************************

Thursday 14 March 2024  01:21:47 +0000 (0:00:01.196)       1:31:26.774 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/fpga-user-image : Abort FPGA update] ***********************************************************************************************

Thursday 14 March 2024  01:21:48 +0000 (0:00:00.022)       1:31:26.797 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/fpga-user-image : include_tasks] ***************************************************************************************************

Thursday 14 March 2024  01:21:48 +0000 (0:00:00.021)       1:31:26.819 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/fpga-user-image : Check FPGA update status (HPE-LS3-e910)] *************************************************************************

Thursday 14 March 2024  01:21:48 +0000 (0:00:00.020)       1:31:26.840 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/fpga-user-image : Check FPGA update status (ZTS-LS3-trtn)] *************************************************************************

Thursday 14 March 2024  01:21:48 +0000 (0:00:00.019)       1:31:26.859 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/fpga-user-image : Noop if the system has been updated] *****************************************************************************

Thursday 14 March 2024  01:21:48 +0000 (0:00:00.020)       1:31:26.880 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/fpga-user-image : Print message if the system has been updated] ********************************************************************

Thursday 14 March 2024  01:21:48 +0000 (0:00:00.019)       1:31:26.899 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/fpga-user-image : In main block] ***************************************************************************************************

Thursday 14 March 2024  01:21:48 +0000 (0:00:00.021)       1:31:26.921 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/fpga-user-image : Copy files to host] **********************************************************************************************

Thursday 14 March 2024  01:21:48 +0000 (0:00:00.020)       1:31:26.942 ********
skipping: [welktxef-931887-rh-le292s6-021] => (item=20ww43.5-1x2x25G-5GLDPC-v1.6.2-3.0.1-unsigned.bin)

TASK [remote/fpga-user-image : Do system device-image-upload] ***********************************************************************************

Thursday 14 March 2024  01:21:48 +0000 (0:00:00.021)       1:31:26.964 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/fpga-user-image : debug - print UUID] **********************************************************************************************

Thursday 14 March 2024  01:21:48 +0000 (0:00:00.018)       1:31:26.983 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/fpga-user-image : Do system device-image-apply] ************************************************************************************

Thursday 14 March 2024  01:21:48 +0000 (0:00:00.019)       1:31:27.003 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/fpga-user-image : Do system host-device-image-update] ******************************************************************************

Thursday 14 March 2024  01:21:48 +0000 (0:00:00.018)       1:31:27.022 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/fpga-user-image : Wait till application completed] *********************************************************************************

Thursday 14 March 2024  01:21:48 +0000 (0:00:00.018)       1:31:27.040 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/fpga-user-image : Do system device-image-state-list] *******************************************************************************

Thursday 14 March 2024  01:21:48 +0000 (0:00:00.018)       1:31:27.059 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/fpga-user-image : force an error if image state is not completed] ******************************************************************

Thursday 14 March 2024  01:21:48 +0000 (0:00:00.019)       1:31:27.079 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [remote/fpga-user-image : include_tasks] ***************************************************************************************************

Thursday 14 March 2024  01:21:48 +0000 (0:00:00.019)       1:31:27.099 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [Install DM Monitor] ***********************************************************************************************************************

Thursday 14 March 2024  01:21:48 +0000 (0:00:00.022)       1:31:27.121 ********

TASK [remote/dm-monitor : Install DM Monitor] ***************************************************************************************************

Thursday 14 March 2024  01:21:48 +0000 (0:00:00.099)       1:31:27.220 ********
changed: [welktxef-931887-rh-le292s6-021]

TASK [remote/dm-monitor : Wait for DM Monitor pod created] **************************************************************************************

Thursday 14 March 2024  01:22:26 +0000 (0:00:38.381)       1:32:05.602 ********
changed: [welktxef-931887-rh-le292s6-021]

TASK [remote/dm-monitor : Wait for control-plane pods become ready] *****************************************************************************

Thursday 14 March 2024  01:22:28 +0000 (0:00:01.286)       1:32:06.888 ********
changed: [welktxef-931887-rh-le292s6-021]

TASK [remote/dm-monitor : debug] ****************************************************************************************************************

Thursday 14 March 2024  01:22:29 +0000 (0:00:01.294)       1:32:08.183 ********
ok: [welktxef-931887-rh-le292s6-021] =>
  dm_monitor_pod_ready.stdout_lines:
  - pod/dm-monitor-7697bdfc6f-kv62q condition met

TASK [2212mr1 workarounds] **********************************************************************************************************************

Thursday 14 March 2024  01:22:29 +0000 (0:00:00.031)       1:32:08.214 ********
skipping: [welktxef-931887-rh-le292s6-021]

TASK [include_tasks] ****************************************************************************************************************************

Thursday 14 March 2024  01:22:29 +0000 (0:00:00.022)       1:32:08.237 ********
skipping: [welktxef-931887-rh-le292s6-021]

PLAY RECAP **************************************************************************************************************************************

welktxef-931887-rh-le292s6-021 : ok=146  changed=76   unreachable=0    failed=0    skipped=143  rescued=0
ignored=5

Thursday 14 March 2024  01:22:29 +0000 (0:00:00.025)       1:32:08.263 ********
===============================================================================
remote/remote-install : 4th polling: Wait for subcloud to install OS (this may still take a while) ------------------------------------ 2762.19s
remote/remote-install : 2nd polling: Wait for subcloud to install OS (this will take a while) ------------------------------------------ 880.38s
remote/manage : Wait for system to stabilize before running kubectl -------------------------------------------------------------------- 480.02s
remote/wrap-23.09-0 : Wait until application is in the applied or apply-failed state --------------------------------------------------- 321.92s
remote/reset_bmc : Wait for ZTS BMC to reset ------------------------------------------------------------------------------------------- 300.03s
remote/manage : Wait for system to stabilize ------------------------------------------------------------------------------------------- 300.02s
remote/ldap : Detect applied status of oidc-auth-apps application ----------------------------------------------------------------------- 49.25s
remote/starlingx : wait until system configuration is updated --------------------------------------------------------------------------- 39.74s
remote/dm-monitor : Install DM Monitor -------------------------------------------------------------------------------------------------- 38.38s
remote/metrics-server : Wait until application is in the applied or apply-failed state -------------------------------------------------- 35.05s
remote/remote-install : 1st polling: Wait for subcloud to start installing OS ----------------------------------------------------------- 31.07s
remote/wrap-23.09-0 : Wait until application is in the uploaded state ------------------------------------------------------------------- 19.53s
remote/set-facts : Get central controller's software load version ----------------------------------------------------------------------- 11.71s
remote/wrap-23.09-0 : Copy templates to host -------------------------------------------------------------------------------------------- 11.18s
remote/remote-configure : copy seed templates -------------------------------------------------------------------------------------------- 8.28s
remote/remote-install : Set subcloud system time by NTP server --------------------------------------------------------------------------- 7.36s
remote/ldap : template overrides --------------------------------------------------------------------------------------------------------- 6.74s
remote/remote-install : Deploy remote cloud ---------------------------------------------------------------------------------------------- 6.74s
remote/manage : Set distributed cloud state to managed ----------------------------------------------------------------------------------- 6.08s
remote/wrap-get-central-version : Determine central WRA current version ------------------------------------------------------------------ 5.85s
szabota@welktxefnce-h-pe1util-vm05:~/playbooks/wr-installer-atlas-me$

szabota@welktxefnce-h-pe1util-vm05:~/playbooks/wr-installer-atlas-me$ exit

Script done on 2024-03-14 18:26:43+00:00 [COMMAND_EXIT_CODE="0"]
(ansible_6.7) szabota@welktxefnce-h-pe1util-vm05:~/playbooks/wr-installer-atlas-me$
```

### After deployment information from the Controller

```log

[XXXXXX@controller-1 ~(keystone_admin)]$ system show
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
| updated_at             | 2024-03-06T14:48:58.942362+00:00     |
| uuid                   | bbf4823c-1b22-440a-83b3-55fe6679c36f |
| vswitch_type           | none                                 |
+------------------------+--------------------------------------+
[XXXXXX@controller-1 ~(keystone_admin)]$ sw-patch query
      Patch ID         RR  Release  Patch State
=====================  ==  =======  ===========
WRCP_22.12_PATCH_0001  Y    22.12    Committed
WRCP_22.12_PATCH_0002  Y    22.12    Committed
WRCP_22.12_PATCH_0003  Y    22.12    Committed
WRCP_22.12_PATCH_0004  Y    22.12    Committed

[XXXXXX@controller-1 ~(keystone_admin)]$ system application-list
+--------------------------+----------+-------------------------------------------+------------------+----------+-----------+
| application              | version  | manifest name                             | manifest file    | status   | progress  |
+--------------------------+----------+-------------------------------------------+------------------+----------+-----------+
| cert-manager             | 22.12-8  | cert-manager-fluxcd-manifests             | fluxcd-manifests | applied  | completed |
| nginx-ingress-controller | 22.12-1  | nginx-ingress-controller-fluxcd-manifests | fluxcd-manifests | applied  | completed |
| oidc-auth-apps           | 22.12-6  | oidc-auth-apps-fluxcd-manifests           | fluxcd-manifests | applied  | completed |
| platform-integ-apps      | 22.12-66 | platform-integ-apps-fluxcd-manifests      | fluxcd-manifests | uploaded | completed |
| wr-analytics             | 23.09-0  | wr-analytics-fluxcd-manifests             | fluxcd-manifests | applied  | completed |
+--------------------------+----------+-------------------------------------------+------------------+----------+-----------+
[XXXXXX@controller-1 ~(keystone_admin)]$ dcmanager subcloud list
+----+----------------------+------------+--------------+---------------+---------+---------------+-----------------+
| id | name                 | management | availability | deploy status | sync    | backup status | backup datetime |
+----+----------------------+------------+--------------+---------------+---------+---------------+-----------------+
| 17 | welktxef-d931881-005 | managed    | online       | complete      | in-sync | None          | None            |
| 18 | welktxef-d931884-034 | managed    | online       | complete      | in-sync | None          | None            |
| 20 | welktxef-d931855-003 | managed    | online       | complete      | in-sync | None          | None            |
| 22 | welktxef-d931887-021 | managed    | online       | complete      | in-sync | None          | None            |
+----+----------------------+------------+--------------+---------------+---------+---------------+-----------------+
[XXXXXX@controller-1 ~(keystone_admin)]$ dcmanager subcloud list welktxef-d931887-021
usage: dcmanager subcloud list [-h] [-f {csv,json,table,value,yaml}] [-c COLUMN] [--quote {all,minimal,none,nonnumeric}] [--noindent]
                               [--max-width <integer>] [--fit-width] [--print-empty] [--sort-column SORT_COLUMN]
dcmanager subcloud list: error: unrecognized arguments: welktxef-d931887-021
[XXXXXX@controller-1 ~(keystone_admin)]$ dcmanager subcloud list welktxef-d9^C887-021
[XXXXXX@controller-1 ~(keystone_admin)]$ dcmanager subcloud show welktxef-d931887-021
+-----------------------------+---------------------------------+
| Field                       | Value                           |
+-----------------------------+---------------------------------+
| id                          | 22                              |
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
| created_at                  | 2024-03-13 23:56:00.426125      |
| updated_at                  | 2024-03-14 01:06:21.226509      |
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
[XXXXXX@controller-1 ~(keystone_admin)]$

```

### Subcloud deployment had no isue, marking test as a pass
