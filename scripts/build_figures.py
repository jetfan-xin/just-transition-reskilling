#!/usr/bin/env python3
"""Build deterministic, dependency-free SVG figures from public aggregates."""

import argparse
import csv
import html
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIGURES = (
    "scenario-willingness.svg",
    "random-forest-feature-importance-11.svg",
    "open-text-positive-reasons.svg",
    "open-text-negative-reasons.svg",
    "replication-permutation-importance.svg",
)
FEATURE_LABELS = {
    "age": "Age",
    "lns": "Log savings",
    "un_ins_level": "Unemployment-insurance awareness",
    "coal_policy": "Carbon-policy awareness",
    "educ_year": "Years of education",
    "ambig_aver": "Ambiguity-aversion score",
    "marital": "Marital-status encoding",
    "reason_dis": "Proximity motive",
    "reason_major": "Job/major fit motive",
    "male": "Gender indicator",
    "reason_earning": "Earnings motive",
}


def esc(value):
    return html.escape(str(value), quote=True)


def document(width, height, title, description, body):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
<title id="title">{esc(title)}</title>
<desc id="desc">{esc(description)}</desc>
<rect width="100%" height="100%" fill="#ffffff"/>
<style>
text {{ font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif; fill: #172033; }}
.title {{ font-size: 30px; font-weight: 700; }}
.subtitle {{ font-size: 16px; fill: #526079; }}
.label {{ font-size: 16px; }}
.small {{ font-size: 13px; fill: #526079; }}
.value {{ font-size: 14px; font-weight: 650; }}
.axis {{ stroke: #b8c1d1; stroke-width: 1; }}
.grid {{ stroke: #e7eaf0; stroke-width: 1; }}
</style>
{body}
</svg>
'''


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def scenario_figure(output):
    payload = json.loads((ROOT / "results/survey-summary.json").read_text())
    labels = {
        "control": "Policy background",
        "training": "Training",
        "wage_protection": "Wage protection",
        "employment_support": "Employment support",
    }
    colors = ("#b42318", "#e66a4e", "#d9dee8", "#4fa58b", "#087f5b")
    x0, chart_width = 285, 720
    body = [
        '<text x="60" y="55" class="title">Willingness by policy scenario</text>',
        '<text x="60" y="84" class="subtitle">Verified five-point responses; n = 655</text>',
    ]
    legend_x = 60
    for rating, color in enumerate(colors, 1):
        body.append(
            f'<rect x="{legend_x}" y="110" width="16" height="16" rx="2" fill="{color}"/>'
        )
        body.append(f'<text x="{legend_x + 22}" y="123" class="small">{rating}</text>')
        legend_x += 73
    body.append(
        '<text x="442" y="123" class="small">1 = very unwilling · 5 = very willing</text>'
    )

    for index, group in enumerate(payload["groups"]):
        y = 176 + index * 105
        body.append(
            f'<text x="60" y="{y + 24}" class="label">{esc(labels[group["id"]])}</text>'
        )
        body.append(f'<text x="60" y="{y + 47}" class="small">n = {group["n"]}</text>')
        cursor = x0
        for count, color in zip(group["rating_counts"], colors):
            width = chart_width * count / group["n"]
            body.append(
                f'<rect x="{cursor:.2f}" y="{y}" width="{width:.2f}" height="48" fill="{color}"/>'
            )
            if width >= 45:
                share = 100 * count / group["n"]
                text_color = "#ffffff" if color != "#d9dee8" else "#172033"
                body.append(
                    f'<text x="{cursor + width / 2:.2f}" y="{y + 30}" '
                    f'text-anchor="middle" class="value" fill="{text_color}" style="fill:{text_color}">{share:.0f}%</text>'
                )
            cursor += width
        willing_share = 100 * group["willing_n"] / group["n"]
        body.append(
            f'<text x="{x0 + chart_width + 25}" y="{y + 22}" class="value">{willing_share:.1f}%</text>'
        )
        body.append(
            f'<text x="{x0 + chart_width + 25}" y="{y + 43}" class="small">ratings 4–5</text>'
        )

    for tick in range(0, 101, 20):
        x = x0 + chart_width * tick / 100
        body.append(f'<line x1="{x:.1f}" y1="590" x2="{x:.1f}" y2="600" class="axis"/>')
        body.append(
            f'<text x="{x:.1f}" y="622" text-anchor="middle" class="small">{tick}%</text>'
        )
    body.append(
        f'<line x1="{x0}" y1="590" x2="{x0 + chart_width}" y2="590" class="axis"/>'
    )
    body.append(
        '<text x="60" y="667" class="small">Descriptive shares only; scenarios were cumulative bundles and the outcome was stated willingness.</text>'
    )
    write(
        output / "scenario-willingness.svg",
        document(
            1200,
            700,
            "Willingness by policy scenario",
            "Four stacked bars show response distributions from very unwilling to very willing.",
            "\n".join(body),
        ),
    )


def feature_figure(output):
    with (ROOT / "results/random-forest-feature-importance-11.csv").open(
        newline=""
    ) as handle:
        rows = list(csv.DictReader(handle))
    x0, chart_width = 420, 620
    maximum = 0.21
    body = [
        '<text x="50" y="52" class="title">Legacy random-forest importance</text>',
        '<text x="50" y="81" class="subtitle">11-feature saved workbook · impurity-based importance</text>',
    ]
    for tick in (0, 0.05, 0.10, 0.15, 0.20):
        x = x0 + chart_width * tick / maximum
        body.append(f'<line x1="{x:.1f}" y1="112" x2="{x:.1f}" y2="670" class="grid"/>')
        body.append(
            f'<text x="{x:.1f}" y="696" text-anchor="middle" class="small">{tick:.2f}</text>'
        )
    for index, row in enumerate(rows):
        y = 120 + index * 49
        value = float(row["importance"])
        width = chart_width * value / maximum
        fill = "#087f5b" if index < 5 else "#5c7c9c"
        body.append(
            f'<text x="50" y="{y + 23}" class="label">{esc(FEATURE_LABELS.get(row["feature"], row["feature"]))}</text>'
        )
        body.append(
            f'<rect x="{x0}" y="{y}" width="{width:.2f}" height="31" rx="3" fill="{fill}"/>'
        )
        body.append(
            f'<text x="{x0 + width + 10:.2f}" y="{y + 22}" class="value">{value:.3f}</text>'
        )
    body.append(
        '<text x="50" y="738" class="small">Directly extracted from S06; ranking is exploratory and does not establish causality.</text>'
    )
    write(
        output / "random-forest-feature-importance-11.svg",
        document(
            1200,
            770,
            "Legacy random-forest feature importance",
            "A horizontal bar chart of eleven impurity-based importance values extracted from the saved workbook.",
            "\n".join(body),
        ),
    )


def wrap_label(label, limit=43):
    words = label.split()
    lines = [""]
    for word in words:
        candidate = (lines[-1] + " " + word).strip()
        if len(candidate) <= limit or not lines[-1]:
            lines[-1] = candidate
        else:
            lines.append(word)
    return lines[:2]


def reason_figure(output, group, filename, title):
    with (ROOT / "results/open-text-reason-categories.csv").open(newline="") as handle:
        rows = [row for row in csv.DictReader(handle) if row["group"] == group]
    maximum = max(float(row["share"]) for row in rows)
    x0, chart_width, row_height = 500, 520, 51
    height = 170 + len(rows) * row_height
    body = [
        f'<text x="48" y="51" class="title">{esc(title)}</text>',
        '<text x="48" y="80" class="subtitle">Aggregated categories cached in the final report</text>',
    ]
    for tick in range(0, int(maximum * 100) + 6, 5):
        x = x0 + chart_width * (tick / 100) / maximum
        body.append(
            f'<line x1="{x:.1f}" y1="105" x2="{x:.1f}" y2="{height - 55}" class="grid"/>'
        )
        body.append(
            f'<text x="{x:.1f}" y="{height - 30}" text-anchor="middle" class="small">{tick}%</text>'
        )
    for index, row in enumerate(rows):
        y = 112 + index * row_height
        share = float(row["share"])
        width = chart_width * share / maximum
        lines = wrap_label(row["category_en"])
        start_y = y + 15 if len(lines) == 2 else y + 24
        for line_index, line in enumerate(lines):
            body.append(
                f'<text x="48" y="{start_y + line_index * 18}" class="label">{esc(line)}</text>'
            )
        body.append(
            f'<rect x="{x0}" y="{y + 5}" width="{width:.2f}" height="30" rx="3" fill="#2b8a78"/>'
        )
        body.append(
            f'<text x="{x0 + width + 9:.2f}" y="{y + 26}" class="value">{share:.1%} · {row["count"]}</text>'
        )
    body.append(
        f'<text x="48" y="{height - 4}" class="small">Counts are responses/categories retained in the report chart cache, not the full survey sample.</text>'
    )
    write(
        output / filename,
        document(
            1200,
            height,
            title,
            f"A horizontal bar chart of aggregated open-text reason categories for {group.replace('_', ' ')} respondents.",
            "\n".join(body),
        ),
    )


def replication_figure(output):
    with (ROOT / "results/replication-random-forest-permutation-importance.csv").open(
        newline=""
    ) as handle:
        rows = list(csv.DictReader(handle))
    values = [float(row["mean_balanced_accuracy_decrease"]) for row in rows]
    limit = max(0.01, max(abs(value) for value in values) * 1.15)
    x0, half_width = 620, 430
    body = [
        '<text x="48" y="51" class="title">Held-out permutation audit</text>',
        '<text x="48" y="80" class="subtitle">Mean change in balanced accuracy across 50 test folds</text>',
        f'<line x1="{x0}" y1="108" x2="{x0}" y2="664" stroke="#596579" stroke-width="1.5"/>',
    ]
    for index, row in enumerate(rows):
        y = 120 + index * 49
        value = float(row["mean_balanced_accuracy_decrease"])
        std = float(row["between_split_std"])
        width = half_width * abs(value) / limit
        start = x0 if value >= 0 else x0 - width
        fill = "#087f5b" if value >= 0 else "#b42318"
        body.append(
            f'<text x="48" y="{y + 23}" class="label">{esc(FEATURE_LABELS.get(row["feature"], row["feature"]))}</text>'
        )
        body.append(
            f'<rect x="{start:.2f}" y="{y}" width="{width:.2f}" height="30" rx="3" fill="{fill}"/>'
        )
        value_x = x0 + half_width + 18
        body.append(
            f'<text x="{value_x}" y="{y + 21}" class="value">{value:+.3f}</text>'
        )
        body.append(
            f'<text x="{value_x + 62}" y="{y + 21}" class="small">SD {std:.3f}</text>'
        )
    body.append(
        '<text x="48" y="723" class="small">Positive values indicate lower held-out balanced accuracy after permutation; negative values reflect sampling noise or instability.</text>'
    )
    write(
        output / "replication-permutation-importance.svg",
        document(
            1200,
            755,
            "Held-out permutation importance audit",
            "A diverging horizontal bar chart of held-out permutation importance from the deterministic sensitivity analysis.",
            "\n".join(body),
        ),
    )


def build(output):
    scenario_figure(output)
    feature_figure(output)
    reason_figure(
        output,
        "willing",
        "open-text-positive-reasons.svg",
        "Why respondents were willing",
    )
    reason_figure(
        output,
        "not_willing",
        "open-text-negative-reasons.svg",
        "Why respondents were not willing",
    )
    replication_figure(output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "figures")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        with tempfile.TemporaryDirectory(prefix="just-transition-figures-") as temp:
            generated = Path(temp)
            build(generated)
            changed = [
                name
                for name in FIGURES
                if (generated / name).read_bytes()
                != (ROOT / "figures" / name).read_bytes()
            ]
            if changed:
                raise SystemExit("Generated figures are stale: " + ", ".join(changed))
        print(f"PASS: all {len(FIGURES)} generated SVG figures are current.")
    else:
        build(args.output_dir)
        print(f"Wrote {len(FIGURES)} deterministic SVG figures to {args.output_dir}.")


if __name__ == "__main__":
    main()
