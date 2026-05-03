# Phase 31 First Work Unit: Portfolio Risk Input And Validation Contract

## 목적

이 문서는 Phase 31의 첫 번째 작업 단위를 정의한다.
첫 작업은 UI를 바로 늘리는 것이 아니라,
Portfolio Risk / Live Readiness Validation이 무엇을 입력으로 읽고 무엇을 출력으로 보여줄지 먼저 고정하는 것이다.

## 쉽게 말하면

단일 후보와 Portfolio Proposal은 모양이 다르다.

- 단일 후보는 current candidate와 Pre-Live record를 바로 읽는다.
- proposal draft는 여러 current candidate와 target weight, role, evidence snapshot을 함께 읽는다.

첫 번째 작업은 이 둘을 같은 validation pack으로 읽을 수 있게 입력 모양을 맞추는 것이다.

## 왜 필요한가

입력 계약이 없으면 Phase 31이 기존 Candidate Review / Portfolio Proposal 판단을 또 저장하는 화면으로 흐를 위험이 있다.
Phase 31은 새 decision registry를 먼저 만드는 단계가 아니라,
기존 기록을 읽어 risk/readiness summary를 만드는 단계여야 한다.

## 입력 소스

| 입력 | 위치 | Phase 31에서 읽는 이유 |
|---|---|---|
| Current Candidate Registry | `.note/finance/registries/CURRENT_CANDIDATE_REGISTRY.jsonl` | 후보 identity, strategy family, result snapshot, contract를 읽는다 |
| Pre-Live Candidate Registry | `.note/finance/registries/PRE_LIVE_CANDIDATE_REGISTRY.jsonl` | paper / watchlist / hold / rejected 같은 운영 상태와 tracking plan을 읽는다 |
| Portfolio Proposal Registry | `.note/finance/registries/PORTFOLIO_PROPOSAL_REGISTRY.jsonl` | 다중 후보 구성, role, target weight, objective, evidence snapshot을 읽는다 |

## 출력 모델 초안

Phase 31 validation result는 우선 화면에서 계산되는 summary로 본다.
처음부터 append-only registry를 만들지 않는다.

필수 출력:

- `source_type`: `single_candidate` 또는 `portfolio_proposal`
- `source_id`: current candidate id 또는 proposal id
- `validation_route`: `READY_FOR_ROBUSTNESS_REVIEW`, `PAPER_TRACKING_REQUIRED`, `NEEDS_PORTFOLIO_RISK_REVIEW`, `BLOCKED_FOR_LIVE_READINESS`
- `validation_score`: 0~10 사이의 검증 점수
- `hard_blockers`: 반드시 해결해야 하는 차단 항목
- `review_gaps`: 다음 검증 전에 확인하면 좋은 항목
- `next_action`: 사용자가 다음에 해야 할 행동
- `component_rows`: 후보별 role / weight / status / risk signal table
- `handoff_summary`: 다음 robustness 검증 단계가 읽을 요약

## 첫 구현 위치 후보

| 파일 | 역할 |
|---|---|
| `app/web/backtest_portfolio_proposal_helpers.py` | validation input build, route/score/blocker 계산 helper |
| `app/web/backtest_portfolio_proposal.py` | `Backtest > Portfolio Proposal` 안의 validation surface render |
| `app/web/backtest_ui_components.py` | 기존 route/readiness panel 재사용. 새 공용 component가 꼭 필요할 때만 수정 |

## 첫 작업의 완료 기준

- `completed` 단일 후보와 proposal draft를 같은 validation input dict로 만들 수 있다.
- `completed` validation result가 route, score, blocker, next action을 반환한다.
- `completed` helper 단위 smoke로 입력/출력이 확인됐다.
- `completed` 새 registry를 만들지 않았다는 점이 문서와 UI에 남아 있다.

## 구현 결과

- `app/web/backtest_portfolio_proposal_helpers.py`에 Phase 31 validation input / result helper를 추가했다.
- `app/web/backtest_portfolio_proposal.py`에서 단일 후보, 작성 중 proposal, 저장된 proposal을 같은 Validation Pack으로 렌더링한다.
- validation route는 `READY_FOR_ROBUSTNESS_REVIEW`, `PAPER_TRACKING_REQUIRED`, `NEEDS_PORTFOLIO_RISK_REVIEW`, `BLOCKED_FOR_LIVE_READINESS`로 구분한다.
- component table은 role, weight, family, benchmark, universe, factors, Pre-Live, Data Trust, Promotion, Deployment를 함께 보여준다.
- `handoff_summary`는 `검증 기준 / 다음 단계 안내` expander 안에서 확인할 수 있다.

## 이번 작업에서 하지 않는 것

- live approval 저장
- broker 주문 연동
- 최종 투자 추천 report
- 실제 paper PnL ledger
- optimizer / 자동 비중 산출
- 본격 robustness / stress sweep

## 다음 작업

두 번째 작업에서는 이 입력 계약을 바탕으로
`Backtest > Portfolio Proposal` 안에 Portfolio Risk / Live Readiness Validation surface를 추가한다.
