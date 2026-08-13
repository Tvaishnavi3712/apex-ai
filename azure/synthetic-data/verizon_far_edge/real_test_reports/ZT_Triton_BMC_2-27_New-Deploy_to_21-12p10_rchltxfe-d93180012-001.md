# ZT Triton 2.27 BMC firmware validation
# New Deploy of 21.12p10 with firmware installed in subcloud to 2.27
# 12/13/23 James Patchett

## Target Controller rchltxib-c000000-003 CR-3 (Richardson infrastructure System)
OAM: 2607:f160:0:3049:cd:290:0:10

## Subcloud rchltxfe-d93180012-001 (VCP-fe Infrastructure)
OAM: 2607:f160:10:9073:ce:40a:0:f400
ILO: 2607:f160:10:9073:ce:406:0:1000

ipmitool -I lanplus -U XXXXXX -P XXXXXX -H 2607:f160:10:9073:ce:406:0:1000 sol activate


### controller has been upgraded to 21.12p10, next step is to upgrade subcloud with triton 2.27 firmware

### Controller validation of 21.12p10 readyness
```log
[XXXXXX@controller-0 ~(keystone_admin)]$ system show
+------------------------+--------------------------------------+
| Property               | Value                                |
+------------------------+--------------------------------------+
| contact                | demo.contact@verizon.com            |
| created_at             | 2023-12-05T01:21:55.798101+00:00     |
| description            | Wind River Cloud Platform 21.05      |
| distributed_cloud_role | systemcontroller                     |
| https_enabled          | True                                 |
| latitude               | None                                 |
| location               | None                                 |
| longitude              | None                                 |
| name                   | rchltxib-c000000-003                 |
| region_name            | RegionOne                            |
| sdn_enabled            | False                                |
| security_feature       | spectre_meltdown_v1                  |
| service_project_name   | services                             |
| software_version       | 21.12                                |
| system_mode            | duplex                               |
| system_type            | Standard                             |
| timezone               | UTC                                  |
| updated_at             | 2023-12-06T03:00:52.809897+00:00     |
| uuid                   | 7035e534-a268-4484-9fae-c8d27c3831a8 |
| vswitch_type           | none                                 |
+------------------------+--------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ sw-patch query
      Patch ID         RR  Release  Patch State
=====================  ==  =======  ===========
WRCP_21.05_PATCH_0001  N    21.05    Committed
WRCP_21.05_PATCH_0002  Y    21.05    Committed
WRCP_21.05_PATCH_0003  N    21.05    Committed
WRCP_21.05_PATCH_0004  N    21.05    Committed
WRCP_21.05_PATCH_0005  N    21.05     Applied
WRCP_21.05_PATCH_0006  N    21.05     Applied
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

[XXXXXX@controller-0 ~(keystone_admin)]$ fm alarm-list

[XXXXXX@controller-0 ~(keystone_admin)]$ dcmanager subcloud list
+----+------------------------+------------+--------------+---------------+---------+
| id | name                   | management | availability | deploy status | sync    |
+----+------------------------+------------+--------------+---------------+---------+
|  2 | rchltxfe-d93180012-001 | managed    | online       | complete      | in-sync |
|  3 | welktxef-d931881-005   | managed    | online       | complete      | in-sync |
|  6 | welktxef-d931884-034   | managed    | online       | complete      | in-sync |
+----+------------------------+------------+--------------+---------------+---------+
[XXXXXX@controller-0 ~(keystone_admin)]$ system application-list
+--------------------------+----------+-----------------------------------+-----------------------+----------+-------------+
| application              | version  | manifest name                     | manifest file         | status   | progress    |
+--------------------------+----------+-----------------------------------+-----------------------+----------+-------------+
| cert-manager             | 21.12-28 | cert-manager-manifest             | certmanager-manifest. | applied  | completed   |
|                          |          |                                   | yaml                  |          |             |
|                          |          |                                   |                       |          |             |
| nginx-ingress-controller | 21.12-18 | nginx-ingress-controller-manifest | nginx_ingress_control | applied  | Application |
|                          |          |                                   | ler_manifest.yaml     |          | update from |
|                          |          |                                   |                       |          | version 21. |
|                          |          |                                   |                       |          | 05-16 to    |
|                          |          |                                   |                       |          | version 21. |
|                          |          |                                   |                       |          | 12-18       |
|                          |          |                                   |                       |          | completed.  |
|                          |          |                                   |                       |          |             |
| oidc-auth-apps           | 21.12-61 | oidc-auth-manifest                | manifest.yaml         | applied  | completed   |
| platform-integ-apps      | 21.12-46 | platform-integration-manifest     | manifest.yaml         | uploaded | completed   |
| rook-ceph-apps           | 1.0-5    | rook-ceph-manifest                | manifest.yaml         | uploaded | completed   |
+--------------------------+----------+-----------------------------------+-----------------------+----------+-------------+
[XXXXXX@controller-0 ~(keystone_admin)]$


```


### start new deployment 
### Unmanage subcloud then delete from controller..
```log
[XXXXXX@controller-0 ~(keystone_admin)]$ dcmanager subcloud list
+----+------------------------+------------+--------------+---------------+---------+
| id | name                   | management | availability | deploy status | sync    |
+----+------------------------+------------+--------------+---------------+---------+
|  2 | rchltxfe-d93180012-001 | managed    | online       | complete      | in-sync |
|  3 | welktxef-d931881-005   | managed    | online       | complete      | in-sync |
|  6 | welktxef-d931884-034   | managed    | online       | complete      | in-sync |
+----+------------------------+------------+--------------+---------------+---------+
[XXXXXX@controller-0 ~(keystone_admin)]$ dcmanager subcloud unmanage rchltxfe-d93180012-001
+-----------------------------+---------------------------------+
| Field                       | Value                           |
+-----------------------------+---------------------------------+
| id                          | 2                               |
| name                        | rchltxfe-d93180012-001          |
| description                 | Wind River Cloud Platform 21.05 |
| location                    | rchltxfe-d93180012-001          |
| software_version            | 21.12                           |
| management                  | unmanaged                       |
| availability                | online                          |
| deploy_status               | complete                        |
| management_subnet           | 2607:f160:10:907b::/64          |
| management_start_ip         | 2607:f160:10:907b:ce:40a::      |
| management_end_ip           | 2607:f160:10:907b:ce:40a:0:f    |
| management_gateway_ip       | 2607:f160:10:907b:ce:28::       |
| systemcontroller_gateway_ip | 2607:f160:0:3048:cd:28::        |
| group_id                    | 1                               |
| created_at                  | 2023-12-05T15:46:21.700016      |
| updated_at                  | 2023-12-13T15:46:56.706381      |
+-----------------------------+---------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$
[XXXXXX@controller-0 ~(keystone_admin)]$ dcmanager subcloud list
+----+------------------------+------------+--------------+---------------+-------------+
| id | name                   | management | availability | deploy status | sync        |
+----+------------------------+------------+--------------+---------------+-------------+
|  2 | rchltxfe-d93180012-001 | unmanaged  | online       | complete      | out-of-sync |
|  3 | welktxef-d931881-005   | managed    | online       | complete      | in-sync     |
|  6 | welktxef-d931884-034   | managed    | online       | complete      | in-sync     |
+----+------------------------+------------+--------------+---------------+-------------+
[XXXXXX@controller-0 ~(keystone_admin)]$
```

### wipedisk the subcloud, then power off

```log
controller-0 login: XXXXXX
Password:
XXXXXX login: Wed Dec 13 00:50:00 from 2607:f160:0:3048:cd:290:0:11
/etc/motd.d/00-header:

WARNING: Unauthorized access to this system is forbidden and will be
prosecuted by law. By accessing this system, you agree that your
actions may be monitored if unauthorized usage is suspected.

/etc/motd.d/10-system:


====================================================================
         SYSTEM: rchltxfe-d93180012-001
====================================================================

controller-0:~$ sudo -i
Password:
XXXXXX, try again.
Password:
XXXXXX wipedisk
This will result in the loss of all data on the hard drives and
will require this node to be re-installed.
The following disks will be wiped:
    /dev/nvme0n1
    /dev/nvme0n1p5
    /dev/nvme0n1p6

Are you absolutely sure? [y/n] y
Type 'wipediskscompletely' to confirm: wipediskscompletely
Wiping /dev/nvme0n1p5...
/dev/nvme0n1p5: 8 bytes were erased at offset 0x00000218 (LVM2_member): 4c 56 4d 32 20 30 30 31
Trying to unmount /dev/nvme0n1p5
Warning! /dev/nvme0n1p5 is not mounted
34+0 records in
34+0 records out
17408 bytes (17 kB) copied, 0.000121509 s, 143 MB/s
34+0 records in
34+0 records out
17408 bytes (17 kB) copied, 0.000113583 s, 153 MB/s
Wiping /dev/nvme0n1p6...
/dev/nvme0n1p6: 8 bytes were erased at offset 0x00000218 (LVM2_member): 4c 56 4d 32 20 30 30 31
Trying to unmount /dev/nvme0n1p6
Warning! /dev/nvme0n1p6 is not mounted
34+0 records in
34+0 records out
17408 bytes (17 kB) copied, 0.000152374 s, 114 MB/s
34+0 records in
34+0 records out
17408 bytes (17 kB) copied, 0.000152739 s, 114 MB/s
Skipping wipe backup partition /dev/nvme0n1p1...
Wiping partition /dev/nvme0n1p2...
/dev/nvme0n1p2: 8 bytes were erased at offset 0x00000036 (vfat): 46 41 54 31 36 20 20 20
/dev/nvme0n1p2: 1 bytes were erased at offset 0x00000000 (vfat): eb
/dev/nvme0n1p2: 2 bytes were erased at offset 0x000001fe (vfat): 55 aa
Trying to unmount /dev/nvme0n1p2
/dev/nvme0n1p2 has been successfully unmounted
34+0 records in
34+0 records out
17408 bytes (17 kB) copied, 0.00301434 s, 5.8 MB/s
34+0 records in
34+0 records out
17408 bytes (17 kB) copied, 0.000929771 s, 18.7 MB/s
Removing partition /dev/nvme0n1p2...
Warning: The kernel is still using the old partition table.
The new table will be used at the next reboot.
The operation has completed successfully.
Wiping partition /dev/nvme0n1p3...
/dev/nvme0n1p3: 2 bytes were erased at offset 0x00000438 (ext4): 53 ef
Trying to unmount /dev/nvme0n1p3
/dev/nvme0n1p3 has been successfully unmounted
34+0 records in
34+0 records out
17408 bytes (17 kB) copied, 0.00415153 s, 4.2 MB/s
34+0 records in
34+0 records out
17408 bytes (17 kB) copied, 0.000509237 s, 34.2 MB/s
Removing partition /dev/nvme0n1p3...
Warning: The kernel is still using the old partition table.
The new table will be used at the next reboot.
The operation has completed successfully.
Wiping partition /dev/nvme0n1p4...
/dev/nvme0n1p4: 2 bytes were erased at offset 0x00000438 (ext4): 53 ef
Removing partition /dev/nvme0n1p4...
Warning: The kernel is still using the old partition table.
The new table will be used at the next reboot.
The operation has completed successfully.
Wiping partition /dev/nvme0n1p5...
Trying to unmount /dev/nvme0n1p5
Warning! /dev/nvme0n1p5 is not mounted
34+0 records in
34+0 records out
17408 bytes (17 kB) copied, 0.00014631 s, 119 MB/s
34+0 records in
34+0 records out
17408 bytes (17 kB) copied, 0.000166848 s, 104 MB/s
Removing partition /dev/nvme0n1p5...
Warning: The kernel is still using the old partition table.
The new table will be used at the next reboot.
The operation has completed successfully.
Wiping partition /dev/nvme0n1p6...
Trying to unmount /dev/nvme0n1p6
Warning! /dev/nvme0n1p6 is not mounted
34+0 records in
34+0 records out
17408 bytes (17 kB) copied, 0.000156513 s, 111 MB/s
34+0 records in
34+0 records out
17408 bytes (17 kB) copied, 0.000174112 s, 100 MB/s
Removing partition /dev/nvme0n1p6...
Warning: The kernel is still using the old partition table.
The new table will be used at the next reboot.
The operation has completed successfully.
1+0 records in
1+0 records out
440 bytes (440 B) copied, 0.000151492 s, 2.9 MB/s
The disk(s) have been wiped.
controller-0:~#
controller-0:~# poweroff
[  OK  ] Stopped target rpc_pipefs.target.
[  OK  ] Stopped target Timers.
[  OK  ] Stopped Daily Cleanup of Temporary[  OK  ] Stopped Dump dmesg to /var/log/dmesg.
         Stopping LVM2 PV scan on device 259:5...
         Stopping Fault Management REST API Service...
         Stopping Session 802 of user XXXXXX.
[  OK  ] Stopped dnf makecache --timer.
         Stopping Etcd Server...
         Stopping StarlingX Affine Platform...
         Stopping fast remote file copy program daemon...
         Stopping Titanium Cloud libvirt QEMU cleanup...
         Stopping Authorization Manager...
         Stopping Self Monitoring and Reporting Technology (SMART) Daemon...
         Stopping Dynamic System Tuning Daemon...
         Unmounting RPC Pipe File System...
         Stopping Docker Application Container Engine...
         Stopping Command Scheduler...
         Stopping StarlingX Filesystem Initialization...
         Stopping Availability of block devices...
[  OK  ] Stopped target RPC Port Mapper.
[  OK  ] Stopped Authorization Manager.
[  OK  ] Stopped libstoragemgmt plug-in server daemon.
[  OK  ] Stopped Self Monitoring and Reporting Technology (SMART) Daemon.
[  OK  ] Stopped memcached daemon.
[  OK  ] Stopped LLDP daemon.
[  OK  ] Stopped Command Scheduler.
[  OK  ] Stopped Naming services LDAP client daemon..
[  OK  ] Stopped Serial Getty on ttyS0.
[  OK  ] Stopped Getty on tty1.
[  OK  ] Stopped Kubernetes Isolated CPU Plugin Daemon.
[  OK  ] Stopped LVM2 PV scan on device 259:6.
[  OK  ] Stopped StarlingX Maintenance Worker Goenable Ready.
[  OK  ] Stopped LVM2 PV scan on device 259:5.
[  OK  ] Stopped Session 802 of user XXXXXX.
[  OK  ] Stopped Titanium Cloud libvirt QEMU cleanup.
[FAILED] Failed unmounting RPC Pipe File System.
[  OK  ] Stopped StarlingX Filesystem Initialization.
[  OK  ] Stopped Docker Application Container Engine.
[  OK  ] Stopped v2 Registry token server for Docker.
[  OK  ] Stopped Etcd Server.
[  OK  ] Stopped v2 Registry server for Docker.
[  OK  ] Unmounted /var/lib/kubelet/pods/e9f...ubpaths/armada-etc/armada-api/4.
[  OK  ] Unmounted /var/lib/kubelet/pods/e9f...ubpaths/armada-etc/armada-api/3.
[  OK  ] Unmounted /var/lib/kubelet/pods/e9f...ubpaths/armada-etc/armada-api/2.
[  OK  ] Unmounted /www/tmp.
[  OK  ] Unmounted /opt/backups.
[60814.997023] watchdog: watchdog0: watchdog did not stop!
         Stopping containerd container runtime...
         Stopping StarlingX Cloud Filesystem Auto-mounter...
[  OK  ] Removed slice User Slice of XXXXXX.
         Stopping Login Service...
[  OK  ] Removed slice system-lvm2\x2dpvscan.slice.
         Stopping Kubernetes Kubelet Server...
[  OK  ] Removed slice system-getty.slice.
[  OK  ] Removed slice system-serial\x2dgetty.slice.
[  OK  ] Stopped target System Time Synchronized.
         Stopping Permit User Sessions...
[  OK  ] Stopped Login Service.
[  OK  ] Stopped fast remote file copy program daemon.
[  OK  ] Stopped StarlingX Affine Platform.
[  OK  ] Stopped StarlingX Cloud Filesystem Auto-mounter.
[  OK  ] Stopped Permit User Sessions.
[  OK  ] Stopped Availability of block devices.
[  OK  ] Stopped Kubernetes Kubelet Server.
[  OK  ] Stopped Fault Management REST API Service.
         Stopping D-Bus System Message Bus...
[  OK  ] Stopped D-Bus System Message Bus.
[  OK  ] Stopped Dynamic System Tuning Daemon.
[  OK  ] Unmounted /run/containerd/io.contai...1e258b338f9e7bf3911352c2/rootfs.
[  OK  ] Unmounted /run/containerd/io.contai...3712d3b2336908ebd43d1a4b/rootfs.
[  OK  ] Unmounted /run/containerd/io.contai...d58d34534f0e9bd66e9432bf/rootfs.
[  OK  ] Unmounted /run/containerd/io.contai...f4eda80ea61cd24a88b546c8/rootfs.
[  OK  ] Stopped StarlingX Maintenance Host Watchdog.
         Stopping StarlingX Maintenance Process Monitor...
[  OK  ] Stopped StarlingX Maintenance Process Monitor.
         Stopping StarlingX Maintenance Guest Heartbeat Monitor Server...
         Stopping StarlingX Maintenance Heartbeat Agent...
         Stopping StarlingX Patching Agent...
         Stopping StarlingX PCI Interrupt Affinity Agent...
         Stopping StarlingX Maintenance Alarm Handler Client...
         Stopping StarlingX Maintenance Goenable Ready...
         Stopping ACPI Event Daemon...
         Stopping Service Management Event Recorder Unit...
         Stopping StarlingX Maintenance Filesystem Monitor...
         Stopping Collectd statistics daemon and extension services...
         Stopping StarlingX Maintenance Command Handler Client...
         Stopping Network Time Service...
         Stopping StarlingX Maintenance Logger...
         Stopping Starling-X Maintenance Link Monitor...
         Stopping StarlingX FPGA Agent...
         Stopping StarlingX Patching Controller Daemon...
[  OK  ] Stopped ACPI Event Daemon.
[  OK  ] Stopped Network Time Service.
[  OK  ] Stopped StarlingX Patching Agent.
[  OK  ] Stopped StarlingX PCI Interrupt Affinity Agent.
[  OK  ] Stopped StarlingX Maintenance Goenable Ready.
[  OK  ] Stopped StarlingX Patching Controller Daemon.
[  OK  ] Stopped StarlingX FPGA Agent.
[  OK  ] Stopped StarlingX Patching Controller.
         Stopping StarlingX Filesystem Server...
[  OK  ] Stopped Set time via NTP.
[  OK  ] Stopped StarlingX Maintenance Guest Heartbeat Monitor Server.
[  OK  ] Stopped Collectd statistics daemon and extension services.
[  OK  ] Stopped StarlingX Maintenance Heartbeat Agent.
[  OK  ] Stopped StarlingX Maintenance Alarm Handler Client.
[  OK  ] Stopped Starling-X Maintenance Link Monitor.
[  OK  ] Stopped StarlingX Maintenance Command Handler Client.
         Stopping StarlingX Maintenance Heartbeat Client...
[  OK  ] Stopped StarlingX Maintenance Filesystem Monitor.
[  OK  ] Stopped StarlingX Maintenance Logger.
[  OK  ] Stopped StarlingX Maintenance Heartbeat Client.
[  OK  ] Stopped StarlingX Filesystem Server.
[  OK  ] Stopped Service Management Event Recorder Unit.
         Stopping Service Management API Unit...
[  OK  ] Stopped Service Management API Unit.
[  OK  ] Unmounted /run/containerd/io.contai...d357c63965903ecb966420d3/rootfs.
[  OK  ] Unmounted /run/containerd/io.contai...b834ee5fb5ee852026ebea53/rootfs.
[  OK  ] Unmounted /run/containerd/io.contai...5143d063900b5a3bea2fad5f/rootfs.
[  OK  ] Unmounted /run/containerd/io.contai...c4fae08ba254636e9207e20d/rootfs.
[  OK  ] Unmounted /run/containerd/io.contai...d5238190371b1b61ce8a0290/rootfs.
[  OK  ] Unmounted /opt/extension.
[  OK  ] Unmounted /opt/etcd.
[  OK  ] Unmounted /www/pages/device_images.
[  OK  ] Unmounted /var/lib/docker-distribution.
[  OK  ] Unmounted /www/pages/helm_charts.
[  OK  ] Unmounted /run/containerd/io.contai...0a3875e41c625ceb24b555d7/rootfs.
[  OK  ] Unmounted /run/containerd/io.contai...5e908e86433dc2eb3a775109/rootfs.
[  OK  ] Unmounted /run/containerd/io.contai...456b9ef9e0111fadbbe3584b/rootfs.
[  OK  ] Unmounted /run/containerd/io.contai...a8e6456fe189d9c4f9bf6d81/rootfs.
[  OK  ] Unmounted /run/containerd/io.contai...ad1f4f7cd7f236ea1be2ae4d/rootfs.
[  OK  ] Unmounted /run/containerd/io.contai...171b4156586ed63ba1a5a783/rootfs.
[  OK  ] Unmounted /run/containerd/io.contai...3feb38ef9a1ce2e73cc62c67/rootfs.
[  OK  ] Unmounted /run/containerd/io.contai...b98f11cbdd524c4d1366e646/rootfs.
[  OK  ] Unmounted /run/containerd/io.contai...2448e9e01aa048f2cb537460/rootfs.
[  OK  ] Unmounted /run/containerd/io.contai...4863244ebcb28126ec694c9b/rootfs.
[  OK  ] Unmounted /opt/platform.
[  OK  ] Unmounted /var/lib/postgresql.
[  OK  ] Unmounted /run/containerd/io.contai...a0101cb1d2a8cad36ba04c68/rootfs.
[  OK  ] Unmounted /var/lib/rabbitmq.
[  OK  ] Unmounted /run/containerd/io.contai...e185c168d16ae7ff581cc2f3/rootfs.
[  OK  ] Unmounted /run/containerd/io.contai...183ee336fd3f3f556e4fb940/rootfs.
[  OK  ] Unmounted /run/containerd/io.contai...6431462c20012f8f17e7c318/rootfs.
[  OK  ] Stopped containerd container runtime.
         Stopping /usr/bin/ceph-osd -i 0 --p...c/ceph/ceph.conf --cluster ceph.
         Stopping /usr/bin/ceph-mds -i contr...c/ceph/ceph.conf --cluster ceph.
         Stopping /usr/bin/ceph-mon -i contr...c/ceph/ceph.conf --cluster ceph.
[  OK  ] Stopped /usr/bin/ceph-osd -i 0 --pi...c/ceph/ceph.conf --cluster ceph.
[  OK  ] Stopped /usr/bin/ceph-mon -i contro...c/ceph/ceph.conf --cluster ceph.
[  OK  ] Stopped /usr/bin/ceph-mds -i contro...c/ceph/ceph.conf --cluster ceph.
         Stopping Service Management Shutdown Unit...
[  OK  ] Removed slice system-ceph.slice.
[  OK  ] Stopped Service Management Shutdown Unit.
         Stopping Service Management Unit...
[  OK  ] Stopped Service Management Unit.
         Stopping Control drbd resources....
         Stopping Service Management Watchdog...
[  OK  ] Stopped Control drbd resources..
         Stopping OpenSSH server daemon...
[  OK  ] Stopped OpenSSH server daemon.
[  OK  ] Stopped Service Management Watchdog.
[  OK  ] Stopped General StarlingX config gate.
         Stopping StarlingX Log Management...
[  OK  ] Stopped controllerconfig service.
[  OK  ] Stopped target Remote File Systems.
[  OK  ] Stopped target Remote File Systems (Pre).
[  OK  ] Stopped target NFS client services.
         Stopping GSSAPI Proxy Daemon...
         Stopping Logout off all iSCSI sessions on shutdown...
         Stopping StarlingX System Inventory Agent...
[  OK  ] Stopped GSSAPI Proxy Daemon.
[  OK  ] Stopped StarlingX Log Management.
[  OK  ] Stopped Logout off all iSCSI sessions on shutdown.
         Stopping Open-iSCSI...
         Stopping System Logger Daemon...
[  OK  ] Stopped StarlingX System Inventory Agent.
[  OK  ] Stopped Open-iSCSI.
         Stopping Device-Mapper Multipath Device Controller...
         Stopping StarlingX Filesystem Common...
[  OK  ] Stopped target Network is Online.
[  OK  ] Stopped Device-Mapper Multipath Device Controller.
[  OK  ] Stopped StarlingX Filesystem Common.
[  OK  ] Stopped target Network.
         Stopping LSB: Bring up/down networking...
         Stopping RPC bind service...
[  OK  ] Stopped RPC bind service.
[  OK  ] Stopped System Logger Daemon.
[  OK  ] Stopped LSB: Bring up/down networking.
[  OK  ] Stopped target Basic System.
[  OK  ] Stopped target Slices.
[  OK  ] Removed slice User and Session Slice.
[  OK  ] Stopped target Paths.
[  OK  ] Stopped sysinv-conf-watcher.path.
[  OK  ] Stopped Dispatch Password Requests to Console Directory Watch.
[  OK  ] Stopped Forward Password Requests to Wall Directory Watch.
[  OK  ] Stopped target Sockets.
[  OK  ] Closed D-Bus System Message Bus Socket.
[  OK  ] Closed Open-iSCSI iscsid Socket.
[  OK  ] Closed RPCbind Server Activation Socket.
[  OK  ] Closed Open-iSCSI iscsiuio Socket.
[  OK  ] Closed Syslog Socket.
[  OK  ] Closed Docker Socket for the API.
[  OK  ] Stopped target System Initialization.
[  OK  ] Stopped Setup Virtual Console.
[  OK  ] Stopped Apply Kernel Variables.
         Stopping Load/Save Random Seed...
[  OK  ] Stopped target Local Encrypted Volumes.
[  OK  ] Stopped Load Kernel Modules.
[  OK  ] Stopped Read and set NIS domainname from /etc/sysconfig/network.
         Stopping Update UTMP about System Boot/Shutdown...
[  OK  ] Stopped Load/Save Random Seed.
[  OK  ] Stopped Update UTMP about System Boot/Shutdown.
[  OK  ] Stopped Create Volatile Files and Directories.
[  OK  ] Stopped Import network configuration from initramfs.
[  OK  ] Stopped target Local File Systems.
         Unmounting /usr/local/kubernetes/current/stage1...
         Unmounting /var/lib/kubelet/pods/c7...io~secret/default-token-gq26j...
         Unmounting /run/containerd/io.conta...1aee20c2518fcf12ec76b7/rootfs...
         Unmounting /run/netns/cni-6b372a07-1905-3e02-145b-b39a636ffc5d...
         Unmounting /run/user/42425...
         Unmounting /mnt/huge-2048kB...
         Unmounting /var/lib/kubelet/pods/40...t-manager-webhook-token-fb8hr...
         Unmounting /run/containerd/io.conta...c19aa8f67b57c9f0d36cde0df/shm...
         Unmounting /run/containerd/io.conta...240efe5c7b113ada28be8c995/shm...
         Unmounting /var/lib/kubelet/pods/45...ecret/calico-node-token-ldgqw...
         Unmounting /mnt/huge-1048576kB...
         Unmounting /run/containerd/io.conta...514e215a3012a3ba32ed51/rootfs...
         Unmounting /run/containerd/io.conta...a538949ff642dc7b25b3f909e/shm...
         Unmounting /scratch...
         Unmounting /run/containerd/io.conta...92bd0c4d9f4127c28055b5/rootfs...
         Unmounting /var/lib/kubelet/pods/16...ojected/kube-api-access-b7szn...
         Unmounting /var/lib/kubelet/pods/18...iov-device-plugin-token-2v9n4...
         Unmounting /run/netns/cni-6847d3a4-d760-0a02-5553-39238666cccd...
         Unmounting /var/lib/kubelet/pods/9d...anager-cainjector-token-xpzvc...
         Unmounting /run/netns/cni-234716cc-2e72-b9e8-d821-98f942da0e60...
         Unmounting /run/containerd/io.conta...3732f3e7aaa2e503ddd207/rootfs...
         Unmounting /run/containerd/io.conta...c94ea50fa570cf0577a9fa977/shm...
         Unmounting /var/lib/kubelet/pods/ac...ojected/kube-api-access-tmgr8...
         Unmounting /var/lib/kubelet/pods/16.../kubernetes.io~secret/certdir...
         Unmounting /run/containerd/io.conta...c3a92bd0c4d9f4127c28055b5/shm...
         Unmounting /run/containerd/io.conta...ea50fa570cf0577a9fa977/rootfs...
         Unmounting /var/lib/kubelet/pods/65...t/rbd-provisioner-token-fj69f...
         Unmounting /var/lib/docker...
         Unmounting /run/containerd/io.conta...5ff3732f3e7aaa2e503ddd207/shm...
         Unmounting /run/netns/cni-ad0e07d7-5b64-1553-dec9-0295c6f9e241...
         Unmounting /run/netns/cni-0a4a3263-7887-36ef-3ca9-40f44f5ea96f...
         Unmounting /var/lib/kubelet/pods/7f...rnetes.io~secret/webhook-cert...
         Unmounting /run/netns/cni-a6584c78-d8f3-c3e4-8805-3c0bc4da39e3...
         Unmounting /run/netns/cni-7b06068f-1460-5fff-4353-5c7de64e0817...
         Unmounting /run/containerd/io.conta...f7184045dc07004b5d47bb/rootfs...
         Unmounting /run/containerd/io.conta...cf4fdb6143cffc4eb0d1abe64/shm...
         Unmounting /var/lib/kubelet/pods/2c...ojected/kube-api-access-vr5m7...
         Unmounting /run/containerd/io.conta...e91fa769cf7c60278212d3/rootfs...
         Unmounting /var/lib/kubelet/pods/7f...ess-ingress-nginx-token-kzkb6...
         Unmounting /run/containerd/io.conta...efe5c7b113ada28be8c995/rootfs...
         Unmounting /run/containerd/io.conta...dc9c21c67cea1ed3c00c4f/rootfs...
         Unmounting /run/netns/cni-f016ad0e-9638-5947-9e4c-c2c5e60dd639...
         Unmounting /run/containerd/io.conta...c258abd1e7529bbb7ca556/rootfs...
         Unmounting /var/lib/kubelet/pods/7b...ephfs-provisioner-token-66nh6...
         Unmounting /var/lib/kubelet/pods/16...ubernetes.io~secret/https-tls...
         Unmounting /run/netns/cni-7206c30f-afa4-ab39-9c9a-647755cb225f...
         Unmounting /var/lib/kubelet/pods/d7...ubernetes.io~secret/https-tls...
         Unmounting /run/containerd/io.conta...8bc7585948ec3872d3cfdff88/shm...
         Unmounting /run/containerd/io.conta...7dc2a576c0ee930f729ab4/rootfs...
         Unmounting /var/lib/ceph/mon...
         Unmounting /opt/platform-backup...
         Unmounting /run/containerd/io.conta...7585948ec3872d3cfdff88/rootfs...
         Unmounting /run/containerd/io.conta...8949ff642dc7b25b3f909e/rootfs...
         Unmounting /run/netns/cni-af936a23-3f92-b586-3477-e4d74357c33f...
         Unmounting /run/containerd/io.conta...d3c1aee20c2518fcf12ec76b7/shm...
         Unmounting /sys/fs/bpf...
         Unmounting /run/netns/cni-d236dd87-a859-87a4-3748-391ae82c414b...
         Unmounting /var/lib/kubelet/pods/f1...-kube-controllers-token-5cqdv...
         Unmounting /run/containerd/io.conta...fdb6143cffc4eb0d1abe64/rootfs...
         Unmounting /run/netns/cni-5f5eb862-c89b-a775-9de9-54133406d727...
         Unmounting /run/netns/cni-97f041e9-b6b3-78d6-7cc4-305818489ca7...
         Unmounting /run/containerd/io.conta...f5609d19b0905a507101f1/rootfs...
         Unmounting /var/lib/kubelet/pods/d7...ojected/kube-api-access-prvjb...
         Unmounting /run/containerd/io.conta...458f5609d19b0905a507101f1/shm...
         Unmounting /var/lib/kubelet/pods/16...s/kubernetes.io~secret/config...
         Unmounting /var/lib/kubelet/pods/16...ernetes.io~secret/grpc-tls-ca...
         Unmounting /run/containerd/io.conta...e47514e215a3012a3ba32ed51/shm...
         Unmounting /var/lib/kubelet/pods/13...io~secret/default-token-67jx9...
         Unmounting /run/netns/cni-0d7a9579-4efb-ed05-fc3c-0874027e6ebf...
         Unmounting /run/containerd/io.conta...0d9d52465e35073b7710ed127/shm...
         Unmounting /var/lib/kubelet/pods/f6...t/cm-cert-manager-token-k62mc...
         Unmounting /var/lib/kubelet/pods/d7...cret/dex-client-secret-volume...
         Unmounting /var/lib/kubelet/pods/5d...ms-metrics-server-token-5k224...
         Unmounting /run/containerd/io.conta...2d5cc1806616b2d84f925a/rootfs...
         Unmounting /usr/local/kubernetes/current/stage2...
         Unmounting /run/containerd/io.conta...48939240b9d4b84b921d97c26/shm...
         Unmounting /run/containerd/io.conta...10a2d5cc1806616b2d84f925a/shm...
         Unmounting Temporary Directory...
         Unmounting /run/containerd/io.conta...d52465e35073b7710ed127/rootfs...
         Unmounting /run/containerd/io.conta...cd6199d15c5d4bb780c5d1607/shm...
         Unmounting /run/containerd/io.conta...77fe91fa769cf7c60278212d3/shm...
         Unmounting /run/containerd/io.conta...199d15c5d4bb780c5d1607/rootfs...
         Unmounting /run/containerd/io.conta...7a900c09831002e4621923/rootfs...
         Unmounting /run/containerd/io.conta...aa8f67b57c9f0d36cde0df/rootfs...
         Unmounting /run/containerd/io.conta...469fb452211e3d08a6f1949a4/shm...
         Unmounting /run/containerd/io.conta...db4f7184045dc07004b5d47bb/shm...
         Unmounting /run/containerd/io.conta...18bdc9c21c67cea1ed3c00c4f/shm...
         Unmounting /run/containerd/io.conta...92bc258abd1e7529bbb7ca556/shm...
         Unmounting /run/containerd/io.conta...39240b9d4b84b921d97c26/rootfs...
         Unmounting /var/lib/ceph/osd/ceph-0...
         Unmounting /run/containerd/io.conta...2c97a900c09831002e4621923/shm...
         Unmounting /var/lib/kubelet/pods/ac....io~secret/multus-token-hp9st...
         Unmounting /var/lib/kubelet/pods/8b...ret/dm-monitor-sa-token-lc6tr...
         Unmounting /var/lib/kubelet/pods/e9...secret/armada-api-token-k7jv7...
         Unmounting /run/containerd/io.conta...4107dc2a576c0ee930f729ab4/shm...
         Unmounting /var/lib/kubelet/pods/16...tes.io~secret/grpc-tls-server...
         Unmounting /var/lib/kubelet/pods/13...mes/kubernetes.io~secret/cert...
         Unmounting /run/containerd/io.conta...fb452211e3d08a6f1949a4/rootfs...
[  OK  ] Stopped Flush Journal to Persistent Storage.
         Unmounting /var/log...
[  OK  ] Stopped Configure read-only root support.
[  OK  ] Unmounted /usr/local/kubernetes/current/stage1.
[  OK  ] Unmounted /var/lib/kubelet/pods/c7a...s.io~secret/default-token-gq26j.
[  OK  ] Unmounted /run/containerd/io.contai...3c1aee20c2518fcf12ec76b7/rootfs.
[  OK  ] Unmounted /run/netns/cni-6b372a07-1905-3e02-145b-b39a636ffc5d.
[  OK  ] Unmounted /run/user/42425.
[  OK  ] Unmounted /mnt/huge-2048kB.
[  OK  ] Unmounted /var/lib/kubelet/pods/401...ert-manager-webhook-token-fb8hr.
[  OK  ] Unmounted /run/containerd/io.contai...07c19aa8f67b57c9f0d36cde0df/shm.
[  OK  ] Unmounted /run/containerd/io.contai...11240efe5c7b113ada28be8c995/shm.
[  OK  ] Unmounted /var/lib/kubelet/pods/454...~secret/calico-node-token-ldgqw.
[  OK  ] Unmounted /mnt/huge-1048576kB.
[  OK  ] Unmounted /run/containerd/io.contai...47514e215a3012a3ba32ed51/rootfs.
[  OK  ] Unmounted /run/containerd/io.contai...7fa538949ff642dc7b25b3f909e/shm.
[  OK  ] Unmounted /scratch.
[  OK  ] Unmounted /run/containerd/io.contai...3a92bd0c4d9f4127c28055b5/rootfs.
[  OK  ] Unmounted /var/lib/kubelet/pods/167...projected/kube-api-access-b7szn.
[  OK  ] Unmounted /var/lib/kubelet/pods/183...sriov-device-plugin-token-2v9n4.
[  OK  ] Unmounted /run/netns/cni-6847d3a4-d760-0a02-5553-39238666cccd.
[  OK  ] Unmounted /var/lib/kubelet/pods/9d0...-manager-cainjector-token-xpzvc.
[  OK  ] Unmounted /run/netns/cni-234716cc-2e72-b9e8-d821-98f942da0e60.
[  OK  ] Unmounted /run/containerd/io.contai...ff3732f3e7aaa2e503ddd207/rootfs.
[  OK  ] Unmounted /run/containerd/io.contai...7ec94ea50fa570cf0577a9fa977/shm.
[  OK  ] Unmounted /var/lib/kubelet/pods/ac5...projected/kube-api-access-tmgr8.
[  OK  ] Unmounted /var/lib/kubelet/pods/167...es/kubernetes.io~secret/certdir.
[  OK  ] Unmounted /run/containerd/io.contai...1ec3a92bd0c4d9f4127c28055b5/shm.
[  OK  ] Unmounted /run/containerd/io.contai...94ea50fa570cf0577a9fa977/rootfs.
[  OK  ] Unmounted /var/lib/kubelet/pods/65b...ret/rbd-provisioner-token-fj69f.
[  OK  ] Unmounted /var/lib/docker.
[  OK  ] Unmounted /run/containerd/io.contai...545ff3732f3e7aaa2e503ddd207/shm.
[  OK  ] Unmounted /run/netns/cni-ad0e07d7-5b64-1553-dec9-0295c6f9e241.
[  OK  ] Unmounted /run/netns/cni-0a4a3263-7887-36ef-3ca9-40f44f5ea96f.
[  OK  ] Unmounted /var/lib/kubelet/pods/7fb...bernetes.io~secret/webhook-cert.
[  OK  ] Unmounted /run/netns/cni-a6584c78-d8f3-c3e4-8805-3c0bc4da39e3.
[  OK  ] Unmounted /run/netns/cni-7b06068f-1460-5fff-4353-5c7de64e0817.
[  OK  ] Unmounted /run/containerd/io.contai...b4f7184045dc07004b5d47bb/rootfs.
[  OK  ] Unmounted /run/containerd/io.contai...91cf4fdb6143cffc4eb0d1abe64/shm.
[  OK  ] Unmounted /var/lib/kubelet/pods/2c4...projected/kube-api-access-vr5m7.
[  OK  ] Unmounted /run/containerd/io.contai...7fe91fa769cf7c60278212d3/rootfs.
[  OK  ] Unmounted /var/lib/kubelet/pods/7fb...gress-ingress-nginx-token-kzkb6.
[  OK  ] Unmounted /run/containerd/io.contai...40efe5c7b113ada28be8c995/rootfs.
[  OK  ] Unmounted /run/containerd/io.contai...8bdc9c21c67cea1ed3c00c4f/rootfs.
[  OK  ] Unmounted /run/netns/cni-f016ad0e-9638-5947-9e4c-c2c5e60dd639.
[  OK  ] Unmounted /run/containerd/io.contai...2bc258abd1e7529bbb7ca556/rootfs.
[  OK  ] Unmounted /var/lib/kubelet/pods/7b4.../cephfs-provisioner-token-66nh6.
[  OK  ] Unmounted /var/lib/kubelet/pods/167.../kubernetes.io~secret/https-tls.
[  OK  ] Unmounted /run/netns/cni-7206c30f-afa4-ab39-9c9a-647755cb225f.
[  OK  ] Unmounted /var/lib/kubelet/pods/d7a.../kubernetes.io~secret/https-tls.
[  OK  ] Unmounted /run/containerd/io.contai...6a8bc7585948ec3872d3cfdff88/shm.
[  OK  ] Unmounted /run/containerd/io.contai...107dc2a576c0ee930f729ab4/rootfs.
[  OK  ] Unmounted /var/lib/ceph/mon.
[  OK  ] Unmounted /opt/platform-backup.
[  OK  ] Unmounted /run/containerd/io.contai...bc7585948ec3872d3cfdff88/rootfs.
[  OK  ] Unmounted /run/containerd/io.contai...538949ff642dc7b25b3f909e/rootfs.
[  OK  ] Unmounted /run/netns/cni-af936a23-3f92-b586-3477-e4d74357c33f.
[  OK  ] Unmounted /run/containerd/io.contai...bad3c1aee20c2518fcf12ec76b7/shm.
[  OK  ] Unmounted /sys/fs/bpf.
[  OK  ] Unmounted /run/netns/cni-d236dd87-a859-87a4-3748-391ae82c414b.
[  OK  ] Unmounted /var/lib/kubelet/pods/f1a...co-kube-controllers-token-5cqdv.
[  OK  ] Unmounted /run/containerd/io.contai...f4fdb6143cffc4eb0d1abe64/rootfs.
[  OK  ] Unmounted /run/netns/cni-5f5eb862-c89b-a775-9de9-54133406d727.
[  OK  ] Unmounted /run/netns/cni-97f041e9-b6b3-78d6-7cc4-305818489ca7.
[  OK  ] Unmounted /run/containerd/io.contai...58f5609d19b0905a507101f1/rootfs.
[  OK  ] Unmounted /var/lib/kubelet/pods/d7a...projected/kube-api-access-prvjb.
[  OK  ] Unmounted /run/containerd/io.contai...3f458f5609d19b0905a507101f1/shm.
[  OK  ] Unmounted /var/lib/kubelet/pods/167...mes/kubernetes.io~secret/config.
[  OK  ] Unmounted /var/lib/kubelet/pods/167...ubernetes.io~secret/grpc-tls-ca.
[  OK  ] Unmounted /run/containerd/io.contai...6de47514e215a3012a3ba32ed51/shm.
[  OK  ] Unmounted /var/lib/kubelet/pods/13a...s.io~secret/default-token-67jx9.
[  OK  ] Unmounted /run/netns/cni-0d7a9579-4efb-ed05-fc3c-0874027e6ebf.
[  OK  ] Unmounted /run/containerd/io.contai...050d9d52465e35073b7710ed127/shm.
[  OK  ] Unmounted /var/lib/kubelet/pods/f63...ret/cm-cert-manager-token-k62mc.
[  OK  ] Unmounted /var/lib/kubelet/pods/d7a...secret/dex-client-secret-volume.
[  OK  ] Unmounted /var/lib/kubelet/pods/5dd...t/ms-metrics-server-token-5k224.
[  OK  ] Unmounted /run/containerd/io.contai...0a2d5cc1806616b2d84f925a/rootfs.
[  OK  ] Unmounted /usr/local/kubernetes/current/stage2.
[  OK  ] Unmounted /run/containerd/io.contai...b148939240b9d4b84b921d97c26/shm.
[  OK  ] Unmounted /run/containerd/io.contai...6d10a2d5cc1806616b2d84f925a/shm.
[  OK  ] Unmounted Temporary Directory.
[  OK  ] Unmounted /run/containerd/io.contai...d9d52465e35073b7710ed127/rootfs.
[  OK  ] Unmounted /run/containerd/io.contai...40cd6199d15c5d4bb780c5d1607/shm.
[  OK  ] Unmounted /run/containerd/io.contai...f877fe91fa769cf7c60278212d3/shm.
[  OK  ] Unmounted /run/containerd/io.contai...d6199d15c5d4bb780c5d1607/rootfs.
[  OK  ] Unmounted /run/containerd/io.contai...c97a900c09831002e4621923/rootfs.
[  OK  ] Unmounted /run/containerd/io.contai...19aa8f67b57c9f0d36cde0df/rootfs.
[  OK  ] Unmounted /run/containerd/io.contai...a5469fb452211e3d08a6f1949a4/shm.
[  OK  ] Unmounted /run/containerd/io.contai...49db4f7184045dc07004b5d47bb/shm.
[  OK  ] Unmounted /run/containerd/io.contai...d718bdc9c21c67cea1ed3c00c4f/shm.
[  OK  ] Unmounted /run/containerd/io.contai...0492bc258abd1e7529bbb7ca556/shm.
[  OK  ] Unmounted /run/containerd/io.contai...8939240b9d4b84b921d97c26/rootfs.
[  OK  ] Unmounted /var/lib/ceph/osd/ceph-0.
[  OK  ] Unmounted /run/containerd/io.contai...092c97a900c09831002e4621923/shm.
[  OK  ] Unmounted /var/lib/kubelet/pods/ac4...es.io~secret/multus-token-hp9st.
[  OK  ] Unmounted /var/lib/kubelet/pods/8bf...ecret/dm-monitor-sa-token-lc6tr.
[  OK  ] Unmounted /var/lib/kubelet/pods/e9f...o~secret/armada-api-token-k7jv7.
[  OK  ] Unmounted /run/containerd/io.contai...524107dc2a576c0ee930f729ab4/shm.
[  OK  ] Unmounted /var/lib/kubelet/pods/167...netes.io~secret/grpc-tls-server.
[  OK  ] Unmounted /var/lib/kubelet/pods/13a...lumes/kubernetes.io~secret/cert.
[  OK  ] Unmounted /run/containerd/io.contai...69fb452211e3d08a6f1949a4/rootfs.
[  OK  ] Unmounted /var/log.
[  OK  ] Stopped File System Check on /dev/mapper/cgts--vg-log--lv.
[  OK  ] Stopped File System Check on /dev/d...b5b-2f8f-4799-b14a-4ee003a7551b.
[  OK  ] Removed slice system-systemd\x2dfsck.slice.
[  OK  ] Stopped target Swap.
         Unmounting /var/lib/kubelet...
[  OK  ] Unmounted /var/lib/kubelet.
[  OK  ] Reached target Unmount All Filesystems.
[  OK  ] Stopped target Local File Systems (Pre).
[  OK  ] Stopped Create Static Device Nodes in /dev.
[  OK  ] Stopped Remount Root and Kernel File Systems.
[  OK  ] Reached target Shutdown.
[60816.368600] nfsd: last server has exited, flushing export cache
[60825.157964] block drbd8: role( Primary -> Secondary )
[60825.158011] block drbd8: 100 GB (26213591 bits) marked out-of-sync by on disk bit-map.
[60825.161120] block drbd5: role( Primary -> Secondary )
[60825.161152] block drbd5: 1024 MB (262127 bits) marked out-of-sync by on disk bit-map.
[60825.177926] drbd drbd-dockerdistribution: conn( WFConnection -> Disconnecting )
[60825.177933] drbd drbd-dockerdistribution: Discarding network configuration.
[60825.177994] drbd drbd-dockerdistribution: Connection closed
[60825.178004] drbd drbd-dockerdistribution: conn( Disconnecting -> StandAlone )
[60825.178008] drbd drbd-dockerdistribution: receiver terminated
[60825.178011] drbd drbd-dockerdistribution: Terminating drbd_r_drbd-doc
[60825.178195] block drbd8: disk( UpToDate -> Failed )
[60825.187415] block drbd8: 100 GB (26213591 bits) marked out-of-sync by on disk bit-map.
[60825.187421] block drbd8: disk( Failed -> Diskless )
[60825.214436] drbd drbd-dockerdistribution: Terminating drbd_w_drbd-doc
[60825.222493] drbd drbd-extension: conn( WFConnection -> Disconnecting )
[60825.222499] drbd drbd-extension: Discarding network configuration.
[60825.222549] drbd drbd-extension: Connection closed
[60825.222558] drbd drbd-extension: conn( Disconnecting -> StandAlone )
[60825.222561] drbd drbd-extension: receiver terminated
[60825.222564] drbd drbd-extension: Terminating drbd_r_drbd-ext
[60825.222669] block drbd5: disk( UpToDate -> Failed )
[60825.235387] block drbd5: 1024 MB (262127 bits) marked out-of-sync by on disk bit-map.
[60825.235401] block drbd5: disk( Failed -> Diskless )
[60825.268193] drbd drbd-extension: Terminating drbd_w_drbd-ext
[60825.291466] block drbd7: role( Primary -> Secondary )
[60825.291490] block drbd7: 5120 MB (1310671 bits) marked out-of-sync by on disk bit-map.
[60826.300693] drbd drbd-etcd: conn( WFConnection -> Disconnecting )
[60826.300701] drbd drbd-etcd: Discarding network configuration.
[60826.300733] drbd drbd-etcd: Connection closed
[60826.300742] drbd drbd-etcd: conn( Disconnecting -> StandAlone )
[60826.300746] drbd drbd-etcd: receiver terminated
[60826.300749] drbd drbd-etcd: Terminating drbd_r_drbd-etc
[60826.300759] block drbd7: disk( UpToDate -> Failed )
[60826.306119] block drbd7: 5120 MB (1310671 bits) marked out-of-sync by on disk bit-map.
[60826.306127] block drbd7: disk( Failed -> Diskless )
[60826.329444] drbd drbd-etcd: Terminating drbd_w_drbd-etc
[60839.238407] block drbd2: role( Primary -> Secondary )
[60839.238468] block drbd2: 10 GB (2621351 bits) marked out-of-sync by on disk bit-map.
[60839.260386] drbd drbd-platform: conn( WFConnection -> Disconnecting )
[60839.260395] drbd drbd-platform: Discarding network configuration.
[60839.260442] drbd drbd-platform: Connection closed
[60839.260453] drbd drbd-platform: conn( Disconnecting -> StandAlone )
[60839.260457] drbd drbd-platform: receiver terminated
[60839.260462] drbd drbd-platform: Terminating drbd_r_drbd-pla
[60839.260483] block drbd2: disk( UpToDate -> Failed )
[60839.270906] block drbd2: 10 GB (2621351 bits) marked out-of-sync by on disk bit-map.
[60839.270912] block drbd2: disk( Failed -> Diskless )
[60839.293984] drbd drbd-platform: Terminating drbd_w_drbd-pla
[60839.684873] block drbd0: role( Primary -> Secondary )
[60839.684899] block drbd0: 20 GB (5242711 bits) marked out-of-sync by on disk bit-map.
[60839.692398] drbd drbd-pgsql: conn( WFConnection -> Disconnecting )
[60839.692405] drbd drbd-pgsql: Discarding network configuration.
[60839.692438] drbd drbd-pgsql: Connection closed
[60839.692444] drbd drbd-pgsql: conn( Disconnecting -> StandAlone )
[60839.692447] drbd drbd-pgsql: receiver terminated
[60839.692449] drbd drbd-pgsql: Terminating drbd_r_drbd-pgs
[60839.692457] block drbd0: disk( UpToDate -> Failed )
[60839.701895] block drbd0: 20 GB (5242711 bits) marked out-of-sync by on disk bit-map.
[60839.701902] block drbd0: disk( Failed -> Diskless )
[60839.726931] drbd drbd-pgsql: Terminating drbd_w_drbd-pgs
[60844.219652] block drbd1: role( Primary -> Secondary )
[60844.219683] block drbd1: 2048 MB (524263 bits) marked out-of-sync by on disk bit-map.
[60844.228118] drbd drbd-rabbit: conn( WFConnection -> Disconnecting )
[60844.228125] drbd drbd-rabbit: Discarding network configuration.
[60844.228157] drbd drbd-rabbit: Connection closed
[60844.228163] drbd drbd-rabbit: conn( Disconnecting -> StandAlone )
[60844.228165] drbd drbd-rabbit: receiver terminated
[60844.228168] drbd drbd-rabbit: Terminating drbd_r_drbd-rab
[60844.228176] block drbd1: disk( UpToDate -> Failed )
[60844.236052] block drbd1: 2048 MB (524263 bits) marked out-of-sync by on disk bit-map.
[60844.236062] block drbd1: disk( Failed -> Diskless )
[60844.264863] drbd drbd-rabbit: Terminating drbd_w_drbd-rab
[60860.934850] drbd: module cleanup done.
[60864.063132] XFS (nvme1n1p1): Unmounting Filesystem
[60865.256115] systemd-shutdown[1]: Syncing filesystems and block devices.
[60865.256472] systemd-shutdown[1]: Sending SIGTERM to remaining processes...
[60865.279046] systemd-journald[1034]: Received SIGTERM from PID 1 (systemd-shutdow).
[60865.751639] XFS (dm-2): Unmounting Filesystem
[60875.280216] systemd-shutdown[1]: Sending SIGKILL to remaining processes...
[60875.298348] systemd-shutdown[1]: Sending SIGKILL to PID 529796 (containerd-shim).
[60875.298448] systemd-shutdown[1]: Sending SIGKILL to PID 571975 (containerd-shim).
[60875.298538] systemd-shutdown[1]: Sending SIGKILL to PID 572266 (containerd-shim).
[60875.298625] systemd-shutdown[1]: Sending SIGKILL to PID 572552 (containerd-shim).
[60875.298710] systemd-shutdown[1]: Sending SIGKILL to PID 572993 (containerd-shim).
[60875.298798] systemd-shutdown[1]: Sending SIGKILL to PID 573587 (containerd-shim).
[60875.298894] systemd-shutdown[1]: Sending SIGKILL to PID 573597 (containerd-shim).
[60875.298971] systemd-shutdown[1]: Sending SIGKILL to PID 574541 (containerd-shim).
[60875.299080] systemd-shutdown[1]: Sending SIGKILL to PID 575276 (containerd-shim).
[60875.402453] EXT4-fs (nvme0n1p4): re-mounted. Opts:
[60875.761807] kvm: exiting hardware virtualization
[60878.136149] sd 9:0:0:0: [sdb] Synchronizing SCSI cache
[60878.136195] sd 9:0:0:0: [sdb] Stopping disk
[60879.187696] sd 8:0:0:0: [sda] Synchronizing SCSI cache
[60879.187741] sd 8:0:0:0: [sda] Stopping disk
[60885.357448] ACPI: Preparing to enter system sleep state S5
[60885.368447] reboot: Power down
[60885.368448] printk: enabled sync mode
[60885.945895] printk: console [ttyS0]: printing thread stopped
[60886.048545] acpi_power_off called

```

### subcloud wiped and powered off 

### Now delete subcloud from controller

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ dcmanager subcloud list
+----+------------------------+------------+--------------+---------------+-------------+
| id | name                   | management | availability | deploy status | sync        |
+----+------------------------+------------+--------------+---------------+-------------+
|  2 | rchltxfe-d93180012-001 | unmanaged  | online       | complete      | out-of-sync |
|  3 | welktxef-d931881-005   | managed    | online       | complete      | in-sync     |
|  6 | welktxef-d931884-034   | managed    | online       | complete      | in-sync     |
+----+------------------------+------------+--------------+---------------+-------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ dcmanager subcloud delete rchltxfe-d93180012-001
[XXXXXX@controller-0 ~(keystone_admin)]$ dcmanager subcloud list
+----+----------------------+------------+--------------+---------------+---------+
| id | name                 | management | availability | deploy status | sync    |
+----+----------------------+------------+--------------+---------------+---------+
|  3 | welktxef-d931881-005 | managed    | online       | complete      | in-sync |
|  6 | welktxef-d931884-034 | managed    | online       | complete      | in-sync |
+----+----------------------+------------+--------------+---------------+---------+
[XXXXXX@controller-0 ~(keystone_admin)]$

```

### Now start automation deployment of the subcloud

```log
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 wr-installer]$ source ~/python_venvs/ansible_2.10.15/bin/activate
(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 wr-installer]$ ansible-playbook --vault-password-file /tmp/vault-pass -i inventory/rchltxfe-d93180012-001.yaml wr_remote.yaml

PLAY [Wind River Remote Subcloud Installer] ***************************************************************************

TASK [Download Files] *************************************************************************************************

TASK [common/download_files : Check if artifact files exist locally] **************************************************
ok: [rchltxfe-93180012-rz-le0trtn-001 -> localhost]

TASK [common/download_files : Download & unarchive artifact files to local directory if they don't exist] *************
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [Setup] **********************************************************************************************************

TASK [common/setup : Create temporary working directory] **************************************************************
changed: [rchltxfe-93180012-rz-le0trtn-001 -> localhost]

TASK [common/setup : Set temporary working directory path] ************************************************************
ok: [rchltxfe-93180012-rz-le0trtn-001]

TASK [Remote Configure] ***********************************************************************************************

TASK [remote/remote-configure : Set facts for vip, ansible, and wr_admin] *********************************************
ok: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/remote-configure : Set facts for wr_release_version] *****************************************************
ok: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/remote-configure : Print wr_release_version] *************************************************************
ok: [rchltxfe-93180012-rz-le0trtn-001] => {
    "msg": "wr_release_version: 21.12"
}

TASK [remote/remote-configure : Set fact wr_distribution_directory to use based on WR version] ************************
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/remote-configure : Set fact wr_distribution_directory to use based on WR version] ************************
ok: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/remote-configure : Set facts for which image list to use based on WR version] ****************************
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/remote-configure : Set facts for which image list to use based on WR version] ****************************
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/remote-configure : Set facts for which image list to use based on WR version] ****************************
ok: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/remote-configure : Print wr_image_list] ******************************************************************
ok: [rchltxfe-93180012-rz-le0trtn-001] => {
    "msg": "wr_image_list: /opt/external/vcpfe-team/artifacts/WRCP-2112/wind-river-cloud-platform-container-images-list-21.12.txt"
}

TASK [remote/remote-configure : Set fact to wr_license_key] ***********************************************************
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/remote-configure : Set fact to wr_license_key] ***********************************************************
ok: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/remote-configure : print wr_license_key] *****************************************************************
ok: [rchltxfe-93180012-rz-le0trtn-001] => {
    "msg": "wr_license_key = IyBXaW5kIFJpdmVyIFByb2R1Y3QgQWN0aXZhdGlvbiBGaWxlIChpbnN0YWxsLnR4dCkKIyBJc3N1ZWQgZm9yIGhvc3Q6IDxWZXJpem9uPiA8VmVyaXpvbj4gPEFueT4KIyBMaWNlbnNlIG51bWJlcihzKTogNjgyMzc0CiMgSXNzdWVkIG9uOiAyNi1qYW4tMjAyMiAwOTo1MDo1MAojCiMgTm90ZTogdGhpcyBsaWNlbnNlIGlzIGdlbmVyYXRlZCBjdW11bGF0aXZlbHkgZm9yIGFsbAojIFdpbmQgUml2ZXIgc29mdHdhcmUgbWFuYWdlZCBieSB0aGlzIGhvc3QuCgojIDEuIEZsZXhMTSBsaWNlbnNlIGZpbGU6CiMgQmVnaW46IFNlcnZlciBsaWNlbnNlICAtLS0tLS0tLS0tLS0tLS0tLS0tLS0KIyBTZXJpYWwgTnVtYmVyOiA2ODQ0NDktVmVyaXpvblBPQy1HNFdEQzlDUEVLCgpQQUNLQUdFIFdSQ1BfQ09OVEFJTkVSX1BLRyB3cnNkIDIxIDAwNDY1REZDRUI5QiBcCglDT01QT05FTlRTPVdSQ1BfQ09OVEFJTkVSOjIxLjEyIE9QVElPTlM9U1VJVEUgXAoJU0lHTj0yNTAwQzhCMjRFRDAKSU5DUkVNRU5UIFdSQ1BfQ09OVEFJTkVSX1BLRyB3cnNkIDIxIHBlcm1hbmVudCB1bmNvdW50ZWQgNDQyRThBMzg2QUE4IFwKCVZFTkRPUl9TVFJJTkc9PGxuPjY4MjM3NDwvbG4+PHBzPjIyMTMtNDM8L3BzPiBIT1NUSUQ9QU5ZIFwKCUlTU1VFRD0yNi1qYW4tMjAyMiBTTj1zZXJpYWwtVmVyaXpvbi1MVjJJV0FVTEVCIFwKCVNUQVJUPTI2LWphbi0yMDIyIFNJR049QjUzNzk2OTBENEE2Cg=="
}

TASK [remote/remote-configure : Copy storage checking script if server is HPE-LS3-e910] *******************************
skipping: [rchltxfe-93180012-rz-le0trtn-001] => (item=hpe_storage_check.py)

TASK [remote/remote-configure : Execute storage checking script if server is HPE-LS3-e910] ****************************
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor HPE HPE-LS3-e910 (4 disks)] ****
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor HPE HPE-LS3-e910 (2 disks)] ****
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor HPE HPE-LS3-92s3] **************
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor HPE HPE-LS6-92s6] **************
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor ZTS ZTS-LS3-trtn] **************
ok: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/remote-configure : Set facts for Corning] ****************************************************************
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor ZTS ZTS-LS6-pts6 & ZTS-LS3-pts3] ***
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/remote-configure : Set facts for disk device and main nic based on vendor ZTS ZTS-LS6-aks6 & ZTS-LS3-aks3] ***
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/remote-configure : set_fact] *****************************************************************************
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [include_role : remote/zt-redfish] *******************************************************************************
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/remote-configure : Set facts for BIOS version based on vendor ZTS ZTS-LS6-pts6 & ZTS-LS3-pts3] ***********
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/remote-configure : debug] ********************************************************************************
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/remote-configure : Find out which DM Docker version contral has] *****************************************
changed: [rchltxfe-93180012-rz-le0trtn-001 -> rchltxib-c000000-003]

TASK [remote/remote-configure : Find out which DM file version contral has] *******************************************
changed: [rchltxfe-93180012-rz-le0trtn-001 -> rchltxib-c000000-003]

TASK [remote/remote-configure : Print dm docker version and dm file version] ******************************************
ok: [rchltxfe-93180012-rz-le0trtn-001] => {
    "msg": "dm_docker_version: WRCP_21.12-wrs.4, dm_file: wind-river-cloud-platform-deployment-manager-2.0.8-4.tgz"
}

TASK [remote/remote-configure : Discover Wind River docker image names] ***********************************************
changed: [rchltxfe-93180012-rz-le0trtn-001 -> localhost]

TASK [remote/remote-configure : Print local_images_full] **************************************************************
ok: [rchltxfe-93180012-rz-le0trtn-001] => {
    "msg": "docker.io/starlingx/ceph-config-helper:v1.15.0\ndocker.io/starlingx/dex:stx.4.0-v2.14.0-1\ndocker.io/starlingx/n3000-opae:stx.6.0-v1.0.1\ndocker.io/starlingx/stx-oidc-client:stx.5.0-v1.0.4\ndocker.io/wind-river/cloud-platform-deployment-manager:WRCP_21.12-wrs.4\ngcr.io/google_containers/kubernetes-dashboard-init-amd64:v1.0.0\ngcr.io/kubebuilder/kube-rbac-proxy:v0.4.0\nquay.io/external_storage/rbd-provisioner:v2.1.1-k8s1.11"
}

TASK [remote/remote-configure : Create fact for Wind River docker image names] ****************************************
ok: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/remote-configure : Determine DM Helm Chart path] *********************************************************
ok: [rchltxfe-93180012-rz-le0trtn-001 -> localhost]

TASK [remote/remote-configure : Print dm_helm_chart] ******************************************************************
ok: [rchltxfe-93180012-rz-le0trtn-001] => {
    "msg": "/opt/external/vcpfe-team/artifacts/WRCP-2112/wind-river-cloud-platform-deployment-manager-2.0.8-4.tgz"
}

TASK [remote/remote-configure : Set DM Helm Chart file] ***************************************************************
ok: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/remote-configure : Lookup Deployment Manager image tag] **************************************************
changed: [rchltxfe-93180012-rz-le0trtn-001 -> localhost]

TASK [remote/remote-configure : Lookup RBAC Proxy image tag] **********************************************************
changed: [rchltxfe-93180012-rz-le0trtn-001 -> localhost]

TASK [remote/remote-configure : Copy WRCP DM Playbook] ****************************************************************
ok: [rchltxfe-93180012-rz-le0trtn-001 -> rchltxib-c000000-003] => (item=wind-river-cloud-platform-deployment-manager.yaml)
ok: [rchltxfe-93180012-rz-le0trtn-001 -> rchltxib-c000000-003] => (item=wind-river-cloud-platform-deployment-manager-2.0.8-4.tgz)

TASK [remote/remote-configure : Set a fact for the central controller VIP address] ************************************
ok: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/remote-configure : Configure WRCP seed template] *********************************************************
changed: [rchltxfe-93180012-rz-le0trtn-001 -> rchltxib-c000000-003] => (item={'src': 'bootstrap-values.yaml', 'dest': 'rchltxfe-d93180012-001-bootstrap-values.yaml'})
changed: [rchltxfe-93180012-rz-le0trtn-001 -> rchltxib-c000000-003] => (item={'src': 'deploy-values.yaml', 'dest': 'rchltxfe-d93180012-001-deploy-values.yaml'})
changed: [rchltxfe-93180012-rz-le0trtn-001 -> rchltxib-c000000-003] => (item={'src': 'deploy-standard.yaml', 'dest': 'rchltxfe-d93180012-001-deploy-standard.yaml'})
changed: [rchltxfe-93180012-rz-le0trtn-001 -> rchltxib-c000000-003] => (item={'src': 'install-values.yaml', 'dest': 'rchltxfe-d93180012-001-install-values.yaml'})

TASK [remote/remote-configure : Copy SSL cert files] ******************************************************************
ok: [rchltxfe-93180012-rz-le0trtn-001 -> rchltxib-c000000-003] => (item={'filename': 'k8s_root_ca_cert.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIF8jCCA9qgAwIBAgIJAIf9Ql2uDZh+MA0GCSqGSIb3DQEBDQUAMIGFMQswCQYD\nVQQGEwJVUzEOMAwGA1UECAwFVGV4YXMxETAPBgNVBAcMCFdlc3RsYWtlMR0wGwYD\nVQQKDBRWZXJpem9uIFNvdXJjaW5nIExMQzE0MDIGA1UEAwwrVmVyaXpvbiBOZXR3\nb3JrIFdFTEtUWElCIExBQiAxIDMgUlNBIEs4UyBDQTAeFw0yMDEwMjUyMjEyNDha\nFw0zMDEwMjMyMjEyNDhaMIGFMQswCQYDVQQGEwJVUzEOMAwGA1UECAwFVGV4YXMx\nETAPBgNVBAcMCFdlc3RsYWtlMR0wGwYDVQQKDBRWZXJpem9uIFNvdXJjaW5nIExM\nQzE0MDIGA1UEAwwrVmVyaXpvbiBOZXR3b3JrIFdFTEtUWElCIExBQiAxIDMgUlNB\nIEs4UyBDQTCCAiIwDQYJKoZIhvcNAQEBBQADggIPADCCAgoCggIBAKyF9svdv/qG\n7HxBr1DWvZ3CQiDsA4m1kj0hD7jo3B3W/32ODcPpgeNmp4Oful0SsndpqEGhXDq5\noiBfqszMUpzDgdQ7siIHekb2olFEK2KniMP3H53nilIppeyMby5K3ZwF0Qbmk5WK\ncoXoYegP+Uv9bV0AMH6Dn4CVgYrLAYfmPyGgUSt4vuZ9F/rf9UkBf/DcZGqMnMax\n/Gfaq8KwmDzD9D8IVCHPrM5f4+CaKMQCFu5QkSsLYJFRiuQWWaICMMdnqpb0HZh5\niPnCSHwPPUyXxtujdI97Ovy4X5WR46jJ2+KzPYe8tVa/DL3TlKmRL9AF+oSE17bw\nzGAE7GNWxPojebHIUuoKdOQC1qiJBVS+c14r9+9P2Uy6XEhNUs+h3juRI4U3YkQ1\nUCUU3opqhOPh4jUIuPGg5aX07lt4Wpxc48D+CY1D4i6vaJLl3WCsVK7PFwWVQQEW\nIQabfuj1R2jEu7pp2Yabza58S00v1P5/kv/DNr7ADm8eYRvxLAAXCedMeSDXKBgd\npPmVXXZoZ8+X8VRGYxcw0mBBLIAiTOntT2vgLeq5T3QyiVKdU6TLAYEjS65QZ3Eg\naIX0wRqlcQI7lruTXubtENG6wWXYtnDf5795ZID1YIEqkgzZLMBqq1SBiLnWd6aK\n78Zsr4j5GmTBGpKRmwE2oO1btJCCYyG5AgMBAAGjYzBhMA8GA1UdEwEB/wQFMAMB\nAf8wHQYDVR0OBBYEFEDQ5EaGp3x02WUuvqetygqpM3dCMB8GA1UdIwQYMBaAFEDQ\n5EaGp3x02WUuvqetygqpM3dCMA4GA1UdDwEB/wQEAwICpDANBgkqhkiG9w0BAQ0F\nAAOCAgEAeCMxVJr5Jyg87DVaUtEhiWfhto993ENrnevAGqrBOoRc/KU1/C3paqhR\nsvr2r2LR+npSmeo6iz0FaO31XwHSHX95+XJeGP5Q8TGddbRiTglQsMfOkGNzxqgg\nTkdZ8A1y9v2jprONUmLADVGIVT0AoHc7V9w1I8NKhrY+rIllum4FRDiDPSnImh5h\nxmH+Nq2ZuEFVdtV/oNKzEu2ywmbgBRd5Jv3rTejxltmTZtyq8IKoKguj3NVFn93Q\nU4TbsxkcAdrLMooLYYDRTWA4t0iqKM/UkYUg4xl2l9NrY7ZUbaNd5+YsLNdqXO/c\nmp7wyMv/8ZIy1BLG4zJmX/JzWkYmULqQ+A+21+YuqrV3a81V7vcHhJcRaPOrg5cd\nYwY2eCbXMvNOdrzppIglUrlddNuqAhs1MTi/VibxYuI9isU0JckXIcCy1L+xbEda\n6v/z6wSrScVz0I4m0DpK6xMQ8t9sLcrGp5uGbj6J4nQWd+QLdq6kmAzDOZ/Gs0wb\nPYdkER4dXAVcioYFekpKv7d+nur0FPtMNIw0OdhX2eAwC22IFAq2DZRjUFvaBGaD\ni1ptfq6P1mVJ2T/exYujEDtq+8yQTfWgFm/DjEfWtcCp0Jukgv8opLR2DpCf5Ucq\nd5X7d/DP0mukJ3vZ8EIqYorwZJ1L1a2jgngjA+gPxIaW+JHfTHU=\n-----END CERTIFICATE-----\n'})
ok: [rchltxfe-93180012-rz-le0trtn-001 -> rchltxib-c000000-003] => (item={'filename': 'k8s_root_ca_key.pem', 'value': '-----BEGIN PRIVATE KEY-----\nMIIJQQIBADANBgkqhkiG9w0BAQEFAASCCSswggknAgEAAoICAQCshfbL3b/6hux8\nQa9Q1r2dwkIg7AOJtZI9IQ+46Nwd1v99jg3D6YHjZqeDn7pdErJ3aahBoVw6uaIg\nX6rMzFKcw4HUO7IiB3pG9qJRRCtip4jD9x+d54pSKaXsjG8uSt2cBdEG5pOVinKF\n6GHoD/lL/W1dADB+g5+AlYGKywGH5j8hoFEreL7mfRf63/VJAX/w3GRqjJzGsfxn\n2qvCsJg8w/Q/CFQhz6zOX+PgmijEAhbuUJErC2CRUYrkFlmiAjDHZ6qW9B2YeYj5\nwkh8Dz1Ml8bbo3SPezr8uF+VkeOoydvisz2HvLVWvwy905SpkS/QBfqEhNe28Mxg\nBOxjVsT6I3mxyFLqCnTkAtaoiQVUvnNeK/fvT9lMulxITVLPod47kSOFN2JENVAl\nFN6KaoTj4eI1CLjxoOWl9O5beFqcXOPA/gmNQ+Iur2iS5d1grFSuzxcFlUEBFiEG\nm37o9UdoxLu6admGm82ufEtNL9T+f5L/wza+wA5vHmEb8SwAFwnnTHkg1ygYHaT5\nlV12aGfPl/FURmMXMNJgQSyAIkzp7U9r4C3quU90MolSnVOkywGBI0uuUGdxIGiF\n9MEapXECO5a7k17m7RDRusFl2LZw3+e/eWSA9WCBKpIM2SzAaqtUgYi51nemiu/G\nbK+I+RpkwRqSkZsBNqDtW7SQgmMhuQIDAQABAoICACysO62qa+2pRk8eixD5qfvR\ns2Hm+zuLYqSljPaqhWTMqTePswzJyDJkAHhawd0b3E6Dc2gbKlCihNKxMv744WNq\nVJHqK0QYf5ckgf9dEYboLsffk7ZFoFGKK0bHTnrENAIUl32b8xdD1EfMVp3KlRkS\nNGFijSwVVRXsoLCZxHm2Kx6/7oS9LWFtfuodV9xhoQlzaCUW5/mjWOJjgxpUs/b4\nHqS7uV1P80U1G0KraGboy5tGDXEB7y1x2e8Zwnfq7UqVE10nNQqoXcmefzpwj8Tn\ngDybZLFKjYmnDEkkj7jDHEbldsdRG/usWNZGlTYbPDA3fBkYdOsQCzvJypQmgbZ+\n3yk3Lj2+9vLEMfPrruuzyOSXgki6o5uvy7Je6PdBpsz75k8FH6a+Rw3vvP8HuP3S\nLSUYm3tyOheXHR7BKN4bnfi11RAWvDpT9S+QnZ+R8DmQzOADlnjRC8WewDJYoNJ1\np1jeuqswlxo144oMO92cmdS2dAbPvS6aQP1I85Q2NniY+6YhHkBwIQIlfVs1JPbY\nX7QtTy1IXQhR3sospyvUwY2GPSAeVHDRL53ClQKDsvWpSy0MAmWYJkZu1P+jKBim\nj34ytApgG65Hv/RHf3L4+4zzItZ3TN2tJ/g9EKc6oMNtqKbbG56kkmvRPWKtMGV8\nFqxCvG5NydUK7fN+P2WJAoIBAQDXLFC//Fn9ed1U+pKa2M25aJwEetkGLXQvkwVi\n8uJFaXITb2ceveSEo6iBExyn4eYL5A4X+RZdJJdRRbj4whsNN13Pm+6lYX3pp7MN\nO+78uvwVfKZiWPFKfZs7ZH1/O9VIlLGnXUHeaHK1tmv9ixxMixdnjUDkcVa0O3qT\nKBLpvXnVEMYizxQBN0P5Z9QvQQGpUhKnNw+FhV1SP+YHxrB0Pu6qbYAmZZC2MQc1\nTsDyqGjmHk9VJaFYAAPEjqACDbfnkVUCj0ylM4xPQuBJs9DOKh4InG+znusdmd8H\nmvoEFDppsrH1NhO6GTeuCk6n0WBi6cUm76K/gPscYyV4ZtkfAoIBAQDNQgDXtfqv\nxbAhvDk0o/P8fqOdgQF0uFTqYHmyW31Ty9nF0ptA8LVJOIljU3zlLplhIFjBnSEG\nLqu4jnLLRR+zej0MXmJuZ9BMWmQeTrZzttnH5bn54E07DPJ5BvFoTMJNklBiXjB5\n5hTPZS4yK1KjoxY+Ypnj4W1iZjP37ya/A34J2nlYtoW4LdVfJHqCxBXel9Nz2zkv\nvwwPu8Eu7gFLuhNQM6Iv4mORGI8yg7Y/BwodfDPRuFvrG1KXkjwASb0O5b1suRQy\n9H80q5EAbT36K1z48ilr8fcroN+hV8g4yntrBBgOHPMmBk/vHKU8B1rkBr0p2haI\n3PwKmDFRsDInAoIBAGrjjMmSZnHQk+6e+y0I/klYegiPrjevZMQtWMOqvFSW6SBW\nevd+hYKOeiqEf/u18D1/8LBgAIgMoU6yQAzy/9U059k2MPrez1m/AOdWGoZZrNhP\nr6ezX0oN04tRhDYsVutTUl09qnb9k95I3KR68nfjsKC0PsQ8uUGXOnDXu215vofl\naUfpbpqcBZxjw7glptmh97oxU/iUI6O0MmUygn18tbrb4okwcw7OlDIbCSaCGnoW\nHHrD0r6QY07FOx9KCU1zmLNI1F5MmSrWoex68wM3UOweKi8khs+RnIV+qyxTkCDp\nsBWL44jS9iHy5Nfg3uzEDDgnWsWfIR8c8YQ6MykCggEADr0ollTI9Yo6hZGggfkr\n8fueABddZWY/Ir1ev8H2E+hVcPEYmOcv/VwD8Y/zLfnUpbbO6MhBsNH1HsGL2LDT\n/+1NKPA2HTtzJ6ht/Acm7tQ4ezQx0JGcuhrJ5orrFtQ8N5nED+w3iulMoT/gu1WF\nD58MX9pwtn5ffmtcW/deTuUPTeHUSNyCaaFQ6w4RhgZSk7NPSch6KMWNNiwDST1p\n9mgcLuwmP04AXFDpJ3VxxsDYpxleFzcn0pAZtCyaBmNFIia5HW+E1cvcvol7Vg6C\nHs6yVGX/N3MejpF0vX8yL3HKvvqCR7EofJiDcOYbr13P1wPs3W59o8JKjvAyymze\njQKCAQAUY/0asRL33D7tFoIbLg/N9hi+tCCM35DMf2FeXm3QwSkAR/BJw0ewCE5C\n+VqukHN3/i0Xe8KSHwEuLK2sGLk9Ys8A5NytjqFApYwpIk8UrRONfC12H3ez5VYk\nJlhMVhVXEZvVhEFJiBC7q6x6s7BVtLTGV7FA5CW8YKBhwHwrpm+h/Xb798oaKyel\nP/xYq+GZzfWfbvUjZvgN0J0RGxKA+GRgsmhoyOfgCVXgSzuUkI+9cAUvC0OV407L\n4XIK0GDJ7Tv/2USSPfmueyGEmacc/oYUPVBUgeINSoaCM4cpZwyLylVEtKOdQoEE\n77G5mvQsoXxsMjd+nbHil450UHsL\n-----END PRIVATE KEY-----\n'})

TASK [Proteus MWIAT - ENABLE] *****************************************************************************************
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [Remote Install] *************************************************************************************************

TASK [remote/remote-install : Check if the subcloud deployed but failed] **********************************************
fatal: [rchltxfe-93180012-rz-le0trtn-001 -> rchltxib-c000000-003]: FAILED! => {"changed": true, "cmd": ". /etc/platform/openrc\ndcmanager subcloud show rchltxfe-d93180012-001 --column \"deploy_status\" --format value\n", "delta": "0:00:01.178847", "end": "2023-12-13 15:54:52.580894", "msg": "non-zero return code", "rc": 1, "start": "2023-12-13 15:54:51.402047", "stderr": "ERROR (app) Subcloud not found", "stderr_lines": ["ERROR (app) Subcloud not found"], "stdout": "", "stdout_lines": []}
...ignoring

TASK [remote/remote-install : debug] **********************************************************************************
ok: [rchltxfe-93180012-rz-le0trtn-001] => {
    "msg": "subcloud_status:"
}

TASK [remote/remote-install : Delete the subcloud that's 'install-failed' & 'pre-install-failed'] *********************
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/remote-install : Deploy remote cloud] ********************************************************************
changed: [rchltxfe-93180012-rz-le0trtn-001 -> rchltxib-c000000-003]

TASK [remote/remote-install : 1st polling prep: Obtain Keystone auth token] *******************************************
ok: [rchltxfe-93180012-rz-le0trtn-001 -> localhost]

TASK [remote/remote-install : 1st polling: Wait for subcloud to start installing OS] **********************************
FAILED - RETRYING: 1st polling: Wait for subcloud to start installing OS (40 retries left).

```

### Controller has new subcloud installation start

```log

Every 10.0s: dcmanager subcloud list                                                           Wed Dec 13 15:55:44 2023

+----+------------------------+------------+--------------+---------------+---------+
| id | name                   | management | availability | deploy status | sync    |
+----+------------------------+------------+--------------+---------------+---------+
|  3 | welktxef-d931881-005   | managed    | online	  | complete	  | in-sync |
|  6 | welktxef-d931884-034   | managed    | online	  | complete	  | in-sync |
|  7 | rchltxfe-d93180012-001 | unmanaged  | offline	  | installing    | unknown |
+----+------------------------+------------+--------------+---------------+---------+


```

### Ansible subcloud deploymnet continued

```log
TASK [remote/remote-install : 1st polling: Wait for subcloud to start installing OS] **********************************
FAILED - RETRYING: 1st polling: Wait for subcloud to start installing OS (40 retries left).
FAILED - RETRYING: 1st polling: Wait for subcloud to start installing OS (39 retries left).
ok: [rchltxfe-93180012-rz-le0trtn-001 -> localhost]

TASK [remote/remote-install : 1st polling result: Fail if the installation failed] ************************************
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/remote-install : 2nd polling prep: Obtain Keystone auth token] *******************************************
ok: [rchltxfe-93180012-rz-le0trtn-001 -> localhost]

TASK [remote/remote-install : 2nd polling: Wait for subcloud to install OS (this will take a while)] ******************
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (100 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (98 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (97 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (96 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (95 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (94 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (93 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (92 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (91 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (90 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (89 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (88 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (87 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (86 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (85 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (84 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (83 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (82 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (81 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (80 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (79 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (78 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (77 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (76 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (75 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (74 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (73 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (72 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (71 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (70 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (69 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (68 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (67 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (66 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (65 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (64 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (63 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (62 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (61 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (60 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (59 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (58 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (57 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (56 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (55 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (54 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (53 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (52 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (51 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (50 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (49 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (48 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (47 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (46 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (45 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (44 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (43 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (42 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (41 retries left).
FAILED - RETRYING: 2nd polling: Wait for subcloud to install OS (this will take a while) (40 retries left).
ok: [rchltxfe-93180012-rz-le0trtn-001 -> localhost]

TASK [remote/remote-install : 2nd polling result: Fail if any error occurred] *****************************************
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/remote-install : 3rd polling prep: Obtain Keystone auth token] *******************************************
ok: [rchltxfe-93180012-rz-le0trtn-001 -> localhost]

TASK [remote/remote-install : 3rd polling: Wait for subcloud to install OS (this may take a while)] *******************
ok: [rchltxfe-93180012-rz-le0trtn-001 -> localhost]

TASK [remote/remote-install : 3rd polling result: Fail if any error occurred] *****************************************
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/remote-install : 4th polling prep: Obtain Keystone auth token] *******************************************
ok: [rchltxfe-93180012-rz-le0trtn-001 -> localhost]

TASK [remote/remote-install : 4th polling: Wait for subcloud to install OS (this may still take a while)] *************
ok: [rchltxfe-93180012-rz-le0trtn-001 -> localhost]

TASK [remote/remote-install : 4th polling result: Fail if the installation failed] ************************************
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/remote-install : 5th polling prep: Obtain Keystone auth token] *******************************************
ok: [rchltxfe-93180012-rz-le0trtn-001 -> localhost]

TASK [remote/remote-install : 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while)] ***
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (100 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (99 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (98 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (97 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (96 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (95 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (94 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (93 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (92 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (91 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (90 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (89 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (88 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (87 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (86 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (85 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (84 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (83 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (82 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (81 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (80 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (79 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (78 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (77 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (76 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (75 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (74 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (73 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (72 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (71 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (70 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (69 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (68 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (67 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (66 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (65 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (64 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (63 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (62 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (61 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (60 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (59 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (58 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (57 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (56 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (55 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (54 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (53 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (52 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (51 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (50 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (49 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (48 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (47 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (46 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (45 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (44 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (43 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (42 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (41 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (40 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (39 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (38 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (37 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (36 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (35 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (34 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (33 retries left).
FAILED - RETRYING: 5th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while) (32 retries left).
ok: [rchltxfe-93180012-rz-le0trtn-001 -> localhost]

TASK [remote/remote-install : 5th polling result: Fail if bootstrap/deploy failed] ************************************
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/remote-install : 6th polling prep: Obtain Keystone auth token] *******************************************
ok: [rchltxfe-93180012-rz-le0trtn-001 -> localhost]

TASK [remote/remote-install : 6th polling: Wait for contoller-0 bootstrap/deploy to complete (this will take a while)] ***
ok: [rchltxfe-93180012-rz-le0trtn-001 -> localhost]

TASK [remote/remote-install : 6th polling result: Fail if bootstrap/deploy failed] ************************************
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/remote-install : Wait for controller-0 restart] **********************************************************
FAILED - RETRYING: Wait for controller-0 restart (40 retries left).
FAILED - RETRYING: Wait for controller-0 restart (39 retries left).
FAILED - RETRYING: Wait for controller-0 restart (38 retries left).
FAILED - RETRYING: Wait for controller-0 restart (37 retries left).
fatal: [rchltxfe-93180012-rz-le0trtn-001]: FAILED! => {"attempts": 5, "changed": false, "elapsed": 5, "msg": "timed out waiting for ping module test: Failed to connect to the host via ssh: ssh: connect to host 2607:f160:10:9073:ce:40a:0:f400 port 22: Connection refused"}
...ignoring

TASK [remote/remote-install : Wait for controller-0 recovery] *********************************************************
FAILED - RETRYING: 1st Wait for contoller-0 availability status online (100 retries left).
FAILED - RETRYING: 1st Wait for contoller-0 availability status online (99 retries left).
FAILED - RETRYING: 1st Wait for contoller-0 availability status online (98 retries left).
FAILED - RETRYING: 1st Wait for contoller-0 availability status online (97 retries left).
FAILED - RETRYING: 1st Wait for contoller-0 availability status online (96 retries left).
FAILED - RETRYING: 1st Wait for contoller-0 availability status online (95 retries left).
FAILED - RETRYING: 1st Wait for contoller-0 availability status online (94 retries left).
ok: [rchltxfe-93180012-rz-le0trtn-001 -> localhost]

TASK [remote/manage : 2nd Obtain Keystone auth token] *****************************************************************
ok: [rchltxfe-93180012-rz-le0trtn-001 -> localhost]

TASK [remote/manage : 2nd Wait for contoller-0 availability status online] ********************************************
ok: [rchltxfe-93180012-rz-le0trtn-001 -> localhost]

TASK [remote/manage : Wait for system to stabilize before running kubectl] ********************************************
Pausing for 480 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)
ok: [rchltxfe-93180012-rz-le0trtn-001]

TASK [Wait for distributed cloud to be reconciled] ********************************************************************

TASK [common/wait_for_reconciliation : Making sure node is reachable] *************************************************
ok: [rchltxfe-93180012-rz-le0trtn-001]

TASK [common/wait_for_reconciliation : Wait for K8s API to be up] *****************************************************
ok: [rchltxfe-93180012-rz-le0trtn-001]

TASK [common/wait_for_reconciliation : Wait for hosts to be reconciled] ***********************************************
changed: [rchltxfe-93180012-rz-le0trtn-001]

TASK [common/wait_for_reconciliation : Wait for systems to be reconciled] *********************************************
FAILED - RETRYING: Wait for systems to be reconciled (30 retries left).
FAILED - RETRYING: Wait for systems to be reconciled (29 retries left).
FAILED - RETRYING: Wait for systems to be reconciled (28 retries left).
FAILED - RETRYING: Wait for systems to be reconciled (27 retries left).
FAILED - RETRYING: Wait for systems to be reconciled (26 retries left).
FAILED - RETRYING: Wait for systems to be reconciled (25 retries left).
FAILED - RETRYING: Wait for systems to be reconciled (24 retries left).
FAILED - RETRYING: Wait for systems to be reconciled (23 retries left).
FAILED - RETRYING: Wait for systems to be reconciled (22 retries left).
FAILED - RETRYING: Wait for systems to be reconciled (21 retries left).
FAILED - RETRYING: Wait for systems to be reconciled (20 retries left).
FAILED - RETRYING: Wait for systems to be reconciled (19 retries left).
FAILED - RETRYING: Wait for systems to be reconciled (18 retries left).
FAILED - RETRYING: Wait for systems to be reconciled (17 retries left).
FAILED - RETRYING: Wait for systems to be reconciled (16 retries left).
FAILED - RETRYING: Wait for systems to be reconciled (15 retries left).
FAILED - RETRYING: Wait for systems to be reconciled (14 retries left).
FAILED - RETRYING: Wait for systems to be reconciled (13 retries left).
FAILED - RETRYING: Wait for systems to be reconciled (12 retries left).
FAILED - RETRYING: Wait for systems to be reconciled (11 retries left).
FAILED - RETRYING: Wait for systems to be reconciled (10 retries left).
FAILED - RETRYING: Wait for systems to be reconciled (9 retries left).
FAILED - RETRYING: Wait for systems to be reconciled (8 retries left).
FAILED - RETRYING: Wait for systems to be reconciled (7 retries left).
FAILED - RETRYING: Wait for systems to be reconciled (6 retries left).
FAILED - RETRYING: Wait for systems to be reconciled (5 retries left).
FAILED - RETRYING: Wait for systems to be reconciled (4 retries left).
FAILED - RETRYING: Wait for systems to be reconciled (3 retries left).
FAILED - RETRYING: Wait for systems to be reconciled (2 retries left).
FAILED - RETRYING: Wait for systems to be reconciled (1 retries left).
fatal: [rchltxfe-93180012-rz-le0trtn-001]: FAILED! => {"attempts": 30, "changed": true, "cmd": "kubectl --kubeconfig=/etc/kubernetes/admin.conf -n deployment get systems -o jsonpath='{range .items[?(@.status.reconciled==false)]}{.metadata.name}{\"\\n\"}{end}'\n", "delta": "0:00:00.079433", "end": "2023-12-13 17:35:22.598879", "msg": "", "rc": 0, "start": "2023-12-13 17:35:22.519446", "stderr": "", "stderr_lines": [], "stdout": "rchltxfe-d93180012-001", "stdout_lines": ["rchltxfe-d93180012-001"]}

TASK [common/wait_for_reconciliation : try deleting dm pod] ***********************************************************
changed: [rchltxfe-93180012-rz-le0trtn-001]

TASK [common/wait_for_reconciliation : Wait for hosts to be reconciled] ***********************************************
changed: [rchltxfe-93180012-rz-le0trtn-001]

TASK [common/wait_for_reconciliation : Wait for systems to be reconciled] *********************************************
FAILED - RETRYING: Wait for systems to be reconciled (30 retries left).

TASK [remote/manage : Wait for distributed cloud to be reconciled but subcloud OAM VIP becomes unreachable] ***********
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/manage : Check if the subcloud deployed but failed] ******************************************************
changed: [rchltxfe-93180012-rz-le0trtn-001 -> rchltxib-c000000-003]

TASK [remote/manage : Set distributed cloud state to managed] *********************************************************
changed: [rchltxfe-93180012-rz-le0trtn-001 -> rchltxib-c000000-003]

TASK [remote/manage : Wait for system to stabilize] *******************************************************************
Pausing for 300 seconds
(ctrl+C then 'C' = continue early, ctrl+C then 'A' = abort)

ok: [rchltxfe-93180012-rz-le0trtn-001]

TASK [Remote Trust] ***************************************************************************************************

TASK [remote/trust : Create temporary working directory] **************************************************************
changed: [rchltxfe-93180012-rz-le0trtn-001 -> localhost]

TASK [remote/trust : Copy SSL cert files to working dir] **************************************************************
changed: [rchltxfe-93180012-rz-le0trtn-001 -> localhost] => (item={'filename': 'k8s_root_ca_cert.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIF8jCCA9qgAwIBAgIJAIf9Ql2uDZh+MA0GCSqGSIb3DQEBDQUAMIGFMQswCQYD\nVQQGEwJVUzEOMAwGA1UECAwFVGV4YXMxETAPBgNVBAcMCFdlc3RsYWtlMR0wGwYD\nVQQKDBRWZXJpem9uIFNvdXJjaW5nIExMQzE0MDIGA1UEAwwrVmVyaXpvbiBOZXR3\nb3JrIFdFTEtUWElCIExBQiAxIDMgUlNBIEs4UyBDQTAeFw0yMDEwMjUyMjEyNDha\nFw0zMDEwMjMyMjEyNDhaMIGFMQswCQYDVQQGEwJVUzEOMAwGA1UECAwFVGV4YXMx\nETAPBgNVBAcMCFdlc3RsYWtlMR0wGwYDVQQKDBRWZXJpem9uIFNvdXJjaW5nIExM\nQzE0MDIGA1UEAwwrVmVyaXpvbiBOZXR3b3JrIFdFTEtUWElCIExBQiAxIDMgUlNB\nIEs4UyBDQTCCAiIwDQYJKoZIhvcNAQEBBQADggIPADCCAgoCggIBAKyF9svdv/qG\n7HxBr1DWvZ3CQiDsA4m1kj0hD7jo3B3W/32ODcPpgeNmp4Oful0SsndpqEGhXDq5\noiBfqszMUpzDgdQ7siIHekb2olFEK2KniMP3H53nilIppeyMby5K3ZwF0Qbmk5WK\ncoXoYegP+Uv9bV0AMH6Dn4CVgYrLAYfmPyGgUSt4vuZ9F/rf9UkBf/DcZGqMnMax\n/Gfaq8KwmDzD9D8IVCHPrM5f4+CaKMQCFu5QkSsLYJFRiuQWWaICMMdnqpb0HZh5\niPnCSHwPPUyXxtujdI97Ovy4X5WR46jJ2+KzPYe8tVa/DL3TlKmRL9AF+oSE17bw\nzGAE7GNWxPojebHIUuoKdOQC1qiJBVS+c14r9+9P2Uy6XEhNUs+h3juRI4U3YkQ1\nUCUU3opqhOPh4jUIuPGg5aX07lt4Wpxc48D+CY1D4i6vaJLl3WCsVK7PFwWVQQEW\nIQabfuj1R2jEu7pp2Yabza58S00v1P5/kv/DNr7ADm8eYRvxLAAXCedMeSDXKBgd\npPmVXXZoZ8+X8VRGYxcw0mBBLIAiTOntT2vgLeq5T3QyiVKdU6TLAYEjS65QZ3Eg\naIX0wRqlcQI7lruTXubtENG6wWXYtnDf5795ZID1YIEqkgzZLMBqq1SBiLnWd6aK\n78Zsr4j5GmTBGpKRmwE2oO1btJCCYyG5AgMBAAGjYzBhMA8GA1UdEwEB/wQFMAMB\nAf8wHQYDVR0OBBYEFEDQ5EaGp3x02WUuvqetygqpM3dCMB8GA1UdIwQYMBaAFEDQ\n5EaGp3x02WUuvqetygqpM3dCMA4GA1UdDwEB/wQEAwICpDANBgkqhkiG9w0BAQ0F\nAAOCAgEAeCMxVJr5Jyg87DVaUtEhiWfhto993ENrnevAGqrBOoRc/KU1/C3paqhR\nsvr2r2LR+npSmeo6iz0FaO31XwHSHX95+XJeGP5Q8TGddbRiTglQsMfOkGNzxqgg\nTkdZ8A1y9v2jprONUmLADVGIVT0AoHc7V9w1I8NKhrY+rIllum4FRDiDPSnImh5h\nxmH+Nq2ZuEFVdtV/oNKzEu2ywmbgBRd5Jv3rTejxltmTZtyq8IKoKguj3NVFn93Q\nU4TbsxkcAdrLMooLYYDRTWA4t0iqKM/UkYUg4xl2l9NrY7ZUbaNd5+YsLNdqXO/c\nmp7wyMv/8ZIy1BLG4zJmX/JzWkYmULqQ+A+21+YuqrV3a81V7vcHhJcRaPOrg5cd\nYwY2eCbXMvNOdrzppIglUrlddNuqAhs1MTi/VibxYuI9isU0JckXIcCy1L+xbEda\n6v/z6wSrScVz0I4m0DpK6xMQ8t9sLcrGp5uGbj6J4nQWd+QLdq6kmAzDOZ/Gs0wb\nPYdkER4dXAVcioYFekpKv7d+nur0FPtMNIw0OdhX2eAwC22IFAq2DZRjUFvaBGaD\ni1ptfq6P1mVJ2T/exYujEDtq+8yQTfWgFm/DjEfWtcCp0Jukgv8opLR2DpCf5Ucq\nd5X7d/DP0mukJ3vZ8EIqYorwZJ1L1a2jgngjA+gPxIaW+JHfTHU=\n-----END CERTIFICATE-----\n'})
changed: [rchltxfe-93180012-rz-le0trtn-001 -> localhost] => (item={'filename': 'vz_root_ca_cert.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIFpTCCA42gAwIBAgIUa3vZ0YGxO1TQ8NwhiVfQC0JslXgwDQYJKoZIhvcNAQEL\nBQAwWjELMAkGA1UEBhMCVVMxEDAOBgNVBAoMB1Zlcml6b24xEzARBgNVBAsMClZa\nSUFNIFRlc3QxJDAiBgNVBAMMG1Zlcml6b24gTmV0d29yayBSU0EgQ0EgVGVzdDAe\nFw0yMDA2MTUyMTAxMTNaFw0zNTA2MTUyMTAxMTNaMFoxCzAJBgNVBAYTAlVTMRAw\nDgYDVQQKDAdWZXJpem9uMRMwEQYDVQQLDApWWklBTSBUZXN0MSQwIgYDVQQDDBtW\nZXJpem9uIE5ldHdvcmsgUlNBIENBIFRlc3QwggIiMA0GCSqGSIb3DQEBAQUAA4IC\nDwAwggIKAoICAQC8AIrksI57CbIl5uGZ6yqfpQj3aK+N8f1EVHdwK9JFskoipvC8\n7yFTk8tgmO1i0YA5oRGfNxneqCdrXZiWL6Ko8v/iln9vuN+2rK3rgWZPPRJBAsBN\na49L7U6lJjIGxIZtZqmK5h47oiUtwlYVrbZMN2ijuBQ22/eQ9tsFDV28oBuZ3WAR\npSSbj/tubPQYkw3YYOhv/VpEpsd0rkoEt3QCmTVcX2rtblanpXowTV5R0Hy4014n\nT49jrEo40r4mwYoyS835Uv4ENUFA+pXicT9eUot3RSH6rYdx4A/14UtoI9U0ol8M\n62GHpxSASQ2Kc3yQWvxRGTFslTduYM+vVmMLEDDdqcsjYnStPpwdxxmKItmbjxSv\nIwYIndp8A04WkX2iiJCciC3BNxiLamPtYVyB1HHqbGTGirKYuSvwZt337q1OI3WH\nwVn2S4Mj/wqa4iCyGTvFSUnGq34Xkrb9XNwWBok9Tc2XWGAU/mb/xcd1hX74GZbF\nsrZ11aPtym4kMAjU2KQi96GcAH2lnGZYoOja1J4Cs4WYx1uAx74H/m84CrYavVfl\n1ONJVLDfuZaEkSmu+jHQX15pAECNORTuLD06PbWnOEcOi1xmbt/OT3SA3rhD2mb7\n2wxl7oJpV3ap8xGwYmxiFzmInxFJ1axjg8Rimol0mXTKAy6OdNHbCOnAwwIDAQAB\no2MwYTAPBgNVHRMBAf8EBTADAQH/MA4GA1UdDwEB/wQEAwIBBjAfBgNVHSMEGDAW\ngBQleng3lqGBeTrbLVuABoEmUHm1+TAdBgNVHQ4EFgQUJXp4N5ahgXk62y1bgAaB\nJlB5tfkwDQYJKoZIhvcNAQELBQADggIBADQ9jpmVh9nyY7ZQ4s+S9RuSRYn7QsrW\nDePeMzQgh8ZtS8WE65GY5HS61iHNP2Co8Q1lAaBWF4ipq+VZOcQbPLccHzd1kZv4\ns4u0aTzBd9ccidl73FS0DJDQOBbzPSzgsaiGHSMyGzkTeA8z3ntsSqrXXcDUvoRi\nFus/110AwdtNhJLrWveX6btYtHp9Lqe0YtNCy5AaXlrr1yRSckP5BWVtlwD4dzSO\n/dqI3wHS/ncUx9wSQomZ+AmxYW3KtJQKgHzTqHru1x9BBk7Bzfz9FZr6HLLmEitj\nuFoDRd5TNt5LbO0zDQokvY3oqso6Htup/rS7C08mcmnelYE+yXuOc1YrlyGnpBzk\nmy+1VYbOxRRdqKAZRbE72u/h847IVpsOvjR51iksuCAurZdp2+y2zvV8NhWekuNy\nirECRy9cb4YasjRaKi0/TCGPVSICuLyeG2W72liCj/N2VKfjPP9zsOR5XjwCXfRg\n+9xhLy77/gov2NWXx5fzTkhxCrHOxFdLVMn0wQhksDmw6QsXzDIHSpIOypdDfnx9\nCsthx3nhkuHLUaEP22D22dG+vImA9ukj4R/RRI/87jmi9Q8+ehH+NqN0GZZcLjdN\nSLVXpncuwWQFUDPR06wNkkkmBSXWiIYhwqSpU0Pl3er3fD0uWvXuWPm2PzfOmUAE\nUrkzyw9XmLw0\n-----END CERTIFICATE-----\n'})
changed: [rchltxfe-93180012-rz-le0trtn-001 -> localhost] => (item={'filename': 'vz_root_ica_cert.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIFNzCCAx+gAwIBAgIUGLJR/hP48n+vdq2v1hcfspXo/78wDQYJKoZIhvcNAQEL\nBQAwWjELMAkGA1UEBhMCVVMxEDAOBgNVBAoMB1Zlcml6b24xEzARBgNVBAsMClZa\nSUFNIFRlc3QxJDAiBgNVBAMMG1Zlcml6b24gTmV0d29yayBSU0EgQ0EgVGVzdDAe\nFw0yMDEwMjIyMTE0MDNaFw0zMDEwMjIyMTE0MDNaMIGRMQswCQYDVQQGEwJVUzEL\nMAkGA1UECAwCVFgxETAPBgNVBAcMCFdlc3RsYWtlMRAwDgYDVQQKDAdWZXJpem9u\nMR0wGwYDVQQLDBRWZXJpem9uIFNvdXJjaW5nIExMQzExMC8GA1UEAwwoVmVyaXpv\nbiBOZXR3b3JrIFdFTEtUWElCIExBQiAxIDMgUlNBIElDQTCCASIwDQYJKoZIhvcN\nAQEBBQADggEPADCCAQoCggEBANhkGTXOCKEYf5znDDeX3n/DHFPVqazgQsr0/SIG\n4eb1JY5q5Jq3ZhAaZCr9HJuCkwAP/zgYH0llqOvf8AC2Uh+7z1b33IbwxPmJfWCP\nAqSNFkLWWVRdbELapCu408QsrLMW8IrdP6PLiKAepwncfm4T0/6bANqIEmUkpw8Q\nxProeiNwlGbwUll+tELmdCk7vA7hKX3j1kUvS5Z84Z5ivJBWEcUEggmC97TK4aLo\nFVEHbyahze568JVEaM1vY5L4mnRRTl+u5ipaSMxVBsiXzF7eFuKCzqF7wxbDIt2T\nIFEJtwyJDW5bXjyXgiF1d5H/URprUcRV9Qmf2+PXcfwHII8CAwEAAaOBvDCBuTAS\nBgNVHRMBAf8ECDAGAQH/AgEAMA4GA1UdDwEB/wQEAwIBBjAfBgNVHSMEGDAWgBQl\neng3lqGBeTrbLVuABoEmUHm1+TBTBgNVHR8ETDBKMEigRqBEhkJodHRwOi8vc2Vj\ndXJlLnN0YWdpbmcuc2VjdXJpdHljcmVkZW50aWFsaW5nLmNvbS9jcmwvdnpuZXRy\nc2FjYS5jcmwwHQYDVR0OBBYEFP0Z+/vaDLtAoFig1I9ttNKnmzByMA0GCSqGSIb3\nDQEBCwUAA4ICAQBuXVTf9e01HeymHgRcFCwP2N6G6u+vIzY8Bz0zSUZeRDHMZQcS\nNoabDyn5FfGJlw4BqGC591Sp0/unFQDzAg17rDBcrgwajeFeUiFdb9PiAJwHaX9S\nvq/7VmVLCmpeb+a/laXAe6+tkY1kcFrd1+ItRKC6ZGXMsoDkmk5Ndxxgw77estcI\nMiiLQbvpXRygX5wD4/ayazuLms9qITZkOZ1nTLVqq7QrwYCsSoih7hj6sbsfXr19\nGoYWmk8Y7O/d3ttgyHuRH9k/2dQ/xL7avRpMNkPdr7ocJqI46hvx2X6UyOo7IBua\nkSkFbSmPZWIVAidNMBOnvffCQ32tfjT2/xso/a9cdskvxqgLi0MPARU9Nl2Pufsb\nD7l4/sBvz/PiNTKp+Daa9FdyLb9ySidos1uS0c24bUtY1RXXGAVV2qgfyrzvzfye\nSM+w16hMU/yeYiuA1jsPmsnZnuIJj4Nv8ZjjZ0WS53pP5wcghaHkBrqWQNT8meqA\nVElrMBPlYq67T+AXP0B9lf5Sc3QVIio7XKKfqrlcQxY2JGLEyE53JgZGX7dpwU4I\nukLvyHbT4p06oY3qG6+wH8+YIXCNAYtadJ/C5/u9GcLX5NnZrcuduj0inw2/a3Ao\nWgCt6/Pr28BkCvkWdDt9d8Z40qeu1aZdcr157mR+yZGPfBfB2vasrNIEwQ==\n-----END CERTIFICATE-----\n'})

TASK [remote/trust : Generate trust_ca.pem] ***************************************************************************
changed: [rchltxfe-93180012-rz-le0trtn-001 -> localhost]

TASK [remote/trust : Copy trust_ca.pem to host] ***********************************************************************
changed: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/trust : Install certificate] *****************************************************************************
changed: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/trust : Remove temporary working directory] **************************************************************
changed: [rchltxfe-93180012-rz-le0trtn-001 -> localhost]

TASK [Remote Starlingx] ***********************************************************************************************

TASK [remote/starlingx : Create temporary working directory] **********************************************************
changed: [rchltxfe-93180012-rz-le0trtn-001 -> localhost]

TASK [remote/starlingx : Copy SSL root certificates] ******************************************************************
changed: [rchltxfe-93180012-rz-le0trtn-001 -> localhost] => (item={'filename': 'vz_root_ica_cert.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIFNzCCAx+gAwIBAgIUGLJR/hP48n+vdq2v1hcfspXo/78wDQYJKoZIhvcNAQEL\nBQAwWjELMAkGA1UEBhMCVVMxEDAOBgNVBAoMB1Zlcml6b24xEzARBgNVBAsMClZa\nSUFNIFRlc3QxJDAiBgNVBAMMG1Zlcml6b24gTmV0d29yayBSU0EgQ0EgVGVzdDAe\nFw0yMDEwMjIyMTE0MDNaFw0zMDEwMjIyMTE0MDNaMIGRMQswCQYDVQQGEwJVUzEL\nMAkGA1UECAwCVFgxETAPBgNVBAcMCFdlc3RsYWtlMRAwDgYDVQQKDAdWZXJpem9u\nMR0wGwYDVQQLDBRWZXJpem9uIFNvdXJjaW5nIExMQzExMC8GA1UEAwwoVmVyaXpv\nbiBOZXR3b3JrIFdFTEtUWElCIExBQiAxIDMgUlNBIElDQTCCASIwDQYJKoZIhvcN\nAQEBBQADggEPADCCAQoCggEBANhkGTXOCKEYf5znDDeX3n/DHFPVqazgQsr0/SIG\n4eb1JY5q5Jq3ZhAaZCr9HJuCkwAP/zgYH0llqOvf8AC2Uh+7z1b33IbwxPmJfWCP\nAqSNFkLWWVRdbELapCu408QsrLMW8IrdP6PLiKAepwncfm4T0/6bANqIEmUkpw8Q\nxProeiNwlGbwUll+tELmdCk7vA7hKX3j1kUvS5Z84Z5ivJBWEcUEggmC97TK4aLo\nFVEHbyahze568JVEaM1vY5L4mnRRTl+u5ipaSMxVBsiXzF7eFuKCzqF7wxbDIt2T\nIFEJtwyJDW5bXjyXgiF1d5H/URprUcRV9Qmf2+PXcfwHII8CAwEAAaOBvDCBuTAS\nBgNVHRMBAf8ECDAGAQH/AgEAMA4GA1UdDwEB/wQEAwIBBjAfBgNVHSMEGDAWgBQl\neng3lqGBeTrbLVuABoEmUHm1+TBTBgNVHR8ETDBKMEigRqBEhkJodHRwOi8vc2Vj\ndXJlLnN0YWdpbmcuc2VjdXJpdHljcmVkZW50aWFsaW5nLmNvbS9jcmwvdnpuZXRy\nc2FjYS5jcmwwHQYDVR0OBBYEFP0Z+/vaDLtAoFig1I9ttNKnmzByMA0GCSqGSIb3\nDQEBCwUAA4ICAQBuXVTf9e01HeymHgRcFCwP2N6G6u+vIzY8Bz0zSUZeRDHMZQcS\nNoabDyn5FfGJlw4BqGC591Sp0/unFQDzAg17rDBcrgwajeFeUiFdb9PiAJwHaX9S\nvq/7VmVLCmpeb+a/laXAe6+tkY1kcFrd1+ItRKC6ZGXMsoDkmk5Ndxxgw77estcI\nMiiLQbvpXRygX5wD4/ayazuLms9qITZkOZ1nTLVqq7QrwYCsSoih7hj6sbsfXr19\nGoYWmk8Y7O/d3ttgyHuRH9k/2dQ/xL7avRpMNkPdr7ocJqI46hvx2X6UyOo7IBua\nkSkFbSmPZWIVAidNMBOnvffCQ32tfjT2/xso/a9cdskvxqgLi0MPARU9Nl2Pufsb\nD7l4/sBvz/PiNTKp+Daa9FdyLb9ySidos1uS0c24bUtY1RXXGAVV2qgfyrzvzfye\nSM+w16hMU/yeYiuA1jsPmsnZnuIJj4Nv8ZjjZ0WS53pP5wcghaHkBrqWQNT8meqA\nVElrMBPlYq67T+AXP0B9lf5Sc3QVIio7XKKfqrlcQxY2JGLEyE53JgZGX7dpwU4I\nukLvyHbT4p06oY3qG6+wH8+YIXCNAYtadJ/C5/u9GcLX5NnZrcuduj0inw2/a3Ao\nWgCt6/Pr28BkCvkWdDt9d8Z40qeu1aZdcr157mR+yZGPfBfB2vasrNIEwQ==\n-----END CERTIFICATE-----\n'})
changed: [rchltxfe-93180012-rz-le0trtn-001 -> localhost] => (item={'filename': 'vz_root_ica_key.pem', 'value': '-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA2GQZNc4IoRh/nOcMN5fef8McU9WprOBCyvT9Igbh5vUljmrk\nmrdmEBpkKv0cm4KTAA//OBgfSWWo69/wALZSH7vPVvfchvDE+Yl9YI8CpI0WQtZZ\nVF1sQtqkK7jTxCyssxbwit0/o8uIoB6nCdx+bhPT/psA2ogSZSSnDxDE+uh6I3CU\nZvBSWX60QuZ0KTu8DuEpfePWRS9LlnzhnmK8kFYRxQSCCYL3tMrhougVUQdvJqHN\n7nrwlURozW9jkviadFFOX67mKlpIzFUGyJfMXt4W4oLOoXvDFsMi3ZMgUQm3DIkN\nbltePJeCIXV3kf9RGmtRxFX1CZ/b49dx/AcgjwIDAQABAoIBABSd1NkPfDr8/ouQ\nZ9WUHprFmBlUrgnOhA6aMNPhG/zJNn7PKGClQJAgM5L08pjOY/sJiyNpCPIRQXrX\npyIqPMDRP/vlOZmRrvKnas6cUYAkAQ71JSWokPv9oM6ZmXODXiDh+qEAW2PbrHS0\n9u01mMYcFYKYeghYFoiUaWZCDsJo3v3dgeE9aQ4tB9ksovSmWrpuCY7NKbd7Qrbo\n5XxQhkujTkE6knOHz8CVwYETtj8LZ/bvHIkGMGvRvwsKYDZkIKr5CZ7DX+KcMfPN\neMZU4VCHYSXNxsyp5DJ1Zw+gx8/32kUL0CzJLLam1G021Hq41KPwwSV/KPrOKel7\nHXDLXeECgYEA8MR+lgxGjYTc/k4TdZvcFVgqHGLXnyjO7ZVt4b7UpwmayLuoSD/M\nOpHQYX+JBIIWTNlGhG8UV3DPC3v+auhYa7twwbekS30IYCAmu5GCKgMAcWFinz6A\nYZxG55P/hShetCyOqikgwXqzMlwGs8KEul8f8BKssROzUy8mIlFhjq0CgYEA5hTM\nSNxAD3dlRtb0771fBU7fjx8JPfjptP9vP/JVEelkc/ti9nZ5buTC+9cQC/B+YFx7\nc82uCrXV13bGR9iH8xBhwU7JOYJZbgCpwp0F56wIN5Pdk9Eo79Batrw3oGBG4Yvt\nDc2eltxQbHgObc/qygf88j9XqD8aGIvQrc4Jf6sCgYAtxX03M1A6WTbWFau3YRD+\n8crXqKbLOCvWmODR2MB+nOHTJXHBgndl7xCJaIB43e41X9z7Ek7wrJ5/1WuxkUg1\n+uVdvna6byOnepVCdVAkgnuUEmp4UZ6AcAA+yDD8dIdEg2//w1/ZyGTGvx37EJDB\nCZJ9xl8ULuWZe84pGgWM5QKBgQCYVUbYKrNjShrM5z9uh4QlII6V1Oeql2YtBz4i\nKZE3db6jp9pi8hf+WwnZ8g9WyFjz9edqydAkmTXHHYW0ReHlBYCjm0VRhUMuuNOs\n3YfuVpFuMsFuv/oJpXqaKE3wKi5j4OAH1o7ctWuuFWMAQ7vhHZ7UySmBZJ4jiFaW\n7KaPVwKBgE8E0xbSDVGxXbEGwRXxeaOSemEHD9uEnbAyq1p3EBBhBvInWmDiP5vJ\n68IYNZ4SGxXEKDifwrLGHyekt3RK9B2+U03okd1qH7gfBIlxBJivcjhBe2PtK/Qj\n6fBN0fC1UJoE6pseT9cJDaBq2wMRXJGRYtT8fU9PPJcfa23JlKNS\n-----END RSA PRIVATE KEY-----\n'})

TASK [remote/starlingx : Copy templates] ******************************************************************************
changed: [rchltxfe-93180012-rz-le0trtn-001 -> localhost] => (item=req_starlingx.cnf)

TASK [remote/starlingx : Generate SSL cert] ***************************************************************************
changed: [rchltxfe-93180012-rz-le0trtn-001 -> localhost]

TASK [remote/starlingx : Copy SSL starlingx certs to server] **********************************************************
changed: [rchltxfe-93180012-rz-le0trtn-001] => (item=starlingx-ca-cert.pem)

TASK [remote/starlingx : Configure starlingx] *************************************************************************
changed: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/starlingx : Remove temporary working directory] **********************************************************
changed: [rchltxfe-93180012-rz-le0trtn-001 -> localhost]

TASK [Remote Integ] ***************************************************************************************************

TASK [remote/integ : Detect applied status of platform-integ-apps application] ****************************************
changed: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/integ : Fail if platform-integ-apps application apply failed] ********************************************
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [Remote Ldap] ****************************************************************************************************

TASK [remote/ldap : Create temporary working directory] ***************************************************************
changed: [rchltxfe-93180012-rz-le0trtn-001 -> localhost]

TASK [remote/ldap : Copy SSL root certificates] ***********************************************************************
changed: [rchltxfe-93180012-rz-le0trtn-001 -> localhost] => (item={'filename': 'vz_root_ca_cert.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIFpTCCA42gAwIBAgIUa3vZ0YGxO1TQ8NwhiVfQC0JslXgwDQYJKoZIhvcNAQEL\nBQAwWjELMAkGA1UEBhMCVVMxEDAOBgNVBAoMB1Zlcml6b24xEzARBgNVBAsMClZa\nSUFNIFRlc3QxJDAiBgNVBAMMG1Zlcml6b24gTmV0d29yayBSU0EgQ0EgVGVzdDAe\nFw0yMDA2MTUyMTAxMTNaFw0zNTA2MTUyMTAxMTNaMFoxCzAJBgNVBAYTAlVTMRAw\nDgYDVQQKDAdWZXJpem9uMRMwEQYDVQQLDApWWklBTSBUZXN0MSQwIgYDVQQDDBtW\nZXJpem9uIE5ldHdvcmsgUlNBIENBIFRlc3QwggIiMA0GCSqGSIb3DQEBAQUAA4IC\nDwAwggIKAoICAQC8AIrksI57CbIl5uGZ6yqfpQj3aK+N8f1EVHdwK9JFskoipvC8\n7yFTk8tgmO1i0YA5oRGfNxneqCdrXZiWL6Ko8v/iln9vuN+2rK3rgWZPPRJBAsBN\na49L7U6lJjIGxIZtZqmK5h47oiUtwlYVrbZMN2ijuBQ22/eQ9tsFDV28oBuZ3WAR\npSSbj/tubPQYkw3YYOhv/VpEpsd0rkoEt3QCmTVcX2rtblanpXowTV5R0Hy4014n\nT49jrEo40r4mwYoyS835Uv4ENUFA+pXicT9eUot3RSH6rYdx4A/14UtoI9U0ol8M\n62GHpxSASQ2Kc3yQWvxRGTFslTduYM+vVmMLEDDdqcsjYnStPpwdxxmKItmbjxSv\nIwYIndp8A04WkX2iiJCciC3BNxiLamPtYVyB1HHqbGTGirKYuSvwZt337q1OI3WH\nwVn2S4Mj/wqa4iCyGTvFSUnGq34Xkrb9XNwWBok9Tc2XWGAU/mb/xcd1hX74GZbF\nsrZ11aPtym4kMAjU2KQi96GcAH2lnGZYoOja1J4Cs4WYx1uAx74H/m84CrYavVfl\n1ONJVLDfuZaEkSmu+jHQX15pAECNORTuLD06PbWnOEcOi1xmbt/OT3SA3rhD2mb7\n2wxl7oJpV3ap8xGwYmxiFzmInxFJ1axjg8Rimol0mXTKAy6OdNHbCOnAwwIDAQAB\no2MwYTAPBgNVHRMBAf8EBTADAQH/MA4GA1UdDwEB/wQEAwIBBjAfBgNVHSMEGDAW\ngBQleng3lqGBeTrbLVuABoEmUHm1+TAdBgNVHQ4EFgQUJXp4N5ahgXk62y1bgAaB\nJlB5tfkwDQYJKoZIhvcNAQELBQADggIBADQ9jpmVh9nyY7ZQ4s+S9RuSRYn7QsrW\nDePeMzQgh8ZtS8WE65GY5HS61iHNP2Co8Q1lAaBWF4ipq+VZOcQbPLccHzd1kZv4\ns4u0aTzBd9ccidl73FS0DJDQOBbzPSzgsaiGHSMyGzkTeA8z3ntsSqrXXcDUvoRi\nFus/110AwdtNhJLrWveX6btYtHp9Lqe0YtNCy5AaXlrr1yRSckP5BWVtlwD4dzSO\n/dqI3wHS/ncUx9wSQomZ+AmxYW3KtJQKgHzTqHru1x9BBk7Bzfz9FZr6HLLmEitj\nuFoDRd5TNt5LbO0zDQokvY3oqso6Htup/rS7C08mcmnelYE+yXuOc1YrlyGnpBzk\nmy+1VYbOxRRdqKAZRbE72u/h847IVpsOvjR51iksuCAurZdp2+y2zvV8NhWekuNy\nirECRy9cb4YasjRaKi0/TCGPVSICuLyeG2W72liCj/N2VKfjPP9zsOR5XjwCXfRg\n+9xhLy77/gov2NWXx5fzTkhxCrHOxFdLVMn0wQhksDmw6QsXzDIHSpIOypdDfnx9\nCsthx3nhkuHLUaEP22D22dG+vImA9ukj4R/RRI/87jmi9Q8+ehH+NqN0GZZcLjdN\nSLVXpncuwWQFUDPR06wNkkkmBSXWiIYhwqSpU0Pl3er3fD0uWvXuWPm2PzfOmUAE\nUrkzyw9XmLw0\n-----END CERTIFICATE-----\n'})
changed: [rchltxfe-93180012-rz-le0trtn-001 -> localhost] => (item={'filename': 'vz_root_ica_cert.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIFNzCCAx+gAwIBAgIUGLJR/hP48n+vdq2v1hcfspXo/78wDQYJKoZIhvcNAQEL\nBQAwWjELMAkGA1UEBhMCVVMxEDAOBgNVBAoMB1Zlcml6b24xEzARBgNVBAsMClZa\nSUFNIFRlc3QxJDAiBgNVBAMMG1Zlcml6b24gTmV0d29yayBSU0EgQ0EgVGVzdDAe\nFw0yMDEwMjIyMTE0MDNaFw0zMDEwMjIyMTE0MDNaMIGRMQswCQYDVQQGEwJVUzEL\nMAkGA1UECAwCVFgxETAPBgNVBAcMCFdlc3RsYWtlMRAwDgYDVQQKDAdWZXJpem9u\nMR0wGwYDVQQLDBRWZXJpem9uIFNvdXJjaW5nIExMQzExMC8GA1UEAwwoVmVyaXpv\nbiBOZXR3b3JrIFdFTEtUWElCIExBQiAxIDMgUlNBIElDQTCCASIwDQYJKoZIhvcN\nAQEBBQADggEPADCCAQoCggEBANhkGTXOCKEYf5znDDeX3n/DHFPVqazgQsr0/SIG\n4eb1JY5q5Jq3ZhAaZCr9HJuCkwAP/zgYH0llqOvf8AC2Uh+7z1b33IbwxPmJfWCP\nAqSNFkLWWVRdbELapCu408QsrLMW8IrdP6PLiKAepwncfm4T0/6bANqIEmUkpw8Q\nxProeiNwlGbwUll+tELmdCk7vA7hKX3j1kUvS5Z84Z5ivJBWEcUEggmC97TK4aLo\nFVEHbyahze568JVEaM1vY5L4mnRRTl+u5ipaSMxVBsiXzF7eFuKCzqF7wxbDIt2T\nIFEJtwyJDW5bXjyXgiF1d5H/URprUcRV9Qmf2+PXcfwHII8CAwEAAaOBvDCBuTAS\nBgNVHRMBAf8ECDAGAQH/AgEAMA4GA1UdDwEB/wQEAwIBBjAfBgNVHSMEGDAWgBQl\neng3lqGBeTrbLVuABoEmUHm1+TBTBgNVHR8ETDBKMEigRqBEhkJodHRwOi8vc2Vj\ndXJlLnN0YWdpbmcuc2VjdXJpdHljcmVkZW50aWFsaW5nLmNvbS9jcmwvdnpuZXRy\nc2FjYS5jcmwwHQYDVR0OBBYEFP0Z+/vaDLtAoFig1I9ttNKnmzByMA0GCSqGSIb3\nDQEBCwUAA4ICAQBuXVTf9e01HeymHgRcFCwP2N6G6u+vIzY8Bz0zSUZeRDHMZQcS\nNoabDyn5FfGJlw4BqGC591Sp0/unFQDzAg17rDBcrgwajeFeUiFdb9PiAJwHaX9S\nvq/7VmVLCmpeb+a/laXAe6+tkY1kcFrd1+ItRKC6ZGXMsoDkmk5Ndxxgw77estcI\nMiiLQbvpXRygX5wD4/ayazuLms9qITZkOZ1nTLVqq7QrwYCsSoih7hj6sbsfXr19\nGoYWmk8Y7O/d3ttgyHuRH9k/2dQ/xL7avRpMNkPdr7ocJqI46hvx2X6UyOo7IBua\nkSkFbSmPZWIVAidNMBOnvffCQ32tfjT2/xso/a9cdskvxqgLi0MPARU9Nl2Pufsb\nD7l4/sBvz/PiNTKp+Daa9FdyLb9ySidos1uS0c24bUtY1RXXGAVV2qgfyrzvzfye\nSM+w16hMU/yeYiuA1jsPmsnZnuIJj4Nv8ZjjZ0WS53pP5wcghaHkBrqWQNT8meqA\nVElrMBPlYq67T+AXP0B9lf5Sc3QVIio7XKKfqrlcQxY2JGLEyE53JgZGX7dpwU4I\nukLvyHbT4p06oY3qG6+wH8+YIXCNAYtadJ/C5/u9GcLX5NnZrcuduj0inw2/a3Ao\nWgCt6/Pr28BkCvkWdDt9d8Z40qeu1aZdcr157mR+yZGPfBfB2vasrNIEwQ==\n-----END CERTIFICATE-----\n'})
changed: [rchltxfe-93180012-rz-le0trtn-001 -> localhost] => (item={'filename': 'vz_root_ica_key.pem', 'value': '-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA2GQZNc4IoRh/nOcMN5fef8McU9WprOBCyvT9Igbh5vUljmrk\nmrdmEBpkKv0cm4KTAA//OBgfSWWo69/wALZSH7vPVvfchvDE+Yl9YI8CpI0WQtZZ\nVF1sQtqkK7jTxCyssxbwit0/o8uIoB6nCdx+bhPT/psA2ogSZSSnDxDE+uh6I3CU\nZvBSWX60QuZ0KTu8DuEpfePWRS9LlnzhnmK8kFYRxQSCCYL3tMrhougVUQdvJqHN\n7nrwlURozW9jkviadFFOX67mKlpIzFUGyJfMXt4W4oLOoXvDFsMi3ZMgUQm3DIkN\nbltePJeCIXV3kf9RGmtRxFX1CZ/b49dx/AcgjwIDAQABAoIBABSd1NkPfDr8/ouQ\nZ9WUHprFmBlUrgnOhA6aMNPhG/zJNn7PKGClQJAgM5L08pjOY/sJiyNpCPIRQXrX\npyIqPMDRP/vlOZmRrvKnas6cUYAkAQ71JSWokPv9oM6ZmXODXiDh+qEAW2PbrHS0\n9u01mMYcFYKYeghYFoiUaWZCDsJo3v3dgeE9aQ4tB9ksovSmWrpuCY7NKbd7Qrbo\n5XxQhkujTkE6knOHz8CVwYETtj8LZ/bvHIkGMGvRvwsKYDZkIKr5CZ7DX+KcMfPN\neMZU4VCHYSXNxsyp5DJ1Zw+gx8/32kUL0CzJLLam1G021Hq41KPwwSV/KPrOKel7\nHXDLXeECgYEA8MR+lgxGjYTc/k4TdZvcFVgqHGLXnyjO7ZVt4b7UpwmayLuoSD/M\nOpHQYX+JBIIWTNlGhG8UV3DPC3v+auhYa7twwbekS30IYCAmu5GCKgMAcWFinz6A\nYZxG55P/hShetCyOqikgwXqzMlwGs8KEul8f8BKssROzUy8mIlFhjq0CgYEA5hTM\nSNxAD3dlRtb0771fBU7fjx8JPfjptP9vP/JVEelkc/ti9nZ5buTC+9cQC/B+YFx7\nc82uCrXV13bGR9iH8xBhwU7JOYJZbgCpwp0F56wIN5Pdk9Eo79Batrw3oGBG4Yvt\nDc2eltxQbHgObc/qygf88j9XqD8aGIvQrc4Jf6sCgYAtxX03M1A6WTbWFau3YRD+\n8crXqKbLOCvWmODR2MB+nOHTJXHBgndl7xCJaIB43e41X9z7Ek7wrJ5/1WuxkUg1\n+uVdvna6byOnepVCdVAkgnuUEmp4UZ6AcAA+yDD8dIdEg2//w1/ZyGTGvx37EJDB\nCZJ9xl8ULuWZe84pGgWM5QKBgQCYVUbYKrNjShrM5z9uh4QlII6V1Oeql2YtBz4i\nKZE3db6jp9pi8hf+WwnZ8g9WyFjz9edqydAkmTXHHYW0ReHlBYCjm0VRhUMuuNOs\n3YfuVpFuMsFuv/oJpXqaKE3wKi5j4OAH1o7ctWuuFWMAQ7vhHZ7UySmBZJ4jiFaW\n7KaPVwKBgE8E0xbSDVGxXbEGwRXxeaOSemEHD9uEnbAyq1p3EBBhBvInWmDiP5vJ\n68IYNZ4SGxXEKDifwrLGHyekt3RK9B2+U03okd1qH7gfBIlxBJivcjhBe2PtK/Qj\n6fBN0fC1UJoE6pseT9cJDaBq2wMRXJGRYtT8fU9PPJcfa23JlKNS\n-----END RSA PRIVATE KEY-----\n'})

TASK [remote/ldap : Copy templates] ***********************************************************************************
changed: [rchltxfe-93180012-rz-le0trtn-001 -> localhost] => (item={'name': 'req-ldap.cnf', 'mode': '0644'})

TASK [remote/ldap : Generate SSL cert] ********************************************************************************
changed: [rchltxfe-93180012-rz-le0trtn-001 -> localhost]

TASK [remote/ldap : Copy templates] ***********************************************************************************
changed: [rchltxfe-93180012-rz-le0trtn-001] => (item={'name': 'dex-overrides.yaml', 'mode': '0644'})

TASK [remote/ldap : Copy SSL dex certs to server] *********************************************************************
changed: [rchltxfe-93180012-rz-le0trtn-001] => (item=dex-cert.pem)
changed: [rchltxfe-93180012-rz-le0trtn-001] => (item=dex-key.pem)
changed: [rchltxfe-93180012-rz-le0trtn-001] => (item=dex-ca.pem)

TASK [remote/ldap : Copy SSL AD cert to server] ***********************************************************************
changed: [rchltxfe-93180012-rz-le0trtn-001] => (item={'filename': 'ad_ca.pem', 'value': '-----BEGIN CERTIFICATE-----\nMIIFpTCCA42gAwIBAgIUa3vZ0YGxO1TQ8NwhiVfQC0JslXgwDQYJKoZIhvcNAQEL\nBQAwWjELMAkGA1UEBhMCVVMxEDAOBgNVBAoMB1Zlcml6b24xEzARBgNVBAsMClZa\nSUFNIFRlc3QxJDAiBgNVBAMMG1Zlcml6b24gTmV0d29yayBSU0EgQ0EgVGVzdDAe\nFw0yMDA2MTUyMTAxMTNaFw0zNTA2MTUyMTAxMTNaMFoxCzAJBgNVBAYTAlVTMRAw\nDgYDVQQKDAdWZXJpem9uMRMwEQYDVQQLDApWWklBTSBUZXN0MSQwIgYDVQQDDBtW\nZXJpem9uIE5ldHdvcmsgUlNBIENBIFRlc3QwggIiMA0GCSqGSIb3DQEBAQUAA4IC\nDwAwggIKAoICAQC8AIrksI57CbIl5uGZ6yqfpQj3aK+N8f1EVHdwK9JFskoipvC8\n7yFTk8tgmO1i0YA5oRGfNxneqCdrXZiWL6Ko8v/iln9vuN+2rK3rgWZPPRJBAsBN\na49L7U6lJjIGxIZtZqmK5h47oiUtwlYVrbZMN2ijuBQ22/eQ9tsFDV28oBuZ3WAR\npSSbj/tubPQYkw3YYOhv/VpEpsd0rkoEt3QCmTVcX2rtblanpXowTV5R0Hy4014n\nT49jrEo40r4mwYoyS835Uv4ENUFA+pXicT9eUot3RSH6rYdx4A/14UtoI9U0ol8M\n62GHpxSASQ2Kc3yQWvxRGTFslTduYM+vVmMLEDDdqcsjYnStPpwdxxmKItmbjxSv\nIwYIndp8A04WkX2iiJCciC3BNxiLamPtYVyB1HHqbGTGirKYuSvwZt337q1OI3WH\nwVn2S4Mj/wqa4iCyGTvFSUnGq34Xkrb9XNwWBok9Tc2XWGAU/mb/xcd1hX74GZbF\nsrZ11aPtym4kMAjU2KQi96GcAH2lnGZYoOja1J4Cs4WYx1uAx74H/m84CrYavVfl\n1ONJVLDfuZaEkSmu+jHQX15pAECNORTuLD06PbWnOEcOi1xmbt/OT3SA3rhD2mb7\n2wxl7oJpV3ap8xGwYmxiFzmInxFJ1axjg8Rimol0mXTKAy6OdNHbCOnAwwIDAQAB\no2MwYTAPBgNVHRMBAf8EBTADAQH/MA4GA1UdDwEB/wQEAwIBBjAfBgNVHSMEGDAW\ngBQleng3lqGBeTrbLVuABoEmUHm1+TAdBgNVHQ4EFgQUJXp4N5ahgXk62y1bgAaB\nJlB5tfkwDQYJKoZIhvcNAQELBQADggIBADQ9jpmVh9nyY7ZQ4s+S9RuSRYn7QsrW\nDePeMzQgh8ZtS8WE65GY5HS61iHNP2Co8Q1lAaBWF4ipq+VZOcQbPLccHzd1kZv4\ns4u0aTzBd9ccidl73FS0DJDQOBbzPSzgsaiGHSMyGzkTeA8z3ntsSqrXXcDUvoRi\nFus/110AwdtNhJLrWveX6btYtHp9Lqe0YtNCy5AaXlrr1yRSckP5BWVtlwD4dzSO\n/dqI3wHS/ncUx9wSQomZ+AmxYW3KtJQKgHzTqHru1x9BBk7Bzfz9FZr6HLLmEitj\nuFoDRd5TNt5LbO0zDQokvY3oqso6Htup/rS7C08mcmnelYE+yXuOc1YrlyGnpBzk\nmy+1VYbOxRRdqKAZRbE72u/h847IVpsOvjR51iksuCAurZdp2+y2zvV8NhWekuNy\nirECRy9cb4YasjRaKi0/TCGPVSICuLyeG2W72liCj/N2VKfjPP9zsOR5XjwCXfRg\n+9xhLy77/gov2NWXx5fzTkhxCrHOxFdLVMn0wQhksDmw6QsXzDIHSpIOypdDfnx9\nCsthx3nhkuHLUaEP22D22dG+vImA9ukj4R/RRI/87jmi9Q8+ehH+NqN0GZZcLjdN\nSLVXpncuwWQFUDPR06wNkkkmBSXWiIYhwqSpU0Pl3er3fD0uWvXuWPm2PzfOmUAE\nUrkzyw9XmLw0\n-----END CERTIFICATE-----\n'})

TASK [remote/ldap : Configure local-dex.tls] **************************************************************************
changed: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/ldap : Configure generic] ********************************************************************************
changed: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/ldap : Configure wadcert] ********************************************************************************
changed: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/ldap : Configure dex-overrides.yaml] *********************************************************************
changed: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/ldap : Wait for distributed cloud synchronization] *******************************************************
changed: [rchltxfe-93180012-rz-le0trtn-001 -> rchltxib-c000000-003]

TASK [remote/ldap : Remove temporary working directory] ***************************************************************
changed: [rchltxfe-93180012-rz-le0trtn-001 -> localhost]

TASK [remote/ldap : Detect oidc-auth-apps application in applying state (from a previous attempt)] ********************
changed: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/ldap : Fail if oidc-auth-apps application-abort failed] **************************************************
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/ldap : Detect oidc-auth-apps application in apply-failed or aborted state] *******************************
changed: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/ldap : Fail if oidc-auth-apps application apply failed] **************************************************
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/ldap : Apply oidc-auth-apps application] *****************************************************************
changed: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/ldap : Detect applied status of oidc-auth-apps application] **********************************************
FAILED - RETRYING: Detect applied status of oidc-auth-apps application (60 retries left).
FAILED - RETRYING: Detect applied status of oidc-auth-apps application (59 retries left).
changed: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/ldap : Fail if oidc-auth-apps application apply failed] **************************************************
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [Remote Metrics Server] ******************************************************************************************

TASK [remote/metrics-server : Set facts - 21.05] **********************************************************************
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/metrics-server : Set facts - 21.12] **********************************************************************
ok: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/metrics-server : Get software load status] ***************************************************************
changed: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/metrics-server : Noop if the system is NOT at the right caas_version] ************************************
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/metrics-server : Print message if system is NOT at the right caas_version] *******************************
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/metrics-server : Detect presence of existing application] ************************************************
fatal: [rchltxfe-93180012-rz-le0trtn-001]: FAILED! => {"changed": true, "cmd": ". /etc/platform/openrc\nsystem application-show metrics-server --column status --format value\n", "delta": "0:00:02.430601", "end": "2023-12-13 17:45:01.472202", "msg": "non-zero return code", "rc": 1, "start": "2023-12-13 17:44:59.041601", "stderr": "application not found: metrics-server", "stderr_lines": ["application not found: metrics-server"], "stdout": "", "stdout_lines": []}
...ignoring

TASK [remote/metrics-server : Print message if system already has the appication] *************************************
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/metrics-server : Apply again since the previous apply failed or in uploaded state] ***********************
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/metrics-server : Wait until apply is in the applied or apply-failed state] *******************************
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/metrics-server : Print message if re-apply succeeds] *****************************************************
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/metrics-server : Print message if re-apply failed] *******************************************************
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/metrics-server : Noop if system requires no further action or needs manual investigation] ****************
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/metrics-server : Upload application] *********************************************************************
changed: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/metrics-server : Wait until application is in the uploaded state] ****************************************
FAILED - RETRYING: Wait until application is in the uploaded state (30 retries left).
changed: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/metrics-server : Apply application] **********************************************************************
changed: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/metrics-server : Wait until application is in the applied or apply-failed state] *************************
FAILED - RETRYING: Wait until application is in the applied or apply-failed state (90 retries left).
FAILED - RETRYING: Wait until application is in the applied or apply-failed state (89 retries left).
FAILED - RETRYING: Wait until application is in the applied or apply-failed state (88 retries left).
FAILED - RETRYING: Wait until application is in the applied or apply-failed state (87 retries left).
changed: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/metrics-server : Apply again since the first apply failed] ***********************************************
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/metrics-server : Wait again until apply is in the applied or apply-failed state] *************************
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/metrics-server : Print message if apply is successful] ***************************************************
ok: [rchltxfe-93180012-rz-le0trtn-001] => {
    "msg": [
        "=======================================================",
        " rchltxfe-d93180012-001: metrics-server install SUCCEEDED! ",
        "======================================================="
    ]
}

TASK [remote/metrics-server : Print message if apply is failure] ******************************************************
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [Remote wrap-get-central-version] ********************************************************************************

TASK [remote/wrap-get-central-version : Set facts for playbook] *******************************************************
ok: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/wrap-get-central-version : Determine central WRA current version] ****************************************
fatal: [rchltxfe-93180012-rz-le0trtn-001 -> rchltxib-c000000-003]: FAILED! => {"changed": true, "cmd": ". /etc/platform/openrc\nsystem application-show wr-analytics --column app_version --format value\n", "delta": "0:00:01.269612", "end": "2023-12-13 17:46:30.793473", "msg": "non-zero return code", "rc": 1, "start": "2023-12-13 17:46:29.523861", "stderr": "application not found: wr-analytics", "stderr_lines": ["application not found: wr-analytics"], "stdout": "", "stdout_lines": []}
...ignoring

TASK [remote/wrap-get-central-version : Set facts for wra_target_version] *********************************************
ok: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/wrap-get-central-version : debug] ************************************************************************
ok: [rchltxfe-93180012-rz-le0trtn-001] => {
    "msg": "wra_target_version:"
}

TASK [Remote wrap-2112-2] *********************************************************************************************
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [Remote wrap-2106-2] *********************************************************************************************
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [Remote wrap-6] **************************************************************************************************
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [Remote fpga-user-image] *****************************************************************************************

TASK [remote/fpga-user-image : Set facts for ansible credential - 21.05] **********************************************
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/fpga-user-image : Set facts for ansible credential - 21.12] **********************************************
ok: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/fpga-user-image : Get software load status] **************************************************************
changed: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/fpga-user-image : Noop if the system is NOT at the right caas_version] ***********************************
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/fpga-user-image : Print message if system is NOT at the right caas_version] ******************************
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/fpga-user-image : Set facts for default fpga_image_file] *************************************************
ok: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/fpga-user-image : Set facts for fpga_image_file from host_vars] ******************************************
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/fpga-user-image : Print message if server is not LS3 cascadelake] ****************************************
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/fpga-user-image : Register noop because server is not LS3 cascadelake] ***********************************
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/fpga-user-image : Check if FPGA update is stuck] *********************************************************
changed: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/fpga-user-image : Abort FPGA update] *********************************************************************
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/fpga-user-image : include_tasks] *************************************************************************
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/fpga-user-image : Check FPGA update status (HPE-LS3-e910)] ***********************************************
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/fpga-user-image : Check FPGA update status (ZTS-LS3-trtn)] ***********************************************
changed: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/fpga-user-image : Noop if the system has been updated] ***************************************************
changed: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/fpga-user-image : Print message if the system has been updated] ******************************************
ok: [rchltxfe-93180012-rz-le0trtn-001] => {
    "msg": [
        "========================================================",
        " rchltxfe-d93180012-001 FPGA has already been updated! ",
        "========================================================"
    ]
}

TASK [remote/fpga-user-image : In main block] *************************************************************************
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/fpga-user-image : Copy files to host] ********************************************************************
skipping: [rchltxfe-93180012-rz-le0trtn-001] => (item=20ww43.5-1x2x25G-5GLDPC-v1.6.2-3.0.1-unsigned.bin)

TASK [remote/fpga-user-image : Do system device-image-upload] *********************************************************
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/fpga-user-image : debug - print UUID] ********************************************************************
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/fpga-user-image : Do system device-image-apply] **********************************************************
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/fpga-user-image : Do system host-device-image-update] ****************************************************
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/fpga-user-image : Wait till application completed] *******************************************************
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/fpga-user-image : Do system device-image-state-list] *****************************************************
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/fpga-user-image : force an error if image state is not completed] ****************************************
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [remote/fpga-user-image : include_tasks] *************************************************************************
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [Install DM Monitor] *********************************************************************************************

TASK [common/dm-monitor : Install DM Monitor] *************************************************************************
changed: [rchltxfe-93180012-rz-le0trtn-001]

TASK [common/dm-monitor : Wait for DM Monitor pod created] ************************************************************
changed: [rchltxfe-93180012-rz-le0trtn-001]

TASK [common/dm-monitor : Wait for control-plane pods become ready] ***************************************************
changed: [rchltxfe-93180012-rz-le0trtn-001]

TASK [common/dm-monitor : debug] **************************************************************************************
ok: [rchltxfe-93180012-rz-le0trtn-001] => {
    "dm_monitor_pod_ready.stdout_lines": [
        "pod/dm-monitor-74877db4bd-85t4t condition met"
    ]
}

TASK [Proteus MWIAT - DISABLE] ****************************************************************************************
skipping: [rchltxfe-93180012-rz-le0trtn-001]

TASK [Lock/unlock after MWAIT change] *********************************************************************************
skipping: [rchltxfe-93180012-rz-le0trtn-001]

PLAY RECAP ************************************************************************************************************
rchltxfe-93180012-rz-le0trtn-001 : ok=113  changed=61   unreachable=0    failed=0    skipped=68   rescued=1    ignored=4

(ansible_2.10.15) [XXXXXX@welktxefnce-h-pe1util-vm01 wr-installer]$

```

### Deployment of subcloud completed, now lets just validate the subcloud is upgraded 

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ dcmanager subcloud list
+----+------------------------+------------+--------------+---------------+---------+
| id | name                   | management | availability | deploy status | sync    |
+----+------------------------+------------+--------------+---------------+---------+
|  3 | welktxef-d931881-005   | managed    | online       | complete      | in-sync |
|  6 | welktxef-d931884-034   | managed    | online       | complete      | in-sync |
|  7 | rchltxfe-d93180012-001 | managed    | online       | complete      | in-sync |
+----+------------------------+------------+--------------+---------------+---------+
[XXXXXX@controller-0 ~(keystone_admin)]$ dcmanager subcloud show rchltxfe-d93180012-001
+-----------------------------+---------------------------------+
| Field                       | Value                           |
+-----------------------------+---------------------------------+
| id                          | 7                               |
| name                        | rchltxfe-d93180012-001          |
| description                 | Wind River Cloud Platform 21.12 |
| location                    | rchltxfe-d93180012-001          |
| software_version            | 21.12                           |
| management                  | managed                         |
| availability                | online                          |
| deploy_status               | complete                        |
| management_subnet           | 2607:f160:10:907b::/64          |
| management_start_ip         | 2607:f160:10:907b:ce:40a::      |
| management_end_ip           | 2607:f160:10:907b:ce:40a:0:f    |
| management_gateway_ip       | 2607:f160:10:907b:ce:28::       |
| systemcontroller_gateway_ip | 2607:f160:0:3048:cd:28::        |
| group_id                    | 1                               |
| created_at                  | 2023-12-13 15:54:55.781426      |
| updated_at                  | 2023-12-13 17:36:53.951462      |
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
[XXXXXX@controller-0 ~(keystone_admin)]$ ssh rchltxfe-d93180012-001
The authenticity of host 'rchltxfe-d93180012-001 (2607:f160:10:907b:ce:40a::)' can't be established.
ECDSA key fingerprint is SHA256:HrOK+7/p5s2Ey+vfbCbaekyxdUgkHpwtIBg1j00TQjs.
ECDSA key fingerprint is MD5:2c:72:68:9e:61:47:a3:70:eb:e0:0b:ec:01:60:24:d2.
Are you sure you want to continue connecting (yes/no)? yes
Warning: Permanently added 'rchltxfe-d93180012-001,2607:f160:10:907b:ce:40a::' (ECDSA) to the list of known hosts.
Release 21.12
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

XXXXXX@rchltxfe-d93180012-001's password:
XXXXXX denied, please try again.
XXXXXX@rchltxfe-d93180012-001's password:
XXXXXX login: Wed Dec 13 17:46:52 2023 from 2607:f160:10:9239:ce:290:0:2000
/etc/motd.d/00-header:

WARNING: Unauthorized access to this system is forbidden and will be
prosecuted by law. By accessing this system, you agree that your
actions may be monitored if unauthorized usage is suspected.

/etc/motd.d/10-system:


====================================================================
         SYSTEM: rchltxfe-d93180012-001
====================================================================

controller-0:~$

[XXXXXX@controller-0 ~(keystone_admin)]$ system show
+------------------------+--------------------------------------+
| Property               | Value                                |
+------------------------+--------------------------------------+
| contact                | None                                 |
| created_at             | 2023-12-13T16:29:19.953081+00:00     |
| description            | None                                 |
| distributed_cloud_role | subcloud                             |
| https_enabled          | True                                 |
| latitude               | None                                 |
| location               | None                                 |
| longitude              | None                                 |
| name                   | rchltxfe-d93180012-001               |
| region_name            | rchltxfe-d93180012-001               |
| sdn_enabled            | False                                |
| security_feature       | spectre_meltdown_v1                  |
| service_project_name   | services                             |
| shared_services        | []                                   |
| software_version       | 21.12                                |
| system_mode            | simplex                              |
| system_type            | All-in-one                           |
| timezone               | UTC                                  |
| updated_at             | 2023-12-13T17:41:31.309394+00:00     |
| uuid                   | 4b4996b9-b5bd-447f-ab81-f2a1f6b8dfda |
| vswitch_type           | none                                 |
+------------------------+--------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ system application-list
+--------------------------+----------+-----------------------------------+----------------------------------------+----------+-----------+
| application              | version  | manifest name                     | manifest file                          | status   | progress  |
+--------------------------+----------+-----------------------------------+----------------------------------------+----------+-----------+
| cert-manager             | 21.12-28 | cert-manager-manifest             | certmanager-manifest.yaml              | applied  | completed |
| metrics-server           | 21.12-9  | metrics-server-manifest           | metrics-server_manifest.yaml           | applied  | completed |
| nginx-ingress-controller | 21.12-18 | nginx-ingress-controller-manifest | nginx_ingress_controller_manifest.yaml | applied  | completed |
| oidc-auth-apps           | 21.12-61 | oidc-auth-manifest                | manifest.yaml                          | applied  | completed |
| platform-integ-apps      | 21.12-46 | platform-integration-manifest     | manifest.yaml                          | applied  | completed |
| rook-ceph-apps           | 1.0-14   | rook-ceph-manifest                | manifest.yaml                          | uploaded | completed |
+--------------------------+----------+-----------------------------------+----------------------------------------+----------+-----------+
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

[XXXXXX@controller-0 ~(keystone_admin)]$


```

### Test is complete, new subcloud deployment worked as expected