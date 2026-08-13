# ZT Galene 1.13 BMC firmware validation
# ZT Proteus BIOS 1.01
# 4/15/25 James Patchett

## Soak started with this system on 4/08/25
## Soak period is 4/08/25-4/15/25 (~7 days)

## Target Subcloud welktxsr-d29991563804-001
BMC: 2607:f160:10:9803:ce:40a:0:e012
OAM: 2607:f160:10:9803:ce:40a:0:f412 

### BMC & BIOS on the system

```log
[XXXXXX@welktxefnce-h-pe1util-vm01 ZT-Galene-BMC-update-v1.13]$ IP=2607:f160:10:9803:ce:40a:0:e012
[XXXXXX@welktxefnce-h-pe1util-vm01 ZT-Galene-BMC-update-v1.13]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[${IP}]/redfish/v1/UpdateService/FirmwareInventory/BMCImage1 | jq .
{
  "@odata.context": "/redfish/v1/$metadata#SoftwareInventory.SoftwareInventory",
  "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/BMCImage1",
  "@odata.type": "#SoftwareInventory.v1_10_2.SoftwareInventory",
  "Id": "BMCImage1",
  "Name": "Primary Baseboard Management Controller",
  "Oem": {
    "Information": {
      "@odata.context": "/redfish/v1/$metadata#OemZTFirmware.Information",
      "@odata.type": "#OemZTFirmware.v1_0_0.Information",
      "Manufacturer": "ZTSystems",
      "ReleaseDate": "20241212082612"
    }
  },
  "Status": {
    "Health": "OK",
    "HealthRollup": "OK",
    "State": "Enabled"
  },
  "Updateable": true,
  "Version": "01.13.00"
}
[XXXXXX@welktxefnce-h-pe1util-vm01 ZT-Galene-BMC-update-v1.13]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[${IP}]/redfish/v1/UpdateService/FirmwareInventory/BIOS | jq .
{
  "@odata.context": "/redfish/v1/$metadata#SoftwareInventory.SoftwareInventory",
  "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/BIOS",
  "@odata.type": "#SoftwareInventory.v1_10_2.SoftwareInventory",
  "Description": "Host BIOS Firmware",
  "Id": "BIOS",
  "Name": "Host BIOS Firmware",
  "Oem": {
    "Information": {
      "@odata.context": "/redfish/v1/$metadata#OemZTFirmware.Information",
      "@odata.type": "#OemZTFirmware.v1_0_0.Information",
      "Manufacturer": "ZTSystems"
    }
  },
  "Status": {
    "Health": "OK",
    "HealthRollup": "OK",
    "State": "Enabled"
  },
  "Updateable": true,
  "Version": "1.01"
}
[XXXXXX@welktxefnce-h-pe1util-vm01 ZT-Galene-BMC-update-v1.13]$
```


### Looking at /var/log/user.log for any increase of PTPL4 sync errors over the 1 week soak period

```log
[XXXXXX@controller-0 log(keystone_admin)]$ cat /var/log/user.log | grep -e "XXXXXX" -e "XXXXXX"
2025-04-07T20:22:18.211 controller-0 ptp4l: err [14948750.847] ptp4l-legacy timed out while polling for tx timestamp
2025-04-07T20:22:18.211 controller-0 ptp4l: err [14948750.847] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
[XXXXXX@controller-0 log(keystone_admin)]$
```

```log
[XXXXXX@controller-0 log(keystone_admin)]$ grep -e "err" /var/log/user.log
2025-04-02T21:01:46.188 controller-0 ptp4l: err [14519118.824] ptp4l-legacy failed to adjust the clock: Input/output error
2025-04-02T21:01:46.259 controller-0 ptp4l: err [14519118.886] ptp4l-legacy failed to adjust the clock: Input/output error
2025-04-07T20:22:18.211 controller-0 ptp4l: err [14948750.847] ptp4l-legacy timed out while polling for tx timestamp
2025-04-07T20:22:18.211 controller-0 ptp4l: err [14948750.847] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2025-04-07T20:22:18.211 controller-0 ptp4l: err [14948750.847] ptp4l-legacy port 1: send sync failed
2025-04-12T19:44:59.683 controller-0 ptp4l: err [15378512.310] ptp4l-legacy failed to adjust the clock: Input/output error
2025-04-12T19:44:59.751 controller-0 phc2sys: err [15378512.373] phc2sys-legacy ioctl PTP_SYS_OFFSET_EXTENDED: Device or resource busy
2025-04-12T19:44:59.751 controller-0 ptp4l: err [15378512.373] ptp4l-legacy failed to adjust the clock: Input/output error
2025-04-12T19:44:59.799 controller-0 ptp4l: err [15378512.435] ptp4l-legacy failed to adjust the clock: Input/output error
2025-04-12T19:44:59.863 controller-0 ptp4l: err [15378512.499] ptp4l-legacy failed to adjust the clock: Input/output error
[XXXXXX@controller-0 log(keystone_admin)]$
```

```log
[XXXXXX@controller-0 log(keystone_admin)]$ grep -e "err" /var/log/user.log
2025-04-02T21:01:46.188 controller-0 ptp4l: err [14519118.824] ptp4l-legacy failed to adjust the clock: Input/output error
2025-04-02T21:01:46.259 controller-0 ptp4l: err [14519118.886] ptp4l-legacy failed to adjust the clock: Input/output error
2025-04-07T20:22:18.211 controller-0 ptp4l: err [14948750.847] ptp4l-legacy timed out while polling for tx timestamp
2025-04-07T20:22:18.211 controller-0 ptp4l: err [14948750.847] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2025-04-07T20:22:18.211 controller-0 ptp4l: err [14948750.847] ptp4l-legacy port 1: send sync failed
2025-04-12T19:44:59.683 controller-0 ptp4l: err [15378512.310] ptp4l-legacy failed to adjust the clock: Input/output error
2025-04-12T19:44:59.751 controller-0 phc2sys: err [15378512.373] phc2sys-legacy ioctl PTP_SYS_OFFSET_EXTENDED: Device or resource busy
2025-04-12T19:44:59.751 controller-0 ptp4l: err [15378512.373] ptp4l-legacy failed to adjust the clock: Input/output error
2025-04-12T19:44:59.799 controller-0 ptp4l: err [15378512.435] ptp4l-legacy failed to adjust the clock: Input/output error
2025-04-12T19:44:59.863 controller-0 ptp4l: err [15378512.499] ptp4l-legacy failed to adjust the clock: Input/output error
[XXXXXX@controller-0 log(keystone_admin)]$ grep -v -e "info" /var/log/user.log
2025-04-02T15:32:47.797 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/secrets/monitor/\" range_end:\"/registry/secrets/monitor0\" " with result "range_response_count:24 size:1019716" took too long (103.662009ms) to execute
2025-04-02T20:01:15.148 controller-0 ptp4l: notice [14515487.784] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T20:01:15.198 controller-0 ptp4l: notice [14515487.834] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T20:01:15.311 controller-0 ptp4l: notice [14515487.948] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T20:01:15.361 controller-0 ptp4l: notice [14515487.997] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T20:01:15.489 controller-0 ptp4l: notice [14515488.125] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T20:01:15.535 controller-0 ptp4l: notice [14515488.171] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T20:01:19.615 controller-0 ptp4l: notice [14515492.251] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T20:01:19.663 controller-0 ptp4l: notice [14515492.299] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T20:01:19.762 controller-0 ptp4l: notice [14515492.398] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T20:01:19.823 controller-0 ptp4l: notice [14515492.459] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T20:01:20.075 controller-0 ptp4l: notice [14515492.711] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T20:01:20.135 controller-0 ptp4l: notice [14515492.771] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T20:04:28.342 controller-0 ptp4l: notice [14515680.978] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T20:04:28.392 controller-0 ptp4l: notice [14515681.028] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T20:04:28.451 controller-0 ptp4l: notice [14515681.087] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T20:04:28.499 controller-0 ptp4l: notice [14515681.135] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T20:04:28.563 controller-0 ptp4l: notice [14515681.199] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T20:04:28.619 controller-0 ptp4l: notice [14515681.255] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T20:04:32.906 controller-0 ptp4l: notice [14515685.542] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T20:04:32.957 controller-0 ptp4l: notice [14515685.592] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T20:04:33.014 controller-0 ptp4l: notice [14515685.650] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T20:04:33.061 controller-0 ptp4l: notice [14515685.696] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T20:04:33.112 controller-0 ptp4l: notice [14515685.748] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T20:04:33.161 controller-0 ptp4l: notice [14515685.797] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T21:01:46.188 controller-0 ptp4l: err [14519118.824] ptp4l-legacy failed to adjust the clock: Input/output error
2025-04-02T21:01:46.259 controller-0 ptp4l: err [14519118.886] ptp4l-legacy failed to adjust the clock: Input/output error
2025-04-02T22:31:12.194 controller-0 ptp4l: notice [14524484.830] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:12.244 controller-0 ptp4l: notice [14524484.880] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:12.335 controller-0 ptp4l: notice [14524484.971] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:12.396 controller-0 ptp4l: notice [14524485.032] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:12.462 controller-0 ptp4l: notice [14524485.098] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:12.509 controller-0 ptp4l: notice [14524485.145] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:12.904 controller-0 ptp4l: notice [14524485.539] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:12.958 controller-0 ptp4l: notice [14524485.594] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:13.266 controller-0 ptp4l: notice [14524485.901] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:13.319 controller-0 ptp4l: notice [14524485.955] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:35.705 controller-0 ptp4l: notice [14524508.340] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:35.757 controller-0 ptp4l: notice [14524508.393] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:35.820 controller-0 ptp4l: notice [14524508.456] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:35.870 controller-0 ptp4l: notice [14524508.506] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:35.927 controller-0 ptp4l: notice [14524508.563] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:35.985 controller-0 ptp4l: notice [14524508.620] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:40.275 controller-0 ptp4l: notice [14524512.911] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:40.319 controller-0 ptp4l: notice [14524512.955] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:40.573 controller-0 ptp4l: notice [14524513.209] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:40.642 controller-0 ptp4l: notice [14524513.277] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:41.251 controller-0 ptp4l: notice [14524513.887] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:41.299 controller-0 ptp4l: notice [14524513.934] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:41.402 controller-0 ptp4l: notice [14524514.039] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:41.454 controller-0 ptp4l: notice [14524514.090] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:43.789 controller-0 ptp4l: notice [14524516.425] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:43.839 controller-0 ptp4l: notice [14524516.473] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:43.897 controller-0 ptp4l: notice [14524516.533] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:43.946 controller-0 ptp4l: notice [14524516.582] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:44.090 controller-0 ptp4l: notice [14524516.727] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:44.142 controller-0 ptp4l: notice [14524516.778] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:44.267 controller-0 ptp4l: notice [14524516.904] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:44.316 controller-0 ptp4l: notice [14524516.952] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:45.802 controller-0 ptp4l: notice [14524518.438] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:45.859 controller-0 ptp4l: notice [14524518.496] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:45.987 controller-0 ptp4l: notice [14524518.623] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:46.071 controller-0 ptp4l: notice [14524518.707] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:46.383 controller-0 ptp4l: notice [14524519.019] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:46.431 controller-0 ptp4l: notice [14524519.067] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:46.576 controller-0 ptp4l: notice [14524519.212] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:46.625 controller-0 ptp4l: notice [14524519.261] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:49.076 controller-0 ptp4l: notice [14524521.712] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:49.125 controller-0 ptp4l: notice [14524521.761] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:49.242 controller-0 ptp4l: notice [14524521.878] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:49.303 controller-0 ptp4l: notice [14524521.939] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:49.508 controller-0 ptp4l: notice [14524522.144] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:49.563 controller-0 ptp4l: notice [14524522.198] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:49.761 controller-0 ptp4l: notice [14524522.397] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:49.807 controller-0 ptp4l: notice [14524522.443] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:52.818 controller-0 ptp4l: notice [14524525.454] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:52.879 controller-0 ptp4l: notice [14524525.515] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:52.945 controller-0 ptp4l: notice [14524525.581] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:53.024 controller-0 ptp4l: notice [14524525.660] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:53.172 controller-0 ptp4l: notice [14524525.809] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:53.238 controller-0 ptp4l: notice [14524525.874] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:53.337 controller-0 ptp4l: notice [14524525.973] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:53.409 controller-0 ptp4l: notice [14524526.045] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:54.774 controller-0 ptp4l: notice [14524527.410] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:54.824 controller-0 ptp4l: notice [14524527.460] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:54.928 controller-0 ptp4l: notice [14524527.564] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:55.001 controller-0 ptp4l: notice [14524527.637] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:55.163 controller-0 ptp4l: notice [14524527.799] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:55.209 controller-0 ptp4l: notice [14524527.844] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:55.313 controller-0 ptp4l: notice [14524527.949] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:55.368 controller-0 ptp4l: notice [14524528.004] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:56.832 controller-0 ptp4l: notice [14524529.467] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:56.876 controller-0 ptp4l: notice [14524529.512] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:57.089 controller-0 ptp4l: notice [14524529.725] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:57.160 controller-0 ptp4l: notice [14524529.796] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:57.336 controller-0 ptp4l: notice [14524529.972] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:57.390 controller-0 ptp4l: notice [14524530.023] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:57.518 controller-0 ptp4l: notice [14524530.154] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:57.574 controller-0 ptp4l: notice [14524530.210] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:58.834 controller-0 ptp4l: notice [14524531.469] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:58.894 controller-0 ptp4l: notice [14524531.528] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:58.958 controller-0 ptp4l: notice [14524531.595] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:59.005 controller-0 ptp4l: notice [14524531.641] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:59.159 controller-0 ptp4l: notice [14524531.794] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:59.203 controller-0 ptp4l: notice [14524531.839] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:59.351 controller-0 ptp4l: notice [14524531.987] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:31:59.401 controller-0 ptp4l: notice [14524532.037] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:00.886 controller-0 ptp4l: notice [14524533.522] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:00.948 controller-0 ptp4l: notice [14524533.584] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:01.018 controller-0 ptp4l: notice [14524533.654] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:01.068 controller-0 ptp4l: notice [14524533.704] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:01.228 controller-0 ptp4l: notice [14524533.864] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:01.275 controller-0 ptp4l: notice [14524533.911] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:01.371 controller-0 ptp4l: notice [14524534.007] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:01.417 controller-0 ptp4l: notice [14524534.053] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:02.682 controller-0 ptp4l: notice [14524535.317] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:02.727 controller-0 ptp4l: notice [14524535.363] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:02.803 controller-0 ptp4l: notice [14524535.439] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:02.854 controller-0 ptp4l: notice [14524535.490] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:02.999 controller-0 ptp4l: notice [14524535.636] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:03.050 controller-0 ptp4l: notice [14524535.685] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:03.149 controller-0 ptp4l: notice [14524535.784] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:03.199 controller-0 ptp4l: notice [14524535.835] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:04.891 controller-0 ptp4l: notice [14524537.527] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:04.964 controller-0 ptp4l: notice [14524537.600] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:05.031 controller-0 ptp4l: notice [14524537.667] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:05.078 controller-0 ptp4l: notice [14524537.714] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:05.233 controller-0 ptp4l: notice [14524537.869] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:05.279 controller-0 ptp4l: notice [14524537.915] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:05.384 controller-0 ptp4l: notice [14524538.020] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:05.436 controller-0 ptp4l: notice [14524538.072] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:06.884 controller-0 ptp4l: notice [14524539.518] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:06.941 controller-0 ptp4l: notice [14524539.577] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:07.039 controller-0 ptp4l: notice [14524539.675] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:07.112 controller-0 ptp4l: notice [14524539.748] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:07.463 controller-0 ptp4l: notice [14524540.099] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:07.516 controller-0 ptp4l: notice [14524540.151] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:10.076 controller-0 ptp4l: notice [14524542.712] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:10.121 controller-0 ptp4l: notice [14524542.757] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:10.201 controller-0 ptp4l: notice [14524542.837] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:10.203 controller-0 ptp4l: notice [14524542.838] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:10.355 controller-0 ptp4l: notice [14524542.991] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:10.406 controller-0 ptp4l: notice [14524543.042] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:10.503 controller-0 ptp4l: notice [14524543.139] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:10.554 controller-0 ptp4l: notice [14524543.189] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:11.775 controller-0 ptp4l: notice [14524544.411] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:11.821 controller-0 ptp4l: notice [14524544.456] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:11.888 controller-0 ptp4l: notice [14524544.524] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:11.942 controller-0 ptp4l: notice [14524544.578] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:12.076 controller-0 ptp4l: notice [14524544.712] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:12.121 controller-0 ptp4l: notice [14524544.757] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:12.214 controller-0 ptp4l: notice [14524544.849] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:12.258 controller-0 ptp4l: notice [14524544.894] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:13.914 controller-0 ptp4l: notice [14524546.550] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:13.966 controller-0 ptp4l: notice [14524546.602] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:14.066 controller-0 ptp4l: notice [14524546.702] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:14.125 controller-0 ptp4l: notice [14524546.761] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:14.378 controller-0 ptp4l: notice [14524547.015] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:14.424 controller-0 ptp4l: notice [14524547.060] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:14.551 controller-0 ptp4l: notice [14524547.186] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:14.598 controller-0 ptp4l: notice [14524547.234] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:15.888 controller-0 ptp4l: notice [14524548.524] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:15.942 controller-0 ptp4l: notice [14524548.578] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:16.052 controller-0 ptp4l: notice [14524548.688] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:16.097 controller-0 ptp4l: notice [14524548.733] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:16.309 controller-0 ptp4l: notice [14524548.944] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:16.359 controller-0 ptp4l: notice [14524548.995] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:16.477 controller-0 ptp4l: notice [14524549.113] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:16.524 controller-0 ptp4l: notice [14524549.159] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:17.820 controller-0 ptp4l: notice [14524550.455] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:17.867 controller-0 ptp4l: notice [14524550.502] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:17.958 controller-0 ptp4l: notice [14524550.594] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:18.011 controller-0 ptp4l: notice [14524550.647] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:18.225 controller-0 ptp4l: notice [14524550.861] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:18.272 controller-0 ptp4l: notice [14524550.909] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:18.496 controller-0 ptp4l: notice [14524551.132] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:18.545 controller-0 ptp4l: notice [14524551.180] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:20.635 controller-0 ptp4l: notice [14524553.271] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:20.726 controller-0 ptp4l: notice [14524553.362] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:21.014 controller-0 ptp4l: notice [14524553.650] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:21.097 controller-0 ptp4l: notice [14524553.733] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:21.332 controller-0 ptp4l: notice [14524553.968] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:21.392 controller-0 ptp4l: notice [14524554.027] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:21.548 controller-0 ptp4l: notice [14524554.184] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:21.623 controller-0 ptp4l: notice [14524554.259] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:22.856 controller-0 ptp4l: notice [14524555.492] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:22.917 controller-0 ptp4l: notice [14524555.554] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:23.011 controller-0 ptp4l: notice [14524555.647] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:23.072 controller-0 ptp4l: notice [14524555.708] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:23.266 controller-0 ptp4l: notice [14524555.902] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:23.310 controller-0 ptp4l: notice [14524555.946] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:23.423 controller-0 ptp4l: notice [14524556.059] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:23.474 controller-0 ptp4l: notice [14524556.110] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:24.853 controller-0 ptp4l: notice [14524557.489] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:24.915 controller-0 ptp4l: notice [14524557.551] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:24.991 controller-0 ptp4l: notice [14524557.627] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:25.042 controller-0 ptp4l: notice [14524557.677] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:25.237 controller-0 ptp4l: notice [14524557.873] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:25.282 controller-0 ptp4l: notice [14524557.918] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:25.423 controller-0 ptp4l: notice [14524558.060] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:25.476 controller-0 ptp4l: notice [14524558.111] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:26.839 controller-0 ptp4l: notice [14524559.475] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:26.885 controller-0 ptp4l: notice [14524559.522] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:26.979 controller-0 ptp4l: notice [14524559.615] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:27.042 controller-0 ptp4l: notice [14524559.678] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:27.218 controller-0 ptp4l: notice [14524559.854] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:27.265 controller-0 ptp4l: notice [14524559.900] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:27.402 controller-0 ptp4l: notice [14524560.038] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:27.454 controller-0 ptp4l: notice [14524560.090] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:28.915 controller-0 ptp4l: notice [14524561.551] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:28.976 controller-0 ptp4l: notice [14524561.612] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:29.067 controller-0 ptp4l: notice [14524561.703] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:29.127 controller-0 ptp4l: notice [14524561.763] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:29.320 controller-0 ptp4l: notice [14524561.956] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:29.374 controller-0 ptp4l: notice [14524562.011] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:29.520 controller-0 ptp4l: notice [14524562.156] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:29.575 controller-0 ptp4l: notice [14524562.211] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:30.932 controller-0 ptp4l: notice [14524563.567] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:30.997 controller-0 ptp4l: notice [14524563.632] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:31.085 controller-0 ptp4l: notice [14524563.721] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:31.135 controller-0 ptp4l: notice [14524563.771] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:31.330 controller-0 ptp4l: notice [14524563.966] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:31.382 controller-0 ptp4l: notice [14524564.018] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:31.519 controller-0 ptp4l: notice [14524564.154] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:31.572 controller-0 ptp4l: notice [14524564.208] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:32.941 controller-0 ptp4l: notice [14524565.576] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:33.027 controller-0 ptp4l: notice [14524565.663] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:33.125 controller-0 ptp4l: notice [14524565.761] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:33.183 controller-0 ptp4l: notice [14524565.819] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:33.370 controller-0 ptp4l: notice [14524566.006] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:33.415 controller-0 ptp4l: notice [14524566.051] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:33.542 controller-0 ptp4l: notice [14524566.178] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:33.600 controller-0 ptp4l: notice [14524566.235] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:34.907 controller-0 ptp4l: notice [14524567.543] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:34.975 controller-0 ptp4l: notice [14524567.611] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:35.072 controller-0 ptp4l: notice [14524567.708] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:35.117 controller-0 ptp4l: notice [14524567.753] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:35.315 controller-0 ptp4l: notice [14524567.951] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:35.367 controller-0 ptp4l: notice [14524568.004] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:35.474 controller-0 ptp4l: notice [14524568.110] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:35.519 controller-0 ptp4l: notice [14524568.155] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:36.944 controller-0 ptp4l: notice [14524569.580] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:36.997 controller-0 ptp4l: notice [14524569.633] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:37.087 controller-0 ptp4l: notice [14524569.723] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:37.143 controller-0 ptp4l: notice [14524569.779] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:37.396 controller-0 ptp4l: notice [14524570.032] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:37.446 controller-0 ptp4l: notice [14524570.081] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:37.576 controller-0 ptp4l: notice [14524570.212] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:37.625 controller-0 ptp4l: notice [14524570.261] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:39.053 controller-0 ptp4l: notice [14524571.689] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:39.097 controller-0 ptp4l: notice [14524571.733] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:39.188 controller-0 ptp4l: notice [14524571.824] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:39.241 controller-0 ptp4l: notice [14524571.877] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:39.444 controller-0 ptp4l: notice [14524572.080] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:39.489 controller-0 ptp4l: notice [14524572.125] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:39.664 controller-0 ptp4l: notice [14524572.300] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:39.711 controller-0 ptp4l: notice [14524572.346] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:41.076 controller-0 ptp4l: notice [14524573.712] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:41.137 controller-0 ptp4l: notice [14524573.771] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:41.268 controller-0 ptp4l: notice [14524573.904] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:41.337 controller-0 ptp4l: notice [14524573.973] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:41.592 controller-0 ptp4l: notice [14524574.228] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:41.641 controller-0 ptp4l: notice [14524574.277] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:41.753 controller-0 ptp4l: notice [14524574.389] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:41.803 controller-0 ptp4l: notice [14524574.438] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:44.139 controller-0 ptp4l: notice [14524576.775] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:44.193 controller-0 ptp4l: notice [14524576.829] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:44.314 controller-0 ptp4l: notice [14524576.950] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:44.394 controller-0 ptp4l: notice [14524577.030] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:44.950 controller-0 ptp4l: notice [14524577.586] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:45.010 controller-0 ptp4l: notice [14524577.646] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:45.154 controller-0 ptp4l: notice [14524577.790] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:45.204 controller-0 ptp4l: notice [14524577.840] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:47.026 controller-0 ptp4l: notice [14524579.662] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:47.075 controller-0 ptp4l: notice [14524579.711] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:47.198 controller-0 ptp4l: notice [14524579.834] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:47.261 controller-0 ptp4l: notice [14524579.897] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:47.538 controller-0 ptp4l: notice [14524580.174] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:47.590 controller-0 ptp4l: notice [14524580.226] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:47.723 controller-0 ptp4l: notice [14524580.360] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:47.782 controller-0 ptp4l: notice [14524580.418] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:49.027 controller-0 ptp4l: notice [14524581.662] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:49.074 controller-0 ptp4l: notice [14524581.710] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:49.170 controller-0 ptp4l: notice [14524581.807] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:49.216 controller-0 ptp4l: notice [14524581.852] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:49.441 controller-0 ptp4l: notice [14524582.077] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:49.485 controller-0 ptp4l: notice [14524582.121] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:49.609 controller-0 ptp4l: notice [14524582.245] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:49.658 controller-0 ptp4l: notice [14524582.294] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:51.055 controller-0 ptp4l: notice [14524583.691] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:51.116 controller-0 ptp4l: notice [14524583.752] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:51.206 controller-0 ptp4l: notice [14524583.842] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:51.252 controller-0 ptp4l: notice [14524583.888] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:51.433 controller-0 ptp4l: notice [14524584.069] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:51.481 controller-0 ptp4l: notice [14524584.117] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:51.612 controller-0 ptp4l: notice [14524584.249] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:51.660 controller-0 ptp4l: notice [14524584.296] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:53.063 controller-0 ptp4l: notice [14524585.699] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:53.111 controller-0 ptp4l: notice [14524585.747] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:53.207 controller-0 ptp4l: notice [14524585.843] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:53.269 controller-0 ptp4l: notice [14524585.905] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:53.458 controller-0 ptp4l: notice [14524586.095] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:53.504 controller-0 ptp4l: notice [14524586.140] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:53.652 controller-0 ptp4l: notice [14524586.288] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:53.697 controller-0 ptp4l: notice [14524586.333] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:54.989 controller-0 ptp4l: notice [14524587.624] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:55.052 controller-0 ptp4l: notice [14524587.688] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:55.126 controller-0 ptp4l: notice [14524587.762] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:55.183 controller-0 ptp4l: notice [14524587.820] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:55.384 controller-0 ptp4l: notice [14524588.020] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:55.433 controller-0 ptp4l: notice [14524588.069] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:55.570 controller-0 ptp4l: notice [14524588.206] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:55.621 controller-0 ptp4l: notice [14524588.257] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:57.686 controller-0 ptp4l: notice [14524590.321] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:57.764 controller-0 ptp4l: notice [14524590.400] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:57.923 controller-0 ptp4l: notice [14524590.559] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:58.024 controller-0 ptp4l: notice [14524590.660] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:58.236 controller-0 ptp4l: notice [14524590.873] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-02T22:32:58.237 controller-0 ptp4l: notice [14524590.873] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T03:03:38.768 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/dex.coreos.com/authrequests/kube-system/jrgggqqirlwlwbyoacmj676pz\" " with result "range_response_count:1 size:887" took too long (170.555675ms) to execute
2025-04-03T03:16:23.384 controller-0 etcd[23910]: warning request "header:<ID:7587882124340700313 username:\"apiserver-etcd-client\" auth_revision:1 > txn:<compare:<target:MOD key:\"/registry/minions/controller-0\" mod_revision:94014220 > success:<request_put:<key:\"/registry/minions/controller-0\" value_size:18649 >> failure:<request_range:<key:\"/registry/minions/controller-0\" > >>" with result "size:20" took too long (194.197421ms) to execute
2025-04-03T05:11:43.798 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/leases/kube-system/external-snapshotter-leader-cephfs-csi-ceph-com\" " with result "range_response_count:1 size:544" took too long (149.519101ms) to execute
2025-04-03T05:15:01.473 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/services/specs/welktxsr-vzwcvdu-u-ss-adpf-29991563804/\" range_end:\"/registry/services/specs/welktxsr-vzwcvdu-u-ss-adpf-299915638040\" " with result "range_response_count:7 size:60983" took too long (130.860466ms) to execute
2025-04-03T06:49:57.666 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/minions/controller-0\" " with result "range_response_count:1 size:18710" took too long (151.64052ms) to execute
2025-04-03T07:29:27.414 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/pods/welktxsr-vzwcvdu-u-ss-adpf-29991563804/uadpf29991563804-dip0-55f8b95b47-hffvt\" " with result "range_response_count:1 size:9636" took too long (157.079209ms) to execute
2025-04-03T10:48:30.224 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/secrets/monitor/\" range_end:\"/registry/secrets/monitor0\" " with result "range_response_count:24 size:1019716" took too long (108.61324ms) to execute
2025-04-03T16:09:28.783 controller-0 ptp4l: notice [14587981.419] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T16:09:28.955 controller-0 ptp4l: notice [14587981.590] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T16:09:29.360 controller-0 ptp4l: notice [14587981.996] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T16:09:29.417 controller-0 ptp4l: notice [14587982.053] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T16:09:29.707 controller-0 ptp4l: notice [14587982.343] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T16:09:29.758 controller-0 ptp4l: notice [14587982.395] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T16:09:30.021 controller-0 ptp4l: notice [14587982.657] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T16:09:30.070 controller-0 ptp4l: notice [14587982.705] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T16:09:30.175 controller-0 ptp4l: notice [14587982.811] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T16:09:30.226 controller-0 ptp4l: notice [14587982.862] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T16:09:30.304 controller-0 ptp4l: notice [14587982.940] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T16:09:30.356 controller-0 ptp4l: notice [14587982.992] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T16:09:44.466 controller-0 ptp4l: notice [14587997.102] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T16:09:44.550 controller-0 ptp4l: notice [14587997.187] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T16:09:44.644 controller-0 ptp4l: notice [14587997.280] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T16:09:44.701 controller-0 ptp4l: notice [14587997.337] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T16:09:44.782 controller-0 ptp4l: notice [14587997.418] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T16:09:44.864 controller-0 ptp4l: notice [14587997.500] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T16:09:59.505 controller-0 ptp4l: notice [14588012.141] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T16:09:59.579 controller-0 ptp4l: notice [14588012.215] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T16:09:59.698 controller-0 ptp4l: notice [14588012.334] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T16:09:59.756 controller-0 ptp4l: notice [14588012.392] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T16:09:59.831 controller-0 ptp4l: notice [14588012.467] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T16:09:59.884 controller-0 ptp4l: notice [14588012.520] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T17:46:39.169 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/minions/controller-0\" " with result "range_response_count:1 size:18710" took too long (163.734668ms) to execute
2025-04-03T17:46:39.169 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/pods/armada/\" range_end:\"/registry/pods/armada0\" " with result "range_response_count:1 size:11900" took too long (147.139874ms) to execute
2025-04-03T17:46:39.169 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/services/specs/welktxsr-vzwcvdu-u-ss-adpf-29991563804/\" range_end:\"/registry/services/specs/welktxsr-vzwcvdu-u-ss-adpf-299915638040\" " with result "range_response_count:7 size:60983" took too long (129.623045ms) to execute
2025-04-03T20:12:21.564 controller-0 etcd[23910]: warning request "header:<ID:7587882124341798279 username:\"apiserver-etcd-client\" auth_revision:1 > txn:<compare:<target:MOD key:\"/registry/minions/controller-0\" mod_revision:94287657 > success:<request_put:<key:\"/registry/minions/controller-0\" value_size:18649 >> failure:<request_range:<key:\"/registry/minions/controller-0\" > >>" with result "size:20" took too long (121.185794ms) to execute
2025-04-03T20:31:57.966 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/pods/welktxsr-vzwcvdu-u-ss-adpf-29991563804/uadpf29991563804-dmp0-5dc545498d-x5qfr\" " with result "range_response_count:1 size:9153" took too long (132.72636ms) to execute
2025-04-03T20:31:57.966 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/snapshot.storage.k8s.io/volumesnapshotclasses/\" range_end:\"/registry/snapshot.storage.k8s.io/volumesnapshotclasses0\" count_only:true " with result "range_response_count:0 size:7" took too long (129.268327ms) to execute
2025-04-03T20:37:46.916 controller-0 ptp4l: notice [14604079.552] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T20:37:46.993 controller-0 ptp4l: notice [14604079.629] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T20:37:47.578 controller-0 ptp4l: notice [14604080.214] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T20:37:47.750 controller-0 ptp4l: notice [14604080.386] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T20:37:47.759 controller-0 ptp4l: notice [14604080.396] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T20:37:47.811 controller-0 ptp4l: notice [14604080.447] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T20:37:47.871 controller-0 ptp4l: notice [14604080.507] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T20:37:48.007 controller-0 ptp4l: notice [14604080.573] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T20:37:48.074 controller-0 ptp4l: notice [14604080.710] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T20:37:48.192 controller-0 ptp4l: notice [14604080.828] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T20:37:48.242 controller-0 ptp4l: notice [14604080.878] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T20:37:48.303 controller-0 ptp4l: notice [14604080.939] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T20:38:07.620 controller-0 ptp4l: notice [14604100.256] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T20:38:07.668 controller-0 ptp4l: notice [14604100.304] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T20:38:07.728 controller-0 ptp4l: notice [14604100.364] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T20:38:07.777 controller-0 ptp4l: notice [14604100.413] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T20:38:07.860 controller-0 ptp4l: notice [14604100.497] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T20:38:07.923 controller-0 ptp4l: notice [14604100.559] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T20:38:17.238 controller-0 ptp4l: notice [14604109.874] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T20:38:17.289 controller-0 ptp4l: notice [14604109.925] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T20:38:17.410 controller-0 ptp4l: notice [14604110.047] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T20:38:17.454 controller-0 ptp4l: notice [14604110.091] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T20:38:17.515 controller-0 ptp4l: notice [14604110.151] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T20:38:17.566 controller-0 ptp4l: notice [14604110.202] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T20:43:23.540 controller-0 etcd[23910]: warning request "header:<ID:7587882124341835024 username:\"apiserver-etcd-client\" auth_revision:1 > txn:<compare:<target:MOD key:\"/registry/leases/kube-system/external-snapshotter-leader-cephfs-csi-ceph-com\" mod_revision:94296293 > success:<request_put:<key:\"/registry/leases/kube-system/external-snapshotter-leader-cephfs-csi-ceph-com\" value_size:438 >> failure:<request_range:<key:\"/registry/leases/kube-system/external-snapshotter-leader-cephfs-csi-ceph-com\" > >>" with result "size:20" took too long (123.491975ms) to execute
2025-04-03T20:45:14.569 controller-0 ptp4l: notice [14604527.204] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T20:45:14.653 controller-0 ptp4l: notice [14604527.289] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T20:45:15.311 controller-0 ptp4l: notice [14604527.947] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T20:45:15.384 controller-0 ptp4l: notice [14604528.020] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T20:45:15.590 controller-0 ptp4l: notice [14604528.220] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T20:45:15.646 controller-0 ptp4l: notice [14604528.283] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T20:45:15.871 controller-0 ptp4l: notice [14604528.507] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T20:45:15.937 controller-0 ptp4l: notice [14604528.568] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T20:45:16.157 controller-0 ptp4l: notice [14604528.793] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T20:45:16.256 controller-0 ptp4l: notice [14604528.892] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T20:45:16.377 controller-0 ptp4l: notice [14604529.014] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T20:45:16.431 controller-0 ptp4l: notice [14604529.066] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T20:49:15.476 controller-0 ptp4l: notice [14604768.112] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T20:49:15.522 controller-0 ptp4l: notice [14604768.158] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T20:49:15.609 controller-0 ptp4l: notice [14604768.245] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T20:49:15.674 controller-0 ptp4l: notice [14604768.310] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T20:49:15.745 controller-0 ptp4l: notice [14604768.381] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T20:49:15.803 controller-0 ptp4l: notice [14604768.439] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T20:49:18.795 controller-0 ptp4l: notice [14604771.419] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T20:49:18.828 controller-0 ptp4l: notice [14604771.464] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T20:49:18.897 controller-0 ptp4l: notice [14604771.533] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T20:49:18.958 controller-0 ptp4l: notice [14604771.593] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T20:49:19.020 controller-0 ptp4l: notice [14604771.656] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T20:49:19.070 controller-0 ptp4l: notice [14604771.706] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T21:42:35.441 controller-0 ptp4l: notice [14607968.077] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T21:42:35.497 controller-0 ptp4l: notice [14607968.133] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T21:42:35.744 controller-0 ptp4l: notice [14607968.380] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T21:42:35.810 controller-0 ptp4l: notice [14607968.446] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T21:42:36.431 controller-0 ptp4l: notice [14607969.067] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T21:42:36.493 controller-0 ptp4l: notice [14607969.129] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T21:42:36.778 controller-0 ptp4l: notice [14607969.414] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T21:42:36.885 controller-0 ptp4l: notice [14607969.521] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T21:42:37.003 controller-0 ptp4l: notice [14607969.639] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T21:42:37.158 controller-0 ptp4l: notice [14607969.793] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T21:42:37.279 controller-0 ptp4l: notice [14607969.915] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T21:42:37.332 controller-0 ptp4l: notice [14607969.968] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T21:49:02.638 controller-0 ptp4l: notice [14608355.273] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T21:49:02.691 controller-0 ptp4l: notice [14608355.327] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T21:49:02.749 controller-0 ptp4l: notice [14608355.385] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T21:49:02.795 controller-0 ptp4l: notice [14608355.431] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T21:49:02.848 controller-0 ptp4l: notice [14608355.484] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T21:49:02.901 controller-0 ptp4l: notice [14608355.537] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T21:49:06.607 controller-0 ptp4l: notice [14608359.242] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T21:49:06.673 controller-0 ptp4l: notice [14608359.309] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T21:49:06.792 controller-0 ptp4l: notice [14608359.428] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T21:49:06.841 controller-0 ptp4l: notice [14608359.477] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T21:49:07.087 controller-0 ptp4l: notice [14608359.723] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T21:49:07.135 controller-0 ptp4l: notice [14608359.771] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-03T23:28:46.137 controller-0 etcd[23910]: warning request "header:<ID:7587882124342037772 > lease_revoke:<id:694d9296faf18c07>" with result "size:31" took too long (157.338536ms) to execute
2025-04-04T01:16:00.134 controller-0 etcd[23910]: warning request "header:<ID:7587882124342153461 username:\"apiserver-etcd-client\" auth_revision:1 > txn:<compare:<target:MOD key:\"/registry/leases/kube-system/kube-controller-manager\" mod_revision:94370646 > success:<request_put:<key:\"/registry/leases/kube-system/kube-controller-manager\" value_size:437 >> failure:<request_range:<key:\"/registry/leases/kube-system/kube-controller-manager\" > >>" with result "size:20" took too long (251.664332ms) to execute
2025-04-04T16:45:28.430 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/crd.projectcalico.org/bgpconfigurations/\" range_end:\"/registry/crd.projectcalico.org/bgpconfigurations0\" count_only:true " with result "range_response_count:0 size:7" took too long (102.180183ms) to execute
2025-04-04T20:41:34.036 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/secrets/kube-system/\" range_end:\"/registry/secrets/kube-system0\" " with result "range_response_count:33 size:320247" took too long (167.033561ms) to execute
2025-04-04T23:29:17.467 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/leases/kube-system/kube-controller-manager\" " with result "range_response_count:1 size:518" took too long (189.451235ms) to execute
2025-04-04T23:29:17.467 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/leases/kube-system/kube-scheduler\" " with result "range_response_count:1 size:491" took too long (190.456502ms) to execute
2025-04-04T23:29:17.467 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/leases/kube-system/external-snapshotter-leader-rbd-csi-ceph-com\" " with result "range_response_count:1 size:536" took too long (156.77095ms) to execute
2025-04-05T01:20:57.569 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/health\" " with result "range_response_count:0 size:7" took too long (101.255621ms) to execute
2025-04-05T03:40:07.578 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/health\" " with result "range_response_count:0 size:7" took too long (100.362104ms) to execute
2025-04-05T12:34:02.199 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/secrets/kube-system/\" range_end:\"/registry/secrets/kube-system0\" " with result "range_response_count:33 size:320247" took too long (189.988246ms) to execute
2025-04-05T14:35:58.065 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/pods/welktxsr-vzwcvdu-u-ss-adpf-29991563804/uadpf29991563804-rmp0-8574758c76-pxb9d\" " with result "range_response_count:1 size:12287" took too long (120.716268ms) to execute
2025-04-05T14:35:58.066 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/minions/controller-0\" " with result "range_response_count:1 size:18710" took too long (179.124601ms) to execute
2025-04-05T15:49:40.166 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/pods/welktxsr-vzwcvdu-u-ss-adpf-29991563804/\" range_end:\"/registry/pods/welktxsr-vzwcvdu-u-ss-adpf-299915638040\" " with result "range_response_count:7 size:73905" took too long (202.79881ms) to execute
2025-04-05T15:51:00.171 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/pods/welktxsr-vzwcvdu-u-ss-adpf-29991563804/\" range_end:\"/registry/pods/welktxsr-vzwcvdu-u-ss-adpf-299915638040\" " with result "range_response_count:7 size:73905" took too long (115.192642ms) to execute
2025-04-05T17:17:30.680 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/services/specs/welktxsr-vzwcvdu-u-ss-adpf-29991563804/\" range_end:\"/registry/services/specs/welktxsr-vzwcvdu-u-ss-adpf-299915638040\" " with result "range_response_count:7 size:60983" took too long (109.713352ms) to execute
2025-04-06T02:57:24.707 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/secrets/monitor/\" range_end:\"/registry/secrets/monitor0\" " with result "range_response_count:24 size:1019716" took too long (151.229794ms) to execute
2025-04-06T04:14:45.662 controller-0 etcd[23910]: warning request "header:<ID:7587882124345444975 username:\"apiserver-etcd-client\" auth_revision:1 > txn:<compare:<target:MOD key:\"/registry/leases/flux-helm/helm-controller-leader-election\" mod_revision:95192902 > success:<request_put:<key:\"/registry/leases/flux-helm/helm-controller-leader-election\" value_size:456 >> failure:<request_range:<key:\"/registry/leases/flux-helm/helm-controller-leader-election\" > >>" with result "size:20" took too long (204.992786ms) to execute
2025-04-06T04:21:51.612 controller-0 etcd[23910]: warning request "header:<ID:7587882124345452802 username:\"apiserver-etcd-client\" auth_revision:1 > txn:<compare:<target:MOD key:\"/registry/leases/kube-system/external-snapshotter-leader-rbd-csi-ceph-com\" mod_revision:95194821 > success:<request_put:<key:\"/registry/leases/kube-system/external-snapshotter-leader-rbd-csi-ceph-com\" value_size:433 >> failure:<request_range:<key:\"/registry/leases/kube-system/external-snapshotter-leader-rbd-csi-ceph-com\" > >>" with result "size:20" took too long (103.896188ms) to execute
2025-04-06T07:54:21.028 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/leases/kube-system/cert-manager-cainjector-leader-election\" " with result "range_response_count:1 size:564" took too long (157.98794ms) to execute
2025-04-06T08:02:41.787 controller-0 etcd[23910]: warning request "header:<ID:7587882124345690477 username:\"apiserver-etcd-client\" auth_revision:1 > txn:<compare:<target:MOD key:\"/registry/leases/kube-system/kube-scheduler\" mod_revision:95254198 > success:<request_put:<key:\"/registry/leases/kube-system/kube-scheduler\" value_size:419 >> failure:<request_range:<key:\"/registry/leases/kube-system/kube-scheduler\" > >>" with result "size:20" took too long (101.547205ms) to execute
2025-04-06T10:47:18.718 controller-0 etcd[23910]: warning request "header:<ID:7587882124345867614 username:\"apiserver-etcd-client\" auth_revision:1 > txn:<compare:<target:MOD key:\"/registry/leases/kube-system/kube-scheduler\" mod_revision:95298433 > success:<request_put:<key:\"/registry/leases/kube-system/kube-scheduler\" value_size:419 >> failure:<request_range:<key:\"/registry/leases/kube-system/kube-scheduler\" > >>" with result "size:20" took too long (169.832081ms) to execute
2025-04-06T13:24:38.067 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/leases/kube-system/external-snapshotter-leader-rbd-csi-ceph-com\" " with result "range_response_count:1 size:536" took too long (179.913493ms) to execute
2025-04-06T13:24:38.067 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/pods/welktxsr-vzwcvdu-u-ss-adpf-29991563804/\" range_end:\"/registry/pods/welktxsr-vzwcvdu-u-ss-adpf-299915638040\" " with result "range_response_count:7 size:73905" took too long (176.799527ms) to execute
2025-04-06T13:24:38.067 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/helm.toolkit.fluxcd.io/helmreleases/monitor/filebeat\" " with result "range_response_count:1 size:3715" took too long (186.779431ms) to execute
2025-04-06T13:24:38.067 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/leases/kube-system/external-resizer-rbd-csi-ceph-com\" " with result "range_response_count:1 size:510" took too long (153.012731ms) to execute
2025-04-06T23:46:32.705 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/leases/kube-system/rbd.csi.ceph.com-kube-system\" " with result "range_response_count:1 size:533" took too long (100.145944ms) to execute
2025-04-07T02:31:59.971 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/pods/welktxsr-vzwcvdu-u-ss-adpf-29991563804/uadpf29991563804-pmp0-7fff49b98-w8fjc\" " with result "range_response_count:1 size:8627" took too long (148.57219ms) to execute
2025-04-07T02:31:59.971 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/pods/welktxsr-vzwcvdu-u-ss-adpf-29991563804/uadpf29991563804-rmp0-8574758c76-pxb9d\" " with result "range_response_count:1 size:12287" took too long (155.237132ms) to execute
2025-04-07T08:22:58.766 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/leases/kube-system/external-snapshotter-leader-cephfs-csi-ceph-com\" " with result "range_response_count:1 size:544" took too long (145.431788ms) to execute
2025-04-07T08:22:58.766 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/leases/kube-system/external-attacher-leader-rbd-csi-ceph-com\" " with result "range_response_count:1 size:527" took too long (166.156413ms) to execute
2025-04-07T10:22:18.818 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/secrets/kube-system/\" range_end:\"/registry/secrets/kube-system0\" " with result "range_response_count:33 size:320247" took too long (180.445612ms) to execute
2025-04-07T12:01:22.261 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/helm.toolkit.fluxcd.io/helmreleases/kube-system/cephfs-provisioner\" " with result "range_response_count:1 size:3772" took too long (136.580611ms) to execute
2025-04-07T12:08:57.230 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/services/specs/welktxsr-vzwcvdu-u-ss-adpf-29991563804/\" range_end:\"/registry/services/specs/welktxsr-vzwcvdu-u-ss-adpf-299915638040\" " with result "range_response_count:7 size:60983" took too long (149.927401ms) to execute
2025-04-07T14:56:00.266 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/leases/flux-helm/helm-controller-leader-election\" " with result "range_response_count:1 size:543" took too long (201.491763ms) to execute
2025-04-07T14:56:00.266 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/services/specs/welktxsr-vzwcvdu-u-ss-adpf-29991563804/\" range_end:\"/registry/services/specs/welktxsr-vzwcvdu-u-ss-adpf-299915638040\" " with result "range_response_count:7 size:60983" took too long (187.281574ms) to execute
2025-04-07T14:56:00.266 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/pods/welktxsr-vzwcvdu-u-ss-adpf-29991563804/uadpf29991563804-cmp0-5bcb6f4964-wwzlh\" " with result "range_response_count:1 size:8444" took too long (117.5991ms) to execute
2025-04-07T14:56:00.266 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/pods/welktxsr-vzwcvdu-u-ss-adpf-29991563804/\" range_end:\"/registry/pods/welktxsr-vzwcvdu-u-ss-adpf-299915638040\" " with result "range_response_count:7 size:73905" took too long (169.552222ms) to execute
2025-04-07T17:34:36.583 controller-0 etcd[23910]: warning request "header:<ID:7587882124347854542 username:\"apiserver-etcd-client\" auth_revision:1 > txn:<compare:<target:MOD key:\"/registry/leases/kube-system/rbd.csi.ceph.com-kube-system\" mod_revision:95795025 > success:<request_put:<key:\"/registry/leases/kube-system/rbd.csi.ceph.com-kube-system\" value_size:446 >> failure:<request_range:<key:\"/registry/leases/kube-system/rbd.csi.ceph.com-kube-system\" > >>" with result "size:20" took too long (112.513248ms) to execute
2025-04-07T18:10:54.915 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/secrets/monitor/\" range_end:\"/registry/secrets/monitor0\" " with result "range_response_count:24 size:1019716" took too long (190.499356ms) to execute
2025-04-07T20:21:54.997 controller-0 ptp4l: notice [14948727.633] ptp4l-legacy port 1: SLAVE to MASTER on ANNOUNCE_RECEIPT_TIMEOUT_EXPIRES
2025-04-07T20:21:54.997 controller-0 ptp4l: notice [14948727.633] ptp4l-legacy selected local clock f0b2b9.fffe.031c6f as best master
2025-04-07T20:21:54.997 controller-0 ptp4l: notice [14948727.633] ptp4l-legacy port 1: assuming the grand master role
2025-04-07T20:21:54.997 controller-0 ptp4l: notice [14948727.633] ptp4l-legacy port 2: assuming the grand master role
2025-04-07T20:21:54.997 controller-0 ptp4l: notice [14948727.633] ptp4l-legacy port 3: assuming the grand master role
2025-04-07T20:21:54.997 controller-0 ptp4l: notice [14948727.633] ptp4l-legacy port 4: assuming the grand master role
2025-04-07T20:21:55.226 controller-0 ptp4l: notice [14948727.862] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-07T20:21:55.226 controller-0 ptp4l: notice [14948727.862] ptp4l-legacy port 1: MASTER to UNCALIBRATED on RS_SLAVE
2025-04-07T20:21:56.026 controller-0 ptp4l: notice [14948728.662] ptp4l-legacy port 1: UNCALIBRATED to MASTER on ANNOUNCE_RECEIPT_TIMEOUT_EXPIRES
2025-04-07T20:21:56.026 controller-0 ptp4l: notice [14948728.662] ptp4l-legacy selected local clock f0b2b9.fffe.031c6f as best master
2025-04-07T20:21:56.026 controller-0 ptp4l: notice [14948728.662] ptp4l-legacy port 1: assuming the grand master role
2025-04-07T20:21:56.026 controller-0 ptp4l: notice [14948728.662] ptp4l-legacy port 2: assuming the grand master role
2025-04-07T20:21:56.026 controller-0 ptp4l: notice [14948728.662] ptp4l-legacy port 3: assuming the grand master role
2025-04-07T20:21:56.026 controller-0 ptp4l: notice [14948728.662] ptp4l-legacy port 4: assuming the grand master role
2025-04-07T20:22:18.211 controller-0 ptp4l: err [14948750.847] ptp4l-legacy timed out while polling for tx timestamp
2025-04-07T20:22:18.211 controller-0 ptp4l: err [14948750.847] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2025-04-07T20:22:18.211 controller-0 ptp4l: err [14948750.847] ptp4l-legacy port 1: send sync failed
2025-04-07T20:22:18.211 controller-0 ptp4l: notice [14948750.847] ptp4l-legacy port 1: MASTER to FAULTY on FAULT_DETECTED (FT_UNSPECIFIED)
2025-04-07T20:22:18.240 controller-0 ptp4l: notice [14948750.876] ptp4l-legacy port 1: link down
2025-04-07T20:22:18.240 controller-0 ptp4l: notice [14948750.876] ptp4l-legacy selected local clock f0b2b9.fffe.031c6f as best master
2025-04-07T20:22:18.240 controller-0 ptp4l: notice [14948750.876] ptp4l-legacy port 1: assuming the grand master role
2025-04-07T20:22:18.240 controller-0 ptp4l: notice [14948750.876] ptp4l-legacy port 2: assuming the grand master role
2025-04-07T20:22:18.240 controller-0 ptp4l: notice [14948750.876] ptp4l-legacy port 3: assuming the grand master role
2025-04-07T20:22:18.240 controller-0 ptp4l: notice [14948750.876] ptp4l-legacy port 4: assuming the grand master role
2025-04-07T20:25:42.158 controller-0 ptp4l: notice [14948954.792] ptp4l-legacy port 1: link up
2025-04-07T20:25:42.189 controller-0 ptp4l: notice [14948954.821] ptp4l-legacy port 1: FAULTY to LISTENING on INIT_COMPLETE
2025-04-07T20:25:42.664 controller-0 ptp4l: notice [14948955.300] ptp4l-legacy port 1: LISTENING to MASTER on ANNOUNCE_RECEIPT_TIMEOUT_EXPIRES
2025-04-07T20:25:42.664 controller-0 ptp4l: notice [14948955.300] ptp4l-legacy selected local clock f0b2b9.fffe.031c6f as best master
2025-04-07T20:25:42.664 controller-0 ptp4l: notice [14948955.300] ptp4l-legacy port 1: assuming the grand master role
2025-04-07T20:25:42.664 controller-0 ptp4l: notice [14948955.300] ptp4l-legacy port 2: assuming the grand master role
2025-04-07T20:25:42.664 controller-0 ptp4l: notice [14948955.300] ptp4l-legacy port 3: assuming the grand master role
2025-04-07T20:25:42.664 controller-0 ptp4l: notice [14948955.300] ptp4l-legacy port 4: assuming the grand master role
2025-04-07T20:25:47.118 controller-0 ptp4l: notice [14948959.754] ptp4l-legacy port 1: new foreign master 2c4a11.fffe.7fa180-23
2025-04-07T20:25:47.368 controller-0 ptp4l: notice [14948960.004] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-07T20:25:47.368 controller-0 ptp4l: notice [14948960.004] ptp4l-legacy port 1: MASTER to UNCALIBRATED on RS_SLAVE
2025-04-07T20:25:47.623 controller-0 ptp4l: notice [14948960.259] ptp4l-legacy port 1: UNCALIBRATED to SLAVE on MASTER_CLOCK_SELECTED
2025-04-08T01:25:44.078 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/services/specs/default/kubernetes\" " with result "range_response_count:1 size:722" took too long (144.449539ms) to execute
2025-04-08T06:01:32.090 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/secrets/kube-system/\" range_end:\"/registry/secrets/kube-system0\" " with result "range_response_count:33 size:320247" took too long (207.638204ms) to execute
2025-04-08T07:55:24.095 controller-0 etcd[23910]: warning request "header:<ID:7587882124348780891 username:\"apiserver-etcd-client\" auth_revision:1 > txn:<compare:<target:MOD key:\"/registry/minions/controller-0\" mod_revision:96026446 > success:<request_put:<key:\"/registry/minions/controller-0\" value_size:18649 >> failure:<request_range:<key:\"/registry/minions/controller-0\" > >>" with result "size:20" took too long (170.834173ms) to execute
2025-04-08T08:01:19.267 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/services/specs/welktxsr-vzwcvdu-u-ss-adpf-29991563804/\" range_end:\"/registry/services/specs/welktxsr-vzwcvdu-u-ss-adpf-299915638040\" " with result "range_response_count:7 size:60983" took too long (188.061054ms) to execute
2025-04-08T14:52:57.778 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/minions/controller-0\" " with result "range_response_count:1 size:18710" took too long (118.019049ms) to execute
2025-04-08T18:20:17.895 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/secrets/kube-system/\" range_end:\"/registry/secrets/kube-system0\" " with result "range_response_count:33 size:320247" took too long (105.635061ms) to execute
2025-04-08T21:24:54.424 controller-0 ptp4l: notice [15038907.058] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-08T21:24:54.499 controller-0 ptp4l: notice [15038907.135] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-08T21:24:55.382 controller-0 ptp4l: notice [15038908.017] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-08T21:24:55.448 controller-0 ptp4l: notice [15038908.083] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-08T21:24:55.769 controller-0 ptp4l: notice [15038908.405] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-08T21:24:55.838 controller-0 ptp4l: notice [15038908.474] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-08T21:24:56.808 controller-0 ptp4l: notice [15038909.444] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-08T21:24:56.859 controller-0 ptp4l: notice [15038909.495] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-08T21:24:56.935 controller-0 ptp4l: notice [15038909.571] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-08T21:24:56.991 controller-0 ptp4l: notice [15038909.627] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-08T21:24:57.107 controller-0 ptp4l: notice [15038909.743] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-08T21:24:57.290 controller-0 ptp4l: notice [15038909.927] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-08T21:25:12.717 controller-0 ptp4l: notice [15038925.352] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-08T21:25:12.761 controller-0 ptp4l: notice [15038925.397] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-08T21:25:12.833 controller-0 ptp4l: notice [15038925.469] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-08T21:25:12.892 controller-0 ptp4l: notice [15038925.529] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-08T21:25:12.969 controller-0 ptp4l: notice [15038925.605] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-08T21:25:13.047 controller-0 ptp4l: notice [15038925.683] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-08T21:25:23.584 controller-0 ptp4l: notice [15038936.220] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-08T21:25:23.641 controller-0 ptp4l: notice [15038936.276] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-08T21:25:23.716 controller-0 ptp4l: notice [15038936.352] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-08T21:25:23.773 controller-0 ptp4l: notice [15038936.408] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-08T21:25:23.829 controller-0 ptp4l: notice [15038936.465] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-08T21:25:23.878 controller-0 ptp4l: notice [15038936.514] ptp4l-legacy selected best master clock 2c4a11.fffe.7fa180
2025-04-09T06:58:20.530 controller-0 etcd[23910]: warning request "header:<ID:7587882124350272354 username:\"apiserver-etcd-client\" auth_revision:1 > txn:<compare:<target:MOD key:\"/registry/minions/controller-0\" mod_revision:96398496 > success:<request_put:<key:\"/registry/minions/controller-0\" value_size:18649 >> failure:<request_range:<key:\"/registry/minions/controller-0\" > >>" with result "size:20" took too long (123.500653ms) to execute
2025-04-09T07:09:05.198 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/services/specs/welktxsr-vzwcvdu-u-ss-adpf-29991563804/\" range_end:\"/registry/services/specs/welktxsr-vzwcvdu-u-ss-adpf-299915638040\" " with result "range_response_count:7 size:60983" took too long (240.434598ms) to execute
2025-04-09T12:21:18.765 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/leases/kube-system/kube-scheduler\" " with result "range_response_count:1 size:492" took too long (135.132304ms) to execute
2025-04-09T15:26:18.666 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/configmaps/\" range_end:\"/registry/configmaps0\" count_only:true " with result "range_response_count:0 size:9" took too long (176.039431ms) to execute
2025-04-09T18:26:03.312 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/pods/welktxsr-vzwcvdu-u-ss-adpf-29991563804/\" range_end:\"/registry/pods/welktxsr-vzwcvdu-u-ss-adpf-299915638040\" " with result "range_response_count:6 size:68518" took too long (102.52996ms) to execute
2025-04-09T23:13:20.274 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/pods/welktxsr-vzwcvdu-u-ss-adpf-29991563804/uadpf29991563804-dpp0-547cdfc48f-bs94v\" " with result "range_response_count:1 size:20663" took too long (145.476757ms) to execute
2025-04-09T23:17:57.867 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/leases/kube-system/external-resizer-rbd-csi-ceph-com\" " with result "range_response_count:1 size:510" took too long (131.928788ms) to execute
2025-04-09T23:57:00.719 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/pods/welktxsr-vzwcvdu-u-ss-adpf-29991563804/\" range_end:\"/registry/pods/welktxsr-vzwcvdu-u-ss-adpf-299915638040\" " with result "range_response_count:6 size:68518" took too long (143.343201ms) to execute
2025-04-10T07:20:24.989 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/pods/welktxsr-vzwcvdu-u-ss-adpf-29991563804/\" range_end:\"/registry/pods/welktxsr-vzwcvdu-u-ss-adpf-299915638040\" " with result "range_response_count:6 size:68518" took too long (306.625506ms) to execute
2025-04-10T07:34:18.071 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/leases/kube-system/cert-manager-controller\" " with result "range_response_count:1 size:517" took too long (193.277561ms) to execute
2025-04-10T07:34:18.071 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/services/specs/welktxsr-vzwcvdu-u-ss-adpf-29991563804/\" range_end:\"/registry/services/specs/welktxsr-vzwcvdu-u-ss-adpf-299915638040\" " with result "range_response_count:7 size:60983" took too long (113.341786ms) to execute
2025-04-10T17:47:59.667 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/minions/controller-0\" " with result "range_response_count:1 size:18710" took too long (159.28715ms) to execute
2025-04-10T22:06:02.422 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/leases/kube-system/cephfs-csi-ceph-com\" " with result "range_response_count:1 size:492" took too long (154.604049ms) to execute
2025-04-10T23:12:59.074 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/pods/welktxsr-vzwcvdu-u-ss-adpf-29991563804/uadpf29991563804-dip0-55f8b95b47-mg54x\" " with result "range_response_count:1 size:9636" took too long (195.112248ms) to execute
2025-04-10T23:12:59.074 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/pods/welktxsr-vzwcvdu-u-ss-adpf-29991563804/uadpf29991563804-rmp0-8574758c76-glpqb\" " with result "range_response_count:1 size:12287" took too long (191.826853ms) to execute
2025-04-10T23:12:59.074 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/namespaces/default\" " with result "range_response_count:1 size:345" took too long (185.126497ms) to execute
2025-04-10T23:12:59.074 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/pods/welktxsr-vzwcvdu-u-ss-adpf-29991563804/uadpf29991563804-cmp0-5bcb6f4964-8xp4p\" " with result "range_response_count:1 size:8444" took too long (179.300118ms) to execute
2025-04-10T23:12:59.075 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/pods/welktxsr-vzwcvdu-u-ss-adpf-29991563804/uadpf29991563804-pmp0-7fff49b98-vwrsm\" " with result "range_response_count:1 size:8380" took too long (173.923672ms) to execute
2025-04-10T23:12:59.075 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/services/specs/welktxsr-vzwcvdu-u-ss-adpf-29991563804/\" range_end:\"/registry/services/specs/welktxsr-vzwcvdu-u-ss-adpf-299915638040\" " with result "range_response_count:7 size:60983" took too long (116.03168ms) to execute
2025-04-11T19:12:17.566 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/minions/controller-0\" " with result "range_response_count:1 size:18710" took too long (127.059016ms) to execute
2025-04-11T20:48:36.375 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/services/specs/welktxsr-vzwcvdu-u-ss-adpf-29991563804/\" range_end:\"/registry/services/specs/welktxsr-vzwcvdu-u-ss-adpf-299915638040\" " with result "range_response_count:7 size:60983" took too long (106.399314ms) to execute
2025-04-12T01:38:59.368 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/leases/kube-system/kube-scheduler\" " with result "range_response_count:1 size:491" took too long (196.432553ms) to execute
2025-04-12T01:38:59.368 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/leases/kube-system/rbd.csi.ceph.com-kube-system\" " with result "range_response_count:1 size:532" took too long (160.868807ms) to execute
2025-04-12T01:38:59.368 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/pods/welktxsr-vzwcvdu-u-ss-adpf-29991563804/\" range_end:\"/registry/pods/welktxsr-vzwcvdu-u-ss-adpf-299915638040\" " with result "range_response_count:6 size:68518" took too long (193.196701ms) to execute
2025-04-12T09:21:19.568 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/minions/controller-0\" " with result "range_response_count:1 size:18710" took too long (173.568391ms) to execute
2025-04-12T15:15:04.081 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/services/specs/welktxsr-vzwcvdu-u-ss-adpf-29991563804/\" range_end:\"/registry/services/specs/welktxsr-vzwcvdu-u-ss-adpf-299915638040\" " with result "range_response_count:7 size:60983" took too long (121.325546ms) to execute
2025-04-12T16:13:17.765 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/leases/kube-system/external-snapshotter-leader-cephfs-csi-ceph-com\" " with result "range_response_count:1 size:544" took too long (177.307592ms) to execute
2025-04-12T16:13:17.765 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/health\" " with result "range_response_count:0 size:7" took too long (295.178231ms) to execute
2025-04-12T16:13:17.765 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/leases/kube-system/external-attacher-leader-rbd-csi-ceph-com\" " with result "range_response_count:1 size:527" took too long (204.02192ms) to execute
2025-04-12T16:13:17.765 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/leases/kube-system/external-resizer-rbd-csi-ceph-com\" " with result "range_response_count:1 size:510" took too long (270.353475ms) to execute
2025-04-12T17:54:59.770 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/minions/controller-0\" " with result "range_response_count:1 size:18710" took too long (101.961652ms) to execute
2025-04-12T18:22:19.277 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/secrets/kube-system/\" range_end:\"/registry/secrets/kube-system0\" " with result "range_response_count:33 size:320247" took too long (319.165881ms) to execute
2025-04-12T19:06:59.366 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/leases/flux-helm/source-controller-leader-election\" " with result "range_response_count:1 size:551" took too long (115.247134ms) to execute
2025-04-12T19:06:59.366 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/minions/controller-0\" " with result "range_response_count:1 size:18710" took too long (180.421004ms) to execute
2025-04-12T19:40:47.472 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/pods/welktxsr-vzwcvdu-u-ss-adpf-29991563804/uadpf29991563804-cmp0-5bcb6f4964-8xp4p\" " with result "range_response_count:1 size:8444" took too long (141.854728ms) to execute
2025-04-12T19:44:59.683 controller-0 ptp4l: err [15378512.310] ptp4l-legacy failed to adjust the clock: Input/output error
2025-04-12T19:44:59.751 controller-0 phc2sys: err [15378512.373] phc2sys-legacy ioctl PTP_SYS_OFFSET_EXTENDED: Device or resource busy
2025-04-12T19:44:59.751 controller-0 ptp4l: err [15378512.373] ptp4l-legacy failed to adjust the clock: Input/output error
2025-04-12T19:44:59.799 controller-0 ptp4l: err [15378512.435] ptp4l-legacy failed to adjust the clock: Input/output error
2025-04-12T19:44:59.863 controller-0 ptp4l: err [15378512.499] ptp4l-legacy failed to adjust the clock: Input/output error
2025-04-12T20:12:40.395 controller-0 etcd[23910]: warning request "header:<ID:7587882124355774360 username:\"apiserver-etcd-client\" auth_revision:1 > txn:<compare:<target:MOD key:\"/registry/configmaps/kube-system/cert-manager-controller\" mod_revision:97773312 > success:<request_put:<key:\"/registry/configmaps/kube-system/cert-manager-controller\" value_size:525 >> failure:<request_range:<key:\"/registry/configmaps/kube-system/cert-manager-controller\" > >>" with result "size:20" took too long (151.305431ms) to execute
2025-04-12T23:56:38.873 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/dex.coreos.com/authrequests/kube-system/hc42u5s3dhdecwjjsmculyvqu\" " with result "range_response_count:1 size:886" took too long (275.825206ms) to execute
2025-04-12T23:56:38.873 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/pods/welktxsr-vzwcvdu-u-ss-adpf-29991563804/\" range_end:\"/registry/pods/welktxsr-vzwcvdu-u-ss-adpf-299915638040\" " with result "range_response_count:6 size:68518" took too long (125.91938ms) to execute
2025-04-13T00:38:52.174 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/pods/welktxsr-vzwcvdu-u-ss-adpf-29991563804/\" range_end:\"/registry/pods/welktxsr-vzwcvdu-u-ss-adpf-299915638040\" " with result "range_response_count:6 size:68518" took too long (129.933027ms) to execute
2025-04-13T00:58:22.016 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/crd.projectcalico.org/bgpconfigurations/\" range_end:\"/registry/crd.projectcalico.org/bgpconfigurations0\" count_only:true " with result "range_response_count:0 size:7" took too long (197.350456ms) to execute
2025-04-13T07:38:27.264 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/secrets/kube-system/\" range_end:\"/registry/secrets/kube-system0\" " with result "range_response_count:33 size:320247" took too long (135.31452ms) to execute
2025-04-13T10:10:18.086 controller-0 etcd[23910]: warning request "header:<ID:7587882124356675488 username:\"apiserver-etcd-client\" auth_revision:1 > txn:<compare:<target:MOD key:\"/registry/minions/controller-0\" mod_revision:97998520 > success:<request_put:<key:\"/registry/minions/controller-0\" value_size:18649 >> failure:<request_range:<key:\"/registry/minions/controller-0\" > >>" with result "size:20" took too long (132.895023ms) to execute
2025-04-13T10:52:33.370 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/secrets/kube-system/\" range_end:\"/registry/secrets/kube-system0\" " with result "range_response_count:33 size:320247" took too long (116.196551ms) to execute
2025-04-13T12:30:00.151 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/pods/welktxsr-vzwcvdu-u-ss-adpf-29991563804/\" range_end:\"/registry/pods/welktxsr-vzwcvdu-u-ss-adpf-299915638040\" " with result "range_response_count:6 size:68518" took too long (104.071564ms) to execute
2025-04-13T13:53:38.168 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/services/specs/welktxsr-vzwcvdu-u-ss-adpf-29991563804/\" range_end:\"/registry/services/specs/welktxsr-vzwcvdu-u-ss-adpf-299915638040\" " with result "range_response_count:7 size:60983" took too long (209.336762ms) to execute
2025-04-13T13:53:38.168 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/ranges/serviceips\" " with result "range_response_count:1 size:8219" took too long (230.251557ms) to execute
2025-04-13T13:53:38.168 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/leases/flux-helm/source-controller-leader-election\" " with result "range_response_count:1 size:552" took too long (247.271711ms) to execute
2025-04-13T13:53:38.169 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/leases/kube-system/external-resizer-rbd-csi-ceph-com\" " with result "range_response_count:1 size:509" took too long (101.529556ms) to execute
2025-04-13T13:53:38.169 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/csistoragecapacities/\" range_end:\"/registry/csistoragecapacities0\" count_only:true " with result "range_response_count:0 size:7" took too long (198.387289ms) to execute
2025-04-13T13:53:38.169 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/leases/kube-system/external-resizer-cephfs-csi-ceph-com\" " with result "range_response_count:1 size:516" took too long (101.932359ms) to execute
2025-04-13T13:53:38.169 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/leases/kube-system/external-attacher-leader-rbd-csi-ceph-com\" " with result "range_response_count:1 size:526" took too long (104.959157ms) to execute
2025-04-13T13:53:38.169 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/leases/kube-system/external-snapshotter-leader-cephfs-csi-ceph-com\" " with result "range_response_count:1 size:543" took too long (108.804044ms) to execute
2025-04-13T13:53:38.169 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/leases/kube-system/external-snapshotter-leader-rbd-csi-ceph-com\" " with result "range_response_count:1 size:535" took too long (120.129213ms) to execute
2025-04-13T13:53:38.169 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/leases/kube-system/cephfs-csi-ceph-com\" " with result "range_response_count:1 size:492" took too long (126.007854ms) to execute
2025-04-13T13:53:38.169 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/leases/kube-system/rbd-csi-ceph-com\" " with result "range_response_count:1 size:483" took too long (126.060523ms) to execute
2025-04-13T16:50:11.009 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/pods/welktxsr-vzwcvdu-u-ss-adpf-29991563804/uadpf29991563804-dpp0-547cdfc48f-bs94v\" " with result "range_response_count:1 size:20663" took too long (126.509116ms) to execute
2025-04-13T17:12:43.972 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/pods/welktxsr-vzwcvdu-u-ss-adpf-29991563804/\" range_end:\"/registry/pods/welktxsr-vzwcvdu-u-ss-adpf-299915638040\" " with result "range_response_count:6 size:68518" took too long (189.734355ms) to execute
2025-04-13T17:12:43.972 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/leases/kube-system/cephfs-csi-ceph-com\" " with result "range_response_count:1 size:493" took too long (185.188973ms) to execute
2025-04-13T17:12:43.972 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/leases/kube-system/external-snapshotter-leader-rbd-csi-ceph-com\" " with result "range_response_count:1 size:536" took too long (174.291716ms) to execute
2025-04-13T17:12:43.972 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/leases/kube-system/external-resizer-cephfs-csi-ceph-com\" " with result "range_response_count:1 size:517" took too long (146.587121ms) to execute
2025-04-13T17:12:43.972 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/leases/kube-system/external-resizer-rbd-csi-ceph-com\" " with result "range_response_count:1 size:510" took too long (144.007394ms) to execute
2025-04-13T17:23:00.166 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/leases/flux-helm/helm-controller-leader-election\" " with result "range_response_count:1 size:544" took too long (159.718644ms) to execute
2025-04-13T20:09:45.697 controller-0 etcd[23910]: warning request "header:<ID:7587882124357320073 username:\"apiserver-etcd-client\" auth_revision:1 > txn:<compare:<target:MOD key:\"/registry/minions/controller-0\" mod_revision:98159603 > success:<request_put:<key:\"/registry/minions/controller-0\" value_size:18649 >> failure:<request_range:<key:\"/registry/minions/controller-0\" > >>" with result "size:20" took too long (154.378452ms) to execute
2025-04-14T00:49:13.250 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/pods/welktxsr-vzwcvdu-u-ss-adpf-29991563804/\" range_end:\"/registry/pods/welktxsr-vzwcvdu-u-ss-adpf-299915638040\" " with result "range_response_count:6 size:68518" took too long (176.990587ms) to execute
2025-04-14T03:00:02.633 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/pods/welktxsr-vzwcvdu-u-ss-adpf-29991563804/\" range_end:\"/registry/pods/welktxsr-vzwcvdu-u-ss-adpf-299915638040\" " with result "range_response_count:6 size:68518" took too long (195.708719ms) to execute
2025-04-14T05:15:01.633 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/pods/welktxsr-vzwcvdu-u-ss-adpf-29991563804/\" range_end:\"/registry/pods/welktxsr-vzwcvdu-u-ss-adpf-299915638040\" " with result "range_response_count:6 size:68518" took too long (110.698368ms) to execute
2025-04-14T05:15:01.633 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/pods/welktxsr-vzwcvdu-u-ss-adpf-29991563804/\" range_end:\"/registry/pods/welktxsr-vzwcvdu-u-ss-adpf-299915638040\" " with result "range_response_count:6 size:68518" took too long (111.663002ms) to execute
2025-04-14T06:54:35.671 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/secrets/kube-system/\" range_end:\"/registry/secrets/kube-system0\" " with result "range_response_count:33 size:320247" took too long (162.592505ms) to execute
2025-04-14T12:14:19.366 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/leases/kube-system/external-snapshotter-leader-cephfs-csi-ceph-com\" " with result "range_response_count:1 size:543" took too long (106.548822ms) to execute
2025-04-14T12:14:19.366 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/pods/welktxsr-vzwcvdu-u-ss-adpf-29991563804/uadpf29991563804-rmp0-8574758c76-glpqb\" " with result "range_response_count:1 size:12287" took too long (117.506206ms) to execute
2025-04-14T15:01:34.928 controller-0 etcd[23910]: warning request "header:<ID:7587882124358537208 username:\"apiserver-etcd-client\" auth_revision:1 > txn:<compare:<target:MOD key:\"/registry/leases/kube-system/kube-controller-manager\" mod_revision:98463847 > success:<request_put:<key:\"/registry/leases/kube-system/kube-controller-manager\" value_size:437 >> failure:<request_range:<key:\"/registry/leases/kube-system/kube-controller-manager\" > >>" with result "size:20" took too long (229.400202ms) to execute
2025-04-14T16:25:48.564 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/leases/kube-system/external-attacher-leader-rbd-csi-ceph-com\" " with result "range_response_count:1 size:527" took too long (220.847201ms) to execute
2025-04-14T19:00:00.344 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/pods/welktxsr-vzwcvdu-u-ss-adpf-29991563804/\" range_end:\"/registry/pods/welktxsr-vzwcvdu-u-ss-adpf-299915638040\" " with result "range_response_count:6 size:68518" took too long (136.227831ms) to execute
2025-04-15T00:03:03.047 controller-0 etcd[23910]: warning request "header:<ID:7587882124359119531 username:\"apiserver-etcd-client\" auth_revision:1 > txn:<compare:<target:MOD key:\"/registry/leases/kube-system/rbd.csi.ceph.com-kube-system\" mod_revision:98609365 > success:<request_put:<key:\"/registry/leases/kube-system/rbd.csi.ceph.com-kube-system\" value_size:446 >> failure:<request_range:<key:\"/registry/leases/kube-system/rbd.csi.ceph.com-kube-system\" > >>" with result "size:20" took too long (243.268916ms) to execute
2025-04-15T07:54:47.572 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/health\" " with result "range_response_count:0 size:7" took too long (100.418111ms) to execute
2025-04-15T07:54:47.572 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/minions/controller-0\" " with result "range_response_count:1 size:18710" took too long (194.18191ms) to execute
2025-04-15T12:29:22.654 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/minions/controller-0\" " with result "range_response_count:1 size:18710" took too long (146.723977ms) to execute
2025-04-15T15:03:18.667 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/leases/kube-system/external-resizer-cephfs-csi-ceph-com\" " with result "range_response_count:1 size:517" took too long (182.221153ms) to execute
2025-04-15T15:03:18.667 controller-0 etcd[23910]: warning read-only range request "key:\"/registry/leases/kube-system/external-attacher-leader-rbd-csi-ceph-com\" " with result "range_response_count:1 size:527" took too long (173.33001ms) to execute
[XXXXXX@controller-0 log(keystone_admin)]$
```


### Test appears to be success, we don't see an issue with PTPL4 timeouts, the LaaS team has not called with any issue.
### Test is success