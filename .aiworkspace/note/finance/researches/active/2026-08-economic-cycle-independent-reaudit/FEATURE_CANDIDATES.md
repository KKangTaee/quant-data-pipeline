# Feature Candidates

Status: RTDSM data expansion completed; state-target decision required
Last Updated: 2026-08-12

## Summary

현행 V3 observed-state는 유지할 수 있지만 adjacent transition monitor는 forecast가
아니다. 다음 제품 변경은 UI 구현이 아니라 forecast feasibility gate여야 한다.

## Candidate Matrix

| Candidate | Bucket | Impact | Effort | Risk | Confidence | Strategic Fit | Owner Area |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| Forecast feasibility gate | Done | 5 | 3 | 2 | 5 | 5 | research + economic-cycle domain |
| RTDSM realtime history expansion | Done / No-Go parity | 5 | 4 | 3 | 5 | 5 | ingestion + loaders + research |
| Current state + multi-path forecast | Blocked | 5 | 5 | 5 | 3 | 5 | economic-cycle data/model/service/UI |
| External-anchor long-history state target | Decision required | 5 | 5 | 5 | 2 | 5 | economic-cycle research + data/model |
| Resilient forecast input contract | Blocked | 4 | 4 | 3 | 4 | 5 | ingestion + loaders + model runtime |
| Dynamic-factor / regime ensemble | Later | 4 | 5 | 5 | 2 | 4 | shadow research |

## Candidates

### Forecast Feasibility Gate

- Bucket: Done
- Problem: 기존 1·2개월·4국면 모델과 이후 방향 모델이 반복해서 표본·baseline·calibration
  gate를 통과하지 못했는데 UI 또는 pipeline부터 개발했다.
- User workflow change: 없음. 개발 전에 어떤 horizon과 target이 실제로 예측 가능한지
  go/no-go report로 결정한다.
- Evidence: 현재 DB의 모든 forecast artifact가 LIMITED, INSUFFICIENT_EVIDENCE,
  REJECTED 또는 PUBLICATION_HOLD다.
- Required areas: PIT dataset audit, target definition, chronological validation runner,
  candidate/baseline report. UI·schema production change 없음.
- Result: 사용자가 next confirmed phase와 transition imminence 의미를 승인했고, actual
  PIT audit는 usable origin 148 / independent event 32로 `NO_GO_DATA`를 반환했다.
- Risks: 좋은 결과가 나오는 target을 사후 선택하는 과최적화.
- Validation: 사전에 고정한 target/horizon으로 repeated walk-forward, episode-block
  bootstrap, Brier/log loss/ECE와 baseline skill을 계산한다.
- Owner skill: finance-product-audit + finance-feature-opportunity; 승인 후 별도 domain task.
- Priority rationale: 통과하면 구현 근거가 되고 실패하면 비용 큰 잘못된 개발을 막는다.

### RTDSM Realtime History Expansion

- Bucket: Done / No-Go parity
- Problem: 현재 strict PIT observed-state는 2014-04 이후 148개월만 usable하며 확장·둔화
  holdout 사건이 0건이다.
- User workflow change: 없음. probability UI 전에 공식 장기 realtime data가 표본 gate를
  실제로 해결하는지 판단한다.
- Evidence: Philadelphia Fed RTDSM은 payroll monthly vintages를 1964-12부터 제공하고,
  unemployment, hours와 industrial production도 full vintage history를 제공한다. ADS는
  assessed-in-real-time vintages를 공개한다.
- Implemented: official workbook contract, source-isolated shared ledger, conservative known-at,
  bounded batch/overlap UPSERT, DB-only PIT loader와 sample/parity audit.
- Actual: 1,334,818 unique rows, 589 usable origins, 117 transitions로 sample은 통과했다.
  그러나 common 142개월 exact phase agreement 54.2%, Cohen's kappa 0.368로 사전 parity
  기준 60%/0.40을 통과하지 못했다.
- Decision: `NO_GO_PARITY`. RTDSM shadow state를 current product state나 forecast label로
  연결하지 않는다.
- Owner skill: finance-db-pipeline + economic-cycle research task.
- Priority rationale: 현재 NO_GO_DATA를 정직하게 해결할 수 있는 유일한 다음 단계다.

### Current State + Multi-Path Forecast

- Bucket: Blocked
- Problem: 현행 시스템은 모든 후보를 비교하지 않고 배열상 다음 국면만 감시한다.
- User workflow change: `현재 진단 → 향후 주경로 → 대안 경로 → 위험 요인 → 반증 조건`을
  한 흐름에서 읽는다.
- Evidence: `_next_phase()`와 `_next_observed_phase()`가 다음 국면을 deterministic하게
  선택하며 역사적 outcome을 조회하지 않는다.
- Required areas: forecast target/model, artifact/persistence, Overview service, cycle route UI,
  methodology copy. 자산별 확인 포인트는 frozen scope로 유지한다.
- Dependencies: realtime history 확장 뒤 sample gate 통과와 확률 publication contract 승인.
- Risks: sample scarcity, probability miscalibration, current phase와 forecast target 혼동.
- Validation: 모든 후보 국면 probability simplex, chronological OOS, baseline superiority,
  calibration, revision stress, Browser QA.
- Owner skill: 승인 후 finance data/model domain task와 UI implementation task.
- Priority rationale: 사용자 원래 목적과 직접 일치하지만 gate 이전에는 시작할 수 없다.

### External-Anchor Long-History State Target

- Bucket: Decision required
- Problem: 현행 8지표 state와 RTDSM 4지표 state는 표본 수는 충분하지만 같은 국면을
  충분히 일관되게 측정하지 않는다.
- Proposed scope: NBER turning-point chronology와 독립 coincident benchmark를 보조 정답으로
  사용해, 전체 장기 구간에서 하나의 current-state label을 먼저 정의한다.
- Boundary: 현행 화면 label을 유지한 채 신규 label을 억지로 맞추거나 parity threshold를
  완화하지 않는다. target이 고정된 뒤 chronological OOS gate를 처음부터 다시 통과해야 한다.
- Risk: 공식 recession chronology는 월별 4국면 정답이 아니므로 추가 설계도 실패할 수 있다.
- Decision: 사용자가 이 별도 연구 범위를 승인하거나 forecast 개발을 중단해야 한다.

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
