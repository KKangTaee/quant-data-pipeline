# Inflation Policy Functional Recovery Plan

## 이걸 하는 이유?

현재 Inflation / Policy Workbench는 코드와 fixture 테스트가 존재하지만 실제 DB에서는
연말 Core PCE, 정책 경로, 공동 금리 경로와 equity 입력이 준비되지 않아 핵심 결과가
`LIMITED` 또는 `NOT_AVAILABLE`로 닫힌다. 더구나 역산 command 결과의 `datetime`이
Streamlit component transport에서 직렬화되지 않아 클릭 시 화면이 크래시한다.

이 task의 목적은 새 V2/V3 화면이나 안내 문구를 추가하는 것이 아니라 기존
`inflation_policy_v1` 경로를 실제 데이터·검증·명령·UI까지 끝까지 작동하게 복구하는
것이다. 기존 경제 사이클 확률은 입력이나 fallback으로 사용하지 않는다.

## 전체 Roadmap

| 차수 | 목적 | 주요 범위 | 완료 조건 |
| ---: | --- | --- | --- |
| 1 | runtime 무결성 복구 | command JSON 경계, component별 공개 상태, actual DB 회귀 테스트 | 역산 클릭이 크래시하지 않고 각 component가 자기 상태만 사용한다. |
| 2 | 연말 Core PCE 결과 실사용화 | 다음 발표 시나리오 직렬화, Q4/Q4 rolling-origin, SPF/공식 benchmark | 실제 DB snapshot에서 다섯 상태와 0.1~0.5% 조건이 검증 상태와 함께 나온다. |
| 3 | 정책·공동 금리 경로 실사용화 | FOMC history backfill, policy chronological validation, joint rate path materialization | 다음 회의·연말 정책 경로와 목표 역산이 actual DB에서 계산된다. |
| 4 | S&P 500 조건부 stress 실사용화 | PIT forward EPS source/backfill, equity validation, joint path 연결 | official/검증 가능한 EPS vintage로 actual equity result가 계산된다. |
| 5 | 독립 침체 연결 | 별도 episode/OOS 침체 모델 | 경제 사이클 재사용 없이 검증된 침체 결과가 연결된다. |

1~5차를 모두 완료했다. 마지막 5차는 기존 경제 사이클 결과를 읽지 않고 독립
FRED/ALFRED 시점 원장과 지연 확정 NBER label만 사용해 실제 snapshot·service·UI까지
연결했다. 확률 gate를 fixture 숫자나 안내 문구로 우회하지 않았다.

## 구현 순서

### Task 1. Command transport와 UI gate 복구

- 수정 후보: `app/web/overview/market_context_helpers.py`
- 수정 후보: `app/web/streamlit_components/economic_cycle_workbench/src/InflationPolicyWorkbench.tsx`
- 테스트: `tests/test_market_context_inflation_policy.py`
- 테스트: `InflationPolicyWorkbench.test.tsx`
- `command_result`를 payload 합성 뒤에도 JSON-safe하게 정규화한다.
- snapshot 전체 상태 하나가 아니라 inflation/policy/rates/reverse/equity component 상태가
  자기 패널의 공개 여부를 결정하게 한다.

### Task 2. Core PCE 다섯 상태와 다음 발표 조건

- 수정 후보: `finance/inflation_path.py`
- 수정 후보: `finance/inflation_policy_validation.py`
- 수정 후보: `finance/inflation_policy_pipeline.py`
- 수정 후보: `finance/data/*`, `finance/loaders/inflation_policy.py`
- 다음 발표 MoM `0.1/0.2/0.3/0.4/0.5%` 시나리오를 snapshot에 보존한다.
- 월간 nowcast의 검증을 연말 Q4/Q4에 상속하지 않고, Q4/Q4 target을 직접
  chronological rolling-origin으로 검증한다.
- Philadelphia Fed SPF Core PCE Q4/Q4와 공식 nowcast를 benchmark/anchor로 수집·저장한다.

### Task 3. FOMC policy와 joint rate path

- 수정 후보: `finance/data/fomc_policy.py`
- 수정 후보: `finance/policy_path.py`
- 수정 후보: `finance/inflation_policy_simulation.py`
- 수정 후보: `finance/inflation_policy_pipeline.py`
- 2026년 5건만 있는 decision table을 공식 FOMC historical source로 backfill한다.
- 수동 반응 prior 대신 chronological decision target으로 policy probability를 검증한다.
- Core PCE·policy·DGS2·DGS10·DFII10·T10YIE의 공동 경로를 실제 history에서 만들고
  `joint_macro_paths` artifact로 저장한다.

### Task 4. Equity PIT source와 stress

- 수정 후보: `finance/data/sp500_valuation.py`
- 수정 후보: `finance/loaders/inflation_policy.py`
- 수정 후보: `finance/inflation_policy_equity_stress.py`
- current actual workbook를 과거 vintage처럼 소급하지 않는다.
- 당시 공개된 next-year forward EPS를 재구성할 수 있는 source와 release timestamp를
  확보하고, 없으면 해당 origin은 제외한다.
- actual DB에서 60개 이상 completed origin과 세 baseline/coverage gate를 검증한다.

### Task 5. 독립 침체 모델과 최종 실제 DB/Browser QA

- 기존 경제 사이클 확률·artifact·snapshot을 입력이나 fallback으로 사용하지 않는다.
- 침체 episode와 label 공개시각을 별도로 정의하고 chronological OOS gate를 통과시킨다.
- 동일한 production materialization command로 2026-08-03 snapshot을 재생성한다.
- 역산·정책·equity command와 독립 침체 결과를 actual DB로 실행한다.
- desktop/mobile Browser에서 결과, click, overflow와 console을 확인한다.
- 기존 task/phase의 잘못된 `complete` 기록을 실제 상태로 정렬하고 QA screenshot을 남긴다.

## Stop Condition

- 사용자가 지적한 6개 증상이 fixture나 안내 문구가 아니라 actual DB 경로에서 해결된다.
- 각 component는 자체 rolling-origin gate와 source evidence를 통과한 경우에만 숫자를
  공개한다.
- 역산·equity command가 동일 snapshot/artifact를 사용하고 크래시하지 않는다.
- 실제 Browser QA와 regression suite가 통과한다.
- 해결하지 못한 외부 데이터 권리/가용성 문제가 있으면 가짜 데이터로 우회하지 않고,
  정확한 source 계약과 재현 가능한 수집 실패 evidence를 task risk에 남긴다.
