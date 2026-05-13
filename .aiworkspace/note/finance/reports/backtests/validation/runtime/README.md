# Runtime Validation Reports

Status: Ready
Last Verified: 2026-05-12

Backtest engine, replay runtime, Practical Validation runtime smoke report를 둔다.

성과 후보 report와 섞지 않는다.

## Reports

| Report | Purpose |
|---|---|
| [WEIGHTED_PORTFOLIO_REPLAY_VALIDATION.md](./WEIGHTED_PORTFOLIO_REPLAY_VALIDATION.md) | 여러 전략 결과를 weighted portfolio로 묶고 save / replay 결과가 재현되는지 확인 |
| [QUARTERLY_CONTRACT_RUNTIME_SMOKE.md](./QUARTERLY_CONTRACT_RUNTIME_SMOKE.md) | quarterly strict family의 portfolio handling contract가 runtime meta에 보존되는지 확인 |
| [GLOBAL_RELATIVE_STRENGTH_RUNTIME_SMOKE.md](./GLOBAL_RELATIVE_STRENGTH_RUNTIME_SMOKE.md) | Global Relative Strength core strategy와 DB-backed runtime wrapper가 result bundle을 생성하는지 확인 |
