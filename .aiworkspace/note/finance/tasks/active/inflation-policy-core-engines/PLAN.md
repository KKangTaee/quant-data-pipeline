# Inflation Policy Core Engines Plan

## 이걸 하는 이유?

1차에서 확보한 독립 Point-in-Time 원자료를 사용자의 분석 순서인
`Core PCE -> FOMC 정책 -> 2년물·10년물 -> 동적 저항대`로 연결하려면,
숫자 하나를 규칙으로 박지 않고 검증 상태와 불확실성을 보존하는 계산 엔진이 필요하다.

## Scope

1. Core PCE index 기반 월별 path와 연말 Q4/Q4 계산·목표 역산
2. 최신 SEP에서 버전별 다섯 상태 경계와 threshold probability 생성
3. 경제·SEP·최근 의결 component를 분리한 정책 경로 ensemble
4. pivot known-at, 다중 기간 zone, 저항 상태와 상승 driver 분해
5. 순방향 path와 목표 zone 조건부 역산 simulation
6. rolling-origin metric·baseline·calibration publication gate와 2026 replay
7. model artifact/snapshot materialization 계약과 durable docs 정렬

## Out Of Scope

- React/Streamlit workbench와 사용자 zone 편집 화면
- S&P 500 EPS·multiple 스트레스
- 신규 침체 모델
- CME FedWatch 신규 수집
- 기존 경제 사이클 확률·factor·artifact·snapshot 재사용

## Stop Condition

- 계산·검증·pipeline 집중 테스트가 통과한다.
- 실제 2026 DB replay가 당시 공개시각 이후 값만 사용한다.
- rolling-origin gate를 통과하지 못한 component는 `READY`가 아니라
  `LIMITED` 또는 `NOT_AVAILABLE`로 저장된다.
- 10년물 단독 돌파가 인플레이션 확인이나 자동 인상 신호로 승격되지 않는다.
