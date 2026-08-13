# HPE ILO5 3.06 BIOS H08 v2.12
# HPE Sapphire Rapids E910t server
# 8/28/24 James Patchett - MTCE Lab VCPfe
# BMC/ILO Sensor validation MEAKV-1789

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
### List all sensors on the machine
### Validate no sensors are experiencing issues, or not showing data

```log
[XXXXXX@vcpe-jumpserver ~]$ ssh XXXXXX@2607:f160:10:80b1:ce:40a:0:f402
Release 22.12
------------------------------------------------------------------------
W A R N I N G *** W A R N I N G *** W A R N I N G *** W A R N I N G ***
------------------------------------------------------------------------
THIS IS A PRIVATE COMPUTER SYSTEM.
This computer system including all related equipment, network devices
(specifically including Internet access), are provided only for authorized use.
All computer systems may be monitored for all lawful purposes, including to
ensure that their use is authorized, for management of the system, to
facilitate protection against unauthorized access, and to verify security
procedures, survivability and operational security. Monitoring includes active
attacks by authorized personnel and their entities to test or verify the
security of the system. During monitoring, information may be examined,
recorded, copied and used for authorized purposes. All information including
personal information, placed on or sent over this system may be monitored. Uses
of this system, authorized or unauthorized, constitutes consent to monitoring
of this system. Unauthorized use may subject you to criminal prosecution.
Evidence of any such unauthorized use collected during monitoring may be used
for administrative, criminal or other adverse action. Use of this system
constitutes consent to monitoring for these purposes.

XXXXXX@2607:f160:10:80b1:ce:40a:0:f402's password:

XXXXXX Unauthorized access to this system is forbidden and will be
prosecuted by law. By accessing this system, you agree that your
actions may be monitored if unauthorized usage is suspected.


====================================================================
         SYSTEM: welktxsr-d931883-001
====================================================================


Linux controller-0 5.10.0-6-rt-amd64 #1 SMP PREEMPT_RT StarlingX Debian 5.10.177-1.stx.76 (2024-03-29 x86_64

WARNING: Unauthorized access to this system is forbidden and will be
prosecuted by law. By accessing this system, you agree that your
actions may be monitored if unauthorized usage is suspected.


====================================================================
         SYSTEM: welktxsr-d931883-001
====================================================================


Linux controller-0 5.10.0-6-rt-amd64 #1 SMP PREEMPT_RT StarlingX Debian 5.10.177-1.stx.76 (2024-03-29 x86_64
Last login: Fri Jun 28 22:08:57 2024 from 2607:f160:0:3042:cd:290:0:11
XXXXXX@controller-0:~$ source /etc/platform/openrc
[XXXXXX@controller-0 ~(keystone_admin)]$ sudo -i
Password:
XXXXXX ipmitool sensor
UID              | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
SysHealth_Stat   | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
01-Inlet Ambient | 32.000     | degrees C  | ok    | na        | na        | na        | na        | 62.000    | 66.000
02-CPU 1 PkgTmp  | 59.000     | degrees C  | ok    | na        | na        | na        | na        | 91.000    | na
03-P1 DIMM 1-6   | 42.000     | degrees C  | ok    | na        | na        | na        | na        | 90.000    | na
04-P1 PMM 1-6    | na         |            | na    | na        | na        | na        | na        | 82.000    | na
05-P1 DIMM 7-12  | 50.000     | degrees C  | ok    | na        | na        | na        | na        | 90.000    | na
06-P1 PMM 7-12   | na         |            | na    | na        | na        | na        | na        | 82.000    | na
07-VR P1         | 57.000     | degrees C  | ok    | na        | na        | na        | na        | 110.000   | na
08-Chipset       | 48.000     | degrees C  | ok    | na        | na        | na        | na        | 100.000   | na
09-BMC           | 54.000     | degrees C  | ok    | na        | na        | na        | na        | 110.000   | na
10-M2            | 40.000     | degrees C  | ok    | na        | na        | na        | na        | 80.000    | na
16-PCI 1 Zone    | 32.000     | degrees C  | ok    | na        | na        | na        | na        | 70.000    | 75.000
18-PCI 2 Zone    | 32.000     | degrees C  | ok    | na        | na        | na        | na        | 70.000    | 75.000
20-PCI 3 Zone    | 32.000     | degrees C  | ok    | na        | na        | na        | na        | 70.000    | 75.000
21-PCI 4         | na         |            | na    | na        | na        | na        | na        | 95.000    | na
22-PCI 4 Zone    | na         |            | na    | na        | na        | na        | na        | 70.000    | 75.000
27-Sys Exhaust 1 | 51.000     | degrees C  | ok    | na        | na        | na        | na        | 85.000    | na
Fan 1            | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
Fan 1 DutyCycle  | 21.952     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 1 Presence   | 0x0        | discrete   | 0x0280| na        | na        | na        | na        | na        | na
Fan 2            | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
Fan 2 DutyCycle  | 21.952     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 2 Presence   | 0x0        | discrete   | 0x0280| na        | na        | na        | na        | na        | na
Fan 3            | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
Fan 3 DutyCycle  | 17.640     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 3 Presence   | 0x0        | discrete   | 0x0280| na        | na        | na        | na        | na        | na
Fan 4            | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
Fan 4 DutyCycle  | 17.640     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 4 Presence   | 0x0        | discrete   | 0x0280| na        | na        | na        | na        | na        | na
Fan 5            | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
Fan 5 DutyCycle  | 17.640     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 5 Presence   | 0x0        | discrete   | 0x0280| na        | na        | na        | na        | na        | na
Fan 6            | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
Fan 6 DutyCycle  | 17.640     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 6 Presence   | 0x0        | discrete   | 0x0280| na        | na        | na        | na        | na        | na
Power Supply 1   | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
PS 1 Input       | 150.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
Power Supply 2   | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
PS 2 Input       | 2550.000   | Watts      | ok    | na        | na        | na        | na        | na        | na
Power Meter      | 130.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
Fans             | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
Memory Status    | 0x0        | discrete   | 0x4080| na        | na        | na        | na        | na        | na
Megacell Status  | na         | discrete   | na    | na        | na        | na        | na        | na        | na
Intrusion        | na         | discrete   | na    | na        | na        | na        | na        | na        | na
CPU Utilization  | 7.000      | unspecified | ok    | na        | na        | na        | na        | na        | na
PS 1 Output      | 0.000      | Watts      | ok    | na        | na        | na        | na        | na        | na
PS_Volt_Out_01   | 0.000      | Volts      | ok    | na        | na        | na        | na        | na        | na
PS_Volt_In_01    | 212.000    | Volts      | ok    | na        | na        | na        | na        | na        | na
PS_Curr_Out_01   | 0.000      | Amps       | ok    | na        | na        | na        | na        | na        | na
PS_Curr_In_01    | 0.300      | Amps       | ok    | na        | na        | na        | na        | na        | na
PS 2 Output      | 0.000      | Watts      | ok    | na        | na        | na        | na        | na        | na
PS_Volt_Out_02   | 0.000      | Volts      | ok    | na        | na        | na        | na        | na        | na
PS_Volt_In_02    | 212.000    | Volts      | ok    | na        | na        | na        | na        | na        | na
PS_Curr_Out_02   | 0.000      | Amps       | ok    | na        | na        | na        | na        | na        | na
PS_Curr_In_02    | 0.300      | Amps       | ok    | na        | na        | na        | na        | na        | na
15.1-PCI 1-Netwo | 66.000     | degrees C  | ok    | na        | na        | na        | 95.000    | 105.000   | 115.000
15.2-PCI 1-SFP28 | 41.000     | degrees C  | ok    | na        | na        | na        | 73.000    | 78.000    | 0.000
15.3-PCI 1-SFP28 | 37.000     | degrees C  | ok    | na        | na        | na        | 70.000    | 75.000    | 0.000
15.4-PCI 1-SFP28 | 37.000     | degrees C  | ok    | na        | na        | na        | 70.000    | 75.000    | 0.000
15.5-PCI 1-SFP28 | 37.000     | degrees C  | ok    | na        | na        | na        | 70.000    | 75.000    | 0.000
17.1-PCI 2-Netwo | 69.000     | degrees C  | ok    | na        | na        | na        | 95.000    | 105.000   | 115.000
17.2-PCI 2-SFP28 | 31.000     | degrees C  | ok    | na        | na        | na        | 70.000    | 75.000    | 0.000
17.3-PCI 2-SFP28 | 33.000     | degrees C  | ok    | na        | na        | na        | 70.000    | 75.000    | 0.000
19.1-PCI 3-Netwo | 63.000     | degrees C  | ok    | na        | na        | na        | 95.000    | 105.000   | 115.000
19.2-PCI 3-SFP28 | 37.000     | degrees C  | ok    | na        | na        | na        | 73.000    | 78.000    | 0.000
19.3-PCI 3-SFP28 | 33.000     | degrees C  | ok    | na        | na        | na        | 70.000    | 75.000    | 0.000
LOM_Link_P1      | na         | discrete   | na    | na        | na        | na        | na        | na        | na
NIC_Link_01P1    | 0x0        | discrete   | 0x0280| na        | na        | na        | na        | na        | na
NIC_Link_01P2    | 0x0        | discrete   | 0x0280| na        | na        | na        | na        | na        | na
NIC_Link_01P3    | 0x0        | discrete   | 0x0280| na        | na        | na        | na        | na        | na
NIC_Link_01P4    | na         | discrete   | na    | na        | na        | na        | na        | na        | na
NIC_Link_02P1    | na         | discrete   | na    | na        | na        | na        | na        | na        | na
NIC_Link_02P2    | 0x0        | discrete   | 0x0280| na        | na        | na        | na        | na        | na
NIC_Link_02P3    | na         | discrete   | na    | na        | na        | na        | na        | na        | na
NIC_Link_02P4    | 0x0        | discrete   | 0x0280| na        | na        | na        | na        | na        | na
NIC_Link_03P1    | 0x0        | discrete   | 0x0280| na        | na        | na        | na        | na        | na
NIC_Link_03P2    | 0x0        | discrete   | 0x0280| na        | na        | na        | na        | na        | na
NIC_Link_03P3    | na         | discrete   | na    | na        | na        | na        | na        | na        | na
NIC_Link_03P4    | na         | discrete   | na    | na        | na        | na        | na        | na        | na
CPU_Stat_C1      | 0x0        | discrete   | 0x8080| na        | na        | na        | na        | na        | na
root@controller-0:~#

```

### Test has PASSED
