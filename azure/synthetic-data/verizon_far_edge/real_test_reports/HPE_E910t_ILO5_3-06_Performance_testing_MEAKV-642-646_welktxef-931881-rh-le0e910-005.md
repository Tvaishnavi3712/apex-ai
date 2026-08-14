# HPE ILO5 3.06 BIOS H08 v2.12
# HPE e910t server
# 8/27/24 James Patchett - MTCE Lab VCPfe
# Performance Test MEAKV-642-646 

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

## MEAKV-642
## Performance Test sudo ./ptat -ct 1 -b 0
## measure sensors first, then run load, then check during load

## Sensors

```log
root@controller-0:/home/XXXXXX/ptu# ipmitool sensor| grep -e CPU -e DutyCycle -e Watts
02-CPU           | 42.000     | degrees C  | ok    | na        | na        | na        | na        | 70.000    | na
51-CPU 1 PkgTmp  | 77.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
Fan 1 DutyCycle  | 28.616     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 2 DutyCycle  | 28.616     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 3 DutyCycle  | 28.616     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 4 DutyCycle  | 28.616     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 5 DutyCycle  | 28.616     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 6 DutyCycle  | 28.616     | percent    | ok    | na        | na        | na        | na        | na        | na
PS 1 Input       | 160.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PS 2 Input       | 150.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
CPU Utilization  | 20.000     | percent    | ok    | na        | na        | na        | na        | na        | na
PS 1 Output      | 160.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PS 2 Output      | 150.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
CPU_Stat_C1      | 0x0        | discrete   | 0x8080| na        | na        | na        | na        | na        | na
root@controller-0:/home/XXXXXX/ptu#
```

### Fan sensors show 54% usage, typically this is much lower on other 920 930 systems, but appears to be normal for 910

## Initiate load 

```log
root@controller-0:/home/XXXXXX/ptu# ./ptu -ct 1 -b 0

Command: ./ptu -ct 1 -b 0

Intel(R) Power Thermal Utility - Server Edition v2.3.1
Release Date: 12/04/2020
Copyright (C) 2020 Intel Corporation. All rights reserved.
Intel Confidential

/dev/ptusys: No such file or directory
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> System Info:                   <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Host Name:                           controller-0
Host IP:                             169.254.202.1
OS Name:                             Debian GNU/Linux 11 (bullseye) 11
Kernel Version:                      Linux 5.10.0-6-rt-amd64 #1 SMP PREEMPT_RT StarlingX Debian 5.10.177-1.stx.76 (2024-03-29
BIOS Version:                        HPE, H08, 09/14/2023
Processor(s):                        1 Processor(s) Installed.
DIMM(s):                             6 DIMM(s) Installed.
Total System Memory:                 93923 MB
Available System Memory:             46709 MB


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Processor: [CPU_0]             <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU ID:                              0x00050657 (Family 6 Model 55h Stepping 7)
CPU Brand Name:                      Intel(R) Xeon(R) Gold 6212U CPU @ 2.40GHz
CPU Code Name:                       Cascade Lake
CPU Type:                            Production Part
CPU Segment:                         Server
CPU PPIN:                            0x169B33BDA6E28B0C
CPU Base Frequency:                  1500 MHz
CPU Minimum Frequency:               1000 MHz
CPU Maximum Turbo Frequency:         3900 MHz
Uncore Minimum Frequency:            2400 MHz
Uncore Maximum Frequency:            2400 MHz
L2 Cache:                            24 x 1024 KB
L3 Cache:                            36608 KB
Hyper-threading:                     Enabled
Microcode Update Revision:           0x05003604
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
Platform Info:                       0x80070A2CF2810F00
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
CAPID6:                              0x0FFDFF7F
CAPID7:                              0x07FDFF77


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Memory: [MEM_0]                <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Number of DIMM(s):                   6
Number of Active Channel(s):         6
DRAM Power Meter Disabled:           0
DRAM RAPL Disabled:                  0
DRAM TDP Power:                      Min = 4.5 W, Max = 27.8 W, Time = 32.00 sec
DRAM / NVDIMM Info:
  MC 0, Chnl 0, Slot 0:              tempLo: 80 C, tempMid: 93 C, tempHi: 100 C
  MC 0, Chnl 1, Slot 0:              tempLo: 80 C, tempMid: 93 C, tempHi: 100 C
  MC 0, Chnl 2, Slot 0:              tempLo: 80 C, tempMid: 93 C, tempHi: 100 C
  MC 1, Chnl 3, Slot 0:              tempLo: 80 C, tempMid: 93 C, tempHi: 100 C
  MC 1, Chnl 4, Slot 0:              tempLo: 80 C, tempMid: 93 C, tempHi: 100 C
  MC 1, Chnl 5, Slot 0:              tempLo: 80 C, tempMid: 93 C, tempHi: 100 C


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Platform Controller Hub: [PCH] <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
PCH Device ID:                       8086:A1C3 (LBG-4)
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

[08/27/24 22:40:52 UTC] PTU started.

Press <Ctrl-C> to stop.


CPU_0: [IDLE] CFreq=2293, UFreq=2400, Util=2.86, IPC=1.57, Temp=78, DTS=26, Power=80.2, Volt=0.758
CPU_0: [TESTCFG] TestSel=1 (TDP), CoreMask=0xFFFFFFFFFFFFFFFF, ThreadMask=0xFF, PwrLevel=TDP, Turbo=0
CPU_0: [RUNNING] CFreq=2295, UFreq=2400, Util=100.00, IPC=3.93, Temp=87, DTS=17, Power=163.0, Volt=0.753

```

## Checked the sensors, FAN rpms increased as expected with a rise in CPU resources and Temp.

```log
root@controller-0:/home/XXXXXX/ptu# ipmitool sensor| grep -e CPU -e DutyCycle -e Watts
02-CPU           | 58.000     | degrees C  | ok    | na        | na        | na        | na        | 70.000    | na
51-CPU 1 PkgTmp  | 93.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
Fan 1 DutyCycle  | 46.648     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 2 DutyCycle  | 46.648     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 3 DutyCycle  | 46.648     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 4 DutyCycle  | 46.648     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 5 DutyCycle  | 46.648     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 6 DutyCycle  | 46.648     | percent    | ok    | na        | na        | na        | na        | na        | na
PS 1 Input       | 210.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PS 2 Input       | 200.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
CPU Utilization  | 252.000    | percent    | ok    | na        | na        | na        | na        | na        | na
PS 1 Output      | 210.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PS 2 Output      | 200.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
CPU_Stat_C1      | 0x0        | discrete   | 0x8080| na        | na        | na        | na        | na        | na
root@controller-0:/home/XXXXXX/ptu#
```

### Success as we have observed thermals rising, FAN RPMS increasing, due to load generation on the cpu

## MEAKV-643
## Performance Test #2 
## Run Core IA/SSE with 100% power, and Turbo on
## ./ptat -ct 3 -cp 100 -b 1

## Sensors before run

```log
root@controller-0:/home/XXXXXX/ptu# ipmitool sensor| grep -e CPU -e DutyCycle -e Watts
02-CPU           | 47.000     | degrees C  | ok    | na        | na        | na        | na        | 70.000    | na
51-CPU 1 PkgTmp  | 81.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
Fan 1 DutyCycle  | 24.696     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 2 DutyCycle  | 24.696     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 3 DutyCycle  | 24.696     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 4 DutyCycle  | 24.696     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 5 DutyCycle  | 24.696     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 6 DutyCycle  | 24.696     | percent    | ok    | na        | na        | na        | na        | na        | na
PS 1 Input       | 160.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PS 2 Input       | 150.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
CPU Utilization  | 12.000     | percent    | ok    | na        | na        | na        | na        | na        | na
PS 1 Output      | 150.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PS 2 Output      | 150.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
CPU_Stat_C1      | 0x0        | discrete   | 0x8080| na        | na        | na        | na        | na        | na
root@controller-0:/home/XXXXXX/ptu#
```

## Initiate Load 

```log
root@controller-0:/home/XXXXXX/ptu# ./ptu -ct 3 -cp 100 -b 1

Command: ./ptu -ct 3 -cp 100 -b 1

Intel(R) Power Thermal Utility - Server Edition v2.3.1
Release Date: 12/04/2020
Copyright (C) 2020 Intel Corporation. All rights reserved.
Intel Confidential

/dev/ptusys: No such file or directory
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> System Info:                   <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Host Name:                           controller-0
Host IP:                             169.254.202.1
OS Name:                             Debian GNU/Linux 11 (bullseye) 11
Kernel Version:                      Linux 5.10.0-6-rt-amd64 #1 SMP PREEMPT_RT StarlingX Debian 5.10.177-1.stx.76 (2024-03-29
BIOS Version:                        HPE, H08, 09/14/2023
Processor(s):                        1 Processor(s) Installed.
DIMM(s):                             6 DIMM(s) Installed.
Total System Memory:                 93923 MB
Available System Memory:             46543 MB


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Processor: [CPU_0]             <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU ID:                              0x00050657 (Family 6 Model 55h Stepping 7)
CPU Brand Name:                      Intel(R) Xeon(R) Gold 6212U CPU @ 2.40GHz
CPU Code Name:                       Cascade Lake
CPU Type:                            Production Part
CPU Segment:                         Server
CPU PPIN:                            0x169B33BDA6E28B0C
CPU Base Frequency:                  1500 MHz
CPU Minimum Frequency:               1000 MHz
CPU Maximum Turbo Frequency:         3900 MHz
Uncore Minimum Frequency:            2400 MHz
Uncore Maximum Frequency:            2400 MHz
L2 Cache:                            24 x 1024 KB
L3 Cache:                            36608 KB
Hyper-threading:                     Enabled
Microcode Update Revision:           0x05003604
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
Platform Info:                       0x80070A2CF2810F00
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
CAPID6:                              0x0FFDFF7F
CAPID7:                              0x07FDFF77


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Memory: [MEM_0]                <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Number of DIMM(s):                   6
Number of Active Channel(s):         6
DRAM Power Meter Disabled:           0
DRAM RAPL Disabled:                  0
DRAM TDP Power:                      Min = 4.5 W, Max = 27.8 W, Time = 32.00 sec
DRAM / NVDIMM Info:
  MC 0, Chnl 0, Slot 0:              tempLo: 80 C, tempMid: 93 C, tempHi: 100 C
  MC 0, Chnl 1, Slot 0:              tempLo: 80 C, tempMid: 93 C, tempHi: 100 C
  MC 0, Chnl 2, Slot 0:              tempLo: 80 C, tempMid: 93 C, tempHi: 100 C
  MC 1, Chnl 3, Slot 0:              tempLo: 80 C, tempMid: 93 C, tempHi: 100 C
  MC 1, Chnl 4, Slot 0:              tempLo: 80 C, tempMid: 93 C, tempHi: 100 C
  MC 1, Chnl 5, Slot 0:              tempLo: 80 C, tempMid: 93 C, tempHi: 100 C


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Platform Controller Hub: [PCH] <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
PCH Device ID:                       8086:A1C3 (LBG-4)
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

[08/27/24 23:53:57 UTC] PTU started.

Press <Ctrl-C> to stop.


CPU_0: [IDLE] CFreq=2303, UFreq=2400, Util=1.95, IPC=1.89, Temp=80, DTS=24, Power=81.4, Volt=0.755
CPU_0: [TESTCFG] TestSel=3 (Core IA/SSE), CoreMask=0xFFFFFFFFFFFFFFFF, ThreadMask=0xFF, PwrLevel=100, Turbo=1
CPU_0: [RUNNING] CFreq=2295, UFreq=2000, Util=100.00, IPC=3.91, Temp=93, DTS=11, Power=164.6, Volt=0.750

```

## ptu -mon

```log
rroot@controller-0:/home/XXXXXX/ptu# ./ptu -mon

Command: ./ptu -mon

Intel(R) Power Thermal Utility - Server Edition v2.3.1
Release Date: 12/04/2020
Copyright (C) 2020 Intel Corporation. All rights reserved.
Intel Confidential

/dev/ptusys: No such file or directory
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> System Info:                   <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Host Name:                           controller-0
Host IP:                             169.254.202.1
OS Name:                             Debian GNU/Linux 11 (bullseye) 11
Kernel Version:                      Linux 5.10.0-6-rt-amd64 #1 SMP PREEMPT_RT StarlingX Debian 5.10.177-1.stx.76 (2024-03-29
BIOS Version:                        HPE, H08, 09/14/2023
Processor(s):                        1 Processor(s) Installed.
DIMM(s):                             6 DIMM(s) Installed.
Total System Memory:                 93923 MB
Available System Memory:             46436 MB


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Processor: [CPU_0]             <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU ID:                              0x00050657 (Family 6 Model 55h Stepping 7)
CPU Brand Name:                      Intel(R) Xeon(R) Gold 6212U CPU @ 2.40GHz
CPU Code Name:                       Cascade Lake
CPU Type:                            Production Part
CPU Segment:                         Server
CPU PPIN:                            0x169B33BDA6E28B0C
CPU Base Frequency:                  1500 MHz
CPU Minimum Frequency:               1000 MHz
CPU Maximum Turbo Frequency:         3900 MHz
Uncore Minimum Frequency:            2400 MHz
Uncore Maximum Frequency:            2400 MHz
L2 Cache:                            24 x 1024 KB
L3 Cache:                            36608 KB
Hyper-threading:                     Enabled
Microcode Update Revision:           0x05003604
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
Platform Info:                       0x80070A2CF2810F00
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
CAPID6:                              0x0FFDFF7F
CAPID7:                              0x07FDFF77


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Memory: [MEM_0]                <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Number of DIMM(s):                   6
Number of Active Channel(s):         6
DRAM Power Meter Disabled:           0
DRAM RAPL Disabled:                  0
DRAM TDP Power:                      Min = 4.5 W, Max = 27.8 W, Time = 32.00 sec
DRAM / NVDIMM Info:
  MC 0, Chnl 0, Slot 0:              tempLo: 80 C, tempMid: 93 C, tempHi: 100 C
  MC 0, Chnl 1, Slot 0:              tempLo: 80 C, tempMid: 93 C, tempHi: 100 C
  MC 0, Chnl 2, Slot 0:              tempLo: 80 C, tempMid: 93 C, tempHi: 100 C
  MC 1, Chnl 3, Slot 0:              tempLo: 80 C, tempMid: 93 C, tempHi: 100 C
  MC 1, Chnl 4, Slot 0:              tempLo: 80 C, tempMid: 93 C, tempHi: 100 C
  MC 1, Chnl 5, Slot 0:              tempLo: 80 C, tempMid: 93 C, tempHi: 100 C


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Platform Controller Hub: [PCH] <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
PCH Device ID:                       8086:A1C3 (LBG-4)
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

[08/27/24 23:55:13 UTC] PTU started.

Press <Ctrl-C> to stop.


 Index Device Cor Thr CFreq UFreq   Util  IPC     C0     C1     C6    PC2    PC6 MC Ch Sl  Temp DTS  Power  Volt TStat TLog #TL TMargin
     0   CPU0   -   -  2295  1900 100.00 3.91  99.76   0.24   0.00   0.00   0.00  -  -  -    94  10 164.53 0.755   0x0  0x0   0   6.949
     0   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    44   -   0.00     -     -  0x0   -       -
     1   CPU0   -   -  2293  2000 100.00 3.91  99.72   0.28   0.00   0.00   0.00  -  -  -    94  10 164.45 0.756   0x0  0x0   0   6.855
     1   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    44   -   0.00     -     -  0x0   -       -
     2   CPU0   -   -  2296  1900 100.00 3.87  99.51   0.49   0.00   0.00   0.00  -  -  -    94  10 164.50 0.756   0x0  0x0   0   6.801
     2   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    44   -   0.00     -     -  0x0   -       -
     3   CPU0   -   -  2295  1900 100.00 3.91  99.66   0.34   0.00   0.00   0.00  -  -  -    94  10 164.61 0.755   0x0  0x0   0   6.766
     3   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    44   -   0.00     -     -  0x0   -       -
     4   CPU0   -   -  2295  2000 100.00 3.93  99.84   0.16   0.00   0.00   0.00  -  -  -    94  10 164.55 0.755   0x0  0x0   0   6.648
     4   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    44   -   0.00     -     -  0x0   -       -
     5   CPU0   -   -  2295  2000 100.00 3.92  99.64   0.36   0.00   0.00   0.00  -  -  -    94  10 164.44 0.755   0x0  0x0   0   6.746
     5   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    44   -   0.00     -     -  0x0   -       -
     6   CPU0   -   -  2293  2000 100.00 3.89  99.64   0.36   0.00   0.00   0.00  -  -  -    94  10 164.58 0.755   0x0  0x0   0   6.738
     6   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    44   -   0.00     -     -  0x0   -       -
     7   CPU0   -   -  2296  2000 100.00 3.89  99.52   0.48   0.00   0.00   0.00  -  -  -    94  10 164.54 0.755   0x0  0x0   0   6.711
     7   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    44   -   0.00     -     -  0x0   -       -
     8   CPU0   -   -  2295  1900 100.00 3.93  99.83   0.17   0.00   0.00   0.00  -  -  -    94  10 164.56 0.755   0x0  0x0   0   6.605
     8   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    44   -   0.00     -     -  0x0   -       -
     9   CPU0   -   -  2295  1900 100.00 3.91  99.56   0.44   0.00   0.00   0.00  -  -  -    95   9 155.73 0.755   0x0  0x0   0   6.715
     9   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    44   -   0.00     -     -  0x0   -       -
    10   CPU0   -   -  2294  2000 100.00 3.88  99.51   0.49   0.00   0.00   0.00  -  -  -    94  10 173.24 0.756   0x0  0x0   0   6.652
    10   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    44   -   0.00     -     -  0x0   -       -
    11   CPU0   -   -  2295  2000 100.00 3.89  99.52   0.48   0.00   0.00   0.00  -  -  -    94  10 164.57 0.755   0x0  0x0   0   6.730
    11   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    44   -   0.00     -     -  0x0   -       -
    12   CPU0   -   -  2295  2000 100.00 3.88  99.58   0.42   0.00   0.00   0.00  -  -  -    94  10 164.60 0.756   0x0  0x0   0   6.621
    12   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    44   -   0.00     -     -  0x0   -       -
    13   CPU0   -   -  2294  1900 100.00 3.89  99.52   0.48   0.00   0.00   0.00  -  -  -    94  10 164.38 0.756   0x0  0x0   0   6.723
    13   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    44   -   0.00     -     -  0x0   -       -
    14   CPU0   -   -  2295  1900 100.00 3.88  99.46   0.54   0.00   0.00   0.00  -  -  -    95   9 164.57 0.755   0x0  0x0   0   6.707
    14   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    44   -   0.00     -     -  0x0   -       -
    15   CPU0   -   -  2294  2000 100.00 3.88  99.58   0.42   0.00   0.00   0.00  -  -  -    94  10 164.48 0.756   0x0  0x0   0   6.621
    15   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    44   -   0.00     -     -  0x0   -       -
    16   CPU0   -   -  2293  2000 100.00 3.89  99.51   0.49   0.00   0.00   0.00  -  -  -    94  10 164.62 0.755   0x0  0x0   0   6.641
    16   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    44   -   0.00     -     -  0x0   -       -
    17   CPU0   -   -  2298  2000 100.00 3.90  99.63   0.37   0.00   0.00   0.00  -  -  -    94  10 164.42 0.755   0x0  0x0   0   6.660
    17   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    44   -   0.00     -     -  0x0   -       -
    18   CPU0   -   -  2295  1900 100.00 3.90  99.67   0.33   0.00   0.00   0.00  -  -  -    94  10 164.68 0.755   0x0  0x0   0   6.648
    18   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    44   -   0.00     -     -  0x0   -       -
    19   CPU0   -   -  2292  2000 100.00 3.90  99.54   0.46   0.00   0.00   0.00  -  -  -    94  10 164.50 0.755   0x0  0x0   0   6.648
    19   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    44   -   0.00     -     -  0x0   -       -
    20   CPU0   -   -  2297  2000 100.00 3.91  99.60   0.40   0.00   0.00   0.00  -  -  -    94  10 164.52 0.756   0x0  0x0   0   6.664
    20   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    44   -   0.00     -     -  0x0   -       -
    21   CPU0   -   -  2295  2000 100.00 3.89  99.57   0.43   0.00   0.00   0.00  -  -  -    94  10 164.52 0.756   0x0  0x0   0   6.672
    21   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    44   -   0.00     -     -  0x0   -       -
    22   CPU0   -   -  2293  2000 100.00 3.89  99.56   0.44   0.00   0.00   0.00  -  -  -    94  10 164.40 0.755   0x0  0x0   0   6.660
    22   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    44   -   0.00     -     -  0x0   -       -
    23   CPU0   -   -  2295  1900 100.00 3.89  99.54   0.46   0.00   0.00   0.00  -  -  -    94  10 164.64 0.755   0x0  0x0   0   6.629
    23   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    44   -   0.00     -     -  0x0   -       -
    24   CPU0   -   -  2295  2000 100.00 3.89  99.55   0.45   0.00   0.00   0.00  -  -  -    95   9 164.55 0.755   0x0  0x0   0   6.652
    24   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    44   -   0.00     -     -  0x0   -       -
    25   CPU0   -   -  2295  2000 100.00 3.87  99.54   0.46   0.00   0.00   0.00  -  -  -    94  10 164.45 0.755   0x0  0x0   0   6.559
    25   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    44   -   0.00     -     -  0x0   -       -
    26   CPU0   -   -  2294  2000 100.00 3.85  99.50   0.50   0.00   0.00   0.00  -  -  -    94  10 164.52 0.756   0x0  0x0   0   6.691
    26   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    44   -   0.00     -     -  0x0   -       -
^C
[08/27/24 23:55:44 UTC] PTU stopped.

root@controller-0:/home/XXXXXX/ptu#
```


## Sensors after load ~2-3mins after

```log
root@controller-0:/home/XXXXXX/ptu# ipmitool sensor| grep -e CPU -e DutyCycle -e Watts
02-CPU           | 58.000     | degrees C  | ok    | na        | na        | na        | na        | 70.000    | na
51-CPU 1 PkgTmp  | 93.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
Fan 1 DutyCycle  | 44.688     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 2 DutyCycle  | 44.688     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 3 DutyCycle  | 44.688     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 4 DutyCycle  | 44.688     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 5 DutyCycle  | 44.688     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 6 DutyCycle  | 44.688     | percent    | ok    | na        | na        | na        | na        | na        | na
PS 1 Input       | 200.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PS 2 Input       | 190.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
CPU Utilization  | 252.000    | percent    | ok    | na        | na        | na        | na        | na        | na
PS 1 Output      | 200.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PS 2 Output      | 190.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
CPU_Stat_C1      | 0x0        | discrete   | 0x8080| na        | na        | na        | na        | na        | na
```

## Test is success, observed temps rise fans increased to cool as expected

## MEAKV-644
## Performance test PTU 3 - Core AVX2 with Turbo - MEAKV-644
## Run Core Intel® AVX-2 with power level 100% and Turbo on.
## sudo ./ptat -ct 4 -cp 100 -b 1

## Check sensors bofore starting load

```log
root@controller-0:/home/XXXXXX/ptu# ipmitool sensor| grep -e CPU -e DutyCycle -e Watts
02-CPU           | 46.000     | degrees C  | ok    | na        | na        | na        | na        | 70.000    | na
51-CPU 1 PkgTmp  | 81.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
Fan 1 DutyCycle  | 26.656     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 2 DutyCycle  | 26.656     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 3 DutyCycle  | 26.656     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 4 DutyCycle  | 26.656     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 5 DutyCycle  | 26.656     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 6 DutyCycle  | 26.656     | percent    | ok    | na        | na        | na        | na        | na        | na
PS 1 Input       | 150.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PS 2 Input       | 150.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
CPU Utilization  | 5.000      | percent    | ok    | na        | na        | na        | na        | na        | na
PS 1 Output      | 150.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PS 2 Output      | 150.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
CPU_Stat_C1      | 0x0        | discrete   | 0x8080| na        | na        | na        | na        | na        | na
root@controller-0:/home/XXXXXX/ptu#
```

## load Intiated

```log
root@controller-0:/home/XXXXXX/ptu# ./ptu -ct 4 -cp 100 -b 1

Command: ./ptu -ct 4 -cp 100 -b 1

Intel(R) Power Thermal Utility - Server Edition v2.3.1
Release Date: 12/04/2020
Copyright (C) 2020 Intel Corporation. All rights reserved.
Intel Confidential

/dev/ptusys: No such file or directory
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> System Info:                   <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Host Name:                           controller-0
Host IP:                             169.254.202.1
OS Name:                             Debian GNU/Linux 11 (bullseye) 11
Kernel Version:                      Linux 5.10.0-6-rt-amd64 #1 SMP PREEMPT_RT StarlingX Debian 5.10.177-1.stx.76 (2024-03-29
BIOS Version:                        HPE, H08, 09/14/2023
Processor(s):                        1 Processor(s) Installed.
DIMM(s):                             6 DIMM(s) Installed.
Total System Memory:                 93923 MB
Available System Memory:             46258 MB


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Processor: [CPU_0]             <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU ID:                              0x00050657 (Family 6 Model 55h Stepping 7)
CPU Brand Name:                      Intel(R) Xeon(R) Gold 6212U CPU @ 2.40GHz
CPU Code Name:                       Cascade Lake
CPU Type:                            Production Part
CPU Segment:                         Server
CPU PPIN:                            0x169B33BDA6E28B0C
CPU Base Frequency:                  1500 MHz
CPU Minimum Frequency:               1000 MHz
CPU Maximum Turbo Frequency:         3900 MHz
Uncore Minimum Frequency:            2400 MHz
Uncore Maximum Frequency:            2400 MHz
L2 Cache:                            24 x 1024 KB
L3 Cache:                            36608 KB
Hyper-threading:                     Enabled
Microcode Update Revision:           0x05003604
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
Platform Info:                       0x80070A2CF2810F00
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
CAPID6:                              0x0FFDFF7F
CAPID7:                              0x07FDFF77


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Memory: [MEM_0]                <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Number of DIMM(s):                   6
Number of Active Channel(s):         6
DRAM Power Meter Disabled:           0
DRAM RAPL Disabled:                  0
DRAM TDP Power:                      Min = 4.5 W, Max = 27.8 W, Time = 32.00 sec
DRAM / NVDIMM Info:
  MC 0, Chnl 0, Slot 0:              tempLo: 80 C, tempMid: 93 C, tempHi: 100 C
  MC 0, Chnl 1, Slot 0:              tempLo: 80 C, tempMid: 93 C, tempHi: 100 C
  MC 0, Chnl 2, Slot 0:              tempLo: 80 C, tempMid: 93 C, tempHi: 100 C
  MC 1, Chnl 3, Slot 0:              tempLo: 80 C, tempMid: 93 C, tempHi: 100 C
  MC 1, Chnl 4, Slot 0:              tempLo: 80 C, tempMid: 93 C, tempHi: 100 C
  MC 1, Chnl 5, Slot 0:              tempLo: 80 C, tempMid: 93 C, tempHi: 100 C


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Platform Controller Hub: [PCH] <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
PCH Device ID:                       8086:A1C3 (LBG-4)
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

[08/28/24 00:00:30 UTC] PTU started.

Press <Ctrl-C> to stop.


CPU_0: [IDLE] CFreq=2292, UFreq=2400, Util=2.38, IPC=1.33, Temp=82, DTS=22, Power=81.4, Volt=0.756
CPU_0: [TESTCFG] TestSel=4 (Core AVX2), CoreMask=0xFFFFFFFFFFFFFFFF, ThreadMask=0xFF, PwrLevel=100, Turbo=1
CPU_0: [RUNNING] CFreq=2046, UFreq=1600, Util=100.00, IPC=3.88, Temp=91, DTS=13, Power=164.6, Volt=0.729

```

## ptu -mon

```log
root@controller-0:/home/XXXXXX/ptu# ./ptu -mon

Command: ./ptu -mon

Intel(R) Power Thermal Utility - Server Edition v2.3.1
Release Date: 12/04/2020
Copyright (C) 2020 Intel Corporation. All rights reserved.
Intel Confidential

/dev/ptusys: No such file or directory
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> System Info:                   <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Host Name:                           controller-0
Host IP:                             169.254.202.1
OS Name:                             Debian GNU/Linux 11 (bullseye) 11
Kernel Version:                      Linux 5.10.0-6-rt-amd64 #1 SMP PREEMPT_RT StarlingX Debian 5.10.177-1.stx.76 (2024-03-29
BIOS Version:                        HPE, H08, 09/14/2023
Processor(s):                        1 Processor(s) Installed.
DIMM(s):                             6 DIMM(s) Installed.
Total System Memory:                 93923 MB
Available System Memory:             46249 MB


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Processor: [CPU_0]             <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU ID:                              0x00050657 (Family 6 Model 55h Stepping 7)
CPU Brand Name:                      Intel(R) Xeon(R) Gold 6212U CPU @ 2.40GHz
CPU Code Name:                       Cascade Lake
CPU Type:                            Production Part
CPU Segment:                         Server
CPU PPIN:                            0x169B33BDA6E28B0C
CPU Base Frequency:                  1500 MHz
CPU Minimum Frequency:               1000 MHz
CPU Maximum Turbo Frequency:         3900 MHz
Uncore Minimum Frequency:            2400 MHz
Uncore Maximum Frequency:            2400 MHz
L2 Cache:                            24 x 1024 KB
L3 Cache:                            36608 KB
Hyper-threading:                     Enabled
Microcode Update Revision:           0x05003604
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
Platform Info:                       0x80070A2CF2810F00
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
CAPID6:                              0x0FFDFF7F
CAPID7:                              0x07FDFF77


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Memory: [MEM_0]                <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Number of DIMM(s):                   6
Number of Active Channel(s):         6
DRAM Power Meter Disabled:           0
DRAM RAPL Disabled:                  0
DRAM TDP Power:                      Min = 4.5 W, Max = 27.8 W, Time = 32.00 sec
DRAM / NVDIMM Info:
  MC 0, Chnl 0, Slot 0:              tempLo: 80 C, tempMid: 93 C, tempHi: 100 C
  MC 0, Chnl 1, Slot 0:              tempLo: 80 C, tempMid: 93 C, tempHi: 100 C
  MC 0, Chnl 2, Slot 0:              tempLo: 80 C, tempMid: 93 C, tempHi: 100 C
  MC 1, Chnl 3, Slot 0:              tempLo: 80 C, tempMid: 93 C, tempHi: 100 C
  MC 1, Chnl 4, Slot 0:              tempLo: 80 C, tempMid: 93 C, tempHi: 100 C
  MC 1, Chnl 5, Slot 0:              tempLo: 80 C, tempMid: 93 C, tempHi: 100 C


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Platform Controller Hub: [PCH] <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
PCH Device ID:                       8086:A1C3 (LBG-4)
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

[08/28/24 00:00:45 UTC] PTU started.

Press <Ctrl-C> to stop.


 Index Device Cor Thr CFreq UFreq   Util  IPC     C0     C1     C6    PC2    PC6 MC Ch Sl  Temp DTS  Power  Volt TStat TLog #TL TMargin
     0   CPU0   -   -  2052  1600 100.00 3.89  99.05   0.95   0.00   0.00   0.00  -  -  -    91  13 164.61 0.740   0x0  0x0   0   7.383
     0   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    46   -   0.00     -     -  0x0   -       -
     1   CPU0   -   -  2049  1500 100.00 3.90  99.12   0.88   0.00   0.00   0.00  -  -  -    90  14 164.58 0.732   0x0  0x0   0   7.492
     1   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    46   -   0.00     -     -  0x0   -       -
     2   CPU0   -   -  2051  1500 100.00 3.89  99.01   0.99   0.00   0.00   0.00  -  -  -    90  14 164.49 0.740   0x0  0x0   0   7.594
     2   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    46   -   0.00     -     -  0x0   -       -
     3   CPU0   -   -  2050  1600 100.00 3.89  99.06   0.94   0.00   0.00   0.00  -  -  -    91  13 164.51 0.740   0x0  0x0   0   7.594
     3   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    46   -   0.00     -     -  0x0   -       -
     4   CPU0   -   -  2050  1600 100.00 3.89  99.07   0.93   0.00   0.00   0.00  -  -  -    91  13 164.55 0.740   0x0  0x0   0   7.566
     4   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    46   -   0.00     -     -  0x0   -       -
     5   CPU0   -   -  2048  1600 100.00 3.89  99.04   0.96   0.00   0.00   0.00  -  -  -    91  13 164.42 0.740   0x0  0x0   0   7.641
     5   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    46   -   0.00     -     -  0x0   -       -
     6   CPU0   -   -  2051  1600 100.00 3.86  99.07   0.93   0.00   0.00   0.00  -  -  -    91  13 164.63 0.732   0x0  0x0   0   7.676
     6   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    46   -   0.00     -     -  0x0   -       -
     7   CPU0   -   -  2049  1500 100.00 3.87  99.01   0.99   0.00   0.00   0.00  -  -  -    91  13 164.54 0.740   0x0  0x0   0   7.738
     7   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    46   -   0.00     -     -  0x0   -       -
     8   CPU0   -   -  2054  1600 100.00 3.87  99.12   0.88   0.00   0.00   0.00  -  -  -    91  13 164.51 0.731   0x0  0x0   0   7.848
     8   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    46   -   0.00     -     -  0x0   -       -
     9   CPU0   -   -  2048  1600 100.00 3.90  99.08   0.92   0.00   0.00   0.00  -  -  -    91  13 164.03 0.731   0x0  0x0   0   7.863
     9   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    46   -   0.00     -     -  0x0   -       -
    10   CPU0   -   -  2051  1600 100.00 3.87  99.11   0.89   0.00   0.00   0.00  -  -  -    91  13 165.01 0.731   0x0  0x0   0   7.820
    10   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    46   -   0.00     -     -  0x0   -       -
    11   CPU0   -   -  2051  1500  98.93 3.87  99.02   0.98   0.00   0.00   0.00  -  -  -    91  13 164.54 0.740   0x0  0x0   0   7.871
    11   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    46   -   0.00     -     -  0x0   -       -
    12   CPU0   -   -  2050  1600 100.00 3.87  99.08   0.92   0.00   0.00   0.00  -  -  -    91  13 164.43 0.740   0x0  0x0   0   7.883
    12   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    46   -   0.00     -     -  0x0   -       -
    13   CPU0   -   -  2051  1500 100.00 3.87  99.04   0.96   0.00   0.00   0.00  -  -  -    91  13 164.55 0.732   0x0  0x0   0   7.973
    13   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    46   -   0.00     -     -  0x0   -       -
    14   CPU0   -   -  2048  1600  98.83 3.87  99.04   0.96   0.00   0.00   0.00  -  -  -    91  13 164.59 0.732   0x0  0x0   0   8.090
    14   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    46   -   0.00     -     -  0x0   -       -
    15   CPU0   -   -  2049  1600 100.00 3.86  99.10   0.90   0.00   0.00   0.00  -  -  -    91  13 164.45 0.732   0x0  0x0   0   8.141
```

## check sensors after load 

```log
root@controller-0:/home/XXXXXX/ptu# ipmitool sensor| grep -e CPU -e DutyCycle -e Watts
02-CPU           | 59.000     | degrees C  | ok    | na        | na        | na        | na        | 70.000    | na
51-CPU 1 PkgTmp  | 94.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
Fan 1 DutyCycle  | 44.688     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 2 DutyCycle  | 44.688     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 3 DutyCycle  | 44.688     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 4 DutyCycle  | 44.688     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 5 DutyCycle  | 44.688     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 6 DutyCycle  | 44.688     | percent    | ok    | na        | na        | na        | na        | na        | na
PS 1 Input       | 210.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PS 2 Input       | 200.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
CPU Utilization  | 224.000    | percent    | ok    | na        | na        | na        | na        | na        | na
PS 1 Output      | 210.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PS 2 Output      | 190.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
CPU_Stat_C1      | 0x0        | discrete   | 0x8080| na        | na        | na        | na        | na        | na
root@controller-0:/home/XXXXXX/ptu#
```

## Observed temps raise, and fans increased.. 

## MEAKV-645
## PTU 4 - Core AVX512 with Turbo
## sudo ./ptat -ct 5 -cp 100 -b 1


## Sensors before load

```log
root@controller-0:/home/XXXXXX/ptu# ipmitool sensor| grep -e CPU -e DutyCycle -e Watts
02-CPU           | 47.000     | degrees C  | ok    | na        | na        | na        | na        | 70.000    | na
51-CPU 1 PkgTmp  | 82.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
Fan 1 DutyCycle  | 24.696     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 2 DutyCycle  | 24.696     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 3 DutyCycle  | 24.696     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 4 DutyCycle  | 24.696     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 5 DutyCycle  | 24.696     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 6 DutyCycle  | 24.696     | percent    | ok    | na        | na        | na        | na        | na        | na
PS 1 Input       | 150.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PS 2 Input       | 150.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
CPU Utilization  | 10.000     | percent    | ok    | na        | na        | na        | na        | na        | na
PS 1 Output      | 160.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PS 2 Output      | 150.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
CPU_Stat_C1      | 0x0        | discrete   | 0x8080| na        | na        | na        | na        | na        | na
root@controller-0:/home/XXXXXX/ptu#

```

## Initate load

```log
root@controller-0:/home/XXXXXX/ptu# ./ptu -ct 5 -cp 100 -b 1

Command: ./ptu -ct 5 -cp 100 -b 1

Intel(R) Power Thermal Utility - Server Edition v2.3.1
Release Date: 12/04/2020
Copyright (C) 2020 Intel Corporation. All rights reserved.
Intel Confidential

/dev/ptusys: No such file or directory
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> System Info:                   <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Host Name:                           controller-0
Host IP:                             169.254.202.1
OS Name:                             Debian GNU/Linux 11 (bullseye) 11
Kernel Version:                      Linux 5.10.0-6-rt-amd64 #1 SMP PREEMPT_RT StarlingX Debian 5.10.177-1.stx.76 (2024-03-29
BIOS Version:                        HPE, H08, 09/14/2023
Processor(s):                        1 Processor(s) Installed.
DIMM(s):                             6 DIMM(s) Installed.
Total System Memory:                 93923 MB
Available System Memory:             46293 MB


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Processor: [CPU_0]             <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU ID:                              0x00050657 (Family 6 Model 55h Stepping 7)
CPU Brand Name:                      Intel(R) Xeon(R) Gold 6212U CPU @ 2.40GHz
CPU Code Name:                       Cascade Lake
CPU Type:                            Production Part
CPU Segment:                         Server
CPU PPIN:                            0x169B33BDA6E28B0C
CPU Base Frequency:                  1500 MHz
CPU Minimum Frequency:               1000 MHz
CPU Maximum Turbo Frequency:         3900 MHz
Uncore Minimum Frequency:            2400 MHz
Uncore Maximum Frequency:            2400 MHz
L2 Cache:                            24 x 1024 KB
L3 Cache:                            36608 KB
Hyper-threading:                     Enabled
Microcode Update Revision:           0x05003604
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
Platform Info:                       0x80070A2CF2810F00
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
CAPID6:                              0x0FFDFF7F
CAPID7:                              0x07FDFF77


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Memory: [MEM_0]                <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Number of DIMM(s):                   6
Number of Active Channel(s):         6
DRAM Power Meter Disabled:           0
DRAM RAPL Disabled:                  0
DRAM TDP Power:                      Min = 4.5 W, Max = 27.8 W, Time = 32.00 sec
DRAM / NVDIMM Info:
  MC 0, Chnl 0, Slot 0:              tempLo: 80 C, tempMid: 93 C, tempHi: 100 C
  MC 0, Chnl 1, Slot 0:              tempLo: 80 C, tempMid: 93 C, tempHi: 100 C
  MC 0, Chnl 2, Slot 0:              tempLo: 80 C, tempMid: 93 C, tempHi: 100 C
  MC 1, Chnl 3, Slot 0:              tempLo: 80 C, tempMid: 93 C, tempHi: 100 C
  MC 1, Chnl 4, Slot 0:              tempLo: 80 C, tempMid: 93 C, tempHi: 100 C
  MC 1, Chnl 5, Slot 0:              tempLo: 80 C, tempMid: 93 C, tempHi: 100 C


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Platform Controller Hub: [PCH] <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
PCH Device ID:                       8086:A1C3 (LBG-4)
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

[08/28/24 00:07:11 UTC] PTU started.

Press <Ctrl-C> to stop.


CPU_0: [IDLE] CFreq=2296, UFreq=2400, Util=4.60, IPC=1.81, Temp=82, DTS=22, Power=83.3, Volt=0.755
CPU_0: [TESTCFG] TestSel=5 (Core AVX-512), CoreMask=0xFFFFFFFFFFFFFFFF, ThreadMask=0xFF, PwrLevel=100, Turbo=1
CPU_0: [RUNNING] CFreq=1530, UFreq=1200, Util=100.00, IPC=4.17, Temp=93, DTS=11, Power=164.0, Volt=0.678


```

## ptu -mon

```log
root@controller-0:/home/XXXXXX/ptu# ./ptu -mon

Command: ./ptu -mon

Intel(R) Power Thermal Utility - Server Edition v2.3.1
Release Date: 12/04/2020
Copyright (C) 2020 Intel Corporation. All rights reserved.
Intel Confidential

/dev/ptusys: No such file or directory
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> System Info:                   <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Host Name:                           controller-0
Host IP:                             169.254.202.1
OS Name:                             Debian GNU/Linux 11 (bullseye) 11
Kernel Version:                      Linux 5.10.0-6-rt-amd64 #1 SMP PREEMPT_RT StarlingX Debian 5.10.177-1.stx.76 (2024-03-29
BIOS Version:                        HPE, H08, 09/14/2023
Processor(s):                        1 Processor(s) Installed.
DIMM(s):                             6 DIMM(s) Installed.
Total System Memory:                 93923 MB
Available System Memory:             46309 MB


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Processor: [CPU_0]             <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU ID:                              0x00050657 (Family 6 Model 55h Stepping 7)
CPU Brand Name:                      Intel(R) Xeon(R) Gold 6212U CPU @ 2.40GHz
CPU Code Name:                       Cascade Lake
CPU Type:                            Production Part
CPU Segment:                         Server
CPU PPIN:                            0x169B33BDA6E28B0C
CPU Base Frequency:                  1500 MHz
CPU Minimum Frequency:               1000 MHz
CPU Maximum Turbo Frequency:         3900 MHz
Uncore Minimum Frequency:            2400 MHz
Uncore Maximum Frequency:            2400 MHz
L2 Cache:                            24 x 1024 KB
L3 Cache:                            36608 KB
Hyper-threading:                     Enabled
Microcode Update Revision:           0x05003604
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
Platform Info:                       0x80070A2CF2810F00
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
CAPID6:                              0x0FFDFF7F
CAPID7:                              0x07FDFF77


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Memory: [MEM_0]                <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Number of DIMM(s):                   6
Number of Active Channel(s):         6
DRAM Power Meter Disabled:           0
DRAM RAPL Disabled:                  0
DRAM TDP Power:                      Min = 4.5 W, Max = 27.8 W, Time = 32.00 sec
DRAM / NVDIMM Info:
  MC 0, Chnl 0, Slot 0:              tempLo: 80 C, tempMid: 93 C, tempHi: 100 C
  MC 0, Chnl 1, Slot 0:              tempLo: 80 C, tempMid: 93 C, tempHi: 100 C
  MC 0, Chnl 2, Slot 0:              tempLo: 80 C, tempMid: 93 C, tempHi: 100 C
  MC 1, Chnl 3, Slot 0:              tempLo: 80 C, tempMid: 93 C, tempHi: 100 C
  MC 1, Chnl 4, Slot 0:              tempLo: 80 C, tempMid: 93 C, tempHi: 100 C
  MC 1, Chnl 5, Slot 0:              tempLo: 80 C, tempMid: 93 C, tempHi: 100 C


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Platform Controller Hub: [PCH] <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
PCH Device ID:                       8086:A1C3 (LBG-4)
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

[08/28/24 00:07:57 UTC] PTU started.

Press <Ctrl-C> to stop.


 Index Device Cor Thr CFreq UFreq   Util  IPC     C0     C1     C6    PC2    PC6 MC Ch Sl  Temp DTS  Power  Volt TStat TLog #TL TMargin
     0   CPU0   -   -  1534  1300 100.00 4.16  99.09   0.91   0.00   0.00   0.00  -  -  -    92  12 164.55 0.690   0x0  0x0   0   7.863
     0   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    45   -   0.00     -     -  0x0   -       -
     1   CPU0   -   -  1538  1200 100.00 4.17  99.16   0.84   0.00   0.00   0.00  -  -  -    93  11 164.17 0.690   0x0  0x0   0   7.902
     1   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    45   -   0.00     -     -  0x0   -       -
     2   CPU0   -   -  1537  1200 100.00 4.16  99.16   0.84   0.00   0.00   0.00  -  -  -    92  12 164.83 0.699   0x0  0x0   0   7.902
     2   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    45   -   0.00     -     -  0x0   -       -
     3   CPU0   -   -  1538  1300 100.00 4.16  99.07   0.93   0.00   0.00   0.00  -  -  -    93  11 164.62 0.690   0x0  0x0   0   7.922
     3   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    45   -   0.00     -     -  0x0   -       -
     4   CPU0   -   -  1544  1300 100.00 4.15  99.04   0.96   0.00   0.00   0.00  -  -  -    93  11 164.50 0.699   0x0  0x0   0   8.008
     4   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    45   -   0.00     -     -  0x0   -       -
     5   CPU0   -   -  1548  1300 100.00 4.13  99.19   0.81   0.00   0.00   0.00  -  -  -    92  12 163.33 0.690   0x0  0x0   0   7.898
     5   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    45   -   0.00     -     -  0x0   -       -
     6   CPU0   -   -  1547  1200 100.00 4.16  99.06   0.94   0.00   0.00   0.00  -  -  -    92  12 166.05 0.689   0x0  0x0   0   7.832
     6   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    45   -   0.00     -     -  0x0   -       -
     7   CPU0   -   -  1535  1200 100.00 4.18  99.21   0.79   0.00   0.00   0.00  -  -  -    92  12 164.60 0.698   0x0  0x0   0   7.770
     7   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    45   -   0.00     -     -  0x0   -       -
     8   CPU0   -   -  1534  1200 100.00 4.18  99.23   0.77   0.00   0.00   0.00  -  -  -    93  11 164.50 0.699   0x0  0x0   0   7.711
     8   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    45   -   0.00     -     -  0x0   -       -
     9   CPU0   -   -  1534  1200 100.00 4.17  99.15   0.85   0.00   0.00   0.00  -  -  -    93  11 164.44 0.689   0x0  0x0   0   7.641
     9   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    45   -   0.00     -     -  0x0   -       -
    10   CPU0   -   -  1536  1300 100.00 4.15  99.00   1.00   0.00   0.00   0.00  -  -  -    93  11 157.88 0.690   0x0  0x0   0   7.586
    10   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    45   -   0.00     -     -  0x0   -       -
    11   CPU0   -   -  1534  1200 100.00 4.17  99.42   0.58   0.00   0.00   0.00  -  -  -    93  11 170.71 0.689   0x0  0x0   0   7.504
    11   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    45   -   0.00     -     -  0x0   -       -
    12   CPU0   -   -  1533  1300 100.00 4.18  99.22   0.78   0.00   0.00   0.00  -  -  -    93  11 164.40 0.689   0x0  0x0   0   7.434
    12   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    45   -   0.00     -     -  0x0   -       -
    13   CPU0   -   -  1531  1200 100.00 4.17  99.26   0.74   0.00   0.00   0.00  -  -  -    93  11 164.56 0.689   0x0  0x0   0   7.387
    13   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    45   -   0.00     -     -  0x0   -       -
    14   CPU0   -   -  1525  1300 100.00 4.22  99.43   0.57   0.00   0.00   0.00  -  -  -    93  11 164.58 0.688   0x0  0x0   0   7.410
    14   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    45   -   0.00     -     -  0x0   -       -
    15   CPU0   -   -  1527  1200 100.00 4.18  99.29   0.71   0.00   0.00   0.00  -  -  -    93  11 157.30 0.689   0x0  0x0   0   7.332
    15   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    45   -   0.00     -     -  0x0   -       -
    16   CPU0   -   -  1535  1200 100.00 4.18  99.20   0.80   0.00   0.00   0.00  -  -  -    93  11 171.08 0.697   0x0  0x0   0   7.305
    16   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    45   -   0.00     -     -  0x0   -       -
    17   CPU0   -   -  1531  1200 100.00 4.19  99.34   0.66   0.00   0.00   0.00  -  -  -    94  10 164.43 0.698   0x0  0x0   0   7.086
    17   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    45   -   0.00     -     -  0x0   -       -
    18   CPU0   -   -  1533  1300 100.00 4.17  99.10   0.90   0.00   0.00   0.00  -  -  -    94  10 158.26 0.689   0x0  0x0   0   6.992
    18   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    45   -   0.00     -     -  0x0   -       -
    19   CPU0   -   -  1531  1300 100.00 4.19  99.26   0.74   0.00   0.00   0.00  -  -  -    94  10 169.79 0.689   0x0  0x0   0   6.930
    19   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    45   -   0.00     -     -  0x0   -       -
    20   CPU0   -   -  1530  1200 100.00 4.18  99.26   0.74   0.00   0.00   0.00  -  -  -    94  10 164.49 0.688   0x0  0x0   0   6.777
    20   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    45   -   0.00     -     -  0x0   -       -
    21   CPU0   -   -  1531  1300 100.00 4.17  99.21   0.79   0.00   0.00   0.00  -  -  -    94  10 164.52 0.689   0x0  0x0   0   6.758
```

## check sensors

```log
root@controller-0:/home/XXXXXX/ptu# ipmitool sensor| grep -e CPU -e DutyCycle -e Watts
02-CPU           | 60.000     | degrees C  | ok    | na        | na        | na        | na        | 70.000    | na
51-CPU 1 PkgTmp  | 94.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
Fan 1 DutyCycle  | 45.864     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 2 DutyCycle  | 45.864     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 3 DutyCycle  | 45.864     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 4 DutyCycle  | 45.864     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 5 DutyCycle  | 45.864     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 6 DutyCycle  | 45.864     | percent    | ok    | na        | na        | na        | na        | na        | na
PS 1 Input       | 210.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PS 2 Input       | 190.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
CPU Utilization  | 168.000    | percent    | ok    | na        | na        | na        | na        | na        | na
PS 1 Output      | 200.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PS 2 Output      | 190.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
CPU_Stat_C1      | 0x0        | discrete   | 0x8080| na        | na        | na        | na        | na        | na
root@controller-0:/home/XXXXXX/ptu#
```

## Success, was able to observe temp rise, then fans increasing as load was started


## MEAKV-646 
## PTU 5 - Turbo Test
## sudo ./ptat -ct 8 -b 1

## sensors before load

```log
root@controller-0:/home/XXXXXX/ptu# ipmitool sensor| grep -e CPU -e DutyCycle -e Watts
02-CPU           | 44.000     | degrees C  | ok    | na        | na        | na        | na        | 70.000    | na
51-CPU 1 PkgTmp  | 80.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
Fan 1 DutyCycle  | 24.696     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 2 DutyCycle  | 24.696     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 3 DutyCycle  | 24.696     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 4 DutyCycle  | 24.696     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 5 DutyCycle  | 24.696     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 6 DutyCycle  | 24.696     | percent    | ok    | na        | na        | na        | na        | na        | na
PS 1 Input       | 150.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PS 2 Input       | 140.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
CPU Utilization  | 10.000     | percent    | ok    | na        | na        | na        | na        | na        | na
PS 1 Output      | 210.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PS 2 Output      | 190.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
CPU_Stat_C1      | 0x0        | discrete   | 0x8080| na        | na        | na        | na        | na        | na
root@controller-0:/home/XXXXXX/ptu#
```

## Initiating load

```log

root@controller-0:/home/XXXXXX/ptu# ./ptu -ct 8 -b 1

Command: ./ptu -ct 8 -b 1

Intel(R) Power Thermal Utility - Server Edition v2.3.1
Release Date: 12/04/2020
Copyright (C) 2020 Intel Corporation. All rights reserved.
Intel Confidential

/dev/ptusys: No such file or directory
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> System Info:                   <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Host Name:                           controller-0
Host IP:                             169.254.202.1
OS Name:                             Debian GNU/Linux 11 (bullseye) 11
Kernel Version:                      Linux 5.10.0-6-rt-amd64 #1 SMP PREEMPT_RT StarlingX Debian 5.10.177-1.stx.76 (2024-03-29
BIOS Version:                        HPE, H08, 09/14/2023
Processor(s):                        1 Processor(s) Installed.
DIMM(s):                             6 DIMM(s) Installed.
Total System Memory:                 93923 MB
Available System Memory:             46437 MB


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Processor: [CPU_0]             <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU ID:                              0x00050657 (Family 6 Model 55h Stepping 7)
CPU Brand Name:                      Intel(R) Xeon(R) Gold 6212U CPU @ 2.40GHz
CPU Code Name:                       Cascade Lake
CPU Type:                            Production Part
CPU Segment:                         Server
CPU PPIN:                            0x169B33BDA6E28B0C
CPU Base Frequency:                  1500 MHz
CPU Minimum Frequency:               1000 MHz
CPU Maximum Turbo Frequency:         3900 MHz
Uncore Minimum Frequency:            2400 MHz
Uncore Maximum Frequency:            2400 MHz
L2 Cache:                            24 x 1024 KB
L3 Cache:                            36608 KB
Hyper-threading:                     Enabled
Microcode Update Revision:           0x05003604
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
Platform Info:                       0x80070A2CF2810F00
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
CAPID6:                              0x0FFDFF7F
CAPID7:                              0x07FDFF77


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Memory: [MEM_0]                <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Number of DIMM(s):                   6
Number of Active Channel(s):         6
DRAM Power Meter Disabled:           0
DRAM RAPL Disabled:                  0
DRAM TDP Power:                      Min = 4.5 W, Max = 27.8 W, Time = 32.00 sec
DRAM / NVDIMM Info:
  MC 0, Chnl 0, Slot 0:              tempLo: 80 C, tempMid: 93 C, tempHi: 100 C
  MC 0, Chnl 1, Slot 0:              tempLo: 80 C, tempMid: 93 C, tempHi: 100 C
  MC 0, Chnl 2, Slot 0:              tempLo: 80 C, tempMid: 93 C, tempHi: 100 C
  MC 1, Chnl 3, Slot 0:              tempLo: 80 C, tempMid: 93 C, tempHi: 100 C
  MC 1, Chnl 4, Slot 0:              tempLo: 80 C, tempMid: 93 C, tempHi: 100 C
  MC 1, Chnl 5, Slot 0:              tempLo: 80 C, tempMid: 93 C, tempHi: 100 C


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Platform Controller Hub: [PCH] <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
PCH Device ID:                       8086:A1C3 (LBG-4)
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

[08/28/24 00:11:01 UTC] PTU started.

Press <Ctrl-C> to stop.


CPU_0: [IDLE] CFreq=2303, UFreq=2400, Util=2.94, IPC=1.13, Temp=82, DTS=22, Power=82.1, Volt=0.755

### TURBO is enabled ###

Instr   CPU #Cores CFreq(act) CFreq(exp) UFreq Power TDP  Temp Volt
IA/SSE  0   1      2.3        3.9        2.4   82.6  165  82   0.758
IA/SSE  0   2      2.3        3.9        2.4   85.0  165  83   0.758
IA/SSE  0   3      2.3        3.7        2.4   88.2  165  83   0.755
IA/SSE  0   4      2.3        3.7        2.4   90.2  165  83   0.754
IA/SSE  0   5      2.3        3.6        2.4   92.1  165  84   0.754
IA/SSE  0   6      2.3        3.6        2.4   94.9  165  83   0.753
IA/SSE  0   7      2.3        3.6        2.4   97.1  165  84   0.754
IA/SSE  0   8      2.3        3.6        2.4   99.2  165  84   0.754
IA/SSE  0   9      2.3        3.6        2.4   101.1 165  84   0.754
IA/SSE  0   10     2.3        3.6        2.4   101.0 165  85   0.754
IA/SSE  0   11     2.3        3.6        2.4   103.1 165  85   0.754
IA/SSE  0   12     2.3        3.6        2.4   104.5 165  86   0.753
IA/SSE  0   13     2.3        3.6        2.4   108.7 165  86   0.753
IA/SSE  0   14     2.3        3.6        2.4   111.1 165  86   0.753
IA/SSE  0   15     2.3        3.6        2.4   112.8 165  87   0.753
IA/SSE  0   16     2.3        3.6        2.4   110.7 165  87   0.753
IA/SSE  0   17     2.3        3.3        2.4   117.7 165  88   0.752
IA/SSE  0   18     2.3        3.3        2.4   120.5 165  89   0.752
IA/SSE  0   19     2.3        3.3        2.4   122.2 165  89   0.751
IA/SSE  0   20     2.3        3.3        2.4   124.5 165  90   0.751
IA/SSE  0   21     2.3        3.1        2.4   127.1 165  90   0.751
IA/SSE  0   22     2.3        3.1        2.4   128.2 165  90   0.751
IA/SSE  0   23     2.3        3.1        2.4   129.9 165  90   0.751
IA/SSE  0   24     2.3        3.1        2.4   131.7 165  89   0.751

```

## ptu -mon

```log
root@controller-0:/home/XXXXXX/ptu# ./ptu -mon

Command: ./ptu -mon

Intel(R) Power Thermal Utility - Server Edition v2.3.1
Release Date: 12/04/2020
Copyright (C) 2020 Intel Corporation. All rights reserved.
Intel Confidential

/dev/ptusys: No such file or directory
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> System Info:                   <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Host Name:                           controller-0
Host IP:                             169.254.202.1
OS Name:                             Debian GNU/Linux 11 (bullseye) 11
Kernel Version:                      Linux 5.10.0-6-rt-amd64 #1 SMP PREEMPT_RT StarlingX Debian 5.10.177-1.stx.76 (2024-03-29
BIOS Version:                        HPE, H08, 09/14/2023
Processor(s):                        1 Processor(s) Installed.
DIMM(s):                             6 DIMM(s) Installed.
Total System Memory:                 93923 MB
Available System Memory:             45974 MB


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Processor: [CPU_0]             <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
CPU ID:                              0x00050657 (Family 6 Model 55h Stepping 7)
CPU Brand Name:                      Intel(R) Xeon(R) Gold 6212U CPU @ 2.40GHz
CPU Code Name:                       Cascade Lake
CPU Type:                            Production Part
CPU Segment:                         Server
CPU PPIN:                            0x169B33BDA6E28B0C
CPU Base Frequency:                  1500 MHz
CPU Minimum Frequency:               1000 MHz
CPU Maximum Turbo Frequency:         3900 MHz
Uncore Minimum Frequency:            2400 MHz
Uncore Maximum Frequency:            2400 MHz
L2 Cache:                            24 x 1024 KB
L3 Cache:                            36608 KB
Hyper-threading:                     Enabled
Microcode Update Revision:           0x05003604
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
Platform Info:                       0x80070A2CF2810F00
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
CAPID6:                              0x0FFDFF7F
CAPID7:                              0x07FDFF77


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Memory: [MEM_0]                <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
Number of DIMM(s):                   6
Number of Active Channel(s):         6
DRAM Power Meter Disabled:           0
DRAM RAPL Disabled:                  0
DRAM TDP Power:                      Min = 4.5 W, Max = 27.8 W, Time = 32.00 sec
DRAM / NVDIMM Info:
  MC 0, Chnl 0, Slot 0:              tempLo: 80 C, tempMid: 93 C, tempHi: 100 C
  MC 0, Chnl 1, Slot 0:              tempLo: 80 C, tempMid: 93 C, tempHi: 100 C
  MC 0, Chnl 2, Slot 0:              tempLo: 80 C, tempMid: 93 C, tempHi: 100 C
  MC 1, Chnl 3, Slot 0:              tempLo: 80 C, tempMid: 93 C, tempHi: 100 C
  MC 1, Chnl 4, Slot 0:              tempLo: 80 C, tempMid: 93 C, tempHi: 100 C
  MC 1, Chnl 5, Slot 0:              tempLo: 80 C, tempMid: 93 C, tempHi: 100 C


>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Platform Controller Hub: [PCH] <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
PCH Device ID:                       8086:A1C3 (LBG-4)
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

[08/28/24 00:14:23 UTC] PTU started.

Press <Ctrl-C> to stop.


 Index Device Cor Thr CFreq UFreq   Util  IPC     C0     C1     C6    PC2    PC6 MC Ch Sl  Temp DTS  Power  Volt TStat TLog #TL TMargin
     0   CPU0   -   -  2296  2400   4.49 2.26   4.50  95.50   0.00   0.00   0.00  -  -  -    84  20  84.19 0.757   0x0  0x0   0   9.641
     0   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -   0.00     -     -  0x0   -       -
     1   CPU0   -   -  2296  2400   4.14 2.21   4.13  95.87   0.00   0.00   0.00  -  -  -    84  20  84.54 0.757   0x0  0x0   0   9.672
     1   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -   0.00     -     -  0x0   -       -
     2   CPU0   -   -  2287  2400   3.73 0.92   3.73  96.27   0.00   0.00   0.00  -  -  -    84  20  83.52 0.757   0x0  0x0   0   9.828
     2   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -   0.00     -     -  0x0   -       -
     3   CPU0   -   -  2295  2400   4.42 1.73   4.42  95.58   0.00   0.00   0.00  -  -  -    84  20  84.36 0.757   0x0  0x0   0   9.672
     3   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -   0.00     -     -  0x0   -       -
     4   CPU0   -   -  2296  2400   5.24 1.66   5.24  94.76   0.00   0.00   0.00  -  -  -    84  20  85.07 0.757   0x0  0x0   0   9.781
     4   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -   0.00     -     -  0x0   -       -
     5   CPU0   -   -  2304  2400   3.60 0.70   3.60  96.40   0.00   0.00   0.00  -  -  -    84  20  83.29 0.757   0x0  0x0   0  10.078
     5   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -   0.00     -     -  0x0   -       -
     6   CPU0   -   -  2290  2400   3.11 2.19   3.11  96.89   0.00   0.00   0.00  -  -  -    83  21  83.58 0.757   0x0  0x0   0  10.281
     6   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -   0.00     -     -  0x0   -       -
     7   CPU0   -   -  2297  2400   3.54 1.40   3.54  96.46   0.00   0.00   0.00  -  -  -    83  21  83.59 0.757   0x0  0x0   0  10.906
     7   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -   0.00     -     -  0x0   -       -
     8   CPU0   -   -  2289  2400   2.42 1.12   2.42  97.58   0.00   0.00   0.00  -  -  -    84  20  82.74 0.757   0x0  0x0   0  10.625
     8   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -   0.00     -     -  0x0   -       -
     9   CPU0   -   -  2299  2400   1.94 1.24   1.94  98.06   0.00   0.00   0.00  -  -  -    84  20  82.20 0.757   0x0  0x0   0  11.250
     9   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -   0.00     -     -  0x0   -       -
    10   CPU0   -   -  2295  2400   4.06 2.24   4.05  95.95   0.00   0.00   0.00  -  -  -    81  23  84.12 0.758   0x0  0x0   0  10.953
    10   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -   0.00     -     -  0x0   -       -
    11   CPU0   -   -  2292  2400   1.57 1.94   1.58  98.42   0.00   0.00   0.00  -  -  -    81  23  81.83 0.758   0x0  0x0   0  12.109
    11   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -   0.00     -     -  0x0   -       -
    12   CPU0   -   -  2296  2400   1.80 2.43   1.80  98.20   0.00   0.00   0.00  -  -  -    81  23  81.98 0.758   0x0  0x0   0  11.594
    12   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -   0.00     -     -  0x0   -       -
    13   CPU0   -   -  2296  2400   1.07 1.67   1.07  98.93   0.00   0.00   0.00  -  -  -    82  22  81.25 0.758   0x0  0x0   0  12.406
    13   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -   0.00     -     -  0x0   -       -
    14   CPU0   -   -  2294  2400   2.39 1.52   2.39  97.61   0.00   0.00   0.00  -  -  -    81  23  82.74 0.758   0x0  0x0   0  12.625
    14   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -   0.00     -     -  0x0   -       -
    15   CPU0   -   -  2294  2400   2.71 1.17   2.71  97.29   0.00   0.00   0.00  -  -  -    84  20  82.74 0.757   0x0  0x0   0  12.391
    15   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -   0.00     -     -  0x0   -       -
    16   CPU0   -   -  2291  2400   4.69 2.27   4.70  95.30   0.00   0.00   0.00  -  -  -    84  20  85.11 0.757   0x0  0x0   0  10.422
    16   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -   0.00     -     -  0x0   -       -
    17   CPU0   -   -  2301  2400   4.13 0.96   4.12  95.88   0.00   0.00   0.00  -  -  -    85  19  84.03 0.757   0x0  0x0   0   9.984
    17   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -   0.00     -     -  0x0   -       -
    18   CPU0   -   -  2275  2400   3.93 0.84   3.94  96.06   0.00   0.00   0.00  -  -  -    84  20  83.82 0.757   0x0  0x0   0   9.781
    18   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -   0.00     -     -  0x0   -       -
    19   CPU0   -   -  2300  2400   4.25 0.94   4.25  95.75   0.00   0.00   0.00  -  -  -    84  20  83.82 0.757   0x0  0x0   0   9.891
    19   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -   0.00     -     -  0x0   -       -
    20   CPU0   -   -  2295  2400   4.75 2.32   4.76  95.24   0.00   0.00   0.00  -  -  -    84  20  84.44 0.757   0x0  0x0   0   9.953
    20   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -   0.00     -     -  0x0   -       -
    21   CPU0   -   -  2294  2400   2.71 1.88   2.71  97.29   0.00   0.00   0.00  -  -  -    83  21  82.85 0.757   0x0  0x0   0  10.000
    21   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -   0.00     -     -  0x0   -       -
    22   CPU0   -   -  2296  2400   3.96 2.44   3.96  96.04   0.00   0.00   0.00  -  -  -    84  20  83.83 0.757   0x0  0x0   0  11.484
    22   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -   0.00     -     -  0x0   -       -
    23   CPU0   -   -  2298  2400   4.33 1.55   4.33  95.67   0.00   0.00   0.00  -  -  -    84  20  84.28 0.757   0x0  0x0   0  10.359
    23   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -   0.00     -     -  0x0   -       -
    24   CPU0   -   -  2295  2400   4.77 1.47   4.77  95.23   0.00   0.00   0.00  -  -  -    84  20  84.59 0.757   0x0  0x0   0   9.750
    24   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -   0.00     -     -  0x0   -       -
    25   CPU0   -   -  2296  2400   4.53 1.08   4.53  95.47   0.00   0.00   0.00  -  -  -    84  20  84.24 0.757   0x0  0x0   0   9.953
    25   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -   0.00     -     -  0x0   -       -
    26   CPU0   -   -  2291  2400   5.33 1.97   5.33  94.67   0.00   0.00   0.00  -  -  -    85  19  85.82 0.757   0x0  0x0   0   9.938
    26   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -   0.00     -     -  0x0   -       -
    27   CPU0   -   -  2297  2400   4.84 1.22   4.85  95.15   0.00   0.00   0.00  -  -  -    84  20  84.65 0.757   0x0  0x0   0   9.547
    27   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -   0.00     -     -  0x0   -       -
    28   CPU0   -   -  2295  2400   4.76 1.42   4.75  95.25   0.00   0.00   0.00  -  -  -    85  19  84.57 0.757   0x0  0x0   0   9.672
    28   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -   0.00     -     -  0x0   -       -
    29   CPU0   -   -  2296  2400   4.54 1.08   4.54  95.46   0.00   0.00   0.00  -  -  -    83  21  84.38 0.757   0x0  0x0   0   9.688
    29   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -   0.00     -     -  0x0   -       -
    30   CPU0   -   -  2294  2400   4.74 1.40   4.74  95.26   0.00   0.00   0.00  -  -  -    84  20  84.66 0.757   0x0  0x0   0  10.016
    30   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -   0.00     -     -  0x0   -       -
    31   CPU0   -   -  2292  2400   4.68 1.86   4.68  95.32   0.00   0.00   0.00  -  -  -    85  19  84.38 0.757   0x0  0x0   0   9.750
    31   MEM0   -   -     -     -      -    -      -      -      -      -      -  -  -  -    48   -   0.00     -     -  0x0   -       -
```


```log
root@controller-0:/home/XXXXXX/ptu# ipmitool sensor| grep -e CPU -e DutyCycle -e Watts
02-CPU           | 47.000     | degrees C  | ok    | na        | na        | na        | na        | 70.000    | na
51-CPU 1 PkgTmp  | 82.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
Fan 1 DutyCycle  | 26.656     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 2 DutyCycle  | 26.656     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 3 DutyCycle  | 26.656     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 4 DutyCycle  | 26.656     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 5 DutyCycle  | 26.656     | percent    | ok    | na        | na        | na        | na        | na        | na
Fan 6 DutyCycle  | 26.656     | percent    | ok    | na        | na        | na        | na        | na        | na
PS 1 Input       | 160.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PS 2 Input       | 150.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
CPU Utilization  | 12.000     | percent    | ok    | na        | na        | na        | na        | na        | na
PS 1 Output      | 160.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PS 2 Output      | 150.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
CPU_Stat_C1      | 0x0        | discrete   | 0x8080| na        | na        | na        | na        | na        | na
root@controller-0:/home/XXXXXX/ptu#
```

### All Test passed.

