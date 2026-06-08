# Strategy Promotion Contract Handoff Plan

Status: Active
Created: 2026-06-08
Owner worktree: `codex/main-dev`

## Goal

`backtest-dev`에서 분석, 개선, 추가 개발한 전략을 `main-dev`의 제품 workflow에 올리기 전에 확인해야 하는 `Strategy Promotion Contract`를 만든다.

## 이걸 하는 이유?

현재 제품은 `Backtest Analysis -> Practical Validation -> Final Review -> Operations > Portfolio Monitoring` 흐름을 가진다. 하지만 전략 연구 결과가 main 제품 workflow로 들어오기 전, 단순 성과 수치가 아니라 universe, PIT, survivorship, parameter / optimization, OOS / walk-forward, cost / liquidity, replay, generated artifact, known failure, `NOT_RUN` evidence를 명확히 확인하는 handoff 계약이 아직 별도 문서로 고정돼 있지 않다.

이 task의 가치는 `backtest-dev`의 전략 성과 개선과 `main-dev`의 제품 승격 판단을 분리해, 좋은 수익률만으로 Practical Validation / Final Review / Portfolio Monitoring에 진입하지 않게 하는 데 있다.

## Working Roadmap

| 차수 | 목적 | 바뀔 범위 | 완료 조건 | 다음 차수 연결 |
|---|---|---|---|---|
| 1차 | 현재 전략 handoff / backtest report / Practical Validation source 흐름 감사와 필수 필드 정의 | active task docs | handoff gap, 필수 필드, 이번 scope / out-of-scope가 문서화됨 | 2차 contract / template 작성 |
| 2차 | Strategy Promotion Contract 문서와 template 작성 | `reports/backtests/`, 필요한 durable docs | backtest-dev가 채워서 넘길 checklist / template과 기존 strategy hub 연결 기준이 생김 | 3차 helper / docs sync |
| 3차 | 최소 helper 또는 문서 중심 검증, docs sync, root handoff log, commit | helper script / tests, docs index / roadmap / root logs | 검증 가능한 contract와 coherent commit이 생김 | 다음 전략 handoff나 Risk-On Momentum 5D 예시 적용 |

## Scope

- 현재 제품 workflow와 report 구조를 감사한다.
- `backtest-dev -> main-dev` handoff에 필요한 필수 field와 gate state를 정의한다.
- Backtest report workspace에 전략 승격 contract와 reusable template을 추가한다.
- Risk-On Momentum 5D 같은 research lane을 제품 workflow로 승격할 때 필요한 예시 흐름을 설명한다.
- 필요 최소 수준의 helper를 추가해 template의 필수 section 누락을 빠르게 점검한다.
- durable docs, report index, root handoff logs를 필요한 범위에서 정렬한다.

## Out Of Scope

- 새 전략 개발 또는 전략 성과 개선.
- Risk-On Momentum 5D 또는 다른 전략의 제품 승인.
- Practical Validation / Final Review / Portfolio Monitoring UI redesign.
- live approval, broker order, account sync, auto rebalance.
- registry / saved JSONL 재작성.
- generated run history, screenshots, temp artifacts 커밋.
- Candidate Review / Portfolio Proposal / Candidate Library / Run History 삭제.

## Owner Skills

- Intake: `finance-task-intake`
- Backtest workflow boundary: `finance-backtest-web-workflow`
- Future strategy implementation only if needed: `finance-strategy-implementation`
- Closeout docs: `finance-doc-sync`

## Stop Condition

이 task는 Strategy Promotion Contract와 template이 생기고, 최소 검증 또는 문서 중심 검증을 통과하며, 관련 docs와 root handoff log가 정렬되고, coherent commit이 만들어지면 완료한다.
