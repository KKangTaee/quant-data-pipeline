# Ingestion Console UX / Data Quality V1 Risks

## Open Risks

- UI wording improvements do not by themselves validate existing DB row freshness.
- Lifecycle current snapshot jobs can be misunderstood as survivorship proof unless caveats remain visible.
- Actual provider jobs were not executed during QA, so DB write behavior and live provider availability remain covered by existing service contracts and should be checked during operator review.
- Full OHLCV coverage guard may require a later data-layer hardening slice if this UI slice becomes too large.

## Mitigated In This Slice

- Browser QA no longer blocks closeout; the Streamlit app started locally and the Ingestion page rendered.
- Current snapshot caveats are visible in both the job guide and lifecycle tab copy.
