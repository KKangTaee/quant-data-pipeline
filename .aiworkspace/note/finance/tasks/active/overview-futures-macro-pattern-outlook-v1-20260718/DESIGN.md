# Futures Macro Pattern Outlook V1 Design

Status: Approved — UI Direction A
Last Updated: 2026-07-18

## 1. Design Summary

Futures Macro V1은 `빠른 시장 재가격화 + 향후 1~4주 위험 체제 전이`를 설명한다.

```text
Stored futures daily OHLCV
  -> point-in-time multi-horizon features
  -> current pattern state
  -> historical episode / conditional outcome engine
  -> validation and publication gate
  -> Futures Macro React workbench
```

첫 화면의 핵심 질문은 다음과 같다.

1. 오늘 새롭게 발생한 위험은 무엇인가?
2. 그 움직임은 1주·1개월 흐름을 강화하는가, 되돌리는가?
3. 현재는 지속·전환·충돌·저신호 중 어느 패턴인가?
4. 이 패턴 뒤 5D / 20D 위험 체제는 평소보다 어느 방향이 더 자주 나타났는가?
5. 그 우위는 검증됐는가, 잠정인가, 판단 불가인가?
6. 어떤 조건이 바뀌면 현재 해석도 바뀌는가?

## 2. Existing Problem

현재 `compute_symbol_metrics()`는 최신 화면용 1D / 3D / 5D / 20D / 60D 변화를 계산한다.
하지만 historical validation은 과거 각 날짜에서 5D / 20D feature를 `None`으로 두고 1D standardized move만으로 scenario를 다시 생성한다.
그 결과 `과거 점검`은 다중 기간 패턴 매칭이 아니라 같은 1일 scenario label의 결과 집계다.

2026-07-18 read-only actual audit:

- daily history: 2021-02-19 ~ 2026-07-17, 5.4년
- validation dates: 1,175
- `혼재된 매크로 흐름`: 915일, 약 77.9%
- mixed scenario는 target family와 directional rule이 없어 5D / 20D 결과가 비어 있음
- 현재 1D, 1W, 1M 흐름은 서로 다른 정보를 주지만 historical match에는 1D만 들어감

따라서 UI 문구 개선이 아니라 feature, state, validation, publication contract를 함께 바꿔야 한다.

## 3. Considered Approaches

### Approach A. Rule-Based Persistence Copy

1D / 5D / 20D의 부호와 임계값으로 `지속`, `반전`, `확산`, `혼재` 문구만 만든다.

- 장점: 빠르고 해석 가능하며 표본 요구가 낮다.
- 단점: 향후 확률과 기준 확률 대비 우위를 답하지 못한다.
- 판단: 현재 흐름 설명 보강에는 사용하지만 최종 해법으로는 부족하다.

### Approach B. Multi-Window Historical Pattern Outlook — Recommended

1D 충격, 5D 흐름, 20D 체제, breadth, conflict, volatility를 하나의 point-in-time pattern state로 만들고,
과거 유사 episode의 5D / 20D 결과 분포를 unconditional baseline과 비교한다.

- 장점: 사용자의 원래 의도와 직접 맞고, 유사 episode와 결과 근거를 설명할 수 있다.
- 단점: 독립 표본 수가 빠르게 줄며, similarity contract와 validation을 엄격히 설계해야 한다.
- 판단: V1 권장. rule-based current interpretation과 함께 사용한다.

### Approach C. Supervised Probabilistic Regime Model

다중 기간 feature로 calibrated logistic model, tree ensemble 또는 regime model을 학습한다.

- 장점: feature interaction을 더 잘 반영하고 확률을 직접 생성할 수 있다.
- 단점: 현재 5.4년 history로 overfit 위험이 크며, 사용자가 유사 과거를 확인하기 어렵다.
- 판단: V1 검증 framework와 더 긴 history가 확보된 후 후속 후보로 둔다.

## 4. Time And Ownership Contract

| Surface | Observation | Forecast / Interpretation | Owner |
|---|---|---|---|
| Futures live monitor | 1m / 15m / 60m | 현재 shock / freshness | existing monitor |
| Futures Macro today | 1D | 오늘의 재가격화와 근거 | existing thermometer, refined copy |
| Futures Macro pattern | 1D + 5D + 20D | 지속·전환·충돌·저신호 | new pattern state |
| Futures Macro outlook | current pattern | next 5D / 20D conditional regime distribution | new pattern validation |
| Economic Cycle | monthly official macro vintages | current +1M / +2M economic phase | existing economic cycle |

선물 매크로는 경제사이클의 월별 구조 판단을 복제하지 않는다.
경제사이클과의 연결은 `구조 배경과 빠른 시장 반응이 일치 / 불일치`하는 보조 설명으로만 둔다.

## 5. Current Pattern State

### 5.1 Input Features

각 날짜의 feature는 그 날짜까지 공개·저장된 데이터만 사용한다.

#### Score families

- Risk-On
- Growth / Cyclical
- Rate Pressure
- Dollar Pressure
- Safe Haven
- Inflation / Commodity Pressure

#### Per-family multi-window features

- 1D standardized shock
- 5D cumulative move and mean daily standardized move
- 20D cumulative move and mean daily standardized move
- 5D / 20D slope
- recent 5D versus previous 5D acceleration
- sign persistence: 같은 방향을 유지한 일수와 비율
- breadth: family member 중 같은 방향에 동참한 비율
- volatility state: 20D volatility versus trailing baseline
- reversal flag: 1D가 5D / 20D 방향과 반대이고 material threshold를 넘는지

#### Cross-family features

- Risk-On versus Safe Haven conflict
- Growth versus Rate Pressure conflict
- Risk-On versus Dollar Pressure conflict
- Inflation Pressure versus Growth divergence
- overall coherence / dispersion
- available symbol count and missing family state

### 5.2 State Labels

V1의 state label은 설명용이며 확률 target을 강제하지 않는다.

- `확산 중`: 여러 family에서 같은 위험 체제가 넓어짐
- `지속 중`: 5D와 20D 방향이 같고 breadth가 유지됨
- `전환 시도`: 1D / 5D가 20D와 반대로 material하게 움직임
- `충돌`: 중요한 family가 상반된 체제를 지지함
- `저신호 / 관망`: 움직임과 breadth가 모두 임계값 아래
- `자료 부족`: required family 또는 history 부족

state는 `overall regime`과 `transition phase`를 분리한다.
예: `방어적 위험 체제 · 전환 시도`, `물가 부담 체제 · 지속 중`.

### 5.3 Change Conditions

각 state는 다음 관찰에서 해석이 바뀌는 명시적 조건을 제공한다.

- 어떤 family score / breadth가 어느 방향으로 바뀌어야 하는가
- 1D 반전이 5D persistence로 확인되려면 무엇이 필요한가
- data gap이 채워져야 하는 family가 있는가

이 조건은 매매 trigger가 아니라 현재 해석의 invalidate / confirmation 기준이다.

## 6. Conditional Outlook Engine

### 6.1 Primary Outcome

첫 결과는 `전체 위험 체제`다.

- Risk-seeking
- Defensive / risk-off
- Inflation / rate pressure
- Mixed / no dominant edge

자산 family별 forward return은 이 분류의 근거와 보조 분포로 둔다.

각 historical episode의 forward outcome은 다음 순서로 만든다.

1. episode 기준일까지의 trailing 60D volatility만 사용해 향후 5D / 20D family return을 표준화한다.
2. 기존 score family weight를 재사용해 forward Risk-On, Rate Pressure, Dollar Pressure, Safe Haven, Inflation Pressure를 계산한다.
3. 절대값이 material threshold를 넘는 family만 directional evidence로 인정한다.
4. 아래 mutually exclusive precedence로 하나의 outcome regime을 부여한다.
   - `Inflation / rate pressure`: Rate / Dollar / Inflation pressure 중 둘 이상이 같은 부담 방향이고 Risk-On이 이를 압도하지 못함
   - `Defensive / risk-off`: Risk-On이 음(-)의 material move이며 Safe Haven 또는 Dollar Pressure가 확인함
   - `Risk-seeking`: Risk-On이 양(+)의 material move이며 breadth가 충족되고 Defensive 조건이 아님
   - `Mixed / no dominant edge`: 위 조건 미충족 또는 중요한 family 충돌

material threshold와 breadth threshold는 기존 `SIGNAL_Z_THRESHOLD` / family coverage contract를 초기값으로 사용하고,
actual outcome을 본 뒤 유리하게 조정하지 않는다. 변경하려면 sensitivity 결과와 별도 설계 승인이 필요하다.

### 6.2 Horizons

- 5D: 다음 1주 위험 체제와 주요 family 방향
- 20D: 다음 1개월 위험 체제와 주요 family 방향

1D forward result는 raw validation detail에 남길 수 있지만 hero probability로 공개하지 않는다.

### 6.3 Similar Episode Selection

V1은 투명한 multi-window historical matching을 사용한다.

- feature는 당시 trailing data만 사용한다.
- 현재 feature와 historical feature를 robust-standardize한다.
- family level, slope, persistence, breadth, conflict를 가중 거리로 비교한다.
- exact label match를 요구하지 않고 nearest episode를 찾는다.
- 동일한 연속 구간이 표본 수를 부풀리지 않도록 episode anchor를 분리한다.
- current window와 forward horizon이 겹치는 episode는 제외한다.
- future outcome이 없는 latest rows는 제외한다.
- symbol coverage가 크게 다른 episode는 제외하거나 downgrade한다.

초기 weight는 code constant로 숨기지 않고 result metadata와 test fixture에서 확인 가능하게 둔다.

### 6.4 Published Metrics

각 horizon은 다음을 제공한다.

- dominant conditional regime
- regime별 probability
- unconditional baseline probability
- probability lift / reduction
- independent episode count
- family별 median forward return과 interquartile range
- adverse path summary
- closest episode dates와 similarity quality
- estimate status와 reason

### 6.5 Publication Gate

상태는 경제사이클과 같은 세 단계 시각 문법을 사용한다.

- `VERIFIED`: walk-forward에서 minimum sample, calibration, baseline improvement gate 충족
- `PROVISIONAL`: 계산 가능하지만 sample / stability / coverage 일부 미달
- `UNAVAILABLE`: 확률을 공개하기에 근거 부족

V1 minimum publication rule:

- independent episodes 30개 미만이면 probability를 `UNAVAILABLE`로 둔다.
- 30~59개는 최대 `PROVISIONAL`이다.
- 60개 이상이어도 out-of-sample baseline improvement와 calibration을 통과해야 `VERIFIED`다.
- baseline improvement는 chronological test fold 전체에서 unconditional regime frequency보다 낮은 multiclass Brier score로 확인한다.
- 최소 한 fold만 좋아서는 안 되며, test fold 다수에서 같은 개선 방향이 유지되어야 한다.
- probability calibration은 forecast probability bucket과 observed frequency의 차이를 공개하고, calibration error가 baseline보다 나쁘면 최대 `PROVISIONAL`이다.
- lift가 사실상 0이거나 confidence interval이 기준 확률과 구분되지 않으면 `방향 우위 미확인`이다.
- 빈도 표본과 방향 적중 표본을 구분한다.

숫자 threshold는 구현 전 RED test에서 contract로 고정하고, actual validation 결과에 따라 낮추지 않는다.

## 7. Validation Design

### 7.1 Point-In-Time Correctness

- feature date 이후 OHLCV를 feature 계산에 사용하지 않는다.
- 5D / 20D forward outcome은 feature generation과 별도 단계에서 붙인다.
- rolling normalization은 expanding 또는 trailing past window만 사용한다.
- data availability / missingness도 당시 상태를 보존한다.

### 7.2 Temporal Validation

- chronological walk-forward split
- forward horizon만큼 purge / embargo
- 동일 episode family가 train / test에 걸쳐 과도하게 중복되지 않게 anchor separation
- overlap-adjusted effective sample 공개
- regime probability calibration과 unconditional baseline 비교
- threshold / weight sensitivity는 raw disclosure에 두고 첫 화면에서 숨김

### 7.3 Required Checks

- future leakage sentinel test
- current latest row와 historical replay feature parity
- adjacent date duplicate episode suppression
- insufficient history / missing family fallback
- current pattern without publishable outlook
- mixed pattern에도 target distribution이 계산되되, 우위가 없으면 neutral publication
- deterministic fixture에서 persistence / reversal / conflict 분류 검증

## 8. Service And File Boundaries

### Existing owner retained

- `app/services/futures_macro_thermometer.py`
  - today score, evidence, current symbol metrics
- `app/services/futures_macro_validation.py`
  - legacy scenario validation compatibility until V2 rollout
- `app/web/overview/futures_macro_helpers.py`
  - Streamlit session / action bridge and React payload composition
- `app/web/streamlit_components/futures_macro_workbench/`
  - visible React workbench

### New focused modules

- `app/services/futures_macro_pattern.py`
  - point-in-time multi-window feature and current pattern state
- `app/services/futures_macro_pattern_validation.py`
  - historical replay, episode matching, forward distributions, publication gate

두 새 module은 Streamlit을 import하지 않는다.
기존 1,300줄대 validation module에 새 pattern logic을 계속 추가하지 않는다.

### Persistence

V1은 기존 stored futures daily OHLCV를 읽는다.
새 registry / saved JSONL은 만들지 않는다.
계산 비용이 actual QA에서 UI latency를 해치면 DB schema를 즉시 추가하지 않고, 기존 cache 또는 daily materialized artifact 후보를 별도 설계 checkpoint로 올린다.

## 9. UI Design

기존 경제사이클 React workbench의 visual grammar를 재사용한다.

### Approved Direction A — Context To Outlook

사용자는 2026-07-18 비교 와이어프레임에서 `A · 맥락→전망형`을 선택했다.
첫 화면의 고정 reading order는 아래와 같다.

1. 현재 선물 체제와 오늘 달라진 위험
2. 현재 관측 / 다음 1주 / 다음 1개월 horizon path
3. 최근 패턴 경로와 그 전망의 근거·반대 조건
4. 최근 60거래일 체제 ribbon
5. 자산 family별 현재 흐름·보조 전망·변화 조건
6. 접힌 방법론과 historical episode 품질

`분석 콕핏형`처럼 family score와 raw matrix를 첫 화면에 동시에 펼치거나,
`데일리 브리핑형`처럼 패턴 지도와 검증 근거를 상세 영역으로 내리는 방식은 V1에서 채택하지 않는다.
정보 밀도보다 사용자가 `현재 맥락 -> 조건부 전망 -> 확인할 조건`을 순서대로 이해하는 것을 우선한다.

### Section 1. Hero — 현재 선물 체제

- 큰 체제 제목과 transition phase
- 오늘 위험 요약과 핵심 이유
- 기준일, data coverage, VERIFIED / PROVISIONAL / UNAVAILABLE badge
- refresh는 보조 action이며 hero의 주인공이 아님

### Section 2. Horizon Path — 현재 / 다음 1주 / 다음 1개월

- 현재: 관측 pattern state, 확률로 표현하지 않음
- 다음 1주: 5D conditional regime probabilities
- 다음 1개월: 20D conditional regime probabilities
- 각 전망 카드에 baseline 대비 변화와 검증 상태 표시
- 네 상태 합계는 100%이며 unavailable일 때 숫자를 만들지 않음

### Section 3. Pattern Map + Evidence

왼쪽은 최근 20거래일 경로, 오른쪽은 현재와 전망의 근거다.

- x축: Risk Appetite
- y축: Macro Pressure composite
- 실선: 실제 관측 경로
- 현재점: current pattern
- 미래: 단일 점선 예측 경로가 아니라 matched episode의 5D / 20D outcome을 집계한 반투명 probability zone
- zone 중심은 outcome median, 크기는 interquartile range, opacity는 해당 regime probability를 나타냄
- hover / focus: 날짜, state, 핵심 family score, estimate status

Evidence는 다음을 분리한다.

- 현재 위치 근거
- 전환 / 지속 근거
- 전망 우위 근거
- 반대 / invalidate 조건

### Section 4. Multi-Horizon Ribbon

최근 60거래일의 overall regime과 transition phase를 연속 ribbon으로 표시한다.
1D / 1W / 1M을 탭으로 분리하는 대신 시간 경로 안에서 `충격 -> 지속 -> 체제`를 읽게 한다.

### Section 5. Asset Pathways

- 주식 위험선호
- 금리 부담
- 달러 압력
- 안전자산 선호
- 원자재 / 물가 압력

각 카드에는 현재 1D / 5D / 20D 상태, 다음 5D / 20D 보조 분포, 바뀌는 조건을 둔다.
개별 자산 가격 목표나 매매 결론은 만들지 않는다.

### Section 6. Method / Historical Episodes

- closest historical episodes
- baseline comparison
- effective sample and overlap handling
- source, continuous futures / roll caveat
- raw tables and legacy validation

기존 `과거 점검` CTA와 metric grid는 제거하고, 패턴 전망이 기본 화면에 바로 나타나게 한다.
무거운 계산은 daily snapshot / cache 경계를 통해 사용자 클릭 없이 준비하는 방향을 우선한다.

## 10. Error And Fallback Behavior

- current pattern 계산 가능, outlook 불가: 현재 경로는 표시하고 horizon card는 `전망 검증 부족`.
- 일부 family missing: partial evidence와 missing family를 표시하고 confidence downgrade.
- 20D history 부족: 1D / 5D current pattern만 보여주고 20D state와 outlook은 unavailable.
- validation exception: today brief를 숨기지 않고 pattern outlook만 isolated unavailable.
- stale latest candle: hero basis에 stale 표시, 확률을 최신처럼 표현하지 않음.
- mixed / low signal: 강제 방향을 만들지 않고 `우위 미확인`과 바뀌는 조건을 보여줌.

## 11. Testing And Acceptance

### Service Tests

- multi-window point-in-time feature values
- persistence / reversal / breadth / conflict state
- historical replay parity
- leakage / purge / episode separation
- baseline probability and lift
- publication gate transitions
- missing / stale / insufficient fallback

### React Contract Tests

- current observation and future probability semantic separation
- VERIFIED / PROVISIONAL / UNAVAILABLE rendering
- no `매수`, `매도`, `승인`, `선정`, `통과` wording
- no diagnostic run / row count as primary content
- current / 5D / 20D horizon order
- path map, evidence, ribbon, asset pathways presence
- responsive behavior at desktop and phone width

### Actual QA

- stored actual snapshot payload inspection
- current pattern state and closest episodes sanity check
- desktop Browser QA
- mobile Browser QA
- screenshot 1장 final attachment
- console errors 0

## 12. Completion Criteria

- 사용자가 첫 화면에서 현재 위험 체제와 전환 단계를 읽는다.
- 1D / 5D / 20D가 별도 변화율 카드가 아니라 하나의 시간 경로로 연결된다.
- 5D / 20D 전망은 baseline과 검증 상태를 함께 제공한다.
- 표본이 부족하거나 우위가 없을 때 확률을 강제로 만들지 않는다.
- 기존 today evidence와 DB-backed source boundary를 보존한다.
- 경제사이클 UI의 hierarchy와 visual grammar를 따르되 시간축과 의미는 분리된다.
- 관련 tests, compile / build, diff check, actual desktop / mobile Browser QA가 통과한다.
