# Readme

This file is responsible for uploading files from `backup-container` to Object Storage.

# Setup

```bash
# Local dev setup 
source backup-copy/bin/activate

```

## Deploy to OpenShift

```bash
# in tools
oc process -f build-job.yaml -o yaml | oc apply -f -
oc start-build backup-to-s3-build

# in dev
# upload env file as params
# then upload job yaml

oc process -f deploy-job.yaml --param-file=.env -o yaml
```


## Trigger the cronjob manually

Want to just trigger the cronjob manually? This can be useful while developing (i.e. you don't want to wait until schedule to verify it works), or if you want to just trigger a backup.

```bash

# TODO VERIFY IT WORKS
oc create job --from=cronjob/<cronjob-name> <job-name> -n <namespace-name>
oc create job --from=cronjob/backup-to-s3 s3-job-manual


```