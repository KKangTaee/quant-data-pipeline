# Finance Flows

Status: Active
Last Verified: 2026-06-23

## Main User Flow

```text
Workspace > Ingestion
  -> Workspace > Overview
  -> Backtest > Backtest Analysis
  -> Backtest > Practical Validation
  -> Backtest > Final Review
  -> Operations > Operations Console
  -> Operations > Portfolio Monitoring
```

`Workspace > Overview`는 Backtest의 필수 선행 단계가 아니라 시장 context / data health 확인 표면이다.
Sentiment, futures macro, Why It Moved는 판단 보조 정보이며 validation gate, trade signal, monitoring signal을 만들지 않는다.

화면 경계가 code layer / storage boundary와 섞일 때는 [System Boundaries](../architecture/SYSTEM_BOUNDARIES.md)를 먼저 확인한다.

## Overview Futures Monitor Flow

`Workspace > Overview > Futures Monitor`는 선물/매크로 context를 읽는 화면이며 provider run 진단이나 trading signal 화면이 아니다.

기본 화면의 정보 소유권은 다음처럼 유지한다.

- Workbench context bar: 관찰 범위, 시간/봉/차트 범위, 데이터 상태, 다음 행동을 한 줄로 요약한다.
- 자료 갱신 module: 실제 갱신 행동을 소유한다. 실시간 차트 자료는 선택 선물 1분봉 / 최신 candle age / 60초 자동 확인 대상을 보여주고, 매크로 일봉 자료는 1D OHLCV / macro context 기준일 / daily coverage를 보여준다.
- Compact watch strip: 선택 심볼의 이름, 계약 설명, 15m/60m 움직임, symbol-level stale state만 보여준다. 심볼 선택 multiselect는 `관찰 대상 편집` disclosure 안에 둔다.
- Macro Context: 오늘 기준 시장 브리프, 근거 강도 / 자료 기준, score chip, 현재 score evidence를 한 카드에서 읽는다.
- Chart workspace: “이 차트에서 확인할 것”을 먼저 말하고, 차트 범위와 symbol-level 상태를 이어서 보여준다. Page-level provider run rows / latest candle details는 반복하지 않는다.
- Disclosure: React `현재 근거`는 `매크로 컨텍스트` 내부에서 현재 score evidence를 맡고, 하단 `원본 데이터 / 계산 추적`은 `매크로 컨텍스트 -> 최근 흐름 -> 과거 점검`의 화면 섹션별 원본 연결과 `현재 점수 -> 구성 기여 -> 선물 일봉 변화 -> 과거 표본` 순서로 읽는다. 진단 / Provider 근거는 별도 접힌 상세로 둔다.

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
- Overview의 Sentiment, Futures Monitor, Why It Moved는 시장 배경 / 조사 단서이며 Practical Validation PASS / BLOCKER가 아니다.
- 부족 provider data는 Practical Validation Provider Gaps에서 확인하고, 수집 가능한 항목은 ingestion job을 통해 보강한다.
- Ingestion의 current listing snapshot, SEC identity cross-check, computed snapshot lifecycle row는 survivorship PASS 근거가 아니다. Form 25 delisting row도 delisting evidence이며, Form 25 부재를 active listing proof로 해석하지 않는다.

## Detailed Flow Docs

| Need | Document |
|---|---|
| 화면 stage와 code / storage boundary가 섞일 때 | [System Boundaries](../architecture/SYSTEM_BOUNDARIES.md) |
| Backtest UI, history, saved replay, Practical Validation, Final Review 화면 흐름 | [BACKTEST_UI_FLOW.md](./BACKTEST_UI_FLOW.md) |
| Backtest Analysis 1단계 closeout 현재 상태 | [BACKTEST_ANALYSIS_STAGE1_CLOSEOUT.md](./BACKTEST_ANALYSIS_STAGE1_CLOSEOUT.md) |
| 후보 생성부터 최종 선정 후 dashboard까지의 Portfolio Selection 흐름 | [PORTFOLIO_SELECTION_FLOW.md](./PORTFOLIO_SELECTION_FLOW.md) |
| Final Review selected-route waiver 허용 조건 | [STRUCTURED_WAIVER_POLICY.md](./STRUCTURED_WAIVER_POLICY.md) |
