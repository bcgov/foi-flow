# Github Actions Readme

## Documentation

https://github.com/redhat-actions/oc-login/wiki/Using-a-Service-Account-for-GitHub-Actions

https://docs.openshift.com/container-platform/4.4/authentication/understanding-and-creating-service-accounts.html


## Grant permissions to monitor deploys

        oc policy add-role-to-user view system:serviceaccount:NAMESPACE-tools:github-actions-sa