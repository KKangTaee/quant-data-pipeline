# PLAN - Investability Evidence Packet V1

Status: Active
Created: 2026-05-28

## Goal

Final Review에서 기존 Practical Validation / diagnostics / provider / benchmark / paper observation evidence를 하나의 compact 판단 packet으로 읽고, critical gap이 있으면 `SELECT_FOR_PRACTICAL_PORTFOLIO` 저장을 막거나 재검토 판단으로 유도한다.

## 이걸 하는 이유?

현재 프로젝트는 Backtest -> Practical Validation -> Final Review -> Selected Dashboard 흐름을 이미 갖고 있다.
하지만 실전 투자 판단 보조 도구로 쓰기에는 `NOT_RUN`, proxy evidence, provider coverage, benchmark parity, assumptions / limitations가 Final Review에서 충분히 강한 gate로 읽히지 않는다.

이번 task는 새 JSONL 저장소를 늘리거나 사용자 메모 저장 기능을 추가하지 않고, 이미 생성되는 validation / final decision 흐름 안에서 투자 가능성 판단 근거를 더 명확히 보여주는 첫 구현이다.

## Scope

Include:

- Final Review evidence packet read model
- critical gap / assumption / source chain summary
- Final Review save readiness hardening for selected route
- compact UI display in Final Review
- focused service contract tests
- minimal durable docs / handoff log sync

Exclude:

- 새 JSONL registry 생성
- DB schema 변경
- provider collector / crawler 추가
- full report export
- broker order, live approval, auto rebalance
- 사용자 free-form memo 저장 기능 추가

## Storage Principles

- 기존 `PRACTICAL_VALIDATION_RESULTS`와 `FINAL_PORTFOLIO_SELECTION_DECISIONS_V2` 흐름을 유지한다.
- 새 append-only JSONL 저장소를 만들지 않는다.
- Final decision row에는 full raw data가 아니라 compact packet / gate snapshot만 붙인다.
- full holdings, macro series, provider raw-ish row는 DB 영역으로 유지한다.

## Target Files

| File | Work |
| --- | --- |
| `app/services/backtest_evidence_read_model.py` | Streamlit-free packet / gate / assumptions read model 추가 |
| `app/web/backtest_final_review_helpers.py` | packet 기반 save evaluation / decision row snapshot 연결 |
| `app/web/backtest_final_review.py` | Final Review UI에 packet / critical gaps / assumptions 표시 |
| `tests/test_service_contracts.py` | selected route gate / assumptions / packet contract tests |
| `.aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md` | 구현 후 필요한 최소 흐름 문서 보정 |

## Completion Criteria

- Final Review에서 selected route 저장은 critical gap이 있으면 차단된다.
- hold / reject / re-review는 critical gap이 있어도 사유와 함께 저장 가능하다.
- packet은 source chain, backtest/data/provider/benchmark/robustness/paper/assumption 영역을 compact하게 요약한다.
- 기존 registry JSONL 파일을 새로 만들지 않는다.
- service contract tests pass.
