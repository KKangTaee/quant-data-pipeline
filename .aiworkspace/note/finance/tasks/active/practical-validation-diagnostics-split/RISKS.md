# Practical Validation Diagnostics Split Risks

Status: Active
Created: 2026-05-27

## Active Risks

| Risk | Mitigation |
| --- | --- |
| Existing UI imports break after moving builder functions | Keep diagnostics re-export compatibility and run service contract tests |
| Source builder behavior changes during extraction | Copy logic unchanged and avoid formula edits |
| Diagnostics orchestration loses shared helpers | Import `_now_text`, `_optional_float`, `_slug` from the new source module |
| Browser QA is skipped despite a runtime import issue | Run service import tests; browser only if visible Streamlit flow changes |
| Curve context extraction accidentally drags component interpretation into a generic helper | Keep `_build_curve_context` and `_component_universe_tickers` in diagnostics for 7-02; only move shared curve math / snapshot helpers |
