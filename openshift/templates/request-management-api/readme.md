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

```
oc project d7abee-dev

oc process -f openshift/templates/request-management-api/request-management-api-deploy.yaml -o yaml | oc apply -f - 
oc process -f request-management-api-deploy.yaml -o yaml | oc apply -f - 
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