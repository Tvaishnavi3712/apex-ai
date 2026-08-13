# ZT Proteus .46 BMC firmware validation
# ZT Proteus BIOS .23
# 1/18/24 James Patchett

## Soak started with this system on 1/10/24 
## Soak period is 1/10/24-1/18/24 (~8 days)

## Target Subcloud welktxef-d1372466-007
OAM: 2607:f160:10:8067:ce:40a:0:f408
BMC: 2607:f160:10:8067:ce:40a:0:e005

### BMC & BIOS on the system

```log
[XXXXXX@welktxefnce-h-pe1util-vm01 host_vars]$ IP=2607:f160:10:8067:ce:40a:0:e005
[XXXXXX@welktxefnce-h-pe1util-vm01 host_vars]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[${IP}]/redfish/v1/UpdateService/FirmwareInventory/BMC | jq .
{
  "@odata.context": "/redfish/v1/$metadata#SoftwareInventory.SoftwareInventory",
  "@odata.etag": "\"1704926637\"",
  "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/BMC",
  "@odata.type": "#SoftwareInventory.v1_2_3.SoftwareInventory",
  "Id": "BMC",
  "Name": "BMC",
  "Updateable": true,
  "Version": "0.46.00"
}
[XXXXXX@welktxefnce-h-pe1util-vm01 host_vars]$ curl -gsk -u XXXXXX:XXXXXX -X GET https://[${IP}]/redfish/v1/UpdateService/FirmwareInventory/BIOS | jq .
{
  "@odata.context": "/redfish/v1/$metadata#SoftwareInventory.SoftwareInventory",
  "@odata.etag": "\"1705523746\"",
  "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/BIOS",
  "@odata.type": "#SoftwareInventory.v1_2_3.SoftwareInventory",
  "Id": "BIOS",
  "Name": "BIOS",
  "Updateable": true,
  "Version": "0.23"
}
[XXXXXX@welktxefnce-h-pe1util-vm01 host_vars]$
```


### Looking at /var/log/user.log for any increase of PTPL4 sync errors over the 1 week soak period

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ cat /var/log/user.log | grep -e "XXXXXX" -e "XXXXXX"
2023-12-11T04:24:37.000 controller-0 ptp4l: err [9973826.378] ptp4l-legacy timed out while polling for tx timestamp
2023-12-11T04:24:37.000 controller-0 ptp4l: err [9973826.378] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2023-12-11T07:01:37.000 controller-0 ptp4l: err [9983245.597] ptp4l-legacy timed out while polling for tx timestamp
2023-12-11T07:01:37.000 controller-0 ptp4l: err [9983245.597] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2023-12-11T19:16:17.000 controller-0 ptp4l: err [10027326.360] ptp4l-legacy timed out while polling for tx timestamp
2023-12-11T19:16:17.000 controller-0 ptp4l: err [10027326.360] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2023-12-13T18:35:10.000 controller-0 ptp4l: err [10197659.312] ptp4l-legacy timed out while polling for tx timestamp
2023-12-13T18:35:10.000 controller-0 ptp4l: err [10197659.312] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2023-12-13T18:35:11.000 controller-0 ptp4l: err [10197660.007] ptp4l-legacy timed out while polling for tx timestamp
2023-12-13T18:35:11.000 controller-0 ptp4l: err [10197660.007] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2023-12-13T18:38:12.000 controller-0 ptp4l: err [10197840.501] ptp4l-legacy timed out while polling for tx timestamp
2023-12-13T18:38:12.000 controller-0 ptp4l: err [10197840.501] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2023-12-14T23:30:09.000 controller-0 ptp4l: err [10301758.405] ptp4l-legacy timed out while polling for tx timestamp
2023-12-14T23:30:09.000 controller-0 ptp4l: err [10301758.405] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2023-12-14T23:30:19.000 controller-0 ptp4l: err [10301768.263] ptp4l-legacy timed out while polling for tx timestamp
2023-12-14T23:30:19.000 controller-0 ptp4l: err [10301768.263] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2023-12-14T23:30:19.000 controller-0 ptp4l: err [10301768.415] ptp4l-legacy timed out while polling for tx timestamp
2023-12-14T23:30:19.000 controller-0 ptp4l: err [10301768.415] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2023-12-14T23:31:03.000 controller-0 ptp4l: err [10301811.940] ptp4l-legacy timed out while polling for tx timestamp
2023-12-14T23:31:03.000 controller-0 ptp4l: err [10301811.940] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2023-12-14T23:33:04.000 controller-0 ptp4l: err [10301932.817] ptp4l-legacy timed out while polling for tx timestamp
2023-12-14T23:33:04.000 controller-0 ptp4l: err [10301932.817] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2023-12-14T23:33:26.000 controller-0 ptp4l: err [10301955.223] ptp4l-legacy timed out while polling for tx timestamp
2023-12-14T23:33:26.000 controller-0 ptp4l: err [10301955.223] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2023-12-16T08:53:37.000 controller-0 ptp4l: err [10421965.963] ptp4l-legacy timed out while polling for tx timestamp
2023-12-16T08:53:37.000 controller-0 ptp4l: err [10421965.963] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2023-12-17T19:45:48.000 controller-0 ptp4l: err [10547496.642] ptp4l-legacy timed out while polling for tx timestamp
2023-12-17T19:45:48.000 controller-0 ptp4l: err [10547496.642] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2023-12-18T03:02:18.000 controller-0 ptp4l: err [10573686.582] ptp4l-legacy timed out while polling for tx timestamp
2023-12-18T03:02:18.000 controller-0 ptp4l: err [10573686.582] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2023-12-18T22:40:37.000 controller-0 ptp4l: err [10644385.602] ptp4l-legacy timed out while polling for tx timestamp
2023-12-18T22:40:37.000 controller-0 ptp4l: err [10644385.602] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2023-12-19T05:35:10.000 controller-0 ptp4l: err [10669258.804] ptp4l-legacy timed out while polling for tx timestamp
2023-12-19T05:35:10.000 controller-0 ptp4l: err [10669258.804] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2023-12-19T16:57:38.000 controller-0 ptp4l: err [10710206.578] ptp4l-legacy timed out while polling for tx timestamp
2023-12-19T16:57:38.000 controller-0 ptp4l: err [10710206.578] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2023-12-19T20:27:57.000 controller-0 ptp4l: err [96.961] ptp4l-legacy timed out while polling for tx timestamp
2023-12-19T20:27:57.000 controller-0 ptp4l: err [96.961] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2023-12-19T20:41:19.000 controller-0 ptp4l: err [899.018] ptp4l-legacy timed out while polling for tx timestamp
2023-12-19T20:41:19.000 controller-0 ptp4l: err [899.018] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2023-12-19T20:42:29.000 controller-0 ptp4l: err [968.622] ptp4l-legacy timed out while polling for tx timestamp
2023-12-19T20:42:29.000 controller-0 ptp4l: err [968.622] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2023-12-19T21:58:17.000 controller-0 ptp4l: err [100.043] ptp4l-legacy timed out while polling for tx timestamp
2023-12-19T21:58:17.000 controller-0 ptp4l: err [100.043] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2023-12-19T22:06:08.000 controller-0 ptp4l: err [571.445] ptp4l-legacy timed out while polling for tx timestamp
2023-12-19T22:06:08.000 controller-0 ptp4l: err [571.445] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2023-12-19T22:07:35.000 controller-0 ptp4l: err [658.121] ptp4l-legacy timed out while polling for tx timestamp
2023-12-19T22:07:35.000 controller-0 ptp4l: err [658.121] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2023-12-21T14:45:01.000 controller-0 ptp4l: err [146904.441] ptp4l-legacy timed out while polling for tx timestamp
2023-12-21T14:45:01.000 controller-0 ptp4l: err [146904.441] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2023-12-21T14:45:15.000 controller-0 ptp4l: err [146918.414] ptp4l-legacy timed out while polling for tx timestamp
2023-12-21T14:45:15.000 controller-0 ptp4l: err [146918.414] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2023-12-21T14:47:35.000 controller-0 ptp4l: err [147058.758] ptp4l-legacy timed out while polling for tx timestamp
2023-12-21T14:47:35.000 controller-0 ptp4l: err [147058.759] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2023-12-21T14:47:59.000 controller-0 ptp4l: err [147082.241] ptp4l-legacy timed out while polling for tx timestamp
2023-12-21T14:47:59.000 controller-0 ptp4l: err [147082.241] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2023-12-21T14:48:34.000 controller-0 ptp4l: err [147117.184] ptp4l-legacy timed out while polling for tx timestamp
2023-12-21T14:48:34.000 controller-0 ptp4l: err [147117.184] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2023-12-22T02:14:16.000 controller-0 ptp4l: err [188259.073] ptp4l-legacy timed out while polling for tx timestamp
2023-12-22T02:14:16.000 controller-0 ptp4l: err [188259.073] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2023-12-23T04:18:36.000 controller-0 ptp4l: err [282119.299] ptp4l-legacy timed out while polling for tx timestamp
2023-12-23T04:18:36.000 controller-0 ptp4l: err [282119.299] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2023-12-29T12:15:56.000 controller-0 ptp4l: err [829158.992] ptp4l-legacy timed out while polling for tx timestamp
2023-12-29T12:15:56.000 controller-0 ptp4l: err [829158.992] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2023-12-29T12:18:58.000 controller-0 ptp4l: err [829341.412] ptp4l-legacy timed out while polling for tx timestamp
2023-12-29T12:18:58.000 controller-0 ptp4l: err [829341.412] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2023-12-30T21:14:56.000 controller-0 ptp4l: err [947899.392] ptp4l-legacy timed out while polling for tx timestamp
2023-12-30T21:14:56.000 controller-0 ptp4l: err [947899.392] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-04T17:37:23.000 controller-0 ptp4l: err [1366845.900] ptp4l-legacy timed out while polling for tx timestamp
2024-01-04T17:37:23.000 controller-0 ptp4l: err [1366845.900] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-04T18:09:14.000 controller-0 ptp4l: err [1368757.521] ptp4l-legacy timed out while polling for tx timestamp
2024-01-04T18:09:14.000 controller-0 ptp4l: err [1368757.521] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-07T21:07:16.000 controller-0 ptp4l: err [1638639.690] ptp4l-legacy timed out while polling for tx timestamp
2024-01-07T21:07:16.000 controller-0 ptp4l: err [1638639.690] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-08T20:36:56.000 controller-0 ptp4l: err [1723219.570] ptp4l-legacy timed out while polling for tx timestamp
2024-01-08T20:36:56.000 controller-0 ptp4l: err [1723219.570] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-08T21:48:48.000 controller-0 ptp4l: err [1727531.637] ptp4l-legacy timed out while polling for tx timestamp
2024-01-08T21:48:48.000 controller-0 ptp4l: err [1727531.637] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-09T15:08:11.000 controller-0 ptp4l: err [1789893.887] ptp4l-legacy timed out while polling for tx timestamp
2024-01-09T15:08:11.000 controller-0 ptp4l: err [1789893.887] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-09T15:17:01.000 controller-0 ptp4l: err [1790424.859] ptp4l-legacy timed out while polling for tx timestamp
2024-01-09T15:17:01.000 controller-0 ptp4l: err [1790424.859] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-09T15:17:19.000 controller-0 ptp4l: err [1790442.606] ptp4l-legacy timed out while polling for tx timestamp
2024-01-09T15:17:19.000 controller-0 ptp4l: err [1790442.606] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-09T15:17:21.000 controller-0 ptp4l: err [1790444.124] ptp4l-legacy timed out while polling for tx timestamp
2024-01-09T15:17:21.000 controller-0 ptp4l: err [1790444.124] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-09T15:18:33.000 controller-0 ptp4l: err [1790516.303] ptp4l-legacy timed out while polling for tx timestamp
2024-01-09T15:18:33.000 controller-0 ptp4l: err [1790516.303] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-09T15:20:11.000 controller-0 ptp4l: err [1790614.581] ptp4l-legacy timed out while polling for tx timestamp
2024-01-09T15:20:11.000 controller-0 ptp4l: err [1790614.581] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-09T15:20:25.000 controller-0 ptp4l: err [1790628.572] ptp4l-legacy timed out while polling for tx timestamp
2024-01-09T15:20:25.000 controller-0 ptp4l: err [1790628.572] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-09T15:20:28.000 controller-0 ptp4l: err [1790631.418] ptp4l-legacy timed out while polling for tx timestamp
2024-01-09T15:20:28.000 controller-0 ptp4l: err [1790631.418] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-09T15:21:18.000 controller-0 ptp4l: err [1790681.553] ptp4l-legacy timed out while polling for tx timestamp
2024-01-09T15:21:18.000 controller-0 ptp4l: err [1790681.553] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-09T15:21:19.000 controller-0 ptp4l: err [1790682.590] ptp4l-legacy timed out while polling for tx timestamp
2024-01-09T15:21:19.000 controller-0 ptp4l: err [1790682.590] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-09T15:21:42.000 controller-0 ptp4l: err [1790705.567] ptp4l-legacy timed out while polling for tx timestamp
2024-01-09T15:21:42.000 controller-0 ptp4l: err [1790705.567] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-09T15:23:14.000 controller-0 ptp4l: err [1790797.089] ptp4l-legacy timed out while polling for tx timestamp
2024-01-09T15:23:14.000 controller-0 ptp4l: err [1790797.089] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-09T15:23:47.000 controller-0 ptp4l: err [1790830.184] ptp4l-legacy timed out while polling for tx timestamp
2024-01-09T15:23:47.000 controller-0 ptp4l: err [1790830.184] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-09T15:23:52.000 controller-0 ptp4l: err [1790835.705] ptp4l-legacy timed out while polling for tx timestamp
2024-01-09T15:23:52.000 controller-0 ptp4l: err [1790835.705] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-09T15:24:35.000 controller-0 ptp4l: err [1790877.946] ptp4l-legacy timed out while polling for tx timestamp
2024-01-09T15:24:35.000 controller-0 ptp4l: err [1790877.946] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-09T15:24:45.000 controller-0 ptp4l: err [1790888.744] ptp4l-legacy timed out while polling for tx timestamp
2024-01-09T15:24:45.000 controller-0 ptp4l: err [1790888.744] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-09T15:24:46.000 controller-0 ptp4l: err [1790888.887] ptp4l-legacy timed out while polling for tx timestamp
2024-01-09T15:24:46.000 controller-0 ptp4l: err [1790888.887] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-09T15:25:39.000 controller-0 ptp4l: err [1790941.892] ptp4l-legacy timed out while polling for tx timestamp
2024-01-09T15:25:39.000 controller-0 ptp4l: err [1790941.892] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-09T15:25:59.000 controller-0 ptp4l: err [1790962.095] ptp4l-legacy timed out while polling for tx timestamp
2024-01-09T15:25:59.000 controller-0 ptp4l: err [1790962.095] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-09T15:26:35.000 controller-0 ptp4l: err [1790998.484] ptp4l-legacy timed out while polling for tx timestamp
2024-01-09T15:26:35.000 controller-0 ptp4l: err [1790998.484] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-09T15:27:08.000 controller-0 ptp4l: err [1791031.601] ptp4l-legacy timed out while polling for tx timestamp
2024-01-09T15:27:08.000 controller-0 ptp4l: err [1791031.601] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-09T15:28:23.000 controller-0 ptp4l: err [1791106.211] ptp4l-legacy timed out while polling for tx timestamp
2024-01-09T15:28:23.000 controller-0 ptp4l: err [1791106.211] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-09T15:28:42.000 controller-0 ptp4l: err [1791125.541] ptp4l-legacy timed out while polling for tx timestamp
2024-01-09T15:28:42.000 controller-0 ptp4l: err [1791125.541] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-09T15:30:59.000 controller-0 ptp4l: err [1791262.111] ptp4l-legacy timed out while polling for tx timestamp
2024-01-09T15:30:59.000 controller-0 ptp4l: err [1791262.111] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-09T15:41:55.000 controller-0 ptp4l: err [1791918.163] ptp4l-legacy timed out while polling for tx timestamp
2024-01-09T15:41:55.000 controller-0 ptp4l: err [1791918.163] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-09T15:41:56.000 controller-0 ptp4l: err [1791919.080] ptp4l-legacy timed out while polling for tx timestamp
2024-01-09T15:41:56.000 controller-0 ptp4l: err [1791919.080] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-09T15:42:40.000 controller-0 ptp4l: err [1791962.901] ptp4l-legacy timed out while polling for tx timestamp
2024-01-09T15:42:40.000 controller-0 ptp4l: err [1791962.901] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-09T15:42:40.000 controller-0 ptp4l: err [1791963.218] ptp4l-legacy timed out while polling for tx timestamp
2024-01-09T15:42:40.000 controller-0 ptp4l: err [1791963.218] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-09T15:43:12.000 controller-0 ptp4l: err [1791995.072] ptp4l-legacy timed out while polling for tx timestamp
2024-01-09T15:43:12.000 controller-0 ptp4l: err [1791995.072] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-09T15:43:16.000 controller-0 ptp4l: err [1791999.684] ptp4l-legacy timed out while polling for tx timestamp
2024-01-09T15:43:16.000 controller-0 ptp4l: err [1791999.684] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-09T15:43:18.000 controller-0 ptp4l: err [1792001.770] ptp4l-legacy timed out while polling for tx timestamp
2024-01-09T15:43:18.000 controller-0 ptp4l: err [1792001.770] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-09T15:46:04.000 controller-0 ptp4l: err [1792167.862] ptp4l-legacy timed out while polling for tx timestamp
2024-01-09T15:46:04.000 controller-0 ptp4l: err [1792167.862] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-09T16:50:42.000 controller-0 ptp4l: err [1796045.445] ptp4l-legacy timed out while polling for tx timestamp
2024-01-09T16:50:42.000 controller-0 ptp4l: err [1796045.445] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-09T16:50:48.000 controller-0 ptp4l: err [1796051.345] ptp4l-legacy timed out while polling for tx timestamp
2024-01-09T16:50:48.000 controller-0 ptp4l: err [1796051.345] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-09T16:50:49.000 controller-0 ptp4l: err [1796052.298] ptp4l-legacy timed out while polling for tx timestamp
2024-01-09T16:50:49.000 controller-0 ptp4l: err [1796052.298] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-09T16:51:40.000 controller-0 ptp4l: err [1796103.781] ptp4l-legacy timed out while polling for tx timestamp
2024-01-09T16:51:40.000 controller-0 ptp4l: err [1796103.781] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-09T16:53:20.000 controller-0 ptp4l: err [1796203.317] ptp4l-legacy timed out while polling for tx timestamp
2024-01-09T16:53:20.000 controller-0 ptp4l: err [1796203.317] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-09T16:53:21.000 controller-0 ptp4l: err [1796204.292] ptp4l-legacy timed out while polling for tx timestamp
2024-01-09T16:53:21.000 controller-0 ptp4l: err [1796204.292] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-09T21:09:47.000 controller-0 ptp4l: err [1811590.354] ptp4l-legacy timed out while polling for tx timestamp
2024-01-09T21:09:47.000 controller-0 ptp4l: err [1811590.354] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-09T21:10:26.000 controller-0 ptp4l: err [1811629.370] ptp4l-legacy timed out while polling for tx timestamp
2024-01-09T21:10:26.000 controller-0 ptp4l: err [1811629.370] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-09T21:10:31.000 controller-0 ptp4l: err [1811634.356] ptp4l-legacy timed out while polling for tx timestamp
2024-01-09T21:10:31.000 controller-0 ptp4l: err [1811634.356] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-09T21:10:32.000 controller-0 ptp4l: err [1811635.064] ptp4l-legacy timed out while polling for tx timestamp
2024-01-09T21:10:32.000 controller-0 ptp4l: err [1811635.064] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-09T21:11:24.000 controller-0 ptp4l: err [1811687.747] ptp4l-legacy timed out while polling for tx timestamp
2024-01-09T21:11:24.000 controller-0 ptp4l: err [1811687.747] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-09T21:13:10.000 controller-0 ptp4l: err [1811793.146] ptp4l-legacy timed out while polling for tx timestamp
2024-01-09T21:13:10.000 controller-0 ptp4l: err [1811793.146] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-09T21:13:11.000 controller-0 ptp4l: err [1811793.940] ptp4l-legacy timed out while polling for tx timestamp
2024-01-09T21:13:11.000 controller-0 ptp4l: err [1811793.940] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-09T21:15:39.000 controller-0 ptp4l: err [1811942.175] ptp4l-legacy timed out while polling for tx timestamp
2024-01-09T21:15:39.000 controller-0 ptp4l: err [1811942.175] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-10T18:00:10.000 controller-0 ptp4l: err [1886613.383] ptp4l-legacy timed out while polling for tx timestamp
2024-01-10T18:00:10.000 controller-0 ptp4l: err [1886613.383] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-11T21:50:18.000 controller-0 ptp4l: err [1986821.552] ptp4l-legacy timed out while polling for tx timestamp
2024-01-11T21:50:18.000 controller-0 ptp4l: err [1986821.552] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-11T21:50:34.000 controller-0 ptp4l: err [1986837.628] ptp4l-legacy timed out while polling for tx timestamp
2024-01-11T21:50:34.000 controller-0 ptp4l: err [1986837.628] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-12T06:01:00.000 controller-0 ptp4l: err [2016263.467] ptp4l-legacy timed out while polling for tx timestamp
2024-01-12T06:01:00.000 controller-0 ptp4l: err [2016263.467] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-12T21:35:06.000 controller-0 ptp4l: err [2072309.089] ptp4l-legacy timed out while polling for tx timestamp
2024-01-12T21:35:06.000 controller-0 ptp4l: err [2072309.089] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-13T01:36:40.000 controller-0 ptp4l: err [2086803.090] ptp4l-legacy timed out while polling for tx timestamp
2024-01-13T01:36:40.000 controller-0 ptp4l: err [2086803.090] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-14T16:19:10.000 controller-0 ptp4l: err [2226153.116] ptp4l-legacy timed out while polling for tx timestamp
2024-01-14T16:19:10.000 controller-0 ptp4l: err [2226153.116] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-14T16:22:30.000 controller-0 ptp4l: err [2226352.988] ptp4l-legacy timed out while polling for tx timestamp
2024-01-14T16:22:30.000 controller-0 ptp4l: err [2226352.988] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-16T13:02:36.000 controller-0 ptp4l: err [2387159.187] ptp4l-legacy timed out while polling for tx timestamp
2024-01-16T13:02:36.000 controller-0 ptp4l: err [2387159.187] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-16T17:30:09.000 controller-0 ptp4l: err [2403212.719] ptp4l-legacy timed out while polling for tx timestamp
2024-01-16T17:30:09.000 controller-0 ptp4l: err [2403212.719] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-16T20:19:16.000 controller-0 ptp4l: err [2413359.381] ptp4l-legacy timed out while polling for tx timestamp
2024-01-16T20:19:16.000 controller-0 ptp4l: err [2413359.381] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-17T02:12:20.000 controller-0 ptp4l: err [2434543.269] ptp4l-legacy timed out while polling for tx timestamp
2024-01-17T02:12:20.000 controller-0 ptp4l: err [2434543.269] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-17T16:01:11.000 controller-0 ptp4l: err [2484274.048] ptp4l-legacy timed out while polling for tx timestamp
2024-01-17T16:01:11.000 controller-0 ptp4l: err [2484274.048] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-17T16:01:11.000 controller-0 ptp4l: err [2484274.366] ptp4l-legacy timed out while polling for tx timestamp
2024-01-17T16:01:11.000 controller-0 ptp4l: err [2484274.367] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-17T16:02:03.000 controller-0 ptp4l: err [2484325.923] ptp4l-legacy timed out while polling for tx timestamp
2024-01-17T16:02:03.000 controller-0 ptp4l: err [2484325.923] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-17T16:02:10.000 controller-0 ptp4l: err [2484333.250] ptp4l-legacy timed out while polling for tx timestamp
2024-01-17T16:02:10.000 controller-0 ptp4l: err [2484333.250] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-17T16:05:07.000 controller-0 ptp4l: err [2484510.582] ptp4l-legacy timed out while polling for tx timestamp
2024-01-17T16:05:07.000 controller-0 ptp4l: err [2484510.582] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-17T16:05:10.000 controller-0 ptp4l: err [2484513.306] ptp4l-legacy timed out while polling for tx timestamp
2024-01-17T16:05:10.000 controller-0 ptp4l: err [2484513.306] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-18T11:46:30.000 controller-0 ptp4l: err [2555393.497] ptp4l-legacy timed out while polling for tx timestamp
2024-01-18T11:46:30.000 controller-0 ptp4l: err [2555393.497] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-18T19:14:02.000 controller-0 ptp4l: err [2582245.603] ptp4l-legacy timed out while polling for tx timestamp
2024-01-18T19:14:02.000 controller-0 ptp4l: err [2582245.603] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
2024-01-18T19:14:36.000 controller-0 ptp4l: err [2582279.695] ptp4l-legacy timed out while polling for tx timestamp
2024-01-18T19:14:36.000 controller-0 ptp4l: err [2582279.695] ptp4l-legacy increasing tx_timestamp_timeout may correct this issue, but it is likely caused by a driver bug
[XXXXXX@controller-0 ~(keystone_admin)]$
```

### Breaking it down by day...
```log
[XXXXXX@controller-0 ~(keystone_admin)]$ awk '{print $1}' welktxef-d1372466-007_soak-test-ptpl4-sync-log.txt |awk -FT '{print $1}'|sort -u > sort.lst
[XXXXXX@controller-0 ~(keystone_admin)]$ cat sort.lst |while read day ; do
> echo ${day}
> grep -c ${day}T welktxef-d1372466-007_soak-test-ptpl4-sync-log.txt
> done
2023-12-11
6
2023-12-13
6
2023-12-14
12
2023-12-16
2
2023-12-17
2
2023-12-18
4
2023-12-19
16
2023-12-21
10
2023-12-22
2
2023-12-23
2
2023-12-29
4
2023-12-30
2
2024-01-04
4
2024-01-07
2
2024-01-08
4
2024-01-09
92
2024-01-10
2
2024-01-11
4
2024-01-12
4
2024-01-13
2
2024-01-14
4
2024-01-16
6
2024-01-17
14
2024-01-18
6
[XXXXXX@controller-0 ~(keystone_admin)]$
```

### History 

2023-12-11
6
2023-12-13
6
2023-12-14
12
2023-12-16
2
2023-12-17
2
2023-12-18
4
2023-12-19
16
2023-12-21
10
2023-12-22
2
2023-12-23
2
2023-12-29
4
2023-12-30
2
2024-01-04
4
2024-01-07
2
2024-01-08
4
2024-01-09
92

### Soak period between 1/10/24 and 1/18/24

2024-01-10
2
2024-01-11
4
2024-01-12
4
2024-01-13
2
2024-01-14
4
2024-01-16
6
2024-01-17
14
2024-01-18
6

### Test appears to be success, we don't see an issue with PTPL4 timeouts, the LaaS team has not called with any issue.
### Test is success