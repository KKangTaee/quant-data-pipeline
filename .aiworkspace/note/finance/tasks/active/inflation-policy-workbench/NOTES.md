# Inflation Policy Workbench Notes

## Confirmed Decisions

- 기존 경제 사이클 화면은 기본 탭과 기존 동작을 유지한다.
- 신규 화면은 같은 component transport 안에 독립 `inflation_policy` payload로 붙인다.
- 최신 실제 snapshot은 `LIMITED`, reverse는 `NOT_AVAILABLE`이며 UI fixture로 승격하지 않는다.
- 2026-07-29 replay의 DGS10 active zone은 4.58~4.65%, next overhead는 4.67%다.
- 4.7%는 전역 상수가 아니라 시점별 동적 저항 후보로만 해석한다.

## Plan Review Finding

기존 plan이 소비한다고 명시한 `load_yield_resistance_definitions`와 exact model artifact
loader가 코드에는 없었다. service에서 SQL을 직접 쓰지 않도록 finance loader에 두고,
PIT cutoff·정확한 artifact identity를 테스트한다.
