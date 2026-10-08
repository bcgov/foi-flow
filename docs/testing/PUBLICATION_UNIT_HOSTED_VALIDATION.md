# Publication unit workflow: PR and hosted validation

This is hosted evidence for [implementation PR #6393](https://github.com/bcgov/foi-flow/pull/6393), separate from the [initial local baseline](PUBLICATION_UNIT_CI.md). No application code, existing tests, deployment workflow or branch protection is changed.

## Tracked dependencies and review scope

Implementation commit `956af16e929435acdec1dfce2ccb883314a81952` includes the workflow, Bash runner, Python reporter, reporter regression tests and `.github/scripts/.gitattributes`. `publication-service/go.mod` and `go.sum` were already tracked. `git ls-tree` verified every referenced local dependency; the Bash file has `text eol=lf`. Official action dependencies remain pinned to immutable commits. The isolated review worktree excludes all earlier API repairs and broad audit documents. Those local audit references are described as context rather than broken links.

## First hosted baseline and cold cache

[Run 37731003835](https://github.com/bcgov/foi-flow/actions/runs/37731003835), triggered by opening PR #6393, completed successfully on 2026-10-08 UTC. GitHub ran `ubuntu-24.04` with Go `1.25.0`; all 13 reporter regression tests passed in 0.081 seconds.

| Evidence | Observed result |
| --- | --- |
| PR head | `956af16e929435acdec1dfce2ccb883314a81952` |
| Checked-out/tested merge commit | `3ec6b7d99f3443a710956b90cc2a1ddd24e5e17e` |
| Top-level passed / failed / skipped | 179 / 0 / 0 |
| Subtest passed / failed / skipped | 51 / 0 / 0 |
| Package results / packages executing tests | 22 / 17 |
| Statement coverage | 920 / 1762 = 52.2134% (display 52.2%), package-local/default tags |
| Test-command wall duration | 39 seconds, including dependency download/build |
| Full job duration | 62 seconds; run page displayed 1m 6s including scheduling |
| Cache evidence | setup-go logged `Cache is not found`; stderr recorded dependency downloads; cache saved only after success |
| Artifact | `publication-unit-3ec6b7d99f3443a710956b90cc2a1ddd24e5e17e-1`, ID `11530095225`, 78,641 compressed bytes |

The downloaded artifact contains `run.json`, `tests.jsonl`, `summary.json`, `summary.md`, raw/function/HTML coverage and diagnostic logs. Its metadata matches the PR API and checkout log. The reporter successfully appended the hosted step summary and its complete Markdown is also in the artifact. The anonymous browser confirms success and artifact identity; the authenticated job-summary rendering still needs a maintainer UI check because that view is not exposed in the available unsigned-in browser.

The unchanged dynamic image workflow also ran: [37731004491](https://github.com/bcgov/foi-flow/actions/runs/37731004491). Service detection succeeded, while build/push and notification jobs were skipped. No registry or deployment operation ran.

## Remaining hosted validation in progress

Disposable [validation PR #6394](https://github.com/bcgov/foi-flow/pull/6394) targets `ci/publication-unit-tests`, not a maintained branch. Its only tracked diff is a temporary workflow exercising the unchanged helpers. It will be closed without merging after evidence is collected. Runtime-only probes cover a deliberate synthetic Go assertion failure, removal of the generated HTML report after a normal suite, and a separate temporary Go module with no tests and an honestly recorded synthetic Git identity. No production behavior or existing assertion is changed.

Concurrency validation will supersede one active documentation-only run of the actual implementation workflow. Cold-cache execution is verified above; subsequent success, cancellation, probe statuses and artifact checks will be recorded here once observed. A failed setup, unrelated infrastructure error or cancellation does not count as a successful negative probe.

## Branch introduction and maintainer actions

The default `main` revision is `871a3e549adc36e48c11d1dcdf0c7fea86503c33`; reviewed `dev` is `d333c30e96964257612cd49832d5a6d92a5dfd45`. Go sources/tests/manifests match, but their Dockerfile and delivery workflow histories differ. [CONTRIBUTING.md](https://github.com/bcgov/foi-flow/blob/871a3e549adc36e48c11d1dcdf0c7fea86503c33/CONTRIBUTING.md) supports maintainer-reviewed PRs and still names the historical `master`; it does not establish a current dev-first rule. The existing main-to-dev synchronization [PR #6258](https://github.com/bcgov/foi-flow/pull/6258) is outside this task.

Recommend reviewing this main-based change first, then opening a separate dev-based cherry-pick PR for the reviewed commits. Do not retarget this branch to dev or merge unrelated branch differences. Maintainers must confirm the promotion order and review both PRs. No deployment or branch-rule changes are needed for this optional check. Separate validation is still required for dev, fork permissions/approvals, and any future merge queue. Retain the observation and negative-case readiness criteria in the local implementation note before an administrator makes the check mandatory.
