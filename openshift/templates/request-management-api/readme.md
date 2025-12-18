# Request Management API Openshift Documentation

### API Build



```bash

# IMPORTANT, SET PROJECT TO TOOLS
oc project d7abee-tools
# Deploy build to tools
oc process -f openshift/templates/request-management-api/request-management-api-build.yaml -o yaml | oc apply -f - 


# OPTIONAL - Change deployment branch, commit, tag, etc. 
# Safe to run this even if already deployed, as it's using `apply` not `create
# Just need to trigger new build after the apply command
# oc process -f openshift/templates/request-management-api/request-management-api-build.yaml -o yaml \
#     -p GIT_REF=fix/adjudication-build \
# | oc apply -f - -n d7abee-tools

# # Reverts back  to default branch (main)
# oc process -f adjudication/build -o yaml | oc apply -f - -n d7abee-tools
```


## API Deploy

There are two associated environment files you will need for a deploy.  Assuming deploying in dev:

1. `request-management-secrets.dev.env` - contains all secrets
2. `request-management-api-config.dev.env` - contains non-secret environment configuration variables

The secret file is **not** included as it contains sensitive information.  An example file exists you can use to recreate, or other developers on the project may be able to provide you dev env vars as appropriate.

```bash
# The env
oc create secret generic request-management-api-002 --from-env-file=openshift/templates/request-management-api/request-management-secrets.dev.env

# Make sure `REQUEST_MANAGEMENT_SECRETS` in the config env matches the name of the secret created in previous step.
oc process -n d7abee-dev -f openshift/templates/request-management-api/request-management-api-deploy.yaml --param-file=openshift/templates/request-management-api/request-management-api-config.dev.env -o yaml | oc -n d7abee-dev create -f - --dry-run
```

## Test Submit

```bash

curl --header "Content-Type: application/json" \
  --request POST \
  --data  '{"requestData":{"requestType":{"requestType":"personal"},"choose-idenity":{"answerYes":null},"selectAbout":{"yourself":true,"child":null,"another":null},"ministry":{"selectedMinistry":[{"code":"EMBC","name":"Emergency Management BC","selected":true},{"code":"EMPR","name":"Energy, Mines and Low Carbon Innovation (and Minister Responsible for the Consular Corps of British Columbia)","selected":true}],"ministryPage":"/personal/ministry-confirmation","defaultMinistry":{}},"contactInfo":{"firstName":"DV","middleName":null,"lastName":"DV","alsoKnownAs":null,"businessName":null,"birthDate":"2001-12-12T05:00:00.000Z"},"requestTopic":{"value":"anotherTopic","text":"Other","ministryCode":null},"descriptionTimeframe":{"description":"test personal","fromDate":"2021-06-01T04:00:00.000Z","toDate":"2021-06-06T04:00:00.000Z","correctionalServiceNumber":null,"publicServiceEmployeeNumber":null,"topic":"Other"},"contactInfoOptions":{"email":"test@email.com","phonePrimary":null,"phoneSecondary":null,"address":null,"city":null,"postal":null,"province":null,"country":null},"Attachments":[]}}' \
  https://request-management-api-dev.apps.silver.devops.gov.bc.ca/api/foirawrequests
```

## Tag for test manually

Deploys dev build to test

```
oc -n d7abee-tools tag request-management-api:dev request-management-api:test
```






