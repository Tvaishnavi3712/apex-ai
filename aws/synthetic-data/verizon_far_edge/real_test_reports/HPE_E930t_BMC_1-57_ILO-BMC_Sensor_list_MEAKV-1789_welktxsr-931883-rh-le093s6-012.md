# HPE ILO6 1.57 BIOS H11 v1.11
# HPE Sapphire Rapids E930t server
# 4/24/24 James Patchett - MTCE Lab VCPfe
# BMC/ILO Sensor validation MEAKV-1789

## welktxsr-931883-rh-le093s6-012
ILO:  2607:f160:0010:8803:ce:40a:0:e001
OAM:  2607:f160:0010:8803:ce:40a:0:f401

### List all sensors on the machine
### Validate no sensors are experiencing issues, or not showing data

```log

[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ IP=2607:f160:10:8803:ce:40a:0:e001
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ rf_sensor_list.py -u XXXXXX -p XXXXXX -r https://[$IP]
Chassis 'Computer System Chassis' Status
  Sensor                    | Reading    | Health   | LF       | LC       | LNC      | UNC      | UC       | UF       | PhysicalContext
  State                     | Starting   | Warning  | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  HpeServerPowerSupply Stat | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  HpeServerPowerSupply Line | 207V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  HpeServerPowerSupply Powe | 1500W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  HpeServerPowerSupply Last | 142W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  HpeServerPowerSupply Stat | Unavailabl | Critical | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  HpeServerPowerSupply Line | 0V         | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  HpeServerPowerSupply Powe | 1500W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  HpeServerPowerSupply Last | 0W         | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  01-Inlet Ambient          | 37Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 62       | 66       | Intake
  02-CPU 1 PkgTmp           | 82Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 91       | N/A      | CPU
  03-P1 DIMM 1-6            | 54Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 90       | N/A      | Memory
  04-P1 PMM 1-6             | 0Cel       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Memory
  05-P1 DIMM 7-12           | 61Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 90       | N/A      | Memory
  06-P1 PMM 7-12            | 0Cel       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Memory
  07-VR P1                  | 71Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | N/A      | SystemBoard
  08-Chipset                | 52Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 100      | N/A      | SystemBoard
  09-BMC                    | 60Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | N/A      | SystemBoard
  10-M2                     | 51Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 80       | N/A      | SystemBoard
  16-PCI 1 Zone             | 34Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 70       | 75       | SystemBoard
  18-PCI 2 Zone             | 34Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 70       | 75       | SystemBoard
  20-PCI 3 Zone             | 34Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 70       | 75       | SystemBoard
  21-PCI 4                  | 0Cel       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard
  22-PCI 4 Zone             | 0Cel       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard
  27-Sys Exhaust 1          | 62Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 85       | N/A      | SystemBoard
  15.1-PCI 1-Network contro | 69Cel      | OK       | N/A      | N/A      | N/A      | 95       | 105      | 115      | SystemBoard
  15.2-PCI 1-SFP28 (SFF-840 | 34Cel      | OK       | N/A      | N/A      | N/A      | 70       | 75       | N/A      | SystemBoard
  17.1-PCI 2-Network contro | 71Cel      | OK       | N/A      | N/A      | N/A      | 95       | 105      | 115      | SystemBoard
  19.1-PCI 3-Network contro | 64Cel      | OK       | N/A      | N/A      | N/A      | 95       | 105      | 115      | SystemBoard
  19.2-PCI 3-SFP28 (SFF-840 | 36Cel      | OK       | N/A      | N/A      | N/A      | 70       | 75       | N/A      | SystemBoard
  Fan 1                     | 17%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard
  Fan 2                     | 17%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard
  Fan 3                     | 17%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard
  Fan 4                     | 17%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard
  Fan 5                     | 17%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard
  Fan 6                     | 17%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard

Chassis 'HPE EL8000t     ' Status
  Sensor                    | Reading    | Health   | LF       | LC       | LNC      | UNC      | UC       | UF       | PhysicalContext

[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$

```
### This host has a missing power supply cord, and thus shows missing data for PSU
```log

  Sensor                    | Reading    | Health   | LF       | LC       | LNC      | UNC      | UC       | UF       | PhysicalContext
  State                     | Starting   | Warning  | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
 
"Missing power cord"
  HpeServerPowerSupply Stat | Unavailabl | Critical | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  HpeServerPowerSupply Line | 0V         | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  HpeServerPowerSupply Last | 0W         | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A

"Memory Option that we do not use we can ignore these missing"  
  04-P1 PMM 1-6             | 0Cel       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Memory
  06-P1 PMM 7-12            | 0Cel       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Memory

"Due to missing PCI card in SLOT 4, we can ignore these missing"
  21-PCI 4                  | 0Cel       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard
  22-PCI 4 Zone             | 0Cel       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard
  
```

### Pulled senor info from a e930t that has dual power cords feeding it, just do show and prove sensors work properly all is setup properly :-)

```log
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ IP=2607:f160:10:80b1:ce:40a:0:e002
[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ rf_sensor_list.py -u XXXXXX -p XXXXXX -r https://[$IP]
Chassis 'Computer System Chassis' Status
  Sensor                    | Reading    | Health   | LF       | LC       | LNC      | UNC      | UC       | UF       | PhysicalContext
  State                     | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  HpeServerPowerSupply Stat | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  HpeServerPowerSupply Line | 213V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  HpeServerPowerSupply Powe | 1500W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  HpeServerPowerSupply Last | 139W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  HpeServerPowerSupply Stat | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  HpeServerPowerSupply Line | 214V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  HpeServerPowerSupply Powe | 1500W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  HpeServerPowerSupply Last | 139W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  01-Inlet Ambient          | 36Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 62       | 66       | Intake
  02-CPU 1 PkgTmp           | 76Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 91       | N/A      | CPU
  03-P1 DIMM 1-6            | 51Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 90       | N/A      | Memory
  04-P1 PMM 1-6             | 0Cel       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Memory
  05-P1 DIMM 7-12           | 60Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 90       | N/A      | Memory
  06-P1 PMM 7-12            | 0Cel       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Memory
  07-VR P1                  | 67Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | N/A      | SystemBoard
  08-Chipset                | 57Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 100      | N/A      | SystemBoard
  09-BMC                    | 60Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | N/A      | SystemBoard
  10-M2                     | 50Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 80       | N/A      | SystemBoard
  16-PCI 1 Zone             | 37Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 70       | 75       | SystemBoard
  18-PCI 2 Zone             | 37Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 70       | 75       | SystemBoard
  20-PCI 3 Zone             | 37Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 70       | 75       | SystemBoard
  21-PCI 4                  | 0Cel       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard
  22-PCI 4 Zone             | 0Cel       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard
  27-Sys Exhaust 1          | 59Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 85       | N/A      | SystemBoard
  15.1-PCI 1-Network contro | 79Cel      | OK       | N/A      | N/A      | N/A      | 95       | 105      | 115      | SystemBoard
  15.2-PCI 1-SFP28 (SFF-840 | 46Cel      | OK       | N/A      | N/A      | N/A      | 73       | 78       | N/A      | SystemBoard
  15.3-PCI 1-SFP28 (SFF-840 | 41Cel      | OK       | N/A      | N/A      | N/A      | 70       | 75       | N/A      | SystemBoard
  15.4-PCI 1-SFP28 (SFF-840 | 42Cel      | OK       | N/A      | N/A      | N/A      | 70       | 75       | N/A      | SystemBoard
  15.5-PCI 1-SFP28 (SFF-840 | 42Cel      | OK       | N/A      | N/A      | N/A      | 70       | 75       | N/A      | SystemBoard
  17.1-PCI 2-Network contro | 82Cel      | OK       | N/A      | N/A      | N/A      | 95       | 105      | 115      | SystemBoard
  17.2-PCI 2-SFP28 (SFF-840 | 39Cel      | OK       | N/A      | N/A      | N/A      | 70       | 75       | N/A      | SystemBoard
  17.3-PCI 2-SFP28 (SFF-840 | 41Cel      | OK       | N/A      | N/A      | N/A      | 70       | 75       | N/A      | SystemBoard
  17.4-PCI 2-SFP28 (SFF-840 | 41Cel      | OK       | N/A      | N/A      | N/A      | 70       | 75       | N/A      | SystemBoard
  19.1-PCI 3-Network contro | 71Cel      | OK       | N/A      | N/A      | N/A      | 95       | 105      | 115      | SystemBoard
  19.2-PCI 3-SFP28 (SFF-840 | 42Cel      | OK       | N/A      | N/A      | N/A      | 73       | 78       | N/A      | SystemBoard
  19.3-PCI 3-SFP28 (SFF-840 | 37Cel      | OK       | N/A      | N/A      | N/A      | 70       | 75       | N/A      | SystemBoard
  Fan 1                     | 15%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard
  Fan 2                     | 15%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard
  Fan 3                     | 15%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard
  Fan 4                     | 15%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard
  Fan 5                     | 15%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard
  Fan 6                     | 15%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | SystemBoard

Chassis 'HPE EL8000t     ' Status
  Sensor                    | Reading    | Health   | LF       | LC       | LNC      | UNC      | UC       | UF       | PhysicalContext

[XXXXXX@welktxefnce-h-pe1util-vm01 ~]$

```

### As you see from above, power supplies reporting properly with dual power cords, and other missing data in sensors are showing same as other e930t

### Test has PASSED
