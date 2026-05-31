# Risks

Status: Draft
Last Updated: 2026-05-28

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
