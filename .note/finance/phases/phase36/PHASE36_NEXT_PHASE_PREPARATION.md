# Phase 36 Next Phase Preparation

## 목적

이 문서는 Phase36 이후 다음 phase에서 무엇을 다루는 것이 자연스러운지 정리한다.

## 현재 handoff 상태

Phase36 first pass를 통해 아래가 고정됐다.

- 최종 판단 원본은 `FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl`이다.
- `SELECT_FOR_PRACTICAL_PORTFOLIO` row만 최종 선정 운영 대상으로 읽는다.
- `Operations > Selected Portfolio Dashboard`는 read-only 운영 화면이다.
- Final Review는 여전히 마지막 판단 단계다.
- Phase36 dashboard는 live approval, broker order, 자동매매를 만들지 않는다.

## 다음 phase에서 더 중요한 질문

1. 최종 선정 포트폴리오의 현재 비중을 어떻게 계산할 것인가
2. 목표 비중과 현재 비중 차이를 어느 기준 이상이면 리밸런싱 필요로 볼 것인가
3. 실제 보유 수량 / 평가금액 / 현재 가격을 어떤 입력 계약으로 받을 것인가
4. 리밸런싱 안내가 주문 지시로 오해되지 않게 어떻게 경계를 둘 것인가

## 다음 phase에서 실제로 할 작업

쉽게 말하면:

- Phase36은 `무엇이 선정됐는지`를 보여줬다.
- 다음 phase는 `선정된 포트폴리오가 지금 목표 비중에서 얼마나 벗어났는지`를 계산할 준비를 해야 한다.

주요 작업:

1. current price / holding input contract 정리
   - 현재 가격을 DB에서 읽을지, 수동 입력이나 paper 가정 금액으로 계산할지 결정한다.
   - 실제 계좌 정보가 없는 상태에서 어떤 값까지 자동 계산할 수 있는지 경계를 정한다.

2. target vs current weight 계산
   - selected component target weight와 현재 평가금액 기반 current weight를 비교한다.
   - drift threshold를 넘으면 `rebalance_needed` 후보로 표시한다.

3. 리밸런싱 안내 경계 정의
   - 주문 수량 계산이나 broker API 연결은 하지 않는다.
   - 필요하면 `검토 필요` 수준의 read-only guide로 둔다.

## 추천 다음 방향

Phase37은 `Selected Portfolio Current Weight And Drift Contract` 방향이 자연스럽다.

이유:

- 운영 대시보드가 생겼으므로 다음 질문은 현재 상태와 목표 상태의 차이다.
- 리밸런싱은 현재 가격과 보유 수량 계약 없이는 정확히 계산할 수 없다.
- 먼저 drift 계약을 정리해야 risk alert, rebalance draft, execution workflow가 안전하게 이어진다.

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
