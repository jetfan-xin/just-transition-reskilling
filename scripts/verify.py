#!/usr/bin/env python3
"""Check the public research portfolio and its aggregate evidence chain.

Standard library only. Reads repository files and writes nothing.
"""

import collections
import csv
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_sources():
    manifest = json.loads((ROOT / "source-manifest.json").read_text())
    sources = {item["id"]: item for item in manifest["sources"]}
    require(len(sources) == 10, "Expected ten distinct evidence sources")
    require(
        set(sources) == {f"S{number:02d}" for number in range(1, 11)},
        "Unexpected source IDs",
    )
    for item in sources.values():
        require(
            re.fullmatch(r"[0-9a-f]{64}", item["sha256"]), "Invalid source fingerprint"
        )
    redistributed = [item for item in sources.values() if item["redistributed"]]
    require(
        [item["id"] for item in redistributed] == ["S05"],
        "Only S05 may be directly redistributed",
    )
    public_log = ROOT / redistributed[0]["public_path"]
    require(public_log.is_file(), "Redistributed S05 log is missing")
    require(
        digest(public_log) == sources["S05"]["sha256"],
        "S05 copy is not byte-for-byte exact",
    )
    return sources


def check_artifacts(sources):
    manifest = json.loads((ROOT / "artifact-manifest.json").read_text())
    require(
        len(manifest["artifacts"]) == 10, "Expected ten registered public artifacts"
    )
    seen = set()
    for item in manifest["artifacts"]:
        path = (ROOT / item["path"]).resolve()
        require(
            path.is_relative_to(ROOT) and path.is_file(),
            "Missing or external artifact path",
        )
        require(item["path"] not in seen, "Duplicate public artifact path")
        seen.add(item["path"])
        require(
            digest(path) == item["sha256"],
            "Public artifact fingerprint changed: " + item["path"],
        )
        require(
            item["contains_respondent_rows"] is False,
            "Respondent rows cannot be registered",
        )
        require(
            all(source_id in sources for source_id in item["source_ids"]),
            "Unknown artifact source",
        )
    generated = manifest["generated_figures"]["paths"]
    require(
        len(generated) == 5 and all((ROOT / path).is_file() for path in generated),
        "Generated figures are incomplete",
    )


def check_survey_summary(sources):
    summary = json.loads((ROOT / "results/survey-summary.json").read_text())
    require(summary["source_id"] == "S08", "Unexpected aggregate source")
    require(
        summary["source_sha256"] == sources["S08"]["sha256"],
        "Aggregate source fingerprint differs",
    )
    require(summary["total_records"] == 655, "Unexpected retained sample")
    require(
        sum(group["n"] for group in summary["groups"]) == 655, "Arm totals disagree"
    )
    require(
        summary["source_data_rows"] - summary["excluded_non_record_rows"] == 655,
        "Non-record row accounting disagrees",
    )
    require(len(summary["groups"]) == 4, "Expected four survey arms")
    expected = {
        "control": [7, 11, 59, 41, 51],
        "training": [15, 12, 56, 31, 50],
        "wage_protection": [9, 11, 35, 48, 55],
        "employment_support": [10, 9, 44, 46, 55],
    }
    for group in summary["groups"]:
        counts = group["rating_counts"]
        require(counts == expected[group["id"]], "Scenario rating distribution changed")
        require(sum(counts) == group["n"], "Ratings do not sum to arm total")
        require(
            sum(counts[3:]) == group["willing_n"], "Willingness threshold disagrees"
        )


def check_model_outputs(sources):
    with (ROOT / "results/model-metrics.csv").open(newline="") as handle:
        metrics = list(csv.DictReader(handle))
    require(len(metrics) == 3, "Keep the three historical result versions separate")
    expected = [(0.645, 0.707, None), (0.432, 0.538, 0.314), (0.445, 0.557, 0.329)]
    for row, values in zip(metrics, expected):
        require(None not in row, "Malformed metric row")
        require(
            all(source_id in sources for source_id in row["source_ids"].split(";")),
            "Unknown metric source",
        )
        for column, expected_value in zip(("accuracy", "auc", "f1"), values):
            actual = float(row[column]) if row[column] else None
            require(actual == expected_value, "Metric transcription changed: " + column)

    with (ROOT / "results/random-forest-feature-importance-11.csv").open(
        newline=""
    ) as handle:
        importance = list(csv.DictReader(handle))
    require(len(importance) == 11, "Expected eleven saved feature importances")
    require(
        [int(row["rank"]) for row in importance] == list(range(1, 12)),
        "Importance ranks are invalid",
    )
    values = [float(row["importance"]) for row in importance]
    require(
        values == sorted(values, reverse=True), "Saved feature importance is not sorted"
    )
    require(
        abs(sum(values) - 0.999999) < 1e-9, "Saved feature importance total changed"
    )
    require(
        importance[0]["feature"] == "age" and importance[3]["feature"] == "coal_policy",
        "Saved ranking changed",
    )

    audit = json.loads(
        (ROOT / "results/replication-random-forest-metrics.json").read_text()
    )
    require(audit["source_id"] == "S09", "Unexpected sensitivity-analysis source")
    require(
        audit["source_sha256"] == sources["S09"]["sha256"],
        "Sensitivity source fingerprint differs",
    )
    require(
        audit["record_count"] == 153 and audit["feature_count"] == 11,
        "Sensitivity input shape changed",
    )
    require(audit["validation"]["total_splits"] == 50, "Sensitivity validation changed")
    mapping = audit["target"]["recovered_mapping_to_original_five_point_scale"]
    require(
        mapping == {"2": 1, "4": 2, "6": 3, "8": 4, "9": 5},
        "Recovered target mapping changed",
    )
    model = audit["metrics"]["random_forest"]
    baseline = audit["metrics"]["most_frequent_baseline"]
    require(
        model["balanced_accuracy"]["mean"] > baseline["balanced_accuracy"]["mean"],
        "Model no longer beats baseline",
    )
    require(
        model["macro_f1"]["mean"] > baseline["macro_f1"]["mean"],
        "Model macro F1 no longer beats baseline",
    )

    with (ROOT / "results/replication-random-forest-permutation-importance.csv").open(
        newline=""
    ) as handle:
        held_out = list(csv.DictReader(handle))
    require(len(held_out) == 11, "Expected eleven held-out importance rows")
    require(
        {row["source_id"] for row in held_out} == {"S09"},
        "Unexpected held-out importance source",
    )


def check_reason_categories():
    with (ROOT / "results/open-text-reason-categories.csv").open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    groups = collections.defaultdict(list)
    for row in rows:
        groups[row["group"]].append(row)
        require(row["source_id"] == "S01", "Unexpected open-text category source")
    require(
        {group: len(values) for group, values in groups.items()}
        == {"willing": 12, "not_willing": 14},
        "Open-text category count changed",
    )
    for group, expected_total in (("willing", 122), ("not_willing", 88)):
        values = groups[group]
        require(
            sum(int(row["count"]) for row in values) == expected_total,
            "Open-text total changed",
        )
        require(
            {int(row["group_total"]) for row in values} == {expected_total},
            "Open-text denominator changed",
        )
        for row in values:
            require(
                abs(float(row["share"]) - int(row["count"]) / expected_total) < 1e-6,
                "Open-text share changed",
            )


def check_documentation():
    checked_links = 0
    disallowed_year = "20" + "26"
    for path in ROOT.rglob("*.md"):
        content = path.read_text()
        require(
            disallowed_year not in content,
            "Disallowed year marker in " + str(path.relative_to(ROOT)),
        )
        require(
            not re.search(r"[\u4e00-\u9fff]", content),
            "Explanatory prose must be English",
        )
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", content):
            parsed = urlsplit(target)
            if parsed.scheme or not parsed.path:
                continue
            linked = (path.parent / unquote(parsed.path)).resolve()
            require(
                linked.is_relative_to(ROOT) and linked.exists(),
                "Broken or external local link: " + target,
            )
            checked_links += 1
    return checked_links


def main():
    sources = check_sources()
    check_artifacts(sources)
    check_survey_summary(sources)
    check_model_outputs(sources)
    check_reason_categories()
    links = check_documentation()
    print(
        "PASS: 10 evidence sources, 10 registered public artifacts, 655 survey "
        f"records, 3 historical model versions and {links} local documentation links."
    )
    print(
        "Aggregate and provenance consistency only; historical model validity is not certified."
    )


if __name__ == "__main__":
    main()
