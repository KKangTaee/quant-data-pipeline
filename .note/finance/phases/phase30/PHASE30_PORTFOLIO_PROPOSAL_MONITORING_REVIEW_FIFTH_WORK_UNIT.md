# Phase 30 Portfolio Proposal Monitoring Review Fifth Work Unit

## 이 문서는 무엇인가

Phase 30의 다섯 번째 작업 단위 기록이다.
네 번째 작업에서 저장할 수 있게 된 Portfolio Proposal draft를
다시 읽고 점검하는 `Monitoring Review` surface를 추가했다.

## 쉽게 말하면

이제 proposal draft를 저장한 뒤,
그 proposal이 어떤 후보들로 구성되어 있고,
target weight 합계가 어떤지,
blocker와 review gap이 무엇인지,
다음 행동과 review date가 무엇인지 한 화면에서 다시 볼 수 있다.

이 화면도 live trading 승인이나 주문 지시가 아니다.
저장된 proposal draft를 사람이 다시 읽고 점검하기 위한 review surface다.

## 왜 필요한가

Portfolio Proposal을 저장만 할 수 있으면,
시간이 지난 뒤 "이 proposal이 지금 어떤 상태였지?"를 다시 읽기 어렵다.

최종 목표는 포트폴리오 구성안과 가이드를 제시하는 것이므로,
proposal draft도 아래 관점으로 다시 확인할 수 있어야 한다.

- 후보 구성
- 후보별 proposal role
- target weight 합계
- Real-Money / Pre-Live 상태
- data trust review gap
- proposal blocker
- operator decision과 next action
- review date

## 바뀐 코드

변경된 파일:

- `app/web/pages/backtest.py`

추가된 것:

- `Backtest > Portfolio Proposal > Monitoring Review` tab
- proposal monitoring summary table
- selected proposal detail review
- component monitoring table
- blocker / review gap readout
- operator decision readout
- proposal JSON inspect expander

## UI 흐름

```text
PORTFOLIO_PROPOSAL_REGISTRY.jsonl
  -> Backtest > Portfolio Proposal
  -> Monitoring Review
  -> proposal monitoring summary 확인
  -> proposal 선택
  -> objective / construction / component table 확인
  -> blocker / review gap 확인
  -> operator decision / JSON inspect 확인
```

## Monitoring State 기준

현재 UI의 monitoring state는 live approval gate가 아니다.
저장된 proposal draft를 다시 읽기 위한 간단한 상태 요약이다.

| 상태 | 뜻 |
|---|---|
| `blocked` | proposal open blocker, component blocker, rejected pre-live active weight, blocked core anchor 같은 문제가 있다 |
| `needs_review` | blocker는 아니지만 data trust, pre-live status, review date 같은 추가 확인 gap이 있다 |
| `review_ready` | 저장된 정보 기준으로 blocker와 review gap이 보이지 않는다 |

## 의도적으로 바꾸지 않은 것

- proposal row append schema
- proposal draft 저장 방식
- current candidate registry
- pre-live registry
- saved portfolio replay
- live readiness approval
- broker / order integration
- automatic optimizer

## 검증 기준

- `python3 -m py_compile app/web/runtime/portfolio_proposal.py app/web/runtime/__init__.py app/web/pages/backtest.py`
- `.venv/bin/python` proposal monitoring helper smoke
- `python3 plugins/quant-finance-workflow/scripts/manage_current_candidate_registry.py validate`
- `python3 plugins/quant-finance-workflow/scripts/manage_pre_live_candidate_registry.py validate`
- `python3 plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py`
- `git diff --check`

## 현재 판단

Phase 30은 이제 proposal draft를 작성 / 저장하는 흐름뿐 아니라,
저장된 proposal을 다시 점검하는 monitoring review surface도 갖췄다.

아직 남은 것은 paper / pre-live tracking feedback을 proposal에 연결하는 더 깊은 monitoring과,
Candidate Review / Pre-Live / History / Saved Portfolio의 추가 `backtest.py` 모듈 분리다.
