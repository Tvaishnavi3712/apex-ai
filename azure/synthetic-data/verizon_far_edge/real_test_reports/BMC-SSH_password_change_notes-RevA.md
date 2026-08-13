# MTCE VCPfe James Patchett 4/6/26
# How to change password with BMC via SSH 
# Document covers HPe e910t/e920t/e930t, ZT Triton/Proteus/Galene, and Dell XR8620t/R7615

## e910t Host 2607:f160:10:922a:ce:406:0:1000

### Login to the BMC IPV6 Address as user "XXXXXX" and change the password with the following command

```sh
set /map1/accounts1/XXXXXX password=<NEW-PASSWORD>
```

### Example password change

```log
[XXXXXX@welktxme-jump140 ~]$ ssh XXXXXX@2607:f160:10:922a:ce:406:0:1000
XXXXXX@2607:f160:10:922a:ce:406:0:1000's password:
XXXXXX logged-in to welktxef-931881-rh-le0e910-005.faredge.vzwops.com(192.168.1.10 / FE80::B67A:F1FF:FEDE:201F)
Integrated Lights-Out 5
iLO Advanced 3.06 at  Jul 10 2024
Server Name: welktxef-931881-rh-le0e910-005
Server Power: On

</>hpiLO-> set /map1/accounts1/XXXXXX password=XXXXXX

status=0
status_tag=COMMAND COMPLETED
Mon Apr  6 22:35:20 2026

User information modified successfully.




</>hpiLO-> exit

status=0
status_tag=COMMAND COMPLETED
Mon Apr  6 22:35:22 2026




CLI session stopped
Received disconnect from 2607:f160:10:922a:ce:406:0:1000 port 22:11:  Client Disconnect
Disconnected from 2607:f160:10:922a:ce:406:0:1000 port 22
[XXXXXX@welktxme-jump140 ~]$

```

## e920t Host 2607:f160:10:9249:ce:40a:0:e030

### Login to the BMC IPV6 Address as user "XXXXXX" and change the password with the following command

```sh
set /map1/accounts1/XXXXXX password=<NEW-PASSWORD>
```

### Example password change

```log
[XXXXXX@welktxme-jump140 ~]$ ssh XXXXXX@2607:f160:10:9249:ce:40a:0:e030
XXXXXX@2607:f160:10:9249:ce:40a:0:e030's password:
XXXXXX logged-in to welktxef-931885-rh-pe092s6-001.vcpfe.vzwops.com(192.168.1.10 / FE80::B67A:F1FF:FEDE:55CA)
Integrated Lights-Out 5
iLO Advanced 3.06 at  Jul 10 2024
Server Name: welktxef-931886-rh-pe092s6-001
Server Power: On

</>hpiLO-> set /map1/accounts1/XXXXXX password=XXXXXX

status=0
status_tag=COMMAND COMPLETED
Mon Apr  6 22:36:54 2026

User information modified successfully.




</>hpiLO-> exit

status=0
status_tag=COMMAND COMPLETED
Mon Apr  6 22:37:02 2026




CLI session stopped
Received disconnect from 2607:f160:10:9249:ce:40a:0:e030 port 22:11:  Client Disconnect
Disconnected from 2607:f160:10:9249:ce:40a:0:e030 port 22
[XXXXXX@welktxme-jump140 ~]$

```

## e930t Host 2607:f160:10:80c2:ce:40a:0:e004

### Login to the BMC IPV6 Address as user "XXXXXX" and change the password with the following command

```sh
set /map1/accounts1/XXXXXX password=<NEW-PASSWORD>
```

### Example password change

```log
[XXXXXX@welktxme-jump140 ~]$ ssh XXXXXX@2607:f160:10:80c2:ce:40a:0:e004
XXXXXX@2607:f160:10:80c2:ce:40a:0:e004's password:
XXXXXX denied, please try again.
XXXXXX@2607:f160:10:80c2:ce:40a:0:e004's password:
XXXXXX logged-in to welktxfb-1372466-rh-le093s3-001.faredge.vzwops.com(192.168.1.10 / FE80::5EED:8CFF:FEEF:AE0A)
Integrated Lights-Out 6
iLO Advanced 1.68 at  Apr 24 2025
Server Name:
Server Power: On

</>hpiLO->
set /map1/accounts1/XXXXXX password=XXXXXX
status=0
status_tag=COMMAND COMPLETED
Mon Apr  6 22:39:40 2026

User information modified successfully.




</>hpiLO-> exit

status=0
status_tag=COMMAND COMPLETED
Mon Apr  6 22:39:42 2026




CLI session stopped
Received disconnect from 2607:f160:10:80c2:ce:40a:0:e004 port 22:11:  Client Disconnect
Disconnected from 2607:f160:10:80c2:ce:40a:0:e004 port 22
[XXXXXX@welktxme-jump140 ~]$
```

## Dell SPR Host 2607:f160:10:823a:ce:40a:0:e010

### Verify where the "XXXXXX" account is, iDRAC has default root account as well, but we added XXXXXX to make same across all platforms.

### validate what user.id is root and which is XXXXXX with a redfish command

```sh
USER=XXXXXX
PASS=1verizon
BMC=2607:f160:10:823a:ce:40a:0:e010
curl -gsk -u $USER:$PASS https://[$BMC]/redfish/v1/AccountService/Accounts/2 | jq .UserName
curl -gsk -u $USER:$PASS https://[$BMC]/redfish/v1/AccountService/Accounts/3 | jq .UserName
```

### Example

```log
[XXXXXX@welktxme-jump140 ~]$ USER=XXXXXX
[XXXXXX@welktxme-jump140 ~]$ PASS=1verizon
[XXXXXX@welktxme-jump140 ~]$ BMC=2607:f160:10:823a:ce:40a:0:e010
[XXXXXX@welktxme-jump140 ~]$ curl -gsk -u $USER:$PASS https://[$BMC]/redfish/v1/AccountService/Accounts/2 | jq .UserName
"root"
[XXXXXX@welktxme-jump140 ~]$ curl -gsk -u $USER:$PASS https://[$BMC]/redfish/v1/AccountService/Accounts/3 | jq .UserName
"XXXXXX"
[XXXXXX@welktxme-jump140 ~]$
```

### you see normally user root is iDRAC.Users.2.Password XXXXXX XXXXXX is iDRAC.Users.3.Password, we needed to confirm this for the next step of changing the password with SSH.


### Login to the BMC IPV6 Address as user "XXXXXX" and change the password with the following command

```sh
set iDRAC.Users.3.Password <new_password>
```

### Example password change

```log
[XXXXXX@welktxme-jump140 ~]$ ssh XXXXXX@2607:f160:10:823a:ce:40a:0:e010
Password:
XXXXXX iDRAC.Users.3.Password XXXXXX
[Key=iDRAC.Embedded.1#Users.3]
Object value modified successfully
racadm>>exit

Connection to 2607:f160:10:823a:ce:40a:0:e010 closed.
[XXXXXX@welktxme-jump140 ~]$
```

## Procedure for ZT hosts TBD

## ZT Triton Host 2607:f160:10:9075:ce:406:0:1000

## ZT Protues Host 2607:f160:10:80b1:ce:40a:0:e003

## ZT Galene Host 2607:f160:10:8803:ce:40a:0:e005




