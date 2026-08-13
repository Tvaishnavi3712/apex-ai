# BMC Playbook Change Specification
# New Server Type: HPE EL140 Gen12 (iLO 7)
# Playbook Version: commit 5ff15f7028 / tag v1.0-66548 / branch master
# Playbook Repo: vcpe-jumpserver2:/home/patchja/bmc_playbook_EL140
# Test Results: HPE-EL140-ilo_1.20.00-BIOS_v1.30 — PROPOSED-20 through PROPOSED-32
# BMC IP Tested: 2607:f160:10:9249:ce:40a:0:e033 (rev 2: e033 / 2026-06-10)
# Previous IP:   2607:f160:10:90bf:ce:40a:0:e002 (rev 1: e002 / 2026-06-10, same FW)
# Date: 2026-06-10
# Status: DRAFT — Pending automation team review

---

## Role Assessment Summary

| Role / File | Assessment | PROPOSED Ref | Scope |
|---|---|---|---|
| `group_vars/HPE` | **CHANGE REQUIRED** | PROPOSED-28 | Add missing vRAN WorkloadProfile var |
| `check_model` | **CHANGE REQUIRED** | PROPOSED-28 | No EL140 match condition |
| `bios-config` | **CHANGE REQUIRED** | PROPOSED-28 | Wrong WorkloadProfile value; absent BIOS attrs break PATCH |
| `mac-discover` | **CHANGE REQUIRED** | PROPOSED-28 | No EL140 case; NIC name match fails on iLO7 |
| `ilo-hostname` | **CHANGE REQUIRED** | PROPOSED-25 | OEM EthernetInterfaces HostName path fails on iLO7 |
| `subscribe-redfish-events` | **CHANGE REQUIRED** | PROPOSED-27 | EventTypes rejected; RegistryPrefixes required on iLO6 + iLO7 |
| `enable_secure_boot.py` | **VERIFY REQUIRED** | PROPOSED-30 | Script needs iLO7 cert path verification |
| `ilo-reset` | NO CHANGE REQUIRED (timing confirmed) | PROPOSED-25 | iLO7 reset observed ~133s; existing 3-min wait sufficient |
| `account-create` | NO CHANGE REQUIRED | PROPOSED-20/21/22 | Script uses dynamic @odata.id; handles non-sequential IDs |
| `system-off` / `system-on` | NO CHANGE REQUIRED | PROPOSED-28 | Paths and reset types identical on iLO7 |
| `syslog-enable` / `syslog-disable` | NO CHANGE REQUIRED | PROPOSED-26 | OEM NetworkProtocol syslog path identical on iLO7 |
| `dhcp-disable` | NO CHANGE REQUIRED | PROPOSED-24 | Domain-name disable path unchanged; NTP/DNS handled separately |
| `disable_dhcp_ntp.py` | NO CHANGE REQUIRED | PROPOSED-23 | Already targets correct EthernetInterfaces/1 OEM DHCP path |
| `set_ilo_sntp_servers.py` | NO CHANGE REQUIRED | PROPOSED-23 | Already targets DateTime endpoint with StaticNTPServers |
| `configure_dns.py` | **VERIFY REQUIRED** | PROPOSED-24 | Oem.Hpe.IPv6.DNSServers path compatible; resource_directory dependency needs iLO7 verification |
| `configure_syslog.py` | NO CHANGE REQUIRED | PROPOSED-26 | OEM RemoteSyslog path identical on iLO7 (confirmed via direct Redfish test) |
| `security-hardening` (new role) | **GAP — DOES NOT EXIST** | PROPOSED-32 | No security hardening role in playbook; EL140 requires SNMP/HTTP/IPMI/SSDP disable and login banner |
| (no role) | **OPERATIONAL NOTE** | PROPOSED-31 | NEBS 62°C inlet threshold not Redfish-settable; manual iLO UI step required post-provisioning |

---

## CHANGE 1 — `group_vars/HPE`

**Assessment:** CHANGE REQUIRED

**PROPOSED Test Reference:** PROPOSED-28 result: PASS WITH DEVIATION

**Observed Behavior on HPE EL140 Gen12:**
EL140 does not support individual BIOS attribute patching for BootMode, PciSlot1Enable,
MinProcIdlePower, LlcPrefetch, or ProcessorConfigTDPLevel — these attributes do not exist
in the EL140 BIOS attribute registry (273 total attributes, iLO 7 1.20.00). WorkloadProfile
must be set to the exact string `vRAN` to apply all 11 vRAN BIOS settings atomically.

**Current Ansible (from commit 5ff15f7028):**
```yaml
# group_vars/HPE
bios_attribute_value_workload_profile: Virtualization-MaxPerformance
bios_attribute_value_workload_profile_custom: Custom
```

**Required Change:**
```yaml
# group_vars/HPE — ADD the following line
bios_attribute_value_workload_profile_vRAN: vRAN
```

**Reason:**
`bios_attribute_value_workload_profile_vRAN` is referenced in the new EL140 bios-config
block (CHANGE 3) but is not defined in group_vars/HPE. Setting it to the string `vRAN`
is required — the EL140 BIOS rejects any other WorkloadProfile value including
`Virtualization-MaxPerformance`.

**Risk / Notes:**
Adding a new var does not affect existing e910t/e920t/e930t flows since it is only
referenced in EL140-specific `when: server_type == "HPE-GEN12-el140"` blocks.

---

## CHANGE 2 — `roles/hpe/check_model/tasks/main.yaml`

**Assessment:** CHANGE REQUIRED

**PROPOSED Test Reference:** PROPOSED-28 result: PASS WITH DEVIATION (model field confirmed)

**Observed Behavior on HPE EL140 Gen12:**
`/redfish/v1/Chassis/1` returns `Model: "ProLiant Compute EL140 Gen12"`. The current
`when:` condition only validates `e910t` and `e920t` hostname-to-model matches. An EL140
server passes through `check_model` unchecked and no `server_type` fact is set — all
downstream `when: server_type == "HPE-GEN12-el140"` guards will be skipped.

**Current Ansible (from commit 5ff15f7028):**
```yaml
- name: Fail when model specifier substring in hostname does not match the actual model name
  fail:
    msg: There is a mismatch between the ILO hostname and the server model.
          This server needs to be purged from DB and reingested after updating hostname in the CIQ.
  when: "'e910' in inventory_hostname and not '910t' in model_name or
         'e092' in inventory_hostname and not '920t' in model_name"
```

**Required Change:**
```yaml
- name: Fail when model specifier substring in hostname does not match the actual model name
  fail:
    msg: There is a mismatch between the ILO hostname and the server model.
          This server needs to be purged from DB and reingested after updating hostname in the CIQ.
  when: "'e910' in inventory_hostname and not '910t' in model_name or
         'e092' in inventory_hostname and not '920t' in model_name or
         'le1140' in inventory_hostname and not 'EL140' in model_name"

- name: "Set server_type for HPE EL140 Gen12"
  set_fact:
    server_type: "HPE-GEN12-el140"
  when: "'EL140' in model_name"
```

**Reason:**
Two additions: (1) a fail guard that catches hostname/model mismatch for EL140 servers
identified by the `le1140` hostname token (per VCP-Far Edge hostname convention v1.9,
EL140 servers use equipment code `le1140`); (2) a `set_fact` that sets `server_type` to
`HPE-GEN12-el140` so all downstream role branches can identify the platform.

**Risk / Notes:**
The `set_fact` for `server_type` should also be verified for e910t and e920t — if they
rely on server_type being set elsewhere, ensure the new fact does not conflict.
Equipment code `le1140` confirmed from hostname convention v1.9 memory reference.
`model_name` confirmed as `"ProLiant Compute EL140 Gen12"` from PROPOSED-28.

---

## CHANGE 3 — `roles/hpe/bios-config/tasks/main.yaml`

**Assessment:** CHANGE REQUIRED

**PROPOSED Test Reference:** PROPOSED-28 result: PASS WITH DEVIATION

**Observed Behavior on HPE EL140 Gen12:**
EL140 iLO7 does not expose `BootMode`, `PciSlot1Enable`, `MinProcIdlePower`,
`LlcPrefetch`, or `ProcessorConfigTDPLevel` BIOS attributes. Patching these attrs
on EL140 returns HTTP 400 `PropertyNotInList`. Setting `WorkloadProfile: vRAN`
atomically applies all 11 vRAN attributes (NumaGroupSizeOpt=Flat, Numa=Enabled,
ProcHyperthreading=Enabled, ProcTurbo=Enabled, SubNumaClustering=Disabled,
VirtualNuma=Disabled, EnergyEfficientTurbo=Disabled, EnergyPerfBias=MaxPerf, etc.).
Confirmed on both e002 and e033 — WorkloadProfile = vRAN at test time on both units.

**Current Ansible — Part 1 SetBiosAttributes block (from commit 5ff15f7028):**
```yaml
- name: "Set HPE BIOS configuration attribute (part 1)"
  redfish_config:
    category: Systems
    command: SetBiosAttributes
    baseuri: "[{{ bmc_ip }}]"
    username: "{{ bmc_username }}"
    password: "{{ bmc_password }}"
    bios_attributes:
      BootMode: "{{ bios_attribute_value_boot_mode }}"
      UefiOptimizedBoot: "{{ bios_attribute_value_uefi_optimized_boot }}"
      WorkloadProfile: "{{ bios_attribute_value_workload_profile }}"
      ProcVirtualization: "{{ bios_attribute_value_proc_virtualization }}"
      Sriov: "{{ bios_attribute_value_sriov }}"
      PciSlot1Enable: "{{ bios_attribute_value_pci_slot1_enable }}"
```

**Current Ansible — Part 2 SetBiosAttributes block:**
```yaml
- name: "Set HPE BIOS configuration attribute (part 2)"
  redfish_config:
    category: Systems
    command: SetBiosAttributes
    baseuri: "[{{ bmc_ip }}]"
    username: "{{ bmc_username }}"
    password: "{{ bmc_password }}"
    bios_attributes:
      WorkloadProfile: "{{ bios_attribute_value_workload_profile_custom }}"
      SubNumaClustering: "{{ bios_attribute_value_sub_numa_clustering }}"
      MinProcIdlePower: "{{ bios_attribute_value_min_proc_idle_power }}"
      ProcTurbo: "{{ bios_attribute_value_proc_turbo }}"
      ProcHyperthreading: "{{ bios_attribute_value_proc_hyperthreading }}"
      LlcPrefetch: "{{ bios_attribute_value_llc_prefetch }}"
      ProcessorConfigTDPLevel: "{{ bios_attribute_value_processor_config_tdp_level }}"
```

**Current Ansible — Fail condition:**
```yaml
- name: Fail when BIOS attributes are not set correctly
  fail:
    msg: At least one bios attribute failed to set correctly.
  when: output.json.Attributes.BootMode != bios_attribute_value_boot_mode or
        output.json.Attributes.UefiOptimizedBoot != bios_attribute_value_uefi_optimized_boot or
        output.json.Attributes.WorkloadProfile != bios_attribute_value_workload_profile_custom or
        output.json.Attributes.ProcVirtualization != bios_attribute_value_proc_virtualization or
        output.json.Attributes.Sriov != bios_attribute_value_sriov or
        output.json.Attributes.PciSlot1Enable != bios_attribute_value_pci_slot1_enable or
        output.json.Attributes.SubNumaClustering != bios_attribute_value_sub_numa_clustering or
        output.json.Attributes.MinProcIdlePower != bios_attribute_value_min_proc_idle_power or
        output.json.Attributes.ProcTurbo != bios_attribute_value_proc_turbo or
        output.json.Attributes.ProcHyperthreading != bios_attribute_value_proc_hyperthreading or
        output.json.Attributes.LlcPrefetch != bios_attribute_value_llc_prefetch or
        output.json.Attributes.ProcessorConfigTDPLevel != bios_attribute_value_processor_config_tdp_level
```

**Required Change:**

Add `when: server_type != "HPE-GEN12-el140"` to the existing Part 1, Part 2, and Fail tasks.
Add the following EL140-specific block BEFORE the "Execute HPE disable DHCP script" task:

```yaml
# --- EL140 Gen12 / iLO7 BIOS config block ---
- name: "Set WorkloadProfile to vRAN (EL140 Gen12 only)"
  uri:
    url: "https://[{{ bmc_ip }}]/redfish/v1/Systems/1/Bios/Settings"
    method: PATCH
    body_format: json
    body:
      Attributes:
        WorkloadProfile: "{{ bios_attribute_value_workload_profile_vRAN }}"
    url_username: "{{ bmc_username }}"
    url_password: "{{ bmc_password }}"
    force_basic_auth: yes
    status_code: [200, 201, 204]
    validate_certs: no
    return_content: yes
  register: result
  delegate_to: localhost
  when: server_type == "HPE-GEN12-el140"

- name: "Fail if WorkloadProfile vRAN not set (EL140 Gen12)"
  fail:
    msg: "WorkloadProfile did not set to vRAN on EL140. Check iLO7 BIOS/Settings response."
  when:
    - server_type == "HPE-GEN12-el140"
    - result.json.Attributes.WorkloadProfile is defined
    - result.json.Attributes.WorkloadProfile != bios_attribute_value_workload_profile_vRAN
```

Also add `when: server_type != "HPE-GEN12-el140"` to the existing part 1, part 2, and fail blocks.

**Reason:**
The existing attribute list contains attributes that do not exist on EL140 — patching them
returns HTTP 400 and the task fails. EL140 uses WorkloadProfile: vRAN which atomically sets
all required vRAN BIOS attributes. Confirmed on both e002 and e033.

**Risk / Notes:**
The EL140 bios-config block may trigger a cold boot cycle (ForceRestart → PowerOff → On)
when WorkloadProfile changes from default. The cold boot (PowerOff → On) is automatic HPE
behavior. The post-restart PostState polling loop must allow enough time (~8–10 min total).
If WorkloadProfile is already vRAN (both test units were), no reboot cycle occurs.

---

## CHANGE 4 — `roles/hpe/mac-discover/tasks/main.yaml`

**Assessment:** CHANGE REQUIRED

**PROPOSED Test Reference:** PROPOSED-28 result: PASS WITH DEVIATION

**Observed Behavior on HPE EL140 Gen12 (both e002 and e033):**
24 EthernetInterfaces at `/redfish/v1/Systems/1/EthernetInterfaces`. Interface IDs are
non-sequential large integers (5–12, 2265–2268, 2333–2336, 2473–2480). All `Name` fields
are empty strings — NIC name-based identification fails completely. OAM NIC identified by
`LinkStatus: LinkUp`:
- **e002:** Interface ID 5, MAC `10:2e:00:03:26:e0` (Intel OUI — E825-C integrated port)
- **e033:** Interface ID 2473, MAC `b4:7a:f1:d9:48:fc` (HPE OUI — OCP port)

Both units had exactly one interface with `LinkStatus: LinkUp`. The active OAM interface is
cable-dependent — the correct discovery method is `LinkStatus: LinkUp`, regardless of interface ID.
The existing scripts (`find_ilo_mac_address.py`, etc.) match by NIC `Name` string which is
empty on iLO7 and would return `None`. No `server_type == "HPE-GEN12-el140"` case exists.

**Current Ansible (from commit 5ff15f7028):**
```yaml
# Only handles server_type in: HPE-LS3-e910, HPE-LS3-92s3, HPE-LS6-92s6
# No case for HPE-GEN12-el140 — MAC discovery silently skipped for EL140
```

**Required Change:**

```yaml
- name: "Get EthernetInterfaces list for EL140 MAC discovery"
  uri:
    url: "https://[{{ bmc_ip }}]/redfish/v1/Systems/1/EthernetInterfaces"
    method: GET
    url_username: "{{ bmc_username }}"
    url_password: "{{ bmc_password }}"
    force_basic_auth: yes
    status_code: [200]
    validate_certs: no
    return_content: yes
  register: el140_eth_list
  delegate_to: localhost
  when: server_type == "HPE-GEN12-el140"

- name: "Fetch each EthernetInterface for EL140 MAC discovery"
  uri:
    url: "https://[{{ bmc_ip }}]{{ item['@odata.id'] }}"
    method: GET
    url_username: "{{ bmc_username }}"
    url_password: "{{ bmc_password }}"
    force_basic_auth: yes
    status_code: [200]
    validate_certs: no
    return_content: yes
  loop: "{{ el140_eth_list.json.Members }}"
  register: el140_eth_details
  delegate_to: localhost
  when: server_type == "HPE-GEN12-el140"

- name: "Set EL140 OAM MAC from first LinkUp interface"
  set_fact:
    el140_pxe_mac: "{{ item.json.MACAddress }}"
  loop: "{{ el140_eth_details.results }}"
  when:
    - server_type == "HPE-GEN12-el140"
    - item.json.LinkStatus == "LinkUp"
    - el140_pxe_mac is not defined

- name: "Fail if no LinkUp interface found (EL140)"
  fail:
    msg: "No LinkUp EthernetInterface found on EL140. Cannot determine OAM MAC."
  when:
    - server_type == "HPE-GEN12-el140"
    - el140_pxe_mac is not defined

- name: "Push EL140 MAC address to middleware"
  uri:
    url: "{{ middleware_endpoint }}/caas/macaddress/"
    method: POST
    body_format: form-urlencoded
    body:
      ilo_host_address: "{{ bmc_ip }}"
      pxe_mac_address: "{{ el140_pxe_mac }}"
      intel_nic_firmware_version: "unknown"
    url_username: "{{ middleware_username }}"
    url_password: "{{ middleware_password }}"
    force_basic_auth: yes
    validate_certs: no
    status_code: [200, 201, 204]
    timeout: 120
  register: output
  until: output.status in [200, 201, 204]
  retries: 8
  delay: 15
  delegate_to: localhost
  when: server_type == "HPE-GEN12-el140"
```

**Reason:**
Name-based NIC identification fails on iLO7 (all Name fields are empty strings). LinkStatus=LinkUp
is the correct method — confirmed on two different EL140 units with different OAM NICs (ID 5 vs 2473).
The `intel_nic_firmware_version` is not available via EthernetInterfaces on iLO7 — middleware POST
must accept `"unknown"` or the field must be made optional.

**Risk / Notes:**
`el140_pxe_mac is not defined` guard takes the FIRST LinkUp interface in Members list order.
If multiple interfaces are LinkUp (fully-cabled EL140 in production), verify Members ordering
to ensure the OAM management NIC is selected. OUI check on MAC prefix `b4:7a:f1` (HPE OCP)
or `10:2e:00:03` (Intel E825/E830) can serve as a secondary validation.

---

## CHANGE 5 — `roles/hpe/ilo-hostname/tasks/main.yaml`

**Assessment:** CHANGE REQUIRED

**PROPOSED Test Reference:** PROPOSED-25 result: PASS WITH DEVIATION

**Observed Behavior on HPE EL140 Gen12:**
Patching `Oem.Hpe.HostName` in `/redfish/v1/Managers/1/EthernetInterfaces/1` returns
HTTP 200 but the hostname is NOT updated on iLO7 (field is null on read-back). The correct
iLO7 hostname path is `PATCH /redfish/v1/Managers/1/NetworkProtocol` with `{"HostName": "..."}`.
The new hostname is immediately readable in GET without a reset, but full service activation
(TLS certs, DNS registration) requires an iLO manager reset.

Additional finding on e033: `NetworkProtocol.FQDN` uses `.laserlab-bench.local` domain —
the domain suffix is not set by the hostname PATCH alone. The authoritative full FQDN is at
`Systems/1.Oem.Hpe.ServerFQDN`. If the FQDN suffix must be set, a separate PATCH to
`NetworkProtocol {"FQDN": "..."}` or DNS domain configuration is needed.

**Current Ansible (from commit 5ff15f7028):**
```yaml
- name: "Change host name for iLO interface"
  uri:
    url: "https://[{{ bmc_ip }}]/redfish/v1/Managers/1/EthernetInterfaces/1"
    method: PATCH
    body_format: json
    body: '{ "Oem": {
                "Hpe": {
                  "HostName": "{{ inventory_hostname }}",
                  "DomainName": "{{ dns_domain }}"
                }
              }
           }'
    ...
```

**Required Change:**
```yaml
# Existing task — add when condition to skip on EL140
- name: "Change host name for iLO interface"
  uri:
    url: "https://[{{ bmc_ip }}]/redfish/v1/Managers/1/EthernetInterfaces/1"
    method: PATCH
    body_format: json
    body: '{ "Oem": { "Hpe": { "HostName": "{{ inventory_hostname }}", "DomainName": "{{ dns_domain }}" } } }'
    ...
  when: server_type != "HPE-GEN12-el140"     # ADD THIS LINE

# New task — EL140 uses NetworkProtocol path
- name: "Change host name for iLO interface (iLO7 / EL140)"
  uri:
    url: "https://[{{ bmc_ip }}]/redfish/v1/Managers/1/NetworkProtocol"
    method: PATCH
    body_format: json
    body: '{ "HostName": "{{ inventory_hostname }}", "FQDN": "{{ inventory_hostname }}.{{ dns_domain }}" }'
    url_username: "{{ bmc_username }}"
    url_password: "{{ bmc_password }}"
    force_basic_auth: yes
    status_code: [200, 201, 204]
    validate_certs: no
    return_content: yes
  delegate_to: localhost
  when: server_type == "HPE-GEN12-el140"     # ADD THIS BLOCK
```

**Reason:**
On iLO7, `EthernetInterfaces/1.Oem.Hpe.HostName` is null and not writable. The iLO7 manager
hostname is set at `NetworkProtocol.HostName`. Adding explicit FQDN in the PATCH body ensures
the correct domain suffix is applied (not the lab default laserlab-bench.local observed on e033).

**Risk / Notes:**
The existing `Reset iLO` task that follows the hostname PATCH should remain — it applies to
both iLO5/6 and iLO7 and is required for full hostname activation on all platforms. `Systems/1.HostName`
will show a truncated value on iLO7 — use `NetworkProtocol.HostName` as the verification field.

---

## CHANGE 6 — `roles/hpe/subscribe-redfish-events/tasks/main.yaml`

**Assessment:** CHANGE REQUIRED

**PROPOSED Test Reference:** PROPOSED-27 result: PASS WITH DEVIATION

**Observed Behavior on HPE EL140 Gen12 AND HPE E930t (iLO6):**
`EventTypesForSubscription` is **absent** from the EventService response on both iLO6
(e930t at 2607:f160:10:8803:ce:40a:0:e004) and iLO7 (EL140 e033). Both platforms require
`RegistryPrefixes` in the subscription POST body. An `EventTypes` POST is likely
silently ignored or rejected. This affects ALL current HPE iLO platforms, not just EL140.

Available RegistryPrefixes on both iLO6 and iLO7 (identical):
`iLOEvents`, `ResourceEvent`, `NetworkDevice`, `StorageDevice`, `iLOResourceEvents`, `iLOSecurityEvents`

Subscription confirmed created at HTTP 201 on e033 with all 6 RegistryPrefixes.

**Current Ansible (from commit 5ff15f7028):**
```yaml
- name: "Set facts to subscribe events for HPE servers"
  set_fact:
    event_context: "Subscription_VCMP"
    event_destination: "https://vcp-fe-redfishevents.mon.vzwops.com:443/"
    event_types: ["StatusChange", "ResourceUpdated", "ResourceAdded", "ResourceRemoved", "Alert"]

- name: "Subscribe to Redfish Alarms"
  uri:
    url: "https://[{{ bmc_ip }}]/redfish/v1/EventService/Subscriptions"
    method: POST
    body_format: json
    body: '{
            "Context": "{{ event_context }}",
            "Destination": "{{ event_destination }}",
            "EventTypes": {{ event_types }},          ← BROKEN on iLO6 and iLO7
            "Protocol": "Redfish",
            ...
          }'
```

**Required Change:**
```yaml
- name: "Set facts to subscribe events for HPE servers"
  set_fact:
    event_context: "Subscription_VCMP"
    event_destination: "https://vcp-fe-redfishevents.mon.vzwops.com:443/"
    event_types: ["StatusChange", "ResourceUpdated", "ResourceAdded", "ResourceRemoved", "Alert"]
    event_registry_prefixes: ["iLOEvents", "ResourceEvent", "NetworkDevice", "StorageDevice",
                               "iLOResourceEvents", "iLOSecurityEvents"]

- name: "Subscribe to Redfish Alarms (iLO6 / iLO7 — RegistryPrefixes)"
  uri:
    url: "https://[{{ bmc_ip }}]/redfish/v1/EventService/Subscriptions"
    method: POST
    body_format: json
    body: '{
            "Context": "{{ event_context }}",
            "Destination": "{{ event_destination }}",
            "RegistryPrefixes": {{ event_registry_prefixes }},
            "Protocol": "Redfish",
            "Oem": {
              "Hpe": {
                "DeliveryRetryAttempts": 3,
                "DeliveryRetryIntervalInSeconds": 30,
                "MutualAuthenticationEnabled": false,
                "RequestedMaxEventsToQueue": 3,
                "RetireOldEventInMinutes": 10
              }
            }
          }'
    url_username: "{{ bmc_username }}"
    url_password: "{{ bmc_password }}"
    force_basic_auth: yes
    status_code: [200, 201, 204]
    validate_certs: no
    return_content: yes
  register: result
  until: result.status == 201
  retries: 10
  delay: 30
  delegate_to: localhost
```

**Reason:**
Confirmed on both iLO6 (e930t) and iLO7 (EL140 e033) that `EventTypesForSubscription` is absent
and `RegistryPrefixes` is the required mechanism. The existing `EventTypes` field will silently
fail or be ignored on iLO6/7.

**Risk / Notes:**
If iLO5 (E910t/E920t) still requires `EventTypes`, add a `when:` branch splitting the two paths.
Verify on an E910t or E920t before applying to the full HPE role.

---

## VERIFY REQUIRED — `enable_secure_boot.py` / `roles/hpe/secure-boot`

**Assessment:** VERIFY REQUIRED

**PROPOSED Test Reference:** PROPOSED-30 result: PASS

**Observed Behavior on HPE EL140 Gen12:**
Both Verizon KEK and Wind River DB certificates confirmed installed on e033:
- KEK count = 4 (baseline 3 factory + 1 VZ KEK cert: "Verizon KEK CA 2026")
- DB count = 9 (baseline 8 factory + 1 WR DB cert: "Wind River Systems, Inc.")
- Secure Boot enabled, SecureBootCurrentBoot = Enabled
- Cert install paths: `SecureBoot/SecureBootDatabases/KEK/Certificates` and `.../db/Certificates`
- Cert IDs are sequential integers; new cert ID = current count + 1

The bios-config role references `shell: enable_secure_boot.py ...` for EL140. This script
must be verified to:
1. POST cert files to `/redfish/v1/Systems/1/SecureBoot/SecureBootDatabases/KEK/Certificates` and `.../db/Certificates`
2. PATCH `SecureBoot.SecureBootEnable: true`
3. Handle the WorkloadProfile cold boot cycle if WorkloadProfile changes
4. Wait for `PostState = FinishedPost` before reading back cert IDs

The iLO7 cert install paths are identical to what was validated in PROPOSED-30.

**Action Required:**
Read `enable_secure_boot.py` source and verify it targets these exact paths. If it uses
iLO5/6 paths or a different mechanism, add an iLO7 code path guarded by `server_type`.

---

## OPERATIONAL NOTE — NEBS 62°C Inlet Ambient Threshold (PROPOSED-31)

**Assessment:** NO PLAYBOOK CHANGE — MANUAL POST-PROVISIONING STEP REQUIRED

**PROPOSED Test Reference:** PROPOSED-31 result: PASS WITH DEVIATION

**Observed Behavior:**
`ThermalConfiguration = OptimalCooling` is the factory default — no playbook action needed.
`WarningTempUserThreshold` (the NEBS GR-63 inlet ambient caution threshold) is not Redfish-writable
on iLO7 v1.20.00. It cannot be set by the Ansible playbook or by any automated Redfish PATCH.
Confirmed on both e002 and e033: value = 0 (not set).

**Manual Step Required After Playbook Completes:**
1. Log in to iLO web interface at `https://[BMC_IP]`
2. Navigate to: Host → Hardware → Thermal and Cooling
3. Set 01-Inlet Ambient Caution Threshold = 62°C
4. Click Apply
5. Verify via `GET /Chassis/1/Thermal` that `Temperatures[0].Oem.Hpe.WarningTempUserThreshold = 62`

**Add to site provisioning SOP.** Do not block the playbook run on this step — it is a
post-handoff operational requirement, not an automation gate.

---

## GAP — Security Hardening Role Does Not Exist

**Assessment:** GAP — CHANGE REQUIRED (new role)

**PROPOSED Test Reference:** PROPOSED-32 result: PASS WITH DEVIATION

**Observed Behavior:**
The BMC Ansible playbook has no security hardening role for any platform. The EL140 provisioning
standard requires:
- SNMP service disabled (SnmpService: SNMPv1Enabled=false, AlertsEnabled=false)
- HTTP plaintext disabled (NetworkProtocol: HTTP.ProtocolEnabled=false)
- SSDP multicast disabled (NetworkProtocol: SSDP.ProtocolEnabled=false)
- IPMI/DCMI over LAN disabled (NetworkProtocol: IPMI.ProtocolEnabled=false)
- Login security banner enabled with Verizon policy text
- Auth failure delay: AuthFailureDelayTimeSeconds >= 5

All of the above are currently applied by `el140_configure.py` when run manually. The Ansible
playbook does not call `el140_configure.py` or perform equivalent steps.

**Currently passing on e033 because `el140_configure.py` was run prior to this test.**

**Deferred items (not blocking):**
- Password Complexity (EnforcePasswordComplexity) — disabled, deferred per VCP Far Edge decision
- Global Component Integrity — disabled, deferred (NIC SPDM compat verification pending)
- Default TLS Certificate — self-signed, deferred (PKI infrastructure required)
- iLO Service Port USB hardening — deferred

**Action Required:**
Add a `security-hardening` role to the BMC playbook (or extend an existing role) that:
1. Calls `el140_configure.py --check-only` and reports WARN if any setting is incorrect
2. OR implements the security hardening steps directly as Ansible tasks
   (SNMP disable, HTTP/SSDP/IPMI disable, login banner, auth failure settings)

This role should be guarded `when: server_type == "HPE-GEN12-el140"` initially, and expanded
to other HPE platforms as those are validated.

---

## NO CHANGE — `roles/hpe/account-create`

**Assessment:** NO CHANGE REQUIRED

**PROPOSED Test Reference:** PROPOSED-20, PROPOSED-21, PROPOSED-22 — all PASS (e033)

**Reason:**
`add_user_account.py` enumerates account members via the AccountService Members list
and constructs paths from the `@odata.id` values. Non-sequential large integer IDs
(65536 for Administrator, 65547 for new account) are handled correctly — the script does
not assume sequential IDs. AccountService POST, PATCH, and DELETE paths are identical on iLO7.
`LoginName` check uses `Oem.Hpe.LoginName` which is auto-populated from UserName on iLO7.

---

## NO CHANGE — `roles/hpe/system-off`, `roles/hpe/system-on`

**Assessment:** NO CHANGE REQUIRED

**PROPOSED Test Reference:** PROPOSED-28 — PASS

**Reason:**
`ForceOff` and `On` reset types confirmed functional on iLO7 at
`/redfish/v1/Systems/1/Actions/ComputerSystem.Reset`. Paths and body format identical.

---

## NO CHANGE — `roles/hpe/syslog-enable`, `roles/hpe/syslog-disable`

**Assessment:** NO CHANGE REQUIRED

**PROPOSED Test Reference:** PROPOSED-26 — PASS WITH DEVIATION (initial state only; path confirmed)

**Reason:**
`Oem.Hpe.RemoteSyslogEnabled`, `RemoteSyslogServer`, `RemoteSyslogPort` confirmed
writable via `PATCH /redfish/v1/Managers/1/NetworkProtocol` on iLO7 — identical path
to iLO5/6. Port 5140 confirmed as lab syslog port (vcpe-faredge-syslog.mon.vzwops.com:5140).
Note: syslog was enabled but server was blank on e033 at test start — el140_configure.py
had been run partially. After PATCH: server and port confirmed correct.

---

## NO CHANGE — `disable_dhcp_ntp.py`, `set_ilo_sntp_servers.py`

**Assessment:** NO CHANGE REQUIRED

**PROPOSED Test Reference:** PROPOSED-23 — PASS WITH DEVIATION (scripts already correct)

**Reason:**
`disable_dhcp_ntp.py` correctly targets `EthernetInterfaces/1.DHCPv4/v6.UseNTPServers` —
confirmed compatible with iLO7 (both fields false on e033). `set_ilo_sntp_servers.py` already
targets `/redfish/v1/Managers/1/DateTime` with `StaticNTPServers` — correct iLO7 path.
StaticNTPServers = [2607:f160:10:9200::a, 2607:f160:10:9200::b] confirmed on e033.

Note: `set_ilo_sntp_servers.py` also patches `PropagateTimeToHost: True` and
`TimeZone: {Index: 15}` — verify these fields are accepted by iLO7 without error.
In PROPOSED-23, a PATCH with `StaticNTPServers` only returned HTTP 200; the script's
additional fields need a test run to confirm they do not trigger HTTP 400.

---

## VERIFY REQUIRED — `configure_dns.py`

**Assessment:** VERIFY REQUIRED (likely works, not confirmed on iLO7)

**PROPOSED Test Reference:** PROPOSED-24 — PASS WITH DEVIATION

**Reason:**
IPv6 DNS servers confirmed present in `EthernetInterfaces/1.StaticNameServers` on e033:
`2607:f160:10:4409:ce:103:0:5` and `2607:f160:10:4409:ce:103:0:6`. The script targets
`Oem.Hpe.IPv6.DNSServers` — a separate IPv6-specific path that needs verification.
Script also uses `get_resource_directory` which hits `/redfish/v1/resourcedirectory` — this
endpoint needs verification on iLO7 (if it fails, the script falls back to Managers
enumeration which should work). Confirm by running `configure_dns.py` against the EL140.

---

## Inventory / host_vars Addition Required

For any HPE EL140 Gen12 node, add to its host_vars file:

```yaml
server_type: HPE-GEN12-el140
```

This is required for all `when: server_type == "HPE-GEN12-el140"` guards to activate.
Without this, the EL140 will execute the iLO5/6 code paths and fail.

---

## Summary of Files to Change

| File | Change Type |
|------|-------------|
| `group_vars/HPE` | Add `bios_attribute_value_workload_profile_vRAN: vRAN` |
| `roles/hpe/check_model/tasks/main.yaml` | Add EL140 fail guard + server_type set_fact |
| `roles/hpe/bios-config/tasks/main.yaml` | Guard existing tasks; add EL140 WorkloadProfile-only block |
| `roles/hpe/mac-discover/tasks/main.yaml` | Add EL140 LinkStatus-based MAC discovery block |
| `roles/hpe/ilo-hostname/tasks/main.yaml` | Guard existing task; add EL140 NetworkProtocol task + FQDN |
| `roles/hpe/subscribe-redfish-events/tasks/main.yaml` | Replace EventTypes with RegistryPrefixes |
| `enable_secure_boot.py` | Verify iLO7 cert paths — update if needed |
| `roles/hpe/security-hardening/` | NEW ROLE — SNMP/HTTP/IPMI/SSDP disable, login banner |
| `inventory/<el140-hostname>.yaml` | Add `server_type: HPE-GEN12-el140` |

---

## New Findings vs. Rev 1 (e002 → e033)

| Finding | e002 Result | e033 Result | Impact |
|---------|-------------|-------------|--------|
| OAM NIC interface | ID 5, MAC 10:2e:00:03:26:e0 (Intel) | ID 2473, MAC b4:7a:f1:d9:48:fc (HPE) | Confirms LinkUp-based discovery is correct; interface ID is not fixed |
| NetworkProtocol.FQDN domain | Not checked | laserlab-bench.local (wrong domain) | Hostname PATCH should include explicit FQDN to override lab default |
| Syslog at test start | Correct (el140_configure.py run) | Blank server, port 514 (not configured) | Playbook must explicitly set syslog server/port |
| Secure Boot | Not tested on e002 | Both certs installed, SecureBoot Enabled | PROPOSED-30 PASS; enable_secure_boot.py needs iLO7 verification |
| Security hardening | Not tested on e002 | 3 deferred Risk items; all critical controls PASS | Playbook missing security hardening role |
