# UI Patterns

Status: Complete
Last Updated: 2026-07-14

## Summary

이번 연구의 중심은 데이터 source이며 새로운 UI benchmark는 범위 밖이다. 기존 Market Context 디자인을 유지하되 source 의미가 S&P/Shiller와 다르다는 점만 명확하게 표현한다.

## Pattern Catalog

### Source And Derivation Badge

- User problem: 사용자가 역산 EPS를 Nasdaq 공식 EPS로 오해할 수 있음
- Interaction shape: `EPS 출처`, `계산 방식`, `기준일`, `품질` badge
- Recommended copy for the free route: `QQQ 공개 공시·SEC 기업 실적 기반 재구성 EPS`
- Paid-provider copy, only after a separate source decision: `외부 Nasdaq-100 trailing P/E 기반 QQQ 환산 EPS`
- Avoid: `Nasdaq 공식 EPS`, `애널리스트 컨센서스 EPS`

### Compact Cross-Check Evidence

- User problem: P/E와 EPS가 서로 일치하는지 알기 어려움
- Interaction shape: 기본 화면에는 `교차검증 정상/차이 있음`만 표시하고 상세 수치는 자료 기준 disclosure에 둔다.
- Data required: same-date NDX, trailing P/E, direct quarterly EPS

### Reconstructed History Disclosure

- User problem: historical series를 당시 알 수 있던 release vintage로 오해
- Interaction shape: 기존 `과거 시점 재구성` badge와 함께 `provider history는 strict release-vintage PIT가 아님` 표시

### Forward Versus Trailing Separation

- User problem: MacroMicro forward P/E를 기존 actual trailing P/E의 결측 보강값으로 오해할 수 있음
- Interaction shape: source selector가 아니라 metric-level tab 또는 독립 card로 `실적 기준 Trailing P/E`와 `예상 실적 기준 Forward P/E`를 분리
- Required copy: forward track에는 `애널리스트 예상 이익 기반`, provider, forecast horizon과 revision 성격을 함께 표시
- Avoid: 두 metric을 같은 평균·표준편차 표본에 혼합하거나 forward series로 현재 trailing graph의 빈 달을 채우는 표현

## Patterns That Conflict With Current Boundaries

- UI에서 GuruFocus/Nasdaq/FactSet API 직접 호출
- request count, API token, raw response를 사용자 가치평가 화면에 노출
- provider-derived EPS를 공식 Nasdaq 발표값으로 표현
