# Backtest Validation Reports

Status: Active
Last Verified: 2026-05-12

이 폴더는 투자 성과 탐색 report가 아니라, backtest runtime이나 UI replay가 의도대로 작동했는지 확인한 report를 보관한다.

| 위치 | 용도 |
|---|---|
| `runtime/` | engine/runtime smoke, saved source replay, benchmark parity 검증 |
| `ui_replay/` | Streamlit 화면에서 저장된 source가 재현되는지 확인 |

## Classified Legacy Reports

| Report | 위치 | 의미 |
|---|---|---|
| `WEIGHTED_PORTFOLIO_REPLAY_VALIDATION.md` | `runtime/` | 여러 전략 결과를 weighted portfolio로 묶고 saved replay로 재현하는 workflow 검증 |
| `QUARTERLY_CONTRACT_RUNTIME_SMOKE.md` | `runtime/` | quarterly contract가 DB-backed runtime과 result meta에 보존되는지 검증 |
| `GLOBAL_RELATIVE_STRENGTH_RUNTIME_SMOKE.md` | `runtime/` | Global Relative Strength core/runtime smoke 검증 |
| `GLOBAL_RELATIVE_STRENGTH_UI_REPLAY_SMOKE.md` | `ui_replay/` | Global Relative Strength UI, compare, history, saved replay 연결 검증 |
