# Overview Service Split V25-V32 Plan

## 이걸 하는 이유?

`app/services/overview_market_intelligence.py`가 7,788줄의 Overview 계산 본문을 모두 가진 상태라, 화면 탭은 분리되었지만 서비스 계산 경계는 아직 한 파일에 모여 있다. 이번 작업은 UI 동작을 유지하면서 Market Context, Market Movers, Events, Sentiment, Data Health, Why It Moved의 서비스 본문을 도메인별 파일로 옮겨 수정 위치와 책임 경계를 명확히 한다.

## Scope

- 대상: `app/services/overview_market_intelligence.py`, `app/services/overview/*.py`, Overview service contract tests, 관련 문서
- 비대상: Overview 화면 UX 변경, DB schema 변경, ingestion job 동작 변경, provider 수집 정책 변경
- 원칙: 기존 public import path는 중간 단계에서 compatibility facade로 보존한다.

## 차수 계획

| 차수 | 목적 | 파일 범위 | 완료 조건 |
|---|---|---|---|
| 25차 | public 계약 / 작업 기준 고정 | task docs, tests | 분리 대상과 QA 기준 문서화 |
| 26차 | Sentiment 본문 분리 | `overview/sentiment.py` | sentiment service surface가 자체 구현을 소유 |
| 27차 | Events 본문 분리 | `overview/events.py` | event calendar / macro week lane이 자체 구현을 소유 |
| 28차 | Data Health 본문 분리 | `overview/data_health.py` | collection ops / ingestion handoff가 자체 구현을 소유 |
| 29차 | Market Movers 본문 분리 | `overview/market_movers.py` | movers / group leadership / breadth가 자체 구현을 소유 |
| 30차 | Market Context 본문 분리 | `overview/market_context.py` | cockpit / source confidence가 자체 구현을 소유 |
| 31차 | Why It Moved 본문 분리 | `overview/why_it_moved.py` | catalyst / metadata 조사 helper가 자체 구현을 소유 |
| 32차 | compatibility facade 축소 | `overview_market_intelligence.py`, docs | monolith가 facade로 축소되고 문서가 새 구조를 설명 |

## QA 기준

- 각 차수마다 관련 structural contract test를 먼저 추가하고 실패를 확인한다.
- 구현 후 `py_compile`과 관련 `tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests` 일부 또는 전체를 실행한다.
- 32차 최종에서는 `python -m unittest tests.test_service_contracts.OverviewAutomationContractTests tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests`와 `git diff --check`를 실행한다.
