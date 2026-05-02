# Phase 8 Operator Runtime And Shadow Rebuild Tooling

## Summary

이번 보강은 `Ingestion` 화면에서 실제 운영자가 가장 자주 막히던 지점을 줄이는 데 초점을 두었다.

핵심은 다섯 가지다.

1. 현재 Streamlit 프로세스가 어떤 코드 상태로 떠 있는지 바로 보는 `Runtime / Build` indicator
2. raw statement 재수집 없이 shadow만 다시 만드는 `Statement Shadow Rebuild Only`
3. `Statement Shadow Coverage Preview`에서 missing symbol을 바로 다음 작업으로 넘기는 action bridge
4. persisted run을 다시 읽고 관련 artifact / logs까지 같이 보는 `Run Inspector`
5. web-app job 기준 표준 JSON / failure CSV artifact emission

## Implemented Features

### 1. Runtime / Build Indicator

`Ingestion` 화면 상단에 `Runtime / Build` block을 추가했다.

표시 항목:

- `Runtime Marker`
- `Loaded At`
- `Git SHA`

목적:

- 코드 수정 후에도 예전 Streamlit 프로세스가 살아 있어 old path를 타는 문제를 줄이기 위함
- 특히 statement refresh / quarterly coverage recovery 같은 장시간 작업에서
  “지금 내가 돌리는 버튼이 정말 최신 코드 기준인지”를 빨리 확인하기 위함

또한 run metadata에도 아래가 같이 저장된다.

- `runtime_marker`
- `runtime_loaded_at`
- `git_sha`

## 2. Statement Shadow Rebuild Only

`Ingestion > Manual Jobs / Inspection`에 새 카드가 추가되었다.

이 카드는:

- EDGAR raw statement를 다시 수집하지 않고
- 이미 저장된 raw statement ledger를 읽어서
  - `nyse_fundamentals_statement`
  - `nyse_factors_statement`
  를 다시 만든다

적합한 상황:

- `Statement Shadow Coverage Preview`에서
  `raw_statement_present_but_shadow_missing`
  이 많은 경우

즉:

- raw는 이미 있지만
- quarterly / annual statement shadow만 비어 있을 때

더 빠른 복구 경로로 쓸 수 있다.

## 3. Coverage Gap -> Action Bridge

`Backtest > quarterly prototype > Statement Shadow Coverage Preview`의
`Coverage Gap Drilldown`은 이제 단순 진단에 그치지 않는다.

추가된 연결:

- `no_raw_statement_coverage`
  - `Extended Statement Refresh`로 보내는 payload
  - `Send Raw-Coverage Gaps To Extended Statement Refresh`
- `raw_statement_present_but_shadow_missing`
  - `Statement Shadow Rebuild Only`로 보내는 payload
  - `Send Shadow-Missing Gaps To Statement Shadow Rebuild`

동작 방식:

- 사용자가 backtest 쪽에서 버튼을 누르면
- ingestion 쪽 관련 카드의 입력값이 다음 rerun에서 미리 채워진다
- 실제 job 실행은 사용자가 ingestion 탭에서 명시적으로 다시 누른다

이 구조는 진단과 실행을 분리하면서도, operator 이동 비용을 줄이기 위한 설계다.

## 4. Run Inspector

`Ingestion > Persistent Run History` 아래에 `Run Inspector`를 추가했다.

이제 persisted run 하나를 선택해서 아래를 함께 볼 수 있다.

- 기본 result summary
- execution mode / pipeline type
- runtime marker
- pipeline steps
- standardized artifact paths
- likely related logs

목적:

- 긴 run이 old path를 탔는지
- 어떤 step에서 멈췄는지
- 어떤 failure artifact가 남았는지
를 history에서 바로 다시 읽을 수 있게 하는 것

## 5. Failure Artifact Standardization

web-app에서 실행된 ingestion job 결과는 이제 표준 artifact를 남긴다.

현재 기준:

- every run:
  - `.note/finance/run_artifacts/<run-key>/result.json`
  - `.note/finance/run_artifacts/<run-key>/manifest.json`
- when symbol-level issues exist:
  - `csv/<run-key>_failures.csv`

failure CSV는 다음 같은 symbol-level issue를 표준 row로 남긴다.

- `failed_symbol`
- `provider_missing`
- `provider_no_data`
- `rate_limited`
- `price_stale_diagnosis`
- fallback `job_status`

제한:

- 이 표준화는 현재 “web-app job result” 기준이다
- underlying collector 자체가 모두 같은 artifact 정책을 가지는 것은 아직 아니다

즉 이번 pass는

- operator-facing artifact standardization first pass

로 보는 것이 맞다.

## Usage Guidance

### A. Quarterly preview에서 `Covered < Requested`

1. `Coverage Gap Drilldown`을 연다
2. `Need Raw Collection`이 있으면
   - `Extended Statement Refresh`로 보낸다
3. `Raw Exists / Shadow Missing`이 많으면
   - `Statement Shadow Rebuild Only`로 보낸다

### B. 코드를 고친 뒤 결과가 기대와 다를 때

1. `Runtime / Build`의 `Loaded At`과 `Git SHA`를 본다
2. 최근 run의 `Run Inspector`에서 `runtime_marker`를 본다
3. old runtime으로 보이면 서버 restart 후 다시 실행한다

### C. 실패 원인을 다시 보고 싶을 때

1. `Persistent Run History`에서 run 선택
2. `Run Inspector` 확인
3. 필요하면 `Run Artifacts`와 `Related Logs`를 같이 본다
4. symbol-level issue는 `Failure CSV Preview`에서도 다시 볼 수 있다

## Recommended Test Flow

1. `Ingestion` 화면 상단에서 `Runtime / Build`가 보이는지 확인
2. `Statement Shadow Rebuild Only` 카드가 보이는지 확인
3. quarterly prototype에서 `Coverage Gap Drilldown`을 열고 두 action bridge 버튼이 보이는지 확인
4. 버튼을 눌러 ingestion 카드에 symbols/freq가 실제로 prefill 되는지 확인
5. run 하나 실행 후 `Persistent Run History > Run Inspector`에서 runtime marker / artifacts / related logs가 보이는지 확인
6. symbol-level issue가 있는 run 뒤 `Failure CSV Preview`에서 새 standardized CSV가 뜨는지 확인

## Recommendation

현재 기준으로 이 다섯 가지 보강은 같이 묶는 것이 맞다.

이유:

- runtime/build indicator는 old process confusion을 줄이고
- shadow rebuild helper는 quarterly recovery 시간을 줄이고
- action bridge는 operator handoff 비용을 줄이고
- run inspector와 artifacts는 긴 run의 사후 분석 비용을 줄인다

즉 각각이 따로 있는 것보다, 함께 있어야 operator workflow가 하나의 닫힌 루프로 완성된다.
