# Reference Guides Center V1 2026-06-07

Status: Completed

## 이걸 하는 이유?

`Reference > Guides`는 현재 포트폴리오 후보 선정 guide로는 쓸 만하지만, 현재 finance console 전체 흐름인 Overview, Ingestion, Backtest, Practical Validation, Final Review, Operations를 안내하기에는 범위가 좁다.

사용자가 데이터 stale, `NOT_RUN`, Final Review 후보 미노출, Portfolio Monitoring stale scenario 같은 문제를 만났을 때 Reference에서 바로 owner screen, safe action, stop condition을 찾게 만든다.

## Scope

- 1차 구현 범위: `Reference > Guides`를 task-first Reference Center로 개편
- 기존 portfolio-selection guide는 `후보를 모니터링 후보로 보내기` journey로 보존
- 최소 journey / concept / records / troubleshooting catalog 추가
- Streamlit render와 content catalog를 분리해 future drift를 줄임
- Canonical flow docs와 root handoff log를 최소 동기화

## Stop Condition

- Reference catalog contract test가 RED 후 GREEN으로 통과한다.
- `app/web/reference_guides.py`와 새 catalog module이 `py_compile`을 통과한다.
- Browser QA에서 `Reference > Guides` 첫 화면이 task-first landing으로 보이고 기존 portfolio journey로 진입할 수 있다.
- Reference에서 job execution, registry write, DB write, provider fetch, broker order, auto rebalance 동작을 추가하지 않는다.

## Out Of Scope

- `Reference > Glossary` 전면 개편
- Overview / Backtest / Practical Validation / Monitoring 화면에서 Reference contextual link 연결
- 새 persistence, registry rewrite, saved setup rewrite
- live approval, broker order, account sync, auto rebalance guide
- 전체 markdown docs 자동 색인
