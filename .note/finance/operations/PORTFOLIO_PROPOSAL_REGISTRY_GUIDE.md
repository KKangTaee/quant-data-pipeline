# Portfolio Proposal Registry Guide

## 이 문서는 무엇인가

이 문서는 `.note/finance/PORTFOLIO_PROPOSAL_REGISTRY.jsonl`을
어떤 용도로 쓰고, Current Candidate Registry / Pre-Live Candidate Registry와
어떻게 구분하는지 설명한다.

## 쉽게 말하면

`CURRENT_CANDIDATE_REGISTRY.jsonl`은
"다시 볼 만한 후보가 무엇인가"를 저장한다.

`PRE_LIVE_CANDIDATE_REGISTRY.jsonl`은
"그 후보를 실전 전에 어떻게 관찰할 것인가"를 저장한다.

`PORTFOLIO_PROPOSAL_REGISTRY.jsonl`은
"여러 후보를 어떤 목적과 비중으로 하나의 포트폴리오 제안 초안으로 묶을 것인가"를 저장한다.

즉 Portfolio Proposal은 후보 목록도 아니고 live approval도 아니다.
후보 묶음의 설명서에 가깝다.

단일 후보만 다룰 때는 이 저장소를 반드시 새로 만들 필요가 없다.
Candidate Review에서 이미 current candidate와 Pre-Live 운영 기록이 남아 있다면,
`Backtest > Portfolio Proposal`은 그 후보가 Live Readiness로 직행 가능한지만 평가한다.

## 왜 필요한가

최종 목표는 단일 전략 후보를 많이 모으는 것이 아니라,
사용자가 실제로 검토할 수 있는 포트폴리오 구성안과 가이드를 제시하는 것이다.

그러려면 후보 여러 개를 묶을 때 아래 내용이 함께 남아야 한다.

- 어떤 목적의 포트폴리오인지
- 어떤 후보가 어떤 역할을 하는지
- 각 후보의 target weight는 얼마인지
- 비중을 왜 그렇게 두었는지
- Real-Money / Pre-Live 상태가 어떤지
- 저장 전 blocker가 남아 있는지
- 다음 검토 행동이 무엇인지

## 파일 위치

| 구분 | 위치 | 역할 |
|---|---|---|
| Current candidate registry | `.note/finance/CURRENT_CANDIDATE_REGISTRY.jsonl` | current anchor, near-miss, scenario 후보 저장 |
| Pre-Live candidate registry | `.note/finance/PRE_LIVE_CANDIDATE_REGISTRY.jsonl` | 후보의 pre-live 운영 상태 저장 |
| Portfolio proposal registry | `.note/finance/PORTFOLIO_PROPOSAL_REGISTRY.jsonl` | 후보 묶음의 proposal draft 저장 |
| Runtime helper | `app/web/runtime/portfolio_proposal.py` | proposal JSONL append / load helper |
| UI | `Backtest > Portfolio Proposal` | 단일 후보 직행 평가, 다중 후보 proposal 초안 작성, monitoring / feedback / 저장 record inspect |

`PORTFOLIO_PROPOSAL_REGISTRY.jsonl`은 첫 row를 append할 때 생성된다.
row가 없으면 `Backtest > Portfolio Proposal > Proposal Registry`에는 빈 상태가 표시된다.

## 저장해야 하는 핵심 필드

| 필드 | 뜻 |
|---|---|
| `schema_version` | proposal row schema version |
| `proposal_id` | proposal draft의 stable id |
| `proposal_status` | `draft`, `review_ready`, `paper_tracking`, `hold`, `rejected`, `superseded`, `live_readiness_candidate` 중 하나 |
| `proposal_type` | `balanced_core`, `lower_drawdown_core`, `defensive_blend`, `satellite_pack` 중 하나 |
| `objective` | primary goal, secondary goal, review cadence, capital scope |
| `candidate_refs` | proposal에 포함된 current candidate 목록과 역할 / 비중 |
| `construction` | weighting method, benchmark policy, date alignment note |
| `risk_constraints` | component weight, review 필요 여부 같은 위험 경계 |
| `evidence_snapshot` | 저장 시점의 CAGR, MDD, promotion, shortlist, period 요약 |
| `open_blockers` | 저장 전 해결해야 할 문제 |
| `operator_decision` | 사람이 남기는 판단, 이유, 다음 행동, review date |

## 기본 사용 방법

앱 화면에서는 `Backtest > Portfolio Proposal`에서 사용한다.

- `1. Proposal 후보 확인`
  - Candidate Review에서 넘어온 후보가 있으면 자동 선택된다.
  - 직접 들어온 사용자는 current candidate 목록에서 1~6개 후보를 고른다.
  - `Proposal Components`는 비교 기능이 아니라 포트폴리오에 넣을 구성 후보 선택이다.
- 단일 후보 경로
  - 후보가 1개이면 기본값은 `단일 후보 직행 평가`다.
  - 이 경로는 role `core_anchor`, target weight `100%`, capital scope `paper_only`를 자동 전제로 둔다.
  - 새 proposal draft를 저장하지 않고, 기존 current candidate / Pre-Live record가 Live Readiness 입력으로 충분한지만 확인한다.
  - route가 `LIVE_READINESS_DIRECT_READY`이면 이후 Live Readiness에서 바로 읽을 수 있는 후보 형태로 본다.
- `2. 목적 / 역할 / 비중 설계`
  - 후보가 2개 이상이거나 단일 후보라도 명시적인 포트폴리오 초안을 남기고 싶을 때만 사용한다.
  - proposal 목적, type, status, capital scope를 입력한다.
  - 후보별 proposal role, target weight, weight reason을 입력한다.
- `3. Proposal 저장 및 다음 단계 판단`
  - 단일 후보 경로에서는 `Live Readiness 직행 평가`에서 route, 10점 readiness, blocker를 확인한다.
  - 다중 후보 경로에서는 `Live Readiness 진입 평가`에서 route, 10점 readiness, blocker를 확인한다.
  - `LIVE_READINESS_CANDIDATE_READY`이면 저장 후 이후 Live Readiness 단계 후보로 넘길 수 있는 형태다.
  - `PROPOSAL_DRAFT_READY`이면 proposal draft 저장은 가능하지만 Live Readiness 전 보강 항목이 남은 상태다.
  - `Save Portfolio Proposal Draft`는 다중 후보 구성 초안 또는 명시 저장이 필요한 단일 후보에만 사용한다.
- `보조 도구: Saved Proposals / Feedback`
  - 저장된 proposal draft 목록과 raw JSON을 확인한다.
  - Monitoring, Pre-Live Feedback, Paper Tracking Feedback을 읽기 전용으로 확인한다.
  - 이 보조 도구는 proposal이나 Pre-Live record를 자동 수정하지 않는다.

## 운영 기준

- Portfolio Proposal은 live trading approval이 아니다.
- Portfolio Proposal은 주문 지시가 아니다.
- 단일 후보를 Live Readiness로 직행 평가할 때는 proposal draft 저장이 필수가 아니다.
- 여러 후보를 하나의 포트폴리오 구성안으로 묶는 경우에만 proposal draft 저장이 핵심이다.
- `live_readiness_candidate` 상태도 "최종 승인"이 아니라 다음 phase의 검토 후보라는 뜻이다.
- saved portfolio는 재현 가능한 weight setup이고, Portfolio Proposal은 그 setup이나 후보 묶음을 왜 검토하는지 설명하는 기록이다.
- proposal row를 저장해도 `CURRENT_CANDIDATE_REGISTRY.jsonl`이나 `PRE_LIVE_CANDIDATE_REGISTRY.jsonl`이 자동으로 바뀌지 않는다.
- `Live Readiness 진입 평가`에서 `LIVE_READINESS_CANDIDATE_READY`가 보여도 실전 승인이나 주문 가능 상태라는 뜻은 아니다.
- `Saved Proposals / Feedback`에서 gap이 보여도 자동으로 proposal이 reject되거나 hold되는 것은 아니다.
- `Paper Tracking Feedback`에서 `stable_or_better`가 보여도 실전 승인이나 주문 가능 상태라는 뜻은 아니다.

## 현재 한계

- 자동 optimizer는 없다.
- 후보 간 correlation / overlap / turnover / capacity 평가는 아직 별도 surface로 구현되지 않았다.
- paper tracking 성과 결과를 proposal에 자동 반영하지 않는다.
- 실제 paper PnL 시계열 저장소는 아직 없다. 현재 `Paper Tracking Feedback`은 Pre-Live record에 저장된 `result_snapshot` 기준 비교다.
- live readiness / final approval은 Phase 30 이후 별도 phase 후보로 남긴다.
