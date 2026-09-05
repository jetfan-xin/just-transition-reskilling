# Methods and findings

This document distinguishes **historical report statements**, **saved model outputs**, and **aggregate checks performed in September 2026**. No original model was retrained for this repository.

## 1. Survey preparation

The midterm report records questionnaire design, spreadsheet organisation, manual plausibility review and cleaning with Excel and Stata, assisted by Python. The final report describes exclusions involving eligibility, age and logical inconsistencies. Earlier cleaning instructions differ from the final report; they are evidence of the workflow, not a complete executable specification. [S01, S02, S07](PROVENANCE.md)

## 2. Verified descriptive responses

The following counts were recomputed from S08 during the 2026 archive review. Records with a numeric survey-order field were retained for this check; each of these 655 records had exactly one populated scenario response. One additional non-record row had no survey-order identifier or scenario response and was not counted. No participant-level records are redistributed.

| Scenario | Very unwilling (1) | Unwilling (2) | Undecided (3) | Willing (4) | Very willing (5) | Total | Ratings 4–5 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Control | 7 | 11 | 59 | 41 | 51 | 169 | 54.4% |
| Training | 15 | 12 | 56 | 31 | 50 | 164 | 49.4% |
| Wage protection | 9 | 11 | 35 | 48 | 55 | 158 | 65.2% |
| Employment support | 10 | 9 | 44 | 46 | 55 | 164 | 61.6% |

These are **unadjusted descriptive proportions**, not fitted marginal effects or evidence about realised employment. The wage-protection group had a higher observed willingness share than the training-only group. The employment-support group was not the highest, so the pattern should not be presented as a monotonic benefit from each additional support feature. Machine-readable counts are in [survey-summary.json](../results/survey-summary.json).

## 3. Regression analysis

The final report uses binary Probit models to examine policy-scenario differences and ordered logistic regression for the control-group willingness outcome. The latter considers savings, education, policy and insurance awareness, employment reasons, ambiguity aversion and demographic controls. [S01, sections 3.3–3.4](PROVENANCE.md)

The report interprets income continuity during training as important and discusses associations involving savings, age and awareness of transition-related policies. Some significance statements in the narrative are inconsistent, and the full estimation workflow is unavailable. This repository therefore does not promote a selected coefficient or p-value as a verified headline result.

**Interpretation correction:** a Probit coefficient is not a percentage-point probability change. Probability-scale comparisons require predicted probabilities or marginal effects with an explicit evaluation rule. The archived report's probability-style readings of raw coefficients are not repeated as findings. See the official [statsmodels marginal-effects documentation](https://www.statsmodels.org/stable/generated/statsmodels.discrete.discrete_model.ProbitResults.get_margeff.html). This reference informs the 2026 review; it does not establish that statsmodels was used in the original study.

## 4. Random forests

S01 and S04 describe a Python/scikit-learn random forest with 100 trees and impurity-based feature importance. Its role was exploratory: examine potentially nonlinear associations alongside regression, not deliver an employment prediction service.

The archive contains three distinct sets of metrics:

| Artifact | Accuracy | AUC | F1 | Status |
| --- | ---: | ---: | ---: | --- |
| Final report and methods note (S01, S04) | 0.645 | 0.707 | Not stated | Narrative-reported results |
| Saved 32-feature output log (S05) | 0.432 ± 0.060 | 0.538 ± 0.057 | 0.314 ± 0.069 | Directly retained output |
| Saved 11-feature workbook (S06) | 0.445 ± 0.124 | 0.557 ± 0.096 | 0.329 ± 0.101 | Directly retained output |

The meaning of the saved “±” values, AUC averaging convention, precise targets and links between runs are not established. These rows **must not be combined as one experiment**, and the higher report numbers are not independently verified. Numeric transcriptions are in [model-metrics.csv](../results/model-metrics.csv).

In the 11-feature workbook, the highest impurity-based importance scores belong to age, log savings, insurance awareness, carbon-policy awareness and education. Its carbon-policy value is about 12.9%, while the report prose states 13.8%; the discrepancy remains unresolved. Neither ranking establishes causality. No feature-importance chart is presented as a validated causal explanation.

### Methodological notes from the 2026 review

- The report's label “10-fold stratified bootstrap cross-validation” is ambiguous: its steps describe repeated sampling with replacement and testing on remaining observations, not conventional disjoint K-fold splits. Without code, the procedure cannot be certified. See [scikit-learn cross-validation guidance](https://scikit-learn.org/stable/modules/cross_validation.html).
- The report describes Z-score scaling, but its justification that random forests generally require scale normalisation is not retained. Decision trees ordinarily need little preprocessing and do not require normalisation. See [scikit-learn decision trees](https://scikit-learn.org/stable/modules/tree.html).
- Impurity-based importance can favour high-cardinality variables and need not reflect held-out predictive value. A future rerun should include an appropriate baseline, held-out evaluation and permutation importance. See [scikit-learn's comparison of importance methods](https://scikit-learn.org/stable/auto_examples/inspection/plot_permutation_importance.html).

These are present-day review recommendations, not additional methods claimed for 2023.

## 5. Chinese text analysis and interviews

The report describes jieba tokenisation, TF-IDF keyword extraction and K-means clustering of short written reasons. Five to eight initial clusters were combined with iterative manual interpretation; the final report presents eleven positive-reason categories and thirteen negative-reason categories. Those final categories were not simply an untouched K-means output. [S01, section 4.1](PROVENANCE.md)

Themes include future prospects in renewable energy, income and employment stability, interrupted earnings during training, and uncertainty about an unfamiliar sector. The project timeline records seven follow-up interviews. Original tokenisation settings, cluster assignments and interview coding files were not located as a reproducible pipeline. Quotes and recordings are withheld.

## Practical outcome

The project produced a research report linking worker circumstances, hypothetical support packages and reasons for retraining decisions. Its practical contribution was to frame transition support around workers' financial constraints and information needs. There is no evidence here of a deployed training programme, demonstrated employment gains or a production-grade predictive model.
