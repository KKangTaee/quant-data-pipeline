# Risks

Status: Active
Date: 2026-07-06

## Product Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Too many checks stay visible | 사용자가 다시 가이드 / 체크리스트처럼 느낀다. | Flow 4 main은 category result only, technical detail은 접힌 상태로 둔다. |
| Gate gets too loose | 실전검증이 약한 후보가 Final Review로 넘어갈 수 있다. | source/replay/benchmark/PIT/survivorship/cost/liquidity core blockers는 유지한다. |
| Gate stays too strict | 후보 특성과 무관한 provider, stress, construction gap이 이동을 막는다. | 조건부 적용과 review severity를 명시한다. |
| `selected_route_preflight` removal is misunderstood | Final Review 저장 차단 gap을 놓칠 수 있다. | 제거하지 않고 handoff summary로 낮춘다. |
| Sentiment context reappears as validation | 시장 배경이 pass/fail 근거처럼 오해된다. | sentiment는 context-only, gate 제외 원칙을 유지한다. |

## Implementation Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Existing React Fix Queue contract breaks | Flow 3이 비거나 fallback으로 돌아갈 수 있다. | 기존 field를 compatibility로 유지하고 새 category field를 추가한다. |
| Docs and code wording drift | 다시 Final Review 기준 중심으로 문서가 굳을 수 있다. | 구현 후 `PORTFOLIO_SELECTION_FLOW.md`와 `PROJECT_MAP.md`를 category-first wording으로 맞춘다. |
| Duplicated blocker counts remain | 같은 이슈가 여러 category에서 실패처럼 보인다. | category summary에서 primary owner를 정하고 duplicate rows는 related evidence로 낮춘다. |
| Tests only check structure | 실제 user-facing copy가 다시 raw status로 돌아갈 수 있다. | display label test와 snapshot-like contract test를 추가한다. |

## Open Questions

- stress / robustness를 hard blocker로 삼을 profile을 명시적으로 둘 것인가?
- ETF-like가 아닌 factor equity source에서 provider snapshot row를 완전히 숨길 것인가, reference로 남길 것인가?
- walk-forward / OOS / regime 중 어느 항목을 "최소 필수"로 볼 것인가, 아니면 전부 review evidence로 둘 것인가?

현재 추천은 conservative하게 둔다.

- 일반 profile: walk-forward / OOS / regime / stress는 review
- ETF-like: provider / look-through는 conditional core
- weighted mix: risk contribution / component role은 conditional core
- tactical / hedged profile: macro regime은 conditional review
- sentiment: context-only
