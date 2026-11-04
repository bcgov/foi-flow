# Legacy OpenShift configuration — discontinued deployment flow

The legacy application deployment flow using the OpenShift templates in this
directory is discontinued for services migrated to **Argo CD**.

Maintain deployment configuration for those services in the
[tenant-gitops-d7abee repository](https://github.com/bcgov-c/tenant-gitops-d7abee/tree/main/foi-flow),
using its Helm chart and environment values. Argo CD reconciles that configuration
to OpenShift. Application image builds and GitOps updates are handled by the
repository's [GitHub Actions workflows](../.github/workflows/) and
[service catalog](../.github/configuration/service-catalog.yaml).

Do not use the legacy deployment templates to deploy or update migrated services.
Their historical deployment commands are superseded by the GitOps flow.

Some files remain because their replacements have not been confirmed, including
infrastructure and prerequisite resources such as Secrets, ConfigMaps, and PVCs,
as well as build definitions and backup application source. Their presence does
not mean they are all managed by Argo CD or ready for deletion.

## Retained configuration

| Area | Reason retained |
| --- | --- |
| Request Management API examples | Configuration and Secret provisioning references; see the [API deployment notes](templates/request-management-api/readme.md). |
| Notification manager Secrets | GitOps references the Secret but does not provision it. |
| Template API PVC | The GitOps Deployment mounts `app-data-pvc` but does not provision it. |
| BPM | The deployment template also provisions the mail ConfigMap; the build definition is still used by the BPM workflow. |
| Backups | Mixed templates contain PVCs, Secrets, and a NetworkPolicy. `backup.conf` supplies configuration, and `backup/copy-to-s3/` contains application source used as an image build context. |
| AXIS page sync | No replacement job was identified in this tenant chart. |
| AI web, Form.io, and forms-flow-api | Not established as migrated by this tenant chart; AI web has a separate build/deployment workflow. |
| Shared Secrets, network policies, MongoDB, Patroni, and Redis | No provisioning replacement was identified in this tenant chart. Redis Insight does not replace Redis itself. |

Templates containing both migrated workloads and retained prerequisites require
review before use. Establish a maintained source for the remaining prerequisites
before removing those templates. The S3 backup job also requires separate review
of its schedule and environment coverage before retiring its legacy template.

## Manually trigger Keycloak user sync

The `synckeycloakusers` CronJob definition is maintained in GitOps. When an
authorized operator needs an additional run, use an existing CronJob in the
intended namespace and a unique Job name:

Before an additional test-environment run, have the GitOps owner remove the
command's literal client credential and credential echo, and use the declared
Secret reference instead. These are pre-existing GitOps issues requiring
remediation in that repository; do not copy credentials into commands or logs.

```bash
oc -n <namespace> create job --from=cronjob/synckeycloakusers <unique-job-name>
```

This starts a real job that refreshes Keycloak user groups; it is an operational
procedure, not a deployment verification step.

## Cleanup verification (FOIMOD-5484)

The legacy API, notification manager, and template API build/deployment templates,
notification deployment parameters, and restart/Keycloak-sync job definitions
were removed from this repository. Runtime counterparts render from the GitOps
chart, and the three application images are covered by GitHub Actions builds.

The repository comparison used GitOps revision
`af0c85645ce53fbc9990ace5f4352477bc3c1ea5` on 2026-11-04. Dev, test, and prod
rendered successfully. Production uses `request-management-api-002`; dev/test
use `request-management-api`.

Live Argo CD Application sources, values-file ordering, ownership, health/sync
status, and production promotion still require DevOps verification before merge:
the OpenShift session available during cleanup returned `Unauthorized`. Retained
prerequisite resources also need their provisioning owners confirmed. Removing
these repository files does not delete cluster resources or change GitOps values.

The deleted jobs have the following chart counterparts in all three environments:

| Job | Target | Schedule and timezone | Suspended | Credentials and operational ownership |
| --- | --- | --- | --- | --- |
| `synckeycloakusers` | Request Management API `/api/foiuser/refresh` in the environment | `0 13 * * *`, `America/Vancouver` | `false` | Declares `request-management-api-002` Secret, key `KEYCLOAK_ADMIN_CLIENT_SECRET`; test command needs the remediation above. Operator ownership requires confirmation. |
| `restart-pods` | Notification manager workload; no HTTP endpoint | `0 3 * * *`, `America/Vancouver` | `false` | Uses the namespace's default ServiceAccount; confirm its RBAC and operational owner. |

Before merge, confirm that Keycloak sync's explicit `America/Vancouver` timezone
is intentional: the legacy manifest did not specify a timezone. For the restart
job, the chart changes patch targets from a DeploymentConfig to a Deployment but
retains `oc rollout latest notification-manager`; have the GitOps owner verify
that command against the intended workload. Matching job names and schedule text
alone do not establish operational equivalence.
