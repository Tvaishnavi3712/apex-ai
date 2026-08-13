# HPE EL140 Gen12 — Test Campaign Summary
# Platform: HPE ProLiant Compute EL140 Gen12
# BMC Firmware: iLO 7 v1.20.00 | BIOS: v1.30
# BMC IP: 2607:f160:10:90bf:ce:40a:0:e002
# Date: 2026-06-10
# Test Cases: PROPOSED-20 through PROPOSED-30
# Replaces Blocked: MEAKV-1750, MEAKV-1793

---

## Campaign Overview

Starting from a set of blocked MEAKV tickets (MEAKV-1750/1793) covering the HPE EL140 Gen12
(iLO 7, BIOS v1.30) as a new server type unsupported by the existing BMC playbook, we designed
and executed a ten-test Redfish certification campaign against a live lab unit at
`2607:f160:10:90bf:ce:40a:0:e002`. Tests PROPOSED-20 through PROPOSED-28 covered the full
provisioning sequence — user account management, NTP, DNS, hostname, syslog, Redfish event
subscriptions, NIC/MAC discovery, and BIOS WorkloadProfile — all executed via SSH proxy through
the jump server and verified against iLO 7 Redfish responses. Rather than using placeholder
values, we pulled real production reference values (NTP, DNS, syslog) directly from a live
e930t (iLO6) unit in the same lab, which also yielded a secondary finding: several iLO7
behavioral deviations (DateTime NTP endpoint, RegistryPrefixes for events, StaticNameServers
array limit) turned out to be present on iLO6 as well, broadening the scope of required
playbook changes beyond just the EL140. All nine result files were written to this results
directory and served as structured input to PROPOSED-29, which cross-referenced the results
against the live playbook at `vcpe-jumpserver2:/home/patchja/bmc_playbook_EL140` to produce a
formal change specification identifying seven required Ansible changes. In parallel, PROPOSED-30
was created as a new HPE-only test case covering the Secure Boot certificate installation
procedure that was validated earlier in the lab. Finally, after reading the HPE EL140 GNR-D
Installation Guideline (v1.01, April 2026), five additional gaps were identified — most notably
that the `Chassis/1/NetworkAdapters` endpoint (not `Systems/1`) exposes the correctly named
E830 and E825 NICs, and that the NEBS inlet ambient caution threshold (required to be 62°C) is
currently unset (`null`) on the EL140 — both of which need new test cases and playbook coverage.

---

## Test Case Change Matrix

| Test Case | Title | TC File | Result File | What Changed | Key Finding |
|---|---|---|---|---|---|
| PROPOSED-20 | BMC User Account Create | No change | Created | — | iLO7 account IDs are non-sequential large integers (65536+); `add_user_account.py` already handles this correctly via dynamic `@odata.id` enumeration |
| PROPOSED-21 | BMC Password Change | No change | Created | — | Password PATCH and login verification pass on iLO7 unchanged |
| PROPOSED-22 | BMC Account Delete | No change | Created | — | DELETE + 404 verification pass on iLO7 unchanged |
| PROPOSED-23 | NTP Configuration | **Updated** | Created / Updated | Session Variables updated with real lab NTP servers (`2607:f160:10:9200::a` / `::b` from e930t); vendor procedure updated for E930t (iLO6) and EL140 to confirm DateTime endpoint | NTP lives at `/redfish/v1/Managers/1/DateTime` on **both** iLO6 (e930t) and iLO7 — not in NetworkProtocol; `set_ilo_sntp_servers.py` already targets the correct endpoint; no playbook change needed |
| PROPOSED-24 | DNS Configuration | **Updated** | **Rewritten** PASS → PASS WITH DEVIATION | Session Variables updated with real lab DNS servers; EL140 vendor procedure updated with 3-entry IPv6 array limit; result rewritten after actually executing the PATCH (was originally filed as PASS without the PATCH having run) | `StaticNameServers(IPv6)` on iLO7 bounded 1..3; 6-entry array returns HTTP 400 `ArrayPropertyOutOfBound`; correct PATCH body: `["DNS1","DNS2","::"]` |
| PROPOSED-25 | BMC Hostname | No change | Created | — | Hostname PATCH must target `NetworkProtocol.HostName` on iLO7 (not `EthernetInterfaces/1.Oem.Hpe.HostName`); returns `ResetRequired` but value immediately readable; current lab baseline hostname retained |
| PROPOSED-26 | Syslog Configuration | **Updated** | Created | Session Variables updated with real lab syslog server (`vcp-faredge-syslog.mon.vzwops.com:5140`); real PATCH executed and verified | OEM syslog path `Oem.Hpe.RemoteSyslogEnabled/Server/Port` in NetworkProtocol works identically on iLO6 and iLO7; `configure_syslog.py` needs no change |
| PROPOSED-27 | Redfish Event Subscription | **Updated** | Created | HPE vendor procedure updated: `RegistryPrefixes` confirmed on **both** iLO6 (e930t) and iLO7 (EL140); iLO5 marked unconfirmed; available prefixes documented | `EventTypesForSubscription` absent on all current HPE iLO; `EventTypes`-based POST fails; `RegistryPrefixes` required — broadens the playbook `subscribe-redfish-events` fix from EL140-only to all HPE iLO platforms |
| PROPOSED-28 | NIC/MAC Discovery & BIOS Config | No change | Created | — | 24 EthernetInterface `Name` fields all empty on iLO7; interface IDs non-sequential (range 5–2480); OAM NIC identified by `LinkStatus=LinkUp`; `Chassis/1/NetworkAdapters` (not tested in this run) has correctly named E830/E825 entries — proper fix path for mac-discover |
| PROPOSED-29 | Playbook Gap Analysis | **Major rewrite** | Executed → change spec | Added Step 0 (existing results inventory); Step 1 rewritten as USER ACTION REQUIRED with 3 git clone options; Step 3 reads from existing result files rather than re-running tests; EL140/iLO7 vendor section updated with all confirmed deviations | Produced `playbook-change-spec-HPE-EL140-Gen12-2026-06-10.md`: 7 CHANGE REQUIRED, 7 NO CHANGE, 1 VERIFY REQUIRED across 15 role files and Python scripts |
| PROPOSED-30 | Secure Boot Cert Install | **New** | Not yet run | New test case created (HPE iLO7 only); 9-step procedure with cold boot cycle | POST KEK + DB certs → set `WorkloadProfile=vRAN` → enable SecureBoot → ForceRestart → handle cold boot (ForceRestart → PowerOff → manual On) → poll `FinishedPost` (~8–10 min) → verify cert count baseline+1 |

---

## Result Files Produced

| File | Type | Outcome |
|---|---|---|
| `PROPOSED-20-result.md` | Test result | PASS |
| `PROPOSED-21-result.md` | Test result | PASS |
| `PROPOSED-22-result.md` | Test result | PASS |
| `PROPOSED-23-result.md` | Test result | PASS WITH DEVIATION (DateTime endpoint) |
| `PROPOSED-24-result.md` | Test result | PASS WITH DEVIATION (StaticNameServers array limit) |
| `PROPOSED-25-result.md` | Test result | PASS WITH DEVIATION (NetworkProtocol path) |
| `PROPOSED-26-result.md` | Test result | PASS |
| `PROPOSED-27-result.md` | Test result | PASS WITH DEVIATION (RegistryPrefixes required) |
| `PROPOSED-28-result.md` | Test result | PASS WITH DEVIATION (Names empty, non-sequential IDs) |
| `playbook-change-spec-HPE-EL140-Gen12-2026-06-10.md` | Change specification | 7 changes required |

---

## Playbook Change Specification Summary

Output: `playbook-change-spec-HPE-EL140-Gen12-2026-06-10.md`
Playbook: commit `5ff15f7028` / tag `v1.0-66548` / branch `master`
Location: `vcpe-jumpserver2:/home/patchja/bmc_playbook_EL140`

| # | File | Assessment | Change |
|---|---|---|---|
| 1 | `group_vars/HPE` | CHANGE REQUIRED | Add `bios_attribute_value_workload_profile_vRAN: vRAN` |
| 2 | `check_model` | CHANGE REQUIRED | Add `le1140` hostname guard + `set_fact server_type: HPE-GEN12-el140` when `EL140` in model |
| 3 | `bios-config` | CHANGE REQUIRED | Guard existing blocks `when: server_type != "HPE-GEN12-el140"`; add EL140 block for `WorkloadProfile: vRAN` only |
| 4 | `mac-discover` | CHANGE REQUIRED | Add EL140 block using `Chassis/1/NetworkAdapters` E830 model match (not `LinkStatus=LinkUp` workaround) |
| 5 | `ilo-hostname` | CHANGE REQUIRED | Guard existing task; add EL140 task targeting `NetworkProtocol.HostName` |
| 6 | `subscribe-redfish-events` | CHANGE REQUIRED | Replace `EventTypes` with `RegistryPrefixes` — applies to all HPE iLO (iLO6 + iLO7) |
| 7 | `ilo-reset` | CHANGE RECOMMENDED | Increase pause from 3 to 4 minutes for iLO7 (~133s observed) |
| — | `configure_dns.py` | VERIFY REQUIRED | `Oem.Hpe.IPv6.DNSServers` path via resource_directory — needs iLO7 confirmation |
| — | `set_ilo_sntp_servers.py` | NO CHANGE | Already targets DateTime endpoint with StaticNTPServers |
| — | `disable_dhcp_ntp.py` | NO CHANGE | Correct EthernetInterfaces/1 OEM DHCP path |
| — | `configure_syslog.py` | NO CHANGE | OEM RemoteSyslog path identical on iLO7 |
| — | `account-create` | NO CHANGE | Dynamic `@odata.id` enumeration handles non-sequential iLO7 IDs |
| — | `system-off` / `system-on` | NO CHANGE | Reset paths identical on iLO7 |
| — | `syslog-enable` / `syslog-disable` | NO CHANGE | OEM NetworkProtocol syslog path unchanged |
| — | `dhcp-disable` | NO CHANGE | Domain-name disable path unchanged |

---

## Additional Gaps Identified from Installation Guideline (HPE EL140 GNR-D v1.01, April 2026)

The following items were identified after reviewing the HPE installation guideline and confirmed
against the live EL140. No test cases or playbook roles currently cover these.

| Gap | Endpoint | Current State on EL140 | Action Needed |
|---|---|---|---|
| `Chassis/1/NetworkAdapters` NIC verification (E830/E825 by model name) | `GET /redfish/v1/Chassis/1/NetworkAdapters/{id}` | 4 adapters present: 2x E825-C (DE008000, DE009000), 2x E830-XXVDA8F (DE07A000, DE07B000) | Update PROPOSED-28; update playbook CHANGE 4 to use model-name match |
| NEBS inlet ambient caution threshold (guideline: 62°C) | `GET /redfish/v1/Chassis/1/Thermal` → `01-Inlet Ambient.UpperThresholdCaution` | `null` (not set; critical=42°C) | New PROPOSED-31; investigate whether vRAN WorkloadProfile or separate PATCH sets this |
| iLO Advanced license pre-flight verification | `GET /redfish/v1/Managers/1` → `Oem.Hpe.License` | `LicenseType: Perpetual / iLO Advanced` — confirmed present | Add as pre-flight check to PROPOSED-20 or standalone PROPOSED-31 |
| Full DHCPv4/v6 disable (not just `UseDomainName`) | `GET /redfish/v1/Managers/1/EthernetInterfaces/1` | All DHCP flags false / DHCPv6 Disabled — manually set at install | `dhcp-disable` role only patches `UseDomainName`; no verification of full state |
| `Systems/1.HostName` + `Oem.Hpe.ServerFQDN` writable on iLO7 | `PATCH /redfish/v1/Systems/1` | Not tested | `host-name` role untested on iLO7; PROPOSED-25 only covers `NetworkProtocol.HostName` |

---

## Lab Reference Values Used

| Setting | Value | Source |
|---|---|---|
| NTP Server 1 | `2607:f160:10:9200::a` | e930t (iLO6) production config |
| NTP Server 2 | `2607:f160:10:9200::b` | e930t (iLO6) production config |
| DNS Server 1 | `2607:F160:10:4409:CE:103:0:5` | e930t (iLO6) production config |
| DNS Server 2 | `2607:F160:10:4409:CE:103:0:6` | e930t (iLO6) production config |
| Syslog Server | `vcp-faredge-syslog.mon.vzwops.com` | e930t (iLO6) production config |
| Syslog Port | `5140` | e930t (iLO6) production config |
| IPv6 Default Gateway | `2607:f160:10:90bf:ce:400::` | EL140 lab assignment |
| iLO Static IPv6 | `2607:f160:10:90bf:ce:40a:0:e002/64` | EL140 lab assignment |
| OAM NIC MAC | `10:2e:00:03:26:e0` | EL140 EthernetInterfaces/5 (LinkUp) |
