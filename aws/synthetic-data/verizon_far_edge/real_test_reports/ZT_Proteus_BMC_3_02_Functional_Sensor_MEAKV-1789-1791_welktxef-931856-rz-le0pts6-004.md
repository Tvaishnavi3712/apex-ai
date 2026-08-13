# ZT Proteus 3.02 BMC firmware validation
# ZT Proteus BIOS .30
# 10/17/25 James Patchett


## welktxef-931856-rz-le0pts6-004
BMC:  2607:f160:10:80b1:ce:40a:0:e003
OAM:  2607:f160:10:80b1:ce:40a:0:f403



### MEAKV-1789
### List All Sensor data in ipmitool
```sh
sudo -i 
ipmitool sensor
```

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ sudo su
root@controller-0:/var/home/XXXXXX# ipmitool sensor
CPU_0_PROCHOT    | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
CPU_0_STATUS     | 0x0        | discrete   | 0x8080| na        | na        | na        | na        | na        | na
CPU_0_Vcore      | 1.819      | Volts      | ok    | na        | 1.690     | na        | na        | 1.870     | na
CPU0DDR_ABC_1.2V | 1.231      | Volts      | ok    | na        | 1.134     | na        | na        | 1.256     | na
CPU0DDR_DEF_1.2V | 1.231      | Volts      | ok    | na        | 1.134     | na        | na        | 1.256     | na
CPU_0_DTS_TEMP   | -57.000    | degrees C  | ok    | na        | na        | na        | na        | na        | na
CPU_0_TEMP       | 41.000     | degrees C  | ok    | na        | na        | na        | 96.000    | 98.000    | na
CPU_0_MARGIN     | 46.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
CPU0_Power       | 97.000     | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_PCH_TEMP     | 26.000     | degrees C  | ok    | na        | 5.000     | na        | na        | 82.000    | na
CPU_0_DIMM_C0    | 29.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_D0    | 28.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_A0    | 27.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_B0    | 27.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_G0    | 28.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_H0    | 28.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_E0    | 28.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_F0    | 28.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
MAX_DIMM_TEMP    | 29.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
INLET_TEMP_L     | 23.000     | degrees C  | ok    | na        | -6.000    | na        | 50.000    | 59.000    | 61.000
INLET_TEMP_R     | 22.000     | degrees C  | ok    | na        | -6.000    | na        | 50.000    | 59.000    | 61.000
INLET_TEMP_MAX   | 23.000     | degrees C  | ok    | na        | -6.000    | na        | 50.000    | 59.000    | 61.000
OUTLET_TEMP_L    | 31.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
OUTLET_TEMP_R    | 32.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
OUTLET_TEMP_MAX  | 32.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 12625.000  | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1B       | 13500.000  | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_2A       | 12500.000  | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_2B       | 13625.000  | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1A_PWM   | 51.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1B_PWM   | 51.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_2A_PWM   | 51.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_2B_PWM   | 51.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_V1.05        | 1.055      | Volts      | ok    | na        | 0.993     | na        | na        | 1.097     | na
SYS_V12          | 12.270     | Volts      | ok    | na        | 11.348    | na        | na        | 12.552    | na
SYS_V3.3         | 3.339      | Volts      | ok    | na        | 3.104     | na        | na        | 3.431     | na
SYS_V5           | 5.061      | Volts      | ok    | na        | 4.725     | na        | na        | 5.225     | na
CPU_CUPS         | 19.000     | percent    | ok    | na        | na        | na        | na        | 100.000   | na
MB_HSC_TEMP      | 31.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 125.000   | na
DIMM_VREFGH_TEMP | 26.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 125.000   | na
DIMM_VRABCD_TEMP | 28.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 125.000   | na
RTC_Voltage      | 2.884      | Volts      | ok    | na        | 2.289     | na        | na        | 3.444     | na
MB_HSC_PIN       | 208.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
MB_HSC_PIN_AVG   | 284.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
MB_HSC_PEAK_PIN  | 412.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_1_STATUS     | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
PSU_2_STATUS     | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
PSU_1_FAN        | 4000.000   | RPM        | ok    | 800.000   | 1120.000  | na        | na        | na        | na
PSU_2_FAN        | 3840.000   | RPM        | ok    | 800.000   | 1120.000  | na        | na        | na        | na
PSU_1_TEMP_1     | 26.000     | degrees C  | ok    | na        | na        | na        | na        | 60.000    | 64.000
PSU_2_TEMP_1     | 26.000     | degrees C  | ok    | na        | na        | na        | na        | 60.000    | 64.000
PSU_1_TEMP_2     | 44.000     | degrees C  | ok    | na        | na        | na        | na        | 92.000    | 97.000
PSU_2_TEMP_2     | 45.000     | degrees C  | ok    | na        | na        | na        | na        | 92.000    | 97.000
PSU_POWER_IN     | 396.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_1_POWER_IN   | 204.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_2_POWER_IN   | 192.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_1_POWER_OUT  | 192.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_2_POWER_OUT  | 174.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_1_CURRENT_IN | 1.008      | Amps       | ok    | na        | na        | na        | na        | na        | na
PSU_2_CURRENT_IN | 0.882      | Amps       | ok    | na        | na        | na        | na        | na        | na
PSU1_CURRENT_OUT | 15.900     | Amps       | ok    | na        | na        | na        | na        | na        | na
PSU2_CURRENT_OUT | 14.310     | Amps       | ok    | na        | na        | na        | na        | na        | na
PWR_UNIT_REDUND  | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
PWR_UNIT_STATUS  | 0x0        | discrete   | 0x0080| na        | na        | na        | na        | na        | na
ACPI_STATE       | 0x0        | discrete   | 0x0180| na        | na        | na        | na        | na        | na
SSD_0_TEMP       | 28.000     | degrees C  | ok    | na        | 0.000     | na        | na        | 70.000    | 79.000
SSD_1_TEMP       | 29.000     | degrees C  | ok    | na        | 0.000     | na        | na        | 70.000    | 79.000
PML_WEST_TEMP    | 41.000     | degrees C  | ok    | na        | na        | na        | na        | 110.000   | 114.000
PML_LOCAL_TEMP   | 36.000     | degrees C  | ok    | na        | na        | na        | 80.000    | 85.000    | na
PML_VDD_TEMP     | 41.000     | degrees C  | ok    | na        | na        | na        | na        | 125.000   | na
PML_EAST_TEMP    | 41.000     | degrees C  | ok    | na        | na        | na        | na        | 110.000   | 114.000
SC_1_E810        | 33.000     | degrees C  | ok    | na        | 0.000     | 5.000     | 100.000   | 105.000   | 115.000
SC_2_E810        | 32.000     | degrees C  | ok    | na        | 0.000     | 5.000     | 100.000   | 105.000   | 115.000
root@controller-0:/var/home/XXXXXX#
```


### MEAKV-1790
### List All Sensor data in RedFish

### Command is ran from Ansible host in Lab
```sh
source ~/python_venvs/ansible_2.10.15/bin/activate
rf_sensor_list.py -u XXXXXX -p XXXXXX -r https://[2607:f160:10:80b1:ce:40a:0:e003]
```

```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ rf_sensor_list.py -u XXXXXX -p XXXXXX -r https://[2607:f160:10:80b1:ce:40a:0:e003]
Chassis 'Computer System Chassis' Status
  Sensor                    | Reading    | Health   | LF       | LC       | LNC      | UNC      | UC       | UF       | PhysicalContext
  State                     | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Redundancy 0 | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU_1_FAN State           | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU_2_FAN State           | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_FAN_1 State           | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_FAN_2 State           | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  CPU_0_DTS_TEMP            | -59        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  CPU_0_MARGIN              | 48         | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  CPU0_Power                | 96         | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  ACPI_STATE                | 32769      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  CPU_0_PROCHOT             | 32769      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU_1_TEMP_2              | 44         | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU_1_TEMP_1              | 26         | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU_2_TEMP_2              | 44         | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU_2_TEMP_1              | 26         | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  CPU_0_DIMM_C0             | 28         | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  CPU_0_DIMM_D0             | 27         | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  CPU_0_DIMM_A0             | 27         | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  CPU_0_DIMM_B0             | 26         | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  CPU_0_DIMM_G0             | 27         | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  CPU_0_DIMM_H0             | 27         | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  CPU_0_DIMM_E0             | 27         | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  CPU_0_DIMM_F0             | 28         | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  DIMM_VRABCD_TEMP          | 27         | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  DIMM_VREFGH_TEMP          | 25         | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  MAX_DIMM_TEMP             | 28         | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  CPU_CUPS                  | 20         | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_FAN_1A                | 19375      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PML_WEST_TEMP             | 40         | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PML_LOCAL_TEMP            | 34         | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PML_VDD_TEMP              | 40         | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PML_EAST_TEMP             | 39         | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SC_1_E810                 | 32         | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SC_2_E810                 | 31         | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_V5                    | 5.0608     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_V12                   | 12.2508    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SSD_0_TEMP                | 28         | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SSD_1_TEMP                | 29         | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_V3.3                  | 3.3338     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_V1.05                 | 1.0532     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  RTC_Voltage               | 2.884      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_FAN_1B                | 20500      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  MB_HSC_PEAK_PIN           | 412        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  INLET_TEMP_L              | 23         | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  INLET_TEMP_R              | 21         | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  MB_HSC_TEMP               | 31         | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  OUTLET_TEMP_L             | 31         | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  OUTLET_TEMP_R             | 33         | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_FAN_2A                | 18750      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  INLET_TEMP_MAX            | 23         | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  OUTLET_TEMP_MAX           | 33         | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  MB_HSC_PIN                | 280        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  MB_HSC_PIN_AVG            | 304        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_PCH_TEMP              | 26         | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU_1_STATUS              | 32769      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_FAN_2B                | 20375      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU_2_STATUS              | 32769      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU_1_POWER_OUT           | 222        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU_2_POWER_OUT           | 204        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU_1_CURRENT_IN          | 1.071      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU_2_CURRENT_IN          | 1.008      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PWR_UNIT_STATUS           | 32768      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PWR_UNIT_REDUND           | 32769      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU_POWER_IN              | 451        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU_1_POWER_IN            | 234        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU_2_POWER_IN            | 216        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU_1_FAN                 | 4000       | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU_2_FAN                 | 4000       | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  CPU_0_STATUS              | 32896      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU1_CURRENT_OUT          | 18.02      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU2_CURRENT_OUT          | 16.96      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_FAN_1A_PWM            | 78         | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_FAN_1B_PWM            | 78         | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  CPU_0_Vcore               | 1.8192     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  CPU0DDR_ABC_1.2V          | 1.2306     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_FAN_2A_PWM            | 78         | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  CPU0DDR_DEF_1.2V          | 1.2306     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  CPU_0_TEMP                | 39         | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_FAN_2B_PWM            | 78         | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A

(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 ~]$
```

### MEAKV-1791
### List all sensor and data for both previous BMC firmware version as well as new BMC firmware version
### Compare the results of both to ensure nothing new or if anything has changed in format or sensors   

### Command is ran from Ansible host in Lab
```sh
source ~/python_venvs/ansible_2.10.15/bin/activate
rf_sensor_list.py -u XXXXXX -p XXXXXX -r https://[2607:f160:10:80b1:ce:40a:0:e008]
```

### Target BMC 0.46 (new in test version)
### Target Subcloud welktxef-d931856-008
OAM: 2607:f160:10:80b1:ce:40a:0:f408
BMC: 2607:f160:10:80b1:ce:40a:0:e008

```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[2607:f160:10:80b1:ce:40a:0:e008]/redfish/v1/UpdateService/FirmwareInventory/BMC | jq .Version
"0.46.00"
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 ~]$
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ rf_sensor_list.py -u XXXXXX -p XXXXXX -r https://[2607:f160:10:80b1:ce:40a:0:e008]
Chassis 'Computer System Chassis' Status
  Sensor                    | Reading    | Health   | LF       | LC       | LNC      | UNC      | UC       | UF       | PhysicalContext
  State                     | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 212V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 186W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 213V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 162W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_V5                    | 5.014V     | OK       | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | 12.1944V   | OK       | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | 3.3287V    | OK       | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | 1.05156V   | OK       | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  RTC_Voltage               | 3.024V     | OK       | N/A      | 2.289    | N/A      | N/A      | 3.444    | N/A      | VoltageRegulator
  CPU_0_Vcore               | 1.808V     | OK       | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | 1.2269V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | 1.2232V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | -41Cel     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_MARGIN              | 30Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_PROCHOT             | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  PSU_1_TEMP_2              | 45Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_1_TEMP_1              | 27Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  PSU_2_TEMP_2              | 44Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_2_TEMP_1              | 26Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  CPU_0_DIMM_C0             | 40Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_D0             | 38Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_A0             | 37Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_B0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_G0             | 38Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_H0             | 37Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_E0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_F0             | 35Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  DIMM_VRABCD_TEMP          | 40Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  DIMM_VREFGH_TEMP          | 37Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  MAX_DIMM_TEMP             | 40Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  PML_WEST_TEMP             | 62Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  PML_LOCAL_TEMP            | 60Cel      | OK       | N/A      | N/A      | N/A      | 80       | 85       | N/A      | Intake
  PML_VDD_TEMP              | 68Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 125      | N/A      | Intake
  PML_EAST_TEMP             | 62Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  SC_1_E810                 | 44Cel      | OK       | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SC_2_E810                 | 40Cel      | OK       | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SSD_0_TEMP                | 30Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  SSD_1_TEMP                | 30Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  INLET_TEMP_L              | 27Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  INLET_TEMP_R              | 25Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  MB_HSC_TEMP               | 38Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  OUTLET_TEMP_L             | 43Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  OUTLET_TEMP_R             | 40Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  INLET_TEMP_MAX            | 27Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  OUTLET_TEMP_MAX           | 43Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  SYS_PCH_TEMP              | 32Cel      | OK       | N/A      | 5        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_TEMP                | 57Cel      | OK       | N/A      | N/A      | N/A      | 96       | 98       | N/A      | Intake
  SYS_FAN_1A                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_1B                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2A                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2B                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_1_FAN                 | 3840RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_2_FAN                 | 4000RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan

(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 ~]$
```

### Previous BMC 0.45 (new in test version)
### Target Subcloud welktxef-d931887-021 
OAM 2607:f160:10:9249:ce:40a:0:f409
BMC 2607:f160:10:9249:ce:40a:0:e015

```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[2607:f160:10:9249:ce:40a:0:e015]/redfish/v1/UpdateService/FirmwareInventory/BMC | jq .Version
"0.45.00"
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ rf_sensor_list.py -u XXXXXX -p XXXXXX -r https://[2607:f160:10:9249:ce:40a:0:e015]
Chassis 'Computer System Chassis' Status
  Sensor                    | Reading    | Health   | LF       | LC       | LNC      | UNC      | UC       | UF       | PhysicalContext
  State                     | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enable     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 213V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 162W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enable     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LineInpu | 212V       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay PowerCap | 1300W      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay LastPowe | 150W       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_V5                    | 5.053V     | OK       | N/A      | 4.7254   | N/A      | N/A      | 5.2246   | N/A      | VoltageRegulator
  SYS_V12                   | 12.1568V   | OK       | N/A      | 11.3484  | N/A      | N/A      | 12.5516  | N/A      | VoltageRegulator
  SYS_V3.3                  | 3.3287V    | OK       | N/A      | 3.1043   | N/A      | N/A      | 3.4307   | N/A      | VoltageRegulator
  SYS_V1.05                 | 1.05484V   | OK       | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | VoltageRegulator
  RTC_Voltage               | 3.031V     | OK       | N/A      | 2.289    | N/A      | N/A      | 3.444    | N/A      | VoltageRegulator
  CPU_0_Vcore               | 1.822V     | OK       | N/A      | 1.6904   | N/A      | N/A      | 1.8696   | N/A      | VoltageRegulator
  CPU0DDR_ABC_1.2V          | 1.2306V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU0DDR_DEF_1.2V          | 1.2306V    | OK       | N/A      | 1.1344   | N/A      | N/A      | 1.2565   | N/A      | VoltageRegulator
  CPU_0_DTS_TEMP            | -44Cel     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  CPU_0_MARGIN              | 33Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  PSU_1_TEMP_2              | 47Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_1_TEMP_1              | 27Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  PSU_2_TEMP_2              | 46Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 92       | 97       | Intake
  PSU_2_TEMP_1              | 27Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 60       | 64       | Intake
  CPU_0_DIMM_C0             | 38Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_D0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_A0             | 35Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_B0             | 35Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_G0             | 37Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_H0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_E0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_DIMM_F0             | 36Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  DIMM_VRABCD_TEMP          | 35Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  DIMM_VREFGH_TEMP          | 34Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  MAX_DIMM_TEMP             | 38Cel      | OK       | N/A      | 6        | N/A      | N/A      | 82       | N/A      | Intake
  PML_WEST_TEMP             | 56Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  PML_LOCAL_TEMP            | 54Cel      | OK       | N/A      | N/A      | N/A      | 80       | 85       | N/A      | Intake
  PML_VDD_TEMP              | 59Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 125      | N/A      | Intake
  PML_EAST_TEMP             | 56Cel      | OK       | N/A      | N/A      | N/A      | N/A      | 110      | 114      | Intake
  SC_1_E810                 | Absent     | N/A      | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SC_2_E810                 | Absent     | N/A      | N/A      | 0        | 5        | 100      | 105      | 115      | Intake
  SSD_0_TEMP                | 33Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  SSD_1_TEMP                | 35Cel      | OK       | N/A      | 0        | N/A      | N/A      | 70       | 79       | Intake
  INLET_TEMP_L              | 25Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  INLET_TEMP_R              | 23Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  MB_HSC_TEMP               | 38Cel      | OK       | N/A      | 6        | N/A      | N/A      | 125      | N/A      | Intake
  OUTLET_TEMP_L             | 42Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  OUTLET_TEMP_R             | 39Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  INLET_TEMP_MAX            | 25Cel      | OK       | N/A      | -6       | N/A      | 50       | 59       | 61       | Intake
  OUTLET_TEMP_MAX           | 42Cel      | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Intake
  SYS_PCH_TEMP              | 32Cel      | OK       | N/A      | 5        | N/A      | N/A      | 82       | N/A      | Intake
  CPU_0_TEMP                | 54Cel      | OK       | N/A      | N/A      | N/A      | 96       | 98       | N/A      | Intake
  SYS_FAN_1A                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_1B                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2A                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  SYS_FAN_2B                | 18%        | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_1_FAN                 | 3840RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan
  PSU_2_FAN                 | 3840RPM    | OK       | 800      | 1120     | N/A      | N/A      | N/A      | N/A      | Fan

(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 ~]$
```

### compare

```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ rf_sensor_list.py -u XXXXXX -p XXXXXX -r https://[2607:f160:10:9249:ce:40a:0:e015] | awk -F\| '{print $1}' > /tmp/e015.txt
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ rf_sensor_list.py -u XXXXXX -p XXXXXX -r https://[2607:f160:10:80b1:ce:40a:0:e008] | awk -F\| '{print $1}' > /tmp/e008.txt
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ diff /tmp/e015.txt /tmp/e008.txt
21a22
>   CPU_0_PROCHOT
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 ~]$
```

### Results
It appears we have a new sensor reporting in with BMC .46 firmware for CPU "CPU_0_PROCHOT", however we have not lost or changed any other sensor name or data type, all looks good from sensor comparison in redhat with previous versions.
