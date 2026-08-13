# ZT .45 BMC firmware validation
# Firmware installation testing
# 11/15/23 James Patchett

## Target Controller welktxef-c000004-001 CR-4 (LaaS System)
OAM 2607:f160:10:9051:ce:290:0:1000

## Target Subcloud welktxef-d1372466-006 (LaaS System)
OAM: 2607:f160:10:9804:ce:40a:0:f401
ILO: 2607:f160:10:9084:ce:40a:0:e003

ipmitool -I lanplus -U XXXXXX -P XXXXXX -H 2607:f160:10:9084:ce:40a:0:e003 sol activate

## Subcloud rchltxfe-d93180012-001 (VCP-fe Infrastructure)
OAM: 2607:f160:10:9073:ce:40a:0:f400
ILO: 2607:f160:10:9073:ce:406:0:1000

ipmitool -I lanplus -U XXXXXX -P XXXXXX -H 2607:f160:10:9073:ce:406:0:1000 sol activate

## Test Case
### Install Firmware to 2.17 base with 2.06 bios
### Pause 5 mins 
### Install Firmware to 2.27 with 2.06 bios
### Repeat until you have 15 iterations of installing 2.27

## Subcloud rchltxfe-d93180012-001 (VCP-fe Infrastructure)
## Ran test 15 iterations with no issue on this host.
## Logs have been uploaded of upgrade and downgrade runs.

