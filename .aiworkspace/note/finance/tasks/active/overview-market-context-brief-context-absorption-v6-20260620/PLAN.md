# Overview Market Context Brief Context Absorption V6

Status: Completed
Date: 2026-06-20

## Why

V5에서 `브리프 신뢰도`를 분리했지만, 사용자가 실제 화면을 검토한 뒤 이 섹션이 시장맥락 자체가 아니라 또 다른 가이드/주의사항처럼 보인다고 지적했다.

## Scope

- `Workspace > Overview > Market Context`
- `app/services/overview_market_intelligence.py`
- `app/web/overview_ui_components.py`
- `tests/test_service_contracts.py`

## Done Criteria

- `브리프 신뢰도` 독립 섹션을 제거한다.
- Events / 자료 기준을 별도 주의사항 목록으로 보여주지 않는다.
- Event context는 필요할 때 `이벤트 배경` 브리프 행으로 흡수해, 오늘 움직임의 직접 원인으로 볼 수 있는지 여부를 시장맥락 결론으로 보여준다.
- Futures 자료 제한은 실제 Futures data-health 항목이 있을 때만 `Futures/Macro 배경` 행을 `장중 macro 해석 보류`로 낮춘다.
- 상세 source / freshness / 보강 위치는 하단 `근거: 자료 기준 / 출처 상태` disclosure에 남긴다.

## Out Of Scope

- 새 provider / schema / loader / persistence path
- UI render 중 external fetch
- FRED / events / sentiment hard conditioning
- registry / saved JSONL write
- Backtest / Practical Validation / Final Review / Operations core logic
- trade signal / 추천 / validation gate / monitoring signal
