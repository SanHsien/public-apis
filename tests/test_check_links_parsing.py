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


def test_lone_backtick_does_not_pair_with_a_longer_backtick_run(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The single backtick has no single-backtick closer (``cmd`` is a run of
    # two), so CommonMark renders it literally and the link stays a link.
    text = "Press the ` key, see [x](gone.md), then run ``cmd``.\n"
    problems = _check(tmp_path, monkeypatch, text)
    assert len(problems) == 1 and "gone.md" in problems[0]


def test_lone_backtick_closed_by_a_later_single_backtick_is_a_code_span(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # CommonMark (checked with markdown-it-py 4.2.0) pairs the stray backtick
    # with the next single backtick, so this "link" renders as code.
    text = "Press the ` key, see [x](gone.md), then run `cmd`.\n"
    assert _check(tmp_path, monkeypatch, text) == []


def test_code_span_closes_only_on_an_equal_length_backtick_run(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # ``a ` [x](nope.md)`` is one code span: the single backtick inside does
    # not close a double-backtick opener.
    assert _check(tmp_path, monkeypatch, "Use `` a ` [x](nope.md) `` here.\n") == []


def test_unclosed_double_backtick_does_not_hide_a_broken_link(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    text = "An `` unclosed run, [x](gone.md), and `ok` code.\n"
    problems = _check(tmp_path, monkeypatch, text)
    assert len(problems) == 1 and "gone.md" in problems[0]


def _readme(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, text: str) -> list[str]:
    (tmp_path / "FORK.md").write_text("x", encoding="utf-8")
    readme = tmp_path / "README.md"
    readme.write_text(text, encoding="utf-8")
    monkeypatch.setattr(check_links, "ROOT", tmp_path.resolve())
    return check_links.check_document(readme.resolve())


def test_readme_fork_notice_links_are_checked(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    text = (
        f"{check_links.FORK_NOTICE_START}\n"
        "See [FORK.md](FORK.md) and [NOTICE.md](NOTICE.md).\n"
        f"{check_links.FORK_NOTICE_END}\n"
    )
    problems = _readme(tmp_path, monkeypatch, text)
    assert len(problems) == 1 and "NOTICE.md" in problems[0]


def test_readme_catalog_below_the_fork_notice_is_not_checked(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    text = (
        f"{check_links.FORK_NOTICE_START}\n[FORK.md](FORK.md)\n"
        f"{check_links.FORK_NOTICE_END}\n\n[catalog](upstream-owned/gone.md)\n"
    )
    assert _readme(tmp_path, monkeypatch, text) == []


def test_readme_without_fork_notice_markers_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # A sync that drops the marker block must not turn the check into a no-op.
    problems = _readme(tmp_path, monkeypatch, "[FORK.md](FORK.md)\n")
    assert len(problems) == 1 and "fork-notice" in problems[0]
