# FOIMOD-4864 — Remove AXIS Sync: Technical Investigation

**Ticket:** FOIMOD-4864  
**Date:** 2026-03-25  
**Deadline:** April 1, 2026  
**Priority:** Critical — data integrity risk  

---

## 1. Problem Summary

### Context

The FOI Modernization system currently integrates with the AXIS external system for request synchronization. **Access to AXIS will be lost on April 1st, 2026.** After that date, any sync operation will either fail silently, timeout, or—in the worst case—overwrite valid local data with stale or empty AXIS responses.

### Risks of Keeping AXIS Sync Active After Access Is Lost

| Risk | Severity | Likelihood |
|------|----------|------------|
| **Data rollback**: Sync overwrites current local request data with outdated AXIS state | 🔴 Critical | High |
| **Partial updates**: Sync fails mid-write, leaving request in inconsistent state | 🔴 Critical | Medium |
| **Timeouts / errors**: Users encounter confusing error messages when sync fails | 🟡 Medium | Certain |
| **Silent failure**: Backend swallows exceptions, user unaware sync failed | 🟡 Medium | High |
| **Extension data loss**: AXIS extension sync deletes FOI-only extensions not in AXIS | 🔴 Critical | Medium |

### Impact of Incorrect Rollbacks

The most dangerous scenario is the **data rollback**: when AXIS becomes unreachable or returns stale data, the sync logic in `AxisSyncModal` compares AXIS data with local data and offers to overwrite **30+ fields** including:

- Applicant details (name, contact info, address)
- Request dates (due date, received date, CFR due date, start date)  
- Request type, description, delivery/received mode
- Extensions (can **delete** locally-created extensions)
- Linked requests
- Page counts
- Subject code

If AXIS returns cached/stale data (or empty responses from a failing service), the system could silently roll back months of local updates to an outdated AXIS snapshot.

---

## 2. Current Integration Flow

### Architecture Overview

```
┌──────────────────┐     HTTPS GET        ┌──────────────────────────────────┐
│  forms-flow-web  │ ──────────────────▶  │  flowaxisapidev.gov.bc.ca       │
│  (React FE)      │  /api/RequestSearch/ │  (AXIS External Integration API) │
│                  │  ◀──────────────────  │                                  │
└──────────────────┘     JSON response    └──────────────────────────────────┘
         │                                              ▲
         │  Save request                                │ HTTPS POST
         ▼                                              │ /api/requestspagecount
┌──────────────────┐                           ┌────────┴─────────┐
│  request-        │                           │  axissyncservice  │
│  management-api  │ ◀──── CronJob ──────────▶ │  (Python backend) │
│  (Flask backend) │      POST foiaxis/        │                   │
│                  │      sync/pageinfo        └───────────────────┘
└──────────────────┘
         │
         ▼
┌──────────────────┐
│  PostgreSQL      │
│  (FOIDB)         │
└──────────────────┘
```

### Sync Trigger Points

There are **three distinct sync trigger points**:

#### 1. User-Initiated Sync (FE → AXIS Direct)

**Trigger:** "Sync with AXIS" button in `BottomButtonGroup`

**Flow:**
1. When a request with an `axisRequestId` loads, `FOIRequest.js` calls `axisBannerCheck()`
2. `axisBannerCheck()` dispatches `fetchRequestDataFromAxis()` which calls `AXIS_API_URL/api/RequestSearch/{axisRequestId}`
3. FE compares the AXIS response fields with local request data
4. If differences found → shows `AxisMessageBanner` with "WARNING" message
5. User clicks "Sync with AXIS" → opens `AxisSyncModal`
6. User clicks "Save Changes" → overwrites local data with AXIS data via `saveRequestDetails()`

**Components involved:**
- [FOIRequest.js](file:///home/alvesfc/workspace/bcgov/foi-modernization/foi-flow/forms-flow-web/src/components/FOI/FOIRequest/FOIRequest.js) — `axisBannerCheck()`, `checkIfAxisDataUpdated()`
- [BottomButtonGroup/index.js](file:///home/alvesfc/workspace/bcgov/foi-modernization/foi-flow/forms-flow-web/src/components/FOI/FOIRequest/BottomButtonGroup/index.js) — "Sync with AXIS" button (line 501-510)
- [AxisSyncModal.js](file:///home/alvesfc/workspace/bcgov/foi-modernization/foi-flow/forms-flow-web/src/components/FOI/FOIRequest/AxisDetails/AxisSyncModal.js) — comparison, save, extension sync
- [AxisMessageBanner.js](file:///home/alvesfc/workspace/bcgov/foi-modernization/foi-flow/forms-flow-web/src/components/FOI/FOIRequest/AxisDetails/AxisMessageBanner.js) — warning, error, unauthorized banners
- [foiRequestServices.js](file:///home/alvesfc/workspace/bcgov/foi-modernization/foi-flow/forms-flow-web/src/apiManager/services/FOI/foiRequestServices.js) — `fetchRequestDataFromAxis()`, `checkDuplicateAndFetchRequestDataFromAxis()`

#### 2. New Request AXIS ID Validation (FE → AXIS Direct)

**Trigger:** User enters an AXIS ID in the `AxisDetails` component during request creation

**Flow:**
1. User types AXIS ID in the `AxisDetails` text field
2. `checkDuplicateAndFetchRequestDataFromAxis()` validates against local DB first
3. If not duplicate, calls `fetchRequestDataFromAxis()` → AXIS API
4. Response populates the new request form with AXIS data

**Components involved:**
- [AxisDetails.js](file:///home/alvesfc/workspace/bcgov/foi-modernization/foi-flow/forms-flow-web/src/components/FOI/FOIRequest/AxisDetails/AxisDetails.js) — `syncWithAxis()`, `checkDuplicatedAxisID()`

#### 3. Scheduled Page Count Sync (CronJob → Backend → AXIS)

**Trigger:** OpenShift CronJob `syncaxispagedetails` runs daily at 10:00 UTC

**Flow:**
1. CronJob calls `POST /api/foiaxis/sync/pageinfo` on `request-management-api`
2. [foiaxissync.py](file:///home/alvesfc/workspace/bcgov/foi-modernization/foi-flow/request-management-api/request_api/resources/foiaxissync.py) handles the request
3. [axissyncservice.py](file:///home/alvesfc/workspace/bcgov/foi-modernization/foi-flow/request-management-api/request_api/services/external/axissyncservice.py) iterates through program areas
4. Calls `AXIS_API_URL/api/requestspagecount` with batch of AXIS request IDs  
5. Updates `axispagecount` and `axislanpagecount` in `FOIMinistryRequests`

**Components involved:**
- [syncaxispagedetails.yaml](file:///home/alvesfc/workspace/bcgov/foi-modernization/foi-flow/openshift/templates/cronjob/syncaxispagedetails/syncaxispagedetails.yaml) — CronJob definition
- [foiaxissync.py](file:///home/alvesfc/workspace/bcgov/foi-modernization/foi-flow/request-management-api/request_api/resources/foiaxissync.py) — API endpoint
- [axissyncservice.py](file:///home/alvesfc/workspace/bcgov/foi-modernization/foi-flow/request-management-api/request_api/services/external/axissyncservice.py) — batch page count sync logic

### What Data Is Read/Written During Sync

| Data Field | Source | Destination | Sync Type |
|-----------|--------|-------------|-----------|
| Applicant info (name, contact, address) | AXIS → FE | FE → local DB | User-initiated |
| Request dates (received, due, start, CFR) | AXIS → FE | FE → local DB | User-initiated |
| Request type, description, delivery mode | AXIS → FE | FE → local DB | User-initiated |
| Extensions | AXIS → FE | FE → DB via `addAXISExtensions` | User-initiated |
| Linked requests | AXIS → FE | FE → local DB | User-initiated |
| Page counts (`axispagecount`, `axislanpagecount`) | AXIS → Backend | Backend → DB | CronJob |
| Subject code | AXIS → FE | FE → local DB | User-initiated |
| `axisSyncDate` timestamp | Generated | FE → local DB | User-initiated |
| `axisApplicantID` | AXIS → FE | FE → local DB | User-initiated |

### Configuration & Environment Variables

| Variable | Location | Purpose |
|----------|----------|---------|
| `REACT_APP_AXIS_API_URL` | FE `.env` / `window._env_` | AXIS Integration API base URL |
| `AXIS_API_URL` | Backend env | Backend AXIS API base URL (used in `axissyncservice.py`) |
| `AXIS_SYNC_BATCHSIZE` | Backend env | Batch size for page count sync (default: 250) |
| `AXISSYNC_PAGEINFO` | OpenShift secret | Request body for CronJob page sync |
| `KEYCLOAK_ADMIN_CLIENT_SECRET` | OpenShift secret | Auth for backend → AXIS calls |

---

## 3. Risk Analysis

### What Happens After April 1st If Sync Is Triggered?

#### Scenario 1: AXIS API Becomes Unreachable (Most Likely)
- **FE sync check (`axisBannerCheck`)**: `fetchRequestDataFromAxis()` will catch the error and set `axisMessage` to `"ERROR"` → banner shows "System is unable to connect with AXIS"
- **FE "Sync with AXIS" button**: Correctly disabled when `axisMessage !== "WARNING"` — so the button is already disabled if the error banner shows
- **CronJob page sync**: `axissyncservice.axis_getpageinfo()` catches exceptions and returns `{}` → prints "axis page response is empty" → **no data mutation** ✅

#### Scenario 2: AXIS Returns Stale/Cached Data (Dangerous)
- If a proxy or cache returns old data with HTTP 200:
  - FE compares it against current local data → shows "WARNING" banner
  - User clicks "Sync with AXIS" → **overwrites valid local data with stale AXIS data** 🔴
  - Extensions could be deleted if AXIS returns fewer or outdated extensions
  - Page counts could be rolled back

#### Scenario 3: AXIS Returns Partial Data or Empty Response
- `fetchRequestDataFromAxis()` checks `Object.entries(data).length > 0` — empty response is handled
- But if AXIS returns partial JSON (some fields null/empty), those empty values could **overwrite non-empty local data** 🔴

#### Scenario 4: Network Timeout During Sync Save
- User clicks "Save Changes" in `AxisSyncModal` → `saveRequestDetails()` is called
- This saves to the **local** request-management-api, not AXIS — so AXIS unavailability doesn't affect the save itself
- However, the data being saved may be incorrect if it was sourced from stale AXIS data

### Failure Mode Summary

| Failure Mode | Impact | Mitigation Available? |
|-------------|--------|----------------------|
| Connection timeout/refused | "ERROR" banner, button disabled | ✅ Existing |
| HTTP 401 (expired auth) | "UNAUTHORIZED" banner | ✅ Existing |
| Stale data with HTTP 200 | Data rollback — **CRITICAL** | ❌ None |
| Empty/partial response | Potential field overwrites | ⚠️ Partial |
| CronJob page sync failure | Swallowed — no data mutation | ✅ Safe |

### Most Dangerous Scenario: Data Rollback

> **A user opens a request. AXIS returns old cached data (with HTTP 200). The FE shows "updates available from AXIS." The user, following their usual workflow, clicks "Sync with AXIS" and "Save Changes," unknowingly rolling back the request to a months-old state.**

This is the highest-priority risk because:
1. It can happen **silently** — no error is raised
2. The **user is actively encouraged** to sync (WARNING banner)
3. It can affect **all 30+ synced fields** in a single operation
4. Extensions can be **deleted** from the local system

---

## 4. Scope Definition

### What Needs to Be Disabled

**Sync for ALL existing/active requests:**
- "Sync with AXIS" button in `BottomButtonGroup`
- `AxisSyncModal` dialog
- `AxisMessageBanner` warning/sync prompts
- Automatic `axisBannerCheck()` on request load
- CronJob `syncaxispagedetails` (daily page count sync)

### What Needs to Remain (Temporarily)

**Sync during new request creation:**
- `AxisDetails.js`'s "Sync with AXIS" functionality (used during request creation to populate initial data from AXIS)
- AXIS ID validation and duplicate checking

> [!IMPORTANT]
> Evaluate whether new request AXIS sync is still needed. If AXIS access is fully lost, this will also fail and show errors. Consider disabling this too unless confirmed that AXIS will remain partially available for new requests.

### Edge Cases

| Edge Case | Risk | Recommendation |
|-----------|------|----------------|
| Partially synced requests (sync started, user didn't save) | Low — data only persisted on "Save" | No action needed |
| Requests with `axisSyncDate` but now stale | None — historical timestamp only | No action needed |
| In-flight CronJob on April 1st | Could attempt sync during cutover | Suspend CronJob before April 1st |
| FE loaded before cutover, user clicks sync after | AXIS unavailable → ERROR banner → button disabled | ✅ Existing error handling covers this |
| Backend extensions sync via `addAXISExtensions` | Only triggered from AxisSyncModal save | Disabled if button is hidden |

---

## 5. Options for Disabling Sync

### Option A: FE-Only (Hide Button / Banner)

**Changes:**
- Remove/hide "Sync with AXIS" button in `BottomButtonGroup/index.js`
- Remove/hide `AxisMessageBanner` rendering
- Skip `axisBannerCheck()` call in `FOIRequest.js`
- Optionally remove `AxisSyncModal` rendering

**Pros:** Quick, no backend deployment needed  
**Cons:** Backend endpoints still callable via API; doesn't prevent CronJob sync  
**Risk:** ⚠️ Endpoints remain open — if any other integration or script calls them, data can still be mutated  

### Option B: Backend Enforcement (Block API Endpoint)

**Changes:**
- Return `403 Forbidden` or `503 Service Unavailable` from `/api/foiaxis/sync/pageinfo`
- Block or remove the backend AXIS API calls
- Unset/clear `AXIS_API_URL` environment variable

**Pros:** Guarantees no AXIS sync occurs regardless of FE state  
**Cons:** Requires backend deployment  

### Option C: Feature Flag / Config Toggle (Preferred)

**Changes:**
- Add env variable `AXIS_SYNC_ENABLED=false`  
- FE reads `REACT_APP_AXIS_SYNC_ENABLED` to control button/banner visibility
- Backend checks `AXIS_SYNC_ENABLED` in `axissyncservice.py` before making AXIS calls
- Can be toggled without code deployment

**Pros:** Reversible, no code deployment for toggle, defense in depth  
**Cons:** Requires initial code deployment to add the flag  

### Option D: Service-Level Disable (No Release Required)

**Changes:**
- Suspend CronJob `syncaxispagedetails` in OpenShift (`suspend: true`)
- Unset `AXIS_API_URL` and `REACT_APP_AXIS_API_URL` environment variables
- Or set them to a non-existent URL / localhost

**Pros:** No code deployment; can be done via OpenShift config/secrets  
**Cons:** FE will show "ERROR" banner (confusing to users); less clean  

---

## 6. Recommended Approach

### Strategy: Defense in Depth (FE + Backend + Infra)

Combine multiple layers to ensure no sync can occur:

```
Layer 1 (FE):     Hide sync UI elements → prevents user-initiated sync
Layer 2 (Backend): Guard endpoints with feature flag → prevents API-level sync  
Layer 3 (Infra):  Suspend CronJob + remove env vars → prevents scheduled sync
```

### Implementation Order

#### Phase 1: Immediate Mitigation (Before April 1st — No Code Release)
1. **Suspend CronJob** `syncaxispagedetails` in OpenShift (`suspend: true`)
2. **Unset/blank** `AXIS_API_URL` in the backend environment → `axissyncservice.py` checks `if self.AXIS_BASE_URL not in (None,'')` and returns empty dict
3. **Unset/blank** `REACT_APP_AXIS_API_URL` in the FE environment → AXIS API calls will fail, error banner appears

#### Phase 2: Feature Flag + FE Cleanup (Next Sprint)
1. Add `REACT_APP_AXIS_SYNC_ENABLED` env var (defaults to `false`)
2. Conditionally render/hide in FE based on flag:
   - "Sync with AXIS" button in `BottomButtonGroup`
   - `AxisMessageBanner`
   - `axisBannerCheck()` call
   - `AxisSyncModal`
3. Add `AXIS_SYNC_ENABLED` env var to backend
4. Guard `foiaxissync.py` endpoint and `axissyncservice.py` with flag check

#### Phase 3: Full Removal (Future Sprint)
- See Section 10: Cleanup / Long-Term Plan

---

## 7. No-Release / Fast Mitigation Strategy

> [!CAUTION]
> AXIS access is lost on **April 1st, 2026**. The following steps can be executed **without any code release**.

### Step-by-Step (Infra-Only Changes)

| # | Action | How | Time | Effect |
|---|--------|-----|------|--------|
| 1 | **Suspend CronJob** | Set `suspend: true` in `syncaxispagedetails` CronJob in OpenShift | ~2 min | No more daily page count syncs |
| 2 | **Blank `AXIS_API_URL`** in request-management-api | Update env var/secret in OpenShift, restart pods | ~5 min | Backend `axissyncservice` returns `{}` for all AXIS calls |
| 3 | **Blank `REACT_APP_AXIS_API_URL`** in forms-flow-web | Update env var/ConfigMap in OpenShift, restart pods | ~5 min | FE AXIS API calls fail → "ERROR" banner shows → sync button disabled |

### Validation After Changes

- Open a request with an `axisRequestId` in the FE
- Verify: "ERROR" banner appears ("System is unable to connect with AXIS")
- Verify: "Sync with AXIS" button is **disabled**
- Verify: No CronJob runs visible in OpenShift logs

### Limitations

- Users will see the "ERROR" banner (confusing but safe)
- UI elements still visible (button disabled, but present)
- Backend endpoints still technically callable (but will return empty results)

---

## 8. Data Integrity Safeguards

### Existing Safeguards

| Safeguard | Location | Status |
|-----------|----------|--------|
| Error handling: AXIS unavailable → "ERROR" banner → button disabled | `FOIRequest.js` | ✅ Active |
| HTTP 401 → "UNAUTHORIZED" banner | `foiRequestServices.js` | ✅ Active |
| Empty response → no data mutation | `FOIRequest.js` line 698 | ✅ Active |
| CronJob empty response → no DB writes | `axissyncservice.py` line 33 | ✅ Active |
| Backend `AXIS_BASE_URL` null check | `axissyncservice.py` line 44 | ✅ Active |

### Recommended Additional Safeguards

#### Short-Term (Phase 2)

1. **Reject sync if AXIS feature flag is disabled:**
   ```python
   # foiaxissync.py
   if not os.getenv('AXIS_SYNC_ENABLED', 'false').lower() == 'true':
       return {'status': False, 'message': 'AXIS sync is disabled'}, 403
   ```

2. **Reject sync for requests not in "new" state:**
   ```javascript
   // BottomButtonGroup - only show sync for new/unopened requests
   const showSyncButton = urlIndexCreateRequest > -1 || 
     requestState?.toLowerCase() === StateEnum.intakeinprogress.name.toLowerCase();
   ```

3. **Add audit logging for any sync attempts:**
   ```python
   # axissyncservice.py
   logging.warning(f"AXIS sync attempted for request {axisrequestid} at {datetime.now()}")
   ```

#### Long-Term (Phase 3)

4. **Add `axisSyncDate` comparison guard:** Reject sync if the returned `axisSyncDate` is older than the local `axisSyncDate`
5. **Add field-level validation:** Before overwriting, compare timestamps to ensure AXIS data is newer
6. **Transaction-level rollback:** Wrap sync save in a DB transaction that can be rolled back

---

## 9. Observability Plan

### Metrics to Track

| Metric | Source | Implementation |
|--------|--------|----------------|
| Sync attempts after cutoff | FE → `axisBannerCheck()` calls | Add FE logging / analytics event |
| Sync failures / blocked calls | Backend → `axissyncservice.py` | Add structured logging with timestamp |
| Data mutations from AXIS | Backend → `saveRequestDetails()` with `axisSyncDate` | Query audit table for requests with `axisSyncDate` changes |
| CronJob execution attempts | OpenShift | Check CronJob status in monitoring |

### Alerting

| Alert | Condition | Channel |
|-------|-----------|---------|
| AXIS sync attempted after April 1st | Any call to `AXIS_API_URL` from backend | Log alert / Slack |
| CronJob `syncaxispagedetails` unexpectedly running | CronJob not in `suspended` state | OpenShift alert |
| Request data modified with `axisSyncDate` after April 1st | DB audit shows `axisSyncDate` change | DB trigger / monitoring query |

### Monitoring Queries

```sql
-- Detect any requests with axisSyncDate updated after April 1st
SELECT requestid, axissyncdate, updated_at, updatedby
FROM "FOIMinistryRequests"
WHERE axissyncdate > '2026-04-01'
ORDER BY updated_at DESC;

-- Count of requests still referencing AXIS
SELECT COUNT(*) as total_axis_requests,
       COUNT(CASE WHEN axissyncdate IS NOT NULL THEN 1 END) as synced_requests
FROM "FOIMinistryRequests"
WHERE axisrequestid IS NOT NULL;
```

---

## 10. Cleanup / Long-Term Plan

### Full AXIS Integration Removal Checklist

#### Frontend (forms-flow-web)

| # | File | Action |
|---|------|--------|
| 1 | `AxisDetails/AxisSyncModal.js` | Delete file |
| 2 | `AxisDetails/axissyncmodal.scss` | Delete file |
| 3 | `AxisDetails/AxisMessageBanner.js` | Delete file |
| 4 | `AxisDetails/axismessagebanner.scss` | Delete file |
| 5 | `AxisDetails/AxisDetails.js` | Remove AXIS sync logic; retain AXIS ID field if needed |
| 6 | `BottomButtonGroup/index.js` | Remove "Sync with AXIS" button, `AxisSyncModal` import/render, `axisSyncedData` / `axisMessage` props |
| 7 | `FOIRequest.js` | Remove `axisBannerCheck()`, `checkIfAxisDataUpdated()`, `extensionComparison()`, `axisSyncedData` state, `axisMessage` state |
| 8 | `utils.js` | Remove `isAxisSyncDisplayField()`, `AXIS_SYNC_DISPLAY_FIELDS` import |
| 9 | `constants/FOI/axisSyncDisplayFields.js` | Delete file |
| 10 | `apiManager/services/FOI/foiRequestServices.js` | Remove `fetchRequestDataFromAxis()`, `checkDuplicateAndFetchRequestDataFromAxis()` |
| 11 | `apiManager/endpoints/index.js` | Remove `FOI_GET_AXIS_REQUEST_DATA` endpoint |
| 12 | `apiManager/endpoints/config.js` | Remove `AXIS_API_URL` export |
| 13 | `BottomButtonGroup/BottomButtonGroup.test.js` | Update test to remove `axisSyncedData` |

#### Backend (request-management-api)

| # | File | Action |
|---|------|--------|
| 1 | `resources/foiaxissync.py` | Delete file |
| 2 | `resources/__init__.py` | Remove `FOIAXISSYNC_API` import and namespace registration |
| 3 | `services/external/axissyncservice.py` | Delete file |
| 4 | `schemas/foiaxissync.py` | Delete file (if exists) |
| 5 | `services/extensionservice.py` | Remove AXIS extension comparison logic |
| 6 | `services/rawrequestservice.py` | Evaluate: `axisrequestid` / `axissyncdate` may need to remain as data fields |

#### Infrastructure

| # | Item | Action |
|---|------|--------|
| 1 | CronJob `syncaxispagedetails` | Delete from OpenShift templates |
| 2 | `REACT_APP_AXIS_API_URL` env var | Remove from all environments |
| 3 | `AXIS_API_URL` backend env var | Remove from all environments |
| 4 | `AXIS_SYNC_BATCHSIZE` env var | Remove |
| 5 | `AXISSYNC_PAGEINFO` secret | Remove |
| 6 | Feature flags (after full removal) | Remove `AXIS_SYNC_ENABLED` / `REACT_APP_AXIS_SYNC_ENABLED` |

#### Integration API (MCS.FOI.Integration)

| # | File | Action |
|---|------|--------|
| 1 | `DTOs/FOIRawRequestDTO.cs` | Remove `AxisSyncDate` property |
| 2 | `DTOs/FOIMinistryRequestDto.cs` | Remove `AxisSyncDate` property |

#### Data Migration Considerations

- **`axisrequestid`** column in `FOIRawRequests` and `FOIMinistryRequests`: **RETAIN** — this is a historical identifier still used for display, search, and linked requests
- **`axissyncdate`** column: Can be **RETAINED** as historical metadata or dropped if no longer needed
- **`axispagecount` / `axislanpagecount`** columns: Evaluate if `recordspagecount` has fully replaced these; if so, can be deprecated
- **Database indexes**: Clean up AXIS-related indexes (`FOIRawRequests_axis`, `FOIMinistryRequests_axis`, etc.)

---

## 11. Risks & Considerations

| Risk | Mitigation |
|------|------------|
| **Users confused by missing sync** | Add in-app notification or banner explaining AXIS sync is no longer available |
| **Partial dependency for new requests** | Validate whether AXIS data population during new request creation is still needed; if so, provide manual entry alternative |
| **Hidden but still callable endpoints** | Backend feature flag ensures endpoints return 403 even if FE is bypassed |
| **CronJob accidentally re-enabled** | Remove CronJob template entirely in Phase 3; add monitoring alert |
| **Stale AXIS data in DB** | No risk — AXIS data already in DB is historical and won't be overwritten after sync is disabled |
| **Integration API still sending `axisSyncDate`** | The DTO field is write-only; no harm in retaining temporarily |
| **Testing gaps** | Update `BottomButtonGroup.test.js` and any E2E tests that reference AXIS sync |

---

## 12. Next Steps

### Immediate Mitigation (Before April 1st) — No Release Required

- [ ] **Suspend** CronJob `syncaxispagedetails` in OpenShift
- [ ] **Blank/unset** `AXIS_API_URL` backend env var → restart pods
- [ ] **Blank/unset** `REACT_APP_AXIS_API_URL` FE env var → restart pods  
- [ ] **Validate** by loading a request with AXIS ID → confirm "ERROR" banner and disabled sync button
- [ ] **Communicate** to team that AXIS sync is disabled and the "unable to connect" banner is expected

### Follow-Up Tasks: Phase 2 — Feature Flag (Next Sprint)

- [ ] Add `REACT_APP_AXIS_SYNC_ENABLED` FE env var
- [ ] Add `AXIS_SYNC_ENABLED` backend env var
- [ ] Conditionally hide/show AXIS sync UI based on flag
- [ ] Guard backend endpoint with flag check
- [ ] Replace "ERROR" banner with informational "AXIS sync has been disabled" message
- [ ] Add structured logging for any sync attempts
- [ ] Update unit tests

### Follow-Up Tasks: Phase 3 — Full Removal (Future Sprint)

- [ ] Delete all AXIS sync FE components (see Section 10)
- [ ] Delete backend AXIS sync service and API endpoint
- [ ] Delete CronJob template
- [ ] Remove all AXIS env vars and secrets
- [ ] Remove feature flags
- [ ] Evaluate DB column cleanup
- [ ] Update integration API DTOs
- [ ] Final regression testing

---

> [!NOTE]
> **Priority is data integrity over feature completeness.** The immediate mitigation (infra-only changes) should be executed before April 1st. The FE/backend feature flag and full removal can follow in subsequent sprints.
