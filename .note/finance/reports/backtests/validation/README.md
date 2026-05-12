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
| `PHASE23_QUARTERLY_CONTRACT_SMOKE_VALIDATION_FIRST_PASS.md` | `runtime/` | quarterly contract가 DB-backed runtime과 result meta에 보존되는지 검증 |
| `PHASE24_GLOBAL_RELATIVE_STRENGTH_CORE_RUNTIME_SMOKE_VALIDATION.md` | `runtime/` | Global Relative Strength core/runtime smoke 검증 |
| `PHASE24_GLOBAL_RELATIVE_STRENGTH_UI_REPLAY_SMOKE_VALIDATION.md` | `ui_replay/` | Global Relative Strength UI, compare, history, saved replay 연결 검증 |
