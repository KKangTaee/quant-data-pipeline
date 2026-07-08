# Overview Market Movers Sector V4 Plan

## 이걸 하는 이유?

Market Movers 1~3차로 사용자는 탐색 모드와 선택 종목 조사 흐름을 갖게 됐다. 4차는 개별 급등락을 sector-level 확산 / 집중 맥락과 같이 읽게 해, 움직임이 특정 섹터에 몰렸는지 또는 시장 전반에 퍼졌는지 더 빨리 판단하게 만드는 단계다.

## Scope

- Existing market mover snapshot rows에서 sector breadth read model을 만든다.
- Sector별 participation, advancers / decliners, average / median / market-cap weighted return, top gainer / top loser context를 제공한다.
- Market Movers UI에 sector heatmap summary와 상세 fallback table을 연결한다.
- 기존 exploration mode, selected-symbol investigation, coverage diagnostics는 유지한다.

## Out Of Scope

- 새 DB schema / provider / external UI fetch.
- sector rotation prediction, 추천, 매수 / 매도 신호, validation gate, monitoring signal.
- Macro Context / Historical Analog hard coupling.
- 5차 Coverage/Data Quality trust UX.

## Stop Condition

- 4차 구현, 검증, Browser QA screenshot, coherent commit까지 완료하고 멈춘다.
- 5차는 사용자가 `5차 진행`이라고 명시할 때만 시작한다.
