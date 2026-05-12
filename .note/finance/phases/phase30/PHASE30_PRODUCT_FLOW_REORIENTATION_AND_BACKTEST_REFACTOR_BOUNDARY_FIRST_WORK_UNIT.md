# Phase 30 Product Flow Reorientation And Backtest Refactor Boundary First Work Unit

## 이 문서는 무엇인가

Phase 30의 첫 번째 작업 단위 기록이다.
Portfolio Proposal 기능 구현 전에,
Phase 29 이후의 사용자 흐름과 `backtest.py` 리팩토링 경계를 먼저 정리한다.

## 쉽게 말하면

지금은 기능을 하나 더 붙이기보다,
"백테스트 결과를 보고 최종 실전 포트폴리오 제안까지 어떻게 가는가"를 다시 손에 잡히게 만드는 단계다.

그리고 그 흐름을 기준으로,
너무 커진 `app/web/pages/backtest.py`를 앞으로 어떤 단위로 나눌지 정한다.

## 왜 필요한가

- Phase 29에서 Candidate Draft, Candidate Review Note, Registry Draft가 생겼지만, 실제 사용 시점이 흐려질 수 있다.
- 기존 Guide는 Phase 29 이전 흐름에 가까워 Candidate Review 이후 단계가 충분히 반영되지 않았다.
- `backtest.py`는 16k lines 이상으로 커져서 기능을 더 붙일수록 변경 위험이 커진다.
- 최종 목표는 실전 포트폴리오와 가이드를 제시하는 것이므로, 사용 흐름과 코드 구조가 같이 정리되어야 한다.

## 기준 제품 흐름

```text
Ingestion / Data Trust
  -> Single Strategy Backtest
  -> Real-Money Signal
  -> Hold / Blocker Resolution
  -> Compare
  -> Candidate Draft
  -> Candidate Review Note
  -> Current Candidate Registry
  -> Candidate Board / Compare / Pre-Live Review
  -> Portfolio Proposal
  -> Live Readiness / Final Approval
```

## 각 단계의 역할

| 단계 | 역할 | 저장 여부 | 투자 승인 여부 |
|---|---|---|---|
| Single Strategy Backtest | 전략 하나를 실행해 결과를 읽는다 | history에 실행 기록 저장 | 아님 |
| Real-Money Signal | 거래비용, benchmark, guardrail, data trust를 본다 | result bundle / history에 신호 저장 | 아님 |
| Compare | 여러 전략 또는 후보를 같은 기간에서 비교한다 | history / saved portfolio 가능 | 아님 |
| Candidate Draft | 최신 run/history를 후보처럼 읽어보는 초안 | session state | 아님 |
| Candidate Review Note | 사람이 후보 판단과 다음 행동을 남긴다 | `CANDIDATE_REVIEW_NOTES.jsonl` | 아님 |
| Current Candidate Registry | 후보로 남길 row를 명시적으로 append한다 | `CURRENT_CANDIDATE_REGISTRY.jsonl` | 아님 |
| Pre-Live Review | paper / watchlist / hold / re-review 운영 상태를 기록한다 | `PRE_LIVE_CANDIDATE_REGISTRY.jsonl` | 아님 |
| Portfolio Proposal | 후보 여러 개를 목적 / 비중 / 위험 역할로 묶는다 | future proposal registry 후보 | 아님 |
| Live Readiness | 실제 돈 투입 가능성의 최종 검토 | future phase | 별도 승인 단계 |

## `backtest.py` 리팩토링 경계

현재 `app/web/pages/backtest.py`에는 아래 책임이 함께 들어 있다.

- strategy-specific form rendering
- latest result rendering
- chart / table display helper
- compare runner and compare display
- weighted portfolio builder and saved portfolio workflow
- history list / inspect / replay / load into form
- Candidate Review workflow
- Pre-Live Review workflow
- registry JSONL load / append helpers
- Streamlit session state prefill helpers

첫 번째 분리 후보는 기능이 독립적이고 저장소 경계가 분명한 곳부터 잡는다.

| 우선순위 | 분리 후보 | 이유 |
|---|---|---|
| 1 | Candidate Review module | Phase 29 기능 묶음이 비교적 독립적이고 `CANDIDATE_REVIEW_NOTES.jsonl` 경계가 분명하다 |
| 2 | Pre-Live Review module | `PRE_LIVE_CANDIDATE_REGISTRY.jsonl`와 운영 상태 helper가 분리 가능하다 |
| 3 | Current candidate registry helpers | Candidate Review / Compare / Pre-Live가 함께 쓰므로 공용 persistence helper로 빼는 것이 자연스럽다 |
| 4 | History module | `BACKTEST_RUN_HISTORY.jsonl` inspect / replay / load 책임이 크고 독립적이다 |
| 5 | Saved Portfolio / Weighted Portfolio module | portfolio proposal과 이어질 가능성이 높아 Phase 30 전에 경계를 정해야 한다 |
| 6 | Chart / result display helpers | UI 표시 helper가 많아 공용 컴포넌트화 가능하지만, 먼저 workflow 모듈이 안정된 뒤가 낫다 |
| 7 | Strategy forms | 가장 크지만 전략별 state key가 많아 가장 나중에 신중히 분리한다 |

## 이번 작업에서 바꾸는 것

1. Guide의 `테스트에서 상용화 후보 검토까지 사용하는 흐름`을 새 canonical flow로 갱신한다.
2. `BACKTEST_UI_FLOW.md`에 리팩토링 경계와 순서를 기록한다.
3. Phase 30 문서 bundle을 준비 작업 중심으로 갱신한다.
4. roadmap / index / work log / question log를 Phase 30 active 상태에 맞춘다.

## 이번 작업에서 아직 하지 않는 것

- 실제 `backtest.py` 모듈 분리
- Portfolio Proposal 저장소 구현
- Portfolio Proposal UI 구현
- Live Readiness / Final Approval 구현

## 다음 작업

다음 작업은 두 갈래 중 하나다.

1. Candidate Review / Pre-Live / registry helper 중 하나를 실제 모듈로 분리하는 작은 리팩토링
2. Portfolio Proposal row 계약을 먼저 문서로 정의하는 작업

현재 판단으로는 Portfolio Proposal 계약을 쓰기 전에
registry helper와 Candidate Review 경계를 먼저 분리할지 검토하는 편이 안전하다.
