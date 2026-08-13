# ZT Proteus .46 BMC firmware validation
# ZT Proteus BIOS .23
# 1/11/24 James Patchett

## Target Controller rchltxib-c000000-001
Controller-0 iLO 2607:f160:a:d02e:cd:fe0::8006 
Controller-1 iLO 2607:f160:a:d02e:cd:fe0::8007
Worker-0 iLO 2607:f160:a:d02e:cd:fe0::8008 
OAM 2607:f160:0:3049:cd:290:0:10

## Target Subcloud welktxef-d931856-008
OAM: 2607:f160:10:80b1:ce:40a:0:f408
BMC: 2607:f160:10:80b1:ce:40a:0:e008

ipmitool -I lanplus -U XXXXXX -P XXXXXX -H 2607:f160:10:80b1:ce:40a:0:e008 sol activate

## Subcloud welktxef-d931856-008 Info
```log
====================================================================
         SYSTEM: welktxef-d931856-008
====================================================================

controller-0:~$ source /etc/platform/openrc
[XXXXXX@controller-0 ~(keystone_admin)]$ system show
+------------------------+--------------------------------------+
| Property               | Value                                |
+------------------------+--------------------------------------+
| contact                | None                                 |
| created_at             | 2023-10-24T23:12:39.021874+00:00     |
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
| updated_at             | 2023-10-24T23:59:50.313360+00:00     |
| uuid                   | b2db84e7-d175-4f9f-b848-8192131d38bf |
| vswitch_type           | none                                 |
+------------------------+--------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ system application-list
+--------------------------+----------+-----------------------------------+--------------------------------------+----------+-----------+
| application              | version  | manifest name                     | manifest file                        | status   | progress  |
+--------------------------+----------+-----------------------------------+--------------------------------------+----------+-----------+
| cert-manager             | 21.12-28 | cert-manager-manifest             | certmanager-manifest.yaml            | applied  | completed |
| metrics-server           | 21.12-9  | metrics-server-manifest           | metrics-server_manifest.yaml         | applied  | completed |
| nginx-ingress-controller | 21.12-18 | nginx-ingress-controller-manifest | nginx_ingress_controller_manifest.   | applied  | completed |
|                          |          |                                   | yaml                                 |          |           |
|                          |          |                                   |                                      |          |           |
| oidc-auth-apps           | 21.12-61 | oidc-auth-manifest                | manifest.yaml                        | applied  | completed |
| platform-integ-apps      | 21.12-46 | platform-integration-manifest     | manifest.yaml                        | applied  | completed |
| rook-ceph-apps           | 1.0-14   | rook-ceph-manifest                | manifest.yaml                        | uploaded | completed |
+--------------------------+----------+-----------------------------------+--------------------------------------+----------+-----------+
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
## Performance Test MEAKV-642 
## sudo ./ptu -ct 1 -b 0
## measure sensors first, then run load, then check during load

## Sensors
```log
controller-0:~# ipmitool sensor | grep -e CPU_0_TEMP -e CPU0_Power -e SYS_FAN_1A -e CPU_CUPS
CPU_0_TEMP       | 58.000     | degrees C  | ok    | na        | na        | na        | 96.000    | 98.000    | na
CPU0_Power       | 106.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 5000.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1A_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
CPU_CUPS         | 1.000      | percent    | ok    | na        | na        | na        | na        | 100.000   | na
controller-0:~#
```

## Initiate load 

```log
controller-0:~# /tmp/ptu -ct 1 -b 0

Command: /tmp/ptu -ct 1 -b 0

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
BIOS Version:                        American Megatrends International, LLC., 0.23, 06/29/2021
Processor(s):                        1 Processor(s) Installed.
DIMM(s):                             8 DIMM(s) Installed.
Total System Memory:                 127963 MB
Available System Memory:             76680 MB


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Processor: [CPU_0]             <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU ID:                              0x000606A6 (Family 6 Model 6Ah Stepping 6)
CPU Brand Name:                      Intel(R) Xeon(R) Gold 6338N CPU @ 2.20GHz
CPU Code Name:                       Ice Lake
CPU Type:                            Production Part
CPU Segment:                         Server
CPU PPIN:                            0xB3DF86FF63529310
CPU Base Frequency:                  1500 MHz
CPU Minimum Frequency:               800 MHz
CPU Maximum Turbo Frequency:         3500 MHz
Uncore Minimum Frequency:            1700 MHz
Uncore Maximum Frequency:            1700 MHz
L2 Cache:                            32 x 1280 KB
L3 Cache:                            49152 KB
Hyper-threading:                     Enabled
Microcode Update Revision:           0x0D0002A0
Number of Physcial Core(s):          32
Number of Logical Core(s):           64
Turbo Boost:                         Enabled
Turbo Boost Frequency:
 IA/SSE:
    1 - 16 Cores (Fused/Resolved):   3500 / 3500 (MHz)
   17 - 20 Cores (Fused/Resolved):   3200 / 3200 (MHz)
   21 - 22 Cores (Fused/Resolved):   3100 / 3100 (MHz)
   23 - 26 Cores (Fused/Resolved):   2900 / 2900 (MHz)
   27 - 28 Cores (Fused/Resolved):   2800 / 2800 (MHz)
   29 - 32 Cores (Fused/Resolved):   2700 / 2700 (MHz)
 AVX2:
    1 - 16 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   17 - 20 Cores (Fused/Resolved):   3100 / 3100 (MHz)
   21 - 22 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   23 - 26 Cores (Fused/Resolved):   2800 / 2800 (MHz)
   27 - 28 Cores (Fused/Resolved):   2700 / 2700 (MHz)
   29 - 32 Cores (Fused/Resolved):   2600 / 2600 (MHz)
 AVX-512:
    1 - 16 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   17 - 20 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   21 - 22 Cores (Fused/Resolved):   2900 / 2900 (MHz)
   23 - 26 Cores (Fused/Resolved):   2700 / 2700 (MHz)
   27 - 28 Cores (Fused/Resolved):   2600 / 2600 (MHz)
   29 - 32 Cores (Fused/Resolved):   2500 / 2500 (MHz)
OVOLT_OVRD Supported:                0
OVOLT_OVRD Disabled:                 1
Platform ID:                         0x0
Platform Info:                       0x8082DF2810F00000
Thermal Design Power (TDP):          185 W
Power Limit 1 - Long Duration:       Enabled, Clamp ON , Power = 185 W, Time = 1.00 sec
Power Limit 2 - Short Duration:      Enabled, Clamp ON , Power = 222 W, Time = 1000.00 sec
Config TDP Level Supported:          2
Config TDP Level 1:                  185.0 W (84.0 W - 652.0 W), 1800 MHz
Config TDP Level 2:                  185.0 W (84.0 W - 652.0 W), 1500 MHz
Current Config TDP Level:            Nominal [Locked]
Tprochot:                            98 C
TCC Offset:                          0
CAPID0:                              0x001883F9
CAPID1:                              0x0AC000C3
CAPID2:                              0x04300000
CAPID3:                              0x07804000
CAPID4:                              0x04002EC0
CAPID5:                              0x6B1FE1FB
CAPID6:                              0x3F777FF6
CAPID7:                              0x000000FB
CAPID8:                              0x3F777FF6
CAPID9:                              0x000000FB
CAPID10:                             0x00000000


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Memory: [MEM_0]                <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Number of DIMM(s):                   8
Number of Active Channel(s):         8
DRAM Power Meter Disabled:           0
DRAM RAPL Disabled:                  0
DRAM TDP Power:                      Min = 5.5 W, Max = 34.0 W, Time = 0.31 sec
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
PCH Device ID:                       8086:A1CB (Unknown Device Type)
PCH Stepping:                        10
PCH Thermal Sensor Enable:           1
PCH Hot Level (PHL):                 85
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

[01/12/24 18:21:10 UTC] PTU started.

Press <Ctrl-C> to stop.


CPU_0: [IDLE] CFreq=2491, UFreq=1700, Util=0.68, IPC=0.89, Temp=57, DTS=41, Power=105.6, Volt=0.864, UVolt=0.865
CPU_0: [TESTCFG] TestSel=1 (TDP), CoreMask=0xFFFFFFFFFFFFFFFF, ThreadMask=0xFF, PwrLevel=TDP, Turbo=0
CPU_0: [RUNNING] CFreq=2284, UFreq=1400, Util=100.00, IPC=3.15, Temp=68, DTS=30, Power=184.4, Volt=0.820, UVolt=0.815


```

## Ptu monitoring

```log
controller-0:~# /tmp/ptu -mon

Command: /tmp/ptu -mon

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
BIOS Version:                        American Megatrends International, LLC., 0.23, 06/29/2021
Processor(s):                        1 Processor(s) Installed.
DIMM(s):                             8 DIMM(s) Installed.
Total System Memory:                 127963 MB
Available System Memory:             76628 MB


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Processor: [CPU_0]             <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU ID:                              0x000606A6 (Family 6 Model 6Ah Stepping 6)
CPU Brand Name:                      Intel(R) Xeon(R) Gold 6338N CPU @ 2.20GHz
CPU Code Name:                       Ice Lake
CPU Type:                            Production Part
CPU Segment:                         Server
CPU PPIN:                            0xB3DF86FF63529310
CPU Base Frequency:                  1500 MHz
CPU Minimum Frequency:               800 MHz
CPU Maximum Turbo Frequency:         3500 MHz
Uncore Minimum Frequency:            1700 MHz
Uncore Maximum Frequency:            1700 MHz
L2 Cache:                            32 x 1280 KB
L3 Cache:                            49152 KB
Hyper-threading:                     Enabled
Microcode Update Revision:           0x0D0002A0
Number of Physcial Core(s):          32
Number of Logical Core(s):           64
Turbo Boost:                         Disabled
Turbo Boost Frequency:
 IA/SSE:
    1 - 16 Cores (Fused/Resolved):   3500 / 3500 (MHz)
   17 - 20 Cores (Fused/Resolved):   3200 / 3200 (MHz)
   21 - 22 Cores (Fused/Resolved):   3100 / 3100 (MHz)
   23 - 26 Cores (Fused/Resolved):   2900 / 2900 (MHz)
   27 - 28 Cores (Fused/Resolved):   2800 / 2800 (MHz)
   29 - 32 Cores (Fused/Resolved):   2700 / 2700 (MHz)
 AVX2:
    1 - 16 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   17 - 20 Cores (Fused/Resolved):   3100 / 3100 (MHz)
   21 - 22 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   23 - 26 Cores (Fused/Resolved):   2800 / 2800 (MHz)
   27 - 28 Cores (Fused/Resolved):   2700 / 2700 (MHz)
   29 - 32 Cores (Fused/Resolved):   2600 / 2600 (MHz)
 AVX-512:
    1 - 16 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   17 - 20 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   21 - 22 Cores (Fused/Resolved):   2900 / 2900 (MHz)
   23 - 26 Cores (Fused/Resolved):   2700 / 2700 (MHz)
   27 - 28 Cores (Fused/Resolved):   2600 / 2600 (MHz)
   29 - 32 Cores (Fused/Resolved):   2500 / 2500 (MHz)
OVOLT_OVRD Supported:                0
OVOLT_OVRD Disabled:                 1
Platform ID:                         0x0
Platform Info:                       0x8082DF2810F00000
Thermal Design Power (TDP):          185 W
Power Limit 1 - Long Duration:       Enabled, Clamp ON , Power = 185 W, Time = 1.00 sec
Power Limit 2 - Short Duration:      Enabled, Clamp ON , Power = 222 W, Time = 1000.00 sec
Config TDP Level Supported:          2
Config TDP Level 1:                  185.0 W (84.0 W - 652.0 W), 1800 MHz
Config TDP Level 2:                  185.0 W (84.0 W - 652.0 W), 1500 MHz
Current Config TDP Level:            Nominal [Locked]
Tprochot:                            98 C
TCC Offset:                          0
CAPID0:                              0x001883F9
CAPID1:                              0x0AC000C3
CAPID2:                              0x04300000
CAPID3:                              0x07804000
CAPID4:                              0x04002EC0
CAPID5:                              0x6B1FE1FB
CAPID6:                              0x3F777FF6
CAPID7:                              0x000000FB
CAPID8:                              0x3F777FF6
CAPID9:                              0x000000FB
CAPID10:                             0x00000000


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Memory: [MEM_0]                <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Number of DIMM(s):                   8
Number of Active Channel(s):         8
DRAM Power Meter Disabled:           0
DRAM RAPL Disabled:                  0
DRAM TDP Power:                      Min = 5.5 W, Max = 34.0 W, Time = 0.31 sec
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
PCH Device ID:                       8086:A1CB (Unknown Device Type)
PCH Stepping:                        10
PCH Thermal Sensor Enable:           1
PCH Hot Level (PHL):                 85
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

[01/12/24 18:26:25 UTC] PTU started.

Press <Ctrl-C> to stop.


 Index Device Cor Thr CFreq UFreq   Util  IPC     C0     C1     C6    PC2    PC6 MC Ch Sl  Temp DTS  Power  Volt UVolt TStat TLog #TL TMargin
     0   CPU0   -   -  2275  1400 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.43 0.822 0.805   0x0  0x0   0  12.656
     0   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.55     -     -     -  0x0   -       -
     1   CPU0   -   -  2273  1400 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.55 0.822 0.805   0x0  0x0   0  12.641
     1   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.66     -     -     -  0x0   -       -
     2   CPU0   -   -  2274  1400 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.43 0.822 0.805   0x0  0x0   0  12.641
     2   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.67     -     -     -  0x0   -       -
     3   CPU0   -   -  2276  1400 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.47 0.822 0.805   0x0  0x0   0  12.594
     3   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.62     -     -     -  0x0   -       -
     4   CPU0   -   -  2278  1400 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.53 0.807 0.805   0x0  0x0   0  12.625
     4   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.58     -     -     -  0x0   -       -
     5   CPU0   -   -  2272  1400 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.32 0.822 0.805   0x0  0x0   0  12.531
     5   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.61     -     -     -  0x0   -       -
     6   CPU0   -   -  2279  1400 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.44 0.822 0.805   0x0  0x0   0  12.438
     6   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.61     -     -     -  0x0   -       -
     7   CPU0   -   -  2272  1400 100.00 3.14 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.47 0.822 0.805   0x0  0x0   0  12.609
     7   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.75     -     -     -  0x0   -       -
     8   CPU0   -   -  2266  1400 100.00 3.14 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.52 0.822 0.805   0x0  0x0   0  12.656
     8   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.77     -     -     -  0x0   -       -
     9   CPU0   -   -  2279  1400 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.52 0.822 0.807   0x0  0x0   0  12.531
     9   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.67     -     -     -  0x0   -       -
    10   CPU0   -   -  2274  1400 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  22 184.46 0.822 0.805   0x0  0x0   0  12.703
    10   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.66     -     -     -  0x0   -       -
    11   CPU0   -   -  2276  1400 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.48 0.822 0.805   0x0  0x0   0  12.547
    11   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.58     -     -     -  0x0   -       -
    12   CPU0   -   -  2272  1400 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 183.83 0.822 0.807   0x0  0x0   0  12.469
    12   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.69     -     -     -  0x0   -       -
    13   CPU0   -   -  2273  1400 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 185.02 0.822 0.807   0x0  0x0   0  12.484
    13   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.67     -     -     -  0x0   -       -
    14   CPU0   -   -  2278  1400 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.57 0.807 0.807   0x0  0x0   0  12.438
    14   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.54     -     -     -  0x0   -       -
    15   CPU0   -   -  2275  1400 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.46 0.822 0.805   0x0  0x0   0  12.438
    15   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.63     -     -     -  0x0   -       -
    16   CPU0   -   -  2277  1400 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 183.81 0.822 0.807   0x0  0x0   0  12.344
    16   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.64     -     -     -  0x0   -       -
    17   CPU0   -   -  2272  1400 100.00 3.14 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 185.12 0.822 0.805   0x0  0x0   0  12.219
    17   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.70     -     -     -  0x0   -       -
    18   CPU0   -   -  2273  1400 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.40 0.822 0.807   0x0  0x0   0  12.266
    18   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.58     -     -     -  0x0   -       -
    19   CPU0   -   -  2271  1400 100.00 3.14 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.52 0.822 0.807   0x0  0x0   0  12.344
    19   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.73     -     -     -  0x0   -       -
    20   CPU0   -   -  2269  1400 100.00 3.14 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.44 0.822 0.807   0x0  0x0   0  12.469
    20   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.74     -     -     -  0x0   -       -
    21   CPU0   -   -  2274  1400 100.00 3.14 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.46 0.822 0.807   0x0  0x0   0  12.438
    21   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.69     -     -     -  0x0   -       -
    22   CPU0   -   -  2275  1400 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.46 0.822 0.805   0x0  0x0   0  12.297
    22   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.59     -     -     -  0x0   -       -
    23   CPU0   -   -  2274  1400 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.50 0.822 0.807   0x0  0x0   0  12.344
    23   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.66     -     -     -  0x0   -       -
    24   CPU0   -   -  2277  1400 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.48 0.822 0.805   0x0  0x0   0  12.500
    24   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.53     -     -     -  0x0   -       -
    25   CPU0   -   -  2274  1400 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.47 0.822 0.805   0x0  0x0   0  12.547
    25   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.59     -     -     -  0x0   -       -
    26   CPU0   -   -  2276  1400 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.36 0.822 0.807   0x0  0x0   0  12.500
    26   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.54     -     -     -  0x0   -       -
    27   CPU0   -   -  2273  1400 100.00 3.14 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.53 0.822 0.805   0x0  0x0   0  12.594
    27   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.68     -     -     -  0x0   -       -
    28   CPU0   -   -  2277  1400 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.56 0.807 0.807   0x0  0x0   0  12.406
    28   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.59     -     -     -  0x0   -       -
    29   CPU0   -   -  2279  1400 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.39 0.822 0.807   0x0  0x0   0  12.422
    29   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.52     -     -     -  0x0   -       -
    30   CPU0   -   -  2274  1400 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.51 0.822 0.805   0x0  0x0   0  12.219
    30   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.59     -     -     -  0x0   -       -
    31   CPU0   -   -  2280  1400 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.45 0.822 0.805   0x0  0x0   0  12.328
    31   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.55     -     -     -  0x0   -       -
^C^[
[01/12/24 18:27:00 UTC] PTU stopped.

controller-0:~#

```

## check the sensors again, to see the reaction to raised thermals

```log
controller-0:~# ipmitool sensor | grep -e CPU_0_TEMP -e CPU0_Power -e SYS_FAN_1A -e CPU_CUPS
CPU_0_TEMP       | 75.000     | degrees C  | ok    | na        | na        | na        | 96.000    | 98.000    | na
CPU0_Power       | 184.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 6125.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1A_PWM   | 22.000     | percent    | ok    | na        | na        | na        | na        | na        | na
CPU_CUPS         | 83.000     | percent    | ok    | na        | na        | na        | na        | 100.000   | na
controller-0:~#
```

## Success as we have observed thermals rising, along with fans increase in RPMs...  on to next test

## Performance Test MEAKV-643 
## Run Core IA/SSE with 100% power, and Turbo on
## ./ptu -ct 3 -cp 100 -b 1

## Sensors before run

```log
controller-0:~# ipmitool sensor | grep -e CPU_0_TEMP -e CPU0_Power -e SYS_FAN_1A -e CPU_CUPS
CPU_0_TEMP       | 57.000     | degrees C  | ok    | na        | na        | na        | 96.000    | 98.000    | na
CPU0_Power       | 106.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 5000.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1A_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
CPU_CUPS         | 0.000      | percent    | ok    | na        | na        | na        | na        | 100.000   | na
controller-0:~#

```

## Initiate Load 

```log
controller-0:~# /tmp/ptu -ct 3 -cp 100 -b 1

Command: /tmp/ptu -ct 3 -cp 100 -b 1

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
BIOS Version:                        American Megatrends International, LLC., 0.23, 06/29/2021
Processor(s):                        1 Processor(s) Installed.
DIMM(s):                             8 DIMM(s) Installed.
Total System Memory:                 127963 MB
Available System Memory:             76630 MB


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Processor: [CPU_0]             <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU ID:                              0x000606A6 (Family 6 Model 6Ah Stepping 6)
CPU Brand Name:                      Intel(R) Xeon(R) Gold 6338N CPU @ 2.20GHz
CPU Code Name:                       Ice Lake
CPU Type:                            Production Part
CPU Segment:                         Server
CPU PPIN:                            0xB3DF86FF63529310
CPU Base Frequency:                  1500 MHz
CPU Minimum Frequency:               800 MHz
CPU Maximum Turbo Frequency:         3500 MHz
Uncore Minimum Frequency:            1700 MHz
Uncore Maximum Frequency:            1700 MHz
L2 Cache:                            32 x 1280 KB
L3 Cache:                            49152 KB
Hyper-threading:                     Enabled
Microcode Update Revision:           0x0D0002A0
Number of Physcial Core(s):          32
Number of Logical Core(s):           64
Turbo Boost:                         Enabled
Turbo Boost Frequency:
 IA/SSE:
    1 - 16 Cores (Fused/Resolved):   3500 / 3500 (MHz)
   17 - 20 Cores (Fused/Resolved):   3200 / 3200 (MHz)
   21 - 22 Cores (Fused/Resolved):   3100 / 3100 (MHz)
   23 - 26 Cores (Fused/Resolved):   2900 / 2900 (MHz)
   27 - 28 Cores (Fused/Resolved):   2800 / 2800 (MHz)
   29 - 32 Cores (Fused/Resolved):   2700 / 2700 (MHz)
 AVX2:
    1 - 16 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   17 - 20 Cores (Fused/Resolved):   3100 / 3100 (MHz)
   21 - 22 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   23 - 26 Cores (Fused/Resolved):   2800 / 2800 (MHz)
   27 - 28 Cores (Fused/Resolved):   2700 / 2700 (MHz)
   29 - 32 Cores (Fused/Resolved):   2600 / 2600 (MHz)
 AVX-512:
    1 - 16 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   17 - 20 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   21 - 22 Cores (Fused/Resolved):   2900 / 2900 (MHz)
   23 - 26 Cores (Fused/Resolved):   2700 / 2700 (MHz)
   27 - 28 Cores (Fused/Resolved):   2600 / 2600 (MHz)
   29 - 32 Cores (Fused/Resolved):   2500 / 2500 (MHz)
OVOLT_OVRD Supported:                0
OVOLT_OVRD Disabled:                 1
Platform ID:                         0x0
Platform Info:                       0x8082DF2810F00000
Thermal Design Power (TDP):          185 W
Power Limit 1 - Long Duration:       Enabled, Clamp ON , Power = 185 W, Time = 1.00 sec
Power Limit 2 - Short Duration:      Enabled, Clamp ON , Power = 222 W, Time = 1000.00 sec
Config TDP Level Supported:          2
Config TDP Level 1:                  185.0 W (84.0 W - 652.0 W), 1800 MHz
Config TDP Level 2:                  185.0 W (84.0 W - 652.0 W), 1500 MHz
Current Config TDP Level:            Nominal [Locked]
Tprochot:                            98 C
TCC Offset:                          0
CAPID0:                              0x001883F9
CAPID1:                              0x0AC000C3
CAPID2:                              0x04300000
CAPID3:                              0x07804000
CAPID4:                              0x04002EC0
CAPID5:                              0x6B1FE1FB
CAPID6:                              0x3F777FF6
CAPID7:                              0x000000FB
CAPID8:                              0x3F777FF6
CAPID9:                              0x000000FB
CAPID10:                             0x00000000


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Memory: [MEM_0]                <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Number of DIMM(s):                   8
Number of Active Channel(s):         8
DRAM Power Meter Disabled:           0
DRAM RAPL Disabled:                  0
DRAM TDP Power:                      Min = 5.5 W, Max = 34.0 W, Time = 0.31 sec
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
PCH Device ID:                       8086:A1CB (Unknown Device Type)
PCH Stepping:                        10
PCH Thermal Sensor Enable:           1
PCH Hot Level (PHL):                 85
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

[01/12/24 18:38:22 UTC] PTU started.

Press <Ctrl-C> to stop.


CPU_0: [IDLE] CFreq=2493, UFreq=1700, Util=1.03, IPC=0.87, Temp=58, DTS=40, Power=106.2, Volt=0.864, UVolt=0.865
CPU_0: [TESTCFG] TestSel=3 (Core IA/SSE), CoreMask=0xFFFFFFFFFFFFFFFF, ThreadMask=0xFF, PwrLevel=100, Turbo=1
CPU_0: [RUNNING] CFreq=2189, UFreq=1400, Util=100.00, IPC=3.90, Temp=68, DTS=30, Power=184.5, Volt=0.815, UVolt=0.815


```

## ptu -mon

```log
controller-0:~# /tmp/ptu -mon

Command: /tmp/ptu -mon

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
BIOS Version:                        American Megatrends International, LLC., 0.23, 06/29/2021
Processor(s):                        1 Processor(s) Installed.
DIMM(s):                             8 DIMM(s) Installed.
Total System Memory:                 127963 MB
Available System Memory:             76622 MB


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Processor: [CPU_0]             <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU ID:                              0x000606A6 (Family 6 Model 6Ah Stepping 6)
CPU Brand Name:                      Intel(R) Xeon(R) Gold 6338N CPU @ 2.20GHz
CPU Code Name:                       Ice Lake
CPU Type:                            Production Part
CPU Segment:                         Server
CPU PPIN:                            0xB3DF86FF63529310
CPU Base Frequency:                  1500 MHz
CPU Minimum Frequency:               800 MHz
CPU Maximum Turbo Frequency:         3500 MHz
Uncore Minimum Frequency:            1700 MHz
Uncore Maximum Frequency:            1700 MHz
L2 Cache:                            32 x 1280 KB
L3 Cache:                            49152 KB
Hyper-threading:                     Enabled
Microcode Update Revision:           0x0D0002A0
Number of Physcial Core(s):          32
Number of Logical Core(s):           64
Turbo Boost:                         Enabled
Turbo Boost Frequency:
 IA/SSE:
    1 - 16 Cores (Fused/Resolved):   3500 / 3500 (MHz)
   17 - 20 Cores (Fused/Resolved):   3200 / 3200 (MHz)
   21 - 22 Cores (Fused/Resolved):   3100 / 3100 (MHz)
   23 - 26 Cores (Fused/Resolved):   2900 / 2900 (MHz)
   27 - 28 Cores (Fused/Resolved):   2800 / 2800 (MHz)
   29 - 32 Cores (Fused/Resolved):   2700 / 2700 (MHz)
 AVX2:
    1 - 16 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   17 - 20 Cores (Fused/Resolved):   3100 / 3100 (MHz)
   21 - 22 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   23 - 26 Cores (Fused/Resolved):   2800 / 2800 (MHz)
   27 - 28 Cores (Fused/Resolved):   2700 / 2700 (MHz)
   29 - 32 Cores (Fused/Resolved):   2600 / 2600 (MHz)
 AVX-512:
    1 - 16 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   17 - 20 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   21 - 22 Cores (Fused/Resolved):   2900 / 2900 (MHz)
   23 - 26 Cores (Fused/Resolved):   2700 / 2700 (MHz)
   27 - 28 Cores (Fused/Resolved):   2600 / 2600 (MHz)
   29 - 32 Cores (Fused/Resolved):   2500 / 2500 (MHz)
OVOLT_OVRD Supported:                0
OVOLT_OVRD Disabled:                 1
Platform ID:                         0x0
Platform Info:                       0x8082DF2810F00000
Thermal Design Power (TDP):          185 W
Power Limit 1 - Long Duration:       Enabled, Clamp ON , Power = 185 W, Time = 1.00 sec
Power Limit 2 - Short Duration:      Enabled, Clamp ON , Power = 222 W, Time = 1000.00 sec
Config TDP Level Supported:          2
Config TDP Level 1:                  185.0 W (84.0 W - 652.0 W), 1800 MHz
Config TDP Level 2:                  185.0 W (84.0 W - 652.0 W), 1500 MHz
Current Config TDP Level:            Nominal [Locked]
Tprochot:                            98 C
TCC Offset:                          0
CAPID0:                              0x001883F9
CAPID1:                              0x0AC000C3
CAPID2:                              0x04300000
CAPID3:                              0x07804000
CAPID4:                              0x04002EC0
CAPID5:                              0x6B1FE1FB
CAPID6:                              0x3F777FF6
CAPID7:                              0x000000FB
CAPID8:                              0x3F777FF6
CAPID9:                              0x000000FB
CAPID10:                             0x00000000


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Memory: [MEM_0]                <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Number of DIMM(s):                   8
Number of Active Channel(s):         8
DRAM Power Meter Disabled:           0
DRAM RAPL Disabled:                  0
DRAM TDP Power:                      Min = 5.5 W, Max = 34.0 W, Time = 0.31 sec
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
PCH Device ID:                       8086:A1CB (Unknown Device Type)
PCH Stepping:                        10
PCH Thermal Sensor Enable:           1
PCH Hot Level (PHL):                 85
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

[01/12/24 18:39:12 UTC] PTU started.

Press <Ctrl-C> to stop.


 Index Device Cor Thr CFreq UFreq   Util  IPC     C0     C1     C6    PC2    PC6 MC Ch Sl  Temp DTS  Power  Volt UVolt TStat TLog #TL TMargin
     0   CPU0   -   -  2185  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.46 0.810 0.807   0x0  0x0   0  13.938
     0   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.64     -     -     -  0x0   -       -
     1   CPU0   -   -  2183  1400 100.00 3.88 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.51 0.810 0.807   0x0  0x0   0  13.906
     1   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.83     -     -     -  0x0   -       -
     2   CPU0   -   -  2185  1400 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.51 0.810 0.807   0x0  0x0   0  13.750
     2   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.74     -     -     -  0x0   -       -
     3   CPU0   -   -  2185  1300 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.44 0.810 0.797   0x0  0x0   0  13.812
     3   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.61     -     -     -  0x0   -       -
     4   CPU0   -   -  2185  1300 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.43 0.810 0.797   0x0  0x0   0  13.984
     4   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.63     -     -     -  0x0   -       -
     5   CPU0   -   -  2185  1400 100.00 3.91 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.35 0.810 0.807   0x0  0x0   0  14.000
     5   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.63     -     -     -  0x0   -       -
     6   CPU0   -   -  2184  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.60 0.810 0.807   0x0  0x0   0  13.703
     6   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.67     -     -     -  0x0   -       -
     7   CPU0   -   -  2184  1400 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.46 0.810 0.807   0x0  0x0   0  13.859
     7   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.74     -     -     -  0x0   -       -
     8   CPU0   -   -  2184  1400 100.00 3.88 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.47 0.810 0.807   0x0  0x0   0  13.984
     8   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.70     -     -     -  0x0   -       -
     9   CPU0   -   -  2182  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.56 0.810 0.810   0x0  0x0   0  13.938
     9   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.62     -     -     -  0x0   -       -
    10   CPU0   -   -  2183  1400 100.00 3.87 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.46 0.797 0.807   0x0  0x0   0  14.062
    10   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.74     -     -     -  0x0   -       -
    11   CPU0   -   -  2183  1400 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.47 0.810 0.807   0x0  0x0   0  13.969
    11   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.74     -     -     -  0x0   -       -
    12   CPU0   -   -  2183  1400 100.00 3.88 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.45 0.810 0.807   0x0  0x0   0  13.938
    12   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.75     -     -     -  0x0   -       -
    13   CPU0   -   -  2182  1400 100.00 3.88 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.46 0.810 0.807   0x0  0x0   0  14.047
    13   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.78     -     -     -  0x0   -       -
    14   CPU0   -   -  2183  1400 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.46 0.810 0.807   0x0  0x0   0  13.969
    14   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.69     -     -     -  0x0   -       -
    15   CPU0   -   -  2184  1300 100.00 3.88 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.35 0.810 0.797   0x0  0x0   0  13.812
    15   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.75     -     -     -  0x0   -       -
    16   CPU0   -   -  2183  1400 100.00 3.88 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.54 0.810 0.807   0x0  0x0   0  13.922
    16   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.76     -     -     -  0x0   -       -
    17   CPU0   -   -  2182  1300 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.33 0.810 0.797   0x0  0x0   0  13.859
    17   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.73     -     -     -  0x0   -       -
    18   CPU0   -   -  2183  1400 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.61 0.810 0.807   0x0  0x0   0  13.766
    18   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.69     -     -     -  0x0   -       -
    19   CPU0   -   -  2184  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.47 0.810 0.807   0x0  0x0   0  13.844
    19   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.65     -     -     -  0x0   -       -
    20   CPU0   -   -  2184  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.49 0.810 0.807   0x0  0x0   0  13.750
    20   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.61     -     -     -  0x0   -       -
    21   CPU0   -   -  2183  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.39 0.795 0.807   0x0  0x0   0  13.781
    21   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.65     -     -     -  0x0   -       -
    22   CPU0   -   -  2183  1400 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 183.07 0.810 0.807   0x0  0x0   0  13.859
    22   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.67     -     -     -  0x0   -       -
    23   CPU0   -   -  2184  1300 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 185.89 0.810 0.797   0x0  0x0   0  13.734
    23   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.65     -     -     -  0x0   -       -
    24   CPU0   -   -  2183  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.55 0.810 0.797   0x0  0x0   0  13.812
    24   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.65     -     -     -  0x0   -       -
    25   CPU0   -   -  2183  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.45 0.810 0.807   0x0  0x0   0  13.844
    25   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.68     -     -     -  0x0   -       -
    26   CPU0   -   -  2183  1400 100.00 3.91 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.49 0.810 0.807   0x0  0x0   0  13.734
    26   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.64     -     -     -  0x0   -       -
    27   CPU0   -   -  2184  1300 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.43 0.810 0.797   0x0  0x0   0  13.719
    27   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.65     -     -     -  0x0   -       -
    28   CPU0   -   -  2182  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.46 0.810 0.807   0x0  0x0   0  13.594
    28   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.71     -     -     -  0x0   -       -
    29   CPU0   -   -  2182  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.41 0.810 0.807   0x0  0x0   0  13.609
    29   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.70     -     -     -  0x0   -       -
    30   CPU0   -   -  2182  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.39 0.810 0.807   0x0  0x0   0  13.703
    30   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.71     -     -     -  0x0   -       -
    31   CPU0   -   -  2183  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.65 0.810 0.807   0x0  0x0   0  13.547
    31   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.69     -     -     -  0x0   -       -
    32   CPU0   -   -  2182  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.36 0.807 0.807   0x0  0x0   0  13.656
    32   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.70     -     -     -  0x0   -       -
    33   CPU0   -   -  2181  1400 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.41 0.795 0.797   0x0  0x0   0  13.562
    33   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.72     -     -     -  0x0   -       -
    34   CPU0   -   -  2180  1400 100.00 3.87 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.35 0.810 0.807   0x0  0x0   0  13.547
    34   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.80     -     -     -  0x0   -       -
    35   CPU0   -   -  2182  1400 100.00 3.88 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.62 0.810 0.807   0x0  0x0   0  13.484
    35   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.74     -     -     -  0x0   -       -
    36   CPU0   -   -  2182  1300 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.65 0.795 0.797   0x0  0x0   0  13.516
    36   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.68     -     -     -  0x0   -       -
    37   CPU0   -   -  2182  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.42 0.810 0.807   0x0  0x0   0  13.562
    37   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.69     -     -     -  0x0   -       -
    38   CPU0   -   -  2183  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.49 0.810 0.807   0x0  0x0   0  13.609
    38   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.69     -     -     -  0x0   -       -
^C
[01/12/24 18:39:53 UTC] PTU stopped.

controller-0:~#
```


## Sensors after load ~2-3mins after

```log
controller-0:~# ipmitool sensor | grep -e CPU_0_TEMP -e CPU0_Power -e SYS_FAN_1A -e CPU_CUPS
CPU_0_TEMP       | 75.000     | degrees C  | ok    | na        | na        | na        | 96.000    | 98.000    | na
CPU0_Power       | 184.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 6125.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1A_PWM   | 23.000     | percent    | ok    | na        | na        | na        | na        | na        | na
CPU_CUPS         | 80.000     | percent    | ok    | na        | na        | na        | na        | 100.000   | na
controller-0:~#

```

## Test is success, observed temps rise and fan rpms rise with the load
## Performance test MEAKV-644
## PTU 3 - Core AVX2 with Turbo 
## Run Core Intel® AVX-2 with power level 100% and Turbo on.
## sudo ./ptu -ct 4 -cp 100 -b 1

## Check sensors bofore starting load

```log
controller-0:~# ipmitool sensor | grep -e CPU_0_TEMP -e CPU0_Power -e SYS_FAN_1A -e CPU_CUPS
CPU_0_TEMP       | 58.000     | degrees C  | ok    | na        | na        | na        | 96.000    | 98.000    | na
CPU0_Power       | 105.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 5000.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1A_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
CPU_CUPS         | 0.000      | percent    | ok    | na        | na        | na        | na        | 100.000   | na
controller-0:~#
```

## load Intiated

```log
controller-0:~# /tmp/ptu -ct 4 -cp 100 -b 1

Command: /tmp/ptu -ct 4 -cp 100 -b 1

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
BIOS Version:                        American Megatrends International, LLC., 0.23, 06/29/2021
Processor(s):                        1 Processor(s) Installed.
DIMM(s):                             8 DIMM(s) Installed.
Total System Memory:                 127963 MB
Available System Memory:             76614 MB


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Processor: [CPU_0]             <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU ID:                              0x000606A6 (Family 6 Model 6Ah Stepping 6)
CPU Brand Name:                      Intel(R) Xeon(R) Gold 6338N CPU @ 2.20GHz
CPU Code Name:                       Ice Lake
CPU Type:                            Production Part
CPU Segment:                         Server
CPU PPIN:                            0xB3DF86FF63529310
CPU Base Frequency:                  1500 MHz
CPU Minimum Frequency:               800 MHz
CPU Maximum Turbo Frequency:         3500 MHz
Uncore Minimum Frequency:            1700 MHz
Uncore Maximum Frequency:            1700 MHz
L2 Cache:                            32 x 1280 KB
L3 Cache:                            49152 KB
Hyper-threading:                     Enabled
Microcode Update Revision:           0x0D0002A0
Number of Physcial Core(s):          32
Number of Logical Core(s):           64
Turbo Boost:                         Enabled
Turbo Boost Frequency:
 IA/SSE:
    1 - 16 Cores (Fused/Resolved):   3500 / 3500 (MHz)
   17 - 20 Cores (Fused/Resolved):   3200 / 3200 (MHz)
   21 - 22 Cores (Fused/Resolved):   3100 / 3100 (MHz)
   23 - 26 Cores (Fused/Resolved):   2900 / 2900 (MHz)
   27 - 28 Cores (Fused/Resolved):   2800 / 2800 (MHz)
   29 - 32 Cores (Fused/Resolved):   2700 / 2700 (MHz)
 AVX2:
    1 - 16 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   17 - 20 Cores (Fused/Resolved):   3100 / 3100 (MHz)
   21 - 22 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   23 - 26 Cores (Fused/Resolved):   2800 / 2800 (MHz)
   27 - 28 Cores (Fused/Resolved):   2700 / 2700 (MHz)
   29 - 32 Cores (Fused/Resolved):   2600 / 2600 (MHz)
 AVX-512:
    1 - 16 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   17 - 20 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   21 - 22 Cores (Fused/Resolved):   2900 / 2900 (MHz)
   23 - 26 Cores (Fused/Resolved):   2700 / 2700 (MHz)
   27 - 28 Cores (Fused/Resolved):   2600 / 2600 (MHz)
   29 - 32 Cores (Fused/Resolved):   2500 / 2500 (MHz)
OVOLT_OVRD Supported:                0
OVOLT_OVRD Disabled:                 1
Platform ID:                         0x0
Platform Info:                       0x8082DF2810F00000
Thermal Design Power (TDP):          185 W
Power Limit 1 - Long Duration:       Enabled, Clamp ON , Power = 185 W, Time = 1.00 sec
Power Limit 2 - Short Duration:      Enabled, Clamp ON , Power = 222 W, Time = 1000.00 sec
Config TDP Level Supported:          2
Config TDP Level 1:                  185.0 W (84.0 W - 652.0 W), 1800 MHz
Config TDP Level 2:                  185.0 W (84.0 W - 652.0 W), 1500 MHz
Current Config TDP Level:            Nominal [Locked]
Tprochot:                            98 C
TCC Offset:                          0
CAPID0:                              0x001883F9
CAPID1:                              0x0AC000C3
CAPID2:                              0x04300000
CAPID3:                              0x07804000
CAPID4:                              0x04002EC0
CAPID5:                              0x6B1FE1FB
CAPID6:                              0x3F777FF6
CAPID7:                              0x000000FB
CAPID8:                              0x3F777FF6
CAPID9:                              0x000000FB
CAPID10:                             0x00000000


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Memory: [MEM_0]                <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Number of DIMM(s):                   8
Number of Active Channel(s):         8
DRAM Power Meter Disabled:           0
DRAM RAPL Disabled:                  0
DRAM TDP Power:                      Min = 5.5 W, Max = 34.0 W, Time = 0.31 sec
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
PCH Device ID:                       8086:A1CB (Unknown Device Type)
PCH Stepping:                        10
PCH Thermal Sensor Enable:           1
PCH Hot Level (PHL):                 85
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

[01/12/24 18:47:45 UTC] PTU started.

Press <Ctrl-C> to stop.


CPU_0: [IDLE] CFreq=2451, UFreq=1700, Util=2.85, IPC=0.85, Temp=58, DTS=40, Power=109.0, Volt=0.864, UVolt=0.865
CPU_0: [TESTCFG] TestSel=4 (Core AVX2), CoreMask=0xFFFFFFFFFFFFFFFF, ThreadMask=0xFF, PwrLevel=100, Turbo=1
CPU_0: [RUNNING] CFreq=2059, UFreq=1300, Util=100.00, IPC=3.91, Temp=69, DTS=29, Power=184.5, Volt=0.801, UVolt=0.805

```

## ptu -mon

```log
controller-0:~# /tmp/ptu -mon

Command: /tmp/ptu -mon

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
BIOS Version:                        American Megatrends International, LLC., 0.23, 06/29/2021
Processor(s):                        1 Processor(s) Installed.
DIMM(s):                             8 DIMM(s) Installed.
Total System Memory:                 127963 MB
Available System Memory:             76600 MB


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Processor: [CPU_0]             <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU ID:                              0x000606A6 (Family 6 Model 6Ah Stepping 6)
CPU Brand Name:                      Intel(R) Xeon(R) Gold 6338N CPU @ 2.20GHz
CPU Code Name:                       Ice Lake
CPU Type:                            Production Part
CPU Segment:                         Server
CPU PPIN:                            0xB3DF86FF63529310
CPU Base Frequency:                  1500 MHz
CPU Minimum Frequency:               800 MHz
CPU Maximum Turbo Frequency:         3500 MHz
Uncore Minimum Frequency:            1700 MHz
Uncore Maximum Frequency:            1700 MHz
L2 Cache:                            32 x 1280 KB
L3 Cache:                            49152 KB
Hyper-threading:                     Enabled
Microcode Update Revision:           0x0D0002A0
Number of Physcial Core(s):          32
Number of Logical Core(s):           64
Turbo Boost:                         Enabled
Turbo Boost Frequency:
 IA/SSE:
    1 - 16 Cores (Fused/Resolved):   3500 / 3500 (MHz)
   17 - 20 Cores (Fused/Resolved):   3200 / 3200 (MHz)
   21 - 22 Cores (Fused/Resolved):   3100 / 3100 (MHz)
   23 - 26 Cores (Fused/Resolved):   2900 / 2900 (MHz)
   27 - 28 Cores (Fused/Resolved):   2800 / 2800 (MHz)
   29 - 32 Cores (Fused/Resolved):   2700 / 2700 (MHz)
 AVX2:
    1 - 16 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   17 - 20 Cores (Fused/Resolved):   3100 / 3100 (MHz)
   21 - 22 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   23 - 26 Cores (Fused/Resolved):   2800 / 2800 (MHz)
   27 - 28 Cores (Fused/Resolved):   2700 / 2700 (MHz)
   29 - 32 Cores (Fused/Resolved):   2600 / 2600 (MHz)
 AVX-512:
    1 - 16 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   17 - 20 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   21 - 22 Cores (Fused/Resolved):   2900 / 2900 (MHz)
   23 - 26 Cores (Fused/Resolved):   2700 / 2700 (MHz)
   27 - 28 Cores (Fused/Resolved):   2600 / 2600 (MHz)
   29 - 32 Cores (Fused/Resolved):   2500 / 2500 (MHz)
OVOLT_OVRD Supported:                0
OVOLT_OVRD Disabled:                 1
Platform ID:                         0x0
Platform Info:                       0x8082DF2810F00000
Thermal Design Power (TDP):          185 W
Power Limit 1 - Long Duration:       Enabled, Clamp ON , Power = 185 W, Time = 1.00 sec
Power Limit 2 - Short Duration:      Enabled, Clamp ON , Power = 222 W, Time = 1000.00 sec
Config TDP Level Supported:          2
Config TDP Level 1:                  185.0 W (84.0 W - 652.0 W), 1800 MHz
Config TDP Level 2:                  185.0 W (84.0 W - 652.0 W), 1500 MHz
Current Config TDP Level:            Nominal [Locked]
Tprochot:                            98 C
TCC Offset:                          0
CAPID0:                              0x001883F9
CAPID1:                              0x0AC000C3
CAPID2:                              0x04300000
CAPID3:                              0x07804000
CAPID4:                              0x04002EC0
CAPID5:                              0x6B1FE1FB
CAPID6:                              0x3F777FF6
CAPID7:                              0x000000FB
CAPID8:                              0x3F777FF6
CAPID9:                              0x000000FB
CAPID10:                             0x00000000


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Memory: [MEM_0]                <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Number of DIMM(s):                   8
Number of Active Channel(s):         8
DRAM Power Meter Disabled:           0
DRAM RAPL Disabled:                  0
DRAM TDP Power:                      Min = 5.5 W, Max = 34.0 W, Time = 0.31 sec
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
PCH Device ID:                       8086:A1CB (Unknown Device Type)
PCH Stepping:                        10
PCH Thermal Sensor Enable:           1
PCH Hot Level (PHL):                 85
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

[01/12/24 18:48:55 UTC] PTU started.

Press <Ctrl-C> to stop.


 Index Device Cor Thr CFreq UFreq   Util  IPC     C0     C1     C6    PC2    PC6 MC Ch Sl  Temp DTS  Power  Volt UVolt TStat TLog #TL TMargin
     0   CPU0   -   -  2052  1300 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.50 0.795 0.797   0x0  0x0   0  14.203
     0   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.63     -     -     -  0x0   -       -
     1   CPU0   -   -  2051  1300 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.48 0.795 0.797   0x0  0x0   0  14.016
     1   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.61     -     -     -  0x0   -       -
     2   CPU0   -   -  2051  1300 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.43 0.795 0.797   0x0  0x0   0  14.016
     2   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.64     -     -     -  0x0   -       -
     3   CPU0   -   -  2050  1300 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.35 0.782 0.797   0x0  0x0   0  13.734
     3   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.65     -     -     -  0x0   -       -
     4   CPU0   -   -  2051  1300 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.52 0.795 0.797   0x0  0x0   0  13.828
     4   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.68     -     -     -  0x0   -       -
     5   CPU0   -   -  2052  1200 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.45 0.782 0.790   0x0  0x0   0  13.734
     5   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.65     -     -     -  0x0   -       -
     6   CPU0   -   -  2051  1300 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.62 0.782 0.905   0x0  0x0   0  13.859
     6   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.66     -     -     -  0x0   -       -
     7   CPU0   -   -  2052  1200 100.00 3.88 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.33 0.795 0.790   0x0  0x0   0  13.859
     7   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.72     -     -     -  0x0   -       -
     8   CPU0   -   -  2050  1300 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 179.25 0.795 0.797   0x0  0x0   0  14.000
     8   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.67     -     -     -  0x0   -       -
     9   CPU0   -   -  2052  1200 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 189.10 0.795 0.797   0x0  0x0   0  13.828
     9   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.73     -     -     -  0x0   -       -
    10   CPU0   -   -  2054  1300 100.00 3.87 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 185.19 0.795 0.797   0x0  0x0   0  13.812
    10   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.72     -     -     -  0x0   -       -
    11   CPU0   -   -  2051  1200 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.40 0.795 0.790   0x0  0x0   0  13.812
    11   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.65     -     -     -  0x0   -       -
    12   CPU0   -   -  2052  1300 100.00 3.88 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.46 0.795 0.797   0x0  0x0   0  13.625
    12   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.76     -     -     -  0x0   -       -
    13   CPU0   -   -  2052  1200 100.00 3.88 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.57 0.795 0.790   0x0  0x0   0  13.672
    13   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.72     -     -     -  0x0   -       -
    14   CPU0   -   -  2050  1300 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.47 0.782 0.797   0x0  0x0   0  13.953
    14   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.70     -     -     -  0x0   -       -
    15   CPU0   -   -  2050  1300 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.52 0.795 0.797   0x0  0x0   0  13.688
    15   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.61     -     -     -  0x0   -       -
    16   CPU0   -   -  2049  1200 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.44 0.780 0.790   0x0  0x0   0  13.766
    16   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.63     -     -     -  0x0   -       -
    17   CPU0   -   -  2050  1300 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.49 0.795 0.797   0x0  0x0   0  13.547
    17   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.63     -     -     -  0x0   -       -
    18   CPU0   -   -  2049  1200 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.44 0.795 0.790   0x0  0x0   0  13.359
    18   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.60     -     -     -  0x0   -       -
    19   CPU0   -   -  2050  1300 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.52 0.795 0.797   0x0  0x0   0  13.594
    19   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.56     -     -     -  0x0   -       -
    20   CPU0   -   -  2050  1300 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.53 0.795 0.797   0x0  0x0   0  13.312
    20   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.58     -     -     -  0x0   -       -
    21   CPU0   -   -  2050  1200 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.34 0.782 0.790   0x0  0x0   0  13.219
    21   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.62     -     -     -  0x0   -       -
    22   CPU0   -   -  2049  1300 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.46 0.782 0.797   0x0  0x0   0  13.234
    22   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.60     -     -     -  0x0   -       -
    23   CPU0   -   -  2049  1300 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.36 0.782 0.797   0x0  0x0   0  13.438
    23   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.58     -     -     -  0x0   -       -
    24   CPU0   -   -  2049  1200 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.70 0.795 0.790   0x0  0x0   0  13.531
    24   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.61     -     -     -  0x0   -       -
    25   CPU0   -   -  2049  1300 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.45 0.795 0.790   0x0  0x0   0  13.188
    25   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.65     -     -     -  0x0   -       -
    26   CPU0   -   -  2050  1400 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.52 0.782 0.807   0x0  0x0   0  13.266
    26   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.64     -     -     -  0x0   -       -
    27   CPU0   -   -  2050  1200 100.00 3.88 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.26 0.795 0.790   0x0  0x0   0  13.641
    27   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.76     -     -     -  0x0   -       -
    28   CPU0   -   -  2049  1200 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.61 0.795 0.790   0x0  0x0   0  13.781
    28   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.62     -     -     -  0x0   -       -
    29   CPU0   -   -  2049  1200 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.46 0.795 0.790   0x0  0x0   0  13.094
    29   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.67     -     -     -  0x0   -       -
    30   CPU0   -   -  2049  1200 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.46 0.782 0.790   0x0  0x0   0  13.281
    30   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.64     -     -     -  0x0   -       -
    31   CPU0   -   -  2048  1200 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.34 0.795 0.790   0x0  0x0   0  13.141
    31   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.67     -     -     -  0x0   -       -
    32   CPU0   -   -  2049  1200 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.68 0.780 0.790   0x0  0x0   0  13.359
    32   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.74     -     -     -  0x0   -       -
    33   CPU0   -   -  2049  1200 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.43 0.795 0.790   0x0  0x0   0  13.375
    33   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.59     -     -     -  0x0   -       -
    34   CPU0   -   -  2048  1200 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.44 0.795 0.790   0x0  0x0   0  13.234
    34   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.61     -     -     -  0x0   -       -
    35   CPU0   -   -  2049  1300 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.37 0.780 0.797   0x0  0x0   0  13.562
    35   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.59     -     -     -  0x0   -       -
    36   CPU0   -   -  2049  1200 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.55 0.780 0.790   0x0  0x0   0  13.203
    36   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.66     -     -     -  0x0   -       -
    37   CPU0   -   -  2049  1200 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.54 0.780 0.790   0x0  0x0   0  13.312
    37   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.69     -     -     -  0x0   -       -
    38   CPU0   -   -  2049  1300 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.40 0.782 0.797   0x0  0x0   0  13.375
    38   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.60     -     -     -  0x0   -       -
    39   CPU0   -   -  2050  1200 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.35 0.795 0.790   0x0  0x0   0  13.234
    39   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.67     -     -     -  0x0   -       -
    40   CPU0   -   -  2049  1300 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.64 0.780 0.797   0x0  0x0   0  13.250
    40   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.59     -     -     -  0x0   -       -
    41   CPU0   -   -  2049  1200 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.49 0.795 0.790   0x0  0x0   0  13.422
    41   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.66     -     -     -  0x0   -       -
    42   CPU0   -   -  2049  1300 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.44 0.780 0.797   0x0  0x0   0  13.578
    42   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.66     -     -     -  0x0   -       -
    43   CPU0   -   -  2048  1200 100.00 3.91 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.46 0.795 0.790   0x0  0x0   0  13.406
    43   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.60     -     -     -  0x0   -       -
    44   CPU0   -   -  2049  1300 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.43 0.795 0.797   0x0  0x0   0  13.375
    44   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.68     -     -     -  0x0   -       -
    45   CPU0   -   -  2048  1300 100.00 3.91 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.58 0.795 0.797   0x0  0x0   0  13.531
    45   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.57     -     -     -  0x0   -       -
    46   CPU0   -   -  2049  1200 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.46 0.795 0.790   0x0  0x0   0  13.203
    46   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.63     -     -     -  0x0   -       -
    47   CPU0   -   -  2050  1300 100.00 3.88 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.45 0.780 0.797   0x0  0x0   0  13.234
    47   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.70     -     -     -  0x0   -       -
    48   CPU0   -   -  2048  1300 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.47 0.780 0.797   0x0  0x0   0  13.328
    48   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.58     -     -     -  0x0   -       -
    49   CPU0   -   -  2049  1300 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.40 0.795 0.797   0x0  0x0   0  13.359
    49   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.64     -     -     -  0x0   -       -
    50   CPU0   -   -  2049  1200 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.57 0.795 0.790   0x0  0x0   0  13.266
    50   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.69     -     -     -  0x0   -       -
    51   CPU0   -   -  2051  1300 100.00 3.87 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.44 0.795 0.797   0x0  0x0   0  13.141
    51   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.77     -     -     -  0x0   -       -
    52   CPU0   -   -  2052  1300 100.00 3.87 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.41 0.795 0.797   0x0  0x0   0  13.000
    52   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.80     -     -     -  0x0   -       -
    53   CPU0   -   -  2050  1200 100.00 3.88 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.44 0.795 0.797   0x0  0x0   0  12.938
    53   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.69     -     -     -  0x0   -       -
^C
[01/12/24 18:49:52 UTC] PTU stopped.

controller-0:~#
```

## check sensors after load 

```log
controller-0:~# ipmitool sensor | grep -e CPU_0_TEMP -e CPU0_Power -e SYS_FAN_1A -e CPU_CUPS
CPU_0_TEMP       | 75.000     | degrees C  | ok    | na        | na        | na        | 96.000    | 98.000    | na
CPU0_Power       | 184.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 6125.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1A_PWM   | 23.000     | percent    | ok    | na        | na        | na        | na        | na        | na
CPU_CUPS         | 75.000     | percent    | ok    | na        | na        | na        | na        | 100.000   | na
controller-0:~#
```

## Observed temps raise and fans rpm raise with load - success

## MEAKV-645
## PTU 4 - Core AVX512 with Turbo
## sudo ./ptu -ct 5 -cp 100 -b 1


## Sensors before load

```log
[controller-0:~# ipmitool sensor | grep -e CPU_0_TEMP -e CPU0_Power -e SYS_FAN_1A -e CPU_CUPS
CPU_0_TEMP       | 58.000     | degrees C  | ok    | na        | na        | na        | 96.000    | 98.000    | na
CPU0_Power       | 108.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 5000.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1A_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
CPU_CUPS         | 0.000      | percent    | ok    | na        | na        | na        | na        | 100.000   | na
controller-0:~#
```

## Initate load

```log
controller-0:~# /tmp/ptu -ct 5 -cp 100 -b 1

Command: /tmp/ptu -ct 5 -cp 100 -b 1

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
BIOS Version:                        American Megatrends International, LLC., 0.23, 06/29/2021
Processor(s):                        1 Processor(s) Installed.
DIMM(s):                             8 DIMM(s) Installed.
Total System Memory:                 127963 MB
Available System Memory:             76622 MB


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Processor: [CPU_0]             <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU ID:                              0x000606A6 (Family 6 Model 6Ah Stepping 6)
CPU Brand Name:                      Intel(R) Xeon(R) Gold 6338N CPU @ 2.20GHz
CPU Code Name:                       Ice Lake
CPU Type:                            Production Part
CPU Segment:                         Server
CPU PPIN:                            0xB3DF86FF63529310
CPU Base Frequency:                  1500 MHz
CPU Minimum Frequency:               800 MHz
CPU Maximum Turbo Frequency:         3500 MHz
Uncore Minimum Frequency:            1700 MHz
Uncore Maximum Frequency:            1700 MHz
L2 Cache:                            32 x 1280 KB
L3 Cache:                            49152 KB
Hyper-threading:                     Enabled
Microcode Update Revision:           0x0D0002A0
Number of Physcial Core(s):          32
Number of Logical Core(s):           64
Turbo Boost:                         Enabled
Turbo Boost Frequency:
 IA/SSE:
    1 - 16 Cores (Fused/Resolved):   3500 / 3500 (MHz)
   17 - 20 Cores (Fused/Resolved):   3200 / 3200 (MHz)
   21 - 22 Cores (Fused/Resolved):   3100 / 3100 (MHz)
   23 - 26 Cores (Fused/Resolved):   2900 / 2900 (MHz)
   27 - 28 Cores (Fused/Resolved):   2800 / 2800 (MHz)
   29 - 32 Cores (Fused/Resolved):   2700 / 2700 (MHz)
 AVX2:
    1 - 16 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   17 - 20 Cores (Fused/Resolved):   3100 / 3100 (MHz)
   21 - 22 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   23 - 26 Cores (Fused/Resolved):   2800 / 2800 (MHz)
   27 - 28 Cores (Fused/Resolved):   2700 / 2700 (MHz)
   29 - 32 Cores (Fused/Resolved):   2600 / 2600 (MHz)
 AVX-512:
    1 - 16 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   17 - 20 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   21 - 22 Cores (Fused/Resolved):   2900 / 2900 (MHz)
   23 - 26 Cores (Fused/Resolved):   2700 / 2700 (MHz)
   27 - 28 Cores (Fused/Resolved):   2600 / 2600 (MHz)
   29 - 32 Cores (Fused/Resolved):   2500 / 2500 (MHz)
OVOLT_OVRD Supported:                0
OVOLT_OVRD Disabled:                 1
Platform ID:                         0x0
Platform Info:                       0x8082DF2810F00000
Thermal Design Power (TDP):          185 W
Power Limit 1 - Long Duration:       Enabled, Clamp ON , Power = 185 W, Time = 1.00 sec
Power Limit 2 - Short Duration:      Enabled, Clamp ON , Power = 222 W, Time = 1000.00 sec
Config TDP Level Supported:          2
Config TDP Level 1:                  185.0 W (84.0 W - 652.0 W), 1800 MHz
Config TDP Level 2:                  185.0 W (84.0 W - 652.0 W), 1500 MHz
Current Config TDP Level:            Nominal [Locked]
Tprochot:                            98 C
TCC Offset:                          0
CAPID0:                              0x001883F9
CAPID1:                              0x0AC000C3
CAPID2:                              0x04300000
CAPID3:                              0x07804000
CAPID4:                              0x04002EC0
CAPID5:                              0x6B1FE1FB
CAPID6:                              0x3F777FF6
CAPID7:                              0x000000FB
CAPID8:                              0x3F777FF6
CAPID9:                              0x000000FB
CAPID10:                             0x00000000


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Memory: [MEM_0]                <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Number of DIMM(s):                   8
Number of Active Channel(s):         8
DRAM Power Meter Disabled:           0
DRAM RAPL Disabled:                  0
DRAM TDP Power:                      Min = 5.5 W, Max = 34.0 W, Time = 0.31 sec
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
PCH Device ID:                       8086:A1CB (Unknown Device Type)
PCH Stepping:                        10
PCH Thermal Sensor Enable:           1
PCH Hot Level (PHL):                 85
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

[01/12/24 18:58:59 UTC] PTU started.

Press <Ctrl-C> to stop.


CPU_0: [IDLE] CFreq=2499, UFreq=1700, Util=1.15, IPC=0.87, Temp=58, DTS=40, Power=106.4, Volt=0.864, UVolt=0.865
CPU_0: [TESTCFG] TestSel=5 (Core AVX-512), CoreMask=0xFFFFFFFFFFFFFFFF, ThreadMask=0xFF, PwrLevel=100, Turbo=1
CPU_0: [RUNNING] CFreq=1997, UFreq=1200, Util=100.00, IPC=3.45, Temp=69, DTS=29, Power=184.4, Volt=0.774, UVolt=0.795

```

## ptu -mon

```log
controller-0:~# /tmp/ptu -mon

Command: /tmp/ptu -mon

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
BIOS Version:                        American Megatrends International, LLC., 0.23, 06/29/2021
Processor(s):                        1 Processor(s) Installed.
DIMM(s):                             8 DIMM(s) Installed.
Total System Memory:                 127963 MB
Available System Memory:             76469 MB


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Processor: [CPU_0]             <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU ID:                              0x000606A6 (Family 6 Model 6Ah Stepping 6)
CPU Brand Name:                      Intel(R) Xeon(R) Gold 6338N CPU @ 2.20GHz
CPU Code Name:                       Ice Lake
CPU Type:                            Production Part
CPU Segment:                         Server
CPU PPIN:                            0xB3DF86FF63529310
CPU Base Frequency:                  1500 MHz
CPU Minimum Frequency:               800 MHz
CPU Maximum Turbo Frequency:         3500 MHz
Uncore Minimum Frequency:            1700 MHz
Uncore Maximum Frequency:            1700 MHz
L2 Cache:                            32 x 1280 KB
L3 Cache:                            49152 KB
Hyper-threading:                     Enabled
Microcode Update Revision:           0x0D0002A0
Number of Physcial Core(s):          32
Number of Logical Core(s):           64
Turbo Boost:                         Enabled
Turbo Boost Frequency:
 IA/SSE:
    1 - 16 Cores (Fused/Resolved):   3500 / 3500 (MHz)
   17 - 20 Cores (Fused/Resolved):   3200 / 3200 (MHz)
   21 - 22 Cores (Fused/Resolved):   3100 / 3100 (MHz)
   23 - 26 Cores (Fused/Resolved):   2900 / 2900 (MHz)
   27 - 28 Cores (Fused/Resolved):   2800 / 2800 (MHz)
   29 - 32 Cores (Fused/Resolved):   2700 / 2700 (MHz)
 AVX2:
    1 - 16 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   17 - 20 Cores (Fused/Resolved):   3100 / 3100 (MHz)
   21 - 22 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   23 - 26 Cores (Fused/Resolved):   2800 / 2800 (MHz)
   27 - 28 Cores (Fused/Resolved):   2700 / 2700 (MHz)
   29 - 32 Cores (Fused/Resolved):   2600 / 2600 (MHz)
 AVX-512:
    1 - 16 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   17 - 20 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   21 - 22 Cores (Fused/Resolved):   2900 / 2900 (MHz)
   23 - 26 Cores (Fused/Resolved):   2700 / 2700 (MHz)
   27 - 28 Cores (Fused/Resolved):   2600 / 2600 (MHz)
   29 - 32 Cores (Fused/Resolved):   2500 / 2500 (MHz)
OVOLT_OVRD Supported:                0
OVOLT_OVRD Disabled:                 1
Platform ID:                         0x0
Platform Info:                       0x8082DF2810F00000
Thermal Design Power (TDP):          185 W
Power Limit 1 - Long Duration:       Enabled, Clamp ON , Power = 185 W, Time = 1.00 sec
Power Limit 2 - Short Duration:      Enabled, Clamp ON , Power = 222 W, Time = 1000.00 sec
Config TDP Level Supported:          2
Config TDP Level 1:                  185.0 W (84.0 W - 652.0 W), 1800 MHz
Config TDP Level 2:                  185.0 W (84.0 W - 652.0 W), 1500 MHz
Current Config TDP Level:            Nominal [Locked]
Tprochot:                            98 C
TCC Offset:                          0
CAPID0:                              0x001883F9
CAPID1:                              0x0AC000C3
CAPID2:                              0x04300000
CAPID3:                              0x07804000
CAPID4:                              0x04002EC0
CAPID5:                              0x6B1FE1FB
CAPID6:                              0x3F777FF6
CAPID7:                              0x000000FB
CAPID8:                              0x3F777FF6
CAPID9:                              0x000000FB
CAPID10:                             0x00000000


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Memory: [MEM_0]                <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Number of DIMM(s):                   8
Number of Active Channel(s):         8
DRAM Power Meter Disabled:           0
DRAM RAPL Disabled:                  0
DRAM TDP Power:                      Min = 5.5 W, Max = 34.0 W, Time = 0.31 sec
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
PCH Device ID:                       8086:A1CB (Unknown Device Type)
PCH Stepping:                        10
PCH Thermal Sensor Enable:           1
PCH Hot Level (PHL):                 85
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

[01/12/24 18:59:49 UTC] PTU started.

Press <Ctrl-C> to stop.


 Index Device Cor Thr CFreq UFreq   Util  IPC     C0     C1     C6    PC2    PC6 MC Ch Sl  Temp DTS  Power  Volt UVolt TStat TLog #TL TMargin
     0   CPU0   -   -  1996  1200 100.00 3.46 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.41 0.782 0.790   0x0  0x0   0  13.906
     0   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.58     -     -     -  0x0   -       -
     1   CPU0   -   -  1999  1200 100.00 3.46 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.52 0.795 0.790   0x0  0x0   0  13.781
     1   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.60     -     -     -  0x0   -       -
     2   CPU0   -   -  2004  1200 100.00 3.46 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.43 0.782 0.790   0x0  0x0   0  13.766
     2   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.65     -     -     -  0x0   -       -
     3   CPU0   -   -  2002  1200 100.00 3.44 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.54 0.782 0.790   0x0  0x0   0  13.625
     3   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.79     -     -     -  0x0   -       -
     4   CPU0   -   -  2000  1200 100.00 3.46 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.45 0.782 0.790   0x0  0x0   0  13.625
     4   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.59     -     -     -  0x0   -       -
     5   CPU0   -   -  2003  1200 100.00 3.46 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.59 0.782 0.790   0x0  0x0   0  13.625
     5   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.63     -     -     -  0x0   -       -
     6   CPU0   -   -  1996  1200 100.00 3.46 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.50 0.782 0.790   0x0  0x0   0  13.641
     6   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.64     -     -     -  0x0   -       -
     7   CPU0   -   -  2002  1200 100.00 3.45 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.46 0.782 0.790   0x0  0x0   0  13.703
     7   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.69     -     -     -  0x0   -       -
     8   CPU0   -   -  1998  1200 100.00 3.46 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.50 0.782 0.790   0x0  0x0   0  13.594
     8   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.68     -     -     -  0x0   -       -
     9   CPU0   -   -  2002  1200 100.00 3.46 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.32 0.782 0.790   0x0  0x0   0  13.625
     9   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.61     -     -     -  0x0   -       -
    10   CPU0   -   -  2003  1200 100.00 3.45 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.60 0.797 0.790   0x0  0x0   0  13.438
    10   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.68     -     -     -  0x0   -       -
    11   CPU0   -   -  2003  1200 100.00 3.44 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.47 0.782 0.790   0x0  0x0   0  13.469
    11   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.76     -     -     -  0x0   -       -
    12   CPU0   -   -  2003  1200 100.00 3.44 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.44 0.782 0.790   0x0  0x0   0  13.422
    12   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.75     -     -     -  0x0   -       -
    13   CPU0   -   -  2007  1300 100.00 3.41 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.41 0.782 0.797   0x0  0x0   0  13.234
    13   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.87     -     -     -  0x0   -       -
    14   CPU0   -   -  2005  1200 100.00 3.44 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.40 0.785 0.790   0x0  0x0   0  13.125
    14   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.75     -     -     -  0x0   -       -
    15   CPU0   -   -  2007  1200 100.00 3.43 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.64 0.782 0.790   0x0  0x0   0  13.016
    15   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.77     -     -     -  0x0   -       -
    16   CPU0   -   -  2007  1200 100.00 3.42 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.45 0.782 0.790   0x0  0x0   0  13.094
    16   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.79     -     -     -  0x0   -       -
    17   CPU0   -   -  2006  1200 100.00 3.43 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.47 0.782 0.790   0x0  0x0   0  13.078
    17   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.80     -     -     -  0x0   -       -
    18   CPU0   -   -  2007  1200 100.00 3.42 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.36 0.797 0.790   0x0  0x0   0  12.828
    18   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.81     -     -     -  0x0   -       -
    19   CPU0   -   -  2005  1200 100.00 3.43 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.62 0.782 0.790   0x0  0x0   0  13.000
    19   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.77     -     -     -  0x0   -       -
    20   CPU0   -   -  2005  1200 100.00 3.43 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.37 0.785 0.790   0x0  0x0   0  12.938
    20   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.77     -     -     -  0x0   -       -
    21   CPU0   -   -  2004  1200 100.00 3.45 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.48 0.782 0.790   0x0  0x0   0  12.906
    21   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.67     -     -     -  0x0   -       -
    22   CPU0   -   -  1997  1200 100.00 3.46 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.41 0.782 0.790   0x0  0x0   0  13.234
    22   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.67     -     -     -  0x0   -       -
    23   CPU0   -   -  2006  1200 100.00 3.44 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.55 0.782 0.790   0x0  0x0   0  13.375
    23   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.78     -     -     -  0x0   -       -
    24   CPU0   -   -  1994  1200 100.00 3.46 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.47 0.782 0.790   0x0  0x0   0  13.125
    24   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.62     -     -     -  0x0   -       -
    25   CPU0   -   -  1997  1200 100.00 3.46 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.44 0.782 0.790   0x0  0x0   0  13.031
    25   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.58     -     -     -  0x0   -       -
    26   CPU0   -   -  1999  1200 100.00 3.46 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.55 0.782 0.790   0x0  0x0   0  13.172
    26   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.56     -     -     -  0x0   -       -
    27   CPU0   -   -  1999  1200 100.00 3.45 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.45 0.782 0.790   0x0  0x0   0  13.141
    27   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.66     -     -     -  0x0   -       -
    28   CPU0   -   -  1999  1300 100.00 3.45 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.50 0.780 0.797   0x0  0x0   0  13.062
    28   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.66     -     -     -  0x0   -       -
    29   CPU0   -   -  1998  1200 100.00 3.45 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.33 0.782 0.790   0x0  0x0   0  12.859
    29   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.62     -     -     -  0x0   -       -
    30   CPU0   -   -  2004  1200 100.00 3.44 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.62 0.782 0.790   0x0  0x0   0  12.688
    30   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.69     -     -     -  0x0   -       -
    31   CPU0   -   -  2000  1200 100.00 3.44 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.25 0.780 0.790   0x0  0x0   0  12.578
    31   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.70     -     -     -  0x0   -       -
    32   CPU0   -   -  1999  1200 100.00 3.46 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.60 0.782 0.790   0x0  0x0   0  12.969
    32   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.57     -     -     -  0x0   -       -
    33   CPU0   -   -  2002  1200 100.00 3.45 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.45 0.782 0.790   0x0  0x0   0  12.984
    33   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.74     -     -     -  0x0   -       -
    34   CPU0   -   -  1998  1200 100.00 3.46 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.32 0.795 0.790   0x0  0x0   0  12.984
    34   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.46     -     -     -  0x0   -       -
    35   CPU0   -   -  1994  1200 100.00 3.45 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.51 0.780 0.790   0x0  0x0   0  12.938
    35   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.58     -     -     -  0x0   -       -
    36   CPU0   -   -  1997  1300 100.00 3.46 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.49 0.780 0.797   0x0  0x0   0  12.828
    36   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.59     -     -     -  0x0   -       -
    37   CPU0   -   -  1999  1200 100.00 3.45 100.00   0.00   0.00   0.00   0.00  -  -  -    75  22 184.53 0.780 0.790   0x0  0x0   0  12.766
    37   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.78     -     -     -  0x0   -       -
    38   CPU0   -   -  2002  1200 100.00 3.45 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.58 0.780 0.790   0x0  0x0   0  12.750
    38   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.68     -     -     -  0x0   -       -
    39   CPU0   -   -  2001  1200 100.00 3.45 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.46 0.780 0.790   0x0  0x0   0  12.719
    39   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.68     -     -     -  0x0   -       -
    40   CPU0   -   -  1994  1200 100.00 3.46 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.34 0.782 0.790   0x0  0x0   0  12.797
    40   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.51     -     -     -  0x0   -       -
    41   CPU0   -   -  1998  1300 100.00 3.46 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.52 0.782 0.797   0x0  0x0   0  12.688
    41   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.57     -     -     -  0x0   -       -
    42   CPU0   -   -  1992  1200 100.00 3.46 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.50 0.780 0.790   0x0  0x0   0  12.531
    42   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.60     -     -     -  0x0   -       -
    43   CPU0   -   -  1998  1200 100.00 3.45 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.48 0.780 0.790   0x0  0x0   0  12.719
    43   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.72     -     -     -  0x0   -       -
    44   CPU0   -   -  1989  1200 100.00 3.46 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.44 0.780 0.790   0x0  0x0   0  12.719
    44   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.52     -     -     -  0x0   -       -
    45   CPU0   -   -  1997  1200 100.00 3.45 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.57 0.782 0.790   0x0  0x0   0  12.703
    45   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.64     -     -     -  0x0   -       -
^C
[01/12/24 19:00:38 UTC] PTU stopped.

controller-0:~#
```

## check sensors

```log
controller-0:~# ipmitool sensor | grep -e CPU_0_TEMP -e CPU0_Power -e SYS_FAN_1A -e CPU_CUPS
CPU_0_TEMP       | 76.000     | degrees C  | ok    | na        | na        | na        | 96.000    | 98.000    | na
CPU0_Power       | 184.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 6125.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1A_PWM   | 23.000     | percent    | ok    | na        | na        | na        | na        | na        | na
CPU_CUPS         | 72.000     | percent    | ok    | na        | na        | na        | na        | 100.000   | na
controller-0:~#
```


## Success, was able to observe temp rise, then fans increasing as load was started


## MEAKV-646 
## PTU 5 - Turbo Test
## sudo ./ptu -ct 8 -allcore -b 1

## sensors before load

```log
controller-0:~# ipmitool sensor | grep -e CPU_0_TEMP -e CPU0_Power -e SYS_FAN_1A -e CPU_CUPS
CPU_0_TEMP       | 57.000     | degrees C  | ok    | na        | na        | na        | 96.000    | 98.000    | na
CPU0_Power       | 106.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 5000.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1A_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
CPU_CUPS         | 0.000      | percent    | ok    | na        | na        | na        | na        | 100.000   | na
controller-0:~#
```

## Initiating load

```log
controller-0:~# /tmp/ptu -ct 8 -allcore -b 1

Command: /tmp/ptu -ct 8 -allcore -b 1

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
BIOS Version:                        American Megatrends International, LLC., 0.23, 06/29/2021
Processor(s):                        1 Processor(s) Installed.
DIMM(s):                             8 DIMM(s) Installed.
Total System Memory:                 127963 MB
Available System Memory:             76567 MB


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Processor: [CPU_0]             <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU ID:                              0x000606A6 (Family 6 Model 6Ah Stepping 6)
CPU Brand Name:                      Intel(R) Xeon(R) Gold 6338N CPU @ 2.20GHz
CPU Code Name:                       Ice Lake
CPU Type:                            Production Part
CPU Segment:                         Server
CPU PPIN:                            0xB3DF86FF63529310
CPU Base Frequency:                  1500 MHz
CPU Minimum Frequency:               800 MHz
CPU Maximum Turbo Frequency:         3500 MHz
Uncore Minimum Frequency:            1700 MHz
Uncore Maximum Frequency:            1700 MHz
L2 Cache:                            32 x 1280 KB
L3 Cache:                            49152 KB
Hyper-threading:                     Enabled
Microcode Update Revision:           0x0D0002A0
Number of Physcial Core(s):          32
Number of Logical Core(s):           64
Turbo Boost:                         Enabled
Turbo Boost Frequency:
 IA/SSE:
    1 - 16 Cores (Fused/Resolved):   3500 / 3500 (MHz)
   17 - 20 Cores (Fused/Resolved):   3200 / 3200 (MHz)
   21 - 22 Cores (Fused/Resolved):   3100 / 3100 (MHz)
   23 - 26 Cores (Fused/Resolved):   2900 / 2900 (MHz)
   27 - 28 Cores (Fused/Resolved):   2800 / 2800 (MHz)
   29 - 32 Cores (Fused/Resolved):   2700 / 2700 (MHz)
 AVX2:
    1 - 16 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   17 - 20 Cores (Fused/Resolved):   3100 / 3100 (MHz)
   21 - 22 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   23 - 26 Cores (Fused/Resolved):   2800 / 2800 (MHz)
   27 - 28 Cores (Fused/Resolved):   2700 / 2700 (MHz)
   29 - 32 Cores (Fused/Resolved):   2600 / 2600 (MHz)
 AVX-512:
    1 - 16 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   17 - 20 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   21 - 22 Cores (Fused/Resolved):   2900 / 2900 (MHz)
   23 - 26 Cores (Fused/Resolved):   2700 / 2700 (MHz)
   27 - 28 Cores (Fused/Resolved):   2600 / 2600 (MHz)
   29 - 32 Cores (Fused/Resolved):   2500 / 2500 (MHz)
OVOLT_OVRD Supported:                0
OVOLT_OVRD Disabled:                 1
Platform ID:                         0x0
Platform Info:                       0x8082DF2810F00000
Thermal Design Power (TDP):          185 W
Power Limit 1 - Long Duration:       Enabled, Clamp ON , Power = 185 W, Time = 1.00 sec
Power Limit 2 - Short Duration:      Enabled, Clamp ON , Power = 222 W, Time = 1000.00 sec
Config TDP Level Supported:          2
Config TDP Level 1:                  185.0 W (84.0 W - 652.0 W), 1800 MHz
Config TDP Level 2:                  185.0 W (84.0 W - 652.0 W), 1500 MHz
Current Config TDP Level:            Nominal [Locked]
Tprochot:                            98 C
TCC Offset:                          0
CAPID0:                              0x001883F9
CAPID1:                              0x0AC000C3
CAPID2:                              0x04300000
CAPID3:                              0x07804000
CAPID4:                              0x04002EC0
CAPID5:                              0x6B1FE1FB
CAPID6:                              0x3F777FF6
CAPID7:                              0x000000FB
CAPID8:                              0x3F777FF6
CAPID9:                              0x000000FB
CAPID10:                             0x00000000


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Memory: [MEM_0]                <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Number of DIMM(s):                   8
Number of Active Channel(s):         8
DRAM Power Meter Disabled:           0
DRAM RAPL Disabled:                  0
DRAM TDP Power:                      Min = 5.5 W, Max = 34.0 W, Time = 0.31 sec
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
PCH Device ID:                       8086:A1CB (Unknown Device Type)
PCH Stepping:                        10
PCH Thermal Sensor Enable:           1
PCH Hot Level (PHL):                 85
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

[01/12/24 19:16:25 UTC] PTU started.

Press <Ctrl-C> to stop.


CPU_0: [IDLE] CFreq=2493, UFreq=1700, Util=0.50, IPC=0.88, Temp=58, DTS=40, Power=105.7, Volt=0.863, UVolt=0.865

### TURBO is enabled ###

Instr   CPU #Cores CFreq(act) CFreq(exp) UFreq Power TDP  Temp Volt  UVolt
IA/SSE  0   32     2.5        2.7        1.7   155.3 185  65   0.858 0.862

```

## ptu -mon

```log
controller-0:~# /tmp/ptu -mon

Command: /tmp/ptu -mon

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
BIOS Version:                        American Megatrends International, LLC., 0.23, 06/29/2021
Processor(s):                        1 Processor(s) Installed.
DIMM(s):                             8 DIMM(s) Installed.
Total System Memory:                 127963 MB
Available System Memory:             76565 MB


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Processor: [CPU_0]             <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU ID:                              0x000606A6 (Family 6 Model 6Ah Stepping 6)
CPU Brand Name:                      Intel(R) Xeon(R) Gold 6338N CPU @ 2.20GHz
CPU Code Name:                       Ice Lake
CPU Type:                            Production Part
CPU Segment:                         Server
CPU PPIN:                            0xB3DF86FF63529310
CPU Base Frequency:                  1500 MHz
CPU Minimum Frequency:               800 MHz
CPU Maximum Turbo Frequency:         3500 MHz
Uncore Minimum Frequency:            1700 MHz
Uncore Maximum Frequency:            1700 MHz
L2 Cache:                            32 x 1280 KB
L3 Cache:                            49152 KB
Hyper-threading:                     Enabled
Microcode Update Revision:           0x0D0002A0
Number of Physcial Core(s):          32
Number of Logical Core(s):           64
Turbo Boost:                         Enabled
Turbo Boost Frequency:
 IA/SSE:
    1 - 16 Cores (Fused/Resolved):   3500 / 3500 (MHz)
   17 - 20 Cores (Fused/Resolved):   3200 / 3200 (MHz)
   21 - 22 Cores (Fused/Resolved):   3100 / 3100 (MHz)
   23 - 26 Cores (Fused/Resolved):   2900 / 2900 (MHz)
   27 - 28 Cores (Fused/Resolved):   2800 / 2800 (MHz)
   29 - 32 Cores (Fused/Resolved):   2700 / 2700 (MHz)
 AVX2:
    1 - 16 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   17 - 20 Cores (Fused/Resolved):   3100 / 3100 (MHz)
   21 - 22 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   23 - 26 Cores (Fused/Resolved):   2800 / 2800 (MHz)
   27 - 28 Cores (Fused/Resolved):   2700 / 2700 (MHz)
   29 - 32 Cores (Fused/Resolved):   2600 / 2600 (MHz)
 AVX-512:
    1 - 16 Cores (Fused/Resolved):   3300 / 3300 (MHz)
   17 - 20 Cores (Fused/Resolved):   3000 / 3000 (MHz)
   21 - 22 Cores (Fused/Resolved):   2900 / 2900 (MHz)
   23 - 26 Cores (Fused/Resolved):   2700 / 2700 (MHz)
   27 - 28 Cores (Fused/Resolved):   2600 / 2600 (MHz)
   29 - 32 Cores (Fused/Resolved):   2500 / 2500 (MHz)
OVOLT_OVRD Supported:                0
OVOLT_OVRD Disabled:                 1
Platform ID:                         0x0
Platform Info:                       0x8082DF2810F00000
Thermal Design Power (TDP):          185 W
Power Limit 1 - Long Duration:       Enabled, Clamp ON , Power = 185 W, Time = 1.00 sec
Power Limit 2 - Short Duration:      Enabled, Clamp ON , Power = 222 W, Time = 1000.00 sec
Config TDP Level Supported:          2
Config TDP Level 1:                  185.0 W (84.0 W - 652.0 W), 1800 MHz
Config TDP Level 2:                  185.0 W (84.0 W - 652.0 W), 1500 MHz
Current Config TDP Level:            Nominal [Locked]
Tprochot:                            98 C
TCC Offset:                          0
CAPID0:                              0x001883F9
CAPID1:                              0x0AC000C3
CAPID2:                              0x04300000
CAPID3:                              0x07804000
CAPID4:                              0x04002EC0
CAPID5:                              0x6B1FE1FB
CAPID6:                              0x3F777FF6
CAPID7:                              0x000000FB
CAPID8:                              0x3F777FF6
CAPID9:                              0x000000FB
CAPID10:                             0x00000000


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Memory: [MEM_0]                <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Number of DIMM(s):                   8
Number of Active Channel(s):         8
DRAM Power Meter Disabled:           0
DRAM RAPL Disabled:                  0
DRAM TDP Power:                      Min = 5.5 W, Max = 34.0 W, Time = 0.31 sec
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
PCH Device ID:                       8086:A1CB (Unknown Device Type)
PCH Stepping:                        10
PCH Thermal Sensor Enable:           1
PCH Hot Level (PHL):                 85
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

[01/12/24 19:19:06 UTC] PTU started.

Press <Ctrl-C> to stop.


 Index Device Cor Thr CFreq UFreq   Util  IPC     C0     C1     C6    PC2    PC6 MC Ch Sl  Temp DTS  Power  Volt UVolt TStat TLog #TL TMargin
     0   CPU0   -   -  2509  1700   1.80 0.93   3.14  96.86   0.00   0.00   0.00  -  -  -    59  39 108.24 0.862 0.865   0x0  0x0   0  29.234
     0   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.83     -     -     -  0x0   -       -
     1   CPU0   -   -  2491  1700   1.05 0.89   1.86  98.14   0.00   0.00   0.00  -  -  -    58  40 106.63 0.862 0.865   0x0  0x0   0  29.750
     1   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.81     -     -     -  0x0   -       -
     2   CPU0   -   -  2498  1700   1.38 0.88   2.35  97.65   0.00   0.00   0.00  -  -  -    58  40 107.22 0.862 0.865   0x0  0x0   0  29.844
     2   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.82     -     -     -  0x0   -       -
     3   CPU0   -   -  2492  1700   0.61 0.88   1.10  98.90   0.00   0.00   0.00  -  -  -    58  40 105.87 0.862 0.865   0x0  0x0   0  29.875
     3   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.82     -     -     -  0x0   -       -
     4   CPU0   -   -  2499  1700   0.71 0.89   1.23  98.77   0.00   0.00   0.00  -  -  -    58  40 106.06 0.862 0.865   0x0  0x0   0  29.906
     4   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.79     -     -     -  0x0   -       -
     5   CPU0   -   -  2492  1700   0.49 0.87   0.90  99.10   0.00   0.00   0.00  -  -  -    58  40 105.66 0.862 0.865   0x0  0x0   0  29.812
     5   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.80     -     -     -  0x0   -       -
     6   CPU0   -   -  2496  1700   1.41 0.90   2.13  97.87   0.00   0.00   0.00  -  -  -    58  40 106.92 0.862 0.865   0x0  0x0   0  29.562
     6   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.82     -     -     -  0x0   -       -
     7   CPU0   -   -  2494  1700   0.82 0.88   1.47  98.53   0.00   0.00   0.00  -  -  -    58  40 106.35 0.862 0.865   0x0  0x0   0  29.984
     7   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.78     -     -     -  0x0   -       -
     8   CPU0   -   -  2485  1700   1.05 0.87   1.67  98.33   0.00   0.00   0.00  -  -  -    58  40 106.41 0.862 0.865   0x0  0x0   0  29.969
     8   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.84     -     -     -  0x0   -       -
     9   CPU0   -   -  2504  1700   1.07 0.90   1.82  98.18   0.00   0.00   0.00  -  -  -    58  40 106.80 0.862 0.865   0x0  0x0   0  29.938
     9   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.79     -     -     -  0x0   -       -
    10   CPU0   -   -  2492  1700   0.56 0.86   1.01  98.99   0.00   0.00   0.00  -  -  -    58  40 105.73 0.865 0.865   0x0  0x0   0  29.969
    10   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.82     -     -     -  0x0   -       -
    11   CPU0   -   -  2496  1700   0.66 0.90   1.15  98.85   0.00   0.00   0.00  -  -  -    58  40 105.79 0.862 0.865   0x0  0x0   0  29.922
    11   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.79     -     -     -  0x0   -       -
    12   CPU0   -   -  2493  1700   0.71 0.89   1.25  98.75   0.00   0.00   0.00  -  -  -    58  40 106.00 0.862 0.865   0x0  0x0   0  29.969
    12   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.78     -     -     -  0x0   -       -
    13   CPU0   -   -  2495  1700   0.80 0.89   1.40  98.60   0.00   0.00   0.00  -  -  -    58  40 106.28 0.862 0.865   0x0  0x0   0  29.953
    13   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.81     -     -     -  0x0   -       -
    14   CPU0   -   -  2495  1700   0.71 0.90   1.22  98.78   0.00   0.00   0.00  -  -  -    58  40 105.93 0.862 0.865   0x0  0x0   0  29.938
    14   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.79     -     -     -  0x0   -       -
    15   CPU0   -   -  2492  1700   0.51 0.89   0.97  99.03   0.00   0.00   0.00  -  -  -    58  40 105.89 0.862 0.865   0x0  0x0   0  29.984
    15   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.81     -     -     -  0x0   -       -
    16   CPU0   -   -  2495  1700   2.62 0.89   3.32  96.68   0.00   0.00   0.00  -  -  -    58  40 108.54 0.862 0.865   0x0  0x0   0  28.812
    16   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.84     -     -     -  0x0   -       -
    17   CPU0   -   -  2494  1700   0.82 0.88   1.37  98.63   0.00   0.00   0.00  -  -  -    58  40 106.22 0.862 0.865   0x0  0x0   0  29.938
    17   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.80     -     -     -  0x0   -       -
    18   CPU0   -   -  2484  1700   0.82 0.88   1.40  98.60   0.00   0.00   0.00  -  -  -    58  40 106.21 0.862 0.865   0x0  0x0   0  29.984
    18   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.82     -     -     -  0x0   -       -
    19   CPU0   -   -  2506  1700   1.24 0.90   2.12  97.88   0.00   0.00   0.00  -  -  -    58  40 106.86 0.862 0.865   0x0  0x0   0  29.938
    19   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.80     -     -     -  0x0   -       -
    20   CPU0   -   -  2497  1700   0.50 0.88   0.91  99.09   0.00   0.00   0.00  -  -  -    58  40 105.71 0.862 0.865   0x0  0x0   0  29.797
    20   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.81     -     -     -  0x0   -       -
    21   CPU0   -   -  2491  1700   1.25 0.90   2.14  97.86   0.00   0.00   0.00  -  -  -    58  40 106.86 0.862 0.865   0x0  0x0   0  29.828
    21   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.81     -     -     -  0x0   -       -
    22   CPU0   -   -  2493  1700   1.40 0.89   2.27  97.73   0.00   0.00   0.00  -  -  -    58  40 107.08 0.865 0.865   0x0  0x0   0  29.828
    22   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.84     -     -     -  0x0   -       -
    23   CPU0   -   -  2484  1700   0.50 0.88   0.91  99.09   0.00   0.00   0.00  -  -  -    58  40 105.76 0.862 0.865   0x0  0x0   0  29.672
    23   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.79     -     -     -  0x0   -       -
    24   CPU0   -   -  2501  1700   1.29 0.91   2.11  97.89   0.00   0.00   0.00  -  -  -    59  39 106.84 0.862 0.865   0x0  0x0   0  29.781
    24   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.81     -     -     -  0x0   -       -
    25   CPU0   -   -  2499  1700   0.89 0.88   1.58  98.42   0.00   0.00   0.00  -  -  -    58  40 106.30 0.862 0.865   0x0  0x0   0  29.797
    25   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.79     -     -     -  0x0   -       -
    26   CPU0   -   -  2488  1700   1.40 0.81   2.09  97.91   0.00   0.00   0.00  -  -  -    59  39 106.89 0.862 0.865   0x0  0x0   0  29.562
    26   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.82     -     -     -  0x0   -       -
    27   CPU0   -   -  2497  1700   0.75 0.89   1.28  98.72   0.00   0.00   0.00  -  -  -    58  40 105.97 0.862 0.865   0x0  0x0   0  29.781
    27   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.78     -     -     -  0x0   -       -
    28   CPU0   -   -  2499  1700   1.06 0.88   1.74  98.26   0.00   0.00   0.00  -  -  -    58  40 106.57 0.862 0.865   0x0  0x0   0  29.969
    28   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.85     -     -     -  0x0   -       -
    29   CPU0   -   -  2494  1700   1.39 0.91   2.28  97.72   0.00   0.00   0.00  -  -  -    58  40 107.04 0.865 0.865   0x0  0x0   0  29.688
    29   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.78     -     -     -  0x0   -       -
    30   CPU0   -   -  2497  1700   0.58 0.87   1.07  98.93   0.00   0.00   0.00  -  -  -    58  40 105.77 0.865 0.865   0x0  0x0   0  30.031
    30   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.81     -     -     -  0x0   -       -
    31   CPU0   -   -  2493  1700   0.49 0.89   0.90  99.10   0.00   0.00   0.00  -  -  -    58  40 105.60 0.862 0.865   0x0  0x0   0  29.922
    31   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.78     -     -     -  0x0   -       -
    32   CPU0   -   -  2495  1700   0.63 0.88   1.13  98.87   0.00   0.00   0.00  -  -  -    58  40 105.84 0.862 0.865   0x0  0x0   0  30.031
    32   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.77     -     -     -  0x0   -       -
    33   CPU0   -   -  2493  1700   0.90 0.89   1.55  98.45   0.00   0.00   0.00  -  -  -    58  40 106.19 0.862 0.865   0x0  0x0   0  29.906
    33   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.80     -     -     -  0x0   -       -
    34   CPU0   -   -  2492  1700   0.78 0.91   1.36  98.64   0.00   0.00   0.00  -  -  -    58  40 106.09 0.865 0.865   0x0  0x0   0  29.906
    34   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.78     -     -     -  0x0   -       -
    35   CPU0   -   -  2498  1700   0.60 0.87   1.11  98.89   0.00   0.00   0.00  -  -  -    58  40 105.82 0.862 0.865   0x0  0x0   0  29.938
    35   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.81     -     -     -  0x0   -       -
    36   CPU0   -   -  2491  1700   1.43 0.90   2.18  97.82   0.00   0.00   0.00  -  -  -    58  40 106.99 0.862 0.865   0x0  0x0   0  29.750
    36   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.83     -     -     -  0x0   -       -
    37   CPU0   -   -  2496  1700   1.07 0.90   1.92  98.08   0.00   0.00   0.00  -  -  -    58  40 106.66 0.862 0.865   0x0  0x0   0  29.844
    37   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.80     -     -     -  0x0   -       -
    38   CPU0   -   -  2497  1700   1.02 0.86   1.64  98.36   0.00   0.00   0.00  -  -  -    58  40 106.40 0.865 0.865   0x0  0x0   0  29.766
    38   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.85     -     -     -  0x0   -       -
    39   CPU0   -   -  2493  1700   0.92 0.90   1.66  98.34   0.00   0.00   0.00  -  -  -    58  40 106.32 0.865 0.865   0x0  0x0   0  29.906
    39   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.78     -     -     -  0x0   -       -
    40   CPU0   -   -  2491  1700   0.66 0.87   1.20  98.80   0.00   0.00   0.00  -  -  -    58  40 105.96 0.865 0.865   0x0  0x0   0  29.875
    40   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   7.82     -     -     -  0x0   -       -
^C
[01/12/24 19:19:50 UTC] PTU stopped.

controller-0:~#
```

## Sensors after load started

```log
controller-0:~# ipmitool sensor | grep -e CPU_0_TEMP -e CPU0_Power -e SYS_FAN_1A -e CPU_CUPS
CPU_0_TEMP       | 58.000     | degrees C  | ok    | na        | na        | na        | 96.000    | 98.000    | na
CPU0_Power       | 105.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 5000.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1A_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
CPU_CUPS         | 1.000      | percent    | ok    | na        | na        | na        | na        | 100.000   | na
controller-0:~#

```


## Temps didn't rise as much as with other tests, but all data recorded, no issues found.
## Success, end of performance tests with PTU