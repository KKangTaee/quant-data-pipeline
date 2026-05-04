# Phase 35 Input Selector And Readiness Second Work Unit

## 목적

Phase35 두 번째 작업은 어떤 final review record가 최종 투자 지침 확인 대상인지 명확히 보여주는 것이다.

## 쉽게 말하면

모든 Final Review 기록이 투자 가능 후보는 아니다.
`선정`으로 기록된 record만 마지막 확인 대상으로 넘기고,
보류 / 거절 / 재검토 record는 각각 내용 부족 / 투자하면 안 됨 / 재검토 필요로 보여준다.

## 왜 필요한가

- 보류나 거절 record까지 투자 가능 후보처럼 보이면 사용자가 흐름을 오해한다.
- 최종 선정 후보만 운영 전 기준을 확인해야 Phase35가 주문 / 승인 단계처럼 보이지 않는다.
- readiness는 저장 가능 여부가 아니라 최종 확인이 충분한지 보여줘야 한다.

## 구현한 내용

- `Backtest > Post-Selection Guide` 상단에서 Final Review record 전체를 table로 보여준다.
- `투자 가능성` column으로 최종 판단을 plain-language로 표시한다.
- `Final Guide Eligible` column으로 Phase35 선택 대상 여부를 표시한다.
- selector는 eligible record만 선택지로 제공한다.
- readiness route를 보정했다.
  - `FINAL_INVESTMENT_GUIDE_READY`
  - `FINAL_INVESTMENT_GUIDE_NEEDS_INPUT`
  - `FINAL_INVESTMENT_GUIDE_BLOCKED`

## 결과

사용자는 Phase35에서 어떤 최종 선정 record가 실제 투자 후보로 읽히는지 먼저 확인한 뒤,
선택된 record의 components와 evidence를 보고 운영 전 기준을 확인할 수 있다.
