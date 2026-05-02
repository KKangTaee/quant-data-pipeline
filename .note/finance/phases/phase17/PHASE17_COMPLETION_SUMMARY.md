# Phase 17 Completion Summary

## 목적

- Phase 17 `Structural Downside Improvement`를 practical closeout 기준으로 정리한다.
- 이번 phase에서 실제로 무엇을 구현했고,
  current anchor를 바꿀 정도의 same-gate lower-MDD rescue가 있었는지 분명히 남긴다.

## 이번 phase에서 실제로 완료된 것

### 1. structural lever inventory를 current code 기준으로 고정

- strict annual family에서 current practical 질문은
  bounded `Top N` / one-factor tweak 반복이 아니라
  **구조 레버를 실제로 여는 것**이라는 점을 정리했다.
- current code 기준 first three levers:
  - `partial cash retention`
  - `defensive sleeve risk-off`
  - `concentration-aware weighting`

### 2. `partial cash retention` 구현과 representative rerun 완료

- trend filter partial rejection 시
  rejected slot share를 현금으로 남길 수 있게 했다.
- representative rerun 결과:
  - downside는 크게 줄었지만
  - cash drag가 너무 커서
    current gate를 유지한 practical rescue까지는 못 갔다.

### 3. `defensive sleeve risk-off` 구현과 representative rerun 완료

- full risk-off를 `cash_only` 대신
  `BIL / SHY / LQD` sleeve로 돌릴 수 있게 했다.
- representative rerun 결과:
  - gate는 유지됐다
  - 하지만 `MDD`를 더 낮추지 못했다.

### 4. `concentration-aware weighting` 구현과 representative rerun 완료

- `Weighting Contract`
  - `Equal Weight`
  - `Rank-Tapered`
  를 strict annual family 3종에 연결했다.
- representative rerun 결과:
  - gate는 유지됐다
  - 하지만 `Value`, `Quality + Value` current anchor 모두
    `MDD`는 더 좋아지지 않았다.

### 5. strategy hub / backtest log / index / phase 문서 동기화

- strategy hub
- strategy backtest log
- current practical candidate summary
- phase17 archive report
- glossary / doc index / roadmap / concise logs

을 current conclusion 기준으로 맞췄다.

## 이번 phase를 practical closeout으로 보는 이유

- current code 기준 structural lever 3개가 모두 구현됐다
- 각 레버에 대해 representative rerun까지 끝나서
  “실제로 current anchor를 바꾸는가”를 확인했다
- 공통 결론이 분명하다:
  - same-gate lower-MDD exact rescue는 아직 없다
  - `Value` current anchor는 그대로 유지
  - `Quality + Value` current strongest practical point도 그대로 유지

즉 Phase 17의 핵심 목표였던
**“어떤 structural lever를 먼저 열고,
그 결과가 current anchor를 바꿀 정도인지 확인하는 일”**
은 practical 기준으로 달성되었다.

## 아직 남아 있지만 closeout blocker는 아닌 것

- operator workflow bridge를 next phase에서 병행할지 최종 결정
- current 3개 lever 이후 더 큰 구조 레버를 설계할지 판단
- `Value` / `Quality + Value` same-gate lower-MDD rescue를 위한
  더 큰 구조 실험

## guidance / reference review 결과

closeout 시점에 아래를 다시 확인했다.

- `README.md`
- `.note/finance/MASTER_PHASE_ROADMAP.md`
- `.note/finance/FINANCE_DOC_INDEX.md`
- `.note/finance/backtest_reports/BACKTEST_REPORT_INDEX.md`
- `.note/finance/phases/phase17/README.md`
- `plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py`

결론:

- 이번 phase에서 새 운영 규칙을 더 추가할 필요는 없었다
- 대신 phase closeout 기준으로
  roadmap / index / concise logs / report index를 동기화한다

## closeout 판단

현재 기준으로:

- structural lever inventory:
  - `completed`
- first three implementation slices:
  - `completed`
- representative rerun and document sync:
  - `completed`
- next lever prioritization:
  - `prepared`

즉 Phase 17은
**practical closeout / manual_validation_pending** 상태로 닫는 것이 맞다.
