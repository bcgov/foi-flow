###Current Version : 4.0.5-alpha

####How to Build
1. Navigate to project's tools space.
2. Execute the below given command.

##### For example, xxx refers to project space.
```bash
# in tools
oc process -f api_bc.yaml | oc -n xxxx-tools apply -f -

```

####How to Deploy

1. Navigate to  project's profile(dev/test/prod) space.
2. Execute the below given command.

```bash
# in {profile}
oc process -f webapi_dc.yaml --param-file=webapi_param-dev.yaml | oc -n xxx-dev create -f -

```


