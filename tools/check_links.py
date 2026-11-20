#!/usr/bin/env python3
"""檢查維護文件之間的相對連結指得到東西。

本 fork 的公開入口互相連來連去：FORK、NOTICE、AGENTS 與 docs。
文件被重新定位或改名時，這些連結會靜靜斷掉。只驗相對連結；外部網址交給人看。
根目錄 `README.md` 是 1000+ API 目錄，只掃頂端 fork 自己寫的說明：
`<!-- fork-notice:start -->` 到 `<!-- fork-notice:end -->` 之間。標記不見時報錯，
避免同步上游時把它弄丟、檢查卻靜靜變成空轉。`scripts/README.md` 整份都掃。

    python tools/check_links.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
LINK_PATTERN = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
SKIP_PREFIXES = ("http://", "https://", "mailto:", "tel:", "#")
# Code is not prose: a link written inside a fence or backticks is an example.
FENCED_CODE = re.compile(
    r"^ {0,3}(`{3,}|~{3,})[^\n]*\n.*?(?:^ {0,3}\1[`~]*[ \t]*$|\Z)",
    re.DOTALL | re.MULTILINE,
)
BACKTICK_RUN = re.compile(r"`+")
# Kept by re.split (capturing group) so paragraphs stay apart after stripping.
PARAGRAPH_BREAK = re.compile(r"(\n[ \t]*\n)")

# The root README is the upstream catalog; only the fork-authored notice at its
# top is ours to check.
CATALOG_README = "README.md"
FORK_NOTICE_START = "<!-- fork-notice:start -->"
FORK_NOTICE_END = "<!-- fork-notice:end -->"

SKIP_RELATIVE = {
    "upstream-review-report.md",
}


def strip_code_spans(text: str) -> str:
    """Remove CommonMark code spans.

    A backtick run opens a span that closes only on the next run of exactly
    the same length in the same paragraph. A run with no such closer is
    literal text, so the prose after it (and any link there) is still checked.
    """
    return "".join(_strip_paragraph(part) for part in PARAGRAPH_BREAK.split(text))


def _strip_paragraph(text: str) -> str:
    runs = list(BACKTICK_RUN.finditer(text))
    kept: list[str] = []
    position = 0
    index = 0
    while index < len(runs):
        width = len(runs[index].group())
        closer = next(
            (j for j in range(index + 1, len(runs)) if len(runs[j].group()) == width),
            None,
        )
        if closer is None:
            index += 1
            continue
        kept.append(text[position : runs[index].start()])
        position = runs[closer].end()
        index = closer + 1
    kept.append(text[position:])
    return "".join(kept)


def iter_documents() -> list[Path]:
    documents = []
    documents.extend(ROOT.glob("*.md"))
    documents.extend((ROOT / "docs").glob("*.md"))
    github = ROOT / ".github"
    if github.is_dir():
        documents.extend(github.rglob("*.md"))
    scripts_readme = ROOT / "scripts" / "README.md"
    if scripts_readme.is_file():
        documents.append(scripts_readme)
    return sorted(
        path
        for path in documents
        if path.is_file() and path.relative_to(ROOT).as_posix() not in SKIP_RELATIVE
    )


def link_destination(raw: str) -> str:
    """The path of `[x](path "title")`; `<...>` allows spaces in the path."""
    raw = raw.strip()
    if raw.startswith("<") and ">" in raw:
        return raw[1 : raw.index(">")].strip()
    return raw.split(None, 1)[0] if raw else ""


def _relative(path: Path) -> str | None:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return None


def check_document(path: Path) -> list[str]:
    problems: list[str] = []
    text = path.read_text(encoding="utf-8")
    if _relative(path) == CATALOG_README:
        start = text.find(FORK_NOTICE_START)
        end = text.find(FORK_NOTICE_END, start + 1)
        if start < 0 or end < 0:
            return [
                f"找不到 {FORK_NOTICE_START} … {FORK_NOTICE_END} 標記；"
                "fork 說明的連結因此沒有被檢查"
            ]
        text = text[start + len(FORK_NOTICE_START) : end]
    text = strip_code_spans(FENCED_CODE.sub("", text))
    for match in LINK_PATTERN.finditer(text):
        target = link_destination(match.group(1))
        if not target or target.startswith(SKIP_PREFIXES):
            continue
        file_part = unquote(target.split("#", 1)[0])
        if not file_part:
            continue
        if file_part.startswith("/"):
            resolved = (ROOT / file_part.lstrip("/")).resolve()
        else:
            resolved = (path.parent / file_part).resolve()
        if not resolved.is_relative_to(ROOT):
            problems.append(f"{target} → 連結逃出 repo 根目錄")
            continue
        if not resolved.exists():
            try:
                shown = resolved.relative_to(ROOT)
            except ValueError:
                shown = resolved
            problems.append(f"{target} → 找不到 {shown}")
    return problems


def main() -> int:
    documents = iter_documents()
    if not documents:
        print("找不到任何維護用 Markdown 檔")
        return 1

    failures = 0
    for path in documents:
        problems = check_document(path)
        rel = path.relative_to(ROOT)
        if problems:
            failures += 1
            for problem in problems:
                print(f"FAIL {rel}: {problem}")
        else:
            print(f"OK   {rel}")

    print(f"\n共 {len(documents)} 份文件，{failures} 份有斷掉的相對連結。")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
