# HPE ILO6 1.57 BIOS H11 v1.11
# HPE Sapphire Rapids E930t server
# 3/24/24 James Patchett - MTCE Lab VCPfe
# Performance Test MEAKV-642-646 

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

## MEAKV-642
## Performance Test sudo ./ptat -ct 1 -b 0
## measure sensors first, then run load, then check during load

## Sensors
```log
root@controller-0:/home/XXXXXX/compile/Ptu#  ipmitool sensor| grep -e CPU -e DutyCycle
02-CPU 1 PkgTmp  | 74.000     | degrees C  | ok    | na        | na        | na        | na        | 91.000    | na
Fan 1 DutyCycle  | 17.640     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 2 DutyCycle  | 17.640     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 3 DutyCycle  | 17.640     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 4 DutyCycle  | 17.640     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 5 DutyCycle  | 17.640     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 6 DutyCycle  | 17.640     | percent    | ok    | na        | na        | na        | na        | na        | na
CPU Utilization  | 6.000      | unspecified | ok    | na        | na        | na        | na        | na        | na
CPU_Stat_C1      | 0x0        | discrete   | 0x8080| na        | na        | na        | na        | na        | na
root@controller-0:/home/XXXXXX/compile/Ptu#
```

## Initiate load 

```log
root@controller-0:/home/XXXXXX/compile/Ptu# ./ptat -ct 1 -b 0

Command: ./ptat -ct 1 -b 0

Intel(R) PTAT - Server Edition 4.4.0
Release Date: 12/19/2023
Copyright (C) 2023 Intel Corporation. All rights reserved.
Intel Confidential

>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> System Info:                   <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Host Name:                           controller-0
Host IP:                             169.254.202.1
OS Name:                             Debian GNU/Linux 11 (bullseye) 11
Kernel Version:                      Linux 5.10.0-6-rt-amd64 #1 SMP PREEMPT_RT StarlingX Debian 5.10.177-1.stx.73 (2023-11-25
BIOS Version:                        HPE, 1.11, 03/07/2024
Processor(s):                        1 Processor(s) Installed.
DIMM(s):                             8 DIMM(s) Installed.
Total System Memory:                 255208 MB
Available System Memory:             145150 MB


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Processor: [CPU_0]             <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU ID:                              0x000806F8 (Family 6 Model 8Fh Stepping 8)
CPU Brand Name:                      Intel(R) Xeon(R) Gold 6443N
CPU Code Name:                       Sapphire Rapids
CPU Type:                            Production Part
CPU Segment:                         Server
CPU PPIN:                            0x0000000000000000
CPU Base Frequency:                  1300 MHz
CPU Minimum Frequency:               800 MHz
CPU Maximum Turbo Frequency:         3600 MHz
Uncore Minimum Frequency:            1600 MHz
Uncore Maximum Frequency:            1600 MHz
L2 Cache:                            32 x 2048 KB
L3 Cache:                            61440 KB
Hyper-threading:                     Enabled
Microcode Update Revision:           0x2B000571
Number of Physcial Core(s):          32
Number of Logical Core(s):           64
Turbo Boost:                         Enabled
Turbo Boost Frequency:
 IA/SSE:
    1 - 16 Cores (Fused/Resolved):   3600 / 3600 (MHz)
   17 - 20 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   21 - 24 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   25 - 26 Cores (Fused/Resolved):   2900 / 2900 (MHz)
   27 - 32 Cores (Fused/Resolved):   2700 / 2700 (MHz)
 AVX2:
    1 - 16 Cores (Fused/Resolved):   3600 / 3600 (MHz)
   17 - 20 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   21 - 24 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   25 - 26 Cores (Fused/Resolved):   2800 / 2800 (MHz)
   27 - 32 Cores (Fused/Resolved):   2600 / 2600 (MHz)
 AVX-512:
    1 - 16 Cores (Fused/Resolved):   3600 / 3600 (MHz)
   17 - 20 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   21 - 24 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   25 - 26 Cores (Fused/Resolved):   2700 / 2700 (MHz)
   27 - 32 Cores (Fused/Resolved):   2500 / 2500 (MHz)
OVOLT_OVRD Supported:                0
OVOLT_OVRD Disabled:                 1
Platform ID:                         0x0
Platform Info:                       0x8405082EF4810D00
Thermal Design Power (TDP):          195 W
Power Limit 1 - Long Duration:       Enabled, Clamp ON , Power = 195 W, Time = 10.00 sec
Power Limit 2 - Short Duration:      Enabled, Clamp ON , Power = 234 W
Config TDP Level Supported:          3
Config TDP Level 1:                  195.0 W (110.0 W - 526.0 W), 0 MHz
Config TDP Level 2:                  195.0 W (110.0 W - 526.0 W), 0 MHz
Current Config TDP Level:            Nominal [Unlocked]
Tprochot:                            91 C
TCC Offset:                          0
CAPID0:                              0x42188138
CAPID1:                              0x5AC400C2
CAPID2:                              0xFF900003
CAPID3:                              0x07804000
CAPID4:                              0x04042EA0
CAPID5:                              0x6F0001EB
CAPID6:                              0xFDFEFFFF
CAPID7:                              0x00000003
CAPID8:                              0xFDFEFFFF
CAPID9:                              0x00000003
CAPID10:                             0x00000000


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Memory: [MEM_0]                <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Number of DIMM(s):                   8
Number of Active Channel(s):         8
DRAM Power Meter Disabled:           0
DRAM RAPL Disabled:                  0
DRAM TDP Power:                      Min = 15.0 W, Max = 66.0 W, Time = 0.31 sec
DRAM / NVDIMM Info:
  MC 0, Chnl 0, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 0, Chnl 1, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 1, Chnl 2, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 1, Chnl 3, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 2, Chnl 4, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 2, Chnl 5, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 3, Chnl 6, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 3, Chnl 7, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Platform Controller Hub: [PCH] <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
PCH Device ID:                       8086:1B81 (EBG)
PCH Stepping:                        17
PCH Thermal Sensor Enable:           0
PCH Hot Level (PHL):                 115


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> PTAT Current Settings:         <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU Test Selected:                   1
MEM Test Selected:                   1
CPU Mask:                            0xFFFFFFFF
CPU Core Mask:                       0xFFFFFFFFFFFFFFFF
CPU Thread Mask:                     0xFFFFFFFFFFFFFFFF
MEM Mask:                            0xFFFF
MEM Core Mask:                       0x1
MEM Thread Mask:                     0x1
Core Power Level:                    100
Memory Power Level:                  100
Turbo Enabled:                       Yes
AVX Test Level:                      1
Pmax Pre-sync:                       5000 ms
Pmax Post-sync:                      3000 ms
Pmax Idle:                           2000 ms
Run Time:                            0 (Forever)
PTAT Mon CPU Mask:                   0xFFFFFFFFFFFFFFFF
PTAT Mon Core Mask:                  0xFFFFFFFFFFFFFFFF
PTAT Mon MEM Mask:                   0xFFFFFFFF
PTAT Mon Filter Mask:                0x1F
PTAT Mon Update Interval:            1000000 usec
PTAT Mon Long Level:                 0
PTAT Mon Timestamp:                  No
Log Enabled:                         No
Log Directory:                       /root/ptat/log
Log File Prefix:                     <timestamp>
Log Message File:                    <timestamp>_ptatmsg.txt
Log Monitor File:                    <timestamp>_ptatmon.txt
CSV Enabled:                         No
PTAT License Auto Accept:            No
PTAT Driver Loaded:                  Yes

[03/29/24 23:10:48 UTC] PTAT started.

Press <Ctrl-C> to stop.


CPU_0: [IDLE] CFreq=1302, UFreq=1600, PState=1, Util=1.56, IPC=0.81, Temp=74, DTS=17, Power=72.7, Volt=0.661, UVolt=0.725
MEM_0: [IDLE] Power=11.61, Temp=43, Read=0.0, Write=0.0
MEM_0: [TESTCFG] TestSel=1 (Read), CoreMask=0x1, ThreadMask=0x1, PwrLevel=100, Turbo=0
MEM_0: [RUNNING] Power=11.19, Temp=43, Read=827.5, Write=278.1
CPU_0: , CoreMask=0xFFFFFFFFFFFFFFFF, ThreadMask=0xFFFFFFFFFFFFFFFF, PwrLevel=TDP, Turbo=0

```

## Ptu monitoring

```log
root@controller-0:/home/XXXXXX/compile/Ptu# ./ptat -mon

Command: ./ptat -mon

Intel(R) PTAT - Server Edition 4.4.0
Release Date: 12/19/2023
Copyright (C) 2023 Intel Corporation. All rights reserved.
Intel Confidential

>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> System Info:                   <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Host Name:                           controller-0
Host IP:                             169.254.202.1
OS Name:                             Debian GNU/Linux 11 (bullseye) 11
Kernel Version:                      Linux 5.10.0-6-rt-amd64 #1 SMP PREEMPT_RT StarlingX Debian 5.10.177-1.stx.73 (2023-11-25
BIOS Version:                        HPE, 1.11, 03/07/2024
Processor(s):                        1 Processor(s) Installed.
DIMM(s):                             8 DIMM(s) Installed.
Total System Memory:                 255208 MB
Available System Memory:             145086 MB


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Processor: [CPU_0]             <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU ID:                              0x000806F8 (Family 6 Model 8Fh Stepping 8)
CPU Brand Name:                      Intel(R) Xeon(R) Gold 6443N
CPU Code Name:                       Sapphire Rapids
CPU Type:                            Production Part
CPU Segment:                         Server
CPU PPIN:                            0x0000000000000000
CPU Base Frequency:                  1300 MHz
CPU Minimum Frequency:               800 MHz
CPU Maximum Turbo Frequency:         3600 MHz
Uncore Minimum Frequency:            1600 MHz
Uncore Maximum Frequency:            1600 MHz
L2 Cache:                            32 x 2048 KB
L3 Cache:                            61440 KB
Hyper-threading:                     Enabled
Microcode Update Revision:           0x2B000571
Number of Physcial Core(s):          32
Number of Logical Core(s):           64
Turbo Boost:                         Disabled
Turbo Boost Frequency:
 IA/SSE:
    1 - 16 Cores (Fused/Resolved):   3600 / 3600 (MHz)
   17 - 20 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   21 - 24 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   25 - 26 Cores (Fused/Resolved):   2900 / 2900 (MHz)
   27 - 32 Cores (Fused/Resolved):   2700 / 2700 (MHz)
 AVX2:
    1 - 16 Cores (Fused/Resolved):   3600 / 3600 (MHz)
   17 - 20 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   21 - 24 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   25 - 26 Cores (Fused/Resolved):   2800 / 2800 (MHz)
   27 - 32 Cores (Fused/Resolved):   2600 / 2600 (MHz)
 AVX-512:
    1 - 16 Cores (Fused/Resolved):   3600 / 3600 (MHz)
   17 - 20 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   21 - 24 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   25 - 26 Cores (Fused/Resolved):   2700 / 2700 (MHz)
   27 - 32 Cores (Fused/Resolved):   2500 / 2500 (MHz)
OVOLT_OVRD Supported:                0
OVOLT_OVRD Disabled:                 1
Platform ID:                         0x0
Platform Info:                       0x8405082EF4810D00
Thermal Design Power (TDP):          195 W
Power Limit 1 - Long Duration:       Enabled, Clamp ON , Power = 195 W, Time = 10.00 sec
Power Limit 2 - Short Duration:      Enabled, Clamp ON , Power = 234 W
Config TDP Level Supported:          3
Config TDP Level 1:                  195.0 W (110.0 W - 526.0 W), 0 MHz
Config TDP Level 2:                  195.0 W (110.0 W - 526.0 W), 0 MHz
Current Config TDP Level:            Nominal [Unlocked]
Tprochot:                            91 C
TCC Offset:                          0
CAPID0:                              0x42188138
CAPID1:                              0x5AC400C2
CAPID2:                              0xFF900003
CAPID3:                              0x07804000
CAPID4:                              0x04042EA0
CAPID5:                              0x6F0001EB
CAPID6:                              0xFDFEFFFF
CAPID7:                              0x00000003
CAPID8:                              0xFDFEFFFF
CAPID9:                              0x00000003
CAPID10:                             0x00000000


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Memory: [MEM_0]                <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Number of DIMM(s):                   8
Number of Active Channel(s):         8
DRAM Power Meter Disabled:           0
DRAM RAPL Disabled:                  0
DRAM TDP Power:                      Min = 15.0 W, Max = 66.0 W, Time = 0.31 sec
DRAM / NVDIMM Info:
  MC 0, Chnl 0, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 0, Chnl 1, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 1, Chnl 2, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 1, Chnl 3, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 2, Chnl 4, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 2, Chnl 5, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 3, Chnl 6, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 3, Chnl 7, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Platform Controller Hub: [PCH] <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
PCH Device ID:                       8086:1B81 (EBG)
PCH Stepping:                        17
PCH Thermal Sensor Enable:           0
PCH Hot Level (PHL):                 115


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> PTAT Current Settings:         <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU Test Selected:                   0
MEM Test Selected:                   0
CPU Mask:                            0xFFFFFFFF
CPU Core Mask:                       0xFFFFFFFFFFFFFFFF
CPU Thread Mask:                     0xFFFFFFFFFFFFFFFF
MEM Mask:                            0xFFFF
MEM Core Mask:                       0xFFFFFFFFFFFFFFFF
MEM Thread Mask:                     0xFFFFFFFFFFFFFFFF
Core Power Level:                    100
Memory Power Level:                  100
Turbo Enabled:                       No
AVX Test Level:                      1
Pmax Pre-sync:                       5000 ms
Pmax Post-sync:                      3000 ms
Pmax Idle:                           2000 ms
Run Time:                            0 (Forever)
PTAT Mon CPU Mask:                   0xFFFFFFFFFFFFFFFF
PTAT Mon Core Mask:                  0xFFFFFFFFFFFFFFFF
PTAT Mon MEM Mask:                   0xFFFFFFFF
PTAT Mon Filter Mask:                0x1F
PTAT Mon Update Interval:            1000000 usec
PTAT Mon Long Level:                 0
PTAT Mon Timestamp:                  No
Log Enabled:                         No
Log Directory:                       /root/ptat/log
Log File Prefix:                     <timestamp>
Log Message File:                    <timestamp>_ptatmsg.txt
Log Monitor File:                    <timestamp>_ptatmon.txt
CSV Enabled:                         No
PTAT License Auto Accept:            No
PTAT Driver Loaded:                  Yes

[03/29/24 23:11:33 UTC] PTAT started.

Press <Ctrl-C> to stop.


 Index Device Cor Thr CFreq UFreq  PState   Util  IPC     C0     C1     C6    PC2    PC6 MC Ch Sl  Temp DTS  Power  Volt UVolt TStat TLog #TL TMargin MCPMargin
     0   CPU0   -   -  1303  1600       1 100.00 6.02 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 140.96 0.651 0.723   0x0  0x0   0   2.156     2.156
     0   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    57   -  10.92     -     -     -  0x0   -       -         -
     1   CPU0   -   -  1300  1600       1 100.00 6.01 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 141.03 0.651 0.723   0x0  0x0   0   2.234     2.234
     1   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    57   -  11.09     -     -     -  0x0   -       -         -
     2   CPU0   -   -  1300  1600       1 100.00 5.99 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 141.02 0.648 0.723   0x0  0x0   0   2.109     2.109
     2   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    57   -  11.07     -     -     -  0x0   -       -         -
     3   CPU0   -   -  1300  1600       1 100.00 5.99 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 138.43 0.651 0.723   0x0  0x0   0   2.016     2.016
     3   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    57   -  11.06     -     -     -  0x0   -       -         -
     4   CPU0   -   -  1300  1600       1 100.00 5.98 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 143.08 0.648 0.723   0x0  0x0   0   2.047     2.047
     4   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    57   -  11.08     -     -     -  0x0   -       -         -
     5   CPU0   -   -  1300  1600       1 100.00 6.01 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 141.27 0.648 0.723   0x0  0x0   0   2.094     2.094
     5   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    57   -  10.76     -     -     -  0x0   -       -         -
     6   CPU0   -   -  1300  1600       1 100.00 5.99 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 140.87 0.648 0.723   0x0  0x0   0   1.906     1.906
     6   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    57   -  11.43     -     -     -  0x0   -       -         -
     7   CPU0   -   -  1300  1600       1 100.00 5.98 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 141.14 0.648 0.720   0x0  0x0   0   1.891     1.891
     7   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    57   -  11.21     -     -     -  0x0   -       -         -
     8   CPU0   -   -  1298  1600       1 100.00 5.98 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 141.20 0.648 0.720   0x0  0x0   0   1.938     1.938
     8   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    57   -  11.16     -     -     -  0x0   -       -         -
     9   CPU0   -   -  1302  1600       1 100.00 5.98 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 141.23 0.648 0.723   0x0  0x0   0   2.078     2.078
     9   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    56   -  11.16     -     -     -  0x0   -       -         -
    10   CPU0   -   -  1300  1600       1 100.00 5.98 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 141.41 0.648 0.723   0x0  0x0   0   2.000     2.000
    10   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    56   -  11.12     -     -     -  0x0   -       -         -
    11   CPU0   -   -  1300  1600       1 100.00 5.98 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 141.19 0.648 0.723   0x0  0x0   0   1.719     1.719
    11   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    56   -  11.08     -     -     -  0x0   -       -         -
    12   CPU0   -   -  1300  1600       1 100.00 5.98 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 141.09 0.648 0.720   0x0  0x0   0   1.719     1.719
    12   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    56   -  11.20     -     -     -  0x0   -       -         -
    13   CPU0   -   -  1297  1600       1 100.00 5.98 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 141.16 0.648 0.720   0x0  0x0   0   1.688     1.688
    13   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    56   -  11.19     -     -     -  0x0   -       -         -
    14   CPU0   -   -  1302  1600       1 100.00 5.99 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 141.09 0.648 0.720   0x0  0x0   0   1.828     1.828
    14   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    56   -  11.05     -     -     -  0x0   -       -         -
    15   CPU0   -   -  1301  1600       1 100.00 5.99 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 141.21 0.648 0.720   0x0  0x0   0   1.781     1.781
    15   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    56   -  11.02     -     -     -  0x0   -       -         -
    16   CPU0   -   -  1300  1600       1 100.00 5.99 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 141.16 0.648 0.720   0x0  0x0   0   1.641     1.641
    16   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    56   -  11.13     -     -     -  0x0   -       -         -
    17   CPU0   -   -  1300  1600       1 100.00 6.02 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 137.39 0.648 0.723   0x0  0x0   0   1.812     1.812
    17   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    56   -  10.86     -     -     -  0x0   -       -         -
    18   CPU0   -   -  1299  1600       1 100.00 5.97 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 145.68 0.648 0.720   0x0  0x0   0   1.750     1.750
    18   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    56   -  11.11     -     -     -  0x0   -       -         -
    19   CPU0   -   -  1301  1600       1 100.00 5.98 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 141.29 0.648 0.723   0x0  0x0   0   1.750     1.750
    19   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    56   -  11.21     -     -     -  0x0   -       -         -
    20   CPU0   -   -  1301  1600       1 100.00 5.98 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 141.43 0.648 0.723   0x0  0x0   0   1.672     1.672
    20   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    56   -  11.11     -     -     -  0x0   -       -         -
    21   CPU0   -   -  1300  1600       1 100.00 6.00 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 141.32 0.648 0.720   0x0  0x0   0   1.547     1.547
    21   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    56   -  10.95     -     -     -  0x0   -       -         -
    22   CPU0   -   -  1300  1600       1 100.00 6.01 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 141.34 0.648 0.720   0x0  0x0   0   1.656     1.656
    22   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    56   -  11.13     -     -     -  0x0   -       -         -
    23   CPU0   -   -  1300  1600       1 100.00 5.99 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 141.25 0.648 0.723   0x0  0x0   0   1.578     1.578
    23   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    56   -  11.11     -     -     -  0x0   -       -         -
    24   CPU0   -   -  1300  1600       1 100.00 6.01 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 141.39 0.648 0.723   0x0  0x0   0   1.594     1.594
    24   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    56   -  11.09     -     -     -  0x0   -       -         -
    25   CPU0   -   -  1300  1600       1 100.00 5.99 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 141.26 0.648 0.723   0x0  0x0   0   1.578     1.578
    25   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    56   -  10.96     -     -     -  0x0   -       -         -
    26   CPU0   -   -  1300  1600       1 100.00 6.01 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 140.99 0.648 0.723   0x0  0x0   0   1.453     1.453
    26   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    56   -  10.96     -     -     -  0x0   -       -         -
    27   CPU0   -   -  1300  1600       1 100.00 6.01 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 141.37 0.648 0.723   0x0  0x0   0   1.344     1.344
    27   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    56   -  10.99     -     -     -  0x0   -       -         -
    28   CPU0   -   -  1300  1600       1 100.00 6.03 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 141.22 0.648 0.723   0x0  0x0   0   1.359     1.359
    28   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    56   -  10.96     -     -     -  0x0   -       -         -
    29   CPU0   -   -  1300  1600       1 100.00 6.02 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 141.32 0.648 0.723   0x0  0x0   0   1.578     1.578
    29   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    56   -  11.02     -     -     -  0x0   -       -         -
    30   CPU0   -   -  1300  1600       1 100.00 6.00 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 141.11 0.648 0.723   0x0  0x0   0   1.453     1.453
    30   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    56   -  11.06     -     -     -  0x0   -       -         -
    31   CPU0   -   -  1300  1600       1 100.00 6.02 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 141.08 0.648 0.723   0x0  0x0   0   1.406     1.406
    31   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    56   -  10.96     -     -     -  0x0   -       -         -
    32   CPU0   -   -  1300  1600       1 100.00 6.01 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 141.26 0.648 0.720   0x0  0x0   0   1.578     1.578
    32   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    56   -  11.06     -     -     -  0x0   -       -         -
    33   CPU0   -   -  1300  1600       1 100.00 6.02 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 141.10 0.648 0.723   0x0  0x0   0   1.641     1.641
    33   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    56   -  11.01     -     -     -  0x0   -       -         -
    34   CPU0   -   -  1300  1600       1 100.00 6.01 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 141.12 0.648 0.723   0x0  0x0   0   1.578     1.578
    34   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    56   -  10.99     -     -     -  0x0   -       -         -
    35   CPU0   -   -  1300  1600       1 100.00 6.01 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 141.22 0.648 0.723   0x0  0x0   0   1.453     1.453
    35   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    56   -  11.03     -     -     -  0x0   -       -         -
    36   CPU0   -   -  1300  1600       1 100.00 5.99 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 141.23 0.648 0.723   0x0  0x0   0   1.375     1.375
    36   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    56   -  11.22     -     -     -  0x0   -       -         -
    37   CPU0   -   -  1300  1600       1 100.00 6.01 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 141.32 0.648 0.720   0x0  0x0   0   1.266     1.266
    37   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    56   -  11.01     -     -     -  0x0   -       -         -
    38   CPU0   -   -  1299  1600       1 100.00 5.99 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 141.02 0.648 0.723   0x0  0x0   0   1.266     1.266
    38   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    56   -  10.99     -     -     -  0x0   -       -         -
    39   CPU0   -   -  1301  1600       1 100.00 5.98 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 141.17 0.648 0.720   0x0  0x0   0   1.219     1.219
    39   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    56   -  10.91     -     -     -  0x0   -       -         -
    40   CPU0   -   -  1300  1600       1 100.00 6.00 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 140.99 0.651 0.720   0x0  0x0   0   1.188     1.188
    40   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    56   -  10.95     -     -     -  0x0   -       -         -
    41   CPU0   -   -  1300  1600       1 100.00 6.02 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 141.41 0.648 0.720   0x0  0x0   0   1.047     1.047
    41   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    56   -  10.99     -     -     -  0x0   -       -         -
^C
[03/29/24 23:12:22 UTC] PTAT stopped.

root@controller-0:/home/XXXXXX/compile/Ptu#
```

## check the sensors again, to see the reaction to raised thermals

```log
root@controller-0:/home/XXXXXX/compile/Ptu#  ipmitool sensor| grep -e CPU -e DutyCycle
02-CPU 1 PkgTmp  | 83.000     | degrees C  | ok    | na        | na        | na        | na        | 91.000    | na
Fan 1 DutyCycle  | 41.944     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 2 DutyCycle  | 41.944     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 3 DutyCycle  | 41.944     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 4 DutyCycle  | 41.944     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 5 DutyCycle  | 41.944     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 6 DutyCycle  | 41.944     | percent    | ok    | na        | na        | na        | na        | na        | na
CPU Utilization  | 206.000    | unspecified | ok    | na        | na        | na        | na        | na        | na
CPU_Stat_C1      | 0x0        | discrete   | 0x8080| na        | na        | na        | na        | na        | na
root@controller-0:/home/XXXXXX/compile/Ptu#
```

## Success as we have observed thermals rising, along with fans increase in RPMs...  on to next test

## MEAKV-643
## Performance Test #2 
## Run Core IA/SSE with 100% power, and Turbo on
## ./ptat -ct 3 -cp 100 -b 1

## Sensors before run

```log
root@controller-0:/home/XXXXXX/compile/Ptu#  ipmitool sensor| grep -e CPU -e DutyCycle
02-CPU 1 PkgTmp  | 70.000     | degrees C  | ok    | na        | na        | na        | na        | 91.000    | na
Fan 1 DutyCycle  | 11.760     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 2 DutyCycle  | 11.760     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 3 DutyCycle  | 11.760     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 4 DutyCycle  | 11.760     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 5 DutyCycle  | 11.760     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 6 DutyCycle  | 11.760     | percent    | ok    | na        | na        | na        | na        | na        | na
CPU Utilization  | 10.000     | unspecified | ok    | na        | na        | na        | na        | na        | na
CPU_Stat_C1      | 0x0        | discrete   | 0x8080| na        | na        | na        | na        | na        | na
root@controller-0:/home/XXXXXX/compile/Ptu#
```

## Initiate Load 

```log
root@controller-0:/home/XXXXXX/compile/Ptu# ./ptat  -ct 3 -cp 100 -b 1

Command: ./ptat -ct 3 -cp 100 -b 1

Intel(R) PTAT - Server Edition 4.4.0
Release Date: 12/19/2023
Copyright (C) 2023 Intel Corporation. All rights reserved.
Intel Confidential

>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> System Info:                   <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Host Name:                           controller-0
Host IP:                             169.254.202.1
OS Name:                             Debian GNU/Linux 11 (bullseye) 11
Kernel Version:                      Linux 5.10.0-6-rt-amd64 #1 SMP PREEMPT_RT StarlingX Debian 5.10.177-1.stx.73 (2023-11-25
BIOS Version:                        HPE, 1.11, 03/07/2024
Processor(s):                        1 Processor(s) Installed.
DIMM(s):                             8 DIMM(s) Installed.
Total System Memory:                 255208 MB
Available System Memory:             145108 MB


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Processor: [CPU_0]             <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU ID:                              0x000806F8 (Family 6 Model 8Fh Stepping 8)
CPU Brand Name:                      Intel(R) Xeon(R) Gold 6443N
CPU Code Name:                       Sapphire Rapids
CPU Type:                            Production Part
CPU Segment:                         Server
CPU PPIN:                            0x0000000000000000
CPU Base Frequency:                  1300 MHz
CPU Minimum Frequency:               800 MHz
CPU Maximum Turbo Frequency:         3600 MHz
Uncore Minimum Frequency:            1600 MHz
Uncore Maximum Frequency:            1600 MHz
L2 Cache:                            32 x 2048 KB
L3 Cache:                            61440 KB
Hyper-threading:                     Enabled
Microcode Update Revision:           0x2B000571
Number of Physcial Core(s):          32
Number of Logical Core(s):           64
Turbo Boost:                         Enabled
Turbo Boost Frequency:
 IA/SSE:
    1 - 16 Cores (Fused/Resolved):   3600 / 3600 (MHz)
   17 - 20 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   21 - 24 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   25 - 26 Cores (Fused/Resolved):   2900 / 2900 (MHz)
   27 - 32 Cores (Fused/Resolved):   2700 / 2700 (MHz)
 AVX2:
    1 - 16 Cores (Fused/Resolved):   3600 / 3600 (MHz)
   17 - 20 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   21 - 24 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   25 - 26 Cores (Fused/Resolved):   2800 / 2800 (MHz)
   27 - 32 Cores (Fused/Resolved):   2600 / 2600 (MHz)
 AVX-512:
    1 - 16 Cores (Fused/Resolved):   3600 / 3600 (MHz)
   17 - 20 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   21 - 24 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   25 - 26 Cores (Fused/Resolved):   2700 / 2700 (MHz)
   27 - 32 Cores (Fused/Resolved):   2500 / 2500 (MHz)
OVOLT_OVRD Supported:                0
OVOLT_OVRD Disabled:                 1
Platform ID:                         0x0
Platform Info:                       0x8405082EF4810D00
Thermal Design Power (TDP):          195 W
Power Limit 1 - Long Duration:       Enabled, Clamp ON , Power = 195 W, Time = 10.00 sec
Power Limit 2 - Short Duration:      Enabled, Clamp ON , Power = 234 W
Config TDP Level Supported:          3
Config TDP Level 1:                  195.0 W (110.0 W - 526.0 W), 0 MHz
Config TDP Level 2:                  195.0 W (110.0 W - 526.0 W), 0 MHz
Current Config TDP Level:            Nominal [Unlocked]
Tprochot:                            91 C
TCC Offset:                          0
CAPID0:                              0x42188138
CAPID1:                              0x5AC400C2
CAPID2:                              0xFF900003
CAPID3:                              0x07804000
CAPID4:                              0x04042EA0
CAPID5:                              0x6F0001EB
CAPID6:                              0xFDFEFFFF
CAPID7:                              0x00000003
CAPID8:                              0xFDFEFFFF
CAPID9:                              0x00000003
CAPID10:                             0x00000000


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Memory: [MEM_0]                <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Number of DIMM(s):                   8
Number of Active Channel(s):         8
DRAM Power Meter Disabled:           0
DRAM RAPL Disabled:                  0
DRAM TDP Power:                      Min = 15.0 W, Max = 66.0 W, Time = 0.31 sec
DRAM / NVDIMM Info:
  MC 0, Chnl 0, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 0, Chnl 1, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 1, Chnl 2, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 1, Chnl 3, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 2, Chnl 4, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 2, Chnl 5, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 3, Chnl 6, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 3, Chnl 7, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Platform Controller Hub: [PCH] <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
PCH Device ID:                       8086:1B81 (EBG)
PCH Stepping:                        17
PCH Thermal Sensor Enable:           0
PCH Hot Level (PHL):                 115


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> PTAT Current Settings:         <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU Test Selected:                   3
MEM Test Selected:                   1
CPU Mask:                            0xFFFFFFFF
CPU Core Mask:                       0xFFFFFFFFFFFFFFFF
CPU Thread Mask:                     0xFFFFFFFFFFFFFFFF
MEM Mask:                            0xFFFF
MEM Core Mask:                       0x1
MEM Thread Mask:                     0x1
Core Power Level:                    100
Memory Power Level:                  100
Turbo Enabled:                       Yes
AVX Test Level:                      1
Pmax Pre-sync:                       5000 ms
Pmax Post-sync:                      3000 ms
Pmax Idle:                           2000 ms
Run Time:                            0 (Forever)
PTAT Mon CPU Mask:                   0xFFFFFFFFFFFFFFFF
PTAT Mon Core Mask:                  0xFFFFFFFFFFFFFFFF
PTAT Mon MEM Mask:                   0xFFFFFFFF
PTAT Mon Filter Mask:                0x1F
PTAT Mon Update Interval:            1000000 usec
PTAT Mon Long Level:                 0
PTAT Mon Timestamp:                  No
Log Enabled:                         No
Log Directory:                       /root/ptat/log
Log File Prefix:                     <timestamp>
Log Message File:                    <timestamp>_ptatmsg.txt
Log Monitor File:                    <timestamp>_ptatmon.txt
CSV Enabled:                         No
PTAT License Auto Accept:            No
PTAT Driver Loaded:                  Yes

[03/29/24 23:16:01 UTC] PTAT started.

Press <Ctrl-C> to stop.


CPU_0: [IDLE] CFreq=2511, UFreq=1600, PState=0, Util=1.04, IPC=0.66, Temp=70, DTS=21, Power=72.4, Volt=0.765, UVolt=0.728
MEM_0: [IDLE] Power=10.88, Temp=40, Read=0.0, Write=0.0
MEM_0: [TESTCFG] TestSel=1 (Read), CoreMask=0x1, ThreadMask=0x1, PwrLevel=100, Turbo=1
MEM_0: [RUNNING] Power=153.46, Temp=40, Read=1134.5, Write=364.9
CPU_0: , CoreMask=0xFFFFFFFFFFFFFFFF, ThreadMask=0xFFFFFFFFFFFFFFFF, PwrLevel=100, Turbo=1
CPU_0: [RUNNING] CFreq=2087, UFreq=1600, PState=0, Util=100.00, IPC=5.99, Temp=82, DTS=9, Power=194.8, Volt=0.714, UVolt=0.723

```

## ptu -mon

```log
root@controller-0:/home/XXXXXX/compile/Ptu# ./ptat -mon

Command: ./ptat -mon

Intel(R) PTAT - Server Edition 4.4.0
Release Date: 12/19/2023
Copyright (C) 2023 Intel Corporation. All rights reserved.
Intel Confidential

>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> System Info:                   <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Host Name:                           controller-0
Host IP:                             169.254.202.1
OS Name:                             Debian GNU/Linux 11 (bullseye) 11
Kernel Version:                      Linux 5.10.0-6-rt-amd64 #1 SMP PREEMPT_RT StarlingX Debian 5.10.177-1.stx.73 (2023-11-25
BIOS Version:                        HPE, 1.11, 03/07/2024
Processor(s):                        1 Processor(s) Installed.
DIMM(s):                             8 DIMM(s) Installed.
Total System Memory:                 255208 MB
Available System Memory:             144933 MB


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Processor: [CPU_0]             <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU ID:                              0x000806F8 (Family 6 Model 8Fh Stepping 8)
CPU Brand Name:                      Intel(R) Xeon(R) Gold 6443N
CPU Code Name:                       Sapphire Rapids
CPU Type:                            Production Part
CPU Segment:                         Server
CPU PPIN:                            0x0000000000000000
CPU Base Frequency:                  1300 MHz
CPU Minimum Frequency:               800 MHz
CPU Maximum Turbo Frequency:         3600 MHz
Uncore Minimum Frequency:            1600 MHz
Uncore Maximum Frequency:            1600 MHz
L2 Cache:                            32 x 2048 KB
L3 Cache:                            61440 KB
Hyper-threading:                     Enabled
Microcode Update Revision:           0x2B000571
Number of Physcial Core(s):          32
Number of Logical Core(s):           64
Turbo Boost:                         Enabled
Turbo Boost Frequency:
 IA/SSE:
    1 - 16 Cores (Fused/Resolved):   3600 / 3600 (MHz)
   17 - 20 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   21 - 24 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   25 - 26 Cores (Fused/Resolved):   2900 / 2900 (MHz)
   27 - 32 Cores (Fused/Resolved):   2700 / 2700 (MHz)
 AVX2:
    1 - 16 Cores (Fused/Resolved):   3600 / 3600 (MHz)
   17 - 20 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   21 - 24 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   25 - 26 Cores (Fused/Resolved):   2800 / 2800 (MHz)
   27 - 32 Cores (Fused/Resolved):   2600 / 2600 (MHz)
 AVX-512:
    1 - 16 Cores (Fused/Resolved):   3600 / 3600 (MHz)
   17 - 20 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   21 - 24 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   25 - 26 Cores (Fused/Resolved):   2700 / 2700 (MHz)
   27 - 32 Cores (Fused/Resolved):   2500 / 2500 (MHz)
OVOLT_OVRD Supported:                0
OVOLT_OVRD Disabled:                 1
Platform ID:                         0x0
Platform Info:                       0x8405082EF4810D00
Thermal Design Power (TDP):          195 W
Power Limit 1 - Long Duration:       Enabled, Clamp ON , Power = 195 W, Time = 10.00 sec
Power Limit 2 - Short Duration:      Enabled, Clamp ON , Power = 234 W
Config TDP Level Supported:          3
Config TDP Level 1:                  195.0 W (110.0 W - 526.0 W), 0 MHz
Config TDP Level 2:                  195.0 W (110.0 W - 526.0 W), 0 MHz
Current Config TDP Level:            Nominal [Unlocked]
Tprochot:                            91 C
TCC Offset:                          0
CAPID0:                              0x42188138
CAPID1:                              0x5AC400C2
CAPID2:                              0xFF900003
CAPID3:                              0x07804000
CAPID4:                              0x04042EA0
CAPID5:                              0x6F0001EB
CAPID6:                              0xFDFEFFFF
CAPID7:                              0x00000003
CAPID8:                              0xFDFEFFFF
CAPID9:                              0x00000003
CAPID10:                             0x00000000


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Memory: [MEM_0]                <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Number of DIMM(s):                   8
Number of Active Channel(s):         8
DRAM Power Meter Disabled:           0
DRAM RAPL Disabled:                  0
DRAM TDP Power:                      Min = 15.0 W, Max = 66.0 W, Time = 0.31 sec
DRAM / NVDIMM Info:
  MC 0, Chnl 0, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 0, Chnl 1, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 1, Chnl 2, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 1, Chnl 3, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 2, Chnl 4, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 2, Chnl 5, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 3, Chnl 6, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 3, Chnl 7, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Platform Controller Hub: [PCH] <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
PCH Device ID:                       8086:1B81 (EBG)
PCH Stepping:                        17
PCH Thermal Sensor Enable:           0
PCH Hot Level (PHL):                 115


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> PTAT Current Settings:         <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU Test Selected:                   0
MEM Test Selected:                   0
CPU Mask:                            0xFFFFFFFF
CPU Core Mask:                       0xFFFFFFFFFFFFFFFF
CPU Thread Mask:                     0xFFFFFFFFFFFFFFFF
MEM Mask:                            0xFFFF
MEM Core Mask:                       0xFFFFFFFFFFFFFFFF
MEM Thread Mask:                     0xFFFFFFFFFFFFFFFF
Core Power Level:                    100
Memory Power Level:                  100
Turbo Enabled:                       No
AVX Test Level:                      1
Pmax Pre-sync:                       5000 ms
Pmax Post-sync:                      3000 ms
Pmax Idle:                           2000 ms
Run Time:                            0 (Forever)
PTAT Mon CPU Mask:                   0xFFFFFFFFFFFFFFFF
PTAT Mon Core Mask:                  0xFFFFFFFFFFFFFFFF
PTAT Mon MEM Mask:                   0xFFFFFFFF
PTAT Mon Filter Mask:                0x1F
PTAT Mon Update Interval:            1000000 usec
PTAT Mon Long Level:                 0
PTAT Mon Timestamp:                  No
Log Enabled:                         No
Log Directory:                       /root/ptat/log
Log File Prefix:                     <timestamp>
Log Message File:                    <timestamp>_ptatmsg.txt
Log Monitor File:                    <timestamp>_ptatmon.txt
CSV Enabled:                         No
PTAT License Auto Accept:            No
PTAT Driver Loaded:                  Yes

[03/29/24 23:17:11 UTC] PTAT started.

Press <Ctrl-C> to stop.


 Index Device Cor Thr CFreq UFreq  PState   Util  IPC     C0     C1     C6    PC2    PC6 MC Ch Sl  Temp DTS  Power  Volt UVolt TStat TLog #TL TMargin MCPMargin
     0   CPU0   -   -  2103  1600       0 100.00 6.00 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 194.87 0.711 0.725   0x0  0x0   0   1.219     1.219
     0   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  11.40     -     -     -  0x0   -       -         -
     1   CPU0   -   -  2085  1600       0 100.00 6.00 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 194.94 0.711 0.725   0x0  0x0   0   1.469     1.469
     1   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  11.25     -     -     -  0x0   -       -         -
     2   CPU0   -   -  2086  1600       0 100.00 6.00 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 194.61 0.711 0.725   0x0  0x0   0   1.328     1.328
     2   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  11.17     -     -     -  0x0   -       -         -
     3   CPU0   -   -  2086  1600       0 100.00 5.99 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 195.10 0.711 0.725   0x0  0x0   0   1.312     1.312
     3   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  11.28     -     -     -  0x0   -       -         -
     4   CPU0   -   -  2085  1600       0 100.00 5.99 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 194.86 0.711 0.725   0x0  0x0   0   1.422     1.422
     4   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  11.30     -     -     -  0x0   -       -         -
     5   CPU0   -   -  2084  1600       0 100.00 5.98 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 194.92 0.711 0.725   0x0  0x0   0   1.484     1.484
     5   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  10.98     -     -     -  0x0   -       -         -
     6   CPU0   -   -  2087  1600       0 100.00 5.99 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 194.79 0.711 0.725   0x0  0x0   0   1.375     1.375
     6   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  11.12     -     -     -  0x0   -       -         -
     7   CPU0   -   -  2085  1600       0 100.00 5.97 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 194.91 0.711 0.725   0x0  0x0   0   1.500     1.500
     7   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  11.35     -     -     -  0x0   -       -         -
     8   CPU0   -   -  2082  1600       0 100.00 5.97 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 194.92 0.711 0.725   0x0  0x0   0   1.594     1.594
     8   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  11.31     -     -     -  0x0   -       -         -
     9   CPU0   -   -  2084  1600       0 100.00 5.99 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 190.54 0.711 0.725   0x0  0x0   0   1.359     1.359
     9   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  11.22     -     -     -  0x0   -       -         -
    10   CPU0   -   -  2087  1600       0 100.00 5.99 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 198.55 0.701 0.725   0x0  0x0   0   1.375     1.375
    10   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  11.26     -     -     -  0x0   -       -         -
    11   CPU0   -   -  2087  1600       0 100.00 5.99 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 194.54 0.701 0.725   0x0  0x0   0   1.203     1.203
    11   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  10.98     -     -     -  0x0   -       -         -
    12   CPU0   -   -  2086  1600       0 100.00 6.02 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 195.16 0.711 0.725   0x0  0x0   0   1.328     1.328
    12   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  10.91     -     -     -  0x0   -       -         -
    13   CPU0   -   -  2084  1600       0 100.00 6.02 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 194.89 0.711 0.725   0x0  0x0   0   1.203     1.203
    13   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  10.89     -     -     -  0x0   -       -         -
    14   CPU0   -   -  2085  1600       0 100.00 6.01 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 194.83 0.711 0.725   0x0  0x0   0   1.297     1.297
    14   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  10.87     -     -     -  0x0   -       -         -
    15   CPU0   -   -  2085  1600       0 100.00 6.02 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 195.00 0.711 0.725   0x0  0x0   0   1.266     1.266
    15   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  11.08     -     -     -  0x0   -       -         -
    16   CPU0   -   -  2084  1600       0 100.00 6.01 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 194.78 0.701 0.725   0x0  0x0   0   1.172     1.172
    16   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  11.14     -     -     -  0x0   -       -         -
    17   CPU0   -   -  2086  1600       0 100.00 6.02 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 194.86 0.698 0.725   0x0  0x0   0   1.125     1.125
    17   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  10.90     -     -     -  0x0   -       -         -
    18   CPU0   -   -  2083  1600       0 100.00 5.99 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 194.92 0.711 0.725   0x0  0x0   0   1.156     1.156
    18   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  11.30     -     -     -  0x0   -       -         -
    19   CPU0   -   -  2084  1600       0 100.00 6.01 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 194.84 0.711 0.725   0x0  0x0   0   0.906     0.906
    19   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  11.06     -     -     -  0x0   -       -         -
    20   CPU0   -   -  2083  1600       0 100.00 6.03 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 194.96 0.711 0.725   0x0  0x0   0   0.812     0.812
    20   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  10.99     -     -     -  0x0   -       -         -
    21   CPU0   -   -  2084  1600       0 100.00 5.99 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 194.91 0.711 0.725   0x0  0x0   0   0.828     0.828
    21   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  11.25     -     -     -  0x0   -       -         -
    22   CPU0   -   -  2085  1600       0 100.00 5.99 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 194.90 0.711 0.725   0x0  0x0   0   0.891     0.891
    22   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  11.16     -     -     -  0x0   -       -         -
    23   CPU0   -   -  2084  1600       0 100.00 6.01 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 194.86 0.711 0.725   0x0  0x0   0   0.922     0.922
    23   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  10.89     -     -     -  0x0   -       -         -
    24   CPU0   -   -  2086  1600       0 100.00 6.02 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 194.77 0.711 0.725   0x0  0x0   0   0.797     0.797
    24   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  10.90     -     -     -  0x0   -       -         -
    25   CPU0   -   -  2085  1600       0 100.00 6.01 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 194.83 0.701 0.725   0x0  0x0   0   0.859     0.859
    25   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  11.01     -     -     -  0x0   -       -         -
    26   CPU0   -   -  2084  1600       0 100.00 6.01 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 195.04 0.701 0.725   0x0  0x0   0   0.781     0.781
    26   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  11.23     -     -     -  0x0   -       -         -
    27   CPU0   -   -  2086  1600       0 100.00 6.01 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 194.77 0.711 0.725   0x0  0x0   0   0.719     0.719
    27   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  11.25     -     -     -  0x0   -       -         -
    28   CPU0   -   -  2084  1600       0 100.00 6.01 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 194.77 0.711 0.725   0x0  0x0   0   0.734     0.734
    28   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  11.12     -     -     -  0x0   -       -         -
    29   CPU0   -   -  2086  1600       0 100.00 6.00 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 195.07 0.711 0.725   0x0  0x0   0   0.688     0.688
    29   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    51   -  11.03     -     -     -  0x0   -       -         -
    30   CPU0   -   -  2086  1600       0 100.00 5.97 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 194.93 0.711 0.725   0x0  0x0   0   0.734     0.734
    30   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    51   -  11.21     -     -     -  0x0   -       -         -
    31   CPU0   -   -  2086  1600       0 100.00 5.99 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 194.85 0.711 0.725   0x0  0x0   0   0.672     0.672
    31   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    51   -  11.08     -     -     -  0x0   -       -         -
    32   CPU0   -   -  2090  1600       0 100.00 6.01 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 194.77 0.711 0.725   0x0  0x0   0   0.750     0.750
    32   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    51   -  10.83     -     -     -  0x0   -       -         -
    33   CPU0   -   -  2084  1600       0 100.00 5.99 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 195.03 0.711 0.725   0x0  0x0   0   0.828     0.828
    33   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    51   -  11.02     -     -     -  0x0   -       -         -
    34   CPU0   -   -  2087  1600       0 100.00 6.00 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 194.80 0.711 0.725   0x0  0x0   0   1.094     1.094
    34   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    51   -  11.04     -     -     -  0x0   -       -         -
    35   CPU0   -   -  2082  1600       0 100.00 5.99 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 194.95 0.701 0.725   0x0  0x0   0   1.219     1.219
    35   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    51   -  11.22     -     -     -  0x0   -       -         -
    36   CPU0   -   -  2086  1600       0 100.00 6.02 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 194.72 0.711 0.725   0x0  0x0   0   1.047     1.047
    36   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    51   -  11.13     -     -     -  0x0   -       -         -
    37   CPU0   -   -  2084  1600       0 100.00 6.02 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 195.02 0.711 0.725   0x0  0x0   0   1.141     1.141
    37   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    51   -  11.04     -     -     -  0x0   -       -         -
    38   CPU0   -   -  2084  1600       0 100.00 6.01 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 194.85 0.688 0.725   0x0  0x0   0   1.141     1.141
    38   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    51   -  11.26     -     -     -  0x0   -       -         -
    39   CPU0   -   -  2085  1600       0 100.00 6.02 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 194.77 0.701 0.725   0x0  0x0   0   1.203     1.203
    39   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    51   -  11.08     -     -     -  0x0   -       -         -
    40   CPU0   -   -  2082  1600       0 100.00 6.01 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 195.08 0.701 0.725   0x0  0x0   0   1.031     1.031
    40   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    51   -  11.15     -     -     -  0x0   -       -         -
    41   CPU0   -   -  2085  1600       0 100.00 5.99 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 194.78 0.701 0.725   0x0  0x0   0   1.219     1.219
    41   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    51   -  11.22     -     -     -  0x0   -       -         -
^C
[03/29/24 23:17:58 UTC] PTAT stopped.

root@controller-0:/home/XXXXXX/compile/Ptu#
```


## Sensors after load ~2-3mins after

```log
root@controller-0:/home/XXXXXX/compile/Ptu#  ipmitool sensor| grep -e CPU -e DutyCycle -e Watts
02-CPU 1 PkgTmp  | 82.000     | degrees C  | ok    | na        | na        | na        | na        | 91.000    | na
Fan 1 DutyCycle  | 36.848     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 2 DutyCycle  | 36.848     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 3 DutyCycle  | 36.848     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 4 DutyCycle  | 36.848     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 5 DutyCycle  | 36.848     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 6 DutyCycle  | 36.848     | percent    | ok    | na        | na        | na        | na        | na        | na
PS 1 Input       | 200.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PS 2 Input       | 2550.000   | Watts      | ok    | na        | na        | na        | na        | na        | na
Power Meter      | 130.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
CPU Utilization  | 205.000    | unspecified | ok    | na        | na        | na        | na        | na        | na
PS 1 Output      | 0.000      | Watts      | ok    | na        | na        | na        | na        | na        | na
PS 2 Output      | 0.000      | Watts      | ok    | na        | na        | na        | na        | na        | na
CPU_Stat_C1      | 0x0        | discrete   | 0x8080| na        | na        | na        | na        | na        | na
root@controller-0:/home/XXXXXX/compile/Ptu#
```

## Test is success, observed temps rise and fan rpms rise with the load

## MEAKV-644
## Performance test PTU 3 - Core AVX2 with Turbo - MEAKV-644
## Run Core Intel® AVX-2 with power level 100% and Turbo on.
## sudo ./ptat -ct 4 -cp 100 -b 1

## Check sensors bofore starting load

```log
root@controller-0:/home/XXXXXX/compile/Ptu#  ipmitool sensor| grep -e CPU -e DutyCycle -e Watts
02-CPU 1 PkgTmp  | 69.000     | degrees C  | ok    | na        | na        | na        | na        | 91.000    | na
Fan 1 DutyCycle  | 10.976     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 2 DutyCycle  | 10.976     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 3 DutyCycle  | 10.976     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 4 DutyCycle  | 10.976     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 5 DutyCycle  | 10.976     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 6 DutyCycle  | 10.976     | percent    | ok    | na        | na        | na        | na        | na        | na
PS 1 Input       | 140.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PS 2 Input       | 2550.000   | Watts      | ok    | na        | na        | na        | na        | na        | na
Power Meter      | 60.000     | Watts      | ok    | na        | na        | na        | na        | na        | na
CPU Utilization  | 8.000      | unspecified | ok    | na        | na        | na        | na        | na        | na
PS 1 Output      | 0.000      | Watts      | ok    | na        | na        | na        | na        | na        | na
PS 2 Output      | 0.000      | Watts      | ok    | na        | na        | na        | na        | na        | na
CPU_Stat_C1      | 0x0        | discrete   | 0x8080| na        | na        | na        | na        | na        | na
root@controller-0:/home/XXXXXX/compile/Ptu#
```

## load Intiated

```log
root@controller-0:/home/XXXXXX/compile/Ptu# ./ptat  -ct 4 -cp 100 -b 1

Command: ./ptat -ct 4 -cp 100 -b 1

Intel(R) PTAT - Server Edition 4.4.0
Release Date: 12/19/2023
Copyright (C) 2023 Intel Corporation. All rights reserved.
Intel Confidential

>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> System Info:                   <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Host Name:                           controller-0
Host IP:                             169.254.202.1
OS Name:                             Debian GNU/Linux 11 (bullseye) 11
Kernel Version:                      Linux 5.10.0-6-rt-amd64 #1 SMP PREEMPT_RT StarlingX Debian 5.10.177-1.stx.73 (2023-11-25
BIOS Version:                        HPE, 1.11, 03/07/2024
Processor(s):                        1 Processor(s) Installed.
DIMM(s):                             8 DIMM(s) Installed.
Total System Memory:                 255208 MB
Available System Memory:             145090 MB


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Processor: [CPU_0]             <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU ID:                              0x000806F8 (Family 6 Model 8Fh Stepping 8)
CPU Brand Name:                      Intel(R) Xeon(R) Gold 6443N
CPU Code Name:                       Sapphire Rapids
CPU Type:                            Production Part
CPU Segment:                         Server
CPU PPIN:                            0x0000000000000000
CPU Base Frequency:                  1300 MHz
CPU Minimum Frequency:               800 MHz
CPU Maximum Turbo Frequency:         3600 MHz
Uncore Minimum Frequency:            1600 MHz
Uncore Maximum Frequency:            1600 MHz
L2 Cache:                            32 x 2048 KB
L3 Cache:                            61440 KB
Hyper-threading:                     Enabled
Microcode Update Revision:           0x2B000571
Number of Physcial Core(s):          32
Number of Logical Core(s):           64
Turbo Boost:                         Enabled
Turbo Boost Frequency:
 IA/SSE:
    1 - 16 Cores (Fused/Resolved):   3600 / 3600 (MHz)
   17 - 20 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   21 - 24 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   25 - 26 Cores (Fused/Resolved):   2900 / 2900 (MHz)
   27 - 32 Cores (Fused/Resolved):   2700 / 2700 (MHz)
 AVX2:
    1 - 16 Cores (Fused/Resolved):   3600 / 3600 (MHz)
   17 - 20 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   21 - 24 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   25 - 26 Cores (Fused/Resolved):   2800 / 2800 (MHz)
   27 - 32 Cores (Fused/Resolved):   2600 / 2600 (MHz)
 AVX-512:
    1 - 16 Cores (Fused/Resolved):   3600 / 3600 (MHz)
   17 - 20 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   21 - 24 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   25 - 26 Cores (Fused/Resolved):   2700 / 2700 (MHz)
   27 - 32 Cores (Fused/Resolved):   2500 / 2500 (MHz)
OVOLT_OVRD Supported:                0
OVOLT_OVRD Disabled:                 1
Platform ID:                         0x0
Platform Info:                       0x8405082EF4810D00
Thermal Design Power (TDP):          195 W
Power Limit 1 - Long Duration:       Enabled, Clamp ON , Power = 195 W, Time = 10.00 sec
Power Limit 2 - Short Duration:      Enabled, Clamp ON , Power = 234 W
Config TDP Level Supported:          3
Config TDP Level 1:                  195.0 W (110.0 W - 526.0 W), 0 MHz
Config TDP Level 2:                  195.0 W (110.0 W - 526.0 W), 0 MHz
Current Config TDP Level:            Nominal [Unlocked]
Tprochot:                            91 C
TCC Offset:                          0
CAPID0:                              0x42188138
CAPID1:                              0x5AC400C2
CAPID2:                              0xFF900003
CAPID3:                              0x07804000
CAPID4:                              0x04042EA0
CAPID5:                              0x6F0001EB
CAPID6:                              0xFDFEFFFF
CAPID7:                              0x00000003
CAPID8:                              0xFDFEFFFF
CAPID9:                              0x00000003
CAPID10:                             0x00000000


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Memory: [MEM_0]                <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Number of DIMM(s):                   8
Number of Active Channel(s):         8
DRAM Power Meter Disabled:           0
DRAM RAPL Disabled:                  0
DRAM TDP Power:                      Min = 15.0 W, Max = 66.0 W, Time = 0.31 sec
DRAM / NVDIMM Info:
  MC 0, Chnl 0, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 0, Chnl 1, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 1, Chnl 2, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 1, Chnl 3, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 2, Chnl 4, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 2, Chnl 5, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 3, Chnl 6, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 3, Chnl 7, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Platform Controller Hub: [PCH] <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
PCH Device ID:                       8086:1B81 (EBG)
PCH Stepping:                        17
PCH Thermal Sensor Enable:           0
PCH Hot Level (PHL):                 115


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> PTAT Current Settings:         <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU Test Selected:                   4
MEM Test Selected:                   1
CPU Mask:                            0xFFFFFFFF
CPU Core Mask:                       0xFFFFFFFFFFFFFFFF
CPU Thread Mask:                     0xFFFFFFFFFFFFFFFF
MEM Mask:                            0xFFFF
MEM Core Mask:                       0x1
MEM Thread Mask:                     0x1
Core Power Level:                    100
Memory Power Level:                  100
Turbo Enabled:                       Yes
AVX Test Level:                      1
Pmax Pre-sync:                       5000 ms
Pmax Post-sync:                      3000 ms
Pmax Idle:                           2000 ms
Run Time:                            0 (Forever)
PTAT Mon CPU Mask:                   0xFFFFFFFFFFFFFFFF
PTAT Mon Core Mask:                  0xFFFFFFFFFFFFFFFF
PTAT Mon MEM Mask:                   0xFFFFFFFF
PTAT Mon Filter Mask:                0x1F
PTAT Mon Update Interval:            1000000 usec
PTAT Mon Long Level:                 0
PTAT Mon Timestamp:                  No
Log Enabled:                         No
Log Directory:                       /root/ptat/log
Log File Prefix:                     <timestamp>
Log Message File:                    <timestamp>_ptatmsg.txt
Log Monitor File:                    <timestamp>_ptatmon.txt
CSV Enabled:                         No
PTAT License Auto Accept:            No
PTAT Driver Loaded:                  Yes

[03/29/24 23:23:07 UTC] PTAT started.

Press <Ctrl-C> to stop.


CPU_0: [IDLE] CFreq=2484, UFreq=1600, PState=0, Util=3.33, IPC=0.63, Temp=72, DTS=19, Power=75.6, Volt=0.765, UVolt=0.730
MEM_0: [IDLE] Power=11.43, Temp=39, Read=0.0, Write=0.0
MEM_0: [TESTCFG] TestSel=1 (Read), CoreMask=0x1, ThreadMask=0x1, PwrLevel=100, Turbo=1
MEM_0: [RUNNING] Power=11.11, Temp=39, Read=1122.4, Write=401.9
CPU_0: , CoreMask=0xFFFFFFFFFFFFFFFF, ThreadMask=0xFFFFFFFFFFFFFFFF, PwrLevel=100, Turbo=1


```

## ptu -mon

```log
root@controller-0:/home/XXXXXX/compile/Ptu# ./ptat -mon

Command: ./ptat -mon

Intel(R) PTAT - Server Edition 4.4.0
Release Date: 12/19/2023
Copyright (C) 2023 Intel Corporation. All rights reserved.
Intel Confidential

>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> System Info:                   <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Host Name:                           controller-0
Host IP:                             169.254.202.1
OS Name:                             Debian GNU/Linux 11 (bullseye) 11
Kernel Version:                      Linux 5.10.0-6-rt-amd64 #1 SMP PREEMPT_RT StarlingX Debian 5.10.177-1.stx.73 (2023-11-25
BIOS Version:                        HPE, 1.11, 03/07/2024
Processor(s):                        1 Processor(s) Installed.
DIMM(s):                             8 DIMM(s) Installed.
Total System Memory:                 255208 MB
Available System Memory:             144950 MB


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Processor: [CPU_0]             <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU ID:                              0x000806F8 (Family 6 Model 8Fh Stepping 8)
CPU Brand Name:                      Intel(R) Xeon(R) Gold 6443N
CPU Code Name:                       Sapphire Rapids
CPU Type:                            Production Part
CPU Segment:                         Server
CPU PPIN:                            0x0000000000000000
CPU Base Frequency:                  1300 MHz
CPU Minimum Frequency:               800 MHz
CPU Maximum Turbo Frequency:         3600 MHz
Uncore Minimum Frequency:            1600 MHz
Uncore Maximum Frequency:            1600 MHz
L2 Cache:                            32 x 2048 KB
L3 Cache:                            61440 KB
Hyper-threading:                     Enabled
Microcode Update Revision:           0x2B000571
Number of Physcial Core(s):          32
Number of Logical Core(s):           64
Turbo Boost:                         Enabled
Turbo Boost Frequency:
 IA/SSE:
    1 - 16 Cores (Fused/Resolved):   3600 / 3600 (MHz)
   17 - 20 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   21 - 24 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   25 - 26 Cores (Fused/Resolved):   2900 / 2900 (MHz)
   27 - 32 Cores (Fused/Resolved):   2700 / 2700 (MHz)
 AVX2:
    1 - 16 Cores (Fused/Resolved):   3600 / 3600 (MHz)
   17 - 20 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   21 - 24 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   25 - 26 Cores (Fused/Resolved):   2800 / 2800 (MHz)
   27 - 32 Cores (Fused/Resolved):   2600 / 2600 (MHz)
 AVX-512:
    1 - 16 Cores (Fused/Resolved):   3600 / 3600 (MHz)
   17 - 20 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   21 - 24 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   25 - 26 Cores (Fused/Resolved):   2700 / 2700 (MHz)
   27 - 32 Cores (Fused/Resolved):   2500 / 2500 (MHz)
OVOLT_OVRD Supported:                0
OVOLT_OVRD Disabled:                 1
Platform ID:                         0x0
Platform Info:                       0x8405082EF4810D00
Thermal Design Power (TDP):          195 W
Power Limit 1 - Long Duration:       Enabled, Clamp ON , Power = 195 W, Time = 10.00 sec
Power Limit 2 - Short Duration:      Enabled, Clamp ON , Power = 234 W
Config TDP Level Supported:          3
Config TDP Level 1:                  195.0 W (110.0 W - 526.0 W), 0 MHz
Config TDP Level 2:                  195.0 W (110.0 W - 526.0 W), 0 MHz
Current Config TDP Level:            Nominal [Unlocked]
Tprochot:                            91 C
TCC Offset:                          0
CAPID0:                              0x42188138
CAPID1:                              0x5AC400C2
CAPID2:                              0xFF900003
CAPID3:                              0x07804000
CAPID4:                              0x04042EA0
CAPID5:                              0x6F0001EB
CAPID6:                              0xFDFEFFFF
CAPID7:                              0x00000003
CAPID8:                              0xFDFEFFFF
CAPID9:                              0x00000003
CAPID10:                             0x00000000


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Memory: [MEM_0]                <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Number of DIMM(s):                   8
Number of Active Channel(s):         8
DRAM Power Meter Disabled:           0
DRAM RAPL Disabled:                  0
DRAM TDP Power:                      Min = 15.0 W, Max = 66.0 W, Time = 0.31 sec
DRAM / NVDIMM Info:
  MC 0, Chnl 0, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 0, Chnl 1, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 1, Chnl 2, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 1, Chnl 3, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 2, Chnl 4, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 2, Chnl 5, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 3, Chnl 6, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 3, Chnl 7, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Platform Controller Hub: [PCH] <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
PCH Device ID:                       8086:1B81 (EBG)
PCH Stepping:                        17
PCH Thermal Sensor Enable:           0
PCH Hot Level (PHL):                 115


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> PTAT Current Settings:         <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU Test Selected:                   0
MEM Test Selected:                   0
CPU Mask:                            0xFFFFFFFF
CPU Core Mask:                       0xFFFFFFFFFFFFFFFF
CPU Thread Mask:                     0xFFFFFFFFFFFFFFFF
MEM Mask:                            0xFFFF
MEM Core Mask:                       0xFFFFFFFFFFFFFFFF
MEM Thread Mask:                     0xFFFFFFFFFFFFFFFF
Core Power Level:                    100
Memory Power Level:                  100
Turbo Enabled:                       No
AVX Test Level:                      1
Pmax Pre-sync:                       5000 ms
Pmax Post-sync:                      3000 ms
Pmax Idle:                           2000 ms
Run Time:                            0 (Forever)
PTAT Mon CPU Mask:                   0xFFFFFFFFFFFFFFFF
PTAT Mon Core Mask:                  0xFFFFFFFFFFFFFFFF
PTAT Mon MEM Mask:                   0xFFFFFFFF
PTAT Mon Filter Mask:                0x1F
PTAT Mon Update Interval:            1000000 usec
PTAT Mon Long Level:                 0
PTAT Mon Timestamp:                  No
Log Enabled:                         No
Log Directory:                       /root/ptat/log
Log File Prefix:                     <timestamp>
Log Message File:                    <timestamp>_ptatmsg.txt
Log Monitor File:                    <timestamp>_ptatmon.txt
CSV Enabled:                         No
PTAT License Auto Accept:            No
PTAT Driver Loaded:                  Yes

[03/29/24 23:24:00 UTC] PTAT started.

Press <Ctrl-C> to stop.


 Index Device Cor Thr CFreq UFreq  PState   Util  IPC     C0     C1     C6    PC2    PC6 MC Ch Sl  Temp DTS  Power  Volt UVolt TStat TLog #TL TMargin MCPMargin
     0   CPU0   -   -  2399  1600       0 100.00 6.85 100.00   0.00   0.00   0.00   0.00  -  -  -    80  11 194.88 0.743 0.728   0x0  0x0   0   2.672     2.672
     0   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    51   -  11.39     -     -     -  0x0   -       -         -
     1   CPU0   -   -  2366  1600       0 100.00 6.87 100.00   0.00   0.00   0.00   0.00  -  -  -    80  11 194.83 0.733 0.728   0x0  0x0   0   2.781     2.781
     1   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    51   -  11.17     -     -     -  0x0   -       -         -
     2   CPU0   -   -  2368  1600       0 100.00 6.85 100.00   0.00   0.00   0.00   0.00  -  -  -    80  11 194.90 0.733 0.725   0x0  0x0   0   2.750     2.750
     2   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    51   -  11.22     -     -     -  0x0   -       -         -
     3   CPU0   -   -  2370  1600       0 100.00 6.86 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 194.88 0.743 0.725   0x0  0x0   0   2.719     2.719
     3   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    51   -  11.22     -     -     -  0x0   -       -         -
     4   CPU0   -   -  2368  1600       0 100.00 6.85 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 194.77 0.743 0.725   0x0  0x0   0   2.578     2.578
     4   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    51   -  11.23     -     -     -  0x0   -       -         -
     5   CPU0   -   -  2371  1600       0 100.00 6.89 100.00   0.00   0.00   0.00   0.00  -  -  -    80  11 194.95 0.743 0.725   0x0  0x0   0   2.641     2.641
     5   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    51   -  11.09     -     -     -  0x0   -       -         -
     6   CPU0   -   -  2367  1600       0 100.00 6.87 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 194.90 0.733 0.728   0x0  0x0   0   2.672     2.672
     6   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    51   -  11.31     -     -     -  0x0   -       -         -
     7   CPU0   -   -  2363  1600       0 100.00 6.89 100.00   0.00   0.00   0.00   0.00  -  -  -    80  11 194.94 0.733 0.725   0x0  0x0   0   2.609     2.609
     7   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    51   -  11.21     -     -     -  0x0   -       -         -
     8   CPU0   -   -  2372  1600       0 100.00 6.90 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 194.80 0.743 0.725   0x0  0x0   0   2.703     2.703
     8   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    51   -  11.07     -     -     -  0x0   -       -         -
     9   CPU0   -   -  2368  1600       0 100.00 6.89 100.00   0.00   0.00   0.00   0.00  -  -  -    80  11 194.93 0.733 0.725   0x0  0x0   0   2.625     2.625
     9   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    51   -  11.17     -     -     -  0x0   -       -         -
    10   CPU0   -   -  2366  1600       0 100.00 6.86 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 194.84 0.743 0.725   0x0  0x0   0   2.594     2.594
    10   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    51   -  11.45     -     -     -  0x0   -       -         -
    11   CPU0   -   -  2374  1600       0 100.00 6.85 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 194.81 0.743 0.725   0x0  0x0   0   2.516     2.516
    11   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    51   -  11.57     -     -     -  0x0   -       -         -
    12   CPU0   -   -  2363  1600       0 100.00 6.87 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 195.05 0.743 0.725   0x0  0x0   0   2.453     2.453
    12   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    51   -  11.54     -     -     -  0x0   -       -         -
    13   CPU0   -   -  2366  1600       0 100.00 6.90 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 194.79 0.743 0.725   0x0  0x0   0   2.047     2.047
    13   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    51   -  11.22     -     -     -  0x0   -       -         -
    14   CPU0   -   -  2366  1600       0 100.00 6.88 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 194.82 0.743 0.725   0x0  0x0   0   2.062     2.062
    14   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    51   -  11.35     -     -     -  0x0   -       -         -
    15   CPU0   -   -  2366  1600       0 100.00 6.85 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 195.01 0.733 0.725   0x0  0x0   0   1.797     1.797
    15   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    51   -  11.40     -     -     -  0x0   -       -         -
    16   CPU0   -   -  2367  1600       0 100.00 6.88 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 194.76 0.743 0.725   0x0  0x0   0   1.516     1.516
    16   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    51   -  11.31     -     -     -  0x0   -       -         -
    17   CPU0   -   -  2367  1600       0 100.00 6.89 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 194.92 0.743 0.725   0x0  0x0   0   1.953     1.953
    17   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    51   -  11.28     -     -     -  0x0   -       -         -
    18   CPU0   -   -  2365  1600       0 100.00 6.88 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 194.88 0.743 0.725   0x0  0x0   0   2.141     2.141
    18   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    51   -  11.28     -     -     -  0x0   -       -         -
    19   CPU0   -   -  2372  1600       0 100.00 6.86 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 194.99 0.743 0.725   0x0  0x0   0   1.969     1.969
    19   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    51   -  11.20     -     -     -  0x0   -       -         -
    20   CPU0   -   -  2361  1600       0 100.00 6.84 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 194.90 0.746 0.725   0x0  0x0   0   2.047     2.047
    20   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    51   -  11.36     -     -     -  0x0   -       -         -
    21   CPU0   -   -  2364  1600       0 100.00 6.83 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 194.78 0.743 0.725   0x0  0x0   0   2.062     2.062
    21   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    51   -  11.28     -     -     -  0x0   -       -         -
    22   CPU0   -   -  2370  1600       0 100.00 6.85 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 194.87 0.743 0.725   0x0  0x0   0   1.812     1.812
    22   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    50   -  11.35     -     -     -  0x0   -       -         -
    23   CPU0   -   -  2367  1600       0 100.00 6.85 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 194.87 0.733 0.725   0x0  0x0   0   1.750     1.750
    23   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    50   -  11.05     -     -     -  0x0   -       -         -
    24   CPU0   -   -  2360  1600       0 100.00 6.86 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 194.97 0.733 0.725   0x0  0x0   0   1.812     1.812
    24   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    50   -  11.07     -     -     -  0x0   -       -         -
    25   CPU0   -   -  2354  1600       0 100.00 6.87 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 194.98 0.743 0.725   0x0  0x0   0   1.578     1.578
    25   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    50   -  11.29     -     -     -  0x0   -       -         -
    26   CPU0   -   -  2355  1600       0 100.00 6.85 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 194.88 0.743 0.725   0x0  0x0   0   1.500     1.500
    26   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    50   -  11.27     -     -     -  0x0   -       -         -
    27   CPU0   -   -  2351  1600       0 100.00 6.84 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 194.69 0.743 0.725   0x0  0x0   0   1.578     1.578
    27   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    50   -  11.61     -     -     -  0x0   -       -         -
    28   CPU0   -   -  2357  1600       0 100.00 6.83 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 195.07 0.743 0.725   0x0  0x0   0   1.859     1.859
    28   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    50   -  11.52     -     -     -  0x0   -       -         -
    29   CPU0   -   -  2355  1600       0 100.00 6.83 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 194.86 0.733 0.725   0x0  0x0   0   1.672     1.672
    29   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    50   -  11.78     -     -     -  0x0   -       -         -
    30   CPU0   -   -  2358  1600       0 100.00 6.84 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 194.83 0.743 0.725   0x0  0x0   0   1.875     1.875
    30   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    50   -  11.70     -     -     -  0x0   -       -         -
    31   CPU0   -   -  2355  1600       0 100.00 6.84 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 193.03 0.733 0.725   0x0  0x0   0   1.844     1.844
    31   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    50   -  11.43     -     -     -  0x0   -       -         -
    32   CPU0   -   -  2361  1600       0 100.00 6.85 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 196.25 0.743 0.725   0x0  0x0   0   1.781     1.781
    32   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    50   -  11.13     -     -     -  0x0   -       -         -
    33   CPU0   -   -  2361  1600       0 100.00 6.85 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 193.76 0.743 0.725   0x0  0x0   0   1.375     1.375
    33   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    50   -  11.14     -     -     -  0x0   -       -         -
    34   CPU0   -   -  2364  1600       0 100.00 6.84 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 195.99 0.743 0.725   0x0  0x0   0   1.406     1.406
    34   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    50   -  11.18     -     -     -  0x0   -       -         -
^C
[03/29/24 23:24:39 UTC] PTAT stopped.

root@controller-0:/home/XXXXXX/compile/Ptu#
```

## check sensors after load 

```log
root@controller-0:/home/XXXXXX/compile/Ptu#  ipmitool sensor| grep -e CPU -e DutyCycle -e Watts
02-CPU 1 PkgTmp  | 82.000     | degrees C  | ok    | na        | na        | na        | na        | 91.000    | na
Fan 1 DutyCycle  | 34.888     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 2 DutyCycle  | 34.888     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 3 DutyCycle  | 34.888     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 4 DutyCycle  | 34.888     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 5 DutyCycle  | 34.888     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 6 DutyCycle  | 34.888     | percent    | ok    | na        | na        | na        | na        | na        | na
PS 1 Input       | 200.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PS 2 Input       | 2550.000   | Watts      | ok    | na        | na        | na        | na        | na        | na
Power Meter      | 130.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
CPU Utilization  | 230.000    | unspecified | ok    | na        | na        | na        | na        | na        | na
PS 1 Output      | 0.000      | Watts      | ok    | na        | na        | na        | na        | na        | na
PS 2 Output      | 0.000      | Watts      | ok    | na        | na        | na        | na        | na        | na
CPU_Stat_C1      | 0x0        | discrete   | 0x8080| na        | na        | na        | na        | na        | na
root@controller-0:/home/XXXXXX/compile/Ptu#
```

## Observed temps raise and fans rpm raise with load - success

## MEAKV-645
## PTU 4 - Core AVX512 with Turbo
## sudo ./ptat -ct 5 -cp 100 -b 1


## Sensors before load

```log
root@controller-0:~#  ipmitool sensor| grep -e CPU -e DutyCycle -e Watts
02-CPU 1 PkgTmp  | 68.000     | degrees C  | ok    | na        | na        | na        | na        | 91.000    | na
Fan 1 DutyCycle  | 11.760     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 2 DutyCycle  | 11.760     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 3 DutyCycle  | 11.760     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 4 DutyCycle  | 11.760     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 5 DutyCycle  | 11.760     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 6 DutyCycle  | 11.760     | percent    | ok    | na        | na        | na        | na        | na        | na
PS 1 Input       | 140.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PS 2 Input       | 2550.000   | Watts      | ok    | na        | na        | na        | na        | na        | na
Power Meter      | 60.000     | Watts      | ok    | na        | na        | na        | na        | na        | na
CPU Utilization  | 9.000      | unspecified | ok    | na        | na        | na        | na        | na        | na
PS 1 Output      | 0.000      | Watts      | ok    | na        | na        | na        | na        | na        | na
PS 2 Output      | 0.000      | Watts      | ok    | na        | na        | na        | na        | na        | na
CPU_Stat_C1      | 0x0        | discrete   | 0x8080| na        | na        | na        | na        | na        | na
root@controller-0:~#

```

## Initate load

```log
root@controller-0:/home/XXXXXX/compile/Ptu# ./ptat -ct 5 -cp 100 -b 1

Command: ./ptat -ct 5 -cp 100 -b 1

Intel(R) PTAT - Server Edition 4.4.0
Release Date: 12/19/2023
Copyright (C) 2023 Intel Corporation. All rights reserved.
Intel Confidential

>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> System Info:                   <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Host Name:                           controller-0
Host IP:                             169.254.202.1
OS Name:                             Debian GNU/Linux 11 (bullseye) 11
Kernel Version:                      Linux 5.10.0-6-rt-amd64 #1 SMP PREEMPT_RT StarlingX Debian 5.10.177-1.stx.73 (2023-11-25
BIOS Version:                        HPE, 1.11, 03/07/2024
Processor(s):                        1 Processor(s) Installed.
DIMM(s):                             8 DIMM(s) Installed.
Total System Memory:                 255208 MB
Available System Memory:             145114 MB


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Processor: [CPU_0]             <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU ID:                              0x000806F8 (Family 6 Model 8Fh Stepping 8)
CPU Brand Name:                      Intel(R) Xeon(R) Gold 6443N
CPU Code Name:                       Sapphire Rapids
CPU Type:                            Production Part
CPU Segment:                         Server
CPU PPIN:                            0x0000000000000000
CPU Base Frequency:                  1300 MHz
CPU Minimum Frequency:               800 MHz
CPU Maximum Turbo Frequency:         3600 MHz
Uncore Minimum Frequency:            1600 MHz
Uncore Maximum Frequency:            1600 MHz
L2 Cache:                            32 x 2048 KB
L3 Cache:                            61440 KB
Hyper-threading:                     Enabled
Microcode Update Revision:           0x2B000571
Number of Physcial Core(s):          32
Number of Logical Core(s):           64
Turbo Boost:                         Enabled
Turbo Boost Frequency:
 IA/SSE:
    1 - 16 Cores (Fused/Resolved):   3600 / 3600 (MHz)
   17 - 20 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   21 - 24 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   25 - 26 Cores (Fused/Resolved):   2900 / 2900 (MHz)
   27 - 32 Cores (Fused/Resolved):   2700 / 2700 (MHz)
 AVX2:
    1 - 16 Cores (Fused/Resolved):   3600 / 3600 (MHz)
   17 - 20 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   21 - 24 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   25 - 26 Cores (Fused/Resolved):   2800 / 2800 (MHz)
   27 - 32 Cores (Fused/Resolved):   2600 / 2600 (MHz)
 AVX-512:
    1 - 16 Cores (Fused/Resolved):   3600 / 3600 (MHz)
   17 - 20 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   21 - 24 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   25 - 26 Cores (Fused/Resolved):   2700 / 2700 (MHz)
   27 - 32 Cores (Fused/Resolved):   2500 / 2500 (MHz)
OVOLT_OVRD Supported:                0
OVOLT_OVRD Disabled:                 1
Platform ID:                         0x0
Platform Info:                       0x8405082EF4810D00
Thermal Design Power (TDP):          195 W
Power Limit 1 - Long Duration:       Enabled, Clamp ON , Power = 195 W, Time = 10.00 sec
Power Limit 2 - Short Duration:      Enabled, Clamp ON , Power = 234 W
Config TDP Level Supported:          3
Config TDP Level 1:                  195.0 W (110.0 W - 526.0 W), 0 MHz
Config TDP Level 2:                  195.0 W (110.0 W - 526.0 W), 0 MHz
Current Config TDP Level:            Nominal [Unlocked]
Tprochot:                            91 C
TCC Offset:                          0
CAPID0:                              0x42188138
CAPID1:                              0x5AC400C2
CAPID2:                              0xFF900003
CAPID3:                              0x07804000
CAPID4:                              0x04042EA0
CAPID5:                              0x6F0001EB
CAPID6:                              0xFDFEFFFF
CAPID7:                              0x00000003
CAPID8:                              0xFDFEFFFF
CAPID9:                              0x00000003
CAPID10:                             0x00000000


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Memory: [MEM_0]                <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Number of DIMM(s):                   8
Number of Active Channel(s):         8
DRAM Power Meter Disabled:           0
DRAM RAPL Disabled:                  0
DRAM TDP Power:                      Min = 15.0 W, Max = 66.0 W, Time = 0.31 sec
DRAM / NVDIMM Info:
  MC 0, Chnl 0, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 0, Chnl 1, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 1, Chnl 2, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 1, Chnl 3, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 2, Chnl 4, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 2, Chnl 5, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 3, Chnl 6, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 3, Chnl 7, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Platform Controller Hub: [PCH] <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
PCH Device ID:                       8086:1B81 (EBG)
PCH Stepping:                        17
PCH Thermal Sensor Enable:           0
PCH Hot Level (PHL):                 115


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> PTAT Current Settings:         <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU Test Selected:                   5
MEM Test Selected:                   1
CPU Mask:                            0xFFFFFFFF
CPU Core Mask:                       0xFFFFFFFFFFFFFFFF
CPU Thread Mask:                     0xFFFFFFFFFFFFFFFF
MEM Mask:                            0xFFFF
MEM Core Mask:                       0x1
MEM Thread Mask:                     0x1
Core Power Level:                    100
Memory Power Level:                  100
Turbo Enabled:                       Yes
AVX Test Level:                      1
Pmax Pre-sync:                       5000 ms
Pmax Post-sync:                      3000 ms
Pmax Idle:                           2000 ms
Run Time:                            0 (Forever)
PTAT Mon CPU Mask:                   0xFFFFFFFFFFFFFFFF
PTAT Mon Core Mask:                  0xFFFFFFFFFFFFFFFF
PTAT Mon MEM Mask:                   0xFFFFFFFF
PTAT Mon Filter Mask:                0x1F
PTAT Mon Update Interval:            1000000 usec
PTAT Mon Long Level:                 0
PTAT Mon Timestamp:                  No
Log Enabled:                         No
Log Directory:                       /root/ptat/log
Log File Prefix:                     <timestamp>
Log Message File:                    <timestamp>_ptatmsg.txt
Log Monitor File:                    <timestamp>_ptatmon.txt
CSV Enabled:                         No
PTAT License Auto Accept:            No
PTAT Driver Loaded:                  Yes

[03/29/24 23:29:26 UTC] PTAT started.

Press <Ctrl-C> to stop.


CPU_0: [IDLE] CFreq=2531, UFreq=1600, PState=0, Util=1.31, IPC=0.70, Temp=69, DTS=22, Power=72.2, Volt=0.767, UVolt=0.730
MEM_0: [IDLE] Power=175.48, Temp=38, Read=0.0, Write=0.0
MEM_0: [TESTCFG] TestSel=1 (Read), CoreMask=0x1, ThreadMask=0x1, PwrLevel=100, Turbo=1
MEM_0: [RUNNING] Power=126.83, Temp=38, Read=942.2, Write=362.8
CPU_0: , CoreMask=0xFFFFFFFFFFFFFFFF, ThreadMask=0xFFFFFFFFFFFFFFFF, PwrLevel=100, Turbo=1
CPU_0: [RUNNING] CFreq=2192, UFreq=1600, PState=0, Util=100.00, IPC=6.84, Temp=80, DTS=11, Power=194.9, Volt=0.727, UVolt=0.725

```

## ptu -mon

```log
root@controller-0:/home/XXXXXX/compile/Ptu# ./ptat -mon

Command: ./ptat -mon

Intel(R) PTAT - Server Edition 4.4.0
Release Date: 12/19/2023
Copyright (C) 2023 Intel Corporation. All rights reserved.
Intel Confidential

>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> System Info:                   <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Host Name:                           controller-0
Host IP:                             169.254.202.1
OS Name:                             Debian GNU/Linux 11 (bullseye) 11
Kernel Version:                      Linux 5.10.0-6-rt-amd64 #1 SMP PREEMPT_RT StarlingX Debian 5.10.177-1.stx.73 (2023-11-25
BIOS Version:                        HPE, 1.11, 03/07/2024
Processor(s):                        1 Processor(s) Installed.
DIMM(s):                             8 DIMM(s) Installed.
Total System Memory:                 255208 MB
Available System Memory:             144935 MB


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Processor: [CPU_0]             <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU ID:                              0x000806F8 (Family 6 Model 8Fh Stepping 8)
CPU Brand Name:                      Intel(R) Xeon(R) Gold 6443N
CPU Code Name:                       Sapphire Rapids
CPU Type:                            Production Part
CPU Segment:                         Server
CPU PPIN:                            0x0000000000000000
CPU Base Frequency:                  1300 MHz
CPU Minimum Frequency:               800 MHz
CPU Maximum Turbo Frequency:         3600 MHz
Uncore Minimum Frequency:            1600 MHz
Uncore Maximum Frequency:            1600 MHz
L2 Cache:                            32 x 2048 KB
L3 Cache:                            61440 KB
Hyper-threading:                     Enabled
Microcode Update Revision:           0x2B000571
Number of Physcial Core(s):          32
Number of Logical Core(s):           64
Turbo Boost:                         Enabled
Turbo Boost Frequency:
 IA/SSE:
    1 - 16 Cores (Fused/Resolved):   3600 / 3600 (MHz)
   17 - 20 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   21 - 24 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   25 - 26 Cores (Fused/Resolved):   2900 / 2900 (MHz)
   27 - 32 Cores (Fused/Resolved):   2700 / 2700 (MHz)
 AVX2:
    1 - 16 Cores (Fused/Resolved):   3600 / 3600 (MHz)
   17 - 20 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   21 - 24 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   25 - 26 Cores (Fused/Resolved):   2800 / 2800 (MHz)
   27 - 32 Cores (Fused/Resolved):   2600 / 2600 (MHz)
 AVX-512:
    1 - 16 Cores (Fused/Resolved):   3600 / 3600 (MHz)
   17 - 20 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   21 - 24 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   25 - 26 Cores (Fused/Resolved):   2700 / 2700 (MHz)
   27 - 32 Cores (Fused/Resolved):   2500 / 2500 (MHz)
OVOLT_OVRD Supported:                0
OVOLT_OVRD Disabled:                 1
Platform ID:                         0x0
Platform Info:                       0x8405082EF4810D00
Thermal Design Power (TDP):          195 W
Power Limit 1 - Long Duration:       Enabled, Clamp ON , Power = 195 W, Time = 10.00 sec
Power Limit 2 - Short Duration:      Enabled, Clamp ON , Power = 234 W
Config TDP Level Supported:          3
Config TDP Level 1:                  195.0 W (110.0 W - 526.0 W), 0 MHz
Config TDP Level 2:                  195.0 W (110.0 W - 526.0 W), 0 MHz
Current Config TDP Level:            Nominal [Unlocked]
Tprochot:                            91 C
TCC Offset:                          0
CAPID0:                              0x42188138
CAPID1:                              0x5AC400C2
CAPID2:                              0xFF900003
CAPID3:                              0x07804000
CAPID4:                              0x04042EA0
CAPID5:                              0x6F0001EB
CAPID6:                              0xFDFEFFFF
CAPID7:                              0x00000003
CAPID8:                              0xFDFEFFFF
CAPID9:                              0x00000003
CAPID10:                             0x00000000


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Memory: [MEM_0]                <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Number of DIMM(s):                   8
Number of Active Channel(s):         8
DRAM Power Meter Disabled:           0
DRAM RAPL Disabled:                  0
DRAM TDP Power:                      Min = 15.0 W, Max = 66.0 W, Time = 0.31 sec
DRAM / NVDIMM Info:
  MC 0, Chnl 0, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 0, Chnl 1, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 1, Chnl 2, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 1, Chnl 3, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 2, Chnl 4, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 2, Chnl 5, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 3, Chnl 6, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 3, Chnl 7, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Platform Controller Hub: [PCH] <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
PCH Device ID:                       8086:1B81 (EBG)
PCH Stepping:                        17
PCH Thermal Sensor Enable:           0
PCH Hot Level (PHL):                 115


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> PTAT Current Settings:         <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU Test Selected:                   0
MEM Test Selected:                   0
CPU Mask:                            0xFFFFFFFF
CPU Core Mask:                       0xFFFFFFFFFFFFFFFF
CPU Thread Mask:                     0xFFFFFFFFFFFFFFFF
MEM Mask:                            0xFFFF
MEM Core Mask:                       0xFFFFFFFFFFFFFFFF
MEM Thread Mask:                     0xFFFFFFFFFFFFFFFF
Core Power Level:                    100
Memory Power Level:                  100
Turbo Enabled:                       No
AVX Test Level:                      1
Pmax Pre-sync:                       5000 ms
Pmax Post-sync:                      3000 ms
Pmax Idle:                           2000 ms
Run Time:                            0 (Forever)
PTAT Mon CPU Mask:                   0xFFFFFFFFFFFFFFFF
PTAT Mon Core Mask:                  0xFFFFFFFFFFFFFFFF
PTAT Mon MEM Mask:                   0xFFFFFFFF
PTAT Mon Filter Mask:                0x1F
PTAT Mon Update Interval:            1000000 usec
PTAT Mon Long Level:                 0
PTAT Mon Timestamp:                  No
Log Enabled:                         No
Log Directory:                       /root/ptat/log
Log File Prefix:                     <timestamp>
Log Message File:                    <timestamp>_ptatmsg.txt
Log Monitor File:                    <timestamp>_ptatmon.txt
CSV Enabled:                         No
PTAT License Auto Accept:            No
PTAT Driver Loaded:                  Yes

[03/29/24 23:30:45 UTC] PTAT started.

Press <Ctrl-C> to stop.


 Index Device Cor Thr CFreq UFreq  PState   Util  IPC     C0     C1     C6    PC2    PC6 MC Ch Sl  Temp DTS  Power  Volt UVolt TStat TLog #TL TMargin MCPMargin
     0   CPU0   -   -  2223  1600       0 100.00 6.83 100.00   0.00   0.00   0.00   0.00  -  -  -    80  11 194.85 0.723 0.725   0x0  0x0   0   2.469     2.469
     0   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    50   -  11.09     -     -     -  0x0   -       -         -
     1   CPU0   -   -  2193  1600       0 100.00 6.87 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 194.79 0.721 0.725   0x0  0x0   0   2.375     2.375
     1   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    50   -  11.16     -     -     -  0x0   -       -         -
     2   CPU0   -   -  2192  1600       0 100.00 6.87 100.00   0.00   0.00   0.00   0.00  -  -  -    80  11 194.95 0.723 0.725   0x0  0x0   0   2.438     2.438
     2   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    50   -  11.05     -     -     -  0x0   -       -         -
     3   CPU0   -   -  2194  1600       0 100.00 6.86 100.00   0.00   0.00   0.00   0.00  -  -  -    80  11 194.88 0.711 0.725   0x0  0x0   0   2.312     2.312
     3   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    50   -  11.24     -     -     -  0x0   -       -         -
     4   CPU0   -   -  2189  1600       0 100.00 6.85 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 194.81 0.723 0.725   0x0  0x0   0   2.469     2.469
     4   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    50   -  11.31     -     -     -  0x0   -       -         -
     5   CPU0   -   -  2193  1600       0 100.00 6.84 100.00   0.00   0.00   0.00   0.00  -  -  -    80  11 194.70 0.723 0.725   0x0  0x0   0   2.297     2.297
     5   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    50   -  11.36     -     -     -  0x0   -       -         -
     6   CPU0   -   -  2197  1600       0 100.00 6.83 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 195.09 0.723 0.725   0x0  0x0   0   2.219     2.219
     6   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    50   -  11.44     -     -     -  0x0   -       -         -
     7   CPU0   -   -  2192  1600       0 100.00 6.83 100.00   0.00   0.00   0.00   0.00  -  -  -    80  11 194.97 0.723 0.725   0x0  0x0   0   2.281     2.281
     7   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    50   -  11.19     -     -     -  0x0   -       -         -
     8   CPU0   -   -  2191  1600       0 100.00 6.84 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 194.86 0.723 0.725   0x0  0x0   0   2.359     2.359
     8   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    50   -  11.04     -     -     -  0x0   -       -         -
     9   CPU0   -   -  2191  1600       0 100.00 6.83 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 194.78 0.723 0.725   0x0  0x0   0   1.844     1.844
     9   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    50   -  11.33     -     -     -  0x0   -       -         -
    10   CPU0   -   -  2193  1600       0 100.00 6.80 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 194.92 0.721 0.725   0x0  0x0   0   2.047     2.047
    10   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    50   -  11.48     -     -     -  0x0   -       -         -
    11   CPU0   -   -  2190  1600       0 100.00 6.83 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 194.85 0.721 0.725   0x0  0x0   0   1.953     1.953
    11   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    50   -  11.52     -     -     -  0x0   -       -         -
    12   CPU0   -   -  2191  1600       0 100.00 6.83 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 194.85 0.721 0.725   0x0  0x0   0   2.062     2.062
    12   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    50   -  11.43     -     -     -  0x0   -       -         -
    13   CPU0   -   -  2190  1600       0 100.00 6.85 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 194.97 0.723 0.725   0x0  0x0   0   1.984     1.984
    13   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    50   -  11.22     -     -     -  0x0   -       -         -
    14   CPU0   -   -  2192  1600       0 100.00 6.84 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 194.85 0.721 0.725   0x0  0x0   0   1.953     1.953
    14   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    50   -  11.51     -     -     -  0x0   -       -         -
    15   CPU0   -   -  2190  1600       0 100.00 6.85 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 194.73 0.711 0.725   0x0  0x0   0   1.750     1.750
    15   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    50   -  10.89     -     -     -  0x0   -       -         -
    16   CPU0   -   -  2193  1600       0 100.00 6.85 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 194.92 0.721 0.725   0x0  0x0   0   1.781     1.781
    16   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    50   -  11.49     -     -     -  0x0   -       -         -
    17   CPU0   -   -  2191  1600       0 100.00 6.87 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 194.99 0.721 0.725   0x0  0x0   0   1.672     1.672
    17   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    50   -  11.19     -     -     -  0x0   -       -         -
    18   CPU0   -   -  2191  1600       0 100.00 6.86 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 194.87 0.721 0.725   0x0  0x0   0   1.688     1.688
    18   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    50   -  11.21     -     -     -  0x0   -       -         -
    19   CPU0   -   -  2193  1600       0 100.00 6.84 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 194.81 0.723 0.725   0x0  0x0   0   1.453     1.453
    19   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    50   -  11.14     -     -     -  0x0   -       -         -
    20   CPU0   -   -  2189  1600       0 100.00 6.86 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 195.02 0.721 0.725   0x0  0x0   0   1.281     1.281
    20   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    50   -  11.11     -     -     -  0x0   -       -         -
    21   CPU0   -   -  2188  1600       0 100.00 6.85 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 194.79 0.721 0.725   0x0  0x0   0   1.391     1.391
    21   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    50   -  11.11     -     -     -  0x0   -       -         -
    22   CPU0   -   -  2188  1600       0 100.00 6.84 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 194.91 0.711 0.725   0x0  0x0   0   1.203     1.203
    22   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    50   -  11.17     -     -     -  0x0   -       -         -
    23   CPU0   -   -  2189  1600       0 100.00 6.84 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 194.84 0.721 0.725   0x0  0x0   0   1.375     1.375
    23   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    50   -  11.38     -     -     -  0x0   -       -         -
    24   CPU0   -   -  2189  1600       0 100.00 6.85 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 194.88 0.721 0.725   0x0  0x0   0   1.125     1.125
    24   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    50   -  11.50     -     -     -  0x0   -       -         -
    25   CPU0   -   -  2190  1600       0 100.00 6.85 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 194.92 0.721 0.725   0x0  0x0   0   1.375     1.375
    25   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    50   -  11.37     -     -     -  0x0   -       -         -
    26   CPU0   -   -  2189  1600       0 100.00 6.86 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 194.93 0.721 0.725   0x0  0x0   0   1.094     1.094
    26   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    50   -  11.33     -     -     -  0x0   -       -         -
    27   CPU0   -   -  2190  1600       0 100.00 6.86 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 194.77 0.721 0.725   0x0  0x0   0   1.000     1.000
    27   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    50   -  11.20     -     -     -  0x0   -       -         -
    28   CPU0   -   -  2190  1600       0 100.00 6.87 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 194.86 0.723 0.725   0x0  0x0   0   1.438     1.438
    28   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    50   -  11.16     -     -     -  0x0   -       -         -
    29   CPU0   -   -  2191  1600       0 100.00 6.85 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 194.89 0.721 0.725   0x0  0x0   0   1.281     1.281
    29   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    50   -  11.08     -     -     -  0x0   -       -         -
    30   CPU0   -   -  2191  1600       0 100.00 6.88 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 194.91 0.721 0.725   0x0  0x0   0   1.094     1.094
    30   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    50   -  10.99     -     -     -  0x0   -       -         -
    31   CPU0   -   -  2190  1600       0 100.00 6.87 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 194.91 0.721 0.725   0x0  0x0   0   1.359     1.359
    31   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    50   -  11.01     -     -     -  0x0   -       -         -
    32   CPU0   -   -  2189  1600       0 100.00 6.87 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 194.91 0.721 0.725   0x0  0x0   0   1.203     1.203
    32   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    50   -  11.10     -     -     -  0x0   -       -         -
    33   CPU0   -   -  2189  1600       0 100.00 6.87 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 194.94 0.711 0.725   0x0  0x0   0   1.031     1.031
    33   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    50   -  11.07     -     -     -  0x0   -       -         -
    34   CPU0   -   -  2188  1600       0 100.00 6.86 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 194.78 0.723 0.725   0x0  0x0   0   1.156     1.156
    34   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    50   -  11.09     -     -     -  0x0   -       -         -
    35   CPU0   -   -  2192  1600       0 100.00 6.87 100.00   0.00   0.00   0.00   0.00  -  -  -    82   9 195.00 0.721 0.725   0x0  0x0   0   1.094     1.094
    35   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    50   -  10.91     -     -     -  0x0   -       -         -
^C
[03/29/24 23:31:25 UTC] PTAT stopped.

root@controller-0:/home/XXXXXX/compile/Ptu#
```

## check sensors

```log
root@controller-0:/home/XXXXXX/compile/Ptu#  ipmitool sensor| grep -e CPU -e DutyCycle -e Watts
02-CPU 1 PkgTmp  | 81.000     | degrees C  | ok    | na        | na        | na        | na        | 91.000    | na
Fan 1 DutyCycle  | 37.632     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 2 DutyCycle  | 37.632     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 3 DutyCycle  | 37.632     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 4 DutyCycle  | 37.632     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 5 DutyCycle  | 37.632     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 6 DutyCycle  | 37.632     | percent    | ok    | na        | na        | na        | na        | na        | na
PS 1 Input       | 210.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PS 2 Input       | 2550.000   | Watts      | ok    | na        | na        | na        | na        | na        | na
Power Meter      | 130.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
CPU Utilization  | 217.000    | unspecified | ok    | na        | na        | na        | na        | na        | na
PS 1 Output      | 0.000      | Watts      | ok    | na        | na        | na        | na        | na        | na
PS 2 Output      | 0.000      | Watts      | ok    | na        | na        | na        | na        | na        | na
CPU_Stat_C1      | 0x0        | discrete   | 0x8080| na        | na        | na        | na        | na        | na
root@controller-0:/home/XXXXXX/compile/Ptu#
```

## Success, was able to observe temp rise, then fans increasing as load was started


## MEAKV-646 
## PTU 5 - Turbo Test
## sudo ./ptat -ct 8 -b 1

## sensors before load

```log
root@controller-0:/home/XXXXXX/compile/Ptu#  ipmitool sensor| grep -e CPU -e DutyCycle -e Watts
02-CPU 1 PkgTmp  | 69.000     | degrees C  | ok    | na        | na        | na        | na        | 91.000    | na
Fan 1 DutyCycle  | 10.976     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 2 DutyCycle  | 10.976     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 3 DutyCycle  | 10.976     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 4 DutyCycle  | 10.976     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 5 DutyCycle  | 10.976     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 6 DutyCycle  | 10.976     | percent    | ok    | na        | na        | na        | na        | na        | na
PS 1 Input       | 140.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PS 2 Input       | 2550.000   | Watts      | ok    | na        | na        | na        | na        | na        | na
Power Meter      | 60.000     | Watts      | ok    | na        | na        | na        | na        | na        | na
CPU Utilization  | 10.000     | unspecified | ok    | na        | na        | na        | na        | na        | na
PS 1 Output      | 0.000      | Watts      | ok    | na        | na        | na        | na        | na        | na
PS 2 Output      | 0.000      | Watts      | ok    | na        | na        | na        | na        | na        | na
CPU_Stat_C1      | 0x0        | discrete   | 0x8080| na        | na        | na        | na        | na        | na
root@controller-0:/home/XXXXXX/compile/Ptu#
```

## Initiating load

```log
root@controller-0:/home/XXXXXX/compile/Ptu# ./ptat -ct 8 -b 1

Command: ./ptat -ct 8 -b 1

Intel(R) PTAT - Server Edition 4.4.0
Release Date: 12/19/2023
Copyright (C) 2023 Intel Corporation. All rights reserved.
Intel Confidential

>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> System Info:                   <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Host Name:                           controller-0
Host IP:                             169.254.202.1
OS Name:                             Debian GNU/Linux 11 (bullseye) 11
Kernel Version:                      Linux 5.10.0-6-rt-amd64 #1 SMP PREEMPT_RT StarlingX Debian 5.10.177-1.stx.73 (2023-11-25
BIOS Version:                        HPE, 1.11, 03/07/2024
Processor(s):                        1 Processor(s) Installed.
DIMM(s):                             8 DIMM(s) Installed.
Total System Memory:                 255208 MB
Available System Memory:             145050 MB


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Processor: [CPU_0]             <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU ID:                              0x000806F8 (Family 6 Model 8Fh Stepping 8)
CPU Brand Name:                      Intel(R) Xeon(R) Gold 6443N
CPU Code Name:                       Sapphire Rapids
CPU Type:                            Production Part
CPU Segment:                         Server
CPU PPIN:                            0x0000000000000000
CPU Base Frequency:                  1300 MHz
CPU Minimum Frequency:               800 MHz
CPU Maximum Turbo Frequency:         3600 MHz
Uncore Minimum Frequency:            1600 MHz
Uncore Maximum Frequency:            1600 MHz
L2 Cache:                            32 x 2048 KB
L3 Cache:                            61440 KB
Hyper-threading:                     Enabled
Microcode Update Revision:           0x2B000571
Number of Physcial Core(s):          32
Number of Logical Core(s):           64
Turbo Boost:                         Enabled
Turbo Boost Frequency:
 IA/SSE:
    1 - 16 Cores (Fused/Resolved):   3600 / 3600 (MHz)
   17 - 20 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   21 - 24 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   25 - 26 Cores (Fused/Resolved):   2900 / 2900 (MHz)
   27 - 32 Cores (Fused/Resolved):   2700 / 2700 (MHz)
 AVX2:
    1 - 16 Cores (Fused/Resolved):   3600 / 3600 (MHz)
   17 - 20 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   21 - 24 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   25 - 26 Cores (Fused/Resolved):   2800 / 2800 (MHz)
   27 - 32 Cores (Fused/Resolved):   2600 / 2600 (MHz)
 AVX-512:
    1 - 16 Cores (Fused/Resolved):   3600 / 3600 (MHz)
   17 - 20 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   21 - 24 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   25 - 26 Cores (Fused/Resolved):   2700 / 2700 (MHz)
   27 - 32 Cores (Fused/Resolved):   2500 / 2500 (MHz)
OVOLT_OVRD Supported:                0
OVOLT_OVRD Disabled:                 1
Platform ID:                         0x0
Platform Info:                       0x8405082EF4810D00
Thermal Design Power (TDP):          195 W
Power Limit 1 - Long Duration:       Enabled, Clamp ON , Power = 195 W, Time = 10.00 sec
Power Limit 2 - Short Duration:      Enabled, Clamp ON , Power = 234 W
Config TDP Level Supported:          3
Config TDP Level 1:                  195.0 W (110.0 W - 526.0 W), 0 MHz
Config TDP Level 2:                  195.0 W (110.0 W - 526.0 W), 0 MHz
Current Config TDP Level:            Nominal [Unlocked]
Tprochot:                            91 C
TCC Offset:                          0
CAPID0:                              0x42188138
CAPID1:                              0x5AC400C2
CAPID2:                              0xFF900003
CAPID3:                              0x07804000
CAPID4:                              0x04042EA0
CAPID5:                              0x6F0001EB
CAPID6:                              0xFDFEFFFF
CAPID7:                              0x00000003
CAPID8:                              0xFDFEFFFF
CAPID9:                              0x00000003
CAPID10:                             0x00000000


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Memory: [MEM_0]                <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Number of DIMM(s):                   8
Number of Active Channel(s):         8
DRAM Power Meter Disabled:           0
DRAM RAPL Disabled:                  0
DRAM TDP Power:                      Min = 15.0 W, Max = 66.0 W, Time = 0.31 sec
DRAM / NVDIMM Info:
  MC 0, Chnl 0, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 0, Chnl 1, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 1, Chnl 2, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 1, Chnl 3, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 2, Chnl 4, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 2, Chnl 5, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 3, Chnl 6, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 3, Chnl 7, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Platform Controller Hub: [PCH] <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
PCH Device ID:                       8086:1B81 (EBG)
PCH Stepping:                        17
PCH Thermal Sensor Enable:           0
PCH Hot Level (PHL):                 115


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> PTAT Current Settings:         <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU Test Selected:                   8
MEM Test Selected:                   0
CPU Mask:                            0xFFFFFFFF
CPU Core Mask:                       0xFFFFFFFFFFFFFFFF
CPU Thread Mask:                     0xFFFFFFFFFFFFFFFF
MEM Mask:                            0xFFFF
MEM Core Mask:                       0xFFFFFFFFFFFFFFFF
MEM Thread Mask:                     0xFFFFFFFFFFFFFFFF
Core Power Level:                    100
Memory Power Level:                  100
Turbo Enabled:                       Yes
AVX Test Level:                      1
Pmax Pre-sync:                       5000 ms
Pmax Post-sync:                      3000 ms
Pmax Idle:                           2000 ms
Run Time:                            0 (Forever)
PTAT Mon CPU Mask:                   0xFFFFFFFFFFFFFFFF
PTAT Mon Core Mask:                  0xFFFFFFFFFFFFFFFF
PTAT Mon MEM Mask:                   0xFFFFFFFF
PTAT Mon Filter Mask:                0x1F
PTAT Mon Update Interval:            1000000 usec
PTAT Mon Long Level:                 0
PTAT Mon Timestamp:                  No
Log Enabled:                         No
Log Directory:                       /root/ptat/log
Log File Prefix:                     <timestamp>
Log Message File:                    <timestamp>_ptatmsg.txt
Log Monitor File:                    <timestamp>_ptatmon.txt
CSV Enabled:                         No
PTAT License Auto Accept:            No
PTAT Driver Loaded:                  Yes

[03/29/24 23:38:30 UTC] PTAT started.

Press <Ctrl-C> to stop.


CPU_0: [IDLE] CFreq=2515, UFreq=1600, PState=0, Util=2.25, IPC=0.65, Temp=74, DTS=17, Power=75.2, Volt=0.763, UVolt=0.728

### TURBO is enabled ###

Instr   CPU #Cores CFreq(act) CFreq(exp) UFreq Power TDP  Temp Volt
IA/SSE  0   1      2.5        3.6        1.6   74.8  195  74   0.756
IA/SSE  0   2      2.5        3.6        1.6   77.2  195  74   0.756
IA/SSE  0   3      2.5        3.6        1.6   80.1  195  75   0.756
IA/SSE  0   4      2.5        3.6        1.6   81.9  195  74   0.756
IA/SSE  0   5      2.5        3.6        1.6   83.6  195  76   0.756
IA/SSE  0   6      2.5        3.6        1.6   85.8  195  76   0.757
IA/SSE  0   7      2.5        3.6        1.6   87.9  195  76   0.758
IA/SSE  0   8      2.5        3.6        1.6   90.3  195  77   0.758
IA/SSE  0   9      2.5        3.6        1.6   93.2  195  78   0.758
IA/SSE  0   10     2.5        3.6        1.6   95.1  195  78   0.757
IA/SSE  0   11     2.5        3.6        1.6   98.1  195  79   0.758
IA/SSE  0   12     2.5        3.6        1.6   99.2  195  79   0.757
IA/SSE  0   13     2.5        3.6        1.6   103.3 195  80   0.756
IA/SSE  0   14     2.5        3.6        1.6   105.3 195  80   0.756
IA/SSE  0   15     2.5        3.6        1.6   107.8 195  80   0.755
IA/SSE  0   16     2.5        3.6        1.6   110.0 195  81   0.755
IA/SSE  0   17     2.5        3.3        1.6   112.4 195  82   0.755
IA/SSE  0   18     2.5        3.3        1.6   114.8 195  82   0.756
IA/SSE  0   19     2.5        3.3        1.6   116.1 195  82   0.756
IA/SSE  0   20     2.5        3.3        1.6   119.1 195  83   0.756
IA/SSE  0   21     2.5        3.0        1.6   121.1 195  83   0.756
IA/SSE  0   22     2.5        3.0        1.6   125.0 195  83   0.755
IA/SSE  0   23     2.5        3.0        1.6   127.4 195  83   0.756
IA/SSE  0   24     2.5        3.0        1.6   129.4 195  83   0.756
IA/SSE  0   25     2.5        2.9        1.6   131.4 195  83   0.756
IA/SSE  0   26     2.5        2.9        1.6   134.1 195  83   0.756
IA/SSE  0   27     2.5        2.7        1.6   136.1 195  83   0.756
IA/SSE  0   28     2.5        2.7        1.6   135.7 195  83   0.756
IA/SSE  0   29     2.5        2.7        1.6   143.4 195  83   0.756
IA/SSE  0   30     2.5        2.7        1.6   142.8 195  84   0.756
IA/SSE  0   31     2.5        2.7        1.6   145.2 195  83   0.756
IA/SSE  0   32     2.5        2.7        1.6   147.6 195  83   0.756





```

## ptu -mon

```log
root@controller-0:/home/XXXXXX/compile/Ptu# ./ptat -mon

Command: ./ptat -mon

Intel(R) PTAT - Server Edition 4.4.0
Release Date: 12/19/2023
Copyright (C) 2023 Intel Corporation. All rights reserved.
Intel Confidential

>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> System Info:                   <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Host Name:                           controller-0
Host IP:                             169.254.202.1
OS Name:                             Debian GNU/Linux 11 (bullseye) 11
Kernel Version:                      Linux 5.10.0-6-rt-amd64 #1 SMP PREEMPT_RT StarlingX Debian 5.10.177-1.stx.73 (2023-11-25
BIOS Version:                        HPE, 1.11, 03/07/2024
Processor(s):                        1 Processor(s) Installed.
DIMM(s):                             8 DIMM(s) Installed.
Total System Memory:                 255208 MB
Available System Memory:             145038 MB


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Processor: [CPU_0]             <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU ID:                              0x000806F8 (Family 6 Model 8Fh Stepping 8)
CPU Brand Name:                      Intel(R) Xeon(R) Gold 6443N
CPU Code Name:                       Sapphire Rapids
CPU Type:                            Production Part
CPU Segment:                         Server
CPU PPIN:                            0x0000000000000000
CPU Base Frequency:                  1300 MHz
CPU Minimum Frequency:               800 MHz
CPU Maximum Turbo Frequency:         3600 MHz
Uncore Minimum Frequency:            1600 MHz
Uncore Maximum Frequency:            1600 MHz
L2 Cache:                            32 x 2048 KB
L3 Cache:                            61440 KB
Hyper-threading:                     Enabled
Microcode Update Revision:           0x2B000571
Number of Physcial Core(s):          32
Number of Logical Core(s):           64
Turbo Boost:                         Enabled
Turbo Boost Frequency:
 IA/SSE:
    1 - 16 Cores (Fused/Resolved):   3600 / 3600 (MHz)
   17 - 20 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   21 - 24 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   25 - 26 Cores (Fused/Resolved):   2900 / 2900 (MHz)
   27 - 32 Cores (Fused/Resolved):   2700 / 2700 (MHz)
 AVX2:
    1 - 16 Cores (Fused/Resolved):   3600 / 3600 (MHz)
   17 - 20 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   21 - 24 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   25 - 26 Cores (Fused/Resolved):   2800 / 2800 (MHz)
   27 - 32 Cores (Fused/Resolved):   2600 / 2600 (MHz)
 AVX-512:
    1 - 16 Cores (Fused/Resolved):   3600 / 3600 (MHz)
   17 - 20 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   21 - 24 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   25 - 26 Cores (Fused/Resolved):   2700 / 2700 (MHz)
   27 - 32 Cores (Fused/Resolved):   2500 / 2500 (MHz)
OVOLT_OVRD Supported:                0
OVOLT_OVRD Disabled:                 1
Platform ID:                         0x0
Platform Info:                       0x8405082EF4810D00
Thermal Design Power (TDP):          195 W
Power Limit 1 - Long Duration:       Enabled, Clamp ON , Power = 195 W, Time = 10.00 sec
Power Limit 2 - Short Duration:      Enabled, Clamp ON , Power = 234 W
Config TDP Level Supported:          3
Config TDP Level 1:                  195.0 W (110.0 W - 526.0 W), 0 MHz
Config TDP Level 2:                  195.0 W (110.0 W - 526.0 W), 0 MHz
Current Config TDP Level:            Nominal [Unlocked]
Tprochot:                            91 C
TCC Offset:                          0
CAPID0:                              0x42188138
CAPID1:                              0x5AC400C2
CAPID2:                              0xFF900003
CAPID3:                              0x07804000
CAPID4:                              0x04042EA0
CAPID5:                              0x6F0001EB
CAPID6:                              0xFDFEFFFF
CAPID7:                              0x00000003
CAPID8:                              0xFDFEFFFF
CAPID9:                              0x00000003
CAPID10:                             0x00000000


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Memory: [MEM_0]                <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Number of DIMM(s):                   8
Number of Active Channel(s):         8
DRAM Power Meter Disabled:           0
DRAM RAPL Disabled:                  0
DRAM TDP Power:                      Min = 15.0 W, Max = 66.0 W, Time = 0.31 sec
DRAM / NVDIMM Info:
  MC 0, Chnl 0, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 0, Chnl 1, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 1, Chnl 2, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 1, Chnl 3, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 2, Chnl 4, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 2, Chnl 5, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 3, Chnl 6, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C
  MC 3, Chnl 7, Slot 0:              tempLo: 83 C, tempMid: 93 C, tempHi: 95 C


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Platform Controller Hub: [PCH] <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
PCH Device ID:                       8086:1B81 (EBG)
PCH Stepping:                        17
PCH Thermal Sensor Enable:           0
PCH Hot Level (PHL):                 115


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> PTAT Current Settings:         <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU Test Selected:                   0
MEM Test Selected:                   0
CPU Mask:                            0xFFFFFFFF
CPU Core Mask:                       0xFFFFFFFFFFFFFFFF
CPU Thread Mask:                     0xFFFFFFFFFFFFFFFF
MEM Mask:                            0xFFFF
MEM Core Mask:                       0xFFFFFFFFFFFFFFFF
MEM Thread Mask:                     0xFFFFFFFFFFFFFFFF
Core Power Level:                    100
Memory Power Level:                  100
Turbo Enabled:                       No
AVX Test Level:                      1
Pmax Pre-sync:                       5000 ms
Pmax Post-sync:                      3000 ms
Pmax Idle:                           2000 ms
Run Time:                            0 (Forever)
PTAT Mon CPU Mask:                   0xFFFFFFFFFFFFFFFF
PTAT Mon Core Mask:                  0xFFFFFFFFFFFFFFFF
PTAT Mon MEM Mask:                   0xFFFFFFFF
PTAT Mon Filter Mask:                0x1F
PTAT Mon Update Interval:            1000000 usec
PTAT Mon Long Level:                 0
PTAT Mon Timestamp:                  No
Log Enabled:                         No
Log Directory:                       /root/ptat/log
Log File Prefix:                     <timestamp>
Log Message File:                    <timestamp>_ptatmsg.txt
Log Monitor File:                    <timestamp>_ptatmon.txt
CSV Enabled:                         No
PTAT License Auto Accept:            No
PTAT Driver Loaded:                  Yes

[03/29/24 23:42:38 UTC] PTAT started.

Press <Ctrl-C> to stop.


 Index Device Cor Thr CFreq UFreq  PState   Util  IPC     C0     C1     C6    PC2    PC6 MC Ch Sl  Temp DTS  Power  Volt UVolt TStat TLog #TL TMargin MCPMargin
     0   CPU0   -   -  2510  1600       0   3.04 0.70   4.07   0.16  95.77   0.00   0.00  -  -  -    76  15  76.24 0.753 0.725   0x0  0x0   0   6.750     6.750
     0   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    56   -  11.28     -     -     -  0x0   -       -         -
     1   CPU0   -   -  2452  1600       0   1.51 0.68   2.44   0.89  96.67   0.00   0.00  -  -  -    77  14  74.79 0.753 0.725   0x0  0x0   0   7.391     7.391
     1   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    56   -  11.08     -     -     -  0x0   -       -         -
     2   CPU0   -   -  2528  1600       0   2.76 0.59   3.82   0.22  95.96   0.00   0.00  -  -  -    76  15  75.66 0.753 0.725   0x0  0x0   0   7.078     7.078
     2   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    56   -  11.29     -     -     -  0x0   -       -         -
     3   CPU0   -   -  2521  1600       0   2.31 0.65   3.34   0.68  95.97   0.00   0.00  -  -  -    75  16  75.65 0.753 0.725   0x0  0x0   0   6.938     6.938
     3   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    56   -  11.30     -     -     -  0x0   -       -         -
     4   CPU0   -   -  2497  1600       0   1.48 0.66   2.36   0.92  96.72   0.00   0.00  -  -  -    76  15  74.40 0.753 0.725   0x0  0x0   0   7.344     7.344
     4   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    56   -  11.01     -     -     -  0x0   -       -         -
     5   CPU0   -   -  2510  1600       0   0.88 0.65   1.59   1.20  97.21   0.00   0.00  -  -  -    75  16  73.56 0.753 0.725   0x0  0x0   0   7.328     7.328
     5   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    56   -  10.78     -     -     -  0x0   -       -         -
     6   CPU0   -   -  2485  1600       0   1.84 0.60   2.94   0.55  96.51   0.00   0.00  -  -  -    76  15  74.44 0.753 0.725   0x0  0x0   0   7.406     7.406
     6   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    56   -  10.77     -     -     -  0x0   -       -         -
     7   CPU0   -   -  2529  1600       0   2.77 0.67   4.24   0.19  95.57   0.00   0.00  -  -  -    77  14  75.88 0.753 0.725   0x0  0x0   0   6.906     6.906
     7   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    56   -  11.05     -     -     -  0x0   -       -         -
     8   CPU0   -   -  2442  1600       0   2.98 0.65   4.09   0.23  95.68   0.00   0.00  -  -  -    75  16  76.36 0.753 0.725   0x0  0x0   0   5.688     5.688
     8   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    56   -  11.13     -     -     -  0x0   -       -         -
     9   CPU0   -   -  2502  1600       0   1.83 0.58   3.14   0.58  96.28   0.00   0.00  -  -  -    76  15  74.74 0.753 0.725   0x0  0x0   0   6.797     6.797
     9   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    56   -  11.09     -     -     -  0x0   -       -         -
    10   CPU0   -   -  2500  1600       0   1.19 0.57   1.75   1.00  97.25   0.00   0.00  -  -  -    76  15  73.90 0.753 0.725   0x0  0x0   0   7.609     7.609
    10   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    56   -  11.04     -     -     -  0x0   -       -         -
    11   CPU0   -   -  2528  1600       0   1.26 0.65   2.20   1.08  96.72   0.00   0.00  -  -  -    75  16  74.31 0.753 0.725   0x0  0x0   0   7.578     7.578
    11   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    56   -  11.07     -     -     -  0x0   -       -         -
    12   CPU0   -   -  2540  1600       0   1.85 0.66   2.99   0.90  96.11   0.00   0.00  -  -  -    75  16  75.07 0.753 0.725   0x0  0x0   0   7.172     7.172
    12   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    56   -  11.35     -     -     -  0x0   -       -         -
    13   CPU0   -   -  2472  1600       0   1.61 0.63   2.78   1.01  96.21   0.00   0.00  -  -  -    75  16  74.69 0.756 0.725   0x0  0x0   0   6.984     6.984
    13   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    56   -  11.31     -     -     -  0x0   -       -         -
    14   CPU0   -   -  2485  1600       0   1.99 0.61   3.25   0.49  96.25   0.00   0.00  -  -  -    77  14  75.20 0.753 0.725   0x0  0x0   0   6.984     6.984
    14   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    56   -  10.99     -     -     -  0x0   -       -         -
    15   CPU0   -   -  2528  1600       0   2.81 0.64   3.78   0.43  95.79   0.00   0.00  -  -  -    76  15  76.06 0.753 0.725   0x0  0x0   0   6.047     6.047
    15   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    56   -  11.57     -     -     -  0x0   -       -         -
    16   CPU0   -   -  2470  1600       0   1.31 0.62   2.24   0.98  96.78   0.00   0.00  -  -  -    76  15  74.23 0.753 0.725   0x0  0x0   0   7.203     7.203
    16   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    56   -  11.10     -     -     -  0x0   -       -         -
    17   CPU0   -   -  2497  1600       0   2.90 0.61   3.83   0.20  95.97   0.00   0.00  -  -  -    77  14  75.99 0.753 0.725   0x0  0x0   0   6.562     6.562
    17   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    56   -  11.34     -     -     -  0x0   -       -         -
    18   CPU0   -   -  2515  1600       0   2.93 0.62   3.84   0.18  95.98   0.00   0.00  -  -  -    78  13  76.13 0.753 0.725   0x0  0x0   0   5.703     5.703
    18   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    56   -  11.29     -     -     -  0x0   -       -         -
    19   CPU0   -   -  2541  1600       0   3.17 0.68   4.24   0.15  95.61   0.00   0.00  -  -  -    78  13  76.65 0.753 0.725   0x0  0x0   0   5.891     5.891
    19   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    56   -  11.50     -     -     -  0x0   -       -         -
    20   CPU0   -   -  2457  1600       0   3.28 0.61   4.11   0.22  95.67   0.00   0.00  -  -  -    78  13  76.54 0.753 0.725   0x0  0x0   0   5.281     5.281
    20   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    56   -  11.35     -     -     -  0x0   -       -         -
    21   CPU0   -   -  2499  1600       0   3.27 0.63   4.08   0.19  95.72   0.00   0.00  -  -  -    77  14  76.29 0.753 0.725   0x0  0x0   0   5.281     5.281
    21   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    56   -  11.06     -     -     -  0x0   -       -         -
    22   CPU0   -   -  2527  1600       0   1.72 0.61   2.64   0.84  96.52   0.00   0.00  -  -  -    78  13  74.67 0.753 0.725   0x0  0x0   0   6.547     6.547
    22   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    57   -  11.32     -     -     -  0x0   -       -         -
    23   CPU0   -   -  2504  1600       0   1.76 0.66   2.78   0.79  96.43   0.00   0.00  -  -  -    75  16  75.01 0.753 0.725   0x0  0x0   0   6.922     6.922
    23   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    57   -  11.17     -     -     -  0x0   -       -         -
    24   CPU0   -   -  2519  1600       0   1.28 0.69   2.27   0.97  96.76   0.00   0.00  -  -  -    78  13  74.38 0.753 0.725   0x0  0x0   0   7.000     7.000
    24   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    57   -  11.04     -     -     -  0x0   -       -         -
    25   CPU0   -   -  2492  1600       0   0.94 0.65   1.71   1.09  97.21   0.00   0.00  -  -  -    75  16  73.77 0.756 0.725   0x0  0x0   0   7.219     7.219
    25   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    57   -  10.95     -     -     -  0x0   -       -         -
    26   CPU0   -   -  2507  1600       0   1.09 0.60   1.89   1.03  97.07   0.00   0.00  -  -  -    78  13  73.79 0.753 0.725   0x0  0x0   0   7.469     7.469
    26   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    57   -  11.04     -     -     -  0x0   -       -         -
    27   CPU0   -   -  2460  1600       0   2.66 0.64   4.08   0.20  95.72   0.00   0.00  -  -  -    76  15  75.97 0.753 0.725   0x0  0x0   0   6.688     6.688
    27   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    57   -  11.06     -     -     -  0x0   -       -         -
    28   CPU0   -   -  2487  1600       0   1.53 0.64   2.50   0.83  96.66   0.00   0.00  -  -  -    76  15  74.62 0.753 0.725   0x0  0x0   0   6.406     6.406
    28   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    57   -  11.02     -     -     -  0x0   -       -         -
    29   CPU0   -   -  2531  1600       0   1.30 0.65   2.09   1.02  96.88   0.00   0.00  -  -  -    75  16  74.32 0.753 0.725   0x0  0x0   0   7.219     7.219
    29   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    57   -  10.99     -     -     -  0x0   -       -         -
    30   CPU0   -   -  2528  1600       0   1.24 0.60   2.06   1.03  96.91   0.00   0.00  -  -  -    75  16  74.11 0.753 0.725   0x0  0x0   0   6.688     6.688
    30   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    57   -  11.02     -     -     -  0x0   -       -         -
    31   CPU0   -   -  2492  1600       0   1.81 0.64   2.85   0.70  96.45   0.00   0.00  -  -  -    76  15  74.85 0.753 0.725   0x0  0x0   0   6.984     6.984
    31   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    57   -  11.21     -     -     -  0x0   -       -         -
    32   CPU0   -   -  2509  1600       0   1.99 0.62   3.27   0.90  95.82   0.00   0.00  -  -  -    78  13  75.56 0.753 0.725   0x0  0x0   0   6.656     6.656
    32   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    57   -  11.45     -     -     -  0x0   -       -         -
    33   CPU0   -   -  2511  1600       0   2.55 0.56   3.72   0.29  95.99   0.00   0.00  -  -  -    75  16  75.73 0.753 0.725   0x0  0x0   0   6.484     6.484
    33   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    57   -  11.12     -     -     -  0x0   -       -         -
    34   CPU0   -   -  2511  1600       0   1.80 0.64   2.92   0.70  96.39   0.00   0.00  -  -  -    75  16  74.98 0.753 0.725   0x0  0x0   0   6.641     6.641
    34   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    57   -  11.10     -     -     -  0x0   -       -         -
    35   CPU0   -   -  2509  1600       0   1.46 0.67   2.30   1.00  96.70   0.00   0.00  -  -  -    75  16  74.44 0.753 0.725   0x0  0x0   0   7.234     7.234
    35   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    57   -  11.05     -     -     -  0x0   -       -         -
^C
[03/29/24 23:43:18 UTC] PTAT stopped.

root@controller-0:/home/XXXXXX/compile/Ptu#
```

## Sensors after load started

```log
root@controller-0:/home/XXXXXX/compile/Ptu#  ipmitool sensor| grep -e CPU -e DutyCycle -e Watts
02-CPU 1 PkgTmp  | 76.000     | degrees C  | ok    | na        | na        | na        | na        | 91.000    | na
Fan 1 DutyCycle  | 11.760     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 2 DutyCycle  | 11.760     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 3 DutyCycle  | 11.760     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 4 DutyCycle  | 11.760     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 5 DutyCycle  | 11.760     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 6 DutyCycle  | 11.760     | percent    | ok    | na        | na        | na        | na        | na        | na
PS 1 Input       | 150.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PS 2 Input       | 2550.000   | Watts      | ok    | na        | na        | na        | na        | na        | na
Power Meter      | 60.000     | Watts      | ok    | na        | na        | na        | na        | na        | na
CPU Utilization  | 7.000      | unspecified | ok    | na        | na        | na        | na        | na        | na
PS 1 Output      | 0.000      | Watts      | ok    | na        | na        | na        | na        | na        | na
PS 2 Output      | 0.000      | Watts      | ok    | na        | na        | na        | na        | na        | na
CPU_Stat_C1      | 0x0        | discrete   | 0x8080| na        | na        | na        | na        | na        | na
root@controller-0:/home/XXXXXX/compile/Ptu#
```


## Temps didn't rise as much as with other tests, but all data recorded, no issues found.
## Success, end of performance tests with PTU