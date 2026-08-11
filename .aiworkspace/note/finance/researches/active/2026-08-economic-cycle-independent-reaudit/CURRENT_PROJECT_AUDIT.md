# Current Project Audit

Date: 2026-08-11
Evidence status: current HEAD code + read-only DB reproduction + focused tests + git decision trace

## 2026-08-11 Post-V3 Reaudit Conclusion

현재 V3의 `현재 국면` 계산은 정상적으로 materialize되고 있지만, 사용자가 원한
`향후 미래 방향 예측`은 구현되어 있지 않다. 대신 현재 또는 마지막 확인 국면에서
순환 배열의 다음 인접 국면 하나를 골라 조건을 확인하는 deterministic monitor가
들어가 있다.

따라서 이번 문제는 임계값이나 UI copy 하나의 오류가 아니다. 검증을 통과하지 못한
1·2개월 확률을 제거하는 과정에서 원래 제품 목적이던 multi-path forecast까지 함께
제거하고, 이를 fixed next-phase monitor로 대체한 **제품 계약 축소**가 root cause다.

### Intended Versus Actual Contract

| Concern | Intended contract | Current V3 contract | Audit result |
| --- | --- | --- | --- |
| 현재 상태 | 최신 정보로 네 국면 중 현재를 판정 | 8개 실물 series의 level / momentum 사분면 | 구현됨 |
| 미래 방향 | 현재 상태에서 가능한 다른 국면을 과거 데이터로 비교 | 순환 배열의 다음 인접 국면 하나만 선택 | 미구현 |
| 과거 데이터 | 유사 상태와 이후 결과를 학습·검증 | 현재 feature 정규화와 조건 계산에 사용 | forecast 용도로는 미사용 |
| 위험·변화 확률 | 검증·보정된 확률 공개 | 확률 제거, 조건 충족 수 공개 | 미구현 |
| 순환 UI | 분석 결과에 따라 예상 경로를 강조 | `회복→확장→둔화→위축→회복` 고정 | 예측처럼 오해 가능 |

### Where The Goal Changed

1. 기존 Gaussian 1·2개월 모델이 baseline과 calibration gate를 통과하지 못한 것은
   재현 가능한 사실이었다. 미래 확률을 화면에서 제거한 결정 자체는 타당했다.
2. 2026-08-03 V3 설계는 대안 B인 `Observed State + Transition Monitor`를 채택하면서
   target을 `다음 인접 국면`으로 제한했다. 같은 설계에서 probabilistic research는
   out of scope로 명시됐다.
3. 구현은 `PHASE_SEQUENCE`와 `_next_phase()`로 그 제한을 그대로 코드화했다. 과거
   유사 사례, 후보 국면별 likelihood 또는 transition probability는 호출하지 않는다.
4. 2026-08-10 UI 보완은 현재 위축과 과거 회복 앵커의 불일치를 줄였지만,
   `_next_observed_phase()`로 `위축→회복`을 다시 고정했다. 이는 표시 일관성 개선이지
   forecast 복원이 아니었다.
5. canonical product docs도 이 결과를 `Observed State Before Forecast`, 미래 월별
   국면 예측 아님으로 기록했다. 구현·테스트·문서가 모두 같은 축소 계약을 정상
   동작으로 간주한다.

이 과정에서 사용자에게 `확률을 제거한다`와 `향후 방향 비교 기능도 제거한다`가 같은
결정이라는 점이 충분히 드러나지 않았다. 기술적 안전 조치가 제품 목적 변경으로
확장된 것이 요구사항 전달 실패의 핵심이다.

### Current Runtime Reproduction

2026-08-11 read-only DB/service 실행 결과:

- current snapshot: `2026-07-31`, `READY`, real-economy `8/8`
- observed phase: `contraction / 위축`
- level `-0.507`, momentum `-0.159`, confidence `MEDIUM`
- revision sensitivity: `SENSITIVE`
- persisted monitor: anchor `recovery`, target `expansion`, `WATCH 0/3`
- presentation helper: current `contraction → recovery`, `WATCH 0/3`
- freshness: `READY`, refresh scope 없음

데이터가 부족해서 현재 화면이 이렇게 동작하는 것이 아니다. 최신 입력은 준비되어
있고, 고정 인접 경로를 선택하도록 설계돼 있기 때문에 이렇게 동작한다.

### Forecast Evidence Reproduction

현재 DB에는 서로 다른 과거 forecast 시도의 결과가 남아 있으나 모두 publication
gate를 통과하지 못했다.

| Attempt | Evidence | Result |
| --- | --- | --- |
| Gaussian four-phase +1M | 105 OOS origins, accuracy 53.3%, Brier 0.598, log loss 1.316 | `LIMITED`; origin·baseline gate 실패 |
| Gaussian four-phase +2M | 104 OOS origins, accuracy 43.3%, Brier 0.710, log loss 1.706 | historical-transition baseline보다 열위 |
| Overlay four-phase +1M | development 113, holdout 35 | `INSUFFICIENT_EVIDENCE` |
| Overlay four-phase +2M | development 113, holdout 34 | `INSUFFICIENT_EVIDENCE` |
| 3-class direction | holdout improving/weakening support가 각 3~6건 수준 | publication hold / rejected |
| 3M guide direction | non-overlap origin 0, class support 0 | `INSUFFICIENT_DATA` |

월별 row 수는 독립 경기 episode 수가 아니다. 인접 월은 강하게 자기상관되어 있고,
현재 strict PIT forecast feature 교집합은 짧아 네 국면 확률을 안정적으로 보정하기에
부족하다. 현재 데이터로 production probability UI를 바로 다시 만드는 것은 No-Go다.

### Architecture And Handoff Drift

- current UI authority는 `economic_cycle_snapshot` V3지만 DB에는 별도 forecast artifact,
  direction publication state, guide snapshot 테이블이 남아 있다.
- 현행 코드에서 이 세 실험 read path의 소유자가 검색되지 않아 orphaned research
  artifact 상태다.
- 같은 `2026-07-31`에 guide snapshot은 medium cycle을 `expansion`, V3 current는
  `contraction`으로 기록한다. 서로 다른 정의를 같은 경제사이클 결과처럼 재사용하면
  다시 사용자 혼란이 발생한다.
- 경제사이클의 canonical target, training dataset, publication authority를 하나로
  고정하기 전에는 새 UI나 새 확률 카드를 붙이면 안 된다.

### Go / No-Go Assessment

- 현재 국면 진단 유지·개선: **Go**. 실제 데이터와 PIT 경로가 있고 focused tests도
  `106 passed`다.
- 현행 fixed adjacent monitor를 미래 예측으로 계속 표현: **No-Go**.
- 현재 데이터와 기존 모델을 그대로 사용한 네 국면 확률 재공개: **No-Go**.
- 새 target·horizon·dataset으로 제한된 forecast feasibility 연구: **Go**.
- feasibility gate를 통과하기 전에 제품 UI 구현: **No-Go**.

### Mandatory Improvement Guardrails

1. current-state와 forecast를 별도 모델·payload·검증 계약으로 분리한다.
2. forecast는 현재를 제외한 모든 후보 국면을 평가하며 고정 순환 순서를 prior나
   visual reference 이상으로 사용하지 않는다.
3. 특정 1·2개월 점예측 대신 macro horizon을 먼저 확정한다.
4. 모든 feature는 해당 forecast origin에서 실제로 알 수 있었던 값만 사용한다.
5. 확률은 chronological OOS, calibration, baseline skill, class/episode support를 모두
   통과한 경우에만 공개한다.
6. data freshness 문제와 model evidence 부족을 같은 `자료 부족` 상태로 합치지 않는다.
7. runtime resilience는 core model, independently validated reduced model, dated last-good
   result 순으로 설계하되 검증되지 않은 fallback probability를 만들지 않는다.
8. feasibility가 실패하면 forecast UI를 만들지 않고 `현재 국면 진단만 제공 가능`으로
   개발을 중단한다.

## Audit Conclusion

현재 기능은 `현재 상태 진단`과 `미래 국면 확률 예측`을 같은 Gaussian 분류 모델과
확률 좌표에 결합한다. 이 때문에 현재 4분면 정의, 저장된 현재 국면, 그래프 위치가
서로 다른 의미를 갖고, 검증 기준을 통과하지 못한 1·2개월 결과도 잠정 숫자로 계속
노출된다. 작은 임계값 조정만으로 해결할 문제가 아니라 제품 계약을 분리해야 한다.

## Current Product Promise And Surface Role

- Surface: `Research > Market Research > 경제 사이클`
- Role: 사용자 판단을 돕는 research context surface
- Non-goal: NBER 공식 판정, 확정 경기 예측, 투자 승인, 매매 신호
- User value intended: 현재 경기 위치, 변화 방향과 자산별 관찰 조건 파악
- `자산별 확인 포인트`: 경제 상태, 측정된 시장 경로와 실제 가격을 분리하는 현재
  구조가 유용하므로 보존한다.

## Implemented Data Flow

```text
FRED / ALFRED vintage
  -> macro_series_vintage_observation
  -> finance/loaders/economic_cycle.py
  -> finance/economic_cycle_features.py
  -> finance/economic_cycle_labels.py
  -> finance/economic_cycle_model.py / economic_cycle_validation.py
  -> economic_cycle_model_artifact / economic_cycle_snapshot
  -> app/services/overview/economic_cycle.py
  -> EconomicCycleWorkbench.tsx
```

현재 국면용 모델 feature는 `activity_score`, `labor_income_score`와 각 3개월
momentum이다. 미래 모델은 여기에 `financial_leading_score`,
`inflation_policy_score`를 추가한다.

## Reproduced Facts

### 1. 현재 국면 판정식과 표시값이 일치하지 않는다

현재 label 정의는 아래와 같다.

```text
level = 0.5 * activity_score + 0.5 * labor_income_score
momentum = 0.5 * activity_momentum_3m + 0.5 * labor_momentum_3m
```

level / momentum 부호와 USREC override로 네 국면 label을 만든다. 그러나 저장되는
`current_phase`는 이 규칙의 결과가 아니라, 같은 feature로 label을 다시 맞추는 h0
Gaussian 모델의 최빈 국면이다.

2026-06-30 재현:

| Evidence | Value |
| --- | ---: |
| activity score | -0.8180 |
| labor / income score | -0.4378 |
| composite level | -0.6279 |
| composite 3M momentum | -0.2879 |
| rule-defined quadrant | recession |
| stored / displayed dominant phase | recovery, 46.7% |

현재 저장된 historical replay 121개월을 같은 현재 코드의 label 규칙과 대조했을 때
42개월, 34.7%가 불일치했다. h0 OOF 정확도도 69.8%이므로, 결정적으로 생성한 label을
확률모델이 다시 추정하면서 약 30%를 잃는 구조다.

### 2. `침체`라는 이름이 입력값의 경제 의미보다 강하다

level의 0은 경제활동 증가율 0이나 추세 output gap 0이 아니다. 각 변환값을 expanding
median / MAD로 표준화한 뒤 합친 `자기 과거 중앙값`이다. 따라서 level < 0과
momentum < 0은 `평균 이하이며 약화`를 뜻할 수는 있어도 곧바로 broad recession을
뜻하지 않는다.

현행 UI가 이 사분면을 `침체`라고 부르면 정상적인 below-trend slowdown도 공식
침체처럼 읽힌다. 상대 성장순환이라면 `위축/약화`가 더 맞고, NBER recession은
별도 reference overlay여야 한다.

### 3. USREC가 current-state target을 오염시킨다

USREC는 실시간 독립 진단 입력이 아니라 NBER의 후행·수정 판정을 반영한다. 현재
PIT label은 USREC가 1이면 level / momentum과 무관하게 recession으로 덮어쓴다.

실제 저장 vintage 재현:

- 2020-08-31 origin에서 latest USREC 2020-07 값은 1이었다.
- 2021-06-30 origin에서 latest USREC 2021-05 값도 1이었다.
- 2021-07-31 origin에서 NBER trough 발표 뒤 latest USREC 2021-06 값이 0이 됐다.

그 결과 2020-08부터 2021-06의 강한 양(+) level / momentum 일부도 학습 label에서는
recession이다. 현재 h0 모델은 독립 실물 진단이 아니라 NBER 발표 상태를 간접 학습한다.

### 4. h0 coverage gate가 사용하지 않는 미래 입력까지 센다

h0 artifact feature는 네 개의 real-economy aggregate뿐이다. 하지만 validation row의
`complete_feature_ratio`는 catalog의 16개 non-label series 전체에 대한
`overall_coverage`를 사용한다. 금융선행·물가정책 source가 초기 역사에서 없으면 h0도
`LOW_FEATURE_COVERAGE`가 된다.

2026-05-31 학습 artifact의 h0 ratio는 0.7402로 0.75 gate를 소폭 밑돌았지만, 이 값은
h0 입력 전용 coverage가 아니다.

### 5. 공개되지 못한 미래 모델을 제품이 계속 숫자로 보여준다

현재 snapshot model `economic-cycle-v1-59ba078b22ba`의 모든 horizon은 LIMITED다.

| Horizon | Accuracy | Brier | Log loss | Main gate result |
| --- | ---: | ---: | ---: | --- |
| current | 69.8% | 0.445 | 1.090 | coverage, calibration 실패 |
| +1M | 52.9% | 0.597 | 1.317 | origin 부족, baseline log loss 열위 |
| +2M | 43.7% | 0.708 | 1.707 | origin 부족, calibration·baseline 모두 열위 |

+2M historical-transition baseline은 Brier 0.671, log loss 1.223으로 모델보다 모두
좋다. 그럼에도 materialization은 LIMITED artifact를 scoring copy로 바꾸어 확률과
dominant phase를 저장하고, 서비스와 UI는 이를 `잠정 모델 추정`으로 노출한다.

### 6. +2M transition prior는 validation과 serving에서 다르다

rolling validation은 known phase에서 target까지 horizon에 맞게 transition matrix를
여러 번 전개한다. 실제 materialization은 current h0에서 +1M과 +2M 모두 같은 one-step
transition row를 섞는다. +2M은 two-step prior가 필요한데 one-step prior를 사용한다.

### 7. 4분면 그래프가 실제 level / momentum을 그리지 않는다

React의 `probabilityCoordinate()`는 아래처럼 국면 확률을 좌표로 바꾼다.

```text
x = P(expansion) + P(slowdown) - P(recovery) - P(recession)
y = P(recovery) + P(expansion) - P(slowdown) - P(recession)
```

따라서 모델 불확실성이 높을수록 실제 score와 관계없이 중앙으로 수축한다. 이 좌표를
`성장 레벨`, `모멘텀` 축에 표시하는 것은 표현 계약 위반이다. 과거 12개월과 미래
+1M / +2M을 연결한 선도 실제 경제 경로가 아니라 확률분포의 이동이다.

### 8. headline은 더 최신 intramonth 상태를 current로 승격하지 않는다

2026-08-03 DB 기준 canonical current snapshot은 2026-06-30이고, 별도 intramonth
snapshot은 2026-07-31이다. 서비스 headline과 current phase는 계속 6월말 row를 쓰고
7월말 계산은 보조 패널로만 둔다. `현재`라는 사용자 문구와 기준일 의미가 어긋난다.

## Test Contract Gaps

경제사이클 관련 현재 테스트 172개는 모두 통과했다. 이는 regression 안정성을
보이지만 아래 잘못된 의미도 의도된 contract로 고정하고 있다.

- LIMITED horizon의 provisional probabilities를 계속 노출하는 테스트가 있다.
- h0 dominant phase가 `label_phase()` 결과와 일치해야 한다는 테스트가 없다.
- +2M serving prior가 two-step인지 확인하는 테스트가 없다.
- React 테스트는 `probabilityCoordinate` 문자열 존재를 확인할 뿐 실제 factor 좌표를
  검증하지 않는다.
- vintage replay를 final reference와 비교해 false alarm, turning-point delay, revision
  sensitivity를 평가하는 acceptance test가 없다.

## Current Data Correctness Risks

- PIT observation filter 자체는 origin과 realtime interval을 적용한다.
- 다만 label truth와 feature availability가 같은 PIT frame에 묶여 training target의
  경제적 의미가 흐려진다.
- monthly series의 latest available value를 origin 상태로 사용하므로 release lag를
  source별로 설명해야 한다.
- 0 threshold 부근에서 상태가 매달 바뀔 수 있지만 hysteresis, minimum duration,
  breadth gate가 없다.
- 평균 이하 성장과 broad recession, current nowcast와 ex-post chronology가 분리되지
  않는다.

## Implication

현재 문제의 root cause는 임계값 하나가 지나치게 보수적인 것이 아니다. `관측된 현재
상태`, `후행 공식 판정`, `미래 확률`, `그래프 좌표`가 한 모델과 한 phase vocabulary에
섞인 것이 핵심이다. 다음 설계에서는 이 네 책임을 먼저 분리해야 한다.
