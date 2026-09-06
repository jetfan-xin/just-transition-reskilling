#!/usr/bin/env python3
"""Run a deterministic random-forest audit on the private control data.

This is a modern sensitivity analysis, not the missing 2023 training script.
Only aggregate metrics and feature importances are written; respondent rows and
predictions never leave the private source file.
"""

import argparse
import collections
import csv
import hashlib
import json
import platform
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FEATURES = (
    "age",
    "marital",
    "lns",
    "educ_year",
    "un_ins_level",
    "coal_policy",
    "ambig_aver",
    "reason_dis",
    "reason_earning",
    "reason_major",
    "male",
)
TARGET_MAP = {"2": 1, "4": 2, "6": 3, "8": 4, "9": 5}


def read_private_csv(path, np):
    raw = path.read_bytes()
    rows = list(csv.DictReader(raw.decode("utf-8-sig").splitlines()))
    if not rows:
        raise ValueError("Private source contains no rows")
    required = {*FEATURES, "w2"}
    missing = required.difference(rows[0])
    if missing:
        raise ValueError("Missing required fields: " + ", ".join(sorted(missing)))
    if any(row["w2"].strip() not in TARGET_MAP for row in rows):
        raise ValueError(
            "Unexpected w2 code; expected the recovered five-level mapping"
        )
    matrix = np.asarray(
        [[float(row[name]) for name in FEATURES] for row in rows], dtype=float
    )
    target = np.asarray([TARGET_MAP[row["w2"].strip()] for row in rows], dtype=int)
    if not np.isfinite(matrix).all():
        raise ValueError("Feature matrix contains a missing or non-finite value")
    return raw, matrix, target


def summary(values, np):
    values = np.asarray(values, dtype=float)
    return {
        "mean": round(float(values.mean()), 6),
        "std": round(float(values.std(ddof=1)), 6),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_csv", type=Path)
    parser.add_argument(
        "--metrics-out",
        type=Path,
        default=ROOT / "results/replication-random-forest-metrics.json",
    )
    parser.add_argument(
        "--importance-out",
        type=Path,
        default=ROOT / "results/replication-random-forest-permutation-importance.csv",
    )
    parser.add_argument("--seed", type=int, default=20230301)
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--repeats", type=int, default=10)
    parser.add_argument("--trees", type=int, default=300)
    parser.add_argument("--permutation-repeats", type=int, default=10)
    args = parser.parse_args()

    try:
        import numpy as np
        import sklearn
        from sklearn.dummy import DummyClassifier
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.inspection import permutation_importance
        from sklearn.metrics import (
            accuracy_score,
            balanced_accuracy_score,
            f1_score,
            roc_auc_score,
        )
        from sklearn.model_selection import RepeatedStratifiedKFold
    except ImportError as exc:
        raise SystemExit(
            "Install the pinned audit environment first: "
            "python -m pip install -r requirements-replication.txt"
        ) from exc

    raw, matrix, target = read_private_csv(args.source_csv, np)
    classes = np.asarray([1, 2, 3, 4, 5], dtype=int)
    counts = collections.Counter(int(value) for value in target)
    if min(counts.values()) < args.folds:
        raise ValueError("Each outcome class must have at least one record per fold")

    splitter = RepeatedStratifiedKFold(
        n_splits=args.folds,
        n_repeats=args.repeats,
        random_state=args.seed,
    )
    metric_names = ("accuracy", "balanced_accuracy", "macro_f1", "macro_ovr_auc")
    model_metrics = {name: [] for name in metric_names}
    baseline_metrics = {name: [] for name in metric_names}
    importances = []

    def evaluate(model, x_test, y_test):
        prediction = model.predict(x_test)
        probabilities = model.predict_proba(x_test)
        ordered = np.zeros((len(y_test), len(classes)), dtype=float)
        for column, label in enumerate(model.classes_):
            ordered[:, np.flatnonzero(classes == label)[0]] = probabilities[:, column]
        return {
            "accuracy": accuracy_score(y_test, prediction),
            "balanced_accuracy": balanced_accuracy_score(y_test, prediction),
            "macro_f1": f1_score(y_test, prediction, average="macro", zero_division=0),
            "macro_ovr_auc": roc_auc_score(
                y_test,
                ordered,
                labels=classes,
                multi_class="ovr",
                average="macro",
            ),
        }

    for split_number, (train_index, test_index) in enumerate(
        splitter.split(matrix, target)
    ):
        split_seed = args.seed + split_number
        model = RandomForestClassifier(
            n_estimators=args.trees,
            min_samples_leaf=2,
            max_features="sqrt",
            class_weight="balanced_subsample",
            random_state=split_seed,
            n_jobs=1,
        )
        baseline = DummyClassifier(strategy="most_frequent")
        model.fit(matrix[train_index], target[train_index])
        baseline.fit(matrix[train_index], target[train_index])

        for name, value in evaluate(
            model, matrix[test_index], target[test_index]
        ).items():
            model_metrics[name].append(value)
        for name, value in evaluate(
            baseline, matrix[test_index], target[test_index]
        ).items():
            baseline_metrics[name].append(value)

        held_out = permutation_importance(
            model,
            matrix[test_index],
            target[test_index],
            scoring="balanced_accuracy",
            n_repeats=args.permutation_repeats,
            random_state=split_seed,
            n_jobs=1,
        )
        importances.append(held_out.importances_mean)

    importance_matrix = np.vstack(importances)
    importance_rows = []
    for column, feature in enumerate(FEATURES):
        values = importance_matrix[:, column]
        importance_rows.append(
            (
                feature,
                float(values.mean()),
                float(values.std(ddof=1)),
            )
        )
    importance_rows.sort(key=lambda row: row[1], reverse=True)

    payload = {
        "schema_version": 1,
        "analysis_type": "deterministic_sensitivity_analysis_not_historical_rerun",
        "source_id": "S09",
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "record_count": len(target),
        "feature_count": len(FEATURES),
        "features": list(FEATURES),
        "target": {
            "source_field": "w2",
            "recovered_mapping_to_original_five_point_scale": TARGET_MAP,
            "class_counts": {str(key): counts[key] for key in sorted(counts)},
        },
        "validation": {
            "method": "repeated_stratified_k_fold",
            "folds": args.folds,
            "repeats": args.repeats,
            "total_splits": args.folds * args.repeats,
            "seed": args.seed,
        },
        "estimator": {
            "name": "RandomForestClassifier",
            "n_estimators": args.trees,
            "min_samples_leaf": 2,
            "max_features": "sqrt",
            "class_weight": "balanced_subsample",
            "scaling": "none_tree_models_do_not_require_z_score_scaling",
        },
        "permutation_importance": {
            "scoring": "balanced_accuracy",
            "repeats_per_split": args.permutation_repeats,
            "output": args.importance_out.name,
        },
        "metrics": {
            "random_forest": {
                name: summary(values, np) for name, values in model_metrics.items()
            },
            "most_frequent_baseline": {
                name: summary(values, np) for name, values in baseline_metrics.items()
            },
        },
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scikit_learn": sklearn.__version__,
        },
        "interpretation_limit": (
            "Small non-probability control sample; exploratory association only. "
            "Metrics are not directly comparable with the undocumented 2023 runs."
        ),
    }

    args.metrics_out.parent.mkdir(parents=True, exist_ok=True)
    args.metrics_out.write_text(json.dumps(payload, indent=2) + "\n")
    args.importance_out.parent.mkdir(parents=True, exist_ok=True)
    with args.importance_out.open("w", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(
            (
                "rank",
                "feature",
                "mean_balanced_accuracy_decrease",
                "between_split_std",
                "source_id",
                "evidence_status",
            )
        )
        for rank, (feature, mean, std) in enumerate(importance_rows, 1):
            writer.writerow(
                (
                    rank,
                    feature,
                    f"{mean:.6f}",
                    f"{std:.6f}",
                    "S09",
                    "held_out_permutation_audit",
                )
            )

    print(
        f"Wrote aggregate audit outputs for {len(target)} records and "
        f"{args.folds * args.repeats} held-out splits; no predictions exported."
    )


if __name__ == "__main__":
    main()
