# ZT Proteus BMC 3.02 with BIOS 0.30
# 9/28/25 James Patchett - MTCE Lab VCPfe
# MEAKV-224 Deployment test 24.09.301
 
## welktxef-931886-rz-le0pts6-002  welktxef-d931886-002
BMC:  2607:f160:10:9249:ce:40a:0:e039
OAM:  2607:f160:10:9249:ce:40a:0:f439

### deployment of 24.09.301
### lost the full deployment log with tmux session

```log


====================================================================
         SYSTEM: welktxef-d931886-002
====================================================================

Linux controller-0 6.6.0-1-rt-amd64 #1 SMP PREEMPT_RT StarlingX Debian 6.6.71-1.stx.104 (2025-09-24) x86_64
Last login: Sat Oct  4 16:44:37 2025 from 2607:f160:0:3042:cd:290:0:11
XXXXXX@controller-0:~$
XXXXXX@controller-0:~$
XXXXXX@controller-0:~$ source /etc/platform/openrc ; alias k=kubectl
[XXXXXX@controller-0 ~(keystone_admin)]$
[XXXXXX@controller-0 ~(keystone_admin)]$
[XXXXXX@controller-0 ~(keystone_admin)]$ sudo dmidecode -t system
Password:
XXXXXX dmidecode 3.3
Getting SMBIOS data from sysfs.
SMBIOS 3.3.0 present.

Handle 0x0001, DMI type 1, 27 bytes
System Information
	Manufacturer: ZTSYSTEMS
	Product Name: Proteus I_Mix
	Version:
	Serial Number: 20743160N038
	UUID: 4344545a-1041-3100-3350-d04b31373837
	Wake-up Type: Power Switch
	SKU Number: PA-00371-003
	Family: To be filled by O.E.M.

[XXXXXX@controller-0 ~(keystone_admin)]$
[XXXXXX@controller-0 ~(keystone_admin)]$ sudo dmidecode -t bios
# dmidecode 3.3
Getting SMBIOS data from sysfs.
SMBIOS 3.3.0 present.

Handle 0x0000, DMI type 0, 26 bytes
BIOS Information
	Vendor: American Megatrends International, LLC.
	Version: 0.30
	Release Date: 08/04/2023
	Address: 0xF0000
	Runtime Size: 64 kB
	ROM Size: 32 MB
	Characteristics:
		PCI is supported
		BIOS is upgradeable
		BIOS shadowing is allowed
		Boot from CD is supported
		Selectable boot is supported
		BIOS ROM is socketed
		EDD is supported
		Japanese floppy for NEC 9800 1.2 MB is supported (int 13h)
		Japanese floppy for Toshiba 1.2 MB is supported (int 13h)
		5.25"/360 kB floppy services are supported (int 13h)
		5.25"/1.2 MB floppy services are supported (int 13h)
		3.5"/720 kB floppy services are supported (int 13h)
		3.5"/2.88 MB floppy services are supported (int 13h)
		Print screen service is supported (int 5h)
		Serial services are supported (int 14h)
		Printer services are supported (int 17h)
		CGA/mono video services are supported (int 10h)
		USB legacy is supported
		BIOS boot specification is supported
		Targeted content distribution is supported
		UEFI is supported
	BIOS Revision: 0.30
	Firmware Revision: 3.2

[XXXXXX@controller-0 ~(keystone_admin)]$ software list
+----------------+------+----------+
| Release        | RR   |  State   |
+----------------+------+----------+
| WRCP-24.09.301 | True | deployed |
+----------------+------+----------+
[XXXXXX@controller-0 ~(keystone_admin)]$ ip a show|grep 2607
    inet6 2607:f160:10:9249:ce:40a:0:f439/64 scope global
    inet6 2607:f160:10:80e9:ce:40a::/64 scope global deprecated
    inet6 2607:f160:10:80e9:ce:40a:0:1/64 scope global
timed out waiting for input: auto-logout]$
Connection to 2607:f160:10:9249:ce:40a:0:f439 closed.
[XXXXXX@welktxme-jump140 ~]$



```