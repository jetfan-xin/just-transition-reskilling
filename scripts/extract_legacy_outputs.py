#!/usr/bin/env python3
"""Extract selected non-identifying outputs from the private Office archive.

The source report and workbook are not redistributed. This script copies only
four embedded PNG figures, transcribes two cached chart series, extracts the
saved 11-feature importance table, and preserves the plain-text model log.
"""

import argparse
import csv
import hashlib
import io
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

CHART_NS = {
    "c": "http://schemas.openxmlformats.org/drawingml/2006/chart",
}
SHEET_NS = {
    "m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
}

POSITIVE_TRANSLATIONS = {
    "发展前景好": "Good development prospects",
    "国家号召、未来所趋": "National policy direction and future trend",
    "更高的收入": "Higher income",
    "稳定的收入和工作": "Stable income and employment",
    "积极面对挑战": "Willingness to face change and challenge",
    "学习新知，提高自身能力": "Learning new skills and self-improvement",
    "节能环保": "Energy conservation and environmental protection",
    "更好的福利待遇": "Better benefits",
    "更好的个人生活": "Better quality of life",
    "看好创新": "Confidence in innovation",
    "改善工作环境": "Better working conditions",
    "其他": "Other",
}

NEGATIVE_TRANSLATIONS = {
    "转行期间无收入，没有生活保障": "No income or living security during transition",
    "行业发展和待遇不明朗": "Uncertain industry prospects and pay",
    "不了解新能源行业": "Unfamiliarity with renewable energy",
    "年龄大": "Older age",
    "转行浪费时间精力": "Switching costs in time and effort",
    "自身文化程度低": "Limited formal education",
    "哪里赚钱、待遇好就去哪里": "Preference for the best-paying available work",
    "当前工作稳定": "Current job is stable",
    "通勤困难": "Commuting difficulty",
    "不喜欢": "Lack of interest",
    "专业不对口": "Skills or major mismatch",
    "担心收入下降": "Concern about lower income",
    "转行影响照顾孩子": "Transition would disrupt childcare",
    "其他": "Other",
}


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def shared_strings(archive):
    root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    return ["".join(item.itertext()) for item in root.findall("m:si", SHEET_NS)]


def workbook_cells(archive):
    strings = shared_strings(archive)
    sheet = ET.fromstring(archive.read("xl/worksheets/sheet1.xml"))
    cells = {}
    for cell in sheet.findall(".//m:c", SHEET_NS):
        value_node = cell.find("m:v", SHEET_NS)
        value = value_node.text if value_node is not None else ""
        if cell.get("t") == "s":
            value = strings[int(value)]
        cells[cell.get("r")] = value
    return cells


def chart_series(archive, chart_number):
    root = ET.fromstring(archive.read(f"word/charts/chart{chart_number}.xml"))
    series = root.find(".//c:ser", CHART_NS)
    if series is None:
        raise ValueError(f"Chart {chart_number} contains no series")
    categories = [node.text or "" for node in series.findall(".//c:cat//c:v", CHART_NS)]
    values = [
        int(float(node.text)) for node in series.findall(".//c:val//c:v", CHART_NS)
    ]
    if not categories or len(categories) != len(values):
        raise ValueError(f"Chart {chart_number} cache is incomplete")
    return categories, values


def write_csv(path, header, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(header)
    writer.writerows(rows)
    path.write_text(buffer.getvalue())


def extract_workbook(workbook, root):
    with zipfile.ZipFile(workbook) as archive:
        cells = workbook_cells(archive)
        rows = []
        for row_number in range(2, 13):
            feature = cells[f"A{row_number}"]
            importance = float(cells[f"B{row_number}"])
            rows.append((feature, importance))
        rows.sort(key=lambda item: item[1], reverse=True)
        write_csv(
            root / "results/random-forest-feature-importance-11.csv",
            ("rank", "feature", "importance", "source_id", "evidence_status"),
            [
                (rank, feature, f"{importance:.6f}", "S06", "saved_workbook_output")
                for rank, (feature, importance) in enumerate(rows, 1)
            ],
        )
        image = archive.read("xl/media/image1.png")
    image_path = root / "figures/legacy-random-forest-feature-importance-11.png"
    image_path.parent.mkdir(parents=True, exist_ok=True)
    image_path.write_bytes(image)
    return image_path, sha256(image)


def extract_report(report, root):
    media = {
        "word/media/image2.png": "legacy-policy-awareness-boxplot.png",
        "word/media/image3.png": "legacy-positive-reasons-wordcloud.png",
        "word/media/image4.png": "legacy-negative-reasons-wordcloud.png",
    }
    hashes = []
    reason_rows = []
    with zipfile.ZipFile(report) as archive:
        for member, filename in media.items():
            data = archive.read(member)
            path = root / "figures" / filename
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            hashes.append((path, sha256(data)))

        for group, chart_number, translations in (
            ("willing", 9, POSITIVE_TRANSLATIONS),
            ("not_willing", 10, NEGATIVE_TRANSLATIONS),
        ):
            categories, values = chart_series(archive, chart_number)
            total = sum(values)
            for rank, (category, count) in enumerate(zip(categories, values), 1):
                if category not in translations:
                    raise ValueError(
                        f"Missing translation for cached label: {category}"
                    )
                reason_rows.append(
                    (
                        group,
                        rank,
                        category,
                        translations[category],
                        count,
                        total,
                        f"{count / total:.6f}",
                        "S01",
                        f"chart{chart_number}_cached_series",
                    )
                )
    write_csv(
        root / "results/open-text-reason-categories.csv",
        (
            "group",
            "rank",
            "category_zh",
            "category_en",
            "count",
            "group_total",
            "share",
            "source_id",
            "extraction_method",
        ),
        reason_rows,
    )
    return hashes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--workbook", type=Path, required=True)
    parser.add_argument("--random-forest-log", type=Path, required=True)
    parser.add_argument(
        "--repo-root", type=Path, default=Path(__file__).resolve().parents[1]
    )
    args = parser.parse_args()
    root = args.repo_root.resolve()

    workbook_image, workbook_hash = extract_workbook(args.workbook, root)
    report_hashes = extract_report(args.report, root)
    log_data = args.random_forest_log.read_bytes()
    log_path = root / "results/legacy-random-forest-output.txt"
    log_path.write_bytes(log_data)

    print(f"Extracted {workbook_image.relative_to(root)} ({workbook_hash})")
    for path, digest in report_hashes:
        print(f"Extracted {path.relative_to(root)} ({digest})")
    print(f"Copied {log_path.relative_to(root)} ({sha256(log_data)})")
    print("No respondent rows, Office metadata, or local source paths were exported.")


if __name__ == "__main__":
    main()
