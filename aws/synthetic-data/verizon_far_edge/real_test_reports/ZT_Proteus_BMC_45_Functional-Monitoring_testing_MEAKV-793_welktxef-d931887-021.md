# ZT .45 BMC firmware validation
# Redfish Functional Testing MEAKV-793
# 11/1/23 James Patchett

## Target Controller Rchltxfe-c000000-001
Controller-0 iLO 2607:f160:a:d02e:cd:fe0::8000 
Controller-1 iLO 2607:f160:a:d02e:cd:fe0::8001
Worker-0 iLO 2607:f160:a:d02e:cd:fe0::8002 
OAM 2607:f160:0:3043:cd:290:0:10

## Target Subcloud welktxef-d931887-021 (currently on controller 2607:f160:0:3049:cd:290:0:10 )
OAM 2607:f160:10:9249:ce:40a:0:f409
BMC 2607:f160:10:9249:ce:40a:0:e015

ipmitool -I lanplus -U XXXXXX -P XXXXXX -H 2607:f160:10:9249:ce:40a:0:e015 sol activate

## Subcloud welktxef-d931887-021

## MEAKV-793
## Add Certs to BMC to replace theirs
## using existing from old tamas test with welktxfe-d05400001-002

```sh
export CERT_STR="-----BEGIN CERTIFICATE-----\nMIIFYTCCBEmgAwIBAgIUEDtGa0jsYmz84njl0cSLGzgg8T4wDQYJKoZIhvcNAQEL\nBQAwgZExCzAJBgNVBAYTAlVTMQswCQYDVQQIDAJUWDERMA8GA1UEBwwIV2VzdGxh\na2UxEDAOBgNVBAoMB1Zlcml6b24xHTAbBgNVBAsMFFZlcml6b24gU291cmNpbmcg\nTExDMTEwLwYDVQQDDChWZXJpem9uIE5ldHdvcmsgV0VMS1RYRkUgTEFCIDEgMiBS\nU0EgSUNBMB4XDTIxMDcxNTIxNTI0MVoXDTMxMDcxMzIxNTI0MVowgaoxCzAJBgNV\nBAYTAlVTMQ4wDAYDVQQIDAVUZXhhczERMA8GA1UEBwwIV2VzdGxha2UxIzAhBgNV\nBAoMGlZlcml6b24gRGF0YSBTZXJ2aWNlcywgTExDMRUwEwYDVQQLDAxWQ1AgRmFy\nIEVkZ2UxPDA6BgNVBAMMM3dlbGt0eGZlLTA1NDAwMDAxLXJ6LWxlMXB0czYtMDAy\nLmZhcmVkZ2Uudnp3b3BzLmNvbTCCAiIwDQYJKoZIhvcNAQEBBQADggIPADCCAgoC\nggIBALld5Qbio4f7JKPt5NUAsxAsfRFVexeeNKZn0niktfiIXAvy7sEIBKNijZTD\nYIhNIgiBkYUf3X2fJfdwZ3VWhAJzdcL/sd+PeBXeZ/2m29kDMlN0tdm9ruZMANzo\nqaDyKnSfJLlVJqQToIrrXEv2FkI7diwvxKWkQrxjGwqgpyABJm4VsCBgqrYr3uwD\nCaVkROPyfiDS3K+cOKtI7K0DIYLjCI+li/1YOBEGqufPOGoRObsWyC/6yP1TPI7/\njoMM0r1/rLdz1wOnOtmuk2Enpn8pFVlvkxL2YpZ3NbmVV2mspdlDKVN0YmKt5ccl\no2tF4monyLgq4lrND6hlJy380Uz8C+5mDQy6oV4Da91hXLWlb7XbPdZrjVsV9sBu\nQO+TkAod8U1ug5vAYEQL6Nffz9nWXkxK6TbpyPpefu0FgX1sorCPWXohP0wZTP3r\n/i+JXk+ij6oYXCMYA9SzDr927bnavfRJZEnDwwVhM9NJ9YWVncO7w0wgiXcRF+Sc\nR0ROC9PFrJjjKWdwOoOr9VoCG6RZK7StYmteGFVvQM1bitSiPFZeXutz6Dd2VfKW\n24doXSdfg1wV3FyywWfSLFAMIMjGbuft1tBio898XApnBpO9+3tmB/nSrOsLP6lP\nhT5iGYqdMJ4vVjtU9KmXCqH1qxenPsKLs0VPhE4xvhZsfkdfAgMBAAGjgZUwgZIw\nUAYDVR0RBEkwR4Izd2Vsa3R4ZmUtMDU0MDAwMDEtcnotbGUxcHRzNi0wMDIuZmFy\nZWRnZS52endvcHMuY29thxAmB/FgABCQhADOBAoAAOACMB0GA1UdDgQWBBSy25eD\nfteCNDBsZzblWAi24ppRYDAfBgNVHSMEGDAWgBS+0KD7lwLbyLuUEtRdut6q6LOm\nxjANBgkqhkiG9w0BAQsFAAOCAQEAMSxXJVBVG9uGH/0MNJgMYEh8PQGPXjuNeKj8\n5xy2beaaFY6r6r1txJ0xN5Wu/i5+JPtrg+ykAHlEiIRx8St7dZ3jADmP0y0Jj8aE\nuuHaUsxoXoYc0H2lO2rM2wlpT8Wi/cI0yVDpnG2vVBkoFJPPcBo/2LV3yOcNwbac\nobGnyAFjeIaCC81m7Jyf6JqjDceo6os9YUbPTW4RUYM0BEWUWri2PeXoXAG2ARGp\neCP2pTC003GN5/HUcszUSVqI1DS2m5IF9uRglQE08LhS7jxyxSugZ1IqT+eEH3Un\nVNzUEMzl8Vjrl/orKQoK1RmOWG3Th0yhJ83b7tacHeu8l51D9A==\n-----END CERTIFICATE-----\n-----BEGIN RSA PRIVATE KEY-----\n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\n-----END RSA PRIVATE KEY-----"
```
## Current Certs
## nodes come with default AMI Self signed out of the box

## openssl check of current certs

```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ echo | openssl s_client -connect [${IP}]:443 -showcerts
CONNECTED(00000003)
Can't use SSL_get_servername
depth=0 C = US, ST = Georgia, L = Norcross, O = American Megatrends International LLC (AMI), OU = Service Processors, CN = megarac.com, emailAddress = support@ami.com
verify error:num=18:self signed certificate
verify return:1
depth=0 C = US, ST = Georgia, L = Norcross, O = American Megatrends International LLC (AMI), OU = Service Processors, CN = megarac.com, emailAddress = support@ami.com
verify return:1
---
Certificate chain
 0 s:C = US, ST = Georgia, L = Norcross, O = American Megatrends International LLC (AMI), OU = Service Processors, CN = megarac.com, emailAddress = support@ami.com
   i:C = US, ST = Georgia, L = Norcross, O = American Megatrends International LLC (AMI), OU = Service Processors, CN = megarac.com, emailAddress = support@ami.com
-----BEGIN CERTIFICATE-----
MIIEOzCCAyOgAwIBAgIJAO8c/Hd0c/0GMA0GCSqGSIb3DQEBCwUAMIG7MQswCQYD
VQQGEwJVUzEQMA4GA1UECAwHR2VvcmdpYTERMA8GA1UEBwwITm9yY3Jvc3MxNDAy
BgNVBAoMK0FtZXJpY2FuIE1lZ2F0cmVuZHMgSW50ZXJuYXRpb25hbCBMTEMgKEFN
SSkxGzAZBgNVBAsMElNlcnZpY2UgUHJvY2Vzc29yczEUMBIGA1UEAwwLbWVnYXJh
Yy5jb20xHjAcBgkqhkiG9w0BCQEWD3N1cHBvcnRAYW1pLmNvbTAeFw0xOTA4Mjcx
MzAzMDBaFw0zNDA4MjMxMzAzMDBaMIG7MQswCQYDVQQGEwJVUzEQMA4GA1UECAwH
R2VvcmdpYTERMA8GA1UEBwwITm9yY3Jvc3MxNDAyBgNVBAoMK0FtZXJpY2FuIE1l
Z2F0cmVuZHMgSW50ZXJuYXRpb25hbCBMTEMgKEFNSSkxGzAZBgNVBAsMElNlcnZp
Y2UgUHJvY2Vzc29yczEUMBIGA1UEAwwLbWVnYXJhYy5jb20xHjAcBgkqhkiG9w0B
CQEWD3N1cHBvcnRAYW1pLmNvbTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoC
ggEBAPjhY7RBU5kLGB3yHZfiEk9Zm9vJhe/1mRZlWTT77g8iy5eo2L9BiIsctpTm
2clMGBRwFgCjOyZqkldU2Mu2zeALS31Bkvx12/OOloG/MkvVxc09MrNWwEU0Q2Az
jGu7X+bEKSAQAYzFZIWSYf4hnadEtzh53rkdk9mKYp101YfnAqZ+zg9MxXuzl8TM
EGh7iemTtwozsLTHlwIiH6cIKNm7TmsL7ILifEQUP4wBTJBf1nmVe80fdNoDC+FB
vXwSuvHI5wIt4Nd2hthI6Ll6GRJrKGFE7FsqxVzBVb2anp8U44VDV69guPo47XlS
2yYXHPNwZmw9zm7mD5TCRJLKT20CAwEAAaNAMD4wCQYDVR0TBAIwADALBgNVHQ8E
BAMCBeAwJAYDVR0RBB0wG4ILbWVnYXJhYy5jb22CDDE2OS4yNTQuMC4xNzANBgkq
hkiG9w0BAQsFAAOCAQEAZi3ILVGGyVR6LJ+Au7gY5w9T+k+CpXgzorF+yRcSJo/h
/kfSMPPgH6yY+5ja4Z9kQ57nTfnaBqmHnEhwhAQrPVAPd3iKYEHNHO4u0gB4ZnkA
yeLA4vM3KG5510Iry8oBhYuvwZwE3YhtYNNocZd1ct5A8zJmpeuS4ffPwWFGZGmV
fiDSGa4NdzLr1auPt5FUgbsm5V0FNPNhYNRPYvHRMYh+orv727sJrxocr4BJ3ncq
UGNdPvVow5QQrmm0WsSjv285F3BiIeE1b6iSDksiiZ4lYLcr8twBeTq5gjc91qVh
Y7Ms4UrZYTJhYxq0oVGplADOn+LL9qEZ9MXAR6SkeQ==
-----END CERTIFICATE-----
---
Server certificate
subject=C = US, ST = Georgia, L = Norcross, O = American Megatrends International LLC (AMI), OU = Service Processors, CN = megarac.com, emailAddress = support@ami.com

issuer=C = US, ST = Georgia, L = Norcross, O = American Megatrends International LLC (AMI), OU = Service Processors, CN = megarac.com, emailAddress = support@ami.com

---
No client certificate CA names sent
Peer signing digest: SHA256
Peer signature type: RSA-PSS
Server Temp Key: ECDH, P-256, 256 bits
---
SSL handshake has read 1769 bytes and written 691 bytes
Verification error: self signed certificate
---
New, TLSv1.3, Cipher is TLS_AES_256_GCM_SHA384
Server public key is 2048 bit
Secure Renegotiation IS NOT supported
Compression: NONE
Expansion: NONE
No ALPN negotiated
Early data was not sent
Verify return code: 18 (self signed certificate)
---
DONE
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$
```

## Redfish 

```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ curl -ksn -u XXXXXX:XXXXXX https://[${IP}]/redfish/v1/Managers/Self/NetworkProtocol/HTTPS/Certificates/1 | jq .
{
  "@odata.context": "/redfish/v1/$metadata#Certificate.Certificate",
  "@odata.etag": "\"1699034003\"",
  "@odata.id": "/redfish/v1/Managers/Self/NetworkProtocol/HTTPS/Certificates/1",
  "@odata.type": "#Certificate.v1_1_1.Certificate",
  "Actions": {
    "#Certificate.Rekey": {
      "@Redfish.ActionInfo": "/redfish/v1/Managers/Self/NetworkProtocol/HTTPS/Certificates/1/Certificate.RekeyActionInfo",
      "target": "/redfish/v1/Managers/Self/NetworkProtocol/HTTPS/Certificates/1/Actions/Certificate.Rekey"
    },
    "#Certificate.Renew": {
      "@Redfish.ActionInfo": "/redfish/v1/Managers/Self/NetworkProtocol/HTTPS/Certificates/1/Certificate.RenewActionInfo",
      "target": "/redfish/v1/Managers/Self/NetworkProtocol/HTTPS/Certificates/1/Actions/Certificate.Renew"
    }
  },
  "CertificateString": "-----BEGIN CERTIFICATE-----\nMIIEOzCCAyOgAwIBAgIJAO8c/Hd0c/0GMA0GCSqGSIb3DQEBCwUAMIG7MQswCQYD\nVQQGEwJVUzEQMA4GA1UECAwHR2VvcmdpYTERMA8GA1UEBwwITm9yY3Jvc3MxNDAy\nBgNVBAoMK0FtZXJpY2FuIE1lZ2F0cmVuZHMgSW50ZXJuYXRpb25hbCBMTEMgKEFN\nSSkxGzAZBgNVBAsMElNlcnZpY2UgUHJvY2Vzc29yczEUMBIGA1UEAwwLbWVnYXJh\nYy5jb20xHjAcBgkqhkiG9w0BCQEWD3N1cHBvcnRAYW1pLmNvbTAeFw0xOTA4Mjcx\nMzAzMDBaFw0zNDA4MjMxMzAzMDBaMIG7MQswCQYDVQQGEwJVUzEQMA4GA1UECAwH\nR2VvcmdpYTERMA8GA1UEBwwITm9yY3Jvc3MxNDAyBgNVBAoMK0FtZXJpY2FuIE1l\nZ2F0cmVuZHMgSW50ZXJuYXRpb25hbCBMTEMgKEFNSSkxGzAZBgNVBAsMElNlcnZp\nY2UgUHJvY2Vzc29yczEUMBIGA1UEAwwLbWVnYXJhYy5jb20xHjAcBgkqhkiG9w0B\nCQEWD3N1cHBvcnRAYW1pLmNvbTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoC\nggEBAPjhY7RBU5kLGB3yHZfiEk9Zm9vJhe/1mRZlWTT77g8iy5eo2L9BiIsctpTm\n2clMGBRwFgCjOyZqkldU2Mu2zeALS31Bkvx12/OOloG/MkvVxc09MrNWwEU0Q2Az\njGu7X+bEKSAQAYzFZIWSYf4hnadEtzh53rkdk9mKYp101YfnAqZ+zg9MxXuzl8TM\nEGh7iemTtwozsLTHlwIiH6cIKNm7TmsL7ILifEQUP4wBTJBf1nmVe80fdNoDC+FB\nvXwSuvHI5wIt4Nd2hthI6Ll6GRJrKGFE7FsqxVzBVb2anp8U44VDV69guPo47XlS\n2yYXHPNwZmw9zm7mD5TCRJLKT20CAwEAAaNAMD4wCQYDVR0TBAIwADALBgNVHQ8E\nBAMCBeAwJAYDVR0RBB0wG4ILbWVnYXJhYy5jb22CDDE2OS4yNTQuMC4xNzANBgkq\nhkiG9w0BAQsFAAOCAQEAZi3ILVGGyVR6LJ+Au7gY5w9T+k+CpXgzorF+yRcSJo/h\n/kfSMPPgH6yY+5ja4Z9kQ57nTfnaBqmHnEhwhAQrPVAPd3iKYEHNHO4u0gB4ZnkA\nyeLA4vM3KG5510Iry8oBhYuvwZwE3YhtYNNocZd1ct5A8zJmpeuS4ffPwWFGZGmV\nfiDSGa4NdzLr1auPt5FUgbsm5V0FNPNhYNRPYvHRMYh+orv727sJrxocr4BJ3ncq\nUGNdPvVow5QQrmm0WsSjv285F3BiIeE1b6iSDksiiZ4lYLcr8twBeTq5gjc91qVh\nY7Ms4UrZYTJhYxq0oVGplADOn+LL9qEZ9MXAR6SkeQ==\n-----END CERTIFICATE-----",
  "CertificateType": "PEM",
  "Description": "Instance for Certificate Instance",
  "Id": "1",
  "Issuer": {
    "City": "Norcross",
    "CommonName": "megarac.com",
    "Country": "US",
    "Email": "support@ami.com",
    "Organization": "American Megatrends International LLC (AMI)",
    "OrganizationalUnit": "Service Processors",
    "State": "Georgia"
  },
  "KeyUsage": [
    "KeyEncipherment",
    "NonRepudiation",
    "DigitalSignature"
  ],
  "Name": "Certificate Instance",
  "Oem": {
    "Ami": {
      "@odata.type": "#AMICaCert.v1_0_0.AMICaCert"
    }
  },
  "Subject": {
    "City": "Norcross",
    "CommonName": "megarac.com",
    "Country": "US",
    "Email": "support@ami.com",
    "Organization": "American Megatrends International LLC (AMI)",
    "OrganizationalUnit": "Service Processors",
    "State": "Georgia"
  },
  "ValidNotAfter": "2034-8-23T13:03:00+00:00",
  "ValidNotBefore": "2019-8-27T13:03:00+00:00"
}
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]
```

## Import signed cert


```sh
curl -skin -u XXXXXX:XXXXXX -X POST "https://[${IP}]/redfish/v1/CertificateService/Actions/CertificateService.ReplaceCertificate" \
--header 'Content-Type: application/json' \
--data-raw '{
    "CertificateUri": {
        "@odata.id": "/redfish/v1/Managers/Self/NetworkProtocol/HTTPS/Certificates/1"
    },
    "CertificateString": "'"${CERT_STR}"'",
    "CertificateType": "PEM"
}'
```

## Import cert

```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ curl -skin -u XXXXXX:XXXXXX -X POST "https://[${IP}]/redfish/v1/CertificateService/Actions/CertificateService.ReplaceCertificate" \
> --header 'Content-Type: application/json' \
> --data-raw '{
>     "CertificateUri": {
>         "@odata.id": "/redfish/v1/Managers/Self/NetworkProtocol/HTTPS/Certificates/1"
>     },
>     "CertificateString": "'"${CERT_STR}"'",
>     "CertificateType": "PEM"
> }'
HTTP/1.1 100 Continue
Transfer-Encoding: chunked
Date: Fri, 03 Nov 2023 21:13:10 GMT
Server: lighttpd

HTTP/1.1 204 No Content
Server: AMI MegaRAC Redfish Service
Access-Control-Allow-Origin: *
Access-Control-Expose-Headers: X-Auth-Token
Access-Control-Allow-Headers: X-Auth-Token
Access-Control-Allow-Credentials: true
Cache-Control: no-cache, must-revalidate
ETag: "1699034003"
OData-Version: 4.0
Date: Fri, 03 Nov 2023 21:13:19 GMT

(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$


```

## Verify that cert is now on bmc

### openssl

```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ curl -skin -u XXXXXX:XXXXXX -X POST "https://[${IP}]/redfish/v1/CertificateService/Actions/CertificateService.ReplaceCertificate" \
> --header 'Content-Type: application/json' \
> --data-raw '{
>     "CertificateUri": {
>         "@odata.id": "/redfish/v1/Managers/Self/NetworkProtocol/HTTPS/Certificates/1"
>     },
>     "CertificateString": "'"${CERT_STR}"'",
>     "CertificateType": "PEM"
> }'
HTTP/1.1 100 Continue
Transfer-Encoding: chunked
Date: Fri, 03 Nov 2023 21:13:10 GMT
Server: lighttpd

HTTP/1.1 204 No Content
Server: AMI MegaRAC Redfish Service
Access-Control-Allow-Origin: *
Access-Control-Expose-Headers: X-Auth-Token
Access-Control-Allow-Headers: X-Auth-Token
Access-Control-Allow-Credentials: true
Cache-Control: no-cache, must-revalidate
ETag: "1699034003"
OData-Version: 4.0
Date: Fri, 03 Nov 2023 21:13:19 GMT

(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$ echo | openssl s_client -connect [${IP}]:443 -showcerts
CONNECTED(00000003)
Can't use SSL_get_servername
depth=0 C = US, ST = Texas, L = Westlake, O = "Verizon Data Services, LLC", OU = VCP Far Edge, CN = welktxfe-05400001-rz-le1pts6-002.faredge.vzwops.com
verify error:num=20:unable to get local issuer certificate
verify return:1
depth=0 C = US, ST = Texas, L = Westlake, O = "Verizon Data Services, LLC", OU = VCP Far Edge, CN = welktxfe-05400001-rz-le1pts6-002.faredge.vzwops.com
verify error:num=21:unable to verify the first certificate
verify return:1
depth=0 C = US, ST = Texas, L = Westlake, O = "Verizon Data Services, LLC", OU = VCP Far Edge, CN = welktxfe-05400001-rz-le1pts6-002.faredge.vzwops.com
verify return:1
---
Certificate chain
 0 s:C = US, ST = Texas, L = Westlake, O = "Verizon Data Services, LLC", OU = VCP Far Edge, CN = welktxfe-05400001-rz-le1pts6-002.faredge.vzwops.com
   i:C = US, ST = TX, L = Westlake, O = Verizon, OU = Verizon Sourcing LLC, CN = Verizon Network WELKTXFE LAB 1 2 RSA ICA
-----BEGIN CERTIFICATE-----
MIIFYTCCBEmgAwIBAgIUEDtGa0jsYmz84njl0cSLGzgg8T4wDQYJKoZIhvcNAQEL
BQAwgZExCzAJBgNVBAYTAlVTMQswCQYDVQQIDAJUWDERMA8GA1UEBwwIV2VzdGxh
a2UxEDAOBgNVBAoMB1Zlcml6b24xHTAbBgNVBAsMFFZlcml6b24gU291cmNpbmcg
TExDMTEwLwYDVQQDDChWZXJpem9uIE5ldHdvcmsgV0VMS1RYRkUgTEFCIDEgMiBS
U0EgSUNBMB4XDTIxMDcxNTIxNTI0MVoXDTMxMDcxMzIxNTI0MVowgaoxCzAJBgNV
BAYTAlVTMQ4wDAYDVQQIDAVUZXhhczERMA8GA1UEBwwIV2VzdGxha2UxIzAhBgNV
BAoMGlZlcml6b24gRGF0YSBTZXJ2aWNlcywgTExDMRUwEwYDVQQLDAxWQ1AgRmFy
IEVkZ2UxPDA6BgNVBAMMM3dlbGt0eGZlLTA1NDAwMDAxLXJ6LWxlMXB0czYtMDAy
LmZhcmVkZ2Uudnp3b3BzLmNvbTCCAiIwDQYJKoZIhvcNAQEBBQADggIPADCCAgoC
ggIBALld5Qbio4f7JKPt5NUAsxAsfRFVexeeNKZn0niktfiIXAvy7sEIBKNijZTD
YIhNIgiBkYUf3X2fJfdwZ3VWhAJzdcL/sd+PeBXeZ/2m29kDMlN0tdm9ruZMANzo
qaDyKnSfJLlVJqQToIrrXEv2FkI7diwvxKWkQrxjGwqgpyABJm4VsCBgqrYr3uwD
CaVkROPyfiDS3K+cOKtI7K0DIYLjCI+li/1YOBEGqufPOGoRObsWyC/6yP1TPI7/
joMM0r1/rLdz1wOnOtmuk2Enpn8pFVlvkxL2YpZ3NbmVV2mspdlDKVN0YmKt5ccl
o2tF4monyLgq4lrND6hlJy380Uz8C+5mDQy6oV4Da91hXLWlb7XbPdZrjVsV9sBu
QO+TkAod8U1ug5vAYEQL6Nffz9nWXkxK6TbpyPpefu0FgX1sorCPWXohP0wZTP3r
/i+JXk+ij6oYXCMYA9SzDr927bnavfRJZEnDwwVhM9NJ9YWVncO7w0wgiXcRF+Sc
R0ROC9PFrJjjKWdwOoOr9VoCG6RZK7StYmteGFVvQM1bitSiPFZeXutz6Dd2VfKW
24doXSdfg1wV3FyywWfSLFAMIMjGbuft1tBio898XApnBpO9+3tmB/nSrOsLP6lP
hT5iGYqdMJ4vVjtU9KmXCqH1qxenPsKLs0VPhE4xvhZsfkdfAgMBAAGjgZUwgZIw
UAYDVR0RBEkwR4Izd2Vsa3R4ZmUtMDU0MDAwMDEtcnotbGUxcHRzNi0wMDIuZmFy
ZWRnZS52endvcHMuY29thxAmB/FgABCQhADOBAoAAOACMB0GA1UdDgQWBBSy25eD
fteCNDBsZzblWAi24ppRYDAfBgNVHSMEGDAWgBS+0KD7lwLbyLuUEtRdut6q6LOm
xjANBgkqhkiG9w0BAQsFAAOCAQEAMSxXJVBVG9uGH/0MNJgMYEh8PQGPXjuNeKj8
5xy2beaaFY6r6r1txJ0xN5Wu/i5+JPtrg+ykAHlEiIRx8St7dZ3jADmP0y0Jj8aE
uuHaUsxoXoYc0H2lO2rM2wlpT8Wi/cI0yVDpnG2vVBkoFJPPcBo/2LV3yOcNwbac
obGnyAFjeIaCC81m7Jyf6JqjDceo6os9YUbPTW4RUYM0BEWUWri2PeXoXAG2ARGp
eCP2pTC003GN5/HUcszUSVqI1DS2m5IF9uRglQE08LhS7jxyxSugZ1IqT+eEH3Un
VNzUEMzl8Vjrl/orKQoK1RmOWG3Th0yhJ83b7tacHeu8l51D9A==
-----END CERTIFICATE-----
---
Server certificate
subject=C = US, ST = Texas, L = Westlake, O = "Verizon Data Services, LLC", OU = VCP Far Edge, CN = welktxfe-05400001-rz-le1pts6-002.faredge.vzwops.com

issuer=C = US, ST = TX, L = Westlake, O = Verizon, OU = Verizon Sourcing LLC, CN = Verizon Network WELKTXFE LAB 1 2 RSA ICA

---
No client certificate CA names sent
Peer signing digest: SHA256
Peer signature type: RSA-PSS
Server Temp Key: ECDH, P-256, 256 bits
---
SSL handshake has read 2319 bytes and written 691 bytes
Verification error: unable to verify the first certificate
---
New, TLSv1.3, Cipher is TLS_AES_256_GCM_SHA384
Server public key is 4096 bit
Secure Renegotiation IS NOT supported
Compression: NONE
Expansion: NONE
No ALPN negotiated
Early data was not sent
Verify return code: 21 (unable to verify the first certificate)
---
DONE
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 vcp-fe-ib-automation]$
```

## Redfish 

```log

```


```log

```



