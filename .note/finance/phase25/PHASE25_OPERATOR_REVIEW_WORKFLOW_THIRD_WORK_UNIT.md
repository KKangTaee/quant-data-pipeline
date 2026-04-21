# Phase 25 Operator Review Workflow Third Work Unit

## 이 문서는 무엇인가

이 문서는 `Phase 25`의 세 번째 작업 단위인
`Operator Review Workflow`를 정리한다.

두 번째 작업에서 Pre-Live 후보 기록소를 만들었다면,
이번 작업은 current candidate를 보고
`watchlist`, `paper_tracking`, `hold`, `reject`, `re_review` 중
어떤 운영 상태로 둘지 초안을 만드는 흐름이다.

## 쉽게 말하면

후보 자체는 이미 `CURRENT_CANDIDATE_REGISTRY.jsonl`에 있다.

이번 작업은 그 후보를 보고
"이건 실제 돈을 넣자는 뜻이 아니라, 일단 종이로 추적하자",
"이건 watchlist에만 두자",
"이건 blocker가 있으니 보류하자"를
Pre-Live 기록 초안으로 바꾸는 단계다.

## 왜 필요한가

Real-Money 신호를 보고 바로 사람이 수동으로 JSON을 쓰면
다음 문제가 생긴다.

- 상태값을 매번 다르게 쓸 수 있다.
- paper tracking과 watchlist의 차이가 흐려질 수 있다.
- 후보 원본과 Pre-Live 운영 기록이 연결되지 않을 수 있다.
- 나중에 왜 이 후보를 관찰했는지 복원하기 어렵다.

그래서 current candidate에서 Pre-Live 기록 초안을 만드는 helper entry point를 추가했다.

## 이번 작업에서 만든 것

`manage_pre_live_candidate_registry.py`에 아래 명령을 추가했다.

```bash
python3 plugins/quant-finance-workflow/scripts/manage_pre_live_candidate_registry.py draft-from-current <registry_id>
```

이 명령은 `CURRENT_CANDIDATE_REGISTRY.jsonl`의 후보를 읽어서
Pre-Live registry에 들어갈 JSON row 초안을 출력한다.

중요한 점:

- 기본값은 출력만 한다.
- 실제 저장은 하지 않는다.
- 운영자가 초안을 확인한 뒤 `--append`를 붙일 때만
  `.note/finance/PRE_LIVE_CANDIDATE_REGISTRY.jsonl`에 기록된다.

## 상태 추천 기준

helper는 Real-Money 신호를 보고 아래처럼 기본 상태를 추천한다.

| Real-Money 신호 | 기본 Pre-Live 상태 | 쉬운 뜻 |
|---|---|---|
| `shortlist = paper_probation` | `paper_tracking` | 실제 돈 없이 추적해 볼 후보 |
| `shortlist = small_capital_trial` | `paper_tracking` | 소액 실험 전, 먼저 종이 추적할 후보 |
| `shortlist = watchlist` | `watchlist` | 다시 볼 가치는 있지만 아직 paper tracking 전 |
| blocker가 있음 | `hold` | 문제를 풀기 전에는 진행하지 않음 |
| reject / fail 계열 신호 | `reject` | 현재 기준에서는 추적 종료 |
| 그 외 판단 애매한 경우 | `re_review` | 정해진 날짜에 다시 보기 |

이 추천은 자동 투자 판단이 아니다.
운영자가 `--pre-live-status`, `--operator-reason`, `--next-action`, `--review-date`로
수정할 수 있는 초안이다.

## 사용 예시

### 1. current candidate 목록 확인

```bash
python3 plugins/quant-finance-workflow/scripts/manage_current_candidate_registry.py list
```

### 2. Pre-Live 기록 초안 만들기

```bash
python3 plugins/quant-finance-workflow/scripts/manage_pre_live_candidate_registry.py draft-from-current value_current_anchor_top14_psr
```

### 3. 상태를 직접 바꿔 초안 만들기

```bash
python3 plugins/quant-finance-workflow/scripts/manage_pre_live_candidate_registry.py draft-from-current value_current_anchor_top14_psr --pre-live-status watchlist
```

### 4. 운영자가 확인한 뒤 실제 저장

```bash
python3 plugins/quant-finance-workflow/scripts/manage_pre_live_candidate_registry.py draft-from-current value_current_anchor_top14_psr --append
```

`--append`를 붙이면 실제 registry row가 추가된다.
따라서 단순 확인 중에는 붙이지 않는다.

## 이번 작업에서 하지 않은 것

- Backtest UI 안에 버튼을 추가하지 않았다.
- live trading이나 투자 승인 기능을 열지 않았다.
- 특정 후보를 실제 Pre-Live registry에 seed하지 않았다.

아직 실제 후보를 기록하려면 운영자가 초안을 보고 명시적으로 append해야 한다.

## 다음에 확인할 것

- 이 helper 기반 workflow만으로 충분한지,
  아니면 Backtest UI 안에 `Create Pre-Live Draft` 같은 버튼이 필요한지 확인한다.
- Pre-Live registry에 row가 쌓이면 dashboard 또는 summary view가 필요한지 검토한다.
- Phase 25 QA에서는 실제 append 전까지는 "초안 생성이 이해되는지"를 먼저 확인한다.

## 한 줄 정리

이번 작업은 current candidate를 Pre-Live 운영 기록 초안으로 바꾸는
안전한 report/helper 기반 진입점을 만든 것이다.
