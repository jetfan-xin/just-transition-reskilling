#!/usr/bin/env python3
"""Fail on common private-research files, local paths, secrets or PII."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLOCKED_SUFFIXES = {
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".sav",
    ".dta",
    ".pdf",
    ".zip",
    ".rar",
    ".m4a",
    ".wav",
}
TEXT_SUFFIXES = {
    "",
    ".md",
    ".py",
    ".json",
    ".csv",
    ".txt",
    ".yml",
    ".yaml",
    ".gitignore",
    ".cff",
}
SENSITIVE_CSV_FIELDS = {
    "order",
    "time_spent",
    "company",
    "company_more",
    "loan_amount",
    "entry_time",
}
SKIP_PARTS = {".git", ".pytest_cache", ".ruff_cache", ".venv", "__pycache__"}


def public_files():
    for path in ROOT.rglob("*"):
        if not path.is_file() or SKIP_PARTS.intersection(path.parts):
            continue
        yield path


def main():
    failures = []
    disallowed_year = "20" + "26"
    patterns = {
        "macOS user path": re.compile(re.escape("/" + "Users/")),
        "mounted-volume path": re.compile(re.escape("/" + "Volumes/")),
        "Windows drive path": re.compile(r"[A-Za-z]:\\\\"),
        "email address": re.compile(
            r"(?<![\w.+-])[\w.+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
        ),
        "Chinese mobile number": re.compile(
            r"(?<![A-Za-z0-9])1[3-9][0-9]{9}(?![A-Za-z0-9])"
        ),
        "GitHub token": re.compile("g" + "ho_[A-Za-z0-9]{20,}"),
        "OpenAI-style key": re.compile("s" + "k-[A-Za-z0-9_-]{20,}"),
    }

    files = list(public_files())
    for path in files:
        relative = path.relative_to(ROOT)
        if path.suffix.lower() in BLOCKED_SUFFIXES:
            failures.append(f"blocked research/archive file: {relative}")
        if path.name.startswith("~$") or "source-index" in path.name.lower():
            failures.append(f"temporary or private index file: {relative}")
        if path.stat().st_size > 5 * 1024 * 1024:
            failures.append(f"file exceeds 5 MiB public-release limit: {relative}")
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text()
        except UnicodeDecodeError:
            try:
                text = path.read_text(encoding="gb18030")
            except UnicodeDecodeError:
                failures.append(f"unreadable text encoding: {relative}")
                continue
        for label, pattern in patterns.items():
            if pattern.search(text):
                failures.append(f"{label}: {relative}")
        if disallowed_year in text:
            failures.append(f"disallowed year marker: {relative}")
        if path.suffix.lower() == ".csv":
            header = {
                field.strip().lower() for field in text.splitlines()[0].split(",")
            }
            leaked = header.intersection(SENSITIVE_CSV_FIELDS)
            if leaked:
                failures.append(
                    f"respondent-level field(s) {sorted(leaked)}: {relative}"
                )
            if len(text.splitlines()) > 500:
                failures.append(f"unexpectedly large public CSV: {relative}")

    if failures:
        raise SystemExit("Public-release audit failed:\n- " + "\n- ".join(failures))
    print(
        f"PASS: public-release audit scanned {len(files)} files; no blocked data, local paths, secrets or common PII patterns found."
    )


if __name__ == "__main__":
    main()
