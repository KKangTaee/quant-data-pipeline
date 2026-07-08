# Design

Status: Active
Last Updated: 2026-06-29

## 1차 Design Decision

1차는 Streamlit layout을 크게 갈아엎기 전에 화면 언어를 먼저 정렬한다. 현재 화면이 완성형 금융 UI처럼 보이지 않는 가장 큰 이유 중 하나는 `작업대`, `탐색 모드`, `Top Gainers` 같은 내부 / 영문 / prototype 용어가 혼재하기 때문이다.

## Benchmark Interpretation

- Toss Securities / Upbit류의 retail market list는 사용자가 바로 이해하는 한국어 순위 언어를 앞에 둔다.
- StockAnalysis / MarketWatch / Nasdaq류의 market movers는 gainers / losers / active처럼 ranking purpose를 분리해 사용자가 먼저 방향을 선택하게 한다.
- TradingView / Finviz류의 heatmap은 섹터 / 퍼포먼스 맥락을 별도 진단 표가 아니라 시각 스캔 영역으로 둔다.

## 1차 UI Rule

- 화면에서 보이는 mode는 `랭킹 기준`이다.
- mode option은 `상승`, `하락`, `거래량`, `이상 거래량`, `섹터`다.
- 상단 strip은 사용자가 현재 보고 있는 universe / period / freshness / 보기 기준을 요약한다.
- 기존 service read model의 계산과 DB boundary는 유지한다.

## Follow-Up Design For 2차

2차부터는 metric-card 반복 대신 compact list / tape / rank row 중심으로 상위 변동종목을 재배치한다. Streamlit 기본 버튼만 고집하지 않고 HTML/CSS component rendering, `st.dataframe` column config, Altair mark layer를 조합해 더 금융 화면다운 밀도를 만든다.
