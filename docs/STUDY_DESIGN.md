# Study design

## Research question and context

Which personal circumstances and policy-support features shape coal workers' willingness to retrain for renewable-energy jobs?

The 2022–2023 study was an undergraduate team project at Renmin University of China, supported through a Beijing municipal undergraduate innovation programme. Its original working title translates approximately as *Can Coal Workers Wear Suits?* The research concerned a just transition: supporting workers whose livelihoods may be affected by a changing energy system. [S01–S03](PROVENANCE.md)

## Population and recruitment

The final report describes online recruitment during July–August 2022 through coal-industry contacts in Shaanxi, including workers in Shenmu, Hancheng and Binzhou. Recruitment was through a local contact network, not a probability sample of all Chinese coal workers. The report records 1,016 returned questionnaires and 655 retained responses. The retained sample size and group allocation were independently checked against the merged export in September 2026; the original return total is not fully reconciled. [S01, S08](PROVENANCE.md)

| Stage | Count | Evidence status |
| --- | ---: | --- |
| Returned questionnaires | 1,016 | Reported in the final report; available raw export versions do not fully reconcile |
| Retained survey records | 655 | Reported and confirmed in the merged export |
| Control arm | 169 | Reported and confirmed from populated scenario responses |
| Control-arm determinant analysis | 153 | Reported; the March analysis export also contains 153 rows |
| Follow-up interviews | 7 | Recorded in the project timeline; not reanalysed here |

The additional exclusions between 169 and 153 control observations are not reconstructable from a saved exclusion ledger. An intermediate control export contains 154 observations. See [data limitations](DATA_AND_REPRODUCIBILITY.md).

## Randomised information experiment

The survey displayed one of four information bundles to each participant. All bundles included background information about energy policy and the renewable sector. Each participant then rated willingness to participate in retraining and move into renewable-energy work on a five-point scale. [S01, section 3.3.1](PROVENANCE.md)

| Arm | Three-month free course | Previous wage maintained during training | Employment after training | n |
| --- | --- | --- | --- | ---: |
| Control | Not offered in the vignette | Not offered | Not offered | 169 |
| Training | Yes | Not offered | Not offered | 164 |
| Wage protection | Yes | Yes | Not offered | 158 |
| Employment support | Yes | Yes | Yes | 164 |

These were **hypothetical offers**, not courses, wages or jobs delivered by the researchers. The bundles were cumulative, not a fully crossed factorial design. In particular, the study did not vary course length across several durations; the archive's “duration group” refers to the three-month training scenario.

The final report describes random assignment through the questionnaire platform, but assignment code and a randomisation seed were not located. Group-balance checks showed some covariate differences. Consequently, a careful interpretation must account for allocation, post-survey exclusions and model specification, rather than assuming balance or representativeness.

## Outcomes and analysis tracks

1. **Policy-scenario comparison:** the five-point response was collapsed to a binary outcome for Probit analysis, with ratings 4–5 classified as willing and 1–3 as not meeting that threshold.
2. **Individual determinants:** the control subsample was analysed with ordered logistic regression; random forests provided an exploratory comparison of variable importance.
3. **Reasons behind decisions:** Chinese free-text responses were examined using tokenisation, TF-IDF, clustering and manual interpretation. The timeline also records seven semi-structured interviews.

The binary outcome means “willing or very willing,” not a claim that every neutral respondent refused training. The separate March modelling file uses a differently coded target; its mapping remains unresolved. [S01, S03, S09](PROVENANCE.md)

## Timeline

| Period | Team activity |
| --- | --- |
| January–April 2022 | Topic development, policy context and literature review |
| May–June 2022 | Questionnaire design and refinement |
| July–August 2022 | Online survey collection |
| September–November 2022 | Data cleaning and descriptive analysis |
| December 2022–January 2023 | Probit, logistic regression and random forest analysis |
| February 2023 | Free-text analysis and follow-up interviews |
| February–March 2023 | Final report preparation |

This is the team's research timeline, not a substitute for an individual's contracted or CV participation dates. It follows the detailed entries in S03; a contradictory date range in that document's introductory sentence is not repeated here.
