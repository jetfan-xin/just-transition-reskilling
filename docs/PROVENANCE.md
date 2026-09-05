# Provenance, contribution and sharing

## Editorial scope

This repository was prepared in September 2026 from a privately held Chinese-language project archive. All new explanatory documents are in English. They are source-grounded summaries, not a complete certified translation of the original reports.

Original files were inspected read-only. No participant data or source-report binaries are redistributed. English source labels and SHA-256 fingerprints are recorded in [source-manifest.json](../source-manifest.json); original local paths are kept outside the repository.

## Evidence for Jingfan Xin's role

Jingfan's clarification on 5 September 2026 identifies her main responsibilities as **quantitative-method research and design, data processing and analysis**. She also explicitly confirmed her participation in questionnaire cleaning, Python random forest modelling, regression analysis, questionnaire and experimental design, and report writing. This is the organising emphasis of the README; the contemporaneous report provides supporting evidence below.

Questionnaire distribution and report writing were not her primary contributions and are not presented as headline responsibilities. The README prioritises quantitative methods, data preparation and analysis, and statistical and machine-learning modelling.

The midterm report's member-responsibility section, PDF pages 23–24, identifies Jingfan Xin as primarily responsible for data collection and organisation, questionnaire cleaning and analysis, and model construction. Its narrative specifically describes her contribution to the logistic stepwise regression model. It also records primary/shared responsibilities for questionnaire design and distribution, literature research, consultation and staged report writing. [S02]

This supports a substantive modelling and data-analysis role. It does not identify Jingfan as the overall project leader or establish sole authorship of every algorithm and final result. Field recruitment and respondent liaison were led by another team member, with Jingfan in a supporting role. The project findings and final report are collaborative outputs.

## Source register

| ID | English description | Used for |
| --- | --- | --- |
| S01 | Final research report | Sections 3.1–3.4: sample, scenarios, regressions and random forest; section 4: text and interview analysis |
| S02 | Midterm research report | Project context and funding; contribution narrative and table, PDF pages 23–24 |
| S03 | Project timeline | Detailed 2022–2023 stages and seven follow-up interviews |
| S04 | Random forest methods note | Algorithm description and narrative model metrics |
| S05 | Saved random forest output log | 32-feature output and accuracy/AUC/F1 values |
| S06 | March random forest results workbook | 11-feature importance table and saved metrics |
| S07 | October survey cleaning instructions | Earlier eligibility and plausibility checks; manual-review flags |
| S08 | Merged February survey export | Independently checked 655 records and four-arm response distribution |
| S09 | March control-group analysis export | 153 rows and a target requiring coding clarification |
| S10 | February control-group analysis export | Intermediate 154-row control dataset |

Early proposals and teaching references were not treated as evidence that a method was actually implemented. A document belonging to an unrelated research topic was excluded. Raw export variants were counted only to assess the return-count discrepancy; they were not combined into a new respondent dataset.

## Claims and evidence boundaries

- **Study setting and scope:** supported by the reports and timeline.
- **655 retained records and arm counts:** supported by both the report and a read-only aggregate check of S08.
- **Personal contribution:** quantitative-method research/design, data processing, Python random forest modelling, regression analysis, questionnaire/experimental design and report writing confirmed by Jingfan; contemporaneous data/modelling and related responsibilities supported by S02. This confirmation establishes the stated role, not independent reproduction of the retained model metrics.
- **Python/scikit-learn random forests and jieba/TF-IDF/K-means:** described in the final report; a runnable historical implementation was not located.
- **Model performance:** conflicting source versions are retained separately, not endorsed as independently reproduced scores.
- **Project distinction or completion grade:** no award claim is made here without a verified supporting record.
- **Employment or policy impact:** no deployed programme or demonstrated real-world employment improvement is claimed.

The source manifest and audit utilities document what was checked; they are not a substitute for access to the private research evidence or an independent replication.

## Sharing and attribution

The original research was a team effort. Repository maintenance by Jingfan Xin does not imply sole ownership of questionnaires, team reports, participant data or third-party publications. No blanket open-source licence is assigned to those materials.

The repository is public at Jingfan Xin's request. Recruiters can access the English project overview and supporting documentation without a GitHub invitation. Public access covers only the curated repository contents; original reports, respondent-level data, interview materials and the private source-path index remain excluded. Repository visibility does not grant redistribution rights to those original materials.

## External methodological references

Official documentation consulted on 5 September 2026 is linked beside the relevant review notes in [Methods and findings](METHODS_AND_FINDINGS.md). These sources clarify interpretation and possible future validation; their current versions are not asserted to be the study's 2023 software environment.
