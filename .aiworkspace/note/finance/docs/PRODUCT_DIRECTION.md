# Product Direction

Status: Active
Last Verified: 2026-07-19

## Product Summary

`finance` 프로젝트는 데이터 수집, 백테스트, 실전 후보 검증, 최종 포트폴리오 선정 이후 모니터링까지 이어지는 퀀트 리서치 워크스페이스다.

현재 제품의 중심은 "좋아 보이는 백테스트 결과"를 바로 투자 판단으로 받아들이지 않고,
데이터 신뢰도, ETF 운용성, holdings / exposure, macro context, stress / sensitivity, Final Review evidence를 통해
실전 추적 가능한 후보인지 확인하는 데 있다.

2026-07-08 master 병합 후 현재 제품은 네 축으로 읽는다.

| 축 | 현재 의미 |
|---|---|
| Data / Market Context | DB-backed 가격·지수 EPS·SEP·macro·futures·sentiment를 바탕으로 시장 상태를 입체적으로 본다. Market Context 기본 화면은 S&P 500 상대 멀티플과 예상 실적 기반 지수 시나리오를 분리해 보여준다 |
| Transparent Macro Evidence | FRED, futures OHLCV, FOMC / BLS / BEA calendar, CNN Fear & Greed, AAII sentiment 같은 macro / sentiment context를 source와 freshness가 보이는 형태로 표시한다 |
| Backtest To Monitoring Workflow | Backtest Analysis에서 후보를 만들고, Practical Validation과 Final Review를 거쳐 Operations Portfolio Monitoring에서 사후 확인한다 |
| UI / Engine Boundary | Streamlit UI는 화면과 session state를 담당하고, 데이터 수집 / loader / runtime / service read model은 Streamlit-free 계층에 둔다 |

## Target Experience

- 사용자는 Backtest Analysis에서 전략이나 저장된 포트폴리오 mix를 후보 source로 만든다.
- Workspace > Overview는 Market Context, Market Movers / Why It Moved, Futures Macro, Sentiment, Events로 시장 context를 보여준다. Market Context는 5년 후행 PER 상대 구간과 FOMC 거시 가정 기반 EPS/SPX 시나리오를 보여주며, 공식 적정가나 거래 신호로 표현하지 않는다. Sector evidence는 Market Movers가 소유하고 수집 결과·실패 확인은 Workspace > Ingestion으로 분리한다.
- Workspace > Institutional Portfolios는 Overview Market Movers와 분리된 read-only research surface로, 투자 대가 / 기관별 delayed SEC Form 13F portfolio를 React workbench에서 포트폴리오 allocation, 상위 보유, 분기별 reported change, 섹터 노출, 종목별 보유기관 drill-down으로 탐색한다.
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
- `Workspace > Institutional Portfolios`
- `Backtest > Backtest Analysis`
- `Backtest > Practical Validation`
- `Backtest > Final Review`
- `Operations > Portfolio Monitoring`
- `Reference > Guides`

현재 구현 완료로 보는 큰 흐름:

- Overview Market Intelligence는 Market Context, Market Movers / Why It Moved manual investigation, sector breadth / group leadership evidence, Futures Macro, events calendar, sentiment, data-health handoff, browser-session auto refresh까지 production baseline을 갖췄다. `Futures Monitor`와 `Sector / Industry` standalone tab 표현은 current primary surface가 아니라 retained data / helper context로 본다.
- Institutional Portfolios는 SEC Form 13F 공식 data sets를 DB로 적재한 뒤 기관별 holdings를 allocation donut, 상위 보유 리스트, 신규 / 증가 / 감소 / 전량 매도 후보 board, 섹터 노출 bar, 종목별 보유 기관 reverse lookup으로 읽는 Workspace research surface다. DB가 비어 있으면 clearly labeled preview workbench만 보여주며 실제 보유로 표현하지 않는다. 13F 지연, long holdings 한계, CUSIP-symbol mapping caveat를 항상 표시하며 추천 / 매수매도 신호 / live approval로 해석하지 않는다.
- Macro / sentiment context는 DB-backed collection과 loader를 통해 읽고, 화면에서는 freshness / source / partial state를 숨기지 않는다.
- Backtest Analysis는 기존 ETF / factor / mix 후보와 Risk-On Momentum 5D Daily Swing research lane을 포함한다. Risk-On Momentum daily signal governance는 아직 Practical Validation / Final Review / Portfolio Monitoring에 연결하지 않았다.
- Practical Validation V2 P2 / P3, Final Review selection readiness, Operations > Portfolio Monitoring read-only monitoring / recheck 연결은 closeout 완료 상태다.
- Operations는 Portfolio Monitoring만 사용자-facing 화면으로 둔다. 최종 선정 후보의 그룹·항목 lifecycle, 공통 기준 성과, contribution, 개별 상세와 review context를 이 화면에서 바로 확인한다. 수집 실행 결과, run history, log, failure CSV는 `Workspace > Ingestion > 실행 기록 / 결과`가 소유하며 Portfolio Monitoring에 진단 패널로 중복하지 않는다.

현재 active phase는 없다. 다음 개발은 사용자가 승인한 구체적 scope를 새 task 또는 phase로 열어 진행한다.
