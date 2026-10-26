"""--strict must agree with --github-output about an empty parse."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import check_dependency_freshness as freshness  # noqa: E402


def test_freshness_strict_fails_when_no_requirement_was_parsed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # --github-output already reports check_failed for zero rows; --strict must agree.
    monkeypatch.setattr(freshness, "load_direct_dependencies", lambda: [])
    monkeypatch.setattr(sys, "argv", ["x", "--strict", "--output", str(tmp_path / "r.md")])
    assert freshness.main() == 1
