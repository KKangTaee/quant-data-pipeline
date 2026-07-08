# Risks

- Legacy broad functions remain in code for compatibility. Future cleanup must not remove them without replay testing old saved setups and run history.
- Some docs and evidence inventory entries still mention broad `nyse_factors` as legacy source. That is intentional, but Phase 8 should align indexes and runbooks so the canonical source is unambiguous.
- Existing Streamlit deprecation warnings for `use_container_width` appear during Browser QA; they are not specific to this migration.
