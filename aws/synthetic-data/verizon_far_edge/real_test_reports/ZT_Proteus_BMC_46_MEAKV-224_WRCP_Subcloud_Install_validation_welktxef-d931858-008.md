# ZT Proteus .46 BMC firmware validation
# ZT Proteus BIOS .23
# 1/29/24 James Patchett

## WRCP Subcloud deployment to test the various functions required with the BMC

## Target Controller rchltxib-c000000-003
Controller-0 iLO 2607:f160:a:d02e:cd:fe0::8006 
Controller-1 iLO 2607:f160:a:d02e:cd:fe0::8007
Worker-0 iLO 2607:f160:a:d02e:cd:fe0::8008 
OAM 2607:f160:0:3049:cd:290:0:10

## Target Subcloud welktxef-d931856-008
OAM: 2607:f160:10:80b1:ce:40a:0:f408
BMC: 2607:f160:10:80b1:ce:40a:0:e008

ipmitool -I lanplus -U XXXXXX -P XXXXXX -H 2607:f160:10:80b1:ce:40a:0:e008 sol activate


## Using our Ansible system to run the playbook to deploy the new subcloud.
## subcloud has been "disk wipped", powered off

```log
TASK [remote/remote-configure : Set facts for which image list to use based on WR version] **************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/remote-configure : Set facts for which image list to use based on WR version] **************************************
ok: [welktxef-931856-rz-le2pts6-008]

TASK [remote/remote-configure : Print wr_image_list] ****************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "msg": "wr_image_list: /opt/external/vcpfe-team/artifacts/WRCP-2112/wind-river-cloud-platform-container-images-list-21.12.txt"
}

TASK [remote/remote-configure : Set fact to wr_license_key] *********************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/remote-configure : Set fact to wr_license_key] *********************************************************************
ok: [welktxef-931856-rz-le2pts6-008]

TASK [remote/remote-configure : print wr_license_key] ***************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "msg": "wr_license_key = IyBXaW5kIFJpdmVyIFByb2R1Y3QgQWN0aXZhdGlvbiBGaWxlIChpbnN0YWxsLnR4dCkKIyBJc3N1ZWQgZm9yIGhvc3Q6IDxWZXJpem9uPiA8VmVyaXpvbj4gPEFueT4KIyBMaWNlbnNlIG51bWJlcihzKTogNjgyMzc0CiMgSXNzdWVkIG9uOiAyNi1qYW4tMjAyMiAwOTo1MDo1MAojCiMgTm90ZTogdGhpcyBsaWNlbnNlIGlzIGdlbmVyYXRlZCBjdW11bGF0aXZlbHkgZm9yIGFsbAojIFdpbmQgUml2ZXIgc29mdHdhcmUgbWFuYWdlZCBieSB0aGlzIGhvc3QuCgojIDEuIEZsZXhMTSBsaWNlbnNlIGZpbGU6CiMgQmVnaW46IFNlcnZlciBsaWNlbnNlICAtLS0tLS0tLS0tLS0tLS0tLS0tLS0KIyBTZXJpYWwgTnVtYmVyOiA2ODQ0NDktVmVyaXpvblBPQy1HNFdEQzlDUEVLCgpQQUNLQUdFIFdSQ1BfQ09OVEFJTkVSX1BLRyB3cnNkIDIxIDAwNDY1REZDRUI5QiBcCglDT01QT05FTlRTPVdSQ1BfQ09OVEFJTkVSOjIxLjEyIE9QVElPTlM9U1VJVEUgXAoJU0lHTj0yNTAwQzhCMjRFRDAKSU5DUkVNRU5UIFdSQ1BfQ09OVEFJTkVSX1BLRyB3cnNkIDIxIHBlcm1hbmVudCB1bmNvdW50ZWQgNDQyRThBMzg2QUE4IFwKCVZFTkRPUl9TVFJJTkc9PGxuPjY4MjM3NDwvbG4+PHBzPjIyMTMtNDM8L3BzPiBIT1NUSUQ9QU5ZIFwKCUlTU1VFRD0yNi1qYW4tMjAyMiBTTj1zZXJpYWwtVmVyaXpvbi1MVjJJV0FVTEVCIFwKCVNUQVJUPTI2LWphbi0yMDIyIFNJR049QjUzNzk2OTBENEE2Cg=="
}

TASK [remote/remote-configure : Copy storage checking script if server is HPE-LS3-e910] *****************************************
skipping: [welktxef-931856-rz-le2pts6-008] => (item=hpe_storage_check.py)

TASK [remote/remote-configure : Execute storage checking script if server is HPE-LS3-e910] **************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor HPE HPE-LS3-e910 (4 disks)] **************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor HPE HPE-LS3-e910 (2 disks)] **************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor HPE HPE-LS3-92s3] ************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor HPE HPE-LS6-92s6] ************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor ZTS ZTS-LS3-trtn] ************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/remote-configure : Set facts for Corning] **************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor ZTS ZTS-LS6-pts6 & ZTS-LS3-pts3] *********
ok: [welktxef-931856-rz-le2pts6-008]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor ZTS ZTS-LS6-aks6 & ZTS-LS3-aks3] *********
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/remote-configure : set_fact] ***************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008]

TASK [include_role : remote/zt-redfish] *****************************************************************************************

TASK [remote/zt-redfish : get content from /redfish/v1/Systems/Self] ************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/zt-redfish : Extract and store BiosVersion from returned content] **************************************************
ok: [welktxef-931856-rz-le2pts6-008]

TASK [remote/remote-configure : Set facts for BIOS version based on vendor ZTS ZTS-LS6-pts6 & ZTS-LS3-pts3] *********************
ok: [welktxef-931856-rz-le2pts6-008]

TASK [remote/remote-configure : debug] ******************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "bios_version": "0.23"
}

TASK [remote/remote-configure : Find out which DM Docker version contral has] ***************************************************
changed: [welktxef-931856-rz-le2pts6-008 -> rchltxib-c000000-003]

TASK [remote/remote-configure : Find out which DM file version contral has] *****************************************************
changed: [welktxef-931856-rz-le2pts6-008 -> rchltxib-c000000-003]

TASK [remote/remote-configure : Print dm docker version and dm file version] ****************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "msg": "dm_docker_version: WRCP_21.12-wrs.4, dm_file: wind-river-cloud-platform-deployment-manager-2.0.8-4.tgz"
}

TASK [remote/remote-configure : Discover Wind River docker image names] *********************************************************
changed: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/remote-configure : Print local_images_full] ************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "msg": "docker.io/starlingx/ceph-config-helper:v1.15.0\ndocker.io/starlingx/dex:stx.4.0-v2.14.0-1\ndocker.io/starlingx/n3000-opae:stx.6.0-v1.0.1\ndocker.io/starlingx/stx-oidc-client:stx.5.0-v1.0.4\ndocker.io/wind-river/cloud-platform-deployment-manager:WRCP_21.12-wrs.4\ngcr.io/google_containers/kubernetes-dashboard-init-amd64:v1.0.0\ngcr.io/kubebuilder/kube-rbac-proxy:v0.4.0\nquay.io/external_storage/rbd-provisioner:v2.1.1-k8s1.11"
}

TASK [remote/remote-configure : Create fact for Wind River docker image names] **************************************************
ok: [welktxef-931856-rz-le2pts6-008]

TASK [remote/remote-configure : Determine DM Helm Chart path] *******************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/remote-configure : Print dm_helm_chart] ****************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "msg": "/opt/external/vcpfe-team/artifacts/WRCP-2112/wind-river-cloud-platform-deployment-manager-2.0.8-4.tgz"
}

TASK [remote/remote-configure : Set DM Helm Chart file] *************************************************************************
ok: [welktxef-931856-rz-le2pts6-008]

TASK [remote/remote-configure : Lookup Deployment Manager image tag] ************************************************************
changed: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/remote-configure : Lookup RBAC Proxy image tag] ********************************************************************
changed: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/remote-configure : Copy WRCP DM Playbook] **************************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> rchltxib-c000000-003] => (item=wind-river-cloud-platform-deployment-manager.yaml)
ok: [welktxef-931856-rz-le2pts6-008 -> rchltxib-c000000-003] => (item=wind-river-cloud-platform-deployment-manager-2.0.8-4.tgz)

TASK [remote/remote-configure : Set a fact for the central controller VIP address] **********************************************
ok: [welktxef-931856-rz-le2pts6-008]

TASK [remote/remote-configure : Configure WRCP seed template] *******************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> rchltxib-c000000-003] => (item={'src': 'bootstrap-values.yaml', 'dest': 'welktxef-d931856-008-bootstrap-values.yaml'})
ok: [welktxef-931856-rz-le2pts6-008 -> rchltxib-c000000-003] => (item={'src': 'deploy-values.yaml', 'dest': 'welktxef-d931856-008-deploy-values.yaml'})
ok: [welktxef-931856-rz-le2pts6-008 -> rchltxib-c000000-003] => (item={'src': 'deploy-standard.yaml', 'dest': 'welktxef-d931856-008-deploy-standard.yaml'})
ok: [welktxef-931856-rz-le2pts6-008 -> rchltxib-c000000-003] => (item={'src': 'install-values.yaml', 'dest': 'welktxef-d931856-008-install-values.yaml'})

TASK [remote/remote-configure : Copy SSL cert files] ****************************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> rchltxib-c000000-003] => (item={'filename': 'k8s_root_ca_cert.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIF8jCCA9qgAwIBAgIJAIf9Ql2uDZh+MA0GCSqGSIb3DQEBDQUAMIGFMQswCQYD\nVQQGEwJVUzEOMAwGA1UECAwFVGV4YXMxETAPBgNVBAcMCFdlc3RsYWtlMR0wGwYD\nVQQKDBRWZXJpem9uIFNvdXJjaW5nIExMQzE0MDIGA1UEAwwrVmVyaXpvbiBOZXR3\nb3JrIFdFTEtUWElCIExBQiAxIDMgUlNBIEs4UyBDQTAeFw0yMDEwMjUyMjEyNDha\nFw0zMDEwMjMyMjEyNDhaMIGFMQswCQYDVQQGEwJVUzEOMAwGA1UECAwFVGV4YXMx\nETAPBgNVBAcMCFdlc3RsYWtlMR0wGwYDVQQKDBRWZXJpem9uIFNvdXJjaW5nIExM\nQzE0MDIGA1UEAwwrVmVyaXpvbiBOZXR3b3JrIFdFTEtUWElCIExBQiAxIDMgUlNB\nIEs4UyBDQTCCAiIwDQYJKoZIhvcNAQEBBQADggIPADCCAgoCggIBAKyF9svdv/qG\n7HxBr1DWvZ3CQiDsA4m1kj0hD7jo3B3W/32ODcPpgeNmp4Oful0SsndpqEGhXDq5\noiBfqszMUpzDgdQ7siIHekb2olFEK2KniMP3H53nilIppeyMby5K3ZwF0Qbmk5WK\ncoXoYegP+Uv9bV0AMH6Dn4CVgYrLAYfmPyGgUSt4vuZ9F/rf9UkBf/DcZGqMnMax\n/Gfaq8KwmDzD9D8IVCHPrM5f4+CaKMQCFu5QkSsLYJFRiuQWWaICMMdnqpb0HZh5\niPnCSHwPPUyXxtujdI97Ovy4X5WR46jJ2+KzPYe8tVa/DL3TlKmRL9AF+oSE17bw\nzGAE7GNWxPojebHIUuoKdOQC1qiJBVS+c14r9+9P2Uy6XEhNUs+h3juRI4U3YkQ1\nUCUU3opqhOPh4jUIuPGg5aX07lt4Wpxc48D+CY1D4i6vaJLl3WCsVK7PFwWVQQEW\nIQabfuj1R2jEu7pp2Yabza58S00v1P5/kv/DNr7ADm8eYRvxLAAXCedMeSDXKBgd\npPmVXXZoZ8+X8VRGYxcw0mBBLIAiTOntT2vgLeq5T3QyiVKdU6TLAYEjS65QZ3Eg\naIX0wRqlcQI7lruTXubtENG6wWXYtnDf5795ZID1YIEqkgzZLMBqq1SBiLnWd6aK\n78Zsr4j5GmTBGpKRmwE2oO1btJCCYyG5AgMBAAGjYzBhMA8GA1UdEwEB/wQFMAMB\nAf8wHQYDVR0OBBYEFEDQ5EaGp3x02WUuvqetygqpM3dCMB8GA1UdIwQYMBaAFEDQ\n5EaGp3x02WUuvqetygqpM3dCMA4GA1UdDwEB/wQEAwICpDANBgkqhkiG9w0BAQ0F\nAAOCAgEAeCMxVJr5Jyg87DVaUtEhiWfhto993ENrnevAGqrBOoRc/KU1/C3paqhR\nsvr2r2LR+npSmeo6iz0FaO31XwHSHX95+XJeGP5Q8TGddbRiTglQsMfOkGNzxqgg\nTkdZ8A1y9v2jprONUmLADVGIVT0AoHc7V9w1I8NKhrY+rIllum4FRDiDPSnImh5h\nxmH+Nq2ZuEFVdtV/oNKzEu2ywmbgBRd5Jv3rTejxltmTZtyq8IKoKguj3NVFn93Q\nU4TbsxkcAdrLMooLYYDRTWA4t0iqKM/UkYUg4xl2l9NrY7ZUbaNd5+YsLNdqXO/c\nmp7wyMv/8ZIy1BLG4zJmX/JzWkYmULqQ+A+21+YuqrV3a81V7vcHhJcRaPOrg5cd\nYwY2eCbXMvNOdrzppIglUrlddNuqAhs1MTi/VibxYuI9isU0JckXIcCy1L+xbEda\n6v/z6wSrScVz0I4m0DpK6xMQ8t9sLcrGp5uGbj6J4nQWd+QLdq6kmAzDOZ/Gs0wb\nPYdkER4dXAVcioYFekpKv7d+nur0FPtMNIw0OdhX2eAwC22IFAq2DZRjUFvaBGaD\ni1ptfq6P1mVJ2T/exYujEDtq+8yQTfWgFm/DjEfWtcCp0Jukgv8opLR2DpCf5Ucq\nd5X7d/DP0mukJ3vZ8EIqYorwZJ1L1a2jgngjA+gPxIaW+JHfTHU=\n-----END CERTIFICATE-----\n'})
ok: [welktxef-931856-rz-le2pts6-008 -> rchltxib-c000000-003] => (item={'filename': 'k8s_root_ca_key.pem', 'value': '-----BEGIN PRIVATE KEY-----\nMIIJQQIBADANBgkqhkiG9w0BAQEFAASCCSswggknAgEAAoICAQCshfbL3b/6hux8\nQa9Q1r2dwkIg7AOJtZI9IQ+46Nwd1v99jg3D6YHjZqeDn7pdErJ3aahBoVw6uaIg\nX6rMzFKcw4HUO7IiB3pG9qJRRCtip4jD9x+d54pSKaXsjG8uSt2cBdEG5pOVinKF\n6GHoD/lL/W1dADB+g5+AlYGKywGH5j8hoFEreL7mfRf63/VJAX/w3GRqjJzGsfxn\n2qvCsJg8w/Q/CFQhz6zOX+PgmijEAhbuUJErC2CRUYrkFlmiAjDHZ6qW9B2YeYj5\nwkh8Dz1Ml8bbo3SPezr8uF+VkeOoydvisz2HvLVWvwy905SpkS/QBfqEhNe28Mxg\nBOxjVsT6I3mxyFLqCnTkAtaoiQVUvnNeK/fvT9lMulxITVLPod47kSOFN2JENVAl\nFN6KaoTj4eI1CLjxoOWl9O5beFqcXOPA/gmNQ+Iur2iS5d1grFSuzxcFlUEBFiEG\nm37o9UdoxLu6admGm82ufEtNL9T+f5L/wza+wA5vHmEb8SwAFwnnTHkg1ygYHaT5\nlV12aGfPl/FURmMXMNJgQSyAIkzp7U9r4C3quU90MolSnVOkywGBI0uuUGdxIGiF\n9MEapXECO5a7k17m7RDRusFl2LZw3+e/eWSA9WCBKpIM2SzAaqtUgYi51nemiu/G\nbK+I+RpkwRqSkZsBNqDtW7SQgmMhuQIDAQABAoICACysO62qa+2pRk8eixD5qfvR\ns2Hm+zuLYqSljPaqhWTMqTePswzJyDJkAHhawd0b3E6Dc2gbKlCihNKxMv744WNq\nVJHqK0QYf5ckgf9dEYboLsffk7ZFoFGKK0bHTnrENAIUl32b8xdD1EfMVp3KlRkS\nNGFijSwVVRXsoLCZxHm2Kx6/7oS9LWFtfuodV9xhoQlzaCUW5/mjWOJjgxpUs/b4\nHqS7uV1P80U1G0KraGboy5tGDXEB7y1x2e8Zwnfq7UqVE10nNQqoXcmefzpwj8Tn\ngDybZLFKjYmnDEkkj7jDHEbldsdRG/usWNZGlTYbPDA3fBkYdOsQCzvJypQmgbZ+\n3yk3Lj2+9vLEMfPrruuzyOSXgki6o5uvy7Je6PdBpsz75k8FH6a+Rw3vvP8HuP3S\nLSUYm3tyOheXHR7BKN4bnfi11RAWvDpT9S+QnZ+R8DmQzOADlnjRC8WewDJYoNJ1\np1jeuqswlxo144oMO92cmdS2dAbPvS6aQP1I85Q2NniY+6YhHkBwIQIlfVs1JPbY\nX7QtTy1IXQhR3sospyvUwY2GPSAeVHDRL53ClQKDsvWpSy0MAmWYJkZu1P+jKBim\nj34ytApgG65Hv/RHf3L4+4zzItZ3TN2tJ/g9EKc6oMNtqKbbG56kkmvRPWKtMGV8\nFqxCvG5NydUK7fN+P2WJAoIBAQDXLFC//Fn9ed1U+pKa2M25aJwEetkGLXQvkwVi\n8uJFaXITb2ceveSEo6iBExyn4eYL5A4X+RZdJJdRRbj4whsNN13Pm+6lYX3pp7MN\nO+78uvwVfKZiWPFKfZs7ZH1/O9VIlLGnXUHeaHK1tmv9ixxMixdnjUDkcVa0O3qT\nKBLpvXnVEMYizxQBN0P5Z9QvQQGpUhKnNw+FhV1SP+YHxrB0Pu6qbYAmZZC2MQc1\nTsDyqGjmHk9VJaFYAAPEjqACDbfnkVUCj0ylM4xPQuBJs9DOKh4InG+znusdmd8H\nmvoEFDppsrH1NhO6GTeuCk6n0WBi6cUm76K/gPscYyV4ZtkfAoIBAQDNQgDXtfqv\nxbAhvDk0o/P8fqOdgQF0uFTqYHmyW31Ty9nF0ptA8LVJOIljU3zlLplhIFjBnSEG\nLqu4jnLLRR+zej0MXmJuZ9BMWmQeTrZzttnH5bn54E07DPJ5BvFoTMJNklBiXjB5\n5hTPZS4yK1KjoxY+Ypnj4W1iZjP37ya/A34J2nlYtoW4LdVfJHqCxBXel9Nz2zkv\nvwwPu8Eu7gFLuhNQM6Iv4mORGI8yg7Y/BwodfDPRuFvrG1KXkjwASb0O5b1suRQy\n9H80q5EAbT36K1z48ilr8fcroN+hV8g4yntrBBgOHPMmBk/vHKU8B1rkBr0p2haI\n3PwKmDFRsDInAoIBAGrjjMmSZnHQk+6e+y0I/klYegiPrjevZMQtWMOqvFSW6SBW\nevd+hYKOeiqEf/u18D1/8LBgAIgMoU6yQAzy/9U059k2MPrez1m/AOdWGoZZrNhP\nr6ezX0oN04tRhDYsVutTUl09qnb9k95I3KR68nfjsKC0PsQ8uUGXOnDXu215vofl\naUfpbpqcBZxjw7glptmh97oxU/iUI6O0MmUygn18tbrb4okwcw7OlDIbCSaCGnoW\nHHrD0r6QY07FOx9KCU1zmLNI1F5MmSrWoex68wM3UOweKi8khs+RnIV+qyxTkCDp\nsBWL44jS9iHy5Nfg3uzEDDgnWsWfIR8c8YQ6MykCggEADr0ollTI9Yo6hZGggfkr\n8fueABddZWY/Ir1ev8H2E+hVcPEYmOcv/VwD8Y/zLfnUpbbO6MhBsNH1HsGL2LDT\n/+1NKPA2HTtzJ6ht/Acm7tQ4ezQx0JGcuhrJ5orrFtQ8N5nED+w3iulMoT/gu1WF\nD58MX9pwtn5ffmtcW/deTuUPTeHUSNyCaaFQ6w4RhgZSk7NPSch6KMWNNiwDST1p\n9mgcLuwmP04AXFDpJ3VxxsDYpxleFzcn0pAZtCyaBmNFIia5HW+E1cvcvol7Vg6C\nHs6yVGX/N3MejpF0vX8yL3HKvvqCR7EofJiDcOYbr13P1wPs3W59o8JKjvAyymze\njQKCAQAUY/0asRL33D7tFoIbLg/N9hi+tCCM35DMf2FeXm3QwSkAR/BJw0ewCE5C\n+VqukHN3/i0Xe8KSHwEuLK2sGLk9Ys8A5NytjqFApYwpIk8UrRONfC12H3ez5VYk\nJlhMVhVXEZvVhEFJiBC7q6x6s7BVtLTGV7FA5CW8YKBhwHwrpm+h/Xb798oaKyel\nP/xYq+GZzfWfbvUjZvgN0J0RGxKA+GRgsmhoyOfgCVXgSzuUkI+9cAUvC0OV407L\n4XIK0GDJ7Tv/2USSPfmueyGEmacc/oYUPVBUgeINSoaCM4cpZwyLylVEtKOdQoEE\n77G5mvQsoXxsMjd+nbHil450UHsL\n-----END PRIVATE KEY-----\n'})

TASK [Proteus MWIAT - ENABLE] ***************************************************************************************************

TASK [remote/zt-redfish : Update Attributes at /redfish/v1/Systems/Self/Bios/SD] ************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/zt-redfish : Update result] ****************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "update_result": {
        "allow": "GET, PUT, PATCH, POST",
        "changed": false,
        "connection": "close",
        "content": "",
        "cookies": {},
        "cookies_string": "",
        "date": "Tue, 30 Jan 2024 02:25:30 GMT",
        "elapsed": 0,
        "failed": false,
        "msg": "OK (unknown bytes)",
        "redirected": false,
        "server": "AMI MegaRAC Redfish Service",
        "status": 204,
        "url": "https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/Systems/Self/Bios/SD"
    }
}

TASK [Remote Install] ***********************************************************************************************************

TASK [remote/remote-install : Check if the subcloud deployed but failed] ********************************************************
fatal: [welktxef-931856-rz-le2pts6-008 -> rchltxib-c000000-003]: FAILED! => {"changed": true, "cmd": ". /etc/platform/openrc\ndcmanager subcloud show welktxef-d931856-008 --column \"deploy_status\" --format value\n", "delta": "0:00:01.194805", "end": "2024-01-30 02:25:33.615468", "msg": "non-zero return code", "rc": 1, "start": "2024-01-30 02:25:32.420663", "stderr": "ERROR (app) Subcloud not found", "stderr_lines": ["ERROR (app) Subcloud not found"], "stdout": "", "stdout_lines": []}
...ignoring

TASK [remote/remote-install : debug] ********************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "msg": "subcloud_status:"
}

TASK [remote/remote-install : Delete the subcloud that's 'install-failed' & 'pre-install-failed'] *******************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/remote-install : Deploy remote cloud] ******************************************************************************
changed: [welktxef-931856-rz-le2pts6-008 -> rchltxib-c000000-003]

TASK [remote/remote-install : 1st polling prep: Obtain Keystone auth token] *****************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/remote-install : 1st polling: Wait for subcloud to start installing OS] ********************************************
FAILED - RETRYING: 1st polling: Wait for subcloud to start installing OS (40 retries left).
FAILED - RETRYING: 1st polling: Wait for subcloud to start installing OS (39 retries left).
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/remote-install : 1st polling result: Fail if the installation failed] **********************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/remote-install : 2nd polling prep: Obtain Keystone auth token] *****************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/remote-install : 2nd polling: Wait for subcloud to install OS (this will take a while)] ****************************
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
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (49 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (48 retries left).
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/remote-install : 2nd polling result: Fail if any error occurred] ***************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/remote-install : 3rd polling prep: Obtain Keystone auth token] *****************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/remote-install : 3rd polling: Wait for subcloud to install OS (this may take a while)] *****************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/remote-install : 3rd polling result: Fail if any error occurred] ***************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/remote-install : 4th polling prep: Obtain Keystone auth token] *****************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/remote-install : 4th polling: Wait for subcloud to install OS (this may still take a while)] ***********************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/remote-install : 4th polling result: Fail if the installation failed] **********************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/remote-install : 5th polling prep: Obtain Keystone auth token] *****************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/remote-install : 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while)] **********
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
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/remote-install : 5th polling result: Fail if bootstrap/deploy failed] **********************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/remote-install : 6th polling prep: Obtain Keystone auth token] *****************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/remote-install : 6th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while)] **********
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/remote-install : 6th polling result: Fail if bootstrap/deploy failed] **********************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/remote-install : Wait for controller-0 restart] ********************************************************************
FAILED - RETRYING: Wait for controller-0 restart (40 retries left).
FAILED - RETRYING: Wait for controller-0 restart (39 retries left).
FAILED - RETRYING: Wait for controller-0 restart (38 retries left).
fatal: [welktxef-931856-rz-le2pts6-008]: FAILED! => {"attempts": 4, "changed": false, "elapsed": 5, "msg": "timed out waiting for ping module test success: Failed to connect to the host via ssh: ssh: connect to host 2607:f160:10:80b1:ce:40a:0:f408 port 22: Connection refused"}
...ignoring

TASK [remote/remote-install : Wait for controller-0 recovery] *******************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/remote-install : setup kdump] **************************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [Remote Cleanup] ***********************************************************************************************************

TASK [common/cleanup : Remove temporary working directory] **********************************************************************
changed: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [Remote Manage] ************************************************************************************************************

TASK [remote/manage : 1st Obtain Keystone auth token] ***************************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/manage : 1st Wait for contoller-0 availability status online] ******************************************************
FAILED - RETRYING: 1st Wait for contoller-0 availability status online (100 retries left).
FAILED - RETRYING: 1st Wait for contoller-0 availability status online (99 retries left).
FAILED - RETRYING: 1st Wait for contoller-0 availability status online (98 retries left).
FAILED - RETRYING: 1st Wait for contoller-0 availability status online (97 retries left).
FAILED - RETRYING: 1st Wait for contoller-0 availability status online (96 retries left).
FAILED - RETRYING: 1st Wait for contoller-0 availability status online (95 retries left).
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/manage : 2nd Obtain Keystone auth token] ***************************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/manage : 2nd Wait for contoller-0 availability status online] ******************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/manage : Wait for system to stabilize before running kubectl] ******************************************************
Pausing for 480 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [welktxef-931856-rz-le2pts6-008]

TASK [Wait for distributed cloud to be reconciled] ******************************************************************************

TASK [common/wait_for_reconciliation : Making sure node is reachable] ***********************************************************
ok: [welktxef-931856-rz-le2pts6-008]

TASK [common/wait_for_reconciliation : Wait for K8s API to be up] ***************************************************************
ok: [welktxef-931856-rz-le2pts6-008]

TASK [common/wait_for_reconciliation : Wait for hosts to be reconciled] *********************************************************
changed: [welktxef-931856-rz-le2pts6-008]

TASK [common/wait_for_reconciliation : Wait for systems to be reconciled] *******************************************************
changed: [welktxef-931856-rz-le2pts6-008]

TASK [remote/manage : Wait for distributed cloud to be reconciled but subcloud OAM VIP becomes unreachable] *********************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/manage : Check if the subcloud deployed but failed] ****************************************************************
changed: [welktxef-931856-rz-le2pts6-008 -> rchltxib-c000000-003]

TASK [remote/manage : Set distributed cloud state to managed] *******************************************************************
changed: [welktxef-931856-rz-le2pts6-008 -> rchltxib-c000000-003]

TASK [remote/manage : Wait for system to stabilize] *****************************************************************************
Pausing for 300 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [welktxef-931856-rz-le2pts6-008]

TASK [Remote Trust] *************************************************************************************************************

TASK [remote/trust : Create temporary working directory] ************************************************************************
changed: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/trust : Copy SSL cert files to working dir] ************************************************************************
changed: [welktxef-931856-rz-le2pts6-008 -> localhost] => (item={'filename': 'k8s_root_ca_cert.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIF8jCCA9qgAwIBAgIJAIf9Ql2uDZh+MA0GCSqGSIb3DQEBDQUAMIGFMQswCQYD\nVQQGEwJVUzEOMAwGA1UECAwFVGV4YXMxETAPBgNVBAcMCFdlc3RsYWtlMR0wGwYD\nVQQKDBRWZXJpem9uIFNvdXJjaW5nIExMQzE0MDIGA1UEAwwrVmVyaXpvbiBOZXR3\nb3JrIFdFTEtUWElCIExBQiAxIDMgUlNBIEs4UyBDQTAeFw0yMDEwMjUyMjEyNDha\nFw0zMDEwMjMyMjEyNDhaMIGFMQswCQYDVQQGEwJVUzEOMAwGA1UECAwFVGV4YXMx\nETAPBgNVBAcMCFdlc3RsYWtlMR0wGwYDVQQKDBRWZXJpem9uIFNvdXJjaW5nIExM\nQzE0MDIGA1UEAwwrVmVyaXpvbiBOZXR3b3JrIFdFTEtUWElCIExBQiAxIDMgUlNB\nIEs4UyBDQTCCAiIwDQYJKoZIhvcNAQEBBQADggIPADCCAgoCggIBAKyF9svdv/qG\n7HxBr1DWvZ3CQiDsA4m1kj0hD7jo3B3W/32ODcPpgeNmp4Oful0SsndpqEGhXDq5\noiBfqszMUpzDgdQ7siIHekb2olFEK2KniMP3H53nilIppeyMby5K3ZwF0Qbmk5WK\ncoXoYegP+Uv9bV0AMH6Dn4CVgYrLAYfmPyGgUSt4vuZ9F/rf9UkBf/DcZGqMnMax\n/Gfaq8KwmDzD9D8IVCHPrM5f4+CaKMQCFu5QkSsLYJFRiuQWWaICMMdnqpb0HZh5\niPnCSHwPPUyXxtujdI97Ovy4X5WR46jJ2+KzPYe8tVa/DL3TlKmRL9AF+oSE17bw\nzGAE7GNWxPojebHIUuoKdOQC1qiJBVS+c14r9+9P2Uy6XEhNUs+h3juRI4U3YkQ1\nUCUU3opqhOPh4jUIuPGg5aX07lt4Wpxc48D+CY1D4i6vaJLl3WCsVK7PFwWVQQEW\nIQabfuj1R2jEu7pp2Yabza58S00v1P5/kv/DNr7ADm8eYRvxLAAXCedMeSDXKBgd\npPmVXXZoZ8+X8VRGYxcw0mBBLIAiTOntT2vgLeq5T3QyiVKdU6TLAYEjS65QZ3Eg\naIX0wRqlcQI7lruTXubtENG6wWXYtnDf5795ZID1YIEqkgzZLMBqq1SBiLnWd6aK\n78Zsr4j5GmTBGpKRmwE2oO1btJCCYyG5AgMBAAGjYzBhMA8GA1UdEwEB/wQFMAMB\nAf8wHQYDVR0OBBYEFEDQ5EaGp3x02WUuvqetygqpM3dCMB8GA1UdIwQYMBaAFEDQ\n5EaGp3x02WUuvqetygqpM3dCMA4GA1UdDwEB/wQEAwICpDANBgkqhkiG9w0BAQ0F\nAAOCAgEAeCMxVJr5Jyg87DVaUtEhiWfhto993ENrnevAGqrBOoRc/KU1/C3paqhR\nsvr2r2LR+npSmeo6iz0FaO31XwHSHX95+XJeGP5Q8TGddbRiTglQsMfOkGNzxqgg\nTkdZ8A1y9v2jprONUmLADVGIVT0AoHc7V9w1I8NKhrY+rIllum4FRDiDPSnImh5h\nxmH+Nq2ZuEFVdtV/oNKzEu2ywmbgBRd5Jv3rTejxltmTZtyq8IKoKguj3NVFn93Q\nU4TbsxkcAdrLMooLYYDRTWA4t0iqKM/UkYUg4xl2l9NrY7ZUbaNd5+YsLNdqXO/c\nmp7wyMv/8ZIy1BLG4zJmX/JzWkYmULqQ+A+21+YuqrV3a81V7vcHhJcRaPOrg5cd\nYwY2eCbXMvNOdrzppIglUrlddNuqAhs1MTi/VibxYuI9isU0JckXIcCy1L+xbEda\n6v/z6wSrScVz0I4m0DpK6xMQ8t9sLcrGp5uGbj6J4nQWd+QLdq6kmAzDOZ/Gs0wb\nPYdkER4dXAVcioYFekpKv7d+nur0FPtMNIw0OdhX2eAwC22IFAq2DZRjUFvaBGaD\ni1ptfq6P1mVJ2T/exYujEDtq+8yQTfWgFm/DjEfWtcCp0Jukgv8opLR2DpCf5Ucq\nd5X7d/DP0mukJ3vZ8EIqYorwZJ1L1a2jgngjA+gPxIaW+JHfTHU=\n-----END CERTIFICATE-----\n'})
changed: [welktxef-931856-rz-le2pts6-008 -> localhost] => (item={'filename': 'vz_root_ca_cert.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIFpTCCA42gAwIBAgIUa3vZ0YGxO1TQ8NwhiVfQC0JslXgwDQYJKoZIhvcNAQEL\nBQAwWjELMAkGA1UEBhMCVVMxEDAOBgNVBAoMB1Zlcml6b24xEzARBgNVBAsMClZa\nSUFNIFRlc3QxJDAiBgNVBAMMG1Zlcml6b24gTmV0d29yayBSU0EgQ0EgVGVzdDAe\nFw0yMDA2MTUyMTAxMTNaFw0zNTA2MTUyMTAxMTNaMFoxCzAJBgNVBAYTAlVTMRAw\nDgYDVQQKDAdWZXJpem9uMRMwEQYDVQQLDApWWklBTSBUZXN0MSQwIgYDVQQDDBtW\nZXJpem9uIE5ldHdvcmsgUlNBIENBIFRlc3QwggIiMA0GCSqGSIb3DQEBAQUAA4IC\nDwAwggIKAoICAQC8AIrksI57CbIl5uGZ6yqfpQj3aK+N8f1EVHdwK9JFskoipvC8\n7yFTk8tgmO1i0YA5oRGfNxneqCdrXZiWL6Ko8v/iln9vuN+2rK3rgWZPPRJBAsBN\na49L7U6lJjIGxIZtZqmK5h47oiUtwlYVrbZMN2ijuBQ22/eQ9tsFDV28oBuZ3WAR\npSSbj/tubPQYkw3YYOhv/VpEpsd0rkoEt3QCmTVcX2rtblanpXowTV5R0Hy4014n\nT49jrEo40r4mwYoyS835Uv4ENUFA+pXicT9eUot3RSH6rYdx4A/14UtoI9U0ol8M\n62GHpxSASQ2Kc3yQWvxRGTFslTduYM+vVmMLEDDdqcsjYnStPpwdxxmKItmbjxSv\nIwYIndp8A04WkX2iiJCciC3BNxiLamPtYVyB1HHqbGTGirKYuSvwZt337q1OI3WH\nwVn2S4Mj/wqa4iCyGTvFSUnGq34Xkrb9XNwWBok9Tc2XWGAU/mb/xcd1hX74GZbF\nsrZ11aPtym4kMAjU2KQi96GcAH2lnGZYoOja1J4Cs4WYx1uAx74H/m84CrYavVfl\n1ONJVLDfuZaEkSmu+jHQX15pAECNORTuLD06PbWnOEcOi1xmbt/OT3SA3rhD2mb7\n2wxl7oJpV3ap8xGwYmxiFzmInxFJ1axjg8Rimol0mXTKAy6OdNHbCOnAwwIDAQAB\no2MwYTAPBgNVHRMBAf8EBTADAQH/MA4GA1UdDwEB/wQEAwIBBjAfBgNVHSMEGDAW\ngBQleng3lqGBeTrbLVuABoEmUHm1+TAdBgNVHQ4EFgQUJXp4N5ahgXk62y1bgAaB\nJlB5tfkwDQYJKoZIhvcNAQELBQADggIBADQ9jpmVh9nyY7ZQ4s+S9RuSRYn7QsrW\nDePeMzQgh8ZtS8WE65GY5HS61iHNP2Co8Q1lAaBWF4ipq+VZOcQbPLccHzd1kZv4\ns4u0aTzBd9ccidl73FS0DJDQOBbzPSzgsaiGHSMyGzkTeA8z3ntsSqrXXcDUvoRi\nFus/110AwdtNhJLrWveX6btYtHp9Lqe0YtNCy5AaXlrr1yRSckP5BWVtlwD4dzSO\n/dqI3wHS/ncUx9wSQomZ+AmxYW3KtJQKgHzTqHru1x9BBk7Bzfz9FZr6HLLmEitj\nuFoDRd5TNt5LbO0zDQokvY3oqso6Htup/rS7C08mcmnelYE+yXuOc1YrlyGnpBzk\nmy+1VYbOxRRdqKAZRbE72u/h847IVpsOvjR51iksuCAurZdp2+y2zvV8NhWekuNy\nirECRy9cb4YasjRaKi0/TCGPVSICuLyeG2W72liCj/N2VKfjPP9zsOR5XjwCXfRg\n+9xhLy77/gov2NWXx5fzTkhxCrHOxFdLVMn0wQhksDmw6QsXzDIHSpIOypdDfnx9\nCsthx3nhkuHLUaEP22D22dG+vImA9ukj4R/RRI/87jmi9Q8+ehH+NqN0GZZcLjdN\nSLVXpncuwWQFUDPR06wNkkkmBSXWiIYhwqSpU0Pl3er3fD0uWvXuWPm2PzfOmUAE\nUrkzyw9XmLw0\n-----END CERTIFICATE-----\n'})
changed: [welktxef-931856-rz-le2pts6-008 -> localhost] => (item={'filename': 'vz_root_ica_cert.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIFNzCCAx+gAwIBAgIUGLJR/hP48n+vdq2v1hcfspXo/78wDQYJKoZIhvcNAQEL\nBQAwWjELMAkGA1UEBhMCVVMxEDAOBgNVBAoMB1Zlcml6b24xEzARBgNVBAsMClZa\nSUFNIFRlc3QxJDAiBgNVBAMMG1Zlcml6b24gTmV0d29yayBSU0EgQ0EgVGVzdDAe\nFw0yMDEwMjIyMTE0MDNaFw0zMDEwMjIyMTE0MDNaMIGRMQswCQYDVQQGEwJVUzEL\nMAkGA1UECAwCVFgxETAPBgNVBAcMCFdlc3RsYWtlMRAwDgYDVQQKDAdWZXJpem9u\nMR0wGwYDVQQLDBRWZXJpem9uIFNvdXJjaW5nIExMQzExMC8GA1UEAwwoVmVyaXpv\nbiBOZXR3b3JrIFdFTEtUWElCIExBQiAxIDMgUlNBIElDQTCCASIwDQYJKoZIhvcN\nAQEBBQADggEPADCCAQoCggEBANhkGTXOCKEYf5znDDeX3n/DHFPVqazgQsr0/SIG\n4eb1JY5q5Jq3ZhAaZCr9HJuCkwAP/zgYH0llqOvf8AC2Uh+7z1b33IbwxPmJfWCP\nAqSNFkLWWVRdbELapCu408QsrLMW8IrdP6PLiKAepwncfm4T0/6bANqIEmUkpw8Q\nxProeiNwlGbwUll+tELmdCk7vA7hKX3j1kUvS5Z84Z5ivJBWEcUEggmC97TK4aLo\nFVEHbyahze568JVEaM1vY5L4mnRRTl+u5ipaSMxVBsiXzF7eFuKCzqF7wxbDIt2T\nIFEJtwyJDW5bXjyXgiF1d5H/URprUcRV9Qmf2+PXcfwHII8CAwEAAaOBvDCBuTAS\nBgNVHRMBAf8ECDAGAQH/AgEAMA4GA1UdDwEB/wQEAwIBBjAfBgNVHSMEGDAWgBQl\neng3lqGBeTrbLVuABoEmUHm1+TBTBgNVHR8ETDBKMEigRqBEhkJodHRwOi8vc2Vj\ndXJlLnN0YWdpbmcuc2VjdXJpdHljcmVkZW50aWFsaW5nLmNvbS9jcmwvdnpuZXRy\nc2FjYS5jcmwwHQYDVR0OBBYEFP0Z+/vaDLtAoFig1I9ttNKnmzByMA0GCSqGSIb3\nDQEBCwUAA4ICAQBuXVTf9e01HeymHgRcFCwP2N6G6u+vIzY8Bz0zSUZeRDHMZQcS\nNoabDyn5FfGJlw4BqGC591Sp0/unFQDzAg17rDBcrgwajeFeUiFdb9PiAJwHaX9S\nvq/7VmVLCmpeb+a/laXAe6+tkY1kcFrd1+ItRKC6ZGXMsoDkmk5Ndxxgw77estcI\nMiiLQbvpXRygX5wD4/ayazuLms9qITZkOZ1nTLVqq7QrwYCsSoih7hj6sbsfXr19\nGoYWmk8Y7O/d3ttgyHuRH9k/2dQ/xL7avRpMNkPdr7ocJqI46hvx2X6UyOo7IBua\nkSkFbSmPZWIVAidNMBOnvffCQ32tfjT2/xso/a9cdskvxqgLi0MPARU9Nl2Pufsb\nD7l4/sBvz/PiNTKp+Daa9FdyLb9ySidos1uS0c24bUtY1RXXGAVV2qgfyrzvzfye\nSM+w16hMU/yeYiuA1jsPmsnZnuIJj4Nv8ZjjZ0WS53pP5wcghaHkBrqWQNT8meqA\nVElrMBPlYq67T+AXP0B9lf5Sc3QVIio7XKKfqrlcQxY2JGLEyE53JgZGX7dpwU4I\nukLvyHbT4p06oY3qG6+wH8+YIXCNAYtadJ/C5/u9GcLX5NnZrcuduj0inw2/a3Ao\nWgCt6/Pr28BkCvkWdDt9d8Z40qeu1aZdcr157mR+yZGPfBfB2vasrNIEwQ==\n-----END CERTIFICATE-----\n'})

TASK [remote/trust : Generate trust_ca.pem] *************************************************************************************
changed: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/trust : Copy trust_ca.pem to host] *********************************************************************************
changed: [welktxef-931856-rz-le2pts6-008]

TASK [remote/trust : Install certificate] ***************************************************************************************
changed: [welktxef-931856-rz-le2pts6-008]

TASK [remote/trust : Remove temporary working directory] ************************************************************************
changed: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [Remote Starlingx] *********************************************************************************************************

TASK [remote/starlingx : Create temporary working directory] ********************************************************************
changed: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/starlingx : Copy SSL root certificates] ****************************************************************************
changed: [welktxef-931856-rz-le2pts6-008 -> localhost] => (item={'filename': 'vz_root_ica_cert.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIFNzCCAx+gAwIBAgIUGLJR/hP48n+vdq2v1hcfspXo/78wDQYJKoZIhvcNAQEL\nBQAwWjELMAkGA1UEBhMCVVMxEDAOBgNVBAoMB1Zlcml6b24xEzARBgNVBAsMClZa\nSUFNIFRlc3QxJDAiBgNVBAMMG1Zlcml6b24gTmV0d29yayBSU0EgQ0EgVGVzdDAe\nFw0yMDEwMjIyMTE0MDNaFw0zMDEwMjIyMTE0MDNaMIGRMQswCQYDVQQGEwJVUzEL\nMAkGA1UECAwCVFgxETAPBgNVBAcMCFdlc3RsYWtlMRAwDgYDVQQKDAdWZXJpem9u\nMR0wGwYDVQQLDBRWZXJpem9uIFNvdXJjaW5nIExMQzExMC8GA1UEAwwoVmVyaXpv\nbiBOZXR3b3JrIFdFTEtUWElCIExBQiAxIDMgUlNBIElDQTCCASIwDQYJKoZIhvcN\nAQEBBQADggEPADCCAQoCggEBANhkGTXOCKEYf5znDDeX3n/DHFPVqazgQsr0/SIG\n4eb1JY5q5Jq3ZhAaZCr9HJuCkwAP/zgYH0llqOvf8AC2Uh+7z1b33IbwxPmJfWCP\nAqSNFkLWWVRdbELapCu408QsrLMW8IrdP6PLiKAepwncfm4T0/6bANqIEmUkpw8Q\nxProeiNwlGbwUll+tELmdCk7vA7hKX3j1kUvS5Z84Z5ivJBWEcUEggmC97TK4aLo\nFVEHbyahze568JVEaM1vY5L4mnRRTl+u5ipaSMxVBsiXzF7eFuKCzqF7wxbDIt2T\nIFEJtwyJDW5bXjyXgiF1d5H/URprUcRV9Qmf2+PXcfwHII8CAwEAAaOBvDCBuTAS\nBgNVHRMBAf8ECDAGAQH/AgEAMA4GA1UdDwEB/wQEAwIBBjAfBgNVHSMEGDAWgBQl\neng3lqGBeTrbLVuABoEmUHm1+TBTBgNVHR8ETDBKMEigRqBEhkJodHRwOi8vc2Vj\ndXJlLnN0YWdpbmcuc2VjdXJpdHljcmVkZW50aWFsaW5nLmNvbS9jcmwvdnpuZXRy\nc2FjYS5jcmwwHQYDVR0OBBYEFP0Z+/vaDLtAoFig1I9ttNKnmzByMA0GCSqGSIb3\nDQEBCwUAA4ICAQBuXVTf9e01HeymHgRcFCwP2N6G6u+vIzY8Bz0zSUZeRDHMZQcS\nNoabDyn5FfGJlw4BqGC591Sp0/unFQDzAg17rDBcrgwajeFeUiFdb9PiAJwHaX9S\nvq/7VmVLCmpeb+a/laXAe6+tkY1kcFrd1+ItRKC6ZGXMsoDkmk5Ndxxgw77estcI\nMiiLQbvpXRygX5wD4/ayazuLms9qITZkOZ1nTLVqq7QrwYCsSoih7hj6sbsfXr19\nGoYWmk8Y7O/d3ttgyHuRH9k/2dQ/xL7avRpMNkPdr7ocJqI46hvx2X6UyOo7IBua\nkSkFbSmPZWIVAidNMBOnvffCQ32tfjT2/xso/a9cdskvxqgLi0MPARU9Nl2Pufsb\nD7l4/sBvz/PiNTKp+Daa9FdyLb9ySidos1uS0c24bUtY1RXXGAVV2qgfyrzvzfye\nSM+w16hMU/yeYiuA1jsPmsnZnuIJj4Nv8ZjjZ0WS53pP5wcghaHkBrqWQNT8meqA\nVElrMBPlYq67T+AXP0B9lf5Sc3QVIio7XKKfqrlcQxY2JGLEyE53JgZGX7dpwU4I\nukLvyHbT4p06oY3qG6+wH8+YIXCNAYtadJ/C5/u9GcLX5NnZrcuduj0inw2/a3Ao\nWgCt6/Pr28BkCvkWdDt9d8Z40qeu1aZdcr157mR+yZGPfBfB2vasrNIEwQ==\n-----END CERTIFICATE-----\n'})
changed: [welktxef-931856-rz-le2pts6-008 -> localhost] => (item={'filename': 'vz_root_ica_key.pem', 'value': '-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA2GQZNc4IoRh/nOcMN5fef8McU9WprOBCyvT9Igbh5vUljmrk\nmrdmEBpkKv0cm4KTAA//OBgfSWWo69/wALZSH7vPVvfchvDE+Yl9YI8CpI0WQtZZ\nVF1sQtqkK7jTxCyssxbwit0/o8uIoB6nCdx+bhPT/psA2ogSZSSnDxDE+uh6I3CU\nZvBSWX60QuZ0KTu8DuEpfePWRS9LlnzhnmK8kFYRxQSCCYL3tMrhougVUQdvJqHN\n7nrwlURozW9jkviadFFOX67mKlpIzFUGyJfMXt4W4oLOoXvDFsMi3ZMgUQm3DIkN\nbltePJeCIXV3kf9RGmtRxFX1CZ/b49dx/AcgjwIDAQABAoIBABSd1NkPfDr8/ouQ\nZ9WUHprFmBlUrgnOhA6aMNPhG/zJNn7PKGClQJAgM5L08pjOY/sJiyNpCPIRQXrX\npyIqPMDRP/vlOZmRrvKnas6cUYAkAQ71JSWokPv9oM6ZmXODXiDh+qEAW2PbrHS0\n9u01mMYcFYKYeghYFoiUaWZCDsJo3v3dgeE9aQ4tB9ksovSmWrpuCY7NKbd7Qrbo\n5XxQhkujTkE6knOHz8CVwYETtj8LZ/bvHIkGMGvRvwsKYDZkIKr5CZ7DX+KcMfPN\neMZU4VCHYSXNxsyp5DJ1Zw+gx8/32kUL0CzJLLam1G021Hq41KPwwSV/KPrOKel7\nHXDLXeECgYEA8MR+lgxGjYTc/k4TdZvcFVgqHGLXnyjO7ZVt4b7UpwmayLuoSD/M\nOpHQYX+JBIIWTNlGhG8UV3DPC3v+auhYa7twwbekS30IYCAmu5GCKgMAcWFinz6A\nYZxG55P/hShetCyOqikgwXqzMlwGs8KEul8f8BKssROzUy8mIlFhjq0CgYEA5hTM\nSNxAD3dlRtb0771fBU7fjx8JPfjptP9vP/JVEelkc/ti9nZ5buTC+9cQC/B+YFx7\nc82uCrXV13bGR9iH8xBhwU7JOYJZbgCpwp0F56wIN5Pdk9Eo79Batrw3oGBG4Yvt\nDc2eltxQbHgObc/qygf88j9XqD8aGIvQrc4Jf6sCgYAtxX03M1A6WTbWFau3YRD+\n8crXqKbLOCvWmODR2MB+nOHTJXHBgndl7xCJaIB43e41X9z7Ek7wrJ5/1WuxkUg1\n+uVdvna6byOnepVCdVAkgnuUEmp4UZ6AcAA+yDD8dIdEg2//w1/ZyGTGvx37EJDB\nCZJ9xl8ULuWZe84pGgWM5QKBgQCYVUbYKrNjShrM5z9uh4QlII6V1Oeql2YtBz4i\nKZE3db6jp9pi8hf+WwnZ8g9WyFjz9edqydAkmTXHHYW0ReHlBYCjm0VRhUMuuNOs\n3YfuVpFuMsFuv/oJpXqaKE3wKi5j4OAH1o7ctWuuFWMAQ7vhHZ7UySmBZJ4jiFaW\n7KaPVwKBgE8E0xbSDVGxXbEGwRXxeaOSemEHD9uEnbAyq1p3EBBhBvInWmDiP5vJ\n68IYNZ4SGxXEKDifwrLGHyekt3RK9B2+U03okd1qH7gfBIlxBJivcjhBe2PtK/Qj\n6fBN0fC1UJoE6pseT9cJDaBq2wMRXJGRYtT8fU9PPJcfa23JlKNS\n-----END RSA PRIVATE KEY-----\n'})

TASK [remote/starlingx : Copy templates] ****************************************************************************************
changed: [welktxef-931856-rz-le2pts6-008 -> localhost] => (item=req_starlingx.cnf)

TASK [remote/starlingx : Generate SSL cert] *************************************************************************************
changed: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/starlingx : Copy SSL starlingx certs to server] ********************************************************************
changed: [welktxef-931856-rz-le2pts6-008] => (item=starlingx-ca-cert.pem)

TASK [remote/starlingx : Configure starlingx] ***********************************************************************************
changed: [welktxef-931856-rz-le2pts6-008]

TASK [remote/starlingx : Remove temporary working directory] ********************************************************************
changed: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [Remote Integ] *************************************************************************************************************

TASK [remote/integ : Detect applied status of platform-integ-apps application] **************************************************
changed: [welktxef-931856-rz-le2pts6-008]

TASK [remote/integ : Fail if platform-integ-apps application apply failed] ******************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [Remote Ldap] **************************************************************************************************************

TASK [remote/ldap : Create temporary working directory] *************************************************************************
changed: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/ldap : Copy SSL root certificates] *********************************************************************************
changed: [welktxef-931856-rz-le2pts6-008 -> localhost] => (item={'filename': 'vz_root_ca_cert.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIFpTCCA42gAwIBAgIUa3vZ0YGxO1TQ8NwhiVfQC0JslXgwDQYJKoZIhvcNAQEL\nBQAwWjELMAkGA1UEBhMCVVMxEDAOBgNVBAoMB1Zlcml6b24xEzARBgNVBAsMClZa\nSUFNIFRlc3QxJDAiBgNVBAMMG1Zlcml6b24gTmV0d29yayBSU0EgQ0EgVGVzdDAe\nFw0yMDA2MTUyMTAxMTNaFw0zNTA2MTUyMTAxMTNaMFoxCzAJBgNVBAYTAlVTMRAw\nDgYDVQQKDAdWZXJpem9uMRMwEQYDVQQLDApWWklBTSBUZXN0MSQwIgYDVQQDDBtW\nZXJpem9uIE5ldHdvcmsgUlNBIENBIFRlc3QwggIiMA0GCSqGSIb3DQEBAQUAA4IC\nDwAwggIKAoICAQC8AIrksI57CbIl5uGZ6yqfpQj3aK+N8f1EVHdwK9JFskoipvC8\n7yFTk8tgmO1i0YA5oRGfNxneqCdrXZiWL6Ko8v/iln9vuN+2rK3rgWZPPRJBAsBN\na49L7U6lJjIGxIZtZqmK5h47oiUtwlYVrbZMN2ijuBQ22/eQ9tsFDV28oBuZ3WAR\npSSbj/tubPQYkw3YYOhv/VpEpsd0rkoEt3QCmTVcX2rtblanpXowTV5R0Hy4014n\nT49jrEo40r4mwYoyS835Uv4ENUFA+pXicT9eUot3RSH6rYdx4A/14UtoI9U0ol8M\n62GHpxSASQ2Kc3yQWvxRGTFslTduYM+vVmMLEDDdqcsjYnStPpwdxxmKItmbjxSv\nIwYIndp8A04WkX2iiJCciC3BNxiLamPtYVyB1HHqbGTGirKYuSvwZt337q1OI3WH\nwVn2S4Mj/wqa4iCyGTvFSUnGq34Xkrb9XNwWBok9Tc2XWGAU/mb/xcd1hX74GZbF\nsrZ11aPtym4kMAjU2KQi96GcAH2lnGZYoOja1J4Cs4WYx1uAx74H/m84CrYavVfl\n1ONJVLDfuZaEkSmu+jHQX15pAECNORTuLD06PbWnOEcOi1xmbt/OT3SA3rhD2mb7\n2wxl7oJpV3ap8xGwYmxiFzmInxFJ1axjg8Rimol0mXTKAy6OdNHbCOnAwwIDAQAB\no2MwYTAPBgNVHRMBAf8EBTADAQH/MA4GA1UdDwEB/wQEAwIBBjAfBgNVHSMEGDAW\ngBQleng3lqGBeTrbLVuABoEmUHm1+TAdBgNVHQ4EFgQUJXp4N5ahgXk62y1bgAaB\nJlB5tfkwDQYJKoZIhvcNAQELBQADggIBADQ9jpmVh9nyY7ZQ4s+S9RuSRYn7QsrW\nDePeMzQgh8ZtS8WE65GY5HS61iHNP2Co8Q1lAaBWF4ipq+VZOcQbPLccHzd1kZv4\ns4u0aTzBd9ccidl73FS0DJDQOBbzPSzgsaiGHSMyGzkTeA8z3ntsSqrXXcDUvoRi\nFus/110AwdtNhJLrWveX6btYtHp9Lqe0YtNCy5AaXlrr1yRSckP5BWVtlwD4dzSO\n/dqI3wHS/ncUx9wSQomZ+AmxYW3KtJQKgHzTqHru1x9BBk7Bzfz9FZr6HLLmEitj\nuFoDRd5TNt5LbO0zDQokvY3oqso6Htup/rS7C08mcmnelYE+yXuOc1YrlyGnpBzk\nmy+1VYbOxRRdqKAZRbE72u/h847IVpsOvjR51iksuCAurZdp2+y2zvV8NhWekuNy\nirECRy9cb4YasjRaKi0/TCGPVSICuLyeG2W72liCj/N2VKfjPP9zsOR5XjwCXfRg\n+9xhLy77/gov2NWXx5fzTkhxCrHOxFdLVMn0wQhksDmw6QsXzDIHSpIOypdDfnx9\nCsthx3nhkuHLUaEP22D22dG+vImA9ukj4R/RRI/87jmi9Q8+ehH+NqN0GZZcLjdN\nSLVXpncuwWQFUDPR06wNkkkmBSXWiIYhwqSpU0Pl3er3fD0uWvXuWPm2PzfOmUAE\nUrkzyw9XmLw0\n-----END CERTIFICATE-----\n'})
changed: [welktxef-931856-rz-le2pts6-008 -> localhost] => (item={'filename': 'vz_root_ica_cert.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIFNzCCAx+gAwIBAgIUGLJR/hP48n+vdq2v1hcfspXo/78wDQYJKoZIhvcNAQEL\nBQAwWjELMAkGA1UEBhMCVVMxEDAOBgNVBAoMB1Zlcml6b24xEzARBgNVBAsMClZa\nSUFNIFRlc3QxJDAiBgNVBAMMG1Zlcml6b24gTmV0d29yayBSU0EgQ0EgVGVzdDAe\nFw0yMDEwMjIyMTE0MDNaFw0zMDEwMjIyMTE0MDNaMIGRMQswCQYDVQQGEwJVUzEL\nMAkGA1UECAwCVFgxETAPBgNVBAcMCFdlc3RsYWtlMRAwDgYDVQQKDAdWZXJpem9u\nMR0wGwYDVQQLDBRWZXJpem9uIFNvdXJjaW5nIExMQzExMC8GA1UEAwwoVmVyaXpv\nbiBOZXR3b3JrIFdFTEtUWElCIExBQiAxIDMgUlNBIElDQTCCASIwDQYJKoZIhvcN\nAQEBBQADggEPADCCAQoCggEBANhkGTXOCKEYf5znDDeX3n/DHFPVqazgQsr0/SIG\n4eb1JY5q5Jq3ZhAaZCr9HJuCkwAP/zgYH0llqOvf8AC2Uh+7z1b33IbwxPmJfWCP\nAqSNFkLWWVRdbELapCu408QsrLMW8IrdP6PLiKAepwncfm4T0/6bANqIEmUkpw8Q\nxProeiNwlGbwUll+tELmdCk7vA7hKX3j1kUvS5Z84Z5ivJBWEcUEggmC97TK4aLo\nFVEHbyahze568JVEaM1vY5L4mnRRTl+u5ipaSMxVBsiXzF7eFuKCzqF7wxbDIt2T\nIFEJtwyJDW5bXjyXgiF1d5H/URprUcRV9Qmf2+PXcfwHII8CAwEAAaOBvDCBuTAS\nBgNVHRMBAf8ECDAGAQH/AgEAMA4GA1UdDwEB/wQEAwIBBjAfBgNVHSMEGDAWgBQl\neng3lqGBeTrbLVuABoEmUHm1+TBTBgNVHR8ETDBKMEigRqBEhkJodHRwOi8vc2Vj\ndXJlLnN0YWdpbmcuc2VjdXJpdHljcmVkZW50aWFsaW5nLmNvbS9jcmwvdnpuZXRy\nc2FjYS5jcmwwHQYDVR0OBBYEFP0Z+/vaDLtAoFig1I9ttNKnmzByMA0GCSqGSIb3\nDQEBCwUAA4ICAQBuXVTf9e01HeymHgRcFCwP2N6G6u+vIzY8Bz0zSUZeRDHMZQcS\nNoabDyn5FfGJlw4BqGC591Sp0/unFQDzAg17rDBcrgwajeFeUiFdb9PiAJwHaX9S\nvq/7VmVLCmpeb+a/laXAe6+tkY1kcFrd1+ItRKC6ZGXMsoDkmk5Ndxxgw77estcI\nMiiLQbvpXRygX5wD4/ayazuLms9qITZkOZ1nTLVqq7QrwYCsSoih7hj6sbsfXr19\nGoYWmk8Y7O/d3ttgyHuRH9k/2dQ/xL7avRpMNkPdr7ocJqI46hvx2X6UyOo7IBua\nkSkFbSmPZWIVAidNMBOnvffCQ32tfjT2/xso/a9cdskvxqgLi0MPARU9Nl2Pufsb\nD7l4/sBvz/PiNTKp+Daa9FdyLb9ySidos1uS0c24bUtY1RXXGAVV2qgfyrzvzfye\nSM+w16hMU/yeYiuA1jsPmsnZnuIJj4Nv8ZjjZ0WS53pP5wcghaHkBrqWQNT8meqA\nVElrMBPlYq67T+AXP0B9lf5Sc3QVIio7XKKfqrlcQxY2JGLEyE53JgZGX7dpwU4I\nukLvyHbT4p06oY3qG6+wH8+YIXCNAYtadJ/C5/u9GcLX5NnZrcuduj0inw2/a3Ao\nWgCt6/Pr28BkCvkWdDt9d8Z40qeu1aZdcr157mR+yZGPfBfB2vasrNIEwQ==\n-----END CERTIFICATE-----\n'})
changed: [welktxef-931856-rz-le2pts6-008 -> localhost] => (item={'filename': 'vz_root_ica_key.pem', 'value': '-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA2GQZNc4IoRh/nOcMN5fef8McU9WprOBCyvT9Igbh5vUljmrk\nmrdmEBpkKv0cm4KTAA//OBgfSWWo69/wALZSH7vPVvfchvDE+Yl9YI8CpI0WQtZZ\nVF1sQtqkK7jTxCyssxbwit0/o8uIoB6nCdx+bhPT/psA2ogSZSSnDxDE+uh6I3CU\nZvBSWX60QuZ0KTu8DuEpfePWRS9LlnzhnmK8kFYRxQSCCYL3tMrhougVUQdvJqHN\n7nrwlURozW9jkviadFFOX67mKlpIzFUGyJfMXt4W4oLOoXvDFsMi3ZMgUQm3DIkN\nbltePJeCIXV3kf9RGmtRxFX1CZ/b49dx/AcgjwIDAQABAoIBABSd1NkPfDr8/ouQ\nZ9WUHprFmBlUrgnOhA6aMNPhG/zJNn7PKGClQJAgM5L08pjOY/sJiyNpCPIRQXrX\npyIqPMDRP/vlOZmRrvKnas6cUYAkAQ71JSWokPv9oM6ZmXODXiDh+qEAW2PbrHS0\n9u01mMYcFYKYeghYFoiUaWZCDsJo3v3dgeE9aQ4tB9ksovSmWrpuCY7NKbd7Qrbo\n5XxQhkujTkE6knOHz8CVwYETtj8LZ/bvHIkGMGvRvwsKYDZkIKr5CZ7DX+KcMfPN\neMZU4VCHYSXNxsyp5DJ1Zw+gx8/32kUL0CzJLLam1G021Hq41KPwwSV/KPrOKel7\nHXDLXeECgYEA8MR+lgxGjYTc/k4TdZvcFVgqHGLXnyjO7ZVt4b7UpwmayLuoSD/M\nOpHQYX+JBIIWTNlGhG8UV3DPC3v+auhYa7twwbekS30IYCAmu5GCKgMAcWFinz6A\nYZxG55P/hShetCyOqikgwXqzMlwGs8KEul8f8BKssROzUy8mIlFhjq0CgYEA5hTM\nSNxAD3dlRtb0771fBU7fjx8JPfjptP9vP/JVEelkc/ti9nZ5buTC+9cQC/B+YFx7\nc82uCrXV13bGR9iH8xBhwU7JOYJZbgCpwp0F56wIN5Pdk9Eo79Batrw3oGBG4Yvt\nDc2eltxQbHgObc/qygf88j9XqD8aGIvQrc4Jf6sCgYAtxX03M1A6WTbWFau3YRD+\n8crXqKbLOCvWmODR2MB+nOHTJXHBgndl7xCJaIB43e41X9z7Ek7wrJ5/1WuxkUg1\n+uVdvna6byOnepVCdVAkgnuUEmp4UZ6AcAA+yDD8dIdEg2//w1/ZyGTGvx37EJDB\nCZJ9xl8ULuWZe84pGgWM5QKBgQCYVUbYKrNjShrM5z9uh4QlII6V1Oeql2YtBz4i\nKZE3db6jp9pi8hf+WwnZ8g9WyFjz9edqydAkmTXHHYW0ReHlBYCjm0VRhUMuuNOs\n3YfuVpFuMsFuv/oJpXqaKE3wKi5j4OAH1o7ctWuuFWMAQ7vhHZ7UySmBZJ4jiFaW\n7KaPVwKBgE8E0xbSDVGxXbEGwRXxeaOSemEHD9uEnbAyq1p3EBBhBvInWmDiP5vJ\n68IYNZ4SGxXEKDifwrLGHyekt3RK9B2+U03okd1qH7gfBIlxBJivcjhBe2PtK/Qj\n6fBN0fC1UJoE6pseT9cJDaBq2wMRXJGRYtT8fU9PPJcfa23JlKNS\n-----END RSA PRIVATE KEY-----\n'})

TASK [remote/ldap : Copy templates] *********************************************************************************************
changed: [welktxef-931856-rz-le2pts6-008 -> localhost] => (item={'name': 'req-ldap.cnf', 'mode': '0644'})

TASK [remote/ldap : Generate SSL cert] ******************************************************************************************
changed: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/ldap : Copy templates] *********************************************************************************************
changed: [welktxef-931856-rz-le2pts6-008] => (item={'name': 'dex-overrides.yaml', 'mode': '0644'})

TASK [remote/ldap : Copy SSL dex certs to server] *******************************************************************************
changed: [welktxef-931856-rz-le2pts6-008] => (item=dex-cert.pem)
changed: [welktxef-931856-rz-le2pts6-008] => (item=dex-key.pem)
changed: [welktxef-931856-rz-le2pts6-008] => (item=dex-ca.pem)

TASK [remote/ldap : Copy SSL AD cert to server] *********************************************************************************
changed: [welktxef-931856-rz-le2pts6-008] => (item={'filename': 'ad_ca.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIFpTCCA42gAwIBAgIUa3vZ0YGxO1TQ8NwhiVfQC0JslXgwDQYJKoZIhvcNAQEL\nBQAwWjELMAkGA1UEBhMCVVMxEDAOBgNVBAoMB1Zlcml6b24xEzARBgNVBAsMClZa\nSUFNIFRlc3QxJDAiBgNVBAMMG1Zlcml6b24gTmV0d29yayBSU0EgQ0EgVGVzdDAe\nFw0yMDA2MTUyMTAxMTNaFw0zNTA2MTUyMTAxMTNaMFoxCzAJBgNVBAYTAlVTMRAw\nDgYDVQQKDAdWZXJpem9uMRMwEQYDVQQLDApWWklBTSBUZXN0MSQwIgYDVQQDDBtW\nZXJpem9uIE5ldHdvcmsgUlNBIENBIFRlc3QwggIiMA0GCSqGSIb3DQEBAQUAA4IC\nDwAwggIKAoICAQC8AIrksI57CbIl5uGZ6yqfpQj3aK+N8f1EVHdwK9JFskoipvC8\n7yFTk8tgmO1i0YA5oRGfNxneqCdrXZiWL6Ko8v/iln9vuN+2rK3rgWZPPRJBAsBN\na49L7U6lJjIGxIZtZqmK5h47oiUtwlYVrbZMN2ijuBQ22/eQ9tsFDV28oBuZ3WAR\npSSbj/tubPQYkw3YYOhv/VpEpsd0rkoEt3QCmTVcX2rtblanpXowTV5R0Hy4014n\nT49jrEo40r4mwYoyS835Uv4ENUFA+pXicT9eUot3RSH6rYdx4A/14UtoI9U0ol8M\n62GHpxSASQ2Kc3yQWvxRGTFslTduYM+vVmMLEDDdqcsjYnStPpwdxxmKItmbjxSv\nIwYIndp8A04WkX2iiJCciC3BNxiLamPtYVyB1HHqbGTGirKYuSvwZt337q1OI3WH\nwVn2S4Mj/wqa4iCyGTvFSUnGq34Xkrb9XNwWBok9Tc2XWGAU/mb/xcd1hX74GZbF\nsrZ11aPtym4kMAjU2KQi96GcAH2lnGZYoOja1J4Cs4WYx1uAx74H/m84CrYavVfl\n1ONJVLDfuZaEkSmu+jHQX15pAECNORTuLD06PbWnOEcOi1xmbt/OT3SA3rhD2mb7\n2wxl7oJpV3ap8xGwYmxiFzmInxFJ1axjg8Rimol0mXTKAy6OdNHbCOnAwwIDAQAB\no2MwYTAPBgNVHRMBAf8EBTADAQH/MA4GA1UdDwEB/wQEAwIBBjAfBgNVHSMEGDAW\ngBQleng3lqGBeTrbLVuABoEmUHm1+TAdBgNVHQ4EFgQUJXp4N5ahgXk62y1bgAaB\nJlB5tfkwDQYJKoZIhvcNAQELBQADggIBADQ9jpmVh9nyY7ZQ4s+S9RuSRYn7QsrW\nDePeMzQgh8ZtS8WE65GY5HS61iHNP2Co8Q1lAaBWF4ipq+VZOcQbPLccHzd1kZv4\ns4u0aTzBd9ccidl73FS0DJDQOBbzPSzgsaiGHSMyGzkTeA8z3ntsSqrXXcDUvoRi\nFus/110AwdtNhJLrWveX6btYtHp9Lqe0YtNCy5AaXlrr1yRSckP5BWVtlwD4dzSO\n/dqI3wHS/ncUx9wSQomZ+AmxYW3KtJQKgHzTqHru1x9BBk7Bzfz9FZr6HLLmEitj\nuFoDRd5TNt5LbO0zDQokvY3oqso6Htup/rS7C08mcmnelYE+yXuOc1YrlyGnpBzk\nmy+1VYbOxRRdqKAZRbE72u/h847IVpsOvjR51iksuCAurZdp2+y2zvV8NhWekuNy\nirECRy9cb4YasjRaKi0/TCGPVSICuLyeG2W72liCj/N2VKfjPP9zsOR5XjwCXfRg\n+9xhLy77/gov2NWXx5fzTkhxCrHOxFdLVMn0wQhksDmw6QsXzDIHSpIOypdDfnx9\nCsthx3nhkuHLUaEP22D22dG+vImA9ukj4R/RRI/87jmi9Q8+ehH+NqN0GZZcLjdN\nSLVXpncuwWQFUDPR06wNkkkmBSXWiIYhwqSpU0Pl3er3fD0uWvXuWPm2PzfOmUAE\nUrkzyw9XmLw0\n-----END CERTIFICATE-----\n'})

TASK [remote/ldap : Configure local-dex.tls] ************************************************************************************
changed: [welktxef-931856-rz-le2pts6-008]

TASK [remote/ldap : Configure generic] ******************************************************************************************
changed: [welktxef-931856-rz-le2pts6-008]

TASK [remote/ldap : Configure wadcert] ******************************************************************************************
changed: [welktxef-931856-rz-le2pts6-008]

TASK [remote/ldap : Configure dex-overrides.yaml] *******************************************************************************
changed: [welktxef-931856-rz-le2pts6-008]

TASK [remote/ldap : Wait for distributed cloud synchronization] *****************************************************************
changed: [welktxef-931856-rz-le2pts6-008 -> rchltxib-c000000-003]

TASK [remote/ldap : Remove temporary working directory] *************************************************************************
changed: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/ldap : Detect oidc-auth-apps application in applying state (from a previous attempt)] ******************************
changed: [welktxef-931856-rz-le2pts6-008]

TASK [remote/ldap : Fail if oidc-auth-apps application-abort failed] ************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/ldap : Detect oidc-auth-apps application in apply-failed or aborted state] *****************************************
changed: [welktxef-931856-rz-le2pts6-008]

TASK [remote/ldap : Fail if oidc-auth-apps application apply failed] ************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/ldap : Apply oidc-auth-apps application] ***************************************************************************
changed: [welktxef-931856-rz-le2pts6-008]

TASK [remote/ldap : Detect applied status of oidc-auth-apps application] ********************************************************
FAILED - RETRYING: Detect applied status of oidc-auth-apps application (60 retries left).
FAILED - RETRYING: Detect applied status of oidc-auth-apps application (59 retries left).
changed: [welktxef-931856-rz-le2pts6-008]

TASK [remote/ldap : Fail if oidc-auth-apps application apply failed] ************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [Remote Metrics Server] ****************************************************************************************************

TASK [remote/metrics-server : Set facts - 21.05] ********************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/metrics-server : Set facts - 21.12] ********************************************************************************
ok: [welktxef-931856-rz-le2pts6-008]

TASK [remote/metrics-server : Get software load status] *************************************************************************
changed: [welktxef-931856-rz-le2pts6-008]

TASK [remote/metrics-server : Noop if the system is NOT at the right caas_version] **********************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/metrics-server : Print message if system is NOT at the right caas_version] *****************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/metrics-server : Detect presence of existing application] **********************************************************
fatal: [welktxef-931856-rz-le2pts6-008]: FAILED! => {"changed": true, "cmd": ". /etc/platform/openrc\nsystem application-show metrics-server --column status --format value\n", "delta": "0:00:02.118992", "end": "2024-01-30 03:44:59.798796", "msg": "non-zero return code", "rc": 1, "start": "2024-01-30 03:44:57.679804", "stderr": "application not found: metrics-server", "stderr_lines": ["application not found: metrics-server"], "stdout": "", "stdout_lines": []}
...ignoring

TASK [remote/metrics-server : Print message if system already has the appication] ***********************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/metrics-server : Apply again since the previous apply failed or in uploaded state] *********************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/metrics-server : Wait until apply is in the applied or apply-failed state] *****************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/metrics-server : Print message if re-apply succeeds] ***************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/metrics-server : Print message if re-apply failed] *****************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/metrics-server : Noop if system requires no further action or needs manual investigation] **************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/metrics-server : Upload application] *******************************************************************************
changed: [welktxef-931856-rz-le2pts6-008]

TASK [remote/metrics-server : Wait until application is in the uploaded state] **************************************************
changed: [welktxef-931856-rz-le2pts6-008]

TASK [remote/metrics-server : Apply application] ********************************************************************************
changed: [welktxef-931856-rz-le2pts6-008]

TASK [remote/metrics-server : Wait until application is in the applied or apply-failed state] ***********************************
FAILED - RETRYING: Wait until application is in the applied or apply-failed state (90 retries left).
FAILED - RETRYING: Wait until application is in the applied or apply-failed state (89 retries left).
FAILED - RETRYING: Wait until application is in the applied or apply-failed state (88 retries left).
FAILED - RETRYING: Wait until application is in the applied or apply-failed state (87 retries left).
changed: [welktxef-931856-rz-le2pts6-008]

TASK [remote/metrics-server : Apply again since the first apply failed] *********************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/metrics-server : Wait again until apply is in the applied or apply-failed state] ***********************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/metrics-server : Print message if apply is successful] *************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "msg": [
        "=======================================================",
        " welktxef-d931856-008: metrics-server install SUCCEEDED! ",
        "======================================================="
    ]
}

TASK [remote/metrics-server : Print message if apply is failure] ****************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [Remote wrap-get-central-version] ******************************************************************************************

TASK [remote/wrap-get-central-version : Set facts for playbook] *****************************************************************
ok: [welktxef-931856-rz-le2pts6-008]

TASK [remote/wrap-get-central-version : Determine central WRA current version] **************************************************
fatal: [welktxef-931856-rz-le2pts6-008 -> rchltxib-c000000-003]: FAILED! => {"changed": true, "cmd": ". /etc/platform/openrc\nsystem application-show wr-analytics --column app_version --format value\n", "delta": "0:00:01.267100", "end": "2024-01-30 03:46:11.475358", "msg": "non-zero return code", "rc": 1, "start": "2024-01-30 03:46:10.208258", "stderr": "application not found: wr-analytics", "stderr_lines": ["application not found: wr-analytics"], "stdout": "", "stdout_lines": []}
...ignoring

TASK [remote/wrap-get-central-version : Set facts for wra_target_version] *******************************************************
ok: [welktxef-931856-rz-le2pts6-008]

TASK [remote/wrap-get-central-version : debug] **********************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "msg": "wra_target_version:"
}

TASK [Remote wrap-2112-2] *******************************************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [Remote wrap-2106-2] *******************************************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [Remote wrap-6] ************************************************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [Remote fpga-user-image] ***************************************************************************************************

TASK [remote/fpga-user-image : Set facts for ansible credential - 21.05] ********************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/fpga-user-image : Set facts for ansible credential - 21.12] ********************************************************
ok: [welktxef-931856-rz-le2pts6-008]

TASK [remote/fpga-user-image : Get software load status] ************************************************************************
changed: [welktxef-931856-rz-le2pts6-008]

TASK [remote/fpga-user-image : Noop if the system is NOT at the right caas_version] *********************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/fpga-user-image : Print message if system is NOT at the right caas_version] ****************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/fpga-user-image : Set facts for default fpga_image_file] ***********************************************************
ok: [welktxef-931856-rz-le2pts6-008]

TASK [remote/fpga-user-image : Set facts for fpga_image_file from host_vars] ****************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/fpga-user-image : Print message if server is not LS3 cascadelake] **************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "msg": [
        "==================================================================================",
        " Server type ZTS-LS6-pts6 is not LS3 cascadelake, no action will take place! ",
        "=================================================================================="
    ]
}

TASK [remote/fpga-user-image : Register noop because server is not LS3 cascadelake] *********************************************
changed: [welktxef-931856-rz-le2pts6-008]

TASK [remote/fpga-user-image : Check if FPGA update is stuck] *******************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/fpga-user-image : Abort FPGA update] *******************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/fpga-user-image : include_tasks] ***********************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/fpga-user-image : Check FPGA update status (HPE-LS3-e910)] *********************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/fpga-user-image : Check FPGA update status (ZTS-LS3-trtn)] *********************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/fpga-user-image : Noop if the system has been updated] *************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/fpga-user-image : Print message if the system has been updated] ****************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/fpga-user-image : In main block] ***********************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/fpga-user-image : Copy files to host] ******************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008] => (item=20ww43.5-1x2x25G-5GLDPC-v1.6.2-3.0.1-unsigned.bin)

TASK [remote/fpga-user-image : Do system device-image-upload] *******************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/fpga-user-image : debug - print UUID] ******************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/fpga-user-image : Do system device-image-apply] ********************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/fpga-user-image : Do system host-device-image-update] **************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/fpga-user-image : Wait till application completed] *****************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/fpga-user-image : Do system device-image-state-list] ***************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/fpga-user-image : force an error if image state is not completed] **************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [remote/fpga-user-image : include_tasks] ***********************************************************************************
skipping: [welktxef-931856-rz-le2pts6-008]

TASK [Install DM Monitor] *******************************************************************************************************

TASK [common/dm-monitor : Install DM Monitor] ***********************************************************************************
changed: [welktxef-931856-rz-le2pts6-008]

TASK [common/dm-monitor : Wait for DM Monitor pod created] **********************************************************************
changed: [welktxef-931856-rz-le2pts6-008]

TASK [common/dm-monitor : Wait for control-plane pods become ready] *************************************************************
changed: [welktxef-931856-rz-le2pts6-008]

TASK [common/dm-monitor : debug] ************************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "dm_monitor_pod_ready.stdout_lines": [
        "pod/dm-monitor-7f657fd988-46bsb condition met"
    ]
}

TASK [Proteus MWIAT - DISABLE] **************************************************************************************************

TASK [remote/zt-redfish : Update Attributes at /redfish/v1/Systems/Self/Bios/SD] ************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [remote/zt-redfish : Update result] ****************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "update_result": {
        "allow": "GET, PUT, PATCH, POST",
        "changed": false,
        "connection": "close",
        "content": "",
        "cookies": {},
        "cookies_string": "",
        "date": "Tue, 30 Jan 2024 03:46:26 GMT",
        "elapsed": 0,
        "failed": false,
        "msg": "OK (unknown bytes)",
        "redirected": false,
        "server": "AMI MegaRAC Redfish Service",
        "status": 204,
        "url": "https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/Systems/Self/Bios/SD"
    }
}

TASK [Lock/unlock after MWAIT change] *******************************************************************************************

TASK [common/lock-unlock : set_fact] ********************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008]

TASK [common/lock-unlock : include_tasks] ***************************************************************************************
included: /home/XXXXXX/playbooks/wr-installer/roles/common/lock-unlock/tasks/lock_node.yaml for welktxef-931856-rz-le2pts6-008

TASK [common/lock-unlock : Check subcloud status before locking] ****************************************************************
ok: [welktxef-931856-rz-le2pts6-008]

TASK [common/lock-unlock : debug] ***********************************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "msg": "The host is unlocked, continue with locking."
}

TASK [common/lock-unlock : Lock subcloud] ***************************************************************************************
changed: [welktxef-931856-rz-le2pts6-008]

TASK [common/lock-unlock : Pause for 10 seconds for the command to complete] ****************************************************
Pausing for 10 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [welktxef-931856-rz-le2pts6-008]

TASK [common/lock-unlock : Wait until subcloud is in locked status] *************************************************************
ok: [welktxef-931856-rz-le2pts6-008]

TASK [common/lock-unlock : Display subcloud status] *****************************************************************************
ok: [welktxef-931856-rz-le2pts6-008] => {
    "host_status_new.stdout": "locked"
}

TASK [common/lock-unlock : include_tasks] ***************************************************************************************
included: /home/XXXXXX/playbooks/wr-installer/roles/common/lock-unlock/tasks/unlock_node.yaml for welktxef-931856-rz-le2pts6-008

TASK [common/lock-unlock : Check subcloud status before unlocking] **************************************************************
ok: [welktxef-931856-rz-le2pts6-008]

TASK [common/lock-unlock : Unlock subcloud] *************************************************************************************
changed: [welktxef-931856-rz-le2pts6-008]

TASK [common/lock-unlock : Wait for node to restart (port 22 goes down)] ********************************************************
ok: [welktxef-931856-rz-le2pts6-008]

TASK [common/lock-unlock : Wait for node be back up (port 5000 comes up)] *******************************************************
ok: [welktxef-931856-rz-le2pts6-008]

TASK [common/lock-unlock : Obtain Keystone auth token] **************************************************************************
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

TASK [common/lock-unlock : Wait for contoller-0 enabled] ************************************************************************
FAILED - RETRYING: Wait for contoller-0 enabled (60 retries left).
ok: [welktxef-931856-rz-le2pts6-008 -> localhost]

PLAY RECAP **********************************************************************************************************************
welktxef-931856-rz-le2pts6-008 : ok=133  changed=58   unreachable=0    failed=0    skipped=63   rescued=0    ignored=4

[XXXXXX@welktxefnce-h-pe1util-vm01 wr-installer]$

```


### Installation was successful no issue, here is the subcloud reporting in to controller

```log
Every 5.0s: dcmanager subcloud list                                                                      Tue Jan 30 15:28:33 2024

+----+----------------------+------------+--------------+---------------+---------+
|  4 | welktxef-d931856-008 | managed    | online	| complete	| in-sync |
+----+----------------------+------------+--------------+---------------+---------+






```