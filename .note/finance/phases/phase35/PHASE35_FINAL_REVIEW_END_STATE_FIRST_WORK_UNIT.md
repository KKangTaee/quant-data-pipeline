# Phase 35 Final Review End State First Work Unit

## 목적

첫 번째 작업은 Final Review가 현재 Backtest 후보 선정 workflow의 마지막 단계라는 계약을 정리하는 것이다.

## 쉽게 말하면

사용자가 Final Review에서 최종 판단을 저장하면,
이제 별도 후속 탭으로 이동하지 않고 그 자리에서 최종 상태를 읽는다.

## 왜 필요한가

- Final Review가 이미 validation, robustness, paper observation, operator judgment를 모두 묶는다.
- 별도 마지막 탭을 더 만들면 같은 내용을 다시 읽는 중복 단계가 된다.
- 사용자는 마지막에 "투자 가능인가, 아닌가"를 명확히 보면 된다.

## 구현한 계약

- `SELECT_FOR_PRACTICAL_PORTFOLIO` -> 투자 가능 후보
- `HOLD_FOR_MORE_PAPER_TRACKING` -> 내용 부족 / 관찰 필요
- `REJECT_FOR_PRACTICAL_USE` -> 투자하면 안 됨
- `RE_REVIEW_REQUIRED` -> 재검토 필요

## 결과

Final Review의 saved decision review가 최종 판단 완료 상태를 보여준다.
`phase35_handoff`라는 legacy field는 호환용으로 남아 있을 수 있지만,
사용자-facing UI에서는 `Final Review Status`로 읽는다.
