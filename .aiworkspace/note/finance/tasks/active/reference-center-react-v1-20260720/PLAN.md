# Reference Center React V1 Plan

Status: Design Approved / Implementation Not Started
Date: 2026-07-20

## 이걸 하는 이유?

현재 Reference는 Guide와 Glossary가 분리돼 있고, Streamlit native UI와 오래된 catalog 때문에
사용자가 현재 제품 기능·상태·다음 행동을 빠르게 찾기 어렵다.
Reference 기능 자체는 유지하되 검색 중심 단일 React 화면으로 통합해
화면별 설명 중복과 콘텐츠 drift를 함께 줄인다.

## Goal

- `Reference` 단일 navigation entry를 만든다.
- Guide, 상태/용어, 문제 해결을 하나의 검색과 상세 패널로 통합한다.
- 현재 사용자 화면과 연결되는 stable deep link와 contextual help를 제공한다.
- legacy·개발자 용어와 로그/진단 surface를 사용자 Reference에서 제외한다.

## Tentative Roadmap

| 차수 | 목적 | 주요 범위 | 완료 조건 |
| --- | --- | --- | --- |
| 1차 | catalog / contract 정식화 | current surface catalog, schema, search projection, drift guard | current surface 필수/legacy 금지/ID·destination 계약 테스트 통과 |
| 2차 | React workbench | 통합 검색, 필터, 6개 여정, 결과, drawer/sheet | typecheck, Vitest, production build와 component contract 통과 |
| 3차 | navigation / contextual help 통합 | 단일 Reference page, deep link, 화면 이동 intent, contextual help 확대 | `/guides`·`/glossary` primary navigation 제거 및 허용 destination 검증 |
| 4차 | legacy 제거 / docs / QA | old renderer/catalog 정리, 문서 sync, desktop/900/420 QA | focused regression, diff-check, actual Browser QA와 screenshot 완료 |

## In Scope

- `app/services/reference_center.py`
- `app/web/reference_center.py`
- `app/web/reference_center_react_component.py`
- `app/web/streamlit_components/reference_center_workbench/`
- `app/services/reference_contextual_help.py`
- `app/web/reference_contextual_help.py`
- `app/web/streamlit_app.py`
- Reference focused Python / React tests
- Reference 관련 durable docs와 task/root handoff 정렬

## Out Of Scope

- 로그 관리 tab
- run history / failure artifact / raw registry browser
- Reference 안의 ingestion/job 실행
- provider fetch, DB write, registry/saved write
- broker order, live approval, auto rebalance
- 내부 `GLOSSARY.md` 전체를 자동 생성하거나 사용자 UI에서 그대로 노출
- Reference와 무관한 화면 재설계

## Stop Condition

- 설계 문서에 대한 사용자 검토가 끝나기 전에는 구현 계획이나 코드를 시작하지 않는다.
- 구현 중 화면 의미나 범위가 본 설계와 달라지면 사용자 확인 전까지 해당 변경을 멈춘다.
