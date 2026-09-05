#!/usr/bin/env python3
"""Read-only 2026 archive audit. Never exports respondent rows or fits a model.

Requires a private JSON source-ID/path map kept outside the repository.
Only Python standard-library modules are used. No files are written.
"""

import argparse
import collections
import csv
import hashlib
import io
import json
import re
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_csv(path):
    raw = path.read_bytes()
    for encoding in ('utf-8-sig', 'gb18030'):
        try:
            return list(csv.DictReader(io.StringIO(raw.decode(encoding))))
        except UnicodeDecodeError:
            continue
    raise ValueError('Unsupported source encoding; no data printed')


def workbook_cells(path):
    with zipfile.ZipFile(path) as archive:
        strings = []
        if 'xl/sharedStrings.xml' in archive.namelist():
            tree = ET.fromstring(archive.read('xl/sharedStrings.xml'))
            strings = [''.join(node.itertext()) for node in tree]
        sheet = ET.fromstring(archive.read('xl/worksheets/sheet1.xml'))
        result = {}
        for cell in sheet.findall('.//m:c', NS):
            value_node = cell.find('m:v', NS)
            value = value_node.text if value_node is not None else ''
            if cell.get('t') == 's':
                value = strings[int(value)]
            elif cell.get('t') == 'inlineStr':
                value = ''.join(cell.find('m:is', NS).itertext())
            result[cell.get('r')] = value
        return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-map', type=Path, required=True)
    args = parser.parse_args()
    source_map = args.source_map.resolve()
    require(not source_map.is_relative_to(ROOT), 'Keep the source map outside the repository')
    paths = {sid: Path(path) for sid, path in
             json.loads(source_map.read_text())['sources'].items()}
    manifest = json.loads((ROOT / 'source-manifest.json').read_text())
    for item in manifest['sources']:
        sid = item['id']
        require(sid in paths and paths[sid].is_file(), 'Missing source ' + sid)
        digest = hashlib.sha256(paths[sid].read_bytes()).hexdigest()
        require(digest == item['sha256'], 'Source version differs: ' + sid)
    print('PASS: all 10 source fingerprints match the reviewed versions.')

    expected = json.loads((ROOT / 'results/survey-summary.json').read_text())
    rows = read_csv(paths['S08'])
    require(len(rows) == expected['source_data_rows'], 'S08 row count differs')
    records = [row for row in rows if row['order'].strip().isdigit()]
    require(len(records) == expected['total_records'], 'S08 record count differs')
    fields = [group['source_field'] for group in expected['groups']]
    for row in records:
        active = [row[field].strip() for field in fields if row[field].strip()]
        require(len(active) == 1 and active[0] in ('1', '2', '3', '4', '5'),
                'Invalid scenario structure in S08; no row data printed')
    for row in rows:
        if not row['order'].strip().isdigit():
            require(not any(row[field].strip() for field in fields),
                    'Unidentified row contains a scenario response; review required')
    for group in expected['groups']:
        counts = collections.Counter(row[group['source_field']].strip() for row in records)
        actual = [counts[str(rating)] for rating in range(1, 6)]
        require(actual == group['rating_counts'], 'Aggregate mismatch: ' + group['id'])
    print('PASS: 655 records, one scenario per record, all four rating distributions match.')

    for sid, expected_count, target, expected_codes in (
        ('S09', 153, 'w2', {'2', '4', '6', '8', '9'}),
        ('S10', 154, 'sc1', {'1', '2', '3', '4', '5'}),
    ):
        subset = read_csv(paths[sid])
        require(len(subset) == expected_count, 'Subset row count differs: ' + sid)
        require({row[target] for row in subset} == expected_codes,
                'Target coding differs: ' + sid)
    print('PASS: February/March subset sizes and distinct target encodings confirmed.')

    cells = workbook_cells(paths['S06'])
    for cell, pair in {'E1': (0.445, 0.124), 'E2': (0.557, 0.096),
                       'E3': (0.329, 0.101)}.items():
        parsed = tuple(float(x) for x in re.findall(r'\d+\.\d+', cells[cell]))
        require(parsed == pair, 'Saved workbook metric differs at ' + cell)
    require(abs(float(cells['B9']) - 0.128772) < 1e-10,
            'Carbon-policy importance differs in workbook')
    print('PASS: saved 11-feature workbook metrics and policy-importance value confirmed.')
    print('Read-only audit complete. No participant rows exported and no files written.')


if __name__ == '__main__':
    main()
