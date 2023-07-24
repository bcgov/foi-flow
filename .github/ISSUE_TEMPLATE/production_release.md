---
name: Production Release
about: Capture the activities associated with FOI release.
title: ''
labels: Production Release
assignees: ''

---

**Place-in the release name**
Release name & link

#### Activity start time
Summarize issue 

#### Activity end time
Summarize issue 

#### Step-1: Database Backup (Check the desired components)
Capture the backup details 
- [ ] FOI DB (xxx)
- [ ] BPM DB
- [ ] Docreviewer DB

#### Step-2: Image Backup (Check the desired components)
Capture the image details 
- [ ] request-management-api (yyy)
- [ ] forms-flow-web
- [ ] notification-manager
- [ ] reviewer-api
- [ ] reviewer-web
- [ ] reviewer-conversion
- [ ] reviewer-conversion-largefiles
- [ ] reviewer-dedupe
- [ ] reviewer-dedupe-largefiles
- [ ] reviewer-pdfstitch
- [ ] reviewer-pdfstitch-largefiles

#### Step-3: Production - Tagging of image (Check the desired components)
- [ ] request-management-api
- [ ] forms-flow-web
- [ ] notification-manager
- [ ] reviewer-api
- [ ] reviewer-web
- [ ] reviewer-conversion
- [ ] reviewer-conversion-largefiles
- [ ] reviewer-dedupe
- [ ] reviewer-dedupe-largefiles
- [ ] reviewer-pdfstitch
- [ ] reviewer-pdfstitch-largefiles

#### Step-4: Signoff from business
- [ ] Yes
- [ ] No
- [ ] Not Applicable

#### Step-5: Healthcheck (Check the desired components)
- [ ] FOI DB
- [ ] BPM DB
- [ ] Docreviewer DB
- [ ] redis-
- [ ] redis-
- [ ] redis-
- [ ] request-management-api
- [ ] forms-flow-web
- [ ] notification-manager
- [ ] reviewer-api
- [ ] reviewer-web
- [ ] reviewer-conversion
- [ ] reviewer-conversion-largefiles
- [ ] reviewer-dedupe
- [ ] reviewer-dedupe-largefiles
- [ ] reviewer-pdfstitch
- [ ] reviewer-pdfstitch-largefiles

#### Step-6: Staging - Tagging of image (Check the desired components)
- [ ] request-management-api
- [ ] forms-flow-web
- [ ] notification-manager
- [ ] reviewer-api
- [ ] reviewer-web
- [ ] reviewer-conversion
- [ ] reviewer-conversion-largefiles
- [ ] reviewer-dedupe
- [ ] reviewer-dedupe-largefiles
- [ ] reviewer-pdfstitch
- [ ] reviewer-pdfstitch-largefiles

**Observations**
List down the observations of incidents which happened in release window

**Overall Rating**
- [ ] Good (No change)
- [ ] OK (With observations)
- [ ] Bad(Rollback)