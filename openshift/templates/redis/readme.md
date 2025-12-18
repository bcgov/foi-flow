As per https://gist.github.com/jujaga/7048148a7c960d6a910ff29f33565407

FOI uses redis as caching and message broker.

```bash
  


# switch to dev for deploys (same for test/prod/etc).
oc project d7abee-dev

oc process -n d7abee-dev -f redis.secret.yaml -p INSTANCE=foi-cache -p CLUSTER_MODE=no | oc create -n d7abee-dev -f –
oc process -n d7abee-dev -f redis-cluster.dc.yaml -p INSTANCE=foi-cache -p APP_NAME=redis| oc apply -n d7abee-dev -f –


oc process -n d7abee-dev -f redis.secret.yaml -p INSTANCE=foi-msgbroker -p CLUSTER_MODE=yes | oc create -n d7abee-dev -f –
oc process -n d7abee-dev -f redis-cluster.dc.yaml -p INSTANCE=foi-msgbroker -p APP_NAME=redis| oc apply -n d7abee-dev -f –



```

