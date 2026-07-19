# Finance Flows

Status: Active
Last Verified: 2026-07-08

## Main User Flow

```text
Workspace > Ingestion
  -> Workspace > Institutional Portfolios
  -> Workspace > Overview
  -> Backtest > Backtest Analysis
  -> Backtest > Practical Validation
  -> Backtest > Final Review
  -> Operations > Operations Console
  -> Operations > Portfolio Monitoring
```

`Workspace > Overview`는 Backtest의 필수 선행 단계가 아니라 시장 context / data health 확인 표면이다.
`Workspace > Institutional Portfolios`도 Backtest의 필수 선행 단계가 아니라 delayed SEC 13F institutional holdings를 탐색하는 별도 research surface다.
Sentiment, futures macro, Why It Moved는 판단 보조 정보이며 validation gate, trade signal, monitoring signal을 만들지 않는다.
현재 Overview primary tabs는 `Market Context`, `Market Movers`, `Futures Macro`, `Sentiment`, `Events`다.
`Market Context`는 S&P 500의 최근 60개월 후행 PER 상대 구간과 FOMC SEP 기반 EPS/SPX 시나리오를 두 React 그래프로 읽는다. 36개월은 민감도이며, actual As-Reported TTM EPS가 없으면 예상 지수 숫자를 표시하지 않는다.
`Futures Monitor`와 `Sector / Industry` standalone tab은 current primary navigation이 아니며, 관련 데이터는 Futures Macro / Market Movers의 context evidence로 읽는다.

화면 경계가 code layer / storage boundary와 섞일 때는 [System Boundaries](../architecture/SYSTEM_BOUNDARIES.md)를 먼저 확인한다.

## Overview Futures Macro Flow

`Workspace > Overview > Futures Macro`는 저장된 futures daily OHLCV를 읽어 오늘의 재가격화, 다중 기간 현재 패턴, 다음 5D / 20D 조건부 위험 체제를 한 흐름에서 확인하는 단기 매크로 레이더다. 장기 경제사이클, provider run 진단, 확정 예측, trading signal 화면이 아니다.

기본 화면의 정보 소유권은 다음처럼 유지한다.

- Current regime: 오늘 shock과 trailing 1D / 5D / 20D family feature로 현재 체제와 지속·전환 상태를 먼저 읽는다. 현재 카드는 관측이며 미래 확률이 아니다.
- Conditional outlook: 겹치는 날짜를 독립 episode 간격으로 줄인 유사 패턴의 다음 5D / 20D 결과 분포를 기본으로 계산한다. 30개 미만은 숫자를 숨기고, 30~59개는 최대 `PROVISIONAL`, 60개 이상도 시간순 Brier / calibration gate를 충족해야 `VERIFIED`다.
- Pattern evidence: 최근 60개 일봉을 한 선으로 잇지 않고 `20D 전 → 5D 전 → 현재` 핵심 관측 시점만 실선으로 표시한다. `관측만 / 다음 5D / 다음 20D`를 전환하면 현재점에서 선택 horizon 말일의 과거 유사 episode 중앙 위치까지를 한 개의 `예상 순이동` 점선으로 직접 연결하고, 말일의 축별 q25~q75 도착 범위 하나만 옅은 음영 박스로 표시한다. 점선은 중간 일별 경로가 아니며 서비스의 stepwise median은 검증용으로 보존한다. 세 관측 anchor와 5D/20D 전망은 두 말일 terminal/range로 계산한 하나의 공통 visible-data 좌표계를 사용하므로 horizon 전환 때 관측 위치가 움직이지 않는다. 화면에서 제거한 중간 median과 q25~q75는 scale을 바꾸지 않는다. 좌표는 `현재 위치 + 표준화된 조건부 이동`이며 절대 경제상태·가격 목표·실제 미래 경로가 아니다. 우측 확률 카드가 체제 확률의 primary surface이고, 경로는 별도 시간순 오차·baseline·coverage 검증 상태를 더 보수적으로 적용한다.
- Asset pathways: 주식 위험선호, 금리 부담, 달러 압력, 안전자산, 원자재·물가는 전체 시장 체제의 보조 근거이며 독립 추천으로 승격하지 않는다.
- Disclosure: React 방법론에는 독립 표본, Brier / baseline Brier, calibration, continuous futures roll 한계를 둔다. 하단 `원본 데이터 / 계산 추적`은 원시 점수와 daily candle 검산용 appendix로 남긴다.

## Backtest Selection Flow

| Step | What Happens | Main Files |
|---|---|---|
| Backtest Analysis | 단일 전략, compare, saved mix로 후보 source 생성 | `app/web/backtest_analysis.py`, `app/web/backtest_single_*.py`, `app/web/backtest_compare/` |
| Practical Validation | 후보 source를 12개 진단과 module gate로 검증하고, Gate 미통과 저장-only row는 audit trail로만 남긴다 | `app/web/backtest_practical_validation/` |
| Final Review | Practical Validation Gate를 통과한 후보만 source picker에 표시하고 최종 select / hold / reject / re-review 판단 | `app/web/backtest_final_review/` |
| Operations Console | 선정 후 monitoring과 system / data health 확인 입구 | `app/web/operations_overview.py` |
| Portfolio Monitoring | 선정 이후 성과 재확인과 read-only monitoring / recheck signal 확인 | `app/web/final_selected_portfolio_dashboard*.py` |

## Practical Validation Provider Flow

```text
Workspace > Ingestion
  -> ETF provider source map discovery
  -> ETF operability / holdings / exposure snapshot
  -> FRED macro market-context snapshot
  -> symbol lifecycle evidence
     (SEC Form 25 actual delisting evidence,
      Nasdaq current listing snapshot,
      SEC CIK / ticker cross-check,
      computed repeated-observation summary)
  -> MySQL
  -> finance/loaders/provider.py / macro.py / universe.py
  -> Practical Validation diagnostics
```

## Flow Rules

- Practical Validation result는 최종 투자 승인 기록이 아니다.
- Practical Validation의 `검증 결과 저장(기록용)`은 Final Review 후보 등록이 아니다. Final Review에는 Gate를 통과한 result만 표시한다.
- Practical Validation의 최신 runtime replay 결과는 현재 세션에서 사용자가 직접 실행한 뒤에만 표시한다.
- Final Review decision도 broker order나 auto rebalance가 아니다.
- Operations > Portfolio Monitoring은 read-only monitoring surface이며 monitoring log 자동 저장, live approval, broker order, auto rebalance를 하지 않는다.
- Overview의 Sentiment, Futures Macro, Why It Moved는 시장 배경 / 조사 단서이며 Practical Validation PASS / BLOCKER가 아니다.
- 부족 provider data는 Practical Validation Provider Gaps에서 확인하고, 수집 가능한 항목은 ingestion job을 통해 보강한다.
- Ingestion의 current listing snapshot, SEC identity cross-check, computed snapshot lifecycle row는 survivorship PASS 근거가 아니다. Form 25 delisting row도 delisting evidence이며, Form 25 부재를 active listing proof로 해석하지 않는다.

## Detailed Flow Docs

| Need | Document |
|---|---|
| 화면 stage와 code / storage boundary가 섞일 때 | [System Boundaries](../architecture/SYSTEM_BOUNDARIES.md) |
| 투자 대가 / 기관별 delayed SEC Form 13F portfolio 탐색 | [INSTITUTIONAL_PORTFOLIOS_FLOW.md](./INSTITUTIONAL_PORTFOLIOS_FLOW.md) |
| Backtest UI, history, saved replay, Practical Validation, Final Review 화면 흐름 | [BACKTEST_UI_FLOW.md](./BACKTEST_UI_FLOW.md) |
| Backtest Analysis 1단계 closeout 현재 상태 | [BACKTEST_ANALYSIS_STAGE1_CLOSEOUT.md](./BACKTEST_ANALYSIS_STAGE1_CLOSEOUT.md) |
| 후보 생성부터 최종 선정 후 dashboard까지의 Portfolio Selection 흐름 | [PORTFOLIO_SELECTION_FLOW.md](./PORTFOLIO_SELECTION_FLOW.md) |
| Final Review selected-route waiver 허용 조건 | [STRUCTURED_WAIVER_POLICY.md](./STRUCTURED_WAIVER_POLICY.md) |
