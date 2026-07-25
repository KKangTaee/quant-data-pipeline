# Notes

Last Updated: 2026-07-25

## Diagnosis

- `_pathway_narrative()`가 common `economic_state.summary`를 첫 문장으로 포함한다.
- `MarketImplicationCard`는 narrative를 상단에 표시하고 `EconomicStateBlock`도 바로
  렌더링한다.
- 금·달러 context에는 `current_interpretation`이 없어 React fallback이 narrative를
  `현재 해석`에 다시 사용한다.
- 채권·주식 narrative에는 common state가 포함되지 않아 같은 형태의 exact duplication은
  금·달러 경로에 집중된다.

## Decisions

- common state block을 숨기지 않고 자산 고유 문구를 분리한다.
- 전체 자산 section typography는 승인된 `+1px`로 해석한다.
- layout spacing과 다른 Economic Cycle section typography는 유지한다.

## Implemented Resolution

- Gold/Dollar pathway builder가 asset-specific `summary`와
  `current_interpretation`을 명시하고 `narrative`는 legacy 호환값으로 유지한다.
- interpretation service는 명시 summary를 narrative로 덮어쓰지 않는다.
- React 상단은 `summary -> narrative -> context`, 현재 해석은 explicit list 우선순위를
  사용한다. 원자재 내부 금도 `asset.summary -> asset.narrative` 순서다.
- 별도 `.implication-section`을 추가하지 않고 이미 해당 화면만 소유하는
  `.market-implications`를 typography scope로 재사용했다. 기존 source 계약과 DOM
  ownership을 유지하면서 같은 격리 효과를 얻는다.
