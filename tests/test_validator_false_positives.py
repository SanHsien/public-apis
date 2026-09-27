"""Regression tests for the two validator false-positive classes.

A validator that reports 557 failures on a README nobody touched cannot gate
anything: the only way to use it is to ignore it. These tests pin the two causes
so the check keeps meaning "someone has to look".

Taken from upstream PR #7010 (public-apis/public-apis). Upstream's own unit
tests in `scripts/tests/` cover the entry rules; these cover what the scan
should never have been looking at in the first place.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "validate"))

import format as validator  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

ENTRY = "| [Name](https://example.com) | A description | `apiKey` | Yes | Yes |"


def test_a_colon_aligned_separator_row_is_not_an_api_entry() -> None:
    """Every table in README.md writes `|:---|`, not `|---`.

    The old guard only recognised `|---`, so all 45 separator rows were parsed
    as entries and each produced five bogus column errors.
    """
    assert validator.is_table_row("|:---|:---|:---|:---|:---|") is False
    assert validator.is_table_row("|---|---|---|---|---|") is False
    assert validator.is_table_row("| --- | --- |") is False
    assert validator.is_table_row(ENTRY) is True
    assert validator.is_table_row("## Index") is False


def test_the_scan_is_bounded_to_the_api_listing() -> None:
    """Sponsor tables and the license footer are not five-column API entries."""
    lines = [
        "# Title",
        "| Sponsor | Blurb |",
        "|:---|:---|",
        "## Index",
        ENTRY,
        "## License",
        "| MIT | text |",
    ]

    start, end = validator.get_api_list_bounds(lines)

    assert lines[start] == "## Index"
    assert lines[end] == "## License"
    assert start < 4 < end


def test_bounds_fall_back_to_the_whole_file_when_headings_are_absent() -> None:
    """A fragment (the per-PR path passes changed files) must still be checked."""
    lines = [ENTRY, ENTRY]

    assert validator.get_api_list_bounds(lines) == (0, 2)


def test_the_real_readme_no_longer_produces_separator_errors() -> None:
    """The measurable half: 45 separator rows used to yield 225 column errors."""
    lines = (ROOT / "README.md").read_text(encoding="utf-8").splitlines()

    errors = validator.check_file_format(lines)

    assert not [error for error in errors if ":---" in error]


def test_link_checker_does_not_pin_the_host_header() -> None:
    """`requests` derives Host per hop; pinning it breaks cross-domain redirects.

    A pinned Host on the redirect target gets a 421 or loops to
    TooManyRedirects, which the checker reports as a broken link.
    """
    source = (ROOT / "scripts" / "validate" / "links.py").read_text(encoding="utf-8")

    assert "'host': get_host_from_link(link)" not in source
