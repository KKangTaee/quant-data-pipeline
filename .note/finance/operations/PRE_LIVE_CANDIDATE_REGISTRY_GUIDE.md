# Pre-Live Candidate Registry Guide

## 이 문서는 무엇인가

이 문서는 `.note/finance/registries/PRE_LIVE_CANDIDATE_REGISTRY.jsonl`을
어떤 용도로 쓰고, 기존 `CURRENT_CANDIDATE_REGISTRY.jsonl`과 어떻게 구분하는지 설명한다.

## 쉽게 말하면

`CURRENT_CANDIDATE_REGISTRY.jsonl`은
"지금 다시 볼 만한 후보가 무엇인가"를 저장한다.

`PRE_LIVE_CANDIDATE_REGISTRY.jsonl`은
"그 후보를 실전 전에 어떻게 관찰하고 보류하고 다시 볼 것인가"를 저장한다.

즉 하나는 후보 목록이고, 다른 하나는 운영 노트다.

## 왜 필요한가

백테스트 결과가 좋거나 Real-Money 신호가 괜찮아도
바로 투자 승인으로 넘어가면 안 된다.

Pre-Live 단계에서는 아래 내용이 남아야 한다.

- 왜 이 후보를 보고 있는지
- 어떤 Real-Money 신호를 근거로 삼았는지
- 지금 상태가 watchlist인지, paper tracking인지, hold인지
- 다음에 무엇을 해야 하는지
- 언제 다시 볼 것인지
- 어떤 주기로 확인할 것인지
- 어떤 조건이면 중단하거나 다음 단계로 갈 것인지

이 정보를 Markdown 문서에만 두면 나중에 자동화하거나 한눈에 모아 보기 어렵다.
그래서 JSONL 기반 registry를 별도로 둔다.

## 상태값과 다음 행동 기록의 차이

`watchlist`, `paper_tracking`, `hold`, `reject`, `re_review`는 상태값이다.
이 값만 보면 Real-Money의 promotion / shortlist 단계와 비슷하게 보일 수 있다.

Pre-Live registry가 따로 필요한 이유는 상태값 때문만이 아니다.
진짜 핵심은 아래 action package를 함께 남기는 것이다.

| 항목 | 역할 |
|---|---|
| `operator_reason` | 왜 이 상태로 두었는지 설명한다. |
| `next_action` | 다음에 무엇을 확인하거나 실행할지 적는다. |
| `review_date` | 다시 볼 날짜를 남긴다. |
| `tracking_plan.cadence` | 얼마나 자주 확인할지 정한다. |
| `tracking_plan.stop_condition` | 어떤 조건이면 추적을 멈출지 정한다. |
| `tracking_plan.success_condition` | 어떤 조건이면 다음 review 단계로 갈지 정한다. |

즉 Real-Money는 "진단 결과"이고,
Pre-Live는 "진단 결과를 본 뒤의 운영 계획"이다.

## 파일 위치

| 구분 | 위치 | 역할 |
|---|---|---|
| Current candidate registry | `.note/finance/registries/CURRENT_CANDIDATE_REGISTRY.jsonl` | current anchor, near-miss, scenario 후보 저장 |
| Pre-Live candidate registry | `.note/finance/registries/PRE_LIVE_CANDIDATE_REGISTRY.jsonl` | 후보의 pre-live 운영 상태 저장 |
| Helper script | `plugins/quant-finance-workflow/scripts/manage_pre_live_candidate_registry.py` | template / draft-from-current / list / show / append / validate |
| UI | `Backtest > Pre-Live Review` | current candidate 선택, Pre-Live 초안 확인, 저장 record inspect |

`PRE_LIVE_CANDIDATE_REGISTRY.jsonl`은 첫 row를 append할 때 생성된다.
아직 row가 없으면 helper의 `validate` 명령은 "empty"로 통과한다.

## 저장해야 하는 핵심 필드

| 필드 | 뜻 |
|---|---|
| `pre_live_id` | Pre-Live 기록의 stable id |
| `source_kind` | 어디서 온 후보인지. 예: `current_candidate_registry`, `backtest_run`, `saved_portfolio`, `backtest_report`, `manual_review` |
| `source_candidate_registry_id` | current candidate registry에서 넘어온 경우 원본 id |
| `strategy_or_bundle` | 단일 전략인지, portfolio bundle인지, saved portfolio인지 |
| `settings_snapshot` | 후보를 다시 찾거나 재현하는 데 필요한 핵심 설정 |
| `result_snapshot` | CAGR, MDD, Sharpe, End Balance 같은 결과 요약 |
| `real_money_signal` | promotion, shortlist, deployment, blocker 같은 Real-Money 진단 |
| `pre_live_status` | `watchlist`, `paper_tracking`, `hold`, `reject`, `re_review` 중 하나 |
| `operator_reason` | 왜 이 상태로 두었는지 사람이 읽는 설명 |
| `next_action` | 다음에 해야 할 일 |
| `review_date` | 다시 볼 날짜. `re_review`에는 필수 |
| `tracking_plan` | paper tracking cadence, 중단 조건, 성공 조건 |
| `docs` | 관련 Markdown report나 strategy hub |

## Pre-Live 상태값

| 상태 | 뜻 | 대표 상황 |
|---|---|---|
| `watchlist` | 다시 볼 가치는 있지만 아직 paper tracking 전 | 설정 안정성이나 최근성 확인이 더 필요함 |
| `paper_tracking` | 실제 돈 없이 정해진 기간 관찰 | Real-Money 신호가 크게 나쁘지 않고 관찰 가치가 있음 |
| `hold` | 지금은 진행하지 않음 | 데이터 결측, 과도한 MDD, 비용, 구조 설명 부족 등 blocker가 있음 |
| `reject` | 현재 기준에서는 추적 종료 | 목적에 맞지 않거나 반복 검증에서 부적합 |
| `re_review` | 특정 날짜나 조건 이후 다시 확인 | 데이터가 더 쌓인 뒤 보거나 이벤트 이후 재검토 |

## 기본 사용 방법

### 0. Backtest UI에서 사용

앱 화면에서는 `Backtest > Pre-Live Review`에서 사용할 수 있다.

- `Create From Current Candidate`: current candidate를 골라 Pre-Live 초안을 확인하고 저장한다.
- `Pre-Live Registry`: 저장된 active Pre-Live record를 확인한다.

이 화면도 투자 승인 화면이 아니다.
`Save Pre-Live Record`는 실전 주문이 아니라 운영 기록 저장이다.

### 1. JSON template 확인

```bash
python3 plugins/quant-finance-workflow/scripts/manage_pre_live_candidate_registry.py template
```

### 2. registry 검증

```bash
python3 plugins/quant-finance-workflow/scripts/manage_pre_live_candidate_registry.py validate
```

### 3. 현재 active Pre-Live 기록 보기

```bash
python3 plugins/quant-finance-workflow/scripts/manage_pre_live_candidate_registry.py list
```

### 4. 특정 기록 상세 보기

```bash
python3 plugins/quant-finance-workflow/scripts/manage_pre_live_candidate_registry.py show example_pre_live_candidate_id
```

### 5. 새 기록 추가

```bash
python3 plugins/quant-finance-workflow/scripts/manage_pre_live_candidate_registry.py append --json-file path/to/pre_live_row.json
```

### 6. current candidate에서 Pre-Live 초안 만들기

```bash
python3 plugins/quant-finance-workflow/scripts/manage_pre_live_candidate_registry.py draft-from-current value_current_anchor_top14_psr
```

이 명령은 `CURRENT_CANDIDATE_REGISTRY.jsonl`의 후보를 읽어서
Pre-Live 기록 초안을 출력한다.
기본값은 출력만 하며, 실제 registry에는 저장하지 않는다.

운영자가 초안을 확인한 뒤 실제로 저장하려면 아래처럼 `--append`를 붙인다.

```bash
python3 plugins/quant-finance-workflow/scripts/manage_pre_live_candidate_registry.py draft-from-current value_current_anchor_top14_psr --append
```

주의:

- `--append`는 실제 운영 기록을 남기는 명령이다.
- 단순 확인이나 QA 중에는 `--append` 없이 초안만 확인한다.
- 상태를 직접 바꾸려면 `--pre-live-status watchlist`처럼 override한다.

## 상태 추천 기준

`draft-from-current`는 current candidate의 Real-Money 신호를 읽어
기본 Pre-Live 상태를 추천한다.

| Real-Money 신호 | 추천 상태 | 뜻 |
|---|---|---|
| `shortlist = paper_probation` | `paper_tracking` | 실제 돈 없이 추적해 볼 후보 |
| `shortlist = small_capital_trial` | `paper_tracking` | 소액 검토 전 먼저 종이 추적할 후보 |
| `shortlist = watchlist` | `watchlist` | 다시 볼 가치는 있지만 아직 paper tracking 전 |
| blocker가 있음 | `hold` | 문제를 풀기 전에는 진행하지 않음 |
| reject / fail 계열 신호 | `reject` | 현재 기준에서는 추적 종료 |
| 그 외 판단 애매한 경우 | `re_review` | 정해진 날짜에 다시 보기 |

이 추천은 자동 승인이나 투자 판단이 아니다.
초안을 빠르게 만들기 위한 운영 보조 규칙이며,
운영자가 이유와 다음 행동을 수정할 수 있다.

## 운영 기준

- 이 registry는 투자 승인 장부가 아니다.
- `pre_live_status = paper_tracking`이어도 실제 돈을 넣는다는 뜻이 아니다.
- live deployment 판단은 Phase 25 이후 별도의 deployment readiness review에서 다룬다.
- 현재 후보 자체를 업데이트하려면 `CURRENT_CANDIDATE_REGISTRY.jsonl`을 본다.
- 후보의 운영 상태를 업데이트하려면 `PRE_LIVE_CANDIDATE_REGISTRY.jsonl`을 본다.

## 한 줄 정리

Pre-Live registry는 **좋아 보이는 후보를 바로 투자로 넘기지 않고,
watchlist / paper tracking / hold / reject / re-review로 관리하기 위한 운영 기록소**다.
