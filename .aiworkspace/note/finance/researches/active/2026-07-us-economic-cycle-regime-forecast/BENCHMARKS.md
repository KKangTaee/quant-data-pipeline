# Benchmarks

Status: Complete
Last Updated: 2026-07-16

Evidence labels:

- `Observed`: official UI/docs directly show the pattern.
- `Documented`: official docs or repository describe the pattern.
- `Claimed`: product page or marketing copy claims the pattern.
- `Inferred`: synthesis from multiple supported facts.
- `Unknown`: evidence is missing or unclear.

## Benchmark Matrix

| Product / Service | Category | Evidence | Relevant pattern |
| --- | --- | --- | --- |
| NBER Business Cycle Dating | Official U.S. chronology | Documented | Recession is broad, deep, and durable; dating is retrospective and two-state. |
| OECD Composite Leading Indicator | Leading growth-cycle indicator | Documented / Observed | Trend-relative level and direction create a readable four-phase cycle clock; revisions must be disclosed. |
| Chicago Fed CFNAI | Coincident monthly activity index | Documented / Observed | 85-series common factor, three-month average, and diffusion distinguish level, persistence, and breadth. |
| Philadelphia Fed ADS | High-frequency business-conditions index | Documented | Mixed-frequency dynamic factor with real-time vintages and a tentacle plot of revisions. |
| Dallas Fed WEI | Weekly real-activity index | Documented / Observed | A weekly common factor provides a timely bridge between monthly releases. |
| ALFRED | Real-time macro vintage archive | Documented | Historical forecasts must use values available on each forecast date, not today's revised history. |
| Hamilton / Chauvet-Hamilton | Regime-switching methods | Documented | Latent state probabilities and one-extra-release confirmation reduce false turning-point calls. |
| Stock-Watson / Giannone-Reichlin-Small | Factor and nowcasting methods | Documented | Many indicators with mixed release lags can be compressed into interpretable common factors. |
| New York Fed yield-curve research | Financial leading indicator | Documented | Yield slope is valuable mainly at longer recession horizons; it is not a sufficient one-/two-month classifier. |
| Sahm real-time indicator | Labor deterioration confirmation | Documented / Observed | Timely recession confirmation signal, but not a standalone leading forecast. |

## Key Findings

### 1. The Four User Phases Need A Growth-Cycle Definition

- NBER officially distinguishes expansion and recession and dates them retrospectively.
- OECD defines a growth cycle around trend: above/below trend crossed with rising/falling direction. This naturally maps to `회복`, `확장`, `둔화`, `침체/수축` for a product estimate.
- The UI must say that `침체` is the model's current growth-cycle estimate unless and until NBER later dates a recession.

### 2. One Indicator Is Not Enough

- NBER emphasizes breadth across income, payrolls, household employment, real consumption/sales, and industrial production.
- CFNAI uses 85 indicators and publishes a three-month average plus diffusion, reinforcing the importance of level, persistence, and breadth.
- ADS and WEI show how mixed daily, weekly, monthly, and quarterly data can be summarized without pretending every input shares the same reference month.

### 3. Real-Time Vintages Are A Product Requirement

- ALFRED exposes observations by vintage and initial release.
- Chauvet and Hamilton explicitly reconstruct turning-point inference using data as originally released.
- The current local UPSERT table loses that information. A final-revised backtest would overstate historical accuracy.

### 4. Forecast Probabilities Need Horizon-Specific Validation

- Dynamic factors are suitable for ragged macro panels; regime-switching methods produce state probabilities.
- A direct one-month and two-month forecast should be evaluated separately with rolling forecast origins.
- Accuracy alone is insufficient. Brier score, log loss, calibration error, confusion by phase, and turning-point lead/lag are required.
- Yield curve and financial prices are useful priors/overlays, but New York Fed evidence is strongest at multi-quarter horizons.

### 5. Current Official Evidence Is Consistent With Expansion, Not A Confirmed Recession

Observed on 2026-07-16:

| Indicator | Latest available | Reading | Research interpretation |
| --- | --- | ---: | --- |
| OECD U.S. CLI | 2026-05 | 101.02 and rising | Above trend and improving; an expansion-quadrant leading signal. |
| CFNAI-MA3 | 2026-05 | -0.03 | Near historical trend and well above the -0.70 contraction threshold. |
| Dallas Fed WEI | week ended 2026-07-04 | 3.17%; 13-week average 2.85% | Positive high-frequency real activity. |
| Real-time Sahm indicator | 2026-06 | 0.07 | Well below the 0.50 recession trigger. |
| U.S. payroll employment | 2026-06 | 158.984 million | Still rising, but the latest monthly gain is modest. |
| Adjusted NFCI | week ended 2026-07-10 | -0.535 | Financial conditions are looser than average. |
| 10Y–3M Treasury spread | 2026-07-15 | +0.72%p | Positive curve; no current inversion. |

This is a preliminary evidence synthesis, not a calibrated product probability. It supports `확장` as the leading current hypothesis with a non-zero `둔화` alternative because coincident activity is near trend rather than strongly above it.

## Source And Data Implications

- Core current-state evidence: CFNAI/CFNAI-MA3, payrolls, industrial production, real sales, real income less transfers, ADS or WEI.
- Leading evidence: OECD CLI, initial claims, building permits, term spread, credit spread, adjusted NFCI.
- Inflation/policy context: core PCE momentum, breakeven inflation, effective fed funds / 2Y Treasury.
- Market-implied overlay: 2Y/10Y rates, high-yield spread, broad dollar, gold, and equity breadth. These explain market interpretation but do not determine the real-economy label.
- Every series needs a cadence, expected release lag, transformation, vintage policy, polarity, and missing-data rule.

## Benchmark-Informed Gaps

| Gap | Source pattern | Finance implication |
| --- | --- | --- |
| No real-economy cycle model | NBER, CFNAI, ADS | Add a broad and persistent activity factor rather than an asset-rule table. |
| No four-phase semantics | OECD CLI | Define phase by activity level and direction, with a recession-probability override and explicit model wording. |
| No vintage history | ALFRED, ADS vintages, Chauvet-Hamilton | Add vintage-aware storage and rolling-origin evaluation before publishing probabilities. |
| No forecast calibration | Regime-switching / nowcasting literature | Produce separate now, +1M, +2M distributions and calibration evidence. |
| No trajectory visualization | OECD cycle clock plus FRED/NBER recession shading | Combine a phase-plane clock with a calendar regime ribbon. |
| User note overweights market prices | NBER breadth and factor methods | Move rates, gold, dollar, and credit into an explanatory overlay. |
