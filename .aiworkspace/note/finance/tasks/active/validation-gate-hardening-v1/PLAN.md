# PLAN - Validation Gate Hardening V1

Status: Active
Created: 2026-05-28

## Goal

Final Review의 `Investability Evidence Packet` gate를 단순 critical gap 목록에서 명시적인 validation policy matrix로 강화한다.

## 이걸 하는 이유?

Phase 0에서 정한 핵심은 "백테스트 결과를 더 많이 저장하는 것"이 아니라 "실전 검토 후보로 올릴 수 없는 이유를 더 정확히 막는 것"이다.

현재 V1 packet은 hard blocker, critical `NOT_RUN`, paper observation blocker를 막기 시작했지만, 어떤 영역이 critical인지, profile별로 어떻게 볼지, proxy-only / benchmark / provider gap을 어떤 route로 유도할지 아직 정책으로 충분히 드러나지 않는다.

이번 task는 새 JSONL registry나 사용자 memo 저장 없이, Final Review read model 안에서 gate policy를 구조화해 다음 phase task들이 같은 기준을 재사용하게 만드는 작업이다.

## Scope

Include:

- Streamlit-free gate policy matrix helper
- profile-aware critical diagnostic group classification
- selected route block / hold / re-review recommendation reason 정리
- compact `gate_policy_snapshot`를 final decision row에 포함
- Final Review UI에 policy matrix / route guidance 표시
- focused service contract tests
- 최소 durable docs / phase status sync

Exclude:

- 새 JSONL registry 생성
- waiver 입력 UI 구현
- DB schema 변경
- provider crawler / ingestion 구현
- report export
- broker order, live approval, auto rebalance

## Initial Policy Defaults

- Structured waiver는 V1에서 구현하지 않는다.
- critical gap이 있으면 `SELECT_FOR_PRACTICAL_PORTFOLIO`는 막는다.
- hold / reject / re-review는 critical gap이 있어도 저장 가능하다.
- proxy-only provider / holdings / operability evidence는 selected route에 보수적으로 작동한다.
- benchmark parity, provider coverage, stress / robustness, leveraged / inverse suitability는 profile에 따라 critical 또는 review-required로 분류한다.

## Target Files

| File | Work |
| --- | --- |
| `app/services/backtest_evidence_read_model.py` | gate policy matrix, route guidance, compact snapshot |
| `app/web/backtest_final_review_helpers.py` | final decision row에 policy snapshot 연결 |
| `app/web/backtest_final_review.py` | Final Review UI에 policy matrix / guidance 표시 |
| `tests/test_service_contracts.py` | gate policy contract tests |
| `.aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md` | 구현 후 필요한 최소 문구 보정 |

## Completion Criteria

- selected route gate가 policy matrix 기반으로 설명된다.
- profile-aware critical groups가 service contract로 검증된다.
- final decision row에는 full raw evidence가 아니라 compact policy snapshot만 붙는다.
- 새 registry 파일은 만들지 않는다.
- focused tests, compile, boundary lint, diff check가 통과한다.
