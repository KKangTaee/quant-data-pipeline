# Phase 30 Portfolio Proposal Contract Second Work Unit

## 이 문서는 무엇인가

Phase 30의 두 번째 작업 단위 기록이다.
이번 작업은 Portfolio Proposal UI를 바로 만들기 전에,
포트폴리오 제안 초안이 무엇을 담아야 하는지 먼저 정한다.

## 왜 이 문서가 두 번째 작업인가

Phase 30의 첫 번째 작업은 `사용 흐름 재정렬 + backtest.py 리팩토링 경계 검토`였다.
그 작업은 제품 흐름과 코드 분리 경계를 정하는 준비 작업이었다.

이 문서는 그 다음 단계다.
흐름상 Portfolio Proposal이 어디에 오는지 정했으므로,
이제 실제 UI나 저장소를 만들기 전에
"무엇을 Portfolio Proposal이라고 부를 것인가"를 먼저 정한다.

즉 이 문서는 첫 번째 작업을 대체하거나 건너뛴 것이 아니라,
첫 번째 작업 이후에 이어지는 Phase 30의 두 번째 설계 작업이다.

## 쉽게 말하면

좋은 후보 여러 개를 그냥 묶는다고 포트폴리오 제안이 되는 것은 아니다.

어떤 목적의 포트폴리오인지,
각 후보가 어떤 역할을 하는지,
비중을 왜 그렇게 주는지,
데이터 신뢰성과 Real-Money / Pre-Live 상태가 어떤지까지 함께 남아야 한다.

이번 작업은 그 저장 단위와 판단 기준을 먼저 고정하는 작업이다.

## 왜 필요한가

- Phase 29까지는 단일 후보를 검토하고 기록하는 흐름이 중심이었다.
- Phase 30의 목표는 후보 묶음을 포트폴리오 제안과 monitoring surface로 연결하는 것이다.
- 후보 여러 개를 묶는 순간 단일 전략보다 해석 책임이 커진다.
- UI를 먼저 만들면 "무엇을 기준으로 포트폴리오라고 부를 것인가"가 비어 있을 수 있다.
- 따라서 저장소와 화면을 만들기 전에 proposal row의 최소 계약을 먼저 정한다.

## 이 작업이 끝나면 좋은 점

- Portfolio Proposal이 단순 weighted result나 saved portfolio와 구분된다.
- 후보별 역할, 비중 근거, 위험 경계, data trust, Real-Money 상태가 함께 남는다.
- 다음 UI 구현자는 어떤 입력과 확인 항목을 화면에 올려야 하는지 알 수 있다.
- 사용자는 제안을 투자 승인으로 오해하지 않고, 검토 / paper tracking 전 단계로 읽을 수 있다.

## Portfolio Proposal의 위치

```text
Current Candidate Registry
  -> Candidate Board / Compare / Pre-Live Review
  -> Portfolio Proposal Draft
  -> Proposal Review / Paper Monitoring
  -> Live Readiness / Final Approval
```

Portfolio Proposal은 `Current Candidate Registry`와 `Pre-Live Review` 이후에 온다.
다만 live readiness나 final approval은 아니다.

## Portfolio Proposal과 기존 저장소의 차이

| 저장소 / 개념 | 역할 | Portfolio Proposal과의 차이 |
|---|---|---|
| `CURRENT_CANDIDATE_REGISTRY.jsonl` | 단일 후보 또는 near-miss / scenario 후보를 남긴다 | 후보 단위 저장소다. 여러 후보의 비중과 목적을 정의하지 않는다 |
| `CANDIDATE_REVIEW_NOTES.jsonl` | 후보 초안에 대한 사람 판단을 남긴다 | 판단 기록이지 포트폴리오 구성안이 아니다 |
| `PRE_LIVE_CANDIDATE_REGISTRY.jsonl` | 후보의 paper / watchlist / hold / re-review 상태를 기록한다 | 운영 상태 기록이지 후보 묶음 제안이 아니다 |
| `SAVED_PORTFOLIOS.jsonl` | weighted portfolio 설정을 저장 / replay한다 | 재현성 저장소다. 제안 목적, 후보 역할, 승인 경계가 충분하지 않다 |
| Portfolio Proposal | 후보 여러 개를 목적 / 비중 / 위험 역할로 묶은 제안 초안이다 | 투자 승인이나 주문 지시가 아니다 |

## 제안 row의 최소 필드

향후 저장소를 구현한다면 기본 후보 위치는
`.note/finance/PORTFOLIO_PROPOSAL_REGISTRY.jsonl`이다.

아직 이번 작업에서는 파일을 만들거나 append 기능을 구현하지 않는다.
아래는 다음 구현에서 맞춰야 할 row 계약이다.

```json
{
  "schema_version": 1,
  "proposal_id": "proposal_YYYYMMDD_slug",
  "created_at": "YYYY-MM-DDTHH:MM:SSZ",
  "updated_at": "YYYY-MM-DDTHH:MM:SSZ",
  "proposal_status": "draft",
  "proposal_type": "balanced_core",
  "objective": {
    "primary_goal": "balanced_growth",
    "secondary_goal": "drawdown_control",
    "target_holding_style": "monthly_or_quarterly_review",
    "capital_scope": "paper_only"
  },
  "candidate_refs": [],
  "construction": {},
  "risk_constraints": {},
  "evidence_snapshot": {},
  "open_blockers": [],
  "operator_decision": {}
}
```

## 필드 의미

| 필드 | 의미 | 필수 여부 |
|---|---|---|
| `schema_version` | proposal row 구조 버전 | 필수 |
| `proposal_id` | 사람이 추적할 수 있는 고유 ID | 필수 |
| `created_at`, `updated_at` | 생성 / 수정 시각 | 필수 |
| `proposal_status` | draft, review_ready, paper_tracking, hold, rejected, superseded 같은 상태 | 필수 |
| `proposal_type` | balanced_core, lower_drawdown_core, defensive_blend, satellite_pack 같은 제안 유형 | 필수 |
| `objective` | 이 제안이 무엇을 위해 만들어졌는지 | 필수 |
| `candidate_refs` | 포함 후보 목록과 후보별 역할 / 비중 / 근거 | 필수 |
| `construction` | 비중 산정 방식과 date alignment / benchmark 기준 | 필수 |
| `risk_constraints` | 최대 비중, MDD, turnover, liquidity, concentration 제한 | 필수 |
| `evidence_snapshot` | proposal 생성 시점의 성과 / data trust / Real-Money / Pre-Live 요약 | 필수 |
| `open_blockers` | 해결되지 않은 데이터 / 검증 / 운영 blocker | 필수 |
| `operator_decision` | 사람이 남긴 판단, 다음 행동, 재검토 날짜 | 필수 |

## 후보 구성 필드

`candidate_refs`의 각 row는 아래를 포함해야 한다.

| 필드 | 의미 |
|---|---|
| `registry_id` | `CURRENT_CANDIDATE_REGISTRY.jsonl`의 후보 ID |
| `strategy_family` | Value, Quality, GTAA, Global Relative Strength 등 |
| `candidate_role` | registry에서의 후보 역할 |
| `proposal_role` | 이 포트폴리오 안에서의 역할 |
| `target_weight` | 제안 비중 |
| `weight_reason` | 왜 이 비중인지 |
| `data_trust_status` | 결과 기간, 가격 최신성, excluded ticker 등 요약 |
| `real_money_status` | Promotion / Shortlist / Deployment / Guardrail 요약 |
| `pre_live_status` | paper / watchlist / hold / re-review 상태 |
| `open_candidate_blockers` | 후보별 미해결 blocker |

## Proposal role 기준

| 역할 | 기본 설명 | 사용 기준 |
|---|---|---|
| `core_anchor` | 포트폴리오의 중심 후보 | data trust와 Real-Money 상태가 충분히 강하고, 장기 후보로 볼 수 있을 때 |
| `return_driver` | 수익 기여를 기대하는 후보 | 변동성이나 MDD가 있어도 보상 근거가 분명할 때 |
| `diversifier` | 다른 후보와 성격이 다른 분산 후보 | 상관 / drawdown timing / strategy family가 다를 때 |
| `defensive_sleeve` | 방어 또는 위험 완충 후보 | 위험 회피, cash / bond / trend 방어 역할이 있을 때 |
| `satellite` | 작은 비중 실험 후보 | 아직 core로 보기 어렵지만 관찰 가치가 있을 때 |
| `watch_only` | 비중 없이 관찰만 하는 후보 | blocker가 남아 있거나 paper tracking 전일 때 |

## 비중 산정 원칙

초기 Phase 30에서는 복잡한 optimizer를 먼저 만들지 않는다.
먼저 사람이 이해 가능한 방식부터 지원한다.

| 방식 | 의미 | 초기 사용 여부 |
|---|---|---|
| `manual_weight` | 사람이 직접 비중을 정한다 | 우선 |
| `equal_weight` | 후보 수로 균등 배분한다 | 우선 |
| `role_based_weight` | core / diversifier / defensive 역할별 기본 범위를 둔다 | 후속 |
| `risk_budget_weight` | 변동성, MDD, downside 기준으로 비중을 조정한다 | 후속 |
| `optimizer_weight` | 수학적 최적화로 비중을 산정한다 | 당장 제외 |

초기 제안은 `manual_weight` 또는 `equal_weight`로 시작하고,
비중 이유를 `weight_reason`에 반드시 남긴다.

## 저장 전 차단 조건

아래 조건이 있으면 proposal을 `review_ready` 이상으로 올리지 않는다.

- 포함 후보의 `registry_id`가 없다.
- 후보별 `target_weight` 합계가 100%로 해석되지 않는다.
- 후보별 `proposal_role`이 비어 있다.
- `data_trust_status`가 missing이거나 error인데 blocker가 기록되지 않았다.
- `real_money_status`가 hold / blocked인데 비중이 core처럼 들어가 있다.
- `pre_live_status`가 rejected인데 active proposal에 포함되어 있다.
- proposal objective와 후보 구성이 맞지 않는다.
- proposal이 live approval이나 주문 지시처럼 표현되어 있다.

## Proposal lifecycle

```text
draft
  -> review_ready
  -> paper_tracking
  -> re_review
  -> hold / rejected / superseded
  -> live_readiness_candidate
```

- `draft`: 초안이다. 저장 전 검토 또는 임시 row다.
- `review_ready`: 필수 필드와 blocker 기록이 채워진 상태다.
- `paper_tracking`: 실제 돈 없이 관찰하는 상태다.
- `re_review`: 다시 검토해야 하는 상태다.
- `hold`: 아직 해결되지 않은 blocker가 있어 보류한다.
- `rejected`: 현재 기준으로 제안에서 제외한다.
- `superseded`: 더 최신 제안으로 대체되었다.
- `live_readiness_candidate`: 이후 별도 phase에서 live readiness 검토 대상으로 넘길 수 있는 상태다. 승인 자체는 아니다.

## 화면 구현 시 필요한 최소 readout

Portfolio Proposal UI를 구현할 때는 최소한 아래를 보여줘야 한다.

1. Proposal Objective
   - primary goal, secondary goal, capital scope, review cadence
2. Component Candidates
   - registry ID, strategy family, proposal role, target weight, weight reason
3. Evidence Snapshot
   - CAGR, MDD, benchmark, result period, data trust, Real-Money, Pre-Live status
4. Portfolio Construction
   - weighting method, date alignment, benchmark policy
5. Risk Constraints
   - max candidate weight, max family concentration, MDD / turnover / liquidity constraints
6. Open Blockers
   - data, strategy, Real-Money, Pre-Live, paper tracking blockers
7. Operator Decision
   - decision, reason, next action, review date

## 이번 작업에서 아직 하지 않는 것

- `.note/finance/PORTFOLIO_PROPOSAL_REGISTRY.jsonl` 파일 생성
- proposal append helper 구현
- Backtest UI에 Proposal tab 추가
- portfolio optimizer 구현
- live readiness approval 구현
- broker / order integration

## 다음 작업

다음 작업은 둘 중 하나가 자연스럽다.

1. Portfolio Proposal UI / persistence를 구현하기 전에 Candidate Review / registry helper를 모듈로 분리한다.
2. 위 계약을 기준으로 Proposal Draft UI와 저장소를 작은 범위로 구현한다.

현재 판단으로는 저장소와 UI를 만들기 전,
`current candidate registry` helper를 먼저 분리하면 Proposal 구현 때 같은 helper를 재사용하기 쉽다.
