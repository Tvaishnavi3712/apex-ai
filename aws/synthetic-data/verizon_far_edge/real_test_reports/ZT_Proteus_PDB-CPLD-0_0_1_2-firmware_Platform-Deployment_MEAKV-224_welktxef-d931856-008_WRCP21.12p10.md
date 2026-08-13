# ZT Proteus PDB-CPLD 0.0.1.2 Firmware Validation
# ZT Proteus .46 BMC / BIOS .30
# 1/16/24 James Patchett
# Platform-Deployment MEAKV-224 WRCP21.12p10 Deployment


## Right side Subcloud welktxef-d931856-008
## BMC 0.46 BIOS 0.23
BMC:  2607:f160:10:80b1:ce:40a:0:e008
OAM:  2607:f160:10:80b1:ce:40a:0:f408

## Subcloud welktxef-d931856-008 Info
```log

====================================================================
         SYSTEM: welktxef-d931856-008
====================================================================

controller-0:~$ system show
You must provide a username via either --os-username or via env[OS_USERNAME]
controller-0:~$ source /etc/platform/openrc
[XXXXXX@controller-0 ~(keystone_admin)]$ system show
+------------------------+--------------------------------------+
| Property               | Value                                |
+------------------------+--------------------------------------+
| contact                | None                                 |
| created_at             | 2024-03-14T20:24:31.593270+00:00     |
| description            | None                                 |
| distributed_cloud_role | subcloud                             |
| https_enabled          | True                                 |
| latitude               | None                                 |
| location               | None                                 |
| longitude              | None                                 |
| name                   | welktxef-d931856-008                 |
| region_name            | welktxef-d931856-008                 |
| sdn_enabled            | False                                |
| security_feature       | spectre_meltdown_v1                  |
| service_project_name   | services                             |
| shared_services        | []                                   |
| software_version       | 21.12                                |
| system_mode            | simplex                              |
| system_type            | All-in-one                           |
| timezone               | UTC                                  |
| updated_at             | 2024-03-14T21:10:40.703304+00:00     |
| uuid                   | 513ef33a-4291-466f-ae6e-5ddaee2bf34d |
| vswitch_type           | none                                 |
+------------------------+--------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ system oam-show
+----------------+---------------------------------------+
| Property       | Value                                 |
+----------------+---------------------------------------+
| created_at     | 2024-03-14T20:26:13.069396+00:00      |
| isystem_uuid   | 513ef33a-4291-466f-ae6e-5ddaee2bf34d  |
| oam_end_ip     | 2607:f160:10:80b1:ffff:ffff:ffff:fffe |
| oam_gateway_ip | 2607:f160:10:80b1:ce:23::             |
| oam_ip         | 2607:f160:10:80b1:ce:40a:0:f408       |
| oam_start_ip   | 2607:f160:10:80b1::1                  |
| oam_subnet     | 2607:f160:10:80b1::/64                |
| updated_at     | None                                  |
| uuid           | 0f8d3ffe-8906-4288-bc8b-5d25696dbba4  |
+----------------+---------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ 
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

[XXXXXX@controller-0 ~(keystone_admin)]$
```



### MEAKV-224
### Ansible install script

```log
[XXXXXX@welktxefnce-h-pe1util-vm01 wr-installer]$ ansible-playbook --vault-passwor
d-file ./vault_pass -i inventory/welktxef-931856-rz-le2pts6-008.yaml wr_remote.yaml


PLAY [Wind River Remote Subcloud Installer] ************************************************************
*****************************************

TASK [Download Files] **********************************************************************************
*****************************************

TASK [common/download_files : Check if artifact files exist locally] ***********************************
*****************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [common/download_files : Download & unarchive artifact files to local directory if they don't exist
] ***************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [Setup] *******************************************************************************************
*****************************************

TASK [common/setup : Create temporary working directory] ***********************************************
*****************************************
changed: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [common/setup : Set temporary working directory path] *********************************************
*****************************************
ok: [welktxef-931856-rz-le2pts6-008]

TASK [Remote Configure] ********************************************************************************
*****************************************

TASK [remote/remote-configure : Set facts for vip, ansible, and wr_admin] ******************************
*****************************************
ok: [welktxef-931856-rz-le2pts6-008]

TASK [remote/remote-configure : Set facts for wr_release_version] **************************************
*****************************************
ok: [welktxef-931856-rz-le2pts6-008]

TASK [remote/remote-configure : Print wr_release_version] **********************************************
*****************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "msg": "wr_release_version: 21.12"
}

TASK [remote/remote-configure : Set fact wr_distribution_directory to use based on WR version] *********
*****************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/remote-configure : Set fact wr_distribution_directory to use based on WR version] *********
*****************************************
ok: [welktxef-931856-rz-le2pts6-008]

TASK [remote/remote-configure : Set facts for which image list to use based on WR version] *************
*****************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/remote-configure : Set facts for which image list to use based on WR version] *************
*****************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/remote-configure : Set facts for which image list to use based on WR version] *************
*****************************************
ok: [welktxef-931856-rz-le2pts6-008]

TASK [remote/remote-configure : Print wr_image_list] ***************************************************
*****************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "msg": "wr_image_list: /opt/external/vcpfe-team/artifacts/WRCP-2112/wind-river-cloud-platform-
container-images-list-21.12.txt"
}

TASK [remote/remote-configure : Set fact to wr_license_key] ********************************************
*****************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/remote-configure : Set fact to wr_license_key] ********************************************
*****************************************
ok: [welktxef-931856-rz-le2pts6-008]

TASK [remote/remote-configure : print wr_license_key] **************************************************
*****************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "msg": "wr_license_key = IyBXaW5kIFJpdmVyIFByb2R1Y3QgQWN0aXZhdGlvbiBGaWxlIChpbnN0YWxsLnR4dCkKI
yBJc3N1ZWQgZm9yIGhvc3Q6IDxWZXJpem9uPiA8VmVyaXpvbj4gPEFueT4KIyBMaWNlbnNlIG51bWJlcihzKTogNjgyMzc0CiMgSXNzd
WVkIG9uOiAyNi1qYW4tMjAyMiAwOTo1MDo1MAojCiMgTm90ZTogdGhpcyBsaWNlbnNlIGlzIGdlbmVyYXRlZCBjdW11bGF0aXZlbHkgZ
m9yIGFsbAojIFdpbmQgUml2ZXIgc29mdHdhcmUgbWFuYWdlZCBieSB0aGlzIGhvc3QuCgojIDEuIEZsZXhMTSBsaWNlbnNlIGZpbGU6C
iMgQmVnaW46IFNlcnZlciBsaWNlbnNlICAtLS0tLS0tLS0tLS0tLS0tLS0tLS0KIyBTZXJpYWwgTnVtYmVyOiA2ODQ0NDktVmVyaXpvb
lBPQy1HNFdEQzlDUEVLCgpQQUNLQUdFIFdSQ1BfQ09OVEFJTkVSX1BLRyB3cnNkIDIxIDAwNDY1REZDRUI5QiBcCglDT01QT05FTlRTP
VdSQ1BfQ09OVEFJTkVSOjIxLjEyIE9QVElPTlM9U1VJVEUgXAoJU0lHTj0yNTAwQzhCMjRFRDAKSU5DUkVNRU5UIFdSQ1BfQ09OVEFJT
kVSX1BLRyB3cnNkIDIxIHBlcm1hbmVudCB1bmNvdW50ZWQgNDQyRThBMzg2QUE4IFwKCVZFTkRPUl9TVFJJTkc9PGxuPjY4MjM3NDwvb
G4+PHBzPjIyMTMtNDM8L3BzPiBIT1NUSUQ9QU5ZIFwKCUlTU1VFRD0yNi1qYW4tMjAyMiBTTj1zZXJpYWwtVmVyaXpvbi1MVjJJV0FVT
EVCIFwKCVNUQVJUPTI2LWphbi0yMDIyIFNJR049QjUzNzk2OTBENEE2Cg=="
}

TASK [remote/remote-configure : Copy storage checking script if server is HPE-LS3-e910] ****************
*****************************************
skipping: [welktxef-931856-rz-le2pts6-008] => (item=hpe_storage_check.py)

TASK [remote/remote-configure : Execute storage checking script if server is HPE-LS3-e910] *************
*****************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor HPE HPE-LS3-e910
(4 disks)] ******************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor HPE HPE-LS3-e910
(2 disks)] ******************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor HPE HPE-LS3-92s3]
 ****************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor HPE HPE-LS6-92s6]
 ****************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor ZTS ZTS-LS3-trtn]
 ****************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/remote-configure : Set facts for Corning] *************************************************
*****************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor ZTS ZTS-LS6-pts6
& ZTS-LS3-pts3] *************************
ok: [welktxef-931856-rz-le2pts6-008]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor ZTS ZTS-LS6-aks6
& ZTS-LS3-aks3] *************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/remote-configure : set_fact] **************************************************************
*****************************************
ok: [welktxef-931856-rz-le2pts6-008]

TASK [include_role : remote/zt-redfish] ****************************************************************
*****************************************

TASK [remote/zt-redfish : get content from /redfish/v1/Systems/Self] ***********************************
*****************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/zt-redfish : Extract and store BiosVersion from returned content] *************************
*****************************************
ok: [welktxef-931856-rz-le2pts6-008]

TASK [remote/remote-configure : Set facts for BIOS version based on vendor ZTS ZTS-LS6-pts6 & ZTS-LS3-pt
s3] *************************************
ok: [welktxef-931856-rz-le2pts6-008]

TASK [remote/remote-configure : debug] *****************************************************************
*****************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "bios_version": "0.23"
}

TASK [remote/remote-configure : Find out which DM Docker version contral has] **************************
*****************************************
changed: [welktxef-931856-rz-le2pts6-008 -> rchltxib-c000000-003]

TASK [remote/remote-configure : Find out which DM file version contral has] ****************************
*****************************************
changed: [welktxef-931856-rz-le2pts6-008 -> rchltxib-c000000-003]

TASK [remote/remote-configure : Print dm docker version and dm file version] ***************************
*****************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "msg": "dm_docker_version: WRCP_21.12-wrs.4, dm_file: wind-river-cloud-platform-deployment-man
ager-2.0.8-4.tgz"
}

TASK [remote/remote-configure : Discover Wind River docker image names] ********************************
*****************************************
changed: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/remote-configure : Print local_images_full] ***********************************************
*****************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "msg": "docker.io/starlingx/ceph-config-helper:v1.15.0\ndocker.io/starlingx/dex:stx.4.0-v2.14.
0-1\ndocker.io/starlingx/n3000-opae:stx.6.0-v1.0.1\ndocker.io/starlingx/stx-oidc-client:stx.5.0-v1.0.4\n
docker.io/wind-river/cloud-platform-deployment-manager:WRCP_21.12-wrs.4\ngcr.io/google_containers/kubern
etes-dashboard-init-amd64:v1.0.0\ngcr.io/kubebuilder/kube-rbac-proxy:v0.4.0\nquay.io/external_storage/rb
d-provisioner:v2.1.1-k8s1.11"
}

TASK [remote/remote-configure : Create fact for Wind River docker image names] *************************
*****************************************
ok: [welktxef-931856-rz-le2pts6-008]

TASK [remote/remote-configure : Determine DM Helm Chart path] ******************************************
*****************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/remote-configure : Print dm_helm_chart] ***************************************************
*****************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "msg": "/opt/external/vcpfe-team/artifacts/WRCP-2112/wind-river-cloud-platform-deployment-mana
ger-2.0.8-4.tgz"
}

TASK [remote/remote-configure : Set DM Helm Chart file] ************************************************
*****************************************
ok: [welktxef-931856-rz-le2pts6-008]

TASK [remote/remote-configure : Lookup Deployment Manager image tag] ***********************************
*****************************************
changed: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/remote-configure : Lookup RBAC Proxy image tag] *******************************************
*****************************************
changed: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/remote-configure : Copy WRCP DM Playbook] *************************************************
*****************************************
ok: [welktxef-931856-rz-le2pts6-008 -> rchltxib-c000000-003] => (item=wind-river-cloud-platform-de
ployment-manager.yaml)
ok: [welktxef-931856-rz-le2pts6-008 -> rchltxib-c000000-003] => (item=wind-river-cloud-platform-de
ployment-manager-2.0.8-4.tgz)

TASK [remote/remote-configure : Set a fact for the central controller VIP address] *********************
*****************************************
ok: [welktxef-931856-rz-le2pts6-008]

TASK [remote/remote-configure : Configure WRCP seed template] ******************************************
*****************************************
ok: [welktxef-931856-rz-le2pts6-008 -> rchltxib-c000000-003] => (item={'src': 'bootstrap-values.ya
ml', 'dest': 'welktxef-d931856-008-bootstrap-values.yaml'})
ok: [welktxef-931856-rz-le2pts6-008 -> rchltxib-c000000-003] => (item={'src': 'deploy-values.yaml'
, 'dest': 'welktxef-d931856-008-deploy-values.yaml'})
ok: [welktxef-931856-rz-le2pts6-008 -> rchltxib-c000000-003] => (item={'src': 'deploy-standard.yam
l', 'dest': 'welktxef-d931856-008-deploy-standard.yaml'})
ok: [welktxef-931856-rz-le2pts6-008 -> rchltxib-c000000-003] => (item={'src': 'install-values.yaml
', 'dest': 'welktxef-d931856-008-install-values.yaml'})

TASK [remote/remote-configure : Copy SSL cert files] ***************************************************
*****************************************
ok: [welktxef-931856-rz-le2pts6-008 -> rchltxib-c000000-003] => (item={'filename': 'k8s_root_ca_ce
rt.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIF8jCCA9qgAwIBAgIJAIf9Ql2uDZh+MA0GCSqGSIb3DQEBDQUAMIGF
MQswCQYD\nVQQGEwJVUzEOMAwGA1UECAwFVGV4YXMxETAPBgNVBAcMCFdlc3RsYWtlMR0wGwYD\nVQQKDBRWZXJpem9uIFNvdXJjaW5n
IExMQzE0MDIGA1UEAwwrVmVyaXpvbiBOZXR3\nb3JrIFdFTEtUWElCIExBQiAxIDMgUlNBIEs4UyBDQTAeFw0yMDEwMjUyMjEyNDha\n
Fw0zMDEwMjMyMjEyNDhaMIGFMQswCQYDVQQGEwJVUzEOMAwGA1UECAwFVGV4YXMx\nETAPBgNVBAcMCFdlc3RsYWtlMR0wGwYDVQQKDB
RWZXJpem9uIFNvdXJjaW5nIExM\nQzE0MDIGA1UEAwwrVmVyaXpvbiBOZXR3b3JrIFdFTEtUWElCIExBQiAxIDMgUlNB\nIEs4UyBDQT
CCAiIwDQYJKoZIhvcNAQEBBQADggIPADCCAgoCggIBAKyF9svdv/qG\n7HxBr1DWvZ3CQiDsA4m1kj0hD7jo3B3W/32ODcPpgeNmp4Of
ul0SsndpqEGhXDq5\noiBfqszMUpzDgdQ7siIHekb2olFEK2KniMP3H53nilIppeyMby5K3ZwF0Qbmk5WK\ncoXoYegP+Uv9bV0AMH6D
n4CVgYrLAYfmPyGgUSt4vuZ9F/rf9UkBf/DcZGqMnMax\n/Gfaq8KwmDzD9D8IVCHPrM5f4+CaKMQCFu5QkSsLYJFRiuQWWaICMMdnqp
b0HZh5\niPnCSHwPPUyXxtujdI97Ovy4X5WR46jJ2+KzPYe8tVa/DL3TlKmRL9AF+oSE17bw\nzGAE7GNWxPojebHIUuoKdOQC1qiJBV
S+c14r9+9P2Uy6XEhNUs+h3juRI4U3YkQ1\nUCUU3opqhOPh4jUIuPGg5aX07lt4Wpxc48D+CY1D4i6vaJLl3WCsVK7PFwWVQQEW\nIQ
abfuj1R2jEu7pp2Yabza58S00v1P5/kv/DNr7ADm8eYRvxLAAXCedMeSDXKBgd\npPmVXXZoZ8+X8VRGYxcw0mBBLIAiTOntT2vgLeq5
T3QyiVKdU6TLAYEjS65QZ3Eg\naIX0wRqlcQI7lruTXubtENG6wWXYtnDf5795ZID1YIEqkgzZLMBqq1SBiLnWd6aK\n78Zsr4j5GmTB
GpKRmwE2oO1btJCCYyG5AgMBAAGjYzBhMA8GA1UdEwEB/wQFMAMB\nAf8wHQYDVR0OBBYEFEDQ5EaGp3x02WUuvqetygqpM3dCMB8GA1
UdIwQYMBaAFEDQ\n5EaGp3x02WUuvqetygqpM3dCMA4GA1UdDwEB/wQEAwICpDANBgkqhkiG9w0BAQ0F\nAAOCAgEAeCMxVJr5Jyg87D
VaUtEhiWfhto993ENrnevAGqrBOoRc/KU1/C3paqhR\nsvr2r2LR+npSmeo6iz0FaO31XwHSHX95+XJeGP5Q8TGddbRiTglQsMfOkGNz
xqgg\nTkdZ8A1y9v2jprONUmLADVGIVT0AoHc7V9w1I8NKhrY+rIllum4FRDiDPSnImh5h\nxmH+Nq2ZuEFVdtV/oNKzEu2ywmbgBRd5
Jv3rTejxltmTZtyq8IKoKguj3NVFn93Q\nU4TbsxkcAdrLMooLYYDRTWA4t0iqKM/UkYUg4xl2l9NrY7ZUbaNd5+YsLNdqXO/c\nmp7w
yMv/8ZIy1BLG4zJmX/JzWkYmULqQ+A+21+YuqrV3a81V7vcHhJcRaPOrg5cd\nYwY2eCbXMvNOdrzppIglUrlddNuqAhs1MTi/VibxYu
I9isU0JckXIcCy1L+xbEda\n6v/z6wSrScVz0I4m0DpK6xMQ8t9sLcrGp5uGbj6J4nQWd+QLdq6kmAzDOZ/Gs0wb\nPYdkER4dXAVcio
YFekpKv7d+nur0FPtMNIw0OdhX2eAwC22IFAq2DZRjUFvaBGaD\ni1ptfq6P1mVJ2T/exYujEDtq+8yQTfWgFm/DjEfWtcCp0Jukgv8o
pLR2DpCf5Ucq\nd5X7d/DP0mukJ3vZ8EIqYorwZJ1L1a2jgngjA+gPxIaW+JHfTHU=\n-----END CERTIFICATE-----\n'})
ok: [welktxef-931856-rz-le2pts6-008 -> rchltxib-c000000-003] => (item={'filename': 'k8s_root_ca_ke
y.pem', 'value': '-----BEGIN PRIVATE KEY-----\nMIIJQQIBADANBgkqhkiG9w0BAQEFAASCCSswggknAgEAAoICAQCshfbL3
b/6hux8\nQa9Q1r2dwkIg7AOJtZI9IQ+46Nwd1v99jg3D6YHjZqeDn7pdErJ3aahBoVw6uaIg\nX6rMzFKcw4HUO7IiB3pG9qJRRCtip
4jD9x+d54pSKaXsjG8uSt2cBdEG5pOVinKF\n6GHoD/lL/W1dADB+g5+AlYGKywGH5j8hoFEreL7mfRf63/VJAX/w3GRqjJzGsfxn\n2
qvCsJg8w/Q/CFQhz6zOX+PgmijEAhbuUJErC2CRUYrkFlmiAjDHZ6qW9B2YeYj5\nwkh8Dz1Ml8bbo3SPezr8uF+VkeOoydvisz2HvLV
Wvwy905SpkS/QBfqEhNe28Mxg\nBOxjVsT6I3mxyFLqCnTkAtaoiQVUvnNeK/fvT9lMulxITVLPod47kSOFN2JENVAl\nFN6KaoTj4eI
1CLjxoOWl9O5beFqcXOPA/gmNQ+Iur2iS5d1grFSuzxcFlUEBFiEG\nm37o9UdoxLu6admGm82ufEtNL9T+f5L/wza+wA5vHmEb8SwAF
wnnTHkg1ygYHaT5\nlV12aGfPl/FURmMXMNJgQSyAIkzp7U9r4C3quU90MolSnVOkywGBI0uuUGdxIGiF\n9MEapXECO5a7k17m7RDRu
sFl2LZw3+e/eWSA9WCBKpIM2SzAaqtUgYi51nemiu/G\nbK+I+RpkwRqSkZsBNqDtW7SQgmMhuQIDAQABAoICACysO62qa+2pRk8eixD
5qfvR\ns2Hm+zuLYqSljPaqhWTMqTePswzJyDJkAHhawd0b3E6Dc2gbKlCihNKxMv744WNq\nVJHqK0QYf5ckgf9dEYboLsffk7ZFoFG
KK0bHTnrENAIUl32b8xdD1EfMVp3KlRkS\nNGFijSwVVRXsoLCZxHm2Kx6/7oS9LWFtfuodV9xhoQlzaCUW5/mjWOJjgxpUs/b4\nHqS
7uV1P80U1G0KraGboy5tGDXEB7y1x2e8Zwnfq7UqVE10nNQqoXcmefzpwj8Tn\ngDybZLFKjYmnDEkkj7jDHEbldsdRG/usWNZGlTYbP
DA3fBkYdOsQCzvJypQmgbZ+\n3yk3Lj2+9vLEMfPrruuzyOSXgki6o5uvy7Je6PdBpsz75k8FH6a+Rw3vvP8HuP3S\nLSUYm3tyOheXH
R7BKN4bnfi11RAWvDpT9S+QnZ+R8DmQzOADlnjRC8WewDJYoNJ1\np1jeuqswlxo144oMO92cmdS2dAbPvS6aQP1I85Q2NniY+6YhHkB
wIQIlfVs1JPbY\nX7QtTy1IXQhR3sospyvUwY2GPSAeVHDRL53ClQKDsvWpSy0MAmWYJkZu1P+jKBim\nj34ytApgG65Hv/RHf3L4+4z
zItZ3TN2tJ/g9EKc6oMNtqKbbG56kkmvRPWKtMGV8\nFqxCvG5NydUK7fN+P2WJAoIBAQDXLFC//Fn9ed1U+pKa2M25aJwEetkGLXQvk
wVi\n8uJFaXITb2ceveSEo6iBExyn4eYL5A4X+RZdJJdRRbj4whsNN13Pm+6lYX3pp7MN\nO+78uvwVfKZiWPFKfZs7ZH1/O9VIlLGnX
UHeaHK1tmv9ixxMixdnjUDkcVa0O3qT\nKBLpvXnVEMYizxQBN0P5Z9QvQQGpUhKnNw+FhV1SP+YHxrB0Pu6qbYAmZZC2MQc1\nTsDyq
GjmHk9VJaFYAAPEjqACDbfnkVUCj0ylM4xPQuBJs9DOKh4InG+znusdmd8H\nmvoEFDppsrH1NhO6GTeuCk6n0WBi6cUm76K/gPscYyV
4ZtkfAoIBAQDNQgDXtfqv\nxbAhvDk0o/P8fqOdgQF0uFTqYHmyW31Ty9nF0ptA8LVJOIljU3zlLplhIFjBnSEG\nLqu4jnLLRR+zej0
MXmJuZ9BMWmQeTrZzttnH5bn54E07DPJ5BvFoTMJNklBiXjB5\n5hTPZS4yK1KjoxY+Ypnj4W1iZjP37ya/A34J2nlYtoW4LdVfJHqCx
BXel9Nz2zkv\nvwwPu8Eu7gFLuhNQM6Iv4mORGI8yg7Y/BwodfDPRuFvrG1KXkjwASb0O5b1suRQy\n9H80q5EAbT36K1z48ilr8fcro
N+hV8g4yntrBBgOHPMmBk/vHKU8B1rkBr0p2haI\n3PwKmDFRsDInAoIBAGrjjMmSZnHQk+6e+y0I/klYegiPrjevZMQtWMOqvFSW6SB
W\nevd+hYKOeiqEf/u18D1/8LBgAIgMoU6yQAzy/9U059k2MPrez1m/AOdWGoZZrNhP\nr6ezX0oN04tRhDYsVutTUl09qnb9k95I3KR
68nfjsKC0PsQ8uUGXOnDXu215vofl\naUfpbpqcBZxjw7glptmh97oxU/iUI6O0MmUygn18tbrb4okwcw7OlDIbCSaCGnoW\nHHrD0r6
QY07FOx9KCU1zmLNI1F5MmSrWoex68wM3UOweKi8khs+RnIV+qyxTkCDp\nsBWL44jS9iHy5Nfg3uzEDDgnWsWfIR8c8YQ6MykCggEAD
r0ollTI9Yo6hZGggfkr\n8fueABddZWY/Ir1ev8H2E+hVcPEYmOcv/VwD8Y/zLfnUpbbO6MhBsNH1HsGL2LDT\n/+1NKPA2HTtzJ6ht/
Acm7tQ4ezQx0JGcuhrJ5orrFtQ8N5nED+w3iulMoT/gu1WF\nD58MX9pwtn5ffmtcW/deTuUPTeHUSNyCaaFQ6w4RhgZSk7NPSch6KMW
NNiwDST1p\n9mgcLuwmP04AXFDpJ3VxxsDYpxleFzcn0pAZtCyaBmNFIia5HW+E1cvcvol7Vg6C\nHs6yVGX/N3MejpF0vX8yL3HKvvq
CR7EofJiDcOYbr13P1wPs3W59o8JKjvAyymze\njQKCAQAUY/0asRL33D7tFoIbLg/N9hi+tCCM35DMf2FeXm3QwSkAR/BJw0ewCE5C\
n+VqukHN3/i0Xe8KSHwEuLK2sGLk9Ys8A5NytjqFApYwpIk8UrRONfC12H3ez5VYk\nJlhMVhVXEZvVhEFJiBC7q6x6s7BVtLTGV7FA5
CW8YKBhwHwrpm+h/Xb798oaKyel\nP/xYq+GZzfWfbvUjZvgN0J0RGxKA+GRgsmhoyOfgCVXgSzuUkI+9cAUvC0OV407L\n4XIK0GDJ7
Tv/2USSPfmueyGEmacc/oYUPVBUgeINSoaCM4cpZwyLylVEtKOdQoEE\n77G5mvQsoXxsMjd+nbHil450UHsL\n-----END PRIVATE
KEY-----\n'})

TASK [Proteus MWIAT - ENABLE] **************************************************************************
*****************************************

TASK [remote/zt-redfish : Update Attributes at /redfish/v1/Systems/Self/Bios/SD] ***********************
*****************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/zt-redfish : Update result] ***************************************************************
*****************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "update_result": {
        "allow": "GET, PUT, PATCH, POST",
        "changed": false,
        "connection": "close",
        "content": "",
        "cookies": {},
        "cookies_string": "",
        "date": "Thu, 14 Mar 2024 19:55:05 GMT",
        "elapsed": 0,
        "failed": false,
        "msg": "OK (unknown bytes)",
        "redirected": false,
        "server": "AMI MegaRAC Redfish Service",
        "status": 204,
        "url": "https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/Systems/Self/Bios/SD"
    }
}

TASK [Remote Install] **********************************************************************************
*****************************************

TASK [remote/remote-install : Check if the subcloud deployed but failed] *******************************
*****************************************
fatal: [welktxef-931856-rz-le2pts6-008 -> rchltxib-c000000-003]: FAILED! => {"changed": true, "cmd
": ". /etc/platform/openrc\ndcmanager subcloud show welktxef-d931856-008 --column \"deploy_status\" --fo
rmat value\n", "delta": "0:00:01.192361", "end": "2024-03-14 19:55:08.434606", "msg": "non-zero return c
ode", "rc": 1, "start": "2024-03-14 19:55:07.242245", "stderr": "ERROR (app) Subcloud not found", "stder
r_lines": ["ERROR (app) Subcloud not found"], "stdout": "", "stdout_lines": []}
...ignoring

TASK [remote/remote-install : debug] *******************************************************************
*****************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "msg": "subcloud_status:"
}

TASK [remote/remote-install : Delete the subcloud that's 'install-failed' & 'pre-install-failed'] ******
*****************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/remote-install : Deploy remote cloud] *****************************************************
*****************************************
changed: [welktxef-931856-rz-le2pts6-008 -> rchltxib-c000000-003]

TASK [remote/remote-install : 1st polling prep: Obtain Keystone auth token] ****************************
*****************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/remote-install : 1st polling: Wait for subcloud to start installing OS] *******************
*****************************************
FAILED - RETRYING: 1st polling: Wait for subcloud to start installing OS (40 retries left).
FAILED - RETRYING: 1st polling: Wait for subcloud to start installing OS (39 retries left).
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/remote-install : 1st polling result: Fail if the installation failed] *********************
*****************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/remote-install : 2nd polling prep: Obtain Keystone auth token] ****************************
*****************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/remote-install : 2nd polling: Wait for subcloud to install OS (this will take a while)] ***
*****************************************
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (100 retr
ies left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (99 retri
es left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (98 retri
es left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (97 retri
es left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (96 retri
es left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (95 retri
es left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (94 retri
es left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (93 retri
es left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (92 retri
es left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (91 retri
es left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (90 retri
es left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (89 retri
es left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (88 retri
es left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (87 retri
es left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (86 retri
es left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (85 retri
es left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (84 retri
es left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (83 retri
es left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (82 retri
es left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (81 retri
es left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (80 retri
es left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (79 retri
es left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (78 retri
es left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (77 retri
es left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (76 retri
es left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (75 retri
es left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (74 retri
es left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (73 retri
es left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (72 retri
es left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (71 retri
es left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (70 retri
es left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (69 retri
es left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (68 retri
es left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (67 retri
es left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (66 retri
es left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (65 retri
es left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (64 retri
es left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (63 retri
es left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (62 retri
es left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (61 retri
es left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (60 retri
es left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (59 retri
es left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (58 retri
es left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (57 retri
es left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (56 retri
es left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (55 retri
es left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (54 retri
es left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (53 retri
es left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (52 retri
es left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (51 retri
es left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (50 retri
es left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (49 retri
es left).
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/remote-install : 2nd polling result: Fail if any error occurred] **************************
*****************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/remote-install : 3rd polling prep: Obtain Keystone auth token] ****************************
*****************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/remote-install : 3rd polling: Wait for subcloud to install OS (this may take a while)] ****
*****************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/remote-install : 3rd polling result: Fail if any error occurred] **************************
*****************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/remote-install : 4th polling prep: Obtain Keystone auth token] ****************************
*****************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/remote-install : 4th polling: Wait for subcloud to install OS (this may still take a while)
] ***************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/remote-install : 4th polling result: Fail if the installation failed] *********************
*****************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/remote-install : 5th polling prep: Obtain Keystone auth token] ****************************
*****************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/remote-install : 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will
take a while)] **************************
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take
a while) (100 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take
a while) (99 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take
a while) (98 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take
a while) (97 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take
a while) (96 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take
a while) (95 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take
a while) (94 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take
a while) (93 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take
a while) (92 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take
a while) (91 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take
a while) (90 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take
a while) (89 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take
a while) (88 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take
a while) (87 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take
a while) (86 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take
a while) (85 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take
a while) (84 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take
a while) (83 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take
a while) (82 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take
a while) (81 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take
a while) (80 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take
a while) (79 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take
a while) (78 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take
a while) (77 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take
a while) (76 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take
a while) (75 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take
a while) (74 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take
a while) (73 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take
a while) (72 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take
a while) (71 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take
a while) (70 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take
a while) (69 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take
a while) (68 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take
a while) (67 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take
a while) (66 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take
a while) (65 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take
a while) (64 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take
a while) (63 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take
a while) (62 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take
a while) (61 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take
a while) (60 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take
a while) (59 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take
a while) (58 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take
a while) (57 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take
a while) (56 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take
a while) (55 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take
a while) (54 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take
a while) (53 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take
a while) (52 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take
a while) (51 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take
a while) (50 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take
a while) (49 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take
a while) (48 retries left).
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/remote-install : 5th polling result: Fail if bootstrap/deploy failed] *********************
*****************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/remote-install : 6th polling prep: Obtain Keystone auth token] ****************************
*****************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/remote-install : 6th polling: Wait for contoller-0 bootstrap/deploy to complete (this will
take a while)] **************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/remote-install : 6th polling result: Fail if bootstrap/deploy failed] *********************
*****************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/remote-install : Wait for controller-0 restart] *******************************************
*****************************************
FAILED - RETRYING: Wait for controller-0 restart (40 retries left).
FAILED - RETRYING: Wait for controller-0 restart (39 retries left).
FAILED - RETRYING: Wait for controller-0 restart (38 retries left).
fatal: [welktxef-931856-rz-le2pts6-008]: FAILED! => {"attempts": 4, "changed": false, "elapsed": 5
, "msg": "timed out waiting for ping module test: Failed to connect to the host via ssh: ssh: connect to
 host 2607:f160:10:80b1:ce:40a:0:f408 port 22: Connection refused"}
...ignoring

TASK [remote/remote-install : Wait for controller-0 recovery] ******************************************
*****************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/remote-install : setup kdump] *************************************************************
*****************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [Remote Cleanup] **********************************************************************************
*****************************************

TASK [common/cleanup : Remove temporary working directory] *********************************************
*****************************************
changed: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [Remote Manage] ***********************************************************************************
*****************************************

TASK [remote/manage : 1st Obtain Keystone auth token] **************************************************
*****************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/manage : 1st Wait for contoller-0 availability status online] *****************************
*****************************************
FAILED - RETRYING: 1st Wait for contoller-0 availability status online (100 retries left).
FAILED - RETRYING: 1st Wait for contoller-0 availability status online (99 retries left).
FAILED - RETRYING: 1st Wait for contoller-0 availability status online (98 retries left).
FAILED - RETRYING: 1st Wait for contoller-0 availability status online (97 retries left).
FAILED - RETRYING: 1st Wait for contoller-0 availability status online (96 retries left).
FAILED - RETRYING: 1st Wait for contoller-0 availability status online (95 retries left).
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/manage : 2nd Obtain Keystone auth token] **************************************************
*****************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/manage : 2nd Wait for contoller-0 availability status online] *****************************
*****************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/manage : Wait for system to stabilize before running kubectl] *****************************
*****************************************
Pausing for 480 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [welktxef-931856-rz-le2pts6-008]

TASK [Wait for distributed cloud to be reconciled] *****************************************************
*****************************************

TASK [common/wait_for_reconciliation : Making sure node is reachable] **********************************
*****************************************
ok: [welktxef-931856-rz-le2pts6-008]

TASK [common/wait_for_reconciliation : Wait for K8s API to be up] **************************************
*****************************************
ok: [welktxef-931856-rz-le2pts6-008]

TASK [common/wait_for_reconciliation : Wait for hosts to be reconciled] ********************************
*****************************************
changed: [welktxef-931856-rz-le2pts6-008]

TASK [common/wait_for_reconciliation : Wait for systems to be reconciled] ******************************
*****************************************
changed: [welktxef-931856-rz-le2pts6-008]

TASK [remote/manage : Wait for distributed cloud to be reconciled but subcloud OAM VIP becomes unreachab
le] *************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/manage : Check if the subcloud deployed but failed] ***************************************
*****************************************
changed: [welktxef-931856-rz-le2pts6-008 -> rchltxib-c000000-003]

TASK [remote/manage : Set distributed cloud state to managed] ******************************************
*****************************************
changed: [welktxef-931856-rz-le2pts6-008 -> rchltxib-c000000-003]

TASK [remote/manage : Wait for system to stabilize] ****************************************************
*****************************************
Pausing for 300 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [welktxef-931856-rz-le2pts6-008]

TASK [Remote Trust] ************************************************************************************
*****************************************

TASK [remote/trust : Create temporary working directory] ***********************************************
*****************************************
changed: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/trust : Copy SSL cert files to working dir] ***********************************************
*****************************************
changed: [welktxef-931856-rz-le2pts6-008 -> localhost] => (item={'filename': 'k8s_root_ca_cert.pem
', 'value': '-----BEGIN CERTIFICATE-----\nMIIF8jCCA9qgAwIBAgIJAIf9Ql2uDZh+MA0GCSqGSIb3DQEBDQUAMIGFMQswCQ
YD\nVQQGEwJVUzEOMAwGA1UECAwFVGV4YXMxETAPBgNVBAcMCFdlc3RsYWtlMR0wGwYD\nVQQKDBRWZXJpem9uIFNvdXJjaW5nIExMQz
E0MDIGA1UEAwwrVmVyaXpvbiBOZXR3\nb3JrIFdFTEtUWElCIExBQiAxIDMgUlNBIEs4UyBDQTAeFw0yMDEwMjUyMjEyNDha\nFw0zMD
EwMjMyMjEyNDhaMIGFMQswCQYDVQQGEwJVUzEOMAwGA1UECAwFVGV4YXMx\nETAPBgNVBAcMCFdlc3RsYWtlMR0wGwYDVQQKDBRWZXJp
em9uIFNvdXJjaW5nIExM\nQzE0MDIGA1UEAwwrVmVyaXpvbiBOZXR3b3JrIFdFTEtUWElCIExBQiAxIDMgUlNB\nIEs4UyBDQTCCAiIw
DQYJKoZIhvcNAQEBBQADggIPADCCAgoCggIBAKyF9svdv/qG\n7HxBr1DWvZ3CQiDsA4m1kj0hD7jo3B3W/32ODcPpgeNmp4Oful0Ssn
dpqEGhXDq5\noiBfqszMUpzDgdQ7siIHekb2olFEK2KniMP3H53nilIppeyMby5K3ZwF0Qbmk5WK\ncoXoYegP+Uv9bV0AMH6Dn4CVgY
rLAYfmPyGgUSt4vuZ9F/rf9UkBf/DcZGqMnMax\n/Gfaq8KwmDzD9D8IVCHPrM5f4+CaKMQCFu5QkSsLYJFRiuQWWaICMMdnqpb0HZh5
\niPnCSHwPPUyXxtujdI97Ovy4X5WR46jJ2+KzPYe8tVa/DL3TlKmRL9AF+oSE17bw\nzGAE7GNWxPojebHIUuoKdOQC1qiJBVS+c14r
9+9P2Uy6XEhNUs+h3juRI4U3YkQ1\nUCUU3opqhOPh4jUIuPGg5aX07lt4Wpxc48D+CY1D4i6vaJLl3WCsVK7PFwWVQQEW\nIQabfuj1
R2jEu7pp2Yabza58S00v1P5/kv/DNr7ADm8eYRvxLAAXCedMeSDXKBgd\npPmVXXZoZ8+X8VRGYxcw0mBBLIAiTOntT2vgLeq5T3QyiV
KdU6TLAYEjS65QZ3Eg\naIX0wRqlcQI7lruTXubtENG6wWXYtnDf5795ZID1YIEqkgzZLMBqq1SBiLnWd6aK\n78Zsr4j5GmTBGpKRmw
E2oO1btJCCYyG5AgMBAAGjYzBhMA8GA1UdEwEB/wQFMAMB\nAf8wHQYDVR0OBBYEFEDQ5EaGp3x02WUuvqetygqpM3dCMB8GA1UdIwQY
MBaAFEDQ\n5EaGp3x02WUuvqetygqpM3dCMA4GA1UdDwEB/wQEAwICpDANBgkqhkiG9w0BAQ0F\nAAOCAgEAeCMxVJr5Jyg87DVaUtEh
iWfhto993ENrnevAGqrBOoRc/KU1/C3paqhR\nsvr2r2LR+npSmeo6iz0FaO31XwHSHX95+XJeGP5Q8TGddbRiTglQsMfOkGNzxqgg\n
TkdZ8A1y9v2jprONUmLADVGIVT0AoHc7V9w1I8NKhrY+rIllum4FRDiDPSnImh5h\nxmH+Nq2ZuEFVdtV/oNKzEu2ywmbgBRd5Jv3rTe
jxltmTZtyq8IKoKguj3NVFn93Q\nU4TbsxkcAdrLMooLYYDRTWA4t0iqKM/UkYUg4xl2l9NrY7ZUbaNd5+YsLNdqXO/c\nmp7wyMv/8Z
Iy1BLG4zJmX/JzWkYmULqQ+A+21+YuqrV3a81V7vcHhJcRaPOrg5cd\nYwY2eCbXMvNOdrzppIglUrlddNuqAhs1MTi/VibxYuI9isU0
JckXIcCy1L+xbEda\n6v/z6wSrScVz0I4m0DpK6xMQ8t9sLcrGp5uGbj6J4nQWd+QLdq6kmAzDOZ/Gs0wb\nPYdkER4dXAVcioYFekpK
v7d+nur0FPtMNIw0OdhX2eAwC22IFAq2DZRjUFvaBGaD\ni1ptfq6P1mVJ2T/exYujEDtq+8yQTfWgFm/DjEfWtcCp0Jukgv8opLR2Dp
Cf5Ucq\nd5X7d/DP0mukJ3vZ8EIqYorwZJ1L1a2jgngjA+gPxIaW+JHfTHU=\n-----END CERTIFICATE-----\n'})
changed: [welktxef-931856-rz-le2pts6-008 -> localhost] => (item={'filename': 'vz_root_ca_cert.pem'
, 'value': '-----BEGIN CERTIFICATE-----\nMIIFpTCCA42gAwIBAgIUa3vZ0YGxO1TQ8NwhiVfQC0JslXgwDQYJKoZIhvcNAQE
L\nBQAwWjELMAkGA1UEBhMCVVMxEDAOBgNVBAoMB1Zlcml6b24xEzARBgNVBAsMClZa\nSUFNIFRlc3QxJDAiBgNVBAMMG1Zlcml6b24
gTmV0d29yayBSU0EgQ0EgVGVzdDAe\nFw0yMDA2MTUyMTAxMTNaFw0zNTA2MTUyMTAxMTNaMFoxCzAJBgNVBAYTAlVTMRAw\nDgYDVQQ
KDAdWZXJpem9uMRMwEQYDVQQLDApWWklBTSBUZXN0MSQwIgYDVQQDDBtW\nZXJpem9uIE5ldHdvcmsgUlNBIENBIFRlc3QwggIiMA0GC
SqGSIb3DQEBAQUAA4IC\nDwAwggIKAoICAQC8AIrksI57CbIl5uGZ6yqfpQj3aK+N8f1EVHdwK9JFskoipvC8\n7yFTk8tgmO1i0YA5o
RGfNxneqCdrXZiWL6Ko8v/iln9vuN+2rK3rgWZPPRJBAsBN\na49L7U6lJjIGxIZtZqmK5h47oiUtwlYVrbZMN2ijuBQ22/eQ9tsFDV2
8oBuZ3WAR\npSSbj/tubPQYkw3YYOhv/VpEpsd0rkoEt3QCmTVcX2rtblanpXowTV5R0Hy4014n\nT49jrEo40r4mwYoyS835Uv4ENUF
A+pXicT9eUot3RSH6rYdx4A/14UtoI9U0ol8M\n62GHpxSASQ2Kc3yQWvxRGTFslTduYM+vVmMLEDDdqcsjYnStPpwdxxmKItmbjxSv\
nIwYIndp8A04WkX2iiJCciC3BNxiLamPtYVyB1HHqbGTGirKYuSvwZt337q1OI3WH\nwVn2S4Mj/wqa4iCyGTvFSUnGq34Xkrb9XNwWB
ok9Tc2XWGAU/mb/xcd1hX74GZbF\nsrZ11aPtym4kMAjU2KQi96GcAH2lnGZYoOja1J4Cs4WYx1uAx74H/m84CrYavVfl\n1ONJVLDfu
ZaEkSmu+jHQX15pAECNORTuLD06PbWnOEcOi1xmbt/OT3SA3rhD2mb7\n2wxl7oJpV3ap8xGwYmxiFzmInxFJ1axjg8Rimol0mXTKAy6
OdNHbCOnAwwIDAQAB\no2MwYTAPBgNVHRMBAf8EBTADAQH/MA4GA1UdDwEB/wQEAwIBBjAfBgNVHSMEGDAW\ngBQleng3lqGBeTrbLVu
ABoEmUHm1+TAdBgNVHQ4EFgQUJXp4N5ahgXk62y1bgAaB\nJlB5tfkwDQYJKoZIhvcNAQELBQADggIBADQ9jpmVh9nyY7ZQ4s+S9RuSR
Yn7QsrW\nDePeMzQgh8ZtS8WE65GY5HS61iHNP2Co8Q1lAaBWF4ipq+VZOcQbPLccHzd1kZv4\ns4u0aTzBd9ccidl73FS0DJDQOBbzP
SzgsaiGHSMyGzkTeA8z3ntsSqrXXcDUvoRi\nFus/110AwdtNhJLrWveX6btYtHp9Lqe0YtNCy5AaXlrr1yRSckP5BWVtlwD4dzSO\n/
dqI3wHS/ncUx9wSQomZ+AmxYW3KtJQKgHzTqHru1x9BBk7Bzfz9FZr6HLLmEitj\nuFoDRd5TNt5LbO0zDQokvY3oqso6Htup/rS7C08
mcmnelYE+yXuOc1YrlyGnpBzk\nmy+1VYbOxRRdqKAZRbE72u/h847IVpsOvjR51iksuCAurZdp2+y2zvV8NhWekuNy\nirECRy9cb4Y
asjRaKi0/TCGPVSICuLyeG2W72liCj/N2VKfjPP9zsOR5XjwCXfRg\n+9xhLy77/gov2NWXx5fzTkhxCrHOxFdLVMn0wQhksDmw6QsXz
DIHSpIOypdDfnx9\nCsthx3nhkuHLUaEP22D22dG+vImA9ukj4R/RRI/87jmi9Q8+ehH+NqN0GZZcLjdN\nSLVXpncuwWQFUDPR06wNk
kkmBSXWiIYhwqSpU0Pl3er3fD0uWvXuWPm2PzfOmUAE\nUrkzyw9XmLw0\n-----END CERTIFICATE-----\n'})
changed: [welktxef-931856-rz-le2pts6-008 -> localhost] => (item={'filename': 'vz_root_ica_cert.pem
', 'value': '-----BEGIN CERTIFICATE-----\nMIIFNzCCAx+gAwIBAgIUGLJR/hP48n+vdq2v1hcfspXo/78wDQYJKoZIhvcNAQ
EL\nBQAwWjELMAkGA1UEBhMCVVMxEDAOBgNVBAoMB1Zlcml6b24xEzARBgNVBAsMClZa\nSUFNIFRlc3QxJDAiBgNVBAMMG1Zlcml6b2
4gTmV0d29yayBSU0EgQ0EgVGVzdDAe\nFw0yMDEwMjIyMTE0MDNaFw0zMDEwMjIyMTE0MDNaMIGRMQswCQYDVQQGEwJVUzEL\nMAkGA1
UECAwCVFgxETAPBgNVBAcMCFdlc3RsYWtlMRAwDgYDVQQKDAdWZXJpem9u\nMR0wGwYDVQQLDBRWZXJpem9uIFNvdXJjaW5nIExMQzEx
MC8GA1UEAwwoVmVyaXpv\nbiBOZXR3b3JrIFdFTEtUWElCIExBQiAxIDMgUlNBIElDQTCCASIwDQYJKoZIhvcN\nAQEBBQADggEPADCC
AQoCggEBANhkGTXOCKEYf5znDDeX3n/DHFPVqazgQsr0/SIG\n4eb1JY5q5Jq3ZhAaZCr9HJuCkwAP/zgYH0llqOvf8AC2Uh+7z1b33I
bwxPmJfWCP\nAqSNFkLWWVRdbELapCu408QsrLMW8IrdP6PLiKAepwncfm4T0/6bANqIEmUkpw8Q\nxProeiNwlGbwUll+tELmdCk7vA
7hKX3j1kUvS5Z84Z5ivJBWEcUEggmC97TK4aLo\nFVEHbyahze568JVEaM1vY5L4mnRRTl+u5ipaSMxVBsiXzF7eFuKCzqF7wxbDIt2T
\nIFEJtwyJDW5bXjyXgiF1d5H/URprUcRV9Qmf2+PXcfwHII8CAwEAAaOBvDCBuTAS\nBgNVHRMBAf8ECDAGAQH/AgEAMA4GA1UdDwEB
/wQEAwIBBjAfBgNVHSMEGDAWgBQl\neng3lqGBeTrbLVuABoEmUHm1+TBTBgNVHR8ETDBKMEigRqBEhkJodHRwOi8vc2Vj\ndXJlLnN0
YWdpbmcuc2VjdXJpdHljcmVkZW50aWFsaW5nLmNvbS9jcmwvdnpuZXRy\nc2FjYS5jcmwwHQYDVR0OBBYEFP0Z+/vaDLtAoFig1I9ttN
KnmzByMA0GCSqGSIb3\nDQEBCwUAA4ICAQBuXVTf9e01HeymHgRcFCwP2N6G6u+vIzY8Bz0zSUZeRDHMZQcS\nNoabDyn5FfGJlw4BqG
C591Sp0/unFQDzAg17rDBcrgwajeFeUiFdb9PiAJwHaX9S\nvq/7VmVLCmpeb+a/laXAe6+tkY1kcFrd1+ItRKC6ZGXMsoDkmk5Ndxxg
w77estcI\nMiiLQbvpXRygX5wD4/ayazuLms9qITZkOZ1nTLVqq7QrwYCsSoih7hj6sbsfXr19\nGoYWmk8Y7O/d3ttgyHuRH9k/2dQ/
xL7avRpMNkPdr7ocJqI46hvx2X6UyOo7IBua\nkSkFbSmPZWIVAidNMBOnvffCQ32tfjT2/xso/a9cdskvxqgLi0MPARU9Nl2Pufsb\n
D7l4/sBvz/PiNTKp+Daa9FdyLb9ySidos1uS0c24bUtY1RXXGAVV2qgfyrzvzfye\nSM+w16hMU/yeYiuA1jsPmsnZnuIJj4Nv8ZjjZ0
WS53pP5wcghaHkBrqWQNT8meqA\nVElrMBPlYq67T+AXP0B9lf5Sc3QVIio7XKKfqrlcQxY2JGLEyE53JgZGX7dpwU4I\nukLvyHbT4p
06oY3qG6+wH8+YIXCNAYtadJ/C5/u9GcLX5NnZrcuduj0inw2/a3Ao\nWgCt6/Pr28BkCvkWdDt9d8Z40qeu1aZdcr157mR+yZGPfBfB
2vasrNIEwQ==\n-----END CERTIFICATE-----\n'})

TASK [remote/trust : Generate trust_ca.pem] ************************************************************
*****************************************
changed: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/trust : Copy trust_ca.pem to host] ********************************************************
*****************************************
changed: [welktxef-931856-rz-le2pts6-008]

TASK [remote/trust : Install certificate] **************************************************************
*****************************************
changed: [welktxef-931856-rz-le2pts6-008]

TASK [remote/trust : Remove temporary working directory] ***********************************************
*****************************************
changed: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [Remote Starlingx] ********************************************************************************
*****************************************

TASK [remote/starlingx : Create temporary working directory] *******************************************
*****************************************
changed: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/starlingx : Copy SSL root certificates] ***************************************************
*****************************************
changed: [welktxef-931856-rz-le2pts6-008 -> localhost] => (item={'filename': 'vz_root_ica_cert.pem
', 'value': '-----BEGIN CERTIFICATE-----\nMIIFNzCCAx+gAwIBAgIUGLJR/hP48n+vdq2v1hcfspXo/78wDQYJKoZIhvcNAQ
EL\nBQAwWjELMAkGA1UEBhMCVVMxEDAOBgNVBAoMB1Zlcml6b24xEzARBgNVBAsMClZa\nSUFNIFRlc3QxJDAiBgNVBAMMG1Zlcml6b2
4gTmV0d29yayBSU0EgQ0EgVGVzdDAe\nFw0yMDEwMjIyMTE0MDNaFw0zMDEwMjIyMTE0MDNaMIGRMQswCQYDVQQGEwJVUzEL\nMAkGA1
UECAwCVFgxETAPBgNVBAcMCFdlc3RsYWtlMRAwDgYDVQQKDAdWZXJpem9u\nMR0wGwYDVQQLDBRWZXJpem9uIFNvdXJjaW5nIExMQzEx
MC8GA1UEAwwoVmVyaXpv\nbiBOZXR3b3JrIFdFTEtUWElCIExBQiAxIDMgUlNBIElDQTCCASIwDQYJKoZIhvcN\nAQEBBQADggEPADCC
AQoCggEBANhkGTXOCKEYf5znDDeX3n/DHFPVqazgQsr0/SIG\n4eb1JY5q5Jq3ZhAaZCr9HJuCkwAP/zgYH0llqOvf8AC2Uh+7z1b33I
bwxPmJfWCP\nAqSNFkLWWVRdbELapCu408QsrLMW8IrdP6PLiKAepwncfm4T0/6bANqIEmUkpw8Q\nxProeiNwlGbwUll+tELmdCk7vA
7hKX3j1kUvS5Z84Z5ivJBWEcUEggmC97TK4aLo\nFVEHbyahze568JVEaM1vY5L4mnRRTl+u5ipaSMxVBsiXzF7eFuKCzqF7wxbDIt2T
\nIFEJtwyJDW5bXjyXgiF1d5H/URprUcRV9Qmf2+PXcfwHII8CAwEAAaOBvDCBuTAS\nBgNVHRMBAf8ECDAGAQH/AgEAMA4GA1UdDwEB
/wQEAwIBBjAfBgNVHSMEGDAWgBQl\neng3lqGBeTrbLVuABoEmUHm1+TBTBgNVHR8ETDBKMEigRqBEhkJodHRwOi8vc2Vj\ndXJlLnN0
YWdpbmcuc2VjdXJpdHljcmVkZW50aWFsaW5nLmNvbS9jcmwvdnpuZXRy\nc2FjYS5jcmwwHQYDVR0OBBYEFP0Z+/vaDLtAoFig1I9ttN
KnmzByMA0GCSqGSIb3\nDQEBCwUAA4ICAQBuXVTf9e01HeymHgRcFCwP2N6G6u+vIzY8Bz0zSUZeRDHMZQcS\nNoabDyn5FfGJlw4BqG
C591Sp0/unFQDzAg17rDBcrgwajeFeUiFdb9PiAJwHaX9S\nvq/7VmVLCmpeb+a/laXAe6+tkY1kcFrd1+ItRKC6ZGXMsoDkmk5Ndxxg
w77estcI\nMiiLQbvpXRygX5wD4/ayazuLms9qITZkOZ1nTLVqq7QrwYCsSoih7hj6sbsfXr19\nGoYWmk8Y7O/d3ttgyHuRH9k/2dQ/
xL7avRpMNkPdr7ocJqI46hvx2X6UyOo7IBua\nkSkFbSmPZWIVAidNMBOnvffCQ32tfjT2/xso/a9cdskvxqgLi0MPARU9Nl2Pufsb\n
D7l4/sBvz/PiNTKp+Daa9FdyLb9ySidos1uS0c24bUtY1RXXGAVV2qgfyrzvzfye\nSM+w16hMU/yeYiuA1jsPmsnZnuIJj4Nv8ZjjZ0
WS53pP5wcghaHkBrqWQNT8meqA\nVElrMBPlYq67T+AXP0B9lf5Sc3QVIio7XKKfqrlcQxY2JGLEyE53JgZGX7dpwU4I\nukLvyHbT4p
06oY3qG6+wH8+YIXCNAYtadJ/C5/u9GcLX5NnZrcuduj0inw2/a3Ao\nWgCt6/Pr28BkCvkWdDt9d8Z40qeu1aZdcr157mR+yZGPfBfB
2vasrNIEwQ==\n-----END CERTIFICATE-----\n'})
changed: [welktxef-931856-rz-le2pts6-008 -> localhost] => (item={'filename': 'vz_root_ica_key.pem'
, 'value': '-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA2GQZNc4IoRh/nOcMN5fef8McU9WprOBCyvT9Igbh5vU
ljmrk\nmrdmEBpkKv0cm4KTAA//OBgfSWWo69/wALZSH7vPVvfchvDE+Yl9YI8CpI0WQtZZ\nVF1sQtqkK7jTxCyssxbwit0/o8uIoB6
nCdx+bhPT/psA2ogSZSSnDxDE+uh6I3CU\nZvBSWX60QuZ0KTu8DuEpfePWRS9LlnzhnmK8kFYRxQSCCYL3tMrhougVUQdvJqHN\n7nr
wlURozW9jkviadFFOX67mKlpIzFUGyJfMXt4W4oLOoXvDFsMi3ZMgUQm3DIkN\nbltePJeCIXV3kf9RGmtRxFX1CZ/b49dx/AcgjwIDA
QABAoIBABSd1NkPfDr8/ouQ\nZ9WUHprFmBlUrgnOhA6aMNPhG/zJNn7PKGClQJAgM5L08pjOY/sJiyNpCPIRQXrX\npyIqPMDRP/vlO
ZmRrvKnas6cUYAkAQ71JSWokPv9oM6ZmXODXiDh+qEAW2PbrHS0\n9u01mMYcFYKYeghYFoiUaWZCDsJo3v3dgeE9aQ4tB9ksovSmWrp
uCY7NKbd7Qrbo\n5XxQhkujTkE6knOHz8CVwYETtj8LZ/bvHIkGMGvRvwsKYDZkIKr5CZ7DX+KcMfPN\neMZU4VCHYSXNxsyp5DJ1Zw+
gx8/32kUL0CzJLLam1G021Hq41KPwwSV/KPrOKel7\nHXDLXeECgYEA8MR+lgxGjYTc/k4TdZvcFVgqHGLXnyjO7ZVt4b7UpwmayLuoS
D/M\nOpHQYX+JBIIWTNlGhG8UV3DPC3v+auhYa7twwbekS30IYCAmu5GCKgMAcWFinz6A\nYZxG55P/hShetCyOqikgwXqzMlwGs8KEu
l8f8BKssROzUy8mIlFhjq0CgYEA5hTM\nSNxAD3dlRtb0771fBU7fjx8JPfjptP9vP/JVEelkc/ti9nZ5buTC+9cQC/B+YFx7\nc82uC
rXV13bGR9iH8xBhwU7JOYJZbgCpwp0F56wIN5Pdk9Eo79Batrw3oGBG4Yvt\nDc2eltxQbHgObc/qygf88j9XqD8aGIvQrc4Jf6sCgYA
txX03M1A6WTbWFau3YRD+\n8crXqKbLOCvWmODR2MB+nOHTJXHBgndl7xCJaIB43e41X9z7Ek7wrJ5/1WuxkUg1\n+uVdvna6byOnepV
CdVAkgnuUEmp4UZ6AcAA+yDD8dIdEg2//w1/ZyGTGvx37EJDB\nCZJ9xl8ULuWZe84pGgWM5QKBgQCYVUbYKrNjShrM5z9uh4QlII6V1
Oeql2YtBz4i\nKZE3db6jp9pi8hf+WwnZ8g9WyFjz9edqydAkmTXHHYW0ReHlBYCjm0VRhUMuuNOs\n3YfuVpFuMsFuv/oJpXqaKE3wK
i5j4OAH1o7ctWuuFWMAQ7vhHZ7UySmBZJ4jiFaW\n7KaPVwKBgE8E0xbSDVGxXbEGwRXxeaOSemEHD9uEnbAyq1p3EBBhBvInWmDiP5v
J\n68IYNZ4SGxXEKDifwrLGHyekt3RK9B2+U03okd1qH7gfBIlxBJivcjhBe2PtK/Qj\n6fBN0fC1UJoE6pseT9cJDaBq2wMRXJGRYtT
8fU9PPJcfa23JlKNS\n-----END RSA PRIVATE KEY-----\n'})

TASK [remote/starlingx : Copy templates] ***************************************************************
*****************************************
changed: [welktxef-931856-rz-le2pts6-008 -> localhost] => (item=req_starlingx.cnf)

TASK [remote/starlingx : Generate SSL cert] ************************************************************
*****************************************
changed: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/starlingx : Copy SSL starlingx certs to server] *******************************************
*****************************************
changed: [welktxef-931856-rz-le2pts6-008] => (item=starlingx-ca-cert.pem)

TASK [remote/starlingx : Configure starlingx] **********************************************************
*****************************************
changed: [welktxef-931856-rz-le2pts6-008]

TASK [remote/starlingx : Remove temporary working directory] *******************************************
*****************************************
changed: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [Remote Integ] ************************************************************************************
*****************************************

TASK [remote/integ : Detect applied status of platform-integ-apps application] *************************
*****************************************
changed: [welktxef-931856-rz-le2pts6-008]

TASK [remote/integ : Fail if platform-integ-apps application apply failed] *****************************
*****************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [Remote Ldap] *************************************************************************************
*****************************************

TASK [remote/ldap : Create temporary working directory] ************************************************
*****************************************
changed: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/ldap : Copy SSL root certificates] ********************************************************
*****************************************
changed: [welktxef-931856-rz-le2pts6-008 -> localhost] => (item={'filename': 'vz_root_ca_cert.pem'
, 'value': '-----BEGIN CERTIFICATE-----\nMIIFpTCCA42gAwIBAgIUa3vZ0YGxO1TQ8NwhiVfQC0JslXgwDQYJKoZIhvcNAQE
L\nBQAwWjELMAkGA1UEBhMCVVMxEDAOBgNVBAoMB1Zlcml6b24xEzARBgNVBAsMClZa\nSUFNIFRlc3QxJDAiBgNVBAMMG1Zlcml6b24
gTmV0d29yayBSU0EgQ0EgVGVzdDAe\nFw0yMDA2MTUyMTAxMTNaFw0zNTA2MTUyMTAxMTNaMFoxCzAJBgNVBAYTAlVTMRAw\nDgYDVQQ
KDAdWZXJpem9uMRMwEQYDVQQLDApWWklBTSBUZXN0MSQwIgYDVQQDDBtW\nZXJpem9uIE5ldHdvcmsgUlNBIENBIFRlc3QwggIiMA0GC
SqGSIb3DQEBAQUAA4IC\nDwAwggIKAoICAQC8AIrksI57CbIl5uGZ6yqfpQj3aK+N8f1EVHdwK9JFskoipvC8\n7yFTk8tgmO1i0YA5o
RGfNxneqCdrXZiWL6Ko8v/iln9vuN+2rK3rgWZPPRJBAsBN\na49L7U6lJjIGxIZtZqmK5h47oiUtwlYVrbZMN2ijuBQ22/eQ9tsFDV2
8oBuZ3WAR\npSSbj/tubPQYkw3YYOhv/VpEpsd0rkoEt3QCmTVcX2rtblanpXowTV5R0Hy4014n\nT49jrEo40r4mwYoyS835Uv4ENUF
A+pXicT9eUot3RSH6rYdx4A/14UtoI9U0ol8M\n62GHpxSASQ2Kc3yQWvxRGTFslTduYM+vVmMLEDDdqcsjYnStPpwdxxmKItmbjxSv\
nIwYIndp8A04WkX2iiJCciC3BNxiLamPtYVyB1HHqbGTGirKYuSvwZt337q1OI3WH\nwVn2S4Mj/wqa4iCyGTvFSUnGq34Xkrb9XNwWB
ok9Tc2XWGAU/mb/xcd1hX74GZbF\nsrZ11aPtym4kMAjU2KQi96GcAH2lnGZYoOja1J4Cs4WYx1uAx74H/m84CrYavVfl\n1ONJVLDfu
ZaEkSmu+jHQX15pAECNORTuLD06PbWnOEcOi1xmbt/OT3SA3rhD2mb7\n2wxl7oJpV3ap8xGwYmxiFzmInxFJ1axjg8Rimol0mXTKAy6
OdNHbCOnAwwIDAQAB\no2MwYTAPBgNVHRMBAf8EBTADAQH/MA4GA1UdDwEB/wQEAwIBBjAfBgNVHSMEGDAW\ngBQleng3lqGBeTrbLVu
ABoEmUHm1+TAdBgNVHQ4EFgQUJXp4N5ahgXk62y1bgAaB\nJlB5tfkwDQYJKoZIhvcNAQELBQADggIBADQ9jpmVh9nyY7ZQ4s+S9RuSR
Yn7QsrW\nDePeMzQgh8ZtS8WE65GY5HS61iHNP2Co8Q1lAaBWF4ipq+VZOcQbPLccHzd1kZv4\ns4u0aTzBd9ccidl73FS0DJDQOBbzP
SzgsaiGHSMyGzkTeA8z3ntsSqrXXcDUvoRi\nFus/110AwdtNhJLrWveX6btYtHp9Lqe0YtNCy5AaXlrr1yRSckP5BWVtlwD4dzSO\n/
dqI3wHS/ncUx9wSQomZ+AmxYW3KtJQKgHzTqHru1x9BBk7Bzfz9FZr6HLLmEitj\nuFoDRd5TNt5LbO0zDQokvY3oqso6Htup/rS7C08
mcmnelYE+yXuOc1YrlyGnpBzk\nmy+1VYbOxRRdqKAZRbE72u/h847IVpsOvjR51iksuCAurZdp2+y2zvV8NhWekuNy\nirECRy9cb4Y
asjRaKi0/TCGPVSICuLyeG2W72liCj/N2VKfjPP9zsOR5XjwCXfRg\n+9xhLy77/gov2NWXx5fzTkhxCrHOxFdLVMn0wQhksDmw6QsXz
DIHSpIOypdDfnx9\nCsthx3nhkuHLUaEP22D22dG+vImA9ukj4R/RRI/87jmi9Q8+ehH+NqN0GZZcLjdN\nSLVXpncuwWQFUDPR06wNk
kkmBSXWiIYhwqSpU0Pl3er3fD0uWvXuWPm2PzfOmUAE\nUrkzyw9XmLw0\n-----END CERTIFICATE-----\n'})
changed: [welktxef-931856-rz-le2pts6-008 -> localhost] => (item={'filename': 'vz_root_ica_cert.pem
', 'value': '-----BEGIN CERTIFICATE-----\nMIIFNzCCAx+gAwIBAgIUGLJR/hP48n+vdq2v1hcfspXo/78wDQYJKoZIhvcNAQ
EL\nBQAwWjELMAkGA1UEBhMCVVMxEDAOBgNVBAoMB1Zlcml6b24xEzARBgNVBAsMClZa\nSUFNIFRlc3QxJDAiBgNVBAMMG1Zlcml6b2
4gTmV0d29yayBSU0EgQ0EgVGVzdDAe\nFw0yMDEwMjIyMTE0MDNaFw0zMDEwMjIyMTE0MDNaMIGRMQswCQYDVQQGEwJVUzEL\nMAkGA1
UECAwCVFgxETAPBgNVBAcMCFdlc3RsYWtlMRAwDgYDVQQKDAdWZXJpem9u\nMR0wGwYDVQQLDBRWZXJpem9uIFNvdXJjaW5nIExMQzEx
MC8GA1UEAwwoVmVyaXpv\nbiBOZXR3b3JrIFdFTEtUWElCIExBQiAxIDMgUlNBIElDQTCCASIwDQYJKoZIhvcN\nAQEBBQADggEPADCC
AQoCggEBANhkGTXOCKEYf5znDDeX3n/DHFPVqazgQsr0/SIG\n4eb1JY5q5Jq3ZhAaZCr9HJuCkwAP/zgYH0llqOvf8AC2Uh+7z1b33I
bwxPmJfWCP\nAqSNFkLWWVRdbELapCu408QsrLMW8IrdP6PLiKAepwncfm4T0/6bANqIEmUkpw8Q\nxProeiNwlGbwUll+tELmdCk7vA
7hKX3j1kUvS5Z84Z5ivJBWEcUEggmC97TK4aLo\nFVEHbyahze568JVEaM1vY5L4mnRRTl+u5ipaSMxVBsiXzF7eFuKCzqF7wxbDIt2T
\nIFEJtwyJDW5bXjyXgiF1d5H/URprUcRV9Qmf2+PXcfwHII8CAwEAAaOBvDCBuTAS\nBgNVHRMBAf8ECDAGAQH/AgEAMA4GA1UdDwEB
/wQEAwIBBjAfBgNVHSMEGDAWgBQl\neng3lqGBeTrbLVuABoEmUHm1+TBTBgNVHR8ETDBKMEigRqBEhkJodHRwOi8vc2Vj\ndXJlLnN0
YWdpbmcuc2VjdXJpdHljcmVkZW50aWFsaW5nLmNvbS9jcmwvdnpuZXRy\nc2FjYS5jcmwwHQYDVR0OBBYEFP0Z+/vaDLtAoFig1I9ttN
KnmzByMA0GCSqGSIb3\nDQEBCwUAA4ICAQBuXVTf9e01HeymHgRcFCwP2N6G6u+vIzY8Bz0zSUZeRDHMZQcS\nNoabDyn5FfGJlw4BqG
C591Sp0/unFQDzAg17rDBcrgwajeFeUiFdb9PiAJwHaX9S\nvq/7VmVLCmpeb+a/laXAe6+tkY1kcFrd1+ItRKC6ZGXMsoDkmk5Ndxxg
w77estcI\nMiiLQbvpXRygX5wD4/ayazuLms9qITZkOZ1nTLVqq7QrwYCsSoih7hj6sbsfXr19\nGoYWmk8Y7O/d3ttgyHuRH9k/2dQ/
xL7avRpMNkPdr7ocJqI46hvx2X6UyOo7IBua\nkSkFbSmPZWIVAidNMBOnvffCQ32tfjT2/xso/a9cdskvxqgLi0MPARU9Nl2Pufsb\n
D7l4/sBvz/PiNTKp+Daa9FdyLb9ySidos1uS0c24bUtY1RXXGAVV2qgfyrzvzfye\nSM+w16hMU/yeYiuA1jsPmsnZnuIJj4Nv8ZjjZ0
WS53pP5wcghaHkBrqWQNT8meqA\nVElrMBPlYq67T+AXP0B9lf5Sc3QVIio7XKKfqrlcQxY2JGLEyE53JgZGX7dpwU4I\nukLvyHbT4p
06oY3qG6+wH8+YIXCNAYtadJ/C5/u9GcLX5NnZrcuduj0inw2/a3Ao\nWgCt6/Pr28BkCvkWdDt9d8Z40qeu1aZdcr157mR+yZGPfBfB
2vasrNIEwQ==\n-----END CERTIFICATE-----\n'})
changed: [welktxef-931856-rz-le2pts6-008 -> localhost] => (item={'filename': 'vz_root_ica_key.pem'
, 'value': '-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA2GQZNc4IoRh/nOcMN5fef8McU9WprOBCyvT9Igbh5vU
ljmrk\nmrdmEBpkKv0cm4KTAA//OBgfSWWo69/wALZSH7vPVvfchvDE+Yl9YI8CpI0WQtZZ\nVF1sQtqkK7jTxCyssxbwit0/o8uIoB6
nCdx+bhPT/psA2ogSZSSnDxDE+uh6I3CU\nZvBSWX60QuZ0KTu8DuEpfePWRS9LlnzhnmK8kFYRxQSCCYL3tMrhougVUQdvJqHN\n7nr
wlURozW9jkviadFFOX67mKlpIzFUGyJfMXt4W4oLOoXvDFsMi3ZMgUQm3DIkN\nbltePJeCIXV3kf9RGmtRxFX1CZ/b49dx/AcgjwIDA
QABAoIBABSd1NkPfDr8/ouQ\nZ9WUHprFmBlUrgnOhA6aMNPhG/zJNn7PKGClQJAgM5L08pjOY/sJiyNpCPIRQXrX\npyIqPMDRP/vlO
ZmRrvKnas6cUYAkAQ71JSWokPv9oM6ZmXODXiDh+qEAW2PbrHS0\n9u01mMYcFYKYeghYFoiUaWZCDsJo3v3dgeE9aQ4tB9ksovSmWrp
uCY7NKbd7Qrbo\n5XxQhkujTkE6knOHz8CVwYETtj8LZ/bvHIkGMGvRvwsKYDZkIKr5CZ7DX+KcMfPN\neMZU4VCHYSXNxsyp5DJ1Zw+
gx8/32kUL0CzJLLam1G021Hq41KPwwSV/KPrOKel7\nHXDLXeECgYEA8MR+lgxGjYTc/k4TdZvcFVgqHGLXnyjO7ZVt4b7UpwmayLuoS
D/M\nOpHQYX+JBIIWTNlGhG8UV3DPC3v+auhYa7twwbekS30IYCAmu5GCKgMAcWFinz6A\nYZxG55P/hShetCyOqikgwXqzMlwGs8KEu
l8f8BKssROzUy8mIlFhjq0CgYEA5hTM\nSNxAD3dlRtb0771fBU7fjx8JPfjptP9vP/JVEelkc/ti9nZ5buTC+9cQC/B+YFx7\nc82uC
rXV13bGR9iH8xBhwU7JOYJZbgCpwp0F56wIN5Pdk9Eo79Batrw3oGBG4Yvt\nDc2eltxQbHgObc/qygf88j9XqD8aGIvQrc4Jf6sCgYA
txX03M1A6WTbWFau3YRD+\n8crXqKbLOCvWmODR2MB+nOHTJXHBgndl7xCJaIB43e41X9z7Ek7wrJ5/1WuxkUg1\n+uVdvna6byOnepV
CdVAkgnuUEmp4UZ6AcAA+yDD8dIdEg2//w1/ZyGTGvx37EJDB\nCZJ9xl8ULuWZe84pGgWM5QKBgQCYVUbYKrNjShrM5z9uh4QlII6V1
Oeql2YtBz4i\nKZE3db6jp9pi8hf+WwnZ8g9WyFjz9edqydAkmTXHHYW0ReHlBYCjm0VRhUMuuNOs\n3YfuVpFuMsFuv/oJpXqaKE3wK
i5j4OAH1o7ctWuuFWMAQ7vhHZ7UySmBZJ4jiFaW\n7KaPVwKBgE8E0xbSDVGxXbEGwRXxeaOSemEHD9uEnbAyq1p3EBBhBvInWmDiP5v
J\n68IYNZ4SGxXEKDifwrLGHyekt3RK9B2+U03okd1qH7gfBIlxBJivcjhBe2PtK/Qj\n6fBN0fC1UJoE6pseT9cJDaBq2wMRXJGRYtT
8fU9PPJcfa23JlKNS\n-----END RSA PRIVATE KEY-----\n'})

TASK [remote/ldap : Copy templates] ********************************************************************
*****************************************
changed: [welktxef-931856-rz-le2pts6-008 -> localhost] => (item={'name': 'req-ldap.cnf', 'mode': '
0644'})

TASK [remote/ldap : Generate SSL cert] *****************************************************************
*****************************************
changed: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/ldap : Copy templates] ********************************************************************
*****************************************
changed: [welktxef-931856-rz-le2pts6-008] => (item={'name': 'dex-overrides.yaml', 'mode': '0644'})


TASK [remote/ldap : Copy SSL dex certs to server] ******************************************************
*****************************************
changed: [welktxef-931856-rz-le2pts6-008] => (item=dex-cert.pem)
changed: [welktxef-931856-rz-le2pts6-008] => (item=dex-key.pem)
changed: [welktxef-931856-rz-le2pts6-008] => (item=dex-ca.pem)

TASK [remote/ldap : Copy SSL AD cert to server] ********************************************************
*****************************************
changed: [welktxef-931856-rz-le2pts6-008] => (item={'filename': 'ad_ca.pem', 'value': '-----BEGIN
CERTIFICATE-----\nMIIFpTCCA42gAwIBAgIUa3vZ0YGxO1TQ8NwhiVfQC0JslXgwDQYJKoZIhvcNAQEL\nBQAwWjELMAkGA1UEBhMC
VVMxEDAOBgNVBAoMB1Zlcml6b24xEzARBgNVBAsMClZa\nSUFNIFRlc3QxJDAiBgNVBAMMG1Zlcml6b24gTmV0d29yayBSU0EgQ0EgVG
VzdDAe\nFw0yMDA2MTUyMTAxMTNaFw0zNTA2MTUyMTAxMTNaMFoxCzAJBgNVBAYTAlVTMRAw\nDgYDVQQKDAdWZXJpem9uMRMwEQYDVQ
QLDApWWklBTSBUZXN0MSQwIgYDVQQDDBtW\nZXJpem9uIE5ldHdvcmsgUlNBIENBIFRlc3QwggIiMA0GCSqGSIb3DQEBAQUAA4IC\nDw
AwggIKAoICAQC8AIrksI57CbIl5uGZ6yqfpQj3aK+N8f1EVHdwK9JFskoipvC8\n7yFTk8tgmO1i0YA5oRGfNxneqCdrXZiWL6Ko8v/i
ln9vuN+2rK3rgWZPPRJBAsBN\na49L7U6lJjIGxIZtZqmK5h47oiUtwlYVrbZMN2ijuBQ22/eQ9tsFDV28oBuZ3WAR\npSSbj/tubPQY
kw3YYOhv/VpEpsd0rkoEt3QCmTVcX2rtblanpXowTV5R0Hy4014n\nT49jrEo40r4mwYoyS835Uv4ENUFA+pXicT9eUot3RSH6rYdx4A
/14UtoI9U0ol8M\n62GHpxSASQ2Kc3yQWvxRGTFslTduYM+vVmMLEDDdqcsjYnStPpwdxxmKItmbjxSv\nIwYIndp8A04WkX2iiJCciC
3BNxiLamPtYVyB1HHqbGTGirKYuSvwZt337q1OI3WH\nwVn2S4Mj/wqa4iCyGTvFSUnGq34Xkrb9XNwWBok9Tc2XWGAU/mb/xcd1hX74
GZbF\nsrZ11aPtym4kMAjU2KQi96GcAH2lnGZYoOja1J4Cs4WYx1uAx74H/m84CrYavVfl\n1ONJVLDfuZaEkSmu+jHQX15pAECNORTu
LD06PbWnOEcOi1xmbt/OT3SA3rhD2mb7\n2wxl7oJpV3ap8xGwYmxiFzmInxFJ1axjg8Rimol0mXTKAy6OdNHbCOnAwwIDAQAB\no2Mw
YTAPBgNVHRMBAf8EBTADAQH/MA4GA1UdDwEB/wQEAwIBBjAfBgNVHSMEGDAW\ngBQleng3lqGBeTrbLVuABoEmUHm1+TAdBgNVHQ4EFg
QUJXp4N5ahgXk62y1bgAaB\nJlB5tfkwDQYJKoZIhvcNAQELBQADggIBADQ9jpmVh9nyY7ZQ4s+S9RuSRYn7QsrW\nDePeMzQgh8ZtS8
WE65GY5HS61iHNP2Co8Q1lAaBWF4ipq+VZOcQbPLccHzd1kZv4\ns4u0aTzBd9ccidl73FS0DJDQOBbzPSzgsaiGHSMyGzkTeA8z3nts
SqrXXcDUvoRi\nFus/110AwdtNhJLrWveX6btYtHp9Lqe0YtNCy5AaXlrr1yRSckP5BWVtlwD4dzSO\n/dqI3wHS/ncUx9wSQomZ+Amx
YW3KtJQKgHzTqHru1x9BBk7Bzfz9FZr6HLLmEitj\nuFoDRd5TNt5LbO0zDQokvY3oqso6Htup/rS7C08mcmnelYE+yXuOc1YrlyGnpB
zk\nmy+1VYbOxRRdqKAZRbE72u/h847IVpsOvjR51iksuCAurZdp2+y2zvV8NhWekuNy\nirECRy9cb4YasjRaKi0/TCGPVSICuLyeG2
W72liCj/N2VKfjPP9zsOR5XjwCXfRg\n+9xhLy77/gov2NWXx5fzTkhxCrHOxFdLVMn0wQhksDmw6QsXzDIHSpIOypdDfnx9\nCsthx3
nhkuHLUaEP22D22dG+vImA9ukj4R/RRI/87jmi9Q8+ehH+NqN0GZZcLjdN\nSLVXpncuwWQFUDPR06wNkkkmBSXWiIYhwqSpU0Pl3er3
fD0uWvXuWPm2PzfOmUAE\nUrkzyw9XmLw0\n-----END CERTIFICATE-----\n'})

TASK [remote/ldap : Configure local-dex.tls] ***********************************************************
*****************************************
changed: [welktxef-931856-rz-le2pts6-008]

TASK [remote/ldap : Configure generic] *****************************************************************
*****************************************
changed: [welktxef-931856-rz-le2pts6-008]

TASK [remote/ldap : Configure wadcert] *****************************************************************
*****************************************
changed: [welktxef-931856-rz-le2pts6-008]

TASK [remote/ldap : Configure dex-overrides.yaml] ******************************************************
*****************************************
changed: [welktxef-931856-rz-le2pts6-008]

TASK [remote/ldap : Wait for distributed cloud synchronization] ****************************************
*****************************************
changed: [welktxef-931856-rz-le2pts6-008 -> rchltxib-c000000-003]

TASK [remote/ldap : Remove temporary working directory] ************************************************
*****************************************
changed: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/ldap : Detect oidc-auth-apps application in applying state (from a previous attempt)] *****
*****************************************
changed: [welktxef-931856-rz-le2pts6-008]

TASK [remote/ldap : Fail if oidc-auth-apps application-abort failed] ***********************************
*****************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/ldap : Detect oidc-auth-apps application in apply-failed or aborted state] ****************
*****************************************
changed: [welktxef-931856-rz-le2pts6-008]

TASK [remote/ldap : Fail if oidc-auth-apps application apply failed] ***********************************
*****************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/ldap : Apply oidc-auth-apps application] **************************************************
*****************************************
changed: [welktxef-931856-rz-le2pts6-008]

TASK [remote/ldap : Detect applied status of oidc-auth-apps application] *******************************
*****************************************
FAILED - RETRYING: Detect applied status of oidc-auth-apps application (60 retries left).
FAILED - RETRYING: Detect applied status of oidc-auth-apps application (59 retries left).
changed: [welktxef-931856-rz-le2pts6-008]

TASK [remote/ldap : Fail if oidc-auth-apps application apply failed] ***********************************
*****************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [Remote Metrics Server] ***************************************************************************
*****************************************

TASK [remote/metrics-server : Set facts - 21.05] *******************************************************
*****************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/metrics-server : Set facts - 21.12] *******************************************************
*****************************************
ok: [welktxef-931856-rz-le2pts6-008]

TASK [remote/metrics-server : Get software load status] ************************************************
*****************************************
changed: [welktxef-931856-rz-le2pts6-008]

TASK [remote/metrics-server : Noop if the system is NOT at the right caas_version] *********************
*****************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/metrics-server : Print message if system is NOT at the right caas_version] ****************
*****************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/metrics-server : Detect presence of existing application] *********************************
*****************************************
fatal: [welktxef-931856-rz-le2pts6-008]: FAILED! => {"changed": true, "cmd": ". /etc/platform/open
rc\nsystem application-show metrics-server --column status --format value\n", "delta": "0:00:01.969072",
 "end": "2024-03-14 21:13:57.596484", "msg": "non-zero return code", "rc": 1, "start": "2024-03-14 21:13
:55.627412", "stderr": "application not found: metrics-server", "stderr_lines": ["application not found:
 metrics-server"], "stdout": "", "stdout_lines": []}
...ignoring

TASK [remote/metrics-server : Print message if system already has the appication] **********************
*****************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/metrics-server : Apply again since the previous apply failed or in uploaded state] ********
*****************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/metrics-server : Wait until apply is in the applied or apply-failed state] ****************
*****************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/metrics-server : Print message if re-apply succeeds] **************************************
*****************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/metrics-server : Print message if re-apply failed] ****************************************
*****************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/metrics-server : Noop if system requires no further action or needs manual investigation] *
*****************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/metrics-server : Upload application] ******************************************************
*****************************************
changed: [welktxef-931856-rz-le2pts6-008]

TASK [remote/metrics-server : Wait until application is in the uploaded state] *************************
*****************************************
changed: [welktxef-931856-rz-le2pts6-008]

TASK [remote/metrics-server : Apply application] *******************************************************
*****************************************
changed: [welktxef-931856-rz-le2pts6-008]

TASK [remote/metrics-server : Wait until application is in the applied or apply-failed state] **********
*****************************************
FAILED - RETRYING: Wait until application is in the applied or apply-failed state (90 retries left
).
FAILED - RETRYING: Wait until application is in the applied or apply-failed state (89 retries left
).
FAILED - RETRYING: Wait until application is in the applied or apply-failed state (88 retries left
).
FAILED - RETRYING: Wait until application is in the applied or apply-failed state (87 retries left
).
changed: [welktxef-931856-rz-le2pts6-008]

TASK [remote/metrics-server : Apply again since the first apply failed] ********************************
*****************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/metrics-server : Wait again until apply is in the applied or apply-failed state] **********
*****************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/metrics-server : Print message if apply is successful] ************************************
*****************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "msg": [
        "=======================================================",
        " welktxef-d931856-008: metrics-server install SUCCEEDED! ",
        "======================================================="
    ]
}

TASK [remote/metrics-server : Print message if apply is failure] ***************************************
*****************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [Remote wrap-get-central-version] *****************************************************************
*****************************************

TASK [remote/wrap-get-central-version : Set facts for playbook] ****************************************
*****************************************
ok: [welktxef-931856-rz-le2pts6-008]

TASK [remote/wrap-get-central-version : Determine central WRA current version] *************************
*****************************************
fatal: [welktxef-931856-rz-le2pts6-008 -> rchltxib-c000000-003]: FAILED! => {"changed": true, "cmd
": ". /etc/platform/openrc\nsystem application-show wr-analytics --column app_version --format value\n",
 "delta": "0:00:01.273621", "end": "2024-03-14 21:15:08.575233", "msg": "non-zero return code", "rc": 1,
 "start": "2024-03-14 21:15:07.301612", "stderr": "application not found: wr-analytics", "stderr_lines":
 ["application not found: wr-analytics"], "stdout": "", "stdout_lines": []}
...ignoring

TASK [remote/wrap-get-central-version : Set facts for wra_target_version] ******************************
*****************************************
ok: [welktxef-931856-rz-le2pts6-008]

TASK [remote/wrap-get-central-version : debug] *********************************************************
*****************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "msg": "wra_target_version:"
}

TASK [Remote wrap-2112-2] ******************************************************************************
*****************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [Remote wrap-2106-2] ******************************************************************************
*****************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [Remote wrap-6] ***********************************************************************************
*****************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [Remote fpga-user-image] **************************************************************************
*****************************************

TASK [remote/fpga-user-image : Set facts for ansible credential - 21.05] *******************************
*****************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/fpga-user-image : Set facts for ansible credential - 21.12] *******************************
*****************************************
ok: [welktxef-931856-rz-le2pts6-008]

TASK [remote/fpga-user-image : Get software load status] ***********************************************
*****************************************
changed: [welktxef-931856-rz-le2pts6-008]

TASK [remote/fpga-user-image : Noop if the system is NOT at the right caas_version] ********************
*****************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/fpga-user-image : Print message if system is NOT at the right caas_version] ***************
*****************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/fpga-user-image : Set facts for default fpga_image_file] **********************************
*****************************************
ok: [welktxef-931856-rz-le2pts6-008]

TASK [remote/fpga-user-image : Set facts for fpga_image_file from host_vars] ***************************
*****************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/fpga-user-image : Print message if server is not LS3 cascadelake] *************************
*****************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "msg": [
        "==================================================================================",
        " Server type ZTS-LS6-pts6 is not LS3 cascadelake, no action will take place! ",
        "=================================================================================="
    ]
}

TASK [remote/fpga-user-image : Register noop because server is not LS3 cascadelake] ********************
*****************************************
changed: [welktxef-931856-rz-le2pts6-008]

TASK [remote/fpga-user-image : Check if FPGA update is stuck] ******************************************
*****************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/fpga-user-image : Abort FPGA update] ******************************************************
*****************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/fpga-user-image : include_tasks] **********************************************************
*****************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/fpga-user-image : Check FPGA update status (HPE-LS3-e910)] ********************************
*****************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/fpga-user-image : Check FPGA update status (ZTS-LS3-trtn)] ********************************
*****************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/fpga-user-image : Noop if the system has been updated] ************************************
*****************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/fpga-user-image : Print message if the system has been updated] ***************************
*****************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/fpga-user-image : In main block] **********************************************************
*****************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/fpga-user-image : Copy files to host] *****************************************************
*****************************************
skipping: [welktxef-931856-rz-le2pts6-008] => (item=20ww43.5-1x2x25G-5GLDPC-v1.6.2-3.0.1-unsigned.
bin)

TASK [remote/fpga-user-image : Do system device-image-upload] ******************************************
*****************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/fpga-user-image : debug - print UUID] *****************************************************
*****************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/fpga-user-image : Do system device-image-apply] *******************************************
*****************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/fpga-user-image : Do system host-device-image-update] *************************************
*****************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/fpga-user-image : Wait till application completed] ****************************************
*****************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/fpga-user-image : Do system device-image-state-list] **************************************
*****************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/fpga-user-image : force an error if image state is not completed] *************************
*****************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/fpga-user-image : include_tasks] **********************************************************
*****************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [Install DM Monitor] ******************************************************************************
*****************************************

TASK [common/dm-monitor : Install DM Monitor] **********************************************************
*****************************************
changed: [welktxef-931856-rz-le2pts6-008]

TASK [common/dm-monitor : Wait for DM Monitor pod created] *********************************************
*****************************************
changed: [welktxef-931856-rz-le2pts6-008]

TASK [common/dm-monitor : Wait for control-plane pods become ready] ************************************
*****************************************
changed: [welktxef-931856-rz-le2pts6-008]

TASK [common/dm-monitor : debug] ***********************************************************************
*****************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "dm_monitor_pod_ready.stdout_lines": [
        "pod/dm-monitor-7f657fd988-fkz5f condition met"
    ]
}

TASK [Proteus MWIAT - DISABLE] *************************************************************************
*****************************************

TASK [remote/zt-redfish : Update Attributes at /redfish/v1/Systems/Self/Bios/SD] ***********************
*****************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/zt-redfish : Update result] ***************************************************************
*****************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "update_result": {
        "allow": "GET, PUT, PATCH, POST",
        "changed": false,
        "connection": "close",
        "content": "",
        "cookies": {},
        "cookies_string": "",
        "date": "Thu, 14 Mar 2024 21:15:24 GMT",
        "elapsed": 1,
        "failed": false,
        "msg": "OK (unknown bytes)",
        "redirected": false,
        "server": "AMI MegaRAC Redfish Service",
        "status": 204,
        "url": "https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/Systems/Self/Bios/SD"
    }
}

TASK [Lock/unlock after MWAIT change] ******************************************************************
*****************************************

TASK [common/lock-unlock : set_fact] *******************************************************************
*****************************************
ok: [welktxef-931856-rz-le2pts6-008]

TASK [common/lock-unlock : include_tasks] **************************************************************
*****************************************
included: /home/XXXXXX/playbooks/wr-installer/roles/common/lock-unlock/tasks/lock_node.yaml for
 welktxef-931856-rz-le2pts6-008

TASK [common/lock-unlock : Check subcloud status before locking] ***************************************
*****************************************
ok: [welktxef-931856-rz-le2pts6-008]

TASK [common/lock-unlock : debug] **********************************************************************
*****************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "msg": "The host is unlocked, continue with locking."
}

TASK [common/lock-unlock : Lock subcloud] **************************************************************
*****************************************
changed: [welktxef-931856-rz-le2pts6-008]

TASK [common/lock-unlock : Pause for 10 seconds for the command to complete] ***************************
*****************************************
Pausing for 10 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [welktxef-931856-rz-le2pts6-008]

TASK [common/lock-unlock : Wait until subcloud is in locked status] ************************************
*****************************************
ok: [welktxef-931856-rz-le2pts6-008]

TASK [common/lock-unlock : Display subcloud status] ****************************************************
*****************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "host_status_new.stdout": "locked"
}

TASK [common/lock-unlock : include_tasks] **************************************************************
*****************************************
included: /home/XXXXXX/playbooks/wr-installer/roles/common/lock-unlock/tasks/unlock_node.yaml f
or welktxef-931856-rz-le2pts6-008

TASK [common/lock-unlock : Check subcloud status before unlocking] *************************************
*****************************************
ok: [welktxef-931856-rz-le2pts6-008]

TASK [common/lock-unlock : Unlock subcloud] ************************************************************
*****************************************
changed: [welktxef-931856-rz-le2pts6-008]

TASK [common/lock-unlock : Wait for node to restart (port 22 goes down)] *******************************
*****************************************
ok: [welktxef-931856-rz-le2pts6-008]

TASK [common/lock-unlock : Wait for node be back up (port 5000 comes up)] ******************************
*****************************************
ok: [welktxef-931856-rz-le2pts6-008]

TASK [common/lock-unlock : Obtain Keystone auth token] *************************************************
*****************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [common/lock-unlock : Wait for contoller-0 enabled] ***********************************************
*****************************************
FAILED - RETRYING: Wait for contoller-0 enabled (60 retries left).
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

PLAY RECAP *********************************************************************************************
*****************************************
welktxef-931856-rz-le2pts6-008 : ok=133  changed=58   unreachable=0    failed
=0    skipped=63   rescued=0    ignored=4

(ansible_2.10.15) [XXXXXX@welktxefnce
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 wr-installer]$ exit

Script done on 2024-03-14 16:45:11-05:00
[XXXXXX@welktxefnce-h-pe1util-vm01 wr-installer]$
```

### After deployment information from the Controller

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ system show
+------------------------+--------------------------------------+
| Property               | Value                                |
+------------------------+--------------------------------------+
| contact                | demo.contact@verizon.com            |
| created_at             | 2024-01-18T00:40:33.250920+00:00     |
| description            | Wind River Cloud Platform 21.05      |
| distributed_cloud_role | systemcontroller                     |
| https_enabled          | True                                 |
| latitude               | None                                 |
| location               | None                                 |
| longitude              | None                                 |
| name                   | rchltxib-c000000-003                 |
| region_name            | RegionOne                            |
| sdn_enabled            | False                                |
| security_feature       | spectre_meltdown_v1                  |
| service_project_name   | services                             |
| software_version       | 21.12                                |
| system_mode            | duplex                               |
| system_type            | Standard                             |
| timezone               | UTC                                  |
| updated_at             | 2024-01-26T23:27:36.478975+00:00     |
| uuid                   | dbdde529-5c44-414c-a95c-5a95297c22ad |
| vswitch_type           | none                                 |
+------------------------+--------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ sw-patch query
      Patch ID         RR  Release  Patch State
=====================  ==  =======  ===========
WRCP_21.05_PATCH_0001  N    21.05    Committed
WRCP_21.05_PATCH_0002  Y    21.05    Committed
WRCP_21.05_PATCH_0003  N    21.05    Committed
WRCP_21.05_PATCH_0004  N    21.05    Committed
WRCP_21.05_PATCH_0005  N    21.05     Applied
WRCP_21.05_PATCH_0006  N    21.05     Applied
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

[XXXXXX@controller-0 ~(keystone_admin)]$ dcmanager subcloud list
+----+----------------------+------------+--------------+---------------+---------+
| id | name                 | management | availability | deploy status | sync    |
+----+----------------------+------------+--------------+---------------+---------+
|  6 | welktxef-d931856-008 | managed    | online       | complete      | in-sync |
+----+----------------------+------------+--------------+---------------+---------+
[XXXXXX@controller-0 ~(keystone_admin)]$ dcmanager subcloud show welktxef-d931856-008
+-----------------------------+---------------------------------+
| Field                       | Value                           |
+-----------------------------+---------------------------------+
| id                          | 6                               |
| name                        | welktxef-d931856-008            |
| description                 | Wind River Cloud Platform 21.12 |
| location                    | welktxef-d931856-008            |
| software_version            | 21.12                           |
| management                  | managed                         |
| availability                | online                          |
| deploy_status               | complete                        |
| management_subnet           | 2607:f160:10:80bb::/64          |
| management_start_ip         | 2607:f160:10:80bb:ce:40a::      |
| management_end_ip           | 2607:f160:10:80bb:ce:40a:0:f    |
| management_gateway_ip       | 2607:f160:10:80bb:ce:23::       |
| systemcontroller_gateway_ip | 2607:f160:0:3048:cd:28::        |
| group_id                    | 1                               |
| created_at                  | 2024-03-14 19:55:11.704759      |
| updated_at                  | 2024-03-14 21:32:00.284697      |
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

### Subcloud deployment had no isue, marking test as a pass
