#!/usr/bin/env python3
"""Check the 2026 research portfolio, not historical model performance.

Standard library only. Reads repository files; writes nothing.
"""

import csv
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    manifest = json.loads((ROOT / 'source-manifest.json').read_text())
    sources = {item['id']: item for item in manifest['sources']}
    require(len(sources) == 10, 'Expected ten distinct evidence sources')
    for item in sources.values():
        require(re.fullmatch(r'[0-9a-f]{64}', item['sha256']), 'Invalid fingerprint')
        require(item['redistributed'] is False, 'Source binaries must stay excluded')

    summary = json.loads((ROOT / 'results/survey-summary.json').read_text())
    require(summary['source_id'] in sources, 'Unknown aggregate source')
    require(summary['total_records'] == 655, 'Unexpected retained sample')
    require(sum(g['n'] for g in summary['groups']) == 655, 'Arm totals disagree')
    require(summary['source_data_rows'] - summary['excluded_non_record_rows'] == 655,
            'Non-record row accounting disagrees')
    require(len(summary['groups']) == 4, 'Expected four survey arms')
    for group in summary['groups']:
        counts = group['rating_counts']
        require(len(counts) == 5 and all(type(n) is int and n >= 0 for n in counts),
                'Expected five non-negative rating counts')
        require(sum(counts) == group['n'], 'Ratings do not sum to arm total')
        require(sum(counts[3:]) == group['willing_n'], 'Willingness threshold disagrees')

    with (ROOT / 'results/model-metrics.csv').open(newline='') as handle:
        metrics = list(csv.DictReader(handle))
    require(len(metrics) == 3, 'Keep the three legacy result versions separate')
    expected = [(0.645, 0.707, None), (0.432, 0.538, 0.314), (0.445, 0.557, 0.329)]
    for row, values in zip(metrics, expected):
        require(None not in row, 'Malformed CSV row')
        require(all(sid in sources for sid in row['source_ids'].split(';')),
                'Unknown model source')
        for column, expected_value in zip(('accuracy', 'auc', 'f1'), values):
            actual = float(row[column]) if row[column] else None
            require(actual == expected_value, 'Metric transcription changed: ' + column)

    checked_links = 0
    for path in ROOT.rglob('*.md'):
        content = path.read_text()
        require(not re.search(r'[\u4e00-\u9fff]', content), 'Explanatory prose must be English')
        for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', content):
            parsed = urlsplit(target)
            if parsed.scheme or not parsed.path:
                continue
            linked = (path.parent / unquote(parsed.path)).resolve()
            require(linked.is_relative_to(ROOT) and linked.exists(),
                    'Broken or external local link: ' + target)
            checked_links += 1
    require(not any(ROOT.rglob('*source-index*.json')), 'Private source map must stay outside')
    require(not any(ROOT.rglob('*.xlsx')), 'Do not commit respondent workbooks')
    print(f'PASS: 10 evidence sources, 655 records, 4 arms, 3 result versions, '
          f'{checked_links} local documentation links.')
    print('Documentation consistency only; no model training or statistical validation performed.')


if __name__ == '__main__':
    main()
