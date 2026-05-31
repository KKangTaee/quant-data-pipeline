# Notes

- Current Final Review logic already does the right stage work:
  - Candidate Board: which Gate-passed candidate to inspect first.
  - Decision Cockpit: selected-route status, must-fix, must-review, monitoring seed.
  - Decision Record: final select / hold / reject / re-review record.
  - Evidence Appendix: read-only detail.
  - Saved Decision / Handoff: decision history and operations destination.
- The weak point is not logic; it is information architecture and visual hierarchy.
- Existing Practical Validation visual shell is a useful local pattern, but Final Review should have its own `fr-*` CSS namespace.
# Notes

## 2026-05-31

- The UX pass stays deliberately UI-only. It does not introduce a new score, registry, waiver model, provider fetch, approval, order, or monitoring write.
- The visual order is now: Decision Command Center -> flow rail -> Candidate Board -> Decision Cockpit -> Final Decision Action -> Evidence Appendix -> Decision History / Dashboard Handoff.
- Candidate Board and Decision Cockpit still read the existing `backtest_evidence_read_model` outputs. The new UI components only change how those read models are displayed.
- Evidence Appendix remains available for traceability, but detailed validation tables are no longer the first thing the user sees.
