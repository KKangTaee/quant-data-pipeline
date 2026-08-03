# Economic Cycle Observed State / Transition V1 Design

Status: User-approved
Last Updated: 2026-08-03

## Approved Product Contract

사용자가 첫 화면에서 답을 얻어야 하는 질문은 세 가지다.

1. 현재 상대 성장순환의 어느 국면인가?
2. 최근 1·3·6개월에 무엇이 달라졌는가?
3. 어떤 실물 조건이 이어지면 다음 국면 전환을 확인하는가?

현재/+1개월/+2개월 국면 확률과 미래 좌표는 제거한다. 현재 상태는 실물지표로 직접
계산하고, 미래는 특정 월의 예측이 아니라 조건부 전환 감시로 표현한다.

Phase vocabulary는 `회복 / 확장 / 둔화 / 위축`이다. `위축`은 자기 과거 기준보다
경제활동 수준이 낮고 변화 속도도 약한 상대 성장순환 국면이며 NBER 공식 침체와
같지 않다. NBER chronology는 별도 historical reference로만 사용한다.

## Considered Approaches

### A. 기존 모델 수리

h0 일관성과 +2M prior만 고치고 확률 UI를 유지한다. 변경량은 작지만 검증 미달 미래
확률과 사용자 목적의 불일치를 남기므로 채택하지 않는다.

### B. Observed State + Transition Monitor

실제 level / momentum / breadth / duration으로 현재를 진단하고, 미래 확률을 조건부
전환 상태로 교체한다. 현재 상태와 다음 확인 행동이 직접 연결되어 채택한다.

### C. Dynamic Factor / Markov Shadow Model

mixed-frequency latent state를 추정하는 장기 연구안이다. 구현·검증 비용과 확률 중심
화면으로 회귀할 위험이 있어 이번 제품 범위에서는 shadow research로만 남긴다.

## Reproduced Basis For Formula Choice

동일 PIT monthly panel에서 후보를 비교한 결과는 다음과 같다.

| Candidate | Transitions | One-month flipbacks | Median run |
| --- | ---: | ---: | ---: |
| raw monthly quadrant | 345 | 82 | 1 month |
| 3M-smoothed quadrant | 249 | 32 | 3 months |
| 3M-smoothed + two-release confirmation | 168 | 0 | 4 months |
| 6M-smoothed quadrant | 167 | 13 | 4 months |

6개월 평균은 revision agreement가 더 높지만 전환 반응을 추가로 늦춘다. 사용자가
지적한 과도한 보수성을 반복하지 않도록 3개월 평균 좌표를 사용하고 persistence는
전환 상태에서 별도로 확인한다.

## Domain Boundary

신규 `finance/economic_cycle_observed_state.py`가 observed-state 계산의 단일 authority가
된다. 이 모듈은 feature panel을 입력으로 받고 UI copy나 DB access를 소유하지 않는다.

책임은 아래처럼 분리한다.

```text
PIT feature panel
  -> observed-state domain
       - actual level / momentum
       - quadrant / breadth / duration
       - recent 1 / 3 / 6 month changes
       - transition conditions
       - revision-sensitivity comparison
  -> snapshot persistence
  -> overview service read model
  -> React presentation
```

Gaussian horizon artifacts는 shadow validation 호환을 위해 저장할 수 있지만 product
read model과 기본 화면에는 확률·dominant future phase를 전달하지 않는다.

## Current Observed-State Formula

각 월 `t`에서 existing PIT robust-z factor를 사용한다.

```text
raw_level_t = 0.5 * activity_score_t + 0.5 * labor_income_score_t
level_t = mean(raw_level_t, raw_level_t-1, raw_level_t-2)
momentum_t = level_t - level_t-3
```

`momentum_t`는 최근 3개월 평균과 그 직전 3개월 평균의 차이다. 모든 항은 해당
forecast origin에서 알 수 있었던 vintage만 사용한다.

Quadrant mapping은 deterministic하다.

| Level | Momentum | Phase |
| --- | --- | --- |
| `< 0` | `>= 0` | recovery |
| `>= 0` | `>= 0` | expansion |
| `>= 0` | `< 0` | slowdown |
| `< 0` | `< 0` | contraction |

headline phase, persisted `current_phase`, cycle-map current point는 이 동일 계산 결과를
사용한다. h0 probability argmax가 현재 국면을 덮어쓰지 않는다.

현재 관측 국면과 전환 확인은 같은 값이 아니다. `observed_phase`는 위 좌표가 경계를
넘는 즉시 바뀌며 headline과 graph의 현재점을 소유한다. `transition_anchor_phase`는
마지막으로 조건이 모두 확인된 국면이며, 새 관측 국면의 지속성을 검사하는 기준점이다.
따라서 첫 경계 통과 월에는 headline이 새 관측 국면을 즉시 보여주면서 transition
card는 `이전 확인 국면 -> 새 관측 국면 · 확인 진행 중`으로 표시할 수 있다.

## Breadth And Data Eligibility

실물 universe는 activity 4개(`INDPRO`, `W875RX1`, `RRSFS`, `CFNAI`), labor / income
4개(`PAYEMS`, `UNRATE`, `ICSA`, `AWHMAN`)로 총 8개다. 기존 feature transform과
direction normalization을 거친 robust score를 그대로 사용한다.

```text
level_breadth_t = count(z_i,t > 0) / available real-economy series
momentum_breadth_t = count(z_i,t - z_i,t-3 > 0) / available real-economy series
```

- 8개가 fresh하면 data status는 `READY`다.
- 6~7개가 가능하거나 하나 이상 stale이면 좌표는 계산하되 `LIMITED`다.
- 6개 미만이거나 activity / labor factor 중 하나가 없으면 phase는 `UNAVAILABLE`이다.
- unavailable month는 persistence streak를 진행하지 않고 candidate streak를 끊는다.
- breadth가 `>= 0.60`이면 positive diffusion, `<= 0.40`이면 negative diffusion,
  그 사이는 mixed다.

h0 coverage는 forecast-only 또는 inflation-policy series를 포함하지 않고 위 8개만
평가한다.

## Revision Sensitivity And Confidence

현재 phase authority는 PIT-origin track이다. 같은 기준일에 최신 저장 관측치로 다시
구성한 revised-history panel에 동일 공식을 적용해 robustness reference를 만든다.
reference panel도 해당 기준일 이후의 관측치를 사용하지 않으며, 현재 phase를 바꾸지
않는 진단값이다.

- 두 track의 quadrant가 같으면 `revision_sensitivity = STABLE`이다.
- quadrant가 다르면 `revision_sensitivity = SENSITIVE`이며 current point에 boundary
  halo를 표시한다.
- confidence `HIGH`는 READY, STABLE, 동일 quadrant 2회 이상 지속, level과 momentum
  breadth가 해당 축의 부호를 모두 지지할 때만 사용한다.
- phase는 계산 가능하지만 HIGH 조건 중 하나라도 빠지면 `MEDIUM`이다.
- data status가 LIMITED 또는 UNAVAILABLE이면 confidence도 `LIMITED`다.

confidence는 국면 확률이 아니며 UI에서 percentage로 변환하지 않는다.

## Recent Change Contract

최근 변화는 smoothed phase coordinate가 아니라 각 실물 component의 당시 raw score
변화로 계산해 최신 움직임을 감지한다.

각 `h in {1, 3, 6}`에 대해:

```text
composite_delta_h = raw_level_t - raw_level_t-h
breadth_h = count(z_i,t - z_i,t-h > 0) / available pairs
```

- `composite_delta_h > 0`이고 breadth `>= 0.60`: `STRENGTHENING`
- `composite_delta_h < 0`이고 breadth `<= 0.40`: `WEAKENING`
- 그 외: `MIXED`
- paired series가 6개 미만이면 `UNAVAILABLE`

1개월은 최신 변화 감지, 3개월은 방향 확인, 6개월은 현재 국면의 배경이라는 UI
역할을 갖는다. activity와 labor / income 기여를 함께 저장해 서비스가 실제로 변한
요인을 설명하고 임의 narrative를 만들지 않게 한다.

## Transition Monitor Contract

다음 target은 마지막 확인 국면의 relative growth-cycle 인접 국면으로 제한한다.

```text
recovery -> expansion -> slowdown -> contraction -> recovery
```

각 전환은 persistence, diffusion, corroboration 세 조건을 가진다.

| Current -> Target | Persistence | Diffusion | Corroboration |
| --- | --- | --- | --- |
| contraction -> recovery | momentum `>= 0` two consecutive months | momentum breadth `>= 0.60` | activity and labor momentum both `>= 0` |
| recovery -> expansion | level `>= 0` two consecutive months | level breadth `>= 0.60` | smoothed activity and labor levels both `>= 0` |
| expansion -> slowdown | momentum `< 0` two consecutive months | momentum breadth `<= 0.40` | activity and labor momentum both `< 0` |
| slowdown -> contraction | level `< 0` two consecutive months | level breadth `<= 0.40` | smoothed activity and labor levels both `< 0` |

상태는 세 개만 공개한다.

- `MAINTAIN`: 충족된 condition이 0개이고 observed phase가 anchor와 같다.
- `WATCH`: 1~2개가 충족됐거나 observed phase가 anchor와 다르다. UI에 `N / 3`을
  표시하며 첫 경계 통과 시에는 `0 / 3`도 가능하다.
- `CONFIRMED`: 세 조건이 모두 충족됐다.

상태 machine은 다음 계약을 따른다.

- 최초 valid month는 `transition_anchor_phase = observed_phase`, `MAINTAIN`으로
  초기화하며 과거 전환을 추정하지 않는다.
- target은 anchor의 다음 인접 국면이다. 조건이 1개 이상 충족되면 active candidate를
  열고, observed coordinate가 target quadrant로 먼저 이동해도 candidate를 유지한다.
- headline과 persisted `current_phase`는 항상 즉시 계산된 `observed_phase`다. 첫 경계
  통과를 확정 전환처럼 표현하지 않고 confidence와 transition progress를 함께 표시한다.
- 세 조건이 충족된 release는 기존 anchor / target과 `CONFIRMED`를 기록하고, 다음
  valid release부터 anchor를 confirmed target으로 승격해 다음 인접 국면을 감시한다.
- candidate 조건이 모두 사라지고 observed phase도 anchor로 돌아오면 anchor는 유지하고
  상태를 `MAINTAIN`으로 되돌린다. observed phase가 다르면 `WATCH`를 유지한다.
- observed phase가 anchor에서 두 칸 이상 이동하는 shock가 발생해도 anchor를 건너뛰지
  않는다. `non_adjacent_observation = true`를 표시하고 가장 가까운 인접 전환부터
  순차 확인한다.
- unavailable month는 persistence streak를 끊지만 마지막 confirmed anchor는 유지한다.

`transition_monitor_json`은 최소한 `observed_phase`, `anchor_phase`, `target_phase`,
`status`, `conditions_met`, `conditions_total`, `candidate_started_at`,
`confirmed_at`, `non_adjacent_observation`, condition records를 저장한다. historical
replay와 current materialization은 월 순서대로 같은 state machine을 실행해야 한다.

금융·선행·신용·물가·정책 요인은 support / burden / mixed context로 표시하지만 위
세 조건 수에 포함하지 않고 current phase도 변경하지 않는다.

## Intramonth Contract

- headline authority는 최신 비교 가능한 정식 month-end snapshot이다.
- intramonth snapshot은 baseline month-end 대비 raw level, factor와 recent-change
  delta만 보여준다.
- intramonth state는 항상 provisional이며 정식 headline phase를 교체하지 않는다.
- 8개 실물 series 중 6개 미만이면 intramonth coordinate도 표시하지 않는다.
- 다음 정식 month-end materialization에서만 persistence count를 진행한다.

## Persistence Contract

`economic_cycle_snapshot`에 아래 nullable JSON fields를 추가한다.

- `observed_state_json`: level, momentum, phase, breadth, duration, confidence,
  revision sensitivity와 data status
- `recent_changes_json`: 1·3·6개월 change records
- `transition_monitor_json`: observed / anchor / target phase, status, condition records와
  context

기존 `current_phase` ENUM에는 backward compatibility를 위해 `recession`을 남기고
`contraction`을 추가한다. 신규 observed-state row는 `recession`을 쓰지 않는다.
`probabilities_json`과 `forecast_path_json`은 shadow model / old-row compatibility를
위해 저장하되 product read model에서 사용하지 않는다.

historical replay는 세 신규 JSON을 origin-specific 값으로 backfill한다. 신규 JSON이
없는 legacy row를 읽을 때 service는 probability로 상태를 복원하지 않고 상단을
`새 국면 계산 필요`로 제한하며, 독립적으로 구성 가능한 자산 영역은 계속 제공한다.

## Service Payload V3

정상 payload는 아래 top-level contract를 사용한다.

```text
schema_version: economic_cycle_v3
headline
observed_state
recent_changes[1M, 3M, 6M]
transition_monitor
cycle_map.points
intramonth_change
data_freshness
evidence
market_implications
sources
limitations
```

제거되는 product fields:

- `horizons`
- forecast probabilities / confidence percentages
- `cycle_clock.forecast_markers`
- expected +1M / +2M phase

`market_implications` subtree는 같은 입력에서 v2와 deep-equal해야 한다.
V3 service도 현재와 동일한 evidence, market rows, price rows, earnings와 기준일을 asset
builder에 전달한다. builder가 phase horizons를 사용하지 않는 현재 계약을 유지하며,
V3 payload에서 제거되는 horizons 때문에 asset 입력이 달라지지 않게 한다.

## UI Contract

첫 화면 순서는 다음과 같다.

1. 현재 phase, 기준일, confidence label과 짧은 설명
2. actual cycle map + 최근 1·3·6개월 관측 변화
3. 현재 국면 유지 근거 + 다음 인접 국면 전환 조건
4. 전환을 지원하거나 제약하는 금융·선행·물가·정책 context
5. 기존 `자산별 확인 포인트`
6. 접힌 방법론·data limitations

Cycle map:

- x는 actual `level`, y는 actual `momentum`이다.
- display domain은 두 축 모두 `[-2, 2]`로 고정하고 초과값만 edge에 clamp한다.
- 최근 12개월 actual path를 그리고 6개월 전, 3개월 전, 현재만 label한다.
- future terminal point와 probability-derived coordinate를 그리지 않는다.
- WATCH일 때만 현재점에서 target quadrant 방향의 dashed pressure arrow를 표시하고
  `예측 경로가 아님`을 명시한다.
- revision-sensitive current point에는 halo를 표시한다.

Freshness는 기존 compact bar와 explicit refresh action을 유지한다. run count, saved
rows 또는 job diagnostic panel을 새로 추가하지 않는다.

## Frozen Asset Checkpoint Contract

사용자 결정: `자산별 확인 포인트는 지금 디자인 그대로 유지`.

구현 중 아래 항목을 변경하지 않는다.

- `finance/economic_cycle_asset_pathways.py`
- `finance/economic_cycle_interpretation.py`의 asset context logic
- `MarketImplicationCard`, commodity sub-card와 그 하위 presentation component
- asset grid의 2-column desktop / 1-column phone layout
- 채권·금리, 주식, 금, 달러, 원자재 순서
- 공통 경제 배경, 현재 움직임, 함께 관찰된 경로, 현재 해석, 다음 확인 조건
- price return, coverage와 data limitation 표시

새 v3 service는 현재 `build_market_implications()`가 horizons 인자를 사용하지 않는
계약을 유지하고 빈 호환 인자를 전달한다. evidence, market rows, price rows, earnings,
economic / price 기준일은 기존과 동일하게 전달한다. observed-state vocabulary를
자산별 추천 문구로 변환하지 않는다.

## Error And Edge Handling

- snapshot 없음 / DB read 실패: 기존 stable empty state를 유지한다.
- observed-state JSON 없음: 상단은 limited, 자산 subtree는 가능한 범위에서 표시한다.
- recent window 일부 없음: 없는 기간만 unavailable로 표시하고 0으로 만들지 않는다.
- stale / partial source: phase percentage를 만들지 않고 data limitation을 표시한다.
- intramonth source 부족: 기준 month-end 상태만 유지한다.
- transition condition source 부족: 해당 condition은 unmet이 아니라 unavailable이다.
- NBER recession과 observed quadrant가 다르면 둘을 병렬 표시하고 override하지 않는다.

## Test Contract

### Domain

- 4개 quadrant와 zero-tie mapping을 검증한다.
- 3개월 평균과 non-overlapping prior 3개월 momentum을 검증한다.
- real-economy 8개 전용 coverage / breadth를 검증한다.
- unavailable month가 transition streak를 끊는지 검증한다.
- 두 번의 comparable month가 없으면 persistence condition이 충족되지 않는다.
- 첫 경계 통과에서 observed phase는 즉시 바뀌지만 anchor는 유지되고 WATCH가 되는지
  검증한다.
- 세 조건이 충족된 release 다음 valid release에서만 anchor가 target으로 승격되는지
  검증한다.
- non-adjacent observation이 anchor를 건너뛰지 않는지 검증한다.
- revision reference가 phase를 바꾸지 않고 confidence만 제한한다.

### Persistence / Loader

- 신규 JSON field의 schema sync, UPSERT와 round-trip을 검증한다.
- `contraction` write와 legacy `recession` read compatibility를 검증한다.
- historical replay row마다 origin-specific actual coordinates가 저장되는지 검증한다.

### Service

- headline phase와 observed-state phase가 항상 같다.
- `horizons`와 미래 probabilities가 v3 payload에 없다.
- legacy row는 probability를 current state로 승격하지 않는다.
- same-input `market_implications`가 기존 service output과 deep-equal하다.

### React

- probability cards, +1M / +2M marker, future ribbon과 `probabilityCoordinate`가 없다.
- actual level / momentum으로 graph point를 계산한다.
- transition status와 `N / 3` conditions를 표시한다.
- intramonth toggle은 monthly headline을 교체하지 않는다.
- `MarketImplicationCard` 이하 asset markup과 CSS contract가 동일하다.

### Historical Acceptance

- PIT replay에서 current phase / plotted quadrant mismatch는 0이다.
- two-release transition-confirmed phase sequence에서 one-month flipback은 0이다.
- current algorithm과 기존 raw monthly rule의 transition / flipback / duration을 함께
  report해 안정성 개선을 숨기지 않는다.
- NBER peak / trough와의 delay는 참고 지표로 report하며 pass/fail truth로 쓰지 않는다.
- revision-sensitive row 비율과 PIT vs revised quadrant matrix를 report한다.

### Browser QA

- desktop, 760px, 420px에서 horizontal overflow가 0이다.
- current map, recent change, transition conditions가 첫 asset section 전에 읽힌다.
- future probability / future point가 보이지 않는다.
- 자산별 확인 포인트의 기존 카드 구조와 2열/1열 responsive layout이 유지된다.
- 최종 QA screenshot 1장을 생성하되 generated artifact로 commit하지 않는다.

## Documentation Impact

구현 뒤 실제 product contract와 storage ownership이 바뀌므로 다음 canonical docs를
검토한다.

- `docs/PRODUCT_DIRECTION.md`: 확률 공개 대신 observed-state / condition monitor 원칙
- `docs/PROJECT_MAP.md`: observed-state domain / snapshot ownership
- `docs/ROADMAP.md`: 승인 범위와 완료 상태
- focused economic-cycle flow / data docs가 있으면 v3 contract 반영

작업 과정과 검증 결과는 이 active task가 소유한다.
