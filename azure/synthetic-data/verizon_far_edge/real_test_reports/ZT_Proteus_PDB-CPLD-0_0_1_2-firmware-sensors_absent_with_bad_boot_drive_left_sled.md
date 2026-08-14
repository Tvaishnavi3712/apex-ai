# ZT Proteus PDB-DPLD 0.0.1.2 firmware
# ZT Proteus BMC .46 and Bios .30
# 3/7/24 James Patchett
# Sensor validation issue with Left side sled when OS is non-bootable with firmware PDB 0.0.1.2

## Target subclouds RU_12,13 Right and Left side

## Left side Subcloud welktxef-d931887-021
## BMC 0.46 BIOS 0.30
BMC:  2607:f160:10:9249:ce:40a:0:e015
OAM:  2607:f160:10:9249:ce:40a:0:f409

## Controller rchltxfe-c000000-001


## Right side Subcloud welktxef-d931883-022
## BMC 0.46 BIOS 0.30
BMC:  2607:f160:10:9249:ce:40a:0:e016
OAM:  2607:f160:10:9249:ce:40a:0:f407

## Controller IB-CR2 welktxib-c000000-001
BMC:  2607:f160:10:920f:ce:fe0:0:8063
OAM:  2607:f160:10:9109:ce:290:0:10

## Sensor baseline before we start, both hosts are up and booted into OS

```log
[XXXXXX@welktxefnce-h-pe1util-vm01 ZT_FW]$ echo $IP
2607:f160:10:9249:ce:40a:0:e015
[XXXXXX@welktxefnce-h-pe1util-vm01 ZT_FW]$ rf_sensor_list.py -u XXXXXX -p XXXXXX -r https://[$IP]
Chassis 'Computer System Chassis' Status
  Sensor                    | Reading    | Health   | LF       | LC       | LNC      | UNC      | UC       | UF       | PhysicalContext
  State                     | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 213V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 156W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 213V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 144W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_V5                    | 5.053V     | OK       | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | 12.1568V   | OK       | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | 3.3236V    | OK       | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | 1.0532V    | OK       | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  RTC_Voltage               | 3.024V     | OK       | N/A      | 2.289    | N/A      | N/A      | 3.444    | N/A      | VoltageRegulator
  CPU_0_Vcore               | 1.8248V    | OK       | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | 1.2306V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | 1.2306V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | -48Cel     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_MARGIN              | 39Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  PSU_1_TEMP_2              | 46Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_1_TEMP_1              | 27Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  PSU_2_TEMP_2              | 45Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_2_TEMP_1              | 27Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  CPU_0_DIMM_C0             | 37Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_D0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_A0             | 34Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_B0             | 34Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_G0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_H0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_E0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_F0             | 35Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  DIMM_VRABCD_TEMP          | 35Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  DIMM_VREFGH_TEMP          | 34Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  MAX_DIMM_TEMP             | 37Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  PML_WEST_TEMP             | 56Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  PML_LOCAL_TEMP            | 54Cel      | OK       | N/A      | N/A      | N/A      | 80       | 85       | N/A      | Intake
  PML_VDD_TEMP              | 58Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 125      | N/A      | Intake
  PML_EAST_TEMP             | 56Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  SC_1_E810                 | 42Cel      | OK       | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SC_2_E810                 | 39Cel      | OK       | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SSD_0_TEMP                | 35Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  SSD_1_TEMP                | 36Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  INLET_TEMP_L              | 25Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  INLET_TEMP_R              | 24Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  MB_HSC_TEMP               | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  OUTLET_TEMP_L             | 39Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  OUTLET_TEMP_R             | 37Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  INLET_TEMP_MAX            | 25Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  OUTLET_TEMP_MAX           | 39Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  SYS_PCH_TEMP              | 33Cel      | OK       | N/A      | 5        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_TEMP                | 50Cel      | OK       | N/A      | N/A      | N/A      | 96       | 98       | N/A      | Intake
  SYS_FAN_1A                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_1B                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2A                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2B                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_1_FAN                 | 3840RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_2_FAN                 | 4000RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan

[XXXXXX@welktxefnce-h-pe1util-vm01 ZT_FW]$
[XXXXXX@welktxefnce-h-pe1util-vm01 proteus_health]$ echo $IP
2607:f160:10:9249:ce:40a:0:e016
[XXXXXX@welktxefnce-h-pe1util-vm01 proteus_health]$ rf_sensor_list.py -u XXXXXX -p XXXXXX -r https://[$IP]
Chassis 'Computer System Chassis' Status
  Sensor                    | Reading    | Health   | LF       | LC       | LNC      | UNC      | UC       | UF       | PhysicalContext
  State                     | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 213V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 150W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 213V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 138W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_V5                    | 4.9984V    | OK       | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | 12.138V    | OK       | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | 3.3032V    | OK       | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | 1.045V     | OK       | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  RTC_Voltage               | 3.017V     | OK       | N/A      | 2.289    | N/A      | N/A      | 3.444    | N/A      | VoltageRegulator
  CPU_0_Vcore               | 1.8164V    | OK       | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | 1.2232V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | 1.2232V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | -44Cel     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_MARGIN              | 30Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  PSU_1_TEMP_2              | 46Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_1_TEMP_1              | 27Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  PSU_2_TEMP_2              | 45Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_2_TEMP_1              | 27Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  CPU_0_DIMM_C0             | 38Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_D0             | 37Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_A0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_B0             | 35Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_G0             | 37Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_H0             | 37Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_E0             | 37Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_F0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  DIMM_VRABCD_TEMP          | 35Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  DIMM_VREFGH_TEMP          | 34Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  MAX_DIMM_TEMP             | 38Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  PML_WEST_TEMP             | 55Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  PML_LOCAL_TEMP            | 54Cel      | OK       | N/A      | N/A      | N/A      | 80       | 85       | N/A      | Intake
  PML_VDD_TEMP              | 58Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 125      | N/A      | Intake
  PML_EAST_TEMP             | 54Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  SC_1_E810                 | 43Cel      | OK       | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SC_2_E810                 | 39Cel      | OK       | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SSD_0_TEMP                | 35Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  SSD_1_TEMP                | 36Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  INLET_TEMP_L              | 26Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  INLET_TEMP_R              | 25Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  MB_HSC_TEMP               | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  OUTLET_TEMP_L             | 40Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  OUTLET_TEMP_R             | 38Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  INLET_TEMP_MAX            | 26Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  OUTLET_TEMP_MAX           | 40Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  SYS_PCH_TEMP              | 33Cel      | OK       | N/A      | 5        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_TEMP                | 54Cel      | OK       | N/A      | N/A      | N/A      | 96       | 98       | N/A      | Intake
  SYS_FAN_1A                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_1B                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2A                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2B                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_1_FAN                 | 3840RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_2_FAN                 | 4000RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan

[XXXXXX@welktxefnce-h-pe1util-vm01 proteus_health]$



```

###  I have validated with previous tests (20 iterations of power cycling Left and Right Sled and sensor validation after stable boot of OS).  
###  Those tests proved, we had no sensor issue with .46bmc/.30bios & PDB-CPLD 0.0.1.2.  All reboots resulted in good sensor reading, no Absents once OS is booted.

### Now lets cause a non-bootable os situation with the left sled, then check to see if sensors remain stable.

### Subcloud welktxef-d931887-021

```log
root@controller-0:/boot/1# ls -latr
total 206188
-rw-r--r-- 1 root  751       589 Jan  1  1970 vmlinuz.sig
-rw-r--r-- 1 root  751       589 Jan  1  1970 vmlinuz-5.10.0-6-rt-amd64.sig
-rw-r--r-- 1 root  751   9730688 Jan  1  1970 vmlinuz-5.10.0-6-rt-amd64
-rw-r--r-- 1 root  751       589 Jan  1  1970 vmlinuz-5.10.0-6-amd64.sig
-rw-r--r-- 1 root  751  11056704 Jan  1  1970 vmlinuz-5.10.0-6-amd64
-rw-r--r-- 1 root  751  11056704 Jan  1  1970 vmlinuz
-rw-r--r-- 1 root  751       589 Jan  1  1970 initramfs.sig
-rw-r--r-- 1 root  751 179249746 Jan  1  1970 initramfs
-rw-r--r-- 1 root  751         0 Jan  1  1970 .ostree-bootcsumdir-source
drwxr-xr-x 3 root root      4096 Mar  6 22:59 ..
drwxr-xr-x 3 root root      4096 Mar  6 22:59 efi
-rw-r--r-- 1 root  751      1140 Mar  7 01:22 kernel.env
drwxr-xr-x 3 root root      4096 Mar  7 01:22 .
root@controller-0:/boot/1#
root@controller-0:/boot/1# pwd
/boot/1                                                                                                                                         vmlinuz-5.10.0-6-rt-amd64oller-0:/boot/1# mv vmlinuz-5.10.0-6-rt-amd64 Disable.vmlinuz-5.10.0-6-rt-amd64
root@controller-0:/boot/1# ls -latr
total 206188
-rw-r--r-- 1 root  751       589 Jan  1  1970 vmlinuz.sig
-rw-r--r-- 1 root  751       589 Jan  1  1970 vmlinuz-5.10.0-6-rt-amd64.sig
-rw-r--r-- 1 root  751       589 Jan  1  1970 vmlinuz-5.10.0-6-amd64.sig
-rw-r--r-- 1 root  751  11056704 Jan  1  1970 vmlinuz-5.10.0-6-amd64
-rw-r--r-- 1 root  751  11056704 Jan  1  1970 vmlinuz
-rw-r--r-- 1 root  751       589 Jan  1  1970 initramfs.sig
-rw-r--r-- 1 root  751 179249746 Jan  1  1970 initramfs
-rw-r--r-- 1 root  751   9730688 Jan  1  1970 Disable.vmlinuz-5.10.0-6-rt-amd64
-rw-r--r-- 1 root  751         0 Jan  1  1970 .ostree-bootcsumdir-source
drwxr-xr-x 3 root root      4096 Mar  6 22:59 ..
drwxr-xr-x 3 root root      4096 Mar  6 22:59 efi
-rw-r--r-- 1 root  751      1140 Mar  7 01:22 kernel.env
drwxr-xr-x 3 root root      4096 Mar  7 02:12 .
root@controller-0:/boot/1#

```

### now we reboot the subcloud

```log

root@controller-0:/boot/1#
root@controller-0:/boot/1# reboot
[  OK  ] Removed slice system-modprobe.slice.
[  OK  ] Stopped target Graphical Interface.
[  OK  ] Stopped target Multi-User System.
[  OK  ] Stopped target Login Prompts.
[  OK  ] Stopped target Remote Encrypted Volumes.
[  OK  ] Stopped target Remote File Systems (Pre).
[  OK  ] Stopped target NFS client se         Stopping Load/Save Random Seed...
         Stopping Dynamic System Tuning Daemon...
         Stopping StarlingX Filesystem Initialization...
[  OK  ] Stopped pNFS block layout mapping daemon.
[  OK  ] Stopped Avahi mDNS/DNS-SD Stack.
[  OK  ] Stopped Regular background program processing daemon.
[  OK  ] Stopped Authorization Manager.
[  OK  ] Stopped User Login Management.
[  OK  ] Stopped fast remote file copy program daemon.
[  OK  ] Stopped LLDP daemon.
[  OK  ] Stopped Network Time Service.
[  OK  ] Stopped Getty on tty1.
[  OK  ] Stopped Serial Getty on ttyS0.
[  OK  ] Stopped Kubernetes Isolated CPU Plugin Daemon.
[  OK  ] Stopped StarlingX Maintenance Worker Goenable Ready.
[  OK  ] Stopped Logout off all iSCSI sessions on shutdown.
[  OK  ] Stopped LVM event activation on device 259:4.
[  OK  ] Stopped Load/Save Random Seed.
[  OK  ] Stopped StarlingX Filesystem Initialization.
[  OK  ] Stopped v2 Registry token server for Docker.
[  OK  ] Stopped the Docker toolset…p, store, and deliver content.
[  OK  ] Stopped LSB: Provide limit… privileges to specific users.
[  OK  ] Stopped LSB: Open vSwitch VTEP emulator.
[  OK  ] Stopped LSB: Ceph RBD Mapping.
[  OK  ] Removed slice system-getty.slice.
[  OK  ] Removed slice system-lvm2\x2dpvscan.slice.
[  OK  ] Removed slice system-serial\x2dgetty.slice.
         Unmounting RPC Pipe File System...
         Stopping Kubernetes Kubelet Server...
         Stopping StarlingX Cloud Filesystem Auto-mounter...
         Stopping StarlingX Filesystem Server...
         Stopping Permit User Sessions...
[ 3517.727178] kdump-tools[452364]: Stopping kdump-tools:
[  OK  ] Stopped LSB: Load kernel image with kexec.
[  OK  ] Stopped LSB: Simple OpenFlow controller for testing.
[  OK  ] Stopped LSB: radosgw RESTful rados gateway.
[  OK  ] Stopped LSB: rng-tools (Debian variant).
[FAILED] Failed unmounting RPC Pipe File System.
[  OK  ] Stopped Kernel crash dump capture service.
[ 3517.743465] kdump-tools[452508]: Kernel security lockdown: none
[  OK  ] Stopped Permit User Sessions.
[ 3517.807525] kdump-tools[452508]: unloaded kdump kernel.
[  OK  ] Stopped Docker Application Container Engine.
[  OK  ] Stopped Fault Management REST API Service.
[  OK  ] Stopped Kubernetes Kubelet Server.
[  OK  ] Stopped target User and Group Name Lookups.
[ 3517.897789] watchdog: watchdog0: watchdog did not stop!
         Stopping etcd - highly-available key value store...
         Stopping containerd container runtime...
         Stopping LSB: Execute the …-e command to reboot system...
         Stopping System Security Services Daemon...
[  OK  ] Stopped LSB: Open vSwitch GRE-over-IPsec daemon.
[  OK  ] Stopped System Security Services Daemon.
[  OK  ] Stopped StarlingX Maintenance Host Watchdog.
[  OK  ] Stopped StarlingX Affine Platform.
[  OK  ] Stopped StarlingX Cloud Filesystem Auto-mounter.
[  OK  ] Stopped StarlingX Filesystem Server.
         Stopping StarlingX Maintenance Process Monitor...
[  OK  ] Stopped LSB: Execute the k…c -e command to reboot system.
[  OK  ] Stopped Dynamic System Tuning Daemon.
         Stopping D-Bus System Message Bus...
[  OK  ] Stopped D-Bus System Message Bus.
[  OK  ] Unmounted /run/containerd/…21e865654a1e32d6594056/rootfs.
[  OK  ] Unmounted /run/containerd/…4ae909c950827cd186a25f/rootfs.
[  OK  ] Unmounted /run/containerd/…cad18e78d8066452cac89c/rootfs.
[  OK  ] Unmounted /run/containerd/…a2a00c4e217dd1fc375993/rootfs.
[  OK  ] Unmounted /run/containerd/…92f96579d9c5c6714eac83/rootfs.
[  OK  ] Stopped StarlingX Maintenance Process Monitor.
         Stopping ACPI event daemon...
         Stopping Collectd statisti…emon and extension services...
         Stopping StarlingX Maintenance Filesystem Monitor...
         Stopping StarlingX Maintenance Goenable Ready...
         Stopping StarlingX Maintenance Heartbeat Agent...
         Stopping Starling-X Maintenance Link Monitor...
         Stopping StarlingX Maintenance Command Handler Client...
         Stopping StarlingX Maintenance Alarm Handler Client...
         Stopping StarlingX Maintenance Logger...
[  OK  ] Stopped StarlingX Pxeboot Feed Refresh.
         Stopping Service Management Event Recorder Unit...
         Stopping StarlingX Patching Agent...
         Stopping StarlingX Patching Controller Daemon...
[  OK  ] Stopped ACPI event daemon.
[  OK  ] Stopped StarlingX Maintenance Goenable Ready.
[  OK  ] Stopped StarlingX Patching Agent.
[  OK  ] Stopped StarlingX Patching Controller Daemon.
[  OK  ] Stopped Collectd statistic…daemon and extension services.
[  OK  ] Stopped etcd - highly-available key value store.
[  OK  ] Stopped StarlingX Patching Controller.
[  OK  ] Stopped StarlingX Maintenance Filesystem Monitor.
[  OK  ] Stopped Starling-X Maintenance Link Monitor.
[  OK  ] Stopped StarlingX Maintenance Heartbeat Agent.
[  OK  ] Unmounted /run/containerd/…0131119aeaab2be6e24ef1/rootfs.
[  OK  ] Unmounted /run/containerd/…d3c5cadf1f22e3d25df74f/rootfs.
[  OK  ] Unmounted /run/containerd/…797c89f450de75f81547ef/rootfs.
[  OK  ] Unmounted /run/containerd/…164313a41f22b1cc4ceead/rootfs.
[  OK  ] Unmounted /run/containerd/…f48b95b64868666c3af7ed/rootfs.
[  OK  ] Unmounted /run/containerd/…0b194a934dc7c88f66a2bb/rootfs.
[  OK  ] Unmounted /run/containerd/…e91a3401349afcb8e555c3/rootfs.
[  OK  ] Unmounted /run/containerd/…bf6a2b8b9375499a5a4a3d/rootfs.
[  OK  ] Unmounted /run/containerd/…632fc7aa5841c66ad1c3b6/rootfs.
[  OK  ] Stopped StarlingX Maintenance Command Handler Client.
[  OK  ] Stopped StarlingX Maintenance Alarm Handler Client.
[  OK  ] Stopped StarlingX Maintenance Logger.
         Stopping StarlingX Maintenance Heartbeat Client...
[  OK  ] Stopped memcached daemon.
[  OK  ] Unmounted /run/containerd/…c996ddb0a67f6a2670fa5e/rootfs.
[  OK  ] Unmounted /run/containerd/…bcf02f644873512dc400b1/rootfs.
[  OK  ] Stopped StarlingX Maintenance Heartbeat Client.
[  OK  ] Unmounted /run/containerd/…92ffebf179aa1f1e47dd5a/rootfs.
[  OK  ] Unmounted /run/containerd/…c832929ed679bd2acb3de7/rootfs.
[  OK  ] Unmounted /run/containerd/…bde9b6af00e080a66f384c/rootfs.
[  OK  ] Unmounted /run/containerd/…d54d0a0820cb400afde183/rootfs.
[  OK  ] Unmounted /var/www/tmp.
[  OK  ] Unmounted /run/containerd/…94a4156e55046ac4081a5a/rootfs.
[  OK  ] Unmounted /run/containerd/…549e3f28b0f801ef6185f2/rootfs.
[  OK  ] Unmounted /run/containerd/…f3c4fa474b0bb7c5f0059c/rootfs.
[  OK  ] Unmounted /run/containerd/…74134448796965a1854477/rootfs.
[  OK  ] Unmounted /run/containerd/…00ec071805e8230936b7e8/rootfs.
[  OK  ] Unmounted /run/containerd/…c0e29031fd8ceca9985390/rootfs.
[  OK  ] Unmounted /run/containerd/…56be0f30cf727c0a5ac06d/rootfs.
[  OK  ] Unmounted /run/containerd/…98ce3b5b56d3aece5fca39/rootfs.
[  OK  ] Unmounted /run/containerd/…5161b58edb80b29ec4e308/rootfs.
[  OK  ] Stopped Service Management Event Recorder Unit.
         Stopping Service Management API Unit...
[  OK  ] Stopped Service Management API Unit.
[  OK  ] Unmounted /run/containerd/…5cb62439ff5a2758f7b543/rootfs.
[  OK  ] Unmounted /run/containerd/…396ca40167232cd1b3fbe7/rootfs.
[  OK  ] Unmounted /run/containerd/…9d7640a196c66c220e24f6/rootfs.
[  OK  ] Unmounted /run/containerd/…55f05ee741bf4e5f8bf1ab/rootfs.
[  OK  ] Unmounted /run/containerd/…d3b390a73d71795b690b4a/rootfs.
[  OK  ] Unmounted /run/containerd/…f4d258bc29f9c495b806a6/rootfs.
[  OK  ] Unmounted /run/containerd/…be6176496fb0dcee1a5450/rootfs.
[  OK  ] Unmounted /run/containerd/…a7c246b178bd845117c18a/rootfs.
[  OK  ] Unmounted /run/containerd/…ae62f34dc7ec12e7b7480c/rootfs.
[  OK  ] Unmounted /run/containerd/…d636b738b3d8ba099e44a9/rootfs.
[  OK  ] Unmounted /run/containerd/…309e74664951d16f0d883a/rootfs.
[  OK  ] Unmounted /run/containerd/…8054e0f71e1c9d08055ebe/rootfs.
[  OK  ] Unmounted /var/lib/docker-distribution.
[  OK  ] Unmounted /var/www/pages/device_images.
[  OK  ] Unmounted /var/www/pages/helm_charts.
[  OK  ] Unmounted /var/rootdirs/opt/extension.
[  OK  ] Unmounted /var/rootdirs/opt/etcd.
[  OK  ] Unmounted /var/rootdirs/opt/platform.
[  OK  ] Unmounted /run/containerd/…ac37d277b4867721f8701b/rootfs.
[  OK  ] Unmounted /run/containerd/…6f2395748f3eaaf683eeee/rootfs.
[  OK  ] Unmounted /run/containerd/…40147192ed4664434720e9/rootfs.
[  OK  ] Unmounted /run/containerd/…6e3c06cea0db1ec71396880f4/shm.
[  OK  ] Unmounted /run/containerd/…47e6b14ee98b8afb279b3f7e0/shm.
[  OK  ] Unmounted /run/containerd/…5ea4259751a01360a21fd7f64/shm.
[  OK  ] Unmounted /run/containerd/…9beb84859fa9aaafbf2b05e95/shm.
[  OK  ] Unmounted /run/containerd/…4259751a01360a21fd7f64/rootfs.
[  OK  ] Unmounted /run/containerd/…c06cea0db1ec71396880f4/rootfs.
[  OK  ] Unmounted /run/containerd/…b84859fa9aaafbf2b05e95/rootfs.
[  OK  ] Unmounted /run/containerd/…6b14ee98b8afb279b3f7e0/rootfs.
[  OK  ] Unmounted /run/containerd/…4f9bd11de5345bd365a99e1ee/shm.
[  OK  ] Unmounted /run/containerd/…848b874caf8d567e0e96258b4/shm.
[  OK  ] Unmounted /run/containerd/…673035b79c9a18df404652c72/shm.
[  OK  ] Unmounted /run/containerd/…b0e00688bc601ed6e02d9baa4/shm.
[  OK  ] Unmounted /run/containerd/…72a9ac835f51495603f787275/shm.
[  OK  ] Unmounted /run/containerd/…8377c6cd854eba4ae7fc75f5c/shm.
[  OK  ] Unmounted /run/containerd/…edd30ab1f28a3736e3326155c/shm.
[  OK  ] Unmounted /run/containerd/…b874caf8d567e0e96258b4/rootfs.
[  OK  ] Unmounted /run/containerd/…00688bc601ed6e02d9baa4/rootfs.
[  OK  ] Unmounted /run/containerd/…3a9af5350a3246c5e908f0241/shm.
[  OK  ] Unmounted /run/containerd/…d0471f5bec2e5abf669b649d5/shm.
[  OK  ] Unmounted /run/containerd/…bd11de5345bd365a99e1ee/rootfs.
[  OK  ] Unmounted /run/containerd/…2704713e62e57878bcac91927/shm.
[  OK  ] Unmounted /run/containerd/…035b79c9a18df404652c72/rootfs.
[  OK  ] Unmounted /run/containerd/…9ac835f51495603f787275/rootfs.
[  OK  ] Unmounted /run/containerd/…7c6cd854eba4ae7fc75f5c/rootfs.
[  OK  ] Unmounted /run/containerd/…30ab1f28a3736e3326155c/rootfs.
[  OK  ] Unmounted /run/containerd/…af5350a3246c5e908f0241/rootfs.
[  OK  ] Unmounted /run/containerd/…71f5bec2e5abf669b649d5/rootfs.
[  OK  ] Unmounted /run/containerd/…4713e62e57878bcac91927/rootfs.
[  OK  ] Unmounted /run/containerd/…19d7a5744a0efd844c4784/rootfs.
[  OK  ] Unmounted /run/containerd/…45c19d7a5744a0efd844c4784/shm.
[  OK  ] Unmounted /run/containerd/…0808baa7639b058d7c3bb6/rootfs.
[  OK  ] Unmounted /run/containerd/…8440808baa7639b058d7c3bb6/shm.
[  OK  ] Unmounted /run/containerd/…9df328484fb2b03151ded4/rootfs.
[  OK  ] Unmounted /run/containerd/…6ec9df328484fb2b03151ded4/shm.
[  OK  ] Unmounted /run/containerd/…502ab3b0a8e898861c4455/rootfs.
[  OK  ] Unmounted /run/containerd/…abf502ab3b0a8e898861c4455/shm.
[  OK  ] Unmounted /run/containerd/…88d2b069e060cddb1715bd/rootfs.
[  OK  ] Unmounted /run/containerd/…a8a88d2b069e060cddb1715bd/shm.
[  OK  ] Unmounted /run/containerd/…7b6acaf6726299a3d1f5045cb/shm.
[  OK  ] Unmounted /run/containerd/…c5fbdff826021e7143ea899bf/shm.
[  OK  ] Unmounted /run/containerd/…de731236f5bb93b4aa9d3c75e/shm.
[  OK  ] Unmounted /run/containerd/…82eac5f827cabbcc13c89054e/shm.
[  OK  ] Unmounted /run/containerd/…d12feade4156c4c020b382387/shm.
[  OK  ] Unmounted /run/containerd/…466d61ac2248004e760af0deb/shm.
[  OK  ] Unmounted /run/containerd/…76fdf703d4bd1e2e3c1cf09a7/shm.
[  OK  ] Unmounted /run/containerd/…e0a27e9d5446819802d3765e0/shm.
[  OK  ] Unmounted /var/lib/postgresql.
[  OK  ] Unmounted /run/containerd/…acaf6726299a3d1f5045cb/rootfs.
[  OK  ] Unmounted /run/containerd/…bdff826021e7143ea899bf/rootfs.
[  OK  ] Unmounted /run/containerd/…31236f5bb93b4aa9d3c75e/rootfs.
[  OK  ] Unmounted /run/containerd/…ac5f827cabbcc13c89054e/rootfs.
[  OK  ] Unmounted /run/containerd/…feade4156c4c020b382387/rootfs.
[  OK  ] Unmounted /run/containerd/…d61ac2248004e760af0deb/rootfs.
[  OK  ] Unmounted /run/containerd/…b7ed3a12f52dc9cf778aeedf5/shm.
[  OK  ] Unmounted /run/containerd/…d30b4697e0a01ef3b456185a8/shm.
[  OK  ] Unmounted /run/containerd/…fca2f50d6981e5c3dc895bad6/shm.
[  OK  ] Unmounted /run/containerd/…3a32082b27b13151512a4cedf/shm.
[  OK  ] Unmounted /run/containerd/…3e31714476dd1c2606a7f6567/shm.
[  OK  ] Unmounted /run/containerd/…df703d4bd1e2e3c1cf09a7/rootfs.
[  OK  ] Unmounted /run/containerd/…27e9d5446819802d3765e0/rootfs.
[  OK  ] Unmounted /run/containerd/…d3a12f52dc9cf778aeedf5/rootfs.
[  OK  ] Unmounted /run/containerd/…b4697e0a01ef3b456185a8/rootfs.
[  OK  ] Stopped containerd container runtime.
         Stopping /usr/bin/ceph-mds…ceph/ceph.conf --cluster ceph.
         Stopping /usr/bin/ceph-mon…ceph/ceph.conf --cluster ceph.
         Stopping /usr/bin/ceph-osd…ceph/ceph.conf --cluster ceph.
[  OK  ] Stopped /usr/bin/ceph-mon …ceph/ceph.conf --cluster ceph.
[  OK  ] Unmounted /run/containerd/…2082b27b13151512a4cedf/rootfs.
[  OK  ] Unmounted /run/containerd/…2f50d6981e5c3dc895bad6/rootfs.
[  OK  ] Unmounted /run/containerd/…1714476dd1c2606a7f6567/rootfs.
[  OK  ] Stopped /usr/bin/ceph-osd …ceph/ceph.conf --cluster ceph.
[  OK  ] Unmounted /var/lib/rabbitmq.
[  OK  ] Stopped /usr/bin/ceph-mds …ceph/ceph.conf --cluster ceph.
[  OK  ] Removed slice system-ceph.slice.
         Stopping Service Management Shutdown Unit...



....etc......
```

### After reboot command in os, post bios, booting grub...

### right side sled

```log
[XXXXXX@welktxefnce-h-pe1util-vm01 ZT_FW]$ count=0 ; while [ $count -lt 100 ] ; do  rf_sensor_list.py -u XXXXXX -p XXXXXX -r https://[$IP] |grep Absent; echo "sleeping 30 seconds"; sleep 30; count=$((count+1)); done
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
^C
[XXXXXX@welktxefnce-h-pe1util-vm01 ZT_FW]$

```

### left side sled

```log
[XXXXXX@welktxefnce-h-pe1util-vm01 ZT_FW]$ count=0 ; while [ $count -lt 100 ] ; do  rf_sensor_list.py -u XXXXXX -p XXXXXX -r https://[$IP] |grep Absent; echo "sleeping 30 seconds"; sleep 30; count=$((count+1)); done
  CPU_0_DTS_TEMP            | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_MARGIN              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_DIMM_C0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_D0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_A0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_B0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_G0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_H0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_E0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_F0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  MAX_DIMM_TEMP             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
sleeping 30 seconds
  SYS_V5                    | Absent     | N/A      | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | Absent     | N/A      | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | Absent     | N/A      | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | Absent     | N/A      | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  CPU_0_Vcore               | Absent     | N/A      | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  MAX_DIMM_TEMP             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds

sleeping 30 seconds
  SYS_V5                    | Absent     | N/A      | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | Absent     | N/A      | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | Absent     | N/A      | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | Absent     | N/A      | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  CPU_0_Vcore               | Absent     | N/A      | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_MARGIN              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  MAX_DIMM_TEMP             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  SC_1_E810                 | Absent     | N/A      | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SC_2_E810                 | Absent     | N/A      | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
sleeping 30 seconds
  SYS_V5                    | Absent     | N/A      | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | Absent     | N/A      | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | Absent     | N/A      | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | Absent     | N/A      | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  CPU_0_Vcore               | Absent     | N/A      | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  MAX_DIMM_TEMP             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
  SYS_V5                    | Absent     | N/A      | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | Absent     | N/A      | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | Absent     | N/A      | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | Absent     | N/A      | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  CPU_0_Vcore               | Absent     | N/A      | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_MARGIN              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  PSU_1_TEMP_2              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_1_TEMP_1              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  PSU_2_TEMP_2              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_2_TEMP_1              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  CPU_0_DIMM_C0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_D0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_A0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_B0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_G0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_H0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_E0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_F0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  MAX_DIMM_TEMP             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  PML_WEST_TEMP             | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  PML_LOCAL_TEMP            | Absent     | N/A      | N/A      | N/A      | N/A      | 80       | 85       | N/A      | Intake
  PML_VDD_TEMP              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 125      | N/A      | Intake
  PML_EAST_TEMP             | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  SC_1_E810                 | Absent     | N/A      | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SC_2_E810                 | Absent     | N/A      | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SSD_0_TEMP                | Absent     | N/A      | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  SSD_1_TEMP                | Absent     | N/A      | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  CPU_0_TEMP                | Absent     | N/A      | N/A      | N/A      | N/A      | 96       | 98       | N/A      | Intake
  SYS_FAN_1A                | Absent%    | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_1B                | Absent%    | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2A                | Absent%    | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2B                | Absent%    | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_1_FAN                 | Absent     | N/A      | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_2_FAN                 | Absent     | N/A      | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
sleeping 30 seconds
  SYS_V5                    | Absent     | N/A      | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | Absent     | N/A      | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | Absent     | N/A      | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | Absent     | N/A      | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  CPU_0_Vcore               | Absent     | N/A      | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_MARGIN              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  MAX_DIMM_TEMP             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  SC_1_E810                 | Absent     | N/A      | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SC_2_E810                 | Absent     | N/A      | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
  SYS_V5                    | Absent     | N/A      | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | Absent     | N/A      | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | Absent     | N/A      | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | Absent     | N/A      | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  CPU_0_Vcore               | Absent     | N/A      | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_MARGIN              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  PSU_1_TEMP_2              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_1_TEMP_1              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  PSU_2_TEMP_2              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_2_TEMP_1              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  MAX_DIMM_TEMP             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  PML_WEST_TEMP             | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  PML_LOCAL_TEMP            | Absent     | N/A      | N/A      | N/A      | N/A      | 80       | 85       | N/A      | Intake
  PML_VDD_TEMP              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 125      | N/A      | Intake
  PML_EAST_TEMP             | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  SC_1_E810                 | Absent     | N/A      | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SC_2_E810                 | Absent     | N/A      | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SSD_0_TEMP                | Absent     | N/A      | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  SSD_1_TEMP                | Absent     | N/A      | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  PSU_1_FAN                 | Absent     | N/A      | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_2_FAN                 | Absent     | N/A      | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
sleeping 30 seconds
  SYS_V5                    | Absent     | N/A      | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | Absent     | N/A      | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | Absent     | N/A      | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | Absent     | N/A      | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  CPU_0_Vcore               | Absent     | N/A      | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_MARGIN              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  MAX_DIMM_TEMP             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  SC_1_E810                 | Absent     | N/A      | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SC_2_E810                 | Absent     | N/A      | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
  SYS_V5                    | Absent     | N/A      | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | Absent     | N/A      | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | Absent     | N/A      | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | Absent     | N/A      | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  CPU_0_Vcore               | Absent     | N/A      | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_MARGIN              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  PSU_1_TEMP_2              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_1_TEMP_1              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  PSU_2_TEMP_2              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_2_TEMP_1              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  CPU_0_DIMM_C0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_D0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_A0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_B0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_G0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_H0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_E0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_F0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  DIMM_VRABCD_TEMP          | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  DIMM_VREFGH_TEMP          | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  MAX_DIMM_TEMP             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  PML_WEST_TEMP             | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  PML_LOCAL_TEMP            | Absent     | N/A      | N/A      | N/A      | N/A      | 80       | 85       | N/A      | Intake
  PML_VDD_TEMP              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 125      | N/A      | Intake
  PML_EAST_TEMP             | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  SC_1_E810                 | Absent     | N/A      | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SC_2_E810                 | Absent     | N/A      | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SSD_0_TEMP                | Absent     | N/A      | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  SSD_1_TEMP                | Absent     | N/A      | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  MB_HSC_TEMP               | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  SYS_PCH_TEMP              | Absent     | N/A      | N/A      | 5        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_TEMP                | Absent     | N/A      | N/A      | N/A      | N/A      | 96       | 98       | N/A      | Intake
  SYS_FAN_1B                | Absent%    | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2A                | Absent%    | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2B                | Absent%    | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_1_FAN                 | Absent     | N/A      | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_2_FAN                 | Absent     | N/A      | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
sleeping 30 seconds
  SYS_V5                    | Absent     | N/A      | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | Absent     | N/A      | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | Absent     | N/A      | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | Absent     | N/A      | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  CPU_0_Vcore               | Absent     | N/A      | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_MARGIN              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  MAX_DIMM_TEMP             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  SC_1_E810                 | Absent     | N/A      | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SC_2_E810                 | Absent     | N/A      | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SYS_PCH_TEMP              | Absent     | N/A      | N/A      | 5        | N/A      | N/A      | 82       | N/A      | Intake
sleeping 30 seconds
  SYS_V5                    | Absent     | N/A      | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | Absent     | N/A      | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | Absent     | N/A      | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | Absent     | N/A      | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  CPU_0_Vcore               | Absent     | N/A      | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  MAX_DIMM_TEMP             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  SYS_PCH_TEMP              | Absent     | N/A      | N/A      | 5        | N/A      | N/A      | 82       | N/A      | Intake
sleeping 30 seconds
  SYS_PCH_TEMP              | Absent     | N/A      | N/A      | 5        | N/A      | N/A      | 82       | N/A      | Intake
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
  SYS_V5                    | Absent     | N/A      | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | Absent     | N/A      | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | Absent     | N/A      | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | Absent     | N/A      | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  CPU_0_Vcore               | Absent     | N/A      | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_MARGIN              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  PSU_1_TEMP_2              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_1_TEMP_1              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  PSU_2_TEMP_2              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_2_TEMP_1              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  CPU_0_DIMM_C0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_D0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_A0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_B0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_G0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_H0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_E0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_F0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  MAX_DIMM_TEMP             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  PML_WEST_TEMP             | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  PML_LOCAL_TEMP            | Absent     | N/A      | N/A      | N/A      | N/A      | 80       | 85       | N/A      | Intake
  PML_VDD_TEMP              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 125      | N/A      | Intake
  PML_EAST_TEMP             | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  SC_1_E810                 | Absent     | N/A      | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SC_2_E810                 | Absent     | N/A      | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SSD_0_TEMP                | Absent     | N/A      | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  SSD_1_TEMP                | Absent     | N/A      | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  CPU_0_TEMP                | Absent     | N/A      | N/A      | N/A      | N/A      | 96       | 98       | N/A      | Intake
  SYS_FAN_1A                | Absent%    | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_1B                | Absent%    | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2A                | Absent%    | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2B                | Absent%    | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_1_FAN                 | Absent     | N/A      | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_2_FAN                 | Absent     | N/A      | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
sleeping 30 seconds
  SYS_V5                    | Absent     | N/A      | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | Absent     | N/A      | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | Absent     | N/A      | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | Absent     | N/A      | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  CPU_0_Vcore               | Absent     | N/A      | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_MARGIN              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  MAX_DIMM_TEMP             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  SC_1_E810                 | Absent     | N/A      | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SC_2_E810                 | Absent     | N/A      | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
  SYS_V5                    | Absent     | N/A      | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | Absent     | N/A      | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | Absent     | N/A      | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | Absent     | N/A      | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  CPU_0_Vcore               | Absent     | N/A      | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_MARGIN              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  MAX_DIMM_TEMP             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  SC_1_E810                 | Absent     | N/A      | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SC_2_E810                 | Absent     | N/A      | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
sleeping 30 seconds
  SYS_V5                    | Absent     | N/A      | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | Absent     | N/A      | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | Absent     | N/A      | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | Absent     | N/A      | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  CPU_0_Vcore               | Absent     | N/A      | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  MAX_DIMM_TEMP             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
  SYS_V5                    | Absent     | N/A      | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | Absent     | N/A      | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | Absent     | N/A      | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | Absent     | N/A      | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  CPU_0_Vcore               | Absent     | N/A      | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_MARGIN              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  PSU_1_TEMP_2              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_1_TEMP_1              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  PSU_2_TEMP_2              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_2_TEMP_1              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  CPU_0_DIMM_C0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_D0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_A0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_B0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_G0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_H0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_E0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_F0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  DIMM_VRABCD_TEMP          | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  DIMM_VREFGH_TEMP          | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  MAX_DIMM_TEMP             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  PML_WEST_TEMP             | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  PML_LOCAL_TEMP            | Absent     | N/A      | N/A      | N/A      | N/A      | 80       | 85       | N/A      | Intake
  PML_VDD_TEMP              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 125      | N/A      | Intake
  PML_EAST_TEMP             | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  SC_1_E810                 | Absent     | N/A      | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SC_2_E810                 | Absent     | N/A      | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SSD_0_TEMP                | Absent     | N/A      | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  SSD_1_TEMP                | Absent     | N/A      | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  SYS_PCH_TEMP              | Absent     | N/A      | N/A      | 5        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_TEMP                | Absent     | N/A      | N/A      | N/A      | N/A      | 96       | 98       | N/A      | Intake
  SYS_FAN_1A                | Absent%    | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_1B                | Absent%    | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2A                | Absent%    | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2B                | Absent%    | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_1_FAN                 | Absent     | N/A      | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_2_FAN                 | Absent     | N/A      | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
sleeping 30 seconds
  SYS_V5                    | Absent     | N/A      | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | Absent     | N/A      | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | Absent     | N/A      | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | Absent     | N/A      | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  CPU_0_Vcore               | Absent     | N/A      | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_MARGIN              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  MAX_DIMM_TEMP             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  SC_1_E810                 | Absent     | N/A      | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SC_2_E810                 | Absent     | N/A      | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
sleeping 30 seconds
  SYS_V5                    | Absent     | N/A      | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | Absent     | N/A      | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | Absent     | N/A      | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | Absent     | N/A      | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  CPU_0_Vcore               | Absent     | N/A      | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  MAX_DIMM_TEMP             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
  SYS_V5                    | Absent     | N/A      | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | Absent     | N/A      | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | Absent     | N/A      | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | Absent     | N/A      | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  CPU_0_Vcore               | Absent     | N/A      | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_MARGIN              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  PSU_1_TEMP_2              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_1_TEMP_1              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  PSU_2_TEMP_2              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_2_TEMP_1              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  MAX_DIMM_TEMP             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  PML_WEST_TEMP             | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  PML_LOCAL_TEMP            | Absent     | N/A      | N/A      | N/A      | N/A      | 80       | 85       | N/A      | Intake
  PML_VDD_TEMP              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 125      | N/A      | Intake
  PML_EAST_TEMP             | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  SC_1_E810                 | Absent     | N/A      | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SC_2_E810                 | Absent     | N/A      | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SSD_0_TEMP                | Absent     | N/A      | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  SSD_1_TEMP                | Absent     | N/A      | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  PSU_1_FAN                 | Absent     | N/A      | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_2_FAN                 | Absent     | N/A      | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
sleeping 30 seconds
  SYS_V5                    | Absent     | N/A      | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | Absent     | N/A      | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | Absent     | N/A      | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | Absent     | N/A      | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  CPU_0_Vcore               | Absent     | N/A      | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_MARGIN              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  MAX_DIMM_TEMP             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  SC_1_E810                 | Absent     | N/A      | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SC_2_E810                 | Absent     | N/A      | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
  SYS_V12                   | Absent     | N/A      | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | Absent     | N/A      | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | Absent     | N/A      | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  CPU_0_Vcore               | Absent     | N/A      | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_MARGIN              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  PSU_1_TEMP_2              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_1_TEMP_1              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  PSU_2_TEMP_2              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_2_TEMP_1              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  CPU_0_DIMM_C0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_D0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_A0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_B0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_G0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_H0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_E0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_F0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  DIMM_VRABCD_TEMP          | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  DIMM_VREFGH_TEMP          | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  MAX_DIMM_TEMP             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  PML_WEST_TEMP             | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  PML_LOCAL_TEMP            | Absent     | N/A      | N/A      | N/A      | N/A      | 80       | 85       | N/A      | Intake
  PML_VDD_TEMP              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 125      | N/A      | Intake
  PML_EAST_TEMP             | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  SC_1_E810                 | Absent     | N/A      | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SC_2_E810                 | Absent     | N/A      | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SSD_0_TEMP                | Absent     | N/A      | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  SSD_1_TEMP                | Absent     | N/A      | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  MB_HSC_TEMP               | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  SYS_PCH_TEMP              | Absent     | N/A      | N/A      | 5        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_TEMP                | Absent     | N/A      | N/A      | N/A      | N/A      | 96       | 98       | N/A      | Intake
  PSU_1_FAN                 | Absent     | N/A      | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_2_FAN                 | Absent     | N/A      | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
sleeping 30 seconds
  SYS_V5                    | Absent     | N/A      | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | Absent     | N/A      | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | Absent     | N/A      | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | Absent     | N/A      | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  CPU_0_Vcore               | Absent     | N/A      | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_MARGIN              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  MAX_DIMM_TEMP             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  SC_1_E810                 | Absent     | N/A      | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SC_2_E810                 | Absent     | N/A      | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
sleeping 30 seconds
  SYS_V5                    | Absent     | N/A      | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | Absent     | N/A      | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | Absent     | N/A      | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | Absent     | N/A      | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  CPU_0_Vcore               | Absent     | N/A      | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  MAX_DIMM_TEMP             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
sleeping 30 seconds
  SYS_V5                    | Absent     | N/A      | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | Absent     | N/A      | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | Absent     | N/A      | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | Absent     | N/A      | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  CPU_0_Vcore               | Absent     | N/A      | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_MARGIN              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  PSU_1_TEMP_2              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_1_TEMP_1              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  PSU_2_TEMP_2              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_2_TEMP_1              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  CPU_0_DIMM_C0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_D0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_A0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_B0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_G0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_H0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_E0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_F0             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  MAX_DIMM_TEMP             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  PML_WEST_TEMP             | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  PML_LOCAL_TEMP            | Absent     | N/A      | N/A      | N/A      | N/A      | 80       | 85       | N/A      | Intake
  PML_VDD_TEMP              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 125      | N/A      | Intake
  PML_EAST_TEMP             | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  SC_1_E810                 | Absent     | N/A      | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SC_2_E810                 | Absent     | N/A      | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SYS_PCH_TEMP              | Absent     | N/A      | N/A      | 5        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_TEMP                | Absent     | N/A      | N/A      | N/A      | N/A      | 96       | 98       | N/A      | Intake
  SYS_FAN_1A                | Absent%    | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_1B                | Absent%    | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2A                | Absent%    | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2B                | Absent%    | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_1_FAN                 | Absent     | N/A      | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_2_FAN                 | Absent     | N/A      | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
sleeping 30 seconds
  SYS_V5                    | Absent     | N/A      | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | Absent     | N/A      | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | Absent     | N/A      | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | Absent     | N/A      | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  CPU_0_Vcore               | Absent     | N/A      | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_MARGIN              | Absent     | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  MAX_DIMM_TEMP             | Absent     | N/A      | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  SC_1_E810                 | Absent     | N/A      | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SC_2_E810                 | Absent     | N/A      | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SYS_PCH_TEMP              | Absent     | N/A      | N/A      | 5        | N/A      | N/A      | 82       | N/A      | Intake
sleeping 30 seconds
  SYS_V5                    | Absent     | N/A      | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | Absent     | N/A      | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | Absent     | N/A      | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | Absent     | N/A      | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  CPU_0_Vcore               | Absent     | N/A      | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | Absent     | N/A      | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  SYS_PCH_TEMP              | Absent     | N/A      | N/A      | 5        | N/A      | N/A      | 82       | N/A      | Intake
sleeping 30 seconds
^C
[XXXXXX@welktxefnce-h-pe1util-vm01 ZT_FW]$
```

### Notes:  During OS boot up, it trys to load linux file, but its missing, it does not pause at that state, it timesout and reboots.. 
### Its in a reboot loop essentially... while its booting in bios post, sensors go absent, then it boots linux, but fails, sensors still report with Absent data.

