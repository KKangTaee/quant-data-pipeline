# Overview Market Movers Modes V2 Plan

## 이걸 하는 이유?

Market Movers 1차는 화면 골격을 `변동종목 작업대`로 정리했지만, 사용자는 여전히 수익률/거래량/섹터 흐름을 명확한 탐색 모드로 전환해서 보기 어렵다. 2차는 기존 DB snapshot/read model만 사용해 상용 Market Movers에 가까운 mode-first 탐색 흐름을 만든다.

## Scope

- Top Gainers, Top Losers, Volume Leaders, Unusual Volume, Sector Leaders read model을 추가한다.
- Top Losers는 음수 수익률만 별도로 정렬한다.
- Unusual Volume은 저장된 EOD 1d volume의 10일 평균 대비 current volume으로 계산하고, 계산할 수 없으면 이유를 표시한다.
- Streamlit UI에 explicit exploration mode selector를 추가하고, 선택 모드의 표/차트를 첫 화면에 배치한다.
- Why It Moved는 3차 대상이므로 선택 모드의 종목 목록에서 조사 시작점으로 이어지는 기존 경계만 유지한다.

## Out Of Scope

- 새 DB schema/provider 추가.
- UI 직접 외부 fetch.
- buy/sell/trade signal, catalyst score, validation/Final Review/Operations signal.
- 선택 종목 detail pane과 Why It Moved 통합. 이 내용은 3차에서 다룬다.
- 섹터 heatmap/breadth 전면 개편. 이 내용은 4차에서 다룬다.
- Coverage/Data Quality trust UX 전면 정리. 이 내용은 5차에서 다룬다.

## Stop Condition

- 관련 service contract test가 추가/갱신되고 통과한다.
- `git diff --check`, py_compile, 관련 service contract 검증이 완료된다.
- Streamlit Browser QA에서 SP500 daily, SP500 weekly/monthly 중 하나, NASDAQ coverage 상태, 좁은 화면을 확인하고 screenshot 1장을 확보한다.
- generated artifact는 stage하지 않고, coherent Korean commit을 만든 뒤 3차 진행 전 멈춘다.
