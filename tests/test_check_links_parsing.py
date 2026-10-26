"""Markdown link syntax that check_links must read the way a renderer does."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import check_links  # noqa: E402


def _check(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, text: str) -> list[str]:
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "real.md").write_text("x", encoding="utf-8")
    doc = tmp_path / "doc.md"
    doc.write_text(text, encoding="utf-8")
    monkeypatch.setattr(check_links, "ROOT", tmp_path.resolve())
    return check_links.check_document(doc.resolve())


def test_link_with_title_is_checked_against_the_path_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert _check(tmp_path, monkeypatch, '[a](docs/real.md "Real doc")\n') == []


def test_link_with_title_still_reports_a_missing_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    problems = _check(tmp_path, monkeypatch, "[a](docs/gone.md 'T')\n")
    assert len(problems) == 1 and "docs/gone.md" in problems[0]


def test_links_inside_code_are_examples_not_links(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    text = "```md\n[x](docs/example-only.md)\n```\n\nUse `[y](nope.md)` syntax.\n"
    assert _check(tmp_path, monkeypatch, text) == []
