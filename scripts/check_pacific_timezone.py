#!/usr/bin/env python3
"""Read-only FOIMOD-5453 checks for the providers loaded by a Python service.

Run with the service's own Python interpreter, or pipe this file to ``python -B -``
inside its container. The script does not change clocks, TZPATH or application
configuration. A failed installed provider (including effective system zoneinfo)
returns a nonzero exit code, even when the packaged tzdata checks pass.
"""

import argparse
from datetime import datetime, timezone
import importlib
from importlib import metadata, resources
import json
import os
import sys


ZONE = "America/Vancouver"
CASES = (
    ("historical_winter", "2025-01-15T20:00:00Z", "2025-01-15 12:00:00"),
    ("winter_before_change", "2026-01-15T20:00:00Z", "2026-01-15 12:00:00"),
    ("spring_before", "2026-03-08T09:59:59Z", "2026-03-08 01:59:59"),
    ("spring_after", "2026-03-08T10:00:00Z", "2026-03-08 03:00:00"),
    ("no_fall_back_before", "2026-11-01T08:59:59Z", "2026-11-01 01:59:59"),
    ("no_fall_back_after", "2026-11-01T09:00:00Z", "2026-11-01 02:00:00"),
    ("local_midnight", "2026-11-03T07:30:00Z", "2026-11-03 00:30:00"),
    ("receipt_cutoff", "2026-11-02T23:31:00Z", "2026-11-02 16:31:00"),
    ("future_winter", "2027-01-15T19:00:00Z", "2027-01-15 12:00:00"),
)


def package_version(name):
    try:
        return metadata.version(name)
    except metadata.PackageNotFoundError:
        return None


def load_optional(name):
    """Only an absent top-level optional module is a skip; broken imports fail."""
    try:
        return importlib.import_module(name)
    except ModuleNotFoundError as error:
        if error.name == name or (name == "backports.zoneinfo" and error.name == "backports"):
            return None
        raise


def load_converter(name):
    if name in ("pytz", "maya", "pendulum"):
        module = load_optional(name)
        if module is None:
            return None
        if name == "pytz":
            zone = module.timezone(ZONE)
            return lambda instant, raw: instant.astimezone(zone)
        if name == "maya":
            return lambda instant, raw: module.parse(raw).datetime(to_timezone=ZONE, naive=False)
        return lambda instant, raw: module.parse(raw).in_timezone(ZONE)

    zoneinfo = load_optional("zoneinfo") or load_optional("backports.zoneinfo")
    if zoneinfo is None:
        return None
    if name == "zoneinfo_effective":
        zone = zoneinfo.ZoneInfo(ZONE)
    else:
        if load_optional("tzdata") is None:
            return None
        # Read this package directly without overriding the effective lookup path.
        with resources.open_binary("tzdata.zoneinfo.America", "Vancouver") as source:
            zone = zoneinfo.ZoneInfo.from_file(source, key=ZONE)
    return lambda instant, raw: instant.astimezone(zone)


def check_provider(name, required=False):
    try:
        convert = load_converter(name)
    except Exception as error:
        return {"provider": name, "status": "error", "error": str(error)}
    if convert is None:
        return {"provider": name, "status": "missing" if required else "not_installed"}

    checks = []
    for label, raw, expected in CASES:
        try:
            instant = datetime.fromisoformat(raw.replace("Z", "+00:00"))
            converted = convert(instant, raw)
            actual = converted.strftime("%Y-%m-%d %H:%M:%S")
            # A matching wall clock is insufficient if the represented instant changed.
            same_instant = converted.utcoffset() is not None and converted.astimezone(timezone.utc) == instant
            checks.append({"case": label, "utc": raw, "expected": expected,
                           "actual": actual, "pass": actual == expected and same_instant})
        except Exception as error:
            checks.append({"case": label, "utc": raw, "expected": expected,
                           "error": str(error), "pass": False})
    passed = sum(check["pass"] for check in checks)
    return {"provider": name, "status": "pass" if passed == len(checks) else "fail",
            "passed": passed, "total": len(checks), "checks": checks}


def main():
    providers = ("pytz", "maya", "pendulum", "zoneinfo_effective", "tzdata_package")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require", nargs="+", choices=providers, default=["pytz"],
                        help="Providers that must be installed; every installed provider is still checked.")
    args = parser.parse_args()
    zoneinfo = load_optional("zoneinfo") or load_optional("backports.zoneinfo")
    print(json.dumps({"runtime": {"python": sys.version.split()[0], "zone": ZONE,
          "TZ": os.environ.get("TZ"), "PYTHONTZPATH": os.environ.get("PYTHONTZPATH"),
          "zoneinfo_search_path": list(zoneinfo.TZPATH) if zoneinfo else None,
          "versions": {name: package_version(name) for name in
                       ("pytz", "maya", "pendulum", "pytzdata", "tzdata", "backports.zoneinfo")}}}, sort_keys=True))
    results = [check_provider(name, name in args.require) for name in providers]
    for result in results:
        print(json.dumps(result, sort_keys=True))
    failures = [result["provider"] for result in results
                if result["status"] in ("fail", "error", "missing")]
    print(json.dumps({"summary": {"pass": not failures, "failed_providers": failures}}, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
