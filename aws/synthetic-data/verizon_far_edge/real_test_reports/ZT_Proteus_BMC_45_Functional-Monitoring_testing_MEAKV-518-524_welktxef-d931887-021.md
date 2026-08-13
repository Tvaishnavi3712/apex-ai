# ZT .45 BMC firmware validation
# Redfish Functional Testing MEAKV-518-524
# 11/1/23 James Patchett

## Target Controller Rchltxfe-c000000-001
Controller-0 iLO 2607:f160:a:d02e:cd:fe0::8000 
Controller-1 iLO 2607:f160:a:d02e:cd:fe0::8001
Worker-0 iLO 2607:f160:a:d02e:cd:fe0::8002 
OAM 2607:f160:0:3043:cd:290:0:10

## Target Subcloud welktxef-d931887-021 (currently on controller 2607:f160:0:3049:cd:290:0:10 )
OAM 2607:f160:10:9249:ce:40a:0:f409
BMC 2607:f160:10:9249:ce:40a:0:e015

ipmitool -I lanplus -U XXXXXX -P XXXXXX -H 2607:f160:10:9249:ce:40a:0:e015 sol activate

## Subcloud welktxef-d931887-021

## .45 BMC has been deployed to 2 FOA Grow sites to be evaulated in with production collection tools
## Validation found that some of the metrics have changed slightly in formatting or names of the metric has changed.
## Craig Cerney has agreed the changes are ok, and his team can work with them and integrate them
## Metrics has been validated

