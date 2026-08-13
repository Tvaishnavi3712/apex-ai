# ZT Proteus 3.02 BMC firmware validation
# ZT Proteus BIOS .30
# 10/06/25 James Patchett


## welktxef-931886-rz-le0pts6-002  welktxef-d931886-002
BMC:  2607:f160:10:9249:ce:40a:0:e039
OAM:  2607:f160:10:9249:ce:40a:0:f439

## Subcloud welktxef-d931886-002 Info
```log
[XXXXXX@controller-0 ~(keystone_admin)]$ system show
+------------------------+--------------------------------------+
| Property               | Value                                |
+------------------------+--------------------------------------+
| contact                | None                                 |
| created_at             | 2025-10-02T03:20:34.430032+00:00     |
| description            | None                                 |
| distributed_cloud_role | subcloud                             |
| https_enabled          | True                                 |
| latitude               | None                                 |
| location               | None                                 |
| longitude              | None                                 |
| name                   | welktxef-d931886-002                 |
| region_name            | 56b45e35004a45bbaeea1610dd59d4bb     |
| sdn_enabled            | False                                |
| security_feature       | spectre_meltdown_v1                  |
| service_project_name   | services                             |
| shared_services        | []                                   |
| software_version       | 24.09                                |
| system_mode            | simplex                              |
| system_type            | All-in-one                           |
| timezone               | UTC                                  |
| updated_at             | 2025-10-02T03:37:29.274751+00:00     |
| uuid                   | ae9a40ed-0285-4d83-a37c-c4b4fb5f6be6 |
| vswitch_type           | none                                 |
+------------------------+--------------------------------------+
[XXXXXX@controller-0 ~(keystone_admin)]$ system application-list
+--------------------------+----------+-------------------------------------------+------------------+----------+-----------+
| application              | version  | manifest name                             | manifest file    | status   | progress  |
+--------------------------+----------+-------------------------------------------+------------------+----------+-----------+
| cert-manager             | 24.09-79 | cert-manager-fluxcd-manifests             | fluxcd-manifests | applied  | completed |
| dell-storage             | 24.09-26 | dell-storage-fluxcd-manifests             | fluxcd-manifests | uploaded | completed |
| deployment-manager       | 24.09-30 | deployment-manager-fluxcd-manifests       | fluxcd-manifests | applied  | completed |
| metrics-server           | 24.09-59 | metrics-server-fluxcd-manifests           | fluxcd-manifests | applied  | completed |
| nginx-ingress-controller | 24.09-67 | nginx-ingress-controller-fluxcd-manifests | fluxcd-manifests | applied  | completed |
| oidc-auth-apps           | 24.09-66 | oidc-auth-apps-fluxcd-manifests           | fluxcd-manifests | applied  | completed |
| platform-integ-apps      | 24.      | platform-integ-apps-fluxcd-manifests      | fluxcd-manifests | applied  | completed |
|                          | 09-144   |                                           |                  |          |           |
|                          |          |                                           |                  |          |           |
| ptp-notification         | 24.      | ptp-notification-fluxcd-manifests         | fluxcd-manifests | applied  | completed |
|                          | 09-191   |                                           |                  |          |           |
|                          |          |                                           |                  |          |           |
| rook-ceph                | 24.09-78 | rook-ceph-fluxcd-manifests                | fluxcd-manifests | uploaded | completed |
| sriov-fec-operator       | 24.09-45 | sriov-fec-operator-fluxcd-manifests       | fluxcd-manifests | applied  | completed |
| wr-analytics             | 24.09-1  | wr-analytics-fluxcd-manifests             | fluxcd-manifests | applied  | completed |
+--------------------------+----------+-------------------------------------------+------------------+----------+-----------+
[XXXXXX@controller-0 ~(keystone_admin)]$ sw-patch query
Patch ID  RR  Release  Patch State
========  ==  =======  ===========

[XXXXXX@controller-0 ~(keystone_admin)]$ software list
+----------------+------+----------+
| Release        | RR   |  State   |
+----------------+------+----------+
| WRCP-24.09.301 | True | deployed |
+----------------+------+----------+
[XXXXXX@controller-0 ~(keystone_admin)]$
```

## Check Sensors before we start load

```log
root@controller-0:/var/home/XXXXXX/stressng-fans# ipmitool sensor | grep -e CPU_0_TEMP -e CPU0_Power -e FAN -e CPU_CUPS
CPU_0_TEMP       | 49.000     | degrees C  | ok    | na        | na        | na        | 96.000    | 98.000    | na
CPU0_Power       | 69.000     | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 5000.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1B       | 5500.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_2A       | 5000.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_2B       | 5500.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1A_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1B_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_2A_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_2B_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
CPU_CUPS         | 1.000      | percent    | ok    | na        | na        | na        | na        | 100.000   | na
PSU_1_FAN        | 4000.000   | RPM        | ok    | 800.000   | 1120.000  | na        | na        | na        | na
PSU_2_FAN        | 4000.000   | RPM        | ok    | 800.000   | 1120.000  | na        | na        | na        | na
root@controller-0:/var/home/XXXXXX/stressng-fans#

```

## Setup Stressng to use as load driver

```log
[XXXXXX@controller-0 ~(keystone_admin)]$ ls -l stressng-fans-testing.tar.gz
-rw-r--r-- 1 XXXXXX sys_protected 2619 Oct  8 17:20 stressng-fans-testing.tar.gz
[XXXXXX@controller-0 ~(keystone_admin)]$ tar xvfz stressng-fans-testing.tar.gz
stressng-fans/
stressng-fans/18-stressng-fan.yaml
stressng-fans/25-stressng-fan.yaml
stressng-fans/40-stressng-fan.yaml
stressng-fans/34-stressng-fan.yaml
stressng-fans/54-stressng-fan.yaml
stressng-fans/27-stressng-fan.yaml
stressng-fans/55-stressng-fan.yaml
stressng-fans/22-stressng-fan.yaml
stressng-fans/3-stressng-fan.yaml
stressng-fans/19-stressng-fan.yaml
stressng-fans/20-stressng-fan.yaml
stressng-fans/2-stressng-fan.yaml
stressng-fans/42-stressng-fan.yaml
stressng-fans/stressng_fans.yaml
stressng-fans/8-stressng-fan.yaml
stressng-fans/38-stressng-fan.yaml
stressng-fans/6-stressng-fan.yaml
stressng-fans/45-stressng-fan.yaml
stressng-fans/52-stressng-fan.yaml
stressng-fans/44-stressng-fan.yaml
stressng-fans/35-stressng-fan.yaml
stressng-fans/53-stressng-fan.yaml
stressng-fans/4-stressng-fan.yaml
stressng-fans/46-stressng-fan.yaml
stressng-fans/9-stressng-fan.yaml
stressng-fans/51-stressng-fan.yaml
stressng-fans/11-stressng-fan.yaml
stressng-fans/14-stressng-fan.yaml
stressng-fans/56-stressng-fan.yaml
stressng-fans/41-stressng-fan.yaml
stressng-fans/README
stressng-fans/30-stressng-fan.yaml
stressng-fans/50-stressng-fan.yaml
stressng-fans/32-stressng-fan.yaml
stressng-fans/33-stressng-fan.yaml
stressng-fans/17-stressng-fan.yaml
stressng-fans/13-stressng-fan.yaml
stressng-fans/29-stressng-fan.yaml
stressng-fans/28-stressng-fan.yaml
stressng-fans/5-stressng-fan.yaml
stressng-fans/31-stressng-fan.yaml
stressng-fans/24-stressng-fan.yaml
stressng-fans/48-stressng-fan.yaml
stressng-fans/21-stressng-fan.yaml
stressng-fans/23-stressng-fan.yaml
stressng-fans/16-stressng-fan.yaml
stressng-fans/run_pods.sh
stressng-fans/12-stressng-fan.yaml
stressng-fans/43-stressng-fan.yaml
stressng-fans/1-stressng-fan.yaml
stressng-fans/15-stressng-fan.yaml
stressng-fans/47-stressng-fan.yaml
stressng-fans/37-stressng-fan.yaml
stressng-fans/49-stressng-fan.yaml
stressng-fans/10-stressng-fan.yaml
stressng-fans/7-stressng-fan.yaml
stressng-fans/36-stressng-fan.yaml
stressng-fans/39-stressng-fan.yaml
stressng-fans/26-stressng-fan.yaml
[XXXXXX@controller-0 ~(keystone_admin)]$
[XXXXXX@controller-0 ~(keystone_admin)]$ cd stressng-fans/
[XXXXXX@controller-0 stressng-fans(keystone_admin)]$ cat stressng_fans.yaml
apiVersion: v1
kind: Pod
metadata:
  name: POD_NAME
  namespace: default
spec:
  containers:
  - name: stressng
    image: wsregistry.mtce.vzwops.com:443/vcp_far_edge_in_building_docker/testing/load/alpine_stressng:v0.2
    imagePullPolicy: IfNotPresent
    command: ["/usr/bin/stress-ng"]
    args:
      - "--cpu"
      - "0"
      - "--cpu-method"
      - "matrixprod"
      - "--matrix"
      - "0"
      - "--matrix-size"
      - "128"
      - "--ignite-cpu"
      - "--maximize"
      - "-t"
      - "300s"
    resources:
      requests:
        cpu: "0"
        memory: "500Mi"
        windriver.com/isolcpus: "1"
      limits:
        cpu:  "0"
        memory: "500Mi"
        windriver.com/isolcpus: "1"
  restartPolicy: Never
  nodeSelector:
    kubernetes.io/hostname: controller-0
[XXXXXX@controller-0 stressng-fans(keystone_admin)]$
[XXXXXX@controller-0 stressng-fans(keystone_admin)]$ count=1
while [ $count -lt 57 ] ; do
cat stressng_fans.yaml | sed "s/POD_NAME/stressng-fan-james${count}/g" > ${count}-stressng-fan.yaml
count=$((count+1))
done
[XXXXXX@controller-0 stressng-fans(keystone_admin)]$
[XXXXXX@controller-0 stressng-fans(keystone_admin)]$ echo "" > run_pods.sh
ls *-stressng-fan.yaml | while read file ; do
echo "kubectl create -f $file" >> run_pods.sh
done
[XXXXXX@controller-0 stressng-fans(keystone_admin)]$
[XXXXXX@controller-0 stressng-fans(keystone_admin)]$ chmod 755 run_pods.sh
[XXXXXX@controller-0 stressng-fans(keystone_admin)]$
[XXXXXX@controller-0 stressng-fans(keystone_admin)]$ cat run_pods.sh

kubectl create -f 10-stressng-fan.yaml
kubectl create -f 11-stressng-fan.yaml
kubectl create -f 12-stressng-fan.yaml
kubectl create -f 13-stressng-fan.yaml
kubectl create -f 14-stressng-fan.yaml
kubectl create -f 15-stressng-fan.yaml
kubectl create -f 16-stressng-fan.yaml
kubectl create -f 17-stressng-fan.yaml
kubectl create -f 18-stressng-fan.yaml
kubectl create -f 19-stressng-fan.yaml
kubectl create -f 1-stressng-fan.yaml
kubectl create -f 20-stressng-fan.yaml
kubectl create -f 21-stressng-fan.yaml
kubectl create -f 22-stressng-fan.yaml
kubectl create -f 23-stressng-fan.yaml
kubectl create -f 24-stressng-fan.yaml
kubectl create -f 25-stressng-fan.yaml
kubectl create -f 26-stressng-fan.yaml
kubectl create -f 27-stressng-fan.yaml
kubectl create -f 28-stressng-fan.yaml
kubectl create -f 29-stressng-fan.yaml
kubectl create -f 2-stressng-fan.yaml
kubectl create -f 30-stressng-fan.yaml
kubectl create -f 31-stressng-fan.yaml
kubectl create -f 32-stressng-fan.yaml
kubectl create -f 33-stressng-fan.yaml
kubectl create -f 34-stressng-fan.yaml
kubectl create -f 35-stressng-fan.yaml
kubectl create -f 36-stressng-fan.yaml
kubectl create -f 37-stressng-fan.yaml
kubectl create -f 38-stressng-fan.yaml
kubectl create -f 39-stressng-fan.yaml
kubectl create -f 3-stressng-fan.yaml
kubectl create -f 40-stressng-fan.yaml
kubectl create -f 41-stressng-fan.yaml
kubectl create -f 42-stressng-fan.yaml
kubectl create -f 43-stressng-fan.yaml
kubectl create -f 44-stressng-fan.yaml
kubectl create -f 45-stressng-fan.yaml
kubectl create -f 46-stressng-fan.yaml
kubectl create -f 47-stressng-fan.yaml
kubectl create -f 48-stressng-fan.yaml
kubectl create -f 49-stressng-fan.yaml
kubectl create -f 4-stressng-fan.yaml
kubectl create -f 50-stressng-fan.yaml
kubectl create -f 51-stressng-fan.yaml
kubectl create -f 52-stressng-fan.yaml
kubectl create -f 53-stressng-fan.yaml
kubectl create -f 54-stressng-fan.yaml
kubectl create -f 55-stressng-fan.yaml
kubectl create -f 56-stressng-fan.yaml
kubectl create -f 5-stressng-fan.yaml
kubectl create -f 6-stressng-fan.yaml
kubectl create -f 7-stressng-fan.yaml
kubectl create -f 8-stressng-fan.yaml
kubectl create -f 9-stressng-fan.yaml
[XXXXXX@controller-0 stressng-fans(keystone_admin)]$
```

## Initiate  load with run_pods.sh

```log
[XXXXXX@controller-0 stressng-fans(keystone_admin)]$ ./run_pods.sh
pod/stressng-fan-james10 created
pod/stressng-fan-james11 created
pod/stressng-fan-james12 created
pod/stressng-fan-james13 created
pod/stressng-fan-james14 created
pod/stressng-fan-james15 created
pod/stressng-fan-james16 created
pod/stressng-fan-james17 created
pod/stressng-fan-james18 created
pod/stressng-fan-james19 created
pod/stressng-fan-james1 created
pod/stressng-fan-james20 created
pod/stressng-fan-james21 created
pod/stressng-fan-james22 created
pod/stressng-fan-james23 created
pod/stressng-fan-james24 created
pod/stressng-fan-james25 created
pod/stressng-fan-james26 created
pod/stressng-fan-james27 created
pod/stressng-fan-james28 created
pod/stressng-fan-james29 created
pod/stressng-fan-james2 created
pod/stressng-fan-james30 created
pod/stressng-fan-james31 created
pod/stressng-fan-james32 created
pod/stressng-fan-james33 created
pod/stressng-fan-james34 created
pod/stressng-fan-james35 created
pod/stressng-fan-james36 created
pod/stressng-fan-james37 created
pod/stressng-fan-james38 created
pod/stressng-fan-james39 created
pod/stressng-fan-james3 created
pod/stressng-fan-james40 created
pod/stressng-fan-james41 created
pod/stressng-fan-james42 created
pod/stressng-fan-james43 created
pod/stressng-fan-james44 created
pod/stressng-fan-james45 created
pod/stressng-fan-james46 created
pod/stressng-fan-james47 created
pod/stressng-fan-james48 created
pod/stressng-fan-james49 created
pod/stressng-fan-james4 created
pod/stressng-fan-james50 created
pod/stressng-fan-james51 created
pod/stressng-fan-james52 created
pod/stressng-fan-james53 created
pod/stressng-fan-james54 created
pod/stressng-fan-james55 created
pod/stressng-fan-james56 created
pod/stressng-fan-james5 created
pod/stressng-fan-james6 created
pod/stressng-fan-james7 created
pod/stressng-fan-james8 created
pod/stressng-fan-james9 created
[XXXXXX@controller-0 stressng-fans(keystone_admin)]$
[XXXXXX@controller-0 stressng-fans(keystone_admin)]$ kubectl get pods
NAME                   READY   STATUS    RESTARTS   AGE
stressng-fan-james1    1/1     Running   0          56s
stressng-fan-james10   1/1     Running   0          60s
stressng-fan-james11   1/1     Running   0          60s
stressng-fan-james12   1/1     Running   0          60s
stressng-fan-james13   1/1     Running   0          60s
stressng-fan-james14   1/1     Running   0          59s
stressng-fan-james15   1/1     Running   0          59s
stressng-fan-james16   1/1     Running   0          58s
stressng-fan-james17   1/1     Running   0          58s
stressng-fan-james18   1/1     Running   0          57s
stressng-fan-james19   1/1     Running   0          57s
stressng-fan-james2    1/1     Running   0          51s
stressng-fan-james20   1/1     Running   0          56s
stressng-fan-james21   1/1     Running   0          55s
stressng-fan-james22   1/1     Running   0          55s
stressng-fan-james23   1/1     Running   0          54s
stressng-fan-james24   1/1     Running   0          53s
stressng-fan-james25   1/1     Running   0          53s
stressng-fan-james26   1/1     Running   0          53s
stressng-fan-james27   1/1     Running   0          52s
stressng-fan-james28   1/1     Running   0          52s
stressng-fan-james29   1/1     Running   0          51s
stressng-fan-james3    1/1     Running   0          44s
stressng-fan-james30   1/1     Running   0          50s
stressng-fan-james31   1/1     Running   0          50s
stressng-fan-james32   1/1     Running   0          49s
stressng-fan-james33   1/1     Running   0          48s
stressng-fan-james34   1/1     Running   0          47s
stressng-fan-james35   1/1     Running   0          47s
stressng-fan-james36   1/1     Running   0          46s
stressng-fan-james37   1/1     Running   0          45s
stressng-fan-james38   1/1     Running   0          45s
stressng-fan-james39   1/1     Running   0          44s
stressng-fan-james4    1/1     Running   0          39s
stressng-fan-james40   1/1     Running   0          43s
stressng-fan-james41   1/1     Running   0          43s
stressng-fan-james42   1/1     Running   0          42s
stressng-fan-james43   1/1     Running   0          42s
stressng-fan-james44   1/1     Running   0          41s
stressng-fan-james45   1/1     Running   0          41s
stressng-fan-james46   1/1     Running   0          40s
stressng-fan-james47   1/1     Running   0          40s
stressng-fan-james48   1/1     Running   0          39s
stressng-fan-james49   1/1     Running   0          39s
stressng-fan-james5    1/1     Running   0          34s
stressng-fan-james50   1/1     Running   0          38s
stressng-fan-james51   1/1     Running   0          37s
stressng-fan-james52   1/1     Running   0          37s
stressng-fan-james53   1/1     Running   0          37s
stressng-fan-james54   1/1     Running   0          36s
stressng-fan-james55   1/1     Running   0          35s
stressng-fan-james56   1/1     Running   0          35s
stressng-fan-james6    1/1     Running   0          34s
stressng-fan-james7    1/1     Running   0          33s
stressng-fan-james8    1/1     Running   0          33s
stressng-fan-james9    1/1     Running   0          32s
[XXXXXX@controller-0 stressng-fans(keystone_admin)]$
top - 19:02:42 up 6 days,  1:31,  2 users,  load average: 91.73, 34.40, 16.30
Tasks: 2521 total, 113 running, 2389 sleeping,   0 stopped,  19 zombie
%Cpu(s): 88.9 us,  1.1 sy,  0.1 ni,  9.8 id,  0.0 wa,  0.0 hi,  0.1 si,  0.0 st
MiB Mem : 126166.2 total,  33326.6 free,  70833.9 used,  22005.7 buff/cache
MiB Swap:      0.0 total,      0.0 free,      0.0 used.  52526.8 avail Mem

    PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+  P NU CGNAME                              COMMAND
1157407 root      20   0   66216   1536    512 R  50.3   0.0   0:49.09 34  0 systemd:/k8s-infra/kubepods/bursta+ stress-ng-cpu [run]
1157937 root      20   0   66216   1536    512 R  50.3   0.0   0:48.62  4  0 systemd:/k8s-infra/kubepods/bursta+ stress-ng-cpu [run]
1158138 root      20   0   66216   1536    512 R  50.3   0.0   0:48.34 36  0 systemd:/k8s-infra/kubepods/bursta+ stress-ng-cpu [run]
1158444 root      20   0   66408    512    512 R  50.3   0.0   0:48.04  5  0 systemd:/k8s-infra/kubepods/bursta+ stress-ng-matrix [run]
1158869 root      20   0   66216   1536    512 R  50.3   0.0   0:47.66 37  0 systemd:/k8s-infra/kubepods/bursta+ stress-ng-cpu [run]
1159011 root      20   0   66216   1536    512 R  50.3   0.0   0:47.45  6  0 systemd:/k8s-infra/kubepods/bursta+ stress-ng-cpu [run]
1159179 root      20   0   66216   1536    512 R  50.3   0.0   0:47.15 38  0 systemd:/k8s-infra/kubepods/bursta+ stress-ng-cpu [run]
1159318 root      20   0   66216   1536    512 R  50.3   0.0   0:46.99  7  0 systemd:/k8s-infra/kubepods/bursta+ stress-ng-cpu [run]
1159842 root      20   0   66216   1536    512 R  50.3   0.0   0:46.41 39  0 systemd:/k8s-infra/kubepods/bursta+ stress-ng-cpu [run]
1159844 root      20   0   66408    512    512 R  50.3   0.0   0:46.41 39  0 systemd:/k8s-infra/kubepods/bursta+ stress-ng-matrix [run]
1159925 root      20   0   66216   1536    512 R  50.3   0.0   0:46.32  8  0 systemd:/k8s-infra/kubepods/bursta+ stress-ng-cpu [run]
```

## Load is running
## Now will check the fans to see if they are triggered.

```log

root@controller-0:/var/home/XXXXXX/stressng-fans# ipmitool sensor | grep -e CPU_0_TEMP -e CPU0_Power -e FAN -e CPU_CUPS
CPU_0_TEMP       | 74.000     | degrees C  | ok    | na        | na        | na        | 96.000    | 98.000    | na
CPU0_Power       | 184.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 6250.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1B       | 6750.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_2A       | 6250.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_2B       | 6750.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1A_PWM   | 23.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1B_PWM   | 23.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_2A_PWM   | 23.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_2B_PWM   | 23.000     | percent    | ok    | na        | na        | na        | na        | na        | na
CPU_CUPS         | 80.000     | percent    | ok    | na        | na        | na        | na        | 100.000   | na
PSU_1_FAN        | 4160.000   | RPM        | ok    | 800.000   | 1120.000  | na        | na        | na        | na
PSU_2_FAN        | 4000.000   | RPM        | ok    | 800.000   | 1120.000  | na        | na        | na        | na
root@controller-0:/var/home/XXXXXX/stressng-fans#
root@controller-0:/var/home/XXXXXX/stressng-fans# ipmitool sensor | grep -e CPU_0_TEMP -e CPU0_Power -e FAN -e CPU_CUPS
CPU_0_TEMP       | 75.000     | degrees C  | ok    | na        | na        | na        | 96.000    | 98.000    | na
CPU0_Power       | 184.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 6250.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1B       | 6750.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_2A       | 6250.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_2B       | 6750.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1A_PWM   | 23.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1B_PWM   | 23.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_2A_PWM   | 23.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_2B_PWM   | 23.000     | percent    | ok    | na        | na        | na        | na        | na        | na
CPU_CUPS         | 79.000     | percent    | ok    | na        | na        | na        | na        | 100.000   | na
PSU_1_FAN        | 4160.000   | RPM        | ok    | 800.000   | 1120.000  | na        | na        | na        | na
PSU_2_FAN        | 4000.000   | RPM        | ok    | 800.000   | 1120.000  | na        | na        | na        | na
root@controller-0:/var/home/XXXXXX/stressng-fans#
root@controller-0:/var/home/XXXXXX/stressng-fans# ipmitool sensor | grep -e CPU_0_TEMP -e CPU0_Power -e FAN -e CPU_CUPS
CPU_0_TEMP       | 75.000     | degrees C  | ok    | na        | na        | na        | 96.000    | 98.000    | na
CPU0_Power       | 184.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 6125.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1B       | 6750.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_2A       | 6125.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_2B       | 6750.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1A_PWM   | 23.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1B_PWM   | 23.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_2A_PWM   | 23.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_2B_PWM   | 23.000     | percent    | ok    | na        | na        | na        | na        | na        | na
CPU_CUPS         | 80.000     | percent    | ok    | na        | na        | na        | na        | 100.000   | na
PSU_1_FAN        | 4160.000   | RPM        | ok    | 800.000   | 1120.000  | na        | na        | na        | na
PSU_2_FAN        | 4000.000   | RPM        | ok    | 800.000   | 1120.000  | na        | na        | na        | na
root@controller-0:/var/home/XXXXXX/stressng-fans#
root@controller-0:/var/home/XXXXXX/stressng-fans# ipmitool sensor | grep -e CPU_0_TEMP -e CPU0_Power -e FAN -e CPU_CUPS
CPU_0_TEMP       | 77.000     | degrees C  | ok    | na        | na        | na        | 96.000    | 98.000    | na
CPU0_Power       | 171.000    | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 6125.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1B       | 6750.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_2A       | 6125.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_2B       | 6750.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1A_PWM   | 21.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1B_PWM   | 21.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_2A_PWM   | 21.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_2B_PWM   | 21.000     | percent    | ok    | na        | na        | na        | na        | na        | na
CPU_CUPS         | 78.000     | percent    | ok    | na        | na        | na        | na        | 100.000   | na
PSU_1_FAN        | 4000.000   | RPM        | ok    | 800.000   | 1120.000  | na        | na        | na        | na
PSU_2_FAN        | 3840.000   | RPM        | ok    | 800.000   | 1120.000  | na        | na        | na        | na
root@controller-0:/var/home/XXXXXX/stressng-fans# ipmitool sensor | grep -e CPU_0_TEMP -e CPU0_Power -e FAN -e CPU_CUPS
CPU_0_TEMP       | 70.000     | degrees C  | ok    | na        | na        | na        | 96.000    | 98.000    | na
CPU0_Power       | 99.000     | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 5000.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1B       | 5625.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_2A       | 5000.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_2B       | 5500.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1A_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1B_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_2A_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_2B_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
CPU_CUPS         | 50.000     | percent    | ok    | na        | na        | na        | na        | 100.000   | na
PSU_1_FAN        | 4000.000   | RPM        | ok    | 800.000   | 1120.000  | na        | na        | na        | na
PSU_2_FAN        | 3840.000   | RPM        | ok    | 800.000   | 1120.000  | na        | na        | na        | na
root@controller-0:/var/home/XXXXXX/stressng-fans# ipmitool sensor | grep -e CPU_0_TEMP -e CPU0_Power -e FAN -e CPU_CUPS
CPU_0_TEMP       | 61.000     | degrees C  | ok    | na        | na        | na        | 96.000    | 98.000    | na
CPU0_Power       | 72.000     | Watts      | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1A       | 5000.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1B       | 5500.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_2A       | 5000.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_2B       | 5500.000   | RPM        | ok    | na        | 1000.000  | na        | na        | 28500.000 | na
SYS_FAN_1A_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_1B_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_2A_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
SYS_FAN_2B_PWM   | 18.000     | percent    | ok    | na        | na        | na        | na        | na        | na
CPU_CUPS         | 3.000      | percent    | ok    | na        | na        | na        | na        | 100.000   | na
PSU_1_FAN        | 4000.000   | RPM        | ok    | 800.000   | 1120.000  | na        | na        | na        | na
PSU_2_FAN        | 4000.000   | RPM        | ok    | 800.000   | 1120.000  | na        | na        | na        | na
root@controller-0:/var/home/XXXXXX/stressng-fans#
```

## Fans increased in RPM as the CPU temp has risen, success passed test
## you can see the cpu temps going down, and then the fan rpms, this was due to the load coming to an end with the pods.


## clean up test by removing all the PODS for the fan test

```log
[XXXXXX@controller-0 stressng-fans(keystone_admin)]$ kubectl delete pods --all -n default
pod "stressng-fan-james1" deleted
pod "stressng-fan-james10" deleted
pod "stressng-fan-james11" deleted
pod "stressng-fan-james12" deleted
pod "stressng-fan-james13" deleted
pod "stressng-fan-james14" deleted
pod "stressng-fan-james15" deleted
pod "stressng-fan-james16" deleted
pod "stressng-fan-james17" deleted
pod "stressng-fan-james18" deleted
pod "stressng-fan-james19" deleted
pod "stressng-fan-james2" deleted
pod "stressng-fan-james20" deleted
pod "stressng-fan-james21" deleted
pod "stressng-fan-james22" deleted
pod "stressng-fan-james23" deleted
pod "stressng-fan-james24" deleted
pod "stressng-fan-james25" deleted
pod "stressng-fan-james26" deleted
pod "stressng-fan-james27" deleted
pod "stressng-fan-james28" deleted
pod "stressng-fan-james29" deleted
pod "stressng-fan-james3" deleted
pod "stressng-fan-james30" deleted
pod "stressng-fan-james31" deleted
pod "stressng-fan-james32" deleted
pod "stressng-fan-james33" deleted
pod "stressng-fan-james34" deleted
pod "stressng-fan-james35" deleted
pod "stressng-fan-james36" deleted
pod "stressng-fan-james37" deleted
pod "stressng-fan-james38" deleted
pod "stressng-fan-james39" deleted
pod "stressng-fan-james4" deleted
pod "stressng-fan-james40" deleted
pod "stressng-fan-james41" deleted
pod "stressng-fan-james42" deleted
pod "stressng-fan-james43" deleted
pod "stressng-fan-james44" deleted
pod "stressng-fan-james45" deleted
pod "stressng-fan-james46" deleted
pod "stressng-fan-james47" deleted
pod "stressng-fan-james48" deleted
pod "stressng-fan-james49" deleted
pod "stressng-fan-james5" deleted
pod "stressng-fan-james50" deleted
pod "stressng-fan-james51" deleted
pod "stressng-fan-james52" deleted
pod "stressng-fan-james53" deleted
pod "stressng-fan-james54" deleted
pod "stressng-fan-james55" deleted
pod "stressng-fan-james56" deleted
pod "stressng-fan-james6" deleted
pod "stressng-fan-james7" deleted
pod "stressng-fan-james8" deleted
pod "stressng-fan-james9" deleted
[XXXXXX@controller-0 stressng-fans(keystone_admin)]$

```