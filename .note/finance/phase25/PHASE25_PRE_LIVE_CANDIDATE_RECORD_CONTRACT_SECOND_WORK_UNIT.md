# Phase 25 Pre-Live Candidate Record Contract Second Work Unit

## 이 문서는 무엇인가

이 문서는 Phase 25의 두 번째 작업 단위다.

첫 번째 작업에서 `Real-Money 검증 신호`와 `Pre-Live 운영 점검`의 차이를 정리했다.
이번 작업에서는 그 운영 점검을 실제로 남길 저장 포맷과 위치를 정한다.

## 쉽게 말하면

이제부터는 "이 후보가 좋아 보인다"에서 멈추지 않는다.

후보를 실전 전에 어떻게 둘 것인지,
예를 들어 `watchlist`, `paper_tracking`, `hold`, `reject`, `re_review` 중 어디에 둘 것인지
기록으로 남긴다.

## 왜 필요한가

후보가 늘어나면 사람이 기억하기 어렵다.

특히 아래 질문은 나중에 다시 보면 쉽게 사라진다.

- 왜 이 후보를 보고 있었나?
- 어떤 Real-Money 신호가 좋거나 나빴나?
- 지금 paper tracking 중인가, 그냥 watchlist인가?
- 어떤 blocker가 해결되어야 하나?
- 언제 다시 봐야 하나?

이번 작업은 이 질문들을 기계가 다시 읽을 수 있는 기록으로 남기는 기준을 만든다.

## 결정한 저장 위치

Pre-Live 후보 운영 기록은 별도 registry로 둔다.

| 구분 | 위치 | 역할 |
|---|---|---|
| Current candidate registry | `.note/finance/CURRENT_CANDIDATE_REGISTRY.jsonl` | 현재 후보, near-miss, scenario를 저장 |
| Pre-Live candidate registry | `.note/finance/PRE_LIVE_CANDIDATE_REGISTRY.jsonl` | 후보의 운영 상태와 다음 행동을 저장 |
| Pre-Live registry guide | `.note/finance/operations/PRE_LIVE_CANDIDATE_REGISTRY_GUIDE.md` | 사용법과 필드 설명 |
| Helper script | `plugins/quant-finance-workflow/scripts/manage_pre_live_candidate_registry.py` | template / list / show / append / validate |

## 왜 current candidate registry와 분리하는가

`CURRENT_CANDIDATE_REGISTRY.jsonl`은 후보 자체의 기준점이다.

예를 들면:

- Value current anchor
- GTAA paper candidate
- Quality cleaner alternative
- lower-MDD near miss

`PRE_LIVE_CANDIDATE_REGISTRY.jsonl`은 그 후보를 보고 사람이 내린 운영 판단이다.

예를 들면:

- 이 후보는 `paper_tracking`으로 올린다.
- 이 후보는 데이터 보강 전까지 `hold`로 둔다.
- 이 후보는 2026-05-31에 `re_review`한다.

둘을 합치면 후보 정의와 운영 판단이 섞인다.
그래서 분리하고, 필요한 경우 `source_candidate_registry_id`로 연결한다.

## Pre-Live record 최소 계약

Pre-Live record에는 아래 필드가 필요하다.

| 필드 | 뜻 |
|---|---|
| `pre_live_id` | Pre-Live 운영 기록의 stable id |
| `record_status` | registry row 자체의 상태. `active`, `superseded`, `archived` |
| `source_kind` | 어디서 온 후보인지 |
| `source_ref` | 원본 report, registry, saved portfolio 등 |
| `source_candidate_registry_id` | current candidate registry에서 넘어온 경우 원본 id |
| `title` | 사람이 읽는 후보 이름 |
| `strategy_or_bundle` | 단일 전략인지, portfolio인지, saved portfolio인지 |
| `settings_snapshot` | 후보를 다시 찾거나 재현하는 데 필요한 설정 요약 |
| `result_snapshot` | CAGR, MDD, Sharpe, End Balance 같은 결과 요약 |
| `real_money_signal` | promotion, shortlist, deployment, blocker 같은 Real-Money 진단 |
| `pre_live_status` | `watchlist`, `paper_tracking`, `hold`, `reject`, `re_review` |
| `operator_reason` | 왜 이 상태로 두었는지 |
| `next_action` | 다음에 해야 할 일 |
| `review_date` | 다시 볼 날짜 |
| `tracking_plan` | paper tracking 기간, 중단 조건, 성공 조건 |
| `docs` | 관련 문서 링크 |

## 상태값 기준

| 상태 | 쓰는 경우 |
|---|---|
| `watchlist` | 다시 볼 가치는 있지만 paper tracking 전 |
| `paper_tracking` | 실제 돈 없이 일정 기간 관찰 |
| `hold` | blocker가 있어 지금은 진행하지 않음 |
| `reject` | 현재 기준에서는 추적 종료 |
| `re_review` | 날짜나 조건이 지나면 다시 보기로 예약 |

## 이번 작업에서 구현한 것

- Pre-Live record schema를 문서화했다.
- `.note/finance/PRE_LIVE_CANDIDATE_REGISTRY.jsonl`을 canonical 저장 위치로 정했다.
- `manage_pre_live_candidate_registry.py` helper를 추가했다.
- `operations/PRE_LIVE_CANDIDATE_REGISTRY_GUIDE.md`를 추가했다.
- 기존 current candidate registry와 역할이 겹치지 않도록 분리 기준을 고정했다.

## 이번 작업에서 아직 하지 않은 것

- Backtest UI에서 바로 Pre-Live 기록을 생성하는 버튼은 아직 만들지 않았다.
- 실제 후보 row를 seed하지 않았다.
- Phase 25 dashboard는 아직 만들지 않았다.

이유:

- 먼저 기록 계약과 저장 위치가 안정되어야 UI를 붙일 때 덜 흔들린다.
- 실제 후보를 어떤 상태로 올릴지는 사용자의 검토 또는 별도 분석 요청이 필요하다.

## 다음 작업

다음 작업은 operator review workflow를 구체화하는 것이다.

구체적으로는:

- 어떤 Real-Money 신호면 `watchlist`인지
- 어떤 경우 `paper_tracking`으로 올릴 수 있는지
- 어떤 blocker가 있으면 `hold`인지
- `Backtest` 결과에서 Pre-Live 기록으로 넘기는 UI가 필요한지

를 정한다.

## 한 줄 정리

이번 작업은 Pre-Live 후보를 실제로 저장할 수 있게,
`CURRENT_CANDIDATE_REGISTRY`와 분리된 운영 기록소와 최소 record 계약을 만든 것이다.
