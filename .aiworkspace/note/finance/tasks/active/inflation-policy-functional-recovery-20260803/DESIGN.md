# Inflation Policy Functional Recovery Design

## 승인된 문제 해석

이 문제는 상태 안내가 부족해서 생긴 UX 문제가 아니다. fixture 기준 구현 완료와
production data materialization 완료를 혼동했고, 통합 snapshot의 `LIMITED`를 React의
전역 확률 gate로 사용해 독립 component까지 모두 숨겼다. reverse command는 성공한 DB
결과를 transport에 붙인 뒤 JSON 정규화를 다시 하지 않아 실제 클릭 경로가 깨졌다.

## 근본 원인과 소유 경계

| 증상 | 근본 원인 | 소유 계층 |
| --- | --- | --- |
| 검증 제한 상태 | 월간 Core PCE artifact를 공식 benchmark 미완료 때문에 강제 `LIMITED`; Q4/policy/joint는 별도 검증 없음 | model / validation / pipeline |
| 연말 Core PCE 다섯 상태 미표시 | Q4 path status 하드코딩 + `next_release_scenarios` snapshot 직렬화 누락 + UI 전역 gate | path / pipeline / React |
| 다음 회의·연말 정책 경로 미표시 | FOMC decision history 5건 + 수동 reaction prior + policy status 하드코딩 | data / policy / pipeline |
| 역산 클릭 크래시 | command result의 DB `datetime`이 component args에 그대로 남음 | Streamlit transport |
| S&P 500 stress 미표시 | official forward EPS vintage 0건 + production `joint_macro_paths` 생성 경로 부재 | data / loader / equity / simulation |
| 연결 범위·검증 근거 미충족 | 위 component들이 production gate를 통과하지 못한 결과 | service / React는 표현만 담당 |

## 설계 원칙

- 기존 `inflation_policy_v1` schema와 현재 화면을 고친다. 새 버전/새 화면으로 우회하지 않는다.
- `Ingestion -> DB -> Loader -> Model -> Snapshot -> Service -> UI`를 유지한다.
- React에서 확률을 새로 계산하지 않는다.
- Core PCE, policy, rates, reverse, equity는 독립 publication status를 갖는다.
- 한 component의 미충족이 다른 READY component 숫자를 숨기지 않는다.
- 반대로 통합 상태를 READY로 올려 미검증 component를 함께 공개하지도 않는다.
- 익명 SEP marginal 사이에 participant별 joint mapping을 만들지 않는다.
- 10년물 4.7%는 전역 상수가 아니라 그 시점의 confirmed pivot/zone 후보로만 다룬다.
- 경제 사이클 확률은 침체·policy·equity fallback으로 사용하지 않는다.

## 5차 독립 침체 계약

- target은 각 분기 origin 이후 12개월 안에 NBER recession month가 존재하는지다.
- `USREC`은 outcome label로만 쓰고 origin feature로 쓰지 않으며 label은 target 종료 후
  24개월이 지난 fold에서만 학습에 들어간다.
- feature는 당시 발표된 실업률·고용·실업수당·근로시간·임시고용·산업생산·실질소득·
  실질소비·10Y-2Y·하이일드 OAS뿐이다.
- 미개정 일별 시장 series의 `released_at`은 ALFRED 데이터셋 등록일이 아니라 보수적
  관측일 EOD다. revision identity인 `realtime_start/end`는 그대로 보존한다.
- expanding-window OOS Brier가 당시 base-rate Brier보다 낮고, calibration error 0.15 이하,
  평가구간 침체 episode 2개 이상, current feature completeness 80% 이상일 때만 확률을 공개한다.
- 결과는 기존 `inflation_policy_v1`의 별도 `recession_json`/`recession_risk` artifact로
  저장하며 경제 사이클 snapshot/artifact/query를 import하지 않는다.

## 검증 전략

모든 production 변경은 실패 테스트를 먼저 추가한다.

1. actual command 형태의 `datetime` 결과가 JSON 직렬화 가능한지 확인한다.
2. 통합 snapshot이 `LIMITED`여도 READY component만 표시되는지 React에서 확인한다.
3. Q4/Q4 forecast가 직접 rolling-origin target과 benchmark를 이기는지 확인한다.
4. policy probability가 historical decision holdout에서 baseline보다 나은지 확인한다.
5. joint path artifact가 fixture injection 없이 production bundle에서 생성되는지 확인한다.
6. equity는 PIT forward EPS와 label 공개시각을 지키는지 확인한다.
7. 마지막에 actual DB materialization과 Browser click을 재현한다.
