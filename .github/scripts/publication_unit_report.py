#!/usr/bin/env python3
"""Validate uncached Go unit-test evidence; emit a report even on failure."""

import argparse
import datetime
import html
import json
import math
from pathlib import Path
import re


SCOPE = ("publication-service ./..., default build tags (integration excluded), "
         "package-local statement coverage; not repository-wide coverage")
ARTIFACTS = ("run.json", "tests.jsonl", "coverage.out", "coverage.txt", "coverage.html")
TERMINAL = {"pass", "fail", "skip"}


def number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def markdown(value):
    """Render untrusted event/metadata text as inert, single-line Markdown."""
    value = html.escape(str(value)).replace("\n", " ").replace("\r", " ")
    return re.sub(r"([\\`*_\[\]{}()#+.!|\-])", r"\\\1", value)


def validate_metadata(metadata, errors):
    if not isinstance(metadata, dict):
        errors.append("run.json must contain an object")
        return {}
    for field in ("commit_sha", "event_name", "go_version", "goos", "goarch", "command", "started_at"):
        if not isinstance(metadata.get(field), str) or not metadata[field].strip():
            errors.append(f"run.json: missing or invalid {field}")
    for field in ("commit_sha", "pr_head_sha"):
        value = metadata.get(field)
        if not isinstance(value, str) or not (field == "pr_head_sha" and value == "") and not re.fullmatch(r"[0-9a-f]{40}", value):
            errors.append(f"run.json: invalid {field}")
    if metadata.get("event_name") == "pull_request" and not metadata.get("pr_head_sha"):
        errors.append("run.json: pull_request requires pr_head_sha")
    if metadata.get("go_version") != "go1.25.0":
        errors.append("run.json: expected Go go1.25.0")
    try:
        started = datetime.datetime.fromisoformat(metadata.get("started_at", "").replace("Z", "+00:00"))
        if started.utcoffset() != datetime.timedelta(0):
            raise ValueError("not UTC")
    except (TypeError, ValueError, AttributeError):
        errors.append("run.json: started_at must be a UTC ISO timestamp")
    value = metadata.get("duration_seconds")
    if not number(value) or value < 0:
        errors.append("run.json: duration_seconds must be nonnegative and finite")
    for field in ("test_exit_code", "coverage_text_exit_code", "coverage_html_exit_code"):
        value = metadata.get(field)
        if type(value) is not int:
            errors.append(f"run.json: missing or invalid {field}")
        elif value != 0:
            errors.append(f"run.json: {field}={value}")
    return metadata


def parse_events(raw, errors):
    tests, packages, output, build_failures = {}, {}, {}, []
    actions = TERMINAL | {"start", "run", "pause", "cont", "output", "build-output", "build-fail"}
    for line_number, line in enumerate(raw.splitlines(), 1):
        try:
            event = json.loads(line)
            if not isinstance(event, dict) or event.get("Action") not in actions:
                raise ValueError("invalid or unknown event Action")
            action = event["Action"]
            package = event.get("Package", event.get("ImportPath"))
            name = event.get("Test", "")
            if not isinstance(package, str) or not package or not isinstance(name, str):
                raise ValueError("missing/invalid package or test name")
            key = (package, name)
            if action in {"output", "build-output"}:
                if not isinstance(event.get("Output"), str):
                    raise ValueError("invalid Output")
                output[key] = (output.get(key, "") + event["Output"])[-4000:]
                continue
            if action == "build-fail":
                build_failures.append({"package": package, "name": "", "status": "build-fail"})
                errors.append(f"Build failed: {package}")
                continue
            records = tests if name else packages
            identity = key if name else package
            if action in {"start", "run"}:
                if (name and action != "run") or (not name and action != "start"):
                    raise ValueError("incorrect start/run event")
                if identity in records:
                    raise ValueError("duplicate run; expected -count=1")
                records[identity] = {"package": package, "name": name, "started": True,
                                     "status": "running", "duration_seconds": None}
            elif action in TERMINAL:
                if identity not in records:
                    # Build failures may terminate a package without a start event.
                    if name or action != "fail":
                        raise ValueError("terminal event without start/run")
                    records[identity] = {"package": package, "name": name, "started": False,
                                         "status": "running", "duration_seconds": None}
                record = records[identity]
                if record["status"] != "running":
                    raise ValueError("duplicate terminal event")
                elapsed = event.get("Elapsed")
                if elapsed is not None and (not number(elapsed) or elapsed < 0):
                    raise ValueError("invalid Elapsed")
                if elapsed is None and action == "pass":
                    raise ValueError("passing event missing Elapsed")
                record.update(status=action, duration_seconds=elapsed)
                if action == "fail":
                    errors.append(f"Failed: {package}" + (f"/{name}" if name else ""))
            elif not name or identity not in records or records[identity]["status"] != "running":
                raise ValueError("pause/cont without running test")
        except (json.JSONDecodeError, ValueError, TypeError) as exc:
            errors.append(f"tests.jsonl line {line_number}: {exc}")
    for record in list(tests.values()) + list(packages.values()):
        if record["status"] == "running":
            errors.append(f"Unfinished run: {record['package']}/{record['name']}")
    for record in tests.values():
        if record["package"] not in packages:
            errors.append(f"Missing package result: {record['package']}")
    failures = [record.copy() for record in list(tests.values()) + list(packages.values()) if record["status"] == "fail"]
    failures += build_failures
    for record in failures:
        record["output"] = output.get((record["package"], record["name"]), "")
    return list(tests.values()), list(packages.values()), failures


def counts(records):
    return {"started": sum(r["started"] for r in records), "passed": sum(r["status"] == "pass" for r in records),
            "failed": sum(r["status"] == "fail" for r in records),
            "skipped": sum(r["status"] == "skip" for r in records),
            "executed": sum(r["status"] in {"pass", "fail"} for r in records)}


def parse_coverage(profile, report, errors):
    try:
        lines = profile.splitlines()
        if not lines or lines[0] != "mode: set":
            raise ValueError("expected mode: set")
        covered, total = 0, 0
        for line in lines[1:]:
            match = re.fullmatch(r"(.+):(\d+)\.(\d+),(\d+)\.(\d+) (\d+) ([01])", line)
            if not match:
                raise ValueError("malformed statement block")
            start_line, start_col, end_line, end_col, statements, hits = map(int, match.groups()[1:])
            if min(start_line, start_col, end_line, end_col) < 1 or (end_line, end_col) < (start_line, start_col):
                raise ValueError("invalid statement block location")
            total += statements
            covered += statements if hits else 0
        if total == 0:
            raise ValueError("no statement blocks with statements")
        percentage = 100 * covered / total
        totals = re.findall(r"^total:\s+\(statements\)\s+(\d+(?:\.\d+)?)%\s*$", report, re.MULTILINE)
        if len(totals) != 1 or abs(float(totals[0]) - percentage) > 0.051:
            raise ValueError("coverage.txt total missing or inconsistent with coverage.out")
        return {"covered_statements": covered, "total_statements": total, "percent": round(percentage, 4)}
    except ValueError as exc:
        errors.append(f"Coverage report invalid: {exc}")
        return None


def render(summary):
    meta, coverage = summary["metadata"], summary["coverage"]
    rows = ["## Publication service unit tests", "", f"Result: **{summary['status'].upper()}**", "",
            f"Tested commit: {markdown(meta.get('commit_sha', 'unavailable'))}",
            f"PR head: {markdown(meta.get('pr_head_sha') or 'not applicable')}",
            f"Toolchain / platform: {markdown(meta.get('go_version', 'unavailable'))} / {markdown(meta.get('goos', '?'))}/{markdown(meta.get('goarch', '?'))}",
            f"Started (UTC): {markdown(meta.get('started_at', 'unavailable'))}",
            f"Test-command wall duration: {markdown(meta.get('duration_seconds', 'unavailable'))} seconds", "",
            "| Scope | Started | Passed | Failed | Skipped | Executed (pass + fail) |",
            "| --- | ---: | ---: | ---: | ---: | ---: |"]
    for label, field in (("Top-level tests", "top_level_tests"), ("Subtests (separate)", "subtests"), ("Packages", "packages")):
        count = summary[field]
        rows.append(f"| {label} | {count['started']} | {count['passed']} | {count['failed']} | {count['skipped']} | {count['executed']} |")
    rows += ["", f"Scope: {SCOPE}.", "No coverage threshold is applied. Skips do not satisfy the nonzero execution gate.", "",
             "Command: " + markdown(meta.get("command", "unavailable")), ""]
    if coverage:
        rows += [f"Scoped statement coverage: **{coverage['percent']:.1f}%** ({coverage['covered_statements']}/{coverage['total_statements']} statements).", ""]
    if summary["errors"]:
        rows += ["### Validation errors", ""] + ["- " + markdown(error) for error in summary["errors"]] + [""]
    rows += ["Artifacts: run.json, tests.jsonl, coverage.out, coverage.txt, coverage.html, summary.json, summary.md.",
             "Per-test and per-package durations, statuses and bounded failure diagnostics are in summary.json; full output is in tests.jsonl.", ""]
    return "\n".join(rows)


def generate(report_dir):
    errors, inputs = [], {}
    for name in ARTIFACTS:
        try:
            inputs[name] = (report_dir / name).read_text(encoding="utf-8-sig")
            if not inputs[name].strip():
                errors.append(f"Missing or empty artifact: {name}")
        except (OSError, UnicodeError):
            errors.append(f"Missing or unreadable artifact: {name}")
            inputs[name] = ""
    try:
        metadata = validate_metadata(json.loads(inputs["run.json"]), errors)
    except (json.JSONDecodeError, ValueError):
        errors.append("Malformed run.json")
        metadata = {}
    tests, packages, failures = parse_events(inputs["tests.jsonl"], errors)
    top_level = counts([record for record in tests if "/" not in record["name"]])
    if top_level["executed"] == 0:
        errors.append("Zero top-level tests executed (pass or fail); no-tests/all-skipped runs are failures")
    coverage = parse_coverage(inputs["coverage.out"], inputs["coverage.txt"], errors)
    if not re.search(r"<html(?:\s[^>]*)?>", inputs["coverage.html"], re.IGNORECASE) or not re.search(r"</html>", inputs["coverage.html"], re.IGNORECASE):
        errors.append("Malformed coverage.html: incomplete HTML document")
    summary = {"status": "fail" if errors else "pass", "errors": errors, "metadata": metadata,
               "scope": SCOPE, "top_level_tests": top_level,
               "subtests": counts([record for record in tests if "/" in record["name"]]),
               "packages": counts(packages), "tests": tests, "package_results": packages,
               "failures": failures, "coverage": coverage}
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (report_dir / "summary.md").write_text(render(summary), encoding="utf-8")
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report-dir", required=True, type=Path)
    parser.add_argument("--github-summary", type=Path)
    args = parser.parse_args()
    summary = generate(args.report_dir)
    if args.github_summary:
        with args.github_summary.open("a", encoding="utf-8") as handle:
            handle.write(render(summary))
    print(render(summary))
    return int(summary["status"] != "pass")


if __name__ == "__main__":
    raise SystemExit(main())
