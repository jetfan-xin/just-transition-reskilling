#!/usr/bin/env python3
"""Derive privacy-safe scenario aggregates from the private merged export.

This is a retrospective reconstruction of the aggregate audit, not recovered
historical analysis code. It prints no respondent rows and writes only grouped
counts.
"""

import argparse
import collections
import csv
import hashlib
import json
from pathlib import Path

SCENARIOS = (
    ("control", "sc1"),
    ("training", "sc2"),
    ("wage_protection", "sc3"),
    ("employment_support", "sc4"),
)


def read_csv(path):
    raw = path.read_bytes()
    for encoding in ("utf-8-sig", "gb18030"):
        try:
            text = raw.decode(encoding)
            return raw, list(csv.DictReader(text.splitlines()))
        except UnicodeDecodeError:
            continue
    raise ValueError("Unsupported CSV encoding")


def build_summary(source, source_id):
    raw, rows = read_csv(source)
    if not rows:
        raise ValueError("Source CSV contains no data rows")
    required = {"order", *(field for _, field in SCENARIOS)}
    missing = required.difference(rows[0])
    if missing:
        raise ValueError("Missing required fields: " + ", ".join(sorted(missing)))

    records = []
    excluded = []
    for row in rows:
        values = [row[field].strip() for _, field in SCENARIOS]
        if row["order"].strip().isdigit():
            active = [value for value in values if value]
            if len(active) != 1 or active[0] not in {"1", "2", "3", "4", "5"}:
                raise ValueError(
                    "A retained record does not have one valid scenario rating"
                )
            records.append(row)
        else:
            if any(values):
                raise ValueError("An unidentified row contains a scenario response")
            excluded.append(row)

    groups = []
    for group_id, field in SCENARIOS:
        counts = collections.Counter(row[field].strip() for row in records)
        ratings = [counts[str(value)] for value in range(1, 6)]
        groups.append(
            {
                "id": group_id,
                "source_field": field,
                "n": sum(ratings),
                "rating_counts": ratings,
                "willing_n": sum(ratings[3:]),
            }
        )

    return {
        "schema_version": 1,
        "source_id": source_id,
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "kind": "retrospective_aggregate_check_not_model_rerun",
        "source_data_rows": len(rows),
        "excluded_non_record_rows": len(excluded),
        "total_records": len(records),
        "eligibility_rule": (
            "Numeric order identifier and exactly one populated scenario rating "
            "from 1 to 5; confirms the retained export, not the original "
            "survey-cleaning process."
        ),
        "rating_labels": {
            "1": "Very unwilling",
            "2": "Unwilling",
            "3": "Undecided",
            "4": "Willing",
            "5": "Very willing",
        },
        "groups": groups,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_csv", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source-id", default="S08")
    args = parser.parse_args()

    payload = build_summary(args.source_csv, args.source_id)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n")
    print(
        f"Wrote {args.output}: {payload['total_records']} retained records, "
        f"{len(payload['groups'])} scenarios; no respondent rows exported."
    )


if __name__ == "__main__":
    main()
