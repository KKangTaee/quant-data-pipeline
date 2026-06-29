# Overview Market Movers Redesign V2 2차

Status: Active
Last Updated: 2026-06-29

## 이걸 하는 이유?

1차는 화면 언어를 정리했지만, 본문은 여전히 표와 차트 중심으로 남아 있어 상용 market mover 화면처럼 빠르게 스캔하기 어렵다. 2차는 metric-card나 raw table이 아니라 상위 변동 종목을 market-board형 tape/list로 먼저 보이게 한다.

## Scope

- 선택된 랭킹 기준에 맞는 compact board read model을 만든다.
- 상위 5개는 tape로 빠르게 스캔하게 하고, 전체 Top N은 compact list row로 보여준다.
- 기존 상세 표는 삭제하지 않고 expander 안으로 낮춘다.
- 차트, 섹터 breadth, Why It Moved flow는 기존 위치를 유지한다.

## Out Of Scope

- Chart workspace 재설계는 3차.
- Sector heatmap 재설계는 4차.
- 선택 종목 detail pane 재구성은 5차.
- Data trust / empty state hardening은 6차.
