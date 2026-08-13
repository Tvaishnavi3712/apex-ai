# ZT .45 BMC firmware validation
# 10/24/23 James Patchett

## Target Controller Rchltxfe-c000000-001
Controller-0 iLO 2607:f160:a:d02e:cd:fe0::8000 
Controller-1 iLO 2607:f160:a:d02e:cd:fe0::8001
Worker-0 iLO 2607:f160:a:d02e:cd:fe0::8002 
OAM 2607:f160:0:3043:cd:290:0:10



## Target Subcloud welktxef-d931887-021 (currently on controller 2607:f160:0:3049:cd:290:0:10 )
OAM 2607:f160:10:9249:ce:40a:0:f409
BMC 2607:f160:10:9249:ce:40a:0:e015

welktxef-931887-rz-le2pts6-021.yaml

ipmitool -I lanplus -U XXXXXX -P XXXXXX -H 2607:f160:10:9249:ce:40a:0:e015 sol activate

## Subcloud welktxef-d931887-021

## Performance Test sudo ./ptu -ct 1 -b 0
## measure sensors first, then run load, then check during load

## Sensors
```log
[XXXXXX@controller-0 ~(keystone_admin)]$ sudo ipmitool sensor | grep -e CPU_0_TEMP -e CPU0_Power -e SYS_FAN_1A -e CPU_CUPS
Password:
XXXXXX       | 52.000     | degrees C  | ok    | na        | na        | na        | 96.000    | 98.000    | na
CPU0_Power       | 91.000     | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 5125.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1A_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
CPU_CUPS         | 3.000      | percent    | ok    | na        | na        | na        | na        | 100.000   | na
[XXXXXX@controller-0 ~(keystone_admin)]$
```

## Initiate load 

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ sudo ipmitool sensor | grep -e CPU_0_TEMP -e CPU0_Power -e SYS_FAN_1A -e CPU_CUPS
Password:
XXXXXX       | 52.000     | degrees C  | ok    | na        | na        | na        | 96.000    | 98.000    | na
CPU0_Power       | 91.000     | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 5125.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1A_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
CPU_CUPS         | 3.000      | percent    | ok    | na        | na        | na        | na        | 100.000   | na
(reverse-i-search)`p': sudo ipmitool sensor | gre^C-e CPU_0_TEMP -e CPU0_Power -e SYS_FAN_1A -e CPU_CUPS
(reverse-i-search)`': ^C
[XXXXXX@controller-0 ~(keystone_admin)]$ kls
-bash: kls: command not found
[XXXXXX@controller-0 ~(keystone_admin)]$ sudo ./ptu -ct 1 -b 0

Command: ./ptu -ct 1 -b 0

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
Available System Memory:             79119 MB


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

[10/30/23 20:44:32 UTC] PTU started.

Press <Ctrl-C> to stop.


CPU_0: [IDLE] CFreq=2496, UFreq=1700, Util=0.67, IPC=0.87, Temp=53, DTS=45, Power=92.0, Volt=0.878, UVolt=0.870
CPU_0: [TESTCFG] TestSel=1 (TDP), CoreMask=0xFFFFFFFFFFFFFFFF, ThreadMask=0xFF, PwrLevel=TDP, Turbo=0
CPU_0: [RUNNING] CFreq=2375, UFreq=1500, Util=100.00, IPC=3.15, Temp=65, DTS=33, Power=184.5, Volt=0.854, UVolt=0.832


```

## Ptu monitoring

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ sudo ./ptu -mon

Command: ./ptu -mon

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
Available System Memory:             79049 MB


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

[10/30/23 20:49:07 UTC] PTU started.

Press <Ctrl-C> to stop.


 Index Device Cor Thr CFreq UFreq   Util  IPC     C0     C1     C6    PC2    PC6 MC Ch Sl  Temp DTS  Power  Volt UVolt TStat TLog #TL TMargin
     0   CPU0   -   -  2356  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.55 0.830 0.822   0x0  0x0   0  12.672
     0   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.93     -     -     -  0x0   -       -
     1   CPU0   -   -  2357  1500 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.31 0.830 0.822   0x0  0x0   0  12.438
     1   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.89     -     -     -  0x0   -       -
     2   CPU0   -   -  2356  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.39 0.847 0.822   0x0  0x0   0  12.703
     2   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.88     -     -     -  0x0   -       -
     3   CPU0   -   -  2357  1400 100.00 3.14 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.59 0.847 0.805   0x0  0x0   0  12.656
     3   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.91     -     -     -  0x0   -       -
     4   CPU0   -   -  2357  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.56 0.845 0.822   0x0  0x0   0  12.766
     4   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.80     -     -     -  0x0   -       -
     5   CPU0   -   -  2356  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.52 0.845 0.822   0x0  0x0   0  12.766
     5   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.85     -     -     -  0x0   -       -
     6   CPU0   -   -  2356  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.36 0.847 0.822   0x0  0x0   0  12.781
     6   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.99     -     -     -  0x0   -       -
     7   CPU0   -   -  2355  1500 100.00 3.14 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.56 0.830 0.822   0x0  0x0   0  12.688
     7   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.12     -     -     -  0x0   -       -
     8   CPU0   -   -  2356  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.52 0.830 0.822   0x0  0x0   0  12.766
     8   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.86     -     -     -  0x0   -       -
     9   CPU0   -   -  2356  1400 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.45 0.845 0.805   0x0  0x0   0  12.484
     9   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.82     -     -     -  0x0   -       -
    10   CPU0   -   -  2356  1500 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.51 0.830 0.822   0x0  0x0   0  12.719
    10   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.69     -     -     -  0x0   -       -
    11   CPU0   -   -  2356  1500 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.36 0.845 0.822   0x0  0x0   0  12.688
    11   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.77     -     -     -  0x0   -       -
    12   CPU0   -   -  2355  1500 100.00 3.14 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.54 0.847 0.805   0x0  0x0   0  12.594
    12   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.97     -     -     -  0x0   -       -
    13   CPU0   -   -  2356  1400 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.38 0.845 0.805   0x0  0x0   0  12.703
    13   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.80     -     -     -  0x0   -       -
    14   CPU0   -   -  2356  1500 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.57 0.830 0.820   0x0  0x0   0  12.578
    14   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.74     -     -     -  0x0   -       -
    15   CPU0   -   -  2356  1500 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.36 0.830 0.822   0x0  0x0   0  12.875
    15   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.87     -     -     -  0x0   -       -
    16   CPU0   -   -  2356  1400 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.51 0.845 0.805   0x0  0x0   0  12.578
    16   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.93     -     -     -  0x0   -       -
    17   CPU0   -   -  2356  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.45 0.845 0.820   0x0  0x0   0  12.672
    17   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.98     -     -     -  0x0   -       -
    18   CPU0   -   -  2356  1400 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.53 0.845 0.805   0x0  0x0   0  12.703
    18   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.89     -     -     -  0x0   -       -
    19   CPU0   -   -  2355  1400 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.40 0.847 0.805   0x0  0x0   0  12.656
    19   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.98     -     -     -  0x0   -       -
    20   CPU0   -   -  2356  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.59 0.845 0.822   0x0  0x0   0  12.719
    20   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.96     -     -     -  0x0   -       -
    21   CPU0   -   -  2356  1400 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.25 0.830 0.805   0x0  0x0   0  12.734
    21   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.97     -     -     -  0x0   -       -
    22   CPU0   -   -  2356  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.60 0.845 0.820   0x0  0x0   0  12.750
    22   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.10     -     -     -  0x0   -       -
    23   CPU0   -   -  2356  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.50 0.830 0.820   0x0  0x0   0  12.516
    23   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.01     -     -     -  0x0   -       -
    24   CPU0   -   -  2356  1400 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.27 0.847 0.805   0x0  0x0   0  12.797
    24   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.97     -     -     -  0x0   -       -
    25   CPU0   -   -  2356  1500 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.56 0.845 0.822   0x0  0x0   0  12.594
    25   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.91     -     -     -  0x0   -       -
    26   CPU0   -   -  2356  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.57 0.830 0.822   0x0  0x0   0  12.359
    26   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.90     -     -     -  0x0   -       -
    27   CPU0   -   -  2356  1500 100.00 3.14 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.42 0.830 0.822   0x0  0x0   0  12.297
    27   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.02     -     -     -  0x0   -       -
    28   CPU0   -   -  2356  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.59 0.847 0.822   0x0  0x0   0  12.453
    28   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.88     -     -     -  0x0   -       -
    29   CPU0   -   -  2355  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.35 0.845 0.820   0x0  0x0   0  12.500
    29   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.97     -     -     -  0x0   -       -
    30   CPU0   -   -  2356  1500 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.45 0.845 0.822   0x0  0x0   0  12.562
    30   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.79     -     -     -  0x0   -       -
    31   CPU0   -   -  2356  1400 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.46 0.830 0.805   0x0  0x0   0  12.672
    31   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.80     -     -     -  0x0   -       -
    32   CPU0   -   -  2356  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.52 0.845 0.820   0x0  0x0   0  12.797
    32   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.01     -     -     -  0x0   -       -
    33   CPU0   -   -  2356  1500 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.30 0.830 0.822   0x0  0x0   0  12.641
    33   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.91     -     -     -  0x0   -       -
    34   CPU0   -   -  2356  1500 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.46 0.847 0.820   0x0  0x0   0  12.453
    34   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.82     -     -     -  0x0   -       -
    35   CPU0   -   -  2356  1400 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.68 0.845 0.805   0x0  0x0   0  12.547
    35   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.75     -     -     -  0x0   -       -
    36   CPU0   -   -  2356  1500 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.46 0.845 0.822   0x0  0x0   0  12.688
    36   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.85     -     -     -  0x0   -       -
    37   CPU0   -   -  2356  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.50 0.830 0.820   0x0  0x0   0  12.828
    37   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.99     -     -     -  0x0   -       -
    38   CPU0   -   -  2356  1400 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.46 0.830 0.805   0x0  0x0   0  12.766
    38   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.65     -     -     -  0x0   -       -
    39   CPU0   -   -  2356  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.48 0.847 0.820   0x0  0x0   0  12.812
    39   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.92     -     -     -  0x0   -       -
    40   CPU0   -   -  2356  1400 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.35 0.847 0.805   0x0  0x0   0  12.656
    40   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.96     -     -     -  0x0   -       -
    41   CPU0   -   -  2356  1400 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.48 0.845 0.805   0x0  0x0   0  12.688
    41   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.75     -     -     -  0x0   -       -
    42   CPU0   -   -  2356  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.55 0.845 0.822   0x0  0x0   0  12.781
    42   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.81     -     -     -  0x0   -       -
    43   CPU0   -   -  2355  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.53 0.830 0.820   0x0  0x0   0  12.688
    43   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.77     -     -     -  0x0   -       -
    44   CPU0   -   -  2356  1400 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.44 0.845 0.805   0x0  0x0   0  12.688
    44   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.77     -     -     -  0x0   -       -
    45   CPU0   -   -  2356  1500 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.44 0.845 0.820   0x0  0x0   0  12.656
    45   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.78     -     -     -  0x0   -       -
    46   CPU0   -   -  2356  1400 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.47 0.845 0.805   0x0  0x0   0  12.750
    46   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.86     -     -     -  0x0   -       -
    47   CPU0   -   -  2356  1500 100.00 3.14 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.38 0.847 0.820   0x0  0x0   0  12.797
    47   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.07     -     -     -  0x0   -       -
    48   CPU0   -   -  2356  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.51 0.845 0.820   0x0  0x0   0  12.703
    48   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.89     -     -     -  0x0   -       -
    49   CPU0   -   -  2356  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.52 0.845 0.805   0x0  0x0   0  12.516
    49   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.03     -     -     -  0x0   -       -
    50   CPU0   -   -  2356  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.23 0.845 0.820   0x0  0x0   0  12.688
    50   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.89     -     -     -  0x0   -       -
    51   CPU0   -   -  2356  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.68 0.830 0.820   0x0  0x0   0  12.609
    51   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.96     -     -     -  0x0   -       -
    52   CPU0   -   -  2356  1400 100.00 3.14 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.54 0.845 0.805   0x0  0x0   0  12.875
    52   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.09     -     -     -  0x0   -       -
    53   CPU0   -   -  2356  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.40 0.830 0.820   0x0  0x0   0  12.781
    53   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.86     -     -     -  0x0   -       -
    54   CPU0   -   -  2356  1400 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.17 0.847 0.805   0x0  0x0   0  12.766
    54   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.87     -     -     -  0x0   -       -
    55   CPU0   -   -  2356  1400 100.00 3.14 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.84 0.830 0.805   0x0  0x0   0  12.719
    55   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.05     -     -     -  0x0   -       -
    56   CPU0   -   -  2356  1400 100.00 3.13 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.30 0.845 0.805   0x0  0x0   0  12.750
    56   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.01     -     -     -  0x0   -       -
    57   CPU0   -   -  2356  1500 100.00 3.13 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.63 0.845 0.820   0x0  0x0   0  12.797
    57   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.11     -     -     -  0x0   -       -
    58   CPU0   -   -  2355  1400 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.42 0.847 0.822   0x0  0x0   0  12.656
    58   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.01     -     -     -  0x0   -       -
    59   CPU0   -   -  2356  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.49 0.845 0.805   0x0  0x0   0  12.547
    59   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.02     -     -     -  0x0   -       -
    60   CPU0   -   -  2356  1500 100.00 3.14 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.45 0.830 0.820   0x0  0x0   0  12.625
    60   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.10     -     -     -  0x0   -       -
    61   CPU0   -   -  2356  1400 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 182.42 0.830 0.805   0x0  0x0   0  12.734
    61   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.99     -     -     -  0x0   -       -
    62   CPU0   -   -  2356  1500 100.00 3.13 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 186.42 0.830 0.820   0x0  0x0   0  12.641
    62   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.06     -     -     -  0x0   -       -
    63   CPU0   -   -  2356  1400 100.00 3.13 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.64 0.847 0.805   0x0  0x0   0  12.656
    63   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.04     -     -     -  0x0   -       -
    64   CPU0   -   -  2358  1500 100.00 3.14 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.40 0.845 0.822   0x0  0x0   0  12.641
    64   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.83     -     -     -  0x0   -       -
    65   CPU0   -   -  2356  1500 100.00 3.13 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.43 0.830 0.820   0x0  0x0   0  12.672
    65   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.91     -     -     -  0x0   -       -
    66   CPU0   -   -  2356  1500 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.52 0.845 0.822   0x0  0x0   0  12.547
    66   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.75     -     -     -  0x0   -       -
    67   CPU0   -   -  2356  1500 100.00 3.14 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.49 0.847 0.822   0x0  0x0   0  12.609
    67   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.03     -     -     -  0x0   -       -
    68   CPU0   -   -  2356  1500 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.34 0.830 0.820   0x0  0x0   0  12.578
    68   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.74     -     -     -  0x0   -       -
    69   CPU0   -   -  2356  1400 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.36 0.830 0.805   0x0  0x0   0  12.672
    69   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.69     -     -     -  0x0   -       -
    70   CPU0   -   -  2357  1400 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.73 0.830 0.805   0x0  0x0   0  12.578
    70   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.62     -     -     -  0x0   -       -
    71   CPU0   -   -  2356  1400 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.51 0.830 0.805   0x0  0x0   0  12.500
    71   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.76     -     -     -  0x0   -       -
    72   CPU0   -   -  2356  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.32 0.845 0.822   0x0  0x0   0  12.312
    72   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.79     -     -     -  0x0   -       -
    73   CPU0   -   -  2356  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.46 0.845 0.820   0x0  0x0   0  12.562
    73   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.78     -     -     -  0x0   -       -
    74   CPU0   -   -  2356  1500 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.47 0.845 0.822   0x0  0x0   0  12.531
    74   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.76     -     -     -  0x0   -       -
    75   CPU0   -   -  2356  1500 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.39 0.830 0.820   0x0  0x0   0  12.266
    75   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.72     -     -     -  0x0   -       -
    76   CPU0   -   -  2356  1400 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.63 0.845 0.805   0x0  0x0   0  12.516
    76   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.69     -     -     -  0x0   -       -
    77   CPU0   -   -  2356  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.36 0.845 0.820   0x0  0x0   0  12.734
    77   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.83     -     -     -  0x0   -       -
    78   CPU0   -   -  2357  1500 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.64 0.845 0.820   0x0  0x0   0  12.703
    78   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.60     -     -     -  0x0   -       -
    79   CPU0   -   -  2356  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.45 0.845 0.822   0x0  0x0   0  12.734
    79   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.92     -     -     -  0x0   -       -
    80   CPU0   -   -  2356  1400 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.42 0.830 0.820   0x0  0x0   0  12.672
    80   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.89     -     -     -  0x0   -       -
    81   CPU0   -   -  2356  1400 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.52 0.830 0.805   0x0  0x0   0  12.641
    81   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.90     -     -     -  0x0   -       -
    82   CPU0   -   -  2356  1400 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.43 0.845 0.805   0x0  0x0   0  12.516
    82   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.88     -     -     -  0x0   -       -
    83   CPU0   -   -  2356  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.34 0.830 0.822   0x0  0x0   0  12.578
    83   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.98     -     -     -  0x0   -       -
    84   CPU0   -   -  2356  1500 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.48 0.862 0.820   0x0  0x0   0  12.484
    84   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.78     -     -     -  0x0   -       -
    85   CPU0   -   -  2356  1400 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.61 0.830 0.805   0x0  0x0   0  12.625
    85   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.69     -     -     -  0x0   -       -
    86   CPU0   -   -  2355  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.38 0.845 0.822   0x0  0x0   0  12.469
    86   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.86     -     -     -  0x0   -       -
    87   CPU0   -   -  2355  1400 100.00 3.14 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.52 0.845 0.805   0x0  0x0   0  12.281
    87   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.08     -     -     -  0x0   -       -
    88   CPU0   -   -  2355  1400 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.40 0.845 0.805   0x0  0x0   0  12.297
    88   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.72     -     -     -  0x0   -       -
    89   CPU0   -   -  2355  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.51 0.845 0.820   0x0  0x0   0  12.172
    89   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.80     -     -     -  0x0   -       -
    90   CPU0   -   -  2355  1500 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.51 0.845 0.820   0x0  0x0   0  12.203
    90   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.56     -     -     -  0x0   -       -
    91   CPU0   -   -  2355  1500 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.54 0.845 0.820   0x0  0x0   0  12.438
    91   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.68     -     -     -  0x0   -       -
    92   CPU0   -   -  2356  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.28 0.845 0.820   0x0  0x0   0  12.484
    92   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.81     -     -     -  0x0   -       -
    93   CPU0   -   -  2356  1400 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.42 0.847 0.805   0x0  0x0   0  12.344
    93   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.75     -     -     -  0x0   -       -
    94   CPU0   -   -  2356  1500 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.56 0.847 0.822   0x0  0x0   0  12.328
    94   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.67     -     -     -  0x0   -       -
    95   CPU0   -   -  2356  1400 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.57 0.847 0.805   0x0  0x0   0  12.547
    95   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.85     -     -     -  0x0   -       -
    96   CPU0   -   -  2356  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.40 0.847 0.820   0x0  0x0   0  12.484
    96   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.86     -     -     -  0x0   -       -
    97   CPU0   -   -  2355  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.42 0.847 0.820   0x0  0x0   0  12.422
    97   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.98     -     -     -  0x0   -       -
    98   CPU0   -   -  2356  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.51 0.847 0.822   0x0  0x0   0  12.156
    98   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.91     -     -     -  0x0   -       -
    99   CPU0   -   -  2356  1400 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.57 0.847 0.805   0x0  0x0   0  12.266
    99   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.91     -     -     -  0x0   -       -
   100   CPU0   -   -  2356  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.38 0.847 0.822   0x0  0x0   0  12.359
   100   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.85     -     -     -  0x0   -       -
   101   CPU0   -   -  2356  1500 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.54 0.830 0.820   0x0  0x0   0  12.234
   101   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.82     -     -     -  0x0   -       -
   102   CPU0   -   -  2355  1400 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.41 0.847 0.805   0x0  0x0   0  12.266
   102   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.82     -     -     -  0x0   -       -
   103   CPU0   -   -  2355  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.47 0.830 0.822   0x0  0x0   0  12.219
   103   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.79     -     -     -  0x0   -       -
   104   CPU0   -   -  2356  1500 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.41 0.830 0.820   0x0  0x0   0  12.281
   104   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.66     -     -     -  0x0   -       -
   105   CPU0   -   -  2356  1400 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.52 0.847 0.805   0x0  0x0   0  12.375
   105   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.75     -     -     -  0x0   -       -
   106   CPU0   -   -  2355  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.45 0.830 0.820   0x0  0x0   0  12.656
   106   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.77     -     -     -  0x0   -       -
   107   CPU0   -   -  2355  1500 100.00 3.14 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.57 0.847 0.820   0x0  0x0   0  12.469
   107   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.91     -     -     -  0x0   -       -
   108   CPU0   -   -  2356  1500 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.47 0.845 0.820   0x0  0x0   0  12.516
   108   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.65     -     -     -  0x0   -       -
   109   CPU0   -   -  2355  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.44 0.847 0.820   0x0  0x0   0  12.484
   109   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.74     -     -     -  0x0   -       -
   110   CPU0   -   -  2356  1500 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.44 0.845 0.820   0x0  0x0   0  12.344
   110   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.68     -     -     -  0x0   -       -
   111   CPU0   -   -  2356  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.34 0.845 0.820   0x0  0x0   0  12.234
   111   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.78     -     -     -  0x0   -       -
   112   CPU0   -   -  2355  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.57 0.830 0.820   0x0  0x0   0  12.234
   112   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.83     -     -     -  0x0   -       -
   113   CPU0   -   -  2356  1500 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.52 0.847 0.822   0x0  0x0   0  12.266
   113   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.67     -     -     -  0x0   -       -
   114   CPU0   -   -  2355  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.45 0.830 0.820   0x0  0x0   0  12.484
   114   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.99     -     -     -  0x0   -       -
   115   CPU0   -   -  2356  1400 100.00 3.14 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 183.30 0.847 0.805   0x0  0x0   0  12.391
   115   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.02     -     -     -  0x0   -       -
   116   CPU0   -   -  2356  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 185.63 0.845 0.822   0x0  0x0   0  12.281
   116   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.88     -     -     -  0x0   -       -
   117   CPU0   -   -  2356  1400 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.52 0.847 0.805   0x0  0x0   0  12.562
   117   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.98     -     -     -  0x0   -       -
   118   CPU0   -   -  2356  1500 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.48 0.830 0.820   0x0  0x0   0  12.406
   118   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.77     -     -     -  0x0   -       -
   119   CPU0   -   -  2355  1400 100.00 3.14 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.38 0.845 0.805   0x0  0x0   0  12.375
   119   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.92     -     -     -  0x0   -       -
   120   CPU0   -   -  2356  1500 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.46 0.845 0.822   0x0  0x0   0  12.328
   120   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.72     -     -     -  0x0   -       -
   121   CPU0   -   -  2356  1400 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.57 0.845 0.805   0x0  0x0   0  12.438
   121   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.81     -     -     -  0x0   -       -
   122   CPU0   -   -  2357  1400 100.00 3.14 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.51 0.847 0.822   0x0  0x0   0  12.312
   122   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.02     -     -     -  0x0   -       -
   123   CPU0   -   -  2356  1400 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.45 0.830 0.805   0x0  0x0   0  12.406
   123   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.00     -     -     -  0x0   -       -
   124   CPU0   -   -  2356  1400 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.27 0.845 0.805   0x0  0x0   0  12.672
   124   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.93     -     -     -  0x0   -       -
   125   CPU0   -   -  2355  1400 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.60 0.830 0.805   0x0  0x0   0  12.719
   125   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.93     -     -     -  0x0   -       -
   126   CPU0   -   -  2356  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.43 0.830 0.822   0x0  0x0   0  12.531
   126   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.03     -     -     -  0x0   -       -
   127   CPU0   -   -  2355  1500 100.00 3.14 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.58 0.847 0.822   0x0  0x0   0  12.594
   127   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.17     -     -     -  0x0   -       -
   128   CPU0   -   -  2356  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.45 0.845 0.822   0x0  0x0   0  12.688
   128   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.06     -     -     -  0x0   -       -
   129   CPU0   -   -  2356  1500 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.28 0.830 0.805   0x0  0x0   0  12.875
   129   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.84     -     -     -  0x0   -       -
   130   CPU0   -   -  2356  1400 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.57 0.845 0.805   0x0  0x0   0  12.531
   130   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.87     -     -     -  0x0   -       -
   131   CPU0   -   -  2356  1500 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.55 0.830 0.820   0x0  0x0   0  12.562
   131   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.92     -     -     -  0x0   -       -
   132   CPU0   -   -  2356  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.39 0.845 0.820   0x0  0x0   0  12.547
   132   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.93     -     -     -  0x0   -       -
   133   CPU0   -   -  2355  1400 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.59 0.847 0.950   0x0  0x0   0  12.438
   133   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.97     -     -     -  0x0   -       -
   134   CPU0   -   -  2355  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.32 0.830 0.820   0x0  0x0   0  12.516
   134   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.05     -     -     -  0x0   -       -
   135   CPU0   -   -  2356  1400 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.48 0.845 0.805   0x0  0x0   0  12.547
   135   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.09     -     -     -  0x0   -       -
   136   CPU0   -   -  2356  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.56 0.847 0.820   0x0  0x0   0  12.703
   136   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.04     -     -     -  0x0   -       -
   137   CPU0   -   -  2355  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.42 0.830 0.820   0x0  0x0   0  12.406
   137   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.04     -     -     -  0x0   -       -
   138   CPU0   -   -  2356  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 182.32 0.847 0.820   0x0  0x0   0  12.406
   138   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.15     -     -     -  0x0   -       -
   139   CPU0   -   -  2356  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 186.64 0.830 0.805   0x0  0x0   0  12.234
   139   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.03     -     -     -  0x0   -       -
   140   CPU0   -   -  2356  1500 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.42 0.830 0.820   0x0  0x0   0  12.281
   140   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.96     -     -     -  0x0   -       -
   141   CPU0   -   -  2355  1400 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.55 0.845 0.805   0x0  0x0   0  12.281
   141   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.89     -     -     -  0x0   -       -
   142   CPU0   -   -  2356  1500 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.51 0.845 0.820   0x0  0x0   0  12.344
   142   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.94     -     -     -  0x0   -       -
   143   CPU0   -   -  2355  1400 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.37 0.830 0.805   0x0  0x0   0  12.344
   143   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.95     -     -     -  0x0   -       -
   144   CPU0   -   -  2356  1500 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.50 0.830 0.820   0x0  0x0   0  12.375
   144   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.89     -     -     -  0x0   -       -
   145   CPU0   -   -  2356  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.34 0.845 0.820   0x0  0x0   0  12.203
   145   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.94     -     -     -  0x0   -       -
   146   CPU0   -   -  2357  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.48 0.845 0.820   0x0  0x0   0  12.266
   146   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.91     -     -     -  0x0   -       -
   147   CPU0   -   -  2356  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.56 0.845 0.822   0x0  0x0   0  12.281
   147   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.06     -     -     -  0x0   -       -
   148   CPU0   -   -  2356  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.54 0.847 0.820   0x0  0x0   0  12.188
   148   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.04     -     -     -  0x0   -       -
   149   CPU0   -   -  2356  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.51 0.830 0.820   0x0  0x0   0  12.234
   149   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.01     -     -     -  0x0   -       -
   150   CPU0   -   -  2356  1500 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.44 0.845 0.820   0x0  0x0   0  12.172
   150   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.97     -     -     -  0x0   -       -
   151   CPU0   -   -  2355  1400 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.46 0.845 0.805   0x0  0x0   0  12.141
   151   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.07     -     -     -  0x0   -       -
   152   CPU0   -   -  2355  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.35 0.845 0.820   0x0  0x0   0  12.250
   152   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.11     -     -     -  0x0   -       -
   153   CPU0   -   -  2355  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.63 0.830 0.820   0x0  0x0   0  11.953
   153   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.04     -     -     -  0x0   -       -
   154   CPU0   -   -  2356  1500 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.36 0.845 0.820   0x0  0x0   0  12.094
   154   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.98     -     -     -  0x0   -       -
   155   CPU0   -   -  2356  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.59 0.830 0.822   0x0  0x0   0  12.141
   155   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.95     -     -     -  0x0   -       -
   156   CPU0   -   -  2356  1500 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.40 0.845 0.820   0x0  0x0   0  12.031
   156   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.95     -     -     -  0x0   -       -
   157   CPU0   -   -  2355  1500 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.49 0.845 0.822   0x0  0x0   0  12.125
   157   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.98     -     -     -  0x0   -       -
   158   CPU0   -   -  2355  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.53 0.847 0.820   0x0  0x0   0  12.109
   158   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.08     -     -     -  0x0   -       -
   159   CPU0   -   -  2356  1400 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.31 0.845 0.805   0x0  0x0   0  12.188
   159   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.94     -     -     -  0x0   -       -
   160   CPU0   -   -  2356  1400 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.37 0.845 0.802   0x0  0x0   0  12.203
   160   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.95     -     -     -  0x0   -       -
   161   CPU0   -   -  2356  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.70 0.845 0.820   0x0  0x0   0  12.141
   161   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.96     -     -     -  0x0   -       -
   162   CPU0   -   -  2356  1500 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.38 0.845 0.820   0x0  0x0   0  12.250
   162   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.88     -     -     -  0x0   -       -
   163   CPU0   -   -  2355  1500 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.51 0.845 0.820   0x0  0x0   0  12.344
   163   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.94     -     -     -  0x0   -       -
   164   CPU0   -   -  2356  1400 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.34 0.830 0.805   0x0  0x0   0  12.141
   164   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.98     -     -     -  0x0   -       -
   165   CPU0   -   -  2356  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.55 0.845 0.820   0x0  0x0   0  12.266
   165   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.93     -     -     -  0x0   -       -
   166   CPU0   -   -  2356  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.54 0.845 0.820   0x0  0x0   0  12.500
   166   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.92     -     -     -  0x0   -       -
   167   CPU0   -   -  2356  1400 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.39 0.830 0.805   0x0  0x0   0  12.453
   167   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.97     -     -     -  0x0   -       -
   168   CPU0   -   -  2356  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.55 0.830 0.805   0x0  0x0   0  12.469
   168   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.96     -     -     -  0x0   -       -
   169   CPU0   -   -  2356  1400 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.51 0.830 0.805   0x0  0x0   0  12.266
   169   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.87     -     -     -  0x0   -       -
   170   CPU0   -   -  2356  1500 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.37 0.847 0.820   0x0  0x0   0  12.359
   170   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.94     -     -     -  0x0   -       -
   171   CPU0   -   -  2356  1400 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.47 0.845 0.805   0x0  0x0   0  12.516
   171   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.04     -     -     -  0x0   -       -
   172   CPU0   -   -  2355  1400 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  22 184.36 0.845 0.805   0x0  0x0   0  12.453
   172   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.15     -     -     -  0x0   -       -
   173   CPU0   -   -  2356  1500 100.00 3.14 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.51 0.847 0.820   0x0  0x0   0  12.422
   173   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.23     -     -     -  0x0   -       -
   174   CPU0   -   -  2355  1500 100.00 3.14 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.57 0.845 0.822   0x0  0x0   0  12.375
   174   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.13     -     -     -  0x0   -       -
   175   CPU0   -   -  2355  1400 100.00 3.13 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.50 0.845 0.805   0x0  0x0   0  12.172
   175   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.17     -     -     -  0x0   -       -
   176   CPU0   -   -  2356  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.49 0.830 0.820   0x0  0x0   0  12.125
   176   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.13     -     -     -  0x0   -       -
   177   CPU0   -   -  2356  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.37 0.845 0.820   0x0  0x0   0  12.406
   177   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.07     -     -     -  0x0   -       -
   178   CPU0   -   -  2355  1400 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.53 0.845 0.805   0x0  0x0   0  12.328
   178   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.02     -     -     -  0x0   -       -
   179   CPU0   -   -  2355  1400 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.44 0.830 0.805   0x0  0x0   0  12.266
   179   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.96     -     -     -  0x0   -       -
   180   CPU0   -   -  2356  1500 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.46 0.845 0.820   0x0  0x0   0  12.266
   180   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.89     -     -     -  0x0   -       -
   181   CPU0   -   -  2356  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.51 0.830 0.820   0x0  0x0   0  12.219
   181   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.99     -     -     -  0x0   -       -
   182   CPU0   -   -  2355  1400 100.00 3.13 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.51 0.847 0.805   0x0  0x0   0  12.328
   182   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.07     -     -     -  0x0   -       -
   183   CPU0   -   -  2355  1500 100.00 3.14 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 180.52 0.845 0.820   0x0  0x0   0  12.297
   183   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.99     -     -     -  0x0   -       -
   184   CPU0   -   -  2355  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 188.51 0.847 0.820   0x0  0x0   0  12.297
   184   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.92     -     -     -  0x0   -       -
   185   CPU0   -   -  2355  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.34 0.845 0.820   0x0  0x0   0  12.234
   185   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.95     -     -     -  0x0   -       -
   186   CPU0   -   -  2356  1400 100.00 3.14 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.58 0.845 0.805   0x0  0x0   0  12.547
   186   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.98     -     -     -  0x0   -       -
   187   CPU0   -   -  2356  1400 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.38 0.845 0.805   0x0  0x0   0  12.312
   187   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.97     -     -     -  0x0   -       -
   188   CPU0   -   -  2355  1500 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.44 0.845 0.820   0x0  0x0   0  12.219
   188   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.84     -     -     -  0x0   -       -
   189   CPU0   -   -  2356  1400 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.51 0.830 0.805   0x0  0x0   0  12.344
   189   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.69     -     -     -  0x0   -       -
   190   CPU0   -   -  2356  1500 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.61 0.830 0.820   0x0  0x0   0  12.281
   190   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.76     -     -     -  0x0   -       -
   191   CPU0   -   -  2356  1400 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.32 0.830 0.805   0x0  0x0   0  12.469
   191   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.79     -     -     -  0x0   -       -
   192   CPU0   -   -  2356  1400 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.54 0.847 0.805   0x0  0x0   0  12.406
   192   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.79     -     -     -  0x0   -       -
   193   CPU0   -   -  2355  1400 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.49 0.830 0.805   0x0  0x0   0  12.438
   193   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.91     -     -     -  0x0   -       -
   194   CPU0   -   -  2355  1500 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.35 0.830 0.822   0x0  0x0   0  12.438
   194   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.87     -     -     -  0x0   -       -
   195   CPU0   -   -  2355  1500 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.41 0.830 0.822   0x0  0x0   0  12.531
   195   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.89     -     -     -  0x0   -       -
   196   CPU0   -   -  2356  1400 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.71 0.845 0.805   0x0  0x0   0  12.406
   196   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.79     -     -     -  0x0   -       -
   197   CPU0   -   -  2356  1400 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.41 0.845 0.805   0x0  0x0   0  12.219
   197   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.79     -     -     -  0x0   -       -
   198   CPU0   -   -  2355  1500 100.00 3.14 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.46 0.845 0.820   0x0  0x0   0  12.375
   198   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.09     -     -     -  0x0   -       -
   199   CPU0   -   -  2355  1500 100.00 3.15 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.47 0.845 0.820   0x0  0x0   0  12.328
   199   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.92     -     -     -  0x0   -       -
   200   CPU0   -   -  2356  1400 100.00 3.16 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.30 0.845 0.805   0x0  0x0   0  12.297
```

## check the sensors again, to see the reaction to raised thermals

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ sudo ipmitool sensor | grep -e CPU_0_TEMP -e CPU0_Power -e SYS_FAN_1A -e CPU_CUPS
Password:
XXXXXX       | 75.000     | degrees C  | ok    | na        | na        | na        | 96.000    | 98.000    | na
CPU0_Power       | 184.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 6000.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1A_PWM   | 22.000     | percent    | ok    | na        | na        | na        | na        | na        | na
CPU_CUPS         | 3.000      | percent    | ok    | na        | na        | na        | na        | 100.000   | na
[XXXXXX@controller-0 ~(keystone_admin)]$
```

## Success as we have observed thermals rising, along with fans increase in RPMs...  on to next test

## Performance Test #2 
## Run Core IA/SSE with 100% power, and Turbo on
## ./ptu -ct 3 -cp 100 -b 1

## Sensors before run

```log
controller-0:~# sudo ipmitool sensor | grep -e CPU_0_TEMP -e CPU0_Power -e SYS_FAN_1A -e CPU_CUPS
CPU_0_TEMP       | 56.000     | degrees C  | ok    | na        | na        | na        | 96.000    | 98.000    | na
CPU0_Power       | 94.000     | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 5000.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1A_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
CPU_CUPS         | 3.000      | percent    | ok    | na        | na        | na        | na        | 100.000   | na
controller-0:~# sudo ipmitool sensor
CPU_0_PROCHOT    | 0x0        | discrete   | 0x0080| na        | na        | na        | na        | na        | na
CPU_0_STATUS     | 0x0        | discrete   | 0x8080| na        | na        | na        | na        | na        | na
CPU_0_Vcore      | 1.822      | Volts      | ok    | na        | 1.690     | na        | na        | 1.870     | na
CPU0DDR_ABC_1.2V | 1.231      | Volts      | ok    | na        | 1.134     | na        | na        | 1.256     | na
CPU0DDR_DEF_1.2V | 1.231      | Volts      | ok    | na        | 1.134     | na        | na        | 1.256     | na
CPU_0_DTS_TEMP   | -43.000    | degrees C  | ok    | na        | na        | na        | na        | na        | na
CPU_0_TEMP       | 55.000     | degrees C  | ok    | na        | na        | na        | 96.000    | 98.000    | na
CPU_0_MARGIN     | 31.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
CPU0_Power       | 94.000     | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_PCH_TEMP     | 34.000     | degrees C  | ok    | na        | 5.000     | na        | na        | 82.000    | na
CPU_0_DIMM_C0    | 39.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_D0    | 37.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_A0    | 36.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_B0    | 36.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_G0    | 38.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_H0    | 37.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_E0    | 37.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_F0    | 36.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
MAX_DIMM_TEMP    | 39.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
INLET_TEMP_L     | 25.000     | degrees C  | ok    | na        | -6.000    | na        | 50.000    | 59.000    | 61.000
INLET_TEMP_R     | 24.000     | degrees C  | ok    | na        | -6.000    | na        | 50.000    | 59.000    | 61.000
INLET_TEMP_MAX   | 25.000     | degrees C  | ok    | na        | -6.000    | na        | 50.000    | 59.000    | 61.000
OUTLET_TEMP_L    | 45.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
OUTLET_TEMP_R    | 41.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
OUTLET_TEMP_MAX  | 45.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 5000.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1B       | 5500.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_2A       | 5000.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_2B       | 5500.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1A_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1B_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_2A_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_2B_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_V1.05        | 1.052      | Volts      | ok    | na        | 0.993     | na        | na        | 1.097     | na
SYS_V12          | 12.157     | Volts      | ok    | na        | 11.348    | na        | na        | 12.552    | na
SYS_V3.3         | 3.324      | Volts      | ok    | na        | 3.104     | na        | na        | 3.431     | na
SYS_V5           | 5.053      | Volts      | ok    | na        | 4.725     | na        | na        | 5.225     | na
CPU_CUPS         | 3.000      | percent    | ok    | na        | na        | na        | na        | 100.000   | na
MB_HSC_TEMP      | 40.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 125.000   | na
DIMM_VREFGH_TEMP | 34.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 125.000   | na
DIMM_VRABCD_TEMP | 36.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 125.000   | na
RTC_Voltage      | 3.066      | Volts      | ok    | na        | 2.289     | na        | na        | 3.444     | na
MB_HSC_PIN       | 188.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
MB_HSC_PIN_AVG   | 280.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
MB_HSC_PEAK_PIN  | 440.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_1_STATUS     | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
PSU_2_STATUS     | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
PSU_1_FAN        | 3840.000   | RPM        | ok    | 800.000   | 1120.000  | na        | na        | na        | na
PSU_2_FAN        | 3840.000   | RPM        | ok    | 800.000   | 1120.000  | na        | na        | na        | na
PSU_1_TEMP_1     | 27.000     | degrees C  | ok    | na        | na        | na        | na        | 60.000    | 64.000
PSU_2_TEMP_1     | 27.000     | degrees C  | ok    | na        | na        | na        | na        | 60.000    | 64.000
PSU_1_TEMP_2     | 46.000     | degrees C  | ok    | na        | na        | na        | na        | 92.000    | 97.000
PSU_2_TEMP_2     | 46.000     | degrees C  | ok    | na        | na        | na        | na        | 92.000    | 97.000
PSU_POWER_IN     | 374.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_1_POWER_IN   | 192.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_2_POWER_IN   | 180.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_1_POWER_OUT  | 174.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_2_POWER_OUT  | 162.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_1_CURRENT_IN | 0.945      | Amps       | ok    | na        | na        | na        | na        | na        | na
PSU_2_CURRENT_IN | 0.882      | Amps       | ok    | na        | na        | na        | na        | na        | na
PSU1_CURRENT_OUT | 14.310     | Amps       | ok    | na        | na        | na        | na        | na        | na
PSU2_CURRENT_OUT | 13.250     | Amps       | ok    | na        | na        | na        | na        | na        | na
PWR_UNIT_REDUND  | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
PWR_UNIT_STATUS  | 0x0        | discrete   | 0x0080| na        | na        | na        | na        | na        | na
ACPI_STATE       | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
SSD_0_TEMP       | 33.000     | degrees C  | ok    | na        | 0.000     | na        | na        | 70.000    | 79.000
SSD_1_TEMP       | 35.000     | degrees C  | ok    | na        | 0.000     | na        | na        | 70.000    | 79.000
PML_WEST_TEMP    | 55.000     | degrees C  | ok    | na        | na        | na        | na        | 110.000   | 114.000
PML_LOCAL_TEMP   | 53.000     | degrees C  | ok    | na        | na        | na        | 80.000    | 85.000    | na
PML_VDD_TEMP     | 57.000     | degrees C  | ok    | na        | na        | na        | na        | 125.000   | na
PML_EAST_TEMP    | 55.000     | degrees C  | ok    | na        | na        | na        | na        | 110.000   | 114.000
SC_1_E810        | na         | degrees C  | na    | na        | 0.000     | 5.000     | 100.000   | 105.000   | 115.000
SC_2_E810        | 42.000     | degrees C  | ok    | na        | 0.000     | 5.000     | 100.000   | 105.000   | 115.000
controller-0:~# sudo ipmitool sensor | grep -e CPU_0_TEMP -e CPU0_Power -e SYS_FAN_1A -e CPU_CUPS
CPU_0_TEMP       | 55.000     | degrees C  | ok    | na        | na        | na        | 96.000    | 98.000    | na
CPU0_Power       | 95.000     | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 5000.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1A_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
CPU_CUPS         | 3.000      | percent    | ok    | na        | na        | na        | na        | 100.000   | na
controller-0:~#

```

## Initiate Load 

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ sudo ./ptu -ct 3 -cp 100 -b 1
Password:

XXXXXX ./ptu -ct 3 -cp 100 -b 1

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
Available System Memory:             78926 MB


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

[10/30/23 21:24:30 UTC] PTU started.

Press <Ctrl-C> to stop.


CPU_0: [IDLE] CFreq=2493, UFreq=1700, Util=0.60, IPC=0.87, Temp=53, DTS=45, Power=91.9, Volt=0.877, UVolt=0.870
CPU_0: [TESTCFG] TestSel=3 (Core IA/SSE), CoreMask=0xFFFFFFFFFFFFFFFF, ThreadMask=0xFF, PwrLevel=100, Turbo=1
CPU_0: [RUNNING] CFreq=2285, UFreq=1400, Util=100.00, IPC=3.90, Temp=66, DTS=32, Power=184.4, Volt=0.838, UVolt=0.815


```

## ptu -mon

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ sudo ./ptu -mon
Password:

XXXXXX ./ptu -mon

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
Available System Memory:             78896 MB


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

[10/30/23 21:25:42 UTC] PTU started.

Press <Ctrl-C> to stop.


 Index Device Cor Thr CFreq UFreq   Util  IPC     C0     C1     C6    PC2    PC6 MC Ch Sl  Temp DTS  Power  Volt UVolt TStat TLog #TL TMargin
     0   CPU0   -   -  2278  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.50 0.830 0.805   0x0  0x0   0  13.922
     0   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   8.62     -     -     -  0x0   -       -
     1   CPU0   -   -  2278  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.57 0.830 0.805   0x0  0x0   0  14.062
     1   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   8.58     -     -     -  0x0   -       -
     2   CPU0   -   -  2278  1400 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.23 0.815 0.805   0x0  0x0   0  13.922
     2   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   8.79     -     -     -  0x0   -       -
     3   CPU0   -   -  2278  1400 100.00 3.91 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.63 0.830 0.805   0x0  0x0   0  13.781
     3   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   8.67     -     -     -  0x0   -       -
     4   CPU0   -   -  2278  1400 100.00 3.91 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.47 0.817 0.805   0x0  0x0   0  13.781
     4   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   8.68     -     -     -  0x0   -       -
     5   CPU0   -   -  2278  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.31 0.830 0.805   0x0  0x0   0  13.797
     5   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   8.80     -     -     -  0x0   -       -
     6   CPU0   -   -  2278  1400 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 182.27 0.832 0.805   0x0  0x0   0  13.859
     6   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   8.84     -     -     -  0x0   -       -
     7   CPU0   -   -  2278  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 186.90 0.830 0.805   0x0  0x0   0  13.688
     7   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   8.75     -     -     -  0x0   -       -
     8   CPU0   -   -  2278  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.47 0.830 0.805   0x0  0x0   0  13.547
     8   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   8.77     -     -     -  0x0   -       -
     9   CPU0   -   -  2277  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.48 0.832 0.805   0x0  0x0   0  13.609
     9   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   8.72     -     -     -  0x0   -       -
    10   CPU0   -   -  2277  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.37 0.832 0.805   0x0  0x0   0  13.688
    10   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   8.76     -     -     -  0x0   -       -
    11   CPU0   -   -  2278  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.42 0.832 0.805   0x0  0x0   0  13.703
    11   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   8.70     -     -     -  0x0   -       -
    12   CPU0   -   -  2278  1400 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.39 0.830 0.805   0x0  0x0   0  13.734
    12   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   8.94     -     -     -  0x0   -       -
    13   CPU0   -   -  2277  1400 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.45 0.830 0.805   0x0  0x0   0  13.547
    13   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   8.94     -     -     -  0x0   -       -
    14   CPU0   -   -  2278  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.65 0.830 0.805   0x0  0x0   0  13.641
    14   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   8.71     -     -     -  0x0   -       -
    15   CPU0   -   -  2278  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.46 0.830 0.805   0x0  0x0   0  13.594
    15   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   8.78     -     -     -  0x0   -       -
    16   CPU0   -   -  2278  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.46 0.830 0.805   0x0  0x0   0  13.406
    16   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   8.76     -     -     -  0x0   -       -
    17   CPU0   -   -  2278  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.52 0.830 0.805   0x0  0x0   0  13.391
    17   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   8.78     -     -     -  0x0   -       -
    18   CPU0   -   -  2277  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.41 0.815 0.805   0x0  0x0   0  13.453
    18   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   8.76     -     -     -  0x0   -       -
    19   CPU0   -   -  2278  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.33 0.830 0.805   0x0  0x0   0  13.625
    19   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   8.86     -     -     -  0x0   -       -
    20   CPU0   -   -  2278  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.68 0.815 0.805   0x0  0x0   0  13.516
    20   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   8.72     -     -     -  0x0   -       -
    21   CPU0   -   -  2277  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.54 0.815 0.805   0x0  0x0   0  13.375
    21   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   8.80     -     -     -  0x0   -       -
    22   CPU0   -   -  2278  1400 100.00 3.88 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.44 0.817 0.805   0x0  0x0   0  13.359
    22   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   8.95     -     -     -  0x0   -       -
    23   CPU0   -   -  2277  1400 100.00 3.88 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.36 0.832 0.805   0x0  0x0   0  13.406
    23   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   9.02     -     -     -  0x0   -       -
    24   CPU0   -   -  2278  1400 100.00 3.88 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.60 0.830 0.805   0x0  0x0   0  13.344
    24   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   8.84     -     -     -  0x0   -       -
    25   CPU0   -   -  2278  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    74  23 184.29 0.830 0.805   0x0  0x0   0  13.406
    25   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   8.70     -     -     -  0x0   -       -
    26   CPU0   -   -  2278  1400 100.00 3.91 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.58 0.832 0.805   0x0  0x0   0  13.422
    26   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   8.57     -     -     -  0x0   -       -
    27   CPU0   -   -  2278  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.52 0.830 0.805   0x0  0x0   0  13.438
    27   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   8.70     -     -     -  0x0   -       -
    28   CPU0   -   -  2278  1400 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 184.45 0.830 0.805   0x0  0x0   0  13.406
    28   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   8.86     -     -     -  0x0   -       -
    29   CPU0   -   -  2279  1400 100.00 3.88 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.44 0.830 0.805   0x0  0x0   0  13.516
    29   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   8.90     -     -     -  0x0   -       -
    30   CPU0   -   -  2277  1400 100.00 3.87 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 183.85 0.830 0.805   0x0  0x0   0  13.344
    30   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   9.04     -     -     -  0x0   -       -
    31   CPU0   -   -  2278  1400 100.00 3.88 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 185.01 0.832 0.805   0x0  0x0   0  13.406
    31   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   8.92     -     -     -  0x0   -       -
    32   CPU0   -   -  2278  1400 100.00 3.87 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 183.55 0.830 0.805   0x0  0x0   0  13.312
    32   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   8.87     -     -     -  0x0   -       -
    33   CPU0   -   -  2277  1400 100.00 3.88 100.00   0.00   0.00   0.00   0.00  -  -  -    74  24 185.47 0.830 0.805   0x0  0x0   0  13.359
    33   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.89     -     -     -  0x0   -       -
    34   CPU0   -   -  2277  1400 100.00 3.87 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.44 0.832 0.805   0x0  0x0   0  13.266
    34   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   9.02     -     -     -  0x0   -       -
    35   CPU0   -   -  2278  1400 100.00 3.88 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.56 0.830 0.805   0x0  0x0   0  13.328
    35   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   8.89     -     -     -  0x0   -       -
^C
[10/30/23 21:26:20 UTC] PTU stopped.

[XXXXXX@controller-0 ~(keystone_admin)]$
```


## Sensors after load ~2-3mins after

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ sudo ipmitool sensor | grep -e CPU_0_TEMP -e CPU0_Power -e SYS_FAN_1A -e CPU_CUPS
CPU_0_TEMP       | 75.000     | degrees C  | ok    | na        | na        | na        | 96.000    | 98.000    | na
CPU0_Power       | 184.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 6000.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1A_PWM   | 22.000     | percent    | ok    | na        | na        | na        | na        | na        | na
CPU_CUPS         | 3.000      | percent    | ok    | na        | na        | na        | na        | 100.000   | na
[XXXXXX@controller-0 ~(keystone_admin)]$ sudo ipmitool sensor
CPU_0_PROCHOT    | 0x0        | discrete   | 0x0080| na        | na        | na        | na        | na        | na
CPU_0_STATUS     | 0x0        | discrete   | 0x8080| na        | na        | na        | na        | na        | na
CPU_0_Vcore      | 1.811      | Volts      | ok    | na        | 1.690     | na        | na        | 1.870     | na
CPU0DDR_ABC_1.2V | 1.231      | Volts      | ok    | na        | 1.134     | na        | na        | 1.256     | na
CPU0DDR_DEF_1.2V | 1.231      | Volts      | ok    | na        | 1.134     | na        | na        | 1.256     | na
CPU_0_DTS_TEMP   | -23.000    | degrees C  | ok    | na        | na        | na        | na        | na        | na
CPU_0_TEMP       | 75.000     | degrees C  | ok    | na        | na        | na        | 96.000    | 98.000    | na
CPU_0_MARGIN     | 12.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
CPU0_Power       | 184.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_PCH_TEMP     | 34.000     | degrees C  | ok    | na        | 5.000     | na        | na        | 82.000    | na
CPU_0_DIMM_C0    | 39.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_D0    | 37.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_A0    | 35.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_B0    | 35.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_G0    | 38.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_H0    | 37.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_E0    | 36.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_F0    | 36.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
MAX_DIMM_TEMP    | 39.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
INLET_TEMP_L     | 25.000     | degrees C  | ok    | na        | -6.000    | na        | 50.000    | 59.000    | 61.000
INLET_TEMP_R     | 24.000     | degrees C  | ok    | na        | -6.000    | na        | 50.000    | 59.000    | 61.000
INLET_TEMP_MAX   | 25.000     | degrees C  | ok    | na        | -6.000    | na        | 50.000    | 59.000    | 61.000
OUTLET_TEMP_L    | 46.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
OUTLET_TEMP_R    | 41.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
OUTLET_TEMP_MAX  | 46.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 6000.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1B       | 6500.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_2A       | 6000.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_2B       | 6500.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1A_PWM   | 22.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1B_PWM   | 22.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_2A_PWM   | 22.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_2B_PWM   | 22.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_V1.05        | 1.052      | Volts      | ok    | na        | 0.993     | na        | na        | 1.097     | na
SYS_V12          | 12.119     | Volts      | ok    | na        | 11.348    | na        | na        | 12.552    | na
SYS_V3.3         | 3.329      | Volts      | ok    | na        | 3.104     | na        | na        | 3.431     | na
SYS_V5           | 5.053      | Volts      | ok    | na        | 4.725     | na        | na        | 5.225     | na
CPU_CUPS         | 3.000      | percent    | ok    | na        | na        | na        | na        | 100.000   | na
MB_HSC_TEMP      | 41.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 125.000   | na
DIMM_VREFGH_TEMP | 34.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 125.000   | na
DIMM_VRABCD_TEMP | 35.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 125.000   | na
RTC_Voltage      | 3.066      | Volts      | ok    | na        | 2.289     | na        | na        | 3.444     | na
MB_HSC_PIN       | 300.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
MB_HSC_PIN_AVG   | 272.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
MB_HSC_PEAK_PIN  | 440.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_1_STATUS     | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
PSU_2_STATUS     | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
PSU_1_FAN        | 3840.000   | RPM        | ok    | 800.000   | 1120.000  | na        | na        | na        | na
PSU_2_FAN        | 4000.000   | RPM        | ok    | 800.000   | 1120.000  | na        | na        | na        | na
PSU_1_TEMP_1     | 27.000     | degrees C  | ok    | na        | na        | na        | na        | 60.000    | 64.000
PSU_2_TEMP_1     | 27.000     | degrees C  | ok    | na        | na        | na        | na        | 60.000    | 64.000
PSU_1_TEMP_2     | 46.000     | degrees C  | ok    | na        | na        | na        | na        | 92.000    | 97.000
PSU_2_TEMP_2     | 46.000     | degrees C  | ok    | na        | na        | na        | na        | 92.000    | 97.000
PSU_POWER_IN     | 451.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_1_POWER_IN   | 234.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_2_POWER_IN   | 222.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_1_POWER_OUT  | 216.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_2_POWER_OUT  | 204.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_1_CURRENT_IN | 1.134      | Amps       | ok    | na        | na        | na        | na        | na        | na
PSU_2_CURRENT_IN | 1.071      | Amps       | ok    | na        | na        | na        | na        | na        | na
PSU1_CURRENT_OUT | 18.020     | Amps       | ok    | na        | na        | na        | na        | na        | na
PSU2_CURRENT_OUT | 16.960     | Amps       | ok    | na        | na        | na        | na        | na        | na
PWR_UNIT_REDUND  | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
PWR_UNIT_STATUS  | 0x0        | discrete   | 0x0080| na        | na        | na        | na        | na        | na
ACPI_STATE       | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
SSD_0_TEMP       | 33.000     | degrees C  | ok    | na        | 0.000     | na        | na        | 70.000    | 79.000
SSD_1_TEMP       | 35.000     | degrees C  | ok    | na        | 0.000     | na        | na        | 70.000    | 79.000
PML_WEST_TEMP    | 54.000     | degrees C  | ok    | na        | na        | na        | na        | 110.000   | 114.000
PML_LOCAL_TEMP   | 51.000     | degrees C  | ok    | na        | na        | na        | 80.000    | 85.000    | na
PML_VDD_TEMP     | 56.000     | degrees C  | ok    | na        | na        | na        | na        | 125.000   | na
PML_EAST_TEMP    | 54.000     | degrees C  | ok    | na        | na        | na        | na        | 110.000   | 114.000
SC_1_E810        | na         | degrees C  | na    | na        | 0.000     | 5.000     | 100.000   | 105.000   | 115.000
SC_2_E810        | 40.000     | degrees C  | ok    | na        | 0.000     | 5.000     | 100.000   | 105.000   | 115.000
[XXXXXX@controller-0 ~(keystone_admin)]$


```

## Test is success, observed temps rise and fan rpms rise with the load

## Performance test PTU 3 - Core AVX2 with Turbo - MEAKV-644
## Run Core Intel® AVX-2 with power level 100% and Turbo on.
## sudo ./ptu -ct 4 -cp 100 -b 1

## Check sensors bofore starting load

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ sudo ipmitool sensor | grep -e CPU_0_TEMP -e CPU0_Power -e SYS_FAN_1A -e CPU_CUPS
Password:
XXXXXX       | 53.000     | degrees C  | ok    | na        | na        | na        | 96.000    | 98.000    | na
CPU0_Power       | 91.000     | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 5125.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1A_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
CPU_CUPS         | 3.000      | percent    | ok    | na        | na        | na        | na        | 100.000   | na
[XXXXXX@controller-0 ~(keystone_admin)]$
[XXXXXX@controller-0 ~(keystone_admin)]$ sudo ipmitool sensor
CPU_0_PROCHOT    | 0x0        | discrete   | 0x0080| na        | na        | na        | na        | na        | na
CPU_0_STATUS     | 0x0        | discrete   | 0x8080| na        | na        | na        | na        | na        | na
CPU_0_Vcore      | 1.825      | Volts      | ok    | na        | 1.690     | na        | na        | 1.870     | na
CPU0DDR_ABC_1.2V | 1.231      | Volts      | ok    | na        | 1.134     | na        | na        | 1.256     | na
CPU0DDR_DEF_1.2V | 1.231      | Volts      | ok    | na        | 1.134     | na        | na        | 1.256     | na
CPU_0_DTS_TEMP   | -45.000    | degrees C  | ok    | na        | na        | na        | na        | na        | na
CPU_0_TEMP       | 53.000     | degrees C  | ok    | na        | na        | na        | 96.000    | 98.000    | na
CPU_0_MARGIN     | 34.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
CPU0_Power       | 93.000     | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_PCH_TEMP     | 34.000     | degrees C  | ok    | na        | 5.000     | na        | na        | 82.000    | na
CPU_0_DIMM_C0    | 38.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_D0    | 37.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_A0    | 35.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_B0    | 35.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_G0    | 37.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_H0    | 37.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_E0    | 36.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_F0    | 36.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
MAX_DIMM_TEMP    | 38.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
INLET_TEMP_L     | 26.000     | degrees C  | ok    | na        | -6.000    | na        | 50.000    | 59.000    | 61.000
INLET_TEMP_R     | 24.000     | degrees C  | ok    | na        | -6.000    | na        | 50.000    | 59.000    | 61.000
INLET_TEMP_MAX   | 26.000     | degrees C  | ok    | na        | -6.000    | na        | 50.000    | 59.000    | 61.000
OUTLET_TEMP_L    | 43.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
OUTLET_TEMP_R    | 39.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
OUTLET_TEMP_MAX  | 43.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 5000.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1B       | 5500.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_2A       | 5000.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_2B       | 5500.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1A_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1B_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_2A_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_2B_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_V1.05        | 1.053      | Volts      | ok    | na        | 0.993     | na        | na        | 1.097     | na
SYS_V12          | 12.157     | Volts      | ok    | na        | 11.348    | na        | na        | 12.552    | na
SYS_V3.3         | 3.324      | Volts      | ok    | na        | 3.104     | na        | na        | 3.431     | na
SYS_V5           | 5.053      | Volts      | ok    | na        | 4.725     | na        | na        | 5.225     | na
CPU_CUPS         | 3.000      | percent    | ok    | na        | na        | na        | na        | 100.000   | na
MB_HSC_TEMP      | 39.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 125.000   | na
DIMM_VREFGH_TEMP | 34.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 125.000   | na
DIMM_VRABCD_TEMP | 35.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 125.000   | na
RTC_Voltage      | 3.066      | Volts      | ok    | na        | 2.289     | na        | na        | 3.444     | na
MB_HSC_PIN       | 184.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
MB_HSC_PIN_AVG   | 252.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
MB_HSC_PEAK_PIN  | 440.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_1_STATUS     | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
PSU_2_STATUS     | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
PSU_1_FAN        | 3840.000   | RPM        | ok    | 800.000   | 1120.000  | na        | na        | na        | na
PSU_2_FAN        | 4000.000   | RPM        | ok    | 800.000   | 1120.000  | na        | na        | na        | na
PSU_1_TEMP_1     | 27.000     | degrees C  | ok    | na        | na        | na        | na        | 60.000    | 64.000
PSU_2_TEMP_1     | 27.000     | degrees C  | ok    | na        | na        | na        | na        | 60.000    | 64.000
PSU_1_TEMP_2     | 47.000     | degrees C  | ok    | na        | na        | na        | na        | 92.000    | 97.000
PSU_2_TEMP_2     | 46.000     | degrees C  | ok    | na        | na        | na        | na        | 92.000    | 97.000
PSU_POWER_IN     | 374.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_1_POWER_IN   | 192.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_2_POWER_IN   | 180.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_1_POWER_OUT  | 174.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_2_POWER_OUT  | 162.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_1_CURRENT_IN | 0.945      | Amps       | ok    | na        | na        | na        | na        | na        | na
PSU_2_CURRENT_IN | 0.882      | Amps       | ok    | na        | na        | na        | na        | na        | na
PSU1_CURRENT_OUT | 14.840     | Amps       | ok    | na        | na        | na        | na        | na        | na
PSU2_CURRENT_OUT | 13.250     | Amps       | ok    | na        | na        | na        | na        | na        | na
PWR_UNIT_REDUND  | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
PWR_UNIT_STATUS  | 0x0        | discrete   | 0x0080| na        | na        | na        | na        | na        | na
ACPI_STATE       | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
SSD_0_TEMP       | 33.000     | degrees C  | ok    | na        | 0.000     | na        | na        | 70.000    | 79.000
SSD_1_TEMP       | 35.000     | degrees C  | ok    | na        | 0.000     | na        | na        | 70.000    | 79.000
PML_WEST_TEMP    | 56.000     | degrees C  | ok    | na        | na        | na        | na        | 110.000   | 114.000
PML_LOCAL_TEMP   | 53.000     | degrees C  | ok    | na        | na        | na        | 80.000    | 85.000    | na
PML_VDD_TEMP     | 57.000     | degrees C  | ok    | na        | na        | na        | na        | 125.000   | na
PML_EAST_TEMP    | 55.000     | degrees C  | ok    | na        | na        | na        | na        | 110.000   | 114.000
SC_1_E810        | na         | degrees C  | na    | na        | 0.000     | 5.000     | 100.000   | 105.000   | 115.000
SC_2_E810        | 42.000     | degrees C  | ok    | na        | 0.000     | 5.000     | 100.000   | 105.000   | 115.000
[XXXXXX@controller-0 ~(keystone_admin)]$
```

## load Intiated

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ sudo ./ptu -ct 4 -cp 100 -b 1
Password:

XXXXXX ./ptu -ct 4 -cp 100 -b 1

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
Available System Memory:             78858 MB


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

[10/30/23 21:37:20 UTC] PTU started.

Press <Ctrl-C> to stop.


CPU_0: [IDLE] CFreq=2492, UFreq=1700, Util=0.71, IPC=0.89, Temp=53, DTS=45, Power=92.0, Volt=0.877, UVolt=0.870
CPU_0: [TESTCFG] TestSel=4 (Core AVX2), CoreMask=0xFFFFFFFFFFFFFFFF, ThreadMask=0xFF, PwrLevel=100, Turbo=1
CPU_0: [RUNNING] CFreq=2131, UFreq=1300, Util=100.00, IPC=3.89, Temp=65, DTS=33, Power=184.6, Volt=0.809, UVolt=0.940

```

## ptu -mon

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ sudo ./ptu -mon

Command: ./ptu -mon

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
Available System Memory:             78677 MB


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

[10/30/23 21:43:18 UTC] PTU started.

Press <Ctrl-C> to stop.


 Index Device Cor Thr CFreq UFreq   Util  IPC     C0     C1     C6    PC2    PC6 MC Ch Sl  Temp DTS  Power  Volt UVolt TStat TLog #TL TMargin
     0   CPU0   -   -  2132  1300 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.53 0.797 0.792   0x0  0x0   0  12.203
     0   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.81     -     -     -  0x0   -       -
     1   CPU0   -   -  2130  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.55 0.797 0.805   0x0  0x0   0  12.391
     1   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.91     -     -     -  0x0   -       -
     2   CPU0   -   -  2129  1300 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.39 0.797 0.792   0x0  0x0   0  12.359
     2   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.89     -     -     -  0x0   -       -
     3   CPU0   -   -  2131  1300 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.59 0.812 0.792   0x0  0x0   0  12.438
     3   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.94     -     -     -  0x0   -       -
     4   CPU0   -   -  2129  1300 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.46 0.812 0.792   0x0  0x0   0  12.281
     4   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.02     -     -     -  0x0   -       -
     5   CPU0   -   -  2130  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.34 0.812 0.805   0x0  0x0   0  12.391
     5   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.03     -     -     -  0x0   -       -
     6   CPU0   -   -  2131  1300 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.60 0.812 0.792   0x0  0x0   0  12.406
     6   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.07     -     -     -  0x0   -       -
     7   CPU0   -   -  2128  1300 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.36 0.797 0.792   0x0  0x0   0  12.250
     7   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.08     -     -     -  0x0   -       -
     8   CPU0   -   -  2130  1300 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.44 0.797 0.792   0x0  0x0   0  12.266
     8   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.94     -     -     -  0x0   -       -
     9   CPU0   -   -  2130  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.40 0.815 0.805   0x0  0x0   0  12.422
     9   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.09     -     -     -  0x0   -       -
    10   CPU0   -   -  2130  1300 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.59 0.812 0.792   0x0  0x0   0  12.484
    10   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.06     -     -     -  0x0   -       -
    11   CPU0   -   -  2129  1300 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.56 0.797 0.792   0x0  0x0   0  12.406
    11   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.00     -     -     -  0x0   -       -
    12   CPU0   -   -  2130  1300 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.41 0.812 0.792   0x0  0x0   0  12.422
    12   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.95     -     -     -  0x0   -       -
    13   CPU0   -   -  2131  1300 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.48 0.800 0.792   0x0  0x0   0  12.359
    13   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.06     -     -     -  0x0   -       -
    14   CPU0   -   -  2130  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.40 0.812 0.805   0x0  0x0   0  12.422
    14   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.93     -     -     -  0x0   -       -
    15   CPU0   -   -  2130  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.42 0.797 0.805   0x0  0x0   0  12.453
    15   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.90     -     -     -  0x0   -       -
    16   CPU0   -   -  2131  1300 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.52 0.815 0.792   0x0  0x0   0  12.344
    16   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.95     -     -     -  0x0   -       -
    17   CPU0   -   -  2130  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.47 0.812 0.805   0x0  0x0   0  12.266
    17   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.86     -     -     -  0x0   -       -
    18   CPU0   -   -  2131  1300 100.00 3.88 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.50 0.815 0.792   0x0  0x0   0  12.422
    18   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.92     -     -     -  0x0   -       -
    19   CPU0   -   -  2131  1300 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.43 0.797 0.792   0x0  0x0   0  12.250
    19   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.06     -     -     -  0x0   -       -
    20   CPU0   -   -  2130  1300 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.53 0.797 0.792   0x0  0x0   0  12.312
    20   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.97     -     -     -  0x0   -       -
    21   CPU0   -   -  2130  1400 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.42 0.797 0.802   0x0  0x0   0  12.391
    21   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.00     -     -     -  0x0   -       -
    22   CPU0   -   -  2129  1400 100.00 3.91 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.46 0.797 0.805   0x0  0x0   0  12.391
    22   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.87     -     -     -  0x0   -       -
    23   CPU0   -   -  2131  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.52 0.812 0.802   0x0  0x0   0  12.328
    23   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.95     -     -     -  0x0   -       -
    24   CPU0   -   -  2129  1300 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.52 0.797 0.792   0x0  0x0   0  12.297
    24   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.06     -     -     -  0x0   -       -
    25   CPU0   -   -  2130  1400 100.00 3.88 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.28 0.812 0.805   0x0  0x0   0  12.406
    25   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.12     -     -     -  0x0   -       -
    26   CPU0   -   -  2131  1400 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.64 0.800 0.805   0x0  0x0   0  12.359
    26   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.07     -     -     -  0x0   -       -
    27   CPU0   -   -  2130  1300 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.45 0.797 0.792   0x0  0x0   0  12.359
    27   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.06     -     -     -  0x0   -       -
    28   CPU0   -   -  2130  1300 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.39 0.812 0.792   0x0  0x0   0  12.375
    28   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.03     -     -     -  0x0   -       -
    29   CPU0   -   -  2130  1300 100.00 3.88 100.00   0.00   0.00   0.00   0.00  -  -  -    75  22 184.58 0.800 0.792   0x0  0x0   0  12.375
    29   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.07     -     -     -  0x0   -       -
    30   CPU0   -   -  2131  1300 100.00 3.88 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.41 0.800 0.792   0x0  0x0   0  12.422
    30   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.04     -     -     -  0x0   -       -
    31   CPU0   -   -  2130  1300 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.40 0.797 0.792   0x0  0x0   0  12.375
    31   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.96     -     -     -  0x0   -       -
    32   CPU0   -   -  2130  1400 100.00 3.88 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.50 0.797 0.805   0x0  0x0   0  12.328
    32   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.10     -     -     -  0x0   -       -
    33   CPU0   -   -  2129  1400 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.50 0.797 0.802   0x0  0x0   0  12.203
    33   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.02     -     -     -  0x0   -       -
    34   CPU0   -   -  2130  1300 100.00 3.91 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.47 0.812 0.792   0x0  0x0   0  12.281
    34   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.88     -     -     -  0x0   -       -
    35   CPU0   -   -  2130  1300 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.47 0.797 0.790   0x0  0x0   0  12.188
    35   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.95     -     -     -  0x0   -       -
    36   CPU0   -   -  2130  1400 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.40 0.812 0.802   0x0  0x0   0  12.188
    36   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.01     -     -     -  0x0   -       -
    37   CPU0   -   -  2128  1300 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.51 0.800 0.792   0x0  0x0   0  12.328
    37   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.81     -     -     -  0x0   -       -
    38   CPU0   -   -  2130  1300 100.00 3.88 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.43 0.800 0.792   0x0  0x0   0  12.281
    38   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.01     -     -     -  0x0   -       -
    39   CPU0   -   -  2129  1300 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.39 0.797 0.790   0x0  0x0   0  12.359
    39   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.97     -     -     -  0x0   -       -
    40   CPU0   -   -  2129  1400 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.58 0.797 0.805   0x0  0x0   0  12.234
    40   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.93     -     -     -  0x0   -       -
    41   CPU0   -   -  2130  1300 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.46 0.797 0.792   0x0  0x0   0  12.344
    41   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.93     -     -     -  0x0   -       -
    42   CPU0   -   -  2130  1400 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.37 0.797 0.805   0x0  0x0   0  12.297
    42   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.99     -     -     -  0x0   -       -
    43   CPU0   -   -  2130  1400 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.60 0.797 0.805   0x0  0x0   0  12.422
    43   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.00     -     -     -  0x0   -       -
    44   CPU0   -   -  2130  1300 100.00 3.91 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.43 0.812 0.802   0x0  0x0   0  12.344
    44   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.00     -     -     -  0x0   -       -
    45   CPU0   -   -  2128  1400 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.29 0.797 0.805   0x0  0x0   0  12.344
    45   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.02     -     -     -  0x0   -       -
    46   CPU0   -   -  2129  1300 100.00 3.90 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.68 0.797 0.792   0x0  0x0   0  12.438
    46   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.10     -     -     -  0x0   -       -
    47   CPU0   -   -  2129  1300 100.00 3.89 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.50 0.797 0.792   0x0  0x0   0  12.375
    47   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.13     -     -     -  0x0   -       -
    48   CPU0   -   -  2131  1300 100.00 3.87 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.38 0.812 0.792   0x0  0x0   0  12.344
    48   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.10     -     -     -  0x0   -       -
^C
[10/30/23 21:44:11 UTC] PTU stopped.

[XXXXXX@controller-0 ~(keystone_admin)]$
```

## check sensors after load 

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ sudo ipmitool sensor | grep -e CPU_0_TEMP -e CPU0_Power -e SYS_FAN_1A -e CPU_CUPS
CPU_0_TEMP       | 75.000     | degrees C  | ok    | na        | na        | na        | 96.000    | 98.000    | na
CPU0_Power       | 184.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 6000.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1A_PWM   | 22.000     | percent    | ok    | na        | na        | na        | na        | na        | na
CPU_CUPS         | 3.000      | percent    | ok    | na        | na        | na        | na        | 100.000   | na
[XXXXXX@controller-0 ~(keystone_admin)]$ sudo ipmitool sensor
CPU_0_PROCHOT    | 0x0        | discrete   | 0x0080| na        | na        | na        | na        | na        | na
CPU_0_STATUS     | 0x0        | discrete   | 0x8080| na        | na        | na        | na        | na        | na
CPU_0_Vcore      | 1.811      | Volts      | ok    | na        | 1.690     | na        | na        | 1.870     | na
CPU0DDR_ABC_1.2V | 1.231      | Volts      | ok    | na        | 1.134     | na        | na        | 1.256     | na
CPU0DDR_DEF_1.2V | 1.231      | Volts      | ok    | na        | 1.134     | na        | na        | 1.256     | na
CPU_0_DTS_TEMP   | -23.000    | degrees C  | ok    | na        | na        | na        | na        | na        | na
CPU_0_TEMP       | 75.000     | degrees C  | ok    | na        | na        | na        | 96.000    | 98.000    | na
CPU_0_MARGIN     | 12.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
CPU0_Power       | 184.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_PCH_TEMP     | 34.000     | degrees C  | ok    | na        | 5.000     | na        | na        | 82.000    | na
CPU_0_DIMM_C0    | 39.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_D0    | 37.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_A0    | 35.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_B0    | 35.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_G0    | 38.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_H0    | 37.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_E0    | 36.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_F0    | 36.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
MAX_DIMM_TEMP    | 39.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
INLET_TEMP_L     | 25.000     | degrees C  | ok    | na        | -6.000    | na        | 50.000    | 59.000    | 61.000
INLET_TEMP_R     | 24.000     | degrees C  | ok    | na        | -6.000    | na        | 50.000    | 59.000    | 61.000
INLET_TEMP_MAX   | 25.000     | degrees C  | ok    | na        | -6.000    | na        | 50.000    | 59.000    | 61.000
OUTLET_TEMP_L    | 46.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
OUTLET_TEMP_R    | 41.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
OUTLET_TEMP_MAX  | 46.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 6000.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1B       | 6500.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_2A       | 6000.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_2B       | 6500.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1A_PWM   | 22.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1B_PWM   | 22.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_2A_PWM   | 22.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_2B_PWM   | 22.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_V1.05        | 1.053      | Volts      | ok    | na        | 0.993     | na        | na        | 1.097     | na
SYS_V12          | 12.119     | Volts      | ok    | na        | 11.348    | na        | na        | 12.552    | na
SYS_V3.3         | 3.329      | Volts      | ok    | na        | 3.104     | na        | na        | 3.431     | na
SYS_V5           | 5.053      | Volts      | ok    | na        | 4.725     | na        | na        | 5.225     | na
CPU_CUPS         | 3.000      | percent    | ok    | na        | na        | na        | na        | 100.000   | na
MB_HSC_TEMP      | 42.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 125.000   | na
DIMM_VREFGH_TEMP | 34.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 125.000   | na
DIMM_VRABCD_TEMP | 35.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 125.000   | na
RTC_Voltage      | 3.066      | Volts      | ok    | na        | 2.289     | na        | na        | 3.444     | na
MB_HSC_PIN       | 288.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
MB_HSC_PIN_AVG   | 248.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
MB_HSC_PEAK_PIN  | 440.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_1_STATUS     | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
PSU_2_STATUS     | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
PSU_1_FAN        | 4000.000   | RPM        | ok    | 800.000   | 1120.000  | na        | na        | na        | na
PSU_2_FAN        | 4000.000   | RPM        | ok    | 800.000   | 1120.000  | na        | na        | na        | na
PSU_1_TEMP_1     | 27.000     | degrees C  | ok    | na        | na        | na        | na        | 60.000    | 64.000
PSU_2_TEMP_1     | 27.000     | degrees C  | ok    | na        | na        | na        | na        | 60.000    | 64.000
PSU_1_TEMP_2     | 46.000     | degrees C  | ok    | na        | na        | na        | na        | 92.000    | 97.000
PSU_2_TEMP_2     | 46.000     | degrees C  | ok    | na        | na        | na        | na        | 92.000    | 97.000
PSU_POWER_IN     | 484.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_1_POWER_IN   | 252.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_2_POWER_IN   | 240.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_1_POWER_OUT  | 228.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_2_POWER_OUT  | 216.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_1_CURRENT_IN | 1.197      | Amps       | ok    | na        | na        | na        | na        | na        | na
PSU_2_CURRENT_IN | 1.134      | Amps       | ok    | na        | na        | na        | na        | na        | na
PSU1_CURRENT_OUT | 19.080     | Amps       | ok    | na        | na        | na        | na        | na        | na
PSU2_CURRENT_OUT | 18.020     | Amps       | ok    | na        | na        | na        | na        | na        | na
PWR_UNIT_REDUND  | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
PWR_UNIT_STATUS  | 0x0        | discrete   | 0x0080| na        | na        | na        | na        | na        | na
ACPI_STATE       | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
SSD_0_TEMP       | 33.000     | degrees C  | ok    | na        | 0.000     | na        | na        | 70.000    | 79.000
SSD_1_TEMP       | 35.000     | degrees C  | ok    | na        | 0.000     | na        | na        | 70.000    | 79.000
PML_WEST_TEMP    | 54.000     | degrees C  | ok    | na        | na        | na        | na        | 110.000   | 114.000
PML_LOCAL_TEMP   | 51.000     | degrees C  | ok    | na        | na        | na        | 80.000    | 85.000    | na
PML_VDD_TEMP     | 56.000     | degrees C  | ok    | na        | na        | na        | na        | 125.000   | na
PML_EAST_TEMP    | 54.000     | degrees C  | ok    | na        | na        | na        | na        | 110.000   | 114.000
SC_1_E810        | na         | degrees C  | na    | na        | 0.000     | 5.000     | 100.000   | 105.000   | 115.000
SC_2_E810        | 40.000     | degrees C  | ok    | na        | 0.000     | 5.000     | 100.000   | 105.000   | 115.000
[XXXXXX@controller-0 ~(keystone_admin)]$

```

## Observed temps raise and fans rpm raise with load - success

## MEAKV-645
## PTU 4 - Core AVX512 with Turbo
## sudo ./ptu -ct 5 -cp 100 -b 1


## Sensors before load

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ sudo ipmitool sensor | grep -e CPU_0_TEMP -e CPU0_Power -e SYS_FAN_1A -e CPU_CUPS
CPU_0_TEMP       | 54.000     | degrees C  | ok    | na        | na        | na        | 96.000    | 98.000    | na
CPU0_Power       | 92.000     | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 5000.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1A_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
CPU_CUPS         | 3.000      | percent    | ok    | na        | na        | na        | na        | 100.000   | na
[XXXXXX@controller-0 ~(keystone_admin)]$
[XXXXXX@controller-0 ~(keystone_admin)]$ sudo ipmitool sensor
CPU_0_PROCHOT    | 0x0        | discrete   | 0x0080| na        | na        | na        | na        | na        | na
CPU_0_STATUS     | 0x0        | discrete   | 0x8080| na        | na        | na        | na        | na        | na
CPU_0_Vcore      | 1.822      | Volts      | ok    | na        | 1.690     | na        | na        | 1.870     | na
CPU0DDR_ABC_1.2V | 1.231      | Volts      | ok    | na        | 1.134     | na        | na        | 1.256     | na
CPU0DDR_DEF_1.2V | 1.231      | Volts      | ok    | na        | 1.134     | na        | na        | 1.256     | na
CPU_0_DTS_TEMP   | -44.000    | degrees C  | ok    | na        | na        | na        | na        | na        | na
CPU_0_TEMP       | 54.000     | degrees C  | ok    | na        | na        | na        | 96.000    | 98.000    | na
CPU_0_MARGIN     | 33.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
CPU0_Power       | 94.000     | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_PCH_TEMP     | 34.000     | degrees C  | ok    | na        | 5.000     | na        | na        | 82.000    | na
CPU_0_DIMM_C0    | 39.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_D0    | 37.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_A0    | 36.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_B0    | 35.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_G0    | 38.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_H0    | 37.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_E0    | 37.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_F0    | 36.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
MAX_DIMM_TEMP    | 39.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
INLET_TEMP_L     | 25.000     | degrees C  | ok    | na        | -6.000    | na        | 50.000    | 59.000    | 61.000
INLET_TEMP_R     | 24.000     | degrees C  | ok    | na        | -6.000    | na        | 50.000    | 59.000    | 61.000
INLET_TEMP_MAX   | 25.000     | degrees C  | ok    | na        | -6.000    | na        | 50.000    | 59.000    | 61.000
OUTLET_TEMP_L    | 44.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
OUTLET_TEMP_R    | 40.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
OUTLET_TEMP_MAX  | 44.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 5000.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1B       | 5500.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_2A       | 5000.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_2B       | 5500.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1A_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1B_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_2A_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_2B_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_V1.05        | 1.055      | Volts      | ok    | na        | 0.993     | na        | na        | 1.097     | na
SYS_V12          | 12.138     | Volts      | ok    | na        | 11.348    | na        | na        | 12.552    | na
SYS_V3.3         | 3.329      | Volts      | ok    | na        | 3.104     | na        | na        | 3.431     | na
SYS_V5           | 5.053      | Volts      | ok    | na        | 4.725     | na        | na        | 5.225     | na
CPU_CUPS         | 3.000      | percent    | ok    | na        | na        | na        | na        | 100.000   | na
MB_HSC_TEMP      | 40.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 125.000   | na
DIMM_VREFGH_TEMP | 34.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 125.000   | na
DIMM_VRABCD_TEMP | 36.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 125.000   | na
RTC_Voltage      | 3.066      | Volts      | ok    | na        | 2.289     | na        | na        | 3.444     | na
MB_HSC_PIN       | 188.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
MB_HSC_PIN_AVG   | 248.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
MB_HSC_PEAK_PIN  | 440.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_1_STATUS     | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
PSU_2_STATUS     | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
PSU_1_FAN        | 3840.000   | RPM        | ok    | 800.000   | 1120.000  | na        | na        | na        | na
PSU_2_FAN        | 4000.000   | RPM        | ok    | 800.000   | 1120.000  | na        | na        | na        | na
PSU_1_TEMP_1     | 27.000     | degrees C  | ok    | na        | na        | na        | na        | 60.000    | 64.000
PSU_2_TEMP_1     | 27.000     | degrees C  | ok    | na        | na        | na        | na        | 60.000    | 64.000
PSU_1_TEMP_2     | 46.000     | degrees C  | ok    | na        | na        | na        | na        | 92.000    | 97.000
PSU_2_TEMP_2     | 46.000     | degrees C  | ok    | na        | na        | na        | na        | 92.000    | 97.000
PSU_POWER_IN     | 374.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_1_POWER_IN   | 198.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_2_POWER_IN   | 180.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_1_POWER_OUT  | 174.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_2_POWER_OUT  | 162.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_1_CURRENT_IN | 0.945      | Amps       | ok    | na        | na        | na        | na        | na        | na
PSU_2_CURRENT_IN | 0.882      | Amps       | ok    | na        | na        | na        | na        | na        | na
PSU1_CURRENT_OUT | 14.840     | Amps       | ok    | na        | na        | na        | na        | na        | na
PSU2_CURRENT_OUT | 13.780     | Amps       | ok    | na        | na        | na        | na        | na        | na
PWR_UNIT_REDUND  | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
PWR_UNIT_STATUS  | 0x0        | discrete   | 0x0080| na        | na        | na        | na        | na        | na
ACPI_STATE       | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
SSD_0_TEMP       | 34.000     | degrees C  | ok    | na        | 0.000     | na        | na        | 70.000    | 79.000
SSD_1_TEMP       | 35.000     | degrees C  | ok    | na        | 0.000     | na        | na        | 70.000    | 79.000
PML_WEST_TEMP    | 55.000     | degrees C  | ok    | na        | na        | na        | na        | 110.000   | 114.000
PML_LOCAL_TEMP   | 53.000     | degrees C  | ok    | na        | na        | na        | 80.000    | 85.000    | na
PML_VDD_TEMP     | 57.000     | degrees C  | ok    | na        | na        | na        | na        | 125.000   | na
PML_EAST_TEMP    | 55.000     | degrees C  | ok    | na        | na        | na        | na        | 110.000   | 114.000
SC_1_E810        | na         | degrees C  | na    | na        | 0.000     | 5.000     | 100.000   | 105.000   | 115.000
SC_2_E810        | 42.000     | degrees C  | ok    | na        | 0.000     | 5.000     | 100.000   | 105.000   | 115.000
[XXXXXX@controller-0 ~(keystone_admin)]$
```

## Initate load

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ sudo ./ptu -ct 5 -cp 100 -b 1
Password:

XXXXXX ./ptu -ct 5 -cp 100 -b 1

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
Available System Memory:             78754 MB


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

[10/30/23 21:53:57 UTC] PTU started.

Press <Ctrl-C> to stop.


CPU_0: [IDLE] CFreq=2490, UFreq=1700, Util=0.62, IPC=0.89, Temp=54, DTS=44, Power=92.0, Volt=0.877, UVolt=0.870
CPU_0: [TESTCFG] TestSel=5 (Core AVX-512), CoreMask=0xFFFFFFFFFFFFFFFF, ThreadMask=0xFF, PwrLevel=100, Turbo=1
CPU_0: [RUNNING] CFreq=2063, UFreq=1300, Util=100.00, IPC=3.45, Temp=66, DTS=32, Power=184.5, Volt=0.807, UVolt=0.802

```

## ptu -mon

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ sudo ./ptu -mon

Command: ./ptu -mon

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
Available System Memory:             78731 MB


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

[10/30/23 21:56:13 UTC] PTU started.

Press <Ctrl-C> to stop.


 Index Device Cor Thr CFreq UFreq   Util  IPC     C0     C1     C6    PC2    PC6 MC Ch Sl  Temp DTS  Power  Volt UVolt TStat TLog #TL TMargin
     0   CPU0   -   -  2058  1300 100.00 3.43 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.52 0.800 0.792   0x0  0x0   0  12.359
     0   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.11     -     -     -  0x0   -       -
     1   CPU0   -   -  2055  1200 100.00 3.44 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.35 0.782 0.780   0x0  0x0   0  12.438
     1   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.04     -     -     -  0x0   -       -
     2   CPU0   -   -  2050  1200 100.00 3.45 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.57 0.782 0.780   0x0  0x0   0  12.438
     2   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.93     -     -     -  0x0   -       -
     3   CPU0   -   -  2052  1300 100.00 3.45 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.43 0.800 0.792   0x0  0x0   0  12.453
     3   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.90     -     -     -  0x0   -       -
     4   CPU0   -   -  2054  1300 100.00 3.45 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.33 0.797 0.780   0x0  0x0   0  12.344
     4   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.01     -     -     -  0x0   -       -
     5   CPU0   -   -  2051  1200 100.00 3.46 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.71 0.782 0.780   0x0  0x0   0  12.438
     5   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.91     -     -     -  0x0   -       -
     6   CPU0   -   -  2052  1200 100.00 3.45 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.34 0.797 0.780   0x0  0x0   0  12.297
     6   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.96     -     -     -  0x0   -       -
     7   CPU0   -   -  2056  1200 100.00 3.45 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.59 0.800 0.780   0x0  0x0   0  12.266
     7   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.97     -     -     -  0x0   -       -
     8   CPU0   -   -  2057  1200 100.00 3.45 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.38 0.800 0.777   0x0  0x0   0  12.469
     8   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.02     -     -     -  0x0   -       -
     9   CPU0   -   -  2056  1300 100.00 3.44 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.55 0.782 0.792   0x0  0x0   0  12.359
     9   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.06     -     -     -  0x0   -       -
    10   CPU0   -   -  2057  1200 100.00 3.44 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.40 0.800 0.780   0x0  0x0   0  12.453
    10   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.98     -     -     -  0x0   -       -
    11   CPU0   -   -  2057  1200 100.00 3.45 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.48 0.800 0.780   0x0  0x0   0  12.391
    11   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.97     -     -     -  0x0   -       -
    12   CPU0   -   -  2056  1200 100.00 3.46 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.45 0.800 0.780   0x0  0x0   0  12.531
    12   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.81     -     -     -  0x0   -       -
    13   CPU0   -   -  2053  1300 100.00 3.45 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.55 0.800 0.792   0x0  0x0   0  12.406
    13   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.87     -     -     -  0x0   -       -
    14   CPU0   -   -  2056  1200 100.00 3.44 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.48 0.800 0.780   0x0  0x0   0  12.453
    14   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.81     -     -     -  0x0   -       -
    15   CPU0   -   -  2056  1200 100.00 3.45 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.36 0.797 0.777   0x0  0x0   0  12.484
    15   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.95     -     -     -  0x0   -       -
    16   CPU0   -   -  2056  1200 100.00 3.45 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.44 0.800 0.780   0x0  0x0   0  12.375
    16   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.86     -     -     -  0x0   -       -
    17   CPU0   -   -  2051  1300 100.00 3.46 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.64 0.785 0.792   0x0  0x0   0  12.344
    17   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.76     -     -     -  0x0   -       -
    18   CPU0   -   -  2052  1300 100.00 3.46 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.27 0.782 0.792   0x0  0x0   0  12.312
    18   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.76     -     -     -  0x0   -       -
    19   CPU0   -   -  2055  1200 100.00 3.45 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 180.22 0.785 0.780   0x0  0x0   0  12.422
    19   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.92     -     -     -  0x0   -       -
    20   CPU0   -   -  2053  1300 100.00 3.46 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 188.98 0.800 0.792   0x0  0x0   0  12.406
    20   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.97     -     -     -  0x0   -       -
    21   CPU0   -   -  2050  1300 100.00 3.46 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.34 0.782 0.792   0x0  0x0   0  12.203
    21   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.81     -     -     -  0x0   -       -
    22   CPU0   -   -  2054  1200 100.00 3.45 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.61 0.797 0.780   0x0  0x0   0  12.344
    22   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.93     -     -     -  0x0   -       -
    23   CPU0   -   -  2055  1200 100.00 3.44 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.36 0.782 0.777   0x0  0x0   0  12.422
    23   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.01     -     -     -  0x0   -       -
    24   CPU0   -   -  2053  1300 100.00 3.44 100.00   0.00   0.00   0.00   0.00  -  -  -    75  23 184.57 0.785 0.792   0x0  0x0   0  12.328
    24   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   9.12     -     -     -  0x0   -       -
    25   CPU0   -   -  2052  1200 100.00 3.46 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.32 0.800 0.792   0x0  0x0   0  12.266
    25   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.88     -     -     -  0x0   -       -
    26   CPU0   -   -  2051  1300 100.00 3.46 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.62 0.782 0.792   0x0  0x0   0  12.312
    26   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.82     -     -     -  0x0   -       -
    27   CPU0   -   -  2048  1200 100.00 3.46 100.00   0.00   0.00   0.00   0.00  -  -  -    76  22 184.43 0.800 0.780   0x0  0x0   0  12.344
    27   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    39   -   8.79     -     -     -  0x0   -       -
^C
[10/30/23 21:56:44 UTC] PTU stopped.

[XXXXXX@controller-0 ~(keystone_admin)]$
```

## check sensors

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ sudo ipmitool sensor | grep -e CPU_0_TEMP -e CPU0_Power -e SYS_FAN_1A -e CPU_CUPS
CPU_0_TEMP       | 75.000     | degrees C  | ok    | na        | na        | na        | 96.000    | 98.000    | na
CPU0_Power       | 184.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 6000.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1A_PWM   | 22.000     | percent    | ok    | na        | na        | na        | na        | na        | na
CPU_CUPS         | 3.000      | percent    | ok    | na        | na        | na        | na        | 100.000   | na
[XXXXXX@controller-0 ~(keystone_admin)]$ sudo ipmitool sensor
CPU_0_PROCHOT    | 0x0        | discrete   | 0x0080| na        | na        | na        | na        | na        | na
CPU_0_STATUS     | 0x0        | discrete   | 0x8080| na        | na        | na        | na        | na        | na
CPU_0_Vcore      | 1.811      | Volts      | ok    | na        | 1.690     | na        | na        | 1.870     | na
CPU0DDR_ABC_1.2V | 1.227      | Volts      | ok    | na        | 1.134     | na        | na        | 1.256     | na
CPU0DDR_DEF_1.2V | 1.231      | Volts      | ok    | na        | 1.134     | na        | na        | 1.256     | na
CPU_0_DTS_TEMP   | -23.000    | degrees C  | ok    | na        | na        | na        | na        | na        | na
CPU_0_TEMP       | 75.000     | degrees C  | ok    | na        | na        | na        | 96.000    | 98.000    | na
CPU_0_MARGIN     | 12.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
CPU0_Power       | 184.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_PCH_TEMP     | 34.000     | degrees C  | ok    | na        | 5.000     | na        | na        | 82.000    | na
CPU_0_DIMM_C0    | 39.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_D0    | 36.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_A0    | 35.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_B0    | 35.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_G0    | 38.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_H0    | 36.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_E0    | 36.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_F0    | 36.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
MAX_DIMM_TEMP    | 39.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
INLET_TEMP_L     | 25.000     | degrees C  | ok    | na        | -6.000    | na        | 50.000    | 59.000    | 61.000
INLET_TEMP_R     | 24.000     | degrees C  | ok    | na        | -6.000    | na        | 50.000    | 59.000    | 61.000
INLET_TEMP_MAX   | 25.000     | degrees C  | ok    | na        | -6.000    | na        | 50.000    | 59.000    | 61.000
OUTLET_TEMP_L    | 44.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
OUTLET_TEMP_R    | 41.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
OUTLET_TEMP_MAX  | 44.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 6000.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1B       | 6500.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_2A       | 6000.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_2B       | 6500.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1A_PWM   | 22.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1B_PWM   | 22.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_2A_PWM   | 22.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_2B_PWM   | 22.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_V1.05        | 1.053      | Volts      | ok    | na        | 0.993     | na        | na        | 1.097     | na
SYS_V12          | 12.100     | Volts      | ok    | na        | 11.348    | na        | na        | 12.552    | na
SYS_V3.3         | 3.329      | Volts      | ok    | na        | 3.104     | na        | na        | 3.431     | na
SYS_V5           | 5.053      | Volts      | ok    | na        | 4.725     | na        | na        | 5.225     | na
CPU_CUPS         | 3.000      | percent    | ok    | na        | na        | na        | na        | 100.000   | na
MB_HSC_TEMP      | 40.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 125.000   | na
DIMM_VREFGH_TEMP | 34.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 125.000   | na
DIMM_VRABCD_TEMP | 35.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 125.000   | na
RTC_Voltage      | 3.066      | Volts      | ok    | na        | 2.289     | na        | na        | 3.444     | na
MB_HSC_PIN       | 304.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
MB_HSC_PIN_AVG   | 252.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
MB_HSC_PEAK_PIN  | 440.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_1_STATUS     | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
PSU_2_STATUS     | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
PSU_1_FAN        | 4000.000   | RPM        | ok    | 800.000   | 1120.000  | na        | na        | na        | na
PSU_2_FAN        | 3840.000   | RPM        | ok    | 800.000   | 1120.000  | na        | na        | na        | na
PSU_1_TEMP_1     | 27.000     | degrees C  | ok    | na        | na        | na        | na        | 60.000    | 64.000
PSU_2_TEMP_1     | 27.000     | degrees C  | ok    | na        | na        | na        | na        | 60.000    | 64.000
PSU_1_TEMP_2     | 46.000     | degrees C  | ok    | na        | na        | na        | na        | 92.000    | 97.000
PSU_2_TEMP_2     | 46.000     | degrees C  | ok    | na        | na        | na        | na        | 92.000    | 97.000
PSU_POWER_IN     | 473.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_1_POWER_IN   | 246.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_2_POWER_IN   | 234.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_1_POWER_OUT  | 222.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_2_POWER_OUT  | 210.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_1_CURRENT_IN | 1.134      | Amps       | ok    | na        | na        | na        | na        | na        | na
PSU_2_CURRENT_IN | 1.071      | Amps       | ok    | na        | na        | na        | na        | na        | na
PSU1_CURRENT_OUT | 18.550     | Amps       | ok    | na        | na        | na        | na        | na        | na
PSU2_CURRENT_OUT | 17.490     | Amps       | ok    | na        | na        | na        | na        | na        | na
PWR_UNIT_REDUND  | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
PWR_UNIT_STATUS  | 0x0        | discrete   | 0x0080| na        | na        | na        | na        | na        | na
ACPI_STATE       | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
SSD_0_TEMP       | 33.000     | degrees C  | ok    | na        | 0.000     | na        | na        | 70.000    | 79.000
SSD_1_TEMP       | 35.000     | degrees C  | ok    | na        | 0.000     | na        | na        | 70.000    | 79.000
PML_WEST_TEMP    | 55.000     | degrees C  | ok    | na        | na        | na        | na        | 110.000   | 114.000
PML_LOCAL_TEMP   | 53.000     | degrees C  | ok    | na        | na        | na        | 80.000    | 85.000    | na
PML_VDD_TEMP     | 57.000     | degrees C  | ok    | na        | na        | na        | na        | 125.000   | na
PML_EAST_TEMP    | 55.000     | degrees C  | ok    | na        | na        | na        | na        | 110.000   | 114.000
SC_1_E810        | na         | degrees C  | na    | na        | 0.000     | 5.000     | 100.000   | 105.000   | 115.000
SC_2_E810        | 41.000     | degrees C  | ok    | na        | 0.000     | 5.000     | 100.000   | 105.000   | 115.000
[XXXXXX@controller-0 ~(keystone_admin)]$


```


## Success, was able to observe temp rise, then fans increasing as load was started


## MEAKV-646 
## PTU 5 - Turbo Test
## sudo ./ptu -ct 8 -allcore -b 1

## sensors before load

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ sudo ipmitool sensor | grep -e CPU_0_TEMP -e CPU0_Power -e SYS_FAN_1A -e CPU_CUPS
CPU_0_TEMP       | 55.000     | degrees C  | ok    | na        | na        | na        | 96.000    | 98.000    | na
CPU0_Power       | 92.000     | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 5000.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1A_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
CPU_CUPS         | 3.000      | percent    | ok    | na        | na        | na        | na        | 100.000   | na
[XXXXXX@controller-0 ~(keystone_admin)]$ sudo ipmitool sensor
CPU_0_PROCHOT    | 0x0        | discrete   | 0x0080| na        | na        | na        | na        | na        | na
CPU_0_STATUS     | 0x0        | discrete   | 0x8080| na        | na        | na        | na        | na        | na
CPU_0_Vcore      | 1.825      | Volts      | ok    | na        | 1.690     | na        | na        | 1.870     | na
CPU0DDR_ABC_1.2V | 1.231      | Volts      | ok    | na        | 1.134     | na        | na        | 1.256     | na
CPU0DDR_DEF_1.2V | 1.231      | Volts      | ok    | na        | 1.134     | na        | na        | 1.256     | na
CPU_0_DTS_TEMP   | -43.000    | degrees C  | ok    | na        | na        | na        | na        | na        | na
CPU_0_TEMP       | 55.000     | degrees C  | ok    | na        | na        | na        | 96.000    | 98.000    | na
CPU_0_MARGIN     | 32.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
CPU0_Power       | 92.000     | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_PCH_TEMP     | 34.000     | degrees C  | ok    | na        | 5.000     | na        | na        | 82.000    | na
CPU_0_DIMM_C0    | 39.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_D0    | 37.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_A0    | 36.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_B0    | 36.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_G0    | 38.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_H0    | 37.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_E0    | 37.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_F0    | 36.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
MAX_DIMM_TEMP    | 39.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
INLET_TEMP_L     | 25.000     | degrees C  | ok    | na        | -6.000    | na        | 50.000    | 59.000    | 61.000
INLET_TEMP_R     | 24.000     | degrees C  | ok    | na        | -6.000    | na        | 50.000    | 59.000    | 61.000
INLET_TEMP_MAX   | 25.000     | degrees C  | ok    | na        | -6.000    | na        | 50.000    | 59.000    | 61.000
OUTLET_TEMP_L    | 45.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
OUTLET_TEMP_R    | 41.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
OUTLET_TEMP_MAX  | 45.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 5000.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1B       | 5500.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_2A       | 5000.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_2B       | 5500.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1A_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1B_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_2A_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_2B_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_V1.05        | 1.055      | Volts      | ok    | na        | 0.993     | na        | na        | 1.097     | na
SYS_V12          | 12.157     | Volts      | ok    | na        | 11.348    | na        | na        | 12.552    | na
SYS_V3.3         | 3.329      | Volts      | ok    | na        | 3.104     | na        | na        | 3.431     | na
SYS_V5           | 5.053      | Volts      | ok    | na        | 4.725     | na        | na        | 5.225     | na
CPU_CUPS         | 3.000      | percent    | ok    | na        | na        | na        | na        | 100.000   | na
MB_HSC_TEMP      | 40.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 125.000   | na
DIMM_VREFGH_TEMP | 34.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 125.000   | na
DIMM_VRABCD_TEMP | 36.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 125.000   | na
RTC_Voltage      | 3.066      | Volts      | ok    | na        | 2.289     | na        | na        | 3.444     | na
MB_HSC_PIN       | 196.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
MB_HSC_PIN_AVG   | 256.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
MB_HSC_PEAK_PIN  | 440.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_1_STATUS     | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
PSU_2_STATUS     | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
PSU_1_FAN        | 3840.000   | RPM        | ok    | 800.000   | 1120.000  | na        | na        | na        | na
PSU_2_FAN        | 3840.000   | RPM        | ok    | 800.000   | 1120.000  | na        | na        | na        | na
PSU_1_TEMP_1     | 27.000     | degrees C  | ok    | na        | na        | na        | na        | 60.000    | 64.000
PSU_2_TEMP_1     | 27.000     | degrees C  | ok    | na        | na        | na        | na        | 60.000    | 64.000
PSU_1_TEMP_2     | 46.000     | degrees C  | ok    | na        | na        | na        | na        | 92.000    | 97.000
PSU_2_TEMP_2     | 46.000     | degrees C  | ok    | na        | na        | na        | na        | 92.000    | 97.000
PSU_POWER_IN     | 374.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_1_POWER_IN   | 192.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_2_POWER_IN   | 180.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_1_POWER_OUT  | 174.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_2_POWER_OUT  | 162.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_1_CURRENT_IN | 0.945      | Amps       | ok    | na        | na        | na        | na        | na        | na
PSU_2_CURRENT_IN | 0.882      | Amps       | ok    | na        | na        | na        | na        | na        | na
PSU1_CURRENT_OUT | 14.840     | Amps       | ok    | na        | na        | na        | na        | na        | na
PSU2_CURRENT_OUT | 13.250     | Amps       | ok    | na        | na        | na        | na        | na        | na
PWR_UNIT_REDUND  | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
PWR_UNIT_STATUS  | 0x0        | discrete   | 0x0080| na        | na        | na        | na        | na        | na
ACPI_STATE       | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
SSD_0_TEMP       | 33.000     | degrees C  | ok    | na        | 0.000     | na        | na        | 70.000    | 79.000
SSD_1_TEMP       | 35.000     | degrees C  | ok    | na        | 0.000     | na        | na        | 70.000    | 79.000
PML_WEST_TEMP    | 55.000     | degrees C  | ok    | na        | na        | na        | na        | 110.000   | 114.000
PML_LOCAL_TEMP   | 53.000     | degrees C  | ok    | na        | na        | na        | 80.000    | 85.000    | na
PML_VDD_TEMP     | 57.000     | degrees C  | ok    | na        | na        | na        | na        | 125.000   | na
PML_EAST_TEMP    | 55.000     | degrees C  | ok    | na        | na        | na        | na        | 110.000   | 114.000
SC_1_E810        | na         | degrees C  | na    | na        | 0.000     | 5.000     | 100.000   | 105.000   | 115.000
SC_2_E810        | 41.000     | degrees C  | ok    | na        | 0.000     | 5.000     | 100.000   | 105.000   | 115.000
[XXXXXX@controller-0 ~(keystone_admin)]$
```

## Initiating load

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ sudo ./ptu -ct 8 -allcore -b 1
Password:

XXXXXX ./ptu -ct 8 -allcore -b 1

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
Available System Memory:             78747 MB


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

[10/30/23 22:06:44 UTC] PTU started.

Press <Ctrl-C> to stop.


CPU_0: [IDLE] CFreq=2530, UFreq=1700, Util=0.34, IPC=0.87, Temp=54, DTS=44, Power=91.6, Volt=0.877, UVolt=0.870

### TURBO is enabled ###

Instr   CPU #Cores CFreq(act) CFreq(exp) UFreq Power TDP  Temp Volt  UVolt
IA/SSE  0   32     2.5        2.7        1.7   142.2 185  59   0.871 0.867


```

## ptu -mon

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ sudo ./ptu -mon

Command: ./ptu -mon

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
Available System Memory:             78731 MB


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

[10/30/23 22:07:33 UTC] PTU started.

Press <Ctrl-C> to stop.


 Index Device Cor Thr CFreq UFreq   Util  IPC     C0     C1     C6    PC2    PC6 MC Ch Sl  Temp DTS  Power  Volt UVolt TStat TLog #TL TMargin
     0   CPU0   -   -  2495  1700   2.19 0.94   3.84  96.16   0.00   0.00   0.00  -  -  -    55  43  94.50 0.877 0.870   0x0  0x0   0  32.000
     0   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   9.19     -     -     -  0x0   -       -
     1   CPU0   -   -  2499  1700   2.47 0.93   4.01  95.99   0.00   0.00   0.00  -  -  -    56  42  94.86 0.877 0.870   0x0  0x0   0  31.828
     1   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   9.20     -     -     -  0x0   -       -
     2   CPU0   -   -  2495  1700   1.91 0.98   3.43  96.57   0.00   0.00   0.00  -  -  -    57  41  94.20 0.877 0.870   0x0  0x0   0  32.297
     2   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   9.17     -     -     -  0x0   -       -
     3   CPU0   -   -  2493  1700   1.29 0.95   2.26  97.74   0.00   0.00   0.00  -  -  -    54  44  93.09 0.877 0.870   0x0  0x0   0  32.609
     3   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   9.12     -     -     -  0x0   -       -
     4   CPU0   -   -  2494  1700   2.63 0.90   3.80  96.20   0.00   0.00   0.00  -  -  -    54  44  94.71 0.877 0.870   0x0  0x0   0  32.016
     4   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   9.25     -     -     -  0x0   -       -
     5   CPU0   -   -  2493  1700   0.76 0.89   1.31  98.69   0.00   0.00   0.00  -  -  -    54  44  92.16 0.877 0.870   0x0  0x0   0  33.719
     5   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   9.10     -     -     -  0x0   -       -
     6   CPU0   -   -  2495  1700   0.69 0.89   1.23  98.77   0.00   0.00   0.00  -  -  -    54  44  92.15 0.877 0.870   0x0  0x0   0  33.812
     6   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   9.03     -     -     -  0x0   -       -
     7   CPU0   -   -  2493  1700   1.32 0.89   2.22  97.78   0.00   0.00   0.00  -  -  -    54  44  93.04 0.877 0.870   0x0  0x0   0  33.516
     7   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   9.09     -     -     -  0x0   -       -
     8   CPU0   -   -  2495  1700   0.59 0.88   1.04  98.96   0.00   0.00   0.00  -  -  -    54  44  91.74 0.877 0.870   0x0  0x0   0  33.734
     8   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   9.04     -     -     -  0x0   -       -
     9   CPU0   -   -  2494  1700   1.20 0.89   1.96  98.04   0.00   0.00   0.00  -  -  -    54  44  92.89 0.877 0.870   0x0  0x0   0  33.719
     9   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   9.15     -     -     -  0x0   -       -
    10   CPU0   -   -  2495  1700   0.56 0.89   1.00  99.00   0.00   0.00   0.00  -  -  -    54  44  91.95 0.877 0.870   0x0  0x0   0  33.812
    10   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   8.95     -     -     -  0x0   -       -
    11   CPU0   -   -  2485  1700   0.91 0.89   1.58  98.42   0.00   0.00   0.00  -  -  -    54  44  92.30 0.877 0.870   0x0  0x0   0  33.625
    11   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   8.98     -     -     -  0x0   -       -
    12   CPU0   -   -  2503  1700   0.53 0.89   0.89  99.11   0.00   0.00   0.00  -  -  -    54  44  91.78 0.877 0.870   0x0  0x0   0  33.734
    12   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   9.04     -     -     -  0x0   -       -
    13   CPU0   -   -  2493  1700   0.41 0.88   0.74  99.26   0.00   0.00   0.00  -  -  -    54  44  91.66 0.877 0.870   0x0  0x0   0  33.953
    13   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   9.01     -     -     -  0x0   -       -
    14   CPU0   -   -  2494  1700   0.77 0.88   1.35  98.65   0.00   0.00   0.00  -  -  -    54  44  92.14 0.877 0.870   0x0  0x0   0  33.500
    14   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   9.11     -     -     -  0x0   -       -
    15   CPU0   -   -  2494  1700   1.05 0.90   1.77  98.23   0.00   0.00   0.00  -  -  -    54  44  92.61 0.877 0.870   0x0  0x0   0  33.281
    15   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   9.08     -     -     -  0x0   -       -
    16   CPU0   -   -  2479  1700   1.60 0.91   2.56  97.44   0.00   0.00   0.00  -  -  -    55  43  93.39 0.877 0.870   0x0  0x0   0  33.375
    16   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   9.02     -     -     -  0x0   -       -
    17   CPU0   -   -  2511  1700   1.06 0.89   1.81  98.19   0.00   0.00   0.00  -  -  -    54  44  92.55 0.877 0.870   0x0  0x0   0  33.125
    17   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   9.02     -     -     -  0x0   -       -
    18   CPU0   -   -  2492  1700   0.48 0.88   0.88  99.12   0.00   0.00   0.00  -  -  -    54  44  91.73 0.877 0.870   0x0  0x0   0  33.953
    18   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   8.91     -     -     -  0x0   -       -
    19   CPU0   -   -  2492  1700   1.32 0.88   1.98  98.02   0.00   0.00   0.00  -  -  -    55  43  92.91 0.877 0.870   0x0  0x0   0  33.703
    19   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   9.07     -     -     -  0x0   -       -
    20   CPU0   -   -  2498  1700   0.86 0.89   1.48  98.52   0.00   0.00   0.00  -  -  -    54  44  92.40 0.877 0.870   0x0  0x0   0  33.719
    20   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   9.03     -     -     -  0x0   -       -
    21   CPU0   -   -  2493  1700   0.92 0.90   1.55  98.45   0.00   0.00   0.00  -  -  -    54  44  92.32 0.877 0.870   0x0  0x0   0  33.750
    21   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   9.08     -     -     -  0x0   -       -
    22   CPU0   -   -  2499  1700   0.54 0.87   0.94  99.06   0.00   0.00   0.00  -  -  -    54  44  91.85 0.877 0.870   0x0  0x0   0  34.094
    22   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   9.01     -     -     -  0x0   -       -
    23   CPU0   -   -  2491  1700   0.51 0.86   0.91  99.09   0.00   0.00   0.00  -  -  -    54  44  91.82 0.877 0.870   0x0  0x0   0  34.172
    23   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   9.02     -     -     -  0x0   -       -
    24   CPU0   -   -  2494  1700   1.95 0.89   3.03  96.97   0.00   0.00   0.00  -  -  -    55  43  93.67 0.877 0.870   0x0  0x0   0  32.641
    24   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   9.18     -     -     -  0x0   -       -
    25   CPU0   -   -  2495  1700   0.69 0.89   1.21  98.79   0.00   0.00   0.00  -  -  -    54  44  92.04 0.877 0.870   0x0  0x0   0  33.938
    25   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   9.05     -     -     -  0x0   -       -
    26   CPU0   -   -  2493  1700   1.17 0.91   1.99  98.01   0.00   0.00   0.00  -  -  -    54  44  92.62 0.877 0.870   0x0  0x0   0  33.500
    26   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   9.11     -     -     -  0x0   -       -
    27   CPU0   -   -  2488  1700   1.09 0.89   1.80  98.20   0.00   0.00   0.00  -  -  -    54  44  92.45 0.877 0.870   0x0  0x0   0  34.047
    27   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   9.10     -     -     -  0x0   -       -
    28   CPU0   -   -  2501  1700   0.57 0.89   1.04  98.96   0.00   0.00   0.00  -  -  -    54  44  91.85 0.877 0.870   0x0  0x0   0  34.078
    28   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    38   -   9.09     -     -     -  0x0   -       -
^C
[10/30/23 22:08:04 UTC] PTU stopped.

[XXXXXX@controller-0 ~(keystone_admin)]$
```

## Sensors after load started

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ sudo ipmitool sensor | grep -e CPU_0_TEMP -e CPU0_Power -e SYS_FAN_1A -e CPU_CUPS
CPU_0_TEMP       | 53.000     | degrees C  | ok    | na        | na        | na        | 96.000    | 98.000    | na
CPU0_Power       | 93.000     | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 5000.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1A_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
CPU_CUPS         | 3.000      | percent    | ok    | na        | na        | na        | na        | 100.000   | na
[XXXXXX@controller-0 ~(keystone_admin)]$ sudo ipmitool sensor
CPU_0_PROCHOT    | 0x0        | discrete   | 0x0080| na        | na        | na        | na        | na        | na
CPU_0_STATUS     | 0x0        | discrete   | 0x8080| na        | na        | na        | na        | na        | na
CPU_0_Vcore      | 1.822      | Volts      | ok    | na        | 1.690     | na        | na        | 1.870     | na
CPU0DDR_ABC_1.2V | 1.231      | Volts      | ok    | na        | 1.134     | na        | na        | 1.256     | na
CPU0DDR_DEF_1.2V | 1.231      | Volts      | ok    | na        | 1.134     | na        | na        | 1.256     | na
CPU_0_DTS_TEMP   | -45.000    | degrees C  | ok    | na        | na        | na        | na        | na        | na
CPU_0_TEMP       | 53.000     | degrees C  | ok    | na        | na        | na        | 96.000    | 98.000    | na
CPU_0_MARGIN     | 34.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
CPU0_Power       | 91.000     | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_PCH_TEMP     | 34.000     | degrees C  | ok    | na        | 5.000     | na        | na        | 82.000    | na
CPU_0_DIMM_C0    | 38.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_D0    | 37.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_A0    | 35.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_B0    | 35.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_G0    | 37.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_H0    | 36.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_E0    | 36.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_F0    | 36.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
MAX_DIMM_TEMP    | 38.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
INLET_TEMP_L     | 25.000     | degrees C  | ok    | na        | -6.000    | na        | 50.000    | 59.000    | 61.000
INLET_TEMP_R     | 24.000     | degrees C  | ok    | na        | -6.000    | na        | 50.000    | 59.000    | 61.000
INLET_TEMP_MAX   | 25.000     | degrees C  | ok    | na        | -6.000    | na        | 50.000    | 59.000    | 61.000
OUTLET_TEMP_L    | 43.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
OUTLET_TEMP_R    | 39.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
OUTLET_TEMP_MAX  | 43.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 5000.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1B       | 5500.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_2A       | 5000.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_2B       | 5500.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1A_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1B_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_2A_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_2B_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_V1.05        | 1.053      | Volts      | ok    | na        | 0.993     | na        | na        | 1.097     | na
SYS_V12          | 12.138     | Volts      | ok    | na        | 11.348    | na        | na        | 12.552    | na
SYS_V3.3         | 3.329      | Volts      | ok    | na        | 3.104     | na        | na        | 3.431     | na
SYS_V5           | 5.053      | Volts      | ok    | na        | 4.725     | na        | na        | 5.225     | na
CPU_CUPS         | 3.000      | percent    | ok    | na        | na        | na        | na        | 100.000   | na
MB_HSC_TEMP      | 38.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 125.000   | na
DIMM_VREFGH_TEMP | 34.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 125.000   | na
DIMM_VRABCD_TEMP | 35.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 125.000   | na
RTC_Voltage      | 3.066      | Volts      | ok    | na        | 2.289     | na        | na        | 3.444     | na
MB_HSC_PIN       | 196.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
MB_HSC_PIN_AVG   | 248.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
MB_HSC_PEAK_PIN  | 440.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_1_STATUS     | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
PSU_2_STATUS     | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
PSU_1_FAN        | 3840.000   | RPM        | ok    | 800.000   | 1120.000  | na        | na        | na        | na
PSU_2_FAN        | 3840.000   | RPM        | ok    | 800.000   | 1120.000  | na        | na        | na        | na
PSU_1_TEMP_1     | 27.000     | degrees C  | ok    | na        | na        | na        | na        | 60.000    | 64.000
PSU_2_TEMP_1     | 27.000     | degrees C  | ok    | na        | na        | na        | na        | 60.000    | 64.000
PSU_1_TEMP_2     | 46.000     | degrees C  | ok    | na        | na        | na        | na        | 92.000    | 97.000
PSU_2_TEMP_2     | 46.000     | degrees C  | ok    | na        | na        | na        | na        | 92.000    | 97.000
PSU_POWER_IN     | 363.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_1_POWER_IN   | 192.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_2_POWER_IN   | 180.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_1_POWER_OUT  | 174.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_2_POWER_OUT  | 156.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_1_CURRENT_IN | 0.882      | Amps       | ok    | na        | na        | na        | na        | na        | na
PSU_2_CURRENT_IN | 0.882      | Amps       | ok    | na        | na        | na        | na        | na        | na
PSU1_CURRENT_OUT | 14.310     | Amps       | ok    | na        | na        | na        | na        | na        | na
PSU2_CURRENT_OUT | 13.250     | Amps       | ok    | na        | na        | na        | na        | na        | na
PWR_UNIT_REDUND  | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
PWR_UNIT_STATUS  | 0x0        | discrete   | 0x0080| na        | na        | na        | na        | na        | na
ACPI_STATE       | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
SSD_0_TEMP       | 33.000     | degrees C  | ok    | na        | 0.000     | na        | na        | 70.000    | 79.000
SSD_1_TEMP       | 35.000     | degrees C  | ok    | na        | 0.000     | na        | na        | 70.000    | 79.000
PML_WEST_TEMP    | 56.000     | degrees C  | ok    | na        | na        | na        | na        | 110.000   | 114.000
PML_LOCAL_TEMP   | 54.000     | degrees C  | ok    | na        | na        | na        | 80.000    | 85.000    | na
PML_VDD_TEMP     | 58.000     | degrees C  | ok    | na        | na        | na        | na        | 125.000   | na
PML_EAST_TEMP    | 56.000     | degrees C  | ok    | na        | na        | na        | na        | 110.000   | 114.000
SC_1_E810        | na         | degrees C  | na    | na        | 0.000     | 5.000     | 100.000   | 105.000   | 115.000
SC_2_E810        | 42.000     | degrees C  | ok    | na        | 0.000     | 5.000     | 100.000   | 105.000   | 115.000
[XXXXXX@controller-0 ~(keystone_admin)]$

```


## Temps didn't rise as much as with other tests, but all data recorded, no issues found.
## Success, end of performance tests with PTU