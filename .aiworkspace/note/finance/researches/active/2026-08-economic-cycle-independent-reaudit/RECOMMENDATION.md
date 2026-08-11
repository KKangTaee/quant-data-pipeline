# Recommendation

Status: user decision required
Last Updated: 2026-08-11

## Recommended Direction

현재 observed-state는 유지하되, fixed adjacent transition monitor를 미래 예측 기능으로
간주하지 않는다. 다음 작업은 UI 개편이 아니라 **bounded forecast feasibility gate**로
제한한다. 이 gate가 통과할 때만 multi-path probability forecast를 별도 계층으로
구현한다.

## Decision Scope

- Immediate next build: production build 없음. forecast target·horizon·PIT dataset의
  feasibility 연구와 go/no-go report만 수행.
- Needs human approval before execution: macro horizon, probability의 event 의미,
  pre-registered publication gate.
- Longer roadmap option: current state + calibrated multi-path forecast + resilient fallback.
- Not approved / parking lot: 1·2개월 확률 복구, fixed adjacent path의 forecast 표현,
  복잡한 Markov/dynamic-factor production deployment.

## Why This Direction

- 현재 데이터 freshness는 READY이며 current-state layer는 작동한다.
- 미래 기능 실패 원인은 단순 source 부족이 아니라 짧은 독립 표본, class imbalance,
  baseline 열위와 calibration 실패다.
- 과거에는 모델·schema·UI를 먼저 만든 뒤 마지막 gate에서 결과를 숨기는 순서가
  반복됐다. 이번에는 순서를 반대로 해야 한다.
- OECD CLI도 특정 point forecast보다 turning point의 early signal과 lead consistency를
  강조한다. 현재 제품의 macro 목적에는 exact +1M/+2M보다 broader horizon이 맞다.

## What To Build First

`Forecast Feasibility Report V1` 한 개만 만든다.

1. current phase target과 forecast outcome을 분리한다.
2. 후보 horizon을 사전에 고정한다.
3. 현재를 제외한 모든 destination phase와 `현재 유지`를 평가한다.
4. stable long-history predictors와 strict PIT predictors의 두 dataset contract를 비교한다.
5. simple baselines, regularized candidate와 historical analog를 동일 walk-forward에서
   평가한다.
6. probability calibration과 independent episode support를 함께 검사한다.
7. 통과/실패를 숫자와 reason code로 결론 내린다.

## Feasibility Stop Gate

아래 중 하나라도 충족하지 못하면 product forecast 개발을 시작하지 않는다.

- target과 horizon별 class/transition support가 사전 최소 기준을 충족
- forecast-origin leakage와 revised-data leakage가 없음
- repeated chronological OOS에서 persistence와 historical-transition baseline보다
  Brier score와 log loss가 모두 개선
- aggregate뿐 아니라 class별 calibration이 허용 범위 안에 있음
- COVID 포함/제외, 최근 구간, revision stress에서 결론이 뒤집히지 않음
- 실제 현재 input으로 매월 materialize 가능한 core feature coverage 확보

실패 시 결론은 `자료 부족` UI가 아니라 다음과 같이 명시한다.

> 현재 데이터와 정의로는 신뢰할 수 있는 미래 국면 확률을 만들 수 없으므로 예측
> 기능 개발을 중단한다. 현재 국면 진단만 유지한다.

## What To Defer

- probability UI, 순환 화살표, forecast persistence schema
- model ensemble과 dynamic factor
- 자동 자산배분·매매 해석
- 자산별 확인 포인트의 디자인과 계산 변경

## Decision Checkpoint

feasibility gate가 통과하면 그때 아래 제품 계약을 별도 승인받는다.

- 현재: 현재 국면과 confidence
- 향후: 가장 가능성 높은 경로와 확률
- 대안: 두 번째 경로와 확률
- 위험: 현재 국면 유지 실패 또는 악화 확률
- 근거: 과거 유사 결과, 주요 선행요인, 반증 조건
- 모델 신뢰도: outcome probability와 분리된 calibration/coverage 등급

## Required Decision

첫 feasibility 연구의 예측 기간을 확정해야 한다. 권장안은 정확한 특정 월보다
거시적 변화를 포착하는 `향후 3개월`과 `향후 6개월` 두 horizon이다.

## Proposed Next Handoff

사용자가 horizon과 gate-first 원칙을 승인하면 별도 research/design cycle을 연다.
forecast 가능성이 확인되기 전에는 구현 task, roadmap 변경 또는 UI prototype을 열지
않는다.

## Evidence Summary

- actual current read model: 2026-07-31 READY, 위축, 8/8 series
- focused economic-cycle tests: 106 passed
- current +1M/+2M artifact: all LIMITED
- separate forecast artifacts: both INSUFFICIENT_EVIDENCE
- direction publication states: PUBLICATION_HOLD / REJECTED
- current code: fixed next-phase selection, historical destination comparison 없음

## Risks And Unknowns

- strict PIT history가 짧아 4-class probability는 끝내 성립하지 않을 수 있다.
- revised long history를 사용하면 표본은 늘지만 real-time 재현성 위험이 생긴다.
- `3개월/6개월 후 국면`과 `3개월/6개월 안에 전환`은 다른 target이므로 하나를 명확히
  선택해야 한다.
- 여러 target을 시험한 뒤 가장 좋아 보이는 것만 고르면 publication bias가 생긴다.
