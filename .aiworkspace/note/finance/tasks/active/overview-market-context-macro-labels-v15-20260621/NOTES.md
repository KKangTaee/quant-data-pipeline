# Overview Market Context Macro Labels V15 Notes

## Notes

- The macro-conditioned analog calculation remains unchanged. This task only clarifies the rendered meaning of existing broad / conditioned sample counts and reference macro backdrop counts.
- `GLD 조건 적용` count is read from the existing `gld_safe_haven_context` dimension preview when available.
- `금리선물 조건 적용` count is read from the existing `futures_rate_pressure_context` dimension preview or final conditioned sample count.
- T10Y3M / VIXCLS / BAA10Y are still reference backdrop only; they are not hard filters.
