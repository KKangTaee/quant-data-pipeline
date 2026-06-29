# Design

Status: Completed
Last Verified: 2026-06-08

## Ownership

| Area | File |
|---|---|
| ETF evidence read model | `app/services/backtest_etf_evidence_expansion.py` |
| Backtest Analysis render | `app/web/backtest_analysis.py` |
| Contract tests | `tests/test_backtest_etf_evidence_expansion.py` |
| Durable docs | `docs/PROJECT_MAP.md`, `docs/architecture/SCRIPT_STRUCTURE_MAP.md`, `docs/flows/BACKTEST_UI_FLOW.md`, `docs/ROADMAP.md` |

## Product Shape

The panel is a read-only evidence normalization board for non-GTAA ETF strategies.

It should show:

- Target strategies: Global Relative Strength, Risk Parity Trend, Dual Momentum.
- Current anchor: runtime / replay / product exposure currently available.
- Near miss: why the strategy is plausible but not evidence-mature yet.
- Not-ready reason: the specific blocker before Practical Validation emphasis.
- Required evidence: provider / cost / price freshness / benchmark / guardrail / concentration evidence.
- Next workflow: what to run or document later, without writing registries now.

## Boundary

The read model must not import Streamlit, call runtime, read DB, fetch providers, write JSONL, or create current candidate rows.
The UI must only render the service payload and leave Single Strategy / Portfolio Mix execution unchanged.

## Implemented Shape

- The read model returns a copied payload with target rows, baseline references, route boundary, storage boundary, and deferred-workflow flags.
- The UI renders compact metrics for target count, baseline count, candidate writes, and backtest reruns.
- The target table stays summary-oriented, with detailed not-ready / evidence lists shown in expandable per-strategy rows.
- The next workflow table stays read-only and does not trigger reruns or persistence.
