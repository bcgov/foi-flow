# synckeycloakusers

This is a cronjob to call an endpoint in request management api to sync keycloak user groups

## To manually trigger a job

```
kubectl create job --from=cronjob/synckeycloakusers <name of job>
```

