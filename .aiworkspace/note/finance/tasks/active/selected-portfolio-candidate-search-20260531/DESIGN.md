# Design

## Workflow Boundary

현재 main flow는 `PORTFOLIO_SELECTION_SOURCES -> PRACTICAL_VALIDATION_RESULTS -> FINAL_PORTFOLIO_SELECTION_DECISIONS_V2 -> Selected Portfolio Dashboard`다. Final Review 저장은 selected-route gate를 통과한 row만 `SELECT_FOR_PRACTICAL_PORTFOLIO`로 append하는 방식이다.

## Execution Approach

1. Registry / saved portfolio / run history를 구조적으로 요약한다.
2. Gate-passed Practical Validation result를 Final Review evidence read model로 평가한다.
3. 이미 저장된 selected row와 중복되는 후보는 dashboard 노출 재확인 대상으로 보고, 새 row append 여부는 gate와 중복성을 함께 본다.
4. 신규 저장이 필요한 경우 runtime helper를 사용해 UI와 같은 registry append contract를 따른다.
5. Streamlit UI는 read-only 확인과 screenshot QA에 사용한다.

## Safety

- `registries/*.jsonl`은 append-only로 다룬다.
- Gate 미통과 후보는 final decision registry에 저장하지 않는다.
- selected dashboard는 read-only 운영 확인 화면으로만 사용한다.
