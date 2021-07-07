# foi-requests

This is for the foi requests angular app.

## Modify on submit email

```
oc process -f openshift/templates/foi-request/secrets.yaml --param-file=openshift/templates/foi-request/env.properties -o yaml | oc apply -f - 
```

To change recipient email address, first modify env.properties, then re-run above command.  After, you must manually re-trigger a deploy.

## Deploying a Build to Test

```
oc -n 04d1a3-tools tag api:latest api:test
```

