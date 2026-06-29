# Sources

Status: Active
Last Verified: 2026-06-08
Access date: 2026-06-08

## Source Policy

이번 bundle은 internal product direction research다.
외부 benchmark browsing은 수행하지 않았다.
아래 sources는 현재 worktree의 local docs, code, strategy reports이며 접근일은 2026-06-08 KST다.

Evidence labels:

- `Observed`: code or local file directly confirms behavior.
- `Documented`: durable docs or strategy report states the point.
- `Inferred`: conclusion synthesized from multiple local sources.

## Local Sources

| Evidence | Label | Source | Used for |
| --- | --- | --- | --- |
| Product direction | Documented | `.aiworkspace/note/finance/docs/PRODUCT_DIRECTION.md` | Evidence-first / no-live-trading boundary |
| Roadmap state | Documented | `.aiworkspace/note/finance/docs/ROADMAP.md` | Risk-On governance deferred, no active phase |
| Project ownership | Documented | `.aiworkspace/note/finance/docs/PROJECT_MAP.md` | Backtest runtime / strategy / UI file ownership |
| Runtime flow | Documented | `.aiworkspace/note/finance/docs/architecture/BACKTEST_RUNTIME_FLOW.md` | Single / Compare / Risk-On runtime paths |
| Strategy implementation flow | Documented | `.aiworkspace/note/finance/docs/architecture/STRATEGY_IMPLEMENTATION_FLOW.md` | Strategy family contracts and implementation checklist |
| Backtest UI flow | Documented | `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md` | Candidate Library support, strategy capability snapshot, workflow boundary |
| Strategy catalog | Observed | `app/web/backtest_strategy_catalog.py` | User-facing strategy list |
| Single strategy dispatch | Observed | `app/services/backtest_execution.py` | Runtime-supported strategy keys |
| Candidate replay support | Observed | `app/runtime/candidate_library.py` | Replay-supported strategy keys |
| Risk-On runtime | Observed | `app/runtime/backtest_risk_on_momentum.py` | Daily swing runtime and generated artifact behavior |
| Core strategy logic | Observed | `finance/strategy.py`, `finance/swing.py` | Strategy rule interpretation |
| Current candidate summary | Documented | `.aiworkspace/note/finance/reports/backtests/strategies/CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md` | Strict annual / GTAA / EW current candidate interpretation |
| Value hub | Documented | `.aiworkspace/note/finance/reports/backtests/strategies/VALUE_STRICT_ANNUAL.md` | Value strengths / weak points |
| Quality hub | Documented | `.aiworkspace/note/finance/reports/backtests/strategies/QUALITY_STRICT_ANNUAL.md` | Quality rescue and cleaner alternative |
| Quality + Value hub | Documented | `.aiworkspace/note/finance/reports/backtests/strategies/QUALITY_VALUE_STRICT_ANNUAL.md` | Blended family current strongest candidate |
| GTAA hub | Documented | `.aiworkspace/note/finance/reports/backtests/strategies/GTAA.md` | ETF tactical candidate state |
| Equal Weight hub | Documented | `.aiworkspace/note/finance/reports/backtests/strategies/EQUAL_WEIGHT.md` | ETF sleeve interpretation |
| GRS runtime smoke | Documented | `.aiworkspace/note/finance/reports/backtests/validation/runtime/GLOBAL_RELATIVE_STRENGTH_RUNTIME_SMOKE.md` | GRS core/runtime validation state |
| GRS UI replay smoke | Documented | `.aiworkspace/note/finance/reports/backtests/validation/ui_replay/GLOBAL_RELATIVE_STRENGTH_UI_REPLAY_SMOKE.md` | GRS UI / replay connection state |
| Quarterly runtime smoke | Documented | `.aiworkspace/note/finance/reports/backtests/validation/runtime/QUARTERLY_CONTRACT_RUNTIME_SMOKE.md` | Quarterly prototype contract preservation |

## External Sources

None used in this 2차 internal direction pass.

External benchmark research can be opened later if the user wants to compare this strategy workflow against commercial quant platforms, portfolio analytics products, or research report tools.
