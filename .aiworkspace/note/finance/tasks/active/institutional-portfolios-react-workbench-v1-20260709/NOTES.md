# Institutional Portfolios React Workbench V1 Notes

## Product Direction

- First viewport must answer: "이 기관의 포트폴리오가 어떻게 구성되어 있나?"
- Ingestion readiness is supporting context, not the protagonist of this tab.
- React component owns visual layout. Python owns DB loader calls and payload calculation.
- 13F caveats remain visible: quarterly delayed filings, up to 45-day filing lag, long-only / no shorts / derivative and hedge limitation, best-effort CUSIP-symbol mapping.

## Current Weakness From V1

- `app/web/institutional_portfolios.py` starts with `Manager Search` and DB readiness warnings.
- Visuals are Streamlit metrics and tables only; no portfolio allocation chart.
- React workbench pattern exists elsewhere but is not used for this surface.
- Empty DB state makes `Workspace > Institutional Portfolios` feel like an ingestion console.
