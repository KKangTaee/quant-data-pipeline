# Economic Cycle Forecast Feasibility Design

Status: Draft for user review
Date: 2026-08-11

## 목적

현재 경제사이클 V3의 observed-state와 별도로, 향후 3개월·6개월 시점의 네 국면
확률을 과거 데이터로 신뢰성 있게 계산할 수 있는지 먼저 판정한다. 이 연구가
publication gate를 통과하기 전에는 forecast production model, DB serving schema,
Overview payload 또는 React UI를 만들지 않는다.

이번 연구가 답해야 하는 질문은 하나다.

> forecast origin에서 실제로 알 수 있었던 정보만 사용했을 때, 3개월·6개월 후
> 회복·확장·둔화·위축 확률이 단순 baseline보다 안정적으로 우수하고 보정되어 있는가?

## 승인된 제품 의도

1. 현재 국면은 최신 실물 활동과 고용·소득의 level / momentum으로 별도 진단한다.
2. 미래는 고정 순환 순서가 아니라 모든 destination phase를 비교한다.
3. 예측은 과거 forecast-origin 정보와 이후 실제 outcome의 관계에서 학습한다.
4. 위험과 변화는 검증·보정된 확률로 공개한다.
5. feasibility가 실패하면 forecast 기능 개발을 중단하고 현재 국면 진단만 유지한다.
6. `자산별 확인 포인트`의 계산, payload, 카드 디자인과 순서는 변경하지 않는다.

## 연구 범위

### 포함

- 3개월·6개월 target 정의와 leakage-safe dataset
- strict PIT / known-at feature coverage profile
- baseline과 사전 고정 candidate model 비교
- chronological OOS, calibration, episode support와 stress test
- horizon별 `GO | PARTIAL | NO_GO` 판정과 근거
- 후속 product implementation 착수 여부 결정

### 제외

- 현재 경제사이클 화면, 순환 경로 UI 또는 자산 카드 변경
- production DB schema, loader, service payload와 runtime job 변경
- 모델 결과를 현재 사용자 화면에 노출
- 1개월·2개월 확률 재사용
- 자동 자산배분, 매매 신호 또는 수익률 예측
- dynamic-factor / Markov-switching production 구현

## Target Contract

Forecast origin을 `t`, horizon을 `h ∈ {3, 6}`으로 둔다.

```text
primary target = phase observed at t + h
output = P(S[t+h] = recovery | I[t])
       + P(S[t+h] = expansion | I[t])
       + P(S[t+h] = slowdown | I[t])
       + P(S[t+h] = contraction | I[t])
```

- 네 확률은 유한하고 음수가 아니며 합이 1이어야 한다.
- target phase는 `economic_cycle_observed_state.phase_from_coordinates()`와 같은
  상대 성장순환 정의를 사용한다.
- target은 target origin에서 사용 가능했던 PIT observed state로 만든다. 최신 revised
  history를 primary target으로 사용하지 않는다.
- revised-history phase는 revision stress reference로만 사용한다.
- `현재 국면 이탈 확률`은 `1 - P(S[t+h] = current_phase)`로 파생한다.
- 이번 V1은 `h개월 안에 한 번이라도 전환`하는 path event를 target으로 사용하지 않는다.
- 고정 순환 순서는 UI reference 또는 baseline prior로는 사용할 수 있지만 candidate
  destination을 제한하지 않는다.

## Information-Date Contract

각 forecast origin `t`의 input은 `t`까지 실제로 알려진 정보만 포함한다.

```text
FRED / ALFRED vintage + released_at / realtime interval
stable daily market observations known by observation date
  -> origin-specific transforms
  -> expanding normalization fitted through t only
  -> feature row I[t]
```

- 실물 target family: activity, labor / income 8개 series
- current-state predictors: level, momentum, breadth, duration, recent 1·3·6개월 delta
- leading predictors: real leading, curve/rates, credit, financial conditions,
  inflation/policy family
- revised macro value를 과거 origin에 소급해서 채우지 않는다.
- publication lag가 불명확한 series는 core candidate에서 제외한다.
- daily market series처럼 revision이 없는 series도 target date 이후 observation을 쓰지 않는다.
- 모든 feature에는 source, observation date, known-at date와 transform version을 남긴다.

## Dataset Contracts

두 dataset을 병렬 감사하지만 product candidate는 leakage-safe 조건을 충족해야 한다.

### Dataset A — Strict PIT Core

- ALFRED realtime interval과 release evidence가 있는 series만 사용한다.
- 정확성은 가장 높지만 feature 교집합과 역사 길이가 짧을 수 있다.
- 이 dataset이 sample gate를 통과하면 primary contract로 우선한다.

### Dataset B — PIT Target + Stable Long-History Predictors

- target은 Dataset A와 동일한 PIT observed phase다.
- predictor는 revision이 없거나 known-at 규칙을 재현할 수 있는 장기 market/leading
  series를 추가한다.
- revised macro backfill은 허용하지 않는다.
- Dataset A보다 sample을 늘리되 target authority는 바꾸지 않는다.

Dataset A와 B 모두 sample gate를 통과하지 못하면 즉시 `NO_GO`로 종료한다.

## Pre-Registered Model Approaches

holdout 결과를 본 뒤 새로운 candidate를 추가하지 않는다. 추가 모델은 새 research
version과 새 untouched holdout을 요구한다.

### A. Regularized Multinomial Model

- 네 국면을 직접 예측하는 L2-regularized multinomial logistic model
- 장점: 단순하고 contribution과 probability를 설명하기 쉽다.
- 한계: minority phase와 짧은 episode에 민감하다.

### B. Coordinate Distribution Model — 권장 후보

- 미래 level과 momentum을 regularized regression으로 예측한다.
- development residual distribution으로 네 quadrant probability를 계산한다.
- 장점: continuous target을 사용해 모든 row에서 정보를 얻고 현재 phase 정의와
  좌표 의미가 일치한다.
- 한계: residual distribution과 level / momentum dependence를 검증해야 한다.

### C. Historical Analog

- 거리 기반 유사 시점의 outcome distribution을 계산한다.
- publication candidate가 아니라 explanation benchmark로만 사용한다.
- 독립 episode가 부족하면 확률로 승격하지 않는다.

candidate 선택은 development rolling-origin 결과에서 끝낸다. development log loss가
낮은 모델을 선택하고 차이가 1% 이내면 더 단순한 A를 선택한다. Brier score와
classwise calibration이 이 선택을 반박하면 어느 모델도 선택하지 않는다. 선택된
하나의 candidate와 고정된 hyperparameter·calibration만 locked holdout에서 한 번
평가한다. 선택 모델이 holdout gate를 실패해도 다른 candidate로 교체하지 않는다.

## Baselines

모든 candidate는 동일 origin에서 다음 baseline과 비교한다.

1. expanding unconditional phase frequency
2. current phase와 같은 horizon의 expanding empirical transition distribution
3. current-state persistence를 phase별 historical persistence rate로 smooth한 distribution

candidate는 가장 강한 baseline 하나만이 아니라 세 baseline 모두와 비교한다.

## Validation Design

### Chronological Split

- 가장 최근 25% origin을 locked final holdout으로 두되 48개월보다 짧으면 마지막
  48개월을 사용한다.
- 앞선 75%에서 expanding rolling-origin development validation을 수행한다.
- 각 origin의 training row는 그 row의 target date가 현재 origin 이전인 경우에만
  학습에 포함한다.
- calibration parameter도 development 구간에서만 학습한다.
- locked holdout은 candidate와 threshold가 고정된 뒤 한 번만 평가한다.

### Sample Gate

각 horizon이 아래를 모두 만족해야 한다.

- usable monthly origins: 180개 이상
- development origins: 120개 이상
- locked holdout origins: 48개 이상
- non-overlapping effective origins: 3M은 40개 이상, 6M은 24개 이상
- 전체 OOS target에서 phase별 15건 이상
- locked holdout에서 phase별 5건 이상
- phase별 distinct episode 5개 이상

월별 인접 row는 독립 episode로 세지 않는다. 같은 phase run은 하나의 episode로
묶고, uncertainty는 horizon 길이 이상의 block bootstrap으로 계산한다.

### Probability Gate

각 horizon candidate가 아래를 모두 만족해야 한다.

- 모든 row가 valid probability simplex
- strongest baseline 대비 Brier score 5% 이상 개선
- strongest baseline 대비 log loss 5% 이상 개선
- block bootstrap에서 두 metric 개선 확률 80% 이상
- aggregate ECE 0.10 이하
- classwise ECE 0.15 이하
- holdout macro-F1이 strongest baseline보다 낮지 않음
- probability margin이 큰 구간에서 calibration이 더 나빠지지 않음

### Stress Gate

- COVID 포함 / 제외
- 최근 36개월
- PIT target / revised reference disagreement month 제외
- 한 feature family씩 제거한 dropout test
- origin을 1개월 이동한 boundary sensitivity

candidate가 어느 stress slice에서든 두 proper scoring rule 모두 strongest baseline보다
나쁘면 해당 horizon은 publish하지 않는다.

## Decision Contract

### GO

- 3M과 6M이 모두 sample, probability, stress gate를 통과한다.
- 후속 product forecast 설계로 이동할 수 있다.

### PARTIAL

- 한 horizon만 통과하거나 stress 결과가 불안정하다.
- research 결과만 보존하고 UI와 production runtime은 만들지 않는다.

### NO_GO

- dataset sample gate가 실패하거나 두 horizon 모두 publication gate를 실패한다.
- forecast 개발을 종료하고 현재 observed-state만 유지한다.

`PARTIAL`과 `NO_GO`를 사용자 화면의 `자료 부족` 상태로 만들지 않는다. 이는 제품이
아직 존재하지 않는다는 연구 결론이다.

## Research Outputs

새 active research bundle은 아래 evidence를 소유한다.

```text
.aiworkspace/note/finance/researches/active/2026-08-economic-cycle-forecast-feasibility/
  RESEARCH_PLAN.md
  CURRENT_PROJECT_AUDIT.md
  BENCHMARKS.md
  UI_PATTERNS.md
  FEATURE_CANDIDATES.md
  RECOMMENDATION.md
  SOURCES.md
  RISKS.md
  DATASET_PROFILE.md
  FEASIBILITY_REPORT.md
```

- raw feature panel, prediction row와 bootstrap sample은 generated artifact로 두고
  명시 요청 없이 commit하지 않는다.
- registry, saved setup, run history와 production DB table을 수정하지 않는다.
- current product docs와 Roadmap은 feasibility 결론만으로 변경하지 않는다.

## Verification

- target date와 origin date의 strict ordering test
- revised future row가 origin feature에 들어가지 않는 leakage test
- same-origin rerun fingerprint equality
- baseline/candidate가 exact same target rows를 사용하는 alignment test
- probability simplex와 calibration test
- sample/episode count independently recomputed assertion
- configuration hash와 source coverage report
- research bundle checker

## Stop Conditions

다음 중 하나가 확인되면 모델·UI 구현 없이 중단한다.

- target 자체가 revision으로 지나치게 불안정함
- 3M·6M 중 하나라도 required sample을 확보할 수 없음
- minority phase / episode support 부족
- strongest baseline을 proper scoring rule에서 이기지 못함
- 결과가 COVID 또는 최근 한 구간에 집중됨
- 현재 월마다 필요한 core feature를 materialize할 수 없음

중단 보고서는 실패 metric, 원인, 추가 데이터로 해결 가능한 문제인지 구조적으로
어려운 문제인지를 분리해 기록한다.

## 후속 구현 경계

`GO` 이후에도 바로 UI를 만들지 않는다. 별도 product design에서 아래를 승인받는다.

- primary / alternative / stay probabilities의 정보 구조
- outcome probability와 model reliability의 분리
- 순환 경로 화살표가 분석 결과를 사용하도록 하는 계약
- independently validated reduced model과 dated last-good fallback
- 자산별 확인 포인트 frozen regression

이 후속 설계가 승인된 뒤에만 implementation plan과 production code 변경을 시작한다.
