# Provider Gap Collection Boundary Notes

## Findings

- Provider gap collection currently imports ingestion jobs directly into the Streamlit UI module.
- The UI also reads `finance.data.etf_provider.load_etf_provider_source_map` directly to decide whether holdings / exposure collection is possible.
- The existing service contract test confirms service imports do not load Streamlit, so new provider gap service code must keep that property.

## Decisions

- Keep provider collection in the existing Practical Validation service rather than creating a separate service module because the use-case is tightly bound to a Practical Validation result payload.
- Preserve the existing `st.session_state` key format through `provider_gap_state_key()` so users do not lose the latest collection result display behavior.
- Do not change `app.jobs.run_history` storage path in this slice; that is separate run-history cleanup work.
