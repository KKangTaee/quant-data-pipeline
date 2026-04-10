# Phase 14 Current Chapter TODO

## 상태 기준

- `pending`
- `in_progress`
- `completed`

## 1. Chapter Setup

- `completed` Phase 14 방향 고정
  - `real-money gate calibration + deployment workflow bridge`로 연다
- `completed` 보류 논의 재등록
  - Phase 13 QA 이후 다시 보기로 했던
    `promotion / shortlist gate calibration`을 이번 phase 핵심 질문으로 올린다
- `completed` current active phase 전환 준비
  - roadmap / index / progress / analysis log 기준으로 Phase 14를 현재 준비 phase로 둔다

## 2. Gate Blocker Distribution Audit

- `completed` representative run set 정의
  - strict annual family
  - ETF family
  - repeated near-miss candidate
- `completed` blocker distribution 집계
  - `validation`
  - `benchmark policy`
  - `liquidity policy`
  - `validation policy`
  - `guardrail policy`
  - `ETF operability`
  - `price freshness`
- `completed` repeated hold 원인 문서화
  - “전략 quality 문제”와 “gate threshold 문제”를 분리해서 정리
- `completed` history evidence gap 보강
  - future audit를 위해 backtest history에 `gate_snapshot`을 같이 저장한다

## 3. Promotion / Shortlist Calibration Review

- `completed` current threshold inventory 정리
  - promotion 관련 threshold를 한 문서에서 다시 읽을 수 있게 정리
- `completed` family별 calibration necessity review
  - strict annual vs ETF family
- `completed` factor expansion necessity review
  - factor 부족이 현재 repeated hold의 1차 원인인지 분리해서 본다
- `completed` controlled factor expansion shortlist
  - existing factor DB 안에서 UI에 아직 안 연 후보를 small-set으로 추린다
- `completed` near-miss candidate case study
  - strongest raw winner
  - strongest balanced near-miss
  - repeated watchlist candidate
- `completed` strict annual validation-policy sensitivity review
  - exact-hit hold 케이스를 기준으로 validation / validation_policy threshold를 좁혀 본다
- `completed` ETF operability sensitivity review
  - practical non-hold와 aggressive near-miss 경계를 기준으로 operability threshold를 다시 본다

## 4. Deployment Workflow Bridge

- `pending` shortlist -> paper probation handoff 흐름 정리
- `pending` monthly review note / operator log 필요 범위 정리
- `pending` small-capital trial readiness interpretation 정리
- `pending` backtest result와 operator action 문서 연결점 정의

## 5. PIT Operability Later Pass

- `pending` ETF PIT operability dependency 정리
- `pending` actual block rule 승격 조건 정의
- `pending` snapshot overlay와 PIT contract boundary 문서화

## 6. Documentation And Validation

- `completed` Phase 14 분석 문서 인덱스 반영
- `completed` roadmap / progress / analysis log 동기화
- `pending` Phase 14 manual test checklist 준비

## 현재 메모

- `Phase 12`: implementation closed / manual_validation_pending
- `Phase 13`: practical closeout / manual_validation_pending
- `Phase 14`: gate blocker audit first pass 완료 / calibration review 대기

- 이번 phase의 핵심은 새 전략 추가보다
  **현재 real-money gate가 어떻게 막히는지 설명 가능한 상태로 만드는 것**
  이다.
- 사용자 보류 항목이었던 `promotion / shortlist gate calibration` 논의를
  이제 Phase 14의 정식 workstream으로 다룬다.
- first-pass audit 결과,
  strict annual repeated hold의 핵심 blocker는 `validation / validation_policy`,
  ETF family practical blocker는 `ETF operability + validation 해석` 쪽으로 좁혀졌다.
- representative rerun `9`건 기준 current outcome은
  - `real_money_candidate = 1`
  - `production_candidate = 2`
  - `hold = 6`
  이며, 다음 active step은 near-miss candidate case study다.
- calibration review first pass 기준,
  factor 부족은 repeated hold의 1차 원인으로 보이지 않았고,
  factor expansion은 이후 controlled search workstream으로 여는 것이 더 적절하다.
- controlled factor expansion first pass에서는
  - Quality: `interest_coverage`, `ocf_margin`, `fcf_margin`, `net_debt_to_equity`
  - Value: `liquidation_value`
  만 small-set으로 먼저 열었다.
- near-miss case study first pass 기준,
  다음 calibration 실험은 blanket relaxation보다
  - strict annual: `validation / validation_policy`
  - ETF: `operability watch/caution boundary`
  를 family별로 좁혀 보는 쪽이 더 적절하다.
- sensitivity review first pass 기준,
  strict annual exact-hit hold는 `validation_policy` 완화만으로는 잘 풀리지 않았고,
  ETF aggressive near-miss는 AUM/spread 완화보다 `partial data coverage` 해석이 더 직접적인 blocker였다.
- 따라서 next active step은
  - strict annual: `validation_status` fixed threshold review
  - ETF: `operability data coverage interpretation review`
  쪽으로 가는 것이 더 맞다.
