# Risks

Status: Draft
Last Updated: 2026-06-08

## Product Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Research output is mistaken for approved roadmap | High | Keep recommendation as evidence until user approval. Do not update `docs/ROADMAP.md` or create phase files yet. |
| "투자 가능 후보" sounds like investment approval | High | Reword or pair with explicit no-live-approval / no-order language. Consider "실전 검토 통과 후보" or "운영 관찰 후보". |
| Gate hardening makes the workflow feel unusable | Medium / High | Use a waiver model for partial provider coverage, but require reason, expiry / re-review date, and monitoring trigger. |
| Waiver model weakens validation again | High | Treat waiver as unresolved risk, not as pass. Surface waived gaps on dashboard and monitoring timeline. |
| More UI sections add complexity | Medium | Implement compact packet summary first, with expandable details. Avoid new stages. |

## Technical Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Final Review packet duplicates data and grows JSONL rows | Medium | Store compact snapshot and references; keep full holdings / macro series in DB. |
| Data provenance fields are inconsistent across DB / JSONL | High | Define a minimal provenance contract before expanding evidence features. |
| Strict gate depends on provider data that is still partial | High | Gate by criticality and coverage. Let missing provider data drive review / waiver rather than silent pass. |
| Robustness Lab becomes phase-sized too quickly | High | Start with small deterministic suite and one strategy family before broad runtime integration. |
| Legacy registry compatibility confuses source chain | Medium | Add source breadcrumb and identify V2 source-of-truth explicitly. |
| Schema changes are not managed by formal migrations | Medium | Keep first phase read-model/UI focused; defer DB schema changes to a separate data governance task. |

## Data And Validation Risks

| Risk | Why it matters | Mitigation |
| --- | --- | --- |
| Current ETF snapshot used as historical truth | Can introduce look-ahead-like interpretation for past decisions | Label snapshot as validation-time current evidence; store as-of and source age in packet. |
| FRED observation without vintage data | Macro values can be revised or released with lag | Label as observation-date context; consider ALFRED / vintage layer later. |
| Survivorship bias in current universe/profile | Backtests can overstate performance if historical membership is not modeled | Add survivorship caveat and future historical membership task. |
| Multiple-testing / overfit in strategy exploration | Comparing many variants can pick noise | Add experiment count / parameter sensitivity / walk-forward evidence. |
| Cost / slippage assumptions too light | Real returns can differ materially | Make cost/slippage assumption visible and perturbable in Robustness Lab. |

## Research Gaps

| Gap | Why it matters | Follow-up |
| --- | --- | --- |
| No live app UI inspection during this research | Could miss current screen-level friction | If direction is approved, run Streamlit and inspect Backtest -> Practical Validation -> Final Review -> Selected Dashboard. |
| Benchmarks rely on public product pages | Public pages may omit calculation details | Treat benchmark output as pattern evidence only. |
| No user profile locked | Required strictness depends on whether target user is self-directed investor, quant researcher, or advisor-like operator | Decide target user before finalizing copy and gate severity. |
| No exact critical diagnostic policy yet | Implementation needs a clear list | Decide critical diagnostics with user before coding. |
| No report export format chosen | Packet could be UI-only or report artifact | Decide whether first build should produce Markdown/report snapshot or only Final Review read model. |

## Follow-Up Decision Risks

- If user wants actual capital deployment readiness, product boundary must change and legal / compliance / broker risk increases sharply.
- If user wants only internal research discipline, the first phase can stay entirely inside Streamlit / services and avoid product UI migration.
- If user wants external sharing / advisor-like reporting, disclosure and report artifact quality become more important than new strategy runtime features.

## 2026-06-08 Refresh Risks

### Product Direction Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| This baseline is mistaken for approved roadmap | High | Keep recommendations in `researches/active`; do not create new phase / task until user approves a build scope. |
| main-dev starts doing strategy research that belongs to backtest-dev | Medium / High | Treat strategy quality questions as handoff criteria; keep actual strategy improvement in `backtest-dev`. |
| Monitoring Snapshot V2 drifts into account tracking / broker integration | High | Keep manual / virtual / session-driven inputs; no account sync, order, live approval, or auto rebalance. |
| Strategy Promotion Contract becomes too bureaucratic | Medium | Start with a compact checklist and one strategy family; avoid blocking exploratory research. |
| Legacy deletion happens before archive semantics are proven | High | Use demotion matrix first; delete only after source-of-truth and recovery proof. |

### Technical Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Portfolio Monitoring files are large and easy to regress | High | If Monitoring Snapshot V2 is approved, split around snapshot schema / read model / render panels before adding broad UI. |
| Robustness experiment registry can become compute-heavy | Medium / High | Start with one source and small default suite; store compact run-set summaries, not full artifacts. |
| Data provenance contract touches DB, loader, registry, and UI layers | High | Treat as separate data phase; first define fields and decision effects before schema changes. |
| Strategy handoff contracts conflict with backtest-dev output format | Medium | Agree on a minimal report / metadata contract before integrating a specific strategy. |
| Research bundle grows into a planning dump | Medium | Keep this research as evidence and recommendation; future implementation history belongs in task / phase docs. |

### Remaining Evidence Gaps

| Gap | Why it matters | Follow-up |
| --- | --- | --- |
| No live Streamlit walkthrough in this refresh | Static docs/code can miss actual screen friction | Run Browser QA only when an approved UI build starts, or if the user asks for visual UX audit. |
| No current benchmark screenshots captured | Public product pages can omit UI details | Use official docs now; capture screenshots only if a dedicated benchmark/UI research pass is approved. |
| No exact monitoring snapshot schema approved | Implementation needs durable row shape | Decide snapshot fields before coding. |
| No exact strategy promotion checklist approved | Backtest-dev handoff could vary by strategy family | Define one compact contract, then test on Risk-On Momentum 5D or the next improved strategy. |
| No removal list approved | Legacy pages may still be useful for recovery | Produce demotion matrix before any delete / hide work. |
