# Design

## Production Contract

`economic_cycle_transition_v1`은 두 모델을 하나의 snapshot에 묶되 역할을 분리한다.

- current state: confirmed RTDSM state
- transition pressure: required extended driver model
- destination distribution: compact core model

`transition_monitor_json.contract_version = transition_forecast_v1`일 때만 Overview가
예측으로 해석한다. legacy fixed-route monitor는 호환 표시만 유지하고 새 snapshot에서는
예측 대체값으로 사용하지 않는다.

## UI Contract

- 순환 경로: 현재 국면에서 model primary destination으로 화살표
- 현재 진단: 현재 국면, 전환압력, 가장 유력한 다음 국면, 대안 국면 분포
- 조건 변화: pressure model의 표준화 기여도를 바탕으로 압력을 높이거나 낮추는 관측을 설명
- 시간 경계: 정확한 달 예측이 아니라 다음 3개 usable release 안의 pressure와 다음
  confirmed transition의 destination을 분리해 표시
- 자산별 확인 포인트: 기존 payload builder와 React section을 그대로 유지

## Fail Closed

- feasibility가 `GO`가 아니면 artifact/snapshot을 publish하지 않는다.
- current origin 또는 필수 feature가 없으면 기존 last-good snapshot을 덮어쓰지 않는다.
- legacy `probabilities_json`과 `forecast_path_json`은 새 예측에 사용하지 않는다.
