# E920t SSD Firmware in field came as GDC7302Q but should only be GDC7202Q
# HPe should send parts that have the right firmware levels (Brusca will escalate)
# Procedure has been written so that field can have some way of dealing with this issue if they come across it again
# James Patchett
# Date 10/28/24

# MTCELab e920t host welktxef-d931884-034
OAM:  2607:f160:10:9249:ce:40a:0:f40
ILO:  2607:f160:10:9249:ce:40a:0:e009

# HPE provided instructions for SSD firmware upgrade/downgrade
```log
Installation:

To install firmware from Linux operating system on target server:

 

Execute the below commands:

> rpm -Uvh <filename>.rpm
 
See where the files land
> rpm -qlp <filename>.rpm
 
Change(cd) to the directory you see in the previous step and run hpsetup by typing ‘./setup’ at the command prompt.

Note: Installing the firmware rpm package (rpm -ivh) does not update the firmware.  It merely extracts the rpm content to the local system. Updating the firmware on the local system requires following the above outlined steps.

```

## First we must upgrade a current e920t in the MTCE Lab to get to the latest version of SSD firmware
## need filename firmware-hdd-samsung-pm9a3-GDC7302Q-1.1.x86_64.rpm

## ssh to host to install RPM and run HPe setup utility.
## I pushed both files to the e920t
```log
[XXXXXX@controller-0 SSD(keystone_admin)]$ ls -latr
total 19664
-rw-r--r--  1 XXXXXX sys_protected 10061563 Oct 28 20:14 firmware-hdd-samsung-pm9a3-GDC7202Q-1.1.x86_64.rpm
-rw-r--r--  1 XXXXXX sys_protected 10063006 Oct 28 20:14 firmware-hdd-samsung-pm9a3-GDC7302Q-1.1.x86_64.rpm
drwxr-xr-x 10 XXXXXX sys_protected     4096 Oct 28 20:15 ..
drwxr-xr-x  2 XXXXXX sys_protected     4096 Oct 28 20:15 .
[XXXXXX@controller-0 SSD(keystone_admin)]$
[XXXXXX@controller-0 SSD(keystone_admin)]$ rpm -Uvh firmware-hdd-samsung-pm9a3-GDC7302Q-1.1.x86_64.rpm
rpm: RPM should not be used directly install RPM packages, use Alien instead!
rpm: However assuming you know what you are doing...
warning: firmware-hdd-samsung-pm9a3-GDC7302Q-1.1.x86_64.rpm: Header V3 RSA/SHA256 Signature, key ID 26c2b797: NOKEY
error: Failed dependencies:
	/bin/sh is needed by firmware-hdd-samsung-pm9a3-GDC7302Q-1.1.x86_64
	libc.so.6()(64bit) is needed by firmware-hdd-samsung-pm9a3-GDC7302Q-1.1.x86_64
	libc.so.6(GLIBC_2.14)(64bit) is needed by firmware-hdd-samsung-pm9a3-GDC7302Q-1.1.x86_64
	libc.so.6(GLIBC_2.2.5)(64bit) is needed by firmware-hdd-samsung-pm9a3-GDC7302Q-1.1.x86_64
	libc.so.6(GLIBC_2.3)(64bit) is needed by firmware-hdd-samsung-pm9a3-GDC7302Q-1.1.x86_64
	libc.so.6(GLIBC_2.3.4)(64bit) is needed by firmware-hdd-samsung-pm9a3-GDC7302Q-1.1.x86_64
	libc.so.6(GLIBC_2.4)(64bit) is needed by firmware-hdd-samsung-pm9a3-GDC7302Q-1.1.x86_64
	libc.so.6(GLIBC_2.7)(64bit) is needed by firmware-hdd-samsung-pm9a3-GDC7302Q-1.1.x86_64
	libdl.so.2()(64bit) is needed by firmware-hdd-samsung-pm9a3-GDC7302Q-1.1.x86_64
	libdl.so.2(GLIBC_2.2.5)(64bit) is needed by firmware-hdd-samsung-pm9a3-GDC7302Q-1.1.x86_64
	libgcc_s.so.1()(64bit) is needed by firmware-hdd-samsung-pm9a3-GDC7302Q-1.1.x86_64
	libgcc_s.so.1(GCC_3.0)(64bit) is needed by firmware-hdd-samsung-pm9a3-GDC7302Q-1.1.x86_64
	libm.so.6()(64bit) is needed by firmware-hdd-samsung-pm9a3-GDC7302Q-1.1.x86_64
	libpthread.so.0()(64bit) is needed by firmware-hdd-samsung-pm9a3-GDC7302Q-1.1.x86_64
	libpthread.so.0(GLIBC_2.2.5)(64bit) is needed by firmware-hdd-samsung-pm9a3-GDC7302Q-1.1.x86_64
	libstdc++.so.6()(64bit) is needed by firmware-hdd-samsung-pm9a3-GDC7302Q-1.1.x86_64
	libstdc++.so.6(GLIBCXX_3.4)(64bit) is needed by firmware-hdd-samsung-pm9a3-GDC7302Q-1.1.x86_64
	libuuid.so.1()(64bit) is needed by firmware-hdd-samsung-pm9a3-GDC7302Q-1.1.x86_64
	libz.so.1()(64bit) is needed by firmware-hdd-samsung-pm9a3-GDC7302Q-1.1.x86_64
[XXXXXX@controller-0 SSD(keystone_admin)]$
[XXXXXX@controller-0 SSD(keystone_admin)]$
[XXXXXX@controller-0 SSD(keystone_admin)]$ rpm -qlp firmware-hdd-samsung-pm9a3-GDC7302Q-1.1.x86_64.rpm
warning: firmware-hdd-samsung-pm9a3-GDC7302Q-1.1.x86_64.rpm: Header V3 RSA/SHA256 Signature, key ID 26c2b797: NOKEY
/usr/lib/x86_64-linux-gnu/firmware-hdd-samsung-pm9a3-GDC7302Q-1.1
/usr/lib/x86_64-linux-gnu/firmware-hdd-samsung-pm9a3-GDC7302Q-1.1/.cpq_package.inc
/usr/lib/x86_64-linux-gnu/firmware-hdd-samsung-pm9a3-GDC7302Q-1.1/.setup
/usr/lib/x86_64-linux-gnu/firmware-hdd-samsung-pm9a3-GDC7302Q-1.1/CP054677.xml
/usr/lib/x86_64-linux-gnu/firmware-hdd-samsung-pm9a3-GDC7302Q-1.1/GDC7302Q.bin
/usr/lib/x86_64-linux-gnu/firmware-hdd-samsung-pm9a3-GDC7302Q-1.1/hpsetup
/usr/lib/x86_64-linux-gnu/firmware-hdd-samsung-pm9a3-GDC7302Q-1.1/ilorest_chif.so
/usr/lib/x86_64-linux-gnu/firmware-hdd-samsung-pm9a3-GDC7302Q-1.1/nvme
/usr/lib/x86_64-linux-gnu/firmware-hdd-samsung-pm9a3-GDC7302Q-1.1/payload.json
/usr/lib/x86_64-linux-gnu/firmware-hdd-samsung-pm9a3-GDC7302Q-1.1/setup
/usr/lib/x86_64-linux-gnu/hp-scexe-compat
/usr/lib/x86_64-linux-gnu/hp-scexe-compat/CP054677.scexe
/usr/lib/x86_64-linux-gnu/scexe-compat
/usr/lib/x86_64-linux-gnu/scexe-compat/CP054677.scexe
[XXXXXX@controller-0 SSD(keystone_admin)]$


```

## HPE instructions says to cd to directory where the "setup" file is

```log


```