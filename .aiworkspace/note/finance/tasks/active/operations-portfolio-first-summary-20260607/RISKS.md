# Risks

## 2026-06-07

- Operations Overview can read persisted selected dashboard setup, but it cannot read current Streamlit session-only monitoring scenario results from Portfolio Monitoring. 2차 therefore treats scenario freshness as explicit payload metadata when available and setup/review readiness otherwise.
- Browser QA still shows Streamlit `_stcore/health` and `_stcore/host-config` 404 console entries under the `/operations` route, matching the prior Operations QA residual; the page content rendered correctly.
