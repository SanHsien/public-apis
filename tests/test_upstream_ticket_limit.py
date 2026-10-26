"""A gh listing cut off at --limit must not be reported as a complete triage list."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import check_upstream_updates as upstream  # noqa: E402


def _stub_gh(monkeypatch: pytest.MonkeyPatch, items: list[dict]) -> None:
    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(args, 0, stdout=json.dumps(items), stderr="")

    monkeypatch.setattr(upstream.subprocess, "run", fake_run)


def test_ticket_listing_that_hit_the_gh_limit_is_not_reported_as_complete(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # gh returns newest-first and stops at --limit; when every row returned is
    # above the watermark, older unreviewed items may have been cut off.
    limit = 1000  # the --limit tools/check_upstream_updates.py passes to gh
    _stub_gh(monkeypatch, [{"number": 5000 + n, "title": "t"} for n in range(limit)])
    baseline = {"repo": "https://github.com/o/n.git", "reviewed_pr_through": 10}
    assert upstream.collect_new_tickets(baseline, "pr") is None


def test_ticket_listing_below_the_limit_is_returned(monkeypatch: pytest.MonkeyPatch) -> None:
    _stub_gh(monkeypatch, [{"number": 12, "title": "a"}, {"number": 3, "title": "b"}])
    baseline = {"repo": "https://github.com/o/n.git", "reviewed_pr_through": 10}
    assert upstream.collect_new_tickets(baseline, "pr") == [{"number": 12, "title": "a"}]
