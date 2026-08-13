# ZT .43 BMC firmware validation
# New deploy of sublcoud on 21.12p10
# 8/25/23 James Patchett

## Build and setup of environment

## Target Controller Rchltxfe-c000000-001
Controller-0 iLO 2607:f160:a:d02e:cd:fe0::8000 
Controller-1 iLO 2607:f160:a:d02e:cd:fe0::8001
Worker-0 iLO 2607:f160:a:d02e:cd:fe0::8002 
OAM 2607:f160:0:3043:cd:290:0:10



## Target Subcloud welktxef-d931887-021 (currently on controller 2607:f160:0:3049:cd:290:0:10 )
iLO 2607:f160:10:9249:ce:40a:0:e015
OAM 2607:f160:10:9249:ce:40a:0:f409

host_vars welktxef-931887-rz-le2pts6-021
inventory welktxef-d931887-021.yaml

ipmitool -I lanplus -U XXXXXX -P XXXXXX -H 2607:f160:10:9249:ce:40a:0:e015 sol activate



## Baseline record of controller and subcloud
### Controller:

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ system show
+------------------------+--------------------------------------+
| Property               | Value                                |
+------------------------+--------------------------------------+
| contact                | demo.engineer@verizon.com              |
| created_at             | 2023-08-26T04:43:17.345039+00:00     |
| description            | Wind River Cloud Platform 21.05      |
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
| software_version       | 21.12                                |
| system_mode            | duplex                               |
| system_type            | Standard                             |
| timezone               | UTC                                  |
| updated_at             | 2023-09-12T01:10:47.235770+00:00     |
| uuid                   | 85d98699-635d-490f-ae18-ba3302ed8605 |
| vswitch_type           | none                                 |
+------------------------+--------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ system application-list
+--------------------------+----------+-----------------------------------+----------------------------------------+----------+-------------------------------------------------------------------------+
| application              | version  | manifest name                     | manifest file                          | status   | progress                                                                |
+--------------------------+----------+-----------------------------------+----------------------------------------+----------+-------------------------------------------------------------------------+
| cert-manager             | 21.12-28 | cert-manager-manifest             | certmanager-manifest.yaml              | applied  | completed                                                               |
| nginx-ingress-controller | 21.12-18 | nginx-ingress-controller-manifest | nginx_ingress_controller_manifest.yaml | applied  | Application update from version 21.05-16 to version 21.12-18 completed. |
| oidc-auth-apps           | 21.12-61 | oidc-auth-manifest                | manifest.yaml                          | applied  | completed                                                               |
| platform-integ-apps      | 21.12-46 | platform-integration-manifest     | manifest.yaml                          | uploaded | completed                                                               |
| rook-ceph-apps           | 1.0-5    | rook-ceph-manifest                | manifest.yaml                          | uploaded | completed                                                               |
+--------------------------+----------+-----------------------------------+----------------------------------------+----------+-------------------------------------------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ sw-patch query
      Patch ID         RR  Release  Patch State
=====================  ==  =======  ===========
WRCP_21.05_PATCH_0001  N    21.05    Committed
WRCP_21.05_PATCH_0002  Y    21.05    Committed
WRCP_21.05_PATCH_0003  N    21.05    Committed
WRCP_21.05_PATCH_0004  N    21.05    Committed
WRCP_21.05_PATCH_0005  N    21.05    Committed
WRCP_21.05_PATCH_0006  N    21.05    Committed
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

[XXXXXX@controller-0 ~(keystone_admin)]$ fm alarm-list
+-------+---------------------------------------------------+-----------------------+----------+-------------+
| Alarm | Reason Text                                       | Entity ID             | Severity | Time Stamp  |
| ID    |                                                   |                       |          |             |
+-------+---------------------------------------------------+-----------------------+----------+-------------+
| 280.  | welktxef-d931887-021 kubernetes sync_status is    | subcloud=             | major    | 2023-09-12T |
| 002   | out-of-sync                                       | welktxef-d931887-021. |          | 23:33:53.   |
|       |                                                   | resource=kubernetes   |          | 261828      |
|       |                                                   |                       |          |             |
+-------+---------------------------------------------------+-----------------------+----------+-------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ dcmanager subcloud list
+----+----------------------+------------+--------------+---------------+-------------+
| id | name                 | management | availability | deploy status | sync        |
+----+----------------------+------------+--------------+---------------+-------------+
|  1 | welktxef-d931887-021 | managed    | online       | complete      | out-of-sync |
+----+----------------------+------------+--------------+---------------+-------------+
[XXXXXX@controller-0 ~(keystone_admin)]$

```

### Subcloud firmware query shows .43, we can now continue with deployment automation 
### Also setting MWAIT enabled for the deployment since this is a ZT proteus
```log
[XXXXXX@welktxefnce-h-pe1util-vm01 inventory]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/UpdateService/FirmwareInventory/BMC | jq

{
  "@odata.context": "/redfish/v1/$metadata#SoftwareInventory.SoftwareInventory",
  "@odata.etag": "\"1694561301\"",
  "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/BMC",
  "@odata.type": "#SoftwareInventory.v1_2_3.SoftwareInventory",
  "Id": "BMC",
  "Name": "BMC",
  "Updateable": true,
  "Version": "0.43.00"
}
[XXXXXX@welktxefnce-h-pe1util-vm01 inventory]$

[XXXXXX@welktxefnce-h-pe1util-vm01 inventory]$ curl -k -w "\\n%{http_code} %{url_effective}\\n" -u XXXXXX:XXXXXX -H "Content-Type: application/json" -d '{"Attributes": {"PMS012": "Enable"}}' -X PATCH https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Systems/Self/Bios/SD

204 https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Systems/Self/Bios/SD
[XXXXXX@welktxefnce-h-pe1util-vm01 inventory]$ curl -u XXXXXX:XXXXXX -ks https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Systems/Self/Bios | jq '.Attributes.PMS012'
"Enable"
[XXXXXX@welktxefnce-h-pe1util-vm01 inventory]$

```


### deploying subcloud with 21.12p10 through Ansible server

```log
[XXXXXX@welktxefnce-h-pe1util-vm01 wr-installer]$ ansible-playbook --vault-password-file /tmp/vault-pass -i inventory/welktxef-d931887-021.yaml wr_remote.yaml

PLAY [Wind River Remote Subcloud Installer] ****************************************************************************************************

TASK [Download Files] **************************************************************************************************************************

TASK [common/download_files : Check if artifact files exist locally] ***************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [common/download_files : Download & unarchive artifact files to local directory if they don't exist] **************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [Setup] ***********************************************************************************************************************************

TASK [common/setup : Create temporary working directory] ***************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [common/setup : Set temporary working directory path] *************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [Remote Configure] ************************************************************************************************************************

TASK [remote/remote-configure : Set facts for vip, ansible, and wr_admin] **********************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Set facts for wr_release_version] ******************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Print wr_release_version] **************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "msg": "wr_release_version: 21.12"
}

TASK [remote/remote-configure : Set fact wr_distribution_directory to use based on WR version] *************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Set fact wr_distribution_directory to use based on WR version] *************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Set facts for which image list to use based on WR version] *****************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Set facts for which image list to use based on WR version] *****************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Set facts for which image list to use based on WR version] *****************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Print wr_image_list] *******************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "msg": "wr_image_list: /opt/external/vcpfe-team/artifacts/WRCP-2112/wind-river-cloud-platform-container-images-list-21.12.txt"
}

TASK [remote/remote-configure : Set fact to wr_license_key] ************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Set fact to wr_license_key] ************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : print wr_license_key] ******************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "msg": "wr_license_key = IyBXaW5kIFJpdmVyIFByb2R1Y3QgQWN0aXZhdGlvbiBGaWxlIChpbnN0YWxsLnR4dCkKIyBJc3N1ZWQgZm9yIGhvc3Q6IDxWZXJpem9uPiA8VmVyaXpvbj4gPEFueT4KIyBMaWNlbnNlIG51bWJlcihzKTogNjgyMzc0CiMgSXNzdWVkIG9uOiAyNi1qYW4tMjAyMiAwOTo1MDo1MAojCiMgTm90ZTogdGhpcyBsaWNlbnNlIGlzIGdlbmVyYXRlZCBjdW11bGF0aXZlbHkgZm9yIGFsbAojIFdpbmQgUml2ZXIgc29mdHdhcmUgbWFuYWdlZCBieSB0aGlzIGhvc3QuCgojIDEuIEZsZXhMTSBsaWNlbnNlIGZpbGU6CiMgQmVnaW46IFNlcnZlciBsaWNlbnNlICAtLS0tLS0tLS0tLS0tLS0tLS0tLS0KIyBTZXJpYWwgTnVtYmVyOiA2ODQ0NDktVmVyaXpvblBPQy1HNFdEQzlDUEVLCgpQQUNLQUdFIFdSQ1BfQ09OVEFJTkVSX1BLRyB3cnNkIDIxIDAwNDY1REZDRUI5QiBcCglDT01QT05FTlRTPVdSQ1BfQ09OVEFJTkVSOjIxLjEyIE9QVElPTlM9U1VJVEUgXAoJU0lHTj0yNTAwQzhCMjRFRDAKSU5DUkVNRU5UIFdSQ1BfQ09OVEFJTkVSX1BLRyB3cnNkIDIxIHBlcm1hbmVudCB1bmNvdW50ZWQgNDQyRThBMzg2QUE4IFwKCVZFTkRPUl9TVFJJTkc9PGxuPjY4MjM3NDwvbG4+PHBzPjIyMTMtNDM8L3BzPiBIT1NUSUQ9QU5ZIFwKCUlTU1VFRD0yNi1qYW4tMjAyMiBTTj1zZXJpYWwtVmVyaXpvbi1MVjJJV0FVTEVCIFwKCVNUQVJUPTI2LWphbi0yMDIyIFNJR049QjUzNzk2OTBENEE2Cg=="
}

TASK [remote/remote-configure : Copy storage checking script if server is HPE-LS3-e910] ********************************************************
skipping: [welktxef-931887-rz-le2pts6-021] => (item=hpe_storage_check.py)

TASK [remote/remote-configure : Execute storage checking script if server is HPE-LS3-e910] *****************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor HPE HPE-LS3-e910 (4 disks)] *****************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor HPE HPE-LS3-e910 (2 disks)] *****************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor HPE HPE-LS3-92s3] ***************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor HPE HPE-LS6-92s6] ***************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor ZTS ZTS-LS3-trtn] ***************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Set facts for Corning] *****************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor ZTS ZTS-LS6-pts6 & ZTS-LS3-pts3] ************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor ZTS ZTS-LS6-aks6 & ZTS-LS3-aks3] ************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : set_fact] ******************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [include_role : remote/zt-redfish] ********************************************************************************************************

TASK [remote/zt-redfish : get content from /redfish/v1/Systems/Self] ***************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/zt-redfish : Extract and store BiosVersion from returned content] *****************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Set facts for BIOS version based on vendor ZTS ZTS-LS6-pts6 & ZTS-LS3-pts3] ************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : debug] *********************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "bios_version": "0.23"
}

TASK [remote/remote-configure : Find out which DM Docker version contral has] ******************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001]

TASK [remote/remote-configure : Find out which DM file version contral has] ********************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001]

TASK [remote/remote-configure : Print dm docker version and dm file version] *******************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "msg": "dm_docker_version: WRCP_21.12-wrs.4, dm_file: wind-river-cloud-platform-deployment-manager-2.0.8-4.tgz"
}

TASK [remote/remote-configure : Discover Wind River docker image names] ************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-configure : Print local_images_full] ***************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "msg": "docker.io/starlingx/ceph-config-helper:v1.15.0\ndocker.io/starlingx/dex:stx.4.0-v2.14.0-1\ndocker.io/starlingx/n3000-opae:stx.6.0-v1.0.1\ndocker.io/starlingx/stx-oidc-client:stx.5.0-v1.0.4\ndocker.io/wind-river/cloud-platform-deployment-manager:WRCP_21.12-wrs.4\ngcr.io/google_containers/kubernetes-dashboard-init-amd64:v1.0.0\ngcr.io/kubebuilder/kube-rbac-proxy:v0.4.0\nquay.io/external_storage/rbd-provisioner:v2.1.1-k8s1.11"
}

TASK [remote/remote-configure : Create fact for Wind River docker image names] *****************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Determine DM Helm Chart path] **********************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-configure : Print dm_helm_chart] *******************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "msg": "/opt/external/vcpfe-team/artifacts/WRCP-2112/wind-river-cloud-platform-deployment-manager-2.0.8-4.tgz"
}

TASK [remote/remote-configure : Set DM Helm Chart file] ****************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Lookup Deployment Manager image tag] ***************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-configure : Lookup RBAC Proxy image tag] ***********************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-configure : Copy WRCP DM Playbook] *****************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001] => (item=wind-river-cloud-platform-deployment-manager.yaml)
ok: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001] => (item=wind-river-cloud-platform-deployment-manager-2.0.8-4.tgz)

TASK [remote/remote-configure : Set a fact for the central controller VIP address] *************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Configure WRCP seed template] **********************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001] => (item={'src': 'bootstrap-values.yaml', 'dest': 'welktxef-d931887-021-bootstrap-values.yaml'})
ok: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001] => (item={'src': 'deploy-values.yaml', 'dest': 'welktxef-d931887-021-deploy-values.yaml'})
changed: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001] => (item={'src': 'deploy-standard.yaml', 'dest': 'welktxef-d931887-021-deploy-standard.yaml'})
ok: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001] => (item={'src': 'install-values.yaml', 'dest': 'welktxef-d931887-021-install-values.yaml'})

TASK [remote/remote-configure : Copy SSL cert files] *******************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001] => (item={'filename': 'k8s_root_ca_cert.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIF8jCCA9qgAwIBAgIJAIf9Ql2uDZh+MA0GCSqGSIb3DQEBDQUAMIGFMQswCQYD\nVQQGEwJVUzEOMAwGA1UECAwFVGV4YXMxETAPBgNVBAcMCFdlc3RsYWtlMR0wGwYD\nVQQKDBRWZXJpem9uIFNvdXJjaW5nIExMQzE0MDIGA1UEAwwrVmVyaXpvbiBOZXR3\nb3JrIFdFTEtUWElCIExBQiAxIDMgUlNBIEs4UyBDQTAeFw0yMDEwMjUyMjEyNDha\nFw0zMDEwMjMyMjEyNDhaMIGFMQswCQYDVQQGEwJVUzEOMAwGA1UECAwFVGV4YXMx\nETAPBgNVBAcMCFdlc3RsYWtlMR0wGwYDVQQKDBRWZXJpem9uIFNvdXJjaW5nIExM\nQzE0MDIGA1UEAwwrVmVyaXpvbiBOZXR3b3JrIFdFTEtUWElCIExBQiAxIDMgUlNB\nIEs4UyBDQTCCAiIwDQYJKoZIhvcNAQEBBQADggIPADCCAgoCggIBAKyF9svdv/qG\n7HxBr1DWvZ3CQiDsA4m1kj0hD7jo3B3W/32ODcPpgeNmp4Oful0SsndpqEGhXDq5\noiBfqszMUpzDgdQ7siIHekb2olFEK2KniMP3H53nilIppeyMby5K3ZwF0Qbmk5WK\ncoXoYegP+Uv9bV0AMH6Dn4CVgYrLAYfmPyGgUSt4vuZ9F/rf9UkBf/DcZGqMnMax\n/Gfaq8KwmDzD9D8IVCHPrM5f4+CaKMQCFu5QkSsLYJFRiuQWWaICMMdnqpb0HZh5\niPnCSHwPPUyXxtujdI97Ovy4X5WR46jJ2+KzPYe8tVa/DL3TlKmRL9AF+oSE17bw\nzGAE7GNWxPojebHIUuoKdOQC1qiJBVS+c14r9+9P2Uy6XEhNUs+h3juRI4U3YkQ1\nUCUU3opqhOPh4jUIuPGg5aX07lt4Wpxc48D+CY1D4i6vaJLl3WCsVK7PFwWVQQEW\nIQabfuj1R2jEu7pp2Yabza58S00v1P5/kv/DNr7ADm8eYRvxLAAXCedMeSDXKBgd\npPmVXXZoZ8+X8VRGYxcw0mBBLIAiTOntT2vgLeq5T3QyiVKdU6TLAYEjS65QZ3Eg\naIX0wRqlcQI7lruTXubtENG6wWXYtnDf5795ZID1YIEqkgzZLMBqq1SBiLnWd6aK\n78Zsr4j5GmTBGpKRmwE2oO1btJCCYyG5AgMBAAGjYzBhMA8GA1UdEwEB/wQFMAMB\nAf8wHQYDVR0OBBYEFEDQ5EaGp3x02WUuvqetygqpM3dCMB8GA1UdIwQYMBaAFEDQ\n5EaGp3x02WUuvqetygqpM3dCMA4GA1UdDwEB/wQEAwICpDANBgkqhkiG9w0BAQ0F\nAAOCAgEAeCMxVJr5Jyg87DVaUtEhiWfhto993ENrnevAGqrBOoRc/KU1/C3paqhR\nsvr2r2LR+npSmeo6iz0FaO31XwHSHX95+XJeGP5Q8TGddbRiTglQsMfOkGNzxqgg\nTkdZ8A1y9v2jprONUmLADVGIVT0AoHc7V9w1I8NKhrY+rIllum4FRDiDPSnImh5h\nxmH+Nq2ZuEFVdtV/oNKzEu2ywmbgBRd5Jv3rTejxltmTZtyq8IKoKguj3NVFn93Q\nU4TbsxkcAdrLMooLYYDRTWA4t0iqKM/UkYUg4xl2l9NrY7ZUbaNd5+YsLNdqXO/c\nmp7wyMv/8ZIy1BLG4zJmX/JzWkYmULqQ+A+21+YuqrV3a81V7vcHhJcRaPOrg5cd\nYwY2eCbXMvNOdrzppIglUrlddNuqAhs1MTi/VibxYuI9isU0JckXIcCy1L+xbEda\n6v/z6wSrScVz0I4m0DpK6xMQ8t9sLcrGp5uGbj6J4nQWd+QLdq6kmAzDOZ/Gs0wb\nPYdkER4dXAVcioYFekpKv7d+nur0FPtMNIw0OdhX2eAwC22IFAq2DZRjUFvaBGaD\ni1ptfq6P1mVJ2T/exYujEDtq+8yQTfWgFm/DjEfWtcCp0Jukgv8opLR2DpCf5Ucq\nd5X7d/DP0mukJ3vZ8EIqYorwZJ1L1a2jgngjA+gPxIaW+JHfTHU=\n-----END CERTIFICATE-----\n'})
ok: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001] => (item={'filename': 'k8s_root_ca_key.pem', 'value': '-----BEGIN PRIVATE KEY-----\nMIIJQQIBADANBgkqhkiG9w0BAQEFAASCCSswggknAgEAAoICAQCshfbL3b/6hux8\nQa9Q1r2dwkIg7AOJtZI9IQ+46Nwd1v99jg3D6YHjZqeDn7pdErJ3aahBoVw6uaIg\nX6rMzFKcw4HUO7IiB3pG9qJRRCtip4jD9x+d54pSKaXsjG8uSt2cBdEG5pOVinKF\n6GHoD/lL/W1dADB+g5+AlYGKywGH5j8hoFEreL7mfRf63/VJAX/w3GRqjJzGsfxn\n2qvCsJg8w/Q/CFQhz6zOX+PgmijEAhbuUJErC2CRUYrkFlmiAjDHZ6qW9B2YeYj5\nwkh8Dz1Ml8bbo3SPezr8uF+VkeOoydvisz2HvLVWvwy905SpkS/QBfqEhNe28Mxg\nBOxjVsT6I3mxyFLqCnTkAtaoiQVUvnNeK/fvT9lMulxITVLPod47kSOFN2JENVAl\nFN6KaoTj4eI1CLjxoOWl9O5beFqcXOPA/gmNQ+Iur2iS5d1grFSuzxcFlUEBFiEG\nm37o9UdoxLu6admGm82ufEtNL9T+f5L/wza+wA5vHmEb8SwAFwnnTHkg1ygYHaT5\nlV12aGfPl/FURmMXMNJgQSyAIkzp7U9r4C3quU90MolSnVOkywGBI0uuUGdxIGiF\n9MEapXECO5a7k17m7RDRusFl2LZw3+e/eWSA9WCBKpIM2SzAaqtUgYi51nemiu/G\nbK+I+RpkwRqSkZsBNqDtW7SQgmMhuQIDAQABAoICACysO62qa+2pRk8eixD5qfvR\ns2Hm+zuLYqSljPaqhWTMqTePswzJyDJkAHhawd0b3E6Dc2gbKlCihNKxMv744WNq\nVJHqK0QYf5ckgf9dEYboLsffk7ZFoFGKK0bHTnrENAIUl32b8xdD1EfMVp3KlRkS\nNGFijSwVVRXsoLCZxHm2Kx6/7oS9LWFtfuodV9xhoQlzaCUW5/mjWOJjgxpUs/b4\nHqS7uV1P80U1G0KraGboy5tGDXEB7y1x2e8Zwnfq7UqVE10nNQqoXcmefzpwj8Tn\ngDybZLFKjYmnDEkkj7jDHEbldsdRG/usWNZGlTYbPDA3fBkYdOsQCzvJypQmgbZ+\n3yk3Lj2+9vLEMfPrruuzyOSXgki6o5uvy7Je6PdBpsz75k8FH6a+Rw3vvP8HuP3S\nLSUYm3tyOheXHR7BKN4bnfi11RAWvDpT9S+QnZ+R8DmQzOADlnjRC8WewDJYoNJ1\np1jeuqswlxo144oMO92cmdS2dAbPvS6aQP1I85Q2NniY+6YhHkBwIQIlfVs1JPbY\nX7QtTy1IXQhR3sospyvUwY2GPSAeVHDRL53ClQKDsvWpSy0MAmWYJkZu1P+jKBim\nj34ytApgG65Hv/RHf3L4+4zzItZ3TN2tJ/g9EKc6oMNtqKbbG56kkmvRPWKtMGV8\nFqxCvG5NydUK7fN+P2WJAoIBAQDXLFC//Fn9ed1U+pKa2M25aJwEetkGLXQvkwVi\n8uJFaXITb2ceveSEo6iBExyn4eYL5A4X+RZdJJdRRbj4whsNN13Pm+6lYX3pp7MN\nO+78uvwVfKZiWPFKfZs7ZH1/O9VIlLGnXUHeaHK1tmv9ixxMixdnjUDkcVa0O3qT\nKBLpvXnVEMYizxQBN0P5Z9QvQQGpUhKnNw+FhV1SP+YHxrB0Pu6qbYAmZZC2MQc1\nTsDyqGjmHk9VJaFYAAPEjqACDbfnkVUCj0ylM4xPQuBJs9DOKh4InG+znusdmd8H\nmvoEFDppsrH1NhO6GTeuCk6n0WBi6cUm76K/gPscYyV4ZtkfAoIBAQDNQgDXtfqv\nxbAhvDk0o/P8fqOdgQF0uFTqYHmyW31Ty9nF0ptA8LVJOIljU3zlLplhIFjBnSEG\nLqu4jnLLRR+zej0MXmJuZ9BMWmQeTrZzttnH5bn54E07DPJ5BvFoTMJNklBiXjB5\n5hTPZS4yK1KjoxY+Ypnj4W1iZjP37ya/A34J2nlYtoW4LdVfJHqCxBXel9Nz2zkv\nvwwPu8Eu7gFLuhNQM6Iv4mORGI8yg7Y/BwodfDPRuFvrG1KXkjwASb0O5b1suRQy\n9H80q5EAbT36K1z48ilr8fcroN+hV8g4yntrBBgOHPMmBk/vHKU8B1rkBr0p2haI\n3PwKmDFRsDInAoIBAGrjjMmSZnHQk+6e+y0I/klYegiPrjevZMQtWMOqvFSW6SBW\nevd+hYKOeiqEf/u18D1/8LBgAIgMoU6yQAzy/9U059k2MPrez1m/AOdWGoZZrNhP\nr6ezX0oN04tRhDYsVutTUl09qnb9k95I3KR68nfjsKC0PsQ8uUGXOnDXu215vofl\naUfpbpqcBZxjw7glptmh97oxU/iUI6O0MmUygn18tbrb4okwcw7OlDIbCSaCGnoW\nHHrD0r6QY07FOx9KCU1zmLNI1F5MmSrWoex68wM3UOweKi8khs+RnIV+qyxTkCDp\nsBWL44jS9iHy5Nfg3uzEDDgnWsWfIR8c8YQ6MykCggEADr0ollTI9Yo6hZGggfkr\n8fueABddZWY/Ir1ev8H2E+hVcPEYmOcv/VwD8Y/zLfnUpbbO6MhBsNH1HsGL2LDT\n/+1NKPA2HTtzJ6ht/Acm7tQ4ezQx0JGcuhrJ5orrFtQ8N5nED+w3iulMoT/gu1WF\nD58MX9pwtn5ffmtcW/deTuUPTeHUSNyCaaFQ6w4RhgZSk7NPSch6KMWNNiwDST1p\n9mgcLuwmP04AXFDpJ3VxxsDYpxleFzcn0pAZtCyaBmNFIia5HW+E1cvcvol7Vg6C\nHs6yVGX/N3MejpF0vX8yL3HKvvqCR7EofJiDcOYbr13P1wPs3W59o8JKjvAyymze\njQKCAQAUY/0asRL33D7tFoIbLg/N9hi+tCCM35DMf2FeXm3QwSkAR/BJw0ewCE5C\n+VqukHN3/i0Xe8KSHwEuLK2sGLk9Ys8A5NytjqFApYwpIk8UrRONfC12H3ez5VYk\nJlhMVhVXEZvVhEFJiBC7q6x6s7BVtLTGV7FA5CW8YKBhwHwrpm+h/Xb798oaKyel\nP/xYq+GZzfWfbvUjZvgN0J0RGxKA+GRgsmhoyOfgCVXgSzuUkI+9cAUvC0OV407L\n4XIK0GDJ7Tv/2USSPfmueyGEmacc/oYUPVBUgeINSoaCM4cpZwyLylVEtKOdQoEE\n77G5mvQsoXxsMjd+nbHil450UHsL\n-----END PRIVATE KEY-----\n'})

TASK [Proteus MWIAT - ENABLE] ******************************************************************************************************************

TASK [remote/zt-redfish : Update Attributes at /redfish/v1/Systems/Self/Bios/SD] ***************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/zt-redfish : Update result] *******************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "update_result": {
        "allow": "GET, PUT, PATCH, POST",
        "changed": false,
        "connection": "close",
        "content": "",
        "cookies": {},
        "cookies_string": "",
        "date": "Thu, 14 Sep 2023 22:15:55 GMT",
        "elapsed": 1,
        "failed": false,
        "msg": "OK (unknown bytes)",
        "redirected": false,
        "server": "AMI MegaRAC Redfish Service",
        "status": 204,
        "url": "https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Systems/Self/Bios/SD"
    }
}

TASK [Remote Install] **************************************************************************************************************************

TASK [remote/remote-install : Check if the subcloud deployed but failed] ***********************************************************************
fatal: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001]: FAILED! => {"changed": true, "cmd": ". /etc/platform/openrc\ndcmanager subcloud show welktxef-d931887-021 --column \"deploy_status\" --format value\n", "delta": "0:00:01.189803", "end": "2023-09-14 22:15:58.085712", "msg": "non-zero return code", "rc": 1, "start": "2023-09-14 22:15:56.895909", "stderr": "ERROR (app) Subcloud not found", "stderr_lines": ["ERROR (app) Subcloud not found"], "stdout": "", "stdout_lines": []}
...ignoring

TASK [remote/remote-install : debug] ***********************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "msg": "subcloud_status:"
}

TASK [remote/remote-install : Delete the subcloud that's 'install-failed' & 'pre-install-failed'] **********************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-install : Deploy remote cloud] *********************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001]

TASK [remote/remote-install : 1st polling prep: Obtain Keystone auth token] ********************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-install : 1st polling: Wait for subcloud to start installing OS] ***********************************************************
FAILED - RETRYING: 1st polling: Wait for subcloud to start installing OS (40 retries left).
FAILED - RETRYING: 1st polling: Wait for subcloud to start installing OS (39 retries left).
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-install : 1st polling result: Fail if the installation failed] *************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-install : 2nd polling prep: Obtain Keystone auth token] ********************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-install : 2nd polling: Wait for subcloud to install OS (this will take a while)] *******************************************
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (100 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (99 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (98 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (97 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (96 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (95 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (94 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (93 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (92 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (91 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (90 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (89 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (88 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (87 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (86 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (85 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (84 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (83 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (82 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (81 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (80 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (79 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (78 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (77 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (76 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (75 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (74 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (73 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (72 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (71 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (70 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (69 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (68 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (67 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (66 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (65 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (64 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (63 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (62 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (61 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (60 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (59 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (58 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (57 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (56 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (55 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (54 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (53 retries left).
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-install : 2nd polling result: Fail if any error occurred] ******************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-install : 3rd polling prep: Obtain Keystone auth token] ********************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-install : 3rd polling: Wait for subcloud to install OS (this may take a while)] ********************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-install : 3rd polling result: Fail if any error occurred] ******************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-install : 4th polling prep: Obtain Keystone auth token] ********************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-install : 4th polling: Wait for subcloud to install OS (this may still take a while)] **************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-install : 4th polling result: Fail if the installation failed] *************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-install : 5th polling prep: Obtain Keystone auth token] ********************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-install : 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while)] *************************
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (100 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (99 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (98 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (97 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (96 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (95 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (94 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (93 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (92 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (91 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (90 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (89 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (88 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (87 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (86 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (85 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (84 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (83 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (82 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (81 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (80 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (79 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (78 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (77 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (76 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (75 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (74 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (73 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (72 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (71 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (70 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (69 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (68 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (67 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (66 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (65 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (64 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (63 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (62 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (61 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (60 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (59 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (58 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (57 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (56 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (55 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (54 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (53 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (52 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (51 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (50 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (49 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (48 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (47 retries left).
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-install : 5th polling result: Fail if bootstrap/deploy failed] *************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-install : 6th polling prep: Obtain Keystone auth token] ********************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-install : 6th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while)] *************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-install : 6th polling result: Fail if bootstrap/deploy failed] *************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-install : Wait for controller-0 restart] ***********************************************************************************
FAILED - RETRYING: Wait for controller-0 restart (40 retries left).
FAILED - RETRYING: Wait for controller-0 restart (39 retries left).
FAILED - RETRYING: Wait for controller-0 restart (38 retries left).
fatal: [welktxef-931887-rz-le2pts6-021]: FAILED! => {"attempts": 4, "changed": false, "elapsed": 5, "msg": "timed out waiting for ping module test success: Failed to connect to the host via ssh: ssh: connect to host 2607:f160:10:9249:ce:40a:0:f409 port 22: Connection refused"}
...ignoring

TASK [remote/remote-install : Wait for controller-0 recovery] **********************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-install : setup kdump] *****************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [Remote Cleanup] **************************************************************************************************************************

TASK [common/cleanup : Remove temporary working directory] *************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [Remote Manage] ***************************************************************************************************************************

TASK [remote/manage : 1st Obtain Keystone auth token] ******************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/manage : 1st Wait for contoller-0 availability status online] *********************************************************************
FAILED - RETRYING: 1st Wait for contoller-0 availability status online (100 retries left).
FAILED - RETRYING: 1st Wait for contoller-0 availability status online (99 retries left).
FAILED - RETRYING: 1st Wait for contoller-0 availability status online (98 retries left).
FAILED - RETRYING: 1st Wait for contoller-0 availability status online (97 retries left).
FAILED - RETRYING: 1st Wait for contoller-0 availability status online (96 retries left).
FAILED - RETRYING: 1st Wait for contoller-0 availability status online (95 retries left).
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/manage : 2nd Obtain Keystone auth token] ******************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/manage : 2nd Wait for contoller-0 availability status online] *********************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/manage : Wait for system to stabilize before running kubectl] *********************************************************************
Pausing for 480 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [welktxef-931887-rz-le2pts6-021]

TASK [Wait for distributed cloud to be reconciled] *********************************************************************************************

TASK [common/wait_for_reconciliation : Making sure node is reachable] **************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [common/wait_for_reconciliation : Wait for K8s API to be up] ******************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [common/wait_for_reconciliation : Wait for hosts to be reconciled] ************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [common/wait_for_reconciliation : Wait for systems to be reconciled] **********************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/manage : Wait for distributed cloud to be reconciled but subcloud OAM VIP becomes unreachable] ************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/manage : Check if the subcloud deployed but failed] *******************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001]

TASK [remote/manage : Set distributed cloud state to managed] **********************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001]

TASK [remote/manage : Wait for system to stabilize] ********************************************************************************************
Pausing for 300 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [welktxef-931887-rz-le2pts6-021]

TASK [Remote Trust] ****************************************************************************************************************************

TASK [remote/trust : Create temporary working directory] ***************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/trust : Copy SSL cert files to working dir] ***************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost] => (item={'filename': 'k8s_root_ca_cert.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIF8jCCA9qgAwIBAgIJAIf9Ql2uDZh+MA0GCSqGSIb3DQEBDQUAMIGFMQswCQYD\nVQQGEwJVUzEOMAwGA1UECAwFVGV4YXMxETAPBgNVBAcMCFdlc3RsYWtlMR0wGwYD\nVQQKDBRWZXJpem9uIFNvdXJjaW5nIExMQzE0MDIGA1UEAwwrVmVyaXpvbiBOZXR3\nb3JrIFdFTEtUWElCIExBQiAxIDMgUlNBIEs4UyBDQTAeFw0yMDEwMjUyMjEyNDha\nFw0zMDEwMjMyMjEyNDhaMIGFMQswCQYDVQQGEwJVUzEOMAwGA1UECAwFVGV4YXMx\nETAPBgNVBAcMCFdlc3RsYWtlMR0wGwYDVQQKDBRWZXJpem9uIFNvdXJjaW5nIExM\nQzE0MDIGA1UEAwwrVmVyaXpvbiBOZXR3b3JrIFdFTEtUWElCIExBQiAxIDMgUlNB\nIEs4UyBDQTCCAiIwDQYJKoZIhvcNAQEBBQADggIPADCCAgoCggIBAKyF9svdv/qG\n7HxBr1DWvZ3CQiDsA4m1kj0hD7jo3B3W/32ODcPpgeNmp4Oful0SsndpqEGhXDq5\noiBfqszMUpzDgdQ7siIHekb2olFEK2KniMP3H53nilIppeyMby5K3ZwF0Qbmk5WK\ncoXoYegP+Uv9bV0AMH6Dn4CVgYrLAYfmPyGgUSt4vuZ9F/rf9UkBf/DcZGqMnMax\n/Gfaq8KwmDzD9D8IVCHPrM5f4+CaKMQCFu5QkSsLYJFRiuQWWaICMMdnqpb0HZh5\niPnCSHwPPUyXxtujdI97Ovy4X5WR46jJ2+KzPYe8tVa/DL3TlKmRL9AF+oSE17bw\nzGAE7GNWxPojebHIUuoKdOQC1qiJBVS+c14r9+9P2Uy6XEhNUs+h3juRI4U3YkQ1\nUCUU3opqhOPh4jUIuPGg5aX07lt4Wpxc48D+CY1D4i6vaJLl3WCsVK7PFwWVQQEW\nIQabfuj1R2jEu7pp2Yabza58S00v1P5/kv/DNr7ADm8eYRvxLAAXCedMeSDXKBgd\npPmVXXZoZ8+X8VRGYxcw0mBBLIAiTOntT2vgLeq5T3QyiVKdU6TLAYEjS65QZ3Eg\naIX0wRqlcQI7lruTXubtENG6wWXYtnDf5795ZID1YIEqkgzZLMBqq1SBiLnWd6aK\n78Zsr4j5GmTBGpKRmwE2oO1btJCCYyG5AgMBAAGjYzBhMA8GA1UdEwEB/wQFMAMB\nAf8wHQYDVR0OBBYEFEDQ5EaGp3x02WUuvqetygqpM3dCMB8GA1UdIwQYMBaAFEDQ\n5EaGp3x02WUuvqetygqpM3dCMA4GA1UdDwEB/wQEAwICpDANBgkqhkiG9w0BAQ0F\nAAOCAgEAeCMxVJr5Jyg87DVaUtEhiWfhto993ENrnevAGqrBOoRc/KU1/C3paqhR\nsvr2r2LR+npSmeo6iz0FaO31XwHSHX95+XJeGP5Q8TGddbRiTglQsMfOkGNzxqgg\nTkdZ8A1y9v2jprONUmLADVGIVT0AoHc7V9w1I8NKhrY+rIllum4FRDiDPSnImh5h\nxmH+Nq2ZuEFVdtV/oNKzEu2ywmbgBRd5Jv3rTejxltmTZtyq8IKoKguj3NVFn93Q\nU4TbsxkcAdrLMooLYYDRTWA4t0iqKM/UkYUg4xl2l9NrY7ZUbaNd5+YsLNdqXO/c\nmp7wyMv/8ZIy1BLG4zJmX/JzWkYmULqQ+A+21+YuqrV3a81V7vcHhJcRaPOrg5cd\nYwY2eCbXMvNOdrzppIglUrlddNuqAhs1MTi/VibxYuI9isU0JckXIcCy1L+xbEda\n6v/z6wSrScVz0I4m0DpK6xMQ8t9sLcrGp5uGbj6J4nQWd+QLdq6kmAzDOZ/Gs0wb\nPYdkER4dXAVcioYFekpKv7d+nur0FPtMNIw0OdhX2eAwC22IFAq2DZRjUFvaBGaD\ni1ptfq6P1mVJ2T/exYujEDtq+8yQTfWgFm/DjEfWtcCp0Jukgv8opLR2DpCf5Ucq\nd5X7d/DP0mukJ3vZ8EIqYorwZJ1L1a2jgngjA+gPxIaW+JHfTHU=\n-----END CERTIFICATE-----\n'})
changed: [welktxef-931887-rz-le2pts6-021 -> localhost] => (item={'filename': 'vz_root_ca_cert.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIFpTCCA42gAwIBAgIUa3vZ0YGxO1TQ8NwhiVfQC0JslXgwDQYJKoZIhvcNAQEL\nBQAwWjELMAkGA1UEBhMCVVMxEDAOBgNVBAoMB1Zlcml6b24xEzARBgNVBAsMClZa\nSUFNIFRlc3QxJDAiBgNVBAMMG1Zlcml6b24gTmV0d29yayBSU0EgQ0EgVGVzdDAe\nFw0yMDA2MTUyMTAxMTNaFw0zNTA2MTUyMTAxMTNaMFoxCzAJBgNVBAYTAlVTMRAw\nDgYDVQQKDAdWZXJpem9uMRMwEQYDVQQLDApWWklBTSBUZXN0MSQwIgYDVQQDDBtW\nZXJpem9uIE5ldHdvcmsgUlNBIENBIFRlc3QwggIiMA0GCSqGSIb3DQEBAQUAA4IC\nDwAwggIKAoICAQC8AIrksI57CbIl5uGZ6yqfpQj3aK+N8f1EVHdwK9JFskoipvC8\n7yFTk8tgmO1i0YA5oRGfNxneqCdrXZiWL6Ko8v/iln9vuN+2rK3rgWZPPRJBAsBN\na49L7U6lJjIGxIZtZqmK5h47oiUtwlYVrbZMN2ijuBQ22/eQ9tsFDV28oBuZ3WAR\npSSbj/tubPQYkw3YYOhv/VpEpsd0rkoEt3QCmTVcX2rtblanpXowTV5R0Hy4014n\nT49jrEo40r4mwYoyS835Uv4ENUFA+pXicT9eUot3RSH6rYdx4A/14UtoI9U0ol8M\n62GHpxSASQ2Kc3yQWvxRGTFslTduYM+vVmMLEDDdqcsjYnStPpwdxxmKItmbjxSv\nIwYIndp8A04WkX2iiJCciC3BNxiLamPtYVyB1HHqbGTGirKYuSvwZt337q1OI3WH\nwVn2S4Mj/wqa4iCyGTvFSUnGq34Xkrb9XNwWBok9Tc2XWGAU/mb/xcd1hX74GZbF\nsrZ11aPtym4kMAjU2KQi96GcAH2lnGZYoOja1J4Cs4WYx1uAx74H/m84CrYavVfl\n1ONJVLDfuZaEkSmu+jHQX15pAECNORTuLD06PbWnOEcOi1xmbt/OT3SA3rhD2mb7\n2wxl7oJpV3ap8xGwYmxiFzmInxFJ1axjg8Rimol0mXTKAy6OdNHbCOnAwwIDAQAB\no2MwYTAPBgNVHRMBAf8EBTADAQH/MA4GA1UdDwEB/wQEAwIBBjAfBgNVHSMEGDAW\ngBQleng3lqGBeTrbLVuABoEmUHm1+TAdBgNVHQ4EFgQUJXp4N5ahgXk62y1bgAaB\nJlB5tfkwDQYJKoZIhvcNAQELBQADggIBADQ9jpmVh9nyY7ZQ4s+S9RuSRYn7QsrW\nDePeMzQgh8ZtS8WE65GY5HS61iHNP2Co8Q1lAaBWF4ipq+VZOcQbPLccHzd1kZv4\ns4u0aTzBd9ccidl73FS0DJDQOBbzPSzgsaiGHSMyGzkTeA8z3ntsSqrXXcDUvoRi\nFus/110AwdtNhJLrWveX6btYtHp9Lqe0YtNCy5AaXlrr1yRSckP5BWVtlwD4dzSO\n/dqI3wHS/ncUx9wSQomZ+AmxYW3KtJQKgHzTqHru1x9BBk7Bzfz9FZr6HLLmEitj\nuFoDRd5TNt5LbO0zDQokvY3oqso6Htup/rS7C08mcmnelYE+yXuOc1YrlyGnpBzk\nmy+1VYbOxRRdqKAZRbE72u/h847IVpsOvjR51iksuCAurZdp2+y2zvV8NhWekuNy\nirECRy9cb4YasjRaKi0/TCGPVSICuLyeG2W72liCj/N2VKfjPP9zsOR5XjwCXfRg\n+9xhLy77/gov2NWXx5fzTkhxCrHOxFdLVMn0wQhksDmw6QsXzDIHSpIOypdDfnx9\nCsthx3nhkuHLUaEP22D22dG+vImA9ukj4R/RRI/87jmi9Q8+ehH+NqN0GZZcLjdN\nSLVXpncuwWQFUDPR06wNkkkmBSXWiIYhwqSpU0Pl3er3fD0uWvXuWPm2PzfOmUAE\nUrkzyw9XmLw0\n-----END CERTIFICATE-----\n'})
changed: [welktxef-931887-rz-le2pts6-021 -> localhost] => (item={'filename': 'vz_root_ica_cert.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIFNzCCAx+gAwIBAgIUGLJR/hP48n+vdq2v1hcfspXo/78wDQYJKoZIhvcNAQEL\nBQAwWjELMAkGA1UEBhMCVVMxEDAOBgNVBAoMB1Zlcml6b24xEzARBgNVBAsMClZa\nSUFNIFRlc3QxJDAiBgNVBAMMG1Zlcml6b24gTmV0d29yayBSU0EgQ0EgVGVzdDAe\nFw0yMDEwMjIyMTE0MDNaFw0zMDEwMjIyMTE0MDNaMIGRMQswCQYDVQQGEwJVUzEL\nMAkGA1UECAwCVFgxETAPBgNVBAcMCFdlc3RsYWtlMRAwDgYDVQQKDAdWZXJpem9u\nMR0wGwYDVQQLDBRWZXJpem9uIFNvdXJjaW5nIExMQzExMC8GA1UEAwwoVmVyaXpv\nbiBOZXR3b3JrIFdFTEtUWElCIExBQiAxIDMgUlNBIElDQTCCASIwDQYJKoZIhvcN\nAQEBBQADggEPADCCAQoCggEBANhkGTXOCKEYf5znDDeX3n/DHFPVqazgQsr0/SIG\n4eb1JY5q5Jq3ZhAaZCr9HJuCkwAP/zgYH0llqOvf8AC2Uh+7z1b33IbwxPmJfWCP\nAqSNFkLWWVRdbELapCu408QsrLMW8IrdP6PLiKAepwncfm4T0/6bANqIEmUkpw8Q\nxProeiNwlGbwUll+tELmdCk7vA7hKX3j1kUvS5Z84Z5ivJBWEcUEggmC97TK4aLo\nFVEHbyahze568JVEaM1vY5L4mnRRTl+u5ipaSMxVBsiXzF7eFuKCzqF7wxbDIt2T\nIFEJtwyJDW5bXjyXgiF1d5H/URprUcRV9Qmf2+PXcfwHII8CAwEAAaOBvDCBuTAS\nBgNVHRMBAf8ECDAGAQH/AgEAMA4GA1UdDwEB/wQEAwIBBjAfBgNVHSMEGDAWgBQl\neng3lqGBeTrbLVuABoEmUHm1+TBTBgNVHR8ETDBKMEigRqBEhkJodHRwOi8vc2Vj\ndXJlLnN0YWdpbmcuc2VjdXJpdHljcmVkZW50aWFsaW5nLmNvbS9jcmwvdnpuZXRy\nc2FjYS5jcmwwHQYDVR0OBBYEFP0Z+/vaDLtAoFig1I9ttNKnmzByMA0GCSqGSIb3\nDQEBCwUAA4ICAQBuXVTf9e01HeymHgRcFCwP2N6G6u+vIzY8Bz0zSUZeRDHMZQcS\nNoabDyn5FfGJlw4BqGC591Sp0/unFQDzAg17rDBcrgwajeFeUiFdb9PiAJwHaX9S\nvq/7VmVLCmpeb+a/laXAe6+tkY1kcFrd1+ItRKC6ZGXMsoDkmk5Ndxxgw77estcI\nMiiLQbvpXRygX5wD4/ayazuLms9qITZkOZ1nTLVqq7QrwYCsSoih7hj6sbsfXr19\nGoYWmk8Y7O/d3ttgyHuRH9k/2dQ/xL7avRpMNkPdr7ocJqI46hvx2X6UyOo7IBua\nkSkFbSmPZWIVAidNMBOnvffCQ32tfjT2/xso/a9cdskvxqgLi0MPARU9Nl2Pufsb\nD7l4/sBvz/PiNTKp+Daa9FdyLb9ySidos1uS0c24bUtY1RXXGAVV2qgfyrzvzfye\nSM+w16hMU/yeYiuA1jsPmsnZnuIJj4Nv8ZjjZ0WS53pP5wcghaHkBrqWQNT8meqA\nVElrMBPlYq67T+AXP0B9lf5Sc3QVIio7XKKfqrlcQxY2JGLEyE53JgZGX7dpwU4I\nukLvyHbT4p06oY3qG6+wH8+YIXCNAYtadJ/C5/u9GcLX5NnZrcuduj0inw2/a3Ao\nWgCt6/Pr28BkCvkWdDt9d8Z40qeu1aZdcr157mR+yZGPfBfB2vasrNIEwQ==\n-----END CERTIFICATE-----\n'})

TASK [remote/trust : Generate trust_ca.pem] ****************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/trust : Copy trust_ca.pem to host] ************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/trust : Install certificate] ******************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/trust : Remove temporary working directory] ***************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [Remote Starlingx] ************************************************************************************************************************

TASK [remote/starlingx : Create temporary working directory] ***********************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/starlingx : Copy SSL root certificates] *******************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost] => (item={'filename': 'vz_root_ica_cert.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIFNzCCAx+gAwIBAgIUGLJR/hP48n+vdq2v1hcfspXo/78wDQYJKoZIhvcNAQEL\nBQAwWjELMAkGA1UEBhMCVVMxEDAOBgNVBAoMB1Zlcml6b24xEzARBgNVBAsMClZa\nSUFNIFRlc3QxJDAiBgNVBAMMG1Zlcml6b24gTmV0d29yayBSU0EgQ0EgVGVzdDAe\nFw0yMDEwMjIyMTE0MDNaFw0zMDEwMjIyMTE0MDNaMIGRMQswCQYDVQQGEwJVUzEL\nMAkGA1UECAwCVFgxETAPBgNVBAcMCFdlc3RsYWtlMRAwDgYDVQQKDAdWZXJpem9u\nMR0wGwYDVQQLDBRWZXJpem9uIFNvdXJjaW5nIExMQzExMC8GA1UEAwwoVmVyaXpv\nbiBOZXR3b3JrIFdFTEtUWElCIExBQiAxIDMgUlNBIElDQTCCASIwDQYJKoZIhvcN\nAQEBBQADggEPADCCAQoCggEBANhkGTXOCKEYf5znDDeX3n/DHFPVqazgQsr0/SIG\n4eb1JY5q5Jq3ZhAaZCr9HJuCkwAP/zgYH0llqOvf8AC2Uh+7z1b33IbwxPmJfWCP\nAqSNFkLWWVRdbELapCu408QsrLMW8IrdP6PLiKAepwncfm4T0/6bANqIEmUkpw8Q\nxProeiNwlGbwUll+tELmdCk7vA7hKX3j1kUvS5Z84Z5ivJBWEcUEggmC97TK4aLo\nFVEHbyahze568JVEaM1vY5L4mnRRTl+u5ipaSMxVBsiXzF7eFuKCzqF7wxbDIt2T\nIFEJtwyJDW5bXjyXgiF1d5H/URprUcRV9Qmf2+PXcfwHII8CAwEAAaOBvDCBuTAS\nBgNVHRMBAf8ECDAGAQH/AgEAMA4GA1UdDwEB/wQEAwIBBjAfBgNVHSMEGDAWgBQl\neng3lqGBeTrbLVuABoEmUHm1+TBTBgNVHR8ETDBKMEigRqBEhkJodHRwOi8vc2Vj\ndXJlLnN0YWdpbmcuc2VjdXJpdHljcmVkZW50aWFsaW5nLmNvbS9jcmwvdnpuZXRy\nc2FjYS5jcmwwHQYDVR0OBBYEFP0Z+/vaDLtAoFig1I9ttNKnmzByMA0GCSqGSIb3\nDQEBCwUAA4ICAQBuXVTf9e01HeymHgRcFCwP2N6G6u+vIzY8Bz0zSUZeRDHMZQcS\nNoabDyn5FfGJlw4BqGC591Sp0/unFQDzAg17rDBcrgwajeFeUiFdb9PiAJwHaX9S\nvq/7VmVLCmpeb+a/laXAe6+tkY1kcFrd1+ItRKC6ZGXMsoDkmk5Ndxxgw77estcI\nMiiLQbvpXRygX5wD4/ayazuLms9qITZkOZ1nTLVqq7QrwYCsSoih7hj6sbsfXr19\nGoYWmk8Y7O/d3ttgyHuRH9k/2dQ/xL7avRpMNkPdr7ocJqI46hvx2X6UyOo7IBua\nkSkFbSmPZWIVAidNMBOnvffCQ32tfjT2/xso/a9cdskvxqgLi0MPARU9Nl2Pufsb\nD7l4/sBvz/PiNTKp+Daa9FdyLb9ySidos1uS0c24bUtY1RXXGAVV2qgfyrzvzfye\nSM+w16hMU/yeYiuA1jsPmsnZnuIJj4Nv8ZjjZ0WS53pP5wcghaHkBrqWQNT8meqA\nVElrMBPlYq67T+AXP0B9lf5Sc3QVIio7XKKfqrlcQxY2JGLEyE53JgZGX7dpwU4I\nukLvyHbT4p06oY3qG6+wH8+YIXCNAYtadJ/C5/u9GcLX5NnZrcuduj0inw2/a3Ao\nWgCt6/Pr28BkCvkWdDt9d8Z40qeu1aZdcr157mR+yZGPfBfB2vasrNIEwQ==\n-----END CERTIFICATE-----\n'})
changed: [welktxef-931887-rz-le2pts6-021 -> localhost] => (item={'filename': 'vz_root_ica_key.pem', 'value': '-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA2GQZNc4IoRh/nOcMN5fef8McU9WprOBCyvT9Igbh5vUljmrk\nmrdmEBpkKv0cm4KTAA//OBgfSWWo69/wALZSH7vPVvfchvDE+Yl9YI8CpI0WQtZZ\nVF1sQtqkK7jTxCyssxbwit0/o8uIoB6nCdx+bhPT/psA2ogSZSSnDxDE+uh6I3CU\nZvBSWX60QuZ0KTu8DuEpfePWRS9LlnzhnmK8kFYRxQSCCYL3tMrhougVUQdvJqHN\n7nrwlURozW9jkviadFFOX67mKlpIzFUGyJfMXt4W4oLOoXvDFsMi3ZMgUQm3DIkN\nbltePJeCIXV3kf9RGmtRxFX1CZ/b49dx/AcgjwIDAQABAoIBABSd1NkPfDr8/ouQ\nZ9WUHprFmBlUrgnOhA6aMNPhG/zJNn7PKGClQJAgM5L08pjOY/sJiyNpCPIRQXrX\npyIqPMDRP/vlOZmRrvKnas6cUYAkAQ71JSWokPv9oM6ZmXODXiDh+qEAW2PbrHS0\n9u01mMYcFYKYeghYFoiUaWZCDsJo3v3dgeE9aQ4tB9ksovSmWrpuCY7NKbd7Qrbo\n5XxQhkujTkE6knOHz8CVwYETtj8LZ/bvHIkGMGvRvwsKYDZkIKr5CZ7DX+KcMfPN\neMZU4VCHYSXNxsyp5DJ1Zw+gx8/32kUL0CzJLLam1G021Hq41KPwwSV/KPrOKel7\nHXDLXeECgYEA8MR+lgxGjYTc/k4TdZvcFVgqHGLXnyjO7ZVt4b7UpwmayLuoSD/M\nOpHQYX+JBIIWTNlGhG8UV3DPC3v+auhYa7twwbekS30IYCAmu5GCKgMAcWFinz6A\nYZxG55P/hShetCyOqikgwXqzMlwGs8KEul8f8BKssROzUy8mIlFhjq0CgYEA5hTM\nSNxAD3dlRtb0771fBU7fjx8JPfjptP9vP/JVEelkc/ti9nZ5buTC+9cQC/B+YFx7\nc82uCrXV13bGR9iH8xBhwU7JOYJZbgCpwp0F56wIN5Pdk9Eo79Batrw3oGBG4Yvt\nDc2eltxQbHgObc/qygf88j9XqD8aGIvQrc4Jf6sCgYAtxX03M1A6WTbWFau3YRD+\n8crXqKbLOCvWmODR2MB+nOHTJXHBgndl7xCJaIB43e41X9z7Ek7wrJ5/1WuxkUg1\n+uVdvna6byOnepVCdVAkgnuUEmp4UZ6AcAA+yDD8dIdEg2//w1/ZyGTGvx37EJDB\nCZJ9xl8ULuWZe84pGgWM5QKBgQCYVUbYKrNjShrM5z9uh4QlII6V1Oeql2YtBz4i\nKZE3db6jp9pi8hf+WwnZ8g9WyFjz9edqydAkmTXHHYW0ReHlBYCjm0VRhUMuuNOs\n3YfuVpFuMsFuv/oJpXqaKE3wKi5j4OAH1o7ctWuuFWMAQ7vhHZ7UySmBZJ4jiFaW\n7KaPVwKBgE8E0xbSDVGxXbEGwRXxeaOSemEHD9uEnbAyq1p3EBBhBvInWmDiP5vJ\n68IYNZ4SGxXEKDifwrLGHyekt3RK9B2+U03okd1qH7gfBIlxBJivcjhBe2PtK/Qj\n6fBN0fC1UJoE6pseT9cJDaBq2wMRXJGRYtT8fU9PPJcfa23JlKNS\n-----END RSA PRIVATE KEY-----\n'})

TASK [remote/starlingx : Copy templates] *******************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost] => (item=req_starlingx.cnf)

TASK [remote/starlingx : Generate SSL cert] ****************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/starlingx : Copy SSL starlingx certs to server] ***********************************************************************************
changed: [welktxef-931887-rz-le2pts6-021] => (item=starlingx-ca-cert.pem)

TASK [remote/starlingx : Configure starlingx] **************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/starlingx : Remove temporary working directory] ***********************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [Remote Integ] ****************************************************************************************************************************

TASK [remote/integ : Detect applied status of platform-integ-apps application] *****************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/integ : Fail if platform-integ-apps application apply failed] *********************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [Remote Ldap] *****************************************************************************************************************************

TASK [remote/ldap : Create temporary working directory] ****************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/ldap : Copy SSL root certificates] ************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost] => (item={'filename': 'vz_root_ca_cert.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIFpTCCA42gAwIBAgIUa3vZ0YGxO1TQ8NwhiVfQC0JslXgwDQYJKoZIhvcNAQEL\nBQAwWjELMAkGA1UEBhMCVVMxEDAOBgNVBAoMB1Zlcml6b24xEzARBgNVBAsMClZa\nSUFNIFRlc3QxJDAiBgNVBAMMG1Zlcml6b24gTmV0d29yayBSU0EgQ0EgVGVzdDAe\nFw0yMDA2MTUyMTAxMTNaFw0zNTA2MTUyMTAxMTNaMFoxCzAJBgNVBAYTAlVTMRAw\nDgYDVQQKDAdWZXJpem9uMRMwEQYDVQQLDApWWklBTSBUZXN0MSQwIgYDVQQDDBtW\nZXJpem9uIE5ldHdvcmsgUlNBIENBIFRlc3QwggIiMA0GCSqGSIb3DQEBAQUAA4IC\nDwAwggIKAoICAQC8AIrksI57CbIl5uGZ6yqfpQj3aK+N8f1EVHdwK9JFskoipvC8\n7yFTk8tgmO1i0YA5oRGfNxneqCdrXZiWL6Ko8v/iln9vuN+2rK3rgWZPPRJBAsBN\na49L7U6lJjIGxIZtZqmK5h47oiUtwlYVrbZMN2ijuBQ22/eQ9tsFDV28oBuZ3WAR\npSSbj/tubPQYkw3YYOhv/VpEpsd0rkoEt3QCmTVcX2rtblanpXowTV5R0Hy4014n\nT49jrEo40r4mwYoyS835Uv4ENUFA+pXicT9eUot3RSH6rYdx4A/14UtoI9U0ol8M\n62GHpxSASQ2Kc3yQWvxRGTFslTduYM+vVmMLEDDdqcsjYnStPpwdxxmKItmbjxSv\nIwYIndp8A04WkX2iiJCciC3BNxiLamPtYVyB1HHqbGTGirKYuSvwZt337q1OI3WH\nwVn2S4Mj/wqa4iCyGTvFSUnGq34Xkrb9XNwWBok9Tc2XWGAU/mb/xcd1hX74GZbF\nsrZ11aPtym4kMAjU2KQi96GcAH2lnGZYoOja1J4Cs4WYx1uAx74H/m84CrYavVfl\n1ONJVLDfuZaEkSmu+jHQX15pAECNORTuLD06PbWnOEcOi1xmbt/OT3SA3rhD2mb7\n2wxl7oJpV3ap8xGwYmxiFzmInxFJ1axjg8Rimol0mXTKAy6OdNHbCOnAwwIDAQAB\no2MwYTAPBgNVHRMBAf8EBTADAQH/MA4GA1UdDwEB/wQEAwIBBjAfBgNVHSMEGDAW\ngBQleng3lqGBeTrbLVuABoEmUHm1+TAdBgNVHQ4EFgQUJXp4N5ahgXk62y1bgAaB\nJlB5tfkwDQYJKoZIhvcNAQELBQADggIBADQ9jpmVh9nyY7ZQ4s+S9RuSRYn7QsrW\nDePeMzQgh8ZtS8WE65GY5HS61iHNP2Co8Q1lAaBWF4ipq+VZOcQbPLccHzd1kZv4\ns4u0aTzBd9ccidl73FS0DJDQOBbzPSzgsaiGHSMyGzkTeA8z3ntsSqrXXcDUvoRi\nFus/110AwdtNhJLrWveX6btYtHp9Lqe0YtNCy5AaXlrr1yRSckP5BWVtlwD4dzSO\n/dqI3wHS/ncUx9wSQomZ+AmxYW3KtJQKgHzTqHru1x9BBk7Bzfz9FZr6HLLmEitj\nuFoDRd5TNt5LbO0zDQokvY3oqso6Htup/rS7C08mcmnelYE+yXuOc1YrlyGnpBzk\nmy+1VYbOxRRdqKAZRbE72u/h847IVpsOvjR51iksuCAurZdp2+y2zvV8NhWekuNy\nirECRy9cb4YasjRaKi0/TCGPVSICuLyeG2W72liCj/N2VKfjPP9zsOR5XjwCXfRg\n+9xhLy77/gov2NWXx5fzTkhxCrHOxFdLVMn0wQhksDmw6QsXzDIHSpIOypdDfnx9\nCsthx3nhkuHLUaEP22D22dG+vImA9ukj4R/RRI/87jmi9Q8+ehH+NqN0GZZcLjdN\nSLVXpncuwWQFUDPR06wNkkkmBSXWiIYhwqSpU0Pl3er3fD0uWvXuWPm2PzfOmUAE\nUrkzyw9XmLw0\n-----END CERTIFICATE-----\n'})
changed: [welktxef-931887-rz-le2pts6-021 -> localhost] => (item={'filename': 'vz_root_ica_cert.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIFNzCCAx+gAwIBAgIUGLJR/hP48n+vdq2v1hcfspXo/78wDQYJKoZIhvcNAQEL\nBQAwWjELMAkGA1UEBhMCVVMxEDAOBgNVBAoMB1Zlcml6b24xEzARBgNVBAsMClZa\nSUFNIFRlc3QxJDAiBgNVBAMMG1Zlcml6b24gTmV0d29yayBSU0EgQ0EgVGVzdDAe\nFw0yMDEwMjIyMTE0MDNaFw0zMDEwMjIyMTE0MDNaMIGRMQswCQYDVQQGEwJVUzEL\nMAkGA1UECAwCVFgxETAPBgNVBAcMCFdlc3RsYWtlMRAwDgYDVQQKDAdWZXJpem9u\nMR0wGwYDVQQLDBRWZXJpem9uIFNvdXJjaW5nIExMQzExMC8GA1UEAwwoVmVyaXpv\nbiBOZXR3b3JrIFdFTEtUWElCIExBQiAxIDMgUlNBIElDQTCCASIwDQYJKoZIhvcN\nAQEBBQADggEPADCCAQoCggEBANhkGTXOCKEYf5znDDeX3n/DHFPVqazgQsr0/SIG\n4eb1JY5q5Jq3ZhAaZCr9HJuCkwAP/zgYH0llqOvf8AC2Uh+7z1b33IbwxPmJfWCP\nAqSNFkLWWVRdbELapCu408QsrLMW8IrdP6PLiKAepwncfm4T0/6bANqIEmUkpw8Q\nxProeiNwlGbwUll+tELmdCk7vA7hKX3j1kUvS5Z84Z5ivJBWEcUEggmC97TK4aLo\nFVEHbyahze568JVEaM1vY5L4mnRRTl+u5ipaSMxVBsiXzF7eFuKCzqF7wxbDIt2T\nIFEJtwyJDW5bXjyXgiF1d5H/URprUcRV9Qmf2+PXcfwHII8CAwEAAaOBvDCBuTAS\nBgNVHRMBAf8ECDAGAQH/AgEAMA4GA1UdDwEB/wQEAwIBBjAfBgNVHSMEGDAWgBQl\neng3lqGBeTrbLVuABoEmUHm1+TBTBgNVHR8ETDBKMEigRqBEhkJodHRwOi8vc2Vj\ndXJlLnN0YWdpbmcuc2VjdXJpdHljcmVkZW50aWFsaW5nLmNvbS9jcmwvdnpuZXRy\nc2FjYS5jcmwwHQYDVR0OBBYEFP0Z+/vaDLtAoFig1I9ttNKnmzByMA0GCSqGSIb3\nDQEBCwUAA4ICAQBuXVTf9e01HeymHgRcFCwP2N6G6u+vIzY8Bz0zSUZeRDHMZQcS\nNoabDyn5FfGJlw4BqGC591Sp0/unFQDzAg17rDBcrgwajeFeUiFdb9PiAJwHaX9S\nvq/7VmVLCmpeb+a/laXAe6+tkY1kcFrd1+ItRKC6ZGXMsoDkmk5Ndxxgw77estcI\nMiiLQbvpXRygX5wD4/ayazuLms9qITZkOZ1nTLVqq7QrwYCsSoih7hj6sbsfXr19\nGoYWmk8Y7O/d3ttgyHuRH9k/2dQ/xL7avRpMNkPdr7ocJqI46hvx2X6UyOo7IBua\nkSkFbSmPZWIVAidNMBOnvffCQ32tfjT2/xso/a9cdskvxqgLi0MPARU9Nl2Pufsb\nD7l4/sBvz/PiNTKp+Daa9FdyLb9ySidos1uS0c24bUtY1RXXGAVV2qgfyrzvzfye\nSM+w16hMU/yeYiuA1jsPmsnZnuIJj4Nv8ZjjZ0WS53pP5wcghaHkBrqWQNT8meqA\nVElrMBPlYq67T+AXP0B9lf5Sc3QVIio7XKKfqrlcQxY2JGLEyE53JgZGX7dpwU4I\nukLvyHbT4p06oY3qG6+wH8+YIXCNAYtadJ/C5/u9GcLX5NnZrcuduj0inw2/a3Ao\nWgCt6/Pr28BkCvkWdDt9d8Z40qeu1aZdcr157mR+yZGPfBfB2vasrNIEwQ==\n-----END CERTIFICATE-----\n'})
changed: [welktxef-931887-rz-le2pts6-021 -> localhost] => (item={'filename': 'vz_root_ica_key.pem', 'value': '-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA2GQZNc4IoRh/nOcMN5fef8McU9WprOBCyvT9Igbh5vUljmrk\nmrdmEBpkKv0cm4KTAA//OBgfSWWo69/wALZSH7vPVvfchvDE+Yl9YI8CpI0WQtZZ\nVF1sQtqkK7jTxCyssxbwit0/o8uIoB6nCdx+bhPT/psA2ogSZSSnDxDE+uh6I3CU\nZvBSWX60QuZ0KTu8DuEpfePWRS9LlnzhnmK8kFYRxQSCCYL3tMrhougVUQdvJqHN\n7nrwlURozW9jkviadFFOX67mKlpIzFUGyJfMXt4W4oLOoXvDFsMi3ZMgUQm3DIkN\nbltePJeCIXV3kf9RGmtRxFX1CZ/b49dx/AcgjwIDAQABAoIBABSd1NkPfDr8/ouQ\nZ9WUHprFmBlUrgnOhA6aMNPhG/zJNn7PKGClQJAgM5L08pjOY/sJiyNpCPIRQXrX\npyIqPMDRP/vlOZmRrvKnas6cUYAkAQ71JSWokPv9oM6ZmXODXiDh+qEAW2PbrHS0\n9u01mMYcFYKYeghYFoiUaWZCDsJo3v3dgeE9aQ4tB9ksovSmWrpuCY7NKbd7Qrbo\n5XxQhkujTkE6knOHz8CVwYETtj8LZ/bvHIkGMGvRvwsKYDZkIKr5CZ7DX+KcMfPN\neMZU4VCHYSXNxsyp5DJ1Zw+gx8/32kUL0CzJLLam1G021Hq41KPwwSV/KPrOKel7\nHXDLXeECgYEA8MR+lgxGjYTc/k4TdZvcFVgqHGLXnyjO7ZVt4b7UpwmayLuoSD/M\nOpHQYX+JBIIWTNlGhG8UV3DPC3v+auhYa7twwbekS30IYCAmu5GCKgMAcWFinz6A\nYZxG55P/hShetCyOqikgwXqzMlwGs8KEul8f8BKssROzUy8mIlFhjq0CgYEA5hTM\nSNxAD3dlRtb0771fBU7fjx8JPfjptP9vP/JVEelkc/ti9nZ5buTC+9cQC/B+YFx7\nc82uCrXV13bGR9iH8xBhwU7JOYJZbgCpwp0F56wIN5Pdk9Eo79Batrw3oGBG4Yvt\nDc2eltxQbHgObc/qygf88j9XqD8aGIvQrc4Jf6sCgYAtxX03M1A6WTbWFau3YRD+\n8crXqKbLOCvWmODR2MB+nOHTJXHBgndl7xCJaIB43e41X9z7Ek7wrJ5/1WuxkUg1\n+uVdvna6byOnepVCdVAkgnuUEmp4UZ6AcAA+yDD8dIdEg2//w1/ZyGTGvx37EJDB\nCZJ9xl8ULuWZe84pGgWM5QKBgQCYVUbYKrNjShrM5z9uh4QlII6V1Oeql2YtBz4i\nKZE3db6jp9pi8hf+WwnZ8g9WyFjz9edqydAkmTXHHYW0ReHlBYCjm0VRhUMuuNOs\n3YfuVpFuMsFuv/oJpXqaKE3wKi5j4OAH1o7ctWuuFWMAQ7vhHZ7UySmBZJ4jiFaW\n7KaPVwKBgE8E0xbSDVGxXbEGwRXxeaOSemEHD9uEnbAyq1p3EBBhBvInWmDiP5vJ\n68IYNZ4SGxXEKDifwrLGHyekt3RK9B2+U03okd1qH7gfBIlxBJivcjhBe2PtK/Qj\n6fBN0fC1UJoE6pseT9cJDaBq2wMRXJGRYtT8fU9PPJcfa23JlKNS\n-----END RSA PRIVATE KEY-----\n'})

TASK [remote/ldap : Copy templates] ************************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost] => (item={'name': 'req-ldap.cnf', 'mode': '0644'})

TASK [remote/ldap : Generate SSL cert] *********************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/ldap : Copy templates] ************************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021] => (item={'name': 'dex-overrides.yaml', 'mode': '0644'})

TASK [remote/ldap : Copy SSL dex certs to server] **********************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021] => (item=dex-cert.pem)
changed: [welktxef-931887-rz-le2pts6-021] => (item=dex-key.pem)
changed: [welktxef-931887-rz-le2pts6-021] => (item=dex-ca.pem)

TASK [remote/ldap : Copy SSL AD cert to server] ************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021] => (item={'filename': 'ad_ca.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIFpTCCA42gAwIBAgIUa3vZ0YGxO1TQ8NwhiVfQC0JslXgwDQYJKoZIhvcNAQEL\nBQAwWjELMAkGA1UEBhMCVVMxEDAOBgNVBAoMB1Zlcml6b24xEzARBgNVBAsMClZa\nSUFNIFRlc3QxJDAiBgNVBAMMG1Zlcml6b24gTmV0d29yayBSU0EgQ0EgVGVzdDAe\nFw0yMDA2MTUyMTAxMTNaFw0zNTA2MTUyMTAxMTNaMFoxCzAJBgNVBAYTAlVTMRAw\nDgYDVQQKDAdWZXJpem9uMRMwEQYDVQQLDApWWklBTSBUZXN0MSQwIgYDVQQDDBtW\nZXJpem9uIE5ldHdvcmsgUlNBIENBIFRlc3QwggIiMA0GCSqGSIb3DQEBAQUAA4IC\nDwAwggIKAoICAQC8AIrksI57CbIl5uGZ6yqfpQj3aK+N8f1EVHdwK9JFskoipvC8\n7yFTk8tgmO1i0YA5oRGfNxneqCdrXZiWL6Ko8v/iln9vuN+2rK3rgWZPPRJBAsBN\na49L7U6lJjIGxIZtZqmK5h47oiUtwlYVrbZMN2ijuBQ22/eQ9tsFDV28oBuZ3WAR\npSSbj/tubPQYkw3YYOhv/VpEpsd0rkoEt3QCmTVcX2rtblanpXowTV5R0Hy4014n\nT49jrEo40r4mwYoyS835Uv4ENUFA+pXicT9eUot3RSH6rYdx4A/14UtoI9U0ol8M\n62GHpxSASQ2Kc3yQWvxRGTFslTduYM+vVmMLEDDdqcsjYnStPpwdxxmKItmbjxSv\nIwYIndp8A04WkX2iiJCciC3BNxiLamPtYVyB1HHqbGTGirKYuSvwZt337q1OI3WH\nwVn2S4Mj/wqa4iCyGTvFSUnGq34Xkrb9XNwWBok9Tc2XWGAU/mb/xcd1hX74GZbF\nsrZ11aPtym4kMAjU2KQi96GcAH2lnGZYoOja1J4Cs4WYx1uAx74H/m84CrYavVfl\n1ONJVLDfuZaEkSmu+jHQX15pAECNORTuLD06PbWnOEcOi1xmbt/OT3SA3rhD2mb7\n2wxl7oJpV3ap8xGwYmxiFzmInxFJ1axjg8Rimol0mXTKAy6OdNHbCOnAwwIDAQAB\no2MwYTAPBgNVHRMBAf8EBTADAQH/MA4GA1UdDwEB/wQEAwIBBjAfBgNVHSMEGDAW\ngBQleng3lqGBeTrbLVuABoEmUHm1+TAdBgNVHQ4EFgQUJXp4N5ahgXk62y1bgAaB\nJlB5tfkwDQYJKoZIhvcNAQELBQADggIBADQ9jpmVh9nyY7ZQ4s+S9RuSRYn7QsrW\nDePeMzQgh8ZtS8WE65GY5HS61iHNP2Co8Q1lAaBWF4ipq+VZOcQbPLccHzd1kZv4\ns4u0aTzBd9ccidl73FS0DJDQOBbzPSzgsaiGHSMyGzkTeA8z3ntsSqrXXcDUvoRi\nFus/110AwdtNhJLrWveX6btYtHp9Lqe0YtNCy5AaXlrr1yRSckP5BWVtlwD4dzSO\n/dqI3wHS/ncUx9wSQomZ+AmxYW3KtJQKgHzTqHru1x9BBk7Bzfz9FZr6HLLmEitj\nuFoDRd5TNt5LbO0zDQokvY3oqso6Htup/rS7C08mcmnelYE+yXuOc1YrlyGnpBzk\nmy+1VYbOxRRdqKAZRbE72u/h847IVpsOvjR51iksuCAurZdp2+y2zvV8NhWekuNy\nirECRy9cb4YasjRaKi0/TCGPVSICuLyeG2W72liCj/N2VKfjPP9zsOR5XjwCXfRg\n+9xhLy77/gov2NWXx5fzTkhxCrHOxFdLVMn0wQhksDmw6QsXzDIHSpIOypdDfnx9\nCsthx3nhkuHLUaEP22D22dG+vImA9ukj4R/RRI/87jmi9Q8+ehH+NqN0GZZcLjdN\nSLVXpncuwWQFUDPR06wNkkkmBSXWiIYhwqSpU0Pl3er3fD0uWvXuWPm2PzfOmUAE\nUrkzyw9XmLw0\n-----END CERTIFICATE-----\n'})

TASK [remote/ldap : Configure local-dex.tls] ***************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/ldap : Configure generic] *********************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/ldap : Configure wadcert] *********************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/ldap : Configure dex-overrides.yaml] **********************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/ldap : Wait for distributed cloud synchronization] ********************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001]

TASK [remote/ldap : Remove temporary working directory] ****************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/ldap : Detect oidc-auth-apps application in applying state (from a previous attempt)] *********************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/ldap : Fail if oidc-auth-apps application-abort failed] ***************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/ldap : Detect oidc-auth-apps application in apply-failed or aborted state] ********************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/ldap : Fail if oidc-auth-apps application apply failed] ***************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/ldap : Apply oidc-auth-apps application] ******************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/ldap : Detect applied status of oidc-auth-apps application] ***********************************************************************
FAILED - RETRYING: Detect applied status of oidc-auth-apps application (60 retries left).
FAILED - RETRYING: Detect applied status of oidc-auth-apps application (59 retries left).
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/ldap : Fail if oidc-auth-apps application apply failed] ***************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [Remote Metrics Server] *******************************************************************************************************************

TASK [remote/metrics-server : Set facts - 21.05] ***********************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Set facts - 21.12] ***********************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Get software load status] ****************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Noop if the system is NOT at the right caas_version] *************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Print message if system is NOT at the right caas_version] ********************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Detect presence of existing application] *************************************************************************
fatal: [welktxef-931887-rz-le2pts6-021]: FAILED! => {"changed": true, "cmd": ". /etc/platform/openrc\nsystem application-show metrics-server --column status --format value\n", "delta": "0:00:02.140364", "end": "2023-09-14 23:33:19.593022", "msg": "non-zero return code", "rc": 1, "start": "2023-09-14 23:33:17.452658", "stderr": "application not found: metrics-server", "stderr_lines": ["application not found: metrics-server"], "stdout": "", "stdout_lines": []}
...ignoring

TASK [remote/metrics-server : Print message if system already has the appication] **************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Apply again since the previous apply failed or in uploaded state] ************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Wait until apply is in the applied or apply-failed state] ********************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Print message if re-apply succeeds] ******************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Print message if re-apply failed] ********************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Noop if system requires no further action or needs manual investigation] *****************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Upload application] **********************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Wait until application is in the uploaded state] *****************************************************************
FAILED - RETRYING: Wait until application is in the uploaded state (30 retries left).
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Apply application] ***********************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Wait until application is in the applied or apply-failed state] **************************************************
FAILED - RETRYING: Wait until application is in the applied or apply-failed state (90 retries left).
FAILED - RETRYING: Wait until application is in the applied or apply-failed state (89 retries left).
FAILED - RETRYING: Wait until application is in the applied or apply-failed state (88 retries left).
FAILED - RETRYING: Wait until application is in the applied or apply-failed state (87 retries left).
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Apply again since the first apply failed] ************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Wait again until apply is in the applied or apply-failed state] **************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Print message if apply is successful] ****************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "msg": [
        "=======================================================",
        " welktxef-d931887-021: metrics-server install SUCCEEDED! ",
        "======================================================="
    ]
}

TASK [remote/metrics-server : Print message if apply is failure] *******************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [Remote wrap-get-central-version] *********************************************************************************************************

TASK [remote/wrap-get-central-version : Set facts for playbook] ********************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/wrap-get-central-version : Determine central WRA current version] *****************************************************************
fatal: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001]: FAILED! => {"changed": true, "cmd": ". /etc/platform/openrc\nsystem application-show wr-analytics --column app_version --format value\n", "delta": "0:00:01.266564", "end": "2023-09-14 23:34:42.998332", "msg": "non-zero return code", "rc": 1, "start": "2023-09-14 23:34:41.731768", "stderr": "application not found: wr-analytics", "stderr_lines": ["application not found: wr-analytics"], "stdout": "", "stdout_lines": []}
...ignoring

TASK [remote/wrap-get-central-version : Set facts for wra_target_version] **********************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/wrap-get-central-version : debug] *************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "msg": "wra_target_version:"
}

TASK [Remote wrap-2112-2] **********************************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [Remote wrap-2106-2] **********************************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [Remote wrap-6] ***************************************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [Remote fpga-user-image] ******************************************************************************************************************

TASK [remote/fpga-user-image : Set facts for ansible credential - 21.05] ***********************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Set facts for ansible credential - 21.12] ***********************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Get software load status] ***************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Noop if the system is NOT at the right caas_version] ************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Print message if system is NOT at the right caas_version] *******************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Set facts for default fpga_image_file] **************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Set facts for fpga_image_file from host_vars] *******************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Print message if server is not LS3 cascadelake] *****************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "msg": [
        "==================================================================================",
        " Server type ZTS-LS6-pts6 is not LS3 cascadelake, no action will take place! ",
        "=================================================================================="
    ]
}

TASK [remote/fpga-user-image : Register noop because server is not LS3 cascadelake] ************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Check if FPGA update is stuck] **********************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Abort FPGA update] **********************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : include_tasks] **************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Check FPGA update status (HPE-LS3-e910)] ************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Check FPGA update status (ZTS-LS3-trtn)] ************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Noop if the system has been updated] ****************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Print message if the system has been updated] *******************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : In main block] **************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Copy files to host] *********************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021] => (item=20ww43.5-1x2x25G-5GLDPC-v1.6.2-3.0.1-unsigned.bin)

TASK [remote/fpga-user-image : Do system device-image-upload] **********************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : debug - print UUID] *********************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Do system device-image-apply] ***********************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Do system host-device-image-update] *****************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Wait till application completed] ********************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Do system device-image-state-list] ******************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : force an error if image state is not completed] *****************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : include_tasks] **************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [Install DM Monitor] **********************************************************************************************************************

TASK [common/dm-monitor : Install DM Monitor] **************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [common/dm-monitor : Wait for DM Monitor pod created] *************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [common/dm-monitor : Wait for control-plane pods become ready] ****************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [common/dm-monitor : debug] ***************************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "dm_monitor_pod_ready.stdout_lines": [
        "pod/dm-monitor-77fd4b6649-hgtwr condition met"
    ]
}

TASK [Proteus MWIAT - DISABLE] *****************************************************************************************************************

TASK [remote/zt-redfish : Update Attributes at /redfish/v1/Systems/Self/Bios/SD] ***************************************************************
fatal: [welktxef-931887-rz-le2pts6-021 -> localhost]: FAILED! => {"allow": "GET, PUT, PATCH, POST", "changed": false, "connection": "close", "content": "{\"error\":{\"@Message.ExtendedInfo\":[{\"@odata.type\":\"#Message.v1_0_8.Message\",\"Message\":\"The requested operation is temporarily unavailable since Host System Reboot might be in progress or Host might be in Bios Setup or Redfish Inventory processing might be in progress. Please try after sometime.\",\"MessageId\":\"Ami.1.0.ServiceTemporarilyUnavailableDueToHostBooting\",\"Resolution\":\"Retry after some time.\",\"Severity\":\"Critical\"}],\"code\":\"Ami.1.0.ServiceTemporarilyUnavailableDueToHostBooting\",\"message\":\"The requested operation is temporarily unavailable since Host System Reboot might be in progress or Host might be in Bios Setup or Redfish Inventory processing might be in progress. Please try after sometime.\"}}", "content_length": "712", "content_type": "application/json; charset=UTF-8", "date": "Thu, 14 Sep 2023 23:34:56 GMT", "elapsed": 0, "json": {"error": {"@Message.ExtendedInfo": [{"@odata.type": "#Message.v1_0_8.Message", "Message": "The requested operation is temporarily unavailable since Host System Reboot might be in progress or Host might be in Bios Setup or Redfish Inventory processing might be in progress. Please try after sometime.", "MessageId": "Ami.1.0.ServiceTemporarilyUnavailableDueToHostBooting", "Resolution": "Retry after some time.", "Severity": "Critical"}], "code": "Ami.1.0.ServiceTemporarilyUnavailableDueToHostBooting", "message": "The requested operation is temporarily unavailable since Host System Reboot might be in progress or Host might be in Bios Setup or Redfish Inventory processing might be in progress. Please try after sometime."}}, "msg": "Status code was 503 and not [204]: HTTP Error 503: Service Not Available", "odata_version": "4.0", "redirected": false, "server": "AMI MegaRAC Redfish Service", "status": 503, "url": "https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Systems/Self/Bios/SD"}

PLAY RECAP *************************************************************************************************************************************
welktxef-931887-rz-le2pts6-021 : ok=116  changed=57   unreachable=0    failed=1    skipped=63   rescued=0    ignored=4

[XXXXXX@welktxefnce-h-pe1util-vm01 wr-installer]$


```


### suspect updating MWAIT was rejected, due to bug, I've experienced this on this .43 upgrade iteration manually while setting state


running commands to set MWAIT manually 

```log
[XXXXXX@vcpe-jumpserver ~]$ curl -k -w "\\n%{http_code} %{url_effective}\\n" -u XXXXXX:XXXXXX -H "Content-Type: application/json" -d '{"Attributes": {"PMS012": "Enable"}}' -X PATCH https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Systems/Self/Bios/SD
{"error":{"@Message.ExtendedInfo":[{"@odata.type":"#Message.v1_0_8.Message","Message":"The requested operation is temporarily unavailable since Host System Reboot might be in progress or Host might be in Bios Setup or Redfish Inventory processing might be in progress. Please try after sometime.","MessageId":"Ami.1.0.ServiceTemporarilyUnavailableDueToHostBooting","Resolution":"Retry after some time.","Severity":"Critical"}],"code":"Ami.1.0.ServiceTemporarilyUnavailableDueToHostBooting","message":"The requested operation is temporarily unavailable since Host System Reboot might be in progress or Host might be in Bios Setup or Redfish Inventory processing might be in progress. Please try after sometime."}}
503 https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Systems/Self/Bios/SD
[XXXXXX@vcpe-jumpserver ~]$ curl -k -w "\\n%{http_code} %{url_effective}\\n" -u XXXXXX:XXXXXX -H "Content-Type: application/json" -d '{"Attributes": {"PMS012": "Disable"}}' -X PATCH https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Systems/Self/Bios/SD
{"error":{"@Message.ExtendedInfo":[{"@odata.type":"#Message.v1_0_8.Message","Message":"The requested operation is temporarily unavailable since Host System Reboot might be in progress or Host might be in Bios Setup or Redfish Inventory processing might be in progress. Please try after sometime.","MessageId":"Ami.1.0.ServiceTemporarilyUnavailableDueToHostBooting","Resolution":"Retry after some time.","Severity":"Critical"}],"code":"Ami.1.0.ServiceTemporarilyUnavailableDueToHostBooting","message":"The requested operation is temporarily unavailable since Host System Reboot might be in progress or Host might be in Bios Setup or Redfish Inventory processing might be in progress. Please try after sometime."}}
503 https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Systems/Self/Bios/SD
[XXXXXX@vcpe-jumpserver ~]$
```

### trying ZT prescribed workaround which is to reset the Redfish DB


```sh
curl -sk -u XXXXXX:XXXXXX -X POST "https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Managers/Self/Actions/Oem/AMIManager.RedfishDBReset" -d '{"RedfishDBResetType": "ResetAll"}' -H "Content-Type: application/json" | python3 -m json.tool
```
```log
[XXXXXX@vcpe-jumpserver ~]$ curl -sk -u XXXXXX:XXXXXX -X POST "https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Managers/Self/Actions/Oem/AMIManager.RedfishDBReset" -d '{"RedfishDBResetType": "ResetAll"}' -H "Content-Type: application/json" | python3 -m json.tool
{
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.id": "/redfish/v1/TaskService/Tasks/1",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for RedfishDBReset Task",
    "Id": "1",
    "Name": "RedfishDBReset Task",
    "TaskState": "New"
}
[XXXXXX@vcpe-jumpserver ~]$

[XXXXXX@vcpe-jumpserver ~]$ curl -k -w "\\n%{http_code} %{url_effective}\\n" -u XXXXXX:XXXXXX -H "Content-Type: application/json" -d '{"Attributes": {"PMS012": "Disable"}}' -X PATCH https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Systems/Self/Bios/SD

204 https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Systems/Self/Bios/SD
[XXXXXX@vcpe-jumpserver ~]$ curl -k -w "\\n%{http_code} %{url_effective}\\n" -u XXXXXX:XXXXXX -H "Content-Type: application/json" -d '{"Attributes": {"PMS012": "Enable"}}' -X PATCH https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Systems/Self/Bios/SD

204 https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Systems/Self/Bios/SD
[XXXXXX@vcpe-jumpserver ~]$
```

### Reseting the redfish db resolves the issue in the db, however we must test more iterations to see how often this occurs.
### going to downgrade firmware to .36 and then move to .43 again before more testing.  Essentially the issue was caused by issue of .26-->.43, 
### so need to freshen the system to see if this redfish issue comes up again.


### Downgrade to .36 bmc

```log

[XXXXXX@welktxefnce-h-pe1util-vm01 ZT-Proteus-BMC-update-Redfish-v0.36.00-x86_64_20230328]$ ./update-bmc-redfish-python-v07-20230221.sh 2607:f160:10:9249:ce:40a:0:e015 XXXXXX XXXXXX ./welktxef-d931887-021_new_deployment_testing.txt force
===============================================================
          ZT BMC Update for Proteus
     update-bmc-redfish-python-v07-20230221.sh
                    02/21/2023
                     Ver 0.07
===============================================================

2023-09-14-19:57:39  Check if IP address is valid
2023-09-14-19:57:39  IPv6 IP detected
2023-09-14-19:57:40  2607:f160:10:9249:ce:40a:0:e015 is a valid IP
2023-09-14-19:57:40  IPv6 Address is 2607:f160:10:9249:ce:40a:0:e015
2023-09-14-19:57:42  Redfish Creditials are correct, continue update
2023-09-14-19:57:42  Check if right version of python3 is installed
2023-09-14-19:57:42  Python3 is installed, continue update
2023-09-14-19:57:44  Model name is Proteus
2023-09-14-19:57:44  Product is Proteus or Force option is slected, ok to proceed
2023-09-14-19:57:44  System Serial is 20741213N074
2023-09-14-19:57:44  BMC current version is 0.43.00
2023-09-14-19:57:44  Preparing to update BMC.....
2023-09-14-19:57:44  Update can take ~10 to ~12 minutes
2023-09-14-19:57:59  Updating BMC please wait till the update is finished
20230914_195804 Version 3.0.9
20230914_195804 Copyright 2021 ZT Group Int'l, Inc. All Rights Reserved.
20230914_195804 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1
20230914_195804 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/UpdateService
20230914_195805 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/UpdateService/FirmwareInventory
20230914_195805 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/UpdateService/FirmwareInventory/BMC
20230914_195805 {
    "@odata.context": "/redfish/v1/$metadata#SoftwareInventory.SoftwareInventory",
    "@odata.etag": "\"1694738882\"",
    "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/BMC",
    "@odata.type": "#SoftwareInventory.v1_2_3.SoftwareInventory",
    "Id": "BMC",
    "Name": "BMC",
    "Updateable": true,
    "Version": "0.43.00"
}
20230914_195805 fwversion = [0.43.00]
20230914_195805 Initial BMC FW version: [0.43.00]
20230914_195805 initiate_fwupdate from /home/XXXXXX/ZT_FW/ZT-Proteus-BMC-update-Redfish-v0.36.00-x86_64_20230328 with v0.36.00.ima via redfish/v1/UpdateService/FirmwareInventory/BMC [timeout=300]
20230914_195805 JSON update_parameters : {"Targets": ["/redfish/v1/UpdateService/FirmwareInventory/BMC"]}
20230914_195805 JSON OEM_parameters    : {"ImageType": "BMC"}
20230914_195805 POST: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/UpdateService/upload
20230914_195905 POST done: return code 202
20230914_195905 POST done: return data:
<Response [202]>
20230914_195905 {"@odata.type":"#UpdateService.v1_6_0.UpdateService","Messages":[{"@odata.type":"#Message.v1_0_8.Message","Message":"A new task /redfish/v1/TaskService/Tasks/2 was created.","MessageArgs":["/redfish/v1/TaskService/Tasks/2"],"MessageId":"Task.1.0.New","Resolution":"None","Severity":"OK"},{"@odata.type":"#Message.v1_0_8.Message","Message":"The action UpdateService.MultipartPush was submitted to do firmware update.","MessageArgs":["UpdateService.MultipartPush"],"MessageId":"UpdateService.1.0.StartFirmwareUpdate","Resolution":"None","Severity":"OK"}]}
20230914_195905 initiate_fwupdate returns polling uri: redfish/v1/TaskService/Tasks/2
20230914_200005 Polling for up to 60 seconds to check that the update starts
20230914_200005 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200006 Update status : Running
20230914_200006 Polling for up to 1500 seconds to check that the update completes properly
20230914_200006 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200006 Update status : Running (Percent complete = 0)
20230914_200006 Checking status on redfish/v1/TaskService/Tasks/2
20230914_200006 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200007 Task     status : Running (Percent complete = 0)
20230914_200007 Found 2 messages from [redfish/v1/TaskService/Tasks/2]
20230914_200007 {"@odata.context": "/redfish/v1/$metadata#Task.Task", "@odata.etag": "\"1694739545\"", "@odata.id": "/redfish/v1/TaskService/Tasks/2", "@odata.type": "#Task.v1_4_2.Task", "Description": "Task for Update Service Task", "Id": "2", "Messages": [{"@odata.type": "#Message.v1_0_8.Message", "Message": "Task /redfish/v1/UpdateService/upload is running normally.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "Task.1.0.Running", "Resolution": "None", "Severity": "OK"}, {"@odata.type": "#Message.v1_0_8.Message", "Message": "Device is prepareing flash area for action /redfish/v1/UpdateService/upload.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "UpdateService.1.0.PrepareFlashArea", "Resolution": "None", "Severity": "OK"}], "Name": "Update Service Task", "PercentComplete": 0, "TaskState": "Running", "TaskStatus": "OK"}
20230914_200007     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20230914_200007     Unknown             OK          Device is prepareing flash area for action /redfish/v1/UpdateService/upload.
20230914_200012 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200012 Update status : Running (Percent complete = 0)
20230914_200012 Checking status on redfish/v1/TaskService/Tasks/2
20230914_200012 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200013 Task     status : Running (Percent complete = 0)
20230914_200013 Found 2 messages from [redfish/v1/TaskService/Tasks/2]
20230914_200013 {"@odata.context": "/redfish/v1/$metadata#Task.Task", "@odata.etag": "\"1694739545\"", "@odata.id": "/redfish/v1/TaskService/Tasks/2", "@odata.type": "#Task.v1_4_2.Task", "Description": "Task for Update Service Task", "Id": "2", "Messages": [{"@odata.type": "#Message.v1_0_8.Message", "Message": "Task /redfish/v1/UpdateService/upload is running normally.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "Task.1.0.Running", "Resolution": "None", "Severity": "OK"}, {"@odata.type": "#Message.v1_0_8.Message", "Message": "Device is verifying firmware image file which from Remote Path - /tmp/redfishfwupdate//rom.ima for action /redfish/v1/UpdateService/upload.", "MessageArgs": ["/tmp/redfishfwupdate//rom.ima", "/redfish/v1/UpdateService/upload"], "MessageId": "UpdateService.1.0.VerifyFirmware", "Resolution": "None", "Severity": "OK"}], "Name": "Update Service Task", "PercentComplete": 0, "TaskState": "Running", "TaskStatus": "OK"}
20230914_200013     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20230914_200013     Unknown             OK          Device is verifying firmware image file which from Remote Path - /tmp/redfishfwupdate//rom.ima for action /redfish/v1/UpdateService/upload.
20230914_200018 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200018 Update status : Running (Percent complete = 0)
20230914_200018 Checking status on redfish/v1/TaskService/Tasks/2
20230914_200018 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200019 Task     status : Running (Percent complete = 0)
20230914_200019 Found 2 messages from [redfish/v1/TaskService/Tasks/2]
20230914_200019 {"@odata.context": "/redfish/v1/$metadata#Task.Task", "@odata.etag": "\"1694739545\"", "@odata.id": "/redfish/v1/TaskService/Tasks/2", "@odata.type": "#Task.v1_4_2.Task", "Description": "Task for Update Service Task", "Id": "2", "Messages": [{"@odata.type": "#Message.v1_0_8.Message", "Message": "Task /redfish/v1/UpdateService/upload is running normally.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "Task.1.0.Running", "Resolution": "None", "Severity": "OK"}, {"@odata.type": "#Message.v1_0_8.Message", "Message": "Device is verifying firmware image file which from Remote Path - /tmp/redfishfwupdate//rom.ima for action /redfish/v1/UpdateService/upload.", "MessageArgs": ["/tmp/redfishfwupdate//rom.ima", "/redfish/v1/UpdateService/upload"], "MessageId": "UpdateService.1.0.VerifyFirmware", "Resolution": "None", "Severity": "OK"}], "Name": "Update Service Task", "PercentComplete": 0, "TaskState": "Running", "TaskStatus": "OK"}
20230914_200019     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20230914_200019     Unknown             OK          Device is verifying firmware image file which from Remote Path - /tmp/redfishfwupdate//rom.ima for action /redfish/v1/UpdateService/upload.
20230914_200024 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200024 Update status : Running
20230914_200024 Checking status on redfish/v1/TaskService/Tasks/2
20230914_200024 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200024 Task     status : Running
20230914_200024 Found 2 messages from [redfish/v1/TaskService/Tasks/2]
20230914_200024 {"@odata.context": "/redfish/v1/$metadata#Task.Task", "@odata.etag": "\"1694739545\"", "@odata.id": "/redfish/v1/TaskService/Tasks/2", "@odata.type": "#Task.v1_4_2.Task", "Description": "Task for Update Service Task", "Id": "2", "Messages": [{"@odata.type": "#Message.v1_0_8.Message", "Message": "Task /redfish/v1/UpdateService/upload is running normally.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "Task.1.0.Running", "Resolution": "None", "Severity": "OK"}, {"@odata.type": "#Message.v1_0_8.Message", "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "UpdateService.1.0.FlashFirmware", "Resolution": "None", "Severity": "OK"}], "Name": "Update Service Task", "TaskState": "Running", "TaskStatus": "OK"}
20230914_200024     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20230914_200024     Unknown             OK          Device is flashing firmware for action /redfish/v1/UpdateService/upload.
20230914_200029 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200030 Update status : Running (Percent complete = 2)
20230914_200030 Checking status on redfish/v1/TaskService/Tasks/2
20230914_200030 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200030 Task     status : Running (Percent complete = 2)
20230914_200030 Found 2 messages from [redfish/v1/TaskService/Tasks/2]
20230914_200030 {"@odata.context": "/redfish/v1/$metadata#Task.Task", "@odata.etag": "\"1694739545\"", "@odata.id": "/redfish/v1/TaskService/Tasks/2", "@odata.type": "#Task.v1_4_2.Task", "Description": "Task for Update Service Task", "Id": "2", "Messages": [{"@odata.type": "#Message.v1_0_8.Message", "Message": "Task /redfish/v1/UpdateService/upload is running normally.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "Task.1.0.Running", "Resolution": "None", "Severity": "OK"}, {"@odata.type": "#Message.v1_0_8.Message", "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "UpdateService.1.0.FlashFirmware", "Resolution": "None", "Severity": "OK"}], "Name": "Update Service Task", "PercentComplete": 2, "TaskState": "Running", "TaskStatus": "OK"}
20230914_200030     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20230914_200030     Unknown             OK          Device is flashing firmware for action /redfish/v1/UpdateService/upload.
20230914_200035 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200036 Update status : Running (Percent complete = 5)
20230914_200036 Checking status on redfish/v1/TaskService/Tasks/2
20230914_200036 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200036 Task     status : Running (Percent complete = 5)
20230914_200036 Found 2 messages from [redfish/v1/TaskService/Tasks/2]
20230914_200036 {"@odata.context": "/redfish/v1/$metadata#Task.Task", "@odata.etag": "\"1694739545\"", "@odata.id": "/redfish/v1/TaskService/Tasks/2", "@odata.type": "#Task.v1_4_2.Task", "Description": "Task for Update Service Task", "Id": "2", "Messages": [{"@odata.type": "#Message.v1_0_8.Message", "Message": "Task /redfish/v1/UpdateService/upload is running normally.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "Task.1.0.Running", "Resolution": "None", "Severity": "OK"}, {"@odata.type": "#Message.v1_0_8.Message", "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "UpdateService.1.0.FlashFirmware", "Resolution": "None", "Severity": "OK"}], "Name": "Update Service Task", "PercentComplete": 5, "TaskState": "Running", "TaskStatus": "OK"}
20230914_200036     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20230914_200036     Unknown             OK          Device is flashing firmware for action /redfish/v1/UpdateService/upload.
20230914_200041 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200042 Update status : Running (Percent complete = 6)
20230914_200042 Checking status on redfish/v1/TaskService/Tasks/2
20230914_200042 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200042 Task     status : Running (Percent complete = 6)
20230914_200042 Found 2 messages from [redfish/v1/TaskService/Tasks/2]
20230914_200042 {"@odata.context": "/redfish/v1/$metadata#Task.Task", "@odata.etag": "\"1694739545\"", "@odata.id": "/redfish/v1/TaskService/Tasks/2", "@odata.type": "#Task.v1_4_2.Task", "Description": "Task for Update Service Task", "Id": "2", "Messages": [{"@odata.type": "#Message.v1_0_8.Message", "Message": "Task /redfish/v1/UpdateService/upload is running normally.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "Task.1.0.Running", "Resolution": "None", "Severity": "OK"}, {"@odata.type": "#Message.v1_0_8.Message", "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "UpdateService.1.0.FlashFirmware", "Resolution": "None", "Severity": "OK"}], "Name": "Update Service Task", "PercentComplete": 6, "TaskState": "Running", "TaskStatus": "OK"}
20230914_200042     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20230914_200042     Unknown             OK          Device is flashing firmware for action /redfish/v1/UpdateService/upload.
20230914_200047 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200047 Update status : Running (Percent complete = 8)
20230914_200047 Checking status on redfish/v1/TaskService/Tasks/2
20230914_200047 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200048 Task     status : Running (Percent complete = 8)
20230914_200048 Found 2 messages from [redfish/v1/TaskService/Tasks/2]
20230914_200048 {"@odata.context": "/redfish/v1/$metadata#Task.Task", "@odata.etag": "\"1694739545\"", "@odata.id": "/redfish/v1/TaskService/Tasks/2", "@odata.type": "#Task.v1_4_2.Task", "Description": "Task for Update Service Task", "Id": "2", "Messages": [{"@odata.type": "#Message.v1_0_8.Message", "Message": "Task /redfish/v1/UpdateService/upload is running normally.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "Task.1.0.Running", "Resolution": "None", "Severity": "OK"}, {"@odata.type": "#Message.v1_0_8.Message", "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "UpdateService.1.0.FlashFirmware", "Resolution": "None", "Severity": "OK"}], "Name": "Update Service Task", "PercentComplete": 8, "TaskState": "Running", "TaskStatus": "OK"}
20230914_200048     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20230914_200048     Unknown             OK          Device is flashing firmware for action /redfish/v1/UpdateService/upload.
20230914_200053 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200053 Update status : Running (Percent complete = 10)
20230914_200053 Checking status on redfish/v1/TaskService/Tasks/2
20230914_200053 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200054 Task     status : Running (Percent complete = 10)
20230914_200054 Found 2 messages from [redfish/v1/TaskService/Tasks/2]
20230914_200054 {"@odata.context": "/redfish/v1/$metadata#Task.Task", "@odata.etag": "\"1694739545\"", "@odata.id": "/redfish/v1/TaskService/Tasks/2", "@odata.type": "#Task.v1_4_2.Task", "Description": "Task for Update Service Task", "Id": "2", "Messages": [{"@odata.type": "#Message.v1_0_8.Message", "Message": "Task /redfish/v1/UpdateService/upload is running normally.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "Task.1.0.Running", "Resolution": "None", "Severity": "OK"}, {"@odata.type": "#Message.v1_0_8.Message", "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "UpdateService.1.0.FlashFirmware", "Resolution": "None", "Severity": "OK"}], "Name": "Update Service Task", "PercentComplete": 10, "TaskState": "Running", "TaskStatus": "OK"}
20230914_200054     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20230914_200054     Unknown             OK          Device is flashing firmware for action /redfish/v1/UpdateService/upload.
20230914_200059 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200059 Update status : Running (Percent complete = 12)
20230914_200059 Checking status on redfish/v1/TaskService/Tasks/2
20230914_200059 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200100 Task     status : Running (Percent complete = 12)
20230914_200100 Found 2 messages from [redfish/v1/TaskService/Tasks/2]
20230914_200100 {"@odata.context": "/redfish/v1/$metadata#Task.Task", "@odata.etag": "\"1694739545\"", "@odata.id": "/redfish/v1/TaskService/Tasks/2", "@odata.type": "#Task.v1_4_2.Task", "Description": "Task for Update Service Task", "Id": "2", "Messages": [{"@odata.type": "#Message.v1_0_8.Message", "Message": "Task /redfish/v1/UpdateService/upload is running normally.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "Task.1.0.Running", "Resolution": "None", "Severity": "OK"}, {"@odata.type": "#Message.v1_0_8.Message", "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "UpdateService.1.0.FlashFirmware", "Resolution": "None", "Severity": "OK"}], "Name": "Update Service Task", "PercentComplete": 12, "TaskState": "Running", "TaskStatus": "OK"}
20230914_200100     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20230914_200100     Unknown             OK          Device is flashing firmware for action /redfish/v1/UpdateService/upload.
20230914_200105 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200105 Update status : Running (Percent complete = 14)
20230914_200105 Checking status on redfish/v1/TaskService/Tasks/2
20230914_200105 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200105 Task     status : Running (Percent complete = 14)
20230914_200105 Found 2 messages from [redfish/v1/TaskService/Tasks/2]
20230914_200105 {"@odata.context": "/redfish/v1/$metadata#Task.Task", "@odata.etag": "\"1694739545\"", "@odata.id": "/redfish/v1/TaskService/Tasks/2", "@odata.type": "#Task.v1_4_2.Task", "Description": "Task for Update Service Task", "Id": "2", "Messages": [{"@odata.type": "#Message.v1_0_8.Message", "Message": "Task /redfish/v1/UpdateService/upload is running normally.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "Task.1.0.Running", "Resolution": "None", "Severity": "OK"}, {"@odata.type": "#Message.v1_0_8.Message", "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "UpdateService.1.0.FlashFirmware", "Resolution": "None", "Severity": "OK"}], "Name": "Update Service Task", "PercentComplete": 14, "TaskState": "Running", "TaskStatus": "OK"}
20230914_200105     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20230914_200105     Unknown             OK          Device is flashing firmware for action /redfish/v1/UpdateService/upload.
20230914_200110 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200111 Update status : Running (Percent complete = 16)
20230914_200111 Checking status on redfish/v1/TaskService/Tasks/2
20230914_200111 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200111 Task     status : Running (Percent complete = 16)
20230914_200111 Found 2 messages from [redfish/v1/TaskService/Tasks/2]
20230914_200111 {"@odata.context": "/redfish/v1/$metadata#Task.Task", "@odata.etag": "\"1694739545\"", "@odata.id": "/redfish/v1/TaskService/Tasks/2", "@odata.type": "#Task.v1_4_2.Task", "Description": "Task for Update Service Task", "Id": "2", "Messages": [{"@odata.type": "#Message.v1_0_8.Message", "Message": "Task /redfish/v1/UpdateService/upload is running normally.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "Task.1.0.Running", "Resolution": "None", "Severity": "OK"}, {"@odata.type": "#Message.v1_0_8.Message", "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "UpdateService.1.0.FlashFirmware", "Resolution": "None", "Severity": "OK"}], "Name": "Update Service Task", "PercentComplete": 16, "TaskState": "Running", "TaskStatus": "OK"}
20230914_200111     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20230914_200111     Unknown             OK          Device is flashing firmware for action /redfish/v1/UpdateService/upload.
20230914_200116 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200117 Update status : Running (Percent complete = 17)
20230914_200117 Checking status on redfish/v1/TaskService/Tasks/2
20230914_200117 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200117 Task     status : Running (Percent complete = 18)
20230914_200117 Found 2 messages from [redfish/v1/TaskService/Tasks/2]
20230914_200117 {"@odata.context": "/redfish/v1/$metadata#Task.Task", "@odata.etag": "\"1694739545\"", "@odata.id": "/redfish/v1/TaskService/Tasks/2", "@odata.type": "#Task.v1_4_2.Task", "Description": "Task for Update Service Task", "Id": "2", "Messages": [{"@odata.type": "#Message.v1_0_8.Message", "Message": "Task /redfish/v1/UpdateService/upload is running normally.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "Task.1.0.Running", "Resolution": "None", "Severity": "OK"}, {"@odata.type": "#Message.v1_0_8.Message", "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "UpdateService.1.0.FlashFirmware", "Resolution": "None", "Severity": "OK"}], "Name": "Update Service Task", "PercentComplete": 18, "TaskState": "Running", "TaskStatus": "OK"}
20230914_200117     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20230914_200117     Unknown             OK          Device is flashing firmware for action /redfish/v1/UpdateService/upload.
20230914_200122 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200123 Update status : Running (Percent complete = 19)
20230914_200123 Checking status on redfish/v1/TaskService/Tasks/2
20230914_200123 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200123 Task     status : Running (Percent complete = 19)
20230914_200123 Found 2 messages from [redfish/v1/TaskService/Tasks/2]
20230914_200123 {"@odata.context": "/redfish/v1/$metadata#Task.Task", "@odata.etag": "\"1694739545\"", "@odata.id": "/redfish/v1/TaskService/Tasks/2", "@odata.type": "#Task.v1_4_2.Task", "Description": "Task for Update Service Task", "Id": "2", "Messages": [{"@odata.type": "#Message.v1_0_8.Message", "Message": "Task /redfish/v1/UpdateService/upload is running normally.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "Task.1.0.Running", "Resolution": "None", "Severity": "OK"}, {"@odata.type": "#Message.v1_0_8.Message", "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "UpdateService.1.0.FlashFirmware", "Resolution": "None", "Severity": "OK"}], "Name": "Update Service Task", "PercentComplete": 19, "TaskState": "Running", "TaskStatus": "OK"}
20230914_200123     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20230914_200123     Unknown             OK          Device is flashing firmware for action /redfish/v1/UpdateService/upload.
20230914_200128 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200128 Update status : Running (Percent complete = 21)
20230914_200128 Checking status on redfish/v1/TaskService/Tasks/2
20230914_200128 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200129 Task     status : Running (Percent complete = 21)
20230914_200129 Found 2 messages from [redfish/v1/TaskService/Tasks/2]
20230914_200129 {"@odata.context": "/redfish/v1/$metadata#Task.Task", "@odata.etag": "\"1694739545\"", "@odata.id": "/redfish/v1/TaskService/Tasks/2", "@odata.type": "#Task.v1_4_2.Task", "Description": "Task for Update Service Task", "Id": "2", "Messages": [{"@odata.type": "#Message.v1_0_8.Message", "Message": "Task /redfish/v1/UpdateService/upload is running normally.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "Task.1.0.Running", "Resolution": "None", "Severity": "OK"}, {"@odata.type": "#Message.v1_0_8.Message", "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "UpdateService.1.0.FlashFirmware", "Resolution": "None", "Severity": "OK"}], "Name": "Update Service Task", "PercentComplete": 21, "TaskState": "Running", "TaskStatus": "OK"}
20230914_200129     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20230914_200129     Unknown             OK          Device is flashing firmware for action /redfish/v1/UpdateService/upload.
20230914_200134 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200134 Update status : Running (Percent complete = 23)
20230914_200134 Checking status on redfish/v1/TaskService/Tasks/2
20230914_200134 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200135 Task     status : Running (Percent complete = 23)
20230914_200135 Found 2 messages from [redfish/v1/TaskService/Tasks/2]
20230914_200135 {"@odata.context": "/redfish/v1/$metadata#Task.Task", "@odata.etag": "\"1694739545\"", "@odata.id": "/redfish/v1/TaskService/Tasks/2", "@odata.type": "#Task.v1_4_2.Task", "Description": "Task for Update Service Task", "Id": "2", "Messages": [{"@odata.type": "#Message.v1_0_8.Message", "Message": "Task /redfish/v1/UpdateService/upload is running normally.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "Task.1.0.Running", "Resolution": "None", "Severity": "OK"}, {"@odata.type": "#Message.v1_0_8.Message", "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "UpdateService.1.0.FlashFirmware", "Resolution": "None", "Severity": "OK"}], "Name": "Update Service Task", "PercentComplete": 23, "TaskState": "Running", "TaskStatus": "OK"}
20230914_200135     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20230914_200135     Unknown             OK          Device is flashing firmware for action /redfish/v1/UpdateService/upload.
20230914_200140 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200140 Update status : Running (Percent complete = 24)
20230914_200140 Checking status on redfish/v1/TaskService/Tasks/2
20230914_200140 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200141 Task     status : Running (Percent complete = 24)
20230914_200141 Found 2 messages from [redfish/v1/TaskService/Tasks/2]
20230914_200141 {"@odata.context": "/redfish/v1/$metadata#Task.Task", "@odata.etag": "\"1694739545\"", "@odata.id": "/redfish/v1/TaskService/Tasks/2", "@odata.type": "#Task.v1_4_2.Task", "Description": "Task for Update Service Task", "Id": "2", "Messages": [{"@odata.type": "#Message.v1_0_8.Message", "Message": "Task /redfish/v1/UpdateService/upload is running normally.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "Task.1.0.Running", "Resolution": "None", "Severity": "OK"}, {"@odata.type": "#Message.v1_0_8.Message", "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "UpdateService.1.0.FlashFirmware", "Resolution": "None", "Severity": "OK"}], "Name": "Update Service Task", "PercentComplete": 24, "TaskState": "Running", "TaskStatus": "OK"}
20230914_200141     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20230914_200141     Unknown             OK          Device is flashing firmware for action /redfish/v1/UpdateService/upload.
20230914_200146 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200146 Update status : Running (Percent complete = 26)
20230914_200146 Checking status on redfish/v1/TaskService/Tasks/2
20230914_200146 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200147 Task     status : Running (Percent complete = 26)
20230914_200147 Found 2 messages from [redfish/v1/TaskService/Tasks/2]
20230914_200147 {"@odata.context": "/redfish/v1/$metadata#Task.Task", "@odata.etag": "\"1694739545\"", "@odata.id": "/redfish/v1/TaskService/Tasks/2", "@odata.type": "#Task.v1_4_2.Task", "Description": "Task for Update Service Task", "Id": "2", "Messages": [{"@odata.type": "#Message.v1_0_8.Message", "Message": "Task /redfish/v1/UpdateService/upload is running normally.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "Task.1.0.Running", "Resolution": "None", "Severity": "OK"}, {"@odata.type": "#Message.v1_0_8.Message", "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "UpdateService.1.0.FlashFirmware", "Resolution": "None", "Severity": "OK"}], "Name": "Update Service Task", "PercentComplete": 26, "TaskState": "Running", "TaskStatus": "OK"}
20230914_200147     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20230914_200147     Unknown             OK          Device is flashing firmware for action /redfish/v1/UpdateService/upload.
20230914_200152 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200152 Update status : Running (Percent complete = 28)
20230914_200152 Checking status on redfish/v1/TaskService/Tasks/2
20230914_200152 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200152 Task     status : Running (Percent complete = 28)
20230914_200152 Found 2 messages from [redfish/v1/TaskService/Tasks/2]
20230914_200152 {"@odata.context": "/redfish/v1/$metadata#Task.Task", "@odata.etag": "\"1694739545\"", "@odata.id": "/redfish/v1/TaskService/Tasks/2", "@odata.type": "#Task.v1_4_2.Task", "Description": "Task for Update Service Task", "Id": "2", "Messages": [{"@odata.type": "#Message.v1_0_8.Message", "Message": "Task /redfish/v1/UpdateService/upload is running normally.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "Task.1.0.Running", "Resolution": "None", "Severity": "OK"}, {"@odata.type": "#Message.v1_0_8.Message", "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "UpdateService.1.0.FlashFirmware", "Resolution": "None", "Severity": "OK"}], "Name": "Update Service Task", "PercentComplete": 28, "TaskState": "Running", "TaskStatus": "OK"}
20230914_200152     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20230914_200152     Unknown             OK          Device is flashing firmware for action /redfish/v1/UpdateService/upload.
20230914_200157 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200158 Update status : Running (Percent complete = 29)
20230914_200158 Checking status on redfish/v1/TaskService/Tasks/2
20230914_200158 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200158 Task     status : Running (Percent complete = 30)
20230914_200158 Found 2 messages from [redfish/v1/TaskService/Tasks/2]
20230914_200158 {"@odata.context": "/redfish/v1/$metadata#Task.Task", "@odata.etag": "\"1694739545\"", "@odata.id": "/redfish/v1/TaskService/Tasks/2", "@odata.type": "#Task.v1_4_2.Task", "Description": "Task for Update Service Task", "Id": "2", "Messages": [{"@odata.type": "#Message.v1_0_8.Message", "Message": "Task /redfish/v1/UpdateService/upload is running normally.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "Task.1.0.Running", "Resolution": "None", "Severity": "OK"}, {"@odata.type": "#Message.v1_0_8.Message", "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "UpdateService.1.0.FlashFirmware", "Resolution": "None", "Severity": "OK"}], "Name": "Update Service Task", "PercentComplete": 30, "TaskState": "Running", "TaskStatus": "OK"}
20230914_200158     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20230914_200158     Unknown             OK          Device is flashing firmware for action /redfish/v1/UpdateService/upload.
20230914_200203 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200204 Update status : Running (Percent complete = 31)
20230914_200204 Checking status on redfish/v1/TaskService/Tasks/2
20230914_200204 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200204 Task     status : Running (Percent complete = 31)
20230914_200204 Found 2 messages from [redfish/v1/TaskService/Tasks/2]
20230914_200204 {"@odata.context": "/redfish/v1/$metadata#Task.Task", "@odata.etag": "\"1694739545\"", "@odata.id": "/redfish/v1/TaskService/Tasks/2", "@odata.type": "#Task.v1_4_2.Task", "Description": "Task for Update Service Task", "Id": "2", "Messages": [{"@odata.type": "#Message.v1_0_8.Message", "Message": "Task /redfish/v1/UpdateService/upload is running normally.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "Task.1.0.Running", "Resolution": "None", "Severity": "OK"}, {"@odata.type": "#Message.v1_0_8.Message", "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "UpdateService.1.0.FlashFirmware", "Resolution": "None", "Severity": "OK"}], "Name": "Update Service Task", "PercentComplete": 31, "TaskState": "Running", "TaskStatus": "OK"}
20230914_200204     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20230914_200204     Unknown             OK          Device is flashing firmware for action /redfish/v1/UpdateService/upload.
20230914_200209 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200210 Update status : Running (Percent complete = 33)
20230914_200210 Checking status on redfish/v1/TaskService/Tasks/2
20230914_200210 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200210 Task     status : Running (Percent complete = 33)
20230914_200210 Found 2 messages from [redfish/v1/TaskService/Tasks/2]
20230914_200210 {"@odata.context": "/redfish/v1/$metadata#Task.Task", "@odata.etag": "\"1694739545\"", "@odata.id": "/redfish/v1/TaskService/Tasks/2", "@odata.type": "#Task.v1_4_2.Task", "Description": "Task for Update Service Task", "Id": "2", "Messages": [{"@odata.type": "#Message.v1_0_8.Message", "Message": "Task /redfish/v1/UpdateService/upload is running normally.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "Task.1.0.Running", "Resolution": "None", "Severity": "OK"}, {"@odata.type": "#Message.v1_0_8.Message", "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "UpdateService.1.0.FlashFirmware", "Resolution": "None", "Severity": "OK"}], "Name": "Update Service Task", "PercentComplete": 33, "TaskState": "Running", "TaskStatus": "OK"}
20230914_200210     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20230914_200210     Unknown             OK          Device is flashing firmware for action /redfish/v1/UpdateService/upload.
20230914_200215 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200216 Update status : Running (Percent complete = 35)
20230914_200216 Checking status on redfish/v1/TaskService/Tasks/2
20230914_200216 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200216 Task     status : Running (Percent complete = 35)
20230914_200216 Found 2 messages from [redfish/v1/TaskService/Tasks/2]
20230914_200216 {"@odata.context": "/redfish/v1/$metadata#Task.Task", "@odata.etag": "\"1694739545\"", "@odata.id": "/redfish/v1/TaskService/Tasks/2", "@odata.type": "#Task.v1_4_2.Task", "Description": "Task for Update Service Task", "Id": "2", "Messages": [{"@odata.type": "#Message.v1_0_8.Message", "Message": "Task /redfish/v1/UpdateService/upload is running normally.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "Task.1.0.Running", "Resolution": "None", "Severity": "OK"}, {"@odata.type": "#Message.v1_0_8.Message", "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "UpdateService.1.0.FlashFirmware", "Resolution": "None", "Severity": "OK"}], "Name": "Update Service Task", "PercentComplete": 35, "TaskState": "Running", "TaskStatus": "OK"}
20230914_200216     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20230914_200216     Unknown             OK          Device is flashing firmware for action /redfish/v1/UpdateService/upload.
20230914_200221 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200221 Update status : Running (Percent complete = 36)
20230914_200221 Checking status on redfish/v1/TaskService/Tasks/2
20230914_200221 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200222 Task     status : Running (Percent complete = 36)
20230914_200222 Found 2 messages from [redfish/v1/TaskService/Tasks/2]
20230914_200222 {"@odata.context": "/redfish/v1/$metadata#Task.Task", "@odata.etag": "\"1694739545\"", "@odata.id": "/redfish/v1/TaskService/Tasks/2", "@odata.type": "#Task.v1_4_2.Task", "Description": "Task for Update Service Task", "Id": "2", "Messages": [{"@odata.type": "#Message.v1_0_8.Message", "Message": "Task /redfish/v1/UpdateService/upload is running normally.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "Task.1.0.Running", "Resolution": "None", "Severity": "OK"}, {"@odata.type": "#Message.v1_0_8.Message", "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "UpdateService.1.0.FlashFirmware", "Resolution": "None", "Severity": "OK"}], "Name": "Update Service Task", "PercentComplete": 36, "TaskState": "Running", "TaskStatus": "OK"}
20230914_200222     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20230914_200222     Unknown             OK          Device is flashing firmware for action /redfish/v1/UpdateService/upload.
20230914_200227 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200227 Update status : Running (Percent complete = 38)
20230914_200227 Checking status on redfish/v1/TaskService/Tasks/2
20230914_200227 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200228 Task     status : Running (Percent complete = 38)
20230914_200228 Found 2 messages from [redfish/v1/TaskService/Tasks/2]
20230914_200228 {"@odata.context": "/redfish/v1/$metadata#Task.Task", "@odata.etag": "\"1694739545\"", "@odata.id": "/redfish/v1/TaskService/Tasks/2", "@odata.type": "#Task.v1_4_2.Task", "Description": "Task for Update Service Task", "Id": "2", "Messages": [{"@odata.type": "#Message.v1_0_8.Message", "Message": "Task /redfish/v1/UpdateService/upload is running normally.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "Task.1.0.Running", "Resolution": "None", "Severity": "OK"}, {"@odata.type": "#Message.v1_0_8.Message", "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "UpdateService.1.0.FlashFirmware", "Resolution": "None", "Severity": "OK"}], "Name": "Update Service Task", "PercentComplete": 38, "TaskState": "Running", "TaskStatus": "OK"}
20230914_200228     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20230914_200228     Unknown             OK          Device is flashing firmware for action /redfish/v1/UpdateService/upload.
20230914_200233 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200233 Update status : Running (Percent complete = 40)
20230914_200233 Checking status on redfish/v1/TaskService/Tasks/2
20230914_200233 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200233 Task     status : Running (Percent complete = 40)
20230914_200233 Found 2 messages from [redfish/v1/TaskService/Tasks/2]
20230914_200233 {"@odata.context": "/redfish/v1/$metadata#Task.Task", "@odata.etag": "\"1694739545\"", "@odata.id": "/redfish/v1/TaskService/Tasks/2", "@odata.type": "#Task.v1_4_2.Task", "Description": "Task for Update Service Task", "Id": "2", "Messages": [{"@odata.type": "#Message.v1_0_8.Message", "Message": "Task /redfish/v1/UpdateService/upload is running normally.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "Task.1.0.Running", "Resolution": "None", "Severity": "OK"}, {"@odata.type": "#Message.v1_0_8.Message", "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "UpdateService.1.0.FlashFirmware", "Resolution": "None", "Severity": "OK"}], "Name": "Update Service Task", "PercentComplete": 40, "TaskState": "Running", "TaskStatus": "OK"}
20230914_200233     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20230914_200233     Unknown             OK          Device is flashing firmware for action /redfish/v1/UpdateService/upload.
20230914_200238 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200239 Update status : Running (Percent complete = 42)
20230914_200239 Checking status on redfish/v1/TaskService/Tasks/2
20230914_200239 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200239 Task     status : Running (Percent complete = 42)
20230914_200239 Found 2 messages from [redfish/v1/TaskService/Tasks/2]
20230914_200239 {"@odata.context": "/redfish/v1/$metadata#Task.Task", "@odata.etag": "\"1694739545\"", "@odata.id": "/redfish/v1/TaskService/Tasks/2", "@odata.type": "#Task.v1_4_2.Task", "Description": "Task for Update Service Task", "Id": "2", "Messages": [{"@odata.type": "#Message.v1_0_8.Message", "Message": "Task /redfish/v1/UpdateService/upload is running normally.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "Task.1.0.Running", "Resolution": "None", "Severity": "OK"}, {"@odata.type": "#Message.v1_0_8.Message", "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "UpdateService.1.0.FlashFirmware", "Resolution": "None", "Severity": "OK"}], "Name": "Update Service Task", "PercentComplete": 42, "TaskState": "Running", "TaskStatus": "OK"}
20230914_200239     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20230914_200239     Unknown             OK          Device is flashing firmware for action /redfish/v1/UpdateService/upload.
20230914_200244 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200245 Update status : Running (Percent complete = 44)
20230914_200245 Checking status on redfish/v1/TaskService/Tasks/2
20230914_200245 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200245 Task     status : Running (Percent complete = 44)
20230914_200245 Found 2 messages from [redfish/v1/TaskService/Tasks/2]
20230914_200245 {"@odata.context": "/redfish/v1/$metadata#Task.Task", "@odata.etag": "\"1694739545\"", "@odata.id": "/redfish/v1/TaskService/Tasks/2", "@odata.type": "#Task.v1_4_2.Task", "Description": "Task for Update Service Task", "Id": "2", "Messages": [{"@odata.type": "#Message.v1_0_8.Message", "Message": "Task /redfish/v1/UpdateService/upload is running normally.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "Task.1.0.Running", "Resolution": "None", "Severity": "OK"}, {"@odata.type": "#Message.v1_0_8.Message", "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "UpdateService.1.0.FlashFirmware", "Resolution": "None", "Severity": "OK"}], "Name": "Update Service Task", "PercentComplete": 44, "TaskState": "Running", "TaskStatus": "OK"}
20230914_200245     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20230914_200245     Unknown             OK          Device is flashing firmware for action /redfish/v1/UpdateService/upload.
20230914_200250 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200251 Update status : Running (Percent complete = 45)
20230914_200251 Checking status on redfish/v1/TaskService/Tasks/2
20230914_200251 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200251 Task     status : Running (Percent complete = 45)
20230914_200251 Found 2 messages from [redfish/v1/TaskService/Tasks/2]
20230914_200251 {"@odata.context": "/redfish/v1/$metadata#Task.Task", "@odata.etag": "\"1694739545\"", "@odata.id": "/redfish/v1/TaskService/Tasks/2", "@odata.type": "#Task.v1_4_2.Task", "Description": "Task for Update Service Task", "Id": "2", "Messages": [{"@odata.type": "#Message.v1_0_8.Message", "Message": "Task /redfish/v1/UpdateService/upload is running normally.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "Task.1.0.Running", "Resolution": "None", "Severity": "OK"}, {"@odata.type": "#Message.v1_0_8.Message", "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "UpdateService.1.0.FlashFirmware", "Resolution": "None", "Severity": "OK"}], "Name": "Update Service Task", "PercentComplete": 45, "TaskState": "Running", "TaskStatus": "OK"}
20230914_200251     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20230914_200251     Unknown             OK          Device is flashing firmware for action /redfish/v1/UpdateService/upload.
20230914_200256 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200257 Update status : Running (Percent complete = 47)
20230914_200257 Checking status on redfish/v1/TaskService/Tasks/2
20230914_200257 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200257 Task     status : Running (Percent complete = 47)
20230914_200257 Found 2 messages from [redfish/v1/TaskService/Tasks/2]
20230914_200257 {"@odata.context": "/redfish/v1/$metadata#Task.Task", "@odata.etag": "\"1694739545\"", "@odata.id": "/redfish/v1/TaskService/Tasks/2", "@odata.type": "#Task.v1_4_2.Task", "Description": "Task for Update Service Task", "Id": "2", "Messages": [{"@odata.type": "#Message.v1_0_8.Message", "Message": "Task /redfish/v1/UpdateService/upload is running normally.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "Task.1.0.Running", "Resolution": "None", "Severity": "OK"}, {"@odata.type": "#Message.v1_0_8.Message", "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "UpdateService.1.0.FlashFirmware", "Resolution": "None", "Severity": "OK"}], "Name": "Update Service Task", "PercentComplete": 47, "TaskState": "Running", "TaskStatus": "OK"}
20230914_200257     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20230914_200257     Unknown             OK          Device is flashing firmware for action /redfish/v1/UpdateService/upload.
20230914_200302 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200302 Update status : Running (Percent complete = 49)
20230914_200302 Checking status on redfish/v1/TaskService/Tasks/2
20230914_200302 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200303 Task     status : Running (Percent complete = 49)
20230914_200303 Found 2 messages from [redfish/v1/TaskService/Tasks/2]
20230914_200303 {"@odata.context": "/redfish/v1/$metadata#Task.Task", "@odata.etag": "\"1694739545\"", "@odata.id": "/redfish/v1/TaskService/Tasks/2", "@odata.type": "#Task.v1_4_2.Task", "Description": "Task for Update Service Task", "Id": "2", "Messages": [{"@odata.type": "#Message.v1_0_8.Message", "Message": "Task /redfish/v1/UpdateService/upload is running normally.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "Task.1.0.Running", "Resolution": "None", "Severity": "OK"}, {"@odata.type": "#Message.v1_0_8.Message", "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "UpdateService.1.0.FlashFirmware", "Resolution": "None", "Severity": "OK"}], "Name": "Update Service Task", "PercentComplete": 49, "TaskState": "Running", "TaskStatus": "OK"}
20230914_200303     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20230914_200303     Unknown             OK          Device is flashing firmware for action /redfish/v1/UpdateService/upload.
20230914_200308 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200308 Update status : Running (Percent complete = 50)
20230914_200308 Checking status on redfish/v1/TaskService/Tasks/2
20230914_200308 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200309 Task     status : Running (Percent complete = 51)
20230914_200309 Found 2 messages from [redfish/v1/TaskService/Tasks/2]
20230914_200309 {"@odata.context": "/redfish/v1/$metadata#Task.Task", "@odata.etag": "\"1694739545\"", "@odata.id": "/redfish/v1/TaskService/Tasks/2", "@odata.type": "#Task.v1_4_2.Task", "Description": "Task for Update Service Task", "Id": "2", "Messages": [{"@odata.type": "#Message.v1_0_8.Message", "Message": "Task /redfish/v1/UpdateService/upload is running normally.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "Task.1.0.Running", "Resolution": "None", "Severity": "OK"}, {"@odata.type": "#Message.v1_0_8.Message", "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "UpdateService.1.0.FlashFirmware", "Resolution": "None", "Severity": "OK"}], "Name": "Update Service Task", "PercentComplete": 51, "TaskState": "Running", "TaskStatus": "OK"}
20230914_200309     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20230914_200309     Unknown             OK          Device is flashing firmware for action /redfish/v1/UpdateService/upload.
20230914_200314 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200314 Update status : Running (Percent complete = 52)
20230914_200314 Checking status on redfish/v1/TaskService/Tasks/2
20230914_200314 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200315 Task     status : Running (Percent complete = 52)
20230914_200315 Found 2 messages from [redfish/v1/TaskService/Tasks/2]
20230914_200315 {"@odata.context": "/redfish/v1/$metadata#Task.Task", "@odata.etag": "\"1694739545\"", "@odata.id": "/redfish/v1/TaskService/Tasks/2", "@odata.type": "#Task.v1_4_2.Task", "Description": "Task for Update Service Task", "Id": "2", "Messages": [{"@odata.type": "#Message.v1_0_8.Message", "Message": "Task /redfish/v1/UpdateService/upload is running normally.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "Task.1.0.Running", "Resolution": "None", "Severity": "OK"}, {"@odata.type": "#Message.v1_0_8.Message", "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "UpdateService.1.0.FlashFirmware", "Resolution": "None", "Severity": "OK"}], "Name": "Update Service Task", "PercentComplete": 52, "TaskState": "Running", "TaskStatus": "OK"}
20230914_200315     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20230914_200315     Unknown             OK          Device is flashing firmware for action /redfish/v1/UpdateService/upload.
20230914_200320 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200320 Update status : Running (Percent complete = 55)
20230914_200320 Checking status on redfish/v1/TaskService/Tasks/2
20230914_200320 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200321 Task     status : Running (Percent complete = 55)
20230914_200321 Found 2 messages from [redfish/v1/TaskService/Tasks/2]
20230914_200321 {"@odata.context": "/redfish/v1/$metadata#Task.Task", "@odata.etag": "\"1694739545\"", "@odata.id": "/redfish/v1/TaskService/Tasks/2", "@odata.type": "#Task.v1_4_2.Task", "Description": "Task for Update Service Task", "Id": "2", "Messages": [{"@odata.type": "#Message.v1_0_8.Message", "Message": "Task /redfish/v1/UpdateService/upload is running normally.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "Task.1.0.Running", "Resolution": "None", "Severity": "OK"}, {"@odata.type": "#Message.v1_0_8.Message", "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "UpdateService.1.0.FlashFirmware", "Resolution": "None", "Severity": "OK"}], "Name": "Update Service Task", "PercentComplete": 55, "TaskState": "Running", "TaskStatus": "OK"}
20230914_200321     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20230914_200321     Unknown             OK          Device is flashing firmware for action /redfish/v1/UpdateService/upload.
20230914_200326 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200326 Update status : Running (Percent complete = 69)
20230914_200326 Checking status on redfish/v1/TaskService/Tasks/2
20230914_200326 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200326 Task     status : Running (Percent complete = 69)
20230914_200326 Found 2 messages from [redfish/v1/TaskService/Tasks/2]
20230914_200326 {"@odata.context": "/redfish/v1/$metadata#Task.Task", "@odata.etag": "\"1694739545\"", "@odata.id": "/redfish/v1/TaskService/Tasks/2", "@odata.type": "#Task.v1_4_2.Task", "Description": "Task for Update Service Task", "Id": "2", "Messages": [{"@odata.type": "#Message.v1_0_8.Message", "Message": "Task /redfish/v1/UpdateService/upload is running normally.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "Task.1.0.Running", "Resolution": "None", "Severity": "OK"}, {"@odata.type": "#Message.v1_0_8.Message", "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "UpdateService.1.0.FlashFirmware", "Resolution": "None", "Severity": "OK"}], "Name": "Update Service Task", "PercentComplete": 69, "TaskState": "Running", "TaskStatus": "OK"}
20230914_200326     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20230914_200326     Unknown             OK          Device is flashing firmware for action /redfish/v1/UpdateService/upload.
20230914_200331 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200332 Update status : Running (Percent complete = 74)
20230914_200332 Checking status on redfish/v1/TaskService/Tasks/2
20230914_200332 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200332 Task     status : Running (Percent complete = 74)
20230914_200332 Found 2 messages from [redfish/v1/TaskService/Tasks/2]
20230914_200332 {"@odata.context": "/redfish/v1/$metadata#Task.Task", "@odata.etag": "\"1694739545\"", "@odata.id": "/redfish/v1/TaskService/Tasks/2", "@odata.type": "#Task.v1_4_2.Task", "Description": "Task for Update Service Task", "Id": "2", "Messages": [{"@odata.type": "#Message.v1_0_8.Message", "Message": "Task /redfish/v1/UpdateService/upload is running normally.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "Task.1.0.Running", "Resolution": "None", "Severity": "OK"}, {"@odata.type": "#Message.v1_0_8.Message", "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "UpdateService.1.0.FlashFirmware", "Resolution": "None", "Severity": "OK"}], "Name": "Update Service Task", "PercentComplete": 74, "TaskState": "Running", "TaskStatus": "OK"}
20230914_200332     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20230914_200332     Unknown             OK          Device is flashing firmware for action /redfish/v1/UpdateService/upload.
20230914_200337 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200338 Update status : Running (Percent complete = 86)
20230914_200338 Checking status on redfish/v1/TaskService/Tasks/2
20230914_200338 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200338 Task     status : Running (Percent complete = 86)
20230914_200338 Found 2 messages from [redfish/v1/TaskService/Tasks/2]
20230914_200338 {"@odata.context": "/redfish/v1/$metadata#Task.Task", "@odata.etag": "\"1694739545\"", "@odata.id": "/redfish/v1/TaskService/Tasks/2", "@odata.type": "#Task.v1_4_2.Task", "Description": "Task for Update Service Task", "Id": "2", "Messages": [{"@odata.type": "#Message.v1_0_8.Message", "Message": "Task /redfish/v1/UpdateService/upload is running normally.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "Task.1.0.Running", "Resolution": "None", "Severity": "OK"}, {"@odata.type": "#Message.v1_0_8.Message", "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "UpdateService.1.0.FlashFirmware", "Resolution": "None", "Severity": "OK"}], "Name": "Update Service Task", "PercentComplete": 86, "TaskState": "Running", "TaskStatus": "OK"}
20230914_200338     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20230914_200338     Unknown             OK          Device is flashing firmware for action /redfish/v1/UpdateService/upload.
20230914_200343 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200344 Update status : Running (Percent complete = 100)
20230914_200344 Checking status on redfish/v1/TaskService/Tasks/2
20230914_200344 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200344 Task     status : Running (Percent complete = 100)
20230914_200344 Found 2 messages from [redfish/v1/TaskService/Tasks/2]
20230914_200344 {"@odata.context": "/redfish/v1/$metadata#Task.Task", "@odata.etag": "\"1694739545\"", "@odata.id": "/redfish/v1/TaskService/Tasks/2", "@odata.type": "#Task.v1_4_2.Task", "Description": "Task for Update Service Task", "Id": "2", "Messages": [{"@odata.type": "#Message.v1_0_8.Message", "Message": "Task /redfish/v1/UpdateService/upload is running normally.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "Task.1.0.Running", "Resolution": "None", "Severity": "OK"}, {"@odata.type": "#Message.v1_0_8.Message", "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "UpdateService.1.0.FlashFirmware", "Resolution": "None", "Severity": "OK"}], "Name": "Update Service Task", "PercentComplete": 100, "TaskState": "Running", "TaskStatus": "OK"}
20230914_200344     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20230914_200344     Unknown             OK          Device is flashing firmware for action /redfish/v1/UpdateService/upload.
20230914_200349 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200349 Update status : Running (Percent complete = 100)
20230914_200349 Checking status on redfish/v1/TaskService/Tasks/2
20230914_200349 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200350 Task     status : Running (Percent complete = 100)
20230914_200350 Found 2 messages from [redfish/v1/TaskService/Tasks/2]
20230914_200350 {"@odata.context": "/redfish/v1/$metadata#Task.Task", "@odata.etag": "\"1694739545\"", "@odata.id": "/redfish/v1/TaskService/Tasks/2", "@odata.type": "#Task.v1_4_2.Task", "Description": "Task for Update Service Task", "Id": "2", "Messages": [{"@odata.type": "#Message.v1_0_8.Message", "Message": "Task /redfish/v1/UpdateService/upload is running normally.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "Task.1.0.Running", "Resolution": "None", "Severity": "OK"}, {"@odata.type": "#Message.v1_0_8.Message", "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "UpdateService.1.0.FlashFirmware", "Resolution": "None", "Severity": "OK"}], "Name": "Update Service Task", "PercentComplete": 100, "TaskState": "Running", "TaskStatus": "OK"}
20230914_200350     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20230914_200350     Unknown             OK          Device is flashing firmware for action /redfish/v1/UpdateService/upload.
20230914_200355 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200355 Update status : Running (Percent complete = 100)
20230914_200355 Checking status on redfish/v1/TaskService/Tasks/2
20230914_200355 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200356 Task     status : Running (Percent complete = 100)
20230914_200356 Found 2 messages from [redfish/v1/TaskService/Tasks/2]
20230914_200356 {"@odata.context": "/redfish/v1/$metadata#Task.Task", "@odata.etag": "\"1694739545\"", "@odata.id": "/redfish/v1/TaskService/Tasks/2", "@odata.type": "#Task.v1_4_2.Task", "Description": "Task for Update Service Task", "Id": "2", "Messages": [{"@odata.type": "#Message.v1_0_8.Message", "Message": "Task /redfish/v1/UpdateService/upload is running normally.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "Task.1.0.Running", "Resolution": "None", "Severity": "OK"}, {"@odata.type": "#Message.v1_0_8.Message", "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "UpdateService.1.0.FlashFirmware", "Resolution": "None", "Severity": "OK"}], "Name": "Update Service Task", "PercentComplete": 100, "TaskState": "Running", "TaskStatus": "OK"}
20230914_200356     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20230914_200356     Unknown             OK          Device is flashing firmware for action /redfish/v1/UpdateService/upload.
20230914_200401 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200401 Update status : Running (Percent complete = 100)
20230914_200401 Checking status on redfish/v1/TaskService/Tasks/2
20230914_200401 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200402 Task     status : Running (Percent complete = 100)
20230914_200402 Found 2 messages from [redfish/v1/TaskService/Tasks/2]
20230914_200402 {"@odata.context": "/redfish/v1/$metadata#Task.Task", "@odata.etag": "\"1694739545\"", "@odata.id": "/redfish/v1/TaskService/Tasks/2", "@odata.type": "#Task.v1_4_2.Task", "Description": "Task for Update Service Task", "Id": "2", "Messages": [{"@odata.type": "#Message.v1_0_8.Message", "Message": "Task /redfish/v1/UpdateService/upload is running normally.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "Task.1.0.Running", "Resolution": "None", "Severity": "OK"}, {"@odata.type": "#Message.v1_0_8.Message", "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "UpdateService.1.0.FlashFirmware", "Resolution": "None", "Severity": "OK"}], "Name": "Update Service Task", "PercentComplete": 100, "TaskState": "Running", "TaskStatus": "OK"}
20230914_200402     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20230914_200402     Unknown             OK          Device is flashing firmware for action /redfish/v1/UpdateService/upload.
20230914_200407 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200407 Update status : Running (Percent complete = 100)
20230914_200407 Checking status on redfish/v1/TaskService/Tasks/2
20230914_200407 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200408 Task     status : Completed (Percent complete = 100)
20230914_200408 Found 2 messages from [redfish/v1/TaskService/Tasks/2]
20230914_200408 {"@odata.context": "/redfish/v1/$metadata#Task.Task", "@odata.etag": "\"1694739545\"", "@odata.id": "/redfish/v1/TaskService/Tasks/2", "@odata.type": "#Task.v1_4_2.Task", "Description": "Task for Update Service Task", "EndTime": "2023-09-15T01:04:07+00:00", "Id": "2", "Messages": [{"@odata.type": "#Message.v1_0_8.Message", "Message": "Task /redfish/v1/UpdateService/upload has completed.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "Task.1.0.Completed", "Resolution": "None", "Severity": "OK"}, {"@odata.type": "#Message.v1_0_8.Message", "Message": "Action /redfish/v1/UpdateService/upload firmware update is completed.", "MessageArgs": ["/redfish/v1/UpdateService/upload"], "MessageId": "UpdateService.1.0.FirmwareUpdateCompleted", "Resolution": "None", "Severity": "OK"}], "Name": "Update Service Task", "PercentComplete": 100, "TaskState": "Completed", "TaskStatus": "OK"}
20230914_200408     Unknown             OK          Task /redfish/v1/UpdateService/upload has completed.
20230914_200408     Unknown             OK          Action /redfish/v1/UpdateService/upload firmware update is completed.
20230914_200413 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/2
20230914_200413 Update status : Completed (Percent complete = 100)
20230914_200413 Update completed successfully
20230914_200433 FW update completed -- waiting 180 seconds before checking for new version
20230914_200733 Polling for up to 600 seconds to detect version string
20230914_200733 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/UpdateService/FirmwareInventory/BMC
20230914_200735 fwversion = [Unknown]
20230914_200745 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/UpdateService/FirmwareInventory/BMC
20230914_200746 fwversion = [Unknown]
20230914_200756 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/UpdateService/FirmwareInventory/BMC
20230914_200757 fwversion = [Unknown]
20230914_200807 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/UpdateService/FirmwareInventory/BMC
20230914_200808 fwversion = [Unknown]
20230914_200818 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/UpdateService/FirmwareInventory/BMC
20230914_200819 fwversion = [Unknown]
20230914_200829 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/UpdateService/FirmwareInventory/BMC
20230914_200830 {
    "@odata.context": "/redfish/v1/$metadata#SoftwareInventory.SoftwareInventory",
    "@odata.etag": "\"1694738882\"",
    "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/BMC",
    "@odata.type": "#SoftwareInventory.v1_2_3.SoftwareInventory",
    "Id": "BMC",
    "Name": "BMC",
    "Updateable": true,
    "Version": "0.36.00"
}
20230914_200830 fwversion = [0.36.00]
20230914_200830 Final BMC FW version: [0.36.00]
Statistics: starts
datetime,ecode,nerrs,fw_imgfile,fwver_start,fwver_end,component_type,component_name,bmc_ip,oshost_ip,osping_pre_secs,osping_total_secs,osping_pass,osping_fail,wait_before_update_poll_start,wait_after_poll_complete,poll_time_for_update_start,poll_time_for_update_complete,poll_time_for_post,poll_count_for_post,poll_time_for_version,poll_count_for_version,do_reboot,do_clear_sel_log,total_time,initiate_fwupdate_time,wait_for_update_done_time,iterate_for_post_complete_time,wait_for_version_available_time,wait_for_host_status_time,
20230914_195804,0,0,v0.36.00.ima,0.43.00,0.36.00,BMC,BMC,[2607:f160:10:9249:ce:40a:0:e015],,10,120,0,0,60,180,60,1500,0,2,600,2,0,0,625,59,328,0,56,0
Statistics: ends
20230914_200830 Process completed successfully
2023-09-14-20:08:30  Final Check
2023-09-14-20:08:30  BMC Update failed. Expected 0.36.0; but got 0.36.00.  See logs for failure details
[XXXXXX@welktxefnce-h-pe1util-vm01 ZT-Proteus-BMC-update-Redfish-v0.36.00-x86_64_20230328]$

```



### system settlement, 20 minutes

### .36 --> .43 upgrade

```log
20230914_202615     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20230914_202615     Unknown             OK          Device is flashing firmware for action /redfish/v1/UpdateService/upload.
20230914_202615 task_status : Running ... checking again
20230914_202620 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/3
20230914_202620 HTTP: 200
20230914_202620 JSON: {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1694740913\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/3",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "3",
    "Messages": [
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Task /redfish/v1/UpdateService/upload is running normally.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "Task.1.0.Running",
            "Resolution": "None",
            "Severity": "OK"
        },
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "UpdateService.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 73,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20230914_202620 Update status (monitor, running) : Running (Percent complete = 73)
20230914_202620 Checking task status on /redfish/v1/TaskService/Tasks/3
20230914_202620 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/3
20230914_202621 HTTP: 200
20230914_202621 JSON: {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1694740913\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/3",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "3",
    "Messages": [
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Task /redfish/v1/UpdateService/upload is running normally.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "Task.1.0.Running",
            "Resolution": "None",
            "Severity": "OK"
        },
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "UpdateService.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 74,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20230914_202621 Task /redfish/v1/TaskService/Tasks/3  status : 200 Running (Percent complete = 74)
20230914_202621 Found 2 messages from [/redfish/v1/TaskService/Tasks/3]
20230914_202621 {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1694740913\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/3",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "3",
    "Messages": [
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Task /redfish/v1/UpdateService/upload is running normally.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "Task.1.0.Running",
            "Resolution": "None",
            "Severity": "OK"
        },
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "UpdateService.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 74,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20230914_202621     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20230914_202621     Unknown             OK          Device is flashing firmware for action /redfish/v1/UpdateService/upload.
20230914_202621 task_status : Running ... checking again
20230914_202626 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/3
20230914_202626 HTTP: 200
20230914_202626 JSON: {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1694740913\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/3",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "3",
    "Messages": [
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Task /redfish/v1/UpdateService/upload is running normally.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "Task.1.0.Running",
            "Resolution": "None",
            "Severity": "OK"
        },
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "UpdateService.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 76,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20230914_202626 Update status (monitor, running) : Running (Percent complete = 76)
20230914_202626 Checking task status on /redfish/v1/TaskService/Tasks/3
20230914_202626 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/3
20230914_202626 HTTP: 200
20230914_202626 JSON: {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1694740913\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/3",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "3",
    "Messages": [
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Task /redfish/v1/UpdateService/upload is running normally.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "Task.1.0.Running",
            "Resolution": "None",
            "Severity": "OK"
        },
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "UpdateService.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 76,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20230914_202626 Task /redfish/v1/TaskService/Tasks/3  status : 200 Running (Percent complete = 76)
20230914_202626 Found 2 messages from [/redfish/v1/TaskService/Tasks/3]
20230914_202626 {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1694740913\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/3",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "3",
    "Messages": [
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Task /redfish/v1/UpdateService/upload is running normally.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "Task.1.0.Running",
            "Resolution": "None",
            "Severity": "OK"
        },
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "UpdateService.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 76,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20230914_202626     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20230914_202626     Unknown             OK          Device is flashing firmware for action /redfish/v1/UpdateService/upload.
20230914_202626 task_status : Running ... checking again
20230914_202631 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/3
20230914_202632 HTTP: 200
20230914_202632 JSON: {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1694740913\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/3",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "3",
    "Messages": [
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Task /redfish/v1/UpdateService/upload is running normally.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "Task.1.0.Running",
            "Resolution": "None",
            "Severity": "OK"
        },
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "UpdateService.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 99,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20230914_202632 Update status (monitor, running) : Running (Percent complete = 99)
20230914_202632 Checking task status on /redfish/v1/TaskService/Tasks/3
20230914_202632 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/3
20230914_202632 HTTP: 200
20230914_202632 JSON: {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1694740913\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/3",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "3",
    "Messages": [
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Task /redfish/v1/UpdateService/upload is running normally.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "Task.1.0.Running",
            "Resolution": "None",
            "Severity": "OK"
        },
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "UpdateService.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 99,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20230914_202632 Task /redfish/v1/TaskService/Tasks/3  status : 200 Running (Percent complete = 99)
20230914_202632 Found 2 messages from [/redfish/v1/TaskService/Tasks/3]
20230914_202632 {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1694740913\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/3",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "3",
    "Messages": [
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Task /redfish/v1/UpdateService/upload is running normally.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "Task.1.0.Running",
            "Resolution": "None",
            "Severity": "OK"
        },
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "UpdateService.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 99,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20230914_202632     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20230914_202632     Unknown             OK          Device is flashing firmware for action /redfish/v1/UpdateService/upload.
20230914_202632 task_status : Running ... checking again
20230914_202637 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/3
20230914_202638 HTTP: 200
20230914_202638 JSON: {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1694740913\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/3",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "3",
    "Messages": [
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Task /redfish/v1/UpdateService/upload is running normally.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "Task.1.0.Running",
            "Resolution": "None",
            "Severity": "OK"
        },
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "UpdateService.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 100,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20230914_202638 Update status (monitor, running) : Running (Percent complete = 100)
20230914_202638 Checking task status on /redfish/v1/TaskService/Tasks/3
20230914_202638 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/3
20230914_202638 HTTP: 200
20230914_202638 JSON: {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1694740913\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/3",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "3",
    "Messages": [
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Task /redfish/v1/UpdateService/upload is running normally.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "Task.1.0.Running",
            "Resolution": "None",
            "Severity": "OK"
        },
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "UpdateService.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 100,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20230914_202638 Task /redfish/v1/TaskService/Tasks/3  status : 200 Running (Percent complete = 100)
20230914_202638 Found 2 messages from [/redfish/v1/TaskService/Tasks/3]
20230914_202638 {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1694740913\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/3",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "3",
    "Messages": [
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Task /redfish/v1/UpdateService/upload is running normally.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "Task.1.0.Running",
            "Resolution": "None",
            "Severity": "OK"
        },
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "UpdateService.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 100,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20230914_202638     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20230914_202638     Unknown             OK          Device is flashing firmware for action /redfish/v1/UpdateService/upload.
20230914_202638 task_status : Running ... checking again
20230914_202643 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/3
20230914_202643 HTTP: 200
20230914_202643 JSON: {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1694740913\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/3",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "3",
    "Messages": [
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Task /redfish/v1/UpdateService/upload is running normally.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "Task.1.0.Running",
            "Resolution": "None",
            "Severity": "OK"
        },
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "UpdateService.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 100,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20230914_202643 Update status (monitor, running) : Running (Percent complete = 100)
20230914_202643 Checking task status on /redfish/v1/TaskService/Tasks/3
20230914_202643 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/3
20230914_202644 HTTP: 200
20230914_202644 JSON: {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1694740913\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/3",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "3",
    "Messages": [
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Task /redfish/v1/UpdateService/upload is running normally.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "Task.1.0.Running",
            "Resolution": "None",
            "Severity": "OK"
        },
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "UpdateService.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 100,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20230914_202644 Task /redfish/v1/TaskService/Tasks/3  status : 200 Running (Percent complete = 100)
20230914_202644 Found 2 messages from [/redfish/v1/TaskService/Tasks/3]
20230914_202644 {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1694740913\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/3",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "3",
    "Messages": [
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Task /redfish/v1/UpdateService/upload is running normally.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "Task.1.0.Running",
            "Resolution": "None",
            "Severity": "OK"
        },
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "UpdateService.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 100,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20230914_202644     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20230914_202644     Unknown             OK          Device is flashing firmware for action /redfish/v1/UpdateService/upload.
20230914_202644 task_status : Running ... checking again
20230914_202649 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/3
20230914_202649 HTTP: 200
20230914_202649 JSON: {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1694740913\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/3",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "3",
    "Messages": [
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Task /redfish/v1/UpdateService/upload is running normally.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "Task.1.0.Running",
            "Resolution": "None",
            "Severity": "OK"
        },
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "UpdateService.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 100,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20230914_202649 Update status (monitor, running) : Running (Percent complete = 100)
20230914_202649 Checking task status on /redfish/v1/TaskService/Tasks/3
20230914_202649 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/3
20230914_202650 HTTP: 200
20230914_202650 JSON: {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1694740913\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/3",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "3",
    "Messages": [
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Task /redfish/v1/UpdateService/upload is running normally.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "Task.1.0.Running",
            "Resolution": "None",
            "Severity": "OK"
        },
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "UpdateService.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 100,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20230914_202650 Task /redfish/v1/TaskService/Tasks/3  status : 200 Running (Percent complete = 100)
20230914_202650 Found 2 messages from [/redfish/v1/TaskService/Tasks/3]
20230914_202650 {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1694740913\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/3",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "3",
    "Messages": [
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Task /redfish/v1/UpdateService/upload is running normally.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "Task.1.0.Running",
            "Resolution": "None",
            "Severity": "OK"
        },
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "UpdateService.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 100,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20230914_202650     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20230914_202650     Unknown             OK          Device is flashing firmware for action /redfish/v1/UpdateService/upload.
20230914_202650 task_status : Running ... checking again
20230914_202655 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/3
20230914_202655 HTTP: 200
20230914_202655 JSON: {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1694740913\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/3",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "3",
    "Messages": [
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Task /redfish/v1/UpdateService/upload is running normally.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "Task.1.0.Running",
            "Resolution": "None",
            "Severity": "OK"
        },
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "UpdateService.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 100,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20230914_202655 Update status (monitor, running) : Running (Percent complete = 100)
20230914_202655 Checking task status on /redfish/v1/TaskService/Tasks/3
20230914_202655 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/3
20230914_202656 HTTP: 200
20230914_202656 JSON: {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1694740913\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/3",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "3",
    "Messages": [
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Task /redfish/v1/UpdateService/upload is running normally.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "Task.1.0.Running",
            "Resolution": "None",
            "Severity": "OK"
        },
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "UpdateService.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 100,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20230914_202656 Task /redfish/v1/TaskService/Tasks/3  status : 200 Running (Percent complete = 100)
20230914_202656 Found 2 messages from [/redfish/v1/TaskService/Tasks/3]
20230914_202656 {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1694740913\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/3",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "3",
    "Messages": [
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Task /redfish/v1/UpdateService/upload is running normally.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "Task.1.0.Running",
            "Resolution": "None",
            "Severity": "OK"
        },
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Device is flashing firmware for action /redfish/v1/UpdateService/upload.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "UpdateService.1.0.FlashFirmware",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 100,
    "TaskState": "Running",
    "TaskStatus": "OK"
}
20230914_202656     Unknown             OK          Task /redfish/v1/UpdateService/upload is running normally.
20230914_202656     Unknown             OK          Device is flashing firmware for action /redfish/v1/UpdateService/upload.
20230914_202656 task_status : Running ... checking again
20230914_202701 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/3
20230914_202701 HTTP: 200
20230914_202701 JSON: {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1694740913\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/3",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "3",
    "Messages": [
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Task /redfish/v1/UpdateService/upload has completed.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "Task.1.0.Completed",
            "Resolution": "None",
            "Severity": "OK"
        },
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Action /redfish/v1/UpdateService/upload firmware update is completed.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "UpdateService.1.0.FirmwareUpdateCompleted",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 100,
    "TaskState": "Completed",
    "TaskStatus": "OK"
}
20230914_202701 Update status (monitor, running) : Completed (Percent complete = 100)
20230914_202701 Update completed successfully
20230914_202721 Checking task status on /redfish/v1/TaskService/Tasks/3
20230914_202721 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/TaskService/Tasks/3
20230914_202721 HTTP: 200
20230914_202721 JSON: {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1694740913\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/3",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "3",
    "Messages": [
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Task /redfish/v1/UpdateService/upload has completed.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "Task.1.0.Completed",
            "Resolution": "None",
            "Severity": "OK"
        },
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Action /redfish/v1/UpdateService/upload firmware update is completed.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "UpdateService.1.0.FirmwareUpdateCompleted",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 100,
    "TaskState": "Completed",
    "TaskStatus": "OK"
}
20230914_202721 Task /redfish/v1/TaskService/Tasks/3  status : 200 Completed (Percent complete = 100)
20230914_202721 Found 2 messages from [/redfish/v1/TaskService/Tasks/3]
20230914_202721 {
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.etag": "\"1694740913\"",
    "@odata.id": "/redfish/v1/TaskService/Tasks/3",
    "@odata.type": "#Task.v1_4_2.Task",
    "Description": "Task for Update Service Task",
    "Id": "3",
    "Messages": [
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Task /redfish/v1/UpdateService/upload has completed.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "Task.1.0.Completed",
            "Resolution": "None",
            "Severity": "OK"
        },
        {
            "@odata.type": "#Message.v1_0_8.Message",
            "Message": "Action /redfish/v1/UpdateService/upload firmware update is completed.",
            "MessageArgs": [
                "/redfish/v1/UpdateService/upload"
            ],
            "MessageId": "UpdateService.1.0.FirmwareUpdateCompleted",
            "Resolution": "None",
            "Severity": "OK"
        }
    ],
    "Name": "Update Service Task",
    "PercentComplete": 100,
    "TaskState": "Completed",
    "TaskStatus": "OK"
}
20230914_202721     Unknown             OK          Task /redfish/v1/UpdateService/upload has completed.
20230914_202721     Unknown             OK          Action /redfish/v1/UpdateService/upload firmware update is completed.
20230914_202721 FW update completed -- waiting 180 seconds before checking for new version
20230914_203021 Polling for up to 600 seconds to detect new FW versions
20230914_203021 Target: BMC                              Any
20230914_203021 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/UpdateService/FirmwareInventory/BMC
20230914_203023 HTTP: 503
20230914_203023 JSON: {
    "error": {
        "@Message.ExtendedInfo": [
            {
                "@odata.type": "#Message.v1_0_8.Message",
                "Message": "The operation failed because the service is in an unknown state and can no longer take incoming requests.",
                "MessageId": "Base.1.5.ServiceInUnknownState",
                "Resolution": "Restart the service or resubmit the request if the operation failed.",
                "Severity": "Critical"
            }
        ],
        "code": "Base.1.5.ServiceInUnknownState",
        "message": "The operation failed because the service is in an unknown state and can no longer take incoming requests."
    }
}
20230914_203023 fwversion = [Unknown] [Unknown]
20230914_203033 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/UpdateService/FirmwareInventory/BMC
20230914_203034 HTTP: 503
20230914_203034 JSON: {
    "error": {
        "@Message.ExtendedInfo": [
            {
                "@odata.type": "#Message.v1_0_8.Message",
                "Message": "The operation failed because the service is in an unknown state and can no longer take incoming requests.",
                "MessageId": "Base.1.5.ServiceInUnknownState",
                "Resolution": "Restart the service or resubmit the request if the operation failed.",
                "Severity": "Critical"
            }
        ],
        "code": "Base.1.5.ServiceInUnknownState",
        "message": "The operation failed because the service is in an unknown state and can no longer take incoming requests."
    }
}
20230914_203034 fwversion = [Unknown] [Unknown]
20230914_203044 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/UpdateService/FirmwareInventory/BMC
20230914_203045 HTTP: 503
20230914_203045 JSON: {
    "error": {
        "@Message.ExtendedInfo": [
            {
                "@odata.type": "#Message.v1_0_8.Message",
                "Message": "The operation failed because the service is in an unknown state and can no longer take incoming requests.",
                "MessageId": "Base.1.5.ServiceInUnknownState",
                "Resolution": "Restart the service or resubmit the request if the operation failed.",
                "Severity": "Critical"
            }
        ],
        "code": "Base.1.5.ServiceInUnknownState",
        "message": "The operation failed because the service is in an unknown state and can no longer take incoming requests."
    }
}
20230914_203045 fwversion = [Unknown] [Unknown]
20230914_203055 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/UpdateService/FirmwareInventory/BMC
20230914_203056 HTTP: 503
20230914_203056 JSON: {
    "error": {
        "@Message.ExtendedInfo": [
            {
                "@odata.type": "#Message.v1_0_8.Message",
                "Message": "The operation failed because the service is in an unknown state and can no longer take incoming requests.",
                "MessageId": "Base.1.5.ServiceInUnknownState",
                "Resolution": "Restart the service or resubmit the request if the operation failed.",
                "Severity": "Critical"
            }
        ],
        "code": "Base.1.5.ServiceInUnknownState",
        "message": "The operation failed because the service is in an unknown state and can no longer take incoming requests."
    }
}
20230914_203056 fwversion = [Unknown] [Unknown]
20230914_203106 GET: https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/UpdateService/FirmwareInventory/BMC
20230914_203107 HTTP: 200
20230914_203107 JSON: {
    "@odata.context": "/redfish/v1/$metadata#SoftwareInventory.SoftwareInventory",
    "@odata.etag": "\"1694741437\"",
    "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/BMC",
    "@odata.type": "#SoftwareInventory.v1_2_3.SoftwareInventory",
    "Id": "BMC",
    "Name": "BMC",
    "Updateable": true,
    "Version": "0.43.00"
}
20230914_203107 {
    "@odata.context": "/redfish/v1/$metadata#SoftwareInventory.SoftwareInventory",
    "@odata.etag": "\"1694741437\"",
    "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/BMC",
    "@odata.type": "#SoftwareInventory.v1_2_3.SoftwareInventory",
    "Id": "BMC",
    "Name": "BMC",
    "Updateable": true,
    "Version": "0.43.00"
}
20230914_203107 fwversion = [Version] [0.43.00]
20230914_203107 Obtained 1 of 1 FW versions
20230914_203107 Final BMC FW version: [0.43.00]
20230914_203107 Checking for final FW version match
Statistics: starts
datetime,ecode,nerrs,fw_imgfile,fwver_start,fwver_end,fwver_expected,component_type,component_name,component_count,component_updated,bmc_ip,oshost_ip,osping_pre_secs,osping_total_secs,osping_pass,osping_fail,wait_before_update_poll_start,wait_after_poll_complete,poll_time_for_update_start,poll_time_for_update_complete,poll_time_for_post,poll_count_for_post,poll_time_for_version,poll_count_for_version,do_reboot,do_clear_sel_log,total_time,initiate_fwupdate_time,wait_for_update_done_time,iterate_for_post_complete_time,wait_for_version_available_time,wait_for_host_status_time,
20230914_202100,0,0,v0.43.00.ima,0.36.00,0.43.00,,BMC,BMC,1,1,[2607:f160:10:9249:ce:40a:0:e015],,10,120,0,0,60,180,60,1500,0,2,600,2,0,0,607,50,328,0,45,0
Statistics: ends
20230914_203107 Process completed successfully
2023-09-14-20:31:07  Final Check
2023-09-14-20:31:10  BMC updated Successfully to 0.43.00
[XXXXXX@welktxefnce-h-pe1util-vm01 ZT-Proteus-BMC-update-Redfish-v0.43.00-x86_64_20230623]$


```



### 20 min time for system to settle

```log
2023-09-14-20:31:10  BMC updated Successfully to 0.43.00
[XXXXXX@vcpe-jumpserver ~]$ date
Thu Sep 14 20:52:39 CDT 2023
```
```log
[XXXXXX@welktxefnce-h-pe1util-vm01 ZT-Proteus-BMC-update-Redfish-v0.43.00-x86_64_20230623]$ curl -k -w "\\n%{http_code} %{url_effective}\\n" -u XXXXXX:XXXXXX -H "Content-Type: application/json" -d '{"Attributes": {"PMS012": "Disable"}}' -X PATCH https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Systems/Self/Bios/SD

204 https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Systems/Self/Bios/SD
[XXXXXX@welktxefnce-h-pe1util-vm01 ZT-Proteus-BMC-update-Redfish-v0.43.00-x86_64_20230623]$ curl -k -w "\\n%{http_code} %{url_effective}\\n" -u XXXXXX:XXXXXX -H "Content-Type: application/json" -d '{"Attributes": {"PMS012": "Enable"}}' -X PATCH https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Systems/Self/Bios/SD

204 https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Systems/Self/Bios/SD
[XXXXXX@welktxefnce-h-pe1util-vm01 ZT-Proteus-BMC-update-Redfish-v0.43.00-x86_64_20230623]$
```

### Upgraded to .43, now going to initiate another rebuild of the host

```log
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [Setup] ***********************************************************************************************************************************

TASK [common/setup : Create temporary working directory] ***************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [common/setup : Set temporary working directory path] *************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [Remote Configure] ************************************************************************************************************************

TASK [remote/remote-configure : Set facts for vip, ansible, and wr_admin] **********************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Set facts for wr_release_version] ******************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Print wr_release_version] **************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "msg": "wr_release_version: 21.12"
}

TASK [remote/remote-configure : Set fact wr_distribution_directory to use based on WR version] *************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Set fact wr_distribution_directory to use based on WR version] *************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Set facts for which image list to use based on WR version] *****************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Set facts for which image list to use based on WR version] *****************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Set facts for which image list to use based on WR version] *****************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Print wr_image_list] *******************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "msg": "wr_image_list: /opt/external/vcpfe-team/artifacts/WRCP-2112/wind-river-cloud-platform-container-images-list-21.12.txt"
}

TASK [remote/remote-configure : Set fact to wr_license_key] ************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Set fact to wr_license_key] ************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : print wr_license_key] ******************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "msg": "wr_license_key = IyBXaW5kIFJpdmVyIFByb2R1Y3QgQWN0aXZhdGlvbiBGaWxlIChpbnN0YWxsLnR4dCkKIyBJc3N1ZWQgZm9yIGhvc3Q6IDxWZXJpem9uPiA8VmVyaXpvbj4gPEFueT4KIyBMaWNlbnNlIG51bWJlcihzKTogNjgyMzc0CiMgSXNzdWVkIG9uOiAyNi1qYW4tMjAyMiAwOTo1MDo1MAojCiMgTm90ZTogdGhpcyBsaWNlbnNlIGlzIGdlbmVyYXRlZCBjdW11bGF0aXZlbHkgZm9yIGFsbAojIFdpbmQgUml2ZXIgc29mdHdhcmUgbWFuYWdlZCBieSB0aGlzIGhvc3QuCgojIDEuIEZsZXhMTSBsaWNlbnNlIGZpbGU6CiMgQmVnaW46IFNlcnZlciBsaWNlbnNlICAtLS0tLS0tLS0tLS0tLS0tLS0tLS0KIyBTZXJpYWwgTnVtYmVyOiA2ODQ0NDktVmVyaXpvblBPQy1HNFdEQzlDUEVLCgpQQUNLQUdFIFdSQ1BfQ09OVEFJTkVSX1BLRyB3cnNkIDIxIDAwNDY1REZDRUI5QiBcCglDT01QT05FTlRTPVdSQ1BfQ09OVEFJTkVSOjIxLjEyIE9QVElPTlM9U1VJVEUgXAoJU0lHTj0yNTAwQzhCMjRFRDAKSU5DUkVNRU5UIFdSQ1BfQ09OVEFJTkVSX1BLRyB3cnNkIDIxIHBlcm1hbmVudCB1bmNvdW50ZWQgNDQyRThBMzg2QUE4IFwKCVZFTkRPUl9TVFJJTkc9PGxuPjY4MjM3NDwvbG4+PHBzPjIyMTMtNDM8L3BzPiBIT1NUSUQ9QU5ZIFwKCUlTU1VFRD0yNi1qYW4tMjAyMiBTTj1zZXJpYWwtVmVyaXpvbi1MVjJJV0FVTEVCIFwKCVNUQVJUPTI2LWphbi0yMDIyIFNJR049QjUzNzk2OTBENEE2Cg=="
}

TASK [remote/remote-configure : Copy storage checking script if server is HPE-LS3-e910] ********************************************************
skipping: [welktxef-931887-rz-le2pts6-021] => (item=hpe_storage_check.py)

TASK [remote/remote-configure : Execute storage checking script if server is HPE-LS3-e910] *****************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor HPE HPE-LS3-e910 (4 disks)] *****************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor HPE HPE-LS3-e910 (2 disks)] *****************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor HPE HPE-LS3-92s3] ***************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor HPE HPE-LS6-92s6] ***************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor ZTS ZTS-LS3-trtn] ***************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Set facts for Corning] *****************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor ZTS ZTS-LS6-pts6 & ZTS-LS3-pts3] ************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor ZTS ZTS-LS6-aks6 & ZTS-LS3-aks3] ************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : set_fact] ******************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [include_role : remote/zt-redfish] ********************************************************************************************************

TASK [remote/zt-redfish : get content from /redfish/v1/Systems/Self] ***************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/zt-redfish : Extract and store BiosVersion from returned content] *****************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Set facts for BIOS version based on vendor ZTS ZTS-LS6-pts6 & ZTS-LS3-pts3] ************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : debug] *********************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "bios_version": "0.23"
}

TASK [remote/remote-configure : Find out which DM Docker version contral has] ******************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001]

TASK [remote/remote-configure : Find out which DM file version contral has] ********************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001]

TASK [remote/remote-configure : Print dm docker version and dm file version] *******************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "msg": "dm_docker_version: WRCP_21.12-wrs.4, dm_file: wind-river-cloud-platform-deployment-manager-2.0.8-4.tgz"
}

TASK [remote/remote-configure : Discover Wind River docker image names] ************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-configure : Print local_images_full] ***************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "msg": "docker.io/starlingx/ceph-config-helper:v1.15.0\ndocker.io/starlingx/dex:stx.4.0-v2.14.0-1\ndocker.io/starlingx/n3000-opae:stx.6.0-v1.0.1\ndocker.io/starlingx/stx-oidc-client:stx.5.0-v1.0.4\ndocker.io/wind-river/cloud-platform-deployment-manager:WRCP_21.12-wrs.4\ngcr.io/google_containers/kubernetes-dashboard-init-amd64:v1.0.0\ngcr.io/kubebuilder/kube-rbac-proxy:v0.4.0\nquay.io/external_storage/rbd-provisioner:v2.1.1-k8s1.11"
}

TASK [remote/remote-configure : Create fact for Wind River docker image names] *****************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Determine DM Helm Chart path] **********************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-configure : Print dm_helm_chart] *******************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "msg": "/opt/external/vcpfe-team/artifacts/WRCP-2112/wind-river-cloud-platform-deployment-manager-2.0.8-4.tgz"
}

TASK [remote/remote-configure : Set DM Helm Chart file] ****************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Lookup Deployment Manager image tag] ***************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-configure : Lookup RBAC Proxy image tag] ***********************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-configure : Copy WRCP DM Playbook] *****************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001] => (item=wind-river-cloud-platform-deployment-manager.yaml)
ok: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001] => (item=wind-river-cloud-platform-deployment-manager-2.0.8-4.tgz)

TASK [remote/remote-configure : Set a fact for the central controller VIP address] *************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Configure WRCP seed template] **********************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001] => (item={'src': 'bootstrap-values.yaml', 'dest': 'welktxef-d931887-021-bootstrap-values.yaml'})
ok: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001] => (item={'src': 'deploy-values.yaml', 'dest': 'welktxef-d931887-021-deploy-values.yaml'})
ok: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001] => (item={'src': 'deploy-standard.yaml', 'dest': 'welktxef-d931887-021-deploy-standard.yaml'})
ok: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001] => (item={'src': 'install-values.yaml', 'dest': 'welktxef-d931887-021-install-values.yaml'})

TASK [remote/remote-configure : Copy SSL cert files] *******************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001] => (item={'filename': 'k8s_root_ca_cert.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIF8jCCA9qgAwIBAgIJAIf9Ql2uDZh+MA0GCSqGSIb3DQEBDQUAMIGFMQswCQYD\nVQQGEwJVUzEOMAwGA1UECAwFVGV4YXMxETAPBgNVBAcMCFdlc3RsYWtlMR0wGwYD\nVQQKDBRWZXJpem9uIFNvdXJjaW5nIExMQzE0MDIGA1UEAwwrVmVyaXpvbiBOZXR3\nb3JrIFdFTEtUWElCIExBQiAxIDMgUlNBIEs4UyBDQTAeFw0yMDEwMjUyMjEyNDha\nFw0zMDEwMjMyMjEyNDhaMIGFMQswCQYDVQQGEwJVUzEOMAwGA1UECAwFVGV4YXMx\nETAPBgNVBAcMCFdlc3RsYWtlMR0wGwYDVQQKDBRWZXJpem9uIFNvdXJjaW5nIExM\nQzE0MDIGA1UEAwwrVmVyaXpvbiBOZXR3b3JrIFdFTEtUWElCIExBQiAxIDMgUlNB\nIEs4UyBDQTCCAiIwDQYJKoZIhvcNAQEBBQADggIPADCCAgoCggIBAKyF9svdv/qG\n7HxBr1DWvZ3CQiDsA4m1kj0hD7jo3B3W/32ODcPpgeNmp4Oful0SsndpqEGhXDq5\noiBfqszMUpzDgdQ7siIHekb2olFEK2KniMP3H53nilIppeyMby5K3ZwF0Qbmk5WK\ncoXoYegP+Uv9bV0AMH6Dn4CVgYrLAYfmPyGgUSt4vuZ9F/rf9UkBf/DcZGqMnMax\n/Gfaq8KwmDzD9D8IVCHPrM5f4+CaKMQCFu5QkSsLYJFRiuQWWaICMMdnqpb0HZh5\niPnCSHwPPUyXxtujdI97Ovy4X5WR46jJ2+KzPYe8tVa/DL3TlKmRL9AF+oSE17bw\nzGAE7GNWxPojebHIUuoKdOQC1qiJBVS+c14r9+9P2Uy6XEhNUs+h3juRI4U3YkQ1\nUCUU3opqhOPh4jUIuPGg5aX07lt4Wpxc48D+CY1D4i6vaJLl3WCsVK7PFwWVQQEW\nIQabfuj1R2jEu7pp2Yabza58S00v1P5/kv/DNr7ADm8eYRvxLAAXCedMeSDXKBgd\npPmVXXZoZ8+X8VRGYxcw0mBBLIAiTOntT2vgLeq5T3QyiVKdU6TLAYEjS65QZ3Eg\naIX0wRqlcQI7lruTXubtENG6wWXYtnDf5795ZID1YIEqkgzZLMBqq1SBiLnWd6aK\n78Zsr4j5GmTBGpKRmwE2oO1btJCCYyG5AgMBAAGjYzBhMA8GA1UdEwEB/wQFMAMB\nAf8wHQYDVR0OBBYEFEDQ5EaGp3x02WUuvqetygqpM3dCMB8GA1UdIwQYMBaAFEDQ\n5EaGp3x02WUuvqetygqpM3dCMA4GA1UdDwEB/wQEAwICpDANBgkqhkiG9w0BAQ0F\nAAOCAgEAeCMxVJr5Jyg87DVaUtEhiWfhto993ENrnevAGqrBOoRc/KU1/C3paqhR\nsvr2r2LR+npSmeo6iz0FaO31XwHSHX95+XJeGP5Q8TGddbRiTglQsMfOkGNzxqgg\nTkdZ8A1y9v2jprONUmLADVGIVT0AoHc7V9w1I8NKhrY+rIllum4FRDiDPSnImh5h\nxmH+Nq2ZuEFVdtV/oNKzEu2ywmbgBRd5Jv3rTejxltmTZtyq8IKoKguj3NVFn93Q\nU4TbsxkcAdrLMooLYYDRTWA4t0iqKM/UkYUg4xl2l9NrY7ZUbaNd5+YsLNdqXO/c\nmp7wyMv/8ZIy1BLG4zJmX/JzWkYmULqQ+A+21+YuqrV3a81V7vcHhJcRaPOrg5cd\nYwY2eCbXMvNOdrzppIglUrlddNuqAhs1MTi/VibxYuI9isU0JckXIcCy1L+xbEda\n6v/z6wSrScVz0I4m0DpK6xMQ8t9sLcrGp5uGbj6J4nQWd+QLdq6kmAzDOZ/Gs0wb\nPYdkER4dXAVcioYFekpKv7d+nur0FPtMNIw0OdhX2eAwC22IFAq2DZRjUFvaBGaD\ni1ptfq6P1mVJ2T/exYujEDtq+8yQTfWgFm/DjEfWtcCp0Jukgv8opLR2DpCf5Ucq\nd5X7d/DP0mukJ3vZ8EIqYorwZJ1L1a2jgngjA+gPxIaW+JHfTHU=\n-----END CERTIFICATE-----\n'})
ok: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001] => (item={'filename': 'k8s_root_ca_key.pem', 'value': '-----BEGIN PRIVATE KEY-----\nMIIJQQIBADANBgkqhkiG9w0BAQEFAASCCSswggknAgEAAoICAQCshfbL3b/6hux8\nQa9Q1r2dwkIg7AOJtZI9IQ+46Nwd1v99jg3D6YHjZqeDn7pdErJ3aahBoVw6uaIg\nX6rMzFKcw4HUO7IiB3pG9qJRRCtip4jD9x+d54pSKaXsjG8uSt2cBdEG5pOVinKF\n6GHoD/lL/W1dADB+g5+AlYGKywGH5j8hoFEreL7mfRf63/VJAX/w3GRqjJzGsfxn\n2qvCsJg8w/Q/CFQhz6zOX+PgmijEAhbuUJErC2CRUYrkFlmiAjDHZ6qW9B2YeYj5\nwkh8Dz1Ml8bbo3SPezr8uF+VkeOoydvisz2HvLVWvwy905SpkS/QBfqEhNe28Mxg\nBOxjVsT6I3mxyFLqCnTkAtaoiQVUvnNeK/fvT9lMulxITVLPod47kSOFN2JENVAl\nFN6KaoTj4eI1CLjxoOWl9O5beFqcXOPA/gmNQ+Iur2iS5d1grFSuzxcFlUEBFiEG\nm37o9UdoxLu6admGm82ufEtNL9T+f5L/wza+wA5vHmEb8SwAFwnnTHkg1ygYHaT5\nlV12aGfPl/FURmMXMNJgQSyAIkzp7U9r4C3quU90MolSnVOkywGBI0uuUGdxIGiF\n9MEapXECO5a7k17m7RDRusFl2LZw3+e/eWSA9WCBKpIM2SzAaqtUgYi51nemiu/G\nbK+I+RpkwRqSkZsBNqDtW7SQgmMhuQIDAQABAoICACysO62qa+2pRk8eixD5qfvR\ns2Hm+zuLYqSljPaqhWTMqTePswzJyDJkAHhawd0b3E6Dc2gbKlCihNKxMv744WNq\nVJHqK0QYf5ckgf9dEYboLsffk7ZFoFGKK0bHTnrENAIUl32b8xdD1EfMVp3KlRkS\nNGFijSwVVRXsoLCZxHm2Kx6/7oS9LWFtfuodV9xhoQlzaCUW5/mjWOJjgxpUs/b4\nHqS7uV1P80U1G0KraGboy5tGDXEB7y1x2e8Zwnfq7UqVE10nNQqoXcmefzpwj8Tn\ngDybZLFKjYmnDEkkj7jDHEbldsdRG/usWNZGlTYbPDA3fBkYdOsQCzvJypQmgbZ+\n3yk3Lj2+9vLEMfPrruuzyOSXgki6o5uvy7Je6PdBpsz75k8FH6a+Rw3vvP8HuP3S\nLSUYm3tyOheXHR7BKN4bnfi11RAWvDpT9S+QnZ+R8DmQzOADlnjRC8WewDJYoNJ1\np1jeuqswlxo144oMO92cmdS2dAbPvS6aQP1I85Q2NniY+6YhHkBwIQIlfVs1JPbY\nX7QtTy1IXQhR3sospyvUwY2GPSAeVHDRL53ClQKDsvWpSy0MAmWYJkZu1P+jKBim\nj34ytApgG65Hv/RHf3L4+4zzItZ3TN2tJ/g9EKc6oMNtqKbbG56kkmvRPWKtMGV8\nFqxCvG5NydUK7fN+P2WJAoIBAQDXLFC//Fn9ed1U+pKa2M25aJwEetkGLXQvkwVi\n8uJFaXITb2ceveSEo6iBExyn4eYL5A4X+RZdJJdRRbj4whsNN13Pm+6lYX3pp7MN\nO+78uvwVfKZiWPFKfZs7ZH1/O9VIlLGnXUHeaHK1tmv9ixxMixdnjUDkcVa0O3qT\nKBLpvXnVEMYizxQBN0P5Z9QvQQGpUhKnNw+FhV1SP+YHxrB0Pu6qbYAmZZC2MQc1\nTsDyqGjmHk9VJaFYAAPEjqACDbfnkVUCj0ylM4xPQuBJs9DOKh4InG+znusdmd8H\nmvoEFDppsrH1NhO6GTeuCk6n0WBi6cUm76K/gPscYyV4ZtkfAoIBAQDNQgDXtfqv\nxbAhvDk0o/P8fqOdgQF0uFTqYHmyW31Ty9nF0ptA8LVJOIljU3zlLplhIFjBnSEG\nLqu4jnLLRR+zej0MXmJuZ9BMWmQeTrZzttnH5bn54E07DPJ5BvFoTMJNklBiXjB5\n5hTPZS4yK1KjoxY+Ypnj4W1iZjP37ya/A34J2nlYtoW4LdVfJHqCxBXel9Nz2zkv\nvwwPu8Eu7gFLuhNQM6Iv4mORGI8yg7Y/BwodfDPRuFvrG1KXkjwASb0O5b1suRQy\n9H80q5EAbT36K1z48ilr8fcroN+hV8g4yntrBBgOHPMmBk/vHKU8B1rkBr0p2haI\n3PwKmDFRsDInAoIBAGrjjMmSZnHQk+6e+y0I/klYegiPrjevZMQtWMOqvFSW6SBW\nevd+hYKOeiqEf/u18D1/8LBgAIgMoU6yQAzy/9U059k2MPrez1m/AOdWGoZZrNhP\nr6ezX0oN04tRhDYsVutTUl09qnb9k95I3KR68nfjsKC0PsQ8uUGXOnDXu215vofl\naUfpbpqcBZxjw7glptmh97oxU/iUI6O0MmUygn18tbrb4okwcw7OlDIbCSaCGnoW\nHHrD0r6QY07FOx9KCU1zmLNI1F5MmSrWoex68wM3UOweKi8khs+RnIV+qyxTkCDp\nsBWL44jS9iHy5Nfg3uzEDDgnWsWfIR8c8YQ6MykCggEADr0ollTI9Yo6hZGggfkr\n8fueABddZWY/Ir1ev8H2E+hVcPEYmOcv/VwD8Y/zLfnUpbbO6MhBsNH1HsGL2LDT\n/+1NKPA2HTtzJ6ht/Acm7tQ4ezQx0JGcuhrJ5orrFtQ8N5nED+w3iulMoT/gu1WF\nD58MX9pwtn5ffmtcW/deTuUPTeHUSNyCaaFQ6w4RhgZSk7NPSch6KMWNNiwDST1p\n9mgcLuwmP04AXFDpJ3VxxsDYpxleFzcn0pAZtCyaBmNFIia5HW+E1cvcvol7Vg6C\nHs6yVGX/N3MejpF0vX8yL3HKvvqCR7EofJiDcOYbr13P1wPs3W59o8JKjvAyymze\njQKCAQAUY/0asRL33D7tFoIbLg/N9hi+tCCM35DMf2FeXm3QwSkAR/BJw0ewCE5C\n+VqukHN3/i0Xe8KSHwEuLK2sGLk9Ys8A5NytjqFApYwpIk8UrRONfC12H3ez5VYk\nJlhMVhVXEZvVhEFJiBC7q6x6s7BVtLTGV7FA5CW8YKBhwHwrpm+h/Xb798oaKyel\nP/xYq+GZzfWfbvUjZvgN0J0RGxKA+GRgsmhoyOfgCVXgSzuUkI+9cAUvC0OV407L\n4XIK0GDJ7Tv/2USSPfmueyGEmacc/oYUPVBUgeINSoaCM4cpZwyLylVEtKOdQoEE\n77G5mvQsoXxsMjd+nbHil450UHsL\n-----END PRIVATE KEY-----\n'})

TASK [Proteus MWIAT - ENABLE] ******************************************************************************************************************

TASK [remote/zt-redfish : Update Attributes at /redfish/v1/Systems/Self/Bios/SD] ***************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/zt-redfish : Update result] *******************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "update_result": {
        "allow": "GET, PUT, PATCH, POST",
        "changed": false,
        "connection": "close",
        "content": "",
        "cookies": {},
        "cookies_string": "",
        "date": "Fri, 15 Sep 2023 01:55:07 GMT",
        "elapsed": 0,
        "failed": false,
        "msg": "OK (unknown bytes)",
        "redirected": false,
        "server": "AMI MegaRAC Redfish Service",
        "status": 204,
        "url": "https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Systems/Self/Bios/SD"
    }
}

TASK [Remote Install] **************************************************************************************************************************

TASK [remote/remote-install : Check if the subcloud deployed but failed] ***********************************************************************
fatal: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001]: FAILED! => {"changed": true, "cmd": ". /etc/platform/openrc\ndcmanager subcloud show welktxef-d931887-021 --column \"deploy_status\" --format value\n", "delta": "0:00:01.174848", "end": "2023-09-15 01:55:10.686247", "msg": "non-zero return code", "rc": 1, "start": "2023-09-15 01:55:09.511399", "stderr": "ERROR (app) Subcloud not found", "stderr_lines": ["ERROR (app) Subcloud not found"], "stdout": "", "stdout_lines": []}
...ignoring

TASK [remote/remote-install : debug] ***********************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "msg": "subcloud_status:"
}

TASK [remote/remote-install : Delete the subcloud that's 'install-failed' & 'pre-install-failed'] **********************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-install : Deploy remote cloud] *********************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001]

TASK [remote/remote-install : 1st polling prep: Obtain Keystone auth token] ********************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-install : 1st polling: Wait for subcloud to start installing OS] ***********************************************************
FAILED - RETRYING: 1st polling: Wait for subcloud to start installing OS (40 retries left).
FAILED - RETRYING: 1st polling: Wait for subcloud to start installing OS (39 retries left).
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-install : 1st polling result: Fail if the installation failed] *************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-install : 2nd polling prep: Obtain Keystone auth token] ********************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-install : 2nd polling: Wait for subcloud to install OS (this will take a while)] *******************************************
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (100 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (99 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (98 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (97 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (96 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (95 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (94 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (93 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (92 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (91 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (90 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (89 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (88 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (87 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (86 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (85 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (84 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (83 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (82 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (81 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (80 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (79 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (78 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (77 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (76 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (75 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (74 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (73 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (72 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (71 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (70 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (69 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (68 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (67 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (66 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (65 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (64 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (63 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (62 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (61 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (60 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (59 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (58 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (57 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (56 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (55 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (54 retries left).
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-install : 2nd polling result: Fail if any error occurred] ******************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-install : 3rd polling prep: Obtain Keystone auth token] ********************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-install : 3rd polling: Wait for subcloud to install OS (this may take a while)] ********************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-install : 3rd polling result: Fail if any error occurred] ******************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-install : 4th polling prep: Obtain Keystone auth token] ********************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-install : 4th polling: Wait for subcloud to install OS (this may still take a while)] **************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-install : 4th polling result: Fail if the installation failed] *************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-install : 5th polling prep: Obtain Keystone auth token] ********************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-install : 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while)] *************************
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (100 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (99 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (98 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (97 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (96 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (95 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (94 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (93 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (92 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (91 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (90 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (89 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (88 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (87 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (86 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (85 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (84 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (83 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (82 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (81 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (80 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (79 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (78 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (77 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (76 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (75 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (74 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (73 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (72 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (71 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (70 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (69 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (68 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (67 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (66 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (65 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (64 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (63 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (62 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (61 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (60 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (59 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (58 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (57 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (56 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (55 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (54 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (53 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (52 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (51 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (50 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (49 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (48 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (47 retries left).
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-install : 5th polling result: Fail if bootstrap/deploy failed] *************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-install : 6th polling prep: Obtain Keystone auth token] ********************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-install : 6th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while)] *************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-install : 6th polling result: Fail if bootstrap/deploy failed] *************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-install : Wait for controller-0 restart] ***********************************************************************************
FAILED - RETRYING: Wait for controller-0 restart (40 retries left).
FAILED - RETRYING: Wait for controller-0 restart (39 retries left).
FAILED - RETRYING: Wait for controller-0 restart (38 retries left).
fatal: [welktxef-931887-rz-le2pts6-021]: FAILED! => {"attempts": 4, "changed": false, "elapsed": 5, "msg": "timed out waiting for ping module test success: Failed to connect to the host via ssh: ssh: connect to host 2607:f160:10:9249:ce:40a:0:f409 port 22: Connection refused"}
...ignoring

TASK [remote/remote-install : Wait for controller-0 recovery] **********************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-install : setup kdump] *****************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [Remote Cleanup] **************************************************************************************************************************

TASK [common/cleanup : Remove temporary working directory] *************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [Remote Manage] ***************************************************************************************************************************

TASK [remote/manage : 1st Obtain Keystone auth token] ******************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/manage : 1st Wait for contoller-0 availability status online] *********************************************************************
FAILED - RETRYING: 1st Wait for contoller-0 availability status online (100 retries left).
FAILED - RETRYING: 1st Wait for contoller-0 availability status online (99 retries left).
FAILED - RETRYING: 1st Wait for contoller-0 availability status online (98 retries left).
FAILED - RETRYING: 1st Wait for contoller-0 availability status online (97 retries left).
FAILED - RETRYING: 1st Wait for contoller-0 availability status online (96 retries left).
FAILED - RETRYING: 1st Wait for contoller-0 availability status online (95 retries left).
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/manage : 2nd Obtain Keystone auth token] ******************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/manage : 2nd Wait for contoller-0 availability status online] *********************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/manage : Wait for system to stabilize before running kubectl] *********************************************************************
Pausing for 480 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [welktxef-931887-rz-le2pts6-021]

TASK [Wait for distributed cloud to be reconciled] *********************************************************************************************

TASK [common/wait_for_reconciliation : Making sure node is reachable] **************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [common/wait_for_reconciliation : Wait for K8s API to be up] ******************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [common/wait_for_reconciliation : Wait for hosts to be reconciled] ************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [common/wait_for_reconciliation : Wait for systems to be reconciled] **********************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/manage : Wait for distributed cloud to be reconciled but subcloud OAM VIP becomes unreachable] ************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/manage : Check if the subcloud deployed but failed] *******************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001]

TASK [remote/manage : Set distributed cloud state to managed] **********************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001]

TASK [remote/manage : Wait for system to stabilize] ********************************************************************************************
Pausing for 300 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [welktxef-931887-rz-le2pts6-021]

TASK [Remote Trust] ****************************************************************************************************************************

TASK [remote/trust : Create temporary working directory] ***************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/trust : Copy SSL cert files to working dir] ***************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost] => (item={'filename': 'k8s_root_ca_cert.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIF8jCCA9qgAwIBAgIJAIf9Ql2uDZh+MA0GCSqGSIb3DQEBDQUAMIGFMQswCQYD\nVQQGEwJVUzEOMAwGA1UECAwFVGV4YXMxETAPBgNVBAcMCFdlc3RsYWtlMR0wGwYD\nVQQKDBRWZXJpem9uIFNvdXJjaW5nIExMQzE0MDIGA1UEAwwrVmVyaXpvbiBOZXR3\nb3JrIFdFTEtUWElCIExBQiAxIDMgUlNBIEs4UyBDQTAeFw0yMDEwMjUyMjEyNDha\nFw0zMDEwMjMyMjEyNDhaMIGFMQswCQYDVQQGEwJVUzEOMAwGA1UECAwFVGV4YXMx\nETAPBgNVBAcMCFdlc3RsYWtlMR0wGwYDVQQKDBRWZXJpem9uIFNvdXJjaW5nIExM\nQzE0MDIGA1UEAwwrVmVyaXpvbiBOZXR3b3JrIFdFTEtUWElCIExBQiAxIDMgUlNB\nIEs4UyBDQTCCAiIwDQYJKoZIhvcNAQEBBQADggIPADCCAgoCggIBAKyF9svdv/qG\n7HxBr1DWvZ3CQiDsA4m1kj0hD7jo3B3W/32ODcPpgeNmp4Oful0SsndpqEGhXDq5\noiBfqszMUpzDgdQ7siIHekb2olFEK2KniMP3H53nilIppeyMby5K3ZwF0Qbmk5WK\ncoXoYegP+Uv9bV0AMH6Dn4CVgYrLAYfmPyGgUSt4vuZ9F/rf9UkBf/DcZGqMnMax\n/Gfaq8KwmDzD9D8IVCHPrM5f4+CaKMQCFu5QkSsLYJFRiuQWWaICMMdnqpb0HZh5\niPnCSHwPPUyXxtujdI97Ovy4X5WR46jJ2+KzPYe8tVa/DL3TlKmRL9AF+oSE17bw\nzGAE7GNWxPojebHIUuoKdOQC1qiJBVS+c14r9+9P2Uy6XEhNUs+h3juRI4U3YkQ1\nUCUU3opqhOPh4jUIuPGg5aX07lt4Wpxc48D+CY1D4i6vaJLl3WCsVK7PFwWVQQEW\nIQabfuj1R2jEu7pp2Yabza58S00v1P5/kv/DNr7ADm8eYRvxLAAXCedMeSDXKBgd\npPmVXXZoZ8+X8VRGYxcw0mBBLIAiTOntT2vgLeq5T3QyiVKdU6TLAYEjS65QZ3Eg\naIX0wRqlcQI7lruTXubtENG6wWXYtnDf5795ZID1YIEqkgzZLMBqq1SBiLnWd6aK\n78Zsr4j5GmTBGpKRmwE2oO1btJCCYyG5AgMBAAGjYzBhMA8GA1UdEwEB/wQFMAMB\nAf8wHQYDVR0OBBYEFEDQ5EaGp3x02WUuvqetygqpM3dCMB8GA1UdIwQYMBaAFEDQ\n5EaGp3x02WUuvqetygqpM3dCMA4GA1UdDwEB/wQEAwICpDANBgkqhkiG9w0BAQ0F\nAAOCAgEAeCMxVJr5Jyg87DVaUtEhiWfhto993ENrnevAGqrBOoRc/KU1/C3paqhR\nsvr2r2LR+npSmeo6iz0FaO31XwHSHX95+XJeGP5Q8TGddbRiTglQsMfOkGNzxqgg\nTkdZ8A1y9v2jprONUmLADVGIVT0AoHc7V9w1I8NKhrY+rIllum4FRDiDPSnImh5h\nxmH+Nq2ZuEFVdtV/oNKzEu2ywmbgBRd5Jv3rTejxltmTZtyq8IKoKguj3NVFn93Q\nU4TbsxkcAdrLMooLYYDRTWA4t0iqKM/UkYUg4xl2l9NrY7ZUbaNd5+YsLNdqXO/c\nmp7wyMv/8ZIy1BLG4zJmX/JzWkYmULqQ+A+21+YuqrV3a81V7vcHhJcRaPOrg5cd\nYwY2eCbXMvNOdrzppIglUrlddNuqAhs1MTi/VibxYuI9isU0JckXIcCy1L+xbEda\n6v/z6wSrScVz0I4m0DpK6xMQ8t9sLcrGp5uGbj6J4nQWd+QLdq6kmAzDOZ/Gs0wb\nPYdkER4dXAVcioYFekpKv7d+nur0FPtMNIw0OdhX2eAwC22IFAq2DZRjUFvaBGaD\ni1ptfq6P1mVJ2T/exYujEDtq+8yQTfWgFm/DjEfWtcCp0Jukgv8opLR2DpCf5Ucq\nd5X7d/DP0mukJ3vZ8EIqYorwZJ1L1a2jgngjA+gPxIaW+JHfTHU=\n-----END CERTIFICATE-----\n'})
changed: [welktxef-931887-rz-le2pts6-021 -> localhost] => (item={'filename': 'vz_root_ca_cert.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIFpTCCA42gAwIBAgIUa3vZ0YGxO1TQ8NwhiVfQC0JslXgwDQYJKoZIhvcNAQEL\nBQAwWjELMAkGA1UEBhMCVVMxEDAOBgNVBAoMB1Zlcml6b24xEzARBgNVBAsMClZa\nSUFNIFRlc3QxJDAiBgNVBAMMG1Zlcml6b24gTmV0d29yayBSU0EgQ0EgVGVzdDAe\nFw0yMDA2MTUyMTAxMTNaFw0zNTA2MTUyMTAxMTNaMFoxCzAJBgNVBAYTAlVTMRAw\nDgYDVQQKDAdWZXJpem9uMRMwEQYDVQQLDApWWklBTSBUZXN0MSQwIgYDVQQDDBtW\nZXJpem9uIE5ldHdvcmsgUlNBIENBIFRlc3QwggIiMA0GCSqGSIb3DQEBAQUAA4IC\nDwAwggIKAoICAQC8AIrksI57CbIl5uGZ6yqfpQj3aK+N8f1EVHdwK9JFskoipvC8\n7yFTk8tgmO1i0YA5oRGfNxneqCdrXZiWL6Ko8v/iln9vuN+2rK3rgWZPPRJBAsBN\na49L7U6lJjIGxIZtZqmK5h47oiUtwlYVrbZMN2ijuBQ22/eQ9tsFDV28oBuZ3WAR\npSSbj/tubPQYkw3YYOhv/VpEpsd0rkoEt3QCmTVcX2rtblanpXowTV5R0Hy4014n\nT49jrEo40r4mwYoyS835Uv4ENUFA+pXicT9eUot3RSH6rYdx4A/14UtoI9U0ol8M\n62GHpxSASQ2Kc3yQWvxRGTFslTduYM+vVmMLEDDdqcsjYnStPpwdxxmKItmbjxSv\nIwYIndp8A04WkX2iiJCciC3BNxiLamPtYVyB1HHqbGTGirKYuSvwZt337q1OI3WH\nwVn2S4Mj/wqa4iCyGTvFSUnGq34Xkrb9XNwWBok9Tc2XWGAU/mb/xcd1hX74GZbF\nsrZ11aPtym4kMAjU2KQi96GcAH2lnGZYoOja1J4Cs4WYx1uAx74H/m84CrYavVfl\n1ONJVLDfuZaEkSmu+jHQX15pAECNORTuLD06PbWnOEcOi1xmbt/OT3SA3rhD2mb7\n2wxl7oJpV3ap8xGwYmxiFzmInxFJ1axjg8Rimol0mXTKAy6OdNHbCOnAwwIDAQAB\no2MwYTAPBgNVHRMBAf8EBTADAQH/MA4GA1UdDwEB/wQEAwIBBjAfBgNVHSMEGDAW\ngBQleng3lqGBeTrbLVuABoEmUHm1+TAdBgNVHQ4EFgQUJXp4N5ahgXk62y1bgAaB\nJlB5tfkwDQYJKoZIhvcNAQELBQADggIBADQ9jpmVh9nyY7ZQ4s+S9RuSRYn7QsrW\nDePeMzQgh8ZtS8WE65GY5HS61iHNP2Co8Q1lAaBWF4ipq+VZOcQbPLccHzd1kZv4\ns4u0aTzBd9ccidl73FS0DJDQOBbzPSzgsaiGHSMyGzkTeA8z3ntsSqrXXcDUvoRi\nFus/110AwdtNhJLrWveX6btYtHp9Lqe0YtNCy5AaXlrr1yRSckP5BWVtlwD4dzSO\n/dqI3wHS/ncUx9wSQomZ+AmxYW3KtJQKgHzTqHru1x9BBk7Bzfz9FZr6HLLmEitj\nuFoDRd5TNt5LbO0zDQokvY3oqso6Htup/rS7C08mcmnelYE+yXuOc1YrlyGnpBzk\nmy+1VYbOxRRdqKAZRbE72u/h847IVpsOvjR51iksuCAurZdp2+y2zvV8NhWekuNy\nirECRy9cb4YasjRaKi0/TCGPVSICuLyeG2W72liCj/N2VKfjPP9zsOR5XjwCXfRg\n+9xhLy77/gov2NWXx5fzTkhxCrHOxFdLVMn0wQhksDmw6QsXzDIHSpIOypdDfnx9\nCsthx3nhkuHLUaEP22D22dG+vImA9ukj4R/RRI/87jmi9Q8+ehH+NqN0GZZcLjdN\nSLVXpncuwWQFUDPR06wNkkkmBSXWiIYhwqSpU0Pl3er3fD0uWvXuWPm2PzfOmUAE\nUrkzyw9XmLw0\n-----END CERTIFICATE-----\n'})
changed: [welktxef-931887-rz-le2pts6-021 -> localhost] => (item={'filename': 'vz_root_ica_cert.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIFNzCCAx+gAwIBAgIUGLJR/hP48n+vdq2v1hcfspXo/78wDQYJKoZIhvcNAQEL\nBQAwWjELMAkGA1UEBhMCVVMxEDAOBgNVBAoMB1Zlcml6b24xEzARBgNVBAsMClZa\nSUFNIFRlc3QxJDAiBgNVBAMMG1Zlcml6b24gTmV0d29yayBSU0EgQ0EgVGVzdDAe\nFw0yMDEwMjIyMTE0MDNaFw0zMDEwMjIyMTE0MDNaMIGRMQswCQYDVQQGEwJVUzEL\nMAkGA1UECAwCVFgxETAPBgNVBAcMCFdlc3RsYWtlMRAwDgYDVQQKDAdWZXJpem9u\nMR0wGwYDVQQLDBRWZXJpem9uIFNvdXJjaW5nIExMQzExMC8GA1UEAwwoVmVyaXpv\nbiBOZXR3b3JrIFdFTEtUWElCIExBQiAxIDMgUlNBIElDQTCCASIwDQYJKoZIhvcN\nAQEBBQADggEPADCCAQoCggEBANhkGTXOCKEYf5znDDeX3n/DHFPVqazgQsr0/SIG\n4eb1JY5q5Jq3ZhAaZCr9HJuCkwAP/zgYH0llqOvf8AC2Uh+7z1b33IbwxPmJfWCP\nAqSNFkLWWVRdbELapCu408QsrLMW8IrdP6PLiKAepwncfm4T0/6bANqIEmUkpw8Q\nxProeiNwlGbwUll+tELmdCk7vA7hKX3j1kUvS5Z84Z5ivJBWEcUEggmC97TK4aLo\nFVEHbyahze568JVEaM1vY5L4mnRRTl+u5ipaSMxVBsiXzF7eFuKCzqF7wxbDIt2T\nIFEJtwyJDW5bXjyXgiF1d5H/URprUcRV9Qmf2+PXcfwHII8CAwEAAaOBvDCBuTAS\nBgNVHRMBAf8ECDAGAQH/AgEAMA4GA1UdDwEB/wQEAwIBBjAfBgNVHSMEGDAWgBQl\neng3lqGBeTrbLVuABoEmUHm1+TBTBgNVHR8ETDBKMEigRqBEhkJodHRwOi8vc2Vj\ndXJlLnN0YWdpbmcuc2VjdXJpdHljcmVkZW50aWFsaW5nLmNvbS9jcmwvdnpuZXRy\nc2FjYS5jcmwwHQYDVR0OBBYEFP0Z+/vaDLtAoFig1I9ttNKnmzByMA0GCSqGSIb3\nDQEBCwUAA4ICAQBuXVTf9e01HeymHgRcFCwP2N6G6u+vIzY8Bz0zSUZeRDHMZQcS\nNoabDyn5FfGJlw4BqGC591Sp0/unFQDzAg17rDBcrgwajeFeUiFdb9PiAJwHaX9S\nvq/7VmVLCmpeb+a/laXAe6+tkY1kcFrd1+ItRKC6ZGXMsoDkmk5Ndxxgw77estcI\nMiiLQbvpXRygX5wD4/ayazuLms9qITZkOZ1nTLVqq7QrwYCsSoih7hj6sbsfXr19\nGoYWmk8Y7O/d3ttgyHuRH9k/2dQ/xL7avRpMNkPdr7ocJqI46hvx2X6UyOo7IBua\nkSkFbSmPZWIVAidNMBOnvffCQ32tfjT2/xso/a9cdskvxqgLi0MPARU9Nl2Pufsb\nD7l4/sBvz/PiNTKp+Daa9FdyLb9ySidos1uS0c24bUtY1RXXGAVV2qgfyrzvzfye\nSM+w16hMU/yeYiuA1jsPmsnZnuIJj4Nv8ZjjZ0WS53pP5wcghaHkBrqWQNT8meqA\nVElrMBPlYq67T+AXP0B9lf5Sc3QVIio7XKKfqrlcQxY2JGLEyE53JgZGX7dpwU4I\nukLvyHbT4p06oY3qG6+wH8+YIXCNAYtadJ/C5/u9GcLX5NnZrcuduj0inw2/a3Ao\nWgCt6/Pr28BkCvkWdDt9d8Z40qeu1aZdcr157mR+yZGPfBfB2vasrNIEwQ==\n-----END CERTIFICATE-----\n'})

TASK [remote/trust : Generate trust_ca.pem] ****************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/trust : Copy trust_ca.pem to host] ************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/trust : Install certificate] ******************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/trust : Remove temporary working directory] ***************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [Remote Starlingx] ************************************************************************************************************************

TASK [remote/starlingx : Create temporary working directory] ***********************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/starlingx : Copy SSL root certificates] *******************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost] => (item={'filename': 'vz_root_ica_cert.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIFNzCCAx+gAwIBAgIUGLJR/hP48n+vdq2v1hcfspXo/78wDQYJKoZIhvcNAQEL\nBQAwWjELMAkGA1UEBhMCVVMxEDAOBgNVBAoMB1Zlcml6b24xEzARBgNVBAsMClZa\nSUFNIFRlc3QxJDAiBgNVBAMMG1Zlcml6b24gTmV0d29yayBSU0EgQ0EgVGVzdDAe\nFw0yMDEwMjIyMTE0MDNaFw0zMDEwMjIyMTE0MDNaMIGRMQswCQYDVQQGEwJVUzEL\nMAkGA1UECAwCVFgxETAPBgNVBAcMCFdlc3RsYWtlMRAwDgYDVQQKDAdWZXJpem9u\nMR0wGwYDVQQLDBRWZXJpem9uIFNvdXJjaW5nIExMQzExMC8GA1UEAwwoVmVyaXpv\nbiBOZXR3b3JrIFdFTEtUWElCIExBQiAxIDMgUlNBIElDQTCCASIwDQYJKoZIhvcN\nAQEBBQADggEPADCCAQoCggEBANhkGTXOCKEYf5znDDeX3n/DHFPVqazgQsr0/SIG\n4eb1JY5q5Jq3ZhAaZCr9HJuCkwAP/zgYH0llqOvf8AC2Uh+7z1b33IbwxPmJfWCP\nAqSNFkLWWVRdbELapCu408QsrLMW8IrdP6PLiKAepwncfm4T0/6bANqIEmUkpw8Q\nxProeiNwlGbwUll+tELmdCk7vA7hKX3j1kUvS5Z84Z5ivJBWEcUEggmC97TK4aLo\nFVEHbyahze568JVEaM1vY5L4mnRRTl+u5ipaSMxVBsiXzF7eFuKCzqF7wxbDIt2T\nIFEJtwyJDW5bXjyXgiF1d5H/URprUcRV9Qmf2+PXcfwHII8CAwEAAaOBvDCBuTAS\nBgNVHRMBAf8ECDAGAQH/AgEAMA4GA1UdDwEB/wQEAwIBBjAfBgNVHSMEGDAWgBQl\neng3lqGBeTrbLVuABoEmUHm1+TBTBgNVHR8ETDBKMEigRqBEhkJodHRwOi8vc2Vj\ndXJlLnN0YWdpbmcuc2VjdXJpdHljcmVkZW50aWFsaW5nLmNvbS9jcmwvdnpuZXRy\nc2FjYS5jcmwwHQYDVR0OBBYEFP0Z+/vaDLtAoFig1I9ttNKnmzByMA0GCSqGSIb3\nDQEBCwUAA4ICAQBuXVTf9e01HeymHgRcFCwP2N6G6u+vIzY8Bz0zSUZeRDHMZQcS\nNoabDyn5FfGJlw4BqGC591Sp0/unFQDzAg17rDBcrgwajeFeUiFdb9PiAJwHaX9S\nvq/7VmVLCmpeb+a/laXAe6+tkY1kcFrd1+ItRKC6ZGXMsoDkmk5Ndxxgw77estcI\nMiiLQbvpXRygX5wD4/ayazuLms9qITZkOZ1nTLVqq7QrwYCsSoih7hj6sbsfXr19\nGoYWmk8Y7O/d3ttgyHuRH9k/2dQ/xL7avRpMNkPdr7ocJqI46hvx2X6UyOo7IBua\nkSkFbSmPZWIVAidNMBOnvffCQ32tfjT2/xso/a9cdskvxqgLi0MPARU9Nl2Pufsb\nD7l4/sBvz/PiNTKp+Daa9FdyLb9ySidos1uS0c24bUtY1RXXGAVV2qgfyrzvzfye\nSM+w16hMU/yeYiuA1jsPmsnZnuIJj4Nv8ZjjZ0WS53pP5wcghaHkBrqWQNT8meqA\nVElrMBPlYq67T+AXP0B9lf5Sc3QVIio7XKKfqrlcQxY2JGLEyE53JgZGX7dpwU4I\nukLvyHbT4p06oY3qG6+wH8+YIXCNAYtadJ/C5/u9GcLX5NnZrcuduj0inw2/a3Ao\nWgCt6/Pr28BkCvkWdDt9d8Z40qeu1aZdcr157mR+yZGPfBfB2vasrNIEwQ==\n-----END CERTIFICATE-----\n'})
changed: [welktxef-931887-rz-le2pts6-021 -> localhost] => (item={'filename': 'vz_root_ica_key.pem', 'value': '-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA2GQZNc4IoRh/nOcMN5fef8McU9WprOBCyvT9Igbh5vUljmrk\nmrdmEBpkKv0cm4KTAA//OBgfSWWo69/wALZSH7vPVvfchvDE+Yl9YI8CpI0WQtZZ\nVF1sQtqkK7jTxCyssxbwit0/o8uIoB6nCdx+bhPT/psA2ogSZSSnDxDE+uh6I3CU\nZvBSWX60QuZ0KTu8DuEpfePWRS9LlnzhnmK8kFYRxQSCCYL3tMrhougVUQdvJqHN\n7nrwlURozW9jkviadFFOX67mKlpIzFUGyJfMXt4W4oLOoXvDFsMi3ZMgUQm3DIkN\nbltePJeCIXV3kf9RGmtRxFX1CZ/b49dx/AcgjwIDAQABAoIBABSd1NkPfDr8/ouQ\nZ9WUHprFmBlUrgnOhA6aMNPhG/zJNn7PKGClQJAgM5L08pjOY/sJiyNpCPIRQXrX\npyIqPMDRP/vlOZmRrvKnas6cUYAkAQ71JSWokPv9oM6ZmXODXiDh+qEAW2PbrHS0\n9u01mMYcFYKYeghYFoiUaWZCDsJo3v3dgeE9aQ4tB9ksovSmWrpuCY7NKbd7Qrbo\n5XxQhkujTkE6knOHz8CVwYETtj8LZ/bvHIkGMGvRvwsKYDZkIKr5CZ7DX+KcMfPN\neMZU4VCHYSXNxsyp5DJ1Zw+gx8/32kUL0CzJLLam1G021Hq41KPwwSV/KPrOKel7\nHXDLXeECgYEA8MR+lgxGjYTc/k4TdZvcFVgqHGLXnyjO7ZVt4b7UpwmayLuoSD/M\nOpHQYX+JBIIWTNlGhG8UV3DPC3v+auhYa7twwbekS30IYCAmu5GCKgMAcWFinz6A\nYZxG55P/hShetCyOqikgwXqzMlwGs8KEul8f8BKssROzUy8mIlFhjq0CgYEA5hTM\nSNxAD3dlRtb0771fBU7fjx8JPfjptP9vP/JVEelkc/ti9nZ5buTC+9cQC/B+YFx7\nc82uCrXV13bGR9iH8xBhwU7JOYJZbgCpwp0F56wIN5Pdk9Eo79Batrw3oGBG4Yvt\nDc2eltxQbHgObc/qygf88j9XqD8aGIvQrc4Jf6sCgYAtxX03M1A6WTbWFau3YRD+\n8crXqKbLOCvWmODR2MB+nOHTJXHBgndl7xCJaIB43e41X9z7Ek7wrJ5/1WuxkUg1\n+uVdvna6byOnepVCdVAkgnuUEmp4UZ6AcAA+yDD8dIdEg2//w1/ZyGTGvx37EJDB\nCZJ9xl8ULuWZe84pGgWM5QKBgQCYVUbYKrNjShrM5z9uh4QlII6V1Oeql2YtBz4i\nKZE3db6jp9pi8hf+WwnZ8g9WyFjz9edqydAkmTXHHYW0ReHlBYCjm0VRhUMuuNOs\n3YfuVpFuMsFuv/oJpXqaKE3wKi5j4OAH1o7ctWuuFWMAQ7vhHZ7UySmBZJ4jiFaW\n7KaPVwKBgE8E0xbSDVGxXbEGwRXxeaOSemEHD9uEnbAyq1p3EBBhBvInWmDiP5vJ\n68IYNZ4SGxXEKDifwrLGHyekt3RK9B2+U03okd1qH7gfBIlxBJivcjhBe2PtK/Qj\n6fBN0fC1UJoE6pseT9cJDaBq2wMRXJGRYtT8fU9PPJcfa23JlKNS\n-----END RSA PRIVATE KEY-----\n'})

TASK [remote/starlingx : Copy templates] *******************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost] => (item=req_starlingx.cnf)

TASK [remote/starlingx : Generate SSL cert] ****************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/starlingx : Copy SSL starlingx certs to server] ***********************************************************************************
changed: [welktxef-931887-rz-le2pts6-021] => (item=starlingx-ca-cert.pem)

TASK [remote/starlingx : Configure starlingx] **************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/starlingx : Remove temporary working directory] ***********************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [Remote Integ] ****************************************************************************************************************************

TASK [remote/integ : Detect applied status of platform-integ-apps application] *****************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/integ : Fail if platform-integ-apps application apply failed] *********************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [Remote Ldap] *****************************************************************************************************************************

TASK [remote/ldap : Create temporary working directory] ****************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/ldap : Copy SSL root certificates] ************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost] => (item={'filename': 'vz_root_ca_cert.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIFpTCCA42gAwIBAgIUa3vZ0YGxO1TQ8NwhiVfQC0JslXgwDQYJKoZIhvcNAQEL\nBQAwWjELMAkGA1UEBhMCVVMxEDAOBgNVBAoMB1Zlcml6b24xEzARBgNVBAsMClZa\nSUFNIFRlc3QxJDAiBgNVBAMMG1Zlcml6b24gTmV0d29yayBSU0EgQ0EgVGVzdDAe\nFw0yMDA2MTUyMTAxMTNaFw0zNTA2MTUyMTAxMTNaMFoxCzAJBgNVBAYTAlVTMRAw\nDgYDVQQKDAdWZXJpem9uMRMwEQYDVQQLDApWWklBTSBUZXN0MSQwIgYDVQQDDBtW\nZXJpem9uIE5ldHdvcmsgUlNBIENBIFRlc3QwggIiMA0GCSqGSIb3DQEBAQUAA4IC\nDwAwggIKAoICAQC8AIrksI57CbIl5uGZ6yqfpQj3aK+N8f1EVHdwK9JFskoipvC8\n7yFTk8tgmO1i0YA5oRGfNxneqCdrXZiWL6Ko8v/iln9vuN+2rK3rgWZPPRJBAsBN\na49L7U6lJjIGxIZtZqmK5h47oiUtwlYVrbZMN2ijuBQ22/eQ9tsFDV28oBuZ3WAR\npSSbj/tubPQYkw3YYOhv/VpEpsd0rkoEt3QCmTVcX2rtblanpXowTV5R0Hy4014n\nT49jrEo40r4mwYoyS835Uv4ENUFA+pXicT9eUot3RSH6rYdx4A/14UtoI9U0ol8M\n62GHpxSASQ2Kc3yQWvxRGTFslTduYM+vVmMLEDDdqcsjYnStPpwdxxmKItmbjxSv\nIwYIndp8A04WkX2iiJCciC3BNxiLamPtYVyB1HHqbGTGirKYuSvwZt337q1OI3WH\nwVn2S4Mj/wqa4iCyGTvFSUnGq34Xkrb9XNwWBok9Tc2XWGAU/mb/xcd1hX74GZbF\nsrZ11aPtym4kMAjU2KQi96GcAH2lnGZYoOja1J4Cs4WYx1uAx74H/m84CrYavVfl\n1ONJVLDfuZaEkSmu+jHQX15pAECNORTuLD06PbWnOEcOi1xmbt/OT3SA3rhD2mb7\n2wxl7oJpV3ap8xGwYmxiFzmInxFJ1axjg8Rimol0mXTKAy6OdNHbCOnAwwIDAQAB\no2MwYTAPBgNVHRMBAf8EBTADAQH/MA4GA1UdDwEB/wQEAwIBBjAfBgNVHSMEGDAW\ngBQleng3lqGBeTrbLVuABoEmUHm1+TAdBgNVHQ4EFgQUJXp4N5ahgXk62y1bgAaB\nJlB5tfkwDQYJKoZIhvcNAQELBQADggIBADQ9jpmVh9nyY7ZQ4s+S9RuSRYn7QsrW\nDePeMzQgh8ZtS8WE65GY5HS61iHNP2Co8Q1lAaBWF4ipq+VZOcQbPLccHzd1kZv4\ns4u0aTzBd9ccidl73FS0DJDQOBbzPSzgsaiGHSMyGzkTeA8z3ntsSqrXXcDUvoRi\nFus/110AwdtNhJLrWveX6btYtHp9Lqe0YtNCy5AaXlrr1yRSckP5BWVtlwD4dzSO\n/dqI3wHS/ncUx9wSQomZ+AmxYW3KtJQKgHzTqHru1x9BBk7Bzfz9FZr6HLLmEitj\nuFoDRd5TNt5LbO0zDQokvY3oqso6Htup/rS7C08mcmnelYE+yXuOc1YrlyGnpBzk\nmy+1VYbOxRRdqKAZRbE72u/h847IVpsOvjR51iksuCAurZdp2+y2zvV8NhWekuNy\nirECRy9cb4YasjRaKi0/TCGPVSICuLyeG2W72liCj/N2VKfjPP9zsOR5XjwCXfRg\n+9xhLy77/gov2NWXx5fzTkhxCrHOxFdLVMn0wQhksDmw6QsXzDIHSpIOypdDfnx9\nCsthx3nhkuHLUaEP22D22dG+vImA9ukj4R/RRI/87jmi9Q8+ehH+NqN0GZZcLjdN\nSLVXpncuwWQFUDPR06wNkkkmBSXWiIYhwqSpU0Pl3er3fD0uWvXuWPm2PzfOmUAE\nUrkzyw9XmLw0\n-----END CERTIFICATE-----\n'})
changed: [welktxef-931887-rz-le2pts6-021 -> localhost] => (item={'filename': 'vz_root_ica_cert.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIFNzCCAx+gAwIBAgIUGLJR/hP48n+vdq2v1hcfspXo/78wDQYJKoZIhvcNAQEL\nBQAwWjELMAkGA1UEBhMCVVMxEDAOBgNVBAoMB1Zlcml6b24xEzARBgNVBAsMClZa\nSUFNIFRlc3QxJDAiBgNVBAMMG1Zlcml6b24gTmV0d29yayBSU0EgQ0EgVGVzdDAe\nFw0yMDEwMjIyMTE0MDNaFw0zMDEwMjIyMTE0MDNaMIGRMQswCQYDVQQGEwJVUzEL\nMAkGA1UECAwCVFgxETAPBgNVBAcMCFdlc3RsYWtlMRAwDgYDVQQKDAdWZXJpem9u\nMR0wGwYDVQQLDBRWZXJpem9uIFNvdXJjaW5nIExMQzExMC8GA1UEAwwoVmVyaXpv\nbiBOZXR3b3JrIFdFTEtUWElCIExBQiAxIDMgUlNBIElDQTCCASIwDQYJKoZIhvcN\nAQEBBQADggEPADCCAQoCggEBANhkGTXOCKEYf5znDDeX3n/DHFPVqazgQsr0/SIG\n4eb1JY5q5Jq3ZhAaZCr9HJuCkwAP/zgYH0llqOvf8AC2Uh+7z1b33IbwxPmJfWCP\nAqSNFkLWWVRdbELapCu408QsrLMW8IrdP6PLiKAepwncfm4T0/6bANqIEmUkpw8Q\nxProeiNwlGbwUll+tELmdCk7vA7hKX3j1kUvS5Z84Z5ivJBWEcUEggmC97TK4aLo\nFVEHbyahze568JVEaM1vY5L4mnRRTl+u5ipaSMxVBsiXzF7eFuKCzqF7wxbDIt2T\nIFEJtwyJDW5bXjyXgiF1d5H/URprUcRV9Qmf2+PXcfwHII8CAwEAAaOBvDCBuTAS\nBgNVHRMBAf8ECDAGAQH/AgEAMA4GA1UdDwEB/wQEAwIBBjAfBgNVHSMEGDAWgBQl\neng3lqGBeTrbLVuABoEmUHm1+TBTBgNVHR8ETDBKMEigRqBEhkJodHRwOi8vc2Vj\ndXJlLnN0YWdpbmcuc2VjdXJpdHljcmVkZW50aWFsaW5nLmNvbS9jcmwvdnpuZXRy\nc2FjYS5jcmwwHQYDVR0OBBYEFP0Z+/vaDLtAoFig1I9ttNKnmzByMA0GCSqGSIb3\nDQEBCwUAA4ICAQBuXVTf9e01HeymHgRcFCwP2N6G6u+vIzY8Bz0zSUZeRDHMZQcS\nNoabDyn5FfGJlw4BqGC591Sp0/unFQDzAg17rDBcrgwajeFeUiFdb9PiAJwHaX9S\nvq/7VmVLCmpeb+a/laXAe6+tkY1kcFrd1+ItRKC6ZGXMsoDkmk5Ndxxgw77estcI\nMiiLQbvpXRygX5wD4/ayazuLms9qITZkOZ1nTLVqq7QrwYCsSoih7hj6sbsfXr19\nGoYWmk8Y7O/d3ttgyHuRH9k/2dQ/xL7avRpMNkPdr7ocJqI46hvx2X6UyOo7IBua\nkSkFbSmPZWIVAidNMBOnvffCQ32tfjT2/xso/a9cdskvxqgLi0MPARU9Nl2Pufsb\nD7l4/sBvz/PiNTKp+Daa9FdyLb9ySidos1uS0c24bUtY1RXXGAVV2qgfyrzvzfye\nSM+w16hMU/yeYiuA1jsPmsnZnuIJj4Nv8ZjjZ0WS53pP5wcghaHkBrqWQNT8meqA\nVElrMBPlYq67T+AXP0B9lf5Sc3QVIio7XKKfqrlcQxY2JGLEyE53JgZGX7dpwU4I\nukLvyHbT4p06oY3qG6+wH8+YIXCNAYtadJ/C5/u9GcLX5NnZrcuduj0inw2/a3Ao\nWgCt6/Pr28BkCvkWdDt9d8Z40qeu1aZdcr157mR+yZGPfBfB2vasrNIEwQ==\n-----END CERTIFICATE-----\n'})
changed: [welktxef-931887-rz-le2pts6-021 -> localhost] => (item={'filename': 'vz_root_ica_key.pem', 'value': '-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA2GQZNc4IoRh/nOcMN5fef8McU9WprOBCyvT9Igbh5vUljmrk\nmrdmEBpkKv0cm4KTAA//OBgfSWWo69/wALZSH7vPVvfchvDE+Yl9YI8CpI0WQtZZ\nVF1sQtqkK7jTxCyssxbwit0/o8uIoB6nCdx+bhPT/psA2ogSZSSnDxDE+uh6I3CU\nZvBSWX60QuZ0KTu8DuEpfePWRS9LlnzhnmK8kFYRxQSCCYL3tMrhougVUQdvJqHN\n7nrwlURozW9jkviadFFOX67mKlpIzFUGyJfMXt4W4oLOoXvDFsMi3ZMgUQm3DIkN\nbltePJeCIXV3kf9RGmtRxFX1CZ/b49dx/AcgjwIDAQABAoIBABSd1NkPfDr8/ouQ\nZ9WUHprFmBlUrgnOhA6aMNPhG/zJNn7PKGClQJAgM5L08pjOY/sJiyNpCPIRQXrX\npyIqPMDRP/vlOZmRrvKnas6cUYAkAQ71JSWokPv9oM6ZmXODXiDh+qEAW2PbrHS0\n9u01mMYcFYKYeghYFoiUaWZCDsJo3v3dgeE9aQ4tB9ksovSmWrpuCY7NKbd7Qrbo\n5XxQhkujTkE6knOHz8CVwYETtj8LZ/bvHIkGMGvRvwsKYDZkIKr5CZ7DX+KcMfPN\neMZU4VCHYSXNxsyp5DJ1Zw+gx8/32kUL0CzJLLam1G021Hq41KPwwSV/KPrOKel7\nHXDLXeECgYEA8MR+lgxGjYTc/k4TdZvcFVgqHGLXnyjO7ZVt4b7UpwmayLuoSD/M\nOpHQYX+JBIIWTNlGhG8UV3DPC3v+auhYa7twwbekS30IYCAmu5GCKgMAcWFinz6A\nYZxG55P/hShetCyOqikgwXqzMlwGs8KEul8f8BKssROzUy8mIlFhjq0CgYEA5hTM\nSNxAD3dlRtb0771fBU7fjx8JPfjptP9vP/JVEelkc/ti9nZ5buTC+9cQC/B+YFx7\nc82uCrXV13bGR9iH8xBhwU7JOYJZbgCpwp0F56wIN5Pdk9Eo79Batrw3oGBG4Yvt\nDc2eltxQbHgObc/qygf88j9XqD8aGIvQrc4Jf6sCgYAtxX03M1A6WTbWFau3YRD+\n8crXqKbLOCvWmODR2MB+nOHTJXHBgndl7xCJaIB43e41X9z7Ek7wrJ5/1WuxkUg1\n+uVdvna6byOnepVCdVAkgnuUEmp4UZ6AcAA+yDD8dIdEg2//w1/ZyGTGvx37EJDB\nCZJ9xl8ULuWZe84pGgWM5QKBgQCYVUbYKrNjShrM5z9uh4QlII6V1Oeql2YtBz4i\nKZE3db6jp9pi8hf+WwnZ8g9WyFjz9edqydAkmTXHHYW0ReHlBYCjm0VRhUMuuNOs\n3YfuVpFuMsFuv/oJpXqaKE3wKi5j4OAH1o7ctWuuFWMAQ7vhHZ7UySmBZJ4jiFaW\n7KaPVwKBgE8E0xbSDVGxXbEGwRXxeaOSemEHD9uEnbAyq1p3EBBhBvInWmDiP5vJ\n68IYNZ4SGxXEKDifwrLGHyekt3RK9B2+U03okd1qH7gfBIlxBJivcjhBe2PtK/Qj\n6fBN0fC1UJoE6pseT9cJDaBq2wMRXJGRYtT8fU9PPJcfa23JlKNS\n-----END RSA PRIVATE KEY-----\n'})

TASK [remote/ldap : Copy templates] ************************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost] => (item={'name': 'req-ldap.cnf', 'mode': '0644'})

TASK [remote/ldap : Generate SSL cert] *********************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/ldap : Copy templates] ************************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021] => (item={'name': 'dex-overrides.yaml', 'mode': '0644'})

TASK [remote/ldap : Copy SSL dex certs to server] **********************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021] => (item=dex-cert.pem)
changed: [welktxef-931887-rz-le2pts6-021] => (item=dex-key.pem)
changed: [welktxef-931887-rz-le2pts6-021] => (item=dex-ca.pem)

TASK [remote/ldap : Copy SSL AD cert to server] ************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021] => (item={'filename': 'ad_ca.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIFpTCCA42gAwIBAgIUa3vZ0YGxO1TQ8NwhiVfQC0JslXgwDQYJKoZIhvcNAQEL\nBQAwWjELMAkGA1UEBhMCVVMxEDAOBgNVBAoMB1Zlcml6b24xEzARBgNVBAsMClZa\nSUFNIFRlc3QxJDAiBgNVBAMMG1Zlcml6b24gTmV0d29yayBSU0EgQ0EgVGVzdDAe\nFw0yMDA2MTUyMTAxMTNaFw0zNTA2MTUyMTAxMTNaMFoxCzAJBgNVBAYTAlVTMRAw\nDgYDVQQKDAdWZXJpem9uMRMwEQYDVQQLDApWWklBTSBUZXN0MSQwIgYDVQQDDBtW\nZXJpem9uIE5ldHdvcmsgUlNBIENBIFRlc3QwggIiMA0GCSqGSIb3DQEBAQUAA4IC\nDwAwggIKAoICAQC8AIrksI57CbIl5uGZ6yqfpQj3aK+N8f1EVHdwK9JFskoipvC8\n7yFTk8tgmO1i0YA5oRGfNxneqCdrXZiWL6Ko8v/iln9vuN+2rK3rgWZPPRJBAsBN\na49L7U6lJjIGxIZtZqmK5h47oiUtwlYVrbZMN2ijuBQ22/eQ9tsFDV28oBuZ3WAR\npSSbj/tubPQYkw3YYOhv/VpEpsd0rkoEt3QCmTVcX2rtblanpXowTV5R0Hy4014n\nT49jrEo40r4mwYoyS835Uv4ENUFA+pXicT9eUot3RSH6rYdx4A/14UtoI9U0ol8M\n62GHpxSASQ2Kc3yQWvxRGTFslTduYM+vVmMLEDDdqcsjYnStPpwdxxmKItmbjxSv\nIwYIndp8A04WkX2iiJCciC3BNxiLamPtYVyB1HHqbGTGirKYuSvwZt337q1OI3WH\nwVn2S4Mj/wqa4iCyGTvFSUnGq34Xkrb9XNwWBok9Tc2XWGAU/mb/xcd1hX74GZbF\nsrZ11aPtym4kMAjU2KQi96GcAH2lnGZYoOja1J4Cs4WYx1uAx74H/m84CrYavVfl\n1ONJVLDfuZaEkSmu+jHQX15pAECNORTuLD06PbWnOEcOi1xmbt/OT3SA3rhD2mb7\n2wxl7oJpV3ap8xGwYmxiFzmInxFJ1axjg8Rimol0mXTKAy6OdNHbCOnAwwIDAQAB\no2MwYTAPBgNVHRMBAf8EBTADAQH/MA4GA1UdDwEB/wQEAwIBBjAfBgNVHSMEGDAW\ngBQleng3lqGBeTrbLVuABoEmUHm1+TAdBgNVHQ4EFgQUJXp4N5ahgXk62y1bgAaB\nJlB5tfkwDQYJKoZIhvcNAQELBQADggIBADQ9jpmVh9nyY7ZQ4s+S9RuSRYn7QsrW\nDePeMzQgh8ZtS8WE65GY5HS61iHNP2Co8Q1lAaBWF4ipq+VZOcQbPLccHzd1kZv4\ns4u0aTzBd9ccidl73FS0DJDQOBbzPSzgsaiGHSMyGzkTeA8z3ntsSqrXXcDUvoRi\nFus/110AwdtNhJLrWveX6btYtHp9Lqe0YtNCy5AaXlrr1yRSckP5BWVtlwD4dzSO\n/dqI3wHS/ncUx9wSQomZ+AmxYW3KtJQKgHzTqHru1x9BBk7Bzfz9FZr6HLLmEitj\nuFoDRd5TNt5LbO0zDQokvY3oqso6Htup/rS7C08mcmnelYE+yXuOc1YrlyGnpBzk\nmy+1VYbOxRRdqKAZRbE72u/h847IVpsOvjR51iksuCAurZdp2+y2zvV8NhWekuNy\nirECRy9cb4YasjRaKi0/TCGPVSICuLyeG2W72liCj/N2VKfjPP9zsOR5XjwCXfRg\n+9xhLy77/gov2NWXx5fzTkhxCrHOxFdLVMn0wQhksDmw6QsXzDIHSpIOypdDfnx9\nCsthx3nhkuHLUaEP22D22dG+vImA9ukj4R/RRI/87jmi9Q8+ehH+NqN0GZZcLjdN\nSLVXpncuwWQFUDPR06wNkkkmBSXWiIYhwqSpU0Pl3er3fD0uWvXuWPm2PzfOmUAE\nUrkzyw9XmLw0\n-----END CERTIFICATE-----\n'})

TASK [remote/ldap : Configure local-dex.tls] ***************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/ldap : Configure generic] *********************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/ldap : Configure wadcert] *********************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/ldap : Configure dex-overrides.yaml] **********************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/ldap : Wait for distributed cloud synchronization] ********************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001]

TASK [remote/ldap : Remove temporary working directory] ****************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/ldap : Detect oidc-auth-apps application in applying state (from a previous attempt)] *********************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/ldap : Fail if oidc-auth-apps application-abort failed] ***************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/ldap : Detect oidc-auth-apps application in apply-failed or aborted state] ********************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/ldap : Fail if oidc-auth-apps application apply failed] ***************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/ldap : Apply oidc-auth-apps application] ******************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/ldap : Detect applied status of oidc-auth-apps application] ***********************************************************************
FAILED - RETRYING: Detect applied status of oidc-auth-apps application (60 retries left).
FAILED - RETRYING: Detect applied status of oidc-auth-apps application (59 retries left).
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/ldap : Fail if oidc-auth-apps application apply failed] ***************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [Remote Metrics Server] *******************************************************************************************************************

TASK [remote/metrics-server : Set facts - 21.05] ***********************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Set facts - 21.12] ***********************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Get software load status] ****************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Noop if the system is NOT at the right caas_version] *************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Print message if system is NOT at the right caas_version] ********************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Detect presence of existing application] *************************************************************************
fatal: [welktxef-931887-rz-le2pts6-021]: FAILED! => {"changed": true, "cmd": ". /etc/platform/openrc\nsystem application-show metrics-server --column status --format value\n", "delta": "0:00:02.111076", "end": "2023-09-15 03:11:59.038340", "msg": "non-zero return code", "rc": 1, "start": "2023-09-15 03:11:56.927264", "stderr": "application not found: metrics-server", "stderr_lines": ["application not found: metrics-server"], "stdout": "", "stdout_lines": []}
...ignoring

TASK [remote/metrics-server : Print message if system already has the appication] **************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Apply again since the previous apply failed or in uploaded state] ************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Wait until apply is in the applied or apply-failed state] ********************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Print message if re-apply succeeds] ******************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Print message if re-apply failed] ********************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Noop if system requires no further action or needs manual investigation] *****************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Upload application] **********************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Wait until application is in the uploaded state] *****************************************************************
FAILED - RETRYING: Wait until application is in the uploaded state (30 retries left).
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Apply application] ***********************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Wait until application is in the applied or apply-failed state] **************************************************
FAILED - RETRYING: Wait until application is in the applied or apply-failed state (90 retries left).
FAILED - RETRYING: Wait until application is in the applied or apply-failed state (89 retries left).
FAILED - RETRYING: Wait until application is in the applied or apply-failed state (88 retries left).
FAILED - RETRYING: Wait until application is in the applied or apply-failed state (87 retries left).
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Apply again since the first apply failed] ************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Wait again until apply is in the applied or apply-failed state] **************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Print message if apply is successful] ****************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "msg": [
        "=======================================================",
        " welktxef-d931887-021: metrics-server install SUCCEEDED! ",
        "======================================================="
    ]
}

TASK [remote/metrics-server : Print message if apply is failure] *******************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [Remote wrap-get-central-version] *********************************************************************************************************

TASK [remote/wrap-get-central-version : Set facts for playbook] ********************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/wrap-get-central-version : Determine central WRA current version] *****************************************************************
fatal: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001]: FAILED! => {"changed": true, "cmd": ". /etc/platform/openrc\nsystem application-show wr-analytics --column app_version --format value\n", "delta": "0:00:01.356250", "end": "2023-09-15 03:13:21.453793", "msg": "non-zero return code", "rc": 1, "start": "2023-09-15 03:13:20.097543", "stderr": "application not found: wr-analytics", "stderr_lines": ["application not found: wr-analytics"], "stdout": "", "stdout_lines": []}
...ignoring

TASK [remote/wrap-get-central-version : Set facts for wra_target_version] **********************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/wrap-get-central-version : debug] *************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "msg": "wra_target_version:"
}

TASK [Remote wrap-2112-2] **********************************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [Remote wrap-2106-2] **********************************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [Remote wrap-6] ***************************************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [Remote fpga-user-image] ******************************************************************************************************************

TASK [remote/fpga-user-image : Set facts for ansible credential - 21.05] ***********************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Set facts for ansible credential - 21.12] ***********************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Get software load status] ***************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Noop if the system is NOT at the right caas_version] ************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Print message if system is NOT at the right caas_version] *******************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Set facts for default fpga_image_file] **************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Set facts for fpga_image_file from host_vars] *******************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Print message if server is not LS3 cascadelake] *****************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "msg": [
        "==================================================================================",
        " Server type ZTS-LS6-pts6 is not LS3 cascadelake, no action will take place! ",
        "=================================================================================="
    ]
}

TASK [remote/fpga-user-image : Register noop because server is not LS3 cascadelake] ************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Check if FPGA update is stuck] **********************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Abort FPGA update] **********************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : include_tasks] **************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Check FPGA update status (HPE-LS3-e910)] ************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Check FPGA update status (ZTS-LS3-trtn)] ************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Noop if the system has been updated] ****************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Print message if the system has been updated] *******************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : In main block] **************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Copy files to host] *********************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021] => (item=20ww43.5-1x2x25G-5GLDPC-v1.6.2-3.0.1-unsigned.bin)

TASK [remote/fpga-user-image : Do system device-image-upload] **********************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : debug - print UUID] *********************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Do system device-image-apply] ***********************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Do system host-device-image-update] *****************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Wait till application completed] ********************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Do system device-image-state-list] ******************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : force an error if image state is not completed] *****************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : include_tasks] **************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [Install DM Monitor] **********************************************************************************************************************

TASK [common/dm-monitor : Install DM Monitor] **************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [common/dm-monitor : Wait for DM Monitor pod created] *************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [common/dm-monitor : Wait for control-plane pods become ready] ****************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [common/dm-monitor : debug] ***************************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "dm_monitor_pod_ready.stdout_lines": [
        "pod/dm-monitor-77fd4b6649-g7ffx condition met"
    ]
}

TASK [Proteus MWIAT - DISABLE] *****************************************************************************************************************

TASK [remote/zt-redfish : Update Attributes at /redfish/v1/Systems/Self/Bios/SD] ***************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/zt-redfish : Update result] *******************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "update_result": {
        "allow": "GET, PUT, PATCH, POST",
        "changed": false,
        "connection": "close",
        "content": "",
        "cookies": {},
        "cookies_string": "",
        "date": "Fri, 15 Sep 2023 03:13:35 GMT",
        "elapsed": 0,
        "failed": false,
        "msg": "OK (unknown bytes)",
        "redirected": false,
        "server": "AMI MegaRAC Redfish Service",
        "status": 204,
        "url": "https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Systems/Self/Bios/SD"
    }
}

TASK [Lock/unlock after MWAIT change] **********************************************************************************************************

TASK [common/lock-unlock : set_fact] ***********************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [common/lock-unlock : include_tasks] ******************************************************************************************************
included: /home/XXXXXX/playbooks/wr-installer/roles/common/lock-unlock/tasks/lock_node.yaml for welktxef-931887-rz-le2pts6-021

TASK [common/lock-unlock : Check subcloud status before locking] *******************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [common/lock-unlock : debug] **************************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "msg": "The host is unlocked, continue with locking."
}

TASK [common/lock-unlock : Lock subcloud] ******************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [common/lock-unlock : Pause for 10 seconds for the command to complete] *******************************************************************
Pausing for 10 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [welktxef-931887-rz-le2pts6-021]

TASK [common/lock-unlock : Wait until subcloud is in locked status] ****************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [common/lock-unlock : Display subcloud status] ********************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "host_status_new.stdout": "locked"
}

TASK [common/lock-unlock : include_tasks] ******************************************************************************************************
included: /home/XXXXXX/playbooks/wr-installer/roles/common/lock-unlock/tasks/unlock_node.yaml for welktxef-931887-rz-le2pts6-021

TASK [common/lock-unlock : Check subcloud status before unlocking] *****************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [common/lock-unlock : Unlock subcloud] ****************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [common/lock-unlock : Wait for node to restart (port 22 goes down)] ***********************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [common/lock-unlock : Wait for node be back up (port 5000 comes up)] **********************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [common/lock-unlock : Obtain Keystone auth token] *****************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [common/lock-unlock : Wait for contoller-0 enabled] ***************************************************************************************
FAILED - RETRYING: Wait for contoller-0 enabled (60 retries left).
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

PLAY RECAP *************************************************************************************************************************************
welktxef-931887-rz-le2pts6-021 : ok=133  changed=58   unreachable=0    failed=0    skipped=63   rescued=0    ignored=4

[XXXXXX@welktxefnce-h-pe1util-vm01 wr-installer]$



```
### success on installation, running postdeployment playbook to ensure complete install and test


### POst deployment playbook

```log
[XXXXXX@welktxefnce-h-pe1util-vm01 wrcp_post_deployment]$ ansible-playbook --vault-password-file /tmp/vault-pass -i inventory/ri_1.yaml wrcp_subcloud_post_deployment.yaml

PLAY [Post deployment steps fro WRCP subclouds] ******************************************************************************************************************

TASK [set vendor as samsung] *************************************************************************************************************************************
ok: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : create vdu namespace] ******************************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]
included: /home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/generic/tasks/create_generic_resources.yaml for welktxef-931887-rz-le0pts6-021

TASK [subclouds/generic : Create working directory] **************************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : Template generic files into workdir] ***************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/generic/templates/samsung/generic/crd-role.yaml.j2)
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/generic/templates/samsung/generic/orchestration_sa_cluster.yaml.j2)
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/generic/templates/samsung/generic/orchestration_sa.yaml.j2)
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/generic/templates/samsung/generic/samsung_debug_sa.yaml.j2)
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/generic/templates/samsung/generic/ss_sa.yaml.j2)

TASK [subclouds/generic : Create generic resources] **************************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]
included: /home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/generic/tasks/create_k8s_files.yaml for welktxef-931887-rz-le0pts6-021

TASK [subclouds/generic : Create working directory] **************************************************************************************************************
ok: [welktxef-931887-rz-le0pts6-021 -> localhost]

TASK [subclouds/generic : Get token for Orch - 21.05] ************************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : store orch token] **********************************************************************************************************************
ok: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : Get token for SS Debug] ****************************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : store ss token] ************************************************************************************************************************
ok: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : print orch token] **********************************************************************************************************************
ok: [welktxef-931887-rz-le0pts6-021] => {
    "orch_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6Im01VE1hcjcwNkFGNFBzX3I0Y0dHOFJNdlBJMmxTTzk2cmFkQkVqZG04Z1UifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6Im9yY2hlc3RyYXRpb24tc2EtdG9rZW4tN2dtbGwiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoib3JjaGVzdHJhdGlvbi1zYSIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6IjdhNTlhYzUzLTM3OTItNGZhOC1hY2JlLTNmMDdjODc3NGNmYSIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpkZWZhdWx0Om9yY2hlc3RyYXRpb24tc2EifQ.y3HKjZwbmNy-WuqeqOBmAZy60wj4om7UCWbgmxdKZhFXqbGl2sIFs2zwblzuWGTPGjTXv2wj21KAOFqOQ4FXJdxcvtBRZYTfvHC07Sc1iCxoBuyPFc7sqklsSEVy1k64jFg1IOMkQsyUy8mOaWVqLAjw62xGJsPsSQcalH6PNN-uTlpivLOXI1Lim3aiqP-6O2eO6RhAUnZ_vwuQKbvPtyTG7zCPdqM5hqtesWRSsEDYf9QGm4MTV8iWNEtOQ_0SS05GctOF6mm_pHLd4Pk_NVxD2acjeqbw0fLucY-3PAxB7-QT67EfA_sZHYaeLSQNv1V0U7CIxxd8gfio5_TpLg"
}

TASK [subclouds/generic : print ss token] ************************************************************************************************************************
ok: [welktxef-931887-rz-le0pts6-021] => {
    "ss_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6Im01VE1hcjcwNkFGNFBzX3I0Y0dHOFJNdlBJMmxTTzk2cmFkQkVqZG04Z1UifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6InNhbXN1bmctc2EtdG9rZW4tNnJucDQiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoic2Ftc3VuZy1zYSIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6IjU0MDU2NGZmLTFmNzctNDA4MC05MmIyLTI0MTc4MDA5OTQxNCIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpkZWZhdWx0OnNhbXN1bmctc2EifQ.LtJgFRWY_Nn1IONjibD3ZAzjcEd-H_wa0ARD2-VF4knvPBOAMgqPmtv44UfBL77Iw3UoFUwLQ6W5KnuJfQiQtUBZ9XGRIw0UM0QwO8pDbpfKy59i34DavkNKvIHKX6T0vVhN4JxSe2rYkA1ygj-GHjhnQpEsmaaOM5zEdcuoW_B2YSbPzpCXAEBkm829fCOTc_GYvrq40WP5QTfzJWef-XXrOZ61huE3j89R_nCe8awjGeM4pZSUW-xTiwl21QotbKDXrOSEqm_YNOpOlCQFBzR6mTotWpwgBuzcPbGCiMaaGYgHZEtZdYh-R6QJHZtbpA_zSzQOKUHdHjiIOcv6rQ"
}

TASK [subclouds/generic : Template k8s files into temp dir] ******************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021 -> localhost] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/generic/templates/samsung/k8s/kubeconfig-orchestration.conf.j2)
changed: [welktxef-931887-rz-le0pts6-021 -> localhost] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/generic/templates/samsung/k8s/kubeconfig-samsung-debug.conf.j2)
included: /home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/generic/tasks/create_local_registry_secret.yaml for welktxef-931887-rz-le0pts6-021

TASK [subclouds/generic : Create secret in welktxef-931887vzwcvdu-y-ss-ls6-00000000021 for pulling from local registry] ******************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : Create alternative secret in welktxef-931887vzwcvdu-y-ss-ls6-00000000021 for pulling from vudorch's own registry] **********************
changed: [welktxef-931887-rz-le0pts6-021]
included: /home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/generic/tasks/update_platform_integ_apps.yaml for welktxef-931887-rz-le0pts6-021

TASK [subclouds/generic : Create working directory] **************************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : Template platform integ apps override file into temp dir] ******************************************************************************
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/generic/tasks/../templates/samsung/platform-integ/rbd-namespaces.yaml.j2)

TASK [subclouds/generic : Update platform integ apps] ************************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]
FAILED - RETRYING: Wait until application is out of the applying state (90 retries left).

TASK [subclouds/generic : Wait until application is out of the applying state] ***********************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]
included: /home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/generic/tasks/store_ptp_notification_client_image.yaml for welktxef-931887-rz-le0pts6-021

TASK [subclouds/generic : set the correct tag for notificationclient-base image - up to 21.12] *******************************************************************
ok: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : Log in registry.central] ***************************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : Pull ptp notification client image from registry.central] ******************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : Log out from registry.central] *********************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : Tag ptp notification client image from registry.central] *******************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : Log in registry.local] *****************************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : Push ptp notification client image to registry.local] **********************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : Log out from registry.local] ***********************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : Delete image from Docker cache] ********************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : create vdu namespace] *****************************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]
included: /home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/tasks/lock_node.yaml for welktxef-931887-rz-le0pts6-021

TASK [subclouds/specific : Check subcloud status before locking] *************************************************************************************************
ok: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Lock subcloud] ************************************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]
Pausing for 10 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)

TASK [subclouds/specific : Pause for 10 seconds for the command to complete] *************************************************************************************
ok: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Wait until subcloud is in locked status] **********************************************************************************************
ok: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Display subcloud status] **************************************************************************************************************
ok: [welktxef-931887-rz-le0pts6-021] => {
    "subcloud_status.stdout_lines": [
        "+----+--------------+-------------+----------------+-------------+--------------+",
        "| id | hostname     | personality | administrative | operational | availability |",
        "+----+--------------+-------------+----------------+-------------+--------------+",
        "| 1  | controller-0 | controller  | locked         | disabled    | online       |",
        "+----+--------------+-------------+----------------+-------------+--------------+"
    ]
}
included: /home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/tasks/system_configs_ls6.yaml for welktxef-931887-rz-le0pts6-021

TASK [subclouds/specific : Configure CPU] ************************************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Configure sriov0] *********************************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Configure sriov1] *********************************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Configure fh0] ************************************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Configure fh1] ************************************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Configure fh2] ************************************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Configure fh3] ************************************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Configure fh4] ************************************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Configure fh5] ************************************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Configure ptp] ************************************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Configure PLM] ************************************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]
Pausing for 120 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)

TASK [subclouds/specific : Wait for PLM configuration to complete] ***********************************************************************************************
ok: [welktxef-931887-rz-le0pts6-021]
included: /home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/tasks/unlock_node.yaml for welktxef-931887-rz-le0pts6-021

TASK [subclouds/specific : Check subcloud status before unlocking] ***********************************************************************************************
ok: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Unlock subcloud] **********************************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Wait for node to restart (port 22 goes down)] *****************************************************************************************
ok: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Wait for node be back up (port 5000 comes up)] ****************************************************************************************
ok: [welktxef-931887-rz-le0pts6-021]
FAILED - RETRYING: Obtain Keystone auth token (60 retries left).

TASK [subclouds/specific : Obtain Keystone auth token] ***********************************************************************************************************
ok: [welktxef-931887-rz-le0pts6-021 -> localhost]

TASK [subclouds/specific : Wait for contoller-0 enabled] *********************************************************************************************************
ok: [welktxef-931887-rz-le0pts6-021 -> localhost]
included: /home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/tasks/create_nads.yaml for welktxef-931887-rz-le0pts6-021

TASK [subclouds/specific : Create working directory] *************************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : set_fact] *****************************************************************************************************************************
ok: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Template NAD files into temp dir] *****************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/templates/samsung/LS6_21D/NAD/adpf-ca-nad.yaml.j2)
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/templates/samsung/LS6_21D/NAD/adpf-f1c-nad.yaml.j2)
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/templates/samsung/LS6_21D/NAD/adpf-f1u-nad.yaml.j2)
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/templates/samsung/LS6_21D/NAD/adpf-fh0-nad.yaml.j2)
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/templates/samsung/LS6_21D/NAD/adpf-fh0m-nad.yaml.j2)
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/templates/samsung/LS6_21D/NAD/adpf-fh1-nad.yaml.j2)
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/templates/samsung/LS6_21D/NAD/adpf-fh1m-nad.yaml.j2)
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/templates/samsung/LS6_21D/NAD/adpf-fh2-nad.yaml.j2)
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/templates/samsung/LS6_21D/NAD/adpf-fh2m-nad.yaml.j2)
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/templates/samsung/LS6_21D/NAD/adpf-fh3-nad.yaml.j2)
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/templates/samsung/LS6_21D/NAD/adpf-fh4-nad.yaml.j2)
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/templates/samsung/LS6_21D/NAD/adpf-fh5-nad.yaml.j2)

TASK [subclouds/specific : Create NADs] **************************************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]
included: /home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/tasks/create_rbac.yaml for welktxef-931887-rz-le0pts6-021

TASK [subclouds/specific : Create working directory] *************************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Template RBAC files into temp dir] ****************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/templates/samsung/rbac/rbac_ss_sa_new_install.yaml.j2)

TASK [subclouds/specific : Create RBACs] *************************************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]
included: /home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/tasks/install_ptp_notification_app.yaml for welktxef-931887-rz-le0pts6-021

TASK [subclouds/specific : Add necessary labels to the host] *****************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : set_fact] *****************************************************************************************************************************
ok: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Upload ptp-notification app] **********************************************************************************************************
fatal: [welktxef-931887-rz-le0pts6-021]: FAILED! => {"changed": true, "cmd": "source /etc/platform/openrc\nset -e\nsystem application-upload /usr/local/share/applications/helm/ptp-notification-21.05-49.tgz\n", "delta": "0:00:01.803221", "end": "2023-09-15 04:01:28.964869", "msg": "non-zero return code", "rc": 1, "start": "2023-09-15 04:01:27.161648", "stderr": "Error: Tar file /usr/local/share/applications/helm/ptp-notification-21.05-49.tgz does not exist", "stderr_lines": ["Error: Tar file /usr/local/share/applications/helm/ptp-notification-21.05-49.tgz does not exist"], "stdout": "", "stdout_lines": []}

PLAY RECAP *******************************************************************************************************************************************************
welktxef-931887-rz-le0pts6-021 : ok=72   changed=42   unreachable=0    failed=1    skipped=25   rescued=0    ignored=0

[XXXXXX@welktxefnce-h-pe1util-vm01 wrcp_post_deployment]$


```

### succesful deployment

### wiping and starting over...

```log

TASK [Remote Configure] ************************************************************************************************************************

TASK [remote/remote-configure : Set facts for vip, ansible, and wr_admin] **********************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Set facts for wr_release_version] ******************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Print wr_release_version] **************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "msg": "wr_release_version: 21.12"
}

TASK [remote/remote-configure : Set fact wr_distribution_directory to use based on WR version] *************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Set fact wr_distribution_directory to use based on WR version] *************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Set facts for which image list to use based on WR version] *****************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Set facts for which image list to use based on WR version] *****************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Set facts for which image list to use based on WR version] *****************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Print wr_image_list] *******************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "msg": "wr_image_list: /opt/external/vcpfe-team/artifacts/WRCP-2112/wind-river-cloud-platform-container-images-list-21.12.txt"
}

TASK [remote/remote-configure : Set fact to wr_license_key] ************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Set fact to wr_license_key] ************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : print wr_license_key] ******************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "msg": "wr_license_key = IyBXaW5kIFJpdmVyIFByb2R1Y3QgQWN0aXZhdGlvbiBGaWxlIChpbnN0YWxsLnR4dCkKIyBJc3N1ZWQgZm9yIGhvc3Q6IDxWZXJpem9uPiA8VmVyaXpvbj4gPEFueT4KIyBMaWNlbnNlIG51bWJlcihzKTogNjgyMzc0CiMgSXNzdWVkIG9uOiAyNi1qYW4tMjAyMiAwOTo1MDo1MAojCiMgTm90ZTogdGhpcyBsaWNlbnNlIGlzIGdlbmVyYXRlZCBjdW11bGF0aXZlbHkgZm9yIGFsbAojIFdpbmQgUml2ZXIgc29mdHdhcmUgbWFuYWdlZCBieSB0aGlzIGhvc3QuCgojIDEuIEZsZXhMTSBsaWNlbnNlIGZpbGU6CiMgQmVnaW46IFNlcnZlciBsaWNlbnNlICAtLS0tLS0tLS0tLS0tLS0tLS0tLS0KIyBTZXJpYWwgTnVtYmVyOiA2ODQ0NDktVmVyaXpvblBPQy1HNFdEQzlDUEVLCgpQQUNLQUdFIFdSQ1BfQ09OVEFJTkVSX1BLRyB3cnNkIDIxIDAwNDY1REZDRUI5QiBcCglDT01QT05FTlRTPVdSQ1BfQ09OVEFJTkVSOjIxLjEyIE9QVElPTlM9U1VJVEUgXAoJU0lHTj0yNTAwQzhCMjRFRDAKSU5DUkVNRU5UIFdSQ1BfQ09OVEFJTkVSX1BLRyB3cnNkIDIxIHBlcm1hbmVudCB1bmNvdW50ZWQgNDQyRThBMzg2QUE4IFwKCVZFTkRPUl9TVFJJTkc9PGxuPjY4MjM3NDwvbG4+PHBzPjIyMTMtNDM8L3BzPiBIT1NUSUQ9QU5ZIFwKCUlTU1VFRD0yNi1qYW4tMjAyMiBTTj1zZXJpYWwtVmVyaXpvbi1MVjJJV0FVTEVCIFwKCVNUQVJUPTI2LWphbi0yMDIyIFNJR049QjUzNzk2OTBENEE2Cg=="
}

TASK [remote/remote-configure : Copy storage checking script if server is HPE-LS3-e910] ********************************************************
skipping: [welktxef-931887-rz-le2pts6-021] => (item=hpe_storage_check.py)

TASK [remote/remote-configure : Execute storage checking script if server is HPE-LS3-e910] *****************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor HPE HPE-LS3-e910 (4 disks)] *****************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor HPE HPE-LS3-e910 (2 disks)] *****************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor HPE HPE-LS3-92s3] ***************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor HPE HPE-LS6-92s6] ***************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor ZTS ZTS-LS3-trtn] ***************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Set facts for Corning] *****************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor ZTS ZTS-LS6-pts6 & ZTS-LS3-pts3] ************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor ZTS ZTS-LS6-aks6 & ZTS-LS3-aks3] ************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : set_fact] ******************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [include_role : remote/zt-redfish] ********************************************************************************************************

TASK [remote/zt-redfish : get content from /redfish/v1/Systems/Self] ***************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/zt-redfish : Extract and store BiosVersion from returned content] *****************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Set facts for BIOS version based on vendor ZTS ZTS-LS6-pts6 & ZTS-LS3-pts3] ************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : debug] *********************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "bios_version": "0.23"
}

TASK [remote/remote-configure : Find out which DM Docker version contral has] ******************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001]

TASK [remote/remote-configure : Find out which DM file version contral has] ********************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001]

TASK [remote/remote-configure : Print dm docker version and dm file version] *******************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "msg": "dm_docker_version: WRCP_21.12-wrs.4, dm_file: wind-river-cloud-platform-deployment-manager-2.0.8-4.tgz"
}

TASK [remote/remote-configure : Discover Wind River docker image names] ************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-configure : Print local_images_full] ***************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "msg": "docker.io/starlingx/ceph-config-helper:v1.15.0\ndocker.io/starlingx/dex:stx.4.0-v2.14.0-1\ndocker.io/starlingx/n3000-opae:stx.6.0-v1.0.1\ndocker.io/starlingx/stx-oidc-client:stx.5.0-v1.0.4\ndocker.io/wind-river/cloud-platform-deployment-manager:WRCP_21.12-wrs.4\ngcr.io/google_containers/kubernetes-dashboard-init-amd64:v1.0.0\ngcr.io/kubebuilder/kube-rbac-proxy:v0.4.0\nquay.io/external_storage/rbd-provisioner:v2.1.1-k8s1.11"
}

TASK [remote/remote-configure : Create fact for Wind River docker image names] *****************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Determine DM Helm Chart path] **********************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-configure : Print dm_helm_chart] *******************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "msg": "/opt/external/vcpfe-team/artifacts/WRCP-2112/wind-river-cloud-platform-deployment-manager-2.0.8-4.tgz"
}

TASK [remote/remote-configure : Set DM Helm Chart file] ****************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Lookup Deployment Manager image tag] ***************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-configure : Lookup RBAC Proxy image tag] ***********************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-configure : Copy WRCP DM Playbook] *****************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001] => (item=wind-river-cloud-platform-deployment-manager.yaml)
ok: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001] => (item=wind-river-cloud-platform-deployment-manager-2.0.8-4.tgz)

TASK [remote/remote-configure : Set a fact for the central controller VIP address] *************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Configure WRCP seed template] **********************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001] => (item={'src': 'bootstrap-values.yaml', 'dest': 'welktxef-d931887-021-bootstrap-values.yaml'})
ok: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001] => (item={'src': 'deploy-values.yaml', 'dest': 'welktxef-d931887-021-deploy-values.yaml'})
ok: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001] => (item={'src': 'deploy-standard.yaml', 'dest': 'welktxef-d931887-021-deploy-standard.yaml'})
ok: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001] => (item={'src': 'install-values.yaml', 'dest': 'welktxef-d931887-021-install-values.yaml'})

TASK [remote/remote-configure : Copy SSL cert files] *******************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001] => (item={'filename': 'k8s_root_ca_cert.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIF8jCCA9qgAwIBAgIJAIf9Ql2uDZh+MA0GCSqGSIb3DQEBDQUAMIGFMQswCQYD\nVQQGEwJVUzEOMAwGA1UECAwFVGV4YXMxETAPBgNVBAcMCFdlc3RsYWtlMR0wGwYD\nVQQKDBRWZXJpem9uIFNvdXJjaW5nIExMQzE0MDIGA1UEAwwrVmVyaXpvbiBOZXR3\nb3JrIFdFTEtUWElCIExBQiAxIDMgUlNBIEs4UyBDQTAeFw0yMDEwMjUyMjEyNDha\nFw0zMDEwMjMyMjEyNDhaMIGFMQswCQYDVQQGEwJVUzEOMAwGA1UECAwFVGV4YXMx\nETAPBgNVBAcMCFdlc3RsYWtlMR0wGwYDVQQKDBRWZXJpem9uIFNvdXJjaW5nIExM\nQzE0MDIGA1UEAwwrVmVyaXpvbiBOZXR3b3JrIFdFTEtUWElCIExBQiAxIDMgUlNB\nIEs4UyBDQTCCAiIwDQYJKoZIhvcNAQEBBQADggIPADCCAgoCggIBAKyF9svdv/qG\n7HxBr1DWvZ3CQiDsA4m1kj0hD7jo3B3W/32ODcPpgeNmp4Oful0SsndpqEGhXDq5\noiBfqszMUpzDgdQ7siIHekb2olFEK2KniMP3H53nilIppeyMby5K3ZwF0Qbmk5WK\ncoXoYegP+Uv9bV0AMH6Dn4CVgYrLAYfmPyGgUSt4vuZ9F/rf9UkBf/DcZGqMnMax\n/Gfaq8KwmDzD9D8IVCHPrM5f4+CaKMQCFu5QkSsLYJFRiuQWWaICMMdnqpb0HZh5\niPnCSHwPPUyXxtujdI97Ovy4X5WR46jJ2+KzPYe8tVa/DL3TlKmRL9AF+oSE17bw\nzGAE7GNWxPojebHIUuoKdOQC1qiJBVS+c14r9+9P2Uy6XEhNUs+h3juRI4U3YkQ1\nUCUU3opqhOPh4jUIuPGg5aX07lt4Wpxc48D+CY1D4i6vaJLl3WCsVK7PFwWVQQEW\nIQabfuj1R2jEu7pp2Yabza58S00v1P5/kv/DNr7ADm8eYRvxLAAXCedMeSDXKBgd\npPmVXXZoZ8+X8VRGYxcw0mBBLIAiTOntT2vgLeq5T3QyiVKdU6TLAYEjS65QZ3Eg\naIX0wRqlcQI7lruTXubtENG6wWXYtnDf5795ZID1YIEqkgzZLMBqq1SBiLnWd6aK\n78Zsr4j5GmTBGpKRmwE2oO1btJCCYyG5AgMBAAGjYzBhMA8GA1UdEwEB/wQFMAMB\nAf8wHQYDVR0OBBYEFEDQ5EaGp3x02WUuvqetygqpM3dCMB8GA1UdIwQYMBaAFEDQ\n5EaGp3x02WUuvqetygqpM3dCMA4GA1UdDwEB/wQEAwICpDANBgkqhkiG9w0BAQ0F\nAAOCAgEAeCMxVJr5Jyg87DVaUtEhiWfhto993ENrnevAGqrBOoRc/KU1/C3paqhR\nsvr2r2LR+npSmeo6iz0FaO31XwHSHX95+XJeGP5Q8TGddbRiTglQsMfOkGNzxqgg\nTkdZ8A1y9v2jprONUmLADVGIVT0AoHc7V9w1I8NKhrY+rIllum4FRDiDPSnImh5h\nxmH+Nq2ZuEFVdtV/oNKzEu2ywmbgBRd5Jv3rTejxltmTZtyq8IKoKguj3NVFn93Q\nU4TbsxkcAdrLMooLYYDRTWA4t0iqKM/UkYUg4xl2l9NrY7ZUbaNd5+YsLNdqXO/c\nmp7wyMv/8ZIy1BLG4zJmX/JzWkYmULqQ+A+21+YuqrV3a81V7vcHhJcRaPOrg5cd\nYwY2eCbXMvNOdrzppIglUrlddNuqAhs1MTi/VibxYuI9isU0JckXIcCy1L+xbEda\n6v/z6wSrScVz0I4m0DpK6xMQ8t9sLcrGp5uGbj6J4nQWd+QLdq6kmAzDOZ/Gs0wb\nPYdkER4dXAVcioYFekpKv7d+nur0FPtMNIw0OdhX2eAwC22IFAq2DZRjUFvaBGaD\ni1ptfq6P1mVJ2T/exYujEDtq+8yQTfWgFm/DjEfWtcCp0Jukgv8opLR2DpCf5Ucq\nd5X7d/DP0mukJ3vZ8EIqYorwZJ1L1a2jgngjA+gPxIaW+JHfTHU=\n-----END CERTIFICATE-----\n'})
ok: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001] => (item={'filename': 'k8s_root_ca_key.pem', 'value': '-----BEGIN PRIVATE KEY-----\nMIIJQQIBADANBgkqhkiG9w0BAQEFAASCCSswggknAgEAAoICAQCshfbL3b/6hux8\nQa9Q1r2dwkIg7AOJtZI9IQ+46Nwd1v99jg3D6YHjZqeDn7pdErJ3aahBoVw6uaIg\nX6rMzFKcw4HUO7IiB3pG9qJRRCtip4jD9x+d54pSKaXsjG8uSt2cBdEG5pOVinKF\n6GHoD/lL/W1dADB+g5+AlYGKywGH5j8hoFEreL7mfRf63/VJAX/w3GRqjJzGsfxn\n2qvCsJg8w/Q/CFQhz6zOX+PgmijEAhbuUJErC2CRUYrkFlmiAjDHZ6qW9B2YeYj5\nwkh8Dz1Ml8bbo3SPezr8uF+VkeOoydvisz2HvLVWvwy905SpkS/QBfqEhNe28Mxg\nBOxjVsT6I3mxyFLqCnTkAtaoiQVUvnNeK/fvT9lMulxITVLPod47kSOFN2JENVAl\nFN6KaoTj4eI1CLjxoOWl9O5beFqcXOPA/gmNQ+Iur2iS5d1grFSuzxcFlUEBFiEG\nm37o9UdoxLu6admGm82ufEtNL9T+f5L/wza+wA5vHmEb8SwAFwnnTHkg1ygYHaT5\nlV12aGfPl/FURmMXMNJgQSyAIkzp7U9r4C3quU90MolSnVOkywGBI0uuUGdxIGiF\n9MEapXECO5a7k17m7RDRusFl2LZw3+e/eWSA9WCBKpIM2SzAaqtUgYi51nemiu/G\nbK+I+RpkwRqSkZsBNqDtW7SQgmMhuQIDAQABAoICACysO62qa+2pRk8eixD5qfvR\ns2Hm+zuLYqSljPaqhWTMqTePswzJyDJkAHhawd0b3E6Dc2gbKlCihNKxMv744WNq\nVJHqK0QYf5ckgf9dEYboLsffk7ZFoFGKK0bHTnrENAIUl32b8xdD1EfMVp3KlRkS\nNGFijSwVVRXsoLCZxHm2Kx6/7oS9LWFtfuodV9xhoQlzaCUW5/mjWOJjgxpUs/b4\nHqS7uV1P80U1G0KraGboy5tGDXEB7y1x2e8Zwnfq7UqVE10nNQqoXcmefzpwj8Tn\ngDybZLFKjYmnDEkkj7jDHEbldsdRG/usWNZGlTYbPDA3fBkYdOsQCzvJypQmgbZ+\n3yk3Lj2+9vLEMfPrruuzyOSXgki6o5uvy7Je6PdBpsz75k8FH6a+Rw3vvP8HuP3S\nLSUYm3tyOheXHR7BKN4bnfi11RAWvDpT9S+QnZ+R8DmQzOADlnjRC8WewDJYoNJ1\np1jeuqswlxo144oMO92cmdS2dAbPvS6aQP1I85Q2NniY+6YhHkBwIQIlfVs1JPbY\nX7QtTy1IXQhR3sospyvUwY2GPSAeVHDRL53ClQKDsvWpSy0MAmWYJkZu1P+jKBim\nj34ytApgG65Hv/RHf3L4+4zzItZ3TN2tJ/g9EKc6oMNtqKbbG56kkmvRPWKtMGV8\nFqxCvG5NydUK7fN+P2WJAoIBAQDXLFC//Fn9ed1U+pKa2M25aJwEetkGLXQvkwVi\n8uJFaXITb2ceveSEo6iBExyn4eYL5A4X+RZdJJdRRbj4whsNN13Pm+6lYX3pp7MN\nO+78uvwVfKZiWPFKfZs7ZH1/O9VIlLGnXUHeaHK1tmv9ixxMixdnjUDkcVa0O3qT\nKBLpvXnVEMYizxQBN0P5Z9QvQQGpUhKnNw+FhV1SP+YHxrB0Pu6qbYAmZZC2MQc1\nTsDyqGjmHk9VJaFYAAPEjqACDbfnkVUCj0ylM4xPQuBJs9DOKh4InG+znusdmd8H\nmvoEFDppsrH1NhO6GTeuCk6n0WBi6cUm76K/gPscYyV4ZtkfAoIBAQDNQgDXtfqv\nxbAhvDk0o/P8fqOdgQF0uFTqYHmyW31Ty9nF0ptA8LVJOIljU3zlLplhIFjBnSEG\nLqu4jnLLRR+zej0MXmJuZ9BMWmQeTrZzttnH5bn54E07DPJ5BvFoTMJNklBiXjB5\n5hTPZS4yK1KjoxY+Ypnj4W1iZjP37ya/A34J2nlYtoW4LdVfJHqCxBXel9Nz2zkv\nvwwPu8Eu7gFLuhNQM6Iv4mORGI8yg7Y/BwodfDPRuFvrG1KXkjwASb0O5b1suRQy\n9H80q5EAbT36K1z48ilr8fcroN+hV8g4yntrBBgOHPMmBk/vHKU8B1rkBr0p2haI\n3PwKmDFRsDInAoIBAGrjjMmSZnHQk+6e+y0I/klYegiPrjevZMQtWMOqvFSW6SBW\nevd+hYKOeiqEf/u18D1/8LBgAIgMoU6yQAzy/9U059k2MPrez1m/AOdWGoZZrNhP\nr6ezX0oN04tRhDYsVutTUl09qnb9k95I3KR68nfjsKC0PsQ8uUGXOnDXu215vofl\naUfpbpqcBZxjw7glptmh97oxU/iUI6O0MmUygn18tbrb4okwcw7OlDIbCSaCGnoW\nHHrD0r6QY07FOx9KCU1zmLNI1F5MmSrWoex68wM3UOweKi8khs+RnIV+qyxTkCDp\nsBWL44jS9iHy5Nfg3uzEDDgnWsWfIR8c8YQ6MykCggEADr0ollTI9Yo6hZGggfkr\n8fueABddZWY/Ir1ev8H2E+hVcPEYmOcv/VwD8Y/zLfnUpbbO6MhBsNH1HsGL2LDT\n/+1NKPA2HTtzJ6ht/Acm7tQ4ezQx0JGcuhrJ5orrFtQ8N5nED+w3iulMoT/gu1WF\nD58MX9pwtn5ffmtcW/deTuUPTeHUSNyCaaFQ6w4RhgZSk7NPSch6KMWNNiwDST1p\n9mgcLuwmP04AXFDpJ3VxxsDYpxleFzcn0pAZtCyaBmNFIia5HW+E1cvcvol7Vg6C\nHs6yVGX/N3MejpF0vX8yL3HKvvqCR7EofJiDcOYbr13P1wPs3W59o8JKjvAyymze\njQKCAQAUY/0asRL33D7tFoIbLg/N9hi+tCCM35DMf2FeXm3QwSkAR/BJw0ewCE5C\n+VqukHN3/i0Xe8KSHwEuLK2sGLk9Ys8A5NytjqFApYwpIk8UrRONfC12H3ez5VYk\nJlhMVhVXEZvVhEFJiBC7q6x6s7BVtLTGV7FA5CW8YKBhwHwrpm+h/Xb798oaKyel\nP/xYq+GZzfWfbvUjZvgN0J0RGxKA+GRgsmhoyOfgCVXgSzuUkI+9cAUvC0OV407L\n4XIK0GDJ7Tv/2USSPfmueyGEmacc/oYUPVBUgeINSoaCM4cpZwyLylVEtKOdQoEE\n77G5mvQsoXxsMjd+nbHil450UHsL\n-----END PRIVATE KEY-----\n'})

TASK [Proteus MWIAT - ENABLE] ******************************************************************************************************************

TASK [remote/zt-redfish : Update Attributes at /redfish/v1/Systems/Self/Bios/SD] ***************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/zt-redfish : Update result] *******************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "update_result": {
        "allow": "GET, PUT, PATCH, POST",
        "changed": false,
        "connection": "close",
        "content": "",
        "cookies": {},
        "cookies_string": "",
        "date": "Fri, 15 Sep 2023 04:42:38 GMT",
        "elapsed": 0,
        "failed": false,
        "msg": "OK (unknown bytes)",
        "redirected": false,
        "server": "AMI MegaRAC Redfish Service",
        "status": 204,
        "url": "https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Systems/Self/Bios/SD"
    }
}

TASK [Remote Install] **************************************************************************************************************************

TASK [remote/remote-install : Check if the subcloud deployed but failed] ***********************************************************************
fatal: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001]: FAILED! => {"changed": true, "cmd": ". /etc/platform/openrc\ndcmanager subcloud show welktxef-d931887-021 --column \"deploy_status\" --format value\n", "delta": "0:00:01.228068", "end": "2023-09-15 04:42:41.264402", "msg": "non-zero return code", "rc": 1, "start": "2023-09-15 04:42:40.036334", "stderr": "ERROR (app) Subcloud not found", "stderr_lines": ["ERROR (app) Subcloud not found"], "stdout": "", "stdout_lines": []}
...ignoring

TASK [remote/remote-install : debug] ***********************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "msg": "subcloud_status:"
}

TASK [remote/remote-install : Delete the subcloud that's 'install-failed' & 'pre-install-failed'] **********************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-install : Deploy remote cloud] *********************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001]

TASK [remote/remote-install : 1st polling prep: Obtain Keystone auth token] ********************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-install : 1st polling: Wait for subcloud to start installing OS] ***********************************************************
FAILED - RETRYING: 1st polling: Wait for subcloud to start installing OS (40 retries left).
FAILED - RETRYING: 1st polling: Wait for subcloud to start installing OS (39 retries left).
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-install : 1st polling result: Fail if the installation failed] *************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-install : 2nd polling prep: Obtain Keystone auth token] ********************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-install : 2nd polling: Wait for subcloud to install OS (this will take a while)] *******************************************
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (100 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (99 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (98 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (97 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (96 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (95 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (94 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (93 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (92 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (91 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (90 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (89 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (88 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (87 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (86 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (85 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (84 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (83 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (82 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (81 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (80 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (79 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (78 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (77 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (76 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (75 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (74 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (73 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (72 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (71 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (70 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (69 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (68 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (67 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (66 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (65 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (64 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (63 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (62 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (61 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (60 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (59 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (58 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (57 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (56 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (55 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (54 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (53 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (52 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (51 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (50 retries left).
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-install : 2nd polling result: Fail if any error occurred] ******************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-install : 3rd polling prep: Obtain Keystone auth token] ********************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-install : 3rd polling: Wait for subcloud to install OS (this may take a while)] ********************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-install : 3rd polling result: Fail if any error occurred] ******************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-install : 4th polling prep: Obtain Keystone auth token] ********************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-install : 4th polling: Wait for subcloud to install OS (this may still take a while)] **************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-install : 4th polling result: Fail if the installation failed] *************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-install : 5th polling prep: Obtain Keystone auth token] ********************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-install : 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while)] *************************
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (100 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (99 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (98 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (97 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (96 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (95 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (94 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (93 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (92 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (91 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (90 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (89 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (88 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (87 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (86 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (85 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (84 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (83 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (82 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (81 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (80 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (79 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (78 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (77 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (76 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (75 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (74 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (73 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (72 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (71 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (70 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (69 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (68 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (67 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (66 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (65 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (64 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (63 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (62 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (61 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (60 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (59 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (58 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (57 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (56 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (55 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (54 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (53 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (52 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (51 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (50 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (49 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (48 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (47 retries left).
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-install : 5th polling result: Fail if bootstrap/deploy failed] *************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-install : 6th polling prep: Obtain Keystone auth token] ********************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-install : 6th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while)] *************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-install : 6th polling result: Fail if bootstrap/deploy failed] *************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-install : Wait for controller-0 restart] ***********************************************************************************
FAILED - RETRYING: Wait for controller-0 restart (40 retries left).
FAILED - RETRYING: Wait for controller-0 restart (39 retries left).
FAILED - RETRYING: Wait for controller-0 restart (38 retries left).
fatal: [welktxef-931887-rz-le2pts6-021]: FAILED! => {"attempts": 4, "changed": false, "elapsed": 5, "msg": "timed out waiting for ping module test success: Failed to connect to the host via ssh: ssh: connect to host 2607:f160:10:9249:ce:40a:0:f409 port 22: Connection refused"}
...ignoring

TASK [remote/remote-install : Wait for controller-0 recovery] **********************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-install : setup kdump] *****************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [Remote Cleanup] **************************************************************************************************************************

TASK [common/cleanup : Remove temporary working directory] *************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [Remote Manage] ***************************************************************************************************************************

TASK [remote/manage : 1st Obtain Keystone auth token] ******************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/manage : 1st Wait for contoller-0 availability status online] *********************************************************************
FAILED - RETRYING: 1st Wait for contoller-0 availability status online (100 retries left).
FAILED - RETRYING: 1st Wait for contoller-0 availability status online (99 retries left).
FAILED - RETRYING: 1st Wait for contoller-0 availability status online (98 retries left).
FAILED - RETRYING: 1st Wait for contoller-0 availability status online (97 retries left).
FAILED - RETRYING: 1st Wait for contoller-0 availability status online (96 retries left).
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/manage : 2nd Obtain Keystone auth token] ******************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/manage : 2nd Wait for contoller-0 availability status online] *********************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/manage : Wait for system to stabilize before running kubectl] *********************************************************************
Pausing for 480 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [welktxef-931887-rz-le2pts6-021]

TASK [Wait for distributed cloud to be reconciled] *********************************************************************************************

TASK [common/wait_for_reconciliation : Making sure node is reachable] **************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [common/wait_for_reconciliation : Wait for K8s API to be up] ******************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [common/wait_for_reconciliation : Wait for hosts to be reconciled] ************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [common/wait_for_reconciliation : Wait for systems to be reconciled] **********************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/manage : Wait for distributed cloud to be reconciled but subcloud OAM VIP becomes unreachable] ************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/manage : Check if the subcloud deployed but failed] *******************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001]

TASK [remote/manage : Set distributed cloud state to managed] **********************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001]

TASK [remote/manage : Wait for system to stabilize] ********************************************************************************************
Pausing for 300 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [welktxef-931887-rz-le2pts6-021]

TASK [Remote Trust] ****************************************************************************************************************************

TASK [remote/trust : Create temporary working directory] ***************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/trust : Copy SSL cert files to working dir] ***************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost] => (item={'filename': 'k8s_root_ca_cert.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIF8jCCA9qgAwIBAgIJAIf9Ql2uDZh+MA0GCSqGSIb3DQEBDQUAMIGFMQswCQYD\nVQQGEwJVUzEOMAwGA1UECAwFVGV4YXMxETAPBgNVBAcMCFdlc3RsYWtlMR0wGwYD\nVQQKDBRWZXJpem9uIFNvdXJjaW5nIExMQzE0MDIGA1UEAwwrVmVyaXpvbiBOZXR3\nb3JrIFdFTEtUWElCIExBQiAxIDMgUlNBIEs4UyBDQTAeFw0yMDEwMjUyMjEyNDha\nFw0zMDEwMjMyMjEyNDhaMIGFMQswCQYDVQQGEwJVUzEOMAwGA1UECAwFVGV4YXMx\nETAPBgNVBAcMCFdlc3RsYWtlMR0wGwYDVQQKDBRWZXJpem9uIFNvdXJjaW5nIExM\nQzE0MDIGA1UEAwwrVmVyaXpvbiBOZXR3b3JrIFdFTEtUWElCIExBQiAxIDMgUlNB\nIEs4UyBDQTCCAiIwDQYJKoZIhvcNAQEBBQADggIPADCCAgoCggIBAKyF9svdv/qG\n7HxBr1DWvZ3CQiDsA4m1kj0hD7jo3B3W/32ODcPpgeNmp4Oful0SsndpqEGhXDq5\noiBfqszMUpzDgdQ7siIHekb2olFEK2KniMP3H53nilIppeyMby5K3ZwF0Qbmk5WK\ncoXoYegP+Uv9bV0AMH6Dn4CVgYrLAYfmPyGgUSt4vuZ9F/rf9UkBf/DcZGqMnMax\n/Gfaq8KwmDzD9D8IVCHPrM5f4+CaKMQCFu5QkSsLYJFRiuQWWaICMMdnqpb0HZh5\niPnCSHwPPUyXxtujdI97Ovy4X5WR46jJ2+KzPYe8tVa/DL3TlKmRL9AF+oSE17bw\nzGAE7GNWxPojebHIUuoKdOQC1qiJBVS+c14r9+9P2Uy6XEhNUs+h3juRI4U3YkQ1\nUCUU3opqhOPh4jUIuPGg5aX07lt4Wpxc48D+CY1D4i6vaJLl3WCsVK7PFwWVQQEW\nIQabfuj1R2jEu7pp2Yabza58S00v1P5/kv/DNr7ADm8eYRvxLAAXCedMeSDXKBgd\npPmVXXZoZ8+X8VRGYxcw0mBBLIAiTOntT2vgLeq5T3QyiVKdU6TLAYEjS65QZ3Eg\naIX0wRqlcQI7lruTXubtENG6wWXYtnDf5795ZID1YIEqkgzZLMBqq1SBiLnWd6aK\n78Zsr4j5GmTBGpKRmwE2oO1btJCCYyG5AgMBAAGjYzBhMA8GA1UdEwEB/wQFMAMB\nAf8wHQYDVR0OBBYEFEDQ5EaGp3x02WUuvqetygqpM3dCMB8GA1UdIwQYMBaAFEDQ\n5EaGp3x02WUuvqetygqpM3dCMA4GA1UdDwEB/wQEAwICpDANBgkqhkiG9w0BAQ0F\nAAOCAgEAeCMxVJr5Jyg87DVaUtEhiWfhto993ENrnevAGqrBOoRc/KU1/C3paqhR\nsvr2r2LR+npSmeo6iz0FaO31XwHSHX95+XJeGP5Q8TGddbRiTglQsMfOkGNzxqgg\nTkdZ8A1y9v2jprONUmLADVGIVT0AoHc7V9w1I8NKhrY+rIllum4FRDiDPSnImh5h\nxmH+Nq2ZuEFVdtV/oNKzEu2ywmbgBRd5Jv3rTejxltmTZtyq8IKoKguj3NVFn93Q\nU4TbsxkcAdrLMooLYYDRTWA4t0iqKM/UkYUg4xl2l9NrY7ZUbaNd5+YsLNdqXO/c\nmp7wyMv/8ZIy1BLG4zJmX/JzWkYmULqQ+A+21+YuqrV3a81V7vcHhJcRaPOrg5cd\nYwY2eCbXMvNOdrzppIglUrlddNuqAhs1MTi/VibxYuI9isU0JckXIcCy1L+xbEda\n6v/z6wSrScVz0I4m0DpK6xMQ8t9sLcrGp5uGbj6J4nQWd+QLdq6kmAzDOZ/Gs0wb\nPYdkER4dXAVcioYFekpKv7d+nur0FPtMNIw0OdhX2eAwC22IFAq2DZRjUFvaBGaD\ni1ptfq6P1mVJ2T/exYujEDtq+8yQTfWgFm/DjEfWtcCp0Jukgv8opLR2DpCf5Ucq\nd5X7d/DP0mukJ3vZ8EIqYorwZJ1L1a2jgngjA+gPxIaW+JHfTHU=\n-----END CERTIFICATE-----\n'})
changed: [welktxef-931887-rz-le2pts6-021 -> localhost] => (item={'filename': 'vz_root_ca_cert.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIFpTCCA42gAwIBAgIUa3vZ0YGxO1TQ8NwhiVfQC0JslXgwDQYJKoZIhvcNAQEL\nBQAwWjELMAkGA1UEBhMCVVMxEDAOBgNVBAoMB1Zlcml6b24xEzARBgNVBAsMClZa\nSUFNIFRlc3QxJDAiBgNVBAMMG1Zlcml6b24gTmV0d29yayBSU0EgQ0EgVGVzdDAe\nFw0yMDA2MTUyMTAxMTNaFw0zNTA2MTUyMTAxMTNaMFoxCzAJBgNVBAYTAlVTMRAw\nDgYDVQQKDAdWZXJpem9uMRMwEQYDVQQLDApWWklBTSBUZXN0MSQwIgYDVQQDDBtW\nZXJpem9uIE5ldHdvcmsgUlNBIENBIFRlc3QwggIiMA0GCSqGSIb3DQEBAQUAA4IC\nDwAwggIKAoICAQC8AIrksI57CbIl5uGZ6yqfpQj3aK+N8f1EVHdwK9JFskoipvC8\n7yFTk8tgmO1i0YA5oRGfNxneqCdrXZiWL6Ko8v/iln9vuN+2rK3rgWZPPRJBAsBN\na49L7U6lJjIGxIZtZqmK5h47oiUtwlYVrbZMN2ijuBQ22/eQ9tsFDV28oBuZ3WAR\npSSbj/tubPQYkw3YYOhv/VpEpsd0rkoEt3QCmTVcX2rtblanpXowTV5R0Hy4014n\nT49jrEo40r4mwYoyS835Uv4ENUFA+pXicT9eUot3RSH6rYdx4A/14UtoI9U0ol8M\n62GHpxSASQ2Kc3yQWvxRGTFslTduYM+vVmMLEDDdqcsjYnStPpwdxxmKItmbjxSv\nIwYIndp8A04WkX2iiJCciC3BNxiLamPtYVyB1HHqbGTGirKYuSvwZt337q1OI3WH\nwVn2S4Mj/wqa4iCyGTvFSUnGq34Xkrb9XNwWBok9Tc2XWGAU/mb/xcd1hX74GZbF\nsrZ11aPtym4kMAjU2KQi96GcAH2lnGZYoOja1J4Cs4WYx1uAx74H/m84CrYavVfl\n1ONJVLDfuZaEkSmu+jHQX15pAECNORTuLD06PbWnOEcOi1xmbt/OT3SA3rhD2mb7\n2wxl7oJpV3ap8xGwYmxiFzmInxFJ1axjg8Rimol0mXTKAy6OdNHbCOnAwwIDAQAB\no2MwYTAPBgNVHRMBAf8EBTADAQH/MA4GA1UdDwEB/wQEAwIBBjAfBgNVHSMEGDAW\ngBQleng3lqGBeTrbLVuABoEmUHm1+TAdBgNVHQ4EFgQUJXp4N5ahgXk62y1bgAaB\nJlB5tfkwDQYJKoZIhvcNAQELBQADggIBADQ9jpmVh9nyY7ZQ4s+S9RuSRYn7QsrW\nDePeMzQgh8ZtS8WE65GY5HS61iHNP2Co8Q1lAaBWF4ipq+VZOcQbPLccHzd1kZv4\ns4u0aTzBd9ccidl73FS0DJDQOBbzPSzgsaiGHSMyGzkTeA8z3ntsSqrXXcDUvoRi\nFus/110AwdtNhJLrWveX6btYtHp9Lqe0YtNCy5AaXlrr1yRSckP5BWVtlwD4dzSO\n/dqI3wHS/ncUx9wSQomZ+AmxYW3KtJQKgHzTqHru1x9BBk7Bzfz9FZr6HLLmEitj\nuFoDRd5TNt5LbO0zDQokvY3oqso6Htup/rS7C08mcmnelYE+yXuOc1YrlyGnpBzk\nmy+1VYbOxRRdqKAZRbE72u/h847IVpsOvjR51iksuCAurZdp2+y2zvV8NhWekuNy\nirECRy9cb4YasjRaKi0/TCGPVSICuLyeG2W72liCj/N2VKfjPP9zsOR5XjwCXfRg\n+9xhLy77/gov2NWXx5fzTkhxCrHOxFdLVMn0wQhksDmw6QsXzDIHSpIOypdDfnx9\nCsthx3nhkuHLUaEP22D22dG+vImA9ukj4R/RRI/87jmi9Q8+ehH+NqN0GZZcLjdN\nSLVXpncuwWQFUDPR06wNkkkmBSXWiIYhwqSpU0Pl3er3fD0uWvXuWPm2PzfOmUAE\nUrkzyw9XmLw0\n-----END CERTIFICATE-----\n'})
changed: [welktxef-931887-rz-le2pts6-021 -> localhost] => (item={'filename': 'vz_root_ica_cert.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIFNzCCAx+gAwIBAgIUGLJR/hP48n+vdq2v1hcfspXo/78wDQYJKoZIhvcNAQEL\nBQAwWjELMAkGA1UEBhMCVVMxEDAOBgNVBAoMB1Zlcml6b24xEzARBgNVBAsMClZa\nSUFNIFRlc3QxJDAiBgNVBAMMG1Zlcml6b24gTmV0d29yayBSU0EgQ0EgVGVzdDAe\nFw0yMDEwMjIyMTE0MDNaFw0zMDEwMjIyMTE0MDNaMIGRMQswCQYDVQQGEwJVUzEL\nMAkGA1UECAwCVFgxETAPBgNVBAcMCFdlc3RsYWtlMRAwDgYDVQQKDAdWZXJpem9u\nMR0wGwYDVQQLDBRWZXJpem9uIFNvdXJjaW5nIExMQzExMC8GA1UEAwwoVmVyaXpv\nbiBOZXR3b3JrIFdFTEtUWElCIExBQiAxIDMgUlNBIElDQTCCASIwDQYJKoZIhvcN\nAQEBBQADggEPADCCAQoCggEBANhkGTXOCKEYf5znDDeX3n/DHFPVqazgQsr0/SIG\n4eb1JY5q5Jq3ZhAaZCr9HJuCkwAP/zgYH0llqOvf8AC2Uh+7z1b33IbwxPmJfWCP\nAqSNFkLWWVRdbELapCu408QsrLMW8IrdP6PLiKAepwncfm4T0/6bANqIEmUkpw8Q\nxProeiNwlGbwUll+tELmdCk7vA7hKX3j1kUvS5Z84Z5ivJBWEcUEggmC97TK4aLo\nFVEHbyahze568JVEaM1vY5L4mnRRTl+u5ipaSMxVBsiXzF7eFuKCzqF7wxbDIt2T\nIFEJtwyJDW5bXjyXgiF1d5H/URprUcRV9Qmf2+PXcfwHII8CAwEAAaOBvDCBuTAS\nBgNVHRMBAf8ECDAGAQH/AgEAMA4GA1UdDwEB/wQEAwIBBjAfBgNVHSMEGDAWgBQl\neng3lqGBeTrbLVuABoEmUHm1+TBTBgNVHR8ETDBKMEigRqBEhkJodHRwOi8vc2Vj\ndXJlLnN0YWdpbmcuc2VjdXJpdHljcmVkZW50aWFsaW5nLmNvbS9jcmwvdnpuZXRy\nc2FjYS5jcmwwHQYDVR0OBBYEFP0Z+/vaDLtAoFig1I9ttNKnmzByMA0GCSqGSIb3\nDQEBCwUAA4ICAQBuXVTf9e01HeymHgRcFCwP2N6G6u+vIzY8Bz0zSUZeRDHMZQcS\nNoabDyn5FfGJlw4BqGC591Sp0/unFQDzAg17rDBcrgwajeFeUiFdb9PiAJwHaX9S\nvq/7VmVLCmpeb+a/laXAe6+tkY1kcFrd1+ItRKC6ZGXMsoDkmk5Ndxxgw77estcI\nMiiLQbvpXRygX5wD4/ayazuLms9qITZkOZ1nTLVqq7QrwYCsSoih7hj6sbsfXr19\nGoYWmk8Y7O/d3ttgyHuRH9k/2dQ/xL7avRpMNkPdr7ocJqI46hvx2X6UyOo7IBua\nkSkFbSmPZWIVAidNMBOnvffCQ32tfjT2/xso/a9cdskvxqgLi0MPARU9Nl2Pufsb\nD7l4/sBvz/PiNTKp+Daa9FdyLb9ySidos1uS0c24bUtY1RXXGAVV2qgfyrzvzfye\nSM+w16hMU/yeYiuA1jsPmsnZnuIJj4Nv8ZjjZ0WS53pP5wcghaHkBrqWQNT8meqA\nVElrMBPlYq67T+AXP0B9lf5Sc3QVIio7XKKfqrlcQxY2JGLEyE53JgZGX7dpwU4I\nukLvyHbT4p06oY3qG6+wH8+YIXCNAYtadJ/C5/u9GcLX5NnZrcuduj0inw2/a3Ao\nWgCt6/Pr28BkCvkWdDt9d8Z40qeu1aZdcr157mR+yZGPfBfB2vasrNIEwQ==\n-----END CERTIFICATE-----\n'})

TASK [remote/trust : Generate trust_ca.pem] ****************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/trust : Copy trust_ca.pem to host] ************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/trust : Install certificate] ******************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/trust : Remove temporary working directory] ***************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [Remote Starlingx] ************************************************************************************************************************

TASK [remote/starlingx : Create temporary working directory] ***********************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/starlingx : Copy SSL root certificates] *******************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost] => (item={'filename': 'vz_root_ica_cert.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIFNzCCAx+gAwIBAgIUGLJR/hP48n+vdq2v1hcfspXo/78wDQYJKoZIhvcNAQEL\nBQAwWjELMAkGA1UEBhMCVVMxEDAOBgNVBAoMB1Zlcml6b24xEzARBgNVBAsMClZa\nSUFNIFRlc3QxJDAiBgNVBAMMG1Zlcml6b24gTmV0d29yayBSU0EgQ0EgVGVzdDAe\nFw0yMDEwMjIyMTE0MDNaFw0zMDEwMjIyMTE0MDNaMIGRMQswCQYDVQQGEwJVUzEL\nMAkGA1UECAwCVFgxETAPBgNVBAcMCFdlc3RsYWtlMRAwDgYDVQQKDAdWZXJpem9u\nMR0wGwYDVQQLDBRWZXJpem9uIFNvdXJjaW5nIExMQzExMC8GA1UEAwwoVmVyaXpv\nbiBOZXR3b3JrIFdFTEtUWElCIExBQiAxIDMgUlNBIElDQTCCASIwDQYJKoZIhvcN\nAQEBBQADggEPADCCAQoCggEBANhkGTXOCKEYf5znDDeX3n/DHFPVqazgQsr0/SIG\n4eb1JY5q5Jq3ZhAaZCr9HJuCkwAP/zgYH0llqOvf8AC2Uh+7z1b33IbwxPmJfWCP\nAqSNFkLWWVRdbELapCu408QsrLMW8IrdP6PLiKAepwncfm4T0/6bANqIEmUkpw8Q\nxProeiNwlGbwUll+tELmdCk7vA7hKX3j1kUvS5Z84Z5ivJBWEcUEggmC97TK4aLo\nFVEHbyahze568JVEaM1vY5L4mnRRTl+u5ipaSMxVBsiXzF7eFuKCzqF7wxbDIt2T\nIFEJtwyJDW5bXjyXgiF1d5H/URprUcRV9Qmf2+PXcfwHII8CAwEAAaOBvDCBuTAS\nBgNVHRMBAf8ECDAGAQH/AgEAMA4GA1UdDwEB/wQEAwIBBjAfBgNVHSMEGDAWgBQl\neng3lqGBeTrbLVuABoEmUHm1+TBTBgNVHR8ETDBKMEigRqBEhkJodHRwOi8vc2Vj\ndXJlLnN0YWdpbmcuc2VjdXJpdHljcmVkZW50aWFsaW5nLmNvbS9jcmwvdnpuZXRy\nc2FjYS5jcmwwHQYDVR0OBBYEFP0Z+/vaDLtAoFig1I9ttNKnmzByMA0GCSqGSIb3\nDQEBCwUAA4ICAQBuXVTf9e01HeymHgRcFCwP2N6G6u+vIzY8Bz0zSUZeRDHMZQcS\nNoabDyn5FfGJlw4BqGC591Sp0/unFQDzAg17rDBcrgwajeFeUiFdb9PiAJwHaX9S\nvq/7VmVLCmpeb+a/laXAe6+tkY1kcFrd1+ItRKC6ZGXMsoDkmk5Ndxxgw77estcI\nMiiLQbvpXRygX5wD4/ayazuLms9qITZkOZ1nTLVqq7QrwYCsSoih7hj6sbsfXr19\nGoYWmk8Y7O/d3ttgyHuRH9k/2dQ/xL7avRpMNkPdr7ocJqI46hvx2X6UyOo7IBua\nkSkFbSmPZWIVAidNMBOnvffCQ32tfjT2/xso/a9cdskvxqgLi0MPARU9Nl2Pufsb\nD7l4/sBvz/PiNTKp+Daa9FdyLb9ySidos1uS0c24bUtY1RXXGAVV2qgfyrzvzfye\nSM+w16hMU/yeYiuA1jsPmsnZnuIJj4Nv8ZjjZ0WS53pP5wcghaHkBrqWQNT8meqA\nVElrMBPlYq67T+AXP0B9lf5Sc3QVIio7XKKfqrlcQxY2JGLEyE53JgZGX7dpwU4I\nukLvyHbT4p06oY3qG6+wH8+YIXCNAYtadJ/C5/u9GcLX5NnZrcuduj0inw2/a3Ao\nWgCt6/Pr28BkCvkWdDt9d8Z40qeu1aZdcr157mR+yZGPfBfB2vasrNIEwQ==\n-----END CERTIFICATE-----\n'})
changed: [welktxef-931887-rz-le2pts6-021 -> localhost] => (item={'filename': 'vz_root_ica_key.pem', 'value': '-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA2GQZNc4IoRh/nOcMN5fef8McU9WprOBCyvT9Igbh5vUljmrk\nmrdmEBpkKv0cm4KTAA//OBgfSWWo69/wALZSH7vPVvfchvDE+Yl9YI8CpI0WQtZZ\nVF1sQtqkK7jTxCyssxbwit0/o8uIoB6nCdx+bhPT/psA2ogSZSSnDxDE+uh6I3CU\nZvBSWX60QuZ0KTu8DuEpfePWRS9LlnzhnmK8kFYRxQSCCYL3tMrhougVUQdvJqHN\n7nrwlURozW9jkviadFFOX67mKlpIzFUGyJfMXt4W4oLOoXvDFsMi3ZMgUQm3DIkN\nbltePJeCIXV3kf9RGmtRxFX1CZ/b49dx/AcgjwIDAQABAoIBABSd1NkPfDr8/ouQ\nZ9WUHprFmBlUrgnOhA6aMNPhG/zJNn7PKGClQJAgM5L08pjOY/sJiyNpCPIRQXrX\npyIqPMDRP/vlOZmRrvKnas6cUYAkAQ71JSWokPv9oM6ZmXODXiDh+qEAW2PbrHS0\n9u01mMYcFYKYeghYFoiUaWZCDsJo3v3dgeE9aQ4tB9ksovSmWrpuCY7NKbd7Qrbo\n5XxQhkujTkE6knOHz8CVwYETtj8LZ/bvHIkGMGvRvwsKYDZkIKr5CZ7DX+KcMfPN\neMZU4VCHYSXNxsyp5DJ1Zw+gx8/32kUL0CzJLLam1G021Hq41KPwwSV/KPrOKel7\nHXDLXeECgYEA8MR+lgxGjYTc/k4TdZvcFVgqHGLXnyjO7ZVt4b7UpwmayLuoSD/M\nOpHQYX+JBIIWTNlGhG8UV3DPC3v+auhYa7twwbekS30IYCAmu5GCKgMAcWFinz6A\nYZxG55P/hShetCyOqikgwXqzMlwGs8KEul8f8BKssROzUy8mIlFhjq0CgYEA5hTM\nSNxAD3dlRtb0771fBU7fjx8JPfjptP9vP/JVEelkc/ti9nZ5buTC+9cQC/B+YFx7\nc82uCrXV13bGR9iH8xBhwU7JOYJZbgCpwp0F56wIN5Pdk9Eo79Batrw3oGBG4Yvt\nDc2eltxQbHgObc/qygf88j9XqD8aGIvQrc4Jf6sCgYAtxX03M1A6WTbWFau3YRD+\n8crXqKbLOCvWmODR2MB+nOHTJXHBgndl7xCJaIB43e41X9z7Ek7wrJ5/1WuxkUg1\n+uVdvna6byOnepVCdVAkgnuUEmp4UZ6AcAA+yDD8dIdEg2//w1/ZyGTGvx37EJDB\nCZJ9xl8ULuWZe84pGgWM5QKBgQCYVUbYKrNjShrM5z9uh4QlII6V1Oeql2YtBz4i\nKZE3db6jp9pi8hf+WwnZ8g9WyFjz9edqydAkmTXHHYW0ReHlBYCjm0VRhUMuuNOs\n3YfuVpFuMsFuv/oJpXqaKE3wKi5j4OAH1o7ctWuuFWMAQ7vhHZ7UySmBZJ4jiFaW\n7KaPVwKBgE8E0xbSDVGxXbEGwRXxeaOSemEHD9uEnbAyq1p3EBBhBvInWmDiP5vJ\n68IYNZ4SGxXEKDifwrLGHyekt3RK9B2+U03okd1qH7gfBIlxBJivcjhBe2PtK/Qj\n6fBN0fC1UJoE6pseT9cJDaBq2wMRXJGRYtT8fU9PPJcfa23JlKNS\n-----END RSA PRIVATE KEY-----\n'})

TASK [remote/starlingx : Copy templates] *******************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost] => (item=req_starlingx.cnf)

TASK [remote/starlingx : Generate SSL cert] ****************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/starlingx : Copy SSL starlingx certs to server] ***********************************************************************************
changed: [welktxef-931887-rz-le2pts6-021] => (item=starlingx-ca-cert.pem)

TASK [remote/starlingx : Configure starlingx] **************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/starlingx : Remove temporary working directory] ***********************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [Remote Integ] ****************************************************************************************************************************

TASK [remote/integ : Detect applied status of platform-integ-apps application] *****************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/integ : Fail if platform-integ-apps application apply failed] *********************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [Remote Ldap] *****************************************************************************************************************************

TASK [remote/ldap : Create temporary working directory] ****************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/ldap : Copy SSL root certificates] ************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost] => (item={'filename': 'vz_root_ca_cert.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIFpTCCA42gAwIBAgIUa3vZ0YGxO1TQ8NwhiVfQC0JslXgwDQYJKoZIhvcNAQEL\nBQAwWjELMAkGA1UEBhMCVVMxEDAOBgNVBAoMB1Zlcml6b24xEzARBgNVBAsMClZa\nSUFNIFRlc3QxJDAiBgNVBAMMG1Zlcml6b24gTmV0d29yayBSU0EgQ0EgVGVzdDAe\nFw0yMDA2MTUyMTAxMTNaFw0zNTA2MTUyMTAxMTNaMFoxCzAJBgNVBAYTAlVTMRAw\nDgYDVQQKDAdWZXJpem9uMRMwEQYDVQQLDApWWklBTSBUZXN0MSQwIgYDVQQDDBtW\nZXJpem9uIE5ldHdvcmsgUlNBIENBIFRlc3QwggIiMA0GCSqGSIb3DQEBAQUAA4IC\nDwAwggIKAoICAQC8AIrksI57CbIl5uGZ6yqfpQj3aK+N8f1EVHdwK9JFskoipvC8\n7yFTk8tgmO1i0YA5oRGfNxneqCdrXZiWL6Ko8v/iln9vuN+2rK3rgWZPPRJBAsBN\na49L7U6lJjIGxIZtZqmK5h47oiUtwlYVrbZMN2ijuBQ22/eQ9tsFDV28oBuZ3WAR\npSSbj/tubPQYkw3YYOhv/VpEpsd0rkoEt3QCmTVcX2rtblanpXowTV5R0Hy4014n\nT49jrEo40r4mwYoyS835Uv4ENUFA+pXicT9eUot3RSH6rYdx4A/14UtoI9U0ol8M\n62GHpxSASQ2Kc3yQWvxRGTFslTduYM+vVmMLEDDdqcsjYnStPpwdxxmKItmbjxSv\nIwYIndp8A04WkX2iiJCciC3BNxiLamPtYVyB1HHqbGTGirKYuSvwZt337q1OI3WH\nwVn2S4Mj/wqa4iCyGTvFSUnGq34Xkrb9XNwWBok9Tc2XWGAU/mb/xcd1hX74GZbF\nsrZ11aPtym4kMAjU2KQi96GcAH2lnGZYoOja1J4Cs4WYx1uAx74H/m84CrYavVfl\n1ONJVLDfuZaEkSmu+jHQX15pAECNORTuLD06PbWnOEcOi1xmbt/OT3SA3rhD2mb7\n2wxl7oJpV3ap8xGwYmxiFzmInxFJ1axjg8Rimol0mXTKAy6OdNHbCOnAwwIDAQAB\no2MwYTAPBgNVHRMBAf8EBTADAQH/MA4GA1UdDwEB/wQEAwIBBjAfBgNVHSMEGDAW\ngBQleng3lqGBeTrbLVuABoEmUHm1+TAdBgNVHQ4EFgQUJXp4N5ahgXk62y1bgAaB\nJlB5tfkwDQYJKoZIhvcNAQELBQADggIBADQ9jpmVh9nyY7ZQ4s+S9RuSRYn7QsrW\nDePeMzQgh8ZtS8WE65GY5HS61iHNP2Co8Q1lAaBWF4ipq+VZOcQbPLccHzd1kZv4\ns4u0aTzBd9ccidl73FS0DJDQOBbzPSzgsaiGHSMyGzkTeA8z3ntsSqrXXcDUvoRi\nFus/110AwdtNhJLrWveX6btYtHp9Lqe0YtNCy5AaXlrr1yRSckP5BWVtlwD4dzSO\n/dqI3wHS/ncUx9wSQomZ+AmxYW3KtJQKgHzTqHru1x9BBk7Bzfz9FZr6HLLmEitj\nuFoDRd5TNt5LbO0zDQokvY3oqso6Htup/rS7C08mcmnelYE+yXuOc1YrlyGnpBzk\nmy+1VYbOxRRdqKAZRbE72u/h847IVpsOvjR51iksuCAurZdp2+y2zvV8NhWekuNy\nirECRy9cb4YasjRaKi0/TCGPVSICuLyeG2W72liCj/N2VKfjPP9zsOR5XjwCXfRg\n+9xhLy77/gov2NWXx5fzTkhxCrHOxFdLVMn0wQhksDmw6QsXzDIHSpIOypdDfnx9\nCsthx3nhkuHLUaEP22D22dG+vImA9ukj4R/RRI/87jmi9Q8+ehH+NqN0GZZcLjdN\nSLVXpncuwWQFUDPR06wNkkkmBSXWiIYhwqSpU0Pl3er3fD0uWvXuWPm2PzfOmUAE\nUrkzyw9XmLw0\n-----END CERTIFICATE-----\n'})
changed: [welktxef-931887-rz-le2pts6-021 -> localhost] => (item={'filename': 'vz_root_ica_cert.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIFNzCCAx+gAwIBAgIUGLJR/hP48n+vdq2v1hcfspXo/78wDQYJKoZIhvcNAQEL\nBQAwWjELMAkGA1UEBhMCVVMxEDAOBgNVBAoMB1Zlcml6b24xEzARBgNVBAsMClZa\nSUFNIFRlc3QxJDAiBgNVBAMMG1Zlcml6b24gTmV0d29yayBSU0EgQ0EgVGVzdDAe\nFw0yMDEwMjIyMTE0MDNaFw0zMDEwMjIyMTE0MDNaMIGRMQswCQYDVQQGEwJVUzEL\nMAkGA1UECAwCVFgxETAPBgNVBAcMCFdlc3RsYWtlMRAwDgYDVQQKDAdWZXJpem9u\nMR0wGwYDVQQLDBRWZXJpem9uIFNvdXJjaW5nIExMQzExMC8GA1UEAwwoVmVyaXpv\nbiBOZXR3b3JrIFdFTEtUWElCIExBQiAxIDMgUlNBIElDQTCCASIwDQYJKoZIhvcN\nAQEBBQADggEPADCCAQoCggEBANhkGTXOCKEYf5znDDeX3n/DHFPVqazgQsr0/SIG\n4eb1JY5q5Jq3ZhAaZCr9HJuCkwAP/zgYH0llqOvf8AC2Uh+7z1b33IbwxPmJfWCP\nAqSNFkLWWVRdbELapCu408QsrLMW8IrdP6PLiKAepwncfm4T0/6bANqIEmUkpw8Q\nxProeiNwlGbwUll+tELmdCk7vA7hKX3j1kUvS5Z84Z5ivJBWEcUEggmC97TK4aLo\nFVEHbyahze568JVEaM1vY5L4mnRRTl+u5ipaSMxVBsiXzF7eFuKCzqF7wxbDIt2T\nIFEJtwyJDW5bXjyXgiF1d5H/URprUcRV9Qmf2+PXcfwHII8CAwEAAaOBvDCBuTAS\nBgNVHRMBAf8ECDAGAQH/AgEAMA4GA1UdDwEB/wQEAwIBBjAfBgNVHSMEGDAWgBQl\neng3lqGBeTrbLVuABoEmUHm1+TBTBgNVHR8ETDBKMEigRqBEhkJodHRwOi8vc2Vj\ndXJlLnN0YWdpbmcuc2VjdXJpdHljcmVkZW50aWFsaW5nLmNvbS9jcmwvdnpuZXRy\nc2FjYS5jcmwwHQYDVR0OBBYEFP0Z+/vaDLtAoFig1I9ttNKnmzByMA0GCSqGSIb3\nDQEBCwUAA4ICAQBuXVTf9e01HeymHgRcFCwP2N6G6u+vIzY8Bz0zSUZeRDHMZQcS\nNoabDyn5FfGJlw4BqGC591Sp0/unFQDzAg17rDBcrgwajeFeUiFdb9PiAJwHaX9S\nvq/7VmVLCmpeb+a/laXAe6+tkY1kcFrd1+ItRKC6ZGXMsoDkmk5Ndxxgw77estcI\nMiiLQbvpXRygX5wD4/ayazuLms9qITZkOZ1nTLVqq7QrwYCsSoih7hj6sbsfXr19\nGoYWmk8Y7O/d3ttgyHuRH9k/2dQ/xL7avRpMNkPdr7ocJqI46hvx2X6UyOo7IBua\nkSkFbSmPZWIVAidNMBOnvffCQ32tfjT2/xso/a9cdskvxqgLi0MPARU9Nl2Pufsb\nD7l4/sBvz/PiNTKp+Daa9FdyLb9ySidos1uS0c24bUtY1RXXGAVV2qgfyrzvzfye\nSM+w16hMU/yeYiuA1jsPmsnZnuIJj4Nv8ZjjZ0WS53pP5wcghaHkBrqWQNT8meqA\nVElrMBPlYq67T+AXP0B9lf5Sc3QVIio7XKKfqrlcQxY2JGLEyE53JgZGX7dpwU4I\nukLvyHbT4p06oY3qG6+wH8+YIXCNAYtadJ/C5/u9GcLX5NnZrcuduj0inw2/a3Ao\nWgCt6/Pr28BkCvkWdDt9d8Z40qeu1aZdcr157mR+yZGPfBfB2vasrNIEwQ==\n-----END CERTIFICATE-----\n'})
changed: [welktxef-931887-rz-le2pts6-021 -> localhost] => (item={'filename': 'vz_root_ica_key.pem', 'value': '-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA2GQZNc4IoRh/nOcMN5fef8McU9WprOBCyvT9Igbh5vUljmrk\nmrdmEBpkKv0cm4KTAA//OBgfSWWo69/wALZSH7vPVvfchvDE+Yl9YI8CpI0WQtZZ\nVF1sQtqkK7jTxCyssxbwit0/o8uIoB6nCdx+bhPT/psA2ogSZSSnDxDE+uh6I3CU\nZvBSWX60QuZ0KTu8DuEpfePWRS9LlnzhnmK8kFYRxQSCCYL3tMrhougVUQdvJqHN\n7nrwlURozW9jkviadFFOX67mKlpIzFUGyJfMXt4W4oLOoXvDFsMi3ZMgUQm3DIkN\nbltePJeCIXV3kf9RGmtRxFX1CZ/b49dx/AcgjwIDAQABAoIBABSd1NkPfDr8/ouQ\nZ9WUHprFmBlUrgnOhA6aMNPhG/zJNn7PKGClQJAgM5L08pjOY/sJiyNpCPIRQXrX\npyIqPMDRP/vlOZmRrvKnas6cUYAkAQ71JSWokPv9oM6ZmXODXiDh+qEAW2PbrHS0\n9u01mMYcFYKYeghYFoiUaWZCDsJo3v3dgeE9aQ4tB9ksovSmWrpuCY7NKbd7Qrbo\n5XxQhkujTkE6knOHz8CVwYETtj8LZ/bvHIkGMGvRvwsKYDZkIKr5CZ7DX+KcMfPN\neMZU4VCHYSXNxsyp5DJ1Zw+gx8/32kUL0CzJLLam1G021Hq41KPwwSV/KPrOKel7\nHXDLXeECgYEA8MR+lgxGjYTc/k4TdZvcFVgqHGLXnyjO7ZVt4b7UpwmayLuoSD/M\nOpHQYX+JBIIWTNlGhG8UV3DPC3v+auhYa7twwbekS30IYCAmu5GCKgMAcWFinz6A\nYZxG55P/hShetCyOqikgwXqzMlwGs8KEul8f8BKssROzUy8mIlFhjq0CgYEA5hTM\nSNxAD3dlRtb0771fBU7fjx8JPfjptP9vP/JVEelkc/ti9nZ5buTC+9cQC/B+YFx7\nc82uCrXV13bGR9iH8xBhwU7JOYJZbgCpwp0F56wIN5Pdk9Eo79Batrw3oGBG4Yvt\nDc2eltxQbHgObc/qygf88j9XqD8aGIvQrc4Jf6sCgYAtxX03M1A6WTbWFau3YRD+\n8crXqKbLOCvWmODR2MB+nOHTJXHBgndl7xCJaIB43e41X9z7Ek7wrJ5/1WuxkUg1\n+uVdvna6byOnepVCdVAkgnuUEmp4UZ6AcAA+yDD8dIdEg2//w1/ZyGTGvx37EJDB\nCZJ9xl8ULuWZe84pGgWM5QKBgQCYVUbYKrNjShrM5z9uh4QlII6V1Oeql2YtBz4i\nKZE3db6jp9pi8hf+WwnZ8g9WyFjz9edqydAkmTXHHYW0ReHlBYCjm0VRhUMuuNOs\n3YfuVpFuMsFuv/oJpXqaKE3wKi5j4OAH1o7ctWuuFWMAQ7vhHZ7UySmBZJ4jiFaW\n7KaPVwKBgE8E0xbSDVGxXbEGwRXxeaOSemEHD9uEnbAyq1p3EBBhBvInWmDiP5vJ\n68IYNZ4SGxXEKDifwrLGHyekt3RK9B2+U03okd1qH7gfBIlxBJivcjhBe2PtK/Qj\n6fBN0fC1UJoE6pseT9cJDaBq2wMRXJGRYtT8fU9PPJcfa23JlKNS\n-----END RSA PRIVATE KEY-----\n'})

TASK [remote/ldap : Copy templates] ************************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost] => (item={'name': 'req-ldap.cnf', 'mode': '0644'})

TASK [remote/ldap : Generate SSL cert] *********************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/ldap : Copy templates] ************************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021] => (item={'name': 'dex-overrides.yaml', 'mode': '0644'})

TASK [remote/ldap : Copy SSL dex certs to server] **********************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021] => (item=dex-cert.pem)
changed: [welktxef-931887-rz-le2pts6-021] => (item=dex-key.pem)
changed: [welktxef-931887-rz-le2pts6-021] => (item=dex-ca.pem)

TASK [remote/ldap : Copy SSL AD cert to server] ************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021] => (item={'filename': 'ad_ca.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIFpTCCA42gAwIBAgIUa3vZ0YGxO1TQ8NwhiVfQC0JslXgwDQYJKoZIhvcNAQEL\nBQAwWjELMAkGA1UEBhMCVVMxEDAOBgNVBAoMB1Zlcml6b24xEzARBgNVBAsMClZa\nSUFNIFRlc3QxJDAiBgNVBAMMG1Zlcml6b24gTmV0d29yayBSU0EgQ0EgVGVzdDAe\nFw0yMDA2MTUyMTAxMTNaFw0zNTA2MTUyMTAxMTNaMFoxCzAJBgNVBAYTAlVTMRAw\nDgYDVQQKDAdWZXJpem9uMRMwEQYDVQQLDApWWklBTSBUZXN0MSQwIgYDVQQDDBtW\nZXJpem9uIE5ldHdvcmsgUlNBIENBIFRlc3QwggIiMA0GCSqGSIb3DQEBAQUAA4IC\nDwAwggIKAoICAQC8AIrksI57CbIl5uGZ6yqfpQj3aK+N8f1EVHdwK9JFskoipvC8\n7yFTk8tgmO1i0YA5oRGfNxneqCdrXZiWL6Ko8v/iln9vuN+2rK3rgWZPPRJBAsBN\na49L7U6lJjIGxIZtZqmK5h47oiUtwlYVrbZMN2ijuBQ22/eQ9tsFDV28oBuZ3WAR\npSSbj/tubPQYkw3YYOhv/VpEpsd0rkoEt3QCmTVcX2rtblanpXowTV5R0Hy4014n\nT49jrEo40r4mwYoyS835Uv4ENUFA+pXicT9eUot3RSH6rYdx4A/14UtoI9U0ol8M\n62GHpxSASQ2Kc3yQWvxRGTFslTduYM+vVmMLEDDdqcsjYnStPpwdxxmKItmbjxSv\nIwYIndp8A04WkX2iiJCciC3BNxiLamPtYVyB1HHqbGTGirKYuSvwZt337q1OI3WH\nwVn2S4Mj/wqa4iCyGTvFSUnGq34Xkrb9XNwWBok9Tc2XWGAU/mb/xcd1hX74GZbF\nsrZ11aPtym4kMAjU2KQi96GcAH2lnGZYoOja1J4Cs4WYx1uAx74H/m84CrYavVfl\n1ONJVLDfuZaEkSmu+jHQX15pAECNORTuLD06PbWnOEcOi1xmbt/OT3SA3rhD2mb7\n2wxl7oJpV3ap8xGwYmxiFzmInxFJ1axjg8Rimol0mXTKAy6OdNHbCOnAwwIDAQAB\no2MwYTAPBgNVHRMBAf8EBTADAQH/MA4GA1UdDwEB/wQEAwIBBjAfBgNVHSMEGDAW\ngBQleng3lqGBeTrbLVuABoEmUHm1+TAdBgNVHQ4EFgQUJXp4N5ahgXk62y1bgAaB\nJlB5tfkwDQYJKoZIhvcNAQELBQADggIBADQ9jpmVh9nyY7ZQ4s+S9RuSRYn7QsrW\nDePeMzQgh8ZtS8WE65GY5HS61iHNP2Co8Q1lAaBWF4ipq+VZOcQbPLccHzd1kZv4\ns4u0aTzBd9ccidl73FS0DJDQOBbzPSzgsaiGHSMyGzkTeA8z3ntsSqrXXcDUvoRi\nFus/110AwdtNhJLrWveX6btYtHp9Lqe0YtNCy5AaXlrr1yRSckP5BWVtlwD4dzSO\n/dqI3wHS/ncUx9wSQomZ+AmxYW3KtJQKgHzTqHru1x9BBk7Bzfz9FZr6HLLmEitj\nuFoDRd5TNt5LbO0zDQokvY3oqso6Htup/rS7C08mcmnelYE+yXuOc1YrlyGnpBzk\nmy+1VYbOxRRdqKAZRbE72u/h847IVpsOvjR51iksuCAurZdp2+y2zvV8NhWekuNy\nirECRy9cb4YasjRaKi0/TCGPVSICuLyeG2W72liCj/N2VKfjPP9zsOR5XjwCXfRg\n+9xhLy77/gov2NWXx5fzTkhxCrHOxFdLVMn0wQhksDmw6QsXzDIHSpIOypdDfnx9\nCsthx3nhkuHLUaEP22D22dG+vImA9ukj4R/RRI/87jmi9Q8+ehH+NqN0GZZcLjdN\nSLVXpncuwWQFUDPR06wNkkkmBSXWiIYhwqSpU0Pl3er3fD0uWvXuWPm2PzfOmUAE\nUrkzyw9XmLw0\n-----END CERTIFICATE-----\n'})

TASK [remote/ldap : Configure local-dex.tls] ***************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/ldap : Configure generic] *********************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/ldap : Configure wadcert] *********************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/ldap : Configure dex-overrides.yaml] **********************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/ldap : Wait for distributed cloud synchronization] ********************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001]

TASK [remote/ldap : Remove temporary working directory] ****************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/ldap : Detect oidc-auth-apps application in applying state (from a previous attempt)] *********************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/ldap : Fail if oidc-auth-apps application-abort failed] ***************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/ldap : Detect oidc-auth-apps application in apply-failed or aborted state] ********************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/ldap : Fail if oidc-auth-apps application apply failed] ***************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/ldap : Apply oidc-auth-apps application] ******************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/ldap : Detect applied status of oidc-auth-apps application] ***********************************************************************
FAILED - RETRYING: Detect applied status of oidc-auth-apps application (60 retries left).
FAILED - RETRYING: Detect applied status of oidc-auth-apps application (59 retries left).
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/ldap : Fail if oidc-auth-apps application apply failed] ***************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [Remote Metrics Server] *******************************************************************************************************************

TASK [remote/metrics-server : Set facts - 21.05] ***********************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Set facts - 21.12] ***********************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Get software load status] ****************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Noop if the system is NOT at the right caas_version] *************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Print message if system is NOT at the right caas_version] ********************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Detect presence of existing application] *************************************************************************
fatal: [welktxef-931887-rz-le2pts6-021]: FAILED! => {"changed": true, "cmd": ". /etc/platform/openrc\nsystem application-show metrics-server --column status --format value\n", "delta": "0:00:01.987451", "end": "2023-09-15 06:01:01.430743", "msg": "non-zero return code", "rc": 1, "start": "2023-09-15 06:00:59.443292", "stderr": "application not found: metrics-server", "stderr_lines": ["application not found: metrics-server"], "stdout": "", "stdout_lines": []}
...ignoring

TASK [remote/metrics-server : Print message if system already has the appication] **************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Apply again since the previous apply failed or in uploaded state] ************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Wait until apply is in the applied or apply-failed state] ********************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Print message if re-apply succeeds] ******************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Print message if re-apply failed] ********************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Noop if system requires no further action or needs manual investigation] *****************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Upload application] **********************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Wait until application is in the uploaded state] *****************************************************************
FAILED - RETRYING: Wait until application is in the uploaded state (30 retries left).
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Apply application] ***********************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Wait until application is in the applied or apply-failed state] **************************************************
FAILED - RETRYING: Wait until application is in the applied or apply-failed state (90 retries left).
FAILED - RETRYING: Wait until application is in the applied or apply-failed state (89 retries left).
FAILED - RETRYING: Wait until application is in the applied or apply-failed state (88 retries left).
FAILED - RETRYING: Wait until application is in the applied or apply-failed state (87 retries left).
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Apply again since the first apply failed] ************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Wait again until apply is in the applied or apply-failed state] **************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Print message if apply is successful] ****************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "msg": [
        "=======================================================",
        " welktxef-d931887-021: metrics-server install SUCCEEDED! ",
        "======================================================="
    ]
}

TASK [remote/metrics-server : Print message if apply is failure] *******************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [Remote wrap-get-central-version] *********************************************************************************************************

TASK [remote/wrap-get-central-version : Set facts for playbook] ********************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/wrap-get-central-version : Determine central WRA current version] *****************************************************************
fatal: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001]: FAILED! => {"changed": true, "cmd": ". /etc/platform/openrc\nsystem application-show wr-analytics --column app_version --format value\n", "delta": "0:00:01.289062", "end": "2023-09-15 06:02:24.506714", "msg": "non-zero return code", "rc": 1, "start": "2023-09-15 06:02:23.217652", "stderr": "application not found: wr-analytics", "stderr_lines": ["application not found: wr-analytics"], "stdout": "", "stdout_lines": []}
...ignoring

TASK [remote/wrap-get-central-version : Set facts for wra_target_version] **********************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/wrap-get-central-version : debug] *************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "msg": "wra_target_version:"
}

TASK [Remote wrap-2112-2] **********************************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [Remote wrap-2106-2] **********************************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [Remote wrap-6] ***************************************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [Remote fpga-user-image] ******************************************************************************************************************

TASK [remote/fpga-user-image : Set facts for ansible credential - 21.05] ***********************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Set facts for ansible credential - 21.12] ***********************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Get software load status] ***************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Noop if the system is NOT at the right caas_version] ************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Print message if system is NOT at the right caas_version] *******************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Set facts for default fpga_image_file] **************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Set facts for fpga_image_file from host_vars] *******************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Print message if server is not LS3 cascadelake] *****************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "msg": [
        "==================================================================================",
        " Server type ZTS-LS6-pts6 is not LS3 cascadelake, no action will take place! ",
        "=================================================================================="
    ]
}

TASK [remote/fpga-user-image : Register noop because server is not LS3 cascadelake] ************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Check if FPGA update is stuck] **********************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Abort FPGA update] **********************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : include_tasks] **************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Check FPGA update status (HPE-LS3-e910)] ************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Check FPGA update status (ZTS-LS3-trtn)] ************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Noop if the system has been updated] ****************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Print message if the system has been updated] *******************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : In main block] **************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Copy files to host] *********************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021] => (item=20ww43.5-1x2x25G-5GLDPC-v1.6.2-3.0.1-unsigned.bin)

TASK [remote/fpga-user-image : Do system device-image-upload] **********************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : debug - print UUID] *********************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Do system device-image-apply] ***********************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Do system host-device-image-update] *****************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Wait till application completed] ********************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Do system device-image-state-list] ******************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : force an error if image state is not completed] *****************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : include_tasks] **************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [Install DM Monitor] **********************************************************************************************************************

TASK [common/dm-monitor : Install DM Monitor] **************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [common/dm-monitor : Wait for DM Monitor pod created] *************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [common/dm-monitor : Wait for control-plane pods become ready] ****************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [common/dm-monitor : debug] ***************************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "dm_monitor_pod_ready.stdout_lines": [
        "pod/dm-monitor-77fd4b6649-q9wdh condition met"
    ]
}

TASK [Proteus MWIAT - DISABLE] *****************************************************************************************************************

TASK [remote/zt-redfish : Update Attributes at /redfish/v1/Systems/Self/Bios/SD] ***************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/zt-redfish : Update result] *******************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "update_result": {
        "allow": "GET, PUT, PATCH, POST",
        "changed": false,
        "connection": "close",
        "content": "",
        "cookies": {},
        "cookies_string": "",
        "date": "Fri, 15 Sep 2023 06:02:39 GMT",
        "elapsed": 0,
        "failed": false,
        "msg": "OK (unknown bytes)",
        "redirected": false,
        "server": "AMI MegaRAC Redfish Service",
        "status": 204,
        "url": "https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Systems/Self/Bios/SD"
    }
}

TASK [Lock/unlock after MWAIT change] **********************************************************************************************************

TASK [common/lock-unlock : set_fact] ***********************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [common/lock-unlock : include_tasks] ******************************************************************************************************
included: /home/XXXXXX/playbooks/wr-installer/roles/common/lock-unlock/tasks/lock_node.yaml for welktxef-931887-rz-le2pts6-021

TASK [common/lock-unlock : Check subcloud status before locking] *******************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [common/lock-unlock : debug] **************************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "msg": "The host is unlocked, continue with locking."
}

TASK [common/lock-unlock : Lock subcloud] ******************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [common/lock-unlock : Pause for 10 seconds for the command to complete] *******************************************************************
Pausing for 10 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [welktxef-931887-rz-le2pts6-021]

TASK [common/lock-unlock : Wait until subcloud is in locked status] ****************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [common/lock-unlock : Display subcloud status] ********************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "host_status_new.stdout": "locked"
}

TASK [common/lock-unlock : include_tasks] ******************************************************************************************************
included: /home/XXXXXX/playbooks/wr-installer/roles/common/lock-unlock/tasks/unlock_node.yaml for welktxef-931887-rz-le2pts6-021

TASK [common/lock-unlock : Check subcloud status before unlocking] *****************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [common/lock-unlock : Unlock subcloud] ****************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [common/lock-unlock : Wait for node to restart (port 22 goes down)] ***********************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [common/lock-unlock : Wait for node be back up (port 5000 comes up)] **********************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [common/lock-unlock : Obtain Keystone auth token] *****************************************************************************************
FAILED - RETRYING: Obtain Keystone auth token (60 retries left).
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [common/lock-unlock : Wait for contoller-0 enabled] ***************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

PLAY RECAP *************************************************************************************************************************************
welktxef-931887-rz-le2pts6-021 : ok=133  changed=58   unreachable=0    failed=0    skipped=63   rescued=0    ignored=4

[XXXXXX@welktxefnce-h-pe1util-vm01 wr-installer]$ Timeout, server 2607:f160:10:9239:ce:290:0:2000 not responding.

```


### post - deployment automation

```log

[XXXXXX@welktxefnce-h-pe1util-vm01 wrcp_post_deployment]$ ansible-playbook --vault-password-file /tmp/vault-pass -i inventory/ri_1.yaml wrcp_subcloud_post_deployment.yaml

PLAY [Post deployment steps fro WRCP subclouds] ************************************************************************************************

TASK [set vendor as samsung] *******************************************************************************************************************
ok: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : create vdu namespace] ************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]
included: /home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/generic/tasks/create_generic_resources.yaml for welktxef-931887-rz-le0pts6-021

TASK [subclouds/generic : Create working directory] ********************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : Template generic files into workdir] *********************************************************************************
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/generic/templates/samsung/generic/crd-role.yaml.j2)
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/generic/templates/samsung/generic/orchestration_sa_cluster.yaml.j2)
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/generic/templates/samsung/generic/orchestration_sa.yaml.j2)
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/generic/templates/samsung/generic/samsung_debug_sa.yaml.j2)
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/generic/templates/samsung/generic/ss_sa.yaml.j2)

TASK [subclouds/generic : Create generic resources] ********************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]
included: /home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/generic/tasks/create_k8s_files.yaml for welktxef-931887-rz-le0pts6-021

TASK [subclouds/generic : Create working directory] ********************************************************************************************
ok: [welktxef-931887-rz-le0pts6-021 -> localhost]

TASK [subclouds/generic : Get token for Orch - 21.05] ******************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : store orch token] ****************************************************************************************************
ok: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : Get token for SS Debug] **********************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : store ss token] ******************************************************************************************************
ok: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : print orch token] ****************************************************************************************************
ok: [welktxef-931887-rz-le0pts6-021] => {
    "orch_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjNyTzE3eTdhZGRVc2lva3FkdjRjR0xrMHBfMFcyWjlfSHNGdm5XUlBSM1EifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6Im9yY2hlc3RyYXRpb24tc2EtdG9rZW4teGg5ZmsiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoib3JjaGVzdHJhdGlvbi1zYSIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6ImFmYTE3OTkyLTFjYjQtNDJmYi04OGJlLWU4MjNmZDliOGViOSIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpkZWZhdWx0Om9yY2hlc3RyYXRpb24tc2EifQ.eHsiL4R7_PG_hfNdW6UMvCUTLXyeIFIjKd5VYfi6v40KsykMNrIVzo_Yj8lRwYv0HJBcpTgjr7vvh8BqX-JLxSgt_Gb-cdqMcESgbbJoRbjqN1Lwxp5LKPTDMkOcgBgULqplaKgItN0ZicFXKQEXEGI8CST4iyj0XP-aDKV8rFFb-3yaqjwmzCzUUD-pPSq9D_y72Kz76d2o3ijuf77M3g0wGMPKDINPQ3UEXbQpcFn1EiJnKgNL5GrsKbn3fqne9gQMNt_28QEutBZ_s0xBqv2zikdrMspBJQ07iJGM2_p4t5BVUPsYxbIZp4EZbipcpeva69J4G0nQ9wqhIBwMow"
}

TASK [subclouds/generic : print ss token] ******************************************************************************************************
ok: [welktxef-931887-rz-le0pts6-021] => {
    "ss_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjNyTzE3eTdhZGRVc2lva3FkdjRjR0xrMHBfMFcyWjlfSHNGdm5XUlBSM1EifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6InNhbXN1bmctc2EtdG9rZW4tNW1tNGIiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoic2Ftc3VuZy1zYSIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6ImJjMmM5YWU1LWNmNjMtNDYzNy1hYzY5LTI3ZmUxNzgwZThhYiIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpkZWZhdWx0OnNhbXN1bmctc2EifQ.MiKAoi51FPLV2hRt0_7esiUbe9kP88VcXIo0UvOk132bE8ZhzgPLiG4bQNrTclE3UW_zcgOImgr14YbPM4ANRUALHfquzfCU6mAacc3l_e_un_LYxzsC_WuVJuQK7YKAQy0zRlkeNhgZb_bd1KeWetiuGToGElBASP6sbm_uSV_WmP1gXVXorTW5Yp5kqYI2wcvh9VYapTBOcE4rEkXgfEUeO_-pq_aO5yhykXZjh-YfMxRav6aWlK3KrBbR-1n71KkoeqVjQQeWygRYU-cWML21lwsAgVoeBEgS5HCTF82GOi5lSAHytzHlybscrgqbcLq2RXDe9VwBQIgBZQcB_A"
}

TASK [subclouds/generic : Template k8s files into temp dir] ************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021 -> localhost] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/generic/templates/samsung/k8s/kubeconfig-orchestration.conf.j2)
changed: [welktxef-931887-rz-le0pts6-021 -> localhost] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/generic/templates/samsung/k8s/kubeconfig-samsung-debug.conf.j2)
included: /home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/generic/tasks/create_local_registry_secret.yaml for welktxef-931887-rz-le0pts6-021

TASK [subclouds/generic : Create secret in welktxef-931887vzwcvdu-y-ss-ls6-00000000021 for pulling from local registry] ************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : Create alternative secret in welktxef-931887vzwcvdu-y-ss-ls6-00000000021 for pulling from vudorch's own registry] ****
changed: [welktxef-931887-rz-le0pts6-021]
included: /home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/generic/tasks/update_platform_integ_apps.yaml for welktxef-931887-rz-le0pts6-021

TASK [subclouds/generic : Create working directory] ********************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : Template platform integ apps override file into temp dir] ************************************************************
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/generic/tasks/../templates/samsung/platform-integ/rbd-namespaces.yaml.j2)

TASK [subclouds/generic : Update platform integ apps] ******************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]
FAILED - RETRYING: Wait until application is out of the applying state (90 retries left).

TASK [subclouds/generic : Wait until application is out of the applying state] *****************************************************************
changed: [welktxef-931887-rz-le0pts6-021]
included: /home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/generic/tasks/store_ptp_notification_client_image.yaml for welktxef-931887-rz-le0pts6-021

TASK [subclouds/generic : set the correct tag for notificationclient-base image - up to 21.12] *************************************************
ok: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : Log in registry.central] *********************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : Pull ptp notification client image from registry.central] ************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : Log out from registry.central] ***************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : Tag ptp notification client image from registry.central] *************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : Log in registry.local] ***********************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : Push ptp notification client image to registry.local] ****************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : Log out from registry.local] *****************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : Delete image from Docker cache] **************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : create vdu namespace] ***********************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]
included: /home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/tasks/lock_node.yaml for welktxef-931887-rz-le0pts6-021

TASK [subclouds/specific : Check subcloud status before locking] *******************************************************************************
ok: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Lock subcloud] ******************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]
Pausing for 10 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)

TASK [subclouds/specific : Pause for 10 seconds for the command to complete] *******************************************************************
ok: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Wait until subcloud is in locked status] ****************************************************************************
ok: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Display subcloud status] ********************************************************************************************
ok: [welktxef-931887-rz-le0pts6-021] => {
    "subcloud_status.stdout_lines": [
        "+----+--------------+-------------+----------------+-------------+--------------+",
        "| id | hostname     | personality | administrative | operational | availability |",
        "+----+--------------+-------------+----------------+-------------+--------------+",
        "| 1  | controller-0 | controller  | locked         | disabled    | online       |",
        "+----+--------------+-------------+----------------+-------------+--------------+"
    ]
}
included: /home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/tasks/system_configs_ls6.yaml for welktxef-931887-rz-le0pts6-021

TASK [subclouds/specific : Configure CPU] ******************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Configure sriov0] ***************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Configure sriov1] ***************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Configure fh0] ******************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Configure fh1] ******************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Configure fh2] ******************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Configure fh3] ******************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Configure fh4] ******************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Configure fh5] ******************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Configure ptp] ******************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Configure PLM] ******************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]
Pausing for 120 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)

TASK [subclouds/specific : Wait for PLM configuration to complete] *****************************************************************************
ok: [welktxef-931887-rz-le0pts6-021]
included: /home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/tasks/unlock_node.yaml for welktxef-931887-rz-le0pts6-021

TASK [subclouds/specific : Check subcloud status before unlocking] *****************************************************************************
ok: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Unlock subcloud] ****************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Wait for node to restart (port 22 goes down)] ***********************************************************************
ok: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Wait for node be back up (port 5000 comes up)] **********************************************************************
ok: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Obtain Keystone auth token] *****************************************************************************************
ok: [welktxef-931887-rz-le0pts6-021 -> localhost]
FAILED - RETRYING: Wait for contoller-0 enabled (60 retries left).

TASK [subclouds/specific : Wait for contoller-0 enabled] ***************************************************************************************
ok: [welktxef-931887-rz-le0pts6-021 -> localhost]
included: /home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/tasks/create_nads.yaml for welktxef-931887-rz-le0pts6-021

TASK [subclouds/specific : Create working directory] *******************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : set_fact] ***********************************************************************************************************
ok: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Template NAD files into temp dir] ***********************************************************************************
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/templates/samsung/LS6_21D/NAD/adpf-ca-nad.yaml.j2)
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/templates/samsung/LS6_21D/NAD/adpf-f1c-nad.yaml.j2)
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/templates/samsung/LS6_21D/NAD/adpf-f1u-nad.yaml.j2)
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/templates/samsung/LS6_21D/NAD/adpf-fh0-nad.yaml.j2)
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/templates/samsung/LS6_21D/NAD/adpf-fh0m-nad.yaml.j2)
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/templates/samsung/LS6_21D/NAD/adpf-fh1-nad.yaml.j2)
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/templates/samsung/LS6_21D/NAD/adpf-fh1m-nad.yaml.j2)
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/templates/samsung/LS6_21D/NAD/adpf-fh2-nad.yaml.j2)
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/templates/samsung/LS6_21D/NAD/adpf-fh2m-nad.yaml.j2)
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/templates/samsung/LS6_21D/NAD/adpf-fh3-nad.yaml.j2)
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/templates/samsung/LS6_21D/NAD/adpf-fh4-nad.yaml.j2)
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/templates/samsung/LS6_21D/NAD/adpf-fh5-nad.yaml.j2)

TASK [subclouds/specific : Create NADs] ********************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]
included: /home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/tasks/create_rbac.yaml for welktxef-931887-rz-le0pts6-021

TASK [subclouds/specific : Create working directory] *******************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Template RBAC files into temp dir] **********************************************************************************
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/templates/samsung/rbac/rbac_ss_sa_new_install.yaml.j2)

TASK [subclouds/specific : Create RBACs] *******************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]
included: /home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/tasks/install_ptp_notification_app.yaml for welktxef-931887-rz-le0pts6-021

TASK [subclouds/specific : Add necessary labels to the host] ***********************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : set_fact] ***********************************************************************************************************
ok: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Upload ptp-notification app] ****************************************************************************************
fatal: [welktxef-931887-rz-le0pts6-021]: FAILED! => {"changed": true, "cmd": "source /etc/platform/openrc\nset -e\nsystem application-upload /usr/local/share/applications/helm/ptp-notification-21.05-49.tgz\n", "delta": "0:00:01.731680", "end": "2023-09-15 15:39:18.762140", "msg": "non-zero return code", "rc": 1, "start": "2023-09-15 15:39:17.030460", "stderr": "Error: Tar file /usr/local/share/applications/helm/ptp-notification-21.05-49.tgz does not exist", "stderr_lines": ["Error: Tar file /usr/local/share/applications/helm/ptp-notification-21.05-49.tgz does not exist"], "stdout": "", "stdout_lines": []}

PLAY RECAP *************************************************************************************************************************************
welktxef-931887-rz-le0pts6-021 : ok=72   changed=42   unreachable=0    failed=1    skipped=25   rescued=0    ignored=0

[XXXXXX@welktxefnce-h-pe1util-vm01 wrcp_post_deployment]$
```


### Wipe and install again

### Deployment 

```log
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Set facts for wr_release_version] ******************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Print wr_release_version] **************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "msg": "wr_release_version: 21.12"
}

TASK [remote/remote-configure : Set fact wr_distribution_directory to use based on WR version] *************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Set fact wr_distribution_directory to use based on WR version] *************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Set facts for which image list to use based on WR version] *****************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Set facts for which image list to use based on WR version] *****************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Set facts for which image list to use based on WR version] *****************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Print wr_image_list] *******************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "msg": "wr_image_list: /opt/external/vcpfe-team/artifacts/WRCP-2112/wind-river-cloud-platform-container-images-list-21.12.txt"
}

TASK [remote/remote-configure : Set fact to wr_license_key] ************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Set fact to wr_license_key] ************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : print wr_license_key] ******************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "msg": "wr_license_key = IyBXaW5kIFJpdmVyIFByb2R1Y3QgQWN0aXZhdGlvbiBGaWxlIChpbnN0YWxsLnR4dCkKIyBJc3N1ZWQgZm9yIGhvc3Q6IDxWZXJpem9uPiA8VmVyaXpvbj4gPEFueT4KIyBMaWNlbnNlIG51bWJlcihzKTogNjgyMzc0CiMgSXNzdWVkIG9uOiAyNi1qYW4tMjAyMiAwOTo1MDo1MAojCiMgTm90ZTogdGhpcyBsaWNlbnNlIGlzIGdlbmVyYXRlZCBjdW11bGF0aXZlbHkgZm9yIGFsbAojIFdpbmQgUml2ZXIgc29mdHdhcmUgbWFuYWdlZCBieSB0aGlzIGhvc3QuCgojIDEuIEZsZXhMTSBsaWNlbnNlIGZpbGU6CiMgQmVnaW46IFNlcnZlciBsaWNlbnNlICAtLS0tLS0tLS0tLS0tLS0tLS0tLS0KIyBTZXJpYWwgTnVtYmVyOiA2ODQ0NDktVmVyaXpvblBPQy1HNFdEQzlDUEVLCgpQQUNLQUdFIFdSQ1BfQ09OVEFJTkVSX1BLRyB3cnNkIDIxIDAwNDY1REZDRUI5QiBcCglDT01QT05FTlRTPVdSQ1BfQ09OVEFJTkVSOjIxLjEyIE9QVElPTlM9U1VJVEUgXAoJU0lHTj0yNTAwQzhCMjRFRDAKSU5DUkVNRU5UIFdSQ1BfQ09OVEFJTkVSX1BLRyB3cnNkIDIxIHBlcm1hbmVudCB1bmNvdW50ZWQgNDQyRThBMzg2QUE4IFwKCVZFTkRPUl9TVFJJTkc9PGxuPjY4MjM3NDwvbG4+PHBzPjIyMTMtNDM8L3BzPiBIT1NUSUQ9QU5ZIFwKCUlTU1VFRD0yNi1qYW4tMjAyMiBTTj1zZXJpYWwtVmVyaXpvbi1MVjJJV0FVTEVCIFwKCVNUQVJUPTI2LWphbi0yMDIyIFNJR049QjUzNzk2OTBENEE2Cg=="
}

TASK [remote/remote-configure : Copy storage checking script if server is HPE-LS3-e910] ********************************************************
skipping: [welktxef-931887-rz-le2pts6-021] => (item=hpe_storage_check.py)

TASK [remote/remote-configure : Execute storage checking script if server is HPE-LS3-e910] *****************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor HPE HPE-LS3-e910 (4 disks)] *****************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor HPE HPE-LS3-e910 (2 disks)] *****************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor HPE HPE-LS3-92s3] ***************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor HPE HPE-LS6-92s6] ***************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor ZTS ZTS-LS3-trtn] ***************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Set facts for Corning] *****************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor ZTS ZTS-LS6-pts6 & ZTS-LS3-pts3] ************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor ZTS ZTS-LS6-aks6 & ZTS-LS3-aks3] ************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : set_fact] ******************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [include_role : remote/zt-redfish] ********************************************************************************************************

TASK [remote/zt-redfish : get content from /redfish/v1/Systems/Self] ***************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/zt-redfish : Extract and store BiosVersion from returned content] *****************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Set facts for BIOS version based on vendor ZTS ZTS-LS6-pts6 & ZTS-LS3-pts3] ************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : debug] *********************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "bios_version": "0.23"
}

TASK [remote/remote-configure : Find out which DM Docker version contral has] ******************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001]

TASK [remote/remote-configure : Find out which DM file version contral has] ********************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001]

TASK [remote/remote-configure : Print dm docker version and dm file version] *******************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "msg": "dm_docker_version: WRCP_21.12-wrs.4, dm_file: wind-river-cloud-platform-deployment-manager-2.0.8-4.tgz"
}

TASK [remote/remote-configure : Discover Wind River docker image names] ************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-configure : Print local_images_full] ***************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "msg": "docker.io/starlingx/ceph-config-helper:v1.15.0\ndocker.io/starlingx/dex:stx.4.0-v2.14.0-1\ndocker.io/starlingx/n3000-opae:stx.6.0-v1.0.1\ndocker.io/starlingx/stx-oidc-client:stx.5.0-v1.0.4\ndocker.io/wind-river/cloud-platform-deployment-manager:WRCP_21.12-wrs.4\ngcr.io/google_containers/kubernetes-dashboard-init-amd64:v1.0.0\ngcr.io/kubebuilder/kube-rbac-proxy:v0.4.0\nquay.io/external_storage/rbd-provisioner:v2.1.1-k8s1.11"
}

TASK [remote/remote-configure : Create fact for Wind River docker image names] *****************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Determine DM Helm Chart path] **********************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-configure : Print dm_helm_chart] *******************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "msg": "/opt/external/vcpfe-team/artifacts/WRCP-2112/wind-river-cloud-platform-deployment-manager-2.0.8-4.tgz"
}

TASK [remote/remote-configure : Set DM Helm Chart file] ****************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Lookup Deployment Manager image tag] ***************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-configure : Lookup RBAC Proxy image tag] ***********************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-configure : Copy WRCP DM Playbook] *****************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001] => (item=wind-river-cloud-platform-deployment-manager.yaml)
ok: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001] => (item=wind-river-cloud-platform-deployment-manager-2.0.8-4.tgz)

TASK [remote/remote-configure : Set a fact for the central controller VIP address] *************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-configure : Configure WRCP seed template] **********************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001] => (item={'src': 'bootstrap-values.yaml', 'dest': 'welktxef-d931887-021-bootstrap-values.yaml'})
ok: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001] => (item={'src': 'deploy-values.yaml', 'dest': 'welktxef-d931887-021-deploy-values.yaml'})
ok: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001] => (item={'src': 'deploy-standard.yaml', 'dest': 'welktxef-d931887-021-deploy-standard.yaml'})
ok: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001] => (item={'src': 'install-values.yaml', 'dest': 'welktxef-d931887-021-install-values.yaml'})

TASK [remote/remote-configure : Copy SSL cert files] *******************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001] => (item={'filename': 'k8s_root_ca_cert.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIF8jCCA9qgAwIBAgIJAIf9Ql2uDZh+MA0GCSqGSIb3DQEBDQUAMIGFMQswCQYD\nVQQGEwJVUzEOMAwGA1UECAwFVGV4YXMxETAPBgNVBAcMCFdlc3RsYWtlMR0wGwYD\nVQQKDBRWZXJpem9uIFNvdXJjaW5nIExMQzE0MDIGA1UEAwwrVmVyaXpvbiBOZXR3\nb3JrIFdFTEtUWElCIExBQiAxIDMgUlNBIEs4UyBDQTAeFw0yMDEwMjUyMjEyNDha\nFw0zMDEwMjMyMjEyNDhaMIGFMQswCQYDVQQGEwJVUzEOMAwGA1UECAwFVGV4YXMx\nETAPBgNVBAcMCFdlc3RsYWtlMR0wGwYDVQQKDBRWZXJpem9uIFNvdXJjaW5nIExM\nQzE0MDIGA1UEAwwrVmVyaXpvbiBOZXR3b3JrIFdFTEtUWElCIExBQiAxIDMgUlNB\nIEs4UyBDQTCCAiIwDQYJKoZIhvcNAQEBBQADggIPADCCAgoCggIBAKyF9svdv/qG\n7HxBr1DWvZ3CQiDsA4m1kj0hD7jo3B3W/32ODcPpgeNmp4Oful0SsndpqEGhXDq5\noiBfqszMUpzDgdQ7siIHekb2olFEK2KniMP3H53nilIppeyMby5K3ZwF0Qbmk5WK\ncoXoYegP+Uv9bV0AMH6Dn4CVgYrLAYfmPyGgUSt4vuZ9F/rf9UkBf/DcZGqMnMax\n/Gfaq8KwmDzD9D8IVCHPrM5f4+CaKMQCFu5QkSsLYJFRiuQWWaICMMdnqpb0HZh5\niPnCSHwPPUyXxtujdI97Ovy4X5WR46jJ2+KzPYe8tVa/DL3TlKmRL9AF+oSE17bw\nzGAE7GNWxPojebHIUuoKdOQC1qiJBVS+c14r9+9P2Uy6XEhNUs+h3juRI4U3YkQ1\nUCUU3opqhOPh4jUIuPGg5aX07lt4Wpxc48D+CY1D4i6vaJLl3WCsVK7PFwWVQQEW\nIQabfuj1R2jEu7pp2Yabza58S00v1P5/kv/DNr7ADm8eYRvxLAAXCedMeSDXKBgd\npPmVXXZoZ8+X8VRGYxcw0mBBLIAiTOntT2vgLeq5T3QyiVKdU6TLAYEjS65QZ3Eg\naIX0wRqlcQI7lruTXubtENG6wWXYtnDf5795ZID1YIEqkgzZLMBqq1SBiLnWd6aK\n78Zsr4j5GmTBGpKRmwE2oO1btJCCYyG5AgMBAAGjYzBhMA8GA1UdEwEB/wQFMAMB\nAf8wHQYDVR0OBBYEFEDQ5EaGp3x02WUuvqetygqpM3dCMB8GA1UdIwQYMBaAFEDQ\n5EaGp3x02WUuvqetygqpM3dCMA4GA1UdDwEB/wQEAwICpDANBgkqhkiG9w0BAQ0F\nAAOCAgEAeCMxVJr5Jyg87DVaUtEhiWfhto993ENrnevAGqrBOoRc/KU1/C3paqhR\nsvr2r2LR+npSmeo6iz0FaO31XwHSHX95+XJeGP5Q8TGddbRiTglQsMfOkGNzxqgg\nTkdZ8A1y9v2jprONUmLADVGIVT0AoHc7V9w1I8NKhrY+rIllum4FRDiDPSnImh5h\nxmH+Nq2ZuEFVdtV/oNKzEu2ywmbgBRd5Jv3rTejxltmTZtyq8IKoKguj3NVFn93Q\nU4TbsxkcAdrLMooLYYDRTWA4t0iqKM/UkYUg4xl2l9NrY7ZUbaNd5+YsLNdqXO/c\nmp7wyMv/8ZIy1BLG4zJmX/JzWkYmULqQ+A+21+YuqrV3a81V7vcHhJcRaPOrg5cd\nYwY2eCbXMvNOdrzppIglUrlddNuqAhs1MTi/VibxYuI9isU0JckXIcCy1L+xbEda\n6v/z6wSrScVz0I4m0DpK6xMQ8t9sLcrGp5uGbj6J4nQWd+QLdq6kmAzDOZ/Gs0wb\nPYdkER4dXAVcioYFekpKv7d+nur0FPtMNIw0OdhX2eAwC22IFAq2DZRjUFvaBGaD\ni1ptfq6P1mVJ2T/exYujEDtq+8yQTfWgFm/DjEfWtcCp0Jukgv8opLR2DpCf5Ucq\nd5X7d/DP0mukJ3vZ8EIqYorwZJ1L1a2jgngjA+gPxIaW+JHfTHU=\n-----END CERTIFICATE-----\n'})
ok: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001] => (item={'filename': 'k8s_root_ca_key.pem', 'value': '-----BEGIN PRIVATE KEY-----\nMIIJQQIBADANBgkqhkiG9w0BAQEFAASCCSswggknAgEAAoICAQCshfbL3b/6hux8\nQa9Q1r2dwkIg7AOJtZI9IQ+46Nwd1v99jg3D6YHjZqeDn7pdErJ3aahBoVw6uaIg\nX6rMzFKcw4HUO7IiB3pG9qJRRCtip4jD9x+d54pSKaXsjG8uSt2cBdEG5pOVinKF\n6GHoD/lL/W1dADB+g5+AlYGKywGH5j8hoFEreL7mfRf63/VJAX/w3GRqjJzGsfxn\n2qvCsJg8w/Q/CFQhz6zOX+PgmijEAhbuUJErC2CRUYrkFlmiAjDHZ6qW9B2YeYj5\nwkh8Dz1Ml8bbo3SPezr8uF+VkeOoydvisz2HvLVWvwy905SpkS/QBfqEhNe28Mxg\nBOxjVsT6I3mxyFLqCnTkAtaoiQVUvnNeK/fvT9lMulxITVLPod47kSOFN2JENVAl\nFN6KaoTj4eI1CLjxoOWl9O5beFqcXOPA/gmNQ+Iur2iS5d1grFSuzxcFlUEBFiEG\nm37o9UdoxLu6admGm82ufEtNL9T+f5L/wza+wA5vHmEb8SwAFwnnTHkg1ygYHaT5\nlV12aGfPl/FURmMXMNJgQSyAIkzp7U9r4C3quU90MolSnVOkywGBI0uuUGdxIGiF\n9MEapXECO5a7k17m7RDRusFl2LZw3+e/eWSA9WCBKpIM2SzAaqtUgYi51nemiu/G\nbK+I+RpkwRqSkZsBNqDtW7SQgmMhuQIDAQABAoICACysO62qa+2pRk8eixD5qfvR\ns2Hm+zuLYqSljPaqhWTMqTePswzJyDJkAHhawd0b3E6Dc2gbKlCihNKxMv744WNq\nVJHqK0QYf5ckgf9dEYboLsffk7ZFoFGKK0bHTnrENAIUl32b8xdD1EfMVp3KlRkS\nNGFijSwVVRXsoLCZxHm2Kx6/7oS9LWFtfuodV9xhoQlzaCUW5/mjWOJjgxpUs/b4\nHqS7uV1P80U1G0KraGboy5tGDXEB7y1x2e8Zwnfq7UqVE10nNQqoXcmefzpwj8Tn\ngDybZLFKjYmnDEkkj7jDHEbldsdRG/usWNZGlTYbPDA3fBkYdOsQCzvJypQmgbZ+\n3yk3Lj2+9vLEMfPrruuzyOSXgki6o5uvy7Je6PdBpsz75k8FH6a+Rw3vvP8HuP3S\nLSUYm3tyOheXHR7BKN4bnfi11RAWvDpT9S+QnZ+R8DmQzOADlnjRC8WewDJYoNJ1\np1jeuqswlxo144oMO92cmdS2dAbPvS6aQP1I85Q2NniY+6YhHkBwIQIlfVs1JPbY\nX7QtTy1IXQhR3sospyvUwY2GPSAeVHDRL53ClQKDsvWpSy0MAmWYJkZu1P+jKBim\nj34ytApgG65Hv/RHf3L4+4zzItZ3TN2tJ/g9EKc6oMNtqKbbG56kkmvRPWKtMGV8\nFqxCvG5NydUK7fN+P2WJAoIBAQDXLFC//Fn9ed1U+pKa2M25aJwEetkGLXQvkwVi\n8uJFaXITb2ceveSEo6iBExyn4eYL5A4X+RZdJJdRRbj4whsNN13Pm+6lYX3pp7MN\nO+78uvwVfKZiWPFKfZs7ZH1/O9VIlLGnXUHeaHK1tmv9ixxMixdnjUDkcVa0O3qT\nKBLpvXnVEMYizxQBN0P5Z9QvQQGpUhKnNw+FhV1SP+YHxrB0Pu6qbYAmZZC2MQc1\nTsDyqGjmHk9VJaFYAAPEjqACDbfnkVUCj0ylM4xPQuBJs9DOKh4InG+znusdmd8H\nmvoEFDppsrH1NhO6GTeuCk6n0WBi6cUm76K/gPscYyV4ZtkfAoIBAQDNQgDXtfqv\nxbAhvDk0o/P8fqOdgQF0uFTqYHmyW31Ty9nF0ptA8LVJOIljU3zlLplhIFjBnSEG\nLqu4jnLLRR+zej0MXmJuZ9BMWmQeTrZzttnH5bn54E07DPJ5BvFoTMJNklBiXjB5\n5hTPZS4yK1KjoxY+Ypnj4W1iZjP37ya/A34J2nlYtoW4LdVfJHqCxBXel9Nz2zkv\nvwwPu8Eu7gFLuhNQM6Iv4mORGI8yg7Y/BwodfDPRuFvrG1KXkjwASb0O5b1suRQy\n9H80q5EAbT36K1z48ilr8fcroN+hV8g4yntrBBgOHPMmBk/vHKU8B1rkBr0p2haI\n3PwKmDFRsDInAoIBAGrjjMmSZnHQk+6e+y0I/klYegiPrjevZMQtWMOqvFSW6SBW\nevd+hYKOeiqEf/u18D1/8LBgAIgMoU6yQAzy/9U059k2MPrez1m/AOdWGoZZrNhP\nr6ezX0oN04tRhDYsVutTUl09qnb9k95I3KR68nfjsKC0PsQ8uUGXOnDXu215vofl\naUfpbpqcBZxjw7glptmh97oxU/iUI6O0MmUygn18tbrb4okwcw7OlDIbCSaCGnoW\nHHrD0r6QY07FOx9KCU1zmLNI1F5MmSrWoex68wM3UOweKi8khs+RnIV+qyxTkCDp\nsBWL44jS9iHy5Nfg3uzEDDgnWsWfIR8c8YQ6MykCggEADr0ollTI9Yo6hZGggfkr\n8fueABddZWY/Ir1ev8H2E+hVcPEYmOcv/VwD8Y/zLfnUpbbO6MhBsNH1HsGL2LDT\n/+1NKPA2HTtzJ6ht/Acm7tQ4ezQx0JGcuhrJ5orrFtQ8N5nED+w3iulMoT/gu1WF\nD58MX9pwtn5ffmtcW/deTuUPTeHUSNyCaaFQ6w4RhgZSk7NPSch6KMWNNiwDST1p\n9mgcLuwmP04AXFDpJ3VxxsDYpxleFzcn0pAZtCyaBmNFIia5HW+E1cvcvol7Vg6C\nHs6yVGX/N3MejpF0vX8yL3HKvvqCR7EofJiDcOYbr13P1wPs3W59o8JKjvAyymze\njQKCAQAUY/0asRL33D7tFoIbLg/N9hi+tCCM35DMf2FeXm3QwSkAR/BJw0ewCE5C\n+VqukHN3/i0Xe8KSHwEuLK2sGLk9Ys8A5NytjqFApYwpIk8UrRONfC12H3ez5VYk\nJlhMVhVXEZvVhEFJiBC7q6x6s7BVtLTGV7FA5CW8YKBhwHwrpm+h/Xb798oaKyel\nP/xYq+GZzfWfbvUjZvgN0J0RGxKA+GRgsmhoyOfgCVXgSzuUkI+9cAUvC0OV407L\n4XIK0GDJ7Tv/2USSPfmueyGEmacc/oYUPVBUgeINSoaCM4cpZwyLylVEtKOdQoEE\n77G5mvQsoXxsMjd+nbHil450UHsL\n-----END PRIVATE KEY-----\n'})

TASK [Proteus MWIAT - ENABLE] ******************************************************************************************************************

TASK [remote/zt-redfish : Update Attributes at /redfish/v1/Systems/Self/Bios/SD] ***************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/zt-redfish : Update result] *******************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "update_result": {
        "allow": "GET, PUT, PATCH, POST",
        "changed": false,
        "connection": "close",
        "content": "",
        "cookies": {},
        "cookies_string": "",
        "date": "Fri, 15 Sep 2023 16:24:34 GMT",
        "elapsed": 0,
        "failed": false,
        "msg": "OK (unknown bytes)",
        "redirected": false,
        "server": "AMI MegaRAC Redfish Service",
        "status": 204,
        "url": "https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Systems/Self/Bios/SD"
    }
}

TASK [Remote Install] **************************************************************************************************************************

TASK [remote/remote-install : Check if the subcloud deployed but failed] ***********************************************************************
fatal: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001]: FAILED! => {"changed": true, "cmd": ". /etc/platform/openrc\ndcmanager subcloud show welktxef-d931887-021 --column \"deploy_status\" --format value\n", "delta": "0:00:01.219450", "end": "2023-09-15 16:24:37.517882", "msg": "non-zero return code", "rc": 1, "start": "2023-09-15 16:24:36.298432", "stderr": "ERROR (app) Subcloud not found", "stderr_lines": ["ERROR (app) Subcloud not found"], "stdout": "", "stdout_lines": []}
...ignoring

TASK [remote/remote-install : debug] ***********************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "msg": "subcloud_status:"
}

TASK [remote/remote-install : Delete the subcloud that's 'install-failed' & 'pre-install-failed'] **********************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-install : Deploy remote cloud] *********************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001]

TASK [remote/remote-install : 1st polling prep: Obtain Keystone auth token] ********************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-install : 1st polling: Wait for subcloud to start installing OS] ***********************************************************
FAILED - RETRYING: 1st polling: Wait for subcloud to start installing OS (40 retries left).
FAILED - RETRYING: 1st polling: Wait for subcloud to start installing OS (39 retries left).
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-install : 1st polling result: Fail if the installation failed] *************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-install : 2nd polling prep: Obtain Keystone auth token] ********************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-install : 2nd polling: Wait for subcloud to install OS (this will take a while)] *******************************************
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (100 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (99 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (98 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (97 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (96 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (95 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (94 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (93 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (92 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (91 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (90 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (89 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (88 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (87 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (86 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (85 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (84 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (83 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (82 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (81 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (80 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (79 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (78 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (77 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (76 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (75 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (74 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (73 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (72 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (71 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (70 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (69 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (68 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (67 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (66 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (65 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (64 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (63 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (62 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (61 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (60 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (59 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (58 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (57 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (56 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (55 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (54 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (53 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (52 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (51 retries left).
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-install : 2nd polling result: Fail if any error occurred] ******************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-install : 3rd polling prep: Obtain Keystone auth token] ********************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-install : 3rd polling: Wait for subcloud to install OS (this may take a while)] ********************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-install : 3rd polling result: Fail if any error occurred] ******************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-install : 4th polling prep: Obtain Keystone auth token] ********************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-install : 4th polling: Wait for subcloud to install OS (this may still take a while)] **************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-install : 4th polling result: Fail if the installation failed] *************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-install : 5th polling prep: Obtain Keystone auth token] ********************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-install : 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while)] *************************
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (100 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (99 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (98 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (97 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (96 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (95 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (94 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (93 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (92 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (91 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (90 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (89 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (88 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (87 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (86 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (85 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (84 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (83 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (82 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (81 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (80 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (79 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (78 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (77 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (76 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (75 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (74 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (73 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (72 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (71 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (70 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (69 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (68 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (67 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (66 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (65 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (64 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (63 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (62 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (61 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (60 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (59 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (58 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (57 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (56 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (55 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (54 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (53 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (52 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (51 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (50 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (49 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (48 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (47 retries left).
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-install : 5th polling result: Fail if bootstrap/deploy failed] *************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-install : 6th polling prep: Obtain Keystone auth token] ********************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-install : 6th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while)] *************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-install : 6th polling result: Fail if bootstrap/deploy failed] *************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/remote-install : Wait for controller-0 restart] ***********************************************************************************
FAILED - RETRYING: Wait for controller-0 restart (40 retries left).
FAILED - RETRYING: Wait for controller-0 restart (39 retries left).
FAILED - RETRYING: Wait for controller-0 restart (38 retries left).
fatal: [welktxef-931887-rz-le2pts6-021]: FAILED! => {"attempts": 4, "changed": false, "elapsed": 5, "msg": "timed out waiting for ping module test success: Failed to connect to the host via ssh: ssh: connect to host 2607:f160:10:9249:ce:40a:0:f409 port 22: Connection refused"}
...ignoring

TASK [remote/remote-install : Wait for controller-0 recovery] **********************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/remote-install : setup kdump] *****************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [Remote Cleanup] **************************************************************************************************************************

TASK [common/cleanup : Remove temporary working directory] *************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [Remote Manage] ***************************************************************************************************************************

TASK [remote/manage : 1st Obtain Keystone auth token] ******************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/manage : 1st Wait for contoller-0 availability status online] *********************************************************************
FAILED - RETRYING: 1st Wait for contoller-0 availability status online (100 retries left).
FAILED - RETRYING: 1st Wait for contoller-0 availability status online (99 retries left).
FAILED - RETRYING: 1st Wait for contoller-0 availability status online (98 retries left).
FAILED - RETRYING: 1st Wait for contoller-0 availability status online (97 retries left).
FAILED - RETRYING: 1st Wait for contoller-0 availability status online (96 retries left).
FAILED - RETRYING: 1st Wait for contoller-0 availability status online (95 retries left).
FAILED - RETRYING: 1st Wait for contoller-0 availability status online (94 retries left).
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/manage : 2nd Obtain Keystone auth token] ******************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/manage : 2nd Wait for contoller-0 availability status online] *********************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/manage : Wait for system to stabilize before running kubectl] *********************************************************************
Pausing for 480 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [welktxef-931887-rz-le2pts6-021]

TASK [Wait for distributed cloud to be reconciled] *********************************************************************************************

TASK [common/wait_for_reconciliation : Making sure node is reachable] **************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [common/wait_for_reconciliation : Wait for K8s API to be up] ******************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [common/wait_for_reconciliation : Wait for hosts to be reconciled] ************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [common/wait_for_reconciliation : Wait for systems to be reconciled] **********************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/manage : Wait for distributed cloud to be reconciled but subcloud OAM VIP becomes unreachable] ************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/manage : Check if the subcloud deployed but failed] *******************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001]

TASK [remote/manage : Set distributed cloud state to managed] **********************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001]

TASK [remote/manage : Wait for system to stabilize] ********************************************************************************************
Pausing for 300 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [welktxef-931887-rz-le2pts6-021]

TASK [Remote Trust] ****************************************************************************************************************************

TASK [remote/trust : Create temporary working directory] ***************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/trust : Copy SSL cert files to working dir] ***************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost] => (item={'filename': 'k8s_root_ca_cert.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIF8jCCA9qgAwIBAgIJAIf9Ql2uDZh+MA0GCSqGSIb3DQEBDQUAMIGFMQswCQYD\nVQQGEwJVUzEOMAwGA1UECAwFVGV4YXMxETAPBgNVBAcMCFdlc3RsYWtlMR0wGwYD\nVQQKDBRWZXJpem9uIFNvdXJjaW5nIExMQzE0MDIGA1UEAwwrVmVyaXpvbiBOZXR3\nb3JrIFdFTEtUWElCIExBQiAxIDMgUlNBIEs4UyBDQTAeFw0yMDEwMjUyMjEyNDha\nFw0zMDEwMjMyMjEyNDhaMIGFMQswCQYDVQQGEwJVUzEOMAwGA1UECAwFVGV4YXMx\nETAPBgNVBAcMCFdlc3RsYWtlMR0wGwYDVQQKDBRWZXJpem9uIFNvdXJjaW5nIExM\nQzE0MDIGA1UEAwwrVmVyaXpvbiBOZXR3b3JrIFdFTEtUWElCIExBQiAxIDMgUlNB\nIEs4UyBDQTCCAiIwDQYJKoZIhvcNAQEBBQADggIPADCCAgoCggIBAKyF9svdv/qG\n7HxBr1DWvZ3CQiDsA4m1kj0hD7jo3B3W/32ODcPpgeNmp4Oful0SsndpqEGhXDq5\noiBfqszMUpzDgdQ7siIHekb2olFEK2KniMP3H53nilIppeyMby5K3ZwF0Qbmk5WK\ncoXoYegP+Uv9bV0AMH6Dn4CVgYrLAYfmPyGgUSt4vuZ9F/rf9UkBf/DcZGqMnMax\n/Gfaq8KwmDzD9D8IVCHPrM5f4+CaKMQCFu5QkSsLYJFRiuQWWaICMMdnqpb0HZh5\niPnCSHwPPUyXxtujdI97Ovy4X5WR46jJ2+KzPYe8tVa/DL3TlKmRL9AF+oSE17bw\nzGAE7GNWxPojebHIUuoKdOQC1qiJBVS+c14r9+9P2Uy6XEhNUs+h3juRI4U3YkQ1\nUCUU3opqhOPh4jUIuPGg5aX07lt4Wpxc48D+CY1D4i6vaJLl3WCsVK7PFwWVQQEW\nIQabfuj1R2jEu7pp2Yabza58S00v1P5/kv/DNr7ADm8eYRvxLAAXCedMeSDXKBgd\npPmVXXZoZ8+X8VRGYxcw0mBBLIAiTOntT2vgLeq5T3QyiVKdU6TLAYEjS65QZ3Eg\naIX0wRqlcQI7lruTXubtENG6wWXYtnDf5795ZID1YIEqkgzZLMBqq1SBiLnWd6aK\n78Zsr4j5GmTBGpKRmwE2oO1btJCCYyG5AgMBAAGjYzBhMA8GA1UdEwEB/wQFMAMB\nAf8wHQYDVR0OBBYEFEDQ5EaGp3x02WUuvqetygqpM3dCMB8GA1UdIwQYMBaAFEDQ\n5EaGp3x02WUuvqetygqpM3dCMA4GA1UdDwEB/wQEAwICpDANBgkqhkiG9w0BAQ0F\nAAOCAgEAeCMxVJr5Jyg87DVaUtEhiWfhto993ENrnevAGqrBOoRc/KU1/C3paqhR\nsvr2r2LR+npSmeo6iz0FaO31XwHSHX95+XJeGP5Q8TGddbRiTglQsMfOkGNzxqgg\nTkdZ8A1y9v2jprONUmLADVGIVT0AoHc7V9w1I8NKhrY+rIllum4FRDiDPSnImh5h\nxmH+Nq2ZuEFVdtV/oNKzEu2ywmbgBRd5Jv3rTejxltmTZtyq8IKoKguj3NVFn93Q\nU4TbsxkcAdrLMooLYYDRTWA4t0iqKM/UkYUg4xl2l9NrY7ZUbaNd5+YsLNdqXO/c\nmp7wyMv/8ZIy1BLG4zJmX/JzWkYmULqQ+A+21+YuqrV3a81V7vcHhJcRaPOrg5cd\nYwY2eCbXMvNOdrzppIglUrlddNuqAhs1MTi/VibxYuI9isU0JckXIcCy1L+xbEda\n6v/z6wSrScVz0I4m0DpK6xMQ8t9sLcrGp5uGbj6J4nQWd+QLdq6kmAzDOZ/Gs0wb\nPYdkER4dXAVcioYFekpKv7d+nur0FPtMNIw0OdhX2eAwC22IFAq2DZRjUFvaBGaD\ni1ptfq6P1mVJ2T/exYujEDtq+8yQTfWgFm/DjEfWtcCp0Jukgv8opLR2DpCf5Ucq\nd5X7d/DP0mukJ3vZ8EIqYorwZJ1L1a2jgngjA+gPxIaW+JHfTHU=\n-----END CERTIFICATE-----\n'})
changed: [welktxef-931887-rz-le2pts6-021 -> localhost] => (item={'filename': 'vz_root_ca_cert.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIFpTCCA42gAwIBAgIUa3vZ0YGxO1TQ8NwhiVfQC0JslXgwDQYJKoZIhvcNAQEL\nBQAwWjELMAkGA1UEBhMCVVMxEDAOBgNVBAoMB1Zlcml6b24xEzARBgNVBAsMClZa\nSUFNIFRlc3QxJDAiBgNVBAMMG1Zlcml6b24gTmV0d29yayBSU0EgQ0EgVGVzdDAe\nFw0yMDA2MTUyMTAxMTNaFw0zNTA2MTUyMTAxMTNaMFoxCzAJBgNVBAYTAlVTMRAw\nDgYDVQQKDAdWZXJpem9uMRMwEQYDVQQLDApWWklBTSBUZXN0MSQwIgYDVQQDDBtW\nZXJpem9uIE5ldHdvcmsgUlNBIENBIFRlc3QwggIiMA0GCSqGSIb3DQEBAQUAA4IC\nDwAwggIKAoICAQC8AIrksI57CbIl5uGZ6yqfpQj3aK+N8f1EVHdwK9JFskoipvC8\n7yFTk8tgmO1i0YA5oRGfNxneqCdrXZiWL6Ko8v/iln9vuN+2rK3rgWZPPRJBAsBN\na49L7U6lJjIGxIZtZqmK5h47oiUtwlYVrbZMN2ijuBQ22/eQ9tsFDV28oBuZ3WAR\npSSbj/tubPQYkw3YYOhv/VpEpsd0rkoEt3QCmTVcX2rtblanpXowTV5R0Hy4014n\nT49jrEo40r4mwYoyS835Uv4ENUFA+pXicT9eUot3RSH6rYdx4A/14UtoI9U0ol8M\n62GHpxSASQ2Kc3yQWvxRGTFslTduYM+vVmMLEDDdqcsjYnStPpwdxxmKItmbjxSv\nIwYIndp8A04WkX2iiJCciC3BNxiLamPtYVyB1HHqbGTGirKYuSvwZt337q1OI3WH\nwVn2S4Mj/wqa4iCyGTvFSUnGq34Xkrb9XNwWBok9Tc2XWGAU/mb/xcd1hX74GZbF\nsrZ11aPtym4kMAjU2KQi96GcAH2lnGZYoOja1J4Cs4WYx1uAx74H/m84CrYavVfl\n1ONJVLDfuZaEkSmu+jHQX15pAECNORTuLD06PbWnOEcOi1xmbt/OT3SA3rhD2mb7\n2wxl7oJpV3ap8xGwYmxiFzmInxFJ1axjg8Rimol0mXTKAy6OdNHbCOnAwwIDAQAB\no2MwYTAPBgNVHRMBAf8EBTADAQH/MA4GA1UdDwEB/wQEAwIBBjAfBgNVHSMEGDAW\ngBQleng3lqGBeTrbLVuABoEmUHm1+TAdBgNVHQ4EFgQUJXp4N5ahgXk62y1bgAaB\nJlB5tfkwDQYJKoZIhvcNAQELBQADggIBADQ9jpmVh9nyY7ZQ4s+S9RuSRYn7QsrW\nDePeMzQgh8ZtS8WE65GY5HS61iHNP2Co8Q1lAaBWF4ipq+VZOcQbPLccHzd1kZv4\ns4u0aTzBd9ccidl73FS0DJDQOBbzPSzgsaiGHSMyGzkTeA8z3ntsSqrXXcDUvoRi\nFus/110AwdtNhJLrWveX6btYtHp9Lqe0YtNCy5AaXlrr1yRSckP5BWVtlwD4dzSO\n/dqI3wHS/ncUx9wSQomZ+AmxYW3KtJQKgHzTqHru1x9BBk7Bzfz9FZr6HLLmEitj\nuFoDRd5TNt5LbO0zDQokvY3oqso6Htup/rS7C08mcmnelYE+yXuOc1YrlyGnpBzk\nmy+1VYbOxRRdqKAZRbE72u/h847IVpsOvjR51iksuCAurZdp2+y2zvV8NhWekuNy\nirECRy9cb4YasjRaKi0/TCGPVSICuLyeG2W72liCj/N2VKfjPP9zsOR5XjwCXfRg\n+9xhLy77/gov2NWXx5fzTkhxCrHOxFdLVMn0wQhksDmw6QsXzDIHSpIOypdDfnx9\nCsthx3nhkuHLUaEP22D22dG+vImA9ukj4R/RRI/87jmi9Q8+ehH+NqN0GZZcLjdN\nSLVXpncuwWQFUDPR06wNkkkmBSXWiIYhwqSpU0Pl3er3fD0uWvXuWPm2PzfOmUAE\nUrkzyw9XmLw0\n-----END CERTIFICATE-----\n'})
changed: [welktxef-931887-rz-le2pts6-021 -> localhost] => (item={'filename': 'vz_root_ica_cert.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIFNzCCAx+gAwIBAgIUGLJR/hP48n+vdq2v1hcfspXo/78wDQYJKoZIhvcNAQEL\nBQAwWjELMAkGA1UEBhMCVVMxEDAOBgNVBAoMB1Zlcml6b24xEzARBgNVBAsMClZa\nSUFNIFRlc3QxJDAiBgNVBAMMG1Zlcml6b24gTmV0d29yayBSU0EgQ0EgVGVzdDAe\nFw0yMDEwMjIyMTE0MDNaFw0zMDEwMjIyMTE0MDNaMIGRMQswCQYDVQQGEwJVUzEL\nMAkGA1UECAwCVFgxETAPBgNVBAcMCFdlc3RsYWtlMRAwDgYDVQQKDAdWZXJpem9u\nMR0wGwYDVQQLDBRWZXJpem9uIFNvdXJjaW5nIExMQzExMC8GA1UEAwwoVmVyaXpv\nbiBOZXR3b3JrIFdFTEtUWElCIExBQiAxIDMgUlNBIElDQTCCASIwDQYJKoZIhvcN\nAQEBBQADggEPADCCAQoCggEBANhkGTXOCKEYf5znDDeX3n/DHFPVqazgQsr0/SIG\n4eb1JY5q5Jq3ZhAaZCr9HJuCkwAP/zgYH0llqOvf8AC2Uh+7z1b33IbwxPmJfWCP\nAqSNFkLWWVRdbELapCu408QsrLMW8IrdP6PLiKAepwncfm4T0/6bANqIEmUkpw8Q\nxProeiNwlGbwUll+tELmdCk7vA7hKX3j1kUvS5Z84Z5ivJBWEcUEggmC97TK4aLo\nFVEHbyahze568JVEaM1vY5L4mnRRTl+u5ipaSMxVBsiXzF7eFuKCzqF7wxbDIt2T\nIFEJtwyJDW5bXjyXgiF1d5H/URprUcRV9Qmf2+PXcfwHII8CAwEAAaOBvDCBuTAS\nBgNVHRMBAf8ECDAGAQH/AgEAMA4GA1UdDwEB/wQEAwIBBjAfBgNVHSMEGDAWgBQl\neng3lqGBeTrbLVuABoEmUHm1+TBTBgNVHR8ETDBKMEigRqBEhkJodHRwOi8vc2Vj\ndXJlLnN0YWdpbmcuc2VjdXJpdHljcmVkZW50aWFsaW5nLmNvbS9jcmwvdnpuZXRy\nc2FjYS5jcmwwHQYDVR0OBBYEFP0Z+/vaDLtAoFig1I9ttNKnmzByMA0GCSqGSIb3\nDQEBCwUAA4ICAQBuXVTf9e01HeymHgRcFCwP2N6G6u+vIzY8Bz0zSUZeRDHMZQcS\nNoabDyn5FfGJlw4BqGC591Sp0/unFQDzAg17rDBcrgwajeFeUiFdb9PiAJwHaX9S\nvq/7VmVLCmpeb+a/laXAe6+tkY1kcFrd1+ItRKC6ZGXMsoDkmk5Ndxxgw77estcI\nMiiLQbvpXRygX5wD4/ayazuLms9qITZkOZ1nTLVqq7QrwYCsSoih7hj6sbsfXr19\nGoYWmk8Y7O/d3ttgyHuRH9k/2dQ/xL7avRpMNkPdr7ocJqI46hvx2X6UyOo7IBua\nkSkFbSmPZWIVAidNMBOnvffCQ32tfjT2/xso/a9cdskvxqgLi0MPARU9Nl2Pufsb\nD7l4/sBvz/PiNTKp+Daa9FdyLb9ySidos1uS0c24bUtY1RXXGAVV2qgfyrzvzfye\nSM+w16hMU/yeYiuA1jsPmsnZnuIJj4Nv8ZjjZ0WS53pP5wcghaHkBrqWQNT8meqA\nVElrMBPlYq67T+AXP0B9lf5Sc3QVIio7XKKfqrlcQxY2JGLEyE53JgZGX7dpwU4I\nukLvyHbT4p06oY3qG6+wH8+YIXCNAYtadJ/C5/u9GcLX5NnZrcuduj0inw2/a3Ao\nWgCt6/Pr28BkCvkWdDt9d8Z40qeu1aZdcr157mR+yZGPfBfB2vasrNIEwQ==\n-----END CERTIFICATE-----\n'})

TASK [remote/trust : Generate trust_ca.pem] ****************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/trust : Copy trust_ca.pem to host] ************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/trust : Install certificate] ******************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/trust : Remove temporary working directory] ***************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [Remote Starlingx] ************************************************************************************************************************

TASK [remote/starlingx : Create temporary working directory] ***********************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/starlingx : Copy SSL root certificates] *******************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost] => (item={'filename': 'vz_root_ica_cert.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIFNzCCAx+gAwIBAgIUGLJR/hP48n+vdq2v1hcfspXo/78wDQYJKoZIhvcNAQEL\nBQAwWjELMAkGA1UEBhMCVVMxEDAOBgNVBAoMB1Zlcml6b24xEzARBgNVBAsMClZa\nSUFNIFRlc3QxJDAiBgNVBAMMG1Zlcml6b24gTmV0d29yayBSU0EgQ0EgVGVzdDAe\nFw0yMDEwMjIyMTE0MDNaFw0zMDEwMjIyMTE0MDNaMIGRMQswCQYDVQQGEwJVUzEL\nMAkGA1UECAwCVFgxETAPBgNVBAcMCFdlc3RsYWtlMRAwDgYDVQQKDAdWZXJpem9u\nMR0wGwYDVQQLDBRWZXJpem9uIFNvdXJjaW5nIExMQzExMC8GA1UEAwwoVmVyaXpv\nbiBOZXR3b3JrIFdFTEtUWElCIExBQiAxIDMgUlNBIElDQTCCASIwDQYJKoZIhvcN\nAQEBBQADggEPADCCAQoCggEBANhkGTXOCKEYf5znDDeX3n/DHFPVqazgQsr0/SIG\n4eb1JY5q5Jq3ZhAaZCr9HJuCkwAP/zgYH0llqOvf8AC2Uh+7z1b33IbwxPmJfWCP\nAqSNFkLWWVRdbELapCu408QsrLMW8IrdP6PLiKAepwncfm4T0/6bANqIEmUkpw8Q\nxProeiNwlGbwUll+tELmdCk7vA7hKX3j1kUvS5Z84Z5ivJBWEcUEggmC97TK4aLo\nFVEHbyahze568JVEaM1vY5L4mnRRTl+u5ipaSMxVBsiXzF7eFuKCzqF7wxbDIt2T\nIFEJtwyJDW5bXjyXgiF1d5H/URprUcRV9Qmf2+PXcfwHII8CAwEAAaOBvDCBuTAS\nBgNVHRMBAf8ECDAGAQH/AgEAMA4GA1UdDwEB/wQEAwIBBjAfBgNVHSMEGDAWgBQl\neng3lqGBeTrbLVuABoEmUHm1+TBTBgNVHR8ETDBKMEigRqBEhkJodHRwOi8vc2Vj\ndXJlLnN0YWdpbmcuc2VjdXJpdHljcmVkZW50aWFsaW5nLmNvbS9jcmwvdnpuZXRy\nc2FjYS5jcmwwHQYDVR0OBBYEFP0Z+/vaDLtAoFig1I9ttNKnmzByMA0GCSqGSIb3\nDQEBCwUAA4ICAQBuXVTf9e01HeymHgRcFCwP2N6G6u+vIzY8Bz0zSUZeRDHMZQcS\nNoabDyn5FfGJlw4BqGC591Sp0/unFQDzAg17rDBcrgwajeFeUiFdb9PiAJwHaX9S\nvq/7VmVLCmpeb+a/laXAe6+tkY1kcFrd1+ItRKC6ZGXMsoDkmk5Ndxxgw77estcI\nMiiLQbvpXRygX5wD4/ayazuLms9qITZkOZ1nTLVqq7QrwYCsSoih7hj6sbsfXr19\nGoYWmk8Y7O/d3ttgyHuRH9k/2dQ/xL7avRpMNkPdr7ocJqI46hvx2X6UyOo7IBua\nkSkFbSmPZWIVAidNMBOnvffCQ32tfjT2/xso/a9cdskvxqgLi0MPARU9Nl2Pufsb\nD7l4/sBvz/PiNTKp+Daa9FdyLb9ySidos1uS0c24bUtY1RXXGAVV2qgfyrzvzfye\nSM+w16hMU/yeYiuA1jsPmsnZnuIJj4Nv8ZjjZ0WS53pP5wcghaHkBrqWQNT8meqA\nVElrMBPlYq67T+AXP0B9lf5Sc3QVIio7XKKfqrlcQxY2JGLEyE53JgZGX7dpwU4I\nukLvyHbT4p06oY3qG6+wH8+YIXCNAYtadJ/C5/u9GcLX5NnZrcuduj0inw2/a3Ao\nWgCt6/Pr28BkCvkWdDt9d8Z40qeu1aZdcr157mR+yZGPfBfB2vasrNIEwQ==\n-----END CERTIFICATE-----\n'})
changed: [welktxef-931887-rz-le2pts6-021 -> localhost] => (item={'filename': 'vz_root_ica_key.pem', 'value': '-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA2GQZNc4IoRh/nOcMN5fef8McU9WprOBCyvT9Igbh5vUljmrk\nmrdmEBpkKv0cm4KTAA//OBgfSWWo69/wALZSH7vPVvfchvDE+Yl9YI8CpI0WQtZZ\nVF1sQtqkK7jTxCyssxbwit0/o8uIoB6nCdx+bhPT/psA2ogSZSSnDxDE+uh6I3CU\nZvBSWX60QuZ0KTu8DuEpfePWRS9LlnzhnmK8kFYRxQSCCYL3tMrhougVUQdvJqHN\n7nrwlURozW9jkviadFFOX67mKlpIzFUGyJfMXt4W4oLOoXvDFsMi3ZMgUQm3DIkN\nbltePJeCIXV3kf9RGmtRxFX1CZ/b49dx/AcgjwIDAQABAoIBABSd1NkPfDr8/ouQ\nZ9WUHprFmBlUrgnOhA6aMNPhG/zJNn7PKGClQJAgM5L08pjOY/sJiyNpCPIRQXrX\npyIqPMDRP/vlOZmRrvKnas6cUYAkAQ71JSWokPv9oM6ZmXODXiDh+qEAW2PbrHS0\n9u01mMYcFYKYeghYFoiUaWZCDsJo3v3dgeE9aQ4tB9ksovSmWrpuCY7NKbd7Qrbo\n5XxQhkujTkE6knOHz8CVwYETtj8LZ/bvHIkGMGvRvwsKYDZkIKr5CZ7DX+KcMfPN\neMZU4VCHYSXNxsyp5DJ1Zw+gx8/32kUL0CzJLLam1G021Hq41KPwwSV/KPrOKel7\nHXDLXeECgYEA8MR+lgxGjYTc/k4TdZvcFVgqHGLXnyjO7ZVt4b7UpwmayLuoSD/M\nOpHQYX+JBIIWTNlGhG8UV3DPC3v+auhYa7twwbekS30IYCAmu5GCKgMAcWFinz6A\nYZxG55P/hShetCyOqikgwXqzMlwGs8KEul8f8BKssROzUy8mIlFhjq0CgYEA5hTM\nSNxAD3dlRtb0771fBU7fjx8JPfjptP9vP/JVEelkc/ti9nZ5buTC+9cQC/B+YFx7\nc82uCrXV13bGR9iH8xBhwU7JOYJZbgCpwp0F56wIN5Pdk9Eo79Batrw3oGBG4Yvt\nDc2eltxQbHgObc/qygf88j9XqD8aGIvQrc4Jf6sCgYAtxX03M1A6WTbWFau3YRD+\n8crXqKbLOCvWmODR2MB+nOHTJXHBgndl7xCJaIB43e41X9z7Ek7wrJ5/1WuxkUg1\n+uVdvna6byOnepVCdVAkgnuUEmp4UZ6AcAA+yDD8dIdEg2//w1/ZyGTGvx37EJDB\nCZJ9xl8ULuWZe84pGgWM5QKBgQCYVUbYKrNjShrM5z9uh4QlII6V1Oeql2YtBz4i\nKZE3db6jp9pi8hf+WwnZ8g9WyFjz9edqydAkmTXHHYW0ReHlBYCjm0VRhUMuuNOs\n3YfuVpFuMsFuv/oJpXqaKE3wKi5j4OAH1o7ctWuuFWMAQ7vhHZ7UySmBZJ4jiFaW\n7KaPVwKBgE8E0xbSDVGxXbEGwRXxeaOSemEHD9uEnbAyq1p3EBBhBvInWmDiP5vJ\n68IYNZ4SGxXEKDifwrLGHyekt3RK9B2+U03okd1qH7gfBIlxBJivcjhBe2PtK/Qj\n6fBN0fC1UJoE6pseT9cJDaBq2wMRXJGRYtT8fU9PPJcfa23JlKNS\n-----END RSA PRIVATE KEY-----\n'})

TASK [remote/starlingx : Copy templates] *******************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost] => (item=req_starlingx.cnf)

TASK [remote/starlingx : Generate SSL cert] ****************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/starlingx : Copy SSL starlingx certs to server] ***********************************************************************************
changed: [welktxef-931887-rz-le2pts6-021] => (item=starlingx-ca-cert.pem)

TASK [remote/starlingx : Configure starlingx] **************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/starlingx : Remove temporary working directory] ***********************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [Remote Integ] ****************************************************************************************************************************

TASK [remote/integ : Detect applied status of platform-integ-apps application] *****************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/integ : Fail if platform-integ-apps application apply failed] *********************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [Remote Ldap] *****************************************************************************************************************************

TASK [remote/ldap : Create temporary working directory] ****************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/ldap : Copy SSL root certificates] ************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost] => (item={'filename': 'vz_root_ca_cert.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIFpTCCA42gAwIBAgIUa3vZ0YGxO1TQ8NwhiVfQC0JslXgwDQYJKoZIhvcNAQEL\nBQAwWjELMAkGA1UEBhMCVVMxEDAOBgNVBAoMB1Zlcml6b24xEzARBgNVBAsMClZa\nSUFNIFRlc3QxJDAiBgNVBAMMG1Zlcml6b24gTmV0d29yayBSU0EgQ0EgVGVzdDAe\nFw0yMDA2MTUyMTAxMTNaFw0zNTA2MTUyMTAxMTNaMFoxCzAJBgNVBAYTAlVTMRAw\nDgYDVQQKDAdWZXJpem9uMRMwEQYDVQQLDApWWklBTSBUZXN0MSQwIgYDVQQDDBtW\nZXJpem9uIE5ldHdvcmsgUlNBIENBIFRlc3QwggIiMA0GCSqGSIb3DQEBAQUAA4IC\nDwAwggIKAoICAQC8AIrksI57CbIl5uGZ6yqfpQj3aK+N8f1EVHdwK9JFskoipvC8\n7yFTk8tgmO1i0YA5oRGfNxneqCdrXZiWL6Ko8v/iln9vuN+2rK3rgWZPPRJBAsBN\na49L7U6lJjIGxIZtZqmK5h47oiUtwlYVrbZMN2ijuBQ22/eQ9tsFDV28oBuZ3WAR\npSSbj/tubPQYkw3YYOhv/VpEpsd0rkoEt3QCmTVcX2rtblanpXowTV5R0Hy4014n\nT49jrEo40r4mwYoyS835Uv4ENUFA+pXicT9eUot3RSH6rYdx4A/14UtoI9U0ol8M\n62GHpxSASQ2Kc3yQWvxRGTFslTduYM+vVmMLEDDdqcsjYnStPpwdxxmKItmbjxSv\nIwYIndp8A04WkX2iiJCciC3BNxiLamPtYVyB1HHqbGTGirKYuSvwZt337q1OI3WH\nwVn2S4Mj/wqa4iCyGTvFSUnGq34Xkrb9XNwWBok9Tc2XWGAU/mb/xcd1hX74GZbF\nsrZ11aPtym4kMAjU2KQi96GcAH2lnGZYoOja1J4Cs4WYx1uAx74H/m84CrYavVfl\n1ONJVLDfuZaEkSmu+jHQX15pAECNORTuLD06PbWnOEcOi1xmbt/OT3SA3rhD2mb7\n2wxl7oJpV3ap8xGwYmxiFzmInxFJ1axjg8Rimol0mXTKAy6OdNHbCOnAwwIDAQAB\no2MwYTAPBgNVHRMBAf8EBTADAQH/MA4GA1UdDwEB/wQEAwIBBjAfBgNVHSMEGDAW\ngBQleng3lqGBeTrbLVuABoEmUHm1+TAdBgNVHQ4EFgQUJXp4N5ahgXk62y1bgAaB\nJlB5tfkwDQYJKoZIhvcNAQELBQADggIBADQ9jpmVh9nyY7ZQ4s+S9RuSRYn7QsrW\nDePeMzQgh8ZtS8WE65GY5HS61iHNP2Co8Q1lAaBWF4ipq+VZOcQbPLccHzd1kZv4\ns4u0aTzBd9ccidl73FS0DJDQOBbzPSzgsaiGHSMyGzkTeA8z3ntsSqrXXcDUvoRi\nFus/110AwdtNhJLrWveX6btYtHp9Lqe0YtNCy5AaXlrr1yRSckP5BWVtlwD4dzSO\n/dqI3wHS/ncUx9wSQomZ+AmxYW3KtJQKgHzTqHru1x9BBk7Bzfz9FZr6HLLmEitj\nuFoDRd5TNt5LbO0zDQokvY3oqso6Htup/rS7C08mcmnelYE+yXuOc1YrlyGnpBzk\nmy+1VYbOxRRdqKAZRbE72u/h847IVpsOvjR51iksuCAurZdp2+y2zvV8NhWekuNy\nirECRy9cb4YasjRaKi0/TCGPVSICuLyeG2W72liCj/N2VKfjPP9zsOR5XjwCXfRg\n+9xhLy77/gov2NWXx5fzTkhxCrHOxFdLVMn0wQhksDmw6QsXzDIHSpIOypdDfnx9\nCsthx3nhkuHLUaEP22D22dG+vImA9ukj4R/RRI/87jmi9Q8+ehH+NqN0GZZcLjdN\nSLVXpncuwWQFUDPR06wNkkkmBSXWiIYhwqSpU0Pl3er3fD0uWvXuWPm2PzfOmUAE\nUrkzyw9XmLw0\n-----END CERTIFICATE-----\n'})
changed: [welktxef-931887-rz-le2pts6-021 -> localhost] => (item={'filename': 'vz_root_ica_cert.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIFNzCCAx+gAwIBAgIUGLJR/hP48n+vdq2v1hcfspXo/78wDQYJKoZIhvcNAQEL\nBQAwWjELMAkGA1UEBhMCVVMxEDAOBgNVBAoMB1Zlcml6b24xEzARBgNVBAsMClZa\nSUFNIFRlc3QxJDAiBgNVBAMMG1Zlcml6b24gTmV0d29yayBSU0EgQ0EgVGVzdDAe\nFw0yMDEwMjIyMTE0MDNaFw0zMDEwMjIyMTE0MDNaMIGRMQswCQYDVQQGEwJVUzEL\nMAkGA1UECAwCVFgxETAPBgNVBAcMCFdlc3RsYWtlMRAwDgYDVQQKDAdWZXJpem9u\nMR0wGwYDVQQLDBRWZXJpem9uIFNvdXJjaW5nIExMQzExMC8GA1UEAwwoVmVyaXpv\nbiBOZXR3b3JrIFdFTEtUWElCIExBQiAxIDMgUlNBIElDQTCCASIwDQYJKoZIhvcN\nAQEBBQADggEPADCCAQoCggEBANhkGTXOCKEYf5znDDeX3n/DHFPVqazgQsr0/SIG\n4eb1JY5q5Jq3ZhAaZCr9HJuCkwAP/zgYH0llqOvf8AC2Uh+7z1b33IbwxPmJfWCP\nAqSNFkLWWVRdbELapCu408QsrLMW8IrdP6PLiKAepwncfm4T0/6bANqIEmUkpw8Q\nxProeiNwlGbwUll+tELmdCk7vA7hKX3j1kUvS5Z84Z5ivJBWEcUEggmC97TK4aLo\nFVEHbyahze568JVEaM1vY5L4mnRRTl+u5ipaSMxVBsiXzF7eFuKCzqF7wxbDIt2T\nIFEJtwyJDW5bXjyXgiF1d5H/URprUcRV9Qmf2+PXcfwHII8CAwEAAaOBvDCBuTAS\nBgNVHRMBAf8ECDAGAQH/AgEAMA4GA1UdDwEB/wQEAwIBBjAfBgNVHSMEGDAWgBQl\neng3lqGBeTrbLVuABoEmUHm1+TBTBgNVHR8ETDBKMEigRqBEhkJodHRwOi8vc2Vj\ndXJlLnN0YWdpbmcuc2VjdXJpdHljcmVkZW50aWFsaW5nLmNvbS9jcmwvdnpuZXRy\nc2FjYS5jcmwwHQYDVR0OBBYEFP0Z+/vaDLtAoFig1I9ttNKnmzByMA0GCSqGSIb3\nDQEBCwUAA4ICAQBuXVTf9e01HeymHgRcFCwP2N6G6u+vIzY8Bz0zSUZeRDHMZQcS\nNoabDyn5FfGJlw4BqGC591Sp0/unFQDzAg17rDBcrgwajeFeUiFdb9PiAJwHaX9S\nvq/7VmVLCmpeb+a/laXAe6+tkY1kcFrd1+ItRKC6ZGXMsoDkmk5Ndxxgw77estcI\nMiiLQbvpXRygX5wD4/ayazuLms9qITZkOZ1nTLVqq7QrwYCsSoih7hj6sbsfXr19\nGoYWmk8Y7O/d3ttgyHuRH9k/2dQ/xL7avRpMNkPdr7ocJqI46hvx2X6UyOo7IBua\nkSkFbSmPZWIVAidNMBOnvffCQ32tfjT2/xso/a9cdskvxqgLi0MPARU9Nl2Pufsb\nD7l4/sBvz/PiNTKp+Daa9FdyLb9ySidos1uS0c24bUtY1RXXGAVV2qgfyrzvzfye\nSM+w16hMU/yeYiuA1jsPmsnZnuIJj4Nv8ZjjZ0WS53pP5wcghaHkBrqWQNT8meqA\nVElrMBPlYq67T+AXP0B9lf5Sc3QVIio7XKKfqrlcQxY2JGLEyE53JgZGX7dpwU4I\nukLvyHbT4p06oY3qG6+wH8+YIXCNAYtadJ/C5/u9GcLX5NnZrcuduj0inw2/a3Ao\nWgCt6/Pr28BkCvkWdDt9d8Z40qeu1aZdcr157mR+yZGPfBfB2vasrNIEwQ==\n-----END CERTIFICATE-----\n'})
changed: [welktxef-931887-rz-le2pts6-021 -> localhost] => (item={'filename': 'vz_root_ica_key.pem', 'value': '-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA2GQZNc4IoRh/nOcMN5fef8McU9WprOBCyvT9Igbh5vUljmrk\nmrdmEBpkKv0cm4KTAA//OBgfSWWo69/wALZSH7vPVvfchvDE+Yl9YI8CpI0WQtZZ\nVF1sQtqkK7jTxCyssxbwit0/o8uIoB6nCdx+bhPT/psA2ogSZSSnDxDE+uh6I3CU\nZvBSWX60QuZ0KTu8DuEpfePWRS9LlnzhnmK8kFYRxQSCCYL3tMrhougVUQdvJqHN\n7nrwlURozW9jkviadFFOX67mKlpIzFUGyJfMXt4W4oLOoXvDFsMi3ZMgUQm3DIkN\nbltePJeCIXV3kf9RGmtRxFX1CZ/b49dx/AcgjwIDAQABAoIBABSd1NkPfDr8/ouQ\nZ9WUHprFmBlUrgnOhA6aMNPhG/zJNn7PKGClQJAgM5L08pjOY/sJiyNpCPIRQXrX\npyIqPMDRP/vlOZmRrvKnas6cUYAkAQ71JSWokPv9oM6ZmXODXiDh+qEAW2PbrHS0\n9u01mMYcFYKYeghYFoiUaWZCDsJo3v3dgeE9aQ4tB9ksovSmWrpuCY7NKbd7Qrbo\n5XxQhkujTkE6knOHz8CVwYETtj8LZ/bvHIkGMGvRvwsKYDZkIKr5CZ7DX+KcMfPN\neMZU4VCHYSXNxsyp5DJ1Zw+gx8/32kUL0CzJLLam1G021Hq41KPwwSV/KPrOKel7\nHXDLXeECgYEA8MR+lgxGjYTc/k4TdZvcFVgqHGLXnyjO7ZVt4b7UpwmayLuoSD/M\nOpHQYX+JBIIWTNlGhG8UV3DPC3v+auhYa7twwbekS30IYCAmu5GCKgMAcWFinz6A\nYZxG55P/hShetCyOqikgwXqzMlwGs8KEul8f8BKssROzUy8mIlFhjq0CgYEA5hTM\nSNxAD3dlRtb0771fBU7fjx8JPfjptP9vP/JVEelkc/ti9nZ5buTC+9cQC/B+YFx7\nc82uCrXV13bGR9iH8xBhwU7JOYJZbgCpwp0F56wIN5Pdk9Eo79Batrw3oGBG4Yvt\nDc2eltxQbHgObc/qygf88j9XqD8aGIvQrc4Jf6sCgYAtxX03M1A6WTbWFau3YRD+\n8crXqKbLOCvWmODR2MB+nOHTJXHBgndl7xCJaIB43e41X9z7Ek7wrJ5/1WuxkUg1\n+uVdvna6byOnepVCdVAkgnuUEmp4UZ6AcAA+yDD8dIdEg2//w1/ZyGTGvx37EJDB\nCZJ9xl8ULuWZe84pGgWM5QKBgQCYVUbYKrNjShrM5z9uh4QlII6V1Oeql2YtBz4i\nKZE3db6jp9pi8hf+WwnZ8g9WyFjz9edqydAkmTXHHYW0ReHlBYCjm0VRhUMuuNOs\n3YfuVpFuMsFuv/oJpXqaKE3wKi5j4OAH1o7ctWuuFWMAQ7vhHZ7UySmBZJ4jiFaW\n7KaPVwKBgE8E0xbSDVGxXbEGwRXxeaOSemEHD9uEnbAyq1p3EBBhBvInWmDiP5vJ\n68IYNZ4SGxXEKDifwrLGHyekt3RK9B2+U03okd1qH7gfBIlxBJivcjhBe2PtK/Qj\n6fBN0fC1UJoE6pseT9cJDaBq2wMRXJGRYtT8fU9PPJcfa23JlKNS\n-----END RSA PRIVATE KEY-----\n'})

TASK [remote/ldap : Copy templates] ************************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost] => (item={'name': 'req-ldap.cnf', 'mode': '0644'})

TASK [remote/ldap : Generate SSL cert] *********************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/ldap : Copy templates] ************************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021] => (item={'name': 'dex-overrides.yaml', 'mode': '0644'})

TASK [remote/ldap : Copy SSL dex certs to server] **********************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021] => (item=dex-cert.pem)
changed: [welktxef-931887-rz-le2pts6-021] => (item=dex-key.pem)
changed: [welktxef-931887-rz-le2pts6-021] => (item=dex-ca.pem)

TASK [remote/ldap : Copy SSL AD cert to server] ************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021] => (item={'filename': 'ad_ca.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIFpTCCA42gAwIBAgIUa3vZ0YGxO1TQ8NwhiVfQC0JslXgwDQYJKoZIhvcNAQEL\nBQAwWjELMAkGA1UEBhMCVVMxEDAOBgNVBAoMB1Zlcml6b24xEzARBgNVBAsMClZa\nSUFNIFRlc3QxJDAiBgNVBAMMG1Zlcml6b24gTmV0d29yayBSU0EgQ0EgVGVzdDAe\nFw0yMDA2MTUyMTAxMTNaFw0zNTA2MTUyMTAxMTNaMFoxCzAJBgNVBAYTAlVTMRAw\nDgYDVQQKDAdWZXJpem9uMRMwEQYDVQQLDApWWklBTSBUZXN0MSQwIgYDVQQDDBtW\nZXJpem9uIE5ldHdvcmsgUlNBIENBIFRlc3QwggIiMA0GCSqGSIb3DQEBAQUAA4IC\nDwAwggIKAoICAQC8AIrksI57CbIl5uGZ6yqfpQj3aK+N8f1EVHdwK9JFskoipvC8\n7yFTk8tgmO1i0YA5oRGfNxneqCdrXZiWL6Ko8v/iln9vuN+2rK3rgWZPPRJBAsBN\na49L7U6lJjIGxIZtZqmK5h47oiUtwlYVrbZMN2ijuBQ22/eQ9tsFDV28oBuZ3WAR\npSSbj/tubPQYkw3YYOhv/VpEpsd0rkoEt3QCmTVcX2rtblanpXowTV5R0Hy4014n\nT49jrEo40r4mwYoyS835Uv4ENUFA+pXicT9eUot3RSH6rYdx4A/14UtoI9U0ol8M\n62GHpxSASQ2Kc3yQWvxRGTFslTduYM+vVmMLEDDdqcsjYnStPpwdxxmKItmbjxSv\nIwYIndp8A04WkX2iiJCciC3BNxiLamPtYVyB1HHqbGTGirKYuSvwZt337q1OI3WH\nwVn2S4Mj/wqa4iCyGTvFSUnGq34Xkrb9XNwWBok9Tc2XWGAU/mb/xcd1hX74GZbF\nsrZ11aPtym4kMAjU2KQi96GcAH2lnGZYoOja1J4Cs4WYx1uAx74H/m84CrYavVfl\n1ONJVLDfuZaEkSmu+jHQX15pAECNORTuLD06PbWnOEcOi1xmbt/OT3SA3rhD2mb7\n2wxl7oJpV3ap8xGwYmxiFzmInxFJ1axjg8Rimol0mXTKAy6OdNHbCOnAwwIDAQAB\no2MwYTAPBgNVHRMBAf8EBTADAQH/MA4GA1UdDwEB/wQEAwIBBjAfBgNVHSMEGDAW\ngBQleng3lqGBeTrbLVuABoEmUHm1+TAdBgNVHQ4EFgQUJXp4N5ahgXk62y1bgAaB\nJlB5tfkwDQYJKoZIhvcNAQELBQADggIBADQ9jpmVh9nyY7ZQ4s+S9RuSRYn7QsrW\nDePeMzQgh8ZtS8WE65GY5HS61iHNP2Co8Q1lAaBWF4ipq+VZOcQbPLccHzd1kZv4\ns4u0aTzBd9ccidl73FS0DJDQOBbzPSzgsaiGHSMyGzkTeA8z3ntsSqrXXcDUvoRi\nFus/110AwdtNhJLrWveX6btYtHp9Lqe0YtNCy5AaXlrr1yRSckP5BWVtlwD4dzSO\n/dqI3wHS/ncUx9wSQomZ+AmxYW3KtJQKgHzTqHru1x9BBk7Bzfz9FZr6HLLmEitj\nuFoDRd5TNt5LbO0zDQokvY3oqso6Htup/rS7C08mcmnelYE+yXuOc1YrlyGnpBzk\nmy+1VYbOxRRdqKAZRbE72u/h847IVpsOvjR51iksuCAurZdp2+y2zvV8NhWekuNy\nirECRy9cb4YasjRaKi0/TCGPVSICuLyeG2W72liCj/N2VKfjPP9zsOR5XjwCXfRg\n+9xhLy77/gov2NWXx5fzTkhxCrHOxFdLVMn0wQhksDmw6QsXzDIHSpIOypdDfnx9\nCsthx3nhkuHLUaEP22D22dG+vImA9ukj4R/RRI/87jmi9Q8+ehH+NqN0GZZcLjdN\nSLVXpncuwWQFUDPR06wNkkkmBSXWiIYhwqSpU0Pl3er3fD0uWvXuWPm2PzfOmUAE\nUrkzyw9XmLw0\n-----END CERTIFICATE-----\n'})

TASK [remote/ldap : Configure local-dex.tls] ***************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/ldap : Configure generic] *********************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/ldap : Configure wadcert] *********************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/ldap : Configure dex-overrides.yaml] **********************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/ldap : Wait for distributed cloud synchronization] ********************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001]

TASK [remote/ldap : Remove temporary working directory] ****************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/ldap : Detect oidc-auth-apps application in applying state (from a previous attempt)] *********************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/ldap : Fail if oidc-auth-apps application-abort failed] ***************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/ldap : Detect oidc-auth-apps application in apply-failed or aborted state] ********************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/ldap : Fail if oidc-auth-apps application apply failed] ***************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/ldap : Apply oidc-auth-apps application] ******************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/ldap : Detect applied status of oidc-auth-apps application] ***********************************************************************
FAILED - RETRYING: Detect applied status of oidc-auth-apps application (60 retries left).
FAILED - RETRYING: Detect applied status of oidc-auth-apps application (59 retries left).
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/ldap : Fail if oidc-auth-apps application apply failed] ***************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [Remote Metrics Server] *******************************************************************************************************************

TASK [remote/metrics-server : Set facts - 21.05] ***********************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Set facts - 21.12] ***********************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Get software load status] ****************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Noop if the system is NOT at the right caas_version] *************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Print message if system is NOT at the right caas_version] ********************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Detect presence of existing application] *************************************************************************
fatal: [welktxef-931887-rz-le2pts6-021]: FAILED! => {"changed": true, "cmd": ". /etc/platform/openrc\nsystem application-show metrics-server --column status --format value\n", "delta": "0:00:01.937678", "end": "2023-09-15 17:43:30.530757", "msg": "non-zero return code", "rc": 1, "start": "2023-09-15 17:43:28.593079", "stderr": "application not found: metrics-server", "stderr_lines": ["application not found: metrics-server"], "stdout": "", "stdout_lines": []}
...ignoring

TASK [remote/metrics-server : Print message if system already has the appication] **************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Apply again since the previous apply failed or in uploaded state] ************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Wait until apply is in the applied or apply-failed state] ********************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Print message if re-apply succeeds] ******************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Print message if re-apply failed] ********************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Noop if system requires no further action or needs manual investigation] *****************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Upload application] **********************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Wait until application is in the uploaded state] *****************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Apply application] ***********************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Wait until application is in the applied or apply-failed state] **************************************************
FAILED - RETRYING: Wait until application is in the applied or apply-failed state (90 retries left).
FAILED - RETRYING: Wait until application is in the applied or apply-failed state (89 retries left).
FAILED - RETRYING: Wait until application is in the applied or apply-failed state (88 retries left).
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Apply again since the first apply failed] ************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Wait again until apply is in the applied or apply-failed state] **************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/metrics-server : Print message if apply is successful] ****************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "msg": [
        "=======================================================",
        " welktxef-d931887-021: metrics-server install SUCCEEDED! ",
        "======================================================="
    ]
}

TASK [remote/metrics-server : Print message if apply is failure] *******************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [Remote wrap-get-central-version] *********************************************************************************************************

TASK [remote/wrap-get-central-version : Set facts for playbook] ********************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/wrap-get-central-version : Determine central WRA current version] *****************************************************************
fatal: [welktxef-931887-rz-le2pts6-021 -> rchltxfe-c000000-001]: FAILED! => {"changed": true, "cmd": ". /etc/platform/openrc\nsystem application-show wr-analytics --column app_version --format value\n", "delta": "0:00:01.306062", "end": "2023-09-15 17:44:26.451650", "msg": "non-zero return code", "rc": 1, "start": "2023-09-15 17:44:25.145588", "stderr": "application not found: wr-analytics", "stderr_lines": ["application not found: wr-analytics"], "stdout": "", "stdout_lines": []}
...ignoring

TASK [remote/wrap-get-central-version : Set facts for wra_target_version] **********************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/wrap-get-central-version : debug] *************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "msg": "wra_target_version:"
}

TASK [Remote wrap-2112-2] **********************************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [Remote wrap-2106-2] **********************************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [Remote wrap-6] ***************************************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [Remote fpga-user-image] ******************************************************************************************************************

TASK [remote/fpga-user-image : Set facts for ansible credential - 21.05] ***********************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Set facts for ansible credential - 21.12] ***********************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Get software load status] ***************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Noop if the system is NOT at the right caas_version] ************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Print message if system is NOT at the right caas_version] *******************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Set facts for default fpga_image_file] **************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Set facts for fpga_image_file from host_vars] *******************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Print message if server is not LS3 cascadelake] *****************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "msg": [
        "==================================================================================",
        " Server type ZTS-LS6-pts6 is not LS3 cascadelake, no action will take place! ",
        "=================================================================================="
    ]
}

TASK [remote/fpga-user-image : Register noop because server is not LS3 cascadelake] ************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Check if FPGA update is stuck] **********************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Abort FPGA update] **********************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : include_tasks] **************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Check FPGA update status (HPE-LS3-e910)] ************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Check FPGA update status (ZTS-LS3-trtn)] ************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Noop if the system has been updated] ****************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Print message if the system has been updated] *******************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : In main block] **************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Copy files to host] *********************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021] => (item=20ww43.5-1x2x25G-5GLDPC-v1.6.2-3.0.1-unsigned.bin)

TASK [remote/fpga-user-image : Do system device-image-upload] **********************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : debug - print UUID] *********************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Do system device-image-apply] ***********************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Do system host-device-image-update] *****************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Wait till application completed] ********************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : Do system device-image-state-list] ******************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : force an error if image state is not completed] *****************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [remote/fpga-user-image : include_tasks] **************************************************************************************************
skipping: [welktxef-931887-rz-le2pts6-021]

TASK [Install DM Monitor] **********************************************************************************************************************

TASK [common/dm-monitor : Install DM Monitor] **************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [common/dm-monitor : Wait for DM Monitor pod created] *************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [common/dm-monitor : Wait for control-plane pods become ready] ****************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [common/dm-monitor : debug] ***************************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "dm_monitor_pod_ready.stdout_lines": [
        "pod/dm-monitor-77fd4b6649-67c6t condition met"
    ]
}

TASK [Proteus MWIAT - DISABLE] *****************************************************************************************************************

TASK [remote/zt-redfish : Update Attributes at /redfish/v1/Systems/Self/Bios/SD] ***************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [remote/zt-redfish : Update result] *******************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "update_result": {
        "allow": "GET, PUT, PATCH, POST",
        "changed": false,
        "connection": "close",
        "content": "",
        "cookies": {},
        "cookies_string": "",
        "date": "Fri, 15 Sep 2023 17:44:40 GMT",
        "elapsed": 0,
        "failed": false,
        "msg": "OK (unknown bytes)",
        "redirected": false,
        "server": "AMI MegaRAC Redfish Service",
        "status": 204,
        "url": "https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/Systems/Self/Bios/SD"
    }
}

TASK [Lock/unlock after MWAIT change] **********************************************************************************************************

TASK [common/lock-unlock : set_fact] ***********************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [common/lock-unlock : include_tasks] ******************************************************************************************************
included: /home/XXXXXX/playbooks/wr-installer/roles/common/lock-unlock/tasks/lock_node.yaml for welktxef-931887-rz-le2pts6-021

TASK [common/lock-unlock : Check subcloud status before locking] *******************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [common/lock-unlock : debug] **************************************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "msg": "The host is unlocked, continue with locking."
}

TASK [common/lock-unlock : Lock subcloud] ******************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [common/lock-unlock : Pause for 10 seconds for the command to complete] *******************************************************************
Pausing for 10 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [welktxef-931887-rz-le2pts6-021]

TASK [common/lock-unlock : Wait until subcloud is in locked status] ****************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [common/lock-unlock : Display subcloud status] ********************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021] => {
    "host_status_new.stdout": "locked"
}

TASK [common/lock-unlock : include_tasks] ******************************************************************************************************
included: /home/XXXXXX/playbooks/wr-installer/roles/common/lock-unlock/tasks/unlock_node.yaml for welktxef-931887-rz-le2pts6-021

TASK [common/lock-unlock : Check subcloud status before unlocking] *****************************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [common/lock-unlock : Unlock subcloud] ****************************************************************************************************
changed: [welktxef-931887-rz-le2pts6-021]

TASK [common/lock-unlock : Wait for node to restart (port 22 goes down)] ***********************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [common/lock-unlock : Wait for node be back up (port 5000 comes up)] **********************************************************************
ok: [welktxef-931887-rz-le2pts6-021]

TASK [common/lock-unlock : Obtain Keystone auth token] *****************************************************************************************
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

TASK [common/lock-unlock : Wait for contoller-0 enabled] ***************************************************************************************
FAILED - RETRYING: Wait for contoller-0 enabled (60 retries left).
ok: [welktxef-931887-rz-le2pts6-021 -> localhost]

PLAY RECAP *************************************************************************************************************************************
welktxef-931887-rz-le2pts6-021 : ok=133  changed=58   unreachable=0    failed=0    skipped=63   rescued=0    ignored=4

[XXXXXX@welktxefnce-h-pe1util-vm01 wr-installer]$
```


### post deployment 

```log 
[XXXXXX@welktxefnce-h-pe1util-vm01 wrcp_post_deployment]$ ansible-playbook --vault-password-file /tmp/vault-pass -i inventory/ri_1.yaml wrcp_subcloud_post_deployment.yaml

PLAY [Post deployment steps fro WRCP subclouds] ************************************************************************************************

TASK [set vendor as samsung] *******************************************************************************************************************
ok: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : create vdu namespace] ************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]
included: /home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/generic/tasks/create_generic_resources.yaml for welktxef-931887-rz-le0pts6-021

TASK [subclouds/generic : Create working directory] ********************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : Template generic files into workdir] *********************************************************************************
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/generic/templates/samsung/generic/crd-role.yaml.j2)
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/generic/templates/samsung/generic/orchestration_sa_cluster.yaml.j2)
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/generic/templates/samsung/generic/orchestration_sa.yaml.j2)
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/generic/templates/samsung/generic/samsung_debug_sa.yaml.j2)
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/generic/templates/samsung/generic/ss_sa.yaml.j2)

TASK [subclouds/generic : Create generic resources] ********************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]
included: /home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/generic/tasks/create_k8s_files.yaml for welktxef-931887-rz-le0pts6-021

TASK [subclouds/generic : Create working directory] ********************************************************************************************
ok: [welktxef-931887-rz-le0pts6-021 -> localhost]

TASK [subclouds/generic : Get token for Orch - 21.05] ******************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : store orch token] ****************************************************************************************************
ok: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : Get token for SS Debug] **********************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : store ss token] ******************************************************************************************************
ok: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : print orch token] ****************************************************************************************************
ok: [welktxef-931887-rz-le0pts6-021] => {
    "orch_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjNyTzE3eTdhZGRVc2lva3FkdjRjR0xrMHBfMFcyWjlfSHNGdm5XUlBSM1EifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6Im9yY2hlc3RyYXRpb24tc2EtdG9rZW4teGg5ZmsiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoib3JjaGVzdHJhdGlvbi1zYSIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6ImFmYTE3OTkyLTFjYjQtNDJmYi04OGJlLWU4MjNmZDliOGViOSIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpkZWZhdWx0Om9yY2hlc3RyYXRpb24tc2EifQ.eHsiL4R7_PG_hfNdW6UMvCUTLXyeIFIjKd5VYfi6v40KsykMNrIVzo_Yj8lRwYv0HJBcpTgjr7vvh8BqX-JLxSgt_Gb-cdqMcESgbbJoRbjqN1Lwxp5LKPTDMkOcgBgULqplaKgItN0ZicFXKQEXEGI8CST4iyj0XP-aDKV8rFFb-3yaqjwmzCzUUD-pPSq9D_y72Kz76d2o3ijuf77M3g0wGMPKDINPQ3UEXbQpcFn1EiJnKgNL5GrsKbn3fqne9gQMNt_28QEutBZ_s0xBqv2zikdrMspBJQ07iJGM2_p4t5BVUPsYxbIZp4EZbipcpeva69J4G0nQ9wqhIBwMow"
}

TASK [subclouds/generic : print ss token] ******************************************************************************************************
ok: [welktxef-931887-rz-le0pts6-021] => {
    "ss_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjNyTzE3eTdhZGRVc2lva3FkdjRjR0xrMHBfMFcyWjlfSHNGdm5XUlBSM1EifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6InNhbXN1bmctc2EtdG9rZW4tNW1tNGIiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoic2Ftc3VuZy1zYSIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6ImJjMmM5YWU1LWNmNjMtNDYzNy1hYzY5LTI3ZmUxNzgwZThhYiIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpkZWZhdWx0OnNhbXN1bmctc2EifQ.MiKAoi51FPLV2hRt0_7esiUbe9kP88VcXIo0UvOk132bE8ZhzgPLiG4bQNrTclE3UW_zcgOImgr14YbPM4ANRUALHfquzfCU6mAacc3l_e_un_LYxzsC_WuVJuQK7YKAQy0zRlkeNhgZb_bd1KeWetiuGToGElBASP6sbm_uSV_WmP1gXVXorTW5Yp5kqYI2wcvh9VYapTBOcE4rEkXgfEUeO_-pq_aO5yhykXZjh-YfMxRav6aWlK3KrBbR-1n71KkoeqVjQQeWygRYU-cWML21lwsAgVoeBEgS5HCTF82GOi5lSAHytzHlybscrgqbcLq2RXDe9VwBQIgBZQcB_A"
}

TASK [subclouds/generic : Template k8s files into temp dir] ************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021 -> localhost] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/generic/templates/samsung/k8s/kubeconfig-orchestration.conf.j2)
changed: [welktxef-931887-rz-le0pts6-021 -> localhost] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/generic/templates/samsung/k8s/kubeconfig-samsung-debug.conf.j2)
included: /home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/generic/tasks/create_local_registry_secret.yaml for welktxef-931887-rz-le0pts6-021

TASK [subclouds/generic : Create secret in welktxef-931887vzwcvdu-y-ss-ls6-00000000021 for pulling from local registry] ************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : Create alternative secret in welktxef-931887vzwcvdu-y-ss-ls6-00000000021 for pulling from vudorch's own registry] ****
changed: [welktxef-931887-rz-le0pts6-021]
included: /home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/generic/tasks/update_platform_integ_apps.yaml for welktxef-931887-rz-le0pts6-021

TASK [subclouds/generic : Create working directory] ********************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : Template platform integ apps override file into temp dir] ************************************************************
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/generic/tasks/../templates/samsung/platform-integ/rbd-namespaces.yaml.j2)

TASK [subclouds/generic : Update platform integ apps] ******************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]
FAILED - RETRYING: Wait until application is out of the applying state (90 retries left).

TASK [subclouds/generic : Wait until application is out of the applying state] *****************************************************************
changed: [welktxef-931887-rz-le0pts6-021]
included: /home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/generic/tasks/store_ptp_notification_client_image.yaml for welktxef-931887-rz-le0pts6-021

TASK [subclouds/generic : set the correct tag for notificationclient-base image - up to 21.12] *************************************************
ok: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : Log in registry.central] *********************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : Pull ptp notification client image from registry.central] ************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : Log out from registry.central] ***************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : Tag ptp notification client image from registry.central] *************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : Log in registry.local] ***********************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : Push ptp notification client image to registry.local] ****************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : Log out from registry.local] *****************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : Delete image from Docker cache] **************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : create vdu namespace] ***********************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]
included: /home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/tasks/lock_node.yaml for welktxef-931887-rz-le0pts6-021

TASK [subclouds/specific : Check subcloud status before locking] *******************************************************************************
ok: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Lock subcloud] ******************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]
Pausing for 10 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)

TASK [subclouds/specific : Pause for 10 seconds for the command to complete] *******************************************************************
ok: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Wait until subcloud is in locked status] ****************************************************************************
ok: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Display subcloud status] ********************************************************************************************
ok: [welktxef-931887-rz-le0pts6-021] => {
    "subcloud_status.stdout_lines": [
        "+----+--------------+-------------+----------------+-------------+--------------+",
        "| id | hostname     | personality | administrative | operational | availability |",
        "+----+--------------+-------------+----------------+-------------+--------------+",
        "| 1  | controller-0 | controller  | locked         | disabled    | online       |",
        "+----+--------------+-------------+----------------+-------------+--------------+"
    ]
}
included: /home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/tasks/system_configs_ls6.yaml for welktxef-931887-rz-le0pts6-021

TASK [subclouds/specific : Configure CPU] ******************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Configure sriov0] ***************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Configure sriov1] ***************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Configure fh0] ******************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Configure fh1] ******************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Configure fh2] ******************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Configure fh3] ******************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Configure fh4] ******************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Configure fh5] ******************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Configure ptp] ******************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Configure PLM] ******************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]
Pausing for 120 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)

TASK [subclouds/specific : Wait for PLM configuration to complete] *****************************************************************************
ok: [welktxef-931887-rz-le0pts6-021]
included: /home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/tasks/unlock_node.yaml for welktxef-931887-rz-le0pts6-021

TASK [subclouds/specific : Check subcloud status before unlocking] *****************************************************************************
ok: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Unlock subcloud] ****************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Wait for node to restart (port 22 goes down)] ***********************************************************************
ok: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Wait for node be back up (port 5000 comes up)] **********************************************************************
ok: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Obtain Keystone auth token] *****************************************************************************************
ok: [welktxef-931887-rz-le0pts6-021 -> localhost]
FAILED - RETRYING: Wait for contoller-0 enabled (60 retries left).

TASK [subclouds/specific : Wait for contoller-0 enabled] ***************************************************************************************
ok: [welktxef-931887-rz-le0pts6-021 -> localhost]
included: /home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/tasks/create_nads.yaml for welktxef-931887-rz-le0pts6-021

TASK [subclouds/specific : Create working directory] *******************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : set_fact] ***********************************************************************************************************
ok: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Template NAD files into temp dir] ***********************************************************************************
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/templates/samsung/LS6_21D/NAD/adpf-ca-nad.yaml.j2)
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/templates/samsung/LS6_21D/NAD/adpf-f1c-nad.yaml.j2)
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/templates/samsung/LS6_21D/NAD/adpf-f1u-nad.yaml.j2)
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/templates/samsung/LS6_21D/NAD/adpf-fh0-nad.yaml.j2)
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/templates/samsung/LS6_21D/NAD/adpf-fh0m-nad.yaml.j2)
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/templates/samsung/LS6_21D/NAD/adpf-fh1-nad.yaml.j2)
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/templates/samsung/LS6_21D/NAD/adpf-fh1m-nad.yaml.j2)
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/templates/samsung/LS6_21D/NAD/adpf-fh2-nad.yaml.j2)
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/templates/samsung/LS6_21D/NAD/adpf-fh2m-nad.yaml.j2)
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/templates/samsung/LS6_21D/NAD/adpf-fh3-nad.yaml.j2)
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/templates/samsung/LS6_21D/NAD/adpf-fh4-nad.yaml.j2)
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/templates/samsung/LS6_21D/NAD/adpf-fh5-nad.yaml.j2)

TASK [subclouds/specific : Create NADs] ********************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]
included: /home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/tasks/create_rbac.yaml for welktxef-931887-rz-le0pts6-021

TASK [subclouds/specific : Create working directory] *******************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Template RBAC files into temp dir] **********************************************************************************
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/templates/samsung/rbac/rbac_ss_sa_new_install.yaml.j2)

TASK [subclouds/specific : Create RBACs] *******************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]
included: /home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/tasks/install_ptp_notification_app.yaml for welktxef-931887-rz-le0pts6-021

TASK [subclouds/specific : Add necessary labels to the host] ***********************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : set_fact] ***********************************************************************************************************
ok: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Upload ptp-notification app] ****************************************************************************************
fatal: [welktxef-931887-rz-le0pts6-021]: FAILED! => {"changed": true, "cmd": "source /etc/platform/openrc\nset -e\nsystem application-upload /usr/local/share/applications/helm/ptp-notification-21.05-49.tgz\n", "delta": "0:00:01.731680", "end": "2023-09-15 15:39:18.762140", "msg": "non-zero return code", "rc": 1, "start": "2023-09-15 15:39:17.030460", "stderr": "Error: Tar file /usr/local/share/applications/helm/ptp-notification-21.05-49.tgz does not exist", "stderr_lines": ["Error: Tar file /usr/local/share/applications/helm/ptp-notification-21.05-49.tgz does not exist"], "stdout": "", "stdout_lines": []}

PLAY RECAP *************************************************************************************************************************************
welktxef-931887-rz-le0pts6-021 : ok=72   changed=42   unreachable=0    failed=1    skipped=25   rescued=0    ignored=0

[XXXXXX@welktxefnce-h-pe1util-vm01 wrcp_post_deployment]$
[XXXXXX@welktxefnce-h-pe1util-vm01 wrcp_post_deployment]$
[XXXXXX@welktxefnce-h-pe1util-vm01 wrcp_post_deployment]$ ansible-playbook --vault-password-file /tmp/vault-pass -i inventory/ri_1.yaml wrcp_subcloud_post_deployment.yaml

PLAY [Post deployment steps fro WRCP subclouds] ************************************************************************************************

TASK [set vendor as samsung] *******************************************************************************************************************
ok: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : create vdu namespace] ************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]
included: /home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/generic/tasks/create_generic_resources.yaml for welktxef-931887-rz-le0pts6-021

TASK [subclouds/generic : Create working directory] ********************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : Template generic files into workdir] *********************************************************************************
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/generic/templates/samsung/generic/crd-role.yaml.j2)
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/generic/templates/samsung/generic/orchestration_sa_cluster.yaml.j2)
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/generic/templates/samsung/generic/orchestration_sa.yaml.j2)
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/generic/templates/samsung/generic/samsung_debug_sa.yaml.j2)
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/generic/templates/samsung/generic/ss_sa.yaml.j2)

TASK [subclouds/generic : Create generic resources] ********************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]
included: /home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/generic/tasks/create_k8s_files.yaml for welktxef-931887-rz-le0pts6-021

TASK [subclouds/generic : Create working directory] ********************************************************************************************
ok: [welktxef-931887-rz-le0pts6-021 -> localhost]

TASK [subclouds/generic : Get token for Orch - 21.05] ******************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : store orch token] ****************************************************************************************************
ok: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : Get token for SS Debug] **********************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : store ss token] ******************************************************************************************************
ok: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : print orch token] ****************************************************************************************************
ok: [welktxef-931887-rz-le0pts6-021] => {
    "orch_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6InRXNmJUVUxXVWN3Z2VKaXRJUFVUNTBJcG9YemtlRGF5QUpqSjc4cjBWVXMifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6Im9yY2hlc3RyYXRpb24tc2EtdG9rZW4tajJzN2QiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoib3JjaGVzdHJhdGlvbi1zYSIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6ImZhNmEwYzE5LWVlM2MtNDJmYy05NjYxLTI4NjJmMWExNWRmMCIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpkZWZhdWx0Om9yY2hlc3RyYXRpb24tc2EifQ.lXik-1doVawZLEEJCCaHNIg0Fsy_pw8Q-0GVEXZA6OgLNJKj6ED7ruYvJIOKeZwDfoTsUCSj3P9qBKbccxwa8sVl2OKXlN4NoAeBneCJS1Wfre_FDjVvAusCH5bGq-iPJGvtHHFas3DvrBwCPTfUJ9bvnBm0VOw0wGTdZ8NAqCyjQBYpxVWwAg9su6QGmltLrENfAzQBWZk91pj1lHxdiZu_zh-HYN3Q215Nxc3Cs9r1mbwvJk7vPG1DON8vYg9IyLSR5ZY4AoMNGA3-XLxxvOc3WaMABOgC63XGH_BxFp20W85RR6kjpWZVlJyuGOdasM5hQiCNryvqLqdBZExBaw"
}

TASK [subclouds/generic : print ss token] ******************************************************************************************************
ok: [welktxef-931887-rz-le0pts6-021] => {
    "ss_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6InRXNmJUVUxXVWN3Z2VKaXRJUFVUNTBJcG9YemtlRGF5QUpqSjc4cjBWVXMifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6InNhbXN1bmctc2EtdG9rZW4tcHZ2bGoiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoic2Ftc3VuZy1zYSIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6IjhmOWU2NDk1LWE5ZTMtNDVhNi1iN2NiLTZhYTZkZjY5MzY4MyIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpkZWZhdWx0OnNhbXN1bmctc2EifQ.CxYQq4CQ8l8yb0v5Fbvcu06kwibayMeUJx_SxdEAmh2hnmbUBfPUpWlSAznczSgR49Sa6GOahKDsNLeheb9KSTWkKFFHOEkYIeXTA4GUdDE8KavgnfgpyWFKzsaSCSp7GlHXrZl-p_F4jngJ5fwbtEjNh-WBpqfm0b_dR8EsrEfXvJzhNuICM8_2YUnCK6usfre9-Sts2AhNrJU9QzhPyK1ux-APhr6PDt-JILlmky05fGeQlZLWHvOqExKI4Ej6_Bxy4zbQmG0dyz82Axb8-anFaY5LZ0mdIO2AKExOASAEgpDuF4UO653bAkENN224aZ75WTWZv4emncH4qJ0qog"
}

TASK [subclouds/generic : Template k8s files into temp dir] ************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021 -> localhost] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/generic/templates/samsung/k8s/kubeconfig-orchestration.conf.j2)
changed: [welktxef-931887-rz-le0pts6-021 -> localhost] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/generic/templates/samsung/k8s/kubeconfig-samsung-debug.conf.j2)
included: /home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/generic/tasks/create_local_registry_secret.yaml for welktxef-931887-rz-le0pts6-021

TASK [subclouds/generic : Create secret in welktxef-931887vzwcvdu-y-ss-ls6-00000000021 for pulling from local registry] ************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : Create alternative secret in welktxef-931887vzwcvdu-y-ss-ls6-00000000021 for pulling from vudorch's own registry] ****
changed: [welktxef-931887-rz-le0pts6-021]
included: /home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/generic/tasks/update_platform_integ_apps.yaml for welktxef-931887-rz-le0pts6-021

TASK [subclouds/generic : Create working directory] ********************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : Template platform integ apps override file into temp dir] ************************************************************
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/generic/tasks/../templates/samsung/platform-integ/rbd-namespaces.yaml.j2)

TASK [subclouds/generic : Update platform integ apps] ******************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]
FAILED - RETRYING: Wait until application is out of the applying state (90 retries left).

TASK [subclouds/generic : Wait until application is out of the applying state] *****************************************************************
changed: [welktxef-931887-rz-le0pts6-021]
included: /home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/generic/tasks/store_ptp_notification_client_image.yaml for welktxef-931887-rz-le0pts6-021

TASK [subclouds/generic : set the correct tag for notificationclient-base image - up to 21.12] *************************************************
ok: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : Log in registry.central] *********************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : Pull ptp notification client image from registry.central] ************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : Log out from registry.central] ***************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : Tag ptp notification client image from registry.central] *************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : Log in registry.local] ***********************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : Push ptp notification client image to registry.local] ****************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : Log out from registry.local] *****************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/generic : Delete image from Docker cache] **************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : create vdu namespace] ***********************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]
included: /home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/tasks/lock_node.yaml for welktxef-931887-rz-le0pts6-021

TASK [subclouds/specific : Check subcloud status before locking] *******************************************************************************
ok: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Lock subcloud] ******************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]
Pausing for 10 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)

TASK [subclouds/specific : Pause for 10 seconds for the command to complete] *******************************************************************
ok: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Wait until subcloud is in locked status] ****************************************************************************
ok: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Display subcloud status] ********************************************************************************************
ok: [welktxef-931887-rz-le0pts6-021] => {
    "subcloud_status.stdout_lines": [
        "+----+--------------+-------------+----------------+-------------+--------------+",
        "| id | hostname     | personality | administrative | operational | availability |",
        "+----+--------------+-------------+----------------+-------------+--------------+",
        "| 1  | controller-0 | controller  | locked         | disabled    | online       |",
        "+----+--------------+-------------+----------------+-------------+--------------+"
    ]
}
included: /home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/tasks/system_configs_ls6.yaml for welktxef-931887-rz-le0pts6-021

TASK [subclouds/specific : Configure CPU] ******************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Configure sriov0] ***************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Configure sriov1] ***************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Configure fh0] ******************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Configure fh1] ******************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Configure fh2] ******************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Configure fh3] ******************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Configure fh4] ******************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Configure fh5] ******************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Configure ptp] ******************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Configure PLM] ******************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]
Pausing for 120 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)

TASK [subclouds/specific : Wait for PLM configuration to complete] *****************************************************************************
ok: [welktxef-931887-rz-le0pts6-021]
included: /home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/tasks/unlock_node.yaml for welktxef-931887-rz-le0pts6-021

TASK [subclouds/specific : Check subcloud status before unlocking] *****************************************************************************
ok: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Unlock subcloud] ****************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Wait for node to restart (port 22 goes down)] ***********************************************************************
ok: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Wait for node be back up (port 5000 comes up)] **********************************************************************
ok: [welktxef-931887-rz-le0pts6-021]
FAILED - RETRYING: Obtain Keystone auth token (60 retries left).

TASK [subclouds/specific : Obtain Keystone auth token] *****************************************************************************************
ok: [welktxef-931887-rz-le0pts6-021 -> localhost]

TASK [subclouds/specific : Wait for contoller-0 enabled] ***************************************************************************************
ok: [welktxef-931887-rz-le0pts6-021 -> localhost]
included: /home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/tasks/create_nads.yaml for welktxef-931887-rz-le0pts6-021

TASK [subclouds/specific : Create working directory] *******************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : set_fact] ***********************************************************************************************************
ok: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Template NAD files into temp dir] ***********************************************************************************
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/templates/samsung/LS6_21D/NAD/adpf-ca-nad.yaml.j2)
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/templates/samsung/LS6_21D/NAD/adpf-f1c-nad.yaml.j2)
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/templates/samsung/LS6_21D/NAD/adpf-f1u-nad.yaml.j2)
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/templates/samsung/LS6_21D/NAD/adpf-fh0-nad.yaml.j2)
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/templates/samsung/LS6_21D/NAD/adpf-fh0m-nad.yaml.j2)
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/templates/samsung/LS6_21D/NAD/adpf-fh1-nad.yaml.j2)
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/templates/samsung/LS6_21D/NAD/adpf-fh1m-nad.yaml.j2)
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/templates/samsung/LS6_21D/NAD/adpf-fh2-nad.yaml.j2)
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/templates/samsung/LS6_21D/NAD/adpf-fh2m-nad.yaml.j2)
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/templates/samsung/LS6_21D/NAD/adpf-fh3-nad.yaml.j2)
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/templates/samsung/LS6_21D/NAD/adpf-fh4-nad.yaml.j2)
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/templates/samsung/LS6_21D/NAD/adpf-fh5-nad.yaml.j2)

TASK [subclouds/specific : Create NADs] ********************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]
included: /home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/tasks/create_rbac.yaml for welktxef-931887-rz-le0pts6-021

TASK [subclouds/specific : Create working directory] *******************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Template RBAC files into temp dir] **********************************************************************************
changed: [welktxef-931887-rz-le0pts6-021] => (item=/home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/templates/samsung/rbac/rbac_ss_sa_new_install.yaml.j2)

TASK [subclouds/specific : Create RBACs] *******************************************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]
included: /home/XXXXXX/playbooks/etc/wrcp_post_deployment/roles/subclouds/specific/tasks/install_ptp_notification_app.yaml for welktxef-931887-rz-le0pts6-021

TASK [subclouds/specific : Add necessary labels to the host] ***********************************************************************************
changed: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : set_fact] ***********************************************************************************************************
ok: [welktxef-931887-rz-le0pts6-021]

TASK [subclouds/specific : Upload ptp-notification app] ****************************************************************************************
fatal: [welktxef-931887-rz-le0pts6-021]: FAILED! => {"changed": true, "cmd": "source /etc/platform/openrc\nset -e\nsystem application-upload /usr/local/share/applications/helm/ptp-notification-21.05-49.tgz\n", "delta": "0:00:01.687106", "end": "2023-09-15 18:42:21.865734", "msg": "non-zero return code", "rc": 1, "start": "2023-09-15 18:42:20.178628", "stderr": "Error: Tar file /usr/local/share/applications/helm/ptp-notification-21.05-49.tgz does not exist", "stderr_lines": ["Error: Tar file /usr/local/share/applications/helm/ptp-notification-21.05-49.tgz does not exist"], "stdout": "", "stdout_lines": []}

PLAY RECAP *************************************************************************************************************************************
welktxef-931887-rz-le0pts6-021 : ok=72   changed=42   unreachable=0    failed=1    skipped=25   rescued=0    ignored=0

[XXXXXX@welktxefnce-h-pe1util-vm01 wrcp_post_deployment]$

```