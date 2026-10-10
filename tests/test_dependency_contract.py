"""Offline regressions for the maintained dependency and workflow contracts."""

from __future__ import annotations

import sys
from importlib import metadata
from pathlib import Path
from unittest.mock import patch

import pytest
import requests
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "scripts" / "validate"))

import check_dependency_freshness as freshness  # noqa: E402
import links  # noqa: E402


def workflow(name: str) -> dict:
    # BaseLoader keeps YAML 1.1 from converting GitHub Actions' `on` to True.
    return yaml.load(
        (ROOT / ".github" / "workflows" / name).read_text(encoding="utf-8"),
        Loader=yaml.BaseLoader,
    )


@pytest.mark.parametrize("name", ["ci.yml", "codeql.yml", "upstream-check.yml",
                                  "dependency-freshness.yml"])
def test_maintained_push_targets_main(name: str) -> None:
    assert workflow(name)["on"]["push"]["branches"] == ["main"]


@pytest.mark.parametrize("name", ["ci.yml", "codeql.yml", "dependency-freshness.yml"])
def test_maintained_pr_targets_main(name: str) -> None:
    assert workflow(name)["on"]["pull_request"]["branches"] == ["main"]


def test_freshness_scans_validator_manifest_and_pr_checkout() -> None:
    config = workflow("dependency-freshness.yml")
    for event in ("push", "pull_request"):
        assert "scripts/requirements.txt" in config["on"][event]["paths"]
    checkout = config["jobs"]["check"]["steps"][0]
    assert "ref" not in checkout.get("with", {})
    packages = freshness.load_direct_dependencies()
    validators = {item["name"] for item in packages
                  if item["source"] == "scripts/requirements.txt"}
    assert validators == {"requests", "urllib3", "certifi", "charset-normalizer", "idna"}


def test_development_installs_exact_validator_dependencies() -> None:
    assert "-r scripts/requirements.txt" in (
        ROOT / "requirements-dev.txt"
    ).read_text(encoding="utf-8")
    for package in freshness.parse_requirements(
        (ROOT / "scripts" / "requirements.txt").read_text(encoding="utf-8"),
        "scripts/requirements.txt",
    ):
        assert metadata.version(package["name"]) == package["minimum"]


def test_current_requests_reaches_validator_without_external_network() -> None:
    response = requests.Response()
    response.status_code = 200
    response.url = "https://example.invalid/"
    with patch.object(requests.Session, "send", return_value=response) as send:
        assert links.check_if_link_is_working(response.url) == (False, "")
    assert send.call_count == 1
    assert send.call_args.args[0].url == response.url


def test_freshness_reports_script_pin_updates_offline() -> None:
    packages = freshness.load_direct_dependencies()
    with patch.object(freshness, "fetch_pypi_version", return_value="999.0.0"):
        rows = freshness.collect_status(packages)
    urllib3_row = next(row for row in rows if row["name"] == "urllib3")
    assert urllib3_row["outdated"] is True
    assert "scripts/requirements.txt" in freshness.render_markdown(rows)
