# Camunda → n8n: review responses and next steps

*Decision record from the FOI team meeting, 28 Sep 2026*

**Contents**

1. [Decisions from the FOI team meeting](#decisions-from-the-foi-team-meeting-28-sep-2026)
2. [Part 1: PR review comments, our responses](#part-1-pr-review-comments-our-responses)
3. [Part 2: Migration options](#part-2-migration-options-two-ways-to-get-there)
4. [Side by side](#side-by-side-how-the-two-options-differ)
5. [Option 1: Parallel run (not chosen)](#option-1-parallel-run-camunda--n8n)
6. [Option 2: Full in-flight migration (chosen)](#option-2-full-in-flight-migration)
7. [Questions](#questions)

---

## Decisions from the FOI team meeting (28 Sep 2026)

> **Migration approach · D1 — Option 2: full migration. Camunda will be decommissioned.**
> Matt confirmed this is the approach the business wants. It answers PR comment 1.

| # | Decision | Detail |
| --- | --- | --- |
| D2 | **Only requests waiting for a payment outcome need migrating** | Every other request moves to n8n on its next update. n8n is event-based with no wait nodes, so there is nothing to carry over. |
| D3 | **Roll out through DEV and TEST first** | Run the full migration in DEV, fix what it finds, test properly in TEST, then plan production after sign-off. DEV → fix → TEST → sign-off → PROD. |
| D4 | **No 5-day reopen window in n8n** | Matt confirmed a closed request can be reopened at any time, even after 5 days. Camunda's closed-request timer is not carried over. |
| D5 | **Comment 6 approach agreed** | Build the outbox table, the outbox status updates, the n8n error workflow, and replay mechanism. |

### Next steps (owner: Divya)

1. Resolve the PR review comments, except comment 1 (answered by D1).
2. Prepare a migration plan for in-flight requests waiting for a payment outcome.
3. Run the full migration in DEV, fix the issues, then hand over to TEST.
4. Come up with a rollback plan.

Steps 1 and 2 are part of the current sprint work. Steps 3 and 4 will be considered for the next sprint, after the PR is merged.

---

## Part 1: PR review comments, our responses

Status key: **Fixed / no change** · **After DEV testing** · **Decision in Part 2** · **Staged plan**

### Comment 1 — Keep active Camunda requests on Camunda

**Status: Decided 28 Sep · Option 2**

Decided: full migration to n8n, and Camunda is decommissioned (D1). Only requests waiting for a payment outcome need migrating; a migration plan will follow. See [Decisions](#decisions-from-the-foi-team-meeting-28-sep-2026).

### Comment 2 — Secure and validate n8n status callbacks

**Status: No change needed**

- The Camunda callback `/foirawrequestbpm/addwfinstanceid` only saves `wfinstanceid` and notes. The status in its payload is never used; the saved status is the one already in the DB.
- n8n has no execution id to save, so n8n doesn't need to update the DB at all.
- The n8n branch of the callback is removed, and no n8n workflow calls it. No caller-supplied status reaches the DB.

### Comment 3 — Handle missing n8n config and failed webhooks safely

**Status: Fixed**

- An empty or blank `N8N_BASE_URL` is rejected and logged. The event isn't sent.
- Webhook calls have a timeout (`N8N_WEBHOOK_TIMEOUT_SECONDS`, default 10s).
- Network errors are caught and logged. They no longer break the user's save.
- Tests cover unset/empty URL, timeout, connection error, error and success responses.

### Comment 4 — Pass the n8n settings to the Linux Compose stack

**Status: Fixed**

- `docker-compose-linux.yml` now passes the engine, n8n URL, webhook path, auth header, timeout and retry settings to the backend.
- It also passes the Redis settings the retry queue uses.

### Comment 5 — Stop logging full request schemas and webhook payloads

**Status: After DEV testing**

- The extra logs are there to debug the integration.
- They'll all be removed once the flow is tested properly in DEV.

### Comment 6 — Make outbound events and inbound callbacks safe to retry

**Status: Agreed 28 Sep**

**Outbound · API → n8n.** An event can be **lost** (request saved, POST to n8n fails) or **duplicated** (API times out after n8n already did the work, then retries). Still applies in full.

**Inbound · n8n → API.** The status callback is removed (comment 2), so there is no state to protect. What remains: n8n retries payment, email and notification calls up to 3 times, where Camunda tried once. A retry can **email an applicant twice**.

#### n8n calls into the API: what a retry does

| n8n node | If n8n retries | Risk | Retry |
| --- | --- | --- | --- |
| GET Payment Details | Nothing, read only | None | Keep |
| Invoke Cache Refresh API | Cache reloads again | None | Keep |
| POST Notify Email | Second email to the applicant and a second correspondence row | High | **Turn off** |
| POST Notify Email Ack | Duplicate copy of the sent email on the request | Medium | **Turn off** |
| POST Expiry Notification | Duplicate comment and notification | Medium | **Turn off** |
| Invoke Reminder API | Whole nightly batch runs again | Low–medium | **Turn off** |
| POST Save Payment | Extra payment version with the same data | Low | **Turn off** |
| POST Cancel Payment | Extra version; expiry time moves a few seconds | Low | **Turn off** |

#### Phase A — this PR

- **commonworkflowservice:** timeout and error handling (comment 3). *Done.*
- **commonworkflowservice:** add an `event_id` (uuid4) to every payload. *To do.*
- **FOI Request Routing:** respond immediately. *Done.*
- **FOI Request Routing:** record the `event_id` with the run id in `foi-process-audit`. Skip an `event_id` whose earlier run **completed**; let failed or unfinished ones run again. Add the `event_id` column in FOI - Initialize Data Tables. *To do.*
- **n8n error workflow:** record failed runs and send an alert, because the API can't see them (see below). *To do.*
- **FOI Backend API Manager V2:** turn off retries on the "Turn off" nodes above. Send failures to the error output and log them. Same as Camunda: one attempt, and a failure someone can see. *To do.*
- **Sub-workflow calls:** turn off retries where the sub-workflow sends email or creates a payment, since a retry re-runs the whole sub-workflow. *To do.*

Also in this PR: a Redis retry queue re-sends events that failed to reach n8n. It is a stop-gap until Phase B.

#### Phase B — this PR

- An outbound event table in Postgres (`FOIWorkflowEventOutbox`): event id, payload, status, attempts, next retry time.
- **commonworkflowservice** inserts a row instead of posting, in the same transaction as the request change.
- A dispatcher thread started in `wsgi.py`, like the publication consumer. It claims rows, sends them, and retries with backoff until a dead-letter state.
- n8n reports each run's outcome back to the outbox row, plus a sweeper for runs with no outcome (see below).
- A way to view and replay dead-lettered, failed and "no outcome" events.
- Optional: restrict workflow-only endpoints to an n8n service account.

#### Phase C — dropped

- A callback inbox table, `event_id` on callbacks, and version checks against late callbacks.

Not needed: the status callback is removed (comment 2), and the remaining n8n calls don't write request state sent by the caller.

#### How the pieces work

**n8n error workflow (Phase A)**

1. One workflow starting with an **Error Trigger**, set as the error workflow of FOI Request Routing and the Payment Expiry SLA Job.
2. n8n passes the run link, workflow, failed step and error. Request ids come from the `event_id` recorded at the start of routing.
3. **Record** it in an `foi-execution-errors` Data Table.
4. **Alert** through Teams, or email, with the request number and run link.
5. Phase B: also report it to the API, which marks the outbox row `FAILED`.

Nodes set to "continue on error" hide failures. Route their error output to Stop and Error. Keep failed-run data (`EXECUTIONS_DATA_SAVE_ON_ERROR=all`).

**Outbox row status (Phase B)**

A 2xx only means "n8n received it". n8n must report the outcome back.

`PENDING` → `DELIVERED` → `COMPLETED`, or `FAILED`. If it never reached n8n: `DEAD_LETTER`.

- **COMPLETED:** a last node in FOI Request Routing, after all branches finish, calls `PUT /api/foiworkflow/events/{event_id}`.
- **FAILED:** the error workflow calls the same endpoint.
- **Sweeper:** rows still DELIVERED after ~30 min are flagged "no outcome" and alerted. Silence never counts as success.

This is not the comment 2 callback: it updates only the outbox row, never request state.

---

## Part 2: Migration options, two ways to get there

New requests are ready to run on n8n. The question was what happens to requests already running in Camunda: let them finish there, or move them all to n8n at release. **Decided 28 Sep: move them all (Option 2).**

| | Option 1 · Parallel run: Camunda + n8n | Option 2 · Full in-flight migration |
| --- | --- | --- |
| Status | Not chosen | **✓ Chosen · 28 Sep** |
| Summary | New requests go to n8n. Existing requests finish in Camunda. A per-request `wfengine` column decides which engine gets each event. | At release, every request, new and in-flight, runs through n8n. Camunda FOI processes are suspended at cutover. |
| In-flight risk | Lowest | Medium (payments) |
| Cutover effort | Low | High |
| Camunda stays | Years, until drained | Cutover + rollback window |
| Rollback | Easy | Hard once payments run |

---

## Side by side: how the two options differ

| | Option 1 · Parallel run | Option 2 · Full migration |
| --- | --- | --- |
| Routing | Per request, from the stored `wfengine` | One global switch, `WF_DEFAULT_ENGINE` (today's branch) |
| Database | New `wfengine` column + backfill as `camunda` | No FOI schema change needed (`wfengine` recommended for rollback). One-off n8n payment table backfill |
| n8n workflow work | Payment parity fixes | Two schedules, a reconciliation job |
| Camunda lifetime | Until the last Camunda request closes | Suspended at cutover, removed after rollback window |
| In-flight payments | Stay on Camunda. No gap | Must be exported, backfilled and verified |
| Cutover | Deploy, migrate, flip the switch | Maintenance window: extract, backfill, flip, suspend, verify |
| Rollback | Flip the default back. n8n requests stay on n8n | Scripted. Needs `wfengine` to keep n8n-started payments on n8n |
| Stuck requests | Camunda sync repairs IAO/ministry instances only | Replay tool with per-event rules + reconciliation job |
| Main risk | Long dual-engine period; a version that drops `wfengine` | Payment state at cutover; both engines acting on one request |

---

## Option 1: Parallel run, Camunda + n8n

> **Not chosen · kept for reference.**

Every request is stamped with the engine that owns it. That engine handles it for its whole life, including reopen, fees and correspondence.

### Flow

- **New request** (created after cutover) → stamped at creation from `WF_DEFAULT_ENGINE` → `wfengine = n8n` → fixed webhook → **n8n FOI Request Routing**.
- **In-flight request** (existed at deployment) → set by the migration backfill → `wfengine = camunda` → stored `wfinstanceid`, message correlation → **Camunda BPMN**.

On every event, `workflowservice` reads the request's own `wfengine`. `WF_DEFAULT_ENGINE` is read only when a raw request is created. An opened FOI request inherits its raw request's engine, and ministry requests inherit from their FOI request.

### Required changes

| Area | Changes |
| --- | --- |
| Database | Add `wfengine` (`camunda` \| `n8n`) to FOIRawRequests and FOIRequests. Backfill every existing row as `camunda`, then make it NOT NULL. Optional: requests with no live Camunda instance → `n8n` (Q2) |
| API code | Resolver takes the engine explicitly, with no env fallback. Every workflow entry point loads the request's engine. Carry `wfengine` forward on every new version. New raw request stamps the default. Opened request inherits it |
| API endpoints | No new endpoints. Camunda callback stays for Camunda requests. Sync endpoint says "not applicable" for n8n requests |
| n8n workflows | Nothing needed for in-flight safety. Payment parity fixes still needed for new requests: G4, G12, G13, G14 |

### In-flight requests

**What happens to them**

- Stay on Camunda for life, including reopen, fees and correspondence.
- Camunda keeps its own payment state, so the in-flight payment gaps do not apply.
- A raw request with no Camunda instance self-heals: the sync step creates the instance on its next event, if Camunda is up.
- Reopening an old Camunda request re-creates its Camunda instance, which extends Camunda's life (Q2).

**Existing Camunda payment gaps stay during the drain**

- **Correspondence needs a live instance.** If `wfinstanceid` can't be resolved, the fee message fails silently. Staff see "sent", the applicant gets nothing.
- **Payment failures end the instance.** After 3 retries the fee process just ends. A failure between creating the Form.io submission and saving the URL loses the payment.

### Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| A new version drops `wfengine` | Request switches engine mid-flight | NOT NULL, no env fallback, tests per versioning path |
| Long Camunda tail | Requests stay open for years; reopen revives old ones | Track the drain weekly. Use Q2 and per-request migration for the tail |
| Two engines to operate | Two sets of monitoring and support knowledge | Runbook: which engine owns which request |
| Global timers stay on Camunda | Cache refresh and reminders stop if Camunda goes first | Add n8n schedules (G8) before decommissioning |
| Reporting | Workflow history split across two engines | Agree the reporting source per engine |
| Rollback | Only affects new requests | Accept. n8n requests stay on n8n |

### Deployment steps

1. Merge code + migration with `WF_DEFAULT_ENGINE=camunda`. Every existing row becomes `camunda`. No behaviour change.
2. Verify in TEST: every row has an engine; Camunda flows work end to end.
3. Deploy n8n workflows and Data Tables. Configure n8n variables and webhook credential.
4. Set `WF_DEFAULT_ENGINE=n8n` and restart API pods. New requests now go to n8n.
5. Smoke-test one new request: intake, open, IAO, ministry, fee (PAID, CANCELLED, EXPIRED), close.
6. Monitor the retry dead-letter list and n8n audit daily. Track open Camunda requests weekly.
7. When Camunda reaches zero, add n8n schedules (G8), suspend Camunda timers, decommission.

---

## Option 2: Full in-flight migration

> **Chosen · 28 Sep.**

n8n has no process instance to create. "Migrating" a request means three things: stop Camunda acting on it, seed the one table n8n reads (`foi-payment-sla`), and send every later event to n8n.

### Cutover flow

1. Drain short-lived Camunda work (emails).
2. Export Camunda variables for active instances.
3. Backfill `foi-payment-sla` for open online payments.
4. Set `WF_DEFAULT_ENGINE=n8n`, restart API.
5. Suspend Camunda FOI definitions + instances.

**After release:** every request event → workflowservice → n8n FOI Request Routing.

### In-flight states

| In-flight state | Status | What to do |
| --- | --- | --- |
| Unopened / Intake in Progress | No gap | Suspend the Camunda instance. |
| Open, IAO, ministry states (no payment) | No gap | Suspend the Camunda instance. |
| General correspondence | No gap | The API sends these emails itself. No workflow involved. |
| Fee correspondence, balance due = 0 | No gap | No payment created. Nothing to move. |
| Fee correspondence, balance due > 0, not Closed | **Gap · G2–G6** | Any status, not only On Hold. Backfill it. Select by active payment, not by status. |
| On Hold with a Camunda online payment | **Gap · G2–G6** | Export Form.io ids, backfill the SLA row, fix workflows. |
| Payment expired in Camunda, still unpaid | **Gap · G13** | Backfill so the expiry job skips it but a late PAID still finds it. |
| Fee instance failed before URL saved | Existing defect | Applicant never got the link. Report it, then replay to n8n after cutover. |
| On Hold with offline payment | No gap | Offline flag bypasses the online fee path. Verify in TEST. |
| Email processing in progress | Drain | Short-lived. Wait until none are active before suspending. |
| Closed ≤ 5 days | No gap | Reopen works statelessly in n8n; the 5-day window isn't needed (D4). Suspend the instance. |
| Closed > 5 days | No gap | No Camunda instance left. Nothing to do. |
| Incident or stuck instance | Check | List before cutover and resolve by hand. Examples below. |
| Raw request with no Camunda instance | No gap | Holds no Camunda state. Goes straight to n8n. |

### Stuck Camunda instances: what to look for

| # | Example | Cause | Seen as | Fix |
| --- | --- | --- | --- | --- |
| 1 | Payment link never sent | Fee process fails 3× on payment details or save, then ends | Correspondence "sent", applicant has no link | Replay the correspondence event to n8n |
| 2 | Correspondence never reached Camunda | Missing `wfinstanceid` or inactive IAO task | Same as #1, no fee instance at all | Same as #1 |
| 3 | Orphan Form.io submission | Submission created, then save API fails | Same as #1, plus an unused submission | Ignore the orphan, re-drive as #1 |
| 4 | Expiry notification failed | Notification API fails 3×, instance ends | No expiry email; a late PAID gets no receipt | Send manually or backfill as expired-but-open |
| 5 | Status drift | A message fails to correlate; Camunda keeps an old status | Usually nothing; Camunda-side payment rules may misfire | List only. n8n reads status from the event |
| 6 | Failed job incident | Script error or connector timeout | Stuck in Camunda Cockpit | Resolve or delete, then suspend |

### Gaps to close before release

"Migration only" gaps are specific to moving in-flight requests. "Also new requests" gaps affect n8n-native requests too.

| # | Gap | Detail and fix | Applies to |
| --- | --- | --- | --- |
| G1 | Camunda keeps running after cutover | Its timers still call the cancel and expiry APIs. **Fix:** suspend definitions and instances at cutover. | Migration only |
| G2 | No n8n payment row for Camunda payments | n8n payment logic reads only `foi-payment-sla`. **Fix:** one-off backfill. | Migration only |
| G2a | Form.io ids exist only in Camunda | Needed to mark the applicant's submission paid. **Fix:** export before suspending (Q6). | Migration only |
| G3 | Cancel rule depends on the SLA row | Payment not cancelled when leaving On Hold. **Fix:** trust `isPaymentActive`. | Also new requests |
| G4 | Form.io update fails silently | Submission not marked paid, but the email still goes. **Fix:** fail visibly, guard missing ids. | Also new requests |
| G5 | Cancel blanks the payment URL · low | Cancel still works; history loses the URL. **Fix:** closed by backfill; optionally keep the URL. | Also new requests |
| G6 | Pre-cutover payments never expire | Expiry job only sees SLA rows. **Fix:** closed by G2. | Migration only |
| G7 | No way to re-drive a stuck request | Sync endpoint does nothing for n8n. **Fix:** admin replay with per-event rules. | Support tooling |
| G8 | Daily jobs not scheduled in n8n | Cache refresh and due-date reminders stop with Camunda. **Fix:** two n8n schedules. | Also new requests |
| G9 | Events are not idempotent | A retried event can run twice. **Fix:** `event_id` + dedupe + error workflow. | Also new requests |
| G10 | No cutover tooling | Can't rehearse without it. **Fix:** CLI with report, backfill and rollback modes. | Migration only |
| G12 | Payment start is not resumable | Same class of problem as Camunda. **Fix:** register the SLA row first, reconcile, replay. | Also new requests |
| G13 | Late PAID after expiry | n8n closes the row on expiry, so Form.io can't be updated. **Fix:** keep the row findable. | Also new requests |
| G14 | Form.io data differs from Camunda · verify | Missing `templateName`; no update on CANCELLED. **Fix:** add field, patch on cancel. | Also new requests |

### Stuck fee events: replay rules

| Stuck at | Left behind | Replay? | Make it safe by |
| --- | --- | --- | --- |
| Start, before Form.io | Payment row without URL | Yes | — |
| Start, before URL saved | Orphan Form.io submission | Yes | Reuse stored Form.io ids on replay |
| Start, around the email | URL saved, email unknown | With care | Record `email_sent_at`; skip if set |
| Start, before SLA row | Live payment n8n doesn't know | No | Register the SLA row first (G12) |
| PAID | DB correct; Form.io, receipt, SLA pending | Yes | Close SLA before receipt; skip if already PAID |
| CANCELLED | Payment may still be active | Yes | Skip if already cancelled |
| EXPIRED | SLA row still active | Automatic | Mark "expiring" first; cap attempts |

A daily reconciliation job finds payments without a URL, payments with no SLA row, and SLA rows stuck or out of step with the DB.

### Payment expiry: Camunda vs n8n

| | Camunda | n8n |
| --- | --- | --- |
| Based on | `paymentExpiryDate` (not 20 days; the labels are stale) | `paymentExpiryDate`; 20 days only if no date |
| Checked | Once a day at 13:00 | Once a day at 13:00 |
| Weak spot | Can fire a day early or late; a missed 13:00 check means it never expires | Fires at the first 13:00 check after the expiry day ends; a missed check is caught by the next |
| After expiry | Keeps waiting; a late PAID is handled | Closes the row; a late PAID can't update Form.io (G13) |

### Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Both engines act on a request | Duplicate cancels and expiry emails | Suspend Camunda in the same window as the flip (G1) |
| Wrong Form.io ids in backfill | Paid applicants not shown as paid | Export before suspending; reconciliation report; G4 |
| Applicant pays mid-cutover | n8n sees PAID before its SLA row exists | Payment itself is safe. |
| Visible behaviour changes | Reopen any time; expiry timing changes | Reopen any time: confirmed (D4). Expiry timing: confirm (Q8) |
| Hidden Camunda drift | Stuck instances with wrong state | Pre-cutover report; fix by hand |
| No idempotency | Retries duplicate side effects | G9 before cutover |
| Operational readiness | n8n is the only engine from day one | Alerts on dead letters and failed executions |

### Migration steps

**Before release**

- Close G3–G5, G8, G9, G12–G14. Build the reconciliation job.
- Build the cutover CLI (G10) and SLA import (G2).
- Rehearse on TEST with a production copy, including PAID, CANCELLED and expiry on migrated payments.
- Agree window, rollback window and go/no-go.

**Cutover window**

- Block staff edits. Keep API and payment pages up. Hold workflow events.
- Wait for emails to drain. Run the report; resolve incidents; save the export.
- Backfill; check the count matches open online payments.
- Flip to n8n; suspend Camunda; move the daily schedules.
- Smoke-test; reopen the application.

**After cutover**

- Watch dead letters, failed executions and the audit table daily for two weeks.
- After the rollback window, decommission Camunda FOI processes.

### Rollback

> **Not smooth once n8n has handled payments.** Lifecycle events roll back cleanly. Payments started in n8n have no Camunda instance, so a later PAID or CANCELLED has nothing to match in Camunda.

| At rollback | Problem | Rollback script does |
| --- | --- | --- |
| No payment activity since cutover | None | Reactivate the instance |
| Camunda payment, still open | None after reactivation | Reactivate; close its n8n SLA row |
| Camunda payment, closed in n8n | Old timer may send a wrong expiry email | Delete that fee instance |
| n8n payment, still open | No Camunda instance to match | Keep it on n8n (needs `wfengine`) or recreate in Camunda |
| n8n payment, closed | None | Nothing |

> **Add `wfengine` even for Option 2.** With it, rollback is "set `camunda` for requests without an open n8n payment" and n8n keeps the rest. Without it, every open n8n payment must be rebuilt in Camunda by script.

---

## Questions

### Option 2 — open

- **Q6.** Which Camunda variables hold the Form.io ids, and does every open payment have them?
- **Q7.** How many open online payments and open requests are in production?
- **Q8.** Do business owners accept the n8n payment expiry timing?

### Answered 28 Sep — resolved

- **Q5. Is there a fixed Camunda shutdown date?** **Camunda will be decommissioned.** Production date to be planned after TEST sign-off.
- **Q8. Can a closed request reopen after 5 days?** **Yes, any time.** No 5-day window in n8n.

### Option 1 — not needed

- **Q1.** How many requests are open today, and how long until Camunda drains?
- **Q2.** Can requests with no live Camunda instance (e.g. closed > 5 days) start as `n8n`?

**Dependency:** n8n production hosting, Data Table backups and credentials (FOI OIDC, Form.io, webhook auth) must be ready before any cutover.

---

*Source: [foi-n8n-migration-options.html](foi-n8n-migration-options.html), as discussed and updated in the FOI team meeting on 28 Sep 2026.*
