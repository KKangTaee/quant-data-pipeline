# Risks

## Product Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Report is mistaken for investment advice | High | Label as backtest evidence / decision support only; avoid live approval language. |
| Pretty viewer hides missing evidence | High | Warning and limitation sections must be mandatory in `BacktestReportPack`. |
| `NOT_RUN` validation appears as pass | High | Treat `NOT_RUN` as insufficient evidence in report QA. |
| Report diverges from registry/source-of-truth | High | Use source links and read-only report artifact; never rewrite registry from report generation. |
| User trusts stale benchmark/data | Medium | Include data freshness, benchmark availability, period mismatch warnings. |

## Technical Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Result shapes differ by run type | Medium | Start with one run type and explicitly list unsupported fields. |
| Metric definitions become inconsistent | Medium | Define metric source and formula before adding expanded metrics. |
| Markdown generator becomes another source-of-truth | Medium | Treat generated Markdown as derived artifact with source metadata. |
| Viewer arrives before contract stabilizes | Medium | Build report pack and Markdown draft before Streamlit/Next.js viewer. |
| Existing path drift around `.note` vs `.aiworkspace/note` affects history | Medium | Verify `app/web/runtime/history.py` path behavior before implementation. |
| Chart image/export scope expands too early | Medium | Use chart-ready references first; defer rendered images/PDF. |

## Research Gaps

| Gap | Why it matters | Follow-up |
| --- | --- | --- |
| Actual run history row schema not fully sampled | Generator needs exact available fields | Inspect representative clean run history after user-approved implementation start. |
| Selected portfolio and weighted portfolio report differences | Different source fields may need variant handling | Start with one run type, then expand. |
| Expanded metric data availability | Some metrics require returns series, benchmark returns, holdings, or trades | Add a metric availability matrix before implementation. |
| HTML/PDF export stack not selected | Later export quality depends on rendering path | Decide only after Markdown/report viewer stabilizes. |

## Recommendation Guardrails

- First build only a report contract and Markdown draft generator.
- Do not add public share links, auth, or PDF export in the first slice.
- Do not let report generation mutate registry or saved setup.
- Do not create AI narrative until structured evidence and warnings are mandatory.
- Treat this research as planning input, not as approval to implement every candidate.
