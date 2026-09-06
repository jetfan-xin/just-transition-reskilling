# Figure provenance

## Generated figures

The SVG files are deterministic visualisations of public aggregate JSON/CSV outputs. Rebuild them with:

```bash
python3 scripts/build_figures.py
```

- `scenario-willingness.svg`: five-point response distribution from S08 aggregates.
- `random-forest-feature-importance-11.svg`: saved S06 impurity-importance values.
- `open-text-positive-reasons.svg` and `open-text-negative-reasons.svg`: cached S01 reason-category counts with recalculated shares.
- `replication-permutation-importance.svg`: held-out permutation importance from the deterministic S09 sensitivity analysis.

## Extracted legacy figures

These PNGs are exact image members extracted from private Office packages. They contain no respondent rows, names or Office metadata.

| File | Source package member | SHA-256 | Interpretation limit |
| --- | --- | --- | --- |
| `legacy-random-forest-feature-importance-11.png` | S06 `xl/media/image1.png` | `c947c605450dc54b5c0db54149c48f87840095d34129f4e074b9c696be8ebb38` | Impurity importance; not causal |
| `legacy-policy-awareness-boxplot.png` | S01 `word/media/image2.png` | `5e8883b42d89079c40d1629f2c5dd2a4971330ceea6b756aa27c81e01d0448c8` | Historical descriptive plot; row-level construction unavailable |
| `legacy-positive-reasons-wordcloud.png` | S01 `word/media/image3.png` | `40c744862b06b4130bb82e742e2357fb69025df8c68673031da4f6fe25e37f21` | Illustrative word cloud; preprocessing settings unavailable |
| `legacy-negative-reasons-wordcloud.png` | S01 `word/media/image4.png` | `ac4ecfc1df0c3d790738a43ae1457c11478cbc1a579f3f54c6b068773310ac4e` | Illustrative word cloud; preprocessing settings unavailable |

The black area around each word cloud is transparent canvas in the original PNG, not redaction.
