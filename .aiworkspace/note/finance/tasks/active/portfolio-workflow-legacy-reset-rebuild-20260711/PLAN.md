# Portfolio Workflow Legacy Reset / Rebuild

Status: Active
Date: 2026-07-11

## 이걸 하는 이유?

현재 Final Review와 Portfolio Monitoring에 남아 있는 6개 포트폴리오는 2026-06-01~09 사이의 저장 계약으로 만들어져, 최신 Practical Validation의 `review_role`과 workspace 근거를 포함하지 않는다. 같은 후보를 현재 1차 승격 → 2차 검증 → 3차 판단 흐름으로 다시 생성해 최신 화면 계약으로 읽히게 한다.

## Scope

- 현재 `FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl`의 6개 후보를 재구성 대상으로 식별한다.
- active selection / validation / final decision / monitoring setup 파일은 작업 전 workspace 밖에 백업한다.
- 기존 active legacy rows를 제거하고 각 후보를 현재 workflow service로 다시 생성한다.
- 실제 Gate를 통과한 후보만 Final Review 판단과 Monitoring setup으로 연결한다.
- 기존 `SAVED_PORTFOLIOS.jsonl` reusable setup은 3단계 후보 체인과 별개이므로 참조 여부를 확인한 뒤 요청 범위에 맞춰 정리한다.
- run history, QA screenshot, generated artifact는 stage하지 않는다.

## Stop Condition

- 6개 후보의 재실행 결과와 승격 가능 여부가 확인된다.
- 새 Practical Validation rows에 현재 workspace / `review_role` 계약이 존재한다.
- Final Review와 Portfolio Monitoring이 새 IDs만 읽는다.
- focused tests, compile, diff check, Browser QA가 완료된다.
