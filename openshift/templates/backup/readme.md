# Readme - Backup Container

All original commands were found in official [backup-container](https://github.com/BCDevOps/backup-container) repo.

No passwords or secrets are stored in this file as it's publicly available.

## Commands


oc -n d7abee-tools process -f ./openshift/templates/backup/backup-build.yaml \
  -p NAME=foi-bkup OUTPUT_IMAGE_TAG=v1 | oc -n d7abee-tools create -f -


oc -n d7abee-prod create configmap backup-conf --from-file=./openshift/templates/backup/backup.conf
oc -n d7abee-prod label configmap backup-conf app=foi-bkup

oc -n d7abee-prod process -f ./openshift/templates/backup/backup-deploy.yaml \
  -p NAME=foi-bkup \
  -p IMAGE_NAMESPACE=d7abee-tools \
  -p SOURCE_IMAGE_NAME=foi-bkup \
  -p TAG_NAME=v1 \
  -p BACKUP_VOLUME_NAME=foi-bkup-pvc -p BACKUP_VOLUME_SIZE=20Gi \
  -p VERIFICATION_VOLUME_SIZE=5Gi \
  -p ENVIRONMENT_NAME=d7abee-prod \
  -p DATABASE_DEPLOYMENT_NAME=patroni-001 \
  -p DATABASE_USER_KEY_NAME=app-db-username \
  -p DATABASE_PASSWORD_KEY_NAME=app-db-password \
  -p ENVIRONMENT_FRIENDLY_NAME='FOI DB Backups' | oc -n d7abee-prod create -f -