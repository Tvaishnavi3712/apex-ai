# ZT .45 BMC firmware validation
# Firmware installation testing with a host that has many SEL messages logged (300+)
# 11/29/23 James Patchett

## Target Controller welktxef-c000004-001 CR-4 (LaaS System)
OAM 2607:f160:10:9051:ce:290:0:1000

## Target Subcloud welktxef-d1372466-006 (LaaS System)
OAM: 2607:f160:10:9804:ce:40a:0:f401
ILO: 2607:f160:10:9084:ce:40a:0:e003

ipmitool -I lanplus -U XXXXXX -P XXXXXX -H 2607:f160:10:9084:ce:40a:0:e003 sol activate

## Test Case
### Install Firmware to 2.27 with 2.06 bios, let soak with system with bad fan to create many SEL messages

## Host upgrade with 300+ sels logged was successfully upgraded from 2.27 to 2.27

It appears having multiple SEL messages logged to BMC didn't cause upgrade failures with 2.27, seems issue with inital install on host was a fluke possibly.
