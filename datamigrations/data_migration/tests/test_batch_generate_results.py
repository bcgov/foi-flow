from pathlib import Path

from batch_generate_results import (
    build_output_path,
    collect_pending_request_files,
    iter_request_csvs,
    run,
)


def test_iter_request_csvs_returns_sorted_request_files(tmp_path: Path) -> None:
    (tmp_path / "BETA_requests.csv").write_text("request_id\nBETA-2024-00001\n", encoding="utf-8")
    (tmp_path / "ALPHA_requests.csv").write_text("request_id\nALPHA-2024-00001\n", encoding="utf-8")
    (tmp_path / "ALPHA_results.csv").write_text("request_id,status\n", encoding="utf-8")

    assert [path.name for path in iter_request_csvs(tmp_path)] == [
        "ALPHA_requests.csv",
        "BETA_requests.csv",
    ]


def test_collect_pending_request_files_skips_existing_outputs(tmp_path: Path) -> None:
    alpha = tmp_path / "ALPHA_requests.csv"
    beta = tmp_path / "BETA_requests.csv"
    alpha.write_text("request_id\nALPHA-2024-00001\n", encoding="utf-8")
    beta.write_text("request_id\nBETA-2024-00001\n", encoding="utf-8")
    (tmp_path / "ALPHA_results.csv").write_text("request_id,status\n", encoding="utf-8")

    assert [path.name for path in collect_pending_request_files(tmp_path, limit=10)] == [
        "BETA_requests.csv",
    ]


def test_collect_pending_request_files_uses_default_limit_of_three(tmp_path: Path) -> None:
    for name in ["ALPHA", "BETA", "GAMMA", "DELTA"]:
        (tmp_path / f"{name}_requests.csv").write_text(
            f"request_id\n{name}-2024-00001\n",
            encoding="utf-8",
        )

    assert [path.name for path in collect_pending_request_files(tmp_path)] == [
        "ALPHA_requests.csv",
        "BETA_requests.csv",
        "DELTA_requests.csv",
    ]


def test_build_output_path_replaces_requests_suffix(tmp_path: Path) -> None:
    assert build_output_path(tmp_path / "CFD_requests.csv") == tmp_path / "CFD_results.csv"


def test_run_processes_only_missing_result_files(tmp_path: Path) -> None:
    for name in ["ALPHA", "BETA", "GAMMA", "DELTA"]:
        (tmp_path / f"{name}_requests.csv").write_text(
            f"request_id\n{name}-2024-00001\n",
            encoding="utf-8",
        )

    (tmp_path / "ALPHA_results.csv").write_text("request_id,status\n", encoding="utf-8")

    calls: list[list[str]] = []

    def fake_runner(argv: list[str]) -> int:
        calls.append(argv)
        return 0

    exit_code = run([str(tmp_path)], command_runner=fake_runner)

    assert exit_code == 0
    assert calls == [
        [
            "--input-csv",
            str(tmp_path / "BETA_requests.csv"),
            "--output-csv",
            str(tmp_path / "BETA_results.csv"),
            "--skip-suffix-requests",
        ],
        [
            "--input-csv",
            str(tmp_path / "DELTA_requests.csv"),
            "--output-csv",
            str(tmp_path / "DELTA_results.csv"),
            "--skip-suffix-requests",
        ],
        [
            "--input-csv",
            str(tmp_path / "GAMMA_requests.csv"),
            "--output-csv",
            str(tmp_path / "GAMMA_results.csv"),
            "--skip-suffix-requests",
        ],
    ]


def test_run_honors_custom_limit(tmp_path: Path) -> None:
    for name in ["ALPHA", "BETA", "GAMMA"]:
        (tmp_path / f"{name}_requests.csv").write_text(
            f"request_id\n{name}-2024-00001\n",
            encoding="utf-8",
        )

    calls: list[list[str]] = []

    def fake_runner(argv: list[str]) -> int:
        calls.append(argv)
        return 0

    exit_code = run([str(tmp_path), "--limit", "1"], command_runner=fake_runner)

    assert exit_code == 0
    assert calls == [
        [
            "--input-csv",
            str(tmp_path / "ALPHA_requests.csv"),
            "--output-csv",
            str(tmp_path / "ALPHA_results.csv"),
            "--skip-suffix-requests",
        ],
    ]
