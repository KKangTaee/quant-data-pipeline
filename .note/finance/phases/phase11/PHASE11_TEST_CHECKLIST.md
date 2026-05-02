# Phase 11 Test Checklist

## 목적

- Phase 11이 실제로 열렸을 때
  portfolio workflow가 연구용 surface에서 제품형 surface로 제대로 올라왔는지 확인한다.
- 이 checklist는 지금 즉시 실행용이 아니라,
  **Phase 11 구현 이후 later batch review용 준비 문서**다.

## 1. Saved Portfolio Creation

- `Compare & Portfolio Builder`에서 compare 실행 후
  `Weighted Portfolio Builder`로 결과를 만든다
- `Saved Portfolios > Save Current Weighted Portfolio`에서
  strategy 조합과 weights를 저장할 수 있는지
- 이름 / 설명 / compare_context / portfolio_context가 함께 남는지
- 저장 후 다시 목록에서 보이는지

## 2. Saved Portfolio Reload / Edit

- `Load Into Compare`를 누르면
  compare 화면으로 자동 이동하고
  selected strategies / 기간 / strategy override가 다시 채워지는지
- weighted builder가 다시 보일 때
  저장된 weights / `date_policy`가 다시 채워지는지
- 이후 사용자가 값을 수정한 뒤 다시 compare / weighted build가 가능한지

참고:

- 현재 first pass는 전용 overwrite/edit form이 아니라
  **load -> compare에서 수정 -> 다시 저장**
  흐름으로 본다.

## 3. Compare-To-Portfolio Bridge

- current compare 결과에서 weighted portfolio를 만들고
  그 결과를 saved portfolio로 저장할 수 있는지
- saved portfolio에서 다시 compare로 돌아오는 bridge가 자연스러운지
- strategy-specific advanced input이 저장/복원 후에도 유지되는지

## 4. Portfolio Result Readouts

- contribution summary가 보이는지
- `Meta` 탭에서
  - `portfolio_name`
  - `portfolio_id`
  - `portfolio_source_kind`
  - `date_policy`
  - `selected_strategies`
  - `input_weights_percent`
  가 보이는지
- `Configured Weight (%)`와 `Normalized Weight`가 같이 보이는지
- strategy-level exposure summary / rebalance change summary / benchmark 비교는
  아직 later pass backlog라는 점이 문서와 어긋나지 않는지

## 5. History / Rerun Integration

- `Run Saved Portfolio` 실행 후 history에 compare run + weighted run이 남는지
- history context에
  - `saved_portfolio_id`
  - `saved_portfolio_name`
  가 남는지
- saved run / saved portfolio의 역할 차이가 화면상 이해되는지

## 6. Workflow Readability

- “전략 비교 -> 포트폴리오 구성 -> 저장 -> 다시 실행” 흐름이
  중간 수동 복붙 없이 자연스럽게 이어지는지
- UI 설명 문구가 현재 preset semantics와 충돌하지 않는지

## 7. Static Universe Contract Disclosure

- current preset이 `managed static research universe`라는 점이
  portfolio surface에서도 오해 없이 읽히는지
- 실전 투자 최종 검증은 separate dynamic PIT contract가 필요하다는 점이
  과장 없이 드러나는지

## 8. Batch Review Position

- Phase 8 checklist
- Phase 9 checklist
- Phase 10 checklist
- Phase 11 checklist

를 함께 돌릴 때,
Phase 11 이슈와 이전 phase 이슈를 구분할 수 있을 정도로
history / payload / saved portfolio metadata가 남는지

## closeout 판단 기준

아래가 모두 만족되면
Phase 11은 first-pass productization closeout 후보로 볼 수 있다.

1. saved portfolio workflow가 동작한다
2. compare-to-portfolio bridge가 자연스럽다
3. portfolio readout이 단순 equity curve를 넘는다
4. history / rerun / saved portfolio 관계가 읽힌다
5. current universe contract에 대한 설명이 misleading하지 않다
