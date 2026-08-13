# ZT Proteus PDB-DPLD 0.0.1.2 firmware
# ZT Proteus BMC .46 and Bios .23 
# 3/12/24 James Patchett
# Sensor validation before and after installation of PDB 0.0.1.2

## Target subclouds RU_12,13 Right and Left side

## Left side Subcloud welktxef-d931887-021
## BMC 0.46 BIOS 0.23
BMC:  2607:f160:10:9249:ce:40a:0:e015
OAM:  2607:f160:10:9249:ce:40a:0:f409

## Subcloud welktxef-d931856-008 Info
```log
XXXXXX@controller-0:~$ source /etc/platform/openrc
[XXXXXX@controller-0 ~(keystone_admin)]$ system show
+------------------------+--------------------------------------+
| Property               | Value                                |
+------------------------+--------------------------------------+
| contact                | None                                 |
| created_at             | 2024-03-07T18:03:00.044462+00:00     |
| description            | None                                 |
| distributed_cloud_role | subcloud                             |
| https_enabled          | True                                 |
| latitude               | None                                 |
| location               | None                                 |
| longitude              | None                                 |
| name                   | welktxef-d931887-021                 |
| region_name            | welktxef-d931887-021                 |
| sdn_enabled            | False                                |
| security_feature       | spectre_meltdown_v1                  |
| service_project_name   | services                             |
| shared_services        | []                                   |
| software_version       | 22.12                                |
| system_mode            | simplex                              |
| system_type            | All-in-one                           |
| timezone               | UTC                                  |
| updated_at             | 2024-03-11T19:05:24.739152+00:00     |
| uuid                   | 23aff978-9c1f-4e92-aca9-97621b54bd8a |
| vswitch_type           | none                                 |
+------------------------+--------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ system application-list
+--------------------------+----------+-------------------------------------------+------------------+---------+-----------+
| application              | version  | manifest name                             | manifest file    | status  | progress  |
+--------------------------+----------+-------------------------------------------+------------------+---------+-----------+
| cert-manager             | 22.12-8  | cert-manager-fluxcd-manifests             | fluxcd-manifests | applied | completed |
| metrics-server           | 22.12-1  | metrics-server-fluxcd-manifests           | fluxcd-manifests | applied | completed |
| nginx-ingress-controller | 22.12-1  | nginx-ingress-controller-fluxcd-manifests | fluxcd-manifests | applied | completed |
| oidc-auth-apps           | 22.12-6  | oidc-auth-apps-fluxcd-manifests           | fluxcd-manifests | applied | completed |
| platform-integ-apps      | 22.12-66 | platform-integ-apps-fluxcd-manifests      | fluxcd-manifests | applied | completed |
| wr-analytics             | 23.09-0  | wr-analytics-fluxcd-manifests             | fluxcd-manifests | applied | completed |
+--------------------------+----------+-------------------------------------------+------------------+---------+-----------+
[XXXXXX@controller-0 ~(keystone_admin)]$ sw-patch query
      Patch ID         RR  Release  Patch State
=====================  ==  =======  ===========
WRCP_22.12_PATCH_0001  Y    22.12    Committed
WRCP_22.12_PATCH_0002  Y    22.12    Committed
WRCP_22.12_PATCH_0003  Y    22.12    Committed
WRCP_22.12_PATCH_0004  Y    22.12    Committed

[XXXXXX@controller-0 ~(keystone_admin)]$
```
## Performance Test MEAKV-642 
## sudo ./ptu -ct 1 -b 0
## measure sensors first, then run load, then check during load

## Sensors
```log
[XXXXXX@controller-0 ~(keystone_admin)]$ ipmitool sensor | grep -e CPU_0_TEMP -e CPU0_Power -e SYS_FAN_1A -e CPU_CUPS
Could not open device at /dev/ipmi0 or /dev/ipmi/0 or /dev/ipmidev/0: No such file or directory
[XXXXXX@controller-0 ~(keystone_admin)]$ sudo su -
Password:
XXXXXX ipmitool sensor | grep -e CPU_0_TEMP -e CPU0_Power -e SYS_FAN_1A -e CPU_CUPS
CPU_0_TEMP       | 63.000     | degrees C  | ok    | na        | na        | na        | 96.000    | 98.000    | na
CPU0_Power       | 126.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 5125.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1A_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
CPU_CUPS         | 1.000      | percent    | ok    | na        | na        | na        | na        | 100.000   | na
root@controller-0:~#
```

## Initiate load 

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ cp ptu /tmp
[XXXXXX@controller-0 ~(keystone_admin)]$ sudo -i
root@controller-0:~# /tmp/ptu -ct 1 -b 0

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
OS Name:                             Debian GNU/Linux 11 (bullseye) 11
Kernel Version:                      Linux 5.10.0-6-rt-amd64 #1 SMP PREEMPT_RT StarlingX Debian 5.10.177-1.stx.73 (2023-11-25
BIOS Version:                        American Megatrends International, LLC., 0.23, 06/29/2021
Processor(s):                        1 Processor(s) Installed.
DIMM(s):                             8 DIMM(s) Installed.
Total System Memory:                 126171 MB
Available System Memory:             60589 MB


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Processor: [CPU_0]             <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU ID:                              0x000606A6 (Family 6 Model 6Ah Stepping 6)
CPU Brand Name:                      Intel(R) Xeon(R) Gold 6338N CPU @ 2.20GHz
CPU Code Name:                       Ice Lake
CPU Type:                            Production Part
CPU Segment:                         Server
CPU PPIN:                            0x0CEBB6DEA8DA6042
CPU Base Frequency:                  1500 MHz
CPU Minimum Frequency:               800 MHz
CPU Maximum Turbo Frequency:         3500 MHz
Uncore Minimum Frequency:            1700 MHz
Uncore Maximum Frequency:            1700 MHz
L2 Cache:                            32 x 1280 KB
L3 Cache:                            49152 KB
Hyper-threading:                     Enabled
Microcode Update Revision:           0x0D000280
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
CAPID6:                              0xB59FFFD6
CAPID7:                              0x000000FF
CAPID8:                              0xB59FFFD6
CAPID9:                              0x000000FF
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

[03/12/24 20:20:41 UTC] PTU started.

Press <Ctrl-C> to stop.


CPU_0: [IDLE] CFreq=2494, UFreq=1700, Util=91.07, IPC=0.09, Temp=64, DTS=34, Power=126.2, Volt=0.868, UVolt=0.845
CPU_0: [TESTCFG] TestSel=1 (TDP), CoreMask=0xFFFFFFFFFFFFFFFF, ThreadMask=0xFF, PwrLevel=TDP, Turbo=0
CPU_0: [RUNNING] CFreq=2383, UFreq=1500, Util=100.00, IPC=3.16, Temp=72, DTS=26, Power=184.5, Volt=0.840, UVolt=0.812


```

## Ptu monitoring

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ sudo -i
Password:
XXXXXX /tmp/ptu -mon

Command: /tmp/ptu -mon

Intel(R) Power Thermal Utility - Server Edition v2.3.1
Release Date: 12/04/2020
Copyright (C) 2020 Intel Corporation. All rights reserved.
Intel Confidential

/dev/ptusys: No such file or directory
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> System Info:                   <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Host Name:                           controller-0
Host IP:                             169.254.202.1
OS Name:                             Debian GNU/Linux 11 (bullseye) 11
Kernel Version:                      Linux 5.10.0-6-rt-amd64 #1 SMP PREEMPT_RT StarlingX Debian 5.10.177-1.stx.73 (2023-11-25
BIOS Version:                        American Megatrends International, LLC., 0.23, 06/29/2021
Processor(s):                        1 Processor(s) Installed.
DIMM(s):                             8 DIMM(s) Installed.
Total System Memory:                 126171 MB
Available System Memory:             60450 MB


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Processor: [CPU_0]             <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU ID:                              0x000606A6 (Family 6 Model 6Ah Stepping 6)
CPU Brand Name:                      Intel(R) Xeon(R) Gold 6338N CPU @ 2.20GHz
CPU Code Name:                       Ice Lake
CPU Type:                            Production Part
CPU Segment:                         Server
CPU PPIN:                            0x0CEBB6DEA8DA6042
CPU Base Frequency:                  1500 MHz
CPU Minimum Frequency:               800 MHz
CPU Maximum Turbo Frequency:         3500 MHz
Uncore Minimum Frequency:            1700 MHz
Uncore Maximum Frequency:            1700 MHz
L2 Cache:                            32 x 1280 KB
L3 Cache:                            49152 KB
Hyper-threading:                     Enabled
Microcode Update Revision:           0x0D000280
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
CAPID6:                              0xB59FFFD6
CAPID7:                              0x000000FF
CAPID8:                              0xB59FFFD6
CAPID9:                              0x000000FF
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

[03/12/24 20:22:14 UTC] PTU started.

Press <Ctrl-C> to stop.


 Index Device Cor Thr CFreq UFreq   Util  IPC     C0     C1     C6    PC2    PC6 MC Ch Sl  Temp DTS  Power  Volt UVolt TStat TLog #TL TMargin
     0   CPU0   -   -  2362  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.33 0.830 0.810   0x0  0x0   0  12.609
     0   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.84     -     -     -  0x0   -       -
     1   CPU0   -   -  2363  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.67 0.847 0.810   0x0  0x0   0  12.578
     1   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.71     -     -     -  0x0   -       -
     2   CPU0   -   -  2362  1500 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.44 0.845 0.810   0x0  0x0   0  12.547
     2   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.78     -     -     -  0x0   -       -
     3   CPU0   -   -  2368  1400 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.45 0.830 0.795   0x0  0x0   0  12.500
     3   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.65     -     -     -  0x0   -       -
     4   CPU0   -   -  2367  1500 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.56 0.845 0.807   0x0  0x0   0  12.344
     4   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.73     -     -     -  0x0   -       -
     5   CPU0   -   -  2365  1400 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.47 0.845 0.795   0x0  0x0   0  12.266
     5   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.60     -     -     -  0x0   -       -
     6   CPU0   -   -  2371  1500 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.42 0.845 0.807   0x0  0x0   0  12.375
     6   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.57     -     -     -  0x0   -       -
     7   CPU0   -   -  2369  1500 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.51 0.845 0.807   0x0  0x0   0  12.281
     7   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.83     -     -     -  0x0   -       -
     8   CPU0   -   -  2367  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.50 0.830 0.810   0x0  0x0   0  12.328
     8   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.91     -     -     -  0x0   -       -
     9   CPU0   -   -  2366  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.28 0.830 0.807   0x0  0x0   0  12.547
     9   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.66     -     -     -  0x0   -       -
    10   CPU0   -   -  2362  1400 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.49 0.845 0.795   0x0  0x0   0  12.438
    10   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.70     -     -     -  0x0   -       -
    11   CPU0   -   -  2363  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.51 0.830 0.807   0x0  0x0   0  12.156
    11   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.66     -     -     -  0x0   -       -
    12   CPU0   -   -  2370  1500 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.42 0.845 0.807   0x0  0x0   0  12.156
    12   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.74     -     -     -  0x0   -       -
    13   CPU0   -   -  2373  1500 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.55 0.845 0.807   0x0  0x0   0  12.141
    13   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.57     -     -     -  0x0   -       -
    14   CPU0   -   -  2372  1500 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.37 0.845 0.807   0x0  0x0   0  12.031
    14   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.62     -     -     -  0x0   -       -
    15   CPU0   -   -  2376  1500 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.60 0.845 0.807   0x0  0x0   0  12.141
    15   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.66     -     -     -  0x0   -       -
    16   CPU0   -   -  2376  1400 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.51 0.830 0.795   0x0  0x0   0  12.078
    16   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.64     -     -     -  0x0   -       -
    17   CPU0   -   -  2367  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.42 0.845 0.807   0x0  0x0   0  12.219
    17   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.89     -     -     -  0x0   -       -
    18   CPU0   -   -  2368  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.46 0.845 0.807   0x0  0x0   0  12.203
    18   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.93     -     -     -  0x0   -       -
    19   CPU0   -   -  2372  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.40 0.845 0.807   0x0  0x0   0  12.062
    19   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.91     -     -     -  0x0   -       -
    20   CPU0   -   -  2373  1400 100.00 3.13 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.37 0.830 0.795   0x0  0x0   0  12.062
    20   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.04     -     -     -  0x0   -       -
    21   CPU0   -   -  2374  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.55 0.845 0.807   0x0  0x0   0  12.031
    21   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.88     -     -     -  0x0   -       -
    22   CPU0   -   -  2373  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.46 0.845 0.807   0x0  0x0   0  12.156
    22   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.91     -     -     -  0x0   -       -
    23   CPU0   -   -  2377  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.50 0.830 0.807   0x0  0x0   0  11.953
    23   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.63     -     -     -  0x0   -       -
    24   CPU0   -   -  2375  1500 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.50 0.830 0.807   0x0  0x0   0  11.891
    24   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.62     -     -     -  0x0   -       -
    25   CPU0   -   -  2377  1500 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.52 0.845 0.807   0x0  0x0   0  11.875
    25   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.52     -     -     -  0x0   -       -
    26   CPU0   -   -  2379  1500 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.41 0.845 0.810   0x0  0x0   0  12.016
    26   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.55     -     -     -  0x0   -       -
    27   CPU0   -   -  2377  1500 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.48 0.845 0.810   0x0  0x0   0  12.031
    27   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.60     -     -     -  0x0   -       -
    28   CPU0   -   -  2378  1400 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.38 0.845 0.795   0x0  0x0   0  11.969
    28   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.58     -     -     -  0x0   -       -
    29   CPU0   -   -  2379  1500 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.34 0.845 0.807   0x0  0x0   0  11.891
    29   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.55     -     -     -  0x0   -       -
    30   CPU0   -   -  2379  1500 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.71 0.845 0.807   0x0  0x0   0  11.969
    30   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.72     -     -     -  0x0   -       -
    31   CPU0   -   -  2378  1400 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.41 0.845 0.795   0x0  0x0   0  11.953
    31   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.67     -     -     -  0x0   -       -
    32   CPU0   -   -  2376  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.38 0.845 0.807   0x0  0x0   0  12.000
    32   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.81     -     -     -  0x0   -       -
    33   CPU0   -   -  2376  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.61 0.845 0.807   0x0  0x0   0  12.000
    33   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.59     -     -     -  0x0   -       -
^C
[03/12/24 20:22:51 UTC] PTU stopped.

root@controller-0:~#

```

## check the sensors again, to see the reaction to raised thermals

```log
root@controller-0:~# ipmitool sensor | grep -e CPU_0_TEMP -e CPU0_Power -e SYS_FAN_1A -e CPU_CUPS
CPU_0_TEMP       | 76.000     | degrees C  | ok    | na        | na        | na        | 96.000    | 98.000    | na
CPU0_Power       | 184.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 6000.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1A_PWM   | 22.000     | percent    | ok    | na        | na        | na        | na        | na        | na
CPU_CUPS         | 1.000      | percent    | ok    | na        | na        | na        | na        | 100.000   | na
root@controller-0:~#
```

## Success as we have observed thermals rising, along with fans increase in RPMs...  on to next test

## Performance Test MEAKV-643 
## Run Core IA/SSE with 100% power, and Turbo on
## ./ptu -ct 3 -cp 100 -b 1

## Sensors before run

```log
root@controller-0:~# ipmitool sensor | grep -e CPU_0_TEMP -e CPU0_Power -e SYS_FAN_1A -e CPU_CUPS
CPU_0_TEMP       | 64.000     | degrees C  | ok    | na        | na        | na        | 96.000    | 98.000    | na
CPU0_Power       | 126.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 5000.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1A_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
CPU_CUPS         | 1.000      | percent    | ok    | na        | na        | na        | na        | 100.000   | na
root@controller-0:~#

```

## Initiate Load 

```log
root@controller-0:~# /tmp/ptu -ct 3 -cp 100 -b 1

Command: /tmp/ptu -ct 3 -cp 100 -b 1

Intel(R) Power Thermal Utility - Server Edition v2.3.1
Release Date: 12/04/2020
Copyright (C) 2020 Intel Corporation. All rights reserved.
Intel Confidential

/dev/ptusys: No such file or directory
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> System Info:                   <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Host Name:                           controller-0
Host IP:                             169.254.202.1
OS Name:                             Debian GNU/Linux 11 (bullseye) 11
Kernel Version:                      Linux 5.10.0-6-rt-amd64 #1 SMP PREEMPT_RT StarlingX Debian 5.10.177-1.stx.73 (2023-11-25
BIOS Version:                        American Megatrends International, LLC., 0.23, 06/29/2021
Processor(s):                        1 Processor(s) Installed.
DIMM(s):                             8 DIMM(s) Installed.
Total System Memory:                 126171 MB
Available System Memory:             60426 MB


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Processor: [CPU_0]             <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU ID:                              0x000606A6 (Family 6 Model 6Ah Stepping 6)
CPU Brand Name:                      Intel(R) Xeon(R) Gold 6338N CPU @ 2.20GHz
CPU Code Name:                       Ice Lake
CPU Type:                            Production Part
CPU Segment:                         Server
CPU PPIN:                            0x0CEBB6DEA8DA6042
CPU Base Frequency:                  1500 MHz
CPU Minimum Frequency:               800 MHz
CPU Maximum Turbo Frequency:         3500 MHz
Uncore Minimum Frequency:            1700 MHz
Uncore Maximum Frequency:            1700 MHz
L2 Cache:                            32 x 1280 KB
L3 Cache:                            49152 KB
Hyper-threading:                     Enabled
Microcode Update Revision:           0x0D000280
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
CAPID6:                              0xB59FFFD6
CAPID7:                              0x000000FF
CAPID8:                              0xB59FFFD6
CAPID9:                              0x000000FF
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

[03/12/24 20:28:06 UTC] PTU started.

Press <Ctrl-C> to stop.


CPU_0: [IDLE] CFreq=2494, UFreq=1700, Util=90.35, IPC=0.09, Temp=65, DTS=33, Power=126.0, Volt=0.867, UVolt=0.842
CPU_0: [TESTCFG] TestSel=3 (Core IA/SSE), CoreMask=0xFFFFFFFFFFFFFFFF, ThreadMask=0xFF, PwrLevel=100, Turbo=1
CPU_0: [RUNNING] CFreq=2301, UFreq=1400, Util=100.00, IPC=3.88, Temp=73, DTS=25, Power=184.3, Volt=0.830, UVolt=0.797
```

## ptu -mon

```log
root@controller-0:~# /tmp/ptu -mon

Command: /tmp/ptu -mon

Intel(R) Power Thermal Utility - Server Edition v2.3.1
Release Date: 12/04/2020
Copyright (C) 2020 Intel Corporation. All rights reserved.
Intel Confidential

/dev/ptusys: No such file or directory
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> System Info:                   <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Host Name:                           controller-0
Host IP:                             169.254.202.1
OS Name:                             Debian GNU/Linux 11 (bullseye) 11
Kernel Version:                      Linux 5.10.0-6-rt-amd64 #1 SMP PREEMPT_RT StarlingX Debian 5.10.177-1.stx.73 (2023-11-25
BIOS Version:                        American Megatrends International, LLC., 0.23, 06/29/2021
Processor(s):                        1 Processor(s) Installed.
DIMM(s):                             8 DIMM(s) Installed.
Total System Memory:                 126171 MB
Available System Memory:             60535 MB


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Processor: [CPU_0]             <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU ID:                              0x000606A6 (Family 6 Model 6Ah Stepping 6)
CPU Brand Name:                      Intel(R) Xeon(R) Gold 6338N CPU @ 2.20GHz
CPU Code Name:                       Ice Lake
CPU Type:                            Production Part
CPU Segment:                         Server
CPU PPIN:                            0x0CEBB6DEA8DA6042
CPU Base Frequency:                  1500 MHz
CPU Minimum Frequency:               800 MHz
CPU Maximum Turbo Frequency:         3500 MHz
Uncore Minimum Frequency:            1700 MHz
Uncore Maximum Frequency:            1700 MHz
L2 Cache:                            32 x 1280 KB
L3 Cache:                            49152 KB
Hyper-threading:                     Enabled
Microcode Update Revision:           0x0D000280
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
CAPID6:                              0xB59FFFD6
CAPID7:                              0x000000FF
CAPID8:                              0xB59FFFD6
CAPID9:                              0x000000FF
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

[03/12/24 20:28:40 UTC] PTU started.

Press <Ctrl-C> to stop.


 Index Device Cor Thr CFreq UFreq   Util  IPC     C0     C1     C6    PC2    PC6 MC Ch Sl  Temp DTS  Power  Volt UVolt TStat TLog #TL TMargin
     0   CPU0   -   -  2289  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.48 0.830 0.795   0x0  0x0   0  13.516
     0   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.59     -     -     -  0x0   -       -
     1   CPU0   -   -  2290  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.57 0.830 0.795   0x0  0x0   0  13.281
     1   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.67     -     -     -  0x0   -       -
     2   CPU0   -   -  2296  1400 100.00 3.91 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.22 0.830 0.795   0x0  0x0   0  13.344
     2   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.47     -     -     -  0x0   -       -
     3   CPU0   -   -  2292  1400 100.00 3.91 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.66 0.830 0.795   0x0  0x0   0  13.438
     3   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.50     -     -     -  0x0   -       -
     4   CPU0   -   -  2289  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.49 0.830 0.795   0x0  0x0   0  13.312
     4   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.59     -     -     -  0x0   -       -
     5   CPU0   -   -  2294  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.48 0.830 0.795   0x0  0x0   0  13.312
     5   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.58     -     -     -  0x0   -       -
     6   CPU0   -   -  2296  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.24 0.830 0.795   0x0  0x0   0  13.141
     6   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.49     -     -     -  0x0   -       -
     7   CPU0   -   -  2293  1400 100.00 3.91 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.61 0.830 0.795   0x0  0x0   0  13.344
     7   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.38     -     -     -  0x0   -       -
     8   CPU0   -   -  2291  1400 100.00 3.91 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.56 0.830 0.795   0x0  0x0   0  13.328
     8   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.51     -     -     -  0x0   -       -
     9   CPU0   -   -  2291  1400 100.00 3.91 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.42 0.830 0.795   0x0  0x0   0  13.344
     9   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.56     -     -     -  0x0   -       -
    10   CPU0   -   -  2287  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.46 0.830 0.795   0x0  0x0   0  13.203
    10   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.66     -     -     -  0x0   -       -
    11   CPU0   -   -  2283  1400 100.00 3.88 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.36 0.817 0.795   0x0  0x0   0  13.203
    11   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.77     -     -     -  0x0   -       -
    12   CPU0   -   -  2283  1400 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.54 0.830 0.795   0x0  0x0   0  13.188
    12   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.78     -     -     -  0x0   -       -
    13   CPU0   -   -  2284  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.45 0.830 0.795   0x0  0x0   0  13.188
    13   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.56     -     -     -  0x0   -       -
    14   CPU0   -   -  2294  1400 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.47 0.830 0.795   0x0  0x0   0  13.156
    14   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.70     -     -     -  0x0   -       -
    15   CPU0   -   -  2290  1400 100.00 3.88 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.32 0.832 0.795   0x0  0x0   0  12.797
    15   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.89     -     -     -  0x0   -       -
    16   CPU0   -   -  2296  1400 100.00 3.87 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.70 0.832 0.795   0x0  0x0   0  12.891
    16   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.75     -     -     -  0x0   -       -
    17   CPU0   -   -  2292  1400 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.38 0.830 0.795   0x0  0x0   0  12.938
    17   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.79     -     -     -  0x0   -       -
    18   CPU0   -   -  2287  1400 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.40 0.845 0.795   0x0  0x0   0  13.031
    18   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.65     -     -     -  0x0   -       -
    19   CPU0   -   -  2285  1400 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.56 0.830 0.795   0x0  0x0   0  12.969
    19   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.71     -     -     -  0x0   -       -
    20   CPU0   -   -  2285  1400 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.52 0.830 0.795   0x0  0x0   0  13.016
    20   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.61     -     -     -  0x0   -       -
    21   CPU0   -   -  2284  1400 100.00 3.87 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.44 0.830 0.795   0x0  0x0   0  12.891
    21   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.83     -     -     -  0x0   -       -
    22   CPU0   -   -  2285  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.34 0.830 0.795   0x0  0x0   0  12.766
    22   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.55     -     -     -  0x0   -       -
    23   CPU0   -   -  2284  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.52 0.830 0.795   0x0  0x0   0  12.719
    23   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.64     -     -     -  0x0   -       -
    24   CPU0   -   -  2290  1500 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.56 0.830 0.920   0x0  0x0   0  12.766
    24   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.56     -     -     -  0x0   -       -
    25   CPU0   -   -  2288  1400 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.43 0.830 0.795   0x0  0x0   0  12.672
    25   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.58     -     -     -  0x0   -       -
    26   CPU0   -   -  2291  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.44 0.830 0.795   0x0  0x0   0  12.656
    26   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.57     -     -     -  0x0   -       -
    27   CPU0   -   -  2296  1400 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.47 0.815 0.795   0x0  0x0   0  12.719
    27   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.56     -     -     -  0x0   -       -
    28   CPU0   -   -  2295  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.36 0.830 0.795   0x0  0x0   0  12.625
    28   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.61     -     -     -  0x0   -       -
    29   CPU0   -   -  2300  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.48 0.830 0.795   0x0  0x0   0  12.781
    29   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.49     -     -     -  0x0   -       -
    30   CPU0   -   -  2304  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.58 0.830 0.795   0x0  0x0   0  12.438
    30   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.51     -     -     -  0x0   -       -
    31   CPU0   -   -  2303  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.36 0.830 0.795   0x0  0x0   0  12.656
    31   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.71     -     -     -  0x0   -       -
    32   CPU0   -   -  2305  1400 100.00 3.91 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.60 0.830 0.795   0x0  0x0   0  12.547
    32   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.47     -     -     -  0x0   -       -
    33   CPU0   -   -  2304  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.31 0.830 0.792   0x0  0x0   0  12.281
    33   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.56     -     -     -  0x0   -       -
    34   CPU0   -   -  2305  1400 100.00 3.91 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.48 0.830 0.795   0x0  0x0   0  12.312
    34   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.56     -     -     -  0x0   -       -
    35   CPU0   -   -  2305  1400 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 182.63 0.830 0.795   0x0  0x0   0  12.281
    35   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.69     -     -     -  0x0   -       -
    36   CPU0   -   -  2303  1400 100.00 3.85 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 186.35 0.830 0.795   0x0  0x0   0  12.484
    36   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.85     -     -     -  0x0   -       -
    37   CPU0   -   -  2302  1400 100.00 3.88 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.39 0.830 0.795   0x0  0x0   0  12.406
    37   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.70     -     -     -  0x0   -       -
    38   CPU0   -   -  2304  1400 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.66 0.830 0.795   0x0  0x0   0  12.359
    38   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.64     -     -     -  0x0   -       -
    39   CPU0   -   -  2305  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.47 0.830 0.795   0x0  0x0   0  12.484
    39   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.55     -     -     -  0x0   -       -
^C
[03/12/24 20:29:23 UTC] PTU stopped.

root@controller-0:~#
```

## Sensors after load ~2-3mins after

```log
root@controller-0:~# ipmitool sensor | grep -e CPU_0_TEMP -e CPU0_Power -e SYS_FAN_1A -e CPU_CUPS
CPU_0_TEMP       | 76.000     | degrees C  | ok    | na        | na        | na        | 96.000    | 98.000    | na
CPU0_Power       | 184.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 6000.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1A_PWM   | 22.000     | percent    | ok    | na        | na        | na        | na        | na        | na
CPU_CUPS         | 1.000      | percent    | ok    | na        | na        | na        | na        | 100.000   | na
root@controller-0:~#

```

## Test is success, observed temps rise and fan rpms rise with the load
## Performance test MEAKV-644
## PTU 3 - Core AVX2 with Turbo 
## Run Core Intel® AVX-2 with power level 100% and Turbo on.
## sudo ./ptu -ct 4 -cp 100 -b 1

## Check sensors bofore starting load

```log
root@controller-0:~# ipmitool sensor | grep -e CPU_0_TEMP -e CPU0_Power -e SYS_FAN_1A -e CPU_CUPS
CPU_0_TEMP       | 64.000     | degrees C  | ok    | na        | na        | na        | 96.000    | 98.000    | na
CPU0_Power       | 125.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 5000.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1A_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
CPU_CUPS         | 1.000      | percent    | ok    | na        | na        | na        | na        | 100.000   | na
root@controller-0:~#
```

## load Intiated

```log
root@controller-0:~# /tmp/ptu -ct 4 -cp 100 -b 1

Command: /tmp/ptu -ct 4 -cp 100 -b 1

Intel(R) Power Thermal Utility - Server Edition v2.3.1
Release Date: 12/04/2020
Copyright (C) 2020 Intel Corporation. All rights reserved.
Intel Confidential

/dev/ptusys: No such file or directory
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> System Info:                   <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Host Name:                           controller-0
Host IP:                             169.254.202.1
OS Name:                             Debian GNU/Linux 11 (bullseye) 11
Kernel Version:                      Linux 5.10.0-6-rt-amd64 #1 SMP PREEMPT_RT StarlingX Debian 5.10.177-1.stx.73 (2023-11-25
BIOS Version:                        American Megatrends International, LLC., 0.23, 06/29/2021
Processor(s):                        1 Processor(s) Installed.
DIMM(s):                             8 DIMM(s) Installed.
Total System Memory:                 126171 MB
Available System Memory:             60596 MB


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Processor: [CPU_0]             <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU ID:                              0x000606A6 (Family 6 Model 6Ah Stepping 6)
CPU Brand Name:                      Intel(R) Xeon(R) Gold 6338N CPU @ 2.20GHz
CPU Code Name:                       Ice Lake
CPU Type:                            Production Part
CPU Segment:                         Server
CPU PPIN:                            0x0CEBB6DEA8DA6042
CPU Base Frequency:                  1500 MHz
CPU Minimum Frequency:               800 MHz
CPU Maximum Turbo Frequency:         3500 MHz
Uncore Minimum Frequency:            1700 MHz
Uncore Maximum Frequency:            1700 MHz
L2 Cache:                            32 x 1280 KB
L3 Cache:                            49152 KB
Hyper-threading:                     Enabled
Microcode Update Revision:           0x0D000280
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
CAPID6:                              0xB59FFFD6
CAPID7:                              0x000000FF
CAPID8:                              0xB59FFFD6
CAPID9:                              0x000000FF
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

[03/12/24 20:39:01 UTC] PTU started.

Press <Ctrl-C> to stop.


CPU_0: [IDLE] CFreq=2494, UFreq=1700, Util=90.30, IPC=0.10, Temp=64, DTS=34, Power=126.2, Volt=0.867, UVolt=0.842
CPU_0: [TESTCFG] TestSel=4 (Core AVX2), CoreMask=0xFFFFFFFFFFFFFFFF, ThreadMask=0xFF, PwrLevel=100, Turbo=1
CPU_0: [RUNNING] CFreq=2133, UFreq=1300, Util=100.00, IPC=3.91, Temp=73, DTS=25, Power=184.5, Volt=0.809, UVolt=0.785

```

## ptu -mon

```log
root@controller-0:~# /tmp/ptu -mon

Command: /tmp/ptu -mon

Intel(R) Power Thermal Utility - Server Edition v2.3.1
Release Date: 12/04/2020
Copyright (C) 2020 Intel Corporation. All rights reserved.
Intel Confidential

/dev/ptusys: No such file or directory
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> System Info:                   <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Host Name:                           controller-0
Host IP:                             169.254.202.1
OS Name:                             Debian GNU/Linux 11 (bullseye) 11
Kernel Version:                      Linux 5.10.0-6-rt-amd64 #1 SMP PREEMPT_RT StarlingX Debian 5.10.177-1.stx.73 (2023-11-25
BIOS Version:                        American Megatrends International, LLC., 0.23, 06/29/2021
Processor(s):                        1 Processor(s) Installed.
DIMM(s):                             8 DIMM(s) Installed.
Total System Memory:                 126171 MB
Available System Memory:             60591 MB


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Processor: [CPU_0]             <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU ID:                              0x000606A6 (Family 6 Model 6Ah Stepping 6)
CPU Brand Name:                      Intel(R) Xeon(R) Gold 6338N CPU @ 2.20GHz
CPU Code Name:                       Ice Lake
CPU Type:                            Production Part
CPU Segment:                         Server
CPU PPIN:                            0x0CEBB6DEA8DA6042
CPU Base Frequency:                  1500 MHz
CPU Minimum Frequency:               800 MHz
CPU Maximum Turbo Frequency:         3500 MHz
Uncore Minimum Frequency:            1700 MHz
Uncore Maximum Frequency:            1700 MHz
L2 Cache:                            32 x 1280 KB
L3 Cache:                            49152 KB
Hyper-threading:                     Enabled
Microcode Update Revision:           0x0D000280
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
CAPID6:                              0xB59FFFD6
CAPID7:                              0x000000FF
CAPID8:                              0xB59FFFD6
CAPID9:                              0x000000FF
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

[03/12/24 20:40:21 UTC] PTU started.

Press <Ctrl-C> to stop.


 Index Device Cor Thr CFreq UFreq   Util  IPC     C0     C1     C6    PC2    PC6 MC Ch Sl  Temp DTS  Power  Volt UVolt TStat TLog #TL TMargin
     0   CPU0   -   -  2133  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.39 0.812 0.795   0x0  0x0   0  12.109
     0   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.60     -     -     -  0x0   -       -
     1   CPU0   -   -  2133  1300 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.49 0.812 0.782   0x0  0x0   0  12.312
     1   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.72     -     -     -  0x0   -       -
     2   CPU0   -   -  2132  1400 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.34 0.797 0.795   0x0  0x0   0  12.125
     2   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.87     -     -     -  0x0   -       -
     3   CPU0   -   -  2134  1300 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.51 0.815 0.782   0x0  0x0   0  12.094
     3   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.65     -     -     -  0x0   -       -
     4   CPU0   -   -  2135  1300 100.00 3.88 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.51 0.800 0.782   0x0  0x0   0  12.062
     4   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.85     -     -     -  0x0   -       -
     5   CPU0   -   -  2134  1300 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.53 0.797 0.782   0x0  0x0   0  12.109
     5   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.60     -     -     -  0x0   -       -
     6   CPU0   -   -  2133  1300 100.00 3.91 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.28 0.815 0.782   0x0  0x0   0  12.047
     6   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.56     -     -     -  0x0   -       -
     7   CPU0   -   -  2133  1300 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.60 0.797 0.782   0x0  0x0   0  12.094
     7   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.58     -     -     -  0x0   -       -
     8   CPU0   -   -  2133  1300 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.49 0.812 0.782   0x0  0x0   0  12.156
     8   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.72     -     -     -  0x0   -       -
     9   CPU0   -   -  2133  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.35 0.812 0.795   0x0  0x0   0  12.109
     9   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.65     -     -     -  0x0   -       -
    10   CPU0   -   -  2133  1300 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.46 0.812 0.782   0x0  0x0   0  12.094
    10   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.68     -     -     -  0x0   -       -
    11   CPU0   -   -  2133  1300 100.00 3.91 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.59 0.797 0.782   0x0  0x0   0  12.141
    11   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.68     -     -     -  0x0   -       -
    12   CPU0   -   -  2134  1300 100.00 3.91 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.48 0.797 0.782   0x0  0x0   0  12.109
    12   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.54     -     -     -  0x0   -       -
    13   CPU0   -   -  2135  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.39 0.812 0.792   0x0  0x0   0  12.078
    13   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.70     -     -     -  0x0   -       -
    14   CPU0   -   -  2140  1300 100.00 3.87 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.30 0.815 0.782   0x0  0x0   0  11.969
    14   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.88     -     -     -  0x0   -       -
    15   CPU0   -   -  2136  1300 100.00 3.87 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.62 0.800 0.782   0x0  0x0   0  11.969
    15   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.92     -     -     -  0x0   -       -
    16   CPU0   -   -  2139  1400 100.00 3.86 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.57 0.800 0.792   0x0  0x0   0  11.938
    16   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.87     -     -     -  0x0   -       -
    17   CPU0   -   -  2133  1300 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.43 0.797 0.795   0x0  0x0   0  11.891
    17   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.64     -     -     -  0x0   -       -
    18   CPU0   -   -  2133  1300 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.49 0.797 0.782   0x0  0x0   0  12.016
    18   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.64     -     -     -  0x0   -       -
    19   CPU0   -   -  2133  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.46 0.800 0.792   0x0  0x0   0  12.016
    19   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.69     -     -     -  0x0   -       -
    20   CPU0   -   -  2133  1300 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.44 0.797 0.782   0x0  0x0   0  11.938
    20   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.77     -     -     -  0x0   -       -
    21   CPU0   -   -  2135  1300 100.00 3.88 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.52 0.800 0.782   0x0  0x0   0  11.953
    21   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.82     -     -     -  0x0   -       -
    22   CPU0   -   -  2137  1300 100.00 3.85 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.39 0.800 0.782   0x0  0x0   0  11.969
    22   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.88     -     -     -  0x0   -       -
    23   CPU0   -   -  2134  1300 100.00 3.87 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.44 0.800 0.782   0x0  0x0   0  11.922
    23   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.96     -     -     -  0x0   -       -
    24   CPU0   -   -  2134  1400 100.00 3.88 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.58 0.797 0.792   0x0  0x0   0  11.969
    24   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.84     -     -     -  0x0   -       -
    25   CPU0   -   -  2133  1300 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.45 0.797 0.782   0x0  0x0   0  12.078
    25   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.66     -     -     -  0x0   -       -
    26   CPU0   -   -  2133  1300 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.40 0.800 0.782   0x0  0x0   0  12.016
    26   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.67     -     -     -  0x0   -       -
    27   CPU0   -   -  2133  1300 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.56 0.797 0.782   0x0  0x0   0  11.984
    27   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.67     -     -     -  0x0   -       -
    28   CPU0   -   -  2134  1300 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.28 0.812 0.782   0x0  0x0   0  11.938
    28   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.64     -     -     -  0x0   -       -
    29   CPU0   -   -  2133  1300 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.53 0.797 0.782   0x0  0x0   0  11.922
    29   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.55     -     -     -  0x0   -       -
    30   CPU0   -   -  2132  1300 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.46 0.797 0.782   0x0  0x0   0  11.938
    30   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.84     -     -     -  0x0   -       -
    31   CPU0   -   -  2135  1400 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.56 0.815 0.792   0x0  0x0   0  12.031
    31   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.75     -     -     -  0x0   -       -
    32   CPU0   -   -  2136  1300 100.00 3.87 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 182.69 0.812 0.782   0x0  0x0   0  11.984
    32   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.81     -     -     -  0x0   -       -
    33   CPU0   -   -  2138  1300 100.00 3.86 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 186.10 0.815 0.782   0x0  0x0   0  11.969
    33   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.93     -     -     -  0x0   -       -
    34   CPU0   -   -  2133  1400 100.00 3.85 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.57 0.800 0.782   0x0  0x0   0  11.969
    34   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.97     -     -     -  0x0   -       -
    35   CPU0   -   -  2143  1300 100.00 3.86 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.14 0.815 0.782   0x0  0x0   0  11.922
    35   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.86     -     -     -  0x0   -       -
    36   CPU0   -   -  2139  1400 100.00 3.86 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.79 0.815 0.795   0x0  0x0   0  11.969
    36   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.90     -     -     -  0x0   -       -
    37   CPU0   -   -  2137  1300 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.45 0.812 0.782   0x0  0x0   0  11.953
    37   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.76     -     -     -  0x0   -       -
    38   CPU0   -   -  2138  1300 100.00 3.88 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.50 0.800 0.782   0x0  0x0   0  11.812
    38   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.74     -     -     -  0x0   -       -
    39   CPU0   -   -  2134  1300 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.53 0.797 0.782   0x0  0x0   0  11.859
    39   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.72     -     -     -  0x0   -       -
    40   CPU0   -   -  2135  1300 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.33 0.812 0.782   0x0  0x0   0  11.859
    40   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.82     -     -     -  0x0   -       -
    41   CPU0   -   -  2134  1300 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.59 0.812 0.782   0x0  0x0   0  11.953
    41   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.77     -     -     -  0x0   -       -
    42   CPU0   -   -  2133  1300 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.42 0.797 0.782   0x0  0x0   0  11.938
    42   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.73     -     -     -  0x0   -       -
    43   CPU0   -   -  2133  1300 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.55 0.812 0.782   0x0  0x0   0  11.906
    43   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.74     -     -     -  0x0   -       -
    44   CPU0   -   -  2133  1300 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.35 0.812 0.782   0x0  0x0   0  11.938
    44   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.68     -     -     -  0x0   -       -
    45   CPU0   -   -  2133  1400 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.59 0.797 0.792   0x0  0x0   0  11.984
    45   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.71     -     -     -  0x0   -       -
    46   CPU0   -   -  2133  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.48 0.797 0.792   0x0  0x0   0  11.734
    46   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.76     -     -     -  0x0   -       -
    47   CPU0   -   -  2133  1300 100.00 3.91 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.40 0.797 0.782   0x0  0x0   0  11.859
    47   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.65     -     -     -  0x0   -       -
    48   CPU0   -   -  2132  1400 100.00 3.91 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.40 0.812 0.792   0x0  0x0   0  11.906
    48   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.60     -     -     -  0x0   -       -
    49   CPU0   -   -  2133  1300 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.53 0.812 0.782   0x0  0x0   0  11.859
    49   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.72     -     -     -  0x0   -       -
^C
[03/12/24 20:41:14 UTC] PTU stopped.

root@controller-0:~#
```

## check sensors after load 

```log
root@controller-0:~# ipmitool sensor | grep -e CPU_0_TEMP -e CPU0_Power -e SYS_FAN_1A -e CPU_CUPS
CPU_0_TEMP       | 76.000     | degrees C  | ok    | na        | na        | na        | 96.000    | 98.000    | na
CPU0_Power       | 184.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 6125.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1A_PWM   | 22.000     | percent    | ok    | na        | na        | na        | na        | na        | na
CPU_CUPS         | 1.000      | percent    | ok    | na        | na        | na        | na        | 100.000   | na
root@controller-0:~#
```

## Observed temps raise and fans rpm raise with load - success

## MEAKV-645
## PTU 4 - Core AVX512 with Turbo
## sudo ./ptu -ct 5 -cp 100 -b 1


## Sensors before load

```log
root@controller-0:~# ipmitool sensor | grep -e CPU_0_TEMP -e CPU0_Power -e SYS_FAN_1A -e CPU_CUPS
CPU_0_TEMP       | 65.000     | degrees C  | ok    | na        | na        | na        | 96.000    | 98.000    | na
CPU0_Power       | 130.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 5000.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1A_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
CPU_CUPS         | 1.000      | percent    | ok    | na        | na        | na        | na        | 100.000   | na
root@controller-0:~#
```

## Initate load

```log
root@controller-0:~# /tmp/ptu -ct 5 -cp 100 -b 1

Command: /tmp/ptu -ct 5 -cp 100 -b 1

Intel(R) Power Thermal Utility - Server Edition v2.3.1
Release Date: 12/04/2020
Copyright (C) 2020 Intel Corporation. All rights reserved.
Intel Confidential

/dev/ptusys: No such file or directory
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> System Info:                   <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Host Name:                           controller-0
Host IP:                             169.254.202.1
OS Name:                             Debian GNU/Linux 11 (bullseye) 11
Kernel Version:                      Linux 5.10.0-6-rt-amd64 #1 SMP PREEMPT_RT StarlingX Debian 5.10.177-1.stx.73 (2023-11-25
BIOS Version:                        American Megatrends International, LLC., 0.23, 06/29/2021
Processor(s):                        1 Processor(s) Installed.
DIMM(s):                             8 DIMM(s) Installed.
Total System Memory:                 126171 MB
Available System Memory:             60366 MB


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Processor: [CPU_0]             <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU ID:                              0x000606A6 (Family 6 Model 6Ah Stepping 6)
CPU Brand Name:                      Intel(R) Xeon(R) Gold 6338N CPU @ 2.20GHz
CPU Code Name:                       Ice Lake
CPU Type:                            Production Part
CPU Segment:                         Server
CPU PPIN:                            0x0CEBB6DEA8DA6042
CPU Base Frequency:                  1500 MHz
CPU Minimum Frequency:               800 MHz
CPU Maximum Turbo Frequency:         3500 MHz
Uncore Minimum Frequency:            1700 MHz
Uncore Maximum Frequency:            1700 MHz
L2 Cache:                            32 x 1280 KB
L3 Cache:                            49152 KB
Hyper-threading:                     Enabled
Microcode Update Revision:           0x0D000280
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
CAPID6:                              0xB59FFFD6
CAPID7:                              0x000000FF
CAPID8:                              0xB59FFFD6
CAPID9:                              0x000000FF
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

[03/12/24 20:45:45 UTC] PTU started.

Press <Ctrl-C> to stop.


CPU_0: [IDLE] CFreq=2494, UFreq=1700, Util=90.50, IPC=0.07, Temp=65, DTS=33, Power=125.9, Volt=0.867, UVolt=0.842
CPU_0: [TESTCFG] TestSel=5 (Core AVX-512), CoreMask=0xFFFFFFFFFFFFFFFF, ThreadMask=0xFF, PwrLevel=100, Turbo=1
CPU_0: [RUNNING] CFreq=2058, UFreq=1300, Util=100.00, IPC=3.46, Temp=74, DTS=24, Power=184.5, Volt=0.786, UVolt=0.785
```

## ptu -mon

```log
root@controller-0:~# /tmp/ptu -mon

Command: /tmp/ptu -mon

Intel(R) Power Thermal Utility - Server Edition v2.3.1
Release Date: 12/04/2020
Copyright (C) 2020 Intel Corporation. All rights reserved.
Intel Confidential

/dev/ptusys: No such file or directory
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> System Info:                   <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Host Name:                           controller-0
Host IP:                             169.254.202.1
OS Name:                             Debian GNU/Linux 11 (bullseye) 11
Kernel Version:                      Linux 5.10.0-6-rt-amd64 #1 SMP PREEMPT_RT StarlingX Debian 5.10.177-1.stx.73 (2023-11-25
BIOS Version:                        American Megatrends International, LLC., 0.23, 06/29/2021
Processor(s):                        1 Processor(s) Installed.
DIMM(s):                             8 DIMM(s) Installed.
Total System Memory:                 126171 MB
Available System Memory:             60491 MB


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Processor: [CPU_0]             <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU ID:                              0x000606A6 (Family 6 Model 6Ah Stepping 6)
CPU Brand Name:                      Intel(R) Xeon(R) Gold 6338N CPU @ 2.20GHz
CPU Code Name:                       Ice Lake
CPU Type:                            Production Part
CPU Segment:                         Server
CPU PPIN:                            0x0CEBB6DEA8DA6042
CPU Base Frequency:                  1500 MHz
CPU Minimum Frequency:               800 MHz
CPU Maximum Turbo Frequency:         3500 MHz
Uncore Minimum Frequency:            1700 MHz
Uncore Maximum Frequency:            1700 MHz
L2 Cache:                            32 x 1280 KB
L3 Cache:                            49152 KB
Hyper-threading:                     Enabled
Microcode Update Revision:           0x0D000280
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
CAPID6:                              0xB59FFFD6
CAPID7:                              0x000000FF
CAPID8:                              0xB59FFFD6
CAPID9:                              0x000000FF
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

[03/12/24 20:46:15 UTC] PTU started.

Press <Ctrl-C> to stop.


 Index Device Cor Thr CFreq UFreq   Util  IPC     C0     C1     C6    PC2    PC6 MC Ch Sl  Temp DTS  Power  Volt UVolt TStat TLog #TL TMargin
     0   CPU0   -   -  2059  1200 100.00 3.44 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.37 0.800 0.772   0x0  0x0   0  12.766
     0   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.83     -     -     -  0x0   -       -
     1   CPU0   -   -  2059  1200 100.00 3.45 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.59 0.785 0.772   0x0  0x0   0  12.719
     1   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.76     -     -     -  0x0   -       -
     2   CPU0   -   -  2059  1300 100.00 3.44 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.46 0.800 0.785   0x0  0x0   0  12.594
     2   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.94     -     -     -  0x0   -       -
     3   CPU0   -   -  2058  1200 100.00 3.43 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 180.71 0.787 0.772   0x0  0x0   0  12.562
     3   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.81     -     -     -  0x0   -       -
     4   CPU0   -   -  2059  1200 100.00 3.44 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 188.11 0.800 0.772   0x0  0x0   0  12.500
     4   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.83     -     -     -  0x0   -       -
     5   CPU0   -   -  2060  1200 100.00 3.44 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.55 0.800 0.772   0x0  0x0   0  12.453
     5   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.77     -     -     -  0x0   -       -
     6   CPU0   -   -  2055  1200 100.00 3.46 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.40 0.800 0.772   0x0  0x0   0  12.406
     6   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.62     -     -     -  0x0   -       -
     7   CPU0   -   -  2056  1300 100.00 3.46 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.57 0.800 0.785   0x0  0x0   0  12.344
     7   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.56     -     -     -  0x0   -       -
     8   CPU0   -   -  2055  1200 100.00 3.46 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.40 0.800 0.772   0x0  0x0   0  12.234
     8   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.56     -     -     -  0x0   -       -
     9   CPU0   -   -  2056  1200 100.00 3.46 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.38 0.785 0.772   0x0  0x0   0  12.234
     9   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.55     -     -     -  0x0   -       -
    10   CPU0   -   -  2060  1300 100.00 3.45 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.52 0.785 0.785   0x0  0x0   0  12.312
    10   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.72     -     -     -  0x0   -       -
    11   CPU0   -   -  2059  1300 100.00 3.45 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.50 0.800 0.785   0x0  0x0   0  12.250
    11   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.70     -     -     -  0x0   -       -
    12   CPU0   -   -  2057  1300 100.00 3.46 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.44 0.782 0.785   0x0  0x0   0  12.328
    12   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.82     -     -     -  0x0   -       -
    13   CPU0   -   -  2055  1200 100.00 3.47 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.52 0.800 0.772   0x0  0x0   0  12.312
    13   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   9.00     -     -     -  0x0   -       -
    14   CPU0   -   -  2053  1200 100.00 3.46 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.49 0.800 0.772   0x0  0x0   0  12.344
    14   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.69     -     -     -  0x0   -       -
    15   CPU0   -   -  2056  1300 100.00 3.46 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.31 0.800 0.785   0x0  0x0   0  12.078
    15   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.69     -     -     -  0x0   -       -
    16   CPU0   -   -  2054  1300 100.00 3.46 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.49 0.800 0.785   0x0  0x0   0  12.016
    16   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.66     -     -     -  0x0   -       -
    17   CPU0   -   -  2055  1300 100.00 3.46 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.49 0.782 0.782   0x0  0x0   0  12.125
    17   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.65     -     -     -  0x0   -       -
    18   CPU0   -   -  2057  1300 100.00 3.46 100.00   0.00   0.00   0.00   0.00  -  -  -    77  21 184.59 0.800 0.782   0x0  0x0   0  12.094
    18   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.54     -     -     -  0x0   -       -
    19   CPU0   -   -  2057  1300 100.00 3.45 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.30 0.800 0.782   0x0  0x0   0  11.562
    19   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.57     -     -     -  0x0   -       -
    20   CPU0   -   -  2060  1300 100.00 3.46 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.54 0.800 0.782   0x0  0x0   0  11.781
    20   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.61     -     -     -  0x0   -       -
    21   CPU0   -   -  2061  1400 100.00 3.46 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.58 0.782 0.795   0x0  0x0   0  11.891
    21   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.60     -     -     -  0x0   -       -
    22   CPU0   -   -  2068  1200 100.00 3.44 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.41 0.800 0.772   0x0  0x0   0  11.672
    22   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.84     -     -     -  0x0   -       -
    23   CPU0   -   -  2061  1300 100.00 3.46 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.48 0.782 0.782   0x0  0x0   0  11.875
    23   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.55     -     -     -  0x0   -       -
    24   CPU0   -   -  2065  1300 100.00 3.45 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.46 0.800 0.782   0x0  0x0   0  11.984
    24   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.63     -     -     -  0x0   -       -
    25   CPU0   -   -  2065  1300 100.00 3.44 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.36 0.800 0.782   0x0  0x0   0  11.922
    25   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.79     -     -     -  0x0   -       -
    26   CPU0   -   -  2059  1300 100.00 3.45 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 181.65 0.815 0.785   0x0  0x0   0  11.875
    26   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.61     -     -     -  0x0   -       -
    27   CPU0   -   -  2061  1300 100.00 3.46 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 187.35 0.800 0.782   0x0  0x0   0  11.828
    27   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.62     -     -     -  0x0   -       -
    28   CPU0   -   -  2062  1300 100.00 3.46 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.46 0.782 0.782   0x0  0x0   0  11.438
    28   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.62     -     -     -  0x0   -       -
    29   CPU0   -   -  2068  1300 100.00 3.44 100.00   0.00   0.00   0.00   0.00  -  -  -    77  21 184.59 0.800 0.782   0x0  0x0   0  11.703
    29   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.83     -     -     -  0x0   -       -
    30   CPU0   -   -  2061  1300 100.00 3.46 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.44 0.800 0.782   0x0  0x0   0  11.625
    30   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.63     -     -     -  0x0   -       -
    31   CPU0   -   -  2062  1300 100.00 3.45 100.00   0.00   0.00   0.00   0.00  -  -  -    77  21 184.45 0.785 0.785   0x0  0x0   0  11.703
    31   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.72     -     -     -  0x0   -       -
    32   CPU0   -   -  2066  1300 100.00 3.43 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.31 0.800 0.782   0x0  0x0   0  11.578
    32   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.97     -     -     -  0x0   -       -
    33   CPU0   -   -  2066  1300 100.00 3.43 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.61 0.800 0.782   0x0  0x0   0  11.594
    33   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.90     -     -     -  0x0   -       -
    34   CPU0   -   -  2061  1200 100.00 3.45 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.41 0.782 0.772   0x0  0x0   0  11.516
    34   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.75     -     -     -  0x0   -       -
    35   CPU0   -   -  2060  1200 100.00 3.45 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 183.20 0.785 0.772   0x0  0x0   0  11.719
    35   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.67     -     -     -  0x0   -       -
    36   CPU0   -   -  2059  1300 100.00 3.45 100.00   0.00   0.00   0.00   0.00  -  -  -    77  21 185.73 0.797 0.782   0x0  0x0   0  11.516
    36   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.59     -     -     -  0x0   -       -
    37   CPU0   -   -  2061  1300 100.00 3.46 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.34 0.800 0.782   0x0  0x0   0  11.531
    37   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.65     -     -     -  0x0   -       -
    38   CPU0   -   -  2060  1200 100.00 3.46 100.00   0.00   0.00   0.00   0.00  -  -  -    77  21 184.70 0.782 0.772   0x0  0x0   0  11.406
    38   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.54     -     -     -  0x0   -       -
    39   CPU0   -   -  2062  1300 100.00 3.43 100.00   0.00   0.00   0.00   0.00  -  -  -    77  21 184.37 0.800 0.782   0x0  0x0   0  11.391
    39   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.82     -     -     -  0x0   -       -
    40   CPU0   -   -  2061  1300 100.00 3.45 100.00   0.00   0.00   0.00   0.00  -  -  -    77  21 184.51 0.782 0.782   0x0  0x0   0  11.328
    40   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.60     -     -     -  0x0   -       -
    41   CPU0   -   -  2064  1300 100.00 3.45 100.00   0.00   0.00   0.00   0.00  -  -  -    77  21 184.39 0.782 0.782   0x0  0x0   0  11.312
    41   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.74     -     -     -  0x0   -       -
    42   CPU0   -   -  2064  1200 100.00 3.44 100.00   0.00   0.00   0.00   0.00  -  -  -    77  21 184.53 0.800 0.772   0x0  0x0   0  11.281
    42   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.84     -     -     -  0x0   -       -
    43   CPU0   -   -  2062  1200 100.00 3.45 100.00   0.00   0.00   0.00   0.00  -  -  -    77  21 184.52 0.800 0.772   0x0  0x0   0  11.219
    43   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.67     -     -     -  0x0   -       -
    44   CPU0   -   -  2061  1200 100.00 3.45 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.34 0.782 0.772   0x0  0x0   0  11.375
    44   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.68     -     -     -  0x0   -       -
    45   CPU0   -   -  2058  1200 100.00 3.46 100.00   0.00   0.00   0.00   0.00  -  -  -    77  21 184.62 0.800 0.772   0x0  0x0   0  11.172
    45   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.65     -     -     -  0x0   -       -
    46   CPU0   -   -  2061  1300 100.00 3.46 100.00   0.00   0.00   0.00   0.00  -  -  -    77  21 184.44 0.800 0.785   0x0  0x0   0  11.172
    46   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.63     -     -     -  0x0   -       -
    47   CPU0   -   -  2062  1300 100.00 3.46 100.00   0.00   0.00   0.00   0.00  -  -  -    77  21 184.43 0.800 0.782   0x0  0x0   0  11.203
    47   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.77     -     -     -  0x0   -       -
    48   CPU0   -   -  2060  1200 100.00 3.46 100.00   0.00   0.00   0.00   0.00  -  -  -    77  21 184.39 0.800 0.772   0x0  0x0   0  11.031
    48   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.52     -     -     -  0x0   -       -
^C
[03/12/24 20:47:08 UTC] PTU stopped.

root@controller-0:~#
```

## check sensors

```log
root@controller-0:~# ipmitool sensor | grep -e CPU_0_TEMP -e CPU0_Power -e SYS_FAN_1A -e CPU_CUPS
CPU_0_TEMP       | 77.000     | degrees C  | ok    | na        | na        | na        | 96.000    | 98.000    | na
CPU0_Power       | 184.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 6125.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1A_PWM   | 22.000     | percent    | ok    | na        | na        | na        | na        | na        | na
CPU_CUPS         | 1.000      | percent    | ok    | na        | na        | na        | na        | 100.000   | na
root@controller-0:~#
```


## Success, was able to observe temp rise, then fans increasing as load was started


## MEAKV-646 
## PTU 5 - Turbo Test
## sudo ./ptu -ct 8 -allcore -b 1

## sensors before load

```log
root@controller-0:~# ipmitool sensor | grep -e CPU_0_TEMP -e CPU0_Power -e SYS_FAN_1A -e CPU_CUPS
CPU_0_TEMP       | 64.000     | degrees C  | ok    | na        | na        | na        | 96.000    | 98.000    | na
CPU0_Power       | 125.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 5000.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1A_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
CPU_CUPS         | 1.000      | percent    | ok    | na        | na        | na        | na        | 100.000   | na
root@controller-0:~#
```

## Initiating load

```log
root@controller-0:~# /tmp/ptu -ct 8 -allcore -b 1

Command: /tmp/ptu -ct 8 -allcore -b 1

Intel(R) Power Thermal Utility - Server Edition v2.3.1
Release Date: 12/04/2020
Copyright (C) 2020 Intel Corporation. All rights reserved.
Intel Confidential

/dev/ptusys: No such file or directory
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> System Info:                   <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Host Name:                           controller-0
Host IP:                             169.254.202.1
OS Name:                             Debian GNU/Linux 11 (bullseye) 11
Kernel Version:                      Linux 5.10.0-6-rt-amd64 #1 SMP PREEMPT_RT StarlingX Debian 5.10.177-1.stx.73 (2023-11-25
BIOS Version:                        American Megatrends International, LLC., 0.23, 06/29/2021
Processor(s):                        1 Processor(s) Installed.
DIMM(s):                             8 DIMM(s) Installed.
Total System Memory:                 126171 MB
Available System Memory:             60585 MB


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Processor: [CPU_0]             <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU ID:                              0x000606A6 (Family 6 Model 6Ah Stepping 6)
CPU Brand Name:                      Intel(R) Xeon(R) Gold 6338N CPU @ 2.20GHz
CPU Code Name:                       Ice Lake
CPU Type:                            Production Part
CPU Segment:                         Server
CPU PPIN:                            0x0CEBB6DEA8DA6042
CPU Base Frequency:                  1500 MHz
CPU Minimum Frequency:               800 MHz
CPU Maximum Turbo Frequency:         3500 MHz
Uncore Minimum Frequency:            1700 MHz
Uncore Maximum Frequency:            1700 MHz
L2 Cache:                            32 x 1280 KB
L3 Cache:                            49152 KB
Hyper-threading:                     Enabled
Microcode Update Revision:           0x0D000280
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
CAPID6:                              0xB59FFFD6
CAPID7:                              0x000000FF
CAPID8:                              0xB59FFFD6
CAPID9:                              0x000000FF
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

[03/12/24 21:00:12 UTC] PTU started.

Press <Ctrl-C> to stop.


CPU_0: [IDLE] CFreq=2494, UFreq=1700, Util=91.67, IPC=0.06, Temp=65, DTS=33, Power=125.7, Volt=0.867, UVolt=0.842

### TURBO is enabled ###

Instr   CPU #Cores CFreq(act) CFreq(exp) UFreq Power TDP  Temp Volt  UVolt
IA/SSE  0   32     2.5        2.7        1.7   140.4 185  66   0.865 0.842



```

## ptu -mon

```log
root@controller-0:~# /tmp/ptu -mon

Command: /tmp/ptu -mon

Intel(R) Power Thermal Utility - Server Edition v2.3.1
Release Date: 12/04/2020
Copyright (C) 2020 Intel Corporation. All rights reserved.
Intel Confidential

/dev/ptusys: No such file or directory
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> System Info:                   <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Host Name:                           controller-0
Host IP:                             169.254.202.1
OS Name:                             Debian GNU/Linux 11 (bullseye) 11
Kernel Version:                      Linux 5.10.0-6-rt-amd64 #1 SMP PREEMPT_RT StarlingX Debian 5.10.177-1.stx.73 (2023-11-25
BIOS Version:                        American Megatrends International, LLC., 0.23, 06/29/2021
Processor(s):                        1 Processor(s) Installed.
DIMM(s):                             8 DIMM(s) Installed.
Total System Memory:                 126171 MB
Available System Memory:             60632 MB


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Processor: [CPU_0]             <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU ID:                              0x000606A6 (Family 6 Model 6Ah Stepping 6)
CPU Brand Name:                      Intel(R) Xeon(R) Gold 6338N CPU @ 2.20GHz
CPU Code Name:                       Ice Lake
CPU Type:                            Production Part
CPU Segment:                         Server
CPU PPIN:                            0x0CEBB6DEA8DA6042
CPU Base Frequency:                  1500 MHz
CPU Minimum Frequency:               800 MHz
CPU Maximum Turbo Frequency:         3500 MHz
Uncore Minimum Frequency:            1700 MHz
Uncore Maximum Frequency:            1700 MHz
L2 Cache:                            32 x 1280 KB
L3 Cache:                            49152 KB
Hyper-threading:                     Enabled
Microcode Update Revision:           0x0D000280
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
CAPID6:                              0xB59FFFD6
CAPID7:                              0x000000FF
CAPID8:                              0xB59FFFD6
CAPID9:                              0x000000FF
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

[03/12/24 21:00:58 UTC] PTU started.

Press <Ctrl-C> to stop.


 Index Device Cor Thr CFreq UFreq   Util  IPC     C0     C1     C6    PC2    PC6 MC Ch Sl  Temp DTS  Power  Volt UVolt TStat TLog #TL TMargin
     0   CPU0   -   -  2494  1700  90.76 0.06  96.44   3.56   0.00   0.00   0.00  -  -  -    65  33 126.33 0.870 0.842   0x0  0x0   0  23.234
     0   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.82     -     -     -  0x0   -       -
     1   CPU0   -   -  2494  1700  91.77 0.11  97.45   2.55   0.00   0.00   0.00  -  -  -    65  33 127.57 0.870 0.842   0x0  0x0   0  23.156
     1   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.95     -     -     -  0x0   -       -
     2   CPU0   -   -  2494  1700  90.41 0.08  96.20   3.80   0.00   0.00   0.00  -  -  -    65  33 126.37 0.870 0.842   0x0  0x0   0  23.016
     2   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.78     -     -     -  0x0   -       -
     3   CPU0   -   -  2494  1700  90.58 0.08  96.23   3.77   0.00   0.00   0.00  -  -  -    65  33 126.03 0.870 0.842   0x0  0x0   0  23.141
     3   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.84     -     -     -  0x0   -       -
     4   CPU0   -   -  2494  1700  90.48 0.06  96.19   3.81   0.00   0.00   0.00  -  -  -    65  33 126.02 0.870 0.842   0x0  0x0   0  23.125
     4   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.80     -     -     -  0x0   -       -
     5   CPU0   -   -  2494  1700  89.49 0.08  95.95   4.05   0.00   0.00   0.00  -  -  -    65  33 126.20 0.870 0.842   0x0  0x0   0  23.000
     5   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.86     -     -     -  0x0   -       -
     6   CPU0   -   -  2494  1700  90.72 0.07  96.33   3.67   0.00   0.00   0.00  -  -  -    65  33 126.04 0.870 0.842   0x0  0x0   0  23.188
     6   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.76     -     -     -  0x0   -       -
     7   CPU0   -   -  2494  1700  90.83 0.10  96.82   3.18   0.00   0.00   0.00  -  -  -    64  34 126.76 0.870 0.842   0x0  0x0   0  23.141
     7   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.85     -     -     -  0x0   -       -
     8   CPU0   -   -  2494  1700  90.40 0.07  96.15   3.85   0.00   0.00   0.00  -  -  -    65  33 125.92 0.870 0.842   0x0  0x0   0  23.078
     8   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.66     -     -     -  0x0   -       -
     9   CPU0   -   -  2494  1700  90.03 0.09  95.83   4.17   0.00   0.00   0.00  -  -  -    66  32 126.15 0.870 0.842   0x0  0x0   0  23.109
     9   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.73     -     -     -  0x0   -       -
    10   CPU0   -   -  2494  1700  91.43 0.07  96.51   3.49   0.00   0.00   0.00  -  -  -    65  33 126.55 0.870 0.842   0x0  0x0   0  23.125
    10   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.69     -     -     -  0x0   -       -
    11   CPU0   -   -  2494  1700  90.46 0.08  96.33   3.67   0.00   0.00   0.00  -  -  -    65  33 126.22 0.870 0.842   0x0  0x0   0  22.984
    11   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.70     -     -     -  0x0   -       -
    12   CPU0   -   -  2494  1700  90.64 0.05  95.86   4.14   0.00   0.00   0.00  -  -  -    65  33 125.64 0.870 0.842   0x0  0x0   0  23.141
    12   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.82     -     -     -  0x0   -       -
    13   CPU0   -   -  2494  1700  88.35 0.10  95.75   4.25   0.00   0.00   0.00  -  -  -    65  33 126.15 0.870 0.842   0x0  0x0   0  23.219
    13   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.95     -     -     -  0x0   -       -
    14   CPU0   -   -  2494  1700  89.35 0.08  96.10   3.90   0.00   0.00   0.00  -  -  -    65  33 126.18 0.870 0.842   0x0  0x0   0  23.250
    14   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.97     -     -     -  0x0   -       -
    15   CPU0   -   -  2494  1700  91.53 0.10  97.52   2.48   0.00   0.00   0.00  -  -  -    65  33 127.18 0.870 0.842   0x0  0x0   0  23.188
    15   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.97     -     -     -  0x0   -       -
    16   CPU0   -   -  2494  1700  92.68 0.10  97.88   2.12   0.00   0.00   0.00  -  -  -    65  33 127.79 0.870 0.842   0x0  0x0   0  23.125
    16   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   9.00     -     -     -  0x0   -       -
    17   CPU0   -   -  2494  1700  90.51 0.09  97.16   2.84   0.00   0.00   0.00  -  -  -    64  34 127.15 0.870 0.842   0x0  0x0   0  23.031
    17   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.98     -     -     -  0x0   -       -
    18   CPU0   -   -  2494  1700  91.90 0.09  97.83   2.17   0.00   0.00   0.00  -  -  -    65  33 127.43 0.870 0.842   0x0  0x0   0  23.250
    18   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.93     -     -     -  0x0   -       -
    19   CPU0   -   -  2494  1700  92.47 0.09  97.71   2.29   0.00   0.00   0.00  -  -  -    65  33 127.26 0.870 0.842   0x0  0x0   0  23.125
    19   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.96     -     -     -  0x0   -       -
    20   CPU0   -   -  2494  1700  93.65 0.13  99.09   0.91   0.00   0.00   0.00  -  -  -    66  32 129.25 0.867 0.842   0x0  0x0   0  22.484
    20   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   9.07     -     -     -  0x0   -       -
    21   CPU0   -   -  2494  1700  92.99 0.15  99.34   0.66   0.00   0.00   0.00  -  -  -    66  32 129.93 0.870 0.842   0x0  0x0   0  22.281
    21   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   9.10     -     -     -  0x0   -       -
    22   CPU0   -   -  2494  1700  91.61 0.14  98.33   1.67   0.00   0.00   0.00  -  -  -    65  33 128.77 0.870 0.842   0x0  0x0   0  22.922
    22   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   9.01     -     -     -  0x0   -       -
    23   CPU0   -   -  2494  1700  91.17 0.14  97.86   2.14   0.00   0.00   0.00  -  -  -    66  32 128.03 0.870 0.842   0x0  0x0   0  22.625
    23   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.97     -     -     -  0x0   -       -
    24   CPU0   -   -  2494  1700  91.97 0.14  97.99   2.01   0.00   0.00   0.00  -  -  -    65  33 128.22 0.870 0.842   0x0  0x0   0  22.922
    24   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.93     -     -     -  0x0   -       -
    25   CPU0   -   -  2494  1700  91.27 0.15  97.63   2.37   0.00   0.00   0.00  -  -  -    65  33 128.31 0.870 0.842   0x0  0x0   0  22.969
    25   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.99     -     -     -  0x0   -       -
    26   CPU0   -   -  2494  1700  90.50 0.08  96.50   3.50   0.00   0.00   0.00  -  -  -    65  33 126.11 0.870 0.842   0x0  0x0   0  23.219
    26   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.95     -     -     -  0x0   -       -
    27   CPU0   -   -  2494  1700  90.89 0.05  96.19   3.81   0.00   0.00   0.00  -  -  -    64  34 125.77 0.870 0.842   0x0  0x0   0  23.469
    27   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.77     -     -     -  0x0   -       -
    28   CPU0   -   -  2494  1700  91.41 0.06  96.55   3.45   0.00   0.00   0.00  -  -  -    64  34 125.75 0.870 0.842   0x0  0x0   0  23.266
    28   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.79     -     -     -  0x0   -       -
    29   CPU0   -   -  2494  1700  93.10 0.14  98.78   1.22   0.00   0.00   0.00  -  -  -    65  33 129.23 0.870 0.842   0x0  0x0   0  22.875
    29   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   9.02     -     -     -  0x0   -       -
    30   CPU0   -   -  2494  1700  93.52 0.12  98.72   1.28   0.00   0.00   0.00  -  -  -    65  33 128.77 0.870 0.842   0x0  0x0   0  22.469
    30   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.98     -     -     -  0x0   -       -
    31   CPU0   -   -  2494  1700  91.23 0.07  96.38   3.62   0.00   0.00   0.00  -  -  -    65  33 126.40 0.870 0.842   0x0  0x0   0  23.359
    31   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.85     -     -     -  0x0   -       -
    32   CPU0   -   -  2494  1700  89.96 0.09  96.50   3.50   0.00   0.00   0.00  -  -  -    65  33 126.56 0.870 0.842   0x0  0x0   0  23.375
    32   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.94     -     -     -  0x0   -       -
    33   CPU0   -   -  2494  1700  88.46 0.10  95.62   4.38   0.00   0.00   0.00  -  -  -    65  33 126.18 0.870 0.842   0x0  0x0   0  23.438
    33   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.87     -     -     -  0x0   -       -
    34   CPU0   -   -  2494  1700  91.36 0.06  96.63   3.37   0.00   0.00   0.00  -  -  -    65  33 126.27 0.870 0.842   0x0  0x0   0  23.406
    34   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.73     -     -     -  0x0   -       -
    35   CPU0   -   -  2494  1700  90.42 0.05  95.81   4.19   0.00   0.00   0.00  -  -  -    65  33 125.40 0.870 0.842   0x0  0x0   0  23.422
    35   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.71     -     -     -  0x0   -       -
    36   CPU0   -   -  2494  1700  91.32 0.07  96.51   3.49   0.00   0.00   0.00  -  -  -    65  33 126.01 0.870 0.842   0x0  0x0   0  23.375
    36   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.75     -     -     -  0x0   -       -
    37   CPU0   -   -  2494  1700  89.48 0.07  95.73   4.27   0.00   0.00   0.00  -  -  -    65  33 125.94 0.870 0.842   0x0  0x0   0  23.547
    37   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.74     -     -     -  0x0   -       -
    38   CPU0   -   -  2494  1700  91.12 0.07  96.68   3.32   0.00   0.00   0.00  -  -  -    65  33 126.32 0.870 0.842   0x0  0x0   0  23.359
    38   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.71     -     -     -  0x0   -       -
    39   CPU0   -   -  2494  1700  90.85 0.08  96.15   3.85   0.00   0.00   0.00  -  -  -    65  33 126.21 0.870 0.842   0x0  0x0   0  23.438
    39   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.65     -     -     -  0x0   -       -
    40   CPU0   -   -  2494  1700  92.38 0.11  97.52   2.48   0.00   0.00   0.00  -  -  -    65  33 127.69 0.870 0.842   0x0  0x0   0  23.094
    40   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.96     -     -     -  0x0   -       -
    41   CPU0   -   -  2494  1700  90.36 0.08  95.93   4.07   0.00   0.00   0.00  -  -  -    65  33 126.01 0.870 0.842   0x0  0x0   0  23.141
    41   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.91     -     -     -  0x0   -       -
    42   CPU0   -   -  2494  1700  91.18 0.08  96.12   3.88   0.00   0.00   0.00  -  -  -    64  34 126.61 0.870 0.842   0x0  0x0   0  23.172
    42   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.96     -     -     -  0x0   -       -
    43   CPU0   -   -  2494  1700  89.51 0.06  95.37   4.63   0.00   0.00   0.00  -  -  -    65  33 125.80 0.870 0.842   0x0  0x0   0  23.328
    43   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.89     -     -     -  0x0   -       -
    44   CPU0   -   -  2494  1700  91.51 0.08  96.49   3.51   0.00   0.00   0.00  -  -  -    65  33 126.40 0.870 0.842   0x0  0x0   0  23.297
    44   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.84     -     -     -  0x0   -       -
    45   CPU0   -   -  2494  1700  90.88 0.10  96.32   3.68   0.00   0.00   0.00  -  -  -    65  33 126.47 0.870 0.842   0x0  0x0   0  23.359
    45   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.89     -     -     -  0x0   -       -
    46   CPU0   -   -  2494  1700  91.26 0.10  95.87   4.13   0.00   0.00   0.00  -  -  -    65  33 126.41 0.870 0.842   0x0  0x0   0  23.125
    46   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.96     -     -     -  0x0   -       -
    47   CPU0   -   -  2494  1700  91.79 0.07  96.20   3.80   0.00   0.00   0.00  -  -  -    64  34 125.97 0.870 0.842   0x0  0x0   0  23.328
    47   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.90     -     -     -  0x0   -       -
    48   CPU0   -   -  2494  1700  91.75 0.11  96.42   3.58   0.00   0.00   0.00  -  -  -    66  32 126.73 0.870 0.842   0x0  0x0   0  23.219
    48   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.96     -     -     -  0x0   -       -
    49   CPU0   -   -  2494  1700  91.37 0.07  96.03   3.97   0.00   0.00   0.00  -  -  -    64  34 126.04 0.870 0.842   0x0  0x0   0  23.375
    49   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.79     -     -     -  0x0   -       -
    50   CPU0   -   -  2494  1700  90.20 0.06  95.64   4.36   0.00   0.00   0.00  -  -  -    65  33 125.73 0.870 0.842   0x0  0x0   0  23.516
    50   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.76     -     -     -  0x0   -       -
    51   CPU0   -   -  2494  1700  89.71 0.09  95.54   4.46   0.00   0.00   0.00  -  -  -    65  33 126.03 0.870 0.842   0x0  0x0   0  23.406
    51   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.77     -     -     -  0x0   -       -
    52   CPU0   -   -  2494  1700  89.82 0.13  96.87   3.13   0.00   0.00   0.00  -  -  -    65  33 127.38 0.870 0.842   0x0  0x0   0  23.391
    52   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.87     -     -     -  0x0   -       -
    53   CPU0   -   -  2494  1700  90.80 0.12  97.70   2.30   0.00   0.00   0.00  -  -  -    64  34 127.59 0.870 0.842   0x0  0x0   0  23.453
    53   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.86     -     -     -  0x0   -       -
    54   CPU0   -   -  2494  1700  91.47 0.12  97.56   2.44   0.00   0.00   0.00  -  -  -    64  34 127.74 0.870 0.842   0x0  0x0   0  23.312
    54   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.86     -     -     -  0x0   -       -
    55   CPU0   -   -  2494  1700  92.38 0.10  97.78   2.22   0.00   0.00   0.00  -  -  -    66  32 127.50 0.870 0.842   0x0  0x0   0  23.359
    55   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.81     -     -     -  0x0   -       -
    56   CPU0   -   -  2494  1700  90.66 0.13  97.20   2.80   0.00   0.00   0.00  -  -  -    64  34 127.85 0.870 0.842   0x0  0x0   0  23.000
    56   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.97     -     -     -  0x0   -       -
    57   CPU0   -   -  2494  1700  90.65 0.16  97.51   2.49   0.00   0.00   0.00  -  -  -    65  33 127.68 0.870 0.842   0x0  0x0   0  23.172
    57   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.97     -     -     -  0x0   -       -
    58   CPU0   -   -  2494  1700  92.61 0.13  97.91   2.09   0.00   0.00   0.00  -  -  -    65  33 128.10 0.870 0.842   0x0  0x0   0  22.656
    58   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.85     -     -     -  0x0   -       -
    59   CPU0   -   -  2494  1700  93.25 0.15  98.86   1.14   0.00   0.00   0.00  -  -  -    66  32 129.43 0.870 0.842   0x0  0x0   0  22.984
    59   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   9.05     -     -     -  0x0   -       -
    60   CPU0   -   -  2494  1700  90.71 0.18  97.67   2.33   0.00   0.00   0.00  -  -  -    66  32 128.66 0.870 0.842   0x0  0x0   0  23.203
    60   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   9.02     -     -     -  0x0   -       -
    61   CPU0   -   -  2494  1700  91.80 0.14  97.52   2.48   0.00   0.00   0.00  -  -  -    65  33 128.00 0.870 0.842   0x0  0x0   0  22.812
    61   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.96     -     -     -  0x0   -       -
    62   CPU0   -   -  2494  1700  91.61 0.07  96.53   3.47   0.00   0.00   0.00  -  -  -    65  33 126.33 0.870 0.842   0x0  0x0   0  23.297
    62   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.86     -     -     -  0x0   -       -
    63   CPU0   -   -  2494  1700  90.09 0.06  95.67   4.33   0.00   0.00   0.00  -  -  -    64  34 125.89 0.870 0.842   0x0  0x0   0  23.406
    63   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.78     -     -     -  0x0   -       -
    64   CPU0   -   -  2494  1700  90.89 0.09  96.39   3.61   0.00   0.00   0.00  -  -  -    64  34 126.59 0.870 0.842   0x0  0x0   0  23.453
    64   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.88     -     -     -  0x0   -       -
    65   CPU0   -   -  2494  1700  91.15 0.08  96.08   3.92   0.00   0.00   0.00  -  -  -    65  33 126.24 0.870 0.842   0x0  0x0   0  23.578
    65   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.90     -     -     -  0x0   -       -
    66   CPU0   -   -  2494  1700  89.75 0.08  95.48   4.52   0.00   0.00   0.00  -  -  -    64  34 125.59 0.870 0.842   0x0  0x0   0  23.438
    66   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.80     -     -     -  0x0   -       -
    67   CPU0   -   -  2494  1700  91.21 0.06  95.85   4.15   0.00   0.00   0.00  -  -  -    64  34 125.79 0.870 0.842   0x0  0x0   0  23.328
    67   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.76     -     -     -  0x0   -       -
    68   CPU0   -   -  2494  1700  90.64 0.10  96.23   3.77   0.00   0.00   0.00  -  -  -    65  33 126.37 0.870 0.842   0x0  0x0   0  23.406
    68   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.81     -     -     -  0x0   -       -
    69   CPU0   -   -  2494  1700  91.10 0.07  96.23   3.77   0.00   0.00   0.00  -  -  -    65  33 126.12 0.870 0.842   0x0  0x0   0  23.391
    69   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.71     -     -     -  0x0   -       -
    70   CPU0   -   -  2494  1700  90.17 0.08  96.24   3.76   0.00   0.00   0.00  -  -  -    64  34 126.38 0.870 0.842   0x0  0x0   0  23.391
    70   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.91     -     -     -  0x0   -       -
    71   CPU0   -   -  2494  1700  87.96 0.09  95.44   4.56   0.00   0.00   0.00  -  -  -    65  33 125.94 0.870 0.842   0x0  0x0   0  23.500
    71   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.96     -     -     -  0x0   -       -
    72   CPU0   -   -  2494  1700  89.82 0.11  95.86   4.14   0.00   0.00   0.00  -  -  -    64  34 126.50 0.870 0.842   0x0  0x0   0  23.438
    72   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.86     -     -     -  0x0   -       -
    73   CPU0   -   -  2494  1700  91.97 0.09  97.11   2.89   0.00   0.00   0.00  -  -  -    65  33 126.72 0.870 0.842   0x0  0x0   0  23.469
    73   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.72     -     -     -  0x0   -       -
    74   CPU0   -   -  2494  1700  93.19 0.13  97.96   2.04   0.00   0.00   0.00  -  -  -    66  32 128.21 0.867 0.842   0x0  0x0   0  22.703
    74   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.95     -     -     -  0x0   -       -
    75   CPU0   -   -  2494  1700  92.47 0.12  97.56   2.44   0.00   0.00   0.00  -  -  -    66  32 128.04 0.867 0.842   0x0  0x0   0  23.422
    75   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.86     -     -     -  0x0   -       -
    76   CPU0   -   -  2494  1700  91.64 0.12  97.74   2.26   0.00   0.00   0.00  -  -  -    64  34 128.26 0.870 0.842   0x0  0x0   0  23.359
    76   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.91     -     -     -  0x0   -       -
    77   CPU0   -   -  2494  1700  90.98 0.11  96.80   3.20   0.00   0.00   0.00  -  -  -    64  34 126.99 0.870 0.842   0x0  0x0   0  23.453
    77   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.82     -     -     -  0x0   -       -
    78   CPU0   -   -  2494  1700  92.94 0.12  98.18   1.82   0.00   0.00   0.00  -  -  -    65  33 128.62 0.870 0.842   0x0  0x0   0  22.625
    78   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.97     -     -     -  0x0   -       -
    79   CPU0   -   -  2494  1700  90.78 0.09  96.36   3.64   0.00   0.00   0.00  -  -  -    65  33 126.50 0.870 0.842   0x0  0x0   0  23.469
    79   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.75     -     -     -  0x0   -       -
    80   CPU0   -   -  2494  1700  91.55 0.12  96.64   3.36   0.00   0.00   0.00  -  -  -    65  33 127.46 0.870 0.842   0x0  0x0   0  22.688
    80   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.86     -     -     -  0x0   -       -
    81   CPU0   -   -  2494  1700  90.23 0.07  95.78   4.22   0.00   0.00   0.00  -  -  -    65  33 126.23 0.870 0.842   0x0  0x0   0  23.406
    81   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.79     -     -     -  0x0   -       -
    82   CPU0   -   -  2494  1700  91.17 0.05  96.12   3.88   0.00   0.00   0.00  -  -  -    65  33 125.85 0.870 0.842   0x0  0x0   0  23.516
    82   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    40   -   8.72     -     -     -  0x0   -       -
^C
[03/12/24 21:02:26 UTC] PTU stopped.

root@controller-0:~#
```

## Sensors after load started

```log
root@controller-0:~# ipmitool sensor | grep -e CPU_0_TEMP -e CPU0_Power -e SYS_FAN_1A -e CPU_CUPS
CPU_0_TEMP       | 64.000     | degrees C  | ok    | na        | na        | na        | 96.000    | 98.000    | na
CPU0_Power       | 125.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 5000.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1A_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
CPU_CUPS         | 1.000      | percent    | ok    | na        | na        | na        | na        | 100.000   | na
root@controller-0:~#

```


## Temps didn't rise as much as with other tests, but all data recorded, no issues found.
## Success, end of performance tests with PTU

