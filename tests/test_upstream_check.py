from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from unittest import mock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import check_upstream_updates as checker  # noqa: E402


# R-07: equivalent to repo-fleet-ops tools/canonical/check_upstream_updates_test.py
# RunnerFailures and test_garbled_git_log_output_is_a_check_error_not_a_crash
# (canonical revision c1190760483a7da96d135809cd6fe4efe693baf4).
def test_run_git_wraps_missing_executable() -> None:
    with mock.patch.object(
        checker.subprocess, "run", side_effect=FileNotFoundError("git")
    ), pytest.raises(checker.UpstreamCheckError, match="could not run"):
        checker.run_git(["status"], Path("."))


def test_run_git_wraps_timeout() -> None:
    with mock.patch.object(
        checker.subprocess, "run", side_effect=subprocess.TimeoutExpired("git", 1)
    ), pytest.raises(checker.UpstreamCheckError, match="timed out"):
        checker.run_git(["fetch"], Path("."))


@pytest.mark.parametrize("raw", ["no separators here\n", "sha\x1f2026-11-24\n"])
def test_garbled_git_log_output_is_a_check_error_not_a_crash(raw: str) -> None:
    with mock.patch.object(checker, "run_git", return_value=raw) as run:
        with pytest.raises(checker.UpstreamCheckError, match="unexpected `git log` line"):
            checker.collect_new_commits({"reviewed_through": "a" * 40}, Path("."), "HEAD")
    # Reject the malformed record before trying to read files from a bogus commit.
    assert run.call_count == 1
    assert run.call_args.args[0][0] == "log"


def test_baseline_file_is_valid_and_complete() -> None:
    baseline = checker.load_baseline()

    assert baseline["repo"].endswith("public-apis.git")
    assert baseline["branch"] == "master"
    assert len(baseline["reviewed_through"]) == 40
    assert baseline["reviewed_date"]


def test_workflow_is_scheduled_and_fails_on_unreviewed_commits() -> None:
    workflow = (
        Path(__file__).parents[1] / ".github" / "workflows" / "upstream-check.yml"
    ).read_text(encoding="utf-8")

    assert "schedule:" in workflow
    assert "cron:" in workflow
    assert "workflow_dispatch:" in workflow
    assert "tools/check_upstream_updates.py" in workflow
    assert "fetch-depth: 0" in workflow
    assert "exit 1" in workflow


def test_render_markdown_reports_no_new_commits() -> None:
    baseline = {
        "repo": "https://example.invalid/upstream.git",
        "branch": "master",
        "reviewed_through": "a" * 40,
        "reviewed_date": "2026-08-22",
    }

    report = checker.render_markdown(baseline, [])

    assert "No new upstream commits" in report


def test_render_markdown_surfaces_check_failure() -> None:
    baseline = {
        "repo": "https://example.invalid/upstream.git",
        "branch": "master",
        "reviewed_through": "a" * 40,
        "reviewed_date": "2026-08-22",
    }

    report = checker.render_markdown(baseline, [], error="git fetch failed")

    assert "Check failed" in report
    assert "git fetch failed" in report


def test_load_baseline_rejects_missing_file(tmp_path: Path) -> None:
    with pytest.raises(checker.UpstreamCheckError):
        checker.load_baseline(tmp_path / "nope.json")


def test_baseline_matches_decisions_record() -> None:
    decisions = (
        Path(__file__).parents[1] / "docs" / "DECISIONS.md"
    ).read_text(encoding="utf-8")
    baseline = json.loads(
        (Path(__file__).parents[1] / "tools" / "upstream_baseline.json").read_text(
            encoding="utf-8"
        )
    )

    assert baseline["reviewed_date"] in decisions
    assert baseline["reviewed_through"][:7] in (
        Path(__file__).parents[1] / "docs" / "UPSTREAM.md"
    ).read_text(encoding="utf-8")
