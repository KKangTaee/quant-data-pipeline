# Phase 35 Final Investment Guide Contract First Work Unit

## 목적

Phase35 첫 번째 작업은 Final Review의 최종 판단을 어떤 마지막 지침으로 읽을지 계약을 정하는 것이다.

## 쉽게 말하면

Phase34가 "이 포트폴리오를 최종 후보로 고른다 / 보류한다 / 거절한다 / 재검토한다"를 기록했다면,
이번 작업은 그 기록을 사용자가 바로 이해할 수 있는 최종 투자 가능성 언어로 바꿨다.

## 왜 필요한가

- 사용자는 마지막에 "그래서 투자 가능 후보인가?"를 빠르게 확인해야 한다.
- Phase35가 또 저장소를 만들면 Final Review와 역할이 겹친다.
- Phase35도 주문 / 승인 단계가 아니므로, 실행 경계를 명확히 남겨야 한다.

## 구현한 계약

- 입력 source:
  - `decision_route = SELECT_FOR_PRACTICAL_PORTFOLIO`
  - 신규 row: `phase35_handoff.handoff_route = READY_FOR_FINAL_INVESTMENT_GUIDE`
  - 기존 QA row: `READY_FOR_POST_SELECTION_OPERATING_GUIDE`도 읽기 호환
- 최종 판단 표시:
  - `SELECT_FOR_PRACTICAL_PORTFOLIO` -> 투자 가능 후보
  - `HOLD_FOR_MORE_PAPER_TRACKING` -> 내용 부족 / 관찰 필요
  - `REJECT_FOR_PRACTICAL_USE` -> 투자하면 안 됨
  - `RE_REVIEW_REQUIRED` -> 재검토 필요
- 새 저장소:
  - 없음
- preview 필드:
  - source decision id
  - target components / target weight total
  - capital mode / capital boundary note
  - rebalancing cadence / rebalance trigger
  - reduce trigger / stop trigger / re-review trigger
  - live approval / order disabled boundary

## 결과

`app/web/backtest_post_selection_guide_helpers.py`가 Final Review record를 최종 투자 지침 preview로 읽는다.

이번 보정은 final decision registry를 수정하지 않고,
Phase35에서 별도 append-only registry도 만들지 않는 방향으로 정리했다.
