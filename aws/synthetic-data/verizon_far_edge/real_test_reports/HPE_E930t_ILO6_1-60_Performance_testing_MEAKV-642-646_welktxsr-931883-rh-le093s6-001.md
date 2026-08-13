# HPE ILO6 1.60 BIOS H11 v1.11
# HPE Sapphire Rapids E930t server
# 3/24/24 James Patchett - MTCE Lab VCPfe
# Performance Test MEAKV-642-646 

## welktxsr-931883-rh-le093s6-001
ILO:  2607:f160:10:80b1:ce:40a:0:e002
OAM:  2607:f160:10:80b1:ce:40a:0:f402

## Subcloud welktxsr-d931883-001
## General info before we start

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ system show
+------------------------+--------------------------------------+
| Property               | Value                                |
+------------------------+--------------------------------------+
| contact                | None                                 |
| created_at             | 2024-06-28T16:59:06.305793+00:00     |
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
| updated_at             | 2024-06-28T17:49:39.995411+00:00     |
| uuid                   | bb1b30b6-3971-4a90-b360-77c37e117c8f |
| vswitch_type           | none                                 |
+------------------------+--------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ system oam-show
+----------------+---------------------------------------+
| Property       | Value                                 |
+----------------+---------------------------------------+
| created_at     | 2024-06-28T17:00:44.323797+00:00      |
| isystem_uuid   | bb1b30b6-3971-4a90-b360-77c37e117c8f  |
| oam_end_ip     | 2607:f160:10:80b1:ffff:ffff:ffff:fffe |
| oam_gateway_ip | 2607:f160:10:80b1:ce:23::             |
| oam_ip         | 2607:f160:10:80b1:ce:40a:0:f402       |
| oam_start_ip   | 2607:f160:10:80b1::1                  |
| oam_subnet     | 2607:f160:10:80b1::/64                |
| updated_at     | None                                  |
| uuid           | d7c9003a-12f6-42f7-b7c9-e953d5f0eeb7  |
+----------------+---------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ system application-list
+--------------------------+----------+-------------------------------------------+------------------+---------+-----------+
| application              | version  | manifest name                             | manifest file    | status  | progress  |
+--------------------------+----------+-------------------------------------------+------------------+---------+-----------+
| cert-manager             | 22.12-8  | cert-manager-fluxcd-manifests             | fluxcd-manifests | applied | completed |
| metrics-server           | 22.12-2  | metrics-server-fluxcd-manifests           | fluxcd-manifests | applied | completed |
| nginx-ingress-controller | 22.12-1  | nginx-ingress-controller-fluxcd-manifests | fluxcd-manifests | applied | completed |
| oidc-auth-apps           | 22.12-6  | oidc-auth-apps-fluxcd-manifests           | fluxcd-manifests | applied | completed |
| platform-integ-apps      | 22.12-72 | platform-integ-apps-fluxcd-manifests      | fluxcd-manifests | applied | completed |
| wr-analytics             | 23.09-1  | wr-analytics-fluxcd-manifests             | fluxcd-manifests | applied | completed |
+--------------------------+----------+-------------------------------------------+------------------+---------+-----------+
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

## MEAKV-642
## Performance Test sudo ./ptat -ct 1 -b 0
## measure sensors first, then run load, then check during load

## Sensors
```log
root@controller-0:/home/XXXXXX/james# ipmitool sensor| grep -e CPU -e DutyCycle
02-CPU 1 PkgTmp  | 63.000     | degrees C  | ok    | na        | na        | na        | na        | 91.000    | na
Fan 1 DutyCycle  | 15.680     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 2 DutyCycle  | 15.680     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 3 DutyCycle  | 15.680     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 4 DutyCycle  | 15.680     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 5 DutyCycle  | 15.680     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 6 DutyCycle  | 15.680     | percent    | ok    | na        | na        | na        | na        | na        | na
CPU Utilization  | 7.000      | unspecified | ok    | na        | na        | na        | na        | na        | na
CPU_Stat_C1      | 0x0        | discrete   | 0x8080| na        | na        | na        | na        | na        | na
root@controller-0:/home/XXXXXX/james#
```

## Initiate load 

```log
root@controller-0:/home/XXXXXX/james# ./ptat -ct 1 -b 0 -id

Command: ./ptat -ct 1 -b 0 -id

Intel(R) PTAT - Server Edition 4.4.0
Release Date: 12/19/2023
Copyright (C) 2023 Intel Corporation. All rights reserved.
Intel Confidential

insmod: ERROR: could not insert module driver/ptusys/ptusys.ko: Invalid module format
ptusys driver installation failed
/dev/ptusys: No such file or directory
insmod: ERROR: could not insert module driver/ptusys/ptusys.ko: Invalid module format
ptusys driver installation failed
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> System Info:                   <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Host Name:                           controller-0
Host IP:                             169.254.202.1
OS Name:                             Debian GNU/Linux 11 (bullseye) 11
Kernel Version:                      Linux 5.10.0-6-rt-amd64 #1 SMP PREEMPT_RT StarlingX Debian 5.10.177-1.stx.76 (2024-03-29
BIOS Version:                        HPE, 1.11, 03/07/2024
Processor(s):                        1 Processor(s) Installed.
DIMM(s):                             8 DIMM(s) Installed.
Total System Memory:                 255208 MB
Available System Memory:             180838 MB


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
CAPID6:                              0xEFFFFFFB
CAPID7:                              0x00000003
CAPID8:                              0xEFFFFFFB
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
PTAT Driver Loaded:                  No

[06/28/24 20:42:23 UTC] PTAT started.

Press <Ctrl-C> to stop.


CPU_0: [IDLE] CFreq=1296, UFreq=1600, PState=1, Util=2.12, IPC=1.67, Temp=58, DTS=33, Power=70.7, Volt=0.683, UVolt=0.740
MEM_0: [IDLE] Power=13.33, Temp=37, Read=0.0, Write=0.0
MEM_0: [TESTCFG] TestSel=1 (Read), CoreMask=0x1, ThreadMask=0x1, PwrLevel=100, Turbo=0
MEM_0: [RUNNING] Power=13.36, Temp=37, Read=726.6, Write=279.7
CPU_0: , CoreMask=0xFFFFFFFFFFFFFFFF, ThreadMask=0xFFFFFFFFFFFFFFFF, PwrLevel=TDP, Turbo=0
CPU_0: [RUNNING] CFreq=1300, UFreq=1600, PState=1, Util=100.00, IPC=6.00, Temp=65, DTS=26, Power=137.6, Volt=0.678, UVolt=0.738

```

## Ptu monitoring

```log
root@controller-0:/home/XXXXXX/james# ./ptat -mon -id

Command: ./ptat -mon -id

Intel(R) PTAT - Server Edition 4.4.0
Release Date: 12/19/2023
Copyright (C) 2023 Intel Corporation. All rights reserved.
Intel Confidential

insmod: ERROR: could not insert module driver/ptusys/ptusys.ko: Invalid module format
ptusys driver installation failed
/dev/ptusys: No such file or directory
insmod: ERROR: could not insert module driver/ptusys/ptusys.ko: Invalid module format
ptusys driver installation failed
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> System Info:                   <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Host Name:                           controller-0
Host IP:                             169.254.202.1
OS Name:                             Debian GNU/Linux 11 (bullseye) 11
Kernel Version:                      Linux 5.10.0-6-rt-amd64 #1 SMP PREEMPT_RT StarlingX Debian 5.10.177-1.stx.76 (2024-03-29
BIOS Version:                        HPE, 1.11, 03/07/2024
Processor(s):                        1 Processor(s) Installed.
DIMM(s):                             8 DIMM(s) Installed.
Total System Memory:                 255208 MB
Available System Memory:             180683 MB


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
CAPID6:                              0xEFFFFFFB
CAPID7:                              0x00000003
CAPID8:                              0xEFFFFFFB
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
PTAT Driver Loaded:                  No

[06/28/24 20:44:51 UTC] PTAT started.

Press <Ctrl-C> to stop.


 Index Device Cor Thr CFreq UFreq  PState   Util  IPC     C0     C1     C6    PC2    PC6 MC Ch Sl  Temp DTS  Power  Volt UVolt TStat TLog #TL TMargin MCPMargin
     0   CPU0   -   -  1304  1600       1 100.00 5.99 100.00   0.00   0.00   0.00   0.00  -  -  -    80  11 140.42 0.668 0.725   0x0  0x0   0   2.734     2.734
     0   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.35     -     -     -  0x0   -       -         -
     1   CPU0   -   -  1300  1600       1 100.00 5.93 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 140.30 0.671 0.725   0x0  0x0   0   2.844     2.844
     1   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.40     -     -     -  0x0   -       -         -
     2   CPU0   -   -  1300  1600       1 100.00 5.97 100.00   0.00   0.00   0.00   0.00  -  -  -    80  11 140.43 0.671 0.725   0x0  0x0   0   2.766     2.766
     2   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.23     -     -     -  0x0   -       -         -
     3   CPU0   -   -  1300  1600       1 100.00 5.98 100.00   0.00   0.00   0.00   0.00  -  -  -    80  11 140.11 0.671 0.725   0x0  0x0   0   2.891     2.891
     3   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.28     -     -     -  0x0   -       -         -
     4   CPU0   -   -  1300  1600       1 100.00 5.98 100.00   0.00   0.00   0.00   0.00  -  -  -    80  11 140.46 0.671 0.725   0x0  0x0   0   2.781     2.781
     4   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.20     -     -     -  0x0   -       -         -
     5   CPU0   -   -  1300  1600       1 100.00 5.99 100.00   0.00   0.00   0.00   0.00  -  -  -    80  11 140.38 0.671 0.725   0x0  0x0   0   2.734     2.734
     5   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.26     -     -     -  0x0   -       -         -
     6   CPU0   -   -  1300  1600       1 100.00 5.95 100.00   0.00   0.00   0.00   0.00  -  -  -    80  11 140.58 0.671 0.725   0x0  0x0   0   2.797     2.797
     6   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.22     -     -     -  0x0   -       -         -
     7   CPU0   -   -  1300  1600       1 100.00 5.96 100.00   0.00   0.00   0.00   0.00  -  -  -    80  11 140.22 0.671 0.725   0x0  0x0   0   3.078     3.078
     7   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.22     -     -     -  0x0   -       -         -
     8   CPU0   -   -  1300  1600       1 100.00 6.01 100.00   0.00   0.00   0.00   0.00  -  -  -    80  11 140.50 0.671 0.725   0x0  0x0   0   2.859     2.859
     8   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.21     -     -     -  0x0   -       -         -
     9   CPU0   -   -  1300  1600       1 100.00 6.02 100.00   0.00   0.00   0.00   0.00  -  -  -    80  11 140.32 0.671 0.725   0x0  0x0   0   2.953     2.953
     9   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.04     -     -     -  0x0   -       -         -
    10   CPU0   -   -  1300  1600       1 100.00 5.99 100.00   0.00   0.00   0.00   0.00  -  -  -    80  11 140.68 0.668 0.725   0x0  0x0   0   2.875     2.875
    10   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.25     -     -     -  0x0   -       -         -
    11   CPU0   -   -  1300  1600       1 100.00 5.96 100.00   0.00   0.00   0.00   0.00  -  -  -    80  11 140.51 0.671 0.725   0x0  0x0   0   2.922     2.922
    11   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.26     -     -     -  0x0   -       -         -
    12   CPU0   -   -  1300  1600       1 100.00 5.97 100.00   0.00   0.00   0.00   0.00  -  -  -    80  11 140.85 0.668 0.725   0x0  0x0   0   2.875     2.875
    12   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.16     -     -     -  0x0   -       -         -
    13   CPU0   -   -  1300  1600       1 100.00 5.92 100.00   0.00   0.00   0.00   0.00  -  -  -    80  11 140.67 0.671 0.725   0x0  0x0   0   2.781     2.781
    13   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.13     -     -     -  0x0   -       -         -
    14   CPU0   -   -  1300  1600       1 100.00 5.90 100.00   0.00   0.00   0.00   0.00  -  -  -    80  11 140.49 0.671 0.725   0x0  0x0   0   2.688     2.688
    14   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.30     -     -     -  0x0   -       -         -
    15   CPU0   -   -  1300  1600       1 100.00 5.92 100.00   0.00   0.00   0.00   0.00  -  -  -    80  11 140.33 0.671 0.725   0x0  0x0   0   2.875     2.875
    15   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.29     -     -     -  0x0   -       -         -
    16   CPU0   -   -  1300  1600       1 100.00 5.92 100.00   0.00   0.00   0.00   0.00  -  -  -    80  11 140.50 0.671 0.725   0x0  0x0   0   3.047     3.047
    16   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.33     -     -     -  0x0   -       -         -
    17   CPU0   -   -  1300  1600       1 100.00 5.97 100.00   0.00   0.00   0.00   0.00  -  -  -    80  11 140.74 0.671 0.725   0x0  0x0   0   2.844     2.844
    17   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.10     -     -     -  0x0   -       -         -
    18   CPU0   -   -  1300  1600       1 100.00 5.97 100.00   0.00   0.00   0.00   0.00  -  -  -    80  11 140.23 0.671 0.725   0x0  0x0   0   2.594     2.594
    18   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.14     -     -     -  0x0   -       -         -
    19   CPU0   -   -  1300  1600       1 100.00 5.96 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 139.00 0.668 0.725   0x0  0x0   0   2.719     2.719
    19   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.20     -     -     -  0x0   -       -         -
    20   CPU0   -   -  1300  1600       1 100.00 5.95 100.00   0.00   0.00   0.00   0.00  -  -  -    80  11 142.21 0.671 0.725   0x0  0x0   0   2.609     2.609
    20   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.34     -     -     -  0x0   -       -         -
    21   CPU0   -   -  1300  1600       1 100.00 5.89 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 140.50 0.671 0.725   0x0  0x0   0   2.531     2.531
    21   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.31     -     -     -  0x0   -       -         -
    22   CPU0   -   -  1300  1600       1 100.00 5.89 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 140.77 0.671 0.725   0x0  0x0   0   2.422     2.422
    22   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.67     -     -     -  0x0   -       -         -
    23   CPU0   -   -  1300  1600       1 100.00 5.87 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 140.77 0.671 0.725   0x0  0x0   0   2.203     2.203
    23   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.44     -     -     -  0x0   -       -         -
    24   CPU0   -   -  1300  1600       1 100.00 5.93 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 140.69 0.671 0.725   0x0  0x0   0   2.172     2.172
    24   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.35     -     -     -  0x0   -       -         -
    25   CPU0   -   -  1300  1600       1 100.00 5.94 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 140.62 0.668 0.725   0x0  0x0   0   1.953     1.953
    25   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.27     -     -     -  0x0   -       -         -
    26   CPU0   -   -  1300  1600       1 100.00 5.95 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 140.78 0.668 0.725   0x0  0x0   0   1.906     1.906
    26   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.29     -     -     -  0x0   -       -         -
    27   CPU0   -   -  1300  1600       1 100.00 5.96 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 140.70 0.671 0.725   0x0  0x0   0   2.078     2.078
    27   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.29     -     -     -  0x0   -       -         -
    28   CPU0   -   -  1300  1600       1 100.00 5.98 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 140.31 0.668 0.725   0x0  0x0   0   2.109     2.109
    28   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.14     -     -     -  0x0   -       -         -
    29   CPU0   -   -  1300  1600       1 100.00 5.97 100.00   0.00   0.00   0.00   0.00  -  -  -    81  10 140.86 0.668 0.725   0x0  0x0   0   1.891     1.891
    29   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.28     -     -     -  0x0   -       -         -
^C
[06/28/24 20:45:25 UTC] PTAT stopped.

root@controller-0:/home/XXXXXX/james#
```

## check the sensors again, to see the reaction to raised thermals

```log
root@controller-0:/home/XXXXXX/james#  ipmitool sensor| grep -e CPU -e DutyCycle
02-CPU 1 PkgTmp  | 83.000     | degrees C  | ok    | na        | na        | na        | na        | 91.000    | na
Fan 1 DutyCycle  | 39.984     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 2 DutyCycle  | 39.984     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 3 DutyCycle  | 39.984     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 4 DutyCycle  | 39.984     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 5 DutyCycle  | 37.632     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 6 DutyCycle  | 37.632     | percent    | ok    | na        | na        | na        | na        | na        | na
CPU Utilization  | 205.000    | unspecified | ok    | na        | na        | na        | na        | na        | na
CPU_Stat_C1      | 0x0        | discrete   | 0x8080| na        | na        | na        | na        | na        | na
root@controller-0:/home/XXXXXX/james#
```

## Success as we have observed thermals rising, along with fans increase in RPMs...  on to next test

## MEAKV-643
## Performance Test #2 
## Run Core IA/SSE with 100% power, and Turbo on
## ./ptat -ct 3 -cp 100 -b 1

## Sensors before run

```log
root@controller-0:/home/XXXXXX/james#  ipmitool sensor| grep -e CPU -e DutyCycle
02-CPU 1 PkgTmp  | 63.000     | degrees C  | ok    | na        | na        | na        | na        | 91.000    | na
Fan 1 DutyCycle  | 18.816     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 2 DutyCycle  | 18.816     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 3 DutyCycle  | 18.816     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 4 DutyCycle  | 18.816     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 5 DutyCycle  | 18.816     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 6 DutyCycle  | 18.816     | percent    | ok    | na        | na        | na        | na        | na        | na
CPU Utilization  | 9.000      | unspecified | ok    | na        | na        | na        | na        | na        | na
CPU_Stat_C1      | 0x0        | discrete   | 0x8080| na        | na        | na        | na        | na        | na
root@controller-0:/home/XXXXXX/james#
```

## Initiate Load 

```log
root@controller-0:/home/XXXXXX/james# ./ptat  -ct 3 -cp 100 -b 1 -id

Command: ./ptat -ct 3 -cp 100 -b 1 -id

Intel(R) PTAT - Server Edition 4.4.0
Release Date: 12/19/2023
Copyright (C) 2023 Intel Corporation. All rights reserved.
Intel Confidential

insmod: ERROR: could not insert module driver/ptusys/ptusys.ko: Invalid module format
ptusys driver installation failed
/dev/ptusys: No such file or directory
insmod: ERROR: could not insert module driver/ptusys/ptusys.ko: Invalid module format
ptusys driver installation failed
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> System Info:                   <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Host Name:                           controller-0
Host IP:                             169.254.202.1
OS Name:                             Debian GNU/Linux 11 (bullseye) 11
Kernel Version:                      Linux 5.10.0-6-rt-amd64 #1 SMP PREEMPT_RT StarlingX Debian 5.10.177-1.stx.76 (2024-03-29
BIOS Version:                        HPE, 1.11, 03/07/2024
Processor(s):                        1 Processor(s) Installed.
DIMM(s):                             8 DIMM(s) Installed.
Total System Memory:                 255208 MB
Available System Memory:             180807 MB


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
CAPID6:                              0xEFFFFFFB
CAPID7:                              0x00000003
CAPID8:                              0xEFFFFFFB
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
PTAT Driver Loaded:                  No

[06/28/24 20:52:46 UTC] PTAT started.

Press <Ctrl-C> to stop.


CPU_0: [IDLE] CFreq=3601, UFreq=1600, PState=0, Util=0.99, IPC=1.63, Temp=61, DTS=30, Power=73.9, Volt=0.948, UVolt=0.738
MEM_0: [IDLE] Power=13.38, Temp=38, Read=0.0, Write=0.0
MEM_0: [TESTCFG] TestSel=1 (Read), CoreMask=0x1, ThreadMask=0x1, PwrLevel=100, Turbo=1
MEM_0: [RUNNING] Power=13.45, Temp=38, Read=1070.6, Write=375.0
CPU_0: , CoreMask=0xFFFFFFFFFFFFFFFF, ThreadMask=0xFFFFFFFFFFFFFFFF, PwrLevel=100, Turbo=1
CPU_0: [RUNNING] CFreq=2095, UFreq=1600, PState=0, Util=100.00, IPC=6.03, Temp=74, DTS=17, Power=194.9, Volt=0.731, UVolt=0.733
```

## ptu -mon

```log
root@controller-0:/home/XXXXXX/james# ./ptat -mon -id

Command: ./ptat -mon -id

Intel(R) PTAT - Server Edition 4.4.0
Release Date: 12/19/2023
Copyright (C) 2023 Intel Corporation. All rights reserved.
Intel Confidential

insmod: ERROR: could not insert module driver/ptusys/ptusys.ko: Invalid module format
ptusys driver installation failed
/dev/ptusys: No such file or directory
insmod: ERROR: could not insert module driver/ptusys/ptusys.ko: Invalid module format
ptusys driver installation failed
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> System Info:                   <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Host Name:                           controller-0
Host IP:                             169.254.202.1
OS Name:                             Debian GNU/Linux 11 (bullseye) 11
Kernel Version:                      Linux 5.10.0-6-rt-amd64 #1 SMP PREEMPT_RT StarlingX Debian 5.10.177-1.stx.76 (2024-03-29
BIOS Version:                        HPE, 1.11, 03/07/2024
Processor(s):                        1 Processor(s) Installed.
DIMM(s):                             8 DIMM(s) Installed.
Total System Memory:                 255208 MB
Available System Memory:             180660 MB


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
CAPID6:                              0xEFFFFFFB
CAPID7:                              0x00000003
CAPID8:                              0xEFFFFFFB
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
PTAT Driver Loaded:                  No

[06/28/24 20:53:54 UTC] PTAT started.

Press <Ctrl-C> to stop.


 Index Device Cor Thr CFreq UFreq  PState   Util  IPC     C0     C1     C6    PC2    PC6 MC Ch Sl  Temp DTS  Power  Volt UVolt TStat TLog #TL TMargin MCPMargin
     0   CPU0   -   -  2115  1600       0 100.00 6.04 100.00   0.00   0.00   0.00   0.00  -  -  -    76  15 194.90 0.731 0.730   0x0  0x0   0   6.250     6.250
     0   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    49   -  12.86     -     -     -  0x0   -       -         -
     1   CPU0   -   -  2091  1600       0 100.00 5.96 100.00   0.00   0.00   0.00   0.00  -  -  -    77  14 194.81 0.731 0.730   0x0  0x0   0   6.297     6.297
     1   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    49   -  13.24     -     -     -  0x0   -       -         -
     2   CPU0   -   -  2092  1600       0 100.00 6.02 100.00   0.00   0.00   0.00   0.00  -  -  -    77  14 194.98 0.731 0.730   0x0  0x0   0   6.281     6.281
     2   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    49   -  13.02     -     -     -  0x0   -       -         -
     3   CPU0   -   -  2090  1600       0 100.00 6.02 100.00   0.00   0.00   0.00   0.00  -  -  -    77  14 194.84 0.731 0.730   0x0  0x0   0   6.062     6.062
     3   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    49   -  13.17     -     -     -  0x0   -       -         -
     4   CPU0   -   -  2087  1600       0 100.00 6.00 100.00   0.00   0.00   0.00   0.00  -  -  -    77  14 194.84 0.731 0.730   0x0  0x0   0   6.047     6.047
     4   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    49   -  13.14     -     -     -  0x0   -       -         -
     5   CPU0   -   -  2093  1600       0 100.00 5.97 100.00   0.00   0.00   0.00   0.00  -  -  -    77  14 194.90 0.731 0.730   0x0  0x0   0   6.078     6.078
     5   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    49   -  13.31     -     -     -  0x0   -       -         -
     6   CPU0   -   -  2096  1600       0 100.00 6.00 100.00   0.00   0.00   0.00   0.00  -  -  -    77  14 194.82 0.731 0.730   0x0  0x0   0   5.891     5.891
     6   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    49   -  13.14     -     -     -  0x0   -       -         -
     7   CPU0   -   -  2091  1600       0 100.00 5.99 100.00   0.00   0.00   0.00   0.00  -  -  -    77  14 194.91 0.731 0.730   0x0  0x0   0   5.875     5.875
     7   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    49   -  13.05     -     -     -  0x0   -       -         -
     8   CPU0   -   -  2091  1600       0 100.00 5.99 100.00   0.00   0.00   0.00   0.00  -  -  -    77  14 194.99 0.731 0.730   0x0  0x0   0   5.781     5.781
     8   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    49   -  13.14     -     -     -  0x0   -       -         -
     9   CPU0   -   -  2090  1600       0 100.00 5.96 100.00   0.00   0.00   0.00   0.00  -  -  -    77  14 194.81 0.731 0.730   0x0  0x0   0   5.641     5.641
     9   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    49   -  13.23     -     -     -  0x0   -       -         -
    10   CPU0   -   -  2093  1600       0 100.00 6.02 100.00   0.00   0.00   0.00   0.00  -  -  -    77  14 194.97 0.731 0.730   0x0  0x0   0   5.609     5.609
    10   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    49   -  13.05     -     -     -  0x0   -       -         -
    11   CPU0   -   -  2085  1600       0 100.00 5.95 100.00   0.00   0.00   0.00   0.00  -  -  -    77  14 194.86 0.731 0.730   0x0  0x0   0   5.578     5.578
    11   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    49   -  13.44     -     -     -  0x0   -       -         -
    12   CPU0   -   -  2086  1600       0 100.00 6.00 100.00   0.00   0.00   0.00   0.00  -  -  -    78  13 194.77 0.731 0.730   0x0  0x0   0   5.547     5.547
    12   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    49   -  13.28     -     -     -  0x0   -       -         -
    13   CPU0   -   -  2087  1600       0 100.00 6.02 100.00   0.00   0.00   0.00   0.00  -  -  -    78  13 194.96 0.731 0.730   0x0  0x0   0   5.422     5.422
    13   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    49   -  13.17     -     -     -  0x0   -       -         -
    14   CPU0   -   -  2083  1600       0 100.00 5.98 100.00   0.00   0.00   0.00   0.00  -  -  -    78  13 195.00 0.731 0.730   0x0  0x0   0   5.406     5.406
    14   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    49   -  13.21     -     -     -  0x0   -       -         -
    15   CPU0   -   -  2084  1600       0 100.00 6.03 100.00   0.00   0.00   0.00   0.00  -  -  -    78  13 194.77 0.731 0.730   0x0  0x0   0   5.156     5.156
    15   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    49   -  13.03     -     -     -  0x0   -       -         -
    16   CPU0   -   -  2084  1600       0 100.00 6.00 100.00   0.00   0.00   0.00   0.00  -  -  -    78  13 194.93 0.718 0.730   0x0  0x0   0   5.078     5.078
    16   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    49   -  13.12     -     -     -  0x0   -       -         -
    17   CPU0   -   -  2089  1600       0 100.00 5.99 100.00   0.00   0.00   0.00   0.00  -  -  -    78  13 194.84 0.718 0.730   0x0  0x0   0   5.156     5.156
    17   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    49   -  13.18     -     -     -  0x0   -       -         -
    18   CPU0   -   -  2087  1600       0 100.00 5.99 100.00   0.00   0.00   0.00   0.00  -  -  -    78  13 194.98 0.731 0.730   0x0  0x0   0   4.938     4.938
    18   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    49   -  13.18     -     -     -  0x0   -       -         -
    19   CPU0   -   -  2087  1600       0 100.00 5.95 100.00   0.00   0.00   0.00   0.00  -  -  -    78  13 194.87 0.731 0.730   0x0  0x0   0   4.781     4.781
    19   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    49   -  13.26     -     -     -  0x0   -       -         -
    20   CPU0   -   -  2086  1600       0 100.00 6.01 100.00   0.00   0.00   0.00   0.00  -  -  -    79  12 195.01 0.731 0.728   0x0  0x0   0   4.531     4.531
    20   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    49   -  13.10     -     -     -  0x0   -       -         -
    21   CPU0   -   -  2088  1600       0 100.00 6.00 100.00   0.00   0.00   0.00   0.00  -  -  -    79  12 194.77 0.728 0.728   0x0  0x0   0   4.266     4.266
    21   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    49   -  13.09     -     -     -  0x0   -       -         -
    22   CPU0   -   -  2083  1600       0 100.00 5.99 100.00   0.00   0.00   0.00   0.00  -  -  -    79  12 195.05 0.731 0.728   0x0  0x0   0   3.906     3.906
    22   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    49   -  13.07     -     -     -  0x0   -       -         -
    23   CPU0   -   -  2084  1600       0 100.00 5.99 100.00   0.00   0.00   0.00   0.00  -  -  -    79  12 194.76 0.731 0.728   0x0  0x0   0   3.812     3.812
    23   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    49   -  13.15     -     -     -  0x0   -       -         -
    24   CPU0   -   -  2086  1600       0 100.00 5.99 100.00   0.00   0.00   0.00   0.00  -  -  -    79  12 194.98 0.718 0.728   0x0  0x0   0   3.688     3.688
    24   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    49   -  13.34     -     -     -  0x0   -       -         -
    25   CPU0   -   -  2084  1600       0 100.00 6.01 100.00   0.00   0.00   0.00   0.00  -  -  -    80  11 194.88 0.731 0.728   0x0  0x0   0   3.500     3.500
    25   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    49   -  13.07     -     -     -  0x0   -       -         -
    26   CPU0   -   -  2085  1600       0 100.00 5.98 100.00   0.00   0.00   0.00   0.00  -  -  -    80  11 194.90 0.728 0.728   0x0  0x0   0   3.203     3.203
    26   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    49   -  13.34     -     -     -  0x0   -       -         -
    27   CPU0   -   -  2081  1600       0 100.00 6.01 100.00   0.00   0.00   0.00   0.00  -  -  -    80  11 194.91 0.718 0.728   0x0  0x0   0   3.031     3.031
    27   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    49   -  13.07     -     -     -  0x0   -       -         -
    28   CPU0   -   -  2083  1600       0 100.00 6.03 100.00   0.00   0.00   0.00   0.00  -  -  -    80  11 194.87 0.728 0.728   0x0  0x0   0   2.984     2.984
    28   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    49   -  12.97     -     -     -  0x0   -       -         -
    29   CPU0   -   -  2082  1600       0 100.00 6.02 100.00   0.00   0.00   0.00   0.00  -  -  -    80  11 194.88 0.728 0.728   0x0  0x0   0   2.859     2.859
    29   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    49   -  13.02     -     -     -  0x0   -       -         -
    30   CPU0   -   -  2085  1600       0 100.00 6.02 100.00   0.00   0.00   0.00   0.00  -  -  -    80  11 195.02 0.728 0.728   0x0  0x0   0   2.953     2.953
    30   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    49   -  12.99     -     -     -  0x0   -       -         -
    31   CPU0   -   -  2085  1600       0 100.00 6.04 100.00   0.00   0.00   0.00   0.00  -  -  -    80  11 194.70 0.728 0.728   0x0  0x0   0   2.969     2.969
    31   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    49   -  13.12     -     -     -  0x0   -       -         -
    32   CPU0   -   -  2085  1600       0 100.00 6.03 100.00   0.00   0.00   0.00   0.00  -  -  -    80  11 195.05 0.718 0.728   0x0  0x0   0   3.031     3.031
    32   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    49   -  13.17     -     -     -  0x0   -       -         -
    33   CPU0   -   -  2086  1600       0 100.00 6.02 100.00   0.00   0.00   0.00   0.00  -  -  -    80  11 194.77 0.728 0.728   0x0  0x0   0   2.875     2.875
    33   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    49   -  13.28     -     -     -  0x0   -       -         -
    34   CPU0   -   -  2087  1600       0 100.00 6.02 100.00   0.00   0.00   0.00   0.00  -  -  -    80  11 195.05 0.728 0.728   0x0  0x0   0   2.875     2.875
    34   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    49   -  13.16     -     -     -  0x0   -       -         -
    35   CPU0   -   -  2085  1600       0 100.00 6.04 100.00   0.00   0.00   0.00   0.00  -  -  -    80  11 194.91 0.728 0.728   0x0  0x0   0   3.078     3.078
    35   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    49   -  13.06     -     -     -  0x0   -       -         -
    36   CPU0   -   -  2083  1600       0 100.00 6.05 100.00   0.00   0.00   0.00   0.00  -  -  -    80  11 194.78 0.728 0.728   0x0  0x0   0   3.234     3.234
    36   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    49   -  13.16     -     -     -  0x0   -       -         -
    37   CPU0   -   -  2083  1600       0 100.00 6.03 100.00   0.00   0.00   0.00   0.00  -  -  -    80  11 194.99 0.728 0.728   0x0  0x0   0   3.094     3.094
    37   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    49   -  13.23     -     -     -  0x0   -       -         -
    38   CPU0   -   -  2084  1600       0 100.00 6.00 100.00   0.00   0.00   0.00   0.00  -  -  -    80  11 194.78 0.728 0.728   0x0  0x0   0   2.812     2.812
    38   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    49   -  13.33     -     -     -  0x0   -       -         -
    39   CPU0   -   -  2084  1600       0 100.00 6.01 100.00   0.00   0.00   0.00   0.00  -  -  -    80  11 194.98 0.728 0.728   0x0  0x0   0   2.812     2.812
    39   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    49   -  13.36     -     -     -  0x0   -       -         -
    40   CPU0   -   -  2087  1600       0 100.00 6.04 100.00   0.00   0.00   0.00   0.00  -  -  -    80  11 194.88 0.728 0.728   0x0  0x0   0   2.609     2.609
    40   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    49   -  13.14     -     -     -  0x0   -       -         -
    41   CPU0   -   -  2083  1600       0 100.00 6.02 100.00   0.00   0.00   0.00   0.00  -  -  -    80  11 194.89 0.728 0.728   0x0  0x0   0   2.797     2.797
    41   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    49   -  13.19     -     -     -  0x0   -       -         -
    42   CPU0   -   -  2084  1600       0 100.00 6.01 100.00   0.00   0.00   0.00   0.00  -  -  -    80  11 194.89 0.728 0.728   0x0  0x0   0   2.656     2.656
    42   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    49   -  13.23     -     -     -  0x0   -       -         -
    43   CPU0   -   -  2082  1600       0 100.00 6.01 100.00   0.00   0.00   0.00   0.00  -  -  -    80  11 194.96 0.718 0.728   0x0  0x0   0   2.719     2.719
    43   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    49   -  13.16     -     -     -  0x0   -       -         -
^C
[06/28/24 20:54:40 UTC] PTAT stopped.

root@controller-0:/home/XXXXXX/james#
```


## Sensors after load ~2-3mins after

```log
root@controller-0:/home/XXXXXX/james# ipmitool sensor| grep -e CPU -e DutyCycle -e Watts
02-CPU 1 PkgTmp  | 81.000     | degrees C  | ok    | na        | na        | na        | na        | 91.000    | na
Fan 1 DutyCycle  | 36.848     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 2 DutyCycle  | 36.848     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 3 DutyCycle  | 36.848     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 4 DutyCycle  | 36.848     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 5 DutyCycle  | 32.928     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 6 DutyCycle  | 32.928     | percent    | ok    | na        | na        | na        | na        | na        | na
PS 1 Input       | 190.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PS 2 Input       | 2550.000   | Watts      | ok    | na        | na        | na        | na        | na        | na
Power Meter      | 240.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
CPU Utilization  | 205.000    | unspecified | ok    | na        | na        | na        | na        | na        | na
PS 1 Output      | 0.000      | Watts      | ok    | na        | na        | na        | na        | na        | na
PS 2 Output      | 0.000      | Watts      | ok    | na        | na        | na        | na        | na        | na
CPU_Stat_C1      | 0x0        | discrete   | 0x8080| na        | na        | na        | na        | na        | na
root@controller-0:/home/XXXXXX/james#
```

## Test is success, observed temps rise and fan rpms rise with the load

## MEAKV-644
## Performance test PTU 3 - Core AVX2 with Turbo - MEAKV-644
## Run Core Intel® AVX-2 with power level 100% and Turbo on.
## sudo ./ptat -ct 4 -cp 100 -b 1

## Check sensors bofore starting load

```log
rroot@controller-0:~# ipmitool sensor| grep -e CPU -e DutyCycle -e Watts
02-CPU 1 PkgTmp  | 57.000     | degrees C  | ok    | na        | na        | na        | na        | 91.000    | na
Fan 1 DutyCycle  | 21.952     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 2 DutyCycle  | 17.640     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 3 DutyCycle  | 17.640     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 4 DutyCycle  | 17.640     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 5 DutyCycle  | 17.640     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 6 DutyCycle  | 17.640     | percent    | ok    | na        | na        | na        | na        | na        | na
PS 1 Input       | 140.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PS 2 Input       | 2550.000   | Watts      | ok    | na        | na        | na        | na        | na        | na
Power Meter      | 130.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
CPU Utilization  | 6.000      | unspecified | ok    | na        | na        | na        | na        | na        | na
PS 1 Output      | 0.000      | Watts      | ok    | na        | na        | na        | na        | na        | na
PS 2 Output      | 0.000      | Watts      | ok    | na        | na        | na        | na        | na        | na
CPU_Stat_C1      | 0x0        | discrete   | 0x8080| na        | na        | na        | na        | na        | na
root@controller-0:~#
```

## load Intiated

```log
root@controller-0:/home/XXXXXX/james# ./ptat  -ct 4 -cp 100 -b 1 -id

Command: ./ptat -ct 4 -cp 100 -b 1 -id

Intel(R) PTAT - Server Edition 4.4.0
Release Date: 12/19/2023
Copyright (C) 2023 Intel Corporation. All rights reserved.
Intel Confidential

insmod: ERROR: could not insert module driver/ptusys/ptusys.ko: Invalid module format
ptusys driver installation failed
/dev/ptusys: No such file or directory
insmod: ERROR: could not insert module driver/ptusys/ptusys.ko: Invalid module format
ptusys driver installation failed
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> System Info:                   <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Host Name:                           controller-0
Host IP:                             169.254.202.1
OS Name:                             Debian GNU/Linux 11 (bullseye) 11
Kernel Version:                      Linux 5.10.0-6-rt-amd64 #1 SMP PREEMPT_RT StarlingX Debian 5.10.177-1.stx.76 (2024-03-29
BIOS Version:                        HPE, 1.11, 03/07/2024
Processor(s):                        1 Processor(s) Installed.
DIMM(s):                             8 DIMM(s) Installed.
Total System Memory:                 255208 MB
Available System Memory:             180566 MB


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
CAPID6:                              0xEFFFFFFB
CAPID7:                              0x00000003
CAPID8:                              0xEFFFFFFB
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
PTAT Driver Loaded:                  No

[06/28/24 21:22:13 UTC] PTAT started.

Press <Ctrl-C> to stop.


CPU_0: [IDLE] CFreq=4332, UFreq=1600, PState=0, Util=1.25, IPC=1.82, Temp=60, DTS=31, Power=74.3, Volt=0.946, UVolt=0.740
MEM_0: [IDLE] Power=13.38, Temp=37, Read=0.0, Write=0.0
MEM_0: [TESTCFG] TestSel=1 (Read), CoreMask=0x1, ThreadMask=0x1, PwrLevel=100, Turbo=1
MEM_0: [RUNNING] Power=13.46, Temp=37, Read=792.8, Write=303.9
CPU_0: , CoreMask=0xFFFFFFFFFFFFFFFF, ThreadMask=0xFFFFFFFFFFFFFFFF, PwrLevel=100, Turbo=1
CPU_0: [RUNNING] CFreq=2322, UFreq=1600, PState=0, Util=100.00, IPC=6.85, Temp=71, DTS=20, Power=194.7, Volt=0.755, UVolt=0.735


```

## ptu -mon

```log
oot@controller-0:/home/XXXXXX/james# ./ptat -mon -id

Command: ./ptat -mon -id

Intel(R) PTAT - Server Edition 4.4.0
Release Date: 12/19/2023
Copyright (C) 2023 Intel Corporation. All rights reserved.
Intel Confidential

insmod: ERROR: could not insert module driver/ptusys/ptusys.ko: Invalid module format
ptusys driver installation failed
/dev/ptusys: No such file or directory
insmod: ERROR: could not insert module driver/ptusys/ptusys.ko: Invalid module format
ptusys driver installation failed
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> System Info:                   <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Host Name:                           controller-0
Host IP:                             169.254.202.1
OS Name:                             Debian GNU/Linux 11 (bullseye) 11
Kernel Version:                      Linux 5.10.0-6-rt-amd64 #1 SMP PREEMPT_RT StarlingX Debian 5.10.177-1.stx.76 (2024-03-29
BIOS Version:                        HPE, 1.11, 03/07/2024
Processor(s):                        1 Processor(s) Installed.
DIMM(s):                             8 DIMM(s) Installed.
Total System Memory:                 255208 MB
Available System Memory:             180536 MB


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
CAPID6:                              0xEFFFFFFB
CAPID7:                              0x00000003
CAPID8:                              0xEFFFFFFB
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
PTAT Driver Loaded:                  No

[06/28/24 21:23:09 UTC] PTAT started.

Press <Ctrl-C> to stop.


 Index Device Cor Thr CFreq UFreq  PState   Util  IPC     C0     C1     C6    PC2    PC6 MC Ch Sl  Temp DTS  Power  Volt UVolt TStat TLog #TL TMargin MCPMargin
     0   CPU0   -   -  2314  1600       0 100.00 6.81 100.00   0.00   0.00   0.00   0.00  -  -  -    72  19 194.96 0.756 0.733   0x0  0x0   0  10.141    10.141
     0   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.20     -     -     -  0x0   -       -         -
     1   CPU0   -   -  2322  1600       0 100.00 6.86 100.00   0.00   0.00   0.00   0.00  -  -  -    73  18 194.64 0.756 0.733   0x0  0x0   0   9.609     9.609
     1   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.24     -     -     -  0x0   -       -         -
     2   CPU0   -   -  2351  1600       0 100.00 6.87 100.00   0.00   0.00   0.00   0.00  -  -  -    73  18 194.82 0.756 0.733   0x0  0x0   0   9.938     9.938
     2   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.23     -     -     -  0x0   -       -         -
     3   CPU0   -   -  2337  1600       0 100.00 6.85 100.00   0.00   0.00   0.00   0.00  -  -  -    73  18 194.83 0.753 0.733   0x0  0x0   0  10.016    10.016
     3   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.16     -     -     -  0x0   -       -         -
     4   CPU0   -   -  2337  1600       0 100.00 6.83 100.00   0.00   0.00   0.00   0.00  -  -  -    74  17 194.78 0.753 0.733   0x0  0x0   0   9.594     9.594
     4   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.35     -     -     -  0x0   -       -         -
     5   CPU0   -   -  2334  1600       0 100.00 6.85 100.00   0.00   0.00   0.00   0.00  -  -  -    73  18 194.85 0.756 0.733   0x0  0x0   0   9.344     9.344
     5   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.25     -     -     -  0x0   -       -         -
     6   CPU0   -   -  2327  1600       0 100.00 6.86 100.00   0.00   0.00   0.00   0.00  -  -  -    73  18 194.93 0.753 0.733   0x0  0x0   0   9.516     9.516
     6   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.25     -     -     -  0x0   -       -         -
     7   CPU0   -   -  2327  1600       0 100.00 6.82 100.00   0.00   0.00   0.00   0.00  -  -  -    73  18 194.71 0.743 0.733   0x0  0x0   0   9.609     9.609
     7   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.29     -     -     -  0x0   -       -         -
     8   CPU0   -   -  2344  1600       0 100.00 6.81 100.00   0.00   0.00   0.00   0.00  -  -  -    74  17 194.76 0.766 0.733   0x0  0x0   0   9.578     9.578
     8   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.25     -     -     -  0x0   -       -         -
     9   CPU0   -   -  2325  1600       0 100.00 6.80 100.00   0.00   0.00   0.00   0.00  -  -  -    74  17 194.83 0.753 0.733   0x0  0x0   0   9.438     9.438
     9   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.40     -     -     -  0x0   -       -         -
    10   CPU0   -   -  2338  1600       0 100.00 6.81 100.00   0.00   0.00   0.00   0.00  -  -  -    74  17 194.81 0.766 0.733   0x0  0x0   0   8.984     8.984
    10   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.33     -     -     -  0x0   -       -         -
    11   CPU0   -   -  2341  1600       0 100.00 6.79 100.00   0.00   0.00   0.00   0.00  -  -  -    74  17 193.67 0.763 0.733   0x0  0x0   0   9.000     9.000
    11   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.28     -     -     -  0x0   -       -         -
    12   CPU0   -   -  2317  1600       0 100.00 6.78 100.00   0.00   0.00   0.00   0.00  -  -  -    75  16 195.87 0.753 0.733   0x0  0x0   0   8.938     8.938
    12   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.25     -     -     -  0x0   -       -         -
    13   CPU0   -   -  2326  1600       0 100.00 6.79 100.00   0.00   0.00   0.00   0.00  -  -  -    74  17 194.85 0.753 0.730   0x0  0x0   0   8.531     8.531
    13   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.19     -     -     -  0x0   -       -         -
    14   CPU0   -   -  2341  1600       0 100.00 6.84 100.00   0.00   0.00   0.00   0.00  -  -  -    75  16 194.83 0.763 0.733   0x0  0x0   0   8.500     8.500
    14   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.28     -     -     -  0x0   -       -         -
    15   CPU0   -   -  2335  1600       0 100.00 6.86 100.00   0.00   0.00   0.00   0.00  -  -  -    75  16 194.77 0.763 0.730   0x0  0x0   0   8.422     8.422
    15   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.27     -     -     -  0x0   -       -         -
    16   CPU0   -   -  2330  1600       0 100.00 6.81 100.00   0.00   0.00   0.00   0.00  -  -  -    75  16 194.77 0.753 0.730   0x0  0x0   0   7.922     7.922
    16   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.41     -     -     -  0x0   -       -         -
    17   CPU0   -   -  2316  1600       0 100.00 6.81 100.00   0.00   0.00   0.00   0.00  -  -  -    75  16 194.86 0.753 0.730   0x0  0x0   0   8.172     8.172
    17   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.41     -     -     -  0x0   -       -         -
    18   CPU0   -   -  2317  1600       0 100.00 6.84 100.00   0.00   0.00   0.00   0.00  -  -  -    75  16 194.76 0.753 0.730   0x0  0x0   0   8.000     8.000
    18   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.20     -     -     -  0x0   -       -         -
    19   CPU0   -   -  2324  1600       0 100.00 6.82 100.00   0.00   0.00   0.00   0.00  -  -  -    75  16 194.81 0.753 0.730   0x0  0x0   0   8.000     8.000
    19   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.30     -     -     -  0x0   -       -         -
    20   CPU0   -   -  2297  1600       0 100.00 6.82 100.00   0.00   0.00   0.00   0.00  -  -  -    76  15 195.01 0.753 0.730   0x0  0x0   0   7.516     7.516
    20   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.32     -     -     -  0x0   -       -         -
    21   CPU0   -   -  2295  1600       0 100.00 6.83 100.00   0.00   0.00   0.00   0.00  -  -  -    75  16 194.69 0.753 0.730   0x0  0x0   0   7.625     7.625
    21   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.31     -     -     -  0x0   -       -         -
    22   CPU0   -   -  2307  1600       0 100.00 6.84 100.00   0.00   0.00   0.00   0.00  -  -  -    75  16 194.91 0.753 0.730   0x0  0x0   0   7.625     7.625
    22   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.18     -     -     -  0x0   -       -         -
    23   CPU0   -   -  2303  1600       0 100.00 6.83 100.00   0.00   0.00   0.00   0.00  -  -  -    75  16 194.46 0.753 0.730   0x0  0x0   0   7.609     7.609
    23   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.20     -     -     -  0x0   -       -         -
    24   CPU0   -   -  2331  1600       0 100.00 6.84 100.00   0.00   0.00   0.00   0.00  -  -  -    75  16 193.78 0.753 0.730   0x0  0x0   0   7.656     7.656
    24   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.23     -     -     -  0x0   -       -         -
    25   CPU0   -   -  2313  1600       0 100.00 6.81 100.00   0.00   0.00   0.00   0.00  -  -  -    76  15 196.16 0.753 0.730   0x0  0x0   0   7.328     7.328
    25   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.29     -     -     -  0x0   -       -         -
    26   CPU0   -   -  2342  1600       0 100.00 6.86 100.00   0.00   0.00   0.00   0.00  -  -  -    76  15 194.78 0.763 0.730   0x0  0x0   0   7.391     7.391
    26   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.27     -     -     -  0x0   -       -         -
    27   CPU0   -   -  2311  1600       0 100.00 6.80 100.00   0.00   0.00   0.00   0.00  -  -  -    75  16 194.89 0.753 0.730   0x0  0x0   0   7.359     7.359
    27   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.31     -     -     -  0x0   -       -         -
    28   CPU0   -   -  2331  1600       0 100.00 6.84 100.00   0.00   0.00   0.00   0.00  -  -  -    76  15 194.77 0.721 0.730   0x0  0x0   0   7.438     7.438
    28   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.34     -     -     -  0x0   -       -         -
    29   CPU0   -   -  2334  1600       0 100.00 6.82 100.00   0.00   0.00   0.00   0.00  -  -  -    76  15 194.70 0.753 0.730   0x0  0x0   0   7.344     7.344
    29   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.49     -     -     -  0x0   -       -         -
    30   CPU0   -   -  2321  1600       0 100.00 6.83 100.00   0.00   0.00   0.00   0.00  -  -  -    76  15 195.10 0.743 0.730   0x0  0x0   0   7.078     7.078
    30   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.23     -     -     -  0x0   -       -         -
    31   CPU0   -   -  2331  1600       0 100.00 6.85 100.00   0.00   0.00   0.00   0.00  -  -  -    76  15 194.54 0.753 0.730   0x0  0x0   0   6.938     6.938
    31   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.22     -     -     -  0x0   -       -         -
    32   CPU0   -   -  2333  1600       0 100.00 6.84 100.00   0.00   0.00   0.00   0.00  -  -  -    77  14 194.92 0.763 0.730   0x0  0x0   0   7.062     7.062
    32   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.30     -     -     -  0x0   -       -         -
    33   CPU0   -   -  2333  1600       0 100.00 6.84 100.00   0.00   0.00   0.00   0.00  -  -  -    76  15 194.79 0.763 0.730   0x0  0x0   0   6.516     6.516
    33   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.34     -     -     -  0x0   -       -         -
    34   CPU0   -   -  2326  1600       0 100.00 6.85 100.00   0.00   0.00   0.00   0.00  -  -  -    77  14 194.81 0.753 0.730   0x0  0x0   0   6.859     6.859
    34   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.27     -     -     -  0x0   -       -         -
    35   CPU0   -   -  2325  1600       0 100.00 6.85 100.00   0.00   0.00   0.00   0.00  -  -  -    76  15 194.81 0.763 0.730   0x0  0x0   0   6.719     6.719
    35   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.25     -     -     -  0x0   -       -         -
    36   CPU0   -   -  2328  1600       0 100.00 6.85 100.00   0.00   0.00   0.00   0.00  -  -  -    76  15 194.91 0.753 0.730   0x0  0x0   0   6.656     6.656
    36   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.38     -     -     -  0x0   -       -         -
    37   CPU0   -   -  2337  1600       0 100.00 6.83 100.00   0.00   0.00   0.00   0.00  -  -  -    76  15 194.70 0.753 0.730   0x0  0x0   0   6.594     6.594
    37   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.40     -     -     -  0x0   -       -         -
    38   CPU0   -   -  2342  1600       0 100.00 6.83 100.00   0.00   0.00   0.00   0.00  -  -  -    77  14 194.84 0.751 0.730   0x0  0x0   0   6.625     6.625
    38   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.26     -     -     -  0x0   -       -         -
    39   CPU0   -   -  2334  1600       0 100.00 6.81 100.00   0.00   0.00   0.00   0.00  -  -  -    76  15 194.73 0.753 0.730   0x0  0x0   0   6.438     6.438
    39   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.35     -     -     -  0x0   -       -         -
    40   CPU0   -   -  2340  1600       0 100.00 6.84 100.00   0.00   0.00   0.00   0.00  -  -  -    76  15 194.92 0.763 0.730   0x0  0x0   0   6.391     6.391
    40   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.21     -     -     -  0x0   -       -         -
^C
[06/28/24 21:23:53 UTC] PTAT stopped.

root@controller-0:/home/XXXXXX/james#
```

## check sensors after load 

```log
root@controller-0:/home/XXXXXX/james# ipmitool sensor| grep -e CPU -e DutyCycle -e Watts
02-CPU 1 PkgTmp  | 80.000     | degrees C  | ok    | na        | na        | na        | na        | 91.000    | na
Fan 1 DutyCycle  | 32.928     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 2 DutyCycle  | 32.928     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 3 DutyCycle  | 32.928     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 4 DutyCycle  | 32.928     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 5 DutyCycle  | 32.928     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 6 DutyCycle  | 32.928     | percent    | ok    | na        | na        | na        | na        | na        | na
PS 1 Input       | 210.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PS 2 Input       | 2550.000   | Watts      | ok    | na        | na        | na        | na        | na        | na
Power Meter      | 240.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
CPU Utilization  | 223.000    | unspecified | ok    | na        | na        | na        | na        | na        | na
PS 1 Output      | 0.000      | Watts      | ok    | na        | na        | na        | na        | na        | na
PS 2 Output      | 0.000      | Watts      | ok    | na        | na        | na        | na        | na        | na
CPU_Stat_C1      | 0x0        | discrete   | 0x8080| na        | na        | na        | na        | na        | na
root@controller-0:/home/XXXXXX/james#
```

## Observed temps raise and fans rpm raise with load - success

## MEAKV-645
## PTU 4 - Core AVX512 with Turbo
## sudo ./ptat -ct 5 -cp 100 -b 1


## Sensors before load

```log
root@controller-0:/home/XXXXXX/james# ipmitool sensor| grep -e CPU -e DutyCycle -e Watts
02-CPU 1 PkgTmp  | 59.000     | degrees C  | ok    | na        | na        | na        | na        | 91.000    | na
Fan 1 DutyCycle  | 17.640     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 2 DutyCycle  | 17.640     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 3 DutyCycle  | 17.640     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 4 DutyCycle  | 17.640     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 5 DutyCycle  | 17.640     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 6 DutyCycle  | 17.640     | percent    | ok    | na        | na        | na        | na        | na        | na
PS 1 Input       | 150.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PS 2 Input       | 2550.000   | Watts      | ok    | na        | na        | na        | na        | na        | na
Power Meter      | 130.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
CPU Utilization  | 9.000      | unspecified | ok    | na        | na        | na        | na        | na        | na
PS 1 Output      | 0.000      | Watts      | ok    | na        | na        | na        | na        | na        | na
PS 2 Output      | 0.000      | Watts      | ok    | na        | na        | na        | na        | na        | na
CPU_Stat_C1      | 0x0        | discrete   | 0x8080| na        | na        | na        | na        | na        | na
root@controller-0:/home/XXXXXX/james#

```

## Initate load

```log
root@controller-0:/home/XXXXXX/james# ./ptat -ct 5 -cp 100 -b 1 -id

Command: ./ptat -ct 5 -cp 100 -b 1 -id

Intel(R) PTAT - Server Edition 4.4.0
Release Date: 12/19/2023
Copyright (C) 2023 Intel Corporation. All rights reserved.
Intel Confidential

insmod: ERROR: could not insert module driver/ptusys/ptusys.ko: Invalid module format
ptusys driver installation failed
/dev/ptusys: No such file or directory
insmod: ERROR: could not insert module driver/ptusys/ptusys.ko: Invalid module format
ptusys driver installation failed
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> System Info:                   <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Host Name:                           controller-0
Host IP:                             169.254.202.1
OS Name:                             Debian GNU/Linux 11 (bullseye) 11
Kernel Version:                      Linux 5.10.0-6-rt-amd64 #1 SMP PREEMPT_RT StarlingX Debian 5.10.177-1.stx.76 (2024-03-29
BIOS Version:                        HPE, 1.11, 03/07/2024
Processor(s):                        1 Processor(s) Installed.
DIMM(s):                             8 DIMM(s) Installed.
Total System Memory:                 255208 MB
Available System Memory:             180652 MB


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
CAPID6:                              0xEFFFFFFB
CAPID7:                              0x00000003
CAPID8:                              0xEFFFFFFB
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
PTAT Driver Loaded:                  No

[06/28/24 21:33:10 UTC] PTAT started.

Press <Ctrl-C> to stop.


CPU_0: [IDLE] CFreq=4783, UFreq=1600, PState=0, Util=0.65, IPC=1.35, Temp=59, DTS=32, Power=72.3, Volt=0.948, UVolt=0.740
MEM_0: [IDLE] Power=13.47, Temp=37, Read=0.0, Write=0.0
MEM_0: [TESTCFG] TestSel=1 (Read), CoreMask=0x1, ThreadMask=0x1, PwrLevel=100, Turbo=1
MEM_0: [RUNNING] Power=171.86, Temp=38, Read=981.6, Write=348.9
CPU_0: , CoreMask=0xFFFFFFFFFFFFFFFF, ThreadMask=0xFFFFFFFFFFFFFFFF, PwrLevel=100, Turbo=1
CPU_0: [RUNNING] CFreq=2214, UFreq=1600, PState=0, Util=100.00, IPC=6.86, Temp=73, DTS=18, Power=194.6, Volt=0.753, UVolt=0.733


```

## ptu -mon

```log

root@controller-0:/home/XXXXXX/james# ./ptat -mon -id

Command: ./ptat -mon -id

Intel(R) PTAT - Server Edition 4.4.0
Release Date: 12/19/2023
Copyright (C) 2023 Intel Corporation. All rights reserved.
Intel Confidential

insmod: ERROR: could not insert module driver/ptusys/ptusys.ko: Invalid module format
ptusys driver installation failed
/dev/ptusys: No such file or directory
insmod: ERROR: could not insert module driver/ptusys/ptusys.ko: Invalid module format
ptusys driver installation failed
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> System Info:                   <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Host Name:                           controller-0
Host IP:                             169.254.202.1
OS Name:                             Debian GNU/Linux 11 (bullseye) 11
Kernel Version:                      Linux 5.10.0-6-rt-amd64 #1 SMP PREEMPT_RT StarlingX Debian 5.10.177-1.stx.76 (2024-03-29
BIOS Version:                        HPE, 1.11, 03/07/2024
Processor(s):                        1 Processor(s) Installed.
DIMM(s):                             8 DIMM(s) Installed.
Total System Memory:                 255208 MB
Available System Memory:             180416 MB


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
CAPID6:                              0xEFFFFFFB
CAPID7:                              0x00000003
CAPID8:                              0xEFFFFFFB
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
PTAT Driver Loaded:                  No

[06/28/24 21:34:14 UTC] PTAT started.

Press <Ctrl-C> to stop.


 Index Device Cor Thr CFreq UFreq  PState   Util  IPC     C0     C1     C6    PC2    PC6 MC Ch Sl  Temp DTS  Power  Volt UVolt TStat TLog #TL TMargin MCPMargin
     0   CPU0   -   -  2197  1600       0 100.00 6.87 100.00   0.00   0.00   0.00   0.00  -  -  -    74  17 194.79 0.743 0.733   0x0  0x0   0   8.938     8.938
     0   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.17     -     -     -  0x0   -       -         -
     1   CPU0   -   -  2214  1600       0 100.00 6.88 100.00   0.00   0.00   0.00   0.00  -  -  -    74  17 194.77 0.743 0.733   0x0  0x0   0   8.891     8.891
     1   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.11     -     -     -  0x0   -       -         -
     2   CPU0   -   -  2206  1600       0 100.00 6.87 100.00   0.00   0.00   0.00   0.00  -  -  -    74  17 194.88 0.743 0.733   0x0  0x0   0   8.734     8.734
     2   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.15     -     -     -  0x0   -       -         -
     3   CPU0   -   -  2214  1600       0 100.00 6.85 100.00   0.00   0.00   0.00   0.00  -  -  -    74  17 194.77 0.743 0.733   0x0  0x0   0   8.453     8.453
     3   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.14     -     -     -  0x0   -       -         -
     4   CPU0   -   -  2211  1600       0 100.00 6.87 100.00   0.00   0.00   0.00   0.00  -  -  -    75  16 194.73 0.743 0.733   0x0  0x0   0   8.141     8.141
     4   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.26     -     -     -  0x0   -       -         -
     5   CPU0   -   -  2214  1600       0 100.00 6.88 100.00   0.00   0.00   0.00   0.00  -  -  -    75  16 194.86 0.743 0.733   0x0  0x0   0   8.328     8.328
     5   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.08     -     -     -  0x0   -       -         -
     6   CPU0   -   -  2214  1600       0 100.00 6.87 100.00   0.00   0.00   0.00   0.00  -  -  -    75  16 194.66 0.743 0.733   0x0  0x0   0   8.438     8.438
     6   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.20     -     -     -  0x0   -       -         -
     7   CPU0   -   -  2212  1600       0 100.00 6.88 100.00   0.00   0.00   0.00   0.00  -  -  -    75  16 194.92 0.743 0.733   0x0  0x0   0   8.156     8.156
     7   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.25     -     -     -  0x0   -       -         -
     8   CPU0   -   -  2209  1600       0 100.00 6.88 100.00   0.00   0.00   0.00   0.00  -  -  -    76  15 194.66 0.743 0.733   0x0  0x0   0   8.062     8.062
     8   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.20     -     -     -  0x0   -       -         -
     9   CPU0   -   -  2215  1600       0 100.00 6.88 100.00   0.00   0.00   0.00   0.00  -  -  -    75  16 194.82 0.743 0.730   0x0  0x0   0   7.891     7.891
     9   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.19     -     -     -  0x0   -       -         -
    10   CPU0   -   -  2212  1600       0 100.00 6.90 100.00   0.00   0.00   0.00   0.00  -  -  -    75  16 194.82 0.743 0.730   0x0  0x0   0   7.812     7.812
    10   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.10     -     -     -  0x0   -       -         -
    11   CPU0   -   -  2213  1600       0 100.00 6.87 100.00   0.00   0.00   0.00   0.00  -  -  -    75  16 194.74 0.743 0.730   0x0  0x0   0   7.734     7.734
    11   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.18     -     -     -  0x0   -       -         -
    12   CPU0   -   -  2215  1600       0 100.00 6.86 100.00   0.00   0.00   0.00   0.00  -  -  -    76  15 194.92 0.743 0.730   0x0  0x0   0   7.375     7.375
    12   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.20     -     -     -  0x0   -       -         -
    13   CPU0   -   -  2214  1600       0 100.00 6.86 100.00   0.00   0.00   0.00   0.00  -  -  -    75  16 194.75 0.743 0.730   0x0  0x0   0   6.859     6.859
    13   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.12     -     -     -  0x0   -       -         -
    14   CPU0   -   -  2213  1600       0 100.00 6.81 100.00   0.00   0.00   0.00   0.00  -  -  -    76  15 194.85 0.743 0.730   0x0  0x0   0   7.406     7.406
    14   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.36     -     -     -  0x0   -       -         -
    15   CPU0   -   -  2214  1600       0 100.00 6.83 100.00   0.00   0.00   0.00   0.00  -  -  -    76  15 194.64 0.753 0.730   0x0  0x0   0   7.125     7.125
    15   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.35     -     -     -  0x0   -       -         -
    16   CPU0   -   -  2212  1600       0 100.00 6.84 100.00   0.00   0.00   0.00   0.00  -  -  -    77  14 194.76 0.741 0.730   0x0  0x0   0   6.781     6.781
    16   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.17     -     -     -  0x0   -       -         -
    17   CPU0   -   -  2212  1600       0 100.00 6.85 100.00   0.00   0.00   0.00   0.00  -  -  -    76  15 194.74 0.753 0.730   0x0  0x0   0   6.938     6.938
    17   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.16     -     -     -  0x0   -       -         -
    18   CPU0   -   -  2213  1600       0 100.00 6.84 100.00   0.00   0.00   0.00   0.00  -  -  -    77  14 194.87 0.741 0.730   0x0  0x0   0   6.953     6.953
    18   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.03     -     -     -  0x0   -       -         -
    19   CPU0   -   -  2212  1600       0 100.00 6.78 100.00   0.00   0.00   0.00   0.00  -  -  -    76  15 194.84 0.741 0.730   0x0  0x0   0   6.625     6.625
    19   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.36     -     -     -  0x0   -       -         -
    20   CPU0   -   -  2215  1600       0 100.00 6.78 100.00   0.00   0.00   0.00   0.00  -  -  -    76  15 194.82 0.741 0.730   0x0  0x0   0   6.406     6.406
    20   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.24     -     -     -  0x0   -       -         -
    21   CPU0   -   -  2211  1600       0 100.00 6.78 100.00   0.00   0.00   0.00   0.00  -  -  -    77  14 194.73 0.741 0.730   0x0  0x0   0   6.391     6.391
    21   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.35     -     -     -  0x0   -       -         -
    22   CPU0   -   -  2211  1600       0 100.00 6.82 100.00   0.00   0.00   0.00   0.00  -  -  -    77  14 194.82 0.741 0.730   0x0  0x0   0   6.062     6.062
    22   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.16     -     -     -  0x0   -       -         -
    23   CPU0   -   -  2211  1600       0 100.00 6.84 100.00   0.00   0.00   0.00   0.00  -  -  -    76  15 194.89 0.741 0.730   0x0  0x0   0   6.172     6.172
    23   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.06     -     -     -  0x0   -       -         -
    24   CPU0   -   -  2208  1600       0 100.00 6.85 100.00   0.00   0.00   0.00   0.00  -  -  -    77  14 194.63 0.741 0.730   0x0  0x0   0   5.938     5.938
    24   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.27     -     -     -  0x0   -       -         -
    25   CPU0   -   -  2209  1600       0 100.00 6.83 100.00   0.00   0.00   0.00   0.00  -  -  -    77  14 194.77 0.741 0.730   0x0  0x0   0   6.141     6.141
    25   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.34     -     -     -  0x0   -       -         -
    26   CPU0   -   -  2206  1600       0 100.00 6.84 100.00   0.00   0.00   0.00   0.00  -  -  -    77  14 194.88 0.741 0.730   0x0  0x0   0   5.828     5.828
    26   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.30     -     -     -  0x0   -       -         -
    27   CPU0   -   -  2210  1600       0 100.00 6.83 100.00   0.00   0.00   0.00   0.00  -  -  -    77  14 194.88 0.741 0.730   0x0  0x0   0   5.594     5.594
    27   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.26     -     -     -  0x0   -       -         -
    28   CPU0   -   -  2209  1600       0 100.00 6.88 100.00   0.00   0.00   0.00   0.00  -  -  -    77  14 194.70 0.681 0.730   0x0  0x0   0   5.859     5.859
    28   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.13     -     -     -  0x0   -       -         -
    29   CPU0   -   -  2205  1600       0 100.00 6.87 100.00   0.00   0.00   0.00   0.00  -  -  -    77  14 194.83 0.741 0.730   0x0  0x0   0   5.469     5.469
    29   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.21     -     -     -  0x0   -       -         -
    30   CPU0   -   -  2208  1600       0 100.00 6.88 100.00   0.00   0.00   0.00   0.00  -  -  -    77  14 194.84 0.741 0.730   0x0  0x0   0   5.422     5.422
    30   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.17     -     -     -  0x0   -       -         -
    31   CPU0   -   -  2207  1600       0 100.00 6.86 100.00   0.00   0.00   0.00   0.00  -  -  -    78  13 194.82 0.741 0.728   0x0  0x0   0   5.359     5.359
    31   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.31     -     -     -  0x0   -       -         -
    32   CPU0   -   -  2210  1600       0 100.00 6.85 100.00   0.00   0.00   0.00   0.00  -  -  -    78  13 194.63 0.741 0.728   0x0  0x0   0   5.359     5.359
    32   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.26     -     -     -  0x0   -       -         -
    33   CPU0   -   -  2209  1600       0 100.00 6.86 100.00   0.00   0.00   0.00   0.00  -  -  -    77  14 194.94 0.751 0.728   0x0  0x0   0   5.453     5.453
    33   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.30     -     -     -  0x0   -       -         -
    34   CPU0   -   -  2205  1600       0 100.00 6.87 100.00   0.00   0.00   0.00   0.00  -  -  -    78  13 194.83 0.741 0.730   0x0  0x0   0   5.391     5.391
    34   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.22     -     -     -  0x0   -       -         -
    35   CPU0   -   -  2205  1600       0 100.00 6.88 100.00   0.00   0.00   0.00   0.00  -  -  -    78  13 194.78 0.741 0.730   0x0  0x0   0   5.234     5.234
    35   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.16     -     -     -  0x0   -       -         -
^C
[06/28/24 21:34:53 UTC] PTAT stopped.

root@controller-0:/home/XXXXXX/james#


```

## check sensors

```log
root@controller-0:/home/XXXXXX/james# ipmitool sensor| grep -e CPU -e DutyCycle -e Watts
02-CPU 1 PkgTmp  | 79.000     | degrees C  | ok    | na        | na        | na        | na        | 91.000    | na
Fan 1 DutyCycle  | 35.672     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 2 DutyCycle  | 35.672     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 3 DutyCycle  | 35.672     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 4 DutyCycle  | 35.672     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 5 DutyCycle  | 35.672     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 6 DutyCycle  | 35.672     | percent    | ok    | na        | na        | na        | na        | na        | na
PS 1 Input       | 220.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PS 2 Input       | 2550.000   | Watts      | ok    | na        | na        | na        | na        | na        | na
Power Meter      | 240.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
CPU Utilization  | 217.000    | unspecified | ok    | na        | na        | na        | na        | na        | na
PS 1 Output      | 0.000      | Watts      | ok    | na        | na        | na        | na        | na        | na
PS 2 Output      | 0.000      | Watts      | ok    | na        | na        | na        | na        | na        | na
CPU_Stat_C1      | 0x0        | discrete   | 0x8080| na        | na        | na        | na        | na        | na
root@controller-0:/home/XXXXXX/james#
```

## Success, was able to observe temp rise, then fans increasing as load was started


## MEAKV-646 
## PTU 5 - Turbo Test
## sudo ./ptat -ct 8 -b 1

## sensors before load

```log
root@controller-0:/home/XXXXXX/james# ipmitool sensor| grep -e CPU -e DutyCycle -e Watts
02-CPU 1 PkgTmp  | 60.000     | degrees C  | ok    | na        | na        | na        | na        | 91.000    | na
Fan 1 DutyCycle  | 14.896     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 2 DutyCycle  | 14.896     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 3 DutyCycle  | 14.896     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 4 DutyCycle  | 14.896     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 5 DutyCycle  | 14.896     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 6 DutyCycle  | 14.896     | percent    | ok    | na        | na        | na        | na        | na        | na
PS 1 Input       | 140.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PS 2 Input       | 2550.000   | Watts      | ok    | na        | na        | na        | na        | na        | na
Power Meter      | 130.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
CPU Utilization  | 7.000      | unspecified | ok    | na        | na        | na        | na        | na        | na
PS 1 Output      | 0.000      | Watts      | ok    | na        | na        | na        | na        | na        | na
PS 2 Output      | 0.000      | Watts      | ok    | na        | na        | na        | na        | na        | na
CPU_Stat_C1      | 0x0        | discrete   | 0x8080| na        | na        | na        | na        | na        | na
root@controller-0:/home/XXXXXX/james#
```

## Initiating load

```log

root@controller-0:/home/XXXXXX/james# ./ptat -ct 8 -b 1 -id

Command: ./ptat -ct 8 -b 1 -id

Intel(R) PTAT - Server Edition 4.4.0
Release Date: 12/19/2023
Copyright (C) 2023 Intel Corporation. All rights reserved.
Intel Confidential

insmod: ERROR: could not insert module driver/ptusys/ptusys.ko: Invalid module format
ptusys driver installation failed
/dev/ptusys: No such file or directory
insmod: ERROR: could not insert module driver/ptusys/ptusys.ko: Invalid module format
ptusys driver installation failed
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> System Info:                   <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Host Name:                           controller-0
Host IP:                             169.254.202.1
OS Name:                             Debian GNU/Linux 11 (bullseye) 11
Kernel Version:                      Linux 5.10.0-6-rt-amd64 #1 SMP PREEMPT_RT StarlingX Debian 5.10.177-1.stx.76 (2024-03-29
BIOS Version:                        HPE, 1.11, 03/07/2024
Processor(s):                        1 Processor(s) Installed.
DIMM(s):                             8 DIMM(s) Installed.
Total System Memory:                 255208 MB
Available System Memory:             180602 MB


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
CAPID6:                              0xEFFFFFFB
CAPID7:                              0x00000003
CAPID8:                              0xEFFFFFFB
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
PTAT Driver Loaded:                  No

[06/28/24 21:41:01 UTC] PTAT started.

Press <Ctrl-C> to stop.


CPU_0: [IDLE] CFreq=3485, UFreq=1600, PState=0, Util=1.82, IPC=2.39, Temp=59, DTS=32, Power=76.9, Volt=0.948, UVolt=0.738

### TURBO is enabled ###

Instr   CPU #Cores CFreq(act) CFreq(exp) UFreq Power TDP  Temp Volt
IA/SSE  0   1      3.6        3.6        1.6   77.6  195  62   0.951
IA/SSE  0   2      3.6        3.6        1.6   79.8  195  65   0.951
IA/SSE  0   3      3.6        3.6        1.6   84.8  195  65   0.948
IA/SSE  0   4      3.6        3.6        1.6   88.3  195  66   0.946
IA/SSE  0   5      3.6        3.6        1.6   93.7  195  66   0.946
IA/SSE  0   6      3.6        3.6        1.6   99.4  195  70   0.945
IA/SSE  0   7      3.6        3.6        1.6   104.1 195  69   0.946
IA/SSE  0   8      3.6        3.6        1.6   106.2 195  70   0.945
IA/SSE  0   9      3.6        3.6        1.6   111.8 195  71   0.944
IA/SSE  0   10     3.6        3.6        1.6   116.0 195  72   0.945
IA/SSE  0   11     3.6        3.6        1.6   120.5 195  74   0.944
IA/SSE  0   12     3.6        3.6        1.6   126.9 195  74   0.944
IA/SSE  0   13     3.6        3.6        1.6   132.3 195  78   0.944
IA/SSE  0   14     3.6        3.6        1.6   137.5 195  75   0.944
IA/SSE  0   15     3.6        3.6        1.6   139.9 195  76   0.936
IA/SSE  0   16     3.5        3.6        1.6   142.7 195  77   0.944
IA/SSE  0   17     3.3        3.3        1.6   138.0 195  76   0.898
IA/SSE  0   18     3.3        3.3        1.6   141.3 195  76   0.897
IA/SSE  0   19     3.3        3.3        1.6   143.7 195  77   0.897
IA/SSE  0   20     3.2        3.3        1.6   146.8 195  78   0.850
IA/SSE  0   21     3.0        3.0        1.6   143.8 195  77   0.850
IA/SSE  0   22     3.0        3.0        1.6   144.4 195  79   0.849
IA/SSE  0   23     3.0        3.0        1.6   146.6 195  79   0.839
IA/SSE  0   24     3.0        3.0        1.6   150.5 195  79   0.848
IA/SSE  0   25     2.9        2.9        1.6   148.4 195  80   0.832
IA/SSE  0   26     2.9        2.9        1.6   149.7 195  81   0.800
IA/SSE  0   27     2.7        2.7        1.6   139.6 195  80   0.800
IA/SSE  0   28     2.7        2.7        1.6   143.6 195  80   0.800
IA/SSE  0   29     2.7        2.7        1.6   145.4 195  81   0.799
IA/SSE  0   30     2.7        2.7        1.6   147.8 195  81   0.799
IA/SSE  0   31     2.7        2.7        1.6   150.2 195  82   0.799
IA/SSE  0   32     2.7        2.7        1.6   152.6 195  82   0.799





```

## ptu -mon

```log
root@controller-0:/home/XXXXXX/james# ./ptat -mon -id

Command: ./ptat -mon -id

Intel(R) PTAT - Server Edition 4.4.0
Release Date: 12/19/2023
Copyright (C) 2023 Intel Corporation. All rights reserved.
Intel Confidential

insmod: ERROR: could not insert module driver/ptusys/ptusys.ko: Invalid module format
ptusys driver installation failed
/dev/ptusys: No such file or directory
insmod: ERROR: could not insert module driver/ptusys/ptusys.ko: Invalid module format
ptusys driver installation failed
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> System Info:                   <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Host Name:                           controller-0
Host IP:                             169.254.202.1
OS Name:                             Debian GNU/Linux 11 (bullseye) 11
Kernel Version:                      Linux 5.10.0-6-rt-amd64 #1 SMP PREEMPT_RT StarlingX Debian 5.10.177-1.stx.76 (2024-03-29
BIOS Version:                        HPE, 1.11, 03/07/2024
Processor(s):                        1 Processor(s) Installed.
DIMM(s):                             8 DIMM(s) Installed.
Total System Memory:                 255208 MB
Available System Memory:             180416 MB


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
CAPID6:                              0xEFFFFFFB
CAPID7:                              0x00000003
CAPID8:                              0xEFFFFFFB
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
PTAT Driver Loaded:                  No

[06/28/24 21:34:14 UTC] PTAT started.

Press <Ctrl-C> to stop.


 Index Device Cor Thr CFreq UFreq  PState   Util  IPC     C0     C1     C6    PC2    PC6 MC Ch Sl  Temp DTS  Power  Volt UVolt TStat TLog #TL TMargin MCPMargin
     0   CPU0   -   -  2197  1600       0 100.00 6.87 100.00   0.00   0.00   0.00   0.00  -  -  -    74  17 194.79 0.743 0.733   0x0  0x0   0   8.938     8.938
     0   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.17     -     -     -  0x0   -       -         -
     1   CPU0   -   -  2214  1600       0 100.00 6.88 100.00   0.00   0.00   0.00   0.00  -  -  -    74  17 194.77 0.743 0.733   0x0  0x0   0   8.891     8.891
     1   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.11     -     -     -  0x0   -       -         -
     2   CPU0   -   -  2206  1600       0 100.00 6.87 100.00   0.00   0.00   0.00   0.00  -  -  -    74  17 194.88 0.743 0.733   0x0  0x0   0   8.734     8.734
     2   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.15     -     -     -  0x0   -       -         -
     3   CPU0   -   -  2214  1600       0 100.00 6.85 100.00   0.00   0.00   0.00   0.00  -  -  -    74  17 194.77 0.743 0.733   0x0  0x0   0   8.453     8.453
     3   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.14     -     -     -  0x0   -       -         -
     4   CPU0   -   -  2211  1600       0 100.00 6.87 100.00   0.00   0.00   0.00   0.00  -  -  -    75  16 194.73 0.743 0.733   0x0  0x0   0   8.141     8.141
     4   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.26     -     -     -  0x0   -       -         -
     5   CPU0   -   -  2214  1600       0 100.00 6.88 100.00   0.00   0.00   0.00   0.00  -  -  -    75  16 194.86 0.743 0.733   0x0  0x0   0   8.328     8.328
     5   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.08     -     -     -  0x0   -       -         -
     6   CPU0   -   -  2214  1600       0 100.00 6.87 100.00   0.00   0.00   0.00   0.00  -  -  -    75  16 194.66 0.743 0.733   0x0  0x0   0   8.438     8.438
     6   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.20     -     -     -  0x0   -       -         -
     7   CPU0   -   -  2212  1600       0 100.00 6.88 100.00   0.00   0.00   0.00   0.00  -  -  -    75  16 194.92 0.743 0.733   0x0  0x0   0   8.156     8.156
     7   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.25     -     -     -  0x0   -       -         -
     8   CPU0   -   -  2209  1600       0 100.00 6.88 100.00   0.00   0.00   0.00   0.00  -  -  -    76  15 194.66 0.743 0.733   0x0  0x0   0   8.062     8.062
     8   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.20     -     -     -  0x0   -       -         -
     9   CPU0   -   -  2215  1600       0 100.00 6.88 100.00   0.00   0.00   0.00   0.00  -  -  -    75  16 194.82 0.743 0.730   0x0  0x0   0   7.891     7.891
     9   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.19     -     -     -  0x0   -       -         -
    10   CPU0   -   -  2212  1600       0 100.00 6.90 100.00   0.00   0.00   0.00   0.00  -  -  -    75  16 194.82 0.743 0.730   0x0  0x0   0   7.812     7.812
    10   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.10     -     -     -  0x0   -       -         -
    11   CPU0   -   -  2213  1600       0 100.00 6.87 100.00   0.00   0.00   0.00   0.00  -  -  -    75  16 194.74 0.743 0.730   0x0  0x0   0   7.734     7.734
    11   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.18     -     -     -  0x0   -       -         -
    12   CPU0   -   -  2215  1600       0 100.00 6.86 100.00   0.00   0.00   0.00   0.00  -  -  -    76  15 194.92 0.743 0.730   0x0  0x0   0   7.375     7.375
    12   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.20     -     -     -  0x0   -       -         -
    13   CPU0   -   -  2214  1600       0 100.00 6.86 100.00   0.00   0.00   0.00   0.00  -  -  -    75  16 194.75 0.743 0.730   0x0  0x0   0   6.859     6.859
    13   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.12     -     -     -  0x0   -       -         -
    14   CPU0   -   -  2213  1600       0 100.00 6.81 100.00   0.00   0.00   0.00   0.00  -  -  -    76  15 194.85 0.743 0.730   0x0  0x0   0   7.406     7.406
    14   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.36     -     -     -  0x0   -       -         -
    15   CPU0   -   -  2214  1600       0 100.00 6.83 100.00   0.00   0.00   0.00   0.00  -  -  -    76  15 194.64 0.753 0.730   0x0  0x0   0   7.125     7.125
    15   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.35     -     -     -  0x0   -       -         -
    16   CPU0   -   -  2212  1600       0 100.00 6.84 100.00   0.00   0.00   0.00   0.00  -  -  -    77  14 194.76 0.741 0.730   0x0  0x0   0   6.781     6.781
    16   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.17     -     -     -  0x0   -       -         -
    17   CPU0   -   -  2212  1600       0 100.00 6.85 100.00   0.00   0.00   0.00   0.00  -  -  -    76  15 194.74 0.753 0.730   0x0  0x0   0   6.938     6.938
    17   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.16     -     -     -  0x0   -       -         -
    18   CPU0   -   -  2213  1600       0 100.00 6.84 100.00   0.00   0.00   0.00   0.00  -  -  -    77  14 194.87 0.741 0.730   0x0  0x0   0   6.953     6.953
    18   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.03     -     -     -  0x0   -       -         -
    19   CPU0   -   -  2212  1600       0 100.00 6.78 100.00   0.00   0.00   0.00   0.00  -  -  -    76  15 194.84 0.741 0.730   0x0  0x0   0   6.625     6.625
    19   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.36     -     -     -  0x0   -       -         -
    20   CPU0   -   -  2215  1600       0 100.00 6.78 100.00   0.00   0.00   0.00   0.00  -  -  -    76  15 194.82 0.741 0.730   0x0  0x0   0   6.406     6.406
    20   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.24     -     -     -  0x0   -       -         -
    21   CPU0   -   -  2211  1600       0 100.00 6.78 100.00   0.00   0.00   0.00   0.00  -  -  -    77  14 194.73 0.741 0.730   0x0  0x0   0   6.391     6.391
    21   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.35     -     -     -  0x0   -       -         -
    22   CPU0   -   -  2211  1600       0 100.00 6.82 100.00   0.00   0.00   0.00   0.00  -  -  -    77  14 194.82 0.741 0.730   0x0  0x0   0   6.062     6.062
    22   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.16     -     -     -  0x0   -       -         -
    23   CPU0   -   -  2211  1600       0 100.00 6.84 100.00   0.00   0.00   0.00   0.00  -  -  -    76  15 194.89 0.741 0.730   0x0  0x0   0   6.172     6.172
    23   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.06     -     -     -  0x0   -       -         -
    24   CPU0   -   -  2208  1600       0 100.00 6.85 100.00   0.00   0.00   0.00   0.00  -  -  -    77  14 194.63 0.741 0.730   0x0  0x0   0   5.938     5.938
    24   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.27     -     -     -  0x0   -       -         -
    25   CPU0   -   -  2209  1600       0 100.00 6.83 100.00   0.00   0.00   0.00   0.00  -  -  -    77  14 194.77 0.741 0.730   0x0  0x0   0   6.141     6.141
    25   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.34     -     -     -  0x0   -       -         -
    26   CPU0   -   -  2206  1600       0 100.00 6.84 100.00   0.00   0.00   0.00   0.00  -  -  -    77  14 194.88 0.741 0.730   0x0  0x0   0   5.828     5.828
    26   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.30     -     -     -  0x0   -       -         -
    27   CPU0   -   -  2210  1600       0 100.00 6.83 100.00   0.00   0.00   0.00   0.00  -  -  -    77  14 194.88 0.741 0.730   0x0  0x0   0   5.594     5.594
    27   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.26     -     -     -  0x0   -       -         -
    28   CPU0   -   -  2209  1600       0 100.00 6.88 100.00   0.00   0.00   0.00   0.00  -  -  -    77  14 194.70 0.681 0.730   0x0  0x0   0   5.859     5.859
    28   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.13     -     -     -  0x0   -       -         -
    29   CPU0   -   -  2205  1600       0 100.00 6.87 100.00   0.00   0.00   0.00   0.00  -  -  -    77  14 194.83 0.741 0.730   0x0  0x0   0   5.469     5.469
    29   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.21     -     -     -  0x0   -       -         -
    30   CPU0   -   -  2208  1600       0 100.00 6.88 100.00   0.00   0.00   0.00   0.00  -  -  -    77  14 194.84 0.741 0.730   0x0  0x0   0   5.422     5.422
    30   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.17     -     -     -  0x0   -       -         -
    31   CPU0   -   -  2207  1600       0 100.00 6.86 100.00   0.00   0.00   0.00   0.00  -  -  -    78  13 194.82 0.741 0.728   0x0  0x0   0   5.359     5.359
    31   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.31     -     -     -  0x0   -       -         -
    32   CPU0   -   -  2210  1600       0 100.00 6.85 100.00   0.00   0.00   0.00   0.00  -  -  -    78  13 194.63 0.741 0.728   0x0  0x0   0   5.359     5.359
    32   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.26     -     -     -  0x0   -       -         -
    33   CPU0   -   -  2209  1600       0 100.00 6.86 100.00   0.00   0.00   0.00   0.00  -  -  -    77  14 194.94 0.751 0.728   0x0  0x0   0   5.453     5.453
    33   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.30     -     -     -  0x0   -       -         -
    34   CPU0   -   -  2205  1600       0 100.00 6.87 100.00   0.00   0.00   0.00   0.00  -  -  -    78  13 194.83 0.741 0.730   0x0  0x0   0   5.391     5.391
    34   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.22     -     -     -  0x0   -       -         -
    35   CPU0   -   -  2205  1600       0 100.00 6.88 100.00   0.00   0.00   0.00   0.00  -  -  -    78  13 194.78 0.741 0.730   0x0  0x0   0   5.234     5.234
    35   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -  13.16     -     -     -  0x0   -       -         -
^C
[06/28/24 21:34:53 UTC] PTAT stopped.

root@controller-0:/home/XXXXXX/james# ipmitool sensor| grep -e CPU -e DutyCycle -e Watts
02-CPU 1 PkgTmp  | 79.000     | degrees C  | ok    | na        | na        | na        | na        | 91.000    | na
Fan 1 DutyCycle  | 35.672     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 2 DutyCycle  | 35.672     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 3 DutyCycle  | 35.672     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 4 DutyCycle  | 35.672     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 5 DutyCycle  | 35.672     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 6 DutyCycle  | 35.672     | percent    | ok    | na        | na        | na        | na        | na        | na
PS 1 Input       | 220.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PS 2 Input       | 2550.000   | Watts      | ok    | na        | na        | na        | na        | na        | na
Power Meter      | 240.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
CPU Utilization  | 217.000    | unspecified | ok    | na        | na        | na        | na        | na        | na
PS 1 Output      | 0.000      | Watts      | ok    | na        | na        | na        | na        | na        | na
PS 2 Output      | 0.000      | Watts      | ok    | na        | na        | na        | na        | na        | na
CPU_Stat_C1      | 0x0        | discrete   | 0x8080| na        | na        | na        | na        | na        | na
root@controller-0:/home/XXXXXX/james# sleep 120 ; ipmitool sensor| grep -e CPU -e DutyCycle -e Watts




02-CPU 1 PkgTmp  | 61.000     | degrees C  | ok    | na        | na        | na        | na        | 91.000    | na
Fan 1 DutyCycle  | 14.896     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 2 DutyCycle  | 14.896     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 3 DutyCycle  | 14.896     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 4 DutyCycle  | 14.896     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 5 DutyCycle  | 20.776     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 6 DutyCycle  | 20.776     | percent    | ok    | na        | na        | na        | na        | na        | na
PS 1 Input       | 150.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PS 2 Input       | 2550.000   | Watts      | ok    | na        | na        | na        | na        | na        | na
Power Meter      | 130.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
CPU Utilization  | 11.000     | unspecified | ok    | na        | na        | na        | na        | na        | na
PS 1 Output      | 0.000      | Watts      | ok    | na        | na        | na        | na        | na        | na
PS 2 Output      | 0.000      | Watts      | ok    | na        | na        | na        | na        | na        | na
CPU_Stat_C1      | 0x0        | discrete   | 0x8080| na        | na        | na        | na        | na        | na
root@controller-0:/home/XXXXXX/james#
root@controller-0:/home/XXXXXX/james#
root@controller-0:/home/XXXXXX/james#
root@controller-0:/home/XXXXXX/james#
root@controller-0:/home/XXXXXX/james# ipmitool sensor| grep -e CPU -e DutyCycle -e Watts
02-CPU 1 PkgTmp  | 59.000     | degrees C  | ok    | na        | na        | na        | na        | 91.000    | na
Fan 1 DutyCycle  | 20.776     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 2 DutyCycle  | 20.776     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 3 DutyCycle  | 20.776     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 4 DutyCycle  | 20.776     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 5 DutyCycle  | 20.776     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 6 DutyCycle  | 20.776     | percent    | ok    | na        | na        | na        | na        | na        | na
PS 1 Input       | 150.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PS 2 Input       | 2550.000   | Watts      | ok    | na        | na        | na        | na        | na        | na
Power Meter      | 130.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
CPU Utilization  | 6.000      | unspecified | ok    | na        | na        | na        | na        | na        | na
PS 1 Output      | 0.000      | Watts      | ok    | na        | na        | na        | na        | na        | na
PS 2 Output      | 0.000      | Watts      | ok    | na        | na        | na        | na        | na        | na
CPU_Stat_C1      | 0x0        | discrete   | 0x8080| na        | na        | na        | na        | na        | na
root@controller-0:/home/XXXXXX/james# ipmitool sensor| grep -e CPU -e DutyCycle -e Watts
02-CPU 1 PkgTmp  | 60.000     | degrees C  | ok    | na        | na        | na        | na        | 91.000    | na
Fan 1 DutyCycle  | 14.896     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 2 DutyCycle  | 14.896     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 3 DutyCycle  | 14.896     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 4 DutyCycle  | 14.896     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 5 DutyCycle  | 14.896     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 6 DutyCycle  | 14.896     | percent    | ok    | na        | na        | na        | na        | na        | na
PS 1 Input       | 140.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PS 2 Input       | 2550.000   | Watts      | ok    | na        | na        | na        | na        | na        | na
Power Meter      | 130.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
CPU Utilization  | 7.000      | unspecified | ok    | na        | na        | na        | na        | na        | na
PS 1 Output      | 0.000      | Watts      | ok    | na        | na        | na        | na        | na        | na
PS 2 Output      | 0.000      | Watts      | ok    | na        | na        | na        | na        | na        | na
CPU_Stat_C1      | 0x0        | discrete   | 0x8080| na        | na        | na        | na        | na        | na
root@controller-0:/home/XXXXXX/james# ipmitool sensor| grep -e CPU -e DutyCycle -e Watts
02-CPU 1 PkgTmp  | 76.000     | degrees C  | ok    | na        | na        | na        | na        | 91.000    | na
Fan 1 DutyCycle  | 22.736     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 2 DutyCycle  | 22.736     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 3 DutyCycle  | 22.736     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 4 DutyCycle  | 22.736     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 5 DutyCycle  | 22.736     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 6 DutyCycle  | 22.736     | percent    | ok    | na        | na        | na        | na        | na        | na
PS 1 Input       | 150.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PS 2 Input       | 2550.000   | Watts      | ok    | na        | na        | na        | na        | na        | na
Power Meter      | 200.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
CPU Utilization  | 73.000     | unspecified | ok    | na        | na        | na        | na        | na        | na
PS 1 Output      | 0.000      | Watts      | ok    | na        | na        | na        | na        | na        | na
PS 2 Output      | 0.000      | Watts      | ok    | na        | na        | na        | na        | na        | na
CPU_Stat_C1      | 0x0        | discrete   | 0x8080| na        | na        | na        | na        | na        | na
root@controller-0:/home/XXXXXX/james# ./ptat -mon -id

Command: ./ptat -mon -id

Intel(R) PTAT - Server Edition 4.4.0
Release Date: 12/19/2023
Copyright (C) 2023 Intel Corporation. All rights reserved.
Intel Confidential

insmod: ERROR: could not insert module driver/ptusys/ptusys.ko: Invalid module format
ptusys driver installation failed
/dev/ptusys: No such file or directory
insmod: ERROR: could not insert module driver/ptusys/ptusys.ko: Invalid module format
ptusys driver installation failed
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> System Info:                   <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Host Name:                           controller-0
Host IP:                             169.254.202.1
OS Name:                             Debian GNU/Linux 11 (bullseye) 11
Kernel Version:                      Linux 5.10.0-6-rt-amd64 #1 SMP PREEMPT_RT StarlingX Debian 5.10.177-1.stx.76 (2024-03-29
BIOS Version:                        HPE, 1.11, 03/07/2024
Processor(s):                        1 Processor(s) Installed.
DIMM(s):                             8 DIMM(s) Installed.
Total System Memory:                 255208 MB
Available System Memory:             180543 MB


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
CAPID6:                              0xEFFFFFFB
CAPID7:                              0x00000003
CAPID8:                              0xEFFFFFFB
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
PTAT Driver Loaded:                  No

[06/28/24 21:45:17 UTC] PTAT started.

Press <Ctrl-C> to stop.


 Index Device Cor Thr CFreq UFreq  PState   Util  IPC     C0     C1     C6    PC2    PC6 MC Ch Sl  Temp DTS  Power  Volt UVolt TStat TLog #TL TMargin MCPMargin
     0   CPU0   -   -  3421  1600       0   1.25 1.86   2.45   1.91  95.64   0.00   0.00  -  -  -    66  25  75.48 0.951 0.735   0x0  0x0   0  14.625    14.625
     0   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.57     -     -     -  0x0   -       -         -
     1   CPU0   -   -  3500  1600       0   1.37 2.08   2.55   1.57  95.88   0.00   0.00  -  -  -    71  20  75.02 0.951 0.735   0x0  0x0   0  16.922    16.922
     1   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.66     -     -     -  0x0   -       -         -
     2   CPU0   -   -  3566  1600       0   1.36 2.26   2.57   2.00  95.44   0.00   0.00  -  -  -    66  25  75.86 0.951 0.735   0x0  0x0   0  16.547    16.547
     2   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.88     -     -     -  0x0   -       -         -
     3   CPU0   -   -  3539  1600       0   0.60 1.25   1.16   1.66  97.18   0.00   0.00  -  -  -    65  26  72.72 0.951 0.735   0x0  0x0   0  18.047    18.047
     3   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.50     -     -     -  0x0   -       -         -
     4   CPU0   -   -  3514  1600       0   0.91 1.91   1.77   1.89  96.34   0.00   0.00  -  -  -    65  26  73.80 0.951 0.735   0x0  0x0   0  17.359    17.359
     4   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.55     -     -     -  0x0   -       -         -
     5   CPU0   -   -  3528  1600       0   0.74 2.28   1.38   1.70  96.91   0.00   0.00  -  -  -    64  27  73.05 0.951 0.735   0x0  0x0   0  17.859    17.859
     5   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.49     -     -     -  0x0   -       -         -
     6   CPU0   -   -  3553  1600       0   0.67 1.77   1.29   1.52  97.20   0.00   0.00  -  -  -    64  27  72.45 0.951 0.735   0x0  0x0   0  18.406    18.406
     6   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.57     -     -     -  0x0   -       -         -
     7   CPU0   -   -  3513  1600       0   0.98 1.07   1.79   1.47  96.75   0.00   0.00  -  -  -    64  27  73.84 0.951 0.735   0x0  0x0   0  18.141    18.141
     7   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.66     -     -     -  0x0   -       -         -
     8   CPU0   -   -  3482  1600       0   1.47 1.89   2.43   1.58  95.99   0.00   0.00  -  -  -    66  25  75.29 0.951 0.735   0x0  0x0   0  17.703    17.703
     8   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.50     -     -     -  0x0   -       -         -
     9   CPU0   -   -  3533  1600       0   1.55 1.61   2.65   1.77  95.59   0.00   0.00  -  -  -    64  27  75.54 0.951 0.735   0x0  0x0   0  15.828    15.828
     9   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.91     -     -     -  0x0   -       -         -
    10   CPU0   -   -  3561  1600       0   0.81 1.55   1.51   1.57  96.92   0.00   0.00  -  -  -    66  25  73.28 0.951 0.735   0x0  0x0   0  17.953    17.953
    10   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.52     -     -     -  0x0   -       -         -
    11   CPU0   -   -  3561  1600       0   0.74 1.34   1.40   1.91  96.69   0.00   0.00  -  -  -    64  27  72.95 0.951 0.735   0x0  0x0   0  17.984    17.984
    11   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.62     -     -     -  0x0   -       -         -
    12   CPU0   -   -  3474  1600       0   1.07 2.40   1.99   1.54  96.47   0.00   0.00  -  -  -    63  28  74.24 0.951 0.735   0x0  0x0   0  18.750    18.750
    12   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.68     -     -     -  0x0   -       -         -
    13   CPU0   -   -  3537  1600       0   0.65 1.33   1.25   1.60  97.15   0.00   0.00  -  -  -    63  28  72.47 0.951 0.735   0x0  0x0   0  17.938    17.938
    13   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.48     -     -     -  0x0   -       -         -
    14   CPU0   -   -  3524  1600       0   0.68 1.24   1.29   1.68  97.04   0.00   0.00  -  -  -    63  28  72.58 0.951 0.735   0x0  0x0   0  19.188    19.188
    14   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.40     -     -     -  0x0   -       -         -
    15   CPU0   -   -  3491  1600       0   0.76 2.45   1.44   1.75  96.80   0.00   0.00  -  -  -    64  27  72.88 0.951 0.735   0x0  0x0   0  18.766    18.766
    15   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.53     -     -     -  0x0   -       -         -
    16   CPU0   -   -  3532  1600       0   2.08 2.49   3.53   1.36  95.10   0.00   0.00  -  -  -    65  26  77.17 0.951 0.735   0x0  0x0   0  17.938    17.938
    16   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.79     -     -     -  0x0   -       -         -
    17   CPU0   -   -  3546  1600       0   0.86 1.36   1.60   1.56  96.84   0.00   0.00  -  -  -    65  26  73.09 0.951 0.735   0x0  0x0   0  16.562    16.562
    17   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.55     -     -     -  0x0   -       -         -
    18   CPU0   -   -  3547  1600       0   0.72 1.00   1.35   1.78  96.87   0.00   0.00  -  -  -    67  24  72.80 0.951 0.735   0x0  0x0   0  18.125    18.125
    18   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.46     -     -     -  0x0   -       -         -
    19   CPU0   -   -  3559  1600       0   0.76 0.99   1.34   1.63  97.03   0.00   0.00  -  -  -    64  27  73.10 0.951 0.735   0x0  0x0   0  18.672    18.672
    19   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.39     -     -     -  0x0   -       -         -
    20   CPU0   -   -  3487  1600       0   1.17 2.84   2.18   1.80  96.02   0.00   0.00  -  -  -    69  22  74.44 0.951 0.735   0x0  0x0   0  18.359    18.359
    20   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.57     -     -     -  0x0   -       -         -
    21   CPU0   -   -  3563  1600       0   1.22 2.18   2.35   2.10  95.55   0.00   0.00  -  -  -    63  28  75.24 0.951 0.735   0x0  0x0   0  18.641    18.641
    21   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.73     -     -     -  0x0   -       -         -
    22   CPU0   -   -  3574  1600       0   0.68 1.43   1.27   1.74  96.99   0.00   0.00  -  -  -    64  27  72.89 0.951 0.735   0x0  0x0   0  18.875    18.875
    22   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.52     -     -     -  0x0   -       -         -
    23   CPU0   -   -  3565  1600       0   0.54 1.15   1.04   1.79  97.17   0.00   0.00  -  -  -    64  27  72.31 0.951 0.735   0x0  0x0   0  19.016    19.016
    23   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.56     -     -     -  0x0   -       -         -
    24   CPU0   -   -  3450  1600       0   0.90 2.40   1.74   1.74  96.52   0.00   0.00  -  -  -    65  26  73.57 0.951 0.735   0x0  0x0   0  17.844    17.844
    24   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.61     -     -     -  0x0   -       -         -
    25   CPU0   -   -  3504  1600       0   2.91 2.41   5.09   0.67  94.24   0.00   0.00  -  -  -    74  17  81.47 0.951 0.735   0x0  0x0   0  11.469    11.469
    25   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.64     -     -     -  0x0   -       -         -
    26   CPU0   -   -  3517  1600       0   2.20 1.29   3.93   1.03  95.05   0.00   0.00  -  -  -    70  21  79.24 0.951 0.735   0x0  0x0   0  11.141    11.141
    26   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.52     -     -     -  0x0   -       -         -
    27   CPU0   -   -  3472  1600       0   2.12 1.09   3.70   1.11  95.19   0.00   0.00  -  -  -    65  26  78.95 0.951 0.735   0x0  0x0   0  12.141    12.141
    27   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.45     -     -     -  0x0   -       -         -
    28   CPU0   -   -  3523  1600       0   1.44 1.93   2.63   1.88  95.49   0.00   0.00  -  -  -    65  26  75.79 0.951 0.735   0x0  0x0   0  16.078    16.078
    28   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.71     -     -     -  0x0   -       -         -
    29   CPU0   -   -  3550  1600       0   0.60 1.96   1.19   1.70  97.11   0.00   0.00  -  -  -    63  28  72.70 0.951 0.735   0x0  0x0   0  18.438    18.438
    29   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.62     -     -     -  0x0   -       -         -
    30   CPU0   -   -  3541  1600       0   0.77 1.71   1.44   1.72  96.84   0.00   0.00  -  -  -    63  28  73.08 0.951 0.735   0x0  0x0   0  18.844    18.844
    30   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.38     -     -     -  0x0   -       -         -
    31   CPU0   -   -  3539  1600       0   0.80 1.07   1.52   1.71  96.76   0.00   0.00  -  -  -    64  27  73.23 0.951 0.735   0x0  0x0   0  18.375    18.375
    31   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.49     -     -     -  0x0   -       -         -
    32   CPU0   -   -  3511  1600       0   0.90 2.18   1.81   1.78  96.41   0.00   0.00  -  -  -    66  25  73.66 0.951 0.735   0x0  0x0   0  17.516    17.516
    32   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.47     -     -     -  0x0   -       -         -
    33   CPU0   -   -  3537  1600       0   1.20 1.61   2.18   1.59  96.23   0.00   0.00  -  -  -    71  20  74.99 0.951 0.735   0x0  0x0   0  18.969    18.969
    33   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.37     -     -     -  0x0   -       -         -
    34   CPU0   -   -  3566  1600       0   0.69 1.56   1.33   1.52  97.15   0.00   0.00  -  -  -    64  27  72.88 0.951 0.735   0x0  0x0   0  17.812    17.812
    34   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.43     -     -     -  0x0   -       -         -
    35   CPU0   -   -  3561  1600       0   1.61 1.42   2.56   1.23  96.21   0.00   0.00  -  -  -    64  27  75.18 0.951 0.735   0x0  0x0   0  18.547    18.547
    35   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.75     -     -     -  0x0   -       -         -
    36   CPU0   -   -  3514  1600       0   0.99 2.40   1.92   1.62  96.46   0.00   0.00  -  -  -    63  28  73.92 0.951 0.735   0x0  0x0   0  18.359    18.359
    36   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.73     -     -     -  0x0   -       -         -
    37   CPU0   -   -  3548  1600       0   0.77 1.36   1.42   1.57  97.01   0.00   0.00  -  -  -    64  27  73.11 0.951 0.735   0x0  0x0   0  18.781    18.781
    37   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    52   -  13.57     -     -     -  0x0   -       -         -
    38   CPU0   -   -  3546  1600       0   0.97 0.88   1.73   1.74  96.54   0.00   0.00  -  -  -    63  28  73.54 0.951 0.735   0x0  0x0   0  18.625    18.625
    38   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    51   -  13.61     -     -     -  0x0   -       -         -
    39   CPU0   -   -  3529  1600       0   0.63 1.02   1.20   1.64  97.16   0.00   0.00  -  -  -    63  28  72.59 0.951 0.735   0x0  0x0   0  19.672    19.672
    39   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    51   -  13.50     -     -     -  0x0   -       -         -
    40   CPU0   -   -  3506  1600       0   1.61 2.44   2.86   1.60  95.54   0.00   0.00  -  -  -    62  29  75.98 0.951 0.735   0x0  0x0   0  17.203    17.203
    40   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    51   -  13.99     -     -     -  0x0   -       -         -
    41   CPU0   -   -  3554  1600       0   1.87 2.15   3.49   1.51  95.00   0.00   0.00  -  -  -    66  25  76.59 0.951 0.735   0x0  0x0   0  17.938    17.938
    41   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    51   -  13.94     -     -     -  0x0   -       -         -
    42   CPU0   -   -  3542  1600       0   1.54 1.30   2.80   1.37  95.82   0.00   0.00  -  -  -    67  24  75.39 0.951 0.735   0x0  0x0   0  17.578    17.578
    42   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    51   -  13.62     -     -     -  0x0   -       -         -
    43   CPU0   -   -  3567  1600       0   1.60 1.25   2.77   1.29  95.94   0.00   0.00  -  -  -    67  24  75.13 0.951 0.735   0x0  0x0   0  17.078    17.078
    43   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    51   -  13.51     -     -     -  0x0   -       -         -
    44   CPU0   -   -  3551  1600       0   2.27 2.53   3.59   1.26  95.15   0.00   0.00  -  -  -    70  21  77.59 0.951 0.735   0x0  0x0   0  16.703    16.703
    44   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    51   -  13.61     -     -     -  0x0   -       -         -
    45   CPU0   -   -  3573  1600       0   3.02 2.35   4.48   0.98  94.53   0.00   0.00  -  -  -    71  20  80.61 0.951 0.735   0x0  0x0   0  13.562    13.562
    45   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    51   -  13.59     -     -     -  0x0   -       -         -
    46   CPU0   -   -  3568  1600       0   1.81 1.00   3.18   1.13  95.68   0.00   0.00  -  -  -    63  28  76.55 0.951 0.735   0x0  0x0   0  11.969    11.969
    46   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    51   -  13.65     -     -     -  0x0   -       -         -
    47   CPU0   -   -  3563  1600       0   1.24 1.64   2.25   1.51  96.23   0.00   0.00  -  -  -    63  28  74.15 0.951 0.735   0x0  0x0   0  17.672    17.672
    47   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    51   -  13.54     -     -     -  0x0   -       -         -
    48   CPU0   -   -  3512  1600       0   1.48 2.51   2.48   1.83  95.69   0.00   0.00  -  -  -    62  29  75.88 0.951 0.735   0x0  0x0   0  17.109    17.109
    48   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    51   -  14.07     -     -     -  0x0   -       -         -
    49   CPU0   -   -  3539  1600       0   1.63 0.91   2.80   1.23  95.97   0.00   0.00  -  -  -    67  24  75.39 0.951 0.735   0x0  0x0   0  19.844    19.844
    49   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    51   -  13.56     -     -     -  0x0   -       -         -
    50   CPU0   -   -  3524  1600       0   1.94 1.84   3.32   1.37  95.31   0.00   0.00  -  -  -    63  28  76.59 0.951 0.735   0x0  0x0   0  16.375    16.375
    50   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    51   -  13.81     -     -     -  0x0   -       -         -
    51   CPU0   -   -  3540  1600       0   0.76 1.59   1.48   1.68  96.84   0.00   0.00  -  -  -    67  24  72.52 0.936 0.735   0x0  0x0   0  18.891    18.891
    51   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    51   -  13.65     -     -     -  0x0   -       -         -
    52   CPU0   -   -  3562  1600       0   0.91 2.24   1.63   1.86  96.50   0.00   0.00  -  -  -    63  28  73.98 0.951 0.735   0x0  0x0   0  18.703    18.703
    52   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    51   -  13.76     -     -     -  0x0   -       -         -
    53   CPU0   -   -  3540  1600       0   0.98 0.93   1.71   1.73  96.56   0.00   0.00  -  -  -    62  29  73.56 0.951 0.735   0x0  0x0   0  19.953    19.953
    53   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    51   -  13.73     -     -     -  0x0   -       -         -
    54   CPU0   -   -  3549  1600       0   0.91 2.31   1.65   1.46  96.89   0.00   0.00  -  -  -    66  25  73.22 0.951 0.738   0x0  0x0   0  19.359    19.359
    54   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    51   -  13.72     -     -     -  0x0   -       -         -
    55   CPU0   -   -  3582  1600       0   1.50 2.16   2.59   1.45  95.96   0.00   0.00  -  -  -    68  23  75.08 0.951 0.735   0x0  0x0   0  19.891    19.891
    55   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    51   -  13.89     -     -     -  0x0   -       -         -
    56   CPU0   -   -  3545  1600       0   1.19 1.72   2.18   1.47  96.35   0.00   0.00  -  -  -    62  29  74.64 0.951 0.735   0x0  0x0   0  19.344    19.344
    56   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    51   -  13.71     -     -     -  0x0   -       -         -
    57   CPU0   -   -  3519  1600       0   1.55 0.91   2.72   1.50  95.78   0.00   0.00  -  -  -    64  27  75.81 0.951 0.735   0x0  0x0   0  17.516    17.516
    57   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    51   -  13.86     -     -     -  0x0   -       -         -
^C
[06/28/24 21:46:19 UTC] PTAT stopped.

root@controller-0:/home/XXXXXX/james#
```

## Sensors after load started

```log
root@controller-0:/home/XXXXXX/james# ipmitool sensor| grep -e CPU -e DutyCycle -e Watts
02-CPU 1 PkgTmp  | 62.000     | degrees C  | ok    | na        | na        | na        | na        | 91.000    | na
Fan 1 DutyCycle  | 22.736     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 2 DutyCycle  | 22.736     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 3 DutyCycle  | 22.736     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 4 DutyCycle  | 22.736     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 5 DutyCycle  | 22.736     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 6 DutyCycle  | 22.736     | percent    | ok    | na        | na        | na        | na        | na        | na
PS 1 Input       | 150.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PS 2 Input       | 2550.000   | Watts      | ok    | na        | na        | na        | na        | na        | na
Power Meter      | 130.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
CPU Utilization  | 7.000      | unspecified | ok    | na        | na        | na        | na        | na        | na
PS 1 Output      | 0.000      | Watts      | ok    | na        | na        | na        | na        | na        | na
PS 2 Output      | 0.000      | Watts      | ok    | na        | na        | na        | na        | na        | na
CPU_Stat_C1      | 0x0        | discrete   | 0x8080| na        | na        | na        | na        | na        | na
root@controller-0:/home/XXXXXX/james#
```


## Temps didn't rise as much as with other tests, but all data recorded, no issues found.
## Success, end of performance tests with PTU