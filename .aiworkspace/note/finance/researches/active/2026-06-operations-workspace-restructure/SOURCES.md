# Sources

Access date: 2026-06-03

Evidence labels:

- `Observed`: official UI/docs directly show the pattern.
- `Documented`: official docs or repository describe the pattern.
- `Claimed`: product page or marketing copy claims the pattern.
- `Inferred`: synthesis from multiple supported facts.
- `Unknown`: evidence is missing or unclear.

## Local Sources

| Source | Evidence | Notes |
| --- | --- | --- |
| `.aiworkspace/note/finance/docs/PRODUCT_DIRECTION.md` | Documented | Defines the product as evidence-first quant research through monitoring and states no-live-trading non-goal. |
| `.aiworkspace/note/finance/docs/ROADMAP.md` | Documented | Shows recent Selected Dashboard and Operations-related implementation context. |
| `.aiworkspace/note/finance/docs/PROJECT_MAP.md` | Documented | Maps Selected Dashboard and Operations owner files and data boundary. |
| `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md` | Documented | Describes Backtest -> Practical Validation -> Final Review -> Selected Dashboard flow and Operations support screens. |
| `.aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md` | Documented | Describes Selected Dashboard as read-only monitoring and clarifies storage boundary. |
| `app/web/streamlit_app.py` | Observed | Navigation groups Workspace, Operations, Reference and lists Operations pages. |
| `app/web/ops_review.py` | Observed | Operations Dashboard renders run health, logs, artifacts, route guidance. |
| `app/web/backtest_history.py` | Observed | Backtest Run History restores/reruns/sends old runs to Practical Validation. |
| `app/web/backtest_candidate_library.py` | Observed | Candidate Library inspects saved current/pre-live records and rebuilds result curves. |
| `app/web/final_selected_portfolio_dashboard.py` | Observed | Selected Dashboard monitors Final Review selected rows in user-created monitoring portfolios. |

## Web Sources

| Source | Evidence | Notes |
| --- | --- | --- |
| [QuantConnect Research Engine](https://www.quantconnect.com/docs/v2/research-environment/key-concepts/research-engine?ref=v1) | Documented | Separates research notebooks from event-based backtesting and recommends testing hypotheses before backtests. |
| [Bloomberg PORT](https://professional.bloomberg.com/products/bloomberg-terminal/portfolio-analytics/) | Claimed / documented | Positions portfolio operations around positions, risk, performance, attribution, data validation, scenario analysis, reporting. |
| [Interactive Brokers PortfolioAnalyst](https://www.interactivebrokers.com/en/portfolioanalyst/overview.php?menu=A) | Documented | Portfolio performance/risk/concentration reporting with informational-purpose and data limitation disclosures. |
| [Morningstar X-Ray](https://www.morningstar.com/help-center/portfolio/xray) | Documented | Portfolio analysis organized by holdings breakdown, benchmark-relative allocation, sector/region/style/fees. |
| [Morningstar Rebalance Portfolio Help](https://www.morningstar.com/help-center/portfolio/rebalance-portfolio) | Documented | Rebalance is framed as reviewing allocations and adjusting toward target allocation. |
| [Sharesight Reports Overview](https://help.sharesight.com/au/reports/) | Documented | Report taxonomy separates performance, asset allocation, and tax/compliance reports. |
| [Koyfin Portfolio Tools](https://www.koyfin.com/features/portfolio-tools/) | Claimed | Portfolio tool emphasizes customizable holdings, summary rows, performance monitoring. |
| [Composer](https://www.composer.trade/) | Claimed | Strategy creation/backtest/execution platform with historical allocation and fees/slippage visibility; automation-forward boundary contrast. |

## Source Notes

- Prefer current, official, primary sources.
- Treat product marketing pages as feature-pattern evidence, not verified technical capability.
- Web product details can change; this research used pages accessed on 2026-06-03.
- Benchmark conclusions are pattern-level, not proof that this project should copy any product literally.
