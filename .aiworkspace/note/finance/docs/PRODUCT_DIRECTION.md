# Product Direction

Status: Active
Last Verified: 2026-07-26

## Product Promise

`finance`는 시장 조사, 전략 실험, 실전 검증, 최종 판단과 선정 이후 모니터링을
DB-backed evidence로 연결하는 **Evidence-first 퀀트 투자 리서치 워크스페이스**다.

좋아 보이는 백테스트 결과를 바로 투자 대상으로 받아들이지 않는다. 사용자가
데이터의 기준 시점과 coverage, 운용 가능성, 비용·유동성·구성 위험, stress와
robustness를 확인하고 “계속 추적할 후보인가?”를 근거와 함께 판단하게 한다.

## Who It Is For

- 전략과 포트폴리오를 직접 실험하되 수익률 하나로 결론 내리고 싶지 않은 리서처
- 시장·재무·기관 보유 맥락과 백테스트 근거를 같은 기준으로 확인하려는 사용자
- 후보 생성부터 검증, 판단 기록과 사후 모니터링까지 재현 가능한 흐름이 필요한 운영자
- 데이터·전략·UI의 책임 경계를 유지하며 기능을 확장하는 개발자와 AI 작업자

현재 범위는 개인 또는 소규모 리서치 workflow다. broker 계좌, 주문 시스템이나
수탁·운용 업무를 대신하는 제품이 아니다.

## User Journey

```text
Data Operations
  -> Research
  -> Portfolio Lab
       -> Backtest Analysis
       -> Practical Validation
       -> Final Review
  -> Portfolio Monitoring
  -> Research 재확인 또는 Portfolio Lab 재실행
```

Data Operations는 최초 설치 단계가 아니라 전체 workflow에 evidence를 공급하는
기반이다. Research는 Portfolio Lab의 강제 선행 gate가 아니라 후보와 시장 맥락을
해석하기 위한 조사 surface다.

Portfolio Lab에서는 전략·mix 후보를 만들고, Practical Validation에서 데이터
신뢰도와 실전 운용성 근거를 확인한 뒤, Final Review에서 추적 여부와 이유를
기록한다. 선정 후보는 Portfolio Monitoring에서 성과·기여·보유 변화와 재검토
조건을 확인하고 필요하면 조사나 재실행으로 돌아간다.

## Current Product Surfaces

Finance Console의 current top navigation은 `Research / Portfolio / Data / Help`다.

| Group | Surface | 사용자가 끝낼 수 있는 일 |
|---|---|---|
| Research | Today | 미국 시장 세션, 저장된 시장 근거, 다음 일정과 대표 포트폴리오 상태를 첫 화면에서 파악한다. |
| Research | Market Research | 경제 사이클, 선물 매크로, 심리, 일정, S&P 500 가치평가, 변동 종목과 미국 개별 종목을 기준일·source와 함께 조사한다. |
| Research | Institutional Holdings | delayed SEC Form 13F로 기관별 allocation·보유 변화·섹터 노출과 종목별 보유 기관을 탐색한다. |
| Portfolio | Portfolio Lab | 전략을 실행·비교하고 후보를 만든 뒤 Practical Validation과 Final Review까지 이어간다. |
| Portfolio | Portfolio Monitoring | 최종 선정 후보와 직접 등록한 미국 주식·ETF의 공통 기준 성과, 기여도, 보유 변화와 재검토 조건을 추적한다. |
| Data | Data Operations | 가격·재무·거시·provider·13F 데이터를 MySQL에 수집하고 제품의 evidence 준비 상태를 관리한다. |
| Help | Reference Center | 제품 개념, 판단 기준, 데이터 제한, 문제 해결 방법과 관련 화면을 검색한다. |

Today와 Research의 macro·sentiment·events·13F 정보는 조사 맥락이다. 자동
투자 신호, Practical Validation PASS, Final Review 승인 또는 Monitoring
경고로 승격하지 않는다.

## Product Principles

| Principle | Meaning |
|---|---|
| Evidence First | 높은 백테스트 수익률보다 데이터 신뢰도, 운용 가능성과 검증 근거를 우선한다. |
| DB-Backed Runtime | 기본 흐름은 `Ingestion -> DB -> Loader / Service -> Runtime -> UI`이며 UI가 provider를 직접 조회하지 않는다. |
| Point-in-Time Before Convenience | 과거 시점에 알 수 있었던 데이터와 이후 수정·발표된 정보를 구분한다. |
| Visible Data State | source, 기준일, freshness, coverage와 partial·stale·unavailable 상태를 숨기지 않는다. |
| NOT_RUN Is Not Pass | 자료나 구현이 없어 실행하지 못한 검증을 통과로 취급하지 않는다. |
| Context Is Not Approval | 시장 맥락과 기관 보유 정보는 판단 근거이지 자동 추천이나 승인 권한이 아니다. |
| Human Decision Boundary | 후보 선정, 보류, 제외와 재검토는 사람이 근거를 읽고 기록하는 판단이다. |
| Layer Ownership | Python이 수집·계산·검증·저장 authority를, Streamlit과 React가 route·interaction·presentation 경계를 맡는다. |

## Safety And Non-Goals

현재 제품이 제공하지 않는 기능:

- broker account 연결과 실제 보유 자동 동기화
- live approval, 주문 생성과 자동 매매
- auto rebalance 또는 broker-side allocation 실행
- 투자 성과나 수익 보장
- sentiment, news, events와 13F를 자동 매수·매도 신호로 변환
- 불완전한 provider field를 완전한 사실로 간주
- full raw provider response나 holdings를 workflow JSONL에 복제

Final Review decision과 Portfolio Monitoring의 재검토 표시는 투자 자문, 주문 승인
또는 자동 운용 명령이 아니다.

## Current Maturity And Known Limits

현재 구현된 baseline:

- Research, Portfolio, Data, Help의 7개 top-level surface와 목적형 navigation
- MySQL-backed market·financial statement·macro·provider·13F evidence
- 단일 전략과 portfolio mix 실행, 비교, 저장·재실행과 후보 source 생성
- Practical Validation의 데이터·운용·robustness·construction evidence와 보강 flow
- Final Review의 gate-aware 판단 기록과 Portfolio Monitoring handoff
- 선정 이후 direct stock·ETF와 selected strategy의 read-only monitoring / recheck
- Python / Streamlit / React + TypeScript의 분리된 정상 화면과 fallback 경계

계속 보수적으로 다루는 제한:

- historical universe membership, delisting과 일부 provider coverage는 완전하지 않다.
- survivorship bias와 look-ahead bias는 현재 구현이 완전히 제거했다고 주장하지 않는다.
- SEC 13F는 보고 지연, long holdings 중심 범위와 identifier mapping 한계가 있다.
- macro·sentiment·conditional outlook은 독립 시계열 검증 gate를 통과하지 못하면
  확률이나 확정 전망으로 공개하지 않는다.
- local MySQL 준비와 source별 수집 상태에 따라 화면 evidence가 partial 또는
  unavailable일 수 있다.

## Related Canonical Docs

- 현재 상태와 다음 승인 결정: [Roadmap](./ROADMAP.md)
- 화면·계층·저장 code ownership: [Project Map](./PROJECT_MAP.md)
- 사용자·runtime 흐름: [Flows](./flows/README.md)
- system과 storage boundary: [System Boundaries](./architecture/SYSTEM_BOUNDARIES.md)
- 데이터 의미와 저장 정책: [Data Documentation](./data/README.md)
