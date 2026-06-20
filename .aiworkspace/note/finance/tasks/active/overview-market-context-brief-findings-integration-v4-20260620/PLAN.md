# Overview Market Context Brief Findings Integration V4

Status: Completed
Date: 2026-06-20

## Why

사용자가 `맥락 검토 결과`를 실제 사용해 본 뒤, P1/P2는 이미 `오늘의 시장 브리프`에 있는 가격 움직임 / Futures-Macro 맥락과 중복되고, P3/P4인 Events / 자료 신뢰도 caveat만 오늘 브리프 안으로 올리는 편이 맞다고 지적했다.

## Scope

- `Workspace > Overview > Market Context`
- `app/services/overview_market_intelligence.py`
- `app/web/overview_ui_components.py`
- `app/web/overview_dashboard.py`
- `tests/test_service_contracts.py`

## Done Criteria

- `오늘의 시장 브리프`가 움직임, 확산, Futures/Macro 배경, 이벤트 caveat, 자료 신뢰도 caveat를 한 흐름으로 보여준다.
- 기본 Market Context 화면에서 별도 `맥락 검토 결과` 레일이 다시 나오지 않는다.
- `context_findings` / `next_checks` compatibility payload는 유지하되 user-facing action checklist로 렌더링하지 않는다.
- Historical analog 기준 컨트롤과 근거 / 출처 상태 흐름은 유지한다.

## Out Of Scope

- 새 provider / schema / loader / persistence path
- UI render 중 external fetch
- FRED / events / sentiment hard conditioning
- registry / saved JSONL write
- Backtest / Practical Validation / Final Review / Operations core logic
- trade signal / 추천 / validation gate / monitoring signal
