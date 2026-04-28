# Phase 30 Portfolio Proposal Paper Tracking Feedback Seventh Work Unit

## 이 문서는 무엇인가

Phase 30의 일곱 번째 작업 단위 기록이다.
저장된 Portfolio Proposal draft를 최신 Pre-Live record의
`result_snapshot`과 비교하는 `Paper Tracking Feedback` surface를 추가했다.

## 쉽게 말하면

proposal을 저장한 뒤 후보가 `paper_tracking` 상태로 관찰되면,
저장 당시의 CAGR / MDD와 현재 Pre-Live record에 남은 CAGR / MDD를 다시 비교해야 한다.

이번 작업은 `Backtest > Portfolio Proposal > Paper Tracking Feedback`에서
proposal component별 saved CAGR / MDD, current CAGR / MDD, delta,
tracking plan, feedback gap을 한 화면에 보여준다.

이 화면은 실제 paper PnL을 자동 계산하지 않는다.
현재는 Pre-Live record에 저장된 최신 `result_snapshot`을 읽어,
proposal 관점에서 성과가 악화됐는지 또는 paper tracking 상태가 아닌 후보가 섞였는지 확인한다.

## 왜 필요한가

Portfolio Proposal은 최종 목표인 실전 포트폴리오 제안으로 가기 전 단계다.
하지만 proposal을 만들고 나서 paper tracking 성과를 다시 보지 않으면,
저장 당시에는 좋아 보였던 후보가 이후 관찰 상태에서 악화됐는지 놓칠 수 있다.

최종적으로 실제 돈을 넣을 수 있는 포트폴리오와 가이드를 제시하려면,
proposal이 현재 paper tracking 기록과 성과 피드백을 함께 읽을 수 있어야 한다.

## 이 작업이 끝나면 좋은 점

- proposal component가 실제로 `paper_tracking` 상태인지 한눈에 확인할 수 있다.
- proposal 저장 당시 성과와 현재 Pre-Live snapshot 성과의 차이를 볼 수 있다.
- CAGR / MDD 악화, missing result, paper tracking 미진입 같은 gap을 QA에서 직접 확인할 수 있다.
- Phase 30이 Portfolio Proposal / Pre-Live Monitoring surface의 구현 단위를 마무리하고 manual QA로 넘어갈 수 있다.

## 바뀐 코드

변경된 파일:

- `app/web/pages/backtest.py`

추가된 것:

- `Backtest > Portfolio Proposal > Paper Tracking Feedback` tab
- proposal별 paper tracking feedback summary table
- proposal component별 saved/current CAGR, saved/current MDD, delta readout
- `Performance Signal`
  - `needs_paper_tracking`
  - `missing_current_result`
  - `missing_saved_snapshot`
  - `worsened`
  - `stable_or_better`
- tracking cadence / stop condition / success condition 표시
- feedback gap readout

## UI 흐름

```text
PORTFOLIO_PROPOSAL_REGISTRY.jsonl
  + PRE_LIVE_CANDIDATE_REGISTRY.jsonl
  -> Backtest > Portfolio Proposal
  -> Paper Tracking Feedback
  -> proposal 선택
  -> proposal evidence snapshot과 current Pre-Live result snapshot 비교
  -> CAGR / MDD delta, performance signal, tracking plan 확인
```

## Feedback Gap 기준

현재 UI는 아래를 feedback gap으로 표시한다.

- proposal component에 연결된 active Pre-Live record가 없음
- current Pre-Live status가 `paper_tracking`이 아님
- proposal evidence snapshot에 CAGR 또는 MDD가 없음
- current Pre-Live result snapshot에 CAGR 또는 MDD가 없음
- CAGR delta가 `-2.0` 이하로 악화됨
- MDD delta가 `-5.0` 이하로 악화됨
- `paper_tracking` 상태인데 tracking cadence가 없음

Delta는 `current Pre-Live result snapshot - proposal evidence snapshot`이다.
MDD는 음수이므로 더 음수로 내려가면 악화로 읽는다.

## 의도적으로 바꾸지 않은 것

- 실제 paper PnL 자동 계산
- proposal row 자동 수정
- pre-live registry 자동 수정
- current candidate registry 자동 수정
- live readiness approval
- final approval checklist
- broker / order integration
- portfolio optimizer

## 검증 기준

- `python3 -m py_compile app/web/runtime/portfolio_proposal.py app/web/runtime/__init__.py app/web/pages/backtest.py`
- `.venv/bin/python` Paper Tracking Feedback helper smoke
- `python3 plugins/quant-finance-workflow/scripts/manage_current_candidate_registry.py validate`
- `python3 plugins/quant-finance-workflow/scripts/manage_pre_live_candidate_registry.py validate`
- `python3 plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py`
- `git diff --check`
- 브라우저 smoke에서 `Backtest > Portfolio Proposal > Paper Tracking Feedback` tab 노출 확인

## 현재 판단

Phase 30은 proposal draft 작성 / 저장,
Monitoring Review,
Pre-Live Feedback,
Paper Tracking Feedback까지 구현되었다.

따라서 Phase 30의 제품 기능 단위는 manual QA로 넘길 수 있는 상태다.
`backtest.py` 추가 모듈 분리는 Phase 30 QA와 섞지 않고,
별도 special refactor task로 여는 것이 안전하다.
