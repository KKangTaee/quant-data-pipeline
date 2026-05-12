# Phase 36 Next Phase Preparation

## 목적

이 문서는 Phase36 이후 다음 phase에서 무엇을 다루는 것이 자연스러운지 정리한다.

## 현재 handoff 상태

Phase36 현재 구현을 통해 아래가 고정됐다.

- 최종 판단 원본은 `FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl`이다.
- `SELECT_FOR_PRACTICAL_PORTFOLIO` row만 최종 선정 운영 대상으로 읽는다.
- `Operations > Selected Portfolio Dashboard`는 read-only 운영 화면이다.
- `Performance Recheck`는 selected component의 Current Candidate Registry replay contract를 사용자가 지정한 기간으로 다시 실행한다.
- 기본 종료일은 DB latest market date이며, recheck 결과는 portfolio value, total return, CAGR, MDD, benchmark spread, component contribution으로 표시된다.
- current weight 직접 입력, current value 입력, shares x price 입력 기반 drift check는 `DRIFT_ALIGNED`, `DRIFT_WATCH`, `REBALANCE_NEEDED`, `DRIFT_INPUT_INCOMPLETE`로 읽는다.
- shares x price 입력에서는 DB latest close를 보조로 불러올 수 있다.
- drift 결과는 read-only alert preview와 Final Review review trigger table로 다시 읽을 수 있다.
- Final Review는 여전히 마지막 판단 단계다.
- Phase36 dashboard는 live approval, broker order, 자동매매를 만들지 않는다.

## 다음 phase에서 더 중요한 질문

1. Performance Recheck 결과가 약해졌을 때 어떤 원인 분석을 자동으로 보여줄 것인가
2. component별 contribution을 넘어 factor / regime / period split attribution을 어디까지 계산할 것인가
3. 실제 계좌 보유 수량을 자동으로 읽을 것인가, 계속 operator 입력으로 둘 것인가
4. drift가 커졌을 때 read-only preview를 실제 alert persistence / stop / re-review workflow와 연결할 것인가
5. 리밸런싱 안내가 주문 지시로 오해되지 않게 어떻게 경계를 둘 것인가

## 다음 phase에서 실제로 할 작업

쉽게 말하면:

- Phase36은 `무엇이 선정됐는지`와 `내가 지정한 최신 기간에서 성과가 유지되는지`를 보여줬다.
- 다음 phase는 성과 약화 원인을 더 깊게 분해하거나, 실제 계좌 연결 / drift alert persistence를 어디까지 할지 정해야 한다.

주요 작업:

1. Performance deterioration attribution
   - recheck 결과가 약화될 때 어떤 기간 / component / benchmark 구간에서 문제가 생겼는지 자동으로 요약한다.
   - 단순 CAGR / MDD 변화가 아니라 원인 후보를 보여준다.

2. Account holding 자동 연결 여부 정리
   - 실제 계좌 보유 수량을 자동으로 읽을지, operator 입력을 유지할지 결정한다.
   - 자동 연결을 하더라도 live approval / broker order와 분리되는 경계를 정한다.

3. drift 결과와 risk alert 연결
   - Phase36의 read-only alert preview를 저장 가능한 alert / review surface로 확장할지 정한다.
   - stop / re-review 기준과 중복되지 않게 경계를 둔다.

4. 리밸런싱 안내 경계 고도화
   - 주문 수량 계산이나 broker API 연결은 하지 않는다.
   - 필요하면 `검토 필요` 수준의 read-only guide로 둔다.

## 추천 다음 방향

Phase37은 `Selected Portfolio Performance Attribution And Review Alerts` 방향이 자연스럽다.

이유:

- 운영 대시보드와 기간 확장 재검증이 생겼으므로 다음 질문은 성과가 약해졌을 때 원인을 얼마나 자동으로 설명할 수 있는지다.
- 그 다음 실제 holding source와 저장 가능한 경고 체계를 연결하는 것이 자연스럽다.
- 리밸런싱은 계좌 보유 수량과 operator 확인 없이는 주문 지시로 넘어가면 안 된다.
- 먼저 성과 약화 원인과 alert 경계를 정해야 holding source, rebalance draft, execution workflow가 안전하게 이어진다.

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
- `.note/finance/docs/flows/BACKTEST_UI_FLOW.md`
- `app/web/runtime/final_selected_portfolios.py`
- `app/web/final_selected_portfolio_dashboard.py`
