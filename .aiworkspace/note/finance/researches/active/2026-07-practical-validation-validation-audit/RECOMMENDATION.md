# Recommendation

Status: Active
Date: 2026-07-06

## Product Direction

Practical Validation은 "Final Review에 보낼 수 있는가"를 먼저 말해야 하지만, 그 근거 화면은 "무엇을 검증했는가"를 먼저 보여줘야 한다.

따라서 다음 구현은 Backtest Analysis의 `검증 기준 상세`처럼 카테고리별 검증 결과를 우선하되, Practical Validation에 맞게 더 운영적인 구조로 간다.

## Recommended User Flow

Flow 3:

- 제목: `2차 검증 결론`
- 역할: 지금 Final Review로 이동 가능한지, 막는 이슈가 무엇인지, 먼저 해결할 일이 무엇인지 보여준다.
- 보여줄 것: 결론, blocker count, top issues, 다음 행동
- 숨길 것: 세부 category breakdown, board map, reference-only 근거

Flow 4:

- 제목: `카테고리별 검증 결과`
- 역할: 검증한 내용을 category별로 설명한다.
- 보여줄 것: category별 pass / blocker / review / not-run count, 실패 항목, 부족한 근거, 보강 위치
- 하단 보조: `Final Review 이동 요약`

Flow 5:

- 역할: audit trail 저장과 Final Review 이동 action
- 보여줄 것: 저장 가능 여부, 이동 가능 여부, 저장만 가능한 blocked record인지 여부

## Implementation Guideline

### 1. Service Taxonomy

`backtest_practical_validation_workspace.py`에 category-first grouping을 추가한다.

추천 group id:

- `source_replay`
- `data_bias_control`
- `comparison_validity`
- `realism_tradability`
- `validation_strength`
- `portfolio_construction`
- `conditional_context`
- `handoff_summary`

기존 `source_readiness`, `validation_readiness`, `final_review_readiness_preview`는 compatibility field로 남기되 Flow 4 main render에서는 새 group을 사용한다.

### 2. Gate Severity

Hard blocker로 유지:

- source contract missing
- latest runtime replay not run
- runtime period coverage missing
- benchmark parity missing
- price DB window hard missing
- PIT / look-ahead guard hard missing
- survivorship / listing hard missing
- cost / net curve / liquidity hard missing when applicable
- execution boundary violation
- selected-route preflight deterministic storage blocker

Review로 낮춤:

- walk-forward / OOS / regime not attached
- stress / rolling / sensitivity not fully computed
- construction risk for non-ETF / non-mix source
- provider freshness for non-ETF source
- macro / sentiment context
- tax / account scope
- monitoring baseline

Conditional blocker로 유지:

- provider investability for ETF-like source
- leverage / inverse suitability when leveraged / inverse symbols exist and diagnostic is BLOCKED
- risk contribution for weighted mix when component return matrix is unusable
- component role / weight for weighted mix when weight contract is invalid

### 3. UI Copy

Use these first-read labels:

| Technical Status | User Label |
| --- | --- |
| `PASS` / `READY` | 통과 |
| `REVIEW` | Final Review에서 확인 |
| `NEEDS_INPUT` | 근거 보강 필요 |
| `NOT_RUN` | 아직 실행 안 됨 |
| `BLOCKED` | 이동 차단 |
| `NOT_APPLICABLE` | 이번 후보에는 비적용 |

Avoid showing `NEEDS_INPUT row를 확인해...` as main copy. Instead show:

- 검증한 것: `검증이 특정 기간에만 우연히 좋았는지 확인했습니다.`
- 부족한 것: `walk-forward / OOS / regime 근거가 아직 연결되지 않았습니다.`
- 해야 할 일: `최신 replay 또는 validation evidence를 보강한 뒤 다시 확인합니다.`

### 4. Flow 4 Layout

Top summary:

- 통과
- 보강 필요
- Final Review 확인
- 아직 실행 안 됨
- 비적용

Category card:

- category name
- 검증 질문
- count summary
- 실패한 항목
- 왜 중요한지
- 보강 위치
- optional technical detail

Handoff summary:

- Final Review 이동 가능 / 보류
- 막는 core issue count
- selected-route preflight result
- save-only audit trail 여부

### 5. Tests

Focused tests should cover:

- selected-route preflight is not counted as validation category evidence.
- reference modules do not appear in Flow 4 main category failures.
- provider freshness does not block non-ETF source.
- construction risk is conditional / review for non-mix source.
- stress / robustness missing evidence is review by default unless profile marks it required.
- `NEEDS_INPUT` display label is `근거 보강 필요`.
- category summary counts pass / blocker / review / not-run separately.

## Final Decision For Next Build

다음 개발은 "Flow 4를 후보분석 UI와 완전히 동일하게 복사"하는 것이 아니라, 후보분석의 장점인 category-first 판단 구조를 Practical Validation 목적에 맞게 변형한다.

Backtest Analysis는 source를 넘길 수 있는지 보는 1차 기준이고, Practical Validation은 실전 검증 근거가 충분한지 보는 2차 기준이다. 그래서 Practical Validation은 더 세부적인 evidence category와 보강 위치가 필요하다.

결론:

- 비슷한 시각 언어는 사용한다.
- 정보 구조는 Practical Validation에 맞게 다르게 간다.
- Final Review 이동 기준은 메인이 아니라 파생 요약으로 낮춘다.
- 검증 category와 route gate를 분리한다.
