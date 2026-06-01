# Ingestion Console UX / Data Quality V1 Risks

## Open Risks

- UI quick checks do not replace full post-run coverage auditing for very large OHLCV collections.
- Lifecycle current snapshot jobs can still be misunderstood as survivorship proof if users ignore the warning callouts; Data Coverage Audit must keep PASS criteria strict.
- Actual provider jobs were not executed during QA, so DB write behavior and live provider availability remain covered by existing service contracts and should be checked during operator review.
- Full OHLCV requested-window coverage report may require a later data-layer hardening slice if users need per-symbol post-run coverage output for large universes.
- The responsive polish improves the existing Streamlit layout; it is not yet a full product-style redesign with job catalog cards, active detail pane, and guided recovery flow.

## Mitigated In This Slice

- Browser QA no longer blocks closeout; the Streamlit app started locally and the Ingestion page rendered.
- Current snapshot caveats are visible in both the job guide and lifecycle tab copy.
- Narrow-width text truncation is mitigated for the reported result summary and selector areas by using wrapping cards and full current-selection captions.
- Result summary now uses domain-aware metric labels and interpretation callouts.
- Bounded date-window price runs now have a pre-run DB coverage quick check.
- Lifecycle partial evidence warning is shown as a visible callout in the tab and in result interpretation.
