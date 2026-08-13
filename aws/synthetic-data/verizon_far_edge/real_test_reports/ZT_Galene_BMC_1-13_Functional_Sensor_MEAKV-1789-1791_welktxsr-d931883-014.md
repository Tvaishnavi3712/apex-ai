# Firmware validation
# ZT Galene BMC 1.13
# 2/6/25 James Patchett

## Target Controller rchltxib-c000000-001
Controller-0 iLO 2607:f160:a:d02e:cd:fe0::8006 
Controller-1 iLO 2607:f160:a:d02e:cd:fe0::8007
Worker-0 iLO 2607:f160:a:d02e:cd:fe0::8008 
OAM 2607:f160:0:3049:cd:290:0:10

## Target Subcloud welktxsr-d931883-014
OAM: 2607:f160:10:8803:ce:40a:0:f405
BMC: 2607:f160:10:8803:ce:40a:0:e005

ipmitool -I lanplus -U XXXXXX -P XXXXXX -H 2607:f160:10:8803:ce:40a:0:e005 sol activate


### MEAKV-1789
### List All Sensor data in ipmitool
```sh
sudo -i 
ipmitool sensor
```

```log
root@controller-0:~# ipmitool sensor
PSU1_CURRENT_OUT | 12.000     | Amps       | ok    | na        | na        | na        | na        | na        | na
PSU2_CURRENT_OUT | 11.000     | Amps       | ok    | na        | na        | na        | na        | na        | na
PSU_1_CURRENT_IN | 0.780      | Amps       | ok    | na        | na        | na        | na        | na        | na
PSU_2_CURRENT_IN | 0.702      | Amps       | ok    | na        | na        | na        | na        | na        | na
PSU_1_STATUS     | 0x0        | discrete   | 0x0000| na        | na        | na        | na        | na        | na
PSU_2_STATUS     | 0x0        | discrete   | 0x0000| na        | na        | na        | na        | na        | na
CPU_0_STATUS     | 0x7        | discrete   | 0x0000| na        | na        | na        | na        | na        | na
CPU_0_PROCHOT    | 0x0        | discrete   | 0x0100| na        | na        | na        | na        | na        | na
SYS_FAN_1_PWM    | 14.896     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_2_PWM    | 14.896     | percent    | ok    | na        | na        | na        | na        | na        | na
PSU_1_FAN        | 4012.000   | RPM        | ok    | na        | 826.000   | 1062.000  | na        | na        | na
PSU_2_FAN        | 4012.000   | RPM        | ok    | na        | 826.000   | 1062.000  | na        | na        | na
SYS_FAN_1A       | 3762.000   | RPM        | ok    | na        | 1026.000  | na        | na        | 28500.000 | na
SYS_FAN_1B       | 3648.000   | RPM        | ok    | na        | 1026.000  | na        | na        | 28500.000 | na
SYS_FAN_2A       | 3762.000   | RPM        | ok    | na        | 1026.000  | na        | na        | 28500.000 | na
SYS_FAN_2B       | 3648.000   | RPM        | ok    | na        | 1026.000  | na        | na        | 28500.000 | na
CPU0_Power       | 66.000     | Watts      | ok    | na        | na        | na        | na        | na        | na
MB_HSC_PEAK_PIN  | 362.670    | Watts      | ok    | na        | na        | na        | na        | na        | na
MB_HSC_PIN       | 131.880    | Watts      | ok    | na        | na        | na        | na        | na        | na
MB_HSC_PIN_AVG   | 235.500    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_1_POWER_IN   | 165.200    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_1_POWER_OUT  | 141.600    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_2_POWER_IN   | 141.600    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_2_POWER_OUT  | 129.800    | Watts      | ok    | na        | na        | na        | na        | na        | na
PSU_POWER_IN     | 306.800    | Watts      | ok    | na        | na        | na        | na        | na        | na
PWR_UNIT_REDUND  | 0x0        | discrete   | 0x0000| na        | na        | na        | na        | na        | na
PWR_UNIT_STATUS  | 0x0        | discrete   | 0x0000| na        | na        | na        | na        | na        | na
CPU_0_DIMM_A0    | 39.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_B0    | 37.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_C0    | 36.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_D0    | 36.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_E0    | 39.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_F0    | 37.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_G0    | 36.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DIMM_H0    | 35.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
CPU_0_DTS_TEMP   | -43.000    | degrees C  | ok    | na        | na        | na        | na        | na        | na
CPU_0_MARGIN     | 36.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
CPU_0_TEMP       | 47.000     | degrees C  | ok    | na        | na        | na        | 89.000    | 91.000    | na
DIMM_VR_TEMP     | 39.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 125.000   | na
INLET_TEMP_L     | 25.000     | degrees C  | ok    | na        | -6.000    | na        | 50.000    | 59.000    | 61.000
INLET_TEMP_MAX   | 26.000     | degrees C  | ok    | na        | -6.000    | na        | 50.000    | 59.000    | 61.000
INLET_TEMP_R     | 26.000     | degrees C  | ok    | na        | -6.000    | na        | 50.000    | 59.000    | 61.000
MAX_DIMM_TEMP    | 39.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 82.000    | na
MB_HSC_TEMP      | 37.000     | degrees C  | ok    | na        | 6.000     | na        | na        | 125.000   | na
OUTLET_TEMP_L    | 40.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
OUTLET_TEMP_MAX  | 40.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
OUTLET_TEMP_R    | 37.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
PDB_1_TEMP       | 35.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
PSU_1_TEMP_1     | 28.000     | degrees C  | ok    | na        | na        | na        | na        | 60.000    | 64.000
PSU_1_TEMP_2     | 45.000     | degrees C  | ok    | na        | na        | na        | na        | 92.000    | 97.000
PSU_2_TEMP_1     | 28.000     | degrees C  | ok    | na        | na        | na        | na        | 60.000    | 64.000
PSU_2_TEMP_2     | 46.000     | degrees C  | ok    | na        | na        | na        | na        | 92.000    | 97.000
RISER_TEMP       | 26.000     | degrees C  | ok    | na        | na        | na        | na        | na        | na
SC_1_E810        | 53.000     | degrees C  | ok    | na        | 0.000     | 5.000     | 100.000   | 105.000   | 115.000
SC_2_E810        | 48.000     | degrees C  | ok    | na        | 0.000     | 5.000     | 100.000   | 105.000   | 115.000
SC_3_E810        | 43.000     | degrees C  | ok    | na        | 0.000     | 5.000     | 100.000   | 105.000   | 115.000
SSD_0_TEMP       | 33.000     | degrees C  | ok    | na        | 0.000     | na        | na        | 80.000    | 97.000
SSD_1_TEMP       | 31.000     | degrees C  | ok    | na        | 0.000     | na        | na        | 80.000    | 97.000
SYS_PCH_TEMP     | 41.000     | degrees C  | ok    | na        | 5.000     | na        | na        | 82.000    | na
BMC_CPU          | 16.000     | percent    | ok    | na        | na        | na        | na        | na        | na
BMC_CPU_Kernel   | 8.000      | percent    | ok    | na        | na        | na        | na        | na        | na
BMC_CPU_User     | 8.000      | percent    | ok    | na        | na        | na        | na        | na        | na
BMC_Memory       | 17.000     | percent    | ok    | na        | na        | na        | na        | na        | na
BMC_Storage_RW   | 4.000      | percent    | ok    | na        | na        | na        | na        | 85.000    | na
BMC_Storage_TMP  | 0.000      | percent    | ok    | na        | na        | na        | na        | 85.000    | na
CPU_CUPS         | 2.352      | percent    | ok    | na        | na        | na        | na        | na        | na
CPU0VCCD_1_1V    | 1.166      | Volts      | ok    | na        | 1.049     | na        | na        | 1.196     | na
CPU_0_Vcore      | 1.823      | Volts      | ok    | na        | 1.686     | na        | na        | 1.872     | na
PSU_1_VOLT_IN    | 213.580    | Volts      | ok    | na        | na        | na        | na        | na        | na
PSU_1_VOLT_OUT   | 12.000     | Volts      | ok    | na        | na        | na        | na        | na        | na
PSU_2_VOLT_IN    | 213.580    | Volts      | ok    | na        | na        | na        | na        | na        | na
PSU_2_VOLT_OUT   | 12.000     | Volts      | ok    | na        | na        | na        | na        | na        | na
RTC_Voltage      | 3.028      | Volts      | ok    | na        | 2.293     | na        | na        | 3.440     | na
SYS_V1_05        | 1.048      | Volts      | ok    | na        | 0.989     | na        | na        | 1.096     | na
SYS_V3_3         | 3.304      | Volts      | ok    | na        | 3.115     | na        | na        | 3.422     | na
SYS_V5           | 5.040      | Volts      | ok    | na        | 4.716     | na        | na        | 5.220     | na
SYS_V12          | 12.267     | Volts      | ok    | na        | 11.310    | na        | na        | 12.528    | na
root@controller-0:~#
```


### MEAKV-1790
### List All Sensor data in RedFish

### Command is ran from Ansible host in Lab
```sh
source ~/python_venvs/ansible_2.10.15/bin/activate
rf_sensor_list.py -u XXXXXX -p XXXXXX -r https://[2607:f160:10:8803:ce:40a:0:e005]
```

```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 ZT-Galene-BMC-update-v1.13]$ rf_sensor_list.py -u XXXXXX -p XXXXXX -r https://[2607:f160:10:8803:ce:40a:0:e005]
Chassis 'System' Status
  Sensor                    | Reading    | Health   | LF       | LC       | LNC      | UNC      | UC       | UF       | PhysicalContext
  State                     | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Redundancy 0 | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_FAN_1 State           | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_FAN_2 State           | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU1_CURRENT_OUT          | 12.234A    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU2_CURRENT_OUT          | 10.593A    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU_1_CURRENT_IN          | 0.773A     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU_2_CURRENT_IN          | 0.695A     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU_1_STATUS              | 0          | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU_2_STATUS              | 0          | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  CPU_0_STATUS              | 7          | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  CPU_0_PROCHOT             | 0          | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_FAN_1_PWM             | 14.9019607 | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_FAN_2_PWM             | 14.9019607 | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU_1_FAN                 | 4000.0RPM  | OK       | N/A      | 800.0    | 1120.0   | N/A      | N/A      | N/A      | N/A
  PSU_2_FAN                 | 4000.0RPM  | OK       | N/A      | 800.0    | 1120.0   | N/A      | N/A      | N/A      | N/A
  SYS_FAN_1A                | 3720.0RPM  | OK       | N/A      | 1000.0   | N/A      | N/A      | 28500.0  | N/A      | N/A
  SYS_FAN_1B                | 3600.0RPM  | OK       | N/A      | 1000.0   | N/A      | N/A      | 28500.0  | N/A      | N/A
  SYS_FAN_2A                | 3780.0RPM  | OK       | N/A      | 1000.0   | N/A      | N/A      | 28500.0  | N/A      | N/A
  SYS_FAN_2B                | 3600.0RPM  | OK       | N/A      | 1000.0   | N/A      | N/A      | 28500.0  | N/A      | N/A
  CPU0_Power                | 70.133W    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  MB_HSC_PEAK_PIN           | 363.071895 | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  MB_HSC_PIN                | 132.352941 | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  MB_HSC_PIN_AVG            | 189.878963 | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU_1_POWER_IN            | 164.5W     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU_1_POWER_OUT           | 148.75W    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU_2_POWER_IN            | 146.5W     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU_2_POWER_OUT           | 129.25W    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU_POWER_IN              | 311.0W     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PWR_UNIT_REDUND           | 0          | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PWR_UNIT_STATUS           | 0          | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  CPU_0_DIMM_A0             | 41.0Cel    | OK       | N/A      | 6.0      | N/A      | N/A      | 82.0     | N/A      | N/A
  CPU_0_DIMM_B0             | 39.0Cel    | OK       | N/A      | 6.0      | N/A      | N/A      | 82.0     | N/A      | N/A
  CPU_0_DIMM_C0             | 38.0Cel    | OK       | N/A      | 6.0      | N/A      | N/A      | 82.0     | N/A      | N/A
  CPU_0_DIMM_D0             | 38.0Cel    | OK       | N/A      | 6.0      | N/A      | N/A      | 82.0     | N/A      | N/A
  CPU_0_DIMM_E0             | 41.0Cel    | OK       | N/A      | 6.0      | N/A      | N/A      | 82.0     | N/A      | N/A
  CPU_0_DIMM_F0             | 39.0Cel    | OK       | N/A      | 6.0      | N/A      | N/A      | 82.0     | N/A      | N/A
  CPU_0_DIMM_G0             | 38.0Cel    | OK       | N/A      | 6.0      | N/A      | N/A      | 82.0     | N/A      | N/A
  CPU_0_DIMM_H0             | 36.0Cel    | OK       | N/A      | 6.0      | N/A      | N/A      | 82.0     | N/A      | N/A
  CPU_0_DTS_TEMP            | -38.5Cel   | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  CPU_0_MARGIN              | 33.109Cel  | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  CPU_0_TEMP                | 49.063Cel  | OK       | N/A      | N/A      | N/A      | 89.0     | 91.0     | N/A      | N/A
  DIMM_VR_TEMP              | 39.0Cel    | OK       | N/A      | 6.0      | N/A      | N/A      | 125.0    | N/A      | N/A
  INLET_TEMP_L              | 25.0Cel    | OK       | N/A      | -6.0     | N/A      | 50.0     | 59.0     | 61.0     | N/A
  INLET_TEMP_MAX            | 26.0Cel    | OK       | N/A      | -6.0     | N/A      | 50.0     | 59.0     | 61.0     | N/A
  INLET_TEMP_R              | 26.0Cel    | OK       | N/A      | -6.0     | N/A      | 50.0     | 59.0     | 61.0     | N/A
  MAX_DIMM_TEMP             | 41.0Cel    | OK       | N/A      | 6.0      | N/A      | N/A      | 82.0     | N/A      | N/A
  MB_HSC_TEMP               | 38.333Cel  | OK       | N/A      | 6.0      | N/A      | N/A      | 125.0    | N/A      | N/A
  OUTLET_TEMP_L             | 42.0Cel    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  OUTLET_TEMP_MAX           | 42.0Cel    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  OUTLET_TEMP_R             | 39.0Cel    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PDB_1_TEMP                | 35.125Cel  | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU_1_TEMP_1              | 28.0Cel    | OK       | N/A      | N/A      | N/A      | N/A      | 60.0     | 64.0     | N/A
  PSU_1_TEMP_2              | 45.25Cel   | OK       | N/A      | N/A      | N/A      | N/A      | 92.0     | 97.0     | N/A
  PSU_2_TEMP_1              | 27.75Cel   | OK       | N/A      | N/A      | N/A      | N/A      | 60.0     | 64.0     | N/A
  PSU_2_TEMP_2              | 45.5Cel    | OK       | N/A      | N/A      | N/A      | N/A      | 92.0     | 97.0     | N/A
  RISER_TEMP                | 26.5Cel    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SC_1_E810                 | 54.0Cel    | OK       | N/A      | 0.0      | 5.0      | 100.0    | 105.0    | 115.0    | N/A
  SC_2_E810                 | 48.0Cel    | OK       | N/A      | 0.0      | 5.0      | 100.0    | 105.0    | 115.0    | N/A
  SC_3_E810                 | 43.0Cel    | OK       | N/A      | 0.0      | 5.0      | 100.0    | 105.0    | 115.0    | N/A
  SSD_0_TEMP                | 34.0Cel    | OK       | N/A      | 0.0      | N/A      | N/A      | 80.0     | 97.0     | N/A
  SSD_1_TEMP                | 31.0Cel    | OK       | N/A      | 0.0      | N/A      | N/A      | 80.0     | 97.0     | N/A
  SYS_PCH_TEMP              | 42.0Cel    | OK       | N/A      | 5.0      | N/A      | N/A      | 82.0     | N/A      | N/A
  BMC_CPU                   | 15.6440931 | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  BMC_CPU_Kernel            | 7.70737455 | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  BMC_CPU_User              | 7.91372078 | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  BMC_Memory                | 17.0470969 | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  BMC_Storage_RW            | 4.25595238 | OK       | N/A      | N/A      | N/A      | N/A      | 85.0     | N/A      | N/A
  BMC_Storage_TMP           | 0.00535843 | OK       | N/A      | N/A      | N/A      | N/A      | 85.0     | N/A      | N/A
  CPU_CUPS                  | 1.70505339 | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  CPU0VCCD_1_1V             | 1.164V     | OK       | N/A      | 1.049    | N/A      | N/A      | 1.196    | N/A      | N/A
  CPU_0_Vcore               | 1.821V     | OK       | N/A      | 1.69     | N/A      | N/A      | 1.87     | N/A      | N/A
  PSU_1_VOLT_IN             | 214.25V    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU_1_VOLT_OUT            | 12.16V     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU_2_VOLT_IN             | 213.25V    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU_2_VOLT_OUT            | 12.232V    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  RTC_Voltage               | 3.018V     | OK       | N/A      | 2.289    | N/A      | N/A      | 3.444    | N/A      | N/A
  SYS_V12                   | 12.2655V   | OK       | N/A      | 11.348   | N/A      | N/A      | 12.552   | N/A      | N/A
  SYS_V1_05                 | 1.0497V    | OK       | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | N/A
  SYS_V3_3                  | 3.306V     | OK       | N/A      | 3.104    | N/A      | N/A      | 3.431    | N/A      | N/A
  SYS_V5                    | 5.0441V    | OK       | N/A      | 4.725    | N/A      | N/A      | 5.225    | N/A      | N/A

(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 ZT-Galene-BMC-update-v1.13]$
```

### MEAKV-1791
### List all sensor and data for both previous BMC firmware version as well as new BMC firmware version
### Compare the results of both to ensure nothing new or if anything has changed in format or sensors   

### Command is ran from Ansible host in Lab
```sh
source ~/python_venvs/ansible_2.10.15/bin/activate
rf_sensor_list.py -u XXXXXX -p XXXXXX -r https://[2607:f160:10:8803:ce:40a:0:e005]
```

### BMC 1.13 sensors


```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 ZT-Galene-BMC-update-v1.13]$ rf_sensor_list.py -u XXXXXX -p XXXXXX -r https://[2607:f160:10:8803:ce:40a:0:e005]
Chassis 'System' Status
  Sensor                    | Reading    | Health   | LF       | LC       | LNC      | UNC      | UC       | UF       | PhysicalContext
  State                     | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Bay State    | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  Power Supply Redundancy 0 | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_FAN_1 State           | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_FAN_2 State           | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU1_CURRENT_OUT          | 12.234A    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU2_CURRENT_OUT          | 10.593A    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU_1_CURRENT_IN          | 0.773A     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU_2_CURRENT_IN          | 0.695A     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU_1_STATUS              | 0          | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU_2_STATUS              | 0          | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  CPU_0_STATUS              | 7          | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  CPU_0_PROCHOT             | 0          | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_FAN_1_PWM             | 14.9019607 | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_FAN_2_PWM             | 14.9019607 | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU_1_FAN                 | 4000.0RPM  | OK       | N/A      | 800.0    | 1120.0   | N/A      | N/A      | N/A      | N/A
  PSU_2_FAN                 | 4000.0RPM  | OK       | N/A      | 800.0    | 1120.0   | N/A      | N/A      | N/A      | N/A
  SYS_FAN_1A                | 3720.0RPM  | OK       | N/A      | 1000.0   | N/A      | N/A      | 28500.0  | N/A      | N/A
  SYS_FAN_1B                | 3600.0RPM  | OK       | N/A      | 1000.0   | N/A      | N/A      | 28500.0  | N/A      | N/A
  SYS_FAN_2A                | 3780.0RPM  | OK       | N/A      | 1000.0   | N/A      | N/A      | 28500.0  | N/A      | N/A
  SYS_FAN_2B                | 3600.0RPM  | OK       | N/A      | 1000.0   | N/A      | N/A      | 28500.0  | N/A      | N/A
  CPU0_Power                | 70.133W    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  MB_HSC_PEAK_PIN           | 363.071895 | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  MB_HSC_PIN                | 132.352941 | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  MB_HSC_PIN_AVG            | 189.878963 | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU_1_POWER_IN            | 164.5W     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU_1_POWER_OUT           | 148.75W    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU_2_POWER_IN            | 146.5W     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU_2_POWER_OUT           | 129.25W    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU_POWER_IN              | 311.0W     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PWR_UNIT_REDUND           | 0          | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PWR_UNIT_STATUS           | 0          | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  CPU_0_DIMM_A0             | 41.0Cel    | OK       | N/A      | 6.0      | N/A      | N/A      | 82.0     | N/A      | N/A
  CPU_0_DIMM_B0             | 39.0Cel    | OK       | N/A      | 6.0      | N/A      | N/A      | 82.0     | N/A      | N/A
  CPU_0_DIMM_C0             | 38.0Cel    | OK       | N/A      | 6.0      | N/A      | N/A      | 82.0     | N/A      | N/A
  CPU_0_DIMM_D0             | 38.0Cel    | OK       | N/A      | 6.0      | N/A      | N/A      | 82.0     | N/A      | N/A
  CPU_0_DIMM_E0             | 41.0Cel    | OK       | N/A      | 6.0      | N/A      | N/A      | 82.0     | N/A      | N/A
  CPU_0_DIMM_F0             | 39.0Cel    | OK       | N/A      | 6.0      | N/A      | N/A      | 82.0     | N/A      | N/A
  CPU_0_DIMM_G0             | 38.0Cel    | OK       | N/A      | 6.0      | N/A      | N/A      | 82.0     | N/A      | N/A
  CPU_0_DIMM_H0             | 36.0Cel    | OK       | N/A      | 6.0      | N/A      | N/A      | 82.0     | N/A      | N/A
  CPU_0_DTS_TEMP            | -38.5Cel   | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  CPU_0_MARGIN              | 33.109Cel  | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  CPU_0_TEMP                | 49.063Cel  | OK       | N/A      | N/A      | N/A      | 89.0     | 91.0     | N/A      | N/A
  DIMM_VR_TEMP              | 39.0Cel    | OK       | N/A      | 6.0      | N/A      | N/A      | 125.0    | N/A      | N/A
  INLET_TEMP_L              | 25.0Cel    | OK       | N/A      | -6.0     | N/A      | 50.0     | 59.0     | 61.0     | N/A
  INLET_TEMP_MAX            | 26.0Cel    | OK       | N/A      | -6.0     | N/A      | 50.0     | 59.0     | 61.0     | N/A
  INLET_TEMP_R              | 26.0Cel    | OK       | N/A      | -6.0     | N/A      | 50.0     | 59.0     | 61.0     | N/A
  MAX_DIMM_TEMP             | 41.0Cel    | OK       | N/A      | 6.0      | N/A      | N/A      | 82.0     | N/A      | N/A
  MB_HSC_TEMP               | 38.333Cel  | OK       | N/A      | 6.0      | N/A      | N/A      | 125.0    | N/A      | N/A
  OUTLET_TEMP_L             | 42.0Cel    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  OUTLET_TEMP_MAX           | 42.0Cel    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  OUTLET_TEMP_R             | 39.0Cel    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PDB_1_TEMP                | 35.125Cel  | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU_1_TEMP_1              | 28.0Cel    | OK       | N/A      | N/A      | N/A      | N/A      | 60.0     | 64.0     | N/A
  PSU_1_TEMP_2              | 45.25Cel   | OK       | N/A      | N/A      | N/A      | N/A      | 92.0     | 97.0     | N/A
  PSU_2_TEMP_1              | 27.75Cel   | OK       | N/A      | N/A      | N/A      | N/A      | 60.0     | 64.0     | N/A
  PSU_2_TEMP_2              | 45.5Cel    | OK       | N/A      | N/A      | N/A      | N/A      | 92.0     | 97.0     | N/A
  RISER_TEMP                | 26.5Cel    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SC_1_E810                 | 54.0Cel    | OK       | N/A      | 0.0      | 5.0      | 100.0    | 105.0    | 115.0    | N/A
  SC_2_E810                 | 48.0Cel    | OK       | N/A      | 0.0      | 5.0      | 100.0    | 105.0    | 115.0    | N/A
  SC_3_E810                 | 43.0Cel    | OK       | N/A      | 0.0      | 5.0      | 100.0    | 105.0    | 115.0    | N/A
  SSD_0_TEMP                | 34.0Cel    | OK       | N/A      | 0.0      | N/A      | N/A      | 80.0     | 97.0     | N/A
  SSD_1_TEMP                | 31.0Cel    | OK       | N/A      | 0.0      | N/A      | N/A      | 80.0     | 97.0     | N/A
  SYS_PCH_TEMP              | 42.0Cel    | OK       | N/A      | 5.0      | N/A      | N/A      | 82.0     | N/A      | N/A
  BMC_CPU                   | 15.6440931 | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  BMC_CPU_Kernel            | 7.70737455 | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  BMC_CPU_User              | 7.91372078 | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  BMC_Memory                | 17.0470969 | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  BMC_Storage_RW            | 4.25595238 | OK       | N/A      | N/A      | N/A      | N/A      | 85.0     | N/A      | N/A
  BMC_Storage_TMP           | 0.00535843 | OK       | N/A      | N/A      | N/A      | N/A      | 85.0     | N/A      | N/A
  CPU_CUPS                  | 1.70505339 | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  CPU0VCCD_1_1V             | 1.164V     | OK       | N/A      | 1.049    | N/A      | N/A      | 1.196    | N/A      | N/A
  CPU_0_Vcore               | 1.821V     | OK       | N/A      | 1.69     | N/A      | N/A      | 1.87     | N/A      | N/A
  PSU_1_VOLT_IN             | 214.25V    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU_1_VOLT_OUT            | 12.16V     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU_2_VOLT_IN             | 213.25V    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU_2_VOLT_OUT            | 12.232V    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  RTC_Voltage               | 3.018V     | OK       | N/A      | 2.289    | N/A      | N/A      | 3.444    | N/A      | N/A
  SYS_V12                   | 12.2655V   | OK       | N/A      | 11.348   | N/A      | N/A      | 12.552   | N/A      | N/A
  SYS_V1_05                 | 1.0497V    | OK       | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | N/A
  SYS_V3_3                  | 3.306V     | OK       | N/A      | 3.104    | N/A      | N/A      | 3.431    | N/A      | N/A
  SYS_V5                    | 5.0441V    | OK       | N/A      | 4.725    | N/A      | N/A      | 5.225    | N/A      | N/A

(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 ZT-Galene-BMC-update-v1.13]$
```

### Previous BMC 1.08

```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 ZT-Galene-BMC-update-simple-Redfish-v1.08-20240411]$ rf_sensor_list.py -u XXXXXX -p XXXXXX -r https://[2607:f160:10:8803:ce:40a:0:e005]
Chassis 'System' Status
  Sensor                    | Reading    | Health   | LF       | LC       | LNC      | UNC      | UC       | UF       | PhysicalContext
  State                     | Enabled    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU1_CURRENT_OUT          | 11.734A    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU2_CURRENT_OUT          | 10.796A    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU_1_CURRENT_IN          | 0.761A     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU_2_CURRENT_IN          | 0.695A     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU_1_STATUS              | 0          | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU_2_STATUS              | 0          | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  CPU_0_STATUS              | 7          | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  CPU_0_PROCHOT             | 0          | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_FAN_1_PWM             | 14.9019607 | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SYS_FAN_2_PWM             | 14.9019607 | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU_1_FAN                 | 3968.0RPM  | OK       | N/A      | 800.0    | 1120.0   | N/A      | N/A      | N/A      | N/A
  PSU_2_FAN                 | 4000.0RPM  | OK       | N/A      | 800.0    | 1120.0   | N/A      | N/A      | N/A      | N/A
  SYS_FAN_1A                | 3720.0RPM  | OK       | N/A      | 1000.0   | N/A      | N/A      | 28500.0  | N/A      | N/A
  SYS_FAN_1B                | 3600.0RPM  | OK       | N/A      | 1000.0   | N/A      | N/A      | 28500.0  | N/A      | N/A
  SYS_FAN_2A                | 3780.0RPM  | OK       | N/A      | 1000.0   | N/A      | N/A      | 28500.0  | N/A      | N/A
  SYS_FAN_2B                | 3600.0RPM  | OK       | N/A      | 1000.0   | N/A      | N/A      | 28500.0  | N/A      | N/A
  CPU0_Power                | 66.729W    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  MB_HSC_PEAK_PIN           | 363.071895 | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  MB_HSC_PIN                | 134.422657 | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  MB_HSC_PIN_AVG            | 134.685910 | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU_1_POWER_IN            | 160.75W    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU_1_POWER_OUT           | 142.5W     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU_2_POWER_IN            | 145.25W    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU_2_POWER_OUT           | 129.25W    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU_POWER_IN              | 306.0W     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PWR_UNIT_REDUND           | 0          | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PWR_UNIT_STATUS           | 0          | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  CPU_0_DIMM_A0             | 42.0Cel    | OK       | N/A      | 6.0      | N/A      | N/A      | 82.0     | N/A      | N/A
  CPU_0_DIMM_B0             | 40.0Cel    | OK       | N/A      | 6.0      | N/A      | N/A      | 82.0     | N/A      | N/A
  CPU_0_DIMM_C0             | 39.0Cel    | OK       | N/A      | 6.0      | N/A      | N/A      | 82.0     | N/A      | N/A
  CPU_0_DIMM_D0             | 39.0Cel    | OK       | N/A      | 6.0      | N/A      | N/A      | 82.0     | N/A      | N/A
  CPU_0_DIMM_E0             | 41.0Cel    | OK       | N/A      | 6.0      | N/A      | N/A      | 82.0     | N/A      | N/A
  CPU_0_DIMM_F0             | 39.0Cel    | OK       | N/A      | 6.0      | N/A      | N/A      | 82.0     | N/A      | N/A
  CPU_0_DIMM_G0             | 38.0Cel    | OK       | N/A      | 6.0      | N/A      | N/A      | 82.0     | N/A      | N/A
  CPU_0_DIMM_H0             | 37.0Cel    | OK       | N/A      | 6.0      | N/A      | N/A      | 82.0     | N/A      | N/A
  CPU_0_DTS_TEMP            | -41.203Cel | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  CPU_0_MARGIN              | 33.156Cel  | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  CPU_0_TEMP                | 49.797Cel  | OK       | N/A      | N/A      | N/A      | 89.0     | 91.0     | N/A      | N/A
  DIMM_VR_TEMP              | 40.0Cel    | OK       | N/A      | 6.0      | N/A      | N/A      | 125.0    | N/A      | N/A
  INLET_TEMP_L              | 25.0Cel    | OK       | N/A      | -6.0     | N/A      | 50.0     | 59.0     | N/A      | N/A
  INLET_TEMP_MAX            | 26.0Cel    | OK       | N/A      | -6.0     | N/A      | 50.0     | 59.0     | N/A      | N/A
  INLET_TEMP_R              | 26.0Cel    | OK       | N/A      | -6.0     | N/A      | 50.0     | 59.0     | N/A      | N/A
  MAX_DIMM_TEMP             | 42.0Cel    | OK       | N/A      | 6.0      | N/A      | N/A      | 82.0     | N/A      | N/A
  MB_HSC_TEMP               | 39.761Cel  | OK       | N/A      | 6.0      | N/A      | N/A      | 125.0    | N/A      | N/A
  OUTLET_TEMP_L             | 43.0Cel    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  OUTLET_TEMP_MAX           | 43.0Cel    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  OUTLET_TEMP_R             | 40.0Cel    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PDB_1_TEMP                | 35.313Cel  | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU_1_TEMP_1              | 27.75Cel   | OK       | N/A      | N/A      | N/A      | N/A      | 60.0     | N/A      | N/A
  PSU_1_TEMP_2              | 45.0Cel    | OK       | N/A      | N/A      | N/A      | N/A      | 92.0     | N/A      | N/A
  PSU_2_TEMP_1              | 27.5Cel    | OK       | N/A      | N/A      | N/A      | N/A      | 60.0     | N/A      | N/A
  PSU_2_TEMP_2              | 45.5Cel    | OK       | N/A      | N/A      | N/A      | N/A      | 92.0     | N/A      | N/A
  RISER_TEMP                | 26.563Cel  | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  SC_1_E810                 | 54.0Cel    | OK       | N/A      | 0.0      | 5.0      | 100.0    | 105.0    | N/A      | N/A
  SC_2_E810                 | 49.0Cel    | OK       | N/A      | 0.0      | 5.0      | 100.0    | 105.0    | N/A      | N/A
  SC_3_E810                 | 43.0Cel    | OK       | N/A      | 0.0      | 5.0      | 100.0    | 105.0    | N/A      | N/A
  SSD_0_TEMP                | 34.0Cel    | OK       | N/A      | 0.0      | N/A      | N/A      | 80.0     | N/A      | N/A
  SSD_1_TEMP                | 31.0Cel    | OK       | N/A      | 0.0      | N/A      | N/A      | 80.0     | N/A      | N/A
  SYS_PCH_TEMP              | 42.0Cel    | OK       | N/A      | 5.0      | N/A      | N/A      | 82.0     | N/A      | N/A
  BMC_CPU                   | 13.8860077 | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  BMC_CPU_Kernel            | 6.86469932 | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  BMC_CPU_User              | 6.99110310 | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  BMC_Memory                | 17.0001585 | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  BMC_Storage_RW            | 3.73872302 | OK       | N/A      | N/A      | N/A      | N/A      | 85.0     | N/A      | N/A
  BMC_Storage_TMP           | 0.0%       | OK       | N/A      | N/A      | N/A      | N/A      | 85.0     | N/A      | N/A
  CPU_CUPS                  | 3.98330080 | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  CPU0VCCD_1_1V             | 1.164V     | OK       | N/A      | 1.049    | N/A      | N/A      | 1.196    | N/A      | N/A
  CPU_0_Vcore               | 1.821V     | OK       | N/A      | 1.69     | N/A      | N/A      | 1.87     | N/A      | N/A
  PSU_1_VOLT_IN             | 213.25V    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU_1_VOLT_OUT            | 12.16V     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU_2_VOLT_IN             | 212.0V     | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  PSU_2_VOLT_OUT            | 12.232V    | OK       | N/A      | N/A      | N/A      | N/A      | N/A      | N/A      | N/A
  RTC_Voltage               | 3.018V     | OK       | N/A      | 2.289    | N/A      | N/A      | 3.444    | N/A      | N/A
  SYS_V12                   | 12.2655V   | OK       | N/A      | 11.348   | N/A      | N/A      | 12.552   | N/A      | N/A
  SYS_V1_05                 | 1.0497V    | OK       | N/A      | 0.99252  | N/A      | N/A      | 1.09748  | N/A      | N/A
  SYS_V3_3                  | 3.306V     | OK       | N/A      | 3.104    | N/A      | N/A      | 3.431    | N/A      | N/A
  SYS_V5                    | 5.0441V    | OK       | N/A      | 4.725    | N/A      | N/A      | 5.225    | N/A      | N/A

(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 ZT-Galene-BMC-update-simple-Redfish-v1.08-20240411]$
```

### compare

```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ rf_sensor_list.py -u XXXXXX -p XXXXXX -r https://[2607:f160:10:8803:ce:40a:0:e005] | awk -F\| '{print $1}' > /tmp/bmc-1-13.txt
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 ~]$ rf_sensor_list.py -u XXXXXX -p XXXXXX -r https://[2607:f160:10:8803:ce:40a:0:e005] | awk -F\| '{print $1}' > /tmp/bmc-1-08.txt
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 ZT-Galene-BMC-update-simple-Redfish-v1.08-20240411]$ diff /tmp/bmc-1-13.txt /tmp/bmc-1-08.txt
4,8d3
<   Power Supply Bay State
<   Power Supply Bay State
<   Power Supply Redundancy 0
<   SYS_FAN_1 State
<   SYS_FAN_2 State
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 ZT-Galene-BMC-update-simple-Redfish-v1.08-20240411]$
```

### Results
We have new sensors in 1.13 BMC firmware
