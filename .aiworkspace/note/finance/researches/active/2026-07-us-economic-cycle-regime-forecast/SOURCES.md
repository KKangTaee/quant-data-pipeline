# Sources

Status: Complete
Access date: 2026-07-16

Evidence labels:

- `Observed`: official UI/docs directly show the pattern.
- `Documented`: official docs or repository describe the pattern.
- `Claimed`: product page or marketing copy claims the pattern.
- `Inferred`: synthesis from multiple supported facts.
- `Unknown`: evidence is missing or unclear.

## Local Sources

| Source | Evidence | Notes |
| --- | --- | --- |
| `.aiworkspace/note/finance/docs/INDEX.md` | Observed | Current phase/task state and Overview product summary. |
| `.aiworkspace/note/finance/docs/ROADMAP.md` | Observed | Current product scope and approval boundary. |
| `.aiworkspace/note/finance/docs/PROJECT_MAP.md` | Observed | Overview, ingestion, DB, loader, and component ownership. |
| `app/web/overview/page.py` | Observed | Top-level Overview tab routing. |
| `app/web/overview/market_context.py` | Observed | Current Market Context entrypoint renders valuation only. |
| `app/web/streamlit_components/market_context_valuation/src/MarketContextValuation.tsx` | Observed | Current S&P 500 / U.S. stock selector and component boundary. |
| `finance/data/macro.py` | Observed | Generic FRED collector and three default risk-context series. |
| `finance/loaders/macro.py` | Observed | Historical and latest-as-of DB reads. |
| `finance/data/db/schema.py` | Observed | Macro values overwrite revisions because the unique key has no vintage. |
| `/Users/taeho/.codex/attachments/8ff9bef8-1b9f-4953-b67d-24b5a71de84e/pasted-text.txt` | Observed | User's four-phase study note and policy/asset interpretation rules. |

## Web Sources

| Source | Evidence | Notes |
| --- | --- | --- |
| [NBER Business Cycle Dating](https://www.nber.org/research/business-cycle-dating) | Documented | Official chronology, depth/diffusion/duration, monthly indicators, retrospective boundary. |
| [NBER Business Cycle Dating FAQ](https://www.nber.org/research/business-cycle-dating/business-cycle-dating-procedure-frequently-asked-questions) | Documented | Expansion/recession direction, data revisions, and announcement lags. |
| [Hamilton (1989), A New Approach to the Economic Analysis of Nonstationary Time Series and the Business Cycle](https://doi.org/10.2307/1912559) | Documented | Foundational Markov-switching regime model. |
| [Stock and Watson, Macroeconomic Forecasting Using Diffusion Indexes](https://stock.scholars.harvard.edu/publications/macroeconomic-forecasting-using-diffusion-indexes) | Documented | Approximate factor models and diffusion-index forecasting. |
| [Federal Reserve, Nowcasting GDP and Inflation](https://www.federalreserve.gov/econres/feds/nowcasting-gdp-and-inflation-the-real-time-informational-content-of-macroeconomic-data-releases.htm) | Documented | Ragged real-time releases and factor nowcast updates. |
| [Chauvet and Hamilton, Dating Business Cycle Turning Points](https://www.nber.org/papers/w11422) | Documented | Real-time multiple-indicator recession probabilities and confirmation delay. |
| [OECD Composite Leading Indicators](https://www.oecd.org/en/data/datasets/oecd-composite-leading-indicators-clis.html) | Documented / Observed | Growth-cycle turning points, monthly cadence, and revision data. |
| [OECD CLI FAQ](https://www.oecd.org/en/data/insights/data-explainers/2024/04/composite-leading-indicators-frequently-asked-questions.html) | Documented | Trend-relative four-phase interpretation, 6–9 month target lead, and revision causes. |
| [FRED U.S. OECD CLI table](https://fred.stlouisfed.org/data/USALOLITOAASTSAM) | Observed | Latest available U.S. CLI values used in the current evidence check. |
| [Chicago Fed CFNAI Methodology](https://www.chicagofed.org/research/data/cfnai/about) | Documented / Observed | 85 indicators, MA3, diffusion, trend and contraction thresholds. |
| [Philadelphia Fed ADS Index](https://www.philadelphiafed.org/surveys-and-data/real-time-data-research/ads) | Documented | Mixed-frequency real activity, real-time updates, and vintage/tentacle plots. |
| [Dallas Fed Weekly Economic Index](https://www.dallasfed.org/research/wei) | Documented / Observed | Weekly common factor and 2026-07-09 current reading. |
| [FRED Real-time Sahm Rule](https://fred.stlouisfed.org/release?rid=456) | Documented / Observed | Labor-based current recession confirmation context. |
| [ALFRED Download Data Help](https://alfred.stlouisfed.org/help/downloaddata) | Documented | Observations by vintage, real-time period, and initial release. |
| [New York Fed, Predicting U.S. Recessions](https://www.newyorkfed.org/research/staff_reports/research_papers/9609.html) | Documented | Financial leading indicators and horizon-specific yield-curve evidence. |
| [Federal Reserve, Total Recall?](https://www.federalreserve.gov/econres/feds/total-recall-evaluating-the-macroeconomic-knowledge-of-large-language-models.htm) | Documented | Errors from mixing revisions and unreleased reference periods. |
| [OECD, Extended Markov-Switching Dynamic Factor Model](https://www.oecd.org/en/publications/business-cycle-dynamics-after-the-great-recession_9626dda3-en.html) | Documented | Volatility/trend changes and real-time turning-point performance. |

## Source Notes

- Prefer current, official, primary sources.
- Direct FRED CSV observations were read without DB writes on 2026-07-16 to check latest data dates and values.
- Current readings are research evidence only; no product probability is inferred until the model is calibrated.
- OECD CLI direction is useful, but its recent values are revised as filters and component availability change.
