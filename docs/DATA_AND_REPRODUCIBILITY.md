# Data and reproducibility

## What is included

Only English explanatory documentation, aggregated survey counts, transcribed model metrics, source-file fingerprints and two small audit utilities are included. The fingerprints identify the reviewed file versions; they do not prove that a reported model is correct.

The 2026 utilities validate documentation and selected archive facts. **They are not recovered 2022–2023 analysis code.** No training script, notebook, fitted model, dependency lockfile or complete modelling environment was located among the supplied standalone project files and seven ZIP inventories. One RAR containing teaching material was not unpacked.

## What is excluded

- Respondent-level spreadsheets and CSV exports, including demographic, financial, health, employer and household information.
- Free-text answers, interview transcripts, recordings and identifiable case descriptions.
- Administrative forms, contact details, reimbursement records and signatures.
- Downloaded articles, books, teaching materials and unrelated project files.
- Original team-authored reports and questionnaires pending redistribution review.

Removing names alone would not make these research records suitable for public release. Repository privacy is not a substitute for participant consent or a data-sharing review. No synthetic respondent dataset is supplied or presented as original evidence.

## Compact variable guide

This is a reading guide to fields used in the retained analysis files, not a complete data dictionary or a claim that every historical transformation is known. [S01, S08–S10](PROVENANCE.md)

| Concept | Saved field(s) | Interpretation and caveat |
| --- | --- | --- |
| Scenario willingness | `sc1`, `sc2`, `sc3`, `sc4` | Control, training, wage and employment scenarios; responses 1–5 in S08, exactly one observed per retained record |
| Binary willingness | Derived in report | Ratings 4–5 versus 1–3; not an independently recovered training script |
| Age | `age` | Age in years |
| Education | `educ_year` | Years of education |
| Financial resources | `saving`, `lns` | Savings and a logged-savings field; treatment of zero savings not fully specified |
| Employment history | `years_of_emp` | Years employed |
| Carbon-policy awareness | `coal_policy` | Self-reported awareness, five-level scale in the report |
| Insurance awareness | `un_ins_level` | Self-reported unemployment-insurance awareness |
| Ambiguity aversion | `ambig_aver` | Score from uncertainty-choice questions; exact construction needs recovery |
| Employment reasons | `reason_major`, `reason_earning`, `reason_dis` | Indicator fields for job/major fit, earnings and proximity motives |
| Demographic controls | `male`, `marital` | Encoded indicators in the analysis specification; versions need checking before reuse |
| March target | `w2` | Observed values are 2, 4, 6, 8 and 9; do not assume binary or original five-point coding |

## Version issues requiring care

| Issue | What the archive establishes | What remains unresolved |
| --- | --- | --- |
| Initial return count | Final report says 1,016; available raw export variants include 582 and 433 response rows, totalling 1,015 if treated as complementary | Whether another version or return accounts for the difference; exports cannot be merged blindly |
| Merged export | 656 non-empty rows follow the header, but 655 have numeric order identifiers and one scenario response each | Purpose of the extra non-record row; it is excluded from this repository's aggregate check |
| Control sample | 169 scenario responses, 154 rows in a February subset, 153 in the March subset | Record-level exclusion history |
| Eligibility rules | October instructions and final-report age limits differ; manual colour/font review flags were used | Which exact rules produced the final dataset |
| Financial outliers | Earlier notes include income limits that are not consistent with the final report's descriptive maxima | Final units, corrections and inclusion decisions |
| Model outputs | Separate report, log and workbook metrics survive | Run configurations, target definitions, averaging and version lineage |
| Text categories | Report describes clustering plus manual categorisation | Tokeniser settings, stopwords, assignments and adjudication record |

## Run the repository checks

Python 3 standard library only; no packages, downloads or caches are required:

```bash
python3 -B scripts/verify.py
```

This checks local documentation links, source references, aggregate totals and the metric table. It does not verify statistical validity or contact external services.

### Optional read-only archive audit

The archive owner can supply a **local, uncommitted** JSON file mapping source IDs to absolute file paths:

```json
{"sources": {"S01": "/local/path/to/final-report.docx", "S02": "/local/path/to/midterm-report.pdf"}}
```

Supply all S01–S10 entries from the source manifest, then run:

```bash
python3 -B scripts/audit_sources.py --source-map /local/path/to/private-source-index.json
```

The utility reads files only, verifies their SHA-256 fingerprints, checks aggregate counts and the saved workbook metrics, and prints non-identifying audit summaries. It neither changes the archive nor exports respondent records. Do not commit the private source index.

## If original code is recovered

Preserve its original timestamps and provenance where available, review it for sensitive paths or credentials, and document its actual version. Then establish an exclusion ledger, verify outcome coding, reconstruct the evaluation split and dependency environment, and reconcile each reported result. Any newly implemented analysis must be labelled as a later replication, not backdated as historical work.
