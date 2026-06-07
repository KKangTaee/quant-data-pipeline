# Product Direction

Status: Active
Last Verified: 2026-06-07

## Product Summary

`finance` 프로젝트는 데이터 수집, 백테스트, 실전 후보 검증, 최종 포트폴리오 선정 이후 모니터링까지 이어지는 퀀트 리서치 워크스페이스다.

현재 제품의 중심은 "좋아 보이는 백테스트 결과"를 바로 투자 판단으로 받아들이지 않고,
데이터 신뢰도, ETF 운용성, holdings / exposure, macro context, stress / sensitivity, Final Review evidence를 통해
실전 추적 가능한 후보인지 확인하는 데 있다.

2026-06-07 master 병합 후 현재 제품은 네 축으로 읽는다.

| 축 | 현재 의미 |
|---|---|
| Data / Market Context | 사용자가 직접 수집한 DB-backed 가격, universe, provider, macro, futures, sentiment 데이터를 바탕으로 시장 상태를 입체적으로 본다 |
| Transparent Macro Evidence | FRED, futures OHLCV, FOMC / BLS / BEA calendar, CNN Fear & Greed, AAII sentiment 같은 macro / sentiment context를 source와 freshness가 보이는 형태로 표시한다 |
| Backtest To Monitoring Workflow | Backtest Analysis에서 후보를 만들고, Practical Validation과 Final Review를 거쳐 Operations Portfolio Monitoring에서 사후 확인한다 |
| UI / Engine Boundary | Streamlit UI는 화면과 session state를 담당하고, 데이터 수집 / loader / runtime / service read model은 Streamlit-free 계층에 둔다 |

## Target Experience

- 사용자는 Backtest Analysis에서 전략이나 저장된 포트폴리오 mix를 후보 source로 만든다.
- Workspace > Overview는 Market Movers, Why It Moved, Sector / Industry, Futures Monitor, Sentiment, Events, Data Health로 시장 context를 보여준다.
- Practical Validation은 후보를 source traits, module gate, provider / macro / robustness / realism evidence로 검증한다.
- Final Review는 selected-route gate를 통과한 후보를 최종 관찰 후보로 저장하되, live approval로 해석하지 않는다.
- Operations > Portfolio Monitoring은 사용자가 만든 monitoring portfolio에 최종 선정 후보를 담고, 명시적 scenario update 후 성과와 review signal을 read-only로 확인한다.
- Workspace > Ingestion은 백테스트와 Practical Validation, Overview에 필요한 DB-backed data snapshot을 수집한다.

## Core Pillars

| Pillar | Meaning |
|---|---|
| Evidence First | 백테스트 수익률보다 데이터 신뢰도와 검증 근거를 우선한다 |
| DB-Backed Runtime | UI에서 직접 원격 fetch하지 않고, ingestion과 loader를 통해 DB 데이터를 사용한다 |
| Practical Validation | 실전 운용 전 ETF 비용, 유동성, holdings, macro, stress, sensitivity를 확인한다 |
| Clear Workflow Boundary | Backtest Analysis, Practical Validation, Final Review, Operations > Portfolio Monitoring의 책임을 분리한다 |
| Context Is Not Approval | sentiment, futures macro, Why It Moved는 시장 배경 / 조사 단서이며 PASS, BLOCKER, trade signal, monitoring signal이 아니다 |
| No Live Trading | 현재 시스템은 live approval, broker order, auto rebalance를 만들지 않는다 |

## Non Goals

- 자동 매매 주문 생성
- broker account holding 자동 연결
- 투자 수익 보장 표현
- 모든 ETF provider를 완전하게 지원하는 universal connector
- 모든 실험 로그와 임시 run artifact를 장기 문서로 보존
- phase 문서와 task 문서를 하나의 무거운 진행 로그로 합치는 것
- 시장 심리, 뉴스, 공시 metadata를 자동 catalyst 판정이나 투자 신호로 바꾸는 것

## Current Product Boundary

현재 사용자-facing 주요 화면:

- `Workspace > Ingestion`
- `Workspace > Overview`
- `Backtest > Backtest Analysis`
- `Backtest > Practical Validation`
- `Backtest > Final Review`
- `Operations > Operations Console`
- `Operations > Portfolio Monitoring`
- `Operations > System / Data Health`
- `Reference > Guides`

현재 구현 완료로 보는 큰 흐름:

- Overview Market Intelligence는 market movers, Why It Moved manual investigation, sector / industry leadership, futures monitor, macro thermometer, events calendar, sentiment, data health, browser-session auto refresh까지 production baseline을 갖췄다.
- Macro / sentiment context는 DB-backed collection과 loader를 통해 읽고, 화면에서는 freshness / source / partial state를 숨기지 않는다.
- Backtest Analysis는 기존 ETF / factor / mix 후보와 Risk-On Momentum 5D Daily Swing research lane을 포함한다. Risk-On Momentum daily signal governance는 아직 Practical Validation / Final Review / Portfolio Monitoring에 연결하지 않았다.
- Practical Validation V2 P2 / P3, Final Review selection readiness, Operations > Portfolio Monitoring read-only monitoring / recheck 연결은 closeout 완료 상태다.
- Operations는 Operations Console을 입구로 삼고, Portfolio Monitoring과 System / Data Health만 사용자-facing 운영 탭으로 둔다. Operations Console은 Portfolio Monitoring Status summary와 Evidence Health mini strip을 먼저 보여준 뒤 daily queue와 primary lane을 표시하며, archive / development-history decision table은 운영 화면에 노출하지 않는다. 과거 데이터 / helper code 삭제는 별도 audit 전까지 하지 않는다.

현재 active phase는 없다. 다음 개발은 사용자가 승인한 구체적 scope를 새 task 또는 phase로 열어 진행한다.
