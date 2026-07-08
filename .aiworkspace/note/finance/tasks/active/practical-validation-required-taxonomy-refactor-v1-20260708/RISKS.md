# Risks

- 3차 risk는 해소했다. Module planner, board registry, workspace label을 `Validation Method Strength`와 `Stress / Robustness` 분리 구조로 정렬했다.
- 5차 risk는 해소했다. Final Review evidence read model 회귀 테스트가 method-only blocker wording과 selected-route behavior를 검증한다.
- 남은 주의점: `validation_efficacy`라는 internal id는 backward compatibility 때문에 남아 있다. User-facing copy와 docs에서는 `Validation Method Strength`로 읽어야 한다.
