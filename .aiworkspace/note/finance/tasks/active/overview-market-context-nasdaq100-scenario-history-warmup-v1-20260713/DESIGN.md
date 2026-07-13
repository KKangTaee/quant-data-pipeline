# Overview Market Context Nasdaq-100 Scenario History Warmup V1 Design

Status: Approved in Conversation — Written Spec Review Requested
Last Updated: 2026-07-13

## 이걸 하는 이유?

Nasdaq-100 · QQQ proxy 그래프 1은 최근 60개월의 완결 PER만 있으면 표시할 수 있지만, 그래프 2의 1년·3년·5년 적정구간 이력은 각 표시 월마다 직전 60개월 PER 분포가 필요하다. 현재 DB에는 positive READY PER가 정확히 60개월만 있어 마지막 월 한 점만 계산된다. React는 두 점 미만을 그래프로 표시하지 않으므로 모든 기간이 빈 상태가 된다.

SEP vintage가 없는 것은 아니다. DB에는 21개 SEP release vintage가 있으며 S&P 500은 같은 SEP 자료로 12/36/60점을 반환한다. Nasdaq 화면의 `과거 SEP vintage가 준비되면` 문구는 실제 원인을 잘못 설명한다. 실제 부족분은 rolling PER warmup이다.

## Decision Summary

Nasdaq-100 적정구간 이력용 자료 보강 범위를 최대 119개월로 확장한다. 계산 방식은 기존 60개월 rolling log(PER) 분포, point-in-time `available_at`, 월별 weighted coverage 95% gate를 그대로 유지한다.

- 1년 표시 12점에는 최소 `60 + 12 - 1 = 71개월`의 positive READY PER가 필요하다.
- 3년 표시 36점에는 최소 `60 + 36 - 1 = 95개월`이 필요하다.
- 5년 표시 60점에는 최소 `60 + 60 - 1 = 119개월`이 필요하다.
- 부족한 월은 QQQ holdings, constituent SEC actual diluted EPS, EOD price로 다시 수집한다.
- 무료 원천에서 확인할 수 없는 값은 합성하거나 coverage gate를 낮추지 않는다.

## Approaches Considered

### A. 최대 119개월 실제 자료 보강 — Selected

기존 resumable repair planner/job에 `months=119`를 전달해 현재 DB의 60 READY 월 앞쪽을 보강한다. 이미 준비된 월과 symbol은 다시 수집하지 않고, 수집 후 같은 strict materialization을 실행한다.

장점은 S&P와 같은 60개월 rolling 통계 계약을 유지하면서 1·3·5년 그래프를 복구한다는 점이다. 단점은 과거 편입·퇴출 종목이 늘어 동기 실행 시간이 길어지고 무료 원천 gap이 남을 수 있다는 점이다.

### B. Rolling Window를 60개월보다 짧게 축소 — Rejected

현재 60개월만으로 더 많은 점을 만들 수 있지만, 시점마다 서로 다른 표본 길이를 사용하거나 5년 분포 의미를 바꾸게 된다. S&P와 Nasdaq 비교 가능성도 약해지므로 채택하지 않는다.

### C. 부족한 EPS·가격을 보간 또는 proxy로 합성 — Rejected

그래프는 빠르게 채울 수 있지만 실제 희석 EPS coverage라는 기존 품질 계약을 훼손하고, 무료 원천에서 확인되지 않은 값을 사실처럼 표시하게 된다. blocked 월은 blocked로 보존한다.

## User Flow

```text
Nasdaq-100 valuation READY
  -> 그래프 2의 선택 기간 이력 부족 안내
  -> 1·3·5년 적정구간 자료 보강
  -> 최대 119개월 gap 진단
  -> EPS/가격 target만 동기 수집
  -> 119개월 strict rematerialization
  -> cache clear + rerun
  -> 선택 기간 graph 또는 정확한 잔여 부족 안내
```

화면 진입만으로 provider를 호출하지 않는다. 사용자가 action을 눌렀을 때만 수집하며, 현재 화면에서 완료될 때까지 기다리는 기존 synchronous 방식과 nonce 중복 방지를 재사용한다.

## Architecture And Ownership

```text
MarketContextValuation.tsx
  -> action event {id: repair_nasdaq100_history_119m, nonce}
  -> market_context_helpers.py consume/dedup/progress/rerun
  -> overview_actions.py bounded action facade
  -> ingestion_jobs.py repair(months=119)
  -> finance/data/nasdaq100_valuation.py planner + strict materialization
  -> finance_* DB
  -> loader/service history diagnostics
  -> React graph or actionable empty state
```

### Repair Window Contract

기존 `run_repair_nasdaq100_valuation_coverage(..., months=...)`와 planner의 parameterized window를 재사용한다. 새 schema나 checkpoint table을 만들지 않는다.

- 현재 coverage blocker action은 최근 가치평가 복구용 60개월 계약을 유지한다.
- valuation 자체가 READY지만 history warmup이 부족하면 별도 `repair_nasdaq100_history_119m` action을 노출한다.
- history action은 최대 119개월을 요청한다. DB에 존재하는 observation month 범위와 planner가 계산한 gap만 실제 target이 된다.
- 성공 batch는 즉시 canonical DB에 남고 재실행 planner가 이미 충족된 target을 제외한다.

### Historical Scenario Diagnostics

공유 계산 함수 `calculate_historical_index_scenario`는 결과가 두 점 미만일 때 다음 진단을 반환한다.

```python
{
  "status": "INSUFFICIENT_HISTORY",
  "reason_code": "INSUFFICIENT_ROLLING_PER_WARMUP",
  "rolling_window_months": 60,
  "requested_display_months": 60,
  "required_history_months": 119,
  "available_history_months": 60,
  "missing_history_months": 59,
  "observation_count": 1,
}
```

`required_history_months`는 `rolling_window + requested_display_months - 1`이다. `available_history_months`는 계산 종료월까지 실제 positive PER를 가진 월 수다. S&P READY payload에도 같은 진단 필드를 추가할 수 있지만 기존 READY status와 12/36/60 point 계약은 바꾸지 않는다.

### Nasdaq EPS Source Metadata

Nasdaq service가 graph 2 earnings payload에 다음 실제 source metadata를 명시한다.

- `eps_source`: `QQQ 구성종목 실제 희석 EPS 재구성`
- `eps_source_quality`: `reconstructed_actual`
- `eps_basis_date`: latest Nasdaq monthly evidence의 `earnings_available_through`

React는 Nasdaq source가 없을 때 `Robert Shiller TTM EPS`로 임의 fallback하지 않는다. instrument별 source가 미확정이면 `EPS 출처 미확정`으로 표시한다. 이 변경은 빈 그래프의 직접 원인은 아니지만 같은 화면의 잘못된 근거 표시를 함께 바로잡는다.

### React Empty State And Action

그래프 2 empty state는 선택한 기간의 실제 부족량을 표시한다.

- title: `적정구간 계산 이력이 부족합니다`
- body 예시: `5년 흐름에는 119개월이 필요하지만 현재 60개월이 준비됐습니다.`
- helper: `60개월 rolling PER 사전 이력을 포함해 부족한 EPS와 가격을 보강합니다.`
- primary action: `1·3·5년 적정구간 자료 보강`
- pending: `과거 적정구간 자료를 보강하는 중`
- retry: `남은 적정구간 자료 다시 보강`

진단 row를 별도 운영 패널로 만들지 않는다. 필요한 월 수와 현재 월 수는 사용자가 다음 행동을 판단하는 근거로 empty state 안에만 둔다.

### QQQ Instrument Labels

history graph의 tooltip, legend, aria label에서 S&P 전용 `SPX` 문구를 하드코딩하지 않는다. 선택 instrument에 따라 `실제 QQQ` / `적정 QQQ` 또는 `실제 SPX` / `적정 SPX`를 사용한다.

## Error Handling

- planner failure: 수집을 시작하지 않고 현재 graph 1과 graph 2 empty state를 유지한다.
- individual EPS/price failure: 성공 batch를 보존하고 사용할 수 있는 입력으로 materialization을 계속한다.
- partial result: READY 월을 과장하지 않고 현재/필요 월 수와 재시도 action을 표시한다.
- materialization failure: cache를 clear하지 않고 기존 read model을 유지한다.
- unsupported free source: 합성하지 않고 planner/result evidence에 남긴다.
- 화면 재진입: 자동 수집하지 않으며 저장된 DB 결과만 다시 읽는다.

## Point-In-Time And Quality Boundaries

- constituent EPS는 filing-aware `available_at` 이후 월에만 사용한다.
- 해당 observation month까지 확인된 holdings snapshot과 EOD price만 사용한다.
- 월별 actual diluted EPS/price weighted coverage 95% 미만은 READY로 승격하지 않는다.
- 현재 Nasdaq universe를 과거 전체에 복제하지 않고 저장된 historical QQQ holdings를 사용한다.
- blocked 월을 보간하거나 가장 가까운 READY 월로 대체하지 않는다.
- 60개월 rolling log(PER) 분포와 scenario formula를 변경하지 않는다.

## Test Strategy

### 1차 — Contract / Failure Reproduction

- 60 positive PER months가 5년 요청에서 한 점만 반환하는 기존 실패를 재현한다.
- 1/3/5년 required history가 각각 71/95/119임을 검증한다.

### 2차 — 119-Month Repair

- repair action이 `months=119`를 planner와 materialization에 전달한다.
- 이미 준비된 target 제외, partial failure resume, UPSERT idempotency를 회귀 검증한다.

### 3차 — Service Metadata

- insufficient history reason/required/available/missing contract를 검증한다.
- Nasdaq EPS source/quality/basis date가 실제 QQQ reconstruction evidence를 가리키는지 검증한다.
- S&P 12/36/60 READY history가 유지되는지 검증한다.

### 4차 — UI Contract

- READY valuation에서도 history 부족일 때만 action이 보인다.
- 선택 기간별 정확한 필요/현재 월 수를 표시한다.
- event id/nonce, pending/retry, instrument-aware QQQ labels를 검증한다.

### 5차 — Actual / Browser QA

- actual DB에서 119개월 plan과 target 수를 먼저 확인한다.
- bounded smoke 후 최대 119개월 동기 repair를 실행한다.
- 1년 12점, 3년 36점, 5년 60점 또는 무료 원천 gap에 따른 정확한 partial state를 확인한다.
- desktop/420px, console error, horizontal overflow를 확인하고 generated screenshot은 commit하지 않는다.

## Success Criteria

- 60개월 rolling 통계 기준과 95% coverage gate를 유지한다.
- 충분한 실제 자료가 수집되면 Nasdaq graph 2가 1년 12점, 3년 36점, 5년 60점을 반환한다.
- 부족하면 SEP가 아니라 rolling PER warmup 부족임을 선택 기간별 숫자로 설명한다.
- 사용자는 READY 화면에서 한 번의 action으로 최대 119개월 보강과 재계산을 시작할 수 있다.
- Nasdaq EPS source와 QQQ graph labels가 실제 instrument/source와 일치한다.
- 화면 진입은 read-only이며 provider 호출은 명시 action에서만 발생한다.
- unrelated untracked research folder, generated screenshots, run history artifact는 stage하지 않는다.

## Out Of Scope

- coverage gate 완화
- 60개월 rolling window 축소
- missing EPS/price 보간 또는 proxy 합성
- 유료·계정·token provider
- background queue/daemon
- 새 DB schema/checkpoint table
- 공식 Nasdaq-100 index-level P/E/EPS 표방
