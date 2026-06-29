# Overview Market Movers Detail V3 Risks

- Compact metadata lookup uses external providers through the existing service when the user explicitly presses the button. Provider failure is expected to surface as `FAILED` or `PARTIAL`, not as a reason to infer catalysts.
- Same-sector peer context is based on currently visible mode rows, not the full universe. 4차 will handle broader sector context.
- NASDAQ coverage may still show `No Universe` depending on local DB state. 5차 will make data quality language more systematic.
- `pytest` may still be unavailable in this local environment; if so, use the documented unittest fallback for related contracts.
