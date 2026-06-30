# Fundamental Source Migration P8 - Final Docs / Runbook Alignment

## 이걸 하는 이유?

1차부터 8차까지 코드와 UI 경계가 바뀌었으므로, 다음 세션이 예전 `nyse_fundamentals` / yfinance broad path를 production financial statement source로 다시 해석하지 않게 durable docs를 정렬한다.

## Scope

- Mark EDGAR annual statement shadow as the canonical financial statement source path.
- Mark broad yfinance fundamentals / factors as legacy compatibility for saved/history replay and explicit comparison.
- Record quarterly policy: do not use 10-K/FY full-year flow values as quarterly rows; consume quarterly only through 10-Q / 10-Q/A gates.
- Align docs index, roadmap, project map, data maps, runbooks, task manifests, and root handoff logs.

## Out Of Scope

- Code behavior changes.
- Table drop or schema deletion.
- Registry / saved JSONL rewrite.
- New provider approval or paid normalized provider selection.

## Done Criteria

- Durable docs no longer read as if `nyse_fundamentals` is the production financial statement source.
- Runbook points operators to EDGAR annual refresh, statement shadow rebuild, and coverage QA.
- Phase 8 verification commands pass.
