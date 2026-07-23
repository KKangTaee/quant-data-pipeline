# Today U.S. Market Session Status V1 Runs

## 2026-07-22 Design Investigation

- finance docs INDEX / ROADMAP / PROJECT_MAP과 recent Today V2 task를 확인했다.
- `app/services/today.py`, `app/web/today_page.py`, Today React TSX/types를 확인했다.
- 기존 Nasdaq official holiday / early-close parser와 DB loader를 확인했다.
- NYSE와 Nasdaq 공식 정규장·휴장·조기폐장 자료를 확인했다.
- product scope와 session semantics를 사용자와 확정했다.

## Verification

### Python

- `.venv/bin/python -m unittest tests.test_today_home` — 39 tests passed.
- `.venv/bin/python -m unittest -k today -k market_event tests.test_service_contracts` — 9 tests passed.
- `py_compile` — `today.py`, `today_market_session.py`, `today_page.py`, `today_react_component.py` passed.
- calendar source-status 회귀는 먼저 `unexpected keyword argument 'calendar_statuses'` RED를 확인한 뒤, holiday/early-close loader 중 하나라도 비정상이면 `LIMITED`가 되는 GREEN 2개를 확인했다.

### React

- Vitest — 10 tests passed.
- TypeScript typecheck — passed.
- Vite production build — passed; canonical `component_static/` rebuilt.
- `LIMITED` 일정이 실제 장중 시각에서 `OPEN`을 반환하는 RED를 확인한 뒤 `STALE`·경계 없음으로 닫는 GREEN을 확인했다.

### Actual Browser QA

- desktop 1280×720: `장 진행 중`, 뉴욕·한국 시각, ET/KST 정규장 시간, 마감 countdown을 actual DB-backed root `/`에서 확인했다.
- 09:30 ET 직전 `개장 전` 상태가 경계 통과 뒤 rerun 없이 `장 진행 중`으로 바뀌고 countdown이 개장까지에서 마감까지로 전환됐다.
- 2.1초 관찰에서 countdown이 2초 감소해 local one-second timer를 확인했다.
- mobile 420×900: four-cell strip이 한 열로 재배치되고 iframe 내부 horizontal overflow가 없었다.
- desktop/mobile browser console warning·error 0건.
- QA screenshot: repository root의 generated `today-us-market-session-status-v1-qa.jpg`; 커밋 대상에서 제외했다.

### Independent Review

- Important: early-close loader status 유실 — `calendar_statuses` 전달과 source-status 회귀로 수정했다.
- Important: `LIMITED` 일정의 authoritative open 상태 — React resolver가 `STALE`로 fail-closed하도록 수정했다.
- Minor: 461–520px 구간의 two-column 밀도 — 단일 열 breakpoint를 계획의 520px로 맞췄다.
