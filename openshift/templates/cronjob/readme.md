# synckeycloakusers

This is a cronjob to call an endpoint in request management api to sync keycloak user groups

## To create cronjob

Replace the env values with the proper values depending on which namespace you are in
Login to oc 
Run the following command

```
kubectl create -f <path to file>/synckeycloakusers.yaml
```

## To manually trigger a job

```
kubectl create job --from=cronjob/synckeycloakusers <name of job>
```

