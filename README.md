# Just-Transition Reskilling Study

### Understanding coal workers' willingness to retrain for renewable-energy jobs

An energy transition is also a workforce transition. This undergraduate research project investigated how training support, income security and employment prospects influence coal workers' stated willingness to move into renewable-energy work.

Conducted at **Renmin University of China in 2022–2023**, the team combined a four-arm online survey experiment with statistical modelling, exploratory machine learning and analysis of workers' written responses. The final study used **655 valid survey responses** from coal workers in Shaanxi, China.

## My contribution

I am **Jingfan Xin**, a member of the research team. I took primary responsibility for data collection and organisation, questionnaire cleaning and analysis, and model construction. I also co-designed the questionnaire and contributed to the literature review and research reports. The midterm report specifically records my contribution to constructing the logistic stepwise regression model. [Contribution evidence](docs/PROVENANCE.md)

The work connected a practical energy-sector question with hands-on data preparation, statistical analysis and interdisciplinary research. The completed team's analysis extended to random forests and Chinese text analysis; the methods below describe the study as a whole.

## What the study examined

Participants received one of four hypothetical policy scenarios:

| Scenario | Information presented | Participants |
| --- | --- | ---: |
| Policy background | Energy-transition policy and renewable-sector context | 169 |
| Training | Background plus a free three-month training course | 164 |
| Income protection | Training plus continued payment of the previous wage | 158 |
| Employment support | Training and wage protection plus a job after completion | 164 |

The outcome was **stated willingness to retrain**, not actual training attendance or subsequent employment. [Study design](docs/STUDY_DESIGN.md)

## Main takeaway

The evidence highlighted **income security during retraining and uncertainty about future work** as practical issues for transition support. Responses in the wage-protection scenario were more positive than in the training-only scenario. The report also examined how savings, age and policy awareness related to willingness, and used open-ended responses to understand workers' reasoning.

These findings informed the team's discussion of retraining support; they do not establish that a programme increased employment. Detailed findings and the limits of the retained model outputs are documented in [Methods and findings](docs/METHODS_AND_FINDINGS.md).

## Methods and tools

- Survey preparation and analysis: **Excel, Stata and Python**.
- Statistical modelling: binary Probit and ordered logistic regression.
- Exploratory machine learning: **scikit-learn random forests** and feature-importance analysis.
- Chinese text analysis: **jieba, TF-IDF and K-means**, combined with manual review.

## Explore the project

- [Study design and timeline](docs/STUDY_DESIGN.md): research question, experimental scenarios and sample flow.
- [Methods and findings](docs/METHODS_AND_FINDINGS.md): analysis approach, verified aggregate responses and legacy results.
- [Data and reproducibility](docs/DATA_AND_REPRODUCIBILITY.md): variable guide, privacy decisions and remaining gaps.
- [Source provenance](docs/PROVENANCE.md): evidence behind the project description and my role.
- [Aggregate survey counts](results/survey-summary.json) and [archived model metrics](results/model-metrics.csv).

## Repository status

This English-language research portfolio was prepared in **September 2026** from the original Chinese project archive. It preserves the study's evidence and findings, rather than presenting a newly written model as historical work. Original training scripts were not located, so this is **not an end-to-end reproducible modelling package**. Respondent-level data, interview materials and third-party papers are not included.

The small Python utilities are new documentation-audit tools, not the original research implementation. Check the repository without installing dependencies:

```bash
python3 -B scripts/verify.py
```

Research outputs were produced collaboratively. No open-source licence is asserted for the original team's materials; see [provenance and sharing](docs/PROVENANCE.md).
