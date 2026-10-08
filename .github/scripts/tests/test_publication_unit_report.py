"""Synthetic evidence verifies that reporting failures cannot produce a green check."""

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "publication_unit_report.py"
SPEC = importlib.util.spec_from_file_location("publication_unit_report", SCRIPT)
REPORT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REPORT)


def event(action, test="", **extra):
    return {"Action": action, "Package": "example.test/unit", **({"Test": test} if test else {}), **extra}


class PublicationUnitReportTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.metadata = {"commit_sha": "a" * 40, "pr_head_sha": "", "event_name": "local",
                         "go_version": "go1.25.0", "goos": "linux", "goarch": "amd64",
                         "command": "go test -count=1 -timeout=5m -json -coverprofile=coverage.out ./...",
                         "started_at": "2026-01-01T00:00:00Z", "duration_seconds": 1.5,
                         "test_exit_code": 0, "coverage_text_exit_code": 0, "coverage_html_exit_code": 0}
        self.write("run.json", json.dumps(self.metadata))
        self.events = [event("start"), event("run", "TestSynthetic"),
                       event("pass", "TestSynthetic", Elapsed=0.1), event("pass", Elapsed=0.2)]
        self.write_events()
        self.write("coverage.out", "mode: set\nexample.test/unit/unit.go:1.1,2.2 2 1\nexample.test/unit/unit.go:3.1,4.2 2 0\n")
        self.write("coverage.txt", "example.test/unit/unit.go:1: Example 50.0%\ntotal: (statements) 50.0%\n")
        self.write("coverage.html", "<!DOCTYPE html><html><body>Synthetic coverage</body></html>\n")

    def write(self, name, contents):
        (self.directory / name).write_text(contents, encoding="utf-8")

    def write_events(self):
        self.write("tests.jsonl", "\n".join(json.dumps(entry) for entry in self.events) + "\n")

    def assert_failure(self, expected):
        summary = REPORT.generate(self.directory)
        self.assertEqual(summary["status"], "fail")
        self.assertIn(expected, "\n".join(summary["errors"]))
        self.assertTrue((self.directory / "summary.json").is_file())
        self.assertTrue((self.directory / "summary.md").is_file())
        return summary

    def test_success_counts_subtests_separately_and_preserves_durations(self):
        self.events[2:2] = [event("run", "TestSynthetic/case"), event("pass", "TestSynthetic/case", Elapsed=0.05),
                            event("run", "TestSkipped"), event("skip", "TestSkipped", Elapsed=0)]
        self.write_events()
        summary = REPORT.generate(self.directory)
        self.assertEqual(summary["status"], "pass", summary["errors"])
        self.assertEqual(summary["top_level_tests"], {"started": 2, "passed": 1, "failed": 0, "skipped": 1, "executed": 1})
        self.assertEqual(summary["subtests"]["passed"], 1)
        self.assertEqual(summary["coverage"]["percent"], 50)
        self.assertEqual(summary["package_results"][0]["duration_seconds"], 0.2)
        self.assertEqual(summary["tests"][1]["duration_seconds"], 0.05)

    def test_failed_test_with_zero_exit_code_still_fails(self):
        self.events.insert(2, event("output", "TestSynthetic", Output="synthetic assertion failed\n"))
        self.events[3] = event("fail", "TestSynthetic", Elapsed=0.1)
        self.events[-1] = event("fail", Elapsed=0.2)
        self.write_events()
        summary = self.assert_failure("Failed: example.test/unit/TestSynthetic")
        self.assertEqual(summary["top_level_tests"]["failed"], 1)
        self.assertIn("synthetic assertion", summary["failures"][0]["output"])

    def test_build_failure_and_package_failure_are_rejected(self):
        self.events += [{"Action": "build-output", "ImportPath": "example.test/broken", "Output": "synthetic build failure"},
                        {"Action": "build-fail", "ImportPath": "example.test/broken"},
                        {"Action": "fail", "Package": "example.test/broken", "FailedBuild": "example.test/broken"}]
        self.write_events()
        summary = self.assert_failure("Build failed: example.test/broken")
        self.assertEqual(summary["packages"]["started"], 1)
        self.assertEqual(summary["packages"]["failed"], 1)

    def test_no_test_packages_fail(self):
        self.events = [event("start"), event("pass", Elapsed=0.1)]
        self.write_events()
        self.assert_failure("Zero top-level tests executed")

    def test_all_skipped_is_not_execution(self):
        self.events[2] = event("skip", "TestSynthetic", Elapsed=0)
        self.write_events()
        summary = self.assert_failure("Zero top-level tests executed")
        self.assertEqual(summary["top_level_tests"]["skipped"], 1)

    def test_unfinished_test_or_package_fails(self):
        for removed in (2, 3):
            with self.subTest(removed=removed):
                original = self.events[:]
                del self.events[removed]
                self.write_events()
                self.assert_failure("Unfinished run")
                self.events = original

    def test_malformed_or_truncated_events_fail(self):
        for suffix in ('{"Action":', '{"Action":"future-action","Package":"example.test/unit"}\n', '[]\n'):
            with self.subTest(suffix=suffix):
                self.write_events()
                with (self.directory / "tests.jsonl").open("a", encoding="utf-8") as handle:
                    handle.write(suffix)
                self.assert_failure("tests.jsonl line")

    def test_missing_or_empty_artifacts_fail(self):
        for name in REPORT.ARTIFACTS:
            original = (self.directory / name).read_text(encoding="utf-8")
            with self.subTest(missing=name):
                (self.directory / name).unlink()
                self.assert_failure("Missing or unreadable artifact: " + name)
            with self.subTest(empty=name):
                self.write(name, "")
                self.assert_failure("Missing or empty artifact: " + name)
            self.write(name, original)

    def test_nonzero_exit_codes_fail(self):
        for field in ("test_exit_code", "coverage_text_exit_code", "coverage_html_exit_code"):
            with self.subTest(field=field):
                self.write("run.json", json.dumps({**self.metadata, field: 1}))
                self.assert_failure(field + "=1")

    def test_bad_or_missing_metadata_fails(self):
        for field, value in (("commit_sha", "wrong"), ("go_version", "go1.24.0"), ("duration_seconds", -1),
                             ("started_at", "yesterday"), ("test_exit_code", False)):
            with self.subTest(field=field):
                self.write("run.json", json.dumps({**self.metadata, field: value}))
                self.assert_failure("run.json:")
        self.write("run.json", "{}")
        self.assert_failure("missing or invalid")
        self.write("run.json", "[")
        self.assert_failure("Malformed run.json")

    def test_invalid_coverage_reports_fail(self):
        for profile in ("mode: set\n", "mode: set\nmalformed\n", "mode: count\nunit.go:1.1,2.2 1 1\n"):
            with self.subTest(profile=profile):
                self.write("coverage.out", profile)
                self.assert_failure("Coverage report invalid")

    def test_inconsistent_coverage_or_incomplete_html_fails(self):
        self.write("coverage.txt", "total: (statements) 99.9%\n")
        self.assert_failure("inconsistent")
        self.write("coverage.html", "<html>truncated")
        self.assert_failure("Malformed coverage.html")

    def test_cli_returns_failure_and_appends_safe_markdown(self):
        self.metadata["command"] = "go test <script>alert(1)</script> [link](https://invalid.example)"
        self.metadata["test_exit_code"] = 1
        self.write("run.json", json.dumps(self.metadata))
        github_summary = self.directory / "github-summary.md"
        result = subprocess.run([sys.executable, str(SCRIPT), "--report-dir", str(self.directory),
                                 "--github-summary", str(github_summary)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1, result.stderr)
        rendered = github_summary.read_text(encoding="utf-8")
        self.assertIn("&lt;script&gt;", rendered)
        self.assertNotIn("<script>", rendered)
        self.assertIn(r"\[link\]", rendered)


if __name__ == "__main__":
    unittest.main()
