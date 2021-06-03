# Request Management API Openshift Documentation

### API Build

```bash
# Deploy build to tools
oc process -f openshift/templates/request-management-api/request-management-api-build.yaml -o yaml | oc apply -f - -n d7abee-tools

# OPTIONAL - Change deployment branch, commit, tag, etc. 
# Safe to run this even if already deployed, as it's using `apply` not `create
# Just need to trigger new build after the apply command
oc process -f openshift/templates/request-management-api/request-management-api-build.yaml -o yaml \
    -p GIT_REF=fix/adjudication-build \
| oc apply -f - -n d7abee-tools

# Reverts back  to default branch (main)
oc process -f adjudication/build -o yaml | oc apply -f - -n d7abee-tools
```