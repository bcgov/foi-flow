# Publication service PR unit tests

Implemented locally on 2026-10-08 UTC (2026-10-07 Pacific), against application revision `871a3e549adc36e48c11d1dcdf0c7fea86503c33`. **GitHub-hosted execution is not yet verified.** The workflow is proposed in this working tree; no remote workflow was dispatched, no changes were merged, and no branch settings were changed.

This implements the publication unit-test portion of T12 and the nonzero/reporting safeguards in T09. The starting references were the local audit documents `docs/testing/TESTING_AUDIT.md`, `OTHER_SERVICES_AUDIT.md`, `CI_TEST_STRATEGY.md`, and `TESTING_ROADMAP.md`. The broader audit is not bundled into this focused change. This note preserves the initial local-validation snapshot; subsequent PR and hosted-execution evidence is recorded separately in `docs/testing/PUBLICATION_UNIT_HOSTED_VALIDATION.md`. Retired testing assets remain entirely out of scope.

## Focused change

| File | Purpose |
| --- | --- |
| [publication-service-unit-tests.yml](../../.github/workflows/publication-service-unit-tests.yml) | Independent PR/manual workflow; no delivery dependencies or application secrets |
| [publication-unit-tests.sh](../../.github/scripts/publication-unit-tests.sh) | Exact toolchain check, uncached normal Go tests, coverage generation and run metadata |
| [publication_unit_report.py](../../.github/scripts/publication_unit_report.py) | Standard-library JSON-event validator and JSON/Markdown report generator |
| [test_publication_unit_report.py](../../.github/scripts/tests/test_publication_unit_report.py) | Synthetic regression cases for false-green reporting failures |
| [.gitattributes](../../.github/scripts/.gitattributes) | Preserve LF line endings for the Bash runner on Windows checkouts |

No existing Go test, assertion, fixture, production file, dependency manifest, or delivery/deployment workflow changed. Earlier API test repairs already present in the workspace belong to the preceding audit, not this change. Keep this file set and its evidence together in a focused PR.

The workflow runs on every PR targeting `main` or `dev`: `opened`, `synchronize`, `reopened`, `ready_for_review`, and `edited` (including retargeting). There is no path filter or draft exclusion, so documentation-only PRs also get a real result. A new run cancels the superseded run for that PR. The job name is **Publication unit tests (Go 1.25.0)** in **Publication Service Unit Tests**; it is not required yet. `workflow_dispatch` is available once the workflow is present on the default branch.

The runner is `ubuntu-24.04`, with Go exactly `1.25.0` from the existing `go.mod`. `GOTOOLCHAIN=local` prevents automatic toolchain upgrades, `GOENV=off` disables persisted Go settings, and `GOFLAGS=-mod=readonly` replaces inherited flags and prevents module rewrites. The normal command has no integration tag or test-name exclusion:

```bash
cd publication-service
go test -count=1 -timeout=5m -json -coverprofile=REPORT_DIRECTORY/coverage.out ./...
```

`-count=1` prevents cached test results. Dependency/build caches remain enabled. There are no test retries, ignored failures, `continue-on-error`, or coverage thresholds. The five-minute timeout applies to each package's test binary; the job has a fifteen-minute upper limit. No PostgreSQL, Redis, object-store service container, OpenShift CLI, registry login, deployment environment, or production endpoint is configured. Normal-tag tests use the existing local doubles and `httptest` servers. Docker is used only for local validation, not by this GitHub workflow.

The only token permission is `contents: read`, and checkout does not persist credentials. Official checkout, setup-go, and upload-artifact actions are pinned to verified immutable commits. Their references and verification sources are in [branch and action evidence](evidence/publication-unit-ci-branch-review.json). No PR comments or write permissions are needed. GitHub still supplies its ordinary checkout/cache/artifact infrastructure; “secret-free” means no configured repository/application secrets are required.

## Failure and artifact contract

The runner preserves the Go command's exit status while generating available diagnostic artifacts. A separate `always()` reporting step fails on a failed test/package/build event, nonzero command status, zero executed top-level tests, an all-skipped suite, unfinished/invalid event streams, invalid toolchain/SHA metadata, or missing/empty/invalid required reports. It also verifies the coverage text total against the raw profile. Skips are counted separately and do not satisfy the execution gate. The historical count of 179 is recorded as evidence, not hard-coded as a permanent ceiling or minimum.

Required inputs are `run.json`, `tests.jsonl`, `coverage.out`, `coverage.txt`, and `coverage.html`. The reporter writes `summary.json` and `summary.md`, appends Markdown to the job summary, and exits nonzero for invalid evidence. Failed execution steps remain failed even when later artifact steps succeed. A fresh output directory is required locally to prevent accidental reuse of an earlier run.

The `always()` upload retains the report directory for 14 days under `publication-unit-<tested SHA>-<run attempt>` and fails if it finds no files. It includes full Go JSON output, stderr/coverage diagnostics, metadata, summaries, raw coverage, function coverage, and HTML coverage. The summaries distinguish top-level tests, subtests, and package results. `summary.json` retains individual test/package durations and statuses, plus bounded failure diagnostics; full output remains in `tests.jsonl`. No real FOI data or credentials were added as fixtures.

Coverage is **package-local statement coverage for `publication-service ./...` with default tags**, without `-coverpkg=./...`. It is not repository-wide coverage or proof of integration, race, deployment, or browser behavior. Package success can include packages with no tests; the gate counts actual test events separately. The PR checkout normally tests GitHub's merge commit: `run.json` records the checked-out commit, verifies it against `GITHUB_SHA`, and separately records the PR head SHA.

If checkout/setup fails, the job fails and later steps attempt to report missing evidence. If the runner is terminated or GitHub artifact infrastructure is unavailable, complete artifacts cannot be guaranteed. Such a run is not a successful test result.

## Exact local validation

Both executions used the cached official `golang:1.25.0` image, digest `sha256:5502b0e56fca23feba76dbc5387ba59c593c02ccc2f0f7355871ea9a0852cebe`, on Linux/amd64 through Docker Desktop. Repository source was mounted read-only, test networking was disabled, and module/build caches were mounted from the earlier audit. These are **warm dependency/build-cache executions**, not fresh installs. Test results themselves were not cached.

| Result | Before: direct Go command | After: new runner + reporter |
| --- | ---: | ---: |
| Application commit | `871a3e549adc36e48c11d1dcdf0c7fea86503c33` | same unchanged application revision |
| Started UTC | `2026-10-08T04:26:05Z` | `2026-10-08T04:32:05Z` |
| Go test command exit | 0 | 0 |
| Top-level pass / fail / skip | 179 / 0 / 0 | 179 / 0 / 0 |
| Subtest pass / fail / skip | 51 / 0 / 0 | 51 / 0 / 0 |
| Package results / packages executing tests | 22 / 17 | 22 / 17 |
| Go-command wall duration, whole seconds | 22 | 30 |
| Scoped covered / total statements | 920 / 1762 | 920 / 1762 |
| Scoped coverage | 52.2134% (Go display 52.2%) | 52.2134% (Go display 52.2%) |

The 230 passing test-result events are **179 top-level tests plus 51 subtests**, not 230 independent top-level tests. Five of the 22 successful package results contain no test cases. The before timer also brackets `go version` and shell bookkeeping; neither timer includes container startup or coverage-report rendering. The timing difference is not a performance claim or evidence of a flake. Both runs passed without retries.

Additional validation:

- Reporter regression suite: **13 tests passed**, 0 failures/errors/skips, in **0.381 seconds** on Python 3.12.14. Cases exercise test/build/package failure, zero/all-skipped execution, missing/empty artifacts, malformed/truncated evidence, nonzero exits, and invalid coverage/metadata. CLI failure and job-summary rendering are exercised with synthetic data.
- `actionlint 1.7.12`: first run exited 1 because `runner.temp` was used in job-level `env`; fixed to the permitted `github.workspace` context. Final run exited 0 with no findings. This checks the new workflow only. ShellCheck/Pyflakes were unavailable and are not claimed.
- Bash syntax, complete offline runner execution, text/HTML coverage generation, and report CLI all passed. `summary.md` was successfully appended to a local stand-in for `GITHUB_STEP_SUMMARY`.
- Publication source/manifests/tests and existing delivery workflows have no diff. No application or pre-existing test defect was discovered in these two normal-suite runs.

Machine-readable counts, timestamps, artifact hashes and validation commands are in [validation.json](evidence/publication-unit-ci/validation.json). [Sample job summary](evidence/publication-unit-ci/sample-summary.md) is generated from the actual local after-run; its PR head is correctly “not applicable.” On GitHub the same format supplies the real tested merge SHA and PR head SHA. This sample is **not** a claimed hosted run.

### Reproduce the workflow commands

With Bash, git, Go 1.25.0 and Python 3 available, run from the repository root and choose a new empty report directory:

```bash
python3 -m unittest discover -s .github/scripts/tests -p test_publication_unit_report.py -v
bash .github/scripts/publication-unit-tests.sh /tmp/publication-unit-reports
python3 .github/scripts/publication_unit_report.py --report-dir /tmp/publication-unit-reports
```

When diagnosing a failure manually, run the reporter after the runner even if the runner fails, and retain both exit statuses. Do not interpret a successful upload or a subsequent shell command as overwriting the failed runner status.

The actual local before command (PowerShell; cache mounts already existed) was:

```powershell
docker run --rm --network none `
  --mount 'type=bind,source=C:\Projects\foi-flow-testing-rebuild\publication-service,target=/src,readonly' `
  --mount 'type=bind,source=C:\Projects\foi-flow-testing-rebuild\.audit-work\go-cache,target=/go' `
  --mount 'type=bind,source=C:\Projects\foi-flow-testing-rebuild\.audit-work\go-build,target=/root/.cache/go-build' `
  --mount 'type=bind,source=C:\Projects\foi-flow-testing-rebuild\.audit-work\publication-unit-ci\before,target=/reports' `
  -w /src golang:1.25.0 sh -c 'date -u +%Y-%m-%dT%H:%M:%SZ > /reports/started-at.txt; go version > /reports/runtime.txt; go test -count=1 -timeout=5m -json -coverprofile=/reports/coverage.out ./... > /reports/tests.jsonl 2> /reports/stderr.log; result=$?; printf "%s\n" "$result" > /reports/exit-code.txt; date -u +%Y-%m-%dT%H:%M:%SZ > /reports/finished-at.txt; exit "$result"'
```

The actual after command mounted the repository so the runner could obtain the source SHA:

```powershell
docker run --rm --network none `
  --mount 'type=bind,source=C:\Projects\foi-flow-testing-rebuild,target=/workspace,readonly' `
  --mount 'type=bind,source=C:\Projects\foi-flow-testing-rebuild\.audit-work\go-cache,target=/go' `
  --mount 'type=bind,source=C:\Projects\foi-flow-testing-rebuild\.audit-work\go-build,target=/root/.cache/go-build' `
  --mount 'type=bind,source=C:\Projects\foi-flow-testing-rebuild\.audit-work\publication-unit-ci\after,target=/reports' `
  -w /workspace golang:1.25.0 bash .github/scripts/publication-unit-tests.sh /reports

& 'C:\Users\User\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -B .github/scripts/publication_unit_report.py --report-dir .audit-work/publication-unit-ci/after --github-summary .audit-work/publication-unit-ci/job-summary.md
```

Full local raw reports remain in ignored `.audit-work/publication-unit-ci/before/` and `after/`. Before-run coverage text/HTML were generated afterward from its saved profile; this did not rerun the tests. `validation.json` records provenance. New workflow/helper files were uncommitted during local validation, so the application SHA is paired with implementation-file hashes rather than represented as a committed CI implementation.

## Branch differences and hosted limitations

Read-only public GitHub review found:

| Item | `main` at `871a3e549adc36e48c11d1dcdf0c7fea86503c33` | `dev` at `d333c30e96964257612cd49832d5a6d92a5dfd45` |
| --- | --- | --- |
| `.github/workflows/ci-build-images.yaml` PR base branches | `dev`, `main` | `dev`, `master` |
| Dynamic image workflow PR activity | opened, synchronize, ready_for_review | same |
| `.github/workflows/publication-service-ci.yaml` | Exists, publication path filter, PRs to dev/main; builds/pushes image | Absent |
| Proposed publication unit workflow | Not yet present remotely | Not yet present remotely |
| Publication Go source, tests, go.mod/go.sum | Byte-identical to reviewed dev files | Byte-identical to reviewed main files |
| Publication Dockerfile | Different from dev | Different from main |

Existing image workflows do not invoke this unit suite and remain unchanged. The new workflow does not depend on their outcome or credentials. Matching source hashes do not constitute a separate test execution on `dev`. Deliver the focused workflow and helpers to each maintained branch history through normal review; a `branches` filter does not distribute workflow files. Branch ownership/promotion policy is still an administrative decision from T01.

Local validation does not exercise GitHub event delivery, merge-checkout metadata, action downloads, cold Go-module downloads, cache restoration, hosted Python/runtime versions, artifact upload/retention, fork approval policy, or the PR checks UI. GitHub PR jobs also do not run for merge-conflicted PRs until conflicts are resolved. Organization action policies or first-time contributor approval can delay/block a run. The workflow has no `push` or `merge_group` trigger; direct pushes and merge queues are not covered by this proposal. Those are explicit limits, not successful checks.

## Criteria before making the check mandatory

Keep the job observational first. No branch protection was inspected as authoritative or modified during this focused task. Repository administrators should require the exact observed check name only after all of the following:

1. The workflow/helpers are reviewed and available for both supported branch histories. Owners confirm whether `main`/`dev` are the intended PR targets and how direct pushes or merge queues will be handled.
2. Real GitHub-hosted PR runs succeed for both base branches, same-repository and fork contributions, documentation-only changes, reopen/synchronize/retarget events, and the default merge checkout. Verify both SHAs, nonzero counts, summaries, complete downloadable artifacts, and absence of application secrets.
3. In disposable validation PRs, a deliberate failing test, a zero/all-skipped test stream, a missing required report, and a compile/setup failure each produce a failed check with appropriate diagnostics. Revert the probes; do not weaken or disable existing tests. Verify cancellation is never shown as a successful run.
4. Cold-cache and warm-cache runs complete within the time limit. Observe at least 20 representative hosted PR runs over two weeks with no unexplained flakes or missing reports, without automatic retries. Diagnose failures before enforcement; the sample size is an operational readiness criterion, not proof of statistical reliability.
5. A named maintainer owns toolchain/action updates, artifact access/retention and incidents; administrators review fork approvals and allowed-action policies. Confirm the displayed stable status-check name, then separately approve branch-rule changes and any bypass policy.

Integration tests, race detection, broader regressions, other services, and delivery changes remain separate roadmap items. No further repair work is included in this implementation.
