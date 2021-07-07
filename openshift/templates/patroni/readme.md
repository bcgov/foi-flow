As per https://github.com/BCDevOps/platform-services/tree/master/apps/pgsql/patroni


```bash
# oc process -f build.yaml \
#  -p "GIT_URI=https://github.com/bcgov/foi-flow" \
#  -p "GIT_REF=$(git rev-parse --abbrev-ref HEAD)" \
#  -p SUFFIX=-pg11 \
#  -p OUT_VERSION=v11-latest \
#  -p PG_VERSION=11 | oc apply -f -       


# in tools
oc process -f build.yaml \
 -p "GIT_URI=https://github.com/BCDevOps/platform-services/" \
 -p "GIT_REF=master" \
 -p SUFFIX=-pg11 \
 -p OUT_VERSION=v11-latest \
 -p PG_VERSION=11 | oc apply -f -       

# switch to dev for deploys (same for test/prod/etc).
oc project d7abee-dev

oc process -f deployment-prereq.yaml \
 -p NAME=patroni \
 -p SUFFIX=-001 | oc create -f -

oc process -f deployment.yaml \
 -p NAME=patroni \
 -p "IMAGE_STREAM_NAMESPACE=d7abee-tools" \
 -p "IMAGE_STREAM_TAG=patroni:v11-latest" \
 -p REPLICAS=3 \
 -p SUFFIX=-001 | oc apply -f -
 

```


should be able to pull from dev/test, why error?  check namespace names/strings are correct.

        Failed to pull image "image-registry.openshift-image-registry.svc:5000/d7abee-tools/patroni:v11-latest": rpc error: code = Unknown desc = Error reading manifest v11-latest in image-registry.openshift-image-registry.svc:5000/d7abee-tools/patroni: unauthorized: authentication required