# Phase 36 Next Phase Preparation

## 목적

이 문서는 Phase36 이후 다음 phase에서 무엇을 다루는 것이 자연스러운지 정리한다.

## 현재 handoff 상태

Phase36 현재 구현을 통해 아래가 고정됐다.

- 최종 판단 원본은 `FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl`이다.
- `SELECT_FOR_PRACTICAL_PORTFOLIO` row만 최종 선정 운영 대상으로 읽는다.
- `Operations > Selected Portfolio Dashboard`는 read-only 운영 화면이다.
- current weight 직접 입력, current value 입력, shares x price 입력 기반 drift check는 `DRIFT_ALIGNED`, `DRIFT_WATCH`, `REBALANCE_NEEDED`, `DRIFT_INPUT_INCOMPLETE`로 읽는다.
- shares x price 입력에서는 DB latest close를 보조로 불러올 수 있다.
- Final Review는 여전히 마지막 판단 단계다.
- Phase36 dashboard는 live approval, broker order, 자동매매를 만들지 않는다.

## 다음 phase에서 더 중요한 질문

1. 실제 계좌 보유 수량을 자동으로 읽을 것인가, 계속 operator 입력으로 둘 것인가
2. drift가 커졌을 때 risk alert / stop / re-review와 어떻게 연결할 것인가
3. 리밸런싱 안내가 주문 지시로 오해되지 않게 어떻게 경계를 둘 것인가
4. DB latest close 보조값과 operator 입력값 중 어떤 값을 우선할 것인가

## 다음 phase에서 실제로 할 작업

쉽게 말하면:

- Phase36은 `무엇이 선정됐는지`와 `현재 비중 / 평가금액 / 수량 x 가격 기준으로 목표 비중에서 얼마나 벗어났는지`를 보여줬다.
- 다음 phase는 실제 계좌 연결 여부를 결정하거나, drift 결과를 risk alert / review trigger로 연결해야 한다.

주요 작업:

1. Account holding 자동 연결 여부 정리
   - 실제 계좌 보유 수량을 자동으로 읽을지, operator 입력을 유지할지 결정한다.
   - 자동 연결을 하더라도 live approval / broker order와 분리되는 경계를 정한다.

2. drift 결과와 risk alert 연결
   - `REBALANCE_NEEDED` 상태를 단순 표시로 둘지, review trigger / alert surface로 연결할지 정한다.
   - stop / re-review 기준과 중복되지 않게 경계를 둔다.

3. 리밸런싱 안내 경계 고도화
   - 주문 수량 계산이나 broker API 연결은 하지 않는다.
   - 필요하면 `검토 필요` 수준의 read-only guide로 둔다.

## 추천 다음 방향

Phase37은 `Selected Portfolio Drift Alert And Holding Source Contract` 방향이 자연스럽다.

이유:

- 운영 대시보드와 drift check 입력 계약이 생겼으므로 다음 질문은 실제 holding source와 경고 체계를 어떻게 연결할지다.
- 리밸런싱은 계좌 보유 수량과 operator 확인 없이는 주문 지시로 넘어가면 안 된다.
- 먼저 holding source 계약과 alert 경계를 정해야 rebalance draft, execution workflow가 안전하게 이어진다.

## 명확한 out of scope

다음 phase에서도 별도 승인 없이는 아래를 만들지 않는다.

- 실제 주문 생성
- broker API 연결
- 자동매매
- 실제 투자금 자동 배분
- 세금 최적화
- 수익 보장 표현

## handoff 메모

다음 턴에서 먼저 볼 문서:

- `.note/finance/phases/phase36/PHASE36_CURRENT_CHAPTER_TODO.md`
- `.note/finance/phases/phase36/PHASE36_TEST_CHECKLIST.md`
- `.note/finance/code_analysis/WEB_BACKTEST_UI_FLOW.md`
- `app/web/runtime/final_selected_portfolios.py`
- `app/web/final_selected_portfolio_dashboard.py`
