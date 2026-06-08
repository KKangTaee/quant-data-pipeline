# Overview Macro Context Cockpit V1 Plan

Status: Active
Created: 2026-06-08

## 이걸 하는 이유?

`Workspace > Overview`는 이미 Market Movers, Futures Monitor, Sentiment, Sector / Industry, Events, Data Health를 갖고 있지만 첫 화면에서 시장 맥락을 한 번에 연결해 읽기 어렵다.
이번 1차는 새 수집이나 저장 정책 없이 기존 DB-backed read model을 요약해 사용자가 "지금 무엇을 먼저 봐야 하는가"를 빠르게 판단하도록 만든다.

## Tentative 1차-5차 Roadmap

| 차수 | 목적 | 주요 화면 / 파일 | 완료 조건 | 다음 차수 연결 |
| --- | --- | --- | --- | --- |
| 1차 | Overview Macro Context Cockpit V1 | `Workspace > Overview`, `app/services/overview_market_intelligence.py`, `app/web/overview_dashboard*.py`, `app/web/overview_ui_components.py` | 기존 read model만으로 summary-first market context cockpit 표시 | Data Health handoff의 우선순위 근거가 생김 |
| 2차 | Data Health -> Ingestion Handoff | Overview Data Health, Ingestion Console | stale / missing / failed data의 다음 수집 위치가 분명함 | 더 깊은 시각화 전에 data trust 흐름 정리 |
| 3차 | Breadth / Heatmap and Macro Week View | Overview Sector / Industry, Events | broad / concentrated move와 event week를 더 시각적으로 확인 | source quality / retention 정책 판단 |
| 4차 | Source Retention / Provider Hardening | futures / Why It Moved / macro source policy | 저장 정책, provider 품질, replay 경계 승인 후보 정리 | 승인된 항목만 별도 phase/task 전환 |
| 5차 | Overview IA Closeout Candidate | Overview IA, Candidate Ops 후보 | market context 정체성과 legacy candidate area 정리 후보 기록 | 후속 UX/IA 승인 요청 |

현재 작업은 1차만 진행한다.

## Scope

- 기존 DB-backed Overview read model을 합성한 Cockpit V1을 추가한다.
- Futures, Sentiment, Events, Market Movers, Sector / Industry, Data Health를 compact summary로 연결한다.
- source / freshness / partial / missing / failed 상태를 숨기지 않는다.
- macro / futures / sentiment / calendar context는 분석 보조이며 trade signal, Practical Validation PASS/BLOCKER, Final Review decision, monitoring signal이 아니다.

## Out Of Scope

- 새 provider, DB schema, registry / saved JSONL write.
- Overview UI render 중 외부 provider / FRED / crawler 직접 fetch.
- Ingestion 전체 개편, Data Health action queue 구현.
- Market breadth heatmap 본격 구현, Events Quality / Macro Week View 본격 구현.
- Why It Moved V2 저장 정책, Futures provider hardening.
- Candidate Ops IA 변경, React/API migration, live approval / broker / order / auto rebalance.

## Implementation Plan

1. Read required docs and inspect Overview read-model boundaries.
2. Write focused failing tests for the cockpit read model.
3. Add a Streamlit-free cockpit builder in `app/services/overview_market_intelligence.py`.
4. Add cached helper loader in `app/web/overview_dashboard_helpers.py`.
5. Add cockpit CSS/render helpers in `app/web/overview_ui_components.py`.
6. Render the cockpit above Overview tabs in `app/web/overview_dashboard.py`.
7. Run focused tests, py_compile, boundary check, diff check, Streamlit Browser QA.
8. Update task docs, durable docs / root handoff logs only as needed, commit a coherent implementation unit.
