---
platform: HPE ProLiant Compute EL140 Gen12
ilo_version: 1.20.00
bmc_ip: 2607:f160:10:90bf:ce:40a:0:e002
ilo_hostname: ILO7CED3YR2ET
test_objective: "Test #2 — Install Verizon KEK and Wind River DB certs, set WorkloadProfile to vRAN, enable Secure Boot, verify boot"
date: 2026-06-10
result: PASS
jump_server: vcpe-jumpserver2
---

# Secure Boot Cert Install — 2607:f160:10:90bf:ce:40a:0:e002

## Result: PASS

All objectives completed successfully. Verizon KEK CA 2026 installed in KEK database, Wind River Systems signing cert installed in DB database, WorkloadProfile set to vRAN, Secure Boot enabled and active.

---

## Pre-Installation State

```
curl -gsk -u <USER>:<PASS> https://[2607:f160:10:90bf:ce:40a:0:e002]/redfish/v1/Systems/1/SecureBoot/SecureBootDatabases/KEK/Certificates/
curl -gsk -u <USER>:<PASS> https://[2607:f160:10:90bf:ce:40a:0:e002]/redfish/v1/Systems/1/SecureBoot/SecureBootDatabases/db/Certificates/
curl -gsk -u <USER>:<PASS> https://[2607:f160:10:90bf:ce:40a:0:e002]/redfish/v1/Systems/1/Bios/
```

| Database | Pre-Install Count | Members |
|----------|------------------|---------|
| KEK | 3 | /1/ /2/ /3/ |
| DB | 8 | /1/ /2/ /3/ /4/ /5/ /6/ /7/ /8/ |

**WorkloadProfile (before):** `GeneralPowerEfficientCompute`
**Secure Boot (before):** not checked (changed as part of this procedure)

---

## Step 1 — Install Verizon KEK Certificate

```bash
ssh vcpe-jumpserver2 'curl -gsk -u <USER>:<PASS> \
  -H "Content-Type: application/json" \
  -X POST --data "@vz-kek.json" \
  https://[2607:f160:10:90bf:ce:40a:0:e002]/redfish/v1/Systems/1/SecureBoot/SecureBootDatabases/KEK/Certificates/'
```

**Response:** iLO Task 1 created — `TaskState: New`

```json
{
  "@odata.id": "/redfish/v1/TaskService/Tasks/1/",
  "Id": "1",
  "TaskState": "New",
  "StartTime": "2026-06-10T21:40:51Z",
  "TargetUri": "/redfish/v1/Systems/1/SecureBoot/SecureBootDatabases/KEK/Certificates/"
}
```

---

## Step 2 — Install Wind River DB Certificate

```bash
ssh vcpe-jumpserver2 'curl -gsk -u <USER>:<PASS> \
  -H "Content-Type: application/json" \
  -X POST --data "@wr-db.json" \
  https://[2607:f160:10:90bf:ce:40a:0:e002]/redfish/v1/Systems/1/SecureBoot/SecureBootDatabases/DB/Certificates/'
```

**Response:** iLO Task 2 created — `TaskState: New`

```json
{
  "@odata.id": "/redfish/v1/TaskService/Tasks/2/",
  "Id": "2",
  "TaskState": "New",
  "StartTime": "2026-06-10T21:40:53Z",
  "TargetUri": "/redfish/v1/Systems/1/SecureBoot/SecureBootDatabases/DB/Certificates/"
}
```

> Both cert tasks are queued as pending — they will be committed on next BIOS POST.

---

## Step 3 — Set WorkloadProfile to vRAN

```bash
ssh vcpe-jumpserver2 'curl -gsk -u <USER>:<PASS> \
  -H "Content-Type: application/json" \
  -X PATCH --data "{\"Attributes\":{\"WorkloadProfile\":\"vRAN\"}}" \
  https://[2607:f160:10:90bf:ce:40a:0:e002]/redfish/v1/Systems/1/Bios/Settings'
```

**Response:** `iLO.2.39.SystemResetRequired` — pending reboot

---

## Step 4 — Enable Secure Boot

```bash
ssh vcpe-jumpserver2 'curl -gsk -u <USER>:<PASS> \
  -H "Content-Type: application/json" \
  -X PATCH --data "{\"SecureBootEnable\":true}" \
  https://[2607:f160:10:90bf:ce:40a:0:e002]/redfish/v1/Systems/1/SecureBoot/'
```

**Response:** `iLO.2.39.SystemResetRequired` — pending reboot

---

## Step 5 — Reboot (Apply All Pending Changes)

```bash
ssh vcpe-jumpserver2 'curl -gsk -u <USER>:<PASS> \
  -H "Content-Type: application/json" \
  -X POST --data "{\"ResetType\":\"ForceRestart\"}" \
  https://[2607:f160:10:90bf:ce:40a:0:e002]/redfish/v1/Systems/1/Actions/ComputerSystem.Reset'
```

**Response:** `Base.1.18.Success`

### Boot Sequence

| Time | PostState | Notes |
|------|-----------|-------|
| 14:41:52 | InPost | BIOS memory init |
| 14:43:24 | InPostDiscoveryStart | Hardware enumeration |
| 14:45:01 | PowerOff | Expected — BIOS cold boot cycle to apply WorkloadProfile change |
| 14:45:51 | Reset | Cold boot initiated |
| 14:46:33 | InPost | Second POST cycle |
| 14:47:23 | InPostDiscoveryStart | Hardware enumeration |
| 14:48:55 | FinishedPost | POST complete |

> **Note on PowerOff:** The BIOS performed an automatic cold boot cycle (warm restart → PowerOff → On) to apply the WorkloadProfile change. This is expected HPE behavior when WorkloadProfile is modified — the BIOS requires a full power cycle to reconfigure CPU/memory topology for the new profile. A second `ResetType: On` was issued to complete the cycle.

---

## Post-Install Verification

### Secure Boot State

```bash
ssh vcpe-jumpserver2 'curl -gsk -u <USER>:<PASS> \
  https://[2607:f160:10:90bf:ce:40a:0:e002]/redfish/v1/Systems/1/SecureBoot/'
```

| Field | Value | Expected | Result |
|-------|-------|----------|--------|
| SecureBootEnable | `true` | true | PASS |
| SecureBootCurrentBoot | `Enabled` | Enabled | PASS |
| SecureBootMode | `UserMode` | UserMode | PASS |

---

### WorkloadProfile

```bash
ssh vcpe-jumpserver2 'curl -gsk -u <USER>:<PASS> \
  https://[2607:f160:10:90bf:ce:40a:0:e002]/redfish/v1/Systems/1/Bios/'
```

| Field | Value | Expected | Result |
|-------|-------|----------|--------|
| WorkloadProfile | `vRAN` | vRAN | PASS |

---

### KEK Database — `KEK/Certificates/4/`

```bash
ssh vcpe-jumpserver2 'curl -gsk -u <USER>:<PASS> \
  https://[2607:f160:10:90bf:ce:40a:0:e002]/redfish/v1/Systems/1/SecureBoot/SecureBootDatabases/KEK/Certificates/4/'
```

```json
{
  "@odata.id": "/redfish/v1/Systems/1/SecureBoot/SecureBootDatabases/KEK/Certificates/4/",
  "Id": "4",
  "Name": "Verizon KEK CA 2026",
  "CertificateType": "PEM",
  "CertificateUsageTypes": ["BIOS"],
  "Issuer": { "CommonName": "Verizon KEK CA 2026", "Organization": "Verizon Corporation", "Country": "US" },
  "Subject": { "CommonName": "Verizon KEK CA 2026", "Organization": "Verizon Corporation", "Country": "US" },
  "ValidNotBefore": "2026-05-11T03:51:55Z",
  "ValidNotAfter": "2036-05-08T03:51:55Z",
  "UefiSignatureOwner": "00000000-0000-0000-0000-000000000000"
}
```

**KEK count:** 3 → **4** | **Result: PASS**

---

### DB Database — `db/Certificates/9/`

```bash
ssh vcpe-jumpserver2 'curl -gsk -u <USER>:<PASS> \
  https://[2607:f160:10:90bf:ce:40a:0:e002]/redfish/v1/Systems/1/SecureBoot/SecureBootDatabases/db/Certificates/9/'
```

```json
{
  "@odata.id": "/redfish/v1/Systems/1/SecureBoot/SecureBootDatabases/db/Certificates/9/",
  "Id": "9",
  "Name": "",
  "CertificateType": "PEM",
  "CertificateUsageTypes": ["BIOS"],
  "Issuer": { "Organization": "Wind River Systems, Inc.", "City": "Ottawa", "State": "Ontario", "Country": "CA" },
  "Subject": { "Organization": "Wind River Systems, Inc.", "City": "Ottawa", "State": "Ontario", "Country": "CA" },
  "ValidNotBefore": "2025-03-18T17:11:22Z",
  "ValidNotAfter": "2045-03-13T17:11:22Z",
  "UefiSignatureOwner": "00000000-0000-0000-0000-000000000000"
}
```

**DB count:** 8 → **9** | **Result: PASS**

---

### System Health

| Field | Value | Result |
|-------|-------|--------|
| PowerState | On | PASS |
| PostState | FinishedPost | PASS |
| Health | OK | PASS |

---

## Summary

| Step | Action | Result |
|------|--------|--------|
| Pre-check | KEK: 3, DB: 8, WorkloadProfile: GeneralPowerEfficientCompute | Baseline confirmed |
| Install KEK | POST `vz-kek.json` → KEK/Certificates/ | Task 1 queued |
| Install DB | POST `wr-db.json` → DB/Certificates/ | Task 2 queued |
| WorkloadProfile | PATCH `vRAN` → Bios/Settings | Pending reboot |
| Secure Boot | PATCH `SecureBootEnable: true` → SecureBoot/ | Pending reboot |
| Reboot | ForceRestart | Success (cold boot cycle executed by BIOS) |
| KEK/4 verify | Verizon KEK CA 2026 — valid 2026-05-11 → 2036-05-08 | PASS |
| db/9 verify | Wind River Systems, Inc. — valid 2025-03-18 → 2045-03-13 | PASS |
| WorkloadProfile verify | vRAN | PASS |
| Secure Boot verify | SecureBootCurrentBoot: Enabled, SecureBootMode: UserMode | PASS |
| System health | PowerState: On, PostState: FinishedPost, Health: OK | PASS |

**Overall: PASS**
