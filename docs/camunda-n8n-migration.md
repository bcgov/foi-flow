> Architecture note · request-management-api

# Camunda → Common Workflow (n8n): engine integration

Current status of the n8n workflow-engine integration, what actually shipped, and a condensed record of the earlier per-request design that was evaluated and superseded before implementation.

- **For:** request-management-api / workflow integration
- **Date:** 2026-08-10 (original design) · updated 2026-09-21 (shipped implementation, CCP-5801)
- **Scope:** bpmservice.py, workflowservice.py, workflowengine.py, commonworkflowservice.py, request.py, rawrequestservice.py

## Status: implemented (CCP-5258, CCP-5801)

n8n is wired in as an alternate workflow engine behind `bpmservice`'s existing method surface. Routing is a **single global config switch**, not a per-request decision, and there are **no new database columns**.

## 01 — How engine selection works

`workflowengine.py` exposes `resolve_engine()` / `resolve_engine_name()`, which read one env var — `WF_DEFAULT_ENGINE` (`camunda` | `n8n`, defaults to `camunda`) — and return either `bpmservice()` or `commonworkflowservice()`.

Every call site in `workflowservice.py` that used to instantiate `bpmservice()` directly (`createinstance`, `postunopenedevent`, `postopenedevent`, `postfeeevent`, `postcorrenspodenceevent`, and the internal `__sync_*` / `__get_wf_pid` helpers) now goes through this resolver instead. The state-machine logic, message-name computation, and activity derivation in `workflowservice.py` never had to change — only the leaf calls did.

There is **no `wfengine` column** on `FOIRequests`/`FOIRawRequests`, and no per-request routing decision — every call is routed by whatever `WF_DEFAULT_ENGINE` is set to at the moment it's made. (An earlier design proposed per-row routing; see §05 for why it wasn't built.)

## 02 — commonworkflowservice.py: single fixed webhook

`commonworkflowservice.py` implements the same method surface as `bpmservice.py` (`unopenedsave`, `unopenedcomplete`, `openedcomplete`, `feeevent`, `correspondanceevent`, `reopenevent`), so `resolve_engine()` can hand back either engine interchangeably and `workflowservice.py` never has to know which one it's talking to.

Every event is POSTed to **one fixed n8n webhook**: `N8N_BASE_URL` + `N8N_ROUTING_WEBHOOK_PATH`, with an `"event"` field naming the message type (e.g. `intakeclaim`, `iaocomplete`, `managepayment`) plus whatever ids/metadata are already in the payload (`foiRequestMetaData`, `rawRequestId`, `foiRequestId`, etc.). n8n is responsible for identifying and routing the request from that payload — request-management-api does not construct or store a per-request instance id/address for n8n.

Optional auth: `N8N_WEBHOOK_AUTH_HEADER_NAME` / `N8N_WEBHOOK_AUTH_HEADER_VALUE` are sent as a header if configured.

**Deferred / not implemented:** `getinstancevariables`, `searchinstancebyvariable`, `searchprocessinstance` all raise `NotImplementedError`. As a direct consequence, `workflowservice.syncwfinstance()` short-circuits to `None` whenever the resolved engine is n8n — there is no reconciliation/sync support for n8n yet.

## 03 — Call-site changes in workflowservice.py / bpmservice.py

- `createinstance`: no-op (returns `None`) when the resolved engine isn't Camunda — n8n has no notion of a pre-created instance; its requests reach the fixed webhook via the normal event calls.
- `postunopenedevent`: no longer errors on a missing `wfinstanceid` when the engine is n8n (n8n requests don't carry one).
- `postunopenedevent` / `postopenedevent` / `postfeeevent` metadata payloads gained `rawRequestId` / `foiRequestId` (via `FOIRequest.getrawrequestidbyfoirequestid`) so n8n has enough context to identify the request without an instance id.
- `syncwfinstance`: returns `None` immediately when `WF_DEFAULT_ENGINE` is n8n (see §02).
- `bpmservice.unopenedsave` signature changed from `(processinstanceid, userid, messagetype)` to `(processinstanceid, metadata, messagetype)`, matching the "metadata is the full JSON event payload" convention every other engine method already uses — Camunda pulls `assignedGroup` / `assignedTo` / `filenumber` out of it as process variables.

## 04 — API/resource + DB changes

- `PUT` on the raw-request BPM-process resource (`request.py`) no longer requires `wfinstanceid` in the body. If it's absent, the payload is treated as an n8n status callback and routed to `rawrequestservice.updatestatuswithnotes(status, requestid, notes, userid)` instead of `updateworkflowinstancewithstatus`.
- `FOIRawRequest.updatestatuswithnotes` (new model method): records the status/notes n8n reports for a request, leaving `wfinstanceid` untouched.
- **No schema migration ships with this integration.** An earlier iteration added a migration for `wfengine` / `wfresumeurl` columns on `FOIRequests` / `FOIRawRequests`; it was built, then reverted before merge — see §05.

## 05 — Superseded design: per-request `wfengine` column (evaluated, not built)

The original proposal for this migration (2026-08-10) was designed, partially implemented, and then reverted in favor of the simpler global-switch design in §01–04. Recorded here for context on why, in case per-request routing is revisited later (e.g. for a gradual Camunda→n8n cutover of in-flight requests):

- **Proposed columns:** `wfengine` (`'camunda' | 'n8n'`) and `wfresumeurl` (`varchar(255)`) on `FOIRequests` and `FOIRawRequests`, so each request's row carried its own engine instead of a single env-var switch.
- **Proposed resolver:** `resolve_engine(wfengine_on_record)` — read the row's `wfengine`; `None`/empty fell back to `WF_DEFAULT_ENGINE` (new-request default), otherwise routed to whichever engine the row already said.
- **Proposed migration strategies for in-flight Camunda requests:**
  - *Option 1 — parallel run (recommended default).* Old requests finish on Camunda untouched; only brand-new requests pick up `WF_DEFAULT_ENGINE`. Lowest risk / smallest blast radius, but Camunda has to stay up (licensing, patching, infra) until the last in-flight request closes — potentially months for a long-running FOI request.
  - *Option 2 — migrate in-flight requests.* A `migratewfinstance()` reconciliation step (extending `syncwfinstance`'s existing pattern) would bootstrap an n8n execution mid-workflow, seed it from derived FOI Postgres state, and flip `wfengine` to `'n8n'` only once the n8n side was confirmed created. Lets you set a hard Camunda shutdown date, at the cost of needing correct "resume from step N" logic for every request shape on day one.
  - Recommendation at the time was to run Option 1 as default while building Option 2's mechanism in reserve, for selective use on stuck/long-tail requests rather than a bulk cutover.
- **Risk areas identified for the per-row design:** in-progress Camunda requests being treated as n8n before their Camunda instance finished; Common Workflow's Data Table drifting from FOI Postgres; duplicate execution on retried events (mitigation: search-before-create, mirroring `bpmservice.searchinstancebyvariable`); the flip-to-`'n8n'` happening before bootstrap was confirmed; and rollback (never terminate the Camunda instance during migration — leave it idle so rollback is just flipping the column back).
- **Why it wasn't built:** the shipped scope (CCP-5801) only needed *new* requests to be routable to n8n; migrating in-flight Camunda instances wasn't in scope. The column/resolver machinery and its migration file were removed rather than shipped unused. If per-request/in-flight migration becomes a real requirement, Option 2's shape above (and the risk/mitigation list it came with) is the starting point.

## 06 — Cutover path (current)

Flip `WF_DEFAULT_ENGINE` from `camunda` to `n8n` (env var only, no code deploy) to send new workflow events to n8n. This is currently an **all-or-nothing switch** — there's no in-between state for individual in-flight requests (that's the gap §05 describes). Camunda code (`bpmservice.py`, `camundaservice.py`) stays in place; removing it is a separate, later decision, made only once it's no longer needed.

## Open questions / known gaps

- Reconciliation/sync for n8n (`getinstancevariables` / `searchinstancebyvariable` / `searchprocessinstance`) is unimplemented — needed before `syncwfinstance` can support n8n-routed requests.
