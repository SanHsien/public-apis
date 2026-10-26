"""A malformed baseline must raise UpstreamCheckError, not crash with a traceback."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import check_upstream_updates as upstream  # noqa: E402


@pytest.mark.parametrize(
    "content",
    [
        "null",
        "[]",
        '{"repo":"r","branch":"b","reviewed_through":null,"reviewed_date":"d"}',
        '{"repo":"r","branch":"b","reviewed_through":"%s","reviewed_date":"d",'
        '"reviewed_pr_through":"abc"}' % ("a" * 40),
    ],
)
def test_malformed_baseline_is_an_upstream_check_error(tmp_path: Path, content: str) -> None:
    path = tmp_path / "baseline.json"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(upstream.UpstreamCheckError):
        upstream.load_baseline(path)
