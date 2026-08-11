# Feature Candidates

Status: awaiting user decision
Last Updated: 2026-08-11

## Summary

현행 V3 observed-state는 유지할 수 있지만 adjacent transition monitor는 forecast가
아니다. 다음 제품 변경은 UI 구현이 아니라 forecast feasibility gate여야 한다.

## Candidate Matrix

| Candidate | Bucket | Impact | Effort | Risk | Confidence | Strategic Fit | Owner Area |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| Forecast feasibility gate | Now | 5 | 3 | 2 | 5 | 5 | research + economic-cycle domain |
| Current state + multi-path forecast | Next | 5 | 5 | 5 | 3 | 5 | economic-cycle data/model/service/UI |
| Resilient forecast input contract | Next | 4 | 4 | 3 | 4 | 5 | ingestion + loaders + model runtime |
| Dynamic-factor / regime ensemble | Later | 4 | 5 | 5 | 2 | 4 | shadow research |

## Candidates

### Forecast Feasibility Gate

- Bucket: Now
- Problem: 기존 1·2개월·4국면 모델과 이후 방향 모델이 반복해서 표본·baseline·calibration
  gate를 통과하지 못했는데 UI 또는 pipeline부터 개발했다.
- User workflow change: 없음. 개발 전에 어떤 horizon과 target이 실제로 예측 가능한지
  go/no-go report로 결정한다.
- Evidence: 현재 DB의 모든 forecast artifact가 LIMITED, INSUFFICIENT_EVIDENCE,
  REJECTED 또는 PUBLICATION_HOLD다.
- Required areas: PIT dataset audit, target definition, chronological validation runner,
  candidate/baseline report. UI·schema production change 없음.
- Dependencies: 사용자가 macro horizon과 probability 의미를 승인해야 한다.
- Risks: 좋은 결과가 나오는 target을 사후 선택하는 과최적화.
- Validation: 사전에 고정한 target/horizon으로 repeated walk-forward, episode-block
  bootstrap, Brier/log loss/ECE와 baseline skill을 계산한다.
- Owner skill: finance-product-audit + finance-feature-opportunity; 승인 후 별도 domain task.
- Priority rationale: 통과하면 구현 근거가 되고 실패하면 비용 큰 잘못된 개발을 막는다.

### Current State + Multi-Path Forecast

- Bucket: Next
- Problem: 현행 시스템은 모든 후보를 비교하지 않고 배열상 다음 국면만 감시한다.
- User workflow change: `현재 진단 → 향후 주경로 → 대안 경로 → 위험 요인 → 반증 조건`을
  한 흐름에서 읽는다.
- Evidence: `_next_phase()`와 `_next_observed_phase()`가 다음 국면을 deterministic하게
  선택하며 역사적 outcome을 조회하지 않는다.
- Required areas: forecast target/model, artifact/persistence, Overview service, cycle route UI,
  methodology copy. 자산별 확인 포인트는 frozen scope로 유지한다.
- Dependencies: feasibility gate 통과와 확률 publication contract 승인.
- Risks: sample scarcity, probability miscalibration, current phase와 forecast target 혼동.
- Validation: 모든 후보 국면 probability simplex, chronological OOS, baseline superiority,
  calibration, revision stress, Browser QA.
- Owner skill: 승인 후 finance data/model domain task와 UI implementation task.
- Priority rationale: 사용자 원래 목적과 직접 일치하지만 gate 이전에는 시작할 수 없다.

### Resilient Forecast Input Contract

- Bucket: Next
- Problem: optional source 지연을 전체 forecast unavailable로 만들면 실사용할 수 없다.
- User workflow change: 정상 시 core model을, 일부 optional source 지연 시 검증된 reduced
  model을, 짧은 장애 시 날짜가 표시된 last-good result를 본다.
- Evidence: current data는 최신이지만 과거 모델은 feature 교집합 때문에 origin support가
  크게 줄었다.
- Required areas: stable core feature registry, optional feature groups, model variants,
  freshness policy, last-good persistence.
- Dependencies: 각 fallback 모델의 독립 validation.
- Risks: fallback이 primary보다 약한데 같은 확률처럼 보이는 문제.
- Validation: source dropout simulation, variant별 OOS/calibration gate, stale-age expiry.
- Owner skill: finance-db-pipeline + economic-cycle model/runtime task.
- Priority rationale: forecast gate 통과 뒤 실제 화면이 매달 작동하기 위한 필수 기반이다.

### Dynamic-Factor / Regime Ensemble

- Bucket: Later
- Problem: mixed-frequency 발표와 revision을 단순 monthly factor보다 잘 처리할 가능성이 있다.
- User workflow change: 없음. shadow score로만 운영하다 독립 gate 통과 후 후보가 된다.
- Evidence: ADS 같은 official real-time index가 mixed-frequency nowcast의 실현 가능성을
  보여주지만 현재 프로젝트 모델의 성능 근거는 없다.
- Dependencies: 더 긴 real-time dataset과 운영 복잡도 수용.
- Risks: 설명력 감소, 과최적화, maintenance burden.
- Validation: simple regularized model보다 명확히 우수해야 한다.
- Owner skill: later shadow research.

## Parking Lot

- 1·2개월 네 국면 확률의 즉시 복구
- historical analog 빈도만 확률로 표시
- current monitor의 `N/3`을 probability percentage로 변환

## Rejected Ideas

- 고정 인접 국면을 미래 예상 경로로 계속 표시: 역사적 비교가 없어 사용자 요구를
  충족하지 않는다.
- gate 미통과 probability를 `잠정`, `참고용` 이름으로 공개: 숫자의 오해 위험은
  라벨로 해결되지 않는다.
