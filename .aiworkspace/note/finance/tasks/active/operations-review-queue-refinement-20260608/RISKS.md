# Risks

## 2026-06-08

- Queue ordering must stay deterministic while using only already-loaded selected dashboard / portfolio setup / run history payloads.
- System / Data Health is diagnostic-only here; queue items must not imply job execution or provider fetch from Operations Overview.
- Direct local navigation to `/operations` can show Streamlit's Page not found modal even though the registered Operations page content renders. This appears to be local Streamlit routing noise and is separate from the 4차 queue read model.
