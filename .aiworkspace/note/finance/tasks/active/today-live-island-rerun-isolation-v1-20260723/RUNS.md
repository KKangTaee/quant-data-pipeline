# Today Live Island Rerun Isolation V1 Runs

## 2026-07-23 Investigation

- `main-dev` server가 port 8521에서 실행 중임을 process cwd와 listening port로 확인했다.
- 실제 Today에서 18초 동안 Streamlit status를 샘플링해 periodic run이 약 14.9초 간격으로 발생함을 확인했다.
- 1초 간격 React sample에서 countdown은 변하고 chart SVG path는 유지됨을 확인했다.
- `today_page.py`, `TodayWorkbench.tsx`, `TodayPortfolioChart.tsx`, 기존 contract test와 commit diff를 대조했다.

## Design Verification

- placeholder scan: `TBD`, `TODO`, deferred implementation marker 없음.
- consistency: OPEN/EOD waiting heartbeat, CLOSED confirmed no heartbeat, 300/600초 계약이 PLAN/DESIGN에서 일치함.
- scope: 별도 API/push, provider cadence, DB schema, pre/after market는 명시적으로 제외함.

## Implementation Plan Verification

- `writing-plans` 절차로 projector/policy, React view split, minimal island/conditional fragment, phase event, Browser QA/docs를 3개 TDD task로 분해했다.
- spec coverage, placeholder, type/status consistency, excluded scope를 self-review했다.
- `git diff --check`를 통과했다.

## 2026-07-23 Task 1 — Render Isolation

- baseline Python 107개와 React 13개, typecheck 통과.
- RED: public portfolio projector/heartbeat policy import 2개가 실패했다.
- GREEN: projector/policy focused tests와 Today read-model 회귀 통과.
- RED: React split view가 missing component로, Python timer isolation이 missing file로 실패했다.
- GREEN: context/portfolio/actions SSR 3개, timer isolation, Today Python 54개, React 전체 16개, typecheck/build 통과.
