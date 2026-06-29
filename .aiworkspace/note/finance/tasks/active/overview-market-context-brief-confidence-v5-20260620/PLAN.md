# Overview Market Context Brief Confidence V5

Status: Completed
Date: 2026-06-20

## Why

V4에서 Events / 자료 신뢰도 caveat를 `오늘의 시장 브리프` 안으로 올렸지만, 사용자가 실제 화면을 확인한 뒤 이 두 항목이 시장 브리프의 결론처럼 보이고 "그래서 무엇을 내포하는지" 알기 어렵다고 지적했다.

## Scope

- `Workspace > Overview > Market Context`
- `app/services/overview_market_intelligence.py`
- `app/web/overview_ui_components.py`
- `tests/test_service_contracts.py`

## Done Criteria

- `오늘의 시장 브리프`는 시장 움직임, 확산/집중, Futures/Macro 배경의 3행 market story로 유지한다.
- Events / 자료 신뢰도는 별도 `브리프 신뢰도` 영역으로 분리해, 시장 결론이 아니라 오늘 브리프를 얼마나 강하게 읽을지 조절하는 근거로 표시한다.
- `이벤트 caveat`, `자료 신뢰도 caveat`, `다음 맥락 체크`, `맥락 검토 결과` 같은 action checklist / rail 문구는 기본 Market Context 화면에 다시 나타나지 않는다.
- `context_findings` / `next_checks` compatibility payload는 유지하되, 기본 user-facing checklist로 렌더링하지 않는다.

## Out Of Scope

- 새 provider / schema / loader / persistence path
- UI render 중 external fetch
- FRED / events / sentiment hard conditioning
- registry / saved JSONL write
- Backtest / Practical Validation / Final Review / Operations core logic
- trade signal / 추천 / validation gate / monitoring signal
