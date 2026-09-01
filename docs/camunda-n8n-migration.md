> Architecture note · request-management-api

# Camunda → Common Workflow: how to structure the workflow-engine swap

Where versioning should actually live, how to keep bpmservice.py and workflowservice.py nearly untouched, and which of the two migration strategies to run — grounded in how these two files are wired into the codebase today.

- **For:** request-management-api / workflow integration
- **Date:** 2026-08-10
- **Scope:** bpmservice.py, workflowservice.py, commonworkflow integration
- Keep bpmservice.py exactly as it is. Add a sibling commonworkflowservice.py with the same method surface.
- Add columns — wfengine ( 'camunda' | 'n8n' ), wfresumeurl ( 'varchar(255)' ) — to FOIRequests and FOIRawRequests . It's the only new state the migration needs.
- In workflowservice.py , replace the ~15 direct bpmservice() instantiations with a one-line resolver call that reads wfengine . Every orchestration method keeps its current logic untouched.
- Run Option 1 (parallel run, old finishes on Camunda) as the default. Build Option 2 's reconciliation mechanism anyway — it's a small extension of the syncwfinstance pattern already in the codebase — and keep it in reserve as the tool you reach for if a handful of Camunda instances are still limping along when you actually need to shut Camunda off.

## 01 — Where versioning actually belongs

01

Looking at how workflowservice is used, it's never exposed as an HTTP contract:


| Caller                    | What it calls                                                                             |
| ------------------------- | ----------------------------------------------------------------------------------------- |
| requestservice.py         | syncwfinstance, postunopenedevent, postfeeevent, postopenedevent, postcorrenspodenceevent |
| rawrequestservice.py      | createinstance, syncwfinstance, postunopenedevent                                         |
| foiworkflow.py (resource) | syncwfinstance                                                                            |


All three are plain Python imports ( workflowservice() ), not HTTP calls. Even foiworkflow.py , which is a Flask resource, exposes a stable outward contract (a sync trigger) — it doesn't expose "which BPM engine we're using" to its caller, and it shouldn't start to. That's the tell: the thing changing is an internal implementation detail (which engine backs the workflow), not a public contract (what a caller sends and gets back). REST versioning ( /api/v1 vs /api/v2 ) is for the latter. Applying it here would mean asking every internal caller across three files to know and choose an API version for a decision that's really "which row am I operating on, and which engine currently owns it" — information the call site doesn't have and shouldn't need.

So: version the implementation internally (module-level, via a resolver), not the API . Section 3 below covers the one case where REST-visible versioning would be justified, and why it still isn't needed here.

## 02 — Structuring bpmservice.py / workflowservice.py for minimal change

02

bpmservice(camundaservice) already reads like an implicit interface — every method workflowservice depends on has a fixed shape: createinstance , getinstancevariables , searchinstancebyvariable , searchprocessinstance , unopenedsave , unopenedcomplete , openedcomplete , feeevent , correspondanceevent , reopenevent . Nothing in bpmservice.py needs to change — commonworkflowservice.py just needs to implement the same ten methods against the common workflow interface.

### workflowservice.py — the only change is how the engine is obtained

```text
# before — every call site names bpmservice() directly
def createinstance(self, definitionkey, message):
    response =
bpmservice()
.createinstance(definitionkey, json.loads(message))
    ...

def postunopenedevent(self, id, wfinstanceid, requestsschema, status, ministries=None):
    ...
    return
bpmservice()
.unopenedcomplete(wfinstanceid, metadata, MessageType.intakecomplete.value)
# after — one resolver call replaces the constructor everywhere
from request_api.services.workflowengine import resolve_engine

def createinstance(self, definitionkey, message):
    response =
resolve_engine(None)
.createinstance(definitionkey, json.loads(message))
    ...

def postunopenedevent(self, id, wfinstanceid, requestsschema, status, ministries=None):
    ...
    return
resolve_engine(wfinstanceid=wfinstanceid, requestid=id)
.unopenedcomplete(
        wfinstanceid, metadata, MessageType.intakecomplete.value)
```

Every method that already receives wfinstanceid or an id can resolve its own engine; the state-machine logic, message-name computation, and activity derivation in workflowservice.py ( __messagename , __getministryactivity , __hasreopened , etc.) never has to know Camunda from Common Workflow — it just calls the ten-method contract. That's the whole diff: a find-and-replace of bpmservice() → resolve_engine(...) , roughly 15 call sites, zero business-logic changes.

FOI's own Postgres tables ( FOIRequests , FOIMinistryRequests , FOIRawRequest ) are already the system of record for status and state — syncwfinstance derives the correct message/activity from FOI DB history, then pushes it at the engine. The engine (Camunda today, Common Workflow tomorrow) is a downstream reflector, not the source of truth. That's what makes an engine swap tractable at all: workflowservice.py 's decision logic doesn't change because it was never Camunda-shaped to begin with — only the ten leaf calls at the bottom were.

## 03 — A note on REST versioning

03

REST versioning ( /api/v1 vs /api/v2 ) isn't on the table for this migration: nothing about a request/response contract is changing anywhere in this flow, only which engine sits behind an internal call. Versioning the API would mean asking external callers to know and choose a backend that's none of their concern, for a change they can't observe. Internal versioning — the resolve_engine() strategy in §1–§2 — is the actual solution here.

## 04 — Suggested file structure

04

## 05 — Request routing: old → Camunda, new → Common Workflow, migrated → Common Workflow

05

resolve_engine only ever looks at one thing: the wfengine value already on the row. There's no separate "is this request old or new" heuristic to maintain — a request's engine is whatever the last write left in that column.

```text
flowchart TD
    A["workflowservice method called\nfor a given request/wfinstanceid"] --> B{"wfengine on\nthe request row?"}
    B -- "null / never set\n(brand-new request)" --> C{"WF_DEFAULT_ENGINE\nconfig"}
    C -- "camunda" --> D[bpmservice]
    C -- "n8n" --> E[commonworkflowservice]
    B -- "'camunda'" --> F{"migration trigger\nfired for this row?"}
    F -- "no" --> D
    F -- "yes (Option 2 path)" --> G["migratewfinstance():\nbootstrap commonworkflow execution,\nseed state, flip wfengine='n8n'"]
    G --> E
    B -- "'n8n'" --> E
    D --> H["Camunda process instance\n(existing, unaffected)"]
    E --> I["n8n execution +\nData Table row"]
```

```text
# workflowengine.py
import os
from request_api.services.external.bpmservice import bpmservice
from request_api.services.external.commonworkflowservice import commonworkflowservice

DEFAULT_ENGINE = os.getenv(
"WF_DEFAULT_ENGINE"
,
"camunda"
)

def resolve_engine(wfengine_on_record):
"""wfengine_on_record: the FOIRequests/FOIRawRequests.wfengine value
    for this row, or None if no workflow instance has been created yet."""
if wfengine_on_record in (None, ""):
        return commonworkflowservice() if DEFAULT_ENGINE ==
"n8n"
else bpmservice()
    if wfengine_on_record ==
"n8n"
:
        return commonworkflowservice()
    return bpmservice()
```

"Old request → Camunda" and "migrated request → Common Workflow" collapse into the same branch: both just read wfengine . The only thing that makes a request "migrated" rather than "old" is that something (a background job, or an on-demand trigger inside syncwfinstance ) previously flipped its wfengine column from 'camunda' to 'n8n' and bootstrapped the n8n side. Routing itself never has to know why a row says 'n8n' .

## 06 — Switching from old to new once Camunda is decommissioned

06

Cutover is a config change, not a code change: flip WF_DEFAULT_ENGINE from camunda to n8n so every brand-new request (no wfengine yet) routes to Common Workflow. Existing rows are unaffected — they already carry their own wfengine value, so this flag only governs requests that haven't picked an engine yet.

Code cleanup (deleting bpmservice.py , camundaservice.py , the Camunda branch in resolve_engine ) is a separate, later PR, done only once every row in FOIRequests / FOIRawRequests reports wfengine='n8n' or closed . Don't couple "stop routing new work to Camunda" with "delete the Camunda code" — the first is reversible in one env var; the second isn't.

## 07 — Comparing the two migration approaches

07


| Approach                                                                 | Upside                                                                                                                                                                           | Downside                                                                                                                                                                                                                                |
| ------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Option 1 Parallel run, old finishes on Camunda recommended default       | Zero replay risk for in-flight requests — Camunda instances just run to completion untouched. Smallest blast radius; Common Workflow only has to prove itself on new work first. | Camunda has to stay up (licensing, patching, infra cost) until the last in-flight request closes — which for a long-running FOI request could be months.                                                                                |
| Option 2 Migrate in-flight requests to Common Workflow reserve mechanism | Lets you set a hard Camunda shutdown date regardless of how many requests are still open.                                                                                        | Requires the "determine current step and continue from there" logic to be correct for every request shape on day one — higher up-front risk, and any bug reruns/duplicates live production events rather than failing a fresh instance. |


Recommendation: run Option 1 as the default operating mode. Build Option 2's mechanism (the migratewfinstance extension in §5) at the same time, since it's a small, natural extension of a reconciliation pattern syncwfinstance already implements — but apply it selectively, to specific stuck or long-tail requests, rather than as a bulk cutover. That gets you Option 1's low up-front risk with Option 2's escape hatch already tested and available if Camunda needs to go away on a deadline rather than when the backlog naturally drains.

## 08 — Risks and edge cases

08


| Area                                                            | Risk                                                                                                                                         | Mitigation                                                                                                                                                                                                                                                                                    |
| --------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| In-progress Camunda requests                                    | A request gets treated as "n8n" before its Camunda instance has actually finished, and both engines try to act on the same event. | wfengine is the single gate every call site checks before choosing an engine; never call both engines for one row. Migration (flipping the column) only happens inside migratewfinstance , deliberately, never implicitly.                                                                    |
| Workflow state sync                                             | Common Workflow Data Table drifts from what the request actually did.                                                                        | FOI Postgres stays the single source of truth, exactly as today — engine state (Camunda variables or Common Workflow Data Table rows) is a derived reflection, rebuildable from Postgres via the same reconciliation logic syncwfinstance already runs.                                       |
| Duplicate workflow execution                                    | A retried event or a re-run sync creates a second n8n execution for a request that already has one.                               | Mirror bpmservice.searchinstancebyvariable 's search-before-create in commonworkflowservice : look up the request id in the Data Table before starting a new execution.                                                                                                                       |
| Request updates/events                                          | An event fires for a request mid-migration (row flipped to 'n8n' but bootstrap not yet confirmed).                                | Flip wfengine only after the n8n execution + Data Table row are confirmed created — treat the flip as the last step of migratewfinstance , not the first.                                                                                                                          |
| Determining the latest step                                     | Common Workflow needs to resume mid-workflow without replaying already-completed steps.                                                      | Reuse, don't reinvent: __sync_state_transition / __sync_complete_event already derive "what should have happened" from FOIMinistryRequest state history. Feed that derivation into the Common Workflow Data Table as the seeded state instead of writing a parallel step-detection algorithm. |
| request-management-api ↔ Common Workflow Data Table consistency | Split-brain between the two stores.                                                                                                          | Same posture as Camunda today: Data Table is a cache of Postgres-derived state, not an independent ledger. Never let the Common Workflow Data Table be the thing workflowservice.py trusts for "what happened" — it already asks the FOI DB.                                                  |
| Rollback mid-migration                                          | A migrated request needs to go back to Camunda after a bad bootstrap.                                                                        | Never terminate the Camunda process instance as part of migration — leave it idle/paused. Rollback is then just flipping wfengine back to 'camunda' . Only decommission a Camunda instance after an explicit bake period on Common Workflow.                                                  |


## 09 — Recommended architecture — migrated request, sequence view

09

A concrete walk-through of a request whose wfengine still says 'camunda' , being force-migrated via the Option 2 mechanism (the reserve path from §7), reusing syncwfinstance 's existing reconciliation shape.

```text
sequenceDiagram
    participant Caller as requestservice.py
    participant WS as workflowservice
    participant RE as workflowengine.resolve_engine
    participant DB as FOI Postgres (source of truth)
    participant CW as commonworkflowservice
    participant DT as Common Workflow Data Table

    Caller->>WS: postopenedevent(id, wfinstanceid, ...)
    WS->>DB: read wfengine for this request
    DB-->>WS: wfengine = 'camunda'
    WS->>WS: migration trigger fired for this row
    WS->>DB: read current + prior state history\n(FOIMinistryRequest.getstatesummary)
    DB-->>WS: derived "latest step" + activity
    WS->>CW: migratewfinstance(requestid, derived state)
    CW->>DT: search-by-requestid (dedupe check)
    DT-->>CW: not found
    CW->>CW: start n8n execution seeded\nat derived step
    CW->>DT: write Data Table row (requestid, step, wfinstanceid)
    CW-->>WS: n8n execution id
    WS->>DB: set wfengine='n8n', wfinstanceid=execution id
    WS->>RE: resolve_engine(wfengine='n8n')
    RE-->>WS: commonworkflowservice()
    WS->>CW: openedcomplete(...) for this event
    CW-->>WS: ack
```

## Implementation Notes / Open Questions

Grounded in the current codebase: bpmservice.py (Camunda operations), workflowservice.py (orchestration, ~15 call sites), camundaservice.py (auth base), and the wfinstanceid column on FOIRequests / FOIRawRequests . Worth confirming with the team before implementation: Common Workflow's actual auth model (webhook token vs OAuth, to shape commonworkflowbase.py ), and whether its Data Tables support an indexed lookup by request id cheaply enough for the dedupe check in §8.