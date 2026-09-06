# Data and reproducibility

## What is included

| Public artifact | Evidence status | Rebuild path |
| --- | --- | --- |
| `results/survey-summary.json` | Aggregate check of S08 | `derive_survey_summary.py` |
| `results/legacy-random-forest-output.txt` | Exact archived S05 output | `extract_legacy_outputs.py` |
| `results/random-forest-feature-importance-11.csv` | Cells extracted from S06 | `extract_legacy_outputs.py` |
| `results/open-text-reason-categories.csv` | Cached chart data extracted from S01 | `extract_legacy_outputs.py` |
| `results/model-metrics.csv` | Three source versions kept separate | Checked by `verify.py` |
| `results/replication-random-forest-*` | Deterministic sensitivity audit on S09 | `reproduce_random_forest.py` |
| `figures/*.svg` | Generated from public aggregate files | `build_figures.py` |
| Four `figures/legacy-*.png` files | Exact embedded images from S01/S06 | `extract_legacy_outputs.py` |

The scripts added for repository preparation are not recovered 2022–2023 code. No historical training script, notebook, fitted model, dependency lockfile or complete modelling environment was found in the supplied project archive. The repository does not backdate reconstructed code.

## What is excluded

- Respondent-level spreadsheets and CSV exports, including demographic, financial, health, employer and household information.
- Free-text answers, interview transcripts, recordings and identifiable case descriptions.
- Administrative forms, contact details, reimbursement records and signatures.
- Downloaded articles, books, teaching materials and unrelated project files.
- The original team reports and questionnaires, whose redistribution rights are not assumed.
- The saved results workbook itself, because its package metadata contains an author field and a local absolute path. Its non-identifying values and embedded plot are extracted instead.

Removing names alone would not make the research records suitable for public release. Repository privacy is not a substitute for participant consent or a data-sharing review. No synthetic respondent dataset is presented as original evidence.

## Public workflow

Run all dependency-free integrity, freshness and privacy checks:

```bash
make verify
```

This performs four types of validation:

1. Reconciles the aggregate counts, archived model metrics, extracted feature importances and open-text category totals.
2. Checks documentation links and source identifiers.
3. Rebuilds every generated SVG in a temporary directory and compares bytes.
4. Rejects common private-research formats, local paths, secrets, phone/email patterns and respondent-style CSV columns.

The checks validate provenance and consistency. They do not prove statistical validity.

## Private-source reconstruction

The archive owner can regenerate the public survey aggregate without exporting individual rows:

```bash
python3 scripts/derive_survey_summary.py PRIVATE_MERGED_EXPORT.csv \
  --output results/survey-summary.json
```

Selected legacy figures and result tables can be regenerated from the private Office files:

```bash
python3 scripts/extract_legacy_outputs.py \
  --report PRIVATE_FINAL_REPORT.docx \
  --workbook PRIVATE_RESULTS_WORKBOOK.xlsx \
  --random-forest-log PRIVATE_MODEL_OUTPUT.txt
```

An additional source-fingerprint audit accepts an uncommitted JSON map from source IDs to local paths:

```bash
python3 scripts/audit_sources.py --source-map PRIVATE_SOURCE_INDEX.json
```

Keep that map outside the repository. These tools neither modify the archive nor print respondent rows.

## Deterministic model audit

The model audit reads the 153-row control analysis export S09. It normalises the recovered target coding, then evaluates a random forest with 5-fold cross-validation repeated 10 times. It compares against a most-frequent baseline and calculates held-out permutation importance using balanced accuracy.

```bash
uv run --with-requirements requirements-replication.txt \
  python scripts/reproduce_random_forest.py PRIVATE_CONTROL_EXPORT.csv
```

Key safeguards:

- Fixed seed and pinned NumPy/scikit-learn versions.
- Five folds because the rarest response class has only five observations.
- No unnecessary Z-score scaling for the tree model.
- Explicit macro and balanced metrics for the imbalanced five-class outcome.
- No saved row-level predictions.
- Outputs labelled as a sensitivity analysis, not as a historical rerun.

## Compact variable guide

| Concept | Saved field(s) | Interpretation and caveat |
| --- | --- | --- |
| Scenario willingness | `sc1`, `sc2`, `sc3`, `sc4` | Control, training, wage and employment scenarios; responses 1–5 in S08, exactly one observed per retained record |
| Binary willingness | Derived in report | Ratings 4–5 versus 1–3; no historical transformation script survives |
| Age | `age` | Age in years |
| Education | `educ_year` | Years of education |
| Financial resources | `saving`, `lns` | Savings and a logged-savings field; treatment of zero savings is not fully specified |
| Employment history | `years_of_emp` | Years employed |
| Carbon-policy awareness | `coal_policy` | Self-reported awareness on a five-level scale |
| Insurance awareness | `un_ins_level` | Self-reported unemployment-insurance awareness |
| Ambiguity aversion | `ambig_aver` | Score from uncertainty-choice questions; exact construction needs recovery |
| Employment reasons | `reason_major`, `reason_earning`, `reason_dis` | Indicators for job/major fit, earnings and proximity motives |
| Demographic controls | `male`, `marital` | Encoded indicators; versions need checking before reuse |
| March target | `w2` | Exact matches establish the mapping 2→1, 4→2, 6→3, 8→4, 9→5 on the original scale; the reason for the irregular top code remains undocumented |

## Version issues requiring care

| Issue | What the archive establishes | What remains unresolved |
| --- | --- | --- |
| Initial return count | Final report says 1,016; available raw export variants contain 1,015 rows if treated as complementary | Whether another return or version accounts for the difference |
| Merged export | 656 non-empty rows follow the header; 655 have numeric order identifiers and one scenario response | Purpose of the extra non-record row |
| Control sample | 169 scenario responses, 154 rows in S10 and 153 in S09 | Exact exclusion reason for the last record |
| March target | All 153 S09 rows exactly match S10 on the 11 retained features and reveal a one-to-one `w2` recoding | Why the highest response uses code 9 rather than 10 |
| Eligibility rules | Cleaning notes and the final report use partly different thresholds and manual formatting flags | Complete executable exclusion ledger |
| Model outputs | Report, log and workbook metrics survive as three distinct versions | Historical random seeds, split definitions, AUC convention and model lineage |
| Text categories | Report stores category counts and describes clustering plus manual review | Tokeniser settings, stopwords, sentence assignments and adjudication record |
