# Overview Futures Macro Probabilistic State Outlook V2 Design

Status: Written design review pending
Last Updated: 2026-07-20

## 1. User Intent

이 작업은 미래 좌표를 억지로 만드는 기능이 아니다.

사용자가 끝내려는 일은 다음과 같다.

1. 과거부터 현재까지 시장 상태가 실제로 어떻게 이동했는지 본다.
2. 현재와 유사한 과거 상태 뒤에 5D / 20D 상태가 어디로 이동했는지 분포로 본다.
3. momentum이 macro context 안에서 지속되기 쉬운지 또는 반전되기 쉬운지 구분한다.
4. 검증 근거가 없으면 예상 위치 대신 `예측 우위 없음`을 확인한다.

성공은 항상 forecast를 공개하는 것이 아니다.
`5D만 확률 edge`, `20D no edge`, `regime probability는 가능하지만 coordinate path는 불가`처럼 horizon과 output 종류별로 다른 결론을 정직하게 공개하는 것이 성공이다.

## 2. Confirmed Existing Behavior

### 2.1 Observed coordinates

현재 state coordinate는 같은 날짜까지의 daily futures returns를 trailing 60D volatility로 표준화하고,
5D family score를 다음 두 축으로 투영한다.

- `x`: `risk_on__5d_z`
- `y`: `rate_pressure__5d_z`, `dollar_pressure__5d_z`, `inflation_pressure__5d_z` 평균

React는 60D path에서 배열 위치 `-21`, `-6`, `-1`을 `20D 전 / 5D 전 / 현재`로 선택한다.
그래서 새 session row가 두 개 생기면 세 anchor가 모두 다른 날짜로 이동한다.

2026-07-17 cutoff를 현재 DB row로 재계산한 좌표와 2026-07-20 cutoff 좌표는 다음과 같다.

| cutoff | anchor | date | x | y |
|---|---|---:|---:|---:|
| 2026-07-17 | 20D | 2026-06-24 | +0.409192 | +0.130136 |
| 2026-07-17 | 5D | 2026-07-12 | -0.227341 | +0.437546 |
| 2026-07-17 | current | 2026-07-17 | -0.704503 | -0.076243 |
| 2026-07-20 | 20D | 2026-06-26 | -0.426852 | -0.298409 |
| 2026-07-20 | 5D | 2026-07-14 | +0.285382 | +0.152634 |
| 2026-07-20 | current | 2026-07-20 | -0.311459 | -0.237478 |

동일 날짜의 PIT feature는 future row 추가 전후 최대 차이 `0.0`이었다.
따라서 이번 증상은 historical look-ahead rewrite가 아니라 rolling-window turnover, row-based anchor shift, incomplete current candle, sparse rendering의 결합이다.

### 2.2 Forecast semantic mismatch

현재 visible forecast terminal은 다음 의미다.

```text
current 5D state coordinate
  + median historical forward cumulative h-day standardized return
```

이는 future date에서 같은 공식으로 다시 계산한 상태가 아니다.

```text
Current implementation: S(t) + median(FORWARD_RETURN_Z(i, h))
Required target:         distribution of S(t+h)
Equivalent displacement: distribution of S(i+h) - S(i)
```

V2는 observed state와 future target이 같은 coordinate/state definition을 공유해야 한다.

### 2.3 Current quality evidence

2026-07-20 materialized snapshot:

| horizon | Brier | baseline Brier | path error | baseline path error | nominal 50% coverage | status |
|---|---:|---:|---:|---:|---:|---|
| 5D | 0.690140 | 0.697565 | 0.735945 | 0.735919 | 0.267692 | PROVISIONAL |
| 20D | 0.719307 | 0.718834 | 0.765790 | 0.782831 | 0.282828 | PROVISIONAL |

5D regime probability는 current gate를 통과할 수 있지만 coordinate path는 baseline을 이기지 못한다.
20D는 coordinate error 일부 개선이 있어도 probability와 coverage가 충분하지 않다.
V2 UI는 이 차이를 하나의 status로 뭉개지 않는다.

## 3. Considered Approaches

### A. Observed UI Only

세 anchor 대신 전체 일별 경로를 보여주되 기존 forecast target은 유지한다.

- 장점: 빠르고 관측 오해가 줄어든다.
- 단점: 예상 위치가 same-state future가 아닌 핵심 오류가 남는다.
- 결정: 단독 해법으로 채택하지 않는다.

### B. Same-State Target + Validated Hybrid — Recommended

완료 session의 실제 trail을 보여주고, historical episode의 same-state transition으로 5D / 20D terminal distribution을 만든다.
momentum-only와 macro-conditioned hybrid는 동일 rolling-origin fold에서 경쟁한다.

- 장점: 사용자 의도와 output 의미가 직접 일치한다.
- 장점: macro가 가치 없으면 자동으로 제외할 수 있다.
- 단점: session finality와 PIT macro alignment를 먼저 확립해야 한다.
- 결정: V2 범위로 채택한다.

### C. Full Supervised / Regime-Switching Research

regularized classifier, tree ensemble, HMM 또는 mixture-of-experts를 폭넓게 탐색한다.

- 장점: nonlinear interaction을 포착할 수 있다.
- 단점: 현재 independent sample과 feature dimension에서 overfit 위험이 크다.
- 결정: B가 baseline을 실제로 개선한 뒤 별도 research task에서만 검토한다.

## 4. State And Target Contract

### 4.1 State function

V2는 state builder를 하나만 둔다.

```text
S(date) = {
  coordinate: (risk_on_5d_z, composite_pressure_5d_z),
  regime: classify_pattern_state(feature_row_at_date),
  transition: transition_state(feature_row_at_date),
  coverage: available families and symbols
}
```

관측 trail, historical episode origin, future target, realized outcome가 모두 이 함수를 재사용한다.

### 4.2 Forecast targets

각 origin `i`, horizon `h in {5, 20}`에 대해 다음을 저장한다.

```text
origin_state = S(i)
terminal_state = S(i+h)
delta_state = coordinate(S(i+h)) - coordinate(S(i))
terminal_regime = regime(S(i+h))
```

`i+h`는 canonical completed futures session index 기준이다.
raw UTC calendar row count나 symbol별 서로 다른 최신 날짜를 horizon으로 사용하지 않는다.

### 4.3 Published questions

모델은 horizon마다 세 질문을 분리한다.

1. `P(terminal regime | current evidence)`는 baseline보다 나은가?
2. `terminal coordinate distribution`은 baseline보다 정확하고 calibrated한가?
3. `transition/path shape`는 공개할 만큼 안정적인가?

1만 통과하면 regime probability만 표시한다.
1과 2가 통과하면 terminal density를 표시한다.
3까지 통과할 때만 direction vector 또는 transition detail을 공개한다.

## 5. Completed Session Contract

### 5.1 Canonical session date

daily futures row의 raw `candle_time_utc.date()`를 그대로 horizon index로 사용하지 않는다.
전용 resolver가 provider timestamp, instrument exchange/session family, collection time을 받아 canonical trade session date와 finality를 만든다.

```text
resolve_futures_daily_session(
  provider_symbol,
  candle_time_utc,
  collected_at,
  evaluation_time,
) -> {
  session_date,
  status: FINAL | IN_PROGRESS | UNKNOWN,
  reason
}
```

최신 current state는 required family coverage가 충족된 가장 최근 `FINAL` common session만 사용한다.
현재 session이 `IN_PROGRESS`면 이전 final snapshot을 유지하고 화면에는 다음 확정 예정일만 보조 안내한다.

### 5.2 Safety behavior

- UI entry는 provider를 호출하지 않는다.
- `일봉 갱신`은 raw rows 저장 후 finality resolver를 거쳐 snapshot을 materialize한다.
- final common session이 기존 snapshot보다 새롭지 않으면 current snapshot을 교체하지 않는다.
- missing family를 forward-fill하지 않는다.
- resolver가 안전한 finality를 결정하지 못하면 V2 forecast materialization을 중단하고 이전 latest-good snapshot을 유지한다.

### 5.3 Immutable forecast identity

현재 `overview_current` UPSERT는 빠른 read model로 유지한다.
별도 compact history는 다음 identity를 append-only로 보존한다.

- canonical as-of session date
- source marker / input fingerprint
- feature/state schema version
- model candidate/version
- momentum/macro/event coverage
- horizon forecast/status/validation summary
- materialized/known-at timestamp

같은 source marker와 model version 재실행은 idempotent하며, 다른 input fingerprint는 새 row다.

## 6. Predictor Architecture

### 6.1 Required baselines

모든 candidate는 같은 fold와 target으로 다음 baseline을 이겨야 한다.

- `B0 Unconditional`: training window의 terminal regime frequency / terminal delta distribution
- `B1 Persistence`: current regime 유지와 zero-delta 또는 recent-state persistence
- `M1 Momentum-only`: reduced cross-asset price-state analog
- `M2 Hybrid`: M1 + PIT macro condition + scheduled event risk

production은 horizon별 best validated candidate를 선택한다.
5D와 20D가 다른 candidate를 선택할 수 있다.

### 6.2 Momentum-only features

현재 6 family × 10 suffix 전체를 무조건 거리 계산에 사용하지 않는다.
초기 candidate는 해석 가능하고 중복이 낮은 feature로 제한한다.

- current x / y level
- 1D impulse relative to 5D
- 5D slope / acceleration
- 20D direction / persistence
- family breadth / coherence
- realized volatility regime
- cross-family conflict flag
- coverage quality

exact feature count와 weight는 implementation plan의 ablation test로 결정하되, fold 밖 결과를 보고 tuning하지 않는다.

### 6.3 Macro conditioning

Macro는 forecast 방향을 강제하는 독립 규칙이 아니라 M1 distribution의 soft conditioning이다.

V2 initial context:

- PIT growth state
- PIT inflation state
- policy / rate-pressure state
- financial-condition proxy state
- current and horizon-contained official event count/type: FOMC, CPI, PPI, Employment, GDP

Economic Cycle의 ALFRED/release-aware history를 재사용한다.
daily futures origin에는 그 시점에 알려진 최신 macro state만 backward as-of join한다.
수정된 최신 macro value를 과거 origin에 복사하지 않는다.

현재 저장 Event calendar는 official schedule context를 제공하지만 consensus/actual surprise history는 제공하지 않는다.
따라서 V2 initial event feature는 `upcoming event risk / density`까지만 포함한다.
surprise direction은 별도 PIT consensus source가 승인·구축되기 전에는 만들지 않는다.

### 6.4 Soft hybrid

hard regime filtering은 independent sample을 지나치게 쪼개므로 사용하지 않는다.
V2는 별도 macro forecast model을 섞지 않고 기존 analog distance에 macro/event distance를 soft하게 더한다.

```text
combined_distance
  = momentum_distance
  + lambda_macro * macro_context_distance
  + lambda_event * event_risk_distance

episode_weight = exp(-combined_distance / temperature)
```

고정 candidate grid는 다음과 같다.

- `M1 momentum-only`: `lambda_macro=0`, `lambda_event=0`
- `M2a light hybrid`: `lambda_macro=0.25`, `lambda_event=0.25`
- `M2b balanced hybrid`: `lambda_macro=0.50`, `lambda_event=0.50`
- `M2c macro-sensitive`: `lambda_macro=1.00`, `lambda_event=0.50`

distance scaling과 `temperature`는 outer evaluation fold 밖의 inner chronological training fold에서만 결정한다.
outer fold마다 같은 candidate set과 trial count를 기록한다.
macro가 incremental out-of-sample value를 만들지 않으면 production은 M1을 선택한다.

## 7. Validation And Publication

### 7.1 Rolling-origin rules

- feature, scaler, weight, neighborhood, macro join은 origin 당시 data만 사용한다.
- horizon overlap을 purge한다.
- adjacent episode는 de-overlap한다.
- candidate selection과 evaluation fold를 분리한다.
- 5D / 20D를 독립 평가한다.
- algorithm version 변경 전 sensitivity와 candidate trial count를 기록한다.

### 7.2 Metrics

Regime probability:

- multiclass Brier versus B0/B1
- log loss versus B0/B1 when finite
- calibration error / reliability bins
- fold improvement ratio
- probability confidence interval

Terminal coordinate:

- Euclidean terminal error versus zero-delta / unconditional-delta baseline
- joint 50% / 80% region empirical coverage
- region sharpness / area
- horizon별 median and tail error

Forecast stability:

- adjacent final-session probability distribution change
- terminal center change
- status flip frequency

### 7.3 Statuses

- `OBSERVED`: completed session current state
- `VERIFIED`: configured minimum sample과 rolling-origin baseline/calibration gate 통과
- `PROVISIONAL`: 계산 가능하지만 공개 gate 일부 미달
- `NO_EDGE`: 충분히 평가했으나 baseline 개선 없음
- `UNAVAILABLE`: sample/data/model 계산 불가
- `PENDING_SESSION_FINALIZATION`: 최신 daily row가 아직 final이 아님

`NO_EDGE`는 실패나 오류가 아니라 정상적인 사용자 결과다.

Primary UI publication은 다음처럼 고정한다.

- probability `VERIFIED`: absolute/baseline/lift numeric probability를 첫 화면에 표시
- probability `PROVISIONAL`: 첫 화면에는 `검증 중 · 확정 우위 없음`, numeric distribution은 방법론 disclosure에만 표시
- probability `NO_EDGE`: baseline 개선 없음과 선택되지 않은 candidate를 표시, numeric conditional probability는 첫 화면에서 숨김
- coordinate `VERIFIED`: joint terminal density를 표시
- coordinate `PROVISIONAL / NO_EDGE / UNAVAILABLE`: terminal density, marker, vector를 모두 숨김
- path `VERIFIED`: zero-excluding displacement일 때만 compact direction vector 허용

## 8. UI Design Contract

### 8.1 Observed trail

- 최근 30 final sessions를 날짜 순서대로 모두 연결한다.
- 과거는 옅게, 최근은 진하게 표시한다.
- `20행 전 / 5행 전 / 현재` marker는 보조 anchor이며 실제 날짜를 항상 함께 제공한다.
- current marker는 raw final state다. smoothing으로 원본을 대체하지 않는다.
- x/y 모두 versioned fixed semantic domain `[-2.5, +2.5]`를 사용한다.
- domain 밖 outlier는 경계 clip marker와 실제 raw value tooltip으로 표시하며 화면 전체 scale을 바꾸지 않는다.
- previous final snapshot을 optional ghost trail로 겹칠 수 있지만 V2 initial 필수 범위는 아니다.

### 8.2 Conditional outlook

5D와 20D를 별도 small multiple 또는 explicit selector로 보여준다.

- absolute regime probability
- unconditional/persistence baseline probability
- probability lift
- selected candidate: momentum-only / hybrid / no edge
- independent sample, validation status, as-of session
- terminal joint 50% / 80% density region when coordinate gate passes
- top analog dates and individual trail은 disclosure에만 둔다.

단일 점선은 기본 표현이 아니다.
방향 vector는 coordinate/path gate가 통과하고 displacement uncertainty가 zero를 명확히 배제할 때만 표시한다.

### 8.3 User-first reading

첫 화면은 다음 순서다.

1. completed current state와 실제 최근 trail
2. 5D / 20D `확률 edge 있음 / 없음`
3. 검증된 경우에만 terminal density
4. macro가 forecast를 얼마나 조정했는지
5. 방법론, sample, metric, closest episode detail

run/job/row 진단 패널을 새로 만들지 않는다.
data finality와 source identity는 사용자 판단을 돕는 compact evidence로만 표시한다.

## 9. Service And File Ownership

Expected primary owners:

- `app/services/futures_macro_pattern.py`
  - canonical state function, observed trail, same-state target primitives
- `app/services/futures_macro_pattern_validation.py`
  - candidate selection, momentum/hybrid comparison, rolling-origin metrics, publication status
- `app/services/futures_macro_snapshot.py`
  - completed-session materialization and compact current/history payload
- `finance/data/futures_market.py`
  - raw daily collection boundary and source timestamp evidence
- `finance/data/futures_macro_snapshot.py`
  - current snapshot plus immutable compact forecast history persistence
- `finance/loaders/economic_cycle.py` and relevant economic-cycle services
  - read-only PIT macro context; existing publication model is not changed
- `finance/data/market_intelligence.py` / Overview Events loader
  - official scheduled event context; no forecast calculation ownership
- `app/web/streamlit_components/futures_macro_workbench/src/PatternMapSection.tsx`
  - observed trail and validated terminal density rendering only
- `app/web/overview/futures_macro_helpers.py`
  - thin payload/action bridge

Exact new module/table names are finalized in the implementation plan after written design approval.

## 10. Error And Degradation Behavior

| Condition | Behavior |
|---|---|
| current daily candle in progress | keep previous final state, show pending finalization evidence |
| one family missing | do not fill; downgrade observation/forecast coverage |
| macro PIT missing | M2 unavailable, evaluate/publish M1 if valid |
| event schedule missing | event adjustment unavailable, do not assume no event |
| momentum/hybrid no baseline edge | publish `NO_EDGE`, no expected position/vector |
| probability valid, coordinate invalid | show probabilities only |
| snapshot algorithm mismatch | DB-only UI asks for daily materialization refresh |
| history write failure | do not erase latest-good current snapshot; ingestion result becomes partial success |

## 11. Test And QA Contract

### Python unit / service tests

- future rows do not change a completed historical state
- same cutoff reconstructs identical state and target
- in-progress candle cannot replace final current state
- Sunday evening / holiday session maps to the intended canonical trade date
- `terminal_state` uses the same state function as observed state
- 5D / 20D target row spacing is canonical-session based
- macro as-of join never reads later release/vintage
- missing macro does not contaminate momentum-only candidate
- hybrid is selected only when it improves the configured rolling-origin gate
- evaluated no-improvement returns `NO_EDGE`
- probability-only publication suppresses coordinate density/vector
- immutable forecast history is idempotent by input/model identity

### React / payload tests

- observed trail contains every bounded final session, not only three anchors
- actual dates are present in accessible labels/tooltips
- `NO_EDGE` has no terminal marker, range, or direction line
- probability valid / coordinate invalid renders probability rows only
- 5D / 20D selected candidate and macro adjustment are explicit
- fixed semantic axes do not change across horizon selector states

### Actual QA

- reproduce 2026-07-17 and 2026-07-20 with fixed cutoffs
- confirm same historical date coordinates are stable
- confirm current in-progress row does not replace last final snapshot
- desktop and 420px Browser QA
- attach one generated screenshot; do not commit unless requested

## 12. Tradeoffs And Non-Goals

- Completed-only state is less fresh than an intraday point but is comparable and reproducible.
- Soft macro conditioning may provide no incremental edge; that outcome is accepted.
- Event schedule widens uncertainty but does not predict surprise direction.
- Same-state target answers future regime/location, not future asset return or trade P&L.
- A future coordinate distribution cannot be called a price forecast or investment recommendation.
- V2 prioritizes honest suppression over visually complete forecasts.

## 13. Approval Checklist

The user should confirm the following before implementation planning:

- completed-session state may intentionally lag the live futures monitor
- 5D and 20D can select different models or both return `NO_EDGE`
- macro is a validated soft condition, not a mandatory directional rule
- initial event layer uses official schedules but not consensus surprise direction
- expected line/location is absent unless its own validation gate passes
- exact UI layout can be refined in implementation, but the observation/forecast semantics do not change
