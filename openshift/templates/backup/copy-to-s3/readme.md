# Readme

This file is responsible for uploading files from `backup-container` to Object Storage.

# Setup

```bash
# Local dev setup 
source backup-copy/bin/activate

```


## Pre-requisite for OpenShift: Backup-container pvc

The backup-container pvc, normally called "foi-bkup-pvc" is by default a Read-Write-One PVC.  This won't work for us, we need ReadWriteMany.

So:

1. Create a new PVC called "foi-bkup-shared-pvc"
2. Change backup-container to use new PVC. 
3. Optionally: delete old PVC

This copy-to-s3 script is configured to use `foi-bkup-shared-pvc`, but if you use something different just change `deploy-job.yaml`

## Deploy to OpenShift

```bash
# in tools
oc process -f build-job.yaml -o yaml | oc apply -f -
oc start-build backup-to-s3-build

# in dev
# upload env file as params
# then upload job yaml

oc process -f deploy-job.yaml --param-file=.env -o yaml

oc process -f deploy-job.yaml --param-file=.env -o yaml | oc apply -f -
```


## Trigger the cronjob manually

Want to just trigger the cronjob manually? This can be useful while developing (i.e. you don't want to wait until schedule to verify it works), or if you want to just trigger a backup.

```bash

# TODO VERIFY IT WORKS
oc create job --from=cronjob/<cronjob-name> <job-name> -n <namespace-name>
oc create job --from=cronjob/backup-to-s3 s3-job-manual


```
