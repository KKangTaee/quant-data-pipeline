# Institutional Holdings React Parity V1 Status

Status: Completed
Started: 2026-07-25

## Progress

- 2026-07-25: Request classified as a focused multi-step Institutional Holdings UI task.
- 2026-07-25: Existing completed Institutional context-first task, current Python / React ownership, and Today / Market Research patterns reviewed.
- 2026-07-25: Actual 1280px and 420px render comparison confirmed duplicate Streamlit / React shell, visual-token drift, navigation mismatch, manager-control competition, and delayed mobile first-read.
- 2026-07-25: User approved the direction that the normal user-facing surface should follow Today / Market Research: React owns the complete visible page while Streamlit remains a thin route / data / event / fallback adapter.
- 2026-07-25: Written design drafted for React ownership, component boundaries, event states, visual parity, responsive behavior, fallback and QA.
- 2026-07-25: Visual Companion compared `A · Editorial Research`, `B · Today Decision Canvas`, and `C · Modular Research Studio` with the same Berkshire data and preserved feature set.
- 2026-07-25: User selected `C · Modular Research Studio` as the final visual direction, replacing the briefly stated B preference. The spec now uses a desktop research rail / main canvas and tablet/mobile studio switcher / drawer.
- 2026-07-25: Added a canonical four-destination studio contract and `InstitutionalStudioShell`; desktop uses a deep blue-gray research rail while 980px 이하 uses the same navigation in a drawer.
- 2026-07-25: Moved manager context/search, data freshness, SEC dataset inputs/result, caveats and page heading into React. Healthy React rendering no longer shows the outer Streamlit title/help/refresh/detailed-table shell.
- 2026-07-25: Preserved URL/local ZIP/User-Agent refresh inputs through a new explicit `collect_sec_13f_dataset` event. Streamlit remains the route, DB read-model, server event and unavailable fallback adapter.
- 2026-07-25: Actual QA passed for Berkshire, Bridgewater manager search, AAPL detail/chart, unresolved Bridgewater CUSIP guardrail, 1280/760/420 layout and mobile drawer. No browser errors or warnings were recorded.
- 2026-07-25: Mobile rerun QA found and fixed an open-drawer persistence issue by closing the drawer before manager search/selection and dataset-refresh server events.

## Current Step

전체 roadmap `4/4차` complete.

`C · Modular Research Studio` 구현, automated verification, actual responsive interaction QA와 documentation closeout까지 완료했다.

## Next Action

별도 후속이 없다면 task는 종료 상태다. 장기 흐름은 `docs/flows/INSTITUTIONAL_PORTFOLIOS_FLOW.md`에서 이어서 본다.

## Current Scope Boundary

- 정상 화면 UI는 React가 소유한다.
- Streamlit route, DB / service calls, explicit server events and fallback은 유지한다.
- standalone SPA / new HTTP API / DB schema / ingestion change는 이번 task 밖이다.
