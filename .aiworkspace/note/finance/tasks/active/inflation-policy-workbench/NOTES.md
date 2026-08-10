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

## Implemented User Flow

1. Market Research의 경제 사이클 화면에서 `물가·정책 경로`를 명시적으로 선택한다.
2. `READY`일 때만 연말 Core PCE 다섯 상태와 정책 확률을 보고, 그 외 상태는 제한
   사유와 다음 확인 조건을 본다.
3. DGS10의 현재 자동 전고점 군집과 다음 overhead를 driver lens와 함께 읽는다.
4. 목표 금리 구간·돌파 조건·horizon을 입력해 검증된 공동 경로의 조건부분포를 요청한다.
5. 자동 기준을 바꾸지 않고 필요할 때 USER 기준으로 복사해 저장한다.
6. 관측일·발표시각·수집시각과 model/state/zone version은 접힌 근거 패널에서 확인한다.

actual DB의 reverse artifact는 READY가 아니므로 현재 화면은 필요한 인상 횟수를
추정해 채우지 않고 `공동 경로 검증 전`으로 닫힌다.
