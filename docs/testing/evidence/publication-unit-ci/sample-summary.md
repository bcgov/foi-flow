## Publication service unit tests

Result: **PASS**

Tested commit: 871a3e549adc36e48c11d1dcdf0c7fea86503c33
PR head: not applicable
Toolchain / platform: go1\.25\.0 / linux/amd64
Started (UTC): 2026\-10\-08T04:32:05Z
Test-command wall duration: 30 seconds

| Scope | Started | Passed | Failed | Skipped | Executed (pass + fail) |
| --- | ---: | ---: | ---: | ---: | ---: |
| Top-level tests | 179 | 179 | 0 | 0 | 179 |
| Subtests (separate) | 51 | 51 | 0 | 0 | 51 |
| Packages | 22 | 22 | 0 | 0 | 22 |

Scope: publication-service ./..., default build tags (integration excluded), package-local statement coverage; not repository-wide coverage.
No coverage threshold is applied. Skips do not satisfy the nonzero execution gate.

Command: go test \-count=1 \-timeout=5m \-json \-coverprofile=REPORT\_DIRECTORY/coverage\.out \./\.\.\.

Scoped statement coverage: **52.2%** (920/1762 statements).

Artifacts: run.json, tests.jsonl, coverage.out, coverage.txt, coverage.html, summary.json, summary.md.
Per-test and per-package durations, statuses and bounded failure diagnostics are in summary.json; full output is in tests.jsonl.
