# Economic Cycle State And Transition Feasibility Design

**Date:** 2026-08-17

**Status:** User-approved direction; written-spec review pending

**Scope:** 1차 제품 계약, 2차 Point-in-Time 데이터 적합성, 3차 shadow model
검증까지만 수행한다. production persistence, service, React UI와 기존 자산별 확인
포인트 변경은 포함하지 않는다.

## 이걸 하는 이유?

사용자가 원한 경제사이클 기능은 과거에 알 수 있었던 여러 데이터를 바탕으로 현재
국면을 진단하고, 현재 조건이 어떻게 변할 때 다른 국면으로 이동하는지 설명하며,
현재 정보에서 가장 합리적인 주경로와 대안 경로를 확률적으로 비교하는 기능이다.

현행 V3는 현재 8지표로 관측 국면을 계산하지만 미래 방향은 과거 outcome을 비교하지
않고 고정 순환 배열의 인접 국면을 감시한다. 이후 RTDSM 연구는 모든 목적지를 비교하는
방향으로 고쳤지만, 예측 입력을 실물경제 core에 한정해 통화정책·물가·금리·신용·시장
기대라는 원래 전환 메커니즘을 반영하지 못한다.

이번 작업은 UI를 먼저 다시 만드는 작업이 아니다. current state와 transition forecast의
책임을 분리하고, 원래 의도에 맞는 확장 입력이 strict Point-in-Time 역사에서 실제로
예측력을 갖는지 production 변경 전에 증명한다.

## 사용자 질문과 제품 계약

제품은 다음 세 질문에 서로 다른 evidence로 답한다.

1. **현재 어디에 있는가?** — 동행 실물경제로 공식 현재 국면을 진단한다.
2. **전환이 가까워졌는가?** — 다음 세 번의 usable 공식 발표 안에 공식 국면이
   바뀔 확률을 `전환 압력`으로 정의한다. 특정 3개월 뒤 국면 예측이나 countdown이
   아니다.
3. **바뀐다면 어디로 갈 가능성이 높은가?** — 현재 국면 유지와 현재를 제외한 모든
   목적지를 비교하고, 다음 확정 목적지의 조건부 분포를 계산한다.

조건부 안내는 `금리가 오르면 침체` 같은 단일 고정 규칙이 아니다. 예측 원점에서 함께
관측된 성장, 물가, 정책, 금리곡선, 신용과 시장가격 조합이 과거 어떤 결과와 연결됐는지
모델 민감도와 유사 episode로 설명한다.

## 선택한 접근

### 선택: 안정적 현재 국면 + 검증된 전환 driver의 계층형 모델

- RTDSM 4지표로 과거와 현재에 동일한 raw state를 계산한다.
- 동일한 다른 raw phase가 두 번 연속 usable release에서 확인될 때 공식 국면을 바꾼다.
- 공식 국면은 고정 순환 순서를 따르지 않고 모든 destination을 허용한다.
- forecast는 core-only와 core+transition-driver 모델을 나란히 검증한다.
- 확장 모델이 core-only와 strongest naive baseline을 모두 이기지 못하면 원래 의도에
  맞는 확률 모델로 승인하지 않는다.

### 반려: RTDSM-only 전환 모델

현재 국면과 실물 모멘텀은 설명하지만, 같은 금리 상승이 건강한 성장인지 강제 긴축인지
구분할 정보가 없다. 현재 상태 안정화 연구로는 유효하지만 원래 제품 계약 전체를
충족하지 않는다.

### 반려: 모든 지표를 한 모델에 즉시 결합

source별 시작 시점과 release lag가 다른 지표의 완전 교집합만 사용하면 독립 episode가
급감한다. 누락값 대치로 긴 역사를 인위적으로 만들면 look-ahead와 provider-era bias가
생긴다. feature group별 coverage와 검증 모델을 분리한다.

### 반려: 책의 시나리오를 고정 점수표로 구현

금리·금·달러 조합은 맥락을 설명하는 hypothesis이지 보편 법칙이 아니다. 실제 역사
검증을 통과하지 않은 점수를 확률로 변환하지 않는다.

## 용어 계약

| 용어 | 의미 |
| --- | --- |
| raw phase | 해당 발표 시점의 RTDSM level/momentum 사분면 후보 |
| official phase | 동일 후보 2회 연속 확인 후 확정된 제품 국면 |
| 위축 | 상대 성장순환의 낮은 level·약한 momentum 상태 |
| 침체 위험 | NBER recession 또는 별도 recession-risk 모델의 위험; 위축과 동일하지 않음 |
| candidate 1/2 | 공식 국면과 다른 raw phase가 처음 관측된 미확정 후보 |
| 전환 압력 | 다음 3 usable 공식 발표 안의 official phase change 확률 |
| 다음 목적지 | 시간과 무관하게 다음에 확정되는 official phase |
| 주경로 | 검증된 조건부 목적지 분포에서 가장 높은 비현재 목적지 |
| 대안 경로 | 주경로 외의 비현재 목적지와 현재 유지 가능성 |

## 1차 — 제품·모델 계약 확정

### 현재 국면

Canonical raw state는 Philadelphia Fed RTDSM의 다음 네 real-time series를 사용한다.

- `IPT`: industrial production
- `H`: average weekly hours
- `EMPLOY`: payroll employment
- `RUC`: unemployment rate

각 forecast origin에서 당시 vintage만 사용해 expanding robust scale, 3-release level,
3-release momentum을 계산한다. raw quadrant는 진단 evidence이고 official phase는
2-release confirmation state machine이 소유한다. 전환을 첫 후보 시점으로 소급하지
않고 missing release는 candidate streak를 끊는다.

초기 official phase도 raw phase 한 번으로 설정하지 않는다. 최초 usable raw phase와
다음 usable release의 raw phase가 같을 때 두 번째 release에서 bootstrap하고, 그전에는
official phase를 `UNAVAILABLE`로 둔다.

현행 8개 실물지표는 production 화면의 breadth/corroboration evidence로 유지한다.
RTDSM official phase와 동일 label을 억지로 만들거나 RTDSM training target을 다시
정의하지 않는다. 두 체계의 불일치는 현재 국면 신뢰도 evidence로 기록한다.

### Forecast target

두 개의 target을 별도로 학습한다.

```text
pressure_target = official phase가 다음 3 usable release 안에 바뀌면 1
destination_target = 다음 confirmed transition의 destination phase
```

destination은 `recovery / expansion / slowdown / contraction` 전체를 허용한다.
현재 phase를 제외한 목적지 확률은 transition 조건부로 합이 1이 되며, 현재 유지
가능성은 pressure의 보완 확률로 따로 표시한다.

### Forecast feature groups

모든 값은 `known_at <= forecast_origin`을 만족해야 한다.

#### A. State core — required

- RTDSM `IPT/H/EMPLOY/RUC` robust z-score
- activity/labor score, level, momentum
- 1/3/6-release 변화
- positive breadth와 activity-labor dispersion
- official phase, duration, raw/official disagreement, candidate destination/streak

#### B. Policy and inflation — extended model

- `FEDFUNDS`: 현재 정책금리와 1/3/6개월 변화
- `DGS2`: 정책 기대와 1/3/6개월 변화
- `DFII10`: 실질금리 수준과 변화
- `PCEPILFE`: core PCE momentum과 2% 괴리
- `T10YIE`: 기대인플레이션 수준과 변화

#### C. Growth expectations and credit — extended model

- `DGS10`: 성장·인플레이션 기대 수준과 변화
- `T10Y2Y` 또는 source overlap이 더 긴 `T10Y3M`: curve level과 변화
- `BAMLH0A0HYM2`: high-yield OAS 수준과 변화
- `ANFCI`: 금융여건 수준과 변화
- `PERMIT`: 주택 선행 모멘텀

#### D. Market interpretation — optional shadow block

- `^GSPC`: 1/3/6개월 return과 drawdown
- `VIXCLS`: 수준과 변화
- `GC=F`: 금 1/3/6개월 return
- `DX-Y.NYB`: 달러 1/3/6개월 return

시장가격은 observation timestamp가 forecast origin보다 늦지 않은 저장 가격만 사용한다.
continuous futures의 장기 contract quality와 DB coverage가 acceptance를 통과하지 못하면
primary probability 모델에서 제외하고 shadow ablation evidence로만 남긴다.

#### E. Fiscal policy — feasibility gap

현재 승인된 장기 monthly Point-in-Time fiscal impulse source가 없다. 정부지출이나 정책
발표를 임의 binary flag로 만들지 않는다. 2차 audit는 기존 DB에서 재현 가능한
government expenditure/transfer series와 release timestamp를 조사해 아래 중 하나로
판정한다.

- `ELIGIBLE`: 현재 승인 source와 storage로 chronological PIT 재구성 가능
- `SHADOW_ONLY`: current interpretation에는 쓸 수 있지만 장기 학습에는 부적합
- `NOT_TESTABLE`: 별도 provider/source 승인 전 수치 모델에 사용할 수 없음

이번 1~3차는 새로운 fiscal provider나 DB schema를 추가하지 않는다.

## 2차 — Point-in-Time 데이터 적합성

### 감사 단위

각 series와 feature group은 다음 정보를 보고한다.

- first/last observation and known-at origin
- usable monthly origins
- missing month share와 longest gap
- release lag and revision policy
- state episode와 겹치는 독립 transition 수
- 전체/최근 25% destination support
- core와 결합했을 때 남는 usable origin과 episode 수

### 데이터 판정

| 판정 | 조건 |
| --- | --- |
| `CORE_READY` | confirmed state gate 전체 통과 |
| `DRIVER_READY` | extended required group의 usable origins >= 180, independent transitions >= 48, destination별 전체 >= 8, holdout destination별 >= 2 |
| `SHADOW_ONLY` | current 값은 사용 가능하지만 위 support 또는 known-at contract 실패 |
| `UNUSABLE` | source timing을 재현할 수 없거나 leakage 없이 monthly feature를 만들 수 없음 |

feature group 일부가 늦게 시작한다고 core history를 버리지 않는다. core-only와 extended
모델은 각자의 eligible origin에서 독립 검증하고, 같은 공통 origin에서도 paired metric을
추가 계산한다.

### 상태 안정성 gate

- 2-release invariant와 no-backdating invariant 100%
- usable origins >= 180
- confirmed transitions >= 48
- phase occupancy each 8%~50%
- three-release revised history와 exact agreement >= 60%
- level-side agreement >= 80%
- NBER recession month의 recovery/contraction side >= 65%
- NBER peak/trough window capture each >= 70%
- destination별 전체 support >= 8, 최근 25% holdout support >= 2

raw one-month episode 27.12%는 diagnostic으로 보존한다. official confirmed state에는
최소 2 usable release invariant가 있으므로 raw one-month share를 사후 완화하지 않는다.

## 3차 — Shadow forecast 검증

### 모델군

동일 target에 아래 모델을 비교한다.

1. global transition rate / phase duration hazard baseline
2. fixed-cycle and historical destination-frequency baseline
3. RTDSM core-only pressure/destination model
4. core + policy/inflation + growth/credit extended model
5. market interpretation block을 더한 optional shadow model

모델은 현재 구현된 deterministic NumPy regularized binary/multinomial logistic contract를
재사용한다. 새 복잡한 ML library, hidden-state model과 결과를 본 뒤의 feature search를
추가하지 않는다.

### Chronological validation

- complete future episode를 holdout한다.
- target known-at이 scoring episode 이전인 row만 training에 사용한다.
- regularization은 이전 training episode에서만 선택한다.
- calibration은 이전 OOF prediction만 사용한다.
- 한 episode의 월별 row가 표본 수를 부풀리지 않도록 episode weight를 적용한다.
- 전체 expanding OOS와 마지막 25% episode holdout을 모두 보고한다.

### Publication-quality gate

확률 모델의 4·5차 제품화 후보가 되려면 다음을 모두 통과해야 한다.

- pressure와 destination의 Brier/log loss가 각각 strongest naive baseline보다 2% 이상 개선
- pressure ECE <= 0.10
- destination ECE <= 0.12
- 모든 확률이 finite이며 simplex invariant 충족
- required class/episode support 충족
- extended model이 paired common-origin에서 core-only보다 Brier 또는 log loss 하나만
  좋아지는 것이 아니라 두 metric의 평균 skill을 개선
- latest holdout에서 한 destination도 evaluation support 0이 아님

### 최종 판정

| 판정 | 의미 | 4·5차 허용 범위 |
| --- | --- | --- |
| `GO` | confirmed state와 extended pressure/destination 모두 통과 | 확률 기반 주경로·대안 경로 제품화 검토 가능 |
| `LIMITED_GO` | confirmed state는 통과했으나 destination 또는 pressure 한쪽만 통과 | 통과한 확률만 제품화 후보; 나머지는 정성 evidence이며 별도 사용자 승인 필요 |
| `NO_GO` | state 또는 확장 forecast 핵심 gate 실패 | production probability/service/UI 구현 중단 |

core-only가 통과하고 extended model이 통과하지 못하면 원래 제품 의도를 충족한 `GO`로
간주하지 않는다. 이는 실물 모멘텀만으로 정책·금리·시장 해석을 대신하지 않기 위함이다.

## 조건부 시나리오 연구 출력

3차 결과는 UI copy를 생성하지 않는다. 검증 report에 다음 evidence만 기록한다.

- 현재 official phase와 candidate 1/2
- current transition pressure와 calibrated status
- 목적지별 조건부 확률과 support
- feature group ablation
- historically nearest complete episodes와 이후 destination
- 주경로를 강화하거나 약화한 driver group의 model sensitivity
- current input coverage, source cutoff와 stale status

`금리 상승이 침체를 유발한다` 같은 인과 문구를 생성하지 않는다. 설명은
`과거 유사 조건에서 해당 경로와 연관됐다`는 범위를 넘지 않는다.

## 운영 안정성 계약

- 1~3차 experiment는 read-only이며 production table writer를 받지 않는다.
- provider fetch, DB write, artifact materialization과 UI payload 변경을 하지 않는다.
- actual experiment 결과를 본 뒤 threshold, confirmation count, feature group을 변경하지
  않는다.
- optional source가 실패해도 core state audit는 실행되며 source failure와 model No-Go를
  구분한다.
- missing feature를 0이나 최신 revised 값으로 대치하지 않는다.
- last-good probability나 heuristic fallback은 4차 설계 전에는 만들지 않는다.

## 변경 경계

1~3차에서 변경 가능한 범위:

- `finance/economic_cycle_*` research-only state/dataset/validation/experiment module
- `finance/loaders/`의 read-only composition helper가 필요한 경우
- focused tests
- active task/research evidence와 canonical roadmap/status 문서

이번 범위에서 금지:

- `economic_cycle_snapshot` production write
- Overview service payload와 React component 변경
- route UI, headline, copy와 CSS 변경
- manual refresh/Data Freshness 동작 변경
- `자산별 확인 포인트` 계산, loader, service payload, markup, label, CSS 변경
- 신규 provider 또는 DB schema 추가

## 완료 조건

1. phase 1 contract와 exact feature/target/gate가 문서와 tests에 고정된다.
2. phase 2 actual DB coverage report가 모든 feature group과 fiscal gap을 판정한다.
3. confirmed-state gate의 actual 결과가 기록된다.
4. state READY일 때만 phase 3 model fitting이 실행된다.
5. extended input support가 부족하면 model metric을 만들지 않고 원인을 series/group
   단위로 기록한다.
6. model이 실행되면 baseline, core-only, extended, optional shadow의 OOS metrics와
   paired common-origin 비교를 기록한다.
7. 최종 `GO / LIMITED_GO / NO_GO`와 4·5차 허용 범위를 하나의 read-only report로
   반환한다.
8. focused tests, full economic-cycle regression, `git diff --check`가 통과한다.
9. production snapshot/service/React와 자산별 확인 포인트 diff가 없음을 확인한다.
