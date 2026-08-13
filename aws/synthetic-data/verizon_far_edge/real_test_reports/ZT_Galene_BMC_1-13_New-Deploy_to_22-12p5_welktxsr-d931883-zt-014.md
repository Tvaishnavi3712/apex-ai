# ZT Triton 2.27 BMC firmware validation
# New Deploy of 21.12p10 with firmware installed in subcloud to 2.27
# 12/13/23 James Patchett

## Target Controller rchltxfe-c000000-001 (Richardson infrastructure System)
OAM: 2607:f160:0:3043:cd:290:0:10

## Subcloud welktxsr-d931883-014(VCP-fe Infrastructure)
OAM: 2607:f160:10:8803:ce:40a:0:f405
ILO: 2607:f160:10:8803:ce:40a:0:e005

ipmitool -I lanplus -U XXXXXX -P XXXXXX -H 2607:f160:10:8803:ce:40a:0:e005 sol activate


### controller has been upgraded to 21.12p10, next step is to upgrade subcloud with triton 2.27 firmware

### Controller validation of 21.12p10 readyness
```log
[XXXXXX@controller-0 ~(keystone_admin)]$ system show
+------------------------+--------------------------------------+
| Property               | Value                                |
+------------------------+--------------------------------------+
| contact                | demo.engineer@verizon.com              |
| created_at             | 2024-05-24T19:38:31.409443+00:00     |
| description            | Wind River Cloud Platform 22.12.5    |
| distributed_cloud_role | systemcontroller                     |
| https_enabled          | True                                 |
| latitude               | None                                 |
| location               | None                                 |
| longitude              | None                                 |
| name                   | rchltxfe-c000000-001                 |
| region_name            | RegionOne                            |
| sdn_enabled            | False                                |
| security_feature       | spectre_meltdown_v1                  |
| service_project_name   | services                             |
| software_version       | 22.12                                |
| system_mode            | duplex                               |
| system_type            | Standard                             |
| timezone               | UTC                                  |
| updated_at             | 2025-01-04T20:56:09.453529+00:00     |
| uuid                   | 8eac0d49-bc33-43eb-a80e-fe2d28db5749 |
| vswitch_type           | none                                 |
+------------------------+--------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ sw-patch query
      Patch ID         RR  Release  Patch State
=====================  ==  =======  ===========
WRCP_21.12_PATCH_0001  Y    21.12    Committed
WRCP_21.12_PATCH_0002  Y    21.12    Committed
WRCP_21.12_PATCH_0003  Y    21.12    Committed
WRCP_21.12_PATCH_0004  Y    21.12    Committed
WRCP_21.12_PATCH_0005  Y    21.12    Committed
WRCP_21.12_PATCH_0006  Y    21.12    Committed
WRCP_21.12_PATCH_0007  Y    21.12    Committed
WRCP_21.12_PATCH_0008  Y    21.12    Committed
WRCP_21.12_PATCH_0009  Y    21.12    Committed
WRCP_21.12_PATCH_0010  N    21.12    Committed
WRCP_22.12_PATCH_0001  Y    22.12    Committed
WRCP_22.12_PATCH_0002  Y    22.12    Committed
WRCP_22.12_PATCH_0003  Y    22.12    Committed
WRCP_22.12_PATCH_0004  Y    22.12    Committed
WRCP_22.12_PATCH_0005  Y    22.12    Committed

[XXXXXX@controller-0 ~(keystone_admin)]$ fm alarm-list
+-------+------------------------------------------------+---------------------------------------+----------+-------------+
| Alarm | Reason Text                                    | Entity ID                             | Severity | Time Stamp  |
| ID    |                                                |                                       |          |             |
+-------+------------------------------------------------+---------------------------------------+----------+-------------+
| 100.  | 'CLUSTER-HOST' interface degraded              | host=controller-1.interface=cluster-  | major    | 2025-01-25T |
| 111   |                                                | host                                  |          | 11:01:30    |
|       |                                                |                                       |          |             |
| 100.  | 'MGMT' interface degraded                      | host=controller-1.interface=mgmt      | major    | 2025-01-25T |
| 109   |                                                |                                       |          | 11:01:30    |
|       |                                                |                                       |          |             |
| 100.  | 'OAM' interface degraded                       | host=controller-1.interface=oam       | major    | 2025-01-25T |
| 107   |                                                |                                       |          | 11:01:30    |
|       |                                                |                                       |          |             |
| 100.  | 'MGMT' port failed                             | host=controller-1.port=de2f7df5-d7cb- | major    | 2025-01-25T |
| 108   |                                                | 498b-aa46-256404936868                |          | 11:01:30    |
|       |                                                |                                       |          |             |
| 100.  | 'CLUSTER-HOST' port failed                     | host=controller-1.port=de2f7df5-d7cb- | major    | 2025-01-25T |
| 110   |                                                | 498b-aa46-256404936868                |          | 11:01:30    |
|       |                                                |                                       |          |             |
| 100.  | 'OAM' port failed                              | host=controller-1.port=de2f7df5-d7cb- | major    | 2025-01-25T |
| 106   |                                                | 498b-aa46-256404936868                |          | 11:01:30    |
|       |                                                |                                       |          |             |
| 280.  | welktxef-d931883-022 dc-cert sync_status is    | subcloud=welktxef-d931883-022.        | major    | 2024-06-26T |
| 002   | out-of-sync                                    | resource=dc-cert                      |          | 12:35:49.   |
|       |                                                |                                       |          | 134774      |
|       |                                                |                                       |          |             |
| 280.  | welktxef-d931883-022 is offline                | subcloud=welktxef-d931883-022         | critical | 2024-06-26T |
| 001   |                                                |                                       |          | 06:50:35.   |
|       |                                                |                                       |          | 160514      |
|       |                                                |                                       |          |             |
+-------+------------------------------------------------+---------------------------------------+----------+-------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ dcmanager subcloud list
+----+----------------------+------------+--------------+---------------+-------------+---------------+-----------------+
| id | name                 | management | availability | deploy status | sync        | backup status | backup datetime |
+----+----------------------+------------+--------------+---------------+-------------+---------------+-----------------+
| 42 | welktxef-d931883-022 | managed    | offline      | complete      | out-of-sync | None          | None            |
| 62 | welktxsr-d931883-022 | managed    | online       | complete      | in-sync     | None          | None            |
+----+----------------------+------------+--------------+---------------+-------------+---------------+-----------------+
[XXXXXX@controller-0 ~(keystone_admin)]$  system application-list
+--------------------------+----------+-------------------------------------------+------------------+----------+-----------+
| application              | version  | manifest name                             | manifest file    | status   | progress  |
+--------------------------+----------+-------------------------------------------+------------------+----------+-----------+
| cert-manager             | 22.12-8  | cert-manager-fluxcd-manifests             | fluxcd-manifests | applied  | completed |
| nginx-ingress-controller | 22.12-1  | nginx-ingress-controller-fluxcd-manifests | fluxcd-manifests | applied  | completed |
| oidc-auth-apps           | 22.12-6  | oidc-auth-apps-fluxcd-manifests           | fluxcd-manifests | applied  | completed |
| platform-integ-apps      | 22.12-72 | platform-integ-apps-fluxcd-manifests      | fluxcd-manifests | uploaded | completed |
| wr-analytics             | 23.09-1  | wr-analytics-fluxcd-manifests             | fluxcd-manifests | applied  | completed |
+--------------------------+----------+-------------------------------------------+------------------+----------+-----------+
[XXXXXX@controller-0 ~(keystone_admin)]$


```


### start new deployment 
### Unmanage subcloud then delete from controller..
```log
[XXXXXX@controller-0 ~(keystone_admin)]$ dcmanager subcloud list
+----+----------------------+------------+--------------+---------------+-------------+---------------+-----------------+
| id | name                 | management | availability | deploy status | sync        | backup status | backup datetime |
+----+----------------------+------------+--------------+---------------+-------------+---------------+-----------------+
| 42 | welktxef-d931883-022 | managed    | offline      | complete      | out-of-sync | None          | None            |
| 62 | welktxsr-d931883-022 | managed    | online       | complete      | in-sync     | None          | None            |
+----+----------------------+------------+--------------+---------------+-------------+---------------+-----------------+
[XXXXXX@controller-0 ~(keystone_admin)]$
```
### no evidence of subcloud on Controller



### wipedisk the subcloud, then power off

```log
[XXXXXX@welktxefnce-h-pe1util-vm01 ZT-Galene-BMC-update-v1.13]$ ipmitool -I lanplus -U XXXXXX -P XXXXXX -H 2607:f160:10:8803:ce:40a:0:e005 sol activate
[SOL Session operational.  Use ~? for help]

localhost login:
localhost login: XXXXXX
Password:

XXXXXX Unauthorized access to this system is forbidden and will be
prosecuted by law. By accessing this system, you agree that your
actions may be monitored if unauthorized usage is suspected.

Linux localhost 5.10.0-6-rt-amd64 #1 SMP PREEMPT_RT StarlingX Debian 5.10.177-1.stx.76 (2024-03-29 x86_64

WARNING: Unauthorized access to this system is forbidden and will be
prosecuted by law. By accessing this system, you agree that your
actions may be monitored if unauthorized usage is suspected.

Last login: Tue Nov  5 21:58:59 UTC 2024 from 2607:f160:0:312f::2 on pts/0
XXXXXX@localhost:~$ sudo su -
Password:

XXXXXX Unauthorized access to this system is forbidden and will be
prosecuted by law. By accessing this system, you agree that your
actions may be monitored if unauthorized usage is suspected.

Linux localhost 5.10.0-6-rt-amd64 #1 SMP PREEMPT_RT StarlingX Debian 5.10.177-1.stx.76 (2024-03-29 x86_64

This message is shown once a day. To disable it please create the
/root/.hushlogin file.
root@localhost:~# wipedisk
This will result in the loss of all data on the hard drives and
will require this node to be re-installed.
The following disks will be wiped:
    /dev/nvme0n1
    /dev/nvme0n1p4

Are you absolutely sure? [y/n] y
Type 'wipediskscompletely' to confirm: wipediskscompletely
Wiping /dev/nvme0n1p4...
/dev/nvme0n1p4: 8 bytes were erased at offset 0x00000218 (LVM2_member): 4c 56 4d 32 20 30 30 31
Trying to unmount /dev/nvme0n1p4
Warning! /dev/nvme0n1p4 is not mounted
34+0 records in
34+0 records out
17408 bytes (17 kB, 17 KiB) copied, 6.2401e-05 s, 279 MB/s
34+0 records in
34+0 records out
17408 bytes (17 kB, 17 KiB) copied, 6.1071e-05 s, 285 MB/s
Skipping wipe backup partition /dev/nvme0n1p1...
Wiping partition /dev/nvme0n1p2...
/dev/nvme0n1p2: 8 bytes were erased at offset 0x00000036 (vfat): 46 41 54 31 36 20 20 20
/dev/nvme0n1p2: 1 byte was erased at offset 0x00000000 (vfat): eb
/dev/nvme0n1p2: 2 bytes were erased at offset 0x000001fe (vfat): 55 aa
Trying to unmount /dev/nvme0n1p2
/dev/nvme0n1p2 has been successfully unmounted
34+0 records in
34+0 records out
17408 bytes (17 kB, 17 KiB) copied, 0.000611706 s, 28.5 MB/s
34+0 records in
34+0 records out
17408 bytes (17 kB, 17 KiB) copied, 0.000571189 s, 30.5 MB/s
Removing partition /dev/nvme0n1p2...
Warning: The kernel is still using the old partition table.
The new table will be used at the next reboot or after you
run partprobe(8) or kpartx(8)
The operation has completed successfully.
Wiping partition /dev/nvme0n1p3...
/dev/nvme0n1p3: 2 bytes were erased at offset 0x00000438 (ext4): 53 ef
Removing partition /dev/nvme0n1p3...
Warning: The kernel is still using the old partition table.
The new table will be used at the next reboot or after you
run partprobe(8) or kpartx(8)
The operation has completed successfully.
Wiping partition /dev/nvme0n1p4...
Trying to unmount /dev/nvme0n1p4
Warning! /dev/nvme0n1p4 is not mounted
34+0 records in
34+0 records out
17408 bytes (17 kB, 17 KiB) copied, 6.8528e-05 s, 254 MB/s
34+0 records in
34+0 records out
17408 bytes (17 kB, 17 KiB) copied, 8.8146e-05 s, 197 MB/s
Removing partition /dev/nvme0n1p4...
Warning: The kernel is still using the old partition table.
The new table will be used at the next reboot or after you
run partprobe(8) or kpartx(8)
The operation has completed successfully.
1+0 records in
1+0 records out
440 bytes copied, 3.7642e-05 s, 11.7 MB/s
The disk(s) have been wiped.
root@localhost:~# poweroff
[  OK  ] Removed slice system-modprobe.slice.
[  OK  ] Stopped target Graphical Interface.
[         Stopping Service Management Shutdown Unit...
         Stopping LSB: Provide limi…rivileges to specific users...
         Stopping User Login Management...
         Stopping Load/Save Random Seed...
         Stopping Dynamic System Tuning Daemon...
         Stopping StarlingX Filesystem Initialization...
[  OK  ] Stopped pNFS block layout mapping daemon.
[  OK  ] Stopped Avahi mDNS/DNS-SD Stack.
[  OK  ] Stopped Regular background program processing daemon.
[  OK  ] Stopped Authorization Manager.
[  OK  ] Stopped User Login Management.
[  OK  ] Stopped Lighttpd Daemon.
[  OK  ] Stopped StarlingX Affine Tasks.
[  OK  ] Stopped Getty on tty1.
[  OK  ] Stopped StarlingX Maintenance Worker Goenable Ready.
[  OK  ] Stopped Logout off all iSCSI sessions on shutdown.
[  OK  ] Stopped LVM event activation on device 259:4.
[  OK  ] Stopped Load/Save Random Seed.
[  OK  ] Stopped StarlingX Filesystem Initialization.
[  OK  ] Stopped Serial Getty on ttyS0.
[  OK  ] Stopped LLDP daemon.
[  OK  ] Stopped LSB: Open vSwitch VTEP emulator.
[  OK  ] Stopped LSB: Simple OpenFlow controller for testing.
[  OK  ] Stopped StarlingX Filesystem Server.
[  OK  ] Stopped LSB: Ceph RBD Mapping.
[  OK  ] Stopped LSB: Load kernel image with kexec.
[  OK  ] Stopped LSB: radosgw RESTful rados gateway.
[  OK  ] Stopped LSB: rng-tools (Debian variant).
[  OK  ] Stopped LSB: Provide limit… privileges to specific users.
[  OK  ] Removed slice system-getty.slice.
[  OK  ] Removed slice system-lvm2\x2dpvscan.slice.
[ 4655.242986] kdump-tools[13674]: Stopping kdump-tools:
[  OK  ] Removed slice system-serial\x2dgetty.slice.
[ 4655.257548] kdump-tools[13759]: Kernel security lockdown: none
         Unmounting RPC Pipe File System...
[ 4655.275506] kdump-tools[13759]: unloaded kdump kernel.
         Stopping StarlingX Affine Platform...
         Stopping LSB: Execute the …-e command to reboot system...
         Stopping StarlingX Cloud Filesystem Auto-mounter...
         Stopping Permit User Sessions...
[  OK  ] Stopped Kernel crash dump capture service.
[  OK  ] Stopped StarlingX Maintenance Host Watchdog.
[  OK  ] Stopped fast remote file copy program daemon.
[  OK  ] Stopped LSB: Open vSwitch GRE-over-IPsec daemon.
[  OK  ] Unmounted RPC Pipe File System.
[  OK  ] Stopped Permit User Sessions.
[  OK  ] Stopped Dynamic System Tuning Daemon.
         Stopping StarlingX Maintenance Process Monitor...
[  OK  ] Stopped LSB: Execute the k…c -e command to reboot system.
[  OK  ] Stopped StarlingX Cloud Filesystem Auto-mounter.
[  OK  ] Stopped StarlingX Maintenance Process Monitor.
         Stopping StarlingX Maintenance Filesystem Monitor...
         Stopping StarlingX Maintenance Goenable Ready...
         Stopping StarlingX Maintenance Heartbeat Agent...
         Stopping Starling-X Maintenance Link Monitor...
         Stopping StarlingX Maintenance Command Handler Client...
         Stopping StarlingX Maintenance Alarm Handler Client...
         Stopping StarlingX Maintenance Logger...
[  OK  ] Stopped StarlingX Pxeboot Feed Refresh.
         Stopping Service Management Event Recorder Unit...
         Stopping OpenBSD Secure Shell server...
         Stopping StarlingX Patching Agent...
         Stopping StarlingX Patching Controller Daemon...
         Stopping StarlingX System Inventory Agent...
[  OK  ] Stopped OpenBSD Secure Shell server.
[  OK  ] Stopped StarlingX Affine Platform.
[  OK  ] Stopped StarlingX Maintenance Goenable Ready.
[  OK  ] Stopped StarlingX Patching Agent.
[  OK  ] Stopped StarlingX Patching Controller Daemon.
         Stopping D-Bus System Message Bus...
[  OK  ] Stopped StarlingX Patching Controller.
[  OK  ] Stopped D-Bus System Message Bus.
[  OK  ] Stopped StarlingX System Inventory Agent.
         Stopping StarlingX Filesystem Common...
[  OK  ] Stopped StarlingX Filesystem Common.
[  OK  ] Stopped Starling-X Maintenance Link Monitor.
[  OK  ] Stopped StarlingX Maintenance Filesystem Monitor.
[  OK  ] Stopped StarlingX Maintenance Command Handler Client.
[  OK  ] Stopped StarlingX Maintenance Alarm Handler Client.
[  OK  ] Stopped StarlingX Maintenance Logger.
[  OK  ] Stopped StarlingX Maintenance Heartbeat Agent.
         Stopping StarlingX Maintenance Heartbeat Client...
[  OK  ] Stopped StarlingX Maintenance Heartbeat Client.
[  OK  ] Stopped Service Management Shutdown Unit.
[  OK  ] Stopped Service Management Event Recorder Unit.
         Stopping Service Management API Unit...
[  OK  ] Stopped Service Management API Unit.
         Stopping Service Management Unit...
[  OK  ] Stopped Service Management Unit.
[  OK  ] Stopped General StarlingX config gate.
         Stopping StarlingX Log Management...
[  OK  ] Stopped StarlingX Log Management.
         Stopping iSCSI initiator daemon (iscsid)...
[  OK  ] Stopped StarlingX Patching.
         Stopping System Logger Daemon...
[  OK  ] Stopped iSCSI initiator daemon (iscsid).
[  OK  ] Stopped target Network is Online.
[  OK  ] Stopped target Network.
         Stopping Raise network interfaces...
[  OK  ] Stopped Raise network interfaces.
[  OK  ] Stopped System Logger Daemon.
[  OK  ] Stopped target Basic System.
[  OK  ] Stopped target Paths.
[  OK  ] Stopped OSTree Monitor Staged Deployment.
[  OK  ] Stopped target Slices.
[  OK  ] Removed slice User and Session Slice.
[  OK  ] Stopped target Sockets.
[  OK  ] Closed Avahi mDNS/DNS-SD Stack Activation Socket.
[  OK  ] Closed D-Bus System Message Bus Socket.
[  OK  ] Stopped target System Initialization.
[  OK  ] Stopped target Local Encrypted Volumes.
[  OK  ] Stopped Dispatch Password …ts to Console Directory Watch.
[  OK  ] Stopped Forward Password R…uests to Wall Directory Watch.
[  OK  ] Stopped target Swap.
[  OK  ] Closed Syslog Socket.
[  OK  ] Stopped Apply Kernel Variables.
[  OK  ] Stopped Load Kernel Modules.
         Stopping Update UTMP about System Boot/Shutdown...
[  OK  ] Stopped Update UTMP about System Boot/Shutdown.
[  OK  ] Stopped Create Volatile Files and Directories.
[  OK  ] Stopped target Local File Systems.
         Unmounting /boot...
         Unmounting /sysroot/boot...
         Unmounting Temporary Directory...
         Unmounting /var/rootdirs/opt/platform-backup...
         Unmounting /var/rootdirs/scratch...
         Stopping Flush Journal to Persistent Storage...
[  OK  ] Unmounted /boot.
[  OK  ] Unmounted /sysroot/boot.
[  OK  ] Unmounted Temporary Directory.
[  OK  ] Unmounted /var/rootdirs/opt/platform-backup.
[  OK  ] Unmounted /var/rootdirs/scratch.
[  OK  ] Stopped Flush Journal to Persistent Storage.
         Unmounting /sysroot...
         Unmounting /var/log...
[  OK  ] Stopped OSTree Remount OS/ Bind Mounts.
[  OK  ] Stopped File System Check …disk/by-label/platform_backup.
[  OK  ] Stopped File System Check …v/mapper/cgts--vg-scratch--lv.
[  OK  ] Unmounted /sysroot.
[  OK  ] Unmounted /var/log.
         Unmounting /var...
[  OK  ] Stopped File System Check … /dev/mapper/cgts--vg-log--lv.
[  OK  ] Removed slice system-systemd\x2dfsck.slice.
[  OK  ] Unmounted /var.
[  OK  ] Stopped target Local File Systems (Pre).
[  OK  ] Reached target Unmount All Filesystems.
         Stopping Monitoring of LVM…meventd or progress polling...
         Stopping Device-Mapper Multipath Device Controller...
[  OK  ] Stopped Create Static Device Nodes in /dev.
[  OK  ] Stopped Create System Users.
[  OK  ] Stopped Remount Root and Kernel File Systems.
[  OK  ] Stopped Device-Mapper Multipath Device Controller.
[  OK  ] Stopped Monitoring of LVM2… dmeventd or progress polling.
[  OK  ] Reached target Shutdown.
[  OK  ] Reached target Final Step.
[  OK  ] Finished Power-Off.
[  OK  ] Reached target Power-Off.
ipsec_starter[5796]: charon stopped after 200 ms

ipsec_starter[5796]: ipsec starter stopped

[ 4666.975303] [14320]: Failed to unmount /usr: Device or resource busy
[ 4666.988062] systemd-shutdown[1]: Failed to finalize file systems, DM devices, ignoring.
[ 4666.989244] systemd-shutdown[1]: Powering off.
[ 4666.989282] kvm: exiting hardware virtualization
[ 4672.579737] ice 0000:45:00.0: removed Clock from ens2f0
[ 4675.097785] ice 0000:43:00.0: removed Clock from ens3f0
[ 4677.632633] ice 0000:16:00.0: removed Clock from ens1f0
[ 4678.274410] ACPI: Preparing to enter system sleep state S5
[ 4678.314416] reboot: Power down
[ 4678.314419] printk: enabled sync mode
[ 4678.363470] printk: console [ttyS0]: printing thread stopped
[ 4678.469651] acpi_power_off called


```

### subcloud wiped and powered off 

### Now delete subcloud from controller

```log
Subcloud is not on the controler...
```

### Now start automation deployment of the subcloud

```log
(ansible_6.7) szabota@welktxefnce-h-pe1util-vm05:~/playbooks/wr-installer-atlas-me$ ansible-playbook --vault-password-file password  -i inventory/welktxsr-d931883-zt-014.yaml wr_remote.yaml
883-zt-014.yaml wr_remote.yaml
PLAY [Wind River Remote Subcloud Installer] ***************************************************************************************************

TASK [Reset BMC] ******************************************************************************************************************************
Wednesday 05 February 2025  23:30:34 +0000 (0:00:00.011)       0:00:00.011 ****

TASK [remote/reset_bmc : Reset ZTS BMC using IPMItool] ****************************************************************************************
Wednesday 05 February 2025  23:30:35 +0000 (0:00:00.060)       0:00:00.072 ****
changed: [welktxsr-931883-rz-le0gls6-014 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)]

TASK [remote/reset_bmc : Wait for ZTS BMC to reset] *******************************************************************************************
Wednesday 05 February 2025  23:30:37 +0000 (0:00:02.380)       0:00:02.452 ****
Pausing for 300 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/reset_bmc : Reset HPE ILO using Redfish] *****************************************************************************************
Wednesday 05 February 2025  23:35:37 +0000 (0:05:00.023)       0:05:02.476 ****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/reset_bmc : Wait for HPE BMC to reset] *******************************************************************************************
Wednesday 05 February 2025  23:35:37 +0000 (0:00:00.016)       0:05:02.493 ****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [Download Files] *************************************************************************************************************************
Wednesday 05 February 2025  23:35:37 +0000 (0:00:00.016)       0:05:02.509 ****

TASK [common/download_files : Check if artifact files exist locally] **************************************************************************
Wednesday 05 February 2025  23:35:37 +0000 (0:00:00.026)       0:05:02.535 ****
ok: [welktxsr-931883-rz-le0gls6-014 -> localhost]

TASK [common/download_files : Download & unarchive artifact files to local directory if they don't exist] *************************************
Wednesday 05 February 2025  23:35:37 +0000 (0:00:00.272)       0:05:02.807 ****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [Set Facts] ******************************************************************************************************************************
Wednesday 05 February 2025  23:35:37 +0000 (0:00:00.017)       0:05:02.825 ****

TASK [remote/set-facts : Set facts for vip, ansible, and wr_admin] ****************************************************************************
Wednesday 05 February 2025  23:35:37 +0000 (0:00:00.027)       0:05:02.853 ****
ok: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/set-facts : Get central controller's software load version] **********************************************************************
Wednesday 05 February 2025  23:35:37 +0000 (0:00:00.036)       0:05:02.889 ****
changed: [welktxsr-931883-rz-le0gls6-014 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)]

TASK [remote/set-facts : Set facts for wr_release_version] ************************************************************************************
Wednesday 05 February 2025  23:35:43 +0000 (0:00:06.016)       0:05:08.905 ****
ok: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/set-facts : Print wr_release_version] ********************************************************************************************
Wednesday 05 February 2025  23:35:43 +0000 (0:00:00.019)       0:05:08.925 ****
ok: [welktxsr-931883-rz-le0gls6-014] =>
  msg: 'wr_release_version: 22.12'

TASK [remote/set-facts : set_fact] ************************************************************************************************************
Wednesday 05 February 2025  23:35:43 +0000 (0:00:00.024)       0:05:08.950 ****
ok: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/set-facts : trim subcloud caas version to get its main version] ******************************************************************
Wednesday 05 February 2025  23:35:43 +0000 (0:00:00.014)       0:05:08.964 ****
ok: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/set-facts : debug] ***************************************************************************************************************
Wednesday 05 February 2025  23:35:43 +0000 (0:00:00.028)       0:05:08.993 ****
ok: [welktxsr-931883-rz-le0gls6-014] =>
  subcloud_release_version: '22.12'

TASK [remote/set-facts : debug] ***************************************************************************************************************
Wednesday 05 February 2025  23:35:43 +0000 (0:00:00.016)       0:05:09.009 ****
[WARNING]: Collection ansible.utils does not support Ansible version 2.13.7
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/set-facts : debug] ***************************************************************************************************************
Wednesday 05 February 2025  23:35:44 +0000 (0:00:00.036)       0:05:09.046 ****
[WARNING]: Collection ansible.utils does not support Ansible version 2.13.7
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/set-facts : debug] ***************************************************************************************************************
Wednesday 05 February 2025  23:35:44 +0000 (0:00:00.035)       0:05:09.082 ****
[WARNING]: Collection ansible.utils does not support Ansible version 2.13.7
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/set-facts : set_fact] ************************************************************************************************************
Wednesday 05 February 2025  23:35:44 +0000 (0:00:00.064)       0:05:09.146 ****
[WARNING]: Collection ansible.utils does not support Ansible version 2.13.7
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [Remote Configure] ***********************************************************************************************************************
Wednesday 05 February 2025  23:35:44 +0000 (0:00:00.039)       0:05:09.185 ****

TASK [remote/remote-configure : Set facts] ****************************************************************************************************
Wednesday 05 February 2025  23:35:44 +0000 (0:00:00.069)       0:05:09.254 ****
ok: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-configure : Set facts - new] **********************************************************************************************
Wednesday 05 February 2025  23:35:44 +0000 (0:00:00.014)       0:05:09.269 ****
ok: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-configure : Set facts for which image list to use based on WR version] ****************************************************
Wednesday 05 February 2025  23:35:44 +0000 (0:00:00.021)       0:05:09.291 ****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-configure : Set facts for which image list to use based on WR version] ****************************************************
Wednesday 05 February 2025  23:35:44 +0000 (0:00:00.014)       0:05:09.305 ****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-configure : Set facts for which image list to use based on WR version] ****************************************************
Wednesday 05 February 2025  23:35:44 +0000 (0:00:00.013)       0:05:09.319 ****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-configure : Print wr_image_list] ******************************************************************************************
Wednesday 05 February 2025  23:35:44 +0000 (0:00:00.014)       0:05:09.333 ****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-configure : print wr_license_key] *****************************************************************************************
Wednesday 05 February 2025  23:35:44 +0000 (0:00:00.017)       0:05:09.351 ****
ok: [welktxsr-931883-rz-le0gls6-014] =>
  msg: wr_license_key = IyBXaW5kIFJpdmVyIFByb2R1Y3QgQWN0aXZhdGlvbiBGaWxlIChpbnN0YWxsLnR4dCkKIyBJc3N1ZWQgZm9yIGhvc3Q6IDxWZXJpem9uPiA8VmVyaXpvbj4gPEFueT4KIyBMaWNlbnNlIG51bWJlcihzKTogNjgyMzc0CiMgSXNzdWVkIG9uOiAxMy1hcHItMjAyMyAwOTo1MDo1MAojCiMgTm90ZTogdGhpcyBsaWNlbnNlIGlzIGdlbmVyYXRlZCBjdW11bGF0aXZlbHkgZm9yIGFsbAojIFdpbmQgUml2ZXIgc29mdHdhcmUgbWFuYWdlZCBieSB0aGlzIGhvc3QuCgojIDEuIEZsZXhMTSBsaWNlbnNlIGZpbGU6CiMgQmVnaW46IFNlcnZlciBsaWNlbnNlICAtLS0tLS0tLS0tLS0tLS0tLS0tLS0KIyBTZXJpYWwgTnVtYmVyOiA2ODQ0NDktVmVyaXpvblBPQy1HNFdEQzlDUEVLCgpQQUNLQUdFIFdSQ1BfQ09OVEFJTkVSX1BLRyB3cnNkIDIyIDg1MERCRTAwQkFCRSBcCglDT01QT05FTlRTPVdSQ1BfQ09OVEFJTkVSOjIyLjEyIE9QVElPTlM9U1VJVEUgXAoJU0lHTj0xNkI4MjY4NjkwRDgKSU5DUkVNRU5UIFdSQ1BfQ09OVEFJTkVSX1BLRyB3cnNkIDIyIHBlcm1hbmVudCB1bmNvdW50ZWQgNEMxRUE2NjQyNUUyIFwKCVZFTkRPUl9TVFJJTkc9PGxuPjY4MjM3NDwvbG4+PHBzPjIyMTMtNDM8L3BzPiBIT1NUSUQ9QU5ZIFwKCUlTU1VFRD0xMy1hcHItMjAyMyBTTj1zZXJpYWwtVmVyaXpvbi1MVjJJV0FVTEVCIFwKCVNUQVJUPTEzLWFwci0yMDIzIFNJR049NDI2RjUyOUUxRjYwCg==

TASK [remote/remote-configure : Copy storage checking script if server is HPE-LS3-e910] *******************************************************
Wednesday 05 February 2025  23:35:44 +0000 (0:00:00.019)       0:05:09.370 ****
skipping: [welktxsr-931883-rz-le0gls6-014] => (item=hpe_storage_check.py)

TASK [remote/remote-configure : Execute storage checking script if server is HPE-LS3-e910] ****************************************************
Wednesday 05 February 2025  23:35:44 +0000 (0:00:00.019)       0:05:09.390 ****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor HPE HPE-LS3-e910 (4 disks)] ****************************
Wednesday 05 February 2025  23:35:44 +0000 (0:00:00.014)       0:05:09.404 ****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor HPE HPE-LS3-e910 (2 disks)] ****************************
Wednesday 05 February 2025  23:35:44 +0000 (0:00:00.015)       0:05:09.419 ****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor HPE HPE-LS3-92s3] **************************************
Wednesday 05 February 2025  23:35:44 +0000 (0:00:00.015)       0:05:09.434 ****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor HPE HPE-LS6-92s6] **************************************
Wednesday 05 February 2025  23:35:44 +0000 (0:00:00.013)       0:05:09.448 ****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor HPE HPE-LS6-93s6] **************************************
Wednesday 05 February 2025  23:35:44 +0000 (0:00:00.014)       0:05:09.463 ****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor ZTS ZTS-LS6-gln] ***************************************
Wednesday 05 February 2025  23:35:44 +0000 (0:00:00.014)       0:05:09.478 ****
ok: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor ZTS ZTS-LS3-trtn] **************************************
Wednesday 05 February 2025  23:35:44 +0000 (0:00:00.021)       0:05:09.499 ****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-configure : Set facts for Corning] ****************************************************************************************
Wednesday 05 February 2025  23:35:44 +0000 (0:00:00.018)       0:05:09.518 ****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor ZTS ZTS-LS6-pts6 & ZTS-LS3-pts3 ZTS-LS6-aks6 & ZTS-LS3-aks3 & ZTS-XXX-ptmm] ***
Wednesday 05 February 2025  23:35:44 +0000 (0:00:00.017)       0:05:09.535 ****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-configure : Find out which DM Docker version contral has] *****************************************************************
Wednesday 05 February 2025  23:35:44 +0000 (0:00:00.018)       0:05:09.553 ****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-configure : Find out which DM file version contral has] *******************************************************************
Wednesday 05 February 2025  23:35:44 +0000 (0:00:00.021)       0:05:09.575 ****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-configure : Print dm docker version and dm file version] ******************************************************************
Wednesday 05 February 2025  23:35:44 +0000 (0:00:00.017)       0:05:09.593 ****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-configure : Discover Wind River docker image names] ***********************************************************************
Wednesday 05 February 2025  23:35:44 +0000 (0:00:00.018)       0:05:09.612 ****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-configure : Print local_images_full] **************************************************************************************
Wednesday 05 February 2025  23:35:44 +0000 (0:00:00.017)       0:05:09.629 ****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-configure : Create fact for Wind River docker image names] ****************************************************************
Wednesday 05 February 2025  23:35:44 +0000 (0:00:00.018)       0:05:09.647 ****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-configure : Determine DM Helm Chart path] *********************************************************************************
Wednesday 05 February 2025  23:35:44 +0000 (0:00:00.019)       0:05:09.667 ****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-configure : Print dm_helm_chart] ******************************************************************************************
Wednesday 05 February 2025  23:35:44 +0000 (0:00:00.017)       0:05:09.684 ****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-configure : Set DM Helm Chart file] ***************************************************************************************
Wednesday 05 February 2025  23:35:44 +0000 (0:00:00.017)       0:05:09.702 ****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-configure : Lookup Deployment Manager image tag] **************************************************************************
Wednesday 05 February 2025  23:35:44 +0000 (0:00:00.019)       0:05:09.721 ****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-configure : Lookup RBAC Proxy image tag] **********************************************************************************
Wednesday 05 February 2025  23:35:44 +0000 (0:00:00.018)       0:05:09.740 ****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-configure : Copy WRCP DM Playbook] ****************************************************************************************
Wednesday 05 February 2025  23:35:44 +0000 (0:00:00.020)       0:05:09.761 ****
skipping: [welktxsr-931883-rz-le0gls6-014] => (item=None)

TASK [remote/remote-configure : Set a fact for the central controller VIP address] ************************************************************
Wednesday 05 February 2025  23:35:44 +0000 (0:00:00.019)       0:05:09.781 ****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-configure : Configure WRCP seed template] *********************************************************************************
Wednesday 05 February 2025  23:35:44 +0000 (0:00:00.023)       0:05:09.804 ****
skipping: [welktxsr-931883-rz-le0gls6-014] => (item={'src': 'bootstrap-values.yaml', 'dest': 'welktxsr-d931883-014-bootstrap-values.yaml'})
skipping: [welktxsr-931883-rz-le0gls6-014] => (item={'src': 'deploy-values.yaml', 'dest': 'welktxsr-d931883-014-deploy-values.yaml'})
skipping: [welktxsr-931883-rz-le0gls6-014] => (item={'src': 'deploy-standard.yaml', 'dest': 'welktxsr-d931883-014-deploy-standard.yaml'})
skipping: [welktxsr-931883-rz-le0gls6-014] => (item={'src': 'install-values.yaml', 'dest': 'welktxsr-d931883-014-install-values.yaml'})

TASK [remote/remote-configure : Find out which DM Docker version contral has] *****************************************************************
Wednesday 05 February 2025  23:35:44 +0000 (0:00:00.030)       0:05:09.835 ****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-configure : Find out which DM file version contral has] *******************************************************************
Wednesday 05 February 2025  23:35:44 +0000 (0:00:00.021)       0:05:09.856 ****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-configure : Print dm docker version and dm file version] ******************************************************************
Wednesday 05 February 2025  23:35:44 +0000 (0:00:00.019)       0:05:09.876 ****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-configure : Discover Wind River docker image names] ***********************************************************************
Wednesday 05 February 2025  23:35:44 +0000 (0:00:00.019)       0:05:09.896 ****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-configure : Print local_images_full] **************************************************************************************
Wednesday 05 February 2025  23:35:44 +0000 (0:00:00.019)       0:05:09.915 ****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-configure : Create fact for Wind River docker image names] ****************************************************************
Wednesday 05 February 2025  23:35:44 +0000 (0:00:00.018)       0:05:09.934 ****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-configure : Determine DM Helm Chart path] *********************************************************************************
Wednesday 05 February 2025  23:35:44 +0000 (0:00:00.019)       0:05:09.953 ****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-configure : Print dm_helm_chart] ******************************************************************************************
Wednesday 05 February 2025  23:35:44 +0000 (0:00:00.019)       0:05:09.973 ****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-configure : Set DM Helm Chart file] ***************************************************************************************
Wednesday 05 February 2025  23:35:44 +0000 (0:00:00.017)       0:05:09.991 ****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-configure : Lookup Deployment Manager image tag] **************************************************************************
Wednesday 05 February 2025  23:35:44 +0000 (0:00:00.019)       0:05:10.010 ****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-configure : Lookup RBAC Proxy image tag] **********************************************************************************
Wednesday 05 February 2025  23:35:44 +0000 (0:00:00.019)       0:05:10.030 ****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-configure : Copy WRCP DM Playbook] ****************************************************************************************
Wednesday 05 February 2025  23:35:45 +0000 (0:00:00.021)       0:05:10.051 ****
skipping: [welktxsr-931883-rz-le0gls6-014] => (item=None)

TASK [remote/remote-configure : Set a fact for the central controller VIP address] ************************************************************
Wednesday 05 February 2025  23:35:45 +0000 (0:00:00.019)       0:05:10.071 ****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-configure : Configure WRCP seed template] *********************************************************************************
Wednesday 05 February 2025  23:35:45 +0000 (0:00:00.023)       0:05:10.094 ****
skipping: [welktxsr-931883-rz-le0gls6-014] => (item={'src': 'bootstrap-values.yaml', 'dest': 'welktxsr-d931883-014-bootstrap-values.yaml'})
skipping: [welktxsr-931883-rz-le0gls6-014] => (item={'src': 'deploy-values.yaml', 'dest': 'welktxsr-d931883-014-deploy-values.yaml'})
skipping: [welktxsr-931883-rz-le0gls6-014] => (item={'src': 'deploy-standard.yaml', 'dest': 'welktxsr-d931883-014-deploy-standard.yaml'})
skipping: [welktxsr-931883-rz-le0gls6-014] => (item={'src': 'install-values.yaml', 'dest': 'welktxsr-d931883-014-install-values.yaml'})

TASK [remote/remote-configure : Set a fact for the central controller VIP address] ************************************************************
Wednesday 05 February 2025  23:35:45 +0000 (0:00:00.031)       0:05:10.125 ****
ok: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-configure : Retrieve sysinv password from CC] *****************************************************************************
Wednesday 05 February 2025  23:35:45 +0000 (0:00:00.026)       0:05:10.152 ****
changed: [welktxsr-931883-rz-le0gls6-014 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)]

TASK [remote/remote-configure : Store sysinv password] ****************************************************************************************
Wednesday 05 February 2025  23:35:48 +0000 (0:00:03.728)       0:05:13.880 ****
ok: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-configure : copy seed templates] ******************************************************************************************
Wednesday 05 February 2025  23:35:48 +0000 (0:00:00.028)       0:05:13.909 ****
[WARNING]: Collection ansible.netcommon does not support Ansible version 2.13.7
[WARNING]: Collection ansible.utils does not support Ansible version 2.13.7
changed: [welktxsr-931883-rz-le0gls6-014 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)] => (item={'src': 'bootstrap-values.yaml', 'dest': 'welktxsr-d931883-014-bootstrap-values.yaml'})
ok: [welktxsr-931883-rz-le0gls6-014 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)] => (item={'src': 'deploy-standard.yaml', 'dest': 'welktxsr-d931883-014-deploy-standard.yaml'})
changed: [welktxsr-931883-rz-le0gls6-014 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)] => (item={'src': 'install-values.yaml', 'dest': 'welktxsr-d931883-014-install-values.yaml'})

TASK [remote/remote-configure : Copy SSL cert files] ******************************************************************************************
Wednesday 05 February 2025  23:35:58 +0000 (0:00:09.565)       0:05:23.475 ****
ok: [welktxsr-931883-rz-le0gls6-014 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)] => (item={'filename': 'k8s_root_ca_cert.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIF8jCCA9qgAwIBAgIJAIf9Ql2uDZh+MA0GCSqGSIb3DQEBDQUAMIGFMQswCQYD\nVQQGEwJVUzEOMAwGA1UECAwFVGV4YXMxETAPBgNVBAcMCFdlc3RsYWtlMR0wGwYD\nVQQKDBRWZXJpem9uIFNvdXJjaW5nIExMQzE0MDIGA1UEAwwrVmVyaXpvbiBOZXR3\nb3JrIFdFTEtUWElCIExBQiAxIDMgUlNBIEs4UyBDQTAeFw0yMDEwMjUyMjEyNDha\nFw0zMDEwMjMyMjEyNDhaMIGFMQswCQYDVQQGEwJVUzEOMAwGA1UECAwFVGV4YXMx\nETAPBgNVBAcMCFdlc3RsYWtlMR0wGwYDVQQKDBRWZXJpem9uIFNvdXJjaW5nIExM\nQzE0MDIGA1UEAwwrVmVyaXpvbiBOZXR3b3JrIFdFTEtUWElCIExBQiAxIDMgUlNB\nIEs4UyBDQTCCAiIwDQYJKoZIhvcNAQEBBQADggIPADCCAgoCggIBAKyF9svdv/qG\n7HxBr1DWvZ3CQiDsA4m1kj0hD7jo3B3W/32ODcPpgeNmp4Oful0SsndpqEGhXDq5\noiBfqszMUpzDgdQ7siIHekb2olFEK2KniMP3H53nilIppeyMby5K3ZwF0Qbmk5WK\ncoXoYegP+Uv9bV0AMH6Dn4CVgYrLAYfmPyGgUSt4vuZ9F/rf9UkBf/DcZGqMnMax\n/Gfaq8KwmDzD9D8IVCHPrM5f4+CaKMQCFu5QkSsLYJFRiuQWWaICMMdnqpb0HZh5\niPnCSHwPPUyXxtujdI97Ovy4X5WR46jJ2+KzPYe8tVa/DL3TlKmRL9AF+oSE17bw\nzGAE7GNWxPojebHIUuoKdOQC1qiJBVS+c14r9+9P2Uy6XEhNUs+h3juRI4U3YkQ1\nUCUU3opqhOPh4jUIuPGg5aX07lt4Wpxc48D+CY1D4i6vaJLl3WCsVK7PFwWVQQEW\nIQabfuj1R2jEu7pp2Yabza58S00v1P5/kv/DNr7ADm8eYRvxLAAXCedMeSDXKBgd\npPmVXXZoZ8+X8VRGYxcw0mBBLIAiTOntT2vgLeq5T3QyiVKdU6TLAYEjS65QZ3Eg\naIX0wRqlcQI7lruTXubtENG6wWXYtnDf5795ZID1YIEqkgzZLMBqq1SBiLnWd6aK\n78Zsr4j5GmTBGpKRmwE2oO1btJCCYyG5AgMBAAGjYzBhMA8GA1UdEwEB/wQFMAMB\nAf8wHQYDVR0OBBYEFEDQ5EaGp3x02WUuvqetygqpM3dCMB8GA1UdIwQYMBaAFEDQ\n5EaGp3x02WUuvqetygqpM3dCMA4GA1UdDwEB/wQEAwICpDANBgkqhkiG9w0BAQ0F\nAAOCAgEAeCMxVJr5Jyg87DVaUtEhiWfhto993ENrnevAGqrBOoRc/KU1/C3paqhR\nsvr2r2LR+npSmeo6iz0FaO31XwHSHX95+XJeGP5Q8TGddbRiTglQsMfOkGNzxqgg\nTkdZ8A1y9v2jprONUmLADVGIVT0AoHc7V9w1I8NKhrY+rIllum4FRDiDPSnImh5h\nxmH+Nq2ZuEFVdtV/oNKzEu2ywmbgBRd5Jv3rTejxltmTZtyq8IKoKguj3NVFn93Q\nU4TbsxkcAdrLMooLYYDRTWA4t0iqKM/UkYUg4xl2l9NrY7ZUbaNd5+YsLNdqXO/c\nmp7wyMv/8ZIy1BLG4zJmX/JzWkYmULqQ+A+21+YuqrV3a81V7vcHhJcRaPOrg5cd\nYwY2eCbXMvNOdrzppIglUrlddNuqAhs1MTi/VibxYuI9isU0JckXIcCy1L+xbEda\n6v/z6wSrScVz0I4m0DpK6xMQ8t9sLcrGp5uGbj6J4nQWd+QLdq6kmAzDOZ/Gs0wb\nPYdkER4dXAVcioYFekpKv7d+nur0FPtMNIw0OdhX2eAwC22IFAq2DZRjUFvaBGaD\ni1ptfq6P1mVJ2T/exYujEDtq+8yQTfWgFm/DjEfWtcCp0Jukgv8opLR2DpCf5Ucq\nd5X7d/DP0mukJ3vZ8EIqYorwZJ1L1a2jgngjA+gPxIaW+JHfTHU=\n-----END CERTIFICATE-----\n'})
ok: [welktxsr-931883-rz-le0gls6-014 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)] => (item={'filename': 'k8s_root_ca_key.pem', 'value': '-----BEGIN PRIVATE KEY-----\nMIIJQQIBADANBgkqhkiG9w0BAQEFAASCCSswggknAgEAAoICAQCshfbL3b/6hux8\nQa9Q1r2dwkIg7AOJtZI9IQ+46Nwd1v99jg3D6YHjZqeDn7pdErJ3aahBoVw6uaIg\nX6rMzFKcw4HUO7IiB3pG9qJRRCtip4jD9x+d54pSKaXsjG8uSt2cBdEG5pOVinKF\n6GHoD/lL/W1dADB+g5+AlYGKywGH5j8hoFEreL7mfRf63/VJAX/w3GRqjJzGsfxn\n2qvCsJg8w/Q/CFQhz6zOX+PgmijEAhbuUJErC2CRUYrkFlmiAjDHZ6qW9B2YeYj5\nwkh8Dz1Ml8bbo3SPezr8uF+VkeOoydvisz2HvLVWvwy905SpkS/QBfqEhNe28Mxg\nBOxjVsT6I3mxyFLqCnTkAtaoiQVUvnNeK/fvT9lMulxITVLPod47kSOFN2JENVAl\nFN6KaoTj4eI1CLjxoOWl9O5beFqcXOPA/gmNQ+Iur2iS5d1grFSuzxcFlUEBFiEG\nm37o9UdoxLu6admGm82ufEtNL9T+f5L/wza+wA5vHmEb8SwAFwnnTHkg1ygYHaT5\nlV12aGfPl/FURmMXMNJgQSyAIkzp7U9r4C3quU90MolSnVOkywGBI0uuUGdxIGiF\n9MEapXECO5a7k17m7RDRusFl2LZw3+e/eWSA9WCBKpIM2SzAaqtUgYi51nemiu/G\nbK+I+RpkwRqSkZsBNqDtW7SQgmMhuQIDAQABAoICACysO62qa+2pRk8eixD5qfvR\ns2Hm+zuLYqSljPaqhWTMqTePswzJyDJkAHhawd0b3E6Dc2gbKlCihNKxMv744WNq\nVJHqK0QYf5ckgf9dEYboLsffk7ZFoFGKK0bHTnrENAIUl32b8xdD1EfMVp3KlRkS\nNGFijSwVVRXsoLCZxHm2Kx6/7oS9LWFtfuodV9xhoQlzaCUW5/mjWOJjgxpUs/b4\nHqS7uV1P80U1G0KraGboy5tGDXEB7y1x2e8Zwnfq7UqVE10nNQqoXcmefzpwj8Tn\ngDybZLFKjYmnDEkkj7jDHEbldsdRG/usWNZGlTYbPDA3fBkYdOsQCzvJypQmgbZ+\n3yk3Lj2+9vLEMfPrruuzyOSXgki6o5uvy7Je6PdBpsz75k8FH6a+Rw3vvP8HuP3S\nLSUYm3tyOheXHR7BKN4bnfi11RAWvDpT9S+QnZ+R8DmQzOADlnjRC8WewDJYoNJ1\np1jeuqswlxo144oMO92cmdS2dAbPvS6aQP1I85Q2NniY+6YhHkBwIQIlfVs1JPbY\nX7QtTy1IXQhR3sospyvUwY2GPSAeVHDRL53ClQKDsvWpSy0MAmWYJkZu1P+jKBim\nj34ytApgG65Hv/RHf3L4+4zzItZ3TN2tJ/g9EKc6oMNtqKbbG56kkmvRPWKtMGV8\nFqxCvG5NydUK7fN+P2WJAoIBAQDXLFC//Fn9ed1U+pKa2M25aJwEetkGLXQvkwVi\n8uJFaXITb2ceveSEo6iBExyn4eYL5A4X+RZdJJdRRbj4whsNN13Pm+6lYX3pp7MN\nO+78uvwVfKZiWPFKfZs7ZH1/O9VIlLGnXUHeaHK1tmv9ixxMixdnjUDkcVa0O3qT\nKBLpvXnVEMYizxQBN0P5Z9QvQQGpUhKnNw+FhV1SP+YHxrB0Pu6qbYAmZZC2MQc1\nTsDyqGjmHk9VJaFYAAPEjqACDbfnkVUCj0ylM4xPQuBJs9DOKh4InG+znusdmd8H\nmvoEFDppsrH1NhO6GTeuCk6n0WBi6cUm76K/gPscYyV4ZtkfAoIBAQDNQgDXtfqv\nxbAhvDk0o/P8fqOdgQF0uFTqYHmyW31Ty9nF0ptA8LVJOIljU3zlLplhIFjBnSEG\nLqu4jnLLRR+zej0MXmJuZ9BMWmQeTrZzttnH5bn54E07DPJ5BvFoTMJNklBiXjB5\n5hTPZS4yK1KjoxY+Ypnj4W1iZjP37ya/A34J2nlYtoW4LdVfJHqCxBXel9Nz2zkv\nvwwPu8Eu7gFLuhNQM6Iv4mORGI8yg7Y/BwodfDPRuFvrG1KXkjwASb0O5b1suRQy\n9H80q5EAbT36K1z48ilr8fcroN+hV8g4yntrBBgOHPMmBk/vHKU8B1rkBr0p2haI\n3PwKmDFRsDInAoIBAGrjjMmSZnHQk+6e+y0I/klYegiPrjevZMQtWMOqvFSW6SBW\nevd+hYKOeiqEf/u18D1/8LBgAIgMoU6yQAzy/9U059k2MPrez1m/AOdWGoZZrNhP\nr6ezX0oN04tRhDYsVutTUl09qnb9k95I3KR68nfjsKC0PsQ8uUGXOnDXu215vofl\naUfpbpqcBZxjw7glptmh97oxU/iUI6O0MmUygn18tbrb4okwcw7OlDIbCSaCGnoW\nHHrD0r6QY07FOx9KCU1zmLNI1F5MmSrWoex68wM3UOweKi8khs+RnIV+qyxTkCDp\nsBWL44jS9iHy5Nfg3uzEDDgnWsWfIR8c8YQ6MykCggEADr0ollTI9Yo6hZGggfkr\n8fueABddZWY/Ir1ev8H2E+hVcPEYmOcv/VwD8Y/zLfnUpbbO6MhBsNH1HsGL2LDT\n/+1NKPA2HTtzJ6ht/Acm7tQ4ezQx0JGcuhrJ5orrFtQ8N5nED+w3iulMoT/gu1WF\nD58MX9pwtn5ffmtcW/deTuUPTeHUSNyCaaFQ6w4RhgZSk7NPSch6KMWNNiwDST1p\n9mgcLuwmP04AXFDpJ3VxxsDYpxleFzcn0pAZtCyaBmNFIia5HW+E1cvcvol7Vg6C\nHs6yVGX/N3MejpF0vX8yL3HKvvqCR7EofJiDcOYbr13P1wPs3W59o8JKjvAyymze\njQKCAQAUY/0asRL33D7tFoIbLg/N9hi+tCCM35DMf2FeXm3QwSkAR/BJw0ewCE5C\n+VqukHN3/i0Xe8KSHwEuLK2sGLk9Ys8A5NytjqFApYwpIk8UrRONfC12H3ez5VYk\nJlhMVhVXEZvVhEFJiBC7q6x6s7BVtLTGV7FA5CW8YKBhwHwrpm+h/Xb798oaKyel\nP/xYq+GZzfWfbvUjZvgN0J0RGxKA+GRgsmhoyOfgCVXgSzuUkI+9cAUvC0OV407L\n4XIK0GDJ7Tv/2USSPfmueyGEmacc/oYUPVBUgeINSoaCM4cpZwyLylVEtKOdQoEE\n77G5mvQsoXxsMjd+nbHil450UHsL\n-----END PRIVATE KEY-----\n'})

TASK [Remote Install] *************************************************************************************************************************
Wednesday 05 February 2025  23:36:04 +0000 (0:00:05.754)       0:05:29.229 ****

TASK [remote/remote-install : Check if the subcloud deployed but failed] **********************************************************************
Wednesday 05 February 2025  23:36:04 +0000 (0:00:00.076)       0:05:29.305 ****
fatal: [welktxsr-931883-rz-le0gls6-014 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)]: FAILED! => changed=true
  cmd: |-
    . /etc/platform/openrc
    dcmanager subcloud show welktxsr-d931883-014 --column "deploy_status" --format value
  delta: '0:00:03.728440'
  end: '2025-02-05 23:36:09.915768'
  msg: non-zero return code
  rc: 1
  start: '2025-02-05 23:36:06.187328'
  stderr: ERROR (app) The resource could not be found. Subcloud not found
  stderr_lines: <omitted>
  stdout: ''
  stdout_lines: <omitted>
...ignoring

TASK [remote/remote-install : debug] **********************************************************************************************************
Wednesday 05 February 2025  23:36:10 +0000 (0:00:05.888)       0:05:35.193 ****
ok: [welktxsr-931883-rz-le0gls6-014] =>
  msg: 'subcloud_status:'

TASK [remote/remote-install : Delete the subcloud that is in failed state] ********************************************************************
Wednesday 05 February 2025  23:36:10 +0000 (0:00:00.022)       0:05:35.216 ****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : include_tasks] **************************************************************************************************
Wednesday 05 February 2025  23:36:10 +0000 (0:00:00.021)       0:05:35.237 ****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : Deploy remote cloud - subcloud version same as CC's] ************************************************************
Wednesday 05 February 2025  23:36:10 +0000 (0:00:00.023)       0:05:35.261 ****
[WARNING]: Collection ansible.netcommon does not support Ansible version 2.13.7
[WARNING]: Collection ansible.utils does not support Ansible version 2.13.7
changed: [welktxsr-931883-rz-le0gls6-014 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)]

TASK [remote/remote-install : Deploy remote cloud - subcloud version is CC's - 1] *************************************************************
Wednesday 05 February 2025  23:36:17 +0000 (0:00:06.871)       0:05:42.132 ****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : 1st polling prep: Obtain Keystone auth token] *******************************************************************
Wednesday 05 February 2025  23:36:17 +0000 (0:00:00.019)       0:05:42.152 ****
ok: [welktxsr-931883-rz-le0gls6-014 -> localhost]

TASK [remote/remote-install : 1st polling: Wait for subcloud to start installing OS] **********************************************************
Wednesday 05 February 2025  23:36:18 +0000 (0:00:01.021)       0:05:43.174 ****
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 1st polling: Wait for subcloud to start installing OS (40 retries left).
ok: [welktxsr-931883-rz-le0gls6-014 -> localhost]

TASK [remote/remote-install : 1st polling result: Fail if the installation failed] ************************************************************
Wednesday 05 February 2025  23:36:49 +0000 (0:00:30.894)       0:06:14.068 ****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : 2nd polling prep: Obtain Keystone auth token] *******************************************************************
Wednesday 05 February 2025  23:36:49 +0000 (0:00:00.023)       0:06:14.092 ****
ok: [welktxsr-931883-rz-le0gls6-014 -> localhost]

TASK [remote/remote-install : 2nd polling: Wait for subcloud to install OS (this will take a while)] ******************************************
Wednesday 05 February 2025  23:36:49 +0000 (0:00:00.876)       0:06:14.968 ****
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (100 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (100 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (99 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (98 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (97 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (96 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (95 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (94 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (93 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (92 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (91 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (90 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (89 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (88 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (87 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (86 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (85 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (84 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (83 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (82 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (81 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (80 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (79 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (78 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (77 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 2nd polling: Wait for subcloud to install OS (this will take a while) (76 retries left).
ok: [welktxsr-931883-rz-le0gls6-014 -> localhost]

TASK [remote/remote-install : 2nd polling result: Fail if any error occurred] *****************************************************************
Wednesday 05 February 2025  23:49:29 +0000 (0:12:39.271)       0:18:54.240 ****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : include_tasks] **************************************************************************************************
Wednesday 05 February 2025  23:49:29 +0000 (0:00:00.021)       0:18:54.262 ****
included: /home/szabota/playbooks/wr-installer-atlas-me/roles/remote/remote-install/tasks/set-time.yaml for welktxsr-931883-rz-le0gls6-014

TASK [remote/remote-install : Test if remote host is pingable] ********************************************************************************
Wednesday 05 February 2025  23:49:29 +0000 (0:00:00.028)       0:18:54.290 ****
changed: [welktxsr-931883-rz-le0gls6-014 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)]

TASK [remote/remote-install : Get subcloud system time] ***************************************************************************************
Wednesday 05 February 2025  23:49:31 +0000 (0:00:02.197)       0:18:56.488 ****
changed: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : Print subcloud system time] *************************************************************************************
Wednesday 05 February 2025  23:49:33 +0000 (0:00:01.912)       0:18:58.401 ****
ok: [welktxsr-931883-rz-le0gls6-014] =>
  msg: 'subcloud system time: Wed 05 Feb 2025 11:47:10 PM UTC'

TASK [remote/remote-install : Stop NTP service] ***********************************************************************************************
Wednesday 05 February 2025  23:49:33 +0000 (0:00:00.026)       0:18:58.427 ****
fatal: [welktxsr-931883-rz-le0gls6-014]: FAILED! => changed=false
  msg: 'Could not find the requested service ntpd: host'
...ignoring

TASK [remote/remote-install : Get central controller system time] *****************************************************************************
Wednesday 05 February 2025  23:49:35 +0000 (0:00:01.814)       0:19:00.242 ****
changed: [welktxsr-931883-rz-le0gls6-014 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)]

TASK [remote/remote-install : Print central controller system time] ***************************************************************************
Wednesday 05 February 2025  23:49:37 +0000 (0:00:02.211)       0:19:02.453 ****
ok: [welktxsr-931883-rz-le0gls6-014] =>
  msg: 'central system time: Wed 05 Feb 2025 11:49:37 PM UTC'

TASK [remote/remote-install : Set subcloud system time by central controller system time] *****************************************************
Wednesday 05 February 2025  23:49:37 +0000 (0:00:00.025)       0:19:02.479 ****
changed: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : Set subcloud system time by NTP server] *************************************************************************
Wednesday 05 February 2025  23:49:38 +0000 (0:00:01.471)       0:19:03.950 ****
changed: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : Start NTP service] **********************************************************************************************
Wednesday 05 February 2025  23:49:46 +0000 (0:00:07.620)       0:19:11.571 ****
fatal: [welktxsr-931883-rz-le0gls6-014]: FAILED! => changed=false
  msg: 'Could not find the requested service ntpd: host'
...ignoring

TASK [remote/remote-install : Sync system time to RT clock after adjustment] ******************************************************************
Wednesday 05 February 2025  23:49:48 +0000 (0:00:01.612)       0:19:13.183 ****
changed: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : Get subcloud system time after adjustment] **********************************************************************
Wednesday 05 February 2025  23:49:49 +0000 (0:00:01.569)       0:19:14.753 ****
changed: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : Print subcloud system time after adjustment] ********************************************************************
Wednesday 05 February 2025  23:49:51 +0000 (0:00:01.448)       0:19:16.201 ****
ok: [welktxsr-931883-rz-le0gls6-014] =>
  msg: 'subcloud system time after adjustment: Wed 05 Feb 2025 11:49:50 PM UTC'

TASK [remote/remote-install : Set variable time_is_set to true so this code will not be executed again] ***************************************
Wednesday 05 February 2025  23:49:51 +0000 (0:00:00.026)       0:19:16.228 ****
ok: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : 3rd polling prep: Obtain Keystone auth token] *******************************************************************
Wednesday 05 February 2025  23:49:51 +0000 (0:00:00.027)       0:19:16.255 ****
ok: [welktxsr-931883-rz-le0gls6-014 -> localhost]

TASK [remote/remote-install : 3rd polling: Wait for subcloud to install OS (this may take a while)] *******************************************
Wednesday 05 February 2025  23:49:52 +0000 (0:00:00.862)       0:19:17.118 ****
ok: [welktxsr-931883-rz-le0gls6-014 -> localhost]

TASK [remote/remote-install : 3rd polling result: Fail if any error occurred] *****************************************************************
Wednesday 05 February 2025  23:49:52 +0000 (0:00:00.481)       0:19:17.600 ****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : include_tasks] **************************************************************************************************
Wednesday 05 February 2025  23:49:52 +0000 (0:00:00.020)       0:19:17.620 ****
included: /home/szabota/playbooks/wr-installer-atlas-me/roles/remote/remote-install/tasks/set-time.yaml for welktxsr-931883-rz-le0gls6-014

TASK [remote/remote-install : Test if remote host is pingable] ********************************************************************************
Wednesday 05 February 2025  23:49:52 +0000 (0:00:00.030)       0:19:17.651 ****
changed: [welktxsr-931883-rz-le0gls6-014 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)]

TASK [remote/remote-install : Get subcloud system time] ***************************************************************************************
Wednesday 05 February 2025  23:49:54 +0000 (0:00:02.158)       0:19:19.809 ****
changed: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : Print subcloud system time] *************************************************************************************
Wednesday 05 February 2025  23:49:56 +0000 (0:00:01.453)       0:19:21.263 ****
ok: [welktxsr-931883-rz-le0gls6-014] =>
  msg: 'subcloud system time: Wed 05 Feb 2025 11:49:56 PM UTC'

TASK [remote/remote-install : Stop NTP service] ***********************************************************************************************
Wednesday 05 February 2025  23:49:56 +0000 (0:00:00.030)       0:19:21.293 ****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : Get central controller system time] *****************************************************************************
Wednesday 05 February 2025  23:49:56 +0000 (0:00:00.020)       0:19:21.314 ****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : Print central controller system time] ***************************************************************************
Wednesday 05 February 2025  23:49:56 +0000 (0:00:00.017)       0:19:21.331 ****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : Set subcloud system time by central controller system time] *****************************************************
Wednesday 05 February 2025  23:49:56 +0000 (0:00:00.016)       0:19:21.348 ****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : Set subcloud system time by NTP server] *************************************************************************
Wednesday 05 February 2025  23:49:56 +0000 (0:00:00.016)       0:19:21.365 ****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : Start NTP service] **********************************************************************************************
Wednesday 05 February 2025  23:49:56 +0000 (0:00:00.016)       0:19:21.381 ****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : Sync system time to RT clock after adjustment] ******************************************************************
Wednesday 05 February 2025  23:49:56 +0000 (0:00:00.015)       0:19:21.397 ****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : Get subcloud system time after adjustment] **********************************************************************
Wednesday 05 February 2025  23:49:56 +0000 (0:00:00.015)       0:19:21.413 ****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : Print subcloud system time after adjustment] ********************************************************************
Wednesday 05 February 2025  23:49:56 +0000 (0:00:00.016)       0:19:21.429 ****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : Set variable time_is_set to true so this code will not be executed again] ***************************************
Wednesday 05 February 2025  23:49:56 +0000 (0:00:00.015)       0:19:21.444 ****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : 4th polling prep: Obtain Keystone auth token] *******************************************************************
Wednesday 05 February 2025  23:49:56 +0000 (0:00:00.016)       0:19:21.461 ****
ok: [welktxsr-931883-rz-le0gls6-014 -> localhost]

TASK [remote/remote-install : 4th polling: Wait for subcloud to install OS (this may still take a while)] *************************************
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (100 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (99 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (98 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (97 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (96 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (95 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (94 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (93 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (92 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (91 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (90 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (89 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (88 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (87 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (86 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (85 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (84 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (83 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (82 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (81 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (80 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (79 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (78 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (77 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (76 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (75 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (74 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (73 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (72 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (71 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (70 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (69 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (68 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (67 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (66 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (65 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (64 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (63 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (62 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (61 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (60 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (59 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (58 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (57 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (56 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (55 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (54 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (53 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (52 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (51 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (50 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (49 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (48 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (47 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (46 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (45 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (44 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (43 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (42 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (41 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (40 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (39 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (38 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> localhost]: 4th polling: Wait for subcloud to install OS (this may still take a while) (37 retries left).
ok: [welktxsr-931883-rz-le0gls6-014 -> localhost]

TASK [remote/remote-install : 4th polling result: Fail if the installation failed] ************************************************************
Thursday 06 February 2025  00:30:56 +0000 (0:40:58.753)       1:00:21.154 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : include_tasks] **************************************************************************************************
Thursday 06 February 2025  00:30:56 +0000 (0:00:00.022)       1:00:21.176 *****
included: /home/szabota/playbooks/wr-installer-atlas-me/roles/remote/remote-install/tasks/set-time.yaml for welktxsr-931883-rz-le0gls6-014

TASK [remote/remote-install : Test if remote host is pingable] ********************************************************************************
Thursday 06 February 2025  00:30:56 +0000 (0:00:00.061)       1:00:21.237 *****
changed: [welktxsr-931883-rz-le0gls6-014 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)]

TASK [remote/remote-install : Get subcloud system time] ***************************************************************************************
Thursday 06 February 2025  00:30:58 +0000 (0:00:02.168)       1:00:23.405 *****
changed: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : Print subcloud system time] *************************************************************************************
Thursday 06 February 2025  00:30:59 +0000 (0:00:01.436)       1:00:24.842 *****
ok: [welktxsr-931883-rz-le0gls6-014] =>
  msg: 'subcloud system time: Thu 06 Feb 2025 12:30:59 AM UTC'

TASK [remote/remote-install : Stop NTP service] ***********************************************************************************************
Thursday 06 February 2025  00:30:59 +0000 (0:00:00.025)       1:00:24.868 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : Get central controller system time] *****************************************************************************
Thursday 06 February 2025  00:30:59 +0000 (0:00:00.019)       1:00:24.887 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : Print central controller system time] ***************************************************************************
Thursday 06 February 2025  00:30:59 +0000 (0:00:00.016)       1:00:24.903 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : Set subcloud system time by central controller system time] *****************************************************
Thursday 06 February 2025  00:30:59 +0000 (0:00:00.016)       1:00:24.919 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : Set subcloud system time by NTP server] *************************************************************************
Thursday 06 February 2025  00:30:59 +0000 (0:00:00.016)       1:00:24.936 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : Start NTP service] **********************************************************************************************
Thursday 06 February 2025  00:30:59 +0000 (0:00:00.015)       1:00:24.951 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : Sync system time to RT clock after adjustment] ******************************************************************
Thursday 06 February 2025  00:30:59 +0000 (0:00:00.015)       1:00:24.967 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : Get subcloud system time after adjustment] **********************************************************************
Thursday 06 February 2025  00:30:59 +0000 (0:00:00.015)       1:00:24.983 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : Print subcloud system time after adjustment] ********************************************************************
Thursday 06 February 2025  00:30:59 +0000 (0:00:00.015)       1:00:24.998 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : Set variable time_is_set to true so this code will not be executed again] ***************************************
Thursday 06 February 2025  00:30:59 +0000 (0:00:00.016)       1:00:25.015 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : 5th polling prep: Obtain Keystone auth token] *******************************************************************
Thursday 06 February 2025  00:30:59 +0000 (0:00:00.016)       1:00:25.031 *****
ok: [welktxsr-931883-rz-le0gls6-014 -> localhost]

TASK [remote/remote-install : 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while)] ************************
Thursday 06 February 2025  00:31:00 +0000 (0:00:00.891)       1:00:25.923 *****
ok: [welktxsr-931883-rz-le0gls6-014 -> localhost]

TASK [remote/remote-install : 5th polling result: Fail if install/bootstrap/deploy failed] ****************************************************
Thursday 06 February 2025  00:31:01 +0000 (0:00:00.457)       1:00:26.381 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : include_tasks] **************************************************************************************************
Thursday 06 February 2025  00:31:01 +0000 (0:00:00.021)       1:00:26.402 *****
included: /home/szabota/playbooks/wr-installer-atlas-me/roles/remote/remote-install/tasks/set-time.yaml for welktxsr-931883-rz-le0gls6-014

TASK [remote/remote-install : Test if remote host is pingable] ********************************************************************************
Thursday 06 February 2025  00:31:01 +0000 (0:00:00.037)       1:00:26.440 *****
changed: [welktxsr-931883-rz-le0gls6-014 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)]

TASK [remote/remote-install : Get subcloud system time] ***************************************************************************************
Thursday 06 February 2025  00:31:03 +0000 (0:00:02.174)       1:00:28.615 *****
changed: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : Print subcloud system time] *************************************************************************************
Thursday 06 February 2025  00:31:05 +0000 (0:00:01.444)       1:00:30.059 *****
ok: [welktxsr-931883-rz-le0gls6-014] =>
  msg: 'subcloud system time: Thu 06 Feb 2025 12:31:04 AM UTC'

TASK [remote/remote-install : Stop NTP service] ***********************************************************************************************
Thursday 06 February 2025  00:31:05 +0000 (0:00:00.026)       1:00:30.086 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : Get central controller system time] *****************************************************************************
Thursday 06 February 2025  00:31:05 +0000 (0:00:00.019)       1:00:30.105 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : Print central controller system time] ***************************************************************************
Thursday 06 February 2025  00:31:05 +0000 (0:00:00.021)       1:00:30.127 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : Set subcloud system time by central controller system time] *****************************************************
Thursday 06 February 2025  00:31:05 +0000 (0:00:00.018)       1:00:30.145 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : Set subcloud system time by NTP server] *************************************************************************
Thursday 06 February 2025  00:31:05 +0000 (0:00:00.015)       1:00:30.161 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : Start NTP service] **********************************************************************************************
Thursday 06 February 2025  00:31:05 +0000 (0:00:00.016)       1:00:30.178 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : Sync system time to RT clock after adjustment] ******************************************************************
Thursday 06 February 2025  00:31:05 +0000 (0:00:00.016)       1:00:30.194 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : Get subcloud system time after adjustment] **********************************************************************
Thursday 06 February 2025  00:31:05 +0000 (0:00:00.015)       1:00:30.209 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : Print subcloud system time after adjustment] ********************************************************************
Thursday 06 February 2025  00:31:05 +0000 (0:00:00.018)       1:00:30.227 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : Set variable time_is_set to true so this code will not be executed again] ***************************************
Thursday 06 February 2025  00:31:05 +0000 (0:00:00.016)       1:00:30.243 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : 6th polling prep: Obtain Keystone auth token] *******************************************************************
Thursday 06 February 2025  00:31:05 +0000 (0:00:00.017)       1:00:30.260 *****
ok: [welktxsr-931883-rz-le0gls6-014 -> localhost]

TASK [remote/remote-install : 6th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while)] ************************
Thursday 06 February 2025  00:31:06 +0000 (0:00:00.878)       1:00:31.139 *****
ok: [welktxsr-931883-rz-le0gls6-014 -> localhost]

TASK [remote/remote-install : include_tasks] **************************************************************************************************
Thursday 06 February 2025  00:31:06 +0000 (0:00:00.491)       1:00:31.630 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : 6th polling result: Fail if bootstrap/deploy failed] ************************************************************
Thursday 06 February 2025  00:31:06 +0000 (0:00:00.022)       1:00:31.653 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : include_tasks] **************************************************************************************************
Thursday 06 February 2025  00:31:06 +0000 (0:00:00.020)       1:00:31.674 *****
included: /home/szabota/playbooks/wr-installer-atlas-me/roles/remote/remote-install/tasks/set-time.yaml for welktxsr-931883-rz-le0gls6-014

TASK [remote/remote-install : Test if remote host is pingable] ********************************************************************************
Thursday 06 February 2025  00:31:06 +0000 (0:00:00.042)       1:00:31.716 *****
changed: [welktxsr-931883-rz-le0gls6-014 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)]

TASK [remote/remote-install : Get subcloud system time] ***************************************************************************************
Thursday 06 February 2025  00:31:08 +0000 (0:00:02.198)       1:00:33.914 *****
changed: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : Print subcloud system time] *************************************************************************************
Thursday 06 February 2025  00:31:10 +0000 (0:00:01.534)       1:00:35.449 *****
ok: [welktxsr-931883-rz-le0gls6-014] =>
  msg: 'subcloud system time: Thu 06 Feb 2025 12:31:10 AM UTC'

TASK [remote/remote-install : Stop NTP service] ***********************************************************************************************
Thursday 06 February 2025  00:31:10 +0000 (0:00:00.034)       1:00:35.483 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : Get central controller system time] *****************************************************************************
Thursday 06 February 2025  00:31:10 +0000 (0:00:00.021)       1:00:35.505 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : Print central controller system time] ***************************************************************************
Thursday 06 February 2025  00:31:10 +0000 (0:00:00.017)       1:00:35.522 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : Set subcloud system time by central controller system time] *****************************************************
Thursday 06 February 2025  00:31:10 +0000 (0:00:00.016)       1:00:35.538 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : Set subcloud system time by NTP server] *************************************************************************
Thursday 06 February 2025  00:31:10 +0000 (0:00:00.016)       1:00:35.555 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : Start NTP service] **********************************************************************************************
Thursday 06 February 2025  00:31:10 +0000 (0:00:00.016)       1:00:35.571 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : Sync system time to RT clock after adjustment] ******************************************************************
Thursday 06 February 2025  00:31:10 +0000 (0:00:00.015)       1:00:35.586 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : Get subcloud system time after adjustment] **********************************************************************
Thursday 06 February 2025  00:31:10 +0000 (0:00:00.017)       1:00:35.604 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : Print subcloud system time after adjustment] ********************************************************************
Thursday 06 February 2025  00:31:10 +0000 (0:00:00.015)       1:00:35.620 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : Set variable time_is_set to true so this code will not be executed again] ***************************************
Thursday 06 February 2025  00:31:10 +0000 (0:00:00.016)       1:00:35.636 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : Wait for controller-0 restart] **********************************************************************************
Thursday 06 February 2025  00:31:10 +0000 (0:00:00.016)       1:00:35.653 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : Wait for controller-0 recovery] *********************************************************************************
Thursday 06 February 2025  00:31:10 +0000 (0:00:00.020)       1:00:35.674 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/remote-install : setup kdump] ****************************************************************************************************
Thursday 06 February 2025  00:31:10 +0000 (0:00:00.018)       1:00:35.692 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [Wait for hosts and system to be reconciled] *********************************************************************************************
Thursday 06 February 2025  00:31:10 +0000 (0:00:00.019)       1:00:35.712 *****

TASK [common/wait_for_reconciliation : Making sure node is reachable] *************************************************************************
Thursday 06 February 2025  00:31:10 +0000 (0:00:00.031)       1:00:35.743 *****
ok: [welktxsr-931883-rz-le0gls6-014]

TASK [common/wait_for_reconciliation : Wait for K8s API to be up] *****************************************************************************
Thursday 06 February 2025  00:31:12 +0000 (0:00:01.578)       1:00:37.322 *****
ok: [welktxsr-931883-rz-le0gls6-014]

TASK [common/wait_for_reconciliation : Wait for all 3 hosts to show up] ***********************************************************************
Thursday 06 February 2025  00:31:13 +0000 (0:00:01.592)       1:00:38.915 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [common/wait_for_reconciliation : Wait for hosts to be reconciled] ***********************************************************************
Thursday 06 February 2025  00:31:13 +0000 (0:00:00.025)       1:00:38.940 *****
changed: [welktxsr-931883-rz-le0gls6-014]

TASK [common/wait_for_reconciliation : Wait for systems to be reconciled] *********************************************************************
Thursday 06 February 2025  00:31:15 +0000 (0:00:01.515)       1:00:40.456 *****
changed: [welktxsr-931883-rz-le0gls6-014]

TASK [Remote Manage] **************************************************************************************************************************
Thursday 06 February 2025  00:31:16 +0000 (0:00:01.508)       1:00:41.964 *****

TASK [remote/manage : 1st Obtain Keystone auth token] *****************************************************************************************
Thursday 06 February 2025  00:31:16 +0000 (0:00:00.067)       1:00:42.032 *****
ok: [welktxsr-931883-rz-le0gls6-014 -> localhost]

TASK [remote/manage : 1st Wait for contoller-0 availability status online] ********************************************************************
Thursday 06 February 2025  00:31:17 +0000 (0:00:00.858)       1:00:42.891 *****
ok: [welktxsr-931883-rz-le0gls6-014 -> localhost]

TASK [remote/manage : 2nd Obtain Keystone auth token] *****************************************************************************************
Thursday 06 February 2025  00:31:18 +0000 (0:00:00.468)       1:00:43.359 *****
ok: [welktxsr-931883-rz-le0gls6-014 -> localhost]

TASK [remote/manage : 2nd Wait for contoller-0 availability status online] ********************************************************************
Thursday 06 February 2025  00:31:19 +0000 (0:00:00.859)       1:00:44.218 *****
ok: [welktxsr-931883-rz-le0gls6-014 -> localhost]

TASK [remote/manage : Wait for system to stabilize before running kubectl] ********************************************************************
Thursday 06 February 2025  00:31:19 +0000 (0:00:00.482)       1:00:44.700 *****
Pausing for 480 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [welktxsr-931883-rz-le0gls6-014]

TASK [Wait for system and hosts to be reconciled] *********************************************************************************************
Thursday 06 February 2025  00:39:19 +0000 (0:08:00.021)       1:08:44.721 *****

TASK [common/wait_for_reconciliation : Making sure node is reachable] *************************************************************************
Thursday 06 February 2025  00:39:19 +0000 (0:00:00.029)       1:08:44.751 *****
ok: [welktxsr-931883-rz-le0gls6-014]

TASK [common/wait_for_reconciliation : Wait for K8s API to be up] *****************************************************************************
Thursday 06 February 2025  00:39:21 +0000 (0:00:01.430)       1:08:46.181 *****
ok: [welktxsr-931883-rz-le0gls6-014]

TASK [common/wait_for_reconciliation : Wait for all 3 hosts to show up] ***********************************************************************
Thursday 06 February 2025  00:39:22 +0000 (0:00:01.448)       1:08:47.629 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [common/wait_for_reconciliation : Wait for hosts to be reconciled] ***********************************************************************
Thursday 06 February 2025  00:39:22 +0000 (0:00:00.019)       1:08:47.648 *****
changed: [welktxsr-931883-rz-le0gls6-014]

TASK [common/wait_for_reconciliation : Wait for systems to be reconciled] *********************************************************************
Thursday 06 February 2025  00:39:24 +0000 (0:00:01.480)       1:08:49.129 *****
changed: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/manage : Wait for distributed cloud to be reconciled but subcloud OAM VIP becomes unreachable] ***********************************
Thursday 06 February 2025  00:39:25 +0000 (0:00:01.474)       1:08:50.604 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/manage : Check if the subcloud deployed but failed] ******************************************************************************
Thursday 06 February 2025  00:39:25 +0000 (0:00:00.026)       1:08:50.631 *****
changed: [welktxsr-931883-rz-le0gls6-014 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)]

TASK [remote/manage : Set distributed cloud state to managed] *********************************************************************************
Thursday 06 February 2025  00:39:31 +0000 (0:00:05.928)       1:08:56.560 *****
changed: [welktxsr-931883-rz-le0gls6-014 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)]

TASK [remote/manage : Wait for system to stabilize] *******************************************************************************************
Thursday 06 February 2025  00:39:37 +0000 (0:00:06.010)       1:09:02.570 *****
Pausing for 300 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [welktxsr-931883-rz-le0gls6-014]

TASK [Remote Trust] ***************************************************************************************************************************
Thursday 06 February 2025  00:44:37 +0000 (0:05:00.022)       1:14:02.593 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [Remote Starlingx] ***********************************************************************************************************************
Thursday 06 February 2025  00:44:37 +0000 (0:00:00.024)       1:14:02.617 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [Remote Starlingx and Registry] **********************************************************************************************************
Thursday 06 February 2025  00:44:37 +0000 (0:00:00.021)       1:14:02.639 *****

TASK [remote/starlingx : Copy ICA cert] *******************************************************************************************************
Thursday 06 February 2025  00:44:37 +0000 (0:00:00.077)       1:14:02.717 *****
changed: [welktxsr-931883-rz-le0gls6-014] => (item={'filename': 'vz_root_ica_cert.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIFNzCCAx+gAwIBAgIUGLJR/hP48n+vdq2v1hcfspXo/78wDQYJKoZIhvcNAQEL\nBQAwWjELMAkGA1UEBhMCVVMxEDAOBgNVBAoMB1Zlcml6b24xEzARBgNVBAsMClZa\nSUFNIFRlc3QxJDAiBgNVBAMMG1Zlcml6b24gTmV0d29yayBSU0EgQ0EgVGVzdDAe\nFw0yMDEwMjIyMTE0MDNaFw0zMDEwMjIyMTE0MDNaMIGRMQswCQYDVQQGEwJVUzEL\nMAkGA1UECAwCVFgxETAPBgNVBAcMCFdlc3RsYWtlMRAwDgYDVQQKDAdWZXJpem9u\nMR0wGwYDVQQLDBRWZXJpem9uIFNvdXJjaW5nIExMQzExMC8GA1UEAwwoVmVyaXpv\nbiBOZXR3b3JrIFdFTEtUWElCIExBQiAxIDMgUlNBIElDQTCCASIwDQYJKoZIhvcN\nAQEBBQADggEPADCCAQoCggEBANhkGTXOCKEYf5znDDeX3n/DHFPVqazgQsr0/SIG\n4eb1JY5q5Jq3ZhAaZCr9HJuCkwAP/zgYH0llqOvf8AC2Uh+7z1b33IbwxPmJfWCP\nAqSNFkLWWVRdbELapCu408QsrLMW8IrdP6PLiKAepwncfm4T0/6bANqIEmUkpw8Q\nxProeiNwlGbwUll+tELmdCk7vA7hKX3j1kUvS5Z84Z5ivJBWEcUEggmC97TK4aLo\nFVEHbyahze568JVEaM1vY5L4mnRRTl+u5ipaSMxVBsiXzF7eFuKCzqF7wxbDIt2T\nIFEJtwyJDW5bXjyXgiF1d5H/URprUcRV9Qmf2+PXcfwHII8CAwEAAaOBvDCBuTAS\nBgNVHRMBAf8ECDAGAQH/AgEAMA4GA1UdDwEB/wQEAwIBBjAfBgNVHSMEGDAWgBQl\neng3lqGBeTrbLVuABoEmUHm1+TBTBgNVHR8ETDBKMEigRqBEhkJodHRwOi8vc2Vj\ndXJlLnN0YWdpbmcuc2VjdXJpdHljcmVkZW50aWFsaW5nLmNvbS9jcmwvdnpuZXRy\nc2FjYS5jcmwwHQYDVR0OBBYEFP0Z+/vaDLtAoFig1I9ttNKnmzByMA0GCSqGSIb3\nDQEBCwUAA4ICAQBuXVTf9e01HeymHgRcFCwP2N6G6u+vIzY8Bz0zSUZeRDHMZQcS\nNoabDyn5FfGJlw4BqGC591Sp0/unFQDzAg17rDBcrgwajeFeUiFdb9PiAJwHaX9S\nvq/7VmVLCmpeb+a/laXAe6+tkY1kcFrd1+ItRKC6ZGXMsoDkmk5Ndxxgw77estcI\nMiiLQbvpXRygX5wD4/ayazuLms9qITZkOZ1nTLVqq7QrwYCsSoih7hj6sbsfXr19\nGoYWmk8Y7O/d3ttgyHuRH9k/2dQ/xL7avRpMNkPdr7ocJqI46hvx2X6UyOo7IBua\nkSkFbSmPZWIVAidNMBOnvffCQ32tfjT2/xso/a9cdskvxqgLi0MPARU9Nl2Pufsb\nD7l4/sBvz/PiNTKp+Daa9FdyLb9ySidos1uS0c24bUtY1RXXGAVV2qgfyrzvzfye\nSM+w16hMU/yeYiuA1jsPmsnZnuIJj4Nv8ZjjZ0WS53pP5wcghaHkBrqWQNT8meqA\nVElrMBPlYq67T+AXP0B9lf5Sc3QVIio7XKKfqrlcQxY2JGLEyE53JgZGX7dpwU4I\nukLvyHbT4p06oY3qG6+wH8+YIXCNAYtadJ/C5/u9GcLX5NnZrcuduj0inw2/a3Ao\nWgCt6/Pr28BkCvkWdDt9d8Z40qeu1aZdcr157mR+yZGPfBfB2vasrNIEwQ==\n-----END CERTIFICATE-----\n'})
changed: [welktxsr-931883-rz-le0gls6-014] => (item={'filename': 'vz_root_ica_key.pem', 'value': '-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA2GQZNc4IoRh/nOcMN5fef8McU9WprOBCyvT9Igbh5vUljmrk\nmrdmEBpkKv0cm4KTAA//OBgfSWWo69/wALZSH7vPVvfchvDE+Yl9YI8CpI0WQtZZ\nVF1sQtqkK7jTxCyssxbwit0/o8uIoB6nCdx+bhPT/psA2ogSZSSnDxDE+uh6I3CU\nZvBSWX60QuZ0KTu8DuEpfePWRS9LlnzhnmK8kFYRxQSCCYL3tMrhougVUQdvJqHN\n7nrwlURozW9jkviadFFOX67mKlpIzFUGyJfMXt4W4oLOoXvDFsMi3ZMgUQm3DIkN\nbltePJeCIXV3kf9RGmtRxFX1CZ/b49dx/AcgjwIDAQABAoIBABSd1NkPfDr8/ouQ\nZ9WUHprFmBlUrgnOhA6aMNPhG/zJNn7PKGClQJAgM5L08pjOY/sJiyNpCPIRQXrX\npyIqPMDRP/vlOZmRrvKnas6cUYAkAQ71JSWokPv9oM6ZmXODXiDh+qEAW2PbrHS0\n9u01mMYcFYKYeghYFoiUaWZCDsJo3v3dgeE9aQ4tB9ksovSmWrpuCY7NKbd7Qrbo\n5XxQhkujTkE6knOHz8CVwYETtj8LZ/bvHIkGMGvRvwsKYDZkIKr5CZ7DX+KcMfPN\neMZU4VCHYSXNxsyp5DJ1Zw+gx8/32kUL0CzJLLam1G021Hq41KPwwSV/KPrOKel7\nHXDLXeECgYEA8MR+lgxGjYTc/k4TdZvcFVgqHGLXnyjO7ZVt4b7UpwmayLuoSD/M\nOpHQYX+JBIIWTNlGhG8UV3DPC3v+auhYa7twwbekS30IYCAmu5GCKgMAcWFinz6A\nYZxG55P/hShetCyOqikgwXqzMlwGs8KEul8f8BKssROzUy8mIlFhjq0CgYEA5hTM\nSNxAD3dlRtb0771fBU7fjx8JPfjptP9vP/JVEelkc/ti9nZ5buTC+9cQC/B+YFx7\nc82uCrXV13bGR9iH8xBhwU7JOYJZbgCpwp0F56wIN5Pdk9Eo79Batrw3oGBG4Yvt\nDc2eltxQbHgObc/qygf88j9XqD8aGIvQrc4Jf6sCgYAtxX03M1A6WTbWFau3YRD+\n8crXqKbLOCvWmODR2MB+nOHTJXHBgndl7xCJaIB43e41X9z7Ek7wrJ5/1WuxkUg1\n+uVdvna6byOnepVCdVAkgnuUEmp4UZ6AcAA+yDD8dIdEg2//w1/ZyGTGvx37EJDB\nCZJ9xl8ULuWZe84pGgWM5QKBgQCYVUbYKrNjShrM5z9uh4QlII6V1Oeql2YtBz4i\nKZE3db6jp9pi8hf+WwnZ8g9WyFjz9edqydAkmTXHHYW0ReHlBYCjm0VRhUMuuNOs\n3YfuVpFuMsFuv/oJpXqaKE3wKi5j4OAH1o7ctWuuFWMAQ7vhHZ7UySmBZJ4jiFaW\n7KaPVwKBgE8E0xbSDVGxXbEGwRXxeaOSemEHD9uEnbAyq1p3EBBhBvInWmDiP5vJ\n68IYNZ4SGxXEKDifwrLGHyekt3RK9B2+U03okd1qH7gfBIlxBJivcjhBe2PtK/Qj\n6fBN0fC1UJoE6pseT9cJDaBq2wMRXJGRYtT8fU9PPJcfa23JlKNS\n-----END RSA PRIVATE KEY-----\n'})

TASK [remote/starlingx : Create VZ ICA secret to back the clusterIssuer] **********************************************************************
Thursday 06 February 2025  00:44:43 +0000 (0:00:05.345)       1:14:08.063 *****
changed: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/starlingx : Create VZ ICA clusterIssuer] *****************************************************************************************
Thursday 06 February 2025  00:44:44 +0000 (0:00:01.490)       1:14:09.553 *****
changed: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/starlingx : Make sure VZ ICA clusterIssuer is Ready before proceeding] ***********************************************************
Thursday 06 February 2025  00:44:46 +0000 (0:00:01.600)       1:14:11.154 *****
changed: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/starlingx : create Rest Api (starlingx) certificate] *****************************************************************************
Thursday 06 February 2025  00:44:47 +0000 (0:00:01.463)       1:14:12.618 *****
[WARNING]: Collection ansible.netcommon does not support Ansible version 2.13.7
[WARNING]: Collection ansible.utils does not support Ansible version 2.13.7
changed: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/starlingx : make sure Rest Api (starlingx) certificate is Ready before proceeding] ***********************************************
Thursday 06 February 2025  00:44:49 +0000 (0:00:01.680)       1:14:14.298 *****
changed: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/starlingx : wait until system configuration is updated] **************************************************************************
Thursday 06 February 2025  00:44:50 +0000 (0:00:01.446)       1:14:15.745 *****
changed: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/starlingx : wait until https is enabled on the (public) api endpoints] ***********************************************************
Thursday 06 February 2025  00:44:54 +0000 (0:00:04.124)       1:14:19.870 *****
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014]: wait until https is enabled on the (public) api endpoints (20 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014]: wait until https is enabled on the (public) api endpoints (19 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014]: wait until https is enabled on the (public) api endpoints (18 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014]: wait until https is enabled on the (public) api endpoints (17 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014]: wait until https is enabled on the (public) api endpoints (16 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014]: wait until https is enabled on the (public) api endpoints (15 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014]: wait until https is enabled on the (public) api endpoints (14 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014]: wait until https is enabled on the (public) api endpoints (13 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014]: wait until https is enabled on the (public) api endpoints (12 retries left).
changed: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/starlingx : create registry certificate] *****************************************************************************************
Thursday 06 February 2025  00:50:09 +0000 (0:05:14.231)       1:19:34.102 *****
[WARNING]: Collection ansible.netcommon does not support Ansible version 2.13.7
[WARNING]: Collection ansible.utils does not support Ansible version 2.13.7
changed: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/starlingx : make sure registry certificate is Ready before proceeding] ***********************************************************
Thursday 06 February 2025  00:50:10 +0000 (0:00:01.700)       1:19:35.802 *****
changed: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/starlingx : wait until system configuration is updated] **************************************************************************
Thursday 06 February 2025  00:50:12 +0000 (0:00:01.573)       1:19:37.376 *****
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014]: wait until system configuration is updated (20 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014]: wait until system configuration is updated (19 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014]: wait until system configuration is updated (18 retries left).
changed: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/starlingx : wait until https is enabled on the (public) api endpoints] ***********************************************************
Thursday 06 February 2025  00:44:54 +0000 (0:00:04.124)       1:14:19.870 *****
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014]: wait until https is enabled on the (public) api endpoints (20 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014]: wait until https is enabled on the (public) api endpoints (19 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014]: wait until https is enabled on the (public) api endpoints (18 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014]: wait until https is enabled on the (public) api endpoints (17 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014]: wait until https is enabled on the (public) api endpoints (16 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014]: wait until https is enabled on the (public) api endpoints (15 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014]: wait until https is enabled on the (public) api endpoints (14 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014]: wait until https is enabled on the (public) api endpoints (13 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014]: wait until https is enabled on the (public) api endpoints (12 retries left).
changed: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/starlingx : create registry certificate] *****************************************************************************************
Thursday 06 February 2025  00:50:09 +0000 (0:05:14.231)       1:19:34.102 *****
[WARNING]: Collection ansible.netcommon does not support Ansible version 2.13.7
[WARNING]: Collection ansible.utils does not support Ansible version 2.13.7
changed: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/starlingx : make sure registry certificate is Ready before proceeding] ***********************************************************
Thursday 06 February 2025  00:50:10 +0000 (0:00:01.700)       1:19:35.802 *****
changed: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/starlingx : wait until system configuration is updated] **************************************************************************
Thursday 06 February 2025  00:50:12 +0000 (0:00:01.573)       1:19:37.376 *****
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014]: wait until system configuration is updated (20 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014]: wait until system configuration is updated (19 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014]: wait until system configuration is updated (18 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014]: wait until system configuration is updated (17 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014]: wait until system configuration is updated (16 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014]: wait until system configuration is updated (15 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014]: wait until system configuration is updated (14 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014]: wait until system configuration is updated (13 retries left).
changed: [welktxsr-931883-rz-le0gls6-014]

TASK [Remote Integ] ***************************************************************************************************************************
Thursday 06 February 2025  00:54:52 +0000 (0:04:40.249)       1:24:17.625 *****

TASK [remote/integ : Detect applied status of platform-integ-apps application] ****************************************************************
Thursday 06 February 2025  00:54:52 +0000 (0:00:00.068)       1:24:17.694 *****
changed: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/integ : Fail if platform-integ-apps application apply failed] ********************************************************************
Thursday 06 February 2025  00:54:56 +0000 (0:00:04.300)       1:24:21.994 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [Remote Ldap] ****************************************************************************************************************************
Thursday 06 February 2025  00:54:56 +0000 (0:00:00.022)       1:24:22.017 *****

TASK [remote/ldap : Create temporary working directory] ***************************************************************************************
Thursday 06 February 2025  00:54:57 +0000 (0:00:00.112)       1:24:22.130 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/ldap : Copy SSL root certificates] ***********************************************************************************************
Thursday 06 February 2025  00:54:57 +0000 (0:00:00.031)       1:24:22.162 *****
skipping: [welktxsr-931883-rz-le0gls6-014] => (item={'filename': 'vz_root_ca_cert.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIFpTCCA42gAwIBAgIUa3vZ0YGxO1TQ8NwhiVfQC0JslXgwDQYJKoZIhvcNAQEL\nBQAwWjELMAkGA1UEBhMCVVMxEDAOBgNVBAoMB1Zlcml6b24xEzARBgNVBAsMClZa\nSUFNIFRlc3QxJDAiBgNVBAMMG1Zlcml6b24gTmV0d29yayBSU0EgQ0EgVGVzdDAe\nFw0yMDA2MTUyMTAxMTNaFw0zNTA2MTUyMTAxMTNaMFoxCzAJBgNVBAYTAlVTMRAw\nDgYDVQQKDAdWZXJpem9uMRMwEQYDVQQLDApWWklBTSBUZXN0MSQwIgYDVQQDDBtW\nZXJpem9uIE5ldHdvcmsgUlNBIENBIFRlc3QwggIiMA0GCSqGSIb3DQEBAQUAA4IC\nDwAwggIKAoICAQC8AIrksI57CbIl5uGZ6yqfpQj3aK+N8f1EVHdwK9JFskoipvC8\n7yFTk8tgmO1i0YA5oRGfNxneqCdrXZiWL6Ko8v/iln9vuN+2rK3rgWZPPRJBAsBN\na49L7U6lJjIGxIZtZqmK5h47oiUtwlYVrbZMN2ijuBQ22/eQ9tsFDV28oBuZ3WAR\npSSbj/tubPQYkw3YYOhv/VpEpsd0rkoEt3QCmTVcX2rtblanpXowTV5R0Hy4014n\nT49jrEo40r4mwYoyS835Uv4ENUFA+pXicT9eUot3RSH6rYdx4A/14UtoI9U0ol8M\n62GHpxSASQ2Kc3yQWvxRGTFslTduYM+vVmMLEDDdqcsjYnStPpwdxxmKItmbjxSv\nIwYIndp8A04WkX2iiJCciC3BNxiLamPtYVyB1HHqbGTGirKYuSvwZt337q1OI3WH\nwVn2S4Mj/wqa4iCyGTvFSUnGq34Xkrb9XNwWBok9Tc2XWGAU/mb/xcd1hX74GZbF\nsrZ11aPtym4kMAjU2KQi96GcAH2lnGZYoOja1J4Cs4WYx1uAx74H/m84CrYavVfl\n1ONJVLDfuZaEkSmu+jHQX15pAECNORTuLD06PbWnOEcOi1xmbt/OT3SA3rhD2mb7\n2wxl7oJpV3ap8xGwYmxiFzmInxFJ1axjg8Rimol0mXTKAy6OdNHbCOnAwwIDAQAB\no2MwYTAPBgNVHRMBAf8EBTADAQH/MA4GA1UdDwEB/wQEAwIBBjAfBgNVHSMEGDAW\ngBQleng3lqGBeTrbLVuABoEmUHm1+TAdBgNVHQ4EFgQUJXp4N5ahgXk62y1bgAaB\nJlB5tfkwDQYJKoZIhvcNAQELBQADggIBADQ9jpmVh9nyY7ZQ4s+S9RuSRYn7QsrW\nDePeMzQgh8ZtS8WE65GY5HS61iHNP2Co8Q1lAaBWF4ipq+VZOcQbPLccHzd1kZv4\ns4u0aTzBd9ccidl73FS0DJDQOBbzPSzgsaiGHSMyGzkTeA8z3ntsSqrXXcDUvoRi\nFus/110AwdtNhJLrWveX6btYtHp9Lqe0YtNCy5AaXlrr1yRSckP5BWVtlwD4dzSO\n/dqI3wHS/ncUx9wSQomZ+AmxYW3KtJQKgHzTqHru1x9BBk7Bzfz9FZr6HLLmEitj\nuFoDRd5TNt5LbO0zDQokvY3oqso6Htup/rS7C08mcmnelYE+yXuOc1YrlyGnpBzk\nmy+1VYbOxRRdqKAZRbE72u/h847IVpsOvjR51iksuCAurZdp2+y2zvV8NhWekuNy\nirECRy9cb4YasjRaKi0/TCGPVSICuLyeG2W72liCj/N2VKfjPP9zsOR5XjwCXfRg\n+9xhLy77/gov2NWXx5fzTkhxCrHOxFdLVMn0wQhksDmw6QsXzDIHSpIOypdDfnx9\nCsthx3nhkuHLUaEP22D22dG+vImA9ukj4R/RRI/87jmi9Q8+ehH+NqN0GZZcLjdN\nSLVXpncuwWQFUDPR06wNkkkmBSXWiIYhwqSpU0Pl3er3fD0uWvXuWPm2PzfOmUAE\nUrkzyw9XmLw0\n-----END CERTIFICATE-----\n'})
skipping: [welktxsr-931883-rz-le0gls6-014] => (item={'filename': 'vz_root_ica_cert.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIFNzCCAx+gAwIBAgIUGLJR/hP48n+vdq2v1hcfspXo/78wDQYJKoZIhvcNAQEL\nBQAwWjELMAkGA1UEBhMCVVMxEDAOBgNVBAoMB1Zlcml6b24xEzARBgNVBAsMClZa\nSUFNIFRlc3QxJDAiBgNVBAMMG1Zlcml6b24gTmV0d29yayBSU0EgQ0EgVGVzdDAe\nFw0yMDEwMjIyMTE0MDNaFw0zMDEwMjIyMTE0MDNaMIGRMQswCQYDVQQGEwJVUzEL\nMAkGA1UECAwCVFgxETAPBgNVBAcMCFdlc3RsYWtlMRAwDgYDVQQKDAdWZXJpem9u\nMR0wGwYDVQQLDBRWZXJpem9uIFNvdXJjaW5nIExMQzExMC8GA1UEAwwoVmVyaXpv\nbiBOZXR3b3JrIFdFTEtUWElCIExBQiAxIDMgUlNBIElDQTCCASIwDQYJKoZIhvcN\nAQEBBQADggEPADCCAQoCggEBANhkGTXOCKEYf5znDDeX3n/DHFPVqazgQsr0/SIG\n4eb1JY5q5Jq3ZhAaZCr9HJuCkwAP/zgYH0llqOvf8AC2Uh+7z1b33IbwxPmJfWCP\nAqSNFkLWWVRdbELapCu408QsrLMW8IrdP6PLiKAepwncfm4T0/6bANqIEmUkpw8Q\nxProeiNwlGbwUll+tELmdCk7vA7hKX3j1kUvS5Z84Z5ivJBWEcUEggmC97TK4aLo\nFVEHbyahze568JVEaM1vY5L4mnRRTl+u5ipaSMxVBsiXzF7eFuKCzqF7wxbDIt2T\nIFEJtwyJDW5bXjyXgiF1d5H/URprUcRV9Qmf2+PXcfwHII8CAwEAAaOBvDCBuTAS\nBgNVHRMBAf8ECDAGAQH/AgEAMA4GA1UdDwEB/wQEAwIBBjAfBgNVHSMEGDAWgBQl\neng3lqGBeTrbLVuABoEmUHm1+TBTBgNVHR8ETDBKMEigRqBEhkJodHRwOi8vc2Vj\ndXJlLnN0YWdpbmcuc2VjdXJpdHljcmVkZW50aWFsaW5nLmNvbS9jcmwvdnpuZXRy\nc2FjYS5jcmwwHQYDVR0OBBYEFP0Z+/vaDLtAoFig1I9ttNKnmzByMA0GCSqGSIb3\nDQEBCwUAA4ICAQBuXVTf9e01HeymHgRcFCwP2N6G6u+vIzY8Bz0zSUZeRDHMZQcS\nNoabDyn5FfGJlw4BqGC591Sp0/unFQDzAg17rDBcrgwajeFeUiFdb9PiAJwHaX9S\nvq/7VmVLCmpeb+a/laXAe6+tkY1kcFrd1+ItRKC6ZGXMsoDkmk5Ndxxgw77estcI\nMiiLQbvpXRygX5wD4/ayazuLms9qITZkOZ1nTLVqq7QrwYCsSoih7hj6sbsfXr19\nGoYWmk8Y7O/d3ttgyHuRH9k/2dQ/xL7avRpMNkPdr7ocJqI46hvx2X6UyOo7IBua\nkSkFbSmPZWIVAidNMBOnvffCQ32tfjT2/xso/a9cdskvxqgLi0MPARU9Nl2Pufsb\nD7l4/sBvz/PiNTKp+Daa9FdyLb9ySidos1uS0c24bUtY1RXXGAVV2qgfyrzvzfye\nSM+w16hMU/yeYiuA1jsPmsnZnuIJj4Nv8ZjjZ0WS53pP5wcghaHkBrqWQNT8meqA\nVElrMBPlYq67T+AXP0B9lf5Sc3QVIio7XKKfqrlcQxY2JGLEyE53JgZGX7dpwU4I\nukLvyHbT4p06oY3qG6+wH8+YIXCNAYtadJ/C5/u9GcLX5NnZrcuduj0inw2/a3Ao\nWgCt6/Pr28BkCvkWdDt9d8Z40qeu1aZdcr157mR+yZGPfBfB2vasrNIEwQ==\n-----END CERTIFICATE-----\n'})
skipping: [welktxsr-931883-rz-le0gls6-014] => (item={'filename': 'vz_root_ica_key.pem', 'value': '-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA2GQZNc4IoRh/nOcMN5fef8McU9WprOBCyvT9Igbh5vUljmrk\nmrdmEBpkKv0cm4KTAA//OBgfSWWo69/wALZSH7vPVvfchvDE+Yl9YI8CpI0WQtZZ\nVF1sQtqkK7jTxCyssxbwit0/o8uIoB6nCdx+bhPT/psA2ogSZSSnDxDE+uh6I3CU\nZvBSWX60QuZ0KTu8DuEpfePWRS9LlnzhnmK8kFYRxQSCCYL3tMrhougVUQdvJqHN\n7nrwlURozW9jkviadFFOX67mKlpIzFUGyJfMXt4W4oLOoXvDFsMi3ZMgUQm3DIkN\nbltePJeCIXV3kf9RGmtRxFX1CZ/b49dx/AcgjwIDAQABAoIBABSd1NkPfDr8/ouQ\nZ9WUHprFmBlUrgnOhA6aMNPhG/zJNn7PKGClQJAgM5L08pjOY/sJiyNpCPIRQXrX\npyIqPMDRP/vlOZmRrvKnas6cUYAkAQ71JSWokPv9oM6ZmXODXiDh+qEAW2PbrHS0\n9u01mMYcFYKYeghYFoiUaWZCDsJo3v3dgeE9aQ4tB9ksovSmWrpuCY7NKbd7Qrbo\n5XxQhkujTkE6knOHz8CVwYETtj8LZ/bvHIkGMGvRvwsKYDZkIKr5CZ7DX+KcMfPN\neMZU4VCHYSXNxsyp5DJ1Zw+gx8/32kUL0CzJLLam1G021Hq41KPwwSV/KPrOKel7\nHXDLXeECgYEA8MR+lgxGjYTc/k4TdZvcFVgqHGLXnyjO7ZVt4b7UpwmayLuoSD/M\nOpHQYX+JBIIWTNlGhG8UV3DPC3v+auhYa7twwbekS30IYCAmu5GCKgMAcWFinz6A\nYZxG55P/hShetCyOqikgwXqzMlwGs8KEul8f8BKssROzUy8mIlFhjq0CgYEA5hTM\nSNxAD3dlRtb0771fBU7fjx8JPfjptP9vP/JVEelkc/ti9nZ5buTC+9cQC/B+YFx7\nc82uCrXV13bGR9iH8xBhwU7JOYJZbgCpwp0F56wIN5Pdk9Eo79Batrw3oGBG4Yvt\nDc2eltxQbHgObc/qygf88j9XqD8aGIvQrc4Jf6sCgYAtxX03M1A6WTbWFau3YRD+\n8crXqKbLOCvWmODR2MB+nOHTJXHBgndl7xCJaIB43e41X9z7Ek7wrJ5/1WuxkUg1\n+uVdvna6byOnepVCdVAkgnuUEmp4UZ6AcAA+yDD8dIdEg2//w1/ZyGTGvx37EJDB\nCZJ9xl8ULuWZe84pGgWM5QKBgQCYVUbYKrNjShrM5z9uh4QlII6V1Oeql2YtBz4i\nKZE3db6jp9pi8hf+WwnZ8g9WyFjz9edqydAkmTXHHYW0ReHlBYCjm0VRhUMuuNOs\n3YfuVpFuMsFuv/oJpXqaKE3wKi5j4OAH1o7ctWuuFWMAQ7vhHZ7UySmBZJ4jiFaW\n7KaPVwKBgE8E0xbSDVGxXbEGwRXxeaOSemEHD9uEnbAyq1p3EBBhBvInWmDiP5vJ\n68IYNZ4SGxXEKDifwrLGHyekt3RK9B2+U03okd1qH7gfBIlxBJivcjhBe2PtK/Qj\n6fBN0fC1UJoE6pseT9cJDaBq2wMRXJGRYtT8fU9PPJcfa23JlKNS\n-----END RSA PRIVATE KEY-----\n'})

TASK [remote/ldap : Copy templates] ***********************************************************************************************************
Thursday 06 February 2025  00:54:57 +0000 (0:00:00.034)       1:24:22.196 *****
skipping: [welktxsr-931883-rz-le0gls6-014] => (item={'name': 'req-ldap.cnf', 'mode': '0644'})

TASK [remote/ldap : Generate SSL cert] ********************************************************************************************************
Thursday 06 February 2025  00:54:57 +0000 (0:00:00.023)       1:24:22.219 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/ldap : Copy templates] ***********************************************************************************************************
Thursday 06 February 2025  00:54:57 +0000 (0:00:00.020)       1:24:22.239 *****
skipping: [welktxsr-931883-rz-le0gls6-014] => (item={'name': 'dex-overrides.yaml', 'mode': '0644'})

TASK [remote/ldap : Copy SSL dex certs to server] *********************************************************************************************
Thursday 06 February 2025  00:54:57 +0000 (0:00:00.022)       1:24:22.262 *****
skipping: [welktxsr-931883-rz-le0gls6-014] => (item=dex-cert.pem)
skipping: [welktxsr-931883-rz-le0gls6-014] => (item=dex-key.pem)
skipping: [welktxsr-931883-rz-le0gls6-014] => (item=dex-ca.pem)

TASK [remote/ldap : Copy SSL AD cert to server] ***********************************************************************************************
Thursday 06 February 2025  00:54:57 +0000 (0:00:00.025)       1:24:22.287 *****
skipping: [welktxsr-931883-rz-le0gls6-014] => (item={'filename': 'ad_ca.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIFpTCCA42gAwIBAgIUa3vZ0YGxO1TQ8NwhiVfQC0JslXgwDQYJKoZIhvcNAQEL\nBQAwWjELMAkGA1UEBhMCVVMxEDAOBgNVBAoMB1Zlcml6b24xEzARBgNVBAsMClZa\nSUFNIFRlc3QxJDAiBgNVBAMMG1Zlcml6b24gTmV0d29yayBSU0EgQ0EgVGVzdDAe\nFw0yMDA2MTUyMTAxMTNaFw0zNTA2MTUyMTAxMTNaMFoxCzAJBgNVBAYTAlVTMRAw\nDgYDVQQKDAdWZXJpem9uMRMwEQYDVQQLDApWWklBTSBUZXN0MSQwIgYDVQQDDBtW\nZXJpem9uIE5ldHdvcmsgUlNBIENBIFRlc3QwggIiMA0GCSqGSIb3DQEBAQUAA4IC\nDwAwggIKAoICAQC8AIrksI57CbIl5uGZ6yqfpQj3aK+N8f1EVHdwK9JFskoipvC8\n7yFTk8tgmO1i0YA5oRGfNxneqCdrXZiWL6Ko8v/iln9vuN+2rK3rgWZPPRJBAsBN\na49L7U6lJjIGxIZtZqmK5h47oiUtwlYVrbZMN2ijuBQ22/eQ9tsFDV28oBuZ3WAR\npSSbj/tubPQYkw3YYOhv/VpEpsd0rkoEt3QCmTVcX2rtblanpXowTV5R0Hy4014n\nT49jrEo40r4mwYoyS835Uv4ENUFA+pXicT9eUot3RSH6rYdx4A/14UtoI9U0ol8M\n62GHpxSASQ2Kc3yQWvxRGTFslTduYM+vVmMLEDDdqcsjYnStPpwdxxmKItmbjxSv\nIwYIndp8A04WkX2iiJCciC3BNxiLamPtYVyB1HHqbGTGirKYuSvwZt337q1OI3WH\nwVn2S4Mj/wqa4iCyGTvFSUnGq34Xkrb9XNwWBok9Tc2XWGAU/mb/xcd1hX74GZbF\nsrZ11aPtym4kMAjU2KQi96GcAH2lnGZYoOja1J4Cs4WYx1uAx74H/m84CrYavVfl\n1ONJVLDfuZaEkSmu+jHQX15pAECNORTuLD06PbWnOEcOi1xmbt/OT3SA3rhD2mb7\n2wxl7oJpV3ap8xGwYmxiFzmInxFJ1axjg8Rimol0mXTKAy6OdNHbCOnAwwIDAQAB\no2MwYTAPBgNVHRMBAf8EBTADAQH/MA4GA1UdDwEB/wQEAwIBBjAfBgNVHSMEGDAW\ngBQleng3lqGBeTrbLVuABoEmUHm1+TAdBgNVHQ4EFgQUJXp4N5ahgXk62y1bgAaB\nJlB5tfkwDQYJKoZIhvcNAQELBQADggIBADQ9jpmVh9nyY7ZQ4s+S9RuSRYn7QsrW\nDePeMzQgh8ZtS8WE65GY5HS61iHNP2Co8Q1lAaBWF4ipq+VZOcQbPLccHzd1kZv4\ns4u0aTzBd9ccidl73FS0DJDQOBbzPSzgsaiGHSMyGzkTeA8z3ntsSqrXXcDUvoRi\nFus/110AwdtNhJLrWveX6btYtHp9Lqe0YtNCy5AaXlrr1yRSckP5BWVtlwD4dzSO\n/dqI3wHS/ncUx9wSQomZ+AmxYW3KtJQKgHzTqHru1x9BBk7Bzfz9FZr6HLLmEitj\nuFoDRd5TNt5LbO0zDQokvY3oqso6Htup/rS7C08mcmnelYE+yXuOc1YrlyGnpBzk\nmy+1VYbOxRRdqKAZRbE72u/h847IVpsOvjR51iksuCAurZdp2+y2zvV8NhWekuNy\nirECRy9cb4YasjRaKi0/TCGPVSICuLyeG2W72liCj/N2VKfjPP9zsOR5XjwCXfRg\n+9xhLy77/gov2NWXx5fzTkhxCrHOxFdLVMn0wQhksDmw6QsXzDIHSpIOypdDfnx9\nCsthx3nhkuHLUaEP22D22dG+vImA9ukj4R/RRI/87jmi9Q8+ehH+NqN0GZZcLjdN\nSLVXpncuwWQFUDPR06wNkkkmBSXWiIYhwqSpU0Pl3er3fD0uWvXuWPm2PzfOmUAE\nUrkzyw9XmLw0\n-----END CERTIFICATE-----\n'})

TASK [remote/ldap : Configure local-dex.tls] **************************************************************************************************
Thursday 06 February 2025  00:54:57 +0000 (0:00:00.024)       1:24:22.312 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/ldap : Configure generic] ********************************************************************************************************
Thursday 06 February 2025  00:54:57 +0000 (0:00:00.019)       1:24:22.331 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/ldap : Configure wadcert] ********************************************************************************************************
Thursday 06 February 2025  00:54:57 +0000 (0:00:00.019)       1:24:22.351 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/ldap : Configure dex-overrides.yaml] *********************************************************************************************
Thursday 06 February 2025  00:54:57 +0000 (0:00:00.019)       1:24:22.371 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/ldap : Wait for distributed cloud synchronization] *******************************************************************************
Thursday 06 February 2025  00:54:57 +0000 (0:00:00.022)       1:24:22.393 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/ldap : Remove temporary working directory] ***************************************************************************************
Thursday 06 February 2025  00:54:57 +0000 (0:00:00.022)       1:24:22.415 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/ldap : bringing in variables from the system controller] *************************************************************************
Thursday 06 February 2025  00:54:57 +0000 (0:00:00.018)       1:24:22.434 *****
ok: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/ldap : Copy SSL AD cert to server] ***********************************************************************************************
Thursday 06 February 2025  00:54:57 +0000 (0:00:00.041)       1:24:22.475 *****
changed: [welktxsr-931883-rz-le0gls6-014] => (item={'filename': 'ad_ca.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIFpTCCA42gAwIBAgIUa3vZ0YGxO1TQ8NwhiVfQC0JslXgwDQYJKoZIhvcNAQEL\nBQAwWjELMAkGA1UEBhMCVVMxEDAOBgNVBAoMB1Zlcml6b24xEzARBgNVBAsMClZa\nSUFNIFRlc3QxJDAiBgNVBAMMG1Zlcml6b24gTmV0d29yayBSU0EgQ0EgVGVzdDAe\nFw0yMDA2MTUyMTAxMTNaFw0zNTA2MTUyMTAxMTNaMFoxCzAJBgNVBAYTAlVTMRAw\nDgYDVQQKDAdWZXJpem9uMRMwEQYDVQQLDApWWklBTSBUZXN0MSQwIgYDVQQDDBtW\nZXJpem9uIE5ldHdvcmsgUlNBIENBIFRlc3QwggIiMA0GCSqGSIb3DQEBAQUAA4IC\nDwAwggIKAoICAQC8AIrksI57CbIl5uGZ6yqfpQj3aK+N8f1EVHdwK9JFskoipvC8\n7yFTk8tgmO1i0YA5oRGfNxneqCdrXZiWL6Ko8v/iln9vuN+2rK3rgWZPPRJBAsBN\na49L7U6lJjIGxIZtZqmK5h47oiUtwlYVrbZMN2ijuBQ22/eQ9tsFDV28oBuZ3WAR\npSSbj/tubPQYkw3YYOhv/VpEpsd0rkoEt3QCmTVcX2rtblanpXowTV5R0Hy4014n\nT49jrEo40r4mwYoyS835Uv4ENUFA+pXicT9eUot3RSH6rYdx4A/14UtoI9U0ol8M\n62GHpxSASQ2Kc3yQWvxRGTFslTduYM+vVmMLEDDdqcsjYnStPpwdxxmKItmbjxSv\nIwYIndp8A04WkX2iiJCciC3BNxiLamPtYVyB1HHqbGTGirKYuSvwZt337q1OI3WH\nwVn2S4Mj/wqa4iCyGTvFSUnGq34Xkrb9XNwWBok9Tc2XWGAU/mb/xcd1hX74GZbF\nsrZ11aPtym4kMAjU2KQi96GcAH2lnGZYoOja1J4Cs4WYx1uAx74H/m84CrYavVfl\n1ONJVLDfuZaEkSmu+jHQX15pAECNORTuLD06PbWnOEcOi1xmbt/OT3SA3rhD2mb7\n2wxl7oJpV3ap8xGwYmxiFzmInxFJ1axjg8Rimol0mXTKAy6OdNHbCOnAwwIDAQAB\no2MwYTAPBgNVHRMBAf8EBTADAQH/MA4GA1UdDwEB/wQEAwIBBjAfBgNVHSMEGDAW\ngBQleng3lqGBeTrbLVuABoEmUHm1+TAdBgNVHQ4EFgQUJXp4N5ahgXk62y1bgAaB\nJlB5tfkwDQYJKoZIhvcNAQELBQADggIBADQ9jpmVh9nyY7ZQ4s+S9RuSRYn7QsrW\nDePeMzQgh8ZtS8WE65GY5HS61iHNP2Co8Q1lAaBWF4ipq+VZOcQbPLccHzd1kZv4\ns4u0aTzBd9ccidl73FS0DJDQOBbzPSzgsaiGHSMyGzkTeA8z3ntsSqrXXcDUvoRi\nFus/110AwdtNhJLrWveX6btYtHp9Lqe0YtNCy5AaXlrr1yRSckP5BWVtlwD4dzSO\n/dqI3wHS/ncUx9wSQomZ+AmxYW3KtJQKgHzTqHru1x9BBk7Bzfz9FZr6HLLmEitj\nuFoDRd5TNt5LbO0zDQokvY3oqso6Htup/rS7C08mcmnelYE+yXuOc1YrlyGnpBzk\nmy+1VYbOxRRdqKAZRbE72u/h847IVpsOvjR51iksuCAurZdp2+y2zvV8NhWekuNy\nirECRy9cb4YasjRaKi0/TCGPVSICuLyeG2W72liCj/N2VKfjPP9zsOR5XjwCXfRg\n+9xhLy77/gov2NWXx5fzTkhxCrHOxFdLVMn0wQhksDmw6QsXzDIHSpIOypdDfnx9\nCsthx3nhkuHLUaEP22D22dG+vImA9ukj4R/RRI/87jmi9Q8+ehH+NqN0GZZcLjdN\nSLVXpncuwWQFUDPR06wNkkkmBSXWiIYhwqSpU0Pl3er3fD0uWvXuWPm2PzfOmUAE\nUrkzyw9XmLw0\n-----END CERTIFICATE-----\n'})

TASK [remote/ldap : create oidc-auth-apps-certificate] ****************************************************************************************
Thursday 06 February 2025  00:55:00 +0000 (0:00:02.788)       1:24:25.264 *****
[WARNING]: Collection ansible.netcommon does not support Ansible version 2.13.7
[WARNING]: Collection ansible.utils does not support Ansible version 2.13.7
changed: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/ldap : make sure oidc certificate is Ready before proceeding] ********************************************************************
Thursday 06 February 2025  00:55:01 +0000 (0:00:01.674)       1:24:26.939 *****
changed: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/ldap : wait until system configuration is updated] *******************************************************************************
Thursday 06 February 2025  00:55:03 +0000 (0:00:01.475)       1:24:28.415 *****
changed: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/ldap : create dex-ca-cert secret] ************************************************************************************************
Thursday 06 February 2025  00:55:07 +0000 (0:00:04.587)       1:24:33.002 *****
changed: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/ldap : template overrides] *******************************************************************************************************
Thursday 06 February 2025  00:55:09 +0000 (0:00:01.540)       1:24:34.543 *****
changed: [welktxsr-931883-rz-le0gls6-014] => (item=stx-oidc-client.yaml)
[WARNING]: Collection ansible.netcommon does not support Ansible version 2.13.7
[WARNING]: Collection ansible.utils does not support Ansible version 2.13.7
changed: [welktxsr-931883-rz-le0gls6-014] => (item=dex-overrides-2212.yaml)
changed: [welktxsr-931883-rz-le0gls6-014] => (item=secret-observer-overrides.yaml)

TASK [remote/ldap : override oidc-client] *****************************************************************************************************
Thursday 06 February 2025  00:55:17 +0000 (0:00:07.927)       1:24:42.470 *****
changed: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/ldap : create wad ca cert secret] ************************************************************************************************
Thursday 06 February 2025  00:55:21 +0000 (0:00:04.425)       1:24:46.895 *****
changed: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/ldap : override dex] *************************************************************************************************************
Thursday 06 February 2025  00:55:23 +0000 (0:00:01.483)       1:24:48.379 *****
changed: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/ldap : override secret observer] *************************************************************************************************
Thursday 06 February 2025  00:55:27 +0000 (0:00:04.355)       1:24:52.734 *****
changed: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/ldap : Detect oidc-auth-apps application in applying state (from a previous attempt)] ********************************************
Thursday 06 February 2025  00:55:31 +0000 (0:00:04.285)       1:24:57.020 *****
changed: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/ldap : Fail if oidc-auth-apps application-abort failed] **************************************************************************
Thursday 06 February 2025  00:55:36 +0000 (0:00:04.139)       1:25:01.160 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/ldap : Detect oidc-auth-apps application in apply-failed or aborted state] *******************************************************
Thursday 06 February 2025  00:55:36 +0000 (0:00:00.018)       1:25:01.178 *****
changed: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/ldap : Fail if oidc-auth-apps application apply failed] **************************************************************************
Thursday 06 February 2025  00:55:40 +0000 (0:00:04.342)       1:25:05.520 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/ldap : Apply oidc-auth-apps application] *****************************************************************************************
Thursday 06 February 2025  00:55:40 +0000 (0:00:00.023)       1:25:05.544 *****
changed: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/ldap : Detect applied status of oidc-auth-apps application] **********************************************************************
Thursday 06 February 2025  00:55:44 +0000 (0:00:04.494)       1:25:10.038 *****
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014]: Detect applied status of oidc-auth-apps application (60 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014]: Detect applied status of oidc-auth-apps application (60 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014]: Detect applied status of oidc-auth-apps application (59 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014]: Detect applied status of oidc-auth-apps application (58 retries left).
changed: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/ldap : Fail if oidc-auth-apps application apply failed] **************************************************************************
Thursday 06 February 2025  00:56:32 +0000 (0:00:47.434)       1:25:57.473 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [Remote Nvme] ****************************************************************************************************************************
Thursday 06 February 2025  00:56:32 +0000 (0:00:00.024)       1:25:57.497 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [Remote Metrics Server] ******************************************************************************************************************
Thursday 06 February 2025  00:56:32 +0000 (0:00:00.020)       1:25:57.518 *****

TASK [remote/metrics-server : Determine metrics-server Helm Chart path] ***********************************************************************
Thursday 06 February 2025  00:56:32 +0000 (0:00:00.118)       1:25:57.637 *****
ok: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/metrics-server : Set facts - release independent] ********************************************************************************
Thursday 06 February 2025  00:56:34 +0000 (0:00:01.493)       1:25:59.131 *****
ok: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/metrics-server : Detect presence of existing application] ************************************************************************
Thursday 06 February 2025  00:56:34 +0000 (0:00:00.018)       1:25:59.150 *****
fatal: [welktxsr-931883-rz-le0gls6-014]: FAILED! => changed=true
  cmd: |-
    . /etc/platform/openrc
    system application-show metrics-server --column status --format value
  delta: '0:00:02.762876'
  end: '2025-02-06 00:56:38.075443'
  msg: non-zero return code
  rc: 1
  start: '2025-02-06 00:56:35.312567'
  stderr: 'application not found: metrics-server'
  stderr_lines: <omitted>
  stdout: ''
  stdout_lines: <omitted>
...ignoring

TASK [remote/metrics-server : Print message if system already has the appication] *************************************************************
Thursday 06 February 2025  00:56:38 +0000 (0:00:04.185)       1:26:03.335 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/metrics-server : Apply again since the previous apply failed or in uploaded state] ***********************************************
Thursday 06 February 2025  00:56:38 +0000 (0:00:00.019)       1:26:03.355 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/metrics-server : Wait until apply is in the applied or apply-failed state] *******************************************************
Thursday 06 February 2025  00:56:38 +0000 (0:00:00.017)       1:26:03.373 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/metrics-server : Print message if re-apply succeeds] *****************************************************************************
Thursday 06 February 2025  00:56:38 +0000 (0:00:00.017)       1:26:03.390 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/metrics-server : Print message if re-apply failed] *******************************************************************************
Thursday 06 February 2025  00:56:38 +0000 (0:00:00.020)       1:26:03.411 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/metrics-server : Noop if system requires no further action or needs manual investigation] ****************************************
Thursday 06 February 2025  00:56:38 +0000 (0:00:00.020)       1:26:03.432 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/metrics-server : Upload application] *********************************************************************************************
Thursday 06 February 2025  00:56:38 +0000 (0:00:00.021)       1:26:03.453 *****
changed: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/metrics-server : Wait until application is in the uploaded state] ****************************************************************
Thursday 06 February 2025  00:56:42 +0000 (0:00:04.238)       1:26:07.692 *****
changed: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/metrics-server : copy resource override over] ************************************************************************************
Thursday 06 February 2025  00:56:47 +0000 (0:00:04.380)       1:26:12.072 *****
changed: [welktxsr-931883-rz-le0gls6-014] => (item=ms_resource_override.yaml)

TASK [remote/metrics-server : update ms with resource override] *******************************************************************************
Thursday 06 February 2025  00:56:49 +0000 (0:00:02.720)       1:26:14.793 *****
changed: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/metrics-server : Apply application] **********************************************************************************************
Thursday 06 February 2025  00:56:54 +0000 (0:00:04.525)       1:26:19.318 *****
changed: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/metrics-server : Wait until application is in the applied or apply-failed state] *************************************************
Thursday 06 February 2025  00:56:58 +0000 (0:00:04.187)       1:26:23.506 *****
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014]: Wait until application is in the applied or apply-failed state (90 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014]: Wait until application is in the applied or apply-failed state (89 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014]: Wait until application is in the applied or apply-failed state (88 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014]: Wait until application is in the applied or apply-failed state (87 retries left).
changed: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/metrics-server : Apply again since the first apply failed] ***********************************************************************
Thursday 06 February 2025  00:58:00 +0000 (0:01:02.062)       1:27:25.568 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/metrics-server : Wait again until apply is in the applied or apply-failed state] *************************************************
Thursday 06 February 2025  00:58:00 +0000 (0:00:00.025)       1:27:25.594 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/metrics-server : Print message if apply is successful] ***************************************************************************
Thursday 06 February 2025  00:58:00 +0000 (0:00:00.023)       1:27:25.618 *****
ok: [welktxsr-931883-rz-le0gls6-014] =>
  msg:
  - =======================================================
  - ' welktxsr-d931883-014: metrics-server install SUCCEEDED! '
  - =======================================================

TASK [remote/metrics-server : Print message if apply is failure] ******************************************************************************
Thursday 06 February 2025  00:58:00 +0000 (0:00:00.027)       1:27:25.645 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [set wra_target_version] *****************************************************************************************************************
Thursday 06 February 2025  00:58:00 +0000 (0:00:00.024)       1:27:25.670 *****
ok: [welktxsr-931883-rz-le0gls6-014]

TASK [Remote wrap-23.09-1] ********************************************************************************************************************
Thursday 06 February 2025  00:58:00 +0000 (0:00:00.018)       1:27:25.689 *****

TASK [remote/wrap-23.09-1 : Set facts for playbook] *******************************************************************************************
Thursday 06 February 2025  00:58:00 +0000 (0:00:00.135)       1:27:25.824 *****
ok: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/wrap-23.09-1 : Noop if the system is NOT at the right caas_version] **************************************************************
Thursday 06 February 2025  00:58:00 +0000 (0:00:00.017)       1:27:25.841 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/wrap-23.09-1 : Print message if system is NOT at the right caas_version] *********************************************************
Thursday 06 February 2025  00:58:00 +0000 (0:00:00.016)       1:27:25.857 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/wrap-23.09-1 : Determine WRA current version and status] *************************************************************************
Thursday 06 February 2025  00:58:00 +0000 (0:00:00.015)       1:27:25.873 *****
fatal: [welktxsr-931883-rz-le0gls6-014]: FAILED! => changed=true
  cmd: |-
    . /etc/platform/openrc
    system application-show wr-analytics --column app_version --column status --format value
  delta: '0:00:02.893561'
  end: '2025-02-06 00:58:04.919588'
  msg: non-zero return code
  rc: 1
  start: '2025-02-06 00:58:02.026027'
  stderr: 'application not found: wr-analytics'
  stderr_lines: <omitted>
  stdout: ''
  stdout_lines: <omitted>
...ignoring

TASK [remote/wrap-23.09-1 : Set facts for current WRA version and status] *********************************************************************
Thursday 06 February 2025  00:58:05 +0000 (0:00:04.307)       1:27:30.180 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/wrap-23.09-1 : debug] ************************************************************************************************************
Thursday 06 February 2025  00:58:05 +0000 (0:00:00.019)       1:27:30.200 *****
ok: [welktxsr-931883-rz-le0gls6-014] =>
  msg: 'wra_status:, wra_version:'

TASK [remote/wrap-23.09-1 : Determine if version is up-to-date] *******************************************************************************
Thursday 06 February 2025  00:58:05 +0000 (0:00:00.020)       1:27:30.221 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/wrap-23.09-1 : Noop because version is up-to-date] *******************************************************************************
Thursday 06 February 2025  00:58:05 +0000 (0:00:00.017)       1:27:30.238 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [Delete the existing WRA app] ************************************************************************************************************
Thursday 06 February 2025  00:58:05 +0000 (0:00:00.016)       1:27:30.255 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/wrap-23.09-1 : Delete app if just uploaded] **************************************************************************************
Thursday 06 February 2025  00:58:05 +0000 (0:00:00.020)       1:27:30.276 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/wrap-23.09-1 : Set facts for central security file] ******************************************************************************
Thursday 06 February 2025  00:58:05 +0000 (0:00:00.023)       1:27:30.299 *****
ok: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/wrap-23.09-1 : Set facts for working dir] ****************************************************************************************
Thursday 06 February 2025  00:58:05 +0000 (0:00:00.024)       1:27:30.323 *****
ok: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/wrap-23.09-1 : Create working directory on host] *********************************************************************************
Thursday 06 February 2025  00:58:05 +0000 (0:00:00.025)       1:27:30.349 *****
changed: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/wrap-23.09-1 : Copy files to host] ***********************************************************************************************
Thursday 06 February 2025  00:58:06 +0000 (0:00:01.419)       1:27:31.769 *****
changed: [welktxsr-931883-rz-le0gls6-014] => (item=wr-analytics-23.09-1.tgz)

TASK [remote/wrap-23.09-1 : Copy templates to host] *******************************************************************************************
Thursday 06 February 2025  00:58:09 +0000 (0:00:02.662)       1:27:34.432 *****
changed: [welktxsr-931883-rz-le0gls6-014] => (item=elastic-services-security-config.yaml)
changed: [welktxsr-931883-rz-le0gls6-014] => (item=logstash_sev_overrides-dropAll6.yaml)
changed: [welktxsr-931883-rz-le0gls6-014] => (item=logstash_samsung_vdu_parser.yaml)
changed: [welktxsr-931883-rz-le0gls6-014] => (item=helm-logstash_extra_envvars.yaml)
changed: [welktxsr-931883-rz-le0gls6-014] => (item=metricbeat-overrides.yaml)

TASK [remote/wrap-23.09-1 : test if the elastic override exists on the CC] ********************************************************************
Thursday 06 February 2025  00:58:22 +0000 (0:00:13.235)       1:27:47.668 *****
ok: [welktxsr-931883-rz-le0gls6-014 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)]

TASK [remote/wrap-23.09-1 : debug] ************************************************************************************************************
Thursday 06 February 2025  00:58:24 +0000 (0:00:02.199)       1:27:49.868 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/wrap-23.09-1 : Apply wr-analytics application] ***********************************************************************************
Thursday 06 February 2025  00:58:24 +0000 (0:00:00.031)       1:27:49.899 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/wrap-23.09-1 : Wait until application is in the applied or apply-failed state] ***************************************************
Thursday 06 February 2025  00:58:24 +0000 (0:00:00.029)       1:27:49.929 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/wrap-23.09-1 : the file is brand new, set flag to skip testing its content] ******************************************************
Thursday 06 February 2025  00:58:24 +0000 (0:00:00.024)       1:27:49.954 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/wrap-23.09-1 : get content from the file] ****************************************************************************************
Thursday 06 February 2025  00:58:24 +0000 (0:00:00.026)       1:27:49.980 *****
ok: [welktxsr-931883-rz-le0gls6-014 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)]

TASK [remote/wrap-23.09-1 : get content from kubernetes] **************************************************************************************
Thursday 06 February 2025  00:58:27 +0000 (0:00:02.312)       1:27:52.293 *****
changed: [welktxsr-931883-rz-le0gls6-014 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)]

TASK [remote/wrap-23.09-1 : get ext-ca.crt md5 hashes] ****************************************************************************************
Thursday 06 February 2025  00:58:29 +0000 (0:00:02.285)       1:27:54.579 *****
ok: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/wrap-23.09-1 : debug] ************************************************************************************************************
Thursday 06 February 2025  00:58:29 +0000 (0:00:00.057)       1:27:54.637 *****
ok: [welktxsr-931883-rz-le0gls6-014] =>
  msg: file content md5 is 6070e32274a8740025c8933bcdf99283, k8s content md5 is 5b2ce03ca9fba3d5fdc5ca1ae0667878

TASK [remote/wrap-23.09-1 : debug] ************************************************************************************************************
Thursday 06 February 2025  00:58:29 +0000 (0:00:00.029)       1:27:54.666 *****
ok: [welktxsr-931883-rz-le0gls6-014] =>
  msg: The k8s value of ext-ca.crt on the CC is different from the value in /opt/platform/config/22.12/analytics/elastic-services-security-overrides.yaml. Regenerating.

TASK [remote/wrap-23.09-1 : Apply wr-analytics application] ***********************************************************************************
Thursday 06 February 2025  00:58:29 +0000 (0:00:00.031)       1:27:54.697 *****
changed: [welktxsr-931883-rz-le0gls6-014 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)]

TASK [remote/wrap-23.09-1 : Wait until application is in the applied or apply-failed state] ***************************************************
Thursday 06 February 2025  00:58:35 +0000 (0:00:05.965)       1:28:00.662 *****
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> rchltxfe-c000000-001]: Wait until application is in the applied or apply-failed state (90 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014 -> rchltxfe-c000000-001]: Wait until application is in the applied or apply-failed state (89 retries left).
changed: [welktxsr-931883-rz-le0gls6-014 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)]

TASK [remote/wrap-23.09-1 : Copy elastic security override from CC to Subcloud] ***************************************************************
Thursday 06 February 2025  00:59:52 +0000 (0:01:16.669)       1:29:17.332 *****
changed: [welktxsr-931883-rz-le0gls6-014 -> rchltxfe-c000000-001(2607:f160:0:3043:cd:290:0:10)]

TASK [remote/wrap-23.09-1 : Upload wr-analytics application] **********************************************************************************
Thursday 06 February 2025  00:59:54 +0000 (0:00:02.522)       1:29:19.854 *****
changed: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/wrap-23.09-1 : Wait until application is in the uploaded state] ******************************************************************
Thursday 06 February 2025  00:59:59 +0000 (0:00:04.431)       1:29:24.286 *****
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014]: Wait until application is in the uploaded state (30 retries left).
changed: [welktxsr-931883-rz-le0gls6-014]
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014]: Wait until application is in the applied or apply-failed state (89 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014]: Wait until application is in the applied or apply-failed state (88 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014]: Wait until application is in the applied or apply-failed state (87 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014]: Wait until application is in the applied or apply-failed state (86 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014]: Wait until application is in the applied or apply-failed state (85 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014]: Wait until application is in the applied or apply-failed state (84 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014]: Wait until application is in the applied or apply-failed state (83 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014]: Wait until application is in the applied or apply-failed state (82 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014]: Wait until application is in the applied or apply-failed state (81 retries left).
FAILED - RETRYING: [welktxsr-931883-rz-le0gls6-014]: Wait until application is in the applied or apply-failed state (80 retries left).
changed: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/wrap-23.09-1 : Print message if install succeeded] *******************************************************************************
Thursday 06 February 2025  01:07:07 +0000 (0:06:24.036)       1:36:32.295 *****
ok: [welktxsr-931883-rz-le0gls6-014] =>
  msg:
  - ===================================================================
  - ' welktxsr-d931883-014: WRA 23.09-1 install SUCCEEDED! '
  - ===================================================================

TASK [remote/wrap-23.09-1 : Print message if install failed] **********************************************************************************
Thursday 06 February 2025  01:07:07 +0000 (0:00:00.030)       1:36:32.325 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [Remote fpga-user-image] *****************************************************************************************************************
Thursday 06 February 2025  01:07:07 +0000 (0:00:00.026)       1:36:32.352 *****

TASK [remote/fpga-user-image : Set facts for default fpga_image_file] *************************************************************************
Thursday 06 February 2025  01:07:07 +0000 (0:00:00.111)       1:36:32.463 *****
ok: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/fpga-user-image : Set facts for fpga_image_file from host_vars] ******************************************************************
Thursday 06 February 2025  01:07:07 +0000 (0:00:00.026)       1:36:32.489 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/fpga-user-image : Print message if server is not LS3 cascadelake] ****************************************************************
Thursday 06 February 2025  01:07:07 +0000 (0:00:00.025)       1:36:32.515 *****
ok: [welktxsr-931883-rz-le0gls6-014] =>
  msg:
  - ==================================================================================
  - ' Server type ZTS-LS6-gln is not LS3 cascadelake, no action will take place! '
  - ==================================================================================

TASK [remote/fpga-user-image : Register noop because server is not LS3 cascadelake] ***********************************************************
Thursday 06 February 2025  01:07:07 +0000 (0:00:00.019)       1:36:32.535 *****
changed: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/fpga-user-image : Check if FPGA update is stuck] *********************************************************************************
Thursday 06 February 2025  01:07:08 +0000 (0:00:01.422)       1:36:33.957 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/fpga-user-image : Abort FPGA update] *********************************************************************************************
Thursday 06 February 2025  01:07:08 +0000 (0:00:00.021)       1:36:33.979 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/fpga-user-image : include_tasks] *************************************************************************************************
Thursday 06 February 2025  01:07:08 +0000 (0:00:00.020)       1:36:34.000 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/fpga-user-image : Check FPGA update status (HPE-LS3-e910)] ***********************************************************************
Thursday 06 February 2025  01:07:08 +0000 (0:00:00.020)       1:36:34.020 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/fpga-user-image : Check FPGA update status (ZTS-LS3-trtn)] ***********************************************************************
Thursday 06 February 2025  01:07:09 +0000 (0:00:00.019)       1:36:34.040 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/fpga-user-image : Noop if the system has been updated] ***************************************************************************
Thursday 06 February 2025  01:07:09 +0000 (0:00:00.020)       1:36:34.061 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/fpga-user-image : Print message if the system has been updated] ******************************************************************
Thursday 06 February 2025  01:07:09 +0000 (0:00:00.019)       1:36:34.080 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/fpga-user-image : In main block] *************************************************************************************************
Thursday 06 February 2025  01:07:09 +0000 (0:00:00.019)       1:36:34.099 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/fpga-user-image : Copy files to host] ********************************************************************************************
Thursday 06 February 2025  01:07:09 +0000 (0:00:00.019)       1:36:34.119 *****
skipping: [welktxsr-931883-rz-le0gls6-014] => (item=20ww43.5-1x2x25G-5GLDPC-v1.6.2-3.0.1-unsigned.bin)

TASK [remote/fpga-user-image : Do system device-image-upload] *********************************************************************************
Thursday 06 February 2025  01:07:09 +0000 (0:00:00.023)       1:36:34.142 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/fpga-user-image : debug - print UUID] ********************************************************************************************
Thursday 06 February 2025  01:07:09 +0000 (0:00:00.020)       1:36:34.162 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/fpga-user-image : Do system device-image-apply] **********************************************************************************
Thursday 06 February 2025  01:07:09 +0000 (0:00:00.018)       1:36:34.181 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/fpga-user-image : Do system host-device-image-update] ****************************************************************************
Thursday 06 February 2025  01:07:09 +0000 (0:00:00.018)       1:36:34.200 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/fpga-user-image : Wait till application completed] *******************************************************************************
Thursday 06 February 2025  01:07:09 +0000 (0:00:00.019)       1:36:34.219 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/fpga-user-image : Do system device-image-state-list] *****************************************************************************
Thursday 06 February 2025  01:07:09 +0000 (0:00:00.018)       1:36:34.238 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/fpga-user-image : force an error if image state is not completed] ****************************************************************
Thursday 06 February 2025  01:07:09 +0000 (0:00:00.020)       1:36:34.258 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/fpga-user-image : include_tasks] *************************************************************************************************
Thursday 06 February 2025  01:07:09 +0000 (0:00:00.019)       1:36:34.278 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [Install DM Monitor] *********************************************************************************************************************
Thursday 06 February 2025  01:07:09 +0000 (0:00:00.021)       1:36:34.300 *****

TASK [remote/dm-monitor : Install DM Monitor] *************************************************************************************************
Thursday 06 February 2025  01:07:09 +0000 (0:00:00.141)       1:36:34.442 *****
changed: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/dm-monitor : Wait for DM Monitor pod created] ************************************************************************************
Thursday 06 February 2025  01:07:45 +0000 (0:00:36.255)       1:37:10.697 *****
changed: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/dm-monitor : Wait for control-plane pods become ready] ***************************************************************************
Thursday 06 February 2025  01:07:47 +0000 (0:00:01.517)       1:37:12.215 *****
changed: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/dm-monitor : debug] **************************************************************************************************************
Thursday 06 February 2025  01:07:48 +0000 (0:00:01.470)       1:37:13.685 *****
ok: [welktxsr-931883-rz-le0gls6-014] =>
  dm_monitor_pod_ready.stdout_lines:
  - pod/dm-monitor-984c7659d-xq7kw condition met

TASK [Disable DM] *****************************************************************************************************************************
Thursday 06 February 2025  01:07:48 +0000 (0:00:00.027)       1:37:13.713 *****

TASK [remote/disable-dm : Scale down DM Deployment to 0] **************************************************************************************
Thursday 06 February 2025  01:07:48 +0000 (0:00:00.028)       1:37:13.741 *****
changed: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/disable-dm : Wait for pod to go away ready] **************************************************************************************
Thursday 06 February 2025  01:07:50 +0000 (0:00:01.489)       1:37:15.230 *****
changed: [welktxsr-931883-rz-le0gls6-014]

TASK [Workaround for 00157193] ****************************************************************************************************************
Thursday 06 February 2025  01:07:51 +0000 (0:00:01.538)       1:37:16.769 *****
changed: [welktxsr-931883-rz-le0gls6-014]

TASK [Disable root login] *********************************************************************************************************************
Thursday 06 February 2025  01:07:53 +0000 (0:00:01.566)       1:37:18.335 *****

TASK [remote/disable-root : disable ssh login for root user] **********************************************************************************
Thursday 06 February 2025  01:07:53 +0000 (0:00:00.037)       1:37:18.372 *****
changed: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/disable-root : restart ssh daemon] ***********************************************************************************************
Thursday 06 February 2025  01:07:54 +0000 (0:00:01.589)       1:37:19.962 *****
changed: [welktxsr-931883-rz-le0gls6-014]

TASK [remote/disable-root : lock root's password] *********************************************************************************************
Thursday 06 February 2025  01:07:56 +0000 (0:00:01.638)       1:37:21.600 *****
changed: [welktxsr-931883-rz-le0gls6-014]

TASK [2212mr1 workarounds] ********************************************************************************************************************
Thursday 06 February 2025  01:07:58 +0000 (0:00:01.865)       1:37:23.466 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [include_tasks] **************************************************************************************************************************
Thursday 06 February 2025  01:07:58 +0000 (0:00:00.022)       1:37:23.488 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

TASK [include_tasks] **************************************************************************************************************************
Thursday 06 February 2025  01:07:58 +0000 (0:00:00.022)       1:37:23.511 *****
skipping: [welktxsr-931883-rz-le0gls6-014]

PLAY RECAP ************************************************************************************************************************************
welktxsr-931883-rz-le0gls6-014 : ok=158  changed=87   unreachable=0    failed=0    skipped=167  rescued=0    ignored=5

Thursday 06 February 2025  01:07:58 +0000 (0:00:00.024)       1:37:23.535 *****
===============================================================================
remote/remote-install : 4th polling: Wait for subcloud to install OS (this may still take a while) ---------------------------------- 2458.75s
remote/remote-install : 2nd polling: Wait for subcloud to install OS (this will take a while) ---------------------------------------- 759.27s
remote/manage : Wait for system to stabilize before running kubectl ------------------------------------------------------------------ 480.02s
remote/wrap-23.09-1 : Wait until application is in the applied or apply-failed state ------------------------------------------------- 384.04s
remote/starlingx : wait until https is enabled on the (public) api endpoints --------------------------------------------------------- 314.23s
remote/reset_bmc : Wait for ZTS BMC to reset ----------------------------------------------------------------------------------------- 300.02s
remote/manage : Wait for system to stabilize ----------------------------------------------------------------------------------------- 300.02s
remote/starlingx : wait until system configuration is updated ------------------------------------------------------------------------ 280.25s
remote/wrap-23.09-1 : Wait until application is in the applied or apply-failed state -------------------------------------------------- 76.67s
remote/metrics-server : Wait until application is in the applied or apply-failed state ------------------------------------------------ 62.06s
remote/ldap : Detect applied status of oidc-auth-apps application --------------------------------------------------------------------- 47.43s
remote/dm-monitor : Install DM Monitor ------------------------------------------------------------------------------------------------ 36.26s
remote/remote-install : 1st polling: Wait for subcloud to start installing OS --------------------------------------------------------- 30.89s
remote/wrap-23.09-1 : Wait until application is in the uploaded state ----------------------------------------------------------------- 19.44s
remote/wrap-23.09-1 : Copy templates to host ------------------------------------------------------------------------------------------ 13.24s
remote/remote-configure : copy seed templates ------------------------------------------------------------------------------------------ 9.57s
remote/ldap : template overrides ------------------------------------------------------------------------------------------------------- 7.93s
remote/remote-install : Set subcloud system time by NTP server ------------------------------------------------------------------------- 7.62s
remote/remote-install : Deploy remote cloud - subcloud version same as CC's ------------------------------------------------------------ 6.87s
remote/set-facts : Get central controller's software load version ---------------------------------------------------------------------- 6.02s
(ansible_6.7) szabota@welktxefnce-h-pe1util-vm05:~/playbooks/wr-installer-atlas-me$




```

### Deployment of subcloud completed, now lets just validate the subcloud is upgraded 

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ dcmanager subcloud list
+----+----------------------+------------+--------------+---------------+-------------+---------------+-----------------+
| id | name                 | management | availability | deploy status | sync        | backup status | backup datetime |
+----+----------------------+------------+--------------+---------------+-------------+---------------+-----------------+
| 42 | welktxef-d931883-022 | managed    | offline      | complete      | out-of-sync | None          | None            |
| 62 | welktxsr-d931883-022 | managed    | online       | complete      | in-sync     | None          | None            |
| 63 | welktxsr-d931883-014 | managed    | online       | complete      | in-sync     | None          | None            |
+----+----------------------+------------+--------------+---------------+-------------+---------------+-----------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ dcmanager subcloud show welktxsr-d931883-014
+-----------------------------+---------------------------------+
| Field                       | Value                           |
+-----------------------------+---------------------------------+
| id                          | 63                              |
| name                        | welktxsr-d931883-014            |
| description                 | Wind River Cloud Platform 22.12 |
| location                    | welktxsr-d931883-014            |
| software_version            | 22.12                           |
| management                  | managed                         |
| availability                | online                          |
| deploy_status               | complete                        |
| management_subnet           | 2607:f160:10:80cc::/64          |
| management_start_ip         | 2607:f160:10:80cc:ce:40a::      |
| management_end_ip           | 2607:f160:10:80cc:ce:40a:0:f    |
| management_gateway_ip       | 2607:f160:10:80cc:ce:23::       |
| systemcontroller_gateway_ip | 2607:f160:0:3042:cd:28::        |
| group_id                    | 1                               |
| created_at                  | 2025-02-05 23:36:16.783514      |
| updated_at                  | 2025-02-06 00:39:37.192409      |
| backup_status               | None                            |
| backup_datetime             | None                            |
| dc-cert_sync_status         | in-sync                         |
| firmware_sync_status        | in-sync                         |
| identity_sync_status        | in-sync                         |
| kubernetes_sync_status      | in-sync                         |
| kube-rootca_sync_status     | in-sync                         |
| load_sync_status            | in-sync                         |
| patching_sync_status        | in-sync                         |
| platform_sync_status        | in-sync                         |
+-----------------------------+---------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$
[XXXXXX@controller-0 ~(keystone_admin)]$
[XXXXXX@controller-0 ~(keystone_admin)]$ ssh welktxsr-d931883-014
The authenticity of host 'welktxsr-d931883-014 (2607:f160:10:80cc:ce:40a::)' can't be established.
ECDSA key fingerprint is SHA256:ImF/8KIXZ8NAyZqzwhxk7okycUPexq+hx9NrmpIh+Vg.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added 'welktxsr-d931883-014,2607:f160:10:80cc:ce:40a::' (ECDSA) to the list of known hosts.
Release 22.12
------------------------------------------------------------------------
W A R N I N G *** W A R N I N G *** W A R N I N G *** W A R N I N G ***
------------------------------------------------------------------------
THIS IS A PRIVATE COMPUTER SYSTEM.
This computer system including all related equipment, network devices
(specifically including Internet access), are provided only for authorized use.
All computer systems may be monitored for all lawful purposes, including to
ensure that their use is authorized, for management of the system, to
facilitate protection against unauthorized access, and to verify security
procedures, survivability and operational security. Monitoring includes active
attacks by authorized personnel and their entities to test or verify the
security of the system. During monitoring, information may be examined,
recorded, copied and used for authorized purposes. All information including
personal information, placed on or sent over this system may be monitored. Uses
of this system, authorized or unauthorized, constitutes consent to monitoring
of this system. Unauthorized use may subject you to criminal prosecution.
Evidence of any such unauthorized use collected during monitoring may be used
for administrative, criminal or other adverse action. Use of this system
constitutes consent to monitoring for these purposes.

XXXXXX@welktxsr-d931883-014's password:

XXXXXX Unauthorized access to this system is forbidden and will be
prosecuted by law. By accessing this system, you agree that your
actions may be monitored if unauthorized usage is suspected.


====================================================================
         SYSTEM: welktxsr-d931883-014
====================================================================


Linux controller-0 5.10.0-6-rt-amd64 #1 SMP PREEMPT_RT StarlingX Debian 5.10.177-1.stx.76 (2024-03-29 x86_64
Last login: Thu Feb  6 01:07:57 2025 from 2607:f160:10:9239:ce:290:0:3000
XXXXXX@controller-0:~$ source /etc/platform/openrc
[XXXXXX@controller-0 ~(keystone_admin)]$ system show
+------------------------+--------------------------------------+
| Property               | Value                                |
+------------------------+--------------------------------------+
| contact                | None                                 |
| created_at             | 2025-02-05T23:55:48.457169+00:00     |
| description            | None                                 |
| distributed_cloud_role | subcloud                             |
| https_enabled          | True                                 |
| latitude               | None                                 |
| location               | None                                 |
| longitude              | None                                 |
| name                   | welktxsr-d931883-014                 |
| region_name            | welktxsr-d931883-014                 |
| sdn_enabled            | False                                |
| security_feature       | spectre_meltdown_v1                  |
| service_project_name   | services                             |
| shared_services        | []                                   |
| software_version       | 22.12                                |
| system_mode            | simplex                              |
| system_type            | All-in-one                           |
| timezone               | UTC                                  |
| updated_at             | 2025-02-06T00:49:54.215123+00:00     |
| uuid                   | 9e33cf99-272c-491a-b993-2742afca5cf4 |
| vswitch_type           | none                                 |
+------------------------+--------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ system application-list
+--------------------------+----------+-------------------------------------------+------------------+---------+-----------+
| application              | version  | manifest name                             | manifest file    | status  | progress  |
+--------------------------+----------+-------------------------------------------+------------------+---------+-----------+
| cert-manager             | 22.12-8  | cert-manager-fluxcd-manifests             | fluxcd-manifests | applied | completed |
| metrics-server           | 22.12-2  | metrics-server-fluxcd-manifests           | fluxcd-manifests | applied | completed |
| nginx-ingress-controller | 22.12-1  | nginx-ingress-controller-fluxcd-manifests | fluxcd-manifests | applied | completed |
| oidc-auth-apps           | 22.12-6  | oidc-auth-apps-fluxcd-manifests           | fluxcd-manifests | applied | completed |
| platform-integ-apps      | 22.12-72 | platform-integ-apps-fluxcd-manifests      | fluxcd-manifests | applied | completed |
| wr-analytics             | 23.09-1  | wr-analytics-fluxcd-manifests             | fluxcd-manifests | applied | completed |
+--------------------------+----------+-------------------------------------------+------------------+---------+-----------+
[XXXXXX@controller-0 ~(keystone_admin)]$ sw-patch query
      Patch ID         RR  Release  Patch State
=====================  ==  =======  ===========
WRCP_22.12_PATCH_0001  Y    22.12    Committed
WRCP_22.12_PATCH_0002  Y    22.12    Committed
WRCP_22.12_PATCH_0003  Y    22.12    Committed
WRCP_22.12_PATCH_0004  Y    22.12    Committed
WRCP_22.12_PATCH_0005  Y    22.12    Committed

[XXXXXX@controller-0 ~(keystone_admin)]$
```

### Test is complete, new subcloud deployment worked as expected