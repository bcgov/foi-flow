# Patroni Upgrade

This file documents how to upgrade patroni from version 1.6.5 to 2.0.1.  This is required for compatability with OpenShift platform upgrades.


## Commands

```bash
# BUILD ====================
oc project ****-tools
# This command is same as adding yaml above.
oc patch bc/patroni-pg11 -p '{"spec":{"strategy":{"dockerStrategy":{"buildArgs":[{"name":"patroniv","value": "2.0.1"}]}}}}'
# Watch logs for "(from patroni[kubernetes]==2.0.1)", around 70% down of build. Maybe even CTRL+F in your terminal
oc start-build patroni-pg11 --follow

# DEPLOY ===================

oc project ****-dev
oc rollout restart statefulset patroni-001
```

## BuildConfig yaml Change

Note: This is done in an `oc patch` command, and is just shown here for illustrative purposes.

```yaml
spec:
    strategy:
        dockerStrategy:
            from:
                kind: ImageStreamTag
                name: postgres:{{ postgres_version }}
            buildArgs:
                - name: "patroniv"
                  value: 2.0.1
```

## References

Main Documentation followed: https://github.com/BCDevOps/openshift-wiki/blob/master/docs/HowTo/UpdatePatroni.md (esp Step #3)