# ZT Triton 2.27 BMC firmware validation
# Firmware Performance testing
# 11/29/23 James Patchett

## Target Controller rchltxib-c000000-003 CR-3 (Richardson infrastructure System)
OAM: 2607:f160:0:3049:cd:290:0:10

## Subcloud rchltxfe-d93180012-001 (VCP-fe Infrastructure)
OAM: 2607:f160:10:9073:ce:40a:0:f400
ILO: 2607:f160:10:9073:ce:406:0:1000

ipmitool -I lanplus -U XXXXXX -P XXXXXX -H 2607:f160:10:9073:ce:406:0:1000 sol activate

## Subcloud rchltxfe-d93180012-001
## General info before we start

```log
controller-0:~$ source /etc/platform/openrc
[XXXXXX@controller-0 ~(keystone_admin)]$ system show
+------------------------+--------------------------------------+
| Property               | Value                                |
+------------------------+--------------------------------------+
| contact                | None                                 |
| created_at             | 2023-07-17T16:16:41.669508+00:00     |
| description            | None                                 |
| distributed_cloud_role | subcloud                             |
| https_enabled          | True                                 |
| latitude               | None                                 |
| location               | None                                 |
| longitude              | None                                 |
| name                   | rchltxfe-d93180012-001               |
| region_name            | rchltxfe-d93180012-001               |
| sdn_enabled            | False                                |
| security_feature       | spectre_meltdown_v1                  |
| service_project_name   | services                             |
| shared_services        | []                                   |
| software_version       | 21.12                                |
| system_mode            | simplex                              |
| system_type            | All-in-one                           |
| timezone               | UTC                                  |
| updated_at             | 2023-07-17T17:17:57.144973+00:00     |
| uuid                   | bf8885f0-583a-45fa-bd18-1cab57371a45 |
| vswitch_type           | none                                 |
+------------------------+--------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ system oam-show
+----------------+---------------------------------------+
| Property       | Value                                 |
+----------------+---------------------------------------+
| created_at     | 2023-07-17T16:18:28.746601+00:00      |
| isystem_uuid   | bf8885f0-583a-45fa-bd18-1cab57371a45  |
| oam_end_ip     | 2607:f160:10:9073:ffff:ffff:ffff:fffe |
| oam_gateway_ip | 2607:f160:10:9073:ce:28::             |
| oam_ip         | 2607:f160:10:9073:ce:40a:0:f400       |
| oam_start_ip   | 2607:f160:10:9073::1                  |
| oam_subnet     | 2607:f160:10:9073::/64                |
| updated_at     | None                                  |
| uuid           | 30fca5fe-860d-4d16-ad07-d2b356b994c8  |
+----------------+---------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ fm alarm-list

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
```

## MEAKV-642
## Performance Test sudo ./ptu -ct 1 -b 0
## measure sensors first, then run load, then check during load

## Sensors
```log
controller-0:~# ipmitool sensor | grep -e CPU_0_TEMP -e CPU0_Power -e SYS_FAN_1A -e CPU_CUPS
CPU_0_TEMP       | 39.000     | degrees C  | ok    | na        | na        | na        | 101.000   | 104.000   | na
CPU0_Power       | 60.000     | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 9600.000   | RPM        | ok    | na        | 1120.000  | na        | na        | 39840.000 | na
CPU_CUPS         | 4.000      | percent    | ok    | na        | na        | na        | na        | 100.000   | na
controller-0:~#
```

## Initiate load 

```log
controller-0:~# /home/XXXXXX/ptu -ct 1 -b 0

Command: /home/XXXXXX/ptu -ct 1 -b 0

INTEL SOFTWARE LICENSE AGREEMENT
IMPORTANT - READ BEFORE COPYING, INSTALLING OR USING.
License: Intel grants you the right to use the enclosed program (the "Software").
You will not use, copy, modify, rent, sell, or transfer the Software or any portion thereof except as provided for in this Agreement.

You may:
1 Use the Software on a single computer;
2 Copy the Software solely for backup or archival purposes.

RESTRICTIONS:

You WILL NOT:
1  Use the Software or cause the Software to be used on more than one computer at the same time, including using the Software across a network system;
2  Sublicense the Software;
3  Reverse engineer, decompile, or disassemble the Software;
4  Copy the software except as provided in this Agreement;
5  Permit simultaneous use of the Software by more than one user.

TRANSFER: You may transfer the Software to another party if the receiving party agrees to the terms of this Agreement and you retain no copies of the Software and accompanying documentation.

Transfer of the license terminates your right to use the Software.
OWNERSHIP AND COPYRIGHT OF SOFTWARE: Title to the Software and all copies thereof remain with Intel or its vendors.
The Software is copyrighted and is protected by United States copyright laws and international treaty provisions. You will not remove the copyright notice from the Software. You agree to prevent any unauthorized copying of the Software.

WARRANTY: Intel warrants that it has the right to license you to use the software.

Intel warrants that the media on which the Software is furnished will be free from defects in material and workmanship under normal use for a period of ninety (90) days from the date of purchase.
Intel's entire liability and your exclusive remedy shall be the replacement of the Software if the media on which the Software is furnished proves to be defective. This warranty is void if the media defect has resulted from accident, abuse, or misapplication. Any replacement of media will be warranted for the remainder of the original warranty period or thirty (30) days, whichever is longer.

DISCLAIMER: Except as provided above, the Software is provided "AS IS" without warranty of any kind.

LIMITATION OF LIABILITY: THE ABOVE WARRANTIES ARE THE ONLY WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING WARRANTIES OF
MERCHANTABILITY OR FITNESS FOR ANY PARTICULAR PURPOSE. NEITHER INTEL NOR ITS VENDORS SHALL BE LIABLE FOR ANY LOSS OF PROFITS, LOSS OF USE,
INTERRUPTION OF BUSINESS, NOR FOR INDIRECT, SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES OF ANY KIND WHETHER UNDER THIS AGREEMENT OR
OTHERWISE.

AUDIT: Intel reserves the right to conduct or have conducted audits to verify your compliance with this Agreement.

TERMINATION OF THIS LICENSE: Intel may terminate this license at any time if you are in breach of any of its terms or conditions. Upon termination, you will immediately destroy the Software or return all copies of the Software to Intel along with any copies you have made.

U.S. GOVERNMENT RESTRICTED RIGHTS: The Software and documentation are provided with "RESTRICTED RIGHTS." Use, duplication, or disclosure by the Government is subject to restrictions as set forth in FAR54-227-14 and DFAR252-227-7013 et seq or its successor. Use of this Software by the Government constitutes acknowledgment of Intel's proprietary rights in the Software.

EXPORT LAWS: You agree that neither the Software nor the direct product thereof is intended to be shipped either directly or indirectly to country groups Q, S, W, Y, Z, Afghanistan or the People's Republic of China, unless a validated export license is obtained from the U.S. Department of Commerce.

APPLICABLE LAWS: This Agreement is governed by the laws of the state of California and the United States, including patent and copyright laws. Any claim arising out of this Agreement will be brought in Santa Clara, California.
Accept License Agreement?(Y/y):y
Intel(R) Power Thermal Utility - Server Edition v2.3.1
Release Date: 12/04/2020
Copyright (C) 2020 Intel Corporation. All rights reserved.
Intel Confidential

/dev/ptusys: No such file or directory
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> System Info:                   <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Host Name:                           controller-0
Host IP:                             169.254.202.1
OS Name:                             CentOS Linux 7 (Core)
Kernel Version:                      Linux 5.10.112-200.25.tis.rt.el7.x86_64 #1 SMP PREEMPT_RT Wed May 3 22:37:28 EDT 2023
BIOS Version:                        American Megatrends Inc., 2.06, 06/28/2021
Processor(s):                        1 Processor(s) Installed.
DIMM(s):                             6 DIMM(s) Installed.
Total System Memory:                 95465 MB
Available System Memory:             54706 MB


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Processor: [CPU_0]             <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU ID:                              0x00050657 (Family 6 Model 55h Stepping 7)
CPU Brand Name:                      Intel(R) Xeon(R) Gold 6212U CPU @ 2.40GHz
CPU Code Name:                       Cascade Lake
CPU Type:                            Production Part
CPU Segment:                         Server
CPU PPIN:                            0x66AAEDBA78DF031D
CPU Base Frequency:                  1500 MHz
CPU Minimum Frequency:               1000 MHz
CPU Maximum Turbo Frequency:         3900 MHz
Uncore Minimum Frequency:            1200 MHz
Uncore Maximum Frequency:            2400 MHz
L2 Cache:                            24 x 1024 KB
L3 Cache:                            36608 KB
Hyper-threading:                     Enabled
Microcode Update Revision:           0x05003102
Number of Physcial Core(s):          24
Number of Logical Core(s):           48
Turbo Boost:                         Enabled
Turbo Boost Frequency:
 IA/SSE:
    1 -  2 Cores (Fused/Resolved):   3900 / 3900 (MHz)
    3 -  4 Cores (Fused/Resolved):   3700 / 3700 (MHz)
    5 - 16 Cores (Fused/Resolved):   3600 / 3600 (MHz)
   17 - 20 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   21 - 24 Cores (Fused/Resolved):   3100 / 3100 (MHz)
 AVX2:
    1 -  2 Cores (Fused/Resolved):   3700 / 3700 (MHz)
    3 -  4 Cores (Fused/Resolved):   3500 / 3500 (MHz)
    5 -  8 Cores (Fused/Resolved):   3400 / 3400 (MHz)
    9 - 12 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   13 - 16 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   17 - 20 Cores (Fused/Resolved):   2700 / 2700 (MHz)
   21 - 24 Cores (Fused/Resolved):   2600 / 2600 (MHz)
 AVX-512:
    1 -  2 Cores (Fused/Resolved):   3700 / 3700 (MHz)
    3 -  4 Cores (Fused/Resolved):   3500 / 3500 (MHz)
    5 -  8 Cores (Fused/Resolved):   3400 / 3400 (MHz)
    9 - 12 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   13 - 16 Cores (Fused/Resolved):   2600 / 2600 (MHz)
   17 - 20 Cores (Fused/Resolved):   2400 / 2400 (MHz)
   21 - 24 Cores (Fused/Resolved):   2300 / 2300 (MHz)
OVOLT_OVRD Supported:                0
OVOLT_OVRD Disabled:                 1
Platform ID:                         0x0
Platform Info:                       0x70A2CF2810F00000
Thermal Design Power (TDP):          165 W
Power Limit 1 - Long Duration:       Enabled, Clamp OFF, Power = 165 W, Time = 1.00 sec
Power Limit 2 - Short Duration:      Enabled, Clamp ON , Power = 198 W, Time = 1.95 sec
Config TDP Level Supported:          2
Config TDP Level 1:                  165.0 W (78.0 W - 413.0 W), 1500 MHz
Config TDP Level 2:                  165.0 W (78.0 W - 413.0 W), 1500 MHz
Current Config TDP Level:            NominalLevel 2
Tprochot:                            104 C
TCC Offset:                          0
CAPID0:                              0x001881F8
CAPID1:                              0x040000C3
CAPID2:                              0x13800000
CAPID3:                              0x00004000
CAPID4:                              0x24000EC0
CAPID5:                              0x660001FB
CAPID6:                              0x0FFDFFBF
CAPID7:                              0x07FDFFB7


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Memory: [MEM_0]                <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Number of DIMM(s):                   6
Number of Active Channel(s):         6
DRAM Power Meter Disabled:           0
DRAM RAPL Disabled:                  0
DRAM TDP Power:                      Min = 4.5 W, Max = 27.8 W, Time = 32.00 sec
DRAM / NVDIMM Info:
  MC 0, Chnl 0, Slot 0:              tempLo: 84 C, tempMid: 93 C, tempHi: 100 C
  MC 0, Chnl 1, Slot 0:              tempLo: 84 C, tempMid: 93 C, tempHi: 100 C
  MC 0, Chnl 2, Slot 0:              tempLo: 84 C, tempMid: 93 C, tempHi: 100 C
  MC 1, Chnl 3, Slot 0:              tempLo: 84 C, tempMid: 93 C, tempHi: 100 C
  MC 1, Chnl 4, Slot 0:              tempLo: 84 C, tempMid: 93 C, tempHi: 100 C
  MC 1, Chnl 5, Slot 0:              tempLo: 84 C, tempMid: 93 C, tempHi: 100 C


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Platform Controller Hub: [PCH] <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
PCH Device ID:                       8086:A1C1 (LBG-1G)
PCH Stepping:                        9
PCH Thermal Sensor Enable:           1
PCH Hot Level (PHL):                 -50
PCH Catastrophic Trip Point (CTRIP): 106


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> PTU Current Settings:          <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU Test Selected:                   1
MEM Test Selected:                   0
CPU Mask:                            0xFFFF
CPU Core Mask:                       0xFFFFFFFFFFFFFFFF
CPU Thread Mask:                     0xFF
MEM Mask:                            0xFFFF
MEM Core Mask:                       0xFFFFFFFFFFFFFFFF
MEM Thread Mask:                     0xFF
Core Power Level:                    100
Memory Power Level:                  100
Turbo Enabled:                       Yes
AVX Test Level:                      1
Pmax Pre-sync:                       5000 ms
Pmax Post-sync:                      3000 ms
Pmax Idle:                           2000 ms
Run Time:                            0 (Forever)
PTU Mon CPU Mask:                    0xFFFFFFFF
PTU Mon Core Mask:                   0xFFFFFFFFFFFFFFFF
PTU Mon MEM Mask:                    0xFFFFFFFF
PTU Mon Filter Mask:                 0x1F
PTU Mon Update Interval:             1000000 usec
PTU Mon Long Level:                  0
PTU Mon Timestamp:                   No
Log Enabled:                         No
Log Directory:                       /root/ptu/log
Log File Prefix:                     <timestamp>
Log Message File:                    <timestamp>_ptumsg.txt
Log Monitor File:                    <timestamp>_ptumon.txt
CSV Enabled:                         No
PTU License Auto Accept:             No
PTU Driver Loaded:                   No

[11/29/23 21:10:03 UTC] PTU started.

Press <Ctrl-C> to stop.


CPU_0: [IDLE] CFreq=1468, UFreq=2400, Util=3.03, IPC=0.80, Temp=54, DTS=50, Power=58.3, Volt=0.690
CPU_0: [TESTCFG] TestSel=1 (TDP), CoreMask=0xFFFFFFFFFFFFFFFF, ThreadMask=0xFF, PwrLevel=TDP, Turbo=0
CPU_0: [RUNNING] CFreq=1496, UFreq=2400, Util=100.00, IPC=3.96, Temp=58, DTS=46, Power=96.6, Volt=0.686

```

## Ptu monitoring

```log
[controller-0:~# /home/XXXXXX/ptu -mon

Command: /home/XXXXXX/ptu -mon

Intel(R) Power Thermal Utility - Server Edition v2.3.1
Release Date: 12/04/2020
Copyright (C) 2020 Intel Corporation. All rights reserved.
Intel Confidential

/dev/ptusys: No such file or directory
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> System Info:                   <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Host Name:                           controller-0
Host IP:                             169.254.202.1
OS Name:                             CentOS Linux 7 (Core)
Kernel Version:                      Linux 5.10.112-200.25.tis.rt.el7.x86_64 #1 SMP PREEMPT_RT Wed May 3 22:37:28 EDT 2023
BIOS Version:                        American Megatrends Inc., 2.06, 06/28/2021
Processor(s):                        1 Processor(s) Installed.
DIMM(s):                             6 DIMM(s) Installed.
Total System Memory:                 95465 MB
Available System Memory:             54700 MB


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Processor: [CPU_0]             <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU ID:                              0x00050657 (Family 6 Model 55h Stepping 7)
CPU Brand Name:                      Intel(R) Xeon(R) Gold 6212U CPU @ 2.40GHz
CPU Code Name:                       Cascade Lake
CPU Type:                            Production Part
CPU Segment:                         Server
CPU PPIN:                            0x66AAEDBA78DF031D
CPU Base Frequency:                  1500 MHz
CPU Minimum Frequency:               1000 MHz
CPU Maximum Turbo Frequency:         3900 MHz
Uncore Minimum Frequency:            1200 MHz
Uncore Maximum Frequency:            2400 MHz
L2 Cache:                            24 x 1024 KB
L3 Cache:                            36608 KB
Hyper-threading:                     Enabled
Microcode Update Revision:           0x05003102
Number of Physcial Core(s):          24
Number of Logical Core(s):           48
Turbo Boost:                         Disabled
Turbo Boost Frequency:
 IA/SSE:
    1 -  2 Cores (Fused/Resolved):   3900 / 3900 (MHz)
    3 -  4 Cores (Fused/Resolved):   3700 / 3700 (MHz)
    5 - 16 Cores (Fused/Resolved):   3600 / 3600 (MHz)
   17 - 20 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   21 - 24 Cores (Fused/Resolved):   3100 / 3100 (MHz)
 AVX2:
    1 -  2 Cores (Fused/Resolved):   3700 / 3700 (MHz)
    3 -  4 Cores (Fused/Resolved):   3500 / 3500 (MHz)
    5 -  8 Cores (Fused/Resolved):   3400 / 3400 (MHz)
    9 - 12 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   13 - 16 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   17 - 20 Cores (Fused/Resolved):   2700 / 2700 (MHz)
   21 - 24 Cores (Fused/Resolved):   2600 / 2600 (MHz)
 AVX-512:
    1 -  2 Cores (Fused/Resolved):   3700 / 3700 (MHz)
    3 -  4 Cores (Fused/Resolved):   3500 / 3500 (MHz)
    5 -  8 Cores (Fused/Resolved):   3400 / 3400 (MHz)
    9 - 12 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   13 - 16 Cores (Fused/Resolved):   2600 / 2600 (MHz)
   17 - 20 Cores (Fused/Resolved):   2400 / 2400 (MHz)
   21 - 24 Cores (Fused/Resolved):   2300 / 2300 (MHz)
OVOLT_OVRD Supported:                0
OVOLT_OVRD Disabled:                 1
Platform ID:                         0x0
Platform Info:                       0x70A2CF2810F00000
Thermal Design Power (TDP):          165 W
Power Limit 1 - Long Duration:       Enabled, Clamp OFF, Power = 165 W, Time = 1.00 sec
Power Limit 2 - Short Duration:      Enabled, Clamp ON , Power = 198 W, Time = 1.95 sec
Config TDP Level Supported:          2
Config TDP Level 1:                  165.0 W (78.0 W - 413.0 W), 1500 MHz
Config TDP Level 2:                  165.0 W (78.0 W - 413.0 W), 1500 MHz
Current Config TDP Level:            NominalLevel 2
Tprochot:                            104 C
TCC Offset:                          0
CAPID0:                              0x001881F8
CAPID1:                              0x040000C3
CAPID2:                              0x13800000
CAPID3:                              0x00004000
CAPID4:                              0x24000EC0
CAPID5:                              0x660001FB
CAPID6:                              0x0FFDFFBF
CAPID7:                              0x07FDFFB7


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Memory: [MEM_0]                <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Number of DIMM(s):                   6
Number of Active Channel(s):         6
DRAM Power Meter Disabled:           0
DRAM RAPL Disabled:                  0
DRAM TDP Power:                      Min = 4.5 W, Max = 27.8 W, Time = 32.00 sec
DRAM / NVDIMM Info:
  MC 0, Chnl 0, Slot 0:              tempLo: 84 C, tempMid: 93 C, tempHi: 100 C
  MC 0, Chnl 1, Slot 0:              tempLo: 84 C, tempMid: 93 C, tempHi: 100 C
  MC 0, Chnl 2, Slot 0:              tempLo: 84 C, tempMid: 93 C, tempHi: 100 C
  MC 1, Chnl 3, Slot 0:              tempLo: 84 C, tempMid: 93 C, tempHi: 100 C
  MC 1, Chnl 4, Slot 0:              tempLo: 84 C, tempMid: 93 C, tempHi: 100 C
  MC 1, Chnl 5, Slot 0:              tempLo: 84 C, tempMid: 93 C, tempHi: 100 C


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Platform Controller Hub: [PCH] <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
PCH Device ID:                       8086:A1C1 (LBG-1G)
PCH Stepping:                        9
PCH Thermal Sensor Enable:           1
PCH Hot Level (PHL):                 -50
PCH Catastrophic Trip Point (CTRIP): 106


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> PTU Current Settings:          <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU Test Selected:                   0
MEM Test Selected:                   0
CPU Mask:                            0xFFFF
CPU Core Mask:                       0xFFFFFFFFFFFFFFFF
CPU Thread Mask:                     0xFF
MEM Mask:                            0xFFFF
MEM Core Mask:                       0xFFFFFFFFFFFFFFFF
MEM Thread Mask:                     0xFF
Core Power Level:                    100
Memory Power Level:                  100
Turbo Enabled:                       No
AVX Test Level:                      1
Pmax Pre-sync:                       5000 ms
Pmax Post-sync:                      3000 ms
Pmax Idle:                           2000 ms
Run Time:                            0 (Forever)
PTU Mon CPU Mask:                    0xFFFFFFFF
PTU Mon Core Mask:                   0xFFFFFFFFFFFFFFFF
PTU Mon MEM Mask:                    0xFFFFFFFF
PTU Mon Filter Mask:                 0x1F
PTU Mon Update Interval:             1000000 usec
PTU Mon Long Level:                  0
PTU Mon Timestamp:                   No
Log Enabled:                         No
Log Directory:                       /root/ptu/log
Log File Prefix:                     <timestamp>
Log Message File:                    <timestamp>_ptumsg.txt
Log Monitor File:                    <timestamp>_ptumon.txt
CSV Enabled:                         No
PTU License Auto Accept:             No
PTU Driver Loaded:                   No

[11/29/23 21:11:40 UTC] PTU started.

Press <Ctrl-C> to stop.


 Index Device Cor Thr CFreq UFreq   Util  IPC     C0     C1     C6    PC2    PC6 MC Ch Sl  Temp DTS  Power  Volt TStat TLog #TL TMargin
     0   CPU0   -   -  1496  2400 100.00 3.96 100.00   0.00   0.00   0.00   0.00  -  -  -    66  38  97.93 0.695   0x0  0x0   0  27.391
     0   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.63     -     -  0x0   -       -
     1   CPU0   -   -  1497  2400 100.00 3.96 100.00   0.00   0.00   0.00   0.00  -  -  -    67  37  97.87 0.695   0x0  0x0   0  27.359
     1   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.64     -     -  0x0   -       -
     2   CPU0   -   -  1496  2400 100.00 3.97 100.00   0.00   0.00   0.00   0.00  -  -  -    67  37  98.01 0.694   0x0  0x0   0  27.344
     2   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.66     -     -  0x0   -       -
     3   CPU0   -   -  1496  2400 100.00 3.97 100.00   0.00   0.00   0.00   0.00  -  -  -    67  37  97.94 0.695   0x0  0x0   0  27.281
     3   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.64     -     -  0x0   -       -
     4   CPU0   -   -  1496  2400 100.00 3.96  99.99   0.01   0.00   0.00   0.00  -  -  -    67  37  97.65 0.695   0x0  0x0   0  27.266
     4   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.72     -     -  0x0   -       -
     5   CPU0   -   -  1496  2400 100.00 3.90  99.99   0.01   0.00   0.00   0.00  -  -  -    67  37  98.33 0.695   0x0  0x0   0  27.172
     5   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.81     -     -  0x0   -       -
     6   CPU0   -   -  1496  2400 100.00 3.92 100.00   0.01   0.00   0.00   0.00  -  -  -    67  37  97.55 0.695   0x0  0x0   0  27.219
     6   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.74     -     -  0x0   -       -
     7   CPU0   -   -  1496  2400 100.00 3.94 100.00   0.00   0.00   0.00   0.00  -  -  -    67  37  98.40 0.695   0x0  0x0   0  27.172
     7   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.79     -     -  0x0   -       -
     8   CPU0   -   -  1496  2400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    67  37  93.59 0.695   0x0  0x0   0  27.016
     8   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.75     -     -  0x0   -       -
     9   CPU0   -   -  1496  2400 100.00 3.93 100.00   0.00   0.00   0.00   0.00  -  -  -    67  37 102.71 0.695   0x0  0x0   0  27.094
     9   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.82     -     -  0x0   -       -
    10   CPU0   -   -  1496  2400 100.00 3.97 100.00   0.00   0.00   0.00   0.00  -  -  -    67  37  98.00 0.694   0x0  0x0   0  27.219
    10   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.58     -     -  0x0   -       -
    11   CPU0   -   -  1496  2400 100.00 3.96 100.00   0.00   0.00   0.00   0.00  -  -  -    67  37  97.89 0.694   0x0  0x0   0  27.141
    11   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.58     -     -  0x0   -       -
    12   CPU0   -   -  1496  2400 100.00 3.96 100.00   0.00   0.00   0.00   0.00  -  -  -    67  37  98.00 0.695   0x0  0x0   0  26.891
    12   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.64     -     -  0x0   -       -
    13   CPU0   -   -  1496  2400 100.00 3.92 100.00   0.00   0.00   0.00   0.00  -  -  -    67  37  97.98 0.695   0x0  0x0   0  26.812
    13   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.71     -     -  0x0   -       -
    14   CPU0   -   -  1496  2400 100.00 3.92 100.00   0.00   0.00   0.00   0.00  -  -  -    67  37  97.99 0.694   0x0  0x0   0  26.859
    14   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.79     -     -  0x0   -       -
    15   CPU0   -   -  1496  2400 100.00 3.92 100.00   0.00   0.00   0.00   0.00  -  -  -    67  37  97.92 0.695   0x0  0x0   0  26.812
    15   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.66     -     -  0x0   -       -
    16   CPU0   -   -  1496  2400 100.00 3.93 100.00   0.00   0.00   0.00   0.00  -  -  -    67  37  97.96 0.694   0x0  0x0   0  26.812
    16   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.67     -     -  0x0   -       -
    17   CPU0   -   -  1496  2400 100.00 3.95 100.00   0.00   0.00   0.00   0.00  -  -  -    67  37  98.04 0.694   0x0  0x0   0  26.766
    17   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.64     -     -  0x0   -       -
    18   CPU0   -   -  1496  2400 100.00 3.93 100.00   0.00   0.00   0.00   0.00  -  -  -    67  37  98.04 0.695   0x0  0x0   0  26.719
    18   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.76     -     -  0x0   -       -
    19   CPU0   -   -  1496  2400 100.00 3.91 100.00   0.00   0.00   0.00   0.00  -  -  -    67  37  98.12 0.695   0x0  0x0   0  26.734
    19   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.77     -     -  0x0   -       -
    20   CPU0   -   -  1496  2400 100.00 3.92 100.00   0.00   0.00   0.00   0.00  -  -  -    67  37  98.06 0.694   0x0  0x0   0  26.703
    20   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.69     -     -  0x0   -       -
    21   CPU0   -   -  1496  2400 100.00 3.94 100.00   0.00   0.00   0.00   0.00  -  -  -    67  37  97.96 0.694   0x0  0x0   0  26.703
    21   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.66     -     -  0x0   -       -
    22   CPU0   -   -  1496  2400 100.00 3.97 100.00   0.00   0.00   0.00   0.00  -  -  -    67  37  98.03 0.694   0x0  0x0   0  26.719
    22   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.60     -     -  0x0   -       -
    23   CPU0   -   -  1496  2400 100.00 3.97 100.00   0.00   0.00   0.00   0.00  -  -  -    68  36  97.95 0.693   0x0  0x0   0  26.734
    23   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.63     -     -  0x0   -       -
    24   CPU0   -   -  1496  2400 100.00 3.94 100.00   0.00   0.00   0.00   0.00  -  -  -    68  36  98.00 0.694   0x0  0x0   0  26.656
    24   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.75     -     -  0x0   -       -
    25   CPU0   -   -  1496  2400 100.00 3.87 100.00   0.00   0.00   0.00   0.00  -  -  -    68  36  98.02 0.694   0x0  0x0   0  26.625
    25   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.83     -     -  0x0   -       -
    26   CPU0   -   -  1496  2400 100.00 3.93 100.00   0.00   0.00   0.00   0.00  -  -  -    67  37  98.01 0.694   0x0  0x0   0  26.547
    26   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.69     -     -  0x0   -       -
    27   CPU0   -   -  1496  2400 100.00 3.92 100.00   0.00   0.00   0.00   0.00  -  -  -    67  37  97.20 0.695   0x0  0x0   0  26.531
    27   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.68     -     -  0x0   -       -
    28   CPU0   -   -  1496  2400 100.00 3.95 100.00   0.00   0.00   0.00   0.00  -  -  -    68  36  97.95 0.694   0x0  0x0   0  26.547
    28   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.64     -     -  0x0   -       -
    29   CPU0   -   -  1496  2400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    68  36  98.92 0.694   0x0  0x0   0  26.516
    29   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.75     -     -  0x0   -       -
    30   CPU0   -   -  1496  2400 100.00 3.92 100.00   0.00   0.00   0.00   0.00  -  -  -    68  36  97.99 0.694   0x0  0x0   0  26.516
    30   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.70     -     -  0x0   -       -
    31   CPU0   -   -  1496  2400 100.00 3.94 100.00   0.00   0.00   0.00   0.00  -  -  -    67  37  97.94 0.694   0x0  0x0   0  26.422
    31   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.63     -     -  0x0   -       -
    32   CPU0   -   -  1496  2400 100.00 3.94 100.00   0.00   0.00   0.00   0.00  -  -  -    68  36  98.08 0.693   0x0  0x0   0  26.406
    32   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.65     -     -  0x0   -       -
    33   CPU0   -   -  1497  2400 100.00 3.91 100.00   0.00   0.00   0.00   0.00  -  -  -    67  37  97.01 0.694   0x0  0x0   0  26.484
    33   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.66     -     -  0x0   -       -
    34   CPU0   -   -  1497  2400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    67  37  99.01 0.694   0x0  0x0   0  26.438
    34   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.72     -     -  0x0   -       -
    35   CPU0   -   -  1496  2400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    68  36  98.04 0.694   0x0  0x0   0  26.359
    35   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.71     -     -  0x0   -       -
    36   CPU0   -   -  1496  2400 100.00 3.94 100.00   0.00   0.00   0.00   0.00  -  -  -    67  37  97.94 0.693   0x0  0x0   0  26.422
    36   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.61     -     -  0x0   -       -
    37   CPU0   -   -  1496  2400 100.00 3.96 100.00   0.00   0.00   0.00   0.00  -  -  -    68  36  97.97 0.693   0x0  0x0   0  26.391
    37   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.60     -     -  0x0   -       -
    38   CPU0   -   -  1496  2400 100.00 3.98 100.00   0.00   0.00   0.00   0.00  -  -  -    68  36  97.86 0.693   0x0  0x0   0  26.312
    38   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.51     -     -  0x0   -       -
    39   CPU0   -   -  1496  2400 100.00 3.96 100.00   0.00   0.00   0.00   0.00  -  -  -    68  36  97.89 0.694   0x0  0x0   0  26.359
    39   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.58     -     -  0x0   -       -
    40   CPU0   -   -  1496  2400 100.00 3.96 100.00   0.00   0.00   0.00   0.00  -  -  -    68  36  97.99 0.693   0x0  0x0   0  26.234
    40   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.58     -     -  0x0   -       -
    41   CPU0   -   -  1496  2400 100.00 3.94 100.00   0.00   0.00   0.00   0.00  -  -  -    68  36  97.92 0.693   0x0  0x0   0  26.203
    41   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.58     -     -  0x0   -       -
    42   CPU0   -   -  1496  2400 100.00 3.97 100.00   0.00   0.00   0.00   0.00  -  -  -    68  36  97.94 0.694   0x0  0x0   0  26.172
    42   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.52     -     -  0x0   -       -
    43   CPU0   -   -  1496  2400 100.00 3.96 100.00   0.00   0.00   0.00   0.00  -  -  -    68  36  98.00 0.693   0x0  0x0   0  26.172
    43   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.59     -     -  0x0   -       -
    44   CPU0   -   -  1496  2400 100.00 3.95 100.00   0.00   0.00   0.00   0.00  -  -  -    68  36  97.98 0.693   0x0  0x0   0  26.141
    44   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.61     -     -  0x0   -       -
    45   CPU0   -   -  1496  2400 100.00 3.96 100.00   0.00   0.00   0.00   0.00  -  -  -    68  36  98.00 0.693   0x0  0x0   0  26.109
    45   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.57     -     -  0x0   -       -
    46   CPU0   -   -  1496  2400 100.00 3.94 100.00   0.00   0.00   0.00   0.00  -  -  -    68  36  97.89 0.693   0x0  0x0   0  26.141
    46   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.61     -     -  0x0   -       -
    47   CPU0   -   -  1496  2400 100.00 3.95 100.00   0.00   0.00   0.00   0.00  -  -  -    68  36  97.54 0.693   0x0  0x0   0  26.141
    47   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.60     -     -  0x0   -       -
    48   CPU0   -   -  1496  2400 100.00 3.93 100.00   0.00   0.00   0.00   0.00  -  -  -    68  36  98.42 0.693   0x0  0x0   0  26.141
    48   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.74     -     -  0x0   -       -
    49   CPU0   -   -  1496  2400 100.00 3.93 100.00   0.00   0.00   0.00   0.00  -  -  -    68  36  97.97 0.693   0x0  0x0   0  26.125
    49   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.64     -     -  0x0   -       -
    50   CPU0   -   -  1496  2400 100.00 3.93 100.00   0.00   0.00   0.00   0.00  -  -  -    68  36  98.04 0.693   0x0  0x0   0  26.078
    50   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.71     -     -  0x0   -       -
    51   CPU0   -   -  1496  2400 100.00 3.95 100.00   0.00   0.00   0.00   0.00  -  -  -    68  36  97.90 0.693   0x0  0x0   0  26.094
    51   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.59     -     -  0x0   -       -
    52   CPU0   -   -  1496  2400 100.00 3.94  99.97   0.03   0.00   0.00   0.00  -  -  -    68  36  98.06 0.694   0x0  0x0   0  26.062
    52   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.68     -     -  0x0   -       -
    53   CPU0   -   -  1496  2400 100.00 3.92 100.00   0.03   0.00   0.00   0.00  -  -  -    68  36  98.01 0.693   0x0  0x0   0  26.062
    53   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.71     -     -  0x0   -       -
    54   CPU0   -   -  1496  2400 100.00 3.95 100.00   0.00   0.00   0.00   0.00  -  -  -    68  36  97.69 0.693   0x0  0x0   0  26.016
    54   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.66     -     -  0x0   -       -
    55   CPU0   -   -  1496  2400 100.00 3.96 100.00   0.00   0.00   0.00   0.00  -  -  -    68  36  98.28 0.693   0x0  0x0   0  25.984
    55   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.68     -     -  0x0   -       -
    56   CPU0   -   -  1496  2400 100.00 3.96 100.00   0.00   0.00   0.00   0.00  -  -  -    68  36  97.99 0.693   0x0  0x0   0  25.984
    56   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.62     -     -  0x0   -       -
    57   CPU0   -   -  1496  2400 100.00 3.97 100.00   0.00   0.00   0.00   0.00  -  -  -    68  36  97.84 0.693   0x0  0x0   0  26.016
    57   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.58     -     -  0x0   -       -
    58   CPU0   -   -  1496  2400 100.00 3.96 100.00   0.00   0.00   0.00   0.00  -  -  -    68  36  98.01 0.693   0x0  0x0   0  25.984
    58   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.64     -     -  0x0   -       -
    59   CPU0   -   -  1496  2400 100.00 3.96 100.00   0.00   0.00   0.00   0.00  -  -  -    68  36  97.91 0.693   0x0  0x0   0  25.953
    59   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.59     -     -  0x0   -       -
    60   CPU0   -   -  1496  2400 100.00 3.97 100.00   0.00   0.00   0.00   0.00  -  -  -    68  36  97.92 0.693   0x0  0x0   0  25.953
    60   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.63     -     -  0x0   -       -
    61   CPU0   -   -  1496  2400 100.00 3.96 100.00   0.00   0.00   0.00   0.00  -  -  -    68  36  97.90 0.693   0x0  0x0   0  25.891
    61   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.66     -     -  0x0   -       -
    62   CPU0   -   -  1496  2400 100.00 3.97 100.00   0.00   0.00   0.00   0.00  -  -  -    68  36  97.94 0.693   0x0  0x0   0  25.969
    62   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.66     -     -  0x0   -       -
    63   CPU0   -   -  1497  2400 100.00 3.93 100.00   0.00   0.00   0.00   0.00  -  -  -    68  36  98.06 0.693   0x0  0x0   0  25.938
    63   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.82     -     -  0x0   -       -
    64   CPU0   -   -  1496  2400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    68  36  98.10 0.693   0x0  0x0   0  25.828
    64   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.85     -     -  0x0   -       -
    65   CPU0   -   -  1496  2400 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    68  36  97.99 0.693   0x0  0x0   0  25.797
    65   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.90     -     -  0x0   -       -
    66   CPU0   -   -  1496  2400 100.00 3.92 100.00   0.00   0.00   0.00   0.00  -  -  -    68  36  97.73 0.693   0x0  0x0   0  25.609
    66   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.83     -     -  0x0   -       -
    67   CPU0   -   -  1496  2400 100.00 3.95 100.00   0.00   0.00   0.00   0.00  -  -  -    68  36  98.30 0.693   0x0  0x0   0  25.688
    67   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.70     -     -  0x0   -       -
    68   CPU0   -   -  1496  2400 100.00 3.94 100.00   0.00   0.00   0.00   0.00  -  -  -    68  36  98.00 0.693   0x0  0x0   0  25.641
    68   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.75     -     -  0x0   -       -
    69   CPU0   -   -  1496  2400 100.00 3.93 100.00   0.00   0.00   0.00   0.00  -  -  -    68  36  97.99 0.693   0x0  0x0   0  25.750
    69   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.74     -     -  0x0   -       -
    70   CPU0   -   -  1496  2400 100.00 3.93 100.00   0.00   0.00   0.00   0.00  -  -  -    68  36  97.99 0.694   0x0  0x0   0  25.594
    70   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.70     -     -  0x0   -       -
    71   CPU0   -   -  1496  2400 100.00 3.94 100.00   0.00   0.00   0.00   0.00  -  -  -    68  36  98.03 0.693   0x0  0x0   0  25.594
    71   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.67     -     -  0x0   -       -
    72   CPU0   -   -  1496  2400 100.00 3.92 100.00   0.00   0.00   0.00   0.00  -  -  -    69  35  97.82 0.693   0x0  0x0   0  25.656
    72   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.71     -     -  0x0   -       -
    73   CPU0   -   -  1496  2400 100.00 3.91 100.00   0.00   0.00   0.00   0.00  -  -  -    68  36  98.10 0.693   0x0  0x0   0  25.594
    73   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.72     -     -  0x0   -       -
^C
[11/29/23 21:12:58 UTC] PTU stopped.

controller-0:~#
```

## check the sensors again, to see the reaction to raised thermals

```log

controller-0:~# ipmitool sensor | grep -e CPU_0_TEMP -e CPU0_Power -e SYS_FAN_1A -e CPU_CUPS
CPU_0_TEMP       | 68.000     | degrees C  | ok    | na        | na        | na        | 101.000   | 104.000   | na
CPU0_Power       | 147.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 11520.000  | RPM        | ok    | na        | 1120.000  | na        | na        | 39840.000 | na
CPU_CUPS         | 98.000     | percent    | ok    | na        | na        | na        | na        | 100.000   | na
controller-0:~#
```

## Success as we have observed thermals rising, along with fans increase in RPMs...  on to next test

## MEAKV-643
## Performance Test #2 
## Run Core IA/SSE with 100% power, and Turbo on
## ./ptu -ct 3 -cp 100 -b 1

## Sensors before run

```log
controller-0:~# ipmitool sensor | grep -e CPU_0_TEMP -e CPU0_Power -e SYS_FAN_1A -e CPU_CUPS
CPU_0_TEMP       | 46.000     | degrees C  | ok    | na        | na        | na        | 101.000   | 104.000   | na
CPU0_Power       | 62.000     | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 9440.000   | RPM        | ok    | na        | 1120.000  | na        | na        | 39840.000 | na
CPU_CUPS         | 2.000      | percent    | ok    | na        | na        | na        | na        | 100.000   | na
controller-0:~#
```

## Initiate Load 

```log
controller-0:~# /home/XXXXXX/ptu -ct 3 -cp 100 -b 1

Command: /home/XXXXXX/ptu -ct 3 -cp 100 -b 1

Intel(R) Power Thermal Utility - Server Edition v2.3.1
Release Date: 12/04/2020
Copyright (C) 2020 Intel Corporation. All rights reserved.
Intel Confidential

/dev/ptusys: No such file or directory
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> System Info:                   <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Host Name:                           controller-0
Host IP:                             169.254.202.1
OS Name:                             CentOS Linux 7 (Core)
Kernel Version:                      Linux 5.10.112-200.25.tis.rt.el7.x86_64 #1 SMP PREEMPT_RT Wed May 3 22:37:28 EDT 2023
BIOS Version:                        American Megatrends Inc., 2.06, 06/28/2021
Processor(s):                        1 Processor(s) Installed.
DIMM(s):                             6 DIMM(s) Installed.
Total System Memory:                 95465 MB
Available System Memory:             54677 MB


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Processor: [CPU_0]             <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU ID:                              0x00050657 (Family 6 Model 55h Stepping 7)
CPU Brand Name:                      Intel(R) Xeon(R) Gold 6212U CPU @ 2.40GHz
CPU Code Name:                       Cascade Lake
CPU Type:                            Production Part
CPU Segment:                         Server
CPU PPIN:                            0x66AAEDBA78DF031D
CPU Base Frequency:                  1500 MHz
CPU Minimum Frequency:               1000 MHz
CPU Maximum Turbo Frequency:         3900 MHz
Uncore Minimum Frequency:            1200 MHz
Uncore Maximum Frequency:            2400 MHz
L2 Cache:                            24 x 1024 KB
L3 Cache:                            36608 KB
Hyper-threading:                     Enabled
Microcode Update Revision:           0x05003102
Number of Physcial Core(s):          24
Number of Logical Core(s):           48
Turbo Boost:                         Enabled
Turbo Boost Frequency:
 IA/SSE:
    1 -  2 Cores (Fused/Resolved):   3900 / 3900 (MHz)
    3 -  4 Cores (Fused/Resolved):   3700 / 3700 (MHz)
    5 - 16 Cores (Fused/Resolved):   3600 / 3600 (MHz)
   17 - 20 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   21 - 24 Cores (Fused/Resolved):   3100 / 3100 (MHz)
 AVX2:
    1 -  2 Cores (Fused/Resolved):   3700 / 3700 (MHz)
    3 -  4 Cores (Fused/Resolved):   3500 / 3500 (MHz)
    5 -  8 Cores (Fused/Resolved):   3400 / 3400 (MHz)
    9 - 12 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   13 - 16 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   17 - 20 Cores (Fused/Resolved):   2700 / 2700 (MHz)
   21 - 24 Cores (Fused/Resolved):   2600 / 2600 (MHz)
 AVX-512:
    1 -  2 Cores (Fused/Resolved):   3700 / 3700 (MHz)
    3 -  4 Cores (Fused/Resolved):   3500 / 3500 (MHz)
    5 -  8 Cores (Fused/Resolved):   3400 / 3400 (MHz)
    9 - 12 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   13 - 16 Cores (Fused/Resolved):   2600 / 2600 (MHz)
   17 - 20 Cores (Fused/Resolved):   2400 / 2400 (MHz)
   21 - 24 Cores (Fused/Resolved):   2300 / 2300 (MHz)
OVOLT_OVRD Supported:                0
OVOLT_OVRD Disabled:                 1
Platform ID:                         0x0
Platform Info:                       0x70A2CF2810F00000
Thermal Design Power (TDP):          165 W
Power Limit 1 - Long Duration:       Enabled, Clamp OFF, Power = 165 W, Time = 1.00 sec
Power Limit 2 - Short Duration:      Enabled, Clamp ON , Power = 198 W, Time = 1.95 sec
Config TDP Level Supported:          2
Config TDP Level 1:                  165.0 W (78.0 W - 413.0 W), 1500 MHz
Config TDP Level 2:                  165.0 W (78.0 W - 413.0 W), 1500 MHz
Current Config TDP Level:            NominalLevel 2
Tprochot:                            104 C
TCC Offset:                          0
CAPID0:                              0x001881F8
CAPID1:                              0x040000C3
CAPID2:                              0x13800000
CAPID3:                              0x00004000
CAPID4:                              0x24000EC0
CAPID5:                              0x660001FB
CAPID6:                              0x0FFDFFBF
CAPID7:                              0x07FDFFB7


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Memory: [MEM_0]                <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Number of DIMM(s):                   6
Number of Active Channel(s):         6
DRAM Power Meter Disabled:           0
DRAM RAPL Disabled:                  0
DRAM TDP Power:                      Min = 4.5 W, Max = 27.8 W, Time = 32.00 sec
DRAM / NVDIMM Info:
  MC 0, Chnl 0, Slot 0:              tempLo: 84 C, tempMid: 93 C, tempHi: 100 C
  MC 0, Chnl 1, Slot 0:              tempLo: 84 C, tempMid: 93 C, tempHi: 100 C
  MC 0, Chnl 2, Slot 0:              tempLo: 84 C, tempMid: 93 C, tempHi: 100 C
  MC 1, Chnl 3, Slot 0:              tempLo: 84 C, tempMid: 93 C, tempHi: 100 C
  MC 1, Chnl 4, Slot 0:              tempLo: 84 C, tempMid: 93 C, tempHi: 100 C
  MC 1, Chnl 5, Slot 0:              tempLo: 84 C, tempMid: 93 C, tempHi: 100 C


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Platform Controller Hub: [PCH] <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
PCH Device ID:                       8086:A1C1 (LBG-1G)
PCH Stepping:                        9
PCH Thermal Sensor Enable:           1
PCH Hot Level (PHL):                 -50
PCH Catastrophic Trip Point (CTRIP): 106


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> PTU Current Settings:          <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU Test Selected:                   3
MEM Test Selected:                   0
CPU Mask:                            0xFFFF
CPU Core Mask:                       0xFFFFFFFFFFFFFFFF
CPU Thread Mask:                     0xFF
MEM Mask:                            0xFFFF
MEM Core Mask:                       0xFFFFFFFFFFFFFFFF
MEM Thread Mask:                     0xFF
Core Power Level:                    100
Memory Power Level:                  100
Turbo Enabled:                       Yes
AVX Test Level:                      1
Pmax Pre-sync:                       5000 ms
Pmax Post-sync:                      3000 ms
Pmax Idle:                           2000 ms
Run Time:                            0 (Forever)
PTU Mon CPU Mask:                    0xFFFFFFFF
PTU Mon Core Mask:                   0xFFFFFFFFFFFFFFFF
PTU Mon MEM Mask:                    0xFFFFFFFF
PTU Mon Filter Mask:                 0x1F
PTU Mon Update Interval:             1000000 usec
PTU Mon Long Level:                  0
PTU Mon Timestamp:                   No
Log Enabled:                         No
Log Directory:                       /root/ptu/log
Log File Prefix:                     <timestamp>
Log Message File:                    <timestamp>_ptumsg.txt
Log Monitor File:                    <timestamp>_ptumon.txt
CSV Enabled:                         No
PTU License Auto Accept:             No
PTU Driver Loaded:                   No

[11/29/23 21:17:30 UTC] PTU started.

Press <Ctrl-C> to stop.


CPU_0: [IDLE] CFreq=2313, UFreq=2400, Util=1.24, IPC=0.68, Temp=56, DTS=48, Power=61.2, Volt=0.778
CPU_0: [TESTCFG] TestSel=3 (Core IA/SSE), CoreMask=0xFFFFFFFFFFFFFFFF, ThreadMask=0xFF, PwrLevel=100, Turbo=1
CPU_0: [RUNNING] CFreq=2295, UFreq=2400, Util=100.00, IPC=3.92, Temp=70, DTS=34, Power=158.0, Volt=0.772
```

## ptu -mon

```log
controller-0:~# /home/XXXXXX/ptu -mon

Command: /home/XXXXXX/ptu -mon

Intel(R) Power Thermal Utility - Server Edition v2.3.1
Release Date: 12/04/2020
Copyright (C) 2020 Intel Corporation. All rights reserved.
Intel Confidential

/dev/ptusys: No such file or directory
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> System Info:                   <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Host Name:                           controller-0
Host IP:                             169.254.202.1
OS Name:                             CentOS Linux 7 (Core)
Kernel Version:                      Linux 5.10.112-200.25.tis.rt.el7.x86_64 #1 SMP PREEMPT_RT Wed May 3 22:37:28 EDT 2023
BIOS Version:                        American Megatrends Inc., 2.06, 06/28/2021
Processor(s):                        1 Processor(s) Installed.
DIMM(s):                             6 DIMM(s) Installed.
Total System Memory:                 95465 MB
Available System Memory:             54617 MB


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Processor: [CPU_0]             <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU ID:                              0x00050657 (Family 6 Model 55h Stepping 7)
CPU Brand Name:                      Intel(R) Xeon(R) Gold 6212U CPU @ 2.40GHz
CPU Code Name:                       Cascade Lake
CPU Type:                            Production Part
CPU Segment:                         Server
CPU PPIN:                            0x66AAEDBA78DF031D
CPU Base Frequency:                  1500 MHz
CPU Minimum Frequency:               1000 MHz
CPU Maximum Turbo Frequency:         3900 MHz
Uncore Minimum Frequency:            1200 MHz
Uncore Maximum Frequency:            2400 MHz
L2 Cache:                            24 x 1024 KB
L3 Cache:                            36608 KB
Hyper-threading:                     Enabled
Microcode Update Revision:           0x05003102
Number of Physcial Core(s):          24
Number of Logical Core(s):           48
Turbo Boost:                         Enabled
Turbo Boost Frequency:
 IA/SSE:
    1 -  2 Cores (Fused/Resolved):   3900 / 3900 (MHz)
    3 -  4 Cores (Fused/Resolved):   3700 / 3700 (MHz)
    5 - 16 Cores (Fused/Resolved):   3600 / 3600 (MHz)
   17 - 20 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   21 - 24 Cores (Fused/Resolved):   3100 / 3100 (MHz)
 AVX2:
    1 -  2 Cores (Fused/Resolved):   3700 / 3700 (MHz)
    3 -  4 Cores (Fused/Resolved):   3500 / 3500 (MHz)
    5 -  8 Cores (Fused/Resolved):   3400 / 3400 (MHz)
    9 - 12 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   13 - 16 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   17 - 20 Cores (Fused/Resolved):   2700 / 2700 (MHz)
   21 - 24 Cores (Fused/Resolved):   2600 / 2600 (MHz)
 AVX-512:
    1 -  2 Cores (Fused/Resolved):   3700 / 3700 (MHz)
    3 -  4 Cores (Fused/Resolved):   3500 / 3500 (MHz)
    5 -  8 Cores (Fused/Resolved):   3400 / 3400 (MHz)
    9 - 12 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   13 - 16 Cores (Fused/Resolved):   2600 / 2600 (MHz)
   17 - 20 Cores (Fused/Resolved):   2400 / 2400 (MHz)
   21 - 24 Cores (Fused/Resolved):   2300 / 2300 (MHz)
OVOLT_OVRD Supported:                0
OVOLT_OVRD Disabled:                 1
Platform ID:                         0x0
Platform Info:                       0x70A2CF2810F00000
Thermal Design Power (TDP):          165 W
Power Limit 1 - Long Duration:       Enabled, Clamp OFF, Power = 165 W, Time = 1.00 sec
Power Limit 2 - Short Duration:      Enabled, Clamp ON , Power = 198 W, Time = 1.95 sec
Config TDP Level Supported:          2
Config TDP Level 1:                  165.0 W (78.0 W - 413.0 W), 1500 MHz
Config TDP Level 2:                  165.0 W (78.0 W - 413.0 W), 1500 MHz
Current Config TDP Level:            NominalLevel 2
Tprochot:                            104 C
TCC Offset:                          0
CAPID0:                              0x001881F8
CAPID1:                              0x040000C3
CAPID2:                              0x13800000
CAPID3:                              0x00004000
CAPID4:                              0x24000EC0
CAPID5:                              0x660001FB
CAPID6:                              0x0FFDFFBF
CAPID7:                              0x07FDFFB7


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Memory: [MEM_0]                <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Number of DIMM(s):                   6
Number of Active Channel(s):         6
DRAM Power Meter Disabled:           0
DRAM RAPL Disabled:                  0
DRAM TDP Power:                      Min = 4.5 W, Max = 27.8 W, Time = 32.00 sec
DRAM / NVDIMM Info:
  MC 0, Chnl 0, Slot 0:              tempLo: 84 C, tempMid: 93 C, tempHi: 100 C
  MC 0, Chnl 1, Slot 0:              tempLo: 84 C, tempMid: 93 C, tempHi: 100 C
  MC 0, Chnl 2, Slot 0:              tempLo: 84 C, tempMid: 93 C, tempHi: 100 C
  MC 1, Chnl 3, Slot 0:              tempLo: 84 C, tempMid: 93 C, tempHi: 100 C
  MC 1, Chnl 4, Slot 0:              tempLo: 84 C, tempMid: 93 C, tempHi: 100 C
  MC 1, Chnl 5, Slot 0:              tempLo: 84 C, tempMid: 93 C, tempHi: 100 C


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Platform Controller Hub: [PCH] <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
PCH Device ID:                       8086:A1C1 (LBG-1G)
PCH Stepping:                        9
PCH Thermal Sensor Enable:           1
PCH Hot Level (PHL):                 -50
PCH Catastrophic Trip Point (CTRIP): 106


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> PTU Current Settings:          <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU Test Selected:                   0
MEM Test Selected:                   0
CPU Mask:                            0xFFFF
CPU Core Mask:                       0xFFFFFFFFFFFFFFFF
CPU Thread Mask:                     0xFF
MEM Mask:                            0xFFFF
MEM Core Mask:                       0xFFFFFFFFFFFFFFFF
MEM Thread Mask:                     0xFF
Core Power Level:                    100
Memory Power Level:                  100
Turbo Enabled:                       No
AVX Test Level:                      1
Pmax Pre-sync:                       5000 ms
Pmax Post-sync:                      3000 ms
Pmax Idle:                           2000 ms
Run Time:                            0 (Forever)
PTU Mon CPU Mask:                    0xFFFFFFFF
PTU Mon Core Mask:                   0xFFFFFFFFFFFFFFFF
PTU Mon MEM Mask:                    0xFFFFFFFF
PTU Mon Filter Mask:                 0x1F
PTU Mon Update Interval:             1000000 usec
PTU Mon Long Level:                  0
PTU Mon Timestamp:                   No
Log Enabled:                         No
Log Directory:                       /root/ptu/log
Log File Prefix:                     <timestamp>
Log Message File:                    <timestamp>_ptumsg.txt
Log Monitor File:                    <timestamp>_ptumon.txt
CSV Enabled:                         No
PTU License Auto Accept:             No
PTU Driver Loaded:                   No

[11/29/23 21:18:29 UTC] PTU started.

Press <Ctrl-C> to stop.


 Index Device Cor Thr CFreq UFreq   Util  IPC     C0     C1     C6    PC2    PC6 MC Ch Sl  Temp DTS  Power  Volt TStat TLog #TL TMargin
     0   CPU0   -   -  2295  2400 100.00 3.88 100.00   0.00   0.00   0.00   0.00  -  -  -    82  22 159.34 0.777   0x0  0x0   0  16.285
     0   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    36   -  10.66     -     -  0x0   -       -
     1   CPU0   -   -  2295  2400 100.00 3.93 100.00   0.00   0.00   0.00   0.00  -  -  -    83  21 159.86 0.776   0x0  0x0   0  16.219
     1   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    36   -  10.56     -     -  0x0   -       -
     2   CPU0   -   -  2295  2400 100.00 3.92 100.00   0.00   0.00   0.00   0.00  -  -  -    83  21 159.64 0.776   0x0  0x0   0  16.164
     2   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    36   -  10.63     -     -  0x0   -       -
     3   CPU0   -   -  2295  2400 100.00 3.92 100.00   0.00   0.00   0.00   0.00  -  -  -    83  21 159.56 0.776   0x0  0x0   0  16.203
     3   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    36   -  10.54     -     -  0x0   -       -
     4   CPU0   -   -  2295  2400 100.00 3.91 100.00   0.00   0.00   0.00   0.00  -  -  -    83  21 159.51 0.776   0x0  0x0   0  15.789
     4   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    36   -  10.63     -     -  0x0   -       -
     5   CPU0   -   -  2295  2400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    83  21 159.16 0.775   0x0  0x0   0  15.598
     5   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    36   -  10.58     -     -  0x0   -       -
     6   CPU0   -   -  2295  2400 100.00 3.92 100.00   0.00   0.00   0.00   0.00  -  -  -    83  21 159.66 0.776   0x0  0x0   0  15.637
     6   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    36   -  10.62     -     -  0x0   -       -
     7   CPU0   -   -  2295  2400 100.00 3.92 100.00   0.00   0.00   0.00   0.00  -  -  -    83  21 159.42 0.775   0x0  0x0   0  15.473
     7   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    36   -  10.63     -     -  0x0   -       -
     8   CPU0   -   -  2295  2400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    84  20 159.50 0.776   0x0  0x0   0  15.387
     8   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    36   -  10.64     -     -  0x0   -       -
     9   CPU0   -   -  2295  2400 100.00 3.93 100.00   0.00   0.00   0.00   0.00  -  -  -    84  20 159.66 0.775   0x0  0x0   0  15.293
     9   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    36   -  10.60     -     -  0x0   -       -
    10   CPU0   -   -  2295  2400 100.00 3.94 100.00   0.00   0.00   0.00   0.00  -  -  -    83  21 159.52 0.776   0x0  0x0   0  15.250
    10   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    36   -  10.55     -     -  0x0   -       -
    11   CPU0   -   -  2295  2400 100.00 3.93 100.00   0.00   0.00   0.00   0.00  -  -  -    84  20 159.64 0.775   0x0  0x0   0  15.371
    11   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    36   -  10.50     -     -  0x0   -       -
    12   CPU0   -   -  2295  2400 100.00 3.92 100.00   0.00   0.00   0.00   0.00  -  -  -    84  20 159.72 0.775   0x0  0x0   0  15.234
    12   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    36   -  10.60     -     -  0x0   -       -
    13   CPU0   -   -  2295  2400 100.00 3.93 100.00   0.00   0.00   0.00   0.00  -  -  -    84  20 159.68 0.775   0x0  0x0   0  15.156
    13   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    36   -  10.53     -     -  0x0   -       -
    14   CPU0   -   -  2294  2400 100.00 3.92  99.98   0.02   0.00   0.00   0.00  -  -  -    84  20 159.65 0.776   0x0  0x0   0  15.105
    14   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    36   -  10.59     -     -  0x0   -       -
    15   CPU0   -   -  2295  2400 100.00 3.92 100.00   0.02   0.00   0.00   0.00  -  -  -    84  20 159.54 0.776   0x0  0x0   0  15.027
    15   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    36   -  10.64     -     -  0x0   -       -
    16   CPU0   -   -  2295  2400 100.00 3.86 100.00   0.00   0.00   0.00   0.00  -  -  -    85  19 159.45 0.775   0x0  0x0   0  14.758
    16   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    36   -  10.90     -     -  0x0   -       -
    17   CPU0   -   -  2295  2400 100.00 3.85 100.00   0.00   0.00   0.00   0.00  -  -  -    84  20 159.38 0.775   0x0  0x0   0  14.613
    17   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    36   -  10.81     -     -  0x0   -       -
    18   CPU0   -   -  2295  2400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    85  19 159.65 0.775   0x0  0x0   0  14.559
    18   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    36   -  10.69     -     -  0x0   -       -
    19   CPU0   -   -  2295  2400 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    85  19 159.72 0.775   0x0  0x0   0  14.355
    19   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    36   -  10.78     -     -  0x0   -       -
    20   CPU0   -   -  2295  2400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    85  19 159.82 0.774   0x0  0x0   0  14.324
    20   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    36   -  10.64     -     -  0x0   -       -
    21   CPU0   -   -  2295  2400 100.00 3.93 100.00   0.00   0.00   0.00   0.00  -  -  -    85  19 159.88 0.775   0x0  0x0   0  14.266
    21   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    36   -  10.51     -     -  0x0   -       -
    22   CPU0   -   -  2295  2400 100.00 3.93 100.00   0.00   0.00   0.00   0.00  -  -  -    85  19 159.72 0.775   0x0  0x0   0  14.184
    22   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.56     -     -  0x0   -       -
    23   CPU0   -   -  2295  2400 100.00 3.93 100.00   0.00   0.00   0.00   0.00  -  -  -    86  18 159.99 0.774   0x0  0x0   0  14.129
    23   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    36   -  10.50     -     -  0x0   -       -
    24   CPU0   -   -  2294  2400 100.00 3.88 100.00   0.00   0.00   0.00   0.00  -  -  -    85  19 159.42 0.775   0x0  0x0   0  14.086
    24   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    36   -  10.70     -     -  0x0   -       -
    25   CPU0   -   -  2295  2400 100.00 3.88 100.00   0.00   0.00   0.00   0.00  -  -  -    85  19 159.23 0.775   0x0  0x0   0  13.887
    25   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    36   -  10.66     -     -  0x0   -       -
    26   CPU0   -   -  2295  2400 100.00 3.87 100.00   0.00   0.00   0.00   0.00  -  -  -    85  19 159.42 0.774   0x0  0x0   0  13.852
    26   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    36   -  10.76     -     -  0x0   -       -
    27   CPU0   -   -  2295  2400 100.00 3.87 100.00   0.00   0.00   0.00   0.00  -  -  -    86  18 159.35 0.775   0x0  0x0   0  13.793
    27   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.73     -     -  0x0   -       -
    28   CPU0   -   -  2295  2400 100.00 3.86 100.00   0.00   0.00   0.00   0.00  -  -  -    86  18 159.30 0.775   0x0  0x0   0  13.559
    28   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.76     -     -  0x0   -       -
    29   CPU0   -   -  2295  2400 100.00 3.85 100.00   0.00   0.00   0.00   0.00  -  -  -    85  19 159.28 0.775   0x0  0x0   0  13.574
    29   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.79     -     -  0x0   -       -
    30   CPU0   -   -  2294  2400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    86  18 159.35 0.775   0x0  0x0   0  13.484
    30   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.61     -     -  0x0   -       -
    31   CPU0   -   -  2295  2400 100.00 3.92 100.00   0.00   0.00   0.00   0.00  -  -  -    86  18 160.31 0.774   0x0  0x0   0  13.539
    31   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.55     -     -  0x0   -       -
    32   CPU0   -   -  2294  2400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    86  18 159.85 0.775   0x0  0x0   0  13.492
    32   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.64     -     -  0x0   -       -
    33   CPU0   -   -  2295  2400 100.00 3.91 100.00   0.00   0.00   0.00   0.00  -  -  -    86  18 159.75 0.774   0x0  0x0   0  13.359
    33   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    36   -  10.56     -     -  0x0   -       -
    34   CPU0   -   -  2295  2400 100.00 3.92 100.00   0.00   0.00   0.00   0.00  -  -  -    86  18 160.01 0.774   0x0  0x0   0  13.316
    34   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.58     -     -  0x0   -       -
    35   CPU0   -   -  2295  2400 100.00 3.92 100.00   0.00   0.00   0.00   0.00  -  -  -    86  18 160.00 0.775   0x0  0x0   0  13.301
    35   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.57     -     -  0x0   -       -
    36   CPU0   -   -  2295  2400 100.00 3.92 100.00   0.00   0.00   0.00   0.00  -  -  -    86  18 160.05 0.775   0x0  0x0   0  13.145
    36   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.55     -     -  0x0   -       -
    37   CPU0   -   -  2295  2400 100.00 3.93 100.00   0.00   0.00   0.00   0.00  -  -  -    87  17 160.29 0.774   0x0  0x0   0  13.113
    37   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.55     -     -  0x0   -       -
    38   CPU0   -   -  2295  2400 100.00 3.91 100.00   0.00   0.00   0.00   0.00  -  -  -    86  18 160.18 0.775   0x0  0x0   0  12.973
    38   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.61     -     -  0x0   -       -
    39   CPU0   -   -  2295  2400 100.00 3.93 100.00   0.00   0.00   0.00   0.00  -  -  -    87  17 160.01 0.774   0x0  0x0   0  12.941
    39   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.55     -     -  0x0   -       -
    40   CPU0   -   -  2294  2400 100.00 3.93 100.00   0.00   0.00   0.00   0.00  -  -  -    87  17 160.28 0.774   0x0  0x0   0  12.766
    40   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.59     -     -  0x0   -       -
    41   CPU0   -   -  2295  2400 100.00 3.92 100.00   0.00   0.00   0.00   0.00  -  -  -    87  17 160.12 0.774   0x0  0x0   0  12.691
    41   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.58     -     -  0x0   -       -
    42   CPU0   -   -  2295  2400 100.00 3.93 100.00   0.00   0.00   0.00   0.00  -  -  -    87  17 160.19 0.774   0x0  0x0   0  12.508
    42   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.56     -     -  0x0   -       -
    43   CPU0   -   -  2295  2400 100.00 3.92 100.00   0.00   0.00   0.00   0.00  -  -  -    87  17 160.44 0.774   0x0  0x0   0  12.469
    43   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.57     -     -  0x0   -       -
    44   CPU0   -   -  2295  2400 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    87  17 160.04 0.774   0x0  0x0   0  12.621
    44   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.66     -     -  0x0   -       -
    45   CPU0   -   -  2295  2400 100.00 3.92 100.00   0.00   0.00   0.00   0.00  -  -  -    87  17 160.40 0.774   0x0  0x0   0  12.562
    45   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.60     -     -  0x0   -       -
    46   CPU0   -   -  2295  2400 100.00 3.92 100.00   0.00   0.00   0.00   0.00  -  -  -    87  17 160.30 0.774   0x0  0x0   0  12.469
    46   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.60     -     -  0x0   -       -
    47   CPU0   -   -  2295  2400 100.00 3.92 100.00   0.00   0.00   0.00   0.00  -  -  -    87  17 160.55 0.773   0x0  0x0   0  12.348
    47   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.61     -     -  0x0   -       -
    48   CPU0   -   -  2295  2400 100.00 3.92 100.00   0.00   0.00   0.00   0.00  -  -  -    87  17 160.49 0.774   0x0  0x0   0  12.512
    48   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.57     -     -  0x0   -       -
    49   CPU0   -   -  2295  2400 100.00 3.93 100.00   0.00   0.00   0.00   0.00  -  -  -    87  17 160.64 0.774   0x0  0x0   0  12.535
    49   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.59     -     -  0x0   -       -
    50   CPU0   -   -  2295  2400 100.00 3.93 100.00   0.00   0.00   0.00   0.00  -  -  -    88  16 160.73 0.773   0x0  0x0   0  12.238
    50   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.55     -     -  0x0   -       -
    51   CPU0   -   -  2295  2400 100.00 3.91 100.00   0.00   0.00   0.00   0.00  -  -  -    88  16 160.55 0.774   0x0  0x0   0  12.320
    51   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.59     -     -  0x0   -       -
    52   CPU0   -   -  2295  2400 100.00 3.93 100.00   0.00   0.00   0.00   0.00  -  -  -    87  17 160.61 0.773   0x0  0x0   0  12.199
    52   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.58     -     -  0x0   -       -
    53   CPU0   -   -  2295  2400 100.00 3.92 100.00   0.00   0.00   0.00   0.00  -  -  -    88  16 160.62 0.773   0x0  0x0   0  12.145
    53   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.58     -     -  0x0   -       -
^C
[11/29/23 21:19:26 UTC] PTU stopped.

controller-0:~#
```


## Sensors after load ~2-3mins after

```log
controller-0:~# ipmitool sensor | grep -e CPU_0_TEMP -e CPU0_Power -e SYS_FAN_1A -e CPU_CUPS
CPU_0_TEMP       | 75.000     | degrees C  | ok    | na        | na        | na        | 101.000   | 104.000   | na
CPU0_Power       | 161.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 12160.000  | RPM        | ok    | na        | 1120.000  | na        | na        | 39840.000 | na
CPU_CUPS         | 98.000     | percent    | ok    | na        | na        | na        | na        | 100.000   | na
controller-0:~#
```

## Test is success, observed temps rise and fan rpms rise with the load

## MEAKV-644
## Performance test PTU 3 - Core AVX2 with Turbo - MEAKV-644
## Run Core Intel® AVX-2 with power level 100% and Turbo on.
## sudo ./ptu -ct 4 -cp 100 -b 1

## Check sensors bofore starting load

```log
controller-0:~# ipmitool sensor | grep -e CPU_0_TEMP -e CPU0_Power -e SYS_FAN_1A -e CPU_CUPS
CPU_0_TEMP       | 45.000     | degrees C  | ok    | na        | na        | na        | 101.000   | 104.000   | na
CPU0_Power       | 61.000     | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 9600.000   | RPM        | ok    | na        | 1120.000  | na        | na        | 39840.000 | na
CPU_CUPS         | 3.000      | percent    | ok    | na        | na        | na        | na        | 100.000   | na
controller-0:~#
```

## load Intiated

```log
controller-0:~# /home/XXXXXX/ptu -ct 4 -cp 100 -b 1

Command: /home/XXXXXX/ptu -ct 4 -cp 100 -b 1

Intel(R) Power Thermal Utility - Server Edition v2.3.1
Release Date: 12/04/2020
Copyright (C) 2020 Intel Corporation. All rights reserved.
Intel Confidential

/dev/ptusys: No such file or directory
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> System Info:                   <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Host Name:                           controller-0
Host IP:                             169.254.202.1
OS Name:                             CentOS Linux 7 (Core)
Kernel Version:                      Linux 5.10.112-200.25.tis.rt.el7.x86_64 #1 SMP PREEMPT_RT Wed May 3 22:37:28 EDT 2023
BIOS Version:                        American Megatrends Inc., 2.06, 06/28/2021
Processor(s):                        1 Processor(s) Installed.
DIMM(s):                             6 DIMM(s) Installed.
Total System Memory:                 95465 MB
Available System Memory:             54613 MB


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Processor: [CPU_0]             <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU ID:                              0x00050657 (Family 6 Model 55h Stepping 7)
CPU Brand Name:                      Intel(R) Xeon(R) Gold 6212U CPU @ 2.40GHz
CPU Code Name:                       Cascade Lake
CPU Type:                            Production Part
CPU Segment:                         Server
CPU PPIN:                            0x66AAEDBA78DF031D
CPU Base Frequency:                  1500 MHz
CPU Minimum Frequency:               1000 MHz
CPU Maximum Turbo Frequency:         3900 MHz
Uncore Minimum Frequency:            1200 MHz
Uncore Maximum Frequency:            2400 MHz
L2 Cache:                            24 x 1024 KB
L3 Cache:                            36608 KB
Hyper-threading:                     Enabled
Microcode Update Revision:           0x05003102
Number of Physcial Core(s):          24
Number of Logical Core(s):           48
Turbo Boost:                         Enabled
Turbo Boost Frequency:
 IA/SSE:
    1 -  2 Cores (Fused/Resolved):   3900 / 3900 (MHz)
    3 -  4 Cores (Fused/Resolved):   3700 / 3700 (MHz)
    5 - 16 Cores (Fused/Resolved):   3600 / 3600 (MHz)
   17 - 20 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   21 - 24 Cores (Fused/Resolved):   3100 / 3100 (MHz)
 AVX2:
    1 -  2 Cores (Fused/Resolved):   3700 / 3700 (MHz)
    3 -  4 Cores (Fused/Resolved):   3500 / 3500 (MHz)
    5 -  8 Cores (Fused/Resolved):   3400 / 3400 (MHz)
    9 - 12 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   13 - 16 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   17 - 20 Cores (Fused/Resolved):   2700 / 2700 (MHz)
   21 - 24 Cores (Fused/Resolved):   2600 / 2600 (MHz)
 AVX-512:
    1 -  2 Cores (Fused/Resolved):   3700 / 3700 (MHz)
    3 -  4 Cores (Fused/Resolved):   3500 / 3500 (MHz)
    5 -  8 Cores (Fused/Resolved):   3400 / 3400 (MHz)
    9 - 12 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   13 - 16 Cores (Fused/Resolved):   2600 / 2600 (MHz)
   17 - 20 Cores (Fused/Resolved):   2400 / 2400 (MHz)
   21 - 24 Cores (Fused/Resolved):   2300 / 2300 (MHz)
OVOLT_OVRD Supported:                0
OVOLT_OVRD Disabled:                 1
Platform ID:                         0x0
Platform Info:                       0x70A2CF2810F00000
Thermal Design Power (TDP):          165 W
Power Limit 1 - Long Duration:       Enabled, Clamp OFF, Power = 165 W, Time = 1.00 sec
Power Limit 2 - Short Duration:      Enabled, Clamp ON , Power = 198 W, Time = 1.95 sec
Config TDP Level Supported:          2
Config TDP Level 1:                  165.0 W (78.0 W - 413.0 W), 1500 MHz
Config TDP Level 2:                  165.0 W (78.0 W - 413.0 W), 1500 MHz
Current Config TDP Level:            NominalLevel 2
Tprochot:                            104 C
TCC Offset:                          0
CAPID0:                              0x001881F8
CAPID1:                              0x040000C3
CAPID2:                              0x13800000
CAPID3:                              0x00004000
CAPID4:                              0x24000EC0
CAPID5:                              0x660001FB
CAPID6:                              0x0FFDFFBF
CAPID7:                              0x07FDFFB7


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Memory: [MEM_0]                <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Number of DIMM(s):                   6
Number of Active Channel(s):         6
DRAM Power Meter Disabled:           0
DRAM RAPL Disabled:                  0
DRAM TDP Power:                      Min = 4.5 W, Max = 27.8 W, Time = 32.00 sec
DRAM / NVDIMM Info:
  MC 0, Chnl 0, Slot 0:              tempLo: 84 C, tempMid: 93 C, tempHi: 100 C
  MC 0, Chnl 1, Slot 0:              tempLo: 84 C, tempMid: 93 C, tempHi: 100 C
  MC 0, Chnl 2, Slot 0:              tempLo: 84 C, tempMid: 93 C, tempHi: 100 C
  MC 1, Chnl 3, Slot 0:              tempLo: 84 C, tempMid: 93 C, tempHi: 100 C
  MC 1, Chnl 4, Slot 0:              tempLo: 84 C, tempMid: 93 C, tempHi: 100 C
  MC 1, Chnl 5, Slot 0:              tempLo: 84 C, tempMid: 93 C, tempHi: 100 C


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Platform Controller Hub: [PCH] <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
PCH Device ID:                       8086:A1C1 (LBG-1G)
PCH Stepping:                        9
PCH Thermal Sensor Enable:           1
PCH Hot Level (PHL):                 -50
PCH Catastrophic Trip Point (CTRIP): 106


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> PTU Current Settings:          <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU Test Selected:                   4
MEM Test Selected:                   0
CPU Mask:                            0xFFFF
CPU Core Mask:                       0xFFFFFFFFFFFFFFFF
CPU Thread Mask:                     0xFF
MEM Mask:                            0xFFFF
MEM Core Mask:                       0xFFFFFFFFFFFFFFFF
MEM Thread Mask:                     0xFF
Core Power Level:                    100
Memory Power Level:                  100
Turbo Enabled:                       Yes
AVX Test Level:                      1
Pmax Pre-sync:                       5000 ms
Pmax Post-sync:                      3000 ms
Pmax Idle:                           2000 ms
Run Time:                            0 (Forever)
PTU Mon CPU Mask:                    0xFFFFFFFF
PTU Mon Core Mask:                   0xFFFFFFFFFFFFFFFF
PTU Mon MEM Mask:                    0xFFFFFFFF
PTU Mon Filter Mask:                 0x1F
PTU Mon Update Interval:             1000000 usec
PTU Mon Long Level:                  0
PTU Mon Timestamp:                   No
Log Enabled:                         No
Log Directory:                       /root/ptu/log
Log File Prefix:                     <timestamp>
Log Message File:                    <timestamp>_ptumsg.txt
Log Monitor File:                    <timestamp>_ptumon.txt
CSV Enabled:                         No
PTU License Auto Accept:             No
PTU Driver Loaded:                   No

[11/29/23 21:23:54 UTC] PTU started.

Press <Ctrl-C> to stop.


CPU_0: [IDLE] CFreq=2300, UFreq=2400, Util=7.57, IPC=0.91, Temp=60, DTS=44, Power=66.3, Volt=0.777
CPU_0: [TESTCFG] TestSel=4 (Core AVX2), CoreMask=0xFFFFFFFFFFFFFFFF, ThreadMask=0xFF, PwrLevel=100, Turbo=1
CPU_0: [RUNNING] CFreq=2247, UFreq=1300, Util=100.00, IPC=3.92, Temp=75, DTS=29, Power=164.4, Volt=0.771

```

## ptu -mon

```log
controller-0:~# /home/XXXXXX/ptu -mon

Command: /home/XXXXXX/ptu -mon

Intel(R) Power Thermal Utility - Server Edition v2.3.1
Release Date: 12/04/2020
Copyright (C) 2020 Intel Corporation. All rights reserved.
Intel Confidential

/dev/ptusys: No such file or directory
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> System Info:                   <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Host Name:                           controller-0
Host IP:                             169.254.202.1
OS Name:                             CentOS Linux 7 (Core)
Kernel Version:                      Linux 5.10.112-200.25.tis.rt.el7.x86_64 #1 SMP PREEMPT_RT Wed May 3 22:37:28 EDT 2023
BIOS Version:                        American Megatrends Inc., 2.06, 06/28/2021
Processor(s):                        1 Processor(s) Installed.
DIMM(s):                             6 DIMM(s) Installed.
Total System Memory:                 95465 MB
Available System Memory:             54625 MB


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Processor: [CPU_0]             <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU ID:                              0x00050657 (Family 6 Model 55h Stepping 7)
CPU Brand Name:                      Intel(R) Xeon(R) Gold 6212U CPU @ 2.40GHz
CPU Code Name:                       Cascade Lake
CPU Type:                            Production Part
CPU Segment:                         Server
CPU PPIN:                            0x66AAEDBA78DF031D
CPU Base Frequency:                  1500 MHz
CPU Minimum Frequency:               1000 MHz
CPU Maximum Turbo Frequency:         3900 MHz
Uncore Minimum Frequency:            1200 MHz
Uncore Maximum Frequency:            2400 MHz
L2 Cache:                            24 x 1024 KB
L3 Cache:                            36608 KB
Hyper-threading:                     Enabled
Microcode Update Revision:           0x05003102
Number of Physcial Core(s):          24
Number of Logical Core(s):           48
Turbo Boost:                         Enabled
Turbo Boost Frequency:
 IA/SSE:
    1 -  2 Cores (Fused/Resolved):   3900 / 3900 (MHz)
    3 -  4 Cores (Fused/Resolved):   3700 / 3700 (MHz)
    5 - 16 Cores (Fused/Resolved):   3600 / 3600 (MHz)
   17 - 20 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   21 - 24 Cores (Fused/Resolved):   3100 / 3100 (MHz)
 AVX2:
    1 -  2 Cores (Fused/Resolved):   3700 / 3700 (MHz)
    3 -  4 Cores (Fused/Resolved):   3500 / 3500 (MHz)
    5 -  8 Cores (Fused/Resolved):   3400 / 3400 (MHz)
    9 - 12 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   13 - 16 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   17 - 20 Cores (Fused/Resolved):   2700 / 2700 (MHz)
   21 - 24 Cores (Fused/Resolved):   2600 / 2600 (MHz)
 AVX-512:
    1 -  2 Cores (Fused/Resolved):   3700 / 3700 (MHz)
    3 -  4 Cores (Fused/Resolved):   3500 / 3500 (MHz)
    5 -  8 Cores (Fused/Resolved):   3400 / 3400 (MHz)
    9 - 12 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   13 - 16 Cores (Fused/Resolved):   2600 / 2600 (MHz)
   17 - 20 Cores (Fused/Resolved):   2400 / 2400 (MHz)
   21 - 24 Cores (Fused/Resolved):   2300 / 2300 (MHz)
OVOLT_OVRD Supported:                0
OVOLT_OVRD Disabled:                 1
Platform ID:                         0x0
Platform Info:                       0x70A2CF2810F00000
Thermal Design Power (TDP):          165 W
Power Limit 1 - Long Duration:       Enabled, Clamp OFF, Power = 165 W, Time = 1.00 sec
Power Limit 2 - Short Duration:      Enabled, Clamp ON , Power = 198 W, Time = 1.95 sec
Config TDP Level Supported:          2
Config TDP Level 1:                  165.0 W (78.0 W - 413.0 W), 1500 MHz
Config TDP Level 2:                  165.0 W (78.0 W - 413.0 W), 1500 MHz
Current Config TDP Level:            NominalLevel 2
Tprochot:                            104 C
TCC Offset:                          0
CAPID0:                              0x001881F8
CAPID1:                              0x040000C3
CAPID2:                              0x13800000
CAPID3:                              0x00004000
CAPID4:                              0x24000EC0
CAPID5:                              0x660001FB
CAPID6:                              0x0FFDFFBF
CAPID7:                              0x07FDFFB7


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Memory: [MEM_0]                <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Number of DIMM(s):                   6
Number of Active Channel(s):         6
DRAM Power Meter Disabled:           0
DRAM RAPL Disabled:                  0
DRAM TDP Power:                      Min = 4.5 W, Max = 27.8 W, Time = 32.00 sec
DRAM / NVDIMM Info:
  MC 0, Chnl 0, Slot 0:              tempLo: 84 C, tempMid: 93 C, tempHi: 100 C
  MC 0, Chnl 1, Slot 0:              tempLo: 84 C, tempMid: 93 C, tempHi: 100 C
  MC 0, Chnl 2, Slot 0:              tempLo: 84 C, tempMid: 93 C, tempHi: 100 C
  MC 1, Chnl 3, Slot 0:              tempLo: 84 C, tempMid: 93 C, tempHi: 100 C
  MC 1, Chnl 4, Slot 0:              tempLo: 84 C, tempMid: 93 C, tempHi: 100 C
  MC 1, Chnl 5, Slot 0:              tempLo: 84 C, tempMid: 93 C, tempHi: 100 C


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Platform Controller Hub: [PCH] <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
PCH Device ID:                       8086:A1C1 (LBG-1G)
PCH Stepping:                        9
PCH Thermal Sensor Enable:           1
PCH Hot Level (PHL):                 -50
PCH Catastrophic Trip Point (CTRIP): 106


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> PTU Current Settings:          <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU Test Selected:                   0
MEM Test Selected:                   0
CPU Mask:                            0xFFFF
CPU Core Mask:                       0xFFFFFFFFFFFFFFFF
CPU Thread Mask:                     0xFF
MEM Mask:                            0xFFFF
MEM Core Mask:                       0xFFFFFFFFFFFFFFFF
MEM Thread Mask:                     0xFF
Core Power Level:                    100
Memory Power Level:                  100
Turbo Enabled:                       No
AVX Test Level:                      1
Pmax Pre-sync:                       5000 ms
Pmax Post-sync:                      3000 ms
Pmax Idle:                           2000 ms
Run Time:                            0 (Forever)
PTU Mon CPU Mask:                    0xFFFFFFFF
PTU Mon Core Mask:                   0xFFFFFFFFFFFFFFFF
PTU Mon MEM Mask:                    0xFFFFFFFF
PTU Mon Filter Mask:                 0x1F
PTU Mon Update Interval:             1000000 usec
PTU Mon Long Level:                  0
PTU Mon Timestamp:                   No
Log Enabled:                         No
Log Directory:                       /root/ptu/log
Log File Prefix:                     <timestamp>
Log Message File:                    <timestamp>_ptumsg.txt
Log Monitor File:                    <timestamp>_ptumon.txt
CSV Enabled:                         No
PTU License Auto Accept:             No
PTU Driver Loaded:                   No

[11/29/23 21:25:06 UTC] PTU started.

Press <Ctrl-C> to stop.


 Index Device Cor Thr CFreq UFreq   Util  IPC     C0     C1     C6    PC2    PC6 MC Ch Sl  Temp DTS  Power  Volt TStat TLog #TL TMargin
     0   CPU0   -   -  2241  1300 100.00 3.88  99.32   0.68   0.00   0.00   0.00  -  -  -    88  16 164.51 0.764   0x0  0x0   0  12.492
     0   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.69     -     -  0x0   -       -
     1   CPU0   -   -  2239  1300 100.00 3.88  99.37   0.63   0.00   0.00   0.00  -  -  -    89  15 164.54 0.763   0x0  0x0   0  12.406
     1   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.63     -     -  0x0   -       -
     2   CPU0   -   -  2235  1300 100.00 3.89  99.36   0.64   0.00   0.00   0.00  -  -  -    89  15 164.49 0.774   0x0  0x0   0  12.320
     2   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.65     -     -  0x0   -       -
     3   CPU0   -   -  2233  1300 100.00 3.89  99.39   0.61   0.00   0.00   0.00  -  -  -    89  15 164.41 0.775   0x0  0x0   0  12.336
     3   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.70     -     -  0x0   -       -
     4   CPU0   -   -  2226  1300 100.00 3.92  99.43   0.57   0.00   0.00   0.00  -  -  -    89  15 164.63 0.774   0x0  0x0   0  12.312
     4   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.61     -     -  0x0   -       -
     5   CPU0   -   -  2226  1300 100.00 3.92  99.40   0.60   0.00   0.00   0.00  -  -  -    89  15 164.49 0.763   0x0  0x0   0  12.309
     5   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.58     -     -  0x0   -       -
     6   CPU0   -   -  2225  1300 100.00 3.92  99.48   0.52   0.00   0.00   0.00  -  -  -    88  16 164.54 0.763   0x0  0x0   0  12.176
     6   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.54     -     -  0x0   -       -
     7   CPU0   -   -  2232  1300 100.00 3.90  99.44   0.56   0.00   0.00   0.00  -  -  -    89  15 164.42 0.775   0x0  0x0   0  12.145
     7   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.60     -     -  0x0   -       -
     8   CPU0   -   -  2241  1300 100.00 3.86  99.36   0.64   0.00   0.00   0.00  -  -  -    89  15 164.68 0.763   0x0  0x0   0  11.945
     8   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.71     -     -  0x0   -       -
     9   CPU0   -   -  2234  1300 100.00 3.90  99.34   0.66   0.00   0.00   0.00  -  -  -    89  15 164.47 0.763   0x0  0x0   0  11.957
     9   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.64     -     -  0x0   -       -
    10   CPU0   -   -  2236  1300 100.00 3.88  99.34   0.66   0.00   0.00   0.00  -  -  -    89  15 164.52 0.763   0x0  0x0   0  11.832
    10   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.66     -     -  0x0   -       -
    11   CPU0   -   -  2231  1300 100.00 3.90  99.39   0.61   0.00   0.00   0.00  -  -  -    89  15 163.23 0.774   0x0  0x0   0  11.754
    11   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.61     -     -  0x0   -       -
    12   CPU0   -   -  2224  1300 100.00 3.92  99.47   0.53   0.00   0.00   0.00  -  -  -    89  15 165.72 0.763   0x0  0x0   0  11.750
    12   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.54     -     -  0x0   -       -
    13   CPU0   -   -  2221  1300 100.00 3.93  99.50   0.50   0.00   0.00   0.00  -  -  -    89  15 164.52 0.774   0x0  0x0   0  11.754
    13   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.55     -     -  0x0   -       -
    14   CPU0   -   -  2223  1300 100.00 3.92  99.48   0.52   0.00   0.00   0.00  -  -  -    89  15 164.57 0.774   0x0  0x0   0  11.703
    14   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.56     -     -  0x0   -       -
    15   CPU0   -   -  2226  1300 100.00 3.92  99.43   0.57   0.00   0.00   0.00  -  -  -    89  15 164.63 0.762   0x0  0x0   0  11.555
    15   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.58     -     -  0x0   -       -
    16   CPU0   -   -  2223  1300 100.00 3.92  99.53   0.47   0.00   0.00   0.00  -  -  -    90  14 164.45 0.762   0x0  0x0   0  11.465
    16   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.53     -     -  0x0   -       -
    17   CPU0   -   -  2225  1300 100.00 3.92  99.46   0.54   0.00   0.00   0.00  -  -  -    90  14 164.40 0.774   0x0  0x0   0  11.488
    17   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.58     -     -  0x0   -       -
    18   CPU0   -   -  2223  1300 100.00 3.92  99.50   0.50   0.00   0.00   0.00  -  -  -    90  14 164.70 0.774   0x0  0x0   0  11.402
    18   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.60     -     -  0x0   -       -
    19   CPU0   -   -  2231  1300 100.00 3.89  99.43   0.57   0.00   0.00   0.00  -  -  -    90  14 164.47 0.763   0x0  0x0   0  11.168
    19   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.68     -     -  0x0   -       -
    20   CPU0   -   -  2239  1300 100.00 3.85  99.31   0.69   0.00   0.00   0.00  -  -  -    90  14 164.59 0.763   0x0  0x0   0  11.035
    20   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.71     -     -  0x0   -       -
    21   CPU0   -   -  2235  1300 100.00 3.88  99.38   0.62   0.00   0.00   0.00  -  -  -    90  14 164.53 0.774   0x0  0x0   0  10.922
    21   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.64     -     -  0x0   -       -
    22   CPU0   -   -  2234  1300 100.00 3.88  99.39   0.61   0.00   0.00   0.00  -  -  -    90  14 164.44 0.762   0x0  0x0   0  10.938
    22   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.63     -     -  0x0   -       -
    23   CPU0   -   -  2234  1300 100.00 3.89  99.33   0.67   0.00   0.00   0.00  -  -  -    90  14 164.46 0.763   0x0  0x0   0  10.848
    23   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.65     -     -  0x0   -       -
    24   CPU0   -   -  2235  1300 100.00 3.89  99.36   0.64   0.00   0.00   0.00  -  -  -    90  14 164.57 0.763   0x0  0x0   0  10.793
    24   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.66     -     -  0x0   -       -
    25   CPU0   -   -  2232  1300 100.00 3.89  99.39   0.61   0.00   0.00   0.00  -  -  -    90  14 164.64 0.762   0x0  0x0   0  10.738
    25   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.59     -     -  0x0   -       -
    26   CPU0   -   -  2231  1300 100.00 3.90  99.38   0.62   0.00   0.00   0.00  -  -  -    90  14 164.43 0.762   0x0  0x0   0  10.730
    26   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.66     -     -  0x0   -       -
    27   CPU0   -   -  2236  1300 100.00 3.88  99.32   0.68   0.00   0.00   0.00  -  -  -    90  14 164.59 0.763   0x0  0x0   0  10.695
    27   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.68     -     -  0x0   -       -
    28   CPU0   -   -  2233  1300 100.00 3.87  99.40   0.60   0.00   0.00   0.00  -  -  -    90  14 164.49 0.774   0x0  0x0   0  10.609
    28   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.76     -     -  0x0   -       -
    29   CPU0   -   -  2224  1300 100.00 3.91  99.48   0.52   0.00   0.00   0.00  -  -  -    90  14 164.46 0.774   0x0  0x0   0  10.660
    29   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.57     -     -  0x0   -       -
    30   CPU0   -   -  2222  1300 100.00 3.92  99.49   0.51   0.00   0.00   0.00  -  -  -    90  14 164.60 0.762   0x0  0x0   0  10.648
    30   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.59     -     -  0x0   -       -
    31   CPU0   -   -  2226  1300 100.00 3.90  99.42   0.58   0.00   0.00   0.00  -  -  -    90  14 164.43 0.762   0x0  0x0   0  10.586
    31   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.66     -     -  0x0   -       -
    32   CPU0   -   -  2224  1300 100.00 3.91  99.52   0.48   0.00   0.00   0.00  -  -  -    90  14 164.61 0.773   0x0  0x0   0  10.480
    32   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.54     -     -  0x0   -       -
    33   CPU0   -   -  2223  1300 100.00 3.91  99.50   0.50   0.00   0.00   0.00  -  -  -    91  13 164.47 0.762   0x0  0x0   0  10.527
    33   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.77     -     -  0x0   -       -
    34   CPU0   -   -  2219  1300 100.00 3.93  99.54   0.46   0.00   0.00   0.00  -  -  -    91  13 164.52 0.762   0x0  0x0   0  10.535
    34   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.55     -     -  0x0   -       -
    35   CPU0   -   -  2221  1300 100.00 3.92  99.52   0.48   0.00   0.00   0.00  -  -  -    91  13 164.54 0.773   0x0  0x0   0  10.430
    35   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.63     -     -  0x0   -       -
    36   CPU0   -   -  2225  1300 100.00 3.91  99.44   0.56   0.00   0.00   0.00  -  -  -    91  13 164.46 0.762   0x0  0x0   0  10.398
    36   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.60     -     -  0x0   -       -
    37   CPU0   -   -  2222  1300 100.00 3.92  99.50   0.50   0.00   0.00   0.00  -  -  -    91  13 164.51 0.762   0x0  0x0   0  10.387
    37   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.54     -     -  0x0   -       -
    38   CPU0   -   -  2219  1300 100.00 3.93  99.54   0.46   0.00   0.00   0.00  -  -  -    91  13 164.51 0.773   0x0  0x0   0  10.277
    38   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.61     -     -  0x0   -       -
    39   CPU0   -   -  2231  1300 100.00 3.89  99.40   0.60   0.00   0.00   0.00  -  -  -    91  13 164.41 0.762   0x0  0x0   0  10.176
    39   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.64     -     -  0x0   -       -
    40   CPU0   -   -  2232  1300 100.00 3.88  99.42   0.58   0.00   0.00   0.00  -  -  -    91  13 164.70 0.762   0x0  0x0   0  10.035
    40   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.73     -     -  0x0   -       -
    41   CPU0   -   -  2231  1300 100.00 3.89  99.39   0.61   0.00   0.00   0.00  -  -  -    91  13 164.60 0.773   0x0  0x0   0   9.984
    41   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.67     -     -  0x0   -       -
    42   CPU0   -   -  2234  1300 100.00 3.86  99.36   0.64   0.00   0.00   0.00  -  -  -    91  13 164.42 0.762   0x0  0x0   0   9.930
    42   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.73     -     -  0x0   -       -
    43   CPU0   -   -  2221  1300 100.00 3.92  99.50   0.50   0.00   0.00   0.00  -  -  -    91  13 164.57 0.761   0x0  0x0   0   9.918
    43   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.65     -     -  0x0   -       -
    44   CPU0   -   -  2219  1300 100.00 3.92  99.58   0.42   0.00   0.00   0.00  -  -  -    91  13 164.49 0.773   0x0  0x0   0   9.996
    44   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.54     -     -  0x0   -       -
    45   CPU0   -   -  2217  1300 100.00 3.93  99.56   0.44   0.00   0.00   0.00  -  -  -    91  13 164.58 0.762   0x0  0x0   0   9.930
    45   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.52     -     -  0x0   -       -
    46   CPU0   -   -  2221  1300 100.00 3.92  99.50   0.50   0.00   0.00   0.00  -  -  -    91  13 164.41 0.762   0x0  0x0   0   9.801
    46   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.58     -     -  0x0   -       -
    47   CPU0   -   -  2232  1300 100.00 3.87  99.41   0.59   0.00   0.00   0.00  -  -  -    92  12 164.60 0.773   0x0  0x0   0   9.812
    47   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.69     -     -  0x0   -       -
    48   CPU0   -   -  2235  1300 100.00 3.87  99.40   0.60   0.00   0.00   0.00  -  -  -    92  12 164.45 0.774   0x0  0x0   0   9.523
    48   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.73     -     -  0x0   -       -
    49   CPU0   -   -  2233  1300 100.00 3.86  99.34   0.66   0.00   0.00   0.00  -  -  -    91  13 164.55 0.772   0x0  0x0   0   9.461
    49   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.75     -     -  0x0   -       -
    50   CPU0   -   -  2230  1300 100.00 3.89  99.39   0.61   0.00   0.00   0.00  -  -  -    92  12 164.54 0.774   0x0  0x0   0   9.574
    50   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.67     -     -  0x0   -       -
^C
[11/29/23 21:26:00 UTC] PTU stopped.

controller-0:~#
```

## check sensors after load 

```log
controller-0:~# ipmitool sensor | grep -e CPU_0_TEMP -e CPU0_Power -e SYS_FAN_1A -e CPU_CUPS
CPU_0_TEMP       | 79.000     | degrees C  | ok    | na        | na        | na        | 101.000   | 104.000   | na
CPU0_Power       | 164.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 12000.000  | RPM        | ok    | na        | 1120.000  | na        | na        | 39840.000 | na
CPU_CUPS         | 95.000     | percent    | ok    | na        | na        | na        | na        | 100.000   | na
controller-0:~#
```

## Observed temps raise and fans rpm raise with load - success

## MEAKV-645
## PTU 4 - Core AVX512 with Turbo
## sudo ./ptu -ct 5 -cp 100 -b 1


## Sensors before load

```log
controller-0:~# ipmitool sensor | grep -e CPU_0_TEMP -e CPU0_Power -e SYS_FAN_1A -e CPU_CUPS
CPU_0_TEMP       | 40.000     | degrees C  | ok    | na        | na        | na        | 101.000   | 104.000   | na
CPU0_Power       | 63.000     | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 9600.000   | RPM        | ok    | na        | 1120.000  | na        | na        | 39840.000 | na
CPU_CUPS         | 1.000      | percent    | ok    | na        | na        | na        | na        | 100.000   | na
controller-0:~#
```

## Initate load

```log
controller-0:~# /home/XXXXXX/ptu -ct 5 -cp 100 -b 1

Command: /home/XXXXXX/ptu -ct 5 -cp 100 -b 1

Intel(R) Power Thermal Utility - Server Edition v2.3.1
Release Date: 12/04/2020
Copyright (C) 2020 Intel Corporation. All rights reserved.
Intel Confidential

/dev/ptusys: No such file or directory
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> System Info:                   <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Host Name:                           controller-0
Host IP:                             169.254.202.1
OS Name:                             CentOS Linux 7 (Core)
Kernel Version:                      Linux 5.10.112-200.25.tis.rt.el7.x86_64 #1 SMP PREEMPT_RT Wed May 3 22:37:28 EDT 2023
BIOS Version:                        American Megatrends Inc., 2.06, 06/28/2021
Processor(s):                        1 Processor(s) Installed.
DIMM(s):                             6 DIMM(s) Installed.
Total System Memory:                 95465 MB
Available System Memory:             54625 MB


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Processor: [CPU_0]             <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU ID:                              0x00050657 (Family 6 Model 55h Stepping 7)
CPU Brand Name:                      Intel(R) Xeon(R) Gold 6212U CPU @ 2.40GHz
CPU Code Name:                       Cascade Lake
CPU Type:                            Production Part
CPU Segment:                         Server
CPU PPIN:                            0x66AAEDBA78DF031D
CPU Base Frequency:                  1500 MHz
CPU Minimum Frequency:               1000 MHz
CPU Maximum Turbo Frequency:         3900 MHz
Uncore Minimum Frequency:            1200 MHz
Uncore Maximum Frequency:            2400 MHz
L2 Cache:                            24 x 1024 KB
L3 Cache:                            36608 KB
Hyper-threading:                     Enabled
Microcode Update Revision:           0x05003102
Number of Physcial Core(s):          24
Number of Logical Core(s):           48
Turbo Boost:                         Enabled
Turbo Boost Frequency:
 IA/SSE:
    1 -  2 Cores (Fused/Resolved):   3900 / 3900 (MHz)
    3 -  4 Cores (Fused/Resolved):   3700 / 3700 (MHz)
    5 - 16 Cores (Fused/Resolved):   3600 / 3600 (MHz)
   17 - 20 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   21 - 24 Cores (Fused/Resolved):   3100 / 3100 (MHz)
 AVX2:
    1 -  2 Cores (Fused/Resolved):   3700 / 3700 (MHz)
    3 -  4 Cores (Fused/Resolved):   3500 / 3500 (MHz)
    5 -  8 Cores (Fused/Resolved):   3400 / 3400 (MHz)
    9 - 12 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   13 - 16 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   17 - 20 Cores (Fused/Resolved):   2700 / 2700 (MHz)
   21 - 24 Cores (Fused/Resolved):   2600 / 2600 (MHz)
 AVX-512:
    1 -  2 Cores (Fused/Resolved):   3700 / 3700 (MHz)
    3 -  4 Cores (Fused/Resolved):   3500 / 3500 (MHz)
    5 -  8 Cores (Fused/Resolved):   3400 / 3400 (MHz)
    9 - 12 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   13 - 16 Cores (Fused/Resolved):   2600 / 2600 (MHz)
   17 - 20 Cores (Fused/Resolved):   2400 / 2400 (MHz)
   21 - 24 Cores (Fused/Resolved):   2300 / 2300 (MHz)
OVOLT_OVRD Supported:                0
OVOLT_OVRD Disabled:                 1
Platform ID:                         0x0
Platform Info:                       0x70A2CF2810F00000
Thermal Design Power (TDP):          165 W
Power Limit 1 - Long Duration:       Enabled, Clamp OFF, Power = 165 W, Time = 1.00 sec
Power Limit 2 - Short Duration:      Enabled, Clamp ON , Power = 198 W, Time = 1.95 sec
Config TDP Level Supported:          2
Config TDP Level 1:                  165.0 W (78.0 W - 413.0 W), 1500 MHz
Config TDP Level 2:                  165.0 W (78.0 W - 413.0 W), 1500 MHz
Current Config TDP Level:            NominalLevel 2
Tprochot:                            104 C
TCC Offset:                          0
CAPID0:                              0x001881F8
CAPID1:                              0x040000C3
CAPID2:                              0x13800000
CAPID3:                              0x00004000
CAPID4:                              0x24000EC0
CAPID5:                              0x660001FB
CAPID6:                              0x0FFDFFBF
CAPID7:                              0x07FDFFB7


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Memory: [MEM_0]                <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Number of DIMM(s):                   6
Number of Active Channel(s):         6
DRAM Power Meter Disabled:           0
DRAM RAPL Disabled:                  0
DRAM TDP Power:                      Min = 4.5 W, Max = 27.8 W, Time = 32.00 sec
DRAM / NVDIMM Info:
  MC 0, Chnl 0, Slot 0:              tempLo: 84 C, tempMid: 93 C, tempHi: 100 C
  MC 0, Chnl 1, Slot 0:              tempLo: 84 C, tempMid: 93 C, tempHi: 100 C
  MC 0, Chnl 2, Slot 0:              tempLo: 84 C, tempMid: 93 C, tempHi: 100 C
  MC 1, Chnl 3, Slot 0:              tempLo: 84 C, tempMid: 93 C, tempHi: 100 C
  MC 1, Chnl 4, Slot 0:              tempLo: 84 C, tempMid: 93 C, tempHi: 100 C
  MC 1, Chnl 5, Slot 0:              tempLo: 84 C, tempMid: 93 C, tempHi: 100 C


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Platform Controller Hub: [PCH] <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
PCH Device ID:                       8086:A1C1 (LBG-1G)
PCH Stepping:                        9
PCH Thermal Sensor Enable:           1
PCH Hot Level (PHL):                 -50
PCH Catastrophic Trip Point (CTRIP): 106


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> PTU Current Settings:          <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU Test Selected:                   5
MEM Test Selected:                   0
CPU Mask:                            0xFFFF
CPU Core Mask:                       0xFFFFFFFFFFFFFFFF
CPU Thread Mask:                     0xFF
MEM Mask:                            0xFFFF
MEM Core Mask:                       0xFFFFFFFFFFFFFFFF
MEM Thread Mask:                     0xFF
Core Power Level:                    100
Memory Power Level:                  100
Turbo Enabled:                       Yes
AVX Test Level:                      1
Pmax Pre-sync:                       5000 ms
Pmax Post-sync:                      3000 ms
Pmax Idle:                           2000 ms
Run Time:                            0 (Forever)
PTU Mon CPU Mask:                    0xFFFFFFFF
PTU Mon Core Mask:                   0xFFFFFFFFFFFFFFFF
PTU Mon MEM Mask:                    0xFFFFFFFF
PTU Mon Filter Mask:                 0x1F
PTU Mon Update Interval:             1000000 usec
PTU Mon Long Level:                  0
PTU Mon Timestamp:                   No
Log Enabled:                         No
Log Directory:                       /root/ptu/log
Log File Prefix:                     <timestamp>
Log Message File:                    <timestamp>_ptumsg.txt
Log Monitor File:                    <timestamp>_ptumon.txt
CSV Enabled:                         No
PTU License Auto Accept:             No
PTU Driver Loaded:                   No

[11/29/23 21:32:17 UTC] PTU started.

Press <Ctrl-C> to stop.


CPU_0: [IDLE] CFreq=2296, UFreq=2400, Util=1.87, IPC=0.67, Temp=54, DTS=50, Power=64.0, Volt=0.779
CPU_0: [TESTCFG] TestSel=5 (Core AVX-512), CoreMask=0xFFFFFFFFFFFFFFFF, ThreadMask=0xFF, PwrLevel=100, Turbo=1
CPU_0: [RUNNING] CFreq=1709, UFreq=1200, Util=100.00, IPC=4.21, Temp=73, DTS=31, Power=164.5, Volt=0.703

```

## ptu -mon

```log
controller-0:~# /home/XXXXXX/ptu -mon

Command: /home/XXXXXX/ptu -mon

Intel(R) Power Thermal Utility - Server Edition v2.3.1
Release Date: 12/04/2020
Copyright (C) 2020 Intel Corporation. All rights reserved.
Intel Confidential

/dev/ptusys: No such file or directory
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> System Info:                   <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Host Name:                           controller-0
Host IP:                             169.254.202.1
OS Name:                             CentOS Linux 7 (Core)
Kernel Version:                      Linux 5.10.112-200.25.tis.rt.el7.x86_64 #1 SMP PREEMPT_RT Wed May 3 22:37:28 EDT 2023
BIOS Version:                        American Megatrends Inc., 2.06, 06/28/2021
Processor(s):                        1 Processor(s) Installed.
DIMM(s):                             6 DIMM(s) Installed.
Total System Memory:                 95465 MB
Available System Memory:             54617 MB


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Processor: [CPU_0]             <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU ID:                              0x00050657 (Family 6 Model 55h Stepping 7)
CPU Brand Name:                      Intel(R) Xeon(R) Gold 6212U CPU @ 2.40GHz
CPU Code Name:                       Cascade Lake
CPU Type:                            Production Part
CPU Segment:                         Server
CPU PPIN:                            0x66AAEDBA78DF031D
CPU Base Frequency:                  1500 MHz
CPU Minimum Frequency:               1000 MHz
CPU Maximum Turbo Frequency:         3900 MHz
Uncore Minimum Frequency:            1200 MHz
Uncore Maximum Frequency:            2400 MHz
L2 Cache:                            24 x 1024 KB
L3 Cache:                            36608 KB
Hyper-threading:                     Enabled
Microcode Update Revision:           0x05003102
Number of Physcial Core(s):          24
Number of Logical Core(s):           48
Turbo Boost:                         Enabled
Turbo Boost Frequency:
 IA/SSE:
    1 -  2 Cores (Fused/Resolved):   3900 / 3900 (MHz)
    3 -  4 Cores (Fused/Resolved):   3700 / 3700 (MHz)
    5 - 16 Cores (Fused/Resolved):   3600 / 3600 (MHz)
   17 - 20 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   21 - 24 Cores (Fused/Resolved):   3100 / 3100 (MHz)
 AVX2:
    1 -  2 Cores (Fused/Resolved):   3700 / 3700 (MHz)
    3 -  4 Cores (Fused/Resolved):   3500 / 3500 (MHz)
    5 -  8 Cores (Fused/Resolved):   3400 / 3400 (MHz)
    9 - 12 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   13 - 16 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   17 - 20 Cores (Fused/Resolved):   2700 / 2700 (MHz)
   21 - 24 Cores (Fused/Resolved):   2600 / 2600 (MHz)
 AVX-512:
    1 -  2 Cores (Fused/Resolved):   3700 / 3700 (MHz)
    3 -  4 Cores (Fused/Resolved):   3500 / 3500 (MHz)
    5 -  8 Cores (Fused/Resolved):   3400 / 3400 (MHz)
    9 - 12 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   13 - 16 Cores (Fused/Resolved):   2600 / 2600 (MHz)
   17 - 20 Cores (Fused/Resolved):   2400 / 2400 (MHz)
   21 - 24 Cores (Fused/Resolved):   2300 / 2300 (MHz)
OVOLT_OVRD Supported:                0
OVOLT_OVRD Disabled:                 1
Platform ID:                         0x0
Platform Info:                       0x70A2CF2810F00000
Thermal Design Power (TDP):          165 W
Power Limit 1 - Long Duration:       Enabled, Clamp OFF, Power = 165 W, Time = 1.00 sec
Power Limit 2 - Short Duration:      Enabled, Clamp ON , Power = 198 W, Time = 1.95 sec
Config TDP Level Supported:          2
Config TDP Level 1:                  165.0 W (78.0 W - 413.0 W), 1500 MHz
Config TDP Level 2:                  165.0 W (78.0 W - 413.0 W), 1500 MHz
Current Config TDP Level:            NominalLevel 2
Tprochot:                            104 C
TCC Offset:                          0
CAPID0:                              0x001881F8
CAPID1:                              0x040000C3
CAPID2:                              0x13800000
CAPID3:                              0x00004000
CAPID4:                              0x24000EC0
CAPID5:                              0x660001FB
CAPID6:                              0x0FFDFFBF
CAPID7:                              0x07FDFFB7


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Memory: [MEM_0]                <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Number of DIMM(s):                   6
Number of Active Channel(s):         6
DRAM Power Meter Disabled:           0
DRAM RAPL Disabled:                  0
DRAM TDP Power:                      Min = 4.5 W, Max = 27.8 W, Time = 32.00 sec
DRAM / NVDIMM Info:
  MC 0, Chnl 0, Slot 0:              tempLo: 84 C, tempMid: 93 C, tempHi: 100 C
  MC 0, Chnl 1, Slot 0:              tempLo: 84 C, tempMid: 93 C, tempHi: 100 C
  MC 0, Chnl 2, Slot 0:              tempLo: 84 C, tempMid: 93 C, tempHi: 100 C
  MC 1, Chnl 3, Slot 0:              tempLo: 84 C, tempMid: 93 C, tempHi: 100 C
  MC 1, Chnl 4, Slot 0:              tempLo: 84 C, tempMid: 93 C, tempHi: 100 C
  MC 1, Chnl 5, Slot 0:              tempLo: 84 C, tempMid: 93 C, tempHi: 100 C


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Platform Controller Hub: [PCH] <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
PCH Device ID:                       8086:A1C1 (LBG-1G)
PCH Stepping:                        9
PCH Thermal Sensor Enable:           1
PCH Hot Level (PHL):                 -50
PCH Catastrophic Trip Point (CTRIP): 106


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> PTU Current Settings:          <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU Test Selected:                   0
MEM Test Selected:                   0
CPU Mask:                            0xFFFF
CPU Core Mask:                       0xFFFFFFFFFFFFFFFF
CPU Thread Mask:                     0xFF
MEM Mask:                            0xFFFF
MEM Core Mask:                       0xFFFFFFFFFFFFFFFF
MEM Thread Mask:                     0xFF
Core Power Level:                    100
Memory Power Level:                  100
Turbo Enabled:                       No
AVX Test Level:                      1
Pmax Pre-sync:                       5000 ms
Pmax Post-sync:                      3000 ms
Pmax Idle:                           2000 ms
Run Time:                            0 (Forever)
PTU Mon CPU Mask:                    0xFFFFFFFF
PTU Mon Core Mask:                   0xFFFFFFFFFFFFFFFF
PTU Mon MEM Mask:                    0xFFFFFFFF
PTU Mon Filter Mask:                 0x1F
PTU Mon Update Interval:             1000000 usec
PTU Mon Long Level:                  0
PTU Mon Timestamp:                   No
Log Enabled:                         No
Log Directory:                       /root/ptu/log
Log File Prefix:                     <timestamp>
Log Message File:                    <timestamp>_ptumsg.txt
Log Monitor File:                    <timestamp>_ptumon.txt
CSV Enabled:                         No
PTU License Auto Accept:             No
PTU Driver Loaded:                   No

[11/29/23 21:33:01 UTC] PTU started.

Press <Ctrl-C> to stop.


 Index Device Cor Thr CFreq UFreq   Util  IPC     C0     C1     C6    PC2    PC6 MC Ch Sl  Temp DTS  Power  Volt TStat TLog #TL TMargin
     0   CPU0   -   -  1715  1200 100.00 4.22  99.69   0.31   0.00   0.00   0.00  -  -  -    83  21 164.45 0.711   0x0  0x0   0  16.531
     0   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    36   -  10.55     -     -  0x0   -       -
     1   CPU0   -   -  1709  1200 100.00 4.24  99.80   0.20   0.00   0.00   0.00  -  -  -    84  20 164.69 0.711   0x0  0x0   0  16.504
     1   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    36   -  10.50     -     -  0x0   -       -
     2   CPU0   -   -  1721  1200 100.00 4.20  99.64   0.36   0.00   0.00   0.00  -  -  -    84  20 164.47 0.711   0x0  0x0   0  16.242
     2   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    36   -  10.52     -     -  0x0   -       -
     3   CPU0   -   -  1715  1200 100.00 4.22  99.66   0.34   0.00   0.00   0.00  -  -  -    84  20 164.48 0.711   0x0  0x0   0  15.969
     3   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    36   -  10.52     -     -  0x0   -       -
     4   CPU0   -   -  1724  1200 100.00 4.19  99.55   0.45   0.00   0.00   0.00  -  -  -    84  20 164.60 0.711   0x0  0x0   0  15.797
     4   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    36   -  10.65     -     -  0x0   -       -
     5   CPU0   -   -  1711  1200 100.00 4.23  99.75   0.25   0.00   0.00   0.00  -  -  -    84  20 164.46 0.711   0x0  0x0   0  15.707
     5   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    36   -  10.54     -     -  0x0   -       -
     6   CPU0   -   -  1711  1200 100.00 4.23  99.72   0.28   0.00   0.00   0.00  -  -  -    85  19 164.57 0.711   0x0  0x0   0  15.645
     6   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    36   -  10.52     -     -  0x0   -       -
     7   CPU0   -   -  1706  1200 100.00 4.24  99.84   0.16   0.00   0.00   0.00  -  -  -    85  19 164.55 0.710   0x0  0x0   0  15.609
     7   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    36   -  10.48     -     -  0x0   -       -
     8   CPU0   -   -  1715  1200 100.00 4.22  99.68   0.32   0.00   0.00   0.00  -  -  -    85  19 164.38 0.710   0x0  0x0   0  15.352
     8   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    36   -  10.49     -     -  0x0   -       -
     9   CPU0   -   -  1711  1200 100.00 4.23  99.73   0.27   0.00   0.00   0.00  -  -  -    85  19 164.63 0.721   0x0  0x0   0  15.305
     9   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    36   -  10.49     -     -  0x0   -       -
    10   CPU0   -   -  1713  1200 100.00 4.23  99.71   0.29   0.00   0.00   0.00  -  -  -    85  19 164.40 0.710   0x0  0x0   0  15.191
    10   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    36   -  10.50     -     -  0x0   -       -
    11   CPU0   -   -  1710  1200 100.00 4.24  99.77   0.23   0.00   0.00   0.00  -  -  -    86  18 164.55 0.710   0x0  0x0   0  15.145
    11   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    36   -  10.49     -     -  0x0   -       -
    12   CPU0   -   -  1723  1200 100.00 4.20  99.60   0.40   0.00   0.00   0.00  -  -  -    86  18 164.45 0.710   0x0  0x0   0  14.895
    12   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    36   -  10.61     -     -  0x0   -       -
    13   CPU0   -   -  1728  1200 100.00 4.18  99.48   0.52   0.00   0.00   0.00  -  -  -    86  18 164.56 0.709   0x0  0x0   0  14.430
    13   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    36   -  10.55     -     -  0x0   -       -
    14   CPU0   -   -  1721  1200 100.00 4.20  99.63   0.37   0.00   0.00   0.00  -  -  -    86  18 164.58 0.709   0x0  0x0   0  14.301
    14   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    36   -  10.65     -     -  0x0   -       -
    15   CPU0   -   -  1734  1200 100.00 4.14  99.48   0.52   0.00   0.00   0.00  -  -  -    87  17 164.53 0.710   0x0  0x0   0  14.195
    15   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    36   -  10.71     -     -  0x0   -       -
    16   CPU0   -   -  1713  1200 100.00 4.22  99.71   0.29   0.00   0.00   0.00  -  -  -    87  17 164.51 0.709   0x0  0x0   0  14.266
    16   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    36   -  10.57     -     -  0x0   -       -
    17   CPU0   -   -  1709  1200 100.00 4.23  99.77   0.23   0.00   0.00   0.00  -  -  -    87  17 164.48 0.709   0x0  0x0   0  14.176
    17   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    36   -  10.57     -     -  0x0   -       -
    18   CPU0   -   -  1709  1200 100.00 4.23  99.76   0.24   0.00   0.00   0.00  -  -  -    86  18 164.64 0.708   0x0  0x0   0  14.039
    18   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    36   -  10.57     -     -  0x0   -       -
    19   CPU0   -   -  1710  1200 100.00 4.22  99.74   0.26   0.00   0.00   0.00  -  -  -    87  17 164.51 0.720   0x0  0x0   0  14.102
    19   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    36   -  10.62     -     -  0x0   -       -
    20   CPU0   -   -  1727  1200 100.00 4.17  99.53   0.47   0.00   0.00   0.00  -  -  -    87  17 164.44 0.720   0x0  0x0   0  13.758
    20   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    36   -  10.65     -     -  0x0   -       -
    21   CPU0   -   -  1731  1200 100.00 4.18  99.47   0.53   0.00   0.00   0.00  -  -  -    88  16 164.53 0.720   0x0  0x0   0  13.516
    21   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    36   -  10.58     -     -  0x0   -       -
    22   CPU0   -   -  1732  1200 100.00 4.16  99.45   0.55   0.00   0.00   0.00  -  -  -    88  16 164.65 0.709   0x0  0x0   0  13.324
    22   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    36   -  10.73     -     -  0x0   -       -
    23   CPU0   -   -  1724  1200 100.00 4.19  99.55   0.45   0.00   0.00   0.00  -  -  -    87  17 164.43 0.709   0x0  0x0   0  13.168
    23   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    36   -  10.61     -     -  0x0   -       -
    24   CPU0   -   -  1739  1200 100.00 4.13  99.42   0.58   0.00   0.00   0.00  -  -  -    88  16 164.47 0.709   0x0  0x0   0  13.199
    24   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    36   -  10.79     -     -  0x0   -       -
    25   CPU0   -   -  1734  1200 100.00 4.16  99.47   0.53   0.00   0.00   0.00  -  -  -    88  16 164.52 0.720   0x0  0x0   0  12.824
    25   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    36   -  10.68     -     -  0x0   -       -
    26   CPU0   -   -  1735  1200 100.00 4.15  99.43   0.57   0.00   0.00   0.00  -  -  -    88  16 164.52 0.720   0x0  0x0   0  12.879
    26   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    36   -  10.73     -     -  0x0   -       -
    27   CPU0   -   -  1739  1200 100.00 4.12  99.43   0.57   0.00   0.00   0.00  -  -  -    89  15 162.60 0.720   0x0  0x0   0  12.648
    27   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    36   -  10.71     -     -  0x0   -       -
    28   CPU0   -   -  1733  1200 100.00 4.16  99.48   0.52   0.00   0.00   0.00  -  -  -    88  16 166.55 0.720   0x0  0x0   0  12.441
    28   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    36   -  10.69     -     -  0x0   -       -
    29   CPU0   -   -  1741  1200 100.00 4.14  99.38   0.62   0.00   0.00   0.00  -  -  -    88  16 164.44 0.720   0x0  0x0   0  12.469
    29   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    36   -  10.66     -     -  0x0   -       -
    30   CPU0   -   -  1735  1200 100.00 4.16  99.45   0.55   0.00   0.00   0.00  -  -  -    88  16 164.62 0.708   0x0  0x0   0  12.273
    30   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    36   -  10.66     -     -  0x0   -       -
    31   CPU0   -   -  1705  1200 100.00 4.24  99.84   0.16   0.00   0.00   0.00  -  -  -    88  16 164.40 0.708   0x0  0x0   0  12.379
    31   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    36   -  10.57     -     -  0x0   -       -
^C
[11/29/23 21:33:36 UTC] PTU stopped.

controller-0:~#
```

## check sensors

```log
controller-0:~# ipmitool sensor | grep -e CPU_0_TEMP -e CPU0_Power -e SYS_FAN_1A -e CPU_CUPS
CPU_0_TEMP       | 78.000     | degrees C  | ok    | na        | na        | na        | 101.000   | 104.000   | na
CPU0_Power       | 164.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 12160.000  | RPM        | ok    | na        | 1120.000  | na        | na        | 39840.000 | na
CPU_CUPS         | 73.000     | percent    | ok    | na        | na        | na        | na        | 100.000   | na
controller-0:~#
```

## Success, was able to observe temp rise, then fans increasing as load was started


## MEAKV-646 
## PTU 5 - Turbo Test
## sudo ./ptu -ct 8 -allcore -b 1

## sensors before load

```log
controller-0:~# ipmitool sensor | grep -e CPU_0_TEMP -e CPU0_Power -e SYS_FAN_1A -e CPU_CUPS
CPU_0_TEMP       | 45.000     | degrees C  | ok    | na        | na        | na        | 101.000   | 104.000   | na
CPU0_Power       | 64.000     | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 9600.000   | RPM        | ok    | na        | 1120.000  | na        | na        | 39840.000 | na
CPU_CUPS         | 1.000      | percent    | ok    | na        | na        | na        | na        | 100.000   | na
controller-0:~#
```

## Initiating load

```log
controller-0:~# /home/XXXXXX/ptu -ct 8 -allcore -b 1

Command: /home/XXXXXX/ptu -ct 8 -allcore -b 1

Intel(R) Power Thermal Utility - Server Edition v2.3.1
Release Date: 12/04/2020
Copyright (C) 2020 Intel Corporation. All rights reserved.
Intel Confidential

/dev/ptusys: No such file or directory
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> System Info:                   <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Host Name:                           controller-0
Host IP:                             169.254.202.1
OS Name:                             CentOS Linux 7 (Core)
Kernel Version:                      Linux 5.10.112-200.25.tis.rt.el7.x86_64 #1 SMP PREEMPT_RT Wed May 3 22:37:28 EDT 2023
BIOS Version:                        American Megatrends Inc., 2.06, 06/28/2021
Processor(s):                        1 Processor(s) Installed.
DIMM(s):                             6 DIMM(s) Installed.
Total System Memory:                 95465 MB
Available System Memory:             54609 MB


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Processor: [CPU_0]             <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU ID:                              0x00050657 (Family 6 Model 55h Stepping 7)
CPU Brand Name:                      Intel(R) Xeon(R) Gold 6212U CPU @ 2.40GHz
CPU Code Name:                       Cascade Lake
CPU Type:                            Production Part
CPU Segment:                         Server
CPU PPIN:                            0x66AAEDBA78DF031D
CPU Base Frequency:                  1500 MHz
CPU Minimum Frequency:               1000 MHz
CPU Maximum Turbo Frequency:         3900 MHz
Uncore Minimum Frequency:            1200 MHz
Uncore Maximum Frequency:            2400 MHz
L2 Cache:                            24 x 1024 KB
L3 Cache:                            36608 KB
Hyper-threading:                     Enabled
Microcode Update Revision:           0x05003102
Number of Physcial Core(s):          24
Number of Logical Core(s):           48
Turbo Boost:                         Enabled
Turbo Boost Frequency:
 IA/SSE:
    1 -  2 Cores (Fused/Resolved):   3900 / 3900 (MHz)
    3 -  4 Cores (Fused/Resolved):   3700 / 3700 (MHz)
    5 - 16 Cores (Fused/Resolved):   3600 / 3600 (MHz)
   17 - 20 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   21 - 24 Cores (Fused/Resolved):   3100 / 3100 (MHz)
 AVX2:
    1 -  2 Cores (Fused/Resolved):   3700 / 3700 (MHz)
    3 -  4 Cores (Fused/Resolved):   3500 / 3500 (MHz)
    5 -  8 Cores (Fused/Resolved):   3400 / 3400 (MHz)
    9 - 12 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   13 - 16 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   17 - 20 Cores (Fused/Resolved):   2700 / 2700 (MHz)
   21 - 24 Cores (Fused/Resolved):   2600 / 2600 (MHz)
 AVX-512:
    1 -  2 Cores (Fused/Resolved):   3700 / 3700 (MHz)
    3 -  4 Cores (Fused/Resolved):   3500 / 3500 (MHz)
    5 -  8 Cores (Fused/Resolved):   3400 / 3400 (MHz)
    9 - 12 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   13 - 16 Cores (Fused/Resolved):   2600 / 2600 (MHz)
   17 - 20 Cores (Fused/Resolved):   2400 / 2400 (MHz)
   21 - 24 Cores (Fused/Resolved):   2300 / 2300 (MHz)
OVOLT_OVRD Supported:                0
OVOLT_OVRD Disabled:                 1
Platform ID:                         0x0
Platform Info:                       0x70A2CF2810F00000
Thermal Design Power (TDP):          165 W
Power Limit 1 - Long Duration:       Enabled, Clamp OFF, Power = 165 W, Time = 1.00 sec
Power Limit 2 - Short Duration:      Enabled, Clamp ON , Power = 198 W, Time = 1.95 sec
Config TDP Level Supported:          2
Config TDP Level 1:                  165.0 W (78.0 W - 413.0 W), 1500 MHz
Config TDP Level 2:                  165.0 W (78.0 W - 413.0 W), 1500 MHz
Current Config TDP Level:            NominalLevel 2
Tprochot:                            104 C
TCC Offset:                          0
CAPID0:                              0x001881F8
CAPID1:                              0x040000C3
CAPID2:                              0x13800000
CAPID3:                              0x00004000
CAPID4:                              0x24000EC0
CAPID5:                              0x660001FB
CAPID6:                              0x0FFDFFBF
CAPID7:                              0x07FDFFB7


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Memory: [MEM_0]                <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Number of DIMM(s):                   6
Number of Active Channel(s):         6
DRAM Power Meter Disabled:           0
DRAM RAPL Disabled:                  0
DRAM TDP Power:                      Min = 4.5 W, Max = 27.8 W, Time = 32.00 sec
DRAM / NVDIMM Info:
  MC 0, Chnl 0, Slot 0:              tempLo: 84 C, tempMid: 93 C, tempHi: 100 C
  MC 0, Chnl 1, Slot 0:              tempLo: 84 C, tempMid: 93 C, tempHi: 100 C
  MC 0, Chnl 2, Slot 0:              tempLo: 84 C, tempMid: 93 C, tempHi: 100 C
  MC 1, Chnl 3, Slot 0:              tempLo: 84 C, tempMid: 93 C, tempHi: 100 C
  MC 1, Chnl 4, Slot 0:              tempLo: 84 C, tempMid: 93 C, tempHi: 100 C
  MC 1, Chnl 5, Slot 0:              tempLo: 84 C, tempMid: 93 C, tempHi: 100 C


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Platform Controller Hub: [PCH] <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
PCH Device ID:                       8086:A1C1 (LBG-1G)
PCH Stepping:                        9
PCH Thermal Sensor Enable:           1
PCH Hot Level (PHL):                 -50
PCH Catastrophic Trip Point (CTRIP): 106


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> PTU Current Settings:          <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU Test Selected:                   8
MEM Test Selected:                   0
CPU Mask:                            0xFFFF
CPU Core Mask:                       0xFFFFFFFFFFFFFFFF
CPU Thread Mask:                     0xFF
MEM Mask:                            0xFFFF
MEM Core Mask:                       0xFFFFFFFFFFFFFFFF
MEM Thread Mask:                     0xFF
Core Power Level:                    100
Memory Power Level:                  100
Turbo Enabled:                       Yes
AVX Test Level:                      1
Pmax Pre-sync:                       5000 ms
Pmax Post-sync:                      3000 ms
Pmax Idle:                           2000 ms
Run Time:                            0 (Forever)
PTU Mon CPU Mask:                    0xFFFFFFFF
PTU Mon Core Mask:                   0xFFFFFFFFFFFFFFFF
PTU Mon MEM Mask:                    0xFFFFFFFF
PTU Mon Filter Mask:                 0x1F
PTU Mon Update Interval:             1000000 usec
PTU Mon Long Level:                  0
PTU Mon Timestamp:                   No
Log Enabled:                         No
Log Directory:                       /root/ptu/log
Log File Prefix:                     <timestamp>
Log Message File:                    <timestamp>_ptumsg.txt
Log Monitor File:                    <timestamp>_ptumon.txt
CSV Enabled:                         No
PTU License Auto Accept:             No
PTU Driver Loaded:                   No

[11/29/23 21:37:39 UTC] PTU started.

Press <Ctrl-C> to stop.


CPU_0: [IDLE] CFreq=2284, UFreq=2400, Util=1.23, IPC=0.69, Temp=58, DTS=46, Power=63.8, Volt=0.777

### TURBO is enabled ###

Instr   CPU #Cores CFreq(act) CFreq(exp) UFreq Power TDP  Temp Volt
IA/SSE  0   24     2.3        3.1        2.4   105.8 165  65   0.774



```

## ptu -mon

```log
controller-0:~# /home/XXXXXX/ptu -mon

Command: /home/XXXXXX/ptu -mon

Intel(R) Power Thermal Utility - Server Edition v2.3.1
Release Date: 12/04/2020
Copyright (C) 2020 Intel Corporation. All rights reserved.
Intel Confidential

/dev/ptusys: No such file or directory
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> System Info:                   <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Host Name:                           controller-0
Host IP:                             169.254.202.1
OS Name:                             CentOS Linux 7 (Core)
Kernel Version:                      Linux 5.10.112-200.25.tis.rt.el7.x86_64 #1 SMP PREEMPT_RT Wed May 3 22:37:28 EDT 2023
BIOS Version:                        American Megatrends Inc., 2.06, 06/28/2021
Processor(s):                        1 Processor(s) Installed.
DIMM(s):                             6 DIMM(s) Installed.
Total System Memory:                 95465 MB
Available System Memory:             54598 MB


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Processor: [CPU_0]             <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU ID:                              0x00050657 (Family 6 Model 55h Stepping 7)
CPU Brand Name:                      Intel(R) Xeon(R) Gold 6212U CPU @ 2.40GHz
CPU Code Name:                       Cascade Lake
CPU Type:                            Production Part
CPU Segment:                         Server
CPU PPIN:                            0x66AAEDBA78DF031D
CPU Base Frequency:                  1500 MHz
CPU Minimum Frequency:               1000 MHz
CPU Maximum Turbo Frequency:         3900 MHz
Uncore Minimum Frequency:            1200 MHz
Uncore Maximum Frequency:            2400 MHz
L2 Cache:                            24 x 1024 KB
L3 Cache:                            36608 KB
Hyper-threading:                     Enabled
Microcode Update Revision:           0x05003102
Number of Physcial Core(s):          24
Number of Logical Core(s):           48
Turbo Boost:                         Enabled
Turbo Boost Frequency:
 IA/SSE:
    1 -  2 Cores (Fused/Resolved):   3900 / 3900 (MHz)
    3 -  4 Cores (Fused/Resolved):   3700 / 3700 (MHz)
    5 - 16 Cores (Fused/Resolved):   3600 / 3600 (MHz)
   17 - 20 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   21 - 24 Cores (Fused/Resolved):   3100 / 3100 (MHz)
 AVX2:
    1 -  2 Cores (Fused/Resolved):   3700 / 3700 (MHz)
    3 -  4 Cores (Fused/Resolved):   3500 / 3500 (MHz)
    5 -  8 Cores (Fused/Resolved):   3400 / 3400 (MHz)
    9 - 12 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   13 - 16 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   17 - 20 Cores (Fused/Resolved):   2700 / 2700 (MHz)
   21 - 24 Cores (Fused/Resolved):   2600 / 2600 (MHz)
 AVX-512:
    1 -  2 Cores (Fused/Resolved):   3700 / 3700 (MHz)
    3 -  4 Cores (Fused/Resolved):   3500 / 3500 (MHz)
    5 -  8 Cores (Fused/Resolved):   3400 / 3400 (MHz)
    9 - 12 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   13 - 16 Cores (Fused/Resolved):   2600 / 2600 (MHz)
   17 - 20 Cores (Fused/Resolved):   2400 / 2400 (MHz)
   21 - 24 Cores (Fused/Resolved):   2300 / 2300 (MHz)
OVOLT_OVRD Supported:                0
OVOLT_OVRD Disabled:                 1
Platform ID:                         0x0
Platform Info:                       0x70A2CF2810F00000
Thermal Design Power (TDP):          165 W
Power Limit 1 - Long Duration:       Enabled, Clamp OFF, Power = 165 W, Time = 1.00 sec
Power Limit 2 - Short Duration:      Enabled, Clamp ON , Power = 198 W, Time = 1.95 sec
Config TDP Level Supported:          2
Config TDP Level 1:                  165.0 W (78.0 W - 413.0 W), 1500 MHz
Config TDP Level 2:                  165.0 W (78.0 W - 413.0 W), 1500 MHz
Current Config TDP Level:            NominalLevel 2
Tprochot:                            104 C
TCC Offset:                          0
CAPID0:                              0x001881F8
CAPID1:                              0x040000C3
CAPID2:                              0x13800000
CAPID3:                              0x00004000
CAPID4:                              0x24000EC0
CAPID5:                              0x660001FB
CAPID6:                              0x0FFDFFBF
CAPID7:                              0x07FDFFB7


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Memory: [MEM_0]                <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Number of DIMM(s):                   6
Number of Active Channel(s):         6
DRAM Power Meter Disabled:           0
DRAM RAPL Disabled:                  0
DRAM TDP Power:                      Min = 4.5 W, Max = 27.8 W, Time = 32.00 sec
DRAM / NVDIMM Info:
  MC 0, Chnl 0, Slot 0:              tempLo: 84 C, tempMid: 93 C, tempHi: 100 C
  MC 0, Chnl 1, Slot 0:              tempLo: 84 C, tempMid: 93 C, tempHi: 100 C
  MC 0, Chnl 2, Slot 0:              tempLo: 84 C, tempMid: 93 C, tempHi: 100 C
  MC 1, Chnl 3, Slot 0:              tempLo: 84 C, tempMid: 93 C, tempHi: 100 C
  MC 1, Chnl 4, Slot 0:              tempLo: 84 C, tempMid: 93 C, tempHi: 100 C
  MC 1, Chnl 5, Slot 0:              tempLo: 84 C, tempMid: 93 C, tempHi: 100 C


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Platform Controller Hub: [PCH] <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
PCH Device ID:                       8086:A1C1 (LBG-1G)
PCH Stepping:                        9
PCH Thermal Sensor Enable:           1
PCH Hot Level (PHL):                 -50
PCH Catastrophic Trip Point (CTRIP): 106


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> PTU Current Settings:          <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU Test Selected:                   0
MEM Test Selected:                   0
CPU Mask:                            0xFFFF
CPU Core Mask:                       0xFFFFFFFFFFFFFFFF
CPU Thread Mask:                     0xFF
MEM Mask:                            0xFFFF
MEM Core Mask:                       0xFFFFFFFFFFFFFFFF
MEM Thread Mask:                     0xFF
Core Power Level:                    100
Memory Power Level:                  100
Turbo Enabled:                       No
AVX Test Level:                      1
Pmax Pre-sync:                       5000 ms
Pmax Post-sync:                      3000 ms
Pmax Idle:                           2000 ms
Run Time:                            0 (Forever)
PTU Mon CPU Mask:                    0xFFFFFFFF
PTU Mon Core Mask:                   0xFFFFFFFFFFFFFFFF
PTU Mon MEM Mask:                    0xFFFFFFFF
PTU Mon Filter Mask:                 0x1F
PTU Mon Update Interval:             1000000 usec
PTU Mon Long Level:                  0
PTU Mon Timestamp:                   No
Log Enabled:                         No
Log Directory:                       /root/ptu/log
Log File Prefix:                     <timestamp>
Log Message File:                    <timestamp>_ptumsg.txt
Log Monitor File:                    <timestamp>_ptumon.txt
CSV Enabled:                         No
PTU License Auto Accept:             No
PTU Driver Loaded:                   No

[11/29/23 21:38:57 UTC] PTU started.

Press <Ctrl-C> to stop.


 Index Device Cor Thr CFreq UFreq   Util  IPC     C0     C1     C6    PC2    PC6 MC Ch Sl  Temp DTS  Power  Volt TStat TLog #TL TMargin
     0   CPU0   -   -  2299  2400   2.53 0.70   2.53  97.47   0.00   0.00   0.00  -  -  -    56  48  64.92 0.785   0x0  0x0   0  36.438
     0   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.69     -     -  0x0   -       -
     1   CPU0   -   -  2288  2400   0.72 0.67   0.72  99.28   0.00   0.00   0.00  -  -  -    55  49  63.46 0.786   0x0  0x0   0  38.344
     1   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.59     -     -  0x0   -       -
     2   CPU0   -   -  2262  2400   1.74 0.69   1.75  98.25   0.00   0.00   0.00  -  -  -    57  47  64.21 0.785   0x0  0x0   0  38.328
     2   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.65     -     -  0x0   -       -
     3   CPU0   -   -  2337  2400   1.94 0.70   1.93  98.07   0.00   0.00   0.00  -  -  -    56  48  64.50 0.785   0x0  0x0   0  38.031
     3   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.68     -     -  0x0   -       -
     4   CPU0   -   -  2297  2400   0.62 0.66   0.62  99.38   0.00   0.00   0.00  -  -  -    56  48  63.20 0.786   0x0  0x0   0  38.594
     4   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.55     -     -  0x0   -       -
     5   CPU0   -   -  2295  2400   1.03 0.70   1.03  98.97   0.00   0.00   0.00  -  -  -    55  49  63.76 0.786   0x0  0x0   0  38.375
     5   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.63     -     -  0x0   -       -
     6   CPU0   -   -  2294  2400   0.62 0.70   0.62  99.38   0.00   0.00   0.00  -  -  -    56  48  63.24 0.785   0x0  0x0   0  38.672
     6   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.54     -     -  0x0   -       -
     7   CPU0   -   -  2296  2400   1.02 0.68   1.02  98.98   0.00   0.00   0.00  -  -  -    57  47  63.78 0.785   0x0  0x0   0  38.578
     7   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.60     -     -  0x0   -       -
     8   CPU0   -   -  2289  2400   1.84 0.70   1.84  98.16   0.00   0.00   0.00  -  -  -    58  46  64.45 0.785   0x0  0x0   0  37.359
     8   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.70     -     -  0x0   -       -
     9   CPU0   -   -  2301  2400   0.78 0.69   0.78  99.22   0.00   0.00   0.00  -  -  -    55  49  63.58 0.786   0x0  0x0   0  38.578
     9   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.57     -     -  0x0   -       -
    10   CPU0   -   -  2263  2400   0.94 0.80   0.94  99.06   0.00   0.00   0.00  -  -  -    57  47  63.58 0.785   0x0  0x0   0  38.703
    10   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.60     -     -  0x0   -       -
    11   CPU0   -   -  2332  2400   0.98 0.69   0.98  99.02   0.00   0.00   0.00  -  -  -    55  49  63.70 0.786   0x0  0x0   0  37.734
    11   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.55     -     -  0x0   -       -
    12   CPU0   -   -  2206  2400   0.78 0.79   0.81  99.19   0.00   0.00   0.00  -  -  -    58  46  63.37 0.786   0x0  0x0   0  38.797
    12   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.51     -     -  0x0   -       -
    13   CPU0   -   -  2355  2400   2.16 0.76   2.14  97.86   0.00   0.00   0.00  -  -  -    55  49  64.83 0.786   0x0  0x0   0  38.078
    13   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.67     -     -  0x0   -       -
    14   CPU0   -   -  2310  2400   0.72 0.70   0.73  99.27   0.00   0.00   0.00  -  -  -    57  47  63.45 0.786   0x0  0x0   0  38.828
    14   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.55     -     -  0x0   -       -
    15   CPU0   -   -  2297  2400   0.82 0.80   0.80  99.20   0.00   0.00   0.00  -  -  -    55  49  63.49 0.786   0x0  0x0   0  38.797
    15   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.55     -     -  0x0   -       -
    16   CPU0   -   -  2262  2400   0.60 0.72   0.60  99.40   0.00   0.00   0.00  -  -  -    56  48  63.06 0.785   0x0  0x0   0  38.875
    16   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.52     -     -  0x0   -       -
    17   CPU0   -   -  2316  2400   3.00 0.77   3.00  97.00   0.00   0.00   0.00  -  -  -    58  46  65.43 0.786   0x0  0x0   0  37.078
    17   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.66     -     -  0x0   -       -
    18   CPU0   -   -  2295  2400   2.09 0.67   2.09  97.91   0.00   0.00   0.00  -  -  -    56  48  64.70 0.785   0x0  0x0   0  37.516
    18   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.64     -     -  0x0   -       -
    19   CPU0   -   -  2298  2400   0.89 0.75   0.89  99.11   0.00   0.00   0.00  -  -  -    58  46  63.50 0.786   0x0  0x0   0  38.562
    19   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.54     -     -  0x0   -       -
    20   CPU0   -   -  2278  2400   1.66 0.75   1.67  98.33   0.00   0.00   0.00  -  -  -    57  47  64.31 0.785   0x0  0x0   0  38.703
    20   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.61     -     -  0x0   -       -
    21   CPU0   -   -  2303  2400   0.61 0.69   0.60  99.40   0.00   0.00   0.00  -  -  -    55  49  63.25 0.786   0x0  0x0   0  38.891
    21   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.55     -     -  0x0   -       -
    22   CPU0   -   -  2308  2400   0.87 0.72   0.87  99.13   0.00   0.00   0.00  -  -  -    55  49  63.36 0.786   0x0  0x0   0  38.984
    22   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.56     -     -  0x0   -       -
    23   CPU0   -   -  2294  2400   2.18 0.70   2.18  97.82   0.00   0.00   0.00  -  -  -    57  47  64.62 0.785   0x0  0x0   0  38.375
    23   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.67     -     -  0x0   -       -
    24   CPU0   -   -  2311  2400   1.18 0.71   1.18  98.82   0.00   0.00   0.00  -  -  -    55  49  63.59 0.786   0x0  0x0   0  38.672
    24   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.55     -     -  0x0   -       -
    25   CPU0   -   -  2291  2400   0.97 0.68   0.96  99.04   0.00   0.00   0.00  -  -  -    55  49  63.38 0.786   0x0  0x0   0  38.875
    25   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.56     -     -  0x0   -       -
    26   CPU0   -   -  2277  2400   2.16 0.71   2.17  97.83   0.00   0.00   0.00  -  -  -    58  46  64.79 0.785   0x0  0x0   0  37.328
    26   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.61     -     -  0x0   -       -
    27   CPU0   -   -  2306  2400   3.39 0.70   3.39  96.61   0.00   0.00   0.00  -  -  -    57  47  65.97 0.785   0x0  0x0   0  36.609
    27   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.68     -     -  0x0   -       -
    28   CPU0   -   -  2291  2400   4.00 0.74   4.00  96.00   0.00   0.00   0.00  -  -  -    58  46  66.43 0.785   0x0  0x0   0  36.328
    28   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.74     -     -  0x0   -       -
    29   CPU0   -   -  2299  2400   4.23 0.79   4.22  95.78   0.00   0.00   0.00  -  -  -    57  47  66.60 0.785   0x0  0x0   0  36.172
    29   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.65     -     -  0x0   -       -
    30   CPU0   -   -  2252  2400   2.96 0.71   2.97  97.03   0.00   0.00   0.00  -  -  -    58  46  65.60 0.785   0x0  0x0   0  36.328
    30   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.67     -     -  0x0   -       -
    31   CPU0   -   -  2322  2400   3.74 0.90   3.73  96.27   0.00   0.00   0.00  -  -  -    57  47  66.26 0.785   0x0  0x0   0  35.969
    31   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.69     -     -  0x0   -       -
    32   CPU0   -   -  2305  2400   2.62 0.66   2.62  97.38   0.00   0.00   0.00  -  -  -    55  49  64.86 0.785   0x0  0x0   0  37.109
    32   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    37   -  10.62     -     -  0x0   -       -
^C
[11/29/23 21:39:33 UTC] PTU stopped.

controller-0:~#
```

## Sensors after load started

```log
controller-0:~# ipmitool sensor | grep -e CPU_0_TEMP -e CPU0_Power -e SYS_FAN_1A -e CPU_CUPS
CPU_0_TEMP       | 40.000     | degrees C  | ok    | na        | na        | na        | 101.000   | 104.000   | na
CPU0_Power       | 63.000     | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 9440.000   | RPM        | ok    | na        | 1120.000  | na        | na        | 39840.000 | na
CPU_CUPS         | 4.000      | percent    | ok    | na        | na        | na        | na        | 100.000   | na
controller-0:~# ipmitool sensor | grep -e CPU_0_TEMP -e CPU0_Power -e SYS_FAN_1A -e CPU_CUPS
CPU_0_TEMP       | 40.000     | degrees C  | ok    | na        | na        | na        | 101.000   | 104.000   | na
CPU0_Power       | 62.000     | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 9600.000   | RPM        | ok    | na        | 1120.000  | na        | na        | 39840.000 | na
CPU_CUPS         | 1.000      | percent    | ok    | na        | na        | na        | na        | 100.000   | na
controller-0:~# ipmitool sensor | grep -e CPU_0_TEMP -e CPU0_Power -e SYS_FAN_1A -e CPU_CUPS
CPU_0_TEMP       | 41.000     | degrees C  | ok    | na        | na        | na        | 101.000   | 104.000   | na
CPU0_Power       | 65.000     | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 9600.000   | RPM        | ok    | na        | 1120.000  | na        | na        | 39840.000 | na
CPU_CUPS         | 2.000      | percent    | ok    | na        | na        | na        | na        | 100.000   | na
controller-0:~# ipmitool sensor | grep -e CPU_0_TEMP -e CPU0_Power -e SYS_FAN_1A -e CPU_CUPS
CPU_0_TEMP       | 40.000     | degrees C  | ok    | na        | na        | na        | 101.000   | 104.000   | na
CPU0_Power       | 63.000     | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 9600.000   | RPM        | ok    | na        | 1120.000  | na        | na        | 39840.000 | na
CPU_CUPS         | 1.000      | percent    | ok    | na        | na        | na        | na        | 100.000   | na
controller-0:~# ipmitool sensor | grep -e CPU_0_TEMP -e CPU0_Power -e SYS_FAN_1A -e CPU_CUPS
CPU_0_TEMP       | 40.000     | degrees C  | ok    | na        | na        | na        | 101.000   | 104.000   | na
CPU0_Power       | 62.000     | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 9440.000   | RPM        | ok    | na        | 1120.000  | na        | na        | 39840.000 | na
CPU_CUPS         | 3.000      | percent    | ok    | na        | na        | na        | na        | 100.000   | na
controller-0:~#
```


## Temps didn't rise as much as with other tests, but all data recorded, no issues found.
## Success, end of performance tests with PTU