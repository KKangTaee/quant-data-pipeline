# Phase 35 Input Selector And Readiness Second Work Unit

## 목적

Phase35 두 번째 작업은 어떤 final review record가 운영 가이드 대상인지 명확히 보여주는 것이다.

## 쉽게 말하면

모든 Final Review 기록이 운영 가이드 대상은 아니다.
`선정`으로 저장된 record만 다음 단계로 넘기고,
보류 / 거절 / 재검토 record는 제외한다.

## 왜 필요한가

- 보류나 거절 record까지 운영 가이드 대상으로 보이면 사용자가 흐름을 오해한다.
- 최종 선정 후보만 운영 기준으로 바꿔야 Phase35가 주문 / 승인 단계처럼 보이지 않는다.
- 저장 전 blocker를 사용자가 고칠 수 있게 route와 check를 같이 보여줘야 한다.

## 구현한 내용

- `Backtest > Post-Selection Guide` 상단에서 Final Review record 전체를 table로 보여준다.
- `Guide Eligible` column으로 Phase35 대상 여부를 표시한다.
- selector는 eligible record만 선택지로 제공한다.
- readiness route를 추가했다.
  - `OPERATING_GUIDE_RECORD_READY`
  - `OPERATING_GUIDE_NEEDS_INPUT`
  - `OPERATING_GUIDE_BLOCKED`

## 결과

사용자는 Phase35에서 어떤 최종 선정 record가 운영 가이드 대상인지 먼저 확인한 뒤,
선택된 record의 components와 evidence를 보고 operating policy를 작성할 수 있다.
