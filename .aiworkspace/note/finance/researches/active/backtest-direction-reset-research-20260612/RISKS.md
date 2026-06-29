# Risks

Status: Active
Last Updated: 2026-06-12 KST

## Product Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Research output is mistaken for approved roadmap | High | Keep recommendation as evidence until user approval. Do not update `docs/ROADMAP.md` or phase/task plans in this run. |
| 1차 handoff contract becomes another Backtest Analysis panel | High | Keep the first scope to compact labels/strip/read model; Browser QA must confirm default view remains execution-first. |
| High CAGR/MDD performance upgrades maturity prematurely | High | Maturity labels require data/replay/validation gates, not performance alone. |
| Strict quarterly prototypes lose prototype label too early | High | Require PIT quarterly rows, filing lag evidence, replay parity, validation compatibility, and current anchor before formalization. |
| Risk-On Momentum becomes a monitoring signal by implication | High | Keep it a research lane until Daily Swing validation module, selected-route rule, artifact policy, and monitoring cadence are approved. |
| Saved setup/replay is treated as validation | Medium | Use four-object language: Run Result, Replayable Setup, Validation Source, Monitoring Record. |
| ETF provider evidence is over-read as historical truth | Medium | Add caveats for current holdings, missing historical constituents, delisting/acquisition gaps, and source freshness. |

## Technical Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Future UI edits touch broad Backtest files | Medium | Start with Streamlit-free read model tests and narrow render integration. |
| Existing dirty workspace hides unrelated changes | Medium | Continue preserving pre-existing dirty `docs/ROADMAP.md`, `tasks/active/STATUS_MANIFEST.md`, and untracked run history unless user explicitly scopes them. |
| Strategy catalog / maturity rows drift | Medium | Add catalog coverage tests if maturity labels are implemented. |
| Replay labels require touching history, saved replay, candidate library, and result display | Medium | Sequence as 2차 after 1차 terms are accepted. |
| Practical Validation handoff accidentally changes gate semantics | High | Do not modify Practical Validation behavior until a dedicated approved task. |
| Browser QA is needed for screen weight | Medium | Any future UI change must include Browser screenshot QA. This research run has no UI change. |

## Research Gaps

| Gap | Why it matters | Follow-up |
| --- | --- | --- |
| Portfolio Visualizer direct terminal access returned 403 | Limits detail about current UI/persistence. | Treat as high-level pattern only; use browser/manual inspection later if it becomes decisive. |
| Benchmarks were intentionally limited to five products | Could miss niche workflow patterns. | Open a separate benchmark pass only if user wants deeper market positioning. |
| No live local Browser QA in this research run | No UI was changed, so screenshot QA would not verify new behavior. | Run Browser QA in the first implementation task. |
| No new strategy performance run | This research is product direction, not performance validation. | Run focused smoke/backtests only after user approves a build or evidence-expansion scope. |
| Current branch task docs are retained completed boards | Active/done semantics can be confusing. | Continue using `STATUS_MANIFEST.md` and roadmap as active-state source of truth. |

## Open Questions For User Approval

1. Should the next approved build be 1차 `Backtest Result Handoff Contract` only?
2. Should compact maturity labels appear in strategy selection, result summaries, or only after a result exists?
3. Should 3A~4B reference panels remain hidden in Backtest Analysis for now, or should a later cleanup move them to Reference / reports?
4. After 1차, should the next priority be replay semantics, ETF evidence expansion, or strict annual + ETF sleeve validation handoff?
5. Should strict quarterly prototype and Risk-On governance remain out of the next cycle?

## Boundary Reminders

- Do not implement from this research without approval.
- Do not add Backtest Analysis panels.
- Do not rewrite registry / saved JSONL / run history / generated artifacts.
- Do not direct-fetch provider/FRED data from UI.
- Do not change Practical Validation / Final Review / Portfolio Monitoring behavior from this research alone.
- Do not treat research recommendation as committed roadmap.
