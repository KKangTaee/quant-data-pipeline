# Practical Validation Flow 3/4 Handoff Style V2 Plan

## 이걸 하는 이유?

Flow 3는 Final Review 이동 가능 여부를 빠르게 판단하는 판정판이어야 하고, Flow 4는 그 판단의 기준별 근거를 확인하는 상세 보드여야 한다.
후보분석의 Handoff / 검증 기준 상세 UI가 가진 읽기 순서를 Practical Validation에 맞게 재해석해, 사용자가 "갈 수 있는지"와 "무엇부터 고칠지"를 더 빨리 판단하게 한다.

## Scope

- Flow 3: Final Review 이동 판단, 먼저 해결할 일, 다음 단계, Flow 5 저장 경계 안내를 한 화면에서 읽게 한다.
- Flow 4: `Source Readiness`, `Validation Readiness`, `Final Review Readiness Preview`, 조건부 근거를 기준 상세 보드처럼 정리한다.
- Gate threshold, replay 실행, provider 수집, registry / saved JSONL persistence는 변경하지 않는다.

## Steps

1. Add failing tests for Flow 3 / Flow 4 UI contract and workspace read model.
2. Extend `backtest_practical_validation_workspace.py` with criteria detail groups and summary metrics.
3. Redesign `practical_validation_fix_queue` React surface around the decision board pattern.
4. Add a Flow 4 criteria detail board before detailed tabs and provider actions.
5. Run focused Python tests, React build, compile checks, browser QA.
6. Sync durable docs and commit.
