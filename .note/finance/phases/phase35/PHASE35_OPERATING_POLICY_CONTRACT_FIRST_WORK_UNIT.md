# Phase 35 Operating Policy Contract First Work Unit

## 목적

Phase35 첫 번째 작업은 최종 선정 record를 어떤 운영 기준으로 바꿀지 계약을 정하는 것이다.

## 쉽게 말하면

Phase34가 "이 포트폴리오를 실전 후보로 고른다"를 기록했다면,
이번 작업은 "고른 뒤 어떤 규칙으로 운영할 것인가"를 정했다.

## 왜 필요한가

- 선정 record만 있고 운영 기준이 없으면 사용자가 실제로 따라가기 어렵다.
- 운영 기준을 final decision 원본에 덮어쓰면 선정 판단과 운영 판단이 섞인다.
- Phase35도 주문 / 승인 단계가 아니므로, 자본 투입 경계를 명확히 남겨야 한다.

## 구현한 계약

- 입력 source:
  - `decision_route = SELECT_FOR_PRACTICAL_PORTFOLIO`
  - `phase35_handoff.handoff_route = READY_FOR_POST_SELECTION_OPERATING_GUIDE`
- 새 저장소:
  - `.note/finance/registries/POST_SELECTION_OPERATING_GUIDES.jsonl`
- 핵심 필드:
  - guide id
  - source decision id
  - target components / target weight total
  - capital mode / capital boundary note
  - rebalancing cadence / rebalance trigger
  - reduce trigger / stop trigger / re-review trigger
  - live approval / order disabled boundary

## 결과

`app/web/runtime/post_selection_guides.py`와
`app/web/backtest_post_selection_guide_helpers.py`가 운영 가이드 계약을 담당한다.

이번 작업은 final decision registry를 수정하지 않고,
운영 기준만 별도 append-only registry로 남기는 방향으로 정리했다.
