"""Execute the workflow tracker offline for each event and checker result."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]

# Wall-clock cap for one Git Bash run of the tracker body. It only exists to
# stop a hung shell; it is not a performance assertion. Measured on the
# Windows dev box (2026-11-21, 24 logical CPUs): idle full-suite runs take
# 0.16-1.04 s per case; with the CPU oversubscribed 3x a case took up to
# 5.71 s; the 2026-11-20 review saw 13.42 s during a 187.8 s full run (idle:
# 4-9 s), and 4/16 cases failed at the old 15 s cap. The cost is MSYS process
# creation plus the body's command-substitution forks under host contention,
# which this test cannot remove without changing the workflow it executes.
# 120 s leaves ~9x headroom over the worst observed case.
BASH_TIMEOUT_SECONDS = float(os.environ.get("FRESHNESS_BASH_TIMEOUT_SECONDS", "120"))


@pytest.mark.parametrize("event", ["pull_request", "push", "schedule", "workflow_dispatch"])
@pytest.mark.parametrize("checker_attention", [False, True])
@pytest.mark.parametrize("open_count", [0, 1])
def test_freshness_tracker_event_semantics(
    tmp_path: Path, event: str, checker_attention: bool, open_count: int
) -> None:
    config = yaml.load(
        (ROOT / ".github/workflows/dependency-freshness.yml").read_text(encoding="utf-8"),
        Loader=yaml.BaseLoader,
    )
    steps = config["jobs"]["check"]["steps"]
    tracker = next(step for step in steps if step.get("id") == "tracker")
    assert tracker["env"]["EVENT_NAME"] == "${{ github.event_name }}"
    assert tracker["env"]["CHECKER_NEEDS_ATTENTION"] == (
        "${{ steps.deps.outputs.needs_attention }}"
    )
    final_step = steps[-1]
    assert final_step["if"] == "steps.tracker.outputs.needs_attention == 'true'"
    assert "exit 1" in final_step["run"]
    checker = next(step for step in steps if step.get("id") == "deps")
    assert "--github-output" in checker["run"]
    assert "continue-on-error" not in checker

    # Windows uses Git Bash; avoid the unrelated Windows/WSL bash launcher.
    bash = (Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Git/bin/bash.exe"
            if os.name == "nt" else Path(shutil.which("bash") or ""))
    assert bash.is_file(), "The workflow's bash interpreter must be available"
    output = tmp_path / "output.txt"
    summary = tmp_path / "summary.md"
    # Replace external gh/jq commands with deterministic shell functions.
    # Execute the actual workflow body, including its report/output writes.
    stubs = f"""
gh() {{ printf '%s\\n' '[{{"number":4,"title":"upgrade","url":"https://example.invalid/pr/4"}}]'; }}
jq() {{
  if [ "$1" = "length" ]; then
    printf '%s\\n' '{open_count}'
  else
    printf '%s\\n' '- [#4 upgrade](https://example.invalid/pr/4)'
  fi
}}
"""
    try:
        result = subprocess.run(
            [str(bash), "--noprofile", "--norc", "-e", "-o", "pipefail", "-c",
             stubs + tracker["run"]],
            cwd=tmp_path,
            env={**os.environ, "EVENT_NAME": event,
                 "CHECKER_NEEDS_ATTENTION": str(checker_attention).lower(),
                 "GITHUB_OUTPUT": output.as_posix(),
                 "GITHUB_STEP_SUMMARY": summary.as_posix()},
            stdin=subprocess.DEVNULL, capture_output=True, text=True,
            encoding="utf-8", timeout=BASH_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        # A timeout says nothing about the tracker's semantics; report it as
        # an incomplete run, never as an assertion about the workflow.
        pytest.fail(
            f"INCOMPLETE: Git Bash did not finish within {BASH_TIMEOUT_SECONDS:g} s "
            f"(FRESHNESS_BASH_TIMEOUT_SECONDS); host contention, not a tracker "
            f"result. stderr so far: {exc.stderr!r}",
            pytrace=False,
        )
    assert result.returncode == 0, result.stderr
    expected = checker_attention or (event != "pull_request" and open_count > 0)
    assert output.read_text(encoding="utf-8").strip() == (
        f"needs_attention={str(expected).lower()}"
    )
    report = (tmp_path / "dependency-freshness-report.md").read_text(encoding="utf-8")
    assert ("#4 upgrade" in report) == (open_count > 0)
    assert summary.read_text(encoding="utf-8") == report
