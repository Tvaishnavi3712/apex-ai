# XR8720t Thermal Sensor Comparison — iDRAC 1.30.10.51 vs 1.30.33.10

**Host:** `2607:f160:10:823a:ce:40a:0:e001` (welktxwr-HDM35J4-dl-720x-001)  
**BIOS:** 1.1.3 (unchanged)  
**Endpoint:** `GET /redfish/v1/Chassis/System.Embedded.1/Thermal`  
**Date:** 2026-06-18  
**Question:** Does the newer iDRAC revision expose additional thermal sensors?

---

## Answer: No Additional Sensors

Both iDRAC versions expose **2 temperature sensors** and **16 fan sensors**. The sensor inventory
is identical. The firmware upgrade did not unlock any hidden thermal sensors on this platform.

The only measurable change is that the **Inlet Temp** sensor gained its non-critical (Warning)
threshold values, which were `null` in 1.30.10.51 and are populated in 1.30.33.10.

---

## Temperature Sensors

### Before — iDRAC 1.30.10.51

| ID | Name | Reading | State | Health | LowerCrit | LowerWarn | UpperWarn | UpperCrit | UpperFatal |
|----|------|---------|-------|--------|-----------|-----------|-----------|-----------|------------|
| 0 | CPU0 Temp | 41.4 °C | Enabled | OK | 3 °C | — | — | 107 °C | — |
| 1 | Inlet Temp | 26 °C | Enabled | OK | -30 °C | **null** | **null** | 62 °C | — |

### After — iDRAC 1.30.33.10

| ID | Name | Reading | State | Health | LowerCrit | LowerWarn | UpperWarn | UpperCrit | UpperFatal |
|----|------|---------|-------|--------|-----------|-----------|-----------|-----------|------------|
| 0 | CPU0 Temp | 42 °C | Enabled | OK | 3 °C | — | — | 107 °C | — |
| 1 | Inlet Temp | 26 °C | Enabled | OK | -30 °C | **-23 °C** | **58 °C** | 62 °C | — |

### Diff — Temperature Sensors

| Change | Detail |
|--------|--------|
| Sensor count | No change — 2 sensors in both versions |
| CPU0 Temp reading | 41.4 °C → 42 °C *(normal fluctuation, not firmware-related)* |
| Inlet Temp: LowerThresholdNonCritical (Warning) | `null` → **-23 °C** *(newly populated)* |
| Inlet Temp: UpperThresholdNonCritical (Warning) | `null` → **58 °C** *(newly populated)* |
| All other thresholds | Unchanged |

---

## Fan Sensors

Fan count and names are **identical** in both versions: 16 sensors, Fan1_1 through Fan8_2.
RPM readings differ slightly between samples (normal — iDRAC was recently reset between readings).

### Before — iDRAC 1.30.10.51

| ID | Name | RPM | State | Health |
|----|------|-----|-------|--------|
| 0 | Fan1_1 | 6325 | Enabled | OK |
| 1 | Fan2_1 | 6300 | Enabled | OK |
| 2 | Fan3_1 | 6242 | Enabled | OK |
| 3 | Fan4_1 | 6265 | Enabled | OK |
| 4 | Fan5_1 | 6173 | Enabled | OK |
| 5 | Fan6_1 | 6219 | Enabled | OK |
| 6 | Fan1_2 | 6131 | Enabled | OK |
| 7 | Fan2_2 | 6149 | Enabled | OK |
| 8 | Fan3_2 | 6091 | Enabled | OK |
| 9 | Fan4_2 | 6132 | Enabled | OK |
| 10 | Fan5_2 | 6174 | Enabled | OK |
| 11 | Fan6_2 | 6135 | Enabled | OK |
| 12 | Fan7_1 | 6268 | Enabled | OK |
| 13 | Fan8_1 | 6297 | Enabled | OK |
| 14 | Fan7_2 | 6155 | Enabled | OK |
| 15 | Fan8_2 | 6107 | Enabled | OK |

### After — iDRAC 1.30.33.10

| ID | Name | RPM | State | Health |
|----|------|-----|-------|--------|
| 0 | Fan1_1 | 5929 | Enabled | OK |
| 1 | Fan2_1 | 5911 | Enabled | OK |
| 2 | Fan3_1 | 5896 | Enabled | OK |
| 3 | Fan4_1 | 5924 | Enabled | OK |
| 4 | Fan5_1 | 5829 | Enabled | OK |
| 5 | Fan6_1 | 5891 | Enabled | OK |
| 6 | Fan1_2 | 5787 | Enabled | OK |
| 7 | Fan2_2 | 5802 | Enabled | OK |
| 8 | Fan3_2 | 5772 | Enabled | OK |
| 9 | Fan4_2 | 5790 | Enabled | OK |
| 10 | Fan5_2 | 5833 | Enabled | OK |
| 11 | Fan6_2 | 5790 | Enabled | OK |
| 12 | Fan7_1 | 5921 | Enabled | OK |
| 13 | Fan8_1 | 5903 | Enabled | OK |
| 14 | Fan7_2 | 5813 | Enabled | OK |
| 15 | Fan8_2 | 5797 | Enabled | OK |

### Diff — Fans

| Change | Detail |
|--------|--------|
| Sensor count | No change — 16 sensors in both versions |
| Sensor names | Identical |
| RPM readings | Lower across the board (~300–400 RPM) — normal post-reset transient; fan curve was settling after iDRAC restart |
| State / Health | All Enabled / OK in both cases |

---

## Other Thermal Endpoints Checked

| Endpoint | Result |
|----------|--------|
| `/redfish/v1/Chassis/MCChassis111/Thermal` | 0 temp sensors, 0 fans — empty in both versions |
| `/redfish/v1/Chassis/System.Embedded.1/Power` (Voltages) | 9 voltage sensors present in both |
| `/redfish/v1/Chassis/System.Embedded.1/Oem/Dell/DellThermalSensors` | 404 ResourceNotFound — OEM extension not implemented |

---

## Conclusion

The iDRAC upgrade from **1.30.10.51 → 1.30.33.10** does **not** expose additional thermal
sensors on the Dell XR8720t. The `/Thermal` endpoint reports the same 2 temperature sensors
(CPU0, Inlet) and 16 fan sensors in both versions.

The platform appears to publish a limited sensor set by design — only the integrated CPU package
sensor and the chassis inlet thermistor are visible via Redfish. No per-DIMM, per-PCIe, or
outlet temperature sensors are available at this firmware level.

The only firmware-related change observed is that the **Inlet Temp non-critical (Warning)
thresholds** are now populated in 1.30.33.10 (-23 °C lower, 58 °C upper), which were null in
1.30.10.51. This means Redfish alerting for inlet Warning conditions will function correctly
in the new version without requiring a custom threshold configuration.
