# Request Management API deployment notes

The legacy OpenShift template deployment flow is discontinued. Maintain runtime
configuration in the [FOI Flow GitOps chart](https://github.com/bcgov-c/tenant-gitops-d7abee/tree/main/foi-flow)
and its environment values; Argo CD reconciles those resources to OpenShift.

Application images are built by the [dynamic image-build workflow](../../../.github/workflows/ci-build-images.yaml).
The [CD workflow](../../../.github/workflows/cd-auto-deploy.yaml) updates GitOps
values for dev/test after eligible PR merges. Production promotion follows the
DevOps release process; this workflow does not automatically promote to prod.
Do not use the old template-processing or manual image-tag deployment commands.

## Retained configuration references

- `request-management-api-config.example.env` documents historical template
  parameters. Review their current equivalents in GitOps rather than passing this
  file to a deployment template.
- `request-management-secrets.example.env` is a reference for Secret provisioning.
  Confirm the Secret name and required keys against the target environment's
  GitOps values and the maintained provisioning procedure. Example files may
  differ from the currently deployed configuration.

GitOps references existing Secrets; the chart does not create them. Secret
provisioning remains a separate prerequisite. Keep actual environment files and
credentials outside version control.

For an authorized initial Secret creation, prepare an environment file securely
and substitute the namespace, Secret name, and file path confirmed for the target
environment:

```bash
oc -n <namespace> create secret generic <secret-name> --from-env-file=<secure-env-file>
```

This is a provisioning example, not a routine deployment step. Use the owning
team's procedure for existing Secret updates.

## Test Submit

```bash

curl --header "Content-Type: application/json" \
  --request POST \
  --data  '{"requestData":{"requestType":{"requestType":"personal"},"choose-idenity":{"answerYes":null},"selectAbout":{"yourself":true,"child":null,"another":null},"ministry":{"selectedMinistry":[{"code":"EMBC","name":"Emergency Management BC","selected":true},{"code":"EMPR","name":"Energy, Mines and Low Carbon Innovation (and Minister Responsible for the Consular Corps of British Columbia)","selected":true}],"ministryPage":"/personal/ministry-confirmation","defaultMinistry":{}},"contactInfo":{"firstName":"DV","middleName":null,"lastName":"DV","alsoKnownAs":null,"businessName":null,"birthDate":"2001-12-12T05:00:00.000Z"},"requestTopic":{"value":"anotherTopic","text":"Other","ministryCode":null},"descriptionTimeframe":{"description":"test personal","fromDate":"2021-06-01T04:00:00.000Z","toDate":"2021-06-06T04:00:00.000Z","correctionalServiceNumber":null,"publicServiceEmployeeNumber":null,"topic":"Other"},"contactInfoOptions":{"email":"test@email.com","phonePrimary":null,"phoneSecondary":null,"address":null,"city":null,"postal":null,"province":null,"country":null},"Attachments":[]}}' \
  https://request-management-api-dev.apps.silver.devops.gov.bc.ca/api/foirawrequests
```
