# Practical Validation Source Context V1

Status: Active
Created: 2026-05-31

## 이걸 하는 이유?

Practical Validation은 Backtest Analysis에서 1차 통과한 후보가 실전 검토 가능한지 확인하는 단계다.
하지만 현재 Step 1은 성과 curve와 component snapshot만 보여줘서 사용자가 "이 후보가 어떤 전략이었고, 어떤 구성 규칙과 월별 선택 종목으로 만들어졌는지"를 다시 파악하기 어렵다.

## Scope

- Practical Validation Step 1에 strategy / construction brief를 추가한다.
- 새 source handoff에는 compact selection history snapshot을 보존한다.
- single strategy와 weighted mix 모두 component별 전략 / 비중 / 설정 / 선택 이력을 확인할 수 있게 한다.
- 기존 registry row는 재작성하지 않고, 선택 이력이 없는 과거 source에는 fallback 안내를 표시한다.

## Out Of Scope

- core strategy 계산 방식 변경
- DB schema 변경
- provider / holdings full row 저장
- Final Review gate 정책 변경
- live approval, broker order, auto rebalance

## Verification

- focused service contract tests
- Python compile checks for touched modules
- `git diff --check`
- Practical Validation UI change risk가 있으므로 가능한 범위에서 Browser QA
